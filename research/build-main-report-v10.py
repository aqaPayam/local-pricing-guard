"""V10 report under preparation. No learning or economic cases are run here.

The new timing gate must pass before any output is generated. V9's builder,
report and figures remain preserved. All timing outcomes are still unread by
this report author until the complete independent acceptance receipt exists.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
from importlib.util import spec_from_file_location,module_from_spec
from xml.sax.saxutils import escape
import sys,json,hashlib,re
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
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'output/pdf';FIG=ROOT/'research/capacity-figures';MIXFIG=ROOT/'research/mixed-timing-figures'
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

def main():
 mixed,mixed_audit=mixed_evidence()
 structural,summary,audit=evidence();recurring,misspec,incentive,meshes,continuous=structural
 base=next(r for r in recurring if r['scenario']=='base-g15-t1' and r['continuum']=='effective');target=next(t for t in base['comparisons'] if t['label']=='cap-95pct')
 _,misspec_raw,_,_=misspec;mb=next(r for r in misspec_raw['records'] if r['scenario']=='base-g15-t1' and r['continuum']=='effective');mt=next(t for t in mb['targets'] if t['label']=='cap-95pct')
 _,ir,_,_,_=incentive;ib=next(r for r in ir['records'] if r['scenario']=='base-g15-t1' and r['periodSlot']['id']=='closed-effective-95pct' and r['focalSeller']=='A' and r['discount']['numerator']=='19')
 mixed_figure(mixed);OUT.mkdir(parents=True,exist_ok=True)
 styles=getSampleStyleSheet()
 for name,font,size,leading in [('Body','Times-Roman',10.6,13.5),('Small','Times-Roman',9.4,11.8),('Heading','Times-Bold',12.8,16),('Caption','Times-Roman',9,11.3),('Equation','Courier',9.2,12.4)]:styles.add(ParagraphStyle('M'+name,fontName=font,fontSize=size,leading=leading,spaceAfter=8))
 styles.add(ParagraphStyle('MTitle',fontName='Times-Bold',fontSize=21,leading=24.5,alignment=TA_CENTER,spaceAfter=12));styles.add(ParagraphStyle('MCenter',fontName='Times-Roman',fontSize=10.3,leading=13,alignment=TA_CENTER,spaceAfter=8))
 styles.add(ParagraphStyle('MHash',fontName='Times-Roman',fontSize=8.4,leading=10.2,spaceAfter=4))
 story=[];page_sections=[];table_count=0
 def p(s,style='Body'):story.append(Paragraph(s,styles['M'+style]))
 def h(s):p(s,'Heading')
 def page(section):
  if story:story.append(PageBreak())
  page_sections.append(section)
 def fig(name,caption,width=491):
  path=(MIXFIG if name=='timing-frontier.png' else FIG)/name;w,hh=PILImage.open(path).size;story.append(Image(str(path),width=width,height=width*hh/w));p(caption,'Caption')
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
 abstract='A local pricing guard can satisfy every immediate profit check while failing a customer-benefit promise over time. We study a bounded symmetric logit duopoly where permitted prices have near-best immediate profit against the last public rival price. One real cap round appears protective in a coarse inherited game, but the base continuous worst long-run customer benefit is about 66.272, below the unchanged relaxed 95% target of 68.513. An attained upper-price envelope characterizes fixed and mixed timing of the same physical cap. A funded-calendar argument gives the minimum worst-path cap-rule frequency among causal cap-or-guard controllers protecting every prefix from activation. Validated timing reduces base effective-continuous frequency by about 7.29% relative to the best fixed period; finite and continuous certificates remain separate. A complete deterministic 120-label study preserves all outcomes. We separately quantify calibration reserve and unilateral gains against the adverse script, which is not automatically an equilibrium. Finally, 192 prospectively specified local tabular-learning runs compare four fixed schedules, two initializations and twelve paired seeds under two masks in one calibration. Their four paired mean customer-benefit increases are 2.39–2.95 units. Saved-policy graphs distinguish actual learning, frozen continuation and all-policy protection. The contribution is a model-specific guarantee audit and graphical benchmark using established learning, renewal and budget methods, without a general anti-collusion or language-model-seller claim.'
 words=len(abstract.split());need(150<=words<=250,'Abstract length differs');p('<b>Abstract.</b> '+abstract,'Small')
 h('1 The problem: a local check and a long-run promise')
 p('Two shops choose prices simultaneously. Each wants its own profit. An external guard checks a proposed price against the other shop\'s <i>last completed</i> price. Passing that check says little by itself about what customers obtain after many executions. We ask what customer-benefit promise survives a one-time handover back to this guard, and what continuing control is needed for a stronger promise.')
 p('A cap is a real market round: it limits both executed prices, makes purchases and earns profit and customer surplus. It is not a free reset of a chart. Our human game deliberately lets a coordinator choose both shops\' prices. That illustrates permitted behavior; it does not establish independent collusion or supply human experimental data.')
 p('<b>What is added.</b> The linked sprint starter already provides replacement, history, objective and checkpoint-branch experiments [1]. We instead audit the capacity of an explicit external price rule, including finite-to-continuous transfer, an attainable worst envelope, same-cap timing, model reserve and limited local learning. Known control and learning methods are credited below; priority for these ingredients is not claimed.','Small')
 page('Model and quantifiers')
 h('2 A self-contained game and the scope of each claim')
 p('There are B potential buyers, two symmetric inside goods of quality v and cost c, an outside option of normalized utility zero, and taste scale mu&gt;0. At executed physical prices p_A,p_B, let e_i=exp((v-p_i)/mu). Expected demand, private profit and customer surplus are:')
 p('D_i = B*e_i / (1+e_A+e_B)<br/>R_i = (p_i-c)*D_i<br/>C(p_A,p_B) = B*mu*log(1+e_A+e_B)','Equation')
 p('The base calibration is B=100, v=2, c=1 and mu=0.25. Its inherited bounded physical price domain is approximately [1.427721, 1.970186]. The inherited cap is held exactly at its saved numerical value p_cap=1.4664687420450921; it is not moved to a different continuous Nash price when timing changes. The original 15-quote reference gives cap customer benefit approximately 72.119. The unchanged relaxed 95% target F is approximately 68.513, stored as an absolute numerical threshold. Different experiments do not quietly redefine this target.')
 p('Let q be the rival\'s previous completed price. The guard permits every price in the bounded domain whose immediate expected profit is within epsilon of the best immediate profit available against q:')
 p('S(q) = {p : max_z R(z,q) - R(p,q) &lt;= epsilon + tau}<br/>U(q) = max S(q)','Equation')
 p('Epsilon=0.1 in the base mask; the learner sensitivity uses epsilon=0.05. Tau is the inherited 10^-12 numerical comparison allowance. This is a lagged one-step modeled profit-loss rule, not calibrated regret and not loss against the rival\'s hidden current action. Both sellers are externally constrained; they may coordinate, randomize or use arbitrary history within the legal sets when we state an <i>all-policy</i> guarantee.')
 tab(['Object','What is computed','What it does not establish'],[['Saved finite game','Exact rational comparisons on the saved binary64 payoff weights and legal masks.','Exact-real logit inequalities or grid-invariant protection.'],['Validated continuous model','Directed Decimal interval bounds for imported real constants under checked monotonicity and contraction conditions.','An independent transcendental backend or empirical market validity.'],['Learning behavior','Fixed-budget local Q-learning, paired seeds, saved-policy continuation and visit support.','Convergence, equilibrium, intent, or LLM behavior.']],[100,194,197],'Three evidence types and their distinct scopes.')
 p('In the graphical cap game a saved 61-quote base mesh is augmented by the exact old cap, prioritizing that quote over a nearby mesh quote. The two learner masks each have 62 choices. These are separate numerical games from the original 15-quote and refinement meshes; a continuous period is independently checked in the finite game before any finite guarantee is asserted.','Small')
 p('Finite masks inherit the binary64-rounded epsilon+tau comparator. Continuous validation separately treats imported constants as exact reals and reports nominal/effective allowances. “Continuous limit” describes the model result, not a proof that bit-level JavaScript mask rounding vanishes.','Small')
 h('The three outcome levels')
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
 page('Demand reserve and individual incentives')
 h('5 Two boundaries of the protection claim')
 fig('calibration-and-incentives.png','Figure 3. Separate sensitivity and incentive analyses. (a) The controller and old absolute target remain nominal while actual inside-good quality is v-d*mu. Four declared d values are shown categorically. Quality loss itself reduces customer benefit. (b) Exact best private-profit improvements against a fixed public maximum-allowed-price opponent, seller A, discount 19/20, across eight saved condition labels. These labels are not independent sampled economies; dots are not learner trials.')
 h('A fixed promise consumes model reserve')
 p('To isolate one explicit modeling assumption, actual demand quality is lowered by d taste-scale units while the legal rule, price domain, cap, clock and old target remain unchanged. The same price envelope remains the worst permitted path. If d is an unknown fixed value in [0,dbar], monotonicity makes dbar the worst endpoint; this is a bounded structural sensitivity calculation, not adversarial seller control over demand.')
 p('For the base original-95% rhythm K=4, the positive quality-error reserve is approximately d=0.006963. At dbar=0.01, fixed K=4 has worst customer benefit about 68.442, below the unchanged 68.513 target. Redesigning fixed integer timing conservatively gives K=3 at dbar=0.01 and K=2 at dbar=0.05; at zero error the selected K is 4. Permanent use of the same cap retains more reserve. Tiny 100%-target radii mostly reflect the inherited numerical target margin, and should not be sold as a surprising economic mechanism.')
 h('A worst permitted path is not automatically selfishly stable')
 p('Against an opponent that publicly chooses U of the focal shop\'s previous price, the focal seller can optimize all its own permitted quotes over a cap-to-cap block. Exact finite dynamic programming checks every state and action, with a continuation through the next real cap. Seller B uses the correctly transposed physical rewards. The fixed opponent\'s cap choice makes block restarts history-independent; that special simplification does not transfer to learned cap choices.')
 p(f'In the base K=4 game, seller A earns {val(ib["cap"]["finiteBaseline"]):.6f} by copying the script versus {val(ib["cap"]["finiteOptimal"]):.6f} from its best allowed discounted block. The relative improvement is only {100*val(ib["cap"]["infiniteGain"])/val(ib["cap"]["infiniteBaseline"]):.4f}%. Across all eight labels, every recurring seller/period comparison at discount 19/20 has a positive but small activation gain; permanent-cap comparisons are mostly zero. A simple last-guard-round immediate deviation explains every recurring-script instability found by the full calculation; a separate immediate cap screen covers the exceptional K=1 case.')
 p('A positive gain rejects that specified fixed-script profile, not the controller\'s customer-benefit guarantee. A zero gain is not an equilibrium proof. This audit uses fixed periods and does not certify incentives under the mixed credit clock. Closely related pricing-policy audits already exist [4]; this exact finite dynamic program is not a new algorithm.','Small')
 page('Prospective adaptive learner design')
 h('6 What independently adapting local learners do')
 p('The previous results quantify what is allowed, not what a learner will discover. We therefore froze a prospective study before training on either study game: two saved 62-price masks in the same economic calibration, four schedules, two Q initializations and twelve fresh paired whole-market seeds. All 192 runs were kept, with no outcome-driven horizon or seed changes.')
 tab(['Factor','Predeclared values'],[['Guard masks','Original epsilon 0.1; half tolerance epsilon 0.05. Same economic calibration.'],['Schedules','One startup cap then guard forever; cap every round; inherited 95%-target rhythm (K=4 or 10); K=16. All begin with an actual cap.'],['Private scores','Zero; optimistic value 20 times that firm\'s largest own immediate profit.'],['Seeds and budget','907001–907012, paired actor streams across conditions; 2,000,000 simultaneous rounds per run.'],['Learning parameters','Alpha 0.1, gamma 19/20 represented as binary64; exploration declines exponentially from 1 to 0.01, without cap/checkpoint reset.'],['Saved endpoints','1M secondary and 2M primary checkpoints; exact last 100k training windows; complete frozen-policy graphs; 128-step terminal previews.']],[100,391],'Prospectively frozen adaptive-learning design; 192 retained runs.')
 p('Each firm stores a private Q table on (cap/guard phase, own previous price, rival previous price). Both choose before either current action is revealed. Each observes only its own deterministic expected profit for updating; no teacher, shared reward or communication scripts the choices. Current greedy selection respects the current legal mask; the bootstrap maximum uses the next state and its actual next-clock mask. Exact ties select the smallest original quote index.')
 p('Q(s,a) <- Q(s,a) + 0.1*[R_own + 0.95*max_(legal a_next) Q(s_next,a_next) - Q(s,a)]','Equation')
 p('A cap is continuing, not terminal, and the state still retains price history at cap rounds. Thus a learned cap action can depend on incoming history. Counts are saved exactly, including saturation overflow records. Two private xoshiro128** streams per seed are prospectively separated by 2^64 jump segments, and paired across conditions. Ordinary binary64 arithmetic is used for learning; there is no rational-learning claim.')
 h('The primary comparison does not secretly add a new cap')
 p('For each tolerance and initialization, compare the final frozen-greedy eventual-cycle customer benefit of the selected rhythm with startup-only, using the <i>actual saved terminal history and phase</i>. Startup-only remains in guard forever. All twelve paired differences remain in each of four strata. A new high-history, phase-0 cap start is a separately labeled counterfactual, never the primary endpoint.')
 p('The prospectively saved 5,120 by 12 whole-seed resample matrix gives approximate marginal percentile 95% seed-variation intervals, using type-7 interpolation. These are not simultaneous intervals, market uncertainty, convergence evidence or a causal effect of frequency alone. Increasing K also increases phase-dependent Q rows; equal rounds do not mean equal state/action coverage. There is no unrestricted learner-capability arm, so this design cannot show that the guard prevented learned collusion.','Small')
 page('Adaptive results and audit scope')
 h('7 All four planned learner comparisons')
 fig('adaptive-paired-seeds.png','Figure 4. Every final 2M paired frozen-cycle customer-benefit difference: inherited selected95 rhythm minus one startup cap. Twelve whole-market seeds per panel; zero and reversed outcomes are retained. The horizontal line is the mean, not a protection floor. Tolerances and initializations remain separate; no seed, firm, state or checkpoint is counted as an additional independent economy.')
 rows=[]
 for c in summary['primaryContrasts']:rows.append(['Original' if c['scenario']=='base-g15-t1' else 'Half',c['qInit'],signed(c['mean']),f'{signed(c["range"]["minimum"])} to {signed(c["range"]["maximum"])}',f'{signed(c["interval"]["lower"])} to {signed(c["interval"]["upper"])}'])
 tab(['Tolerance','Scores','Mean difference','All-seed range','Marginal 95% interval'],rows,[69,78,95,123,126],'Final actual-terminal frozen-cycle differences, selected95 minus startup-only; all twelve paired seeds in each stratum.')
 # Describe every stratum mechanically; no cherry-picked example policy.
 positive=sum(ratio(p['difference'])>0 for p in summary['primaryPairs']);zero=sum(ratio(p['difference'])==0 for p in summary['primaryPairs']);negative=48-positive-zero
 p(f'Across the 48 planned paired rows, {positive} differences are positive, {zero} exactly zero and {negative} negative. These four-stratum totals are descriptive bookkeeping, not a pooled effect estimate. Exact signs come from saved-weight fractions; intervals and printed decimals are approximate. Full seed rows remain in the evidence file.')
 tail_means=[];tail_signs=[]
 for c in summary['primaryContrasts']:
  pairs=[]
  for seed in summary['orderedSeeds']:
   def get(control):return next(r for r in summary['runs'] if r['scenario']==c['scenario'] and r['qInit']==c['qInit'] and r['seed']==seed and r['controller']['id']==control)['checkpoints'][1]['trainingTail']['means']['consumerSurplus']
   pairs.append(ratio(get('selected95'))-ratio(get('startup-only')))
  tail_means.append(float(sum(pairs,Fraction())/12));tail_signs.extend(pairs)
 p('The actual last 100k exploratory windows also favor the selected rhythm in '+str(sum(x>0 for x in tail_signs))+'/48 pairs. Four secondary mean gaps, in the paired-results table order, are '+', '.join(signed(x) for x in tail_means)+'. These are observed training-window averages, separate from frozen cycles and the primary interval calculation.')
 endpoints=[(r,c) for r in summary['runs'] for c in r['checkpoints'] if c['step']==2000000]
 unvisited=sum(any(c['frozen']['actualTerminal']['visitSupport'][f]['unvisitedStates'] for f in ['A','B']) for r,c in endpoints)
 untried=sum(any(c['frozen']['actualTerminal']['visitSupport'][f]['neverTriedGreedyActions'] for f in ['A','B']) for r,c in endpoints)
 changed=sum(ratio(r['checkpoints'][0]['frozen']['actualTerminal']['means']['consumerSurplus'])!=ratio(r['checkpoints'][1]['frozen']['actualTerminal']['means']['consumerSurplus']) for r in summary['runs'])
 origin_changed=sum(ratio(c['frozen']['actualTerminal']['means']['consumerSurplus'])!=ratio(c['frozen']['freshCap']['means']['consumerSurplus']) for r,c in endpoints)
 p(f'At the final checkpoint, {unvisited}/192 actual cycles contain an unvisited state and {untried}/192 a never-tried greedy action. Yet {changed}/192 change cycle customer benefit between 1M and 2M, and {origin_changed}/192 differ under fresh-cap versus actual-terminal starts. These secondary diagnostics are not independent samples or convergence evidence. The display retains exploratory windows, both profits/prices, mask geometry, visit support and separate model floors.')
 res=summary['resources'];p(f'All 192 runs were retained: 384 million market rounds, 768 million private updates and 12,288 discarded clone steps. Execution took {res["seconds"]:.2f} seconds; the largest after-run RSS sample ({res["largestObservedRSSBytes"]:,} bytes) exceeded the 256 MB soft target. It is not a measured instantaneous peak. Full resource records remain in completion.json.','Small')
 p('Independent Python reconstructs all 384 saved-Q greedy policy pairs, complete successor graphs and exact saved-weight cycle metrics, checks actual terminal envelopes, counts and diagnostic cloned updates, and rejects corrupted evidence. The numerical core was tested before training; its full schema adapter was completed and snapshotted during training before this independent referee read its first real checkpoint. The complete main training trajectory was not independently replayed; sampled updates and cloned probes were checked. No new learner economic outcomes were interpreted before the complete learner audit passed.','Small')
 page('Interpretation, contribution and access')
 h('8 What this adds, and what remains open')
 p('The strongest result is about <i>the scope of a protection promise</i>. A coarse finite game can give a reassuring one-cap result while a richer price interface admits worse allowed continuations. The continuous upper envelope explains the limit and gives an attainable worst cycle when the same physical cap is repeated. Calibration reserve and unilateral incentives identify different boundaries: model error can consume the old absolute target, while a worst permitted script need not be individually attractive.')
 p('The learner study adds behavior under a precisely declared controller, without replacing the all-policy proof by a favorable simulation. Its outcomes remain conditional on two masks, one calibration, chosen hyperparameters, finite budget and private-score initializations. Neither high prices nor a quiet frozen cycle establishes collusion, punishment, intent or equilibrium. A future experiment needs an unrestricted capability reference, systematic learning sensitivity and an explicit stability audit against the actual learned opponent before making those claims.')
 h('Relation to prior work and the sprint starter')
 p('Calvano et al. study profit-seeking learning and algorithmic pricing [2]. Eschenbaum et al. examine robustness, replacement and continued adaptation [3], and the sprint starter already branches histories, models and objectives [1]. Alshiekh et al. define action restriction and shielding, including reward credit and the need for persistent protection [5]. Brero et al. design ongoing platform interventions for consumer benefit [6]. Hartline et al. study a different, calibrated-regret regulation framework [7]. Periodic resetting and renewal-ratio control are established [8,9]. Lopes de Moraes and De Losso directly audit learned pricing incentives [4]. None should be repackaged here as our invention.')
 p('Our limited addition is a linked guarantee-capacity case: price precision, a fixed physical cap, restricted minimax timing, bounded demand reserve and adaptive observations keep distinct quantifiers. Adjacent timing mixtures already occur in Sun and Cyr [10]; uniform cumulative safety budgets appear in conservative bandits [11,12]. Our pricing-envelope reduction and validated comparison apply these ideas. The mixed result covers the same two actuators, not every intervention, cap strength or economic cost. No broad novelty or empirical-market superiority is established.')
 h('An accessible game, with evidence behind each view')
 p('Start at http://127.0.0.1:3003/. The two-shop challenges let a human choose both permitted quotes, see actual cap executions and separate earned customer benefit from a guaranteed buffer. The mixed-calendar page explains how earlier credit funds a longer gap. The one-shop profit challenge uses a public script and exact block score; the learner page reveals stored executions. These are explanatory artifacts and developer-tested controls, not a human usability study.')
 h('Reproduction')
 p('Start the local viewer with <font name="Courier">node research/demo-server.js</font>. Run <font name="Courier">python research/audit-mixed-study.py</font> for the full new timing audit, or <font name="Courier">python research/audit-adaptive-learning.py</font> for saved learner artifacts. Both verify without rewriting closed receipts by default. README links the raw manifests, source snapshots, earlier checkers and gated derivative builders. The full archive preserves numerical evidence; the smaller viewer archive explicitly omits large checkpoints and points to the full archive hash.','Small')
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
 h('Appendix: Limitations and Dual-Use / Ethical Considerations')
 p('<b>Model limits.</b> The mathematical statements require the explicitly bounded, symmetric, known logit model and checked upper-map assumptions. The saved finite results certify numerical masks and reward weights, not exact-real profit inequalities. The continuous results concern imported constants and directed intervals, not measured economic uncertainty. The quality-error test is one fixed structural perturbation, not general robustness. Frequency counts external rule applications and does not measure implementation cost or useful seller agency.')
 p('<b>Behavioral limits.</b> The new 192-run study has one economic calibration, two tolerance masks, twelve paired seeds and fixed learning settings. Changing phase count changes state space and coverage. Deterministic expected rewards omit sampled demand. Frozen eventual cycles may contain default unvisited scores. No unrestricted capability arm, policy-punishment mechanism test against learned rivals, convergence proof, equilibrium proof, LLM comparison or human participant study is included. A positive fixed-script unilateral gain and a customer-benefit floor answer different questions.')
 p('<b>Verification limits.</b> Separate implementations reconstruct saved finite policy/graph/incentive calculations; they can share a conceptual or modeling error. Continuous primary and independent code share a Decimal transcendental backend. Learner source, checkpoints, counts and cloned probes were audited, but the complete main learning trajectory was not independently replayed; sampled updates and cloned probes were checked. Sampled after-run RSS exceeded the prospective soft memory target and is not a measured instantaneous peak. All declared runs and resource overruns remain visible.')
 p('<b>Dual use and ethics.</b> The toy model can illustrate adverse price coordination, so outputs should be framed as tests of safeguards rather than operational coordination advice for real firms. No real seller communication, customer data, participant recruitment, private economic data or autonomous commercial trading is involved. Human controls operate locally without claiming experimental observations. No external publication, submission, paid inference or deployment was performed in this stage.')
 h('LLM usage and author contributions')
 p('The project builds on the user\'s preexisting browser game and market scaffold, and on published sprint resources. Those are prior work. The guarantee-capacity analyses, new controller demonstrations and 192-run learner study described here were developed in the current sprint work; frozen protocols, source snapshots and timestamps identify that new work. The report does not claim the inherited game or published starter as a new contribution.','Small')
 p('Mohammadpayam Teabi supplied the project, direction and author identity. Codex and collaborating AI agents substantially performed problem formulation, code implementation, mathematical derivation, experiment orchestration, independent AI-agent checks, analysis, visualization and drafting. The report is substantially AI-written; independent AI agents are not independent human peer reviewers. No human validation of the final science is implied.')
 p('The new guarantee-capacity analyses and 192-run tabular experiment use no experimental language-model seller, paid model service, account-backed game player or remote inference. Codex development consumes coding-assistant allowance. Historical account-backed pilot material exists elsewhere in the earlier project and is not evidence for the claims in this report; the report does not claim that the entire project history had zero model usage.')
 h('Compact provenance pointers')
 for label,path in [('Learner frozen manifest','research/adaptive-learning-results/manifest.json'),('Learner independent receipt','research/adaptive-learning-results/independent-audit.json'),('Learner descriptive summary','research/adaptive-learning-results/summary.json'),('Continuous receipt','research/continuous-results/independent-audit.json'),('Recurring receipt','research/recurring-results/independent-audit.json'),('Incentive receipt','research/incentive-results/independent-audit.json')]:
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
 class ReproducibleCanvas(Canvas):
  def __init__(self,*args,**kw):kw['invariant']=1;super().__init__(*args,**kw)
 def footer(canvas,doc):canvas.saveState();canvas.setFont('Times-Roman',9);canvas.drawCentredString(A4[0]/2,23,str(doc.page));canvas.restoreState()
 pdf=OUT/'local-guard-welfare-report-v10.pdf';SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=36,title='When a Local Pricing Guard Is Not a Welfare Promise',author='Mohammadpayam Teabi').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=ReproducibleCanvas)
 texts=[page.extract_text() for page in PdfReader(str(pdf)).pages]
 body_pages=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t))
 checks={'pdf':pdf.relative_to(ROOT).as_posix(),'sha256':sha(pdf.relative_to(ROOT)),'bytes':pdf.stat().st_size,'pages':len(texts),'plannedBodyPages':8,'bodyPages':body_pages,'abstractWords':words,'sections':page_sections,'pageTextCharacters':[len(t) for t in texts],'primaryPairs':48,'positivePairs':positive,'zeroPairs':zero,'negativePairs':negative,'secondaryTrainingTailMeans':tail_means,'changedCheckpointCycleCS':changed,'changedStartCycleCS':origin_changed,'finalCyclesUnvisitedStates':unvisited,'finalCyclesNeverTriedGreedyActions':untried,'learnerAuditSha256':sha('research/adaptive-learning-results/independent-audit.json'),'timingAuditSha256':sha('research/mixed-timing-results/independent-audit.json'),'timingPopulationCounts':mixed['meta']['populationCounts'],'fullTrainingReplay':False,'affiliationSupplied':False}
 (OUT/'main-report-v10-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8');(OUT/'local-guard-welfare-report-v10.txt').write_text('\n\n---PAGE---\n\n'.join(texts),encoding='utf-8')
 print(json.dumps(checks));need(body_pages==8,'Body page overflow: render and repair before accepting report')
if __name__=='__main__':main()
