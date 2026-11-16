"""R6 reserve-benefit thresholds. Standard library; no estimated policy effects."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/r6_2026_11_15'
INPUTS = {}


def read(path, kind='csv'):
    data = (ROOT/path).read_bytes()
    INPUTS[path] = hashlib.sha256(data).hexdigest()
    return json.loads(data) if kind == 'json' else list(csv.DictReader(io.StringIO(data.decode())))


def csv_text(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: round(v, 9) if isinstance(v, float) else v for k,v in row.items()})
    return stream.getvalue()


def avoided_shortfall(buffer, addition, drain):
    """One disjoint pool of liquid funds; a dollar of principal used at most once."""
    if min(buffer, addition, drain) < 0:
        raise ValueError('Negative liquidity input')
    return max(drain-buffer, 0) - max(drain-buffer-addition, 0)


def hazard_threshold(cost, loss):
    if loss <= 0:
        raise ValueError('Positive conditional loss required')
    return max(cost, 0) / loss


def bond_price(face, coupon, yield_rate, years=5, frequency=2):
    if face <= 0 or coupon < 0 or yield_rate <= -frequency or years*frequency != int(years*frequency):
        raise ValueError('Invalid bond domain')
    n = int(years*frequency)
    return sum(face*coupon/frequency/(1+yield_rate/frequency)**k for k in range(1,n+1)) + face/(1+yield_rate/frequency)**n


def price_spread_threshold(face, coupon, yield_rate, cost_pv, spread_limit, years=5):
    """Yield reduction needed for extra proceeds, capped at removing all spread."""
    if spread_limit < 0 or yield_rate-spread_limit <= -2:
        raise ValueError('Invalid spread floor')
    observed = bond_price(face,coupon,yield_rate,years)
    if cost_pv <= 0:
        return 0.
    if cost_pv > bond_price(face,coupon,yield_rate-spread_limit,years)-observed:
        return None
    lo,hi=0.,spread_limit
    for _ in range(80):
        mid=(lo+hi)/2
        if bond_price(face,coupon,yield_rate-mid,years)-observed < cost_pv:
            lo=mid
        else:
            hi=mid
    return (lo+hi)/2


def rolling_sales(rows, horizon):
    """Maximum net sales in complete pre-episode monthly windows; purchases offset sales."""
    ordered=sorted((r for r in rows if '2020-01' <= r['month'] <= '2024-12'),key=lambda r:r['month'])
    if len({r['month'] for r in ordered}) != len(ordered):
        raise ValueError('Duplicate intervention month')
    found=[]
    for i in range(len(ordered)-horizon+1):
        window=ordered[i:i+horizon]
        indices=[int(r['month'][:4])*12+int(r['month'][5:7]) for r in window]
        if any(b-a != 1 for a,b in zip(indices,indices[1:])):
            continue
        values=[float(r['net_market_purchases_usdm']) for r in window]
        if not all(math.isfinite(x) for x in values):
            raise ValueError('Nonfinite intervention')
        found.append((max(-sum(values),0.),window[0]['month'],window[-1]['month']))
    if not found:
        raise ValueError('No complete monthly window')
    value,start,end=max(found)
    return dict(horizon_months=horizon,complete_windows=len(found),max_net_sales_usdm=value,
                start_month=start,end_month=end,classification='historical net market transactions; not external funding stress or a forecast')


def verify_sources(acquire=False):
    for item in read('data/r6_source_manifest.json','json'):
        path=ROOT/item['local_path']
        if not path.exists() and acquire:
            request=urllib.request.Request(item['url'],headers={'User-Agent':'Georgia reserve research replication'})
            with urllib.request.urlopen(request,timeout=60) as response:
                data=response.read(20_000_001)
            if len(data)>20_000_000 or not data.startswith(b'%PDF'):
                raise ValueError('Invalid or oversized source PDF')
            if hashlib.sha256(data).hexdigest()!=item['sha256']:
                raise ValueError('Provider changed pinned source; keep a separate vintage')
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Missing or changed raw source: '+str(path))
        if item['id']=='mof_2026_offering':
            text=subprocess.check_output(['pdftotext','-layout','-f','2','-l','2',str(path),'-'],text=True)
            if not re.search(r'payable semi-annually in arrear on 28 January and 28 July',text):
                raise ValueError('Coupon payment convention differs')
        if item['id']=='mof_feb2026':
            text=subprocess.check_output(['pdftotext','-layout','-f','6','-l','6',str(path),'-'],text=True)
            for label,expected in [('Issue size','$500mm'),('Price','98.917'),('Benchmark Yield','3.856%'),('Spread to Benchmark','151.9 bps'),('Re-offer Yield','5.375%'),('Coupon','5.125%'),('Settlement Date','28 January 2026'),('Maturity Date','28 January 2031')]:
                if not re.search(re.escape(label)+r'\s+'+re.escape(expected),text):
                    raise ValueError('Source term differs: '+label)
            oldtext=subprocess.check_output(['pdftotext','-layout','-f','5','-l','5',str(path),'-'],text=True)
            for label,expected in [('Benchmark Yield','0.801%'),('Spread to Benchmark','207.4 bps'),('Re-offer Yield','2.875%'),('Coupon','2.75%')]:
                if not re.search(re.escape(label)+r'\s+'+re.escape(expected),oldtext):
                    raise ValueError('2021 source term differs: '+label)


def generate():
    INPUTS.clear()
    a=read('research/r6_assumptions.json','json')
    bond=read('research/r6_bond_terms.json','json')
    read('data/r6_source_manifest.json','json')
    # Lock the upstream provenance links as well as the numeric tables.
    for stage,day,key in [('r2','2026_11_11','csv_sha256'),('r4','2026_11_12','sha256')]:
        directory=f'reports/{stage}_{day}/'
        locked=read(directory+'validation.json','json')
        for name,digest in locked[key].items():
            if hashlib.sha256((ROOT/directory/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('Changed upstream checkpoint: '+directory+name)
    carries=read('reports/r4_2026_11_12/conditional_carry.csv')
    ara=[r for r in read('reports/r2_2026_11_11/ara_components.csv') if r['quarter']=='2025Q4']
    stress=read('reports/r2_2026_11_11/liquidity_stress.csv')
    schedule=read('reports/r2_2026_11_11/liquidity_schedule.csv')
    intervention=read('data/derived/episode_2026_11_09/intervention_monthly.csv')
    reference=next(r for r in carries if r['mechanism']=='rolling GEL CD' and float(r['gel_per_usd_change_pct'])==0)
    base_cost=-float(reference['terminal_net_gelm'])/float(reference['initial_gel_per_usd'])
    principal=float(reference['principal_usdm'])
    if principal != a['additional_reserves_usdm']:
        raise ValueError('R4 principal assumption mismatch')
    gdp=a['gdp_usdm']
    reserves=float(ara[0]['gir_usdm'])
    if any(float(r['gir_usdm'])!=reserves for r in ara):
        raise ValueError('Inconsistent reserve stock')
    thresholds=[]
    severity=[]
    for c in carries:
        terminal_fx=float(c['initial_gel_per_usd'])*(1+float(c['gel_per_usd_change_pct'])/100)
        cost=-float(c['terminal_net_gelm'])/terminal_fx
        for loss_share in a['crisis_loss_gdp_shares']:
            for alpha in a['resource_cost_share_scenarios']:
                req=hazard_threshold(alpha*cost,gdp*loss_share)
                thresholds.append(dict(mechanism=c['mechanism'],gel_per_usd_change_pct=float(c['gel_per_usd_change_pct']),
                    terminal_cost_usdm=cost,assumed_resource_cost_share=alpha,crisis_loss_gdp_share=loss_share,
                    hurdle_usdm=max(alpha*cost,0),required_annual_hazard_reduction_pp=100*req,
                    feasible_under_assumed_10pct_hazard=req<=.10,
                    classification='cost-equivalent sensitivity; neither national cost allocation nor achieved hazard reduction'))
        for probability in a['annual_hazard_scenarios']:
            severity.append(dict(mechanism=c['mechanism'],gel_per_usd_change_pct=float(c['gel_per_usd_change_pct']),annual_hazard=probability,
                conditional_financial_cost_usdm=cost,required_conditional_loss_reduction_usdm=max(cost,0)/probability,
                required_normal_state_only_cost_loss_reduction_usdm=(1-probability)*max(cost,0)/probability,
                classification='one-year financial hurdle, not measured national welfare benefit'))
    targets=[]
    for r in ara:
        for ratio in a['target_ara_ratios']:
            target=ratio*float(r['ara_usdm'])
            extra=max(target-reserves,0)
            cost=extra*base_cost/principal
            targets.append(dict(money_definition=r['money_series'],ara_usdm=float(r['ara_usdm']),target_ara_pct=ratio*100,
                current_gir_usdm=reserves,target_gir_usdm=target,additional_reserves_usdm=extra,
                annual_cd_cost_usdm=cost,required_hazard_reduction_pp_if_loss_10pct_gdp=100*cost/(.10*gdp),
                classification='static unchanged-FX CD scenario; fixed ARA/GDP; not replicated IMF target or observed loss'))
    history=[rolling_sales(intervention,h) for h in (1,3,12)]
    base_schedules={(r['date'],r['horizon_months']):r for r in schedule}
    joint=[]
    for r in stress:
        s=base_schedules[r['date'],r['horizon_months']]
        available=float(r['conditional_remaining_usdm'])
        expected=float(s['headline_usdm'])+float(s['reported_II_1_signed_usdm'])+float(r['contingent_called_share'])*float(s['reported_III_1_signed_usdm'])-float(r['gold_unavailable_share'])*float(s['gold_usdm'])
        if abs(expected-available)>1e-6 or available<0:
            raise ValueError('Liquidity accounting failure')
        joint.append(dict(date=r['date'],horizon_months=int(r['horizon_months']),gold_unavailable_share=float(r['gold_unavailable_share']),
            contingent_called_share=float(r['contingent_called_share']),conditional_buffer_usdm=available,
            additional_disjoint_need_to_begin_using_increment_usdm=available,
            additional_disjoint_need_to_exhaust_100m_increment_usdm=available+principal,
            currency_matching_status='unverified; aggregate USD-equivalent only',external_alternative_credit_usdm=None))
    curves=[]
    for r in joint:
        if r['date']!=a['base_date'] or r['horizon_months']!=12:
            continue
        for liquid_share in a['incremental_liquid_shares']:
            knots=set(a['uncovered_drain_grid_usdm']) | {r['conditional_buffer_usdm'],r['conditional_buffer_usdm']+principal*liquid_share}
            for need in sorted(knots):
                avoided=avoided_shortfall(r['conditional_buffer_usdm'],principal*liquid_share,need)
                curves.append(dict(gold_unavailable_share=r['gold_unavailable_share'],contingent_called_share=r['contingent_called_share'],
                    additional_reserves_usdm=principal,incremental_liquid_share=liquid_share,additional_disjoint_need_usdm=need,
                    conditional_buffer_usdm=r['conditional_buffer_usdm'],shortfall_without_increment_usdm=max(need-r['conditional_buffer_usdm'],0),
                    shortfall_avoided_usdm=avoided,classification='conditional liquidity service; no probability or welfare multiplier assigned'))
    face=bond['face_usdm'];coupon=bond['coupon_pct']/100;yield_rate=bond['yield_pct']/100
    observed_price=bond_price(face,coupon,yield_rate,bond['years'])
    reported_proceeds=face*bond['price_pct']/100
    if abs(observed_price-reported_proceeds)>face*.000005+1e-9:
        raise ValueError('Price/yield convention fails reported price rounding')
    if abs((bond['yield_pct']-bond['benchmark_yield_pct'])*100-bond['spread_bps'])>1e-7:
        raise ValueError('Benchmark spread mismatch')
    annual_discount=(1+yield_rate/2)**2-1
    annuity=sum((1+annual_discount)**(-t) for t in range(1,bond['years']+1))
    pricing=[]
    for delta in [principal]+[r['additional_reserves_usdm'] for r in targets]:
        spread=a['spread_slope']*math.log1p(delta/(gdp+reserves))
        pv_cost=base_cost*delta/principal*annuity
        financing_gain=bond_price(face,coupon,yield_rate-spread,bond['years'])-observed_price
        required=price_spread_threshold(face,coupon,yield_rate,pv_cost,bond['spread_bps']/10000,bond['years'])
        loss_avoided=.005*gdp*math.log1p(delta/(gdp+reserves))
        pricing.append(dict(additional_reserves_usdm=delta,exposure_face_usdm=face,observed_gross_proceeds_usdm=reported_proceeds,
            reproduced_gross_proceeds_usdm=observed_price,annual_cost_usdm=base_cost*delta/principal,
            cost_5y_pv_usdm=pv_cost,discount_effective_annual_pct=annual_discount*100,
            annex_implied_spread_change_bps=spread*10000,conditional_issuance_proceeds_gain_usdm=financing_gain,
            breakeven_additional_reserves_yield_reduction_bps=None if required is None else required*10000,
            max_proceeds_gain_if_sovereign_spread_zero_usdm=bond_price(face,coupon,bond['benchmark_yield_pct']/100,bond['years'])-observed_price,
            isolated_dollarization_crisis_loss_reduction_usdm=loss_avoided,
            isolated_expected_loss_reduction_at_annual_10pct_usdm=.10*loss_avoided,
            classification='hypothetical increment above observed reserves; frozen rates 5y; Annex mechanisms unestimated; channels not added'))
    old=bond['old_bond']
    comparison=[dict(variable=key,value_2021=old[key],value_2026=bond[key],change=bond[key]-old[key],
        classification='different pricing dates; no reserve attribution') for key in ['yield_pct','benchmark_yield_pct','spread_bps','coupon_pct']]
    outputs={name+'.csv':csv_text(rows) for name,rows in [
        ('hazard_thresholds',thresholds),('severity_thresholds',severity),('target_sensitivity',targets),
        ('historical_sales_scale',history),('joint_liquidity',joint),('liquidity_service_curves',curves),
        ('financing_and_model_channels',pricing),('issuance_comparison',comparison)]}
    outputs['validation.json']=json.dumps(dict(inputs=INPUTS,outputs_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in outputs.items()},
        end2025_gdp_usdm=gdp,reserve_increment_usdm=principal,reference_annual_financial_cost_usdm=base_cost,
        reported_minus_reproduced_bond_proceeds_usdm=reported_proceeds-observed_price,
        observed_episode_benefit_usdm=None,optimal_reserves_usdm=None,achieved_hazard_reduction=None,
        raw_source_verification_command='python src/r6_benefits.py --verify-sources --check'),indent=2,sort_keys=True)+'\n'
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--verify-sources',action='store_true')
    parser.add_argument('--acquire',action='store_true',help='download missing pinned PDFs only; never overwrite')
    args=parser.parse_args()
    if args.verify_sources or args.acquire:
        verify_sources(args.acquire)
    outputs=generate()
    OUT.mkdir(parents=True,exist_ok=True)
    for name,text in outputs.items():
        path=OUT/name
        if args.check:
            if path.read_bytes()!=text.encode():
                raise ValueError(name+' differs')
        else:
            path.write_bytes(text.encode())
    print('R6: '+str(len(outputs))+' reproducible outputs; episode benefit remains unidentified')


if __name__=='__main__':
    main()
