// Separately frozen refinement diagnostics. No training or inference services.
import {outcome,continuousBenchmarks} from './robust-market.js';

export const MESH_SIZES=Object.freeze([11,15,31,61,121,241,481,961,1921]);
export function uniformPrices(lo,hi,n){
  if(!(Number.isFinite(lo)&&Number.isFinite(hi)&&lo<hi&&Number.isInteger(n)&&n>=3))throw Error('Invalid mesh');
  return Array.from({length:n},(_,i)=>lo+(hi-lo)*i/(n-1));
}
export function discreteUpperMap(prices,economy,epsilon){
  if(!prices.every((p,i)=>Number.isFinite(p)&&(!i||p>prices[i-1]))||!(epsilon>=0))throw Error('Invalid price grid/tolerance');
  const n=prices.length,rows=[],upper=[];
  for(let j=0;j<n;j++){
    const values=new Map(),profit=i=>{if(!values.has(i))values.set(i,outcome([prices[i],prices[j]],economy).profits[0]);return values.get(i);};
    // Unimodality follows from the analytic logit first-order condition.
    let lo=0,hi=n-1;
    while(lo<hi){const mid=Math.floor((lo+hi)/2);if(profit(mid+1)>profit(mid))lo=mid+1;else hi=mid;}
    const best=lo,bestProfit=profit(best),allowance=epsilon+1e-12;
    lo=best;hi=n-1;
    while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(bestProfit-profit(mid)<=allowance)lo=mid;else hi=mid-1;}
    const u=lo;
    rows.push({rival:j,bestIndex:best,bestProfit,upperIndex:u,upperProfit:profit(u),nextProfit:u+1<n?profit(u+1):null,bestLeftProfit:best?profit(best-1):null,bestRightProfit:best+1<n?profit(best+1):null});
    upper.push(u);
  }
  return {upper,rows,monotone:upper.every((u,j)=>!j||u>=upper[j-1]),comparisonAllowance:epsilon+1e-12};
}
export function fixedDestinations(upper){
  const n=upper.length;
  if(!upper.every((u,j)=>Number.isInteger(u)&&u>=0&&u<n&&(!j||u>=upper[j-1])))throw Error('Monotone upper map required');
  const fixed=new Array(n).fill(-1),steps=new Array(n).fill(-1);
  for(let i=0;i<n;i++){
    if(fixed[i]>=0)continue;
    const path=[],seen=new Set();let at=i;
    while(fixed[at]<0&&upper[at]!==at){if(seen.has(at))throw Error('Unexpected nontrivial scalar cycle');seen.add(at);path.push(at);at=upper[at];}
    if(fixed[at]<0){fixed[at]=at;steps[at]=0;}
    for(const j of path.reverse()){fixed[j]=fixed[upper[j]];steps[j]=steps[upper[j]]+1;}
  }
  return {fixed,steps,fixedPoints:upper.flatMap((u,j)=>u===j?[j]:[])};
}
export function nearestIndex(prices,p){return prices.reduce((k,v,i)=>Math.abs(v-p)<Math.abs(prices[k]-p)-1e-14?i:k,0);}
export function analyzeMesh({economy,epsilon,lo,hi,n,targets=[]}){
  const prices=uniformPrices(lo,hi,n),map=discreteUpperMap(prices,economy,epsilon),benchmarks=continuousBenchmarks(economy),cap=nearestIndex(prices,benchmarks.nashPrice),capFloor=outcome([prices[cap],prices[cap]],economy).consumerSurplus;
  const result={n,prices,epsilon,declaredEndpointPrices:[lo,hi],actualEndpointPrices:[prices[0],prices.at(-1)],spacing:(hi-lo)/(n-1),map,capIndex:cap,ownPermanentCapFloor:capFloor,continuousNashPriceDiagnostic:benchmarks.nashPrice,numericScope:'Binary64 numerical diagnostic; not interval-certified real arithmetic'};
  if(!map.monotone)return {...result,status:'unresolved-upper-map-nonmonotone',destinations:null,welfare:null,targets:targets.map(t=>({label:t.label,requestedTarget:t.requestedTarget,actualGuaranteedThreshold:t.actualGuaranteedThreshold,status:'unresolved-upper-map-nonmonotone',allStateFailingTail:null,alreadySafe:null,capCertifiedDiagnostic:null}))};
  const destinations=fixedDestinations(map.upper),minFixed=Math.min(...destinations.fixed),maxFixed=Math.max(...destinations.fixed),worst=outcome([prices[maxFixed],prices[maxFixed]],economy),best=outcome([prices[minFixed],prices[minFixed]],economy),capFixed=Math.max(...destinations.fixed.slice(0,cap+1)),afterCap=outcome([prices[capFixed],prices[capFixed]],economy);
  const anchorTailIndex=destinations.fixed[cap],anchorTailCS=outcome([prices[anchorTailIndex],prices[anchorTailIndex]],economy).consumerSurplus;
  return {...result,status:'monotone-order-envelope',destinations,welfare:{minimumAcrossStartingStates:worst.consumerSurplus,maximumAcrossStartingStates:best.consumerSurplus,spread:best.consumerSurplus-worst.consumerSurplus,oneRoundCapWorst:afterCap.consumerSurplus,capTailIndex:capFixed,anchorTailIndex,anchorTailCS,globalWorstIndex:maxFixed,lowestFixedIndex:minFixed,maximumEntrySteps:Math.max(...destinations.steps),worstStationaryProfits:worst.profits},targets:targets.map(t=>({label:t.label,requestedTarget:t.requestedTarget,actualGuaranteedThreshold:t.actualGuaranteedThreshold,allStateFailingTail:best.consumerSurplus<t.actualGuaranteedThreshold,alreadySafe:worst.consumerSurplus>=t.actualGuaranteedThreshold,capCertifiedDiagnostic:afterCap.consumerSurplus>=t.actualGuaranteedThreshold}))};
}
