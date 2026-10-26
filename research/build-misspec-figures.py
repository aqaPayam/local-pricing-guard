"""Derive calibration figures from exactly bound independently accepted evidence."""
from pathlib import Path
from decimal import Decimal
import argparse,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap,BoundaryNorm
ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def evidence():
 folder='research/misspec-results/';a=read(folder+'independent-audit.json');m=read(folder+'manifest.json');r=read(folder+'results.json');c=read(folder+'completion.json')
 if not a.get('passed') or a['studyManifestHash']!=sha(folder+'manifest.json') or a['resultsSha256']!=sha(folder+'results.json') or r['manifestSha256']!=sha(folder+'manifest.json') or c['resultsSha256']!=sha(folder+'results.json') or not c['finalFrozenDependencyCheck']['passed']:raise ValueError('Exact accepted primary/audit identities required')
 if a['auditorSourceHash']!=sha('research/audit-misspec-study.py') or a['arithmeticBackendHash']!=sha('research/audit-continuous-study.py'):raise ValueError('Independent source identity changed')
 if not a.get('corruptionNegativeControls') or not all(a['corruptionNegativeControls'].values()):raise ValueError('Audit corruption controls required')
 for section in ['sourceHashes','inputHashes']:
  for path,digest in m[section].items():
   if sha(path)!=digest:raise ValueError('Frozen dependency changed: '+path)
 for record in r['records']:
  path=folder+'records/'+record['scenario']+'-'+record['continuum']+'.json'
  if read(path)!=record:raise ValueError('Per-model record identity changed')
 if len(r['records'])!=16:raise ValueError('All16 retained model records required')
 return m,r,a,c
def mid(b):return float((Decimal(b['lower'])+Decimal(b['upper']))/2)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='research/misspec-figures');args=ap.parse_args();out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
 m,raw,a,c=evidence();rows=[r for r in raw['records'] if r['continuum']=='effective'];names=['Base15','Scale0.5','Lower value','Lower cost','Base11','Base31','Half tolerance','Double tolerance'];keys=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor'];levels=['0','0.001','0.01','0.05']
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'demand-misspec-v1','savefig.facecolor':'white'})
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=220,bbox_inches='tight',metadata={'Software':'Market Lab / Matplotlib'});fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 def target(row,key):return next(t for t in row['targets'] if t['label']==key)
 fig,ax=plt.subplots(figsize=(8.8,4.8));colors={'guard-only':'#899488','closed-selected':'#276a70','permanent-cap':'#b27050'};labels={'guard-only':'Guard only','closed-selected':'Original selected timing','permanent-cap':'Cap every execution'}
 positives=[float(p['radius']['radiusEnclosure']['lower']) for row in rows for p in target(row,'cap-95pct')['policies'] if p['radius'].get('radiusEnclosure') and Decimal(p['radius']['radiusEnclosure']['lower'])>0];left=min(positives)/5 if positives else .000001;right=max(positives)*2 if positives else 1
 for i,row in enumerate(rows):
  t=target(row,'cap-95pct')
  for j,p in enumerate(t['policies']):
   rad=p['radius'];y=i+(j-1)*.19;box=rad.get('radiusEnclosure')
   if box and Decimal(box['lower'])>0:
    lo,hi=float(box['lower']),float(box['upper']);ax.plot([lo,hi],[y,y],color=colors[p['slot']],lw=2);ax.scatter((lo+hi)/2,y,color=colors[p['slot']],s=30,marker=['x','o','s'][j],label=labels[p['slot']] if i==0 else None)
   else:ax.text(left*1.1,y,'empty' if 'empty safe' in rad['status'] else '?',color=colors[p['slot']],va='center',ha='left',fontsize=8,label=None)
 ax.set_xscale('log');ax.set_xlim(left,right);ax.set_yticks(range(8),names);ax.invert_yaxis();ax.set_xlabel('Break-even downward quality error d (taste-scale units; log scale)');ax.set_title('How much demand-calibration reserve does the 95% target leave?',pad=13);ax.grid(axis='x',alpha=.18);fig.legend(handles=[Line2D([0],[0],color=colors[key],marker=marker,ls='',label=labels[key]) for key,marker in zip(colors,['x','o','s'])],loc='lower center',bbox_to_anchor=(.55,.035),ncol=3,frameon=False,fontsize=9);fig.text(.55,.005,'Empty means already below target at zero error. Equivalent original labels are retained, not independent replications.',ha='center',fontsize=8.2);fig.tight_layout(rect=(0,.13,1,1));save(fig,'target95-calibration-radius')
 base=next(r for r in rows if r['scenario']=='base-g15-t1');t=target(base,'cap-95pct');fig,ax=plt.subplots(figsize=(8.8,4.3))
 for p in t['policies']:
  values=p['sensitivity'];available=[v for v in values if v.get('surplus')]
  ax.plot([levels.index(v['dbar']['exactDecimal']) for v in available],[mid(v['surplus']) for v in available],'o-',color=colors[p['slot']],lw=1.7,label=labels[p['slot']])
 if t.get('actualThresholdExact'):ax.axhline(float(t['actualThresholdExact']),color='#4f7741',lw=1.5,ls='--',label='Unchanged original 95% target minus margin')
 ax.set_xticks(range(4),['0','.001','.01','.05']);ax.set_xlabel('Declared quality-error bound d_bar (four categorical positions)');ax.set_ylabel('Worst customer surplus');ax.set_title('Fixed enforcement: compare the same absolute welfare promise',pad=13);handles,legend_labels=ax.get_legend_handles_labels();fig.legend(handles,legend_labels,fontsize=8.6,loc='lower center',bbox_to_anchor=(.55,.005),ncol=2,frameon=False);ax.grid(axis='y',alpha=.17);fig.tight_layout(rect=(0,.16,1,1));save(fig,'base-fixed-policies')
 matrix=[];texts=[]
 for key in keys:
  t=target(base,key);mr=[];tr=[]
  for level in levels:
   r=next(x for x in t['robustPeriods'] if x['dbar']['exactDecimal']==level);s=r['status']
   if s=='no recurring cap needed for the long-run target':mr.append(0);tr.append('None')
   elif s=='largest certified fixed period':mr.append(1 if r['largestPeriod']==1 else 2);tr.append(str(r['largestPeriod']))
   elif s=='infeasible for this fixed-cap family':mr.append(3);tr.append('Insufficient')
   else:mr.append(4);tr.append('?')
  matrix.append(mr);texts.append(tr)
 fig,ax=plt.subplots(figsize=(8.8,3.8));ax.imshow(matrix,cmap=ListedColormap(['#dce8d4','#bc8163','#296a70','#f0d9cd','#ddd9cb']),norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5,4.5],5),aspect='auto');ax.set_xticks(range(4),levels);ax.set_yticks(range(5),['90%','95%','99%','100%','Anchor']);ax.tick_params(length=0)
 for i in range(5):
  for j in range(4):ax.text(j,i,texts[i][j],ha='center',va='center',fontsize=10,color='white' if matrix[i][j] in [1,2] else '#294037')
 ax.set_xlabel('Declared quality-error bound d_bar (exact levels)');ax.set_ylabel('Fixed original target label');ax.set_title('Base market: largest safe period at each uncertainty bound',pad=13);fig.text(.55,.005,'None: guard already protects long-run target. 1: cap every execution. Insufficient: this same cap cannot meet it.',ha='center',fontsize=8.3);fig.tight_layout(rect=(0,.04,1,1));save(fig,'base-robust-periods')
 print(json.dumps({'figures':6,'output':str(out)}))
if __name__=='__main__':main()
