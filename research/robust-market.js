// Configurable local two-firm logit experiment; no external inference or services.
export const BASE=Object.freeze({quality:2,cost:1,mu:.25,buyers:100,outsideQuality:0});
export const ECONOMIES=Object.freeze([
 {id:'base',...BASE}, {id:'scale0.5',...BASE,mu:.5},
 {id:'lower-quality',...BASE,quality:1.5}, {id:'lowcost',...BASE,cost:.6},
]);
export function outcome(prices,economy=BASE){
 const {quality,cost,mu,buyers,outsideQuality}=economy;
 if(prices.length!==2||prices.some(x=>!Number.isFinite(x)||x<0)||!(mu>0&&buyers>0))throw Error('Invalid economy/prices');
 const z=prices.map(p=>(quality-p-outsideQuality)/mu),m=Math.max(0,...z),w=z.map(v=>Math.exp(v-m)),den=Math.exp(-m)+w[0]+w[1],quantities=w.map(v=>buyers*v/den),profits=quantities.map((q,f)=>q*(prices[f]-cost)),consumerSurplus=buyers*mu*(m+Math.log(den));
 return {prices:prices.slice(),quantities,profits,consumerSurplus,totalSurplus:consumerSurplus+profits[0]+profits[1]};
}
function root(fn,lo,hi){if(!(fn(lo)>0&&fn(hi)<0))throw Error('Root not bracketed');for(let i=0;i<100;i++){const mid=(lo+hi)/2;if(fn(mid)>0)lo=mid;else hi=mid;}return (lo+hi)/2;}
export function continuousBenchmarks(e=BASE){
 const hi=Math.max(e.quality,e.cost)+20*e.mu+2,derivative=(p,joint)=>1-(p-e.cost)*(1-(joint?2:1)*outcome([p,p],e).quantities[0]/e.buyers)/e.mu;
 const nashPrice=root(p=>derivative(p,false),e.cost,hi),jointPrice=root(p=>derivative(p,true),e.cost,hi);
 return {nashPrice,jointPrice,nash:outcome([nashPrice,nashPrice],e),joint:outcome([jointPrice,jointPrice],e)};
}
export function gridPrices(n=15,e=BASE){if(!Number.isInteger(n)||n<3||n>51)throw Error('Invalid grid');const {nashPrice,jointPrice}=continuousBenchmarks(e),d=jointPrice-nashPrice,lo=nashPrice-.1*d,hi=jointPrice+.1*d;return Array.from({length:n},(_,i)=>lo+(hi-lo)*i/(n-1));}
export function gridBenchmarks(prices,e=BASE){
 const n=prices.length,profits=prices.map(p=>prices.map(q=>outcome([p,q],e).profits[0])),bestResponses=prices.map((_,j)=>{let a=0;for(let i=1;i<n;i++)if(profits[i][j]>profits[a][j]+1e-12)a=i;return a;});
 const equilibria=[];let jointMaximum={indices:[0,0],profit:-Infinity};for(let i=0;i<n;i++)for(let j=0;j<n;j++){if(profits[bestResponses[j]][j]-profits[i][j]<=1e-12&&profits[bestResponses[i]][i]-profits[j][i]<=1e-12)equilibria.push([i,j]);const profit=profits[i][j]+profits[j][i];if(profit>jointMaximum.profit)jointMaximum={indices:[i,j],profit};}
 return {prices,profits,bestResponses,equilibria,jointMaximum};
}
const next=r=>{r.value=(Math.imul(r.value,1664525)+1013904223)>>>0;return r.value/4294967296;};
const nearest=(prices,p)=>prices.reduce((k,v,i)=>Math.abs(v-p)<Math.abs(prices[k]-p)-1e-14?i:k,0);
export function createMarket({seed=1,gridSize=15,gamma=.95,alpha=.15,beta=4e-6,memory=true,economy=BASE}={}){
 if(!Number.isInteger(seed)||seed<0||!(gamma>=0&&gamma<1&&alpha>0&&alpha<=1&&beta>=0))throw Error('Invalid learner');
 const prices=gridPrices(gridSize,economy),n=prices.length,states=memory?n*n+1:1,initial=prices.map(price=>prices.reduce((v,p)=>{const a=Math.exp((economy.quality-price-economy.outsideQuality)/economy.mu),b=Math.exp((economy.quality-p-economy.outsideQuality)/economy.mu);return v+economy.buyers*(price-economy.cost)*a/(1+a+b);},0)/n/(1-gamma)),q=Array.from({length:2},()=>{const a=new Float64Array(states*n);for(let s=0;s<states;s++)a.set(initial,s*n);return a;}),rng=[{value:(seed^0xa5a5a5a5)>>>0},{value:(seed^0x5a5a5a5a)>>>0}],previous=rng.map(r=>Math.floor(next(r)*n));
 return {config:{seed,gridSize,gamma,alpha,beta,memory,economy:structuredClone(economy)},prices,q,rng,t:0,previous,previousPrices:previous.map(i=>prices[i]),reset:[false,false]};
}
export const checkpoint=m=>({...structuredClone(m),q:m.q.map(a=>Array.from(a))});
export const restore=c=>({...structuredClone(c),q:c.q.map(a=>Float64Array.from(a))});
export const cloneMarket=m=>restore(checkpoint(m));
const cache=new Map();
export function tables(m,treatment={}){
 const e=m.config.economy||BASE,key=JSON.stringify([m.prices,e,treatment]);if(cache.has(key))return cache.get(key);
 const prices=m.prices,n=prices.length,type=treatment.type||'none',epsilon=treatment.epsilon??0,map=[],sets=[],profits=gridBenchmarks(prices,e).profits,cap=nearest(prices,continuousBenchmarks(e).nashPrice),tensor=[];
 if(!['none','cap','guard'].includes(type)||!(epsilon>=0))throw Error('Invalid treatment');
 for(let j=0;j<n;j++){const best=Math.max(...profits.map(row=>row[j])),allowed=prices.map((_,i)=>best-profits[i][j]<=epsilon+1e-12?i:-1).filter(i=>i>=0),row=[];for(let a=0;a<n;a++){let k=a;if(type==='cap')k=Math.min(a,cap);else if(type==='guard')k=allowed.reduce((v,i)=>Math.abs(i-a)<Math.abs(v-a)?i:v,allowed[0]);row.push(k);}map.push(row);sets.push([...new Set(row)].sort((a,b)=>a-b));}
 for(const p of prices)for(const q of prices)tensor.push(outcome([p,q],e));const result={map,sets,tensor};cache.set(key,result);return result;
}
const entropy=counts=>{const total=counts.reduce((a,b)=>a+b,0);return total?counts.reduce((s,c)=>s-(c?c/total*Math.log2(c/total):0),0):0;};
// Auditable general path, also used for evaluation with a complete 4-byte trace.
export function advance(m,steps,{treatment={},mode='proposal',learn=true,explorationRate=null,compactTrace=false,traceEvery=0,binSize=10000}={}){
 if(!Number.isInteger(steps)||steps<0||!['proposal','aware'].includes(mode))throw Error('Invalid run');
 const n=m.prices.length,{alpha,gamma,beta,memory}=m.config,{map,sets,tensor}=tables(m,treatment),all=Array.from({length:n},(_,i)=>i),pc=[new Array(n).fill(0),new Array(n).fill(0)],ec=structuredClone(pc),conditional=Array.from({length:2},()=>Array.from({length:n},()=>new Array(n).fill(0))),trace=compactTrace?new Uint8Array(steps*4):null;
 const totals={consumerSurplus:0,profitA:0,profitB:0,priceA:0,priceB:0,retention:0,feasibleCount:0,feasibleFraction:0,feasibleSpan:0,singletonFraction:0,adjustment:0},rows=[],bins=[];let bin={...totals},count=0;
 for(let t=0;t<steps;t++){
  const previous=m.previous.slice(),states=[0,1].map(f=>memory?(m.reset[f]?n*n:previous[f]*n+previous[1-f]):0),a=[0,0],epsilon=explorationRate??Math.exp(-beta*m.t);
  for(let f=0;f<2;f++){const choices=mode==='aware'?sets[previous[1-f]]:all,off=states[f]*n,q=m.q[f];a[f]=choices[0];for(const k of choices)if(q[off+k]>q[off+a[f]])a[f]=k;const u=next(m.rng[f]),v=next(m.rng[f]);if(u<epsilon)a[f]=choices[Math.floor(v*choices.length)];}
  const x=[map[previous[1]][a[0]],map[previous[0]][a[1]]],r=tensor[x[0]*n+x[1]],ns=[memory?x[0]*n+x[1]:0,memory?x[1]*n+x[0]:0],updates=[];
  for(let f=0;f<2;f++){const choices=mode==='aware'?sets[x[1-f]]:all,off=ns[f]*n,q=m.q[f];let max=-Infinity;for(const k of choices)if(q[off+k]>max)max=q[off+k];const index=states[f]*n+a[f],oldQ=q[index],target=r.profits[f]+gamma*max;if(learn)q[index]=oldQ+alpha*(target-oldQ);if(traceEvery&&t%traceEvery===0)updates.push({index,oldQ,target,maxNext:max,newQ:q[index]});pc[f][a[f]]++;ec[f][x[f]]++;conditional[f][previous[1-f]][x[f]]++;}
  if(trace)trace.set([a[0],a[1],x[0],x[1]],t*4);
  const choices=[sets[previous[1]],sets[previous[0]]],v={consumerSurplus:r.consumerSurplus,profitA:r.profits[0],profitB:r.profits[1],priceA:r.prices[0],priceB:r.prices[1],retention:((a[0]===x[0])+(a[1]===x[1]))/2,feasibleCount:(choices[0].length+choices[1].length)/2,feasibleFraction:(choices[0].length+choices[1].length)/(2*n),feasibleSpan:choices.reduce((s,c)=>s+m.prices[c.at(-1)]-m.prices[c[0]],0)/2,singletonFraction:choices.filter(c=>c.length===1).length/2,adjustment:(Math.abs(m.prices[a[0]]-r.prices[0])+Math.abs(m.prices[a[1]]-r.prices[1]))/2};
  for(const k of Object.keys(totals)){totals[k]+=v[k];bin[k]+=v[k];}
  if(traceEvery&&t%traceEvery===0)rows.push({step:m.t,localStep:t,states,previous,actions:a.slice(),executed:x.slice(),profits:r.profits,consumerSurplus:r.consumerSurplus,nextStates:ns,exploration:epsilon,updates});
  m.previous=x;m.previousPrices=r.prices.slice();m.reset=[false,false];m.t++;count++;
  if(count===binSize||t===steps-1){bins.push({endStep:m.t,rounds:count,...Object.fromEntries(Object.entries(bin).map(([k,v])=>[k,v/count]))});bin=Object.fromEntries(Object.keys(bin).map(k=>[k,0]));count=0;}
 }
 const conditionalEntropy=conditional.reduce((sum,firm)=>sum+firm.reduce((s,c)=>s+c.reduce((a,b)=>a+b,0)/(steps||1)*entropy(c),0),0)/2;
 return {metrics:{rounds:steps,...Object.fromEntries(Object.entries(totals).map(([k,v])=>[k,steps?v/steps:0])),proposalEntropy:(entropy(pc[0])+entropy(pc[1]))/2,executionEntropy:(entropy(ec[0])+entropy(ec[1]))/2,conditionalExecutionEntropy:conditionalEntropy,proposalCounts:pc,executionCounts:ec,conditionalExecutionCounts:conditional},rows,bins,trace};
}
// Same choices, Q arithmetic, random draws and timing as general path; no diagnostics.
export function train(m,steps,{treatment={},mode='proposal',binSize=10000}={}){
 const n=m.prices.length,{alpha,gamma,beta,memory}=m.config,{map,sets,tensor}=tables(m,treatment),all=Array.from({length:n},(_,i)=>i),bins=[];let cs=0,pa=0,pb=0,ra=0,rb=0,count=0;
 for(let t=0;t<steps;t++){
  const prev=m.previous,states=[memory?(m.reset[0]?n*n:prev[0]*n+prev[1]):0,memory?(m.reset[1]?n*n:prev[1]*n+prev[0]):0],a=[0,0],epsilon=Math.exp(-beta*m.t);
  for(let f=0;f<2;f++){const choices=mode==='aware'?sets[prev[1-f]]:all,off=states[f]*n,q=m.q[f];a[f]=choices[0];for(const k of choices)if(q[off+k]>q[off+a[f]])a[f]=k;const u=next(m.rng[f]),v=next(m.rng[f]);if(u<epsilon)a[f]=choices[Math.floor(v*choices.length)];}
  const x=[map[prev[1]][a[0]],map[prev[0]][a[1]]],r=tensor[x[0]*n+x[1]],ns=[memory?x[0]*n+x[1]:0,memory?x[1]*n+x[0]:0];
  for(let f=0;f<2;f++){const q=m.q[f],off=ns[f]*n,choices=mode==='aware'?sets[x[1-f]]:all;let max=-Infinity;for(const k of choices)if(q[off+k]>max)max=q[off+k];const index=states[f]*n+a[f];q[index]+=alpha*(r.profits[f]+gamma*max-q[index]);}
  m.previous=x;m.previousPrices=r.prices.slice();m.reset=[false,false];m.t++;count++;cs+=r.consumerSurplus;pa+=r.prices[0];pb+=r.prices[1];ra+=r.profits[0];rb+=r.profits[1];
  if(count===binSize||t===steps-1){bins.push({endStep:m.t,rounds:count,consumerSurplus:cs/count,priceA:pa/count,priceB:pb/count,profitA:ra/count,profitB:rb/count});cs=pa=pb=ra=rb=count=0;}
 }
 return {bins};
}
