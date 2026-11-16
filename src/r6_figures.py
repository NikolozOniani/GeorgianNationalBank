"""Static R6 exhibits from committed results. Matplotlib 3.10.8."""
import argparse
import csv
import io
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/r6_2026_11_15'
plt.rcParams.update({'svg.hashsalt':'georgia-r6-v1','font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})


def build():
    curves=list(csv.DictReader((OUT/'liquidity_service_curves.csv').open()))
    fig,axes=plt.subplots(1,2,figsize=(12.5,5.5))
    for gold,call,color,label in [
        ('0.0','0.0','#185c78','Predetermined drains'),
        ('1.0','0.0','#607c36','Plus unavailable gold'),
        ('0.0','1.0','#b36a20','Plus full contingent calls'),
        ('1.0','1.0','#923844','Both additional stresses')]:
        rows=[r for r in curves if r['gold_unavailable_share']==gold and r['contingent_called_share']==call and r['incremental_liquid_share']=='1.0']
        axes[0].plot([float(r['additional_disjoint_need_usdm'])/1000 for r in rows],[float(r['shortfall_avoided_usdm']) for r in rows],label=label,color=color,lw=2)
    axes[0].set(title='Liquidity service of an extra USD 100m',xlabel='Additional, disjoint FX need (USD billion)',ylabel='Shortfall avoided (USD million)',xlim=(0,6),ylim=(-3,107))
    axes[0].legend(loc='lower right',fontsize=8,frameon=False)
    rows=list(csv.DictReader((OUT/'hazard_thresholds.csv').open()))
    rows=[r for r in rows if r['mechanism']=='rolling GEL CD' and float(r['gel_per_usd_change_pct'])==0 and float(r['assumed_resource_cost_share'])==1]
    values=[float(r['required_annual_hazard_reduction_pp']) for r in rows]
    bars=axes[1].bar([f"{float(r['crisis_loss_gdp_share'])*100:.0f}% of GDP" for r in rows],values,color='#185c78',width=.55)
    axes[1].bar_label(bars,labels=[f'{v:.3f} pp' for v in values],padding=5)
    axes[1].set(title='One-year cost-equivalent insurance hurdle',xlabel='Assumed loss if a crisis occurs',ylabel='Required reduction in annual probability (pp)',ylim=(0,.26))
    for ax in axes: ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('Reserve benefits depend on the stress and financing assumptions',fontsize=15,x=.05,ha='left')
    fig.text(.05,.075,'Left: end-2025 public liquidity schedule; fully liquid USD 100m addition; no alternative financing.',fontsize=9)
    fig.text(.05,.04,'Right: unchanged FX, USD 4.22m annual CD-funded cost. Cost-equivalent scenarios, not estimated policy benefits.',fontsize=9)
    fig.subplots_adjust(left=.07,right=.98,top=.85,bottom=.21,wspace=.29)
    stream=io.StringIO();fig.savefig(stream,format='svg',metadata={'Date':None,'Creator':'R6 scientific exhibits; matplotlib 3.10.8'})
    return fig,'\n'.join(line.rstrip() for line in stream.getvalue().splitlines())+'\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--preview',type=Path)
    args=parser.parse_args();fig,text=build();path=OUT/'conditional_benefits.svg'
    if args.check:
        if path.read_text()!=text: raise ValueError('Figure differs; use pinned plotting version')
    else: path.write_text(text)
    if args.preview: fig.savefig(args.preview,dpi=130)
    plt.close(fig)


if __name__=='__main__': main()
