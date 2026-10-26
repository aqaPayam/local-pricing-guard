"""Read-only, audit-gated matched-study derivatives. Import performs no IO.

No learner, replay, optimizer, Q decoder or economic table generator is called.
An explicitly accepted audit path AND SHA are required by the command line.
"""
import argparse
import base64
import csv
import hashlib
import io
import json
import re
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = tuple(range(907001, 907013))
ARMS = ('startup', 'recurring4')
STEPS = (1_000_000, 2_000_000)
SOURCE_KEYS = dict(auditorSourceHash='research/audit-matched-clock-study.py',
                   controlAuditorSourceHash='research/replay-matched-clock.js',
                   replayCoreSourceHash='research/audit-matched-clock.js')
CORE_KEYS = {'results.json': 'resultsSha256', 'index.json': 'indexSha256',
             'completion.json': 'completionSha256', 'journal.jsonl': 'journalSha256',
             'execution-start.json': 'executionStartSha256'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def local(root, name):
    require(isinstance(name, str) and name and '\\' not in name and ':' not in name
            and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')),
            'Unsafe consumed reference')
    root = Path(root).resolve()
    path = (root / name).resolve()
    require(path != root and path.is_relative_to(root), 'Reference escapes its declared root')
    return path


class Tracker:
    def __init__(self):
        self.files = {}

    def verify(self, path, expected, size=None):
        path = Path(path).resolve()
        require(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected), 'Missing expected SHA256')
        require(path.is_file() and (size is None or path.stat().st_size == size), 'Missing/changed file length: ' + str(path))
        actual = (path.stat().st_size, digest(path))
        require(actual[1] == expected, 'Consumed file hash differs: ' + str(path))
        require(path not in self.files or self.files[path] == actual, 'Consumed file changed during read')
        self.files[path] = actual
        return path

    def ref(self, root, ref, *, read=False, ceiling=100_000_000):
        require(isinstance(ref, dict) and type(ref.get('bytes')) is int and 0 <= ref['bytes'] <= ceiling,
                'Invalid bounded consumed reference')
        p = self.verify(local(root, ref['file']), ref.get('sha256'), ref['bytes'])
        return p.read_bytes() if read else p

    def json_ref(self, root, ref):
        return json.loads(self.ref(root, ref, read=True))

    def close(self):
        for path, (size, sha) in self.files.items():
            require(path.is_file() and path.stat().st_size == size and digest(path) == sha,
                    'Source/input/output changed before derivative closure: ' + str(path))
        return len(self.files)


def ref_at(root, name):
    p = local(root, name)
    return dict(file=name, bytes=p.stat().st_size, sha256=digest(p))


def same(a, b, message):
    # JSON type equality rejects bool-as-int while ignoring map insertion order.
    require(json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False), message)


def planned():
    return [dict(id=f'base-g15-t1--matched5-{arm}--zero--s{seed}', arm=arm, seed=seed)
            for seed in SEEDS for arm in ARMS]


def exact_only(value):
    require(isinstance(value, dict), 'Missing exact graph ratio')
    return {k: value[k] for k in ('numerator', 'denominator')}


def load_analysis(path):
    # Compile the hash-verified source itself: an unbound pyc cache is not an input.
    module = types.ModuleType('bound_matched_analysis')
    module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(),str(path),'exec'),module.__dict__)
    return module


def policy_ref(raw, expected):
    require(len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256'], 'Policy bytes changed')
    return dict(base64=base64.b64encode(raw).decode(), bytes=len(raw), sha256=expected['sha256'])


def build(project, directory, audit_file, audit_sha, *, before_final_check=None):
    """Build in memory; tests may inject a drift callback, never an acceptance bypass."""
    project, directory = Path(project).resolve(), Path(directory).resolve()
    require(directory.is_relative_to(project) and directory != project, 'Study must be project-local')
    tracker = Tracker()
    builder_file='research/build-matched-clock-web.py'
    builder_sha=digest(__file__)
    tracker.verify(local(project,builder_file),builder_sha)
    audit_path = Path(audit_file).resolve()
    require(audit_path.is_relative_to(project), 'Accepted receipt must be project-local')
    tracker.verify(audit_path, audit_sha)
    audit = json.loads(audit_path.read_bytes())
    require(audit.get('passed') is True and audit.get('inventoryAccepted') is True
            and audit.get('independentAuditPassed') is True
            and audit.get('finalSourceInputOutputIntegrityCheck') is True, 'Authoritative inventory/integrity acceptance missing')
    manifest_path = tracker.verify(directory/'manifest.json', audit.get('studyManifestHash'))
    manifest = json.loads(manifest_path.read_bytes())
    sources, inputs = manifest.get('sourceHashes'), manifest.get('inputHashes')
    require(isinstance(sources, dict) and len(sources) == 29 and isinstance(inputs, dict), 'Frozen 29-source closure missing')
    for name, sha in sources.items():
        tracker.verify(local(project, name), sha)
        tracker.verify(local(directory, 'sources/'+name), sha)
    for name, sha in inputs.items():
        tracker.verify(local(project, name), sha)
    for key, name in SOURCE_KEYS.items():
        require(audit.get(key) == sources.get(name), 'Live authoritative auditor source binding differs: '+key)
    require('research/matched-clock-analysis.py' in sources, 'Frozen pure aggregator omitted')
    plan = manifest.get('plan', {})
    expected = planned()
    same([{k: p.get(k) for k in ('id', 'arm', 'seed')} for p in plan.get('runs', [])], expected, 'Complete ordered 24-run matrix differs')
    require(plan.get('T') == 2_000_000 and plan.get('checkpoints') == list(STEPS), 'Frozen horizon/checkpoints differ')
    core = {}
    core_refs = {}
    for name, key in CORE_KEYS.items():
        p = tracker.verify(directory/name, audit.get(key))
        core_refs[name] = dict(file=name, bytes=p.stat().st_size, sha256=audit[key])
        core[name] = [json.loads(row) for row in p.read_bytes().splitlines()] if name.endswith('.jsonl') else json.loads(p.read_bytes())
    results, index, completion, execution = (core[n] for n in ('results.json','index.json','completion.json','execution-start.json'))
    for value in (results,index,completion,execution):
        require(value.get('manifestSha256') == audit['studyManifestHash'], 'Core output manifest differs')
    for name, key in CORE_KEYS.items():
        if name != 'completion.json':
            require(completion.get(key) == audit[key], 'Completion/core output binding differs')
    require(completion.get('inventoryComplete') is True and completion.get('retainedRuns') == 24
            and completion.get('retainedCheckpointSlots') == 48
            and completion.get('finalFrozenDependencyCheck', {}).get('passed') is True, 'Closed inventory/dependency check missing')
    require(audit.get('runs') == 24 and audit.get('checkpointSlots') == 48
            and len(results.get('records', [])) == len(index.get('records', [])) == 24, 'All retained run slots required')
    require(len(core['journal.jsonl']) == 49, 'Complete run journal required')
    if execution.get('adminGate') is not None:
        gate = tracker.json_ref(project, execution['adminGate'])
        require(gate.get('passed') is True and gate.get('studyManifestHash') == audit['studyManifestHash'], 'Administrative receipt differs')
    raw = tracker.json_ref(project, manifest['inputs']['finiteGame'])
    finite = raw.get('finite', {})
    require(raw.get('scenario', {}).get('id') == 'base-g15-t1' and len(finite.get('prices', [])) == 62, 'Bound unchanged 62-price game required')
    n, states = 62, 5*62*62
    for key in ('consumerSurplus','profitA','profitB','quantityA','quantityB'):
        require(len(finite.get('rewards', {}).get(key, [])) == n*n, 'Saved finite table dimensions differ')
    endpoints, slots = audit.get('finalEndpoints'), audit.get('checkpointResults')
    require(isinstance(endpoints, list) and len(endpoints) == 24 and isinstance(slots, list) and len(slots) == 48,
            'All independently assessed endpoint slots required')
    by_endpoint = {e.get('runId'): e for e in endpoints}
    by_slot = {(s.get('runId'),s.get('step')): s for s in slots}
    require(len(by_endpoint) == 24 and len(by_slot) == 48, 'Duplicate independent endpoint identities')
    analysis = load_analysis(local(project,'research/matched-clock-analysis.py'))
    aggregated = analysis.aggregate(endpoints)
    same(aggregated, audit.get('independentSummaries'), 'Frozen aggregate(finalEndpoints) differs from independently computed summaries')
    checkpoints, policies, runs = [], [], []
    for expected_run, record, ix in zip(expected, results['records'], index['records']):
        same({k:record.get(k) for k in expected_run},expected_run,'Retained record identity differs')
        require(ix.get('id') == record['id'] and ix.get('status') == record.get('status'), 'Indexed status differs')
        same(tracker.json_ref(directory,ix),record,'Index/aggregate record duplication differs')
        if record.get('task') is not None:
            task = tracker.json_ref(directory,record['task'])
            require(task.get('manifestSha256') == audit['studyManifestHash'] and task.get('finiteGameRef') == manifest['inputs']['finiteGame'], 'Task input binding differs')
            same(task.get('record'),raw,'Task does not contain the unchanged input record')
        require([s.get('step') for s in record.get('checkpoints', [])] == list(STEPS), 'Planned primary checkpoint slots differ')
        runs.append(dict(id=record['id'],seed=record['seed'],arm=record['arm'],status=record['status'],executionSucceeded=record['executionSucceeded'],failure=record.get('failure'),checkpointIds=[record['id']+f'--t{t}' for t in STEPS]))
        for slot in record['checkpoints']:
            key=(record['id'],slot['step']);checked=by_slot.get(key)
            require(checked is not None and checked.get('seed') == record['seed'] and checked.get('arm') == record['arm']
                    and checked.get('parentEligible') == slot.get('parentEligible'), 'Authoritative checkpoint/parent identity differs')
            available=checked.get('scientificAvailable') is True
            require(checked.get('replayMatched') is available, 'Endpoint acceptance/replay differs')
            meta=graph=None;world=None
            if slot.get('parentEligible'):
                meta=tracker.json_ref(directory,slot['metadata'])
                require(meta.get('id') == record['id'] and meta.get('step') == slot['step'] and meta.get('arm') == record['arm']
                        and meta.get('seed') == record['seed']
                        and meta.get('finiteGameRef') == manifest['inputs']['finiteGame'], 'Bound checkpoint metadata identity differs')
                if available:
                    require(meta.get('n') == n and meta.get('phases') == 5, 'Accepted dense dimensions differ')
                # Hash every compressed dense artifact, without inflating/decoding Q.
                # A parent-eligible but scientifically rejected slot remains in
                # the integrity closure; its numerical claims are NOT adopted.
                for family,width,encoding in [('q',8,'f64le'),('counts',4,'u32le')]:
                    refs=meta.get('artifacts',{}).get(family,[]);require(isinstance(refs,list),'Invalid bound dense reference list')
                    if available:
                        require(len(refs)==2,'Both accepted dense artifact families required')
                    for ref in refs:
                        if available:
                            require(ref.get('rawBytes')==5*n*n*n*width and ref.get('encoding')==encoding
                                    and ref.get('compression')=='gzip-single-member' and re.fullmatch('[a-f0-9]{64}',ref.get('rawSha256','')), 'Accepted compressed dense metadata differs')
                        tracker.ref(directory,ref,ceiling=5*n*n*n*width+65536)
                own=[];world=[]
                for family,output in [('own',own),('world',world)]:
                    refs=meta.get('policies',{}).get(family,[]);require(isinstance(refs,list),'Invalid bound policy reference list')
                    if available:
                        require(len(refs)==2,'Both accepted policy orientations required')
                    for ref in refs:
                        if available:
                            require(ref.get('bytes')==states,'Accepted policy dimension differs')
                            output.append(tracker.ref(directory,ref,read=True,ceiling=states))
                        else:
                            tracker.ref(directory,ref)
                if available:
                    graph=tracker.json_ref(directory,meta['graph'])
                    require(graph.get('policySha256')==[r['sha256'] for r in meta['policies']['own']]
                            and graph.get('worldPolicySha256')==[r['sha256'] for r in meta['policies']['world']], 'Accepted graph/policy file binding differs')
                    for node in range(states):
                        phase,pa,pb=node//(n*n),(node//n)%n,node%n
                        require(world[0][node]==own[0][node] and world[1][node]==own[1][phase*n*n+pb*n+pa],'WORLD B policy was not mapped exactly once')
                        cap=phase==0 or (record['arm']=='recurring4' and phase==4)
                        for firm,previous in ((0,pb),(1,pa)):
                            require(world[firm][node] in (range(finite['capIndex']+1) if cap else finite['sets'][previous]),'Saved world policy violates mask')
                else:
                    tracker.ref(directory,meta['graph'])
            require(not available or (slot.get('parentEligible') and meta is not None),'Scientific endpoint lacks complete primary evidence')
            reason=None if available else checked.get('reason') or slot.get('reason')
            require(available or isinstance(reason,str) and reason.strip(),'Unavailable endpoint reason required')
            public=dict(id=record['id']+f"--t{slot['step']}",runId=record['id'],seed=record['seed'],arm=record['arm'],step=slot['step'],status='accepted' if available else 'unavailable',reason=reason,executionSucceeded=record['executionSucceeded'],scientificAvailable=available,
                        receiptTiming=record.get('events',[]),sourceRefs=dict(metadata=slot.get('metadata'),graph=meta['graph'] if meta else None),replayStatus=dict(accepted=available,parentEligible=slot['parentEligible']),terminal=dict(meta['terminal'],capExecutions=meta['caps']) if available else None,
                        trainingTail=next((w for w in meta['windowMetrics'] if w['endStep']==slot['step']),None) if available else None,coverage=graph.get('coverage') if available else None,frozen=graph if available else None,preview128=graph['terminalPreview128'] if available else None)
            checkpoints.append(public)
            if slot['step']==2_000_000:
                endpoint=by_endpoint.get(record['id']);require(endpoint is not None and endpoint['available']==available,'Final independent availability differs')
                if available:
                    require(endpoint['checkpointSha256']==slot['metadata']['sha256'] and endpoint['graphSha256']==meta['graph']['sha256'],'Final accepted artifact binding differs')
                    same(endpoint['cycleCustomerBenefit'],exact_only(graph['actualTerminal']['cycleMetrics']['consumerSurplus']),'Graph/independent final endpoint differs')
                    same(endpoint['previousIndices'],meta['terminal']['previousIndices'],'Final actual history differs')
                policies.append(dict(checkpointId=public['id'],runId=record['id'],seed=record['seed'],arm=record['arm'],available=available,reason=reason,start=meta['terminal'] if available else None,encoding='uint8 WORLD row-major (phase,previousA,previousB)',states=states,policies={name:policy_ref(world[f],meta['policies']['world'][f]) for f,name in enumerate(('A','B'))} if available else None))
    accepted=sum(c['scientificAvailable'] for c in checkpoints)
    require(accepted==audit.get('scientificallyAvailableCheckpoints') and sum(p['available'] for p in policies)==audit.get('finalAvailable'),'Independent available counts differ')
    require(type(audit.get('fullTrainingReplay')) is bool and audit.get('fullTrainingReplay') is audit.get('replayComplete'),'Aggregate replay flags differ')
    if audit['fullTrainingReplay']:
        require(accepted==48 and audit.get('replayedRounds')==48_000_000,'Aggregate full replay cannot omit secondary checkpoints')
    pairs=[]
    for p in aggregated['pairedRows']:
        pairs.append(dict(seed=p['seed'],available=p['available'],reason=p['unavailableReason'],difference=p['difference'],startup=dict(checkpointId=p['runIds'][0]+'--t2000000',consumerSurplus=p['cycleCustomerBenefits'][0]),recurring4=dict(checkpointId=p['runIds'][1]+'--t2000000',consumerSurplus=p['cycleCustomerBenefits'][1])))
    primary=aggregated['primarySummary']
    meta=dict(inventoryAccepted=True,independentAuditPassed=True,audit=dict(passed=True,file=audit_path.relative_to(project).as_posix(),sha256=audit_sha),independentAuditSha256=audit_sha,primaryManifestSha256=audit['studyManifestHash'],coreOutputRefs=core_refs,
              sourceHashes=sources,inputHashes=inputs,studyDirectory=directory.relative_to(project).as_posix(),fullTrainingReplay=audit['fullTrainingReplay'],replayComplete=audit['replayComplete'],replayedRounds=audit['replayedRounds'],availableCheckpoints=accepted,finalAvailable=audit['finalAvailable'],defaultSelection=dict(seed=907001,checkpointStep=2_000_000,arms=list(ARMS),chosenBeforeMatchedOutcomeInspection=True),runtime=manifest['runtime'],parentRuntime=manifest['parentRuntime'],scope='Authoritative inventory/integrity acceptance; endpoint availability and aggregate replay completion are distinct. New matched study only; prior project outcomes were known before this follow-up.')
    web=dict(schemaVersion=1,meta=meta,orderedSeeds=list(SEEDS),arms=[dict(id=a,label='One initial limit' if a=='startup' else 'Repeated limits',nextPhase=[1,2,3,4,1],capPhases=[0] if a=='startup' else [0,4]) for a in ARMS],finiteGame=dict(finite,source=manifest['inputs']['finiteGame'],scenario=raw['scenario'],n=n),runs=runs,checkpoints=checkpoints,finalPolicyPairs=policies,pairedRows=pairs,primarySummary=dict(available=primary['available'],reason=primary['unavailableReason'],plannedPairs=12,acceptedPairs=primary['availablePairs'],mean=primary['meanDifference']),completePairDescription=aggregated['completePairDescription'],resourceReceipt=audit.get('resources'),scope='Read-only offline accepted-evidence export. No Q decoding, new learning, policy search or payoff enumeration. Exact saved-weight cycle and finite replay have separate scopes.')
    meta['builderSource']=dict(file=builder_file,sha256=builder_sha)
    meta['auditSummary']={k:audit[k] for k in ('runs','checkpointSlots','scientificallyAvailableCheckpoints','finalAvailable','replayedRounds','fullTrainingReplay','replayComplete','executionPassed','executionFailures','resources','scope') if k in audit}
    meta['consumedFiles']={path.relative_to(project).as_posix():dict(bytes=size,sha256=sha) for path,(size,sha) in sorted(tracker.files.items(),key=lambda v:str(v[0]))}
    summary=dict(schemaVersion=1,meta=meta,inputHashes=inputs,sourceHashes=sources,runs=runs,checkpoints=[{k:c[k] for k in ('id','runId','seed','arm','step','scientificAvailable','executionSucceeded','status','reason')} for c in checkpoints],finalEndpoints=endpoints,checkpointResults=slots,**aggregated,resources=audit.get('resources'))
    pairs_csv=io.StringIO(newline='');writer=csv.writer(pairs_csv);writer.writerow(['seed','available','startup_cycle_numerator','startup_cycle_denominator','recurring_cycle_numerator','recurring_cycle_denominator','difference_numerator','difference_denominator','reason'])
    for row in pairs:
        vals=[row['seed'],row['available']]
        for key in ('startup','recurring4'):
            value=row[key]['consumerSurplus'];vals.extend([value['numerator'],value['denominator']] if value else ['',''])
        value=row['difference'];vals.extend([value['numerator'],value['denominator']] if value else ['','']);vals.append(row['reason'] or '');writer.writerow(vals)
    statuses=io.StringIO(newline='');writer=csv.writer(statuses);writer.writerow(['runId','seed','arm','step','executionSucceeded','scientificAvailable','reason'])
    for row in checkpoints:writer.writerow([row[k] for k in ('runId','seed','arm','step','executionSucceeded','scientificAvailable','reason')])
    if before_final_check:
        before_final_check()
    count=tracker.close()
    return dict(outputs={'analysis.json':encoded(summary),'web-data.json':encoded(web),'paired-results.csv':pairs_csv.getvalue().encode(),'checkpoint-statuses.csv':statuses.getvalue().encode()},verification=dict(passed=True,consumedFiles=count,auditSha256=audit_sha,scientificallyAvailableCheckpoints=accepted,finalAvailable=audit['finalAvailable'],fullTrainingReplay=audit['fullTrainingReplay'],builderSourceSha256=digest(__file__),scope='Read-only hash-bound derivatives; compressed dense bytes verified, not inflated/Q-decoded'),tracker=tracker)


def load_accepted(summary_path, expected_audit_sha, *, project=ROOT):
    """Reusable authoritative report/figure gate, with no output writes/Q decode.

    Reassembles the deterministic summary in memory from the actual accepted
    receipt/manifest and every bound artifact. A summary's self-declared maps
    or resource/status fields are never trusted as their own authority.
    """
    project=Path(project).resolve();summary_path=Path(summary_path).resolve()
    require(summary_path.is_relative_to(project),'Summary must be project-local')
    raw=summary_path.read_bytes();summary=json.loads(raw);meta=summary.get('meta',{})
    require(meta.get('independentAuditSha256')==expected_audit_sha,'Expected accepted audit SHA differs')
    directory=local(project,meta.get('studyDirectory'))
    audit_path=local(project,meta.get('audit',{}).get('file'))
    bundle=build(project,directory,audit_path,expected_audit_sha)
    require(raw==bundle['outputs']['analysis.json'],'Summary differs from authoritative deterministic regeneration')
    require(summary_path.read_bytes()==raw,'Summary changed during validation')
    bundle['tracker'].close()
    return summary


def write_outputs(bundle, output):
    output=Path(output).resolve()
    require(not any((output/name).exists() for name in bundle['outputs']), 'Existing/partial derivatives retained; refusing overwrite')
    output.mkdir(parents=True,exist_ok=True)
    for name,raw in bundle['outputs'].items():
        with (output/name).open('xb') as handle:
            handle.write(raw)
    bundle['tracker'].close()
    return bundle['verification']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',default=str(ROOT));parser.add_argument('--directory',default='research/matched-clock-results')
    parser.add_argument('--audit',required=True);parser.add_argument('--audit-sha',required=True);parser.add_argument('--output')
    args=parser.parse_args();project=Path(args.project).resolve();directory=local(project,args.directory)
    bundle=build(project,directory,local(project,args.audit),args.audit_sha)
    print(json.dumps(write_outputs(bundle,Path(args.output).resolve() if args.output else directory)))
