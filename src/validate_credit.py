"""Offline replication and preservation audit; --raw additionally checks source files."""
import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/peer_review'
BASE = '89bbc62a1e2d3dc1fd786568460c39bc431c6cf7'
OUTPUTS = ['table1_observed.csv', 'table2_standardized_new_loan.csv', 'indexed_contract_monthly.csv',
           'table3_reset_sensitivity.csv', 'alternative_reference_9pct.csv',
           'table4_conditional_income_exposure.csv', 'results.json']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--raw', action='store_true'); args = parser.parse_args()
    failures = []
    before = {f: digest(OUT / f) for f in OUTPUTS}
    process = subprocess.run([sys.executable, str(ROOT / 'src/credit_analysis.py')], cwd=ROOT, capture_output=True, text=True)
    after = {f: digest(OUT / f) for f in OUTPUTS}
    if process.returncode or before != after:
        failures.append('Numerical outputs do not reproduce exactly; inspect before/after hashes and stderr')
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, capture_output=True, text=True)
    (OUT / 'tests.log').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    if tests.returncode: failures.append('Automated tests failed')
    tree = subprocess.run(['git', 'ls-tree', '-rz', BASE], cwd=ROOT, capture_output=True)
    preservation = {'baseline': BASE, 'allowed_navigation_change': 'README.md', 'verified_files': 0, 'changes': []}
    if tree.returncode:
        preservation['status'] = 'not_checked: baseline Git objects unavailable'
    else:
        for entry in tree.stdout.split(b'\0'):
            if not entry: continue
            meta, name = entry.split(b'\t', 1)
            filename = name.decode(); expected = meta.decode().split()[2]
            if filename == 'README.md': continue
            path = ROOT / filename
            if not path.is_file(): preservation['changes'].append(filename); continue
            data = path.read_bytes()
            actual = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
            if actual != expected: preservation['changes'].append(filename)
            else: preservation['verified_files'] += 1
        preservation['status'] = 'passed' if not preservation['changes'] else 'failed'
        if preservation['changes']: failures.append('Prior research changed')
    raw = {'status': 'not requested; offline validation only'}
    if args.raw:
        from credit_acquire import validate
        raw = {'checked': 0, 'failures': []}
        for s in json.loads((OUT / 'sources.json').read_text()):
            p = ROOT / 'data/raw/peer_review' / s['filename']
            try:
                if digest(p) != s['sha256']: raise ValueError('Hash mismatch')
                validate(p); raw['checked'] += 1
            except Exception as e: raw['failures'].append({'source': s['id'], 'error': str(e)})
        raw['status'] = 'passed' if not raw['failures'] else 'failed'
        if raw['failures']: failures.append('Raw-source verification failed')
    versions = {}
    for package in ['openpyxl', 'matplotlib', 'reportlab', 'pypdf']:
        try: versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError: versions[package] = 'not installed (optional for core calculations)'
    result = {'checked_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'python': platform.python_version(),
              'packages': versions, 'analysis_returncode': process.returncode, 'analysis_stderr': process.stderr,
              'numerical_outputs_unchanged': before == after, 'output_sha256': after,
              'previous_output_sha256': before, 'tests_returncode': tests.returncode,
              'prior_research_preservation': preservation, 'raw_sources': raw,
              'extraction': json.loads((OUT / 'extraction_validation.json').read_text()),
              'limits': ['Checks establish extraction consistency and conditional arithmetic, not causal identification.',
                         'Provider historical release vintages are not reconstructed.',
                         'No linked borrower contracts/incomes or population welfare estimate.'],
              'failures': failures, 'status': 'passed' if not failures else 'failed'}
    (OUT / 'validation_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if failures: raise SystemExit(1)


if __name__ == '__main__':
    main()
