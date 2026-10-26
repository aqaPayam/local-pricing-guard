// Browser-compatible finite numerical game. No network, model or random player.
const abs=x=>x<0n?-x:x;
function gcd(a,b){a=abs(a);b=abs(b);while(b){const r=a%b;a=b;b=r;}return a;}
export function rational(n,d=1n){n=BigInt(n);d=BigInt(d);if(d===0n)throw Error('Zero denominator');if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return {n:n/g,d:d/g};}
export const add=(a,b)=>rational(a.n*b.d+b.n*a.d,a.d*b.d);
export const subtract=(a,b)=>rational(a.n*b.d-b.n*a.d,a.d*b.d);
export const multiplyInteger=(a,k)=>rational(a.n*BigInt(k),a.d);
export const divideInteger=(a,k)=>rational(a.n,a.d*BigInt(k));
export const compare=(a,b)=>a.n*b.d<b.n*a.d?-1:a.n*b.d>b.n*a.d?1:0;
export const exactJSON=a=>({numerator:String(a.n),denominator:String(a.d)});
export const fromJSON=a=>rational(a.numerator,a.denominator);
export function fromDouble(x){
  if(!Number.isFinite(x))throw Error('Finite binary64 value required');
  const view=new DataView(new ArrayBuffer(8));view.setFloat64(0,x,false);const bits=view.getBigUint64(0,false),sign=bits>>63n?-1n:1n,mantissa=bits&((1n<<52n)-1n),exponent=Number((bits>>52n)&2047n);
  const n=sign*(exponent?mantissa+(1n<<52n):mantissa),e=exponent?exponent-1023-52:-1074;
  return e>=0?rational(n<<BigInt(e)):rational(n,1n<<BigInt(-e));
}
export function approximate(a){
  const n=Number(a.n),d=Number(a.d);if(Number.isFinite(n)&&Number.isFinite(d))return n/d;
  if(a.n===0n)return 0;const sign=a.n<0n?-1:1,nn=abs(a.n),shift=54-nn.toString(2).length+a.d.toString(2).length;
  const q=shift>=0?(nn<<BigInt(shift))/a.d:nn/(a.d<<BigInt(-shift));
  return sign*(Number(q)/2**52)*2**(52-shift);
}
export function nextDown(x){if(Number.isNaN(x)||x===-Infinity)return x;if(x===0)return -Number.MIN_VALUE;const v=new DataView(new ArrayBuffer(8));v.setFloat64(0,x,false);v.setBigUint64(0,v.getBigUint64(0,false)+(x>0?-1n:1n),false);return v.getFloat64(0,false);}
export const nextUp=x=>-nextDown(-x);
export function lowerDouble(a){
  let value=approximate(a);if(!Number.isFinite(value))throw Error('Finite certificate display required');
  while(compare(fromDouble(value),a)>0)value=nextDown(value);
  while(Number.isFinite(nextUp(value))&&compare(fromDouble(nextUp(value)),a)<=0)value=nextUp(value);
  return value;
}

export function certifyCycle(game,K){
  if(!Number.isInteger(K)||K<1||K>65536)throw Error('Invalid period');
  const n=game.prices.length,upper=game.sets.map(s=>Math.max(...s));
  if(!upper.every((u,j)=>!j||u>=upper[j-1]))throw Error('Nonmonotone upper map');
  let at=game.capIndex,sum=rational(0n),floor=null,floorHorizon=null;const cycleIndices=[],rewards=[];
  for(let j=0;j<K;j++){
    const reward=fromDouble(game.rewards.consumerSurplus[at*n+at]);cycleIndices.push(at);rewards.push(reward);sum=add(sum,reward);const mean=divideInteger(sum,j+1);
    if(!floor||compare(mean,floor)<0){floor=mean;floorHorizon=j+1;}at=upper[at];
  }
  const average=divideInteger(sum,K),descending=rewards.every((r,j)=>!j||compare(r,rewards[j-1])<=0);
  return {period:K,cycleIndices,cycleAverageExact:exactJSON(average),cycleAverageLower:lowerDouble(average),activationFloorExact:exactJSON(floor),activationFloorLower:lowerDouble(floor),minimizingPrefix:floorHorizon,descending,capFirst:true,scope:'Exact rational certificate for saved binary64 reward weights and saved numerical guard masks; not an exact-real logit certificate'};
}

export function createGame(record,K,{previous,targetLabel='cap-95pct'}={}){
  const game=record.finite,n=game.prices.length,certificate=game.certificates.find(c=>c.period===K),targets=record.originalTargets||[],target=targets.find(t=>t.label===targetLabel)||null;
  if(!certificate||!Number.isInteger(game.capIndex)||game.capIndex<0||game.capIndex>=n)throw Error('Missing finite-game certificate/cap');
  if(!game.sets.every(s=>s.length&&s.every(i=>Number.isInteger(i)&&i>=0&&i<n))||!['consumerSurplus','profitA','profitB','quantityA','quantityB'].every(k=>game.rewards[k]?.length===n*n&&game.rewards[k].every(Number.isFinite)))throw Error('Malformed finite game');
  const capActions=Array.from({length:game.capIndex+1},(_,i)=>i),initialPair=previous||[n-1,n-1];
  if(initialPair.length!==2||initialPair.some(i=>!Number.isInteger(i)||i<0||i>=n))throw Error('Invalid initial public prices');
  const floor=fromJSON(certificate.activationFloorExact),floorDisplay=certificate.activationFloorLower,displayFloor=fromDouble(floorDisplay);
  if(compare(displayFloor,floor)>0)throw Error('Floor display inflated certificate');
  const cycleRewards=certificate.cycleIndices.map(i=>fromDouble(game.rewards.consumerSurplus[i*n+i]));let cycleSum=rational(0n);const prefix=[cycleSum];for(const r of cycleRewards){cycleSum=add(cycleSum,r);prefix.push(cycleSum);}
  const initial=()=>({previous:initialPair.slice(),phase:0,executions:0,capExecutions:0,cs:rational(0n),profits:[rational(0n),rational(0n)],latest:null});
  let state=initial();const history=[];
  const allowed=shop=>{if(shop!==0&&shop!==1)throw Error('Shop must be0 or1');return (state.phase===0?capActions:game.sets[state.previous[1-shop]]).slice();};
  function preview(a,b){
    const indices=[a,b],legal=indices.every((i,f)=>Number.isInteger(i)&&allowed(f).includes(i));
    if(!legal)return {legal:false,reason:'Choose a permitted price for each shop before executing.'};
    const i=a*n+b,r=game.rewards;return {legal:true,indices,prices:indices.map(j=>game.prices[j]),consumerSurplus:r.consumerSurplus[i],profits:[r.profitA[i],r.profitB[i]],quantities:[r.quantityA[i],r.quantityB[i]],type:state.phase===0?'cap':'guard'};
  }
  function snapshot(){
    const T=state.executions,protectedBuffer=subtract(state.cs,multiplyInteger(displayFloor,T)),benchmark=add(multiplyInteger(cycleSum,Math.floor(T/K)),prefix[T%K]),threshold=target?fromDouble(target.actualGuaranteedThreshold):null;
    return {executions:T,phase:state.phase,nextIsCap:state.phase===0,movesUntilCap:state.phase===0?0:K-state.phase,capExecutions:state.capExecutions,previousIndices:state.previous.slice(),previousPrices:state.previous.map(i=>game.prices[i]),latest:state.latest,averages:T?{consumerSurplus:approximate(divideInteger(state.cs,T)),profits:state.profits.map(p=>approximate(divideInteger(p,T)))}:null,floor:{value:floorDisplay,exact:exactJSON(floor),scope:certificate.scope},protectedBuffer:{value:approximate(protectedBuffer),nonnegative:protectedBuffer.n>=0n,exact:exactJSON(protectedBuffer)},target:target?{label:target.label,threshold:target.actualGuaranteedThreshold,certified:compare(floor,threshold)>=0,buffer:approximate(subtract(state.cs,multiplyInteger(threshold,T)))}:null,benchmark:{cumulativeCS:approximate(benchmark),averageCS:T?approximate(divideInteger(benchmark,T)):null,scope:'Scripted maximum-permitted-price path at the same horizon; no model player'},plannedActivationRate:1/K,period:K,canUndo:history.length>0};
  }
  function execute(a,b){const reward=preview(a,b);if(!reward.legal)throw Error(reward.reason);if(!Number.isSafeInteger(state.executions+1))throw Error('Execution counter exhausted');history.push(state);state={previous:reward.indices.slice(),phase:(state.phase+1)%K,executions:state.executions+1,capExecutions:state.capExecutions+(state.phase===0?1:0),cs:add(state.cs,fromDouble(reward.consumerSurplus)),profits:state.profits.map((p,f)=>add(p,fromDouble(reward.profits[f]))),latest:reward};return snapshot();}
  return {allowed,preview,execute,snapshot,undo(){if(history.length)state=history.pop();return snapshot();},reset(){state=initial();history.length=0;return snapshot();}};
}
