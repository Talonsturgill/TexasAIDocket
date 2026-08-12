/* akpost.js — film-grade post-processing for slide canvases (no deps, CPU).
 *
 * The finishing pass that separates "drawn shapes" from "a graded still".
 * Implements the researched minimal grading stack (Hable's op order + ACES
 * Narkowicz fit + IGN dither + luminance-masked grain + output sharpening):
 *
 *   bloom (linear, brights only)
 *     -> exposure -> saturation -> log-contrast (pivot 0.18)
 *     -> ACES filmic -> display gamma -> lift/gain split-tone
 *     -> luminance-masked soft-light grain
 *     -> IGN dither (LAST grading op: kills 8-bit banding)
 *     -> unsharp mask (output sharpening, optional)
 *
 * ORDER IS NOT OPTIONAL (research-verified): contrast before the filmic curve,
 * dither after all grading, sharpening last. Call grade() ONCE on the ART
 * canvas after all drawing; DOM text sits above and is never touched. All ops
 * deterministic (seeded); single read + single write of ImageData.
 *
 * USAGE (inside renderReady, after drawing the art):
 *   <script src="@@ASSETS@@/js/akpost.js"></script>
 *   TXPOST.grade(cx, {
 *     w: 1080, h: 1350,
 *     exposure: 0.0,                    // stops; art slightly under-exposed (-0.15) gives rolloff headroom
 *     saturation: 1.08,
 *     contrast: 1.12,                   // log-space, pivot 0.18
 *     filmic: true,                     // ACES fit; per-channel (film-like hue shifts by design)
 *     lift: [0.010, 0.014, 0.024],      // shadow tint (cool) 0..~0.05
 *     gain: [1.015, 1.0, 0.975],        // highlight tint (warm)
 *     vignette: 0.2,                    // radial multiply toward a cooler edge, felt not seen
 *     bloom: { threshold: 0.72, strength: 0.35, radius: 8 },
 *     grain: { amount: 0.05, size: 2, seed: 20260711 },  // soft-light, shadows/mids only
 *     aberration: 0,                    // px RGB fringe at corners; hero-art slides ONLY, never data/text
 *     dither: true,                     // IGN, +-1 LSB
 *     sharpen: 0.35                     // unsharp amount; skip on halftone regions (moire)
 *   });
 *
 * THE SHAPES ABOVE ARE ENFORCED (2026-07-26): a wrong option shape THROWS
 * (contrast is a NUMBER, lift/gain are TOP-LEVEL 3-element arrays), and an
 * unknown key is reported via console.error rather than silently ignored.
 *
 * HOUSE GRADE for the dark-arctic register: the defaults above. Brand-exact
 * marks (gold Polaris, wordmark) should be DOM/SVG so the grade never shifts
 * them. Budget total texture (grain + dither + any feTurbulence) <= ~10%.
 */
(function (global) {
  "use strict";
  const P = {};

  function getScale(ctx) {
    const t = ctx.getTransform ? ctx.getTransform() : { a: 1 };
    return t.a || 1;
  }

  /* ---- ARGUMENT VALIDATION (2026-07-26) --------------------------------
   * Added after a slide called grade() with contrast as an OBJECT
   * ({amount, pivot}) and lift/gain as HEX STRINGS inside an undocumented
   * `split` wrapper. Every arithmetic op downstream produced NaN, the whole
   * ImageData wrote 0, and the slide rendered a fully black art canvas with
   * errors=0: nothing in the engine complained, because grade() coerced
   * whatever it was handed. A wrong option shape is a bug, not a style, so it
   * now THROWS (render.py records the page error and hard-fails the slide)
   * rather than silently blanking a canvas. Unknown keys are reported via
   * console.error (qa.py surfaces it as a WARN) because a silently ignored
   * option is how the `split` wrapper hid the real problem.
   */
  const NUM_OPTS = ["w", "h", "exposure", "saturation", "contrast", "vignette",
                    "aberration", "sharpen"];
  const TRIPLE_OPTS = ["lift", "gain"];
  const OBJ_OPTS = { bloom: ["threshold", "strength", "radius"],
                     grain: ["amount", "size", "seed"] };
  const BOOL_OPTS = ["filmic", "dither"];
  const KNOWN = NUM_OPTS.concat(TRIPLE_OPTS, BOOL_OPTS, Object.keys(OBJ_OPTS));

  function bad(where, got, want) {
    throw new TypeError("TXPOST.grade: " + where + " must be " + want +
      ", got " + (Array.isArray(got) ? "array[" + got.length + "]" : typeof got) +
      " " + JSON.stringify(got));
  }

  function validate(o) {
    for (const k of NUM_OPTS) {
      if (o[k] == null) continue;
      if (typeof o[k] !== "number" || !isFinite(o[k])) bad(k, o[k], "a finite number");
    }
    for (const k of TRIPLE_OPTS) {
      if (o[k] == null) continue;
      const v = o[k];
      if (!Array.isArray(v) || v.length !== 3 ||
          !v.every((n) => typeof n === "number" && isFinite(n)))
        bad(k, v, "a 3-element array of finite numbers, e.g. [0.010, 0.014, 0.024]");
    }
    for (const k of Object.keys(OBJ_OPTS)) {
      if (o[k] == null) continue;
      const v = o[k];
      if (typeof v !== "object" || Array.isArray(v))
        bad(k, v, "an object of {" + OBJ_OPTS[k].join(", ") + "}");
      for (const f of OBJ_OPTS[k]) {
        if (v[f] == null) continue;
        if (typeof v[f] !== "number" || !isFinite(v[f]))
          bad(k + "." + f, v[f], "a finite number");
      }
    }
    for (const k of BOOL_OPTS) {
      if (o[k] == null) continue;
      if (typeof o[k] !== "boolean") bad(k, o[k], "true or false");
    }
    for (const k of Object.keys(o)) {
      if (KNOWN.indexOf(k) === -1) {
        try {
          console.error("TXPOST.grade: unknown option '" + k + "' is being IGNORED " +
            "(known options: " + KNOWN.join(", ") + "). Check the contract in " +
            "akpost.js: lift/gain are top-level 3-element arrays, contrast is a number.");
        } catch (e) {}
      }
    }
  }

  P.grade = function (ctx, o) {
    o = o || {};
    validate(o);
    const scale = getScale(ctx);
    const W = Math.round((o.w || ctx.canvas.width / scale) * scale);
    const H = Math.round((o.h || ctx.canvas.height / scale) * scale);
    const img = ctx.getImageData(0, 0, W, H);
    const d = img.data;

    /* ---- srgb<->linear tables ---- */
    const toLin = new Float32Array(256);
    for (let i = 0; i < 256; i++) toLin[i] = Math.pow(i / 255, 2.2);

    /* ---- bloom in linear (downsampled box blur of thresholded brights) ---- */
    if (o.bloom && o.bloom.strength > 0) {
      const bt = o.bloom.threshold != null ? o.bloom.threshold : 0.72;
      const bs = o.bloom.strength != null ? o.bloom.strength : 0.35;
      const ds = 4, bw = Math.ceil(W / ds), bh = Math.ceil(H / ds);
      const rad = Math.max(1, Math.round((o.bloom.radius || 8) / ds));
      let buf = new Float32Array(bw * bh * 3);
      for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) {
        const si = ((y * ds) * W + (x * ds)) * 4;
        const r = toLin[d[si]], g = toLin[d[si + 1]], b = toLin[d[si + 2]];
        const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        if (lum > bt * bt) {  // threshold approx in linear
          const k = Math.min(1, (Math.sqrt(lum) - bt) / (1 - bt)), bi = (y * bw + x) * 3;
          if (k > 0) { buf[bi] = r * k; buf[bi + 1] = g * k; buf[bi + 2] = b * k; }
        }
      }
      // separable box blur x2
      for (let pass = 0; pass < 2; pass++) {
        const out = new Float32Array(bw * bh * 3);
        const dx = pass === 0 ? 1 : bw, len = pass === 0 ? bw : bh, lines = pass === 0 ? bh : bw;
        for (let l = 0; l < lines; l++) {
          const base = pass === 0 ? l * bw : l;
          for (let c = 0; c < 3; c++) {
            let acc = 0;
            for (let i = -rad; i <= rad; i++) acc += buf[(base + Math.min(len - 1, Math.max(0, i)) * dx) * 3 + c];
            for (let i = 0; i < len; i++) {
              out[(base + i * dx) * 3 + c] = acc / (2 * rad + 1);
              acc += buf[(base + Math.min(len - 1, i + rad + 1) * dx) * 3 + c]
                   - buf[(base + Math.max(0, i - rad) * dx) * 3 + c];
            }
          }
        }
        buf = out;
      }
      for (let y = 0; y < H; y++) {
        const by = Math.min(bh - 1, (y / ds) | 0);
        for (let x = 0; x < W; x++) {
          const bi = (by * bw + Math.min(bw - 1, (x / ds) | 0)) * 3;
          const i4 = (y * W + x) * 4;
          for (let c = 0; c < 3; c++) {
            const s = toLin[d[i4 + c]], add = buf[bi + c] * bs;
            // additive in linear, encode back
            d[i4 + c] = 255 * Math.pow(Math.min(1, s + add), 1 / 2.2);
          }
        }
      }
    }

    /* ---- the tone chain as a LUT over post-saturation LINEAR values ---- */
    const expMul = Math.pow(2, o.exposure || 0);
    const sat = o.saturation != null ? o.saturation : 1.06;
    const con = o.contrast != null ? o.contrast : 1.1;
    const filmic = o.filmic !== false;
    const lift = o.lift || [0, 0, 0];
    const gain = o.gain || [1, 1, 1];
    const NL = 1024, LMAX = 2.0;
    const lut = [new Float32Array(NL), new Float32Array(NL), new Float32Array(NL)];
    const log2 = Math.log2 || ((x) => Math.log(x) / Math.LN2);
    for (let c = 0; c < 3; c++) {
      for (let i = 0; i < NL; i++) {
        let x = (i / (NL - 1)) * LMAX;         // linear in
        // log-space contrast, pivot 0.18 (never clamps blacks)
        x = Math.pow(2, (log2(x + 1e-5) - log2(0.18)) * con + log2(0.18));
        // ACES Narkowicz fit (per-channel: film-like hue shifts by design)
        if (filmic) x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14);
        x = Math.min(1, Math.max(0, x));
        // display gamma
        x = Math.pow(x, 1 / 2.2);
        // lift/gain split-tone in display space
        x = lift[c] + x * (gain[c] - lift[c] * 0.5);
        lut[c][i] = Math.min(1, Math.max(0, x));
      }
    }
    /* NaN SENTINEL (2026-07-26): the tone LUT is where every scalar option
     * lands, so one non-finite entry here means the grade would write a black
     * (or garbage) frame over the art. Throw instead: a dead canvas that
     * reports errors=0 is the worst outcome of all. Costs 3 lookups. */
    for (let c = 0; c < 3; c++) {
      if (!isFinite(lut[c][0]) || !isFinite(lut[c][NL >> 1]) || !isFinite(lut[c][NL - 1]))
        throw new Error("TXPOST.grade: tone LUT is non-finite (channel " + c +
          ") -- a grade option produced NaN; the graded frame would be blank");
    }

    const vig = o.vignette || 0;
    const cxm = W / 2, cym = H / 2, maxR2 = cxm * cxm + cym * cym;

    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const i4 = (y * W + x) * 4;
        // to linear + exposure
        let r = toLin[d[i4]] * expMul, g = toLin[d[i4 + 1]] * expMul, b = toLin[d[i4 + 2]] * expMul;
        // saturation in linear
        if (sat !== 1) {
          const l = 0.25 * r + 0.5 * g + 0.25 * b;
          r = l + (r - l) * sat; g = l + (g - l) * sat; b = l + (b - l) * sat;
          r = r < 0 ? 0 : r; g = g < 0 ? 0 : g; b = b < 0 ? 0 : b;
        }
        // LUT chain
        let R = lut[0][Math.min(NL - 1, (r / LMAX * (NL - 1)) | 0)];
        let G = lut[1][Math.min(NL - 1, (g / LMAX * (NL - 1)) | 0)];
        let B = lut[2][Math.min(NL - 1, (b / LMAX * (NL - 1)) | 0)];
        // vignette: multiply toward a slightly COOLER edge (corners stay alive)
        if (vig > 0) {
          const dx = x - cxm, dy = y - cym;
          const f = vig * ((dx * dx + dy * dy) / maxR2);
          R *= 1 - f; G *= 1 - f * 0.96; B *= 1 - f * 0.88;
        }
        d[i4] = 255 * R; d[i4 + 1] = 255 * G; d[i4 + 2] = 255 * B;
      }
    }

    /* ---- chromatic aberration (radial, edges only; hero art ONLY) ---- */
    const aber = (o.aberration || 0) * scale;
    if (aber > 0) {
      const src = new Uint8ClampedArray(d);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const dx = (x - cxm) / cxm, dy = (y - cym) / cym;
        const r2 = dx * dx + dy * dy;
        if (r2 < 0.25) continue;
        const k = (r2 - 0.25) / 0.75 * aber;
        const i4 = (y * W + x) * 4;
        d[i4] = src[(Math.min(H - 1, Math.max(0, Math.round(y + dy * k))) * W
                   + Math.min(W - 1, Math.max(0, Math.round(x + dx * k)))) * 4];
        d[i4 + 2] = src[(Math.min(H - 1, Math.max(0, Math.round(y - dy * k))) * W
                       + Math.min(W - 1, Math.max(0, Math.round(x - dx * k)))) * 4 + 2];
      }
    }

    /* ---- luminance-masked soft-light film grain (shadows/mids only) ---- */
    if (o.grain && o.grain.amount > 0) {
      const ga = o.grain.amount, gs = Math.max(1, o.grain.size || 2);
      let seed = (o.grain.seed || 11) >>> 0;
      const gw = Math.ceil(W / gs) + 2, gh = Math.ceil(H / gs) + 2;
      const gn = new Float32Array(gw * gh);
      for (let i = 0; i < gn.length; i++) {   // seeded LCG
        seed = (seed * 1664525 + 1013904223) >>> 0;
        gn[i] = seed / 4294967296;
      }
      for (let y = 0; y < H; y++) {
        const gy = y / gs, gy0 = gy | 0, fy = gy - gy0;
        for (let x = 0; x < W; x++) {
          const gx = x / gs, gx0 = gx | 0, fx = gx - gx0;
          // bilinear value noise (clumpy, filmic)
          const a = gn[gy0 * gw + gx0], b2 = gn[gy0 * gw + gx0 + 1];
          const c2 = gn[(gy0 + 1) * gw + gx0], e = gn[(gy0 + 1) * gw + gx0 + 1];
          const nv = (a + (b2 - a) * fx) + ((c2 + (e - c2) * fx) - (a + (b2 - a) * fx)) * fy;
          const i4 = (y * W + x) * 4;
          const lum = (0.2126 * d[i4] + 0.7152 * d[i4 + 1] + 0.0722 * d[i4 + 2]) / 255;
          const mask = 1 - Math.min(1, Math.max(0, (lum - 0.05) / 0.45)); // fades in highlights
          const gEff = ga * (0.35 + 0.65 * mask);
          const t = (nv - 0.5) * 2;
          for (let c = 0; c < 3; c++) {
            const s = d[i4 + c] / 255;
            // soft-light-ish: brighten/darken proportional to distance from extremes
            const sl = t < 0 ? s * (1 + t * gEff) : s + (1 - s) * t * gEff;
            d[i4 + c] = 255 * Math.min(1, Math.max(0, sl));
          }
        }
      }
    }

    /* ---- IGN dither: THE banding killer, exactly +-1 LSB, LAST grade op ---- */
    if (o.dither !== false) {
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const f = 52.9829189 * ((0.06711056 * x + 0.00583715 * y) % 1);
          const t2 = (f - Math.floor(f)) - 0.5;
          const i4 = (y * W + x) * 4;
          for (let c = 0; c < 3; c++) {
            const v = d[i4 + c] + t2;
            d[i4 + c] = v < 0 ? 0 : v > 255 ? 255 : v;
          }
        }
      }
    }

    /* ---- unsharp mask (output sharpening; skip on halftone regions) ---- */
    if (o.sharpen && o.sharpen > 0) {
      const amt = o.sharpen, thr = 3;
      const src = new Uint8ClampedArray(d);
      for (let y = 1; y < H - 1; y++) {
        for (let x = 1; x < W - 1; x++) {
          const i4 = (y * W + x) * 4;
          for (let c = 0; c < 3; c++) {
            const center = src[i4 + c];
            const blur = (src[i4 + c - 4] + src[i4 + c + 4]
                        + src[i4 + c - W * 4] + src[i4 + c + W * 4] + center * 4) / 8;
            const diff = center - blur;
            if (Math.abs(diff) > thr) {
              const v = center + diff * amt;
              d[i4 + c] = v < 0 ? 0 : v > 255 ? 255 : v;
            }
          }
        }
      }
    }

    /* ---- write once ---- */
    const t = ctx.getTransform();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.putImageData(img, 0, 0);
    ctx.setTransform(t);
    return true;
  };

  /* Atmospheric-perspective depth grade for LAYERED 2D scenes: call per layer
   * BEFORE drawing it, with its depth d in [0,1]. Returns {fill hints}. This is
   * a recipe helper (math only), the layer code applies it:
   *   const g = TXPOST.depthGrade(d, {atmo:[0.62,0.68,0.76]});
   *   // lerp your layer colors toward g.atmo by g.mix; multiply contrast by
   *   // g.contrast; multiply chroma by g.chroma; ctx.filter = g.blur
   */
  P.depthGrade = function (depth, o) {
    o = o || {};
    const d2 = Math.min(1, Math.max(0, depth));
    return {
      mix: 0.15 + 0.45 * Math.pow(d2, 1.4),            // toward atmosphere color
      contrast: 1 - 0.5 * d2,
      chroma: 1 - 0.6 * d2,
      blur: 'blur(' + (4 * d2 * d2) + 'px)',
      atmo: o.atmo || [0.62, 0.68, 0.76],
    };
  };

  global.TXPOST = P;
})(typeof window !== "undefined" ? window : globalThis);
