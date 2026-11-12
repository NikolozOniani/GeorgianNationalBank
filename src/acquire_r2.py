"""Retrieve the R2 public-source vintage. Preserve earlier source manifests."""
import argparse
import json
from pathlib import Path

import acquire_episode as acquisition

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'data/r2_source_manifest.json'
PLAN = ROOT / 'research/r2_source_plan.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', nargs='+')
    parser.add_argument('--add-sources', action='store_true', help='Register previously unpinned sources only')
    args = parser.parse_args()
    acquisition.RAW = ROOT / 'data/raw/r2_2026_11_11'
    sources = json.loads(PLAN.read_text())
    if args.ids:
        sources = [row for row in sources if row['id'] in args.ids]
        if {row['id'] for row in sources} != set(args.ids):
            parser.error('Unknown source id')
    if LOCK.exists():
        pins = {row['id']: row for row in json.loads(LOCK.read_text())}
        for row in sources:
            pin = pins.get(row['id'], {})
            if pin.get('status') == 'acquired':
                row.update(sha256=pin['sha256'], bytes=pin['bytes'])
        acquisition.MANIFEST = ROOT / 'replication/local-results/r2_retrieval.json'
        acquisition.MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    else:
        acquisition.MANIFEST = LOCK
    records = acquisition.acquire(sources)
    if args.add_sources and acquisition.MANIFEST != LOCK:
        original = {row['id']: row for row in json.loads(LOCK.read_text())}
        for row in sources:
            if original.get(row['id'], {}).get('status') != 'acquired':
                original[row['id']] = records[row['id']]
        temp = LOCK.with_suffix('.json.partial')
        temp.write_text(json.dumps(sorted(original.values(), key=lambda r: r['id']), indent=2) + '\n')
        temp.replace(LOCK)
    if any(records[row['id']]['status'] != 'acquired' for row in sources):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
