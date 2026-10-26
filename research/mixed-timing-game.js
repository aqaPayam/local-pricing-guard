// Pure manual finite-game execution. Existing rational helpers are unchanged.
// No network, random player, Q policy, learning or model call is used here.
import {rational,add,subtract,multiplyInteger,divideInteger,compare,fromDouble,fromJSON,exactJSON,approximate} from './recurring-game.js';
const need=(ok,message)=>{if(!ok)throw Error(message);},zero=()=>rational(0n);
const eq=(a,b)=>compare(a,b)===0;
const copy=value=>structuredClone(value);
const number=a=>({value:approximate(a),exact:exactJSON(a)});
const parse=x=>{need(x&&typeof x.numerator==='string'&&typeof x.denominator==='string'&&/^-?\d+$/.test(x.numerator)&&/^\d+$/.test(x.denominator)&&x.numerator.length<5000&&x.denominator.length<5000,'Missing exact finite certificate');const q=fromJSON(x);need(q.d>0n,'Invalid denominator');return q;};
const period=k=>Number.isInteger(k)&&k>=1&&k<=65536;

export function finiteTimingEnvelope(record){
 const g=record?.finite,n=g?.prices?.length;
 need(Number.isInteger(n)&&n>0&&n<=62,'Missing saved finite game');
 need(g.prices.every((p,i)=>Number.isFinite(p)&&(!i||p>g.prices[i-1])),'Quotes must be strictly increasing');
 need(Number.isInteger(g.capIndex)&&g.capIndex>=0&&g.capIndex<n&&record.cap?.index===g.capIndex&&record.cap.price===g.prices[g.capIndex],'Physical cap identity differs');
 need(g.sets?.length===n&&g.sets.every(s=>Array.isArray(s)&&s.length&&s.every((a,i)=>Number.isInteger(a)&&a>=0&&a<n&&(!i||a>s[i-1]))),'Missing legal guard choices');
 const upper=g.sets.map(s=>s.at(-1));
 need(upper.every((u,i)=>!i||u>=upper[i-1])&&upper[g.capIndex]>=g.capIndex,'Cap-start ordering is not certified');
 need(!g.upper||g.upper.length===n&&g.upper.every((u,i)=>u===upper[i]),'Recorded upper choices differ');
 for(const key of ['consumerSurplus','profitA','profitB','quantityA','quantityB'])need(g.rewards?.[key]?.length===n*n&&g.rewards[key].every(Number.isFinite),'Incomplete saved reward table');
 const cs=g.rewards.consumerSurplus.map(fromDouble);
 for(let i=0;i<n;i++)for(let j=0;j<n;j++)need((i+1===n||compare(cs[i*n+j],cs[(i+1)*n+j])>=0)&&(j+1===n||compare(cs[i*n+j],cs[i*n+j+1])>=0),'Customer-benefit table is not decreasing in prices');
 const orbit=[g.capIndex];while(upper[orbit.at(-1)]!==orbit.at(-1)){const next=upper[orbit.at(-1)];need(next>orbit.at(-1)&&orbit.length<n,'Upper path does not reach its fixed point');orbit.push(next);}
 const rewards=orbit.map(i=>cs[i*n+i]),prefix=[zero()];for(const r of rewards)prefix.push(add(prefix.at(-1),r));
 function sum(count){need(Number.isSafeInteger(count)&&count>=0,'Invalid execution count');return count<=rewards.length?prefix[count]:add(prefix.at(-1),multiplyInteger(rewards.at(-1),count-rewards.length));}
 return {n,upper,orbit,rewards,sum,limit:rewards.at(-1),reward:age=>rewards[Math.min(age,rewards.length-1)]};
}

export function createTimingGame(record,target,{mode='mixed',previous}={}){
 need(mode==='mixed'||mode==='fixed','Choose mixed or fixed timing');
 const g=record.finite,envelope=finiteTimingEnvelope(record),{n}=envelope;
 need(target?.kind==='finite'&&target.scenario===record.scenario.id,'A matching finite target is required');
 const old=record.originalTargets?.filter(t=>t.label===target.label);need(old?.length===1,'Original target identity missing');
 const F=parse(target.actualThresholdExact);need(eq(F,fromDouble(old[0].actualGuaranteedThreshold)),'Target differs from the original absolute threshold');
 const calendar=target.calendar;need(calendar&&['funded-mixed','fixed-safe','startup-only'].includes(calendar.kind)&&calendar.startupCaps===1,'No certified playable calendar is available');
 let K=null,a=null,b=null,kind=calendar.kind;
 if(kind==='startup-only')need(compare(F,envelope.limit)<=0,'Startup-only certificate does not protect this target');
 else{
  K=calendar.K;need(period(K),'Invalid certified gap');a=subtract(envelope.sum(K),multiplyInteger(F,K));need(a.n>=0n&&eq(a,parse(calendar.creditAExact)),'Safe-gap credit differs from the saved game');
  if(kind==='funded-mixed'){
   need(K<65536,'Long gap exceeds the declared ceiling');b=subtract(envelope.sum(K+1),multiplyInteger(F,K+1));
   need(b.n<0n&&eq(b,parse(calendar.creditBExact))&&eq(subtract(a,b),parse(calendar.creditUpperExclusiveExact)),'Long-gap credit is not certified');
   need(target.frontier?.bestFixedK===K,'The fixed comparator belongs to another target');
   const p=rational(a.n*b.d,a.n*b.d-b.n*a.d),rate=rational(p.d,BigInt(K)*p.d+p.n);
   need(target.rates?.exactOptimum===true&&eq(parse(target.rates.constructedRateExact),rate)&&eq(parse(target.rates.optimumRateBoundsExact.lower),rate)&&eq(parse(target.rates.optimumRateBoundsExact.upper),rate),'Finite mixed rate differs from its exact frontier');
  }else need(target.frontier?.certifiedSafeK===K&&target.frontier.bestFixedK===null,'Unknown fixed fallback identity');
 }
 const bestK=target.frontier?.bestFixedK??null,safeK=bestK??target.frontier?.certifiedSafeK??null;
 if(mode==='fixed'){
  need(period(safeK),'No finite fixed-gap comparator is available');K=safeK;kind='fixed-safe';
  a=subtract(envelope.sum(K),multiplyInteger(F,K));b=null;need(a.n>=0n,'Fixed comparator does not protect this target');
 }
 const initialPair=previous??[n-1,n-1];need(Array.isArray(initialPair)&&initialPair.length===2&&initialPair.every(i=>Number.isInteger(i)&&i>=0&&i<n),'Invalid unearned old history');
 const capActions=Array.from({length:g.capIndex+1},(_,i)=>i);
 function chooseGap(credit){return kind==='startup-only'?null:K+(kind==='funded-mixed'&&a.n>0n&&compare(credit,rational(-b.n,b.d))>=0?1:0);}
 const initial=()=>({previous:initialPair.slice(),T:0,caps:0,block:1,age:0,gap:chooseGap(zero()),credit:zero(),cs:zero(),profits:[zero(),zero()],guarantee:zero(),latest:null,ledger:[]});
 let state=initial();const history=[];
 const nextIsCap=()=>kind==='startup-only'?state.T===0:state.age===0;
 function allowed(shop){need(shop===0||shop===1,'Shop must be 0 or 1');return (nextIsCap()?capActions:g.sets[state.previous[1-shop]]).slice();}
 function preview(i,j){
  if(![i,j].every((q,f)=>Number.isInteger(q)&&allowed(f).includes(q)))return {legal:false,reason:'Choose one permitted price for each shop.'};
  const index=i*n+j,r=g.rewards;return {legal:true,indices:[i,j],prices:[g.prices[i],g.prices[j]],consumerSurplus:r.consumerSurplus[index],profits:[r.profitA[index],r.profitB[index]],quantities:[r.quantityA[index],r.quantityB[index]],type:nextIsCap()?'cap':'guard'};
 }
 function timing(){
  let planned=zero(),firstLong=null,reason='This calendar has no longer gaps.';
  if(kind!=='startup-only')planned=kind==='funded-mixed'?parse(target.rates.constructedRateExact):rational(1n,BigInt(K));
  if(kind==='funded-mixed'&&a.n>0n){
   const numerator=(-b.n)*a.d,denominator=b.d*a.n,shorts=(numerator+denominator-1n)/denominator;
   firstLong={initialShortBlocks:String(shorts),block:String(shorts+1n),execution:String(shorts*BigInt(K)+1n)};reason=null;
  }
  return {mode,kind,K,plannedRate:number(planned),bestFixedK:bestK,fixedSafeK:safeK,fixedRate:bestK===null?null:number(rational(1n,BigInt(bestK))),firstLong,firstLongUnavailableReason:reason,scope:'Cap-rule applications per execution in the limit; session fractions can differ.'};
 }
 function snapshot(){
  const T=state.T,excess=subtract(state.cs,multiplyInteger(F,T));
  return {executions:T,capExecutions:state.caps,capFraction:T?state.caps/T:null,block:state.block,nextAge:state.age,nextIsCap:nextIsCap(),chosenGapLength:state.gap,movesUntilCap:kind==='startup-only'?null:state.age===0?0:state.gap-state.age,
   previousIndices:state.previous.slice(),previousPrices:state.previous.map(i=>g.prices[i]),latest:copy(state.latest),
   target:{label:target.label,threshold:number(F)},averages:T?{consumerSurplus:number(divideInteger(state.cs,T)),profits:state.profits.map(p=>number(divideInteger(p,T)))}:null,
   actualExcess:number(excess),guaranteedBuffer:number(state.guarantee),boundaryCredit:number(state.credit),guaranteedAverage:T?number(add(F,divideInteger(state.guarantee,T))):null,
   benchmarkAverage:T?number(divideInteger(add(multiplyInteger(F,T),state.guarantee),T)):null,
   timing:timing(),canUndo:history.length>0,scope:'Exact saved-weight finite game. Every activation prefix, not each round or sliding window. Manual control of both shops; no model player.'};
 }
 function execute(i,j){
  const reward=preview(i,j);need(reward.legal,reward.reason);need(Number.isSafeInteger(state.T+1),'Execution counter exhausted');
  const T=state.T+1,cs=add(state.cs,fromDouble(reward.consumerSurplus)),partial=subtract(envelope.sum(state.age+1),multiplyInteger(F,state.age+1)),guarantee=add(state.credit,partial),excess=subtract(cs,multiplyInteger(F,T));
  need(guarantee.n>=0n&&compare(excess,guarantee)>=0,'Benefit evidence is inconsistent; no round was executed');
  const completed=kind!=='startup-only'&&state.age+1===state.gap,credit=completed?guarantee:state.credit;
  if(kind==='funded-mixed'&&completed)need(compare(credit,subtract(a,b))<0,'Bounded funding credit is inconsistent');
  const entry={execution:T,block:state.block,age:state.age,gapLength:state.gap,...reward,completedBlock:completed,boundaryCreditBefore:exactJSON(state.credit),boundaryCreditAfter:exactJSON(credit),guaranteedBuffer:exactJSON(guarantee),actualExcess:exactJSON(excess),averageConsumerSurplus:approximate(divideInteger(cs,T))};
  const next={previous:reward.indices.slice(),T,caps:state.caps+(reward.type==='cap'?1:0),block:state.block+(completed?1:0),age:completed?0:state.age+1,gap:completed?chooseGap(credit):state.gap,credit,cs,profits:state.profits.map((p,f)=>add(p,fromDouble(reward.profits[f]))),guarantee,latest:entry,ledger:[...state.ledger,entry]};
  history.push(state);state=next;return snapshot();
 }
 return {allowed,preview,execute,snapshot,ledger:()=>copy(state.ledger),undo(){if(history.length)state=history.pop();return snapshot();},reset(){state=initial();history.length=0;return snapshot();}};
}
