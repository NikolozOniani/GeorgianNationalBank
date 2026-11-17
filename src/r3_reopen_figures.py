"""Diagnostic exhibits: no preferred counterfactual path is released."""
import argparse,csv,io
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/r3_reopen_2026_11_16'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'r3-reopen-rejected-v1','axes.spines.top':False,'axes.spines.right':False})


def figure():
    rows=list(csv.DictReader((OUT/'candidate_paths.csv').open()));comparison=list(csv.DictReader((OUT/'model_comparison.csv').open()))
    fig,ax=plt.subplots(1,2,figsize=(12.5,5.6));primary=[r for r in rows if r['spec']=='A11_col4'];x=list(range(21))
    ax[0].plot(x,[float(r['observed_gel_per_usd']) for r in primary],label='Observed GEL/USD',color='#173951',lw=2.4)
    for spec,label,color in [('A11_col4','Primary: failed stability gate','#b23d3b'),('zero_kernel','Zero direct-effect diagnostic','#73824b'),('reversed_kernel','Reversed-effect diagnostic','#9a7aaf')]:
        values=[float(r['candidate_gel_per_usd']) for r in rows if r['spec']==spec]
        ax[0].plot(x,values,label=label,color=color,ls='--',lw=1.8)
    ax[0].set_xticks([0,5,11,17,20],['Jan 25','Jun 25','Dec 25','Jun 26','Sep 26']);ax[0].set(ylabel='GEL per USD',title='Candidate paths: rejected for inference')
    ax[0].legend(fontsize=8,frameon=False,loc='lower left')
    labels=['Random walk','Primary','Zero direct effect','Reversed effect'];values=[1]+[float(next(r['rmse_over_random_walk'] for r in comparison if r['spec']==s)) for s in ['A11_col4','zero_kernel','reversed_kernel']]
    bars=ax[1].barh(labels,values,color=['#173951','#b23d3b','#73824b','#9a7aaf'],height=.55)
    ax[1].bar_label(bars,labels=[f'{v:.3f}' for v in values],padding=4)
    ax[1].axvline(1.2,color='#666666',ls=':',lw=1);ax[1].set(xlim=(0,1.3),xlabel='Forecast RMSE / random-walk RMSE',title='Predictive fit does not identify the effect')
    ax[1].invert_yaxis()
    for a in ax:a.grid(alpha=.15);a.set_axisbelow(True)
    fig.suptitle('R3 reopening: the tested model does not pass the release gate',x=.05,ha='left',fontsize=14)
    fig.text(.05,.085,'Monthly paths depend on assumed external response and estimated policy rules. They are not an empirical range.',fontsize=9)
    fig.text(.05,.045,'Only 149/199 block resamples are admissible (74.9%; required 90%). Holdout: January 2023–December 2024.',fontsize=9)
    fig.subplots_adjust(left=.07,right=.97,top=.85,bottom=.22,wspace=.4)
    buffer=io.StringIO();fig.savefig(buffer,format='svg',metadata={'Date':None,'Creator':'R3 diagnostic model experiment'})
    return fig,'\n'.join(l.rstrip() for l in buffer.getvalue().splitlines())+'\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--preview',type=Path);args=parser.parse_args()
    fig,text=figure();dest=OUT/'rejected_model_diagnostics.svg'
    if args.check:
        if dest.read_text()!=text:raise ValueError('Figure differs')
    else:dest.write_text(text)
    if args.preview:fig.savefig(args.preview,dpi=130)
    plt.close(fig)
