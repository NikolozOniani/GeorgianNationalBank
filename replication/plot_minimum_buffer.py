"""Render the March 2020 schedule and discretionary sales budgets, in USD million."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/minimum_reserve_buffer'
with (OUT/'minimums.csv').open() as f:
    data = {(r['case'],int(r['months'])):float(r['minimum']) for r in csv.DictReader(f) if r['floor']=='0'}
plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'georgia-minimum-buffer-v1','font.family':'DejaVu Sans'})
horizons = (1,3,12)
dues = [data['2020_schedule',h] for h in horizons]
sales = [data['2020_sales',h] for h in horizons]
fig, ax = plt.subplots(figsize=(8,3.4))
fig.subplots_adjust(left=.16,bottom=.24,right=.96,top=.73)
ax.barh(range(3),dues,color='#255c69',height=.55,label='Scheduled FX drains')
ax.barh(range(3),sales,left=dues,color='#9bc6cb',height=.55,label='Historical net FX sales')
for i,(d,s) in enumerate(zip(dues,sales)):
    ax.text(d+s+18,i,f'{d+s:,.1f}',va='center',fontsize=10)
ax.set(yticks=range(3),yticklabels=['1 month','3 months','12 months'],xlabel='USD million',xlim=(0,1600))
ax.invert_yaxis()
ax.spines[['top','right','left']].set_visible(False)
ax.tick_params(axis='y',length=0)
ax.set_axisbelow(True)
ax.grid(axis='x',alpha=.18)
fig.text(.06,.91,'Georgia’s March 2020 opening reserve requirement under two uses',fontsize=14,weight='bold')
fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.05,.865),ncol=2,frameon=False)
fig.text(.06,.025,'Zero operating floor and no receipts. Scheduled drains and market sales are assumed disjoint.',fontsize=9)
fig.savefig(OUT/'march_2020.svg',metadata={'Date':None})
plt.close(fig)
svg = OUT/'march_2020.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
