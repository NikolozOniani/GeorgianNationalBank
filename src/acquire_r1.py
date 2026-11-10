"""Acquire R1 additions separately; retain old source and output locks."""
from pathlib import Path
import json
import acquire_episode as acquisition

ROOT=Path(__file__).resolve().parents[1]


def main():
    acquisition.RAW=ROOT/'data/raw/r1_2026_11_10'
    lock=ROOT/'data/r1_source_manifest.json'
    plan=json.loads((ROOT/'research/r1_source_plan.json').read_text())
    if lock.exists():
        pins={r['id']:r for r in json.loads(lock.read_text())}
        plan=[dict(r,sha256=pins[r['id']]['sha256'],bytes=pins[r['id']]['bytes']) if r['id'] in pins and pins[r['id']].get('sha256') else r for r in plan]
        acquisition.MANIFEST=ROOT/'replication/local-results/r1_retrieval.json'
        acquisition.MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    else:
        acquisition.MANIFEST=lock
    result=acquisition.acquire(plan)
    if any(result[r['id']]['status']!='acquired' for r in plan):raise SystemExit(1)


if __name__=='__main__':main()
