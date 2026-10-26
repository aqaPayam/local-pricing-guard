"""Distinct V11 figure from the completely accepted response audit.

Revalidates the frozen read-only adapter and saved summary before plotting.
No old figure, primary record, optimizer, policy or checkpoint is modified.
"""
from pathlib import Path
from fractions import Fraction
import hashlib,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.local/matplotlib-learned-opponent'))
try:
 import matplotlib
except ImportError:
 sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'))
 import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(value):
 n,d=int(value['numeratorHex'],16),int(value['denominatorHex'],16)
 if d<=0:raise ValueError('Positive exact denominator required')
 return Fraction(n,d)
def build():
 node=shutil.which('node')
 if not node:raise RuntimeError('Node24+ required for frozen read-only evidence gate; no installation attempted')
 gate="""import fs from 'node:fs';import {analyzeEvidence,localIO,jsonBytes} from './research/learned-opponent-analysis.js';const s=analyzeEvidence(localIO());if(!jsonBytes(s).equals(fs.readFileSync('research/learned-opponent-results/summary.json')))throw Error('Saved summary differs from raw regeneration');console.log(JSON.stringify({passed:true,records:s.records.length,manifest:s.meta.primaryManifestSha256,audit:s.meta.independentAuditSha256}));"""
 receipt=json.loads(subprocess.check_output([node,'--input-type=module','-e',gate],cwd=ROOT,text=True))
 if receipt.get('passed') is not True or receipt.get('records')!=48:raise ValueError('Complete48-label evidence gate required')
 summary_file=ROOT/'research/learned-opponent-results/summary.json'
 summary=json.loads(summary_file.read_text(encoding='utf-8'))
 if summary['meta']['counts']['scientificallyAvailable']!=48:raise ValueError('This accepted complete-case figure requires all48 available; do not omit failed labels')
 rows=summary['records'];seeds=summary['orderedSeeds'];controllers=summary['controllerOrder']
 if len(seeds)!=12 or controllers!=['startup-only','selected95']:raise ValueError('Fixed complete figure population differs')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'svg.hashsalt':'learned-opponent-gains-v11','svg.fonttype':'path','axes.unicode_minus':True})
 fig,axes=plt.subplots(1,2,figsize=(9.2,3.7),sharex=True,sharey=True)
 fig.subplots_adjust(left=.09,right=.985,bottom=.265,top=.81,wspace=.09)
 colors={'A':'#c86609','B':'#2463a9'};markers={'A':'o','B':'D'};offset={'A':-.15,'B':.15}
 upper_max=max(exact(r['performance']['possibleGain']['upper']) for r in rows)
 max_gap=max(exact(r['certificate']['responseOptimalityGap']) for r in rows)
 if max_gap<0:raise ValueError('Negative exact gap')
 for ax,controller,title in zip(axes,controllers,['Startup-only','Recurring cap (K = 4)']):
  group=[r for r in rows if r['control']['id']==controller]
  if len(group)!=24:raise ValueError('Every controller needs both sellers/all12 seeds')
  positive=sum(exact(r['performance']['rawGain'])>0 for r in group)
  ax.set_title(f'{title}  ·  {positive}/24 positive',loc='left',fontsize=10,fontweight='semibold',pad=10)
  for y,seed in enumerate(seeds):
   ax.axhline(y,color='#f0f1f2',linewidth=.6,zorder=0)
   for focal in ['A','B']:
    matches=[r for r in group if r['seed']==seed and r['focal']==focal]
    if len(matches)!=1:raise ValueError('Missing/duplicate seed-seller figure identity')
    r=matches[0];gain=exact(r['performance']['rawGain']);upper=exact(r['performance']['possibleGain']['upper'])
    if upper<gain:raise ValueError('Best-improvement upper below achieved gain')
    yy=y+offset[focal]
    # No artificial enlargement: tiny exact upper gaps overlap at this scale.
    ax.plot([float(gain),float(upper)],[yy,yy],color='#6b7280',linewidth=.8,zorder=2)
    ax.plot(float(upper),yy,marker='|',markersize=6,color='#6b7280',linestyle='None',zorder=2)
    ax.plot(float(gain),yy,marker=markers[focal],markersize=4.4,color=colors[focal],linestyle='None',zorder=3)
  ax.set_xlim(-.35,float(upper_max)*1.065+.05);ax.set_ylim(11.6,-.6)
  ax.set_yticks(range(12),[str(seed) for seed in seeds]);ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
  ax.grid(axis='x',color='#dfe3e8',linewidth=.65);ax.set_axisbelow(True)
  for spine in ax.spines.values():spine.set_visible(False)
  ax.tick_params(axis='both',length=0,labelsize=8);ax.set_xlabel('Extra discounted own profit (absolute payoff units)',labelpad=7)
 axes[0].set_ylabel('Market seed',labelpad=8)
 fig.suptitle('Full-policy deviations against each saved learned partner',x=.09,y=.975,ha='left',fontsize=12,fontweight='semibold')
 handles=[Line2D([],[],color=colors['A'],marker='o',linestyle='None',markersize=5,label='Shop A: achieved gain'),Line2D([],[],color=colors['B'],marker='D',linestyle='None',markersize=5,label='Shop B: achieved gain'),Line2D([],[],color='#6b7280',marker='|',linestyle='-',linewidth=.8,markersize=6,label='Best-gain upper bound (not a CI)')]
 fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.535,.071),ncol=3,frameon=False,fontsize=8.2,handlelength=1.4,columnspacing=2)
 fig.text(.09,.032,'48 dependent counterfactuals; 12 market seeds. Exact upper − achieved ≤ 4.58 × 10⁻⁹, so bounds overlap markers.',fontsize=8,color='#4b5563')
 out=ROOT/'research/learned-opponent-figures';out.mkdir(parents=True,exist_ok=True)
 stem=out/'learned-incentive-gains';description='All48 audited labels; actual terminal histories; mathematical discount19/20. '+receipt['manifest']+'; audit '+receipt['audit']
 fig.savefig(stem.with_suffix('.png'),dpi=220,metadata={'Software':'matplotlib','Description':description})
 fig.savefig(stem.with_suffix('.svg'),metadata={'Date':None,'Creator':'Matplotlib','Description':description})
 plt.close(fig)
 checks={'scope':'All48 complete audited response records; achieved gain and exact best-improvement upper are distinct; outward display/plot floats never decide signs; no CI or clock-only causal effect',
  'builderSha256':digest(__file__),'summarySha256':digest(summary_file),'primaryManifestSha256':receipt['manifest'],'independentAuditSha256':receipt['audit'],'records':48,'marketSeeds':12,'figsizeInches':[9.2,3.7],
  'maximumRemainingGapExact':next(r['certificate']['responseOptimalityGap'] for r in rows if exact(r['certificate']['responseOptimalityGap'])==max_gap),
  'figures':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in [stem.with_suffix('.png'),stem.with_suffix('.svg')]}}
 (out/'figure-checks.json').write_text(json.dumps(checks,separators=(',',':'))+'\n',encoding='utf-8')
 print(json.dumps(checks,separators=(',',':')))
 return checks
if __name__=='__main__':build()
