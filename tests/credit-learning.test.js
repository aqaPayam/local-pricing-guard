import test from 'node:test';import assert from 'node:assert/strict';
import {createMarket,cloneMarket,train,advance} from '../research/learning-market.js';
import {creditAdvance,creditTrain,ARMS} from '../research/credit-learning.js';
test('proposal extension is exact original training parity for none, guard and cap',()=>{
 for(const treatment of [{},{type:'guard',epsilon:.1},{type:'cap'}]){
  const a=createMarket({seed:19}),b=cloneMarket(a);train(a,2000,{treatment});creditAdvance(b,2000,{treatment});
  assert.deepEqual(b,a);
 }
});
test('original adaptive evaluation and extension have matching settlements and Q values',()=>{
 for(const treatment of [{},{type:'guard',epsilon:.1},{type:'cap'}]){
  const a=createMarket({seed:21}),b=cloneMarket(a);const ra=advance(a,200,{treatment,explorationRate:.01}),rb=creditAdvance(b,200,{treatment,explorationRate:.01});
  assert.deepEqual(b,a);assert.equal(ra.metrics.consumerSurplus,rb.metrics.consumerSurplus);assert.ok(Math.abs(1-ra.metrics.interventions-rb.metrics.retention)<1e-14);
 }
});
test('feasible-aware choice retains every proposal including exploration',()=>{
 for(const arm of ARMS.filter(a=>a.mode==='aware')){
  const m=createMarket({seed:18}),r=creditAdvance(m,300,{...arm,explorationRate:1,traceEvery:1});
  assert.equal(r.metrics.retention,1);assert.ok(r.rows.every(x=>x.actions.every((a,f)=>a===x.executed[f])));
 }
});
test('executed credit indexes execution and exact temporal difference math',()=>{
 const m=createMarket({seed:18});const r=creditAdvance(m,100,{mode:'executed',treatment:{type:'guard',epsilon:.1},explorationRate:1,traceEvery:1});
 let changed=0;for(const row of r.rows)for(let f=0;f<2;f++){
  const u=row.updates[f];assert.equal(u.credited,row.executed[f]);assert.equal(u.index,row.states[f]*15+row.executed[f]);assert.equal(u.newQ,u.oldQ+u.alpha*(u.target-u.oldQ));if(row.actions[f]!==row.executed[f])changed++;
 }assert.ok(changed>0);
});
test('frozen evaluations preserve Q; no treatment makes all three interfaces identical',()=>{
 const a=createMarket({seed:26}),b=cloneMarket(a),c=cloneMarket(a);const before=a.q.map(x=>Array.from(x));
 creditAdvance(a,100,{learn:false,mode:'proposal',explorationRate:.05});creditAdvance(b,100,{learn:false,mode:'executed',explorationRate:.05});creditAdvance(c,100,{learn:false,mode:'aware',explorationRate:.05});
 assert.deepEqual(a,b);assert.deepEqual(a,c);assert.deepEqual(a.q.map(x=>Array.from(x)),before);
});
test('fast training matches audited step path for every interface and all arms',()=>{
 for(const arm of ARMS){const a=createMarket({seed:31}),b=cloneMarket(a);creditAdvance(a,500,arm);creditTrain(b,500,arm);assert.deepEqual(a,b);}
});
