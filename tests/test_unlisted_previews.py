import importlib.util
import json
import re
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "site"))
import unlisted_previews as preview


class UnlistedPreviewTest(unittest.TestCase):
    def test_approved_payload_is_self_contained_and_non_discoverable(self):
        rows = preview.payloads()
        self.assertTrue(rows)
        for rel, text in rows:
            self.assertFalse(rel.endswith("index.html"))
            preview.validate(Path(rel).name, text)
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
            self.assertEqual(len(blocks), 1)
            metadata = json.loads(blocks[0])
            self.assertEqual(metadata["@type"], "WebPage")
            self.assertEqual(metadata["creator"]["name"], "Texas AI Docket")
            self.assertIn("synthetic concept", metadata["name"])

    def test_missing_robot_or_referrer_controls_block_publication(self):
        rel, text = preview.payloads()[0]
        for bad in [text.replace("noindex,", ""), text.replace("nofollow,", ""),
                    text.replace("noarchive,", ""), text.replace('content="no-referrer"', 'content="origin"'),
                    text.replace("INDEPENDENT CONCEPT", "OWNER REVIEW")]:
            with self.assertRaises(ValueError):
                preview.validate(Path(rel).name, bad)
        with self.assertRaises(ValueError):
            preview.validate("star-precision.html", text)

    def test_sitemap_search_feed_or_robot_reference_is_a_discovery_leak(self):
        rel, text = preview.payloads()[0]
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp:
            root = Path(tmp)
            preview.write(root)
            self.assertEqual(preview.audit_discovery(root)["discovery_leaks"], [])
            for name in ["index.html", "sitemap.xml", "feed.json", "ask-pack.json", "robots.txt"]:
                file = root / name
                file.write_text(f"https://texasaidocket.com/{rel}")
                with self.assertRaises(ValueError):
                    preview.audit_discovery(root)
                file.unlink()
            (root / "index.html").write_text(Path(rel).stem)
            with self.assertRaises(ValueError):
                preview.audit_discovery(root)

    def test_inline_code_tampering_and_network_widening_are_rejected(self):
        rel, text = preview.payloads()[0]
        with self.assertRaises(ValueError):
            preview.validate(Path(rel).name, text.replace("render();", "render();globalThis.injected=true;", 1))
        with self.assertRaises(ValueError):
            preview.validate(Path(rel).name, text.replace("connect-src 'none'", "connect-src *"))


if __name__ == "__main__":
    (ROOT / "out").mkdir(exist_ok=True)
    unittest.main()
