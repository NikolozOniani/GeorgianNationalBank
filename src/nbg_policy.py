"""Acquire official NBG sources and build an explicitly incomplete 2020–24 panel."""
import calendar,concurrent.futures,csv,datetime as dt,hashlib,json,pathlib,urllib.request,xml.etree.ElementTree as ET
import openpyxl

ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw';OUT=ROOT/'reports'
SOURCES={
 'policy_rate.xlsx':'https://nbg.gov.ge/fm/%E1%83%A1%E1%83%A2%E1%83%90%E1%83%A2%E1%83%98%E1%83%99%E1%83%90/financial_markets/eng/mpireng.xlsx',
 'reserves.xml':'https://nbg.gov.ge/fm/nsdp/nbg/ilv1-geo.xml',
 'bop.xml':'https://nbg.gov.ge/fm/nsdp/nbg/bop5-geo.xml',
 'tibr.xlsx':'https://nbg.gov.ge/fm/%E1%83%A1%E1%83%A2%E1%83%90%E1%83%A2%E1%83%98%E1%83%A1%E1%83%A2%E1%83%98%E1%83%99%E1%83%90/analytical_data/eng/tibreng.xlsx',
 'group_cpi.xlsx':'https://www.geostat.ge/media/83812/Consumer-Price-Indices-(Previous-month=100).xlsx',
 'annual2024.pdf':'https://nbg.gov.ge/fm/%E1%83%9E%E1%83%A3%E1%83%91%E1%83%9A%E1%83%98%E1%83%99%E1%83%90%E1%83%AA%E1%83%98%E1%83%94%E1%83%91%E1%83%98/%E1%83%90%E1%83%9C%E1%83%92%E1%83%90%E1%83%A0%E1%83%98%E1%83%A8%E1%83%94%E1%83%91%E1%83%98/%E1%83%AC%E1%83%9A%E1%83%98%E1%83%A3%E1%83%A0%E1%83%98_%E1%83%90%E1%83%9C%E1%83%92%E1%83%90%E1%83%A0%E1%83%98%E1%83%A8%E1%83%98/2024/annual-eng-2024.pdf?v=bf7fu',
 'auction_20241008.html':'https://nbg.gov.ge/en/media/news/foreign-exchange-auction-results-of-the-national-bank-of-georgia',
 'imf2025.pdf':'https://www.imf.org/-/media/files/publications/cr/2025/english/1geoea2025002-source-pdf.pdf',
}
PINNED={'policy_rate.xlsx':'cd2230ee767dc64c2c526caf21e0fc7f8322bf966b5a0cb98cab2760d049ab9d',
        'reserves.xml':'71590914ddb1ae60a58834058ff74fc7adca0ea1deb48da874adae21f8e19237',
        'bop.xml':'98c2e693c2e697935f0f05fb749d946af0226e8fd5f70f975c8c7fa16fcb47b4',
        'tibr.xlsx':'d0c47075568c36c276cde78821cc3c0322c977fb6618debf4ae74f373b869715',
        'group_cpi.xlsx':'5b2df9ab880ff87e07e3329b35826c301f3c318f35aa1313041ad1b55946b6b7',
        'annual2024.pdf':'87d2d50b99791a3737031f462123dd8908957fe4082d7b639ea2ba883cb68580',
        'auction_20241008.html':'e53438949eee525d5ca3d3dae050837e0fc55bfbc07620b845da70ed43fd4b1a',
        'imf2025.pdf':'696a28892665a1c94a462fcf62b1ad733c9739c8998bd62622ef6a4a3c9d487b'}
def digest(b):return hashlib.sha256(b).hexdigest()
def fetch(name,url,expected=None):
    RAW.mkdir(parents=True,exist_ok=True);p=RAW/name
    if not p.exists():p.write_bytes(urllib.request.urlopen(url,timeout=60).read())
    b=p.read_bytes();h=digest(b)
    if expected and h!=expected:raise ValueError(f'{name} source vintage changed; inspect before using')
    return {'source_url':url,'sha256':h,'bytes':len(b),'local_raw':str(p.relative_to(ROOT))}
def sdmx(name):
    root=ET.parse(RAW/name).getroot();out={}
    for series in root.iter():
        if not series.tag.endswith('Series'):continue
        key=series.attrib.get('INDICATOR');out[key]={}
        for obs in series:
            if obs.tag.endswith('Obs') and 'OBS_VALUE' in obs.attrib:
                out[key][obs.attrib['TIME_PERIOD']]=float(obs.attrib['OBS_VALUE'])
    return out
def rate_events():
    s=openpyxl.load_workbook(RAW/'policy_rate.xlsx',read_only=True,data_only=True).active
    events=[]
    for decision,effective,rate,*_ in list(s.values)[2:]:
        if isinstance(decision,dt.datetime) and isinstance(effective,dt.datetime) and isinstance(rate,(int,float)):
            events.append({'decision_date':decision.date().isoformat(),'effective_date':effective.date().isoformat(),'policy_rate_pct':float(rate)})
    assert events==sorted(events,key=lambda x:x['effective_date'])
    return events
def cpi_monthly():
    s=openpyxl.load_workbook(RAW/'group_cpi.xlsx',read_only=True,data_only=True)['Georgia'];r=list(s.values)
    year=None;month=0;out={}
    for col,y in enumerate(r[2]):
        if isinstance(y,int):year=y;month=0
        if year and r[3][col] in ('I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'):
            month+=1;v=r[4][col]
            if isinstance(v,(int,float)) and v>0:out[f'{year}-{month:02d}']=float(v-100)
    return out
def tibr_daily():
    s=openpyxl.load_workbook(RAW/'tibr.xlsx',read_only=True,data_only=True).active
    rows=[]
    for date,rate,volume,r1m,r3m,r6m,index,*_ in list(s.values)[3:]:
        if isinstance(date,dt.datetime) and 2020<=date.year<=2024:
            rows.append({'date':date.date().isoformat(),'tibr_overnight_pct':100*rate if isinstance(rate,(int,float)) else '',
              'volume_gel':volume if isinstance(volume,(int,float)) else '',
              'tibr_1m_pct':100*r1m if isinstance(r1m,(int,float)) else '',
              'tibr_3m_pct':100*r3m if isinstance(r3m,(int,float)) else '',
              'tibr_6m_pct':100*r6m if isinstance(r6m,(int,float)) else '',
              'tibr_index':index if isinstance(index,(int,float)) else ''})
    return rows
def month_end(y,m):return f'{y}-{m:02d}-{calendar.monthrange(y,m)[1]:02d}'
def usd_request(item):
    y,m=item;date=month_end(y,m)
    url=f'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json/?currencies=USD&date={date}'
    cache=RAW/'usd_api'/f'{y}-{m:02d}.json';cache.parent.mkdir(parents=True,exist_ok=True)
    if not cache.exists():cache.write_bytes(urllib.request.urlopen(url,timeout=50).read())
    raw=cache.read_bytes();arr=json.loads(raw)
    if not arr or len(arr)!=1:raise ValueError(f'bad API response {date}')
    d=arr[0];currency=next(c for c in d['currencies'] if c['code']=='USD')
    if currency['quantity']!=1:raise ValueError('unexpected USD quote quantity')
    return f'{y}-{m:02d}',{'requested_date':date,'api_date':d['date'][:10],'valid_from':currency['validFromDate'][:10],
                         'rate':float(currency['rate']),'source_url':url,'sha256':digest(raw)}
def write_csv(path,rows,fields):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def build():
    OUT.mkdir(exist_ok=True);manifest={}
    for name,url in SOURCES.items():manifest[name]=fetch(name,url,PINNED[name])
    auction_html=(RAW/'auction_20241008.html').read_text()
    assert 'October 8, 2024' in auction_html and '48 500 000' in auction_html and '2.7194' in auction_html
    from pypdf import PdfReader
    annual_pages=[]
    for page in PdfReader(RAW/'annual2024.pdf').pages[:60]:
        text=page.extract_text()
        if '52.65' in text and '382.1' in text and '434.75' in text:annual_pages.append(text)
    assert annual_pages,'2024 annual intervention passage missing'
    auction_events=[{'auction_date':'2024-10-08','status':'executed disclosed auction result','currency':'USD',
                     'nbg_direction':'sale','amount_usd_m':48.5,'weighted_average_gel_per_usd':2.7194,
                     'source_url':SOURCES['auction_20241008.html'],'source_sha256':PINNED['auction_20241008.html']}]
    write_csv(OUT/'nbg_auction_events_verified.csv',auction_events,list(auction_events[0]))
    annual=[{'year':2024,'auction_net_sales_usd_m':382.1,'bmatch_net_sales_usd_m':52.65,'total_net_sales_usd_m':434.75,
             'auction_events_reported_n':7,'source_url':SOURCES['annual2024.pdf'],'source_sha256':PINNED['annual2024.pdf']}]
    write_csv(OUT/'nbg_fx_annual_benchmarks.csv',annual,list(annual[0]))
    events=rate_events();res=sdmx('reserves.xml');bop=sdmx('bop.xml');cpi=cpi_monthly();tibr=tibr_daily()
    write_csv(OUT/'nbg_tibr_daily_2020_2024.csv',tibr,list(tibr[0]))
    months=[(y,m) for y in range(2020,2025) for m in range(1,13)]
    usd={};errors={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures={pool.submit(usd_request,item):item for item in months}
        for future,item in futures.items():
            try:k,v=future.result();usd[k]=v
            except Exception as exc:errors[f'{item[0]}-{item[1]:02d}']=str(exc)
    rows=[];last=None
    for y,m in months:
        period=f'{y}-{m:02d}';end=month_end(y,m)
        current=[e for e in events if e['effective_date']<=end]
        stock=res['RAFA_USD'].get(period);previous=res['RAFA_USD'].get(f'{y-1}-12' if m==1 else f'{y}-{m-1:02d}')
        row={'month':period,'policy_rate_end_pct':current[-1]['policy_rate_pct'] if current else '',
             'policy_decisions_n':sum(e['decision_date'][:7]==period for e in events),
             'official_reserves_usd_m':stock if stock is not None else '',
             'reserve_stock_change_usd_m':stock-previous if stock is not None and previous is not None else '',
             'reserve_fx_usd_m':res['RAXGFX_USD'].get(period,''),
             'reserve_imf_usd_m':res['RAFAIMF_USD'].get(period,''),
             'reserve_sdr_usd_m':res['RAFASDR_USD'].get(period,''),
             'reserve_gold_usd_m':res['RAFAGOLDNV_USD'].get(period,''),
             'reserve_other_usd_m':res['RAFAO_USD'].get(period,''),
             'official_usd_gel_month_end':usd.get(period,{}).get('rate',''),
             'official_usd_rate_valid_from':usd.get(period,{}).get('valid_from',''),
             'cpi_monthly_pct':cpi.get(period,''),
             'tibr_overnight_monthly_mean_pct':sum(x['tibr_overnight_pct'] for x in tibr if x['date'][:7]==period)/sum(x['date'][:7]==period for x in tibr),
             'auction_purchases_usd_m':'','auction_sales_usd_m':'','bmatch_purchases_usd_m':'','bmatch_sales_usd_m':'',
             'government_fx_usd_m':'','reserve_fx_valuation_usd_m':'','reserve_gold_valuation_usd_m':'','reserve_other_movements_usd_m':'',
             'intervention_reconciliation_status':'unavailable: transaction and valuation series missing'}
        rows.append(row)
    write_csv(OUT/'nbg_policy_monthly_2020_2024.csv',rows,list(rows[0]))
    write_csv(OUT/'nbg_policy_decisions_2008_onward.csv',events,list(events[0]))
    quarterly=[{'quarter':q,'current_account_usd_m':v,'bop_reserve_assets_usd_m':bop.get('BFRA_USD',{}).get(q,'')}
               for q,v in bop.get('BCA_USD',{}).items() if '2020-Q1'<=q<='2024-Q4']
    write_csv(OUT/'nbg_external_quarterly_2020_2024.csv',quarterly,list(quarterly[0]))
    manifest['usd_month_end_api']={'base_url':'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json/',
       'observations':usd,'errors':errors,'definition':'one dated official USD/GEL quote requested per calendar month end; effective date retained'}
    counts={k:sum(r[k]!='' for r in rows) for k in rows[0] if k!='month'}
    manifest['panel']={'period':'2020-01 to 2024-12','rows':len(rows),'nonmissing_counts':counts,
      'tibr_definition':'arithmetic monthly mean of published business-day TIBR overnight percentage rates (source decimals multiplied by 100); 1250 daily records separately',
      'cpi_definition':'national all-items previous-month=100, reported as percent change',
      'rate_definition':'effective policy rate on calendar month end; decisions retained separately',
      'reserves_definition':'official reserve asset stock, USD millions; change is stock difference, never intervention',
      'usd_definition':'official GEL per USD valid on requested month end, effective rate may originate earlier on non-business day',
      'bop_definition':'quarterly USD million current account and reserve asset flow; no monthly interpolation',
      'publication_lags':'NBG official FX fix announced by 17:00 for next day; reserve monthly publication near 5–7 of next month; BMatch approximately 25 days after month; contemporaneous historical release timestamps not in source files'}
    dictionary=[]
    specs={
      'policy_rate_end_pct':('policy_rate.xlsx','NBG policy rate in force on month end','percent','monthly from decision dates','decision date in separate file; effective next day'),
      'policy_decisions_n':('policy_rate.xlsx','number of committee decisions in calendar month','count','monthly from event dates','decision date recorded; zero is an observed count from complete rate table'),
      'official_reserves_usd_m':('reserves.xml','official reserve assets, end-month stock','USD millions','monthly','monthly release near fifth business day; historical timestamps unavailable'),
      'reserve_stock_change_usd_m':('reserves.xml','first difference of reserve stock, not FX intervention','USD millions','monthly','same as reserve stock'),
      'reserve_fx_usd_m':('reserves.xml','foreign currency component of reserve assets','USD millions','monthly','same as reserve stock'),
      'reserve_imf_usd_m':('reserves.xml','reserve position in IMF','USD millions','monthly','same as reserve stock'),
      'reserve_sdr_usd_m':('reserves.xml','SDR holdings component','USD millions','monthly','same as reserve stock'),
      'reserve_gold_usd_m':('reserves.xml','monetary gold component','USD millions','monthly','same as reserve stock'),
      'reserve_other_usd_m':('reserves.xml','other reserve assets','USD millions','monthly','same as reserve stock'),
      'official_usd_gel_month_end':('usd_month_end_api','official GEL per USD on requested calendar month end; valid-from retained','GEL/USD','monthly sample of dated daily API','official fix announced by 17:00, effective next day'),
      'cpi_monthly_pct':('group_cpi.xlsx','national all-items previous-month CPI relative minus 100','percent','monthly','Geostat monthly publication; historical dates not in workbook'),
      'tibr_overnight_monthly_mean_pct':('tibr.xlsx','arithmetic mean of available daily TIBR overnight rates','percent','monthly from daily','daily publication; historical release times unavailable'),
    }
    for field,(source,definition,unit,frequency,lag) in specs.items():
        src=manifest[source] if source!='usd_month_end_api' else manifest['usd_month_end_api']
        dictionary.append({'field':field,'source_url':src.get('source_url',src.get('base_url')),'source_sha256':src.get('sha256','per-response hashes in JSON manifest'),
          'definition':definition,'unit':unit,'frequency':frequency,'information_availability':lag,
          'observed_months':counts[field],'missing_months':60-counts[field],'structural_break_note':'2018 TIBR reform predates sample' if field.startswith('tibr') else ''})
    for field in ('auction_purchases_usd_m','auction_sales_usd_m','bmatch_purchases_usd_m','bmatch_sales_usd_m','government_fx_usd_m','reserve_fx_valuation_usd_m','reserve_gold_valuation_usd_m','reserve_other_movements_usd_m'):
        dictionary.append({'field':field,'source_url':'','source_sha256':'','definition':'not acquired; blank is not zero',
         'unit':'USD millions','frequency':'monthly intended','information_availability':'BMatch disclosed about 25 days after month; auction result within 15 minutes',
         'observed_months':0,'missing_months':60,'structural_break_note':'2020 BMatch introduction; transaction/valuation file not verified'})
    write_csv(OUT/'nbg_series_dictionary.csv',dictionary,list(dictionary[0]))
    (OUT/'nbg_source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'counts':counts,'usd_errors':errors,'policy_events':len(events),'quarterly':len(quarterly)},indent=2))
if __name__=='__main__':build()
