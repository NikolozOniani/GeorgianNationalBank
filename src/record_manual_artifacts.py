"""Record already-acquired artifacts awaiting manual transfer; no network calls."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    sources=json.loads((ROOT/'data/source_manifest.json').read_text())
    records=[]
    for r in sources:
        records.append(dict(path=r['local_path'],sha256=r.get('sha256'),bytes=r.get('bytes'),
                            original_url=r['url'],kind='original_source',
                            disposition='Local acquisition predates manual-transfer instruction; not uploaded in this commit'))
    for name in ['reserve_liquidity_cells.csv','money_transfers_country.csv']:
        p=ROOT/'data/derived/episode_2026_11_09'/name
        records.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                            bytes=p.stat().st_size,original_url=None,kind='generated_large_output',
                            disposition='Awaiting author manual commit; compact validation counterpart committed'))
    (ROOT/'data/manual_artifacts.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')


if __name__=='__main__':main()
