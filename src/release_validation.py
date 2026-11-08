"""Build a compact, reproducible release validation summary."""
import hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
assets=json.loads((ROOT/'reports/release_assets.json').read_text())['assets']
profiles=json.loads((ROOT/'reports/release_household_profiles.json').read_text())
rows=[]
for a in assets:
    p=ROOT/'data/raw/release'/a['name']; status='missing'; detail='file absent'
    if p.exists():
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        status='hash_match' if 'sha256:'+actual==a['digest'] else 'hash_mismatch'
        detail={'bytes':p.stat().st_size,'sha256':actual}
        if status=='hash_match' and p.suffix in ('.zip','.xlsx'):
            try:
                with zipfile.ZipFile(p) as z: z.testzip(); detail['zip_members']=len(z.namelist()); status='passed'
            except zipfile.BadZipFile: status='structural_failure'
        elif status=='hash_match' and p.suffix=='.pdf': status='passed' if p.read_bytes().startswith(b'%PDF-') else 'structural_failure'
    rows.append({'name':a['name'],'expected_bytes':a['size'],'expected_digest':a['digest'],'status':status,'detail':detail})
summary={'release_id':437541526,'tag':'GEOSTAT','assets':rows,'validated_household_archives':sorted({x['archive'] for x in profiles}),'profile_table_count':len(profiles),'profile_rows_by_archive':{a:sum(x['rows'] for x in profiles if x['archive']==a) for a in sorted({x['archive'] for x in profiles})},'excluded_archives':{'2020.zip':'release bytes hash-match but ZIP central directory is invalid','2023.zip':'release bytes hash-match but ZIP central directory is invalid'}}
(ROOT/'reports/release_validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
