"""Allowlisted V7 calibration delivery, inheriting the closed V6 payload.

`plan` saves the prospective payload-hash inventory; `build` requires that exact
inventory and the reviewed three-page note hash. Checks use a fresh extraction.
"""
from pathlib import Path
import argparse, importlib.util, json, re, shutil, sys, time, zipfile

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'output/price-guard-recurring-v6.zip'
BASE_SHA='6d843fc7c479457b27f34d08152f90c0531f435d2f908a8947bd7a11ef9f299b'
V3_SHA='2c13cd18f85ce1e3dd42f2b93480d6b9a3412d564d16ac2102a581ca14fa5857'
V4_SHA='b1817ff6931eda87b64a49fe4355094f0cf95b11e98e72298472dbbb16cf25fb'
V5_SHA='898582d2dcfab995a9a56cdaf87aea8a85e90ac2eb0c560b98e6aa6a866b64ef'
V6_SHA='c7c0e309ba38599d7930933b9783e321a5b52732225837e235706d74b6957a1b'
OUT=ROOT/'output/price-guard-calibration-v7.zip'
PLAN=ROOT/'output/misspec-package-plan.json'
RECEIPT=ROOT/'output/misspec-package-verification.json'
REPORT=ROOT/'research/MODEL_MISSPEC_PACKAGE_VERIFICATION.md'
NOTE='output/pdf/demand-calibration-note.pdf'
NODE_TESTS=['tests/uncertainty-view.test.js']
PY_TESTS=['tests/test_misspec.py','tests/test_misspec_audit.py']
HARNESS=['.local/uncertainty-display-smoke.mjs','.local/uncertainty-export-smoke.mjs']
SCRIPTS=['misspec-study.py','audit-misspec-study.py','misspec-analysis.js',
 'build-misspec-web.js','build-misspec-figures.py','build-misspec-note.py',
 'package-misspec.py','demo-server.js']
DOCS=['MODEL_MISSPEC_PROTOCOL.md','MODEL_MISSPEC_THEORY.md','MODEL_MISSPEC_REVIEW.md',
 'MODEL_MISSPEC_RESULTS.md','MISSPEC_WEB_SCHEMA.md','MISSPEC_REPLAY_QA.md',
 'RECURRING_PACKAGE_VERIFICATION.md']
spec=importlib.util.spec_from_file_location('cycle_package',ROOT/'research/package-cycle-study.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha=base.sha;json_bytes=base.json_bytes


def route_map(server):
    """Close the known literal map, allowing the explicitly reviewed front door."""
    routes={}
    pairs=re.findall(r"['\"](/[^'\"]*)['\"]\s*:\s*['\"]([^'\"]+)['\"]",server)
    for url,value in pairs:
        _,name=base.rooted(ROOT/'research'/value)
        if url in routes and routes[url]!=name:
            if not (url=='/' and routes[url]=='research/demo/index.html' and name=='research/demo/overview.html'):
                raise ValueError('Unapproved conflicting static route '+url)
        routes[url]=name
    if routes.get('/')!='research/demo/overview.html' or routes.get('/original')!='research/demo/index.html' or routes.get('/uncertainty')!='research/demo/uncertainty.html':
        raise ValueError('Reviewed front door/legacy/game routes missing')
    return routes


def inherited_payload():
    if base.digest(BASE)!=BASE_SHA:raise ValueError('Closed V6 archive changed')
    with zipfile.ZipFile(BASE) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or archive.testzip():raise ValueError('V6 inventory/CRC mismatch')
        if any(not base.safe_name(name) for name in names):raise ValueError('Unsafe V6 path')
        payloads={name:archive.read(name) for name in names}
    manifest=json.loads(payloads.pop('PACKAGE_CONTENTS.json'))
    if set(payloads)!=set(manifest['files']):raise ValueError('V6 manifest inventory mismatch')
    for name,record in manifest['files'].items():
        if sha(payloads[name])!=record['sha256'] or len(payloads[name])!=record['bytes']:raise ValueError('V6 payload drift '+name)
    return payloads


def instructions(route):
    return f"""PRICE GUARD — DEMAND CALIBRATION SENSITIVITY (V7)

Read output/pdf/demand-calibration-note.pdf, the reviewed three-page calibration
supplement. The V6 recurring-control note and earlier accepted papers are preserved.
Enforcement, physical caps, price paths and absolute welfare targets stay fixed;
the new question is how lower actual inside-product quality changes the guarantee.

This compact archive inherits the complete reviewed V6 payload. It adds all
16 calibration models/80 target labels, 240 policy slots, 960 reserve-level rows,
320 robust-period rows, their independent audit, sources, graphics and evidence.
Duplicate policies and empty safe sets remain explicit. Old full learning traces
are not included/replayed. Four declared error bounds are shown without certified
interpolation. This deterministic sensitivity audit does not estimate error rates.

Node.js24+ (builtins only):
  node research/demo-server.js
  Open http://127.0.0.1:3003/ (Market Lab front door) or {route} (calibration).
  node --test --test-isolation=none {' '.join(NODE_TESTS)}
  node research/misspec-analysis.js
  node .local/uncertainty-display-smoke.mjs
  node .local/uncertainty-export-smoke.mjs
  node research/build-misspec-web.js --output reproduced-calibration-data.json

Python3.11+ (standard library only for arithmetic/audit/tests):
  python -B -m unittest discover -s tests -p test_misspec.py
  python -B -m unittest discover -s tests -p test_misspec_audit.py
  python -B research/audit-misspec-study.py
  python -B research/misspec-study.py verify
Independent code rechecks all new calibration evidence read-only and verifies
inherited provenance. Default audits do not overwrite saved certificates. The
separate interval calculations share the standard Decimal arithmetic backend.

Optional figure/note rebuilding requires numpy, matplotlib, reportlab, pypdf and
Pillow, using saved evidence only:
  python research/build-misspec-figures.py --output reproduced-calibration-figures
  python research/build-misspec-note.py

The three policy slots retain the inherited startup and average-floor meanings.
Largest periods concern one fixed-cap/fixed-period family with a known error bound,
not a newly optimized enforcement rule. Old physical caps/targets can differ across
labels. A welfare-guarantee failure is not seller harm or an incentive claim.
Portable adapters test logic, not human comprehension or full accessibility.
Actual browser checks and their limits are recorded in MISSPEC_REPLAY_QA.md.

DELIVERY_FREEZE.json records the prospective payload inventory, before this zip.
PACKAGE_CONTENTS.json hashes every payload except itself. The external verification
receipt records fresh extraction, complete audits, regeneration and local routes.
To repack this intact extracted payload without any older zip:
  python research/package-cycle-study.py repack EXTRACTED_DIRECTORY OUTPUT.zip
No experimental seller/model API calls, paid service, external submission or
publication. Codex development assistance is separately disclosed.
"""


def collect():
    payloads=inherited_payload();original=dict(payloads);queue=[];provenance={};expected={}
    mutable={'README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','research/demo-server.js','research/demo/overview.html','DELIVERY_FREEZE.json'}
    protected=set(payloads)-mutable
    def add(file,reason):
        p,name=base.rooted(file)
        if any(tag in name for tag in ['SPARSE_RESET_CANDIDATE','FUTURE_']):raise ValueError('Unaccepted future/candidate material excluded')
        data=p.read_bytes()
        if name in protected and data!=original[name]:raise ValueError('Closed V6 payload changed '+name)
        if name not in provenance:queue.append(name)
        payloads[name]=data;provenance.setdefault(name,set()).add(reason)
        return name
    for name in SCRIPTS:add('research/'+name,'explicit accepted calibration source')
    for name in DOCS:add('research/'+name,'accepted calibration theory/results/review/QA')
    for name in NODE_TESTS+PY_TESTS:add(name,'new primary and independent synthetic tests')
    for name in HARNESS:add(name,'portable calibration UI/export adapter checks; not human/layout proof')
    for folder in ['research/misspec-results','research/misspec-figures']:
        for file in (ROOT/folder).rglob('*'):
            if file.is_file():add(file,'complete new calibration evidence and figures')
    for name in ['demand-calibration-note.pdf','demand-calibration-note.txt','misspec-note-checks.json']:
        add('output/pdf/'+name,'reviewed three-page calibration note')
    add('output/recurring-package-verification.json','closed inherited V6 verification receipt')
    for image in (ROOT/'.local').glob('uncertainty-v7-*.png'):add(image,'actual calibration developer screenshot evidence')
    routes=route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
    for url,name in routes.items():add(name,'current closed static route '+url)
    i=0
    while i<len(queue):
        name=queue[i];i+=1;p=ROOT/name;data=payloads[name]
        if p.suffix=='.json':
            value=json.loads(data.decode('utf-8-sig'))
            if isinstance(value,dict):
                for field in base.MANIFEST_FIELDS:
                    for dependency,h in value.get(field,{}).items():
                        dep=add(dependency,name+' / '+field);expected[dep]=h
                        if field=='sourceHashes':
                            snapshot=p.parent/'sources'/dependency
                            if snapshot.is_file():expected[add(snapshot,'frozen primary source snapshot')]=h
        if p.suffix in ['.js','.mjs'] and '/sources/' not in name:
            text=data.decode('utf-8-sig')
            imports=re.findall(r"(?:^|[;\n])\s*(?:import|export)\s+(?:[^;'\"]+?\s+from\s*)?['\"]([^'\"\n]+)['\"]",text,re.M)
            imports+=re.findall(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]",text)
            for dependency in imports:
                if dependency.startswith('node:'):continue
                if dependency.startswith(('./','../')):add(p.parent/dependency,'local import '+name)
                elif dependency.startswith('/'):
                    if dependency not in routes:raise ValueError('Unmapped browser import '+dependency)
                    add(routes[dependency],'browser import '+name)
                else:raise ValueError('Unbundled nonnative module '+dependency)
    for name,h in expected.items():
        if sha(payloads[name])!=h:raise ValueError('Frozen dependency drift '+name)
    for name in protected:
        if payloads[name]!=original[name]:raise ValueError('Inherited payload drift '+name)
    if sum(map(len,payloads.values()))>220_000_000:raise ValueError('Unexpected oversized calibration delivery')
    route=next((url for url,name in routes.items() if name=='research/demo/uncertainty.html'),None)
    if not route:raise ValueError('Calibration route missing')
    payloads['README-v6.md']=payloads['README.md']
    payloads['DELIVERY_FREEZE-v6.json']=payloads.pop('DELIVERY_FREEZE.json')
    payloads['research/demo/overview-v6.html']=original['research/demo/overview.html']
    payloads['README.md']=('# Demand calibration and Market Lab\n\n'+instructions(route)).encode()
    payloads['START-HERE.txt']=instructions(route).encode()
    package={'name':'price-guard-calibration','version':'7.0.0','private':True,'type':'module','engines':{'node':'>=24'},
      'scripts':{'start':'node research/demo-server.js','test':'node --test --test-isolation=none '+' '.join(NODE_TESTS),
                 'audit':'python -B research/audit-misspec-study.py','analyze':'node research/misspec-analysis.js',
                 'test:ui':'node .local/uncertainty-display-smoke.mjs','test:export':'node .local/uncertainty-export-smoke.mjs'}}
    payloads['package.json']=json_bytes(package);payloads['STATIC_ROUTES.json']=json_bytes(routes)
    return payloads,routes,{name:sorted(reasons) for name,reasons in provenance.items()},len(protected),route


def inventory(payloads):
    return {name:{'sha256':sha(data),'bytes':len(data)} for name,data in sorted(payloads.items())}


def reviewed_note(directory,name,checks_name,expected,pages):
    try:from pypdf import PdfReader
    except ImportError:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'
        if bundled.is_dir():sys.path.append(str(bundled))
        from pypdf import PdfReader
    p=directory/name;checks=json.loads((directory/checks_name).read_text(encoding='utf-8'))
    if base.digest(p)!=expected or checks['sha256']!=expected or checks['pages']!=pages:raise ValueError('Reviewed technical note hash/metadata differs '+name)
    reader=PdfReader(str(p));texts=[page.extract_text() for page in reader.pages]
    if len(texts)!=pages or 'Mohammadpayam Teabi' not in '\n'.join(texts):raise ValueError('Reviewed technical note pages/author differ')
    return {'sha256':expected,'bytes':p.stat().st_size,'pages':pages,'authorVerified':True}


def verify(archive,note_sha):
    node=shutil.which('node')
    if not node:raise RuntimeError('Node24+ required; no automatic installation')
    with base.verification_workspace() as target:
        payloads=base.extract_checked(archive,target)
        science={name:sha(data) for name,data in payloads.items() if name.startswith(('research/cycle-results/','research/handover-init-results/','research/continuous-results/','research/mesh-results/','research/recurring-results/','research/sparse-display-results/','research/misspec-results/'))}
        stdout=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*NODE_TESTS],target)
        tests=re.search(r'^# tests (\d+)$',stdout,re.M);fails=re.search(r'^# fail (\d+)$',stdout,re.M)
        if not tests or int(tests.group(1))!=3 or not fails or int(fails.group(1))!=0:raise ValueError('Three calibration view tests did not pass')
        script="import sys,unittest; s=unittest.TestSuite(); [s.addTests(unittest.defaultTestLoader.discover('tests',p)) for p in ('test_misspec.py','test_misspec_audit.py')]; r=unittest.TextTestRunner(stream=sys.stdout,verbosity=1).run(s); sys.exit(not r.wasSuccessful())"
        python_stdout=base.execute([sys.executable,'-B','-c',script],target)
        pytests=re.search(r'Ran (\d+) tests?',python_stdout)
        if not pytests or int(pytests.group(1))!=21 or not re.search(r'^OK$',python_stdout,re.M):raise ValueError('Twenty-one calibration primary/audit tests did not pass')
        base.execute([sys.executable,'-B','research/misspec-study.py','verify'],target)
        ca=json.loads(base.execute([sys.executable,'-B','research/audit-misspec-study.py'],target,timeout=300))
        if not ca['passed'] or ca['records']!=16 or ca['targetLabels']!=80 or ca['policySlots']!=240 or ca['reserveLevelRows']!=960 or ca['robustPeriodRows']!=320 or not all(ca['corruptionNegativeControls'].values()):raise ValueError('Complete independent calibration audit failed')
        base.execute([node,'research/misspec-analysis.js'],target)
        derived={name:base.digest(target/name)==sha(payloads[name]) for name in ['research/misspec-results/summary.json','research/MODEL_MISSPEC_RESULTS.md']}
        if not all(derived.values()):raise ValueError('Derived calibration export did not reproduce byte-exactly')
        scratch=target/'.reproduce';scratch.mkdir()
        base.execute([node,'research/build-misspec-web.js','--output','.reproduce/calibration-data.json'],target)
        if base.digest(scratch/'calibration-data.json')!=sha(payloads['research/misspec-results/web-data.json']):raise ValueError('Calibration web export is not byte-exact')
        smoke=[json.loads(base.execute([node,name],target)) for name in HARNESS]
        if not all(record.get('passed') is True for record in smoke):raise ValueError('Calibration presentation adapter checks did not pass')
        base.execute([sys.executable,'-B','research/build-misspec-figures.py','--output','.reproduce/calibration-figures'],target)
        figures={p.name:base.digest(p)==base.digest(scratch/'calibration-figures'/p.name) for p in (target/'research/misspec-figures').glob('*') if p.suffix in ['.png','.svg']}
        if len(figures)!=6 or not all(figures.values()):raise ValueError('Three new figures in PNG/SVG did not reproduce byte-exactly')
        base.execute([sys.executable,'-B','research/build-misspec-note.py'],target)
        note=reviewed_note(target,NOTE,'output/pdf/misspec-note-checks.json',note_sha,3)
        v6=reviewed_note(target,'output/pdf/recurring-cap-note.pdf','output/pdf/recurring-note-checks.json',V6_SHA,4)
        v5=reviewed_note(target,'output/pdf/continuous-refinement-note.pdf','output/pdf/refinement-note-checks.json',V5_SHA,4)
        previous=reviewed_note(target,'output/pdf/handover-init-note.pdf','output/pdf/handover-note-checks.json',V4_SHA,3)
        paper=base.pdf_check(target,V3_SHA)
        routes=json.loads((target/'STATIC_ROUTES.json').read_text(encoding='utf-8'))
        frozen=json.loads((target/'DELIVERY_FREEZE.json').read_text(encoding='utf-8'))
        if len(routes)!=frozen['routes']:raise ValueError('Frozen route inventory differs from prospective delivery inventory')
        if routes.get('/')!='research/demo/overview.html' or routes.get('/original')!='research/demo/index.html':raise ValueError('New front door or preserved original route differs')
        http=base.http_smoke(target,routes,node)
        http['successfulGetRoutesIncludingHealth']=len(routes)+1
        for name,h in science.items():
            if base.digest(target/name)!=h:raise ValueError('Verification mutated scientific payload '+name)
        restored=base.load_payload(target);repacked=scratch/'repacked.zip';base.zip_payload(repacked,restored)
        if base.digest(repacked)!=base.digest(archive):raise ValueError('Extracted V7 payload did not repack byte-exactly')
        second=scratch/'repacked-extraction';second.mkdir();base.extract_checked(repacked,second)
        return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(payloads),
          'tests':{'nodePassed':3,'pythonPassed':21,'totalPassed':24,'failed':0,'nodeFiles':NODE_TESTS,'pythonFiles':PY_TESTS},
          'calibrationAudit':ca,'inheritedProvenanceCheckedReadOnly':True,'earlierFullAuditsRerun':False,
          'derivedByteExact':derived,'webExportByteExact':True,'presentationAdapterChecks':smoke,
          'adapterScope':'Actual module/exporter logic through portable adapters, not layout/human/accessibility validation',
          'figureByteExact':figures,'reviewedNoteRebuiltByteExact':True,'calibrationNote':note,
          'preservedV6Note':v6,'preservedV5Note':v5,'preservedInitializerNote':previous,'preservedV3Paper':paper,'http':http,
          'scientificPayloadUnchanged':True,'freshPayloadRepackByteExact':True,'repackedFreshExtractionVerified':True,
          'notRepeated':'No new primary sensitivity optimization, old full learning trace replay or rerun of earlier full stage audits; the independent calibration auditor recomputes all new evidence and verifies inherited provenance.'}


def plan():
    payloads,routes,_,protected,route=collect()
    value={'scope':'Prospective accepted Goal5 V7 demand-calibration sensitivity inventory; provisional future work excluded',
      'builderSourceHash':base.digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'calibrationRoute':route,
      'files':inventory(payloads),'protectedInheritedFiles':protected,'routes':len(routes)}
    PLAN.write_bytes(json_bytes(value))
    print(json.dumps({'inventory':PLAN.relative_to(ROOT).as_posix(),'sha256':base.digest(PLAN),'files':len(payloads),
      'bytes':sum(map(len,payloads.values())),'routes':len(routes),'protectedInheritedFiles':protected,'createsArchive':False}))


def build(note_sha):
    if not re.fullmatch('[0-9a-f]{64}',note_sha):raise ValueError('Reviewed note SHA required')
    started=time.perf_counter();payloads,routes,provenance,protected,route=collect()
    if sha(payloads[NOTE])!=note_sha:raise ValueError('Final reviewed note changed')
    frozen=json.loads(PLAN.read_text(encoding='utf-8'))
    if frozen['builderSourceHash']!=base.digest(Path(__file__)) or frozen['baseArchiveSha256']!=BASE_SHA or frozen['files']!=inventory(payloads):raise ValueError('Prospective delivery inventory changed; do not silently rebuild')
    payloads['DELIVERY_FREEZE.json']=PLAN.read_bytes()
    contents={'scope':'Compact fixed-enforcement calibration sensitivity supplement plus closed V6 payload',
      'baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':base.digest(PLAN),
      'files':{name:{**record,'provenance':provenance.get(name,['closed V6 payload or generated V7 instructions/inventory'])} for name,record in inventory(payloads).items()}}
    payloads['PACKAGE_CONTENTS.json']=json_bytes(contents);base.zip_payload(OUT,payloads)
    checks=verify(OUT,note_sha)
    receipt={'archive':OUT.relative_to(ROOT).as_posix(),'sha256':base.digest(OUT),'bytes':OUT.stat().st_size,
      'uncompressedPayloadBytes':sum(map(len,payloads.values())),'seconds':time.perf_counter()-started,
      'builderSourceHash':base.digest(Path(__file__)),'prospectiveInventorySha256':base.digest(PLAN),
      'baseArchive':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':BASE_SHA,'protectedInheritedFiles':protected},
      'calibrationRoute':route,'verification':checks}
    RECEIPT.write_bytes(json_bytes(receipt))
    REPORT.write_text('# Calibration delivery verification\n\n'+f"Archive: `{receipt['archive']}`\n\nSHA256: `{receipt['sha256']}`\n\nSize: {receipt['bytes']:,} bytes; {checks['payloadFiles']} files.\n\n"+
      f"Before archive creation the prospective payload inventory was announced at SHA256 `{receipt['prospectiveInventorySha256']}`. The build required an exact inventory match. A fresh extraction passed 24 targeted tests (3 Node + 21 Python) and the complete independent calibration audit (16 models/80 targets, 240 policy slots, 960 reserve rows and 320 robust-period rows). The auditor verified inherited provenance read-only; earlier full audits were not repeated. All payload SHA256/CRC checks passed.\n\n"+
      f"The descriptive summary/report, graphical export, all three figures in PNG/SVG, and reviewed three-page note regenerated byte-exactly. The actual view module and exporter adapter checks passed, with their detailed view/negative-control counts retained in the receipt. All {checks['http']['staticRoutes']} closed static routes returned exact payload bytes, plus health ({checks['http']['successfulGetRoutesIncludingHealth']} successful GET paths); missing-route and write-method controls passed. Preserved V6/V5/V4 notes and the V3 paper retain their accepted hashes/page checks.\n\n"+
      'Scientific payloads stayed unchanged. The fresh payload repacked into the identical zip and extracted again successfully. Original V6 and earlier archives and frozen sources remain preserved. The V6 prospective inventory is preserved separately as DELIVERY_FREEZE-v6.json; its original overview page is retained as research/demo/overview-v6.html. No new primary optimization, old full learning trace replay, experimental seller/model API calls, paid service, external submission or publication occurred. Codex development assistance is separately disclosed.\n\n'+
      'Portable adapters and HTTP checks do not establish human comprehension, complete accessibility or browser layout; dedicated QA documents actual developer browser checks and limitations. Independent interval calculations share standard Decimal. The sensitivity audit fixes enforcement, physical caps, price paths and absolute welfare targets while lowering inside-product quality. It estimates neither empirical error frequencies nor seller harm or incentive stability. Largest periods remain conditional on a known uncertainty bound and one fixed controller family.\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    sub.add_parser('plan');build_parser=sub.add_parser('build');build_parser.add_argument('--final-freeze-note-sha',required=True)
    args=parser.parse_args()
    if args.mode=='plan':plan()
    else:build(args.final_freeze_note_sha)
