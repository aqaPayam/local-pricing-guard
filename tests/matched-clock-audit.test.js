// Wholly artificial tests; no inherited tables, Q, checkpoints or outcomes read.
import test from 'node:test';
import assert from 'node:assert/strict';
import {word,jumped,initialActors,phaseAfter,following,capped,epsilon,createReplay,support,rowStart,scan,replayStep,replayTo,assertForbiddenZero,canonicalBytes,exactBinary64,frozenGraph,encodeTranscriptRound} from '../research/audit-matched-clock.js';
import {createHash} from 'node:crypto';

const toy=()=>({prices:[1,2,3],capIndex:0,sets:[[0,2],[1],[0,1]],rewards:{
  profitA:[0,-2,4,7,0,-1,3,2,1],profitB:[9,8,7,6,5,4,3,2,1],consumerSurplus:[18,17,16,15,14,13,12,11,10]}});
function bigWord(s){
  const mask=(1n<<32n)-1n,rotate=(x,k)=>((x<<BigInt(k))|(x>>BigInt(32-k)))&mask;
  const out=(rotate((s[1]*5n)&mask,7)*9n)&mask,t=(s[1]<<9n)&mask;
  s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rotate(s[3],11);
  for(let i=0;i<4;i++)s[i]&=mask;return Number(out);
}
function bigJump(state){
  const s=state.map(BigInt),out=[0n,0n,0n,0n];
  for(const polynomial of [0x8764000bn,0xf542d2d3n,0x6fa035c3n,0x77f2db5bn])for(let i=0n;i<32n;i++){
    if(polynomial&(1n<<i))for(let j=0;j<4;j++)out[j]^=s[j];bigWord(s);
  }
  return out.map(Number);
}

test('independent uint32 generator and jump equal a separate BigInt arithmetic oracle',()=>{
  for(const initial of [[1,2,3,4],[0xffffffff,0x80000000,5,0xabcdef01]]){
    const a=initial.slice(),b=initial.map(BigInt);
    for(let i=0;i<1000;i++)assert.equal(word(a),bigWord(b));
    assert.deepEqual(a,b.map(Number));assert.deepEqual(jumped(initial),bigJump(initial));
  }
  const all=initialActors();assert.equal(all.length,12);assert.equal(new Set(all.flatMap(r=>r.actors.map(a=>a.join(',')))).size,24);
  assert.deepEqual(all[0].actors[0],[907001,907002,907003,907004]);assert.deepEqual(all[0].actors[1],bigJump(all[0].actors[0]));
});

test('common five-phase clock never returns to activation and caps only executions1/5/9',()=>{
  let p=0;const caps={startup:[],recurring4:[]};
  for(let t=0;t<13;t++){assert.equal(p,phaseAfter(t));for(const arm of Object.keys(caps))if(capped(arm,p))caps[arm].push(t+1);p=following(p);}
  assert.deepEqual(caps.startup,[1]);assert.deepEqual(caps.recurring4,[1,5,9,13]);
  assert.equal(phaseAfter(1000000),4);assert.equal(phaseAfter(2000000),4);
  assert.equal(epsilon(0,20),1);assert.equal(epsilon(19,20),.01);assert.equal(epsilon(7,20),Math.exp(-Math.log(100)*7/19));
});

test('dense allocation matches arms, next legal scans ignore poisoned forbidden cells and ties choose original index',()=>{
  const m=createReplay(toy(),'startup',{T:20}),other=createReplay(toy(),'recurring4',{T:20});
  assert.equal(m.q[0].length,5*3**3);assert.equal(m.q[0].byteLength,other.q[0].byteLength);
  assert.deepEqual(support(m,4,0),[0,2]);assert.deepEqual(support(other,4,0),[0]);
  const off=rowStart(m,2,1,0);m.q[0][off]=5;m.q[0][off+1]=1e100;m.q[0][off+2]=5;
  assert.deepEqual(scan(m,0,2,1,0),{action:0,value:5});assert.throws(()=>assertForbiddenZero(m),/Forbidden/);
  m.q[0][off+1]=0;assertForbiddenZero(m);
});

test('both pre-update bootstraps and B world reward orientation are sealed before updates',()=>{
  const m=createReplay(toy(),'startup',{T:20});replayStep(m);assert.equal(m.phase,1);
  for(let own=0;own<3;own++)for(let rival=0;rival<3;rival++){
    const base=rowStart(m,2,own,rival),legal=support(m,2,rival);
    for(let a=0;a<3;a++){m.q[0][base+a]=legal.includes(a)?5:1e90;m.q[1][base+a]=legal.includes(a)?8:1e90;}
  }
  const w=replayStep(m,{trace:true}),[a,b]=w.actions,pair=a*3+b;
  assert.deepEqual(w.nextMaxima,[5,8]);
  assert.equal(w.targets[0],toy().rewards.profitA[pair]+.95*5);
  assert.equal(w.targets[1],toy().rewards.profitB[pair]+.95*8);
  assert.equal(m.q[0][w.cells[0]],w.priorQ[0]+.1*(w.targets[0]-w.priorQ[0]));
  assert.equal(m.q[1][w.cells[1]],w.priorQ[1]+.1*(w.targets[1]-w.priorQ[1]));
  assert.equal(w.cells[1],rowStart(m,w.phase,w.previous[1],w.previous[0])+b);
});

test('fixed draw counts remain paired despite different masks, with complete counts and tail source histories',()=>{
  const a=createReplay(toy(),'startup',{T:40}),b=createReplay(toy(),'recurring4',{T:40});
  replayTo(a,20);replayTo(b,20);assert.deepEqual(a.rng,b.rng);assert.equal(a.phase,4);assert.equal(b.phase,4);
  replayTo(a,40);replayTo(b,40);assert.deepEqual(a.rng,b.rng);assert.equal(a.caps,1);assert.equal(b.caps,10);
  for(const m of [a,b]){
    assertForbiddenZero(m);for(const w of m.windows)assert.equal([...w.transitions.values()].reduce((x,y)=>x+y,0),w.rounds);
    const states=initialActors()[0].actors.map(s=>s.slice());for(const s of states)for(let i=0;i<80;i++)word(s);assert.deepEqual(m.rng,states);
    assert.equal(canonicalBytes(m.q[0],'f64').length,8*5*3**3);assert.equal(canonicalBytes(m.counts[0],'u32').length,4*5*3**3);
  }
});

test('all-zero/signed artificial rewards and interrupted numerical replay preserve exact checkpoint bits',()=>{
  const f=toy(),left=createReplay(f,'recurring4',{T:60}),right=createReplay(f,'recurring4',{T:60});
  replayTo(left,60);replayTo(right,30);replayTo(right,60);
  for(let firm=0;firm<2;firm++){assert.ok(canonicalBytes(left.q[firm],'f64').equals(canonicalBytes(right.q[firm],'f64')));assert.ok(canonicalBytes(left.counts[firm],'u32').equals(canonicalBytes(right.counts[firm],'u32')));}
  const z=toy();z.rewards.profitA.fill(0);z.rewards.profitB.fill(0);const zero=createReplay(z,'startup',{T:20});replayTo(zero,20);assert.ok(zero.q.every(q=>q.every(v=>Object.is(v,0))));assertForbiddenZero(zero);
});

test('exact saved-weight graph has no activation cycle and retains B observation transpose',()=>{
  assert.deepEqual(exactBinary64(.5),{n:1n,d:2n});assert.deepEqual(exactBinary64(-.125),{n:-1n,d:8n});assert.deepEqual(exactBinary64(Number.MIN_VALUE),{n:1n,d:1n<<1074n});
  const f={prices:[1,2],capIndex:0,sets:[[0,1],[0,1]],rewards:{profitA:[1,2,3,4],profitB:[4,3,2,1],consumerSurplus:[10,8,7,4]}};
  const m=createReplay(f,'startup',{T:20});
  // At B's own0/rival1 row, choose1. Its WORLD source is A1/B0.
  m.q[1][rowStart(m,1,0,1)+1]=5;
  const graph=frozenGraph(m),world=(1*2+1)*2+0;
  assert.equal(graph.worldPolicies[1][world],1);assert.equal(graph.worldPolicies[1][(1*2+0)*2+1],0);
  assert.equal(graph.cycles.reduce((s,c)=>s+c.basinStates,0),5*2*2);
  for(const c of graph.cycles){assert.equal(c.nodes.length%4,0);assert.ok(c.nodes.every(s=>Math.floor(s/4)>0));}
  const actual=graph.actualTerminal;assert.equal(actual.transientRounds,1);assert.deepEqual(actual.cycleMetrics.consumerSurplus,{numerator:'10',denominator:'1'});
});

test('all-round transcript encoding has independent byte-order oracle, exact blocks and no skipped rounds',()=>{
  const w={step:0x1020304,phase:4,previous:[61,2],actions:[3,5],exploreFlags:2,epsilon:.125,expectedProfits:[-1,2],priorQ:[-0,4],nextMaxima:[5,6],newQ:[7,8],rngAfter:[[1,2,0xffffffff,4],[5,6,7,0xabcdef01]]};
  const bytes=encodeTranscriptRound(w);assert.equal(bytes.length,120);assert.equal(bytes.readUInt32LE(0),w.step);
  // Literal SHA from an independently packed Python struct '<IBBBBBB6x9d8I'.
  assert.equal(createHash('sha256').update(bytes).digest('hex'),'8f92dc34877d01c629c68bdc7bd63cfe27b0e600ce354fcfd83054ee03dfd676');
  assert.deepEqual([...bytes.subarray(4,10)],[4,61,2,3,5,2]);assert.deepEqual([...bytes.subarray(10,16)],[0,0,0,0,0,0]);
  assert.equal(bytes.readDoubleLE(16),.125);assert.equal(bytes.readDoubleLE(24),-1);assert.equal(bytes.readDoubleLE(32),2);assert.ok(Object.is(bytes.readDoubleLE(40),-0));assert.equal(bytes.readUInt32LE(116),0xabcdef01);
  const m=createReplay(toy(),'startup',{T:20,transcriptBlockSize:2}),all=[];
  for(let i=0;i<5;i++){
    const x=replayStep(m,{trace:true}),flags=Number(x.draws[0][0]<x.epsilon)+2*Number(x.draws[1][0]<x.epsilon);all.push(encodeTranscriptRound({...x,step:x.step+1,exploreFlags:flags,expectedProfits:[m.finite.rewards.profitA[x.actions[0]*3+x.actions[1]],m.finite.rewards.profitB[x.actions[0]*3+x.actions[1]]],rngAfter:m.rng}));
  }
  // Decision flags are reconstructed independently from the recorded draws.
  const expected=createHash('sha256').update(Buffer.concat(all.slice(0,2))).digest('hex');
  assert.equal(m.transcript.blocks.length,2);assert.equal(m.transcript.blocks[0].sha256,expected);assert.equal(m.transcript.snapshot().pendingBytes,120);
  assert.equal(m.transcript.blocks[0].firstRound,1);assert.equal(m.transcript.blocks[0].lastRound,2);
  assert.throws(()=>m.transcript.record(99),/Skipped/);
  for(const bad of [{...w,step:0},{...w,phase:5},{...w,exploreFlags:4},{...w,actions:[62,0]},{...w,epsilon:NaN}])assert.throws(()=>encodeTranscriptRound(bad));
});
