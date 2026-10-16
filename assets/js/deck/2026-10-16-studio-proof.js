/* Physics and materials for the engineering study. Each frame authors its own geometry. */
TXDECK.declare({
  world: "machined evidence under a raking key", light: {az: 300, el: 26},
  ground: "dark basalt", material: "ivory ceramic and weathered copper", accent: "#2A7A9E",
  grade: {filmic: false, exposure: 0, saturation: 1, contrast: 1.04,
          aberration: 0, grain: {amount: 0.008, size: 1, seed: 20261016}, vignette: 0.04}
});
window.STUDIO = {
  albedo(X, Y, m) {
    const tooth = 0.96 + 0.04 * Math.sin(X * 1.7 + Math.sin(Y * 0.8));
    const colours = [[0.004, 0.008, 0.012], [0.58, 0.50, 0.36],
      [0.45, 0.16, 0.045], [0.018, 0.15, 0.22], [0.055, 0.055, 0.052]];
    return colours[m].map(v => v * tooth);
  },
  spec: {1: [0.15, 45], 2: [0.65, 65], 3: [0.35, 85], 4: [0.12, 35]}
};
