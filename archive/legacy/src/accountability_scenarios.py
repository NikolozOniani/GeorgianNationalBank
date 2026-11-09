"""Offline, deterministic accountability calculations; no causal estimation.

Run from any directory: python src/accountability_scenarios.py
Only committed, hash-locked inputs are used. Standard library only.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/accountability'


def rows(path):
    with (ROOT / path).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def chain(rates):
    values = list(rates)
    if not values or any(not math.isfinite(x) or x <= -100 for x in values):
        raise ValueError('Missing/invalid CPI relatives must not become zeros')
    return math.prod(1 + x / 100 for x in values)


def interest_increment(principal, shock_pp, pass_through=1):
    if principal < 0 or not 0 <= pass_through <= 1:
        raise ValueError('Invalid balance or pass-through')
    return principal * shock_pp / 100 * pass_through


def fx_increment(usd, rate, depreciation_fraction):
    return usd * rate * depreciation_fraction


def reserve_residual(stock_change, net_sales):
    # Purchases add reserves; the annual source reports sales positive.
    return stock_change + net_sales


def verify_inputs():
    lock = json.loads((OUT / 'inputs.lock.json').read_text())
    for name, expected in lock['sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Input changed: {name}; review before updating lock')
    return lock


def compute():
    verify_inputs()
    panel = rows('reports/nbg_policy_monthly_2020_2024.csv')
    expected = [f'{y}-{m:02}' for y in range(2020, 2025) for m in range(1, 13)]
    if [r['month'] for r in panel] != expected:
        raise ValueError('Monthly panel must be consecutive, unique, and ordered')
    by_month = {r['month']: r for r in panel}
    annual = {r['year']: r for r in rows('reports/nbg_fx_annual_benchmarks.csv')}
    pilot = rows('reports/pilot2017_exposure.csv')
    validation = json.loads((ROOT / 'reports/pilot2017_validation.json').read_text())
    ledger = []

    def add(id, claim, value, units, period, classification, source, calculation, limitations):
        ledger.append(dict(id=id, claim=claim, value=value, units=units, period=period,
                           evidence_class=classification, source_id=source,
                           calculation=calculation, uncertainty_and_limitations=limitations))

    factor = chain(float(r['cpi_monthly_pct']) for r in panel)
    caveat = ('National chained CPI, current downloaded vintage; rounded source relatives; '
              'changing national index weights, not a household-specific constant basket; '
              'not attributable to NBG. No statistical confidence interval estimated.')
    add('N01', 'National CPI cumulative change', 100*(factor-1), 'percent',
        'Dec 2019–Dec 2024', 'C', 'CPI', '100*(product(1+monthly_pct/100)-1)', caveat)
    add('N02', 'Cost of CPI-indexed GEL 1000 baseline spending', 1000*factor, 'GEL/month',
        'Dec 2024 versus Dec 2019', 'B', 'CPI', '1000*price_factor',
        'Illustrative unchanged index exposure; not actual spending or fixed physical basket. '+caveat)
    add('N03', 'Purchasing power of unchanged GEL 1000', 1000/factor, 'Dec 2019 GEL/month',
        'Dec 2024 versus Dec 2019', 'B', 'CPI', '1000/price_factor',
        'Assumes no nominal income change; not measured income evolution. '+caveat)
    add('N04', 'Loss of purchasing power at fixed nominal income', 100*(1-1/factor), 'percent',
        'Dec 2019–Dec 2024', 'B', 'CPI', '100*(1-1/price_factor)',
        'Not the same percentage as price increase; conditional on fixed nominal income. '+caveat)
    for y in range(2020, 2025):
        add(f'Y{y}', 'National annual December-over-December CPI',
            100*(chain(float(r['cpi_monthly_pct']) for r in panel if r['month'][:4]==str(y))-1),
            'percent', f'Dec {y-1}–Dec {y}', 'C', 'CPI', 'Compound twelve monthly relatives', caveat)
    for id, month in [('N05', '2020-01'), ('N06', '2022-03'), ('N07', '2024-12')]:
        add(id, 'NBG policy rate at month end', float(by_month[month]['policy_rate_end_pct']),
            'percent/year', month, 'A', 'RATE', 'Read effective rate from verified panel',
            'Policy instrument, not retail loan APR; 2024 observation is not current rate.')
    for year in ('2023', '2024'):
        for suffix, col in [('A','auction_net_sales_usd_m'),('B','bmatch_net_sales_usd_m'),('T','total_net_sales_usd_m')]:
            add(f'F{year}{suffix}', col, float(annual[year][col]), 'USD million, sales positive',
                year, 'A', f'ANNUAL{year}', 'Annual report benchmark; purchases negative',
                'Net annual flows, not gross turnover, not household costs; execution months unavailable here.')
    stock_change = float(by_month['2024-12']['official_reserves_usd_m'])-float(by_month['2023-12']['official_reserves_usd_m'])
    add('N08', 'Official reserve stock change', stock_change, 'USD million', 'Dec 2023–Dec 2024',
        'B', 'RESERVES', '2024-12 stock minus 2023-12 stock', 'Stock change is not intervention or loss.')
    add('N09', 'Unreconciled stock-flow composite', reserve_residual(stock_change,float(annual['2024']['total_net_sales_usd_m'])),
        'USD million', '2024', 'B', 'RESERVES;ANNUAL2024', 'Stock change + net FX sales',
        'Unallocated government/valuation/income/other effects, timing and perimeter differences; not missing money.')
    add('N10', 'Official GEL per USD quotation', float(by_month['2024-12']['official_usd_gel_month_end']),
        'GEL/USD', 'Dec 2024 month end', 'A', 'USD', 'Verified official API quote',
        'Official reference, not retail transaction rate; actual valid-from retained in policy panel.')
    add('N11', 'Validated household-quarter observations', validation['sample_rows'], 'household-quarters',
        '2017', 'A', 'PILOT', 'Validated merged rows', '11590 records are not 11590 independent annual households.')
    add('N12', 'Survey weighted mean household monthly total expenditure', validation['weighted_mean_total_expenditure_gel'],
        'GEL/month', '2017', 'C', 'PILOT', 'Existing weighted mean, not recalculated microdata',
        'Published comparator 1093 GEL; exact tabulation settings unresolved; not current income.')
    all18 = next(r for r in pilot if r['end_year']=='2018' and r['group']=='all')
    for id,col,units in [('P01','direct_only_expenditure_share_pct','percent'),('P02','matched_expenditure_share_pct','percent'),
                         ('P03','unmatched_expenditure_share_pct','percent'),('P04','direct_only_contribution_pp','percentage points'),
                         ('P05','partial_contribution_pp','percentage points')]:
        add(id,col,float(all18[col]),units,'2017 basket; Dec 2017–Dec 2018 prices','C','PILOT',
            'Read existing survey-weighted pilot result',
            'Partial category exposure only. Expanded mapping has two approximate scopes. Not full inflation or welfare. '
            'DiaryID bootstrap omits verified PSU/strata and CPI/mapping uncertainty.')
    for r in pilot:
        if r['end_year']=='2018' and r['group']!='all':
            add('G_'+r['group']+'_'+r['level'], 'Partial contribution: '+r['group']+' '+r['level'],
                float(r['partial_contribution_pp']),'percentage points','Dec 2017–Dec 2018','C','PILOT',
                'Existing expanded mapping; weighted mean household contributions',
                'Group-specific omitted shares differ; no valid ranking of total inflation; pension-age, not pension receipt.')
    for pt in (0, .5, 1):
        add(f'S_RATE_{int(pt*100)}', 'Extra interest on unchanged GEL 10000 balance', interest_increment(10000,2,pt),
            'GEL/year', 'Hypothetical one year', 'B', 'SCENARIO', '10000 * 0.02 * pass_through; pass_through='+str(pt),
            'Scenario, not a causal estimate. Two-point shock, unchanged principal, no fees or amortization; no estimated pass-through.')
    for dep in (.05,.10,.20):
        for usd, name in [(100,'DEBT'),(300,'REMITTANCE')]:
            add(f'S_FX_{name}_{int(dep*100)}', 'Additional GEL equivalent of fixed USD '+name.lower(),
                fx_increment(usd,float(by_month['2024-12']['official_usd_gel_month_end']),dep), 'GEL/month',
                'Hypothetical shock from Dec 2024 quote', 'B', 'USD;SCENARIO', f'{usd} USD * 2.8068 * {dep}',
                'Depreciation raises GEL debt cost but also remittance receipts. Fixed dollar amounts, no fees; no forecast or NBG attribution.')
    for spread in (-1,0,1):
        add('S_CARRY_'+str(spread), 'Financing cost minus reserve income on illustrative position', 100*spread/100,
            'USD million equivalent/year', 'Hypothetical one year', 'B', 'SCENARIO', f'100m equivalent * {spread}/100',
            'Assumed matched-currency effective financing-minus-return spread after hedging; excludes insurance value. '
            'Not actual NBG expense; domestic and foreign nominal yields cannot simply be subtracted.')
    for id,value,label in [('M01',11,'No-FXI peak core inflation'),('M02',13.4,'No-FXI peak policy rate'),
                           ('M03',1.5,'No-FXI core inflation excess'),('M04',2.4,'No-FXI policy rate excess')]:
        add(id,label,value,'percent' if id in ('M01','M02') else 'percentage points',
            '2020–2024 evaluation; 2020–21 peaks','D','IMF','IMF paragraph 29, figure 19',
            'QIPF structural counterfactual; model restrictions, not externally identified household gains.')
    return ledger, panel


def main():
    ledger, panel = compute()
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'evidence_ledger.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ledger[0].keys());w.writeheader();w.writerows(ledger)
    (OUT/'evidence_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
    trajectory=[];factor=1
    for r in panel:
        factor*=1+float(r['cpi_monthly_pct'])/100
        trajectory.append({'month':r['month'],'national_cpi_dec2019_100':100*factor,
                           'unchanged_1000_gel_in_dec2019_prices':1000/factor})
    with (OUT/'cpi_illustration.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=trajectory[0].keys());w.writeheader();w.writerows(trajectory)
    # Standalone SVG, reproducible without plotting dependencies; no fitted relationships.
    points=' '.join(f'{80+i*10:.1f},{340-(r["national_cpi_dec2019_100"]-100)*7:.2f}' for i,r in enumerate(trajectory))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="460" viewBox="0 0 800 460">',
         '<rect width="800" height="460" fill="white"/>',
         '<g font-family="sans-serif" fill="#17243b">',
         '<text x="55" y="35" font-size="21">Georgia: national consumer price index, 2020–2024</text>',
         '<text x="55" y="62" font-size="14">December 2019 = 100 • compounded verified monthly CPI</text>']
    for n in (100,110,120,130):
        y=340-(n-100)*7
        svg += [f'<path d="M75 {y} H680" stroke="#ddd"/>',f'<text x="35" y="{y+5}">{n}</text>']
    svg += [f'<polyline points="{points}" fill="none" stroke="#125c80" stroke-width="3"/>']
    for i,y in enumerate(range(2020,2025)):
        svg.append(f'<text x="{80+i*120}" y="369">{y}</text>')
    svg += [f'<text x="686" y="125">{trajectory[-1]["national_cpi_dec2019_100"]:.2f}</text>',
            '<text x="55" y="407" font-size="14">Source: Geostat; pinned repository CPI series. Not an NBG causal effect.</text>',
            '<text x="55" y="431" font-size="14">National index; not every household’s basket, income, or welfare.</text></g></svg>']
    (OUT/'national_cpi.svg').write_text('\n'.join(svg)+'\n')
    print(f'Wrote {len(ledger)} evidence/scenario rows; no causal regressions.')


if __name__=='__main__':
    main()
