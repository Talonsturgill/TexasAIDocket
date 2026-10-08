/* Art-direction study. Shared light, materials and type; each frame builds its own image. */
(function (g) {
  'use strict';
  TXDECK.declare({ world: 'port-study', light: { az: 55, el: 8 }, sky: { preset: 'lastLight' },
    ground: '#10151c', material: '#aab2ba', accent: '#ffb54b',
    grade: { exposure: 0.08, saturation: 1.08, contrast: 1.06, filmic: true,
      vignette: 0.10, grain: { amount: 0.012, size: 2, seed: 20261007 },
      bloom: { threshold: 0.85, strength: 0.08, radius: 8 }, dither: true, sharpen: 0.12 } });
  g.STUDY = {
    async boot(THREE, TXT, initKit) {
      await document.fonts.ready;
      TX.fitText(document.querySelector('.hook'), { min: 82, max: 106, maxLines: 3 });
      const h = document.querySelector('.hook'), d = document.querySelector('.dek');
      d.style.top = (h.offsetTop + h.getBoundingClientRect().height + 24) + 'px';
      const F = {"site_side_m":{"value":1838.2,"from":["c2"],"basis":"metres on a side, the site drawn as a square of its own area","rule":"sqrt(acres * 4046.8564224); a drawing rule, the parcel's real shape is not in the record"},"option_side_m":{"value":4219.7,"from":["c3"],"basis":"metres on a side, the option drawn as a square of its own area","rule":"sqrt(acres_option * 4046.8564224); a drawing rule"},"acres":{"value":835,"from":["c2"],"basis":"acres Port Alpha sits on at the Port of Brownsville"},"acres_option":{"value":4400,"from":["c3"],"basis":"acres the site has an option to expand to, nearly"},"crew_drawn":{"value":20,"from":["c29"],"basis":"workers drawn at the hull on frame 8","rule":"a drawing rule, twenty people"},"crew_local_drawn":{"value":7,"from":["c29"],"basis":"of those twenty, the share the 35% local requirement names","rule":"crew_drawn * local_pct / 100"}};
      const gl = document.createElement('canvas'); gl.width = 2160; gl.height = 2700;
      const W = TXT.deckWorld(), R = TXT.setup(gl, { w:1080, h:1350, exposure:W.exposure,
        tone:W.tone, fov:37, near:0.3, far:1200 });
      return { K:initKit(THREE,TXT), F, gl, W, R };
    },
    develop(shot, gl) {
      if (!shot.ok) throw new Error('The study did not render');
      const cx = document.querySelector('#art').getContext('2d');
      cx.setTransform(2,0,0,2,0,0); cx.drawImage(gl,0,0,1080,1350);
      return cx;
    }
  };
})(this);
