/* contrast.mjs — the one implementation of "is this text legible against what is behind it".
 *
 * It lives here because two suites need it and a second copy is how the two of them drift.
 * text_contrast.mjs sweeps every page in two contexts. map_gestures.mjs needs the same
 * question asked of two controls that DO NOT EXIST until a finger has moved the county map,
 * which is a state no sweep can walk into. Same maths, same compositing, same floors.
 *
 * MEASURE is passed to `page.evaluate`, so it is serialised to source and runs with no closure
 * over anything in this module. Everything it needs is declared inside it. Do not reach out.
 *
 * It takes an optional array of selectors. With none it walks the whole body, which is the
 * sweep. With some it measures exactly those elements, which is the targeted call, and an
 * element that is hidden or absent still comes back counted rather than quietly dropped.
 */
export const MEASURE = (only) => {
  const relLum = ([r, g, b]) => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => {
    const x = relLum(a), y = relLum(b);
    const [hi, lo] = x > y ? [x, y] : [y, x];
    return (hi + 0.05) / (lo + 0.05);
  };
  /* THE BROWSER IS THE ONLY HONEST PARSER OF A CSS COLOUR, so it does the parsing.
     The first version of this scraped four numbers out of the computed string with
     /[\d.]+/g, which is correct for `rgb(180, 102, 79)` and silently wrong for
     `color(srgb 1 1 1 / 0.34)`, the form Chrome hands back for anything built with
     `color-mix()`. Those channels are 0 to 1, not 0 to 255, so a white well parsed as
     rgb(1,1,1) and the gate reported a legible numeral as 2.42 against its ground. It very
     nearly talked me into "fixing" a colour that was already right.
     Painting one pixel and reading it back cannot make that mistake, in any colour syntax
     this browser accepts, including ones that do not exist yet. `getImageData` returns
     unpremultiplied channels, so a 34 percent white comes back as 255,255,255 at 0.34. */
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = s => {
    if (!s) return null;
    cx.clearRect(0, 0, 1, 1);
    cx.fillStyle = '#000';
    cx.fillStyle = s;           /* an unparseable value leaves the previous fill in place */
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const over = (fg, bg) => [0, 1, 2].map(i => fg[i] * fg[3] + bg[i] * (1 - fg[3]));

  /* THE GROUND UNDER AN ELEMENT is every ancestor background composited bottom up, starting at
     the browser's own white and ending at the nearest painted layer. Anything that paints an
     image or a gradient anywhere in that stack is not a colour and is declined, not guessed. */
  const groundOf = el => {
    const stack = [];
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor);
      if (c && c[3] > 0) stack.push(c);
      if (c && c[3] >= 0.999) break;
    }
    let ground = [255, 255, 255];
    for (const layer of stack.reverse()) ground = over(layer, ground);
    return ground;
  };

  const hidden = el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return true;
    const r = el.getBoundingClientRect();
    /* The visually-hidden pattern this site uses parks a label off-canvas at -9999px. It is
       read aloud and never seen, so it has no ground and no contrast question. */
    if (r.width < 2 || r.height < 2 || r.right < -1000 || r.bottom < -1000) return true;
    return false;
  };

  const rows = [], skipped = { image: 0, hidden: 0, absent: 0 };

  /* WHAT GETS MEASURED. With no selector list this is every run of text in the body, which is
     the sweep. With one it is those elements and nothing else, and a selector that matches
     nothing is COUNTED rather than skipped, because a targeted call whose selector went stale
     would otherwise report a clean measurement of zero elements. */
  const targets = [];
  if (only && only.length) {
    for (const sel of only) {
      const el = document.querySelector(sel);
      if (!el) { skipped.absent++; continue; }
      const t = [...el.childNodes].find(n => n.nodeType === 3 && n.nodeValue.trim())
        || document.createTreeWalker(el, NodeFilter.SHOW_TEXT).nextNode();
      if (!t || !t.nodeValue.trim()) { skipped.absent++; continue; }
      targets.push([t, t.parentElement, sel]);
    }
  } else {
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new Set();
    for (let t = walk.nextNode(); t; t = walk.nextNode()) {
      if (!t.nodeValue || !t.nodeValue.trim()) continue;
      const el = t.parentElement;
      if (!el || seen.has(el)) continue;
      seen.add(el);
      targets.push([t, el, null]);
    }
  }

  for (const [t, el, sel] of targets) {
    /* SVG text carries `fill`, not `color`, and lives on drawings this suite has no ground for.
       responsive.mjs holds the chart labels. A TARGETED call that lands on one is a stale
       selector rather than a drawing to decline, so it is counted and not waved through. */
    if (el.closest('svg')) { if (sel) skipped.absent++; continue; }
    if (hidden(el)) { skipped.hidden++; continue; }
    const ground = groundOf(el);
    if (!ground) { skipped.image++; continue; }
    const cs = getComputedStyle(el);
    const fg = parse(cs.color);
    if (!fg) continue;
    const size = parseFloat(cs.fontSize);
    const weight = Number(cs.fontWeight) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    rows.push({
      text: t.nodeValue.trim().slice(0, 42),
      sel: sel || (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).join('.') : '')),
      got: Math.round(ratio(over(fg, ground), ground) * 100) / 100,
      need: large ? 3.0 : 4.5,
    });
  }
  return { rows, skipped };
};
