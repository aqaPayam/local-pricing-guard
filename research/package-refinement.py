"""Allowlisted V5 refinement evidence delivery, inheriting the closed V4 payload.

`plan` saves the prospective payload-hash inventory; `build` requires that exact
inventory and the reviewed four-page note hash. Checks use a fresh extraction.
"""
from pathlib import Path
import argparse, importlib.util, json, re, shutil, sys, time, zipfile

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'output/price-guard-handover-v4.zip'
BASE_SHA='c3028623d94d84ba29e75a574214cb1dd045e12bffc44ec106533c5a2ef58851'
V3_SHA='2c13cd18f85ce1e3dd42f2b93480d6b9a3412d564d16ac2102a581ca14fa5857'
V4_SHA='b1817ff6931eda87b64a49fe4355094f0cf95b11e98e72298472dbbb16cf25fb'
OUT=ROOT/'output/price-guard-refinement-v5.zip'
PLAN=ROOT/'output/refinement-package-plan.json'
RECEIPT=ROOT/'output/refinement-package-verification.json'
REPORT=ROOT/'research/REFINEMENT_PACKAGE_VERIFICATION.md'
NOTE='output/pdf/continuous-refinement-note.pdf'
NODE_TESTS=['tests/mesh-refinement.test.js','tests/mesh-refinement-audit.test.js']
PY_TESTS=['tests/test_continuous_interval.py','tests/test_continuous_audit.py']
HARNESS=['.local/refinement-display-smoke.mjs','.local/refinement-export-smoke.mjs']
SCRIPTS=['continuous-study.py','continuous_interval.py','audit-continuous-study.py',
 'mesh-refinement.js','mesh-refinement-study.js','audit-mesh-refinement.js',
 'refinement-analysis.js','build-refinement-web.js','build-refinement-figures.py',
 'build-refinement-note.py','package-refinement.py','demo-server.js']
DOCS=['CONTINUOUS_REFINEMENT_PROTOCOL.md','CONTINUOUS_REFINEMENT_THEORY.md',
 'CONTINUOUS_NUMERIC_ADDENDUM.md','CONTINUOUS_REFINEMENT_REVIEW.md',
 'REFINEMENT_NOVELTY.md','REFINEMENT_REPLAY_DESIGN.md','REFINEMENT_REPLAY_QA.md',
 'REFINEMENT_RESULTS.md','HANDOVER_INIT_PACKAGE_VERIFICATION.md']
spec=importlib.util.spec_from_file_location('cycle_package',ROOT/'research/package-cycle-study.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha=base.sha;json_bytes=base.json_bytes


def inherited_payload():
    if base.digest(BASE)!=BASE_SHA:raise ValueError('Closed V4 archive changed')
    with zipfile.ZipFile(BASE) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or archive.testzip():raise ValueError('V4 inventory/CRC mismatch')
        if any(not base.safe_name(name) for name in names):raise ValueError('Unsafe V4 path')
        payloads={name:archive.read(name) for name in names}
    manifest=json.loads(payloads.pop('PACKAGE_CONTENTS.json'))
    if set(payloads)!=set(manifest['files']):raise ValueError('V4 manifest inventory mismatch')
    for name,record in manifest['files'].items():
        if sha(payloads[name])!=record['sha256'] or len(payloads[name])!=record['bytes']:raise ValueError('V4 payload drift '+name)
    return payloads


def instructions(route):
    return f"""PRICE GUARD — CONTINUOUS TRANSFER AUDIT (V5)

Read output/pdf/continuous-refinement-note.pdf, the reviewed four-page supplement.
Earlier V4 three-page initializer note and V3 eight-page main paper are preserved.
The exact finite-grid guarantees remain valid; this supplement tests transfer to
continuous prices. It does not claim learned collusion or incentive stability.

This compact archive inherits the complete reviewed V4 payload. It includes all
16 validated continuum records and 72 mesh diagnostics, source/input hashes,
independent auditors, corruption controls, figures, notes and local graphical
replays. Old multi-gigabyte learning traces are not included or replayed.

Node.js24+ (builtins only):
  node research/demo-server.js
  Open http://127.0.0.1:3003{route} (or /activation, /stress, /challenge).
  node --test --test-isolation=none {' '.join(NODE_TESTS)}
  node research/audit-mesh-refinement.js research/mesh-results
  node research/refinement-analysis.js
  node .local/refinement-display-smoke.mjs
  node .local/refinement-export-smoke.mjs
  node research/build-refinement-web.js --output reproduced-refinement-data.json

Python3.11+ (standard library only for arithmetic/audit/tests):
  python -B -m unittest discover -s tests -p "test_continuous*.py"
  python -B research/audit-continuous-study.py
  python -B research/continuous-study.py verify
The full mesh audit also rechecks inherited evidence read-only. Saved certificates
are never overwritten by these default audit commands. The independent continuous
code shares the standard Decimal backend, as disclosed in the review.

Optional figure/note rebuilding requires numpy, matplotlib, reportlab, pypdf and
Pillow, using saved evidence only:
  python research/build-refinement-figures.py --output reproduced-refinement-figures
  python research/build-refinement-note.py

Exact decimal interval endpoints, all five requested/actual target comparisons,
nominal/effective tolerances, failures/resources and every predeclared mesh remain
visible. Coarse-grid success is not a continuous guarantee. No quantitative mesh
error constant, unique basin at every tested grid, or human validation is claimed.
Portable DOM-adapter checks test module logic; browser QA limitations and the
wrapper-only error are recorded in REFINEMENT_REPLAY_QA.md.

DELIVERY_FREEZE.json records the prospective payload inventory, before this zip.
PACKAGE_CONTENTS.json hashes every payload except itself. The external verification
receipt records fresh extraction, complete audits, regeneration and local routes.
To repack this intact extracted payload without any older zip:
  python research/package-cycle-study.py repack EXTRACTED_DIRECTORY OUTPUT.zip
No model game players, APIs, paid service, external submission or publication.
"""


def collect():
    payloads=inherited_payload();original=dict(payloads);queue=[];provenance={};expected={}
    mutable={'README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','research/demo-server.js'}
    protected=set(payloads)-mutable
    def add(file,reason):
        p,name=base.rooted(file)
        if any(word in name.lower() for word in ['sparse_reset','sparse-reset']):raise ValueError('Provisional next-goal material excluded '+name)
        data=p.read_bytes()
        if name in protected and data!=original[name]:raise ValueError('Closed V4 payload changed '+name)
        if name not in provenance:queue.append(name)
        payloads[name]=data;provenance.setdefault(name,set()).add(reason)
        return name
    for name in SCRIPTS:add('research/'+name,'explicit accepted refinement source')
    for name in DOCS:add('research/'+name,'accepted refinement theory/results/review/QA')
    for name in NODE_TESTS+PY_TESTS:add(name,'new primary and independent synthetic tests')
    for name in HARNESS:add(name,'portable refinement UI/export adapter checks; not human/layout proof')
    for folder in ['research/continuous-results','research/mesh-results','research/refinement-figures']:
        for file in (ROOT/folder).rglob('*'):
            if file.is_file():add(file,'complete new validated continuum/mesh/figure evidence')
    for name in ['continuous-refinement-note.pdf','continuous-refinement-note.txt','refinement-note-checks.json']:
        add('output/pdf/'+name,'reviewed four-page refinement note')
    add('output/handover-package-verification.json','closed inherited V4 verification receipt')
    for name in ['refinement-v5-desktop.png','refinement-v5-limit.png','refinement-v5-narrow.png']:
        add('.local/'+name,'actual refinement developer screenshot evidence')
    routes=base.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
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
    if sum(map(len,payloads.values()))>180_000_000:raise ValueError('Unexpected oversized refinement delivery')
    route=next((url for url,name in routes.items() if name=='research/demo/refinement.html'),None)
    if not route:raise ValueError('Refinement route missing')
    payloads['README-v4.md']=payloads['README.md']
    payloads['README.md']=('# Continuous transfer audit\n\n'+instructions(route)).encode()
    payloads['START-HERE.txt']=instructions(route).encode()
    package={'name':'price-guard-refinement','version':'5.0.0','private':True,'type':'module','engines':{'node':'>=24'},
      'scripts':{'start':'node research/demo-server.js','test':'node --test --test-isolation=none '+' '.join(NODE_TESTS),
                 'audit':'node research/audit-mesh-refinement.js research/mesh-results','analyze':'node research/refinement-analysis.js',
                 'test:ui':'node .local/refinement-display-smoke.mjs','test:export':'node .local/refinement-export-smoke.mjs'}}
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
        if not tests or int(tests.group(1))!=8 or not fails or int(fails.group(1))!=0:raise ValueError('Eight mesh tests did not pass')
        script="import sys,unittest; s=unittest.defaultTestLoader.discover('tests','test_continuous*.py'); r=unittest.TextTestRunner(stream=sys.stdout,verbosity=1).run(s); sys.exit(not r.wasSuccessful())"
        python_stdout=base.execute([sys.executable,'-B','-c',script],target)
        pytests=re.search(r'Ran (\d+) tests?',python_stdout)
        if not pytests or int(pytests.group(1))!=19 or not re.search(r'^OK$',python_stdout,re.M):raise ValueError('Nineteen continuum tests did not pass')
        base.execute([sys.executable,'-B','research/continuous-study.py','verify'],target)
        ca=json.loads(base.execute([sys.executable,'-B','research/audit-continuous-study.py'],target))
        ma=json.loads(base.execute([node,'research/audit-mesh-refinement.js','research/mesh-results'],target))
        if not ca['passed'] or ca['records']!=16 or ca['comparisonCount']!=80 or not all(ca['corruptionNegativeControls'].values()):raise ValueError('Complete independent continuum audit failed')
        if not ma['passed'] or ma['cases']!=72 or not all(ma['corruptionNegativeControls'].values()):raise ValueError('Complete independent mesh audit failed')
        science={name:sha(data) for name,data in payloads.items() if name.startswith(('research/cycle-results/','research/handover-init-results/','research/continuous-results/','research/mesh-results/'))}
        base.execute([node,'research/refinement-analysis.js'],target)
        derived={name:base.digest(target/name)==sha(payloads[name]) for name in ['research/mesh-results/summary.json','research/REFINEMENT_RESULTS.md']}
        if not all(derived.values()):raise ValueError('Derived refinement export did not reproduce byte-exactly')
        scratch=target/'.reproduce';scratch.mkdir()
        base.execute([node,'research/build-refinement-web.js','--output','.reproduce/refinement-data.json'],target)
        if base.digest(scratch/'refinement-data.json')!=sha(payloads['research/mesh-results/web-data.json']):raise ValueError('Refinement web export is not byte-exact')
        smoke=[json.loads(base.execute([node,name],target)) for name in HARNESS]
        if not all(record.get('passed') is True for record in smoke):raise ValueError('Refinement presentation adapter checks did not pass')
        base.execute([sys.executable,'-B','research/build-refinement-figures.py','--output','.reproduce/refinement-figures'],target)
        figures={p.name:base.digest(p)==base.digest(scratch/'refinement-figures'/p.name) for p in (target/'research/refinement-figures').glob('*') if p.suffix in ['.png','.svg']}
        if len(figures)!=8 or not all(figures.values()):raise ValueError('Four new figures in PNG/SVG did not reproduce byte-exactly')
        base.execute([sys.executable,'-B','research/build-refinement-note.py'],target)
        note=reviewed_note(target,NOTE,'output/pdf/refinement-note-checks.json',note_sha,4)
        previous=reviewed_note(target,'output/pdf/handover-init-note.pdf','output/pdf/handover-note-checks.json',V4_SHA,3)
        paper=base.pdf_check(target,V3_SHA)
        routes=json.loads((target/'STATIC_ROUTES.json').read_text(encoding='utf-8'))
        if len(routes)!=86:raise ValueError('Frozen route inventory differs from 86 static paths plus health')
        http=base.http_smoke(target,routes,node)
        http['successfulGetRoutesIncludingHealth']=len(routes)+1
        for name,h in science.items():
            if base.digest(target/name)!=h:raise ValueError('Verification mutated scientific payload '+name)
        restored=base.load_payload(target);repacked=scratch/'repacked.zip';base.zip_payload(repacked,restored)
        if base.digest(repacked)!=base.digest(archive):raise ValueError('Extracted V5 payload did not repack byte-exactly')
        second=scratch/'repacked-extraction';second.mkdir();base.extract_checked(repacked,second)
        return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(payloads),
          'tests':{'nodePassed':8,'pythonPassed':19,'totalPassed':27,'failed':0,'nodeFiles':NODE_TESTS,'pythonFiles':PY_TESTS},
          'continuousAudit':ca,'meshAudit':ma,'inheritedAuditsReranReadOnly':True,
          'derivedByteExact':derived,'webExportByteExact':True,'presentationAdapterChecks':smoke,
          'adapterScope':'Actual module/exporter logic through portable adapters, not layout/human/accessibility validation',
          'figureByteExact':figures,'reviewedNoteRebuiltByteExact':True,'refinementNote':note,
          'preservedInitializerNote':previous,'preservedV3Paper':paper,'http':http,
          'scientificPayloadUnchanged':True,'freshPayloadRepackByteExact':True,'repackedFreshExtractionVerified':True,
          'notRepeated':'No new primary reoptimization or old full learning trace replay; independent auditors recompute the numerical evidence.'}


def plan():
    payloads,routes,_,protected,route=collect()
    value={'scope':'Prospective accepted Goal3 V5 payload inventory; excludes provisional future reset material',
      'builderSourceHash':base.digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'refinementRoute':route,
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
    contents={'scope':'Compact validated continuum/mesh supplement plus closed V4 payload',
      'baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':base.digest(PLAN),
      'files':{name:{**record,'provenance':provenance.get(name,['closed V4 payload or generated V5 instructions/inventory'])} for name,record in inventory(payloads).items()}}
    payloads['PACKAGE_CONTENTS.json']=json_bytes(contents);base.zip_payload(OUT,payloads)
    checks=verify(OUT,note_sha)
    receipt={'archive':OUT.relative_to(ROOT).as_posix(),'sha256':base.digest(OUT),'bytes':OUT.stat().st_size,
      'uncompressedPayloadBytes':sum(map(len,payloads.values())),'seconds':time.perf_counter()-started,
      'builderSourceHash':base.digest(Path(__file__)),'prospectiveInventorySha256':base.digest(PLAN),
      'baseArchive':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':BASE_SHA,'protectedInheritedFiles':protected},
      'refinementRoute':route,'verification':checks}
    RECEIPT.write_bytes(json_bytes(receipt))
    REPORT.write_text('# Refinement delivery verification\n\n'+f"Archive: `{receipt['archive']}`\n\nSHA256: `{receipt['sha256']}`\n\nSize: {receipt['bytes']:,} bytes; {checks['payloadFiles']} files.\n\n"+
      f"Before archive creation the prospective payload inventory was announced at SHA256 `{receipt['prospectiveInventorySha256']}`. The build required an exact inventory match. A fresh extraction passed 27 targeted tests (8 Node + 19 Python), both complete independent audits (16 continuum records/80 comparisons and 72 fully enumerated meshes), and inherited evidence audits read-only. All payload SHA256/CRC checks passed.\n\n"+
      'The descriptive summary/report, graphical export, all four figures in PNG/SVG, and reviewed four-page note regenerated byte-exactly. Actual presentation-module logic passed 800 saved-data views; the real exporter byte-equality check rejected six altered evidence inputs in memory. All 86 closed static routes returned exact payload bytes, plus the health endpoint (87 successful GET paths); missing-route and write-method controls passed. The preserved V4 three-page note and V3 eight-page paper retain their accepted hashes and page checks.\n\n'+
      'Scientific payloads stayed unchanged. The fresh payload repacked into the identical zip and extracted again successfully. Original V4/V3 delivery archives and frozen sources remain preserved. No new primary reoptimization, old full learning trace replay, model game player, paid service, external submission or publication occurred.\n\n'+
      'Portable adapters and HTTP checks do not establish human comprehension, complete accessibility or browser layout; the dedicated QA documents actual developer browser checks and their limitations. Both continuous calculations share the standard Decimal backend. The exact-real continuum and binary64 mesh diagnostics retain their distinct scopes; no finite-grid error constant or incentive stability is inferred.\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    sub.add_parser('plan');build_parser=sub.add_parser('build');build_parser.add_argument('--final-freeze-note-sha',required=True)
    args=parser.parse_args()
    if args.mode=='plan':plan()
    else:build(args.final_freeze_note_sha)
