/* txsurface.js, THE SURFACE PASS: every material gets a real surface, every primitive a real edge
 * (owner, 2026-11-15: "10x upgrade it all").
 *
 * WHY THIS EXISTS. The bespoke proof (examples/bespoke-proof/2026-11-14) gave nine artists one
 * frame each and nine cold critics scored them 5.8 to 7.2. Every critic named the same thing: the
 * MATERIALS. Cloth that reads as satin plastic, metal that is one flat grey, a cylinder with a
 * knife edge, a box with no highlight on its corner. 22,000 lines of kit models carried colour,
 * metalness and roughness and almost nothing else: 9 colour textures in the whole kit, no normal
 * map, no relief, no edge. A model is only as good as the light its surface returns, and these
 * surfaces returned one value each.
 *
 * WHAT IT DOES, once, inside TXT.snapshot, to every mesh the frame built (kit models, chassis
 * models and an artist's own primitives alike), so no deck has to remember to ask:
 *
 *   SURFACE  Each opaque MeshStandardMaterial / MeshPhysicalMaterial gets a SURFACE CLASS and a
 *            procedural micro surface written into its shader: relief (a height field turned into
 *            a perturbed normal, in metres, from the surface's own object-space position, so it
 *            needs no UVs and keeps its real size at any scale), roughness that varies the way
 *            the real surface's does, and albedo that is never one flat value. Classes:
 *              brushed   rolled and brushed metal: directional grain, streaked roughness
 *              cast      cast, galvanised or machined-and-weathered metal: spangle, pitting
 *              paint     painted metal, car paint, gloss plastic: orange peel, smudges, dust
 *              plastic   matte moulded plastic: fine grain
 *              rubber    tyres, hoses, gaskets: grain and a dusty bloom
 *              mineral   concrete, stone, clay, plaster, dirt, ceramic: aggregate, pores, mottle
 *              fabric    shirts, trousers, upholstery: woven threads, heather, a cloth sheen
 *              skin      faces and hands: pores, a softer roughness
 *              glass     glazing, lenses, screens: smudges in the roughness only
 *              mapped    any surface that carries a colour map (brick, siding, wood, shingle):
 *                        relief from the map's own light and dark, plus mineral grain
 *            The class comes from the material's name (every K.mat key is a name: 'p-denim',
 *            'v-tyre', 'shop_alu'), else from its metalness, roughness and transparency.
 *   EDGE     Every BoxGeometry is rebuilt as a rounded box with a small real bevel, every closed
 *            CylinderGeometry as a lathe with rounded rims, and low-segment cylinders and spheres
 *            are given enough segments to read round. The bounding box does not change, so no
 *            placement, contact or size gate moves. Thin struts, wires and open tubes are left.
 *
 * Both fade with distance: relief finer than a pixel is faded out per octave, so a far skyline
 * does not shimmer and a hero at 40 cm shows its threads.
 *
 * OPTING OUT. `mesh.userData.txSurface = false` or `material.userData.txSurface = false` leaves a
 * mesh or material exactly as built; `mesh.userData.txBevel = false` keeps its geometry. A deck
 * can name a class itself: `material.userData.txSurface = 'brushed'` (any class above), and scale
 * the relief with `material.userData.txRelief = 1.6`. `R.surface = false` turns the pass off for a
 * whole frame. TXT.surface(R) runs it by hand; TXT.surfaceClass(material) says what a material
 * would get.
 */
export function installSurface(THREE, TXT) {
  const CLASSES = ['none', 'brushed', 'cast', 'paint', 'plastic', 'rubber', 'mineral', 'fabric', 'skin', 'glass', 'mapped'];
  const ID = Object.fromEntries(CLASSES.map((c, i) => [c, i]));

  /* ---- classification --------------------------------------------------------------------- */
  // Keyword table, first match wins, read against the material's name (K.mat's key).
  const WORDS = [
    ['none', /hair|brow|lash|iris|pupil|sclera|eye|tooth|teeth|tongue|nail|glow|emis|lit\b|neon|led\b|flame|fire|smoke|cloud|sky|water|foliage|leaf|grass/],
    ['glass', /glass|glaz|lens|screen|window|wscreen|visor|mirror|clear|lamp-?cover|pane|vial|petri|bottle/],
    ['skin', /skin|face|hand|lip|ear\b|nose/],
    ['fabric', /cloth|shirt|pant|trouser|jean|denim|jacket|coat|suit|dress|plaid|fabric|uniform|hivis|vinyl|seat|cushion|uphol|curtain|canvas|tarp|felt|carpet|rug|textile|sleeve|collar|lapel|tie\b|scarf|cap\b|hat\b|hatband|belt|strap|webbing|mesh-?fab|sock|lace|band\b|bill\b|crumple/],
    ['rubber', /rubber|tyre|tire|tread|hose|gasket|seal\b|grommet|bumper-?rub|sole|cord|cable-?jack|wire-?jack/],
    ['mineral', /conc|cement|stone|rock|brick|grout|mortar|plaster|stucco|caliche|dirt|soil|mud|sand|clay|ceramic|porc|tile|asph|gravel|plinth|curb|pad\b|slab|rip-?stone|fines|powder|limestone|granite|marble|terrazzo/],
    ['brushed', /alu|alumin|brush|stainless|steelw|chrome|nickel|anod|satin|titan|machin|bright-?metal|polish/],
    ['cast', /galv|iron|cast|forg|rust|steel|metal|rail|pipe|bolt|nut\b|rebar|beam|girder|frame|bracket|copper|\bcu\b|brass|bronze|lead|zinc|spangle|graphite|carbide|flute/],
    ['paint', /paint|primer|coat|gloss|enamel|lacquer|body|livery|car\b|trim|panel|hood|door|fender|cab\b|dash/],
    ['plastic', /plastic|abs\b|poly|nylon|resin|housing|case|shell|knob|btn|button|key\b|bezel|cover|moulded|molded|matte/],
    ['mapped', /wood|timber|plank|bark|oak|pine|shingle|siding/],
  ];
  function surfaceClass(mat, mesh) {
    if (!mat || Array.isArray(mat)) return 'none';
    const u = mat.userData || {};
    if (u.txSurface === false || (mesh && mesh.userData && mesh.userData.txSurface === false)) return 'none';
    if (typeof u.txSurface === 'string' && ID[u.txSurface] != null) return u.txSurface;
    if (!mat.isMeshStandardMaterial) return 'none';            // physical extends standard
    if (mat.wireframe || mat.bumpMap || mat.displacementMap) return 'none';   // a normal map is fine: our bump rides on top of it
    // a lamp, a screen glow, a sign face: light it gives, not light it returns
    if (mat.emissive && mat.emissiveIntensity > 0.6 && mat.emissive.getHSL({ h: 0, s: 0, l: 0 }).l > 0.2 &&
        mat.color.getHSL({ h: 0, s: 0, l: 0 }).l < 0.12) return 'none';
    const name = (mat.name || '').toLowerCase();
    if (mat.transmission > 0 || (mat.transparent && mat.opacity < 0.95)) return 'glass';
    for (const [cls, re] of WORDS) if (name && re.test(name)) {
      if (cls === 'none') return 'none';
      // a word for metal on a material that is plainly painted (low metalness) reads as paint
      if ((cls === 'brushed' || cls === 'cast') && mat.metalness < 0.3) return mat.roughness < 0.6 ? 'paint' : 'cast';
      return cls;
    }
    // a painted tank with a weathering atlas is still painted steel; only a rough, dull map is wood or board
    if (mat.map && mat.metalness < 0.25 && mat.roughness >= 0.6) return 'mapped';
    if (mat.metalness >= 0.6) return mat.roughness < 0.4 ? 'brushed' : 'cast';
    if (mat.metalness >= 0.25) return 'paint';
    if (mat.clearcoat > 0.5 && mat.roughness < 0.15) return 'glass';
    if (mat.roughness < 0.45) return 'paint';
    if (mat.roughness < 0.7) return 'plastic';
    return 'mineral';
  }
  TXT.surfaceClass = surfaceClass;

  /* ---- the shader ------------------------------------------------------------------------- */
  // Per class: [relief slope, albedo variation, roughness variation, base frequency (1/m)]
  const PARAMS = {
    brushed: [0.10, 0.08, 0.14, 1400],
    cast:    [0.11, 0.12, 0.15, 300],
    paint:   [0.05, 0.05, 0.08, 420],
    plastic: [0.07, 0.06, 0.07, 900],
    rubber:  [0.10, 0.12, 0.10, 700],
    mineral: [0.22, 0.16, 0.08, 120],
    fabric:  [0.22, 0.12, 0.06, 620],
    skin:    [0.025, 0.05, 0.06, 1100],
    glass:   [0.0, 0.0, 0.04, 30],
    mapped:  [0.30, 0.06, 0.06, 160],
  };

  const PARS_V = `
varying vec3 vTxsP; varying vec3 vTxsN; varying float vTxsUp;`;
  const MAIN_V = `
{ vec3 txsS = vec3(length(modelMatrix[0].xyz), length(modelMatrix[1].xyz), length(modelMatrix[2].xyz));
  vTxsP = transformed * txsS; vTxsN = normalize(objectNormal);
  vTxsUp = normalize(mat3(modelMatrix) * objectNormal).y; }`;

  const PARS_F = `
varying vec3 vTxsP; varying vec3 vTxsN; varying float vTxsUp;
uniform vec4 uTxsA;   // class, relief slope, albedo var, roughness var
uniform vec4 uTxsB;   // base frequency, seed, relief scale, unused
float txsH(vec3 p) { p = fract(p * 0.3183099 + vec3(0.71, 0.113, 0.419)); p *= 17.0;
  return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
float txsN(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  return mix(mix(mix(txsH(i), txsH(i + vec3(1,0,0)), f.x), mix(txsH(i + vec3(0,1,0)), txsH(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(txsH(i + vec3(0,0,1)), txsH(i + vec3(1,0,1)), f.x), mix(txsH(i + vec3(0,1,1)), txsH(i + vec3(1,1,1)), f.x), f.y), f.z); }
// an octave's weight: 1 while it spans several pixels, 0 once it is finer than one
float txsW(float freq, float pw) { return 1.0 - smoothstep(0.3, 0.75, pw * freq); }
bool txsDone = false; float txsHt = 0.0; float txsAl = 0.0; float txsRo = 0.0; float txsSheen = 0.0;
void txsEval() {
  if (txsDone) return; txsDone = true;
  int cls = int(uTxsA.x + 0.5);
  vec3 p = vTxsP + uTxsB.y; vec3 an = abs(vTxsN);
  float pw = max(length(fwidth(vTxsP)), 1e-6);
  float f = uTxsB.x, slope = uTxsA.y * uTxsB.z;
  float h = 0.0, al = 0.0, ro = 0.0;
  // THREE SCALES ON EVERY CLASS. Micro (threads, peel, pits) shows only on a hero close up and is
  // faded once it is finer than a pixel; meso (centimetres: streaks, heather, blotches, creases)
  // and macro (decimetres: wear, oxidation, dust) are what a frame at 432 px actually shows.
  bool top = an.y > max(an.x, an.z);
  vec2 q = top ? p.xz : (an.x > an.z ? p.zy : p.xy);      // the plane a face lies in
  if (cls == 1) {                       // brushed: grain along the face's horizontal
    vec3 s = top ? vec3(1.0, 1.0, 1.0) : (an.x > an.z ? vec3(0.0, 1.0, 0.0) : vec3(0.0, 1.0, 0.0));
    vec3 st = top ? vec3(0.06, 1.0, 1.0) : (an.x > an.z ? vec3(1.0, 1.0, 0.06) : vec3(0.06, 1.0, 1.0));
    float g = txsN(p * st * f) * txsW(f, pw) + 0.5 * txsN(p * st * f * 2.7) * txsW(f * 2.7, pw);
    float meso = txsN(p * st * 40.0) * 0.6 + txsN(p * st * 110.0) * 0.4 * txsW(110.0, pw);
    float mac = txsN(p * 2.5);
    h = g / (6.2831 * f) + 0.15 * meso / (6.2831 * 40.0);
    al = (meso - 0.5) * 0.9 + (mac - 0.5) * 0.7;
    ro = (meso - 0.5) * 1.4 + (mac - 0.5) * 0.9;
  } else if (cls == 2) {                // cast / galvanised: spangle crystals, pits, oxidation
    float sp = txsN(p * 38.0); float cell = floor(sp * 6.0) / 6.0;
    float pit = txsN(p * f) * txsW(f, pw) + 0.5 * txsN(p * f * 3.1) * txsW(f * 3.1, pw);
    float ox = smoothstep(0.5, 0.85, txsN(p * 3.0) * 0.65 + txsN(p * 14.0) * 0.35);
    h = pit / (6.2831 * f) + 0.3 * txsN(p * 60.0) / (6.2831 * 60.0);
    al = (cell - 0.5) * 0.9 + (txsN(p * 1.5) - 0.5) * 0.8 - ox * 0.9;
    ro = (cell - 0.5) * 0.8 + ox * 1.2 + (txsN(p * 6.0) - 0.5) * 0.6;
  } else if (cls == 3) {                // paint: orange peel, panel ripple, smudges, dust
    float pe = txsN(p * f) * txsW(f, pw) + 0.4 * txsN(p * f * 2.3) * txsW(f * 2.3, pw);
    float rip = txsN(p * vec3(9.0, 4.0, 9.0));
    h = pe / (6.2831 * f) + 0.6 * rip / (6.2831 * 9.0);
    float sm = txsN(p * 4.0) * 0.6 + txsN(p * 16.0) * 0.4;
    float dust = smoothstep(0.5, 0.95, vTxsUp) * (0.55 + 0.45 * txsN(p * 11.0));
    al = (txsN(p * 1.3) - 0.5) * 0.7 + dust * 1.2;
    ro = (sm - 0.5) * 2.2 + dust * 2.0;
  } else if (cls == 4 || cls == 5) {    // plastic, rubber: grain and moulding flow; rubber blooms
    float gr = txsN(p * f) * txsW(f, pw) + 0.5 * txsN(p * f * 2.9) * txsW(f * 2.9, pw);
    float flow = txsN(p * 22.0);
    h = gr / (6.2831 * f) + 0.3 * flow / (6.2831 * 22.0);
    al = (txsN(p * 3.0) - 0.5) * 0.8 + (flow - 0.5) * 0.5;
    ro = (txsN(p * 5.0) - 0.5) * 1.5 + (flow - 0.5) * 0.8;
    if (cls == 5) { float bl = smoothstep(0.42, 0.8, txsN(p * 2.2) * 0.7 + txsN(p * 9.0) * 0.3); al += bl * 1.4; ro += bl * 1.2; }
  } else if (cls == 6 || cls == 10) {   // mineral (and the grain under a mapped surface)
    float o1 = txsN(p * f * 0.04), o2 = txsN(p * f * 0.33), o3 = txsN(p * f) * txsW(f, pw),
          o4 = txsN(p * f * 4.1) * txsW(f * 4.1, pw);
    float pore = smoothstep(0.72, 0.9, txsN(p * f * 2.2)) * txsW(f * 2.2, pw);
    float stain = smoothstep(0.55, 0.9, txsN(p * 1.1) * 0.7 + txsN(p * 5.0) * 0.3);
    h = (o2 * 2.5 / (6.2831 * f * 0.33) + o3 / (6.2831 * f) + 0.5 * o4 / (6.2831 * f * 4.1)) * 0.5 - pore * 0.4 / (6.2831 * f * 2.2);
    al = (o1 - 0.5) * 1.2 + (o2 - 0.5) * 0.7 - pore * 0.9 - stain * 0.6;
    ro = (o2 - 0.5) + (o1 - 0.5) - stain * 0.4;
  } else if (cls == 7) {                // fabric: twill weave, heather, gravity creases, a sheen
    vec2 w = q * f; float ww = txsW(f, pw);
    float warp = sin(w.x * 6.2831 + floor(w.y) * 1.5708), weft = sin(w.y * 6.2831);
    float weave = (0.5 + 0.5 * warp * sign(sin(w.y * 3.1416 + floor(w.x * 2.0) * 1.5708))) * 0.6 + 0.4 * (0.5 + 0.5 * weft);
    // creases hang: long along the vertical, narrow across it
    float cr = txsN(p * vec3(14.0, 2.2, 14.0)) * 0.7 + txsN(p * vec3(34.0, 5.0, 34.0)) * 0.3 * txsW(34.0, pw);
    float hz = txsN(p * 26.0) * 0.6 + txsN(p * 90.0) * 0.4 * txsW(90.0, pw);
    h = weave * ww / (6.2831 * f) + 2.4 * cr / (6.2831 * 14.0);
    al = (hz - 0.5) * 1.1 + (weave - 0.5) * 0.5 * ww + (cr - 0.5) * 0.6;
    ro = (hz - 0.5) * 0.8; txsSheen = 1.0;
  } else if (cls == 8) {                // skin: pores, a softer, varied roughness, faint flush
    float po = txsN(p * f) * txsW(f, pw);
    h = po / (6.2831 * f) + 0.2 * txsN(p * 80.0) / (6.2831 * 80.0);
    al = (txsN(p * 25.0) - 0.5) * 0.8; ro = (txsN(p * 40.0) - 0.5) * 1.2 + (txsN(p * 9.0) - 0.5);
  } else if (cls == 9) {                // glass: smudges and fingerprints, nothing else
    float sm = txsN(p * f) * 0.6 + txsN(p * f * 4.0) * 0.4;
    ro = smoothstep(0.45, 0.85, sm) * 1.5;
  }
  txsHt = h * slope; txsAl = al * uTxsA.z; txsRo = ro * uTxsA.w;
}
vec3 txsPerturb(vec3 sp, vec3 sn, vec2 dh, float fd) {
  vec3 sx = dFdx(sp), sy = dFdy(sp); vec3 r1 = cross(sy, sn), r2 = cross(sn, sx);
  float det = dot(sx, r1) * fd; vec3 grad = sign(det) * (dh.x * r1 + dh.y * r2);
  return normalize(abs(det) * sn - grad);
}`;

  const COLOR_F = `
txsEval();
diffuseColor.rgb = clamp(diffuseColor.rgb * (1.0 + txsAl), 0.0, 1.0);`;
  const ROUGH_F = `
txsEval();
roughnessFactor = clamp(roughnessFactor + txsRo, 0.03, 1.0);`;
  // the mapped class takes relief from the map's own light and dark
  const NORMAL_F = `
txsEval();
{ float txsHh = txsHt;
#ifdef USE_MAP
  if (int(uTxsA.x + 0.5) == 10) { vec3 tm = texture2D(map, vMapUv).rgb; txsHh += dot(tm, vec3(0.299, 0.587, 0.114)) * 0.004 * uTxsB.z; }
#endif
  if (abs(uTxsA.y) > 0.0) normal = txsPerturb(-vViewPosition, normal, vec2(dFdx(txsHh), dFdy(txsHh)), faceDirection);
  // cloth returns more light at a grazing angle than a plastic does: the sheen of a fibre
  if (txsSheen > 0.5) { float txsNv = clamp(dot(normal, normalize(vViewPosition)), 0.0, 1.0);
    diffuseColor.rgb = clamp(diffuseColor.rgb * (1.0 + 0.45 * pow(1.0 - txsNv, 3.0)), 0.0, 1.0); }
}`;

  function patch(sh, cls, mat) {
    const P = PARAMS[cls];
    const u = mat.userData || {};
    sh.uniforms.uTxsA = { value: new THREE.Vector4(ID[cls], P[0], P[1], P[2]) };
    sh.uniforms.uTxsB = { value: new THREE.Vector4(P[3], (u.txSeed || 0) * 0.137, u.txRelief != null ? u.txRelief : 1, 0) };
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>' + PARS_V)
      .replace('#include <begin_vertex>', '#include <begin_vertex>' + MAIN_V);
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>' + PARS_F)
      .replace('#include <color_fragment>', '#include <color_fragment>' + COLOR_F)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>' + ROUGH_F)
      .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>' + NORMAL_F);
  }

  /* One material, one class, patched once. Its own hook (a kit model's hair normals, TXT.weather's
   * grime, the contact wear) runs first, as TXT.weather keeps it. */
  function adopt(mat, cls) {
    if (mat.userData.txSurfaced) return mat;
    const has = (k) => Object.prototype.hasOwnProperty.call(mat, k);
    const own = has('onBeforeCompile') ? mat.onBeforeCompile : null;
    const ownKey = has('customProgramCacheKey') ? mat.customProgramCacheKey : null;
    mat.onBeforeCompile = (sh, r) => { if (own) own.call(mat, sh, r); patch(sh, cls, mat); };
    mat.customProgramCacheKey = () => (ownKey ? ownKey.call(mat) : '') + '|txs-' + cls;
    mat.userData.txSurfaced = cls;
    mat.needsUpdate = true;
    return mat;
  }

  /* ---- edges -------------------------------------------------------------------------------- */
  const BEVELLED = new WeakMap();
  function bevelBox(g) {
    const p = g.parameters, m = Math.min(p.width, p.height, p.depth);
    // a real edge: 4 percent of the smallest side, at least 1.5 mm, at most 2.5 cm
    const r = Math.min(0.025, Math.max(0.0015, m * 0.04));
    if (m < 0.004 || r >= m / 2) return null;
    const ng = TXT.roundedBox(p.width, p.height, p.depth, r, null, { segments: m > 0.3 ? 3 : 2 });
    return ng;
  }
  function bevelCylinder(g) {
    const p = g.parameters;
    if (p.openEnded || p.thetaLength < Math.PI * 2 - 1e-6) return null;
    const rmax = Math.max(p.radiusTop, p.radiusBottom), rmin = Math.min(p.radiusTop, p.radiusBottom);
    if (rmax < 0.012 || p.height < 0.004) return null;
    const seg = Math.max(p.radialSegments, rmax > 0.25 ? 72 : rmax > 0.06 ? 48 : 32);
    // a strut, a wire, a lattice bar keeps its facets: the builder chose them, and there are many
    if (p.radialSegments < 10) return null;
    const e = Math.min(0.02, Math.max(0.001, Math.min(rmin > 0 ? rmin : rmax, p.height) * 0.06));
    const h2 = p.height / 2, rt = p.radiusTop, rb = p.radiusBottom, pts = [];
    const arc = (cx, cy, a0, a1) => { for (let i = 0; i <= 4; i++) { const a = a0 + (a1 - a0) * i / 4; pts.push(new THREE.Vector2(cx + Math.cos(a) * e, cy + Math.sin(a) * e)); } };
    pts.push(new THREE.Vector2(0, -h2));
    if (rb > e * 1.5) arc(rb - e, -h2 + e, -Math.PI / 2, 0); else pts.push(new THREE.Vector2(rb, -h2));
    if (rt > e * 1.5) arc(rt - e, h2 - e, 0, Math.PI / 2); else pts.push(new THREE.Vector2(rt, h2));
    pts.push(new THREE.Vector2(0, h2));
    const lg = new THREE.LatheGeometry(pts, seg);
    // three's cylinder starts its seam on +z, the lathe on +x: turn it so a cut, a label or a notch
    // a builder placed by angle stays where it was put
    lg.rotateY(Math.PI / 2 - (p.thetaStart || 0));
    lg.computeVertexNormals();
    return lg;
  }
  function roundSphere(g) {
    const p = g.parameters;
    if (p.radius < 0.02 || (p.widthSegments >= 48 && p.heightSegments >= 32)) return null;
    if (p.phiLength < Math.PI * 2 - 1e-6 || p.thetaLength < Math.PI - 1e-6) return null;
    if (p.widthSegments < 8) return null;          // a deliberate low-poly gem or node
    return new THREE.SphereGeometry(p.radius, Math.max(p.widthSegments, 48), Math.max(p.heightSegments, 32));
  }
  function edge(mesh) {
    if (mesh.userData.txBevel === false || mesh.userData.txGround) return;
    const g = mesh.geometry;
    if (!g || !g.parameters) return;
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    // a mapped or back-faced material (a label, a sky box, a room shell) keeps three's own UVs
    if (mats.some((m) => !m || m.map || m.side === THREE.BackSide || m.isMeshBasicMaterial)) return;
    if (Array.isArray(mesh.material) || g.groups.length > 1) return;
    let ng = BEVELLED.get(g);
    if (ng === undefined) {
      ng = g.type === 'BoxGeometry' ? bevelBox(g) : g.type === 'CylinderGeometry' ? bevelCylinder(g)
         : g.type === 'SphereGeometry' ? roundSphere(g) : null;
      BEVELLED.set(g, ng);
    }
    if (ng) { mesh.geometry = ng; mesh.userData.txBevelled = g.type; }
  }

  /* ---- the pass ------------------------------------------------------------------------------ */
  TXT.surface = function (R) {
    if (!R || R.surface === false) return { surfaced: 0, bevelled: 0 };
    let surfaced = 0, bevelled = 0;
    const seen = new Set();
    R.scene.traverse((m) => {
      if (!m.isMesh || m.isSkinnedMesh) return;
      const u = m.userData || {};
      if (u.txSurface === false || u.txGround || u.txScatter || u.txSky) return;
      if (!m.isInstancedMesh) { const before = m.geometry; edge(m); if (m.geometry !== before) bevelled++; }
      const mats = Array.isArray(m.material) ? m.material : [m.material];
      mats.forEach((mat) => {
        if (!mat || seen.has(mat)) return;
        seen.add(mat);
        const cls = surfaceClass(mat, m);
        if (cls !== 'none' && !mat.userData.txSurfaced) { adopt(mat, cls); surfaced++; }
      });
    });
    R._txSurface = { surfaced, bevelled };
    return R._txSurface;
  };
  TXT.SURFACE_CLASSES = CLASSES.slice(1);
}
