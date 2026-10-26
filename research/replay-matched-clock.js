// Independent read-only case component. A study-level authoritative parent must
// bind inputs, supervise this process, and validate all planned identities.
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import zlib from 'node:zlib';import {createHash} from 'node:crypto';import {fileURLToPath} from 'node:url';
import {createReplay,replayTo,canonicalBytes,assertForbiddenZero,expectedGraphClaim,expectedWindowClaims,frozenGraph,scan,initialActors} from './audit-matched-clock.js';
const need=(ok,message)=>{if(!ok)throw Error(message);};
class IntegrityError extends Error{}
const integrity=(ok,message)=>{if(!ok)throw new IntegrityError(message);};
const hash=b=>createHash('sha256').update(b).digest('hex');
const hashFile=p=>{const h=createHash('sha256'),fd=fs.openSync(p,'r'),b=Buffer.alloc(1048576);try{for(;;){const count=fs.readSync(fd,b,0,b.length,null);if(!count)break;h.update(b.subarray(0,count));}}finally{fs.closeSync(fd);}return h.digest('hex');};

export function compareClaim(actual,expected,label='claim'){
  need(typeof actual===typeof expected&&Array.isArray(actual)===Array.isArray(expected),label+': type differs');
  if(expected===null||typeof expected!=='object'){need(Object.is(actual,expected),label+': value differs');return;}
  need(actual!==null,label+': missing object');
  const a=Object.keys(actual).sort(),b=Object.keys(expected).sort();need(a.length===b.length&&a.every((x,i)=>x===b[i]),label+': keys differ');
  for(const key of b)compareClaim(actual[key],expected[key],label+'.'+key);
}
function relative(root,name){
  need(typeof name==='string'&&name&&!name.includes('\\')&&!name.includes(':')&&!name.startsWith('/')&&name.split('/').every(x=>x&&x!=='.'&&x!=='..'),'Unsafe relative artifact');
  const base=fs.realpathSync(root),p=fs.realpathSync(path.resolve(base,name));need(p.startsWith(base+path.sep),'Artifact escapes study directory');return p;
}
function json(bytes,canonical=false){
  const result=JSON.parse(bytes.toString('utf8'));
  if(canonical)need(bytes.equals(Buffer.from(JSON.stringify(result,null,2)+'\n')),'Noncanonical/duplicate-key checkpoint JSON');
  return result;
}
export function independentDense(gzip,ref,n,encoding){
  need(Number.isInteger(n)&&n>0&&n<=62&&['f64le','u32le'].includes(encoding),'Unsupported canonical dense dimension');
  const size=5*n*n*n*(encoding==='f64le'?8:4);
  need(ref.encoding===encoding&&ref.compression==='gzip-single-member'&&ref.rawBytes===size&&/^[a-f0-9]{64}$/.test(ref.rawSha256),'Canonical dense declaration differs');
  need(gzip.length>=18&&gzip.length<=size+65536&&gzip[0]===31&&gzip[1]===139&&gzip[2]===8&&gzip[3]===0&&gzip.readUInt32LE(4)===0,'Invalid canonical gzip header/ceiling');
  // The raw inflater reports exactly where its SINGLE deflate stream ended.
  const deflated=zlib.inflateRawSync(gzip.subarray(10),{info:true,maxOutputLength:size+1});
  need(deflated.engine.bytesWritten+18===gzip.length,'Trailing bytes or additional gzip member');
  need(deflated.buffer.length===size,'Canonical dense raw length differs');
  // Independently exercise the gzip wrapper's CRC/ISIZE checks as well.
  const checked=zlib.gunzipSync(gzip,{maxOutputLength:size+1});need(checked.equals(deflated.buffer),'Inconsistent gzip decoding');
  need(hash(checked)===ref.rawSha256,'Canonical dense raw hash differs');return checked;
}
function runtimeFingerprint(identity){
  const keys=['executableSha256','node','v8','platform','architecture','osRelease','execArgv'];
  need(identity&&keys.every(k=>Object.hasOwn(identity,k)),'Missing explicit Node backend fingerprint');
  return Object.fromEntries(keys.map(k=>[k,identity[k]]));
}

export function replayAndCheck(task,run,directory,{onCheckpoint=()=>{}}={}){
  const started=performance.now(),consumed=new Map();
  const plan=task.plan;need(plan&&['startup','recurring4'].includes(plan.arm)&&Number.isInteger(plan.seed)&&plan.seed>=907001&&plan.seed<=907012,'Unplanned replay identity');
  for(const key of ['id','arm','seed'])compareClaim(run[key],plan[key],'run.'+key);
  const T=task.T??2000000,ends=task.checkpoints??[T/2,T];
  need(Number.isSafeInteger(T)&&T>=2&&T<=2000000&&ends.length===2&&ends[0]===Math.floor(T/2)&&ends[1]===T,'Checkpoint plan differs');
  need(Array.isArray(task.originalTargets),'Bound original target array required');
  need(Array.isArray(run.checkpoints)&&run.checkpoints.length===2,'All checkpoint slots required');
  const finite=task.finite,m=createReplay(finite,plan.arm,{seed:plan.seed,T});
  compareClaim(plan.actors,m.rng,'independent actor namespace');
  function read(ref,ceiling=64000000){
    need(ref&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=ceiling&&/^[a-f0-9]{64}$/.test(ref.sha256),'Malformed bounded reference');
    const p=relative(directory,ref.file);integrity(fs.statSync(p).size===ref.bytes,'Artifact byte count differs');const bytes=fs.readFileSync(p);integrity(hash(bytes)===ref.sha256,'Artifact hash differs');
    if(consumed.has(p))integrity(consumed.get(p)===ref.sha256,'Artifact identity changed during replay');consumed.set(p,ref.sha256);return bytes;
  }
  const results=[];let matchedBlocks=0;
  function verify(slot){
    const meta=json(read(slot.metadata),true),N=5*m.n*m.n,cells=N*m.n;
    compareClaim(Object.keys(meta).sort(),['schemaVersion','id','arm','seed','step','n','phases','layout','finiteGameRef','learning','terminal','actors','caps','allocation','artifacts','policies','policyCoordinateScope','windows','windowMetrics','curves','transcriptBlocks','transcriptPartial','cacheIdentity','graph','software'].sort(),'complete metadata schema');
    const scalar={schemaVersion:1,id:plan.id,arm:plan.arm,seed:plan.seed,step:m.t,n:m.n,phases:5,layout:'dense5-own-rival-original-action-v1'};
    for(const [key,value]of Object.entries(scalar))compareClaim(meta[key],value,'metadata.'+key);
    compareClaim(meta.finiteGameRef,task.finiteGameRef,'finite game identity');
    if(task.software?.executableSha256)compareClaim(runtimeFingerprint(meta.software),runtimeFingerprint(task.software),'software backend identity');
    else compareClaim(meta.software,task.software,'artificial software identity');
    compareClaim(meta.learning,{T,alpha:.1,gamma:19/20,initialization:'positive-zero'},'learning');
    compareClaim(meta.allocation,{cellsPerFirm:cells,qBytesPerFirm:8*cells,countBytesPerFirm:4*cells},'equal dense allocation');
    compareClaim(meta.terminal,{phase:m.phase,previousIndices:m.previous},'actual terminal clock/history');compareClaim(meta.actors,m.rng,'post-round actors');compareClaim(meta.caps,m.caps,'cap count');
    need(meta.artifacts?.q?.length===2&&meta.artifacts?.counts?.length===2,'Both Q/count artifact pairs required');
    assertForbiddenZero(m);
    for(let firm=0;firm<2;firm++)for(const [key,encoding,values,width]of [['q','f64le',m.q[firm],8],['counts','u32le',m.counts[firm],4]]){
      const ref=meta.artifacts[key][firm],raw=independentDense(read(ref,cells*width+65536),ref,m.n,encoding);
      need(raw.equals(canonicalBytes(values,key==='q'?'f64':'u32')),'Every dense '+key+' bit mismatch for firm'+firm);
    }
    const graph=frozenGraph(m),policies=meta.policies;
    need(policies?.own?.length===2&&policies?.world?.length===2,'Both policy coordinate families required');
    const expectedCache={best:[],maximum:[]};
    for(let firm=0;firm<2;firm++){
      need(read(policies.own[firm],N).equals(Buffer.from(graph.focalPolicies[firm])),'Own masked greedy policy mismatch');
      need(read(policies.world[firm],N).equals(Buffer.from(graph.worldPolicies[firm])),'World masked greedy policy mismatch');
      const maxima=new Float64Array(N);
      for(let row=0;row<N;row++){const phase=Math.floor(row/(m.n*m.n)),own=Math.floor(row/m.n)%m.n,rival=row%m.n;maxima[row]=scan(m,firm,phase,own,rival).value;}
      expectedCache.best.push(hash(graph.focalPolicies[firm]));expectedCache.maximum.push(hash(canonicalBytes(maxima,'f64')));
    }
    compareClaim(meta.cacheIdentity,expectedCache,'complete cache identity');
    compareClaim(meta.policyCoordinateScope,'own rows phase/own/rival; WORLD rows phase/A/B; B mapped exactly once','policy coordinate scope');
    const windows=m.windows.map(w=>({startStep:w.start,endStep:w.end,rounds:w.rounds,transitions:[...w.transitions].sort((a,b)=>a[0]-b[0]),maxAllowed:w.maxAllowed,explorations:w.explorationDecisions,priceChanges:w.priceChanges,capExecutions:w.caps}));
    compareClaim(meta.windows,windows,'complete integer training windows');compareClaim(meta.curves,m.learningBlocks,'every approximate display block and integer counter');
    compareClaim(meta.windowMetrics,expectedWindowClaims(m),'all exact training-window reward/geometry/counter means');
    compareClaim(meta.transcriptBlocks,m.transcript.blocks,'all recorded round-transcript blocks');
    const tr=m.transcript.snapshot();compareClaim(meta.transcriptPartial,{rounds:tr.pendingRounds,bytes:tr.pendingBytes,sha256:tr.pendingSha256,scope:'Incomplete engineering tail, not a completed block'},'partial transcript identity');
    const expected=expectedGraphClaim(m,{originalTargets:task.originalTargets}),saved=json(read(meta.graph),true);compareClaim(saved,expected,'every exact graph science/ancillary field');
    // Read-only altered-claim controls on this successfully recomputed endpoint.
    // Fresh values are compared by the SAME strict predicate used above; no
    // original evidence is edited and no second training run is introduced.
    const controls=[];
    const altered=(label,claim,change)=>{const bad=structuredClone(claim);change(bad);let rejected=false;try{compareClaim(bad,claim,label);}catch{rejected=true;}need(rejected,'Scientific negative control unexpectedly accepted: '+label);controls.push({test:label,rejected:true});};
    altered('actual terminal NEXT clock',meta.terminal,x=>{x.phase=(x.phase+1)%5;});
    altered('post-round actor word',meta.actors,x=>{x[0][0]=(x[0][0]+1)>>>0;});
    altered('extra cache identity entry',meta.cacheIdentity,x=>{x.best.push('0'.repeat(64));});
    altered('one-based round-block timing',meta.transcriptBlocks,x=>{x[0].firstRound--;});
    altered('round-block digest',meta.transcriptBlocks,x=>{x[0].sha256='f'.repeat(64);});
    altered('complete executed training window',meta.windows,x=>{x.at(-1).priceChanges[0]++;});
    altered('display profit block',meta.curves,x=>{x[0].profitSums[0]+=1;});
    altered('joint B cycle profit',expected,x=>{x.actualTerminal.cycleMetrics.profits.B.numerator=(BigInt(x.actualTerminal.cycleMetrics.profits.B.numerator)+1n).toString();});
    altered('preview cap-rule label',expected,x=>{x.terminalPreview128[0].cap=!x.terminalPreview128[0].cap;});
    for(const[family,values,encoding]of[['Q',m.q[0],'f64'],['counts',m.counts[1],'u32']]){const original=canonicalBytes(values,encoding),bad=Buffer.from(original);bad[0]^=1;need(!bad.equals(original),'Dense bit negative control unexpectedly accepted');controls.push({test:'all-bit '+family+' comparator',rejected:true});}
    matchedBlocks=Math.max(matchedBlocks,m.transcript.blocks.length);
    return{step:m.t,parentEligible:true,matched:true,available:true,metadataSha256:slot.metadata.sha256,graphSha256:meta.graph.sha256,reason:null,phase:m.phase,previousIndices:m.previous.slice(),cycleLength:expected.actualTerminal.cycleNodesFromStart.length,cycleCustomerBenefit:expected.actualTerminal.cycleMetrics.consumerSurplus,worldStatesChecked:N,canonicalDenseCellsPerFirm:cells,transcriptBlocksMatched:m.transcript.blocks.length,corruptionNegativeControls:controls};
  }
  const maximum=run.checkpoints.reduce((end,slot,index)=>{
    compareClaim(slot.step,ends[index],'checkpoint slot clock');need(typeof slot.parentEligible==='boolean','Explicit checkpoint parent eligibility required');return slot.parentEligible?Math.max(end,slot.step):end;
  },0);
  for(let index=0;index<2;index++){
    const slot=run.checkpoints[index];
    if(!slot.parentEligible){const result={step:ends[index],parentEligible:false,matched:false,available:false,reason:'No complete primary checkpoint was parent-eligible before termination/deadline'};results.push(result);onCheckpoint(result);continue;}
    replayTo(m,slot.step);
    let result;try{result=verify(slot);}catch(error){if(error instanceof IntegrityError)throw error;result={step:slot.step,parentEligible:true,matched:false,available:false,reason:String(error.message)};}
    results.push(result);onCheckpoint(result);
  }
  need(m.t===maximum,'Independent replay did not reach every eligible checkpoint');
  for(const [p,original]of consumed)integrity(hashFile(p)===original,'Consumed artifact changed during replay');
  return{id:plan.id,arm:plan.arm,seed:plan.seed,replayedRounds:m.t,fullHorizonReplayed:m.t===T,checkpointResults:results,allEligibleCheckpointsMatched:results.filter(x=>x.parentEligible).every(x=>x.matched),allPlannedCheckpointsMatched:results.every(x=>x.matched),transcriptBlocksMatched:matchedBlocks,consumedFiles:consumed.size,finalConsumedIntegrityCheck:true,seconds:(performance.now()-started)/1000,nodeProcessRSSBytes:process.memoryUsage().rss,
    scope:'Independent same-V8 full-from-zero reexecution to eligible endpoints; complete checkpoint bytes and all recorded round-block hashes, exact graph/window claims. Shared V8/crypto/zlib backend; this component alone is not study-level acceptance.'};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{
    if(process.argv.length===3&&process.argv[2]==='--runtime'){
      process.stdout.write(JSON.stringify({runtime:{executablePath:process.execPath,executableSha256:hashFile(process.execPath),node:process.version,v8:process.versions.v8,platform:process.platform,architecture:process.arch,osRelease:os.release(),execArgv:process.execArgv},actors:initialActors()})+'\n');
    }else{
    const args=process.argv.slice(2),get=key=>{const i=args.indexOf(key);need(i>=0&&typeof args[i+1]==='string','Missing '+key);return args[i+1];};
    const task=json(fs.readFileSync(get('--task'))),run=json(fs.readFileSync(get('--record'))),directory=get('--directory');
    const result=replayAndCheck(task,run,directory,{onCheckpoint:value=>process.stdout.write(JSON.stringify({type:'checkpoint audited',result:value})+'\n')});
    process.stdout.write(JSON.stringify({type:'replay finished',result})+'\n');process.exitCode=result.allEligibleCheckpointsMatched?0:1;
    }
  }catch(error){process.stdout.write(JSON.stringify({type:'replay failure',failureKind:error instanceof IntegrityError?'integrity':'operational',reason:error.message})+'\n');process.exitCode=1;}
}
