import test from 'node:test';import assert from 'node:assert/strict';
import {thresholdFor,classifyBounds,initializerResult,analyzeTarget,targetsFor,analyzeCase} from '../research/handover-init.js';
function fixture({n=3,intervals=null,existingK=1}={}){
 const bounds=intervals||Array.from({length:n*n},(_,state)=>({lower:state<4?10:4,upper:state<4?10:4})),prices=Array.from({length:n},(_,i)=>i+1),scenario={id:'synthetic',economy:{quality:2,cost:1,mu:.25,buyers:100,outsideQuality:0},gridSize:n,toleranceFactor:1,epsilon:.1},rewards=bounds.map((_,state)=>({prices:[prices[Math.floor(state/n)],prices[state%n]],consumerSurplus:100-state,profitA:state+1,profitB:20-state,jointProfit:21})),starts=bounds.map((economicBounds,state)=>({state,economicBounds,prefix:[state],cycle:[state]})),provenance=[{kind:'near-continuous-Nash-anchor'},...Array.from({length:8},(_,i)=>({kind:'saved-training-terminal-diagnostic',trainedArm:'none',seed:i+1,checkpoint:'unit-only',checkpointSha256:'unit-only'}))],guard={id:'synthetic-guard',controller:'guard',scenario:structuredClone(scenario),game:{n,prices,rewards,adjacency:rewards.map((_,state)=>[state])},objectives:{minCS:{starts,diagnosticStarts:[{state:0,indices:[0,0],provenance,result:starts[0]}]}}},cap={id:'synthetic-cap',controller:'cap',scenario:structuredClone(scenario),game:{n,prices:prices.slice(),sets:prices.map(()=>Array.from({length:existingK+1},(_,i)=>i))},objectives:{minCS:{universal:{economicBounds:{lower:10,upper:10}}}}};return {guard,cap,bounds};
}
const target=value=>({label:'unit-floor',basis:'synthetic test only',referenceValue:value,requestedTarget:value});
test('threshold reports the relaxed guarantee and classification preserves straddlers',()=>{
 const t=thresholdFor(100);assert.equal(t.numericalMargin,1e-6);assert.equal(t.actualGuaranteedThreshold,99.999999);assert.equal(classifyBounds({lower:100,upper:101},100),'safe');assert.equal(classifyBounds({lower:98,upper:99},100),'unsafe');assert.equal(classifyBounds({lower:99,upper:100},100),'ambiguous');assert.throws(()=>classifyBounds({lower:101,upper:100},100));
});
test('all feasible prefix caps are enumerated and largest safe one is class-optimal',()=>{
 const intervals=Array.from({length:9},(_,state)=>({lower:[0,1,3,4].includes(state)?10:4,upper:[0,1,3,4].includes(state)?10:4})),{guard,cap}=fixture({intervals}),r=analyzeTarget(guard,cap,target(9));assert.equal(r.prefixCandidates.length,3);assert.deepEqual(r.prefixCandidates.map(c=>c.certifiedSafe),[true,true,false]);assert.equal(r.largestSafeCommonPrefixCap.index,1);assert.equal(r.existingCompetitiveCap.certifiedSafe,true);assert.equal(r.existingCompetitiveCap.allowedInitialPricesPerSeller,2);assert.equal(r.existingCompetitiveCap.allowedInitialPriceSpan,1);assert.equal(r.safeOutgoingEdges,4);
});
test('a nonempty safe region can admit no common prefix cap',()=>{
 const intervals=Array.from({length:9},(_,state)=>({lower:state===8?10:4,upper:state===8?10:4})),{guard,cap}=fixture({intervals}),r=analyzeTarget(guard,cap,target(9));assert.deepEqual(r.statesByClass.safe,[8]);assert.equal(r.largestSafeCommonPrefixCap,null);assert.equal(r.finiteInitializerImpossible,false);assert.equal(r.existingCompetitiveCap.certifiedFailure,true);assert.ok(r.existingFailureWitness.attainedGuardTailMean<r.actualGuaranteedThreshold);
});
test('empty certified safe set proves no initializer only if no ambiguous state remains',()=>{
 const {guard,cap}=fixture({intervals:Array.from({length:9},()=>({lower:4,upper:4}))}),r=analyzeTarget(guard,cap,target(9));assert.equal(r.certifiedSafeRegionEmpty,true);assert.equal(r.finiteInitializerImpossible,true);guard.objectives.minCS.starts[0].economicBounds={lower:8,upper:10};const unresolved=analyzeTarget(guard,cap,target(9));assert.equal(unresolved.certifiedSafeRegionEmpty,true);assert.equal(unresolved.finiteInitializerImpossible,false);assert.deepEqual(unresolved.statesByClass.ambiguous,[0]);
});
test('forward-invariance failure in purported certificates is rejected',()=>{
 const {guard,cap}=fixture();guard.game.adjacency[0]=[8];assert.throws(()=>analyzeTarget(guard,cap,target(9)),/not forward invariant/);
});
test('first-round ranges use executed rectangle and exclude previous-state reward',()=>{
 const {guard,bounds}=fixture(),r=initializerResult(guard.game,bounds,new Array(9).fill('safe'),0);assert.deepEqual(r.postStates,[0]);assert.deepEqual(r.oneRoundOutcomeRanges.consumerSurplus,{minimum:100,maximum:100});assert.deepEqual(r.oneRoundOutcomeRanges.profitA,{minimum:1,maximum:1});assert.equal(r.allowedInitialPriceSpan,0);assert.equal(r.postStateCount,1);
});
test('five target labels and duplicate numerical targets retain separate provenance',()=>{
 const {guard,cap}=fixture(),labels=targetsFor(guard,cap);assert.equal(labels.length,5);assert.equal(labels[3].requestedTarget,labels[4].requestedTarget);assert.notEqual(labels[3].label,labels[4].label);const r=analyzeCase(guard,cap);assert.equal(r.results.length,5);assert.ok(r.results.every(t=>t.noneTrainedStartComparisons.length===8));
});
test('ambiguous post-cap states prevent certification without a false failure witness',()=>{
 const intervals=Array.from({length:9},()=>({lower:8,upper:10})),{guard,cap}=fixture({intervals}),r=analyzeTarget(guard,cap,target(9));assert.equal(r.existingCompetitiveCap.certifiedSafe,false);assert.equal(r.existingCompetitiveCap.certifiedFailure,false);assert.equal(r.existingCompetitiveCap.unresolved,true);assert.equal(r.existingFailureWitness,null);
});
test('matching IDs and grid sizes cannot hide different economy or prices',()=>{
 const {guard,cap}=fixture(),badEconomy=structuredClone(cap),badPrices=structuredClone(cap);badEconomy.scenario.economy.mu=.5;badPrices.game.prices[1]+=.001;assert.throws(()=>analyzeCase(guard,badEconomy),/economy, prices/);assert.throws(()=>analyzeCase(guard,badPrices),/economy, prices/);
});
