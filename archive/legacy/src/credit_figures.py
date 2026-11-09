"""Publication figures; run after credit_analysis.py. Matplotlib only."""
import csv
import datetime as dt
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/peer_review'


def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))


def main():
    dest=OUT/'figures';dest.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'axes.titleweight':'bold','savefig.facecolor':'white'})
    d=read('credit_monthly_2020_2024.csv');dates=[dt.datetime.strptime(r['month'],'%Y-%m') for r in d]
    fig,ax=plt.subplots(2,1,figsize=(9,6),sharex=True)
    for a,series in zip(ax,[['hh_all_gel_new_housing_rate','hh_all_gel_realestate_secured_outstanding_rate'],
                            ['hh_all_gel_new_consumer_rate','hh_all_gel_deposit_term_rate']]):
        labels={'hh_all_gel_new_housing_rate':'New housing-purpose loans',
                'hh_all_gel_realestate_secured_outstanding_rate':'Outstanding real-estate-secured loans',
                'hh_all_gel_new_consumer_rate':'New consumer loans','hh_all_gel_deposit_term_rate':'Outstanding term deposits'}
        for key,color in zip(series,['#164b68','#aa4d2b']):a.plot(dates,[float(r[key]) for r in d],label=labels[key],color=color,lw=2)
        a.set_ylabel('Annual contractual rate (%)');a.grid(alpha=.2);a.legend(frameon=False,loc='best',fontsize=9)
    ax[0].set_title('GEL household rates followed different paths, 2020-2024',loc='left',pad=14)
    ax[1].xaxis.set_major_locator(mdates.YearLocator());ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.text(.08,.015,'NBG LMR, L3.8.1, D3.23. Changing portfolios; not same-borrower repricing or causal estimates.',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(dest/'observed_rates.png',dpi=180);plt.close(fig)
    p=read('indexed_contract_monthly.csv');dates=[dt.datetime.strptime(r['month'],'%Y-%m') for r in p]
    fig,ax=plt.subplots(figsize=(9,4.6))
    ax.plot(dates,[float(r['payment_gel']) for r in p],label='Observed policy path + assumed 3 pp margin',color='#164b68',lw=2.5)
    ax.plot(dates,[float(r['reference_payment_gel']) for r in p],label='8% held policy reference + 3 pp margin',color='#777777',ls='--',lw=2)
    ax.set_title('Synthetic indexed contract: payment exposure, not measured household loss',loc='left',fontsize=12,pad=14)
    ax.set_ylabel('Monthly payment (GEL)');ax.set_ylim(980,1290);ax.grid(alpha=.2);ax.legend(frameon=False,fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.text(.08,.025,'GEL 100,000; 20 years initially; monthly resets; no fees/prepayment/default. Accounting reference only.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(dest/'indexed_contract.png',dpi=180);plt.close(fig)
    s=read('table3_reset_sensitivity.csv');fig,ax=plt.subplots(figsize=(8,4.5))
    for term,offset,color in [(120,-.12,'#aa4d2b'),(240,.12,'#164b68')]:
        for i,reset in enumerate([1,3,6,12]):
            values=[float(r['extra_payments_48m_gel']) for r in s if int(r['term_months'])==term and int(r['reset_months'])==reset and float(r['pass_through'])==1]
            lo,hi=min(values),max(values);mid=(lo+hi)/2
            ax.errorbar(i+offset,mid,yerr=[[mid-lo],[hi-mid]],fmt='none',capsize=5,color=color,label=f'{term//12}-year initial term' if i==0 else None)
    ax.set_xticks(range(4),['Monthly','Quarterly','Half-yearly','Annual']);ax.set_ylabel('Additional payments, 2021-2024 (GEL)')
    ax.set_title('Reset-calendar sensitivity for a synthetic GEL 100,000 loan',loc='left',fontsize=12,pad=14)
    ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,loc='upper left',fontsize=9)
    fig.text(.08,.025,'Ranges vary reset phase; they are not confidence intervals. Full index linkage; reference policy rate 8%.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(dest/'reset_sensitivity.png',dpi=180);plt.close(fig)


if __name__=='__main__':main()
