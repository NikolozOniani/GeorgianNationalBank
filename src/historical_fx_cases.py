"""Historical cash and financing ledgers, 2009H1 and 2020. Run from any directory."""
import argparse
import csv
import hashlib
import io
import json
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta

from lxml import html
from historical_fx_shocks import ROOT, OUT, end, observations, table

CASES = OUT / 'cases'
PERIODS = [(2009, m) for m in range(1,7)] + [(2020, m) for m in range(1,13)]


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def source_bytes(lock, acquire):
    path = ROOT/lock['path']
    if not path.exists() and acquire:
        with urllib.request.urlopen(lock['url'], timeout=30) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != lock['sha256']:
            raise ValueError('Provider vintage changed; retain the locked extract')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != lock['sha256']:
        raise ValueError(f'Changed source: {path}')
    return raw


def imf_transactions(acquire, periods=PERIODS):
    records = []
    for lock in json.loads((CASES/'imf_sources.json').read_text()):
        raw = source_bytes(lock, acquire)
        doc = html.fromstring(raw)
        if '(in SDRs)' not in doc.text_content():
            raise ValueError('IMF currency field changed')
        totals = [0]*6
        stated = None
        for tr in doc.xpath('//tr'):
            cells = [' '.join(c.text_content().split()) for c in tr.xpath('./th|./td')]
            if len(cells) != 8:
                continue
            if cells[0] == 'Total':
                stated = [int(v.replace(',','')) for v in cells[1:7]]
                continue
            try:
                value_date = datetime.strptime(cells[0], '%B %d, %Y').date()
            except ValueError:
                continue
            amounts = [int(v.replace(',','')) for v in cells[1:7]]
            totals = [a+b for a,b in zip(totals, amounts)]
            if value_date.year != lock['year']:
                raise ValueError('Wrong IMF table year')
            if (value_date.year,value_date.month) in periods:
                records.append(dict(date=value_date.isoformat(), operation=cells[-1],
                                 disbursed_sdr=sum(amounts[::2]), principal_paid_sdr=sum(amounts[1::2])))
        if stated != totals:
            raise ValueError('IMF transactions disagree with published annual totals')
    return records


def ledgers(fund):
    deposits = observations(table('money_aggregates','Monetary Ratios-eng'),9)
    reserves = observations(table('reserve_assets','GIR (eng) '),1,1000)
    quotes = {date.fromisoformat(r['date']):float(r['gel_usd']) for r in read(ROOT/'data/derived/r3_fx_response/daily.csv')}
    flows = {r['month']:float(r['net_usdm']) for r in read(ROOT/'data/derived/r3_fx_response/monthly.csv')}
    auctions = defaultdict(float)
    for r in read(ROOT/'data/derived/r3_fx_response/auctions.csv'):
        auctions[r['date'][:7]] += (float(r['sales_usd'])-float(r['purchases_usd']))/1e6
    monthly = []
    for year,m in PERIODS:
        d = end(year,m)
        p = date(year,m,1)-timedelta(days=1)
        key = d.strftime('%Y-%m')
        tx = [r for r in fund if r['date'][:7]==key]
        monthly.append(dict(month=key, reserves_usdm=reserves[d], reserve_change_usdm=reserves[d]-reserves[p],
            fx_deposits_usdm=deposits[d]/quotes[d], deposit_change_usdm=deposits[d]/quotes[d]-deposits[p]/quotes[p],
            gel_per_usd=quotes[d], dated_auction_net_sales_usdm=auctions[key] if key>='2009-03' else None,
            all_market_net_sales_usdm=-flows[key] if key in flows else None,
            imf_principal_paid_sdr=sum(r['principal_paid_sdr'] for r in tx),
            imf_drawn_sdr=sum(r['disbursed_sdr'] for r in tx)))
    b = table('bop_bpm6','BOP–BPM6')
    a = table('bop_bpm6','BOP-anlt')
    bc = {str(v).strip():i for i,v in enumerate(b[2])}
    ac = {str(v).strip():i for i,v in enumerate(a[2])}
    quarterly = []
    for year,m in PERIODS:
        if m%3:
            continue
        key = f'{year}Q{m//3}'
        j = bc[key]
        prev = bc[f'{year-1}Q{m//3}']
        i = ac[key]
        selected = [r for r in monthly if r['month'][:4]==str(year) and m-2<=int(r['month'][5:])<=m]
        def change(row):
            return b[row-1][j]-b[row-1][prev]
        change_res = sum(r['reserve_change_usdm'] for r in selected)
        reserve_tx, imf, exceptional = (a[n-1][i] for n in (53,54,55))
        if abs(a[50][i]+reserve_tx-imf-exceptional)>1e-6 or abs(reserve_tx-b[836][j])>1e-6:
            raise ValueError('Analytical BOP bridge failed '+key)
        if abs(b[714][j]-b[715][j]-b[716][j])>1e-6 or abs(imf-b[711][j]-b[718][j])>1e-6:
            raise ValueError('Sector decomposition failed '+key)
        quarterly.append(dict(quarter=key,exports_yoy_change_usdm=change(8),imports_yoy_change_usdm=change(9),
            travel_credit_yoy_change_usdm=change(146),trade_balance_yoy_change_usdm=change(8)-change(9),
            banks_net_short_loan_incurrence_usdm=b[715][j],banks_net_long_loan_incurrence_usdm=b[716][j],
            govt_net_loan_incurrence_usdm=b[717][j],govt_imf_net_usdm=b[718][j],central_bank_imf_net_usdm=b[711][j],
            overall_balance_usdm=a[50][i],imf_net_usdm=imf,exceptional_financing_usdm=exceptional,
            reserve_transactions_usdm=reserve_tx,reserve_stock_change_usdm=change_res,other_stock_change_usdm=change_res-reserve_tx))
    return {'imf_cash.csv':fund,'monthly.csv':monthly,'quarterly.csv':quarterly}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--acquire',action='store_true',help='Fetch missing IMF source pages using strict byte locks')
    args=parser.parse_args()
    for lock in json.loads((CASES/'pdf_sources.json').read_text()):
        source_bytes(lock, args.acquire)
    for name,rows in ledgers(imf_transactions(args.acquire)).items():
        f=io.StringIO()
        writer=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({k:f'{v:.6f}' if isinstance(v,float) else v for k,v in row.items()})
        data=f.getvalue().encode()
        if args.check:
            if (CASES/name).read_bytes()!=data:
                raise ValueError(f'Changed output {name}')
        else:
            (CASES/name).write_bytes(data)


if __name__=='__main__':
    main()
