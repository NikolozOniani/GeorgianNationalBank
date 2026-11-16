"""Read-only audit of R6 cf9dee7. Independent Decimal arithmetic; no output rewrites."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from datetime import datetime
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/r6_2026_11_15'
getcontext().prec=45
CHECKS=0
HASHES={}


def read(path):
    p=ROOT/path
    data=p.read_bytes();HASHES[path]=hashlib.sha256(data).hexdigest()
    if p.suffix=='.json': return json.loads(data)
    return list(csv.DictReader(io.StringIO(data.decode())))


def equal(actual,expected,tol='0.00000001'):
    global CHECKS
    assert abs(D(str(actual))-D(str(expected)))<=D(tol),(actual,expected)
    CHECKS+=1


def price(face,coupon,y):
    # Independent closed-form annuity for ten semiannual payments.
    z=1+y/2
    return face*coupon/2*(1-z**-10)/(z-1)+face*z**-10


def run():
    global CHECKS
    CHECKS=0;HASHES.clear()
    assumptions=read('research/r6_assumptions.json')
    bond=read('research/r6_bond_terms.json')
    manifest=read('data/r6_source_manifest.json')
    pdfs={}
    for source in manifest:
        p=ROOT/source['local_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256']
        pdfs[source['id']]=p;CHECKS+=1
    text={p:subprocess.check_output(['pdftotext','-layout','-f',str(p),'-l',str(p),str(pdfs['mof_feb2026']),'-'],text=True) for p in (5,6)}
    def number(page,label):
        match=re.search(re.escape(label)+r'\s+\$?([\d.]+)',text[page]);assert match,label
        return D(match[1].rstrip('.'))
    for field,label in [('face_usdm','Issue size'),('coupon_pct','Coupon'),('yield_pct','Re-offer Yield'),('price_pct','Price'),('benchmark_yield_pct','Benchmark Yield'),('spread_bps','Spread to Benchmark')]:
        equal(bond[field],number(6,label))
    for field,label in [('face_usdm','Issue size'),('coupon_pct','Coupon'),('yield_pct','Re-offer Yield'),('benchmark_yield_pct','Benchmark Yield'),('spread_bps','Spread to Benchmark')]:
        equal(bond['old_bond'][field],number(5,label))
    for field,label in [('pricing_date','Pricing Date'),('settlement_date','Settlement Date'),('maturity_date','Maturity Date')]:
        match=re.search(re.escape(label)+r'\s+(\d+ \w+ \d{4})',text[6]);assert match,label
        assert bond[field]==datetime.strptime(match[1],'%d %B %Y').date().isoformat();CHECKS+=1
    benchmark=re.search(r'Benchmark\s+([\d.]+)%\.?\s+due (\d+ \w+ \d{4})',text[6]);assert benchmark
    equal(bond['benchmark_coupon_pct'],benchmark[1])
    assert bond['benchmark_maturity']==datetime.strptime(benchmark[2],'%d %B %Y').date().isoformat();CHECKS+=1
    frequency=subprocess.check_output(['pdftotext','-layout','-f','2','-l','2',str(pdfs['mof_2026_offering']),'-'],text=True)
    assert 'payable semi-annually in arrear on 28 January and 28 July' in frequency
    assert bond['payments_per_year']==2 and bond['years']==5;CHECKS+=2
    start,end=[datetime.fromisoformat(bond[k]) for k in ('settlement_date','maturity_date')]
    assert (end.year-start.year,end.month,end.day)==(5,start.month,start.day);CHECKS+=1
    carry=read('reports/r4_2026_11_12/conditional_carry.csv')
    cost={}
    for row in carry:
        x=D(row['gel_per_usd_change_pct'])/100
        value=D(row['principal_usdm'])*((1+D(row['gel_cost_pct'])/100)/(1+x)-(1+D(row['usd_return_proxy_pct'])/100))
        equal(-D(row['terminal_net_gelm'])/(D(row['initial_gel_per_usd'])*(1+x)),value)
        cost[row['mechanism'],row['gel_per_usd_change_pct']]=value
    gdp=D(str(assumptions['gdp_usdm']));c=D('4.22')
    for row in read('reports/r6_2026_11_15/hazard_thresholds.csv'):
        x=cost[row['mechanism'],str(int(D(row['gel_per_usd_change_pct'])))];alpha=D(row['assumed_resource_cost_share'])
        equal(row['terminal_cost_usdm'],x)
        equal(row['required_annual_hazard_reduction_pp'],100*max(alpha*x,0)/(gdp*D(row['crisis_loss_gdp_share'])))
    for row in read('reports/r6_2026_11_15/severity_thresholds.csv'):
        x=max(cost[row['mechanism'],str(int(D(row['gel_per_usd_change_pct'])))],0);p=D(row['annual_hazard'])
        equal(row['required_conditional_loss_reduction_usdm'],x/p)
        equal(row['required_normal_state_only_cost_loss_reduction_usdm'],(1-p)*x/p)
    ara={r['money_series']:r for r in read('reports/r2_2026_11_11/ara_components.csv') if r['quarter']=='2025Q4'}
    reserves=D(ara['M2']['gir_usdm']);increments=[D(100)]
    for row in read('reports/r6_2026_11_15/target_sensitivity.csv'):
        target=D(ara[row['money_definition']]['ara_usdm'])*D(row['target_ara_pct'])/100
        gap=target-reserves;increments.append(gap)
        equal(row['target_gir_usdm'],target);equal(row['additional_reserves_usdm'],gap)
        equal(row['annual_cd_cost_usdm'],gap*c/100)
        equal(row['required_hazard_reduction_pp_if_loss_10pct_gdp'],gap*c/(gdp*D('.1')))
    schedules={(r['date'],r['horizon_months']):r for r in read('reports/r2_2026_11_11/liquidity_schedule.csv')}
    for row in read('reports/r6_2026_11_15/joint_liquidity.csv'):
        s=schedules[row['date'],row['horizon_months']]
        b=D(s['headline_usdm'])+D(s['reported_II_1_signed_usdm'])+D(row['contingent_called_share'])*D(s['reported_III_1_signed_usdm'])-D(row['gold_unavailable_share'])*D(s['gold_usdm'])
        equal(row['conditional_buffer_usdm'],b)
        equal(row['additional_disjoint_need_to_exhaust_100m_increment_usdm'],b+100)
    for row in read('reports/r6_2026_11_15/liquidity_service_curves.csv'):
        need=D(row['additional_disjoint_need_usdm']);buffer=D(row['conditional_buffer_usdm'])
        usable=D(row['additional_reserves_usdm'])*D(row['incremental_liquid_share'])
        equal(row['shortfall_avoided_usdm'],min(max(need-buffer,0),usable))
    months=sorted((r for r in read('data/derived/episode_2026_11_09/intervention_monthly.csv') if '2020-01'<=r['month']<='2024-12'),key=lambda r:r['month'])
    assert [r['month'] for r in months]==[f'{y}-{m:02d}' for y in range(2020,2025) for m in range(1,13)];CHECKS+=1
    values=[-D(r['net_market_purchases_usdm']) for r in months]
    for row in read('reports/r6_2026_11_15/historical_sales_scale.csv'):
        n=int(row['horizon_months']);equal(row['max_net_sales_usdm'],max([D(0)]+[sum(values[i:i+n]) for i in range(61-n)]))
        equal(row['complete_windows'],61-n)
    face=D(str(bond['face_usdm']));coupon=D(str(bond['coupon_pct']))/100;y=D(str(bond['yield_pct']))/100
    p0=price(face,coupon,y);factor=(1+y/2)**2
    annuity=(1-factor**-5)/(factor-1)
    finance=read('reports/r6_2026_11_15/financing_and_model_channels.csv')
    for row,extra in zip(finance,increments):
        equal(row['additional_reserves_usdm'],extra)
        slope=D(str(assumptions['spread_slope']));ds=slope*((1+(reserves+extra)/gdp).ln()-(1+reserves/gdp).ln())
        pv=c*extra/100*annuity
        equal(row['cost_5y_pv_usdm'],pv);equal(row['annex_implied_spread_change_bps'],10000*ds)
        equal(row['conditional_issuance_proceeds_gain_usdm'],price(face,coupon,y-ds)-p0)
        def loss(r): return D('.1')*(1+D('.5')*(D('.6')-D('.1')*(1+r).ln()))
        equal(row['isolated_dollarization_crisis_loss_reduction_usdm'],gdp*(loss(reserves/gdp)-loss((reserves+extra)/gdp)))
        if row['breakeven_additional_reserves_yield_reduction_bps']:
            delta=D(row['breakeven_additional_reserves_yield_reduction_bps'])/10000
            equal(price(face,coupon,y-delta)-p0,pv)
        else:
            assert pv>price(face,coupon,D(str(bond['benchmark_yield_pct']))/100)-p0;CHECKS+=1
    # Deliberate in-memory corruption. Do not modify input files or committed outputs.
    sys.path.insert(0,str(ROOT/'src'));import r6_benefits as production
    original_read=production.read
    baseline=production.generate()
    faults={}
    for key,value in [('face_usdm',5000),('payments_per_year',1)]:
        def replacement(path,kind='csv'):
            result=original_read(path,kind)
            if path=='research/r6_bond_terms.json': result[key]=value
            return result
        with patch.object(production,'read',replacement):
            production.verify_sources()
            altered=production.generate()
        changed=[name for name in baseline if name.endswith('.csv') and baseline[name]!=altered[name]]
        faults[key]={'in_memory_value':value,'source_verifier_rejected':False,'generation_rejected':False,'changed_csvs':changed}
    assert faults['face_usdm']['changed_csvs']==['financing_and_model_channels.csv']
    assert faults['payments_per_year']['changed_csvs']==[]
    return {'audited_commit':'cf9dee7c62f3b5eeed8acedd8ab09d8a238b23fd','checks_passed':CHECKS,
        'method':'Decimal precision 45; independent closed-form bond and annuity equations; actual PDF-to-JSON reconciliation',
        'headline_arithmetic':'passed for committed inputs','production_inputs_changed':False,
        'production_outputs_changed':False,'source_binding_failure_demonstrations':faults,'input_sha256':HASHES}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=run();text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.report: args.report.write_text(text)
    print(text)
