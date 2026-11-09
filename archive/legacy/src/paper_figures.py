"""Figures from committed annual accounting outputs."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/paper'


def main():
    dest=OUT/'figures';dest.mkdir(exist_ok=True)
    with (OUT/'annual_results.csv').open() as f:r=list(csv.DictReader(f))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8,4.7))
    for offset,key,label,color in [(-.25,'monetary_interest_income_gel_m','Interest income','#164b68'),
                                    (0,'monetary_interest_expense_gel_m','Interest expense','#aa4d2b'),
                                    (.25,'monetary_net_interest_gel_m','Net interest','#59816c')]:
        vals=[float(x[key]) for x in r]
        bars=ax.bar([i+offset for i in range(2)],vals,.23,label=label,color=color)
        ax.bar_label(bars,labels=[f'{v:.1f}' for v in vals],padding=3,fontsize=9)
    ax.set_xticks([0,1],[x['year'] for x in r]);ax.set_ylabel('GEL million');ax.set_ylim(0,650)
    ax.set_title('NBG monetary-operation interest: expense and revenue',loc='left',weight='bold',pad=14)
    ax.legend(frameon=False,loc='upper left',fontsize=9);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.text(.08,.02,'NBG 2024 accounts, comparative years. Accrued interest; not a net welfare calculation.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(dest/'operation_accounts.png',dpi=180);plt.close(fig)


if __name__=='__main__':main()
