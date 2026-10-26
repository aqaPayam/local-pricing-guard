import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeTarget} from '../research/handover-init.js';
import {auditInitializerTarget,independentlyClassify} from '../research/audit-handover-init.js';

function fixture(intervals=[{lower:10,upper:10},{lower:6,upper:6},{lower:6,upper:6},{lower:2,upper:2}],requestedTarget=7){
 const n=2,prices=[1,2],rewards=intervals.map((b,s)=>({prices:[prices[Math.floor(s/n)],prices[s%n]],consumerSurplus:b.upper,profitA:s+1,profitB:10-s,jointProfit:11})),adjacency=intervals.map((_,s)=>[s]),starts=intervals.map((economicBounds,state)=>({state,economicBounds,prefix:[state],cycle:[state]})),provenance=Array.from({length:8},(_,i)=>({kind:'saved-training-terminal-diagnostic',trainedArm:'none',seed:7001+i,checkpoint:'synthetic-'+i,checkpointSha256:'synthetic-hash-'+i})),guard={game:{n,prices,rewards,adjacency},objectives:{minCS:{starts,diagnosticStarts:[{state:0,indices:[0,0],provenance}]}}},cap={game:{sets:[[0,1],[0,1]]}},target={label:'unit-threshold',basis:'synthetic only',referenceValue:requestedTarget,requestedTarget},game={n,prices,rewards,adjacency,capIndex:1};
 const record={...analyzeTarget(guard,cap,target),anchorAttainedCSUpper:null};return {guard,cap,target,game,record};
}
function check(f){return auditInitializerTarget(f.record,f.guard,f.cap,f.target,f.game);}

test('independent relaxed classification retains a boundary straddler',()=>{
 const r=independentlyClassify([{lower:100,upper:100},{lower:98,upper:99},{lower:99,upper:100}],100);assert.equal(r.margin,1e-6);assert.equal(r.threshold,99.999999);assert.deepEqual(r.classes,['safe','unsafe','ambiguous']);
});
test('valid synthetic output passes; altered sets, caps, ranges and tails fail',()=>{
 const f=fixture();assert.equal(check(f).largestSafeCap,0);
 const mutations=[r=>{r.classification[0]='unsafe';},r=>{r.statesByClass.safe=[];},r=>{r.existingCompetitiveCap.index=0;},r=>{r.largestSafeCommonPrefixCap=null;},r=>{r.existingCompetitiveCap.oneRoundOutcomeRanges.consumerSurplus.minimum++;},r=>{r.existingFailureWitness.guardCycle=[0];},r=>{r.existingFailureWitness.attainedGuardTailMean++;},r=>{r.finiteInitializerImpossible=true;}];
 for(const mutate of mutations){const changed={...f,record:structuredClone(f.record)};mutate(changed.record);assert.throws(()=>check(changed));}
});
test('no prefix cap and empty certified region do not overstate impossibility',()=>{
 const nonprefix=fixture([{lower:2,upper:2},{lower:2,upper:2},{lower:2,upper:2},{lower:10,upper:10}]);const a=check(nonprefix);assert.equal(a.safeStates,1);assert.equal(a.largestSafeCap,null);assert.equal(a.finiteInitializerImpossible,false);
 const ambiguous=fixture([{lower:6,upper:8},{lower:2,upper:2},{lower:2,upper:2},{lower:2,upper:2}]);const b=check(ambiguous);assert.equal(b.safeStates,0);assert.equal(b.ambiguousStates,1);assert.equal(b.finiteInitializerImpossible,false);
 const unsafe=fixture(undefined,11);assert.equal(check(unsafe).finiteInitializerImpossible,true);
});
test('rebuilt unsafe outgoing edge rejects a purported invariant region',()=>{
 const f=fixture();f.game.adjacency[0]=[1];assert.throws(()=>check(f),/preserves safe set/);
});
