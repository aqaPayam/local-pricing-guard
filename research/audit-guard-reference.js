// Independent prospective full-grid adapter and static anchor checker.
// Importing performs no IO, training, inherited payoff enumeration or Q reads.
// Only the accepted independent replay kernel is reused; no primary helper.
import {createHash} from 'node:crypto';
import {
  createReplay, expectedGraphClaim, expectedWindowClaims, assertForbiddenZero,
  validateReplayEndpoint,
} from './audit-matched-clock.js';

const requireThat=(condition,message)=>{if(!condition)throw Error(message);};
const digestJSON=value=>createHash('sha256').update(JSON.stringify(value),'utf8').digest('hex');
const FULL='full-grid-after-cap', PARITY='startup-guard';
const same=(a,b)=>{
  if(Object.is(a,b))return true;
  if(!a||!b||typeof a!=='object'||typeof b!=='object'||Array.isArray(a)!==Array.isArray(b))return false;
  const keys=Object.keys(a),other=Object.keys(b);
  return keys.length===other.length&&keys.every(k=>Object.hasOwn(b,k)&&same(a[k],b[k]));
};

export function referenceScientificTreatment(mode=FULL){
  requireThat(mode===FULL||mode===PARITY,'Unknown explicit reference support mode');
  return {capClock:'startup',supportMode:mode,initialCap:true,postInitialOriginalIndices:mode===FULL?'all':'original rival-dependent guard'};
}

function legalMatrix(finite,mode){
  const n=finite.prices.length,cap=Array.from({length:finite.capIndex+1},(_,a)=>a),full=Array.from({length:n},(_,a)=>a);
  return Array.from({length:5},(_,p)=>Array.from({length:n},(_,r)=>(p===0?cap:mode===FULL?full:finite.sets[r]).slice()));
}

export function referenceSupportDeclaration(finite,mode=FULL){
  referenceScientificTreatment(mode);
  const n=finite.prices.length;
  return {schemaVersion:1,treatment:mode,clock:'startup-only-five-phase',initialCap:'original physical cap; phase0 only',
    laterPhases:[1,2,3,4],laterSupport:mode===FULL?'all original price indices, independent of previous rival':'unchanged original rival-dependent guard',
    originalIndexRange:[0,n-1],originalCapIndex:finite.capIndex,originalGuardMasksSha256:digestJSON(finite.sets),
    physicalRecordUnchanged:true,floorTransferred:false,
    scope:mode===FULL?'Initial cap, unrestricted thereafter over the original price grid; no inherited guard floor':'Artificial old-arm parity mode; not an additional new experimental treatment',
    effectiveSupportsSha256:digestJSON(legalMatrix(finite,mode))};
}

export function createReferenceReplay(original,{mode=FULL,...options}={}){
  referenceScientificTreatment(mode);
  requireThat(original&&typeof original==='object','Original physical record required');
  const physical=original.finite??original;
  // Validate the ORIGINAL saved masks before cloning their effective replacement.
  // Avoid allocating a second discarded dense model for this administrative check.
  const n=physical?.prices?.length;
  requireThat(Number.isInteger(n)&&n>=1&&n<=62,'Invalid physical price domain');
  requireThat(physical.sets?.length===n&&physical.sets.every(s=>Array.isArray(s)&&s.length&&s.every((a,i)=>Number.isInteger(a)&&a>=0&&a<n&&(!i||a>s[i-1]))),'Invalid original legal masks');
  const effective=structuredClone(physical);
  if(mode===FULL)effective.sets=Array.from({length:physical.prices.length},()=>Array.from({length:physical.prices.length},(_,i)=>i));
  const model=createReplay(effective,'startup',options);
  model.physicalRecord=original;
  model.physicalSnapshot=structuredClone(original);
  model.referenceMode=mode;
  model.treatment=mode;
  model.scientificTreatment=referenceScientificTreatment(mode);
  model.supportTreatment=referenceSupportDeclaration(physical,mode);
  return model;
}

// Public cross-author anchor schema; arithmetic and selection stay independent.
export function exactStageAnchors(original){
  const result=enumerateExactStaticAnchors(original);
  const pair=p=>({indices:p.indices,prices:[p.prices.A,p.prices.B],profits:{A:p.profits.A,B:p.profits.B,joint:p.jointProfit},consumerSurplus:p.consumerSurplus});
  return {n:result.n,coordinateOrder:result.payoffOrientation,scope:result.scope,
    bestResponses:{AByRivalB:result.bestResponses.AByFixedB,BByRivalA:result.bestResponses.BByFixedA},
    pureNash:{count:result.pureNash.length,pairs:result.pureNash.map(pair),reason:result.pureNashEmptyReason},
    jointProfitMaximum:{value:result.jointProfitMaximum,count:result.jointProfitMaximizers.length,pairs:result.jointProfitMaximizers.map(pair)}};
}

export function validateReferenceReplay(model){
  requireThat(model.arm==='startup','Reference must use the startup cap clock');
  requireThat(same(model.physicalRecord,model.physicalSnapshot),'Original physical record changed');
  const physical=model.physicalRecord.finite??model.physicalRecord,mode=model.referenceMode;
  const expected=structuredClone(physical);
  if(mode===FULL)expected.sets=Array.from({length:model.n},()=>Array.from({length:model.n},(_,a)=>a));
  requireThat(same(model.finite,expected),'Effective finite view differs from the declared reference supports or physical payoffs');
  requireThat(model.treatment===mode&&same(model.scientificTreatment,referenceScientificTreatment(mode)),'Scientific treatment declaration differs');
  requireThat(same(model.supportTreatment,referenceSupportDeclaration(physical,mode)),'Support declaration differs');
  assertForbiddenZero(model);
  // For full supports this is only a physical grid bound after the first
  // post-cap execution, not an inherited immediate-profit envelope/floor.
  validateReplayEndpoint(model);
  return true;
}

export function expectedReferenceGraph(model){
  validateReferenceReplay(model);
  const graph=expectedGraphClaim(model,{certifyFloor:false});
  graph.scientificTreatment=structuredClone(model.scientificTreatment);
  graph.supportTreatment=structuredClone(model.supportTreatment);
  graph.scope+=' Support treatment is explicit; no inherited guard-envelope/floor assertion applies to full-grid continuation.';
  requireThat(graph.floor===null&&graph.cycles.every(c=>c.floorApplies===null&&c.floorGap===null),'Reference unexpectedly inherited a guard floor');
  return graph;
}

export function expectedReferenceWindows(model){
  validateReferenceReplay(model);
  return expectedWindowClaims(model);
}

// A fresh binary64 decoder for this static checker. No primary or accepted
// rational decoder is imported. Negative zero is the exact rational zero.
const gcd=(a,b)=>{a=a<0n?-a:a;while(b){const remainder=a%b;a=b;b=remainder;}return a;};
const reduced=(n,d)=>{
  requireThat(d>0n,'Exact denominator must be positive');
  if(n===0n)return{n:0n,d:1n};
  const divisor=gcd(n,d);return{n:n/divisor,d:d/divisor};
};
export function decodeAnchorBinary64(value){
  requireThat(typeof value==='number'&&Number.isFinite(value),'Static anchor value must be finite binary64');
  const data=new DataView(new ArrayBuffer(8));data.setFloat64(0,value,false);
  const bits=data.getBigUint64(0,false),negative=(bits>>63n)!==0n,biased=Number((bits>>52n)&2047n),fraction=bits&((1n<<52n)-1n);
  if(biased===0&&fraction===0n)return{n:0n,d:1n};
  const significand=biased===0?fraction:(1n<<52n)+fraction,power=biased===0?-1074:biased-1075;
  const signed=negative?-significand:significand;
  return power>=0?reduced(signed<<BigInt(power),1n):reduced(signed,1n<<BigInt(-power));
}
const plus=(a,b)=>reduced(a.n*b.d+b.n*a.d,a.d*b.d);
const compare=(a,b)=>{const delta=a.n*b.d-b.n*a.d;return delta<0n?-1:delta>0n?1:0;};
const stored=q=>({numerator:q.n.toString(),denominator:q.d.toString()});

export function enumerateExactStaticAnchors(original){
  const finite=original?.finite??original,n=finite?.prices?.length;
  requireThat(Number.isInteger(n)&&n>=1&&n<=62,'Invalid static anchor price domain');
  requireThat(finite.prices.every((p,i)=>typeof p==='number'&&Number.isFinite(p)&&(!i||p>finite.prices[i-1])),'Static anchor prices must increase strictly');
  for(const key of ['profitA','profitB','consumerSurplus'])requireThat(Array.isArray(finite.rewards?.[key])&&finite.rewards[key].length===n*n,'Static anchor payoff dimensions differ');
  const prices=finite.prices.map(decodeAnchorBinary64),A=finite.rewards.profitA.map(decodeAnchorBinary64),B=finite.rewards.profitB.map(decodeAnchorBinary64),CS=finite.rewards.consumerSurplus.map(decodeAnchorBinary64);
  const bestA=Array.from({length:n},()=>[]),bestB=Array.from({length:n},()=>[]);
  for(let b=0;b<n;b++)for(let a=0;a<n;a++){
    const list=bestA[b],order=list.length?compare(A[a*n+b],A[list[0]*n+b]):1;
    if(order>0){list.length=0;list.push(a);}else if(order===0)list.push(a);
  }
  for(let a=0;a<n;a++)for(let b=0;b<n;b++){
    const list=bestB[a],order=list.length?compare(B[a*n+b],B[a*n+list[0]]):1;
    if(order>0){list.length=0;list.push(b);}else if(order===0)list.push(b);
  }
  const joint=A.map((a,i)=>plus(a,B[i])),maximum=joint.reduce((largest,v)=>compare(v,largest)>0?v:largest,joint[0]);
  const profile=(a,b)=>({indices:[a,b],prices:{A:stored(prices[a]),B:stored(prices[b])},profits:{A:stored(A[a*n+b]),B:stored(B[a*n+b])},jointProfit:stored(joint[a*n+b]),consumerSurplus:stored(CS[a*n+b])});
  const nash=[],jointMax=[];
  for(let a=0;a<n;a++)for(let b=0;b<n;b++){
    if(bestA[b].includes(a)&&bestB[a].includes(b))nash.push(profile(a,b));
    if(compare(joint[a*n+b],maximum)===0)jointMax.push(profile(a,b));
  }
  return {schemaVersion:1,n,payoffOrientation:'WORLD row a*n+b for both firms',arithmetic:'Exact saved binary64 prices/payoffs; exact rational sum of separate individual profits',
    bestResponses:{AByFixedB:bestA,BByFixedA:bestB},pureNash:nash,pureNashEmptyReason:nash.length?null:'No pure Nash profile in the saved finite simultaneous payoff table',
    jointProfitMaximum:stored(maximum),jointProfitMaximizers:jointMax,
    scope:'Static simultaneous full-grid stage-game anchors only; no claim about equilibria or stability of learned or guarded history-dependent policies'};
}
