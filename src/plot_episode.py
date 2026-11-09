"""Descriptive source-data figure; no fitted or counterfactual exchange rate."""
import csv
import datetime as dt
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/acquisition_2026_11_09'


def main():
    with (REPORT/'monthly_policy_panel.csv').open() as f:
        rows=[r for r in csv.DictReader(f) if r['month']>='2025-01']
    dates=[dt.datetime.strptime(r['month'],'%Y-%m') for r in rows]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'georgia-reserve-episode-20261109'})
    fig,ax=plt.subplots(3,1,figsize=(10,8.5),sharex=True,layout='constrained')
    net=[float(r['net_market_purchases_usdm']) if r['net_market_purchases_usdm'] else float('nan') for r in rows]
    ax[0].bar(dates,net,width=21,color=['#a24337' if v<0 else '#276275' for v in net])
    ax[0].axhline(0,color='#777',lw=.7);ax[0].set_ylabel('USD million');ax[0].set_title('Monthly net market purchases by NBG',loc='left',fontweight='bold')
    ax[0].annotate('October not yet disclosed',xy=(dates[-1],50),xytext=(-160,50),textcoords='offset points',arrowprops={'arrowstyle':'->','color':'#555'},fontsize=9,bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
    total=[float(r['reserves_end_usdm'])/1000 for r in rows];gold=[float(r['gold_end_usdm'])/1000 for r in rows]
    ax[1].plot(dates,total,label='Gross reserves',color='#276275',lw=2)
    ax[1].plot(dates,gold,label='Gold component at market value',color='#aa8124',lw=1.8)
    ax[1].set_ylabel('USD billion');ax[1].set_title('End-month reserve stocks',loc='left',fontweight='bold');ax[1].legend(frameon=False,loc='upper left',fontsize=9)
    ax[2].plot(dates,[float(r['official_usd_gel_end']) for r in rows],color='#276275',lw=2)
    ax[2].set_ylabel('GEL per USD');ax[2].set_title('Observed end-month official exchange rate',loc='left',fontweight='bold')
    ax[2].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10]));ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    for a in ax:
        a.spines[['top','right']].set_visible(False);a.grid(axis='y',alpha=.18);a.set_axisbelow(True)
    fig.suptitle('Georgia: observed reserve-purchase episode, 2025–2026',fontsize=15,fontweight='bold')
    fig.supxlabel('Sources: NBG statistical tables. Vintage: 9 November 2026.\nNet purchases are not gross purchases; reserve stocks include valuation and other flows. These plots do not identify a policy effect.',fontsize=9)
    fig.savefig(REPORT/'episode_observations.svg',metadata={'Date':None,'Creator':'GeorgianNationalBank research code'})
    svg=REPORT/'episode_observations.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(REPORT/'episode_observations.png',dpi=170,metadata={'Software':'GeorgianNationalBank research code'})


if __name__=='__main__':main()
