// Cross-author interoperability on invented tables only; no inherited inputs.
import test from 'node:test';
import assert from 'node:assert/strict';
import * as primary from '../research/matched-clock-learning.js';
import * as independent from '../research/audit-matched-clock.js';
import {evaluateFrozen} from '../research/matched-clock-graph.js';
import {createHash} from 'node:crypto';

function artificial(zero=false){
 const n=7;
 return{prices:Array.from({length:n},(_,i)=>1+i/16),capIndex:2,
  sets:Array.from({length:n},(_,r)=>Array.from({length:n},(_,a)=>a).filter(a=>a===r||(a+2*r)%3!==0)),
  rewards:{profitA:Array.from({length:n*n},(_,i)=>zero?0:(Math.floor(i/n)-2*(i%n))/8),
   profitB:Array.from({length:n*n},(_,i)=>zero?0:(3*(i%n)-Math.floor(i/n))/16),
   consumerSurplus:Array.from({length:n*n},(_,i)=>zero?0:40-i/32)}};
}

function checkpointEqual(a,b){
 assert.equal(a.t,b.t);assert.equal(a.phase,b.phase);assert.deepEqual(a.previous,b.previous);
 assert.deepEqual(a.actors,b.rng);assert.equal(a.caps,b.caps);
 for(let f=0;f<2;f++){
  assert.deepEqual(primary.f64Bytes(a.q[f]),independent.canonicalBytes(b.q[f],'f64'));
  assert.deepEqual(primary.u32Bytes(a.counts[f]),independent.canonicalBytes(b.counts[f],'u32'));
 }
 const blocks=b.transcript.snapshot().blocks;
 assert.equal(a.transcriptBlocks.length,blocks.length);
 for(let i=0;i<blocks.length;i++){
  assert.equal(a.transcriptBlocks[i].firstRound,blocks[i].firstRound);
  assert.equal(a.transcriptBlocks[i].lastRound,blocks[i].lastRound);
  assert.equal(a.transcriptBlocks[i].sha256,blocks[i].sha256);
 }
 assert.equal(primary.validateState(a),true);
 assert.equal(independent.assertForbiddenZero(b),true);
}

test('separately authored primary/cache and replay/scan match both checkpoints and every transcript block',()=>{
 for(const zero of [false,true])for(const seed of [907001,907012])for(const arm of ['startup','recurring4']){
  const finite=artificial(zero),a=primary.createLearners(finite,arm,{seed,T:20000}),b=independent.createReplay(finite,arm,{seed,T:20000});
  for(const endpoint of [10000,20000]){
   primary.advanceTo(a,endpoint);independent.replayTo(b,endpoint);checkpointEqual(a,b);
  }
 }
});

test('independent whole-state graphs agree on every edge, basin, distance, exact cycle payoff and actual start',()=>{
 const pair=v=>({numerator:v.numerator,denominator:v.denominator});
 for(const arm of ['startup','recurring4']){
  const finite=artificial(),a=primary.createLearners(finite,arm,{seed:907012,T:240}),b=independent.createReplay(finite,arm,{seed:907012,T:240});
  primary.advanceTo(a,240);independent.replayTo(b,240);
  // These deliberately nonmonotone invented masks are numerical graph tests,
  // not premises for an economic floor, hence certifyFloor:false is explicit.
  const p=evaluateFrozen(a,{certifyFloor:false}),q=independent.frozenGraph(b);
  for(let f=0;f<2;f++)assert.deepEqual(p.worldPolicies[f],q.worldPolicies[f]);
  for(const [name,array] of [['successorSha256',q.successor],['cycleLabelSha256',q.labels],['transientDistanceSha256',q.distance]]){
   assert.equal(p.graph[name],createHash('sha256').update(independent.canonicalBytes(array,'u32')).digest('hex'));
  }
  assert.equal(p.graph.cycles.length,q.cycles.length);
  for(let i=0;i<q.cycles.length;i++){
   const x=p.graph.cycles[i],y=q.cycles[i];
   assert.deepEqual(x.nodes,y.nodes);assert.equal(x.basinStates,y.basinStates);
   for(const [v,w] of [[x.metrics.consumerSurplus,y.metrics.consumerSurplus],[x.metrics.profits.A,y.metrics.profitA],[x.metrics.profits.B,y.metrics.profitB],[x.metrics.prices.A,y.metrics.priceA],[x.metrics.prices.B,y.metrics.priceB]])assert.deepEqual(pair(v),pair(w));
   assert.deepEqual(x.trainingSupport,y.trainingSupport);
  }
  assert.equal(p.graph.actualTerminal.startNode,q.actualTerminal.startNode);
  assert.deepEqual(p.graph.actualTerminal.transientNodes,q.actualTerminal.transientNodes);
  assert.deepEqual(p.graph.actualTerminal.cycleNodesFromStart,q.actualTerminal.cycleNodesFromStart);
 }
});

test('paired arms are identical before the first repeated cap and activation Q/counts remain identical forever',()=>{
 const finite=artificial(),a=primary.createLearners(finite,'startup',{seed:907012,T:240}),b=primary.createLearners(finite,'recurring4',{seed:907012,T:240});
 primary.advanceTo(a,4);primary.advanceTo(b,4);
 for(let f=0;f<2;f++){
  assert.deepEqual(primary.f64Bytes(a.q[f]),primary.f64Bytes(b.q[f]));
  assert.deepEqual(primary.u32Bytes(a.counts[f]),primary.u32Bytes(b.counts[f]));
 }
 assert.deepEqual(a.previous,b.previous);assert.deepEqual(a.actors,b.actors);assert.equal(a.phase,4);
 primary.advanceTo(a,240);primary.advanceTo(b,240);
 const activationCells=finite.prices.length**3;
 for(let f=0;f<2;f++){
  assert.deepEqual(primary.f64Bytes(a.q[f].subarray(0,activationCells)),primary.f64Bytes(b.q[f].subarray(0,activationCells)));
  assert.deepEqual(primary.u32Bytes(a.counts[f].subarray(0,activationCells)),primary.u32Bytes(b.counts[f].subarray(0,activationCells)));
  assert.equal(a.counts[f].subarray(0,activationCells).reduce((s,c)=>s+c,0),1);
 }
});
