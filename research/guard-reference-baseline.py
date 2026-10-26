"""Explicit authentication of the accepted old comparator; no IO on import.

This reuses previously accepted numerical evidence, without training, decoding
Q arrays, replaying old streams, or computing new economic anchors.
"""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import types

BUILDER = 'research/build-matched-clock-web.py'
BUILDER_SHA = '8819178086fe455987a10c66e26dedb0c8ef3ca2ca4980e529a4e24e534ceaa0'
SUMMARY = 'research/matched-clock-results/analysis.json'
SUMMARY_SHA = '3bbbc757378f79c4bdf948166ac73458e2aa2ebc0ecaedc6876d55fc5e09f489'
MANIFEST = 'research/matched-clock-results/manifest.json'
MANIFEST_SHA = 'dcd573fc866e59cd1a27c3158cb9e9be58702034f9fb250e251c54f579a01817'
AUDIT = 'research/matched-clock-results/independent-audit.json'
AUDIT_SHA = 'a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def local(root, name):
    need(isinstance(name,str) and name and '\\' not in name and ':' not in name, 'Canonical project-relative path required')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==name, 'Unsafe/noncanonical inherited path')
    resolved = (root/name).resolve()
    need(resolved.is_relative_to(root), 'Inherited path escapes project')
    return resolved


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def load_baseline(project):
    """Return authenticated old endpoints and the complete required identity map.

    This is an explicit read operation. Call only after accepted V12 delivery
    closure for new inventory preparation; it does not constitute numerical GO.
    """
    root=Path(project).resolve()
    fixed={BUILDER:BUILDER_SHA,SUMMARY:SUMMARY_SHA,MANIFEST:MANIFEST_SHA,AUDIT:AUDIT_SHA}
    for name,sha in fixed.items():
        need(digest(local(root,name))==sha, 'Fixed accepted baseline identity differs: '+name)
    module=types.ModuleType('accepted_matched_clock_web')
    module.__file__=str(local(root,BUILDER))
    source=local(root,BUILDER).read_bytes()
    need(hashlib.sha256(source).hexdigest()==BUILDER_SHA, 'Baseline builder changed before compilation')
    exec(compile(source,module.__file__,'exec'),module.__dict__)
    summary=module.load_accepted(local(root,SUMMARY),AUDIT_SHA,project=root)
    meta=summary['meta']
    need(meta['inventoryAccepted'] is True and meta['independentAuditPassed'] is True
         and meta['fullTrainingReplay'] is True and meta['replayComplete'] is True,
         'Accepted baseline is not the required full-replay study')
    need(meta['primaryManifestSha256']==MANIFEST_SHA and meta['replayedRounds']==48_000_000,
         'Accepted baseline manifest/replay scope differs')
    entries=[copy.deepcopy(e) for e in summary['finalEndpoints'] if e.get('arm')=='startup']
    need(len(entries)==12 and [e['seed'] for e in entries]==list(range(907001,907013)),
         'Old startup comparator slots/order differ')
    for e in entries:
        need(e['runId']==f"base-g15-t1--matched5-startup--zero--s{e['seed']}"
             and e['available'] is True and e['replayMatched'] is True
             and e['step']==2_000_000 and e['nextPhase']==4,
             'Old required final comparator unavailable or mismatched')
    manifest_bytes=local(root,MANIFEST).read_bytes()
    need(hashlib.sha256(manifest_bytes).hexdigest()==MANIFEST_SHA,
         'Exact parsed baseline manifest bytes differ')
    manifest=json.loads(manifest_bytes)
    finite_ref=copy.deepcopy(manifest['inputs']['finiteGame'])
    consumed=copy.deepcopy(meta['consumedFiles'])
    need(isinstance(consumed,dict) and consumed, 'Complete accepted baseline dependency map required')
    for name,sha in fixed.items():
        ref=dict(bytes=local(root,name).stat().st_size,sha256=sha)
        need(name not in consumed or consumed[name]==ref, 'Conflicting old fixed dependency')
        consumed[name]=ref
    for name,ref in consumed.items():
        path=local(root,name)
        need(type(ref.get('bytes')) is int and ref['bytes']>=0
             and isinstance(ref.get('sha256'),str) and re.fullmatch('[a-f0-9]{64}',ref['sha256']),
             'Malformed accepted baseline dependency')
        need(path.stat().st_size==ref['bytes'] and digest(path)==ref['sha256'],
             'Accepted baseline dependency changed before return: '+name)
    need(consumed.get(finite_ref['file'])==dict(bytes=finite_ref['bytes'],sha256=finite_ref['sha256']),
         'Physical finite input absent from authenticated baseline closure')
    return dict(scope='Previously accepted startup-guard endpoints reused; no old training or replay repeated, no Q decoding or new anchors',
                manifest=dict(file=MANIFEST,sha256=MANIFEST_SHA),audit=dict(file=AUDIT,sha256=AUDIT_SHA),
                summary=dict(file=SUMMARY,sha256=SUMMARY_SHA),builder=dict(file=BUILDER,sha256=BUILDER_SHA),
                finalEndpoints=entries,finiteGame=finite_ref,consumedFiles=consumed,
                inputHashes={name:ref['sha256'] for name,ref in sorted(consumed.items())})
