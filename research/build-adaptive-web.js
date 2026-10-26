// Audited saved-policy previews only. No learning or policy optimization here.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import{fileURLToPath,pathToFileURL}from'node:url';
import{BOOTSTRAP,indices,pairedMeanInterval}from'./adaptive-bootstrap.js';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),P='research/adaptive-learning-results/',args=process.argv.slice(2);
if(args.length&&!(args.length===2&&args[0]==='--output'))throw Error('Use node research/build-adaptive-web.js [--output FILE]');
const abs=name=>path.resolve(ROOT,name),bytes=name=>fs.readFileSync(abs(name)),read=name=>JSON.parse(bytes(name)),hash=name=>crypto.createHash('sha256').update(bytes(name)).digest('hex'),need=(ok,message)=>{if(!ok)throw Error(message);};
const M=P+'manifest.json',R=P+'results.json',I=P+'index.json',A=P+'independent-audit.json',C=P+'completion.json',S=P+'summary.json',AN='research/adaptive-analysis.js';
const manifest=read(M),results=read(R),index=read(I),audit=read(A),completion=read(C);
need(audit.passed===true&&audit.runs===192&&audit.checkpoints===384&&audit.fullTrainingReplay===false,'Explicit complete independently audited inventory/replay scope required');
need(audit.studyManifestHash===hash(M)&&audit.resultsSha256===hash(R)&&audit.indexSha256===hash(I)&&audit.auditorSourceHash===hash('research/audit-adaptive-learning.py'),'Current independent manifest/results/index/auditor identity differs');
need(audit.completionSha256===hash(C),'Independently audited completion differs');
need(Object.keys(audit.corruptionNegativeControls??{}).length>=5&&Object.values(audit.corruptionNegativeControls).every(v=>v===true),'Independent corruption controls missing/failed');
need(completion.passed===true&&completion.unresolvedRuns===0&&completion.runs===192&&completion.checkpoints===384&&completion.finalFrozenDependencyCheck?.passed===true,'Primary study has not explicitly completed without unresolved runs');
need(results.manifestSha256===hash(M)&&index.manifestSha256===hash(M)&&completion.manifestSha256===hash(M)&&completion.resultsSha256===hash(R)&&completion.indexSha256===hash(I),'Primary manifest/results/index/completion binding differs');
for(const group of ['sourceHashes','inputHashes'])for(const[name,digest]of Object.entries(manifest[group]??{})){
 need(hash(name)===digest,'Frozen dependency differs '+name);if(group==='sourceHashes')need(hash(P+'sources/'+name)===digest,'Frozen source snapshot differs '+name);
}
// The complete descriptive analysis runs against read-only evidence. Only its
// two intended writes are intercepted; no saved result or checkpoint is changed.
const writes=new Map(),adapter={readFileSync:fs.readFileSync,existsSync:fs.existsSync,mkdirSync(){},writeFileSync(name,value){const relative=path.relative(ROOT,path.resolve(name)).replaceAll('\\','/');need([S,'research/ADAPTIVE_LEARNING_RESULTS.md'].includes(relative),'Unexpected descriptive write');writes.set(relative,Buffer.from(value));}};
const source=bytes(AN).toString('utf8').replace(/^import.*\r?\n/gm,'').replaceAll('import.meta.url',JSON.stringify(pathToFileURL(abs(AN)).href));
vm.runInNewContext(source,{fs:adapter,path,crypto,fileURLToPath,BOOTSTRAP,indices,pairedMeanInterval,console:{log(){}}},{filename:'read-only-adaptive-analysis',timeout:180000});
need(writes.has(S)&&writes.get(S).equals(bytes(S)),'Saved summary differs from complete read-only regeneration against audited raw evidence');
const summary=JSON.parse(writes.get(S));need(summary.analysisSourceHash===hash(AN)&&summary.counts.runs===192&&summary.counts.checkpoints===384&&summary.counts.primaryPairs===48&&summary.counts.primaryContrasts===4,'Complete descriptive identity differs');
const runs=summary.runs.map(run=>({id:run.id,scenario:run.scenario,controller:run.controller,qInit:run.qInit,seed:run.seed,status:run.status,source:run.source,learningCurve:run.learningCurve,
 checkpoints:run.checkpoints.map(cp=>({step:cp.step,terminalStart:cp.terminalStart,trainingTail:cp.trainingTail,coverage:cp.coverage,frozen:cp.frozen,
  controllerFloor:{kind:cp.controllerFloor.kind,longRunFloor:cp.controllerFloor.longRunFloor,scope:cp.controllerFloor.scope,displayScope:cp.controllerFloor.displayScope,fixedPointIndex:cp.controllerFloor.fixedPointIndex??null,upperOrbit:cp.controllerFloor.upperOrbit??null},
  old95Target:cp.old95Target,preview128:cp.preview128,previewScope:cp.previewScope,source:cp.source}))}));
need(runs.length===192&&runs.every(r=>r.checkpoints.length===2&&r.checkpoints.every(c=>c.preview128.length===128)),'Complete compact run/checkpoint/preview inventory differs');
const data={schemaVersion:1,meta:{primaryManifestSha256:hash(M),primaryResultsSha256:hash(R),primaryIndexSha256:hash(I),independentAuditSha256:hash(A),summarySha256:hash(S),analysisSourceSha256:hash(AN),exporterSha256:hash('research/build-adaptive-web.js'),
 primaryAudit:{passed:true,runs:192,checkpoints:384,source:A,sha256:hash(A),auditorSourceHash:audit.auditorSourceHash,fullTrainingReplay:false},counts:summary.counts,diagnostics:summary.diagnostics,
 bootstrap:{file:'research/adaptive-bootstrap-indices.json',sha256:hash('research/adaptive-bootstrap-indices.json'),...BOOTSTRAP},
 defaultSelection:{scenario:'base-g15-t1',qInit:'zero',seed:907001,controller:'selected95',step:2000000,chosenBeforeOutcomeInspection:true,scope:'Presentation default selected without inspecting outcomes; no scientific preregistration is implied.'},
 scope:summary.scope,previewScope:'Truncated128-execution actual-terminal frozen-policy preview only; exact complete-cycle means are separately audited. Q/policy binaries are omitted. Startup-only terminal continuation receives no new cap. The browser performs no optimization.',
 experimentalSellerModelApiCalls:0,developmentAssistance:'Codex development and AI-agent auditing assistance disclosed; no language-model/chat/API seller calls.',
 provenance:'All compact rows byte-match full raw-evidence-gated read-only analysis regeneration; exact saved-weight endpoint signs and approximate marginal whole-seed bootstrap intervals remain distinct.'},
 scenarios:summary.scenarios,orderedSeeds:summary.orderedSeeds,runs,primaryPairs:summary.primaryPairs,primaryContrasts:summary.primaryContrasts};
const output=args.length?abs(args[1]):abs(P+'web-data.json'),relativeOutput=path.relative(ROOT,output);
need(relativeOutput!=='..'&&!relativeOutput.startsWith('..'+path.sep)&&!path.isAbsolute(relativeOutput),'Export output escapes workspace');
need(![M,R,I,A,C,S].some(name=>output===abs(name)),'Refusing to overwrite scientific evidence');need(output===abs(P+'web-data.json')||!fs.existsSync(output),'Explicit export output already exists');
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(data));
console.log(JSON.stringify({output:path.relative(ROOT,output),runs:runs.length,checkpoints:runs.reduce((n,r)=>n+r.checkpoints.length,0),primaryPairs:48,primaryContrasts:4,bytes:fs.statSync(output).size,sha256:hash(path.relative(ROOT,output))}));
