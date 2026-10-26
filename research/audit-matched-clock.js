// Independent matched-clock replay core. Importing performs no IO or training.
// No primary learner, phase, PRNG, layout, optimizer or graph helper is imported.
// Binary64 parity intentionally uses the same prospectively bound Node/V8 runtime.
import {createHash} from 'node:crypto';
const demand=(ok,message)=>{if(!ok)throw Error(message);};
const U32=4294967296, MASK=0xffffffff;

export function word(state){
  const first=Math.imul(state[1],5)>>>0;
  const rotated=((first<<7)|(first>>>25))>>>0;
  const result=Math.imul(rotated,9)>>>0;
  const shift=(state[1]<<9)>>>0;
  state[2]=(state[2]^state[0])>>>0;
  state[3]=(state[3]^state[1])>>>0;
  state[1]=(state[1]^state[2])>>>0;
  state[0]=(state[0]^state[3])>>>0;
  state[2]=(state[2]^shift)>>>0;
  state[3]=((state[3]<<11)|(state[3]>>>21))>>>0;
  return result;
}

export function jumped(state){
  const s=state.slice(),acc=[0,0,0,0];
  for(const bits of [0x8764000b,0xf542d2d3,0x6fa035c3,0x77f2db5b]){
    for(let bit=0;bit<32;bit++){
      if((bits>>>bit)&1)for(let j=0;j<4;j++)acc[j]=(acc[j]^s[j])>>>0;
      word(s);
    }
  }
  return acc;
}

export function initialActors(){
  let s=[907001,907002,907003,907004];const result=[];
  for(let i=0;i<12;i++){
    const A=s.slice();s=jumped(s);const B=s.slice();s=jumped(s);
    result.push({seed:907001+i,segments:[2*i,2*i+1],actors:[A,B]});
  }
  return result;
}

export function phaseAfter(t){
  demand(Number.isSafeInteger(t)&&t>=0,'Invalid completed round count');
  return t===0?0:1+((t-1)%4);
}
export function following(phase){demand(Number.isInteger(phase)&&phase>=0&&phase<5,'Invalid phase');return phase===0||phase===4?1:phase+1;}
export function capped(arm,phase){demand(['startup','recurring4'].includes(arm),'Unknown matched arm');return phase===0||(arm==='recurring4'&&phase===4);}
export function epsilon(t,T){
  demand(Number.isSafeInteger(T)&&T>=2&&Number.isSafeInteger(t)&&t>=0&&t<T,'Invalid epsilon clock');
  if(t===0)return 1;if(t===T-1)return .01;
  return Math.exp(-Math.log(100)*t/(T-1));
}

export function createReplay(finite,arm,{seed=907001,T=2000000,alpha=.1,gamma=19/20,actors=null,transcriptBlockSize=10000}={}){
  const n=finite?.prices?.length;
  demand(Number.isInteger(n)&&n>=1&&n<=62&&finite.prices.every((v,i)=>Number.isFinite(v)&&(!i||v>finite.prices[i-1])),'Invalid saved price array');
  demand(Number.isInteger(finite.capIndex)&&finite.capIndex>=0&&finite.capIndex<n,'Invalid cap');
  demand(finite.sets?.length===n&&finite.sets.every(s=>Array.isArray(s)&&s.length&&s.every((a,i)=>Number.isInteger(a)&&a>=0&&a<n&&(!i||a>s[i-1]))),'Invalid saved legal masks');
  for(const key of ['profitA','profitB','consumerSurplus'])demand(finite.rewards?.[key]?.length===n*n&&finite.rewards[key].every(Number.isFinite),'Invalid saved reward '+key);
  demand(Number.isSafeInteger(T)&&T>=2&&T<=2000000&&alpha>0&&alpha<=1&&gamma>=0&&gamma<1,'Invalid learning settings');
  capped(arm,0);
  const rng=(actors??initialActors().find(x=>x.seed===seed)?.actors)?.map(a=>a.slice());
  demand(rng?.length===2&&rng.every(a=>a.length===4&&a.every(v=>Number.isInteger(v)&&v>=0&&v<=MASK)&&a.some(v=>v!==0)),'Invalid independent actor states');
  const cells=5*n*n*n;
  return{finite,arm,n,seed,T,alpha,gamma,rng,q:[new Float64Array(cells),new Float64Array(cells)],counts:[new Uint32Array(cells),new Uint32Array(cells)],t:0,phase:0,previous:[n-1,n-1],caps:0,transcript:new RoundTranscript(transcriptBlockSize),learningBlocks:[],pendingLearningBlock:null,
    capActions:Array.from({length:finite.capIndex+1},(_,i)=>i),
    windows:[Math.floor(T/2),T].map(end=>({start:Math.max(0,end-100000),end,transitions:new Map(),rounds:0,maxAllowed:[0,0],caps:0,explorationDecisions:[0,0],priceChanges:[0,0]}))};
}
export function support(m,phase,rival){return capped(m.arm,phase)?m.capActions:m.finite.sets[rival];}
export function rowStart(m,phase,own,rival){return((phase*m.n+own)*m.n+rival)*m.n;}
export function scan(m,firm,phase,own,rival){
  const legal=support(m,phase,rival),base=rowStart(m,phase,own,rival),q=m.q[firm];
  let action=legal[0],value=q[base+action];
  for(let k=1;k<legal.length;k++){const a=legal[k],candidate=q[base+a];if(candidate>value){action=a;value=candidate;}}
  demand(Number.isFinite(value),'Nonfinite independently scanned maximum');return{action,value};
}

export function replayStep(m,{trace=false}={}){
  demand(m.t<m.T&&m.phase===phaseAfter(m.t),'Replay step/clock mismatch');
  const t=m.t,phase=m.phase,[oldA,oldB]=m.previous,eps=epsilon(t,m.T);
  const uA=word(m.rng[0])/U32,vA=word(m.rng[0])/U32,uB=word(m.rng[1])/U32,vB=word(m.rng[1])/U32;
  const legalA=support(m,phase,oldB),legalB=support(m,phase,oldA);
  const exploreA=uA<eps,exploreB=uB<eps;
  const a=exploreA?legalA[Math.floor(vA*legalA.length)]:scan(m,0,phase,oldA,oldB).action;
  const b=exploreB?legalB[Math.floor(vB*legalB.length)]:scan(m,1,phase,oldB,oldA).action;
  const next=following(phase),index=a*m.n+b;
  // Both bootstrap values come from the still-unmodified tables.
  const maxA=scan(m,0,next,a,b).value,maxB=scan(m,1,next,b,a).value;
  const cellA=rowStart(m,phase,oldA,oldB)+a,cellB=rowStart(m,phase,oldB,oldA)+b;
  const priorA=m.q[0][cellA],priorB=m.q[1][cellB];
  const targetA=m.finite.rewards.profitA[index]+m.gamma*maxA;
  const targetB=m.finite.rewards.profitB[index]+m.gamma*maxB;
  const newA=priorA+m.alpha*(targetA-priorA),newB=priorB+m.alpha*(targetB-priorB);
  demand(Number.isFinite(newA)&&Number.isFinite(newB),'Nonfinite replayed update');
  m.q[0][cellA]=newA;m.q[1][cellB]=newB;m.counts[0][cellA]++;m.counts[1][cellB]++;
  m.transcript.record(t,phase,oldA,oldB,a,b,Number(exploreA)+2*Number(exploreB),eps,m.finite.rewards.profitA[index],m.finite.rewards.profitB[index],priorA,priorB,maxA,maxB,newA,newB,m.rng);
  if(m.pendingLearningBlock===null)m.pendingLearningBlock={firstRound:t+1,lastRound:null,rounds:0,consumerSurplusSum:0,profitSums:[0,0],priceSums:[0,0],explorations:[0,0],maxAllowed:[0,0],capExecutions:0};
  const block=m.pendingLearningBlock;
  block.rounds++;block.consumerSurplusSum+=m.finite.rewards.consumerSurplus[index];
  block.profitSums[0]+=m.finite.rewards.profitA[index];block.profitSums[1]+=m.finite.rewards.profitB[index];
  block.priceSums[0]+=m.finite.prices[a];block.priceSums[1]+=m.finite.prices[b];
  block.explorations[0]+=Number(exploreA);block.explorations[1]+=Number(exploreB);
  block.maxAllowed[0]+=Number(a===legalA.at(-1));block.maxAllowed[1]+=Number(b===legalB.at(-1));block.capExecutions+=Number(capped(m.arm,phase));
  if(block.rounds===10000){block.lastRound=t+1;m.learningBlocks.push(block);m.pendingLearningBlock=null;}
  const jointSource=(phase*m.n+oldA)*m.n+oldB,key=jointSource*m.n*m.n+index;
  for(const w of m.windows)if(t>=w.start&&t<w.end){
    w.transitions.set(key,(w.transitions.get(key)??0)+1);w.rounds++;
    w.maxAllowed[0]+=Number(a===legalA.at(-1));w.maxAllowed[1]+=Number(b===legalB.at(-1));
    w.caps+=Number(capped(m.arm,phase));w.explorationDecisions[0]+=Number(exploreA);w.explorationDecisions[1]+=Number(exploreB);
    w.priceChanges[0]+=Number(a!==oldA);w.priceChanges[1]+=Number(b!==oldB);
  }
  m.caps+=Number(capped(m.arm,phase));m.previous=[a,b];m.phase=next;m.t=t+1;
  return trace?{step:t,phase,previous:[oldA,oldB],actions:[a,b],draws:[[uA,vA],[uB,vB]],epsilon:eps,nextPhase:next,nextMaxima:[maxA,maxB],cells:[cellA,cellB],priorQ:[priorA,priorB],targets:[targetA,targetB],newQ:[newA,newB]}:null;
}

function encodeInto(view,offset,t,phase,prevA,prevB,a,b,flags,eps,rA,rB,oldA,oldB,maxA,maxB,newA,newB,actors){
  demand(Number.isInteger(t)&&t>=1&&t<4294967296&&Number.isInteger(phase)&&phase>=0&&phase<5,'Invalid one-based transcript round/phase');
  demand([prevA,prevB,a,b].every(v=>Number.isInteger(v)&&v>=0&&v<62)&&Number.isInteger(flags)&&flags>=0&&flags<4,'Invalid transcript index/decision flags');
  demand([eps,rA,rB,oldA,oldB,maxA,maxB,newA,newB].every(Number.isFinite)&&eps>=0&&eps<=1,'Invalid transcript numeric field');
  demand(actors?.length===2&&actors.every(row=>row.length===4&&row.every(v=>Number.isInteger(v)&&v>=0&&v<=MASK)),'Invalid transcript actor words');
  view.setUint32(offset,t,true);
  for(const [index,value] of [phase,prevA,prevB,a,b,flags].entries())view.setUint8(offset+4+index,value);
  for(let i=10;i<16;i++)view.setUint8(offset+i,0);
  for(const [index,value] of [eps,rA,rB,oldA,oldB,maxA,maxB,newA,newB].entries())view.setFloat64(offset+16+8*index,value,true);
  for(let firm=0;firm<2;firm++)for(let i=0;i<4;i++)view.setUint32(offset+88+16*firm+4*i,actors[firm][i],true);
}
export function encodeTranscriptRound(w){
  const bytes=new Uint8Array(120),view=new DataView(bytes.buffer);
  encodeInto(view,0,w.step,w.phase,...w.previous,...w.actions,w.exploreFlags,w.epsilon,...w.expectedProfits,...w.priorQ,...w.nextMaxima,...w.newQ,w.rngAfter);
  return Buffer.from(bytes);
}
export class RoundTranscript{
  constructor(blockSize=10000){
    demand(Number.isInteger(blockSize)&&blockSize>=1&&blockSize<=10000,'Invalid transcript block size');
    this.blockSize=blockSize;this.bytes=new Uint8Array(120*blockSize);this.view=new DataView(this.bytes.buffer);this.totalRounds=0;this.pendingRounds=0;this.blocks=[];
  }
  record(t,...fields){
    demand(t===this.totalRounds,'Skipped or duplicate transcript round');
    encodeInto(this.view,120*this.pendingRounds,t+1,...fields);this.pendingRounds++;this.totalRounds++;
    if(this.pendingRounds===this.blockSize){
      const start=this.totalRounds-this.blockSize;
      this.blocks.push({block:this.blocks.length+1,firstRound:start+1,lastRound:this.totalRounds,rounds:this.blockSize,bytes:120*this.blockSize,sha256:createHash('sha256').update(this.bytes).digest('hex')});
      this.pendingRounds=0;
    }
  }
  snapshot(){return{encoding:'120-byte LE round transcript v1',blockSize:this.blockSize,totalRounds:this.totalRounds,blocks:this.blocks.map(x=>({...x})),pendingRounds:this.pendingRounds,pendingBytes:120*this.pendingRounds,pendingSha256:createHash('sha256').update(this.bytes.subarray(0,120*this.pendingRounds)).digest('hex')};}
}
export function replayTo(m,end){demand(Number.isSafeInteger(end)&&end>=m.t&&end<=m.T,'Invalid replay horizon');while(m.t<end)replayStep(m);return m;}
export function assertForbiddenZero(m){
  for(let phase=0;phase<5;phase++)for(let own=0;own<m.n;own++)for(let rival=0;rival<m.n;rival++){
    const legal=new Set(support(m,phase,rival)),base=rowStart(m,phase,own,rival);
    for(let a=0;a<m.n;a++)if(!legal.has(a))for(let f=0;f<2;f++)demand(Object.is(m.q[f][base+a],0)&&m.counts[f][base+a]===0,'Forbidden dense cell changed');
  }
  for(let f=0;f<2;f++)demand(m.counts[f].reduce((a,b)=>a+b,0)===m.t,'Independent total count mismatch');
  return true;
}
export function canonicalBytes(values,kind){
  demand(kind==='f64'||kind==='u32','Unknown canonical type');
  const width=kind==='f64'?8:4,bytes=Buffer.alloc(values.length*width);
  for(let i=0;i<values.length;i++)if(kind==='f64')bytes.writeDoubleLE(values[i],8*i);else bytes.writeUInt32LE(values[i],4*i);
  return bytes;
}

const gcd=(a,b)=>{a=a<0n?-a:a;while(b){const r=a%b;a=b;b=r;}return a;};
function fraction(n,d){demand(d>0n,'Positive exact denominator required');const g=gcd(n,d);return{numerator:(n/g).toString(),denominator:(d/g).toString()};}
export function exactBinary64(value){
  demand(Number.isFinite(value),'Nonfinite exact payoff');
  const bytes=new DataView(new ArrayBuffer(8));bytes.setFloat64(0,value,false);
  const bits=bytes.getBigUint64(0,false),sign=(bits>>63n)?-1n:1n,exponent=Number((bits>>52n)&2047n),tail=bits&((1n<<52n)-1n);
  const mantissa=exponent===0?tail:tail+(1n<<52n),power=exponent===0?-1074:exponent-1075;
  if(mantissa===0n)return{n:0n,d:1n};
  let n=sign*mantissa,d=1n;if(power>=0)n<<=BigInt(power);else d<<=BigInt(-power);
  const g=gcd(n,d);return{n:n/g,d:d/g};
}
function lifted(values){
  const rs=values.map(exactBinary64);let denominator=1n;for(const r of rs)if(r.d>denominator)denominator=r.d;
  return{weights:rs.map(r=>r.n*(denominator/r.d)),denominator};
}
export function validateReplayEndpoint(m){
  demand(m.phase===phaseAfter(m.t),'Independent endpoint next-clock mismatch');
  demand(m.caps===(m.t===0?0:m.arm==='startup'?1:Math.ceil(m.t/4)),'Independent endpoint cap-count mismatch');
  if(m.t===0){demand(m.previous.every(i=>i===m.n-1),'Initial old history differs');return{bound:m.n-1,guardSteps:null};}
  const upper=m.finite.sets.map(s=>s.at(-1));demand(upper.every((u,i)=>i===0||u>=upper[i-1]),'Monotone cap-start envelope premise missing');
  const steps=m.arm==='startup'?m.t-1:(m.t-1)%4;let bound=m.finite.capIndex;
  for(let i=0;i<steps;i++){const next=upper[bound];demand(next>=bound,'Cap-start upper orbit decreases');if(next===bound)break;bound=next;}
  demand(m.previous.every(p=>p<=bound),'Actual endpoint exceeds cap-start envelope');return{bound,guardSteps:steps};
}

export function frozenGraph(m){
  assertForbiddenZero(m);
  const n=m.n,N=5*n*n,focalPolicies=[new Uint8Array(N),new Uint8Array(N)],visits=[new Uint32Array(N),new Uint32Array(N)],chosen=[new Uint32Array(N),new Uint32Array(N)];
  for(let phase=0;phase<5;phase++)for(let own=0;own<n;own++)for(let rival=0;rival<n;rival++){
    const row=(phase*n+own)*n+rival,base=row*n;
    for(let f=0;f<2;f++){
      const action=scan(m,f,phase,own,rival).action;focalPolicies[f][row]=action;
      let total=0;for(let a=0;a<n;a++)total+=m.counts[f][base+a];visits[f][row]=total;chosen[f][row]=m.counts[f][base+action];
    }
  }
  const worldPolicies=[new Uint8Array(N),new Uint8Array(N)],successor=new Uint32Array(N),pairByState=new Uint32Array(N);
  for(let s=0;s<N;s++){
    const phase=Math.floor(s/(n*n)),A=Math.floor(s/n)%n,B=s%n,other=(phase*n+B)*n+A;
    const a=focalPolicies[0][s],b=focalPolicies[1][other];worldPolicies[0][s]=a;worldPolicies[1][s]=b;
    pairByState[s]=a*n+b;successor[s]=(following(phase)*n+a)*n+b;
  }
  const colors=new Uint8Array(N),labels=new Int32Array(N).fill(-1),distance=new Uint32Array(N),position=new Int32Array(N),cycles=[];
  for(let root=0;root<N;root++){
    if(colors[root]===2)continue;const path=[];let s=root;
    while(colors[s]===0){colors[s]=1;position[s]=path.length;path.push(s);s=successor[s];}
    if(colors[s]===1){
      const raw=path.slice(position[s]),id=Math.min(...raw),where=raw.indexOf(id),nodes=raw.slice(where).concat(raw.slice(0,where));
      demand(nodes.every(node=>Math.floor(node/(n*n))!==0)&&nodes.length%4===0,'Activation phase recurred or cyclic clock was lost');
      for(const node of nodes){labels[node]=id;distance[node]=0;}cycles.push({id,nodes,length:nodes.length,basinStates:0});
    }
    for(let i=path.length-1;i>=0;i--){const node=path[i];if(labels[node]<0){labels[node]=labels[successor[node]];distance[node]=distance[successor[node]]+1;}colors[node]=2;}
  }
  cycles.sort((a,b)=>a.id-b.id);const byId=new Map(cycles.map(c=>[c.id,c]));for(const id of labels)byId.get(id).basinStates++;
  const weights={consumerSurplus:lifted(m.finite.rewards.consumerSurplus),profitA:lifted(m.finite.rewards.profitA),profitB:lifted(m.finite.rewards.profitB),prices:lifted(m.finite.prices)};
  function metrics(nodes){
    if(!nodes.length)return null;const sums={consumerSurplus:0n,profitA:0n,profitB:0n,priceA:0n,priceB:0n};
    for(const s of nodes){const pair=pairByState[s];for(const key of ['consumerSurplus','profitA','profitB'])sums[key]+=weights[key].weights[pair];sums.priceA+=weights.prices.weights[Math.floor(pair/n)];sums.priceB+=weights.prices.weights[pair%n];}
    const out={};for(const key of Object.keys(sums))out[key]=fraction(sums[key],BigInt(nodes.length)*(key.startsWith('price')?weights.prices.denominator:weights[key].denominator));return out;
  }
  for(const c of cycles){
    c.metrics=metrics(c.nodes);c.trainingSupport={};
    for(let f=0;f<2;f++){
      const vv=[],aa=[];for(const s of c.nodes){const p=Math.floor(s/(n*n)),A=Math.floor(s/n)%n,B=s%n,row=f===0?s:(p*n+B)*n+A;vv.push(visits[f][row]);aa.push(chosen[f][row]);}
      c.trainingSupport[f===0?'A':'B']={unvisitedStates:vv.filter(v=>v===0).length,neverTriedGreedyActions:aa.filter(v=>v===0).length,minimumStateVisits:Math.min(...vv),minimumActionVisits:Math.min(...aa)};
    }
  }
  function trajectory(start){
    const positions=new Map(),nodes=[];let s=start;
    while(!positions.has(s)){demand(nodes.length<N,'Full graph trajectory bound exceeded');positions.set(s,nodes.length);nodes.push(s);s=successor[s];}
    const h=positions.get(s),cycle=nodes.slice(h);return{startNode:start,transientNodes:nodes.slice(0,h),transientRounds:h,cycleNodesFromStart:cycle,cycleId:labels[start],cycleMetrics:metrics(cycle)};
  }
  const terminal=(m.phase*n+m.previous[0])*n+m.previous[1];
  return{focalPolicies,worldPolicies,successor,labels,distance,cycles,actualTerminal:trajectory(terminal),freshCapCounterfactual:trajectory(n*n-1)};
}

function exactPack(value){const result=fraction(value.n,value.d);return{...result,approximate:Number(result.numerator)/Number(result.denominator)};}
function subtractRatio(a,b){const n=a.n*b.d-b.n*a.d,d=a.d*b.d,g=gcd(n,d);return{n:n/g,d:d/g};}
function ratioFromPacked(p){return{n:BigInt(p.numerator),d:BigInt(p.denominator)};}
const atMost=(a,b)=>a.n*b.d<=b.n*a.d;

// Independently rebuild the COMPLETE science claim, including geometry/support/
// floors/targets/previews, so a full adapter can reject altered ancillary fields.
export function expectedGraphClaim(m,{originalTargets=[],certifyFloor=true}={}){
  const independent=frozenGraph(m),n=m.n,N=5*n*n,cs=lifted(m.finite.rewards.consumerSurplus),pA=lifted(m.finite.rewards.profitA),pB=lifted(m.finite.rewards.profitB),prices=lifted(m.finite.prices);
  const pack=(num,den)=>exactPack({n:num,d:den});
  function execution(s){const phase=Math.floor(s/(n*n)),A=Math.floor(s/n)%n,B=s%n,a=independent.worldPolicies[0][s],b=independent.worldPolicies[1][s];return{phase,A,B,a,b,pair:a*n+b};}
  function metrics(nodes){
    if(!nodes.length)return null;
    let C=0n,A=0n,B=0n,PA=0n,PB=0n,NA=0n,NB=0n,SA=0n,SB=0n,HA=0n,HB=0n,cap=0n;
    for(const s of nodes){const e=execution(s),la=support(m,e.phase,e.B),lb=support(m,e.phase,e.A);
      C+=cs.weights[e.pair];A+=pA.weights[e.pair];B+=pB.weights[e.pair];PA+=prices.weights[e.a];PB+=prices.weights[e.b];
      NA+=BigInt(la.length);NB+=BigInt(lb.length);SA+=prices.weights[la.at(-1)]-prices.weights[la[0]];SB+=prices.weights[lb.at(-1)]-prices.weights[lb[0]];
      HA+=BigInt(e.a===la.at(-1));HB+=BigInt(e.b===lb.at(-1));cap+=BigInt(capped(m.arm,e.phase));
    }
    const len=BigInt(nodes.length),average=(v,d=1n)=>pack(v,d*len);
    return{rounds:nodes.length,consumerSurplus:average(C,cs.denominator),profits:{A:average(A,pA.denominator),B:average(B,pB.denominator)},prices:{A:average(PA,prices.denominator),B:average(PB,prices.denominator)},maskCount:{A:average(NA),B:average(NB)},maskFraction:{A:average(NA,BigInt(n)),B:average(NB,BigInt(n))},maskSpan:{A:average(SA,prices.denominator),B:average(SB,prices.denominator)},maxAllowedUsage:{A:average(HA),B:average(HB)},capRuleFrequency:average(cap)};
  }
  const rowVisits=[new Uint32Array(N),new Uint32Array(N)];
  for(let f=0;f<2;f++)for(let row=0;row<N;row++)for(let a=0;a<n;a++)rowVisits[f][row]+=m.counts[f][row*n+a];
  function trainingSupport(nodes){
    const out={};for(let f=0;f<2;f++){
      let unseen=0,untried=0,minState=null,minAction=null;
      for(const s of nodes){const e=execution(s),row=f===0?s:(e.phase*n+e.B)*n+e.A,action=f===0?e.a:e.b,v=rowVisits[f][row],c=m.counts[f][row*n+action];unseen+=Number(v===0);untried+=Number(c===0);minState=minState===null?v:Math.min(minState,v);minAction=minAction===null?c:Math.min(minAction,c);}
      out[f===0?'A':'B']={unvisitedStates:unseen,neverTriedGreedyActions:untried,minimumStateVisits:minState,minimumActionVisits:minAction};
    }return out;
  }
  let floor=null;
  if(certifyFloor){
    const endpoint=validateReplayEndpoint(m),upper=m.finite.sets.map(s=>s.at(-1)),orbit=[m.finite.capIndex];
    for(let a=0;a<n;a++)for(let b=0;b<n;b++){
      const v=cs.weights[a*n+b];if(a+1<n)demand(v>=cs.weights[(a+1)*n+b],'Saved CS increases in A');if(b+1<n)demand(v>=cs.weights[a*n+b+1],'Saved CS increases in B');
    }
    let bound=m.finite.capIndex;while(upper[bound]!==bound){demand(upper[bound]>=bound&&orbit.length<=n,'Invalid increasing upper orbit');bound=upper[bound];orbit.push(bound);}
    let value,cycleMean;
    if(m.arm==='startup')value=cycleMean={n:cs.weights[bound*n+bound],d:cs.denominator};
    else{
      let a=m.finite.capIndex,sum=0n;value=null;
      for(let i=0;i<4;i++){if(i)a=upper[a];sum+=cs.weights[a*n+a];const prefix={n:sum,d:BigInt(i+1)*cs.denominator};if(value===null||atMost(prefix,value))value=prefix;}
      cycleMean={n:sum,d:4n*cs.denominator};
    }
    const comparisons=originalTargets.map(t=>{
      const actual=exactBinary64(t.actualGuaranteedThreshold);
      if(m.arm==='startup')return{label:t.label,actualThreshold:exactPack(actual),floorMeetsTarget:atMost(actual,value)};
      return{label:t.label,requestedTarget:exactPack(exactBinary64(t.requestedTarget)),numericalMargin:typeof t.numericalMargin==='number'?exactPack(exactBinary64(t.numericalMargin)):null,actualThreshold:exactPack(actual),activationFloorMeetsTarget:atMost(actual,value),activationFloorReserve:exactPack(subtractRatio(value,actual))};
    });
    floor={kind:m.arm==='startup'?'startup-cap-first':'recurring-four-round-cap',activationFloor:exactPack(value),cycleMean:exactPack(cycleMean),upperOrbit:orbit,fixedPointIndex:bound,endpointUpperIndex:endpoint.bound,guardStepsSinceCap:endpoint.guardSteps,
      scope:m.arm==='startup'?'Cap-first histories and their continuations only. Arbitrary guard-history cycles outside this price bound are retained without transferring the cap-first floor.':'Same numerical game, cap-first history and continuing four-round cap/guard schedule; common phase0 is transient.',targetComparisons:comparisons};
  }
  const capReachable=new Set([...independent.labels.subarray(0,n*n)]);
  const cycles=independent.cycles.map(c=>{
    const maximum=[0,0];for(const s of c.nodes){const e=execution(s);maximum[0]=Math.max(maximum[0],e.a);maximum[1]=Math.max(maximum[1],e.b);}
    const met=metrics(c.nodes),applies=floor===null?null:m.arm==='recurring4'||capReachable.has(c.id)||maximum.every(a=>a<=floor.fixedPointIndex),gap=floor===null?null:exactPack(subtractRatio(ratioFromPacked(met.consumerSurplus),ratioFromPacked(floor.activationFloor)));
    if(applies)demand(BigInt(gap.numerator)>=0n,'Applicable independent floor violated');
    return{id:c.id,nodes:c.nodes,length:c.length,basinStates:c.basinStates,metrics:met,trainingSupport:trainingSupport(c.nodes),policyCapReachable:capReachable.has(c.id),maximumExecutedIndices:maximum,floorApplies:applies,floorGap:gap};
  });
  const byId=new Map(cycles.map(c=>[c.id,c]));
  function pathClaim(t,kind){
    const c=byId.get(t.cycleId),start=t.startNode;
    return{kind,startNode:start,start:{phase:Math.floor(start/(n*n)),previousIndices:[Math.floor(start/n)%n,start%n]},transientNodes:t.transientNodes,transientRounds:t.transientRounds,transientMetrics:metrics(t.transientNodes),cycleId:c.id,cycleNodesFromStart:t.cycleNodesFromStart,cycleMetrics:c.metrics,trainingSupport:c.trainingSupport,pathTrainingSupport:trainingSupport(t.transientNodes.concat(t.cycleNodesFromStart)),floorApplies:c.floorApplies,floorGap:c.floorGap};
  }
  const actualTerminal=pathClaim(independent.actualTerminal,'actual-terminal-continuation'),freshCapCounterfactual=pathClaim(independent.freshCapCounterfactual,'counterfactual-high-history-fresh-activation');
  if(floor)demand(actualTerminal.floorApplies===true,'Actual terminal lacks independent cap-start floor');
  const preview=[];let at=actualTerminal.startNode;
  for(let round=1;round<=128;round++){const e=execution(at);preview.push({execution:round,sourceNode:at,phase:e.phase,previousIndices:[e.A,e.B],executedIndices:[e.a,e.b],nextPhase:following(e.phase),prices:[m.finite.prices[e.a],m.finite.prices[e.b]],consumerSurplus:m.finite.rewards.consumerSurplus[e.pair],profits:[m.finite.rewards.profitA[e.pair],m.finite.rewards.profitB[e.pair]],cap:capped(m.arm,e.phase)});at=independent.successor[at];}
  const hash=b=>createHash('sha256').update(b).digest('hex');
  return{states:N,step:m.t,phase:m.phase,arm:m.arm,coordinateOrder:'WORLD (phase,previousA,previousB). policies use focal own/rival rows; worldPolicies have B transposed once.',successorSha256:hash(canonicalBytes(independent.successor,'u32')),cycleLabelSha256:hash(canonicalBytes(independent.labels,'u32')),transientDistanceSha256:hash(canonicalBytes(independent.distance,'u32')),policySha256:independent.focalPolicies.map(a=>hash(a)),worldPolicySha256:independent.worldPolicies.map(a=>hash(a)),cycles,floor,actualTerminal,freshCapCounterfactual,terminalPreview128:preview,
    coverage:{A:{visitedStates:rowVisits[0].filter(v=>v>0).length,visitedActions:m.counts[0].filter(v=>v>0).length},B:{visitedStates:rowVisits[1].filter(v=>v>0).length,visitedActions:m.counts[1].filter(v=>v>0).length},allocatedStatesPerFirm:N,allocatedCellsPerFirm:m.q[0].length},
    scope:'Exact rational saved-weight deterministic frozen cycles; no exploration/update. Actual-terminal endpoint is primary; reset and arbitrary-state cycles are secondary. Preview is truncated; support does not prove competence or convergence.'};
}

export function expectedWindowClaims(m){
  const n=m.n,weights={cs:lifted(m.finite.rewards.consumerSurplus),A:lifted(m.finite.rewards.profitA),B:lifted(m.finite.rewards.profitB),price:lifted(m.finite.prices)};
  return m.windows.map(w=>{
    if(!w.rounds){demand(w.transitions.size===0,'Empty independent window has entries');return{startStep:w.start,endStep:w.end,rounds:0,metrics:null,reason:'No executed rounds in this window at this checkpoint'};}
    const sums={cs:0n,A:0n,B:0n,pa:0n,pb:0n,na:0n,nb:0n,sa:0n,sb:0n,ha:0n,hb:0n,cap:0n,ca:0n,cb:0n};let total=0;
    for(const [key,count]of w.transitions){
      demand(Number.isInteger(key)&&key>=0&&key<5*n**4&&Number.isInteger(count)&&count>0&&count<=m.T,'Malformed independent joint-window entry');
      const source=Math.floor(key/(n*n)),pair=key%(n*n),phase=Math.floor(source/(n*n)),A=Math.floor(source/n)%n,B=source%n,a=Math.floor(pair/n),b=pair%n,la=support(m,phase,B),lb=support(m,phase,A),k=BigInt(count);
      demand(la.includes(a)&&lb.includes(b),'Forbidden independent window action');total+=count;
      sums.cs+=weights.cs.weights[pair]*k;sums.A+=weights.A.weights[pair]*k;sums.B+=weights.B.weights[pair]*k;sums.pa+=weights.price.weights[a]*k;sums.pb+=weights.price.weights[b]*k;
      sums.na+=BigInt(la.length)*k;sums.nb+=BigInt(lb.length)*k;sums.sa+=(weights.price.weights[la.at(-1)]-weights.price.weights[la[0]])*k;sums.sb+=(weights.price.weights[lb.at(-1)]-weights.price.weights[lb[0]])*k;
      if(a===la.at(-1))sums.ha+=k;if(b===lb.at(-1))sums.hb+=k;if(capped(m.arm,phase))sums.cap+=k;if(a!==A)sums.ca+=k;if(b!==B)sums.cb+=k;
    }
    demand(total===w.rounds&&Number(sums.ha)===w.maxAllowed[0]&&Number(sums.hb)===w.maxAllowed[1]&&Number(sums.ca)===w.priceChanges[0]&&Number(sums.cb)===w.priceChanges[1]&&Number(sums.cap)===w.caps,'Independent window counters differ');
    const avg=(value,d=1n)=>exactPack({n:BigInt(value),d:d*BigInt(total)});
    return{startStep:w.start,endStep:w.end,rounds:total,metrics:{consumerSurplus:avg(sums.cs,weights.cs.denominator),profits:{A:avg(sums.A,weights.A.denominator),B:avg(sums.B,weights.B.denominator)},prices:{A:avg(sums.pa,weights.price.denominator),B:avg(sums.pb,weights.price.denominator)},maskCount:{A:avg(sums.na),B:avg(sums.nb)},maskFraction:{A:avg(sums.na,BigInt(n)),B:avg(sums.nb,BigInt(n))},maskSpan:{A:avg(sums.sa,weights.price.denominator),B:avg(sums.sb,weights.price.denominator)},maxAllowedUsage:{A:avg(sums.ha),B:avg(sums.hb)},capRuleFrequency:avg(sums.cap),explorationFrequency:{A:avg(w.explorationDecisions[0]),B:avg(w.explorationDecisions[1])},priceChangeFrequency:{A:avg(sums.ca),B:avg(sums.cb)}},reason:null};
  });
}
