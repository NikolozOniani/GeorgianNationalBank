"""Rebuild the two historical public payment calendars and their restricted cash accounts."""
import argparse
import csv
import io
import json
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from lxml import html
from openpyxl import load_workbook

from historical_fx_cases import CASES, imf_transactions, read, source_bytes

OUT = CASES.parent / 'payment_calendar'
D = Decimal
QUARTERS = ('2009Q1', '2020Q2')


def quarter(day):
    return f'{day.year}Q{(day.month - 1) // 3 + 1}'


def html_rows(raw):
    for tr in html.fromstring(raw).xpath('//tr'):
        yield [' '.join(x.text_content().split()) for x in tr.xpath('./th|./td')]


def source_extracts(acquire):
    locks = json.loads((OUT / 'source_locks.json').read_text())
    raw = {r['id']: source_bytes(r, acquire) for r in locks}
    schedules = []
    for key, vintage, label in [('2009', '2008-12-31', 'obligations'),
                                ('2020_exp', '2020-03-31', 'expectations')]:
        for cells in html_rows(raw[key]):
            if len(cells) != (4 if key == '2009' else 3):
                continue
            try:
                day = datetime.strptime(cells[-2], '%B %d, %Y').date()
            except ValueError:
                continue
            if quarter(day) in QUARTERS:
                schedules.append(dict(date=day.isoformat(), operation=cells[0], amount_sdr=cells[-1].replace(',', ''),
                                      vintage=vintage, basis=label))
    if len(schedules) != 8:
        raise ValueError('Changed IMF schedule coverage')
    rates = []
    for key, data in raw.items():
        if not key.startswith('rate_'):
            continue
        dates = []
        for cells in html_rows(data):
            if cells and cells[0] == 'Currency':
                dates = [datetime.strptime(x.replace(' ', ''), '%B%d,%Y').date() for x in cells[1:]]
            if cells and cells[0] == 'U.S. dollar':
                if len(dates) != len(cells) - 1:
                    raise ValueError('Incomplete IMF currency table')
                for day, rate in zip(dates, cells[1:]):
                    if rate and rate != 'NA':
                        rates.append(dict(date=day.isoformat(), usd_per_sdr=str(D(rate))))
    book = load_workbook(io.BytesIO(raw['template']), read_only=True, data_only=True)
    try:
        rows = list(book['template 03.20'].values)
    finally:
        book.close()
    if (rows[9][2], rows[9][4], rows[19][3]) != ('US Dollars', 'Millions', 'March 31, 2020'):
        raise ValueError('Liquidity template unit or period changed')
    exposures = []
    for number, column, horizon, name in [
        (21, 3, 'stock', 'gross reserves'), (23, 3, 'stock', 'FX securities'),
        (25, 3, 'stock', 'FX currency and deposits'), (32, 3, 'stock', 'SDR holdings'),
        (55, 4, '0-1m', 'principal'), (56, 4, '0-1m', 'interest'),
        (55, 5, '1-3m', 'principal'), (56, 5, '1-3m', 'interest'),
        (79, 3, '0-1m', 'other contingent liabilities')]:
        exposures.append(dict(as_of='2020-03-31', item=name, horizon=horizon,
                              source_row=number, source_column=chr(65 + column),
                              usd_million=f'{rows[number-1][column]:.9f}'))
    return {'imf_schedules.csv': schedules, 'sdr_rates.csv': sorted(rates, key=lambda r: r['date']),
            'opening_template.csv': exposures}


def payment_events(schedules, rates, actual):
    quotes = {r['date']: D(r['usd_per_sdr']) for r in rates}
    if len(quotes) != len(rates):
        raise ValueError('Duplicate FX date')
    events = []

    def event(due, paid, sector, instrument, status, ccy, outflow, inflow):
        day = paid or due
        quote_date = ''
        rate = D(1)
        if ccy == 'SDR':
            quote_date = max(k for k in quotes if k <= day)
            if (date.fromisoformat(day) - date.fromisoformat(quote_date)).days > 5:
                raise ValueError('Stale SDR quote')
            rate = quotes[quote_date]
        events.append(dict(quarter=quarter(date.fromisoformat(day)), nominal_due=due, transaction_date=paid,
                           payer_or_recipient=sector, instrument=instrument, evidence=status, currency=ccy,
                           gross_out=outflow, gross_in=inflow, sdr_quote_date=quote_date,
                           usd_out=format(D(outflow)*rate, '.2f'), usd_in=format(D(inflow)*rate, '.2f')))

    projected = {(r['date'], r['operation']): r for r in schedules}
    if len(projected) != len(schedules):
        raise ValueError('Duplicate scheduled operation')
    for r in actual:
        day = r['date']
        if quarter(date.fromisoformat(day)) not in QUARTERS:
            continue
        sector = 'IMF member account' if day.startswith('2009') else 'government budget'
        paid, received = int(r['principal_paid_sdr']), int(r['disbursed_sdr'])
        if paid:
            p = projected.pop((day, r['operation']))
            if paid != int(p['amount_sdr']):
                raise ValueError('IMF principal disagrees with schedule')
        event(day if paid else '', day, sector, r['operation'], 'IMF transaction', 'SDR', paid, received)
    for (day, op), r in projected.items():
        event(day, '', 'IMF member account', op, 'IMF projection', 'SDR', int(r['amount_sdr']), 0)
    coupon = D(500000000) * D('0.06875') / 2
    event('2020-04-12', '', 'Georgia Ministry of Finance', '2021 Eurobond interest',
          'contract date; quarter paid', 'USD', coupon, 0)
    return sorted(events, key=lambda r: (r['transaction_date'] or r['nominal_due'], r['instrument']))


def peaks(events):
    results = []
    for q in QUARTERS:
        for scope in ('IMF dated transactions', 'IMF plus scheduled obligations and bond'):
            daily = defaultdict(Decimal)
            for r in events:
                if r['quarter'] != q or (scope == 'IMF dated transactions' and not r['transaction_date']):
                    continue
                day = r['transaction_date'] or r['nominal_due']
                daily[day] += D(r['usd_out']) - D(r['usd_in'])
            used = peak = D(0)
            peak_day = ''
            for day, use in sorted(daily.items()):
                used += use
                if used > peak:
                    peak, peak_day = used, day
            results.append(dict(quarter=q, scope=scope, peak_usd=f'{peak:.2f}', first_peak_date=peak_day))
    return results


def reconciliations(template, fiscal):
    monthly = read(CASES/'monthly.csv')
    quarters = {r['quarter']: r for r in read(CASES/'quarterly.csv')}
    official = read(CASES/'document_ledger.csv')
    sales_2009 = next(D(r['usd_million']) for r in official
                      if r['period'] == '2009Q1' and r['measure'] == 'net FX sales')
    results = []
    for q in QUARTERS:
        rows = [r for r in monthly if quarter(date.fromisoformat(r['month'] + '-01')) == q]
        opening = D(rows[0]['reserves_usdm']) - D(rows[0]['reserve_change_usdm'])
        closing = D(rows[-1]['reserves_usdm'])
        sales = sales_2009 if q == '2009Q1' else sum(D(r['all_market_net_sales_usdm']) for r in rows)
        reserve_tx = D(quarters[q]['reserve_transactions_usdm'])
        results.append(dict(quarter=q, opening_gross_usdm=opening, closing_gross_usdm=closing,
                            sales_usdm=sales, bop_reserve_transactions_usdm=reserve_tx,
                            other_net_transactions_usdm=reserve_tx + sales,
                            valuation_other_and_vintage_usdm=closing-opening-reserve_tx))
    drains = -sum(D(r['usd_million']) for r in template if r['item'] in ('principal', 'interest'))
    public = {r['item']: D(r['amount']) for r in fiscal if r['quarter'] == '2020Q2'}
    service = public['external principal paid'] + public['external interest paid']
    comparison = dict(quarter='2020Q2', perimeter='external public debt service',
                      principal_plus_interest_usdm=service,
                      government_plus_nbg_service_usdm=public['external service including guaranteed'] + public['external service'],
                      government_gross_drawings_usdm=public['gross external drawings'],
                      nbg_opening_3m_scheduled_loan_security_deposit_outflows_usdm=drains,
                      schedule_minus_outturn_different_perimeters_usdm=drains - service)
    return results, [comparison]


def emit(name, rows, check):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    path = OUT / name
    if check:
        if path.read_bytes() != stream.getvalue().encode():
            raise ValueError('Output differs: ' + name)
    else:
        path.write_bytes(stream.getvalue().encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-raw', action='store_true')
    parser.add_argument('--acquire', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.from_raw or args.acquire:
        for name, records in source_extracts(args.acquire).items():
            emit(name, records, args.check)
    actual = read(CASES/'imf_cash.csv')
    if args.from_raw or args.acquire:
        original = [{k: str(v) for k, v in r.items()} for r in imf_transactions(args.acquire)]
        if original != actual:
            raise ValueError('IMF transaction extract differs from locked originals')
    events = payment_events(read(OUT/'imf_schedules.csv'), read(OUT/'sdr_rates.csv'), actual)
    emit('payments.csv', events, args.check)
    emit('restricted_peaks.csv', peaks(events), args.check)
    bridges, comparison = reconciliations(read(OUT/'opening_template.csv'), read(OUT/'quarter_inputs.csv'))
    emit('reserve_bridge.csv', bridges, args.check)
    emit('service_comparison.csv', comparison, args.check)


if __name__ == '__main__':
    main()
