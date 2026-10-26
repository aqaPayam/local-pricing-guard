"""Prospective streaming V13 delivery. Never reruns primary training.

Fresh verification independently replays all12 new training trajectories from
zero. A later viewer points to the final full archive without nesting it.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,sys,time,uuid,zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('closed_v12_packager',ROOT/'research/package-matched-clock.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
stream,base,json_bytes=prior.stream,prior.base,prior.json_bytes
BASE=ROOT/'output/price-guard-matched-clock-v12.zip'
BASE_SHA='ecce6c53c83f091792b37f38a6fa2de7a4c5ad81f33d678464b7b3f219c3a18a'
STUDY_SHA='1d800d2a8bae45a0d3710de3889674fa9ed95202f5484619454242e90a34d4e3'
AUDIT_SHA='2443c1f0874aac903c2125b68b47d6c7a7401d801969829b433d79a47e14bc7b'
BENCHMARK_SHA='474b0408fd9256e7741bee7e78397c19c7e49778365bebd42942469d0677e8e1'
PYTHON_SHA='62ebc90a2884bb63a0cd67e789cafdd51e771eee043587e2354327b4ccc9bb05'
FULL=ROOT/'output/price-guard-full-grid-reference-v13.zip'
PLAN=ROOT/'output/guard-reference-package-plan.json'
RECEIPT=ROOT/'output/guard-reference-package-verification.json'
VIEW=ROOT/'output/price-guard-viewer-v13.zip'
VIEW_PLAN=ROOT/'output/viewer-v13-package-plan.json'
VIEW_RECEIPT=ROOT/'output/viewer-v13-package-verification.json'
PDF='output/pdf/local-guard-welfare-report-v13.pdf'
REPORT_BUILDER='research/build-main-report-v13.py'
PREFIX='research/guard-reference-results/'
NODE_TESTS=['tests/guard-reference-learning.test.js','tests/guard-reference-case.test.js','tests/guard-reference-study.test.js','tests/guard-reference-audit.test.js','tests/guard-reference-cross-audit.test.js','tests/guard-reference-serialization-audit.test.js','tests/guard-reference-game.test.js','tests/reference-view.test.js']
PY_TESTS=['test_guard_reference_case.py','test_guard_reference_baseline.py','test_guard_reference_replay_process.py','test_guard_reference_supervisor.py','test_guard_reference_benchmark.py','test_guard_reference_analysis.py','test_guard_reference_cross_anchors.py','test_guard_reference_inventory_audit.py','test_guard_reference_export.py','test_evidence_streaming.py','test_guard_reference_delivery.py']
HARNESSES=['.local/guard-reference-display-smoke.mjs','.local/guard-reference-export-smoke.py']
SCRIPTS=['build-guard-reference-web.py','build-guard-reference-figure.py','package-guard-reference.py','build-main-report-v13.py','guard-reference-game.js','demo-server.js']
DOCS=['GUARD_REFERENCE_RESULTS.md','GUARD_REFERENCE_REVIEW.md','GUARD_REFERENCE_REPLAY_QA.md','REFERENCE_PLAIN_LANGUAGE.md','REFERENCE_USABILITY_REVIEW.md','GUARD_REFERENCE_EXPORT_PEER_REVIEW.md','CURRENT_DEMO_WALKTHROUGH.md','V13_SUBMISSION_REVIEW.md','README.md']
ADMIN=['.local/check-guard-reference-benchmark-independent.py','.local/check-guard-reference-benchmark-v2-independent.py','.local/check-guard-reference-v2-admin-schema.py','.local/v13-report-authoring-state.json','.local/guard-reference-before-undo-feedback.js','.local/v13-report-build-2.log','.local/v13-report-build-3.log']
digest=lambda p:stream.digest_file(p)['sha256']
local=prior.local
jread=prior.jread
def route_imports(sources,routes,add):
 # Only routed production modules are runnable import roots. Frozen scientific
 # sources close separately through the 29-source manifest; copied evidence and
 # quoted test fixtures must never be mistaken for new runtime imports.
 roots=set(routes.values())|{'research/demo-server.js'}
 runnable={n:sources[n] for n in roots if n in sources}
 def include(name,reason):
  n=add(name,reason);runnable[n]=sources[n];return n
 return prior.route_imports(runnable,routes,include)

def require_pinned_python():
 if digest(Path(sys.executable))!=PYTHON_SHA:
  raise RuntimeError('Use the prospectively pinned CPython3.13 executable; absolute path is provenance only')

def milestone(message):
 print('[V13 delivery] '+message,file=sys.stderr,flush=True)

def write_json_exclusive(path,value):
 with Path(path).open('xb') as handle:handle.write(json_bytes(value))

def suite_counts(node_tests,python_tests,game_test):
 """Count reviewed Node unit tests and Python loader cases; never real runs."""
 node=shutil.which('node')
 if not node:raise RuntimeError('Node24+ required; no automatic installation')
 def node_count(names):
  output=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*names],ROOT,timeout=300)
  match=re.search(r'^# tests (\d+)$',output,re.M)
  if not match or not re.search(r'^# fail 0$',output,re.M) or not re.search(r'^# pass '+match.group(1)+'$',output,re.M):raise ValueError('Reviewed Node unit tests failed while counting final suites')
  return int(match.group(1))
 script="import json,unittest\ncounts={}\nfor p in "+repr(python_tests)+":\n loader=unittest.TestLoader();suite=loader.discover('tests',p)\n if loader.errors:raise RuntimeError(str(loader.errors))\n counts[p]=suite.countTestCases()\nprint(json.dumps(counts))"
 python_counts=json.loads(base.execute([sys.executable,'-B','-c',script],ROOT,timeout=300))
 if any(type(n) is not int or n<=0 for n in python_counts.values()):raise ValueError('Empty/missing Python suite')
 node_total=node_count(node_tests);game_count=node_count([game_test]);delivery=sum(python_counts[n] for n in ['test_evidence_streaming.py','test_guard_reference_delivery.py']);scientific=sum(python_counts.values())-delivery
 return {'expectedNode':node_total,'expectedPythonScientific':scientific,'expectedDelivery':delivery,'expectedTotal':node_total+scientific+delivery,'gameTestCount':game_count,'pythonSuiteCounts':python_counts,'testDiscoveryScope':'Reviewed Node unit suites execute to count actual passing cases; Python unittest loader counts. All specified suites execute again in fresh verification. No primary training or new market training is invoked.'}

def collect(game_test_count):
 require_pinned_python()
 if digest(BASE)!=BASE_SHA:raise ValueError('Closed V12 archive changed')
 audit=jread(PREFIX+'independent-audit.json')
 if digest(ROOT/(PREFIX+'independent-audit.json'))!=AUDIT_SHA or not(audit.get('passed') is True and audit.get('runs')==12 and audit.get('checkpointSlots')==24 and audit.get('finalSourceInputOutputIntegrityCheck') is True):raise ValueError('Complete authoritative full-grid reference acceptance required')
 if digest(ROOT/(PREFIX+'manifest.json'))!=STUDY_SHA:raise ValueError('Accepted scientific manifest changed')
 with zipfile.ZipFile(BASE) as z:
  names=z.namelist();inherited=json.loads(z.read('PACKAGE_CONTENTS.json'))['files']
  if len(names)!=len(set(names)) or set(names)!=set(inherited)|{'PACKAGE_CONTENTS.json'} or any(not stream.safe_name(n) for n in names):raise ValueError('Unsafe/unmanifested V12 inventory')
 sources={n:{'kind':'zip','archive':BASE,'member':n} for n in inherited}
 mutable={'README.md','research/README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','DELIVERY_FREEZE.json','research/demo-server.js','research/demo/overview.html','research/demo/overview.css','research/demo/overview.js'}
 protected=set(sources)-mutable;provenance={};expected={}
 def add(name,reason):
  p,n=local(name)
  if any(word in n for word in ['private-pilot','codex-adapter']) or 'CANDIDATE' in n and n not in inherited:raise ValueError('Unrequested private/future candidate '+n)
  observed=stream.digest_file(p)
  if n in protected and any(observed[k]!=inherited[n][k] for k in ['sha256','bytes']):raise ValueError('Protected V12 byte changed '+n)
  sources[n]={'kind':'file','path':p};provenance.setdefault(n,set()).add(reason);return n
 for name in SCRIPTS:add('research/'+name,'accepted V13 derivation/report/delivery source')
 for name in DOCS:add('research/'+name,'accepted current narrative/review/presentation scope')
 node_tests=NODE_TESTS.copy();game_test='tests/guard-reference-game.test.js'
 for name in node_tests+['tests/'+p for p in PY_TESTS]+HARNESSES+['tests/helpers/guard-reference-web-fixture.js']:add(name,'targeted artificial or read-only actual verification')
 for folder in ['research/guard-reference-results','research/guard-reference-figures']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file():add(p,'complete accepted new raw/derived evidence or figure')
 for name in ['local-guard-welfare-report-v13.pdf','local-guard-welfare-report-v13.txt','main-report-v13-checks.json']:add('output/pdf/'+name,'distinct accepted V13 report')
 for name in ['README.md','output/matched-clock-package-verification.json',*ADMIN]:add(name,'current entry or administrative provenance')
 m=jread(PREFIX+'manifest.json')
 for group in ['sourceHashes','inputHashes']:
  for name,h in m[group].items():
   expected[add(name,'frozen manifest / exact '+group)]=h
   if group=='sourceHashes':expected[add(PREFIX+'sources/'+name,'frozen primary source snapshot')]=h
 start=jread(PREFIX+'execution-start.json');admin=start['adminGate']
 expected[add(admin['file'],'post-freeze independently accepted administrative receipt')]=admin['sha256']
 if stream.digest_file(ROOT/admin['file'])!={k:admin[k] for k in ['sha256','bytes']}:raise ValueError('Actual admin receipt reference drift')
 if digest(ROOT/'.local/guard-reference-benchmark-v2.json')!=BENCHMARK_SHA:raise ValueError('Final source-bound artificial benchmark changed')
 # These bounded engineering logs/receipts are history, not extra market runs.
 for p in sorted((ROOT/'.local').glob('guard-reference-*')):
  if p.is_file() and p.suffix in {'.json','.txt','.log','.py','.mjs','.png'}:
   if p.stat().st_size>25_000_000:raise ValueError('Review oversized engineering history before delivery '+p.name)
   add(p,'explicit reference-stage engineering/developer history; not new scientific cases')
 for receipt_name in ['.local/guard-reference-benchmark.json','.local/guard-reference-benchmark-v2.json']:
  historical=jread(receipt_name);folder=historical['directory'];p,n=local(folder)
  for ref in historical['artifacts']:
   if stream.digest_file(ROOT/ref['file'])!={k:ref[k] for k in ['sha256','bytes']}:raise ValueError('Historical artificial artifact drift '+ref['file'])
  for name,h in historical['sourceHashes'].items():
   if digest(p/'sources'/name)!=h:raise ValueError('Historical artificial source drift '+name)
  if not n.startswith('.local/guard-reference-final-benchmark-'):raise ValueError('Unexpected historical benchmark folder')
  for child in sorted(p.rglob('*')):
   if child.is_file():add(child,'separate source-bound artificial engineering history; no accepted new numerical input claim')
 historical_root=ROOT/'research/guard-reference-preexecution-freeze-v1'
 if not historical_root.is_dir() or digest(historical_root/'manifest.json')!='5b13a157a50ed1174125c817a623627d2a34338e4926e08e6eac3f066d5641b3':raise ValueError('Withdrawn preexecution freeze history missing/drifted')
 old_manifest=jread('research/guard-reference-preexecution-freeze-v1/manifest.json')
 for name,h in old_manifest['sourceHashes'].items():
  if digest(historical_root/'sources'/name)!=h:raise ValueError('Withdrawn v1 frozen snapshot drift '+name)
 for child in sorted(historical_root.rglob('*')):
  if child.is_file():add(child,'withdrawn v1 source-only freeze; failed administrative schema check; no market execution occurred')
 delivery_history=ROOT/'.local/v13-delivery-attempt1'
 if not delivery_history.is_dir():raise ValueError('Failed delivery source/plan/log history missing')
 for child in sorted(delivery_history.rglob('*')):
  if child.is_file():add(child,'failed first delivery verification source/plan/log; no scientific mutation; temporary failed ZIP not nested')
 first_report=ROOT/'.local/v13-report-first-build'
 if not first_report.is_dir() or sum(p.stat().st_size for p in first_report.rglob('*') if p.is_file())>20_000_000:raise ValueError('Bounded first-report history missing/oversized')
 for child in sorted(first_report.rglob('*')):
  if child.is_file():add(child,'withdrawn first report candidate/source/checks; presentation history, not final accepted report')
 preservation=jread('.local/v13-working-preservation/receipt.json')
 if digest(ROOT/'.local/v13-working-preservation/receipt.json')!='e9ebfc6a134cbe6a0d10890d3a3b346129678cb48ac65da3ac25ce15ed443378' or not isinstance(preservation.get('files'),dict) or len(preservation['files'])!=8:raise ValueError('Working V12 preservation inventory differs')
 add('.local/v13-working-preservation/receipt.json','exact working V12 preservation before authorized navigation changes')
 for name,row in preservation['files'].items():
  add(row['backup'],'exact pre-integration working V12 copy; not an archive replacement')
  observed={k:row[k] for k in ['sha256','bytes']}
  if stream.digest_file(ROOT/row['backup'])!=observed or any(inherited[name][k]!=observed[k] for k in observed):raise ValueError('Working preservation differs from closed V12 '+name)
 routes=prior.prior.prior.prior.prior.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
 if PDF not in routes.values():raise ValueError('Current V13 report route missing')
 for url,name in routes.items():add(name,'closed current static route '+url)
 route_imports(sources,routes,add)
 for name,h in expected.items():
  if digest(ROOT/name)!=h:raise ValueError('Accepted source/input drift '+name)
 sources['README-v12.md']={'kind':'zip','archive':BASE,'member':'README.md'}
 sources['DELIVERY_FREEZE-v12.json']=sources.pop('DELIVERY_FREEZE.json')
 sources['START-HERE.txt']={'kind':'bytes','data':b'CURRENT REPORT: output/pdf/local-guard-welfare-report-v13.pdf\nStart: node research/demo-server.js and open http://127.0.0.1:3003/\nFull-grid reference view: /reference. This full archive contains12 new runs and24 complete checkpoints.\nIndependent full training replay is distinct from primary training; reproduction never retrains the learners.\nThe separate viewer omits numerical audit evidence. Author affiliation remains unsupplied.\n'}
 sources['STATIC_ROUTES.json']={'kind':'bytes','data':json_bytes(routes)}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-full-grid-reference-study','version':'13.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js','audit':'python -B research/audit-guard-reference-study.py --directory research/guard-reference-results','test':'node --test --test-isolation=none '+' '.join(node_tests)}})}
 inventory=stream.inventory(sources)
 for name in protected:
  if any(inventory[name][k]!=inherited[name][k] for k in ['sha256','bytes']):raise ValueError('Inherited protected byte mismatch '+name)
 if sum(r['bytes'] for r in inventory.values())>5_000_000_000:raise ValueError('Prospectively approved5GB delivery ceiling exceeded; no cases omitted')
 counts=suite_counts(node_tests,PY_TESTS,game_test)
 if counts['gameTestCount']!=game_test_count:raise ValueError('Explicit game-test count differs from final suite')
 config={'nodeTests':node_tests,'pythonTests':PY_TESTS,'harnesses':HARNESSES,'acceptedAuditSha256':AUDIT_SHA,'pythonExecutableSha256':PYTHON_SHA,'payloadCeilingBytes':5_000_000_000,**counts}
 return sources,inventory,routes,provenance,len(protected),config

def report_command(python):
 return [python,'-B',REPORT_BUILDER,'--audit-sha','a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6','--reference-audit-sha',AUDIT_SHA]

def report_check(directory,expected):
 try:from pypdf import PdfReader
 except ImportError:
  sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'));from pypdf import PdfReader
 p=directory/PDF;checks=json.loads((directory/'output/pdf/main-report-v13-checks.json').read_text());texts=[page.extract_text() for page in PdfReader(str(p)).pages]
 if digest(p)!=expected or checks['sha256']!=expected:raise ValueError('PDF differs from final actual-page review')
 body=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t));abstract=re.search(r'\bAbstract\.\s+(.*?)\n1 ',texts[0],re.S)
 if not abstract:raise ValueError('Actual abstract missing')
 words=len(abstract.group(1).split())
 if not(1<=body<=8 and 150<=words<=250 and words==checks['abstractWords'] and len(texts)==checks['pages'] and 'Mohammadpayam Teabi' in texts[0] and 'LLM usage and author contributions' in '\n'.join(texts) and 'Dual-Use / Ethical Considerations' in '\n'.join(texts)):raise ValueError('Actual PDF structure/disclosure invalid')
 return {'sha256':expected,'bytes':p.stat().st_size,'pages':len(texts),'bodyPages':body,'abstractWords':words,'affiliationSupplied':False}

def verify_full(archive,pdf_sha,config):
 require_pinned_python();node=shutil.which('node')
 if not node:raise RuntimeError('Node24+ required; no automatic installation')
 with base.verification_workspace() as target:
  milestone('Fresh extraction: every payload SHA and CRC')
  records=stream.extract_verified(archive,target)
  milestone('Artificial Node/Python suites')
  out=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*config['nodeTests']],target,timeout=600)
  if not re.search(r'^# tests '+str(config['expectedNode'])+'$',out,re.M) or not re.search(r'^# fail 0$',out,re.M):raise ValueError('Declared Node suites differ')
  code="import sys,unittest;s=unittest.TestSuite();[s.addTests(unittest.defaultTestLoader.discover('tests',p)) for p in "+repr(config['pythonTests'])+" ];r=unittest.TextTestRunner(stream=sys.stdout).run(s);sys.exit(not r.wasSuccessful())"
  out=base.execute([sys.executable,'-B','-c',code],target,timeout=900)
  if not re.search(r'Ran '+str(config['expectedPythonScientific']+config['expectedDelivery'])+r' tests?',out) or not re.search(r'^OK$',out,re.M):raise ValueError('Declared Python/delivery suites differ')
  base.execute([node,'research/guard-reference-study.js','verify',PREFIX.rstrip('/')],target,timeout=300)
  scratch=target/'.reproduce';scratch.mkdir()
  fresh=scratch/('independent-audit-'+uuid.uuid4().hex+'.json')
  # Authoritative audit independently replays24M rounds from zero. Never primary run.
  milestone('Authoritative independent full24M-round training replay; primary training is never called')
  base.execute([sys.executable,'-B','research/audit-guard-reference-study.py','--directory',PREFIX.rstrip('/'),'--output',str(fresh)],target,timeout=1800)
  audit=json.loads(fresh.read_text(encoding='utf-8'));accepted=json.loads((target/PREFIX/'independent-audit.json').read_text())
  stable=['passed','inventoryAccepted','independentAuditPassed','studyManifestHash','auditorSourceHash','controlAuditorSourceHash','replayCoreSourceHash','resultsSha256','indexSha256','completionSha256','journalSha256','executionStartSha256','stageAnchorsSha256','roundTranscriptBlocksMatched','primaryPassed','inheritedFinalEndpoints','acceptedOldComparison','anchors','runs','checkpointSlots','scientificallyAvailableCheckpoints','finalAvailable','replayedRounds','fullTrainingReplay','replayComplete','executionPassed','executionFailures','checkpointResults','finalEndpoints','independentSummaries','corruptionNegativeControls','scientificCorruptionNegativeControls','actualScientificNegativeControlsAvailable','finalSourceInputOutputIntegrityCheck','scientificNegativeControlScope']
  if not(audit.get('passed') is True and audit.get('runs')==12 and audit.get('checkpointSlots')==24 and audit.get('fullTrainingReplay') is True and audit.get('replayComplete') is True and audit.get('replayedRounds')==24_000_000 and audit.get('anchors',{}).get('available') is True and audit.get('anchors',{}).get('independentAgreement') is True):raise ValueError('Complete fresh24M replay failed')
  if any(audit[k]!=accepted[k] for k in stable):raise ValueError('Fresh scientific fields differ from accepted actual replay')
  milestone('Fresh24M replay accepted; deterministic derivatives and presentation checks')
  flags=['--audit',PREFIX+'independent-audit.json','--audit-sha',AUDIT_SHA]
  derived_dir=scratch/'derived'
  base.execute([sys.executable,'-B','research/build-guard-reference-web.py',*flags,'--output',str(derived_dir)],target,timeout=300)
  derived=['analysis.json','web-data.json','paired-results.csv','checkpoint-statuses.csv','stage-anchors.csv','endpoint-metrics.csv']
  if any(digest(derived_dir/name)!=records[PREFIX+name]['sha256'] for name in derived):raise ValueError('Exact descriptive/export byte mismatch')
  harnesses=[json.loads(base.execute([node,HARNESSES[0],'--audit-sha',AUDIT_SHA],target,timeout=900)),json.loads(base.execute([sys.executable,'-B',HARNESSES[1],*flags],target,timeout=900))]
  if not all(r['passed'] for r in harnesses):raise ValueError('Actual presentation/export checks failed')
  milestone('Exact scientific figure and distinct V13 report rebuild')
  figure_dir=scratch/'figures'
  base.execute([sys.executable,'-B','research/build-guard-reference-figure.py','--audit-sha',AUDIT_SHA,'--output',str(figure_dir)],target,timeout=300)
  figure_names=[n for n in records if n.startswith('research/guard-reference-figures/') and n.endswith(('.png','.svg','.json'))]
  if len([n for n in figure_names if n.endswith(('.png','.svg'))])!=2 or any(digest(figure_dir/Path(n).name)!=records[n]['sha256'] for n in figure_names):raise ValueError('New figure/receipt byte mismatch')
  base.execute(report_command(sys.executable),target,timeout=300)
  milestone('Current routes and final payload integrity')
  pdf=report_check(target,pdf_sha);routes=json.loads((target/'STATIC_ROUTES.json').read_text());http=base.http_smoke(target,routes,node)
  for name,row in records.items():
   if stream.digest_file(target/name)!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Verification mutated payload '+name)
  milestone('Deterministic repack and second fresh extraction')
  source=stream.extracted_sources(target,records);repacked=scratch/'full-repacked.zip';stream.zip_sources(repacked,source,stream.inventory(source))
  if digest(repacked)!=digest(archive):raise ValueError('Full fresh repack differs')
  second=scratch/'second-full';second.mkdir();stream.extract_verified(repacked,second)
  return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(records)+1,'tests':{'newScientific':config['expectedNode']+config['expectedPythonScientific'],'deliveryIntegrity':config['expectedDelivery'],'total':config['expectedTotal'],'failed':0},'independentAudit':audit,'freshAuditReceiptSeparate':True,'oldFullAuditsRerun':False,'oldPayloadPreservedByteExact':True,'fullTrainingReplay':True,'replayedTrainingRounds':24_000_000,'primaryRetrained':False,'summaryReportExportByteExact':True,'newFigurePairByteExact':True,'mainReport':pdf,'presentationChecks':harnesses,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'allPayloadsUnchanged':True,'freshRepackByteExact':True,'secondFreshExtractionVerified':True}

def full_plan(game_test_count):
 _,files,routes,_,protected,config=collect(game_test_count);value={'scope':'Prospective full V13 full-grid reference evidence preserving closed V12 bytes; no nested older ZIP, primary retraining or repeated full inherited audit','builderSourceHash':digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'scientificManifestSha256':STUDY_SHA,'acceptedAuditSha256':AUDIT_SHA,'primaryResourceAccounting':jread(PREFIX+'completion.json')['resources'],'payloadSizeScope':'Payload bytes count the actual stored canonical-gzip checkpoint files. The separate primary raw-equivalent and canonical-uncompressed counts do not describe ZIP member lengths.','files':files,'staticRoutes':len(routes),'protectedInheritedFiles':protected,'verificationConfiguration':config}
 write_json_exclusive(PLAN,value);print(json.dumps({'plan':PLAN.relative_to(ROOT).as_posix(),'sha256':digest(PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'staticRoutes':len(routes),'createsArchive':False}))

def full_build(pdf_sha):
 if FULL.exists():raise ValueError('Existing closed full archive preserved')
 frozen=jread(PLAN.relative_to(ROOT));config=frozen['verificationConfiguration'];game_count=config['gameTestCount']
 source,files,routes,provenance,protected,current=collect(game_count)
 if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['baseArchiveSha256']!=BASE_SHA or frozen['files']!=files or current!=config or files[PDF]['sha256']!=pdf_sha:raise ValueError('Prospective inventory/reviewed PDF changed')
 if shutil.disk_usage(ROOT).free<4*sum(r['bytes'] for r in files.values())+256_000_000:raise ValueError('Insufficient verification disk; no evidence omitted')
 began=time.perf_counter();source['DELIVERY_FREEZE.json']={'kind':'file','path':PLAN};files['DELIVERY_FREEZE.json']=stream.digest_file(PLAN)
 contents={'scope':'Full accepted V13 full-grid-after-cap reference evidence and immutable inherited V12 data. The new12 training runs receive full independent same-runtime replay; old full audit reruns are not claimed.','baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':digest(PLAN),'files':{n:{**r,'provenance':sorted(provenance.get(n,{'closed V12 payload or generated navigation'}))} for n,r in files.items()}}
 source['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};files['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(source['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(source['PACKAGE_CONTENTS.json']['data'])}
 milestone('Building streamed full evidence archive from the frozen inventory')
 temporary=FULL.with_name(FULL.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,source,files);checks=verify_full(temporary,pdf_sha,config)
 if FULL.exists():raise ValueError('Delivery path appeared during verification')
 temporary.rename(FULL);receipt={'archive':FULL.relative_to(ROOT).as_posix(),'sha256':digest(FULL),'bytes':FULL.stat().st_size,'prospectiveInventorySha256':digest(PLAN),'builderSourceHash':digest(Path(__file__)),'seconds':time.perf_counter()-began,'baseArchiveSha256':BASE_SHA,'protectedInheritedFiles':protected,'verification':checks};write_json_exclusive(RECEIPT,receipt)
 (ROOT/'research/GUARD_REFERENCE_PACKAGE_VERIFICATION.md').write_text('# Full-grid reference delivery verification\n\n'+f"Archive `{receipt['archive']}`; SHA256 `{receipt['sha256']}`.\n\n"+'Fresh extraction passed the complete new24M-round independent training replay in a separate receipt, declared tests, exact derived/web/new-figure/report builds, portable developer checks, all static routes, every payload SHA/CRC and identical repack plus second extraction. Byte-identical inherited evidence was preserved. New12-run training was fully independently replayed from zero; inherited full audits and old optimizer iterations were not repeated. The separate viewer cannot reproduce omitted numerical inputs. Author affiliation remains unsupplied; no external submission occurred.\n',encoding='utf-8')
 print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))

def viewer_sources():
 receipt=jread(RECEIPT.relative_to(ROOT))
 if receipt['verification']['passed'] is not True or digest(FULL)!=receipt['sha256']:raise ValueError('Final verified full archive required first')
 with zipfile.ZipFile(FULL) as z:contents=json.loads(z.read('PACKAGE_CONTENTS.json'));routes=json.loads(z.read('STATIC_ROUTES.json'))
 sources={};provenance={}
 def add(name,reason):
  if name not in contents['files']:raise ValueError('Viewer source absent from full archive '+name)
  sources[name]={'kind':'zip','archive':FULL,'member':name};provenance[name]=reason;return name
 for name in set(routes.values())|{'research/demo-server.js','STATIC_ROUTES.json'}:add(name,'exact full-archive route/runtime copy')
 def import_add(name,reason):
  _,relative=local(name);return add(relative,reason)
 route_imports(sources,routes,import_add)
 pointer={'scope':'Viewer only; omitted raw evidence and checkpoints cannot be audited from this archive','fullEvidenceArchive':receipt['archive'],'fullEvidenceSha256':receipt['sha256'],'fullEvidenceBytes':receipt['bytes'],'fullVerificationReceiptSha256':digest(RECEIPT),'scientificResultsChanged':False}
 sources['FULL_EVIDENCE_POINTER.json']={'kind':'bytes','data':json_bytes(pointer)}
 sources['README.md']={'kind':'bytes','data':('# Viewer only\n\nStart `node research/demo-server.js`, then open http://127.0.0.1:3003/ or /reference. Node24+ is required; no installation, API key or paid service is needed.\n\nThe current report and routed displays are exact full-archive copies. Raw numerical records, large learner checkpoints and audit dependencies are omitted; this viewer cannot reproduce the numerical audits. Use the separate full evidence archive.\n\nFull evidence: `'+pointer['fullEvidenceArchive']+'`\n\nSHA256: `'+pointer['fullEvidenceSha256']+'`\n\nSee FULL_EVIDENCE_POINTER.json. Neither archive nests the other. Author affiliation remains unsupplied. Developer QA is not human validation; no external submission is implied.\n').encode()}
 sources['START-HERE.txt']={'kind':'bytes','data':b'VIEWER ONLY: node research/demo-server.js\nOpen http://127.0.0.1:3003/ or /reference\nRead README.md and FULL_EVIDENCE_POINTER.json. Complete numerical reproduction requires the full archive.\n'}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-viewer','version':'13.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js'}})}
 return sources,stream.inventory(sources),routes,pointer,provenance

def viewer_plan():
 _,files,routes,pointer,_=viewer_sources();value={'scope':'Prospective exact runtime/route subset of final full evidence','builderSourceHash':digest(Path(__file__)),'fullEvidence':pointer,'files':files,'staticRoutes':len(routes)};write_json_exclusive(VIEW_PLAN,value);print(json.dumps({'plan':VIEW_PLAN.relative_to(ROOT).as_posix(),'sha256':digest(VIEW_PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'createsArchive':False}))

def viewer_build():
 if VIEW.exists():raise ValueError('Existing viewer preserved')
 source,files,routes,pointer,provenance=viewer_sources();frozen=jread(VIEW_PLAN.relative_to(ROOT))
 if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['files']!=files or frozen['fullEvidence']!=pointer:raise ValueError('Viewer prospective inventory changed')
 source['DELIVERY_FREEZE.json']={'kind':'file','path':VIEW_PLAN};files['DELIVERY_FREEZE.json']=stream.digest_file(VIEW_PLAN)
 contents={'scope':'Viewer only; numerical reproduction needs the separately hash-bound full evidence','fullEvidence':pointer,'files':{n:{**r,'provenance':provenance.get(n,'generated viewer instructions/provenance')} for n,r in files.items()}}
 source['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};files['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(source['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(source['PACKAGE_CONTENTS.json']['data'])}
 temporary=VIEW.with_name(VIEW.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,source,files)
 with base.verification_workspace() as target:
  records=stream.extract_verified(temporary,target);http=base.http_smoke(target,routes,shutil.which('node'))
  for name,row in records.items():
   if stream.digest_file(target/name)!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Viewer runtime mutated payload '+name)
  scratch=target/'.repack';scratch.mkdir();fresh=stream.extracted_sources(target,records);repacked=scratch/'viewer.zip';stream.zip_sources(repacked,fresh,stream.inventory(fresh))
  if digest(repacked)!=digest(temporary):raise ValueError('Viewer repack differs')
  second=scratch/'second';second.mkdir();stream.extract_verified(repacked,second)
 if VIEW.exists():raise ValueError('Viewer appeared during verification')
 temporary.rename(VIEW);value={'archive':VIEW.relative_to(ROOT).as_posix(),'sha256':digest(VIEW),'bytes':VIEW.stat().st_size,'payloadFiles':len(files),'prospectiveInventorySha256':digest(VIEW_PLAN),'fullEvidence':pointer,'verification':{'passed':True,'scope':'Viewer byte/runtime checks, not numerical audit reproduction','payloadHashesAndCRC':True,'allRuntimeDependenciesFromFullArchive':True,'fullEvidenceHashBound':True,'nestedFullArchive':False,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'freshRepackByteExact':True,'secondFreshExtractionVerified':True}}
 write_json_exclusive(VIEW_RECEIPT,value);print(json.dumps({k:value[k] for k in ['archive','bytes','sha256','payloadFiles']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);a=sub.add_parser('plan');a.add_argument('--game-test-count',type=int,required=True);b=sub.add_parser('build');b.add_argument('--final-freeze-report-sha',required=True);sub.add_parser('viewer-plan');sub.add_parser('viewer-build');args=p.parse_args()
 if args.mode=='plan':full_plan(args.game_test_count)
 elif args.mode=='build':full_build(args.final_freeze_report_sha)
 elif args.mode=='viewer-plan':viewer_plan()
 else:viewer_build()
