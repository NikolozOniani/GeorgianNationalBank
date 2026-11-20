"""Freeze reserve eligibility accounts. Offline rebuild unless --from-raw is used."""
import argparse
import csv
import io
from decimal import Decimal as D

from openpyxl.utils import get_column_letter

from historical_fx_shocks import ROOT, table

OUT = ROOT / 'reports/reserve_buffer_policy'
HIST = ROOT / 'reports/historical_fx_shocks'
CAL = HIST / 'payment_calendar'
R2 = ROOT / 'reports/r2_2026_11_11'
EARLY = ('2008-07-31', '2008-12-31', '2020-03-31')
BANK_DATES = ('2008-06-30', EARLY[1], EARLY[2])


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def emit(name, rows, check):
    buf = io.StringIO()
    w = csv.DictWriter(buf, rows[0].keys(), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    path = OUT / name
    if check:
        if path.read_bytes() != buf.getvalue().encode():
            raise ValueError('Rebuild differs: ' + name)
    else:
        path.write_bytes(buf.getvalue().encode())


def raw_extracts():
    result = []
    def record(day, key, value, source, cell, scale=1):
        amount = '' if value is None else format(D(str(value))/scale, '.9f')
        result.append(dict(date=day, item=key, usd_million=amount, source=source, cell=cell))
    gir = table('reserve_assets', 'GIR (eng) ')
    if 'Thousand USD' not in gir[0][0]:
        raise ValueError('Unexpected GIR units')
    for i, row in enumerate(gir, 1):
        day = str(row[0])[:10]
        if day in EARLY:
            for j, key in enumerate(['headline', 'fx_total', 'sdr', 'imf_position', 'gold', 'other'], 1):
                record(day, key, row[j], 'reserve_assets GIR (eng)', f'{get_column_letter(j+1)}{i}', 1000)
    form = table('reserve_liquidity', 'template 03.20')
    if form[9][4] != 'Millions' or form[9][2] != 'US Dollars' or form[19][3] != 'March 31, 2020':
        raise ValueError('Unexpected template')
    for i,j,key in [(25,4,'deposits'), (23,4,'securities'), (134,4,'pledge'), (137,4,'lent'),
                    (160,4,'basket'), (161,4,'nonbasket')]:
        record(EARLY[2], key, form[i-1][j-1], 'reserve_liquidity template 03.20', f'{get_column_letter(j)}{i}')
    for i, start, key in [(54,5,'II1'), (77,4,'III1')]:
        for offset, h in enumerate([1,3,12]):
            j = start + offset
            record(EARLY[2], f'{key}_bucket_{h}', form[i-1][j-1], 'reserve_liquidity template 03.20', f'{get_column_letter(j)}{i}')
    bank = table('iip', 'IIP-1 (BPM6)')
    if 'Million of USD' not in bank[1][0]:
        raise ValueError('Unexpected IIP units')
    for j, v in enumerate(bank[2]):
        day = str(v)[:10]
        if day == EARLY[1]:
            if 'Reserve assets' not in bank[166][0] or bank[174][0].strip() != 'Currency and deposits' or bank[177][0].strip() != 'Securities':
                raise ValueError('IIP reserve breakdown changed')
            for i, key in [(175,'deposits'),(178,'securities')]:
                record(day, key, bank[i-1][j], 'iip IIP-1 (BPM6)', f'{get_column_letter(j+1)}{i}')
        if day in BANK_DATES:
            for i,key in [(48,'bank_securities'),(80,'bank_deposits'),(261,'bank_deposit_liabilities')]:
                if 'Deposit-taking corporations' not in bank[i-2][0] or bank[i-1][0].strip() != 'Short-term':
                    raise ValueError('IIP sector or maturity changed')
                record(day,key,bank[i-1][j], 'iip IIP-1 (BPM6)', f'{get_column_letter(j+1)}{i}')
    return result


def openings(extract):
    by_date = {}
    for r in extract:
        by_date.setdefault(r['date'], {})[r['item']] = r['usd_million']
    # Opening stock and prospective calls are kept in separate accounts.
    cols = ('headline', 'deposits', 'securities', 'sdr', 'gold', 'imf_position', 'other',
            'pledge', 'lent', 'basket', 'nonbasket')
    assets = []
    calls = []
    for day in EARLY:
        r = by_date[day]
        assets.append(dict(date=day, **{k:r.get(k,'') for k in cols}, fx_total=r['fx_total']))
        for horizon in (1,3,12):
            def cumulative(group):
                if day != EARLY[2]:
                    return ''
                return sum(D(r[f'{group}_bucket_{h}']) for h in (1,3,12) if h <= horizon)
            calls.append(dict(date=day, months=horizon, II1_signed=cumulative('II1'), III1_signed=cumulative('III1')))
    mapping = ['headline','deposits','fx_securities','sdr','gold','imf_position','other_reserve_assets',
               'pledge_memo_in_reserves','repo_lent_in_reserves','sdr_basket_currencies','other_currencies']
    for r in read(R2/'liquidity_schedule.csv'):
        if r['horizon_months'] == '1':
            assets.append(dict(date=r['date'], **{k:r[v+'_usdm'] for k,v in zip(cols,mapping)},
                               fx_total=D(r['deposits_usdm'])+D(r['fx_securities_usdm'])))
        calls.append(dict(date=r['date'], months=r['horizon_months'], II1_signed=r['reported_II_1_signed_usdm'],
                          III1_signed=r['reported_III_1_signed_usdm']))
    for r in assets:
        gross = D(r['headline'])
        component_sum = sum(D(r[k]) for k in ('fx_total','gold','sdr','imf_position','other'))
        if abs(gross-component_sum) > D('.001'):
            raise ValueError('Reserve composition fails at ' + r['date'])
        # Keep negative other positions even when positive miscellaneous assets are excluded.
        negative_other = min(D(0),D(r['other']))
        if r['deposits'] and abs(D(r['deposits'])+D(r['securities'])-D(r['fx_total'])) > D('.001'):
            raise ValueError('FX composition fails')
        if r['pledge'] or r['lent']:
            raise ValueError('Review new encumbrance disclosures before applying access assumptions')
        r.update(fx_split_residual_usdm=(D(r['fx_total'])-D(r['deposits'])-D(r['securities']) if r['deposits'] else ''),
                 deposits_only_conditional=D(r['deposits'])+negative_other if r['deposits'] else '',
                 fx_at_par_conditional=D(r['fx_total'])+negative_other,
                 fx_securities_5pct_discount=(D(r['deposits']) + D('.95') * D(r['securities']) + negative_other
                                             if r['securities'] else ''),
                 all_at_par_conditional=gross, verified_free_cash='', zero_floor=0,
                 sensitivity_floor_usdm= gross * D('.01'))
    return assets,calls


def payment_matrix():
    out = []
    def entry(key,period,payer,description,ccy,amount,public,bank,sales,source):
        out.append(dict(id=key,date_or_interval=period,payer=payer,description=description,unit=ccy,amount=amount,
                        public_float=public,bank_increment=bank,sales_increment=sales,source=source))
    for r in read(CAL/'payments.csv'):
        if D(r['gross_in']):
            continue  # Split funding records below are canonical for receipts.
        day = r['transaction_date'] or r['nominal_due']
        status = {'IMF transaction':'dated paid', 'IMF projection':'schedule scenario only',
                  'contract date; quarter paid':'nominal due; settlement day unknown'}[r['evidence']]
        entry(day+' '+r['instrument'], day, r['payer_or_recipient'], r['instrument'], r['currency'],
              r['gross_out'], status, 'off','off','payment_calendar/payments.csv')
    for r in read(HIST/'cases/imf_cash.csv'):
        if r['date'] == '2009-05-01':
            entry(r['date']+' '+r['operation'], r['date'], 'IMF member account', r['operation'], 'SDR',
                  r['principal_paid_sdr'], 'dated paid', 'off', 'off', 'cases/imf_cash.csv')
    for q, m, actor, item, treatment in [
        ('2009Q1','2009Q1','general government','external amortization outflow','fiscal envelope only'),
        ('2009Q1','2009Q1','general government','interest to nonresidents','fiscal envelope only'),
        ('2020Q2','2020Q2','government','external service including guaranteed','quarter envelope replaces dated government service'),
        ('2020Q2','2020Q2','NBG','external service','quarter envelope replaces dated NBG service'),
        ('2009Q1','2009-01','private Bank of Georgia','Merrill Lynch senior loan face repaid in full in January','off')]:
        r, = [x for x in read(CAL/'quarter_inputs.csv') if (x['quarter'],x['account'],x['item'])==(q,actor,item)]
        entry(m+item,m,actor,item,r['unit'],r['amount'],treatment,'eligible only on verified residual' if treatment=='off' else 'off',
              'off','payment_calendar/quarter_inputs.csv')
    entry('2009-06 private put','2009-06','Bank of Georgia','put notes repaid','USD million',
          next(r['usd_million'] for r in read(HIST/'cases/document_ledger.csv') if r['period']=='2009-06'),
          'off','eligible only on verified residual','off','cases/document_ledger.csv')
    war = {r['observation']:r for r in read(HIST/'war_chronology.csv')}
    for item,public,bank,sales in [('government imports','public use; amount and timing unresolved','off','off'),
                                  ('waiver of FX deposit reserve requirement','off','release only once if claim and cash documented','off'),
                                  ('FX sales','off','off','replay budget')]:
        r = war[item]
        entry('August '+item,r['period'],r['holder_or_payer'],item,r['unit'],r['value'],public,bank,sales,'war_chronology.csv')
    for r in read(HIST/'cases/document_ledger.csv'):
        if r['measure']=='net FX sales':
            entry(r['period']+' sales',r['period'],'NBG','all-market net sales','USD million',r['usd_million'],
                  'off','off','quarter net replay only','cases/document_ledger.csv')
    for r in read(HIST/'cases/monthly.csv'):
        if r['month'].startswith('2020'):
            entry(r['month']+' sales',r['month'],'NBG','all-market net sales','USD million',r['all_market_net_sales_usdm'],
                  'off','off','monthly net replay only','cases/monthly.csv')
    if len({r['id'] for r in out}) != len(out):
        raise ValueError('Duplicate cash call')
    for r in out:
        if r['bank_increment'] != 'off':
            r['account'] = 'bank_support_candidate'
        elif r['sales_increment'] != 'off':
            r['account'] = 'sales_replay'
        elif 'envelope' in r['public_float']:
            r['account'] = 'public_aggregate_alternative'
        elif r['public_float'].startswith('public use'):
            r['account'] = 'unquantified_public'
        elif r['public_float'] == 'schedule scenario only':
            r['account'] = 'projected_public_payment'
        else:
            r['account'] = 'documented_public_payment'
    return out


def bank_inventory(extract):
    dates = {}
    for r in extract:
        if r['item'].startswith('bank_'):
            dates.setdefault(r['date'], {})[r['item']] = D(r['usd_million'])
    fields = {'bank_st_debt_security_assets':'bank_securities', 'bank_st_deposit_assets':'bank_deposits',
              'bank_st_deposit_liabilities':'bank_deposit_liabilities'}
    for r in read(ROOT/'data/derived/r2_2026_11_11/bank_exposures.csv'):
        dates.setdefault(r['date'], {})[fields[r['field']]] = D(r['value_usdm'])
    result = []
    for day, stocks in sorted(dates.items()):
        own = stocks['bank_deposits'] + stocks['bank_securities']
        result.append(dict(date=day, **stocks, zero_access_usdm=0, half_access_usdm=own/2,
                           full_access_usdm=own, verified_bank_specific_usable_usdm=''))
    return result


def financing():
    rows = []
    for r in read(CAL/'financing.csv'):
        origin = '2008-12-31' if r['draw_date'] < '2010' else '2020-03-31'
        pre = (r['signature'] or r['approval_or_availability']) <= origin
        rows.append(dict(facility=r['facility'],owner=r['beneficiary'],origin=origin,
                         approved=r['approval_or_availability'],signature=r['signature'],effective=r['effective'],
                         receipt=r['draw_date'],unit=r['ccy'],actual_gross_face=r['face_amount'],
                         no_new_rescue_gross_face=r['face_amount'] if pre else 0,usable_net_cash='',
                         restriction=r['interpretation']))
    for r in read(HIST/'war_chronology.csv'):
        if r['observation'] in ('first SBA drawing','first repatriation from sovereign wealth funds'):
            own = 'repatriation' in r['observation']
            rows.append(dict(facility=r['observation'],owner='Treasury' if own else 'Georgia IMF member',
                             origin='2008-07-31',approved='' if own else '2008-09-15',signature='',effective='',
                             receipt=r['period'],unit=r['unit'],actual_gross_face=r['value'],
                             no_new_rescue_gross_face=r['value'] if own else 0,usable_net_cash='',restriction=r['cash_treatment']))
    dec, = [r for r in read(HIST/'cases/imf_cash.csv') if r['date']=='2020-12-18']
    rows.append(dict(facility='EFF seventh review', owner='central bank', origin='2020-03-31',
                     approved='2020-12-16', signature='', effective='', receipt=dec['date'], unit='SDR',
                     actual_gross_face=dec['disbursed_sdr'], no_new_rescue_gross_face=0, usable_net_cash='',
                     restriction='December review and drawing; outside Q2, within 12 months of March origin'))
    return rows


def settle_treasury(bill, external_cash, deposit_at_nbg):
    # All three inputs must refer to available funds of the same currency at settlement.
    if min(bill, external_cash, deposit_at_nbg) < 0:
        raise ValueError('Negative payment or balance')
    outside = min(bill, external_cash)
    at_nbg = min(bill - outside, deposit_at_nbg)
    backstop = bill - outside - at_nbg
    return dict(external_treasury_used=outside, treasury_at_nbg_used=at_nbg,
                assumed_public_backstop=backstop, gross_nbg_delivery=at_nbg+backstop)


def coupon_routes():
    coupon, = [r for r in read(CAL/'payments.csv') if r['instrument'] == '2021 Eurobond interest']
    bill = D(coupon['gross_out'])
    rows = []
    for name, external, at_nbg in [('externally funded', bill, 0), ('deposit at NBG', 0, bill),
                                  ('no Treasury funds', 0, 0)]:
        rows.append(dict(scenario=name, bill_usd=bill, assumed_external_usd=external,
                         assumed_deposit_at_nbg_usd=at_nbg, **settle_treasury(bill, external, at_nbg)))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--from-raw',action='store_true')
    args=p.parse_args()
    if args.from_raw:
        emit('historical_cells.csv',raw_extracts(),args.check)
    assets,calls=openings(read(OUT/'historical_cells.csv'))
    for name,data in [('opening_assets',assets),('scheduled_calls',calls),('policy_matrix',payment_matrix()),
                      ('funding_cases',financing()),('coupon_routes',coupon_routes()),('bank_assets',bank_inventory(read(OUT/'historical_cells.csv')))]:
        emit(name+'.csv',data,args.check)


if __name__=='__main__':
    main()
