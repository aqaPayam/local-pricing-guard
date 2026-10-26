"""Prospective audit-gated reference derivatives. Import performs no IO.

No Q decompression/decoding, learner, replay or new anchor selection is called.
Actual use requires an explicitly accepted new authoritative audit SHA.
"""
import argparse
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import types

ROOT=Path(__file__).resolve().parents[1]
UTILITY='research/build-matched-clock-web.py'
UTILITY_SHA='8819178086fe455987a10c66e26dedb0c8ef3ca2ca4980e529a4e24e534ceaa0'
SELF='research/build-guard-reference-web.py'
SEEDS=tuple(range(907001,907013))
STEPS=(1000000,2000000)
TREATMENTS=('startup-guard','full-grid-after-cap')
SCIENTIFIC=dict(capClock='startup',supportMode='full-grid-after-cap',initialCap=True,postInitialOriginalIndices='all')
SOURCE_KEYS=dict(auditorSourceHash='research/audit-guard-reference-study.py',controlAuditorSourceHash='research/replay-guard-reference.js',replayCoreSourceHash='research/audit-guard-reference.js')
IMMUTABLE_SOURCE='research/audit-matched-clock.js'
IMMUTABLE_SHA='43bd5ed658a976248c685bc71aff4f0d0817cec06993f2351a8d79ef89be7cb3'
CORE_KEYS={'results.json':'resultsSha256','index.json':'indexSha256','completion.json':'completionSha256','journal.jsonl':'journalSha256','execution-start.json':'executionStartSha256'}


def require(ok,message):
    if not ok:raise ValueError(message)


def compile_bound(path,expected):
    raw=Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==expected,'Compiled source bytes changed: '+str(path))
    module=types.ModuleType('bound_guard_reference_'+Path(path).stem.replace('-','_'))
    module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def scientific(treatment):
    return dict(capClock='startup',supportMode=treatment,initialCap=True,postInitialOriginalIndices='all' if treatment==TREATMENTS[1] else 'original rival-dependent guard')


def run_id(seed,treatment):
    return f'base-g15-t1--full-grid-after-cap--zero--s{seed}' if treatment==TREATMENTS[1] else f'base-g15-t1--matched5-startup--zero--s{seed}'


def mathematical_anchors(value):
    value=copy.deepcopy(value)
    require(isinstance(value,dict),'Complete raw static-anchor object required')
    value.pop('coordinateOrder',None);value.pop('scope',None)
    pure=value.get('pureNash',{})
    require(type(pure.get('count')) is int and pure.get('count')==len(pure.get('pairs',[])),'Static pure-Nash count differs')
    reason=pure.pop('reason',None)
    require(reason is None if pure['count'] else isinstance(reason,str) and bool(reason.strip()),'Empty Nash explanation differs')
    return value


def build(project,directory,audit_file,audit_sha,*,before_final_check=None):
    project,directory=Path(project).resolve(),Path(directory).resolve()
    require(directory.is_relative_to(project) and directory!=project,'Study must be project-local')
    utility_path=project/UTILITY
    u=compile_bound(utility_path,UTILITY_SHA)
    tracker=u.Tracker();tracker.verify(utility_path,UTILITY_SHA)
    builder_sha=u.digest(__file__);tracker.verify(u.local(project,SELF),builder_sha)
    audit_path=Path(audit_file).resolve();require(audit_path.is_relative_to(project),'Accepted audit must be project-local')
    tracker.verify(audit_path,audit_sha);audit=json.loads(audit_path.read_bytes())
    require(audit.get('passed') is True and audit.get('inventoryAccepted') is True and audit.get('independentAuditPassed') is True and audit.get('finalSourceInputOutputIntegrityCheck') is True,'Authoritative reference inventory/integrity acceptance missing')
    manifest_path=tracker.verify(directory/'manifest.json',audit.get('studyManifestHash'));manifest=json.loads(manifest_path.read_bytes())
    sources,inputs=manifest.get('sourceHashes'),manifest.get('inputHashes')
    require(isinstance(sources,dict) and sources and isinstance(inputs,dict) and inputs,'Frozen source/input closure missing')
    for name,sha in sources.items():tracker.verify(u.local(project,name),sha);tracker.verify(u.local(directory,'sources/'+name),sha)
    for name,sha in inputs.items():tracker.verify(u.local(project,name),sha)
    for key,name in SOURCE_KEYS.items():require(audit.get(key)==sources.get(name) and name in sources,'Authoritative auditor source binding differs: '+key)
    require(sources.get(IMMUTABLE_SOURCE)==IMMUTABLE_SHA,'Fixed accepted immutable replay kernel is missing or changed')
    if 'immutableReplayKernelSourceHash' in audit:require(audit['immutableReplayKernelSourceHash']==IMMUTABLE_SHA,'Optional immutable replay kernel receipt alias differs')
    for name in ['research/guard-reference-analysis.py','research/guard-reference-baseline.py','research/guard-reference-learning.js','research/guard-reference-io.js','research/guard-reference-case.js']:
        require(name in sources,'Critical source omitted: '+name)
    analysis=compile_bound(u.local(project,'research/guard-reference-analysis.py'),sources['research/guard-reference-analysis.py'])
    helper=compile_bound(u.local(project,'research/guard-reference-baseline.py'),sources['research/guard-reference-baseline.py'])
    baseline=helper.load_baseline(project)
    require(baseline['consumedFiles'].get(IMMUTABLE_SOURCE,{}).get('sha256')==IMMUTABLE_SHA,'Inherited authoritative closure has another immutable replay kernel')
    for name,ref in baseline['consumedFiles'].items():tracker.verify(u.local(project,name),ref['sha256'],ref['bytes'])
    u.same({k:manifest.get('baseline',{}).get(k) for k in ('manifest','audit','summary','builder','finalEndpoints')},{k:baseline[k] for k in ('manifest','audit','summary','builder','finalEndpoints')},'Frozen inherited baseline identity differs')
    u.same(audit.get('inheritedFinalEndpoints'),baseline['finalEndpoints'],'Independent old comparator slots differ')
    plan=manifest.get('plan',{})
    expected=[dict(id=run_id(s,TREATMENTS[1]),arm='startup',seed=s,treatment=TREATMENTS[1]) for s in SEEDS]
    u.same([{k:r.get(k) for k in ('id','arm','seed','treatment')} for r in plan.get('runs',[])],expected,'Complete ordered twelve-run reference matrix differs')
    require(plan.get('T')==2000000 and plan.get('checkpoints')==list(STEPS) and plan.get('alpha')==.1 and plan.get('gamma')==19/20,'Frozen learning parameters differ')
    u.same(plan.get('scientificTreatment'),SCIENTIFIC,'Manifest support treatment differs')
    for r in plan['runs']:u.same(r.get('scientificTreatment'),SCIENTIFIC,'Planned support treatment differs')
    core,core_refs={},{}
    for name,key in CORE_KEYS.items():
        p=tracker.verify(directory/name,audit.get(key));core_refs[name]=dict(file=name,bytes=p.stat().st_size,sha256=audit[key])
        core[name]=[json.loads(row) for row in p.read_bytes().splitlines()] if name.endswith('.jsonl') else json.loads(p.read_bytes())
    results,index,completion,start=(core[n] for n in ('results.json','index.json','completion.json','execution-start.json'))
    for value in [results,index,completion,start]:require(value.get('manifestSha256')==audit['studyManifestHash'],'Core manifest binding differs')
    for name,key in CORE_KEYS.items():
        if name!='completion.json':require(completion.get(key)==audit[key],'Completion output binding differs')
    require(completion.get('inventoryComplete') is True and completion.get('retainedRuns')==12 and completion.get('retainedCheckpointSlots')==24 and completion.get('finalFrozenDependencyCheck',{}).get('passed') is True,'Closed reference inventory missing')
    require(audit.get('runs')==12 and audit.get('checkpointSlots')==24 and len(results.get('records',[]))==len(index.get('records',[]))==12 and len(core['journal.jsonl'])==26,'All retained primary identities/journal required')
    if start.get('adminGate') is not None:
        gate=tracker.json_ref(project,start['adminGate']);require(gate.get('passed') is True and gate.get('studyManifestHash')==audit['studyManifestHash'],'Administrative gate binding differs')
    raw=tracker.json_ref(project,manifest['inputs']['finiteGame']);finite=raw.get('finite',{});n=len(finite.get('prices',[]));states=5*n*n
    u.same(manifest['inputs']['finiteGame'],baseline['finiteGame'],'Physical game changed between studies')
    require(raw.get('scenario',{}).get('id')=='base-g15-t1' and n==62,'Unchanged original62-price game required')
    for k in ['consumerSurplus','profitA','profitB','quantityA','quantityB']:require(len(finite.get('rewards',{}).get(k,[]))==n*n,'Saved physical table dimensions differ')
    endpoints,slots=audit.get('finalEndpoints'),audit.get('checkpointResults')
    require(isinstance(endpoints,list) and len(endpoints)==12 and isinstance(slots,list) and len(slots)==24,'All independent new endpoint/checkpoint slots required')
    by_endpoint={e.get('runId'):e for e in endpoints};by_slot={(s.get('runId'),s.get('step')):s for s in slots}
    require(len(by_endpoint)==12 and len(by_slot)==24,'Duplicate independent identities')
    aggregated=analysis.aggregate(endpoints,baseline['finalEndpoints']);u.same(aggregated,audit.get('independentSummaries'),'Exact new/old aggregate differs from independent summaries')

    def adopt(meta_ref,root,available,treatment,seed,step,endpoint=None):
        """Rejected slots are hash-bound without adopting their numerical claims."""
        meta=tracker.json_ref(root,meta_ref);identity=run_id(seed,treatment)
        if available:
            require(meta.get('id')==identity and meta.get('seed')==seed and meta.get('step')==step and meta.get('arm')=='startup' and meta.get('finiteGameRef')==manifest['inputs']['finiteGame'],'Checkpoint physical/clock identity differs')
            require(meta.get('n')==n and meta.get('phases')==5 and meta.get('terminal',{}).get('phase')==4,'Accepted checkpoint dimensions/clock differ')
            if treatment==TREATMENTS[1]:
                u.same(meta.get('scientificTreatment'),SCIENTIFIC,'Accepted checkpoint treatment differs')
                require(meta.get('treatment')==TREATMENTS[1],'Accepted support mode differs')
        for family,width,encoding in [('q',8,'f64le'),('counts',4,'u32le')]:
            refs=meta.get('artifacts',{}).get(family,[]);require(isinstance(refs,list),'Invalid bound dense artifact list')
            if available:require(len(refs)==2,'Both private dense arrays required')
            for ref in refs:
                if available:require(ref.get('rawBytes')==5*n**3*width and ref.get('encoding')==encoding and ref.get('compression')=='gzip-single-member' and isinstance(ref.get('rawSha256'),str) and len(ref['rawSha256'])==64,'Accepted dense metadata differs')
                tracker.ref(root,ref,ceiling=5*n**3*width+65536)
        own,world=[],[]
        for family,target in [('own',own),('world',world)]:
            refs=meta.get('policies',{}).get(family,[]);require(isinstance(refs,list),'Invalid bound policy list')
            if available:require(len(refs)==2,'Both private policy orientations required')
            for ref in refs:
                if available:require(ref.get('bytes')==states,'Accepted policy dimensions differ');target.append(tracker.ref(root,ref,read=True,ceiling=states))
                else:tracker.ref(root,ref)
        if not available:tracker.ref(root,meta['graph']);return meta,None,None
        graph=tracker.json_ref(root,meta['graph'])
        require(graph.get('step')==step and graph.get('phase')==meta['terminal']['phase'] and graph.get('arm')=='startup','Accepted graph clock differs')
        require(graph.get('policySha256')==[r['sha256'] for r in meta['policies']['own']] and graph.get('worldPolicySha256')==[r['sha256'] for r in meta['policies']['world']],'Accepted graph/policy hashes differ')
        if treatment==TREATMENTS[1]:
            u.same(graph.get('scientificTreatment'),SCIENTIFIC,'Accepted graph treatment differs')
            require(graph.get('floor') is None and all(c.get('floorApplies') is None and c.get('floorGap') is None for c in graph.get('cycles',[])) and all(graph.get(k,{}).get('floorApplies') is None and graph.get(k,{}).get('floorGap') is None for k in ['actualTerminal','freshCapCounterfactual']),'Inherited guard floor transferred to full-grid graph')
        for node in range(states):
            phase,pa,pb=node//(n*n),(node//n)%n,node%n
            require(world[0][node]==own[0][node] and world[1][node]==own[1][phase*n*n+pb*n+pa],'WORLD B was not mapped exactly once')
            for f,rival in [(0,pb),(1,pa)]:
                allowed=range(finite['capIndex']+1) if phase==0 else range(n) if treatment==TREATMENTS[1] else finite['sets'][rival]
                require(world[f][node] in allowed,'Saved policy violates its own panel support')
        if endpoint is not None:
            require(endpoint['checkpointSha256']==meta_ref['sha256'] and endpoint['graphSha256']==meta['graph']['sha256'],'Independent final artifact identity differs')
            u.same(endpoint['previousIndices'],meta['terminal']['previousIndices'],'Independent actual final history differs')
            u.same(endpoint['cycleCustomerBenefit'],u.exact_only(graph['actualTerminal']['cycleMetrics']['consumerSurplus']),'Independent exact cycle benefit differs')
        return meta,graph,world

    def final_policy(seed,treatment,available,reason,metadata,graph,world):
        identity=run_id(seed,treatment)
        return dict(seed=seed,treatment=treatment,runId=identity,checkpointId=identity+'--t2000000',available=available,reason=reason,
                    scientificTreatment=scientific(treatment),start=metadata['terminal'] if available else None,
                    encoding='uint8 WORLD row-major (phase,previousA,previousB)',states=states,
                    policies={name:u.policy_ref(world[f],metadata['policies']['world'][f]) for f,name in enumerate(['A','B'])} if available else None,
                    cycleMetrics=graph['actualTerminal']['cycleMetrics'] if available else None,cycleLength=len(graph['actualTerminal']['cycleNodesFromStart']) if available else None,
                    transientRounds=graph['actualTerminal']['transientRounds'] if available else None,trainingSupport=graph['actualTerminal']['trainingSupport'] if available else None,
                    trainingTail=next((w for w in metadata['windowMetrics'] if w['endStep']==2000000),None) if available else None)

    def joint_exact(metrics):
        return analysis.packed(analysis.ratio(u.exact_only(metrics['profits']['A']))+analysis.ratio(u.exact_only(metrics['profits']['B'])))

    def detail(status,metadata,graph,metadata_ref):
        available=status['scientificAvailable']
        actual=graph['actualTerminal'] if available else None
        actual_summary=None if not available else dict(start=actual.get('start'),transientRounds=actual['transientRounds'],cycleLength=len(actual['cycleNodesFromStart']),
            cycleMetrics=actual['cycleMetrics'],jointProfitExact=joint_exact(actual['cycleMetrics']),trainingSupport=actual['trainingSupport'],pathTrainingSupport=actual.get('pathTrainingSupport'),transientMetrics=actual.get('transientMetrics'))
        tail=next((w for w in metadata['windowMetrics'] if w['endStep']==status['step']),None) if available else None
        return dict(status,actualTerminal=actual_summary,trainingTail=tail,coverage=graph.get('coverage') if available else None,
                    sourceRefs=dict(metadata=metadata_ref,graph=metadata.get('graph') if metadata else None))

    runs,public_slots,checkpoint_details,new_policies=[],[],[],{}
    for exp,record,ix,planned in zip(expected,results['records'],index['records'],plan['runs']):
        u.same({k:record.get(k) for k in exp},exp,'Retained new run identity differs')
        require(ix.get('id')==record['id'] and ix.get('status')==record.get('status'),'Indexed status differs');u.same(tracker.json_ref(directory,ix),record,'Indexed/aggregate record differs')
        require(type(record.get('executionSucceeded')) is bool,'Explicit execution status required')
        if record.get('task') is not None:
            task=tracker.json_ref(directory,record['task']);require(task.get('manifestSha256')==audit['studyManifestHash'] and task.get('finiteGameRef')==manifest['inputs']['finiteGame'],'Task binding differs')
            u.same(task.get('record'),raw,'Task changed physical record');u.same(task.get('plan'),planned,'Task planned identities differ');u.same(task.get('scientificTreatment'),SCIENTIFIC,'Task scientific treatment differs')
        require([s.get('step') for s in record.get('checkpoints',[])]==list(STEPS),'Retained checkpoint slots differ')
        runs.append(dict(record,checkpoints=copy.deepcopy(record['checkpoints'])))
        for slot in record['checkpoints']:
            checked=by_slot.get((record['id'],slot['step']));require(checked is not None and checked.get('seed')==record['seed'] and checked.get('parentEligible')==slot.get('parentEligible'),'Independent checkpoint identity differs')
            available=checked.get('scientificAvailable') is True;require(checked.get('replayMatched') is available,'Scientific/replay acceptance differs')
            meta=graph=world=None
            if slot.get('parentEligible'):meta,graph,world=adopt(slot['metadata'],directory,available,TREATMENTS[1],record['seed'],slot['step'],by_endpoint.get(record['id']) if available and slot['step']==2000000 else None)
            require(not available or meta is not None,'Accepted checkpoint lacks complete primary evidence')
            reason=None if available else checked.get('reason') or slot.get('reason');require(available or isinstance(reason,str) and reason.strip(),'Unavailable checkpoint reason required')
            public_slots.append(dict(runId=record['id'],seed=record['seed'],step=slot['step'],scientificAvailable=available,status='accepted' if available else 'unavailable',reason=reason,executionSucceeded=record['executionSucceeded']))
            checkpoint_details.append(detail(public_slots[-1],meta,graph,slot.get('metadata')))
            if slot['step']==2000000:
                require(by_endpoint[record['id']]['available'] is available,'Independent final availability differs')
                new_policies[record['seed']]=final_policy(record['seed'],TREATMENTS[1],available,reason,meta,graph,world)
    accepted=sum(s['scientificAvailable'] for s in public_slots)
    require(accepted==audit.get('scientificallyAvailableCheckpoints') and sum(p['available'] for p in new_policies.values())==audit.get('finalAvailable'),'Authoritative availability counts differ')
    require(type(audit.get('fullTrainingReplay')) is bool and audit.get('fullTrainingReplay') is audit.get('replayComplete'),'Aggregate replay flags differ')
    if audit['fullTrainingReplay']:require(accepted==24 and audit.get('replayedRounds')==24000000 and audit.get('roundTranscriptBlocksMatched')==2400,'Complete new replay cannot omit checkpoint/transcript slots')

    old_summary=tracker.json_ref(project,dict(baseline['summary'],bytes=u.local(project,baseline['summary']['file']).stat().st_size))
    old_directory=u.local(project,old_summary['meta']['studyDirectory'])
    old_results=tracker.json_ref(old_directory,old_summary['meta']['coreOutputRefs']['results.json'])
    old_policies,old_statuses,old_details={},[],[]
    for endpoint in baseline['finalEndpoints']:
        seed=endpoint['seed'];record=next(r for r in old_results['records'] if r['id']==run_id(seed,TREATMENTS[0]));slot=next(s for s in record['checkpoints'] if s['step']==2000000)
        require(slot['parentEligible'] is True,'Accepted old final lacks complete metadata')
        meta,graph,world=adopt(slot['metadata'],old_directory,True,TREATMENTS[0],seed,2000000,endpoint)
        old_policies[seed]=final_policy(seed,TREATMENTS[0],True,None,meta,graph,world)
        old_statuses.append(dict(runId=record['id'],seed=seed,step=2000000,scientificAvailable=True,status='inherited accepted',reason=None,executionSucceeded=endpoint['executionSucceeded']))
        old_details.append(detail(old_statuses[-1],meta,graph,slot['metadata']))

    anchors=audit.get('anchors');require(isinstance(anchors,dict) and type(anchors.get('available')) is bool,'Explicit independently assessed anchors required')
    primary_ref=results.get('stageAnchors')
    if anchors['available']:
        require(anchors.get('independentAgreement') is True and anchors.get('reason') is None and completion.get('anchorCalculationPassed') is True,'Available anchor agreement missing')
        u.same(primary_ref,anchors.get('primaryReference'),'Primary anchor reference differs');require(primary_ref['sha256']==audit.get('stageAnchorsSha256')==completion.get('stageAnchorsSha256'),'Anchor SHA binding differs')
        primary=tracker.json_ref(directory,primary_ref);u.same(mathematical_anchors(primary),mathematical_anchors(anchors.get('values')),'Exact independent anchor mathematical fields differ')
        public_anchors=dict(available=True,independentAgreement=True,reason=None,values=primary,provenance=dict(primaryReference=primary_ref,independentAuditSha256=audit_sha,comparisonScope='All mathematical fields agree; narrative scope/coordinate/empty-set wording may differ'))
    else:
        require(anchors.get('values') is None and isinstance(anchors.get('reason'),str) and anchors['reason'].strip(),'Unavailable anchors must retain null/reason')
        if primary_ref is not None:tracker.ref(directory,primary_ref)
        public_anchors=dict(available=False,independentAgreement=False,reason=anchors['reason'],values=None,provenance=dict(primaryReference=primary_ref,independentAuditSha256=audit_sha))

    meta=dict(inventoryAccepted=True,independentAuditPassed=True,audit=dict(passed=True,file=audit_path.relative_to(project).as_posix(),sha256=audit_sha),independentAuditSha256=audit_sha,
              primaryManifestSha256=audit['studyManifestHash'],startupGuardAuditSha256=baseline['audit']['sha256'],coreOutputRefs=core_refs,
              sourceHashes=sources,inputHashes=inputs,studyDirectory=directory.relative_to(project).as_posix(),fullTrainingReplay=audit['fullTrainingReplay'],replayComplete=audit['replayComplete'],replayedRounds=audit['replayedRounds'],
              defaultSelection=dict(seed=907001,checkpoint=2000000,treatments=list(TREATMENTS),chosenBeforeReferenceOutcomeInspection=True),builderSource=dict(file=SELF,sha256=builder_sha),runtime=manifest.get('runtime'),parentRuntime=manifest.get('parentRuntime'),
              auditSummary={k:audit[k] for k in ['runs','checkpointSlots','scientificallyAvailableCheckpoints','finalAvailable','replayedRounds','roundTranscriptBlocksMatched','fullTrainingReplay','replayComplete','executionPassed','executionFailures','resources','scope'] if k in audit},
              scope='Authoritative inventory acceptance is distinct from endpoint availability and complete replay. New12 runs; accepted old comparators reused. No Q decoding/new learning/replay/anchor enumeration in this exporter.')
    policies=[p for seed in SEEDS for p in [old_policies[seed],new_policies[seed]]]
    # Capture every consumed old/new ref, including compressed arrays; no inflation.
    meta['consumedFiles']={p.relative_to(project).as_posix():dict(bytes=size,sha256=sha) for p,(size,sha) in sorted(tracker.files.items(),key=lambda item:str(item[0]))}
    web=dict(schemaVersion=1,meta=meta,finiteGame=raw,orderedSeeds=list(SEEDS),finalPolicies=policies,checkpointStatuses=public_slots,inheritedComparisonStatuses=old_statuses,anchors=public_anchors,**aggregated)
    summary=dict(schemaVersion=1,meta=meta,sourceHashes=sources,inputHashes=inputs,runs=runs,checkpointStatuses=public_slots,checkpointDetails=checkpoint_details,inheritedComparisonStatuses=old_statuses,inheritedComparisonDetails=old_details,finalEndpoints=endpoints,inheritedFinalEndpoints=baseline['finalEndpoints'],anchors=public_anchors,resources=audit.get('resources'),**aggregated)
    pairs=io.StringIO(newline='');writer=csv.writer(pairs);writer.writerow(['seed','available','startup_guard_numerator','startup_guard_denominator','full_grid_numerator','full_grid_denominator','difference_numerator','difference_denominator','reason'])
    for row in aggregated['pairedRows']:
        values=[row['seed'],row['available']]
        for value in [*row['cycleCustomerBenefits'],row['difference']]:values.extend([value['numerator'],value['denominator']] if value else ['',''])
        writer.writerow(values+[row['unavailableReason'] or ''])
    statuses=io.StringIO(newline='');writer=csv.writer(statuses);writer.writerow(['scope','runId','seed','step','scientificAvailable','executionSucceeded','reason'])
    for scope,items in [('new reference',public_slots),('inherited old final',old_statuses)]:
        for row in items:writer.writerow([scope]+[row.get(k) for k in ['runId','seed','step','scientificAvailable','executionSucceeded','reason']])
    anchor_csv=io.StringIO(newline='');writer=csv.writer(anchor_csv)
    writer.writerow(['group','retainedCount','A_index','B_index','priceA_numerator','priceA_denominator','priceB_numerator','priceB_denominator','profitA_numerator','profitA_denominator','profitB_numerator','profitB_denominator','jointProfit_numerator','jointProfit_denominator','customerBenefit_numerator','customerBenefit_denominator','reason'])
    if public_anchors['available']:
        for group in ['pureNash','jointProfitMaximum']:
            values=public_anchors['values'][group]
            if not values['pairs']:writer.writerow([group,0]+['']*14+[values.get('reason') or ''])
            for pair in values['pairs']:
                row=[group,values['count'],*pair['indices']]
                for value in [*pair['prices'],pair['profits']['A'],pair['profits']['B'],pair['profits']['joint'],pair['consumerSurplus']]:row.extend([value['numerator'],value['denominator']])
                writer.writerow(row+[''])
    else:writer.writerow(['unavailable',0]+['']*14+[public_anchors['reason']])
    metrics_csv=io.StringIO(newline='');writer=csv.writer(metrics_csv)
    metric_names=['consumerBenefit','priceA','priceB','profitA','profitB','jointProfit']
    header=['scope','runId','seed','step','available','reason','transientRounds','cycleLength']
    header += [f'cycle_{name}_{part}' for name in metric_names for part in ['numerator','denominator']]
    header += ['cycleUnvisitedStatesA','cycleUnvisitedStatesB','cycleNeverTriedActionA','cycleNeverTriedActionB','trainingTailAvailable','trainingWindowRounds']
    header += [f'training_{name}_{part}' for name in metric_names for part in ['numerator','denominator']]
    writer.writerow(header)
    def metric_values(metrics):
        if metrics is None:return ['']*12
        values=[metrics['consumerSurplus'],metrics['prices']['A'],metrics['prices']['B'],metrics['profits']['A'],metrics['profits']['B'],joint_exact(metrics)]
        return [part for value in values for part in [value['numerator'],value['denominator']]]
    for scope,items in [('new reference',checkpoint_details),('inherited old final',old_details)]:
        for d in items:
            actual=d['actualTerminal'];tail=d['trainingTail'];tail_metrics=tail.get('metrics') if tail else None
            row=[scope,d['runId'],d['seed'],d['step'],d['scientificAvailable'],d['reason'] or '',actual['transientRounds'] if actual else '',actual['cycleLength'] if actual else '']
            row+=metric_values(actual['cycleMetrics'] if actual else None)
            support=actual['trainingSupport'] if actual else {}
            row += [support.get(f,{}).get(key,'') for key in ['unvisitedStates','neverTriedGreedyActions'] for f in ['A','B']]
            row += [tail_metrics is not None,tail.get('rounds','') if tail else '']+metric_values(tail_metrics)
            writer.writerow(row)
    if before_final_check:before_final_check()
    count=tracker.close()
    return dict(outputs={'analysis.json':u.encoded(summary),'web-data.json':u.encoded(web),'paired-results.csv':pairs.getvalue().encode(),'checkpoint-statuses.csv':statuses.getvalue().encode(),'stage-anchors.csv':anchor_csv.getvalue().encode(),'endpoint-metrics.csv':metrics_csv.getvalue().encode()},tracker=tracker,verification=dict(passed=True,auditSha256=audit_sha,consumedFiles=count,newCheckpointSlots=24,inheritedFinalSlots=12,acceptedNewCheckpoints=accepted,fullTrainingReplay=audit['fullTrainingReplay'],scope='Read-only authoritative deterministic regeneration; compressed dense artifacts hashed without Q decode'))


def load_accepted(summary_path,expected_audit_sha,*,project=ROOT):
    project=Path(project).resolve();summary_path=Path(summary_path).resolve();require(summary_path.is_relative_to(project),'Summary must be project-local')
    raw=summary_path.read_bytes();summary=json.loads(raw);meta=summary.get('meta',{})
    require(meta.get('independentAuditSha256')==expected_audit_sha,'Expected accepted audit SHA differs')
    utility=compile_bound(project/UTILITY,UTILITY_SHA)
    bundle=build(project,utility.local(project,meta.get('studyDirectory')),utility.local(project,meta.get('audit',{}).get('file')),expected_audit_sha)
    require(raw==bundle['outputs']['analysis.json'],'Summary differs from authoritative deterministic regeneration')
    require(summary_path.read_bytes()==raw,'Summary changed during verification');bundle['tracker'].close();return summary


def write_outputs(bundle,output):
    output=Path(output).resolve();require(not any((output/name).exists() for name in bundle['outputs']),'Existing/partial derivatives retained; refusing overwrite')
    output.mkdir(parents=True,exist_ok=True)
    for name,raw in bundle['outputs'].items():
        with (output/name).open('xb') as stream:stream.write(raw)
    bundle['tracker'].close();return bundle['verification']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',default=str(ROOT));parser.add_argument('--directory',default='research/guard-reference-results');parser.add_argument('--audit',required=True);parser.add_argument('--audit-sha',required=True);parser.add_argument('--output')
    args=parser.parse_args();project=Path(args.project).resolve();utility=compile_bound(project/UTILITY,UTILITY_SHA)
    directory=utility.local(project,args.directory);bundle=build(project,directory,utility.local(project,args.audit),args.audit_sha)
    print(json.dumps(write_outputs(bundle,Path(args.output).resolve() if args.output else directory)))
