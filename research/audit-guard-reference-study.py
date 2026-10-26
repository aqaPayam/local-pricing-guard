"""Independent authoritative full-grid-after-cap reference inventory/reexecution audit.

No primary numeric, checkpoint, supervisor, or analysis module is imported.
The independent Node component is separately owned and recomputes every round.
Default operation is read-only; optional receipts are exclusive-create.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zlib
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = tuple(range(907001, 907013))
TREATMENT = 'full-grid-after-cap'
SCIENTIFIC_TREATMENT = dict(capClock='startup', supportMode=TREATMENT, initialCap=True, postInitialOriginalIndices='all')
SHA = re.compile(r'[0-9a-f]{64}\Z')
WORKER = 'research/replay-guard-reference.js'
SELF = 'research/audit-guard-reference-study.py'
CORE = 'research/audit-guard-reference.js'
OLD_MANIFEST = 'dcd573fc866e59cd1a27c3158cb9e9be58702034f9fb250e251c54f579a01817'
OLD_AUDIT = 'a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6'
OLD_SUMMARY = '3bbbc757378f79c4bdf948166ac73458e2aa2ebc0ecaedc6876d55fc5e09f489'
OLD_BUILDER = '8819178086fe455987a10c66e26dedb0c8ef3ca2ca4980e529a4e24e534ceaa0'
REQUIRED = (SELF, WORKER, CORE, 'research/audit-matched-clock.js',
 'research/GUARD_REFERENCE_PROTOCOL.md','research/GUARD_REFERENCE_ANALYSIS_CONTRACT.md',
 'research/GUARD_REFERENCE_PROSPECTIVE_REVIEW.md',
 'research/guard-reference-learning.js','research/guard-reference-io.js','research/guard-reference-case.js',
 'research/guard-reference-study.js','research/run-guard-reference.py','research/benchmark-guard-reference.py',
 'research/guard-reference-analysis.py','research/guard-reference-baseline.py',
 'research/matched-clock-learning.js','research/matched-clock-graph.js','research/matched-clock-io.js',
 'tests/guard-reference-audit.test.js','tests/guard-reference-cross-audit.test.js',
 'tests/guard-reference-serialization-audit.test.js','tests/test_guard_reference_cross_anchors.py',
 'tests/test_guard_reference_inventory_audit.py','tests/test_guard_reference_replay_process.py',
 'research/GUARD_REFERENCE_ROOT_REVIEW.md','tests/guard-reference-learning.test.js',
 'tests/guard-reference-case.test.js','tests/guard-reference-study.test.js',
 'tests/test_guard_reference_analysis.py','tests/test_guard_reference_case.py',
 'tests/test_guard_reference_baseline.py','tests/test_guard_reference_supervisor.py',
 'tests/test_guard_reference_benchmark.py')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def same(a, b, label):
    """Strict recursive identity, including Python bool-versus-int distinctions."""
    need(type(a) is type(b), label + ': type differs')
    if isinstance(b, dict):
        need(a.keys() == b.keys(), label + ': keys differ')
        for k in b:
            same(a[k], b[k], label + '.' + k)
    elif isinstance(b, list):
        need(len(a) == len(b), label + ': length differs')
        for i, v in enumerate(b):
            same(a[i], v, label + '[' + str(i) + ']')
    else:
        need(a == b and not (isinstance(a, float) and not math.isfinite(a)), label + ': value differs')


def parse(data):
    def object_pairs(pairs):
        out = {}
        for k, value in pairs:
            need(k not in out, 'Duplicated JSON object key')
            out[k] = value
        return out
    return json.loads(data, object_pairs_hook=object_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON number')))


def local(root, name):
    need(isinstance(name, str) and name and '\\' not in name and ':' not in name
         and not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')),
         'Unsafe relative reference')
    base = Path(root).resolve()
    target = (base / name).resolve()
    need(target.is_relative_to(base) and target != base, 'Reference escapes declared directory')
    return target


def reference(root, ref, maximum=128_000_000):
    need(isinstance(ref, dict) and isinstance(ref.get('file'), str)
         and type(ref.get('bytes')) is int and 0 <= ref['bytes'] <= maximum
         and isinstance(ref.get('sha256'), str) and SHA.fullmatch(ref['sha256']), 'Invalid bounded artifact reference')
    target = local(root, ref['file'])
    need(target.is_file() and target.stat().st_size == ref['bytes'] and digest(target) == ref['sha256'],
         'Artifact bytes/hash mismatch: ' + ref['file'])
    return target


def packed(v):
    return {'numerator': str(v.numerator), 'denominator': str(v.denominator)}


def fraction(value, approximate=False):
    need(isinstance(value, dict) and set(value) == ({'numerator', 'denominator', 'approximate'} if approximate else {'numerator', 'denominator'}), 'Exact ratio shape differs')
    a, b = value['numerator'], value['denominator']
    need(isinstance(a, str) and isinstance(b, str) and len(a) <= 10000 and len(b) <= 10000
         and re.fullmatch(r'0|-?[1-9][0-9]*', a) and re.fullmatch(r'[1-9][0-9]*', b), 'Noncanonical ratio')
    v = Fraction(int(a), int(b))
    need(str(v.numerator) == a and str(v.denominator) == b, 'Unreduced ratio')
    if approximate:
        need(type(value['approximate']) in (int, float) and math.isfinite(value['approximate']), 'Invalid display approximation')
    return v


def python_runtime():
    return dict(executableSha256=digest(sys.executable), pythonVersion=sys.version,
                implementation=platform.python_implementation(), zlibCompileVersion=zlib.ZLIB_VERSION,
                zlibRuntimeVersion=zlib.ZLIB_RUNTIME_VERSION)


def node_runtime(project, node):
    p = subprocess.run([node, str(local(project, WORKER)), '--runtime'], cwd=project,
                       capture_output=True, timeout=30, check=False)
    need(p.returncode == 0 and len(p.stdout) < 100000, 'Independent metadata-only Node runtime query failed')
    return parse(p.stdout)


def fingerprint(value):
    return {k: value[k] for k in ('executableSha256', 'node', 'v8', 'platform', 'architecture', 'osRelease', 'execArgv')}


def plan_id(seed):
    return f'base-g15-t1--full-grid-after-cap--zero--s{seed}'


def planned_runs(actors):
    need(len(actors)==12, 'All independently derived actor namespaces required')
    return [dict(id=plan_id(a['seed']),scenario='base-g15-t1',arm='startup',seed=a['seed'],
                 initialization='positive-zero',actors=a['actors'],segments=a['segments'],
                 treatment=TREATMENT,scientificTreatment=SCIENTIFIC_TREATMENT.copy()) for a in actors]


def javascript_imports(source):
    """Read static module references without interpreting text inside JS strings.

    Small lexical pass, not a JavaScript execution or general syntax validator.
    Comments/templates/ordinary strings cannot introduce fake import tokens.
    """
    tokens=[];i=0;n=len(source)
    while i<n:
        c=source[i]
        if c.isspace():
            i+=1;continue
        if source.startswith('//',i):
            end=source.find('\n',i+2);i=n if end<0 else end+1;continue
        if source.startswith('/*',i):
            end=source.find('*/',i+2);need(end>=0,'Unclosed JS source comment');i=end+2;continue
        if c in ('\"',"'",'`'):
            quote=c;j=i+1;value=[]
            while j<n:
                if source[j]=='\\':
                    need(j+1<n,'Unclosed JS escape');value.extend(source[j:j+2]);j+=2
                elif source[j]==quote:
                    break
                else:
                    value.append(source[j]);j+=1
            need(j<n,'Unclosed JS literal')
            tokens.append(('literal' if quote!='`' else 'template',''.join(value)));i=j+1;continue
        match=re.match(r'[A-Za-z_$][A-Za-z0-9_$]*',source[i:])
        if match:
            value=match.group();tokens.append(('identifier',value));i+=len(value)
        else:
            tokens.append(('punctuation',c));i+=1
    refs=[]
    for i,(kind,value) in enumerate(tokens):
        if kind!='identifier' or value not in ('import','export'):
            continue
        if i and tokens[i-1][1]=='.':
            continue
        tail=tokens[i+1:]
        if value=='import' and tail and tail[0][0]=='literal':
            refs.append(tail[0][1]);continue
        if value=='import' and len(tail)>1 and tail[0][1]=='(' and tail[1][0]=='literal':
            refs.append(tail[1][1]);continue
        for j,(k,v) in enumerate(tail):
            if v==';':
                break
            if k=='identifier' and v=='from' and j+1<len(tail) and tail[j+1][0]=='literal':
                refs.append(tail[j+1][1]);break
    return [r for r in refs if r.startswith('.')]


# Administrative gates are separately authored below. They perform hashes and
# existing authority/schema authentication only, never new anchor selection or
# replay. Old accepted checkpoint numerics are reused transparently.
def verify_old_comparison(project, bound):
    base='research/matched-clock-results/'
    manifest_name=base+'manifest.json'; audit_name=base+'independent-audit.json'
    need(bound.get(manifest_name)==OLD_MANIFEST and bound.get(audit_name)==OLD_AUDIT,
         'Pinned old matched manifest/audit missing or replaced')
    manifest=parse(local(project,manifest_name).read_bytes())
    audit=parse(local(project,audit_name).read_bytes())
    need(audit.get('passed') is True and audit.get('inventoryAccepted') is True
         and audit.get('independentAuditPassed') is True and audit.get('finalSourceInputOutputIntegrityCheck') is True
         and audit.get('fullTrainingReplay') is True and audit.get('replayComplete') is True
         and audit.get('replayedRounds')==48_000_000
         and audit.get('studyManifestHash')==OLD_MANIFEST, 'Old authoritative inventory acceptance differs')
    for source_key,source in [('auditorSourceHash','research/audit-matched-clock-study.py'),
                              ('controlAuditorSourceHash','research/replay-matched-clock.js'),
                              ('replayCoreSourceHash','research/audit-matched-clock.js')]:
        need(audit.get(source_key)==bound.get(source)==manifest['sourceHashes'].get(source),
             'Old accepted auditor source not bound: '+source)
    for group in ('sourceHashes','inputHashes'):
        for name,sha in manifest[group].items():
            need(bound.get(name)==sha and digest(local(project,name))==sha,'Old source/input identity omitted or changed: '+name)
            if group=='sourceHashes':
                need(digest(local(project,base+'sources/'+name))==sha,'Old frozen source snapshot changed: '+name)
    for name,key in [('results.json','resultsSha256'),('index.json','indexSha256'),('completion.json','completionSha256'),
                     ('execution-start.json','executionStartSha256'),('journal.jsonl','journalSha256')]:
        need(bound.get(base+name)==audit.get(key) and digest(local(project,base+name))==audit[key],
             'Old closed execution output differs: '+name)
    old_results=parse(local(project,base+'results.json').read_bytes())
    old_index=parse(local(project,base+'index.json').read_bytes())
    need(old_results['manifestSha256']==old_index['manifestSha256']==OLD_MANIFEST
         and len(old_results['records'])==len(old_index['records'])==24,'Old ordered inventory differs')
    endpoints=[]
    def checked(ref):
        need(bound.get(base+ref['file'])==ref['sha256'],'Selected old artifact not frozen: '+ref['file'])
        return reference(local(project,'research/matched-clock-results'),ref)
    for seed in SEEDS:
        rid=f'base-g15-t1--matched5-startup--zero--s{seed}'
        rows=[r for r in old_results['records'] if r.get('id')==rid]
        entries=[i for i in old_index['records'] if i.get('id')==rid]
        accepted=[e for e in audit['finalEndpoints'] if e.get('runId')==rid]
        need(len(rows)==len(entries)==len(accepted)==1,'Old planned comparator missing or duplicated')
        row,ix,endpoint=rows[0],entries[0],accepted[0]
        same(parse(checked(ix).read_bytes()),row,'Old record/result duplication')
        need(endpoint['seed']==seed and endpoint['arm']=='startup','Old comparator treatment differs')
        end=dict(endpoint)
        if endpoint['available']:
            need(endpoint.get('replayMatched') is True and endpoint.get('step')==2_000_000
                 and endpoint.get('nextPhase')==4,'Old final not independently accepted from its actual state')
            slots=[cp for cp in row['checkpoints'] if cp['step']==2_000_000]
            need(len(slots)==1 and slots[0]['parentEligible'] is True,'Old accepted final slot absent')
            cp=slots[0];meta=parse(checked(cp['metadata']).read_bytes())
            need(cp['metadata']['sha256']==endpoint['checkpointSha256'] and meta['graph']['sha256']==endpoint['graphSha256'],
                 'Old final checkpoint/graph differs from authority')
            graph=parse(checked(meta['graph']).read_bytes())
            for group in ('artifacts','policies'):
                for refs in meta[group].values():
                    for ref in refs:
                        checked(ref)  # compressed Q/count bytes are HASHED ONLY, never decoded
            same(meta['terminal'],dict(phase=endpoint['nextPhase'],previousIndices=endpoint['previousIndices']),'Old actual-terminal state')
            same(packed(fraction(graph['actualTerminal']['cycleMetrics']['consumerSurplus'],True)),endpoint['cycleCustomerBenefit'],'Old accepted terminal cycle CS')
            need(len(graph['actualTerminal']['cycleNodesFromStart'])==endpoint['cycleLength'],'Old full cycle length differs')
        else:
            need(endpoint.get('cycleCustomerBenefit') is None and isinstance(endpoint.get('unavailableReason'),str),
                 'Old unavailable comparator must remain null')
        endpoints.append(end)
    return dict(manifestFile=manifest_name,manifestSha256=OLD_MANIFEST,auditFile=audit_name,auditSha256=OLD_AUDIT,
                endpoints=endpoints,scope='Reused pinned old numerical acceptance; current source/input/output and selected final compressed artifacts hash-bound, no old Q decode/retraining/replay')


def verify_dependencies(project,directory,node=None):
    """ADMIN-ONLY hash/schema/runtime and old-authority gate; no new numerics."""
    project,directory=Path(project).resolve(),Path(directory).resolve();node=node or shutil.which('node')
    need(node,'Node runtime absent')
    manifest=parse((directory/'manifest.json').read_bytes())
    need(manifest.get('schemaVersion')==1,'Unknown frozen reference manifest schema')
    bound={}
    for group in ('sourceHashes','inputHashes'):
        need(isinstance(manifest.get(group),dict) and manifest[group], 'Complete frozen map absent')
        for name,expected in manifest[group].items():
            need(isinstance(expected,str) and SHA.fullmatch(expected),'Malformed frozen dependency hash')
            target=local(project,name)
            need(target.is_file() and digest(target)==expected,'Frozen live dependency changed: '+name)
            need(name not in bound or bound[name]==expected,'Cross-map dependency conflict')
            bound[name]=expected
            if group=='sourceHashes':need(digest(local(directory,'sources/'+name))==expected,'Frozen source snapshot differs: '+name)
    need(set(REQUIRED)<=set(manifest['sourceHashes']),'Mandatory new reference source/test omitted')
    for name in manifest['sourceHashes']:
        if name.endswith(('.js','.mjs')):
            for module in javascript_imports(local(project,name).read_text(encoding='utf-8')):
                child=os.path.normpath((Path(name).parent/module).as_posix()).replace('\\','/')
                need(child in manifest['sourceHashes'],'Imported source omitted from immutable snapshots: '+child)
    for name in bound:
        if name.endswith('/manifest.json'):
            inherited=parse(local(project,name).read_bytes())
            recognized=[key for key in ('sourceHashes','inputHashes','hashes','sources') if key in inherited]
            need(recognized,'Unrecognized inherited manifest identity schema')
            for key in recognized:
                need(isinstance(inherited[key],dict),'Malformed inherited dependency map')
                for child,value in inherited[key].items():
                    expected=value if isinstance(value,str) else value.get('sha256') if isinstance(value,dict) else None
                    need(isinstance(expected,str) and SHA.fullmatch(expected) and bound.get(child)==expected,
                         'Inherited transitive dependency omitted/changed: '+child)
    runtime=node_runtime(project,node)
    same(fingerprint(manifest['runtime']),fingerprint(runtime['runtime']),'Independent Node/backend fingerprint')
    same({key:manifest['parentRuntime'][key] for key in python_runtime()},python_runtime(),'Frozen Python/zlib parent')
    plan=manifest['plan'];same(plan['runs'],planned_runs(runtime['actors']),'Fixed 12-run namespace/identity plan')
    for key,value in dict(retainedRuns=12,T=2_000_000,checkpoints=[1_000_000,2_000_000],alpha=.1,gamma=19/20,
                          initialization='positive-zero',clock='0->1->2->3->4->1',scientificTreatment=SCIENTIFIC_TREATMENT,
                          transcript=dict(bytesPerRound=120,roundsPerBlock=10000,completeBlocksPerRun=200),hardCaseSeconds=600,
                          softResourceTargets=dict(primarySeconds=3600,replaySeconds=3600,sampledRSSBytes=512000000,newRawEquivalentBytes=1000000000)).items():
        same(plan[key],value,'Prospective reference plan.'+key)
    old=verify_old_comparison(project,bound)
    baseline=manifest.get('baseline');need(isinstance(baseline,dict),'Explicit old comparison descriptor required')
    for key,name,expected in [('manifest',old['manifestFile'],OLD_MANIFEST),('audit',old['auditFile'],OLD_AUDIT),
                              ('summary','research/matched-clock-results/analysis.json',OLD_SUMMARY),
                              ('builder','research/build-matched-clock-web.py',OLD_BUILDER)]:
        same(baseline[key],dict(file=name,sha256=expected),'Explicit accepted baseline.'+key)
        need(bound.get(name)==expected,'Pinned old comparator dependency omitted: '+name)
    same(baseline['finalEndpoints'],old['endpoints'],'Manifest cannot relabel old accepted endpoints')
    finite=manifest['inputs']['finiteGame'];reference(project,finite)
    need(bound.get(finite['file'])==finite['sha256'],'Original physical game not frozen')
    old_manifest=parse(local(project,old['manifestFile']).read_bytes())
    same(finite,old_manifest['inputs']['finiteGame'],'Unchanged original physical payoff/cap reference')
    benchmark=parse(local(project,manifest['benchmark']['file']).read_bytes())
    need(bound.get(manifest['benchmark']['file'])==manifest['benchmark']['sha256'] and benchmark.get('passed') is True
         and benchmark.get('artificial') is True and benchmark.get('n')==62 and benchmark.get('rounds')==2_000_000
         and benchmark.get('fullIndependentReplay') is True and benchmark.get('sourcesUnchanged') is True,
         'Mandatory full-support artificial production benchmark absent')
    same(benchmark['finalSourceHashes'],benchmark['sourceHashes'],'Benchmark source entry/exit')
    same(benchmark['sourceHashes'],manifest['sourceHashes'],'Complete source-bound benchmark inventory')
    for name,sha in benchmark['sourceHashes'].items():need(manifest['sourceHashes'].get(name)==sha,'Benchmark source no longer frozen: '+name)
    need({SELF,WORKER,CORE,'research/guard-reference-learning.js','research/guard-reference-io.js',
          'research/guard-reference-case.js','research/run-guard-reference.py'}<=set(benchmark['sourceHashes']),
         'Maximal production benchmark omits critical source')
    need(isinstance(benchmark.get('artifacts'),list) and benchmark['artifacts'],'Complete benchmark artifact inventory absent')
    for ref in benchmark['artifacts']:
        reference(project,ref);need(bound.get(ref['file'])==ref['sha256'],'Benchmark artifact not frozen')
    return dict(passed=True,studyManifestHash=digest(directory/'manifest.json'),sourcesVerified=True,inputsVerified=True,
                sources=len(manifest['sourceHashes']),inputs=len(manifest['inputHashes']),auditorSourceHash=digest(local(project,SELF)),
                controlAuditorSourceHash=digest(local(project,WORKER)),replayCoreSourceHash=digest(local(project,CORE)),
                immutableReplayKernelSourceHash=digest(local(project,'research/audit-matched-clock.js')),
                acceptedOldComparison={key:value for key,value in old.items() if key!='endpoints'},oldComparisonEndpoints=old['endpoints'],
                runtime=runtime['runtime'],manifest=manifest,
                scope='Administrative source/input/schema/runtime and pinned old acceptance binding only; no new Q decode/replay/anchor selection')


def snapshot(directory):
    return {p.relative_to(directory).as_posix(): (p.stat().st_size, digest(p))
            for p in sorted(Path(directory).rglob('*')) if p.is_file()}


def audit_events(record, ends, budget=600):
    """Check recorded parent chronology; hashes do not authenticate wall-clock provenance."""
    need(type(record.get('executionSucceeded')) is bool and isinstance(record.get('events'), list), 'Missing primary execution flags/events')
    actual_budget=record.get('budgetSeconds',budget)
    need(type(actual_budget) in (int,float) and 0<actual_budget<=budget,'Primary actual case budget invalid')
    budget=actual_budget
    events = record['events']
    last = -1.0
    for i, e in enumerate(events):
        need(type(e.get('sequence')) is int and e['sequence'] == i and isinstance(e.get('type'), str), 'Primary event sequence invalid')
        elapsed = e.get('elapsedMilliseconds')
        need(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= last, 'Primary event time is not monotone')
        last = elapsed
    stops = [e['sequence'] for e in events if e['type'] in ('deadline termination requested', 'owned process stopped after supervisor failure')]
    closed = [e['sequence'] for e in events if e['type'] in ('process exited','supervision closed')]
    need(isinstance(record.get('checkpoints'), list) and len(record['checkpoints']) == 2, 'Both checkpoint slots required')
    for slot, end in zip(record['checkpoints'], ends):
        need(type(slot.get('step')) is int and slot['step'] == end and type(slot.get('parentEligible')) is bool
             and slot.get('scientificAvailable') is False, 'Checkpoint identity/availability claim invalid')
        if slot['parentEligible']:
            a, b = slot.get('receivedSequence'), slot.get('validatedSequence')
            need(type(a) is int and type(b) is int and 0 <= a < b < len(events), 'Eligibility chronology missing')
            need(events[a]['type'] == 'process line received' and events[b]['type'] == 'checkpoint validated'
                 and events[b].get('step') == end and events[b].get('metadata') == slot['metadata'], 'Eligibility event identities differ')
            need(events[b]['elapsedMilliseconds'] < budget * 1000 and (not stops or b < min(stops))
                 and (not closed or b < min(closed)), 'Late/post-termination/exit checkpoint adopted')
            received = [e for e in events[a+1:b] if e['type'] == 'checkpoint received' and e.get('step') == end]
            need(len(received) == 1 and received[0]['metadata'] == slot['metadata'], 'Checkpoint receipt event absent/duplicate')
        else:
            need(isinstance(slot.get('reason'), str) and slot['reason'], 'Unavailable checkpoint lacks reason')
    if record['executionSucceeded']:
        need(record.get('status') == 'completed' and all(s['parentEligible'] for s in record['checkpoints'])
             and record.get('failure') is None and not stops, 'Execution success contradicts failures')
        done = [e for e in events if e['type'] == 'done received']
        exited = [e for e in events if e['type'] == 'process exited']
        need(len(done) == 1 and len(exited) == 1 and exited[0].get('exitCode') == 0
             and done[0]['sequence'] < exited[0]['sequence'] and exited[0]['elapsedMilliseconds'] < budget * 1000,
             'Natural successful exit before deadline missing')
    return True


def working_set(pid=None):
    """Independently authored Windows current working set; no peak/private claim."""
    if os.name!='nt':
        return dict(bytes=None,reason='Windows current-working-set API unavailable on this platform')
    try:
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_=[('size',wintypes.DWORD),('faults',wintypes.DWORD),('peak',ctypes.c_size_t),
                      ('working',ctypes.c_size_t),('remaining',ctypes.c_size_t*6)]
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(0x410,False,pid or os.getpid())
        need(bool(handle),'Working-set process handle unavailable')
        try:
            value=Counters();value.size=ctypes.sizeof(value)
            query=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
            query.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
            need(bool(query(handle,ctypes.byref(value),value.size)),'Current working-set query failed')
            return dict(bytes=int(value.working),reason=None)
        finally:
            kernel.CloseHandle(handle)
    except Exception as e:
        return dict(bytes=None,reason=str(e))


def run_replay(node, project, directory, task_file, record_file, budget=600):
    """Own a separate independent Node PID. Kill only that PID at the hard deadline."""
    need(type(budget) in (int, float) and 0 < budget <= 600, 'Invalid independent replay hard budget')
    start = time.perf_counter()
    try:
        proc = subprocess.Popen([node, str(local(project, WORKER)), '--task', str(task_file),
                                 '--record', str(record_file), '--directory', str(directory)],
                                cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    except OSError as e:
        return dict(operationalFailure='Independent owned process could not start: '+str(e),replayedRounds=0,
                    checkpointResults=[],fullHorizonReplayed=False,allPlannedCheckpointsMatched=False,
                    finalConsumedIntegrityCheck=False,seconds=time.perf_counter()-start,nodeProcessRSSBytes=None,rssSamples=[])
    finished = threading.Event()
    killed = []
    samples=[]
    def sample_loop():
        while True:
            child,parent=working_set(proc.pid),working_set()
            samples.append(dict(elapsedMilliseconds=(time.perf_counter()-start)*1000,
                                nodeRSSBytes=child['bytes'],nodeRSSUnavailableReason=child['reason'],
                                parentRSSBytes=parent['bytes'],parentRSSUnavailableReason=parent['reason'],
                                approximatelyPairedRSSBytes=child['bytes']+parent['bytes'] if child['bytes'] is not None and parent['bytes'] is not None else None))
            if finished.wait(.05):
                break
    sampler=threading.Thread(target=sample_loop,daemon=True);sampler.start()
    def deadline():
        if not finished.wait(max(0, budget - (time.perf_counter()-start))) and proc.poll() is None:
            killed.append(time.perf_counter()-start)
            try:
                proc.kill()
            except ProcessLookupError:
                pass
    threading.Thread(target=deadline, daemon=True).start()
    messages = []
    errors = []
    stderr = bytearray()
    def read_lines():
        try:
            total = 0
            for line in iter(lambda: proc.stdout.readline(4_000_001), b''):
                total += len(line)
                need(len(line) <= 4_000_000 and total <= 16_000_000 and len(messages) < 4, 'Independent child output exceeded bound')
                messages.append(parse(line))
        except Exception as e:
            errors.append(str(e))
            if proc.poll() is None:
                proc.kill()
    def read_errors():
        for b in iter(lambda: proc.stderr.read(4096), b''):
            if len(stderr) < 65536:
                stderr.extend(b[:65536-len(stderr)])
    threads = [threading.Thread(target=read_lines, daemon=True), threading.Thread(target=read_errors, daemon=True)]
    for t in threads:
        t.start()
    try:
        proc.wait(timeout=budget+10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
        killed.append(time.perf_counter()-start)
    finally:
        finished.set()
    for t in threads:
        t.join(timeout=2)
    sampler.join(timeout=2)
    for h in (proc.stdout, proc.stderr):
        h.close()
    fatal = [x for x in messages if x.get('type') == 'replay failure']
    # A consumed-artifact drift is integrity-fatal, even if provisional endpoints matched.
    need(not any(x.get('failureKind')=='integrity' for x in fatal), 'Independent replay consumed-artifact integrity failure: ' + str(fatal))
    def unavailable(reason):
        planned=[]
        try:
            planned=parse(Path(task_file).read_bytes()).get('checkpoints',[])
        except Exception:
            pass
        milestones=[x.get('result',{}).get('step',0) for x in messages if x.get('type')=='checkpoint audited'
                    and x.get('result',{}).get('parentEligible') is True
                    and type(x.get('result',{}).get('step')) is int and x['result']['step'] in planned]
        return dict(operationalFailure=reason, replayedRounds=max(milestones,default=0),
                    checkpointResults=[], fullHorizonReplayed=False, allPlannedCheckpointsMatched=False,
                    finalConsumedIntegrityCheck=False, seconds=time.perf_counter()-start,nodeProcessRSSBytes=None,
                    rssSamples=samples,resourceSamplingScope='50ms current Windows working-set samples of owned Node PID and Python parent, sequential approximate pairs; not a continuous/private peak',
                    countScope='Last reported completed eligible checkpoint is a lower bound on rounds reexecuted, regardless of matching; unreported partial work is unknown. No scientific endpoint is adopted after operational failure.',
                    independentStderr=stderr.decode('utf-8','replace'))
    if killed or time.perf_counter()-start>=budget:
        return unavailable('Independent replay hard deadline exceeded (including result validation)')
    if errors or fatal:
        return unavailable('Independent replay process/output failure: '+str(errors or fatal))
    try:
        need(len(messages) == 3 and [x.get('type') for x in messages] == ['checkpoint audited', 'checkpoint audited', 'replay finished'], 'Complete independent result sequence missing')
        result = messages[-1]['result']
        same([x['result'] for x in messages[:2]], result['checkpointResults'], 'Independent endpoint/result duplication')
        need(result.get('finalConsumedIntegrityCheck') is True and proc.returncode == (0 if result['allEligibleCheckpointsMatched'] else 1), 'Independent completion/exit inconsistency')
    except Exception as e:
        return unavailable('Independent replay incomplete/invalid process result: '+str(e))
    if time.perf_counter()-start>=budget:
        return unavailable('Independent replay result validation finished after hard deadline')
    result['supervisedSeconds'] = time.perf_counter()-start
    result['countScope']='Exact independent replay endpoint reached; numerical round execution and checkpoint matching are separate fields'
    result['independentStderr'] = stderr.decode('utf-8', 'replace')
    result['rssSamples']=samples
    result['resourceSamplingScope']='50ms current Windows working-set samples of owned Node PID and Python parent, sequential approximate pairs; not a continuous/private peak'
    return result


def aggregate(reference,old):
    """Independent all-twelve Fraction contrast, no primary analysis import."""
    need(len(reference)==len(old)==12,'Both full endpoint inventories required')
    rows=[];values=[];seeds=[]
    for seed in SEEDS:
        a=[e for e in old if e['seed']==seed];b=[e for e in reference if e['seed']==seed]
        need(len(a)==len(b)==1,'Missing/duplicate paired seed');a,b=a[0],b[0]
        need(a['runId']==f'base-g15-t1--matched5-startup--zero--s{seed}' and b['runId']==plan_id(seed),'Paired treatment identity differs')
        available=a['available'] and b['available']
        delta=fraction(b['cycleCustomerBenefit'])-fraction(a['cycleCustomerBenefit']) if available else None
        rows.append(dict(seed=seed,runIds=[a['runId'],b['runId']],available=available,
                         executionSucceeded=[a['executionSucceeded'],b['executionSucceeded']],replayMatched=[a['replayMatched'],b['replayMatched']],
                         cycleCustomerBenefits=[a['cycleCustomerBenefit'],b['cycleCustomerBenefit']],difference=packed(delta) if available else None,
                         unavailableReason='; '.join(f'{label}: {e["unavailableReason"]}' for label,e in [('startup-guard',a),('full-grid-after-cap',b)] if not e['available']) or None))
        if available:values.append(delta);seeds.append(seed)
    complete=len(values)==12
    return dict(pairedRows=rows,primarySummary=dict(plannedDenominator=12,availablePairs=len(values),available=complete,
                meanDifference=packed(sum(values,Fraction())/12) if complete else None,
                unavailableReason=None if complete else 'At least one required final pair lacks two accepted endpoints'),
                completePairDescription=dict(scope='Secondary available-pair description; never substitutes for the planned all-twelve mean',
                denominator=len(values),seedIds=seeds,signCounts=dict(positive=sum(v>0 for v in values),zero=sum(v==0 for v in values),negative=sum(v<0 for v in values)),
                meanDifference=packed(sum(values,Fraction())/len(values)) if values else None))


def anchor_math(value):
    need(isinstance(value,dict),'Complete static anchor object required')
    need(set(value)=={'n','coordinateOrder','scope','bestResponses','pureNash','jointProfitMaximum'},
         'Complete static anchor schema required')
    need(all(isinstance(value.get(k),str) and value[k].strip() for k in ('coordinateOrder','scope')),
         'Explicit independent static-anchor coordinate/scope description required')
    result=dict(value);result.pop('scope',None);result.pop('coordinateOrder',None)
    result['pureNash']=dict(result['pureNash'])
    reason=result['pureNash'].pop('reason')
    need((reason is None)==(result['pureNash']['count']>0),'Empty Nash set/reason distinction differs')
    if reason is not None:need(isinstance(reason,str) and reason.strip(),'Empty Nash reason absent')
    return result


def check_anchors(node,project,raw,primary):
    result=subprocess.run([node,str(local(project,WORKER)),'--anchors-stdin'],cwd=project,
                          input=json.dumps(raw,allow_nan=False).encode(),capture_output=True,timeout=60,check=False)
    need(result.returncode==0 and len(result.stdout)<=64_000_000,'Independent static anchor process failed')
    computed=parse(result.stdout);same(anchor_math(primary),anchor_math(computed),'All exact static BR/Nash/joint-max scientific fields')
    return computed


def audit_study(project=ROOT, directory=None, node=None, *, dependency_verifier=verify_dependencies,
                replay_runner=run_replay):
    """Full authoritative entry; injected hooks are for wholly artificial tests only."""
    project = Path(project).resolve()
    directory = Path(directory or project/'research/guard-reference-results').resolve()
    node = node or shutil.which('node')
    started = time.perf_counter()
    before = snapshot(directory)
    dependency = dependency_verifier(project, directory, node)
    m = dependency['manifest']
    mh = dependency['studyManifestHash']
    def read(name):
        need(name in before, 'Missing mandatory closed output: '+name)
        return parse(local(directory, name).read_bytes())
    results, index, completion, execution = (read(n) for n in ('results.json','index.json','completion.json','execution-start.json'))
    journal = [parse(b) for b in local(directory,'journal.jsonl').read_bytes().splitlines()]
    for value in (results,index,completion,execution):
        need(value.get('manifestSha256') == mh, 'Output manifest binding differs')
    for name,key in [('results.json','resultsSha256'),('index.json','indexSha256'),('execution-start.json','executionStartSha256'),('journal.jsonl','journalSha256')]:
        need(completion[key] == before[name][1], 'Primary completion output hash mismatch')
    need(completion.get('inventoryComplete') is True and completion['retainedRuns'] == 12
         and completion['retainedCheckpointSlots'] == 24 and completion['fullTrainingReplay'] is False
         and completion['finalFrozenDependencyCheck']['passed'] is True, 'Closed full inventory/final dependency gate absent')
    same(execution['runIds'], [p['id'] for p in m['plan']['runs']], 'Execution-start planned identities')
    gate=parse(reference(project,execution['adminGate']).read_bytes())
    need(execution['adminGate']['sha256']==execution['adminGateSha256'] and gate.get('passed') is True
         and gate.get('studyManifestHash')==mh and gate.get('sourcesVerified') is True
         and gate.get('inputsVerified') is True and gate.get('auditorSourceHash')==digest(local(project,SELF)),
         'Independent pre-execution administrative receipt binding differs')
    for key,source in [('controlAuditorSourceHash',WORKER),('replayCoreSourceHash',CORE)]:
        need(gate.get(key)==digest(local(project,source)),'Administrative component source binding differs')
    same(fingerprint(execution['software']),fingerprint(m['runtime']),'Execution-start runtime')
    same({k:completion['parentRuntime'][k] for k in python_runtime()},python_runtime(),'Completion parent runtime')
    need(len(results['records']) == len(index['records']) == 12 and len(journal) == 26, '12 records/26 ordered anchor/run/completion journal events required')
    raw = parse(reference(project,m['inputs']['finiteGame']).read_bytes())
    need(raw.get('scenario',{}).get('id') == 'base-g15-t1' and len(raw['finite']['prices']) == 62, 'Fixed 62-quote actual game differs')
    anchor_ref=results.get('stageAnchors')
    need(type(completion.get('anchorCalculationPassed')) is bool,'Explicit anchor calculation status required')
    if anchor_ref is None:
        need(completion['stageAnchorsSha256'] is None and completion['anchorCalculationPassed'] is False
             and isinstance(results.get('stageAnchorsFailure'),(dict,str)) and bool(results['stageAnchorsFailure']),
             'Missing anchors must be retained as an explicit calculation failure')
        anchors=dict(available=False,independentAgreement=False,values=None,primaryReference=None,
                     reason='Primary static-anchor calculation unavailable; retained failure is not an anchor certificate')
        need(journal[0].get('type')=='static anchors unavailable','Missing ordered anchor-failure journal event')
        same(journal[0].get('failure'),results['stageAnchorsFailure'],'Anchor-failure journal identity')
    else:
        need(completion['anchorCalculationPassed'] is True and results.get('stageAnchorsFailure') is None,
             'Available anchors contradict retained failure flags')
        primary_anchors=parse(reference(directory,anchor_ref).read_bytes())
        need(completion['stageAnchorsSha256']==anchor_ref['sha256'],'Primary static-anchor binding differs')
        anchors=dict(available=True,independentAgreement=True,values=check_anchors(node,project,raw,primary_anchors),
                     primaryReference=anchor_ref,reason=None)
        need(journal[0].get('type')=='static anchors retained','Missing ordered anchor-retained journal event')
        same(journal[0].get('reference'),anchor_ref,'Anchor reference journal identity')
    same(completion.get('stageAnchorsFailure'),results.get('stageAnchorsFailure'),'Anchor failure completion/result duplication')
    replay_results, endpoints, slots, eligible, raw_bytes = [], [], [], 0, 0
    for i, (plan, record, ix) in enumerate(zip(m['plan']['runs'],results['records'],index['records'])):
        same({k:record[k] for k in ('id','arm','seed','treatment','scientificTreatment')},{k:plan[k] for k in ('id','arm','seed','treatment','scientificTreatment')},'Primary ordered identity')
        need(record.get('manifestSha256') == mh and ix.get('id') == plan['id'] and ix.get('status') == record['status'], 'Indexed record identity/status differs')
        same(parse(reference(directory,ix).read_bytes()),record,'Indexed record/results exact duplication')
        a,b = journal[1+2*i:3+2*i]
        need(a.get('type') == 'run started' and a.get('id') == plan['id']
             and b.get('type') == 'run retained' and b.get('id') == plan['id'] and b.get('status') == record['status'], 'Per-run journal order/identity differs')
        same(b['record'],{k:ix[k] for k in ('file','bytes','sha256')},'Journal record binding')
        audit_events(record,m['plan']['checkpoints'],m['plan']['hardCaseSeconds'])
        if record.get('task') is None:
            need(not record['executionSucceeded'] and not any(s['parentEligible'] for s in record['checkpoints']) and record.get('failure'), 'Missing task without honest precase failure')
            replay = dict(id=plan['id'],replayedRounds=0,fullHorizonReplayed=False,allPlannedCheckpointsMatched=False,checkpointResults=[])
        else:
            for key in ('budgetSeconds','precaseSeconds','wholeCaseSeconds','seconds'):
                need(type(record.get(key)) in (int,float) and math.isfinite(record[key]) and record[key]>=0,'Primary full-case budget/duration metadata absent')
            need(record['budgetSeconds']>0 and abs(record['budgetSeconds']+record['precaseSeconds']-m['plan']['hardCaseSeconds'])<1e-6
                 and record['wholeCaseSeconds']>=record['seconds'],'Primary budget does not account for precase work')
            task_file=reference(directory,record['task'])
            task=parse(task_file.read_bytes())
            expected=dict(plan=plan,scientificTreatment=SCIENTIFIC_TREATMENT,record=raw,finite=raw['finite'],originalTargets=raw.get('originalTargets',[]),
                          finiteGameRef=m['inputs']['finiteGame'],software=m['runtime'],T=m['plan']['T'],
                          checkpoints=m['plan']['checkpoints'],manifestSha256=mh,executionMode='frozen-primary',projectRoot='.')
            same(task,expected,'Complete fixed-model task; no hidden numerical override')
            if record.get('parentRuntime') is not None:
                same({k:record['parentRuntime'][k] for k in python_runtime()},python_runtime(),'Per-run parent runtime')
            for slot in record['checkpoints']:
                if slot['parentEligible']:
                    meta=parse(reference(directory,slot['metadata']).read_bytes())
                    eligible+=1
                    for refs in meta['artifacts'].values():
                        for ref in refs:
                            reference(directory,ref)
                            need(type(ref.get('rawBytes')) is int and ref['rawBytes'] >= 0,'Dense byte count invalid')
                            raw_bytes+=ref['rawBytes']
                    for refs in meta['policies'].values():
                        for ref in refs:
                            reference(directory,ref)
                    reference(directory,meta['graph'])
            replay=replay_runner(node,project,directory,task_file,local(directory,ix['file']),m['plan']['hardCaseSeconds'])
            need(replay.get('id',plan['id']) == plan['id'],'Replay run identity differs')
            if not replay.get('operationalFailure'):
                need(replay.get('finalConsumedIntegrityCheck') is True,'Independent consumed-artifact final integrity check missing')
        check_by_step={s['step']:s for s in replay.get('checkpointResults',[])}
        need(len(check_by_step) == len(replay.get('checkpointResults',[])), 'Duplicate independently audited checkpoint')
        for cp in record['checkpoints']:
            checked=check_by_step.get(cp['step'])
            available=cp['parentEligible'] and checked is not None and checked.get('matched') is True and checked.get('available') is True and not replay.get('operationalFailure')
            if available:
                need(checked['metadataSha256'] == cp['metadata']['sha256'],'Replay checkpoint source differs')
                need(type(checked['phase']) is int and checked['phase'] == 4 and type(checked['cycleLength']) is int
                     and 0<checked['cycleLength']<=4*62*62 and checked['cycleLength']%4==0,'Accepted terminal phase/cycle differs')
                fraction(checked['cycleCustomerBenefit'],True)
            reason=None if available else (checked or {}).get('reason',replay.get('operationalFailure') or cp['reason'])
            slots.append(dict(runId=plan['id'],seed=plan['seed'],arm=plan['arm'],step=cp['step'],
                              parentEligible=cp['parentEligible'],scientificAvailable=available,
                              replayMatched=available,reason=reason))
            if cp['step']==2_000_000:
                endpoint=dict(seed=plan['seed'],arm=plan['arm'],runId=plan['id'],executionSucceeded=record['executionSucceeded'],
                              available=available,replayMatched=available,cycleCustomerBenefit=packed(fraction(checked['cycleCustomerBenefit'],True)) if available else None,
                              unavailableReason=reason)
                if available:
                    endpoint.update(step=2_000_000,nextPhase=checked['phase'],previousIndices=checked['previousIndices'],
                                    cycleLength=checked['cycleLength'],checkpointSha256=checked['metadataSha256'],graphSha256=checked['graphSha256'])
                endpoints.append(endpoint)
        replay_results.append(replay)
    need(journal[-1].get('type')=='inventory completed' and journal[-1].get('retainedRuns')==12,'Final journal completion missing')
    same(journal[-1]['finalFrozenDependencyCheck'],completion['finalFrozenDependencyCheck'],'Journal final dependency gate')
    failures=sum(not r['executionSucceeded'] for r in results['records'])
    same(completion['executionFailures'],failures,'Execution failure count')
    same(completion['executionPassed'],failures==0,'Explicit execution success count')
    same(completion['budgetFailures'],sum(r['status']=='timeout' for r in results['records']),'Primary budget-failure count')
    same(completion['parentEligibleCheckpoints'],eligible,'Eligible checkpoint count')
    same(completion['primaryPassed'],failures==0 and anchors['available'],'Primary overall success/anchor distinction')
    same(completion['resources']['rawEquivalentEligibleCheckpointBytes'],raw_bytes,'Canonical dense byte budget accounting')
    dense_compressed=sum(ref['bytes'] for r in results['records'] for cp in r['checkpoints'] if cp['parentEligible']
                         for refs in parse(reference(directory,cp['metadata']).read_bytes())['artifacts'].values() for ref in refs)
    same(completion['resources']['eligibleCompressedDenseBytes'],dense_compressed,'Compressed dense byte accounting')
    primary_names={'manifest.json','execution-start.json','journal.jsonl','index.json','results.json'}
    if anchor_ref is not None:primary_names.add(anchor_ref['file'])
    stored=sum(v[0] for name,v in before.items() if name in primary_names or name.startswith(('sources/','tasks/','checkpoints/','records/')))
    same(completion['resources']['storedBytesBeforeCompletion'],stored,'Closed primary output byte accounting')
    raw_total=stored-dense_compressed+raw_bytes if eligible==24 else None
    same(completion['resources']['rawEquivalentOutputBytesBeforeCompletion'],raw_total,'Full raw-equivalent output accounting')
    same(completion['resources']['rawEquivalentOutputSoftTargetExceeded'],raw_total>1_000_000_000 if raw_total is not None else None,'Primary output soft-target flag')
    samples=[s for r in results['records'] for s in r.get('rssSamples',[])]
    nodes=[s['nodeProcessRSSBytes'] for s in samples if s.get('nodeProcessRSSBytes') is not None]
    pairs=[s['nodeProcessRSSBytes']+s['supervisorRSS']['bytes'] for s in samples if s.get('nodeProcessRSSBytes') is not None and s.get('supervisorRSS',{}).get('bytes') is not None]
    need(all(type(x) is int and x>0 for x in nodes+pairs),'Invalid measured working-set sample')
    same(completion['resources']['largestSampledNodeProcessRSSBytes'],max(nodes,default=None),'Primary Node RSS maximum')
    same(completion['resources']['largestApproximatelyPairedRSSBytes'],max(pairs,default=None),'Approximate paired RSS maximum')
    same(completion['resources']['sampledPairedRSSSoftTargetExceeded'],max(pairs)>512_000_000 if pairs else None,'Primary RSS soft-target flag')
    need(type(completion['resources'].get('seconds')) in (int,float) and math.isfinite(completion['resources']['seconds']) and completion['resources']['seconds']>=0,'Primary elapsed time missing')
    same(completion['resources']['primarySecondsSoftTargetExceeded'],completion['resources']['seconds']>3600,'Primary time soft-target flag')
    if not pairs:
        need(isinstance(completion['resources'].get('pairedRSSUnavailableReason'),str),'Missing RSS reason')
    # These checks run AFTER every replay. No provisional endpoint survives global drift.
    after_dependency=dependency_verifier(project,directory,node)
    same(after_dependency['studyManifestHash'],mh,'Final manifest integrity')
    same(snapshot(directory),before,'Global primary output integrity')
    available=sum(s['scientificAvailable'] for s in slots)
    replayed=sum(r['replayedRounds'] for r in replay_results)
    distinct_blocks=sum(r.get('transcriptBlocksMatched',0) for r in replay_results)
    full=available==24 and replayed==24_000_000 and distinct_blocks==2400 and all(r['fullHorizonReplayed'] and r['allPlannedCheckpointsMatched'] for r in replay_results)
    independent=aggregate(endpoints,dependency['oldComparisonEndpoints'])
    controls=[]
    for label,changed,expected in [('boolean-integer identity',True,1),('missing final seed identity',[],[1]),('fixed source hash drift','0'*64,'1'*64)]:
        try:
            same(changed,expected,label)
        except ValueError:
            controls.append(dict(test=label,rejected=True))
        else:
            raise ValueError('Inventory corruption control unexpectedly accepted')
    scientific_controls=[dict(runId=r.get('id'),step=cp['step'],metadataSha256=cp['metadataSha256'],checks=cp['corruptionNegativeControls'])
                         for r in replay_results for cp in r.get('checkpointResults',[]) if cp.get('matched') is True]
    for item in scientific_controls:
        need(len(item['checks'])==14 and all(x.get('rejected') is True for x in item['checks']),'Incomplete scientific negative controls')
    replay_samples=[s for r in replay_results for s in r.get('rssSamples',[])]
    paired_peak=max((s['approximatelyPairedRSSBytes'] for s in replay_samples if s['approximatelyPairedRSSBytes'] is not None),default=None)
    seconds=time.perf_counter()-started
    return dict(passed=True,inventoryAccepted=True,independentAuditPassed=True,studyManifestHash=mh,
                auditorSourceHash=digest(local(project,SELF)),controlAuditorSourceHash=digest(local(project,WORKER)),
                replayCoreSourceHash=digest(local(project,CORE)),
                resultsSha256=before['results.json'][1],indexSha256=before['index.json'][1],
                completionSha256=before['completion.json'][1],journalSha256=before['journal.jsonl'][1],
                executionStartSha256=before['execution-start.json'][1],
                stageAnchorsSha256=anchor_ref['sha256'] if anchor_ref else None,
                runs=12,checkpointSlots=24,scientificallyAvailableCheckpoints=available,
                finalAvailable=sum(e['available'] for e in endpoints),replayedRounds=replayed,
                roundTranscriptBlocksMatched=distinct_blocks,
                fullTrainingReplay=full,replayComplete=full,executionPassed=failures==0,primaryPassed=completion['primaryPassed'],
                executionFailures=failures,checkpointResults=slots,finalEndpoints=endpoints,
                runReplayResults=replay_results,independentSummaries=independent,
                inheritedFinalEndpoints=dependency['oldComparisonEndpoints'],
                corruptionNegativeControls=controls,scientificCorruptionNegativeControls=scientific_controls,
                actualScientificNegativeControlsAvailable=bool(scientific_controls),finalSourceInputOutputIntegrityCheck=True,
                scientificNegativeControlScope='Read-only actual-case altered claim/bit comparator controls, not end-to-end replays of mutated serialized evidence. Separate artificial serialization tests exercise fresh-hash artifact-family corruptions end-to-end.',
                resources=dict(seconds=seconds,primary=completion['resources'],
                               largestSampledReplayNodeRSSBytes=max((s['nodeRSSBytes'] for s in replay_samples if s['nodeRSSBytes'] is not None),default=None),
                               largestApproximatelyPairedReplayRSSBytes=paired_peak,
                               pairedRSSUnavailableReason=None if paired_peak is not None else 'No usable approximate paired replay working-set sample',
                               replaySecondsSoftTargetExceeded=seconds>3600,replayRSSSoftTargetExceeded=paired_peak>512000000 if paired_peak is not None else None,
                               scope='Independent parent samples owned replay child and itself every50ms, sequential approximate paired working sets; missed short peaks remain possible. Primary and replay resource phases remain separate.'),
                acceptedAt=timestamp(),
                acceptedOldComparison=dependency['acceptedOldComparison'],anchors=anchors,
                scope='Inventory acceptance is distinct from numerical availability. Independently authored direct-scan replay from zero checks all available endpoint bytes, every stored transcript block, complete graphs/windows/curves. Shared V8/Math.exp/crypto/zlib backend and inherited audited saved payoff/mask premises; no old economic re-enumeration, no cross-runtime proof. Every-round block hashes are compared, not authenticated original per-round logs. New-reference full replay requires all12 full horizons and all24 checkpoints. Old comparison acceptance is reused, not retrained or replayed. No inferential interval or convergence/equilibrium claim.')


def write_exclusive(path,value):
    path=Path(path)
    need(not path.exists(),'Refusing to overwrite any existing receipt')
    with path.open('x',encoding='utf-8',newline='\n') as out:
        out.write(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',default=str(ROOT))
    parser.add_argument('--directory')
    parser.add_argument('--admin-only',action='store_true')
    parser.add_argument('--output')
    args=parser.parse_args()
    if args.output:
        need(not Path(args.output).exists(),'Refusing to overwrite any existing receipt before doing audit work')
    directory=Path(args.directory or Path(args.project)/'research/guard-reference-results')
    value=verify_dependencies(args.project,directory) if args.admin_only else audit_study(args.project,directory)
    if args.admin_only:
        value.pop('manifest',None); value.pop('oldComparisonEndpoints',None)
    if args.output:
        write_exclusive(args.output,value)
    else:
        print(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False))
