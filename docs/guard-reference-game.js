// Browser-compatible guard-reference paired frozen replay. No IO, randomness, model or Q update.
import {rational,add,subtract,divideInteger,fromDouble,approximate} from '/local-pricing-guard/recurring-game.js';
const need=(ok,message)=>{if(!ok)throw Error(message);},ARMS=['startup-guard','full-grid-after-cap'];
export const MAX_REPLAY_ROUNDS=4096,MAX_REPLAY_BATCH=20;
const zero=()=>rational(0n),pack=v=>({numerator:String(v.n),denominator:String(v.d),approximate:approximate(v)});
const copy=v=>JSON.parse(JSON.stringify(v));
const hashLabel=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
const capAt=(arm,p)=>p===0,next=p=>p===0||p===4?1:p+1;
const node=(n,p,pair)=>(p*n+pair[0])*n+pair[1];

export function decodeWorldPolicy(ref,states){
 need(Number.isInteger(states)&&states>=5&&states<=5*62*62,'Invalid policy dimension');
 need(ref?.bytes===states&&hashLabel(ref.sha256)&&typeof ref.base64==='string'&&ref.base64.length===4*Math.ceil(states/3)&&/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(ref.base64),'Malformed compact policy reference');
 let raw;try{raw=atob(ref.base64);}catch{throw Error('Invalid policy base64');}
 need(raw.length===states&&btoa(raw)===ref.base64,'Noncanonical policy base64 or length');
 return Uint8Array.from(raw,c=>c.charCodeAt(0));
}

export function createReferenceReplay({finiteGame,seed,treatments}){
 const source=finiteGame?.finite??finiteGame,n=source?.prices?.length;
 need(Number.isInteger(n)&&n>=1&&n<=62&&Number.isInteger(seed)&&seed>=907001&&seed<=907012,'Invalid finite dimension or seed');
 need(source.prices.every((p,i)=>Number.isFinite(p)&&(!i||p>source.prices[i-1]))&&Number.isInteger(source.capIndex)&&source.capIndex>=0&&source.capIndex<n,'Malformed original prices or cap');
 need(source.sets?.length===n&&source.sets.every(s=>Array.isArray(s)&&s.length&&s.every((a,i)=>Number.isInteger(a)&&a>=0&&a<n&&(!i||a>s[i-1]))),'Malformed original guard masks');
 for(const key of ['consumerSurplus','profitA','profitB','quantityA','quantityB'])need(source.rewards?.[key]?.length===n*n&&source.rewards[key].every(Number.isFinite),'Malformed saved '+key+' table');
 need(source.rewards.quantityA.every(v=>v>=0)&&source.rewards.quantityB.every(v=>v>=0),'Expected purchases cannot be negative');
 const f={prices:source.prices.slice(),capIndex:source.capIndex,sets:source.sets.map(s=>s.slice()),rewards:Object.fromEntries(['consumerSurplus','profitA','profitB','quantityA','quantityB'].map(k=>[k,source.rewards[k].slice()]))},states=5*n*n,cap=Array.from({length:f.capIndex+1},(_,i)=>i),entries={},decoded={};
 const full=Array.from({length:n},(_,i)=>i);
 const support=(arm,phase,pair,shop)=>capAt(arm,phase)?cap:arm==='full-grid-after-cap'?full:f.sets[pair[1-shop]];
 for(const arm of ARMS){
  const entry=treatments?.[arm];need(entry&&entry.treatment===arm&&entry.seed===seed&&typeof entry.available==='boolean'&&typeof entry.runId==='string'&&entry.runId.length&&typeof entry.checkpointId==='string'&&entry.checkpointId.length,'Missing or mismatched paired identity');
  need(entry.scientificTreatment?.capClock==='startup'&&entry.scientificTreatment.supportMode===arm&&entry.scientificTreatment.initialCap===true&&entry.scientificTreatment.postInitialOriginalIndices===(arm==='full-grid-after-cap'?'all':'original rival-dependent guard'),'Explicit panel support treatment differs');
  entries[arm]=copy(entry);
  if(!entry.available){need(typeof entry.reason==='string'&&entry.reason.length&&entry.policies===null,'Unavailable final arm requires a reason and null policies');continue;}
  need(entry.encoding==='uint8 WORLD row-major (phase,previousA,previousB)'&&entry.states===states,'WORLD policy encoding/dimension differs');
  need(entry.start?.phase===4&&entry.start.previousIndices?.length===2&&entry.start.previousIndices.every(i=>Number.isInteger(i)&&i>=0&&i<n),'Final actual NEXT phase4/history required; no fresh cap reset');
  const policies=[decodeWorldPolicy(entry.policies?.A,states),decodeWorldPolicy(entry.policies?.B,states)];
  for(let s=0;s<states;s++){
   const phase=Math.floor(s/(n*n)),pair=[Math.floor(s/n)%n,s%n];
   for(let shop=0;shop<2;shop++)need(support(arm,phase,pair,shop).includes(policies[shop][s]),'WORLD policy selects a forbidden quote, including off-path states');
  }
  decoded[arm]=policies;
 }
 const unavailable=ARMS.filter(a=>!entries[a].available),available=unavailable.length===0,reason=available?null:unavailable.map(a=>`${a}: ${entries[a].reason}`).join('; ');
 const initialArm=arm=>({phase:entries[arm].start.phase,previous:entries[arm].start.previousIndices.slice(),caps:0,cs:zero(),profits:[zero(),zero()],latest:null});
 const initial=()=>available?{rounds:0,arms:Object.fromEntries(ARMS.map(arm=>[arm,initialArm(arm)]))}:null;
 let state=initial();const past=[],rows=[];
 function reward(arm,s){
  const at=node(n,s.phase,s.previous),pair=[decoded[arm][0][at],decoded[arm][1][at]],index=pair[0]*n+pair[1];
  return{phase:s.phase,nextPhase:next(s.phase),sourceIndices:s.previous.slice(),executedIndices:pair,prices:pair.map(i=>f.prices[i]),consumerSurplus:f.rewards.consumerSurplus[index],profits:[f.rewards.profitA[index],f.rewards.profitB[index]],quantities:[f.rewards.quantityA[index],f.rewards.quantityB[index]],cap:capAt(arm,s.phase)};
 }
 function armSnapshot(arm){
  const s=state.arms[arm],rounds=state.rounds;
  return{treatment:arm,phase:s.phase,nextIsCap:capAt(arm,s.phase),previousIndices:s.previous.slice(),previousPrices:s.previous.map(i=>f.prices[i]),start:copy(entries[arm].start),executions:rounds,capExecutions:s.caps,latest:s.latest?copy(s.latest):null,
   earned:rounds?{customerBenefit:{sum:pack(s.cs),average:pack(divideInteger(s.cs,rounds))},profits:{A:{sum:pack(s.profits[0]),average:pack(divideInteger(s.profits[0],rounds))},B:{sum:pack(s.profits[1]),average:pack(divideInteger(s.profits[1],rounds))}}}:null};
 }
 function snapshot(){
  const rounds=state?.rounds??0;return{available,reason,seed,executions:rounds,canUndo:rounds>0,canAdvance:available&&rounds<MAX_REPLAY_ROUNDS,atRoundLimit:rounds>=MAX_REPLAY_ROUNDS,limit:MAX_REPLAY_ROUNDS,
   treatments:available?Object.fromEntries(ARMS.map(a=>[a,armSnapshot(a)])):Object.fromEntries(ARMS.map(a=>[a,{treatment:a,available:entries[a].available,reason:entries[a].reason??null,latest:null,earned:null}])),
   finiteBenefitDifference:rounds?{sum:pack(subtract(state.arms['full-grid-after-cap'].cs,state.arms['startup-guard'].cs)),average:pack(divideInteger(subtract(state.arms['full-grid-after-cap'].cs,state.arms['startup-guard'].cs),rounds))}:null,
   trace:copy(rows.slice(-60)),traceStartRound:rows.length?Math.max(1,rounds-59):null,
   scope:'New finite frozen replay only: undiscounted exact sums/averages of saved binary64 expected rewards. Old stored memory is unearned. Complete-cycle outcomes and old training are separate; no new floor is inferred.'};
 }
 function oneRound(){
  // Both actions in both worlds use their own prior completed state.
  const settled=Object.fromEntries(ARMS.map(a=>[a,reward(a,state.arms[a])])),round=state.rounds+1,nextArms={};
  for(const arm of ARMS){const previous=state.arms[arm],latest={round,...settled[arm]},cs=add(previous.cs,fromDouble(latest.consumerSurplus)),profits=previous.profits.map((sum,f)=>add(sum,fromDouble(latest.profits[f])));nextArms[arm]={phase:latest.nextPhase,previous:latest.executedIndices.slice(),caps:previous.caps+(latest.cap?1:0),cs,profits,latest};}
  past.push(state);rows.push({round,'startup-guard':copy(nextArms['startup-guard'].latest),'full-grid-after-cap':copy(nextArms['full-grid-after-cap'].latest)});state={rounds:round,arms:nextArms};
 }
 return{snapshot,preview(){need(available,'Paired replay locked: '+reason);return copy(Object.fromEntries(ARMS.map(a=>[a,reward(a,state.arms[a])])));},
  advance(rounds=1){need(available,'Paired replay locked: '+reason);need(Number.isInteger(rounds)&&rounds>=1&&rounds<=MAX_REPLAY_BATCH,'Replay batch must be 1..20 rounds');need(state.rounds+rounds<=MAX_REPLAY_ROUNDS,'Replay batch exceeds the 4096-round limit');for(let i=0;i<rounds;i++)oneRound();return snapshot();},
  undo(rounds=1){need(Number.isInteger(rounds)&&rounds>=1&&rounds<=MAX_REPLAY_BATCH,'Undo batch must be 1..20 rounds');if(available)for(let i=0;i<rounds&&past.length;i++){state=past.pop();rows.pop();}return snapshot();},
  restart(){state=initial();past.length=0;rows.length=0;return snapshot();}};
}
