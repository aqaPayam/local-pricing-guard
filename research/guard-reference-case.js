// One prospective supervised reference child. Import performs no IO/training.
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import {fileURLToPath} from 'node:url';
import {advanceTo} from './matched-clock-learning.js';
import {readRef,sha,local} from './matched-clock-io.js';
import {runtimeIdentity,runtimeFingerprint} from './matched-clock-study.js';
import {createGuardReferenceLearners,validateGuardReference,evaluateGuardReference,summarizeGuardReferenceWindows,scientificTreatment,FULL_GRID_TREATMENT} from './guard-reference-learning.js';
import {writeReferenceCheckpoint} from './guard-reference-io.js';
const need=(v,m)=>{if(!v)throw Error(m);};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function validateTask(task,directory){
 const treatment=scientificTreatment();
 need(['artificial','frozen-primary'].includes(task.executionMode),'Declared artificial or frozen-primary mode required');
 need(same(task.scientificTreatment,treatment)&&same(task.plan?.scientificTreatment,treatment),'Task/plan must declare the full-grid scientific treatment');
 need(task.plan.arm==='startup'&&task.plan.treatment===FULL_GRID_TREATMENT,'Production reference uses startup cap clock and full-grid support');
 need(Number.isSafeInteger(task.T)&&task.T>=2&&task.T<=2000000&&same(task.checkpoints,[Math.floor(task.T/2),task.T]),'Declared horizon/checkpoints differ');
 need(task.record&&same(task.record.finite??task.record,task.finite??task.record.finite??task.record),'Task physical table aliases differ');
 const software=runtimeIdentity();need(same(runtimeFingerprint(software),runtimeFingerprint(task.software)),'Child executable/V8 identity differs');
 if(task.executionMode==='frozen-primary'){
  need(task.T===2000000&&same(task.checkpoints,[1000000,2000000]),'Frozen reference horizon differs');
  const bytes=fs.readFileSync(path.join(directory,'manifest.json'));need(sha(bytes)===task.manifestSha256,'Child frozen manifest hash differs');const manifest=JSON.parse(bytes);
  need(manifest.plan?.runs?.some(p=>same(p,task.plan))&&same(manifest.inputs?.finiteGame,task.finiteGameRef),'Child planned input identity differs');
  need(same(manifest.plan.scientificTreatment,treatment)&&manifest.plan.T===task.T&&same(manifest.plan.checkpoints,task.checkpoints),'Manifest scientific treatment/horizon differs');
  need(manifest.plan.alpha===.1&&manifest.plan.gamma===19/20&&same(runtimeFingerprint(manifest.runtime),runtimeFingerprint(software)),'Manifest numerical/runtime identity differs');
  for(const map of ['sourceHashes','inputHashes']){
   need(manifest[map]&&typeof manifest[map]==='object'&&!Array.isArray(manifest[map])&&Object.keys(manifest[map]).length>0,'Complete frozen dependency maps required');
   for(const[name,digest]of Object.entries(manifest[map])){
    need(/^[a-f0-9]{64}$/.test(digest)&&sha(fs.readFileSync(local(task.projectRoot,name)))===digest,'Frozen live dependency differs '+name);
    if(map==='sourceHashes')need(sha(fs.readFileSync(local(directory,'sources/'+name)))===digest,'Frozen source snapshot differs '+name);
   }
  }
  for(const name of ['research/guard-reference-case.js','research/guard-reference-learning.js','research/guard-reference-io.js','research/matched-clock-learning.js','research/matched-clock-graph.js','research/matched-clock-io.js'])need(manifest.sourceHashes[name],'Critical child source is not frozen '+name);
  need(manifest.inputHashes[task.finiteGameRef.file]===task.finiteGameRef.sha256,'Physical record absent from frozen inputs');
  const original=JSON.parse(readRef(task.projectRoot,task.finiteGameRef));need(same(original,task.record),'Task original game differs from frozen raw input');
 }
 return software;
}
export async function runCase(taskFile){
 const task=JSON.parse(fs.readFileSync(taskFile)),directory=path.dirname(path.dirname(path.resolve(taskFile))),software=validateTask(task,directory);
 const lines=readline.createInterface({input:process.stdin,crlfDelay:Infinity}),iterator=lines[Symbol.asyncIterator]();
 const emit=value=>process.stdout.write(JSON.stringify(value)+'\n'),sample=()=>emit({type:'sample',rssBytes:process.memoryUsage().rss});
 const m=createGuardReferenceLearners(task.record,{seed:task.plan.seed,T:task.T,actorStates:task.plan.actors});sample();
 try{
  for(const end of task.checkpoints){
   while(m.t<end){advanceTo(m,Math.min(end,m.t+10000));sample();}
   try{
    validateGuardReference(m);sample();const graph=evaluateGuardReference(m);sample();
    const metadata=writeReferenceCheckpoint(directory,m,{id:task.plan.id,software,graph,finiteGameRef:task.finiteGameRef,windowMetrics:summarizeGuardReferenceWindows(m)});sample();
    emit({type:'checkpoint',step:m.t,metadata});const ack=await iterator.next();need(!ack.done,'Parent checkpoint acknowledgement absent');const value=JSON.parse(ack.value);
    need(['ack','reject'].includes(value.type)&&value.step===m.t,'Invalid parent acknowledgement');
   }catch(error){emit({type:'checkpoint-failure',step:m.t,message:error.stack});}
  }
  emit({type:'done'});
 }finally{lines.close();}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))runCase(process.argv[2]).catch(error=>{process.stdout.write(JSON.stringify({type:'failure',message:error.stack})+'\n');process.exitCode=1;});
