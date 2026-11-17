"""Registered R3 conditional-model experiment. No identification claim from good fit."""
from pathlib import Path
import argparse,csv,hashlib,io,json,math,re,subprocess,urllib.request
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/r3_reopen_2026_11_16'
OLD='data/derived/episode_2026_11_09/'
INPUTS={}
DESIGN='3546bce794d093ef6458fa8813d570b14a68e42c'


def read(name):
    p=ROOT/name;b=p.read_bytes();INPUTS[name]=hashlib.sha256(b).hexdigest()
    return json.loads(b) if p.suffix=='.json' else list(csv.DictReader(io.StringIO(b.decode())))


def csv_text(rows):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=rows[0],lineterminator='\n');w.writeheader()
    for row in rows:
        w.writerow({k:round(float(v),9) if isinstance(v,(float,np.floating)) and math.isfinite(v) else v for k,v in row.items()})
    return s.getvalue()


def verify_sources(acquire=False):
    items=read('data/r3_reopen_source_manifest.json')
    for item in items:
        if item['status']!='acquired':continue
        p=ROOT/item['local_path']
        if not p.exists() and acquire:
            with urllib.request.urlopen(item['url'],timeout=45) as response:b=response.read(15_000_001)
            if len(b)>15_000_000 or hashlib.sha256(b).hexdigest()!=item['sha256']:raise ValueError('Changed source vintage')
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Missing/changed source '+str(p))
    raw=read('data/raw/r3_reopen_2026_11_16/gdp_wb.json')
    supplied={r['date']:r['value'] for r in raw[1]}
    for r in read('data/derived/r3_reopen_2026_11_16/gdp_observations.csv'):
        if float(r['gdp_current_usd'])!=supplied[r['year']]:raise ValueError('GDP extraction mismatch')
    pdf=ROOT/next(r['local_path'] for r in items if r['id']=='adler2015_alternate')
    text=subprocess.check_output(['pdftotext','-layout','-f','41','-l','41',str(pdf),'-'],text=True)
    labels=['FXI/GDP ','FXI/GDP (lagged)','FXI/GDP (2nd lag)','FXI/GDP (3rd lag)','Dependent variable (lagged)']
    values=[]
    for label in labels:
        line=next(l for l in text.splitlines() if l.strip().startswith(label))
        vals=[float(x) for x in re.findall(r'-?\d+\.\d+',line)]
        if len(vals)!=12:raise ValueError('Table columns shifted '+label)
        values.append(vals)
    for row in read('research/r3_reopen_calibration.json'):
        col=row['column']-1
        if row['source_b_appreciation']!=[v[col] for v in values[:4]] or row['b_gel_per_usd']!=[-v[col] for v in values[:4]] or row['rho']!=values[4][col]:raise ValueError('Source/input calibration mismatch')


def panel():
    monthly=read('reports/acquisition_2026_11_09/monthly_policy_panel.csv')
    def aggregate(name,key):
        grouped={}
        for r in read(OLD+name+'.csv'):
            if r[key]!='':grouped.setdefault(r['date'][:7],[]).append(float(r[key]))
        return {m:(sum(v)/len(v),len(v)) for m,v in grouped.items()}
    dollar=aggregate('broad_dollar_daily','index');vix=aggregate('vix_daily','close');sofr=aggregate('sofr_daily','rate_pct')
    raw=read('data/derived/r3_reopen_2026_11_16/gdp_observations.csv')
    gdp={int(r['year']):float(r['gdp_current_usd'])/1e6 for r in raw}
    if set(gdp)!=set(range(2020,2025)) or min(gdp.values())<=0:raise ValueError('GDP coverage')
    liquidity={r['date'][:7]:r for r in read('reports/r2_2026_11_11/liquidity_schedule.csv') if r['horizon_months']=='1'}
    rows=[]
    for r in monthly:
        m=r['month']
        if not '2020-01'<=m<='2026-09':continue
        rows.append(dict(month=m,gel_per_usd=float(r['official_usd_gel_end']),y=100*math.log(float(r['official_usd_gel_end'])),
            policy_rate_pct=float(r['policy_rate_end_pct']),net_purchases_usdm=float(r['net_market_purchases_usdm']),
            gdp_normalization_usdm=gdp[min(int(m[:4]),2024)],gdp_status='observed annual historical' if m<'2025' else 'frozen 2024 scale; not current GDP',
            dollar_mean=dollar[m][0],dollar_n=dollar[m][1],vix_mean=vix[m][0],vix_n=vix[m][1],sofr_mean_pct=sofr[m][0],
            reserves_usdm=float(r['reserves_end_usdm']),gold_usdm=float(r['gold_end_usdm']),
            sdr_usdm=float(liquidity[m]['sdr_usdm']) if m in liquidity else None))
    if [r['month'] for r in rows]!=[f'{y}-{m:02d}' for y,last in [(2020,12),(2021,12),(2022,12),(2023,12),(2024,12),(2025,12),(2026,9)] for m in range(1,last+1)]:raise ValueError('Month continuity')
    for t,r in enumerate(rows):
        r['dollar_change_log_pct']=None if t==0 else 100*math.log(r['dollar_mean']/rows[t-1]['dollar_mean'])
        r['q_pct_gdp']=100*r['net_purchases_usdm']/r['gdp_normalization_usdm']
    return rows


def arrays(rows,scale2025=False):
    y=np.array([[r['y'],r['policy_rate_pct'],100*r['net_purchases_usdm']/(38100 if scale2025 and r['month']>='2025' else r['gdp_normalization_usdm'])] for r in rows])
    z=np.array([[r['dollar_change_log_pct'] or 0,r['vix_mean']] for r in rows])
    return y,z


def xi(history,z):
    return np.array([1,history[-1,1],history[-1,0]-history[-2,0],history[-1,2],z[0],z[1]])


def zy(history,z,interest):return np.array([1,interest,history[-1,1],z[0],z[1]])


def ols(x,y):
    coef,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    if rank<x.shape[1] or not np.isfinite(coef).all():raise ValueError('Rank/finite failure')
    return coef


def fit(y,z,idx,cfg):
    b=np.array(cfg['b_gel_per_usd']);rho=cfg['rho']
    X=np.array([xi(y[:t],z[t]) for t in idx]);Z=np.array([zy(y[:t],z[t],y[t,1]) for t in idx])
    Q=np.column_stack((X,y[idx,1]));dy=y[idx,0]-y[np.array(idx)-1,0]
    target=np.array([y[t,0]-rho*y[t-1,0]-sum(b[j]*y[t-j,2] for j in range(4)) for t in idx])
    ai=ols(X,y[idx,1]);ay=ols(Z,target);u=target-Z@ay
    def resid(v):return v-Q@ols(Q,v)
    ur=resid(u);yr=resid(dy);qr=resid(y[idx,2]);den=ur@yr
    if abs(den)<1e-10:raise ValueError('Weak/singular structural moment')
    theta=(ur@qr)/den;aq=ols(Q,y[idx,2]-theta*dy)
    det=1-b[0]*theta
    if det<=1e-8:raise ValueError('Misoriented clearing determinant')
    return dict(ai=ai,ay=ay,aq=aq,theta=theta,b=b,rho=rho,det=det,n=len(idx))


def shocks(model,y,z,t):
    h=y[:t];b=model['b']
    return np.array([y[t,1]-xi(h,z[t])@model['ai'],
        y[t,0]-model['rho']*y[t-1,0]-sum(b[j]*y[t-j,2] for j in range(4))-zy(h,z[t],y[t,1])@model['ay'],
        y[t,2]-np.append(xi(h,z[t]),y[t,1])@model['aq']-model['theta']*(y[t,0]-y[t-1,0])])


def step(model,history,z,u,constrain=False):
    b=model['b'];theta=model['theta'];interest=xi(history,z)@model['ai']+u[0]
    supply=model['rho']*history[-1,0]+sum(b[j]*history[-j,2] for j in range(1,4))+zy(history,z,interest)@model['ay']+u[1]
    demand=np.append(xi(history,z),interest)@model['aq']+u[2]
    price=(supply+b[0]*(demand-theta*history[-1,0]))/model['det']
    q=demand+theta*(price-history[-1,0])
    if constrain and q>0:price=supply;q=0.
    result=np.array([price,interest,q])
    if not np.isfinite(result).all():raise ValueError('Nonfinite simulated state')
    return result


def root(model):
    def advance(v):
        h=v.reshape(3,3);new=step(model,h,np.zeros(2),np.zeros(3))
        return np.vstack((h[1:],new)).ravel()
    origin=np.zeros(9);a=advance(origin)
    matrix=np.column_stack([advance(np.eye(9)[j])-a for j in range(9)])
    return float(max(abs(np.linalg.eigvals(matrix))))


def simulate(model,rows,y,z,start=60,constrain=True,scale2025=False):
    history=y[:start].copy();delta_reserve=0.;out=[];cash=0.;max_baseline=0.
    for t in range(start,len(y)):
        u=shocks(model,y,z,t)
        baseline=step(model,y[:t],z[t],u)
        max_baseline=max(max_baseline,float(np.max(abs(baseline-y[t]))))
        state=step(model,history,z[t],u,constrain)
        if abs(state[0]/100)>700:raise ValueError('Explosive FX')
        e=math.exp(state[0]/100);gap=100*math.expm1((y[t,0]-state[0])/100)
        denom=38100 if scale2025 else rows[t]['gdp_normalization_usdm']
        q_usd=state[2]*denom/100
        delta_reserve=delta_reserve*(1+rows[t]['sofr_mean_pct']/1200)+q_usd-rows[t]['net_purchases_usdm']
        reserve=rows[t]['reserves_usdm']+delta_reserve
        cash+=q_usd*e-rows[t]['net_purchases_usdm']*rows[t]['gel_per_usd']
        out.append(dict(month=rows[t]['month'],observed_gel_per_usd=rows[t]['gel_per_usd'],candidate_gel_per_usd=e,
            actual_over_candidate_gap_pct=gap,quote_decline_pct=100*(1-e/rows[t]['gel_per_usd']),
            candidate_policy_rate_pct=state[1],candidate_net_intervention_usdm=q_usd,
            conditional_reserves_usdm=reserve,conditional_non_gold_non_sdr_usdm=reserve-rows[t]['gold_usdm']-rows[t]['sdr_usdm'],
            accumulated_fx_cash_difference_gelm=cash))
        history=np.vstack((history,state))
    return out,max_baseline


def validate(rows,y,z,cfg):
    results=[]
    for t in range(36,60):
        try:
            model=fit(y,z,list(range(3,t)),cfg);prediction=step(model,y[:t],z[t],np.zeros(3))
            results.append(dict(month=rows[t]['month'],predicted_y=prediction[0],actual_y=y[t,0],rw_y=y[t-1,0],fit_n=t-3,status='ok'))
        except ValueError as exc:results.append(dict(month=rows[t]['month'],predicted_y=None,actual_y=y[t,0],rw_y=y[t-1,0],fit_n=t-3,status=str(exc)))
    valid=[r for r in results if r['status']=='ok']
    if len(valid)!=24:return results,None
    mse=lambda key:float(np.mean([(r['actual_y']-r[key])**2 for r in valid]))
    return results,math.sqrt(mse('predicted_y')/mse('rw_y'))


def main_outputs(bootstrap_n=199):
    INPUTS.clear();read('data/r3_reopen_source_manifest.json');rows=panel();y,z=arrays(rows);configs=read('research/r3_reopen_calibration.json')
    primary=next(c for c in configs if c['primary'])
    configs += [dict(primary,id='zero_kernel',b_gel_per_usd=[0]*4,primary=False),dict(primary,id='reversed_kernel',b_gel_per_usd=[-v for v in primary['b_gel_per_usd']],primary=False)]
    outputs={'model_panel.csv':csv_text(rows)};coeff=[];paths=[];validation=[];summaries=[];irfs=[];residuals=[]
    primary_model=None
    for cfg in configs:
        irf=[]
        for t in range(61):
            value=(cfg['rho']*irf[-1] if t else 0)+(cfg['b_gel_per_usd'][t] if t<4 else 0);irf.append(value)
            irfs.append(dict(spec=cfg['id'],month_after_impulse=t,log_quote_pct_response_to_1pct_gdp=value,classification='external kernel or diagnostic challenger'))
        vp,ratio=validate(rows,y,z,cfg)
        validation += [dict(spec=cfg['id'],**r) for r in vp]
        for scaled in (False,True) if cfg['id']==primary['id'] else (False,):
            name=cfg['id']+('_gdp38100' if scaled else '')
            try:
                yy,zz=arrays(rows,scaled);model=fit(yy,zz,list(range(3,60)),cfg);eigen=root(model)
                result,reconstruction=simulate(model,rows,yy,zz,scale2025=scaled)
                reserve_ok=min(r['conditional_non_gold_non_sdr_usdm'] for r in result)>=0
                passing=ratio is not None and ratio<=1.2 and eigen<1 and reserve_ok
                status='preliminary_checks_only' if passing else 'rejected_diagnostic'
                summaries.append(dict(spec=name,fit_n=model['n'],rmse_over_random_walk=ratio,max_transition_root=eigen,
                    min_non_gold_non_sdr_usdm=min(r['conditional_non_gold_non_sdr_usdm'] for r in result),
                    endpoint_candidate_gel_per_usd=result[-1]['candidate_gel_per_usd'],endpoint_gap_pct=result[-1]['actual_over_candidate_gap_pct'],
                    mean_monthly_gap_pct=float(np.mean([r['actual_over_candidate_gap_pct'] for r in result])),
                    min_candidate_rate_pct=min(r['candidate_policy_rate_pct'] for r in result),max_candidate_rate_pct=max(r['candidate_policy_rate_pct'] for r in result),
                    candidate_sales_usdm=-sum(r['candidate_net_intervention_usdm'] for r in result),max_baseline_reconstruction_error=reconstruction,status=status))
                paths += [dict(spec=name,status=status,**r) for r in result]
                for field in ('ai','ay','aq','b'):
                    for j,value in enumerate(model[field]):coeff.append(dict(spec=name,block=field,index=j,value=value))
                for field in ('rho','theta','det'):coeff.append(dict(spec=name,block=field,index=0,value=model[field]))
                innovations=np.array([shocks(model,yy,zz,t) for t in range(3,60)])
                for j,label in enumerate(['rate','fx','intervention']):
                    residuals.append(dict(spec=name,equation=label,lag_one_correlation=float(np.corrcoef(innovations[:-1,j],innovations[1:,j])[0,1]),residual_sd=float(innovations[:,j].std(ddof=1))))
                if name==primary['id']:primary_model=model
            except (ValueError,OverflowError) as exc:
                summaries.append(dict(spec=name,fit_n=57,rmse_over_random_walk=ratio,max_transition_root=None,min_non_gold_non_sdr_usdm=None,endpoint_candidate_gel_per_usd=None,endpoint_gap_pct=None,mean_monthly_gap_pct=None,min_candidate_rate_pct=None,max_candidate_rate_pct=None,candidate_sales_usdm=None,max_baseline_reconstruction_error=None,status='rejected: '+str(exc)))
    boot=[];rng=np.random.default_rng(20261116)
    for draw in range(bootstrap_n):
        indices=[]
        while len(indices)<57:
            start=int(rng.integers(3,55));indices.extend(range(start,start+6))
        try:
            model=fit(y,z,indices[:57],primary);eigen=root(model);rr,_=simulate(model,rows,y,z)
            feasible=min(r['conditional_non_gold_non_sdr_usdm'] for r in rr)>=0
            boot.append(dict(draw=draw,max_root=eigen,endpoint_gap_pct=rr[-1]['actual_over_candidate_gap_pct'],reserve_feasible=feasible,admissible=eigen<1 and feasible,error=''))
        except (ValueError,OverflowError) as exc:boot.append(dict(draw=draw,max_root=None,endpoint_gap_pct=None,reserve_feasible=False,admissible=False,error=str(exc)))
    accepted=[b['endpoint_gap_pct'] for b in boot if b['admissible']]
    primary_summary=next(r for r in summaries if r['spec']==primary['id'])
    publish=(primary_summary['status']=='preliminary_checks_only' and len(accepted)/bootstrap_n>=.9)
    for row in paths:
        row['release_status']='conditional_candidate_only' if publish and row['spec']==primary['id'] else 'NOT_AN_ACCEPTED_COUNTERFACTUAL'
    report=dict(design_commit=DESIGN,fit_months=57,holdout_months=24,bootstrap_draws=bootstrap_n,admissible_bootstrap_draws=len(accepted),
        primary_passes_declared_quantitative_gates=publish,preferred_path_released=publish,
        causal_identification=False,episode_gross_purchases_observed=False,
        bootstrap_unstable=sum(b['max_root'] is not None and b['max_root']>=1 for b in boot),
        bootstrap_reserve_infeasible=sum(not b['reserve_feasible'] for b in boot),
        bootstrap_fit_errors=sum(bool(b['error']) for b in boot),
        historical_policy_rate_min_pct=float(y[:60,1].min()),historical_policy_rate_max_pct=float(y[:60,1].max()),
        historical_max_net_sale_pct_gdp=float(-y[:60,2].min()),
        conditional_bootstrap_percentiles_on_admissible_draws=None if not accepted else np.percentile(accepted,[2.5,50,97.5]).tolist(),
        input_sha256=INPUTS,all_sign_and_calibration_cases=summaries,
        warning='Candidate paths are rejected diagnostics unless gates pass. Conditional sampling percentiles exclude failed draws with counts and are not a causal interval.')
    outputs.update({k+'.csv':csv_text(v) for k,v in [('residual_diagnostics',residuals),('coefficients',coeff),('candidate_paths',paths),('hindcasts',validation),('model_comparison',summaries),('external_kernels',irfs),('bootstrap',boot)]})
    report['output_sha256']={k:hashlib.sha256(v.encode()).hexdigest() for k,v in outputs.items()}
    outputs['validation.json']=json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n'
    return outputs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--verify-sources',action='store_true');parser.add_argument('--acquire',action='store_true')
    args=parser.parse_args()
    if args.verify_sources or args.acquire:verify_sources(args.acquire)
    outputs=main_outputs();OUT.mkdir(parents=True,exist_ok=True)
    for name,value in outputs.items():
        p=OUT/name
        if args.check:
            if p.read_bytes()!=value.encode():raise ValueError('Output differs: '+name)
        else:p.write_bytes(value.encode())
    info=json.loads(outputs['validation.json']);print(json.dumps({k:info[k] for k in ['preferred_path_released','admissible_bootstrap_draws','all_sign_and_calibration_cases']},indent=2))


if __name__=='__main__':main()
