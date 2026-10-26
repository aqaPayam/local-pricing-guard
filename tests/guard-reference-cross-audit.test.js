// Cross-author API interoperability on invented games only.
import test from 'node:test';
import assert from 'node:assert/strict';
import {createGuardReferenceLearners,evaluateGuardReference,summarizeGuardReferenceWindows} from '../research/guard-reference-learning.js';
import {advanceTo,f64Bytes,u32Bytes} from '../research/matched-clock-learning.js';
import {createReferenceReplay,expectedReferenceGraph,expectedReferenceWindows,validateReferenceReplay} from '../research/audit-guard-reference.js';
import {replayTo,canonicalBytes} from '../research/audit-matched-clock.js';

const fixture=zero=>{
 const n=5;
 return {scenario:{id:'invented-cross-reference'},originalTargets:[],finite:{prices:[-1,0,1,2,3],capIndex:1,
  sets:Array.from({length:n},(_,r)=>[r]),rewards:{
   profitA:Array.from({length:n*n},(_,i)=>zero?0:(Math.floor(i/n)-2*(i%n))/8),
   profitB:Array.from({length:n*n},(_,i)=>zero?0:(3*(i%n)-Math.floor(i/n))/16),
   consumerSurplus:Array.from({length:n*n},(_,i)=>zero?0:40-i/32)}}};
};

test('full-support cached learner and independent effective-view replay match all bits/blocks/graphs/windows',()=>{
 for(const zero of [false,true])for(const mode of ['full-grid-after-cap','startup-guard']){
  const original=fixture(zero),before=structuredClone(original);
  const primary=createGuardReferenceLearners(original,{treatment:mode,T:20000,seed:907012});
  const audit=createReferenceReplay(original,{mode,T:20000,seed:907012});
  for(const end of [10000,20000]){
   advanceTo(primary,end);replayTo(audit,end);validateReferenceReplay(audit);
   for(let f=0;f<2;f++){
    assert.deepEqual(f64Bytes(primary.q[f]),canonicalBytes(audit.q[f],'f64'));
    assert.deepEqual(u32Bytes(primary.counts[f]),canonicalBytes(audit.counts[f],'u32'));
   }
   assert.deepEqual(primary.actors,audit.rng);assert.deepEqual(primary.previous,audit.previous);assert.equal(primary.phase,audit.phase);assert.equal(primary.caps,audit.caps);
   assert.deepEqual(primary.transcriptBlocks,audit.transcript.snapshot().blocks);
   const p=evaluateGuardReference(primary),q=expectedReferenceGraph(audit);
   assert.deepEqual(p.graph,q);
   assert.deepEqual(summarizeGuardReferenceWindows(primary),expectedReferenceWindows(audit));
   assert.deepEqual(primary.scientificTreatment,audit.scientificTreatment);assert.deepEqual(primary.supportTreatment,audit.supportTreatment);
  }
  assert.deepEqual(original,before);
 }
});
