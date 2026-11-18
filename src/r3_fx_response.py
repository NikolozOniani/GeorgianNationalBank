"""Historical purchase/price associations and selection diagnostics under the R3 design."""
import argparse
import calendar
import csv
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from r3_fx_inputs import DATA, ROOT, csv_bytes

OUT = ROOT/'reports/r3_fx_response'
PRIOR = ROOT/'reports/r3_reopen_2026_11_16/model_panel.csv'
HORIZONS = (0,1,3,6,12,18)
DAY = timedelta(days=1)


def read(file):
    with file.open() as stream:
        return list(csv.DictReader(stream))


def residualize(x, controls):
    coef,_,rank,_ = np.linalg.lstsq(controls,x,rcond=None)
    if rank < controls.shape[1]:
        raise ValueError('Rank-deficient control matrix')
    return x-controls@coef


def events(prices, auctions):
    auction_dates = {date.fromisoformat(r['date']) for r in auctions}

    def change(d,a,b):
        return 100*math.log(prices[d+b*DAY]/prices[d+a*DAY])

    def count_after(d,h):
        return sum(d<other<=d+h*DAY for other in auction_dates)

    pairs = []
    for r in auctions:
        qty = float(r['purchases_usd'])
        if qty<=0:
            continue
        d = date.fromisoformat(r['date'])
        for h in (1,7,28,84):
            if d+h*DAY not in prices:
                continue
            event7,event28 = change(d,-7,0),change(d,-28,0)
            candidates = []
            for gap in range(14,92,7):
                c = d-gap*DAY
                if c.year!=d.year or c in auction_dates or c+h*DAY>=d:
                    continue
                distance = math.hypot(event7-change(c,-7,0),event28-change(c,-28,0))
                candidates.append((distance,gap,c))
            row = dict(date=d.isoformat(),purchase_usdm=qty/1e6,h_days=h,
                       pre7=event7,pre28=event28,pre28to7=change(d,-28,-7),
                       observed_return=change(d,0,h),other_auctions=count_after(d,h),
                       control=None,distance_pp=None,control_pre7=None,control_pre28=None,
                       control_pre28to7=None,control_return=None,control_other_auctions=None,
                       difference_pp=None)
            if candidates:
                distance,_,c = min(candidates)
                row.update(control=c.isoformat(),distance_pp=distance,control_pre7=change(c,-7,0),
                           control_pre28=change(c,-28,0),control_pre28to7=change(c,-28,-7),
                           control_return=change(c,0,h),control_other_auctions=count_after(c,h),
                           difference_pp=row['observed_return']-change(c,0,h))
            pairs.append(row)

    summaries = []
    for h in (1,7,28,84):
        for era in ('all','pre_2020','2020_onward'):
            base = [r for r in pairs if r['h_days']==h and (era=='all' or
                    (r['date']<'2020')==(era=='pre_2020'))]
            matches = [r for r in base if r['control']]
            for sample in ('all_pairs','no_other_auction'):
                selected = [r for r in matches if sample=='all_pairs' or
                            r['other_auctions']==r['control_other_auctions']==0]
                def mean(key):
                    return float(np.mean([r[key] for r in selected])) if selected else None
                summaries.append(dict(h_days=h,era=era,sample=sample,purchases=len(base),
                     matched=len(matches),used=len(selected),unique_controls=len({r['control'] for r in selected}),
                     avg_pre7=mean('pre7'),avg_control_pre7=mean('control_pre7'),
                     avg_pre28=mean('pre28'),avg_control_pre28=mean('control_pre28'),
                     placebo_28_to_7_difference=mean('pre28to7')-mean('control_pre28to7') if selected else None,
                     avg_observed=mean('observed_return'),avg_control=mean('control_return'),
                     avg_difference=mean('difference_pp'),median_difference=float(np.median(
                         [r['difference_pp'] for r in selected])) if selected else None,
                     avg_matching_distance=mean('distance_pp')))
    return pairs,summaries


def linear_fit(x,y,bandwidth):
    n,k = x.shape
    beta,_,rank,_ = np.linalg.lstsq(x,y,rcond=None)
    if rank!=k or n-k<10:
        raise ValueError('Insufficient regression support')
    u = y-x@beta
    scores = x*u[:,None]
    meat = scores.T@scores
    for lag in range(1,bandwidth+1):
        product = scores[lag:].T@scores[:-lag]
        meat += (1-lag/(bandwidth+1))*(product+product.T)
    bread = np.linalg.inv(x.T@x)
    cov = n/(n-k)*bread@meat@bread
    # Equal-strength partial R²: x_res is treatment residualized on all other
    # regressors. The required bias satisfies R²/sqrt(1-R²)=|b|*||x_res||/||u||.
    independent = residualize(x[:,1],np.delete(x,1,axis=1))
    ratio = abs(beta[1])*np.linalg.norm(independent)/np.linalg.norm(u)
    rv = 2*ratio/(math.sqrt(4+ratio**2)+ratio)
    return beta,np.sqrt(np.diag(cov)),rv


def monthly_inputs(prices,auctions):
    old = {r['month']:r for r in read(PRIOR)}
    months = read(DATA/'monthly.csv')
    rows,discrepancies = [],[]
    for m in months:
        key = m['month']
        year,month = map(int,key.split('-'))
        end = date(year,month,calendar.monthrange(year,month)[1])
        month_auctions = [r for r in auctions if r['date'][:7]==key]
        diffs = {}
        for usd,usdm in [('purchases_usd','auction_buy_usdm'),('sales_usd','auction_sell_usdm')]:
            total = sum(float(r[usd])/1e6 for r in month_auctions)
            diffs[usd] = total-float(m[usdm])
            if abs(diffs[usd])>1e-6:
                discrepancies.append(dict(month=key,leg=usd,dated_usdm=total,
                         workbook_usdm=float(m[usdm]),dated_less_workbook_usdm=diffs[usd]))
        net = float(m['net_usdm'])
        if key in old:
            if not (abs(float(old[key]['net_purchases_usdm']) - net) < 1e-6
                    and abs(float(old[key]['gel_per_usd']) - prices[end]) < 1e-8):
                raise ValueError(f'Market ledger or quote disagrees with R3 panel in {key}')
        rows.append(dict(month=key,logpct=100*math.log(prices[end]),net100=net/100,
                 dated_net100=(net+diffs['purchases_usd']-diffs['sales_usd'])/100,
                 dollar=old.get(key,{}).get('dollar_change_log_pct'),vix=old.get(key,{}).get('vix_mean')))
    numbers = [12*int(r['month'][:4])+int(r['month'][5:]) for r in rows]
    if not np.all(np.diff(numbers) == 1):
        raise ValueError('Monthly market history has duplicate, missing or unordered months')
    return rows,discrepancies


def projections(rows):
    result = []
    for spec in ('full','2020_onward','2020_global','full_dated_sensitivity'):
        netkey = 'dated_net100' if spec=='full_dated_sensitivity' else 'net100'
        for h in (-1,*HORIZONS):
            x,y,months = [],[],[]
            for t in range(2,len(rows)-max(h,0)):
                r = rows[t]
                if spec.startswith('2020') and r['month']<'2020':
                    continue
                if spec=='2020_global' and not r['dollar']:
                    continue
                qty = r[netkey]
                lag_return = rows[t-1]['logpct']-rows[t-2]['logpct']
                reg = [1,max(qty,0),max(-qty,0),rows[t-1][netkey]]
                if h>=0:
                    reg.append(lag_return)
                if spec=='2020_global':
                    reg.extend((float(r['dollar']),float(r['vix'])))
                x.append(reg)
                y.append(lag_return if h<0 else rows[t+h]['logpct']-rows[t-1]['logpct'])
                months.append(r['month'])
            beta,se,rv = linear_fit(np.array(x),np.array(y),max(1,h+1))
            result.append(dict(spec=spec,h_months=h,n=len(y),purchase_months=sum(z[1]>0 for z in x),
                               sale_months=sum(z[2]>0 for z in x),first_origin=months[0],last_origin=months[-1],
                               buy_logpct_per_100m=beta[1],buy_hac_se=se[1],sale_logpct_per_100m=beta[2],
                               sale_hac_se=se[2],equal_partial_r2_to_zero=rv))
    return result


def kernels():
    panel = [r for r in read(PRIOR) if r['month']<'2025']
    primary = next(c for c in json.loads((ROOT/'research/r3_reopen_calibration.json').read_text()) if c['primary'])
    b = np.array(primary['b_gel_per_usd'])
    configs = [('published',primary['rho'],b),('reversed',primary['rho'],-b),
               ('zero',primary['rho'],b*0),('short_lived',.5,np.array([b[0],0,0,0]))]
    out, sensitivity = [], []
    for name,rho,coef in configs:
        u,q,x = [],[],[]
        for t in range(3,len(panel)):
            now,prior = panel[t],panel[t-1]
            flow = [float(panel[t-j]['q_pct_gdp']) for j in range(4)]
            u.append(float(now['y'])-rho*float(prior['y'])-np.dot(coef,flow))
            q.append(flow[0])
            x.append([1,float(now['policy_rate_pct']),float(prior['policy_rate_pct']),
                      float(now['dollar_change_log_pct']),float(now['vix_mean']),flow[1]])
        qq = residualize(np.array(q),np.array(x))
        uu = residualize(np.array(u),np.array(x))
        out.append(dict(spec=name,rho=rho,impact_logpct_per_1pct_gdp=coef[0],n=len(q),
                        partial_correlation=float(np.corrcoef(qq,uu)[0,1]),
                        residual_fx_sd=float(uu.std(ddof=1)),residual_q_sd=float(qq.std(ddof=1))))
        if name=='published':
            # Invert corr(Q, Y* - bQ) exactly, conditional on fixed other lags.
            target = uu+coef[0]*qq
            slope = (qq@target)/(qq@qq)
            scale = np.linalg.norm(target-slope*qq)/np.linalg.norm(qq)
            for correlation in (-.50,-.25,0.,.25):
                current = slope-correlation*scale/math.sqrt(1-correlation**2)
                sensitivity.append(dict(assumed_partial_correlation=correlation,
                       implied_impact_logpct_per_1pct_gdp=current,
                       check_correlation=np.corrcoef(qq,target-current*qq)[0,1]))
    return out,sensitivity


def run(check):
    auctions = read(DATA/'auctions.csv')
    quotes = read(DATA/'daily.csv')
    prices = {date.fromisoformat(r['date']):float(r['gel_usd']) for r in quotes}
    if len(prices) != len(quotes) or len(prices) != (max(prices) - min(prices)).days + 1:
        raise ValueError('Daily quotes contain duplicate or missing dates')
    pairs,summary = events(prices,auctions)
    rows,discrepancies = monthly_inputs(prices,auctions)
    buy = [float(r['purchases_usd'])/1e6 for r in auctions if float(r['purchases_usd'])>0]
    historical = [r['net100']*100 for r in rows if r['net100']>0]
    episode = [float(r['net_purchases_usdm']) for r in read(PRIOR) if r['month']>='2025']
    kernel, sensitivity = kernels()
    out = dict(auction_pairs=pairs,auction_comparison=summary,monthly_projections=projections(rows),
               kernel_diagnostics=kernel,selection_sensitivity=sensitivity,auction_reconciliation=discrepancies)
    files = {k+'.csv':csv_bytes(v) for k,v in out.items()}
    info = dict(design='c9bf0850390ca0a02e8afa7526a43581aad36b8e',auctions=len(auctions),
                purchase_auctions=len(buy),sale_auctions=sum(float(r['sales_usd'])>0 for r in auctions),
                purchase_size_median_usdm=np.median(buy),purchase_size_max_usdm=max(buy),
                preperiod_months=len(rows),historical_max_net_usdm=max(historical),
                episode_months=len(episode),episode_pos=sum(v>0 for v in episode),
                episode_max_net_usdm=max(episode),episode_months_above_history=sum(v>max(historical) for v in episode),
                episode_gross_available=False,identified_impact=False,identified_half_life=False,
                input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [*sorted(DATA.glob('*.csv')),PRIOR,ROOT/'research/r3_reopen_calibration.json']})
    files['validation.json']=(json.dumps(info,indent=2)+'\n').encode()
    for name,body in files.items():
        if check:
            if (OUT/name).read_bytes() != body:
                raise ValueError(f'Response output differs: {name}')
        else:
            (OUT/name).write_bytes(body)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    run(parser.parse_args().check)
