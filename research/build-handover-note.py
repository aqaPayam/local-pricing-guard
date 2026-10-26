"""Supplementary initializer note; does not rewrite the reviewed V3 paper."""
from pathlib import Path
import sys,json,hashlib
try:import reportlab
except ImportError:sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'))
from reportlab.platypus import SimpleDocTemplate,Paragraph,PageBreak,Image,Table,TableStyle,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader
from PIL import Image as PILImage
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8'))
AUDIT=read('research/handover-init-results/independent-audit.json');SUMMARY=read('research/handover-init-results/summary.json')
DONE=read('research/handover-init-results/completion.json');MANIFEST=read('research/handover-init-results/manifest.json')
if not AUDIT['passed']:raise SystemExit('A passed initializer audit is required')
styles=getSampleStyleSheet()
for name,font,size,leading in [('Body','Times-Roman',10.4,13.2),('Small','Times-Roman',9.3,11.6),('Heading','Times-Bold',13,16),
 ('Caption','Times-Roman',9,11.4),('Equation','Courier',9.2,12.5)]:styles.add(ParagraphStyle(name='H'+name,fontName=font,fontSize=size,leading=leading,spaceAfter=8))
styles.add(ParagraphStyle(name='HTitle',fontName='Times-Bold',fontSize=20,leading=24,alignment=TA_CENTER,spaceAfter=8))
styles.add(ParagraphStyle(name='HCenter',fontName='Times-Roman',fontSize=10.5,leading=14,alignment=TA_CENTER,spaceAfter=6))
story=[]
def p(t,s='Body'):story.append(Paragraph(t,styles['H'+s]))
def h(t):p(t,'Heading')
def br():story.append(PageBreak())
def fig(name,caption,width=490):
 f=ROOT/'research/handover-figures'/name;w,hh=PILImage.open(f).size;story.append(Image(str(f),width=width,height=width*hh/w));p(caption,'Caption')
p('One Round to Safer Guarded Pricing?','Title')
p('Finite-grid initializer guarantees and their limits','Center');p('Mohammadpayam Teabi | Independent researcher | 26 October 2026','Center')
p('Supplementary research note to the reviewed version-3 paper. The paper and its evidence remain unchanged.','Small')
h('1 Question and prospective design')
p('Can one actual capped execution at activation enter a region where the original price guard protects customer benefit against every permitted coordinated continuation? '
'The preceding graph audit found different reachable outcomes from unprotected and protected training histories. This follow-up tests a defense to that specific gap, rather than claiming a new shielding algorithm or emergent collusion.')
p('We retained eight existing finite guard games and five target labels each: 90%, 95%, 99%, 100% of the same configuration\'s permanent competitive-cap floor, plus the near-continuous-Nash anchor\'s certified reachable floor. '
'All 40 labels, including duplicates, were fixed before execution. For requested target F, the actual guaranteed threshold is F-delta, where delta=1e-8*max(1,F). Numerical straddlers are retained; none occurred in these cases.')
h('2 Safe region and one real execution')
p('Let [L(s),U(s)] enclose the minimum attainable infinite-average customer benefit from public state s. Classify s safe if L(s) &gt;= F-delta, unsafe if U(s) &lt; F-delta, ambiguous otherwise. '
'The certified safe set G is checked on every outgoing guard edge. The one-round cap changes public history through real executed prices; it does not silently replace a memory field.')
p('A common prefix cap at index k allows every post-execution pair in R_k=[0,k] x [0,k]. It is certified only if the entire rectangle lies in G. '
'We also test every prefix cap and identify the largest safe k <i>within that family</i>. This is not a maximally permissive controller among arbitrary mechanisms.')
fig('initializer-frontier.png','Figure 1. Results for all 40 labels after the stated numerical relaxation. Repair means the cap supplies a uniform guarantee where the unchanged guard was not safe from every state. Already safe means no initialization was needed for that target. Impossible means every state has a witnessed below-target guard tail, ruling out uniform protection by any finite initializer followed by this unchanged guard.',width=490)
br()

h('3 What the cap can and cannot repair')
fig('safe-regions.png','Figure 2. Public post-cap states: green guarantees the relaxed target for every guard tail; red admits a below-target tail. Dashed outlines mark the existing competitive-cap rectangle; solid outlines mark the largest certified common-prefix rectangle. The four panels use different targets/configurations, not independent replications. No numerical ambiguity occurred.',width=450)
p('The near-Nash-anchor target succeeds in all eight configurations, but only six are meaningful uniform repairs: the two affine-equivalent altered-demand cases already satisfy that target from every state. '
'The 95% cap-reference target succeeds in five configurations; 99% and 100% succeed in four. At 90%, seven cases were already safe and only doubled tolerance needs repair.')
p('Example: base15 improves the unprotected-endpoint worst guard tail from 68.477 to 72.119. With 31 prices, the corresponding improvement is 67.271 to 68.961, still below the permanent-cap floor 72.363. '
'For that near-Nash target the largest safe prefix allows five initial quotes per seller, versus three under the existing competitive cap. This is a one-step choice comparison at that weaker target, not superiority over a permanent cap.')
br()

h('4 Why the claims follow')
p('<b>Forward invariance.</b> If s can transition to v, the minimum reachable long-run surplus from s is no larger than from v: a finite first step does not change the tail average. '
'A true safe region is therefore forward invariant. The numerical implementation uses inherited lower certificates and explicitly verifies every edge from its classified safe set. '
'Every possible capped execution lies in R_k, so R_k contained in G gives a uniform long-run guarantee after the guard resumes.')
p('<b>Failure and impossibility.</b> A single post-cap state with a legal below-threshold guard tail disproves uniform protection by that cap. A stronger impossibility is asserted only when every public state is certified unsafe: '
'any finite initializer must eventually return control to the unchanged guard in some state, and that state admits a below-target continuation. An empty certified set alone would not suffice if numerical straddlers remained. '
'This does not say that every actual player chooses the harmful continuation, nor that persistent control or a changed guard is impossible.')
h('5 Independent verification and scope')
p(f'The source/input freeze was {MANIFEST["frozenAt"]}. A separate auditor independently rebuilt economics and guard transitions, checked all {AUDIT["labels"]} target labels, '
f'{AUDIT["edgesChecked"]:,} safe-region edges and {AUDIT["checks"]:,} checks, and rejected four injected corruptions: safe-set membership, cap index, first-round economic range and failure tail. '
'It reran the inherited cycle audit read-only. The 13 meaningful synthetic tests include ambiguity, invalid metadata, family-only optimality and actual first-execution rewards. '
f'The new analysis took {DONE["seconds"]:.3f} seconds; maximum RSS sampled after scenarios was {DONE["largestObservedMemorySample"]["rss"]/1e6:.2f} MB, below its 100 MB target. This is not continuous peak-memory measurement.')
p('All 64 unprotected-training endpoints are inherited diagnostics, viewed under five labels, not 320 independent experiments. First-round customer benefit and both seller-profit ranges are stored without inventing a distribution over coordinated quotes. '
'For example, base15\'s existing capped execution has customer benefit 72.119-75.792 and each seller profit 20.355-22.020 across its possible outcomes. '
'The result concerns subsequent infinite-average welfare; no higher-floor guarantee at every finite horizon or every individual round is inferred.')
p('These are known deterministic symmetric finite-grid games. A permanent cap remains a different controller with a different welfare/choice tradeoff. '
'Grid dependence is substantive: a restoration at 15 prices can fail at 31 prices. Continuous-price reachability, unilateral incentive stability, independent learner discovery and human comprehension remain outside this audit. '
'The next priority is a separately reviewed mesh/continuous analysis before presenting the initializer as a broadly robust solution.')
h('Reproduction, attribution and AI assistance')
p('Run <font face="Courier">node research/audit-handover-init.js</font> for the read-only 40-label audit. Optional figures use '
'<font face="Courier">python research/build-handover-figures.py</font>. The separate Activation Lab illustrates the actual cap step and all-outcome rectangle. '
'It is a developer-built explanation, not human-subject evidence. The full frozen protocol, hashes, inherited certificates and current results accompany this note.','Small')
p('Safety games, invariant regions and permissiveness are established methods (Alshiekh et al., AAAI2018, arXiv:1708.08611; Ji, Yin and Lafortune, Automatica123:109359,2021, doi:10.1016/j.automatica.2020.109359). '
'This is a narrowly scoped economic application. Codex research/coding agents substantially assisted formulation, implementation, analysis, auditing and writing under Mohammadpayam Teabi\'s direction. '
'Separate AI-agent review is not human peer review. No API game players, new training, paid services, customer data, external submission or public deployment were used. Explicit failure witnesses could be misused to coordinate pricing; the results supply toy-model diagnosis, not legal or real-market certification.','Small')
class ReproducibleCanvas(Canvas):
 def __init__(self,*a,**kw):kw['invariant']=1;super().__init__(*a,**kw)
def footer(c,d):c.saveState();c.setFont('Times-Roman',9);c.drawCentredString(A4[0]/2,23,str(d.page));c.restoreState()
pdf=OUT/'handover-init-note.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=43,rightMargin=43,topMargin=36,bottomMargin=36,
 title='One Round to Safer Guarded Pricing?',author='Mohammadpayam Teabi').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=ReproducibleCanvas)
texts=[p.extract_text() for p in PdfReader(str(pdf)).pages]
checks={'pdf':pdf.relative_to(ROOT).as_posix(),'pages':len(texts),'bytes':pdf.stat().st_size,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
 'supplementaryNote':True,'pageTextCharacters':[len(t) for t in texts],'requestedVsRelaxedThreshold':True,'longRunOnly':True}
(OUT/'handover-note-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
(OUT/'handover-init-note.txt').write_text('\n\n---PAGE---\n\n'.join(texts),encoding='utf-8')
if len(texts)!=3:raise SystemExit(json.dumps(checks))
print(json.dumps(checks))
