/* ak3d.js — tiny software 3D renderer for Canvas 2D. No GPU, no WebGL, fully
 * deterministic. Purpose-built for static slide artwork: heightfield terrain,
 * meshes, 3D polylines, point clouds — with perspective projection, painter's
 * z-sorting, Lambert shading, and depth fog.
 *
 * Coordinate system: right-handed-ish, +x right, +y UP, +z toward the camera's
 * default facing. The camera looks down -z after yaw/pitch are applied.
 *
 * Quick start:
 *   const cam = TX3D.camera({ pos: [0, 8, 26], yaw: 0, pitch: -0.25, fov: 55,
 *                             w: 1080, h: 1350 });
 *   const mesh = TX3D.heightfield({
 *     xmin: -20, xmax: 20, zmin: -20, zmax: 20, nx: 90, nz: 90,
 *     y: (x, z) => 3 * TX.fbm2(x * 0.08, z * 0.08, { octaves: 5 }),
 *     color: (x, z, y) => TX3D.mix("#12324e", "#dff3ff", Math.min(1, Math.max(0, y / 3)))
 *   });
 *   TX3D.render(ctx, cam, mesh.faces, {
 *     light: [0.5, 1, 0.35], ambient: 0.35,
 *     fog: { color: "#070b16", near: 18, far: 55 },
 *     stroke: "rgba(150,220,255,0.14)"   // optional wireframe overlay
 *   });
 *
 * COMPOSITION MATH (plan the frame before rendering — do not guess):
 *   f = (h/2) / tan(fov/2)                        // focal length in px
 *   horizonY = cy + tan(-pitch) * f               // screen y where camera-height
 *                                                 // geometry converges at distance
 *   A point d units above the camera at distance D projects ~ (d/D)*f px
 *   ABOVE horizonY; below-camera terrain lands below it. Choose pitch/cy so
 *   horizonY sits where the composition wants the ridge line, then size peak
 *   heights via d = (horizonY - targetY) * D / f. Verified: fov 58 -> f=1218;
 *   pitch -0.18, cy=640 -> horizon y~862; peaks 8-14 units above cam at D~40
 *   crest at y~600-620. Wide-angle drama: fov 65-75, camera low (just above
 *   terrain), pitch near 0. Aerial: camera high, pitch -0.5+, cy low.
 */
(function (global) {
  "use strict";

  // ---------- vectors ----------
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const cross = (a, b) => [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const norm = (a) => {
    const l = Math.hypot(a[0], a[1], a[2]) || 1;
    return [a[0] / l, a[1] / l, a[2] / l];
  };

  // ---------- color ----------
  function hex2rgb(h) {
    h = h.replace("#", "");
    if (h.length === 3) h = h.split("").map(c => c + c).join("");
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }
  const rgb2css = (c) => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
  function mixRgb(a, b, t) {
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  }
  function mix(hexA, hexB, t) { return rgb2css(mixRgb(hex2rgb(hexA), hex2rgb(hexB), t)); }
  function scaleRgb(c, k) { return [c[0] * k, c[1] * k, c[2] * k]; }

  // ---------- camera ----------
  function camera(opts) {
    const o = opts || {};
    const cam = {
      pos: o.pos || [0, 6, 24],
      yaw: o.yaw || 0,          // rotation around +y (radians)
      pitch: o.pitch || 0,      // rotation around +x (radians), negative looks down
      fov: (o.fov || 55) * Math.PI / 180,
      w: o.w || 1080,
      h: o.h || 1350,
      near: o.near || 0.5
    };
    cam.f = (cam.h / 2) / Math.tan(cam.fov / 2);
    cam.cy = o.cy !== undefined ? o.cy : cam.h / 2;   // vertical center (shift horizon)
    cam.cx = o.cx !== undefined ? o.cx : cam.w / 2;
    return cam;
  }

  // world → camera space
  function toCam(cam, p) {
    let x = p[0] - cam.pos[0], y = p[1] - cam.pos[1], z = p[2] - cam.pos[2];
    // yaw around y
    const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw);
    let x1 = cy * x - sy * z, z1 = sy * x + cy * z;
    // pitch around x
    const cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
    let y1 = cp * y - sp * z1, z2 = sp * y + cp * z1;
    return [x1, y1, z2];
  }

  // camera space → screen (returns null when behind the near plane)
  function project(cam, pc) {
    const zv = -pc[2];                     // camera looks down -z
    if (zv < cam.near) return null;
    return {
      x: cam.cx + (pc[0] * cam.f) / zv,
      y: cam.cy - (pc[1] * cam.f) / zv,
      z: zv
    };
  }

  const projectWorld = (cam, p) => project(cam, toCam(cam, p));

  // ---------- geometry builders ----------
  /* heightfield: regular grid of quads. y(x, z) gives elevation; color(x, z, y)
   * gives base face color (hex or css). Returns { faces } for render(). */
  function heightfield(o) {
    const faces = [];
    const dx = (o.xmax - o.xmin) / o.nx, dz = (o.zmax - o.zmin) / o.nz;
    const P = (i, j) => {
      const x = o.xmin + i * dx, z = o.zmin + j * dz;
      return [x, o.y(x, z), z];
    };
    for (let j = 0; j < o.nz; j++) {
      for (let i = 0; i < o.nx; i++) {
        const a = P(i, j), b = P(i + 1, j), c = P(i + 1, j + 1), d = P(i, j + 1);
        const cxw = (a[0] + c[0]) / 2, czw = (a[2] + c[2]) / 2, cyw = (a[1] + b[1] + c[1] + d[1]) / 4;
        faces.push({
          pts: [a, b, c, d],
          color: o.color ? o.color(cxw, czw, cyw) : "#5b7d9e",
          doubleSided: true
        });
      }
    }
    return { faces };
  }

  /* box: axis-aligned cuboid centered at c=[x,y,z] with size s=[sx,sy,sz]. */
  function box(c, s, color) {
    const [x, y, z] = c, hx = s[0] / 2, hy = s[1] / 2, hz = s[2] / 2;
    const v = [
      [x - hx, y - hy, z - hz], [x + hx, y - hy, z - hz], [x + hx, y + hy, z - hz], [x - hx, y + hy, z - hz],
      [x - hx, y - hy, z + hz], [x + hx, y - hy, z + hz], [x + hx, y + hy, z + hz], [x - hx, y + hy, z + hz]
    ];
    const q = (a, b, c2, d) => ({ pts: [v[a], v[b], v[c2], v[d]], color });
    return { faces: [q(4, 5, 6, 7), q(1, 0, 3, 2), q(5, 1, 2, 6), q(0, 4, 7, 3), q(7, 6, 2, 3), q(0, 1, 5, 4)] };
  }

  // ---------- renderer ----------
  /* render(ctx, cam, faces, opts)
   *   faces: [{pts: [[x,y,z]x3+], color: hex/css, doubleSided?: bool}]
   *   opts.light: direction TO the light (world), default [0.5, 1, 0.4]
   *   opts.ambient: 0..1 base light, default 0.35
   *   opts.fog: { color, near, far } in camera-distance units (optional)
   *   opts.stroke: css color for wireframe edges (optional)
   *   opts.cull: backface cull single-sided faces, default true
   */
  function render(ctx, cam, faces, opts) {
    const o = opts || {};
    const L = norm(o.light || [0.5, 1, 0.4]);
    const ambient = o.ambient !== undefined ? o.ambient : 0.35;
    const fog = o.fog || null;
    const fogRgb = fog ? hex2rgb(fog.color) : null;

    const drawList = [];
    for (const f of faces) {
      const camPts = f.pts.map(p => toCam(cam, p));
      const scr = camPts.map(p => project(cam, p));
      if (scr.some(s => s === null)) continue;
      const zAvg = scr.reduce((s, p) => s + p.z, 0) / scr.length;

      // world normal for lighting
      const n = norm(cross(sub(f.pts[1], f.pts[0]), sub(f.pts[2], f.pts[0])));
      let lambert = dot(n, L);
      if (f.doubleSided) lambert = Math.abs(lambert);
      else if (o.cull !== false) {
        // backface cull in camera space
        const nc = norm(cross(sub(camPts[1], camPts[0]), sub(camPts[2], camPts[0])));
        if (dot(nc, norm(camPts[0])) > 0) continue;
      }
      const shade = Math.min(1, ambient + Math.max(0, lambert) * (1 - ambient));

      let rgb = typeof f.color === "string" && f.color[0] === "#"
        ? hex2rgb(f.color)
        : (f.rgb || hex2rgb("#5b7d9e"));
      if (typeof f.color === "string" && f.color.startsWith("rgb")) {
        const m = f.color.match(/([\d.]+)[, ]+([\d.]+)[, ]+([\d.]+)/);
        if (m) rgb = [+m[1], +m[2], +m[3]];
      }
      rgb = scaleRgb(rgb, shade);
      if (fog) {
        const t = Math.min(1, Math.max(0, (zAvg - fog.near) / (fog.far - fog.near)));
        rgb = mixRgb(rgb, fogRgb, t);
      }
      drawList.push({ scr, z: zAvg, css: rgb2css(rgb) });
    }

    drawList.sort((a, b) => b.z - a.z);   // painter's: far first
    for (const d of drawList) {
      ctx.beginPath();
      ctx.moveTo(d.scr[0].x, d.scr[0].y);
      for (let i = 1; i < d.scr.length; i++) ctx.lineTo(d.scr[i].x, d.scr[i].y);
      ctx.closePath();
      ctx.fillStyle = d.css;
      ctx.fill();
      if (o.stroke) { ctx.strokeStyle = o.stroke; ctx.lineWidth = o.strokeWidth || 1; ctx.stroke(); }
    }
    return drawList.length;
  }

  /* line3d: project + stroke a world-space polyline. Width can scale with depth.
   * opts: { color, width, depthWidth: [near multiplier, far multiplier], glow } */
  function line3d(ctx, cam, pts, opts) {
    const o = opts || {};
    const proj = pts.map(p => projectWorld(cam, p));
    ctx.strokeStyle = o.color || "#ffffff";
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    for (let i = 0; i < proj.length - 1; i++) {
      const a = proj[i], b = proj[i + 1];
      if (!a || !b) continue;
      let w = o.width || 2;
      if (o.depthWidth) {
        const t = Math.min(1, a.z / (o.depthFar || 60));
        w = w * (o.depthWidth[0] + (o.depthWidth[1] - o.depthWidth[0]) * t);
      }
      ctx.lineWidth = Math.max(0.4, w);
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    }
  }

  /* points3d: project + dot a point cloud. size shrinks with distance.
   * pts: [[x,y,z]], opts: { color | colorFn(p, i, z), size, sizeFar } */
  function points3d(ctx, cam, pts, opts) {
    const o = opts || {};
    for (let i = 0; i < pts.length; i++) {
      const s = projectWorld(cam, pts[i]);
      if (!s) continue;
      const t = Math.min(1, s.z / (o.depthFar || 60));
      const r = (o.size || 3) * (1 - t) + (o.sizeFar || 0.5) * t;
      ctx.fillStyle = o.colorFn ? o.colorFn(pts[i], i, s.z) : (o.color || "#fff");
      ctx.beginPath(); ctx.arc(s.x, s.y, Math.max(0.3, r), 0, Math.PI * 2); ctx.fill();
    }
  }

  global.TX3D = {
    camera, project: projectWorld, render, heightfield, box, line3d, points3d,
    mix, hex2rgb, rgb2css
  };
})(typeof window !== "undefined" ? window : globalThis);
