// Saved-evidence presentation only. No demand/controller case calculations.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2);
if(args.length&&!(args.length===2&&args[0]==='--output'))throw Error('Use node research/build-misspec-web.js [--output FILE]');
const abs=p=>path.resolve(ROOT,p),bytes=p=>fs.readFileSync(abs(p)),read=p=>JSON.parse(bytes(p));
const hash=p=>crypto.createHash('sha256').update(bytes(p)).digest('hex');
const need=(ok,message)=>{if(!ok)throw Error(message);};
const M='research/misspec-results/manifest.json',R='research/misspec-results/results.json',A='research/misspec-results/independent-audit.json';
const C='research/misspec-results/completion.json',S='research/misspec-results/summary.json',AN='research/misspec-analysis.js';
const manifest=read(M),result=read(R),audit=read(A),completion=read(C);
need(audit.passed===true,'Independent sensitivity audit has not passed');
need(audit.studyManifestHash===hash(M)&&audit.resultsSha256===hash(R),'Audited manifest/results differ');
need(audit.auditorSourceHash===hash('research/audit-misspec-study.py'),'Current independent auditor differs');
need(audit.arithmeticBackendHash===hash('research/audit-continuous-study.py'),'Independent arithmetic backend differs');
need(Object.keys(audit.corruptionNegativeControls||{}).length>0&&Object.values(audit.corruptionNegativeControls).every(v=>v===true),'Missing/failed independent corruption controls');
need(result.manifestSha256===hash(M)&&completion.resultsSha256===hash(R)&&completion.finalFrozenDependencyCheck?.passed===true,'Incomplete or changed primary outputs');
for(const group of ['sourceHashes','inputHashes'])for(const [name,digest]of Object.entries(manifest[group]||{}))need(hash(name)===digest,'Changed frozen dependency '+name);
need(result.records.length===16&&completion.records===16&&completion.policySlots===240&&completion.robustPeriodRows===320,'Declared primary inventory incomplete');

// Rebuild the descriptive adapter with every write intercepted. This verifies
// saved compact rows against raw evidence, rather than trusting their own hash
// declarations. The reviewed local analysis code runs without file mutations.
const writes=new Map(),analysisEntry=abs(AN);
const adapter={readFileSync:fs.readFileSync,existsSync:fs.existsSync,mkdirSync(){},writeFileSync(name,value){
 const relative=path.relative(ROOT,path.resolve(name)).replaceAll('\\','/');
 need(['research/misspec-results/summary.json','research/MODEL_MISSPEC_RESULTS.md'].includes(relative),'Unexpected descriptive adapter write');
 writes.set(relative,Buffer.from(value));
}};
const source=bytes(AN).toString('utf8').replace(/^import .*\r?\n/gm,'').replaceAll('import.meta.url',JSON.stringify(pathToFileURL(analysisEntry).href));
vm.runInNewContext(source,{fs:adapter,path,crypto,fileURLToPath,console:{log(){}}},{filename:'read-only-misspec-analysis',timeout:30000});
need(writes.has(S)&&writes.get(S).equals(bytes(S)),'Saved compact summary differs from read-only regeneration against primary evidence');
const summary=JSON.parse(writes.get(S));
need(summary.analysisSourceHash===hash(AN),'Descriptive analysis source differs');
need(summary.counts.modelSemantics===16&&summary.counts.targetLabels===80&&summary.counts.policySlots===240&&summary.counts.reserveRows===960&&summary.counts.robustPeriodRows===320,'Compact matrix inventory differs');
const rows=summary.rows.map(row=>{
 const compact={scenario:row.scenario,economy:row.economy,physicalCap:row.physicalCap};
 for(const kind of ['effective','nominal']){const model=row[kind];
  compact[kind]={status:model.status,actualDemand:model.actualDemand,nominalEnforcement:model.nominalEnforcement,
   targetGroups:model.targetGroups.map(target=>({label:target.label,requestedExact:target.requestedExact,
    thresholdExact:target.thresholdExact,targetIdentityAvailable:target.targetIdentityAvailable,
    d0ReproducesClosedSelection:target.d0ReproducesClosedSelection,
    policySlots:target.policySlots.map(policy=>({...policy,radius:{...policy.radius,
      source:{record:model.sourceRecord,sha256:model.sourceRecordSha256,label:target.label,slot:policy.slotId}}})),
    robustPeriods:target.robustPeriods.map(period=>({...period,source:{record:model.sourceRecord,
      sha256:model.sourceRecordSha256,label:target.label,dExact:period.dExact}}))}))};
 }
 return compact;
});
const data={schemaVersion:1,meta:{primaryManifestSha256:hash(M),primaryResultsSha256:hash(R),independentAuditSha256:hash(A),
 summarySha256:hash(S),analysisSourceSha256:hash(AN),exporterSha256:hash('research/build-misspec-web.js'),
 sourceHashes:{...manifest.sourceHashes,independentAuditor:audit.auditorSourceHash,independentArithmeticBackend:audit.arithmeticBackendHash},
 primaryAudit:{passed:true,source:A,sha256:hash(A),checks:audit.checks,counts:summary.counts},
 scope:summary.scope,apiCalls:0,apiCallScope:'Experimental seller/model API calls; Codex development assistance is separately disclosed.',newTrainingRounds:0,
 provenance:'Compact rows regenerated read-only and byte-matched against the raw-evidence-gated descriptive analysis; source/current audit and completion independently checked. No finite-game model is changed.'},
 levels:summary.levels,rows};
const output=args.length?abs(args[1]):abs('research/misspec-results/web-data.json');
const relativeOutput=path.relative(ROOT,output);
need(relativeOutput!=='..'&&!relativeOutput.startsWith('..'+path.sep)&&!path.isAbsolute(relativeOutput),'Export output escapes workspace');
need(output!==abs(S)&&output!==abs(R)&&output!==abs(M)&&output!==abs(A)&&output!==abs(C),'Refusing to overwrite scientific evidence');
need(output===abs('research/misspec-results/web-data.json')||!fs.existsSync(output),'Explicit export output already exists; scientific/source files are never overwritten');
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(data));
console.log(JSON.stringify({output:path.relative(ROOT,output),rows:rows.length,levels:data.levels.length,policySlots:240,reserveRows:960,bytes:fs.statSync(output).size}));
