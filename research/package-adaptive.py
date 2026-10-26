"""Streaming V9 research delivery; a prospective inventory precedes the archive.

This builder never trains a learner. Full extracted checkpoint/graph/probe audits
are separate from complete training replay, which is not claimed.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, shutil, sys, time, uuid, zipfile
_stream_spec=importlib.util.spec_from_file_location('delivery_streaming',Path(__file__).with_name('evidence_streaming.py'))
stream=importlib.util.module_from_spec(_stream_spec);_stream_spec.loader.exec_module(stream)

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'output/price-guard-incentive-v8.zip'
BASE_SHA='328ca453295b228ec5975ae9264265cf3a89b34ca4d3d3e8d5de972db637d0dc'
OUT=ROOT/'output/price-guard-adaptive-v9.zip'
PLAN=ROOT/'output/adaptive-package-plan.json'
RECEIPT=ROOT/'output/adaptive-package-verification.json'
REPORT=ROOT/'research/ADAPTIVE_PACKAGE_VERIFICATION.md'
PDF='output/pdf/local-guard-welfare-report.pdf'
NODE_TESTS=['tests/adaptive-learning.test.js','tests/adaptive-bootstrap.test.js']
PY_TESTS=['tests/test_adaptive_learning_audit.py','tests/test_evidence_streaming.py']
HARNESSES=['.local/adaptive-display-smoke.mjs','.local/adaptive-export-smoke.mjs']
SCRIPTS=['adaptive-learning.js','adaptive-bootstrap.js','adaptive-analysis.js','audit-adaptive-learning.py',
 'build-adaptive-web.js','build-capacity-figures.py','build-main-report.py','evidence_streaming.py','package-adaptive.py','demo-server.js']
DOCS=['ADAPTIVE_LEARNING_PROTOCOL.md','ADAPTIVE_ANALYSIS_CONTRACT.md','ADAPTIVE_WEB_SCHEMA.md',
 'ADAPTIVE_LEARNING_RESULTS.md','ADAPTIVE_LEARNING_REVIEW.md','ADAPTIVE_REPLAY_QA.md',
 'INCENTIVE_PACKAGE_VERIFICATION.md','README.md','README-v8.md','README_PRESERVATION_GOAL7.json']
spec=importlib.util.spec_from_file_location('prior_delivery',ROOT/'research/package-incentive.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base=prior.base
json_bytes=base.json_bytes
digest=lambda p:stream.digest_file(p)['sha256']


def rooted(name):
    p=Path(name);p=p if p.is_absolute() else ROOT/p;p=p.resolve()
    if not p.is_relative_to(ROOT):raise ValueError('Source escapes workspace')
    return p,p.relative_to(ROOT).as_posix()


def collect():
    if digest(BASE)!=BASE_SHA:raise ValueError('Closed V8 archive changed')
    with zipfile.ZipFile(BASE) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or any(not stream.safe_name(n) for n in names):raise ValueError('Unsafe inherited inventory')
        inherited=json.loads(z.read('PACKAGE_CONTENTS.json'))['files']
        if set(names)!=set(inherited)|{'PACKAGE_CONTENTS.json'}:raise ValueError('Inherited unmanifested member')
    sources={n:{'kind':'zip','archive':BASE,'member':n} for n in inherited}
    mutable={'README.md','START-HERE.txt','package.json','STATIC_ROUTES.json','DELIVERY_FREEZE.json','research/demo-server.js','research/demo/overview.html'}
    protected=set(sources)-mutable;provenance={};expected={}
    def add(name,reason):
        p,n=rooted(name)
        # This one historic candidate is an explicit frozen primary hash input.
        # Its inclusion records provenance; it is not a new accepted result.
        inherited_candidate=n=='research/ORDER_ENVELOPE_CANDIDATE.md'
        if any(word in n for word in ['CANDIDATE','private-pilot','codex-adapter']) and not inherited_candidate:raise ValueError('Unrequested candidate/private material '+n)
        observed=stream.digest_file(p)
        if n in protected and any(observed[k]!=inherited[n][k] for k in ['sha256','bytes']):raise ValueError('Closed V8 payload changed '+n)
        sources[n]={'kind':'file','path':p};provenance.setdefault(n,set()).add(reason)
        if inherited_candidate:provenance[n].add('Historical candidate retained only as an exact frozen primary provenance dependency; not accepted Goal7 science')
        return n
    for name in SCRIPTS:add('research/'+name,'accepted Goal7 source and delivery tooling')
    for name in DOCS:add('research/'+name,'accepted methods/results/review/navigation')
    for name in NODE_TESTS+PY_TESTS+HARNESSES:add(name,'synthetic or read-only developer verification')
    for name in ['README.md','README-before-goal7.md']:add(name,'current entry or explicitly preserved distinct workspace original')
    add('research/adaptive-bootstrap-indices.json','pre-outcome whole-seed resample matrix')
    add('output/incentive-package-verification.json','verified V8 delivery receipt')
    for folder in ['research/adaptive-learning-results','research/adaptive-learning-audit-provenance','research/capacity-figures']:
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file():add(p,'complete new evidence, pre-outcome audit provenance or report figures')
    for name in ['local-guard-welfare-report.pdf','local-guard-welfare-report.txt','main-report-checks.json']:add('output/pdf/'+name,'one current reviewed main report')
    for p in sorted((ROOT/'.local').glob('adaptive-v9-*.png')):add(p,'actual desktop/narrow developer screenshots')
    for name in ['adaptive-display-smoke-result.json','adaptive-learning-benchmark.json','adaptive-learning-benchmark-final.json','adaptive-preflight.json']:
        p=ROOT/'.local'/name
        if p.exists():add(p,'explicit developer validation or prospective engineering receipt')
    routes=prior.route_map((ROOT/'research/demo-server.js').read_text(encoding='utf-8'))
    if routes.get('/adaptive')!='research/demo/adaptive.html':raise ValueError('Current learner evidence route missing')
    for url,name in routes.items():add(name,'closed current static route '+url)
    # Seed-inventory manifests are administrative hash inputs, not instructions
    # to recursively collect their old pilots/traces. The primary already freezes
    # its actual inherited source/input closure explicitly.
    for manifest_name in ['research/adaptive-learning-results/manifest.json','research/adaptive-learning-results/summary.json']:
        value=json.loads((ROOT/manifest_name).read_text(encoding='utf-8'))
        for field in ['sourceHashes','inputHashes']:
            for name,h in value.get(field,{}).items():
                n=add(name,manifest_name+' / exact '+field);expected[n]=h
                if field=='sourceHashes':
                    snapshot=ROOT/'research/adaptive-learning-results/sources'/name
                    if snapshot.exists():expected[add(snapshot,'primary frozen source snapshot')]=h
    preserved=json.loads((ROOT/'research/README_PRESERVATION_GOAL7.json').read_text(encoding='utf-8'))
    for record in preserved['files']:
        if stream.digest_file(ROOT/record['preservedAs'])!={'sha256':record['sha256'],'bytes':record['bytes']}:raise ValueError('Preserved workspace README drift')
    # Discover only actual local JS dependencies of the explicitly collected code.
    visited=set();queue=list(sources)
    while queue:
        name=queue.pop()
        if name in visited:continue
        visited.add(name)
        if name.endswith(('.js','.mjs')) and '/sources/' not in name:
            with stream.source_stream(sources[name]) as f:text=f.read().decode('utf-8-sig')
            imports=re.findall(r"(?:^|[;\n])\s*(?:import|export)\s*(?:[^;'\"]+?\s*from\s*)?['\"]([^'\"\n]+)['\"]",text,re.M)
            imports+=re.findall(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]",text)
            for dependency in imports:
                if dependency.startswith('node:'):continue
                if dependency.startswith(('./','../')):n=add(ROOT/Path(name).parent/dependency,'local JS dependency '+name)
                elif dependency.startswith('/'):
                    if dependency not in routes:raise ValueError('Unmapped browser import '+dependency)
                    n=add(routes[dependency],'browser import '+name)
                else:raise ValueError('Unbundled module '+dependency)
                if n not in visited:queue.append(n)
    for name,h in expected.items():
        if stream.digest_file(ROOT/name)['sha256']!=h:raise ValueError('Frozen primary/analysis dependency drift '+name)
    sources['README-v8.md']={'kind':'zip','archive':BASE,'member':'README.md'}
    sources['DELIVERY_FREEZE-v8.json']=sources.pop('DELIVERY_FREEZE.json')
    sources['research/demo/overview-v8.html']={'kind':'zip','archive':BASE,'member':'research/demo/overview.html'}
    sources['START-HERE.txt']={'kind':'bytes','data':b'CURRENT REPORT: output/pdf/local-guard-welfare-report.pdf\nStart: node research/demo-server.js then http://127.0.0.1:3003/\nLearner evidence: /adaptive; protection: /recurring; one-shop profit: /profit-challenge.\nRead README.md and research/README.md for scope, attribution and independent reproduction.\nThe main report is local research; author affiliation remains unsupplied.\n'}
    package={'name':'local-guard-welfare-study','version':'9.0.0','private':True,'type':'module','engines':{'node':'>=24'},'scripts':{'start':'node research/demo-server.js','test':'node --test --test-isolation=none '+' '.join(NODE_TESTS),'audit':'python -B research/audit-adaptive-learning.py','analyze':'node research/adaptive-analysis.js','test:ui':'node .local/adaptive-display-smoke.mjs','test:export':'node .local/adaptive-export-smoke.mjs'}}
    sources['package.json']={'kind':'bytes','data':json_bytes(package)};sources['STATIC_ROUTES.json']={'kind':'bytes','data':json_bytes(routes)}
    inventory=stream.inventory(sources)
    for name in protected:
        if any(inventory[name][key]!=inherited[name][key] for key in ['sha256','bytes']):raise ValueError('Inherited protected payload drift '+name)
    if sum(r['bytes'] for r in inventory.values())>3_000_000_000:raise ValueError('Unexpected oversized delivery; preserve evidence and review')
    return sources,inventory,routes,provenance,len(protected)


def main_report(directory,expected):
    try:from pypdf import PdfReader
    except ImportError:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'
        if bundled.is_dir():sys.path.append(str(bundled))
        from pypdf import PdfReader
    p=directory/PDF;checks=json.loads((directory/'output/pdf/main-report-checks.json').read_text(encoding='utf-8'))
    if digest(p)!=expected or checks['sha256']!=expected:raise ValueError('Current report differs from final review')
    texts=[page.extract_text() for page in PdfReader(str(p)).pages];body=next(i for i,t in enumerate(texts) if re.search(r'(^|\n)References(\n|$)',t));abstract=re.search(r'\bAbstract\.\s+(.*?)\n1 ',texts[0],re.S)
    if not abstract:raise ValueError('Actual main report abstract missing')
    words=len(abstract.group(1).split())
    if len(texts)!=9 or body!=7 or words!=checks['abstractWords'] or not 150<=words<=250 or 'Mohammadpayam Teabi' not in texts[0] or 'LLM usage and author contributions' not in '\n'.join(texts) or 'Dual-Use / Ethical Considerations' not in '\n'.join(texts):raise ValueError('Actual main report structure/disclosure differs')
    return {'sha256':expected,'bytes':p.stat().st_size,'pages':len(texts),'bodyPages':body,'abstractWords':words,'authorVerified':True,'affiliationSupplied':False}


def verify(archive,pdf_sha):
    node=shutil.which('node')
    if not node:raise RuntimeError('Node24+ required; no automatic installs')
    with base.verification_workspace() as target:
        records=stream.extract_verified(archive,target)
        output=base.execute([node,'--test','--test-isolation=none','--test-reporter=tap',*NODE_TESTS],target)
        if not re.search(r'^# tests 29$',output,re.M) or not re.search(r'^# fail 0$',output,re.M):raise ValueError('29 Node scientific/bootstrap tests required')
        script="import sys,unittest;s=unittest.TestSuite();[s.addTests(unittest.defaultTestLoader.discover('tests',p)) for p in ('test_adaptive_learning_audit.py','test_evidence_streaming.py')];r=unittest.TextTestRunner(stream=sys.stdout).run(s);sys.exit(not r.wasSuccessful())"
        output=base.execute([sys.executable,'-B','-c',script],target,timeout=300)
        if not re.search(r'Ran 13 tests?',output) or not re.search(r'^OK$',output,re.M):raise ValueError('13 independent-audit/stream-integrity tests required')
        base.execute([node,'research/adaptive-learning.js','verify'],target)
        audit=json.loads(base.execute([sys.executable,'-B','research/audit-adaptive-learning.py'],target,timeout=7200))
        if not audit['passed'] or audit['runs']!=192 or audit['checkpoints']!=384 or audit['fullTrainingReplay'] is not False or not all(audit['corruptionNegativeControls'].values()):raise ValueError('Complete independent checkpoint/graph/probe audit failed')
        base.execute([node,'research/adaptive-analysis.js'],target,timeout=300)
        for name in ['research/adaptive-learning-results/summary.json','research/ADAPTIVE_LEARNING_RESULTS.md']:
            if digest(target/name)!=records[name]['sha256']:raise ValueError('Descriptive byte mismatch '+name)
        scratch=target/'.reproduce';scratch.mkdir()
        base.execute([node,'research/build-adaptive-web.js','--output','.reproduce/adaptive-data.json'],target,timeout=300)
        if digest(scratch/'adaptive-data.json')!=records['research/adaptive-learning-results/web-data.json']['sha256']:raise ValueError('Compact web export is not byte exact')
        harness=[json.loads(base.execute([node,name],target,timeout=900)) for name in HARNESSES]
        if not all(r['passed'] for r in harness):raise ValueError('Presentation adapter checks failed')
        base.execute([sys.executable,'-B','research/build-capacity-figures.py','--structural-only'],target,timeout=300)
        base.execute([sys.executable,'-B','research/build-main-report.py'],target,timeout=300)
        figures=[name for name in records if name.startswith('research/capacity-figures/') and name.endswith(('.png','.svg'))]
        if len(figures)!=6 or any(digest(target/name)!=records[name]['sha256'] for name in figures):raise ValueError('Three figure pairs did not regenerate byte exactly')
        report=main_report(target,pdf_sha);routes=json.loads((target/'STATIC_ROUTES.json').read_text());http=base.http_smoke(target,routes,node)
        for name,record in records.items():
            if stream.digest_file(target/name)!={k:record[k] for k in ['sha256','bytes']}:raise ValueError('Verification mutated manifested payload '+name)
        sources=stream.extracted_sources(target,records);expected=stream.inventory(sources);repacked=scratch/'repacked.zip';stream.zip_sources(repacked,sources,expected)
        if digest(repacked)!=digest(archive):raise ValueError('Fresh payload repack is not identical')
        second=scratch/'second';second.mkdir();stream.extract_verified(repacked,second)
        return {'passed':True,'payloadHashesAndCRC':True,'payloadFiles':len(records)+1,'tests':{'nodeScientificPassed':29,'pythonIndependentAuditPassed':10,'deliveryIntegrityPassed':3,'scientificTotalPassed':39,'totalPassed':42,'failed':0},'independentAudit':audit,'fullTrainingReplay':False,'earlierFullAuditsRerun':False,'inheritedProvenanceCheckedReadOnly':True,'summaryReportWebExportByteExact':True,'presentationAdapterChecks':harness,'figureByteExact':True,'mainReport':report,'http':{**http,'successfulGetRoutesIncludingHealth':len(routes)+1},'allManifestedPayloadsUnchanged':True,'freshRepackByteExact':True,'repackedFreshExtractionVerified':True,'memoryScope':'Streaming file/chunk inventory, archive and extraction; no whole checkpoint corpus retained in memory by packaging.'}


def plan():
    _,inventory,routes,_,protected=collect();value={'scope':'Prospective complete V9 adaptive-study delivery with closed V8 payload; administrative seed manifests not recursively expanded','builderSourceHash':digest(Path(__file__)),'baseArchiveSha256':BASE_SHA,'files':inventory,'routes':len(routes),'protectedInheritedFiles':protected}
    PLAN.write_bytes(json_bytes(value));print(json.dumps({'inventory':PLAN.relative_to(ROOT).as_posix(),'sha256':digest(PLAN),'files':len(inventory),'bytes':sum(r['bytes'] for r in inventory.values()),'routes':len(routes),'protectedInheritedFiles':protected,'createsArchive':False}))


def build(pdf_sha):
    if not re.fullmatch('[0-9a-f]{64}',pdf_sha):raise ValueError('Final reviewed main-PDF hash required')
    if OUT.exists():raise ValueError('Existing delivery archive preserved')
    started=time.perf_counter();sources,inventory,routes,provenance,protected=collect();frozen=json.loads(PLAN.read_text())
    if frozen['builderSourceHash']!=digest(Path(__file__)) or frozen['baseArchiveSha256']!=BASE_SHA or frozen['files']!=inventory:raise ValueError('Prospective inventory changed; refusing silent rebuild')
    if inventory[PDF]['sha256']!=pdf_sha:raise ValueError('Final main report differs')
    needed=4*sum(r['bytes'] for r in inventory.values())+256_000_000
    if shutil.disk_usage(ROOT).free<needed:raise ValueError('Insufficient free space for two fresh extractions/repack; no cases omitted')
    sources['DELIVERY_FREEZE.json']={'kind':'file','path':PLAN};inventory['DELIVERY_FREEZE.json']=stream.digest_file(PLAN)
    contents={'scope':'Complete reviewed V9 adaptive learner evidence and current report; full training replay not claimed','baseArchiveSha256':BASE_SHA,'prospectiveInventorySha256':digest(PLAN),'files':{n:{**r,'provenance':sorted(provenance.get(n,{'closed V8 payload or explicit generated navigation/inventory'}))} for n,r in inventory.items()}}
    sources['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json_bytes(contents)};inventory['PACKAGE_CONTENTS.json']={'sha256':hashlib.sha256(sources['PACKAGE_CONTENTS.json']['data']).hexdigest(),'bytes':len(sources['PACKAGE_CONTENTS.json']['data'])}
    temporary=OUT.with_name(OUT.stem+'.building-'+uuid.uuid4().hex+'.zip');stream.zip_sources(temporary,sources,inventory);checks=verify(temporary,pdf_sha)
    if OUT.exists():raise ValueError('Final delivery path appeared during verification; preserving both')
    temporary.rename(OUT);receipt={'archive':OUT.relative_to(ROOT).as_posix(),'sha256':digest(OUT),'bytes':OUT.stat().st_size,'uncompressedPayloadBytes':sum(r['bytes'] for r in inventory.values()),'seconds':time.perf_counter()-started,'prospectiveInventorySha256':digest(PLAN),'builderSourceHash':digest(Path(__file__)),'baseArchive':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':BASE_SHA,'protectedInheritedFiles':protected},'verification':checks};RECEIPT.write_bytes(json_bytes(receipt))
    REPORT.write_text('# Streaming adaptive delivery verification\n\n'+f"Archive: `{receipt['archive']}`\n\nSHA256: `{receipt['sha256']}`\n\n{receipt['bytes']:,} compressed bytes, {checks['payloadFiles']} files. Prospective inventory `{receipt['prospectiveInventorySha256']}` was announced before archive creation and required byte-identical source inventories.\n\n"+'Fresh extraction passed 39 scientific tests and 3 delivery-integrity tests, the complete 192-run/384-checkpoint independent Q/policy/count/graph/probe audit, descriptive/web/three-figure-pair/main-report byte-exact rebuilds, portable display/export checks and all closed local routes. All manifested SHA256/CRC and post-verification payload checks passed. The complete payload repacked identically and extracted again. Earlier stage archives remain preserved; their full audits and every main training round were not rerun. The package preserves the pre-outcome independent-auditor snapshot and all learner checkpoints.\n\n'+'Inventory, compression, extraction and repack use bounded streaming buffers. Numerical-run resource figures exclude derived displays and packaging. The study has one economic calibration, two mask conditions and 12 paired seeds; no equilibrium, learner convergence, unrestricted capability or empirical-market claim follows. No language-model/chat/API seller calls, paid services, submission or external deployment were performed. Codex assistance is disclosed; author affiliation remains unsupplied.\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['archive','bytes','sha256','seconds']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True);sub.add_parser('plan');b=sub.add_parser('build');b.add_argument('--final-freeze-report-sha',required=True)
    r=sub.add_parser('repack');r.add_argument('directory',type=Path);r.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.mode=='plan':plan()
    elif args.mode=='build':build(args.final_freeze_report_sha)
    else:
        records=json.loads((args.directory/'PACKAGE_CONTENTS.json').read_text())['files'];sources=stream.extracted_sources(args.directory,records);stream.zip_sources(args.output,sources,stream.inventory(sources));print(json.dumps({'repacked':str(args.output),'sha256':digest(args.output)}))
