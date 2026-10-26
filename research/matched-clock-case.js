// One supervised primary process. No case execution on import.
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import {fileURLToPath} from 'node:url';
import {createLearners,advanceTo,validateState} from './matched-clock-learning.js';
import {evaluateFrozen,summarizeWindows} from './matched-clock-graph.js';
import {readRef,sha,writeCheckpoint} from './matched-clock-io.js';
import {runtimeIdentity,runtimeFingerprint} from './matched-clock-study.js';
const need=(v,m)=>{if(!v)throw Error(m);};
export async function runCase(taskFile){
 const task=JSON.parse(fs.readFileSync(taskFile)),directory=path.dirname(path.dirname(path.resolve(taskFile)));
 need(['artificial','frozen-primary'].includes(task.executionMode),'Declared artificial or frozen-primary mode required');
 const actualSoftware=runtimeIdentity();need(JSON.stringify(runtimeFingerprint(actualSoftware))===JSON.stringify(runtimeFingerprint(task.software)),'Child executable/V8 identity differs');
 if(task.executionMode==='frozen-primary'){
  const bytes=fs.readFileSync(path.join(directory,'manifest.json'));need(sha(bytes)===task.manifestSha256,'Child frozen manifest hash differs');const m=JSON.parse(bytes);
  need(m.plan.runs.some(p=>JSON.stringify(p)===JSON.stringify(task.plan))&&JSON.stringify(m.inputs.finiteGame)===JSON.stringify(task.finiteGameRef),'Child planned input identity differs');
  const original=JSON.parse(readRef(task.projectRoot,task.finiteGameRef));need(JSON.stringify(original)===JSON.stringify(task.record),'Task original game differs from frozen raw input');
 }
 const lines=readline.createInterface({input:process.stdin,crlfDelay:Infinity}),iterator=lines[Symbol.asyncIterator]();
 const emit=value=>process.stdout.write(JSON.stringify(value)+'\n'),sample=()=>emit({type:'sample',rssBytes:process.memoryUsage().rss});
 const m=createLearners(task.record??task.finite,task.plan.arm,{seed:task.plan.seed,T:task.T,actorStates:task.plan.actors});sample();
 try{
  for(const end of task.checkpoints){
   while(m.t<end){advanceTo(m,Math.min(end,m.t+10000));sample();}
   try{
    validateState(m);sample();const graph=evaluateFrozen(m,{certifyFloor:task.executionMode!=='artificial'||task.certifyArtificialFloor===true});sample();
    const metadata=writeCheckpoint(directory,m,{id:task.plan.id,software:actualSoftware,graph,finiteGameRef:task.finiteGameRef,windowMetrics:summarizeWindows(m)});sample();
    emit({type:'checkpoint',step:m.t,metadata});const ack=await iterator.next();need(!ack.done,'Parent checkpoint acknowledgement absent');const value=JSON.parse(ack.value);need(['ack','reject'].includes(value.type)&&value.step===m.t,'Invalid parent acknowledgement');
   }catch(error){emit({type:'checkpoint-failure',step:m.t,message:error.stack});}
  }
  emit({type:'done'});
 }finally{lines.close();}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))runCase(process.argv[2]).catch(error=>{process.stdout.write(JSON.stringify({type:'failure',message:error.stack})+'\n');process.exitCode=1;});
