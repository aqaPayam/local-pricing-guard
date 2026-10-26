"""A small set of report figures from accepted evidence; no new experiment."""
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
from importlib.util import spec_from_file_location,module_from_spec
import argparse,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def module(name):
 spec=spec_from_file_location(name.replace('-','_'),ROOT/'research'/name);m=module_from_spec(spec);spec.loader.exec_module(m);return m
def mid(x):return float((Decimal(x['lower'])+Decimal(x['upper']))/2)
def ratio(x):return Fraction(int(x['numerator']),int(x['denominator']))
def structural_evidence():
 recurring=module('build-recurring-figures.py').evidence()
 misspec=module('build-misspec-figures.py').evidence()
 incentive=module('build-incentive-figures.py').evidence()
 ma=read('research/mesh-results/independent-audit.json');ca=read('research/continuous-results/independent-audit.json')
 for audit,folder,source in [(ma,'mesh-results','index'),(ca,'continuous-results','results')]:
  prefix='research/'+folder+'/'
  if audit.get('passed') is not True or audit['studyManifestHash']!=sha(prefix+'manifest.json') or audit[source+'Sha256']!=sha(prefix+source+'.json'):raise ValueError('Current accepted transfer evidence required')
  manifest=read(prefix+'manifest.json')
  for section in ['sourceHashes','inputHashes']:
   for p,digest in manifest[section].items():
    if sha(p)!=digest:raise ValueError('Frozen transfer input changed '+p)
 return recurring,misspec,incentive,read('research/mesh-results/index.json')['cases'],read('research/continuous-results/results.json')['records']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='research/capacity-figures');ap.add_argument('--structural-only',action='store_true');args=ap.parse_args()
 if not args.structural_only:raise SystemExit('Adaptive figure integration awaits its independent audit; use --structural-only for accepted earlier evidence')
 recurring,misspec,incentive,meshes,continuous=structural_evidence();out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'capacity-report-v1','savefig.facecolor':'white'})
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=240,bbox_inches='tight',metadata={'Software':'Market Lab / Matplotlib'});fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 sid='base-g15-t1';base=next(r for r in recurring if r['scenario']==sid and r['continuum']=='effective');target=next(t for t in base['comparisons'] if t['label']=='cap-95pct');threshold=float(target['actualThresholdExact']);csstar=mid(base['inheritedContinuum']['consumerSurplus']);rows=sorted((r for r in meshes if r['scenario']==sid),key=lambda x:x['n'])
 fig,axes=plt.subplots(2,1,figsize=(8.8,6.5));ax=axes[0];ax.plot([r['n'] for r in rows],[r['welfare']['oneRoundCapWorst'] for r in rows],'o-',color='#24656b',label='One cap, then unchanged guard (finite game)');ax.axhline(csstar,color='#5d6665',ls='--',label='Validated continuous worst floor');ax.axhline(threshold,color='#6d7f35',ls=':',label='Original relaxed 95% target');ax.set_xscale('log');ax.set_xticks([11,15,31,61,121,481,1921],['11','15','31','61','121','481','1921']);ax.set_ylabel('Long-run customer benefit');ax.set_xlabel('Number of finite price choices per shop');ax.set_title('(a) A coarse price-grid promise need not survive richer choices',loc='left',pad=10);ax.grid(axis='y',alpha=.17);ax.legend(fontsize=10,loc='best',frameon=False)
 ax=axes[1];points=sorted(base['frontier']+[target['nextFailingPeriod']],key=lambda x:x['period']);periods=[p['period'] for p in points];ax.plot(periods,[mid(p['averageConsumerSurplus']) for p in points],'o-',c='#24656b',label='Continuous all-policy cycle / activation-average floor');ax.axhline(csstar,color='#5d6665',ls='--',label='Unchanged-guard floor');ax.axhline(threshold,color='#6d7f35',ls=':',label='Same original relaxed 95% target')
 for key,label,offset in [('safePeriod','K=4 meets target',(10,12)),('nextFailingPeriod','K=5 falls below',(-95,-23))]:
  point=target[key];ax.annotate(label,(point['period'],mid(point['averageConsumerSurplus'])),xytext=offset,textcoords='offset points',fontsize=10,arrowprops={'arrowstyle':'-','color':'#82958b','lw':.7} if key=='nextFailingPeriod' else None)
 ax.set_xscale('log',base=2);ax.set_xticks([1,2,4,8,16,32,64,128]);ax.set_xticklabels(['1','2','4','8','16','32','64','128']);ax.set_xlabel('Period K: one real cap, then K−1 guard rounds');ax.set_ylabel('Worst customer benefit');ax.set_title('(b) Recurring executions of the same cap repair this fixed target',loc='left',pad=10);ax.grid(axis='y',alpha=.17);ax.legend(fontsize=10,loc='upper right',frameon=False);fig.tight_layout(h_pad=2.3);save(fig,'precision-and-timing')
 _,raw,_,_=misspec;mb=next(r for r in raw['records'] if r['scenario']==sid and r['continuum']=='effective');mt=next(t for t in mb['targets'] if t['label']=='cap-95pct');levels=['0','0.001','0.01','0.05'];fig,axes=plt.subplots(1,2,figsize=(9.6,4.6));ax=axes[0];colors={'guard-only':'#8a9587','closed-selected':'#24656b','permanent-cap':'#b26b48'};labels={'guard-only':'Guard only','closed-selected':'Fixed K=4','permanent-cap':'Same cap every round'}
 for policy in mt['policies']:
  values=[p for p in policy['sensitivity'] if p.get('surplus')];ax.plot([levels.index(p['dbar']['exactDecimal']) for p in values],[mid(p['surplus']) for p in values],'o-',c=colors[policy['slot']],label=labels[policy['slot']],markersize=4)
 ax.axhline(float(mt['actualThresholdExact']),color='#6d7f35',ls=':',label='Unchanged 95% target');ax.set_xticks(range(4),['0','.001','.01','.05']);ax.set_xlabel('Declared downward quality error d\n(taste-scale units; four categorical levels)');ax.set_ylabel('Worst customer benefit');ax.set_title('(a) A fixed absolute promise uses model reserve',loc='left',fontsize=12);ax.grid(axis='y',alpha=.16);ax.legend(fontsize=10.3,frameon=False,loc='upper left',bbox_to_anchor=(-.02,-.28),ncol=2)
 _,ir,_,_,_=incentive;scenarios=[r['scenario'] for r in incentive[0]['plan']['cases']];names=['Base15','Scale 0.5','Lower value','Lower cost','Base11','Base31','Half tolerance','Double tolerance'];ax=axes[1]
 for slot,offset,color,marker,label in [('closed-effective-95pct',-.10,'#24656b','o','Original 95%-target period'),('fixed-16',.10,'#b26b48','^','K=16')]:
  selected=[next(r for r in ir['records'] if r['scenario']==s and r['periodSlot']['id']==slot and r['focalSeller']=='A' and r['discount']['numerator']=='19') for s in scenarios];gains=[100*float(ratio(r['cap']['infiniteGain'])/ratio(r['cap']['infiniteBaseline'])) for r in selected];ax.scatter(gains,[k+offset for k in range(8)],c=color,marker=marker,s=23,label=label)
 ax.set_yticks(range(8),names,fontsize=10.5);ax.invert_yaxis();ax.set_xlim(0,.24);ax.set_xticks([0,.1,.2],['0','.1','.2']);ax.set_xlabel('Best private profit improvement (%)\nagainst the fixed public script');ax.set_title('(b) Worst welfare does not imply selfish stability',loc='left',fontsize=12);ax.grid(axis='x',alpha=.16);ax.legend(fontsize=10.3,frameon=False,loc='upper left',bbox_to_anchor=(0,-.28));fig.tight_layout(w_pad=2.6,rect=(0,.08,1,1));save(fig,'calibration-and-incentives')
 print(json.dumps({'structuralFigures':4,'output':str(out),'newExperimentalCases':0}))
if __name__=='__main__':main()
