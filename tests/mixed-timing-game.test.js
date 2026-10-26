import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {createTimingGame} from '../research/mixed-timing-game.js';
import {rational,exactJSON,fromJSON,compare} from '../research/recurring-game.js';
const q=(n,d=1)=>exactJSON(rational(BigInt(n),BigInt(d)));
function fixture(F=1.5){
 const record={scenario:{id:'artificial'},cap:{index:0,price:0},originalTargets:[{label:'toy',actualGuaranteedThreshold:F}],finite:{prices:[0,1,2],sets:[[0,1],[1,2],[2]],upper:[1,2,2],capIndex:0,rewards:{consumerSurplus:[3,2,1.5,2,1,.5,1.5,.5,0],profitA:Array.from({length:9},(_,i)=>i+1),profitB:Array.from({length:9},(_,i)=>20-i),quantityA:Array(9).fill(0),quantityB:Array(9).fill(0)}}};
 const target={label:'toy',scenario:'artificial',kind:'finite',actualThresholdExact:q(3,2),frontier:{bestFixedK:2,certifiedSafeK:2},calendar:{kind:'funded-mixed',K:2,startupCaps:1,creditAExact:q(1),creditBExact:q(-1,2),creditUpperExclusiveExact:q(3,2)},rates:{exactOptimum:true,constructedRateExact:q(3,8),optimumRateBoundsExact:{lower:q(3,8),upper:q(3,8)}}};
 return {record,target};
}
test('pending cap, actual executed reward, funded long gap, and partial ledger are different',()=>{
 const {record,target}=fixture(),g=createTimingGame(record,target);let s=g.snapshot();
 assert.equal(s.latest,null);assert.equal(s.averages,null);assert.equal(s.executions,0);assert.equal(s.nextIsCap,true);assert.deepEqual(s.previousIndices,[2,2]);
 assert.deepEqual(s.timing.firstLong,{initialShortBlocks:'1',block:'2',execution:'3'});
 s=g.execute(0,0);assert.equal(s.latest.consumerSurplus,3);assert.equal(s.actualExcess.value,1.5);assert.equal(s.boundaryCredit.value,0);assert.equal(s.guaranteedBuffer.value,1.5);assert.equal(s.nextIsCap,false);
 s=g.execute(1,1);assert.equal(s.boundaryCredit.value,1);assert.equal(s.chosenGapLength,3);assert.equal(s.nextIsCap,true);
 s=g.execute(0,0);assert.equal(s.latest.type,'cap');assert.equal(s.boundaryCredit.value,1);assert.equal(s.guaranteedBuffer.value,2.5);
 s=g.execute(1,1);s=g.execute(2,2);assert.equal(s.boundaryCredit.value,.5);assert.equal(s.guaranteedBuffer.value,.5);assert.equal(s.actualExcess.value,.5);
});
test('equality funding tie chooses long; cooperative reward does not buy a different calendar',()=>{
 const {record,target}=fixture(),top=createTimingGame(record,target),low=createTimingGame(record,target);
 for(let t=0;t<40;t++){
  top.execute(top.allowed(0).at(-1),top.allowed(1).at(-1));low.execute(low.allowed(0)[0],low.allowed(1)[0]);
  const a=top.snapshot(),b=low.snapshot();assert.equal(a.nextIsCap,b.nextIsCap);assert.equal(a.chosenGapLength,b.chosenGapLength);assert.deepEqual(a.boundaryCredit.exact,b.boundaryCredit.exact);
  assert.ok(compare(fromJSON(b.actualExcess.exact),fromJSON(b.guaranteedBuffer.exact))>=0);
  if(t===4)assert.equal(a.chosenGapLength,3); // B=.5 equals -b
 }
});
test('lagged sets, deliberate asymmetric choices, undo and reset preserve exact state',()=>{
 const {record,target}=fixture(),g=createTimingGame(record,target);g.execute(0,0);const before=g.snapshot();
 assert.equal(g.preview(1,0).legal,true);assert.deepEqual(g.allowed(1),[0,1]);
 const after=g.execute(1,0);assert.deepEqual(after.latest.indices,[1,0]);assert.deepEqual(after.latest.profits,[4,17]);
 assert.deepEqual(g.undo(),before);assert.deepEqual(g.allowed(0),[0,1]);
 assert.throws(()=>g.execute(2,0),/permitted/);assert.deepEqual(g.snapshot(),before);
 g.reset();assert.equal(g.snapshot().latest,null);assert.equal(g.ledger().length,0);assert.equal(g.snapshot().canUndo,false);
});
test('fixed own comparator, startup-only, zero mixing, fallback and unavailable stay distinct',()=>{
 let {record,target}=fixture();const fixed=createTimingGame(record,target,{mode:'fixed'});for(let t=0;t<10;t++)fixed.execute(fixed.allowed(0).at(-1),fixed.allowed(1).at(-1));
 assert.equal(fixed.snapshot().capExecutions,5);assert.equal(fixed.snapshot().timing.plannedRate.value,.5);
 ({record,target}=fixture(0));target.actualThresholdExact=q(0);target.calendar={kind:'startup-only',startupCaps:1};target.frontier={bestFixedK:null,certifiedSafeK:null};
 const startup=createTimingGame(record,target);for(let t=0;t<20;t++)startup.execute(startup.allowed(0).at(-1),startup.allowed(1).at(-1));
 assert.equal(startup.snapshot().capExecutions,1);assert.equal(startup.snapshot().nextIsCap,false);assert.equal(startup.snapshot().timing.plannedRate.value,0);assert.throws(()=>createTimingGame(record,target,{mode:'fixed'}),/No finite/);
 ({record,target}=fixture(2));target.actualThresholdExact=q(2);target.calendar.creditAExact=q(0);target.calendar.creditBExact=q(-2);target.calendar.creditUpperExclusiveExact=q(2);target.rates.constructedRateExact=q(1,2);target.rates.optimumRateBoundsExact={lower:q(1,2),upper:q(1,2)};
 const equal=createTimingGame(record,target);assert.equal(equal.snapshot().timing.firstLong,null);for(let t=0;t<10;t++)equal.execute(equal.allowed(0).at(-1),equal.allowed(1).at(-1));assert.equal(equal.snapshot().capExecutions,5);
 ({record,target}=fixture());target.calendar.kind='fixed-safe';target.frontier.bestFixedK=null;const fallback=createTimingGame(record,target);assert.equal(fallback.snapshot().timing.bestFixedK,null);assert.equal(fallback.snapshot().timing.kind,'fixed-safe');
 target.calendar.kind='unavailable';assert.throws(()=>createTimingGame(record,target),/No certified/);
});
test('malformed identities/masks/credits/rates and prospective contradictory reward reject atomically',()=>{
 for(const mutate of [x=>x.record.cap.price=1,x=>x.record.finite.sets[0]=[1,0],x=>x.target.actualThresholdExact=q(1),x=>x.target.calendar.creditAExact=q(2),x=>x.target.rates.constructedRateExact=q(1)]){
  const f=fixture();mutate(f);assert.throws(()=>createTimingGame(f.record,f.target));
 }
 const {record,target}=fixture(),g=createTimingGame(record,target),before=g.snapshot();record.finite.rewards.consumerSurplus[0]=-100;
 assert.throws(()=>g.execute(0,0),/no round was executed/);assert.deepEqual(g.snapshot(),before);
});
test('all forty accepted finite target slots lock honestly or replay primary exact upper-path certificates',()=>{
 const results=JSON.parse(fs.readFileSync(new URL('../research/mixed-timing-results/results.json',import.meta.url),'utf8'));
 const display=JSON.parse(fs.readFileSync(new URL('../research/mixed-timing-results/web-data.json',import.meta.url),'utf8'));
 let slots=0,playable=0,locked=0,transitions=0;
 for(const model of results.records.filter(r=>r.kind==='finite')){
  const record=JSON.parse(fs.readFileSync(new URL('../'+model.finiteFile,import.meta.url),'utf8'));
  for(const target of model.targets){slots++;
   if(target.calendar.kind==='unavailable'){assert.throws(()=>createTimingGame(record,target));locked++;continue;}
   const g=createTimingGame(record,target);playable++;
   const timing=display.models.find(m=>m.id===model.id).targets.find(t=>t.id===target.id).constructedCalendarTiming;
   assert.equal(g.snapshot().timing.firstLong?.execution??null,timing?.firstLongExecution??null);
   for(const expected of target.executionPreview){
    const s=g.execute(g.allowed(0).at(-1),g.allowed(1).at(-1));transitions++;
    assert.equal(s.latest.type,expected.mode);assert.deepEqual(s.latest.indices,expected.executedIndices);
    assert.deepEqual(s.guaranteedBuffer.exact,expected.cumulativePrefixExcessBounds.lowerExact);
    assert.deepEqual(s.boundaryCredit.exact,expected.boundaryCreditAfterExact);
    assert.deepEqual(s.actualExcess.exact,s.guaranteedBuffer.exact);
   }
  }
 }
 assert.equal(slots,40);assert.ok(playable>0);assert.equal(playable+locked,40);assert.ok(transitions>1000);
});
