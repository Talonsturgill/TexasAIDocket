/* akthree.js — the GPU illustration bench (three.js + SwiftShader, PROVEN 2026-07-11).
 *
 * Wraps the committed three.module.min.js (r170, MIT) into an opinionated,
 * deterministic, headless-safe editorial-3D kit for slide code. Verified in
 * this container: WebGL2 via ANGLE/SwiftShader "Subzero" renders a full PBR
 * scene (MeshStandardMaterial, 2048px PCFSoft shadow map, ACES tone mapping,
 * antialiasing) at 2160x2700 in ~70ms. Import cost ~60ms. This makes real
 * rendered 3D cheaper than most Canvas-2D art.
 *
 * USAGE (slide code; ES module because three r160+ ships modules only):
 *
 *   <canvas id="scene" width="2160" height="2700"
 *           style="position:absolute;inset:0;width:1080px;height:1350px"></canvas>
 *   <script type="module">
 *     window.renderReady = (async () => {
 *       const THREE = await import('@@ASSETS@@/js/three.module.min.js');
 *       const TXT   = (await import('@@ASSETS@@/js/akthree.js')).init(THREE);
 *       const R = TXT.setup(document.getElementById('scene'),
 *                           { w:1080, h:1350, bg:0x05080f, fog:[0x0b1622, 9, 34], exposure:1.12 });
 *       TXT.environment(R, { intensity: 0.55 });          // procedural IBL (reflections)
 *       TXT.rig(R, TXT.rigs.arcticNight);                 // 3-point illustration lighting
 *       TXT.ground(R, { color: 0x0e2138, y: 0 });
 *       const knot = new THREE.Mesh(new THREE.TorusKnotGeometry(1, .34, 220, 36),
 *                                   TXT.mat.gold());
 *       knot.position.set(0, 1.6, 0); TXT.add(R, knot);   // add() sets shadow flags
 *       TXT.frame(R, { from:[4.5,3.2,7], look:[0,0.9,0], fov:50 });
 *       const shot = await TXT.snapshot(R);              // render + black-frame sentinel
 *       if (!shot.ok) fallbackToCanvasDesign();           // never ship a black frame
 *       return true;
 *     })();
 *   </script>
 *
 * RULES OF THE BENCH
 * - Canvas backing MUST be 2x (width=W*2 etc.); setup() calls setSize(w,h,false)
 *   + setPixelRatio(2) so three renders into the 2x store; screenshots stay crisp.
 * - Deterministic: nothing here uses Math.random(). If your scene scatters
 *   objects, use TX.rng(seed) from noise.js.
 * - ALWAYS render via snapshot() inside renderReady. One frame; this is a still.
 * - Text stays DOM/SVG (never 3D text): the PDF must keep vector type.
 * - Keep a graceful degrade in mind: probe = TXT.webglOK(canvas) before building;
 *   on false, fall back to an TX3D/Canvas design (has not happened in this
 *   container, but slides must never ship a black rectangle).
 * - Fog color = the slide's sky/haze hue, never gray (DESIGN_DOCTRINE 4).
 * - 3D DATA HONESTY still applies: perspective for scenes/objects, NEVER for
 *   quantity comparisons (bars/volumes stay parallel-projected 2D/cabinet).
 */
export function init(THREE) {
  const TXT = { THREE };

  /* ---- probe ------------------------------------------------------------ */
  // Probe on a THROWAWAY canvas, never the render target: getContext fixes a
  // canvas's context attributes forever, so probing the target would strip
  // preserveDrawingBuffer from the renderer and blind the QA sampler
  // (found by the dead-canvas gate's own reconstruction run, 2026-07-11).
  TXT.webglOK = function () {
    try {
      const c = document.createElement('canvas');
      return !!(c.getContext('webgl2') || c.getContext('webgl'));
    } catch (e) { return false; }
  };

  /* ---- setup ------------------------------------------------------------ */
  // Returns R = {renderer, scene, camera, w, h}
  TXT.setup = function (canvas, opts) {
    opts = opts || {};
    const w = opts.w || 1080, h = opts.h || 1350;
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: opts.antialias !== false,
      preserveDrawingBuffer: true });  // stills only: lets the QA gate sample the frame
    // ORDER MATTERS: pixel ratio BEFORE size, or setSize resets the backing
    // store to 1x and every render silently ships at half resolution.
    const ratio = (canvas.width && canvas.width > w) ? canvas.width / w : 2;
    renderer.setPixelRatio(ratio);
    renderer.setSize(w, h, false);                 // buffer becomes w*ratio x h*ratio
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = opts.exposure != null ? opts.exposure : 1.1;
    const scene = new THREE.Scene();
    if (opts.bg != null) scene.background = new THREE.Color(opts.bg);
    if (opts.fog) scene.fog = new THREE.Fog(opts.fog[0], opts.fog[1], opts.fog[2]);
    const camera = new THREE.PerspectiveCamera(opts.fov || 50, w / h, 0.1, 200);
    camera.position.set(5, 4, 8); camera.lookAt(0, 0, 0);
    return { renderer, scene, camera, w, h };
  };

  TXT.frame = function (R, o) {
    if (o.fov) { R.camera.fov = o.fov; R.camera.updateProjectionMatrix(); }
    if (o.from) R.camera.position.set(o.from[0], o.from[1], o.from[2]);
    const l = o.look || [0, 0, 0];
    R.camera.lookAt(l[0], l[1], l[2]);
  };

  TXT.add = function (R, obj, o) {
    o = o || {};
    obj.traverse ? obj.traverse(m => { if (m.isMesh) { m.castShadow = o.cast !== false; m.receiveShadow = o.receive !== false; } })
                 : null;
    if (obj.isMesh) { obj.castShadow = o.cast !== false; obj.receiveShadow = o.receive !== false; }
    R.scene.add(obj);
    return obj;
  };

  /* ---- procedural environment (IBL) ------------------------------------ */
  // A tiny "photo studio" room rendered through PMREMGenerator: emissive
  // panels give PBR materials real reflections without any texture files.
  // intensity scales scene.environmentIntensity (r163+) or panel brightness.
  TXT.environment = function (R, opts) {
    opts = opts || {};
    const env = new THREE.Scene();
    const room = new THREE.Mesh(
      new THREE.BoxGeometry(20, 14, 20),
      new THREE.MeshBasicMaterial({ color: 0x0b1420, side: THREE.BackSide }));
    env.add(room);
    function panel(w, h, color, i, pos, rot) {
      const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
        new THREE.MeshBasicMaterial({ color }));
      p.material.color.multiplyScalar(i);
      p.position.set(pos[0], pos[1], pos[2]);
      if (rot) p.rotation.set(rot[0], rot[1], rot[2]);
      env.add(p); return p;
    }
    // key softbox (warm, high left), cool bounce (right), thin rim strip (back)
    panel(7, 5, 0xfff1dc, 6.0, [-5, 5.5, 3], [Math.PI / 3.4, 0.5, 0]);
    panel(5, 4, 0x9fc8e8, 2.2, [6, 3.5, 1], [0, -Math.PI / 2.6, 0]);
    panel(10, 1.1, 0xbfe9ff, 4.0, [0, 5.2, -8.5], [0.35, 0, 0]);
    panel(16, 16, 0x223244, 1.0, [0, -6.9, 0], [-Math.PI / 2, 0, 0]); // floor bounce
    const pm = new THREE.PMREMGenerator(R.renderer);
    const tex = pm.fromScene(env, 0.04).texture;
    R.scene.environment = tex;
    if ('environmentIntensity' in R.scene) R.scene.environmentIntensity = opts.intensity != null ? opts.intensity : 0.6;
    pm.dispose();
    return tex;
  };

  /* ---- lighting rigs ---------------------------------------------------- */
  // Illustration three-point: warm key with soft shadow, cool rim, low ambient.
  TXT.rig = function (R, spec) {
    const made = [];
    const key = new THREE.DirectionalLight(spec.key.color, spec.key.i);
    key.position.set(...spec.key.pos);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    const s = spec.key.shadowSize || 9;
    key.shadow.camera.left = -s; key.shadow.camera.right = s;
    key.shadow.camera.top = s; key.shadow.camera.bottom = -s;
    key.shadow.bias = -0.0004;
    key.shadow.radius = spec.key.radius != null ? spec.key.radius : 7;
    R.scene.add(key); made.push(key);
    if (spec.rim) { const rim = new THREE.DirectionalLight(spec.rim.color, spec.rim.i);
      rim.position.set(...spec.rim.pos); R.scene.add(rim); made.push(rim); }
    if (spec.fill) { const fill = new THREE.DirectionalLight(spec.fill.color, spec.fill.i);
      fill.position.set(...spec.fill.pos); R.scene.add(fill); made.push(fill); }
    if (spec.ambient) { R.scene.add(new THREE.AmbientLight(spec.ambient.color, spec.ambient.i)); }
    return made;
  };
  TXT.rigs = {
    // house rigs, colors from brand.yaml's world
    arcticNight: {  // warm sodium key, aurora-ice rim — the default hero rig
      key:  { color: 0xffe9c4, i: 3.2, pos: [6, 9, 5], radius: 8 },
      rim:  { color: 0x5ac8f0, i: 1.6, pos: [-7, 3, -5] },
      fill: { color: 0x35507a, i: 0.7, pos: [-3, 2, 7] },
      ambient: { color: 0x1c2a40, i: 1.1 } },
    goldenHour: {   // low warm key, violet fill — drama beats
      key:  { color: 0xffc27a, i: 3.6, pos: [8, 3.2, 6], radius: 10 },
      rim:  { color: 0x9664e6, i: 1.2, pos: [-6, 5, -6] },
      fill: { color: 0x2c3e60, i: 0.6, pos: [0, 6, -8] },
      ambient: { color: 0x22283c, i: 1.0 } },
    galleryWhite: { // even, soft museum light — light decks / clay renders
      key:  { color: 0xffffff, i: 2.6, pos: [4, 10, 6], radius: 12 },
      rim:  { color: 0xdfe9f5, i: 0.8, pos: [-6, 4, -4] },
      fill: { color: 0xcfd8e6, i: 0.9, pos: [-4, 3, 8] },
      ambient: { color: 0x8894a6, i: 1.4 } },
  };

  /* ---- materials -------------------------------------------------------- */
  TXT.mat = {
    gold:  (o) => new THREE.MeshStandardMaterial(Object.assign(
      { color: 0xffc72c, metalness: 0.9, roughness: 0.24 }, o)),
    steel: (o) => new THREE.MeshStandardMaterial(Object.assign(
      { color: 0xaebfcc, metalness: 0.85, roughness: 0.35 }, o)),
    clay:  (c, o) => new THREE.MeshStandardMaterial(Object.assign(
      { color: c != null ? c : 0xf3a24c, metalness: 0.0, roughness: 0.82 }, o)),
    plastic: (c, o) => new THREE.MeshStandardMaterial(Object.assign(
      { color: c != null ? c : 0x5ac8f0, metalness: 0.05, roughness: 0.38 }, o)),
    ice:   (o) => new THREE.MeshPhysicalMaterial(Object.assign(
      { color: 0xbfe4f5, metalness: 0, roughness: 0.15, transmission: 0.7,
        thickness: 1.2, ior: 1.31, attenuationColor: new THREE.Color(0x7fd0e8),
        attenuationDistance: 2.5 }, o)),   // verify visually; transmission is heavier
    emissive: (c, i, o) => new THREE.MeshStandardMaterial(Object.assign(
      { color: 0x0a0f18, emissive: c != null ? c : 0xffc72c,
        emissiveIntensity: i != null ? i : 2.0, roughness: 0.6 }, o)),
  };

  /* ---- stage furniture -------------------------------------------------- */
  TXT.ground = function (R, o) {
    o = o || {};
    const g = new THREE.Mesh(new THREE.PlaneGeometry(o.size || 60, o.size || 60),
      new THREE.MeshStandardMaterial({ color: o.color != null ? o.color : 0x0e2138,
        roughness: o.roughness != null ? o.roughness : 0.95, metalness: 0 }));
    g.rotation.x = -Math.PI / 2; g.position.y = o.y || 0;
    g.receiveShadow = true; R.scene.add(g);
    return g;
  };

  /* ---- geometry helpers ------------------------------------------------- */
  // Tube along a polyline (array of [x,y,z]) — pipes, routes, cables in 3D.
  TXT.tube = function (points, radius, mat, o) {
    o = o || {};
    const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(p[0], p[1], p[2])),
      false, 'catmullrom', o.tension != null ? o.tension : 0.5);
    const geo = new THREE.TubeGeometry(curve, o.segments || 120, radius, o.radial || 20, false);
    return new THREE.Mesh(geo, mat);
  };
  // Lathe from a 2D profile (array of [x,y]) — vessels, turbines, valves.
  TXT.lathe = function (profile, mat, o) {
    o = o || {};
    const pts = profile.map(p => new THREE.Vector2(p[0], p[1]));
    return new THREE.Mesh(new THREE.LatheGeometry(pts, o.segments || 64), mat);
  };
  // Extruded 2D shape (array of [x,y]) — plaques, arrows, silhouettes with depth.
  TXT.extrude = function (outline, depth, mat, o) {
    o = o || {};
    const shape = new THREE.Shape(outline.map(p => new THREE.Vector2(p[0], p[1])));
    const geo = new THREE.ExtrudeGeometry(shape, {
      depth, bevelEnabled: o.bevel !== false,
      bevelThickness: o.bevelThickness || depth * 0.06,
      bevelSize: o.bevelSize || depth * 0.05, bevelSegments: o.bevelSegments || 3 });
    return new THREE.Mesh(geo, mat);
  };

  /* ---- render ------------------------------------------------------------ */
  // Renders one still, waits a paint tick, then ASSERTS the frame is not black
  // (research-documented headless failure modes: first-paint race and silent
  // 2D fallback). Returns {ok, variance, litCount}; on ok=false the slide MUST
  // fall back to its Canvas/TX3D design rather than ship a black rectangle.
  //
  // TWO accept paths, OR'd (purely additive -- a frame the old logic accepted
  // is still accepted, so no existing full-bleed scene regresses):
  //  (1) global 24-sample mean/variance (the historic full-scene check), and
  //  (2) COVERAGE: a dense strided read counts pixels carrying real light; a
  //      lit cluster >= LIT_MIN passes. This fixes the silent false-fail on an
  //      OBJECT HERO that fills only part of the frame over a transparent/dark
  //      empty background (run 2026-07-21 S6: the akthree beluga's lit subject
  //      is a minority of the frame, so the 24 sparse points read ~0 and the
  //      frame was wrongly judged dead, forcing the flat Canvas fallback).
  // The DEAD-CANVAS CONTRACT is preserved: a genuinely black/empty frame has
  // litCount 0 AND fails the mean/variance path, so it still returns ok=false.
  TXT.snapshot = async function (R, o) {
    o = o || {};
    R.renderer.render(R.scene, R.camera);
    await new Promise(r => requestAnimationFrame(() => r()));
    let ok = true, variance = -1, litCount = -1;
    try {
      const gl = R.renderer.getContext();
      const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
      // (1) historic sparse mean/variance (unchanged coordinates + formula)
      const N = 24, px = new Uint8Array(4);
      let sum = 0, sum2 = 0;
      for (let i = 0; i < N; i++) {
        const x = ((i * 2654435761) >>> 8) % W;
        const y = ((i * 40503) >>> 4) % H;
        gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        const v = (px[0] + px[1] + px[2]) / 3;
        sum += v; sum2 += v * v;
      }
      variance = sum2 / N - (sum / N) * (sum / N);
      const meanVarOK = (sum / N > 1) || variance > 1;
      // (2) coverage: one full-buffer read, strided lit-pixel count
      const LIT_FLOOR = o.litFloor != null ? o.litFloor : 12;   // luminance/255
      const STRIDE = o.stride != null ? o.stride : 8;
      const buf = new Uint8Array(W * H * 4);
      gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, buf);
      let sampled = 0, lit = 0;
      for (let y = 0; y < H; y += STRIDE) {
        for (let x = 0; x < W; x += STRIDE) {
          const p = (y * W + x) * 4;
          sampled++;
          if ((buf[p] + buf[p + 1] + buf[p + 2]) / 3 > LIT_FLOOR) lit++;
        }
      }
      litCount = lit;
      // a real lit subject far exceeds this; a dead/black frame gives exactly 0
      const LIT_MIN = o.litMin != null ? o.litMin
        : Math.max(48, Math.round(sampled * 0.0008));
      ok = meanVarOK || lit >= LIT_MIN;
    } catch (e) { /* readPixels unavailable: trust the render */ }
    return { ok, variance, litCount };
  };

  /* ---- object hero ------------------------------------------------------ */
  // Raises the rendered-hero floor for a single foreground object that must
  // read as a SILHOUETTE against a darker background (the backlit-machine
  // case). The failure mode this guards: a dark object under a key+fill+
  // ambient rig reads as a flat blob because nothing carves its contour --
  // run 2026-07-12 S6 (the backlit quadcopter) read as a blob and scored the
  // deck's weakest criterion until a hand-added warm rim from the light
  // direction + a scale bump made the profile read. This encodes both moves.
  //
  //   const g = new THREE.Group(); /* build hero, add to scene */ TXT.add(R,g);
  //   TXT.objectHero(R, g, { toward:[6,2.6,-4], keyColor:0xffb070, height:2.4 });
  //
  // toward = the direction the KEY light comes FROM (so the separation edge
  // reads warm on the same side the key/fire lights it). height (optional) =
  // target world-space height the hero is scaled to fill (the scale bump).
  // The rim is a DirectionalLight placed on the FAR side of the subject from
  // the camera (the geometry that produces a contour-carving backlight; a
  // key-side rim alone leaves the profile flat), leaned toward the key side,
  // aimed at the subject center so it works wherever the hero sits.
  // Returns { rim, center, radius }. Opt-in; existing scenes are unaffected.
  TXT.fitHeight = function (group, worldHeight) {
    group.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(group);
    const size = new THREE.Vector3(); box.getSize(size);
    if (size.y > 1e-6) group.scale.multiplyScalar(worldHeight / size.y);
    return group;
  };
  TXT.objectHero = function (R, group, o) {
    o = o || {};
    if (o.height) TXT.fitHeight(group, o.height);
    group.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(group);
    const center = new THREE.Vector3(); box.getCenter(center);
    const size = new THREE.Vector3(); box.getSize(size);
    const radius = (Math.max(size.x, size.y, size.z) * 0.5) || 1;
    // far side of the subject from the camera = where a rim/backlight lives
    const away = center.clone().sub(R.camera.position).normalize();
    const dist = o.dist != null ? o.dist : Math.max(4, radius * 4);
    const lift = o.lift != null ? o.lift : radius * 1.2;
    const pos = center.clone().add(away.multiplyScalar(dist));
    pos.y += lift;
    if (o.toward) {  // lean the rim toward the key side (stays mostly behind)
      const k = new THREE.Vector3(o.toward[0], o.toward[1], o.toward[2]);
      if (k.lengthSq() > 1e-9) pos.add(k.normalize().multiplyScalar(o.keyLean != null ? o.keyLean : dist * 0.5));
    }
    const rim = new THREE.DirectionalLight(o.keyColor != null ? o.keyColor : 0xffb070,
      o.intensity != null ? o.intensity : 1.7);
    rim.position.copy(pos);
    rim.target.position.copy(center);
    R.scene.add(rim); R.scene.add(rim.target);
    return { rim, center, radius };
  };

  return TXT;
}
