"""Extract historical intervention and valid-date official quotes from three pinned NBG files."""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/derived/r3_fx_response'


def csv_bytes(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def extract(acquire=False):
    manifest = {r['id']: r for r in json.loads((ROOT/'data/source_manifest.json').read_text())}

    def workbook(key):
        record = manifest[key]
        file = ROOT/record['local_path']
        if acquire and not file.exists():
            from acquire_episode import fetch
            file.parent.mkdir(parents=True,exist_ok=True)
            result = fetch(record,previous=record)
            if result['status']!='acquired':
                raise ValueError(result['error'])
        if hashlib.sha256(file.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Changed workbook '+key)
        return load_workbook(file,read_only=True,data_only=True)

    fx = workbook('fx_daily_history')['2001-2025']
    rows = iter(fx.values)
    header = [next(rows) for _ in range(6)]
    usd = header[-1].index('USD')
    if header[-2][usd] != 1:
        raise ValueError('Expected quotes for one USD')
    daily = []
    for i,row in enumerate(rows,7):
        if isinstance(row[0],dt.datetime) and 2008 <= row[0].year <= 2024:
            if not isinstance(row[usd], (int, float)) or row[usd] <= 0:
                raise ValueError(f'Invalid USD quote at row {i}')
            daily.append(dict(date=row[0].date(),gel_usd=row[usd],source_row=i))
    w = workbook('fx_auctions')
    auctions = []
    for i,(number,date,sale,buy,*_) in enumerate(w['NBG FX auction-eng'].values,1):
        if isinstance(date,dt.datetime) and date.year<=2024:
            if min(buy, sale) < 0 or buy * sale != 0:
                raise ValueError(f'Invalid auction legs at row {i}')
            auctions.append(dict(date=date.date(),auction_number=number,purchases_usd=buy,
                                 sales_usd=sale,source_row=i))
    options = []
    for i,(date,announced,sold,exercised) in enumerate(w['Option-eng'].values,1):
        if isinstance(date,dt.datetime):
            options.append(dict(auction_date=date.date(),announced_gel=announced,sold_gel=sold,
                                exercised_gel=exercised,source_row=i))
    w = workbook('fx_market')
    def months(sheet):
        result = {}
        for i,row in enumerate(w[sheet].values,1):
            if isinstance(row[0],dt.datetime):
                key = row[0].strftime('%Y-%m')
                if key in result:
                    raise ValueError(f'Duplicate month {key} in {sheet}')
                result[key] = i,row
        return result
    buy,sell = months('USD_Buy-eng '),months('USD_Sell-eng ')
    if buy.keys() != sell.keys():
        raise ValueError('Monthly workbook legs have different dates')
    monthly = []
    for key in sorted(buy):
        if key[:4]>'2024':
            continue
        bi,b = buy[key]
        si,s = sell[key]
        if not all(isinstance(z, (int, float)) for z in [s[2], s[3], s[4], b[2], b[3]]):
            raise ValueError(f'Missing or nonnumeric transaction leg in {key}')
        monthly.append(dict(month=key,net_usdm=s[3]-b[2]-b[3],auction_buy_usdm=s[3],
                            auction_sell_usdm=b[2],nonauction_net_usdm=-b[3],options_usdm=s[2],
                            swaps_usdm=s[4],buy_row=bi,sell_row=si))
    return dict(daily=daily,auctions=auctions,options=options,monthly=monthly)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--acquire',action='store_true')
    args = parser.parse_args()
    for key,rows in extract(args.acquire).items():
        path = DATA/(key+'.csv')
        if args.check:
            if path.read_bytes() != csv_bytes(rows):
                raise ValueError(f'Extract differs from pinned workbook: {key}')
        else:
            path.write_bytes(csv_bytes(rows))
