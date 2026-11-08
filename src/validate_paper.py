"""Verify integrated-paper numerical reproducibility and optional pinned source bytes."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/paper'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--raw',action='store_true');args=parser.parse_args()
    files=['annual_results.csv','accounting_checks.csv','reserve_bridges.csv','reserve_channel_sensitivity.csv','reserve_target_arithmetic.csv']
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    before={n:digest(OUT/n) for n in files}
    proc=subprocess.run([sys.executable,'src/paper_analysis.py'],cwd=ROOT,capture_output=True,text=True)
    after={n:digest(OUT/n) for n in files}
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True)
    (OUT/'tests.log').write_text(tests.stdout+tests.stderr)
    raw=[]
    if args.raw:
        for s in json.loads((OUT/'sources.json').read_text()):
            p=ROOT/'data/raw/paper'/s['filename']
            raw.append({'id':s['id'],'hash_verified':p.exists() and digest(p)==s['sha256']})
    passed=proc.returncode==tests.returncode==0 and before==after and all(r['hash_verified'] for r in raw)
    result=dict(checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='passed' if passed else 'failed',
                calculations_reproduce_exactly=before==after,calculation_stderr=proc.stderr,test_returncode=tests.returncode,
                outputs_sha256=after,raw_sources=raw if args.raw else 'not requested',
                scope='Numerical replication and source integrity; not independent external peer review or causal identification')
    (OUT/'validation_report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
