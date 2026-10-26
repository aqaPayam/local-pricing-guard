import test from 'node:test';
import assert from 'node:assert/strict';
import {createLearners,advanceTo,rebuildMaxima,modelIdentity} from '../research/matched-clock-learning.js';
import {evaluateFrozen,summarizeWindows} from '../research/matched-clock-graph.js';
const actorStates=[[11,22,33,44],[55,66,77,88]];
const raw=()=>({scenario:{id:'artificial-only'},originalTargets:[{label:'artificial95',requestedTarget:9,actualGuaranteedThreshold:8.55,numericalMargin:.45}],finite:{prices:[1,2,3],capIndex:0,sets:[[0],[0,1],[1,2]],upper:[0,1,2],rewards:{profitA:Array(9).fill(0),profitB:[0,1,2,3,4,5,6,7,8],consumerSurplus:[9,8,7,8,7,6,7,6,5]}}});
const fraction=v=>Number(v.numerator)/Number(v.denominator);
test('frozen graph is nonmutating, phase0 transient and actual NEXT phase preserved',()=>{
 for(const arm of ['startup','recurring4']){
  const m=createLearners(raw(),arm,{T:24,actorStates});advanceTo(m,24);const identity=modelIdentity(m),out=evaluateFrozen(m);
  assert.deepEqual(modelIdentity(m),identity);assert.equal(out.graph.states,45);assert.equal(out.graph.actualTerminal.start.phase,4);assert.equal(out.graph.terminalPreview128[0].cap,arm==='recurring4');
  assert.equal(out.graph.cycles.reduce((sum,c)=>sum+c.basinStates,0),45);for(const c of out.graph.cycles)assert.equal(c.nodes.some(n=>n<9),false);
  assert.equal(out.graph.actualTerminal.floorApplies,true);assert.equal(out.graph.freshCapCounterfactual.start.phase,0);assert.equal(out.graph.terminalPreview128.length,128);
  assert.equal(m.record.originalTargets[0].label,'artificial95');assert.equal(out.graph.floor.targetComparisons[0].label,'artificial95');assert.equal(fraction(out.graph.floor.targetComparisons[0].actualThreshold),8.55);
 }
});
test('off-cap startup history cycle is retained without transferring cap-first floor or training support',()=>{
 const m=createLearners(raw(),'startup',{T:20,actorStates});advanceTo(m,1);
 for(let f=0;f<2;f++)for(let p=1;p<5;p++)for(let own=0;own<3;own++){const row=(p*3+own)*3+2;m.q[f][row*3+2]=10;}
 rebuildMaxima(m);const out=evaluateFrozen(m),high=out.graph.cycles.find(c=>c.nodes.every(node=>out.worldPolicies[0][node]===2&&out.worldPolicies[1][node]===2));
 assert.ok(high);assert.equal(high.policyCapReachable,false);assert.equal(high.floorApplies,false);assert.equal(fraction(high.metrics.consumerSurplus),5);assert.ok(BigInt(high.floorGap.numerator)<0n);assert.equal(high.trainingSupport.A.unvisitedStates,4);
 assert.equal(out.graph.actualTerminal.floorApplies,true);assert.equal(fraction(out.graph.actualTerminal.cycleMetrics.consumerSurplus),9);
});
test('B greedy lookup is transposed once, while executed rewards remain in world order',()=>{
 const m=createLearners(raw(),'startup',{T:24,actorStates});advanceTo(m,4);
 for(let row=0;row<m.rows;row++){const legal=m.supports[Math.floor(row/9)][row%3];for(const a of legal)m.q[1][row*3+a]=a;}
 rebuildMaxima(m);const out=evaluateFrozen(m);
 for(let node=0;node<m.rows;node++){const p=Math.floor(node/9),a=Math.floor(node/3)%3,b=node%3,other=(p*3+b)*3+a;assert.equal(out.worldPolicies[1][node],out.policies[1][other]);}
 for(const row of out.graph.terminalPreview128){const[a,b]=row.executedIndices;assert.equal(row.profits[1],m.finite.rewards.profitB[a*3+b]);}
 const c=out.graph.actualTerminal.cycleNodesFromStart,expected=c.reduce((s,node)=>s+m.finite.rewards.profitB[out.worldPolicies[0][node]*3+out.worldPolicies[1][node]],0)/c.length;
 assert.equal(fraction(out.graph.actualTerminal.cycleMetrics.profits.B),expected);
});
test('exact training-window means derive from joint transitions and independently reject corrupted counters',()=>{
 const m=createLearners(raw(),'recurring4',{T:24,actorStates});advanceTo(m,12);const summaries=summarizeWindows(m);assert.equal(summaries[0].rounds,12);assert.equal(summaries[1].rounds,12);
 for(const row of summaries){assert.equal(fraction(row.metrics.consumerSurplus),9);assert.equal(fraction(row.metrics.capRuleFrequency),.25);assert.equal(fraction(row.metrics.maskCount.A),1);}
 m.windows[0].maxAllowed[1]--;assert.throws(()=>summarizeWindows(m),/counters/);
});
