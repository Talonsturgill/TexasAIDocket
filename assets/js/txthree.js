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
     * rig's radius was dead for two months and every cast shadow shipped hard edged. VSM honoured
     * radius and blurSamples, and was the default until 2026-10-03.
     *
     * VSM BLED LIGHT INTO ITS SHADOWS, and the judges named it on every round of no. 41 (2026-10-03).
     * Frame 8's load face in the van wall's shadow carried a lit, fibrous sawtooth that survived a
     * 4096 map, a 7 m frustum and normalBias 0.08, and the run read it as z-fighting. Measured on
     * the frame: it goes with shadows off and with PCF, and stays with the liner hidden and with
     * the carton texture gone. A variance shadow map stores the mean and spread of depth, and where
     * a wall seen edge on from a low sun puts a wide spread of depths under one texel, Chebyshev's
     * bound lets light through. Frames 4 and 6 were the other half of the same complaint, "hard
     * rectangular casts": VSM blurs every shadow by one radius, so a truck's shadow 20 m long is as
     * sharp at its tip as at the tyres. So the default is now PCSS (installPcss below): the sun's
     * shadow is sharp where a thing touches the ground and widens with the distance from what
     * casts it, as a real sun's does, with no variance to bleed. `shadows:'vsm'` and
     * `shadows:'pcfsoft'` restore the old modes. */
    const mode = opts.shadows === 'vsm' || opts.shadows === 'pcfsoft' ? opts.shadows : 'pcss';
    renderer.shadowMap.type = mode === 'vsm' ? THREE.VSMShadowMap : mode === 'pcfsoft' ? THREE.PCFSoftShadowMap : THREE.PCFShadowMap;
    if (mode === 'pcss') installPcss();
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

  /* ---- PCSS: a sun's shadow, sharp at the foot and soft at the tip (2026-10-03) -------------
   * Patches three's PCF branch of getShadow, once per page and from the pristine chunk (the shared
   * ShaderChunk, as installSkyFog does, so a second init(THREE) never patches a patched chunk).
   *
   *   1. a blocker search: 12 taps on a golden angle disc, turned per pixel, find the mean depth of
   *      what stands between this point and the sun;
   *   2. the penumbra is that difference in depth times K, the light's own texels of penumbra per
   *      unit of depth, which pcssLight publishes through shadow.radius as a negative number;
   *   3. 24 taps of percentage closer filtering over that penumbra.
   *
   * IT HAS TO FIT INSIDE A RENDER BUDGET. 09-29's frame 1, a thousand pebbles and a field of
   * generators, is the heaviest frame on record. Timed in its own page (renders after the first,
   * which compiles), the first cut, a 24 texel search with 16 and 32 taps, drew 4.8 s slower than
   * VSM's 22.5 s, because every pixel within 24 texels of a pebble's shadow took the whole path. The
   * search now stops at 10 texels and the penumbra at the search (so a pixel the first five taps
   * call lit can't sit inside one), with 12 and 24 taps, and that frame draws about 3 s slower than
   * VSM, inside render.py's one 75 s budget.
   *
   * RECEIVER PLANE DEPTH BIAS. A low sun grazes the ground, and a tap 20 texels away on the
   * ground's own plane is metres deeper in the map, so a flat bias either lets the ground shadow
   * itself or lifts every contact off it. Each tap instead compares against the receiver's own
   * plane, its slope in the map taken from screen derivatives, which is exact on a plane.
   * A light with a radius of zero or more (one a frame made itself, a lamp's spot) is filtered at
   * that fixed radius with the same disc, so it can't bleed either. */
  function installPcss() {
    const C = THREE.ShaderChunk;
    const base = C.__txShadowBase || (C.__txShadowBase = C.shadowmap_pars_fragment);
    const at = base.indexOf('float getShadow(');
    const top = base.indexOf('shadowCoord.z += shadowBias;', at);
    const i0 = base.indexOf('#if defined( SHADOWMAP_TYPE_PCF )', at);
    const i1 = base.indexOf('#elif defined( SHADOWMAP_TYPE_PCF_SOFT )', i0);
    // a three.js whose chunk reads differently keeps its own PCF rather than a half patched one
    if (at < 0 || top < 0 || i0 < 0 || i1 < 0 || !(top < i0)) { C.shadowmap_pars_fragment = base; return; }
    const head = 'shadowCoord.z += shadowBias;\n\t\t#if defined( SHADOWMAP_TYPE_PCF )\n\t\t\tvec3 txDx = dFdx( shadowCoord.xyz ), txDy = dFdy( shadowCoord.xyz );\n\t\t#endif';
    /* THE DISCS ARE CONSTANTS, TURNED ONCE A PIXEL. Each tap used to take its own sine and cosine,
     * 82 of them at an edge and 10 on every lit pixel for the five tap test, and SwiftShader works a
     * sine out in software. Now a pixel takes one, and a tap is a rotation of a constant. */
    const disc = (n) => Array.from({ length: n }, (_, i) => {
      const a = i * 2.3999632, r = Math.sqrt((i + 0.5) / n);
      return `vec2( ${(Math.cos(a) * r).toFixed(6)}, ${(Math.sin(a) * r).toFixed(6)} )`;
    }).join(', ');
    const lib = `#if defined( SHADOWMAP_TYPE_PCF )
	const vec2 TX_B12[ 12 ] = vec2[]( ${disc(12)} );
	const vec2 TX_P24[ 24 ] = vec2[]( ${disc(24)} );
	float txBlk( sampler2D m, vec4 c, vec2 rp, vec2 o ) {
		return step( unpackRGBAToDepth( texture2D( m, c.xy + o ) ), c.z + clamp( dot( rp, o ), - 0.01, 0.01 ) - 0.00015 );
	}
	#endif
	`;
    const pcss = `#if defined( SHADOWMAP_TYPE_PCF )
			vec2 txTexel = vec2( 1.0 ) / shadowMapSize;
			float txDet = txDx.x * txDy.y - txDx.y * txDy.x;
			vec2 txRp = abs( txDet ) > 1e-14 ? vec2( txDy.y * txDx.z - txDx.y * txDy.z, txDx.x * txDy.z - txDy.x * txDx.z ) / txDet : vec2( 0.0 );
			float txAng = 6.2831853 * fract( 52.9829189 * fract( dot( gl_FragCoord.xy, vec2( 0.06711056, 0.00583715 ) ) ) );
			vec2 txCS = vec2( cos( txAng ), sin( txAng ) );
			mat2 txRot = mat2( txCS.x, txCS.y, - txCS.y, txCS.x );
			// A MAGNIFIED MAP NEEDS A WIDER FLOOR. Where one shadow texel covers many pixels, a sharp
			// edge shows the map's stair steps, and contact hardening made every foot and kerb edge
			// sharp: 09-29's frame 1 drew a stepped dark hairline along its pad's kerb, where a texel
			// covers about eleven pixels. The narrowest filter grows from 1.5 texels to 3 as a texel
			// grows past three pixels, so an edge is never sharper than the map can draw.
			float txTpp = max( length( txDx.xy ), length( txDy.xy ) ) * shadowMapSize.x;
			float txMin = clamp( 0.35 / max( txTpp, 1e-4 ), 1.5, 3.0 );
			float txK = shadowRadius < 0.0 ? - shadowRadius : 0.0;
			float txR = max( shadowRadius, txMin );
			// THE SHADOW CAMERA'S EDGE IS NOT A SHADOW'S EDGE. A caster longer than the light's box (a
			// median barrier, a fence, a building's long wall) had its shadow cut off in a straight
			// line where the box ends, which is no. 41 frame 4's "hard rectangular cast" across the
			// lanes. Inside the last 8 percent of the box the shadow fades out instead.
			vec2 txEdge = min( shadowCoord.xy, 1.0 - shadowCoord.xy );
			float txFade = smoothstep( 0.0, 0.08, min( txEdge.x, txEdge.y ) );
			if ( txFade <= 0.0 ) return 1.0;
			if ( txK > 0.0 ) {
				float txSearch = clamp( shadowCoord.z * txK, max( 2.0, txMin ), 10.0 ), txSum = 0.0, txN = 0.0;
				// FIVE TAPS FIRST: the centre and four at the search radius. Nearly every pixel is either
				// in full sun or deep in a shadow, and leaves here, so only an edge pays for the full search.
				vec2 txQ = txCS * txSearch * txTexel, txQp = vec2( - txQ.y, txQ.x );
				float txPre = txBlk( shadowMap, shadowCoord, txRp, vec2( 0.0 ) ) + txBlk( shadowMap, shadowCoord, txRp, txQ )
					+ txBlk( shadowMap, shadowCoord, txRp, - txQ ) + txBlk( shadowMap, shadowCoord, txRp, txQp ) + txBlk( shadowMap, shadowCoord, txRp, - txQp );
				if ( txPre < 0.5 ) return 1.0;
				if ( txPre > 4.5 ) return mix( 1.0, 1.0 - txFade, shadowIntensity );
				vec2 txS = txSearch * txTexel;
				for ( int i = 0; i < 12; i ++ ) {
					vec2 o = ( txRot * TX_B12[ i ] ) * txS;
					float d = unpackRGBAToDepth( texture2D( shadowMap, shadowCoord.xy + o ) );
					if ( d < shadowCoord.z + clamp( dot( txRp, o ), - 0.01, 0.01 ) - 0.00015 ) { txSum += d; txN += 1.0; }
				}
				// the whole disc lit, or the whole disc behind something: no penumbra, nothing to filter
				if ( txN < 0.5 ) return 1.0;
				if ( txN > 11.5 ) return mix( 1.0, 1.0 - txFade, shadowIntensity );
				txR = clamp( ( shadowCoord.z - txSum / txN ) * txK, txMin, txSearch );
			}
			float txLit = 0.0;
			vec2 txP = txR * txTexel;
			for ( int i = 0; i < 24; i ++ ) {
				vec2 o = ( txRot * TX_P24[ i ] ) * txP;
				txLit += step( shadowCoord.z + clamp( dot( txRp, o ), - 0.01, 0.01 ) - 0.00005, unpackRGBAToDepth( texture2D( shadowMap, shadowCoord.xy + o ) ) );
			}
			shadow = mix( 1.0, txLit / 24.0, txFade );
		`;
    const out = base.slice(0, top) + head + base.slice(top + 'shadowCoord.z += shadowBias;'.length, i0) + pcss + base.slice(i1);
    C.shadowmap_pars_fragment = out.replace('float getShadow(', lib + 'float getShadow(');
  }
  /* A sun 0.45 degrees in effective radius at the rigs' nominal radius of 6 (the disc is 0.27, and
   * haze and a low sun spread it), scaled by the radius a rig or frame gives: 3 for a high noon
   * sun, 22 for overcast. The getter is read by three every render, so it follows a shadow camera
   * the frame resizes after the rig, and a frame that sets radius sets this softness. */
  const PCSS_SUN = 0.45 * Math.PI / 180;
  function pcssLight(light) {
    const sh = light.shadow;
    let soft = sh.radius;
    Object.defineProperty(sh, 'radius', {
      configurable: true,
      get() {
        const c = sh.camera, w = Math.max(1e-3, (c.right - c.left) / (c.zoom || 1));
        return -Math.max(1e-3, (c.far - c.near) * Math.tan(PCSS_SUN * soft / 6) * sh.mapSize.x / w);
      },
      set(v) { soft = v; },
    });
  }

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
    if (R.renderer.shadowMap.type === THREE.PCFShadowMap) pcssLight(key);
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

  // Drawn is what shows in the pixels: the object visible, and a material that puts colour down. A
  // zero-opacity or colour-masked material is still hit by a ray and shows nothing (Codex, PR 369).
  const shows = (mat) => !!mat && mat.visible !== false && mat.colorWrite !== false &&
    !(mat.transparent && !(mat.opacity > 0.001));
  const drawn = (m) => m.visible && (Array.isArray(m.material) ? m.material.some(shows) : shows(m.material));
  // Drawn through every parent up to this scene, which is what the renderer walks.
  const onStage = (o, scene) => { for (let q = o; q; q = q.parent) { if (!q.visible) return false; if (q === scene) return true; } return false; };
  // ...and on a layer this camera renders, which the renderer checks as well (Codex, PR 369).
  const inView = (m, cam) => drawn(m) && m.layers.test(cam.layers);
  // A HIT IS WHAT THE RENDERER DRAWS THERE (Codex, PR 369). Its own material slot has to show, so
  // a box with one opaque slot and five invisible ones is one face and not a wall, and no clipping
  // plane may cut the point away: the renderer's own, or the material's when local clipping is on.
  const slotOf = (h) => {
    const m = h.object.material;
    return Array.isArray(m) ? m[(h.face && h.face.materialIndex) || 0] : m;
  };
  const clippedAway = (p, mat, renderer) => {
    const g = renderer && renderer.clippingPlanes;
    if (g && g.length && g.some((pl) => pl.distanceToPoint(p) < 0)) return true;
    const l = renderer && renderer.localClippingEnabled && mat && mat.clippingPlanes;
    if (l && l.length) {
      const cut = l.map((pl) => pl.distanceToPoint(p) < 0);
      return mat.clipIntersection ? cut.every(Boolean) : cut.some(Boolean);
    }
    return false;
  };
  // A CUTOUT'S TEXEL DECIDES (Codex, PR 369). An alpha-tested or alpha-mapped material draws only
  // the texels that clear its alphaTest, and the kit builds leaf cards, perforated steel and mesh
  // panels that way, so a hit reads the texture at the hit's own uv: the map's alpha times the
  // alphaMap's green, times the opacity, as three.js shades it. Each texture is read back once per
  // version, so a canvas redrawn with needsUpdate between a preview and the kept snapshot is read
  // again, the way WebGL uploads it again (Codex, PR 369).
  //
  // A TEXEL IS WHAT THE SHADER SAMPLES, NOT THE NUMBER STORED (Codex, PR 369). The first reader
  // divided every stored value by 255. Measured on 2026-09-26 in Chromium through this three.js, a
  // plane at alphaTest 0.5 over a red clear colour:
  //   8-bit        the value over 255, from data or an image: alpha 128 draws and 127 doesn't
  //   half float   the half decoded: 0.6 draws and 0.4 doesn't, where the old reader saw 54 and 57
  //   float        the value itself
  //   16-bit, 32-bit and signed integer types never upload. three.js asks glTexStorage2D for an
  //                unsized format (GL_INVALID_ENUM), and the incomplete texture samples (0, 0, 0, 1)
  //                whatever the data holds, so such a map draws opaque black and such an alphaMap
  //                draws nothing, in RGBA, RG and red alike. Dividing by 65535 would be wrong too
  //   an RG texture samples (r, g, 0, 1) and a red one (r, 0, 0, 1), so a red alphaMap draws nothing
  //   premultiplyAlpha multiplies the colour channels by alpha on upload, for 8-bit, half, float
  //                and canvas sources alike
  //   an 8-bit RGBA texture in sRGB decodes its colour channels and never its alpha, so an sRGB
  //                alphaMap's green of 180 samples 0.46 and fails alphaTest 0.5 (the kit's
  //                chain-link fence is one)
  // Anything else, a packed type, a compressed texture or an array that doesn't match its type, is
  // left unread, and a cutout whose texel can't be read is no wall.
  const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const srgbTexture = (tex) => {
    const CM = THREE.ColorManagement;
    if (CM && typeof CM.getTransfer === 'function' && THREE.SRGBTransfer !== undefined)
      return CM.getTransfer(tex.colorSpace) === THREE.SRGBTransfer;
    return tex.colorSpace === THREE.SRGBColorSpace;
  };
  const UNLOADED = [THREE.UnsignedShortType, THREE.UnsignedIntType, THREE.ByteType, THREE.ShortType, THREE.IntType];
  // One image as the shader samples it, the green and the alpha of every texel, or null when it can't
  // be read. Decoded into a copy, so data changed in place without needsUpdate reads as the GPU still
  // shows it.
  const readImage = (tex, img) => {
    if (!img) return null;
    const w = img.width || img.videoWidth, h = img.height || img.videoHeight;
    const lanes = tex.format === THREE.RGBAFormat ? 4 : tex.format === THREE.RGFormat ? 2 : tex.format === THREE.RedFormat ? 1 : 0;
    if (!lanes || !(w > 0) || !(h > 0)) return null;
    const n = w * h, G = new Float32Array(n), A = new Float32Array(n);
    if (UNLOADED.includes(tex.type)) { A.fill(1); return { w, h, g: G, a: A }; }   // never uploaded
    let d, stride, lane;
    if (img.data) {
      const arr = img.data;
      const fits = (tex.type === THREE.UnsignedByteType && (arr instanceof Uint8Array || arr instanceof Uint8ClampedArray)) ||
        (tex.type === THREE.HalfFloatType && arr instanceof Uint16Array) || (tex.type === THREE.FloatType && arr instanceof Float32Array);
      if (!fits || arr.length < n * lanes) return null;
      d = arr; stride = lanes;
      lane = tex.type === THREE.HalfFloatType ? (v) => THREE.DataUtils.fromHalfFloat(v)
        : tex.type === THREE.FloatType ? (v) => v : (v) => v / 255;
    } else if (typeof document !== 'undefined' &&
               [THREE.UnsignedByteType, THREE.HalfFloatType, THREE.FloatType].includes(tex.type)) {
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(img, 0, 0);
      d = x.getImageData(0, 0, w, h).data; stride = 4; lane = (v) => v / 255;
    } else return null;
    const premul = !!tex.premultiplyAlpha && lanes === 4;
    const decode = lanes === 4 && tex.type === THREE.UnsignedByteType && srgbTexture(tex);
    for (let i = 0; i < n; i++) {
      const o = i * stride, a = lanes === 4 ? lane(d[o + 3]) : 1;
      let g = lanes >= 2 ? lane(d[o + 1]) : 0;
      if (premul) g *= a;
      G[i] = decode ? toLinear(g) : g; A[i] = a;
    }
    return { w, h, g: G, a: A };
  };
  // A MINIFIED TEXTURE IS READ AT ITS MIP LEVEL (Codex, PR 369). The GPU samples through the texture's
  // own filters, and a texture seen from far enough through a mip level. The kit's perforated steel,
  // 128 texels to 5 cm, averages there to an alpha of about 0.67 and clears its alphaTest everywhere,
  // so at 40 m it draws as a solid sheet while its base texels are a third holes. A hit is read at
  // the footprint it would have in this frame, counted in the texture's own texels through its
  // transform (see pixelSteps and footprintOf), and through the filters the GPU samples it with: the
  // texture's own, nearest or bilinear within a level and nearest or linear between levels, or with
  // anisotropy on, SwiftShader's (see footprintOf). The levels are the ones the
  // GPU holds: a chain the texture supplies in `mipmaps`, which three.js uploads in place of its
  // image (Codex, PR 369), or else one averaged in 2 by 2 blocks the way generateMipmap builds it. A
  // hit around the camera and out of the frame is read at the footprint it would have in view.
  const texels = new WeakMap();
  const levelsFor = (tex) => {
    let e = texels.get(tex);
    if (e && e.v === tex.version) return e;
    e = { v: tex.version, levels: null, supplied: false, built: false };
    try {
      if (!tex.isCompressedTexture && !tex.isRenderTargetTexture) {
        const mips = Array.isArray(tex.mipmaps) && tex.mipmaps.length ? tex.mipmaps : null;
        const got = (mips || [tex.image]).map((img) => readImage(tex, img));
        if (got.every(Boolean)) { e.levels = got; e.supplied = !!mips; }
      }
    } catch (err) { e.levels = null; }
    texels.set(tex, e);
    return e;
  };
  const builtLevels = (e) => {
    if (e.built) return e.levels;
    const out = [e.levels[0]];
    for (let p = out[0]; p.w > 1 || p.h > 1;) {
      const w = Math.max(1, p.w >> 1), h = Math.max(1, p.h >> 1);
      const q = { w, h, g: new Float32Array(w * h), a: new Float32Array(w * h) };
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        let sg = 0, sa = 0;
        for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
          const k = Math.min(p.h - 1, 2 * y + dy) * p.w + Math.min(p.w - 1, 2 * x + dx);
          sg += p.g[k]; sa += p.a[k];
        }
        q.g[y * w + x] = sg / 4; q.a[y * w + x] = sa / 4;
      }
      out.push(q); p = q;
    }
    e.levels = out; e.built = true;
    return out;
  };
  const wrapIndex = (i, n, mode) => {
    if (mode === THREE.RepeatWrapping) return ((i % n) + n) % n;
    if (mode === THREE.MirroredRepeatWrapping) { const m = ((i % (2 * n)) + 2 * n) % (2 * n); return m < n ? m : 2 * n - 1 - m; }
    return Math.min(n - 1, Math.max(0, i));
  };
  const fetchTexel = (L, x, y, tex) => {
    const k = wrapIndex(y, L.h, tex.wrapT) * L.w + wrapIndex(x, L.w, tex.wrapS);
    return [L.g[k], L.a[k]];
  };
  const sampleLevel = (L, q, linear, tex) => {
    if (!linear) return fetchTexel(L, Math.floor(q.x * L.w), Math.floor(q.y * L.h), tex);
    const x = q.x * L.w - 0.5, y = q.y * L.h - 0.5, x0 = Math.floor(x), y0 = Math.floor(y), fx = x - x0, fy = y - y0;
    const s00 = fetchTexel(L, x0, y0, tex), s10 = fetchTexel(L, x0 + 1, y0, tex);
    const s01 = fetchTexel(L, x0, y0 + 1, tex), s11 = fetchTexel(L, x0 + 1, y0 + 1, tex);
    const mix = (i) => (s00[i] * (1 - fx) + s10[i] * fx) * (1 - fy) + (s01[i] * (1 - fx) + s11[i] * fx) * fy;
    return [mix(0), mix(1)];
  };
  const stepUv = new THREE.Vector2();
  const filtered = (e, tex, uv, fp) => {
    const mipmapped = tex.minFilter !== THREE.NearestFilter && tex.minFilter !== THREE.LinearFilter;
    let levels = e.levels, top = 0;
    if (mipmapped && e.supplied) top = levels.length - 1;
    else if (mipmapped && tex.generateMipmaps !== false) { levels = builtLevels(e); top = levels.length - 1; }
    // each sample's coordinate through the texture's own transform and wrap, as the GPU takes it
    const at = (du, dv) => tex.transformUv(stepUv.set(uv.x + du, uv.y + dv));
    if (fp.aniso) {
      // WITH ANISOTROPY ON, SwiftShader filters every sample bilinearly in its level, blends the two
      // levels either side of the level, and averages fp.n samples spread evenly along the longer step
      // (SamplerCore::sampleAniso, its uvStart and uvWeight tables)
      const l = Math.min(Math.max(fp.lod, 0), top), k0 = Math.floor(l), k1 = Math.min(top, k0 + 1), fr = l - k0;
      const out = [0, 0];
      for (let i = 0; i < fp.n; i++) {
        const t = -(fp.n - 1) / (2 * fp.n) + i / fp.n, q = at(t * fp.du, t * fp.dv);
        const s0 = sampleLevel(levels[k0], q, true, tex), s1 = k1 === k0 ? s0 : sampleLevel(levels[k1], q, true, tex);
        out[0] += (s0[0] * (1 - fr) + s1[0] * fr) / fp.n;
        out[1] += (s0[1] * (1 - fr) + s1[1] * fr) / fp.n;
      }
      return out;
    }
    const q = at(0, 0), lod = fp.lod;
    const magnified = !(lod > 0), f = magnified ? tex.magFilter : tex.minFilter;
    const linear = f === THREE.LinearFilter || f === THREE.LinearMipmapNearestFilter || f === THREE.LinearMipmapLinearFilter;
    if (magnified || top === 0) return sampleLevel(levels[0], q, linear, tex);
    const l = Math.min(lod, top);
    if (f === THREE.NearestMipmapNearestFilter || f === THREE.LinearMipmapNearestFilter)
      return sampleLevel(levels[Math.min(top, Math.max(0, Math.ceil(l + 0.5) - 1))], q, linear, tex);
    const k0 = Math.floor(l), k1 = Math.min(top, k0 + 1), fr = l - k0;
    const s0 = sampleLevel(levels[k0], q, linear, tex), s1 = sampleLevel(levels[k1], q, linear, tex);
    return [s0[0] * (1 - fr) + s1[0] * fr, s0[1] * (1 - fr) + s1[1] * fr];
  };
  // the anisotropy three.js sets on the texture: only for a trilinear minification, never under a
  // nearest magnification, and never past what the context supports
  const anisotropyOf = (tex, R) => {
    if (!(tex.anisotropy > 1) || tex.magFilter === THREE.NearestFilter) return 1;
    if (tex.minFilter !== THREE.NearestMipmapLinearFilter && tex.minFilter !== THREE.LinearMipmapLinearFilter) return 1;
    const caps = R.renderer && R.renderer.capabilities;
    const cap = caps && typeof caps.getMaxAnisotropy === 'function' ? caps.getMaxAnisotropy() : 1;
    return Math.max(1, Math.min(tex.anisotropy, cap || 1));
  };
  const lodM = new THREE.Matrix4(), lodI = new THREE.Matrix4(), lodA = new THREE.Vector3(), lodB = new THREE.Vector3();
  const lodC = new THREE.Vector3(), lodN = new THREE.Vector3(), lodE = new THREE.Vector3(), lodD = new THREE.Vector3();
  const lodUa = new THREE.Vector2(), lodUb = new THREE.Vector2(), lodUc = new THREE.Vector2(), lodS = new THREE.Vector2();
  // The triangle a hit lies on, in the world, and the footprint one pixel of this frame has there:
  // its span across and the cosine of the angle the view meets the surface at. `m` carries the
  // geometry's own frame into the world, through the instance's matrix when there is one.
  const footprintAt = (h, R) => {
    const cam = R.camera, obj = h.object, g = obj.geometry, f = h.face;
    if (!cam || !f || !g || !g.attributes || !g.attributes.position) return null;
    lodM.copy(obj.matrixWorld);
    if (obj.isInstancedMesh && h.instanceId != null) { obj.getMatrixAt(h.instanceId, lodI); lodM.multiply(lodI); }
    const P = g.attributes.position;
    lodA.fromBufferAttribute(P, f.a).applyMatrix4(lodM);
    lodB.fromBufferAttribute(P, f.b).applyMatrix4(lodM);
    lodC.fromBufferAttribute(P, f.c).applyMatrix4(lodM);
    lodN.subVectors(lodB, lodA).cross(lodE.subVectors(lodC, lodA));
    const world = lodN.length();
    const tall = (R.renderer && typeof R.renderer.getDrawingBufferSize === 'function')
      ? R.renderer.getDrawingBufferSize(lodS).y : 0;
    if (!(world > 1e-12) || !(tall > 0)) return null;
    lodE.setFromMatrixPosition(cam.matrixWorld);
    let across;
    if (cam.isOrthographicCamera) {
      across = (cam.top - cam.bottom) / (cam.zoom || 1) / tall;
      cam.getWorldDirection(lodD);
    } else {
      lodD.subVectors(h.point, lodE);
      const dist = lodD.length();
      if (!(dist > 0)) return null;
      lodD.divideScalar(dist);
      across = dist * 2 * Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2) / (cam.zoom || 1) / tall;
    }
    const cos = Math.max(Math.abs(lodD.dot(lodN.divideScalar(world))), 1e-3);
    return { across, cos, world, m: lodM.clone() };
  };
  // log2 of a square root the way SwiftShader takes it, off the float's own bits: exact at a power of
  // two and at most 0.022 of a level low between them (SamplerCore.cpp, log2sqrt)
  const log2sqrt = (L) => {
    const y = Math.fround(L * L);
    if (!(y > 0)) return -Infinity;
    if (!isFinite(y)) return Infinity;
    const e = Math.floor(Math.log2(y));
    return (e + y / Math.pow(2, e) - 1) / 4;
  };
  // THE LEVEL AND THE SAMPLES THE GPU TAKES (Codex, PR 374), from the step one pixel makes in the
  // geometry's uv, one pixel across (dxu, dxv) and one up (dyu, dyv), measured in texels through the
  // texture's own matrix. The level is read off the longer step. With anisotropy on, SwiftShader,
  // which renders every deck here, takes the footprint's stretch as the longer step squared over the
  // area the two steps span, caps it at the texture's anisotropy, lowers the level by it, and
  // averages that many samples, rounded, along the longer step (SamplerCore::computeLod2D). The
  // reference rule of EXT_texture_filter_anisotropic compared the two steps' lengths instead, and read
  // a footprint stretched along a diagonal of the screen as round.
  const footprintOf = (dxu, dxv, dyu, dyv, tex, R, L0) => {
    const e = tex.matrix.elements;
    const ax = (e[0] * dxu + e[3] * dxv) * L0.w, ay = (e[1] * dxu + e[4] * dxv) * L0.h;
    const bx = (e[0] * dyu + e[3] * dyv) * L0.w, by = (e[1] * dyu + e[4] * dyv) * L0.h;
    const px2 = ax * ax + ay * ay, py2 = bx * bx + by * by, major2 = Math.max(px2, py2);
    const cap = anisotropyOf(tex, R);
    if (cap <= 1) return { lod: log2sqrt(major2), n: 1 };
    const det = Math.abs(ax * by - ay * bx), a = Math.min(det > 0 ? major2 / det : Infinity, cap);
    const across = px2 >= py2;
    return { lod: log2sqrt(major2 / (a * a)), aniso: true, n: Math.max(1, Math.round(a)),
             du: across ? dxu : dyu, dv: across ? dxv : dyv };
  };
  // The geometry's coordinates on channel `ch` at barycentric `b` of face `f`.
  const uvBary = (g, f, b, ch, out) => {
    const a = g.attributes[ch ? 'uv' + ch : 'uv'];
    if (!a) return null;
    return out.set(a.getX(f.a) * b.x + a.getX(f.b) * b.y + a.getX(f.c) * b.z,
                   a.getY(f.a) * b.x + a.getY(f.b) * b.y + a.getY(f.c) * b.z);
  };
  // THE STEP A PIXEL MAKES ON THE SURFACE, AS THE GPU TAKES IT (Codex, PR 373). The GPU reads a
  // texture's level, and an alpha hash its cell, off how far a surface's coordinates move between
  // neighbouring pixels. So the step is taken the same way: where the rays one pixel across and one
  // pixel up from a hit meet the plane of the triangle it lies on, through the camera's own
  // projection, with the vertices where the renderer puts them, a morph or a skin included. The
  // barycentric coordinates of the hit and of those two points come back. Only inside the camera's
  // frustum, where every hit the sky and the room measure lies: the enclosure's rays up from the
  // camera meet things no pixel draws, and those keep the footprint at their distance.
  const stepTri = new THREE.Triangle(), stepQ = new THREE.Vector3(), stepO = new THREE.Vector3();
  const stepR = new THREE.Vector3(), stepN = new THREE.Vector3(), stepT = new THREE.Vector3();
  const stepB0 = new THREE.Vector3(), stepBx = new THREE.Vector3(), stepBy = new THREE.Vector3();
  const pixelSteps = (h, R) => {
    const cam = R.camera, o = h.object, f = h.face, g = o.geometry;
    if (!cam || !f || !g || !g.attributes || !g.attributes.position || typeof o.getVertexPosition !== 'function') return null;
    const buf = (R.renderer && typeof R.renderer.getDrawingBufferSize === 'function')
      ? R.renderer.getDrawingBufferSize(lodS) : null;
    if (!buf || !(buf.x > 0) || !(buf.y > 0)) return null;
    stepQ.copy(h.point).project(cam);
    const edge = 1 + 1e-6;                                                 // a ray on the frame's own edge
    if (!(Math.abs(stepQ.x) <= edge && Math.abs(stepQ.y) <= edge && Math.abs(stepQ.z) <= edge)) return null;
    lodM.copy(o.matrixWorld);
    if (o.isInstancedMesh && h.instanceId != null) { o.getMatrixAt(h.instanceId, lodI); lodM.multiply(lodI); }
    o.getVertexPosition(f.a, stepTri.a).applyMatrix4(lodM);
    o.getVertexPosition(f.b, stepTri.b).applyMatrix4(lodM);
    o.getVertexPosition(f.c, stepTri.c).applyMatrix4(lodM);
    stepTri.getNormal(stepN);
    if (!(stepN.lengthSq() > 0)) return null;
    const at = (dx, dy, bary) => {
      stepO.set(stepQ.x + dx, stepQ.y + dy, -1).unproject(cam);
      stepR.set(stepQ.x + dx, stepQ.y + dy, 1).unproject(cam).sub(stepO);
      const den = stepN.dot(stepR);
      if (!(Math.abs(den) > 1e-9 * stepR.length())) return null;          // a surface seen edge on
      const t = stepN.dot(stepT.subVectors(stepTri.a, stepO)) / den;
      return stepTri.getBarycoord(stepT.copy(stepR).multiplyScalar(t).add(stepO), bary);
    };
    if (!at(0, 0, stepB0) || !at(2 / buf.x, 0, stepBx) || !at(0, 2 / buf.y, stepBy)) return null;
    return { b0: stepB0, bx: stepBx, by: stepBy };
  };
  const lodOf = (h, R, tex, L0) => {
    if (h.object.isSprite) return spriteLod(h, R, tex, L0);
    const g = h.object.geometry, f = h.face, ch = tex.channel || 0;
    const s = pixelSteps(h, R);
    if (s) {
      const u0 = uvBary(g, f, s.b0, ch, lodUa), ux = uvBary(g, f, s.bx, ch, lodUb), uy = uvBary(g, f, s.by, ch, lodUc);
      if (!u0) return { lod: 0, n: 1 };
      return footprintOf(ux.x - u0.x, ux.y - u0.y, uy.x - u0.x, uy.y - u0.y, tex, R, L0);
    }
    // outside the frustum: one pixel's span at the hit's distance, over the texels the triangle holds
    const fp = footprintAt(h, R);
    const uvs = g.attributes[ch ? 'uv' + ch : 'uv'];
    if (!fp || !uvs) return { lod: 0, n: 1 };
    lodUa.fromBufferAttribute(uvs, f.a).applyMatrix3(tex.matrix);
    lodUb.fromBufferAttribute(uvs, f.b).applyMatrix3(tex.matrix);
    lodUc.fromBufferAttribute(uvs, f.c).applyMatrix3(tex.matrix);
    const texels = Math.abs((lodUb.x - lodUa.x) * (lodUc.y - lodUa.y) - (lodUc.x - lodUa.x) * (lodUb.y - lodUa.y)) * L0.w * L0.h;
    if (!(texels > 0)) return { lod: 0, n: 1 };
    const pMin = fp.across * Math.sqrt(texels / fp.world), pMax = pMin / fp.cos;   // texels per pixel
    const n = Math.max(1, Math.min(Math.ceil(pMax / Math.max(pMin, 1e-12)), anisotropyOf(tex, R)));
    return { lod: Math.log2(pMax / n), n: 1 };
  };
  // A SPRITE IS ONE CARD FACING THE CAMERA AT ITS CENTRE'S DEPTH (Codex, PR 373): three.js places
  // every corner of it at that depth, so a pixel steps the same distance across all of it. That step
  // is the drawing buffer's pixel at that depth, through the camera's own projection, turned back by
  // the sprite's rotation and over its size, where a sprite that doesn't attenuate is scaled by its
  // depth the way the shader scales it (Codex, PR 372).
  const spriteLod = (h, R, tex, L0) => {
    const cam = R.camera, o = h.object, mat = slotOf(h);
    const buf = (R.renderer && typeof R.renderer.getDrawingBufferSize === 'function')
      ? R.renderer.getDrawingBufferSize(lodS) : null;
    if (!cam || !buf || !(buf.x > 0) || !(buf.y > 0)) return { lod: 0, n: 1 };
    const P = cam.projectionMatrix.elements, persp = P[11] === -1;          // the shader's isPerspectiveMatrix
    const depth = -lodC.setFromMatrixPosition(o.matrixWorld).applyMatrix4(cam.matrixWorldInverse).z;
    if (persp && !(depth > 0)) return { lod: 0, n: 1 };
    const k = persp ? depth : 1, px = 2 * k / Math.abs(P[0] * buf.x), py = 2 * k / Math.abs(P[5] * buf.y);
    let sx = lodA.setFromMatrixColumn(o.matrixWorld, 0).length(), sy = lodA.setFromMatrixColumn(o.matrixWorld, 1).length();
    if (mat.sizeAttenuation === false && persp) { sx *= depth; sy *= depth; }
    if (!(sx > 0) || !(sy > 0)) return { lod: 0, n: 1 };
    const c = Math.cos(mat.rotation || 0), s = Math.sin(mat.rotation || 0);
    return footprintOf(c * px / sx, -s * px / sy, s * py / sx, c * py / sy, tex, R, L0);
  };
  const texelAt = (tex, uv, h, R) => {
    if (!tex || !uv) return null;
    const e = levelsFor(tex);
    if (!e.levels) return null;
    if (tex.matrixAutoUpdate) tex.updateMatrix();
    const s = filtered(e, tex, uv, h && R ? lodOf(h, R, tex, e.levels[0]) : { lod: 0, n: 1 });
    return { g: s[0], a: s[1] };
  };
  // THE UV CHANNEL THE MATERIAL SAMPLES (Codex, PR 369): a texture on channel 2 or 3 reads the
  // geometry's uv2 or uv3, interpolated at the hit, which the raycaster doesn't report.
  const uvOf = (h, tex) => {
    const ch = tex.channel || 0;
    if (ch === 0) return h.uv;
    if (ch === 1) return h.uv1;
    const g = h.object.geometry, attr = g && g.attributes && g.attributes['uv' + ch], f = h.face, b = h.barycoord;
    if (!attr || !f || !b) return undefined;
    return new THREE.Vector2(attr.getX(f.a) * b.x + attr.getX(f.b) * b.y + attr.getX(f.c) * b.z,
                             attr.getY(f.a) * b.x + attr.getY(f.b) * b.y + attr.getY(f.c) * b.z);
  };
  // The fragment's alpha as three.js computes it: opacity, times the map's alpha, times the alphaMap's
  // green, times the vertex alpha when the material reads RGBA vertex colours (Codex, PR 369: the
  // kit's waterSheet does), interpolated at the hit through its barycentric coordinates.
  const alphaAt = (h, mat, R) => {
    let a = mat.opacity != null ? mat.opacity : 1;
    if (mat.map) { const t = texelAt(mat.map, uvOf(h, mat.map), h, R); if (!t) return null; a *= t.a; }
    if (mat.alphaMap) { const t = texelAt(mat.alphaMap, uvOf(h, mat.alphaMap), h, R); if (!t) return null; a *= t.g; }
    const col = mat.vertexColors && h.object.geometry && h.object.geometry.attributes.color;
    if (col && col.itemSize === 4) {
      const f = h.face, b = h.barycoord;
      if (!f || !b) return null;
      a *= col.getW(f.a) * b.x + col.getW(f.b) * b.y + col.getW(f.c) * b.z;
    }
    return a;
  };
  // HOW LIKELY THE RENDERER DRAWS A HIT, 0 to 1. Its own material slot has to show, no clipping plane
  // may cut the point away, and a wireframe draws its edges and not the faces a ray meets (Codex, PR
  // 369). An opaque material draws every fragment. A cutout or a transparent one draws where its
  // alpha clears the alphaTest and shows at all. AN ALPHA-HASHED ONE DRAWS AT RANDOM (Codex, PR 369):
  // three.js discards a fragment whose alpha falls under a hashed threshold spread evenly from 0 to 1,
  // so a fraction of the fragments equal to the alpha draws, and a shell at 0.2 is a fifth drawn. A
  // measure counts such a hit by that chance, and a ray behind it by the rest.
  // How a hit draws, in two parts: `hash`, the chance it survives an alpha hash (1 without one), and
  // `blend`, the share of the pixel it then covers. null when it doesn't draw.
  const drawParts = (h, R) => {
    const mat = slotOf(h);
    if (!shows(mat) || clippedAway(h.point, mat, R.renderer) || mat.wireframe) return null;
    const hashed = !!mat.alphaHash;
    if (!(mat.alphaTest > 0 || mat.transparent || hashed)) return { hash: 1, blend: 1 };
    const a = alphaAt(h, mat, R);
    if (a === null) return null;                  // a cutout whose texel can't be read is no wall
    if (mat.alphaTest > 0 && a < mat.alphaTest) return null;
    const hash = hashed ? Math.min(1, Math.max(0, a)) : 1;
    if (!(hash > 0)) return null;
    // A BLENDED SURFACE COVERS WHAT IS BEHIND IT BY ITS ALPHA (Codex, PR 369): a shell at opacity 0.01
    // is drawn and is no wall. Normal blending lays it over what is behind at its alpha, and a blend
    // that adds to or multiplies what is behind covers none of it.
    if (!mat.transparent || mat.blending === THREE.NoBlending) return { hash, blend: 1 };
    if (mat.blending !== THREE.NormalBlending || !(a > 0.001)) return null;
    return { hash, blend: Math.min(1, a) };
  };
  // AN ALPHA HASH IS SHARED WHERE SURFACES COINCIDE (Codex, PR 369). three.js hashes the fragment's
  // position in the geometry's own frame, the raw position before a morph, a skin or an instance
  // moves it, over cells a twentieth of how far that position moves between neighbouring pixels
  // (ALPHA_HASH_SCALE 0.05) at two power-of-two scales. So hashed surfaces at the same local point,
  // stacked copies or instances with matching local coordinates, discard the same fragments: eight
  // coincident planes at 0.2 draw a fifth of the frame, not 83 percent. Hashed hits along a ray in
  // the same finer cell share one threshold, and the rest count as independent draws. Inside the
  // frustum the cell comes off the pixel's own step (Codex, PR 373), and outside it off the
  // footprint at the hit's distance.
  const lodL = new THREE.Vector3(), lodV = new THREE.Matrix4(), hashX = new THREE.Vector3(), hashY = new THREE.Vector3();
  const rawAt = (g, f, b, out) => {
    const P = g.attributes.position;
    return out.set(0, 0, 0).addScaledVector(lodA.fromBufferAttribute(P, f.a), b.x)
      .addScaledVector(lodA.fromBufferAttribute(P, f.b), b.y).addScaledVector(lodA.fromBufferAttribute(P, f.c), b.z);
  };
  const hashKey = (h, R) => {
    let reach;
    const s = pixelSteps(h, R);
    if (s) {
      const g = h.object.geometry, f = h.face;
      rawAt(g, f, s.b0, lodL);
      reach = Math.max(rawAt(g, f, s.bx, hashX).distanceTo(lodL), rawAt(g, f, s.by, hashY).distanceTo(lodL));
    } else {
      const fp = footprintAt(h, R);
      if (!fp) return null;
      reach = fp.across / fp.cos / (fp.m.getMaxScaleOnAxis() || 1);
      lodL.copy(h.point).applyMatrix4(lodV.copy(fp.m).invert());
    }
    if (!(reach > 0)) return null;
    const fine = Math.pow(2, Math.ceil(Math.log2(1 / (0.05 * reach))));
    return fine + ':' + Math.floor(fine * lodL.x) + ',' + Math.floor(fine * lodL.y) + ',' + Math.floor(fine * lodL.z);
  };
  // The layers a ray passes, nearest first, each with the share of the pixel it covers (or hides the
  // sky in): an opaque one ends the ray, and coincident hashed ones share one draw.
  //
  // A SHARED HASH STILL BLENDS EVERY SURVIVOR (Codex, PR 372). With the threshold t shared by a cell
  // and even on 0 to 1, every surface in it whose alpha clears t draws, and the blended ones lay over
  // one another. So with the surfaces sorted by that chance, t between the k-th chance and the next
  // draws the first k, and the layer covers the sum of each span times what those k blend to: two
  // coincident layers at 0.5 cover 0.375, where one merged draw at 0.25 undercounted them.
  const layersAlong = (hits, R, partsOf) => {
    const out = [], shared = new Map();
    for (const h of hits) {
      const d = partsOf(h, R);
      if (!d) continue;
      if (d.hash < 1) {
        const k = hashKey(h, R);
        if (k !== null) {
          let g = shared.get(k);
          if (!g) { g = { p: 0, h, members: [] }; shared.set(k, g); out.push(g); }
          g.members.push({ hash: d.hash, blend: d.blend, h });
          continue;
        }
        out.push({ p: d.hash * d.blend, h });
        continue;
      }
      out.push({ p: d.blend, h });
      if (d.blend >= 1) break;
    }
    for (const L of out) if (L.members) {
      const m = L.members.sort((x, y) => y.hash - x.hash);
      let p = 0, open = 1;
      for (let i = 0; i < m.length; i++) {
        open *= 1 - m[i].blend;
        p += (m[i].hash - (i + 1 < m.length ? m[i + 1].hash : 0)) * (1 - open);
      }
      L.p = p; L.h = m[0].h;
    }
    return out;
  };
  // Every mesh the camera could draw, the sky dome aside: the dome is the world, never a roof. With
  // `sprites`, the billboards too (Codex, PR 369): an opaque sprite across the frame hides the sky and
  // the room behind it, though no camera stands inside one, so enclosure leaves them out.
  const drawable = (R, sprites) => {
    const out = [];
    R.scene.traverseVisible((m) => {
      if ((m.isMesh || (sprites && m.isSprite)) && drawn(m) && !(m.userData && m.userData.txSky)) out.push(m);
    });
    return out;
  };
  /* INSIDE IS MEASURED AS A SHARE, NEVER AS ONE RAY (Codex, PR 369). A single ray straight up took
   * a street lamp for a roof, and a room counted as "looked into" from 300 m above it. The
   * showstopper test's question 3 accepts "a deliberate interior" as readily as a sky, so both
   * exemptions now ask how much of an interior there is. Measured on 2026-09-26 through
   * TXT.enclosure itself and the kit, as the share of the sky above the camera that the frame built
   * covers within 12 m:
   *
   *   interiors   the kit's semi_cab_interior at the driver's eye 0.96, a TXT.interior room with a
   *               ceiling 0.88, a closed shelter 1.0
   *   open        the kit gas station's canopy 0.65, a carport roof 0.59, a pecan's crown 0.23, a
   *               streetlight's head 0.02, a lamp 5 m up 0
   *
   * ENCLOSED_MIN sits in that gap, so a roof, a canopy or a tree over a camera looking down is still
   * a frame of the ground. TXT.interior builds no ceiling by default and scores 0.14 to 0.2 from
   * inside, so a room answers by what the frame shows instead: its walls, or its floor between
   * them, fill 0.88 to 1.0 of a frame taken in it or looking into its open side, and 0.003 of one
   * taken 300 m above it. ROOM_MIN is half the frame. Neither number is on TXT, so a frame can't
   * lower one. */
  const ENCLOSED_MIN = 0.8, ROOM_MIN = 0.5, HEMI_RAYS = 128;
  // The sky grid: 25 by 25 rays, and a frame shows its sky when at least one ray's worth reaches it.
  const SKY_GRID = 24, SKY_RAYS = (SKY_GRID + 1) * (SKY_GRID + 1);
  /* TXT.enclosure(R, reach) — the share of the sky above the camera that the frame built covers
   * within `reach` metres (12 by default): HEMI_RAYS rays spread evenly over the upper hemisphere by
   * solid angle, each asking whether it meets something the camera renders. That is a mesh drawn
   * and on its layers, a hit whose own material slot shows and no clipping plane cuts away, and a
   * distance inside the camera's own near and far, so geometry the far plane clips is no wall. A
   * mesh keeps its own visible flag under a hidden parent, and traverseVisible skips it. A chassis
   * that builds its own cab needs no flag to be measured. */
  TXT.enclosure = function (R, reach) {
    const cam = R.camera;
    R.scene.updateMatrixWorld();                 // a caller need not have rendered first
    cam.updateMatrixWorld();
    const eye = new THREE.Vector3().setFromMatrixPosition(cam.matrixWorld);
    const near = Math.max(0.05, cam.near || 0), far = Math.min(reach || 12, cam.far || Infinity);
    if (!(far > near)) return 0;
    const rc = new THREE.Raycaster(eye, new THREE.Vector3(0, 1, 0), near, far);
    rc.camera = cam;
    rc.layers.mask = cam.layers.mask;            // only what this camera renders can cover it
    const hit = drawable(R);
    if (!hit.length) return 0;
    const ga = Math.PI * (3 - Math.sqrt(5));
    let covered = 0;
    try {
      for (let i = 0; i < HEMI_RAYS; i++) {
        const y = (i + 0.5) / HEMI_RAYS, r = Math.sqrt(1 - y * y), th = i * ga;
        rc.ray.direction.set(r * Math.cos(th), y, r * Math.sin(th));
        let open = 1;                              // the chance nothing along this ray draws
        for (const L of layersAlong(rc.intersectObjects(hit, false), R, drawParts)) open *= 1 - L.p;
        covered += 1 - open;
      }
    } catch (e) { return 0; }
    return covered / HEMI_RAYS;
  };
  /* TXT.enclosed(R) — true when the camera stands inside something the frame built: at least
   * ENCLOSED_MIN of the sky above it is covered within `reach` metres. */
  TXT.enclosed = function (R, reach) { return TXT.enclosure(R, reach) >= ENCLOSED_MIN; };
  /* THE ORDER three.js DRAWS IN (Codex, PR 373). Which surface a pixel shows depends on the order
   * things are drawn in once a depth test is off, a surface blends, or a renderOrder moves it. So the
   * room share draws each ray's hits the way WebGLRenderer does, against a depth buffer:
   *
   *   - the opaque list, then the transmissive one, then the transparent one, a material with
   *     transmission going to the second and a transparent one to the third (WebGLRenderLists.push)
   *   - the opaque list by group order, renderOrder, material and nearest first, the other two by
   *     group order, renderOrder and farthest first, then by id (painterSortStable and
   *     reversePainterSortStable), each object's depth taken where the renderer takes it, at its
   *     bounding sphere's centre or a sprite's position, through the camera's projection; and with
   *     sortObjects off, in the order the scene is walked
   *   - a transparent material seen from both sides draws its back faces first, then its front ones
   *   - each hit passes or fails its own depth test, writes depth only when it tests and writes, since
   *     WebGL writes none with the test off, and lays its cover over what is there
   *
   * An alpha hash shares its threshold within a cell (Codex, PR 369), so the hashed hits in a cell
   * survive together, a higher chance whenever a lower one does, and every way a ray's cells can
   * survive is drawn and weighed by its chance: all of them up to HASH_WAYS, and HASH_WAYS fixed draws
   * of the thresholds past that. So a sprite with depthTest off behind a room's back wall paints over
   * the wall, a pane in front of the sprite blends back over it, an opaque backdrop drawn before the
   * walls is drawn over by them, and coincident hashed overlays survive as one. */
  const HASH_WAYS = 4096;
  const sortV = new THREE.Vector4(), sortM = new THREE.Matrix4(), ordM = new THREE.Matrix4(), ordI = new THREE.Matrix4();
  const ordD = new THREE.Vector3();
  const sortDepth = (o, cam) => {
    sortM.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
    if (o.isSprite) sortV.setFromMatrixPosition(o.matrixWorld);
    else {
      let bs = o.boundingSphere;
      if (bs === undefined) { if (o.geometry.boundingSphere === null) o.geometry.computeBoundingSphere(); bs = o.geometry.boundingSphere; }
      else if (bs === null) { o.computeBoundingSphere(); bs = o.boundingSphere; }
      sortV.set(bs.center.x, bs.center.y, bs.center.z, 1).applyMatrix4(o.matrixWorld);
    }
    return sortV.applyMatrix4(sortM).z;
  };
  const groupOrderOf = (o) => { for (let q = o.parent; q; q = q.parent) if (q.isGroup) return q.renderOrder; return 0; };
  // the geometry group a multi-material hit's face is drawn in, which the renderer draws as its own item
  const slotIndexOf = (h) => {
    const g = h.object.geometry, groups = g && g.groups;
    if (!Array.isArray(h.object.material) || !groups || !groups.length || h.faceIndex == null) return 0;
    const i = groups.findIndex((q) => h.faceIndex * 3 >= q.start && h.faceIndex * 3 < q.start + q.count);
    return i < 0 ? 0 : i;
  };
  // A back face as the GPU sees it: the renderer flips the front face for a mirrored object, and not
  // for a mirrored instance.
  const isBack = (h, dir) => {
    const o = h.object;
    if (!o.isMesh || !h.face) return false;
    ordM.copy(o.matrixWorld);
    let flip = false;
    if (o.isInstancedMesh && h.instanceId != null) { o.getMatrixAt(h.instanceId, ordI); ordM.multiply(ordI); flip = ordI.determinant() < 0; }
    const back = ordD.copy(dir).transformDirection(ordM.invert()).dot(h.face.normal) > 0;
    return back !== flip;
  };
  const depthPasses = (func, z, D) => {
    const eq = Math.abs(z - D) <= 1e-6 * Math.max(1, Math.abs(z));      // one surface, drawn twice
    switch (func) {
      case THREE.NeverDepth: return false;
      case THREE.AlwaysDepth: return true;
      case THREE.LessDepth: return z < D && !eq;
      case THREE.EqualDepth: return eq;
      case THREE.GreaterEqualDepth: return z > D || eq;
      case THREE.GreaterDepth: return z > D && !eq;
      case THREE.NotEqualDepth: return !eq;
      default: return z < D || eq;                                       // LessEqualDepth
    }
  };
  // One hit as the renderer draws it, or null when it draws nothing there. `mark` is what the
  // measure counts, 1 or 0, and `depth` the hit's own depth along the camera's view.
  const drawItem = (h, R, dir, depth, mark, zOf, walked, partsOf = drawParts) => {
    const d = partsOf(h, R);
    if (!d) return null;
    const o = h.object, mat = slotOf(h), test = mat.depthTest !== false;
    const twoSided = mat.transparent === true && mat.side === THREE.DoubleSide && mat.forceSinglePass === false;
    return {
      h, hash: d.hash, blend: d.blend, mark, depth, test, write: test && mat.depthWrite !== false,
      func: mat.depthFunc, list: mat.transmission > 0 ? 1 : mat.transparent === true ? 2 : 0,
      group: groupOrderOf(o), order: o.renderOrder, mat: mat.id, z: walked ? 0 : zOf(o), id: o.id,
      walk: walked ? walked.get(o) || 0 : 0, slot: slotIndexOf(h), side: twoSided && !isBack(h, dir) ? 1 : 0,
      inst: h.instanceId != null ? h.instanceId : 0, face: h.faceIndex || 0,
    };
  };
  const drawOrder = (sorted) => (a, b) => a.list - b.list ||
    (sorted ? (a.group - b.group || a.order - b.order ||
      (a.list === 0 ? a.mat - b.mat || a.z - b.z : b.z - a.z) || a.id - b.id) : a.walk - b.walk) ||
    a.slot - b.slot || a.side - b.side || a.inst - b.inst || a.face - b.face;
  // The share of a pixel that shows what `mark` counts, its items in draw order. The clear colour
  // counts nothing.
  const composite = (items, R) => {
    const cells = [], byKey = new Map();
    for (const it of items) {
      if (!(it.hash < 1)) continue;
      const k = hashKey(it.h, R);
      let c = k !== null ? byKey.get(k) : undefined;
      if (!c) { c = []; cells.push(c); if (k !== null) byKey.set(k, c); }
      c.push(it);
    }
    cells.forEach((c, ci) => { c.sort((x, y) => y.hash - x.hash); c.forEach((it, rank) => { it.cell = ci; it.rank = rank; }); });
    const kept = new Array(cells.length).fill(0);                    // how many of each cell survive
    const draw = () => {
      let shown = 0, D = Infinity;
      for (const it of items) {
        if (it.hash < 1 && it.rank >= kept[it.cell]) continue;       // discarded by its hash
        if (it.test && !depthPasses(it.func, it.depth, D)) continue;
        shown += (it.mark - shown) * it.blend;
        if (it.write) D = it.depth;
      }
      return shown;
    };
    let ways = 1;
    for (const c of cells) if ((ways *= c.length + 1) > HASH_WAYS) break;
    if (ways <= HASH_WAYS) {
      let sum = 0;
      const each = (ci, p) => {
        if (ci === cells.length) { sum += p * draw(); return; }
        const c = cells[ci];
        for (let k = 0; k <= c.length; k++) {
          // the threshold falls between the k-th chance and the next, so the first k survive
          const q = k === 0 ? 1 - c[0].hash : k === c.length ? c[k - 1].hash : c[k - 1].hash - c[k].hash;
          if (q > 0) { kept[ci] = k; each(ci + 1, p * q); }
        }
      };
      each(0, 1);
      return sum;
    }
    let seed = 0x2f6b1d35, sum = 0;
    const rand = () => {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    for (let n = 0; n < HASH_WAYS; n++) {
      cells.forEach((c, ci) => { const t = rand(); let k = 0; while (k < c.length && c[k].hash > t) k++; kept[ci] = k; });
      sum += draw();
    }
    return sum / HASH_WAYS;
  };
  /* TXT.roomShare(R) — the share of the frame the room TXT.interior built fills: a 17 by 17 grid of
   * rays through the camera's own projection, each drawing what it meets among the things the camera
   * draws, inside its near and far, in the renderer's own order (Codex, PR 373), and counting the
   * share of the pixel that ends up showing one of the room's walls or a point between them, its
   * floor or whatever stands on it (Codex, PR 369: the first cut counted a floor plane nobody had to
   * render). Only walls the camera renders count, on stage, drawn and on its layers, so a room taken
   * out of the scene, hidden, or on a layer the camera skips fills nothing. 0 when there is no room. */
  TXT.roomShare = function (R) {
    const room = R.room, cam = R.camera;
    if (!room || !room.isObject3D || !onStage(room, R.scene)) return 0;
    const walls = [];
    room.traverseVisible((m) => { if (m.isMesh && inView(m, cam)) walls.push(m); });
    if (!walls.length) return 0;                    // walls made invisible are no room
    R.scene.updateMatrixWorld();                   // a caller need not have rendered first
    cam.updateMatrixWorld();
    // THE ROOM'S OWN FOOTPRINT, IN ITS OWN AXES (Codex, PR 369). A room turned 45 degrees has a world
    // box far larger than its floor, and a camera over an empty corner of that box counted the ground
    // there as the room. So the walls are boxed, and every hit is tested, in the room's local frame.
    const toRoom = new THREE.Matrix4().copy(room.matrixWorld).invert(), rel = new THREE.Matrix4();
    const box = new THREE.Box3(), part = new THREE.Box3();
    walls.forEach((w) => {
      let bb = null;
      if (w.isInstancedMesh) { if (!w.boundingBox) w.computeBoundingBox(); bb = w.boundingBox; }
      else if (w.geometry) { if (!w.geometry.boundingBox) w.geometry.computeBoundingBox(); bb = w.geometry.boundingBox; }
      if (bb && !bb.isEmpty()) box.union(part.copy(bb).applyMatrix4(rel.multiplyMatrices(toRoom, w.matrixWorld)));
    });
    if (box.isEmpty()) return 0;
    const own = new Set(walls), all = drawable(R, true);
    const eye = new THREE.Vector3().setFromMatrixPosition(cam.matrixWorld);
    const fwd = new THREE.Vector3(); cam.getWorldDirection(fwd);
    const rc = new THREE.Raycaster(), v = new THREE.Vector2(), d = new THREE.Vector3();
    rc.layers.mask = cam.layers.mask; rc.camera = cam;           // a sprite is cast against the camera
    const lp = new THREE.Vector3();
    const inside = (p) => {
      lp.copy(p).applyMatrix4(toRoom);
      return lp.x >= box.min.x && lp.x <= box.max.x && lp.z >= box.min.z && lp.z <= box.max.z &&
        lp.y >= box.min.y - 0.05 && lp.y <= box.max.y + 0.05;
    };
    let walked = null;                                              // sortObjects off: the scene's own order
    if (R.renderer && R.renderer.sortObjects === false) { let k = 0; walked = new Map(); R.scene.traverse((o) => walked.set(o, k++)); }
    const zs = new Map(), zOf = (o) => { if (!zs.has(o)) zs.set(o, sortDepth(o, cam)); return zs.get(o); };
    const order = drawOrder(!walked);
    const N = 16;
    let seen = 0;
    for (let i = 0; i <= N; i++) for (let j = 0; j <= N; j++) {
      v.set(-1 + 2 * i / N, -1 + 2 * j / N);
      rc.setFromCamera(v, cam);
      // the share of this pixel that shows the room, its hits drawn in the renderer's own order
      try {
        const items = [];
        for (const h of rc.intersectObjects(all, false)) {
          const z = d.copy(h.point).sub(eye).dot(fwd);
          if (!(z >= cam.near && z <= cam.far)) continue;            // clipped at near and far: not drawn
          const it = drawItem(h, R, rc.ray.direction, z, own.has(h.object) || inside(h.point) ? 1 : 0, zOf, walked);
          if (it) items.push(it);
        }
        seen += composite(items.sort(order), R);
      } catch (e) { /* a ray that can't be measured shows no room */ }
    }
    return seen / ((N + 1) * (N + 1));
  };
  /* TXT.inRoom(R) — true when the room TXT.interior built fills at least ROOM_MIN of the frame, so
   * one the camera has left or sees from far away is no room shot (Codex, PR 369). */
  TXT.inRoom = function (R) { return TXT.roomShare(R) >= ROOM_MIN; };
  // THE SHARE OF A PIXEL A HIT HIDES THE SKY IN: what it draws there, where a pane at alpha 0.5 hides
  // half and lets half of the dome through, and none behind transmissive glass, which renders the sky
  // through itself, though it still writes its depth. An additive glow hides none of it.
  const skyParts = (h, R) => {
    const d = drawParts(h, R);
    return d && slotOf(h).transmission > 0 ? { hash: d.hash, blend: 0 } : d;
  };
  // Every hit along a ray, nearest first, as Raycaster.intersectObjects gives them, except that a
  // mesh a ray can't be cast against hides nothing rather than ending the measurement.
  const castAll = (rc, meshes) => {
    const out = [];
    for (const m of meshes) {
      if (!m.layers.test(rc.layers)) continue;
      try { m.raycast(rc, out); } catch (e) { /* hides nothing */ }
    }
    return out.sort((x, y) => x.distance - y.distance);
  };
  const skyShare = (camera, R, first) => {
    camera.updateMatrixWorld();
    const eye = new THREE.Vector3().setFromMatrixPosition(camera.matrixWorld);
    let c = eye, rad = 0.92 * camera.far, hits = null;
    if (R) {
      const dome = R._txDome;
      if (!dome || !onStage(dome, R.scene) || !inView(dome, camera)) return 0;
      R.scene.updateMatrixWorld();                 // a caller need not have rendered first
      c = new THREE.Vector3().setFromMatrixPosition(dome.matrixWorld);
      rad = dome.matrixWorld.getMaxScaleOnAxis();
      hits = drawable(R, true);
    }
    const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
    const o = new THREE.Vector3(), dir = new THREE.Vector3(), w = new THREE.Vector3(), q = new THREE.Vector3();
    const at = new THREE.Vector3(), rc = new THREE.Raycaster();
    rc.layers.mask = camera.layers.mask; rc.camera = camera;
    // each ray's hits are drawn in the renderer's own order (Codex, PR 373), the dome among them where
    // the renderer puts it, first by its renderOrder, and what the measure counts is the dome
    let walked = null, dome = null, order = null, zOf = null;
    if (hits && hits.length) {
      if (R.renderer && R.renderer.sortObjects === false) { let k = 0; walked = new Map(); R.scene.traverse((x) => walked.set(x, k++)); }
      const zs = new Map();
      zOf = (x) => { if (!zs.has(x)) zs.set(x, sortDepth(x, camera)); return zs.get(x); };
      order = drawOrder(!walked);
      const dm = R._txDome, mat = dm.material, test = mat.depthTest !== false;
      dome = { h: null, hash: 1, blend: 1, mark: 1, depth: 0, test, write: test && mat.depthWrite !== false,
        func: mat.depthFunc, list: mat.transmission > 0 ? 1 : mat.transparent === true ? 2 : 0,
        group: groupOrderOf(dm), order: dm.renderOrder, mat: mat.id, z: walked ? 0 : zOf(dm), id: dm.id,
        walk: walked ? walked.get(dm) || 0 : 0, slot: 0, side: 0, inst: 0, face: 0 };
    }
    const N = SKY_GRID, all = SKY_RAYS;
    let shown = 0;
    // from the top row down, so a frame with sky along its top answers on its first ray
    for (let j = N; j >= 0; j--) for (let i = 0; i <= N; i++) {
      const u = -1 + 2 * i / N, v = -1 + 2 * j / N;
      o.set(u, v, -1).unproject(camera);
      dir.set(u, v, 1).unproject(camera).sub(o).normalize();
      // the dome's far side is what it draws under this ray: where the ray leaves its sphere
      w.copy(o).sub(c);
      const b = w.dot(dir), disc = b * b - (w.lengthSq() - rad * rad);
      if (!(disc >= 0)) continue;                  // an orthographic ray past the dome's rim meets none
      q.copy(dir).multiplyScalar(Math.sqrt(disc) - b).add(w);
      if (!(q.y > 1e-9 * rad)) continue;           // under the dome's horizon is its stand-in ground
      // the share of this pixel the dome shows in, once everything is drawn over it
      let open = 1;
      if (dome) {
        rc.set(o, dir);
        const items = [Object.assign({}, dome, { depth: at.copy(q).add(c).sub(eye).dot(fwd) })];
        for (const h of castAll(rc, hits)) {
          const z = at.copy(h.point).sub(eye).dot(fwd);
          if (!(z >= camera.near && z <= camera.far)) continue;  // clipped at near and far: not drawn
          const it = drawItem(h, R, dir, z, 0, zOf, walked, skyParts);
          if (it) items.push(it);
        }
        open = composite(items.sort(order), R);
      }
      shown += open;
      if (first && shown >= 1) return shown / all;
    }
    return shown / all;
  };
  /* TXT.skyInFrame(camera, R) — the share of the frame where the sky shows, 0 to 1: a 25 by 25 grid
   * of rays through the image, corners included, each unprojected through the projection the
   * renderer uses, so zoom, a lens offset and roll all count (Codex, PR 369: read off pitch alone, a
   * portrait camera rolled 90 degrees and pitched 18 down found 0.054 sky with every corner ray under
   * the horizon). A ray shows sky where it meets the dome above the dome's horizon. The dome sits on
   * the camera and draws its far side, so a perspective ray's own direction decides, and an
   * orthographic camera's rays, parallel and starting across its whole near plane, are each followed
   * to the dome (Codex, PR 369: a frustum 200 m tall pitched 5 degrees down shows sky in its upper
   * rows, and reading its direction alone found none). Given R, the dome has to be drawn and a ray has
   * to reach it: a solid thing the camera draws over it, inside its near and far, hides the sky
   * there, where glass, a veil or a glow doesn't (Codex, PR 369: a wall filling the frame read as
   * sky), each ray's hits drawn in the renderer's own order, the dome among them, so a wall that fails
   * its depth test behind a nearer surface drawn first hides nothing (Codex, PR 373). A cutout is read
   * at the mip level this frame samples it at, and an alpha-hashed surface hides the sky by the chance
   * it draws, so a ray counts for the share of it that gets through. Without R it measures the dome
   * TXT.sky builds for this camera, with nothing in front. */
  TXT.skyInFrame = function (camera, R) { return skyShare(camera, R, false); };
  // Read by scripts/carousel/print_ban.py off the render report. Keep the four in step there.
  TXT.NO_SKY = 'TXT: NO SKY IN FRAME';
  TXT.SKY_SHOWN = 'TXT: SKY IN FRAME';
  TXT.NO_ROOM = 'TXT: NO ROOM IN FRAME';
  TXT.ROOM_SHOWN = 'TXT: ROOM IN FRAME';
  TXT.NO_RENDER = 'TXT: NO RENDER IN FRAME';

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
    prepareSurfaces(R);                          // the contact marks, worn grass and grit (THE RECEIVING SURFACE)
    R.renderer.render(R.scene, R.camera);
    /* A WORLD THE CAMERA DOESN'T SHOW IS A VOID (2026-09-26). No. 33's frame 4 called TXT.sky and
     * looked straight down on a lawn, and a judge named it top-down in every one of five rounds.
     * print_ban counted the call. This counts what the camera shows, and the render report carries
     * it to print_ban before a panel sits. Measured on the shipped decks: no. 33's frame 4 and no.
     * 34's frames 4 and 5 print it, each with 0 of the sky above its camera built over, and no. 34's
     * page on the cab seat does not, its cab covering 0.87. */
    // AN INTERIOR IS EXEMPT: "a sky or a deliberate interior" is the test's own question 3. A camera
    // inside something built passes on TXT.enclosure's share, and a room TXT.interior built passes
    // when it fills half the frame (TXT.inRoom). Both are measured above, with the numbers.
    // THE PAGE'S LAST SNAPSHOT IS ITS VERDICT, as print_ban's kept snapshot is the bench's last on the
    // page. A console line can't be unprinted, so each line names its renderer, and the last line on
    // the page is the verdict print_ban and panel_ready read (Codex, PR 369). There is no option to
    // skip this: an opt-out on the kept snapshot passed every gate with the camera on the ground.
    // EVERY SNAPSHOT OF A FRAME THAT STANDS SOMEWHERE PRINTS A VERDICT (Codex, PR 369), a clean one
    // included, so a frame whose TXT.sky or TXT.interior never ran through this snapshot, a 2D
    // fallback behind a branch, has no verdict and fails, rather than reading as clean. A frame that
    // builds only a room is held to the room: it has to fill half the frame, or the camera has to
    // stand inside something built. qa.py lists a clean verdict as a console warn, and gate_status
    // doesn't count it.
    // MEASURED HERE, on the scene as rendered, and PRINTED BELOW, once the pixels are validated
    // (Codex, PR 369): a render that comes out black returns ok false and the frame falls back to
    // whatever it draws instead, so a clean verdict printed before that check would certify a 2D
    // fallback. A failed render prints TXT.NO_RENDER.
    let place = null;
    if (typeof console !== 'undefined' && (R.world || R.room)) {
      const world = !!R.world;
      let sky = 0, cover = 0, share = 0;
      // A dome hidden or taken out before the snapshot leaves the cleared background, not the sky, and
      // sky that something solid covers is not in the frame either. One visible ray is enough, so
      // this stops at the first.
      if (world) sky = skyShare(R.camera, R, true);
      let shown = sky * SKY_RAYS >= 1 - 1e-9;
      if (!shown) { cover = TXT.enclosure(R); shown = cover >= ENCLOSED_MIN; }
      if (!shown) { share = TXT.roomShare(R); shown = share >= ROOM_MIN; }
      place = { world, sky, cover, share, shown };
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
    if (place) {
      const { world, sky, cover, share, shown } = place;
      const page = (typeof window !== 'undefined') ? window : TXT;
      if (!R._txRid) R._txRid = page.__txRid = (page.__txRid || 0) + 1;
      const tag = ' [r' + R._txRid + ']', was = page.__txSky;
      const pct = (x) => Math.round(x * 100);
      if (!ok) {
        page.__txSky = 'none';
        console.error(TXT.NO_RENDER + tag + '. This frame stands in ' + (world ? 'the world' : 'a room') +
          ' and its render came out black or unreadable, so TXT.snapshot returned ok false and the ' +
          'frame falls back to whatever it draws instead. A 2D fallback stands nowhere, and the ' +
          'showstopper test caps it. Fix the render: qa.py\'s dead canvas and the render log say why');
      } else if (!shown && world) {
        page.__txSky = 'none';
        console.error(TXT.NO_SKY + tag + '. This frame calls TXT.sky and its camera shows none of ' +
          'it (pitched below the horizon, looking straight down, the sky dome hidden, or something ' +
          'solid built across all of it), and it ' +
          'stands inside nothing: what the frame built covers ' + pct(cover) + ' percent of the sky ' +
          'above the camera, where an interior covers ' + pct(ENCLOSED_MIN) + '. A reader sees objects ' +
          'in a void, and the showstopper test caps the frame. Lift the camera to put the horizon in ' +
          'frame, or stand it inside something built (the kit\'s semi_cab_interior, or a TXT.interior ' +
          'room filling half the frame). A roof, a canopy or a tree overhead is not an interior');
      } else if (!shown) {
        page.__txSky = 'none';
        console.error(TXT.NO_ROOM + tag + '. This frame builds a room with TXT.interior and its kept ' +
          'camera shows too little of it: the room fills ' + pct(share) + ' percent of the frame, where ' +
          'a room shot fills ' + pct(ROOM_MIN) + ', and what the frame built covers ' + pct(cover) +
          ' percent of the sky above the camera, where an interior covers ' + pct(ENCLOSED_MIN) + '. A ' +
          'reader sees objects in a void. Point the camera into the room or stand it inside, and keep ' +
          'the room drawn');
      } else {
        page.__txSky = 'shown';
        const why = '. A verdict, not a defect: this snapshot ' + (sky > 0 ? 'shows its sky'
          : cover >= ENCLOSED_MIN ? 'stands inside something built' : 'shows its room') +
          (was === 'none' ? '. The line above was a preview and is withdrawn' : '');
        if (world) console.error(TXT.SKY_SHOWN + tag + why);
        else console.error(TXT.ROOM_SHOWN + tag + why);
      }
    }
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
   *   - SOFT SHADOWS that are actually soft (VSM then, PCSS since 2026-10-03, radius honoured)
   *     plus CONTACT shadows, the dark core where a thing meets the ground, which is what stops it
   *     floating, and since 2026-10-03 the dirt that ground holds (THE RECEIVING SURFACE).
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
      // NO CLOUD (2026-10-03): high cloud lit amber over a deep blue printed maroon, and carousel
      // no. 39's chassis had to set this to 0 to get a blue hour at all
      clouds: 0.0, stars: 0.35, fogDensity: 0.006, exposure: 1.1, envIntensity: 0.55, tone: 'aces',
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
      // a scatter is skipped as a whole, the grass Group included, before it is measured
      if (skip.has(root) || root.userData.txGround || root.isLight || root.isInstancedMesh || root.userData.txScatter) continue;
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
      // THE GLOW TURNS YELLOW-WHITE AS IT RISES (2026-10-03). Added as the sun's own orange over a
      // dim blue sky it raised the red and left the blue, so the sky above a sunset printed rose and
      // then mauve: hue 356 to 343 from 14 to 40 percent of the frame over blue hour's horizon,
      // looking at the sun, and a chassis on carousel no. 39 had to switch the glow nearly off.
      // A real twilight goes orange, then pale yellow, then blue. Exactly the old colour ON the
      // line, so the dome, horizonSky and the sky fog still meet there at one value.
      float txSunL = dot(uSunColor, vec3(0.2126, 0.7152, 0.0722));
      vec3 txTail = mix(uSunColor, vec3(txSunL) * vec3(1.0, 0.96, 0.78), smoothstep(0.0, 0.16, max(h, 0.0)));
      col += txTail * uHorizonGlow * pow(toward, 3.0) * exp(-abs(h) * 7.0);
      // the halo's wide terms take the same turn, and the sun's own core keeps its colour
      col += txTail * uGlow * (0.035 * pow(max(cs, 0.0), 3.0) + 0.30 * pow(max(cs, 0.0), 48.0))
           + uSunColor * uGlow * 1.2 * pow(max(cs, 0.0), 900.0);
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
    R._txDome = dome;             // the snapshot asks whether it is still drawn (Codex, PR 369)
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
  /* ---- THE RECEIVING SURFACE (2026-10-03) ------------------------------------------------
   * The judges named it on six of seven decks in the week to October 3rd, in 21 rounds: a model
   * stands on a ground that is clean where it meets it, and the ground itself reads as one tile
   * repeated to the horizon. No. 41's truck court was "an untextured tiled concrete plane" in
   * every round, no. 40's coping "a smooth plane with one highlight streak", 09-30's lawn "one
   * tiled grass texture" with "no dirt, wear, path or kerb". TXT.contact laid a dark core and
   * TXT.weather grimed the object from its base up, and nothing touched the ground. Two things
   * do now, both in the ground's own shader, so they are lit, shadowed and fogged as the ground:
   *
   *   WEAR, on every TXT.ground surface: value that drifts at 11 and 41 m in WORLD space (so the
   *   6 m texture tile never repeats), each concrete slab a shade of its own pour, grime along the
   *   saw cut joints, and sparse clusters of stains (oil on concrete and asphalt, damp on caliche
   *   and dirt), with straw against green and a bare patch here and there on grass.
   *   `wear:false` turns it off, `wear:'interior'` keeps a floor clean of oil, and an object of
   *   amounts tunes it ({ macro, slab, joint, stain }).
   *
   *   MARKS, from TXT.contact: the ground under and around a thing's BASE (what it stands on, not
   *   its crown or its crossarm) takes a dirt band broken by noise, scaled to the footprint. A
   *   vehicle also drips oil under its engine and polishes two tyre tracks fore and aft. They are
   *   laid when the frame renders, so a ground built after the contact still takes them, and the
   *   nearest 24 to the camera are drawn. `dirt:false` on the contact opts one object out. */
  const WEAR = {
    concrete: { macro: 0.075, slab: 0.05, joint: 0.32, jointW: 0.06, stain: 0.6, stainCol: [0.56, 0.54, 0.51], sheen: 0.1,
      straw: 0, bare: 0, dirt: 0x4b433b, dirtMix: 0.5, dirtDark: 0.08, oil: 1, polish: 1, track: 0, grit: [0x5e574f, 0x6f685f, 0x4a443d, 0x8a847a] },
    asphalt: { macro: 0.09, slab: 0, joint: 0, jointW: 0, stain: 0.4, stainCol: [0.66, 0.66, 0.68], sheen: 0.1,
      straw: 0, bare: 0, dirt: 0x6f665a, dirtMix: 0.32, dirtDark: 0, oil: 0.75, polish: 0.8, track: 0, grit: [0x7a7468, 0x8f887b, 0x5e5850, 0xa49c8e] },
    caliche: { macro: 0.1, slab: 0, joint: 0, jointW: 0, stain: 0.3, stainCol: [0.80, 0.76, 0.70], sheen: 0,
      straw: 0, bare: 0, dirt: 0x8a7860, dirtMix: 0.38, dirtDark: 0.04, oil: 0.55, polish: 0.55, track: 0, grit: [0xcfc4ad, 0xb8ab92, 0x9a8c74, 0xe0d8c6] },
    dirt: { macro: 0.12, slab: 0, joint: 0, jointW: 0, stain: 0.28, stainCol: [0.80, 0.78, 0.75], sheen: 0,
      straw: 0, bare: 0, dirt: 0x3a2e24, dirtMix: 0.3, dirtDark: 0.04, oil: 0.4, polish: 0.5, track: 0, grit: [0x4e4236, 0x5f5141, 0x6b5a48, 0x3e352c] },
    // worn turf in a Texas October is dry and dusty, near the grass's own value: dark brown read as mud
    grass: { macro: 0.1, slab: 0, joint: 0, jointW: 0, stain: 0, stainCol: [1, 1, 1], sheen: 0,
      straw: 0.45, bare: 0.4, dirt: 0x8a7c64, dirtMix: 0.62, dirtDark: 0, oil: 0, polish: 0.3, track: 0.65, grit: null },
    lawn: { macro: 0.08, slab: 0, joint: 0, jointW: 0, stain: 0, stainCol: [1, 1, 1], sheen: 0,
      straw: 0.3, bare: 0.3, dirt: 0x7f7058, dirtMix: 0.6, dirtDark: 0, oil: 0, polish: 0.3, track: 0.65, grit: null },
  };
  // an interior floor: a sealed slab drifts in tone and greys at its joints, and nobody parks on it
  // and no grit, which a blind grader read as stray pebbles on an office floor (09-30 frame 5)
  const WEAR_INTERIOR = { macro: 0.045, slab: 0.035, joint: 0.18, stain: 0, oil: 0, polish: 0, bare: 0, grit: null, dirtMix: 0.15, dirtDark: 0.12 };
  /* A PAD A DECK LAID ITSELF IS A RECEIVING SURFACE TOO (2026-10-03). Decks build their own flat
   * grounds, a graded pad, a field, a lot, as a plain plane over TXT.ground. 09-29's pad hid the
   * worker's dirt band and contact on the ground beneath it, so the wear changed nothing a reader
   * could see, and the blind grader found no difference on any of its nine frames. A plane that is
   * flat, faces up, covers 30 square metres or more, is opaque and matte and receives shadows, and
   * has a contact's base standing on it, takes the marks too: TXT.contact puts its contact on it,
   * and the snapshot gives it the wear shader on a clone of its material. Its surface is not known,
   * so it takes the marks and a slow drift of value and no stains, joints or grit, unless the deck
   * names it (`mesh.userData.txSurface = 'concrete'`). `mesh.userData.txWear = false` keeps a
   * plane exactly as the deck made it. */
  const WEAR_ADOPT = { macro: 0.06, slab: 0, joint: 0, jointW: 0, stain: 0, stainCol: [1, 1, 1], straw: 0, bare: 0,
    track: 0, sheen: 0, dirt: 0x463d34, dirtMix: 0.25, dirtDark: 0.28, oil: 0.6, polish: 0.5, grit: null };
  // a matte, opaque standard material the deck has not written its own shader into
  function supportMaterial(m) {
    const u = m.userData || {}, mat = m.material;
    if (!m.isMesh || m.isInstancedMesh || u.txGround || u.txWear === false || !m.receiveShadow) return false;
    if (!mat || Array.isArray(mat) || !mat.isMeshStandardMaterial || mat.transparent || mat.opacity < 1 || mat.transmission > 0) return false;
    if (!u.txAdopted && Object.prototype.hasOwnProperty.call(mat, 'onBeforeCompile')) return false;
    return mat.roughness >= 0.5 && mat.metalness <= 0.3;
  }
  function flatPlane(m) {
    if (!supportMaterial(m)) return null;
    const g = m.geometry;
    if (!g || !g.attributes.position) return null;
    if (!g.boundingBox) g.computeBoundingBox();
    m.updateWorldMatrix(true, false);
    const bb = g.boundingBox.clone().applyMatrix4(m.matrixWorld);
    const dx = bb.max.x - bb.min.x, dz = bb.max.z - bb.min.z;
    if (bb.max.y - bb.min.y > 0.05 || dx * dz < 30 || Math.min(dx, dz) < 2) return null;
    const n = g.attributes.normal;
    if (n && new THREE.Vector3().fromBufferAttribute(n, 0).transformDirection(m.matrixWorld).y < 0.9) return null;
    return { y: bb.max.y, bb };
  }
  const TX_MARKS = 24;
  function marksOf(R) {
    if (!R._txMarks) R._txMarks = {
      list: [], n: { value: 0 },
      a: Array.from({ length: TX_MARKS }, () => new THREE.Vector4()),
      b: Array.from({ length: TX_MARKS }, () => new THREE.Vector4()),
    };
    return R._txMarks;
  }
  function wearSpec(o) {
    const base = WEAR[o.surface] || WEAR.caliche;
    if (o.wear === false) return Object.assign({}, base, { macro: 0, slab: 0, joint: 0, stain: 0, straw: 0, bare: 0 });
    if (o.wear === 'interior') return Object.assign({}, base, WEAR_INTERIOR);
    return Object.assign({}, base, typeof o.wear === 'object' ? o.wear : {});
  }
  const GROUND_PARS = `
    varying vec3 vTxGW;
    uniform vec4 uTxWearA, uTxWearB, uTxWearC, uTxDirtK;
    uniform vec3 uTxStainCol, uTxDirtCol;
    uniform vec4 uTxMarkA[${TX_MARKS}], uTxMarkB[${TX_MARKS}];
    uniform int uTxMarkN;
    float txgRough;
    float txgH(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
    float txgN(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(txgH(i), txgH(i + vec2(1.0, 0.0)), f.x), mix(txgH(i + vec2(0.0, 1.0)), txgH(i + vec2(1.0, 1.0)), f.x), f.y); }
    float txgF(vec2 p) { float s = 0.0, a = 0.5; for (int i = 0; i < 3; i++) { s += a * txgN(p); p = p * 2.03 + 17.13; a *= 0.5; } return s / 0.875; }`;
  const GROUND_WEAR = `
    txgRough = 0.0;
    {
      vec2 w = vTxGW.xz;
      float sd = uTxWearB.w;
      // 1. value that drifts in world space, at two scales, so the tile never repeats
      float m1 = txgF(w / 11.0 + sd), m2 = txgF(w / 41.0 - sd);
      diffuseColor.rgb *= 1.0 + uTxWearA.x * ((m1 - 0.5) * 1.3 + (m2 - 0.5) * 0.9);
      txgRough += uTxWearA.x * 0.6 * (m1 - 0.5);
      #ifdef USE_MAP
      // 2. a slab poured on its own day, and the dirt a saw cut joint holds
      if (uTxWearB.x > 0.0) {
        vec2 sc = vMapUv * uTxWearB.x;
        // a slab's own tone, held back where the rows crowd to a few pixels and read as bands
        float crowd = smoothstep(0.06, 0.25, length(fwidth(sc)));
        diffuseColor.rgb *= 1.0 + uTxWearA.y * 2.0 * (txgH(floor(sc) + sd) - 0.5) * (1.0 - 0.6 * crowd);
        vec2 fj = abs(fract(sc) - 0.5);
        float dj = (0.5 - max(fj.x, fj.y)) * uTxWearB.z / uTxWearB.x;
        // THE JOINT IS FILTERED. Grime a few centimetres wide is thinner than a pixel far off, and
        // sampled a point at a time it broke into dotted hairlines (no. 41 frame 9). Widened to the
        // pixel it falls in, it keeps its average darkness and loses the dots.
        float gw = uTxWearB.y * (0.5 + txgN(w * 1.7 + 3.0)), fd = fwidth(dj);
        float jl = 1.0 - smoothstep(0.0, gw + fd, dj);
        float jg = jl * jl * gw / (gw + fd) * (0.55 + 0.6 * txgN(w * 0.6));
        diffuseColor.rgb *= 1.0 - uTxWearA.z * jg;
        txgRough += 0.08 * jg;
      }
      #endif
      // 3. stains in sparse clusters: oil on a slab or a lot, damp on caliche and dirt
      if (uTxWearA.w > 0.0) {
        float cl = smoothstep(0.56, 0.68, txgF(w / 23.0 + sd * 1.7));
        if (cl > 0.0) {
          float st = cl * smoothstep(0.6, 0.67, txgF(w / 1.1 - sd));
          diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * uTxStainCol, uTxWearA.w * st);
          txgRough -= uTxWearC.w * st;
        }
      }
      // 4. grass: straw against green, and the odd bare patch
      if (uTxWearC.x > 0.0) diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(1.18, 1.06, 0.72),
        uTxWearC.x * smoothstep(0.35, 0.75, txgF(w / 7.0 + sd * 0.3)));
      if (uTxWearC.y > 0.0) {
        float bc = smoothstep(0.5, 0.62, txgF(w / 23.0 + 5.0));
        if (bc > 0.0) diffuseColor.rgb = mix(diffuseColor.rgb, uTxDirtCol, uTxWearC.y * bc * smoothstep(0.62, 0.74, txgF(w / 3.3 - sd * 0.7)));
      }
      // 5. the marks TXT.contact laid: a dirt band at a base, oil and tyre tracks at a vehicle
      float dirt = 0.0, oil = 0.0, pol = 0.0;
      for (int i = 0; i < ${TX_MARKS}; i++) {
        if (i >= uTxMarkN) break;
        vec4 A = uTxMarkA[i], B = uTxMarkB[i];
        // a mark belongs to the surface at its own height: a yard sunk below a dock, a pad laid
        // over a ground, a floor under a mezzanine each take only their own. A thing standing on a
        // ledge or a sill (a negative half width) marks only that top face, not the side below it.
        bool sup = A.z < 0.0;
        if (abs(vTxGW.y - B.z) > (sup ? 0.03 : 0.3)) continue;
        bool veh = B.w < 0.0;
        float str = abs(B.w);
        vec2 d = w - A.xy;
        float c = cos(B.x), s = sin(B.x);
        vec2 l = vec2(c * d.x - s * d.y, s * d.x + c * d.y);
        vec2 q = abs(l) - vec2(abs(A.z), A.w);
        float reach = B.y * 3.5 + (veh ? 4.0 + A.w * 0.5 : 0.0);
        if (max(q.x, q.y) > reach) continue;
        float sdist = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
        // the band's breakup is sized to the band, so a vial's is as broken as a van's
        float ns = max(1.0, 0.12 / B.y);
        float n = txgN(w * 2.3 * ns + float(i) * 3.7);
        // under the thing the band fades in from its edge; on grass it is trodden all the way across
        float inner = sdist < 0.0 ? mix(smoothstep(-0.6, -0.1, sdist / B.y), 1.0, uTxWearC.z * 0.85) : 1.0;
        float band = exp(-max(sdist, 0.0) / (B.y * (0.45 + 0.8 * n))) * inner;
        dirt = max(dirt, band * str * (0.75 + 0.5 * txgN(w * 6.1 * ns - float(i))));
        if (veh) {
          // oil drips in blots with an edge, most of them under the engine end
          float inside = 1.0 - smoothstep(-0.25, 0.1, sdist);
          float front = 0.55 + 0.45 * smoothstep(-A.w, A.w, l.y);
          oil = max(oil, inside * front * smoothstep(0.57, 0.63, txgF(l * 1.4 + float(i) * 5.1)));
          // two tyre tracks a dual set wide, streaked along the way the wheels roll, fading fore and aft
          float track = max(A.z - 0.42, 0.2);
          float lane = 1.0 - smoothstep(0.18, 0.32, abs(abs(l.x) - track));
          float along = exp(-max(abs(l.y) - A.w, 0.0) / (2.0 + A.w * 0.25));
          float streak = 0.45 + 0.6 * txgN(vec2(l.x * 14.0, l.y * 0.35) + float(i) * 2.9);
          pol = max(pol, lane * along * str * streak);
        }
      }
      diffuseColor.rgb = mix(diffuseColor.rgb, uTxDirtCol, uTxDirtK.y * dirt) * (1.0 - uTxDirtK.x * dirt);
      diffuseColor.rgb *= 1.0 - 0.45 * uTxDirtK.z * oil;
      txgRough -= 0.3 * uTxDirtK.z * oil;
      diffuseColor.rgb = mix(diffuseColor.rgb * (1.0 - 0.3 * uTxDirtK.w * pol), uTxDirtCol, uTxWearC.z * pol);
      txgRough -= 0.22 * uTxDirtK.w * pol * (1.0 - uTxWearC.z) - 0.05 * dirt;
    }`;
  function wearUniforms(o, W, R, tile, jointsPerTile) {
    const M = marksOf(R);
    const sd = ((o.seed || 20260924) % 997) * 0.731;
    return {
      uTxWearA: { value: new THREE.Vector4(W.macro, W.slab, W.joint, W.stain) },
      uTxWearB: { value: new THREE.Vector4(jointsPerTile, W.jointW || 0.06, tile, sd) },
      uTxWearC: { value: new THREE.Vector4(W.straw, W.bare, W.track, W.sheen) },
      uTxDirtK: { value: new THREE.Vector4(W.dirtDark, W.dirtMix, W.oil, W.polish) },
      uTxStainCol: { value: new THREE.Vector3(W.stainCol[0], W.stainCol[1], W.stainCol[2]) },
      uTxDirtCol: { value: new THREE.Color(W.dirt) },
      uTxMarkA: { value: M.a }, uTxMarkB: { value: M.b }, uTxMarkN: M.n,
    };
  }

  // the wear, the marks and the world position they are laid in, into a standard material's shader
  function wearPatch(sh, WU) {
    Object.assign(sh.uniforms, WU);
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vTxGW;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvTxGW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\n' + GROUND_PARS)
      .replace('#include <color_fragment>', '#include <color_fragment>\n' + GROUND_WEAR)
      .replace('#include <roughnessmap_fragment>',
        '#include <roughnessmap_fragment>\nroughnessFactor = clamp(roughnessFactor + txgRough, 0.06, 1.0);');
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
    // whole joints per texture tile, as surfaceTextures draws them: the slab grid the wear reads
    const jpt = (T.S.joints || o.joints) ? Math.max(1, Math.round(o.joints || T.S.joints)) : 0;
    const WU = wearUniforms(o, wearSpec(o), R, tile, jpt);
    /* THE BUMP FADES WITH DISTANCE (2026-09-24). At a grazing angle the fine tooth aliases into
     * thin horizontal stripes, which no. 33's judges read as busy, streaked dirt behind the fence.
     * Relief belongs where a reader can see relief, so the bump fades out between about 18 and
     * 90 m from the camera and the colour map carries the distance. */
    mat.onBeforeCompile = (sh) => {
      wearPatch(sh, WU);
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <bumpmap_pars_fragment>',
          'float txBumpS;\n' + THREE.ShaderChunk.bumpmap_pars_fragment.split('bumpScale *').join('txBumpS *'))
        .replace('#include <normal_fragment_begin>',
          'txBumpS = bumpScale * (1.0 - smoothstep(18.0, 90.0, length(vViewPosition)));\n#include <normal_fragment_begin>');
    };
    const g = new THREE.Mesh(geo, mat);
    g.rotation.x = -Math.PI / 2; g.position.y = o.y || 0;
    g.receiveShadow = true; markGround(g);
    g.userData.txSurface = o.surface;
    g.userData.txWear = wearSpec(o);
    R.scene.add(g);
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
  /* THE BASE, NOT THE BOX. A pole's crossarm, a tree's crown and a streetlight's arm all widen a
   * bounding box well past where the thing meets the ground, so the dirt is laid from what lies in
   * the bottom slice of the object (a fifth of its height, 6 to 50 cm): a pole's foot, a tree's
   * trunk, a desk's four legs, a truck's wheels. Measured on the object as TXT.contact holds it, at
   * the origin and unrotated. */
  /* What a thing with no ground under it stands on: the highest matte, opaque, shadow receiving
   * mesh that is not part of it, whose box takes in the footprint's centre and whose top is within
   * 5 cm below to 3 cm above the thing's base. A box's top is a sill's or a ledge's face. A sloped
   * or carved surface's box top can sit above the face itself, and the shader's 3 cm window then
   * finds no face to mark, which is a mark missed rather than a mark in the air. */
  function supportUnder(R, obj, x, z, base) {
    let best = null;
    const bb = new THREE.Box3();
    R.scene.traverse((m) => {
      if (!m.isMesh || !supportMaterial(m) || !m.geometry || !m.geometry.attributes.position) return;
      const g = m.geometry;
      if (!g.boundingBox) g.computeBoundingBox();
      m.updateWorldMatrix(true, false);
      bb.copy(g.boundingBox).applyMatrix4(m.matrixWorld);
      const top = bb.max.y;
      if (top < base - 0.05 || top > base + 0.03 || x < bb.min.x || x > bb.max.x || z < bb.min.z || z > bb.max.z) return;
      for (let a = m; a; a = a.parent) if (a === obj) return;
      if (!best || top > best.y) best = { m, y: top };
    });
    return best;
  }
  function baseFootprint(obj, box) {
    if (box.isEmpty()) return null;
    const top = box.min.y + Math.max(0.06, Math.min(0.5, 0.2 * (box.max.y - box.min.y)));
    let x0 = Infinity, z0 = Infinity, x1 = -Infinity, z1 = -Infinity;
    const v = new THREE.Vector3(), bb = new THREE.Box3(), im = new THREE.Matrix4(), wm = new THREE.Matrix4();
    obj.traverseVisible((m) => {
      if (!m.isMesh || !m.geometry || !m.geometry.attributes.position || (m.userData && m.userData.txGround)) return;
      const g = m.geometry;
      if (!g.boundingBox) g.computeBoundingBox();
      const n = m.isInstancedMesh ? m.count : 1;
      for (let i = 0; i < n; i++) {
        wm.copy(m.matrixWorld);
        if (m.isInstancedMesh) { m.getMatrixAt(i, im); wm.multiply(im); }
        bb.copy(g.boundingBox).applyMatrix4(wm);
        if (bb.min.y > top) continue;
        if (m.isInstancedMesh || bb.max.y <= top) {
          x0 = Math.min(x0, bb.min.x); z0 = Math.min(z0, bb.min.z); x1 = Math.max(x1, bb.max.x); z1 = Math.max(z1, bb.max.z);
          continue;
        }
        const P = g.attributes.position;
        for (let k = 0; k < P.count; k++) {
          v.fromBufferAttribute(P, k).applyMatrix4(wm);
          if (v.y > top) continue;
          if (v.x < x0) x0 = v.x; if (v.z < z0) z0 = v.z; if (v.x > x1) x1 = v.x; if (v.z > z1) z1 = v.z;
        }
      }
    });
    if (!isFinite(x0)) return null;
    return { cx: (x0 + x1) / 2, cz: (z0 + z1) / 2, hw: Math.max(0.03, (x1 - x0) / 2), hd: Math.max(0.03, (z1 - z0) / 2) };
  }
  // a vehicle drips oil and polishes the ground it drives: the kit's vehicles, a chassis's van
  const VEHICLE_RE = /(^|_)(van|truck|semi|pickup|sedan|suv|bus|trailer|car|tractor)(_|$)/;
  function isVehicle(obj) {
    let v = false;
    obj.traverse((m) => {
      if (v || !m.userData) return;
      const k = m.userData.kit;
      if (m.userData.txVehicle || (typeof k === 'string' && !/interior|recorder/.test(k) && VEHICLE_RE.test(k))) v = true;
    });
    return v;
  }
  function groundAt(R, y) {
    let best = null;
    const v = new THREE.Vector3();
    R.scene.traverse((m) => {
      const u = m.userData;
      if (!u || !((u.txGround && u.txSurface) || u.txAdopted)) return;
      const gy = u.txAdopted ? u.txAdoptY : m.getWorldPosition(v).y;
      if (Math.abs(gy - y) < 0.06 && (!best || gy > best.y)) best = { m, y: gy };
    });
    return best;
  }
  const hash2 = (a, b) => { const s = Math.sin(a * 12.9898 + b * 78.233) * 43758.5453; return s - Math.floor(s); };
  // a mark's footprint in its own frame: signed distance to the rectangle, negative inside
  function markDist(k, x, z) {
    const dx = x - k.cx, dz = z - k.cz, c = Math.cos(k.angle), s = Math.sin(k.angle);
    const qx = Math.abs(c * dx - s * dz) - k.hw, qz = Math.abs(s * dx + c * dz) - k.hd;
    return Math.hypot(Math.max(qx, 0), Math.max(qz, 0)) + Math.min(Math.max(qx, qz), 0);
  }
  /* WORN GRASS: a tuft standing where a thing stands, or where feet and wheels go round it, is
   * trampled, so the scatter thins there and the dirt band shows through. Idempotent. */
  function thinGrass(R, marks) {
    const m4 = new THREE.Matrix4(), w = new THREE.Vector3(), zero = new THREE.Matrix4().makeScale(0, 0, 0);
    let part = 0;
    R.scene.traverse((g) => {
      if (!g.isInstancedMesh || !g.parent) return;
      const tag = (g.userData && g.userData.txScatter) || (g.parent.userData && g.parent.userData.txScatter);
      if (tag !== 'grass') return;
      g.updateMatrixWorld(true);
      part++;
      let changed = false;
      for (let i = 0; i < g.count; i++) {
        g.getMatrixAt(i, m4);
        w.setFromMatrixPosition(m4).applyMatrix4(g.matrixWorld);
        for (const k of marks) {
          if (Math.abs(w.y - k.y) > 0.4) continue;
          const d = markDist(k, w.x, w.z), reach = k.band * 2.5;
          if (d > reach) continue;
          const p = (k.vehicle ? 0.97 : 0.88) * (d <= 0 ? 1 : Math.exp(-d / (k.band * 0.9)));
          if (hash2(i + part * 7919, k.seed) < p) { g.setMatrixAt(i, zero); changed = true; break; }
        }
      }
      if (changed) g.instanceMatrix.needsUpdate = true;
    });
  }
  /* GRIT AT THE BASE: on a hard ground, the grit and crumbs that drift against a thing standing on
   * it, in patchy deposits close in, scaled to the footprint's perimeter. Never round a vehicle,
   * whose ground is its oil and tyre tracks (a ring of crumbs along a trailer read as a line of
   * breadcrumbs in the first proof), and never round anything as small as a person. One draw call. */
  function layGrit(R, marks) {
    const P = [], C = [], col = new THREE.Color();
    for (const k of marks) {
      if (k.gritDone || !k.grit) continue;
      k.gritDone = true;
      if (k.vehicle || Math.min(k.hw, k.hd) * 2 < 0.35) continue;
      const gr = groundAt(R, k.y), W = gr && gr.m.userData.txWear;
      if (!W || !W.grit) continue;
      const rng = TXT.rng(9173 + k.seed * 131), W2 = 2 * k.hw, D2 = 2 * k.hd, per = 2 * (W2 + D2);
      const clusters = Math.min(160, Math.round(per * 2.6 * k.strength));
      const c = Math.cos(k.angle), s = Math.sin(k.angle);
      for (let j = 0; j < clusters; j++) {
        // a deposit at a point on the edge, a little way out, and a handful of grains round it
        let t = rng() * per, lx, lz, nx = 0, nz = 0;
        if (t < W2) { lx = -k.hw + t; lz = -k.hd; nz = -1; }
        else if ((t -= W2) < D2) { lx = k.hw; lz = -k.hd + t; nx = 1; }
        else if ((t -= D2) < W2) { lx = k.hw - t; lz = k.hd; nz = 1; }
        else { t -= W2; lx = -k.hw; lz = k.hd - t; nx = -1; }
        const out = k.band * 0.7 * Math.pow(rng(), 2.2);
        lx += nx * out; lz += nz * out;
        const grains = 2 + Math.floor(rng() * 6), spread = 0.03 + 0.09 * rng();
        for (let g = 0; g < grains; g++) {
          const gx = lx + (rng() - 0.5) * spread * 2, gz = lz + (rng() - 0.5) * spread * 2;
          const sz = 0.004 + 0.014 * Math.pow(rng(), 2.4) + (rng() < 0.05 ? 0.02 * rng() : 0);
          P.push(k.cx + gx * c + gz * s, k.y + sz * 0.2, k.cz - gx * s + gz * c, sz, rng() * Math.PI * 2);
          col.set(W.grit[Math.floor(rng() * W.grit.length)]).multiplyScalar(0.75 + 0.35 * rng());
          C.push(col.r, col.g, col.b);
        }
      }
    }
    if (!P.length) return;
    const count = P.length / 5;
    const geo = lumpGeometry(TXT.rng(4242), 1, 0.55, 0.7);
    const mesh = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ roughness: 0.9 }), count);
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0);
    for (let i = 0; i < count; i++) {
      q.setFromAxisAngle(up, P[i * 5 + 4]);
      m4.compose(new THREE.Vector3(P[i * 5], P[i * 5 + 1], P[i * 5 + 2]), q, new THREE.Vector3(P[i * 5 + 3], P[i * 5 + 3], P[i * 5 + 3]));
      mesh.setMatrixAt(i, m4);
      mesh.setColorAt(i, col.setRGB(C[i * 3], C[i * 3 + 1], C[i * 3 + 2]));
    }
    mesh.castShadow = false; mesh.receiveShadow = true;
    mesh.userData.txScatter = 'grit';
    mesh.raycast = function () {};       // at ground level it can never be a roof or a wall
    R.scene.add(mesh);
  }
  /* Run by TXT.snapshot before it renders, when every ground and every object is in place: the 24
   * marks nearest the lens (ahead of it before behind it) go to the grounds' shaders, the grass
   * under them thins, and the grit is laid. */
  function adoptSurface(R, m, y, seed) {
    const named = WEAR[m.userData.txSurface];
    // a deck's texture has its own joints, at a spacing the engine can't know, so none are drawn
    const W = Object.assign({}, named || WEAR_ADOPT, { slab: 0, joint: 0, jointW: 0 });
    const WU = wearUniforms({ seed: 9001 + 17 * seed }, W, R, 6, 0);
    const mat = m.material.clone();
    mat.onBeforeCompile = (sh) => wearPatch(sh, WU);
    mat.customProgramCacheKey = () => 'txwear-adopted';
    m.material = mat;
    Object.assign(m.userData, { txAdopted: true, txAdoptY: y, txWear: W });
  }
  function adoptPlanes(R, marks) {
    let seed = 0;
    R.scene.traverse((m) => {
      const f = flatPlane(m);
      if (!f || m.userData.txAdopted) return;
      const on = marks.some((k) => !k.support && Math.abs(k.y - f.y) < 0.25 && k.cx >= f.bb.min.x && k.cx <= f.bb.max.x && k.cz >= f.bb.min.z && k.cz <= f.bb.max.z);
      if (on) adoptSurface(R, m, f.y, seed++);
    });
    /* A LEDGE, A SILL OR A COPING a thing stands on outdoors takes its mark on its top face
     * (2026-10-02 item 6: "the coping on frames 1, 7 and 8 is a smooth plane"). Never indoors,
     * where a ring at a monitor's foot on a desk reads as a stain and not as weather. */
    if (R.world && !R.room) for (const k of marks) {
      const m = k.support;
      if (m && !m.userData.txAdopted && m.userData.txWear !== false && supportMaterial(m)) adoptSurface(R, m, k.y, seed++);
    }
  }
  function prepareSurfaces(R) {
    const M = R._txMarks;
    if (!M || !M.list.length) return;
    const cam = R.camera, eye = new THREE.Vector3(), fwd = new THREE.Vector3();
    cam.updateMatrixWorld(); eye.setFromMatrixPosition(cam.matrixWorld); cam.getWorldDirection(fwd);
    const score = (k) => {
      const r = Math.hypot(k.hw, k.hd), dx = k.cx - eye.x, dz = k.cz - eye.z;
      const along = dx * fwd.x + (k.y - eye.y) * fwd.y + dz * fwd.z;
      return (along < -r ? 1e6 : 0) + Math.max(0, Math.hypot(dx, dz) - r);
    };
    const use = M.list.slice().sort((A, B) => score(A) - score(B)).slice(0, TX_MARKS);
    // b.z is the height of the surface the mark lies on, and a vehicle's mark carries its strength negative
    // and a support's mark (a sill, a ledge) carries its half width negative
    use.forEach((k, i) => {
      const hw = Math.max(1e-3, k.hw);
      M.a[i].set(k.cx, k.cz, k.support ? -hw : hw, k.hd);
      M.b[i].set(k.angle, k.band, k.y, k.vehicle ? -Math.max(1e-3, k.strength) : k.strength);
    });
    M.n.value = use.length;
    adoptPlanes(R, use);
    thinGrass(R, use);
    layGrit(R, use);
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
    const foot = o.dirt === false ? null : baseFootprint(obj, box);
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
    let y = o.y, onGround = false;
    if (y == null) {
      const grounds = [], v = new THREE.Vector3();
      R.scene.traverse((m) => {
        if (m.userData && m.userData.txGround) { grounds.push(m.getWorldPosition(v).y); return; }
        // a pad the deck laid over the ground is what the thing stands on (THE RECEIVING SURFACE),
        // unless it is part of the thing itself
        const f = flatPlane(m);
        if (!f) return;
        for (let a = m; a; a = a.parent) if (a === obj) return;
        grounds.push(f.y);
      });
      if (!grounds.length) grounds.push(0);
      const under = grounds.filter((gy) => gy >= wb.min.y - 0.25 && gy < wb.max.y);
      y = under.length ? Math.max(...under) : wb.min.y;
      onGround = under.length > 0;
    }
    // no ground under it: what it stands on, a sill or a ledge, takes its mark on its top face
    let support = null;
    if (foot && !onGround && o.y == null) {
      const c = new THREE.Vector3(foot.cx, 0, foot.cz).applyQuaternion(q).add(p);
      support = supportUnder(R, obj, c.x, c.z, wb.min.y);
      if (support) { y = support.y; onGround = true; }
    }
    /* THE GROUND TAKES THE MARK, a dock or a desk does not: a thing standing on a ground lays its
     * dirt band (and, a vehicle, its oil and tyre tracks) in that ground's shader, and its grit,
     * when the frame renders. See THE RECEIVING SURFACE. */
    if (foot && onGround) {
      const yaw = new THREE.Euler().setFromQuaternion(q, 'YXZ').y;
      const c = new THREE.Vector3(foot.cx, 0, foot.cz).applyQuaternion(q).add(p);
      const vehicle = o.vehicle != null ? !!o.vehicle : isVehicle(obj);
      const minor = Math.min(foot.hw, foot.hd) * 2;
      // a band scaled to the footprint: a van's reaches a third of a metre, a vial's a couple of centimetres
      const band = minor < 0.25 ? Math.max(0.012, 0.7 * minor) : Math.max(0.12, Math.min(0.65, 0.1 + 0.16 * Math.sqrt(minor)));
      marksOf(R).list.push({ cx: c.x, cz: c.z, y, hw: foot.hw, hd: foot.hd, angle: yaw, vehicle, band,
        strength: (typeof o.dirt === 'number' ? o.dirt : 1) * (vehicle ? 0.75 : 1),
        grit: o.grit !== false && !support, support: support && support.m, seed: marksOf(R).list.length + 1 });
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
    TXT.ground(R, { surface: o.floor || 'concrete', size: Math.max(w, d) * 3, tile: o.tile || 3, joints: o.joints,
      wear: o.wear != null ? o.wear : 'interior' });
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
   *                  seed, scale:[min,max], colors:[hex...], variants, translucency }): a seeded field,
   * one InstancedMesh for scrub or rock and for grass a Group of one per tuft in its pool, whose
   * blades transmit light from behind. `variants` sets the pool (default 5, 1 for the old single
   * tuft) and `translucency` the light through a blade (default 0.65, 0 for none).
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
  /* BLADES THAT LET THE LIGHT THROUGH (2026-10-03). A field seen into a low sun printed black
   * stubble on carousel no. 39, frames 1 and 3 in rounds 1 to 3, because a grass blade is a thin
   * sheet that transmits and a standard material has no term for light arriving from behind it.
   * This adds one after every direct light in the material's own light loop, so the light's shadow
   * is already folded into its colour and a blade in a building's shadow stays dark: the share of
   * the light reaching the blade's far face, strongest when the camera looks into that light. */
  const RE_DIRECT = 'RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );';
  function grassMaterial(transl) {
    const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, side: THREE.DoubleSide });
    if (!(transl > 0)) return mat;
    mat.onBeforeCompile = (sh) => {
      sh.uniforms.uTxTransl = { value: transl };
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <lights_physical_pars_fragment>', `#include <lights_physical_pars_fragment>
uniform float uTxTransl;
vec3 txTransl( vec3 L, vec3 lightColor, vec3 N, vec3 V, vec3 albedo ) {
  float through = saturate( -dot( N, L ) );
  float into = saturate( dot( -V, L ) );
  return uTxTransl * through * ( 0.3 + 0.7 * into * into ) * lightColor * BRDF_Lambert( albedo );
}`)
        .replace('#include <lights_fragment_begin>', THREE.ShaderChunk.lights_fragment_begin.split(RE_DIRECT).join(RE_DIRECT
          + '\n\t\treflectedLight.directDiffuse += txTransl( directLight.direction, directLight.color, geometryNormal, geometryViewDir, material.diffuseColor );'));
    };
    mat.customProgramCacheKey = () => 'txgrass';
    return mat;
  }
  TXT.scatter = function (R, o) {
    o = o || {};
    const kind = o.kind || 'grass', rng = TXT.rng(o.seed || 20260924);
    const area = o.area || [-40, -60, 40, 20], avoid = o.avoid || [], count = o.count || 1500;
    let geo, mat, sc, cols, cast, pool = null;
    if (kind === 'grass') {
      geo = tuftGeometry(rng, o.blades || 9); sc = o.scale || [0.55, 1.15]; cast = false;
      cols = o.colors || [0xb9a86a, 0xa39a5e, 0x8f8a52, 0xc4b27a, 0x7e7a48];
      mat = grassMaterial(o.translucency != null ? o.translucency : 0.65);
      /* A POOL OF TUFTS (2026-10-03). Every instance drew the same nine blades, and the craft judge
       * named "one repeated tuft sprite" in every round of carousel no. 39. Rotation and scale do
       * not hide one silhouette repeated nine thousand times. So the field draws from `variants`
       * tufts with their own blade counts. They come from their own stream, so the placement below
       * is the one every existing chassis was framed on, and the first tuft is the old one. */
      const nv = Math.max(1, Math.min(8, Math.round(o.variants != null ? o.variants : 5)));
      if (nv > 1) {
        const vr = TXT.rng((o.seed || 20260924) + 7919), b = o.blades || 9;
        pool = [geo];
        for (let v = 1; v < nv; v++) pool.push(tuftGeometry(vr, Math.max(4, Math.round(b * (0.6 + 0.9 * vr())))));
      }
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
    const pick = pool ? TXT.rng((o.seed || 20260924) + 104729) : null, which = [];
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
      if (pool) which.push(Math.floor(pick() * pool.length));
      placed++;
    }
    mesh.count = placed;
    mesh.castShadow = cast; mesh.receiveShadow = true;
    mesh.instanceMatrix.needsUpdate = true; if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    if (!pool) { mesh.userData.txScatter = kind; R.scene.add(mesh); return mesh; }
    /* ONE InstancedMesh PER TUFT, in a group. The group takes a rotation or a visibility the way
     * the single mesh did, and every child is still an InstancedMesh, which is what the weathering
     * pass skips and what the sky and LOD measurements read instance by instance. */
    const group = new THREE.Group();
    group.userData.txScatter = kind;
    pool.forEach((g, v) => {
      const idx = []; for (let i = 0; i < placed; i++) if (which[i] === v) idx.push(i);
      if (!idx.length) return;
      const part = new THREE.InstancedMesh(g, mat, idx.length);
      idx.forEach((i, j) => {
        mesh.getMatrixAt(i, m4); part.setMatrixAt(j, m4);
        mesh.getColorAt(i, color); part.setColorAt(j, color);
      });
      part.castShadow = cast; part.receiveShadow = true;
      part.instanceMatrix.needsUpdate = true; if (part.instanceColor) part.instanceColor.needsUpdate = true;
      group.add(part);
    });
    mesh.dispose();
    R.scene.add(group);
    return group;
  };

  return TXT;
}
