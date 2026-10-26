"""Prospective V10 full and viewer-only delivery; never runs market cases.

The full package preserves V9 payload bytes and reruns the new timing audit.
The separately finalized viewer points to the full archive without nesting it.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,sys,time,uuid,zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('closed_v9_packager',ROOT/'research/package-adaptive.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
stream=prior.stream;base=prior.base;json_bytes=base.json_bytes
BASE=ROOT/'output/price-guard-adaptive-v9.zip'
BASE_SHA='120a31b1ea82916409b324dd1dca37e6a7fb783337d5d5c7411a01c0534dcafb'
READY_SHA='f8fbc6ec8d3e26f22f1f60492c228b459b93dd0014167d4999b81bb000ef6491'
FULL=ROOT/'output/price-guard-mixed-timing-v10.zip'
PLAN=ROOT/'output/mixed-timing-package-plan.json'
RECEIPT=ROOT/'output/mixed-timing-package-verification.json'
VIEW=ROOT/'output/price-guard-viewer-v10.zip'
VIEW_PLAN=ROOT/'output/viewer-v10-package-plan.json'
VIEW_RECEIPT=ROOT/'output/viewer-v10-package-verification.json'
PDF='output/pdf/local-guard-welfare-report-v10.pdf'
REPORT_BUILDER='research/build-main-report-v10.py'
NODE_TESTS=['tests/mixed-timing-audit.test.js','tests/mixed-timing-format.test.js','tests/mixed-timing-analysis.test.js','tests/mixed-timing-export.test.js']
PY_TESTS=['test_mixed_timing.py','test_mixed_continuous_audit.py','test_mixed_timing_cross_audit.py','test_mixed_audit_driver.py','test_evidence_streaming.py']
HARNESSES=['.local/mixed-timing-display-smoke.mjs','.local/mixed-timing-export-smoke.mjs']
SCRIPTS=['mixed-timing-analysis.js','mixed-timing-format.js','build-mixed-timing-web.js','package-mixed-timing.py','build-main-report-v10.py','demo-server.js']
DOCS=['MIXED_TIMING_RESULTS.md','MIXED_TIMING_REVIEW.md','MIXED_TIMING_REPLAY_QA.md','MIXED_TIMING_PLAY_BRIEF.md','README.md','README_PRESERVATION_GOAL8.json']
digest=lambda p:stream.digest_file(p)['sha256']
def local(name):
 p=Path(name);p=(p if p.is_absolute() else ROOT/p).resolve()
 if not p.is_relative_to(ROOT):raise ValueError('Source escapes workspace')
 return p,p.relative_to(ROOT).as_posix()
def jread(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def route_imports(sources,routes,add):
 seen=set();queue=list(sources)
 while queue:
  name=queue.pop()
  if name in seen:continue
  seen.add(name)
  if not name.endswith(('.js','.mjs')) or '/sources/' in name:continue
  with stream.source_stream(sources[name]) as f:text=f.read().decode('utf-8-sig')
  deps=re.findall(r"(?:^|[;\n])\s*(?:import|export)\s*(?:[^;'\"]+?\s*from\s*)?['\"]([^'\"\n]+)['\"]",text,re.M)
  deps+=re.findall(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]",text)
  for dep in deps:
   if dep.startswith('node:'):continue
   if dep.startswith(('./','../')):n=add(ROOT/Path(name).parent/dep,'local JavaScript dependency of '+name)
   elif dep.startswith('/'):
    if dep not in routes:raise ValueError('Unmapped browser module '+dep)
    n=add(routes[dep],'browser JavaScript dependency of '+name)
   else:raise ValueError('Unbundled external module '+dep)
   if n not in seen:queue.append(n)

def collect(game_test_count):
 if digest(BASE)!=BASE_SHA:raise ValueError('Closed V9 archive changed')
 audit=jread('research/mixed-timing-results/independent-audit.json')
 if not(audit.get('passed') is True and audit.get('requiresOrchestrator') is False and audit.get('continuousChecksComputedInProcess') is True):raise ValueError('Complete authoritative timing acceptance required')
 with zipfile.ZipFile(BASE) as z:
  names=z.namelist();inherited=json.loads(z.read('PACKAGE_CONTENTS.json'))['files']
  if len(names)!=len(set(names)) or set(names)!=set(inherited)|{'PACKAGE_CONTENTS.json'} or any(not stream.safe_name(n) for n in names):raise ValueError('Unsafe/unmanifested V9 inventory')
 sources={n:{'kind':'zip','archive':BASE,'member':n} for n in inherited}
 mutable={'README.md','research/README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','DELIVERY_FREEZE.json','research/demo-server.js','research/demo/overview.html','research/demo/overview.css','research/demo/overview.js'}
 protected=set(sources)-mutable;provenance={};expected={}
 def add(name,reason):
  p,n=local(name)
  if any(word in n for word in ['private-pilot','codex-adapter']) or 'CANDIDATE' in n and n not in inherited:raise ValueError('Unrequested private/candidate material '+n)
  observed=stream.digest_file(p)
  if n in protected and any(observed[k]!=inherited[n][k] for k in ['sha256','bytes']):raise ValueError('Closed protected V9 payload changed '+n)
  sources[n]={'kind':'file','path':p};provenance.setdefault(n,set()).add(reason);return n
 for name in SCRIPTS:add('research/'+name,'accepted timing derivation/report/delivery source')
 for name in DOCS:add('research/'+name,'current accepted narrative/review/presentation scope')
 node_tests=NODE_TESTS.copy();game_test='tests/mixed-timing-game.test.js'
 if (ROOT/game_test).exists():
  if game_test_count<=0:raise ValueError('Explicit actual game-test count required before inventory')
  node_tests.append(game_test)
 elif game_test_count:raise ValueError('Declared game-test suite missing')
 for name in node_tests+['tests/'+p for p in PY_TESTS]+HARNESSES:add(name,'targeted artificial or read-only evidence verification')
 for folder in ['research/mixed-timing-results','research/mixed-timing-figures']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file():add(p,'complete accepted new raw/derived evidence or figure')
 for name in ['local-guard-welfare-report-v10.pdf','local-guard-welfare-report-v10.txt','main-report-v10-checks.json']:add('output/pdf/'+name,'distinct accepted V10 report')
 for name in ['README.md','output/adaptive-package-verification.json','research/mixed-timing-audit-ready.json']:add(name,'current entry or exact accepted/pre-outcome provenance')
 if digest(ROOT/'research/mixed-timing-audit-ready.json')!=READY_SHA:raise ValueError('Pre-outcome independent readiness receipt changed')
 preservation=jread('research/README_PRESERVATION_GOAL8.json')
 if preservation['archiveSha256']!=BASE_SHA:raise ValueError('V9 preservation source differs')
 for row in preservation['files']:
  add(row['preservedAs'],'exact V9 preservation before authorized mutable navigation changes')
  if stream.digest_file(ROOT/row['preservedAs'])!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Preserved V9 file drift')
 for p in sorted((ROOT/'.local').glob('timing-v10-*.png')):add(p,'actual desktop/narrow developer screenshot')
 for name in ['mixed-timing-display-smoke-result.json','mixed-timing-export-smoke-result.json','main-report-v10-first-build.json']:
  if (ROOT/'.local'/name).exists():add('.local/'+name,'explicit developer verification or first-generation provenance')
 routes=prior.prior.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
 if PDF not in routes.values():raise ValueError('Current V10 report route missing')
 for url,name in routes.items():add(name,'closed current static route '+url)
 for mname in ['research/mixed-timing-results/manifest.json','research/mixed-timing-results/summary.json']:
  value=jread(mname)
  for group in ['sourceHashes','inputHashes']:
   for name,h in value.get(group,{}).items():
    expected[add(name,mname+' / exact '+group)]=h
    if group=='sourceHashes' and (ROOT/'research/mixed-timing-results/sources'/name).exists():expected[add('research/mixed-timing-results/sources/'+name,'frozen primary source snapshot')]=h
 route_imports(sources,routes,add)
 for name,h in expected.items():
  if digest(ROOT/name)!=h:raise ValueError('Accepted timing dependency changed '+name)
 sources['README-v9.md']={'kind':'zip','archive':BASE,'member':'README.md'}
 sources['DELIVERY_FREEZE-v9.json']=sources.pop('DELIVERY_FREEZE.json')
 sources['START-HERE.txt']={'kind':'bytes','data':b'CURRENT REPORT: output/pdf/local-guard-welfare-report-v10.pdf\nStart: node research/demo-server.js and open http://127.0.0.1:3003/\nMixed timing: /timing. This full archive contains numerical evidence and inherited checkpoints.\nThe separately labelled viewer-only archive is a smaller interface copy, not a substitute for this evidence.\nAuthor affiliation remains unsupplied. Read README.md for scope and reproduction.\n'}
 sources['STATIC_ROUTES.json']={'kind':'bytes','data':json_bytes(routes)}
 package={'name':'price-guard-mixed-timing-study','version':'10.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js','audit':'python -B research/audit-mixed-study.py','analyze':'node research/mixed-timing-analysis.js','test':'node --test --test-isolation=none '+' '.join(node_tests)}}
 sources['package.json']={'kind':'bytes','data':json_bytes(package)}
 inventory=stream.inventory(sources)
 for name in protected:
  if any(inventory[name][k]!=inherited[name][k] for k in ['sha256','bytes']):raise ValueError('Inherited protected byte mismatch '+name)
 if sum(r['bytes'] for r in inventory.values())>3_000_000_000:raise ValueError('Unexpected oversized payload; no cases omitted')
 config={'nodeTests':node_tests,'pythonTests':PY_TESTS,'harnesses':HARNESSES,'expectedNode':22+game_test_count,'expectedPythonScientific':34,'expectedDelivery':3,'expectedTotal':59+game_test_count}
 return sources,inventory,routes,provenance,len(protected),config

def report_check(directory,expected):
 try:from pypdf import PdfReader
 except ImportError:
  sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'));from pypdf import PdfReader
 p=directory/PDF;checks=json.loads((directory/'output/pdf/main-report-v10-checks.json').read_text());texts=[page.extract_text() for page in PdfReader(str(p)).pages]
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
  if not re.search(r'Ran '+str(config['expectedPythonScientific']+config['expectedDelivery'])+r' tests?',out) or not re.search(r'^OK$',out,re.M):raise ValueError('Declared new Python/delivery tests differ')
  base.execute([sys.executable,'-B','research/mixed-timing-study.py','verify'],target,timeout=300)
  audit=json.loads(base.execute([sys.executable,'-B','research/audit-mixed-study.py'],target,timeout=1800))
  if not(audit['passed'] is True and audit['requiresOrchestrator'] is False and audit['continuousChecksComputedInProcess'] is True and audit['models']==24 and audit['targetLabels']==120 and all(audit['corruptionNegativeControls'].values())):raise ValueError('Complete new timing audit failed')
  base.execute([node,'research/mixed-timing-analysis.js'],target,timeout=300)
  for name in ['research/mixed-timing-results/summary.json','research/MIXED_TIMING_RESULTS.md']:
   if digest(target/name)!=records[name]['sha256']:raise ValueError('Descriptive byte mismatch '+name)
  scratch=target/'.reproduce';scratch.mkdir()
  base.execute([node,'research/build-mixed-timing-web.js','--output','.reproduce/timing-data.json'],target,timeout=300)
  if digest(scratch/'timing-data.json')!=records['research/mixed-timing-results/web-data.json']['sha256']:raise ValueError('Web export byte mismatch')
  harnesses=[json.loads(base.execute([node,name],target,timeout=900)) for name in config['harnesses']]
  if not all(r['passed'] for r in harnesses):raise ValueError('Presentation checks failed')
  base.execute([sys.executable,'-B',REPORT_BUILDER],target,timeout=300)
  figures=[n for n in records if n.startswith('research/mixed-timing-figures/') and n.endswith(('.png','.svg'))]
  if len(figures)!=2 or any(digest(target/n)!=records[n]['sha256'] for n in figures):raise ValueError('New timing figure did not regenerate exactly')
  pdf=report_check(target,pdf_sha);routes=json.loads((target/'STATIC_ROUTES.json').read_text());http=base.http_smoke(target,routes,node)
  for name,row in records.items():
   if stream.digest_file(target/name)!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Verification mutated payload '+name)
  source=stream.extracted_sources(target,records);repacked=scratch/'full-repacked.zip';stream.zip_sources(repacked,source,stream.inventory(source))
  if digest(repacked)!=digest(archive):raise ValueError('Full fresh repack differs')
  second=scratch/'second-full';second.mkdir();stream.extract_verified(repacked,second)
  return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(records)+1,'tests':{'newScientific':config['expectedNode']+config['expectedPythonScientific'],'deliveryIntegrity':config['expectedDelivery'],'total':config['expectedTotal'],'failed':0},'independentAudit':audit,'oldFullAuditsRerun':False,'oldPayloadPreservedByteExact':True,'fullTrainingReplay':False,'summaryReportExportByteExact':True,'newFigurePairByteExact':True,'mainReport':pdf,'presentationChecks':harnesses,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'allPayloadsUnchanged':True,'freshRepackByteExact':True,'secondFreshExtractionVerified':True}

def full_plan(game_test_count):
 _,files,routes,_,protected,config=collect(game_test_count);value={'scope':'Prospective full V10 timing evidence, preserving closed V9 payload; no nested older ZIP or repeated full inherited audit','builderSourceHash':digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'files':files,'staticRoutes':len(routes),'protectedInheritedFiles':protected,'verificationConfiguration':config}
 PLAN.write_bytes(json_bytes(value));print(json.dumps({'plan':PLAN.relative_to(ROOT).as_posix(),'sha256':digest(PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'staticRoutes':len(routes),'createsArchive':False}))

def full_build(pdf_sha):
 if FULL.exists():raise ValueError('Existing closed full archive preserved')
 frozen=jread(PLAN.relative_to(ROOT));config=frozen['verificationConfiguration'];game_count=config['expectedNode']-22
 source,files,routes,provenance,protected,current=collect(game_count)
 if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['baseArchiveSha256']!=BASE_SHA or frozen['files']!=files or current!=config or files[PDF]['sha256']!=pdf_sha:raise ValueError('Prospective inventory or reviewed PDF changed')
 if shutil.disk_usage(ROOT).free<4*sum(r['bytes'] for r in files.values())+256_000_000:raise ValueError('Insufficient verification disk space; no evidence omitted')
 begun=time.perf_counter();source['DELIVERY_FREEZE.json']={'kind':'file','path':PLAN};files['DELIVERY_FREEZE.json']=stream.digest_file(PLAN)
 contents={'scope':'Full accepted V10 timing evidence and immutable inherited V9 data. Full training replay and old full audit reruns are not claimed.','baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':digest(PLAN),'files':{n:{**r,'provenance':sorted(provenance.get(n,{'closed V9 payload or explicit generated navigation'}))} for n,r in files.items()}}
 source['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};files['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(source['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(source['PACKAGE_CONTENTS.json']['data'])}
 temporary=FULL.with_name(FULL.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,source,files);checks=verify_full(temporary,pdf_sha,config)
 if FULL.exists():raise ValueError('Delivery path appeared during verification')
 temporary.rename(FULL);receipt={'archive':FULL.relative_to(ROOT).as_posix(),'sha256':digest(FULL),'bytes':FULL.stat().st_size,'prospectiveInventorySha256':digest(PLAN),'builderSourceHash':digest(Path(__file__)),'seconds':time.perf_counter()-begun,'baseArchiveSha256':BASE_SHA,'protectedInheritedFiles':protected,'verification':checks};RECEIPT.write_bytes(json_bytes(receipt))
 (ROOT/'research/MIXED_TIMING_PACKAGE_VERIFICATION.md').write_text('# Full mixed-timing delivery verification\n\n'+f"Archive `{receipt['archive']}`; SHA256 `{receipt['sha256']}`.\n\n"+'Fresh extraction passed the complete new timing audit, declared new tests, exact derived/web/new-figure/report rebuilds, portable presentation checks, all static routes, every payload SHA/CRC and byte-identical repack plus second extraction. The byte-identical inherited evidence was preserved; old full audits and the complete learner training trajectory were not rerun. The separate viewer-only archive cannot replace this numerical evidence. Author affiliation remains unsupplied; no external submission occurred.\n',encoding='utf-8')
 print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))

def viewer_sources():
 receipt=jread(RECEIPT.relative_to(ROOT))
 if receipt['verification']['passed'] is not True or digest(FULL)!=receipt['sha256']:raise ValueError('Final verified full evidence archive required first')
 with zipfile.ZipFile(FULL) as z:contents=json.loads(z.read('PACKAGE_CONTENTS.json'));routes=json.loads(z.read('STATIC_ROUTES.json'))
 sources={};provenance={}
 def add(name,reason):
  if name not in contents['files']:raise ValueError('Viewer source absent from full archive '+name)
  sources[name]={'kind':'zip','archive':FULL,'member':name};provenance[name]=reason;return name
 for name in set(routes.values())|{'research/demo-server.js','STATIC_ROUTES.json'}:add(name,'exact closed full-archive route/runtime copy')
 def import_add(name,reason):
  _,relative=local(name);return add(relative,reason)
 route_imports(sources,routes,import_add)
 pointer={'scope':'Viewer-only interface; omitted raw numerical evidence and checkpoints cannot be audited from this archive','fullEvidenceArchive':receipt['archive'],'fullEvidenceSha256':receipt['sha256'],'fullEvidenceBytes':receipt['bytes'],'fullVerificationReceiptSha256':digest(RECEIPT),'scientificResultsChanged':False}
 sources['FULL_EVIDENCE_POINTER.json']={'kind':'bytes','data':json_bytes(pointer)}
 sources['README.md']={'kind':'bytes','data':('# Viewer only\n\nThis is the smaller local interface copy. Start `node research/demo-server.js`, then open http://127.0.0.1:3003/ or /timing. Node24+ is required; no installs, API keys or paid services are needed.\n\nThe current report and all routed displays are exact copies from the verified full archive. Raw numerical study records, large learner checkpoints and audit dependencies are omitted. This viewer cannot reproduce the numerical audits; use the full evidence archive for independent research verification.\n\nFull evidence: `'+pointer['fullEvidenceArchive']+'`\n\nSHA256: `'+pointer['fullEvidenceSha256']+'`\n\nSee FULL_EVIDENCE_POINTER.json for the binding. Neither archive nests the other. The report discloses model/guard assumptions, AI assistance and limitations; author affiliation remains unsupplied. No human validation or external submission is implied.\n').encode()}
 sources['START-HERE.txt']={'kind':'bytes','data':b'VIEWER ONLY: node research/demo-server.js\nOpen http://127.0.0.1:3003/ or /timing\nRead README.md and FULL_EVIDENCE_POINTER.json. Full raw audit reproduction requires the separate full evidence archive.\n'}
 sources['package.json']={'kind':'bytes','data':json_bytes({'name':'price-guard-viewer','version':'10.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js'}})}
 return sources,stream.inventory(sources),routes,pointer,provenance

def viewer_plan():
 _,files,routes,pointer,_=viewer_sources();value={'scope':'Prospective viewer-only exact runtime/route subset of final full evidence','builderSourceHash':digest(Path(__file__)),'fullEvidence':pointer,'files':files,'staticRoutes':len(routes)};VIEW_PLAN.write_bytes(json_bytes(value));print(json.dumps({'plan':VIEW_PLAN.relative_to(ROOT).as_posix(),'sha256':digest(VIEW_PLAN),'files':len(files),'bytes':sum(r['bytes'] for r in files.values()),'createsArchive':False}))

def viewer_build():
 if VIEW.exists():raise ValueError('Existing viewer delivery preserved')
 source,files,routes,pointer,provenance=viewer_sources();frozen=jread(VIEW_PLAN.relative_to(ROOT))
 if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['files']!=files or frozen['fullEvidence']!=pointer:raise ValueError('Viewer prospective inventory changed')
 source['DELIVERY_FREEZE.json']={'kind':'file','path':VIEW_PLAN};files['DELIVERY_FREEZE.json']=stream.digest_file(VIEW_PLAN)
 contents={'scope':'Viewer only; numerical audits require the separately hash-bound full evidence archive','fullEvidence':pointer,'files':{n:{**r,'provenance':provenance.get(n,'explicit generated viewer instructions/provenance')} for n,r in files.items()}}
 source['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};files['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(source['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(source['PACKAGE_CONTENTS.json']['data'])}
 temporary=VIEW.with_name(VIEW.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,source,files)
 with base.verification_workspace() as target:
  records=stream.extract_verified(temporary,target);http=base.http_smoke(target,routes,shutil.which('node'))
  for name,row in records.items():
   if stream.digest_file(target/name)!={k:row[k] for k in ['sha256','bytes']}:raise ValueError('Viewer runtime check mutated payload '+name)
  scratch=target/'.repack';scratch.mkdir();fresh=stream.extracted_sources(target,records);repacked=scratch/'viewer.zip';stream.zip_sources(repacked,fresh,stream.inventory(fresh))
  if digest(repacked)!=digest(temporary):raise ValueError('Viewer repack differs')
  second=scratch/'second';second.mkdir();stream.extract_verified(repacked,second)
 if VIEW.exists():raise ValueError('Viewer path appeared during verification')
 temporary.rename(VIEW);value={'archive':VIEW.relative_to(ROOT).as_posix(),'sha256':digest(VIEW),'bytes':VIEW.stat().st_size,'payloadFiles':len(files),'prospectiveInventorySha256':digest(VIEW_PLAN),'fullEvidence':pointer,'verification':{'passed':True,'scope':'Viewer-only byte/runtime checks, not independent numerical audit reproduction','payloadHashesAndCRC':True,'allRuntimeDependenciesFromFullArchive':True,'fullEvidenceHashBound':True,'nestedFullArchive':False,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'freshRepackByteExact':True,'secondFreshExtractionVerified':True}}
 VIEW_RECEIPT.write_bytes(json_bytes(value));print(json.dumps({k:value[k] for k in ['archive','bytes','sha256','payloadFiles']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);a=sub.add_parser('plan');a.add_argument('--game-test-count',type=int,default=0);b=sub.add_parser('build');b.add_argument('--final-freeze-report-sha',required=True);sub.add_parser('viewer-plan');sub.add_parser('viewer-build');args=p.parse_args()
 if args.mode=='plan':full_plan(args.game_test_count)
 elif args.mode=='build':full_build(args.final_freeze_report_sha)
 elif args.mode=='viewer-plan':viewer_plan()
 else:viewer_build()
