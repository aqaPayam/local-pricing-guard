"""Allowlisted V6 recurring-cap delivery, inheriting the closed V5 payload.

`plan` saves the prospective payload-hash inventory; `build` requires that exact
inventory and the reviewed four-page note hash. Checks use a fresh extraction.
"""
from pathlib import Path
import argparse, importlib.util, json, re, shutil, sys, time, zipfile

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'output/price-guard-refinement-v5.zip'
BASE_SHA='c69db287329b6db0beb960435add5ce4a957d63648cd772914cd4022ae1b1e29'
V3_SHA='2c13cd18f85ce1e3dd42f2b93480d6b9a3412d564d16ac2102a581ca14fa5857'
V4_SHA='b1817ff6931eda87b64a49fe4355094f0cf95b11e98e72298472dbbb16cf25fb'
V5_SHA='898582d2dcfab995a9a56cdaf87aea8a85e90ac2eb0c560b98e6aa6a866b64ef'
OUT=ROOT/'output/price-guard-recurring-v6.zip'
PLAN=ROOT/'output/recurring-package-plan.json'
RECEIPT=ROOT/'output/recurring-package-verification.json'
REPORT=ROOT/'research/RECURRING_PACKAGE_VERIFICATION.md'
NOTE='output/pdf/recurring-cap-note.pdf'
NODE_TESTS=['tests/recurring-game.test.js','tests/sparse-display-study.test.js','tests/sparse-display-audit.test.js']
PY_TESTS=['tests/test_recurring_cap.py','tests/test_sparse_reset_audit.py']
HARNESS=['.local/recurring-display-smoke.mjs','.local/recurring-export-smoke.mjs']
SCRIPTS=['recurring-cap-study.py','recurring-game.js','sparse-display-study.js',
 'audit-sparse-reset.py','audit-sparse-display.js','recurring-analysis.js',
 'build-recurring-web.js','build-recurring-figures.py','build-recurring-note.py',
 'package-recurring.py','demo-server.js']
DOCS=['SPARSE_RESET_PROTOCOL.md','SPARSE_RESET_THEORY.md','SPARSE_RESET_REVIEW.md',
 'SPARSE_RESET_NOVELTY.md','SPARSE_RESET_GAME_DESIGN.md','RECURRING_REPLAY_QA.md',
 'RECURRING_RESULTS.md','REFINEMENT_PACKAGE_VERIFICATION.md']
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
    if routes.get('/')!='research/demo/overview.html' or routes.get('/original')!='research/demo/index.html' or routes.get('/recurring')!='research/demo/recurring.html':
        raise ValueError('Reviewed front door/legacy/game routes missing')
    return routes


def inherited_payload():
    if base.digest(BASE)!=BASE_SHA:raise ValueError('Closed V5 archive changed')
    with zipfile.ZipFile(BASE) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or archive.testzip():raise ValueError('V5 inventory/CRC mismatch')
        if any(not base.safe_name(name) for name in names):raise ValueError('Unsafe V5 path')
        payloads={name:archive.read(name) for name in names}
    manifest=json.loads(payloads.pop('PACKAGE_CONTENTS.json'))
    if set(payloads)!=set(manifest['files']):raise ValueError('V5 manifest inventory mismatch')
    for name,record in manifest['files'].items():
        if sha(payloads[name])!=record['sha256'] or len(payloads[name])!=record['bytes']:raise ValueError('V5 payload drift '+name)
    return payloads


def instructions(route):
    return f"""PRICE GUARD — CAP & GO / RECURRING CONTROL (V6)

Read output/pdf/recurring-cap-note.pdf, the reviewed four-page recurring-control
supplement. The V5 continuous audit, V4 initializer note and V3 paper are preserved.
The same original physical price cap now repeats; its timing is the new question.
Largest safe periods concern one fixed-cap/fixed-period controller family only.

This compact archive inherits the complete reviewed V5 payload. It includes all
16 recurring continuum models/80 target labels, 64-term scalar-root receipts,
eight finite human games/64 period certificates, all three independent audits,
sources, graphics and evidence. Old full learning traces are not included/replayed.

Node.js24+ (builtins only):
  node research/demo-server.js
  Open http://127.0.0.1:3003/ (Market Lab front door) or {route} (Cap & Go).
  node --test --test-isolation=none {' '.join(NODE_TESTS)}
  node research/audit-sparse-display.js research/sparse-display-results
  node research/recurring-analysis.js
  node .local/recurring-display-smoke.mjs
  node .local/recurring-export-smoke.mjs
  node research/build-recurring-web.js --output reproduced-recurring-data.json

Python3.11+ (standard library only for arithmetic/audit/tests):
  python -B -m unittest discover -s tests -p test_recurring_cap.py
  python -B -m unittest discover -s tests -p test_sparse_reset_audit.py
  python -B research/audit-sparse-reset.py
  python -B research/audit-sparse-reset.py --finite
  python -B research/recurring-cap-study.py verify
Independent code rechecks inherited continuous evidence read-only. Default audits
do not overwrite saved certificates. Interval stacks share standard Decimal;
the separate Fraction audit checks exact saved finite-game reward weights.

Optional figure/note rebuilding requires numpy, matplotlib, reportlab, pypdf and
Pillow, using saved evidence only:
  python research/build-recurring-figures.py --output reproduced-recurring-figures
  python research/build-recurring-note.py

The first cap is an actual rewarded execution. Old history earns zero reward.
Average-from-activation floors differ from individual-round floors and arbitrary
initial-phase claims. A cap activation rate is not changed-quote frequency or
economic cost. Old physical caps/targets can differ across labels. Human play
and scripted worst-price benchmarks have separate ledgers; no model plays.
Portable adapters test logic, not human comprehension or full accessibility.
Actual browser checks and their limits are recorded in RECURRING_REPLAY_QA.md.

DELIVERY_FREEZE.json records the prospective payload inventory, before this zip.
PACKAGE_CONTENTS.json hashes every payload except itself. The external verification
receipt records fresh extraction, complete audits, regeneration and local routes.
To repack this intact extracted payload without any older zip:
  python research/package-cycle-study.py repack EXTRACTED_DIRECTORY OUTPUT.zip
No model game players, APIs, paid service, external submission or publication.
"""


def collect():
    payloads=inherited_payload();original=dict(payloads);queue=[];provenance={};expected={}
    mutable={'README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','research/demo-server.js','DELIVERY_FREEZE.json'}
    protected=set(payloads)-mutable
    def add(file,reason):
        p,name=base.rooted(file)
        if 'SPARSE_RESET_CANDIDATE' in name:raise ValueError('Historical Nash-cap candidate excluded from accepted physical-cap package')
        data=p.read_bytes()
        if name in protected and data!=original[name]:raise ValueError('Closed V5 payload changed '+name)
        if name not in provenance:queue.append(name)
        payloads[name]=data;provenance.setdefault(name,set()).add(reason)
        return name
    for name in SCRIPTS:add('research/'+name,'explicit accepted recurring-control source')
    for name in DOCS:add('research/'+name,'accepted recurring theory/results/review/QA')
    for name in NODE_TESTS+PY_TESTS:add(name,'new primary and independent synthetic tests')
    for name in HARNESS:add(name,'portable recurring UI/export adapter checks; not human/layout proof')
    for folder in ['research/recurring-results','research/sparse-display-results','research/recurring-figures']:
        for file in (ROOT/folder).rglob('*'):
            if file.is_file():add(file,'complete new continuous/finite controller evidence and figures')
    for name in ['recurring-cap-note.pdf','recurring-cap-note.txt','recurring-note-checks.json']:
        add('output/pdf/'+name,'reviewed four-page recurring-cap note')
    add('output/refinement-package-verification.json','closed inherited V5 verification receipt')
    for pattern in ['recurring-v6-*.png','overview-v6-*.png']:
        for image in (ROOT/'.local').glob(pattern):add(image,'actual recurring/overview developer screenshot evidence')
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
    if sum(map(len,payloads.values()))>180_000_000:raise ValueError('Unexpected oversized recurring delivery')
    route=next((url for url,name in routes.items() if name=='research/demo/recurring.html'),None)
    if not route:raise ValueError('Recurring route missing')
    payloads['README-v5.md']=payloads['README.md']
    payloads['DELIVERY_FREEZE-v5.json']=payloads.pop('DELIVERY_FREEZE.json')
    payloads['README.md']=('# Cap & Go and Market Lab\n\n'+instructions(route)).encode()
    payloads['START-HERE.txt']=instructions(route).encode()
    package={'name':'price-guard-recurring','version':'6.0.0','private':True,'type':'module','engines':{'node':'>=24'},
      'scripts':{'start':'node research/demo-server.js','test':'node --test --test-isolation=none '+' '.join(NODE_TESTS),
                 'audit':'node research/audit-sparse-display.js research/sparse-display-results','analyze':'node research/recurring-analysis.js',
                 'test:ui':'node .local/recurring-display-smoke.mjs','test:export':'node .local/recurring-export-smoke.mjs'}}
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
        stdout=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*NODE_TESTS],target)
        tests=re.search(r'^# tests (\d+)$',stdout,re.M);fails=re.search(r'^# fail (\d+)$',stdout,re.M)
        if not tests or int(tests.group(1))!=12 or not fails or int(fails.group(1))!=0:raise ValueError('Twelve finite controller tests did not pass')
        script="import sys,unittest; s=unittest.TestSuite(); [s.addTests(unittest.defaultTestLoader.discover('tests',p)) for p in ('test_recurring_cap.py','test_sparse_reset_audit.py')]; r=unittest.TextTestRunner(stream=sys.stdout,verbosity=1).run(s); sys.exit(not r.wasSuccessful())"
        python_stdout=base.execute([sys.executable,'-B','-c',script],target)
        pytests=re.search(r'Ran (\d+) tests?',python_stdout)
        if not pytests or int(pytests.group(1))!=15 or not re.search(r'^OK$',python_stdout,re.M):raise ValueError('Fifteen recurring primary/audit tests did not pass')
        base.execute([sys.executable,'-B','research/recurring-cap-study.py','verify'],target)
        ca=json.loads(base.execute([sys.executable,'-B','research/audit-sparse-reset.py'],target,timeout=300))
        fa=json.loads(base.execute([node,'research/audit-sparse-display.js','research/sparse-display-results'],target))
        ra=json.loads(base.execute([sys.executable,'-B','research/audit-sparse-reset.py','--finite'],target))
        if not ca['passed'] or ca['records']!=16 or ca['targetLabels']!=80 or not all(ca['corruptionNegativeControls'].values()):raise ValueError('Complete independent recurring continuum audit failed')
        if not fa['passed'] or fa['cases']!=8 or not all(fa['corruptionNegativeControls'].values()):raise ValueError('Complete independent finite-game audit failed')
        if not ra['passed'] or ra['cases']!=8 or ra['certificates']!=64 or not all(ra['corruptionNegativeControls'].values()):raise ValueError('Complete independent saved-weight rational audit failed')
        science={name:sha(data) for name,data in payloads.items() if name.startswith(('research/cycle-results/','research/handover-init-results/','research/continuous-results/','research/mesh-results/','research/recurring-results/','research/sparse-display-results/'))}
        base.execute([node,'research/recurring-analysis.js'],target)
        derived={name:base.digest(target/name)==sha(payloads[name]) for name in ['research/recurring-results/summary.json','research/RECURRING_RESULTS.md']}
        if not all(derived.values()):raise ValueError('Derived recurring export did not reproduce byte-exactly')
        scratch=target/'.reproduce';scratch.mkdir()
        base.execute([node,'research/build-recurring-web.js','--output','.reproduce/recurring-data.json'],target)
        if base.digest(scratch/'recurring-data.json')!=sha(payloads['research/recurring-results/web-data.json']):raise ValueError('Recurring web export is not byte-exact')
        smoke=[json.loads(base.execute([node,name],target)) for name in HARNESS]
        if not all(record.get('passed') is True for record in smoke):raise ValueError('Refinement presentation adapter checks did not pass')
        base.execute([sys.executable,'-B','research/build-recurring-figures.py','--output','.reproduce/recurring-figures'],target)
        figures={p.name:base.digest(p)==base.digest(scratch/'recurring-figures'/p.name) for p in (target/'research/recurring-figures').glob('*') if p.suffix in ['.png','.svg']}
        if len(figures)!=6 or not all(figures.values()):raise ValueError('Three new figures in PNG/SVG did not reproduce byte-exactly')
        base.execute([sys.executable,'-B','research/build-recurring-note.py'],target)
        note=reviewed_note(target,NOTE,'output/pdf/recurring-note-checks.json',note_sha,4)
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
        if base.digest(repacked)!=base.digest(archive):raise ValueError('Extracted V6 payload did not repack byte-exactly')
        second=scratch/'repacked-extraction';second.mkdir();base.extract_checked(repacked,second)
        return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(payloads),
          'tests':{'nodePassed':12,'pythonPassed':15,'totalPassed':27,'failed':0,'nodeFiles':NODE_TESTS,'pythonFiles':PY_TESTS},
          'continuousControllerAudit':ca,'finiteGameAudit':fa,'savedWeightRationalAudit':ra,'inheritedContinuousAuditReranReadOnly':True,
          'derivedByteExact':derived,'webExportByteExact':True,'presentationAdapterChecks':smoke,
          'adapterScope':'Actual module/exporter logic through portable adapters, not layout/human/accessibility validation',
          'figureByteExact':figures,'reviewedNoteRebuiltByteExact':True,'recurringNote':note,
          'preservedV5Note':v5,'preservedInitializerNote':previous,'preservedV3Paper':paper,'http':http,
          'scientificPayloadUnchanged':True,'freshPayloadRepackByteExact':True,'repackedFreshExtractionVerified':True,
          'notRepeated':'No new primary reoptimization or old full learning trace replay; independent auditors recompute the numerical evidence.'}


def plan():
    payloads,routes,_,protected,route=collect()
    value={'scope':'Prospective accepted Goal4 V6 recurring-control inventory; historical Nash-cap candidate excluded',
      'builderSourceHash':base.digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'recurringRoute':route,
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
    contents={'scope':'Compact recurring inherited-cap control supplement plus closed V5 payload',
      'baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':base.digest(PLAN),
      'files':{name:{**record,'provenance':provenance.get(name,['closed V5 payload or generated V6 instructions/inventory'])} for name,record in inventory(payloads).items()}}
    payloads['PACKAGE_CONTENTS.json']=json_bytes(contents);base.zip_payload(OUT,payloads)
    checks=verify(OUT,note_sha)
    receipt={'archive':OUT.relative_to(ROOT).as_posix(),'sha256':base.digest(OUT),'bytes':OUT.stat().st_size,
      'uncompressedPayloadBytes':sum(map(len,payloads.values())),'seconds':time.perf_counter()-started,
      'builderSourceHash':base.digest(Path(__file__)),'prospectiveInventorySha256':base.digest(PLAN),
      'baseArchive':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':BASE_SHA,'protectedInheritedFiles':protected},
      'recurringRoute':route,'verification':checks}
    RECEIPT.write_bytes(json_bytes(receipt))
    REPORT.write_text('# Recurring-control delivery verification\n\n'+f"Archive: `{receipt['archive']}`\n\nSHA256: `{receipt['sha256']}`\n\nSize: {receipt['bytes']:,} bytes; {checks['payloadFiles']} files.\n\n"+
      f"Before archive creation the prospective payload inventory was announced at SHA256 `{receipt['prospectiveInventorySha256']}`. The build required an exact inventory match. A fresh extraction passed 27 targeted tests (12 Node + 15 Python), all three independent audits (16 continuous controllers/80 targets, eight finite games and 64 exact saved-weight period/prefix certificates), and inherited continuous evidence checks read-only. All payload SHA256/CRC checks passed.\n\n"+
      f"The descriptive summary/report, graphical export, all three figures in PNG/SVG, and reviewed four-page note regenerated byte-exactly. The actual game module and exporter adapter checks passed, with their detailed execution/negative-control counts retained in the receipt. All {checks['http']['staticRoutes']} closed static routes returned exact payload bytes, plus health ({checks['http']['successfulGetRoutesIncludingHealth']} successful GET paths); missing-route and write-method controls passed. The preserved V5/V4 supplements and V3 paper retain their accepted hashes/page checks.\n\n"+
      'Scientific payloads stayed unchanged. The fresh payload repacked into the identical zip and extracted again successfully. Original V5/V4/V3 delivery archives and frozen sources remain preserved. The V5 prospective inventory is preserved separately as DELIVERY_FREEZE-v5.json. No new primary reoptimization, old full learning trace replay, model game player, paid service, external submission or publication occurred.\n\n'+
      'Portable adapters and HTTP checks do not establish human comprehension, complete accessibility or browser layout; dedicated QA documents actual developer browser checks and limitations. Interval calculations share standard Decimal. Exact-real continuous bounds and exact rational means of saved binary64 finite-game weights retain distinct scopes. Cap-rule activation frequency is not changed-quote frequency or general economic cost; no incentive stability or optimum over other controller families is inferred.\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    sub.add_parser('plan');build_parser=sub.add_parser('build');build_parser.add_argument('--final-freeze-note-sha',required=True)
    args=parser.parse_args()
    if args.mode=='plan':plan()
    else:build(args.final_freeze_note_sha)
