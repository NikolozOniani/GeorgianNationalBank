"""Step 3 historical reserve replays. Amounts in millions of the indicated currency."""
import argparse
import calendar
import csv
import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal as D

from historical_fx_cases import imf_transactions
from reserve_buffer_policy import CAL, OUT as POLICY, ROOT, read

OUT = ROOT / 'reports/minimum_reserve_buffer'
ORIGINS = ('2008-07-31', '2008-12-31', '2020-03-31')
WAR, CRISIS, COVID = ORIGINS
M = D(1000000)
ZERO = D(0)


@dataclass(frozen=True)
class Event:
    day: str
    label: str
    use: D  # Cash out positive, cash in negative.


def month_end(origin, months):
    d = date.fromisoformat(origin)
    y, m = divmod(d.year * 12 + d.month - 1 + months, 12)
    return date(y, m+1, calendar.monthrange(y,m+1)[1]).isoformat()


def group_events(origin, events):
    """Simultaneous uses bind jointly. A scenario must specify any within-day netting."""
    days = defaultdict(dict)
    for e in events:
        if e.day <= origin or e.label in days[e.day]:
            raise ValueError(f'Bad date or duplicate economic event: {e}')
        days[e.day][e.label] = e.use
    return [(d, ' + '.join(sorted(c for c,v in items.items() if v > 0)) or 'funding',
             sum(items.values())) for d,items in sorted(days.items())]


def replay(origin, events, months, floor):
    if floor < 0:
        raise ValueError('Negative floor')
    end = month_end(origin, months)
    path = [(origin, 'opening floor', ZERO)]
    path.extend(x for x in group_events(origin,events) if x[0] <= end)
    if path[-1][0] < end:
        path.append((end, 'horizon close', ZERO))
    running = ZERO
    peak = ZERO
    peak_day, bind = origin, 'opening floor'
    for d, label, use in path:
        running += use
        if running > peak:
            peak, peak_day, bind = running, d, label
    minimum = floor + peak
    balance = minimum
    # Halve the total opening balance. Identify actual cash failure separately from floor breach.
    smaller = minimum / 2
    first_floor = first_cash = first_bill = ''
    lowest = smaller
    detailed = []
    for d,label,use in path:
        balance -= use
        smaller -= use
        lowest = min(lowest, smaller)
        if smaller < floor and not first_floor:
            first_floor = d
        if smaller < 0 and not first_cash:
            first_cash,first_bill = d,label
        detailed.append(dict(date=d,group=label,net_use=use,balance_at_minimum=balance,balance_at_half=smaller))
    if min(r['balance_at_minimum'] for r in detailed) != floor or balance < floor:
        raise ArithmeticError('Forward cash simulation disagrees with prefix maximum')
    result = dict(floor=floor,minimum=minimum,first_binding_date=peak_day,binding_group=bind,
                  half_opening=minimum/2,first_floor_breach_at_half=first_floor,
                  first_cash_failure_at_half=first_cash,uncovered_group_at_half=first_bill,
                  max_cash_shortfall_at_half=max(0,-lowest),max_floor_shortfall_at_half=max(0,floor-lowest))
    return result,detailed


def serialize(name, rows, check):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, rows[0], lineterminator='\n')
    writer.writeheader()
    for r in rows:
        writer.writerow({k:format(v,'f') if isinstance(v,D) else v for k,v in r.items()})
    path = OUT/name
    if check:
        if path.read_bytes() != buf.getvalue().encode():
            raise ValueError(f'{name} differs')
    else:
        path.write_bytes(buf.getvalue().encode())


class Study:
    def __init__(self):
        self.results, self.paths, self.events, self.treasury = [], [], [], []
        self.mobilization = []
        self.assets = {r['date']: r for r in read(POLICY/'opening_assets.csv')}
        self.matrix = read(POLICY/'policy_matrix.csv')
        self.funds = {r['facility']:r for r in read(POLICY/'funding_cases.csv')}
        self.payments = read(CAL/'payments.csv')

    def add(self, name, origin, unit, events, horizons, coverage):
        if any(r['case']==name for r in self.results):
            raise ValueError('Duplicate scenario')
        for e in sorted(events,key=lambda x:(x.day,x.label)):
            self.events.append(dict(case=name,date=e.day,flow=e.label,net_use=e.use,unit=unit))
        for h in horizons:
            # The frozen 1% USD-equivalent floor is applied to dollar accounts only.
            floors = [ZERO] if unit != 'USDm' else [ZERO,D(self.assets[origin]['sensitivity_floor_usdm'])]
            for floor in floors:
                r,path = replay(origin,events,h,floor)
                self.results.append(dict(case=name,origin=origin,months=h,unit=unit,coverage=coverage,**r))
                if floor == 0:
                    for row in path:
                        self.paths.append(dict(case=name,months=h,**row))

    def imf_2009(self):
        tx = read(OUT/'imf_2009_full_year.csv')
        principal = [Event(r['date'],r['operation'],D(r['principal_paid_sdr'])/M) for r in tx if int(r['principal_paid_sdr'])]
        for mode in ('actual','no_new_rescue','no_receipts'):
            receipts = []
            for r in tx:
                if not int(r['disbursed_sdr']) or mode=='no_receipts':
                    continue
                n = D(r['disbursed_sdr'])
                if mode == 'no_new_rescue':
                    n = sum(D(f['no_new_rescue_gross_face']) for f in self.funds.values()
                            if f['origin']==CRISIS and f['receipt']==r['date'])
                if n:
                    receipts.append(Event(r['date'],r['operation'],-n/M))
            self.add('2009_principal_'+mode, CRISIS, 'SDRm', principal+receipts, (1,3,12), 'IMF member principal only')
        # USD-valued nominal IMF payments, plus alternative placement of all-market Q1 net sales.
        uses = [Event(r['transaction_date'] or r['nominal_due'],r['instrument'],D(r['usd_out'])/M)
                for r in self.payments if r['quarter']=='2009Q1' and D(r['usd_out'])]
        draw, = [r for r in self.payments if r['quarter']=='2009Q1' and D(r['usd_in'])]
        sale, = [D(r['amount']) for r in self.matrix if r['id']=='2009Q1 sales']
        auctions = [Event(r['date'],'auction '+r['auction_number'],
                          (D(r['sales_usd'])-D(r['purchases_usd']))/M)
                    for r in read(ROOT/'data/derived/r3_fx_response/auctions.csv')
                    if '2009-01' <= r['date'][:7] <= '2009-03']
        unallocated = sale - sum(e.use for e in auctions)
        for mode in ('actual_gross_face','no_new_rescue_gross_face'):
            accessible = sum(D(f[mode]) for f in self.funds.values() if f['receipt']==draw['transaction_date'])
            converted = accessible*D(draw['usd_in'])/D(draw['gross_in'])/M
            base = uses+auctions+[Event(draw['transaction_date'],'SBA at same-day valuation',-converted)]
            for label,day in [('early','2009-01-01'),('late','2009-03-31')]:
                self.add('2009_IMF_sales_'+mode+'_'+label,CRISIS,'USDm',
                         base+[Event(day,'Q1 sales outside auction ledger',unallocated)],(1,3),'pooled USD scenario; Q1 timing extreme')

    def private_2009(self):
        bills = [r for r in self.matrix if r['payer'] in ('Bank of Georgia','private Bank of Georgia')
                 and r['account']=='bank_support_candidate']
        for mode in ('self_funded','full_backstop'):
            events = [Event(month_end(r['date_or_interval']+'-01',0),r['description'],
                            D(r['amount']) if mode=='full_backstop' else ZERO) for r in bills]
            self.add('2009_named_bank_'+mode,CRISIS,'USDm',events,(1,3,12),
                     'two named private redemptions only; assumed eligibility and collateral')

    def currency_accounts_2020(self):
        rows = [r for r in self.payments if r['quarter']=='2020Q2' and D(r['gross_out'])]
        for ccy in ('USD','SDR'):
            uses = [Event(r['nominal_due'],r['instrument'],D(r['gross_out'])/M) for r in rows if r['currency']==ccy]
            self.add('2020_named_'+ccy,COVID,ccy+'m',uses,(1,3),
                     'nominal dates; separate currencies, zero external offsets')

    def sales_2020(self):
        sales = {r['date_or_interval']:D(r['amount']) for r in self.matrix
                 if r['account']=='sales_replay' and '2020-04' <= r['date_or_interval'] <= '2020-12'}
        for r in read(ROOT/'data/derived/r3_fx_response/monthly.csv'):
            if '2021-01' <= r['month'] <= '2021-03':
                sales[r['month']] = -D(r['net_usdm'])
        if set(sales) != {month_end(COVID,i)[:7] for i in range(1,13)}:
            raise ValueError('Incomplete sales coverage')
        return [Event(month_end(COVID,i),'monthly net sales',sales[month_end(COVID,i)[:7]]) for i in range(1,13)]

    def schedule_2020(self,sales):
        rows = [r for r in read(POLICY/'scheduled_calls.csv') if r['date']==COVID]
        previous = ZERO
        schedule = []
        for r in sorted(rows,key=lambda r:int(r['months'])):
            h = int(r['months'])
            cumulative = -D(r['II1_signed'])
            if cumulative < previous:
                raise ValueError('Mixed-sign schedule needs within-bucket flow detail')
            schedule.append(Event(month_end(COVID,h),'section II.1 bucket',cumulative-previous))
            previous = cumulative
        if len(schedule)!=3:
            raise ValueError('Incomplete maturity schedule')
        self.add('2020_sales',COVID,'USDm',sales,(1,3,12),'monthly net sales budget')
        self.add('2020_schedule',COVID,'USDm',schedule,(1,3,12),'maturity buckets; zero receipts')
        self.add('2020_schedule_sales',COVID,'USDm',schedule+sales,(1,3,12),'disjoint scheduled drains and net sales')

        early = [Event(d,e.label,e.use) for d,e in zip(('2020-04-01','2020-05-01','2020-07-01'),schedule)]
        self.add('2020_schedule_sales_early_dues',COVID,'USDm',early+sales,(1,3,12),
                 'same schedule; dues at bucket starts, sales at month ends')
        asset = self.assets[COVID]
        deposits, securities = D(asset['deposits_only_conditional']),D(asset['securities'])
        for h in (1,3,12):
            for floor in [ZERO,D(asset['sensitivity_floor_usdm'])]:
                summary,_ = replay(COVID,schedule+sales,h,floor)
                need = summary['minimum']
                proceeds = max(ZERO,need-deposits)
                # A scenario for cash required before security-sale proceeds settle.
                # The April dated auction is after the assumed two-business-day delay.
                # Allow all unallocated April net sales and first-bucket public uses to come first.
                april_auctions = [r for r in read(ROOT/'data/derived/r3_fx_response/auctions.csv')
                                  if r['date'].startswith('2020-04')]
                if any(r['date'] <= '2020-04-03' or D(r['purchases_usd']) for r in april_auctions):
                    raise ValueError('Review early April auction timing')
                residual_sales = sales[0].use - sum(D(r['sales_usd'])/M for r in april_auctions)
                if residual_sales < 0:
                    raise ValueError('Unallocated flow is not a sales budget')
                late_need = max(floor,need-D('.95')*securities)
                early_need = max(late_need,floor+schedule[0].use+residual_sales)
                cash = deposits
                first_breach = ''
                for d, _, use in group_events(COVID, schedule+sales):
                    if d > month_end(COVID,h):
                        break
                    cash -= use
                    if cash < floor and not first_breach:
                        first_breach = d
                self.mobilization.append(dict(months=h, floor=floor, total_liquid_need=need,
                       first_deposits_only_floor_breach_bucket_end=first_breach,
                       conditional_deposits=deposits, min_security_proceeds=proceeds,
                       market_value_to_sell_no_discount=proceeds, market_value_to_sell_5pct_discount=proceeds/D('.95'),
                       opening_securities=securities, deposit_need_if_all_dues_after_settlement=late_need,
                       deposit_need_if_first_bucket_and_residual_sales_before_settlement=early_need))

    def fiscal_2020(self,sales):
        # External Treasury cash is ring-fenced. Only its uncovered bills enter NBG cash uses.
        pub = {r['payer']:D(r['amount']) for r in self.matrix if r['account']=='public_aggregate_alternative'
               and r['date_or_interval']=='2020Q2'}
        coupon, = [r for r in self.payments if r['instrument']=='2021 Eurobond interest']
        bill = D(coupon['gross_out'])/M
        imf, = [r for r in self.payments if r['quarter']=='2020Q2' and D(r['usd_in'])]
        wb = self.funds['World Bank EMC original DPO']
        fx, = [r for r in read(ROOT/'data/derived/episode_2026_11_09/official_fx_daily.csv') if r['date']==wb['receipt']]
        # Round the illustrative converted amount to the nearest dollar.
        wb_usdm = (D(wb['actual_gross_face'])*D(fx['eur_gel'])/D(fx['usd_gel'])).quantize(D(1))/M
        for mode in ('actual','no_new_rescue','inaccessible'):
            for timing,day in [('early','2020-04-01'),('late','2020-06-30')]:
                name=f'2020_fiscal_{mode}_{timing}'
                bills = {day:('other government service',pub['government']-bill),
                         coupon['nominal_due']:('bond coupon',bill)}
                receipts = {}
                if mode != 'inaccessible':
                    receipts[wb['receipt']] = wb_usdm
                if mode == 'actual':
                    receipts[imf['transaction_date']] = D(imf['usd_in'])/M
                events = [Event(day,'NBG debt service',pub['NBG'])]
                balance = ZERO
                for d in sorted(bills.keys()|receipts.keys()):
                    label,due = bills.get(d,('funding arrives',ZERO))
                    credit = receipts.get(d,ZERO)
                    opening = balance
                    balance += credit
                    own = min(due,balance)
                    balance -= own
                    if due:
                        events.append(Event(d,label,due-own))
                    self.treasury.append(dict(case=name,date=d,description=label,opening=opening,receipt=credit,
                                              gross_bill=due,externally_paid=own,nbg_backstop=due-own,closing=balance))
                self.add(name,COVID,'USDm',events,(1,3),'Q2 debtor totals; Treasury external-account scenario')
                self.add(name+'_sales',COVID,'USDm',events+sales[:3],(1,3),'Q2 fiscal plus disjoint sales')

    def war_2008(self):
        sale, = [r for r in self.matrix if r['id']=='August FX sales']
        self.add('2008_August_sales',WAR,'USDm',[Event('2008-08-31','August sales budget',D(sale['amount']))],
                 (1,), 'August only; monthly budget')

    def fiscal_2009(self):
        fiscal = [r for r in self.matrix if r['date_or_interval']=='2009Q1' and r['account']=='public_aggregate_alternative']
        receipt, = [r for r in read(CAL/'quarter_inputs.csv') if r['quarter']=='2009Q1' and r['item']=='external borrowing']
        for timing, first, last in [('receipt_first','2009-01-01','2009-03-31'),
                                    ('bills_first','2009-03-31','2009-01-01')]:
            events = [Event(last,r['description'],D(r['amount'])) for r in fiscal]
            events.append(Event(first,'external borrowing reported in GEL',-D(receipt['amount'])))
            self.add('2009_fiscal_'+timing, CRISIS,'GELm',events,(1,3),
                     'fiscal reporting units; currencies unverified, no NBG dollar conversion')

    def build(self):
        self.war_2008()
        self.imf_2009()
        self.fiscal_2009()
        self.private_2009()
        self.currency_accounts_2020()
        sales = self.sales_2020()
        self.schedule_2020(sales)
        self.fiscal_2020(sales)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--from-raw',action='store_true')
    args = parser.parse_args()
    if args.from_raw:
        raw = imf_transactions(False, periods={(2009,m) for m in range(1,13)})
        serialize('imf_2009_full_year.csv',raw,args.check)
    s = Study()
    s.build()
    for name, rows in [('minimums',s.results),('forward_paths',s.paths),('scenario_events',s.events),('treasury_cash',s.treasury),('security_mobilization',s.mobilization)]:
        serialize(name+'.csv',rows,args.check)


if __name__=='__main__':
    main()
