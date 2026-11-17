"""Independent QR fit and matrix-solve verification of R3 candidate paths. No production imports."""
from pathlib import Path
import argparse,csv,hashlib,json,math
import numpy as np
from scipy.linalg import lstsq,solve

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/r3_reopen_2026_11_16'


def read(name):return list(csv.DictReader((REPORT/name).open()))
def regress(x,v):return lstsq(x,v,lapack_driver='gelsy')[0]


def audit():
    p=read('model_panel.csv');c=json.loads((ROOT/'research/r3_reopen_calibration.json').read_text())
    primary=next(r for r in c if r['primary']);c += [dict(primary,id='zero_kernel',b_gel_per_usd=[0]*4),dict(primary,id='reversed_kernel',b_gel_per_usd=[-v for v in primary['b_gel_per_usd']])]
    observed={(r['spec'],r['month']):r for r in read('candidate_paths.csv')}
    max_price_error=max_reserve_error=0.;checked=0
    for cfg in c:
        for alternative in (False,True) if cfg['primary'] and cfg['id']==primary['id'] else (False,):
            name=cfg['id']+('_gdp38100' if alternative else '')
            b=cfg['b_gel_per_usd'];rho=cfg['rho']
            d=np.array([38100 if alternative and r['month']>='2025' else float(r['gdp_normalization_usdm']) for r in p])
            a=np.array([[100*math.log(float(r['gel_per_usd'])),float(r['policy_rate_pct']),100*float(r['net_purchases_usdm'])/d[t]] for t,r in enumerate(p)])
            z=np.array([[float(r['dollar_change_log_pct'] or 0),float(r['vix_mean'])] for r in p])
            def xi(h,t):return np.array([1,h[-1][1],h[-1][0]-h[-2][0],h[-1][2],*z[t]])
            def zy(h,t,rate):return np.array([1,rate,h[-1][1],*z[t]])
            ix=range(3,60);X=np.array([xi(a[:t],t) for t in ix]);Z=np.array([zy(a[:t],t,a[t,1]) for t in ix])
            Xq=np.column_stack([X,a[3:60,1]]);change=a[3:60,0]-a[2:59,0]
            target=np.array([a[t,0]-rho*a[t-1,0]-sum(b[j]*a[t-j,2] for j in range(4)) for t in ix])
            ai=regress(X,a[3:60,1]);ay=regress(Z,target);u=target-Z@ay
            residual=lambda v:v-Xq@regress(Xq,v)
            theta=float(residual(u)@residual(a[3:60,2])/(residual(u)@residual(change)))
            aq=regress(Xq,a[3:60,2]-theta*change)
            h=list(a[:60].copy());dr=0.
            for t in range(60,81):
                ui=a[t,1]-xi(a[:t],t)@ai
                uy=a[t,0]-rho*a[t-1,0]-sum(b[j]*a[t-j,2] for j in range(4))-zy(a[:t],t,a[t,1])@ay
                uq=a[t,2]-np.append(xi(a[:t],t),a[t,1])@aq-theta*(a[t,0]-a[t-1,0])
                rate=xi(h,t)@ai+ui
                supply=rho*h[-1][0]+sum(b[j]*h[-j][2] for j in range(1,4))+zy(h,t,rate)@ay+uy
                demand=np.append(xi(h,t),rate)@aq+uq
                price,q=solve(np.array([[1.,-b[0]],[-theta,1.]]),np.array([supply,demand-theta*h[-1][0]]))
                if q>0:price=supply;q=0
                e=math.exp(price/100);dr=dr*(1+float(p[t]['sofr_mean_pct'])/1200)+q*d[t]/100-float(p[t]['net_purchases_usdm'])
                published=observed[name,p[t]['month']]
                pe=abs(e-float(published['candidate_gel_per_usd']));re=abs(float(p[t]['reserves_usdm'])+dr-float(published['conditional_reserves_usdm']))
                max_price_error=max(max_price_error,pe);max_reserve_error=max(max_reserve_error,re)
                assert pe<1e-6 and re<.001,(name,p[t]['month'],pe,re)
                assert q<=0 and published['release_status']=='NOT_AN_ACCEPTED_COUNTERFACTUAL'
                h.append(np.array([price,rate,q]));checked+=1
    boot=read('bootstrap.csv');info=json.loads((REPORT/'validation.json').read_text())
    admissible=sum(r['admissible']=='True' for r in boot)
    assert admissible==info['admissible_bootstrap_draws']==149
    assert not info['preferred_path_released'] and admissible/len(boot)<.9
    return dict(independent_paths_checked=checked,fit_method='SciPy pivoted QR; no production imports',clearing_method='independent 2x2 simultaneous matrix solve',
        maximum_quote_difference=max_price_error,maximum_reserve_difference_usdm=max_reserve_error,
        source_of_small_differences='audit starts from CSV-rounded external regressors',release_rejection_confirmed=True,
        inputs={n:hashlib.sha256((REPORT/n).read_bytes()).hexdigest() for n in ['model_panel.csv','candidate_paths.csv','bootstrap.csv','validation.json']})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=audit();body=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.report:args.report.write_text(body)
    print(body)
