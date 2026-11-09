"""Descriptive credit results and explicit synthetic-contract exposure calculations.

No coefficient in this script estimates a causal policy effect. Core analysis is
offline and requires only Python's standard library and the committed CSV inputs.
"""
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/peer_review'


def rows(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def write(name,data):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)


def payment(principal,annual_percent,months):
    if principal<0 or annual_percent<0 or months<=0:raise ValueError('Invalid annuity inputs')
    r=annual_percent/1200
    return principal/months if r==0 else principal*r/(-math.expm1(-months*math.log1p(r)))


def policy_on(date,decisions):
    available=[r for r in decisions if r['effective_date']<=date.isoformat()]
    if not available:raise ValueError('No effective rate before reset date')
    return float(max(available,key=lambda r:r['effective_date'])['policy_rate_pct'])


def simulate(principal,term,reset,phase=0,pass_through=1,reference=8,margin=3):
    """Monthly annuity recast; reset uses the rate effective at start of month.

    No fees, prepayments, defaults, caps, floors or margin changes. Unchanged
    reference-rate contract is an accounting comparator, not feasible macro policy.
    """
    decisions=rows(ROOT/'reports/nbg_policy_decisions_2008_onward.csv')
    balance=baseline_balance=principal
    baseline_rate=reference+margin
    result=[];current_rate=None
    for t in range(48):
        date=dt.date(2021+t//12,t%12+1,1)
        p=policy_on(date,decisions)
        if t==0 or t%reset==phase:current_rate=margin+reference+pass_through*(p-reference)
        remaining=term-t
        pay=payment(balance,current_rate,remaining)
        basepay=payment(baseline_balance,baseline_rate,remaining)
        interest=balance*current_rate/1200
        baseinterest=baseline_balance*baseline_rate/1200
        closing=balance+interest-pay
        baseclosing=baseline_balance+baseinterest-basepay
        result.append(dict(month=date.strftime('%Y-%m'),policy_at_month_start_pct=p,contract_rate_pct=current_rate,
                           opening_balance_gel=balance,payment_gel=pay,interest_gel=interest,closing_balance_gel=closing,
                           reference_payment_gel=basepay,reference_interest_gel=baseinterest,reference_closing_balance_gel=baseclosing,
                           extra_payment_gel=pay-basepay,extra_interest_gel=interest-baseinterest))
        balance=closing;baseline_balance=baseclosing
    return result


def main():
    lock=json.loads((OUT/'analysis_inputs.lock.json').read_text())
    for name,sha in lock.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:raise ValueError('Changed input '+name)
    data=rows(OUT/'credit_monthly_2020_2024.csv');by={r['month']:r for r in data}
    keys=['hh_resident_gel_stock','hh_resident_fx_stock','hh_resident_gel_rate','hh_resident_fx_rate',
          'hh_all_gel_new_housing_rate','hh_all_gel_new_consumer_rate','hh_all_gel_realestate_secured_outstanding_rate',
          'hh_all_gel_deposit_term_rate','hh_all_gel_new_term_deposit_rate']
    summary=[]
    for k in keys:
        a,b,c=[float(by[m][k]) for m in ('2020-12','2022-12','2024-12')]
        summary.append(dict(series=k,dec2020=a,dec2022=b,dec2024=c,change_2020_2022=b-a,change_2022_2024=c-b,
                            unit='GEL million' if k.endswith('stock') else 'percent per year; changes percentage points',
                            interpretation='Changing aggregate portfolios; not within-borrower repricing or causal transmission'))
    write('table1_observed.csv',summary)
    standardized=[]
    for amount in (50000,100000,200000):
        for term in (120,240):
            for m in ('2020-12','2022-12','2024-12'):
                rate=float(by[m]['hh_all_gel_new_housing_rate']);p=payment(amount,rate,term)
                baseline=payment(amount,float(by['2020-12']['hh_all_gel_new_housing_rate']),term)
                standardized.append(dict(month=m,principal_gel=amount,term_months=term,source_rate_pct=rate,
                                         monthly_payment_gel=p,change_vs_dec2020_gel=p-baseline,
                                         source_series='hh_all_gel_new_housing_rate',
                                         assumption='Synthetic new annuity, fixed size/maturity, nominal rate/12, no fees; not actual borrower payments'))
    write('table2_standardized_new_loan.csv',standardized)
    paths=simulate(100000,240,1);write('indexed_contract_monthly.csv',paths)
    scenarios=[]
    for term in (120,240):
        for reset in (1,3,6,12):
            for phase in range(reset):
                for pt in (0,.5,1):
                    p=simulate(100000,term,reset,phase,pt)
                    extra=sum(r['extra_payment_gel'] for r in p);interest=sum(r['extra_interest_gel'] for r in p)
                    debt=p[-1]['closing_balance_gel']-p[-1]['reference_closing_balance_gel']
                    if abs(extra-(interest-debt))>1e-7:raise ValueError('Payment/interest/debt identity failed')
                    scenarios.append(dict(principal_gel=100000,term_months=term,reset_months=reset,reset_phase=phase,
                                          pass_through=pt,reference_policy_pct=8,margin_pp=3,extra_payments_48m_gel=extra,
                                          extra_interest_48m_gel=interest,extra_terminal_debt_gel=debt,
                                          peak_extra_monthly_payment_gel=max(r['extra_payment_gel'] for r in p),
                                          interpretation='Conditional synthetic contract; not observed or NBG net welfare effect'))
    write('table3_reset_sensitivity.csv',scenarios)
    # Alternative benchmark exposes dependence on the arbitrary held-rate comparison.
    ref=simulate(100000,240,1,reference=9)
    write('alternative_reference_9pct.csv',ref)
    incidence=[]
    peak=max(r['extra_payment_gel'] for r in paths)
    for income in (3000,6000,9000):
        incidence.append(dict(assumed_monthly_income_gel=income,peak_extra_payment_gel=peak,
                              extra_payment_income_pp=100*peak/income,
                              interpretation='Stylized equal-debt income scenarios; not survey groups, quintiles, or approval eligibility'))
    write('table4_conditional_income_exposure.csv',incidence)
    headline=dict(new_housing_rate_dec2020=float(by['2020-12']['hh_all_gel_new_housing_rate']),
                  new_housing_rate_dec2022=float(by['2022-12']['hh_all_gel_new_housing_rate']),
                  new_housing_rate_dec2024=float(by['2024-12']['hh_all_gel_new_housing_rate']),
                  standardized_100k_20y=[r for r in standardized if r['principal_gel']==100000 and r['term_months']==240],
                  indexed_monthly_main=next(r for r in scenarios if r['term_months']==240 and r['reset_months']==1 and r['pass_through']==1),
                  alternative_reference_extra_payments=sum(r['extra_payment_gel'] for r in ref),
                  main_initial_payment=paths[0]['payment_gel'],main_peak_payment=max(r['payment_gel'] for r in paths),
                  main_peak_month=max(paths,key=lambda r:r['payment_gel'])['month'],
                  main_end_payment=paths[-1]['payment_gel'],conditional_income_exposure=incidence)
    (OUT/'results.json').write_text(json.dumps(headline,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(headline,indent=2))


if __name__=='__main__':main()
