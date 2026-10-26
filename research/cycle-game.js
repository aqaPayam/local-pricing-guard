// Finite fully coordinated pricing envelope. No learners, API calls or equilibrium claim.
import {createMarket,tables,continuousBenchmarks,gridBenchmarks} from './robust-market.js';

export function stronglyConnected(adjacency){
 const n=adjacency.length,index=new Int32Array(n).fill(-1),low=new Int32Array(n),on=new Uint8Array(n),stack=[],components=[];let clock=0;
 function visit(v){index[v]=low[v]=clock++;stack.push(v);on[v]=1;for(const w of adjacency[v]){if(index[w]===-1){visit(w);low[v]=Math.min(low[v],low[w]);}else if(on[w])low[v]=Math.min(low[v],index[w]);}if(low[v]===index[v]){const nodes=[];let w;do{w=stack.pop();on[w]=0;nodes.push(w);}while(w!==v);components.push(nodes.sort((a,b)=>a-b));}}
 for(let v=0;v<n;v++)if(index[v]===-1)visit(v);components.sort((a,b)=>a[0]-b[0]);const componentByState=new Int32Array(n);components.forEach((c,i)=>c.forEach(v=>componentByState[v]=i));return {components,componentByState:Array.from(componentByState)};
}
function localEdges(adjacency,weights,nodes){const index=new Map(nodes.map((v,i)=>[v,i])),edges=[];for(const u of nodes)for(let k=0;k<adjacency[u].length;k++){const v=adjacency[u][k];if(index.has(v))edges.push({u:index.get(u),v:index.get(v),weight:weights[u][k]});}return edges;}
export function karpMean(n,edges){
 const dp=Array.from({length:n+1},()=>new Float64Array(n).fill(Infinity));dp[0].fill(0);
 for(let k=1;k<=n;k++)for(const {u,v,weight}of edges){const d=dp[k-1][u]+weight;if(d<dp[k][v])dp[k][v]=d;}
 let answer=Infinity;for(let v=0;v<n;v++){let maximum=-Infinity;for(let k=0;k<n;k++)maximum=Math.max(maximum,(dp[n][v]-dp[k][v])/(n-k));answer=Math.min(answer,maximum);}if(!Number.isFinite(answer))throw Error('Karp requires a cyclic strongly connected graph');return answer;
}
function normalizeCycle(cycle){let p=0;for(let i=1;i<cycle.length;i++)if(cycle[i]<cycle[p])p=i;return [...cycle.slice(p),...cycle.slice(0,p)];}
function extractNegativeCycle(n,edges,threshold){
 const d=new Float64Array(n),parent=new Int32Array(n).fill(-1);let changed=-1;
 for(let k=0;k<n;k++){changed=-1;for(const {u,v,weight}of edges){const candidate=d[u]+weight-threshold;if(candidate<d[v]){d[v]=candidate;parent[v]=u;changed=v;}}}
 if(changed<0)throw Error('No shifted negative cycle found');let v=changed;for(let k=0;k<n;k++){v=parent[v];if(v<0)throw Error('Incomplete cycle predecessor');}const backwards=[v];let x=parent[v];while(x!==v){if(x<0||backwards.length>n)throw Error('Invalid cycle predecessor');backwards.push(x);x=parent[x];}return backwards.reverse();
}
export function certifyComponent(adjacency,weights,nodes,{deltaScale=1e-10,gapScale=1e-6}={}){
 const n=nodes.length,edges=localEdges(adjacency,weights,nodes);if(!edges.length)throw Error('No cyclic edges');const scale=edges.reduce((maximum,e)=>Math.max(maximum,Math.abs(e.weight)),1),delta=deltaScale*scale,karp=karpMean(n,edges),localCycle=extractNegativeCycle(n,edges,karp+delta),potential=new Float64Array(n);
 for(let k=0;k<n-1;k++){let changed=false;for(const {u,v,weight}of edges){const candidate=potential[u]+weight-(karp-delta);if(candidate<potential[v]){potential[v]=candidate;changed=true;}}if(!changed)break;}
 const edgeMinimum=edges.reduce((minimum,{u,v,weight})=>Math.min(minimum,weight+potential[u]-potential[v]),Infinity),lowerBound=Math.min(karp-delta,edgeMinimum)-delta,cycle=normalizeCycle(localCycle.map(v=>nodes[v])),lookup=new Map(edges.map(e=>[`${e.u},${e.v}`,e.weight])),index=new Map(nodes.map((v,i)=>[v,i])),cycleWeights=cycle.map((v,i)=>lookup.get(`${index.get(v)},${index.get(cycle[(i+1)%cycle.length])}`)),upperBound=cycleWeights.reduce((a,b)=>a+b,0)/cycle.length,minimumEdgeResidual=edges.reduce((minimum,{u,v,weight})=>Math.min(minimum,weight-lowerBound+potential[u]-potential[v]),Infinity),numericGap=upperBound-lowerBound;
 if(cycleWeights.some(x=>!Number.isFinite(x))||minimumEdgeResidual<0||numericGap<0||numericGap>gapScale*scale)throw Error(`Numerical cycle certificate failed: residual ${minimumEdgeResidual}, gap ${numericGap}`);
 return {nodes,karpMean:karp,lowerBound,upperBound,delta,scale,potential:Array.from(potential),minimumEdgeResidual,numericGap,cycle,cycleWeights,edgeCount:edges.length};
}
export function prefixPath(adjacency,start,target){
 const parent=new Int32Array(adjacency.length).fill(-1),queue=[start];parent[start]=start;for(let i=0;i<queue.length&&parent[target]===-1;i++)for(const v of adjacency[queue[i]])if(parent[v]===-1){parent[v]=queue[i];queue.push(v);}if(parent[target]===-1)throw Error('Requested witness cycle is unreachable');const path=[target];while(path.at(-1)!==start)path.push(parent[path.at(-1)]);return path.reverse();
}
// Generic weighted directed-graph solver, also exercised against brute-force cycles.
export function solveGraph(adjacency,weights,options={}){
 const n=adjacency.length;if(weights.length!==n||adjacency.some((row,u)=>row.length!==weights[u].length||new Set(row).size!==row.length||row.some(v=>!Number.isInteger(v)||v<0||v>=n))||weights.some(row=>row.some(w=>!Number.isFinite(w))))throw Error('Invalid finite weighted graph');
 const {components,componentByState}=stronglyConnected(adjacency),certificates=components.map(nodes=>nodes.length>1||adjacency[nodes[0]].includes(nodes[0])?certifyComponent(adjacency,weights,nodes,options):null),successors=components.map(()=>new Set());for(let u=0;u<n;u++)for(const v of adjacency[u])if(componentByState[u]!==componentByState[v])successors[componentByState[u]].add(componentByState[v]);
 const reachCache=new Map();function reachable(c){if(reachCache.has(c))return reachCache.get(c);const result=new Set(certificates[c]?[c]:[]);for(const next of successors[c])for(const d of reachable(next))result.add(d);reachCache.set(c,result);return result;}
 const starts=[];for(let state=0;state<n;state++){const candidates=[...reachable(componentByState[state])].sort((a,b)=>certificates[a].upperBound-certificates[b].upperBound||a-b);if(!candidates.length){starts.push({state,infinitePath:false});continue;}const chosen=candidates[0],certificate=certificates[chosen],lowerBound=Math.min(...candidates.map(c=>certificates[c].lowerBound));starts.push({state,infinitePath:true,reachableCyclicComponents:candidates,chosenComponent:chosen,lowerBound,upperBound:certificate.upperBound,numericGap:certificate.upperBound-lowerBound,prefix:prefixPath(adjacency,state,certificate.cycle[0]),cycle:certificate.cycle});}
 const cyclic=certificates.flatMap((c,i)=>c?[i]:[]),best=cyclic.slice().sort((a,b)=>certificates[a].upperBound-certificates[b].upperBound||a-b)[0],universal=best===undefined?null:{chosenComponent:best,lowerBound:Math.min(...cyclic.map(c=>certificates[c].lowerBound)),upperBound:certificates[best].upperBound,cycle:certificates[best].cycle};return {components,componentByState,certificates,starts,universal};
}
export function pricingGame(scenario,type){
 if(!['none','cap','guard'].includes(type))throw Error('Unknown controller');const m=createMarket({gridSize:scenario.gridSize,economy:scenario.economy}),treatment={type,...(type==='guard'?{epsilon:scenario.epsilon}:{})},{sets,tensor,map}=tables(m,treatment),n=m.prices.length,adjacency=type==='guard'?Array.from({length:n*n},(_,state)=>{const i=Math.floor(state/n),j=state%n,targets=[];for(const a of sets[j])for(const b of sets[i])targets.push(a*n+b);return targets;}):null;
 return {scenario:scenario.id,type,n,prices:m.prices,treatment,sets,map,adjacency,rewards:tensor.map(r=>({prices:r.prices,consumerSurplus:r.consumerSurplus,profitA:r.profits[0],profitB:r.profits[1],jointProfit:r.profits[0]+r.profits[1]})),continuous:continuousBenchmarks(scenario.economy),finite:gridBenchmarks(m.prices,scenario.economy)};
}
export function solvePricing(game,objective,options={}){
 if(!['minCS','maxJointProfit'].includes(objective))throw Error('Unknown objective');const reward=r=>objective==='minCS'?r.consumerSurplus:-r.jointProfit;
 if(game.adjacency){const weights=game.adjacency.map(row=>row.map(v=>reward(game.rewards[v])));return {method:'SCC-Karp/Bellman-Ford numeric primal-dual',...solveGraph(game.adjacency,weights,options)};}
 const target=[];for(const a of game.sets[0])for(const b of game.sets[0])target.push(a*game.n+b);let best=target[0];for(const v of target)if(reward(game.rewards[v])<reward(game.rewards[best]))best=v;const value=reward(game.rewards[best]),starts=game.rewards.map((_,state)=>({state,infinitePath:true,chosenComponent:0,lowerBound:value,upperBound:value,numericGap:0,prefix:state===best?[state]:[state,best],cycle:[best]}));
 return {method:'complete-support closed form',support:target,potential:new Array(game.n**2).fill(0),minimumEdgeResidual:0,starts,universal:{chosenComponent:0,lowerBound:value,upperBound:value,cycle:[best]},certificates:[{nodes:target,lowerBound:value,upperBound:value,cycle:[best],cycleWeights:[value],potential:new Array(target.length).fill(0),numericGap:0,edgeCount:target.length**2}]};
}
export function economicWitness(game,result){
 const rows=result.cycle.map(state=>game.rewards[state]),average=key=>rows.reduce((s,r)=>s+r[key],0)/rows.length;return {states:result.cycle,pairs:result.cycle.map(state=>[Math.floor(state/game.n),state%game.n]),length:rows.length,consumerSurplus:average('consumerSurplus'),profitA:average('profitA'),profitB:average('profitB'),jointProfit:average('jointProfit'),priceA:rows.reduce((s,r)=>s+r.prices[0],0)/rows.length,priceB:rows.reduce((s,r)=>s+r.prices[1],0)/rows.length};
}
