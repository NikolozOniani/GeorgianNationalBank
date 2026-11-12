"""R4 public accounting and conditional one-year carry. Python standard library."""
import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import subprocess
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = 'data/derived/episode_2026_11_09/'
R1 = 'reports/r1_2026_11_10/'
R4 = ROOT / 'reports/r4_2026_11_12'
DAY = timedelta(days=1)
INPUTS = {}


def read(name):
    path = ROOT / name
    INPUTS[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def close(a, b, tolerance=.000501):
    if not math.isclose(a, b, abs_tol=tolerance, rel_tol=0):
        raise ValueError(f'{a} differs from {b} beyond {tolerance}')


def csv_text(rows):
    f = io.StringIO(newline='')
    writer = csv.DictWriter(f, fieldnames=rows[0], lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: round(v, 9) if isinstance(v, float) else v for k, v in row.items()})
    return f.getvalue()


def book(issue_cash, face, elapsed_days, term_days):
    """Effective-interest book value from issue to redemption inclusive."""
    return issue_cash * (face / issue_cash) ** (elapsed_days / term_days)


def contracts(name, amount):
    result = []
    for row in read(OLD + name + '.csv'):
        start, end = (date.fromisoformat(row[k]) for k in ('date', 'maturity_date'))
        if start > date(2026, 9, 30) or end <= date(2025, 1, 1):
            continue
        face = float(row[amount]) / 1e6
        if face:
            cash = float(row.get('settlement_gel', row[amount])) / 1e6
            if not (cash > 0 and end > start):
                raise ValueError(row)
            result.append((start, end, face, cash))
    return result


def accounts():
    records = read(OLD + 'annual_interest_accounts.csv')
    levels = {(int(r['year']), r['series']): float(r['value_gelm']) for r in records}
    rows = [dict(series=s, value_2024_gelm=levels[2024,s], value_2025_gelm=v,
                 change_gelm=v-levels[2024,s]) for (y,s),v in levels.items() if y == 2025]
    for year in (2024, 2025):
        get = lambda k: levels[year, k]
        for total, parts in [
            ('reserve_interest_total', ['reserve_interest_cash','reserve_interest_fvoci','reserve_interest_other']),
            ('policy_interest_total', ['policy_interest_financial_institutions','policy_interest_securities']),
            ('policy_expense_total',['policy_expense_financial_institutions','policy_expense_securities']),
            ('interest_income_total',['reserve_interest_total','policy_interest_total','other_interest_income']),
            ('interest_expense_total',['policy_expense_total','imf_interest_expense','customer_interest_expense','lease_interest_expense']),
            ('net_interest_income',['interest_income_total','interest_expense_total'])]:
            close(get(total),sum(map(get,parts)))
    return rows


def monthly():
    cds = contracts('cd_auctions_events','nominal_allocated_gel')
    loans = contracts('refinancing_events','loan_gel')
    positions = {r['date']:r for r in read(R1+'liquidity_counterparts.csv')}
    reserve = {r['date']:r for r in read('reports/r2_2026_11_11/liquidity_schedule.csv') if r['horizon_months']=='1'}
    rows = []
    for y, last in ((2025,12),(2026,9)):
        for m in range(1,last+1):
            n = calendar.monthrange(y,m)[1]
            start = date(y,m,1)
            end = date(y,m,n)
            before, after = (start-DAY).isoformat(), end.isoformat()
            cd_face = accrual = refi = cd_end = 0.
            absent = 0
            for i in range(n):
                day = start+i*DAY
                amount = sum(face for a,b,face,c in loans if a<=day<b)
                refi += amount
                absent += amount == 0
                for a,b,face,c in cds:
                    if a<=day<b:
                        elapsed, term = (day-a).days, (b-a).days
                        cd_face += face
                        accrual += book(c,face,elapsed+1,term)-book(c,face,elapsed,term)
                        if day==end:
                            cd_end += book(c,face,elapsed+1,term)
            r = dict(month=after[:7],days=n,cd_face_daily_average_gelm=cd_face/n,
                     cd_effective_interest_gelm=accrual,cd_close_book_gelm=cd_end,
                     listed_refi_principal_daily_average_gelm=refi/n,
                     days_no_listed_refi_contract=absent,
                     refi_closing_principal_gelm=amount,
                     refi_reported_closing_stock_gelm=float(positions[after]['refinancing_gelm']))
            for data, fields in [(positions,['currency_circulation_gelm','fx_required_reserves_gelm','gel_bank_correspondent_gelm','one_month_operations_gelm','overnight_loans_gelm','government_deposits_gelm']),
                                 (reserve,['headline_usdm','fx_securities_usdm','deposits_usdm','gold_usdm'])]:
                for key in fields:
                    r['endpoint_mean_'+key]=(float(data[before][key])+float(data[after][key]))/2
            r.update(no_purchase_average_reserves_usdm=None,no_purchase_average_funding_gelm=None)
            rows.append(r)
    audit = next(r for r in read(R1+'cd_financing_reconciliation.csv') if r['year']=='2025')
    close(sum(r['cd_effective_interest_gelm'] for r in rows[:12]),float(audit['interest_accrued_gelm']))
    # Closing book values have a small unreconciled timing/basis difference.
    # Keep the difference visible instead of forcing the balance to agree.
    close(sum(c for a,b,face,c in cds if a.year==2025),float(audit['cash_issuance_gelm']))
    return rows


def reconciliations(months):
    """NBG–Treasury boundary eliminations and domestic CD reconciliation."""
    notes = {r['item']: r for r in read('research/r4_notes.csv')}
    eliminations = []
    for year in (2024, 2025):
        def value(item):
            return float(notes[item]['y'+str(year)])/1000
        close(value('cash_operations')+value('custody_settlement')+value('external_manager'),
              value('total_commission_expense'))
        for item, meaning in [
            ('government_interest','income at NBG and corresponding Treasury interest expense'),
            ('government_fvoci','domestic sovereign securities at NBG carrying value'),
            ('government_amortised','amortised-cost government securities at NBG'),
            ('government_deposits','Treasury deposit claim against NBG'),
            ('government_profit_payable','declared profit payable at year-end'),
            ('profit_payment','cash distributed to Treasury in year')]:
            eliminations.append(dict(year=year,item=item,amount_gelm=value(item),eliminate_as=meaning,
                                     internal_transfer_or_position=True))
    cds=contracts('cd_auctions_events','nominal_allocated_gel')
    audited=next(r for r in read(R1+'cd_financing_reconciliation.csv') if r['year']=='2025')
    redemptions=sum(face for a,b,face,c in cds if b.year==2025)
    pairs = [
        ('effective_interest',sum(r['cd_effective_interest_gelm'] for r in months[:12]),float(audited['interest_accrued_gelm'])),
        ('issue_cash',sum(c for a,b,f,c in cds if a.year==2025),float(audited['cash_issuance_gelm'])),
        ('redemptions_including_interest',redemptions,-float(audited['cash_redemption_gelm'])-float(audited['interest_paid_gelm'])),
        ('closing_book_end_of_day',months[11]['cd_close_book_gelm'],float(audited['closing_gelm']))]
    return eliminations,[dict(item=item,contract_gelm=a,audited_gelm=b,residual_gelm=a-b)
                         for item,a,b in pairs]


def scenarios():
    panel = next(r for r in read('reports/acquisition_2026_11_09/monthly_policy_panel.csv') if r['month']=='2025-12')
    spot=float(panel['official_usd_gel_end'])
    sofr=float(next(r['rate_pct'] for r in read(OLD+'sofr_daily.csv') if r['date']=='2025-12-31'))
    cd=float(max((r for r in read(OLD+'cd_auctions_events.csv') if r['date'].startswith('2025')),key=lambda r:r['date'])['weighted_rate_pct'])
    notes = {r['item']:r for r in read('research/r4_notes.csv')}
    rates = [('unremunerated GEL balances',0.),('GEL obligatory reserves',float(notes['gel_obligatory_pct']['y2025'])),
             ('rolling GEL CD',cd),('displaced GEL refinancing low',float(notes['refi_low_pct']['y2025'])),
             ('displaced GEL refinancing high',float(notes['refi_high_pct']['y2025']))]
    out=[]
    for mechanism, cost in rates:
        for fx in (-5,0,5):
            funding=spot*cost
            interest=spot*(1+fx/100)*sofr
            valuation=spot*fx
            out.append(dict(mechanism=mechanism,principal_usdm=100,initial_gel_per_usd=spot,
                            usd_return_proxy_pct=sofr,gel_cost_pct=cost,gel_per_usd_change_pct=fx,
                            asset_interest_gelm=interest,interest_or_opportunity_cost_gelm=funding,
                            principal_revaluation_gelm=valuation,
                            terminal_net_gelm=interest+valuation-funding,
                            breakeven_quote_change_pct=100*((1+cost/100)/(1+sofr/100)-1)))
    return out


def verify_pdf():
    manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
    pin=next(r for r in manifest if r['id']=='annual2025')
    pdf=ROOT/pin['local_path']
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=pin['sha256']:
        raise ValueError('annual report hash')
    pages={}
    for r in read('research/r4_notes.csv'):
        p=r['pdf_page']
        if p not in pages:
            pages[p]=' '.join(subprocess.check_output(['pdftotext','-layout','-f',p,'-l',p,str(pdf),'-'],stderr=subprocess.DEVNULL,text=True).split())
        if r['source_fragment'] not in pages[p]:
            raise ValueError(r['item']+' source fragment mismatch')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--verify-pdf',action='store_true')
    args=parser.parse_args()
    if args.verify_pdf:
        verify_pdf()
    months=monthly()
    eliminations, cd_bridge=reconciliations(months)
    outputs={'public_sector_eliminations.csv':csv_text(eliminations),'cd_reconciliation.csv':csv_text(cd_bridge),
             'annual_accounts.csv':csv_text(accounts()),'monthly_exposures.csv':csv_text(months),
             'conditional_carry.csv':csv_text(scenarios())}
    outputs['validation.json']=json.dumps(dict(inputs=INPUTS,sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in outputs.items()},incremental_episode_cost_gelm=None),indent=2,sort_keys=True)+'\n'
    for name,data in outputs.items():
        path=R4/name
        if args.check:
            if path.read_bytes()!=data.encode():
                raise ValueError(name+' differs')
        else:
            path.write_bytes(data.encode())


if __name__=='__main__':
    main()
