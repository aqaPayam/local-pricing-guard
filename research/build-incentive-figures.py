"""Figures are descriptive outputs of the independently accepted finite study."""
from pathlib import Path
from fractions import Fraction
import argparse,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def evidence():
 folder='research/incentive-results/'
 m,r,i,a,c=[read(folder+name+'.json') for name in ['manifest','results','index','independent-audit','completion']]
 if a.get('passed') is not True or c.get('passed') is not True or c.get('unresolvedRecords')!=0:raise ValueError('Passed complete independent evidence required')
 for key,name in [('studyManifestHash','manifest'),('resultsSha256','results'),('indexSha256','index')]:
  if a[key]!=sha(folder+name+'.json'):raise ValueError('Audit identity changed '+name)
 if a['auditorSourceHash']!=sha('research/audit-incentive-study.py'):raise ValueError('Independent auditor changed')
 if r['manifestSha256']!=sha(folder+'manifest.json') or i['manifestSha256']!=sha(folder+'manifest.json') or not c['finalFrozenDependencyCheck']['passed']:raise ValueError('Primary completion identity changed')
 for key,name in [('resultsSha256','results'),('indexSha256','index')]:
  if c[key]!=sha(folder+name+'.json'):raise ValueError('Completion mismatch')
 for section in ['sourceHashes','inputHashes']:
  for path,digest in m[section].items():
   if sha(path)!=digest:raise ValueError('Frozen source/input changed '+path)
 if len(r['records'])!=96 or len(i['records'])!=96 or len({x['id'] for x in r['records']})!=96:raise ValueError('All96 labels required')
 for entry,record in zip(i['records'],r['records']):
  if entry['id']!=record['id'] or sha(folder+entry['file'])!=entry['sha256'] or read(folder+entry['file'])!=record:raise ValueError('Indexed record mismatch')
  for layer in record['layers']:
   if sha(folder+layer['argmaxFile'])!=layer['argmaxSha256']:raise ValueError('Policy changed')
 for w in i['welfareCertificates']:
  if sha(folder+w['file'])!=w['sha256']:raise ValueError('Welfare changed')
 if not a.get('corruptionNegativeControls') or not all(a['corruptionNegativeControls'].values()):raise ValueError('Corruption controls failed')
 return m,r,i,a,c
def exact(x):return Fraction(int(x['numerator']),int(x['denominator']))
def val(x):return float(exact(x))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='research/incentive-figures');args=ap.parse_args();out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
 m,r,i,a,c=evidence();records=r['records'];scenarios=[x['scenario'] for x in m['plan']['cases']]
 def select(s,slot,g='19/20'):return next(x for x in records if x['scenario']==s and x['periodSlot']['id']==slot and x['focalSeller']=='A' and x['discount']['numerator']+'/'+x['discount']['denominator']==g)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'individual-incentives-v1','savefig.facecolor':'white'})
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=220,bbox_inches='tight',metadata={'Software':'Market Lab / Matplotlib'});fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 fig,ax=plt.subplots(figsize=(8.8,4.6));labels=['Base15','Scale0.5','Lower value','Lower cost','Base11','Base31','Half tolerance','Double tolerance'];slots=['permanent-cap','closed-effective-95pct','fixed-16'];colors=['#8c9987','#246d78','#b36a48'];legends=['Cap every round','Original 95%-target period','Period 16']
 for j,slot in enumerate(slots):
  gains=[]
  for s in scenarios:
   cap=select(s,slot)['cap'];gains.append(100*float(exact(cap['infiniteGain'])/exact(cap['infiniteBaseline'])))
  ax.scatter(gains,[k+(j-1)*.19 for k in range(8)],label=legends[j],s=33,c=colors[j],marker=['s','o','^'][j])
 ax.axvline(0,color='#bdc8b8',lw=.8);ax.set_yticks(range(8),labels);ax.invert_yaxis();ax.set_xlabel('Best gain over copying the script (% of discounted profit)');ax.set_title('Small private incentives to depart from the public price script',pad=12);ax.grid(axis='x',alpha=.17);fig.legend(loc='lower center',bbox_to_anchor=(.55,.01),ncol=3,frameon=False,fontsize=9);fig.tight_layout(rect=(0,.08,1,1));save(fig,'relative-profit-gains')
 base=select('base-g15-t1','closed-effective-95pct');raw=read(next(x['rawFile'] for x in m['plan']['cases'] if x['scenario']=='base-g15-t1'));prices=raw['finite']['prices'];n=len(prices);trace=base['optimalBlockReplay'];phases=base['phaseDiagnostics'];fig,axes=plt.subplots(2,1,figsize=(8.8,5.0),sharex=True);x=list(range(1,5));baseline=[prices[p['baselineAction']] for p in phases]
 axes[0].plot(x,baseline,'o:',c='#858d80',label='Both copy script');axes[0].plot(x,[prices[t['originalQuoteIndices'][0]] for t in trace],'o-',c='#b34f34',label='Best response: your A');axes[0].plot(x,[prices[t['originalQuoteIndices'][1]] for t in trace],'s--',c='#237a91',label='Scripted B after your choices');axes[0].set_ylabel('Executed price');axes[0].set_title('Base game, four-round cycle: optimizing own profit changes the path')
 bp=[raw['finite']['rewards']['profitA'][p['baselineAction']*n+p['opponentAction']] for p in phases];op=[raw['finite']['rewards']['profitA'][t['originalQuoteIndices'][0]*n+t['originalQuoteIndices'][1]] for t in trace]
 axes[1].plot(x,bp,'o:',c='#858d80',label='A when both copy');axes[1].plot(x,op,'o-',c='#b34f34',label='A best response');axes[1].set_ylabel('Profit before discount');axes[1].set_xlabel('Actual round (first is capped)');axes[1].set_xticks(x)
 for ax in axes:ax.axvspan(.8,1.2,color='#e0c3a6',alpha=.25);ax.grid(axis='y',alpha=.16);ax.legend(fontsize=8,loc='best',frameon=False)
 fig.tight_layout();save(fig,'base-cycle-strategies')
 zero=select('base-g15-t1','closed-effective-95pct','0/1');fig,ax=plt.subplots(figsize=(8.8,3.6));ax.plot(x,[val(p['infiniteGain']) for p in phases],'o-',color='#246d78',label='Discount 19/20, including future cycles');ax.plot(x,[val(p['infiniteGain']) for p in zero['phaseDiagnostics']],'s--',color='#b36a48',label='Discount 0: current reward only');ax.scatter([4],[val(base['oneShotScreen']['gain'])],marker='x',s=90,c='#223d35',zorder=5,label='Simple last-guard immediate gain');ax.set_xticks(x,['Cap','Guard 1','Guard 2','Last guard']);ax.set_ylabel('Best gain from this baseline-path phase');ax.set_title('A zero gain at activation can hide a later profitable phase');ax.grid(axis='y',alpha=.17);fig.legend(loc='lower center',bbox_to_anchor=(.55,.01),ncol=1,frameon=False,fontsize=8.5);fig.tight_layout(rect=(0,.2,1,1));save(fig,'phase-gain-screen')
 print(json.dumps({'figures':6,'output':str(out)}))
if __name__=='__main__':main()
