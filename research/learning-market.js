// Local tabular learners. No inference, account access, network or cooperation reward.
import { outcome, NASH_PRICE, MONOPOLY_PRICE } from './replacement-market.js';
import { projectQuote } from './receiver-contract.js';
export function gridPrices(n=15) {
  if(!Number.isInteger(n)||n<3||n>51) throw Error('Invalid grid size');
  const d=MONOPOLY_PRICE-NASH_PRICE, lo=NASH_PRICE-.1*d, hi=MONOPOLY_PRICE+.1*d;
  return Array.from({length:n},(_,i)=>lo+(hi-lo)*i/(n-1));
}
function profit(p,q,{cost=1,mu=.25}={}) {const a=Math.exp((2-p)/mu),b=Math.exp((2-q)/mu);return 100*(p-cost)*a/(1+a+b);}
export function gridBenchmarks(prices) {
  const n=prices.length, profits=prices.map(p=>prices.map(q=>profit(p,q)));
  const br=prices.map((_,j)=>{let k=0;for(let i=1;i<n;i++)if(profits[i][j]>profits[k][j]+1e-12)k=i;return k;});
  const equilibria=[];let joint={indices:[0,0],profit:-Infinity};
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){if(profits[br[j]][j]-profits[i][j]<=1e-12&&profits[br[i]][i]-profits[j][i]<=1e-12)equilibria.push([i,j]);const v=profits[i][j]+profits[j][i];if(v>joint.profit)joint={indices:[i,j],profit:v};}
  return {prices,profits,bestResponses:br,equilibria,jointMaximum:joint};
}
function next(rng) {rng.value=(Math.imul(rng.value,1664525)+1013904223)>>>0;return rng.value/4294967296;}
function nearest(prices,p){let k=0;for(let i=1;i<prices.length;i++)if(Math.abs(prices[i]-p)<Math.abs(prices[k]-p)-1e-14)k=i;return k;}
export function createMarket({seed=1,gridSize=15,gamma=.95,alpha=.15,beta=4e-6,memory=true}={}) {
  if(!Number.isInteger(seed)||seed<0||!Number.isFinite(gamma)||gamma<0||gamma>=1||!Number.isFinite(alpha)||alpha<=0||alpha>1||!Number.isFinite(beta)||beta<0||typeof memory!=='boolean')throw Error('Invalid learner configuration');
  const prices=gridPrices(gridSize), n=prices.length, states=memory?n*n+1:1;
  const q=Array.from({length:2},()=>{const a=new Float64Array(states*n);for(let s=0;s<states;s++)for(let i=0;i<n;i++)a[s*n+i]=prices.reduce((v,p)=>v+profit(prices[i],p),0)/n/(1-gamma);return a;});
  const rng=[{value:(seed^0xa5a5a5a5)>>>0},{value:(seed^0x5a5a5a5a)>>>0}],previous=rng.map(r=>Math.floor(next(r)*n));
  return {config:{seed,gridSize,gamma,alpha,beta,memory},prices,q,rng,t:0,previous,previousPrices:previous.map(i=>prices[i]),reset:[false,false]};
}
export function checkpoint(m){return {...structuredClone(m),q:m.q.map(a=>Array.from(a))};}
export function restore(c){return {...structuredClone(c),q:c.q.map(a=>Float64Array.from(a))};}
export function cloneMarket(m){return restore(checkpoint(m));}
export function resetObservation(m,firm=0){m.reset[firm]=true;}
export function replaceLearner(m,source=null,firm=0,{reset=false}={}){const fresh=source||createMarket(m.config);m.q[firm]=Float64Array.from(fresh.q[firm]);if(reset)m.reset[firm]=true;}
const caches=new Map();
export function treatmentMap(prices,treatment={}) {
  const key=JSON.stringify([prices,treatment]);if(caches.has(key))return caches.get(key);
  const n=prices.length, type=treatment.type||'none',epsilon=treatment.epsilon??0;
  if(!['none','guard','best-response','fixed-nash','cap','continuous'].includes(type)||!Number.isFinite(epsilon)||epsilon<0||!['both','A','B'].includes(treatment.coverage||'both')|| (treatment.releaseAfter!=null&&(!Number.isInteger(treatment.releaseAfter)||treatment.releaseAfter<0)))throw Error('Invalid treatment');
  const map=Array.from({length:n},()=>new Int16Array(n)),counts=[];
  for(let j=0;j<n;j++) {
    const values=prices.map(p=>profit(p,prices[j],treatment.model)),best=Math.max(...values);
    const allowed=values.map((v,i)=>best-v<=epsilon+1e-12?i:-1).filter(i=>i>=0);counts.push(allowed.length);
    for(let a=0;a<n;a++) {let k=a;if(type==='guard'||type==='best-response'){const set=type==='best-response'?values.map((v,i)=>best-v<=1e-12?i:-1).filter(i=>i>=0):allowed;k=set.reduce((v,i)=>Math.abs(i-a)<Math.abs(v-a)?i:v,set[0]);}else if(type==='fixed-nash')k=nearest(prices,NASH_PRICE);else if(type==='cap')k=Math.min(a,nearest(prices,treatment.cap??NASH_PRICE));map[j][a]=k;}
  }
  if(type!=='guard')for(let j=0;j<n;j++)counts[j]=type==='continuous'?NaN:new Set(map[j]).size;
  const result={map,counts};caches.set(key,result);return result;
}
function state(m,f){if(!m.config.memory)return 0;if(m.reset[f])return m.prices.length**2;return m.previous[f]*m.prices.length+m.previous[1-f];}
export function advance(m,steps,{treatment={},learn=true,explore=true,explorationRate=null,traceEvery=0,binSize=10000,fixedOpponent=null,forceFirst=null}={}) {
  if(!Number.isInteger(steps)||steps<0||!Number.isInteger(traceEvery)||traceEvery<0)throw Error('Invalid steps/trace frequency');
  const n=m.prices.length,{alpha,gamma,beta}=m.config,lookup=treatmentMap(m.prices,treatment),rows=[],bins=[];
  let totals={rounds:0,priceA:0,priceB:0,profitA:0,profitB:0,consumerSurplus:0,interventions:0,adjustment:0,allowedFraction:0,laggedRegret:0,realizedRegret:0},bin={...totals};
  for(let t=0;t<steps;t++) {
    const states=[state(m,0),state(m,1)],actions=[],epsilon=explorationRate??(explore?Math.exp(-beta*m.t):0);
    for(let f=0;f<2;f++){const off=states[f]*n;let a=0;for(let k=1;k<n;k++)if(m.q[f][off+k]>m.q[f][off+a])a=k;const u=next(m.rng[f]),v=next(m.rng[f]);if(u<epsilon)a=Math.floor(v*n);actions.push(a);}
    if(fixedOpponent!==null)actions[1]=nearest(m.prices,fixedOpponent);
    const active=treatment.releaseAfter==null||t<treatment.releaseAfter;
    const covered=[0,1].map(f=>active&&(treatment.coverage||'both')!==(f===0?'B':'A')&&(treatment.type||'none')!=='none');
    const executed=actions.map((a,f)=>covered[f]?lookup.map[m.previous[1-f]][a]:a);
    if(t===0&&forceFirst!==null){if(forceFirst==='best-response'){let best=0;for(let k=1;k<n;k++)if(profit(m.prices[k],m.previousPrices[1])>profit(m.prices[best],m.previousPrices[1]))best=k;executed[0]=best;}else executed[0]=forceFirst;}
    let prices=executed.map(a=>m.prices[a]);
    if(treatment.type==='continuous')prices=actions.map((a,f)=>covered[f]?projectQuote(m.prices[a],m.previousPrices[1-f],{epsilon:treatment.epsilon??0,model:treatment.model||{}}).price:m.prices[a]);
    const result=outcome(prices),nextIndices=prices.map(p=>nearest(m.prices,p));
    const nextStates=[0,1].map(f=>m.config.memory?nextIndices[f]*n+nextIndices[1-f]:0),updates=[];
    for(let f=0;f<2;f++){const off=nextStates[f]*n;let max=-Infinity;for(let k=0;k<n;k++)max=Math.max(max,m.q[f][off+k]);const index=states[f]*n+actions[f],oldQ=m.q[f][index],target=result.profits[f]+gamma*max;if(learn)m.q[f][index]+=alpha*(target-oldQ);updates.push({oldQ,target,maxNext:max,newQ:m.q[f][index],alpha,gamma});}
    const changes=prices.map((p,f)=>Math.abs(p-m.prices[actions[f]]));
    const lag=prices.map((p,f)=>Math.max(0,...m.prices.map(a=>profit(a,m.previousPrices[1-f])-profit(p,m.previousPrices[1-f]))));
    const realized=prices.map((p,f)=>Math.max(0,...m.prices.map(a=>profit(a,prices[1-f])-result.profits[f])));
    const values={rounds:1,priceA:prices[0],priceB:prices[1],profitA:result.profits[0],profitB:result.profits[1],consumerSurplus:result.consumerSurplus,interventions:changes.filter(x=>x>1e-10).length/2,adjustment:(changes[0]+changes[1])/2,allowedFraction:covered.reduce((sum,c,f)=>sum+(c?lookup.counts[m.previous[1-f]]/n:1),0)/2,laggedRegret:(lag[0]+lag[1])/2,realizedRegret:(realized[0]+realized[1])/2};
    for(const key of Object.keys(totals)){totals[key]+=values[key];bin[key]+=values[key];}
    if(traceEvery&&t%traceEvery===0)rows.push({step:m.t,localStep:t,states,actions,executedIndices:nextIndices,previousPrices:m.previousPrices.slice(),prices,profits:result.profits,consumerSurplus:result.consumerSurplus,nextStates,covered,exploration:epsilon,updates,laggedRegret:lag,realizedRegret:realized});
    m.previous=nextIndices;m.previousPrices=prices;m.reset=[false,false];m.t++;
    if(bin.rounds===binSize||t===steps-1){bins.push({endStep:m.t,...Object.fromEntries(Object.entries(bin).map(([k,v])=>[k,k==='rounds'?v:v/bin.rounds]))});bin={...Object.fromEntries(Object.keys(bin).map(k=>[k,0]))};}
  }
  return {metrics:Object.fromEntries(Object.entries(totals).map(([k,v])=>[k,k==='rounds'?v:steps?v/steps:0])),rows,bins};
}
// Training path: identical timing and random draws; cached outcome tensors avoid
// repeated exponentials and diagnostics. Full transition auditing uses advance.
export function train(m,steps,{treatment={},binSize=10000,traceEvery=100000,fixedOpponent=null}={}) {
  if(treatment.type==='continuous')throw Error('Continuous guard is evaluation-only; train requires discrete execution.');
  if(!Number.isInteger(steps)||steps<0)throw Error('Invalid training steps');
  const n=m.prices.length,{alpha,gamma,beta}=m.config,lookup=treatmentMap(m.prices,treatment),tensor=[];
  for(let i=0;i<n;i++)for(let j=0;j<n;j++)tensor.push(outcome([m.prices[i],m.prices[j]]));
  const bins=[],rows=[];let cs=0,pa=0,pb=0,ra=0,rb=0,count=0,interventions=0;
  for(let t=0;t<steps;t++) {
    const s0=state(m,0),s1=state(m,1),states=[s0,s1],a=[0,0],epsilon=Math.exp(-beta*m.t);
    for(let f=0;f<2;f++){const off=states[f]*n,q=m.q[f];for(let k=1;k<n;k++)if(q[off+k]>q[off+a[f]])a[f]=k;const u=next(m.rng[f]),v=next(m.rng[f]);if(u<epsilon)a[f]=Math.floor(v*n);}
    if(fixedOpponent!==null)a[1]=nearest(m.prices,fixedOpponent);
    const active=treatment.releaseAfter==null||t<treatment.releaseAfter,coverage=treatment.coverage||'both',type=treatment.type||'none';
    const covered=[active&&type!=='none'&&coverage!=='B',active&&type!=='none'&&coverage!=='A'];
    const x=covered[0]?lookup.map[m.previous[1]][a[0]]:a[0],y=covered[1]?lookup.map[m.previous[0]][a[1]]:a[1],r=tensor[x*n+y];
    const ns=[m.config.memory?x*n+y:0,m.config.memory?y*n+x:0],updates=[];
    for(let f=0;f<2;f++){const q=m.q[f],off=ns[f]*n;let max=-Infinity;for(let k=0;k<n;k++)if(q[off+k]>max)max=q[off+k];const index=states[f]*n+a[f],oldQ=q[index],target=r.profits[f]+gamma*max;q[index]=oldQ+alpha*(target-oldQ);if(traceEvery&&t%traceEvery===0)updates.push({oldQ,target,maxNext:max,newQ:q[index],alpha,gamma});}
    if(traceEvery&&t%traceEvery===0)rows.push({step:m.t,states,actions:a.slice(),executedIndices:[x,y],previousPrices:m.previousPrices.slice(),prices:r.prices,profits:r.profits,consumerSurplus:r.consumerSurplus,nextStates:ns,covered,exploration:epsilon,updates});
    m.previous=[x,y];m.previousPrices=r.prices;m.reset=[false,false];m.t++;
    count++;cs+=r.consumerSurplus;pa+=r.prices[0];pb+=r.prices[1];ra+=r.profits[0];rb+=r.profits[1];interventions+=((x!==a[0])+(y!==a[1]))/2;
    if(count===binSize||t===steps-1){bins.push({endStep:m.t,rounds:count,priceA:pa/count,priceB:pb/count,profitA:ra/count,profitB:rb/count,consumerSurplus:cs/count,interventions:interventions/count});cs=pa=pb=ra=rb=count=interventions=0;}
  }
  return {bins,rows};
}
