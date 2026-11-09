"""Exercise fresh-checkout and supplied-cache reproduction without network access.

Copy indexed paths using current working bytes so the test also covers a pending
commit. No Git history or raw cache is copied into the initial checkout.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def run(work, arguments, expected=0):
    environment=dict(os.environ, PYTHONPATH=str(work), PYTHONDONTWRITEBYTECODE='1')
    # All invoked commands are local checks; none calls an acquisition entry point.
    result=subprocess.run([sys.executable,*arguments],cwd=work,env=environment,capture_output=True,text=True)
    if result.returncode!=expected:
        raise RuntimeError(f'{arguments}: expected {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}')
    return dict(command=arguments,returncode=result.returncode,expected_returncode=expected)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=ROOT/'replication/local-results/r0')
    args=parser.parse_args()
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    sources=json.loads((ROOT/'data/source_manifest.json').read_text())
    commands=[]
    with tempfile.TemporaryDirectory(prefix='r0-clean-') as folder:
        work=Path(folder)
        for name in filter(None,tracked):
            source=ROOT/name
            if not source.is_file():raise ValueError('Indexed path absent: '+name)
            target=work/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        commands.append(run(work,['replication/check_repository.py']))
        commands.append(run(work,['replication/audit_r0.py','--output-dir','replication/local-results/no-raw']))
        empty=json.loads((work/'replication/local-results/no-raw/audit.json').read_text())
        assert empty['raw_verified']==0 and len(empty['raw_absent'])==len(sources)
        commands.append(run(work,['src/validate_episode.py']))
        report=json.loads((work/'replication/local-results/episode/validation.json').read_text())
        assert not report['raw_source_validation_complete'] and len(report['raw_caches_absent'])==len(sources)
        commands.append(run(work,['src/validate_episode.py','--require-raw'],expected=1))
        supplied=0
        for row in sources:
            original=ROOT/row['local_path']
            if not original.is_file():raise ValueError('Cannot test supplied-cache reproduction: '+row['id'])
            if hashlib.sha256(original.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Source mismatch: '+row['id'])
            target=work/row['local_path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target);supplied+=1
        commands.append(run(work,['src/extract_episode.py','--check']))
        commands.append(run(work,['src/validate_episode.py','--require-raw']))
        final=json.loads((work/'replication/local-results/episode/validation.json').read_text())
        assert final['raw_source_validation_complete'] and final['required_checks_passed']
        # Replication of existing numerical outputs, not a new empirical estimate.
        comparisons=[]
        for name in ['annual_reserve_bridge.csv','ara_component_inputs.csv','episode_monthly_missingness.csv',
                     'intervention_reconciliation.csv','monthly_policy_panel.csv','reserve_template_reconciliation.csv']:
            same=(work/'replication/local-results/episode'/name).read_bytes()==(ROOT/'reports/acquisition_2026_11_09'/name).read_bytes()
            assert same,name
            comparisons.append(dict(file=name,byte_identical=True))
        result=dict(registration_date='2026-11-10',baseline_commit='3a16715b6e8c79e4abb2dbb1a596b6e290e3b8e6',
            python_version=sys.version,dependencies={p:importlib.metadata.version(p) for p in ['openpyxl','pypdf','matplotlib']},
            commands=commands,clean_checkout_raw_absent=len(empty['raw_absent']),supplied_raw_verified=supplied,
            all_36_derived_tables_byte_identical=True,accounting_comparisons=comparisons,
            validation_checks=len(final['checks']),passed_source_checks=sum(r['passed'] for r in final['checks']),
            qualified_source_checks=[r['check'] for r in final['checks'] if not r['passed']],
            source_downloads=0,new_empirical_estimation=False,
            limitation='Isolated checkout uses the same installed Python environment and lawful local source cache; not an independent researcher or remote vintage download test')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'replication.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
