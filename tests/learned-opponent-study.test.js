// Artificial examples only. No inherited checkpoint/market read or MDP run.
import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';
import {fraction,pack,unpack,parseHex,hex,bitLength,guardedMultiply,quantize,vectorBytes,parseVector,reconstructGreedy,prepareMDP,iterateValues,bellmanCertificate,discountedPathValue,walkPolicy,evaluateProposal,compareFractions,MAX_STATES,plannedCases,STATUS,writeArtifact,verifyArtifact,contained,loadEvidenceCase,projectReference,assertFreshRun,identifyInputs,manifestDependencies} from '../research/learned-opponent-study.js';
import {layout} from '../research/adaptive-learning.js';
import {rational as Q,binary64} from '../research/incentive-study.js';
const plus=(a,b)=>Q(a.n*b.d+b.n*a.d,a.d*b.d),minus=(a,b)=>Q(a.n*b.d-b.n*a.d,a.d*b.d),mul=(a,b)=>Q(a.n*b.n,a.d*b.d),div=(a,b)=>Q(a.n*b.d,a.d*b.n);
const same=(a,b)=>assert.equal(a.n*b.d,b.n*a.d);
const periodic=k=>({id:'selected95',period:k,phases:k}),startup={id:'startup-only',period:null,phases:2};
function temporary(){const parent=path.resolve('.local'),directory=fs.mkdtempSync(path.join(parent,'learned-synthetic-'));return{directory,cleanup(){const target=fs.realpathSync(directory);assert(target.startsWith(fs.realpathSync(parent)+path.sep)&&path.basename(target).startsWith('learned-synthetic-'));fs.rmSync(target,{recursive:true,force:true});}};}
function finite({profitsA=[1,3,4,2],profitsB=[2,5,7,1],sets=[[0,1],[0,1]],capIndex=1}={}){return{prices:[0,1],sets,capIndex,rewards:{profitA:profitsA,profitB:profitsB,consumerSurplus:[10,8,8,6]}};}
function mdp({f=finite(),control=periodic(1),A=null,B=null,focal='A',coverage}={}){const N=control.phases*f.prices.length**2;return prepareMDP(f,control,[A??new Uint8Array(N),B??Uint8Array.from({length:N},(_,i)=>i%2)],focal,coverage);}
// Independent artificial oracle: rational Gaussian elimination of V=r+gamma PV.
function policyOracle(m,policy){
 const N=m.N,mat=Array.from({length:N},(_,s)=>{const row=Array.from({length:N+1},()=>Q(0n)),e=m.edge(s,policy[s]);row[s]=Q(1n);row[m.successors[e]]=minus(row[m.successors[e]],Q(19n,20n));row[N]=binary64(m.rawRewards[m.pairs[e]]);return row;});
 for(let c=0;c<N;c++){let pivot=c;while(pivot<N&&mat[pivot][c].n===0n)pivot++;assert(pivot<N);[mat[pivot],mat[c]]=[mat[c],mat[pivot]];const d=mat[c][c];mat[c]=mat[c].map(x=>div(x,d));for(let r=0;r<N;r++)if(r!==c){const f=mat[r][c];mat[r]=mat[r].map((x,k)=>minus(x,mul(f,mat[c][k])));}}
 return mat.map(row=>row[N]);
}

test('canonical negative hex parsing and pre-operation bit bounds reject oversized scalars',()=>{
 for(const x of [0n,1n,-1n,19n,-12345678901234567890n])assert.equal(parseHex(hex(x)),x);
 for(const s of ['-0x0','0x00','0xA','0x-1','123','-0x'])assert.throws(()=>parseHex(s));
 assert.throws(()=>parseHex('0x1'+'0'.repeat(260000)),/before parsing/);
 assert.throws(()=>guardedMultiply(1n<<600000n,1n<<600000n),/Product/);
 assert.throws(()=>unpack({numeratorHex:'0x2',denominatorHex:'0x4'}),/reduced/);
 assert.throws(()=>unpack({numeratorHex:'0x1',denominatorHex:'-0x1'}),/Positive/);
 same(unpack(pack(fraction(-5n,7n))),fraction(-5n,7n));
});
test('declared legacy hashes and sources maps bind every child without mapless or malformed fallback',()=>{
 const a='a'.repeat(64),b='b'.repeat(64);assert.deepEqual(manifestDependencies({hashes:{'research/old-source.js':a}}),{'research/old-source.js':a});assert.deepEqual(manifestDependencies({sources:{'research/older.js':a},inputHashes:{'research/nested/manifest.json':b},sourceHashes:{'research/older.js':a}}),{'research/older.js':a,'research/nested/manifest.json':b});
 for(const m of [{frozenAt:'old'},{hashes:null},{sources:[]},{hashes:{'research/a.js':'not-hash'}},{sources:{'../escape':a}},{hashes:{'C:/escape':a}},{sourceHashes:{'research/a.js':a},sources:{'research/a.js':b}}])assert.throws(()=>manifestDependencies(m));
});

test('artifact writes refuse overwrite, path escape and hash-rebound bytes',()=>{
 const tmp=temporary();try{const ref=writeArtifact(tmp.directory,'safe/bytes.bin',Buffer.from('original'));assert.equal(verifyArtifact(tmp.directory,ref).toString(),'original');assert.throws(()=>writeArtifact(tmp.directory,ref.file,Buffer.from('replacement')),/EEXIST/);assert.throws(()=>contained(tmp.directory,'../outside'),/escapes/);fs.writeFileSync(path.join(tmp.directory,ref.file),'changed!');assert.throws(()=>verifyArtifact(tmp.directory,ref),/hash/);}finally{tmp.cleanup();}
});

function checkpointFixture(root){
 const plan=plannedCases()[0],f=finite(),L=layout(f,plan.control),study='research/adaptive-learning-results/',put=(file,value)=>writeArtifact(root,file,Buffer.isBuffer(value)?value:Buffer.from(JSON.stringify(value)+'\n')),q=[],counts=[],policies=[];
 for(const firm of ['A','B']){q.push(put(study+'fixture/Q-'+firm+'.bin',Buffer.alloc(L.cells*8)));const b=Buffer.alloc(L.cells*2);b.writeUInt16LE(65535,0);counts.push(put(study+'fixture/counts-'+firm+'.bin',b));policies.push(put(study+'fixture/policy-'+firm+'.bin',Buffer.alloc(L.rows)));}
 const offsets=Buffer.alloc(L.offsets.length*4);L.offsets.forEach((x,i)=>offsets.writeUInt32LE(x,i*4));const offsetRef=put('offsets.bin',offsets),relative=ref=>({...ref,file:ref.file.slice(study.length)}),meta={step:2000000,T:2000000,phase:1,capExecutions:1,previousIndices:[0,0],control:plan.control,seed:plan.seed,initialization:'zero',alpha:.1,gamma:.95,layout:{n:2,rows:L.rows,cells:L.cells,offsetsSha256:offsetRef.sha256},countOverflow:[[[0,2000000]],[[0,2000000]]],files:{q:q.map(relative),counts:counts.map(relative),policies:policies.map(relative)}},metadata=put(study+'fixture/metadata.json',meta),entry={step:2000000,file:'fixture/metadata.json',sha256:metadata.sha256,terminal:{phase:1,previousIndices:[0,0]}},raw=put('research/artificial-finite.json',{scenario:{id:plan.scenario},finite:f}),old={...plan,id:plan.oldRunID,status:'completed frozen-policy evaluation',actualMainRounds:2000000,rawFile:raw.file,rawSha256:raw.sha256,checkpoints:[entry]},oldRecord=put(study+'records/'+plan.oldRunID+'.json',old),indexed={id:old.id,file:oldRecord.file.slice(study.length),sha256:oldRecord.sha256,checkpoints:[entry]},index={records:[indexed]};put(study+'index.json',index);
 return{plan,meta,old,index,input:{inputRoot:'project',oldRunID:plan.oldRunID,checkpointStep:2000000,finiteGame:raw,oldRecord,metadata,q,counts,savedPolicies:policies,checkpointEntry:entry}};
}
test('portable inherited-format artificial loader preserves terminal, Q and count identities',()=>{
 const tmp=temporary();try{const fixture=checkpointFixture(tmp.directory),input=identifyInputs(fixture.plan,{projectRoot:tmp.directory,index:fixture.index});assert.deepEqual(input,fixture.input);const loaded=loadEvidenceCase(fixture.plan,{projectRoot:tmp.directory,input});assert.equal(loaded.start,4);assert.equal(loaded.mdp.supportCount(0,0,0).stateVisits,2000000);assert.equal(loaded.mdp.worldPolicies[1][7],0);
  // Rebind the artificial metadata and old record to a semantically wrong global
  // count, so rejection is not merely an unchanged outer-file hash failure.
  fixture.meta.countOverflow[0][0][1]=1999999;fs.writeFileSync(path.join(tmp.directory,input.metadata.file),JSON.stringify(fixture.meta)+'\n');input.metadata=projectReference(tmp.directory,input.metadata.file);input.checkpointEntry.sha256=input.metadata.sha256;fixture.old.checkpoints[0].sha256=input.metadata.sha256;fs.writeFileSync(path.join(tmp.directory,input.oldRecord.file),JSON.stringify(fixture.old)+'\n');input.oldRecord=projectReference(tmp.directory,input.oldRecord.file);assert.throws(()=>loadEvidenceCase(fixture.plan,{projectRoot:tmp.directory,input}),/count total/);
 }finally{tmp.cleanup();}
});
test('every partial execution marker blocks a rerun without altering retained evidence',()=>{
 const tmp=temporary();try{for(const name of ['execution-start.json','journal.jsonl','records','artifacts','results.json','index.json','completion.json']){const file=path.join(tmp.directory,name);fs.writeFileSync(file,'preserved');assert.throws(()=>assertFreshRun(tmp.directory),/refusing rerun/);assert.equal(fs.readFileSync(file,'utf8'),'preserved');fs.unlinkSync(file);}}finally{tmp.cleanup();}
});

test('exact binary64 dyadic quantization uses ties-to-even for both signs',()=>{
 const u=2**-32;
 for(const [x,z] of [[0,0n],[u/2,0n],[1.5*u,2n],[2.5*u,2n],[-u/2,0n],[-1.5*u,-2n],[-2.5*u,-2n],[1,1n<<32n],[-1,-(1n<<32n)]])assert.equal(quantize(x),z);
 const v=[0n,-1n,2n];assert.deepEqual(parseVector(vectorBytes(v),3),v);
 assert.throws(()=>parseVector(Buffer.from('0x0'),1),/newline/);assert.throws(()=>parseVector(Buffer.from('0x1\n0x2\n'),1),/dimension/);
 assert.throws(()=>parseVector(Buffer.from('0x1'+'0'.repeat(1100)+'\n'),1),/budget/);
});
test('compact saved-Q reconstruction preserves low-index ties, B transpose and exact overflow counts',()=>{
 const f=finite(),control=periodic(1),L=layout(f,control),q=[new Float64Array(L.cells),new Float64Array(L.cells)],counts=[new Uint16Array(L.cells),new Uint16Array(L.cells)];
 q[1][L.offsets[2]+1]=7;counts[1][L.offsets[2]+1]=65535;
 const g=reconstructGreedy(f,control,q,counts,[[],[[L.offsets[2]+1,65536]]]);
 assert.equal(g.worldPolicies[0][1],0);assert.equal(g.worldPolicies[1][1],1);assert.equal(g.worldPolicies[1][2],0);
 assert.deepEqual(g.supportCount(1,1,1),{stateVisits:65536,chosenActionVisits:65536});
 assert.throws(()=>reconstructGreedy(f,control,q,counts,[[],[]],{expectedRounds:1}),/training horizon/);
 const brokenCounts=counts.map(a=>a.slice());brokenCounts[0][0]=65535;brokenCounts[0][1]=65535;
 assert.throws(()=>reconstructGreedy(f,control,q,brokenCounts,[[[1,65536],[0,65536]],[]]),/overflow/);
 q[0][0]=NaN;assert.throws(()=>reconstructGreedy(f,control,q,counts),/Malformed saved/);
 assert.throws(()=>reconstructGreedy(f,{...control,phases:1e9},q,counts),/dimensions/);
});
test('full cap memory and simultaneous fixed opponent are not a cap-reset shortcut',()=>{
 const m=mdp({B:Uint8Array.from([0,1,1,0])});
 const e0=m.edge(0,0),e1=m.edge(0,1);assert.equal(m.pairs[e0]%2,m.pairs[e1]%2);
 assert.notEqual(m.pairs[m.edge(0,0)]%2,m.pairs[m.edge(1,0)]%2);
 assert.equal(m.successors[e0],0);assert.equal(m.successors[e1],2);
 const b=mdp({focal:'B',A:Uint8Array.from([0,1,1,0]),B:new Uint8Array(4)});
 assert.equal(b.pairs[b.edge(1,1)],3);assert.equal(b.rawRewards[3],1);
 assert.equal(b.pairs[b.edge(0,1)],1);assert.equal(b.rawRewards[1],5); // no second reward transpose
});
test('startup guard is absorbing, while original selected K4 preserves its next phase',()=>{
 const f=finite(),N=8,A=new Uint8Array(N),B=new Uint8Array(N),m=mdp({f,control:startup,A,B});
 const path=walkPolicy(m,m.baseline,4);assert(path.path.states.every(s=>s>=4));assert.equal(path.path.h,0);assert.equal(path.path.c,1);
 const early=walkPolicy(m,m.baseline,0);assert.equal(early.path.h,1);assert.equal(early.path.states[1],4);
 const k4=mdp({control:periodic(4),A:new Uint8Array(16),B:new Uint8Array(16)});let state=0;
 for(let step=1;step<=4;step++){state=k4.successors[k4.edge(state,0)];assert.equal(Math.floor(state/4),step%4);}
});
test('exact discounted transient and cycle values agree with rational linear equations for every toy policy',()=>{
 const m=mdp({B:Uint8Array.from([0,1,1,0])});
 for(let bits=0;bits<16;bits++){const policy=Uint8Array.from({length:4},(_,s)=>(bits>>>s)&1),oracle=policyOracle(m,policy);for(let s=0;s<4;s++)same(walkPolicy(m,policy,s).value,oracle[s]);}
 same(discountedPathValue([100n,0n],1n,1,1),fraction(100n)); // positive transient, zero cycle mean
 assert.throws(()=>discountedPathValue([1n],1n,0,0),/dimensions/);
});
test('all-edge exact greedy response and signed Bellman bound contain exhaustive optimum',()=>{
 const m=mdp({B:Uint8Array.from([0,1,1,0])}),proposal=iterateValues(m),out=evaluateProposal(m,proposal.values,1);
 assert(proposal.completedSweeps>1&&proposal.completedSweeps<=600);assert.equal(out.certificate.allEdgesChecked,m.E);assert.equal(out.certificate.withinRequestedGap,true);
 let optimum=null;
 for(let bits=0;bits<16;bits++){const policy=Uint8Array.from({length:4},(_,s)=>(bits>>>s)&1),v=policyOracle(m,policy)[1];if(optimum===null||compareFractions(v,optimum)>0)optimum=v;}
 assert(compareFractions(out.response.value,optimum)<=0);assert(compareFractions(unpack(out.certificate.upperValue),optimum)>=0);
 const again=bellmanCertificate(m,proposal.values);assert.deepEqual(again.policy,out.candidate.policy);assert.equal(again.M,out.candidate.M);
});
test('negative residual remains signed, with exact lowest-index ties and no clamp',()=>{
 const f=finite({profitsA:Array(4).fill(1)}),m=mdp({f,B:new Uint8Array(4)}),out=evaluateProposal(m,Float64Array.from([30,30,30,30]),0);
 assert(out.candidate.M<0n);same(unpack(out.certificate.upperValue),fraction(20n));same(out.response.value,fraction(20n));assert.deepEqual(Array.from(out.candidate.policy),[0,0,0,0]);
});
test('raw negative response gain stays visible while the best-improvement lower bound is zero',()=>{
 const f=finite({profitsA:[0,0,1,1]}),m=mdp({f,A:Uint8Array.from([1,1,1,1]),B:new Uint8Array(4)}),out=evaluateProposal(m,Float64Array.from([1000,0,0,0]),0);
 same(out.baseline.value,fraction(20n));same(out.response.value,fraction(0n));assert.equal(out.performance.rawGainSign,'negative');same(unpack(out.performance.rawGain),fraction(-20n));same(unpack(out.performance.possibleGain.lower),fraction(0n));same(unpack(out.performance.relativeGain),fraction(-1n));assert.equal(out.certificate.withinRequestedGap,false);
});
test('zero and negative baselines have null relative gain, not a misleading percentage',()=>{
 for(const reward of [0,-1]){const m=mdp({f:finite({profitsA:Array(4).fill(reward)}),B:new Uint8Array(4)}),out=evaluateProposal(m,iterateValues(m).values,0);assert.equal(out.performance.relativeGain,null);assert.match(out.performance.relativeGainReason,/zero or negative/);assert.equal(out.performance.rawGainSign,'zero');}
});
test('coverage counts and exact normalized exposure distinguish remote transient and repeated cycles',()=>{
 // Constant zero opponent; baseline action1 yields 0 -> 2 -> 2. Only source0
 // is unvisited for A, while B's selected action is never tried everywhere.
 const m=mdp({A:Uint8Array.from([1,1,1,1]),B:new Uint8Array(4),coverage:(actor,s)=>({stateVisits:actor===0&&s===0?0:10,chosenActionVisits:actor===1?0:actor===0&&s===0?0:5})}),out=walkPolicy(m,m.baseline,0);
 assert.equal(out.path.h,1);assert.equal(out.path.c,1);assert.equal(out.coverage.A.unweighted.unvisitedStates,1);same(unpack(out.coverage.A.discounted.unvisitedStateExposure),fraction(1n,20n));same(unpack(out.coverage.B.discounted.neverTriedChosenActionExposure),fraction(1n));
 const early=discountedPathValue([1n,0n,0n],1n,2,1),late=discountedPathValue([0n,1n,0n],1n,2,1);assert(compareFractions(early,late)>0);
});
test('secondary eventual-cycle CS uses its own cycle and never enters the profit objective',()=>{
 const f=finite({profitsA:[0,0,1,1]}),m=mdp({f,A:new Uint8Array(4),B:new Uint8Array(4)}),out=evaluateProposal(m,iterateValues(m).values,0);
 same(out.baseline.eventualCycleCustomerBenefit,fraction(10n));same(out.response.eventualCycleCustomerBenefit,fraction(8n));same(unpack(out.performance.cycleCustomerBenefitDifference),fraction(-2n));assert.equal(out.performance.rawGainSign,'positive');
});
test('long exact transients survive decimal-digit limits using bounded canonical hex',()=>{
 const values=Array(5001).fill(0n);values[5000]=1n;const v=discountedPathValue(values,1n,5000,1),encoded=pack(v);
 assert(encoded.denominatorHex.length>4000);same(unpack(encoded),v);assert(bitLength(v.d)<1000000);assert(MAX_STATES>=values.length);
 assert.throws(()=>discountedPathValue(Array(MAX_STATES+1).fill(0n),1n,MAX_STATES,1),/dimensions/);
});
