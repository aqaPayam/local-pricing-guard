// Entirely invented viewer inputs; not project findings or inherited payoffs.
import crypto from 'node:crypto';
import {rational,fromDouble,add,divideInteger,exactJSON} from '../../research/recurring-game.js';
export const TREATMENTS=['startup-guard','full-grid-after-cap'];
export const runId=(seed,t)=>t==='startup-guard'?`base-g15-t1--matched5-startup--zero--s${seed}`:`base-g15-t1--full-grid-after-cap--zero--s${seed}`;
const ref=b=>({bytes:b.length,base64:Buffer.from(b).toString('base64'),sha256:crypto.createHash('sha256').update(b).digest('hex')});
export function referenceFixture(){
 const finite={prices:[.1,.2,.3],capIndex:0,sets:[[0],[1],[1,2]],rewards:{consumerSurplus:[.9,.8,.7,.6,.5,.4,.3,.2,.1],profitA:[-.1,0,.1,.2,.3,.4,.5,.6,.7],profitB:[.7,.6,.5,.4,.3,.2,.1,0,-.1],quantityA:[1,2,3,4,5,6,7,8,9],quantityB:[9,8,7,6,5,4,3,2,1]}},orderedSeeds=Array.from({length:12},(_,i)=>907001+i),finalPolicies=[],pairedRows=[],checkpointStatuses=[],inheritedComparisonStatuses=[];
 const pair=(a,b)=>{const k=a*3+b,A=fromDouble(finite.rewards.profitA[k]),B=fromDouble(finite.rewards.profitB[k]);return{indices:[a,b],prices:[exactJSON(fromDouble(finite.prices[a])),exactJSON(fromDouble(finite.prices[b]))],profits:{A:exactJSON(A),B:exactJSON(B),joint:exactJSON(add(A,B))},consumerSurplus:exactJSON(fromDouble(finite.rewards.consumerSurplus[k]))};};
 let sum=rational(0n);
 for(const seed of orderedSeeds){
  const values=[];
  for(const t of TREATMENTS){
   const p=[new Uint8Array(45),new Uint8Array(45)];
   for(let s=0;s<45;s++){const phase=Math.floor(s/9),a=Math.floor(s/3)%3,b=s%3;p[0][s]=phase===0?0:t==='full-grid-after-cap'?2:finite.sets[b].at(-1);p[1][s]=phase===0?0:t==='full-grid-after-cap'?2:finite.sets[a].at(-1);}
   const cs=fromDouble(t==='startup-guard'?.3:(seed%3===0?.3:seed%3===1?.5:.1));values.push(exactJSON(cs));
   const id=runId(seed,t),scientificTreatment={capClock:'startup',supportMode:t,initialCap:true,postInitialOriginalIndices:t==='full-grid-after-cap'?'all':'original rival-dependent guard'};
   finalPolicies.push({seed,treatment:t,runId:id,checkpointId:id+'--t2000000',available:true,reason:null,encoding:'uint8 WORLD row-major (phase,previousA,previousB)',states:45,start:{phase:4,previousIndices:t==='startup-guard'?[2,1]:[1,2]},scientificTreatment,policies:{A:ref(p[0]),B:ref(p[1])},cycleMetrics:{consumerSurplus:exactJSON(cs)},cycleLength:4,transientRounds:0,trainingSupport:{A:{neverTriedGreedyActions:0},B:{neverTriedGreedyActions:0}}});
   if(t==='full-grid-after-cap')for(const step of [1000000,2000000])checkpointStatuses.push({runId:id,seed,step,scientificAvailable:true,status:'accepted',reason:null});
   else inheritedComparisonStatuses.push({runId:id,seed,step:2000000,scientificAvailable:true,status:'inherited accepted',reason:null});
  }
  const delta=rational(BigInt(values[1].numerator)*BigInt(values[0].denominator)-BigInt(values[0].numerator)*BigInt(values[1].denominator),BigInt(values[1].denominator)*BigInt(values[0].denominator));sum=add(sum,delta);
  pairedRows.push({seed,runIds:TREATMENTS.map(t=>runId(seed,t)),available:true,executionSucceeded:[true,true],replayMatched:[true,true],cycleCustomerBenefits:values,difference:exactJSON(delta),unavailableReason:null});
 }
 return{schemaVersion:1,meta:{inventoryAccepted:true,independentAuditPassed:true,audit:{passed:true},independentAuditSha256:'a'.repeat(64),primaryManifestSha256:'b'.repeat(64),startupGuardAuditSha256:'c'.repeat(64),fullTrainingReplay:true,replayComplete:true,defaultSelection:{seed:907001,checkpoint:2000000,treatments:TREATMENTS.slice(),chosenBeforeReferenceOutcomeInspection:true}},finiteGame:{finite},orderedSeeds,finalPolicies,pairedRows,primarySummary:{plannedDenominator:12,availablePairs:12,available:true,meanDifference:exactJSON(divideInteger(sum,12)),unavailableReason:null},completePairDescription:{denominator:12,seedIds:orderedSeeds.slice()},checkpointStatuses,inheritedComparisonStatuses,
  anchors:{available:true,independentAgreement:true,reason:null,values:{n:3,coordinateOrder:'WORLD row-major (currentA,currentB)',pureNash:{count:1,pairs:[pair(2,0)],reason:null},jointProfitMaximum:{value:pair(1,0).profits.joint,count:2,pairs:[pair(1,0),pair(1,2)]}},provenance:{scope:'Wholly invented presentation fixture; not evaluated stage-game anchors'}}};
}
