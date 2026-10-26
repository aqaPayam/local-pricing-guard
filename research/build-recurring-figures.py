"""Deterministic, audit-gated recurring-cap figures; no new case calculations."""
from pathlib import Path
from decimal import Decimal
import argparse,hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm

ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def evidence():
 for folder,key,source in [('recurring-results','resultsSha256','results.json'),('sparse-display-results','indexSha256','index.json')]:
  manifest=read('research/'+folder+'/manifest.json')
  for section in ['sourceHashes','inputHashes']:
   for path,digest in manifest[section].items():
    if sha(path)!=digest:raise ValueError('Frozen dependency changed: '+path)
  names=['independent-audit.json']+(['rational-audit.json'] if folder=='sparse-display-results' else [])
  for name in names:
   a=read('research/'+folder+'/'+name)
   if not a.get('passed') or a['studyManifestHash']!=sha('research/'+folder+'/manifest.json') or a[key]!=sha('research/'+folder+'/'+source):raise ValueError('Exact independent audit identity required')
   auditor='research/audit-sparse-display.js' if folder=='sparse-display-results' and name=='independent-audit.json' else 'research/audit-sparse-reset.py'
   if a['auditorSourceHash']!=sha(auditor):raise ValueError('Live auditor identity mismatch')
 return read('research/recurring-results/results.json')['records']
def mid(b):return float((Decimal(b['lower'])+Decimal(b['upper']))/2)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='research/recurring-figures');args=ap.parse_args();out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
 rows=[r for r in evidence() if r['continuum']=='effective'];names=['Base15','Scale0.5','Lower value','Lower cost','Base11','Base31','Half tolerance','Double tolerance'];keys=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor']
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'recurring-cap-v1','savefig.facecolor':'white'})
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=220,bbox_inches='tight',metadata={'Software':'Market Lab / Matplotlib'});fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 base=next(r for r in rows if r['scenario']=='base-g15-t1');target=next(x for x in base['comparisons'] if x['label']=='cap-95pct');fig,ax=plt.subplots(figsize=(8.8,3.9));periods=[x['period'] for x in base['frontier']]
 ax.plot(periods,[mid(x['averageConsumerSurplus']) for x in base['frontier']],'o-',color='#24656b',label='Worst cycle / activation-average floor')
 ax.plot(periods,[mid(x['lastRoundConsumerSurplus']) for x in base['frontier']],'s--',color='#b36d4f',label='Worst individual round in cycle',markersize=4)
 ax.axhline(float(target['actualThresholdExact']),color='#6e842f',ls=':',label='Fixed original 95% target minus margin')
 ax.axhline(mid(base['inheritedContinuum']['consumerSurplus']),color='#5f6669',ls='--',lw=1,label='Unchanged-guard long-run floor')
 for name,key,dy in [('K=4 safe','safePeriod',14),('K=5 fails','nextFailingPeriod',-25)]:
  point=target[key];ax.scatter(point['period'],mid(point['averageConsumerSurplus']),color='#24656b',s=35);ax.annotate(name,(point['period'],mid(point['averageConsumerSurplus'])),xytext=(12,dy),textcoords='offset points',fontsize=9)
 ax.set_xscale('log',base=2);ax.set_xticks(periods,[str(x) for x in periods]);ax.set_xlabel('Cap period K (one cap, then K-1 guard executions)');ax.set_ylabel('Customer surplus');ax.set_title('Same physical cap, different timing: base market',pad=12);ax.grid(axis='y',alpha=.18);ax.legend(fontsize=8.7,loc='upper right');fig.tight_layout();save(fig,'base-timing-frontier')
 matrix=[];texts=[]
 for r in rows:
  mr=[];tr=[]
  for key in keys:
   c=next(x for x in r['comparisons'] if x['label']==key)
   if c['status']=='no recurring cap needed for the long-run target':mr.append(0);tr.append('None')
   elif 'largestPeriod' in c:mr.append(1 if c['largestPeriod']==1 else 2);tr.append(str(c['largestPeriod']))
   else:mr.append(3);tr.append('?')
  matrix.append(mr);texts.append(tr)
 fig,ax=plt.subplots(figsize=(8.8,4.9));ax.imshow(matrix,cmap=ListedColormap(['#dce8d4','#b77960','#28676c','#dedad0']),norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5],4),aspect='auto');ax.set_xticks(range(5),['90%','95%','99%','100%','Anchor']);ax.set_yticks(range(8),names);ax.tick_params(length=0)
 for i in range(8):
  for j in range(5):ax.text(j,i,texts[i][j],ha='center',va='center',color='#203e38' if matrix[i][j] in [0,3] else 'white',fontsize=12)
 ax.set_title('Largest safe integer period within each inherited cap family',pad=14);ax.set_xlabel('Fixed original target label (each retains its saved margin)',labelpad=12);fig.text(.54,.005,'None: no recurring cap for long-run goal. 1: cap every execution.\nSame nominal/effective classifications; equivalent labels are not independent economies.',ha='center',fontsize=8.6);fig.tight_layout(rect=(0,.08,1,1));save(fig,'fixed-target-periods')
 # Use audited stored orbit terms; this is a derived plot, not another simulation.
 k=target['largestPeriod'];rewards=[mid(x['consumerSurplus']) for x in base['orbit'][:k]];ys=[rewards[t%k] for t in range(16)];av=[sum(ys[:t])/t for t in range(1,17)];fig,ax=plt.subplots(figsize=(8.8,3.65));ts=list(range(1,17));ax.plot(ts,ys,'o-',color='#b36d4f',label='Individual execution');ax.plot(ts,av,'s-',color='#24656b',label='Average from first actual cap',markersize=4);ax.axhline(mid(target['safePeriod']['averageConsumerSurplus']),ls='--',color='#567c45',label='Certified K=4 average floor');ax.axhline(float(target['actualThresholdExact']),ls=':',color='#777',label='Original 95% target minus margin')
 for t in range(1,17,k):ax.axvspan(t-.15,t+.15,color='#dae6d3',zorder=-1)
 ax.set_xticks(ts);ax.set_xlabel('Actual rewarded execution (cap at 1,5,9,13)');ax.set_ylabel('Customer surplus');ax.set_title('A protected average can contain lower-benefit rounds',pad=12);ax.legend(fontsize=8.5,loc='upper right');ax.grid(axis='y',alpha=.15);fig.tight_layout();save(fig,'activation-prefix')
 print(json.dumps({'figures':6,'output':str(out)}))
if __name__=='__main__':main()
