#!/usr/bin/env python3
"""Narrow Upload-Post REST transport for the released daily edition.

Authentication is injected by Claude cloud Network secrets for api.upload-post.com.
No credential argument, environment lookup, Authorization header, redirect or retry.
The director still owns release gates, account verification, the edition lease,
provider-history reconciliation and verification of each actual published post.
Social ownership uses a separate durable Git intent, never the production lease.
Official contract: https://docs.upload-post.com/api/upload-video (2026-11-10).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from upload_post_state import GitState
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

BASE = 'https://api.upload-post.com/api'
ROUTES = {
    'users': ('/uploadposts/users', set()),
    'facebook-pin': ('/uploadposts/users/facebook-page', {'profile_username'}),
    'linkedin-pin': ('/uploadposts/users/linkedin-page', {'profile_username'}),
    'facebook-pages': ('/uploadposts/facebook/pages', {'profile'}),
    'linkedin-pages': ('/uploadposts/linkedin/pages', {'profile'}),
    'tiktok-settings': ('/uploadposts/tiktok/settings', {'profile'}),
    'history': ('/uploadposts/history', {'page', 'limit'}),
    'status': ('/uploadposts/status', {'request_id', 'job_id'}),
    'media': ('/uploadposts/media', {'user', 'platform', 'page_urn', 'limit', 'cursor'}),
}
BRANDS = {
    'Talonsturgill/alaska-ai-weekly': ('alaska_ai', '117084989', 'video'),
    'Talonsturgill/alaskaaicarousels': ('alaska_ai', '117084989', 'carousel'),
    'Talonsturgill/TexasAIDispatch': ('default', '78748279', 'video'),
    'Talonsturgill/TexasAIDocket': ('default', '78748279', 'carousel'),
}
# Explicit supported subset. Unknown fields fail closed, never silently ignored.
OPTIONS = {
    'video': {
        'description', 'first_comment', 'media_type', 'facebook_media_type',
        'facebook_page_id', 'video_state', 'target_linkedin_page_id', 'visibility',
        'youtube_title', 'youtube_description', 'privacyStatus',
        'linkedin_description', 'facebook_description', 'post_mode', 'privacy_level',
        'is_ai_generated', 'is_aigc', 'containsSyntheticMedia',
        'selfDeclaredMadeForKids', 'brand_content_toggle', 'brand_organic_toggle',
        'disable_comment', 'disable_duet', 'disable_stitch',
    },
    'photos': {
        'description', 'first_comment', 'media_type', 'facebook_media_type',
        'facebook_page_id', 'target_linkedin_page_id', 'visibility',
        'linkedin_description', 'post_mode', 'privacy_level', 'tiktok_description',
        'auto_add_music', 'is_ai_generated', 'brand_content_toggle',
        'brand_organic_toggle', 'disable_comment',
    },
    'document': {'description', 'target_linkedin_page_id', 'visibility'},
}
ENDPOINTS = {'video': ('/upload', 'video'), 'photos': ('/upload_photos', 'photos[]'),
             'document': ('/upload_document', 'document')}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build(manifest):
    """Validate a single bound destination and return path, fields, media, identity."""
    require(isinstance(manifest, dict), 'manifest must be an object')
    required = {'repository', 'edition_id', 'user', 'platform', 'placement',
                'segment_index', 'media_type', 'media', 'title'}
    require(required <= manifest.keys() <= required | {'options'}, 'invalid manifest fields')
    repo = manifest['repository']
    require(repo in BRANDS, 'repository is not an authorized daily routine')
    user, organization, routine = BRANDS[repo]
    require(manifest['user'] == user, 'profile does not match repository')
    require(isinstance(manifest['edition_id'], str) and manifest['edition_id'].strip(), 'edition ID required')
    platform, placement, kind = (manifest[k] for k in ('platform', 'placement', 'media_type'))
    require(platform in {'facebook', 'linkedin', 'instagram', 'tiktok', 'youtube'}, 'unsupported platform')
    require(placement in {'feed', 'story'}, 'unsupported placement')
    require(type(manifest['segment_index']) is int and manifest['segment_index'] >= 0, 'invalid segment index')
    require(placement == 'story' or manifest['segment_index'] == 0, 'feed segment index must be zero')
    require(kind in ENDPOINTS, 'unsupported media type')
    require(kind == 'video' if routine == 'video' else kind in {'document', 'photos'}, 'media does not match routine')
    require(kind != 'document' or (platform == 'linkedin' and placement == 'feed'), 'documents require LinkedIn feed')
    require(kind != 'photos' or platform != 'youtube', 'YouTube cannot publish a photo carousel')
    require(routine != 'carousel' or platform != 'linkedin' or kind == 'document', 'LinkedIn carousel requires released PDF')
    require(placement != 'story' or platform in {'facebook', 'instagram'}, 'unsupported Story destination')
    media = manifest['media']
    require(isinstance(media, list) and media, 'ordered media list required')
    require((kind == 'photos' and placement == 'feed') or len(media) == 1, 'one media item required')
    for item in media:
        require(isinstance(item, dict) and set(item) == {'path', 'sha256'}, 'media needs local path and sha256; remote URLs are not accepted')
        require(isinstance(item['sha256'], str) and re.fullmatch('[a-f0-9]{64}', item['sha256']), 'invalid media SHA256')
        path = Path(item['path'])
        require(path.is_file(), 'media file missing')
        require(file_hash(path) == item['sha256'], 'local media hash mismatch')
    require(isinstance(manifest['title'], str) and manifest['title'].strip(), 'title/caption required')
    options = dict(manifest.get('options', {}))
    require(options.keys() <= OPTIONS[kind], 'unsupported REST option')
    require(all(isinstance(v, (str, bool, int)) for v in options.values()), 'options must be scalar values')

    def fixed(key, value):
        require(key not in options or options[key] == value, 'conflicting placement/account option: ' + key)
        options[key] = value

    if platform == 'linkedin':
        urn = 'urn:li:organization:' + organization
        require(options.get('target_linkedin_page_id', urn) in {organization, urn},
                'LinkedIn organization does not match repository')
        options['target_linkedin_page_id'] = urn
        fixed('visibility', 'PUBLIC')
    else:
        require('target_linkedin_page_id' not in options and 'visibility' not in options,
                'LinkedIn options on another platform')
    if platform == 'facebook':
        expected_page = '2003130316607965' if user == 'alaska_ai' else '113073681274871'
        require(str(options.get('facebook_page_id', '')) == expected_page, 'verified bound Facebook Page ID required')
        fixed('facebook_media_type', 'STORIES' if placement == 'story' else ('VIDEO' if kind == 'video' else 'POSTS'))
        if kind == 'video':
            fixed('video_state', 'PUBLISHED')
    else:
        require(not any(k.startswith('facebook_') or k == 'video_state' for k in options), 'Facebook options on another platform')
    if platform == 'instagram':
        fixed('media_type', 'STORIES' if placement == 'story' else ('REELS' if kind == 'video' else 'IMAGE'))
    else:
        require('media_type' not in options, 'Instagram media_type on another platform')
    if platform == 'tiktok':
        fixed('post_mode', 'DIRECT_POST')
        fixed('privacy_level', 'PUBLIC_TO_EVERYONE')
    else:
        require('post_mode' not in options and 'privacy_level' not in options, 'TikTok options on another platform')
    if platform == 'youtube':
        fixed('privacyStatus', 'public')
        require(bool(options.get('youtube_description')), 'YouTube needs separate description')
    elif 'privacyStatus' in options:
        raise ValueError('YouTube privacy on another platform')
    fields = {'user': user, 'platform[]': platform, 'title': manifest['title'], **options}
    if kind != 'document':
        fields['async_upload'] = True
    identity = {k: manifest[k] for k in ('repository', 'edition_id', 'user', 'platform', 'placement', 'segment_index')}
    return ENDPOINTS[kind][0], fields, media, identity


def transport(path, fields=None, media=(), media_field=None):
    """One curl invocation. Never follow redirects, read curlrc, or retry writes."""
    args = ['curl', '--disable', '--silent', '--show-error', '--retry', '0',
            '--connect-timeout', '30', '--max-time', '180', '--proto', '=https',
            '--request', 'POST' if fields is not None else 'GET',
            '--header', 'Accept: application/json', '--write-out', '\n%{http_code}']
    if fields is not None:
        for key, value in fields.items():
            value = str(value).lower() if isinstance(value, bool) else str(value)
            args += ['--form-string', key + '=' + value]
        for item in media:
            # curl form syntax needs quoted/escaped filenames, not shell quoting.
            path_value = str(Path(item['path']).resolve()).replace('\\', '\\\\').replace('"', '\\"')
            args += ['--form', media_field + '=@"' + path_value + '"']
    args.append(BASE + path)
    result = subprocess.run(args, capture_output=True, text=True, timeout=190, check=False)
    if result.returncode:
        # Do not expose curl stderr, proxy details or any request headers.
        raise RuntimeError('transport failed with curl exit ' + str(result.returncode))
    raw, status = result.stdout.rsplit('\n', 1)
    code = int(status)
    try:
        response = json.loads(raw)
    except (ValueError, TypeError):
        raise RuntimeError('non-JSON provider response; HTTP ' + str(code)) from None
    return code, response


def redact(value):
    """Keep reconciliation metadata, omit unnecessary account email addresses."""
    sensitive = {'user_email', 'access_token', 'refresh_token', 'api_key', 'token',
                 'authorization', 'client_secret', 'password', 'secret', 'session_cookie',
                 'session_token', 'id_token', 'cookie', 'set-cookie'}
    if isinstance(value, dict):
        return {key: redact(item) for key, item in value.items() if key.lower() not in sensitive}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str) and value.startswith(('https://', 'http://')):
        parsed = urlsplit(value)
        query = parse_qsl(parsed.query, keep_blank_values=True)
        secret_query = sensitive | {'sig', 'signature', 'x-amz-signature', 'x-amz-credential',
                                    'x-amz-security-token', 'x-goog-signature', 'x-goog-credential'}
        if any(key.lower() in secret_query for key, _ in query):
            return urlunsplit((parsed.scheme, parsed.hostname or '', parsed.path, 'REDACTED', ''))
    return value


def read(route, query, send=transport):
    path, allowed = ROUTES[route]
    require(query.keys() <= allowed, 'unsupported read query')
    if route == 'status':
        require(len(query) == 1 and bool(next(iter(query.values()), '')), 'supply one request_id or job_id')
    if route == 'history':
        require(query.get('limit', '10') in {'10', '20', '50', '100'}, 'history limit must be 10, 20, 50 or 100')
        require(str(query.get('page', '1')).isdigit() and int(query.get('page', '1')) >= 1, 'history page must be positive')
    if route in {'facebook-pin', 'linkedin-pin'}:
        require(query.get('profile_username') in {'alaska_ai', 'default'}, 'bound profile required')
    if route == 'tiktok-settings':
        require(bool(query.get('profile')), 'TikTok profile required')
    if route == 'media':
        require(bool(query.get('user')) and bool(query.get('platform')), 'media user and platform required')
        if query['platform'] == 'linkedin':
            require(query.get('page_urn') in {'117084989', '78748279'}, 'bound LinkedIn organization required')
    if query:
        path += '?' + urlencode(query)
    status, response = send(path)
    return status, redact(response)


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_json(stream, value):
    stream.write(canonical(value) + '\n')
    stream.flush()
    os.fsync(stream.fileno())


def save_local_receipt(receipt, info):
    temp = receipt.with_suffix('.response.tmp')
    with temp.open('x', encoding='utf-8') as stream:
        write_json(stream, info)
    os.replace(temp, receipt)
    sync_directory(receipt.parent)


def compact_receipt(info):
    """Public minimal recovery data; never persist raw provider content to Git."""
    result = {'state': info['state']}
    if 'http_status' in info:
        result['http_status'] = info['http_status']
    for key in ('request_id', 'job_id'):
        value = info.get(key)
        if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,256}', value):
            result[key] = value
    # Each request has exactly one bound platform. A synchronous provider result
    # may put its public identifiers directly or under a platform/results object.
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'platform_post_id' and isinstance(item, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,256}', item):
                    result.setdefault(key, item)
                elif key == 'post_url' and isinstance(item, str):
                    url = urlsplit(item)
                    host = (url.hostname or '').lower()
                    allowed = ('facebook.com', 'instagram.com', 'linkedin.com', 'tiktok.com', 'youtube.com', 'youtu.be')
                    if (url.scheme == 'https' and not url.username and not url.password and
                            any(host == domain or host.endswith('.' + domain) for domain in allowed)
                            and redact(item) == item):
                        result.setdefault(key, item)
                elif isinstance(item, (dict, list)):
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    visit(info.get('response'))
    return result


def upload(manifest, receipt_dir, dry_run=False, send=transport, state_store=None):
    path, fields, media, identity = build(manifest)
    receipt = Path(receipt_dir) / ('upload-post-' + digest(identity) + '.json')
    fingerprint = digest({'identity': identity, 'media_sha256': [m['sha256'] for m in media],
                          'media_type': manifest['media_type'], 'fields': fields})
    info = {'identity': identity, 'fingerprint': fingerprint, 'endpoint': path,
            'receipt': str(receipt), 'state': 'UNKNOWN',
            'started_at': datetime.now(timezone.utc).isoformat()}
    if dry_run:
        return {**info, 'state': 'DRY_RUN', 'fields': fields, 'media': media}
    require(receipt.parent.is_dir(), 'existing edition scratch directory required')
    # Local receipts from older runs still block automatic re-submission. The
    # remote intent is created first so a rejected CAS cannot leave a misleading
    # local network-attempt marker; no POST is possible without that durable claim.
    require(not receipt.exists() and not receipt.is_symlink(),
            'delivery already attempted; reconcile existing receipt/history, never resubmit')
    store = state_store or GitState(Path(__file__).resolve().parents[1], manifest['repository'])
    claim = store.claim(identity, fingerprint)
    info['social_claim'] = claim
    # A crash or local-write failure here leaves the remote UNKNOWN intent intact.
    # Another container must reconcile it, never take over or repeat the POST.
    with receipt.open('x', encoding='utf-8') as stream:
        write_json(stream, info)
    sync_directory(receipt.parent)
    try:
        build(manifest)  # Verify bytes again after remote claim latency.
        code, response = send(path, fields, media, ENDPOINTS[manifest['media_type']][1])
        info.update(http_status=code, response=redact(response))
        info['state'] = 'ACCEPTED' if 200 <= code < 300 else 'UNKNOWN'
        if isinstance(response, dict):
            for key in ('request_id', 'job_id'):
                if response.get(key):
                    info[key] = response[key]
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        info['error'] = type(error).__name__ + ': transport outcome uncertain; reconcile before retry'
    # Retain the returned request ID before any slower Git metadata operation.
    info['remote_receipt_saved'] = False
    save_local_receipt(receipt, info)
    # Remote response persistence may retry only metadata CAS, never the POST.
    # If it fails, retain local evidence and the durable remote UNKNOWN intent.
    try:
        store.save_result(claim, compact_receipt(info))
        info['remote_receipt_saved'] = True
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired):
        info['remote_receipt_saved'] = False
        info['durability_error'] = 'Remote receipt uncertain; preserve local response and reconcile original request. Never resubmit.'
    save_local_receipt(receipt, info)
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    get = sub.add_parser('read')
    get.add_argument('route', choices=ROUTES)
    get.add_argument('--query', action='append', default=[], metavar='KEY=VALUE')
    post = sub.add_parser('upload')
    post.add_argument('--manifest', required=True)
    post.add_argument('--receipt-dir', required=True)
    post.add_argument('--dry-run', action='store_true')
    state = sub.add_parser('state')
    state.add_argument('--repository', required=True, choices=BRANDS)
    state.add_argument('--edition-id')
    state.add_argument('--initialize', action='store_true', help='Verify/create only the separate empty social state branch; never publish')
    args = parser.parse_args()
    try:
        if args.command == 'state':
            store = GitState(Path(__file__).resolve().parents[1], args.repository)
            if args.initialize:
                store.initialize()
            print(canonical(store.records(args.edition_id)))
            return 0
        if args.command == 'read':
            pairs = [item.split('=', 1) for item in args.query]
            require(all(len(item) == 2 for item in pairs), 'query must be KEY=VALUE')
            require(len(dict(pairs)) == len(pairs), 'duplicate query key')
            status, response = read(args.route, dict(pairs))
            print(canonical({'http_status': status, 'response': response}))
            return 0 if 200 <= status < 300 else 2
        result = upload(json.loads(Path(args.manifest).read_text()), args.receipt_dir, args.dry_run)
        print(canonical(result))
        return 0 if result['state'] == 'DRY_RUN' else 3  # 3 = reconciliation required, not publication success
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print('BLOCKED: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
