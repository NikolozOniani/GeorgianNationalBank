"""Fit and evaluate the registered standalone Georgian policy-rate equation."""
import argparse
import csv
import io
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/r3_rate_rule'
DECISIONS = ROOT/'archive/legacy/reports/nbg_policy_decisions_2008_onward.csv'
VINTAGES = ROOT/'data/derived/r3_rate_rule/vintages.csv'
TERMS = ['intercept','prior_rate','actual_inflation_gap','expected_inflation_gap','expected_growth']


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def month_number(date):
    return 12*int(date[:4])+int(date[5:7])


def meetings():
    releases = read(VINTAGES)
    records = read(DECISIONS)
    dates = [r['decision_date'] for r in records]
    assert dates == sorted(set(dates))
    rows = []
    excluded = []
    for previous, prior, decision in zip(records,records[1:],records[2:]):
        date = decision['decision_date']
        if not '2018' <= date[:4] <= '2024':
            continue
        eligible = [r for r in releases if 1 <= month_number(date)-month_number(r['report_month']) <= 4]
        if not eligible:
            excluded.append(date)
            continue
        release = max(eligible,key=lambda r:r['report_month'])
        prior_rate = float(prior['policy_rate_pct'])
        rows.append(dict(decision_date=date, effective_date=decision['effective_date'],
                         prior_rate=prior_rate,rate=float(decision['policy_rate_pct']),
                         change=float(decision['policy_rate_pct'])-prior_rate,
                         previous_change=prior_rate-float(previous['policy_rate_pct']),
                         report_month=release['report_month'],
                         actual_inflation_gap=float(release['actual_cpi_pct'])-3,
                         expected_inflation_gap=float(release['expected_cpi_pct'])-3,
                         expected_growth=float(release['expected_growth_pct'])))
    return rows, excluded


def design(rows,terms):
    return np.array([[1. if key=='intercept' else r[key] for key in terms] for r in rows])


def fit(rows,terms):
    x = design(rows,terms)
    coef,_,rank,_ = np.linalg.lstsq(x,[r['change'] for r in rows],rcond=None)
    if rank!=len(terms):
        raise ValueError('Insufficient independent regressors')
    return coef


def model_outputs():
    rows, excluded = meetings()
    nested = [term for term in TERMS if term!='expected_inflation_gap']
    initial = [r for r in rows if r['decision_date']<'2023']
    fixed = fit(initial,TERMS)
    forecast = []
    for i,row in enumerate(rows):
        if row['decision_date']<'2023':
            continue
        def predict(terms,coef):
            return float((design([row],terms)@coef).item())
        forecast.append(dict(date=row['decision_date'],n_train=i,actual=row['change'],
                             primary=predict(TERMS,fit(rows[:i],TERMS)),
                             frozen=predict(TERMS,fixed),
                             no_forecast=predict(nested,fit(rows[:i],nested)),
                             hold=0.,last_change=row['previous_change']))
    scores = []
    for period in ['pooled','2023','2024']:
        subset = [r for r in forecast if period=='pooled' or r['date'].startswith(period)]
        actual = np.array([r['actual'] for r in subset])
        for model in ['primary','frozen','no_forecast','hold','last_change']:
            pred = np.array([r[model] for r in subset])
            error = pred-actual
            # Exact sign treats tiny nonzero forecasts as changes; report this convention.
            scores.append(dict(period=period,model=model,n=len(actual),
                               rmse=float(np.sqrt(np.mean(error**2))),mae=float(np.mean(abs(error))),
                               sign_correct=int(np.sum(np.sign(actual)==np.sign(pred)))))
    fits = []
    for sample in ['through_2022','through_2024']:
        source = initial if sample=='through_2022' else rows
        for omit in ['none']+sorted({r['decision_date'][:4] for r in source}):
            kept = [r for r in source if r['decision_date'][:4]!=omit]
            coef = fit(kept,TERMS)
            smooth = 1+coef[1]
            fits.append(dict(sample=sample,omitted_year=omit,n=len(kept),**dict(zip(TERMS,coef)),
                             own_rate=smooth,stable=bool(abs(smooth)<1)))
    primary,hold = (next(r['rmse'] for r in scores if r['model']==m and r['period']=='pooled')
                    for m in ['primary','hold'])
    gates = dict(beats_hold=primary<hold,stable_fits=all(r['stable'] for r in fits),
                 positive_forecast_loading=all(r['expected_inflation_gap']>0 for r in fits))
    decision = dict(design_commit='52a0532764d8f9f1ead49d28a646b1a8b18da504',
                    reports=len(read(VINTAGES)),decisions=len(rows),training=len(initial),
                    holdout=len(forecast),excluded_no_prior_vintage=excluded,
                    criteria=gates,standalone_candidate_accepted=all(gates.values()))
    return {'meetings.csv':rows,'predictions.csv':forecast,'scores.csv':scores,'coefficients.csv':fits},decision


def export(check):
    tables,decision = model_outputs()
    output = {'validation.json':json.dumps(decision,indent=2)+'\n'}
    for name,rows in tables.items():
        buf = io.StringIO()
        writer = csv.DictWriter(buf,fieldnames=rows[0],lineterminator='\n')
        writer.writeheader()
        writer.writerows([{k:round(v,9) if isinstance(v,float) else v for k,v in r.items()} for r in rows])
        output[name] = buf.getvalue()
    for name,data in output.items():
        if check:
            if (OUT/name).read_text()!=data:
                raise ValueError('Result differs: '+name)
        else:
            (OUT/name).write_text(data)
    print(json.dumps(decision,indent=2))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    export(parser.parse_args().check)
