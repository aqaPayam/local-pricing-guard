// Read-only export of audited finite games, exact incentives and stored policies.
// No Bellman optimization or model player runs in this exporter.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import{fileURLToPath,pathToFileURL}from'node:url';
import{certifyCycle,compare,fromJSON}from'./recurring-game.js';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),P='research/incentive-results/',args=process.argv.slice(2);
if(args.length&&!(args.length===2&&args[0]==='--output'))throw Error('Use node research/build-incentive-web.js [--output FILE]');
const abs=name=>path.resolve(ROOT,name),bytes=name=>fs.readFileSync(abs(name)),read=name=>JSON.parse(bytes(name));
const hash=name=>crypto.createHash('sha256').update(bytes(name)).digest('hex'),need=(ok,message)=>{if(!ok)throw Error(message);};
const M=P+'manifest.json',R=P+'results.json',I=P+'index.json',A=P+'independent-audit.json',C=P+'completion.json',S=P+'summary.json',AN='research/incentive-analysis.js';
const manifest=read(M),result=read(R),index=read(I),audit=read(A),completion=read(C);
need(audit.passed===true&&audit.studyManifestHash===hash(M)&&audit.resultsSha256===hash(R)&&audit.indexSha256===hash(I),'Passed independent manifest/results/index binding required');
need(audit.auditorSourceHash===hash('research/audit-incentive-study.py'),'Current independent auditor differs');
need(Object.keys(audit.corruptionNegativeControls??{}).length>=5&&Object.values(audit.corruptionNegativeControls).every(v=>v===true),'Independent corruption controls missing/failed');
need(result.manifestSha256===hash(M)&&index.manifestSha256===hash(M)&&completion.manifestSha256===hash(M),'Primary manifest identities differ');
need(completion.passed===true&&completion.unresolvedRecords===0&&completion.records===96&&completion.resultsSha256===hash(R)&&completion.indexSha256===hash(I)&&completion.finalFrozenDependencyCheck?.passed===true,'Explicit complete primary pass required');
for(const group of ['sourceHashes','inputHashes'])for(const[name,digest]of Object.entries(manifest[group]??{})){
 need(hash(name)===digest,'Changed frozen dependency '+name);if(group==='sourceHashes')need(hash(P+'sources/'+name)===digest,'Changed frozen primary source snapshot '+name);
}
// Execute only the descriptive adapter, intercepting every write. Its complete
// raw-evidence inventory gate prevents edited summaries from becoming evidence.
const writes=new Map(),adapter={readFileSync:fs.readFileSync,existsSync:fs.existsSync,mkdirSync(){},writeFileSync(name,value){
 const relative=path.relative(ROOT,path.resolve(name)).replaceAll('\\','/');need([S,'research/INCENTIVE_RESULTS.md'].includes(relative),'Unexpected descriptive write');writes.set(relative,Buffer.from(value));
}};
const source=bytes(AN).toString('utf8').replace(/^import .*\r?\n/gm,'').replaceAll('import.meta.url',JSON.stringify(pathToFileURL(abs(AN)).href));
vm.runInNewContext(source,{fs:adapter,path,crypto,fileURLToPath,console:{log(){}}},{filename:'read-only-incentive-analysis',timeout:30000});
need(writes.has(S)&&writes.get(S).equals(bytes(S)),'Saved descriptive rows differ from read-only regeneration against raw evidence');
const summary=JSON.parse(writes.get(S));need(summary.analysisSourceHash===hash(AN)&&summary.counts.records===96&&summary.counts.completedRecords===96&&summary.counts.unresolvedRecords===0,'Complete descriptive identity differs');
const records=manifest.plan.cases.map(entry=>{
 need(hash(entry.rawFile)===entry.rawSha256,'Changed finite game '+entry.rawFile);const raw=read(entry.rawFile),group=summary.records.filter(r=>r.scenario===entry.scenario);
 need(group.length===12,'Twelve slot/seller/discount labels required per finite game');
 const periods=[...new Set(group.map(r=>r.period))],certificates=periods.map(K=>{
  const w=summary.welfareRows.filter(w=>w.scenario===entry.scenario&&w.period===K);need(w.length===1,'Missing unique audited game/K welfare certificate');
  const audited=w[0],certificate=certifyCycle(raw.finite,K);
  need(compare(fromJSON(certificate.cycleAverageExact),fromJSON(audited.cycleMean))===0&&compare(fromJSON(certificate.activationFloorExact),fromJSON(audited.activationAverageFloor))===0,'Display engine welfare certificate differs from exact audited one');
  need(certificate.minimizingPrefix===audited.minimizingPrefixLength&&certificate.cycleIndices.length===audited.cycle.length&&certificate.cycleIndices.every((a,j)=>audited.cycle[j].quoteIndices[0]===a&&audited.cycle[j].quoteIndices[1]===a),'Display cycle/prefix differs from audited path');
  return{...certificate,source:{file:audited.sourceFile,sha256:audited.sourceSha256},targetComparisons:audited.targetComparisons,baselineProfitCycleMeans:audited.baselineProfitCycleMeans};
 });
 const comparisons=group.map(r=>{
  need(r.cap&&r.status==='completed exact unilateral audit','Completed exact comparison required');
  const phasePolicies=r.policies.map(layer=>{const data=bytes(layer.argmaxFile);need(hash(layer.argmaxFile)===layer.argmaxSha256&&data.length===layer.argmaxBytes,'Stored policy bytes differ');return{phase:layer.phase,actions:Array.from(data),source:{file:layer.argmaxFile,sha256:layer.argmaxSha256,bytes:layer.argmaxBytes}};});
  return{id:r.id,slotId:r.slotId,period:r.period,periodSource:r.periodSlot,duplicateOf:r.duplicateOf,focalSeller:r.focalSeller,discount:r.discount,discountId:r.discountId,status:r.status,
   source:{file:r.sourceRecord,sha256:r.sourceRecordSha256},cap:r.cap,phases:r.phases,screen:r.screen,baselineBlockTrace:r.baselineBlockTrace,optimalBlockReplay:r.optimalBlockReplay,welfareSource:r.welfare,
   challenge:{period:r.period,focal:r.focalSeller==='A'?0:1,discount:r.discount,optimalBlockProfit:r.cap.finiteOptimal,baselineBlockProfit:r.cap.finiteBaseline,capAction:r.cap.action,phasePolicies}};
 });
 return{...raw,finite:{...raw.finite,certificates},finiteSource:{file:entry.rawFile,sha256:entry.rawSha256},comparisons};
});
const data={schemaVersion:1,meta:{primaryManifestSha256:hash(M),primaryResultsSha256:hash(R),primaryIndexSha256:hash(I),independentAuditSha256:hash(A),summarySha256:hash(S),analysisSourceSha256:hash(AN),exporterSha256:hash('research/build-incentive-web.js'),
 primaryAudit:{passed:true,source:A,sha256:hash(A),auditorSourceHash:audit.auditorSourceHash,arithmeticBackendHash:audit.arithmeticBackendHash??null,records:96,counts:summary.counts},
 finiteGameEngineSha256:hash('research/recurring-game.js'),challengeEngineSha256:hash('research/incentive-game.js'),scope:summary.scope,
 experimentalSellerModelApiCalls:0,newTrainingRounds:0,developmentAssistance:'Codex development and AI-agent auditing assistance disclosed; no experimental model game player.',
 provenance:'Full descriptive export regenerated read-only against all independently audited raw evidence. Each new-K game-core welfare certificate matches its exact independently audited cycle/prefix certificate. Stored all-state phase argmax bytes are embedded, not optimized in the browser.'},
 periodSlots:manifest.plan.periodSlots,discounts:manifest.plan.discounts.map(g=>({numerator:String(g.p),denominator:String(g.q)})),records};
const output=args.length?abs(args[1]):abs(P+'web-data.json'),relativeOutput=path.relative(ROOT,output);
need(relativeOutput!=='..'&&!relativeOutput.startsWith('..'+path.sep)&&!path.isAbsolute(relativeOutput),'Export output escapes workspace');
need(![M,R,I,A,C,S].some(name=>output===abs(name)),'Refusing to overwrite scientific evidence');
need(output===abs(P+'web-data.json')||!fs.existsSync(output),'Explicit export output already exists');
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(data));
console.log(JSON.stringify({output:path.relative(ROOT,output),markets:records.length,comparisons:records.reduce((n,r)=>n+r.comparisons.length,0),policies:records.flatMap(r=>r.comparisons).reduce((n,r)=>n+r.challenge.phasePolicies.length,0),welfareCertificates:records.reduce((n,r)=>n+r.finite.certificates.length,0),bytes:fs.statSync(output).size,sha256:hash(path.relative(ROOT,output))}));
