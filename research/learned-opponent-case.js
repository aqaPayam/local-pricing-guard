// One isolated case process. The Python parent owns the hard deadline and PID.
import fs from 'node:fs';import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareMDP,solveLoadedCase,loadEvidenceCase,float64Bytes,contained} from './learned-opponent-study.js';
export function main(taskPath){
const taskFile=path.resolve(taskPath),task=JSON.parse(fs.readFileSync(taskFile,'utf8'));
task.directory=path.resolve(path.dirname(taskFile),'..');task.projectRoot=process.cwd();
const emit=message=>fs.writeSync(1,JSON.stringify(message)+'\n');
let stage='input';
try{
 const p=task.payload;let loaded;
 if(task.mode==='artificial'){const mdp=prepareMDP(p.record,p.control,p.worldPolicies.map(a=>Uint8Array.from(a)),p.focal);loaded={mdp,start:p.start,input:{inputRoot:'artificial memory fixture',scope:'No inherited market or learned checkpoint'}};}
 else if(task.mode==='evidence')loaded=loadEvidenceCase(task.plan,{projectRoot:task.projectRoot,input:p.input,declaredHashes:JSON.parse(fs.readFileSync(path.join(task.directory,'manifest.json'),'utf8')).inputHashes});
 else throw Error('Unknown isolated case mode');
 const result=solveLoadedCase(task.plan,loaded,task.directory,{onIteration:proposal=>{
  if(proposal.completedSweeps!==1&&proposal.completedSweeps%25!==0&&proposal.difference>1e-10&&proposal.completedSweeps!==600)return;
  const bytes=float64Bytes(proposal.values),file='artifacts/'+task.plan.id+'/progress-latest.f64le',full=contained(task.directory,file),temporary=full+'.tmp';fs.mkdirSync(path.dirname(full),{recursive:true});fs.writeFileSync(temporary,bytes,{flag:'wx'});fs.renameSync(temporary,full);
  emit({type:'iteration',completedSweeps:proposal.completedSweeps,difference:proposal.difference,proposal:{file,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')},processRSSBytes:process.memoryUsage().rss});
  // Acknowledgement prevents replacement before the parent has hashed and copied
  // the completed proposal. A killed process cannot silently salvage it later.
  const ack=Buffer.alloc(1);if(fs.readSync(0,ack,0,1,null)!==1||ack[0]!==10)throw Error('Parent did not acknowledge the completed proposal');
 },onStage:name=>{stage=name;emit({type:'stage',stage});}});
 emit({type:'certificate',complete:result.complete});emit({type:'done'});
}catch(error){emit({type:'failure',failure:{stage,message:error.message,errorType:error.name}});process.exitCode=1;}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))main(process.argv[2]);
