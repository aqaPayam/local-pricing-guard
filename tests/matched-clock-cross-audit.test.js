// Artificial interoperability only; production replay imports no primary helper.
import test from 'node:test';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import * as P from '../research/matched-clock-learning.js';
import * as A from '../research/audit-matched-clock.js';
import {evaluateFrozen} from '../research/matched-clock-graph.js';
const game=()=>({prices:[1,2,3],capIndex:0,sets:[[0,2],[1],[0,1]],rewards:{profitA:[0,-2,4,7,0,-1,3,2,1],profitB:[9,8,7,6,5,4,3,2,1],consumerSurplus:[18,17,16,15,14,13,12,11,10]}});
function compare(a,p){
  assert.equal(a.t,p.t);assert.equal(a.phase,p.phase);assert.equal(a.caps,p.caps);assert.deepEqual(a.previous,p.previous);assert.deepEqual(a.rng,p.actors);
  for(let f=0;f<2;f++){
    assert.ok(A.canonicalBytes(a.q[f],'f64').equals(P.f64Bytes(p.q[f])),'Every dense Q bit, including forbidden cells');
    assert.ok(A.canonicalBytes(a.counts[f],'u32').equals(P.u32Bytes(p.counts[f])),'Every uint32 count');
  }
  assert.deepEqual(a.transcript.blocks,p.transcriptBlocks);
  assert.equal(a.transcript.snapshot().pendingSha256,createHash('sha256').update(p.transcriptBuffer.subarray(0,p.transcriptRounds*120)).digest('hex'));
  assert.deepEqual(a.learningBlocks,p.learningBlocks);assert.deepEqual(a.pendingLearningBlock,p.blockSummary);
  for(let i=0;i<2;i++){
    const x=a.windows[i],y=p.windows[i];assert.equal(x.start,y.startStep);assert.equal(x.end,y.endStep);assert.equal(x.rounds,y.rounds);
    assert.deepEqual([...x.transitions],[...y.transitions]);assert.deepEqual(x.maxAllowed,y.maxAllowed);assert.deepEqual(x.explorationDecisions,y.explorations);
    assert.deepEqual(x.priceChanges,y.priceChanges);assert.equal(x.caps,y.capExecutions);
  }
  A.assertForbiddenZero(a);
}
test('separate primary cached kernel and independent direct scanner agree at all artificial checkpoints and transcript blocks',()=>{
  assert.deepEqual(P.actorNamespaces(),A.initialActors());
  for(const arm of ['startup','recurring4'])for(const seed of [907001,907012]){
    const a=A.createReplay(game(),arm,{seed,T:30000}),p=P.createLearners(game(),arm,{seed,T:30000});
    for(const end of [1,4,5,9,10000,15000,20000,30000]){A.replayTo(a,end);P.advanceTo(p,end);compare(a,p);}
  }
});
test('independent DataView transcript encoder matches primary Buffer encoder on a literal signed/endian fixture',()=>{
  const w={round:0x01020304,phase:4,previous:[61,2],actions:[3,5],explored:[false,true],epsilon:.125,rewards:[-1,2],oldQ:[-0,4],nextMax:[5,6],newQ:[7,8],actorsAfter:[[1,2,0xffffffff,4],[5,6,7,0xabcdef01]]};
  const independent=A.encodeTranscriptRound({step:w.round,phase:w.phase,previous:w.previous,actions:w.actions,exploreFlags:2,epsilon:w.epsilon,expectedProfits:w.rewards,priorQ:w.oldQ,nextMaxima:w.nextMax,newQ:w.newQ,rngAfter:w.actorsAfter});
  const primary=P.encodeRound(w);assert.ok(independent.equals(primary));assert.equal(createHash('sha256').update(primary).digest('hex'),'8f92dc34877d01c629c68bdc7bd63cfe27b0e600ce354fcfd83054ee03dfd676');
});

test('complete independent graph claim matches ALL floor/target/geometry/support/preview fields, including an unreachable bad cycle',()=>{
  const raw={finite:{prices:[1,2,3],capIndex:0,sets:[[0],[0,1],[1,2]],upper:[0,1,2],rewards:{profitA:Array(9).fill(0),profitB:[0,1,2,3,4,5,6,7,8],consumerSurplus:[9,8,7,8,7,6,7,6,5]}},originalTargets:[{label:'artificial95',requestedTarget:9,actualGuaranteedThreshold:8.55,numericalMargin:.45}]};
  for(const arm of ['startup','recurring4']){
    const a=A.createReplay(raw.finite,arm,{T:24}),p=P.createLearners(raw,arm,{T:24});A.replayTo(a,24);P.advanceTo(p,24);
    assert.deepEqual(A.expectedGraphClaim(a,{originalTargets:raw.originalTargets}),evaluateFrozen(p).graph);
    if(arm==='startup'){
      for(let f=0;f<2;f++)for(let phase=1;phase<5;phase++)for(let own=0;own<3;own++){
        const cell=A.rowStart(a,phase,own,2)+2;a.q[f][cell]=10;p.q[f][cell]=10;
      }
      P.rebuildMaxima(p);const independent=A.expectedGraphClaim(a,{originalTargets:raw.originalTargets});
      assert.deepEqual(independent,evaluateFrozen(p).graph);assert.ok(independent.cycles.some(c=>c.floorApplies===false&&BigInt(c.floorGap.numerator)<0n));
    }
  }
});
