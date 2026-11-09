"""Resumable public-source acquisition; a failed asset never discards successes."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/episode_2026_11_09'
MANIFEST = ROOT / 'data/source_manifest.json'
MAX_DOWNLOAD_BYTES = 128 * 1024 * 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def validate_bytes(data, kind):
    if kind == 'json':
        json.loads(data)
    elif kind == 'xml':
        ET.fromstring(data)
    elif kind == 'xlsx':
        import io
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP CRC failure')
            if 'xl/workbook.xml' not in z.namelist():
                raise ValueError('Missing XLSX workbook')
    elif kind == 'pdf':
        if not data.startswith(b'%PDF'):
            raise ValueError('Invalid PDF signature')
    elif kind == 'csv':
        if b'<html' in data[:1000].lower() or not data.strip():
            raise ValueError('HTML or empty response instead of CSV')
    elif kind == 'html':
        if b'<html' not in data[:10000].lower() and b'<!doctype' not in data[:1000].lower():
            raise ValueError('Invalid HTML response')
    elif kind == 'html_fragment':
        if b'<table' not in data.lower():
            raise ValueError('Expected a public HTML table fragment')
    else:
        raise ValueError('Unsupported format: ' + kind)


def fetch(item, previous=None):
    row = dict(item)
    path = RAW / (item['id'] + '.' + item['format'])
    row['local_path'] = str(path.relative_to(ROOT))
    row['checked_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    expected = item.get('sha256') or (previous or {}).get('sha256') or (previous or {}).get('expected_sha256')
    try:
        if path.exists():
            data = path.read_bytes()
            row['retrieved_utc'] = (previous or {}).get('retrieved_utc', 'unknown_local_cache_time')
        else:
            known_size = item.get('bytes') or (previous or {}).get('bytes', 0)
            if known_size > MAX_DOWNLOAD_BYTES:
                raise ValueError('Source exceeds the 128 MiB download safety limit')
            url = urllib.parse.quote(item['url'], safe=':/?=%&,+')
            request = urllib.request.Request(url, headers={'User-Agent': 'GeorgianReserveResearch/1.0', 'Accept-Language': 'en'})
            with urllib.request.urlopen(request, timeout=35) as response:
                declared_size = int(response.headers.get('Content-Length', 0))
                if declared_size > MAX_DOWNLOAD_BYTES:
                    raise ValueError('Response exceeds the 128 MiB download safety limit')
                data = response.read(MAX_DOWNLOAD_BYTES + 1)
                if len(data) > MAX_DOWNLOAD_BYTES:
                    raise ValueError('Response exceeds the 128 MiB download safety limit')
                if declared_size and len(data) != declared_size:
                    raise ValueError('Incomplete response: Content-Length mismatch')
                row.update(final_url=response.url, http_status=response.status,
                           content_type=response.headers.get('Content-Type'),
                           last_modified=response.headers.get('Last-Modified'))
            partial = path.with_suffix(path.suffix + '.partial')
            partial.write_bytes(data)
            row['retrieved_utc'] = row['checked_utc']
            validate_bytes(data, item['format'])
            if expected and sha256(data) != expected:
                raise ValueError('Source vintage changed; partial retained, previous lock not replaced')
            partial.replace(path)
        validate_bytes(data, item['format'])
        digest = sha256(data)
        if expected and digest != expected:
            raise ValueError('Cached source hash does not match pinned vintage')
        row.update(status='acquired', sha256=digest, bytes=len(data))
        for k in ['final_url', 'http_status', 'content_type', 'last_modified']:
            if k not in row and k in (previous or {}):
                row[k] = previous[k]
    except Exception as error:
        row.update(status='failed', error=f'{type(error).__name__}: {error}')
        if expected:
            row['expected_sha256'] = expected
    return row


def acquire(plan):
    RAW.mkdir(parents=True, exist_ok=True)
    previous = {r['id']: r for r in json.loads(MANIFEST.read_text())} if MANIFEST.exists() else {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = [pool.submit(fetch, item, previous.get(item['id'])) for item in plan]
        for future in as_completed(pending):
            row = future.result()
            previous[row['id']] = row
            temporary = MANIFEST.with_suffix('.json.partial')
            temporary.write_text(json.dumps(sorted(previous.values(), key=lambda x: x['id']), ensure_ascii=False, indent=2) + '\n')
            temporary.replace(MANIFEST)
            print(row['id'], row['status'], row.get('bytes'), row.get('error', ''), flush=True)
    return previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--discover', action='store_true')
    parser.add_argument('--ids', nargs='*')
    args = parser.parse_args()
    if args.discover:
        plan = [dict(id=f'category_{n}', url=f'https://nbg.gov.ge/gw/api/ct/statistics/categories/{n}/data',
                     format='json', requirements=['catalogue'], definition='NBG official public table catalogue; not observations')
                for n in [20, 21, 19, 15, 24, 25]]
    else:
        plan = json.loads((ROOT / 'data/source_plan.json').read_text())
        if args.ids:
            plan = [r for r in plan if r['id'] in args.ids]
    result = acquire(plan)
    if any(result[item['id']]['status'] != 'acquired' for item in plan):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
