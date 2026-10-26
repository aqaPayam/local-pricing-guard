"""Build a compact allowlisted Goal-1 evidence delivery; never include old trace trees.

Use `plan` freely. `build --final-freeze-pdf-sha SHA` is reserved for the root's
final freeze after report/UI review. All scientific verification runs in a fresh
temporary extraction. No API, installation, submission or external publication.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, importlib.metadata, json, os, platform, re, shutil
import subprocess, sys, time, urllib.request, urllib.error, zipfile, uuid
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'output/price-guard-cycle-v3.zip'
RESULT = ROOT/'output/cycle-package-verification.json'
REPORT = ROOT/'research/CYCLE_PACKAGE_VERIFICATION.md'
TESTS = ['tests/cycle-game.test.js','tests/cycle-structure.test.js','tests/cycle-audit.test.js']
SCRIPTS = ['cycle-game.js','cycle-study.js','cycle-structure.js','cycle-analysis.js',
           'audit-cycle-study.js','build-cycle-web.js','build-cycle-figures.py',
           'build-cycle-report.py','package-cycle-study.py','demo-server.js']
FORBIDDEN_NAMES = {'.env','auth.json','credentials.json','secrets.json','codex.js',
                   'codex-player.js','codex-adapter.js','llm-runner.js'}
FORBIDDEN_PARTS = {'node_modules','private-pilot','private-pilots','traces'}
MANIFEST_FIELDS = ['sourceHashes','inputHashes','checkpointHashes','oldCheckpointHashes']
MAX_TOTAL_BYTES = 150_000_000

def sha(data): return hashlib.sha256(data).hexdigest()
def digest(file): return sha(Path(file).read_bytes())
def json_bytes(value): return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
def safe_name(name):
    p=PurePosixPath(name)
    if p.is_absolute() or not p.parts or '..' in p.parts or '\\' in name or ':' in name: return False
    if any(part.lower() in FORBIDDEN_PARTS for part in p.parts): return False
    if any(part.lower() in FORBIDDEN_NAMES or part.lower().startswith('.env') for part in p.parts): return False
    if any(word in name.lower() for word in ['codex-adapter','codex-player','llm-runner','private-pilot']): return False
    return True

def rooted(file):
    p=Path(file)
    if not p.is_absolute(): p=ROOT/p
    resolved=p.resolve()
    if not resolved.is_relative_to(ROOT.resolve()): raise ValueError('Dependency escapes workspace: '+str(file))
    name=resolved.relative_to(ROOT.resolve()).as_posix()
    if not safe_name(name): raise ValueError('Forbidden dependency: '+name)
    if not resolved.is_file(): raise FileNotFoundError('Required dependency missing: '+name)
    return resolved,name

def route_map(server):
    # Only literal keys/values in the known closed static map are accepted.
    pairs=re.findall(r"['\"](/[^'\"]*)['\"]\s*:\s*['\"]([^'\"]+)['\"]",server)
    routes={}
    for url,value in pairs:
        file,name=rooted(ROOT/'research'/value)
        if url in routes and routes[url]!=name: raise ValueError('Conflicting static route '+url)
        routes[url]=name
    if not all(key in routes for key in ['/stress','/cycle-data.json','/challenge','/paper-v3']):
        raise ValueError('Expected closed demo routes missing')
    return routes

def collect():
    selected={}; expected={}; queue=[]; provenance={}
    def add(file,reason):
        p,name=rooted(file)
        if name not in selected:
            selected[name]=p; queue.append(name)
        provenance.setdefault(name,set()).add(reason)
        return name
    def dependency(file,hash,reason):
        name=add(file,reason)
        if name in expected and expected[name]!=hash: raise ValueError('Conflicting dependency hashes '+name)
        expected[name]=hash
    for file in SCRIPTS: add('research/'+file,'explicit cycle-stage source')
    for file in TESTS: add(file,'14-test cycle-stage suite')
    for file in (ROOT/'research').glob('CYCLE*.md'):
        if file.name!='CYCLE_PACKAGE_VERIFICATION.md': add(file,'cycle scientific/review document')
    for folder in ['research/cycle-results','research/cycle-figures']:
        for file in (ROOT/folder).rglob('*'):
            if file.is_file(): add(file,'complete new-stage evidence/figure tree')
    for name in ['price-guard-study-v3.pdf','price-guard-study-v3.txt','report-checks-v3.json']:
        add('output/pdf/'+name,'reviewed version-3 report')
    for name in ['.local/stress-v3-desktop.png','.local/stress-v3-narrow.png']:
        add(name,'root developer screenshot evidence; not human validation')
    routes=route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
    for url,name in routes.items(): add(name,'static route '+url)
    i=0
    while i<len(queue):
        name=queue[i]; i+=1; p=selected[name]
        if p.suffix=='.json':
            value=json.loads(p.read_text(encoding='utf-8-sig'))
            if isinstance(value,dict):
                for field in MANIFEST_FIELDS:
                    for file,h in value.get(field,{}).items():
                        dependency(file,h,name+' / '+field)
                        if field=='sourceHashes':
                            snapshot=p.parent/'sources'/file
                            if snapshot.is_file():
                                snap=add(snapshot,'frozen source snapshot '+name)
                                expected[snap]=h
        # Snapshots preserve original bytes, but their relative imports refer to
        # original live locations; executable dependency closure runs there.
        if p.suffix=='.js' and '/sources/' not in name:
            text=p.read_text(encoding='utf-8-sig')
            imports=re.findall(r"\bfrom\s*['\"]([^'\"]+)['\"]",text)
            imports+=re.findall(r"\bimport\s*(?:\(\s*)?['\"]([^'\"]+)['\"]",text)
            for spec in imports:
                if spec.startswith('node:'): continue
                if spec.startswith(('./','../')): add(p.parent/spec,'local module import '+name)
                elif spec.startswith('/'):
                    if spec not in routes: raise ValueError('Unmapped browser module '+spec+' in '+name)
                    add(routes[spec],'browser import '+name)
                else: raise ValueError('Unbundled non-native Node dependency '+spec+' in '+name)
    for name,h in expected.items():
        if digest(selected[name])!=h: raise ValueError('Frozen dependency drift '+name)
    total=sum(p.stat().st_size for p in selected.values())
    if total>MAX_TOTAL_BYTES: raise ValueError('Unexpectedly large stage package: '+str(total))
    return selected,routes,{k:sorted(v) for k,v in provenance.items()}

def instructions():
    return """PRICE GUARD: COORDINATED FINITE-GAME AUDIT — VERSION 3

Start with output/pdf/price-guard-study-v3.pdf and research/CYCLE_RESULTS.md.
This is a compact standalone supplement. It includes every new-stage case and
all hashed input/source/checkpoint dependencies needed for its own audit. Old
multi-gigabyte learning trace trees and earlier zip archives are intentionally
absent. No old long training/evaluation replay is claimed by this package.

Node.js24+ is sufficient for the game, tests, complete new audit and analysis:
  node research/demo-server.js
  Open http://127.0.0.1:3003/stress  (or /challenge for the human game).
  node --test --test-isolation=none tests/cycle-game.test.js tests/cycle-structure.test.js tests/cycle-audit.test.js
  node research/audit-cycle-study.js research/cycle-results
  node research/cycle-study.js verify
  node research/cycle-analysis.js
The audit is read-only unless an explicit --output path is supplied. Analysis
rewrites only derived summary/results; original cases and certificates stay put.

Optional Python figures/report rebuilding needs numpy, matplotlib, reportlab,
pypdf and Pillow. No Python installation is needed to play or audit with Node.
  python research/build-cycle-figures.py --output reproduced-figures
  python research/build-cycle-report.py
  node research/build-cycle-web.js --output reproduced-web-data.json

PACKAGE_CONTENTS.json records SHA256 and size for every payload except itself.
The external cycle-package-verification.json records fresh-extraction checks.
The package builder can recreate this zip from a full extracted payload:
  python research/package-cycle-study.py repack EXTRACTED_DIRECTORY OUTPUT.zip

The joint optimizer deliberately replaces learners and measures feasible
capacity; it does not demonstrate emergent collusion, equilibrium or unilateral
incentive stability. Numerical certificates use floating computed weights.
Separate AI-agent reviews are not independent human validation. No API player,
network model call, payment, external submission or publication is performed.
"""

def generated_payloads(routes):
    package={'name':'price-guard-cycle-audit','private':True,'version':'3.0.0','type':'module',
             'engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js',
             'test':'node --test --test-isolation=none '+' '.join(TESTS),
             'audit':'node research/audit-cycle-study.js research/cycle-results',
             'verify':'node research/cycle-study.js verify','analyze':'node research/cycle-analysis.js'}}
    return {'package.json':json_bytes(package),'START-HERE.txt':instructions().encode('utf-8'),
            'README.md':('# Price Guard cycle-audit evidence\n\n'+instructions()).encode('utf-8'),
            'requirements-cycle.txt':b'numpy\nmatplotlib\nreportlab\npypdf\nPillow\n',
            'STATIC_ROUTES.json':json_bytes(routes)}

def zip_payload(destination,payloads):
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(payloads.items()):
            if not safe_name(name): raise ValueError('Unsafe archive name '+name)
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)

def load_payload(directory):
    manifest=json.loads((directory/'PACKAGE_CONTENTS.json').read_text(encoding='utf-8'))
    payloads={}
    for name,record in manifest['files'].items():
        if not safe_name(name): raise ValueError('Unsafe manifested path')
        file=(directory/name).resolve()
        if not file.is_relative_to(directory.resolve()): raise ValueError('Manifest path escape')
        data=file.read_bytes()
        if sha(data)!=record['sha256'] or len(data)!=record['bytes']: raise ValueError('Payload hash mismatch '+name)
        payloads[name]=data
    payloads['PACKAGE_CONTENTS.json']=(directory/'PACKAGE_CONTENTS.json').read_bytes()
    return payloads

def extract_checked(archive,directory):
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        if len(names)!=len(set(names)): raise ValueError('Duplicate archive entries')
        for name in names:
            if not safe_name(name) or not (directory/name).resolve().is_relative_to(directory.resolve()): raise ValueError('Archive traversal')
        bad=z.testzip()
        if bad: raise ValueError('CRC mismatch '+bad)
        z.extractall(directory)
    payloads=load_payload(directory)
    if set(names)!=set(payloads): raise ValueError('Unmanifested archive members')
    return payloads

def execute(args,cwd,timeout=180):
    p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',
                     timeout=timeout,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if p.returncode: raise RuntimeError('Command failed: '+' '.join(map(str,args))+'\n'+p.stdout+'\n'+p.stderr)
    return p.stdout

def pdf_check(directory,expected):
    try: from pypdf import PdfReader
    except ImportError:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'
        if bundled.is_dir(): sys.path.append(str(bundled))
        from pypdf import PdfReader
    file=directory/'output/pdf/price-guard-study-v3.pdf';data=file.read_bytes()
    if sha(data)!=expected: raise ValueError('Reviewed PDF hash mismatch')
    checks=json.loads((directory/'output/pdf/report-checks-v3.json').read_text(encoding='utf-8'))
    reader=PdfReader(str(file));texts=[p.extract_text() for p in reader.pages]
    body=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t))
    abstract=re.search(r'\bAbstract\s+(.*?)\n1 Introduction',texts[0],re.S)
    if not abstract: raise ValueError('Actual PDF abstract not located')
    words=len(abstract.group(1).split())
    normalized=lambda s:' '.join(s.split())
    if normalized(abstract.group(1))!=normalized(checks['abstractText']): raise ValueError('Actual PDF abstract differs from report checks')
    result={'sha256':expected,'bytes':len(data),'pages':len(texts),'bodyPages':body,'abstractWords':words,
            'ethicalAppendix':any('Limitations and Dual-Use / Ethical Considerations' in t for t in texts),
            'llmUsageStatement':any('LLM Usage Statement' in t for t in texts),'authorVerified':'Mohammadpayam Teabi' in texts[0]}
    if result['pages']!=8 or body!=6 or words!=188 or not all(result[k] for k in ['ethicalAppendix','llmUsageStatement','authorVerified']): raise ValueError('Reviewed PDF structural requirements failed')
    if checks['sha256']!=expected or checks['bytes']!=len(data): raise ValueError('Stored PDF checks drift')
    return result

def http_smoke(directory,routes,node):
    script="import {createDemoServer} from './research/demo-server.js';const s=createDemoServer();s.listen(0,'127.0.0.1',()=>console.log(s.address().port));"
    p=subprocess.Popen([node,'--input-type=module','-e',script],cwd=directory,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                       text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        line=p.stdout.readline().strip()
        if not line.isdigit(): raise RuntimeError('Extracted local demo did not start: '+line)
        base='http://127.0.0.1:'+line;checked={}
        for url,name in routes.items():
            with urllib.request.urlopen(base+url,timeout=10) as response:
                data=response.read();expected=(directory/name).read_bytes()
                if response.status!=200 or sha(data)!=sha(expected): raise ValueError('Static route body mismatch '+url)
                if url.endswith('.js') and not response.headers.get('Content-Type','').startswith('text/javascript'): raise ValueError('Module MIME mismatch '+url)
                checked[url]={'status':response.status,'bytes':len(data),'sha256':sha(data)}
        with urllib.request.urlopen(base+'/health',timeout=10) as response:
            if response.status!=200: raise ValueError('Health route failed')
        for url,method,expected_status in [('/not-a-real-route','GET',404),('/stress','POST',405)]:
            try: urllib.request.urlopen(urllib.request.Request(base+url,method=method),timeout=10)
            except urllib.error.HTTPError as error:
                if error.code!=expected_status: raise
            else: raise ValueError('Read-only/closed-route negative control failed')
        return {'staticRoutes':len(checked),'allBodiesMatchPayload':True,'health':200,'unknownRoute':404,'writeMethod':405,'routes':checked}
    finally:
        p.terminate()
        try: p.wait(timeout=10)
        except subprocess.TimeoutExpired: p.kill();p.wait(timeout=10)

@contextmanager
def verification_workspace():
    parent=(ROOT/'.local').resolve();parent.mkdir(exist_ok=True)
    target=parent/('cycle-evidence-'+uuid.uuid4().hex)
    # Ordinary mkdir inherits the workspace ACL. Python's Windows mkdtemp uses
    # a restrictive DACL that is incompatible with this host's restricted token.
    target.mkdir()
    try:
        if not target.resolve().is_relative_to(parent) or not target.name.startswith('cycle-evidence-'):
            raise ValueError('Unexpected verification workspace')
        yield target
    finally:
        resolved=target.resolve()
        if not resolved.is_relative_to(parent) or not resolved.name.startswith('cycle-evidence-'):
            raise ValueError('Unsafe recursive cleanup scope')
        shutil.rmtree(resolved)

def verify_delivery(archive,expected_pdf,skip_python=False):
    node=shutil.which('node')
    if not node: raise RuntimeError('Node.js24+ required for fresh verification')
    version=execute([node,'--version'],ROOT).strip()
    if int(version.lstrip('v').split('.')[0])<24: raise RuntimeError('Node24+ required')
    with verification_workspace() as target:
        payloads=extract_checked(archive,target)
        output=execute([node,'--test','--test-isolation=none','--test-reporter=tap',*TESTS],target)
        count=re.search(r'^# tests (\d+)$',output,re.M);failed=re.search(r'^# fail (\d+)$',output,re.M)
        if not count or int(count.group(1))!=14 or not failed or int(failed.group(1))!=0: raise ValueError('Expected14 passing cycle tests')
        execute([node,'research/cycle-study.js','verify'],target)
        audit=json.loads(execute([node,'research/audit-cycle-study.js','research/cycle-results'],target))
        if not audit['passed'] or audit['cases']!=24 or audit['objectives']!=48 or not all(audit['corruptionNegativeControls'].values()): raise ValueError('Fresh full cycle audit failed')
        scientific_before={name:sha(data) for name,data in payloads.items() if name.startswith('research/cycle-results/')}
        execute([node,'research/cycle-analysis.js'],target)
        derived_exact={name:digest(target/name)==sha(payloads[name]) for name in ['research/cycle-results/summary.json','research/CYCLE_RESULTS.md']}
        if not all(derived_exact.values()): raise ValueError('Derived evidence did not regenerate byte-exactly')
        web=target/'.reproduce/web-data.json';web.parent.mkdir(exist_ok=True)
        execute([node,'research/build-cycle-web.js','--output','.reproduce/web-data.json'],target)
        web_exact=digest(web)==sha(payloads['research/cycle-results/web-data.json'])
        if not web_exact: raise ValueError('Display data did not regenerate byte-exactly')
        figures={};report_rebuilt=False
        if not skip_python:
            execute([sys.executable,'research/build-cycle-figures.py','--output','.reproduce/figures'],target)
            for original in sorted((target/'research/cycle-figures').glob('*')):
                if original.suffix in ['.png','.svg']:
                    figures[original.name]=digest(original)==digest(target/'.reproduce/figures'/original.name)
            if len(figures)!=6 or not all(figures.values()): raise ValueError('Expected six byte-exact PNG/SVG figures')
            execute([sys.executable,'research/build-cycle-report.py'],target)
            report_rebuilt=digest(target/'output/pdf/price-guard-study-v3.pdf')==expected_pdf
            if not report_rebuilt: raise ValueError('PDF rebuild differs from reviewed PDF')
        pdf=pdf_check(target,expected_pdf);routes=json.loads((target/'STATIC_ROUTES.json').read_text(encoding='utf-8'))
        http=http_smoke(target,routes,node)
        for name,h in scientific_before.items():
            if digest(target/name)!=h: raise ValueError('Verification mutated original scientific payload '+name)
        # Repack only manifested payloads; verification scratch files never enter delivery.
        restored=load_payload(target);repacked=target/'.reproduce/repacked.zip';zip_payload(repacked,restored)
        if digest(repacked)!=digest(archive): raise ValueError('Fresh extracted payload does not repack byte-exactly')
        second=target/'.reproduce/repacked-extraction';second.mkdir();extract_checked(repacked,second)
        return {'passed':True,'nodeVersion':version,'pythonVersion':platform.python_version(),
                'payloadFiles':len(payloads),'payloadHashesAndCRC':True,'tests':{'passed':14,'failed':0},
                'freshCycleAudit':audit,'originalScientificPayloadUnchanged':True,'derivedByteExact':derived_exact,
                'displayExportByteExact':web_exact,'figureByteExact':figures,'reportRebuiltByteExact':report_rebuilt,
                'pythonRebuildSkipped':skip_python,'reviewedPDF':pdf,'http':http,
                'freshPayloadRepackByteExact':True,'repackedArchiveFreshExtractionVerified':True}

def build(expected_pdf,skip_python=False):
    if not re.fullmatch('[0-9a-f]{64}',expected_pdf): raise ValueError('Root-reviewed PDF SHA256 required')
    t=time.perf_counter();selected,routes,provenance=collect()
    if digest(ROOT/'output/pdf/price-guard-study-v3.pdf')!=expected_pdf: raise ValueError('Final freeze PDF hash drift')
    payloads={name:p.read_bytes() for name,p in selected.items()};payloads.update(generated_payloads(routes))
    manifest={'scope':'Compact standalone cycle-stage evidence; old trace trees excluded',
              'files':{name:{'sha256':sha(data),'bytes':len(data),'provenance':provenance.get(name,['generated package instructions'])} for name,data in sorted(payloads.items())}}
    payloads['PACKAGE_CONTENTS.json']=json_bytes(manifest);OUT.parent.mkdir(exist_ok=True);zip_payload(OUT,payloads)
    verification=verify_delivery(OUT,expected_pdf,skip_python)
    result={'archive':OUT.relative_to(ROOT).as_posix(),'sha256':digest(OUT),'bytes':OUT.stat().st_size,
            'uncompressedPayloadBytes':sum(len(data) for data in payloads.values()),'seconds':time.perf_counter()-t,
            'builderSourceHash':digest(Path(__file__)),'verification':verification}
    RESULT.write_bytes(json_bytes(result))
    REPORT.write_text('# Standalone cycle-stage package verification\n\n'
        f"Archive: `{result['archive']}`\n\nSHA256: `{result['sha256']}`\n\n"
        f"Size: {result['bytes']:,} bytes; {verification['payloadFiles']} manifested files.\n\n"
        'A fresh temporary extraction passed every payload SHA256 and ZIP CRC check, all14 cycle tests, '
        'and one complete independent cycle audit. All24 graphs/48 objectives, all-start witnesses, '
        'numerical cycle bounds and finite-horizon certificates were checked again. Original scientific payloads stayed unchanged.\n\n'
        'The derived analysis and display export regenerated byte-exactly. '
        +( 'All three PNG/SVG figures and the reviewed PDF rebuilt byte-exactly.\n\n' if not skip_python else 'Optional Python figure/PDF rebuilding was skipped and is not claimed.\n\n')
        +f"Reviewed PDF:8 total pages,6 body pages,188-word actual extracted abstract; SHA256 `{expected_pdf}`.\n\n"
        f"All {verification['http']['staticRoutes']} declared static routes returned exact packaged bytes; health returned200, unknown routes404 and writes405. "
        'These are developer checks, not human comprehension evidence. The fresh payload repacked into the identical archive and extracted again successfully.\n\n'
        'This compact package includes the256 saved terminal checkpoints and all manifest/derived-input dependencies. '
        'It excludes old multi-gigabyte trace trees and zip archives. No old full learning replay, external submission, publication, API player or paid service was performed. '
        'Version2 files remain preserved.\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['archive','bytes','sha256','seconds']}))

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    sub.add_parser('plan');b=sub.add_parser('build');b.add_argument('--final-freeze-pdf-sha',required=True);b.add_argument('--skip-python-rebuild',action='store_true')
    r=sub.add_parser('repack');r.add_argument('extracted');r.add_argument('destination')
    args=parser.parse_args()
    if args.mode=='plan':
        files,routes,_=collect();print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files.values()),'routes':len(routes),'createsArchive':False}))
    elif args.mode=='build': build(args.final_freeze_pdf_sha,args.skip_python_rebuild)
    else:
        extracted=Path(args.extracted).resolve();destination=Path(args.destination).resolve()
        if destination.is_relative_to(extracted): raise ValueError('Repacked destination must be outside extracted payload')
        zip_payload(destination,load_payload(extracted));print(json.dumps({'archive':str(destination),'sha256':digest(destination)}))

if __name__=='__main__':main()
