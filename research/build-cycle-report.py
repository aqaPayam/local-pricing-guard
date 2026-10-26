"""Create a separate version-3 paper; preserve the reviewed version-2 files."""
from pathlib import Path
import sys,json,re,hashlib
from xml.sax.saxutils import escape
try:import reportlab
except ImportError:sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'))
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8'))
AUDIT=read('research/cycle-results/independent-audit.json');DONE=read('research/cycle-results/completion.json')
if not AUDIT['passed']:raise SystemExit('Independent cycle audit must pass')
INDEX=read('research/cycle-results/index.json');CASES={r['id']:read('research/cycle-results/'+r['file']) for r in INDEX}
STRUCT={r['id']:r for r in read('research/cycle-results/structure.json')['records']}
SCENARIOS=read('research/cycle-results/manifest.json')['plan']['scenarios']
LABELS=['Base, 15 prices','Scale 0.5','Lower value','Lower cost','Base, 11 prices','Base, 31 prices','Half tolerance','Double tolerance']
styles=getSampleStyleSheet()
for name,font,size,leading in [('Body','Times-Roman',10.3,13.0),('Small','Times-Roman',9.2,11.6),
 ('Heading','Times-Bold',13.1,16),('Sub','Times-Bold',11.2,14),('Caption','Times-Roman',9,11.4),
 ('Cell','Times-Roman',8.7,10.6),('CellHead','Times-Bold',8.7,10.6),('Equation','Courier',9.1,12.2)]:
 styles.add(ParagraphStyle(name='C'+name,fontName=font,fontSize=size,leading=leading,spaceAfter=7))
styles.add(ParagraphStyle(name='CTitle',fontName='Times-Bold',fontSize=21,leading=24,alignment=TA_CENTER,spaceAfter=6))
styles.add(ParagraphStyle(name='CSubtitle',fontName='Times-Bold',fontSize=12.5,leading=16,alignment=TA_CENTER,spaceAfter=9))
styles.add(ParagraphStyle(name='CCenter',fontName='Times-Roman',fontSize=10.4,leading=13,alignment=TA_CENTER,spaceAfter=5))
story=[];plain=[]
def p(t,s='Body'):story.append(Paragraph(t,styles['C'+s]));plain.append(re.sub('<[^>]*>','',t))
def h(t):p(t,'Heading')
def sub(t):p(t,'Sub')
def br():story.append(PageBreak());plain.append('\n--- PAGE ---\n')
def fig(name,caption,width=490):
 f=ROOT/'research/cycle-figures'/name;w,hh=PILImage.open(f).size
 story.append(Image(str(f),width=width,height=width*hh/w));p(caption,'Caption')
def table(headers,rows,widths):
 cells=[[Paragraph(escape(str(v)),styles['CCellHead' if i==0 else 'CCell']) for v in row] for i,row in enumerate([headers]+rows)]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([
 ('LINEABOVE',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,0),(-1,0),.4,colors.black),
 ('LINEBELOW',(0,-1),(-1,-1),.6,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),
 ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
 story.append(t);story.append(Spacer(1,7))
def anchor(c):return next(r for r in c['objectives']['minCS']['diagnosticStarts'] if any(p['kind']=='near-continuous-Nash-anchor' for p in r['provenance']))
def welfare(c):return c['objectives']['minCS']['universalWitness']['consumerSurplus']

abstract=('A pricing guard can accept every proposal while leaving little economic choice, and observed customer benefit need not characterize every permitted policy. '
'We audit a lagged own-profit-tolerance guard in a finite logit duopoly against fully coordinated sellers. '
'Using established minimum-mean-cycle optimization, we compute reachable long-run customer-surplus minima and joint-profit maxima for eight fixed configurations under the guard, a price cap and no control. '
'Independent reconstruction verifies all 24 graphs, 48 objectives, reachable witnesses and numerical potential certificates. '
'An interval and monotone-upper-map condition reduces the global customer-surplus minimum to the largest symmetric self-feasible price. '
'A condensation-graph argument additionally bounds finite-horizon transient harm. '
'All optimized outcomes are stationary; complicated cycles are unnecessary. '
'Six guard configurations have distinct history-dependent reachable outcomes. '
'Every saved unprotected-training endpoint can reach its configuration\'s global guard worst case, whereas protected-training endpoints remain in safer regions in those six configurations. '
'Three worst guard outcomes are already exact finite-grid Nash equilibria; five exceed every finite-Nash price, without establishing strategic stability or learner discovery. '
'The contribution is a reproducible, model-specific economic capacity audit and structural explanation, not a new graph algorithm, evidence of emergent collusion, or a real-market guarantee.')
assert 150<=len(abstract.split())<=250
p('Who Chooses the Price?','Title');p('History-dependent protection in guarded pricing','Subtitle')
p('Mohammadpayam Teabi','Center');p('Independent researcher | AI Collusion Research Sprint 2026','Center')
h('Abstract');p(abstract)
h('1 Introduction')
p('When a guard controls executed prices, a favorable learned trajectory can reflect a restricted or unusually safe part of the permitted game. '
'We therefore ask: <b>what customer outcome can any coordinated sequence of allowed prices sustain, and does the public price history at handover matter?</b> '
'A public-state optimizer intentionally replaces the sellers; its output measures feasible capacity, not spontaneous collusion.')
p('Earlier local Q-learning studies separated proposal acceptance, permitted choice and welfare. This follow-up replaces sampled behavior as the basis for a guarantee with a finite-graph audit. '
'It finds both protection and limits: the guard greatly raises worst customer benefit relative to no control, but the cap has a higher global floor in all eight configurations. '
'Initialization explains why some earlier protected learners looked safer than the guard\'s all-state envelope.')
br()

h('2 Prior Work and Model')
p('Q-learning pricing and transfer to new rivals are established [1,2]. Shielding and action restriction already address permitted future behavior and intervention [3,4]. '
'Mean-payoff supervisory control [5], minimum-cycle-mean optimization [6] and corrected witness extraction [7] are prior methods. Economic platforms have been optimized against learning sellers [8]; '
'regret-based collusion audits study a different compliance criterion [9]. We contribute a model-specific economic comparison, a conditional structural derivation and checked handover-state distinctions. '
'We do not introduce shielding, an optimization algorithm, or a general theory of collusion.')
sub('2.1 Economy and controller')
p('Two symmetric sellers choose prices on the unchanged grid of the earlier study. Demand is logit with an outside option, unit cost c, quality v, scale mu and B=100 buyers:')
p('s_i(p)=exp((v-p_i-v0)/mu) / (1+sum_j exp((v-p_j-v0)/mu))<br/>profit_i=B*(p_i-c)*s_i; C(p)=B*mu*log(1+sum_j exp((v-p_j-v0)/mu)).','Equation')
p('The guard uses the <i>previous executed rival price</i> r, not an unseen simultaneous choice. Its allowed index set S(r) contains prices whose modeled one-step own profit is within epsilon of the best response to r. '
'A rejected proposal projects to the nearest allowed index; a proposal already in S(r) executes unchanged. The cap clips at the grid price nearest continuous symmetric Nash. No control allows the full grid.')
p('Let pN and pJ denote continuous symmetric Nash and joint-profit-maximizing prices, with gap g=pJ-pN. Each n-point grid is equally spaced from pN-.1g to pJ+.1g. '
'Tolerance is .1 times own continuous Nash profit divided by base continuous Nash profit, times the declared factor. Nearest-price ties choose the lower index; guard feasibility and finite-Nash comparisons use a 1e-12 payoff allowance.','Small')
sub('2.2 Fixed cases and information')
p('Eight configurations preserve the preceding study\'s grids, economics and tolerance normalization: four calibrations at 15 prices, base grids of 11 and 31 prices, and half/double base tolerance. '
'Base parameters are v=2, c=1, mu=.25, v0=0, epsilon=.1. The altered calibrations change mu to .5, v to 1.5 or c to .6. '
'Tolerance scales with continuous Nash profit. Four calibrations cover three dimensionless shapes; the changed-scale and lower-value cases are affine-equivalent checks.')
p('The public state is (i,j), the previous executed indices. A feasible edge to (a,b) exists iff a belongs to S(j) and b belongs to S(i). '
'Both choices can follow a pre-agreed public policy without observing current quotes. Rewards belong to destination (a,b). We separately minimize long-run average C and maximize joint profit. '
'Each witness reports both seller profits. Coordination, mutual benefit, unilateral stability and independent learning are distinct claims.')
br()

h('3 Graph Bounds and a Structural Explanation')
p('Tarjan decomposition and Karp dynamic programming solve cyclic strongly connected components; reachable-component propagation gives each starting state\'s attainable envelope. '
'A Bellman-Ford shifted-weight search recovers a cycle. For lower bound L and potential h, every internal edge satisfies w(u,v)+h(u)-h(v) &gt;= L. '
'The cycle gives an upper bound, and negated rewards handle maximum joint profit. Complete-support cap/no-control graphs reduce to destination extrema with self-loops.')
sub('3.1 Why a constant price can be the worst case')
p('<b>Proposition.</b> Suppose every S(j) is a nonempty integer interval [L(j),U(j)], U is nondecreasing, and C decreases in both prices. '
'Let m be the largest j with j in S(j). The global minimum customer-surplus cycle mean equals C(p_m,p_m).')
p('<b>Proof.</b> Take any cycle and its largest executed index M. An edge producing M has previous rival index r &lt;= M, so M &lt;= U(r) &lt;= U(M). '
'A state containing M has a successor whose other price k lies in S(M); k &lt;= M gives L(M) &lt;= M. Thus M lies in S(M), hence M &lt;= m. '
'Every cycle price is at most p_m, so coordinatewise surplus monotonicity bounds its mean by C(p_m,p_m). The feasible self-loop at (m,m) attains equality. '
'Logit surplus has derivative -B*s_i &lt; 0. Finite-map interval and U-monotonicity remain assumptions to check, not universal claims about all price guards.')
fig('history-basins.png','Figure 1. Lowest reachable long-run customer benefit by previous executed price pair. Different colors are different reachable envelopes under the same guard. The global worst stationary pair need not be reachable from the near-Nash start. These are state maps, not independent statistical samples.')
br()

h('4 Results: Protection Depends on the Starting History')
rows=[]
for label,s in zip(LABELS,SCENARIOS):
 g=CASES[s['id']+'-guard'];cap=CASES[s['id']+'-cap'];none=CASES[s['id']+'-none']
 rows.append([label,f'{welfare(g):.3f}',f'{anchor(g)["result"]["upperBound"]:.3f}',f'{welfare(cap):.3f}',f'{welfare(none):.3f}',f'{g["objectives"]["minCS"]["universalWitness"]["profitA"]:.3f}'])
table(['Configuration','Guard global','Guard near-Nash','Cap global','None global','Guard profit / seller'],rows,[111,76,82,72,72,78])
p('Table 1. Minimum attainable long-run customer benefit, except the last column: each seller\'s profit at the guard\'s global minimum-CS witness. Both profits coincide here; raw results retain both. '
'Each economy uses its own monetary units. Values are deterministic finite-game optima with numerical certificates, not seed averages or cross-economy pooled effects.','Caption')
p('All 24 minimum-CS witnesses and all 24 maximum-joint-profit witnesses are stationary. In every guard case the two objectives select the same price pair, although they were solved separately. '
'The structural proposition applies in 24/24 cases and exactly matches computed minimum-CS witness values. Six guard configurations have multiple start-dependent reachable values.')
p('All 64 saved unprotected-training endpoints can reach their scenario\'s global guard worst case. In the six history-dependent configurations, all protected-training endpoints lie in safer regions. '
'These are dependent diagnostics from eight earlier paired seeds per configuration, not 64 new independent replications. We preserve all 256 training endpoints and compare 256 protected finite evaluations against their controller\'s finite-horizon certificates.')
p('<b>Important qualification:</b> the global guard pair is itself an exact finite-grid stage Nash equilibrium in base15, half tolerance and lower cost. Base15 has two symmetric finite Nash pairs: '
'(1,1), C=72.119 and profit=22.020 per seller; and (2,2), C=68.477 and profit=23.628. That gap is partly coarse-grid equilibrium selection, not a new cartel discovery. '
'The other five guard worst pairs exceed every exact finite-Nash price, but their dynamic incentive stability remains untested.')
br()

h('5 Finite Horizons and Independent Verification')
sub('5.1 A bound on temporary harm')
p('Under the proposition, every cyclic state has surplus at least C*. A state with C &lt; C* is an acyclic singleton and can be visited at most once. '
'On the condensation DAG assign deficit d(k)=max(0,C*-C(k)) to such singletons, zero otherwise, and compute:')
p('D(c)=max({0} union {d(k)+D(k): c -&gt; k}).<br/>average_T(C) &gt;= C* - D(component(start))/T.','Equation')
p('The previous starting state\'s reward is excluded. h(state)=D(component(state)) supplies a full-edge potential certificate, including cross-component transitions. '
'Numerical slack is subtracted from the floor and negative residual rounding is absorbed explicitly. This is stronger than applying an internal-SCC certificate to a transient prefix.')
fig('finite-horizon-correction.png','Figure 2. Conservative worst-start transient allowance decays as 1/T. Curves overlap for some settings, including the affine-equivalent pair. The allowance is a certificate term, not observed customer harm. At T=20,000 the largest absolute correction is approximately 0.003064 surplus units (lower-cost case).',width=480)
sub('5.2 Audit and resources')
p(f'A separate implementation rebuilt all {AUDIT["cases"]} games, {AUDIT["objectives"]} objectives, {AUDIT["totalStateInstances"]:,} state instances and {AUDIT["totalImplicitEdgeInstances"]:,} implicit edges. '
'It checked economics, components, all-start reachability, prefixes, cycles, individual profits, all certificate inequalities and the structural finite-horizon bounds. '
'Five injected corruptions (action, reward, dual bound, prefix and finite-horizon bound) were rejected. '
f'Maximum primal-dual gap was {AUDIT["maximumPrimalDualGap"]:.3g}; economic recomputation discrepancy was zero. '
f'The primary search took {DONE["seconds"]:.3f} seconds. Maximum observed post-case RSS was 238.5 MB, exceeding the 100 MB target; heap used at that sample was 80.5 MB. '
'This was not continuous peak-memory measurement; no case was dropped.')
br()

h('6 Meaning, Limits and Reproduction')
fig('reachable-welfare.png','Figure 3. Guard worst-case bounds normalized by the same configuration\'s permanent-cap floor. Gray segments show the difference between an arbitrary initial state and the near-Nash anchor. Coincident red/green markers share the same bound. No raw cross-economy welfare averages are pooled.',width=475)
p('A guard may protect against every coordinated permitted sequence in one public-state region while allowing lower-welfare outcomes from another. '
'For safe activation or handover, the initial executed-price history therefore belongs in the guarantee statement. '
'A controller\'s acceptance rate alone measures neither this distinction nor seller freedom. The cap has a higher all-state customer floor in all eight cases, with a different profit/choice tradeoff; there is no all-objective dominance claim.')
p('The strongest limits are known deterministic symmetric demand, finite grids, privileged model knowledge and a fully coordinated controller. '
'The analysis establishes capacity and numerical bounds in that game, not that independent agents would discover or sustain the witness. '
'No unilateral discounted-deviation audit, asymmetric/noisy market validation, continuous-price theorem or human comprehension study is claimed. '
'An exact-grid Nash pair need not be the continuous-game Nash price. More seeds do not repair these scope limits.')
p('The graphical Stress Lab replays a selected reachable prefix and stationary loop, showing both profits and customer benefit. A manual mode lets a human deliberately coordinate both shops within the same finite allowed sets. '
'It is distinct from the earlier continuous-price human game. Browser interactions are developer checks, not human-subject evidence.')
p('<b>Code and data.</b> The separate evidence package includes the frozen cycle protocol, solver, 24 cases, all-start witnesses, numerical potentials, input/checkpoint provenance and independent audit. '
'Run <font face="Courier">node research/audit-cycle-study.js</font> for a read-only audit; optional figures use '
'<font face="Courier">python research/build-cycle-figures.py</font>. Start the local demo server and open /stress. '
'Version-2 report/evidence remain preserved; the extension uses no API game player, purchased compute or paid service. This report is substantially AI-assisted; see Appendix A.')
br()

h('References')
refs=[
'[1] E. Calvano, G. Calzolari, V. Denicolo and S. Pastorello. Artificial Intelligence, Algorithmic Pricing, and Collusion. American Economic Review110(10),3267-3297,2020. https://doi.org/10.1257/aer.20190623',
'[2] N. Eschenbaum, F. Mellgren and P. Zahn. Robust Algorithmic Collusion. arXiv:2201.00345,2022. https://arxiv.org/abs/2201.00345',
'[3] M. Alshiekh et al. Safe Reinforcement Learning via Shielding. AAAI2018; arXiv:1708.08611. https://arxiv.org/abs/1708.08611',
'[4] B. Konighofer et al. Shields for Safe Reinforcement Learning. Communications of the ACM68(11),80-90,2025. https://doi.org/10.1145/3715958',
'[5] Y. Ji, X. Yin and S. Lafortune. Optimal supervisory control with mean payoff objectives and under partial observation. Automatica123,109359,2021. https://doi.org/10.1016/j.automatica.2020.109359',
'[6] R. M. Karp. A characterization of the minimum cycle mean in a digraph. Discrete Mathematics23(3),309-311,1978. https://doi.org/10.1016/0012-365X(78)90011-0',
'[7] M. Chaturvedi and R. M. McConnell. A note on finding minimum mean cycle. Information Processing Letters127,21-22,2017. https://doi.org/10.1016/j.ipl.2017.06.007',
'[8] G. Brero, E. Mibuari, N. Lepore and D. C. Parkes. Learning to Mitigate AI Collusion on Economic Platforms. NeurIPS35,2022. https://papers.neurips.cc/paper_files/paper/2022/file/f746974abd33c0015ca583a267dac1fd-Paper-Conference.pdf',
'[9] J. D. Hartline, C. Wang and C. Zhang. Regulation of Algorithmic Collusion, Refined: Testing Pessimistic Calibrated Regret. arXiv:2501.09740,2025. https://arxiv.org/abs/2501.09740',
'[10] Poseidon Research. AI Collusion Research Sprint starter repository. https://github.com/poseidon-research/collusion_hackathon',
'[11] Apart Research. AI Collusion Research Sprint,23-25October2026: public guidelines and report template. https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25']
for ref in refs:p(escape(ref),'Small')
h('Author Contributions')
p('Mohammadpayam Teabi supplied project direction, its original game context and authorization. AI agents assisted problem formulation, proofs, implementation, local execution, auditing, literature review, graphics and drafting. '
'Separate AI-agent review is not independent human peer review. The new work extends the earlier game and learned-policy evidence using established methods, with their provenance preserved.','Small')
br()

h('Appendix A. Limitations and Dual-Use / Ethical Considerations')
sub('A.1 Chronology and evidence')
p('The original pricing studies and version-2 report preceded this extension. Known outcomes motivated the new question. '
'The cycle protocol, solver, tests, structural note and input/checkpoint hashes were frozen at 2026-10-25T22:07:06.907Z, before the 24 substantive optimizations. '
'The local manifest SHA256 is 176c7c0b226fea52ad80982896cdfdb650c46064aa37dae9a7b7575eceaa4b0b. This is local ordering, not third-party registration. '
'Interpretation of initialization and proposed future interventions followed the results. All assigned cases were retained.','Small')
p('This deterministic graph audit has no statistical seed count. The prior comparison uses eight paired training seeds per configuration, reused across variants; four calibrations cover three demand shapes. '
'Branches, configurations, initial states and repeated cycles do not become independent experimental replications. Existing learning source snapshots and outputs remain unchanged. '
'The prior 768 million training transitions were not independently replayed by this cycle study; their checkpoint provenance and relevant public start states were checked.','Small')
sub('A.2 Potential misuse and scope')
p('Explicit worst-case coordinated pricing policies could help someone design anticompetitive behavior or misleading compliance displays. We expose both seller profits, reachable-state qualifications, ordinary cap baselines and cases already explained by finite Nash multiplicity. '
'The released setting is a toy known-economy simulation, with no customer data or real deployment certificate. Neither a tolerance check nor the graph result establishes legal compliance. '
'The controller\'s model knowledge and deterministic finite grid are substantive assumptions. No human comprehension or external-market validation is invented.','Small')
sub('A.3 LLM Usage Statement')
p('This report is substantially AI-drafted under the author\'s direction. Codex research/coding agents assisted conceptualization, mathematics, implementation, local runs, independent numeric checks, primary-source review and presentation. '
'The audit is a separately implemented AI-agent check, not an unperformed human replication. Current experimental players are local algorithms or a deliberately coordinated finite-game optimizer; there are no new LLM/API game calls or paid services. '
'Earlier exploratory account-backed pilots consumed342 requests and are excluded from the tabular and cycle evidence. Their history is not relabeled as free or as part of this experiment.','Small')
sub('A.4 Reproducibility limits')
p('Certificates use IEEE754 calculations on logit-derived rewards, not interval enclosures of exponentials. Their numerical gaps/residuals are explicitly retained. '
'The structural proposition is a conditional mathematical statement; the 24 finite-map assumption checks do not establish continuous-price or general-market versions. '
'The graphical replay illustrates known computed paths and its developer checks do not supply behavioral evidence about real people. '
'No project has been externally submitted or published by this extension.','Small')

class ReproducibleCanvas(Canvas):
 def __init__(self,*a,**kw):kw['invariant']=1;super().__init__(*a,**kw)
def footer(canvas,doc):
 canvas.saveState();canvas.setFont('Times-Roman',9);canvas.drawCentredString(A4[0]/2,24,str(doc.page));canvas.restoreState()
pdf=OUT/'price-guard-study-v3.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=39,
 title='Who Chooses the Price? History-dependent protection in guarded pricing',author='Mohammadpayam Teabi').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=ReproducibleCanvas)
reader=PdfReader(str(pdf));texts=[p.extract_text() for p in reader.pages]
refpage=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t))
checks={'pdf':pdf.relative_to(ROOT).as_posix(),'bytes':pdf.stat().st_size,'pages':len(texts),'bodyPages':refpage,
 'abstractWords':len(abstract.split()),'abstractText':abstract,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
 'pageTextCharacters':[len(t) for t in texts],'requiredEthicalAppendix':any('Limitations and Dual-Use / Ethical Considerations' in t for t in texts),
 'llmUsageStatement':any('LLM Usage Statement' in t for t in texts)}
(OUT/'report-checks-v3.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
(OUT/'price-guard-study-v3.txt').write_text('\n\n---PAGE---\n\n'.join(texts),encoding='utf-8')
if checks['bodyPages']!=6 or not checks['requiredEthicalAppendix'] or not checks['llmUsageStatement']:raise SystemExit(json.dumps(checks))
print(json.dumps({k:checks[k] for k in ['pages','bodyPages','abstractWords','bytes','sha256']}))
