"""Reconstruct published component-based ARA and audited interest accounts.

Offline numerical replication: run without flags. --extract requires pinned PDFs;
--acquire downloads missing sources and checks their exact reviewed hashes.
"""
import argparse,csv,hashlib,json,re,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/reserve_foundations';RAW=ROOT/'data/raw/reserve_foundations'
def read(name):
 with (OUT/name).open(newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
def number(s):return float(s.replace(',','').replace('(','-').replace(')','')) if s!='-' else 0.
def extract(sources):
 from pypdf import PdfReader
 rows=[];s=sources['imf2024'];text=PdfReader(RAW/s['filename']).pages[52].extract_text()
 labels={'exports':'Exports (goods and Services)','money_m2':'Broad money (M2)','std_residual':'Short-term debt residual maturity','std_original':'ST debt by original maturity','mlt_amortization':'Ammortization on MLT debt','other_liabilities':'Other liabilities','ara_reported':'ARA Metric','ara_adjusted_reported':'ARA Metric-Adjusted','bank_assets':'Bank ST assets (deposits)','bank_liabilities':'Bank ST liabilities (deposits)','bank_uncovered':'Adjusted banks ST deposit liabilities','reserves':'GIR','coverage_reported':'GIR (Percent of ARA metric)','adjusted_coverage_reported':'GIR (Percent of adjusted ARA metric)','import_months_reported':'GIR (Month of imports)'}
 for key,label in labels.items():
  m=re.search(r'^'+re.escape(label)+r'\s+((?:[\d,.]+\s+){6}[\d,.]+)\s*$',text,re.M)
  if not m:raise ValueError(label)
  for year,v in zip(range(2022,2029),m[1].split()):rows.append(dict(year=year,series=key,value=number(v),unit='percent' if 'coverage' in key else 'months' if 'months' in key else 'USD million',status='historical estimate' if year<=2023 else '2024-vintage projection',source_id='imf2024',pdf_page=53,source_label=label,source_sha256=s['sha256']))
 write('ara_components.csv',rows)
 accounts=[]
 specs={'reserve_cash':'Cash and cash equivalents','reserve_securities':'comprehensive income (“FVOCI”)','reserve_other':'Other','bank_income':'Due from resident financial institutions','policy_securities_income':'comprehensive income','cd_expense':'Debt securities issued','bank_expense':'Due to resident financial institutions','imf_expense':'Due to the International Monetary Fund','customer_expense':'Due to customers','lease_expense':'Interest expense on lease liabilities','amortised_income':'Investments measured at amortised cost','total_expense':'Total interest expense','net_interest':'NET INTEREST INCOME'}
 for sid in ['annual2021','annual2023','annual2024']:
  if sid not in sources:continue
  s=sources[sid];pdf=PdfReader(RAW/s['filename']);page=s['income_page'];t=pdf.pages[page-1].extract_text();years=s['income_years']
  for key,label in specs.items():
   pattern=r'^\s*'+re.escape(label)+r'\s+(?:\d{1,2}\s+)?(\(?[\d,]+\)?|-)\s+(\(?[\d,]+\)?|-)\s*$'
   matches=list(re.finditer(pattern,t,re.M));pairs={m.groups() for m in matches}
   if key=='reserve_other' and matches:pairs={matches[0].groups()} # first Other belongs to reserve block
   if len(pairs)!=1:raise ValueError((sid,key,pairs))
   for y,v in zip(years,next(iter(pairs))):accounts.append(dict(year=y,series=key,value_gel_thousand=number(v),source_id=sid,pdf_page=page,source_label=label,source_sha256=s['sha256']))
  # Negative interest is a separate line, important for low-rate reserve returns.
  for key,label in [('negative_reserve_interest','Negative interest on financial assets (International reserves)'),('negative_liability_income','Negative interest on financial liabilities')]:
   ms=list(re.finditer(r'^\s*'+re.escape(label)+r'\s+(\(?[\d,]+\)?|-)\s+(\(?[\d,]+\)?|-)\s*$',t,re.M))
   if key=='negative_liability_income':ms=ms[:1] # monetary-policy block only
   vals=ms[0].groups() if ms else ('-','-')
   for y,v in zip(years,vals):accounts.append(dict(year=y,series=key,value_gel_thousand=number(v),source_id=sid,pdf_page=page,source_label=label if ms else 'No separately reported line on statement',source_sha256=s['sha256']))
  for key,vals in [('other_negative_liability_income',ms_unused(t)),('other_income_extra',other_extra(t))]:
   for y,v in zip(years,vals):accounts.append(dict(year=y,series=key,value_gel_thousand=number(v),source_id=sid,pdf_page=page,source_label='Other interest income block; absent separate line treated as zero',source_sha256=s['sha256']))
  for offset,key,start,end in [(2,'fx_assets','Foreign currency assets','National currency assets'),(3,'fx_liabilities','Foreign currency liabilities','National currency liabilities')]:
   bt=pdf.pages[page+offset-1].extract_text();block=bt.split(start,1)[1].split(end,1)[0]
   pairs=re.findall(r'^\s*([\d,]+)\s+([\d,]+)\s*$',block,re.M)
   if not pairs:raise ValueError('FX total '+sid)
   for y,v in zip(years,pairs[-1]):accounts.append(dict(year=y,series=key,value_gel_thousand=number(v),source_id=sid,pdf_page=page+offset,source_label='Total '+start,source_sha256=s['sha256']))
 write('interest_observations.csv',accounts)
def ms_unused(t):
 ms=list(re.finditer(r'^\s*Negative interest on financial liabilities\s+(\(?[\d,]+\)?|-)\s+(\(?[\d,]+\)?|-)\s*$',t,re.M))
 return ms[1].groups() if len(ms)>1 and ms[1].start()<t.index('Total interest income') else ('-','-')
def other_extra(t):
 block=t.split('Other interest income',1)[1].split('Total interest income',1)[0]
 m=re.search(r'^\s*Other\s+([\d,]+)\s+([\d,]+)\s*$',block,re.M)
 return m.groups() if m else ('-','-')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--extract',action='store_true');ap.add_argument('--acquire',action='store_true');a=ap.parse_args();OUT.mkdir(exist_ok=True);RAW.mkdir(exist_ok=True)
 sources={s['id']:s for s in json.loads((OUT/'sources.json').read_text())}
 if a.acquire or a.extract:
  for s in sources.values():
   p=RAW/s['filename']
   if not p.exists() and a.acquire:
    temp=p.with_suffix('.partial');temp.write_bytes(urllib.request.urlopen(urllib.parse.quote(s['url'],safe=':/?=%&'),timeout=60).read())
    if hashlib.sha256(temp.read_bytes()).hexdigest()!=s['sha256']:raise ValueError('Changed vintage '+s['id'])
    temp.replace(p)
   if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:raise ValueError('Source hash '+s['id'])
 if a.extract:extract(sources)
 lock=OUT/'inputs.lock.json'
 if lock.exists():
  for name,sha in json.loads(lock.read_text()).items():
   if hashlib.sha256((OUT/name).read_bytes()).hexdigest()!=sha:raise ValueError('Changed processed input '+name)
 d={(int(r['year']),r['series']):float(r['value']) for r in read('ara_components.csv')};results=[];contributions=[];targets=[]
 for y in range(2022,2029):
  v=lambda k:d[y,k];parts={k:w*v(k) for k,w in [('exports',.05),('money_m2',.05),('std_residual',.30),('other_liabilities',.15)]};ara=sum(parts.values());gap=ara-v('ara_reported')
  assert abs(gap)<=.8,'ARA difference exceeds rounding bound'
  adjusted=ara-.3*min(v('bank_assets'),v('bank_liabilities'))
  results.append(dict(year=y,status='historical estimate' if y<=2023 else 'projection, not realized data',ara_rebuilt_usd_m=ara,ara_reported_usd_m=v('ara_reported'),ara_residual_usd_m=gap,reserves_usd_m=v('reserves'),coverage_pct=100*v('reserves')/ara,reported_coverage_pct=v('coverage_reported'),reserves_to_m2_pct=100*v('reserves')/v('money_m2'),reserves_to_std_pct=100*v('reserves')/v('std_residual'),std_component_residual_usd_m=v('std_residual')-v('std_original')-v('mlt_amortization'),simple_net_bank_adjusted_ara_usd_m=adjusted,published_adjusted_ara_usd_m=v('ara_adjusted_reported'),adjustment_residual_usd_m=adjusted-v('ara_adjusted_reported')))
  contributions += [dict(year=y,component=k,contribution_usd_m=z,share_pct=100*z/ara) for k,z in parts.items()]
  if y<=2023:
   for target in (1,1.3,1.45,1.5):
    extra=max(0,target*ara-v('reserves'))
    for spread in (.01,.02,.04):targets.append(dict(year=y,target_ara_pct=100*target,target_reserves_usd_m=target*ara,extra_reserves_usd_m=extra,assumed_net_carry_pct=100*spread,conditional_annual_cost_usd_m=extra*spread,scope='Retrospective frozen 2024-vintage denominator; assumed marginal net carry, not measured cost or optimum'))
 write('ara_reconstruction.csv',results);write('ara_contributions.csv',contributions);write('reserve_level_scenarios.csv',targets)
 data=read('interest_observations.csv');years=sorted({int(r['year']) for r in data});annual=[];overlap=[]
 for y in years:
  by={}
  for r in data:
   if int(r['year'])==y:by.setdefault(r['series'],[]).append(r)
  v=lambda k:float(by[k][-1]['value_gel_thousand'])/1000
  for k,rs in by.items():
   if len(rs)>1:
    diff=float(rs[-1]['value_gel_thousand'])-float(rs[0]['value_gel_thousand']);overlap.append(dict(year=y,series=k,revision_gel_thousand=diff));assert diff==0
  reserve=sum(v(k) for k in ['reserve_cash','reserve_securities','reserve_other']);policy=v('bank_income')+v('policy_securities_income')+v('negative_liability_income');expense=-v('cd_expense')-v('bank_expense')
  all_income=reserve+policy+v('amortised_income')+v('other_negative_liability_income')+v('other_income_extra')
  all_expenses=sum(v(k) for k in ['cd_expense','bank_expense','imf_expense','customer_expense','lease_expense','negative_reserve_interest'])
  assert abs(all_income+all_expenses-v('net_interest'))<.00001,'Income reconciliation '+str(y)
  assert abs(all_expenses-v('total_expense'))<.00001,'Expense reconciliation '+str(y)
  annual.append(dict(year=y,reserve_gross_interest_gel_m=reserve,negative_reserve_interest_gel_m=-v('negative_reserve_interest'),reserve_interest_after_negative_gel_m=reserve+v('negative_reserve_interest'),policy_interest_income_gel_m=policy,policy_interest_expense_gel_m=expense,policy_net_interest_gel_m=policy-expense,imf_interest_expense_gel_m=-v('imf_expense'),total_interest_expense_gel_m=-v('total_expense'),total_net_interest_gel_m=v('net_interest'),fx_assets_gel_m=v('fx_assets'),fx_liabilities_gel_m=v('fx_liabilities'),net_fx_accounting_position_gel_m=v('fx_assets')-v('fx_liabilities'),net_interest_identity_residual_gel_m=all_income+all_expenses-v('net_interest')))
 write('historical_interest.csv',annual)
 if overlap:write('comparative_column_checks.csv',overlap)
 (OUT/'validation.json').write_text(json.dumps(dict(ara_rows=len(results),ara_max_residual_usd_m=max(abs(r['ara_residual_usd_m']) for r in results),interest_years=years,overlap_checks=len(overlap),adjusted_metric_status='not reconciled by simple net-deposit substitution; residuals retained',source_hashes={s['id']:s['sha256'] for s in sources.values()}),indent=2)+'\n')
 print(json.dumps({'ara':results[:2],'interest':annual},indent=2))
if __name__=='__main__':main()
