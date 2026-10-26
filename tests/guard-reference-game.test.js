import test from 'node:test';
import assert from 'node:assert/strict';
import {createReferenceReplay} from '../research/guard-reference-game.js';
import {referenceFixture,TREATMENTS} from './helpers/guard-reference-web-fixture.js';
import {rational,fromDouble,add,exactJSON} from '../research/recurring-game.js';
const input=seed=>{const d=referenceFixture();return{finiteGame:d.finiteGame,seed,treatments:Object.fromEntries(TREATMENTS.map(t=>[t,d.finalPolicies.find(p=>p.seed===seed&&p.treatment===t)]))};};
test('both treatment histories start unearned at actual phase4 with no new cap; full-grid B is WORLD-indexed once',()=>{
 for(let seed=907001;seed<=907012;seed++){
  const g=createReferenceReplay(input(seed)),start=g.snapshot();assert.equal(start.treatments['startup-guard'].earned,null);assert.equal(start.treatments['full-grid-after-cap'].nextIsCap,false);
  const s=g.advance();assert.deepEqual(s.treatments['startup-guard'].latest.executedIndices,[1,2]);assert.deepEqual(s.treatments['full-grid-after-cap'].latest.executedIndices,[2,2]);assert.equal(s.treatments['startup-guard'].latest.profits[1],.2);
  assert.ok(TREATMENTS.every(t=>s.treatments[t].capExecutions===0));g.undo();assert.deepEqual(g.snapshot(),start);
 }
});
test('exact finite ledgers, paired batches, undo and restart preserve distinct histories independently of caller data',()=>{
 const x=input(907001),g=createReferenceReplay(x),start=g.snapshot(),sums=Object.fromEntries(TREATMENTS.map(t=>[t,rational(0n)]));x.finiteGame.finite.rewards.consumerSurplus.fill(999);
 for(let i=0;i<37;i++){const s=g.advance();for(const t of TREATMENTS){sums[t]=add(sums[t],fromDouble(s.treatments[t].latest.consumerSurplus));assert.deepEqual({...s.treatments[t].earned.customerBenefit.sum,approximate:undefined},{...exactJSON(sums[t]),approximate:undefined});}}
 const end=g.snapshot();g.undo(20);g.advance(20);assert.deepEqual(g.snapshot(),end);g.restart();assert.deepEqual(g.snapshot(),start);
 for(let i=0;i<204;i++)g.advance(20);g.advance(16);assert.equal(g.snapshot().trace.length,60);const limit=g.snapshot();assert.throws(()=>g.advance(),/4096/);assert.deepEqual(g.snapshot(),limit);
});
test('full-grid support is valid everywhere but cannot weaken the guarded panel or phase0, and missing panels lock atomically',()=>{
 const x=input(907001),full=x.treatments['full-grid-after-cap'];assert.doesNotThrow(()=>createReferenceReplay(x));
 const ownGuard=x.treatments['startup-guard'];ownGuard.policies=structuredClone(full.policies);assert.throws(()=>createReferenceReplay(x),/forbidden/);
 const y=input(907001);y.treatments['full-grid-after-cap']={...y.treatments['full-grid-after-cap'],available:false,reason:'Invented missing final',policies:null};const g=createReferenceReplay(y);assert.equal(g.snapshot().finiteBenefitDifference,null);assert.throws(()=>g.advance(),/locked/);
 for(const mutate of [x=>x.treatments['full-grid-after-cap'].scientificTreatment.supportMode='startup-guard',x=>x.treatments['full-grid-after-cap'].start.phase=0,x=>x.treatments['startup-guard'].seed=907002]){const z=input(907001);mutate(z);assert.throws(()=>createReferenceReplay(z));}
});
