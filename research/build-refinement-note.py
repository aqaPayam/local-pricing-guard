"""Reviewed-stage supplement; earlier finite-model papers are preserved."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
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
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
ma=read('research/mesh-results/independent-audit.json');ca=read('research/continuous-results/independent-audit.json')
if not ma.get('passed') or not ca.get('passed'):raise ValueError('Both independent audits required')
if ma['studyManifestHash']!=sha('research/mesh-results/manifest.json') or ma['indexSha256']!=sha('research/mesh-results/index.json') or ca['studyManifestHash']!=sha('research/continuous-results/manifest.json') or ca['resultsSha256']!=sha('research/continuous-results/results.json'):raise ValueError('Audit evidence identity mismatch')
old=read('research/handover-init-results/results.json')['records'];meshes=read('research/mesh-results/index.json')['cases'];all_cont=read('research/continuous-results/results.json')['records'];cont=[r for r in all_cont if r['continuum']=='effective']
mc=read('research/mesh-results/completion.json');cc=read('research/continuous-results/completion.json')
styles=getSampleStyleSheet()
for name,font,size,leading in [('Body','Times-Roman',10.2,13),('Small','Times-Roman',9.1,11.6),('Heading','Times-Bold',12.8,16),('Caption','Times-Roman',8.7,10.8),('Equation','Courier',9,12.4)]:styles.add(ParagraphStyle(name='R'+name,fontName=font,fontSize=size,leading=leading,spaceAfter=8))
styles.add(ParagraphStyle(name='RTitle',fontName='Times-Bold',fontSize=21,leading=25,alignment=TA_CENTER,spaceAfter=9))
styles.add(ParagraphStyle(name='RCenter',fontName='Times-Roman',fontSize=10.5,leading=14,alignment=TA_CENTER,spaceAfter=7))
story=[]
def p(t,s='Body'):story.append(Paragraph(t,styles['R'+s]))
def h(t):p(t,'Heading')
def br():story.append(PageBreak())
def midpoint(b):return float((Decimal(b['lower'])+Decimal(b['upper']))/2)
def fig(name,caption,width=495):
 f=ROOT/'research/refinement-figures'/name;w,hh=PILImage.open(f).size;story.append(Image(str(f),width=width,height=width*hh/w));p(caption,'Caption')

p('When a Safe Handover Depends<br/>on the Price Grid','Title')
p('A continuous-price transfer audit of a lagged profit-tolerance guard','Center')
p('Mohammadpayam Teabi | 26 October 2026','Center')
p('Supplementary research note. The earlier finite-grid certificates remain valid in their stated models. This note tests their transfer to a different action resolution.','Small')
h('1 The question')
p('Two sellers choose prices simultaneously. A guard permits a quote when its profit against the previous rival price is within epsilon of the best such profit. A one-round competitive-price cap can put a coarse finite game inside a region with better worst-case customer surplus. Does this protect the same long-run target when the price interval is made continuous?')
p('We fix the eight inherited scenario labels and all 40 original requested/relaxed target labels before calculating new outcomes. The experiment changes price resolution while keeping each saved price interval, economic parameters and tolerance. Crucially, the best-profit benchmark is recomputed on each grid; the continuous benchmark is its continuous counterpart. Equivalent calibrations and grid-size labels are retained, not counted as independent economies.')
base=next(r for r in cont if r['scenario']=='base-g15-t1')
if base['status']=='certified theorem and enclosures':
 original=next(r for r in old if r['scenario']['id']=='base-g15-t1');f=next(r for r in original['results'] if r['label']=='cap-100pct')['requestedTarget'];fine=next(r for r in meshes if r['scenario']=='base-g15-t1' and r['n']==1921)
 p(f'<b>Illustration.</b> The original 15-price one-round cap protects an approximately {f:.3f} customer-surplus reference, minus its declared numerical margin. On 1921 choices, the after-cap worst value is approximately {fine["welfare"]["oneRoundCapWorst"]:.3f}. The validated effective continuous floor is approximately {midpoint(base["worst"]["consumerSurplus"]):.3f} from every starting state. These are fixed-model capacities under deliberate permitted continuation choices, not learned outcomes.')
fig('base-transfer-print.png','Figure 1. Base market at all nine declared meshes: worst customer surplus after one competitive-cap execution (points), variation across public starts (shading), and validated effective-continuum floor (dashed). The original 100%-cap target minus its saved allowance stays fixed. Shading is not statistical uncertainty; connecting lines do not assert monotone refinement. Separate full-size figures show all 72 declared labels.',width=495)
br()

h('2 Why the continuous statement is stronger than a sweep')
p('Normalize own/rival prices as x=(p-c)/mu and y=(r-c)/mu, and put k=exp((c-v+v0)/mu). For the primary effective comparison use t=(epsilon+tau)/(B*mu), with tau the exact imported numerical allowance; the nominal sensitivity uses t=epsilon/(B*mu). The normalized profit and customer surplus are:')
p('f(x,y) = x/[1+(k+exp(-y))*exp(x)]<br/>C(x,y) = B*mu*log[1+(exp(-x)+exp(-y))/k]','Equation')
p('The standard logit best response is b(y)=1+w(y), where w(y)=W(1/[e*(k+exp(-y))]). Let U_t(y) be the largest allowed continuous quote, clipped at the common price ceiling. We require interior best responses throughout the interval, t below the minimum w, and a rigorous sufficient small-tolerance condition ensuring that U_t is nondecreasing. We do not infer this from a sampled derivative plot.')
p('With m=w(ell), a sufficient condition is:<br/>0 &lt; t &lt; min{m^2/[2*(1+m)], m^3*(1+m)/2}.','Equation')
p('At the unrestricted upper root u, write a=w-t. Implicit differentiation yields u_w&lt;1 because its numerator minus the negative own-price derivative f_x equals (t/w)*(1-a/u)&gt;0. Under monotonicity, 0&lt;=u_w&lt;1. Also w_y&lt;=rho&lt;1, where rho=W(1/[e*k])/(1+W(1/[e*k])). Thus the clipped U_t is a contraction and has a unique fixed point q_star above continuous Nash N.')
p('<b>Order comparison.</b> From the same initial public pair, choosing U_t of the previous rival price every round dominates every other permitted trajectory coordinatewise. Induction uses only the nondecreasing upper allowance. Since customer surplus falls with either price, this top-choice path minimizes it at every future execution. Contraction sends that path to (q_star,q_star) from every initial pair. Therefore every permitted path has liminf infinite-average surplus at least C_star=C(q_star,q_star), and the top-choice path attains this limiting average.')
p('<b>Finite initialization cannot change this floor.</b> Returning to the same guard after any finite intervention leaves some public state. From that state the top-choice continuation still attains C_star. A target strictly above its validated upper enclosure therefore cannot be guaranteed by any finite initializer. A target at or below its lower enclosure is already protected from every state. Numerical overlap remains unresolved. The limit need not be reached at any finite execution.')
h('3 Why finite grids can still have multiple basins')
p('If Delta is the normalized grid spacing, the grid-based best-profit error is at most A*Delta^2/8, with A=1/2+max(|ell|,|H|)/4. For sufficiently fine grids, a uniform allowed-interval width and positive upper-root slope provide an upper-map error e_n that tends to zero. The continuous contraction then bounds every arbitrary policy from above in price, while a feasible discrete top-choice path supplies a matching near-limit continuation. Worst long-run welfare values converge uniformly across starts.')
p('This convergence theorem concerns exact-arithmetic grids at a common declared tolerance, including the same fixed allowance in the effective comparison. The binary64 meshes are separate numerical diagnostics; fixed arithmetic rounding is not assumed to vanish with spacing. The bound concerns worst values, not unique finite-grid fixed points or contraction of every policy. We validate no numerical slope/width constant or mesh-specific theoretical error rate here.','Small')
p('<b>Counterexample to a broader claim.</b> Monotonicity is not universal: on normalized interval[1,5], k=exp(-2)/2 and t=1/2, the raw upper map has negative derivative at y=2+log2 although all best responses are interior and t is below every best profit. The small-tolerance hypothesis must remain explicit.','Small')
br()

h('4 Keep the target fixed when testing transfer')
fig('target-transfer-print.png','Figure 2. Each cell compares the original-grid initializer outcome with the continuous all-start comparison, using exactly the same saved requested target minus numerical allowance. Safe means no initialization is required; Cap means a one-round cap meets the target; Fail means a below-target tail exists from every state. Continuous classifications use validated exact-model enclosures. A separate figure includes the 1921-choice diagnostic matrix.',width=495)
counts=Counter(c['classification'] for r in cont for c in r['comparisons'])
p(f'The effective continuum has {counts.get("all-start failing continuation",0)} failing-target labels, {counts.get("already guaranteed",0)} labels already guaranteed and {counts.get("unresolved",0)} unresolved labels across the 40 retained comparisons. This is a fixed-case matrix, not40 independent replications or a population estimate.')
data=[['Original label','Nash CS','Continuous CS','CS gap','1921 start spread']]
names=['Base15','Scale0.5','Lower value','Lower cost','Base11','Base31','Half tolerance','Double tolerance']
for source,name in zip(old,names):
 sid=source['scenario']['id'];r=next(c for c in cont if c['scenario']==sid);fine=next(m for m in meshes if m['scenario']==sid and m['n']==1921)
 if r['status']=='certified theorem and enclosures':data.append([name,f'{midpoint(r["nash"]["consumerSurplus"]):.4f}',f'{midpoint(r["worst"]["consumerSurplus"]):.4f}',f'{midpoint(r["nashToWorstSurplusGap"]):.4f}',f'{fine["welfare"]["spread"]:.5f}'])
 else:data.append([name,'unresolved','unresolved','unresolved',f'{fine["welfare"]["spread"]:.5f}'])
table=Table(data,colWidths=[112,83,94,76,125]);table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Times-Bold'),('FONTNAME',(0,1),(-1,-1),'Times-Roman'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),6),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eae5')),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#6f8580')),('ALIGN',(1,0),(-1,-1),'RIGHT')]))
story.append(table);p('Table1. Approximate display values; full directed enclosures and exact binary64-import semantics accompany the data. Positive fine-grid spread is compatible with convergence of worst values and shows why unique finite basins must not be asserted.','Caption')
different=0
for r in cont:
 nominal=next(x for x in all_cont if x['scenario']==r['scenario'] and x['continuum']=='nominal')
 different+=sum(a['classification']!=b['classification'] for a,b in zip(r['comparisons'],nominal['comparisons']))
p(f'The declared nominal-epsilon sensitivity check changes {different} of 40 classifications relative to effective epsilon. The main effective model carries the exact-real sum of imported epsilon and the binary64 literal 1e-12. Its sum is recorded separately from JavaScript\'s rounded addition; neither is presented as an exact replay of all floating profit/subtraction operations.','Small')
br()

h('5 Reproducibility and independent checks')
p('The mesh protocol, code and old inputs were hashed before its 72 cases. A separate streaming auditor enumerated every payoff pair on every grid, independently recovered the allowed upper maps and fixed destinations, and checked each initial-pair tail. It used no primary binary-search function. All matching old graph certificates were crosschecked. The independent continuous auditor uses separate 130-digit interval arithmetic and an independent logarithmic residual for Lambert-W; it imports no primary model or interval calculation function.')
p(f'Mesh audit: {ma["payoffPairsScanned"]:,} payoff pairs, {ma["pairTailValuesChecked"]:,} initial-pair tail values, {ma["checks"]:,} checks and five rejected corruption controls. Mesh run: {mc["seconds"]:.3f} seconds, sampled RSS {mc["largestObservedRSSBytes"]/1e6:.2f} MB. The 16 continuous records use 80-digit directed arithmetic, padded Decimal exp/log endpoints and sign-certified normalized root brackets narrower than 1e-25. Independent audit: {ca["records"]} records and {ca["comparisonCount"]} retained comparisons. Primary continuum run: {cc["resources"]["seconds"]:.2f} seconds, sampled RSS {cc["resources"]["largestObservedRSSBytes"]/1e6:.2f} MB. Memory samples are not continuously measured peaks.')
p('Exact imported constants, source/input hashes, root signs, global sufficient-condition enclosures, all successful/unresolved comparisons, timing and per-case journals are saved. Failures and labels are not dropped. Synthetic tests cover rational containment, correctly padded transcendentals, known roots, clipped fixed points, malformed identities and retained failures. Both independent interval implementations share Python\'s Decimal transcendental backend; this is not a fully independent arithmetic stack or formal verification. The continuous statement additionally depends on the reviewed proof and validated enclosures.')
h('6 What is new, and what remains missing')
p('Price-grid sensitivity, initialization effects, logit best responses, graph/basin audits and finite abstractions are established. The narrow contribution is the transfer question for this lagged payoff-tolerance action restriction: a valid coarse-grid one-execution certificate, its continuous all-policy welfare floor, and a refinement explanation accounting for the grid-based best-profit benchmark. This targeted source review does not establish first publication or broad novelty.')
p('Closest sources include Calvano et al.(2020,AER110:3267-3297,doi:10.1257/aer.20190623); Calvano et al.(2023,IJIO90:102973,doi:10.1016/j.ijindorg.2023.102973); Loots and den Boer(2023,POM32:1169-1186,doi:10.1111/poms.13919); and Lopes de Moraes and De Losso(2026,arXiv:2610.21867v2), whose frozen-policy DP/basin and grid audit predates this sprint. Pola and Tabuada(2009,arXiv:0707.4205) and Saldi et al.(2017,doi:10.1287/moor.2016.0832) provide broader abstraction/approximation context. Exact primary links and inspected sections are in REFINEMENT_NOVELTY.md.','Small')
p('This is a known deterministic symmetric model with a common compact price interval. Above-Nash permitted stationary prices are approximate-Nash outcomes by the guard\'s definition. They need not form an exact equilibrium or a credible repeated-game strategy. The stored unilateral deviation gain makes that distinction explicit. We show neither autonomous discovery nor real-market collusion, human comprehension, unknown-model robustness or an optimal general controller.')
p('A practical next question is whether sparse recurring caps can restore a chosen target with a quantified intervention frequency. That changes the ongoing controller and needs its own protocol; it cannot rescue the claim that a finite initializer alone protects the continuous target. Incentive stability and independent learner behavior remain separate research questions.','Small')
h('AI assistance and local reproduction')
p('Codex research/coding agents substantially assisted formulation, implementation, analysis, separate auditing and writing under Mohammadpayam Teabi\'s direction. AI-agent review is not human peer review. No model game players, new learning, paid services, customer data, external submission or public deployment were used in this stage. The graphical page explains saved evidence and is not human-subject validation.','Small')
p('Read-only checks: node research/audit-mesh-refinement.js and python research/audit-continuous-study.py. Rebuild figures with python research/build-refinement-figures.py; this note with python research/build-refinement-note.py. Earlier finite-grid reports and archives are preserved.','Small')

class ReproducibleCanvas(Canvas):
 def __init__(self,*a,**kw):kw['invariant']=1;super().__init__(*a,**kw)
def footer(c,d):c.saveState();c.setFont('Times-Roman',9);c.drawCentredString(A4[0]/2,23,str(d.page));c.restoreState()
pdf=OUT/'continuous-refinement-note.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=43,rightMargin=43,topMargin=35,bottomMargin=36,title='When a Safe Handover Depends on the Price Grid',author='Mohammadpayam Teabi').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=ReproducibleCanvas)
texts=[page.extract_text() for page in PdfReader(str(pdf)).pages]
checks={'pdf':pdf.relative_to(ROOT).as_posix(),'pages':len(texts),'bytes':pdf.stat().st_size,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'supplementaryNote':True,'pageTextCharacters':[len(t) for t in texts],'bothIndependentAudits':True}
(OUT/'refinement-note-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');(OUT/'continuous-refinement-note.txt').write_text('\n\n---PAGE---\n\n'.join(texts),encoding='utf-8')
if len(texts)!=4:raise SystemExit(json.dumps(checks))
print(json.dumps(checks))
