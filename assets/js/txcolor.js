/* akcolor.js — OKLCH color engine for slide palettes (no deps).
 *
 * Why: palettes and light ramps built in HSL/sRGB are the deepest root cause
 * of "flat automated" color (uneven perceived lightness, gray dead zones in
 * gradients). OKLab/OKLCH gives perceptually even steps and vivid mid-blends.
 *
 * API:
 *   TXC.hexToOklch('#FFC72C')            -> {L, C, H}
 *   TXC.oklchToHex({L:.75,C:.14,H:85})   -> '#...' (gamut-mapped by CHROMA
 *                                           reduction at constant L/H — never
 *                                           naive RGB clamping)
 *   TXC.ramp(baseHex, {steps:7, keyHue:85, ambientHue:255, drift:16})
 *       -> array of hex, dark->light: L evenly stepped, chroma a bell peaking
 *          mid-L, hue drifting toward keyHue as L rises and ambientHue as L
 *          falls ("warm light, cool shadow" encoded numerically).
 *   TXC.mixOklab(hexA, hexB, t)          -> hex (no gray dead zone)
 *   TXC.gradientMapLUT([hex...])         -> Uint8Array(256*3) luminance LUT
 *   TXC.applyGradientMap(ctx, lut, {w,h})-> remap ART canvas luminance through
 *          the ramp (duotone/tritone cohesion: "everything in one light").
 *
 * Slide use: build each material's 5-7 step ramp from the story's material
 * world + the brand anchors, then shade with ramp steps instead of ad-hoc
 * lightening. Gradient-map an entire value-study underpainting through a
 * brand ramp for instant cohesion (see TECHNIQUE_LIBRARY: Gradient-Map
 * Underpainting).
 */
(function (global) {
  "use strict";
  const TXC = {};

  /* ---- sRGB <-> OKLab (Björn Ottosson's reference math) ---- */
  function srgb2lin(c) { return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  function lin2srgb(c) { return c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055; }

  function rgbToOklab(r, g, b) {  // r,g,b in 0..1 sRGB
    const lr = srgb2lin(r), lg = srgb2lin(g), lb = srgb2lin(b);
    const l = Math.cbrt(0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb);
    const m = Math.cbrt(0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb);
    const s = Math.cbrt(0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb);
    return {
      L: 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
      a: 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
      b: 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s };
  }
  function oklabToRgb(L, a, b) {
    const l = Math.pow(L + 0.3963377774 * a + 0.2158037573 * b, 3);
    const m = Math.pow(L - 0.1055613458 * a - 0.0638541728 * b, 3);
    const s = Math.pow(L - 0.0894841775 * a - 1.2914855480 * b, 3);
    return [
      lin2srgb(+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
      lin2srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
      lin2srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)];
  }

  function hexToRgb(hex) {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255];
  }
  function rgbToHex(rgb) {
    const c = rgb.map(v => Math.round(255 * Math.min(1, Math.max(0, v))));
    return '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
  }

  TXC.hexToOklch = function (hex) {
    const [r, g, b] = hexToRgb(hex);
    const lab = rgbToOklab(r, g, b);
    return { L: lab.L, C: Math.hypot(lab.a, lab.b),
             H: (Math.atan2(lab.b, lab.a) * 180 / Math.PI + 360) % 360 };
  };

  function inGamut(rgb) { return rgb.every(v => v >= -0.0005 && v <= 1.0005); }

  // Gamut map: reduce CHROMA at constant L and H until inside sRGB. Never
  // clamp RGB directly (hue/lightness shift).
  TXC.oklchToHex = function (lch) {
    let C = lch.C;
    const hr = lch.H * Math.PI / 180;
    for (let i = 0; i < 24; i++) {
      const rgb = oklabToRgb(lch.L, C * Math.cos(hr), C * Math.sin(hr));
      if (inGamut(rgb)) return rgbToHex(rgb);
      C *= 0.86;
    }
    return rgbToHex(oklabToRgb(lch.L, 0, 0));
  };

  TXC.mixOklab = function (hexA, hexB, t) {
    const A = hexToRgb(hexA), B = hexToRgb(hexB);
    const la = rgbToOklab(A[0], A[1], A[2]), lb = rgbToOklab(B[0], B[1], B[2]);
    const L = la.L + (lb.L - la.L) * t, a = la.a + (lb.a - la.a) * t, b2 = la.b + (lb.b - la.b) * t;
    // gamut-map via chroma reduction
    const C = Math.hypot(a, b2), H = (Math.atan2(b2, a) * 180 / Math.PI + 360) % 360;
    return TXC.oklchToHex({ L, C, H });
  };

  /* Material ramp: dark -> light. Chroma bell peaks near L 0.55 (extremes
   * cannot hold chroma); hue drifts toward the key light as L rises and the
   * ambient/sky hue as L falls — warm light, cool shadow, by the numbers. */
  TXC.ramp = function (baseHex, opts) {
    opts = opts || {};
    const steps = opts.steps || 7;
    const base = TXC.hexToOklch(baseHex);
    const Lmin = opts.Lmin != null ? opts.Lmin : 0.22;
    const Lmax = opts.Lmax != null ? opts.Lmax : 0.93;
    const keyHue = opts.keyHue != null ? opts.keyHue : 85;      // warm gold-ish
    const ambHue = opts.ambientHue != null ? opts.ambientHue : 255; // cool blue
    const drift = opts.drift != null ? opts.drift : 16;         // degrees max
    const out = [];
    for (let i = 0; i < steps; i++) {
      const t = i / (steps - 1);
      const L = Lmin + (Lmax - Lmin) * t;
      // chroma bell: peak at L~0.55, ~40% at the extremes
      const bell = 0.4 + 0.6 * Math.exp(-Math.pow((L - 0.55) / 0.28, 2));
      const C = base.C * bell * (opts.chroma != null ? opts.chroma : 1);
      // hue drift: toward ambient in shadow, toward key in light
      const toward = t < 0.5 ? ambHue : keyHue;
      const k = Math.abs(t - 0.5) * 2 * (drift / 180);
      let dh = ((toward - base.H + 540) % 360) - 180;
      const H = (base.H + dh * k + 360) % 360;
      out.push(TXC.oklchToHex({ L, C, H }));
    }
    return out;
  };

  /* Gradient-map: 256-entry LUT from a ramp (positions optional). */
  TXC.gradientMapLUT = function (hexes, positions) {
    const n = hexes.length;
    const pos = positions || hexes.map((_, i) => i / (n - 1));
    const labs = hexes.map(h => { const [r, g, b] = hexToRgb(h); return rgbToOklab(r, g, b); });
    const lut = new Uint8Array(256 * 3);
    for (let v = 0; v < 256; v++) {
      const t = v / 255;
      let j = 0; while (j < n - 2 && t > pos[j + 1]) j++;
      const f = Math.min(1, Math.max(0, (t - pos[j]) / ((pos[j + 1] - pos[j]) || 1)));
      const L = labs[j].L + (labs[j + 1].L - labs[j].L) * f;
      const a = labs[j].a + (labs[j + 1].a - labs[j].a) * f;
      const b2 = labs[j].b + (labs[j + 1].b - labs[j].b) * f;
      const rgb = oklabToRgb(L, a, b2).map(x => Math.min(1, Math.max(0, x)));
      lut[v * 3] = 255 * rgb[0]; lut[v * 3 + 1] = 255 * rgb[1]; lut[v * 3 + 2] = 255 * rgb[2];
    }
    return lut;
  };

  /* Remap an art canvas's luminance through a gradient-map LUT (in place). */
  TXC.applyGradientMap = function (ctx, lut, o) {
    o = o || {};
    const t = ctx.getTransform ? ctx.getTransform() : { a: 1 };
    const scale = t.a || 1;
    const W = Math.round((o.w || ctx.canvas.width / scale) * scale);
    const H = Math.round((o.h || ctx.canvas.height / scale) * scale);
    const img = ctx.getImageData(0, 0, W, H), d = img.data;
    const amt = o.amount != null ? o.amount : 1;
    for (let i = 0; i < d.length; i += 4) {
      const lum = Math.min(255, Math.max(0, (0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) | 0));
      d[i] = d[i] + (lut[lum * 3] - d[i]) * amt;
      d[i + 1] = d[i + 1] + (lut[lum * 3 + 1] - d[i + 1]) * amt;
      d[i + 2] = d[i + 2] + (lut[lum * 3 + 2] - d[i + 2]) * amt;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.putImageData(img, 0, 0);
    ctx.setTransform(t);
  };

  global.TXC = TXC;
})(typeof window !== "undefined" ? window : globalThis);
