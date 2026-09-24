/* kit/homes.js, see assets/js/txkit.js for the conventions.
 *
 * The Texas street: the one-storey brick ranch, the suburban two-storey, the single-wide, the
 * fences that run between them, the mailbox, the driveway and the lawn. Every house is built
 * the way a house is built: a slab, walls with REAL openings (reveals, sills, lintels), windows
 * that are frames, sashes, meeting rails and glass over a room with blinds in it, a roof with
 * overhang, fascia, soffit, drip edge, gutters and downspouts, and caps on the hips.
 *
 * Geometry is baked into group space and merged per material, so a house is a dozen draw calls
 * and its textures run continuous across every wall piece (UVs are projected in metres AFTER
 * the piece is placed, so a brick course lines up across a window).
 */
export function install(K, THREE, TXT) {
  const V3 = THREE.Vector3;

  /* ---------------------------------------------------------------------------------------
   * textures: our own painters (colour + bump), tileable, cached. A tile covers `metres`.
   * ------------------------------------------------------------------------------------- */
  const TEXC = new Map();
  function hashStr(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function canvas(N) { const c = document.createElement('canvas'); c.width = c.height = N; return c; }
  function tex(key, metres, N, paint) {
    if (TEXC.has(key)) return TEXC.get(key);
    const c = canvas(N), b = canvas(N);
    const cx = c.getContext('2d'), bx = b.getContext('2d');
    const _t0 = performance.now(); paint(cx, bx, N, K.rng(hashStr(key))); (window.__TT = window.__TT || []).push([key, Math.round(performance.now() - _t0)]);
    const mk = (cv, srgb) => {
      const t = new THREE.CanvasTexture(cv);
      t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
      t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
      return t;
    };
    const out = { map: mk(c, true), bump: mk(b, false), metres };
    TEXC.set(key, out);
    return out;
  }
  function hex(c) { return typeof c === 'string' ? c : '#' + (c >>> 0).toString(16).padStart(6, '0'); }
  function rgb(h) { const c = parseInt(hex(h).slice(1), 16); return [c >> 16, (c >> 8) & 255, c & 255]; }
  function css(a, k, al) {
    const f = (v) => Math.max(0, Math.min(255, Math.round(v * (k == null ? 1 : k))));
    return al == null ? 'rgb(' + f(a[0]) + ',' + f(a[1]) + ',' + f(a[2]) + ')'
      : 'rgba(' + f(a[0]) + ',' + f(a[1]) + ',' + f(a[2]) + ',' + al + ')';
  }
  function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
  /* per-pixel grain: one 256 px noise tile per amount, laid over with 'overlay' (grey 128 is
   * neutral), so a 1024 texture costs a pattern fill rather than a million rng calls. */
  const GRAIN = new Map();
  function grain(x, N, r, amt, chroma) {
    const key = amt + '|' + (chroma || 0);
    if (!GRAIN.has(key)) {
      const c = canvas(256), gx = c.getContext('2d'), im = gx.createImageData(256, 256), d = im.data, rr = K.rng(hashStr(key));
      for (let i = 0; i < d.length; i += 4) {
        const k = 128 + (rr() - 0.5) * 2 * amt * 128, j = chroma ? (rr() - 0.5) * chroma * 128 : 0;
        d[i] = k + j; d[i + 1] = k; d[i + 2] = k - j; d[i + 3] = 255;
      }
      gx.putImageData(im, 0, 0); GRAIN.set(key, c);
    }
    x.save(); x.globalCompositeOperation = 'overlay'; x.fillStyle = x.createPattern(GRAIN.get(key), 'repeat');
    x.fillRect(0, 0, N, N); x.restore();
  }
  // soft blotches that wrap around the tile edges
  function blotch(x, N, r, n, rad, style) {
    for (let i = 0; i < n; i++) {
      const cx = r() * N, cy = r() * N, rr = rad[0] + r() * (rad[1] - rad[0]);
      for (let ox = -1; ox <= 1; ox++) for (let oy = -1; oy <= 1; oy++) {
        const g = x.createRadialGradient(cx + ox * N, cy + oy * N, 0, cx + ox * N, cy + oy * N, rr);
        g.addColorStop(0, style); g.addColorStop(1, 'rgba(0,0,0,0)');
        x.fillStyle = g; x.fillRect(cx + ox * N - rr, cy + oy * N - rr, rr * 2, rr * 2);
      }
    }
  }

  // Modular brick, running bond: 8" x 2 2/3" module, 18 courses and 6 bricks per 1.2192 m tile.
  function brickTex(base, mortar) {
    const key = 'brick|' + hex(base) + '|' + hex(mortar);
    return tex(key, 1.2192, 1024, (x, b, N, r) => {
      const B = rgb(base), Mo = rgb(mortar), rows = 18, per = 6, h = N / rows, w = N / per, j = 7;
      x.fillStyle = css(Mo); x.fillRect(0, 0, N, N);
      b.fillStyle = '#303030'; b.fillRect(0, 0, N, N);
      for (let row = 0; row < rows; row++) {
        const off = (row % 2) * w / 2;
        for (let i = -1; i <= per; i++) {
          const roll = r();
          let c = mix(B, [B[0] * 0.62, B[1] * 0.58, B[2] * 0.6], roll < 0.12 ? 0.6 + r() * 0.4 : r() * 0.35);
          if (roll > 0.9) c = mix(c, [B[0] * 1.2, B[1] * 1.12, B[2] * 1.02], 0.5);
          const x0 = i * w + off + j / 2 + (r() - 0.5) * 1.5, y0 = row * h + j / 2 + (r() - 0.5) * 1.5;
          const g = x.createLinearGradient(x0, y0, x0 + w, y0 + h);
          g.addColorStop(0, css(c, 1.05)); g.addColorStop(1, css(c, 0.9));
          x.fillStyle = g; x.fillRect(x0, y0, w - j, h - j);
          // face texture: a few pits and a flashed end
          for (let k = 0; k < 10; k++) { x.fillStyle = css(c, 0.7 + r() * 0.2, 0.5); x.fillRect(x0 + r() * (w - j), y0 + r() * (h - j), 2 + r() * 3, 1 + r() * 2); }
          if (r() < 0.3) { const g2 = x.createLinearGradient(x0, 0, x0 + w * 0.4, 0); g2.addColorStop(0, 'rgba(30,15,10,0.35)'); g2.addColorStop(1, 'rgba(30,15,10,0)'); x.fillStyle = g2; x.fillRect(x0, y0, w * 0.4, h - j); }
          const v = 170 + Math.floor(r() * 50);
          b.fillStyle = 'rgb(' + v + ',' + v + ',' + v + ')'; b.fillRect(x0 + 1, y0 + 1, w - j - 2, h - j - 2);
        }
      }
      grain(x, N, r, 0.1, 0.04); grain(b, N, r, 0.15);
      blotch(x, N, r, 10, [60, 200], 'rgba(40,30,20,0.06)');
    });
  }
  // Hill Country chopped limestone, random ashlar courses.
  function limestoneTex(base) {
    const key = 'lime|' + hex(base);
    return tex(key, 1.6, 1024, (x, b, N, r) => {
      const B = rgb(base);
      x.fillStyle = css(B, 0.78); x.fillRect(0, 0, N, N);
      b.fillStyle = '#282828'; b.fillRect(0, 0, N, N);
      const courses = [];
      let tot = 0; while (tot < N) { const hh = N * (0.075 + r() * 0.08); courses.push(hh); tot += hh; }
      const k = N / tot; let y = 0;
      for (const hh0 of courses) {
        const hh = hh0 * k; let xx = -r() * 80; const start = xx;
        while (xx < N + start) {
          const ww = N * (0.14 + r() * 0.26), c = mix(B, [B[0] * 0.8, B[1] * 0.76, B[2] * 0.66], r() * 0.6);
          const gap = 6;
          for (const ox of [0, N, -N]) {
            x.fillStyle = css(c); b.fillStyle = 'rgb(200,200,200)';
            x.beginPath(); b.beginPath();
            const pts = [[xx + gap + r() * 4, y + gap + r() * 3], [xx + ww - gap - r() * 4, y + gap + r() * 3],
                         [xx + ww - gap - r() * 4, y + hh - gap - r() * 3], [xx + gap + r() * 4, y + hh - gap - r() * 3]];
            pts.forEach((p, i) => { i ? (x.lineTo(p[0] + ox, p[1]), b.lineTo(p[0] + ox, p[1])) : (x.moveTo(p[0] + ox, p[1]), b.moveTo(p[0] + ox, p[1])); });
            x.closePath(); x.fill(); b.closePath(); b.fill();
          }
          // chisel face: soft light and dark facets
          for (let q = 0; q < 14; q++) {
            const px = xx + r() * ww, py = y + r() * hh, rr = 6 + r() * 22;
            x.fillStyle = r() < 0.5 ? css(c, 0.86, 0.35) : css(c, 1.1, 0.3);
            x.beginPath(); x.arc(((px % N) + N) % N, py, rr, 0, 6.3); x.fill();
            b.fillStyle = 'rgba(' + (r() < 0.5 ? '120,120,120' : '240,240,240') + ',0.35)';
            b.beginPath(); b.arc(((px % N) + N) % N, py, rr, 0, 6.3); b.fill();
          }
          xx += ww;
        }
        y += hh;
      }
      grain(x, N, r, 0.12, 0.03); grain(b, N, r, 0.25);
    });
  }
  // Fibre-cement lap siding, 7" exposure, faint cedar-mill grain. 7 boards per 1.2446 m.
  function sidingTex(base) {
    const key = 'siding|' + hex(base);
    return tex(key, 1.2446, 512, (x, b, N, r) => {
      const B = rgb(base), boards = 7, h = N / boards;
      for (let j = 0; j < boards; j++) {
        const y0 = j * h;
        const g = x.createLinearGradient(0, y0, 0, y0 + h);
        g.addColorStop(0, css(B, 0.9)); g.addColorStop(0.12, css(B, 1.0)); g.addColorStop(0.92, css(B, 1.03)); g.addColorStop(1, css(B, 0.97));
        x.fillStyle = g; x.fillRect(0, y0, N, h);
        x.fillStyle = 'rgba(0,0,0,0.42)'; x.fillRect(0, y0 + h - 3, N, 3);   // shadow under the lap (top of the next board down in image space)
        const gb = b.createLinearGradient(0, y0, 0, y0 + h);
        gb.addColorStop(0, 'rgb(90,90,90)'); gb.addColorStop(0.97, 'rgb(215,215,215)'); gb.addColorStop(1, 'rgb(40,40,40)');
        b.fillStyle = gb; b.fillRect(0, y0, N, h);
        for (let k = 0; k < 40; k++) { const yy = y0 + r() * h; b.fillStyle = 'rgba(0,0,0,0.12)'; b.fillRect(0, yy, N, 1); }
      }
      grain(x, N, r, 0.03); grain(b, N, r, 0.06);
    });
  }
  // Laminated architectural shingles, 5 5/8" exposure: 8 courses per 1.143 m.
  function shingleTex(base) {
    const key = 'shingle|' + hex(base);
    return tex(key, 1.143, 1024, (x, b, N, r) => {
      const B = rgb(base), rows = 8, h = N / rows;
      x.fillStyle = css(B, 0.45); x.fillRect(0, 0, N, N);
      b.fillStyle = '#202020'; b.fillRect(0, 0, N, N);
      for (let j = 0; j < rows; j++) {
        const y0 = j * h; let xx = -r() * 100;
        // the under layer (dark), then the dragon-tooth top layer of random-width tabs
        const gB = b.createLinearGradient(0, y0, 0, y0 + h);
        gB.addColorStop(0, 'rgb(70,70,70)'); gB.addColorStop(1, 'rgb(170,170,170)');
        b.fillStyle = gB; b.fillRect(0, y0, N, h);
        x.fillStyle = css(B, 0.55); x.fillRect(0, y0, N, h);
        while (xx < N) {
          const ww = N * (0.1 + r() * 0.2), drop = h * (r() < 0.55 ? 0.0 : 0.16 + r() * 0.1);
          const c = mix(B, r() < 0.5 ? [B[0] * 0.8, B[1] * 0.8, B[2] * 0.82] : [B[0] * 1.12, B[1] * 1.1, B[2] * 1.06], r() * 0.7);
          for (const ox of [0, N]) {
            const gx = x.createLinearGradient(0, y0, 0, y0 + h - drop);
            gx.addColorStop(0, css(c, 0.92)); gx.addColorStop(1, css(c, 1.05));
            x.fillStyle = gx; x.fillRect(xx + ox + 1, y0, ww - 2, h - drop - 4);
            const gb = b.createLinearGradient(0, y0, 0, y0 + h - drop);
            gb.addColorStop(0, 'rgb(120,120,120)'); gb.addColorStop(1, 'rgb(235,235,235)');
            b.fillStyle = gb; b.fillRect(xx + ox + 1, y0, ww - 2, h - drop - 4);
          }
          xx += ww;
        }
        // the shadow line cast by each course onto the one below (image y grows down the roof)
        const gs = x.createLinearGradient(0, y0 + h - 5, 0, y0 + h + 7);
        gs.addColorStop(0, 'rgba(0,0,0,0.55)'); gs.addColorStop(1, 'rgba(0,0,0,0)');
        x.fillStyle = gs; x.fillRect(0, y0 + h - 5, N, 12);
      }
      grain(x, N, r, 0.45, 0.08); grain(x, N, r, 0.3); grain(b, N, r, 0.3);
      blotch(x, N, r, 8, [80, 260], 'rgba(20,20,20,0.10)');
      blotch(x, N, r, 5, [60, 200], 'rgba(150,140,120,0.08)');
    });
  }
  // Broom-finished concrete with stains.
  function concreteTex(base) {
    const key = 'conc|' + hex(base);
    return tex(key, 3.0, 1024, (x, b, N, r) => {
      const B = rgb(base);
      x.fillStyle = css(B); x.fillRect(0, 0, N, N);
      b.fillStyle = '#808080'; b.fillRect(0, 0, N, N);
      for (let i = 0; i < 1400; i++) {
        const yy = r() * N, a = 0.03 + r() * 0.06;
        x.fillStyle = 'rgba(0,0,0,' + a + ')'; x.fillRect(0, yy, N, 1);
        b.fillStyle = 'rgba(' + (r() < 0.5 ? '0,0,0' : '255,255,255') + ',0.25)'; b.fillRect(0, yy, N, 1 + r());
      }
      blotch(x, N, r, 26, [30, 180], 'rgba(60,55,45,0.09)');
      blotch(x, N, r, 12, [40, 160], 'rgba(255,250,240,0.07)');
      grain(x, N, r, 0.07); grain(b, N, r, 0.2);
    });
  }
  // Rough-sawn cedar boards (vertical grain), one board per 1/8 of the tile.
  function cedarTex(base) {
    const key = 'cedar|' + hex(base);
    return tex(key, 1.2, 512, (x, b, N, r) => {
      const B = rgb(base);
      x.fillStyle = css(B); x.fillRect(0, 0, N, N);
      b.fillStyle = '#808080'; b.fillRect(0, 0, N, N);
      for (let i = 0; i < 260; i++) {
        const xx = r() * N, a = 0.05 + r() * 0.12, dx = (r() - 0.5) * 8;
        x.strokeStyle = r() < 0.7 ? 'rgba(40,20,10,' + a + ')' : 'rgba(255,230,200,' + a * 0.6 + ')';
        x.lineWidth = 0.6 + r() * 1.8; x.beginPath(); x.moveTo(xx, 0);
        x.bezierCurveTo(xx + dx, N / 3, xx - dx, 2 * N / 3, xx, N); x.stroke();
        b.strokeStyle = 'rgba(0,0,0,' + a + ')'; b.lineWidth = 1; b.beginPath(); b.moveTo(xx, 0); b.lineTo(xx, N); b.stroke();
      }
      for (let i = 0; i < 5; i++) { const kx = r() * N, ky = r() * N; x.fillStyle = 'rgba(50,25,10,0.5)'; x.beginPath(); x.ellipse(kx, ky, 3 + r() * 4, 5 + r() * 7, 0, 0, 6.3); x.fill(); }
      grain(x, N, r, 0.1, 0.03);
    });
  }
  // What is behind a window: a room, mostly dark, with mini-blinds or a curtain in it.
  function interiorTex(kind) {
    return tex('interior|' + kind, 1, 256, (x, b, N, r) => {
      const g = x.createLinearGradient(0, 0, 0, N);
      g.addColorStop(0, '#3a332c'); g.addColorStop(1, '#16130f');
      x.fillStyle = g; x.fillRect(0, 0, N, N);
      if (kind === 'blinds') {
        const down = 0.35 + r() * 0.5;
        for (let y = 0; y < N * down; y += 7) {
          const gg = x.createLinearGradient(0, y, 0, y + 6);
          gg.addColorStop(0, '#d8d2c4'); gg.addColorStop(1, '#8e877a');
          x.fillStyle = gg; x.fillRect(0, y, N, 6);
        }
      } else if (kind === 'curtain') {
        for (let xx = 0; xx < N; xx += 2) {
          const v = 0.55 + 0.45 * Math.sin(xx * 0.09 + r() * 0.3);
          x.fillStyle = 'rgba(' + Math.round(200 * v) + ',' + Math.round(188 * v) + ',' + Math.round(160 * v) + ',0.9)';
          x.fillRect(xx, 0, 2, N);
        }
        x.fillStyle = 'rgba(0,0,0,0.9)'; x.fillRect(N * 0.32, 0, N * 0.36, N);
      } else {
        // an unlit room: a ceiling line, a lamp-shaped glow, a picture on the far wall
        x.fillStyle = 'rgba(255,220,170,0.06)'; x.fillRect(0, 0, N, N * 0.3);
        x.fillStyle = 'rgba(90,70,50,0.6)'; x.fillRect(N * 0.2, N * 0.25, N * 0.25, N * 0.18);
      }
      grain(x, N, r, 0.08);
    });
  }

  /* ---------------------------------------------------------------------------------------
   * materials, cached by an explicit key (never JSON of a texture)
   * ------------------------------------------------------------------------------------- */
  const MC = new Map();
  function mat(key, make) { if (!MC.has(key)) MC.set(key, make()); return MC.get(key); }
  const std = (key, p) => mat(key, () => new THREE.MeshStandardMaterial(Object.assign({ roughness: 0.8, metalness: 0 }, p)));
  function texMat(T, key, extra) {
    return mat('tm|' + key, () => new THREE.MeshStandardMaterial(Object.assign({
      color: 0xffffff, map: T.map, bumpMap: T.bump, bumpScale: 1.6, roughness: 0.88, metalness: 0 }, extra || {})));
  }
  const paint = (c, rough) => std('paint|' + c + '|' + (rough || 0.55), { color: c, roughness: rough || 0.55 });
  const metal = (c, rough) => std('metal|' + c + '|' + (rough || 0.4), { color: c, roughness: rough || 0.4, metalness: 0.6 });
  const glass = () => mat('glass', () => new THREE.MeshPhysicalMaterial({
    color: 0x2a3438, roughness: 0.02, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.02,
    reflectivity: 0.6, envMapIntensity: 1.9, transparent: true, opacity: 0.62, depthWrite: true }));
  const interior = (kind) => mat('int|' + kind, () => new THREE.MeshBasicMaterial({ map: interiorTex(kind).map, color: 0x9a9a9a }));
  /* A double-sided card lit by ONE normal: three flips the normal on a back face, which turns
   * every blade or leaf card seen from behind black. Foliage wants the same light on both faces. */
  function oneFace(m) {
    m.onBeforeCompile = (sh) => {
      sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>',
        THREE.ShaderChunk.normal_fragment_begin.replace('float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;', 'float faceDirection = 1.0;'));
    };
    return m;
  }
  const brass = () => std('brass', { color: 0xc8a45a, metalness: 1, roughness: 0.3 });

  /* ---------------------------------------------------------------------------------------
   * the bucket: geometry baked into group space, merged per material at the end
   * ------------------------------------------------------------------------------------- */
  function Bucket() {
    const parts = new Map();
    const B = {
      add(m, geo) { if (!parts.has(m)) parts.set(m, []); parts.get(m).push(geo); return geo; },
      flush(group) {
        for (const [m, list] of parts) {
          const meshes = list.map((g) => {
            if (!g.attributes.uv) g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
            if (!g.attributes.normal) g.computeVertexNormals();
            return new THREE.Mesh(g);
          });
          if (m.vertexColors) list.forEach((g) => { if (!g.attributes.color) tint(g, [1, 1, 1]); });
          const colored = list.every((g) => g.attributes.color);
          let mesh;
          if (colored) mesh = mergeColored(list, m); else mesh = K.merge(meshes, m);
          if (m.transparent) mesh.renderOrder = 2;
          group.add(mesh);
        }
        parts.clear();
        return group;
      },
    };
    return B;
  }
  function mergeColored(list, m) {
    let n = 0; list.forEach((g) => { if (g.index) g = g.toNonIndexed(); n += g.attributes.position.count; });
    const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2), col = new Float32Array(n * 3);
    let o = 0;
    list.forEach((g0) => {
      const g = g0.index ? g0.toNonIndexed() : g0;
      pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
      uv.set(g.attributes.uv.array, o * 2); col.set(g.attributes.color.array, o * 3);
      o += g.attributes.position.count;
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    return new THREE.Mesh(geo, m);
  }
  const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), S1 = new V3(1, 1, 1);
  // bake a transform into a geometry: position (x, y, z), rotation about y then x then z
  function bake(g, x, y, z, ry, rx, rz, M) {
    E.set(rx || 0, ry || 0, rz || 0, 'YXZ'); Q.setFromEuler(E);
    M4.compose(new V3(x || 0, y || 0, z || 0), Q, S1); g.applyMatrix4(M4);
    if (M) g.applyMatrix4(M);
    return g;
  }
  // a box on its base: centre x, base y0, centre z
  function bx(B, m, w, h, d, x, y0, z, o) {
    o = o || {};
    const g = o.r ? TXT.roundedBox(w, h, d, o.r, null, { segments: o.seg || 1 }) : new THREE.BoxGeometry(w, h, d);
    bake(g, x, y0 + h / 2, z, o.ry, o.rx, o.rz, o.M);
    if (o.uv) K.uvBox(g, o.uv);
    if (o.color) tint(g, o.color);
    return B.add(m, g);
  }
  function cy(B, m, rt, rb, h, x, y0, z, seg, o) {
    o = o || {};
    const g = new THREE.CylinderGeometry(rt, rb, h, seg || 12);
    bake(g, x, y0 + h / 2, z, o.ry, o.rx, o.rz, o.M);
    return B.add(m, g);
  }
  function tint(g, c) {
    const n = g.attributes.position.count, a = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { a[i * 3] = c[0]; a[i * 3 + 1] = c[1]; a[i * 3 + 2] = c[2]; }
    g.setAttribute('color', new THREE.BufferAttribute(a, 3));
    return g;
  }
  // a thin bar between two points, square section (trim, rails, rake boards)
  function beam(B, m, a, b, w, h, o) {
    o = o || {};
    const A = new V3(...a), Bv = new V3(...b), len = A.distanceTo(Bv);
    const g = new THREE.BoxGeometry(w, h, len);
    const dir = Bv.clone().sub(A).normalize();
    const up = Math.abs(dir.y) > 0.99 ? new V3(1, 0, 0) : new V3(0, 1, 0);
    const mm = new THREE.Matrix4().lookAt(new V3(0, 0, 0), dir, up);
    if (o.roll) mm.multiply(new THREE.Matrix4().makeRotationZ(o.roll));
    mm.setPosition(A.clone().add(Bv).multiplyScalar(0.5));
    g.applyMatrix4(mm);
    if (o.uv) K.uvBox(g, o.uv);
    return B.add(m, g);
  }
  // a planar polygon (triangle fan, convex) with UVs from explicit axes, metres per tile
  function poly(B, m, pts, uAxis, vAxis, origin, metres, flip) {
    const n = pts.length, pos = [], uv = [], nor = [];
    const a = new V3(...pts[0]), bb = new V3(...pts[1]), c = new V3(...pts[2]);
    const N = bb.clone().sub(a).cross(c.clone().sub(a)).normalize(); if (flip) N.negate();
    const O = new V3(...origin);
    const push = (p) => { const P = new V3(...p); pos.push(P.x, P.y, P.z); nor.push(N.x, N.y, N.z);
      const d = P.clone().sub(O); uv.push(d.dot(uAxis) / metres, d.dot(vAxis) / metres); };
    for (let i = 1; i < n - 1; i++) {
      if (flip) { push(pts[0]); push(pts[i + 1]); push(pts[i]); } else { push(pts[0]); push(pts[i]); push(pts[i + 1]); }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    return B.add(m, g);
  }
  // a local frame for building a thing on a wall: origin at the wall's outer face, +z out of it
  function frameM(x, y, z, ry) { return new THREE.Matrix4().compose(new V3(x, y, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, ry, 0)), S1); }

  /* ---------------------------------------------------------------------------------------
   * walls with openings
   *   wallRun(B, m, uvm, M, L, H, t, openings): the wall's outer face on z = 0 of frame M, running
   *   u = 0..L along +x, thickness into -z, base at y = 0. Openings [{u, w, y, h}] (u = centre).
   * ------------------------------------------------------------------------------------- */
  function wallRun(B, m, uvm, M, L, H, t, openings) {
    const ops = (openings || []).map((o) => ({ a: o.u - o.w / 2, b: o.u + o.w / 2, y0: o.y, y1: o.y + o.h }));
    const piece = (u0, u1, y0, y1) => {
      if (u1 - u0 < 1e-3 || y1 - y0 < 1e-3) return;
      const g = new THREE.BoxGeometry(u1 - u0, y1 - y0, t);
      g.translate((u0 + u1) / 2, (y0 + y1) / 2, -t / 2); g.applyMatrix4(M); K.uvBox(g, uvm); B.add(m, g);
    };
    // columns between every opening edge; in each, solid spans between the openings that cross it
    const cuts = [0, L]; ops.forEach((o) => cuts.push(Math.max(0, Math.min(L, o.a)), Math.max(0, Math.min(L, o.b))));
    cuts.sort((x, y) => x - y);
    for (let i = 0; i < cuts.length - 1; i++) {
      const u0 = cuts[i], u1 = cuts[i + 1];
      if (u1 - u0 < 1e-4) continue;
      const mid = (u0 + u1) / 2, holes = ops.filter((o) => o.a < mid && o.b > mid).sort((x, y) => x.y0 - y.y0);
      let y = 0;
      for (const h of holes) { piece(u0, u1, y, h.y0); y = Math.max(y, h.y1); }
      piece(u0, u1, y, H);
    }
  }

  /* a window unit for a wall opening, in the wall's local frame M (opening centred on u, bottom
   * at y, outer wall face z = 0). Single-hung: a fixed top sash, a sliding bottom one proud of it. */
  function windowUnit(B, M, o, r) {
    const w = o.w, h = o.h, u = o.u, y = o.y, fc = paint(o.frame, 0.45), rec = o.recess != null ? o.recess : 0.07;
    const fw = 0.05, fd = 0.09, zf = -rec;
    const add = (g) => { g.applyMatrix4(M); return g; };
    const bxl = (m, ww, hh, dd, x, y0, z) => { const g = new THREE.BoxGeometry(ww, hh, dd); g.translate(x, y0 + hh / 2, z); B.add(m, add(g)); };
    // outer frame
    bxl(fc, w, fw, fd, u, y + h - fw, zf - fd / 2);
    bxl(fc, w, fw, fd, u, y, zf - fd / 2);
    bxl(fc, fw, h, fd, u - w / 2 + fw / 2, y, zf - fd / 2);
    bxl(fc, fw, h, fd, u + w / 2 - fw / 2, y, zf - fd / 2);
    const cols = o.cols || 1, iw = w - 2 * fw, ih = h - 2 * fw;
    const colW = iw / cols;
    const kind = o.interior || 'blinds';
    for (let c = 0; c < cols; c++) {
      const cu = u - iw / 2 + colW * (c + 0.5);
      if (c > 0) bxl(fc, 0.07, ih, fd, u - iw / 2 + colW * c, y + fw, zf - fd / 2);
      const sashes = o.fixed ? [[y + fw, ih, zf - 0.05]] : [[y + fw + ih / 2 - 0.01, ih / 2 + 0.01, zf - 0.065], [y + fw, ih / 2 + 0.02, zf - 0.03]];
      sashes.forEach(([sy, sh, sz], si) => {
        const sw = colW - 0.03, sf = 0.038;
        bxl(fc, sw, sf, 0.035, cu, sy + sh - sf, sz);
        bxl(fc, sw, si === 1 ? 0.055 : sf, 0.035, cu, sy, sz);     // the bottom sash's bottom rail is heavier
        bxl(fc, sf, sh, 0.035, cu - sw / 2 + sf / 2, sy, sz);
        bxl(fc, sf, sh, 0.035, cu + sw / 2 - sf / 2, sy, sz);
        const gw = sw - 2 * sf, gh = sh - 2 * sf, gy = sy + sf;
        const gl = new THREE.PlaneGeometry(gw, gh); gl.translate(cu, gy + gh / 2, sz - 0.004); B.add(glass(), add(gl));
        if (o.grids) {
          const gc = o.grids;
          for (let i = 1; i < gc[0]; i++) bxl(fc, 0.016, gh, 0.012, cu - gw / 2 + gw * i / gc[0], gy, sz + 0.004);
          for (let i = 1; i < gc[1]; i++) bxl(fc, gw, 0.016, 0.012, cu, gy + gh * i / gc[1] - 0.008, sz + 0.004);
        }
      });
      // the room behind it
      const ip = new THREE.PlaneGeometry(colW + 0.3, ih + 0.3); ip.translate(cu, y + fw + ih / 2, -o.t - 0.002);
      B.add(interior(c % 2 && kind === 'blinds' && r() < 0.5 ? 'curtain' : kind), add(ip));
    }
    // reveal liner behind the frame (a dark jamb so no hollow wall shows), sill and lintel
    const jm = paint(0x2e2a26, 0.9);
    bxl(jm, w + 0.02, 0.01, o.t, u, y + h, -o.t / 2);
    if (o.sill !== false) {
      const sm = o.sillMat || paint(0xd8cfbd, 0.85);
      const sg = new THREE.BoxGeometry(w + 0.12, 0.075, rec + 0.07); sg.translate(u, y - 0.0375, -rec / 2 + 0.035);
      sg.rotateX(0); B.add(sm, add(sg));
    }
    if (o.lintel !== false) bxl(metal(0x2c2926, 0.6), w + 0.24, 0.012, 0.012, u, y + h, 0.004);
    // shutters: louvred, fixed open, one each side
    if (o.shutters) {
      const sc = paint(o.shutters, 0.5), sw2 = Math.min(0.42, w * 0.38);
      for (const side of [-1, 1]) {
        const sx = u + side * (w / 2 + 0.05 + sw2 / 2);
        bxl(sc, sw2, h + 0.04, 0.03, sx, y - 0.02, 0.02);
        const n = Math.floor(h / 0.06);
        for (let i = 1; i < n; i++) {
          const g = new THREE.BoxGeometry(sw2 - 0.08, 0.045, 0.012);
          g.rotateX(-0.5); g.translate(sx, y + i * (h / n), 0.04); B.add(sc, add(g));
        }
        bxl(sc, sw2, 0.05, 0.02, sx, y + h / 2 - 0.025, 0.04);
      }
    }
  }

  /* a front door in its opening: a six-panel steel door, casing, threshold, knob and deadbolt */
  function doorUnit(B, M, o) {
    const u = o.u, y = o.y, w = o.w || 0.91, h = o.h || 2.03, t = o.t, trim = paint(o.trim, 0.5), dc = paint(o.color, 0.4);
    const add = (g) => { g.applyMatrix4(M); return g; };
    const bxl = (m, ww, hh, dd, x, y0, z, rr) => {
      const g = rr ? TXT.roundedBox(ww, hh, dd, rr, null, { segments: 1 }) : new THREE.BoxGeometry(ww, hh, dd);
      g.translate(x, y0 + hh / 2, z); B.add(m, add(g));
    };
    const zd = -0.12;
    bxl(dc, w, h, 0.045, u, y, zd);
    // raised panels: 2 across, 3 high (short top, tall middle, medium bottom)
    const pw = w * 0.34, rows = [[0.12, 0.62], [0.86, 0.72], [1.7, 0.24]];
    for (const [py, ph] of rows) for (const s of [-1, 1]) {
      bxl(dc, pw, ph * (h / 2.03), 0.02, u + s * w * 0.22, y + py * (h / 2.03), zd + 0.028, 0.008);
    }
    const kx = u + w / 2 - 0.08;
    const knob = new THREE.SphereGeometry(0.028, 12, 8); knob.translate(kx, y + 0.92, zd + 0.07); B.add(brass(), add(knob));
    const rose = new THREE.CylinderGeometry(0.03, 0.03, 0.02, 14); rose.rotateX(Math.PI / 2); rose.translate(kx, y + 0.92, zd + 0.035); B.add(brass(), add(rose));
    const db = new THREE.CylinderGeometry(0.028, 0.028, 0.02, 14); db.rotateX(Math.PI / 2); db.translate(kx, y + 1.08, zd + 0.035); B.add(brass(), add(db));
    // casing and jambs
    const cw = 0.09;
    bxl(trim, cw, h + cw, 0.025, u - w / 2 - cw / 2 + 0.01, y, 0.0125);
    bxl(trim, cw, h + cw, 0.025, u + w / 2 + cw / 2 - 0.01, y, 0.0125);
    bxl(trim, w + 2 * cw, cw, 0.025, u, y + h, 0.0125);
    bxl(trim, 0.02, h, t, u - w / 2 - 0.01, y, -t / 2);
    bxl(trim, 0.02, h, t, u + w / 2 + 0.01, y, -t / 2);
    bxl(trim, w + 0.04, 0.02, t, u, y + h, -t / 2);
    bxl(metal(0xa08c64, 0.4), w + 0.04, 0.02, t + 0.04, u, y, -t / 2 + 0.02);
  }

  /* a sectional garage door: raised short panels, 4 sections, optional windows in the top one */
  function garageDoor(B, M, o, r) {
    const u = o.u, y = o.y, w = o.w, h = o.h, t = o.t, dc = paint(o.color, 0.42), trim = paint(o.trim, 0.5);
    const add = (g) => { g.applyMatrix4(M); return g; };
    const bxl = (m, ww, hh, dd, x, y0, z, rr) => {
      const g = rr ? TXT.roundedBox(ww, hh, dd, rr, null, { segments: 1 }) : new THREE.BoxGeometry(ww, hh, dd);
      g.translate(x, y0 + hh / 2, z); B.add(m, add(g));
    };
    const zd = -0.1, secs = 4, sh = h / secs, cols = Math.max(4, Math.round(w / 0.6));
    const seam = paint(0x2a2826, 0.9);
    for (let s = 0; s < secs; s++) {
      const sy = y + s * sh;
      bxl(dc, w, sh - 0.012, 0.04, u, sy + 0.006, zd);
      bxl(seam, w, 0.012, 0.03, u, sy, zd - 0.005);
      for (let c = 0; c < cols; c++) {
        const cx = u - w / 2 + (c + 0.5) * (w / cols), pw = w / cols - 0.1, ph = sh - 0.16;
        if (s === secs - 1 && o.windows) {
          bxl(dc, pw + 0.02, ph + 0.02, 0.012, cx, sy + 0.07, zd + 0.024);
          const gl = new THREE.PlaneGeometry(pw - 0.04, ph - 0.04); gl.translate(cx, sy + 0.08 + (ph - 0.04) / 2 + 0.01, zd + 0.032); B.add(glass(), add(gl));
          const ip = new THREE.PlaneGeometry(pw + 0.1, ph + 0.1); ip.translate(cx, sy + 0.08 + ph / 2, zd - 0.05); B.add(interior('room'), add(ip));
        } else {
          bxl(dc, pw, ph, 0.018, cx, sy + 0.08, zd + 0.026, 0.006);
        }
      }
    }
    // weather seal at the bottom, stop moulding and brick mould trim
    bxl(paint(0x1d1d1d, 0.8), w, 0.02, 0.05, u, y + 0.002, zd);
    const cw = 0.1;
    bxl(trim, cw, h + cw, 0.03, u - w / 2 - cw / 2 + 0.01, y, 0.015);
    bxl(trim, cw, h + cw, 0.03, u + w / 2 + cw / 2 - 0.01, y, 0.015);
    bxl(trim, w + 2 * cw, cw, 0.03, u, y + h, 0.015);
    bxl(trim, 0.02, h, t, u - w / 2 - 0.01, y, -t / 2);
    bxl(trim, 0.02, h, t, u + w / 2 + 0.01, y, -t / 2);
    bxl(trim, w, 0.02, t, u, y + h, -t / 2);
    const ip = new THREE.PlaneGeometry(w + 0.4, h + 0.4); ip.translate(u, y + h / 2, -t - 0.01); B.add(interior('room'), add(ip));
  }

  /* a coach lantern by a door: black box with warm panes */
  function lantern(B, M, u, y) {
    const add = (g) => { g.applyMatrix4(M); return g; };
    const blk = paint(0x191919, 0.5);
    const g1 = new THREE.BoxGeometry(0.09, 0.2, 0.03); g1.translate(u, y + 0.1, 0.015); B.add(blk, add(g1));
    const g2 = new THREE.BoxGeometry(0.16, 0.26, 0.16); g2.translate(u, y + 0.1, 0.12); B.add(mat('lanternglass', () => new THREE.MeshStandardMaterial({ color: 0xf2dcae, emissive: 0xffc27a, emissiveIntensity: 0.25, roughness: 0.2 })), add(g2));
    const g3 = new THREE.ConeGeometry(0.13, 0.1, 4); g3.rotateY(Math.PI / 4); g3.translate(u, y + 0.28, 0.12); B.add(blk, add(g3));
    for (const [dx, dz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      const g = new THREE.BoxGeometry(0.014, 0.27, 0.014); g.translate(u + dx * 0.08, y + 0.1, 0.12 + dz * 0.08); B.add(blk, add(g));
    }
  }

  /* ---------------------------------------------------------------------------------------
   * roofs: hip and gable, with overhang, fascia, soffit, drip edge, caps and gutters
   * ------------------------------------------------------------------------------------- */
  function hipRoof(B, o) {
    // o: x0, x1, z0, z1 (the EAVE rectangle, overhang included), ye (eave height, top of fascia),
    // pitch (rise/run), roof material+uvm, trim, fascia height fh, gutters {front, back, left, right}
    const { x0, x1, z0, z1, ye, pitch } = o, rm = o.roofMat, uvm = o.uvm;
    const W = x1 - x0, D = z1 - z0, cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    const alongX = W >= D, half = (alongX ? D : W) / 2, yr = ye + half * pitch;
    let r0, r1;
    if (alongX) { r0 = [x0 + half, yr, cz]; r1 = [x1 - half, yr, cz]; }
    else { r0 = [cx, yr, z0 + half]; r1 = [cx, yr, z1 - half]; }
    const c00 = [x0, ye, z0], c10 = [x1, ye, z0], c11 = [x1, ye, z1], c01 = [x0, ye, z1];
    const slope = (dx, dz) => new V3(-dx, pitch, -dz).normalize();   // up the slope, from an eave whose outward normal is (dx, 0, dz)
    const face = (pts, dx, dz, eaveO) => {
      const s = slope(dx, dz), e = new V3(dz, 0, -dx);
      poly(B, rm, pts, e, s, eaveO, uvm);
    };
    if (alongX) {
      face([c01, c11, r1, r0], 0, 1, c01);       // front
      face([c10, c00, r0, r1], 0, -1, c00);      // back
      face([c00, c01, r0], -1, 0, c00);          // left
      face([c11, c10, r1], 1, 0, c10);           // right
    } else {
      face([c11, c10, r0, r1], 1, 0, c10);
      face([c00, c01, r1, r0], -1, 0, c00);
      face([c01, c11, r1], 0, 1, c01);
      face([c10, c00, r0], 0, -1, c00);
    }
    // ridge and hip caps
    const cap = o.capMat || rm, cw = 0.24, ct = 0.035;
    beam(B, cap, r0, r1, cw, ct);
    const lift = (p, k) => [p[0], p[1] + k, p[2]];
    if (alongX) { [[c00, r0], [c01, r0], [c10, r1], [c11, r1]].forEach(([a, b]) => beam(B, cap, lift(a, 0.01), lift(b, 0.01), 0.2, ct)); }
    else { [[c00, r0], [c10, r0], [c01, r1], [c11, r1]].forEach(([a, b]) => beam(B, cap, lift(a, 0.01), lift(b, 0.01), 0.2, ct)); }
    eaveTrim(B, o, [[c01, c11, 0, 1, 'front'], [c10, c00, 0, -1, 'back'], [c00, c01, -1, 0, 'left'], [c11, c10, 1, 0, 'right']]);
    return { yr };
  }
  // fascia, drip edge, soffit and gutters along level eaves [a, b, nx, nz, side]
  function eaveTrim(B, o, edges) {
    const fh = o.fh || 0.2, fm = paint(o.trim, 0.55), sm = paint(o.soffit != null ? o.soffit : o.trim, 0.7);
    const gm = paint(o.gutter != null ? o.gutter : o.trim, 0.35);
    for (const [a, b, nx, nz, side] of edges) {
      const L = Math.hypot(b[0] - a[0], b[2] - a[2]), mx = (a[0] + b[0]) / 2, mz = (a[2] + b[2]) / 2, ry = Math.atan2(nx, nz);
      bx(B, fm, L + 0.05, fh, 0.03, mx - nx * 0.015, o.ye - fh, mz - nz * 0.015, { ry });
      bx(B, metal(0x4a4642, 0.5), L + 0.06, 0.025, 0.045, mx + nx * 0.005, o.ye - 0.012, mz + nz * 0.005, { ry });
      if (o.gutters && o.gutters[side]) {
        // K-style gutter: a face with an ogee lip and a back, and a bead on top
        bx(B, gm, L + 0.04, 0.125, 0.012, mx + nx * 0.125, o.ye - 0.15, mz + nz * 0.125, { ry });
        bx(B, gm, L + 0.04, 0.012, 0.12, mx + nx * 0.065, o.ye - 0.15, mz + nz * 0.065, { ry });
        bx(B, gm, L + 0.04, 0.02, 0.02, mx + nx * 0.13, o.ye - 0.03, mz + nz * 0.13, { ry });
        bx(B, gm, L + 0.04, 0.03, 0.02, mx + nx * 0.118, o.ye - 0.105, mz + nz * 0.118, { ry });
        const ends = o.gutters[side] === true ? [0.08, L - 0.08] : o.gutters[side];
        for (const t of ends) {
          const px = a[0] + (b[0] - a[0]) * t / L, pz = a[2] + (b[2] - a[2]) * t / L;
          downspout(B, gm, px + nx * 0.07, pz + nz * 0.07, o.ye - 0.15, nx, nz, o.wallOff || 0.5, ry);
        }
      }
    }
    // soffit: one lid under the whole eave rectangle, vented strip near the fascia
    const sg = new THREE.BoxGeometry(o.x1 - o.x0 - 0.06, 0.012, o.z1 - o.z0 - 0.06);
    sg.translate((o.x0 + o.x1) / 2, o.ye - fh + 0.006, (o.z0 + o.z1) / 2); B.add(sm, sg);
  }
  function downspout(B, m, x, z, ytop, nx, nz, wallOff, ry) {
    // a 2x3 rectangular downspout: elbow back to the wall, straight down, kick-out at the foot
    const back = wallOff + 0.02;
    const wx = x - nx * back, wz = z - nz * back;
    beam(B, m, [x, ytop, z], [wx + nx * 0.06, ytop - 0.35, wz + nz * 0.06], 0.075, 0.055);
    bx(B, m, 0.075, ytop - 0.35 - 0.3, 0.055, wx + nx * 0.06, 0.3, wz + nz * 0.06, { ry });
    beam(B, m, [wx + nx * 0.06, 0.34, wz + nz * 0.06], [wx + nx * 0.3, 0.08, wz + nz * 0.3], 0.075, 0.055);
    bx(B, paint(0x9c978d, 0.95), 0.3, 0.05, 0.6, wx + nx * 0.5, 0, wz + nz * 0.5, { ry });  // splash block
  }
  // a gable roof over [x0,x1]x[z0,z1] (eave rectangle); ridge along 'x' or 'z'. gableEnds: which
  // ends get a gable wall and rake trim ('+' / '-' / both); a buried end is left open.
  function gableRoof(B, o) {
    const { x0, x1, z0, z1, ye, pitch, axis } = o, rm = o.roofMat, uvm = o.uvm;
    const rk = o.rake || 0.3;           // rake overhang beyond the gable wall
    const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    const fh = o.fh || 0.2, fm = paint(o.trim, 0.55), ends = o.ends || ['-', '+'];
    if (axis === 'x') {
      const half = (z1 - z0) / 2, yr = ye + half * pitch;
      const L0 = x0, L1 = x1;
      poly(B, rm, [[L0, ye, z1], [L1, ye, z1], [L1, yr, cz], [L0, yr, cz]], new V3(1, 0, 0), new V3(0, pitch, -1).normalize(), [L0, ye, z1], uvm);
      poly(B, rm, [[L1, ye, z0], [L0, ye, z0], [L0, yr, cz], [L1, yr, cz]], new V3(-1, 0, 0), new V3(0, pitch, 1).normalize(), [L1, ye, z0], uvm);
      beam(B, o.capMat || rm, [L0, yr + 0.01, cz], [L1, yr + 0.01, cz], 0.24, 0.035);
      // rake boards on the gable ends (sloped fascia) and the roof edge thickness
      for (const e of ends) {
        const X = e === '+' ? L1 : L0, nx = e === '+' ? 1 : -1;
        for (const zz of [z0, z1]) {
          const g = beam(B, fm, [X - nx * 0.015, ye - fh / 2 + 0.02, zz], [X - nx * 0.015, yr - fh / 2 + 0.03, cz], 0.03, fh + 0.02);
        }
      }
      eaveTrim(B, Object.assign({}, o, { x0: L0, x1: L1 }), [[[L0, ye, z1], [L1, ye, z1], 0, 1, 'front'], [[L1, ye, z0], [L0, ye, z0], 0, -1, 'back']]);
      return { yr, half };
    } else {
      const half = (x1 - x0) / 2, yr = ye + half * pitch;
      poly(B, rm, [[x1, ye, z1], [x1, ye, z0], [cx, yr, z0], [cx, yr, z1]], new V3(0, 0, -1), new V3(-1, pitch, 0).normalize(), [x1, ye, z1], uvm);
      poly(B, rm, [[x0, ye, z0], [x0, ye, z1], [cx, yr, z1], [cx, yr, z0]], new V3(0, 0, 1), new V3(1, pitch, 0).normalize(), [x0, ye, z0], uvm);
      beam(B, o.capMat || rm, [cx, yr + 0.01, z0], [cx, yr + 0.01, z1], 0.24, 0.035);
      for (const e of ends) {
        const Z = e === '+' ? z1 : z0, nz = e === '+' ? 1 : -1;
        for (const xx of [x0, x1]) beam(B, fm, [xx, ye - fh / 2 + 0.02, Z - nz * 0.015], [cx, yr - fh / 2 + 0.03, Z - nz * 0.015], 0.03, fh + 0.02);
      }
      eaveTrim(B, Object.assign({}, o, { z0, z1 }), [[[x1, ye, z1], [x1, ye, z0], 1, 0, 'right'], [[x0, ye, z0], [x0, ye, z1], -1, 0, 'left']]);
      return { yr, half };
    }
  }
  // a gable wall triangle (siding, brick or stucco) with a vent louvre, in frame M (face z = 0)
  function gableWall(B, m, uvm, M, w, ybase, rise, t, vent, trimC, shoulder) {
    const sh = shoulder || 0;
    const shape = new THREE.Shape(sh > 0.001
      ? [new THREE.Vector2(-w / 2, 0), new THREE.Vector2(w / 2, 0), new THREE.Vector2(w / 2, sh), new THREE.Vector2(0, rise), new THREE.Vector2(-w / 2, sh)]
      : [new THREE.Vector2(-w / 2, 0), new THREE.Vector2(w / 2, 0), new THREE.Vector2(0, rise)]);
    const g = new THREE.ExtrudeGeometry(shape, { depth: t, bevelEnabled: false });
    g.translate(0, ybase, -t); g.applyMatrix4(M); K.uvBox(g, uvm); B.add(m, g);
    if (vent) {
      const vm = paint(trimC, 0.6), add = (gg) => { gg.applyMatrix4(M); return gg; };
      const vh = Math.min(0.7, rise * 0.4), vw = vh * 0.8, vy = ybase + rise * 0.35;
      const f = new THREE.BoxGeometry(vw + 0.08, vh + 0.08, 0.03); f.translate(0, vy + vh / 2, 0.015); B.add(vm, add(f));
      const n = Math.floor(vh / 0.06);
      for (let i = 0; i < n; i++) { const l = new THREE.BoxGeometry(vw, 0.04, 0.01); l.rotateX(-0.6); l.translate(0, vy + 0.03 + i * vh / n, 0.035); B.add(vm, add(l)); }
      const bk = new THREE.PlaneGeometry(vw, vh); bk.translate(0, vy + vh / 2, 0.031); B.add(paint(0x151515, 1), add(bk));
    }
  }

  /* roof furniture: a turbine vent (the whirlybird), a pipe stack, a satellite dish */
  function turbine(B, x, y, z) {
    const g = K.finish.galvanized();
    cy(B, g, 0.08, 0.08, 0.18, x, y, z, 12);
    const geo = new THREE.LatheGeometry([[0.0, 0.0], [0.16, 0.02], [0.18, 0.1], [0.15, 0.2], [0.06, 0.26], [0.001, 0.27]].map(p => new THREE.Vector2(p[0], p[1])), 18);
    geo.translate(x, y + 0.16, z); B.add(mat('turbvane', () => new THREE.MeshStandardMaterial({ color: 0xb0b3b5, metalness: 0.9, roughness: 0.35, flatShading: true })), geo);
  }

  /* ---------------------------------------------------------------------------------------
   * palettes
   * ------------------------------------------------------------------------------------- */
  const BRICKS = ['#8e4a33', '#a0583c', '#7c4637', '#9a6a4b', '#b48a62', '#8a5a48', '#a4624a', '#c0a07a'];
  const LIMES = ['#d3c3a0', '#cdb994', '#dccfb2', '#c9b58e'];
  const ROOFS = ['#5d564f', '#46484b', '#6e665c', '#393a3c', '#57524a', '#6a6660'];
  const TRIMS = [0xefece4, 0xe6dfcf, 0xf2f0ea, 0xd9d2c1];
  const DOORS = [0x6b1f1f, 0x1f2c44, 0x1b1b1b, 0x2f4a3c, 0x5a3a24, 0x7a6a50, 0x234b5a];
  const SIDINGS = ['#d8d1c1', '#c9c1ad', '#b6b8ae', '#d2c7ae', '#a9a998', '#e2ddd0'];
  const pick = (r, a) => a[Math.floor(r() * a.length) % a.length];
  const opt = (o, k, d) => (o[k] != null ? o[k] : d);

  /* =======================================================================================
   * ranch_house
   * ===================================================================================== */
  K.define('ranch_house', {
    size: [21, 5.2, 11.2],
    options: { material: null, color: null, brick: null, roof: null, trim: null, door: null, garage: 'right', chimney: null, gable: null, shutters: 'seeded' },
    note: 'Options (null = seeded choice): material brick|limestone|siding, color (wall colour, hex number or string; `brick` is an alias), roof (shingle colour), trim, door, garage right|left|none, chimney bool, gable (front gable over the garage) bool, shutters hex, null for none, seeded to choose. The Texas one-storey ranch: slab, brick/limestone/siding walls with real openings, single-hung windows with sills, a recessed front porch, a two-car garage with a sectional door, a hip roof with overhang, fascia, soffit, gutters and downspouts.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const material = opt(o, 'material', ['brick', 'brick', 'limestone', 'brick', 'siding'][Math.floor(r() * 5)]);
      if (o.brick != null && o.color == null) o = Object.assign({}, o, { color: hex(o.brick) });
      const trimC = opt(o, 'trim', pick(r, TRIMS)), doorC = opt(o, 'door', pick(r, DOORS));
      const roofC = opt(o, 'roof', pick(r, ROOFS));
      const garage = opt(o, 'garage', 'right'), chimney = opt(o, 'chimney', r() < 0.6);
      const frameC = r() < 0.45 ? 0x3d3129 : trimC;          // bronze aluminium or white vinyl windows
      const shutters = o.shutters !== undefined && o.shutters !== 'seeded' ? o.shutters : (r() < 0.45 ? pick(r, [0x243142, 0x1e1e1e, 0x3b4a3a, 0x5b2a24]) : null);
      let wallT;
      if (material === 'limestone') wallT = limestoneTex(hex(opt(o, 'color', pick(r, LIMES))));
      else if (material === 'siding') wallT = sidingTex(hex(opt(o, 'color', pick(r, SIDINGS))));
      else wallT = brickTex(hex(opt(o, 'color', pick(r, BRICKS))), pick(r, ['#bdb4a4', '#a9a293', '#c7bca8']));
      const wallM = texMat(wallT, 'wall|' + material + '|' + (o.color || '') + wallT.map.uuid, { bumpScale: material === 'siding' ? 1.2 : 2.2 });
      const sideT = material === 'brick' && r() < 0.0 ? sidingTex(pick(r, SIDINGS)) : wallT;
      const roofT = shingleTex(roofC), roofM = texMat(roofT, 'roof|' + roofC, { bumpScale: 2.4, roughness: 0.95 });
      const capM = texMat(roofT, 'cap|' + roofC, { bumpScale: 1.0, roughness: 0.95, color: 0xd8d8d8 });
      const concT = concreteTex('#b3ada2'), concM = texMat(concT, 'slab', { bumpScale: 0.6, roughness: 0.93 });

      // plan: main body + garage, one rectangle, front at +z
      const Wm = 13.4 + r() * 2.2, Wg = garage === 'none' ? 0 : 6.6, D = 9.6 + r() * 1.2;
      const W = Wm + Wg, t = 0.26, slabH = 0.18, H = 2.62;     // 8' plate plus a brick ledge
      const xL = -W / 2, xR = W / 2, zF = D / 2, zB = -D / 2;
      const gx0 = garage === 'left' ? xL : xR - Wg, gx1 = gx0 + Wg;          // garage extent
      const mx0 = garage === 'left' ? xL + Wg : xL, mx1 = mx0 + Wm;          // main body extent
      const ybase = slabH, ytop = slabH + H;

      // slab: exposed edge under the veneer, the porch and the garage floor at grade + 0.1
      bx(B, concM, W + 0.04, slabH, D + 0.04, 0, 0, 0, { uv: concT.metres });

      // front wall layout (main body): window bay | porch recess (door + sidelite window) | picture window
      const porchW = 3.0 + r() * 0.8, porchD = 1.7;
      const flip = garage === 'left';
      const L = (u) => (flip ? mx1 - u : mx0 + u);    // u measured from the end away from the garage
      const uP0 = Wm * 0.42 - porchW / 2 + (r() - 0.5) * 0.6, uP1 = uP0 + porchW;
      const frontOps = [];
      const winH = 1.52, sillY = 0.92, hdr = sillY + winH;
      // bedroom windows left of the porch
      const nLeft = uP0 > 5.5 ? 2 : 1;
      for (let i = 0; i < nLeft; i++) frontOps.push({ u: uP0 * (i + 0.5) / nLeft, w: 0.92 + (i === 0 && r() < 0.4 ? 0.9 : 0), y: sillY, h: winH, cols: 1 });
      if (frontOps.length === 2 && frontOps[0].w > 1.2) frontOps[0].cols = 2;
      // picture window (triple) right of the porch
      const rightLen = Wm - uP1;
      frontOps.push({ u: uP1 + rightLen * 0.5, w: Math.min(2.8, rightLen - 1.4), y: sillY - 0.2, h: winH + 0.2, cols: 3 });
      const grids = r() < 0.55 ? [2, 2] : null;

      // walls. front wall of the main body in two runs around the porch, porch back wall, returns
      const M_front = (u0) => frameM(flip ? L(u0) : L(u0), ybase, zF, 0);
      const runs = [[0, uP0], [uP1, Wm]];
      for (const [a, b] of runs) {
        const ops = frontOps.filter((q) => q.u > a && q.u < b).map((q) => Object.assign({}, q, { u: flip ? b - q.u : q.u - a }));
        const x0 = flip ? L(b) : L(a);
        const M = frameM(x0, ybase, zF, 0);
        wallRun(B, wallM, wallT.metres, M, b - a, H, t, ops);
        ops.forEach((q) => windowUnit(B, M, Object.assign({ frame: frameC, t, grids, shutters: q.cols === 1 ? shutters : null, interior: 'blinds' }, q), r));
      }
      // porch back wall: the door and a narrow window
      {
        const x0 = flip ? L(uP1) : L(uP0), M = frameM(x0, ybase, zF - porchD, 0);
        const du = porchW * 0.36, wu = porchW * 0.76;
        const ops = [{ u: du, w: 1.0, y: 0.0, h: 2.1, door: true }, { u: wu, w: 0.62, y: sillY, h: winH, cols: 1 }];
        wallRun(B, wallM, wallT.metres, M, porchW, H, t, ops);
        doorUnit(B, M, { u: du, y: 0.02, t, trim: trimC, color: doorC });
        windowUnit(B, M, { u: wu, w: 0.62, y: sillY, h: winH, frame: frameC, t, grids: grids ? [1, 2] : null, interior: 'curtain' }, r);
        lantern(B, M, du + 0.72, 1.55);
        // porch returns (left and right cheek walls)
        for (const [ux, ry] of [[0, -Math.PI / 2], [porchW, Math.PI / 2]]) {
          const xx = x0 + ux;
          const g2 = new THREE.BoxGeometry(t, H, porchD); g2.translate(xx + (ux === 0 ? -t / 2 : t / 2), ybase + H / 2, zF - porchD / 2); K.uvBox(g2, wallT.metres); B.add(wallM, g2);
        }
        // porch slab and a step
        bx(B, concM, porchW, 0.1, porchD + 0.3, x0 + porchW / 2, slabH, zF - porchD / 2 + 0.15, { uv: concT.metres });
        bx(B, concM, porchW * 0.6, 0.14, 0.4, x0 + porchW * 0.36, 0, zF + 0.45, { uv: concT.metres });
        const pc = paint(trimC, 0.55);
        // porch beam across the open front under the soffit
        bx(B, pc, porchW, 0.22, 0.14, x0 + porchW / 2, ytop - 0.22, zF - 0.07);
      }
      // garage front: a 16' sectional door
      if (garage !== 'none') {
        const M = frameM(gx0, ybase, zF, 0), gw = 4.88, gh = 2.13;
        wallRun(B, wallM, wallT.metres, M, Wg, H, t, [{ u: Wg / 2, w: gw, y: 0, h: gh }]);
        garageDoor(B, M, { u: Wg / 2, y: 0, w: gw, h: gh, t, color: r() < 0.7 ? trimC : 0x8a7a66, trim: trimC, windows: r() < 0.35 }, r);
        lantern(B, M, Wg / 2 - gw / 2 - 0.45, 1.5); lantern(B, M, Wg / 2 + gw / 2 + 0.45, 1.5);
        // the garage floor apron lip
        bx(B, concM, gw + 0.2, 0.02, 0.3, gx0 + Wg / 2, slabH - 0.02, zF + 0.1, { uv: concT.metres });
      }
      // side walls: windows on the house end, a service door on the garage end
      const endHouse = flip ? xR : xL, endGarage = flip ? xL : xR;
      {
        // left end (x = xL) faces -x: frame rotated -90deg, u runs from front to back
        const sides = [[xL, -Math.PI / 2, zB], [xR, Math.PI / 2, zF]];
        for (const [xs, ry, zs] of sides) {
          const M = frameM(xs, ybase, zs, ry);
          const isGarage = garage !== 'none' && xs === endGarage;
          const len = D - 0.0, inset = t;
          const ops = isGarage ? [{ u: D * 0.3, w: 0.92, y: 0.0, h: 2.03, door: true }, { u: D * 0.7, w: 0.92, y: sillY, h: winH }]
                               : [{ u: D * 0.28, w: 0.92, y: sillY, h: winH }, { u: D * 0.72, w: 0.92, y: sillY, h: winH }];
          // side walls sit between the front and back walls
          const M2 = new THREE.Matrix4().multiplyMatrices(M, new THREE.Matrix4().makeTranslation(t, 0, 0));
          wallRun(B, wallM, wallT.metres, M2, len - 2 * t, H, t, ops.map((q) => Object.assign({}, q, { u: q.u - t })));
          ops.forEach((q) => {
            if (q.door) doorUnit(B, M2, { u: q.u - t, y: 0.0, t, trim: trimC, color: trimC });
            else windowUnit(B, M2, Object.assign({ frame: frameC, t, grids, interior: isGarage ? 'room' : 'blinds' }, q, { u: q.u - t }), r);
          });
          if (isGarage) {
            // AC condenser on a pad and the electric meter, the side of every Texas garage
            const nx = Math.sign(xs);
            bx(B, concM, 1.0, 0.08, 1.0, xs + nx * 0.8, 0, D * 0.02, { uv: concT.metres });
            bx(B, paint(0x8d8f8a, 0.5), 0.78, 0.82, 0.78, xs + nx * 0.8, 0.08, D * 0.02, { r: 0.03 });
            bx(B, paint(0x2b2b2b, 0.7), 0.8, 0.02, 0.8, xs + nx * 0.8, 0.9, D * 0.02);
            cy(B, paint(0x1a1a1a, 0.6), 0.3, 0.3, 0.02, xs + nx * 0.8, 0.905, D * 0.02, 20);
            for (let i = 0; i < 12; i++) bx(B, paint(0x3a3a3a, 0.6), 0.79, 0.012, 0.79, xs + nx * 0.8, 0.14 + i * 0.058, D * 0.02);
            bx(B, metal(0x9da1a3, 0.45), 0.02, 0.4, 0.3, xs + nx * 0.01, 1.3, -D * 0.12);
            cy(B, glass(), 0.075, 0.075, 0.08, xs + nx * 0.06, 1.5, -D * 0.12, 16, { rz: Math.PI / 2 });
          }
        }
      }
      // back wall: windows and a patio slider
      {
        const M = frameM(xR, ybase, zB, Math.PI);
        const ops = [{ u: W * 0.2, w: 0.92, y: sillY, h: winH }, { u: W * 0.45, w: 2.4, y: 0.02, h: 2.03, fixed: true, cols: 2 },
                     { u: W * 0.7, w: 0.92, y: sillY, h: winH }];
        wallRun(B, wallM, wallT.metres, M, W, H, t, ops);
        ops.forEach((q) => windowUnit(B, M, Object.assign({ frame: frameC, t, interior: 'blinds' }, q), r));
      }

      // roof: one hip over everything, 6/12, 0.5 m overhang (+ a front gable over the garage)
      const ov = 0.5, pitch = 0.42 + r() * 0.12;
      const ye = ytop + 0.2;
      const gutterEnds = { front: [ov + 0.2, W + ov - 0.2], back: [ov + 0.2, W + ov - 0.2] };
      hipRoof(B, { x0: xL - ov, x1: xR + ov, z0: zB - ov, z1: zF + ov, ye, pitch, roofMat: roofM, capMat: capM, uvm: roofT.metres,
        trim: trimC, gutters: gutterEnds, wallOff: ov });
      if (garage !== 'none' && opt(o, 'gable', r() < 0.6)) {
        const gz1 = zF + ov + 0.05, gz0 = zF - 4.5;
        const gpitch = pitch + 0.08;
        gableRoof(B, { x0: gx0 - 0.35, x1: gx1 + 0.35, z0: gz0, z1: gz1, ye: ye + 0.01, pitch: gpitch, axis: 'z', roofMat: roofM,
          capMat: capM, uvm: roofT.metres, trim: trimC, ends: ['+'], gutters: {} });
        const rise = (Wg / 2 + 0.35) * gpitch;
        gableWall(B, material === 'siding' ? wallM : texMat(sidingTex(pick(r, SIDINGS)), 'gablesid|' + trimC, { bumpScale: 1.2 }),
          1.2446, frameM(gx0 + Wg / 2, ytop, zF + ov - 0.05, 0), Wg + 0.6, 0.2, rise - 0.05, 0.08, true, trimC);
      }
      // chimney: a brick chase through the back slope near the ridge, with a metal cap
      if (chimney) {
        const cx = (flip ? mx1 : mx0) + (flip ? -1 : 1) * Wm * 0.62, cz = -D * 0.12;
        const cT = material === 'limestone' ? wallT : (material === 'siding' ? brickTex(pick(r, BRICKS), '#b9b0a2') : wallT);
        const cm = cT === wallT ? wallM : texMat(cT, 'chim', { bumpScale: 2 });
        const top = ye + (D / 2 + ov) * pitch + 0.9;
        bx(B, cm, 1.1, top - ytop, 0.8, cx, ytop, cz, { uv: cT.metres });
        bx(B, metal(0x6d6e6c, 0.5), 1.22, 0.06, 0.92, cx, top, cz);
        cy(B, metal(0x3a3a3a, 0.5), 0.12, 0.12, 0.3, cx, top + 0.06, cz, 14);
        bx(B, metal(0x6d6e6c, 0.5), 0.4, 0.03, 0.4, cx, top + 0.38, cz);
      }
      // roof furniture on the back slope: turbines and a vent stack
      const yb = (z) => ye + (z - (zB - ov)) * pitch;
      for (let i = 0; i < 2; i++) { const tx = (i - 0.5) * W * 0.3, tz = zB + 1.2; turbine(B, tx, yb(tz) - 0.05, tz); }
      cy(B, paint(0x2b2b2b, 0.7), 0.045, 0.045, 0.35, W * 0.08, yb(zB + 2) - 0.1, zB + 2, 10);

      B.flush(g);
      return g;
    },
  });

  /* more painters: vinyl skirting, lawn, chain-link diamond */
  function skirtTex(base) {
    return tex('skirt|' + hex(base), 1.2, 512, (x, b, N, r) => {
      const B = rgb(base), n = 6, w = N / n;
      for (let i = 0; i < n; i++) {
        const g = x.createLinearGradient(i * w, 0, i * w + w, 0);
        g.addColorStop(0, css(B, 0.86)); g.addColorStop(0.1, css(B, 1.02)); g.addColorStop(0.5, css(B, 0.97)); g.addColorStop(0.55, css(B, 0.86)); g.addColorStop(0.6, css(B, 1.0)); g.addColorStop(1, css(B, 0.95));
        x.fillStyle = g; x.fillRect(i * w, 0, w, N);
        const gb = b.createLinearGradient(i * w, 0, i * w + w, 0);
        gb.addColorStop(0, '#404040'); gb.addColorStop(0.1, '#c0c0c0'); gb.addColorStop(0.5, '#b0b0b0'); gb.addColorStop(0.55, '#606060'); gb.addColorStop(0.6, '#c0c0c0'); gb.addColorStop(1, '#b8b8b8');
        b.fillStyle = gb; b.fillRect(i * w, 0, w, N);
      }
      grain(x, N, r, 0.05);
      blotch(x, N, r, 10, [40, 160], 'rgba(90,70,40,0.12)');
    });
  }
  function lawnTex(dry) {
    const d = Math.round(dry * 10) / 10;
    return tex('lawn|' + d, 1.0, 512, (x, b, N, r) => {
      const G = mix([74, 108, 44], [150, 128, 72], d), G2 = mix([104, 138, 58], [186, 164, 102], d);
      x.fillStyle = css(G, 0.85); x.fillRect(0, 0, N, N);
      b.fillStyle = '#606060'; b.fillRect(0, 0, N, N);
      for (let i = 0; i < 9000; i++) {
        const px = r() * N, py = r() * N, a = r() * 6.28, L = 5 + r() * 9, c = mix(G, G2, r());
        x.strokeStyle = css(c, 0.7 + r() * 0.55); x.lineWidth = 1.6 + r() * 1.6; x.beginPath();
        x.moveTo(px, py); x.lineTo(px + Math.cos(a) * L, py + Math.sin(a) * L); x.stroke();
        b.strokeStyle = 'rgba(255,255,255,0.3)'; b.lineWidth = 1.5; b.beginPath(); b.moveTo(px, py); b.lineTo(px + Math.cos(a) * L, py + Math.sin(a) * L); b.stroke();
      }
      grain(x, N, r, 0.12, 0.05);
    });
  }
  function meshTex() {
    // 2" chain-link diamond, 11.5 gauge wire. The tile covers 0.2 m: four diamonds across.
    return tex('chainlink', 0.2, 256, (x, b, N, r) => {
      x.fillStyle = '#000'; x.fillRect(0, 0, N, N);
      b.fillStyle = '#000'; b.fillRect(0, 0, N, N);
      const d = N / 4;
      x.lineCap = 'round';
      for (let k = -N; k <= 2 * N; k += d) {
        for (const [ctx, col] of [[x, '#fff'], [b, '#fff']]) {
          ctx.strokeStyle = col; ctx.lineWidth = 4.2;
          ctx.beginPath(); ctx.moveTo(k, 0); ctx.lineTo(k + N, N); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(k, 0); ctx.lineTo(k - N, N); ctx.stroke();
        }
      }
    });
  }

  /* =======================================================================================
   * two_story_house
   * ===================================================================================== */
  K.define('two_story_house', {
    size: [19, 9.2, 11],
    options: { brick: null, siding: null, roof: null, trim: null, door: null, garage: 'right' },
    note: 'Options (null = seeded choice): brick (front brick colour), siding (side and back colour), roof, trim, door, garage right|left|none. The suburban two-storey of every Texas subdivision since 1990: brick front, lap siding on the sides and back, a gable roof with the ridge along the street, a gabled portico on columns over the door and a front-loading two-car garage wing.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const trimC = opt(o, 'trim', pick(r, TRIMS)), doorC = opt(o, 'door', pick(r, DOORS)), roofC = opt(o, 'roof', pick(r, ROOFS));
      const garage = opt(o, 'garage', 'right'), flip = garage === 'left' ? -1 : 1;
      const bT = brickTex(hex(opt(o, 'brick', pick(r, BRICKS))), pick(r, ['#bdb4a4', '#a9a293'])), bM = texMat(bT, 'b2|' + bT.map.uuid, { bumpScale: 2.2 });
      const sT = sidingTex(hex(opt(o, 'siding', pick(r, SIDINGS)))), sM = texMat(sT, 's2|' + sT.map.uuid, { bumpScale: 1.2 });
      const roofT = shingleTex(roofC), roofM = texMat(roofT, 'roof|' + roofC, { bumpScale: 2.4, roughness: 0.95 });
      const capM = texMat(roofT, 'cap|' + roofC, { bumpScale: 1.0, roughness: 0.95, color: 0xd8d8d8 });
      const concT = concreteTex('#b3ada2'), concM = texMat(concT, 'slab', { bumpScale: 0.6, roughness: 0.93 });
      const frameC = r() < 0.3 ? 0x3d3129 : trimC, grids = r() < 0.6 ? [2, 2] : null, trim = paint(trimC, 0.55);

      const W = 11.2 + r() * 1.8, D = 9.0, t = 0.26, ybase = 0.18, H1 = 2.95, H = H1 + 2.6;
      const Wg = garage === 'none' ? 0 : 6.6, Dg = 7.0, pf = garage === 'none' ? 0 : 0.8 + r() * 1.2;
      const tot = W + Wg, cx0 = -tot / 2 * flip + (flip > 0 ? W / 2 : -W / 2);  // main block centre x
      const mx = flip > 0 ? -tot / 2 + W / 2 : tot / 2 - W / 2;
      const xL = mx - W / 2, xR = mx + W / 2, zF = D / 2 - pf / 2, zB = zF - D;
      bx(B, concM, W + 0.04, ybase, D + 0.04, mx, 0, (zF + zB) / 2, { uv: concT.metres });

      // front (brick): door off centre, two windows below, three above
      const du = W * (flip > 0 ? 0.36 : 0.64);
      const sill = 0.9, wh = 1.52;
      const ops = [{ u: du, w: 1.0, y: 0, h: 2.1, door: true }];
      const lowWins = flip > 0 ? [W * 0.12, W * 0.66, W * 0.86] : [W * 0.14, W * 0.34, W * 0.88];
      lowWins.forEach((u, i) => ops.push({ u, w: i === 1 ? 1.9 : 0.92, cols: i === 1 ? 2 : 1, y: sill, h: wh }));
      [W * 0.12, W * 0.36, W * 0.64, W * 0.88].forEach((u, i) => ops.push({ u, w: 0.92, y: H1 + 0.75, h: 1.4 }));
      const MF = frameM(xL, ybase, zF, 0);
      wallRun(B, bM, bT.metres, MF, W, H, t, ops);
      ops.forEach((q) => { if (!q.door) windowUnit(B, MF, Object.assign({ frame: frameC, t, grids, interior: 'blinds' }, q), r); });
      doorUnit(B, MF, { u: du, y: 0.02, t, trim: trimC, color: doorC });
      lantern(B, MF, du + 0.75, 1.6);
      // soldier band between floors and the frieze under the eave
      bx(B, trim, W + 0.02, 0.2, 0.03, mx, ybase + H - 0.2, zF + 0.015);
      // sides and back (siding), with corner boards and a band at the floor line
      const sides = [[xL, -Math.PI / 2, zB, 'L'], [xR, Math.PI / 2, zF, 'R']];
      for (const [xs, ry, zs, k] of sides) {
        const M = new THREE.Matrix4().multiplyMatrices(frameM(xs, ybase, zs, ry), new THREE.Matrix4().makeTranslation(t, 0, 0));
        const onGarage = garage !== 'none' && ((k === 'R') === (flip > 0));
        const sops = onGarage ? [] : [{ u: D * 0.3, w: 0.92, y: sill, h: wh }, { u: D * 0.68, w: 0.92, y: H1 + 0.75, h: 1.4 }];
        wallRun(B, sM, sT.metres, M, D - 2 * t, H, t, sops.map((q) => Object.assign({}, q, { u: q.u - t })));
        sops.forEach((q) => windowUnit(B, M, Object.assign({ frame: frameC, t, grids, interior: 'blinds', sill: false, lintel: false }, q, { u: q.u - t }), r));
        const nx = Math.sign(xs - mx);
        bx(B, trim, 0.03, 0.2, D - 0.02, xs + nx * 0.015, ybase + H1 - 0.1, (zF + zB) / 2);
        for (const zc of [zF - 0.05, zB + 0.05]) bx(B, trim, 0.03, H, 0.1, xs + nx * 0.015, ybase, zc);
      }
      {
        const M = frameM(xR, ybase, zB, Math.PI);
        const bops = [{ u: W * 0.25, w: 0.92, y: sill, h: wh }, { u: W * 0.55, w: 2.4, y: 0.02, h: 2.03, fixed: true, cols: 2 },
                      { u: W * 0.8, w: 0.92, y: sill, h: wh }, { u: W * 0.25, w: 0.92, y: H1 + 0.75, h: 1.4 }, { u: W * 0.7, w: 0.92, y: H1 + 0.75, h: 1.4 }];
        wallRun(B, sM, sT.metres, M, W, H, t, bops);
        bops.forEach((q) => windowUnit(B, M, Object.assign({ frame: frameC, t, interior: 'blinds', sill: false, lintel: false }, q), r));
        bx(B, trim, W, 0.2, 0.03, mx, ybase + H1 - 0.1, zB - 0.015);
      }
      // main gable roof, ridge along the street
      const ov = 0.45, rake = 0.3, pitch = 0.55 + r() * 0.12, ye = ybase + H + 0.2, fh = 0.2;
      const res = gableRoof(B, { x0: xL - rake, x1: xR + rake, z0: zB - ov, z1: zF + ov, ye, pitch, axis: 'x', roofMat: roofM, capMat: capM,
        uvm: roofT.metres, trim: trimC, gutters: { front: [0.5, W - 0.2], back: [0.5, W - 0.2] }, wallOff: ov });
      const shoulder = 0.2 + ov * pitch - 0.02;
      for (const [xs, ry] of [[xL, -Math.PI / 2], [xR, Math.PI / 2]]) {
        gableWall(B, sM, sT.metres, frameM(xs, ybase + H, (zF + zB) / 2, ry), D, 0, res.yr - (ybase + H), t, true, trimC, shoulder);
      }
      // the portico: two columns, a gabled roof and a slab with a step
      {
        const pw = 2.6, pd = 1.6, px = xL + du, top = ybase + 2.75;
        bx(B, concM, pw + 0.4, 0.12, pd + 0.2, px, ybase - 0.05, zF + pd / 2 - 0.05, { uv: concT.metres });
        bx(B, concM, pw * 0.7, 0.12, 0.35, px, 0, zF + pd + 0.2, { uv: concT.metres });
        const colM = paint(trimC, 0.5);
        for (const s of [-1, 1]) {
          const cg = new THREE.LatheGeometry([[0.001, 0], [0.15, 0], [0.15, 0.08], [0.12, 0.1], [0.11, 0.2], [0.095, top - ybase - 0.3], [0.13, top - ybase - 0.2], [0.14, top - ybase - 0.08], [0.15, top - ybase - 0.08], [0.15, top - ybase], [0.001, top - ybase]].map(p => new THREE.Vector2(p[0], p[1])), 20);
          cg.translate(px + s * (pw / 2 - 0.2), ybase + 0.07, zF + pd - 0.2); B.add(colM, cg);
        }
        bx(B, colM, pw, 0.26, 0.2, px, top - 0.2, zF + pd - 0.2);
        bx(B, colM, 0.2, 0.26, pd, px - pw / 2 + 0.1, top - 0.2, zF + pd / 2 - 0.1);
        bx(B, colM, 0.2, 0.26, pd, px + pw / 2 - 0.1, top - 0.2, zF + pd / 2 - 0.1);
        const pp = 0.7;
        const rr = gableRoof(B, { x0: px - pw / 2 - 0.25, x1: px + pw / 2 + 0.25, z0: zF - 0.1, z1: zF + pd + 0.15, ye: top + 0.26, pitch: pp, axis: 'z',
          roofMat: roofM, capMat: capM, uvm: roofT.metres, trim: trimC, ends: ['+'], gutters: {}, fh: 0.18 });
        gableWall(B, trim, 1, frameM(px, top + 0.08, zF + pd - 0.12, 0), pw + 0.2, 0, rr.yr - top - 0.1, 0.05, false, trimC, 0.18);
      }
      // the garage wing, one storey, hip roof, doors to the street
      if (garage !== 'none') {
        const gx0 = flip > 0 ? xR : xL - Wg, gzF = zF + pf, gzB = gzF - Dg, Hg = 2.75;
        bx(B, concM, Wg, ybase, Dg, gx0 + Wg / 2, 0, gzF - Dg / 2, { uv: concT.metres });
        const M = frameM(gx0, ybase, gzF, 0), gw = 4.88, gh = 2.13;
        wallRun(B, bM, bT.metres, M, Wg, Hg, t, [{ u: Wg / 2, w: gw, y: 0, h: gh }]);
        garageDoor(B, M, { u: Wg / 2, y: 0, w: gw, h: gh, t, color: trimC, trim: trimC, windows: r() < 0.5 }, r);
        lantern(B, M, Wg / 2 - gw / 2 - 0.45, 1.5); lantern(B, M, Wg / 2 + gw / 2 + 0.45, 1.5);
        // outer side wall and the short return where the wing stands proud of the house
        const xo = flip > 0 ? gx0 + Wg : gx0;
        const Ms = new THREE.Matrix4().multiplyMatrices(frameM(xo, ybase, flip > 0 ? gzF : gzB, flip > 0 ? Math.PI / 2 : -Math.PI / 2), new THREE.Matrix4().makeTranslation(t, 0, 0));
        wallRun(B, sM, sT.metres, Ms, Dg - 2 * t, Hg, t, [{ u: Dg * 0.5, w: 0.92, y: 0.9, h: 1.2 }]);
        windowUnit(B, Ms, { u: Dg * 0.5, w: 0.92, y: 0.9, h: 1.2, frame: frameC, t, interior: 'room', sill: false, lintel: false }, r);
        const Mb = frameM(flip > 0 ? gx0 + Wg : gx0 + Wg, ybase, gzB, Math.PI);
        wallRun(B, sM, sT.metres, Mb, Wg, Hg, t, []);
        if (pf > 0.05) {
          const xi = flip > 0 ? gx0 : gx0 + Wg;
          const g2 = new THREE.BoxGeometry(t, Hg, pf); g2.translate(xi + flip * t / 2, ybase + Hg / 2, gzF - pf / 2); K.uvBox(g2, bT.metres); B.add(bM, g2);
        }
        hipRoof(B, { x0: gx0 - 0.45, x1: gx0 + Wg + 0.45, z0: gzB - 0.45, z1: gzF + 0.45, ye: ybase + Hg + 0.2, pitch: 0.5, roofMat: roofM, capMat: capM,
          uvm: roofT.metres, trim: trimC, gutters: { front: [0.6, Wg + 0.3] }, wallOff: 0.45 });
      }
      B.flush(g);
      return g;
    },
  });

  /* =======================================================================================
   * mobile_home: a 16 x 72 ft single-wide on a skirt, with its wooden steps
   * ===================================================================================== */
  K.define('mobile_home', {
    size: [22.4, 3.9, 6.6],
    options: { style: null, color: null, trim: null },
    note: 'Options (null = seeded choice): style modern|vintage, color (siding), trim (the vintage accent band). A single-wide manufactured home: vinyl skirting over the piers, lap siding, a shallow shingled (modern) or white metal (vintage) roof, aluminium windows, a front door with a treated-pine landing and steps, the hitch tongue at one end, a condenser at the back.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const style = opt(o, 'style', r() < 0.5 ? 'modern' : 'vintage');
      const sc = hex(opt(o, 'color', style === 'vintage' ? pick(r, ['#e8e4d8', '#d9d5c3', '#e4ddc6']) : pick(r, SIDINGS)));
      const trimC = opt(o, 'trim', style === 'vintage' ? pick(r, [0x6d4a36, 0x3b5566, 0x5b6b4a]) : 0xf0eee6);
      const L = 21.9, Wd = 4.88, t = 0.12, yf = 0.8, H = 2.3;
      const sT = sidingTex(sc), sM = texMat(sT, 'mh|' + sT.map.uuid, { bumpScale: style === 'vintage' ? 0.8 : 1.2, metalness: style === 'vintage' ? 0.2 : 0, roughness: 0.6 });
      const kT = skirtTex(style === 'vintage' ? '#cfc8b6' : '#bdb6a4'), kM = texMat(kT, 'skirt|' + kT.map.uuid, { bumpScale: 1.0 });
      const frameC = 0xc9ccce, zF = Wd / 2, zB = -Wd / 2, xL = -L / 2, xR = L / 2;
      // skirting, set in 5 cm, with a crawlspace vent every few metres
      for (const [x, z, w, d] of [[0, zF - 0.05, L - 0.1, 0.02], [0, zB + 0.05, L - 0.1, 0.02], [xL + 0.05, 0, 0.02, Wd - 0.1], [xR - 0.05, 0, 0.02, Wd - 0.1]])
        bx(B, kM, w, yf, d, x, 0, z, { uv: kT.metres });
      for (let i = 0; i < 4; i++) bx(B, paint(0x3a3a38, 0.7), 0.4, 0.2, 0.02, xL + L * (0.15 + i * 0.24), 0.3, zF - 0.035);
      // floor frame band and the walls
      bx(B, paint(0x8a857a, 0.7), L, 0.12, Wd, 0, yf - 0.1, 0);
      const doorU = L * 0.38, sill = 0.85;
      const fOps = [{ u: doorU, w: 0.95, y: 0, h: 1.98, door: true }];
      [0.08, 0.2, 0.52, 0.64, 0.8, 0.92].forEach((k) => fOps.push({ u: L * k, w: 0.92, y: sill, h: 1.1 }));
      const MF = frameM(xL, yf, zF, 0);
      wallRun(B, sM, sT.metres, MF, L, H, t, fOps);
      fOps.forEach((q) => { if (!q.door) windowUnit(B, MF, Object.assign({ frame: frameC, t, recess: 0.0, interior: 'blinds', sill: false, lintel: false,
        shutters: style === 'vintage' ? null : null }, q), r); });
      doorUnit(B, MF, { u: doorU, y: 0.02, h: 1.93, w: 0.86, t, trim: 0xe8e8e2, color: style === 'vintage' ? 0xe8e4d8 : pick(r, DOORS) });
      lantern(B, MF, doorU + 0.65, 1.5);
      const MB = frameM(xR, yf, zB, Math.PI);
      const bOps = [0.1, 0.3, 0.5, 0.75].map((k) => ({ u: L * k, w: 0.92, y: sill, h: 1.1 }));
      wallRun(B, sM, sT.metres, MB, L, H, t, bOps);
      bOps.forEach((q) => windowUnit(B, MB, Object.assign({ frame: frameC, t, recess: 0.0, interior: 'curtain', sill: false, lintel: false }, q), r));
      for (const [xs, ry, zs] of [[xL, -Math.PI / 2, zB], [xR, Math.PI / 2, zF]]) {
        const M = new THREE.Matrix4().multiplyMatrices(frameM(xs, yf, zs, ry), new THREE.Matrix4().makeTranslation(t, 0, 0));
        const eo = [{ u: Wd / 2 - t, w: 0.92, y: sill, h: 1.1 }];
        wallRun(B, sM, sT.metres, M, Wd - 2 * t, H, t, eo);
        eo.forEach((q) => windowUnit(B, M, Object.assign({ frame: frameC, t, recess: 0, interior: 'blinds', sill: false, lintel: false }, q), r));
      }
      // vintage: a painted accent band along the top of the wall
      if (style === 'vintage') {
        bx(B, paint(trimC, 0.5), L + 0.02, 0.22, 0.012, 0, yf + H - 0.34, zF + 0.006);
        bx(B, paint(trimC, 0.5), L + 0.02, 0.22, 0.012, 0, yf + H - 0.34, zB - 0.006);
      }
      // roof: a shallow gable along the length, small eaves
      const ye = yf + H + 0.12, pitch = style === 'vintage' ? 0.14 : 0.25;
      const roofT = style === 'vintage' ? null : shingleTex(pick(r, ROOFS));
      const roofM = style === 'vintage' ? std('mhroof', { color: 0xdcdcd6, metalness: 0.3, roughness: 0.55, map: K.tex('corrugated', { color: '#d8d8d2' }) })
        : texMat(roofT, 'roof|' + roofT.map.uuid, { bumpScale: 2.4, roughness: 0.95 });
      const res = gableRoof(B, { x0: xL - 0.12, x1: xR + 0.12, z0: zB - 0.2, z1: zF + 0.2, ye, pitch, axis: 'x', roofMat: roofM,
        uvm: style === 'vintage' ? 1.0 : roofT.metres, trim: style === 'vintage' ? 0xe0ded6 : 0xf0eee6, fh: 0.12, rake: 0.12,
        gutters: style === 'vintage' ? {} : { front: [0.5, L - 0.3] }, wallOff: 0.2 });
      for (const [xs, ry] of [[xL, -Math.PI / 2], [xR, Math.PI / 2]])
        gableWall(B, sM, sT.metres, frameM(xs, yf + H, 0, ry), Wd, 0, res.yr - yf - H, t, false, trimC, 0.12 + 0.2 * pitch - 0.01);
      // treated pine landing, steps and rail at the door
      const wood = texMat(cedarTex('#a88c62'), 'pine', { bumpScale: 0.4 }), cedarM = wood;
      const lx = xL + doorU, lz = zF + 0.75, lw = 1.8, ld = 1.4, ly = yf - 0.05;
      for (let i = 0; i < 9; i++) bx(B, cedarM, lw, 0.035, 0.14, lx, ly - 0.035, zF + 0.1 + i * 0.155, { uv: 1.2 });
      for (const [dx, dz] of [[-1, 0], [1, 0], [-1, 1], [1, 1]]) bx(B, cedarM, 0.09, ly + 0.95, 0.09, lx + dx * (lw / 2 - 0.05), 0, zF + 0.1 + dz * (ld - 0.1), { uv: 1.2 });
      for (const s of [-1, 1]) {
        bx(B, cedarM, 0.04, 0.09, ld, lx + s * (lw / 2 - 0.02), ly + 0.85, zF + 0.1 + ld / 2 - 0.05, { uv: 1.2 });
        for (let i = 0; i < 9; i++) bx(B, cedarM, 0.035, 0.85, 0.035, lx + s * (lw / 2 - 0.02), ly, zF + 0.15 + i * 0.15, { uv: 1.2 });
      }
      // steps down to grade on the open side
      const nSteps = Math.round(ly / 0.19), sw = 1.0;
      for (let i = 0; i < nSteps; i++) {
        const sy = ly - (i + 1) * (ly / nSteps);
        bx(B, cedarM, sw, 0.035, 0.28, lx + 0.3, sy, zF + ld + 0.15 + i * 0.26, { uv: 1.2 });
      }
      for (const s of [-1, 1]) beam(B, cedarM, [lx + 0.3 + s * (sw / 2 - 0.02), ly, zF + ld + 0.05], [lx + 0.3 + s * (sw / 2 - 0.02), 0.02, zF + ld + 0.15 + nSteps * 0.26], 0.04, 0.24);
      // the hitch tongue sticking out at one end, and a jack stand
      const st = metal(0x2a2a2a, 0.6);
      beam(B, st, [xR, 0.42, 1.0], [xR + 1.3, 0.42, 0.0], 0.1, 0.12);
      beam(B, st, [xR, 0.42, -1.0], [xR + 1.3, 0.42, 0.0], 0.1, 0.12);
      bx(B, st, 0.16, 0.08, 0.16, xR + 1.35, 0.38, 0);
      cy(B, st, 0.03, 0.03, 0.42, xR + 1.15, 0, 0, 10);
      bx(B, st, 0.2, 0.02, 0.2, xR + 1.15, 0, 0);
      // condenser at the back
      bx(B, paint(0x8d8f8a, 0.5), 0.72, 0.75, 0.72, xL + L * 0.3, 0.08, zB - 0.7, { r: 0.03 });
      bx(B, paint(0x2b2b2b, 0.7), 0.74, 0.02, 0.74, xL + L * 0.3, 0.83, zB - 0.7);
      bx(B, texMat(concreteTex('#b3ada2'), 'slab', { bumpScale: 0.6, roughness: 0.93 }), 0.9, 0.08, 0.9, xL + L * 0.3, 0, zB - 0.7, { uv: 3 });
      B.flush(g);
      return g;
    },
  });

  /* =======================================================================================
   * fences
   * ===================================================================================== */
  const cedarColour = (w, r) => {
    const fresh = [1.0, 0.86, 0.72], grey = [0.66, 0.64, 0.6];
    const k = Math.min(1, Math.max(0, w + (r() - 0.5) * 0.35));
    const c = mix(fresh, grey, k), j = 0.86 + r() * 0.22;
    return [c[0] * j, c[1] * j, c[2] * j];
  };
  K.define('privacy_fence', {
    size: [12, 1.9, 0.3],
    options: { length: 12, height: 1.83, gate: false, weathered: null },
    note: 'Options: length m, height m (1.83 is a 6 ft fence), gate (a 4 ft gate at the middle), weathered 0..1 fresh cedar to silver (null = seeded). A Texas cedar privacy fence: dog-eared pickets on three 2x4 rails and cedar posts at 8 ft, a kickboard, each picket weathered a little differently; the picket side faces +z. Runs along x.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const L = opt(o, 'length', 12), H = opt(o, 'height', 1.83), wz = opt(o, 'weathered', 0.25 + r() * 0.5), gate = opt(o, 'gate', false);
      const T = cedarTex('#b58a64'), cm = texMat(T, 'fence-cedar', { vertexColors: true, bumpScale: 0.8, roughness: 0.92 });
      const pw = 0.14, gap = 0.004, pt = 0.016, y0 = 0.06;
      const shape = new THREE.Shape([[-pw / 2, 0], [pw / 2, 0], [pw / 2, H - y0 - 0.025], [pw / 2 - 0.025, H - y0], [-pw / 2 + 0.025, H - y0], [-pw / 2, H - y0 - 0.025]].map(p => new THREE.Vector2(p[0], p[1])));
      const pk = new THREE.ExtrudeGeometry(shape, { depth: pt, bevelEnabled: false });
      const gw = 1.22, gx0 = -gw / 2, gx1 = gw / 2;
      const inGate = (x) => gate && x > gx0 - 0.05 && x < gx1 + 0.05;
      // pickets: a gate's pickets are in the gate
      for (let x = -L / 2 + pw / 2; x <= L / 2 - pw / 2 + 1e-6; x += pw + gap) {
        const p = pk.clone(); const lean = (r() - 0.5) * 0.006;
        bake(p, x, y0 + (r() - 0.5) * 0.01, 0.04, (r() - 0.5) * 0.01, 0, lean);
        K.uvBox(p, T.metres); tint(p, cedarColour(wz, r));
        if (inGate(x)) { /* swings with the gate, same place, closed */ }
        B.add(cm, p);
      }
      // kickboard and cap along the picket face
      const kick = [], k1 = cedarColour(wz + 0.1, r);
      bx(B, cm, L, 0.14, 0.025, 0, 0.0, 0.065, { uv: T.metres, color: k1 });
      bx(B, cm, L + 0.02, 0.035, 0.14, 0, H + 0.005, 0.0, { uv: T.metres, color: cedarColour(wz + 0.15, r) });
      bx(B, cm, L, 0.09, 0.02, 0, H - 0.1, 0.066, { uv: T.metres, color: cedarColour(wz, r) });
      // rails behind, posts every 8 ft
      const nP = Math.max(1, Math.round(L / 2.44));
      const posts = [];
      for (let i = 0; i <= nP; i++) posts.push(-L / 2 + i * L / nP);
      if (gate) posts.push(gx0 - 0.05, gx1 + 0.05);
      for (const px of posts) bx(B, cm, 0.089, H - 0.05, 0.089, px, 0, -0.02, { uv: T.metres, color: cedarColour(wz + 0.2, r) });
      for (const ry of [0.25, H * 0.52, H - 0.3]) {
        const segs = gate ? [[-L / 2, gx0 - 0.1], [gx0 + 0.02, gx1 - 0.02], [gx1 + 0.1, L / 2]] : [[-L / 2, L / 2]];
        for (const [a, b] of segs) bx(B, cm, b - a, 0.089, 0.038, (a + b) / 2, ry, 0.012, { uv: T.metres, color: cedarColour(wz, r) });
      }
      if (gate) {
        // Z-brace on the back, black strap hinges and a latch on the face
        beam(B, cm, [gx0 + 0.1, 0.3, -0.005], [gx1 - 0.1, H - 0.35, -0.005], 0.089, 0.038);
        const blk = paint(0x1a1a1a, 0.6);
        for (const hy of [0.35, H - 0.35]) { bx(B, blk, 0.3, 0.04, 0.006, gx0 + 0.13, hy, 0.059); cy(B, blk, 0.012, 0.012, 0.06, gx0 - 0.02, hy - 0.01, 0.06, 8); }
        bx(B, blk, 0.12, 0.05, 0.02, gx1 - 0.1, 1.05, 0.066);
        cy(B, blk, 0.008, 0.008, 0.2, gx1 - 0.1, 0.95, 0.08, 6);
        bx(B, paint(0x1c1a17, 1), 0.012, H - 0.1, 0.03, gx1, y0, 0.05);   // the gate's gap, in shadow
      }
      B.flush(g);
      return g;
    },
  });

  K.define('chain_link_fence', {
    size: [12, 1.3, 0.12],
    options: { length: 12, height: 1.22, color: 'galvanized' },
    note: 'Options: length m, height m (1.22 is a 4 ft fence), color galvanized|black. Residential chain link: galvanized line posts every 3 m with dome caps, heavier terminal posts with tension bands, a top rail through loop caps, 2 in diamond mesh (a real alpha-cut wire pattern that casts a patterned shadow) and a bottom tension wire. Runs along x.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const L = opt(o, 'length', 12), H = opt(o, 'height', 1.22), black = opt(o, 'color', 'galvanized') === 'black';
      const pm = black ? paint(0x1d1f1f, 0.5) : K.finish.galvanized();
      const nP = Math.max(1, Math.round(L / 3));
      for (let i = 0; i <= nP; i++) {
        const x = -L / 2 + i * L / nP, term = i === 0 || i === nP, rr = term ? 0.036 : 0.024;
        cy(B, pm, rr, rr, H + (term ? 0.05 : 0), x, 0, 0, 14);
        if (term) {
          const cap = new THREE.SphereGeometry(rr + 0.004, 14, 6, 0, Math.PI * 2, 0, Math.PI / 2); cap.translate(x, H + 0.05, 0); B.add(pm, cap);
          for (let k = 0; k < 4; k++) bx(B, pm, rr * 2 + 0.012, 0.02, rr * 2 + 0.012, x, 0.15 + k * (H - 0.2) / 3, 0);
          bx(B, pm, 0.012, H - 0.1, 0.018, x + (i === 0 ? 1 : -1) * (rr + 0.01), 0.07, 0.02);   // tension bar
        } else {
          bx(B, pm, 0.07, 0.05, 0.07, x, H - 0.02, 0.0, { r: 0.012 });                       // loop cap
        }
        cy(B, K.finish.concrete(), 0.12, 0.13, 0.03, x, -0.01, 0, 16);                           // footing collar
      }
      // top rail and bottom wire
      const rail = new THREE.CylinderGeometry(0.0206, 0.0206, L, 12); rail.rotateZ(Math.PI / 2); rail.translate(0, H - 0.01, 0.035);
      B.add(pm, rail);
      const wire = new THREE.CylinderGeometry(0.003, 0.003, L, 5); wire.rotateZ(Math.PI / 2); wire.translate(0, 0.06, 0.035); B.add(pm, wire);
      // the fabric: a double-sided plane with the diamond cut from it
      const T = meshTex();
      const fm = mat('chainfab|' + black, () => {
        const m = new THREE.MeshStandardMaterial({ color: black ? 0x222424 : 0xb9bec0, metalness: black ? 0.1 : 0.75, roughness: 0.42,
          alphaMap: T.map, alphaTest: 0.35, side: THREE.DoubleSide, bumpMap: T.bump, bumpScale: 0.6 });
        return m;
      });
      const fab = new THREE.PlaneGeometry(L - 0.06, H - 0.1);
      const uv = fab.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (L - 0.06) / T.metres, uv.getY(i) * (H - 0.1) / T.metres);
      fab.translate(0, 0.07 + (H - 0.1) / 2, 0.034);
      B.add(fm, fab);
      B.flush(g);
      // shadows: the depth pass keeps the diamond holes
      g.traverse((m) => { if (m.isMesh && m.material === fm) m.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, alphaMap: T.map, alphaTest: 0.35 }); });
      return g;
    },
  });

  K.define('barbed_wire_fence', {
    size: [20, 1.5, 0.6],
    options: { length: 20, strands: 4, spacing: 3.6 },
    note: 'Options: length m, strands, spacing (T-post spacing, m). A ranch pasture fence: green studded steel T-posts with white-painted tops, a cedar H-brace at each end, four strands of galvanized two-point barbed wire that sag between posts, with wire clips on every post. Runs along x.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const L = opt(o, 'length', 20), n = opt(o, 'strands', 4), sp = opt(o, 'spacing', 3.6);
      const green = paint(0x2f5a3a, 0.5), white = paint(0xe8e6de, 0.5), wireM = std('bwire', { color: 0x8c8a84, metalness: 0.7, roughness: 0.55 });
      const bark = K.tex('bark', { color: '#6b5a48' });
      const cedar = mat('bw-cedar', () => new THREE.MeshStandardMaterial({ color: 0xffffff, map: bark, roughness: 0.95 }));
      const hs = [];
      for (let i = 0; i < n; i++) hs.push(0.38 + i * (1.2 - 0.38) / Math.max(1, n - 1));
      const ends = [-L / 2, L / 2], nSp = Math.max(1, Math.round((L - 5) / sp));
      const tposts = [];
      for (let i = 0; i <= nSp; i++) tposts.push(-L / 2 + 2.5 + i * (L - 5) / nSp);
      // T-posts: a flange and a web, studs, a white top, lean a little
      for (const x of tposts) {
        const lean = (r() - 0.5) * 0.05, ry = (r() - 0.5) * 0.3, M = new THREE.Matrix4().compose(new V3(x, 0, 0), new THREE.Quaternion().setFromEuler(new THREE.Euler(lean, ry, lean * 0.5)), S1);
        const hh = 1.4;
        bx(B, green, 0.035, hh - 0.12, 0.005, 0, 0, 0.012, { M });
        bx(B, green, 0.005, hh - 0.12, 0.028, 0, 0, 0.0, { M });
        bx(B, white, 0.035, 0.12, 0.005, 0, hh - 0.12, 0.012, { M });
        bx(B, white, 0.005, 0.12, 0.028, 0, hh - 0.12, 0.0, { M });
        for (let k = 0; k < 14; k++) bx(B, green, 0.012, 0.012, 0.006, 0, 0.1 + k * 0.08, 0.017, { M });
        bx(B, green, 0.16, 0.08, 0.006, 0, 0.0, 0.0, { M });       // the anchor plate at grade
        hs.forEach((h) => bx(B, wireM, 0.045, 0.012, 0.012, 0, h - 0.006, 0.02, { M }));   // wire clips
      }
      // cedar end posts with an H-brace
      const crooked = (x0, h, rad) => {
        const pts = []; for (let i = 0; i <= 6; i++) pts.push([x0 + (r() - 0.5) * 0.04, i * h / 6, (r() - 0.5) * 0.04]);
        const m = TXT.tube(pts, rad, null, { segments: 12, radial: 10 }); K.uvBox(m.geometry, 0.6); B.add(cedar, m.geometry);
      };
      for (const e of ends) {
        const s = Math.sign(e), x1 = e - s * 2.3;
        crooked(e, 1.55, 0.085); crooked(x1, 1.45, 0.07);
        const br = TXT.tube([[e - s * 0.05, 1.1, 0], [x1 + s * 0.05, 1.1, 0]], 0.05, null, { segments: 4, radial: 8 }); K.uvBox(br.geometry, 0.6); B.add(cedar, br.geometry);
        B.add(wireM, TXT.tube([[e - s * 0.08, 1.12, 0.06], [x1 + s * 0.08, 0.1, 0.06]], 0.004, null, { segments: 4, radial: 5 }).geometry);
        B.add(wireM, TXT.tube([[e - s * 0.08, 1.05, -0.06], [x1 + s * 0.08, 0.15, -0.06]], 0.004, null, { segments: 4, radial: 5 }).geometry);
      }
      // strands: sag between supports; barbs every 12.7 cm
      const sup = [ends[0], ...tposts, ends[1]].sort((a, b) => a - b);
      const barbs = [];
      hs.forEach((h, si) => {
        for (let i = 0; i < sup.length - 1; i++) {
          const a = sup[i], b = sup[i + 1], span = b - a, sag = 0.012 * span + r() * 0.02, pts = [];
          for (let k = 0; k <= 10; k++) { const tt = k / 10; pts.push([a + span * tt, h - sag * 4 * tt * (1 - tt), 0.03]); }
          B.add(wireM, TXT.tube(pts, 0.0022, null, { segments: 20, radial: 4 }).geometry);
          for (let x = a + 0.06; x < b - 0.03; x += 0.127) { const tt = (x - a) / span; barbs.push([x, h - sag * 4 * tt * (1 - tt), 0.03, r() * Math.PI]); }
        }
      });
      B.flush(g);
      // barbs: two short crossed wires, instanced, turned about the strand
      const bg = K.merge([new THREE.Mesh(new THREE.BoxGeometry(0.004, 0.028, 0.003)), (() => { const m = new THREE.Mesh(new THREE.BoxGeometry(0.004, 0.003, 0.028)); return m; })()], wireM).geometry;
      const im = new THREE.InstancedMesh(bg, wireM, barbs.length), Mx = new THREE.Matrix4();
      barbs.forEach((b, i) => { Mx.makeRotationX(b[3]); Mx.setPosition(b[0], b[1], b[2]); im.setMatrixAt(i, Mx); });
      im.instanceMatrix.needsUpdate = true; g.add(im);
      return g;
    },
  });

  /* =======================================================================================
   * mailbox
   * ===================================================================================== */
  K.define('mailbox', {
    size: [0.7, 1.5, 0.7],
    options: { style: null, color: null, brick: null },
    note: 'Options (null = seeded choice): style post|brick, color (box colour), brick (column colour). A curbside mailbox: a T1 arch-top steel box with a red flag on a 4x4 cedar post and arm, or the suburban Texas brick column with a cast-stone cap and a mail door. The door faces +z (the street).',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const style = opt(o, 'style', r() < 0.5 ? 'post' : 'brick'), bc = opt(o, 'color', pick(r, [0x1b1b1b, 0x1b1b1b, 0x8d8f8e, 0x1f3325]));
      const boxM = std('mbox|' + bc, { color: bc, metalness: 0.5, roughness: 0.45 });
      const flag = paint(0xc0241c, 0.45);
      const T1 = (x, y, z, parent) => {
        const w = 0.165, h = 0.2, L = 0.48, rr = w / 2, hb = h - rr;
        bx(B, boxM, w, hb, L, x, y, z);
        const top = new THREE.CylinderGeometry(rr, rr, L, 20, 1, false, 0, Math.PI); top.rotateX(Math.PI / 2); top.rotateZ(Math.PI / 2 * 0);
        top.rotateZ(Math.PI / 2); top.translate(x, y + hb, z); B.add(boxM, top);
        // the door, slightly proud, with a pull
        const door = new THREE.Shape(); door.moveTo(-w / 2 - 0.004, 0); door.lineTo(w / 2 + 0.004, 0); door.lineTo(w / 2 + 0.004, hb);
        door.absarc(0, hb, rr + 0.004, 0, Math.PI, false); door.lineTo(-w / 2 - 0.004, 0);
        const dg = new THREE.ExtrudeGeometry(door, { depth: 0.012, bevelEnabled: false, curveSegments: 10 }); dg.translate(x, y, z + L / 2); B.add(boxM, dg);
        bx(B, K.finish.chrome(), 0.04, 0.012, 0.02, x, y + h - 0.03, z + L / 2 + 0.018);
        // flag on the right side, raised
        bx(B, flag, 0.006, 0.2, 0.025, x + w / 2 + 0.006, y + 0.05, z - 0.08);
        bx(B, flag, 0.006, 0.07, 0.1, x + w / 2 + 0.006, y + 0.2, z - 0.12);
        cy(B, boxM, 0.012, 0.012, 0.012, x + w / 2 + 0.003, y + 0.06, z - 0.08, 10, { rz: Math.PI / 2 });
      };
      if (style === 'post') {
        const wood = texMat(cedarTex('#8a6a4a'), 'mbpost', { bumpScale: 0.5 });
        bx(B, wood, 0.089, 1.05, 0.089, 0, 0, -0.2, { uv: 1.2 });
        bx(B, wood, 0.089, 0.089, 0.6, 0, 0.93, 0.0, { uv: 1.2 });
        beam(B, wood, [0, 0.62, -0.16], [0, 0.93, 0.12], 0.06, 0.04, { uv: 1.2 });
        bx(B, wood, 0.25, 0.02, 0.5, 0, 1.02, 0.03, { uv: 1.2 });
        T1(0, 1.04, 0.03);
      } else {
        const bT = brickTex(hex(opt(o, 'brick', pick(r, BRICKS))), '#b9b0a2'), bm = texMat(bT, 'mbrick|' + bT.map.uuid, { bumpScale: 2.2 });
        const cw = 0.61, chh = 1.32;
        const M = frameM(-cw / 2, 0, cw / 2, 0);
        wallRun(B, bm, bT.metres, M, cw, chh, cw, [{ u: cw / 2, w: 0.3, y: 0.82, h: 0.24 }]);
        const cast = texMat(limestoneTex('#d6cdb8'), 'caststone', { bumpScale: 0.6 });
        bx(B, cast, cw + 0.1, 0.07, cw + 0.1, 0, chh, 0, { uv: 1.6, r: 0.01 });
        bx(B, cast, cw - 0.06, 0.06, cw - 0.06, 0, chh + 0.07, 0, { uv: 1.6, r: 0.01 });
        bx(B, cast, cw + 0.06, 0.07, cw + 0.06, 0, 0, 0, { uv: 1.6 });
        const dm = paint(0x1a1a1a, 0.45);
        bx(B, dm, 0.31, 0.25, 0.012, 0, 0.815, cw / 2 - 0.02);
        bx(B, dm, 0.3, 0.02, 0.02, 0, 0.815 + 0.225, cw / 2 - 0.005);
        bx(B, K.finish.chrome(), 0.05, 0.015, 0.02, 0, 0.815 + 0.19, cw / 2 - 0.0);
        bx(B, paint(0x121212, 0.9), 0.3, 0.24, 0.3, 0, 0.82, cw / 2 - 0.16);
        // the address tile (blank: numerals on a model would be typed ones)
        bx(B, paint(0xe5ddcc, 0.4), 0.3, 0.14, 0.015, 0, 0.45, cw / 2 + 0.006, { r: 0.004 });
      }
      B.flush(g);
      return g;
    },
  });

  /* =======================================================================================
   * driveway: a broom-finished slab with sawn joints, a curb apron, a little oil
   * ===================================================================================== */
  K.define('driveway', {
    size: [5.5, 0.08, 9],
    options: { width: 5.5, length: 9, flare: true, age: null },
    note: 'Options: width m, length m (runs along z, the street end at +z), flare (the curb apron) bool, age 0..1 new to stained (null = seeded). A residential concrete driveway: 4 in slab in sawn panels about 3 m square, a centre joint, a flared apron at the street, broom finish, tyre darkening and an oil stain near the garage.',
    make(o, r) {
      const g = new THREE.Group(), B = Bucket();
      const W = opt(o, 'width', 5.5), L = opt(o, 'length', 9), flare = opt(o, 'flare', true), age = opt(o, 'age', 0.3 + r() * 0.5);
      const cT = concreteTex(age > 0.5 ? '#aaa49a' : '#bcb7ad'), cm = texMat(cT, 'drive|' + cT.map.uuid, { bumpScale: 0.8, roughness: 0.92, vertexColors: true });
      const th = 0.06, jt = 0.012;
      const nx = Math.max(1, Math.round(W / 3)), nz = Math.max(1, Math.round(L / 3));
      for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) {
        const pw = W / nx - jt, pd = L / nz - jt, x = -W / 2 + (i + 0.5) * W / nx, z = -L / 2 + (j + 0.5) * L / nz;
        const k = 0.92 + r() * 0.12;
        bx(B, cm, pw, th, pd, x, 0, z, { uv: cT.metres, r: 0.006, color: [k, k, k * 0.99] });
      }
      bx(B, paint(0x2a2826, 1), W - 0.02, th - 0.01, L - 0.02, 0, 0, 0);    // the joints, dark
      if (flare) {
        for (const s of [-1, 1]) {
          const y = th - 0.004, a = [s * W / 2, y, L / 2], b = [s * (W / 2 + 1.0), y, L / 2], c = [s * W / 2, y, L / 2 - 1.1];
          poly(B, cm, [a, b, c], new V3(1, 0, 0), new V3(0, 0, -1), [0, 0, 0], cT.metres, s < 0);
          poly(B, cm, [b, [b[0], 0, b[2]], [c[0], 0, c[2]], c], new V3(0, 0, 1), new V3(0, 1, 0), [0, 0, 0], cT.metres, s > 0);
        }
      }
      B.flush(g);
      // stains: tyre tracks and an oil spot, a transparent decal just above the slab
      const c = canvas(256), x = c.getContext('2d');
      x.clearRect(0, 0, 256, 256);
      for (const tx of [0.3, 0.7]) {
        const gr = x.createLinearGradient(256 * (tx - 0.1), 0, 256 * (tx + 0.1), 0);
        gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(0.5, 'rgba(20,18,15,' + (0.14 * age + 0.03) + ')'); gr.addColorStop(1, 'rgba(0,0,0,0)');
        x.fillStyle = gr; x.fillRect(0, 0, 256, 256);
      }
      const og = x.createRadialGradient(128 + (r() - 0.5) * 60, 60, 2, 128, 60, 40);
      og.addColorStop(0, 'rgba(10,8,6,' + (0.5 * age) + ')'); og.addColorStop(1, 'rgba(10,8,6,0)');
      x.fillStyle = og; x.beginPath(); x.ellipse(128, 60, 44, 30, 0, 0, 6.3); x.fill();
      const dt = new THREE.CanvasTexture(c); dt.colorSpace = THREE.SRGBColorSpace;
      const dm = new THREE.Mesh(new THREE.PlaneGeometry(W * 0.9, L * 0.95), new THREE.MeshStandardMaterial({ map: dt, transparent: true, depthWrite: false, roughness: 0.6,
        polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 }));
      dm.rotation.x = -Math.PI / 2; dm.position.y = th + 0.001; dm.receiveShadow = true; dm.renderOrder = 1;
      dm.customDepthMaterial = new THREE.MeshDepthMaterial({ alphaMap: dt, alphaTest: 1.01 });   // casts nothing
      g.add(dm);
      return g;
    },
  });

  /* =======================================================================================
   * yard: a ready lawn of St. Augustine
   * ===================================================================================== */
  K.define('yard', {
    size: [8, 0.12, 6],
    options: { size: [8, 6], dryness: 0.15, edge: true, budget: 38000 },
    note: 'Options: size m (a number or [w, d]), dryness 0..1 watered green to Texas-August straw, edge (a mown edge) bool, budget (triangles for the blades). A St. Augustine lawn patch: a lawn-green base painted with blade strokes and slow patches, and ~5000 instanced clumps of broad, blunt, folded blades with per-clump colour, so a frame can lay real grass instead of tufts on dirt.',
    make(o, r) {
      const g = new THREE.Group();
      const sz = opt(o, 'size', [8, 6]), W = Array.isArray(sz) ? sz[0] : sz, D = Array.isArray(sz) ? sz[1] : sz;
      const dry = Math.max(0, Math.min(1, opt(o, 'dryness', 0.15)));
      const T = lawnTex(dry);
      // base: subdivided, slow colour patches in vertex colour so the tile never reads
      const seg = 40, base = new THREE.PlaneGeometry(W, D, seg, seg); base.rotateX(-Math.PI / 2);
      const pos = base.attributes.position, col = new Float32Array(pos.count * 3), uv = base.attributes.uv;
      const ph = [r() * 6, r() * 6, r() * 6, r() * 6];
      const patch = (x, z) => 0.5 + 0.2 * Math.sin(x * 0.37 + z * 0.21 + ph[0]) + 0.15 * Math.sin(-x * 0.23 + z * 0.51 + ph[1]) + 0.1 * Math.sin(x * 0.9 - z * 0.7 + ph[2]);
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), z = pos.getZ(i), p = patch(x, z), k = 0.82 + 0.3 * p;
        col[i * 3] = k * (1 + dry * 0.1 * (p - 0.5)); col[i * 3 + 1] = k; col[i * 3 + 2] = k * 0.95;
        uv.setXY(i, (x + W / 2) / T.metres, (z + D / 2) / T.metres);
        pos.setY(i, 0.042 + 0.003 * Math.sin(x * 3.1 + ph[3]) * Math.sin(z * 2.7));   // sod sits proud of the dirt, clear of any contact decal
      }
      base.setAttribute('color', new THREE.BufferAttribute(col, 3)); base.computeVertexNormals();
      const bm = new THREE.MeshStandardMaterial({ color: 0xffffff, map: T.map, bumpMap: T.bump, bumpScale: 1.2, roughness: 0.95, vertexColors: true });
      const bmesh = new THREE.Mesh(base, bm); g.add(bmesh);
      const soil = new THREE.Mesh(new THREE.BoxGeometry(W - 0.01, 0.036, D - 0.01), mat('sodedge', () => new THREE.MeshStandardMaterial({ color: 0x3b3024, roughness: 1 })));
      soil.position.y = 0.018; g.add(soil);
      // clump: 9 broad blunt blades, each a tapered quad folded along its midrib (3 tris)
      const P = [], C = [], NN = [];
      const cr = K.rng(4242);
      for (let b = 0; b < 12; b++) {
        const a = cr() * Math.PI * 2, d = cr() * 0.06, bw = 0.008 + cr() * 0.004, h = 0.035 + cr() * 0.045, lean = 0.8 + cr() * 1.0;
        const ox = Math.cos(a) * d, oz = Math.sin(a) * d, dx = Math.cos(a), dz = Math.sin(a), px = -dz, pz = dx;
        const tip = [ox + dx * h * lean * 0.8, h, oz + dz * h * lean * 0.8];
        const L0 = [ox + px * bw, 0, oz + pz * bw], R0 = [ox - px * bw, 0, oz - pz * bw];
        const tris = [[L0, R0, tip]];
        const c0 = [0.72, 0.76, 0.66], c1 = [1.0, 1.0, 1.0];
        tris.forEach((tr) => tr.forEach((v) => { P.push(...v); const t = v[1] / h; const c = mix(c0, c1, Math.min(1, t)); C.push(...c); NN.push(dx * 0.25, 1, dz * 0.25); }));
      }
      const cg = new THREE.BufferGeometry();
      cg.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
      cg.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
      const nn = new Float32Array(NN); for (let i = 0; i < nn.length; i += 3) { const l = Math.hypot(nn[i], nn[i + 1], nn[i + 2]); nn[i] /= l; nn[i + 1] /= l; nn[i + 2] /= l; }
      cg.setAttribute('normal', new THREE.BufferAttribute(nn, 3));
      const gm = mat('stAug', () => oneFace(new THREE.MeshStandardMaterial({ vertexColors: true, side: THREE.DoubleSide, roughness: 0.72 })));
      const tri = 12, budget = (opt(o, 'budget', 38000)) - 2 * seg * seg, count = Math.max(200, Math.min(Math.floor(budget / tri), Math.round(W * D * 140)));
      const im = new THREE.InstancedMesh(cg, gm, count), Mx = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new V3(), p = new V3(), c = new THREE.Color();
      const green = [0.36, 0.52, 0.16], blue = [0.3, 0.5, 0.18], straw = [0.7, 0.6, 0.34], tan = [0.58, 0.5, 0.3];
      const edge = opt(o, 'edge', true) ? 0.04 : 0;
      for (let i = 0; i < count; i++) {
        const x = (r() - 0.5) * (W - edge * 2), z = (r() - 0.5) * (D - edge * 2), pp = patch(x, z);
        e.set((r() - 0.5) * 0.3, r() * 6.283, (r() - 0.5) * 0.3); q.setFromEuler(e);
        const k = 0.7 + r() * 0.6; s.set(k, 0.55 + r() * 0.6, k); p.set(x, 0.036, z);
        Mx.compose(p, q, s); im.setMatrixAt(i, Mx);
        const dd = Math.max(0, Math.min(1, dry + (pp - 0.5) * 0.35 + (r() - 0.5) * 0.2));
        let cc = mix(mix(green, blue, r()), mix(straw, tan, r()), dd);
        const j = 0.8 + r() * 0.4; c.setRGB(cc[0] * j, cc[1] * j, cc[2] * j, THREE.SRGBColorSpace); im.setColorAt(i, c);
      }
      im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true;
      // blades this small never read in a shadow map; cast into it they only blot the lawn
      // (TXT.add turns casting on for every mesh, so the depth pass is told to discard instead)
      im.customDepthMaterial = new THREE.MeshDepthMaterial({ alphaTest: 1.01 });
      im.customDistanceMaterial = new THREE.MeshDistanceMaterial({ alphaTest: 1.01 });
      g.add(im);
      return g;
    },
  });
}
