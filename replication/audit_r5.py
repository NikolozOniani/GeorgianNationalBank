"""Independent R5 audit: compare public tables with raw survey joins and labeled CPI cells.

Runs separately from src/r5_exposure.py. Uses fixed source anchors, calendar products,
and weighted SQL aggregations to avoid reusing the production implementation.
"""
import argparse
import csv
import hashlib
import json
import math
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from collections import defaultdict

import numpy as np
import openpyxl
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT/'reports/r5_2026_11_13'
BASE = ROOT/'data/derived/episode_2026_11_09'
# Independently inspected row numbers on the Georgia sheet, including both collisions.
PRICES = {
    8: (11, 'Food', 'food'), 9: (12, 'Non-alcoholic beverages', 'drink'),
    11: (21, 'Alcoholic beverages', 'alcohol'), 13: (3, 'Clothing and footwear', 'tansacmeli'),
    22: (5, 'Furnishings, household equipment and routine maintenance of the house', 'saojaxo'),
    29: (6, 'Health', 'samedicino'), 16: (4, 'Housing, water, electricity, gas and other fuels', 'energia'),
    33: (7, 'Transport', 'transporti'), 48: (10, 'Education', 'ganatleba'),
}


def close(actual, expected):
    if not math.isclose(actual, expected, rel_tol=2e-12, abs_tol=1.1e-8):
        raise ValueError(f'Audit mismatch: {actual} vs {expected}')


def report(name):
    with (REPORT/(name+'.csv')).open() as stream:
        return list(csv.DictReader(stream))


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpi(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb['Georgia'].values)
    wb.close()
    months = 'I II III IV V VI VII VIII IX X XI XII'.split()
    result = {}
    for year in range(2020,2026):
        start = rows[2].index(year)
        if list(rows[3][start:start+12]) != months:
            raise ValueError('CPI year layout')
        for number,(code,label,_) in PRICES.items():
            row = rows[number-1]
            if row[:3] != (3 if number in (8,9,11) else 2, code, label):
                raise ValueError(f'Unexpected source identity in row {number}')
            result[year,code] = [float(x)/100 for x in row[start:start+12]]
    return result


def survey_db(zpath, db):
    names = ('sysschedule','tblexpenditures','familysize','tblincomes','conspurch_03')
    with zipfile.ZipFile(zpath) as z, tempfile.TemporaryDirectory() as tmp:
        for name in names:
            member, = (n for n in z.namelist() if Path(n).name == name+'.sav')
            path = Path(tmp)/'input.sav'
            path.write_bytes(z.read(member))
            frame, _ = pyreadstat.read_sav(path)
            frame.to_sql(name,db,index=False)
    # Select product families by decimal strings, retaining all other purchases in the residual.
    db.execute("""CREATE TEMP VIEW diary AS SELECT UID,
        SUM(CASE WHEN printf('%d',ProductCode) GLOB '11[0-9][0-9][0-9]' THEN Paid ELSE 0 END) food,
        SUM(CASE WHEN printf('%d',ProductCode) GLOB '12[0-9][0-9][0-9]' THEN Paid ELSE 0 END) drink,
        SUM(CASE WHEN printf('%d',ProductCode) GLOB '21[0-9][0-9][0-9]' THEN Paid ELSE 0 END) alcohol
        FROM conspurch_03 GROUP BY UID""")
    db.execute("""CREATE TEMP TABLE households AS SELECT e.*, s.Weights w, s.DiaryID diary,
        CAST(strftime('%m',s.MonthYear) AS INT) m, s.UrbanOrRural urban,
        f.Pensioner_age_man+f.Pensioner_age_Woman pension, i.Ucxoetidan remit,
        COALESCE(a.food,0) food, COALESCE(a.drink,0) drink, COALESCE(a.alcohol,0) alcohol,
        1 + CAST(5*(SUM(s.Weights) OVER (ORDER BY e.MTlianimoxmareba_EqAdScale,e.UID)
           - 0.5*s.Weights)/SUM(s.Weights) OVER () AS INT) quintile
        FROM sysschedule s JOIN tblexpenditures e USING(UID) JOIN familysize f USING(UID)
        JOIN tblincomes i USING(UID) LEFT JOIN diary a USING(UID)""")


def audit_groups(year, zpath, indices):
    categories = {(r['group'],r['level'],int(r['cpi'])):r for r in report('category_exposures') if int(r['year'])==year}
    checked = 0
    with sqlite3.connect(':memory:') as db:
        survey_db(zpath, db)
        publication_checks = {}
        if year == 2025:
            # Geostat, Indicators of Living Conditions 2025, page 5. Round to source precision.
            indicators = [
                ('urban_monthly_expenditure_gel', 'SUM(w*MTlianixarjebi_)/SUM(w)', 'urban=1', 2015, 0),
                ('rural_monthly_expenditure_gel', 'SUM(w*MTlianixarjebi_)/SUM(w)', 'urban=2', 1799, 0),
                ('cash_consumption_pct_expenditure', '100*SUM(w*samomxmXarjebi)/SUM(w*MTlianixarjebi_)', '1', 69.3, 1),
                ('food_beverage_tobacco_pct_cash_consumption', '100*SUM(w*sursati__sasmeli__Tambaqo)/SUM(w*samomxmXarjebi)', '1', 38.7, 1),
            ]
            for key, expr, condition, benchmark, digits in indicators:
                actual, = db.execute(f'SELECT {expr} FROM households WHERE {condition}').fetchone()
                if round(actual, digits) != benchmark:
                    raise ValueError(key+' publication mismatch')
                publication_checks[key] = dict(calculated=round(actual,7),published=benchmark)
        for row in report('groups'):
            if int(row['year'])!=year:
                continue
            label = row['level']
            field, value = {
                'all':('1',1), 'quintile':('quintile',int(label) if label.isdigit() else 0),
                'residence':('urban',1 if label=='urban' else 2),
                'pension_age':('pension>0',int(label=='yes')),
                'recipient':('remit>0',int(label=='positive')),
            }[row['group']]
            where=f' FROM households WHERE ({field})=?'
            weight,total,money,count,diaries=db.execute(
                'SELECT SUM(w),SUM(w*MTlianimoxmareba_),SUM(w*remit),COUNT(*),COUNT(DISTINCT diary)'+where,(value,)).fetchone()
            close(count,int(row['records']))
            close(diaries,int(row['diaries']))
            close(weight,float(row['weight_sum']))
            close(total/weight,float(row['consumption_gel']))
            close(.01*money/weight,float(row['loss_all_usd_gel']))
            matched = december = approximate = 0.
            for code,_,col in PRICES.values():
                means=db.execute(f'SELECT m,SUM(w*{col})'+where+' GROUP BY m',(value,))
                amounts=[(x/weight,math.prod(indices[year,code][m:])) for m,x in means]
                at_survey=sum(x for x,_ in amounts)
                at_dec=sum(x*k for x,k in amounts)
                cell=categories[row['group'],label,code]
                close(at_survey,float(cell['survey_gel']))
                close(at_dec,float(cell['dec_gel']))
                close(100*at_survey/(total/weight),float(cell['share_pct']))
                matched+=at_survey
                december+=at_dec
                if code in (4,5):
                    approximate+=at_survey
                checked+=1
            close(100*(1-matched/(total/weight)),float(row['unmatched_pct']))
            close(100*(1-(matched-approximate)/(total/weight)),float(row['strict_unmatched_pct']))
            close(.0025*december,float(row['saving_025_dec_gel']))
            close(.0025*matched-.01*money/weight,float(row['two_channel_all_usd_survey_gel']))
            # Independently compute cluster scores on all three reported scenario variables.
            scores = defaultdict(lambda: [0.,0.,0.])
            cols = [col for _,_,col in PRICES.values()]
            fields = ','.join(cols)
            factors = {m:[math.prod(indices[year,code][m:]) for code,_,_ in PRICES.values()]
                       for m in range(1,13)}
            centers = [.0025*december,.01*money/weight,.0025*matched-.01*money/weight]
            for diary,m,w,remit,*spending in db.execute('SELECT diary,m,w,remit,'+fields+where,(value,)):
                outcomes = [.0025*sum(x*k for x,k in zip(spending,factors[m])), .01*remit,
                            .0025*sum(spending)-.01*remit]
                for j,mean in enumerate(centers):
                    scores[diary][j] += w*(outcomes[j]-mean)/weight
            for j,column in enumerate(('saving_se','loss_se','two_channel_se')):
                se = math.sqrt(diaries/(diaries-1)*sum(score[j]**2 for score in scores.values()))
                close(se,float(row[column]))
        ids={r[0] for r in db.execute('SELECT DISTINCT diary FROM households')}
    return checked,ids,publication_checks


def audit_diagnostics(indices):
    def monthly(file,field):
        d=pd.read_csv(BASE/file,parse_dates=['date']).set_index('date')
        return np.log(d[field].resample('MS').mean()).diff()*100
    fx=monthly('official_fx_daily.csv','usd_gel')
    usd=monthly('broad_dollar_daily.csv','index')
    rows = report('price_diagnostics')
    expected = {(c,k) for c,_,_ in PRICES.values() for k in (0,1,3)}
    observed = {(int(r['code']),int(r['lag_months'])) for r in rows}
    if observed != expected or len(rows) != len(expected):
        raise ValueError('Duplicate or missing diagnostic specification')
    checked=0
    for row in rows:
        code,lag=int(row['code']),int(row['lag_months'])
        dates=pd.date_range('2020-01-01','2024-12-01',freq='MS')
        y=pd.Series([100*math.log(indices[t.year,code][t.month-1]) for t in dates],index=dates)
        data=pd.DataFrame({'y':y,'previous':y.shift(),'x':fx.shift(lag),'usd':usd.shift(lag)}).reindex(dates).dropna()
        # Partial out month-of-year means, then solve the centered system by QR.
        data['app']=data.x.clip(upper=0)
        data['dep']=data.x.clip(lower=0)
        centered=data-data.groupby(data.index.month).transform('mean')
        q,r=np.linalg.qr(centered[['app','dep','usd','previous']].values)
        beta=np.linalg.solve(r,q.T@centered.y)
        close(beta[0],float(row['appreciation_slope']))
        close(beta[1],float(row['depreciation_slope']))
        if (data.index[0].strftime('%Y-%m'), data.index[-1].strftime('%Y-%m')) != (row['first'], row['last']):
            raise ValueError('Diagnostic sample dates differ')
        close((data.x<0).sum(),float(row['appreciation_months']))
        close((data.x>0).sum(),float(row['depreciation_months']))
        close(len(data),float(row['n']))
        checked+=1
    return checked


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--release-dir',type=Path,required=True)
    p.add_argument('--group-cpi',type=Path,required=True)
    args=p.parse_args()
    indices=cpi(args.group_cpi)
    diary_sets=[]
    checked=0
    publication_checks={}
    files=[args.group_cpi, BASE/'official_fx_daily.csv',BASE/'broad_dollar_daily.csv']
    for year in (2024,2025):
        path=args.release_dir/f'{year}.zip'
        files.append(path)
        count,diaries,additional=audit_groups(year,path,indices)
        checked+=count
        diary_sets.append(diaries)
        publication_checks.update(additional)
    fits=audit_diagnostics(indices)
    if (checked,fits)!=(216,27):
        raise ValueError('Incomplete audit')
    result=dict(independent_category_cells=checked,independent_diagnostic_fits=fits,
                          independent_group_standard_errors=3*len(report('groups')),
                          additional_2025_publication_checks=publication_checks,
                          shared_diary_ids=len(set.intersection(*diary_sets)),
                          sha256={p.name:filehash(p) for p in files})
    expected=json.loads((REPORT/'independent_checks.json').read_text())
    if result != expected:
        raise ValueError('Independent audit or source hashes differ from the recorded checkpoint')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
