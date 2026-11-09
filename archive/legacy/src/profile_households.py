"""Profile SPSS tables without exporting individual observations."""
import pathlib,zipfile,tempfile,json
import pyreadstat
ROOT=pathlib.Path(__file__).resolve().parents[1]
profiles=[]
for archive in sorted((ROOT/'data/raw').glob('hies*')):
 with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory() as td:
  for name in z.namelist():
   if not name.lower().endswith('.sav'):continue
   p=pathlib.Path(td)/'table.sav';p.write_bytes(z.read(name))
   data,meta=pyreadstat.read_sav(str(p),output_format='dict')
   cols={k:{'missing':sum(v is None or (isinstance(v,float) and v!=v) for v in vals)} for k,vals in data.items()}
   n=len(next(iter(data.values()),[]))
   for col in cols.values():col['missing_rate']=col['missing']/n if n else None
   profiles.append({'archive':archive.name,'table':name,'rows':n,'columns':cols,'labels':meta.column_names_to_labels})
(ROOT/'reports/household_profiles.json').write_text(json.dumps(profiles,indent=2,ensure_ascii=False))
print([(r['archive'],r['table'].split('/')[-1],r['rows']) for r in profiles])
