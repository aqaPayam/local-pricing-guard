"""Rebuild cycle-study figures from saved, independently audited evidence."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--output',default='research/cycle-figures');args=parser.parse_args()
OUT=ROOT/args.output;OUT.mkdir(parents=True,exist_ok=True)
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8'))
audit=read('research/cycle-results/independent-audit.json')
if not audit['passed']:raise SystemExit('Independent cycle audit must pass first')
index=read('research/cycle-results/index.json')
cases={r['id']:read('research/cycle-results/'+r['file']) for r in index}
structure={r['id']:r for r in read('research/cycle-results/structure.json')['records']}
scenarios=read('research/cycle-results/manifest.json')['plan']['scenarios']
labels=['Base: 15 prices','Demand scale 0.5','Lower product value','Lower cost',
        'Base: 11 prices','Base: 31 prices','Half tolerance','Double tolerance']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
 'axes.spines.right':False,'svg.hashsalt':'price-guard-cycle-v1','savefig.facecolor':'white'})
def save(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=220,bbox_inches='tight',metadata={'Software':'Price Lab / Matplotlib'})
 fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',metadata={'Date':None})
 plt.close(fig)
def anchor(case,kind):
 return next(r for r in case['objectives']['minCS']['diagnosticStarts']
             if any(p['kind']==kind for p in r['provenance']))

fig,axes=plt.subplots(1,2,figsize=(10,4.1))
for ax,sid in zip(axes,['base-g15-t1','base-g31-t1']):
 c=cases[sid+'-guard'];n=c['game']['n'];rows=c['objectives']['minCS']['starts']
 matrix=np.array([r['upperBound'] for r in rows]).reshape(n,n).T
 image=ax.imshow(matrix,origin='lower',cmap='viridis',interpolation='nearest',vmin=67,vmax=73)
 a=anchor(c,'near-continuous-Nash-anchor')['result']['state'];g=c['objectives']['minCS']['universalWitness']['states'][0]
 ax.scatter([a//n],[a%n],s=90,marker='s',facecolors='none',edgecolors='white',linewidths=1.5,label='Near-Nash start')
 ax.scatter([g//n],[g%n],s=80,marker='x',color='#e98e55',linewidths=2,label='Global worst start')
 ax.set(title=f'Base market, {n} prices',xlabel='Previous shop A price index',ylabel='Previous shop B price index')
 ticks=sorted(set([0,n//2,n-1]));ax.set_xticks(ticks);ax.set_yticks(ticks)
 ax.legend(loc='upper right',fontsize=7,framealpha=.92)
fig.colorbar(image,ax=axes,fraction=.035,pad=.03,label='Lowest reachable long-run customer benefit')
fig.subplots_adjust(wspace=.30,right=.87,bottom=.16)
save(fig,'history-basins')

fig,ax=plt.subplots(figsize=(9.3,4.65));ys=np.arange(8)
global_pct=[];anchor_pct=[]
for s in scenarios:
 c=cases[s['id']+'-guard'];cap=cases[s['id']+'-cap']['objectives']['minCS']['universalWitness']['consumerSurplus']
 global_pct.append(100*c['objectives']['minCS']['universalWitness']['consumerSurplus']/cap)
 anchor_pct.append(100*anchor(c,'near-continuous-Nash-anchor')['result']['upperBound']/cap)
ax.hlines(ys,global_pct,anchor_pct,color='#a5ada5',lw=4,zorder=1)
ax.scatter(global_pct,ys,c='#b54d37',s=46,label='Global guard floor',zorder=3)
ax.scatter(anchor_pct,ys,c='#214f50',marker='D',s=37,label='Near-Nash guard floor',zorder=4)
ax.axvline(100,color='#687b41',ls='--',label='Permanent cap reference')
ax.set_yticks(ys,labels);ax.invert_yaxis();ax.set_xlim(84,101)
ax.set_xlabel('Worst long-run customer benefit / permanent-cap bound (%)')
ax.grid(axis='x',alpha=.18);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=3,fontsize=8,frameon=False)
fig.tight_layout();save(fig,'reachable-welfare')

fig,ax=plt.subplots(figsize=(9.1,3.55));T=np.geomspace(1,20000,120)
colors=['#b54d37','#214f50','#6d7b4c','#be8a46','#6f5a85','#33798d','#86734a','#a55778']
for s,label,color in zip(scenarios,labels,colors):
 r=structure[s['id']+'-guard'];gap=100*r['maximumStartDeficit']/T/r['predictedMinimum']
 ax.plot(T,gap,label=label,color=color,lw=1.7)
ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Evaluation horizon T (rounds)')
ax.set_ylabel('Worst-start transient allowance\n(% of stationary surplus floor)')
ax.grid(alpha=.18);ax.legend(ncol=2,fontsize=7.5,loc='upper right')
fig.tight_layout();save(fig,'finite-horizon-correction')
print(json.dumps({'figures':3,'formats':['png','svg'],'output':str(OUT.relative_to(ROOT))}))
