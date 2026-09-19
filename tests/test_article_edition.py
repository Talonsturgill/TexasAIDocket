"""The web edition keeps its evidence intact and rejects unsupported source references."""
import copy
import html
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "site"))

from site_context import load_runs
from site_pages.article_edition import _block, _expand, load_edition, render, validate


class ArticleEditionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article_run = next(run for run in load_runs() if run["date"] == "2026-09-18")
        cls.claims = {claim["id"]: claim for claim in cls.article_run["claims"]}
        cls.edition = json.loads((ROOT / "ledger/articles/2026-09-18.json").read_text())
        cls.items = json.loads((ROOT / "ledger/docket.json").read_text())["items"]

    def test_sources_and_verification_are_preserved(self):
        doc = render(self.article_run, "2026-09-18", self.items)
        sources_html = re.search(r'<ul class="edition-source-list"[^>]*>(.*?)</ul>', doc, re.S).group(1)
        sources = [html.unescape(url) for url in re.findall(r'href="([^"]+)"', sources_html)]
        self.assertEqual(set(sources), {c["url"] for c in self.claims.values()})
        self.assertEqual(len(sources), len({c["url"] for c in self.claims.values()}))
        self.assertEqual(len(re.findall(r'<li id="claim-', doc)), len(self.claims))
        self.assertIn('<details class="edition-verified">', doc)
        self.assertEqual(len(re.findall(r'<li><a href="../../item/', doc)), len(self.edition["related"]))
        for claim in self.claims.values():
            quote = re.search(f'<li id="claim-{claim["id"]}">.*?<blockquote>(.*?)</blockquote>', doc, re.S).group(1)
            self.assertEqual(html.unescape(quote), claim["quote"])
        story = re.search(r'<div class="edition-story prose"[^>]*>(.*?)</div>', doc, re.S).group(1)
        self.assertNotIn("first comment", story)

    def test_numbers_are_formatted_from_claims(self):
        self.assertEqual(_expand("{{date:c1}}", self.claims), "September 1st, 2026")
        self.assertEqual(_expand("{{money:c8}}", self.claims), "$19,200.00")
        changed = copy.deepcopy(self.claims)
        changed["c8"]["quote"] = "in the amount of $21,450.50 for year one"
        self.assertEqual(_expand("{{money:c8}}", changed), "$21,450.50")
        changed["c1"]["text"] = "Meeting on October 2nd, 2027."
        self.assertEqual(_expand("{{date:c1}}", changed), "October 2nd, 2027")

    def test_first_party_label_covers_universities_and_vendors(self):
        for run in load_runs():
            if run["date"] not in {"2026-08-29", "2026-09-18"}:
                continue
            with self.subTest(date=run["date"]):
                doc = render(run, "2026-09-18", self.items)
                sources = re.search(r'<ul class="edition-source-list"[^>]*>(.*?)</ul>', doc, re.S).group(1)
                self.assertIn("First-party account", sources)
                self.assertNotIn("Company account", sources)

    def test_unsupported_claims_links_and_tokens_fail(self):
        for block in [
            {"text": "Unsupported.", "claims": []},
            {"text": "Unsupported.", "claims": ["c999"]},
            {"text": "[Unbound link](c2)", "claims": ["c1"]},
            {"text": "{{money:c8}}", "claims": ["c1"]},
            {"text": "{{unknown}}", "claims": ["c1"]},
        ]:
            with self.subTest(block=block), self.assertRaises(ValueError):
                _block(block, self.claims)

    def test_copy_is_escaped_and_sources_require_http(self):
        rendered = _block({"text": "<script>alert('copy')</script>", "claims": ["c1"]}, self.claims)
        self.assertNotIn("<script>", rendered)
        claims = copy.deepcopy(self.claims)
        claims["c1"]["url"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            _block({"text": "[Source](c1)", "claims": ["c1"]}, claims)

    def test_related_record_must_exist(self):
        with self.assertRaises(ValueError):
            render(self.article_run, "2026-09-18", [])

    def test_missing_edition_is_a_build_failure(self):
        with self.assertRaisesRegex(ValueError, "Missing authored article"):
            load_edition({"date": "2000-01-01"})

    def test_incomplete_or_social_copy_is_rejected(self):
        for field, value in [("introduction", []), ("sections", []), ("section", "")]:
            edition = copy.deepcopy(self.edition)
            edition[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(self.article_run, edition)
        edition = copy.deepcopy(self.edition)
        edition["dek"]["text"] = "Sources in the first comment."
        with self.assertRaises(ValueError):
            validate(self.article_run, edition)

    def test_quoted_numeric_token_is_source_driven(self):
        claims = {"c1": {"quote": "Measured 71% over 2021 to 2024."}}
        self.assertEqual(_expand("{{number:c1}}", claims), "71%")
        self.assertEqual(_expand("{{number:c1:1}}", claims), "2021")
        with self.assertRaises(ValueError):
            _expand("{{number:c1:7}}", claims)

    def test_envelope_and_search_description_are_required(self):
        edition = copy.deepcopy(self.edition)
        del edition["_spec"]
        with self.assertRaisesRegex(ValueError, "_spec"):
            validate(self.article_run, edition)
        for text in ["Too short.", "A long description. " * 20]:
            edition = copy.deepcopy(self.edition)
            edition["dek"]["text"] = text
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "search description"):
                validate(self.article_run, edition)

    def test_every_shipped_date_has_a_complete_article(self):
        runs = load_runs()
        self.assertGreater(len(runs), 1)
        for run in runs:
            with self.subTest(date=run["date"]):
                doc = render(run, "2026-09-18", self.items)
                self.assertIn('class="article-edition"', doc)
                self.assertEqual(doc.count('<li id="claim-'), len(run["claims"]))
                self.assertEqual(doc.count('class="edition-slide"'), len(run["files"]))
                for claim in run["claims"]:
                    if claim.get("quote"):
                        quoted = re.search(f'<li id="claim-{claim["id"]}">.*?<blockquote>(.*?)</blockquote>', doc, re.S).group(1)
                        self.assertEqual(html.unescape(quoted), claim["quote"])


if __name__ == "__main__":
    unittest.main()
