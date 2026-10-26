// Prospective extension, adapted from learning-market.js train/advance.
// Separate learner semantics; original study and engine remain untouched.
import {outcome} from './replacement-market.js';
import {treatmentMap} from './learning-market.js';
export const ARMS=[
 {name:'none',treatment:{},mode:'proposal'},
 {name:'cap-proposal',treatment:{type:'cap'},mode:'proposal'},
 {name:'cap-aware',treatment:{type:'cap'},mode:'aware'},
 {name:'guard-proposal',treatment:{type:'guard',epsilon:.1},mode:'proposal'},
 {name:'guard-executed',treatment:{type:'guard',epsilon:.1},mode:'executed'},
 {name:'guard-aware',treatment:{type:'guard',epsilon:.1},mode:'aware'},
];
const next=r=>{r.value=(Math.imul(r.value,1664525)+1013904223)>>>0;return r.value/4294967296;};
const entropy=counts=>{const total=counts.reduce((a,b)=>a+b,0);return total?counts.reduce((s,c)=>s-(c?c/total*Math.log2(c/total):0),0):0;};
const cache=new Map();
function tables(prices,treatment){
 const key=JSON.stringify([prices,treatment]);if(cache.has(key))return cache.get(key);
 const {map}=treatmentMap(prices,treatment),n=prices.length;
 const sets=map.map(row=>[...new Set(row)].sort((a,b)=>a-b));
 const tensor=[];for(const p of prices)for(const q of prices)tensor.push(outcome([p,q]));
 const result={map,sets,tensor};cache.set(key,result);return result;
}
export function creditAdvance(m,steps,{treatment={},mode='proposal',learn=true,explorationRate=null,traceEvery=0,binSize=10000,compactTrace=false}={}){
 if(!Number.isInteger(steps)||steps<0||!['proposal','executed','aware'].includes(mode))throw Error('Invalid credit run');
 const n=m.prices.length,{alpha,gamma,beta,memory}=m.config,{map,sets,tensor}=tables(m.prices,treatment);
 const all=Array.from({length:n},(_,i)=>i),rows=[],bins=[],pc=[new Array(n).fill(0),new Array(n).fill(0)],ec=[new Array(n).fill(0),new Array(n).fill(0)];
 const trace=compactTrace?new Uint8Array(steps*4):null;
 const totals={consumerSurplus:0,profitA:0,profitB:0,priceA:0,priceB:0,retention:0,feasibleFraction:0,feasibleSpan:0,adjustment:0};
 let bin={...totals},count=0;
 for(let t=0;t<steps;t++){
  const previous=m.previous.slice(),states=[0,1].map(f=>memory?(m.reset[f]?n*n:previous[f]*n+previous[1-f]):0),a=[0,0],epsilon=explorationRate??Math.exp(-beta*m.t);
  for(let f=0;f<2;f++){
   const choices=mode==='aware'?sets[previous[1-f]]:all,off=states[f]*n,q=m.q[f];a[f]=choices[0];
   for(const k of choices)if(q[off+k]>q[off+a[f]])a[f]=k;
   const u=next(m.rng[f]),v=next(m.rng[f]);if(u<epsilon)a[f]=choices[Math.floor(v*choices.length)];
  }
  const x=[map[previous[1]][a[0]],map[previous[0]][a[1]]],r=tensor[x[0]*n+x[1]],ns=[memory?x[0]*n+x[1]:0,memory?x[1]*n+x[0]:0],updates=[];
  for(let f=0;f<2;f++){
   const choices=mode==='aware'?sets[x[1-f]]:all,off=ns[f]*n,q=m.q[f];let max=-Infinity;for(const k of choices)if(q[off+k]>max)max=q[off+k];
   const credited=mode==='proposal'?a[f]:x[f],index=states[f]*n+credited,oldQ=q[index],target=r.profits[f]+gamma*max;if(learn)q[index]=oldQ+alpha*(target-oldQ);
   if(traceEvery&&t%traceEvery===0)updates.push({credited,index,oldQ,target,maxNext:max,newQ:q[index],alpha,gamma});
   pc[f][a[f]]++;ec[f][x[f]]++;
  }
  if(trace)trace.set([a[0],a[1],x[0],x[1]],t*4);
  const choices=previous.map((_,f)=>sets[previous[1-f]]),v={consumerSurplus:r.consumerSurplus,profitA:r.profits[0],profitB:r.profits[1],priceA:r.prices[0],priceB:r.prices[1],retention:((a[0]===x[0])+(a[1]===x[1]))/2,feasibleFraction:(choices[0].length+choices[1].length)/(2*n),feasibleSpan:choices.reduce((s,c)=>s+m.prices[c.at(-1)]-m.prices[c[0]],0)/2,adjustment:(Math.abs(m.prices[a[0]]-r.prices[0])+Math.abs(m.prices[a[1]]-r.prices[1]))/2};
  for(const key of Object.keys(totals)){totals[key]+=v[key];bin[key]+=v[key];}
  if(traceEvery&&t%traceEvery===0)rows.push({step:m.t,localStep:t,states,actions:a.slice(),executed:x.slice(),previous,prices:r.prices,profits:r.profits,consumerSurplus:r.consumerSurplus,nextStates:ns,exploration:epsilon,updates});
  m.previous=x;m.previousPrices=r.prices.slice();m.reset=[false,false];m.t++;count++;
  if(count===binSize||t===steps-1){bins.push({endStep:m.t,rounds:count,...Object.fromEntries(Object.entries(bin).map(([k,v])=>[k,v/count]))});bin=Object.fromEntries(Object.keys(bin).map(k=>[k,0]));count=0;}
 }
 return {metrics:{rounds:steps,...Object.fromEntries(Object.entries(totals).map(([k,v])=>[k,steps?v/steps:0])),proposalEntropy:(entropy(pc[0])+entropy(pc[1]))/2,executionEntropy:(entropy(ec[0])+entropy(ec[1]))/2,proposalCounts:pc,executionCounts:ec},rows,bins,trace};
}
// Fast path: same choices/update/random draws as creditAdvance, no per-step statistics.
export function creditTrain(m,steps,{treatment={},mode='proposal',binSize=10000}={}){
 const n=m.prices.length,{alpha,gamma,beta,memory}=m.config,{map,sets,tensor}=tables(m.prices,treatment),all=Array.from({length:n},(_,i)=>i),bins=[];
 let cs=0,pa=0,pb=0,profitA=0,profitB=0,retained=0,count=0;
 for(let t=0;t<steps;t++){
  const prev=m.previous,states=[memory?(m.reset[0]?n*n:prev[0]*n+prev[1]):0,memory?(m.reset[1]?n*n:prev[1]*n+prev[0]):0],a=[0,0],epsilon=Math.exp(-beta*m.t);
  for(let f=0;f<2;f++){const choices=mode==='aware'?sets[prev[1-f]]:all,off=states[f]*n,q=m.q[f];a[f]=choices[0];for(const k of choices)if(q[off+k]>q[off+a[f]])a[f]=k;const u=next(m.rng[f]),v=next(m.rng[f]);if(u<epsilon)a[f]=choices[Math.floor(v*choices.length)];}
  const x=[map[prev[1]][a[0]],map[prev[0]][a[1]]],r=tensor[x[0]*n+x[1]],ns=[memory?x[0]*n+x[1]:0,memory?x[1]*n+x[0]:0];
  for(let f=0;f<2;f++){const q=m.q[f],off=ns[f]*n,choices=mode==='aware'?sets[x[1-f]]:all;let max=-Infinity;for(const k of choices)if(q[off+k]>max)max=q[off+k];const index=states[f]*n+(mode==='proposal'?a[f]:x[f]);q[index]+=alpha*(r.profits[f]+gamma*max-q[index]);}
  m.previous=x;m.previousPrices=r.prices.slice();m.reset=[false,false];m.t++;count++;cs+=r.consumerSurplus;pa+=r.prices[0];pb+=r.prices[1];profitA+=r.profits[0];profitB+=r.profits[1];retained+=((a[0]===x[0])+(a[1]===x[1]))/2;
  if(count===binSize||t===steps-1){bins.push({endStep:m.t,rounds:count,consumerSurplus:cs/count,priceA:pa/count,priceB:pb/count,profitA:profitA/count,profitB:profitB/count,retention:retained/count});cs=pa=pb=profitA=profitB=retained=count=0;}
 }
 return {bins};
}
