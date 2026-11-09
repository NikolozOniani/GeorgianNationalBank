"""Offline accounting checks and transparent joins of observed public data.

This is validation/accounting, not a causal or optimal-reserve estimator.
"""
from __future__ import annotations
import argparse
import calendar
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/derived/episode_2026_11_09'
REPORT=ROOT/'reports/acquisition_2026_11_09'


def read(name):
    return list(csv.DictReader((DATA/(name+'.csv')).open()))


def f(x):
    return float(x) if x not in ['',None] else None


def put(name,rows):
    REPORT.mkdir(parents=True,exist_ok=True)
    with (REPORT/(name+'.csv')).open('w',newline='') as file:
        writer=csv.DictWriter(file,list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)


def validate():
    checks=[]
    def check(name,ok,detail,qualification=None):
        checks.append(dict(check=name,passed=bool(ok),detail=detail,
                           qualification=qualification if not ok else None))
    catalogue=json.loads((DATA/'catalogue.json').read_text())
    manual={'reserve_liquidity_cells.csv','money_transfers_country.csv'}
    checked=[r for r in catalogue if (ROOT/r['file']).exists()]
    missing_outputs=[r['file'] for r in catalogue if not (ROOT/r['file']).exists()]
    check('extracted_output_hashes',all(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['sha256'] for r in checked)
          and all(Path(p).name in manual for p in missing_outputs),dict(checked=len(checked),manual_files_absent=missing_outputs))
    sources=json.loads((ROOT/'data/source_manifest.json').read_text())
    # Missing download caches are not silently declared hash-verified.
    available=[r for r in sources if r['status']=='acquired' and (ROOT/r['local_path']).exists()]
    check('available_source_hashes',all(hashlib.sha256((ROOT/r['local_path']).read_bytes()).hexdigest()==r['sha256'] for r in available),len(available))
    missing_raw=[r['id'] for r in sources if r['status']=='acquired' and not (ROOT/r['local_path']).exists()]
    for name,key in [('intervention_monthly','month'),('official_fx_daily','date'),('neer_daily','date'),
                     ('tibr_daily','date'),('reserve_stocks_monthly','date'),('money_aggregates_monthly','date')]:
        rows=read(name);check(name+'_unique_dates',len({r[key] for r in rows})==len(rows),len(rows))
    intervention={r['month']:r for r in read('intervention_monthly')}
    check('nonauction_gross_unknown',all(r['nonauction_gross_purchases_usdm']==r['nonauction_gross_sales_usdm']=='' for r in intervention.values()),'Net never split into fabricated gross flows')
    check('purchase_sign',all(abs(f(r['net_market_purchases_usdm'])-(f(r['nonauction_net_purchases_usdm'])+f(r['auction_purchases_usdm'])-f(r['auction_sales_usdm'])))<1e-8 for r in intervention.values()),'NBG purchases positive; sales negative in net')
    annual=[]
    benchmark={2023:(166.8,1445.5,1278.7),2024:(382.1,-52.65,-434.75),2025:(0,2432.5,2432.5)}
    for y in range(2020,2027):
        rows=[r for m,r in intervention.items() if m.startswith(str(y))]
        ap=sum(f(r['auction_purchases_usdm']) for r in rows);s=sum(f(r['auction_sales_usdm']) for r in rows)
        b=sum(f(r['nonauction_net_purchases_usdm']) for r in rows);n=ap-s+b
        target=benchmark.get(y)
        annual.append(dict(year=y,months=len(rows),auction_purchases_usdm=ap,auction_sales_usdm=s,nonauction_net_purchases_usdm=b,
                           total_net_purchases_usdm=n,annual_report_net_usdm=target[2] if target else None,
                           difference_usdm=n-target[2] if target else None,
                           status='unresolved historical discrepancy' if y==2023 else 'reconciled' if target else 'no annual benchmark checked',
                           source='fx_market; annual2025 p47' if y==2025 else 'fx_market; archived annual benchmarks' if target else 'fx_market'))
    put('intervention_reconciliation',annual)
    a={r['year']:r for r in annual}
    check('2024_annual_reconciles',abs(a[2024]['difference_usdm'])<1e-8,a[2024]['difference_usdm'])
    check('2025_annual_reconciles',abs(a[2025]['difference_usdm'])<1e-8,a[2025]['difference_usdm'])
    check('2023_discrepancy_explicit',a[2023]['status']=='unresolved historical discrepancy' and abs(a[2023]['difference_usdm']-.55)<1e-6,a[2023])
    jan_jul=sum(f(r['net_market_purchases_usdm']) for m,r in intervention.items() if '2026-01'<=m<='2026-07')
    check('2026_Jan_Jul_press_reconciles',abs(jan_jul-2566.6)<=.05,dict(computed_usdm=jan_jul,press_usdm=2566.6,tolerance_usdm=.05,source='reserves_aug2026, published 2026-09-07'))
    events=read('fx_auction_events');by_month=collections.defaultdict(float)
    for r in events:by_month[r['date'][:7]]+=(f(r['purchases_usd'])-f(r['sales_usd']))/1e6
    differences=[]
    for m,r in intervention.items():
        if m>'2024-10':continue
        residual=by_month[m]-(f(r['auction_purchases_usdm'])-f(r['auction_sales_usdm']))
        if abs(residual)>.00001:differences.append(dict(month=m,event_minus_monthly_usdm=residual))
    check('dated_auction_vs_monthly',not differences,differences or 'Event-file sums reconcile through its last month',
          'Do not force trade-date sums to match settlement-period tables. September 30 2021 and August 31 2022 events match adjacent-month differences; exact frequency convention requires confirmation.')
    year_errors=[]
    for y in range(2020,2025):
        event_net=sum((f(r['purchases_usd'])-f(r['sales_usd']))/1e6 for r in events if r['date'].startswith(str(y)))
        year_errors.append(event_net-(a[y]['auction_purchases_usdm']-a[y]['auction_sales_usdm']))
    check('dated_auction_calendar_year_totals',max(map(abs,year_errors))<1e-7,year_errors)
    stocks={r['date']:r for r in read('reserve_stocks_monthly')}
    errors={d:f(r['reserves_usdm'])-sum(f(r[k]) for k in ['fx_usdm','sdr_usdm','imf_position_usdm','gold_usdm','other_usdm']) for d,r in stocks.items()}
    check('reserve_component_sum',max(map(abs,errors.values()))<1e-7,max(map(abs,errors.values())))
    irfcl=read('reserve_liquidity_reported');r1={r['date']:f(r['value']) for r in irfcl if r['source_cell']=='D21'}
    rr=[dict(date=d,official_stock_usdm=f(stocks[d]['reserves_usdm']),template_usdm=v,
             difference_usdm=f(stocks[d]['reserves_usdm'])-v) for d,v in sorted(r1.items())]
    put('reserve_template_reconciliation',rr)
    check('reserve_template_matches_stocks',all(abs(r['difference_usdm'])<1e-6 for r in rr),max(abs(r['difference_usdm']) for r in rr))
    for dataset,identities,tolerance in [('money_market',[(4,[5,6]),(12,[13,14])],1e-6),
                                        ('central_bank',[(4,[5,-12]),(20,[21,-25]),(34,[35,36,39])],.0031)]:
        series=collections.defaultdict(dict)
        for r in read(dataset):series[r['date']][int(r['series_row'])]=f(r['value'])
        residuals=[values[left]-sum(values[abs(v)]*(1 if v>0 else -1) for v in right) for values in series.values() for left,right in identities]
        check(dataset+'_identities',max(map(abs,residuals))<tolerance,dict(max_abs_residual_gelm=max(map(abs,residuals)),tolerance_gelm=tolerance))
    market=collections.defaultdict(dict)
    for r in read('money_market'):market[r['date']][int(r['series_row'])]=f(r['value'])
    errors=[dict(date=d,reported_total_gelm=v[8],components_gelm=sum(v[k] for k in [9,10,11]),
                 residual_gelm=v[8]-sum(v[k] for k in [9,10,11])) for d,v in market.items() if abs(v[8]-sum(v[k] for k in [9,10,11]))>1e-6]
    check('money_market_security_total',not errors,errors,
          'Quarantine the reported government-security total on 2026-07-30; retain original. No replacement total is treated as an observation.')
    cds=read('cd_auctions_events')
    errors=[f(r['nominal_allocated_gel'])-f(r['settlement_gel'])-f(r['discount_gel']) for r in cds]
    check('CD_contract_discount_identity',max(map(abs,errors))<.011,max(map(abs,errors)))
    check('operation_maturities',all(r['maturity_date']>=r['date'] for n in ['refinancing_events','cd_auctions_events','repo_events'] for r in read(n)),'Date of issue/trade <= contractual maturity; maturity may follow vintage cutoff')
    accounts={(r['year'],r['series']):f(r['value_gelm']) for r in read('annual_interest_accounts')}
    ar=[]
    for y in ['2024','2025']:
        get=lambda k:accounts[(y,k)]
        ar.extend([get('reserve_interest_total')-sum(get('reserve_interest_'+s) for s in ['cash','fvoci','other']),
                   get('policy_interest_total')-get('policy_interest_financial_institutions')-get('policy_interest_securities'),
                   get('policy_expense_total')-get('policy_expense_securities')-get('policy_expense_financial_institutions'),
                   get('net_interest_income')-get('interest_income_total')-get('interest_expense_total')])
    check('annual_interest_accounting',max(map(abs,ar))<1e-8,dict(max_residual_gelm=max(map(abs,ar)),not_marginal_reserve_cost=True))
    transfer={(r['date'],r['direction']):f(r['value_usdm']) for r in read('money_transfers_canonical')}
    overlap=[abs(f(r['value_usdm'])-transfer[(r['date'],r['direction'])]) for r in read('money_transfers_monthly') if r['value_usdm']]
    check('transfer_workbook_overlap',max(overlap)<1e-7,dict(overlap_observations=len(overlap),max_residual_usdm=max(overlap),recovered_2024_months=12),
          'Small cross-file discrepancies retained; by-country workbook used because it has 2024 and reconciles to its country components. Not evidence that the alternative table is intentionally wrong.')
    countries=collections.defaultdict(float)
    for r in read('money_transfers_country_sums'):
        countries[(r['date'],r['direction'])]=f(r['sum_country_usdm'])
    check('transfer_country_sum',max(abs(countries[k]-v) for k,v in transfer.items())<.000001,max(abs(countries[k]-v) for k,v in transfer.items()))
    fx={r['date']:r for r in read('official_fx_daily')}
    neer={r['date'] for r in read('neer_daily')}
    missing_neer=sorted(set(fx)-neer)
    check('NEER_gap_explicit',missing_neer==['2025-10-11'],missing_neer)
    old=list(csv.DictReader((ROOT/'archive/legacy/reports/nbg_policy_monthly_2020_2024.csv').open()))
    olddiff=[]
    for r in old:
        year,month=map(int,r['month'].split('-'));end=f'{year}-{month:02d}-{calendar.monthrange(year,month)[1]}'
        olddiff.append(abs(f(r['official_usd_gel_month_end'])-f(fx[end]['usd_gel'])))
    check('archived_month_end_FX_overlap',max(olddiff)<1e-9,dict(observations=len(olddiff),max_difference=max(olddiff)))
    report=dict(vintage='2026-11-09',baseline_commit='f741828d53ef843be79b0744d51e0cc24a47fc5b',
                source_count=len(sources),source_hashes_checked=len(available),raw_caches_absent=missing_raw,
                output_count=len(catalogue),checks=checks,all_checks_passed=all(r['passed'] for r in checks),
                required_checks_passed=all(r['passed'] or r['qualification'] for r in checks),
                known_source_discrepancies=json.loads((DATA/'source_discrepancies.json').read_text()),
                annual_2023_reconciliation='not reconciled; +0.55 USD million vs archived annual report',
                causal_estimation_performed=False)
    REPORT.mkdir(parents=True,exist_ok=True)
    (REPORT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def accounting():
    stocks={r['date']:f(r['reserves_usdm']) for r in read('reserve_stocks_monthly')}
    flows={r['month']:f(r['net_market_purchases_usdm']) for r in read('intervention_monthly')}
    bop={(r['date'],int(r['series_row'])):f(r['value']) for r in read('bop_bpm6')}
    rows=[]
    for y in range(2021,2026):
        change=stocks[f'{y}-12-31']-stocks[f'{y-1}-12-31'];purchases=sum(flows[f'{y}-{m:02d}'] for m in range(1,13));transactions=bop[(str(y),39)]
        rows.append(dict(year=y,reserve_stock_change_usdm=change,market_net_purchases_usdm=purchases,
                         bop_reserve_transactions_usdm=transactions,
                         other_reserve_transactions_residual_usdm=transactions-purchases,
                         valuation_and_other_volume_residual_usdm=change-transactions,
                         stock_change_less_market_purchases_usdm=change-purchases,
                         interpretation='Residuals include definitions/revisions; neither residual is an identified government FX flow or a pure valuation series',
                         source_ids='reserve_assets;fx_market;bop_bpm6'))
    put('annual_reserve_bridge',rows)
    fx={r['date']:f(r['usd_gel']) for r in read('official_fx_daily')}
    money={r['date']:r for r in read('money_aggregates_monthly')}
    debt=collections.defaultdict(dict)
    for r in read('external_debt_ED-GEO-Tb2'):debt[r['date']][int(r['series_row'])]=f(r['value'])
    iip=collections.defaultdict(dict)
    for r in read('iip'):iip[r['date']][int(r['series_row'])]=f(r['value'])
    ara={(r['year'],r['indicator']):f(r['value']) for r in read('imf_ara_published')}
    rr=[]
    for y in range(2020,2026):
        d=f'{y}-12-31';m2=f(money[d]['m2_gelm'])/fx[d];m3=f(money[d]['m3_gelm'])/fx[d]
        rr.append(dict(year=y,reserves_usdm=stocks[d],exports_goods_services_usdm=bop[(str(y),8)],
                       m2_usdm=m2,m3_usdm=m3,official_gel_per_usd=fx[d],
                       short_term_debt_original_maturity_usdm=debt[d][5]+debt[d][9],
                       short_term_debt_residual_maturity_usdm=None,
                       portfolio_liabilities_usdm=iip[d][211],other_investment_liabilities_usdm=iip[d][254],
                       independent_reserves_m2_ratio=stocks[d]/m2,independent_reserves_m3_ratio=stocks[d]/m3,
                       imf_published_reserves_money_ratio=ara[(str(y),'Reserves_M2')],
                       imf_published_ara_ratio=ara[(str(y),'Reserves_ARA')],
                       nbg_reported_ara_pct=104.8 if y==2025 else 82.6 if y==2024 else None,
                       independently_reconstructed_ara=None,
                       status='Residual maturity, other-liability adjustments and IMF/NBG denominator conventions unresolved; no full metric claimed'))
    put('ara_component_inputs',rr)


def monthly_panel():
    stocks={r['date'][:7]:r for r in read('reserve_stocks_monthly')}
    fx={r['date']:r for r in read('official_fx_daily')}
    intervention={r['month']:r for r in read('intervention_monthly')}
    neer={r['date'][:7]:f(r['index']) for r in read('neer_monthly')};reer={r['date'][:7]:f(r['index']) for r in read('reer_monthly')}
    tibr=collections.defaultdict(list)
    for r in read('tibr_daily'):
        if r['tibr_pct']:tibr[r['date'][:7]].append(f(r['tibr_pct']))
    decisions=list(csv.DictReader((ROOT/'archive/legacy/reports/nbg_policy_decisions_2008_onward.csv').open()))
    transfers={(r['date'][:7],r['direction']):f(r['value_usdm']) for r in read('money_transfers_canonical')}
    rr=[];previous=None
    for m,s in sorted(stocks.items()):
        end=s['date'];i=intervention.get(m,{})
        known=[r for r in decisions if r['effective_date']<=end]
        row=dict(month=m,official_usd_gel_end=f(fx[end]['usd_gel']),official_eur_gel_end=f(fx[end]['eur_gel']),
                 neer_month_average_index=neer.get(m),reer_month_average_index=reer.get(m),
                 reserves_end_usdm=f(s['reserves_usdm']),reserves_change_usdm=f(s['reserves_usdm'])-previous if previous is not None else None,
                 gold_end_usdm=f(s['gold_usdm']),net_market_purchases_usdm=f(i.get('net_market_purchases_usdm')),
                 auction_purchases_usdm=f(i.get('auction_purchases_usdm')),auction_sales_usdm=f(i.get('auction_sales_usdm')),
                 nonauction_net_purchases_usdm=f(i.get('nonauction_net_purchases_usdm')),
                 nonauction_gross_purchases_usdm=None,nonauction_gross_sales_usdm=None,government_fx_conversions_usdm=None,
                 identified_fx_valuation_usdm=None,policy_rate_end_pct=f(known[-1]['policy_rate_pct']) if known else None,
                 tibr_daily_simple_mean_pct=statistics.mean(tibr[m]) if tibr[m] else None,tibr_observations=len(tibr[m]),
                 transfers_in_usdm=transfers.get((m,'inflow')),transfers_out_usdm=transfers.get((m,'outflow')),
                 intervention_status='monthly net observed; gross nonauction unavailable' if i else 'not yet in acquired monthly disclosure',
                 vintage='2026-11-09')
        rr.append(row);previous=f(s['reserves_usdm'])
    put('monthly_policy_panel',rr)
    missing=[]
    episode=[r for r in rr if r['month']>='2025-01']
    for k in episode[0]:
        n=sum(r[k] is None for r in episode)
        missing.append(dict(variable=k,expected_completed_calendar_months=len(episode),observed_rows=len(episode)-n,missing_rows=n,missing_fraction=n/len(episode)))
    put('episode_monthly_missingness',missing)


def main():
    report=validate();accounting();monthly_panel()
    print(json.dumps(dict(checks=len(report['checks']),passed=report['all_checks_passed'],failed=[r for r in report['checks'] if not r['passed']]),indent=2))
    if not report['required_checks_passed']:raise SystemExit(1)


if __name__=='__main__':main()
