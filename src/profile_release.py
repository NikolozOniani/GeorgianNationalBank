"""Schema and row-count validation for verified household release archives."""
import json, pathlib, tempfile, zipfile
import pyreadstat
ROOT=pathlib.Path(__file__).resolve().parents[1]
out=[]
for archive in sorted((ROOT/'data/raw/release').glob('*.zip')):
    if archive.name in ('2020.zip','2023.zip'): continue
    with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory() as td:
        for member in z.namelist():
            if not member.lower().endswith('.sav'): continue
            p=pathlib.Path(td)/'table.sav'; p.write_bytes(z.read(member))
            data,meta=pyreadstat.read_sav(str(p),output_format='dict')
            n=len(next(iter(data.values()),[])); uid=data.get('UID',[])
            out.append({'archive':archive.name,'table':member,'rows':n,
                        'columns':meta.column_names,
                        'uid_nonmissing':sum(v is not None for v in uid),
                        'uid_unique':len(set(v for v in uid if v is not None)) if uid else None})
(ROOT/'reports/release_household_profiles.json').write_text(json.dumps(out,indent=2)+'\n')
print('tables',len(out),'archives',sorted({x['archive'] for x in out}))
