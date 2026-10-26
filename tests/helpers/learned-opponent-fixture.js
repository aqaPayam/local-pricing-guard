// Artificial arithmetic/schema fixtures only; imports no inherited evidence.
import {pack,subtract,compare,ZERO} from '../../research/learned-opponent-format.js';
export const r=(n,d=1n)=>pack({n:BigInt(n),d:BigInt(d)});
export function record(seed=1,controller='startup-only',focal='A',{baseline=10n,response=11n,upper=12n}={}){
 const b=r(baseline),v=r(response),u=r(upper),gain=subtract(v,b),gap=subtract(u,v);
 const coverage=()=>Object.fromEntries(['A','B'].map(name=>[name,{unweighted:{states:2,unvisitedStates:1,neverTriedChosenActions:1,minimumStateVisits:0,minimumChosenActionVisits:0},discounted:{unvisitedStateExposure:r(19n,20n),neverTriedChosenActionExposure:r(19n,20n)}}]));
 return {id:`s${seed}--${controller}--${focal}`,scenario:'base-g15-t1',initialization:'zero',checkpointStep:2000000,seed,control:{id:controller,period:controller==='startup-only'?null:4},focal,status:'certified loose feasible response',executionSucceeded:true,scientificAvailable:true,failure:null,
 baseline:{value:b,h:1,c:1,coverage:coverage(),eventualCycleCustomerBenefit:r(7n)},response:{value:v,h:1,c:1,coverage:coverage(),eventualCycleCustomerBenefit:r(6n)},
 certificate:{passed:true,upperValue:u,responseOptimalityGap:gap,requestedGap:r(1n,1000000n),withinRequestedGap:compare(gap,r(1n,1000000n))<=0},
 performance:{rawGain:gain,rawGainSign:compare(gain,ZERO)>0?'positive':compare(gain,ZERO)<0?'negative':'zero',possibleGain:{lower:compare(gain,ZERO)>0?gain:ZERO,upper:subtract(u,b)},relativeGain:baseline>0n?r(response-baseline,baseline):null,relativeGainReason:baseline>0n?null:'Exact baseline is zero or negative',cycleCustomerBenefitDifference:r(-1n)}};
}
export function plannedRecords(){const records=[];for(let seed=907001;seed<=907012;seed++)for(const control of ['startup-only','selected95'])for(const focal of ['A','B'])records.push(record(seed,control,focal,{response:control==='selected95'?13n:11n,upper:15n}));return records;}
