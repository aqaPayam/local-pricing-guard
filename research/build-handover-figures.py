"""Plot the frozen 40-label handover initializer audit, without rerunning it."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Rectangle,Patch
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--output',default='research/handover-figures');args=ap.parse_args()
OUT=ROOT/args.output;OUT.mkdir(parents=True,exist_ok=True)
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8'))
audit=read('research/handover-init-results/independent-audit.json')
if not audit['passed']:raise SystemExit('Independent initializer audit required')
raw=read('research/handover-init-results/results.json')['records'];summary=read('research/handover-init-results/summary.json')
labels=['Base: 15 prices','Demand scale 0.5','Lower product value','Lower cost','Base: 11 prices','Base: 31 prices','Half tolerance','Double tolerance']
keys=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
 'axes.spines.right':False,'svg.hashsalt':'price-guard-handover-v1','savefig.facecolor':'white'})
def save(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=220,bbox_inches='tight',metadata={'Software':'Price Lab / Matplotlib'})
 fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
matrix=[];texts=[]
for record in raw:
 row=[];text=[]
 for key in keys:
  r=next(x for x in summary['rows'] if x['scenario']==record['scenario']['id'] and x['label']==key)
  if r['allStatesAlreadySafe']:value=0;word='Already safe'
  elif r['existingOneRoundCapCertified']:value=1;word='Repair'
  elif r['finiteInitializerImpossible']:value=2;word='Impossible'
  else:value=3;word='Unresolved'
  row.append(value);text.append(word)
 matrix.append(row);texts.append(text)
fig,ax=plt.subplots(figsize=(9.4,4.5));cmap=ListedColormap(['#dce9d5','#276365','#c27860','#e1ddd3'])
ax.imshow(matrix,cmap=cmap,norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5],4),aspect='auto')
ax.set_yticks(range(8),labels);ax.set_xticks(range(5),['90% cap','95% cap','99% cap','100% cap','Near-Nash\nanchor'])
ax.tick_params(length=0)
for i in range(8):
 for j in range(5):ax.text(j,i,texts[i][j],ha='center',va='center',fontsize=9,color='white' if matrix[i][j] in [1,2] else '#263e35')
ax.set_title('One competitive-cap round, then the unchanged guard',pad=14)
ax.set_xlabel('Requested long-run target (all guarantees subtract the declared numerical margin)',labelpad=11)
fig.tight_layout();save(fig,'initializer-frontier')

panels=[('base-g15-t1','cap-100pct','Base15: 100% cap target'),('base-g31-t1','cap-100pct','Base31: 100% cap target'),
 ('base-g31-t1','near-Nash-anchor-floor','Base31: near-Nash target'),('scale0.5-g15-t1','near-Nash-anchor-floor','Scale0.5: already safe target')]
fig,axes=plt.subplots(2,2,figsize=(8.7,7.2))
for ax,(sid,key,title) in zip(axes.flat,panels):
 rec=next(r for r in raw if r['scenario']['id']==sid);r=next(x for x in rec['results'] if x['label']==key);n=rec['scenario']['gridSize']
 values=np.array([{'safe':0,'unsafe':1,'ambiguous':2}[c] for c in r['classification']]).reshape(n,n).T
 ax.imshow(values,origin='lower',cmap=ListedColormap(['#bdd3b4','#cf8b75','#ddd7c8']),vmin=0,vmax=2,interpolation='nearest')
 k=r['existingCompetitiveCap']['index'];ax.add_patch(Rectangle((-.45,-.45),k+.9,k+.9,fill=False,edgecolor='#183c4a',lw=2,ls='--'))
 largest=r['largestSafeCommonPrefixCap']
 if largest:ax.add_patch(Rectangle((-.4,-.4),largest['index']+.8,largest['index']+.8,fill=False,edgecolor='#172c22',lw=1.3))
 ax.set(title=title,xlabel='Executed A index after cap',ylabel='Executed B index after cap')
 ticks=sorted(set([0,n//2,n-1]));ax.set_xticks(ticks);ax.set_yticks(ticks)
fig.legend(handles=[Patch(facecolor='#bdd3b4',label='Every guard tail meets target'),Patch(facecolor='#cf8b75',label='Below-target tail exists'),
 Patch(facecolor='none',edgecolor='#183c4a',ls='--',label='Competitive-cap rectangle'),Patch(facecolor='none',edgecolor='#172c22',label='Largest safe prefix rectangle')],
 loc='lower center',ncol=2,fontsize=8,bbox_to_anchor=(.5,-.015),frameon=False)
fig.tight_layout(rect=(0,.06,1,1));save(fig,'safe-regions')
print(json.dumps({'figures':2,'formats':['png','svg'],'output':str(OUT.relative_to(ROOT))}))
