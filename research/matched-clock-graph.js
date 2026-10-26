// Pure frozen-policy evaluation; no exploration, training, file IO or case execution.
import crypto from 'node:crypto';
import {validateState,nextPhase,isCap,u32Bytes} from './matched-clock-learning.js';
import {integerWeights,binary64,rational,welfareCertificate} from './incentive-study.js';
const need=(v,message)=>{if(!v)throw Error(message);},sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const pack=v=>({numerator:String(v.n),denominator:String(v.d),approximate:Number(v.n)/Number(v.d)});
const subtract=(a,b)=>rational(a.n*b.d-b.n*a.d,a.d*b.d),read=v=>rational(v.numerator,v.denominator);
const compare=(a,b)=>a.n*b.d<b.n*a.d?-1:a.n*b.d>b.n*a.d?1:0;
const normalizeExact=value=>Array.isArray(value)?value.map(normalizeExact):value&&typeof value==='object'?('numerator'in value&&'denominator'in value?pack(read(value)):Object.fromEntries(Object.entries(value).map(([k,v])=>[k,normalizeExact(v)]))):value;
const coord=(node,n)=>({phase:Math.floor(node/(n*n)),previousIndices:[Math.floor(node/n)%n,node%n]});
const nodeOf=(n,phase,a,b)=>(phase*n+a)*n+b;

export function greedyPolicies(m){
 const policies=[new Uint8Array(m.rows),new Uint8Array(m.rows)],visits=[new Uint32Array(m.rows),new Uint32Array(m.rows)],chosenVisits=[new Uint32Array(m.rows),new Uint32Array(m.rows)];
 for(let f=0;f<2;f++)for(let row=0;row<m.rows;row++){
  const legal=m.supports[Math.floor(row/(m.n*m.n))][row%m.n],off=row*m.n;let winner=legal[0],total=0;
  for(const action of legal){need(Number.isFinite(m.q[f][off+action]),'Nonfinite frozen Q');if(m.q[f][off+action]>m.q[f][off+winner])winner=action;total+=m.counts[f][off+action];}
  policies[f][row]=winner;visits[f][row]=total;chosenVisits[f][row]=m.counts[f][off+winner];
 }
 return{policies,visits,chosenVisits};
}
function certifiedFloor(m){
 const f=m.finite,n=m.n,upper=f.sets.map(s=>s.at(-1));
 need(upper.every((v,i)=>i===0||v>=upper[i-1]),'Floor premise: upper map must be nondecreasing');
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  const value=f.rewards.consumerSurplus[a*n+b];
  if(a+1<n)need(value>=f.rewards.consumerSurplus[(a+1)*n+b],'Floor premise: CS not decreasing in A price');
  if(b+1<n)need(value>=f.rewards.consumerSurplus[a*n+b+1],'Floor premise: CS not decreasing in B price');
 }
 let bound=f.capIndex;const orbit=[bound];
 while(upper[bound]!==bound){need(upper[bound]>=bound&&orbit.length<=n,'Cap upper orbit not increasing to a fixed point');bound=upper[bound];orbit.push(bound);}
 const guardSteps=m.t===0?null:m.arm==='startup'?m.t-1:(m.t-1)%4;
 let actualBound=f.capIndex;if(m.t>0)for(let i=0;i<guardSteps;i++){const next=upper[actualBound];if(next===actualBound)break;actualBound=next;}
 if(m.t>0)need(m.previous.every(v=>v<=actualBound),'Actual endpoint violates clock-specific cap upper bound');
 const raw=m.record.finite?m.record:{finite:f,originalTargets:[]};
 if(m.arm==='recurring4'){
  const certificate=normalizeExact(welfareCertificate(raw,4));
  return{kind:'recurring-four-round-cap',activationFloor:certificate.activationAverageFloor,cycleMean:certificate.cycleMean,upperOrbit:orbit,fixedPointIndex:bound,endpointUpperIndex:m.t===0?n-1:actualBound,guardStepsSinceCap:guardSteps,scope:'Same numerical game, cap-first history and continuing four-round cap/guard schedule; common phase0 is transient.',targetComparisons:certificate.targetComparisons};
 }
 const value=binary64(f.rewards.consumerSurplus[bound*n+bound]);
 return{kind:'startup-cap-first',activationFloor:pack(value),cycleMean:pack(value),upperOrbit:orbit,fixedPointIndex:bound,endpointUpperIndex:m.t===0?n-1:actualBound,guardStepsSinceCap:guardSteps,scope:'Cap-first histories and their continuations only. Arbitrary guard-history cycles outside this price bound are retained without transferring the cap-first floor.',targetComparisons:(raw.originalTargets??[]).map(t=>({label:t.label,actualThreshold:pack(binary64(t.actualGuaranteedThreshold)),floorMeetsTarget:compare(value,binary64(t.actualGuaranteedThreshold))>=0}))};
}

export function summarizeWindows(m){
 const n=m.n,weights={CS:integerWeights(m.finite.rewards.consumerSurplus),A:integerWeights(m.finite.rewards.profitA),B:integerWeights(m.finite.rewards.profitB),price:integerWeights(m.finite.prices)};
 return m.windows.map(w=>{
  if(!w.rounds){need(w.transitions.size===0,'Empty window has transition counts');return{startStep:w.startStep,endStep:w.endStep,rounds:0,metrics:null,reason:'No executed rounds in this window at this checkpoint'};}
  let total=0,cs=0n,A=0n,B=0n,pA=0n,pB=0n,countA=0n,countB=0n,spanA=0n,spanB=0n,highA=0,highB=0,caps=0,changeA=0,changeB=0;
  for(const[key,count]of w.transitions){
   need(Number.isInteger(key)&&key>=0&&key<m.rows*n*n&&Number.isInteger(count)&&count>0&&count<=m.T,'Malformed window joint transition');
   const source=Math.floor(key/(n*n)),pair=key%(n*n),phase=Math.floor(source/(n*n)),pa=Math.floor(source/n)%n,pb=source%n,a=Math.floor(pair/n),b=pair%n,sA=m.supports[phase][pb],sB=m.supports[phase][pa],k=BigInt(count);
   need(sA.includes(a)&&sB.includes(b),'Window has forbidden executed quote');
   total+=count;cs+=weights.CS.weights[pair]*k;A+=weights.A.weights[pair]*k;B+=weights.B.weights[pair]*k;pA+=weights.price.weights[a]*k;pB+=weights.price.weights[b]*k;countA+=BigInt(sA.length)*k;countB+=BigInt(sB.length)*k;spanA+=(weights.price.weights[sA.at(-1)]-weights.price.weights[sA[0]])*k;spanB+=(weights.price.weights[sB.at(-1)]-weights.price.weights[sB[0]])*k;highA+=(a===sA.at(-1)?count:0);highB+=(b===sB.at(-1)?count:0);caps+=isCap(m.arm,phase)?count:0;changeA+=a!==pa?count:0;changeB+=b!==pb?count:0;
  }
  need(total===w.rounds&&highA===w.maxAllowed[0]&&highB===w.maxAllowed[1]&&caps===w.capExecutions&&changeA===w.priceChanges[0]&&changeB===w.priceChanges[1],'Window counters disagree with joint transitions');
  need(w.explorations.every(v=>Number.isInteger(v)&&v>=0&&v<=total),'Invalid exploration counters');
  const len=BigInt(total),mean=(v,d=1n)=>pack(rational(BigInt(v),d*len));
  return{startStep:w.startStep,endStep:w.endStep,rounds:total,metrics:{consumerSurplus:mean(cs,weights.CS.denominator),profits:{A:mean(A,weights.A.denominator),B:mean(B,weights.B.denominator)},prices:{A:mean(pA,weights.price.denominator),B:mean(pB,weights.price.denominator)},maskCount:{A:mean(countA),B:mean(countB)},maskFraction:{A:mean(countA,BigInt(n)),B:mean(countB,BigInt(n))},maskSpan:{A:mean(spanA,weights.price.denominator),B:mean(spanB,weights.price.denominator)},maxAllowedUsage:{A:mean(highA),B:mean(highB)},capRuleFrequency:mean(caps),explorationFrequency:{A:mean(w.explorations[0]),B:mean(w.explorations[1])},priceChangeFrequency:{A:mean(changeA),B:mean(changeB)}},reason:null};
 });
}

export function evaluateFrozen(m,{certifyFloor=true}={}){
 validateState(m);
 const n=m.n,N=m.rows,{policies,visits,chosenVisits}=greedyPolicies(m),successor=new Uint32Array(N),labels=new Int32Array(N).fill(-1),distance=new Uint32Array(N),position=new Int32Array(N).fill(-1),cycles=new Map();
 const weights={CS:integerWeights(m.finite.rewards.consumerSurplus),A:integerWeights(m.finite.rewards.profitA),B:integerWeights(m.finite.rewards.profitB),price:integerWeights(m.finite.prices)},floor=certifyFloor?certifiedFloor(m):null;
 const worldPolicies=[new Uint8Array(N),new Uint8Array(N)];
 function execution(node){const{phase,previousIndices:[pa,pb]}=coord(node,n),other=nodeOf(n,phase,pb,pa),a=policies[0][node],b=policies[1][other];return{phase,pa,pb,other,a,b,pair:a*n+b};}
 for(let node=0;node<N;node++){const e=execution(node);need(m.supports[e.phase][e.pb].includes(e.a)&&m.supports[e.phase][e.pa].includes(e.b),'Frozen forbidden action');worldPolicies[0][node]=e.a;worldPolicies[1][node]=e.b;successor[node]=nodeOf(n,nextPhase(e.phase),e.a,e.b);}
 for(let start=0;start<N;start++){
  if(labels[start]>=0)continue;const path=[];let at=start;
  while(labels[at]<0&&position[at]<0){position[at]=path.length;path.push(at);at=successor[at];}
  if(labels[at]<0){const raw=path.slice(position[at]);let first=0;for(let k=1;k<raw.length;k++)if(raw[k]<raw[first])first=k;const nodes=raw.slice(first).concat(raw.slice(0,first)),id=nodes[0];need(nodes.every(v=>Math.floor(v/(n*n))!==0),'One-time phase0 cannot recur');cycles.set(id,{id,nodes,length:nodes.length,basinStates:0});for(const node of nodes){labels[node]=id;distance[node]=0;}}
  for(let k=path.length-1;k>=0;k--){const node=path[k];if(labels[node]<0){labels[node]=labels[successor[node]];distance[node]=distance[successor[node]]+1;}position[node]=-1;}
 }
 const capReachable=new Set();for(let node=0;node<n*n;node++)capReachable.add(labels[node]);for(const label of labels)cycles.get(label).basinStates++;
 function metrics(nodes){
  if(!nodes.length)return null;let cs=0n,A=0n,B=0n,pA=0n,pB=0n,countA=0n,countB=0n,spanA=0n,spanB=0n,highA=0n,highB=0n,caps=0n;const len=BigInt(nodes.length);
  for(const node of nodes){const e=execution(node),sA=m.supports[e.phase][e.pb],sB=m.supports[e.phase][e.pa];cs+=weights.CS.weights[e.pair];A+=weights.A.weights[e.pair];B+=weights.B.weights[e.pair];pA+=weights.price.weights[e.a];pB+=weights.price.weights[e.b];countA+=BigInt(sA.length);countB+=BigInt(sB.length);spanA+=weights.price.weights[sA.at(-1)]-weights.price.weights[sA[0]];spanB+=weights.price.weights[sB.at(-1)]-weights.price.weights[sB[0]];highA+=e.a===sA.at(-1)?1n:0n;highB+=e.b===sB.at(-1)?1n:0n;caps+=isCap(m.arm,e.phase)?1n:0n;}
  const fraction=(v,d=1n)=>pack(rational(v,d*len));return{rounds:nodes.length,consumerSurplus:fraction(cs,weights.CS.denominator),profits:{A:fraction(A,weights.A.denominator),B:fraction(B,weights.B.denominator)},prices:{A:fraction(pA,weights.price.denominator),B:fraction(pB,weights.price.denominator)},maskCount:{A:fraction(countA),B:fraction(countB)},maskFraction:{A:fraction(countA,BigInt(n)),B:fraction(countB,BigInt(n))},maskSpan:{A:fraction(spanA,weights.price.denominator),B:fraction(spanB,weights.price.denominator)},maxAllowedUsage:{A:fraction(highA),B:fraction(highB)},capRuleFrequency:fraction(caps)};
 }
 function support(nodes){
  const out={A:{unvisitedStates:0,neverTriedGreedyActions:0,minimumStateVisits:null,minimumActionVisits:null},B:{unvisitedStates:0,neverTriedGreedyActions:0,minimumStateVisits:null,minimumActionVisits:null}};
  for(const node of nodes){const e=execution(node);for(const[f,row,name]of[[0,node,'A'],[1,e.other,'B']]){const total=visits[f][row],chosen=chosenVisits[f][row],u=out[name];u.unvisitedStates+=total===0?1:0;u.neverTriedGreedyActions+=chosen===0?1:0;u.minimumStateVisits=u.minimumStateVisits===null?total:Math.min(total,u.minimumStateVisits);u.minimumActionVisits=u.minimumActionVisits===null?chosen:Math.min(chosen,u.minimumActionVisits);}}
  return out;
 }
 for(const cycle of cycles.values()){
  cycle.metrics=metrics(cycle.nodes);cycle.trainingSupport=support(cycle.nodes);cycle.policyCapReachable=capReachable.has(cycle.id);cycle.maximumExecutedIndices=[0,0];for(const node of cycle.nodes){const e=execution(node);cycle.maximumExecutedIndices[0]=Math.max(cycle.maximumExecutedIndices[0],e.a);cycle.maximumExecutedIndices[1]=Math.max(cycle.maximumExecutedIndices[1],e.b);}
  cycle.floorApplies=floor===null?null:m.arm==='recurring4'||cycle.policyCapReachable||cycle.maximumExecutedIndices.every(a=>a<=floor.fixedPointIndex);
  cycle.floorGap=floor===null?null:pack(subtract(read(cycle.metrics.consumerSurplus),read(floor.activationFloor)));
  if(cycle.floorApplies)need(BigInt(cycle.floorGap.numerator)>=0n,'Applicable all-policy floor violated');
 }
 function trajectory(start,kind){
  const path=[],seen=new Map();let at=start;while(!seen.has(at)){seen.set(at,path.length);path.push(at);at=successor[at];}const h=seen.get(at),cycle=cycles.get(labels[start]);
  return{kind,startNode:start,start:coord(start,n),transientNodes:path.slice(0,h),transientRounds:h,transientMetrics:metrics(path.slice(0,h)),cycleId:cycle.id,cycleNodesFromStart:path.slice(h),cycleMetrics:cycle.metrics,trainingSupport:cycle.trainingSupport,pathTrainingSupport:support(path),floorApplies:cycle.floorApplies,floorGap:cycle.floorGap};
 }
 const actual=trajectory(nodeOf(n,m.phase,...m.previous),'actual-terminal-continuation'),fresh=trajectory(n*n-1,'counterfactual-high-history-fresh-activation');
 if(floor)need(actual.floorApplies===true,'Actual continuation lacks cap-first floor scope');
 const preview=[];let at=actual.startNode;for(let round=1;round<=128;round++){const e=execution(at);preview.push({execution:round,sourceNode:at,phase:e.phase,previousIndices:[e.pa,e.pb],executedIndices:[e.a,e.b],nextPhase:nextPhase(e.phase),prices:[m.finite.prices[e.a],m.finite.prices[e.b]],consumerSurplus:m.finite.rewards.consumerSurplus[e.pair],profits:[m.finite.rewards.profitA[e.pair],m.finite.rewards.profitB[e.pair]],cap:isCap(m.arm,e.phase)});at=successor[at];}
 return{policies,worldPolicies,graph:{states:N,step:m.t,phase:m.phase,arm:m.arm,coordinateOrder:'WORLD (phase,previousA,previousB). policies use focal own/rival rows; worldPolicies have B transposed once.',successorSha256:sha(u32Bytes(successor)),cycleLabelSha256:sha(u32Bytes(labels)),transientDistanceSha256:sha(u32Bytes(distance)),policySha256:policies.map(a=>sha(a)),worldPolicySha256:worldPolicies.map(a=>sha(a)),cycles:[...cycles.values()].sort((a,b)=>a.id-b.id),floor,actualTerminal:actual,freshCapCounterfactual:fresh,terminalPreview128:preview,coverage:{A:{visitedStates:visits[0].filter(v=>v>0).length,visitedActions:m.counts[0].filter(v=>v>0).length},B:{visitedStates:visits[1].filter(v=>v>0).length,visitedActions:m.counts[1].filter(v=>v>0).length},allocatedStatesPerFirm:N,allocatedCellsPerFirm:m.cells},scope:'Exact rational saved-weight deterministic frozen cycles; no exploration/update. Actual-terminal endpoint is primary; reset and arbitrary-state cycles are secondary. Preview is truncated; support does not prove competence or convergence.'}};
}
