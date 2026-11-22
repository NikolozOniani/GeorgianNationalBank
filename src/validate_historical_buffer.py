"""Validate the frozen historical reserve-buffer rules on the seven registered origins."""
import argparse
import json
import io
import re
import subprocess
from datetime import date, datetime
from decimal import Decimal as D

from lxml import html
from openpyxl import load_workbook
from historical_fx_cases import read, source_bytes
from historical_payment_calendar import html_rows
from minimum_reserve_buffer import Event, M, month_end, replay
from r2_reserves import ROOT

OUT = ROOT/'reports/buffer_validation'
HORIZONS = (1, 3, 12)
ZERO = D(0)


def service_columns(pdf, column_count, page=13):
    # Table 6 is physical page 13 of these finance ministry bulletins. PDF text
    # sometimes inserts spaces inside the capitalized row labels.
    text=subprocess.run(['pdftotext','-f',str(page),'-l',str(page),'-layout','-','-'],
                        input=pdf,stdout=subprocess.PIPE,check=True).stdout.decode()
    if "EXTERNAL DEBT SERVICE BY CREDITOR TYPE" not in text:
        raise ValueError("Unexpected service table page")
    fields={}
    for line in text.splitlines():
        parts=line.strip().split()
        label=''.join(re.split(r'[0-9]',line,1)[0].split())
        if label not in ('PRINCIPAL','INTEREST'):
            continue
        values=[D(t.replace(',','')) for t in parts if re.fullmatch(r'[0-9,.]+',t)]
        if len(values)!=2*column_count or label in fields:
            raise ValueError('Ambiguous MoF service column')
        fields[label]=values[::2]
    return [a+b for a,b in zip(fields['PRINCIPAL'],fields['INTEREST'])]


def wider_account(sources,origins):
    work=load_workbook(io.BytesIO(sources['nbg_template']),data_only=True,read_only=True)
    # Each selection is a source table column or a list of consecutive quarters.
    n3='PublicSectorDebtStatisticalBulletinN3ENG31.03.2015'
    refs={'2012Q1':('N1ENG18',6,None,[1]),'2013Q1':('N1ENG18',6,2,[2,3,4,5]),
          '2014Q1':(n3,6,2,[2,3,4,5]),'2018Q3':('N12ENG',8,4,[4,5,6,7]),
          '2021Q2':('N16ENG',6,5,None),'2022Q1':('N18ENG',8,6,None)}
    records=[]
    try:
        for o in origins:
            d=date.fromisoformat(o['origin'])
            key=d.strftime('template %m.%y')
            if key not in work.sheetnames:
                key=key.replace('.',' ')
            a=list(work[key].values)
            if a[19][3] not in (d.strftime('%B %Y'),d.strftime('%B %d, %Y')) or (a[9][2],a[9][4])!=('US Dollars','Millions'):
                raise ValueError('NBG template date or units changed')
            buckets=[-D(str(v)) for v in a[53][4:7]]
            if abs(sum(buckets)+D(str(a[53][3])))>D('.001') or min(buckets)<0:
                raise ValueError('Unreconciled template schedule')
            ref=refs.get(o['episode'])
            amounts=service_columns(sources[ref[0]],ref[1]) if ref else []
            for j,h in enumerate(HORIZONS):
                source = ref[0]+' Table 6 p13' if ref else ''
                columns=None
                if ref and h==3 and ref[2] is not None:
                    columns=[ref[2]]
                if ref and h==12:
                    columns=ref[3]
                data=amounts
                if o['episode']=='2021Q2' and h==12:
                    data=service_columns(sources['N18ENG'],8)
                    source='N18ENG Table 6 p13'
                    columns=[3,4,5,6]
                if o['episode']=='2022Q1' and h==12:
                    data=service_columns(sources['N19ENG'],6,14)
                    source='N19ENG Table 6 physical p14'
                    columns=[2,3,4,5]
                gross=sum(data[k] for k in columns) if columns else None
                schedule=sum(buckets[:j+1]).quantize(D('.000001'))
                records.append(dict(episode=o['episode'],origin=o['origin'],months=h,
                            template=key,II1_net_drain_usdm=schedule,mof_gross_service_usdm=gross,
                            template_minus_mof_usdm=schedule-gross if gross is not None else '',
                            mof_source=source if columns else '',
                            national_predicted_gap='',national_realized_gap='',primary_score='unidentified'))
    finally:
        work.close()
    return records


def raw_inputs(acquire):
    locks = json.loads((OUT/'source_locks.json').read_text())
    sources = {r['id']:source_bytes(r,acquire) for r in locks}
    events, coverage, stock, annual = [], [], [], []
    for origin in read(OUT/'origins.csv'):
        day = origin['origin']
        for basis in ('obl','exp'):
            key = f'{day}_{basis}'
            raw = sources[key]
            doc = html.fromstring(raw)
            title = ' '.join(doc.xpath('string(//title)').split())
            asof = datetime.strptime(title.split(' as of ')[-1],'%B %d, %Y').date().isoformat()
            if asof != day or not title.startswith('Georgia: Projected Payments'):
                raise ValueError('Wrong member or as-of date')
            principal = []
            dates = []
            for row in html_rows(raw):
                if len(row) not in (3,4):
                    continue
                try:
                    due = datetime.strptime(row[-2],'%B %d, %Y').date().isoformat()
                except ValueError:
                    continue
                dates.append(due)
                if row[0].startswith(('GRA Repurchase','PRGT Repayment')):
                    principal.append(dict(source=key,day=due,operation=row[0],pay_sdr=int(row[-1].replace(',','')),draw_sdr=0))
                elif not any(word in row[0] for word in ('Charges','Interest','Assessment')):
                    raise ValueError('Unclassified IMF schedule entry '+row[0])
            if not dates and 'No data is available' not in doc.text_content():
                raise ValueError('Unrecognized empty schedule')
            use = bool(dates and max(dates)>month_end(day,12))
            coverage.append(dict(origin=day,source=key,rows=len(dates),last_scheduled_date=max(dates,default=''),
                                 selected=int(use),principal_rows=len(principal)))
            if use:
                events.extend(r for r in principal if day < r['day'] <= month_end(day,12))
                break
        else:
            raise ValueError('No adequate schedule '+day)
        if origin['bond_status']=='active':
            key = 'stock'+day[:4]
            raw = html.fromstring(sources[key])
            panels = raw.xpath('//div[contains(concat(" ",normalize-space(@class)," "), $tab)]',
                               tab=f' tab{int(day[5:7])} ')
            match = []
            for panel in panels:
                if datetime.fromisoformat(day).strftime('%d.%m.%Y') not in ''.join(panel.itertext()):
                    continue
                for tr in panel.xpath('.//tr'):
                    cols=[' '.join(c.text_content().split()) for c in tr.xpath('./th|./td')]
                    if len(cols)==5 and cols[0].lower() in ('eurobonds','eurobond') and cols[1]=='USD':
                        match.append(D(cols[3].replace(' ','').replace(',',''))/1000)
            if len(match)!=1:
                raise ValueError('Unidentified MoF creditor stock '+day)
            stock.append(dict(origin=day,source=key,all_eurobonds_usdm=match[0]))
    for key,raw in sorted(sources.items()):
        if not key.startswith('tx'):
            continue
        year = int(key[2:])
        heading=' '.join(html.fromstring(raw).xpath('string(//h1)').split())
        if 'Georgia' not in heading or str(year) not in heading or 'in SDRs' not in html.fromstring(raw).text_content():
            raise ValueError('Unexpected member transaction table')
        totals=[0]*6
        reported=None
        for row in html_rows(raw):
            if len(row)!=8:
                continue
            if row[0]=='Total':
                reported=[int(v.replace(',','')) for v in row[1:7]]
                continue
            try:
                day=datetime.strptime(row[0],'%B %d, %Y').date()
            except ValueError:
                continue
            if day.year!=year:
                raise ValueError('Wrong transaction year')
            amounts=[int(v.replace(',','')) for v in row[1:7]]
            totals=[a+b for a,b in zip(totals,amounts)]
            events.append(dict(source=key,day=day.isoformat(),operation=row[-1],pay_sdr=sum(amounts[1::2]),
                               draw_sdr=sum(amounts[::2])))
        if reported!=totals:
            raise ValueError('IMF published annual totals disagree')
        annual.append(dict(year=year,source=key,annual_principal_sdr=sum(reported[1::2]),
                           annual_drawings_sdr=sum(reported[::2])))
    return events,coverage,stock,wider_account(sources,read(OUT/'origins.csv')),annual


def score(pred,low,high,h):
    if low>high or min(low,pred)<0:
        raise ValueError('Invalid score interval')
    missed=(max(ZERO,low-pred),max(ZERO,high-pred))
    excess=(max(ZERO,pred-high),max(ZERO,pred-low))
    return dict(uncovered_low=missed[0],uncovered_high=missed[1],excess_low=excess[0],excess_high=excess[1],
                carry_100bp_low=excess[0]*D('.01')*h/12,carry_100bp_high=excess[1]*D('.01')*h/12)


def month_number(d):
    day=date.fromisoformat(d)
    return 12*day.year+day.month


def accounts(origin, h, events, schedule_key, credit=None):
    cutoff=month_end(origin,h)
    selected=[r for r in events if origin<r['day']<=cutoff]
    plan=[Event(r['day'],str(i),D(r['pay_sdr'])/M) for i,r in enumerate(selected) if r['source']==schedule_key]
    actual=[r for r in selected if r['source'].startswith('tx')]
    realized=[Event(r['day'],str(i),(D(r['pay_sdr'])-D(r['draw_sdr']))/M) for i,r in enumerate(actual)]
    gross=sum((e.use for e in plan),ZERO)
    receipt=sum((D(r['draw_sdr'])/M for r in actual),ZERO)
    paid=sum((D(r['pay_sdr'])/M for r in actual),ZERO)
    simple=replay(origin,plan,h,ZERO)[0]
    if simple['minimum'] != gross:
        raise ValueError('Gross comparator contains signed receipts')
    pred=replay(origin,plan+([credit] if credit else []),h,ZERO)[0]
    outcome=replay(origin,realized,h,ZERO)[0]
    return pred,simple,outcome,paid,receipt


def check_transaction_coverage(origins,events,annual):
    table={int(r['year']):r for r in annual}
    for o in origins:
        start=date.fromisoformat(o['origin'])
        finish=date.fromisoformat(month_end(o['origin'],12))
        first=start.year+int(start.month==12)
        if any(year not in table for year in range(first,finish.year+1)):
            raise ValueError('Missing annual transaction extract '+o['origin'])
    for r in table.values():
        year_events=[x for x in events if x['source']==r['source']]
        if (sum(int(x['pay_sdr']) for x in year_events)!=int(r['annual_principal_sdr'])
                or sum(int(x['draw_sdr']) for x in year_events)!=int(r['annual_drawings_sdr'])):
            raise ValueError('Tracked transactions disagree with annual totals: '+r['source'])


def imf_scores(origins,events,coverage):
    records=[]
    for o in origins:
        origin=o['origin']
        key,=[r['source'] for r in coverage if r['origin']==origin and int(r['selected'])]
        credit=None
        if D(o['forecast_credit_sdr']):
            if not o.get('credit_publication_date') or o['credit_publication_date']>origin or o['credit_receipt_date']<=origin:
                raise ValueError('Credit requires public, pre-cutoff evidence and a future receipt date')
            credit=Event(o['credit_receipt_date'],'eligible approved receipt',-D(o['forecast_credit_sdr'])/M)
        for h in HORIZONS:
            pred,simple,out,paid,drawn=accounts(origin,h,events,key,credit)
            gross=simple['minimum']
            for rule,forecast in [('cash path',pred),('gross debt service',simple)]:
                b=forecast['minimum']
                actual=out['minimum']
                err=(month_number(forecast['first_binding_date'])-month_number(out['first_binding_date'])
                     if b>0 and actual>0 else None)
                records.append(dict(episode=o['episode'],origin=origin,months=h,rule=rule,
                    predicted_sdrm=b,original_schedule=key+' (as-of reconstruction)',actual_draws_sdrm=drawn,
                    actual_gross_no_receipts_sdrm=paid,actual_peak_with_usable_draws_sdrm=actual,
                    gross_schedule_error_sdrm=gross-paid,uncovered_if_no_receipts=max(ZERO,paid-b),
                    excess_if_no_receipts=max(ZERO,b-paid),first_predicted_peak=forecast['first_binding_date'] if b else '',
                    first_realized_peak=out['first_binding_date'] if actual else '',signed_month_error=err,
                    absolute_month_error=abs(err) if err is not None else None,**score(b,actual,actual,h)))
    return records


def bond_forecast(origin,h,face):
    end=month_end(origin,h)
    uses=[]
    for year in range(int(origin[:4]),int(end[:4])+1):
        for month in ('04','10'):
            due=f'{year}-{month}-12'
            if origin<due<=min(end,'2021-04-12'):
                amount=face*D('.06875')/2+(face if due=='2021-04-12' else ZERO)
                uses.append(Event(due,'coupon and principal' if due=='2021-04-12' else 'coupon',amount))
    return replay(origin,uses,h,ZERO)[0],sum((r.use for r in uses),ZERO)


def bond_scores(origins,stocks):
    bands={(r['episode'],int(r['months'])):r for r in read(OUT/'bond_outcomes.csv')}
    stock={r['origin']:D(r['all_eurobonds_usdm']) for r in stocks}
    records=[]
    for o in origins:
        for h in HORIZONS:
            grade = ('public instrument terms and earlier official stock' if o['episode'] in ('2018Q3','2021Q2')
                     else o['bond_grade'])
            base=dict(episode=o['episode'],origin=o['origin'],months=h,input_grade=grade,
                      signed_month_error=0 if (o['episode'],h)==('2021Q2',1) else '',
                      absolute_month_error=0 if (o['episode'],h)==('2021Q2',1) else '')
            if o['bond_status']!='active':
                records.append(dict(**base,model_usdm='',simple_usdm='',predicted_peak_month='',status=o['bond_status'],
                                    actual_low='',actual_high='',**{k:'' for k in score(ZERO,ZERO,ZERO,h)}))
                continue
            total=stock[o['origin']]
            # The 2008 issue remained alongside the new USD 500m issue at the first two openings.
            if total != (D('564.75') if o['episode'] in ('2012Q1','2013Q1') else D(500)):
                raise ValueError('Opening-stock corroboration failed')
            p,simple=bond_forecast(o['origin'],h,D(500))
            band=bands.get((o['episode'],h))
            info = dict(status='other outstanding issue; isolated outturn unavailable',actual_low='',actual_high='',
                        **{k:'' for k in score(ZERO,ZERO,ZERO,h)})
            if band:
                lo,hi=D(band['low_usdm']),D(band['high_usdm'])
                if simple!=p['minimum']:
                    raise ValueError('Compare rules separately when dated financing is added')
                info=dict(status=band['status'],actual_low=lo,actual_high=hi,**score(simple,lo,hi,h))
            records.append(dict(**base,model_usdm=p['minimum'],simple_usdm=simple,
                                predicted_peak_month=p['first_binding_date'][:7] if simple else '',**info))
    return records


def rankings(imf,bonds):
    output=[]
    for account,rows,grade_field in [('IMF principal SDRm',imf,None),('bond gross USDm',bonds,'input_grade')]:
        base=[r for r in rows if r['months']==3 and (r.get('rule','cash path')=='cash path') and r['uncovered_high']!='']
        grades=sorted({r[grade_field] for r in base}) if grade_field else ['as-of reconstruction']
        for grade in grades:
            group=[r for r in base if not grade_field or r[grade_field]==grade]
            for omit in ['none']+[r['episode'] for r in group]:
                sample=[r for r in group if r['episode']!=omit]
                if not sample:
                    continue
                for rule in ('cash path','gross debt service'):
                    out=sample
                    if account.startswith('IMF'):
                        out=[r for r in imf if r['months']==3 and r['rule']==rule and r['episode'] in {v['episode'] for v in sample}]
                    output.append(dict(account=account,grade=grade,exclude=omit,rule=rule,episodes=len(out),
                         **{k:sum(r[k] for r in out) for k in ('uncovered_low','uncovered_high','excess_low','excess_high')}))
    return output


def save(name,rows,check):
    import csv
    import io
    buf=io.StringIO()
    w=csv.DictWriter(buf,rows[0].keys(),lineterminator='\n')
    w.writeheader()
    w.writerows([{k:format(v,'f') if isinstance(v,D) else v for k,v in r.items()} for r in rows])
    path=OUT/name
    if check:
        if buf.getvalue().encode()!=path.read_bytes():
            raise ValueError('Changed output: '+name)
    else:
        path.write_bytes(buf.getvalue().encode())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from-raw',action='store_true')
    p.add_argument('--acquire',action='store_true')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if a.from_raw or a.acquire:
        for f,rows in zip(('imf_events.csv','schedule_coverage.csv','bond_stocks.csv','wider_public_account.csv','transaction_coverage.csv'),raw_inputs(a.acquire)):
            save(f,rows,a.check)
    origins=read(OUT/'origins.csv')
    events=read(OUT/'imf_events.csv')
    check_transaction_coverage(origins,events,read(OUT/'transaction_coverage.csv'))
    imf=imf_scores(origins,events,read(OUT/'schedule_coverage.csv'))
    bonds=bond_scores(origins,read(OUT/'bond_stocks.csv'))
    for f,rows in [('imf_scores.csv',imf),('bond_scores.csv',bonds),('leave_one_out.csv',rankings(imf,bonds))]:
        save(f,rows,a.check)


if __name__=='__main__':
    main()
