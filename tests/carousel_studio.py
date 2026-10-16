"""Replay the missed hardest-frame audition and the October 16th compression defect."""
from __future__ import annotations

import datetime as dt
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import art_preflight as art
import critic_brief
import depth_floor
import layout_check
import native_crops
import print_ban
import ship_images
import studio_clock


class Studio(unittest.TestCase):
    def test_master_prompt_uses_the_actual_tools(self):
        prompt = (ROOT / "prompts/daily_routine.md").read_text()
        audition = prompt.split("Give `art_preflight.webp`", 1)[1].split("Store that object", 1)[0]
        self.assertIn("`carousel-art-director`", audition)
        self.assertNotIn("`carousel-flow-critic`", audition)
        for field in ("encoding_reads", "dominant_subject_finished", "feed_legible", "inputs"):
            self.assertIn(field, audition)
        wake = prompt.split("Stamp the run's first real checkpoint", 1)[1].split("1. Point git", 1)[0]
        self.assertTrue(set(re.findall(r"`([a-z_]+)`", wake)).issubset(studio_clock.CHECKPOINTS))
        self.assertNotIn("Both critics run on every round", prompt)
        self.assertIn("Never start a second whole-deck flow pass", prompt)

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

    def test_clock_report_refuses_missing_checkpoints(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            path = Path(tmp) / "out/2026-10-17/studio_clock.json"
            start = dt.datetime(2026, 10, 17, 6, tzinfo=dt.timezone.utc)
            studio_clock.stamp(path, "wake", start)
            with mock.patch.object(studio_clock, "ROOT", Path(tmp)), mock.patch.object(
                    sys, "argv", ["studio_clock.py", "--date", "2026-10-17", "--report"]):
                error = io.StringIO()
                with contextlib.redirect_stderr(error), self.assertRaises(SystemExit) as exit_code:
                    studio_clock.main()
                self.assertEqual(exit_code.exception.code, 1)
                for name in studio_clock.CHECKPOINTS[1:]:
                    self.assertIn(name, error.getvalue())
                for minute, name in enumerate(studio_clock.CHECKPOINTS[1:], 1):
                    studio_clock.stamp(path, name, start + dt.timedelta(minutes=minute))
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(studio_clock.main(), 0)
                self.assertEqual(set(json.loads(output.getvalue())["elapsed_minutes_from_wake"]),
                                 set(studio_clock.CHECKPOINTS))

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

    def test_native_tiles_cover_current_pixels_and_reject_stale_evidence(self):
        from PIL import Image
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            render = Path(tmp)
            frame = render / "slide-01.png"
            with Image.open(ROOT / "runs/carousel/2026-10-16/slide-01.webp") as image:
                original = image.convert("RGB")
                original.save(frame)
            self.assertEqual(original.size, (2160, 2700))
            self.assertEqual(native_crops.write(frame, 2)["tiles"], 6)
            tiles = native_crops.read(render, 1)["tiles"]
            self.assertEqual(tiles[0]["design"], [0, 0, 540, 450])
            reconstructed = Image.new("RGB", original.size)
            for tile in tiles:
                with Image.open(tile["path"]) as piece:
                    self.assertLessEqual(piece.width, 1080)
                    self.assertLessEqual(piece.height, 900)
                    reconstructed.paste(piece, tuple(tile["px"][:2]))
            self.assertEqual(original.tobytes(), reconstructed.tobytes())
            manifest = render / "crops/slide-01.json"
            record = json.loads(manifest.read_text())
            manifest.write_text(json.dumps(record | {"tiles": record["tiles"][:-1]}))
            self.assertIn("incomplete", native_crops.read(render, 1)["stale"])
            manifest.write_text(json.dumps(record))
            tile = Path(tiles[0]["path"])
            saved = tile.read_bytes()
            tile.write_bytes(b"unreviewed replacement")
            self.assertIn("stale", native_crops.read(render, 1))
            tile.write_bytes(saved)
            tile.unlink()
            self.assertIn("stale", native_crops.read(render, 1))
            native_crops.write(frame, 2)
            original.putpixel((0, 0), (255, 0, 20))
            original.save(frame)
            stale = native_crops.read(render, 1)
            self.assertIn("source image changed", stale["stale"])
            self.assertNotIn("tiles", stale)
            self.assertTrue(native_crops.write(frame, 2)["ok"])
            self.assertEqual(len(native_crops.read(render, 1)["tiles"]), 6)

    def test_reviewer_brief_uses_real_texas_dossiers(self):
        from PIL import Image
        storyboard = (ROOT / "runs/carousel/2026-10-16/storyboard.md").read_text()
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            render = Path(tmp)
            Image.new("RGB", (160, 180), "navy").save(render / "slide-03.png")
            native_crops.write(render / "slide-03.png", 2)
            blocks, problems = critic_brief.brief(storyboard, render, [3])
            self.assertEqual(problems, [])
            self.assertEqual(len(blocks), 1)
            self.assertTrue(blocks[0]["shot"].startswith("CLOSE"))
            self.assertIn("robotaxi", blocks[0]["largest_object"])
            self.assertIn("Bottom third", blocks[0]["lower_third"])
            self.assertTrue(blocks[0]["showstopper"])
            self.assertIn("slide-03-r1c1.png", critic_brief.render_block(blocks[0]))
            missing, problems = critic_brief.brief(storyboard, render, [4])
            self.assertTrue(problems)
            self.assertNotIn("tiles", missing[0]["native_crops"])

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
                 "weakness": "none observed", "repair": "none required", "inputs": art.frame_inputs(digests, n, base),
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
            review["frames"][-1]["inputs"] = art.frame_inputs(record["inputs"], 9, base)
            review["frames"][-1]["dominant_subject_finished"] = False
            save()
            self.assertIn("dominant_subject_finished", " ".join(art.check(base)))

    def test_asset_change_rechecks_only_frames_that_use_it(self):
        from PIL import Image
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            base = Path(tmp) / "2026-10-17"
            assets = base / "assets"
            for folder in (base / "slides", base / "render", assets / "js"):
                folder.mkdir(parents=True)
            shared = assets / "js/shared.js"
            private = assets / "js/close.js"
            shared.write_text("shared chassis")
            private.write_text("close helper")
            for n in (1, 3, 9):
                html = '<script src="@@ASSETS@@/js/shared.js"></script>'
                if n == 9:
                    html += '<script src="@@ASSETS@@/js/close.js"></script>'
                (base / "slides" / f"slide-{n:02}.html").write_text(html)
                Image.new("RGB", (64, 80), "navy").save(base / "render" / f"slide-{n:02}.png")
            (base / "render/render_report.json").write_text('{"slides": []}')
            (base / "art_plan.json").write_text(json.dumps({"hardest_frame": 3,
                "visual_argument": "A measured distinction", "build_risk": "Light and texture",
                "distinct_from_recent": "A new physical scale"}))
            record_path = base / "art_preflight.json"
            def accept():
                record = json.loads(record_path.read_text())
                record["review"] = {"decision": "accept", "inputs": record["inputs"], "frames": [
                    {"slide": n, "role": role, "subject": "finished subject", "visual_consequence": "the distinction reads",
                     "weakness": "none observed", "repair": "none required", "inputs": record["frame_inputs"][str(n)],
                     "encoding_reads": True, "dominant_subject_finished": True, "feed_legible": True}
                    for n, role in zip((1, 3, 9), art.ROLES)]}
                record_path.write_text(json.dumps(record))
                return record
            # Isolate the receipt refresh from the independently exercised render/value gates.
            with mock.patch("panel_ready.check_renders_current", return_value=[]), mock.patch(
                    "panel_ready.load_machine_qa", return_value=({"verdict": "PASS"}, [])), mock.patch(
                    "value_register.frame_stats", return_value={}), mock.patch("value_register.judge", return_value=[]):
                art.build(base, None, assets)
                old = accept()
                self.assertNotIn("assets/js/close.js", old["frame_inputs"]["1"])
                self.assertIn("assets/js/close.js", old["frame_inputs"]["9"])
                private.write_text("changed close helper")
                art.build(base, None, assets)
                refreshed = json.loads(record_path.read_text())
                self.assertEqual(refreshed["needs_review"], [9])
                self.assertEqual(refreshed["review"]["frames"], old["review"]["frames"][:2])
                accept()
                shared.write_text("changed shared chassis")
                art.build(base, None, assets)
                self.assertEqual(json.loads(record_path.read_text())["needs_review"], [1, 3, 9])

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
                shutil.copyfile(archive / name, run / name)
            for path in archive.glob("slide-*.webp"):
                if path.name != "slide-07.webp":
                    shutil.copyfile(path, run / path.name)
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

    def test_new_ship_refuses_missing_layout_inputs_before_writing(self):
        from PIL import Image
        for missing in (("storyboard.md",), ("render_report.json",), ("storyboard.md", "render_report.json")):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
                run = Path(tmp) / "2026-10-17"
                run.mkdir()
                png = run / "slide-01.png"
                Image.new("RGB", (64, 80), "navy").save(png)
                for name in ("storyboard.md", "render_report.json"):
                    if name not in missing:
                        (run / name).write_text("{}")
                _, problems = ship_images.ship(run, dry=False, lock_root=Path(tmp) / "locks")
                self.assertTrue(problems)
                self.assertTrue(all(name in " ".join(problems) for name in missing))
                self.assertTrue(png.exists())
                self.assertFalse(png.with_suffix(".webp").exists())
                self.assertFalse((run / "og.jpg").exists())


if __name__ == "__main__":
    (ROOT / "out").mkdir(exist_ok=True)
    unittest.main()
