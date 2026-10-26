"""Deterministic figures from separately frozen and independently audited evidence."""
from pathlib import Path
from decimal import Decimal
import argparse,hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='research/refinement-figures');args=ap.parse_args()
 out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
 ma=read('research/mesh-results/independent-audit.json');ca=read('research/continuous-results/independent-audit.json')
 if not ma.get('passed') or not ca.get('passed'):raise ValueError('Both independent audits required')
 if ma['studyManifestHash']!=sha('research/mesh-results/manifest.json'):raise ValueError('Mesh audit identity mismatch')
 if ma['indexSha256']!=sha('research/mesh-results/index.json') or ca['studyManifestHash']!=sha('research/continuous-results/manifest.json') or ca['resultsSha256']!=sha('research/continuous-results/results.json'):raise ValueError('Exact audited output identity mismatch')
 meshes=read('research/mesh-results/index.json')['cases'];cont=read('research/continuous-results/results.json')['records'];old=read('research/handover-init-results/results.json')['records']
 scenarios=[r['scenario']['id'] for r in old]
 labels=['Base / 15 original prices','Demand scale 0.5','Lower product value','Lower unit cost','Base / 11 original prices','Base / 31 original prices','Half tolerance','Double tolerance']
 keys=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor']
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'price-guard-refinement-v1','savefig.facecolor':'white'})
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=220,bbox_inches='tight',metadata={'Software':'Price Lab / Matplotlib'})
  fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 def cs_value(row):
  bounds=row['worst']['consumerSurplus'];return float((Decimal(bounds['lower'])+Decimal(bounds['upper']))/2)
 fig,axes=plt.subplots(2,4,figsize=(12.8,6.5))
 for ax,sid,label in zip(axes.flat,scenarios,labels):
  rows=sorted((r for r in meshes if r['scenario']==sid),key=lambda r:r['n']);xs=[r['n'] for r in rows]
  lows=[r['welfare']['minimumAcrossStartingStates'] for r in rows];highs=[r['welfare']['maximumAcrossStartingStates'] for r in rows]
  cap=[r['welfare']['oneRoundCapWorst'] for r in rows]
  ax.fill_between(xs,lows,highs,color='#b9cfca',alpha=.65,label='Range across public starts')
  ax.plot(xs,cap,'o-',color='#225e62',lw=1.7,markersize=3,label='Worst after one cap')
  row=next(r for r in cont if r['scenario']==sid and r['continuum']=='effective')
  if row['status']=='certified theorem and enclosures':ax.axhline(cs_value(row),color='#2c3b3e',lw=1.5,ls='--',label='Validated continuous floor')
  target=next(r for r in next(o for o in old if o['scenario']['id']==sid)['results'] if r['label']=='cap-100pct')['actualGuaranteedThreshold']
  ax.axhline(target,color='#b96042',lw=1.1,ls=':',label='Fixed original100% target minus margin')
  ax.set_xscale('log');ax.set_xticks([15,121,1921],['15','121','1921']);ax.set_title(label,fontsize=10,pad=9)
  ax.set_xlabel('Number of price choices');ax.grid(axis='y',alpha=.17)
 axes[0,0].set_ylabel('Customer surplus');axes[1,0].set_ylabel('Customer surplus')
 handles,names=axes[0,0].get_legend_handles_labels();fig.legend(handles,names,loc='lower center',bbox_to_anchor=(.5,.015),ncol=2,frameon=False,fontsize=9)
 fig.suptitle('Coarse-grid protection does not automatically transfer to continuous prices',fontsize=15,y=1.005)
 fig.text(.5,-.025,'Shading is starting-state variation, not a confidence interval. Grids are not all nested; connecting lines are guides. All72 declared mesh labels are shown.',ha='center',fontsize=8.3)
 fig.tight_layout(rect=(0,.12,1,.98));save(fig,'mesh-continuum-transfer')

 def old_status(r):
  # Distinguish an unnecessary cap from a repair and all-state impossibility.
  classes=r['classification']
  if all(x=='safe' for x in classes):return 0
  if r['existingCompetitiveCap']['certifiedSafe']:return 1
  if all(x=='unsafe' for x in classes):return 2
  return 3
 old_matrix=[];fine_matrix=[];cont_matrix=[]
 for sid in scenarios:
  original=next(o for o in old if o['scenario']['id']==sid)
  fine=read(next(r for r in meshes if r['scenario']==sid and r['n']==1921)['file'].replace('cases/','research/mesh-results/cases/',1))
  effective=next(r for r in cont if r['scenario']==sid and r['continuum']=='effective')
  old_matrix.append([old_status(next(r for r in original['results'] if r['label']==k)) for k in keys])
  fine_matrix.append([0 if next(r for r in fine['targets'] if r['label']==k)['alreadySafe'] else 1 if next(r for r in fine['targets'] if r['label']==k)['capCertifiedDiagnostic'] else 2 if next(r for r in fine['targets'] if r['label']==k)['allStateFailingTail'] else 3 for k in keys])
  cont_matrix.append([{'already guaranteed':0,'all-start failing continuation':2,'unresolved':3}[next(r for r in effective['comparisons'] if r['label']==k)['classification']] for k in keys])
 fig,axes=plt.subplots(1,3,figsize=(12.8,4.8));colors=['#dce8d4','#276366','#bd775e','#dedad0'];cmap=ListedColormap(colors);norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5],4)
 for ax,matrix,title in zip(axes,[old_matrix,fine_matrix,cont_matrix],['Original grid: one capped round','1921 choices: one capped round','Continuous: every starting state']):
  ax.imshow(matrix,cmap=cmap,norm=norm,aspect='auto');ax.set_title(title,fontsize=11,pad=13);ax.set_xticks(range(5),['90%','95%','99%','100%','Anchor'],fontsize=9);ax.tick_params(length=0)
  ax.set_yticks(range(8),labels if ax is axes[0] else ['']*8,fontsize=9)
  for i in range(8):
   for j in range(5):ax.text(j,i,['Safe','Cap','Fail','?'][matrix[i][j]],ha='center',va='center',fontsize=8.5,color='white' if matrix[i][j] in [1,2] else '#233a34')
 fig.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(colors,['Already meets target from all states','Meets target after one cap','Below-target tail from every state','Unresolved'])],loc='lower center',ncol=2,bbox_to_anchor=(.5,-.025),frameon=False,fontsize=8.5)
 fig.suptitle('Keep the original targets fixed when testing transfer',fontsize=15,y=1.035)
 fig.text(.5,-.08,'Every target uses its saved F minus the numerical allowance. Fine-grid entries are audited binary64 diagnostics; continuous entries use validated enclosures.',ha='center',fontsize=8)
 fig.tight_layout(rect=(0,.09,1,1));save(fig,'fixed-target-transfer')
 # Dedicated print-size figures keep labels legible in an A4 research note.
 sid='base-g15-t1';rows=sorted((r for r in meshes if r['scenario']==sid),key=lambda r:r['n']);xs=[r['n'] for r in rows]
 low=[r['welfare']['minimumAcrossStartingStates'] for r in rows];high=[r['welfare']['maximumAcrossStartingStates'] for r in rows];cap=[r['welfare']['oneRoundCapWorst'] for r in rows]
 effective=next(r for r in cont if r['scenario']==sid and r['continuum']=='effective');target=next(r for r in old[0]['results'] if r['label']=='cap-100pct')['actualGuaranteedThreshold']
 fig,ax=plt.subplots(figsize=(7.2,3.4));ax.fill_between(xs,low,high,color='#b9cfca',alpha=.65,label='Range across public starts');ax.plot(xs,cap,'o-',color='#225e62',markersize=4,label='Worst after one cap')
 ax.axhline(cs_value(effective),color='#2c3b3e',ls='--',label='Continuous floor (validated)');ax.axhline(target,color='#b96042',ls=':',label='Fixed original target minus margin')
 ax.set_xscale('log');ax.set_xticks([11,15,31,121,481,1921],['11','15','31','121','481','1921']);ax.set(xlabel='Number of price choices per shop',ylabel='Customer surplus',title='Base market: the after-cap guarantee changes with price resolution');ax.grid(axis='y',alpha=.2)
 ax.legend(loc='upper center',bbox_to_anchor=(.5,-.22),ncol=2,frameon=False,fontsize=8.8);fig.tight_layout();save(fig,'base-transfer-print')
 fig,ax=plt.subplots(figsize=(7.2,4.4));ax.imshow(cont_matrix,cmap=cmap,norm=norm,aspect='auto');ax.set_title('Original finite grid  →  continuous price interval',fontsize=12,pad=14)
 ax.set_yticks(range(8),['Base15','Demand scale0.5','Lower product value','Lower unit cost','Base11','Base31','Half tolerance','Double tolerance'],fontsize=9);ax.set_xticks(range(5),['90% cap','95% cap','99% cap','100% cap','Anchor'],fontsize=9);ax.tick_params(length=0)
 for i in range(8):
  for j in range(5):ax.text(j,i,['Safe','Cap','Fail','?'][old_matrix[i][j]]+' → '+['Safe','Cap','Fail','?'][cont_matrix[i][j]],ha='center',va='center',fontsize=8.7,color='white' if cont_matrix[i][j]==2 else '#233a34')
 fig.text(.5,.025,'Safe: already meets target from all states. Cap: meets after one cap. Fail: below-target tail from every state.',ha='center',fontsize=8)
 fig.tight_layout(rect=(0,.06,1,1));save(fig,'target-transfer-print')
 print(json.dumps({'figures':4,'formats':['png','svg'],'output':str(out.relative_to(ROOT))}))

if __name__=='__main__':main()
