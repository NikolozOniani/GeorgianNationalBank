"""Check preservation and project structure; optional offline numerical replication."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'archive/legacy'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_check():
    manifest = json.loads((ROOT / 'archive/migration_manifest.json').read_text())
    failures = []
    counts = {}
    for row in manifest['files']:
        state = row['disposition']
        counts[state] = counts.get(state, 0) + 1
        if state == 'archived_unchanged':
            p = ROOT / row['current_path']
            if not p.is_file() or digest(p) != row['sha256']:
                failures.append(row['current_path'])
        elif state == 'git_history_only':
            p = LEGACY / row['original_path']
            if p.is_file() and digest(p) == row['sha256']:
                failures.append('Retired file restored: ' + row['original_path'])
    if failures:
        raise AssertionError(failures)
    return counts


def documentation_check():
    study = json.loads((ROOT / 'study.json').read_text())
    for name in ['README.md', 'AGENTS.md', 'research/PROTOCOL.md', 'manuscript/STRUCTURE.md']:
        body = (ROOT / name).read_text()
        for field in ['title', 'author', 'research_question', 'scope']:
            assert study[field] in body, (name, field)
    assert study['title'] in (ROOT / 'CITATION.cff').read_text()
    assert (ROOT / study['protocol']).is_file()
    requirements = json.loads((ROOT / study['data_requirements']).read_text())['requirements']
    source_register = (ROOT / 'research/SOURCES.md').read_text()
    ids = set()
    mandatory = {'id', 'priority', 'dataset', 'variables', 'units', 'frequency', 'period',
                 'source_ids', 'access', 'existing', 'action', 'validation', 'gates'}
    for row in requirements:
        assert mandatory <= row.keys(), row['id']
        assert row['id'] not in ids
        ids.add(row['id'])
        assert row['priority'] in {'P0', 'P1', 'P2'}
        assert all(row[k] for k in mandatory)
        assert all(f'| {sid} |' in source_register for sid in row['source_ids']), row['id']
        assert all(g in {'G1', 'G2', 'G3', 'G4', 'G5'} for g in row['gates'])
    broken = []
    files = [ROOT / 'README.md', ROOT / 'AGENTS.md']
    for folder in ['research', 'evidence', 'manuscript', 'replication', 'docs']:
        files.extend((ROOT / folder).glob('*.md'))
    files += [ROOT / 'archive/README.md', LEGACY / 'README.md']
    for p in files:
        for link in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if re.match(r'^[a-zA-Z]+:', link) or link.startswith('#'):
                continue
            target = unquote(link.split('#', 1)[0])
            if not (p.parent / target).exists():
                broken.append((str(p.relative_to(ROOT)), link))
    assert not broken, broken
    # The withdrawn public heading must not survive in the checked-out textual project.
    prohibited = 'რატომ და როგორ' + ' გვაღარიბებს ეროვნული ბანკი'
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix in {'.md', '.py', '.json', '.csv', '.cff'} and 'data/raw' not in p.as_posix() and '__pycache__' not in p.parts:
            assert prohibited not in p.read_text(errors='replace'), str(p)
    return {'requirements': len(requirements), 'active_markdown_files_checked': len(files), 'broken_local_links': 0}


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def legacy_tests():
    os.chdir(LEGACY)
    sys.path.insert(0, str(LEGACY))
    spec = json.loads((ROOT / 'archive/retired_tests.json').read_text())
    excluded = {r['id'] for r in spec['retired']}
    found = list(flatten(unittest.defaultTestLoader.discover(str(LEGACY / 'tests'))))
    assert excluded <= {t.id() for t in found}
    selected = [t for t in found if t.id() not in excluded]
    assert len(selected) == spec['remaining_legacy_tests_expected']
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    return result.wasSuccessful()


def replicate():
    numerical_json = {
        'reports/accountability/evidence_ledger.json',
        'reports/peer_review/results.json',
        'reports/reserve_foundations/validation.json',
    }
    records = []
    with tempfile.TemporaryDirectory(prefix='georgia-replication-') as temp:
        work = Path(temp) / 'legacy'
        shutil.copytree(LEGACY, work, ignore=shutil.ignore_patterns('data', '__pycache__', '.venv', '.deps'))
        (work / 'data/raw').mkdir(parents=True)
        files = [p for p in work.rglob('*') if p.is_file() and (p.suffix == '.csv' or str(p.relative_to(work)) in numerical_json)]
        before = {str(p.relative_to(work)): digest(p) for p in files}
        for script in ['reserve_foundations.py', 'paper_analysis.py', 'credit_analysis.py', 'accountability_scenarios.py']:
            run = subprocess.run([sys.executable, str(work / 'src' / script)], cwd=work, capture_output=True, text=True)
            if run.returncode:
                raise RuntimeError(f'{script}: {run.stdout}\n{run.stderr}')
            records.append({'script': script, 'returncode': 0})
        after = {name: digest(work / name) for name in before}
        changed = [name for name in before if before[name] != after[name]]
        allowed_newline_differences = {
            'reports/accountability/cpi_illustration.csv',
            'reports/accountability/evidence_ledger.csv',
        }
        for name in changed:
            assert name in allowed_newline_differences, name
            original = (LEGACY / name).read_bytes()
            regenerated = (work / name).read_bytes()
            assert original.replace(b'\r\n', b'\n') == regenerated.replace(b'\r\n', b'\n'), name
        return {'generators': records, 'numerical_files_checked': len(before),
                'exact_output_replication': not changed, 'numerical_content_identical': True,
                'newline_only_differences': sorted(changed), 'source_downloads': 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-only', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--replicate', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.legacy_only:
        raise SystemExit(0 if legacy_tests() else 1)
    result = {'baseline_commit': json.loads((ROOT / 'study.json').read_text())['baseline_commit'],
              'archive': archive_check(), 'documentation': documentation_check()}
    commands = [
        ('current_tests', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
        ('legacy_tests', [sys.executable, str(Path(__file__).resolve()), '--legacy-only']),
    ]
    for name, command in commands:
        run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        log = run.stdout + run.stderr
        print(log, end='')
        if run.returncode:
            raise RuntimeError(name + ' failed')
        count = re.search(r'Ran (\d+) tests', log)
        result[name] = {'returncode': 0, 'passed': int(count[1]), 'skipped': 0}
    result['retired_tests'] = json.loads((ROOT / 'archive/retired_tests.json').read_text())['retired']
    if args.replicate:
        result['replication'] = replicate()
    result['archive_after_checks'] = archive_check()
    result['new_empirical_estimation'] = False
    result['new_manuscript_written'] = False
    result['status'] = 'passed'
    if args.report:
        destination = args.report if args.report.is_absolute() else ROOT / args.report
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
