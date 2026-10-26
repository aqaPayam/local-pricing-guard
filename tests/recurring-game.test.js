import test from 'node:test';import assert from 'node:assert/strict';
import {rational,add,compare,fromDouble,lowerDouble,nextUp,certifyCycle,createGame,exactJSON} from '../research/recurring-game.js';
function fixture({sets=[[0,1],[1,2],[2]],capIndex=0,K=3}={}){
 const prices=[1,2,3],consumerSurplus=prices.flatMap((_,i)=>prices.map((_,j)=>20-i-j)),rewards={consumerSurplus,profitA:new Array(9).fill(2),profitB:new Array(9).fill(3),quantityA:new Array(9).fill(4),quantityB:new Array(9).fill(5)};
 const finite={prices,sets,capIndex,rewards};finite.certificates=[certifyCycle(finite,K)];return {finite,originalTargets:[{label:'cap-95pct',requestedTarget:18,actualGuaranteedThreshold:18}]};
}
test('binary64 conversion and lower displays respect exact rational boundaries',()=>{
 assert.deepEqual(exactJSON(fromDouble(.1)),{numerator:'3602879701896397',denominator:'36028797018963968'});
 const exact=rational(1,10),lo=lowerDouble(exact);assert(compare(fromDouble(lo),exact)<=0);assert(compare(fromDouble(nextUp(lo)),exact)>0);
 assert(compare(add(fromDouble(.1),fromDouble(.2)),fromDouble(.1+.2))<0);assert.deepEqual(exactJSON(fromDouble(0)),{numerator:'0',denominator:'1'});
 assert.throws(()=>fromDouble(Infinity),/Finite/);
});
test('first cap is a real execution overriding the guard; initial history earns nothing',()=>{
 const r=fixture(),g=createGame(r,3,{previous:[2,2]});let s=g.snapshot();assert.equal(s.executions,0);assert.equal(s.latest,null);assert.equal(s.averages,null);assert.equal(s.benchmark.averageCS,null);assert.equal(s.nextIsCap,true);assert.deepEqual(g.allowed(0),[0]);
 s=g.execute(0,0);assert.equal(s.latest.type,'cap');assert.equal(s.latest.consumerSurplus,20);assert.equal(s.averages.consumerSurplus,20);assert.equal(s.capExecutions,1);assert.equal(s.phase,1);assert.equal(s.movesUntilCap,2);assert.deepEqual(s.latest.quantities,[4,5]);
});
test('lagged rival indexing, phase transitions, undo and reset are real',()=>{
 const g=createGame(fixture(),3);g.execute(0,0);g.execute(0,1);assert.deepEqual(g.allowed(0),[1,2]);assert.deepEqual(g.allowed(1),[0,1]);
 let s=g.execute(2,1);assert.equal(s.phase,0);assert.equal(s.capExecutions,1);assert.deepEqual(g.allowed(0),[0]);s=g.undo();assert.equal(s.executions,2);assert.equal(s.phase,2);assert.deepEqual(s.previousIndices,[0,1]);s=g.reset();assert.equal(s.executions,0);assert.equal(s.canUndo,false);
});
test('bad quotes and malformed display floors do not advance the game',()=>{
 const r=fixture(),g=createGame(r,3);assert.equal(g.preview(2,2).legal,false);assert.throws(()=>g.execute(2,2),/permitted/);assert.equal(g.snapshot().executions,0);
 r.finite.certificates[0].activationFloorLower=100;assert.throws(()=>createGame(r,3),/inflated/);
});
test('full dynamic programming agrees with tight top-path finite horizons',()=>{
 for(const K of [1,2,3,4]){
  const r=fixture({K}),g=createGame(r,K),n=3;let costs=new Map(Array.from({length:9},(_,s)=>[s,0]));
  for(let T=1;T<=10;T++){
   const next=new Map(),phase=(T-1)%K;
   for(const [state,cost] of costs){const i=Math.floor(state/n),j=state%n,as=phase===0?[0]:r.finite.sets[j],bs=phase===0?[0]:r.finite.sets[i];for(const a of as)for(const b of bs){const dest=a*n+b,value=cost+r.finite.rewards.consumerSurplus[dest];next.set(dest,Math.min(next.get(dest)??Infinity,value));}}
   costs=next;const observed=g.execute(Math.max(...g.allowed(0)),Math.max(...g.allowed(1)));assert.equal(observed.benchmark.cumulativeCS,Math.min(...costs.values()));assert(observed.protectedBuffer.nonnegative);assert(observed.averages.consumerSurplus>=observed.floor.value);
  }
 }
});
test('prefix floor handles increasing rewards instead of borrowing descending theorem',()=>{
 const r=fixture({sets:[[0],[0],[1]],capIndex:2,K:3}),c=r.finite.certificates[0];assert.equal(c.descending,false);assert.equal(c.cycleAverageLower,18);assert.equal(c.activationFloorLower,16);assert.equal(c.minimizingPrefix,1);
 const g=createGame(r,3);let s=g.execute(2,2);assert.equal(s.target.certified,false);assert.equal(s.target.buffer,-2);assert.equal(s.protectedBuffer.value,0);s=g.execute(1,1);assert(s.protectedBuffer.nonnegative);
});
test('a low individual round can coexist with a protected finite average',()=>{
 const g=createGame(fixture(),3);g.execute(0,0);g.execute(1,1);const s=g.execute(2,2);assert.equal(s.latest.consumerSurplus,16);assert.equal(s.floor.value,18);assert.equal(s.averages.consumerSurplus,18);assert.equal(s.protectedBuffer.nonnegative,true);assert.equal(s.target.certified,true);
});
