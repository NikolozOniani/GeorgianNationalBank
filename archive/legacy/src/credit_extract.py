"""Extract reviewed NBG cells into a provenance-rich monthly credit dataset.

Read-only XLSX use. Observations remain nominal source values; no interpolation.
"""
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/peer_review';OUT=ROOT/'reports/peer_review'
MONTHS=[f'{y}-{m:02}' for y in range(2020,2025) for m in range(1,13)]


def write_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)


def specifications():
    specs=[]
    def add(id,source,sheet,axis,position,unit,population,definition,check_cell,check_text):
        specs.append(dict(series=id,source_id=source,sheet=sheet,date_axis=axis,position=position,unit=unit,
                          population=population,definition=definition,check_cell=check_cell,check_text=check_text))
    for currency,prefix in [('gel','NC'),('fx','FC')]:
        for residency,col in [('resident','F'),('nonresident','G')]:
            for kind,sheet,unit in [('stock',f'{prefix}-loan(E)','GEL million'),('rate',f'{prefix}-%(E)','percent per year')]:
                add(f'hh_{residency}_{currency}_{kind}','L3.6',sheet,'column_A',col,unit,
                    residency+' households, including individual entrepreneurs',
                    'Month-end outstanding principal' if kind=='stock' else 'Outstanding-loan principal-weighted contractual rate; zero-rate loans excluded',
                    col+'5','to residents' if residency=='resident' else 'to nonresidents')
        add(f'hh_resident_{currency}_sector_stock','L3.12','Total NC' if currency=='gel' else 'Total FC','column_A','H','GEL million',
            'resident households including individual entrepreneurs','Independent sector-table principal stock','H3','Households')
        for base,row in [('total',4),('consumer',6),('housing',7),('business_large',8),('business_sme',9),('auto',10),('lombard',11),('other',12)]:
            row=row if currency=='gel' else row+9
            labels={'total':'In National Currency' if currency=='gel' else 'In Foreign Currency','consumer':'Consumer Loans',
                    'housing':'Mortgage loans for real estate purchase and repair','business_large':'Business loans for large enterprises',
                    'business_sme':'Business loans for SME','auto':'Auto loans','lombard':'Lombard Loans','other':'Other Loans'}
            add(f'hh_all_{currency}_{base}_stock','LPR','HH','row_3',row,'GEL million',
                'resident and nonresident households, including individual entrepreneurs','Purpose-classified month-end principal stock','A'+str(row),labels[base])
        for product,row in [('housing',4),('consumer',22)]:
            add(f'hh_all_{currency}_new_{product}_rate','LMR','Loans_NC' if currency=='gel' else 'Loans_FC','row_3',row,
                'percent per year','resident and nonresident households, including individual entrepreneurs',
                'Monthly loan-inflow-weighted contractual rate, original maturities pooled; excludes zero-rate loans','A'+str(row),'Mortgage' if row==4 else 'Consumer Loans')
        sheet='NC Dep.of Individuals-eng' if currency=='gel' else 'FC Dep.of Individuals-eng'
        for item,col,unit,definition in [('total_stock','B','GEL million','Total month-end deposit principal'),
                                         ('term_stock','E','GEL million','Term deposit month-end principal'),
                                         ('term_rate','N','percent per year','Principal-weighted stock term-deposit contractual rate; excludes zero-rate deposits')]:
            add(f'hh_all_{currency}_deposit_{item}','D3.23',sheet,'column_A',col,unit,
                'resident and nonresident households including individual entrepreneurs',definition,col+'4' if col=='B' else col+'5','Deposits, total' if col=='B' else 'Total')
        add(f'hh_all_{currency}_new_term_deposit_rate','D3.22','Interest Rates on Deposits (EN)','column_A','E' if currency=='gel' else 'H',
            'percent per year','resident and nonresident households including individual entrepreneurs',
            'Monthly term-deposit inflow-weighted contractual rate; excludes zero-rate deposits',
            'E5' if currency=='gel' else 'H5','Households')
        for kind,sheet,unit in [('stock','mortgage loans (ENG)','GEL million'),('rate','mortgage loans,% (ENG)','percent per year')]:
            for flow,col in [('outstanding','I' if currency=='gel' else 'Y'),('new','Q' if currency=='gel' else 'AG')]:
                add(f'hh_all_{currency}_realestate_secured_{flow}_{kind}','L3.8.1',sheet,'column_A',col,unit,
                    'resident and nonresident households including individual entrepreneurs',
                    'Collateral-based real-estate-secured loans; not identical to housing-purpose loans; '+flow+' '+kind,col+'4','Households')
    return specs


def main():
    sources={r['id']:r for r in json.loads((OUT/'sources.json').read_text())}
    needed={s['source_id'] for s in specifications()}
    books={}
    for id,r in sources.items():
        if id not in needed:continue
        path=RAW/r['filename']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=r['sha256']:raise ValueError('Hash mismatch '+id)
        books[id]=openpyxl.load_workbook(path,data_only=True)
    observed=[];manifest=[];metadata=[]
    for spec in specifications():
        s=books[spec['source_id']][spec['sheet']]
        if spec['check_text'].lower() not in str(s[spec['check_cell']].value).lower():
            raise ValueError('Header mismatch '+spec['series'])
        locations=[]
        if spec['date_axis']=='column_A':
            for i in range(1,s.max_row+1):
                if isinstance(s.cell(i,1).value,dt.datetime):locations.append((s.cell(i,1),s[str(spec['position'])+str(i)]))
        else:
            for j in range(1,s.max_column+1):
                if isinstance(s.cell(3,j).value,dt.datetime):locations.append((s.cell(3,j),s.cell(spec['position'],j)))
        dates=[c.value.strftime('%Y-%m') for c,v in locations]
        if len(dates)!=len(set(dates)):raise ValueError('Duplicate dates '+spec['series'])
        lookup={c.value.strftime('%Y-%m'):(c,v) for c,v in locations}
        missing=[]
        for month in MONTHS:
            if month not in lookup:raise ValueError('Date absent '+month+' '+spec['series'])
            datecell,valcell=lookup[month];v=valcell.value
            numeric=isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
            if not numeric:missing.append(month)
            observed.append(dict(month=month,series=spec['series'],value=v if numeric else '',unit=spec['unit'],
                                 source_id=spec['source_id'],sheet=s.title,cell=valcell.coordinate,date_cell=datecell.coordinate,
                                 raw_value=repr(v),source_sha256=sources[spec['source_id']]['sha256']))
        manifest.append(dict(series=spec['series'],available_first=min(dates),available_last=max(dates),
                             primary_expected=60,observed=60-len(missing),missing=len(missing),missing_months=';'.join(missing)))
        metadata.append(spec)
    wide={m:{'month':m} for m in MONTHS}
    for r in observed:wide[r['month']][r['series']]=r['value']
    checks=[]
    for m,r in wide.items():
        for c in ('gel','fx'):
            terms=[r[f'hh_all_{c}_{p}_stock'] for p in ['consumer','housing','business_large','business_sme','auto','lombard','other']]
            delta=sum(terms)-r[f'hh_all_{c}_total_stock']
            checks.append(dict(month=m,currency=c,identity='LPR purpose sum minus total',difference_gel_m=delta,tolerance_gel_m=.01))
            delta=r[f'hh_resident_{c}_stock']+r[f'hh_nonresident_{c}_stock']-r[f'hh_all_{c}_total_stock']
            checks.append(dict(month=m,currency=c,identity='L3.6 resident plus nonresident minus LPR total',difference_gel_m=delta,tolerance_gel_m=.01))
            delta=r[f'hh_resident_{c}_stock']-r[f'hh_resident_{c}_sector_stock']
            checks.append(dict(month=m,currency=c,identity='L3.6 resident minus L3.12 resident',difference_gel_m=delta,tolerance_gel_m=.01))
    failed=[r for r in checks if abs(r['difference_gel_m'])>r['tolerance_gel_m']]
    write_csv(OUT/'credit_observations.csv',observed)
    write_csv(OUT/'credit_monthly_2020_2024.csv',list(wide.values()))
    write_csv(OUT/'series_dictionary.csv',metadata)
    write_csv(OUT/'coverage.csv',manifest)
    write_csv(OUT/'reconciliation.csv',checks)
    # Capture methodological notes in full for audit; do not confuse copied stray
    # data lower in Notes sheets with metadata. Relevant notes occupy first 9 rows.
    notes={id:{str(s.cell(i,1).value).strip():str(s.cell(i,2).value) for i in range(1,10) if s.cell(i,1).value is not None}
           for id,w in books.items() if 'Notes' in w for s in [w['Notes']]}
    (OUT/'workbook_notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
    result=dict(series=len(manifest),observations=len(observed),missing=sum(r['missing'] for r in manifest),
                identities_tested=len(checks),identities_outside_tolerance=len(failed),failures=failed)
    (OUT/'extraction_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='failures'},indent=2))
    if failed:print('Reconciliation discrepancies retained; inspect before using aggregate totals.')


if __name__=='__main__':main()
