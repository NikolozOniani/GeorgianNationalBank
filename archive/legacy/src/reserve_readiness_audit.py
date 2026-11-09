"""Read-only audit of committed evidence; writes only the readiness-audit folder."""
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/reserve_readiness'

def rows(path):
    with (ROOT/path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
    OUT.mkdir(exist_ok=True)
    panel=rows('reports/nbg_policy_monthly_2020_2024.csv')
    coverage=[]
    for k in panel[0]:
        if k=='month':continue
        n=sum(r[k]!='' for r in panel)
        coverage.append(dict(series=k,expected_months=60,observed=n,missing=60-n,missing_rate=(60-n)/60))
    with (OUT/'monthly_coverage.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=coverage[0]);w.writeheader();w.writerows(coverage)
    a={(int(r['year']),r['series']):Decimal(r['value_gel_thousand'])/1000 for r in rows('reports/paper/annual_accounts.csv')}
    checks=[]
    for year in (2023,2024):
        get=lambda k:a[year,k]
        income=sum(get(k) for k in ['reserve_cash_interest','reserve_security_interest','reserve_other_interest','bank_interest_income','policy_security_interest','other_interest_income'])
        expense=sum(get(k) for k in ['cd_interest_expense','bank_interest_expense','imf_interest_expense','customer_interest_expense','lease_interest_expense'])
        checks.append(dict(year=year,net_interest_residual=str(income+expense-get('net_interest_income')),
                           balance_sheet_residual=str(get('total_assets')-get('total_liabilities')-get('total_equity'))))
    locks={}
    for filename in ['reports/paper/input_hashes.json','reports/peer_review/analysis_inputs.lock.json']:
        for p,h in json.loads((ROOT/filename).read_text()).items():locks[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    with localcontext() as c:
        c.prec=40
        log=(Decimal('1.2')/Decimal('1.1')).ln()
        delta_D=-Decimal('.1')*log
        expected=Decimal('.1')*Decimal('.1')*Decimal('.5')*(-delta_D)
        normal_cost=Decimal('.9')*Decimal('.01')*Decimal('.1')
        audit=dict(dollarization_change_pp=str(100*delta_D),expected_loss_reduction_pct_gdp=str(100*expected),
                   assumed_normal_state_carry_pct_gdp=str(100*normal_cost),isolated_ratio=str(expected/normal_cost),
                   scope='Single common horizon assumed; no calibrated duration, utility-equivalent welfare or full insurance benefit')
    result=dict(baseline_commit='54988b512af3a8373c5e80d1daaa12ba1fbae5f1',months=len(panel),
                unique_months=len({r['month'] for r in panel}),first=panel[0]['month'],last=panel[-1]['month'],
                monthly_coverage_file='monthly_coverage.csv',annual_account_rows=len(a),
                quarterly_external_rows=len(rows('reports/nbg_external_quarterly_2020_2024.csv')),
                annual_intervention_rows=len(rows('reports/nbg_fx_annual_benchmarks.csv')),
                verified_auction_rows=len(rows('reports/nbg_auction_events_verified.csv')),
                locked_input_hashes=locks,independent_decimal_accounting=checks,independent_channel_arithmetic=audit)
    assert len(panel)==len({r['month'] for r in panel})==60
    assert all(locks.values())
    assert all(Decimal(r[k])==0 for r in checks for k in ('net_interest_residual','balance_sheet_residual'))
    result['status']='passed: arithmetic and input integrity; not economic adequacy'
    (OUT/'audit_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
