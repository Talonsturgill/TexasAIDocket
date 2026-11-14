/* txlook.js — LOOK V2 for the daily carousel: the tone tokens, the grade, and the way type is seated.
 *
 * WHY THIS EXISTS (owner, November 14th, 2026). "Make it 10x better, the artwork on the carousels is nowhere near the
 * quality it needs to be." The measurements that morning, read from Upload-Post:
 *
 *     TikTok photo carousel, average time watched     Texas Nov 13  3.03 s    Texas Nov 14  2.85 s
 *                                                     Alaska Nov 14 17.65 s
 *     deck median L* (measure_shipped, Nov 14 deck)   5.5 of 100
 *
 * A viewer gives a Texas deck one slide. The October 4th cure for "faded colors" was to stage every deck in a near black
 * world, which killed the mid tone wash and replaced it with a brown dark: one small lit object in a black room under a
 * black type band. The owner's words on the same week's films name what was still missing: "very 2D ... every corner is
 * very sharp ... faded colors. I want more pungent ... think about how Apple MacBook they do it." Look v2 is the films'
 * answer (TexasAIDispatch knowledge/craft/LOOK_V2.md, merged November 13th and 14th) carried into the deck, so a reader
 * who saw the morning's film recognises the afternoon's carousel.
 *
 * THE FIVE RULES THIS FILE HOLDS, each one a function a frame calls:
 *   1. ONE TONE PER DECK. The chassis declares look:'v2' and tone, one of wonder, explainer, win, watch, people. The tone
 *      picks the palette, the sky, the key and the grade. It rotates day to day, and at most two `watch` decks run in any
 *      seven (the routine checks it). A tone is how the story should leave a reader.
 *   2. COLOUR, NEVER BLACK. Shadows lean to the tone's deep violet or navy, highlights to its warm key. A wash may tint
 *      but never greys or blackens the art. TXLOOK.typeWash seats light type on the tone's own deep hue.
 *   3. SATURATED, WITH HARMONY. Warm ground under a cool sky, one accent spent on the thing that matters.
 *   4. ROUND AND LIT. The studio (TXT.studio) is a seamless sweep in the tone's colours under a big soft key, with a
 *      cool rim behind, the way a product is shot. Rounded boxes, soft contact shadows.
 *   5. TYPE A THUMB READS. Labels are pills with a 28 px radius in the accent, never a mono caption on black.
 *
 * LOAD ORDER: after txdeck.js and before the chassis. The chassis declares look:'v2' and tone in TXDECK.declare; a deck
 * that declares neither renders exactly as before, byte for byte, because nothing here runs unless called.
 */
(function (global) {
  "use strict";

  var TXLOOK = {};

  /* THE TONES. Sky top and bottom, the sweep's floor, the key, the shade every shadow leans to, the rim, the accent and
   * the ink that sits on it, the type colours, and the grade. Hues are the films' GRADES (TexasAIDispatch
   * video-engine/src/look/tokens.ts) so the brand reads as one; lightness was set on real carousel renders so that
   * cream type at 31 px clears 4.5 to 1 on the type wash in every tone. */
  TXLOOK.TONES = {
    wonder: {
      skyTop: "#1f3fa8", skyMid: "#4a78e0", skyLow: "#ffb86b", floor: "#f2a25a", wall: "#3c63cf",
      key: "#ffd9a0", fill: "#4e5fd6", rim: "#9cc4ff", shade: "#24206a", low: "#14205e",
      accent: "#ffcc00", accent2: "#ff8a00", accentInk: "#1a1200", ink: "#fff7e8", dek: "#e6ecff",
      grade: { saturation: 1.32, contrast: 1.08, lift: [0.028, 0.022, 0.07], gain: [1.04, 1.0, 0.95] }
    },
    explainer: {
      skyTop: "#123d8f", skyMid: "#2f8fe0", skyLow: "#a6dcff", floor: "#ffc68a", wall: "#2a7fd6",
      key: "#e8f6ff", fill: "#5a62e6", rim: "#7fe3ff", shade: "#2a1e78", low: "#0f1f5c",
      accent: "#22d3ee", accent2: "#6366f1", accentInk: "#04212a", ink: "#f4fbff", dek: "#dcecff",
      grade: { saturation: 1.3, contrast: 1.08, lift: [0.02, 0.02, 0.075], gain: [1.02, 1.0, 0.97] }
    },
    win: {
      skyTop: "#0f6fb8", skyMid: "#3aa0e8", skyLow: "#c8f0ff", floor: "#ffd36a", wall: "#2f97df",
      key: "#fff3b8", fill: "#2fa58a", rim: "#b8ffe6", shade: "#0f4d4a", low: "#0b3a44",
      accent: "#a3e635", accent2: "#22c55e", accentInk: "#142200", ink: "#fbfff0", dek: "#e2f6ff",
      grade: { saturation: 1.3, contrast: 1.07, lift: [0.012, 0.03, 0.04], gain: [1.03, 1.01, 0.95] }
    },
    watch: {
      skyTop: "#2a1f78", skyMid: "#5b4bc4", skyLow: "#f0a6c0", floor: "#ff8a5a", wall: "#5444b8",
      key: "#ffc2a8", fill: "#7a4fd0", rim: "#ffb0d0", shade: "#1e1b4b", low: "#1a1442",
      accent: "#ff5d5d", accent2: "#f59e0b", accentInk: "#2a0505", ink: "#fff3f0", dek: "#f0e6ff",
      grade: { saturation: 1.26, contrast: 1.1, lift: [0.035, 0.018, 0.07], gain: [1.04, 0.99, 0.96] }
    },
    people: {
      skyTop: "#2b4fb8", skyMid: "#4a7be0", skyLow: "#ffc7a8", floor: "#ff9f62", wall: "#4673d8",
      key: "#ffdcb0", fill: "#7a52c8", rim: "#ffc7a8", shade: "#3b1f5e", low: "#24164e",
      accent: "#ff9f1c", accent2: "#ff4d6d", accentInk: "#2a1300", ink: "#fff6ec", dek: "#f2e8ff",
      grade: { saturation: 1.3, contrast: 1.08, lift: [0.035, 0.02, 0.06], gain: [1.04, 1.0, 0.95] }
    }
  };
  TXLOOK.TONE_NAMES = ["wonder", "explainer", "win", "watch", "people"];

  /* ---- colour helpers: shade toward the tone's deep hue and light toward its key, never toward black or white ---- */
  function hex(c) { var h = String(c).replace("#", ""); if (h.length === 3) h = h.replace(/./g, "$&$&"); return [0, 2, 4].map(function (i) { return parseInt(h.slice(i, i + 2), 16); }); }
  function out(v) { return "#" + v.map(function (x) { return Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, "0"); }).join(""); }
  TXLOOK.mix = function (a, b, t) { var x = hex(a), y = hex(b); return out(x.map(function (v, i) { return v + (y[i] - v) * t; })); };
  TXLOOK.rgba = function (c, a) { var v = hex(c); return "rgba(" + v[0] + "," + v[1] + "," + v[2] + "," + a + ")"; };
  TXLOOK.num = function (c) { var v = hex(c); return (v[0] << 16) | (v[1] << 8) | v[2]; };
  /* linear 0..1, for TXBENCH albedo, keyColor and ambColor */
  TXLOOK.lin = function (c, k) { k = k == null ? 1 : k; return hex(c).map(function (v) { v /= 255; return k * (v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)); }); };

  /* ---- the deck's tone, from its declaration ---- */
  TXLOOK.active = function () {
    try { var d = global.TXDECK && global.TXDECK.deck(); return !!(d && d.look === "v2"); } catch (e) { return false; }
  };
  TXLOOK.toneName = function () {
    var d = null; try { d = global.TXDECK && global.TXDECK.deck(); } catch (e) { d = null; }
    var t = d && d.tone;
    if (TXLOOK.TONE_NAMES.indexOf(t) < 0) throw new Error("TXLOOK: a look v2 deck declares tone as one of " + TXLOOK.TONE_NAMES.join(", ") + " in TXDECK.declare, got " + t);
    return t;
  };
  TXLOOK.palette = function (tone) { var T = TXLOOK.TONES[tone || TXLOOK.toneName()]; if (!T) throw new Error("TXLOOK: no tone " + tone); return T; };

  /* THE GRADE for TXDECK.declare's `grade`: saturation lifted, shadows lifted toward the tone's violet, highlights toward
   * its key, a soft bloom, light grain. `over` merges on top for a deck's own tuning. */
  TXLOOK.grade = function (tone, over) {
    var T = TXLOOK.TONES[tone]; if (!T) throw new Error("TXLOOK.grade: no tone " + tone);
    return Object.assign({
      exposure: 0, saturation: T.grade.saturation, contrast: T.grade.contrast, filmic: true,
      lift: T.grade.lift.slice(), gain: T.grade.gain.slice(), vignette: 0.08,
      bloom: { threshold: 0.8, strength: 0.22, radius: 10 },
      grain: { amount: 0.01, size: 2, seed: 20261114 },
      aberration: 0, dither: true, sharpen: 0.14
    }, over || {});
  };

  /* THE SKY BAND, for a frame's art above a relief or behind type: the tone's sky as a gradient, top to `y1`, with a
   * soft bright horizon. It replaces the near black fill a relief frame used to start from. */
  TXLOOK.sky2d = function (cx, o) {
    o = o || {}; var T = TXLOOK.palette(o.tone), W = o.w || 1080, y0 = o.y0 || 0, y1 = o.y1 == null ? 1350 : o.y1;
    var g = cx.createLinearGradient(0, y0, 0, y1);
    g.addColorStop(0, T.skyTop); g.addColorStop(0.62, T.skyMid); g.addColorStop(1, TXLOOK.mix(T.skyLow, T.skyMid, 0.25));
    cx.fillStyle = g; cx.fillRect(0, y0, W, y1 - y0);
    /* the key's glow on its side of the sky, so the light has a source the eye can find */
    var kx = o.keyX == null ? W * 0.18 : o.keyX, kr = o.keyR || W * 0.75, rg = cx.createRadialGradient(kx, y1, 10, kx, y1, kr);
    rg.addColorStop(0, TXLOOK.rgba(T.key, 0.55)); rg.addColorStop(1, TXLOOK.rgba(T.key, 0));
    cx.save(); cx.beginPath(); cx.rect(0, y0, W, y1 - y0); cx.clip(); cx.fillStyle = rg; cx.fillRect(0, y0, W, y1 - y0); cx.restore();
    return cx;
  };

  /* THE TYPE SEAT. A tint from the top of the frame to just under the dek in the tone's own deep hue, never black, so
   * cream type clears contrast and the sky behind it keeps its colour. `a` is the strength at the top. */
  TXLOOK.typeWash = function (cx, o) {
    o = o || {}; var T = TXLOOK.palette(o.tone), W = o.w || 1080;
    var dek = document.querySelector(".dek"), b = dek ? dek.getBoundingClientRect() : { top: 400, height: 200 };
    var y1 = (o.to != null ? o.to : b.top + b.height) + (o.pad == null ? 30 : o.pad), f = o.fade == null ? 220 : o.fade, a = o.a == null ? 0.62 : o.a;
    var g = cx.createLinearGradient(0, 0, 0, y1 + f), c = T.low;
    g.addColorStop(0, TXLOOK.rgba(c, a)); g.addColorStop(y1 / (y1 + f) * 0.7, TXLOOK.rgba(c, a * 0.82));
    g.addColorStop(y1 / (y1 + f), TXLOOK.rgba(c, a * 0.5)); g.addColorStop(1, TXLOOK.rgba(c, 0));
    cx.fillStyle = g; cx.fillRect(0, 0, W, y1 + f);
    return cx;
  };
  /* the footer seat: a low tint of the same hue under the site line and claim ids */
  TXLOOK.footWash = function (cx, o) {
    o = o || {}; var T = TXLOOK.palette(o.tone), W = o.w || 1080, H = o.h || 1350, h = o.height || 200, a = o.a == null ? 0.5 : o.a;
    var g = cx.createLinearGradient(0, H - h, 0, H);
    for (var k = 0; k <= 6; k++) { var t = k / 6, e = t * t * (3 - 2 * t); g.addColorStop(t, TXLOOK.rgba(T.low, (a * e).toFixed(4))); }
    cx.fillStyle = g; cx.fillRect(0, H - h, W, h);
    return cx;
  };

  /* THE TYPE. Cream hook, a cool light dek, labels as accent pills. Returned as CSS for the chassis to append after its
   * own, so the layout stays the chassis's and only the colour and the label shape change. */
  TXLOOK.css = function (tone) {
    var T = TXLOOK.palette(tone), halo = TXLOOK.rgba(T.low, 0.55), halo2 = TXLOOK.rgba(T.low, 0.4);
    return [
      "html, body { background:" + T.skyTop + "; }",
      ".hook { color:" + T.ink + "; }",
      ".dek { color:" + T.dek + "; }",
      ".tx-site, .kick, .count, .src { color:" + T.ink + "; }",
      ".hook, .dek, .kick, .count { text-shadow:0 0 2px " + halo + ", 0 2px 18px " + halo2 + "; }",
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 6px " + halo2 + "; }",
      ".lab { color:" + T.accentInk + "; background:linear-gradient(180deg," + T.accent + "," + TXLOOK.mix(T.accent, T.accent2, 0.35) + "); " +
        "border-radius:28px; padding:8px 22px 9px; text-shadow:none; font-weight:700; box-shadow:0 10px 26px " + TXLOOK.rgba(T.low, 0.38) + ", 0 2px 6px " + TXLOOK.rgba(T.low, 0.3) + "; }",
      ".lab.plain { color:" + T.ink + "; background:" + TXLOOK.rgba(T.low, 0.55) + "; box-shadow:none; }"
    ].join("\n");
  };
  TXLOOK.mountCSS = function (tone) {
    var st = document.createElement("style"); st.id = "txlook"; st.textContent = TXLOOK.css(tone); document.head.appendChild(st); return st;
  };

  /* THE RELIEF'S LIGHT, for TXBENCH.relief: the key in the tone's warm colour and the ambient in its sky, so a plan view
   * relief stands in the same light as the deck's spatial frames. */
  TXLOOK.reliefLight = function (tone) {
    var T = TXLOOK.palette(tone);
    return { keyColor: TXLOOK.lin(T.key, 1.15), ambColor: TXLOOK.lin(TXLOOK.mix(T.skyMid, "#ffffff", 0.35), 1.0) };
  };

  global.TXLOOK = TXLOOK;
})(typeof window !== "undefined" ? window : globalThis);
