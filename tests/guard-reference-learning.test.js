import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createLearners,step,advanceTo,modelIdentity,rebuildMaxima,f64Bytes,u32Bytes} from '../research/matched-clock-learning.js';
import {evaluateFrozen,summarizeWindows} from '../research/matched-clock-graph.js';
import {createGuardReferenceLearners,validateGuardReference,evaluateGuardReference,summarizeGuardReferenceWindows,FULL_GRID_TREATMENT,GUARDED_PARITY_TREATMENT} from '../research/guard-reference-learning.js';
import {writeReferenceCheckpoint,validateReferenceDensePair} from '../research/guard-reference-io.js';
import {readRef,readDense} from '../research/matched-clock-io.js';
const actors=[[11,22,33,44],[55,66,77,88]];
const toy=()=>({scenario:{id:'wholly-artificial-reference'},originalTargets:[],finite:{prices:[1,2,3],capIndex:1,sets:[[0],[0,1],[1]],rewards:{profitA:[-2,0,1,3,-1,2,0,1,0],profitB:[1,-3,0,0,2,-1,4,0,1],consumerSurplus:[9,8,7,8,6,5,7,5,3]}}});
const options={T:20000,actorStates:actors};

test('old-arm adapter parity preserves all arithmetic, windows, actor states and complete transcript blocks',()=>{
 const original=toy(),before=JSON.stringify(original),old=createLearners(original,'startup',options),adapted=createGuardReferenceLearners(original,{...options,treatment:GUARDED_PARITY_TREATMENT});
 advanceTo(old,20000);advanceTo(adapted,20000);
 assert.deepEqual(modelIdentity(adapted),modelIdentity(old));
 assert.deepEqual(summarizeGuardReferenceWindows(adapted),summarizeWindows(old));
 const a=evaluateGuardReference(adapted),b=evaluateFrozen(old,{certifyFloor:false});
 assert.deepEqual(a.policies,b.policies);assert.deepEqual(a.worldPolicies,b.worldPolicies);
 delete a.graph.supportTreatment;delete a.graph.scientificTreatment;a.graph.scope=b.graph.scope;assert.deepEqual(a.graph,b.graph);
 assert.equal(JSON.stringify(original),before);assert.equal(adapted.phase,4);assert.equal(adapted.caps,1);
});

test('full supports are independent allocations after phase0 and preserve original physical record',()=>{
 const original=toy(),before=JSON.stringify(original),m=createGuardReferenceLearners(original,options);
 assert.equal(m.record,original);assert.equal(m.finite,original.finite);assert.equal(m.arm,'startup');
 for(let p=0;p<5;p++)for(let r=0;r<3;r++)assert.deepEqual(m.supports[p][r],p===0?[0,1]:[0,1,2]);
 assert.notEqual(m.supports[1][0],m.supports[1][1]);assert.notEqual(m.supports[1][0],m.supports[2][0]);
 assert.equal(m.supportTreatment.treatment,FULL_GRID_TREATMENT);validateGuardReference(m);
 m.supports[1][0].pop();assert.throws(()=>validateGuardReference(m),/Effective supports/);
 assert.equal(JSON.stringify(original),before);
});

test('full-grid adapter matches unchanged startup kernel on an independently constructed full-support artificial view',()=>{
 const original=toy(),full=structuredClone(original);full.finite.sets=Array.from({length:3},()=>[0,1,2]);
 const a=createGuardReferenceLearners(original,options),b=createLearners(full,'startup',options),seen=new Set();
 for(let t=0;t<20000;t++){
  const x=step(a,{trace:true}),y=step(b,{trace:true});assert.deepEqual(x,y);
  assert.equal(x.rewards[1],original.finite.rewards.profitB[x.actions[0]*3+x.actions[1]]);
  if(x.phase>0)for(const quote of x.actions)seen.add(quote);
 }
 assert.deepEqual([...seen].sort(),[0,1,2]);assert.deepEqual(modelIdentity(a),modelIdentity(b));validateGuardReference(a);
 assert.equal(a.caps,1);assert.equal(a.phase,4);assert.deepEqual(a.actors,b.actors);
});

test('full-grid next-mask maxima, smallest-index ties and sealed B WORLD rewards use the intended supports',()=>{
 const m=createGuardReferenceLearners(toy(),{T:12,alpha:1,gamma:.5,actorStates:actors});
 // An artificial state isolates bootstrap support: original guard forbids quote2.
 m.t=3;m.phase=3;m.previous=[0,1];m.caps=1;
 const row=(p,a,b)=>(p*3+a)*3+b;
 for(let f=0;f<2;f++)for(let r=0;r<m.rows;r++)for(const a of m.supports[Math.floor(r/9)][r%3])m.q[f][r*3+a]=-10;
 // Tie at zero over full support resolves to original index0.
 m.q[0].fill(0);m.q[1].fill(0);rebuildMaxima(m);assert.equal(m.best[0][row(3,0,1)],0);
 // Force exploitation with a valid actor whose next first word exceeds epsilon.
 const noExplore=[0,0xffffffff,0,1];m.actors=[noExplore.slice(),noExplore.slice()];
 m.T=4; // Last declared round: epsilon=.01, no actor reset by production code.
 m.q[0][row(3,0,1)*3+2]=10;m.q[1][row(3,1,0)*3+1]=10;
 m.q[0][row(4,2,1)*3+2]=9;m.q[1][row(4,1,2)*3+2]=7;rebuildMaxima(m);
 const w=step(m,{trace:true});assert.deepEqual(w.actions,[2,1]);assert.deepEqual(w.nextMax,[9,7]);
 assert.deepEqual(w.rewards,[1,0]);assert.deepEqual(w.newQ,[1+.5*9,0+.5*7]);
 assert.equal(m.q[1][row(3,1,0)*3+1],3.5);assert.equal(m.phase,4);
});

test('full-support frozen graph and exact windows use effective masks without importing an old floor',()=>{
 const m=createGuardReferenceLearners(toy(),options);advanceTo(m,20000);
 const out=evaluateGuardReference(m);assert.equal(out.graph.floor,null);assert.equal(out.graph.supportTreatment.treatment,FULL_GRID_TREATMENT);
 assert.equal(out.graph.actualTerminal.start.phase,4);
 for(const cycle of out.graph.cycles){assert.equal(cycle.floorApplies,null);assert.equal(cycle.floorGap,null);assert.equal(cycle.metrics.maskCount.A.numerator,'3');assert.equal(cycle.metrics.maskCount.B.numerator,'3');}
 for(const w of summarizeGuardReferenceWindows(m))assert.ok(Number(w.metrics.maskCount.A.approximate)>2.9);
 assert.ok(out.graph.terminalPreview128.every(w=>!w.cap));
});

test('new transport binds treatment and roundtrips full-grid cells forbidden by original guard',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'guard-reference-artificial-'));
 try{
  const m=createGuardReferenceLearners(toy(),options);advanceTo(m,20000);const graph=evaluateGuardReference(m),windowMetrics=summarizeGuardReferenceWindows(m);
  const ref=writeReferenceCheckpoint(temp,m,{id:'artificial-full-grid',software:{scope:'artificial'},finiteGameRef:{file:'artificial-only.json',bytes:0,sha256:'0'.repeat(64)},graph,windowMetrics});
  const meta=JSON.parse(readRef(temp,ref));assert.equal(meta.treatment,FULL_GRID_TREATMENT);assert.deepEqual(meta.supportTreatment,m.supportTreatment);
  assert.deepEqual(meta.scientificTreatment,{capClock:'startup',supportMode:FULL_GRID_TREATMENT,initialCap:true,postInitialOriginalIndices:'all'});
  const q=meta.artifacts.q.map(r=>readDense(temp,r,3,'f64le')),counts=meta.artifacts.counts.map(r=>readDense(temp,r,3,'u32le'));
  validateReferenceDensePair(q,counts,m.finite,meta.treatment,m.t);assert.deepEqual(q,m.q.map(f64Bytes));assert.deepEqual(counts,m.counts.map(u32Bytes));
  const poison=q.map(Buffer.from);poison[0].writeDoubleLE(-0,2*8);assert.throws(()=>validateReferenceDensePair(poison,counts,m.finite,meta.treatment,m.t),/phase0/);
  assert.throws(()=>validateReferenceDensePair(q,counts,m.finite,'startup-guard',m.t),/explicitly/);
  assert.throws(()=>writeReferenceCheckpoint(temp,m,{id:'artificial-full-grid',software:{},finiteGameRef:{},graph,windowMetrics}),/EEXIST/);
  assert.throws(()=>writeReferenceCheckpoint(temp,m,{id:'../escape',software:{},finiteGameRef:{},graph,windowMetrics}),/identity/);
  const falseFloor=structuredClone(graph);falseFloor.graph.cycles[0].floorApplies=true;
  assert.throws(()=>writeReferenceCheckpoint(temp,m,{id:'false-floor',software:{},finiteGameRef:{},graph:falseFloor,windowMetrics}),/guard-floor/);
  const wrongClock=structuredClone(graph);wrongClock.graph.step--;
  assert.throws(()=>writeReferenceCheckpoint(temp,m,{id:'stale-graph',software:{},finiteGameRef:{},graph:wrongClock,windowMetrics}),/clock/);
 }finally{
  const resolved=path.resolve(temp),parent=path.resolve(os.tmpdir());
  assert.ok(resolved.startsWith(parent+path.sep)&&path.basename(resolved).startsWith('guard-reference-artificial-'),'Cleanup target must stay inside the explicitly named artificial temp directory');
  fs.rmSync(resolved,{recursive:true,force:true});
 }
});
