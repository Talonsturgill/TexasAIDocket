"""Source contract and negative controls for the bounded document demo."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/site"))
import document_demo as demo


class DocumentDemoTest(unittest.TestCase):
    def setUp(self):
        self.data = demo.load()

    def test_reviewed_source_locations(self):
        self.assertEqual([(r['section'], r['pages']) for r in self.data['entries']], [
            ('III.A.5', [48, 49]), ('III.A.6', [49]), ('III.D.5', [65]),
            ('III.D.6', [65, 66]), ('III.E.5', [69, 70])])
        self.assertEqual(self.data['effective'], '2026-08-14')
        self.assertEqual(self.data['permit'], 'TXR050000')

    def test_negative_controls(self):
        for mutation in ('version', 'host', 'page', 'duplicate', 'section', 'empty'):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                if mutation == 'version': del data['_spec']
                if mutation == 'host': data['source_url'] = 'https://example.com/permit.pdf'
                if mutation == 'page': data['entries'][0]['pages'] = [data['pdf_pages'] + 1]
                if mutation == 'duplicate': data['entries'].append(data['entries'][0])
                if mutation == 'section': data['entries'][0]['section'] = '<script>'
                if mutation == 'empty': data['entries'] = []
                with self.assertRaises(ValueError): demo.validate(data)

    def test_source_numerals(self):
        allowed = demo.authorised(self.data)
        for value in ('2026', '050000', '230', '48', '49', '65', '66', '69', '70', '5'):
            self.assertIn(value, allowed)
        self.assertNotIn('99999', allowed)

    def test_markup_is_bounded(self):
        html, _ = demo.render('2026-10-01')
        self.assertEqual(html.count('data-source-link'), len(self.data['entries']))
        self.assertIn('not a complete permit', html)
        self.assertIn('No facility records are included', html)
        self.assertIn('Reloading resets them', html)
        self.assertNotIn('type="file"', html)
        script = demo.JS.read_text()
        for api in ('fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage'):
            self.assertNotIn(api, script)


if __name__ == '__main__':
    unittest.main()
