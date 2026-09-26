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
    /* SOFT SHADOWS THAT ARE SOFT (2026-09-24). PCFSoftShadowMap ignores shadow.radius, so every
     * rig's radius was dead for two months and every cast shadow shipped hard edged. VSM honours
     * radius and blurSamples. `shadows:'pcfsoft'` restores the old behaviour. */
    renderer.shadowMap.type = opts.shadows === 'pcfsoft' ? THREE.PCFSoftShadowMap : THREE.VSMShadowMap;
    // tone: 'aces' (default, the old look), 'agx' (graceful highlights: a sun that
    // rolls off instead of clipping yellow), 'neutral' (Khronos PBR Neutral, true brand colour)
    renderer.toneMapping = opts.tone === 'agx' ? THREE.AgXToneMapping
      : opts.tone === 'neutral' ? THREE.NeutralToneMapping : THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = opts.exposure != null ? opts.exposure : 1.1;
    const scene = new THREE.Scene();
    if (opts.bg != null) scene.background = new THREE.Color(opts.bg);
    // fog:[colour, near, far] is linear, as before. fog:[colour, density] is exponential, which is
    // how haze actually thickens with distance and the form a world preset hands you.
    if (opts.fog) scene.fog = opts.fog.length === 2 ? new THREE.FogExp2(opts.fog[0], opts.fog[1])
      : new THREE.Fog(opts.fog[0], opts.fog[1], opts.fog[2]);
    // far is 1000 so a ground that reaches the horizon is not clipped short of the fog
    const camera = new THREE.PerspectiveCamera(opts.fov || 50, w / h, opts.near || 0.1, opts.far || 1000);
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
    /* A WORLD'S SKY ALREADY LIT THIS FRAME (2026-09-24). TXT.sky renders the IBL from the same sky
     * the frame shows, so a studio environment called after it by habit would swap the orange
     * horizon in every reflection for a grey room. `force:true` overrides, for an interior. */
    if (R.world && !opts.force) return R.scene.environment;
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
    key.shadow.blurSamples = spec.key.blurSamples || 20;   // VSM only: smooth, not banded
    if (spec.key.mapSize) key.shadow.mapSize.set(spec.key.mapSize, spec.key.mapSize);
    R.scene.add(key); made.push(key);
    if (spec.rim) { const rim = new THREE.DirectionalLight(spec.rim.color, spec.rim.i);
      rim.position.set(...spec.rim.pos); R.scene.add(rim); made.push(rim); }
    if (spec.fill) { const fill = new THREE.DirectionalLight(spec.fill.color, spec.fill.i);
      fill.position.set(...spec.fill.pos); R.scene.add(fill); made.push(fill); }
    if (spec.ambient) { R.scene.add(new THREE.AmbientLight(spec.ambient.color, spec.ambient.i)); }
    return made;
  };
  /* THE DECK'S LIGHT, READ FROM THE CHASSIS AND NEVER RESTATED (2026-09-23).
   * A frame rendered here used to pick a rig from TXT.rigs, and a rig carries its own key
   * position, which is a SECOND copy of the deck's light that nothing checks against the first.
   * That shape shipped the wrong site URL on three decks and a scene light disagreeing with its
   * chassis on others. deckRig takes the key's DIRECTION from TXDECK.declare's light and keeps
   * only colour and intensity from the spec, so nine frames rendered from nine cameras are lit
   * by one sun in the world, by construction. depth_floor.py reads a frame that calls this as
   * agreeing with its chassis, and a frame that calls TXT.rig alone as unreadable, fail closed.
   *
   * World convention, fixed here once: +Y up, the default camera sits toward +Z looking at the
   * origin, az is degrees clockwise from +Z toward +X, el is degrees above the ground plane. */
  TXT.deckRig = function (R, spec, o) {
    o = o || {};
    const TXD = (typeof window !== 'undefined') ? window.TXDECK : null;
    if (!TXD || !TXD.deck) throw new Error('TXT.deckRig needs txdeck.js and a TXDECK.declare');
    const L = TXD.deck().light;
    const a = L.az * Math.PI / 180, e = L.el * Math.PI / 180, dist = o.distance || 14;
    // o.target moves where the key AIMS, never which way it points: the key sits at the same
    // direction from the target, so a yard forty metres long keeps its shadows inside the key's
    // shadow camera without anybody restating the light.
    const t = o.target || [0, 0, 0];
    const pos = [t[0] + dist * Math.sin(a) * Math.cos(e), t[1] + dist * Math.sin(e), t[2] + dist * Math.cos(a) * Math.cos(e)];
    const s = Object.assign({}, spec, { key: Object.assign({}, spec.key, { pos: pos }) });
    const made = TXT.rig(R, s);
    made[0].target.position.set(t[0], t[1], t[2]);
    R.scene.add(made[0].target);
    if (o.shadowFar) made[0].shadow.camera.far = o.shadowFar;
    made[0].shadow.normalBias = o.normalBias != null ? o.normalBias : 0.02;  // no acne on thin parts
    made[0].shadow.camera.updateProjectionMatrix();
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

  /* TXT.skyInFrame(camera) — the share of the frame's height above the horizon, 0 to 1, from the
   * camera's pitch and field of view (lookAt keeps roll at zero). 0 is a camera that shows no sky:
   * pitched down past half its field of view, or orthographic and pitched down at all, because an
   * orthographic camera's rays are parallel and every one of them points where it points (Codex,
   * PR 369: a cut-off at 11.5 degrees let the shallower top-down views through). */
  TXT.skyInFrame = function (camera) {
    const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
    if (camera.isOrthographicCamera) return fwd.y < -1e-3 ? 0 : fwd.y > 1e-3 ? 1 : 0.5;
    const pitch = Math.asin(Math.max(-1, Math.min(1, fwd.y)));
    // the field three.js actually projects, 2 atan(tan(fov / 2) / zoom): dividing the angle by the
    // zoom overstated a zoomed-out camera's field and found sky it doesn't show (Codex, PR 369)
    const half = THREE.MathUtils.degToRad((camera.getEffectiveFOV ? camera.getEffectiveFOV() : (camera.fov || 50)) / 2);
    if (Math.abs(pitch) >= Math.PI / 2 - 1e-4) return pitch < 0 ? 0 : 1;
    const y = Math.tan(-pitch) / Math.tan(half);            // the horizon's height in NDC
    return y >= 1 ? 0 : y <= -1 ? 1 : (1 - y) / 2;
  };
  /* TXT.enclosed(R) — true when something the frame built stands over the camera within `reach`
   * metres: a cab roof, a ceiling, a canopy. A camera under a roof looking down is inside, and the
   * showstopper test's question 3 accepts "a deliberate interior" as readily as a sky. Measured with
   * one ray straight up, never guessed from the source, so a chassis that builds its own cab needs no
   * flag to say so (no. 34's frame 6, a page on the cab seat, is the case). The sky dome is the
   * world, not a roof, and is never hit. */
  TXT.enclosed = function (R, reach) {
    const rc = new THREE.Raycaster(R.camera.position.clone(), new THREE.Vector3(0, 1, 0), 0.05, reach || 12);
    rc.camera = R.camera;
    const hit = [];
    R.scene.traverse((m) => { if (m.isMesh && m.visible && !(m.userData && m.userData.txSky)) hit.push(m); });
    try { return rc.intersectObjects(hit, false).length > 0; } catch (e) { return false; }
  };
  /* TXT.inRoom(R) — true when the camera stands inside the room TXT.interior built, or looks down
   * into it. A room answers the showstopper test's question 3 only for a camera that shows it, so
   * a camera moved outside it, a room taken out of the scene before the snapshot, or a room left
   * standing in the distance is not an interior shot (Codex, PR 369: the first cut exempted any
   * frame that had called TXT.interior at all). The room's walls give its bounds, with a margin of
   * about one wall's thickness, and the look point is where the camera's own ray meets its floor. */
  TXT.inRoom = function (R) {
    const room = R.room;
    if (!room || !room.isObject3D || !room.parent || !room.visible) return false;
    const box = new THREE.Box3().setFromObject(room);
    if (box.isEmpty()) return false;
    const floorY = box.min.y;
    box.expandByScalar(0.25);
    const cam = R.camera.position;
    if (box.containsPoint(cam)) return true;
    const fwd = new THREE.Vector3(); R.camera.getWorldDirection(fwd);
    if (fwd.y > -1e-6) return false;
    const t = (floorY - cam.y) / fwd.y;
    if (!(t > 0)) return false;
    const p = cam.clone().addScaledVector(fwd, t);
    return p.x >= box.min.x && p.x <= box.max.x && p.z >= box.min.z && p.z <= box.max.z;
  };
  // Read by scripts/carousel/print_ban.py off the render report. Keep the two in step.
  TXT.NO_SKY = 'TXT: NO SKY IN FRAME';

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
    /* A WORLD THE CAMERA DOESN'T SHOW IS A VOID (2026-09-26). No. 33's frame 4 called TXT.sky and
     * looked straight down on a lawn, and a judge named it top-down in every one of five rounds.
     * print_ban counted the call. This counts what the camera shows, and the render report carries
     * it to print_ban before a panel sits. Measured on the shipped decks: no. 33's frame 4 and no.
     * 34's frames 4 and 5 print it, and no. 34's page on the cab seat does not. */
    // A ROOM THE CAMERA SHOWS IS EXEMPT: "a sky or a deliberate interior" is the test's own question
    // 3, and a desk or a document looked down on stands in a room TXT.interior built (ILLUSTRATION_SYSTEM,
    // The gate). TXT.inRoom asks whether this camera stands in that room or looks into it.
    if (R.world && o.skyCheck !== false && typeof console !== 'undefined') {
      const sky = TXT.skyInFrame(R.camera);
      if (typeof window !== 'undefined') window.TXT_SKY_IN_FRAME = sky;
      if (sky <= 0 && !TXT.enclosed(R) && !TXT.inRoom(R)) console.error(TXT.NO_SKY + '. This frame calls TXT.sky and its camera shows none of ' +
        'it (pitched below the horizon or looking straight down), with nothing overhead. A reader sees ' +
        'objects in a void, and the showstopper test caps the frame. Lift the camera to put the horizon in ' +
        'frame, or stand it inside something built (a room with TXT.interior, a cab, a canopy)');
    }
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
    /* THE FRAME IS ALREADY TONE MAPPED, and TXDECK.finish reads this so it does not map it
     * again. Carousel no. 32 ran ACES here and a second ACES curve in the grade, which caps
     * white near 231 of 255 and lifts the mids: the murk measured, not a taste. Marked ONLY
     * when the render is good and kept, because a frame that falls back to a canvas design
     * after a black render still wants the grade's own curve (Codex, #353). */
    // ASSIGNED, never only set: the last snapshot is the one a frame keeps, so a good preliminary
    // render followed by a failed final one must not leave the mark behind (Codex, #353).
    if (typeof window !== 'undefined') {
      const mapped = ok && R.renderer.toneMapping !== THREE.NoToneMapping;
      window.TXT_TONEMAPPED = mapped;
      try {
        if (mapped) R.renderer.domElement.setAttribute('data-tonemapped', '1');
        else R.renderer.domElement.removeAttribute('data-tonemapped');
      } catch (e) {}
    }
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

  /* ======================================================================================
   * THE WORLD (2026-09-24). What every frame used to have to invent, built once, here.
   *
   * WHY. Thirty two decks in, the craft finding is the same one in new words: an object in a
   * void. The engine handed a frame a renderer, a flat background colour and a grey plane, and
   * every chassis then wrote its own sky, its own ground texture and its own develop step under
   * a deadline, nine different ways across seven decks (assets/js/deck/). Carousel no. 32's
   * sky was a dome of near black with a two degree horizon band, its ground a flat plane
   * with a noise texture, and its shadows were hard, because TXT.rig set shadow.radius and
   * PCFSoftShadowMap IGNORES radius. The rigs asked for soft shadows for two months and
   * never got one.
   *
   * WHAT A WORLD IS. One sky, and everything else derived from it, so nothing can disagree:
   *   - the SKY dome, a shader: zenith to horizon gradient, a haze band, the sun's glow and
   *     disc at the deck's declared light, warm horizon on the sun's side, optional cloud
   *     streaks and stars. Seeded, never Math.random.
   *   - the ENVIRONMENT (IBL) rendered FROM THAT SKY, so a steel skin reflects the orange
   *     horizon at golden hour and the blue zenith at noon, rather than the grey studio room.
   *   - FOG in the horizon's own hue, so the ground dissolves into the sky at the horizon.
   *   - SOFT SHADOWS that are actually soft (VSM, radius honoured) plus CONTACT shadows, the
   *     dark core where a thing meets the ground, which is what stops it floating.
   *   - a GROUND with tooth: a surface texture, roughness that varies, macro variation so the
   *     tiling never shows, reaching the horizon.
   *   - SCATTER: grass, scrub and stone, instanced and seeded, so a pad sits in a landscape.
   *   - ROUNDED geometry, because a real edge catches a highlight and a CG edge does not.
   *
   * USAGE, the whole stage in five calls (the depth gate reads frame, ground, deckRig, add):
   *
   *   // the chassis, once:  TXDECK.declare({ ..., light:{az:-62, el:8}, sky:'goldenHour' })
   *   const W = TXT.deckWorld();                             // the deck's one world, resolved
   *   const R = TXT.setup(gl, { w:1080, h:1350, fog:[W.haze, W.fogDensity], exposure:W.exposure,
   *                             tone:W.tone, fov:38 });
   *   TXT.frame(R, { from:[-14, 1.6, 22], look:[0, 3, 0] });
   *   TXT.sky(R, W);                                        // sky + IBL from the sky + fog tint
   *   TXT.deckRig(R, W.rig, { target:[0,0,0], distance:60 });   // the sun IS the deck's light
   *   TXT.ground(R, { surface:'caliche', size:900 });
   *   TXT.scatter(R, { kind:'grass', count:2600, area:[-60,-80,60,30], avoid:[[-8,-6,8,6]] });
   *                                                         // after TXT.frame: it thins with distance
   *                                                         // from wherever the camera is at the call
   *   const hero = TXT.add(R, myObject);  TXT.contact(R, hero);
   *   const shot = await TXT.snapshot(R);
   *
   * The sun sits where TXDECK.declare's light says, so the glow in the sky, the key light, the
   * cast shadows and the warm side of every object agree by construction on all nine frames.
   * Choose the declared elevation to suit the world: golden hour wants el 4 to 14, noon 55+.
   *
   * COST, measured 2026-09-24 in this container on no. 32's forty set yard: building the world
   * takes 0.4 s, the snapshot 6.2 s at the rig's default 2048 shadow map and 9.3 s at 4096, the
   * grade 1.2 s. render.py waits 30 s. Ask for rig.key.mapSize 4096 only for a close hero.
   * ====================================================================================== */

  /* ---- seeded helpers (deterministic, never Math.random) ------------------------------- */
  TXT.rng = function (seed) {
    let t = (seed >>> 0) || 1;
    return function () {
      t += 0x6D2B79F5; let r = Math.imul(t ^ (t >>> 15), 1 | t);
      r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  };
  function valueNoise(seed, nx, ny) {
    // a tileable lattice of values, bilinear-smoothed on read: noise(x, y) with x, y in lattice
    // units, periodic at nx across and ny down. Sample exactly one period across a texture and it
    // tiles; a stretched sample over part of a period leaves a seam at every repeat (Codex, #353).
    ny = ny || nx;
    const R0 = TXT.rng(seed), lat = new Float32Array(nx * ny);
    for (let i = 0; i < nx * ny; i++) lat[i] = R0();
    return function (x, y) {
      const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
      const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
      const x0 = ((xi % nx) + nx) % nx, y0 = ((yi % ny) + ny) % ny, x1 = (x0 + 1) % nx, y1 = (y0 + 1) % ny;
      const a = lat[y0 * nx + x0], b = lat[y0 * nx + x1], c = lat[y1 * nx + x0], d = lat[y1 * nx + x1];
      return (a + (b - a) * sx) + ((c + (d - c) * sx) - (a + (b - a) * sx)) * sy;
    };
  }
  function fbm(noise, x, y, oct) {
    let s = 0, a = 0.5, f = 1;
    for (let i = 0; i < (oct || 5); i++) { s += a * noise(x * f, y * f); f *= 2; a *= 0.5; }
    return s / (1 - Math.pow(0.5, oct || 5));
  }

  /* ---- the sun: the deck's declared light, as a direction toward the sun ---------------- */
  TXT.sunDir = function (o) {
    o = o || {};
    const TXD = (typeof window !== 'undefined') ? window.TXDECK : null;
    let L = null;
    try { if (TXD && TXD.deck) L = TXD.deck().light; } catch (e) { L = null; }
    // WITHOUT A DECK, a direction from `sunAt` ({az, el}) or else the middle of the world's own el
    // range. Never `o.sun`: in every preset that is the sun's COLOUR, a number, and reading az and
    // el off a number gave a NaN sun (Codex, #353).
    const range = Array.isArray(o.el) ? o.el : null;
    const fb = (o.sunAt && typeof o.sunAt.az === 'number' && typeof o.sunAt.el === 'number') ? o.sunAt
      : { az: -35, el: range ? (range[0] + range[1]) / 2 : 9 };
    const s = L || fb;
    // At night the deck's light is a LAMP above the pad, not the sun, so a world may set skyEl:
    // the glow sits on the deck light's azimuth at that elevation (below the horizon at night).
    const a = s.az * Math.PI / 180, e = (o.skyEl != null ? o.skyEl : s.el) * Math.PI / 180;
    return new THREE.Vector3(Math.sin(a) * Math.cos(e), Math.sin(e), Math.cos(a) * Math.cos(e)).normalize();
  };

  /* ---- world presets ----------------------------------------------------------------------
   * Each is ONE coherent light: a sky, the fog that matches its horizon, an exposure, a tone
   * curve and the rig colours for TXT.deckRig. The deck's light supplies the direction, the
   * preset supplies everything the direction is lit WITH. Tune a copy, never these. */
  TXT.worlds = {
    /* A REAL SKY IS BLUE WITH THE COLOUR AT THE HORIZON. The first cut of these mixed an orange
     * horizon into a blue zenith and got mauve smog, because the midpoint of orange and blue is
     * grey. So the gradient is cool all the way round, `haze` is the thin band ON the horizon,
     * and the warmth arrives only where the sun is, through horizonGlow and glow. Measured on
     * the first proof render, 2026-09-24. Sky light (envIntensity, ambient) stays well under the
     * key, or the sun stops casting and the frame goes flat. */
    goldenHour: {  // the low Texas sun: long shadows, warm faces, a burning seam at the horizon
      el: [4, 14], zenith: 0x14386e, horizon: 0x9db6cf, haze: 0xe9c9a2, ground: 0x6b5a48,
      sun: 0xffb466, sunDisc: 26, glow: 1.4, horizonGlow: 1.1, span: 0.5,
      clouds: 0.28, stars: 0, fogDensity: 0.0048, exposure: 1.0, envIntensity: 0.42, tone: 'aces',
      ink: 'light',
      rig: { key: { color: 0xffc27e, i: 4.4, radius: 5 }, rim: { color: 0x9fc0ff, i: 0.7, pos: [-8, 5, -8] },
             fill: { color: 0x5b7bb8, i: 0.28, pos: [-4, 3, 9] }, ambient: { color: 0x3a4460, i: 0.10 } } },
    blueHour: {    // the sun just gone: an amber seam under a deep blue, lamps start to matter
      el: [-2, 3], skyEl: -3, zenith: 0x071634, horizon: 0x5f78a8, haze: 0xd79a78, ground: 0x2c2f3c,
      sun: 0xff9a66, sunDisc: 0, glow: 0.9, horizonGlow: 1.2, span: 0.55,
      clouds: 0.18, stars: 0.35, fogDensity: 0.006, exposure: 1.1, envIntensity: 0.55, tone: 'aces',
      ink: 'light',
      rig: { key: { color: 0xffa877, i: 1.1, radius: 10 }, rim: { color: 0x9ab8ff, i: 1.0, pos: [-8, 6, -8] },
             fill: { color: 0x4c62a0, i: 0.45, pos: [-4, 4, 9] }, ambient: { color: 0x2a3456, i: 0.18 } } },
    nightSodium: { // Texas at night: a black sky, the city glow on one horizon, sodium on the pad. el is the LAMP
      el: [20, 60], skyEl: -9, zenith: 0x02050c, horizon: 0x1d2536, haze: 0x6a4a34, ground: 0x1b1a1c,
      sun: 0xff9a4a, sunDisc: 0, glow: 0.5, horizonGlow: 0.9, span: 0.4,
      clouds: 0.0, stars: 0.8, fogDensity: 0.0065, exposure: 1.15, envIntensity: 0.35, tone: 'aces',
      ink: 'light',
      rig: { key: { color: 0xffb46a, i: 2.6, radius: 8 }, rim: { color: 0x6f8fd8, i: 0.8, pos: [-8, 6, -8] },
             fill: { color: 0x2c3a60, i: 0.25, pos: [-4, 4, 9] }, ambient: { color: 0x1c2233, i: 0.12 } } },
    highNoon: {    // bleached and hard: a white sky at the horizon, short black shadows
      el: [55, 78], zenith: 0x2a63b6, horizon: 0xcfdeeb, haze: 0xe8ecec, ground: 0xb8a88c,
      sun: 0xfff5e6, sunDisc: 28, glow: 0.8, horizonGlow: 0.15, span: 0.6,
      clouds: 0.22, stars: 0, fogDensity: 0.0028, exposure: 0.95, envIntensity: 0.6, tone: 'aces',
      ink: 'dark',
      rig: { key: { color: 0xfff5e6, i: 4.6, radius: 3 }, rim: { color: 0xcfe3ff, i: 0.4, pos: [-8, 5, -8] },
             fill: { color: 0x9db8d8, i: 0.3, pos: [-4, 3, 9] }, ambient: { color: 0x8894a6, i: 0.10 } } },
    overcast: {    // a lid of cloud: no disc, shadows gone soft, colour honest and quiet
      el: [35, 60], zenith: 0x6f7985, horizon: 0xc4c8ca, haze: 0xb8bcbd, ground: 0x7e7668,
      sun: 0xf2f0ea, sunDisc: 0, glow: 0.25, horizonGlow: 0.05, span: 0.6,
      clouds: 0.0, stars: 0, fogDensity: 0.006, exposure: 1.0, envIntensity: 1.0, tone: 'neutral',
      ink: 'dark',
      rig: { key: { color: 0xf2f0ea, i: 1.4, radius: 22 }, rim: { color: 0xdfe6ee, i: 0.4, pos: [-8, 5, -8] },
             fill: { color: 0xc9d0d8, i: 0.5, pos: [-4, 3, 9] }, ambient: { color: 0x9aa2ac, i: 0.3 } } },
    stormFront: {  // a West Texas squall line: a bruised sky, one shaft of low sun under it
      el: [6, 16], zenith: 0x17212c, horizon: 0x7d8a8c, haze: 0xd6b48a, ground: 0x4d4a40,
      sun: 0xffd29a, sunDisc: 0, glow: 1.0, horizonGlow: 1.0, span: 0.35,
      clouds: 0.85, stars: 0, fogDensity: 0.0065, exposure: 1.0, envIntensity: 0.45, tone: 'aces',
      ink: 'light',
      rig: { key: { color: 0xffd29a, i: 3.6, radius: 7 }, rim: { color: 0xa8b8c8, i: 0.5, pos: [-8, 5, -8] },
             fill: { color: 0x5a6878, i: 0.3, pos: [-4, 3, 9] }, ambient: { color: 0x3a4450, i: 0.14 } } },
  };

  /* ---- weathering: nothing in Texas is clean at the bottom ------------------------------
   * TXT.weather(R, { grime, height, mottle, skip }) patches every standard material in the
   * scene once: albedo darkens toward the ground over `height` metres (splash, dust, the dark
   * base every real object has), and a seeded world-space mottle breaks roughness and colour
   * so a painted panel stops reading as clay. Call after the objects are added, before the
   * snapshot. The ground, the sky and the scatter are skipped. Deterministic. */
  TXT.weather = function (R, o) {
    o = o || {};
    // softer since the first interior render: 0.45 read as stains on dark wood, 0.32 reads as use
    const grime = o.grime != null ? o.grime : 0.32, height = o.height || 0.9, mottle = o.mottle != null ? o.mottle : 0.18;
    const skip = new Set(o.skip || []);
    /* FROM EACH OBJECT'S OWN BASE (Codex, #353). Grime used to be measured from world y = 0, so a
     * crate on a 1.2 m dock had none at its foot and a ground below zero darkened everything.
     * Each top level object is measured for its base, and a material shared across two bases is
     * patched once per base, so the same paint on a dock and on a crate weathers at each foot. */
    const made = new Map();
    const isStd = (m) => m && m.isMeshStandardMaterial;
    function patch(mat, base, mot) {
      const k = mat.uuid + '|' + base.toFixed(3) + '|' + mot.toFixed(3);
      if (made.has(k)) return made.get(k);
      let m = mat;
      // A MATERIAL'S OWN SHADER HOOK RUNS FIRST. Kit models inject hair normals, wet noses and
      // one-sided foliage in onBeforeCompile, and replacing it here erased them in every
      // weathered frame. The hook is kept the first time a material is weathered.
      const own = mat.userData.txWeathered ? mat.userData.txOwnHook : mat.onBeforeCompile;
      const ownKeyFn = mat.userData.txWeathered ? mat.userData.txOwnKey : mat.customProgramCacheKey;
      if (mat.userData.txWeathered) {
        if (mat.userData.txBaseY === base && mat.userData.txMottle === mot) { made.set(k, mat); return mat; }
        m = mat.clone(); m.userData = Object.assign({}, m.userData, { txWeathered: false });
      }
      m.userData.txWeathered = true; m.userData.txBaseY = base; m.userData.txMottle = mot;
      m.userData.txOwnHook = own; m.userData.txOwnKey = ownKeyFn;
      m.customProgramCacheKey = () => ownKeyFn.call(m) + '|txw';
      m.onBeforeCompile = (sh, renderer) => {
        if (typeof own === 'function' && own !== THREE.Material.prototype.onBeforeCompile) own.call(m, sh, renderer);
        sh.uniforms.uGrime = { value: grime }; sh.uniforms.uGrimeH = { value: height };
        sh.uniforms.uMottle = { value: m.userData.txMottle }; sh.uniforms.uBaseY = { value: m.userData.txBaseY };
        sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vTxW;')
          .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvTxW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
        sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
          varying vec3 vTxW; uniform float uGrime, uGrimeH, uMottle, uBaseY;
          float txH(vec3 p) { p = fract(p * 0.3183 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
          float txN(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
            return mix(mix(mix(txH(i), txH(i + vec3(1,0,0)), f.x), mix(txH(i + vec3(0,1,0)), txH(i + vec3(1,1,0)), f.x), f.y),
                       mix(mix(txH(i + vec3(0,0,1)), txH(i + vec3(1,0,1)), f.x), mix(txH(i + vec3(0,1,1)), txH(i + vec3(1,1,1)), f.x), f.y), f.z); }`)
          .replace('#include <color_fragment>', `#include <color_fragment>
            float txm = txN(vTxW * 1.7) * 0.6 + txN(vTxW * 7.0) * 0.4;
            float txg = (1.0 - smoothstep(0.0, uGrimeH, vTxW.y - uBaseY)) * uGrime * (0.8 + 0.4 * txN(vTxW * vec3(3.0, 0.6, 3.0)));
            diffuseColor.rgb *= (1.0 - txg) * (1.0 - uMottle * 0.35 * (txm - 0.5));`)
          .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
            roughnessFactor = clamp(roughnessFactor + uMottle * 0.5 * (txN(vTxW * 2.3) - 0.5) + txg * 0.25, 0.04, 1.0);`);
      };
      m.needsUpdate = true;
      made.set(k, m);
      return m;
    }
    for (const root of R.scene.children.slice()) {
      if (skip.has(root) || root.userData.txGround || root.isLight || root.isInstancedMesh) continue;
      const box = new THREE.Box3().setFromObject(root);
      if (box.isEmpty()) continue;
      const base = box.min.y;
      /* LARGE SURFACES MOTTLE LESS (2026-09-24). No. 33's roof, a dark slab 20 m across, read as
       * blotchy contour bands under the same 0.6 m mottle a crate wears as use. The judges called
       * it posterized. So the mottle falls with the object's size: full on a thing a person could
       * lift, about a third on a building. */
      const sz = new THREE.Vector3(); box.getSize(sz);
      const span = Math.max(sz.x, sz.y, sz.z);
      const mot = mottle * (span > 12 ? 0.3 : span > 5 ? 0.55 : 1);
      root.traverse((m) => {
        if (!m.isMesh || m.isInstancedMesh || skip.has(m)) return;
        // GROUNDS ARE TAGGED, NEVER GUESSED. TXT.ground marks its plane. A rotated plane is not
        // terrain on that evidence alone (a tilted solar panel is a subject and weathers, Codex,
        // #353), so the only other plane skipped is one of ground size, 40 m or more both ways,
        // which is how a chassis-built pad is recognised. Anything else goes in `skip`.
        if (m.userData.txGround) return;
        const gp = m.geometry && m.geometry.type === 'PlaneGeometry' ? m.geometry.parameters : null;
        if (gp && gp.width >= 40 && gp.height >= 40) return;
        if (Array.isArray(m.material)) m.material = m.material.map(x => isStd(x) ? patch(x, base, mot) : x);
        else if (isStd(m.material)) m.material = patch(m.material, base, mot);
      });
    }
  };

  /* ---- the sky shader ------------------------------------------------------------------- */
  const SKY_VERT = `
    varying vec3 vDir;
    void main() {
      vDir = (modelMatrix * vec4(position, 0.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      gl_Position.z = gl_Position.w;               // at the far plane: behind everything
    }`;
  const SKY_FRAG = `
    varying vec3 vDir;
    uniform vec3 uZenith, uHorizon, uHaze, uGround, uSunDir, uSunColor;
    uniform float uSunDisc, uGlow, uHorizonGlow, uSpan, uClouds, uStars, uSeed, uEnv, uFogMatch, uCamY, uFogD, uFogNear, uFogFar, uFade;
    float h12(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031 + uSeed * 0.0001); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
    float h13(vec3 p) { p = fract(p * 0.1031 + uSeed * 0.0001); p += dot(p, p.zyx + 31.32); return fract((p.x + p.y) * p.z); }
    float vnoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(h12(i), h12(i + vec2(1.0, 0.0)), f.x), mix(h12(i + vec2(0.0, 1.0)), h12(i + vec2(1.0, 1.0)), f.x), f.y); }
    float fbm(vec2 p) { float s = 0.0, a = 0.5; for (int i = 0; i < 5; i++) { s += a * vnoise(p); p = p * 2.03 + 11.7; a *= 0.5; } return s; }
    // THE SKY ON THE HORIZON LINE, in the direction d. Exactly what main() paints at h = 0 without
    // the disc, so the dome below the line and the fogged ground (installSkyFog) both start from the
    // colour the sky actually has right above them. See installSkyFog for the seam this closes.
    vec3 horizonSky(vec3 d, vec3 sd) {
      vec2 dz = normalize(d.xz + vec2(1e-5)), sz = normalize(sd.xz + vec2(1e-5));
      float toward = 0.5 + 0.5 * dot(dz, sz);
      float cs = max(dot(vec3(dz.x, 0.0, dz.y), sd), 0.0);
      return mix(uHorizon, uHaze, 0.8) + uSunColor * uHorizonGlow * pow(toward, 3.0)
        + uSunColor * uGlow * (0.035 * pow(cs, 3.0) + 0.30 * pow(cs, 48.0) + 1.2 * pow(cs, 900.0));
    }
    void main() {
      vec3 d = normalize(vDir);
      vec3 sd = normalize(uSunDir);
      float h = d.y;
      float cs = dot(d, sd);
      vec2 dz = normalize(d.xz + vec2(1e-5)), sz = normalize(sd.xz + vec2(1e-5));
      float toward = 0.5 + 0.5 * dot(dz, sz);                     // 1 on the sun's side
      vec3 col = mix(uHorizon, uZenith, pow(clamp(h / uSpan, 0.0, 1.0), 0.6));
      col = mix(col, uHaze, exp(-max(h, 0.0) * 22.0) * 0.8);     // the haze band on the horizon
      col += uSunColor * uHorizonGlow * pow(toward, 3.0) * exp(-abs(h) * 7.0);
      col += uSunColor * uGlow * (0.035 * pow(max(cs, 0.0), 3.0) + 0.30 * pow(max(cs, 0.0), 48.0)
                                  + 1.2 * pow(max(cs, 0.0), 900.0));
      if (uSunDisc > 0.0) col += uSunColor * uSunDisc * smoothstep(0.99985, 0.99993, cs);
      if (uClouds > 0.0 && h > 0.0) {
        vec2 uv = d.xz / (h + 0.08);
        // SOFT EDGES AND LESS STREAK (2026-09-24): a 0.5 to 0.82 step over noise stretched 3 to 1
        // cut the clouds into contour bands that no. 33's judges read as a posterized sky.
        vec2 wq = uv * 0.4 + vec2(fbm(uv * 0.23 + 3.1), fbm(uv * 0.23 + 8.4)) * 1.6;
        float n = fbm(wq * vec2(0.8, 1.25) + uSeed * 0.013);
        float w = fbm(uv * 0.3 + 7.3);
        float c = smoothstep(0.38, 0.95, n * 0.75 + w * 0.45) * uClouds * smoothstep(0.0, 0.12, h);
        vec3 lit = mix(uHaze * 0.9, uSunColor * 1.2, pow(toward, 2.0) * 0.6 + 0.4 * pow(max(cs, 0.0), 8.0));
        col = mix(col, lit, c * 0.7);
      }
      if (uStars > 0.0 && h > 0.04 && uEnv < 0.5) {
        vec3 p = d * 420.0; vec3 cell = floor(p); vec3 f = fract(p) - 0.5;
        float r = h13(cell);
        if (r > 0.9965) col += vec3(smoothstep(0.22, 0.0, length(f)) * (0.35 + 0.65 * fract(r * 173.0)) * uStars * smoothstep(0.04, 0.3, h));
      }
      // Below the line: the IBL wants the ground's colour. The visible dome shows wherever the
      // ground plane stops, at its edge or at the far plane, and under a sky fog it stands in for
      // the ground that WOULD be there: at the distance a ray this far below the line meets flat
      // ground from the camera's height, fogged by the scene's own fog toward the horizon sky.
      // At the far plane that is fully fogged, which is what closes the band no. 34 frame 5 had
      // at its clip line (row 226). The old blend, still used without a sky fog, went toward
      // uGround by angle alone and drew that band.
      if (h < 0.0) {
        if (uEnv > 0.5) col = uGround;
        else if (uFogMatch > 0.5) {
          float dist = uCamY / max(-h, 1e-4);
          float f = uFogD > 0.0 ? 1.0 - exp(-uFogD * uFogD * dist * dist) : smoothstep(uFogNear, uFogFar, dist);
          // the same grazing fade TX_GROUND gives the plane, so both sides of its edge agree (Codex, #368)
          if (uFade > 0.0) f = max(f, 1.0 - smoothstep(0.0, uFade, -h));
          col = mix(uGround, horizonSky(d, sd), f);
        } else col = mix(uHaze, uGround, clamp(-h * 5.0, 0.0, 1.0));
      }
      gl_FragColor = vec4(col, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
      if (uEnv < 0.5) gl_FragColor.rgb += (h12(gl_FragCoord.xy) - 0.5) / 255.0;   // no banding
    }`;

  function skyMaterial(o, sunDir, forEnv) {
    const lin = (c) => new THREE.Color(c);
    const W = o;
    return new THREE.ShaderMaterial({
      uniforms: {
        uZenith: { value: lin(W.zenith) }, uHorizon: { value: lin(W.horizon) },
        uHaze: { value: lin(W.haze) }, uGround: { value: lin(W.ground).multiplyScalar(forEnv ? 0.55 : 1) },
        uSunDir: { value: sunDir.clone() }, uSunColor: { value: lin(W.sun) },
        uSunDisc: { value: (W.sunDisc || 0) * (forEnv ? 3.0 : 1.0) }, uGlow: { value: W.glow != null ? W.glow : 1 },
        uHorizonGlow: { value: W.horizonGlow || 0 }, uSpan: { value: W.span || 0.45 },
        uClouds: { value: W.clouds || 0 }, uStars: { value: W.stars || 0 },
        uSeed: { value: (W.seed || 20260924) % 9973 }, uEnv: { value: forEnv ? 1 : 0 }, uFogMatch: { value: 0 },
        uCamY: { value: 2 }, uFogD: { value: 0 }, uFogNear: { value: 0 }, uFogFar: { value: 1 },
        uFade: { value: W.horizonFade != null ? W.horizonFade : 0.025 },
      },
      vertexShader: SKY_VERT, fragmentShader: SKY_FRAG,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
  }

  /* THE FOG IS THE SKY, 2026-09-26. The ground used to meet the sky in a hard band that the judges
   * read as sea or as a slab seam on six frames of carousel no. 34, and named in every round of
   * no. 33 and no. 34. Two faults stacked, measured on no. 34 frame 8 at column 1080: the sky just
   * above the line was (191,189,212) and the first row of ground was (133,133,168), falling to 65
   * within 60 rows.
   *
   *   1. THE FOG WAS ONE FLAT COLOUR, `W.haze`, while the sky over it carries the horizon mix and
   *      the sun's glow, which change with direction. Fully fogged ground could only reach haze.
   *   2. THE FOG WAS NEVER TONE MAPPED. three.js mixes fog in AFTER tone mapping and colour space,
   *      so `fogColor` lands raw while the dome beside it is tone mapped at the frame's exposure.
   *      A frame that raised its exposure (no. 34 frame 8 ran it at +0.4) widened the gap.
   *
   * So when a frame stands under TXT.sky, every fogged material mixes toward the sky's own colour
   * on the horizon IN ITS VIEW DIRECTION, through the same tone curve and output transform the dome
   * uses, and the ground (TX_GROUND, set by TXT.ground) goes all the way to that colour as its view
   * ray grazes the line, over `horizonFade` radians (default 0.025, about 45 px at 2x and 40 deg).
   * Ground that meets the sky meets it at the sky's value, and the line is a gradient.
   *
   * The world's constants are baked into the chunks as literals, because a slide is one page, one
   * world and one render. A material compiled before TXT.sky keeps the old chunks, so call TXT.sky
   * before the first render, which every frame already does. `skyFog:false` in TXT.sky's options
   * keeps the flat fog, and so does `tintFog:false`. The IBL is untouched, so lighting is too. */
  function installSkyFog(W, sunDir) {
    const C = THREE.ShaderChunk;
    // THE PRISTINE CHUNKS LIVE ON THE SHARED ShaderChunk, not on this TXT: a second init(THREE) in
    // the same page would otherwise take the patched chunks as its base and declare everything
    // twice, and every fogged shader after it would fail to compile (Codex, #368).
    const base = C.__txFogBase || (C.__txFogBase = { pv: C.fog_pars_vertex, v: C.fog_vertex,
      pf: C.fog_pars_fragment, f: C.fog_fragment });
    const v3 = (c) => { const k = new THREE.Color(c); return 'vec3(' + [k.r, k.g, k.b].map(x => x.toFixed(6)).join(', ') + ')'; };
    const n = (x) => Number(x || 0).toFixed(6);
    const sd = sunDir.clone().normalize();
    const fade = W.horizonFade != null ? W.horizonFade : 0.025;
    C.fog_pars_vertex = base.pv + '\n#ifdef USE_FOG\n  varying vec3 vTxFogDir;\n#endif\n';
    // row vector times the view matrix is its inverse rotation: the ray from the eye, in world space
    C.fog_vertex = base.v + '\n#ifdef USE_FOG\n  vTxFogDir = (vec4(mvPosition.xyz, 0.0) * viewMatrix).xyz;\n#endif\n';
    C.fog_pars_fragment = base.pf + `
#ifdef USE_FOG
  #define TX_SKY_FOG 1
  varying vec3 vTxFogDir;
  vec3 txSkyFog() {
    vec3 d = normalize(vTxFogDir);
    vec3 sd = vec3(${n(sd.x)}, ${n(sd.y)}, ${n(sd.z)});
    vec2 dz = normalize(d.xz + vec2(1e-5)), sz = normalize(sd.xz + vec2(1e-5));
    float toward = 0.5 + 0.5 * dot(dz, sz);
    float cs = max(dot(vec3(dz.x, 0.0, dz.y), sd), 0.0);
    vec3 c = mix(${v3(W.horizon)}, ${v3(W.haze)}, 0.8) + ${v3(W.sun)} * ${n(W.horizonGlow)} * pow(toward, 3.0)
      + ${v3(W.sun)} * ${n(W.glow != null ? W.glow : 1)} * (0.035 * pow(cs, 3.0) + 0.30 * pow(cs, 48.0) + 1.2 * pow(cs, 900.0));
    #if defined( TONE_MAPPING )
      c = toneMapping(c);
    #endif
    return linearToOutputTexel(vec4(c, 1.0)).rgb;
  }
  float txGroundFade(float f) {
    #ifdef TX_GROUND
      return max(f, 1.0 - smoothstep(0.0, ${n(fade)}, -normalize(vTxFogDir).y));
    #else
      return f;
    #endif
  }
  // A hook that replaces fog_fragment with its own mix toward fogColor (the kit's aerial() haze on
  // far landforms and skylines) still lands on the sky's colour, and the uniform is left unread.
  #define fogColor txSkyFog()
#endif
`;
    C.fog_fragment = `
#ifdef USE_FOG
  #ifdef FOG_EXP2
    float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
  #else
    float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
  #endif
  fogFactor = txGroundFade(fogFactor);
  gl_FragColor.rgb = mix( gl_FragColor.rgb, txSkyFog(), fogFactor );
#endif
`;
  }
  // a ground plane fades into the horizon when the sky fog is installed (TXT.ground sets it)
  function markGround(mesh) {
    const m = mesh.material;
    m.defines = Object.assign({}, m.defines, { TX_GROUND: '' });
    m.needsUpdate = true;
    mesh.userData.txGround = true;
    return mesh;
  }

  /* ONE DECK, ONE WORLD, bound the way TXT.deckRig binds the light (2026-09-24, Codex on #353).
   * The chassis names the world ONCE in TXDECK.declare as `sky`: a preset name ('goldenHour') or
   * an object ({ preset:'goldenHour', haze:0xd8b48e }). TXT.deckWorld() returns it resolved, and
   * TXT.sky THROWS when a frame hands it a different world, so nine frames can't stand under two
   * skies. A deck that declares no sky may still pass a world to TXT.sky, as before. */
  const WORLD_KEYS = ['zenith', 'horizon', 'haze', 'ground', 'sun', 'sunDisc', 'glow', 'horizonGlow',
    'span', 'clouds', 'stars', 'fogDensity', 'exposure', 'envIntensity', 'tone', 'skyEl', 'seed', 'horizonFade'];
  const worldKey = (W) => JSON.stringify(WORLD_KEYS.map(k => (W[k] === undefined ? null : W[k])));
  function deckDeclared() {
    const TXD = (typeof window !== 'undefined') ? window.TXDECK : null;
    try { return !!(TXD && TXD.deck && TXD.deck()); } catch (e) { return false; }
  }
  function declaredWorld() {
    const TXD = (typeof window !== 'undefined') ? window.TXDECK : null;
    let D = null;
    try { if (TXD && TXD.deck) D = TXD.deck().sky; } catch (e) { D = null; }
    if (D == null) return null;
    const name = typeof D === 'string' ? D : (D.preset || 'goldenHour');
    if (!TXT.worlds[name]) throw new Error("TXDECK.declare sky names no world '" + name + "'. The worlds are " +
      Object.keys(TXT.worlds).join(', '));
    return typeof D === 'string' ? Object.assign({}, TXT.worlds[name]) : Object.assign({}, TXT.worlds[name], D);
  }
  TXT.deckWorld = function () {
    const D = declaredWorld();
    if (!D) throw new Error("TXT.deckWorld: the chassis declares no sky. Add sky:'goldenHour' (or another " +
      "TXT.worlds name) to its TXDECK.declare, once, for the whole deck");
    return D;
  };

  /* TXT.sky(R, world) — the dome, the IBL from it, and the fog in its horizon's hue.
   * world: omit it to use the chassis's declared sky, or pass TXT.deckWorld(). Without a
   * declaration, a TXT.worlds preset or a copy of one. Call once per frame, in any order
   * relative to TXT.frame (the dome follows the camera). Returns the dome. */
  TXT.sky = function (R, W, o) {
    const D = declaredWorld();
    if (D) {
      if (W && worldKey(Object.assign({}, TXT.worlds.goldenHour, W)) !== worldKey(D))
        throw new Error("TXT.sky: this frame asked for a world the chassis did not declare. One deck, one " +
          "world: call TXT.sky(R) or TXT.sky(R, TXT.deckWorld())");
      W = D;
    } else if (deckDeclared()) {
      // A DECK WITH NO DECLARED SKY is how five frames end up under five worlds (Codex, #353). A
      // standalone scene, with no TXDECK declaration at all, may still pass its own world.
      throw new Error("TXT.sky: this deck's chassis declares no sky. Add sky:'goldenHour' (or another " +
        "TXT.worlds name) to its TXDECK.declare, once, so every frame stands in one world");
    } else {
      W = Object.assign({}, TXT.worlds.goldenHour, W || {});
    }
    o = o || {};
    const sunDir = TXT.sunDir(W);
    const dome = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 48), skyMaterial(W, sunDir, false));
    const far = R.camera.far * 0.92;
    dome.scale.setScalar(far);
    dome.frustumCulled = false; dome.renderOrder = -1000; dome.userData.txSky = true;
    dome.onBeforeRender = function (r, s, cam) {
      dome.position.copy(cam.position); dome.updateMatrixWorld();
      // the dome's stand-in ground reads the fog as it is AT RENDER, since frames tune it after TXT.sky
      const U = dome.material.uniforms, F = s.fog;
      U.uCamY.value = Math.max(0.05, cam.position.y);
      U.uFogD.value = F && F.isFogExp2 ? F.density : 0;
      if (F && !F.isFogExp2) { U.uFogNear.value = F.near; U.uFogFar.value = F.far; }
    };
    dome.position.copy(R.camera.position);
    R.scene.add(dome);
    R.scene.background = null;
    // the IBL, rendered FROM THIS SKY, so every reflection belongs to the same world
    if (o.environment !== false) {
      const env = new THREE.Scene();
      const e = new THREE.Mesh(new THREE.SphereGeometry(40, 64, 32), skyMaterial(W, sunDir, true));
      env.add(e);
      const pm = new THREE.PMREMGenerator(R.renderer);
      const tex = pm.fromScene(env, 0.0, 0.1, 100).texture;
      R.scene.environment = tex;
      if ('environmentIntensity' in R.scene) R.scene.environmentIntensity = W.envIntensity != null ? W.envIntensity : 0.85;
      pm.dispose();
      e.geometry.dispose(); e.material.dispose();
    }
    // fog in the horizon's own hue (DESIGN_DOCTRINE 4): the ground dissolves into the sky
    if (R.scene.fog && o.tintFog !== false) {
      R.scene.fog.color = new THREE.Color(W.haze);
      if (o.skyFog !== false) { installSkyFog(W, sunDir); dome.material.uniforms.uFogMatch.value = 1; }
    }
    R.world = W;
    return dome;
  };

  /* ---- ground with tooth ---------------------------------------------------------------
   * TXT.ground(R, { surface:'caliche'|'dirt'|'asphalt'|'concrete'|'grass', tile:8, size:900,
   *                 color, seed, joints }) — a seeded, tileable surface map + roughness +
   * bump, and slow macro variation in vertex colour so the tile never shows. Without
   * `surface` the old flat plane is returned, unchanged. */
  const SURFACES = {
    caliche:  { base: 0xb3a58c, var: 0.16, speck: 0.10, speckTone: -0.28, rough: 0.92, bump: 0.6, streak: 0 },
    dirt:     { base: 0x8a5f43, var: 0.20, speck: 0.07, speckTone: -0.25, rough: 0.95, bump: 0.8, streak: 0 },
    asphalt:  { base: 0x3a3b3e, var: 0.10, speck: 0.22, speckTone: 0.35, rough: 0.78, bump: 0.45, streak: 0 },
    concrete: { base: 0x9d9a94, var: 0.08, speck: 0.05, speckTone: -0.18, rough: 0.86, bump: 0.25, streak: 0, joints: 4 },
    // grass read as brown dirt at golden hour (2026-09-24); now a green going to straw, and a lawn
    grass:    { base: 0x6d7a3c, var: 0.22, speck: 0.12, speckTone: 0.18, rough: 0.97, bump: 0.9, streak: 0.5 },
    lawn:     { base: 0x4f6b2c, var: 0.16, speck: 0.10, speckTone: 0.16, rough: 0.96, bump: 0.7, streak: 0.5 },
  };
  function surfaceTextures(o, renderer) {
    const S = Object.assign({}, SURFACES[o.surface] || SURFACES.caliche);
    const N = 1024, seed = o.seed || 20260924;
    // grass streaks along x with 90 cells across and 256 down, each one whole period, so it tiles
    const FX = S.streak ? 90 : 256;
    const nz = valueNoise(seed, 64), nz2 = valueNoise(seed + 17, FX, 256), R0 = TXT.rng(seed + 3);
    const base = new THREE.Color(o.color != null ? o.color : S.base);
    const cMap = document.createElement('canvas'); cMap.width = cMap.height = N;
    const cRgh = document.createElement('canvas'); cRgh.width = cRgh.height = N;
    const cBmp = document.createElement('canvas'); cBmp.width = cBmp.height = N;
    const xm = cMap.getContext('2d'), xr = cRgh.getContext('2d'), xb = cBmp.getContext('2d');
    const im = xm.createImageData(N, N), ir = xr.createImageData(N, N), ib = xb.createImageData(N, N);
    const bs = base.clone().convertLinearToSRGB();
    for (let y = 0; y < N; y++) {
      for (let x = 0; x < N; x++) {
        const u = x / N, v = y / N;
        const m = fbm(nz, u * 64, v * 64, 5);                 // mottling, tileable at 64
        const f = nz2(u * FX, v * 256);                       // fine tooth, one period each way
        let t = (m - 0.5) * 2 * S.var + (f - 0.5) * 0.10;
        const p = (y * N + x) * 4;
        let r = bs.r * (1 + t), g = bs.g * (1 + t), b = bs.b * (1 + t * 0.9);
        let bump = 0.5 + (m - 0.5) * 0.5 + (f - 0.5) * 0.5;
        if (R0() < S.speck * 0.06) {                          // aggregate: stones and grit
          const k = S.speckTone * (0.6 + 0.8 * R0());
          r += k * 0.5; g += k * 0.5; b += k * 0.5; bump += 0.35;
        }
        if (S.joints || o.joints) {                           // saw-cut joints in a slab
          const J = N / Math.max(1, Math.round(o.joints || S.joints));   // whole joints per tile
          const jx = Math.min(x % J, J - (x % J)), jy = Math.min(y % J, J - (y % J));
          if (jx < 1.6 || jy < 1.6) { r *= 0.62; g *= 0.62; b *= 0.62; bump -= 0.4; }
        }
        im.data[p] = 255 * Math.min(1, Math.max(0, r));
        im.data[p + 1] = 255 * Math.min(1, Math.max(0, g));
        im.data[p + 2] = 255 * Math.min(1, Math.max(0, b));
        im.data[p + 3] = 255;
        const rg = 255 * Math.min(1, Math.max(0, S.rough + (m - 0.5) * 0.18));
        ir.data[p] = ir.data[p + 1] = ir.data[p + 2] = rg; ir.data[p + 3] = 255;
        const bb = 255 * Math.min(1, Math.max(0, bump));
        ib.data[p] = ib.data[p + 1] = ib.data[p + 2] = bb; ib.data[p + 3] = 255;
      }
    }
    xm.putImageData(im, 0, 0); xr.putImageData(ir, 0, 0); xb.putImageData(ib, 0, 0);
    const aniso = renderer.capabilities.getMaxAnisotropy ? renderer.capabilities.getMaxAnisotropy() : 1;
    const mk = (c, srgb) => {
      const t = new THREE.CanvasTexture(c);
      t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = Math.min(16, aniso);
      t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
      return t;
    };
    return { map: mk(cMap, true), roughnessMap: mk(cRgh, false), bumpMap: mk(cBmp, false), S };
  }
  const _flatGround = TXT.ground;
  TXT.ground = function (R, o) {
    o = o || {};
    if (!o.surface) return markGround(_flatGround(R, o));
    const size = o.size || 900, tile = o.tile || 6;
    const T = surfaceTextures(o, R.renderer);
    [T.map, T.roughnessMap, T.bumpMap].forEach(t => t.repeat.set(size / tile, size / tile));
    const geo = new THREE.PlaneGeometry(size, size, 160, 160);
    // macro variation: slow, large patches in vertex colour, so the repeat never reads
    const nz = valueNoise((o.seed || 20260924) + 99, 32), pos = geo.attributes.position;
    const col = new Float32Array(pos.count * 3);
    for (let i = 0; i < pos.count; i++) {
      const k = 0.82 + 0.3 * fbm(nz, pos.getX(i) / 70 + 16, pos.getY(i) / 70 + 16, 4);
      col[i * 3] = k; col[i * 3 + 1] = k; col[i * 3 + 2] = k * 0.98;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const mat = new THREE.MeshStandardMaterial({
      map: T.map, roughnessMap: T.roughnessMap, bumpMap: T.bumpMap,
      bumpScale: o.bumpScale != null ? o.bumpScale : T.S.bump, roughness: 1, metalness: 0,
      vertexColors: true, envMapIntensity: o.envMapIntensity != null ? o.envMapIntensity : 0.6 });
    /* THE BUMP FADES WITH DISTANCE (2026-09-24). At a grazing angle the fine tooth aliases into
     * thin horizontal stripes, which no. 33's judges read as busy, streaked dirt behind the fence.
     * Relief belongs where a reader can see relief, so the bump fades out between about 18 and
     * 90 m from the camera and the colour map carries the distance. */
    mat.onBeforeCompile = (sh) => {
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <bumpmap_pars_fragment>',
          'float txBumpS;\n' + THREE.ShaderChunk.bumpmap_pars_fragment.split('bumpScale *').join('txBumpS *'))
        .replace('#include <normal_fragment_begin>',
          'txBumpS = bumpScale * (1.0 - smoothstep(18.0, 90.0, length(vViewPosition)));\n#include <normal_fragment_begin>');
    };
    const g = new THREE.Mesh(geo, mat);
    g.rotation.x = -Math.PI / 2; g.position.y = o.y || 0;
    g.receiveShadow = true; markGround(g); R.scene.add(g);
    return g;
  };

  /* ---- contact shadow: the dark core where a thing meets the ground ------------------------
   * A soft falloff sized to the object's own footprint and turned with it. Cast shadows say
   * where the light is. The contact shadow says the thing has WEIGHT, and without it every
   * render floats. Call after the object is positioned. */
  function blurredRectTexture(aspect, softness) {
    const N = 256, c = document.createElement('canvas'); c.width = c.height = N;
    const x = c.getContext('2d');
    const pad = N * (0.5 * softness / (1 + softness));
    x.filter = 'blur(' + Math.max(1, pad * 0.55).toFixed(1) + 'px)';
    x.fillStyle = 'rgba(0,0,0,1)';
    const r = Math.min(N - 2 * pad, (N - 2 * pad)) * 0.18;
    x.beginPath();
    if (x.roundRect) x.roundRect(pad, pad, N - 2 * pad, N - 2 * pad, r); else x.rect(pad, pad, N - 2 * pad, N - 2 * pad);
    x.fill();
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace;
    return t;
  }
  TXT.contact = function (R, obj, o) {
    o = o || {};
    // A GROUND IS NOT AN OBJECT STANDING ON ONE. Terrain, a creek bed or a shoreline (tagged
    // txGround, or publishing heightAt) would get a flat black plane the size of its whole
    // footprint. The kit's terrain said "never call TXT.contact" in prose; this makes it true.
    let ground = !!(obj.userData && obj.userData.heightAt);
    obj.traverse((c) => { if (c.userData && c.userData.txGround) ground = true; });
    if (ground) return [];
    const q = obj.quaternion.clone(), p = obj.position.clone();
    obj.quaternion.identity(); obj.position.set(0, 0, 0); obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj);
    obj.quaternion.copy(q); obj.position.copy(p); obj.updateMatrixWorld(true);
    const size = new THREE.Vector3(); box.getSize(size);
    const ctr = new THREE.Vector3(); box.getCenter(ctr);
    /* WHERE IT STANDS (Codex, #353, twice). The contact goes on the surface the object stands
     * on. A ground TXT.ground laid (tagged, at any height, a sunken yard at y = -2 included) that
     * passes through the object or lies within 25 cm under its base IS that surface: a model a few
     * centimetres up keeps its contact on the ground instead of growing a ring in the air, and one
     * sunk into its ground keeps it where it meets the ground instead of burying it. A base with
     * no such ground stands on a support, a dock, a slab or a desk, and the contact goes at the
     * base. With no tagged ground at all, y = 0 is the ground. `o.y` wins. */
    const wb = new THREE.Box3().setFromObject(obj);
    let y = o.y;
    if (y == null) {
      const grounds = [], v = new THREE.Vector3();
      R.scene.traverse((m) => { if (m.userData && m.userData.txGround) grounds.push(m.getWorldPosition(v).y); });
      if (!grounds.length) grounds.push(0);
      const under = grounds.filter((gy) => gy >= wb.min.y - 0.25 && gy < wb.max.y);
      y = under.length ? Math.max(...under) : wb.min.y;
    }
    y += 0.004;
    const layers = o.layers || [{ spread: 0.10, opacity: 0.62 }, { spread: 0.55, opacity: 0.30 }];
    const made = [];
    for (const L of layers) {
      const w = size.x * (1 + L.spread * 2) + 0.2, d = size.z * (1 + L.spread * 2) + 0.2;
      const tex = blurredRectTexture(w / d, L.spread + 0.25);
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d),
        new THREE.MeshBasicMaterial({ map: tex, color: 0x000000, transparent: true,
          opacity: (o.opacity != null ? o.opacity : 1) * L.opacity, depthWrite: false,
          polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
      m.rotation.x = -Math.PI / 2;
      const off = new THREE.Vector3(ctr.x, 0, ctr.z).applyQuaternion(q);
      m.position.set(p.x + off.x, y, p.z + off.z);
      m.rotation.z = new THREE.Euler().setFromQuaternion(q, 'YXZ').y;
      m.renderOrder = 1;
      R.scene.add(m); made.push(m);
    }
    return made;
  };

  /* ---- the room: an interior is a place too (2026-09-24) ---------------------------------
   * TXT.interior(R, { w:12, d:10, h:4.2, floor:'concrete', wall:0xb9b3a7, window:'left',
   *                   ceiling:false, light:0.55 })
   * A hearing room, an office or a desk is a real frame with no sky, and before this it had nothing
   * to stand in but a flat colour, which is the void the world was built to end. This builds a
   * floor with tooth, a back wall and two side walls (the camera side open), an optional ceiling,
   * a lit window on one wall, and the studio environment for the light a room holds. The walls
   * RECEIVE shadows and cast none, so the deck's key reads as light through the window. The room
   * is centred on x = 0, its back wall at z = -d/2. Put the subject inside it. print_ban counts a
   * frame that calls this, before its kept snapshot, as standing in a place. */
  TXT.interior = function (R, o) {
    o = o || {};
    const w = o.w || 12, d = o.d || 10, h = o.h || 4.2, t = 0.2;
    const room = new THREE.Group();
    TXT.ground(R, { surface: o.floor || 'concrete', size: Math.max(w, d) * 3, tile: o.tile || 3, joints: o.joints });
    const wall = new THREE.MeshStandardMaterial({ color: o.wall != null ? o.wall : 0xb9b3a7, roughness: 0.93, metalness: 0 });
    const skirt = new THREE.MeshStandardMaterial({ color: o.trim != null ? o.trim : 0x4a4640, roughness: 0.7, metalness: 0.05 });
    const back = TXT.roundedBox(w + t, h, t, 0.02, wall); back.position.set(0, h / 2, -d / 2);
    const left = TXT.roundedBox(t, h, d, 0.02, wall); left.position.set(-w / 2, h / 2, 0);
    const right = TXT.roundedBox(t, h, d, 0.02, wall); right.position.set(w / 2, h / 2, 0);
    room.add(back, left, right);
    const sb = TXT.roundedBox(w, 0.12, 0.03, 0.005, skirt); sb.position.set(0, 0.06, -d / 2 + t / 2 + 0.015); room.add(sb);
    if (o.ceiling) { const c = TXT.roundedBox(w + t, t, d, 0.02, wall); c.position.set(0, h + t / 2, 0); room.add(c); }
    if (o.window !== null) {
      const side = o.window || 'left', ww = o.windowW || Math.min(3.2, d * 0.4), wh = o.windowH || Math.min(2.2, h * 0.55);
      const pane = new THREE.Mesh(new THREE.PlaneGeometry(ww, wh),
        new THREE.MeshBasicMaterial({ color: o.windowColor != null ? o.windowColor : 0xfff0d6, toneMapped: true }));
      pane.material.color.multiplyScalar(o.windowI != null ? o.windowI : 2.2);
      const y = h * 0.55;
      if (side === 'back') pane.position.set(-w * 0.2, y, -d / 2 + t / 2 + 0.01);
      else { pane.rotation.y = side === 'left' ? Math.PI / 2 : -Math.PI / 2;
             pane.position.set((side === 'left' ? -1 : 1) * (w / 2 - t / 2 - 0.01), y, -d * 0.1); }
      room.add(pane);
    }
    room.traverse((m) => { if (m.isMesh) { m.castShadow = false; m.receiveShadow = true; } });
    R.scene.add(room);
    if (!R.world) TXT.environment(R, { intensity: o.light != null ? o.light : 0.55 });
    if (!R.scene.background) R.scene.background = new THREE.Color(o.wall != null ? o.wall : 0xb9b3a7).multiplyScalar(0.25);
    R.room = room;
    return room;
  };

  /* ---- rounded box: edges that catch a highlight -----------------------------------------
   * TXT.roundedBox(w, h, d, r, material, { segments }) — centred on the origin, y up. The
   * sphere-cube mapping: vertices banded into the r-wide edge zones, then pushed onto the arc. */
  TXT.roundedBox = function (w, h, d, r, mat, o) {
    o = o || {};
    const seg = o.segments || 4, N = 2 * seg + 1;
    r = Math.max(0.0005, Math.min(r, w / 2 - 1e-4, h / 2 - 1e-4, d / 2 - 1e-4));
    const g = new THREE.BoxGeometry(1, 1, 1, N, N, N);
    const pos = g.attributes.position, nor = g.attributes.normal;
    const band = seg / N;
    const remap = (c, L) => {           // c in [-0.5, 0.5] on a uniform grid
      const lo = -0.5 + band, hi = 0.5 - band;
      if (c <= lo + 1e-9) return -L / 2 + ((c + 0.5) / band) * r;
      if (c >= hi - 1e-9) return L / 2 - ((0.5 - c) / band) * r;
      return (-L / 2 + r) + ((c - lo) / (hi - lo)) * (L - 2 * r);
    };
    const hx = w / 2 - r, hy = h / 2 - r, hz = d / 2 - r, v = new THREE.Vector3(), n = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.set(remap(pos.getX(i), w), remap(pos.getY(i), h), remap(pos.getZ(i), d));
      const ix = Math.max(-hx, Math.min(hx, v.x)), iy = Math.max(-hy, Math.min(hy, v.y)), iz = Math.max(-hz, Math.min(hz, v.z));
      n.set(v.x - ix, v.y - iy, v.z - iz);
      if (n.lengthSq() < 1e-12) n.set(nor.getX(i), nor.getY(i), nor.getZ(i));
      n.normalize();
      pos.setXYZ(i, ix + n.x * r, iy + n.y * r, iz + n.z * r);
      nor.setXYZ(i, n.x, n.y, n.z);
    }
    pos.needsUpdate = true; nor.needsUpdate = true;
    g.computeBoundingBox(); g.computeBoundingSphere();
    return mat ? new THREE.Mesh(g, mat) : g;
  };

  /* ---- scatter: the landscape a pad sits in ----------------------------------------------
   * TXT.scatter(R, { kind:'grass'|'scrub'|'rock', count, area:[x0,z0,x1,z1], avoid:[[x0,z0,x1,z1]],
   *                  seed, scale:[min,max], colors:[hex...] }) — one InstancedMesh, seeded.
   * Grass is dry Texas bunchgrass, scrub is mesquite and creosote height, rock is caliche
   * cobble. It never goes inside an `avoid` rectangle, so a pad stays a pad. */
  function tuftGeometry(rng, blades) {
    const P = [], C = [];
    for (let b = 0; b < blades; b++) {
      const a = rng() * Math.PI * 2, lean = 0.15 + rng() * 0.45, h = 0.22 + rng() * 0.32, w = 0.012 + rng() * 0.012;
      const bx = Math.cos(a) * 0.05 * rng(), bz = Math.sin(a) * 0.05 * rng();
      const tx = bx + Math.cos(a) * lean * h, tz = bz + Math.sin(a) * lean * h;
      const px = -Math.sin(a) * w, pz = Math.cos(a) * w;
      P.push(bx - px, 0, bz - pz, bx + px, 0, bz + pz, tx, h, tz);
      const k = 0.75 + rng() * 0.35;
      C.push(0.55 * k, 0.55 * k, 0.55 * k, 0.55 * k, 0.55 * k, 0.55 * k, k, k, k);  // darker at the root
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
    g.computeVertexNormals();
    return g;
  }
  function lumpGeometry(rng, detail, squash, rough) {
    const g = new THREE.IcosahedronGeometry(1, detail);
    const p = g.attributes.position, v = new THREE.Vector3();
    const nz = valueNoise(Math.floor(rng() * 1e6), 16);
    for (let i = 0; i < p.count; i++) {
      v.set(p.getX(i), p.getY(i), p.getZ(i));
      const k = 1 + (nz(v.x * 2 + 8, v.z * 2 + v.y + 8) - 0.5) * rough;
      v.multiplyScalar(k); v.y = v.y * squash + squash * 0.35;
      p.setXYZ(i, v.x, v.y, v.z);
    }
    return smoothNormals(g);
  }
  /* SMOOTH, NOT FACETED (Codex, #353). IcosahedronGeometry is non-indexed, so computeVertexNormals
   * gives every triangle its own flat normal and a stone reads as low poly whatever flatShading
   * says. The displacement is a function of position, so coincident corners stay coincident, and
   * their area-weighted face normals are averaged here. */
  function smoothNormals(g) {
    const p = g.attributes.position, n = p.count, acc = new Map(), key = new Array(n);
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), f = new THREE.Vector3();
    for (let i = 0; i < n; i++) key[i] = Math.round(p.getX(i) * 1e4) + ',' + Math.round(p.getY(i) * 1e4) + ',' + Math.round(p.getZ(i) * 1e4);
    for (let t = 0; t < n; t += 3) {
      a.fromBufferAttribute(p, t); b.fromBufferAttribute(p, t + 1); c.fromBufferAttribute(p, t + 2);
      f.subVectors(c, b).cross(a.clone().sub(b));             // area weighted face normal
      for (let j = 0; j < 3; j++) {
        const k = key[t + j], v = acc.get(k);
        if (v) v.add(f); else acc.set(k, f.clone());
      }
    }
    const nor = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const v = acc.get(key[i]).clone().normalize();
      nor[i * 3] = v.x; nor[i * 3 + 1] = v.y; nor[i * 3 + 2] = v.z;
    }
    g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    return g;
  }
  TXT.scatter = function (R, o) {
    o = o || {};
    const kind = o.kind || 'grass', rng = TXT.rng(o.seed || 20260924);
    const area = o.area || [-40, -60, 40, 20], avoid = o.avoid || [], count = o.count || 1500;
    let geo, mat, sc, cols, cast;
    if (kind === 'grass') {
      geo = tuftGeometry(rng, o.blades || 9); sc = o.scale || [0.55, 1.15]; cast = false;
      cols = o.colors || [0xb9a86a, 0xa39a5e, 0x8f8a52, 0xc4b27a, 0x7e7a48];
      mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, side: THREE.DoubleSide });
    } else if (kind === 'scrub') {
      geo = lumpGeometry(rng, 2, 0.62, 0.55); sc = o.scale || [0.35, 1.1]; cast = true;
      cols = o.colors || [0x5f6440, 0x6d6c45, 0x545a3a, 0x77734b];
      mat = new THREE.MeshStandardMaterial({ roughness: 0.92, flatShading: false });
    } else {
      geo = lumpGeometry(rng, 2, 0.5, 0.6); sc = o.scale || [0.03, 0.15]; cast = true;
      cols = o.colors || [0xa89c86, 0x8f8676, 0xb8ad98, 0x7d766a];
      mat = new THREE.MeshStandardMaterial({ roughness: 0.88 });   // smooth: a faceted stone reads as low poly
    }
    const mesh = new THREE.InstancedMesh(geo, mat, count);
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), t = new THREE.Vector3();
    const up = new THREE.Vector3(0, 1, 0), color = new THREE.Color();
    let placed = 0, tries = 0;
    const clump = valueNoise((o.seed || 20260924) + 5, 32);
    /* SPEND THE COUNT WHERE THE CAMERA IS. A uniform scatter over a field puts almost every
     * tuft where it is three pixels tall and leaves the foreground bare, which is what the first
     * proof render showed. Density falls off as (near / distance)^1.5 from the camera. */
    const cam = o.near !== false ? R.camera.position : null, r0 = o.nearRadius || 14;
    while (placed < count && tries < count * 40) {
      tries++;
      const x = area[0] + rng() * (area[2] - area[0]), z = area[1] + rng() * (area[3] - area[1]);
      if (avoid.some(a => x > a[0] && x < a[2] && z > a[1] && z < a[3])) continue;
      if (cam) { const dd = Math.hypot(x - cam.x, z - cam.z); if (rng() > Math.min(1, Math.pow(r0 / Math.max(dd, 0.5), 1.5))) continue; }
      if (clump(x / 9 + 50, z / 9 + 50) < (o.clumping != null ? o.clumping : 0.35) * rng()) continue;
      const k = sc[0] + (sc[1] - sc[0]) * Math.pow(rng(), 1.6);
      q.setFromAxisAngle(up, rng() * Math.PI * 2);
      s.set(k * (0.8 + 0.4 * rng()), k * (0.7 + 0.6 * rng()), k * (0.8 + 0.4 * rng()));
      t.set(x, o.y || 0, z);
      m4.compose(t, q, s); mesh.setMatrixAt(placed, m4);
      color.set(cols[Math.floor(rng() * cols.length)]).multiplyScalar(0.85 + 0.3 * rng());
      mesh.setColorAt(placed, color);
      placed++;
    }
    mesh.count = placed;
    mesh.castShadow = cast; mesh.receiveShadow = true;
    mesh.instanceMatrix.needsUpdate = true; if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    R.scene.add(mesh);
    return mesh;
  };

  return TXT;
}
