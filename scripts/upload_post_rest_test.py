#!/usr/bin/env python3
"""Offline regression tests. No live provider calls or publishing."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import upload_post_rest as rest

FIXTURES = tempfile.TemporaryDirectory()
MEDIA = Path(FIXTURES.name) / 'released.mp4'
MEDIA.write_bytes(b'released')
SECOND = Path(FIXTURES.name) / 'second.jpg'
SECOND.write_bytes(b'second')
SHA = rest.file_hash(MEDIA)
SECOND_SHA = rest.file_hash(SECOND)


def manifest(platform='facebook', kind='video', placement='feed', repo='TexasAIDispatch'):
    alaska = repo.startswith('alaska')
    return {'repository': 'Talonsturgill/' + repo, 'edition_id': '2026-11-10',
            'user': 'alaska_ai' if alaska else 'default', 'platform': platform,
            'placement': placement, 'segment_index': 0, 'media_type': kind,
            'media': [{'path': str(MEDIA), 'sha256': SHA}],
            'title': 'Released daily edition',
            'options': {'facebook_page_id': '2003130316607965' if alaska else '113073681274871'} if platform == 'facebook' else {}}


class RestTests(unittest.TestCase):
    def test_facebook_full_video_is_explicit(self):
        path, fields, _, _ = rest.build(manifest())
        self.assertEqual(path, '/upload')
        self.assertEqual(fields['facebook_media_type'], 'VIDEO')
        self.assertEqual(fields['video_state'], 'PUBLISHED')
        self.assertEqual(fields['platform[]'], 'facebook')

    def test_reels_cannot_override_facebook_feed(self):
        m = manifest(); m['options']['facebook_media_type'] = 'REELS'
        with self.assertRaises(ValueError): rest.build(m)

    def test_facebook_needs_verified_page(self):
        m = manifest(); m['options'] = {}
        with self.assertRaises(ValueError): rest.build(m)

    def test_all_brand_bindings(self):
        for repo, (user, org, kind) in rest.BRANDS.items():
            m = manifest('linkedin', 'video' if kind == 'video' else 'document', repo=repo.split('/')[1])
            _, fields, _, _ = rest.build(m)
            self.assertEqual(fields['user'], user)
            self.assertEqual(fields['target_linkedin_page_id'], org)
            self.assertEqual(fields['visibility'], 'PUBLIC')
            m['user'] = 'other'
            with self.assertRaises(ValueError): rest.build(m)

    def test_wrong_organization_refused(self):
        m = manifest('linkedin'); m['options']['target_linkedin_page_id'] = '117084989'
        with self.assertRaises(ValueError): rest.build(m)

    def test_unknown_platform_and_batch_refused(self):
        for platform in ('x', ['facebook', 'linkedin']):
            m = manifest(); m['platform'] = platform
            with self.assertRaises((ValueError, TypeError)): rest.build(m)

    def test_stories_have_explicit_placement(self):
        for platform, key in [('facebook', 'facebook_media_type'), ('instagram', 'media_type')]:
            m = manifest(platform, placement='story')
            self.assertEqual(rest.build(m)[1][key], 'STORIES')
            m['media'] *= 2
            with self.assertRaises(ValueError): rest.build(m)

    def test_no_story_on_linkedin(self):
        with self.assertRaises(ValueError): rest.build(manifest('linkedin', placement='story'))

    def test_instagram_photo_carousel_enum_and_order(self):
        m = manifest('instagram', 'photos', repo='TexasAIDocket')
        m['media'].append({'path': str(SECOND), 'sha256': SECOND_SHA})
        path, fields, media, _ = rest.build(m)
        self.assertEqual(path, '/upload_photos')
        self.assertEqual(fields['media_type'], 'IMAGE')
        self.assertEqual(media[1]['sha256'], SECOND_SHA)
        m['options']['media_type'] = 'CAROUSEL'
        with self.assertRaises(ValueError): rest.build(m)

    def test_youtube_photos_refused(self):
        with self.assertRaises(ValueError): rest.build(manifest('youtube', 'photos', repo='TexasAIDocket'))

    def test_document_has_only_document_schema(self):
        m = manifest('linkedin', 'document', repo='TexasAIDocket')
        path, fields, _, _ = rest.build(m)
        self.assertEqual(path, '/upload_document')
        self.assertNotIn('async_upload', fields)
        m['options']['first_comment'] = 'test'
        with self.assertRaises(ValueError): rest.build(m)

    def test_tiktok_public_not_draft(self):
        m = manifest('tiktok')
        fields = rest.build(m)[1]
        self.assertEqual(fields['post_mode'], 'DIRECT_POST')
        self.assertEqual(fields['privacy_level'], 'PUBLIC_TO_EVERYONE')
        m['options']['post_mode'] = 'MEDIA_UPLOAD'
        with self.assertRaises(ValueError): rest.build(m)

    def test_youtube_separate_description(self):
        m = manifest('youtube')
        with self.assertRaises(ValueError): rest.build(m)
        m['options']['youtube_description'] = 'Read more at https://texasaidocket.com/'
        self.assertEqual(rest.build(m)[1]['privacyStatus'], 'public')

    def test_unknown_options_and_headers_refused(self):
        for option in ('Authorization', 'api_key', 'scheduled_date', 'add_to_queue', 'platformOptions'):
            m = manifest(); m['options'][option] = 'bad'
            with self.assertRaises(ValueError): rest.build(m)

    def test_local_hash_verified_before_send(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'a.mp4'; path.write_bytes(b'video')
            m = manifest(); m['media'] = [{'path': str(path), 'sha256': hashlib.sha256(b'video').hexdigest()}]
            rest.build(m)
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError): rest.build(m)

    def test_signed_or_credential_media_url_refused(self):
        for url in ('http://example.com/a', 'https://a:b@example.com/a', 'https://example.com/a?sig=secret', 'https://api.upload-post.com/a'):
            m = manifest(); m['media'][0]['url'] = url
            with self.assertRaises(ValueError): rest.build(m)

    def test_dry_run_does_not_write_or_send(self):
        with tempfile.TemporaryDirectory() as d:
            result = rest.upload(manifest(), d, True, send=lambda *a: self.fail('network'))
            self.assertEqual(result['state'], 'DRY_RUN')
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_intent_durable_before_send_and_accepted_not_published(self):
        with tempfile.TemporaryDirectory() as d:
            def send(*args):
                self.assertEqual(json.loads(next(Path(d).glob('*.json')).read_text())['state'], 'UNKNOWN')
                return 200, {'request_id': 'r1', 'success': True}
            result = rest.upload(manifest(), d, send=send)
            self.assertEqual(result['state'], 'ACCEPTED')
            self.assertEqual(result['request_id'], 'r1')
            saved = json.loads(Path(result['receipt']).read_text())
            self.assertEqual(saved, result)

    def test_changed_copy_and_media_cannot_repeat_logical_delivery(self):
        with tempfile.TemporaryDirectory() as d:
            rest.upload(manifest(), d, send=lambda *a: (200, {'request_id': 'r1'}))
            m = manifest(); m['title'] = 'Changed'; m['media'][0] = {'path': str(SECOND), 'sha256': SECOND_SHA}
            with self.assertRaises(ValueError): rest.upload(m, d, send=lambda *a: self.fail('duplicate send'))

    def test_timeout_is_unknown_and_cannot_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            def send(*a): raise subprocess.TimeoutExpired('curl', 190)
            self.assertEqual(rest.upload(manifest(), d, send=send)['state'], 'UNKNOWN')
            with self.assertRaises(ValueError): rest.upload(manifest(), d, send=send)

    def test_500_is_unknown_not_failed(self):
        with tempfile.TemporaryDirectory() as d:
            result = rest.upload(manifest(), d, send=lambda *a: (500, {'error': 'server'}))
            self.assertEqual(result['state'], 'UNKNOWN')
            self.assertEqual(result['response']['error'], 'server')

    def test_empty_crash_receipt_blocks_retry(self):
        with tempfile.TemporaryDirectory() as d:
            preview = rest.upload(manifest(), d, True)
            Path(preview['receipt']).touch()
            with self.assertRaises(ValueError): rest.upload(manifest(), d, send=lambda *a: self.fail('send'))

    def test_segment_receipts_are_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            m = manifest(placement='story')
            first = rest.upload(m, d, True)
            m['segment_index'] = 1
            self.assertNotEqual(first['receipt'], rest.upload(m, d, True)['receipt'])

    def test_read_routes_use_exact_query_contract(self):
        cases = [('tiktok-settings', {'profile': 'default'}),
                 ('media', {'user': 'default', 'platform': 'linkedin', 'page_urn': '78748279'}),
                 ('history', {'page': '2', 'limit': '100'}), ('status', {'request_id': 'r1'})]
        for route, query in cases:
            rest.read(route, query, send=lambda path: (200, {'path': path}))
        for route, query in [('tiktok-settings', {'user': 'default'}), ('media', {'user': 'default', 'platform': 'linkedin'}), ('status', {}), ('history', {'limit': '1'})]:
            with self.assertRaises(ValueError): rest.read(route, query, send=lambda *a: self.fail('network'))

    def test_transport_no_auth_no_redirect_no_retry_and_literal_caption(self):
        completed = subprocess.CompletedProcess([], 0, '{"request_id":"r1"}\n200', '')
        with patch.object(rest.subprocess, 'run', return_value=completed) as run:
            rest.transport('/upload', {'title': '@not-a-file', 'platform[]': 'facebook'},
                           [{'path': str(MEDIA), 'sha256': SHA}], 'video')
        args = run.call_args.args[0]
        self.assertEqual(args[:2], ['curl', '--disable'])
        self.assertNotIn('--location', args)
        self.assertEqual(args[args.index('--retry') + 1], '0')
        self.assertEqual([args[i + 1] for i, v in enumerate(args) if v == '--header'], ['Accept: application/json'])
        self.assertIn('title=@not-a-file', args)
        self.assertEqual(args[-1], rest.BASE + '/upload')

    def test_transport_nonjson_is_uncertain(self):
        completed = subprocess.CompletedProcess([], 0, '<html>error</html>\n502', '')
        with patch.object(rest.subprocess, 'run', return_value=completed):
            with self.assertRaises(RuntimeError): rest.transport('/uploadposts/users')


if __name__ == '__main__':
    unittest.main()
