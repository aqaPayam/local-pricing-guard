import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createLearners,step,advanceTo,randomWord,jump,actorNamespaces,phaseAt,isCap,rebuildMaxima,validateState,modelIdentity,encodeRound,f64Bytes,u32Bytes} from '../research/matched-clock-learning.js';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const toy=()=>({prices:[1,2,3],capIndex:1,sets:[[0,1],[1,2],[0,2]],rewards:{profitA:[-2,0,1,3,-1,2,0,1,0],profitB:[1,-3,0,0,2,-1,4,0,1],consumerSurplus:[9,8,7,8,6,5,7,5,3]}});
const actors=[[11,22,33,44],[55,66,77,88]];
function oracleWord(s){
 const mask=(1n<<32n)-1n,rot=(x,k)=>((x<<BigInt(k))|(x>>BigInt(32-k)))&mask;
 let a=s.map(BigInt),out=Number((rot((a[1]*5n)&mask,7)*9n)&mask),t=(a[1]<<9n)&mask;
 a[2]^=a[0];a[3]^=a[1];a[1]^=a[2];a[0]^=a[3];a[2]^=t;a[3]=rot(a[3],11);
 for(let i=0;i<4;i++)s[i]=Number(a[i]&mask);return out;
}
function refCreate(f,arm,T){return{f,arm,T,n:f.prices.length,q:[new Map(),new Map()],counts:[new Map(),new Map()],rng:actors.map(x=>x.slice()),t:0,p:0,prev:[2,2]};}
function refStep(m){
 const n=m.n,p=m.p,pa=m.prev[0],pb=m.prev[1],cap=p===0||(m.arm==='recurring4'&&p===4),support=r=>cap?[0,1]:m.f.sets[r],epsilon=m.t===0?1:m.t>=m.T-1?.01:Math.exp(-Math.log(100)*m.t/(m.T-1));
 const draws=m.rng.map(s=>[oracleWord(s)/2**32,oracleWord(s)/2**32]),rows=[(p*n+pa)*n+pb,(p*n+pb)*n+pa],legal=[support(pb),support(pa)],next=p===0||p===4?1:p+1;
 const scan=(f,row,list)=>{let best=list[0];for(const a of list.slice(1))if((m.q[f].get(row*n+a)??0)>(m.q[f].get(row*n+best)??0))best=a;return best;};
 const actions=legal.map((s,f)=>draws[f][0]<epsilon?s[Math.floor(draws[f][1]*s.length)]:scan(f,rows[f],s)),[a,b]=actions,index=a*n+b,nextRows=[(next*n+a)*n+b,(next*n+b)*n+a],nextCap=m.arm==='recurring4'&&next===4,nextSupport=r=>nextCap?[0,1]:m.f.sets[r];
 const nextMasks=[nextSupport(b),nextSupport(a)],old=actions.map((a,f)=>m.q[f].get(rows[f]*n+a)??0),max=nextRows.map((r,f)=>m.q[f].get(r*n+scan(f,r,nextMasks[f]))??0),rewards=[m.f.rewards.profitA[index],m.f.rewards.profitB[index]],newQ=old.map((v,f)=>v+.1*((rewards[f]+(19/20)*max[f])-v));
 for(let f=0;f<2;f++){const cell=rows[f]*n+actions[f];m.q[f].set(cell,newQ[f]);m.counts[f].set(cell,(m.counts[f].get(cell)??0)+1);}
 m.t++;m.p=next;m.prev=actions;return{actions,newQ,max};
}
function dataViewRecord(w){
 const out=new Uint8Array(120),v=new DataView(out.buffer);v.setUint32(0,w.round,true);
 [w.phase,...w.previous,...w.actions,(w.explored[0]?1:0)+(w.explored[1]?2:0)].forEach((a,i)=>v.setUint8(4+i,a));
 [w.epsilon,...w.rewards,...w.oldQ,...w.nextMax,...w.newQ].forEach((x,i)=>v.setFloat64(16+i*8,x,true));
 w.actorsAfter.flat().forEach((x,i)=>v.setUint32(88+i*4,x,true));return Buffer.from(out);
}

test('five phases, dense capacity, initial memory and exact cap executions agree across arms',()=>{
 const a=createLearners(toy(),'startup',{T:20,actorStates:actors}),b=createLearners(toy(),'recurring4',{T:20,actorStates:actors});
 assert.equal(a.cells,5*3**3);assert.equal(a.q[0].byteLength,b.q[0].byteLength);assert.equal(a.counts[0].byteLength,b.counts[0].byteLength);
 assert.equal(a.q[0].every(v=>Object.is(v,0)),true);assert.deepEqual(a.previous,[2,2]);
 const phases=[],caps=[];for(let i=0;i<12;i++){phases.push(b.phase);if(isCap(b.arm,b.phase))caps.push(i+1);step(a);step(b);assert.equal(b.phase,phaseAt(i+1));}
 assert.deepEqual(phases,[0,1,2,3,4,1,2,3,4,1,2,3]);assert.deepEqual(caps,[1,5,9]);assert.equal(a.caps,1);assert.equal(b.caps,3);assert.equal(phaseAt(1000000),4);assert.equal(phaseAt(2000000),4);
 validateState(a);validateState(b);
});

test('independent compact direct-scan reference matches all dense bits/counts with signed rewards and both arms',()=>{
 for(const arm of ['startup','recurring4']){
  const f=toy(),m=createLearners(f,arm,{T:1200,actorStates:actors}),r=refCreate(f,arm,1200);
  for(let t=0;t<1200;t++){const w=step(m,{trace:true}),ref=refStep(r);assert.deepEqual(w.actions,ref.actions);assert.deepEqual(w.newQ,ref.newQ);assert.deepEqual(w.nextMax,ref.max);}
  for(let f=0;f<2;f++)for(let i=0;i<m.cells;i++){assert.equal(Object.is(m.q[f][i],r.q[f].get(i)??0),true);assert.equal(m.counts[f][i],r.counts[f].get(i)??0);}
  assert.deepEqual(m.actors,r.rng);assert.deepEqual(m.previous,r.prev);validateState(m);
 }
});

test('PRNG uint32 sequence and published jump agree with a separate BigInt oracle',()=>{
 const a=[0xffffffff,0x80000000,123,42],b=a.slice();for(let i=0;i<500;i++)assert.equal(randomWord(a),oracleWord(b));
 const s=[1,2,3,4],r=s.slice(),expected=[0,0,0,0];
 for(const word of [0x8764000b,0xf542d2d3,0x6fa035c3,0x77f2db5b])for(let k=0;k<32;k++){if((word>>>k)&1)for(let j=0;j<4;j++)expected[j]=(expected[j]^r[j])>>>0;oracleWord(r);}
 assert.deepEqual(jump(s),expected);assert.equal(new Set(actorNamespaces().flatMap(r=>r.actors.map(s=>s.join(',')))).size,24);
});

test('mask differences never change actor draw consumption and seller B uses world rewards with own-coordinate rows',()=>{
 const a=createLearners(toy(),'startup',{T:44,actorStates:actors}),b=createLearners(toy(),'recurring4',{T:44,actorStates:actors}),rng=actors.map(s=>s.slice());
 for(let t=0;t<44;t++){
  const w=step(a,{trace:true});step(b);for(const s of rng){oracleWord(s);oracleWord(s);}
  assert.deepEqual(a.actors,rng);assert.deepEqual(a.actors,b.actors);
  assert.equal(w.rewards[1],a.finite.rewards.profitB[w.actions[0]*3+w.actions[1]]);
  const rowB=(w.phase*3+w.previous[1])*3+w.previous[0],cell=rowB*3+w.actions[1];assert.equal(Object.is(a.q[1][cell],w.newQ[1]),true);
 }
});

test('forbidden-cell poison cannot affect selection or bootstraps, and saved-state validation rejects it',()=>{
 const clean=createLearners(toy(),'recurring4',{T:60,actorStates:actors}),poison=createLearners(toy(),'recurring4',{T:60,actorStates:actors});
 const forbidden=[];for(let f=0;f<2;f++)for(let row=0;row<poison.rows;row++)for(let a=0;a<3;a++)if(!poison.supports[Math.floor(row/9)][row%3].includes(a)){const cell=row*3+a;poison.q[f][cell]=NaN;forbidden.push([f,cell]);}
 for(let t=0;t<60;t++){const a=step(clean,{trace:true}),b=step(poison,{trace:true});assert.deepEqual(a,b);}
 assert.throws(()=>validateState(poison),/Nonfinite/);for(const[f,c]of forbidden)poison.q[f][c]=0;assert.deepEqual(modelIdentity(clean),modelIdentity(poison));
});

test('cached decreases and exact ties reconstruct the smallest legal original index',()=>{
 const m=createLearners(toy(),'startup',{T:20,actorStates:actors});
 for(let f=0;f<2;f++)for(let row=0;row<m.rows;row++)for(const a of m.supports[Math.floor(row/9)][row%3])m.q[f][row*3+a]=-2;
 rebuildMaxima(m);for(let row=0;row<m.rows;row++){assert.equal(m.best[0][row],m.supports[Math.floor(row/9)][row%3][0]);assert.equal(m.max[0][row],-2);}
 for(let i=0;i<20;i++)step(m);validateState(m);
 const before=modelIdentity(m);assert.throws(()=>step(m),/horizon/);assert.deepEqual(modelIdentity(m),before);
});

test('canonical 120-byte fixture independently encodes fields, signed floats, flags, padding and actor order',()=>{
 const w={round:42,phase:4,previous:[61,2],actions:[0,60],explored:[true,false],epsilon:.125,rewards:[-3,7.5],oldQ:[0,-0],nextMax:[.25,-1],newQ:[-.3,.75],actorsAfter:[[1,0xffffffff,3,4],[5,6,0x80000000,8]]};
 const encoded=encodeRound(w),oracle=dataViewRecord(w);assert.deepEqual(encoded,oracle);assert.equal(sha(encoded),'f9f38c46ea497d541c0effb8aef0bfc0c3cb794d7995ab1494632984c15655f2');assert.equal(encoded.length,120);assert.deepEqual([...encoded.subarray(10,16)],[0,0,0,0,0,0]);
 assert.equal(encoded.readUInt32LE(0),42);assert.equal(encoded[9],1);assert.equal(Object.is(encoded.readDoubleLE(48),-0),true);assert.equal(encoded.readUInt32LE(112),0x80000000);
 for(const offset of [0,4,9,10,16,88,119]){const changed=Buffer.from(encoded);changed[offset]^=1;assert.notEqual(sha(changed),sha(encoded));}
 assert.throws(()=>encodeRound({...w,explored:[1,false]}),/flags/);assert.throws(()=>encodeRound({...w,previous:[62,0]}),/indices/);
});

test('two full transcript blocks equal separate DataView bytes, and checkpoint windows/counters bind exact transitions',()=>{
 const m=createLearners(toy(),'recurring4',{T:20000,actorStates:actors}),raw=Buffer.alloc(1200000),hashes=[];
 for(let t=0;t<20000;t++){const w=step(m,{trace:true});dataViewRecord(w).copy(raw,(t%10000)*120);if((t+1)%10000===0)hashes.push(sha(raw));}
 assert.deepEqual(m.transcriptBlocks.map(b=>b.sha256),hashes);assert.deepEqual(m.transcriptBlocks.map(b=>[b.firstRound,b.lastRound]),[[1,10000],[10001,20000]]);assert.equal(m.transcriptRounds,0);assert.equal(m.learningBlocks.length,2);
 for(const w of m.windows){assert.equal([...w.transitions.values()].reduce((a,b)=>a+b,0),w.rounds);assert.equal(w.rounds,w.endStep-w.startStep);let caps=0;for(let t=w.startStep;t<w.endStep;t++)caps+=t%4===0?1:0;assert.equal(w.capExecutions,caps);}
 validateState(m);const last=m.transcriptBlocks[1];m.transcriptBlocks[1]={...last,firstRound:9999};assert.throws(()=>validateState(m),/block inventory/);m.transcriptBlocks[1]=last;
 m.counts[0][0]++;assert.throws(()=>validateState(m),/Global action counts/);
});

test('invalid inputs, count/cache corruption and canonical little-endian identities reject explicitly',()=>{
 assert.throws(()=>createLearners(toy(),'other'),/arm/);assert.throws(()=>createLearners({...toy(),sets:[[1,0],[1],[2]]},'startup'),/masks/);
 const m=createLearners(toy(),'startup',{T:12,actorStates:actors});advanceTo(m,6);const before=modelIdentity(m);assert.throws(()=>advanceTo(m,5),/endpoint/);assert.deepEqual(modelIdentity(m),before);
 m.max[0][0]=123;assert.throws(()=>validateState(m),/Cached/);rebuildMaxima(m);validateState(m);
 assert.equal(f64Bytes(new Float64Array([1])).toString('hex'),'000000000000f03f');assert.equal(u32Bytes(new Uint32Array([0x12345678])).toString('hex'),'78563412');
});
