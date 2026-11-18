"""Independent meeting-level and headline CPI validation. No production model imports."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import lstsq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/r3_rate_rule'


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def audit():
    vintages = read(ROOT/'data/derived/r3_rate_rule/vintages.csv')
    events = read(ROOT/'archive/legacy/reports/nbg_policy_decisions_2008_onward.csv')
    matrix, changes, dates = [], [], []
    for i,event in enumerate(events):
        date = event['decision_date']
        if '2018' <= date[:4] <= '2024':
            previous = [v for v in vintages if v['report_month']<date[:7]]
            if not previous:
                continue
            v = previous[-1]
            age = 12*(int(date[:4])-int(v['report_month'][:4]))+int(date[5:7])-int(v['report_month'][5:])
            assert 1<=age<=4
            prior = float(events[i-1]['policy_rate_pct'])
            matrix.append([1,prior,float(v['actual_cpi_pct'])-3,float(v['expected_cpi_pct'])-3,float(v['expected_growth_pct'])])
            changes.append(float(event['policy_rate_pct'])-prior)
            dates.append(date)
    x,y = np.array(matrix),np.array(changes)
    checked = read(OUT/'predictions.csv')
    errors = []
    for row in checked:
        index = dates.index(row['date'])
        beta = lstsq(x[:index],y[:index],lapack_driver='gelsy')[0]
        errors.append(abs(float(x[index]@beta)-float(row['primary'])))
    coefficients = read(OUT/'coefficients.csv')
    for row in coefficients:
        mask = np.array([(row['sample']=='through_2024' or d<'2023') and d[:4]!=row['omitted_year'] for d in dates])
        beta = lstsq(x[mask],y[mask],lapack_driver='gelsy')[0]
        for term,value in zip(['intercept','prior_rate','actual_inflation_gap','expected_inflation_gap','expected_growth'],beta):
            assert abs(float(row[term])-value)<1e-8
    assert len(errors)==16 and max(errors)<1e-8
    print(f'{len(coefficients)} coefficient vectors and {len(errors)} predictions match pivoted QR within 1e-8.')


def cpi_audit(path):
    from openpyxl import load_workbook
    lock = json.loads((ROOT/'archive/legacy/reports/nbg_source_manifest.json').read_text())['group_cpi.xlsx']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==lock['sha256']
    rows = list(load_workbook(path,read_only=True,data_only=True)['Georgia'].values)
    quarter_levels = {}
    level = 100
    for col,month in enumerate(rows[3]):
        if isinstance(rows[2][col],int):
            year = rows[2][col]
        if month not in 'I II III IV V VI VII VIII IX X XI XII'.split():
            continue
        relative = rows[4][col]
        if not isinstance(relative,(int,float)) or relative<=0:
            continue
        level *= relative/100
        q = 'I II III IV V VI VII VIII IX X XI XII'.split().index(month)//3+1
        quarter_levels.setdefault((year,q),[]).append(level)
    result = []
    for r in read(ROOT/'data/derived/r3_rate_rule/vintages.csv'):
        year,q = map(int,r['actual_quarter'].split('Q'))
        a,b = quarter_levels[year,q],quarter_levels[year-1,q]
        assert len(a)==len(b)==3
        inflation = 100*(np.mean(a)/np.mean(b)-1)
        result.append(dict(quarter=r['actual_quarter'],chart_pct=r['actual_cpi_pct'],
                           geostat_quarterly_yoy_pct=round(inflation,4),
                           difference_pp=round(float(r['actual_cpi_pct'])-inflation,4)))
    with (OUT/'cpi_crosscheck.csv').open('w') as stream:
        writer = csv.DictWriter(stream,fieldnames=result[0],lineterminator='\n')
        writer.writeheader()
        writer.writerows(result)
    print('Largest CPI difference (pp)',max(abs(r['difference_pp']) for r in result))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--geostat-workbook',type=Path)
    args = parser.parse_args()
    audit()
    if args.geostat_workbook:
        cpi_audit(args.geostat_workbook)
