"""Reproduce R5 public aggregates; no household records are written to disk outside temporary extraction."""
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import openpyxl
import pyreadstat

from r5_cpi import SERIES, select_series

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/r5_2026_11_13'
LEGACY = ROOT / 'archive/legacy/reports'
GROUP_SHA = '5b2df9ab880ff87e07e3329b35826c301f3c318f35aa1313041ad1b55946b6b7'
GROUPS = {11:'diary_food', 12:'diary_soft_drinks', 21:'diary_alcohol', 3:'tansacmeli',
          5:'saojaxo', 6:'samedicino', 4:'energia', 7:'transporti', 10:'ganatleba'}
APPROX = {4, 5}
MIXED = 'sursati__sasmeli__Tambaqo'
TOTAL = 'MTlianimoxmareba_'
RANK = 'MTlianimoxmareba_EqAdScale'
REMIT = 'Ucxoetidan'


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prices(path):
    require(sha(path)==GROUP_SHA, 'Group CPI vintage mismatch')
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb['Georgia'].values)
    wb.close()
    indices = {}
    year = None
    months = 'I II III IV V VI VII VIII IX X XI XII'.split()
    for j, value in enumerate(rows[2]):
        if isinstance(value,int):
            year = value
        if year and rows[3][j] in months and 2020 <= year <= 2025:
            key = f'{year}-{1+months.index(rows[3][j]):02}'
            require(key not in indices, 'duplicate CPI month '+key)
            indices[key] = j
    records = select_series(rows[4:])
    require(GROUPS.keys()==records.keys(), 'CPI and household crosswalk disagree')
    rates = pd.DataFrame({k:{t:row[j] for t,j in indices.items()}
                          for k,(_,row) in records.items()},dtype=float).sort_index()/100
    expected=pd.period_range('2020-01','2025-12',freq='M').astype(str)
    require(rates.index.equals(expected) and np.isfinite(rates).all().all()
            and (rates>0).all().all(), 'CPI month coverage')
    return rates, {k:number for k,(number,_) in records.items()}


def household(raw, year, rates):
    archive = raw / f'{year}.zip'
    lock = next(r for r in json.loads((LEGACY/'release_integrity.json').read_text()) if r['name']==archive.name)
    require(sha(archive)==lock['sha256'], 'Survey hash mismatch')
    with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory() as temp:
        require(z.testzip() is None, 'Bad survey CRC')
        def table(name):
            members = [n for n in z.namelist() if Path(n).name.lower()==name+'.sav']
            require(len(members)==1, name)
            p = Path(temp)/'table.sav'
            p.write_bytes(z.read(members[0]))
            return pyreadstat.read_sav(p)[0]
        d = table('sysschedule').set_index('UID',verify_integrity=True)
        for name in ('tblexpenditures','familysize','tblincomes'):
            other = table(name).set_index('UID',verify_integrity=True)
            require(d.index.difference(other.index).empty and other.index.difference(d.index).empty, name+' UID support')
            d = d.join(other,validate='one_to_one')
        items = table('conspurch_03')
    required = ['Weights','DiaryID','UrbanOrRural','Pensioner_age_man','Pensioner_age_Woman',REMIT,TOTAL,RANK,
                'Saxsrebi_Sul','MTlianixarjebi_',MIXED,'sxva','Arafuladi_moxm_','fuladixarjebi','samomxmXarjebi',
                'Fuladisaxsrebi','ArafuladiMoxmareba'] + list(GROUPS.values())[3:]
    require(np.isfinite(d[required]).all().all() and (d[required]>=0).all().all(), 'missing/negative survey field')
    require((d[['Weights',TOTAL,RANK,'Eq_Skale_0_6']]>0).all().all() and d.index.notna().all(), 'nonpositive base')
    require(d.QuartNo.notna().all() and d.QuartNo.nunique()==4, 'missing quarter or wrong number of quarters')
    require(set(d.UrbanOrRural)=={1,2},'residence codes')
    t = pd.to_datetime(d.MonthYear).dt.strftime('%Y-%m')
    require(set(t)=={f'{year}-{i:02}' for i in range(1,13)},'survey months')
    require(not d.reset_index().duplicated(['DiaryID','QuartNo']).any(), 'repeated household within quarter')
    require(items.UID.isin(d.index).all() and np.isfinite(items[['ProductCode','Paid']]).all().all() and not items.duplicated(['UID','ProductCode']).any()
            and (items.Paid>=0).all() and (items.ProductCode%1==0).all(), 'invalid diary fields')
    items['prefix'] = items.ProductCode.astype(int)//1000
    for code in (11,12,21):
        named = items[items.prefix==code].groupby('UID').Paid.sum()
        d[GROUPS[code]] = named.reindex(d.index,fill_value=0)
    d['mixed_remainder'] = d[MIXED]-d[list(GROUPS.values())[:3]].sum(axis=1)
    require(d.mixed_remainder.min()>-1e-7,'diary exceeds mixed cash field')
    def identity(left,right):
        require(np.allclose(left,right,atol=1e-7,rtol=0),'accounting identity')
    identity(d[RANK],d[TOTAL]/d.Eq_Skale_0_6)
    cash = [MIXED,'sxva']+list(GROUPS.values())[3:]
    identity(d[cash].sum(axis=1), d.samomxmXarjebi)
    identity(d.samomxmXarjebi+d.Arafuladi_moxm_,d[TOTAL])
    identity(d.fuladixarjebi+d.Arafuladi_moxm_,d.MTlianixarjebi_)
    identity(d.Fuladisaxsrebi+d.ArafuladiMoxmareba,d.Saxsrebi_Sul)
    unmatched = d.mixed_remainder + d.sxva + d.Arafuladi_moxm_
    identity(d[list(GROUPS.values())].sum(axis=1)+unmatched,d[TOTAL])
    d['unmatched'] = unmatched
    d['approx'] = d[[GROUPS[c] for c in APPROX]].sum(axis=1)
    levels = rates.cumprod()
    for c,field in GROUPS.items():
        # Interview month proxies for the monthly-average expenditure reference prices.
        d['dec_'+field] = d[field]*levels.loc[f'{year}-12',c]/t.map(levels[c])
    d['matched_dec'] = d[['dec_'+f for f in GROUPS.values()]].sum(axis=1)
    d['saving'] = .0025*d.matched_dec
    d['cash_loss'] = .01*d[REMIT]
    d['saving_survey'] = .0025*(d[TOTAL]-d.unmatched)
    d['two_channel_survey'] = d.saving_survey-d.cash_loss
    d['recipient'] = np.where(d[REMIT]>0,'positive','zero')
    d['residence'] = d.UrbanOrRural.map({1:'urban',2:'rural'})
    d['pension_age'] = np.where(d.Pensioner_age_man+d.Pensioner_age_Woman>0,'yes','no')
    ordered = d.sort_values([RANK,'UID'])
    d['quintile'] = np.ceil(5*(ordered.Weights.cumsum()-.5*ordered.Weights)/ordered.Weights.sum()).astype(int)
    return d,dict(year=year,records=len(d),diaries=d.DiaryID.nunique(),diary_product_rows=len(items),
                  unidentified_product_rows=int((~items.prefix.isin([11,12,21])).sum()),sha256=lock['sha256'])


def weighted(d, field):
    return np.average(d[field],weights=d.Weights)


def cluster_se(d, field):
    """Ratio-mean linearization with DiaryID clusters, conditional on group membership."""
    mean=weighted(d,field)
    u=(d.Weights*(d[field]-mean)).groupby(d.DiaryID).sum()/d.Weights.sum()
    return np.sqrt(len(u)/(len(u)-1)*sum(u*u))


def groups(d, year):
    result=[]
    cats=[]
    for name in ('all','quintile','residence','pension_age','recipient'):
        subsets=[('all',d)] if name=='all' else d.groupby(name,sort=True)
        for label,g in subsets:
            tot=weighted(g,TOTAL)
            row=dict(year=year,group=name,level=label,records=len(g),diaries=g.DiaryID.nunique(),
                     weight_sum=g.Weights.sum(),consumption_gel=tot,unmatched_pct=100*weighted(g,'unmatched')/tot,
                     strict_unmatched_pct=100*(weighted(g,'unmatched')+weighted(g,'approx'))/tot,
                     unmatched_mixed_gel=weighted(g,'mixed_remainder'),misc_gel=weighted(g,'sxva'),noncash_gel=weighted(g,'Arafuladi_moxm_'),
                     matched_dec_gel=weighted(g,'matched_dec'),saving_025_dec_gel=weighted(g,'saving'),
                     saving_025_survey_gel=weighted(g,'saving_survey'),
                     two_channel_all_usd_survey_gel=weighted(g,'two_channel_survey'),
                     two_channel_se=cluster_se(g,'two_channel_survey'),
                     saving_se=cluster_se(g,'saving'),remittances_gel=weighted(g,REMIT),
                     loss_all_usd_gel=weighted(g,'cash_loss'),loss_se=cluster_se(g,'cash_loss'),
                     saving_025_pct_of_matched_dec=.25,
                     saving_025_survey_price_pct_total=.25*(1-weighted(g,'unmatched')/tot))
            result.append(row)
            for c,f in GROUPS.items():
                cats.append(dict(year=year,group=name,level=label,cpi=c,cpi_level=SERIES[c][0],survey_gel=weighted(g,f),
                                 dec_gel=weighted(g,'dec_'+f),share_pct=100*weighted(g,f)/tot))
    return result,cats


def checks(d,year):
    out=[]
    def anchor(group,field,published):
        g=d if group=='all' else d[d.residence==group]
        val=weighted(g,field)
        out.append(dict(year=year,group=group,field=field,hies_gel=val,published_gel=published,gap_gel=val-published))
        require(abs(val-published)<.05,f'official discrepancy {year} {group} {field}: {val} vs {published}')
    anchor('all','MTlianixarjebi_',1735.7 if year==2024 else 1936.3)
    anchor('all','Saxsrebi_Sul',1895.7 if year==2024 else 2131.5)
    if year==2024:
        for label,con,rem in [('all',1306.0,60.8),('urban',1382.4,67.6),('rural',1175.4,49.2)]:
            anchor(label,TOTAL,con)
            anchor(label,REMIT,rem)
        for f,val in zip([MIXED,'tansacmeli','saojaxo','samedicino','energia','transporti','ganatleba','sxva','Arafuladi_moxm_'],
                         [462.6,64.7,57,133.4,140.7,131.3,34.2,188.7,93.4]):
            anchor('all',f,val)
    return out


def diagnostics(rates):
    """Pre-episode descriptive fit. Month fixed effects, signed FX movements and broad dollar."""
    base=ROOT/'data/derived/episode_2026_11_09'
    p=pd.read_csv(base/'official_fx_daily.csv')
    monthly=p.groupby(p.date.str[:7]).usd_gel.mean()
    dollar=pd.read_csv(base/'broad_dollar_daily.csv')
    changes=np.log(monthly).diff()
    b=np.log(dollar.groupby(dollar.date.str[:7])['index'].mean()).diff()
    keep=rates.loc['2020-01':'2024-12'].index
    out=[]
    for code in GROUPS:
        pi=100*np.log(rates[code])
        for lag in (0,1,3):
            dx=100*changes.shift(lag)
            frame=pd.DataFrame(dict(y=pi,app=dx.clip(upper=0),dep=dx.clip(lower=0),
                                    dollar=100*b.shift(lag),lag_pi=pi.shift(1))).loc[keep].dropna()
            months=pd.get_dummies(frame.index.str[-2:],drop_first=True,dtype=float)
            x=np.column_stack([np.ones(len(frame)),frame[['app','dep','dollar','lag_pi']],months])
            coef,_,rank,_=np.linalg.lstsq(x,frame.y,rcond=None)
            require(rank==x.shape[1], 'diagnostic rank')
            out.append(dict(code=code,cpi_level=SERIES[code][0],lag_months=lag,first=frame.index[0],last=frame.index[-1],n=len(frame),
                            appreciation_months=sum(frame.app<0),depreciation_months=sum(frame.dep>0),
                            appreciation_slope=coef[1],depreciation_slope=coef[2]))
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--release-dir',required=True,type=Path)
    parser.add_argument('--group-cpi',required=True,type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    rates,source_rows=prices(args.group_cpi)
    exposure=[]; categories=[]; anchors=[]; audit=[]
    for year in (2024,2025):
        d,meta=household(args.release_dir,year,rates)
        audit.append(meta)
        anchors.extend(checks(d,year))
        a,b=groups(d,year)
        exposure+=a
        categories+=b
    outputs={'groups':exposure,'category_exposures':categories,'geostat_checks':anchors,
             'survey_validation':audit,'price_diagnostics':diagnostics(rates),
             'crosswalk':[dict(cpi=k,cpi_level=SERIES[k][0],sheet='Georgia',source_row=source_rows[k],label=SERIES[k][1],survey=v,match='approximate' if k in APPROX else 'direct') for k,v in GROUPS.items()]}
    for name,data in outputs.items():
        content=pd.DataFrame(data).to_csv(index=False,float_format='%.8f').encode()
        path=REPORT/(name+'.csv')
        if args.check:
            require(path.read_bytes()==content,name+' reproduction mismatch')
        else:
            path.write_bytes(content)


if __name__=='__main__':
    main()
