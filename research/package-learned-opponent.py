"""Prospective V11 delivery. Never executes the primary response optimizer.

Full evidence inherits closed V10 bytes, adds the accepted48-label study and
reruns its independent auditor. A later viewer points to the final full hash.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,sys,time,uuid,zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('closed_v10_packager',ROOT/'research/package-mixed-timing.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
stream,base,json_bytes=prior.stream,prior.base,prior.json_bytes
BASE=ROOT/'output/price-guard-mixed-timing-v10.zip'
BASE_SHA='5b494614af0efabe6a416814604a4914fb8e5492d6d78fb106d5a09b8497bdcf'
STUDY_SHA='e1843c954dde7cc3b9d349d6664c0431fcf97839393517f3967004671bddd8d5'
BENCHMARK_SHA='9391c2b53998e7ea75f91ebbb519c228610f20f8efdb641b8be8befd631eb20b'
FULL=ROOT/'output/price-guard-learned-opponents-v11.zip'
PLAN=ROOT/'output/learned-opponent-package-plan.json'
RECEIPT=ROOT/'output/learned-opponent-package-verification.json'
VIEW=ROOT/'output/price-guard-viewer-v11.zip'
VIEW_PLAN=ROOT/'output/viewer-v11-package-plan.json'
VIEW_RECEIPT=ROOT/'output/viewer-v11-package-verification.json'
PDF='output/pdf/local-guard-welfare-report-v11.pdf'
REPORT_BUILDER='research/build-main-report-v11.py'
PREFIX='research/learned-opponent-results/'
NODE_TESTS=['tests/learned-opponent-study.test.js','tests/learned-opponent-format.test.js','tests/learned-opponent-analysis.test.js','tests/learned-opponent-evidence.test.js','tests/learned-opponent-web-game.test.js','tests/learned-opponent-gate.test.js']
PY_TESTS=['test_learned_opponent_supervisor.py','test_learned_opponent_audit.py','test_learned_opponent_cross_audit.py','test_learned_opponent_inventory_audit.py','test_evidence_streaming.py']
HARNESSES=['.local/learned-opponent-display-smoke.mjs','.local/learned-opponent-export-smoke.mjs']
SCRIPTS=['learned-opponent-analysis.js','learned-opponent-format.js','learned-opponent-evidence.js','learned-opponent-web-game.js','build-learned-opponent-web.js','build-learned-opponent-figure.py','package-learned-opponent.py','build-main-report-v11.py','demo-server.js']
DOCS=['LEARNED_OPPONENT_RESULTS.md','LEARNED_OPPONENT_REVIEW.md','LEARNED_OPPONENT_REPLAY_QA.md','LEARNED_OPPONENT_PLAY_BRIEF.md','LEARNED_OPPONENT_REPORT_PLAN.md','README.md']
ADMIN=['.local/learned-opponent-administrative-preflight.json','.local/learned-opponent-root-freeze-check.json','.local/learned-opponent-independent-admin-gate.json']
digest=lambda p:stream.digest_file(p)['sha256']
local=prior.local
jread=prior.jread
def route_imports(sources,routes,add):
 # Historical source copies are evidence, not runnable relative import roots.
 inert=('.local/learned-worker-termination-history/','.local/v11-working-preservation/')
 runnable={n:s for n,s in sources.items() if not n.startswith(inert)}
 def include(name,reason):
  n=add(name,reason);runnable[n]=sources[n];return n
 return prior.route_imports(runnable,routes,include)

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
 return {'expectedNode':node_total,'expectedPythonScientific':scientific,'expectedDelivery':delivery,'expectedTotal':node_total+scientific+delivery,'gameTestCount':game_count,'pythonSuiteCounts':python_counts,'testDiscoveryScope':'Reviewed Node unit suites execute to count actual passing cases; Python unittest loader counts. All specified suites execute again in fresh verification. No primary response optimization or new market training is invoked.'}

def collect(game_test_count):
 if digest(BASE)!=BASE_SHA:raise ValueError('Closed V10 archive changed')
 audit=jread(PREFIX+'independent-audit.json')
 if not(audit.get('passed') is True and audit.get('labels')==48 and audit.get('allPlannedLabelsRetained') is True):raise ValueError('Full48 independent acceptance required')
 if digest(ROOT/(PREFIX+'manifest.json'))!=STUDY_SHA:raise ValueError('Accepted scientific manifest changed')
 with zipfile.ZipFile(BASE) as z:
  names=z.namelist();inherited=json.loads(z.read('PACKAGE_CONTENTS.json'))['files']
  if len(names)!=len(set(names)) or set(names)!=set(inherited)|{'PACKAGE_CONTENTS.json'} or any(not stream.safe_name(n) for n in names):raise ValueError('Unsafe/unmanifested V10 inventory')
 sources={n:{'kind':'zip','archive':BASE,'member':n} for n in inherited}
 mutable={'README.md','research/README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','DELIVERY_FREEZE.json','research/demo-server.js','research/demo/overview.html','research/demo/overview.css','research/demo/overview.js'}
 protected=set(sources)-mutable;provenance={};expected={}
 def add(name,reason):
  p,n=local(name)
  if any(word in n for word in ['private-pilot','codex-adapter']) or 'CANDIDATE' in n and n not in inherited:raise ValueError('Unrequested private/future candidate '+n)
  observed=stream.digest_file(p)
  if n in protected and any(observed[k]!=inherited[n][k] for k in ['sha256','bytes']):raise ValueError('Protected V10 byte changed '+n)
  sources[n]={'kind':'file','path':p};provenance.setdefault(n,set()).add(reason);return n
 for name in SCRIPTS:add('research/'+name,'accepted V11 derivation/report/delivery source')
 for name in DOCS:add('research/'+name,'accepted current narrative/review/presentation scope')
 node_tests=NODE_TESTS.copy();game_test='tests/learned-opponent-game.test.js'
 if not(ROOT/game_test).exists() or game_test_count<=0:raise ValueError('Final explicit actual continuation-game test count required')
 node_tests.extend([game_test,'tests/opponent-view.test.js'])
 for name in node_tests+['tests/'+p for p in PY_TESTS]+HARNESSES:add(name,'targeted artificial or read-only actual verification')
 for folder in ['research/learned-opponent-results','research/learned-opponent-figures']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file():add(p,'complete new raw/derived accepted evidence or figure')
 for name in ['local-guard-welfare-report-v11.pdf','local-guard-welfare-report-v11.txt','main-report-v11-checks.json']:add('output/pdf/'+name,'distinct accepted V11 report')
 for name in ['README.md','output/mixed-timing-package-verification.json',*ADMIN]:add(name,'current entry or pre-outcome administrative provenance')
 # Every frozen input is explicit, including mandatory synthetic benchmark data.
 for mname in [PREFIX+'manifest.json',PREFIX+'summary.json']:
  value=jread(mname)
  for group in ['sourceHashes','inputHashes']:
   for name,h in value.get(group,{}).items():
    expected[add(name,mname+' / exact '+group)]=h
    if group=='sourceHashes':expected[add(PREFIX+'sources/'+name,'frozen primary source snapshot')]=h
 if digest(ROOT/'.local/learned-process-benchmark-final-v2.json')!=BENCHMARK_SHA:raise ValueError('Source-bound final pre-outcome benchmark changed')
 # Engineering history is explicitly labelled, bounded, and not new evidence.
 history=['.local/learned-worker-termination-history','.local/learned-process-benchmark-v1-history']
 for receipt_name in ['.local/learned-process-benchmark.json','.local/learned-process-benchmark-final.json','.local/learned-process-benchmark-final-v2.json']:
  add(receipt_name,'historical artificial engineering benchmark; not a numerical case')
  value=jread(receipt_name);history.append(value['directory'])
 for name in ['.local/learned-process-benchmark-final.py','.local/learned-process-benchmark-final-v2.py']:add(name,'historical source-bound artificial benchmark producer')
 for folder in history:
  p,n=local(folder)
  if not n.startswith('.local/learned-'):raise ValueError('Unexpected historical benchmark folder')
  if sum(x.stat().st_size for x in p.rglob('*') if x.is_file())>30_000_000:raise ValueError('Unexpected engineering-history size; review without omitting records')
  for child in sorted(p.rglob('*')):
   if child.is_file():add(child,'preserved artificial engineering history, not accepted empirical evidence')
 v1=jread('.local/learned-process-benchmark-final.json')
 for name,h in v1['sourceHashes'].items():
  copy='.local/learned-process-benchmark-v1-history/sources/'+name
  if digest(ROOT/copy)!=h:raise ValueError('Historical v1 source copy missing/drifted '+name)
 preservation=jread('.local/v11-working-preservation/receipt.json')
 if preservation.get('v10ArchiveSha256')!=BASE_SHA or len(preservation.get('files',[]))!=10:raise ValueError('Working V10 preservation inventory differs')
 add('.local/v11-working-preservation/receipt.json','exact working V10 preservation before authorized navigation changes')
 for row in preservation['files']:
  add(row['copy'],'exact pre-integration working V10 copy, separately labelled from archive')
  if stream.digest_file(ROOT/row['copy'])!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Working preservation drift '+row['copy'])
 for p in sorted((ROOT/'.local').glob('opponent-v11-*.png')):add(p,'actual developer desktop/narrow screenshot')
 for name in ['learned-opponent-display-smoke-result.json','learned-opponent-export-smoke-result.json','main-report-v11-first-build.json']:
  if (ROOT/'.local'/name).exists():add('.local/'+name,'explicit developer verification or first-report provenance')
 routes=prior.prior.prior.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
 if PDF not in routes.values():raise ValueError('Current V11 report route missing')
 for url,name in routes.items():add(name,'closed current static route '+url)
 route_imports(sources,routes,add)
 for name,h in expected.items():
  if digest(ROOT/name)!=h:raise ValueError('Accepted source/input drift '+name)
 sources['README-v10.md']={'kind':'zip','archive':BASE,'member':'README.md'}
 sources['DELIVERY_FREEZE-v10.json']=sources.pop('DELIVERY_FREEZE.json')
 sources['START-HERE.txt']={'kind':'bytes','data':b'CURRENT REPORT: output/pdf/local-guard-welfare-report-v11.pdf\nStart: node research/demo-server.js and open http://127.0.0.1:3003/\nLearned partner: /opponent. This full archive contains the48-response numerical evidence and inherited checkpoints.\nThe separate viewer is a smaller interface copy, not numerical audit reproduction.\nAuthor affiliation remains unsupplied. Read README.md for scope and reproduction.\n'}
 sources['STATIC_ROUTES.json']={'kind':'bytes','data':json_bytes(routes)}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-learned-opponents-study','version':'11.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js','audit':'python -B research/audit-learned-opponent.py','analyze':'node research/learned-opponent-analysis.js','test':'node --test --test-isolation=none '+' '.join(node_tests)}})}
 inventory=stream.inventory(sources)
 for name in protected:
  if any(inventory[name][k]!=inherited[name][k] for k in ['sha256','bytes']):raise ValueError('Inherited protected byte mismatch '+name)
 if sum(r['bytes'] for r in inventory.values())>3_000_000_000:raise ValueError('Unexpected oversized payload; no cases omitted')
 counts=suite_counts(node_tests,PY_TESTS,game_test)
 if counts['gameTestCount']!=game_test_count:raise ValueError('Explicit game-test count differs from final registered suite')
 config={'nodeTests':node_tests,'pythonTests':PY_TESTS,'harnesses':HARNESSES,**counts}
 return sources,inventory,routes,provenance,len(protected),config

def report_check(directory,expected):
 try:from pypdf import PdfReader
 except ImportError:
  sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'));from pypdf import PdfReader
 p=directory/PDF;checks=json.loads((directory/'output/pdf/main-report-v11-checks.json').read_text());texts=[page.extract_text() for page in PdfReader(str(p)).pages]
 if digest(p)!=expected or checks['sha256']!=expected:raise ValueError('PDF differs from final actual-page review')
 body=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t));abstract=re.search(r'\bAbstract\.\s+(.*?)\n1 ',texts[0],re.S)
 if not abstract:raise ValueError('Actual abstract missing')
 words=len(abstract.group(1).split())
 if not(1<=body<=8 and 150<=words<=250 and words==checks['abstractWords'] and len(texts)==checks['pages'] and 'Mohammadpayam Teabi' in texts[0] and 'LLM usage and author contributions' in '\n'.join(texts) and 'Dual-Use / Ethical Considerations' in '\n'.join(texts)):raise ValueError('Actual PDF structure/disclosure invalid')
 return {'sha256':expected,'bytes':p.stat().st_size,'pages':len(texts),'bodyPages':body,'abstractWords':words,'affiliationSupplied':False}

def verify_full(archive,pdf_sha,config):
 node=shutil.which('node')
 if not node:raise RuntimeError('Node24+ required; no automatic installation')
 with base.verification_workspace() as target:
  records=stream.extract_verified(archive,target)
  out=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*config['nodeTests']],target,timeout=600)
  if not re.search(r'^# tests '+str(config['expectedNode'])+'$',out,re.M) or not re.search(r'^# fail 0$',out,re.M):raise ValueError('Declared new Node tests differ')
  code="import sys,unittest;s=unittest.TestSuite();[s.addTests(unittest.defaultTestLoader.discover('tests',p)) for p in "+repr(config['pythonTests'])+" ];r=unittest.TextTestRunner(stream=sys.stdout).run(s);sys.exit(not r.wasSuccessful())"
  out=base.execute([sys.executable,'-B','-c',code],target,timeout=600)
  if not re.search(r'Ran '+str(config['expectedPythonScientific']+config['expectedDelivery'])+r' tests?',out) or not re.search(r'^OK$',out,re.M):raise ValueError('Declared Python/delivery tests differ')
  # Verify only: never call the Python primary run entry point.
  base.execute([node,'research/learned-opponent-study.js','verify'],target,timeout=300)
  scratch=target/'.reproduce';scratch.mkdir()
  fresh=scratch/('independent-audit-'+uuid.uuid4().hex+'.json')
  audit=json.loads(base.execute([sys.executable,'-B','research/audit-learned-opponent.py','--output',str(fresh)],target,timeout=1800))
  accepted=json.loads((target/PREFIX/'independent-audit.json').read_text())
  if not(audit.get('passed') is True and audit.get('labels')==48 and audit.get('allPlannedLabelsRetained') is True and all(audit['corruptionNegativeControls'].values()) and fresh.exists()):raise ValueError('Complete fresh48 audit failed')
  stable=['studyManifestHash','resultsSha256','indexSha256','completionSha256','journalSha256','runStartSha256','auditorSourceHash','arithmeticBackendHash','labels','certifiedRecords','tightRecords','looseRecords','unavailableRecords','executionFailures','budgetFailures','maskedQCellsReconstructed','worldStatesChecked','legalStateActionEdgesChecked','independentSummaries','corruptionNegativeControls','fullTrainingReplay','optimizerIterationsReplayed','inheritedEconomicReenumeration']
  if any(audit[k]!=accepted[k] for k in stable):raise ValueError('Fresh scientific fields differ from accepted proof')
  base.execute([node,'research/learned-opponent-analysis.js'],target,timeout=300)
  for name in [PREFIX+'summary.json','research/LEARNED_OPPONENT_RESULTS.md']:
   if digest(target/name)!=records[name]['sha256']:raise ValueError('Exact descriptive byte mismatch '+name)
  base.execute([node,'research/build-learned-opponent-web.js','--output','.reproduce/opponent-data.json'],target,timeout=300)
  if digest(scratch/'opponent-data.json')!=records[PREFIX+'web-data.json']['sha256']:raise ValueError('Web export byte mismatch')
  harnesses=[json.loads(base.execute([node,name],target,timeout=900)) for name in config['harnesses']]
  if not all(r['passed'] for r in harnesses):raise ValueError('Presentation checks failed')
  base.execute([sys.executable,'-B','research/build-learned-opponent-figure.py'],target,timeout=300)
  figure_names=[n for n in records if n.startswith('research/learned-opponent-figures/') and n.endswith(('.png','.svg','.json'))]
  if len([n for n in figure_names if n.endswith(('.png','.svg'))])!=2 or any(digest(target/n)!=records[n]['sha256'] for n in figure_names):raise ValueError('New scientific figure/sidecar did not regenerate exactly')
  base.execute([sys.executable,'-B',REPORT_BUILDER],target,timeout=300)
  pdf=report_check(target,pdf_sha);routes=json.loads((target/'STATIC_ROUTES.json').read_text());http=base.http_smoke(target,routes,node)
  for name,row in records.items():
   if stream.digest_file(target/name)!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Verification mutated payload '+name)
  source=stream.extracted_sources(target,records);repacked=scratch/'full-repacked.zip';stream.zip_sources(repacked,source,stream.inventory(source))
  if digest(repacked)!=digest(archive):raise ValueError('Full fresh repack differs')
  second=scratch/'second-full';second.mkdir();stream.extract_verified(repacked,second)
  return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(records)+1,'tests':{'newScientific':config['expectedNode']+config['expectedPythonScientific'],'deliveryIntegrity':config['expectedDelivery'],'total':config['expectedTotal'],'failed':0},'independentAudit':audit,'freshAuditReceiptSeparate':True,'oldFullAuditsRerun':False,'oldPayloadPreservedByteExact':True,'fullTrainingReplay':False,'optimizerIterationsReplayed':False,'summaryReportExportByteExact':True,'newFigurePairByteExact':True,'mainReport':pdf,'presentationChecks':harnesses,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'allPayloadsUnchanged':True,'freshRepackByteExact':True,'secondFreshExtractionVerified':True}

def full_plan(game_test_count):
 _,files,routes,_,protected,config=collect(game_test_count);value={'scope':'Prospective full V11 response evidence preserving closed V10 bytes; no nested older ZIP, primary optimization or repeated full inherited audit','builderSourceHash':digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'scientificManifestSha256':STUDY_SHA,'files':files,'staticRoutes':len(routes),'protectedInheritedFiles':protected,'verificationConfiguration':config}
 PLAN.write_bytes(json_bytes(value));print(json.dumps({'plan':PLAN.relative_to(ROOT).as_posix(),'sha256':digest(PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'staticRoutes':len(routes),'createsArchive':False}))

def full_build(pdf_sha):
 if FULL.exists():raise ValueError('Existing closed full archive preserved')
 frozen=jread(PLAN.relative_to(ROOT));config=frozen['verificationConfiguration'];game_count=config['gameTestCount']
 source,files,routes,provenance,protected,current=collect(game_count)
 if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['baseArchiveSha256']!=BASE_SHA or frozen['files']!=files or current!=config or files[PDF]['sha256']!=pdf_sha:raise ValueError('Prospective inventory/reviewed PDF changed')
 if shutil.disk_usage(ROOT).free<4*sum(r['bytes'] for r in files.values())+256_000_000:raise ValueError('Insufficient verification disk; no evidence omitted')
 began=time.perf_counter();source['DELIVERY_FREEZE.json']={'kind':'file','path':PLAN};files['DELIVERY_FREEZE.json']=stream.digest_file(PLAN)
 contents={'scope':'Full accepted V11 learned-response evidence and immutable inherited V10 data. Complete training/optimizer replay and old full audit reruns are not claimed.','baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':digest(PLAN),'files':{n:{**r,'provenance':sorted(provenance.get(n,{'closed V10 payload or generated navigation'}))} for n,r in files.items()}}
 source['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};files['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(source['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(source['PACKAGE_CONTENTS.json']['data'])}
 temporary=FULL.with_name(FULL.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,source,files);checks=verify_full(temporary,pdf_sha,config)
 if FULL.exists():raise ValueError('Delivery path appeared during verification')
 temporary.rename(FULL);receipt={'archive':FULL.relative_to(ROOT).as_posix(),'sha256':digest(FULL),'bytes':FULL.stat().st_size,'prospectiveInventorySha256':digest(PLAN),'builderSourceHash':digest(Path(__file__)),'seconds':time.perf_counter()-began,'baseArchiveSha256':BASE_SHA,'protectedInheritedFiles':protected,'verification':checks};RECEIPT.write_bytes(json_bytes(receipt))
 (ROOT/'research/LEARNED_OPPONENT_PACKAGE_VERIFICATION.md').write_text('# Full learned-opponent delivery verification\n\n'+f"Archive `{receipt['archive']}`; SHA256 `{receipt['sha256']}`.\n\n"+'Fresh extraction passed the complete new48-label independent audit in a separate receipt, declared tests, exact derived/web/new-figure/report builds, portable developer checks, all static routes, every payload SHA/CRC and identical repack plus second extraction. Byte-identical inherited evidence was preserved. Old full learner audits, complete training and optimizer iterations were not replayed. The separate viewer cannot reproduce omitted numerical inputs. Author affiliation remains unsupplied; no external submission occurred.\n',encoding='utf-8')
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
 sources['README.md']={'kind':'bytes','data':('# Viewer only\n\nStart `node research/demo-server.js`, then open http://127.0.0.1:3003/ or /opponent. Node24+ is required; no installation, API key or paid service is needed.\n\nThe current report and routed displays are exact full-archive copies. Raw numerical records, large learner checkpoints and audit dependencies are omitted; this viewer cannot reproduce the numerical audits. Use the separate full evidence archive.\n\nFull evidence: `'+pointer['fullEvidenceArchive']+'`\n\nSHA256: `'+pointer['fullEvidenceSha256']+'`\n\nSee FULL_EVIDENCE_POINTER.json. Neither archive nests the other. Author affiliation remains unsupplied. Developer QA is not human validation; no external submission is implied.\n').encode()}
 sources['START-HERE.txt']={'kind':'bytes','data':b'VIEWER ONLY: node research/demo-server.js\nOpen http://127.0.0.1:3003/ or /opponent\nRead README.md and FULL_EVIDENCE_POINTER.json. Complete numerical reproduction requires the full archive.\n'}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-viewer','version':'11.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js'}})}
 return sources,stream.inventory(sources),routes,pointer,provenance

def viewer_plan():
 _,files,routes,pointer,_=viewer_sources();value={'scope':'Prospective exact runtime/route subset of final full evidence','builderSourceHash':digest(Path(__file__)),'fullEvidence':pointer,'files':files,'staticRoutes':len(routes)};VIEW_PLAN.write_bytes(json_bytes(value));print(json.dumps({'plan':VIEW_PLAN.relative_to(ROOT).as_posix(),'sha256':digest(VIEW_PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'createsArchive':False}))

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
 VIEW_RECEIPT.write_bytes(json_bytes(value));print(json.dumps({k:value[k] for k in ['archive','bytes','sha256','payloadFiles']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);a=sub.add_parser('plan');a.add_argument('--game-test-count',type=int,required=True);b=sub.add_parser('build');b.add_argument('--final-freeze-report-sha',required=True);sub.add_parser('viewer-plan');sub.add_parser('viewer-build');args=p.parse_args()
 if args.mode=='plan':full_plan(args.game_test_count)
 elif args.mode=='build':full_build(args.final_freeze_report_sha)
 elif args.mode=='viewer-plan':viewer_plan()
 else:viewer_build()
