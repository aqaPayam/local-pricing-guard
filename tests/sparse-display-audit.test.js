import test from 'node:test';
import assert from 'node:assert/strict';
import {checkDisplayRecord,independentSavedOutcome} from '../research/audit-sparse-display.js';
import {certifyCycle} from '../research/recurring-game.js';

function fixture(){
 const e={id:'synthetic',quality:0,cost:0,mu:1,buyers:1,outsideQuality:0},scenario={id:'synthetic',economy:e,epsilon:100,gridSize:3};
 const prices=Array.from({length:61},(_,i)=>1+i/100),physical=1.05,capIndex=prices.indexOf(physical);
 const guard={id:'synthetic-guard',controller:'guard',scenario,game:{prices:[1,physical,1.6]}};
 const cap={id:'synthetic-cap',controller:'cap',scenario,game:{prices:guard.game.prices,sets:[[0,1],[0,1],[0,1]]}};
 const old={scenario,results:['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor'].map(label=>({label,requestedTarget:.1,numericalMargin:1e-8,actualGuaranteedThreshold:.1-1e-8,existingCompetitiveCap:{index:1,price:physical}}))};
 const rewards={consumerSurplus:[],profitA:[],profitB:[],quantityA:[],quantityB:[]};
 for(const a of prices)for(const b of prices){const r=independentSavedOutcome(a,b,e);for(const key in rewards)rewards[key].push(r[key]);}
 const sets=prices.map(()=>prices.map((_,i)=>i)),upper=prices.map(()=>60),finite={prices,sets,upper,capIndex,rewards,epsilon:100,comparisonAllowance:100+1e-12,tableMonotonicityChecks:2*61*60,tableCoordinateMonotone:true,upperMapMonotone:true,capOrbitNondecreasing:true,rowBestProfits:prices.map((_,j)=>Math.max(...prices.map((_,i)=>rewards.profitA[i*61+j])))};
 finite.certificates=[1,2,4,8,16,32,64,128].map(k=>certifyCycle(finite,k));
 return {record:{scenario,cap:{price:physical,index:capIndex,originalIndex:1,priorityTolerance:1e-12,removedBaseQuotes:[{price:physical,absoluteDistance:0}]},finite,originalTargets:old.results.map(({existingCompetitiveCap,...r})=>r)},inputs:{mesh:{scenario:'synthetic',n:61,economy:e,prices},guard,cap,old}};
}

test('independent full tables and actual first-cap/guard phases accept a synthetic game',()=>{
 const {record,inputs}=fixture(),r=checkDisplayRecord(record,inputs);
 assert.equal(r.payoffPairs,3721);assert.equal(r.oldPublicPairsChecked,3721);assert.equal(r.capOutcomesChecked,36);assert(r.executionsChecked>500);
});

test('separate economic/mask/cap/orbit corruptions are rejected',()=>{
 const {record,inputs}=fixture();
 for(const mutate of [r=>r.cap.price+=.01,r=>r.finite.rewards.profitB[0]+=1,r=>r.finite.sets[0]=[0],r=>r.finite.certificates[1].cycleIndices.reverse(),r=>r.originalTargets[0].actualGuaranteedThreshold+=1]){
  const changed=structuredClone(record);mutate(changed);assert.throws(()=>checkDisplayRecord(changed,inputs,{exercise:false}));
 }
});
