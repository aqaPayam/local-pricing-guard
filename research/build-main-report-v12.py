"""V12 report: guarded welfare, incentives, and equal-clock learning. No learning or economic cases are run here.

Complete authoritative learned-opponent acceptance must precede outputs.
V9/V10 builders, reports and figures remain preserved. This builder reuses
their accepted evidence and generates only the distinct V11 report.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
from importlib.util import spec_from_file_location,module_from_spec
from xml.sax.saxutils import escape
import sys,json,hashlib,re,argparse,types
sys.dont_write_bytecode=True
try:import reportlab
except ImportError:sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'))
from reportlab.platypus import SimpleDocTemplate,Paragraph,PageBreak,Image,Table,TableStyle,Spacer,HRFlowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'output/pdf';FIG=ROOT/'research/capacity-figures';MIXFIG=ROOT/'research/mixed-timing-figures';LEARNFIG=ROOT/'research/learned-opponent-figures';MATCHFIG=ROOT/'research/matched-clock-figures'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def need(ok,text):
 if not ok:raise ValueError(text)
def ratio(x):return Fraction(int(x['numerator']),int(x['denominator']))
def val(x):return float(ratio(x))
def signed(x):return '0' if x==0 else (f'{x:+.3e}' if abs(x)<.0005 else f'{x:+.3f}')
def mid(x):return float((Decimal(x['lower'])+Decimal(x['upper']))/2)
def module(name):
 spec=spec_from_file_location(name.replace('-','_'),ROOT/'research'/name);m=module_from_spec(spec);spec.loader.exec_module(m);return m
def evidence():
 # Do not open learner outcomes until the complete independent receipt passes.
 prefix='research/adaptive-learning-results/'
 audit=read(prefix+'independent-audit.json')
 need(audit.get('passed') is True and audit['runs']==192 and audit['checkpoints']==384 and audit['fullTrainingReplay'] is False,'Complete independent learner audit required')
 for key,name in [('studyManifestHash','manifest.json'),('resultsSha256','results.json'),('indexSha256','index.json'),('completionSha256','completion.json')]:need(audit[key]==sha(prefix+name),'Learner audit binding differs '+name)
 need(audit['auditorSourceHash']==sha('research/audit-adaptive-learning.py'),'Auditor source changed')
 summary=read(prefix+'summary.json');web=read(prefix+'web-data.json')
 need(web['meta']['summarySha256']==sha(prefix+'summary.json') and web['meta']['independentAuditSha256']==sha(prefix+'independent-audit.json'),'Display evidence identity differs')
 need(summary['analysisSourceHash']==sha('research/adaptive-analysis.js') and summary['counts']['runs']==192 and summary['counts']['checkpoints']==384,'Descriptive source/inventory changed')
 for p,digest in summary['inputHashes'].items():need(sha(p)==digest,'Descriptive dependency changed '+p)
 structural=module('build-capacity-figures.py').structural_evidence()
 return structural,summary,audit

def mixed_evidence():
 # All timing outcomes remain behind the authoritative two-component audit.
 prefix='research/mixed-timing-results/'
 audit=read(prefix+'independent-audit.json')
 need(audit.get('passed') is True and audit.get('requiresOrchestrator') is False and audit.get('continuousChecksComputedInProcess') is True,'Complete authoritative timing audit required')
 need(audit.get('models')==24 and audit.get('targetLabels')==120 and audit.get('finiteTargetLabels')==40 and audit.get('continuousTargetLabels')==80,'Full timing inventory required')
 need(audit.get('inheritedPremiseRevalidation') is False,'Inherited-premise reuse scope must remain explicit')
 for key,name in [('studyManifestHash','manifest.json'),('resultsSha256','results.json'),('indexSha256','index.json'),('completionSha256','completion.json'),('journalSha256','journal.jsonl'),('executionStartSha256','execution-start.json')]:need(audit[key]==sha(prefix+name),'Timing audit/output binding differs '+name)
 for key,name in [('auditorSourceHash','audit-mixed-study.py'),('controlAuditorSourceHash','audit-mixed-timing.js'),('continuousAuditorSourceHash','audit-mixed-continuous.py'),('arithmeticBackendHash','audit-continuous-study.py')]:need(audit[key]==sha('research/'+name),'Timing independent source differs '+name)
 need(all(audit.get('corruptionNegativeControls',{}).values()) and audit.get('corruptionNegativeControls'),'Timing scientific corruption checks required')
 summary=read(prefix+'summary.json');web=read(prefix+'web-data.json')
 need(summary['meta']['independentAuditPassed'] is True and summary['meta']['independentAuditSha256']==sha(prefix+'independent-audit.json'),'Timing descriptive audit binding differs')
 for name,key in [('mixed-timing-analysis.js','analysis'),('mixed-timing-format.js','format')]:need(summary['meta']['sourceHashes'][key]==sha('research/'+name),'Timing descriptive source differs')
 for name,h in summary['inputHashes'].items():need(sha(name)==h,'Timing descriptive dependency differs '+name)
 need(web['meta']['summarySha256']==sha(prefix+'summary.json') and web['meta']['exporterSha256']==sha('research/build-mixed-timing-web.js'),'Timing display binding differs')
 need(len(summary['models'])==24 and len(summary['targetRows'])==120 and len(web['finiteGames'])==8,'All timing display records required')
 return summary,audit

def hratio(x):return Fraction(int(x['numeratorHex'],16),int(x['denominatorHex'],16))

def learned_evidence():
 prefix='research/learned-opponent-results/'
 audit=read(prefix+'independent-audit.json')
 need(audit.get('passed') is True and audit.get('allPlannedLabelsRetained') is True and audit.get('labels')==48,'Complete learned-partner inventory acceptance required')
 need(audit.get('scientificallyAvailableRecords')==48 and audit.get('tightRecords')==48 and audit.get('executionFailures')==0,'V11 describes this accepted all 48-tight execution; failure inventories need different report wording')
 for key,name in [('studyManifestHash','manifest.json'),('resultsSha256','results.json'),('indexSha256','index.json'),('completionSha256','completion.json'),('journalSha256','journal.jsonl'),('runStartSha256','execution-start.json')]:need(audit[key]==sha(prefix+name),'Learned-partner binding differs '+name)
 need(audit['auditorSourceHash']==sha('research/audit-learned-opponent.py'),'Learned-partner independent source differs')
 need(audit.get('fullTrainingReplay') is False and audit.get('optimizerIterationsReplayed') is False and audit.get('inheritedEconomicReenumeration') is False,'Learned-partner verification scope differs')
 need(audit.get('corruptionNegativeControls') and all(audit['corruptionNegativeControls'].values()),'Learned-partner negative controls required')
 summary=read(prefix+'summary.json');web=read(prefix+'web-data.json')
 need(summary['meta']['independentAuditSha256']==sha(prefix+'independent-audit.json') and summary['meta']['audit']==audit,'Learned-partner descriptive acceptance differs')
 need(len(summary['records'])==48 and len(summary['seedMeans'])==24 and len(summary['pairedDifferences'])==12,'Complete dependent labels/seed units required')
 for name,h in summary['inputHashes'].items():need(sha(name)==h,'Learned-partner descriptive dependency differs '+name)
 need(web['meta']['summarySha256']==sha(prefix+'summary.json') and web['meta']['webExporterSha256']==sha('research/build-learned-opponent-web.js'),'Learned-partner web binding differs')
 return summary,audit

def mixed_figure(summary):
 # Figure scope was chosen before cases: all8 scenarios, all3 models, target95.
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.5,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'mixed-timing-main-v1','savefig.facecolor':'white'})
 fig,ax=plt.subplots(figsize=(9.2,3.9))
 specs=[('finite',-.19,'o','#b26b48','Saved finite game'),('effective',0,'s','#24656b','Effective continuous'),('nominal',.19,'D','#72816c','Nominal sensitivity')]
 labels=['Base reference','Taste scale 0.5','Lower quality','Lower cost','11-quote reference','31-quote reference','Half tolerance','Double tolerance']
 for kind,offset,marker,color,label in specs:
  first=True
  for index,scenario in enumerate(summary['scenarioOrder']):
   row=next(t for t in summary['targetRows'] if t['scenario']==scenario and t['kind']==kind and t['label']=='cap-95pct')
   y=index+offset;rates=row['rates']
   if rates is None or rates['relativeSavingBoundsExact'] is None:
    text='finite: startup only' if kind=='finite' and row['statusCategory']=='startup-only' else kind+': '+row['statusCategory']
    ax.text(.99,y,text,transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=8,color=color)
    continue
   lo=100*val(rates['relativeSavingBoundsExact']['lower']);hi=100*val(rates['relativeSavingBoundsExact']['upper'])
   achieved=100*val(rates['constructedSavingExact'])/val(rates['fixedRateExact'])
   ax.errorbar([achieved],[y],xerr=[[max(0,achieved-lo)],[max(0,hi-achieved)]],fmt=marker,color=color,mfc='white' if kind=='nominal' else color,ms=6,capsize=2,lw=1,label=label if first else None,zorder=3)
   first=False
 ax.set_yticks(range(8),labels);ax.invert_yaxis();ax.set_xlim(0,35);ax.set_xticks(range(0,36,5));ax.grid(axis='x',alpha=.18)
 ax.set_xlabel('Relative reduction in long-run cap-rule applications (%)')
 ax.set_title('Same cap and 95% reference target: mixed gaps versus each model’s own fixed period',loc='left',fontsize=10.5,pad=12)
 ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),ncol=3,frameon=False,fontsize=9)
 fig.tight_layout(rect=(0,.07,1,1));MIXFIG.mkdir(parents=True,exist_ok=True)
 fig.savefig(MIXFIG/'timing-frontier.png',dpi=240,bbox_inches='tight',metadata={'Software':'Market Lab / Matplotlib'})
 fig.savefig(MIXFIG/'timing-frontier.svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)

def adaptive_figure(summary):
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'capacity-main-v1','savefig.facecolor':'white'})
 fig,axes=plt.subplots(2,2,figsize=(9.2,5.2),sharex=True)
 for c,ax in zip(summary['primaryContrasts'],axes.flat):
  values=[val(p['difference']) for p in c['pairedRows']]
  for i,y in enumerate(values):ax.plot([i+1,i+1],[0,y],c='#ccd7c7',lw=1)
  ax.scatter(range(1,13),values,s=22,c='#24656b',zorder=3);ax.axhline(0,c='#737c70',lw=.9,ls='--')
  ax.axhline(c['mean'],c='#b26b48',lw=1,label='Mean paired difference')
  ax.set_title(('Original tolerance' if c['scenario']=='base-g15-t1' else 'Half tolerance')+' / '+c['qInit']+' scores',loc='left',fontsize=10)
  ax.set_xticks(range(1,13),[str(i).zfill(3) for i in range(1,13)],fontsize=7);ax.grid(axis='y',alpha=.15)
  ax.set_ylabel('Customer-benefit difference');ax.set_xlabel('Whole-market seed suffix (907xxx)')
 axes[0,0].legend(fontsize=8,frameon=False,loc='lower left');fig.tight_layout(h_pad=1.8,w_pad=2)
 FIG.mkdir(parents=True,exist_ok=True)
 fig.savefig(FIG/'adaptive-paired-seeds.png',dpi=240,bbox_inches='tight',metadata={'Software':'Market Lab / Matplotlib'})
 fig.savefig(FIG/'adaptive-paired-seeds.svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)

def matched_evidence(audit_sha):
 path=ROOT/'research/build-matched-clock-web.py';m=types.ModuleType('matched_report_export');m.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
 result=m.load_accepted(ROOT/'research/matched-clock-results/analysis.json',audit_sha)
 audit=read(result['meta']['audit']['file'])
 need(sha(result['meta']['audit']['file'])==audit_sha,'Accepted matched audit changed')
 need(audit.get('studyManifestHash')=='dcd573fc866e59cd1a27c3158cb9e9be58702034f9fb250e251c54f579a01817' and audit.get('scientificallyAvailableCheckpoints')==48 and audit.get('finalAvailable')==24 and audit.get('fullTrainingReplay') is True and audit.get('replayComplete') is True,'V12 describes this complete accepted matched execution; a failed inventory needs different report wording')
 need(result['completePairDescription']['signCounts']=={'positive':12,'zero':0,'negative':0},'V12 matched interpretation differs from its described execution')
 receipt=read('research/matched-clock-figures/figure-receipt.json')
 need(receipt['independentAuditSha256']==audit_sha and receipt['analysisSha256']==sha('research/matched-clock-results/analysis.json'),'Matched figure evidence differs')
 need(receipt.get('builderSha256')==sha('research/build-matched-clock-figure.py') and receipt.get('rows')==12 and receipt.get('availablePairs')==12,'Matched figure source or inventory differs')
 for name,ref in receipt['files'].items():need(sha(name)==ref['sha256'] and (ROOT/name).stat().st_size==ref['bytes'],'Matched figure file changed')
 return result,audit

def main():
 cli=argparse.ArgumentParser();cli.add_argument('--audit-sha',required=True);args=cli.parse_args()
 matched,matched_audit=matched_evidence(args.audit_sha)
 learned,learned_audit=learned_evidence()
 mixed,mixed_audit=mixed_evidence()
 structural,summary,audit=evidence();recurring,misspec,incentive,meshes,continuous=structural
 base=next(r for r in recurring if r['scenario']=='base-g15-t1' and r['continuum']=='effective');target=next(t for t in base['comparisons'] if t['label']=='cap-95pct')
 _,misspec_raw,_,_=misspec;mb=next(r for r in misspec_raw['records'] if r['scenario']=='base-g15-t1' and r['continuum']=='effective');mt=next(t for t in mb['targets'] if t['label']=='cap-95pct')
 _,ir,_,_,_=incentive;ib=next(r for r in ir['records'] if r['scenario']=='base-g15-t1' and r['periodSlot']['id']=='closed-effective-95pct' and r['focalSeller']=='A' and r['discount']['numerator']=='19')
 OUT.mkdir(parents=True,exist_ok=True)
 styles=getSampleStyleSheet()
 for name,font,size,leading in [('Body','Times-Roman',10.6,13.5),('Appendix','Times-Roman',10,12.5),('Small','Times-Roman',9.4,11.8),('Heading','Times-Bold',12.8,16),('Caption','Times-Roman',9,11.3),('Equation','Courier',9.2,12.4)]:styles.add(ParagraphStyle('M'+name,fontName=font,fontSize=size,leading=leading,spaceAfter=8))
 styles.add(ParagraphStyle('MTitle',fontName='Times-Bold',fontSize=21,leading=24.5,alignment=TA_CENTER,spaceAfter=12));styles.add(ParagraphStyle('MCenter',fontName='Times-Roman',fontSize=10.3,leading=13,alignment=TA_CENTER,spaceAfter=8))
 styles.add(ParagraphStyle('MHash',fontName='Times-Roman',fontSize=8.4,leading=10.2,spaceAfter=4))
 story=[];page_sections=[];table_count=0;paragraph_default='Body'
 def p(s,style=None):story.append(Paragraph(s,styles['M'+(style or paragraph_default)]))
 def h(s):p(s,'Heading')
 def page(section):
  if story:story.append(PageBreak())
  page_sections.append(section)
 def fig(name,caption,width=491):
  path=(MATCHFIG if name=='matched-clock-paired.png' else LEARNFIG if name=='learned-incentive-gains.png' else MIXFIG if name=='timing-frontier.png' else FIG)/name;w,hh=PILImage.open(path).size;story.append(Image(str(path),width=width,height=width*hh/w));p(caption,'Caption')
 def tab(head,rows,widths,caption):
  nonlocal table_count
  table_count+=1;p(f'Table {table_count}. '+caption,'Caption')
  cells=[[Paragraph(escape(str(x)),styles['MSmall']) for x in row] for row in [head]+rows]
  t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#71856f')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eff2e9')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.append(t);story.append(Spacer(1,9))
 page('Title, abstract and question')
 story.append(HRFlowable(width='100%',thickness=2,color=colors.HexColor('#263b35'),spaceAfter=12))
 p('When a Local Pricing Guard<br/>Is Not a Welfare Promise','Title');p('Finite precision, continuing intervention and adaptive behavior in a bounded logit market','Center')
 story.append(HRFlowable(width='100%',thickness=.6,color=colors.HexColor('#263b35'),spaceAfter=11))
 p('Mohammadpayam Teabi<br/>AI Collusion Research Sprint · 26 October 2026','Center');p('Sprint organizers: Apart Research · Poseidon Research · AE Studio','Center')
 new_mean=matched['primarySummary']['meanDifference']
 new_result=('The paired mean customer-benefit increase is '+f'{val(new_mean):.3f}'+' units; all twelve differences are positive.' if new_mean is not None and matched['completePairDescription']['signCounts']=={'positive':12,'zero':0,'negative':0} else 'The complete paired outcome and every unavailable endpoint are retained without selective replacement.')
 abstract='A local pricing guard can satisfy immediate profit checks while failing a customer-benefit promise over time. We study a bounded symmetric logit duopoly where permitted prices have near-best immediate profit against the last public rival price. One cap round appears protective in a coarse inherited game, but the base continuous worst long-run customer benefit is about 66.272, below the unchanged 95% target of 68.513. An attained upper-price envelope characterizes fixed and mixed timing of the same physical cap. A funded calendar minimizes worst-path cap-rule frequency within causal cap-or-guard controllers protecting every activation prefix; base effective-continuous frequency falls about 7.29% from its best fixed period. Separate finite and continuous calculations retain all 120 target labels. An earlier 192-run tabular-learning comparison has unequal clock capacities. A prospectively frozen follow-up matches five public phases and dense allocated memory in 24 two-million-round runs, with all-round independent reexecution. '+new_result+' This measures ongoing enforcement through learning and evaluation together. A separate 48-label audit against frozen learned partners certifies profitable unilateral responses in 33 cases and zero attained gains in 15; private gains can lower eventual-cycle customer benefit. These finite-budget, full-information results do not establish convergence, equilibrium, collusive intent or discoverability. The contribution is a model-specific guarantee audit, controlled behavioral comparison and graphical benchmark using established methods.'
 words=len(abstract.split());need(150<=words<=250,'Abstract length differs');p('<b>Abstract.</b> '+abstract,'Small')
 h('1 The problem: a local check and a long-run promise')
 p('Two shops choose prices simultaneously. Each wants its own profit. An external guard checks a proposed price against the other shop\'s <i>last completed</i> price. Passing that check says little by itself about what customers obtain after many executions. We ask what customer-benefit promise survives a one-time handover back to this guard, and what continuing control is needed for a stronger promise.')
 p('A cap is a real market round: it limits both executed prices, makes purchases and earns profit and customer surplus. It is not a free reset of a chart. Our human game deliberately lets a coordinator choose both shops\' prices. That illustrates permitted behavior; it does not establish independent collusion or supply human experimental data.')
 p('<b>What is added.</b> The linked sprint starter already provides replacement, history, objective and checkpoint-branch experiments [1]. We audit an explicit external price rule: precision, attainable adverse behavior, same-cap timing, model reserve, local learning and individual responses against saved learned partners. Known control and learning methods are credited below; priority for these ingredients is not claimed.','Small')
 page('Model and quantifiers')
 h('2 A self-contained game and the scope of each claim')
 p('There are B potential buyers, two symmetric inside goods of quality v and cost c, an outside option of normalized utility zero, and taste scale mu&gt;0. At executed physical prices p_A,p_B, let e_i=exp((v-p_i)/mu). Expected demand, private profit and customer surplus are:')
 p('D_i = B*e_i / (1+e_A+e_B)<br/>R_i = (p_i-c)*D_i<br/>C(p_A,p_B) = B*mu*log(1+e_A+e_B)','Equation')
 p('The base calibration is B=100, v=2, c=1 and mu=0.25. Its inherited bounded physical price domain is approximately [1.427721, 1.970186]. The inherited cap is held exactly at its saved numerical value p_cap=1.4664687420450921; it is not moved to a different continuous Nash price when timing changes. The original 15-quote reference gives cap customer benefit approximately 72.119. The unchanged relaxed 95% target F is approximately 68.513, stored as an absolute numerical threshold. Different experiments do not quietly redefine this target.')
 p('Let q be the rival\'s previous completed price. The guard permits every price in the bounded domain whose immediate expected profit is within epsilon of the best immediate profit available against q:')
 p('S(q) = {p : max_z R(z,q) - R(p,q) &lt;= epsilon + tau}<br/>U(q) = max S(q)','Equation')
 p('Epsilon=0.1 in the base mask; the learner sensitivity uses epsilon=0.05. Tau is the inherited 10^-12 numerical comparison allowance. This is a lagged one-step modeled profit-loss rule, not calibrated regret and not loss against the rival\'s hidden current action. Both sellers are externally constrained; they may coordinate, randomize or use arbitrary history within the legal sets when we state an <i>all-policy</i> guarantee.')
 tab(['Object','What is computed','What it does not establish'],[['Saved finite game','Exact rational comparisons on the saved binary64 payoff weights and legal masks.','Exact-real logit inequalities or grid-invariant protection.'],['Validated continuous model','Directed Decimal interval bounds for imported real constants under checked monotonicity and contraction conditions.','An independent transcendental backend or empirical market validity.'],['Learning behavior','Fixed-budget local Q-learning, paired seeds, saved-policy continuation and visit support.','Convergence, equilibrium, intent, or LLM behavior.'],['Frozen-partner incentives','Exact achieved discounted values and a best-response upper bound from saved histories.','Discoverability, resumed learning or every-state equilibrium.']],[100,194,197],'Four evidence types and their distinct scopes.')
 p('In the graphical cap game a saved 61-quote base mesh is augmented by the exact old cap, prioritizing that quote over a nearby mesh quote. The two learner masks each have 62 choices. These are separate numerical games from the original 15-quote and refinement meshes; a continuous period is independently checked in the finite game before any finite guarantee is asserted.','Small')
 p('Finite masks inherit the binary64-rounded epsilon+tau comparator. Continuous validation separately treats imported constants as exact reals and reports nominal/effective allowances. “Continuous limit” describes the model result, not a proof that bit-level JavaScript mask rounding vanishes.','Small')
 h('Different questions, different outcomes')
 p('An all-policy floor concerns every allowed path. A training average concerns the actual exploratory updates. A frozen continuation stops updates and exploration and follows the saved greedy choices. These answer different questions, and the paper and game keep them visible separately.')
 page('Price precision and recurring protection')
 h('3 The handover promise weakens with richer prices')
 p('Under the verified base continuous assumptions, U is monotone and contractive on the inherited interval. It has a unique fixed point q*. Prices on every permitted path are bounded above by iterating U, and the upper choices themselves are permitted. Since customer surplus decreases in either price, C*=C(q*,q*) is a tight worst long-run floor. This does not require every permitted price path to converge.')
 fig('precision-and-timing.png','Figure 1. Base condition. (a) Saved finite one-cap floors at the predeclared mesh sizes and the validated continuous floor. Refinement is not monotone across all coarse meshes; the 11-choice case is already worse than the 15-choice case. (b) A different object: validated continuous recurring-cap floors G_K, with the same old physical cap and unchanged target. These plots show all-policy capacity, not observed learning.')
 p(f'The 15-choice one-cap floor is about 72.119, while the 1,921-choice diagnostic is about 66.298 and the continuous limit is {mid(base["inheritedContinuum"]["consumerSurplus"]):.3f}. The original target is {float(target["actualThresholdExact"]):.3f}. A finite initializer changes a transient; it cannot raise the asymptotic continuous floor above C* when the unchanged guard then runs forever.','Small')
 h('A tight repair within the fixed-period family')
 p('Keep physical price units: let a_0=p_cap and a_(j+1)=U(a_j), and put r_j=C(a_j,a_j). The actual first cap is phase 0; K-1 guard rounds follow. The worst repeated cycle is attained by both shops choosing their maximum legal quote:')
 p('G_K = (r_0 + ... + r_(K-1)) / K','Equation')
 p('The verified sequence r_j decreases, so every cap-first finite running average is at least G_K; a later individual round can still fall below it. The base target permits K=4 (G_4 about 68.676), but K=5 fails (about 68.229). Both 99% and 100% reference targets need K=1 in these audited labels. “Largest safe K” means largest <i>fixed integer period in this same-cap family</i>. Frequency 1/K counts rule applications, not economic cost, changed quotes or autonomy.','Small')
 page('Mixed timing and the integer-period restriction')
 h('4 Can mixed gaps improve the same protection promise?')
 p('Let S_l sum the first l adverse rewards and K be the largest safe fixed period. A K-round block banks a=S_K-KF&gt;=0; a K+1 block spends -b, where b=S_(K+1)-(K+1)F&lt;0. Fund that entire debt before using the longer gap. Concavity then protects every activation prefix, including one ending inside a block.')
 p('long-block fraction p = a/(a-b)<br/>minimum worst-path cap-rule rate = 1/(K+p)','Equation')
 p('The feasible maximum-price response and Jensen inequality, including the last partial gap, force this lower rate for any causal two-mode controller. Bounded funded credit attains it. This is asymptotic minimax optimality within the stated family; sliding windows and pointwise minimum cap counts are different promises. The guard remains active between caps. The methods have close prior art [9–12]; the full conditional proof is in MIXED_TIMING_THEORY.md.','Small')
 fig('timing-frontier.png','Figure 2. Prospectively selected 95% target, all eight scenarios and three model interpretations. Reductions use each record’s own best fixed period. Points are constructed feasible reductions; continuous enclosures are too narrow to resolve graphically but remain nonzero. Startup-only rows have no largest fixed comparator and are labeled rather than plotted as zero savings. Reference-grid labels identify inherited conditions; finite games have 61/62 choices.')
 timing_base=[next(t for t in mixed['targetRows'] if t['scenario']=='base-g15-t1' and t['kind']==kind and t['label']=='cap-95pct') for kind in ['finite','effective']]
 timing_rows=[]
 for t in timing_base:
  r=t['rates'];timing_rows.append(['Saved finite' if t['kind']=='finite' else 'Effective continuous',str(r['bestFixedK']),f'{val(r["fixedRateExact"]):.6f}',f'{val(r["constructedRateExact"]):.9f}',f'{100*val(r["relativeSavingBoundsExact"]["lower"]):.4f}%',t['constructedCalendarTiming']['firstLongExecution']])
 tab(['Base 95% model','Own K','Fixed rate','Constructed rate','Reduction','First long round'],timing_rows,[107,37,70,93,82,102],'Same physical cap and target, different numerical models. Rates are long-run cap applications per execution; decimals are approximate.')
 p('All 120 labels remain: 40 finite give 10 startup-only cases and 30 exact adjacent optima; 80 continuous give 14 startup-only cases and 66 enclosures. All 96 adjacent savings are positive because a&gt;0 here, not because 96 empirical trials succeeded. Every continuous rate enclosure has nonzero width (maximum below 4.19e-28). Twelve finite first-long times exceed the 256-round preview; 26 continuous times exceed 64 rounds. At the 100% target, first long gaps require millions of executions. The 192-run learner study below keeps its old fixed clocks; it supplies no behavior under this new calendar.','Small')
 page('Demand reserve and learned individual incentives')
 h('5 Customer protection and private incentives')
 p('The same cap and legal rule have distinct modeling and strategic boundaries. In the bounded quality-error test, base K=4 has positive reserve only to about d=0.006963. At dbar=0.01 its worst customer benefit is about 68.442, below the unchanged 68.513 target; conservative integer redesign uses K=3, or K=2 at dbar=0.05. Quality loss itself harms customers. This is one structural sensitivity, not general robustness.')
 h('Can a learned shop earn more against its frozen partner?')
 p('A targeted follow-up uses the original 62-quote mask, zero initialization, all twelve seeds, both sellers, and startup-only versus the actual saved selected95 K=4 clock. The 48 labels continue each final 2M history and NEXT phase, with no fresh cap. One seller changes its entire policy; its deterministic learned partner stays fixed. The white-box optimizer knows the complete partner, payoffs and legal supports. It does not model discovering a strategy from limited observations.')
 fig('learned-incentive-gains.png','Figure 3. All 48 exact attained discounted-profit gains, both sellers and controllers. Seed identities are paired and dependent; whiskers show possible best-gain upper bounds, not confidence intervals. The maximum remaining response gap is below 4.58e-9 profit units, so the whiskers are visually indistinguishable at this scale. Zero attained gains remain visible. Gamma is mathematical 19/20; all decimals are approximate.')
 gain_rows=[]
 for c in learned['controllerSummaries']:
  signs=c['rawGainSignCounts'];gain_rows.append(['Startup, then guard' if c['controller']=='startup-only' else 'Recurring K=4',str(c['available'])+'/24',str(signs['positive'])+' / '+str(signs['zero'])+' / '+str(signs['negative']),f'{float(hratio(c["minimum"])):.6f}',f'{float(hratio(c["median"])):.6f}',f'{float(hratio(c["maximum"])):.6f}'])
 tab(['Controller','Available','Gain + / 0 / -','Minimum','Median','Maximum'],gain_rows,[111,57,101,74,74,74],'Complete achieved-gain summaries in discounted profit units; exact signs, descriptive seller labels, no pooled independence.')
 p('All 48 responses meet the prospective 1e-6 absolute gap target. Largest relative attained gains are about 0.896% of baseline discounted profit for startup and 2.355% for K=4: useful but modest. All baseline/response paths have exactly zero discounted exposure to originally unvisited states or never-tried chosen actions for either firm. This removes that particular explanation of these attained gains, not every off-path or learning concern.','Small')
 p('Customer benefit and private gain are separate. Response-cycle customer benefit falls in 16/24 K=4 cases, rises in 6 and is unchanged in 2; startup gives 11 rises and 13 unchanged. These are eventual-cycle means, not discounted welfare or finite-prefix guarantees. A profitable allowed response does not invalidate the all-policy welfare floor or prove collusive intent. The earlier 96-label fixed-script audit remains in the evidence; its special cap-reset block simplification does not apply to learned history-dependent partners [4].','Small')
 page('Adaptive learners and matched architecture')
 h('6 A controlled follow-up to the learner comparison')
 p('The earlier study retains 192 runs: two saved 62-price masks in one economic calibration, four schedules, two Q initializations and twelve whole-market seeds. Each run has two million simultaneous rounds and 1M/2M checkpoints. The startup controller has two phase labels while recurring controllers have K; equal rounds therefore do not match representation capacity. That study remains informative about its declared systems, but cannot isolate cap frequency or clock capacity.')
 p('Both firms use established masked tabular Q-learning, own expected profit and private score tables. They choose simultaneously from the last completed price pair. Next-state bootstrap maxima for both firms are captured before either current update; exact ties choose the smallest original quote index:')
 p('Q(s,a) <- Q(s,a) + 0.1*[R_own + 0.95*max_(legal a_next) Q(s_next,a_next) - Q(s,a)]','Equation')
 tab(['New matched factor','Prospectively fixed values'],[
 ['Physical game','Same original-tolerance 62-price table, cap and guard; no new payoff enumeration.'],
 ['Shared public clock','0 -> 1 -> 2 -> 3 -> 4 -> 1. Phase 0 occurs once; phases 1-4 recur in both arms.'],
 ['Only rule difference','Startup caps only phase 0. Recurring caps phases 0 and 4; all other phases use the original guard.'],
 ['Private allocation','Each firm has 5*62^3 = 1,191,640 binary64 Q cells and equal uint32 visit-count capacity, initialized to positive zero.'],
 ['Budget and streams','12 intentionally reused seed IDs, both arms, 2M rounds. Paired private xoshiro128** streams consume two words per firm per round.'],
 ['Learning and endpoints','Alpha 0.1; binary64 gamma 0.95; exploration 1 to 0.01. Checkpoints 1M/2M; final actual-history frozen-cycle customer benefit is primary.']],[107,384],'Separate 24-run matched-clock follow-up; no old run is relabeled or replaced.')
 p('At both checkpoints the NEXT phase is 4: guard for startup, cap for recurring. Keep each arm\'s actual price history and full cap-state memory; do not add a fresh phase 0 cap. Both arrays have the same allocated capacity, while legal actions, experience and visits differ. Four recurrent clock labels also let the startup learner condition on public time. The clock closes controller state; opponent adaptation still makes each firm\'s learning problem nonstationary.')
 p('This contrast measures the total effect of changing ongoing legal control during training and frozen evaluation. It does not isolate formation from enforcement or explain how much of the older gap came from representation. The K=4 rhythm follows the old learned stratum; it is distinct from finite K=5 or the later funded calendar. All twelve exact paired rows and their exact arithmetic mean are planned; any missing final pair nulls that mean. No new CI or p-value is planned.','Small')
 p('All 29 scientific sources, 182 inputs, 24 ordered plans, full artificial pipeline tests and a maximal serialized rehearsal were frozen before new training. An independently authored direct-scan implementation repeats the complete 48M-round trajectory from zero, compares all 4,800 ten-thousand-round transcript hashes and both complete checkpoints, and independently reconstructs every greedy graph. Shared V8 arithmetic and inherited modeled payoffs remain explicit limitations.','Small')
 page('Earlier comparisons and matched-clock findings')
 h('7 Behavioral results with the capacity objection visible')
 rows=[]
 for c in summary['primaryContrasts']:rows.append(['Original' if c['scenario']=='base-g15-t1' else 'Half',c['qInit'],signed(c['mean']),f'{signed(c["range"]["minimum"])} to {signed(c["range"]["maximum"])}',f'{signed(c["interval"]["lower"])} to {signed(c["interval"]["upper"])}'])
 tab(['Tolerance','Scores','Mean difference','All-seed range','Marginal 95% interval'],rows,[69,78,95,123,126],'Earlier 192-run study: selected95 minus startup actual-terminal cycle benefit. Each stratum has 12 paired seeds; approximate marginal seed-resample intervals are not market uncertainty or causal frequency estimates.')
 positive=sum(ratio(p['difference'])>0 for p in summary['primaryPairs']);zero=sum(ratio(p['difference'])==0 for p in summary['primaryPairs']);negative=48-positive-zero
 p(f'The older four-stratum means range from 2.391 to 2.946 units, with {positive}/48 positive rows. Its full training trajectory was not independently replayed; saved checkpoints, graphs, sampled updates and cloned probes were checked. The old and new systems are different versions, not interchangeable independent replications.','Small')
 fig('matched-clock-paired.png','Figure 4. New 24-run matched architecture: every final actual-terminal recurring-minus-startup cycle-benefit difference. Solid segments begin at zero; dashed vertical line is the planned all-twelve mean. All exact rows, including zero, reversed or unavailable outcomes, remain in the evidence. These are twelve whole-market seed contrasts with paired treatments in one saved finite model, with no confidence interval.')
 signs=matched['completePairDescription']['signCounts'];mp=matched['primarySummary']
 p('The new planned mean is '+(f'{val(mp["meanDifference"]):.6f} customer-benefit units.' if mp['available'] else 'unavailable: '+escape(mp['unavailableReason'])+'.')+f' Accepted pairs: {mp["availablePairs"]}/12; exact signs: {signs["positive"]} positive, {signs["zero"]} zero and {signs["negative"]} negative. Display decimals are approximate. Equal clock labels and allocated capacity therefore retain a positive difference in this execution; this is not proof of convergence or a causal explanation of the older larger gap.')
 p(f'Independent full replay accepted {matched_audit["scientificallyAvailableCheckpoints"]}/48 checkpoints and {matched_audit["finalAvailable"]}/24 final endpoints, with {matched_audit["executionFailures"]} execution failures. It reexecuted {matched_audit["replayedRounds"]:,} rounds. Aggregate full-replay and checkpoint-completeness flags are {matched_audit["fullTrainingReplay"]} and {matched_audit["replayComplete"]}; these concern only the new 24 runs. Every one of the 24 cycle-benefit endpoints changes between 1M and 2M, so these checkpoints give no convergence claim. Training-tail averages and arbitrary-state graph diagnostics remain secondary and separate from eventual-cycle means.','Small')
 tail_means=[];tail_signs=[]
 for c in summary['primaryContrasts']:
  pairs=[]
  for seed in summary['orderedSeeds']:
   def get(control):return next(r for r in summary['runs'] if r['scenario']==c['scenario'] and r['qInit']==c['qInit'] and r['seed']==seed and r['controller']['id']==control)['checkpoints'][1]['trainingTail']['means']['consumerSurplus']
   pairs.append(ratio(get('selected95'))-ratio(get('startup-only')))
  tail_means.append(float(sum(pairs,Fraction())/12));tail_signs.extend(pairs)
 endpoints=[(r,c) for r in summary['runs'] for c in r['checkpoints'] if c['step']==2000000]
 unvisited=sum(any(c['frozen']['actualTerminal']['visitSupport'][f]['unvisitedStates'] for f in ['A','B']) for r,c in endpoints)
 untried=sum(any(c['frozen']['actualTerminal']['visitSupport'][f]['neverTriedGreedyActions'] for f in ['A','B']) for r,c in endpoints)
 changed=sum(ratio(r['checkpoints'][0]['frozen']['actualTerminal']['means']['consumerSurplus'])!=ratio(r['checkpoints'][1]['frozen']['actualTerminal']['means']['consumerSurplus']) for r in summary['runs'])
 origin_changed=sum(ratio(c['frozen']['actualTerminal']['means']['consumerSurplus'])!=ratio(c['frozen']['freshCap']['means']['consumerSurplus']) for r,c in endpoints)
 page('Interpretation, contribution and access')
 h('8 What this adds, and what remains open')
 p('The strongest result is about <i>the scope of a protection promise</i>. A coarse finite game can give a reassuring one-cap result while a richer price interface admits worse allowed continuations. The continuous upper envelope explains the limit and gives an attainable worst cycle when the same physical cap is repeated. Calibration reserve and unilateral incentives identify different boundaries: model error can consume the old absolute target, while a worst permitted script need not be individually attractive.')
 p('The learner study adds behavior under a precisely declared controller, without replacing the all-policy proof by a favorable simulation. Its outcomes remain conditional on two masks, one calibration, chosen hyperparameters, finite budget and private-score initializations. Neither high prices nor a quiet frozen cycle establishes collusion, punishment, intent or equilibrium. The new learned-partner audit establishes modest unilateral opportunities against fixed saved policies, not mutual adaptation or punishment. The matched follow-up addresses clock labels and allocated memory in one stratum. Further work needs an unrestricted capability reference, learning sensitivity and tests with continued adaptation.')
 h('Relation to prior work and the sprint starter')
 p('Calvano et al. study profit-seeking learning and algorithmic pricing [2]. Eschenbaum et al. examine robustness, replacement and continued adaptation [3], and the sprint starter already branches histories, models and objectives [1]. Alshiekh et al. define action restriction and shielding, including reward credit and the need for persistent protection [5]. Brero et al. design ongoing platform interventions for consumer benefit [6]. Hartline et al. study a different, calibrated-regret regulation framework [7]. Periodic resetting and renewal-ratio control are established [8,9]. Lopes de Moraes and De Losso directly audit learned pricing incentives [4]. None should be repackaged here as our invention.')
 p('Our limited addition is a linked guarantee-capacity case: precision, a fixed physical cap, restricted minimax timing, bounded demand reserve, adaptive observations and certified learned-partner responses keep distinct quantifiers. Frozen-policy response MDPs are already explicit in [4], Sections3.2(iv),4.5; our standard Bellman bound is not a new algorithm. Adjacent timing mixtures already occur in Sun and Cyr [10]; uniform cumulative safety budgets appear in conservative bandits [11,12]. Our pricing-envelope reduction and validated comparison apply these ideas. The mixed result covers the same two actuators, not every intervention, cap strength or economic cost. No broad novelty or empirical-market superiority is established.')
 h('An accessible game, with evidence behind each view')
 p('Start at http://127.0.0.1:3003/. The two-shop challenges let a human choose both permitted quotes, see actual cap executions and separate earned customer benefit from a guaranteed buffer. The mixed-calendar page explains how earlier credit funds a longer gap. The one-shop profit challenge uses a public script and exact block score; the learner page reveals stored executions. The one-shop continuation lets a person choose against a saved deterministic learner. The paired /matched replay advances two accepted final worlds together, with equal-clock graphics, all twelve signed differences, undo and restart; finite earned scores stay separate from complete cycles and audited infinite values. These are explanatory artifacts and developer-tested controls, not a human usability study.')
 h('Reproduction')
 p('Start the local viewer with <font name="Courier">node research/demo-server.js</font>. Run <font name="Courier">python research/audit-learned-opponent.py</font> for the learned-partner response audit, <font name="Courier">python research/audit-mixed-study.py</font> for timing, or <font name="Courier">python research/audit-adaptive-learning.py</font> for saved learner artifacts. Use the pinned Python 3.13 runtime for research/audit-matched-clock-study.py to fully replay the new matched study; it checks without rewriting a receipt by default. These auditors verify without rewriting closed receipts by default. README links the raw manifests, source snapshots, earlier checkers and gated derivative builders. The full archive preserves numerical evidence; the smaller viewer archive explicitly omits large checkpoints and points to the full archive hash.','Small')
 p('Verification checks are coverage evidence, not experimental sample size. The exact finite calculations share their economic model; the continuous checkers use separate directed-interval code but the same Decimal transcendental backend. Independent AI-agent review does not substitute for external human peer review.','Small')
 page('References')
 h('References')
 refs=[
 ('1','Poseidon Research. Collusion hackathon starter, llm-cartel, 2026. Replacement, history, objective and checkpoint-branch code.','https://github.com/poseidon-research/collusion_hackathon/tree/main/llm-cartel'),
 ('2','E. Calvano, G. Calzolari, V. Denicolo and S. Pastorello. Artificial Intelligence, Algorithmic Pricing, and Collusion. American Economic Review 110(10), 3267-3297, 2020.','https://doi.org/10.1257/aer.20190623'),
 ('3','N. Eschenbaum, F. Mellgren and P. Zahn. Robust Algorithmic Collusion. arXiv:2201.00345,2022.','https://arxiv.org/abs/2201.00345'),
 ('4','K. Lopes de Moraes and R. De-Losso. Algorithmic Collusion Without Deterrence: Auditing the Punishment Mechanism in Q-Learning Pricing Agents. arXiv:2610.21867v2,2026.','https://arxiv.org/abs/2610.21867v2'),
 ('5','M. Alshiekh et al. Safe Reinforcement Learning via Shielding. AAAI 32(1), 2018. Sections 5.1-5.2.','https://doi.org/10.1609/aaai.v32i1.11797'),
 ('6','G. Brero, E. Mibuari, N. Lepore and D. C. Parkes. Learning to Mitigate AI Collusion on Economic Platforms. NeurIPS 35, 2022.','https://papers.neurips.cc/paper_files/paper/2022/file/f746974abd33c0015ca583a267dac1fd-Paper-Conference.pdf'),
 ('7','J. D. Hartline, C. Wang and C. Zhang. Regulation of Algorithmic Collusion, Refined: Testing Pessimistic Calibrated Regret. arXiv:2501.09740,2025.','https://arxiv.org/abs/2501.09740'),
 ('8','B. De Bruyne and F. Mori. Resetting in Stochastic Optimal Control. Physical Review Research 5, 013122, 2023.','https://doi.org/10.1103/PhysRevResearch.5.013122'),
 ('9','M. J. Neely. Fast Learning for Renewal Optimization in Online Task Scheduling. Journal of Machine Learning Research 22(279), 1-44, 2021.','https://www.jmlr.org/papers/v22/20-813.html'),
 ('10','Y. Sun and B. Cyr. Sampling for Data Freshness Optimization: Non-linear Age Functions. arXiv:1812.07241, 2019 version. Discrete two-threshold constrained sampling, Theorem 4.','https://arxiv.org/abs/1812.07241'),
 ('11','Y. Wu, R. Shariff, T. Lattimore and C. Szepesvari. Conservative Bandits. PMLR 48, 1254-1262, 2016.','https://proceedings.mlr.press/v48/wu16.html'),
 ('12','Y. Du, S. Wang and L. Huang. A One-Size-Fits-All Solution to Conservative Bandit Problems. AAAI 35(8), 7254-7261, 2021.','https://ojs.aaai.org/index.php/AAAI/article/view/16891')]
 for n,title,url in refs:p(f'[{n}] {escape(title)}<br/><link href="{escape(url)}" color="#24656b">{escape(url)}</link>','Small')
 h('Event and document context')
 p('Prepared for the AI Collusion Research Sprint organized by Apart Research. The public sprint page and template guide the question and report structure; this local PDF has not been submitted, externally deployed or endorsed. Affiliation has not been supplied by the named author and no institution is invented.','Small')
 p('<link href="https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25" color="#24656b">Official sprint page</link> · <link href="https://docs.google.com/document/d/1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg/mobilebasic" color="#24656b">Public report template</link>','Small')
 page('Mandatory limitations, dual use and disclosure')
 paragraph_default='Appendix'
 h('Appendix: Limitations and Dual-Use / Ethical Considerations')
 p('<b>Model limits.</b> The mathematical statements require the explicitly bounded, symmetric, known logit model and checked upper-map assumptions. The saved finite results certify numerical masks and reward weights, not exact-real profit inequalities. The continuous results concern imported constants and directed intervals, not measured economic uncertainty. The quality-error test is one fixed structural perturbation, not general robustness. Frequency counts external rule applications and does not measure implementation cost or useful seller agency.')
 p('<b>Behavioral limits.</b> The earlier 192-run study has one economic calibration, two tolerance masks, twelve paired seeds and fixed learning settings. Changing phase count changes state space and coverage. The separate 24-run follow-up matches five labels and allocated dense capacity, but does not equalize allowed actions, training visits or information about the adapting rival. Deterministic expected rewards omit sampled demand. Frozen eventual cycles may contain default unvisited scores. The 48-response follow-up freezes partners and supplies no learning-resumption, punishment-mechanism or equilibrium test. No unrestricted capability arm, convergence proof, LLM comparison or human participant study is included. White-box responses need not be discoverable from limited observations; equal training rounds alone do not match clock capacity or coverage, and equal allocation does not equalize legal experience. A positive fixed-script unilateral gain and a customer-benefit floor answer different questions.')
 p('<b>Verification limits.</b> Separate implementations reconstruct saved finite policy/graph/incentive calculations; they can share a conceptual or modeling error. Continuous primary and independent code share a Decimal transcendental backend. For the earlier 192-run study, sources, checkpoints, counts and cloned probes were audited but full training was not replayed. The new 24-run matched study independently reexecutes its full 48M rounds, hashes every 10K-round transcript block and checks all 48 dense checkpoints and graphs. It shares V8/Math.exp/crypto/zlib, reuses accepted saved economic inputs, and is neither cross-runtime validation nor externally authenticated per-round evidence. Earlier 192-run sampled after-run RSS exceeded its prospective soft memory target and is not a measured instantaneous peak. All declared runs and resource overruns remain visible.')
 p('<b>Dual use and ethics.</b> The toy model can illustrate adverse price coordination, so outputs should be framed as tests of safeguards rather than operational coordination advice for real firms. No real seller communication, customer data, participant recruitment, private economic data or autonomous commercial trading is involved. Human controls operate locally without claiming experimental observations. No external publication, submission, paid inference or deployment was performed in this stage.')
 h('LLM usage and author contributions')
 p('The project builds on the user\'s preexisting browser game and market scaffold, and on published sprint resources. Those are prior work. The guarantee-capacity analyses, new controller demonstrations, 192-run learner study and 48-case frozen-partner audit described here were developed in the current sprint work; frozen protocols, source snapshots and timestamps identify that new work. The report does not claim the inherited game or published starter as a new contribution.','Small')
 p('Mohammadpayam Teabi supplied the project, direction and author identity. Codex and collaborating AI agents substantially performed problem formulation, code implementation, mathematical derivation, experiment orchestration, independent AI-agent checks, analysis, visualization and drafting. The report is substantially AI-written; independent AI agents are not independent human peer reviewers. No human validation of the final science is implied.')
 p('The new guarantee-capacity analyses, 192-run tabular experiment, 24-run matched follow-up and frozen-partner response audit use no experimental language-model seller, paid model service, account-backed game player or remote inference. Codex development consumes coding-assistant allowance. Historical account-backed pilot material exists elsewhere in the earlier project and is not evidence for the claims in this report; the report does not claim that the entire project history had zero model usage.')
 h('Compact provenance pointers')
 for label,path in [('Learner frozen manifest','research/adaptive-learning-results/manifest.json'),('Learner independent receipt','research/adaptive-learning-results/independent-audit.json'),('Learner descriptive summary','research/adaptive-learning-results/summary.json'),('Learned response receipt','research/learned-opponent-results/independent-audit.json')]:
  need((ROOT/path).exists(),'Missing provenance file '+path);p(escape(label)+': '+escape(path)+'<br/>'+sha(path),'Hash')
 page('Mixed-timing proof, numerical scope and resource record')
 h('Appendix: Mixed-timing certificate details')
 p('The controller announces either the same full cap or the same full guard before current simultaneous quotes. The first execution is an actual cap. Cap A and each guard maximum U(q) are attainable; U(A) >= A, U is nondecreasing, and customer benefit decreases in each price. The cap-start orbit A,U(A),... gives an attained nonincreasing adverse reward list r_j tending to C*. Finite C* means this cap-start orbit, not arbitrary old guard cycles. The guarantee requires cumulative customer benefit at least F*T for every integer activation horizon T, every allowed seller policy and every realized controller random path.')
 p('For C*&lt;F&lt;=r_0, interpolate S_l linearly between integers. It is concave. If K is the largest integer with S_K&gt;=KF and K+1 strictly fails, its last nonnegative crossing is L*=K+a/(a-b). Against the feasible maximum-price path, m executed caps partition any horizon T into m positive integer gaps, including the last unfinished gap. Jensen gives F*T&lt;=sum_i S_(l_i)&lt;=m*S(T/m), hence m/T&gt;=1/L*. This supplies the lower bound for the worst-path limsup objective, even for history-dependent or randomized controllers. It does not impose that rate on more cooperative price paths.')
 p('For sufficiency, initialize virtual credit B=0 and choose K+1 only if B&gt;=-b; otherwise choose K. Update credit at block completion by b or a. The invariant 0&lt;=B&lt;a-b implies the long-block fraction tends to a/(a-b). Each block-prefix excess S_j-jF is concave and at least its smaller endpoint, so funding the negative block endpoint protects every interior activation prefix. A partial final block cannot change the limiting rate. Credit represents a certified reward surplus, not money or actual seller cooperation. With a=0 use K only. For F&lt;=C*, one startup cap then guard gives zero limiting rate; F&gt;r_0 is infeasible for this cap-first family. An initial reward plateau handles F=r_0.')
 p('Finite timing uses exact rationals of saved binary64 rewards and thresholds. Continuous credits have certified bounds aL&lt;=a&lt;=aU, bL&lt;=b&lt;=bU, with aL&gt;=0 and bU&lt;0. Since p increases in both credits, the rate bounds are [1/(K+p(aU,bU)), 1/(K+p(aL,bL))]. Exact rational lower credits aL,bL implement the upper endpoint. This conservative feasible rate is not the unknown exact-real optimum; decimal display bounds are a separate outward rounding. All 66 interior continuous enclosures here have nonzero width.')
 p(f'The frozen matrix has 24 model records and 120 labels, with MAX_K=65,536 and no query at 65,537. The accepted new audit rechecks 179 sums, 2,048 stored scalar-root certificates, all finite economics/masks and exact clocks/credit/previews, with {mixed_audit["checks"]:,} checks and 14 rejected scientific corruptions. It reuses hash-bound accepted global monotonicity/contraction and fixed-point certificates rather than re-proving them; both interval implementations share Decimal transcendentals. This is independent code validation, not a formal proof assistant or external human review.')
 mr=mixed['meta']['resources']
 p(f'Primary computation plus final identity checks took {mr["seconds"]:.3f} seconds. Largest after-model working-set sample was {mr["largestObservedRSSBytes"]:,} bytes, not a continuous peak. Primary output before completion was {mr["newOutputBytesBeforeCompletion"]:,} bytes, exceeding the 50,000,000-byte soft target; no labels were dropped or rerun. Derived displays and packaging are additional outputs. The first longer gap can be millions of executions away, so finite replay cap counts are not limiting-rate estimates. No new training or experimental model calls occurred.')
 for label,path in [('Timing frozen manifest','research/mixed-timing-results/manifest.json'),('Timing authoritative receipt','research/mixed-timing-results/independent-audit.json'),('Timing complete derived rows','research/mixed-timing-results/summary.json')]:p(escape(label)+': '+escape(path)+'<br/>'+sha(path),'Hash')
 page('Learned-partner response certificate, coverage and resources')
 h('Appendix: Incentives against the actual saved learned partner')
 p('This targeted follow-up selected one original-tolerance game, zero initialization, final 2M checkpoints, all 12 old seeds, both sellers and two original controllers: 48 retained labels. The stratum was chosen after the previous welfare results, before new response outcomes. It is not whole-project preregistration. The full primary and independent file/schema adapters, artificial tests, analysis contract and source snapshots were frozen before actual response computation; pre-freeze administrative checks repaired recognized legacy hash-map formats. No scientific case was rerun or omitted.')
 p('State s=(phase, previousA, previousB) retains incoming history at cap rounds. Reconstruct both original masked greedy policies from every saved binary64 Q cell, choosing the smallest original index on ties. Seller B swaps own/rival observations once; physical profitB remains in world orientation. At phase 0 the cap replaces the guard; other phases use the saved rival-indexed legal support. Startup guard is absorbing. The saved selected95 clock is K=4, not the later finite K=5 or mixed calendar. Start at the actual terminal history and NEXT phase. Choices are simultaneous; the fixed rival cannot observe the focal current quote.')
 p('Numerical synchronous value iteration starts at zero, stops at completed difference 1e-10 or 600 sweeps, and proposes a binary64 vector. An isolated-process supervisor imposes 300 seconds per whole case. Final values are quantized exactly to 2^-32 with ties-to-even; exact one-step argmax selects the proposed policy over every legal action. These proposal settings are not an optimality proof. The final f64 vector is retained and its quantization/argmax checked independently; all optimizer sweeps are not independently replayed.')
 p('Lift saved binary64 rewards r=R/L and candidate values v=Z/L to a common dyadic denominator. For gamma=19/20 compute the SIGNED maximum M=max_(s,a)[20R(s,a)+19Z(s_next)-20Z(s)] over every legal edge, without clamping M to zero. Then U(s)=(Z(s)+M)/L is a Bellman supersolution. Telescoping its one-step inequality bounds every legal history-dependent or randomized focal response against this fixed rival. This is standard discounted-MDP machinery, not a new algorithm or a guarantee against an adapting partner.')
 p('For each original/proposed deterministic policy, save the full transient h and first repeated cycle c, h+c&lt;=N. Exact value is sum_(t&lt;h) gamma^t*r_t + gamma^h*sum_(j&lt;c) gamma^j*r_(h+j)/(1-gamma^c). Integer polynomials evaluate the complete path, without horizon truncation. Raw gain G=V_response-V_base is kept separately from max(0,G)&lt;=V_star-V_base&lt;=U-V_base. U-V_response is the remaining optimality-gap bound; a zero achieved gain is not exact equilibrium. Mathematical 19/20 differs from the old training binary64 discount.')
 p(f'The independent audit accepted all 48 records, 24 checkpoint reconstructions, {learned_audit["maskedQCellsReconstructed"]:,} compact Q cells, {learned_audit["worldStatesChecked"]:,} world states and {learned_audit["legalStateActionEdgesChecked"]:,} legal state/action edges, with 19 rejected corruption controls. It checks paths, every-state response argmax/residual, count overflows, proposal quantization, execution/receipt chronology and exact seed summaries. Old economic tables are reused through accepted hashes, not re-enumerated. Full original training and optimizer trajectories remain unreplayed.')
 p('Normalized discounted unsupported exposure is (1-gamma)*sum gamma^t*I_t, using exact original state/action counts along the full transient and repeating cycle. All 48 baseline and response paths have zero exposure for each firm, both to unvisited states and never-tried chosen actions. This describes the actual audited continuations; it says nothing about every legal off-path state or retraining. Secondary customer benefit is instead an arithmetic eventual-cycle mean, excluding transient rewards, and never chooses a response or breaks an optimization tie.')
 lr=learned['meta']['resources']
 p(f'All 48 executions succeeded and met the 1e-6 absolute gap target; none was loose, unavailable or over budget. Primary time was {lr["seconds"]:.3f}s, approximately paired sampled child/supervisor RSS {lr["largestApproximatelyPairedRSSBytes"]:,} bytes, and primary output {lr["newOutputBytesBeforeCompletion"]:,} bytes before completion. No prospective soft target was exceeded. RSS samples are neither simultaneous unique physical memory nor continuous peaks. Execution success and scientific availability are orthogonal fields; complete certificates received before a later failure would remain informative without relabeling the failed execution. No new training or model/API seller call occurred.')
 p('The 24 seller labels per controller are dependent within 12 seed identities. Exact two-seller seed means and all 12 selected-minus-startup paired differences remain in evidence, with 9 positive and 3 negative paired differences. There is no new CI or p-value. Controllers differ in learned policies, clocks, experiences and phase capacities, so this is not a causal cap-frequency effect. Full-information profitable responses do not establish discoverability, mutual adaptation, intent, subgame equilibrium or general market behavior.')
 for label,path in [('Response manifest','research/learned-opponent-results/manifest.json'),('Authoritative response receipt','research/learned-opponent-results/independent-audit.json'),('Complete response summary','research/learned-opponent-results/summary.json')]:p(escape(label)+': '+escape(path)+'<br/>'+sha(path),'Hash')
 class ReproducibleCanvas(Canvas):
  def __init__(self,*args,**kw):kw['invariant']=1;super().__init__(*args,**kw)
 def footer(canvas,doc):canvas.saveState();canvas.setFont('Times-Roman',9);canvas.drawCentredString(A4[0]/2,23,str(doc.page));canvas.restoreState()
 page('Matched-clock replay, limitations and resources')
 h('Appendix: Equal clock labels and dense allocation')
 p('This separate follow-up was fixed after the old behavioral results and incentive audit, before new matched outcomes. All twelve old seed namespaces intentionally recur. One original-tolerance finite game, zero Q and the same 2M budget isolate a narrower comparison without pretending to be a new independent market cohort. The prospective display default is seed 907001, final endpoint, both worlds, chosen before new matched outcomes and retained unchanged.')
 p('There are 19,220 WORLD states (phase,previousA,previousB), with phase 0 transient and four recurrent clock labels. Each private table uses own/rival orientation; B\'s WORLD policy is transposed exactly once offline. Actual simultaneous rewards always index the physical pair (a,b). Both bootstrap maxima are read before either update. Forbidden Q/count cells remain positive zero/unvisited. Equal allocated arrays do not imply equal legal supports or visits.')
 p('The canonical 120-byte little-endian round record contains the one-based step, phase, previous price indices, chosen actions, exploration flags, six reserved zero bytes, epsilon, both rewards, both old Q values, both pre-update next maxima, both new Q values and all eight post-draw RNG words. Primary Buffer encoding and independent DataView encoding agree with literal Python struct/SHA fixtures. Every 10K rounds becomes one SHA256 block; there are 200/run and 4,800 distinct blocks. Agreement authenticates neither external execution nor individual raw records, which are not stored.')
 p('Python owns one isolated Node process per case and an active 600-second whole-case watchdog, including checkpoint/graph work and validation. Only closed, hash-bound checkpoints completely validated before the deadline are eligible. Each dense gzip family is bounded before inflation and checked for one member, CRC, ISIZE, no trailing bytes, canonical raw length and hash. All final dense bits/counts, actors, histories, next phases, exact 100K windows, approximate 10K display blocks, greedy caches, masks, complete successor graphs, basins and cycle metrics are independently compared.')
 p('Inventory integrity, execution success, endpoint numerical availability and aggregate full-replay completion are separate. A failed 1M slot may coexist with an accepted 2M endpoint. The planned mean requires all 24 accepted finals, while both aggregate completion flags require all 48 checkpoints and all 24 complete horizons. Missing or invalid values stay null with reasons; no favorable reruns, seed changes or extra horizon are permitted. Read-only actual-case claim/bit comparator perturbations are distinct from fresh-hash full serialized artificial corruption controls, and neither count is an experimental sample size.')
 mr=matched_audit['resources'];pr=mr['primary']
 p(f'Primary 24-run execution took {pr["seconds"]:.3f}s; full independent replay/validation took {mr["seconds"]:.3f}s. Primary approximately paired sampled RSS was {pr["largestApproximatelyPairedRSSBytes"]:,} bytes; replay approximately paired sample was {mr["largestApproximatelyPairedReplayRSSBytes"]:,} bytes. Replay samples every 50 ms may miss peaks; primary samples follow checkpoint and validation milestones. Paired sums are approximate. Primary stored output before completion was {pr["storedBytesBeforeCompletion"]:,} bytes, with {pr["rawEquivalentOutputBytesBeforeCompletion"]:,} raw-equivalent bytes including metadata and replacing compressed dense sizes. The 48 checkpoints have {pr["rawEquivalentEligibleCheckpointBytes"]:,} canonical dense bytes. No declared soft limit was exceeded in this execution; derived displays and delivery are extra outputs.')
 p('The controlled result concerns continued enforcement across training and frozen execution together. It is not formation-only prevention, unrestricted learner capability, convergence, equilibrium, intent, discoverability or general market protection. The paired replay is a deterministic explanatory artifact; developer browser tests supply no human participant evidence. The earlier 192-run training remains unreplayed in full, despite the stronger new 24-run execution audit.')
 for label,path in [('Matched frozen manifest','research/matched-clock-results/manifest.json'),('Matched authoritative replay receipt','research/matched-clock-results/independent-audit.json'),('All twelve matched rows','research/matched-clock-results/analysis.json')]:p(escape(label)+': '+escape(path)+'<br/>'+sha(path),'Hash')
 pdf=OUT/'local-guard-welfare-report-v12.pdf' ;SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=36,title='When a Local Pricing Guard Is Not a Welfare Promise',author='Mohammadpayam Teabi').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=ReproducibleCanvas)
 texts=[page.extract_text() for page in PdfReader(str(pdf)).pages]
 body_pages=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t))
 checks={'pdf':pdf.relative_to(ROOT).as_posix(),'sha256':sha(pdf.relative_to(ROOT)),'bytes':pdf.stat().st_size,'pages':len(texts),'plannedBodyPages':8,'bodyPages':body_pages,'abstractWords':words,'sections':page_sections,'pageTextCharacters':[len(t) for t in texts],'primaryPairs':48,'positivePairs':positive,'zeroPairs':zero,'negativePairs':negative,'secondaryTrainingTailMeans':tail_means,'changedCheckpointCycleCS':changed,'changedStartCycleCS':origin_changed,'finalCyclesUnvisitedStates':unvisited,'finalCyclesNeverTriedGreedyActions':untried,'learnerAuditSha256':sha('research/adaptive-learning-results/independent-audit.json'),'timingAuditSha256':sha('research/mixed-timing-results/independent-audit.json'),'timingPopulationCounts':mixed['meta']['populationCounts'],'old192FullTrainingReplay':False,'matchedFullTrainingReplay':matched_audit['fullTrainingReplay'],'matchedReplayComplete':matched_audit['replayComplete'],'matchedAuditSha256':args.audit_sha,'matchedPrimarySummary':matched['primarySummary'],'matchedSignCounts':matched['completePairDescription']['signCounts'],'affiliationSupplied':False,'learnedOpponentAuditSha256':sha('research/learned-opponent-results/independent-audit.json'),'learnedOpponentRecords':len(learned['records']),'learnedOpponentCounts':learned['meta']['counts'],'learnedOpponentControllerSummaries':learned['controllerSummaries']}
 (OUT/'main-report-v12-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8');(OUT/'local-guard-welfare-report-v12.txt').write_text('\n\n---PAGE---\n\n'.join(texts),encoding='utf-8')
 print(json.dumps(checks));need(body_pages==8,'Body page overflow: render and repair before accepting report')
if __name__=='__main__':main()
