// Structural, finite-map diagnostics. No new optimization or model inference.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

export function structuralBound(game, objective, horizons=[1,10,100,20000]) {
 const {n,sets,rewards,adjacency}=game;
 const intervals=sets.every(s=>s.length>0&&s.every((v,i)=>i===0||v===s[i-1]+1));
 const upper=sets.map(s=>s.at(-1));
 const monotoneUpper=upper.every((v,i)=>i===0||v>=upper[i-1]);
 const selfFeasible=sets.flatMap((s,j)=>s.includes(j)?[j]:[]);
 const scale=Math.max(1,...rewards.map(r=>Math.abs(r.consumerSurplus))),slack=1e-9*scale;
 let decreasingSurplus=true;
 for(let a=0;a<n;a++)for(let b=0;b<n;b++) {
  const c=rewards[a*n+b].consumerSurplus;
  if(a+1<n&&rewards[(a+1)*n+b].consumerSurplus>c)decreasingSurplus=false;
  if(b+1<n&&rewards[a*n+b+1].consumerSurplus>c)decreasingSurplus=false;
 }
 const assumptions={intervals,monotoneUpper,decreasingSurplus,nonemptySelfFeasible:selfFeasible.length>0};
 if(!Object.values(assumptions).every(Boolean))return {applicable:false,assumptions};
 const m=selfFeasible.at(-1),stationaryState=m*n+m,stationaryReward=rewards[stationaryState],
  predictedMinimum=stationaryReward.consumerSurplus,
  discrepancy=objective.universalWitness.consumerSurplus-predictedMinimum;
 if(Math.abs(discrepancy)>slack*5)throw Error('Stationary ceiling disagrees with graph witness');
 const floor=predictedMinimum-slack;
 let componentByState,components,cyclic;
 if(adjacency) {
  ({componentByState,components}=objective);
  cyclic=components.map((nodes,c)=>objective.certificates[c]!==null);
 } else {
  const support=new Set();for(const a of sets[0])for(const b of sets[0])support.add(a*n+b);
  components=[[...support]];componentByState=new Array(n*n);cyclic=[true];
  for(const s of support)componentByState[s]=0;
  for(let s=0;s<n*n;s++)if(!support.has(s)){componentByState[s]=components.length;components.push([s]);cyclic.push(false);}
 }
 const successors=components.map(()=>new Set()),deficits=components.map(()=>0);
 for(let c=0;c<components.length;c++)for(const state of components[c]) {
  const deficit=Math.max(0,floor-rewards[state].consumerSurplus);
  if(cyclic[c]&&deficit>0)throw Error('Below-ceiling state lies on a cycle');
  if(!cyclic[c]) {
   if(components[c].length!==1)throw Error('Acyclic component must be singleton');
   deficits[c]=deficit;
  }
 }
 if(adjacency) {
  for(let u=0;u<n*n;u++)for(const v of adjacency[u])if(componentByState[u]!==componentByState[v])successors[componentByState[u]].add(componentByState[v]);
 } else for(let c=1;c<components.length;c++)successors[c].add(0);
 const memo=new Array(components.length),visiting=new Set();
 function solve(c) {
  if(memo[c]!==undefined)return memo[c];
  if(visiting.has(c))throw Error('Condensation must be acyclic');
  visiting.add(c);let d=0;for(const k of successors[c])d=Math.max(d,deficits[k]+solve(k));
  visiting.delete(c);memo[c]=d;return d;
 }
 for(let c=0;c<components.length;c++)solve(c);
 const potential=componentByState.map(c=>memo[c]);let minimumAllEdgeResidual=Infinity,certificateEdgeCount=0;
 if(adjacency) {
  for(let u=0;u<n*n;u++)for(const v of adjacency[u]) {
   minimumAllEdgeResidual=Math.min(minimumAllEdgeResidual,rewards[v].consumerSurplus-floor+potential[u]-potential[v]);certificateEdgeCount++;
  }
 } else {
  for(const a of sets[0])for(const b of sets[0])minimumAllEdgeResidual=Math.min(minimumAllEdgeResidual,rewards[a*n+b].consumerSurplus-floor);
  certificateEdgeCount=n*n*sets[0].length**2;
 }
 if(minimumAllEdgeResidual < -slack*1e-3)throw Error('Finite-horizon all-edge potential certificate failed');
 const certifiedFloor=floor+Math.min(0,minimumAllEdgeResidual)-slack*1e-3;
 const certifiedMinimumAllEdgeResidual=minimumAllEdgeResidual+floor-certifiedFloor;
 const starts=componentByState.map((c,state)=>({state,component:c,totalPositiveDeficitBound:memo[c],
  finiteAverageLowerBounds:Object.fromEntries(horizons.map(T=>[T,certifiedFloor-memo[c]/T]))}));
 return {applicable:true,assumptions,selfFeasible,largestSelfFeasibleIndex:m,stationaryState,
  stationaryPrices:stationaryReward.prices,stationaryReward,predictedMinimum,graphDiscrepancy:discrepancy,
  numericalSlack:slack,structuralFloor:floor,adjustedFloor:certifiedFloor,components,componentByState,cyclic,
  successors:successors.map(s=>[...s]),componentDeficits:deficits,maximumFutureDeficit:memo,starts,
  potential,minimumAllEdgeResidual,certifiedMinimumAllEdgeResidual,certificateEdgeCount,
  maximumStartDeficit:Math.max(...memo),horizons,
  scope:'Finite known-economy maps; floating computed rewards with explicit slack. Starting previous-state reward excluded. No equilibrium or real-arithmetic interval proof.'};
}

export function runStructure(directory='research/cycle-results') {
 const output=path.join(directory,'structure.json');if(fs.existsSync(output))throw Error('Refuse overwrite of structural evidence');
 const index=JSON.parse(fs.readFileSync(path.join(directory,'index.json'))),records=[];
 for(const row of index) {
  const file=path.join(directory,row.file),bytes=fs.readFileSync(file),record=JSON.parse(bytes);
  records.push({id:record.id,caseSha256:crypto.createHash('sha256').update(bytes).digest('hex'),
   ...structuralBound(record.game,record.objectives.minCS)});
 }
 const summary={generatedAt:new Date().toISOString(),cases:records.length,applicable:records.filter(r=>r.applicable).length,
  largestDiscrepancy:Math.max(...records.filter(r=>r.applicable).map(r=>Math.abs(r.graphDiscrepancy))),records};
 fs.writeFileSync(output,JSON.stringify(summary));console.log(JSON.stringify({cases:summary.cases,applicable:summary.applicable,largestDiscrepancy:summary.largestDiscrepancy}));
 return summary;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))runStructure(process.argv[2]);
