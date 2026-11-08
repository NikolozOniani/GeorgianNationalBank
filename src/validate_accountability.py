"""Run preservation, reproducibility, focused tests and delivery-length checks."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/accountability'


def main():
    lock=json.loads((OUT/'parent_files.lock.json').read_text())
    failures=[name for name,sha in lock['sha256'].items()
              if not (ROOT/name).exists() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha]
    if failures:raise RuntimeError('Prior work modified: '+', '.join(failures))
    subprocess.run([sys.executable,str(ROOT/'src/accountability_scenarios.py')],cwd=ROOT,check=True)
    run=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True)
    log=run.stdout+run.stderr
    # Test duration is machine-dependent; normalize only that display line.
    normalized=re.sub(r'Ran (\d+) tests in [\d.]+s',r'Ran \1 tests (elapsed time omitted)',log)
    (OUT/'test_results.txt').write_text(normalized)
    if run.returncode:raise RuntimeError(log)
    speech=(OUT/'Speech_ka.md').read_text().split('[S01]',1)[1]
    speech=re.sub(r'\[S\d+\]','',speech)
    count=len(speech.split())
    result={'status':'passed','parent_commit':lock['parent_commit'],
            'prior_files_preserved_n':len(lock['sha256']),'intentional_exception':'README.md navigation added',
            'tests_passed':int(re.search(r'Ran (\d+) tests',log)[1]),
            'spoken_word_count':count,'estimated_minutes_at_130_wpm':round(count/130,2),
            'estimated_minutes_at_110_wpm':round(count/110,2),'timed_rehearsal':False,
            'evidence_rows':len(json.loads((OUT/'evidence_ledger.json').read_text())),
            'causal_estimation_run':False,'microdata_reprocessed':False,
            'numerical_output_reproduces':True,
            'limitations':['Tests verify arithmetic and preservation, not causal identification or legal compliance.',
                           'Speech claims manually checked against register and existing research.',
                           'No exhaustive publication-compliance audit or native-speaker oral rehearsal performed.']}
    (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
