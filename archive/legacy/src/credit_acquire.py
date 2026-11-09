"""Acquire official credit sources independently; validate and pin their bytes.

Existing files are verified rather than downloaded again. A changed source is
reported and stored separately, never silently replacing the reviewed vintage.
"""
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/peer_review'
OUT=ROOT/'reports/peer_review'


def validate(path,format_suffix=None):
    suffix=format_suffix or path.suffix
    if suffix=='.xlsx':
        with zipfile.ZipFile(path) as z:
            bad=z.testzip()
            if bad is not None:raise ValueError('Bad ZIP CRC: '+bad)
            if 'xl/workbook.xml' not in z.namelist():raise ValueError('Not an XLSX workbook')
    elif suffix=='.pdf' and not path.read_bytes().startswith(b'%PDF'):
        raise ValueError('Not a PDF')


def fetch(item):
    r={**item,'checked_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    path=RAW/item['filename']
    try:
        if not path.exists():
            url=urllib.parse.quote(item['url'],safe=':/?=%&')
            with urllib.request.urlopen(url,timeout=45) as response:data=response.read()
            temp=path.with_suffix(path.suffix+'.partial');temp.write_bytes(data)
            digest=hashlib.sha256(data).hexdigest()
            r.update(sha256=digest,bytes=len(data))
            validate(temp,path.suffix)
            if item.get('sha256') and digest!=item['sha256']:
                quarantine=path.with_name(path.stem+'.unreviewed-'+digest[:12]+path.suffix)
                temp.replace(quarantine)
                r['unreviewed_file']=str(quarantine.relative_to(ROOT))
                raise ValueError('Source vintage changed; downloaded bytes quarantined before repinning')
            temp.replace(path)
        validate(path)
        data=path.read_bytes();r.update(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
        if item.get('sha256') and r['sha256']!=item['sha256']:
            raise ValueError('Source vintage changed; review before repinning')
        r['status']='verified'
    except Exception as e:r.update(status='failed',error=str(e))
    return r


def main():
    RAW.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    plan=json.loads((OUT/'sources.json').read_text())
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(fetch,plan):
            results.append(r)
            (OUT/'acquisition_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
            print(r['id'],r['status'],r.get('bytes'),r.get('error',''),flush=True)
    if any(r['status']!='verified' for r in results):raise SystemExit(1)


if __name__=='__main__':main()
