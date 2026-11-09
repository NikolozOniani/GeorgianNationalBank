"""Extract pinned official observations. No interpolation or causal estimation.

All source coordinates are Excel coordinates; monetary conversions are explicit.
Blank source cells stay missing. Rows are retained at their native frequency.
"""
from __future__ import annotations
import calendar
import argparse
import csv
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import tempfile
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/derived/episode_2026_11_09'
FINAL = OUT
CUTOFF = dt.date(2026, 11, 9)
START = dt.date(2020, 1, 1)
SOURCES = {}
CATALOGUE = []
ISSUES = []


def number(x):
    return isinstance(x, (float, int)) and not isinstance(x, bool)


def date(x):
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    return None


def within(x, start=START):
    return date(x) is not None and start <= date(x) <= CUTOFF


def num(x, factor=1):
    return x * factor if number(x) else None


def clean(x):
    if isinstance(x, (dt.date, dt.datetime)):
        return date(x).isoformat()
    return x


def source_path(identifier):
    row = SOURCES[identifier]
    assert row['status'] == 'acquired', identifier
    p = ROOT / row['local_path']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], identifier
    return p


def workbook(identifier):
    return openpyxl.load_workbook(source_path(identifier), read_only=True, data_only=True)


def save(name, rows, frequency, units, definition, sources, date_field='date'):
    assert rows, name
    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    assert all(set(r) == set(fields) for r in rows), name
    path = OUT / (name + '.csv')
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows([{k: clean(v) for k,v in r.items()} for r in rows])
    dates = [str(clean(r[date_field])) for r in rows if r.get(date_field)]
    CATALOGUE.append(dict(file=str((FINAL/path.name).relative_to(ROOT)), rows=len(rows), frequency=frequency,
                          units=units, definition=definition, source_ids=sources,
                          first=min(dates) if dates else None, last=max(dates) if dates else None,
                          missing_cells={k:sum(r[k] is None or r[k]=='' for r in rows) for k in fields},
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return rows


def intervention():
    w = workbook('fx_market')
    buy, sell = w['USD_Buy-eng '], w['USD_Sell-eng ']
    sells = {date(r[0]).strftime('%Y-%m'):(i,r) for i,r in enumerate(sell.values,1) if within(r[0])}
    rows, market = [], []
    for i,r in enumerate(buy.values,1):
        if not within(r[0]): continue
        month=date(r[0]).strftime('%Y-%m'); j,s=sells[month]
        assert all(number(v) for v in [r[2],r[3],s[2],s[3],s[4]]), month
        net=-r[3]+s[3]-r[2]
        rows.append(dict(month=month,auction_purchases_usdm=s[3],auction_sales_usdm=r[2],
                         nonauction_net_purchases_usdm=-r[3],net_market_purchases_usdm=net,
                         nonauction_gross_purchases_usdm=None,nonauction_gross_sales_usdm=None,
                         options_exercised_usdm=s[2],nbg_swap_usdm=s[4],
                         source_id='fx_market',buy_row=i,sell_row=j,
                         source_buy_period_date=date(r[0]),source_sell_period_date=date(s[0])))
        # Totals are the source's reported bank transactions, not a clean market turnover measure.
        for side, rr, ii, last in [('bank_buy',r,i,8),('bank_sell',s,j,9)]:
            residual=rr[1]-sum(rr[2:last]) if all(number(v) for v in rr[1:last]) else None
            market.append(dict(month=month,bank_side=side,total_usdm=num(rr[1]),
                               local_banks_usdm=num(rr[4] if side=='bank_buy' else rr[5]),
                               foreign_banks_usdm=num(rr[5] if side=='bank_buy' else rr[6]),
                               legal_entities_usdm=num(rr[6] if side=='bank_buy' else rr[7]),
                               individuals_usdm=num(rr[7] if side=='bank_buy' else rr[8]),
                               total_minus_reported_components_usdm=residual,
                               source_id='fx_market',sheet=buy.title if side=='bank_buy' else sell.title,source_row=ii))
            if residual is not None and abs(residual)>0.00001:
                ISSUES.append(dict(source_id='fx_market',location=f'{side} {month} row {ii}',
                                   issue='Reported total differs from sum of reported components',
                                   residual=residual,action='Retain both; do not silently repair or use total as validated turnover'))
    save('intervention_monthly',rows,'monthly','USD million; NBG purchase positive',
         'Non-auction is NET, not gross BMatch purchases; auction columns are gross. Options/swaps separate. Source cells buy C,D; sell C,D,E.', ['fx_market'],'month')
    save('fx_market_monthly',market,'monthly','USD million','Reported bank FX transactions and accounting discrepancies; no intraday prices/order flow.', ['fx_market'],'month')
    w.close()
    w=workbook('fx_auctions');s=w.worksheets[0];events=[]
    for i,r in enumerate(s.values,1):
        if within(r[1]):
            events.append(dict(date=date(r[1]),auction_number=r[0],sales_usd=num(r[2]),purchases_usd=num(r[3]),
                               execution_price=None,source_id='fx_auctions',sheet=s.title,source_row=i))
    save('fx_auction_events',events,'auction event','USD, not millions','Dated auction transactions; no invented execution prices or zero-event dates.', ['fx_auctions'])
    w.close()


def exchange_rates():
    rows=[]; mapping=[]
    wanted=['USD','EUR','TRY','RUB','AMD','AZN','CNY','PLN','UAH']
    for identifier in ['fx_daily_history','fx_daily_current']:
        w=workbook(identifier)
        sheets=[w[str(y)] for y in range(2020,2026)] if identifier=='fx_daily_history' else [w['E']]
        for s in sheets:
            data=list(s.values)
            header=next(i for i,r in enumerate(data[:10]) if 'USD' in r and 'EUR' in r)
            cols={c:data[header].index(c) for c in wanted if c in data[header]}
            assert len(cols)==len(wanted), (identifier,s.title)
            denom={c:data[header-1][j] for c,j in cols.items()}
            assert all(number(x) and x>0 for x in denom.values())
            for c,j in cols.items():
                mapping.append(dict(source_id=identifier,sheet=s.title,currency=c,column=openpyxl.utils.get_column_letter(j+1),
                                    quoted_units=denom[c],converted_units='GEL per one foreign currency unit'))
            for i,r in enumerate(data,1):
                if not within(r[0]): continue
                # The sheet named 2024 also contains 2023 and early 2025.
                # Select the explicitly named year; never deduplicate contradictory dates silently.
                if identifier=='fx_daily_history' and date(r[0]).year != int(s.title):continue
                row=dict(date=date(r[0]))
                row.update({c.lower()+'_gel':num(r[j],1/denom[c]) for c,j in cols.items()})
                row.update(source_id=identifier,sheet=s.title,source_row=i)
                rows.append(row)
        w.close()
    rows.sort(key=lambda r:r['date'])
    assert len({r['date'] for r in rows})==len(rows)
    save('official_fx_daily',rows,'source calendar-valid daily observations','GEL per one unit of foreign currency',
         'Official valid-date rates, not intraday quotes or independent weekend trades. No forward fill performed.', ['fx_daily_history','fx_daily_current'])
    save('fx_quote_conventions',mapping,'per source sheet','original denomination','Verified currency-header and denomination cells; divide quoted value by quoted_units.', ['fx_daily_history','fx_daily_current'],None)
    for identifier,sheet,base,freq in [('neer_daily','NEER_Eng','December 2005=100','daily'),
                                     ('neer_monthly','Monthly NExR (ENG)','December 1995=100','monthly'),
                                     ('reer_monthly','Monthly REER (ENG)','December 1995=100','monthly')]:
        w=workbook(identifier);s=w[sheet];rr=[]
        for i,r in enumerate(s.values,1):
            if within(r[0]):
                rr.append(dict(date=date(r[0]),index=num(r[1]),base=base,source_id=identifier,sheet=s.title,source_cell=f'B{i}'))
        save(identifier,rr,freq,'index '+base,'Published effective exchange rate level. Distinct daily/monthly bases; not spliced.', [identifier]);w.close()


def liquidity():
    w=workbook('tibr');s=w.worksheets[0];rr=[]
    for i,r in enumerate(s.values,1):
        if within(r[0]):
            rr.append(dict(date=date(r[0]),tibr_pct=num(r[1],100),volume_gel=num(r[2]),
                           tibr_1m_pct=num(r[3],100),tibr_3m_pct=num(r[4],100),tibr_6m_pct=num(r[5],100),
                           source_id='tibr',source_row=i))
    save('tibr_daily',rr,'business daily','annualized percent; GEL volume','Source decimal rates multiplied by 100; term indices are published TIBR indices.', ['tibr']);w.close()
    for identifier in ['refinancing','cd_auctions','repo']:
        w=workbook(identifier);s=w.worksheets[0];rr=[]
        for i,r in enumerate(s.values,1):
            col={'refinancing':0,'cd_auctions':2,'repo':1}[identifier]
            if not within(r[col]):continue
            row=dict(date=date(r[col]))
            if identifier=='refinancing':
                row.update(maturity_date=date(r[1]),maturity_days=r[2],loan_gel=num(r[3]))
            elif identifier=='cd_auctions':
                row.update(auction_number=r[0],maturity_days=r[1],maturity_date=date(r[3]),offered_gel=num(r[4]),
                           demand_gel=num(r[5]),nominal_allocated_gel=num(r[6]),settlement_gel=num(r[7]),
                           discount_gel=num(r[8]),weighted_rate_pct=num(r[11],100))
            else:
                row.update(event_number=r[0],settlement_date=date(r[2]),maturity_date=date(r[3]),
                           maturity_days=r[4],rate_pct=num(r[5]),amount_gel=num(r[6]))
            row.update(source_id=identifier,source_row=i);rr.append(row)
        save(identifier+'_events',rr,'operation event','GEL; annual percent where available',
             'Native dated transactions; future contractual maturities are not future executed observations. Repo is interbank, not NBG intervention.', [identifier]);w.close()
    matrix('money_market','2026-E',range(4,16),'daily','GEL million')
    matrix('central_bank','CBS',list(range(4,61)),'monthly','GEL million, end period')
    w=workbook('market_rates');s=w.worksheets[0];rr=[];data=list(s.values)
    labels=['tibr_1day','tibr_7day','cd_7day','cd_1month','cd_3month','cd_6month',
            'government_6month','government_1year','government_2to3year','government_5year','government_8to10year']
    for i,r in enumerate(data,1):
        if within(r[0]):
            row=dict(date=date(r[0]));row.update({k+'_pct':num(r[j],100) for j,k in enumerate(labels,1)})
            row.update(source_id='market_rates',source_row=i);rr.append(row)
    save('market_rates_monthly',rr,'monthly','annual percent (source decimals x100)',
         'Published money and government-paper rates. Blank terms remain missing; domestic yields are not sovereign external spreads.', ['market_rates']);w.close()


def matrix(identifier,sheet,row_numbers,frequency,units,header=3):
    w=workbook(identifier);s=w[sheet];data=list(s.values);rr=[]
    for j,value in enumerate(data[header-1]):
        d=date(value)
        period=str(value).strip()
        if d:
            if not within(value):continue
            period=d.isoformat()
        elif re.fullmatch(r'20\d\d(Q[1-4])?',period):
            if not 2020<=int(period[:4])<=2026:continue
            # BOP future/unreported cells are retained as missing, never observations.
        else:continue
        for n in row_numbers:
            value=data[n-1][j];label=str(data[n-1][0] or '').strip()
            rr.append(dict(date=period,series_row=n,label=label,value=num(value),source_value_status='reported' if number(value) else 'blank_or_non_numeric',
                           source_id=identifier,sheet=sheet,source_cell=f'{openpyxl.utils.get_column_letter(j+1)}{n}'))
    save(identifier+('_'+sheet.replace(' ','_') if identifier=='external_debt' else ''),rr,frequency,units,
         'Native dated source cells; repeated labels retain source row identity. Annual and quarterly BOP periods remain distinct.', [identifier]);w.close()


def reserves():
    w=workbook('reserve_assets');s=w.worksheets[0];rr=[]
    for i,r in enumerate(s.values,1):
        if within(r[0]):
            rr.append(dict(date=date(r[0]),reserves_usdm=num(r[1],.001),fx_usdm=num(r[2],.001),sdr_usdm=num(r[3],.001),
                           imf_position_usdm=num(r[4],.001),gold_usdm=num(r[5],.001),other_usdm=num(r[6],.001),
                           source_id='reserve_assets',source_row=i))
    save('reserve_stocks_monthly',rr,'monthly end period','USD million (source USD thousand / 1000)',
         'Stocks are not intervention flows. Gold includes market valuation.', ['reserve_assets']);w.close()
    w=workbook('reserve_liquidity');rr=[]
    # Preserve sparse R1 form, including blanks, with labels and coordinates. Do not convert blanks to zero.
    for s in w:
        data=list(s.values)
        try:
            year=int(data[3][5]);month=dt.datetime.strptime(str(data[3][4]).strip(),'%B').month
            d=dt.date(year,month,calendar.monthrange(year,month)[1])
        except (ValueError,TypeError,IndexError):continue
        if not dt.date(2024,12,1)<=d<=CUTOFF:continue
        assert str(data[9][2]).strip()=='US Dollars' and str(data[9][4]).strip()=='Millions',s.title
        for n in list(range(21,45))+list(range(54,69))+list(range(77,104))+list(range(127,162)):
            label=' | '.join(str(v).strip() for v in data[n-1][1:3] if isinstance(v,str) and v.strip())
            if not label:continue
            for j in range(2,7):
                value=data[n-1][j]
                # Column C is a label in section II, but a numeric total in section III.
                if isinstance(value,str) and value.strip():continue
                rr.append(dict(date=d,source_id='reserve_liquidity',sheet=s.title,source_cell=f'{openpyxl.utils.get_column_letter(j+1)}{n}',
                               label=label,value=num(value),source_value_status='reported' if number(value) else 'blank',
                               units='million fine troy ounces' if n==34 else 'USD million'))
    save('reserve_liquidity_cells',rr,'monthly end period; forward drains at that vintage','USD million, except labeled gold volume',
         'Sparse R1 disclosure cells, not a fully audited usable-reserve measure. Section II D total/E-F-G maturity; III C total/D-E-F maturity; I D levels.', ['reserve_liquidity']);w.close()
    save('reserve_liquidity_reported',[r for r in rr if r['value'] is not None],'monthly end period','USD million except labeled gold volume',
         'Only explicitly numeric cells from the sparse R1 form. Omitted cells remain unknown, never zero; full sparse form is a manual-commit artifact.', ['reserve_liquidity'])


def external():
    matrix('bop_bpm6','BOP–BPM6(short)',range(4,41),'quarterly and separate annual totals','USD million')
    matrix('external_debt','ED-GEO-Tb2',[5,6,7,9,10,11,12],'quarterly end period','USD million; original-maturity classification')
    matrix('iip','IIP-1 (BPM6)',[4,5,6,30,73,167,186,187,211,254],'quarterly end period','USD million')
    w=workbook('trade_country');rr=[]
    for s in w:
        data=list(s.values)
        if '2015-2026' not in s.title:continue
        for j,d in enumerate(data[2]):
            if within(d):rr.append(dict(date=date(d),direction=s.title.split('_')[0],value_usdm=num(data[3][j],.001),
                                       source_id='trade_country',sheet=s.title,source_cell=f'{openpyxl.utils.get_column_letter(j+1)}4'))
    save('trade_monthly',rr,'monthly','USD million (source thousand / 1000)','Merchandise trade, not BOP goods-and-services or domestic value added.', ['trade_country']);w.close()
    w=workbook('remittances');s=w['1999-2026 E'];data=list(s.values);rr=[]
    for j,y in enumerate(data[2]):
        if not str(y).isdigit() or not 2020<=int(y)<=2026:continue
        for month in range(1,13):
            d=dt.date(int(y),month,calendar.monthrange(int(y),month)[1]);i=month+4
            if d>CUTOFF:continue
            for k,direction in [(j,'inflow'),(j+1,'outflow')]:
                rr.append(dict(date=d,direction=direction,value_usdm=num(data[i][k],.001),source_id='remittances',sheet=s.title,
                               source_cell=f'{openpyxl.utils.get_column_letter(k+1)}{i+1}'))
    save('money_transfers_monthly',rr,'monthly','USD million (source thousand / 1000)',
         'Electronic transfer-system flows, not all remittances or BOP personal transfers. Source header has no 2024 columns; do not relabel 2025.', ['remittances']);w.close()
    ISSUES.append(dict(source_id='remittances',location='1999-2026 E row 3',issue='Year header jumps from 2023 to 2025; 2024 absent',
                       residual=None,action='Retain explicit years; 2024 independently retrieved from remittances_country; see separate canonical totals and overlap validation'))
    w=workbook('remittances_country');s=w['2012-2026 (eng) '];data=list(s.values);rr=[];country=[]
    for j,d in enumerate(data[2]):
        if not within(d):continue
        for k,direction in [(j,'inflow'),(j+1,'outflow')]:
            assert data[3][k].lower()==direction
            rr.append(dict(date=date(d),direction=direction,value_usdm=num(data[4][k],.001),source_id='remittances_country',sheet=s.title,
                           source_cell=f'{openpyxl.utils.get_column_letter(k+1)}5'))
            for i in range(7,256):
                label=str(data[i-1][0] or '').strip()
                country.append(dict(date=date(d),country=label,direction=direction,value_usdm=num(data[i-1][k],.001),
                                    source_id='remittances_country',source_cell=f'{openpyxl.utils.get_column_letter(k+1)}{i}'))
    save('money_transfers_canonical',rr,'monthly','USD million (source thousand / 1000)',
         'Totals from the complete by-country workbook, including 2024. Original by-month table preserved separately for comparison.', ['remittances_country'])
    save('money_transfers_country',country,'monthly by country','USD million (source thousand / 1000)',
         'All labeled country rows 7-255, including reported zeros and blank cells. Country labels follow the source, not a causal control selection.', ['remittances_country']);w.close()
    sums=[]
    for r in rr:
        group=[x for x in country if x['date']==r['date'] and x['direction']==r['direction']]
        sums.append(dict(date=r['date'],direction=r['direction'],sum_country_usdm=sum(x['value_usdm'] for x in group if x['value_usdm'] is not None),
                         country_rows=len(group),missing_country_cells=sum(x['value_usdm'] is None for x in group),source_id='remittances_country'))
    save('money_transfers_country_sums',sums,'monthly','USD million','Reproducible sum of all country rows; compared with independently published total.', ['remittances_country'])
    w=workbook('travel');s=w['Income,Q'];rr=[]
    for i,r in enumerate(s.values,1):
        if not str(r[0]).isdigit() or not 2020<=int(r[0])<=2026:continue
        for q in range(1,5):
            if dt.date(int(r[0]),q*3,calendar.monthrange(int(r[0]),q*3)[1])>CUTOFF:continue
            rr.append(dict(date=f'{r[0]}Q{q}',travel_receipts_usdm=num(r[q]),source_id='travel',sheet=s.title,
                           source_cell=f'{openpyxl.utils.get_column_letter(q+1)}{i}'))
    save('travel_quarterly',rr,'quarterly','USD million','Quarterly travel receipts; no fabricated monthly travel observations after 2022.', ['travel']);w.close()
    w=workbook('money_aggregates');s=w['Monetary Ratios-eng'];rr=[]
    for i,r in enumerate(s.values,1):
        if within(r[0]):
            rr.append(dict(date=date(r[0]),m3_gelm=num(r[3]),m2_gelm=num(r[4]),fx_deposits_gelm=num(r[9]),
                           source_id='money_aggregates',source_row=i))
    save('money_aggregates_monthly',rr,'monthly end period','GEL million',
         'NBG M2 and M3 kept distinct; IMF ARA money definition remains to be reconciled.', ['money_aggregates']);w.close()
    w=workbook('debt_schedule');rr=[]
    for s in w:
        data=list(s.values);stamp=re.search(r'\d\d\.\d\d\.20\d\d',str(data[0][0]));assert stamp,s.title
        asof=dt.datetime.strptime(stamp.group(),'%d.%m.%Y').date()
        for i,r in enumerate(data,1):
            if i<6 or not r[0] or not any(number(v) for v in r[1:]):continue
            for j in range(1,min(len(r),16)):
                bucket=' | '.join(str(data[k][j]).strip() for k in [3,4] if data[k][j] is not None)
                if not bucket:continue
                rr.append(dict(date=asof,source_id='debt_schedule',sheet=s.title,source_cell=f'{openpyxl.utils.get_column_letter(j+1)}{i}',
                               label=str(r[0]).strip(),payment_bucket=bucket,value_usdm=num(r[j]),
                               measurement='contractual schedule at reference date; not realized future payment'))
    save('external_debt_payment_schedule',rr,'schedule at published stock date','USD million',
         'Principal and interest separated by source labels. Buckets include nested totals; do not sum overlapping buckets. Not a 2025 residual-maturity debt observation.', ['debt_schedule']);w.close()


def globals_data():
    rr=[]
    for i,r in enumerate(json.loads(source_path('sofr').read_text())['refRates']):
        d=dt.date.fromisoformat(r['effectiveDate'])
        if START<=d<=CUTOFF:
            rr.append(dict(date=d,rate_pct=r['percentRate'],volume_usd_bn=r['volumeInBillions'],revision_indicator=r['revisionIndicator'],
                           source_id='sofr',source_record=i))
    save('sofr_daily',sorted(rr,key=lambda r:r['date']),'US business daily','annualized percent; USD billion volume',
         'Effective date, not Georgian same-day pre-trade information. Publication is later; lag before causal use.', ['sofr'])
    rr=[]
    for i,r in enumerate(csv.DictReader(source_path('vix').read_text().splitlines()),2):
        d=dt.datetime.strptime(r['DATE'],'%m/%d/%Y').date()
        if START<=d<=CUTOFF:
            rr.append(dict(date=d,close=float(r['CLOSE']),source_id='vix',source_row=i))
    save('vix_daily',rr,'US trading daily','VIX index points','Cboe close; not information available at Georgian morning trade.', ['vix'])
    text=source_path('broad_dollar').read_text()
    pairs=re.findall(r'<tr[^>]*>\s*<th[^>]*>\s*(\d{1,2}-[A-Z]{3}-\d\d)\s*</th>\s*<td[^>]*>\s*([^<]+)',text,re.I)
    rr=[]
    for ds,v in pairs:
        d=dt.datetime.strptime(ds,'%d-%b-%y').date()
        if START<=d<=CUTOFF:
            rr.append(dict(date=d,index=float(v) if re.fullmatch(r'[0-9.]+',v.strip()) else None,source_id='broad_dollar',source_date_label=ds))
    save('broad_dollar_daily',rr,'US business daily','nominal broad USD index, January 2006=100',
         'Federal Reserve broad goods-and-services dollar index; higher=USD appreciation. Historical weights are revisable. No holiday fill.', ['broad_dollar'])


def text_only(s):
    return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s))).strip()


def html_tables(s):
    return [[ [text_only(td) for td in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S|re.I)]
              for tr in re.findall(r'<tr\b[^>]*>.*?</tr>',table,re.S|re.I)]
            for table in re.findall(r'<table\b[^>]*>.*?</table>',s,re.S|re.I)]


def displayed_number(s):
    s=s.replace(',','').replace(' ','')
    return float(s) if re.fullmatch(r'-?\d+(\.\d+)?',s) else None


def government():
    rr=[]
    for year in [2024,2025,2026]:
        identifier=f'mof_external_{year}'
        for ti,table in enumerate(html_tables(source_path(identifier).read_text()),1):
            stamp=re.search(r'\d\d\.\d\d\.20\d\d',' '.join(table[0]))
            assert stamp, (identifier,ti)
            ds=stamp.group(); day,month,source_year=map(int,ds.split('.'))
            assert source_year==year and 1<=month<=12,(identifier,ti,ds)
            period=f'{year}-{month:02d}'
            try:d=dt.datetime.strptime(ds,'%d.%m.%Y').date()
            except ValueError:
                d=None
                ISSUES.append(dict(source_id=identifier,location=f'HTML table {ti} heading',
                                   issue='Invalid source reference date: '+ds,residual=None,
                                   action='Retain source label and month; exact date left missing, not corrected'))
            if d is not None and d>CUTOFF:continue
            for ri,r in enumerate(table,1):
                if not r:continue
                label=r[0].lower().strip()
                if label not in ['external public debt','government external debt','external debt of national bank of georgia','eurobond']:continue
                # Totals have merged currency cells; trailing columns preserve USD/GEL ordering.
                nums=[displayed_number(s) for s in r]
                if year<2026:
                    usd,gel=nums[-2:];ai_usd=ai_gel=None
                else:
                    usd,ai_usd,gel,ai_gel=nums[-4:]
                assert usd is not None and gel is not None,(identifier,ti,r)
                rr.append(dict(date=d,month=period,source_date_label=ds,category=label,stock_usdm=usd/1000,stock_gelm=gel/1000,
                               accrued_interest_usdm=num(ai_usd,.001),accrued_interest_gelm=num(ai_gel,.001),
                               definition='Nominal including accrued interest' if year>=2026 else 'Pre-2026 debt-stock convention',
                               source_id=identifier,source_table=ti,source_row=ri))
    save('government_external_debt_monthly',rr,'monthly stated reference date','USD and GEL million (source thousand / 1000)',
         'Stocks, not disbursements or FX conversions. Preserve 2026 inclusion of accrued interest and source reference-date anomalies.',
         ['mof_external_2024','mof_external_2025','mof_external_2026'])
    text=source_path('mof_debt').read_text()
    assert 'Reporting Period - September' in text and '2026' in text
    rr=[]
    for ti,table in enumerate(html_tables(text),1):
        for ri,r in enumerate(table,1):
            if len(r)==7 and r[0].startswith(('External Public Debt in USD','External Government Debt in USD')):
                values=[displayed_number(v) for v in r[1:]]
                assert all(v is not None for v in values)
                rr.append(dict(month='2026-09',category=r[0],opening_usdm=values[0]/1000,closing_usdm=values[1]/1000,
                               reported_difference_usdm=values[2]/1000,drawings_usdm=values[3]/1000,
                               principal_paid_usdm=values[4]/1000,interest_paid_usdm=values[5]/1000,
                               source_id='mof_debt',source_table=ti,source_row=ri))
    save('government_debt_flows',rr,'one published month','USD million (source thousand / 1000)',
         'MoF debt cash flows use transaction-day FX; stocks use period-end FX and accrued interest. Conversion channel not disclosed.', ['mof_debt'],'month')


def ara():
    rr=[]
    metadata=json.loads(source_path('ara_indicators').read_text())['indicators']
    for identifier,indicator in [('ara_ratio','Reserves_ARA'),('ara_money_ratio','Reserves_M2'),
                                 ('ara_debt_ratio','Reserves_STD'),('ara_import_cover','Reserves_M')]:
        series=json.loads(source_path(identifier).read_text())['values'][indicator]['GEO']
        for year,value in sorted(series.items()):
            rr.append(dict(year=year,indicator=indicator,value=value,units='months' if indicator=='Reserves_M' else 'ratio, not percent',
                           source_id=identifier,source_key=f'values.{indicator}.GEO.{year}',
                           provider_metadata_modified=metadata[indicator]['last-modified'],
                           observation_status='IMF published benchmark; country input vintage/status not supplied by API'))
    save('imf_ara_published',rr,'annual','ratios or months as labeled',
         'April 2026 ARA dataset. Not an independent reconstruction or proof of an optimal reserve target. API returns all countries; explicitly select GEO.',
         ['ara_ratio','ara_money_ratio','ara_debt_ratio','ara_import_cover','ara_indicators'],'year')


def accounts():
    from pypdf import PdfReader
    reader=PdfReader(source_path('annual2025'))
    text=reader.pages[241].extract_text()
    # Human-selected statement rows, independently checked against the rendered page.
    # Machine verification matches each exact number pair to the pinned original PDF.
    facts=[('reserve_interest_cash',81750,82203),('reserve_interest_fvoci',282097,309042),
           ('reserve_interest_other',38023,47936),('reserve_interest_total',401870,439181),
           ('policy_interest_financial_institutions',536318,334180),('policy_interest_securities',136760,175679),
           ('policy_interest_total',673078,509859),('other_interest_income',708,4356),
           ('interest_income_total',1075656,953396),('policy_expense_securities',-4772,-5124),
           ('policy_expense_financial_institutions',-124559,-90237),('policy_expense_total',-129331,-95361),
           ('imf_interest_expense',-73248,-101102),('customer_interest_expense',-870,-714),
           ('lease_interest_expense',-444,-286),('other_interest_expense_total',-74562,-102102),
           ('interest_expense_total',-203893,-197463),('net_interest_income',871763,755933),
           ('unrealized_foreign_currency_gain',879333,447385),('dealing_gain',17995,13120)]
    rr=[]
    for label,new,old in facts:
        def fmt(v):return f'({abs(v):,})' if v<0 else f'{v:,}'
        assert re.search(re.escape(fmt(new))+r'\s+'+re.escape(fmt(old)),text),(label,new,old)
        for y,v in [(2025,new),(2024,old)]:
            rr.append(dict(year=y,series=label,value_gelm=v/1000,source_value_gel_thousand=v,
                           source_id='annual2025',pdf_page=242,financial_statement_page=6,
                           measurement='annual audited accrual; expense negative',extraction='curated row, numeric pair verified against PDF; visually checked'))
    save('annual_interest_accounts',rr,'annual','GEL million (source thousand / 1000)',
         'Accounting categories, not marginal costs attributable to the reserve-purchase episode. Audit dated 24 April 2026 is not a verified public-release timestamp.', ['annual2025'],'year')


def main():
    global SOURCES, OUT
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    SOURCES={r['id']:r for r in json.loads((ROOT/'data/source_manifest.json').read_text())}
    # Stage everything before promotion. A failed extraction leaves all prior outputs intact.
    with tempfile.TemporaryDirectory(prefix='nbg-extract-') as tmp:
        OUT=Path(tmp)
        intervention();exchange_rates();liquidity();reserves();external();globals_data();government();ara();accounts()
        (OUT/'catalogue.json').write_text(json.dumps(CATALOGUE,indent=2)+'\n')
        (OUT/'source_discrepancies.json').write_text(json.dumps(ISSUES,indent=2)+'\n')
        for p in sorted(OUT.iterdir()):
            target=FINAL/p.name
            if args.check:
                assert target.read_bytes()==p.read_bytes(),target
            else:
                FINAL.mkdir(parents=True,exist_ok=True)
                temporary=target.with_suffix(target.suffix+'.partial');temporary.write_bytes(p.read_bytes());temporary.replace(target)
        print(json.dumps([dict(file=Path(r['file']).name,rows=r['rows'],first=r['first'],last=r['last']) for r in CATALOGUE],indent=2))


if __name__=='__main__':main()
