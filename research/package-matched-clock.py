"""Prospective streaming V12 delivery. Never reruns primary training.

Fresh verification independently replays all24 new training trajectories from
zero. A later viewer points to the final full archive without nesting it.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,sys,time,uuid,zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('closed_v11_packager',ROOT/'research/package-learned-opponent.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
stream,base,json_bytes=prior.stream,prior.base,prior.json_bytes
BASE=ROOT/'output/price-guard-learned-opponents-v11.zip'
BASE_SHA='7544aab654822b5444f966b24ea8e985d973e04562422ff9d1c26bc44b9c9885'
STUDY_SHA='dcd573fc866e59cd1a27c3158cb9e9be58702034f9fb250e251c54f579a01817'
AUDIT_SHA='a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6'
BENCHMARK_SHA='cf6cf927ae4f6619a9e11432fa36d93277211b1b44707305903c8fe99b9619dd'
PYTHON_SHA='62ebc90a2884bb63a0cd67e789cafdd51e771eee043587e2354327b4ccc9bb05'
FULL=ROOT/'output/price-guard-matched-clock-v12.zip'
PLAN=ROOT/'output/matched-clock-package-plan.json'
RECEIPT=ROOT/'output/matched-clock-package-verification.json'
VIEW=ROOT/'output/price-guard-viewer-v12.zip'
VIEW_PLAN=ROOT/'output/viewer-v12-package-plan.json'
VIEW_RECEIPT=ROOT/'output/viewer-v12-package-verification.json'
PDF='output/pdf/local-guard-welfare-report-v12.pdf'
REPORT_BUILDER='research/build-main-report-v12.py'
PREFIX='research/matched-clock-results/'
NODE_TESTS=['tests/matched-clock-learning.test.js','tests/matched-clock-graph.test.js','tests/matched-clock-io.test.js','tests/matched-clock-study.test.js','tests/matched-clock-audit.test.js','tests/matched-clock-root-cross.test.js','tests/matched-clock-cross-audit.test.js','tests/matched-clock-serialization-audit.test.js','tests/matched-clock-game.test.js','tests/matched-view.test.js']
PY_TESTS=['test_matched_clock_supervisor.py','test_matched_clock_benchmark.py','test_matched_clock_analysis.py','test_matched_clock_inventory_audit.py','test_matched_clock_export.py','test_evidence_streaming.py']
HARNESSES=['.local/matched-clock-display-smoke.mjs','.local/matched-clock-export-smoke.py']
SCRIPTS=['build-matched-clock-web.py','build-matched-clock-figure.py','package-matched-clock.py','build-main-report-v12.py','matched-clock-game.js','demo-server.js']
DOCS=['MATCHED_CLOCK_RESULTS.md','MATCHED_CLOCK_REVIEW.md','MATCHED_CLOCK_REPLAY_QA.md','MATCHED_CLOCK_WEB_SCHEMA.md','README.md']
ADMIN=['.local/matched-clock-administrative-preflight.json','.local/matched-clock-administrative-preflight-v2.json','.local/matched-clock-root-artificial-gate.json','.local/matched-clock-independent-benchmark-gate.json','.local/matched-clock-root-freeze-check.json','.local/matched-clock-independent-admin-gate.json','.local/matched-clock-numerical-go.json','.local/check-matched-benchmark-independent.py','.local/matched-prefix-render-before-fix.js']
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
 print('[V12 delivery] '+message,file=sys.stderr,flush=True)

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
 node_total=node_count(node_tests);game_count=node_count([game_test]);delivery=python_counts['test_evidence_streaming.py'];scientific=sum(python_counts.values())-delivery
 return {'expectedNode':node_total,'expectedPythonScientific':scientific,'expectedDelivery':delivery,'expectedTotal':node_total+scientific+delivery,'gameTestCount':game_count,'pythonSuiteCounts':python_counts,'testDiscoveryScope':'Reviewed Node unit suites execute to count actual passing cases; Python unittest loader counts. All specified suites execute again in fresh verification. No primary training or new market training is invoked.'}

def collect(game_test_count):
 require_pinned_python()
 if digest(BASE)!=BASE_SHA:raise ValueError('Closed V11 archive changed')
 audit=jread(PREFIX+'independent-audit.json')
 if digest(ROOT/(PREFIX+'independent-audit.json'))!=AUDIT_SHA or not(audit.get('passed') is True and audit.get('runs')==24 and audit.get('checkpointSlots')==48 and audit.get('finalSourceInputOutputIntegrityCheck') is True):raise ValueError('Complete authoritative matched-clock acceptance required')
 if digest(ROOT/(PREFIX+'manifest.json'))!=STUDY_SHA:raise ValueError('Accepted scientific manifest changed')
 with zipfile.ZipFile(BASE) as z:
  names=z.namelist();inherited=json.loads(z.read('PACKAGE_CONTENTS.json'))['files']
  if len(names)!=len(set(names)) or set(names)!=set(inherited)|{'PACKAGE_CONTENTS.json'} or any(not stream.safe_name(n) for n in names):raise ValueError('Unsafe/unmanifested V11 inventory')
 sources={n:{'kind':'zip','archive':BASE,'member':n} for n in inherited}
 mutable={'README.md','research/README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','DELIVERY_FREEZE.json','research/demo-server.js','research/demo/overview.html','research/demo/overview.css','research/demo/overview.js'}
 protected=set(sources)-mutable;provenance={};expected={}
 def add(name,reason):
  p,n=local(name)
  if any(word in n for word in ['private-pilot','codex-adapter']) or 'CANDIDATE' in n and n not in inherited:raise ValueError('Unrequested private/future candidate '+n)
  observed=stream.digest_file(p)
  if n in protected and any(observed[k]!=inherited[n][k] for k in ['sha256','bytes']):raise ValueError('Protected V11 byte changed '+n)
  sources[n]={'kind':'file','path':p};provenance.setdefault(n,set()).add(reason);return n
 for name in SCRIPTS:add('research/'+name,'accepted V12 derivation/report/delivery source')
 for name in DOCS:add('research/'+name,'accepted current narrative/review/presentation scope')
 node_tests=NODE_TESTS.copy();game_test='tests/matched-clock-game.test.js'
 for name in node_tests+['tests/'+p for p in PY_TESTS]+HARNESSES+['tests/helpers/matched-clock-web-fixture.js']:add(name,'targeted artificial or read-only actual verification')
 for folder in ['research/matched-clock-results','research/matched-clock-figures']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file():add(p,'complete accepted new raw/derived evidence or figure')
 for name in ['local-guard-welfare-report-v12.pdf','local-guard-welfare-report-v12.txt','main-report-v12-checks.json']:add('output/pdf/'+name,'distinct accepted V12 report')
 for name in ['README.md','output/learned-opponent-package-verification.json',*ADMIN]:add(name,'current entry or administrative provenance')
 m=jread(PREFIX+'manifest.json')
 for group in ['sourceHashes','inputHashes']:
  for name,h in m[group].items():
   expected[add(name,'frozen manifest / exact '+group)]=h
   if group=='sourceHashes':expected[add(PREFIX+'sources/'+name,'frozen primary source snapshot')]=h
 start=jread(PREFIX+'execution-start.json');admin=start['adminGate']
 expected[add(admin['file'],'post-freeze independently accepted administrative receipt')]=admin['sha256']
 if stream.digest_file(ROOT/admin['file'])!={k:admin[k] for k in ['sha256','bytes']}:raise ValueError('Actual admin receipt reference drift')
 if digest(ROOT/'.local/matched-clock-benchmark.json')!=BENCHMARK_SHA:raise ValueError('Final source-bound artificial benchmark changed')
 # These bounded engineering logs/receipts are history, not extra market runs.
 for p in sorted((ROOT/'.local').glob('matched-clock-*')):
  if p.is_file() and p.suffix in {'.json','.txt','.py','.mjs','.png'}:
   if p.stat().st_size>25_000_000:raise ValueError('Review oversized engineering history before delivery '+p.name)
   add(p,'explicit matched-stage engineering/developer history; not new scientific cases')
 preservation=jread('.local/v12-working-preservation/receipt.json')
 if preservation.get('v11ArchiveSha256')!=BASE_SHA or len(preservation.get('files',[]))!=8:raise ValueError('Working V11 preservation inventory differs')
 add('.local/v12-working-preservation/receipt.json','exact working V11 preservation before authorized navigation changes')
 for row in preservation['files']:
  add(row['copy'],'exact pre-integration working V11 copy; not an archive replacement')
  if stream.digest_file(ROOT/row['copy'])!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Working preservation drift '+row['copy'])
 routes=prior.prior.prior.prior.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
 if PDF not in routes.values():raise ValueError('Current V12 report route missing')
 for url,name in routes.items():add(name,'closed current static route '+url)
 route_imports(sources,routes,add)
 for name,h in expected.items():
  if digest(ROOT/name)!=h:raise ValueError('Accepted source/input drift '+name)
 sources['README-v11.md']={'kind':'zip','archive':BASE,'member':'README.md'}
 sources['DELIVERY_FREEZE-v11.json']=sources.pop('DELIVERY_FREEZE.json')
 sources['START-HERE.txt']={'kind':'bytes','data':b'CURRENT REPORT: output/pdf/local-guard-welfare-report-v12.pdf\nStart: node research/demo-server.js and open http://127.0.0.1:3003/\nMatched-clock learner view: /matched. This full archive contains24 new runs and48 complete checkpoints.\nIndependent full training replay is distinct from primary training; reproduction never retrains the learners.\nThe separate viewer omits numerical audit evidence. Author affiliation remains unsupplied.\n'}
 sources['STATIC_ROUTES.json']={'kind':'bytes','data':json_bytes(routes)}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-matched-clock-study','version':'12.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js','audit':'python -B research/audit-matched-clock-study.py --directory research/matched-clock-results','test':'node --test --test-isolation=none '+' '.join(node_tests)}})}
 inventory=stream.inventory(sources)
 for name in protected:
  if any(inventory[name][k]!=inherited[name][k] for k in ['sha256','bytes']):raise ValueError('Inherited protected byte mismatch '+name)
 if sum(r['bytes'] for r in inventory.values())>5_000_000_000:raise ValueError('Prospectively approved5GB delivery ceiling exceeded; no cases omitted')
 counts=suite_counts(node_tests,PY_TESTS,game_test)
 if counts['gameTestCount']!=game_test_count:raise ValueError('Explicit game-test count differs from final suite')
 config={'nodeTests':node_tests,'pythonTests':PY_TESTS,'harnesses':HARNESSES,'acceptedAuditSha256':AUDIT_SHA,'pythonExecutableSha256':PYTHON_SHA,'payloadCeilingBytes':5_000_000_000,**counts}
 return sources,inventory,routes,provenance,len(protected),config

def report_check(directory,expected):
 try:from pypdf import PdfReader
 except ImportError:
  sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'));from pypdf import PdfReader
 p=directory/PDF;checks=json.loads((directory/'output/pdf/main-report-v12-checks.json').read_text());texts=[page.extract_text() for page in PdfReader(str(p)).pages]
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
  base.execute([node,'research/matched-clock-study.js','verify',PREFIX.rstrip('/')],target,timeout=300)
  scratch=target/'.reproduce';scratch.mkdir()
  fresh=scratch/('independent-audit-'+uuid.uuid4().hex+'.json')
  # Authoritative audit independently replays48M rounds from zero. Never primary run.
  milestone('Authoritative independent full48M-round training replay; primary training is never called')
  base.execute([sys.executable,'-B','research/audit-matched-clock-study.py','--directory',PREFIX.rstrip('/'),'--output',str(fresh)],target,timeout=1800)
  audit=json.loads(fresh.read_text(encoding='utf-8'));accepted=json.loads((target/PREFIX/'independent-audit.json').read_text())
  stable=['passed','inventoryAccepted','independentAuditPassed','studyManifestHash','auditorSourceHash','controlAuditorSourceHash','replayCoreSourceHash','resultsSha256','indexSha256','completionSha256','journalSha256','executionStartSha256','runs','checkpointSlots','scientificallyAvailableCheckpoints','finalAvailable','replayedRounds','fullTrainingReplay','replayComplete','executionPassed','executionFailures','checkpointResults','finalEndpoints','independentSummaries','corruptionNegativeControls','scientificCorruptionNegativeControls','actualScientificNegativeControlsAvailable','finalSourceInputOutputIntegrityCheck','scientificNegativeControlScope']
  if not(audit.get('passed') is True and audit.get('runs')==24 and audit.get('checkpointSlots')==48 and audit.get('fullTrainingReplay') is True and audit.get('replayComplete') is True and audit.get('replayedRounds')==48_000_000):raise ValueError('Complete fresh48M replay failed')
  if any(audit[k]!=accepted[k] for k in stable):raise ValueError('Fresh scientific fields differ from accepted actual replay')
  milestone('Fresh48M replay accepted; deterministic derivatives and presentation checks')
  flags=['--audit',PREFIX+'independent-audit.json','--audit-sha',AUDIT_SHA]
  derived_dir=scratch/'derived'
  base.execute([sys.executable,'-B','research/build-matched-clock-web.py',*flags,'--output',str(derived_dir)],target,timeout=300)
  derived=['analysis.json','web-data.json','paired-results.csv','checkpoint-statuses.csv']
  if any(digest(derived_dir/name)!=records[PREFIX+name]['sha256'] for name in derived):raise ValueError('Exact descriptive/export byte mismatch')
  harnesses=[json.loads(base.execute([node,HARNESSES[0],'--audit-sha',AUDIT_SHA],target,timeout=900)),json.loads(base.execute([sys.executable,'-B',HARNESSES[1],*flags],target,timeout=900))]
  if not all(r['passed'] for r in harnesses):raise ValueError('Actual presentation/export checks failed')
  milestone('Exact scientific figure and distinct V12 report rebuild')
  base.execute([sys.executable,'-B','research/build-matched-clock-figure.py','--audit-sha',AUDIT_SHA],target,timeout=300)
  figure_names=[n for n in records if n.startswith('research/matched-clock-figures/') and n.endswith(('.png','.svg','.json'))]
  if len([n for n in figure_names if n.endswith(('.png','.svg'))])!=2 or any(digest(target/n)!=records[n]['sha256'] for n in figure_names):raise ValueError('New figure/receipt byte mismatch')
  base.execute([sys.executable,'-B',REPORT_BUILDER,'--audit-sha',AUDIT_SHA],target,timeout=300)
  milestone('Current routes and final payload integrity')
  pdf=report_check(target,pdf_sha);routes=json.loads((target/'STATIC_ROUTES.json').read_text());http=base.http_smoke(target,routes,node)
  for name,row in records.items():
   if stream.digest_file(target/name)!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Verification mutated payload '+name)
  milestone('Deterministic repack and second fresh extraction')
  source=stream.extracted_sources(target,records);repacked=scratch/'full-repacked.zip';stream.zip_sources(repacked,source,stream.inventory(source))
  if digest(repacked)!=digest(archive):raise ValueError('Full fresh repack differs')
  second=scratch/'second-full';second.mkdir();stream.extract_verified(repacked,second)
  return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(records)+1,'tests':{'newScientific':config['expectedNode']+config['expectedPythonScientific'],'deliveryIntegrity':config['expectedDelivery'],'total':config['expectedTotal'],'failed':0},'independentAudit':audit,'freshAuditReceiptSeparate':True,'oldFullAuditsRerun':False,'oldPayloadPreservedByteExact':True,'fullTrainingReplay':True,'replayedTrainingRounds':48_000_000,'primaryRetrained':False,'summaryReportExportByteExact':True,'newFigurePairByteExact':True,'mainReport':pdf,'presentationChecks':harnesses,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'allPayloadsUnchanged':True,'freshRepackByteExact':True,'secondFreshExtractionVerified':True}

def full_plan(game_test_count):
 _,files,routes,_,protected,config=collect(game_test_count);value={'scope':'Prospective full V12 matched-clock training evidence preserving closed V11 bytes; no nested older ZIP, primary retraining or repeated full inherited audit','builderSourceHash':digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'scientificManifestSha256':STUDY_SHA,'acceptedAuditSha256':AUDIT_SHA,'primaryResourceAccounting':jread(PREFIX+'completion.json')['resources'],'payloadSizeScope':'Payload bytes count the actual stored canonical-gzip checkpoint files. The separate primary raw-equivalent and canonical-uncompressed counts do not describe ZIP member lengths.','files':files,'staticRoutes':len(routes),'protectedInheritedFiles':protected,'verificationConfiguration':config}
 write_json_exclusive(PLAN,value);print(json.dumps({'plan':PLAN.relative_to(ROOT).as_posix(),'sha256':digest(PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'staticRoutes':len(routes),'createsArchive':False}))

def full_build(pdf_sha):
 if FULL.exists():raise ValueError('Existing closed full archive preserved')
 frozen=jread(PLAN.relative_to(ROOT));config=frozen['verificationConfiguration'];game_count=config['gameTestCount']
 source,files,routes,provenance,protected,current=collect(game_count)
 if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['baseArchiveSha256']!=BASE_SHA or frozen['files']!=files or current!=config or files[PDF]['sha256']!=pdf_sha:raise ValueError('Prospective inventory/reviewed PDF changed')
 if shutil.disk_usage(ROOT).free<4*sum(r['bytes'] for r in files.values())+256_000_000:raise ValueError('Insufficient verification disk; no evidence omitted')
 began=time.perf_counter();source['DELIVERY_FREEZE.json']={'kind':'file','path':PLAN};files['DELIVERY_FREEZE.json']=stream.digest_file(PLAN)
 contents={'scope':'Full accepted V12 matched-clock training evidence and immutable inherited V11 data. The new24 training runs receive full independent same-runtime replay; old full audit reruns are not claimed.','baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':digest(PLAN),'files':{n:{**r,'provenance':sorted(provenance.get(n,{'closed V11 payload or generated navigation'}))} for n,r in files.items()}}
 source['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};files['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(source['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(source['PACKAGE_CONTENTS.json']['data'])}
 milestone('Building streamed full evidence archive from the frozen inventory')
 temporary=FULL.with_name(FULL.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,source,files);checks=verify_full(temporary,pdf_sha,config)
 if FULL.exists():raise ValueError('Delivery path appeared during verification')
 temporary.rename(FULL);receipt={'archive':FULL.relative_to(ROOT).as_posix(),'sha256':digest(FULL),'bytes':FULL.stat().st_size,'prospectiveInventorySha256':digest(PLAN),'builderSourceHash':digest(Path(__file__)),'seconds':time.perf_counter()-began,'baseArchiveSha256':BASE_SHA,'protectedInheritedFiles':protected,'verification':checks};write_json_exclusive(RECEIPT,receipt)
 (ROOT/'research/MATCHED_CLOCK_PACKAGE_VERIFICATION.md').write_text('# Full matched-clock delivery verification\n\n'+f"Archive `{receipt['archive']}`; SHA256 `{receipt['sha256']}`.\n\n"+'Fresh extraction passed the complete new48M-round independent training replay in a separate receipt, declared tests, exact derived/web/new-figure/report builds, portable developer checks, all static routes, every payload SHA/CRC and identical repack plus second extraction. Byte-identical inherited evidence was preserved. New24-run training was fully independently replayed from zero; inherited full audits and old optimizer iterations were not repeated. The separate viewer cannot reproduce omitted numerical inputs. Author affiliation remains unsupplied; no external submission occurred.\n',encoding='utf-8')
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
 sources['README.md']={'kind':'bytes','data':('# Viewer only\n\nStart `node research/demo-server.js`, then open http://127.0.0.1:3003/ or /matched. Node24+ is required; no installation, API key or paid service is needed.\n\nThe current report and routed displays are exact full-archive copies. Raw numerical records, large learner checkpoints and audit dependencies are omitted; this viewer cannot reproduce the numerical audits. Use the separate full evidence archive.\n\nFull evidence: `'+pointer['fullEvidenceArchive']+'`\n\nSHA256: `'+pointer['fullEvidenceSha256']+'`\n\nSee FULL_EVIDENCE_POINTER.json. Neither archive nests the other. Author affiliation remains unsupplied. Developer QA is not human validation; no external submission is implied.\n').encode()}
 sources['START-HERE.txt']={'kind':'bytes','data':b'VIEWER ONLY: node research/demo-server.js\nOpen http://127.0.0.1:3003/ or /matched\nRead README.md and FULL_EVIDENCE_POINTER.json. Complete numerical reproduction requires the full archive.\n'}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-viewer','version':'12.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js'}})}
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
