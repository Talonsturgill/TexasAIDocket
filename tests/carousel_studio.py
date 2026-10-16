"""Replay the missed hardest-frame audition and the October 16th compression defect."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import art_preflight as art
import depth_floor
import layout_check
import print_ban
import ship_images
import studio_clock


class Studio(unittest.TestCase):
    def test_clock_resumes_without_restarting(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            path = Path(tmp) / "studio_clock.json"
            start = dt.datetime(2026, 10, 17, 6, tzinfo=dt.timezone.utc)
            with self.assertRaises(ValueError):
                studio_clock.stamp(path, "art_done", start)
            studio_clock.stamp(path, "wake", start)
            studio_clock.stamp(path, "wake", start + dt.timedelta(hours=1))
            doc = studio_clock.stamp(path, "art_done", start + dt.timedelta(minutes=70))
            self.assertEqual(studio_clock.elapsed(doc)["art_done"], 70)

    def test_relief_cannot_pass_on_an_import_or_flat_pixels(self):
        source = '<script src="@@ASSETS@@/js/txbench.js"></script> TXBENCH.relief(cx, opts);'
        self.assertTrue(print_ban.is_rendered(source))
        self.assertFalse(print_ban.is_rendered(source.replace('TXBENCH.relief(cx, opts);', '')))
        proof = {"height_range": 8, "materials": 2, "cast_fraction": 0.12, "area": 0.6}
        mark = lambda p: ["TXBENCH: RELIEF " + json.dumps(p)]
        self.assertEqual(print_ban.place_verdict(mark(proof)), "shown")
        for key, value in (("height_range", 0), ("materials", 1), ("cast_fraction", 0), ("area", 0.05)):
            self.assertEqual(print_ban.place_verdict(mark(proof | {key: value})), "no render")
        self.assertEqual(print_ban.place_verdict(["TXBENCH: RELIEF {}"]), "no render")
        frame = depth_floor.frame_report("slide-01.html", source)
        self.assertEqual(depth_floor.check([frame] * 6, {"min_staged_frames": 5, "min_distinct_cues": 4}), [])

    def test_hardest_frame_and_individual_review_binding(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            base = Path(tmp) / "2026-10-17"
            (base / "slides").mkdir(parents=True)
            (base / "render").mkdir()
            selected = [1, 3, 9]
            for n in selected:
                (base / "slides" / f"slide-{n:02}.html").write_text(f"Frame {n}")
                (base / "render" / f"slide-{n:02}.png").write_bytes(b"reviewed image")
            digests = art.inputs(base, selected, base / "assets")
            plan = {"hardest_frame": 3, "visual_argument": "The creek is the difficult frame",
                    "build_risk": "The bank must remain visible", "distinct_from_recent": "Measured relief"}
            review = {"decision": "accept", "inputs": digests, "frames": [
                {"slide": n, "role": role, "subject": "the actual subject", "visual_consequence": "the distinction reads",
                 "weakness": "none observed", "repair": "none required", "inputs": art.frame_inputs(digests, n),
                 "encoding_reads": True, "dominant_subject_finished": True, "feed_legible": True}
                for n, role in zip(selected, art.ROLES)]}
            record = {"version": 2, "selected": selected, "inputs": digests, "plan": plan, "review": review}
            def save():
                (base / "art_plan.json").write_text(json.dumps(plan))
                (base / "art_preflight.json").write_text(json.dumps(record))
            save()
            self.assertEqual(art.check(base), [])
            plan["hardest_frame"] = 4
            save()
            self.assertIn("hardest frame", " ".join(art.check(base)))
            plan["hardest_frame"] = 3
            (base / "render/slide-09.png").write_bytes(b"a changed close")
            record["inputs"] = art.inputs(base, selected, base / "assets")
            review["inputs"] = record["inputs"]
            save()
            problems = " ".join(art.check(base))
            self.assertIn("frame 9", problems)
            self.assertNotIn("frame 1:", problems)
            self.assertNotIn("frame 3:", problems)
            review["frames"][-1]["inputs"] = art.frame_inputs(record["inputs"], 9)
            review["frames"][-1]["dominant_subject_finished"] = False
            save()
            self.assertIn("dominant_subject_finished", " ".join(art.check(base)))

    def test_a_built_interior_does_not_need_an_artificial_sky(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            base = Path(tmp) / "2026-10-17"
            (base / "slides").mkdir(parents=True)
            source = "import { init } from '@@ASSETS@@/js/txthree.js'; const TXT=init(THREE); TXT.interior(R,{}); TXT.snapshot(R);"
            slides = []
            for n in range(1, 10):
                name = f"slide-{n:02}.html"
                (base / "slides" / name).write_text(source)
                slides.append({"file": name, "console_errors": ["TXT: ROOM IN FRAME"]})
            (base / "render_report.json").write_text(json.dumps({"slides": slides}))
            self.assertEqual(print_ban.check_run(base), [])
            slides[3]["console_errors"] = []
            (base / "render_report.json").write_text(json.dumps({"slides": slides}))
            self.assertIn("no verdict", " ".join(print_ban.check_run(base)))

    def test_compressed_calendar_retains_its_fourth_piece(self):
        from PIL import Image
        archive = ROOT / "runs/carousel/2026-10-16"
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            run = Path(tmp)
            for name in ("storyboard.md", "render_report.json"):
                (run / name).symlink_to(archive / name)
            for path in archive.glob("slide-*.webp"):
                if path.name != "slide-07.webp":
                    (run / path.name).symlink_to(path)
            png = run / "slide-07.png"
            with Image.open(archive / "slide-07.webp") as image:
                image.save(png)
            # Retain exact rejected bytes so libwebp encoder versions cannot change the replay.
            shutil.copyfile(ROOT / "tests/fixtures/2026-10-16-calendar-q82.webp", png.with_suffix('.webp'))
            code, _, _ = layout_check.check(run, image_overrides={7: png.with_suffix('.webp')})
            self.assertEqual(code, 1, 'the real q82 calendar replay fails the shipped layout')
            rows = [{"name": png.name}]
            self.assertEqual(ship_images.preserve_layout(run, [png], rows), [])
            self.assertEqual(rows[0]["quality"], "lossless")
            with Image.open(png) as original, Image.open(png.with_suffix('.webp')) as delivery:
                self.assertEqual(original.convert('RGB').tobytes(), delivery.convert('RGB').tobytes())


if __name__ == "__main__":
    (ROOT / "out").mkdir(exist_ok=True)
    unittest.main()
