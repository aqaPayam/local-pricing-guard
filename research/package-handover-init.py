"""Compact V4 initializer supplement, inheriting the verified standalone V3 payload.

`plan` is read-only; `build` requires the root-reviewed technical-note hash after
ROOTGOAL2FINALFREEZE. Checks run only in a fresh inherited-permission extraction.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, shutil, sys, time, zipfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'output/price-guard-cycle-v3.zip'
BASE_SHA='1565ae1c5b30d69db300e2d914dbf9a9126a659935fc1bf1b42bdd4b82bf9c46'
V3_PDF_SHA='2c13cd18f85ce1e3dd42f2b93480d6b9a3412d564d16ac2102a581ca14fa5857'
OUT=ROOT/'output/price-guard-handover-v4.zip'
RECEIPT=ROOT/'output/handover-package-verification.json'
REPORT=ROOT/'research/HANDOVER_INIT_PACKAGE_VERIFICATION.md'
NOTE='output/pdf/handover-init-note.pdf'
TESTS=['tests/handover-init.test.js','tests/handover-init-audit.test.js']
UI_SMOKE='.local/handover-display-smoke.mjs'
SCRIPTS=['handover-init.js','handover-init-analysis.js','audit-handover-init.js',
         'build-handover-web.js','build-handover-figures.py','build-handover-note.py',
         'package-handover-init.py','demo-server.js']
spec=importlib.util.spec_from_file_location('cycle_package',ROOT/'research/package-cycle-study.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha=base.sha;json_bytes=base.json_bytes

def base_payloads():
    if base.digest(BASE)!=BASE_SHA: raise ValueError('Reviewed V3 archive changed')
    with zipfile.ZipFile(BASE) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or archive.testzip(): raise ValueError('V3 ZIP inventory/CRC failed')
        if any(not base.safe_name(name) for name in names): raise ValueError('Unsafe V3 name')
        payloads={name:archive.read(name) for name in names}
    manifest=json.loads(payloads.pop('PACKAGE_CONTENTS.json'))
    if set(manifest['files'])!=set(payloads): raise ValueError('V3 payload inventory mismatch')
    for name,record in manifest['files'].items():
        if sha(payloads[name])!=record['sha256'] or len(payloads[name])!=record['bytes']: raise ValueError('V3 payload hash mismatch '+name)
    return payloads

def collect():
    payloads=base_payloads();original=dict(payloads);queue=[];provenance={};expected={}
    primary_manifest=json.loads(payloads['research/cycle-results/manifest.json'])
    protected=set(primary_manifest['sourceHashes'])
    protected.update(name for name in payloads if name.startswith('research/cycle-results/'))
    protected.add('output/pdf/price-guard-study-v3.pdf')
    def add(file,reason):
        p,name=base.rooted(file);data=p.read_bytes()
        if name in protected and data!=original[name]: raise ValueError('Goal1 frozen scientific payload changed '+name)
        if name not in provenance: queue.append(name)
        payloads[name]=data;provenance.setdefault(name,set()).add(reason)
        return name
    for name in SCRIPTS: add('research/'+name,'explicit initializer-stage source')
    for name in TESTS: add(name,'initializer and independent-audit synthetic tests')
    add(UI_SMOKE,'dependency-free activation DOM-adapter logic smoke; not layout/human validation')
    for file in (ROOT/'research').glob('HANDOVER*.md'):
        if file.name!='HANDOVER_INIT_PACKAGE_VERIFICATION.md': add(file,'initializer scientific/review/QA document')
    for folder in ['research/handover-init-results','research/handover-figures']:
        for file in (ROOT/folder).rglob('*'):
            if file.is_file(): add(file,'complete new initializer evidence/figures')
    for name in ['handover-init-note.pdf','handover-init-note.txt','handover-note-checks.json']:
        add('output/pdf/'+name,'reviewed standalone technical note; V3 paper preserved')
    # Optional developer screenshot evidence; only explicit activation QA names.
    for pattern in ['activation-*.png','handover-activation-*.png']:
        for file in (ROOT/'.local').glob(pattern): add(file,'activation developer screenshot evidence')
    routes=base.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
    for url,name in routes.items(): add(name,'current closed static route '+url)
    i=0
    while i<len(queue):
        name=queue[i];i+=1;data=payloads[name];p=ROOT/name
        if p.suffix=='.json':
            value=json.loads(data.decode('utf-8-sig'))
            if isinstance(value,dict):
                for field in base.MANIFEST_FIELDS:
                    for dependency,h in value.get(field,{}).items():
                        dep=add(dependency,name+' / '+field);expected[dep]=h
                        if field=='sourceHashes':
                            snapshot=p.parent/'sources'/dependency
                            if snapshot.is_file(): expected[add(snapshot,'frozen snapshot '+name)]=h
        if p.suffix in ['.js','.mjs'] and '/sources/' not in name:
            text=data.decode('utf-8-sig')
            # Match actual declaration-shaped statements, not ordinary UI copy
            # such as "from '" next to a template concatenation.
            imports=re.findall(r"(?:^|[;\n])\s*(?:import|export)\s+(?:[^;'\"]+?\s+from\s*)?['\"]([^'\"\n]+)['\"]",text,re.M)
            imports+=re.findall(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]",text)
            for dependency in imports:
                if dependency.startswith('node:'): continue
                if dependency.startswith(('./','../')): add(p.parent/dependency,'local import '+name)
                elif dependency.startswith('/'):
                    if dependency not in routes: raise ValueError('Unmapped browser import '+dependency)
                    add(routes[dependency],'browser import '+name)
                else: raise ValueError('Unbundled non-native import '+dependency)
    for name,h in expected.items():
        if sha(payloads[name])!=h: raise ValueError('Frozen dependency drift '+name)
    for name in protected:
        if payloads[name]!=original[name]: raise ValueError('Inherited science drift '+name)
    total=sum(map(len,payloads.values()))
    if total>180_000_000: raise ValueError('Unexpected large V4 payload')
    return payloads,routes,{name:sorted(reasons) for name,reasons in provenance.items()},len(protected)

def instructions(activation_route):
    return f"""PRICE GUARD — ONE REAL CAPPED EXECUTION AT HANDOVER (V4)

Read output/pdf/handover-init-note.pdf, a separate three-page technical research
note. The reviewed V3 main paper remains output/pdf/price-guard-study-v3.pdf.
The package contains the complete reviewed V3 payload plus the initializer
follow-up; old multi-gigabyte learning trace trees are not included or replayed.

Node.js24+ (no packages, API accounts or model players needed):
  node research/demo-server.js
  Open http://127.0.0.1:3003{activation_route}  (or /stress, /challenge).
  node --test --test-isolation=none {' '.join(TESTS)}
  node research/audit-handover-init.js research/handover-init-results
  node research/handover-init.js verify
  node research/handover-init-analysis.js
  node {UI_SMOKE}
The new auditor also reruns the inherited cycle audit read-only. The UI smoke
uses a DOM adapter for module logic; it is not browser layout or human testing.

Optional figures/note rebuilding needs numpy, matplotlib, reportlab, pypdf and
Pillow. These commands use local saved evidence only:
  python research/build-handover-figures.py --output reproduced-handover-figures
  python research/build-handover-note.py
  node research/build-handover-web.js --output reproduced-handover-data.json

All40 labels, failures and already-safe cases remain visible. Displayed
guarantees use the requested target minus the fixed numerical allowance.
Largest prefix caps are optimal only within common prefix caps. Protection is
long-run for this known finite guard, not a higher-target finite-time promise,
human validation, new general shielding algorithm or incentive-equilibrium test.

PACKAGE_CONTENTS.json hashes every payload except itself. The external
handover-package-verification.json documents fresh extraction and replay.
To reproduce the zip from an intact extracted payload without the V3 zip:
  python research/package-cycle-study.py repack EXTRACTED_DIRECTORY OUTPUT.zip
No external submission, publication, paid service or new model call is performed.
"""

def generate(payloads,routes):
    activation=next((url for url,name in routes.items() if name=='research/demo/activation.html'),None)
    if not activation: raise ValueError('Activation route not yet frozen')
    payloads['README-v3.md']=payloads['README.md']
    payloads['README.md']=('# Guard activation initializer audit\n\n'+instructions(activation)).encode()
    payloads['START-HERE.txt']=instructions(activation).encode()
    package={'name':'price-guard-handover-initializer','private':True,'version':'4.0.0','type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js','test':'node --test --test-isolation=none '+' '.join(TESTS),'audit':'node research/audit-handover-init.js research/handover-init-results','verify':'node research/handover-init.js verify','analyze':'node research/handover-init-analysis.js','test:ui':'node '+UI_SMOKE}}
    payloads['package.json']=json_bytes(package);payloads['STATIC_ROUTES.json']=json_bytes(routes)
    return activation

def note_check(directory,expected):
    try: from pypdf import PdfReader
    except ImportError:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'
        if bundled.is_dir(): sys.path.append(str(bundled))
        from pypdf import PdfReader
    file=directory/NOTE;checks=json.loads((directory/'output/pdf/handover-note-checks.json').read_text(encoding='utf-8'))
    if base.digest(file)!=expected or checks.get('sha256')!=expected: raise ValueError('Reviewed initializer note hash differs')
    reader=PdfReader(str(file));texts=[p.extract_text() for p in reader.pages]
    if len(texts)!=3 or checks.get('pages')!=3 or 'Mohammadpayam Teabi' not in '\n'.join(texts): raise ValueError('Three-page reviewed technical-note checks failed')
    return {'sha256':expected,'bytes':file.stat().st_size,'pages':3,'authorVerified':True,'kind':'Separate technical research note; V3 paper retained'}

def verify(archive,note_sha):
    node=shutil.which('node')
    if not node: raise RuntimeError('Node24+ required')
    with base.verification_workspace() as target:
        payloads=base.extract_checked(archive,target)
        output=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*TESTS],target)
        tests=re.search(r'^# tests (\d+)$',output,re.M);fail=re.search(r'^# fail (\d+)$',output,re.M)
        if not tests or int(tests.group(1))<13 or not fail or int(fail.group(1))!=0: raise ValueError('Initializer test inventory or results failed')
        base.execute([node,'research/handover-init.js','verify'],target)
        audit=json.loads(base.execute([node,'research/audit-handover-init.js','research/handover-init-results'],target))
        if not audit['passed'] or audit['labels']!=40 or audit['scenarios']!=8 or not all(audit['corruptionNegativeControls'].values()): raise ValueError('Complete initializer audit failed')
        science={name:sha(data) for name,data in payloads.items() if name.startswith(('research/cycle-results/','research/handover-init-results/'))}
        base.execute([node,'research/handover-init-analysis.js'],target)
        derived={name:base.digest(target/name)==sha(payloads[name]) for name in ['research/handover-init-results/summary.json','research/HANDOVER_INIT_RESULTS.md']}
        if not all(derived.values()): raise ValueError('Initializer descriptive export changed on reproduction')
        scratch=target/'.reproduce';scratch.mkdir()
        base.execute([node,'research/build-handover-web.js','--output','.reproduce/handover-web.json'],target)
        web_exact=base.digest(scratch/'handover-web.json')==sha(payloads['research/handover-init-results/web-data.json'])
        if not web_exact: raise ValueError('Activation export is not byte-exact')
        smoke_output=base.execute([node,UI_SMOKE],target)
        try: smoke=json.loads(smoke_output)
        except json.JSONDecodeError: smoke={'successfulExit':True,'stdout':smoke_output.strip()}
        base.execute([sys.executable,'research/build-handover-figures.py','--output','.reproduce/handover-figures'],target)
        figures={file.name:base.digest(file)==base.digest(scratch/'handover-figures'/file.name) for file in (target/'research/handover-figures').glob('*') if file.suffix in ['.png','.svg']}
        if len(figures)!=4 or not all(figures.values()): raise ValueError('Two new figures in PNG/SVG did not reproduce byte-exactly')
        base.execute([sys.executable,'research/build-handover-note.py'],target)
        note=note_check(target,note_sha);paper=base.pdf_check(target,V3_PDF_SHA)
        routes=json.loads((target/'STATIC_ROUTES.json').read_text(encoding='utf-8'))
        http=base.http_smoke(target,routes,node)
        for name,h in science.items():
            if base.digest(target/name)!=h: raise ValueError('Verification mutated scientific payload '+name)
        restored=base.load_payload(target);repacked=scratch/'repacked.zip';base.zip_payload(repacked,restored)
        if base.digest(repacked)!=base.digest(archive): raise ValueError('V4 extracted payload failed byte-exact repack')
        second=scratch/'repacked-extraction';second.mkdir();base.extract_checked(repacked,second)
        return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(payloads),'tests':{'passed':int(tests.group(1)),'failed':0,'files':TESTS},'initializerAudit':audit,'inheritedCycleAuditReranReadOnly':True,'derivedByteExact':derived,'activationExportByteExact':web_exact,'uiSmoke':smoke,'uiSmokeScope':'Dependency-free DOM-adapter module logic, not browser layout or human testing','figureByteExact':figures,'technicalNoteRebuiltByteExact':True,'technicalNote':note,'preservedV3Paper':paper,'http':http,'scientificPayloadUnchanged':True,'freshPayloadRepackByteExact':True,'repackedFreshExtractionVerified':True}

def build(note_sha):
    if not re.fullmatch('[0-9a-f]{64}',note_sha): raise ValueError('Root-reviewed technical-note SHA required')
    started=time.perf_counter();payloads,routes,provenance,protected=collect()
    if sha(payloads[NOTE])!=note_sha: raise ValueError('Final reviewed note changed')
    activation=generate(payloads,routes)
    manifest={'scope':'Compact V4 initializer supplement plus preserved reviewed V3 payload','baseArchiveSha256':BASE_SHA,'files':{name:{'sha256':sha(data),'bytes':len(data),'provenance':provenance.get(name,['verified V3 payload or generated V4 instructions'])} for name,data in sorted(payloads.items())}}
    payloads['PACKAGE_CONTENTS.json']=json_bytes(manifest);base.zip_payload(OUT,payloads);checks=verify(OUT,note_sha)
    receipt={'archive':OUT.relative_to(ROOT).as_posix(),'sha256':base.digest(OUT),'bytes':OUT.stat().st_size,'uncompressedPayloadBytes':sum(map(len,payloads.values())),'seconds':time.perf_counter()-started,'builderSourceHash':base.digest(Path(__file__)),'baseArchive':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':BASE_SHA,'protectedScientificFiles':protected},'activationRoute':activation,'verification':checks};RECEIPT.write_bytes(json_bytes(receipt))
    REPORT.write_text('# Initializer supplement package verification\n\n'+f"Archive: `{receipt['archive']}`\n\nSHA256: `{receipt['sha256']}`\n\nSize: {receipt['bytes']:,} bytes; {checks['payloadFiles']} files.\n\n"+f"A fresh extraction passed all {checks['tests']['passed']} initializer tests and the full 40-label independent audit, including the inherited cycle audit read-only. All payload hashes/CRC passed. The derived summary and activation export regenerated byte-exactly, the actual UI module passed its DOM-adapter smoke, and both new PNG/SVG figures plus the reviewed three-page technical note rebuilt byte-exactly.\n\n"+f"The V3 paper remains SHA256 `{V3_PDF_SHA}` with eight total pages, six body pages and an actual 188-word abstract. All {checks['http']['staticRoutes']} static routes returned exact packaged bytes, closed-route/write controls passed, original scientific payloads stayed unchanged, and the extracted payload repacked into the identical archive and extracted again.\n\n"+'DOM-adapter and HTTP checks do not establish browser layout, human comprehension, accessibility coverage or incentive stability. Dedicated developer QA records their actual limits and any wrapper error. All 40 labels and already-safe cases remain visible. This is a known finite-graph long-run initializer supplement, not a higher-floor finite-time promise. No old full learning replay, paid API, external submission or publication was performed. V3 archive and frozen evidence remain preserved.\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True);sub.add_parser('plan');b=sub.add_parser('build');b.add_argument('--final-freeze-note-sha',required=True);args=parser.parse_args()
    if args.mode=='plan':
        payloads,routes,_,protected=collect();print(json.dumps({'files':len(payloads),'bytes':sum(map(len,payloads.values())),'routes':len(routes),'protectedInheritedScientificFiles':protected,'createsArchive':False}))
    else:build(args.final_freeze_note_sha)
if __name__=='__main__':main()
