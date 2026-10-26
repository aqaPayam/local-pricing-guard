import test from 'node:test';import assert from 'node:assert/strict';
import {createProfitChallenge} from '../research/incentive-game.js';
import {certifyCycle} from '../research/recurring-game.js';
const r=(n,d=1)=>({numerator:String(n),denominator:String(d)});
function fixture(){const game={prices:[1,2,3],capIndex:1,sets:[[0,1],[0,1,2],[1,2]],rewards:{consumerSurplus:[10,9,8,9,8,7,8,7,6],profitA:[5,4,3,6,5,7,7,6,3],profitB:[100,101,102,110,111,112,120,121,122],quantityA:Array(9).fill(1),quantityB:Array(9).fill(1)}};game.certificates=[certifyCycle(game,2),certifyCycle(game,1)];return {finite:game,originalTargets:[]};}
const strategy=(focal=0)=>({period:2,focal,discount:r(19,20),optimalBlockProfit:focal?r(4538,20):r(233,20),baselineBlockProfit:focal?r(4538,20):r(157,20),capAction:1,phasePolicies:[{phase:1,actions:Array.from({length:9},(_,s)=>focal?(s%3===0?1:2):1)}]});
test('first cap really executes, script uses previous own price, complete-block score is exact',()=>{
 const game=createProfitChallenge(fixture(),strategy());let s=game.snapshot();assert.equal(s.game.executions,0);assert.equal(s.game.averages,null);assert.equal(s.discountedProfit.value,0);assert.equal(s.shortfall,null);assert.equal(game.opponentQuote(),1);
 assert.equal(game.hint(),1);s=game.execute(1);assert.equal(s.game.latest.type,'cap');assert.equal(s.game.executions,1);assert.equal(game.opponentQuote(),2);assert.equal(s.shortfall,null);assert.equal(game.hint(),1);
 s=game.execute(1);assert.equal(s.complete,true);assert.deepEqual(s.discountedProfit.exact,r(233,20));assert.equal(s.shortfall.matched,true);assert.equal(s.versusBaseline.sign,'positive');assert.equal(s.game.protectedBuffer.nonnegative,true);assert.equal(game.opponentQuote(),null);assert.deepEqual(game.allowed(),[]);assert.throws(()=>game.execute(1),/complete/);
});
test('seller B uses physical reward coordinates and undo restores exact discount/phase state',()=>{
 const game=createProfitChallenge(fixture(),strategy(1));game.execute(0);assert.equal(game.opponentQuote(),1);assert.equal(game.hint(),2);let s=game.execute(1);assert.deepEqual(s.game.latest.indices,[1,1]);assert.deepEqual(s.discountedProfit.exact,r(4309,20));assert.equal(s.shortfall.matched,false);assert.equal(s.versusBaseline.sign,'negative');
 s=game.undo();assert.equal(s.game.executions,1);assert.deepEqual(s.discountedProfit.exact,r(110));assert.equal(s.complete,false);s=game.execute(2);assert.deepEqual(s.discountedProfit.exact,r(1082,5));s=game.reset();assert.equal(s.game.executions,0);assert.equal(s.canUndo,false);assert.equal(s.discountedProfit.value,0);
});
test('illegal choices/invalid hints do not advance; K1 has no fictitious future reward',()=>{
 const record=fixture(),game=createProfitChallenge(record,strategy());assert.throws(()=>game.execute(2));assert.equal(game.snapshot().game.executions,0);
 const bad=strategy();bad.phasePolicies[0].actions.fill(99);assert.throws(()=>createProfitChallenge(record,bad),/not permitted/);
 const one=createProfitChallenge(record,{period:1,focal:0,discount:r(19,20),optimalBlockProfit:r(5),baselineBlockProfit:r(5),capAction:1,phasePolicies:[]});const s=one.execute(1);assert.equal(s.complete,true);assert.equal(s.game.capExecutions,1);assert.equal(s.discountedProfit.value,5);assert.equal(s.shortfall.matched,true);
});
test('inconsistent complete-block evidence rejects the action atomically',()=>{const bad=strategy();bad.optimalBlockProfit=r(8);const game=createProfitChallenge(fixture(),bad);game.execute(1);const before=game.snapshot();assert.throws(()=>game.execute(1),/exceeds its certificate/);assert.deepEqual(game.snapshot(),before);assert.equal(game.snapshot().canUndo,true);game.undo();assert.equal(game.snapshot().game.executions,0);});
