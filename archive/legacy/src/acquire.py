"""Retrieve source bytes atomically; reject truncated or corrupt archives."""
import urllib.request, pathlib, hashlib, json, zipfile, datetime, concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCES={'hies2025':'https://www.geostat.ge/media/79814/2025.zip','hies2016':'https://geostat.ge/media/23296/2016-DB_eng.zip','hies2017':'https://geostat.ge/media/62840/2017.zip','nbg_catalog':'https://nbg.gov.ge/en/statistics/statistics-data'}
def fetch(item):
 name,url=item; result={'id':name,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'license':'unverified; do not redistribute'}
 path=ROOT/'data/raw'/name; tmp=path.with_suffix('.partial')
 try:
  with urllib.request.urlopen(url,timeout=45) as r, tmp.open('wb') as f:
   expected=r.headers.get('Content-Length');result['mime']=r.headers.get('Content-Type')
   while True:
    b=r.read(65536)
    if not b:break
    f.write(b)
  if expected and tmp.stat().st_size!=int(expected):raise ValueError('Content-Length mismatch')
  if url.endswith('.zip'):
   with zipfile.ZipFile(tmp) as z:
    if z.testzip():raise ValueError('ZIP CRC failure')
    result['members']=[{'name':i.filename,'bytes':i.file_size} for i in z.infolist()]
  result.update(bytes=tmp.stat().st_size,sha256=hashlib.sha256(tmp.read_bytes()).hexdigest(),status='integrity_pass')
  tmp.replace(path)
 except Exception as e:result.update(status='failed',error=str(e));tmp.unlink(missing_ok=True)
 return result
if __name__=='__main__':
 (ROOT/'data/raw').mkdir(parents=True,exist_ok=True);(ROOT/'reports').mkdir(exist_ok=True)
 records=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,SOURCES.items()))
 (ROOT/'reports/source_manifest.json').write_text(json.dumps(records,indent=2))
 print(json.dumps(records,indent=2))
