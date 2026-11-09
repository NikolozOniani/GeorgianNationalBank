"""2017 fixed-basket *partial* price exposure. No policy or welfare attribution."""
import csv, hashlib, json, pathlib, tempfile, urllib.request, zipfile
import numpy as np
import pandas as pd
import pyreadstat
import openpyxl
from validation import chain_monthly_indices

ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
REPORT=ROOT/'reports'
FIG=ROOT/'figures'
GROUP_URL='https://www.geostat.ge/media/83812/Consumer-Price-Indices-(Previous-month=100).xlsx'
GROUP_SHA='5b2df9ab880ff87e07e3329b35826c301f3c318f35aa1313041ad1b55946b6b7'
# Survey labels in the SPSS metadata, matched to Geostat's CPI group labels.
# The large mixed food/beverages/tobacco and miscellaneous fields stay unmatched.
CROSSWALK={
 'tansacmeli':(3,'Clothing and footwear','direct'),
 'saojaxo':(5,'Furnishings, household equipment and routine maintenance of the house','approximate: household goods may not include all maintenance'),
 'samedicino':(6,'Health','direct'),
 'energia':(45,'Electricity, gas and other fuels','direct for fuel/electricity; survey wording may exclude gas'),
 'transporti':(7,'Transport','direct'),
 'ganatleba':(10,'Education','direct'),
}
UNMATCHED={'sursati__sasmeli__Tambaqo':'Mixed food, beverages, tobacco spans CPI 1 and 2',
           'sxva':'Other consumption spans several CPI groups',
           'Arafuladi_moxm_':'Noncash consumption lacks category allocation'}
ALL_CASH=list(CROSSWALK)+list(UNMATCHED)[:2]

def sav(z,table):
    name=next(n for n in z.namelist() if n.endswith('/'+table+'.sav'))
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d)/'table.sav';p.write_bytes(z.read(name))
        return pyreadstat.read_sav(str(p))

def group_indices(path):
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    s=w['Georgia']; rows=list(s.values); years={}
    year=None; count=0
    for j,v in enumerate(rows[2]):
        if isinstance(v,int):year=v;count=0
        if year is not None and rows[3][j] in ('I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'):
            years[(year,count+1)]=j;count+=1
    codes={int(r[1]):r for r in rows[4:] if isinstance(r[0],int) and isinstance(r[1],int)}
    missing=[]; rates={}
    for code in [*{v[0] for v in CROSSWALK.values()},0]:
        r=codes.get(code) if code else rows[4]
        if r is None:raise ValueError(f'CPI group missing: {code}')
        vals=[]
        for year in (2018,2019):
            for month in range(1,13):
                j=years.get((year,month));v=r[j] if j is not None else None
                if not isinstance(v,(int,float)) or v<=0:missing.append([code,year,month,v])
                else:vals.append(v/100)
        if not missing or all(x[0]!=code for x in missing):
            rates[code]={2018:chain_monthly_indices([100*v for v in vals[:12]]),2019:chain_monthly_indices([100*v for v in vals])}
    return rates,{'date_start':min(years),'date_end':max(years),'missing_required':missing,'period':'December 2017 to December 2018/2019','total_cpi':rates.get(0)}

def wmean(a,w):return float(np.sum(a*w)/np.sum(w))
def quantile_groups(resource,weight):
    order=np.argsort(resource,kind='stable'); cum=np.cumsum(weight[order]); q=np.empty(len(resource),int)
    q[order]=np.minimum(5,np.searchsorted(np.arange(1,6)*cum[-1]/5,cum,side='left')+1)
    return q

def run():
    path=RAW/'group_cpi.xlsx'
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(GROUP_URL,timeout=90).read())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==GROUP_SHA,'Geostat group CPI vintage changed'
    assert (RAW/'release/2017.zip').exists()
    with zipfile.ZipFile(RAW/'release/2017.zip') as z:
        assert z.testzip() is None
        sched,sm=sav(z,'sysschedule'); expend,em=sav(z,'tblexpenditures'); fam,fm=sav(z,'familysize'); inc,im=sav(z,'tblincomes')
    for name,d in [('schedule',sched),('expenditures',expend),('family',fam),('income',inc)]:
        assert len(d)==11590 and d.UID.is_unique and d.UID.notna().all(),name
    d=sched.merge(expend,on='UID',validate='one_to_one').merge(fam,on='UID',validate='one_to_one').merge(inc,on='UID',validate='one_to_one')
    assert d.MonthYear.min().year==2017 and d.MonthYear.max().year==2017
    assert (d.Weights>0).all() and d.Weights.notna().all() and (d.MTlianimoxmareba_>0).all()
    assert (d[ALL_CASH].sum(axis=1)-d.samomxmXarjebi).abs().max()<1e-7
    assert (d.samomxmXarjebi+d.Arafuladi_moxm_-d.MTlianimoxmareba_).abs().max()<1e-7
    assert (d.fuladixarjebi+d.Arafuladi_moxm_-d.MTlianixarjebi_).abs().max()<1e-7
    assert (d.ShemosavaliDaTransf+d.ArafuladiMoxmareba-d.Shemosavalisul).abs().max()<1e-7
    assert (d.Fuladisaxsrebi+d.ArafuladiMoxmareba-d.Saxsrebi_Sul).abs().max()<1e-7
    for c in ALL_CASH+['Arafuladi_moxm_','PensStipDaxm','SesxAnDanazog']:
        assert d[c].notna().all() and (d[c]>=0).all(),c
    rates,cpi=group_indices(path)
    assert not cpi['missing_required']
    w=d.Weights.to_numpy();total=d.MTlianimoxmareba_.to_numpy()
    matched=d[list(CROSSWALK)].sum(axis=1).to_numpy();unmatched=total-matched
    assert (unmatched>=-1e-6).all()
    q=quantile_groups(d.MTlianimoxmareba_EqAdScale.to_numpy(),w)
    d['quintile']=q
    d['pensioner']=np.where((d.Pensioner_age_man+d.Pensioner_age_Woman)>0,'pensioner','no pensioner')
    d['residence']=d.UrbanOrRural.map({1.0:'urban',2.0:'rural'})
    assert d.residence.notna().all()
    REPORT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
    with (REPORT/'crosswalk_2017_v1.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['survey_variable','survey_label','cpi_group_code','cpi_label','status_note'])
        for col,(code,label,note) in CROSSWALK.items():writer.writerow([col,em.column_names_to_labels[col],code,label,note])
        for col,note in UNMATCHED.items():writer.writerow([col,em.column_names_to_labels[col],'','','unmatched: '+note])
    results=[]
    rng=np.random.default_rng(20261108)
    cluster_index=pd.factorize(d.DiaryID)[0]
    nclusters=cluster_index.max()+1
    draws=rng.multinomial(nclusters,[1/nclusters]*nclusters,size=300)
    for year in (2018,2019):
        change=sum(d[col].to_numpy()*rates[code][year] for col,(code,_,_) in CROSSWALK.items())
        strict=sum(d[col].to_numpy()*rates[code][year] for col,(code,_,note) in CROSSWALK.items() if note=='direct')
        d['contribution_pp']=100*change/total
        d['matched_rate_pct']=100*change/matched
        d['unmatched_pct']=100*unmatched/total
        for group,labels in [('all',np.array(['all']*len(d))),('quintile',q.astype(str)),('residence',d.residence.to_numpy()),('pensioner',d.pensioner.to_numpy())]:
            for label in sorted(set(labels)):
                mask=labels==label;ww=w[mask]
                estimates=[]
                x=d.contribution_pp.to_numpy()[mask]; c=cluster_index[mask]
                for draw in draws:
                    bw=ww*draw[c]
                    estimates.append(wmean(x,bw) if bw.sum()>0 else np.nan)
                lo,hi=np.nanpercentile(estimates,[2.5,97.5])
                results.append({'end_year':year,'group':group,'level':label,'records':int(mask.sum()),'weighted_households_quarter_sum':float(ww.sum()),
                    'matched_expenditure_share_pct':100*wmean(matched[mask]/total[mask],ww),
                    'direct_only_expenditure_share_pct':100*wmean(d[[col for col,(_,_,note) in CROSSWALK.items() if note=='direct']].sum(axis=1).to_numpy()[mask]/total[mask],ww),
                    'unmatched_expenditure_share_pct':100*wmean(unmatched[mask]/total[mask],ww),
                    'partial_contribution_pp':wmean(x,ww),'bootstrap_low_pp':lo,'bootstrap_high_pp':hi,
                    'direct_only_contribution_pp':100*wmean((strict/total)[mask],ww),
                    'matched_basket_rate_pct':wmean(d.matched_rate_pct.to_numpy()[mask],ww)})
    pd.DataFrame(results).to_csv(REPORT/'pilot2017_exposure.csv',index=False,float_format='%.6f')
    summary={'sample_rows':len(d),'unique_diary_ids':int(d.DiaryID.nunique()),'months':sorted(d.MonthYear.dt.strftime('%Y-%m').unique()),
      'weight_sum_four_quarters':float(w.sum()),'weighted_mean_total_expenditure_gel':wmean(d.MTlianixarjebi_.to_numpy(),w),
      'geostat_published_2017_total_expenditure_gel':1093.0,'weighted_mean_consumption_gel':wmean(total,w),
      'weighted_mean_total_cash_and_noncash_inflows_gel':wmean(d.Saxsrebi_Sul.to_numpy(),w),
      'geostat_published_2017_total_income_gel':1110.7,
      'income_fields':im.column_names_to_labels,'cpi':cpi,'group_cpi_url':GROUP_URL,'group_cpi_sha256':GROUP_SHA,
      'survey_sha256':hashlib.sha256((RAW/'release/2017.zip').read_bytes()).hexdigest(),
      'design':'Household-quarter UID; DiaryID repeats across quarters. Weights positive; PSU and strata absent from released schedule. Intervals are 300 seeded DiaryID cluster bootstrap draws, an exploratory approximation, not design-based confidence intervals.'}
    (REPORT/'pilot2017_validation.json').write_text(json.dumps(summary,indent=2,default=str)+'\n')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    p=pd.DataFrame(results);a=p[(p.end_year==2018)&(p.group=='quintile')].sort_values('level')
    fig,ax=plt.subplots(figsize=(7,4));xx=np.arange(5);ax.bar(xx-.19,a.direct_only_contribution_pp,width=.38,color='#6796ac',label='Direct matches only')
    ax.bar(xx+.19,a.partial_contribution_pp,width=.38,color='#245c82',label='Including two approximate matches')
    ax.set_xticks(xx,a.level);ax.legend(frameon=False,fontsize=8)
    ax.set(xlabel='2017 equivalized consumption quintile (households)',ylabel='Matched-category contribution (percentage points)',title='2017 basket, observed price change through Dec 2018')
    ax.axhline(0,color='black',lw=.7);fig.tight_layout();fig.savefig(FIG/'pilot2017_partial_exposure.png',dpi=180);plt.close(fig)
    print(p.to_string(index=False));print(json.dumps(summary,indent=2,default=str)[:1500])
if __name__=='__main__':run()
