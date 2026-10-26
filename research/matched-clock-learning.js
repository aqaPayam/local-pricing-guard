// Pure dense matched-clock learner. Importing performs no IO or training.
import crypto from 'node:crypto';
const need=(ok,message)=>{if(!ok)throw Error(message);};
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const rotate=(word,bits)=>((word<<bits)|(word>>>(32-bits)))>>>0;
export const TRANSCRIPT_ROUNDS=10000,TRANSCRIPT_BYTES=120;

// Published xoshiro128** 1.1 transition and 2^64 jump; no actor draws for logging.
export function randomWord(state){
 const result=Math.imul(rotate(Math.imul(state[1],5)>>>0,7),9)>>>0,t=(state[1]<<9)>>>0;
 state[2]=(state[2]^state[0])>>>0;state[3]=(state[3]^state[1])>>>0;
 state[1]=(state[1]^state[2])>>>0;state[0]=(state[0]^state[3])>>>0;
 state[2]=(state[2]^t)>>>0;state[3]=rotate(state[3],11);return result;
}
export function jump(state){
 const next=[0,0,0,0];
 for(const word of [0x8764000b,0xf542d2d3,0x6fa035c3,0x77f2db5b])for(let bit=0;bit<32;bit++){
  if((word>>>bit)&1)for(let j=0;j<4;j++)next[j]=(next[j]^state[j])>>>0;
  randomWord(state);
 }
 for(let j=0;j<4;j++)state[j]=next[j];return state;
}
export function actorNamespaces(){
 const state=[907001,907002,907003,907004],rows=[];
 for(let seed=907001;seed<=907012;seed++){
  const actors=[];for(let firm=0;firm<2;firm++){actors.push(state.slice());jump(state);}
  rows.push({seed,segments:[2*(seed-907001),2*(seed-907001)+1],actors});
 }
 return rows;
}
export function exploration(t,T){
 need(Number.isSafeInteger(t)&&t>=0&&Number.isSafeInteger(T)&&T>=2,'Invalid exploration clock');
 return t===0?1:t>=T-1?.01:Math.exp(-Math.log(100)*t/(T-1));
}
export function nextPhase(phase){need(Number.isInteger(phase)&&phase>=0&&phase<5,'Invalid phase');return phase===0||phase===4?1:phase+1;}
export function isCap(arm,phase){need(['startup','recurring4'].includes(arm),'Invalid arm');return phase===0||(arm==='recurring4'&&phase===4);}
export const phaseAt=t=>{need(Number.isSafeInteger(t)&&t>=0,'Invalid step');return t===0?0:1+(t-1)%4;};
const rowIndex=(n,phase,own,rival)=>(phase*n+own)*n+rival;
function actorValid(s){return Array.isArray(s)&&s.length===4&&s.every(v=>Number.isInteger(v)&&v>=0&&v<=0xffffffff)&&s.some(v=>v!==0);}

export function createLearners(record,arm,{seed=907001,T=2000000,alpha=.1,gamma=19/20,actorStates=null}={}){
 const finite=record.finite??record,n=finite.prices?.length;
 need(Number.isInteger(n)&&n>=1&&n<=62,'Expected 1..62 original quotes');
 need(finite.prices.every((p,i)=>Number.isFinite(p)&&(!i||p>finite.prices[i-1])),'Prices must increase');
 need(Number.isInteger(finite.capIndex)&&finite.capIndex>=0&&finite.capIndex<n,'Invalid cap index');
 need(Array.isArray(finite.sets)&&finite.sets.length===n&&finite.sets.every(s=>Array.isArray(s)&&s.length&&s.every((a,i)=>Number.isInteger(a)&&a>=0&&a<n&&(!i||a>s[i-1]))),'Malformed legal masks');
 need(['startup','recurring4'].includes(arm)&&Number.isSafeInteger(T)&&T>=2&&T<=2000000,'Invalid arm or horizon');
 need(alpha>0&&alpha<=1&&gamma>=0&&gamma<1,'Invalid learning parameters');
 for(const key of ['profitA','profitB','consumerSurplus'])need(finite.rewards?.[key]?.length===n*n&&finite.rewards[key].every(Number.isFinite),'Malformed saved reward '+key);
 const actors=(actorStates??actorNamespaces().find(r=>r.seed===seed)?.actors)?.map(s=>s.slice());
 need(actors?.length===2&&actors.every(actorValid),'Two nonzero unsigned actor states required');
 const rows=5*n*n,cells=rows*n,cap=Array.from({length:finite.capIndex+1},(_,i)=>i);
 const supports=Array.from({length:5},(_,p)=>isCap(arm,p)?Array.from({length:n},()=>cap):finite.sets);
 const q=[new Float64Array(cells),new Float64Array(cells)],counts=[new Uint32Array(cells),new Uint32Array(cells)],best=[new Uint8Array(rows),new Uint8Array(rows)],max=[new Float64Array(rows),new Float64Array(rows)];
 for(let row=0;row<rows;row++)for(let f=0;f<2;f++)best[f][row]=supports[Math.floor(row/(n*n))][row%n][0];
 const windows=[Math.floor(T/2),T].map(endStep=>({startStep:Math.max(0,endStep-100000),endStep,rounds:0,transitions:new Map(),maxAllowed:[0,0],explorations:[0,0],priceChanges:[0,0],capExecutions:0}));
 return{record,finite,arm,seed,T,alpha,gamma,n,rows,cells,cap,supports,q,counts,best,max,actors,t:0,phase:0,previous:[n-1,n-1],caps:0,windows,
  transcriptBuffer:Buffer.alloc(TRANSCRIPT_ROUNDS*TRANSCRIPT_BYTES),transcriptRounds:0,transcriptBlocks:[],learningBlocks:[],blockSummary:null};
}

function writeRecord(buffer,offset,round,phase,pa,pb,a,b,flags,epsilon,rA,rB,oldA,oldB,maxA,maxB,newA,newB,actors){
 buffer.writeUInt32LE(round,offset);buffer[offset+4]=phase;buffer[offset+5]=pa;buffer[offset+6]=pb;buffer[offset+7]=a;buffer[offset+8]=b;buffer[offset+9]=flags;
 buffer.fill(0,offset+10,offset+16);
 buffer.writeDoubleLE(epsilon,offset+16);buffer.writeDoubleLE(rA,offset+24);buffer.writeDoubleLE(rB,offset+32);
 buffer.writeDoubleLE(oldA,offset+40);buffer.writeDoubleLE(oldB,offset+48);buffer.writeDoubleLE(maxA,offset+56);buffer.writeDoubleLE(maxB,offset+64);
 buffer.writeDoubleLE(newA,offset+72);buffer.writeDoubleLE(newB,offset+80);
 for(let f=0;f<2;f++)for(let k=0;k<4;k++)buffer.writeUInt32LE(actors[f][k],offset+88+(f*4+k)*4);
}
export function encodeRound(w){
 need(Number.isInteger(w.round)&&w.round>=1&&w.round<=0xffffffff&&Number.isInteger(w.phase)&&w.phase>=0&&w.phase<5,'Invalid transcript round/phase');
 need([w.previous,w.actions].every(a=>Array.isArray(a)&&a.length===2&&a.every(v=>Number.isInteger(v)&&v>=0&&v<62)),'Invalid transcript indices');
 need(Array.isArray(w.explored)&&w.explored.length===2&&w.explored.every(v=>typeof v==='boolean'),'Invalid exploration flags');
 need(Number.isFinite(w.epsilon)&&w.epsilon>=0&&w.epsilon<=1&&[w.rewards,w.oldQ,w.nextMax,w.newQ].every(a=>Array.isArray(a)&&a.length===2&&a.every(Number.isFinite)),'Invalid transcript floats');
 need(Array.isArray(w.actorsAfter)&&w.actorsAfter.length===2&&w.actorsAfter.every(actorValid),'Invalid transcript actor words');
 const out=Buffer.alloc(120);writeRecord(out,0,w.round,w.phase,...w.previous,...w.actions,(w.explored[0]?1:0)|(w.explored[1]?2:0),w.epsilon,...w.rewards,...w.oldQ,...w.nextMax,...w.newQ,w.actorsAfter);return out;
}
function updateCache(m,f,row,action,value){
 const current=m.max[f][row];
 if(value>current||(value===current&&action<m.best[f][row])){m.max[f][row]=value;m.best[f][row]=action;}
 else if(action===m.best[f][row]&&value<current){
  const legal=m.supports[Math.floor(row/(m.n*m.n))][row%m.n],off=row*m.n;
  let winner=legal[0];for(let i=1;i<legal.length;i++)if(m.q[f][off+legal[i]]>m.q[f][off+winner])winner=legal[i];
  m.best[f][row]=winner;m.max[f][row]=m.q[f][off+winner];
 }
}
export function step(m,{trace=false}={}){
 need(m.t<m.T,'Declared training horizon exhausted');
 const n=m.n,p=m.phase,pa=m.previous[0],pb=m.previous[1],rowA=rowIndex(n,p,pa,pb),rowB=rowIndex(n,p,pb,pa),eps=exploration(m.t,m.T);
 const uA=randomWord(m.actors[0])/2**32,vA=randomWord(m.actors[0])/2**32,uB=randomWord(m.actors[1])/2**32,vB=randomWord(m.actors[1])/2**32;
 const legalA=m.supports[p][pb],legalB=m.supports[p][pa],exploreA=uA<eps,exploreB=uB<eps;
 const a=exploreA?legalA[Math.floor(vA*legalA.length)]:m.best[0][rowA],b=exploreB?legalB[Math.floor(vB*legalB.length)]:m.best[1][rowB];
 const next=nextPhase(p),nextRowA=rowIndex(n,next,a,b),nextRowB=rowIndex(n,next,b,a),cellA=rowA*n+a,cellB=rowB*n+b,index=a*n+b;
 const rA=m.finite.rewards.profitA[index],rB=m.finite.rewards.profitB[index],oldA=m.q[0][cellA],oldB=m.q[1][cellB];
 // Both bootstrap maxima and old Q values are captured before either update.
 const maxA=m.max[0][nextRowA],maxB=m.max[1][nextRowB],targetA=rA+m.gamma*maxA,targetB=rB+m.gamma*maxB;
 const newA=oldA+m.alpha*(targetA-oldA),newB=oldB+m.alpha*(targetB-oldB);
 need(Number.isFinite(newA)&&Number.isFinite(newB),'Nonfinite Q update');
 m.q[0][cellA]=newA;m.q[1][cellB]=newB;m.counts[0][cellA]++;m.counts[1][cellB]++;
 updateCache(m,0,rowA,a,newA);updateCache(m,1,rowB,b,newB);
 const cap=isCap(m.arm,p),flags=(exploreA?1:0)|(exploreB?2:0);
 writeRecord(m.transcriptBuffer,m.transcriptRounds*120,m.t+1,p,pa,pb,a,b,flags,eps,rA,rB,oldA,oldB,maxA,maxB,newA,newB,m.actors);
 m.transcriptRounds++;
 if(!m.blockSummary)m.blockSummary={firstRound:m.t+1,lastRound:null,rounds:0,consumerSurplusSum:0,profitSums:[0,0],priceSums:[0,0],explorations:[0,0],maxAllowed:[0,0],capExecutions:0};
 const summary=m.blockSummary;summary.rounds++;summary.consumerSurplusSum+=m.finite.rewards.consumerSurplus[index];summary.profitSums[0]+=rA;summary.profitSums[1]+=rB;summary.priceSums[0]+=m.finite.prices[a];summary.priceSums[1]+=m.finite.prices[b];summary.explorations[0]+=exploreA?1:0;summary.explorations[1]+=exploreB?1:0;summary.maxAllowed[0]+=a===legalA.at(-1)?1:0;summary.maxAllowed[1]+=b===legalB.at(-1)?1:0;summary.capExecutions+=cap?1:0;
 if(m.transcriptRounds===10000){m.transcriptBlocks.push({block:m.transcriptBlocks.length+1,firstRound:m.t+1-9999,lastRound:m.t+1,rounds:10000,bytes:1200000,sha256:sha(m.transcriptBuffer)});summary.lastRound=m.t+1;m.learningBlocks.push(summary);m.blockSummary=null;m.transcriptRounds=0;}
 for(const w of m.windows)if(m.t>=w.startStep&&m.t<w.endStep){
  const key=rowA*n*n+index;w.transitions.set(key,(w.transitions.get(key)??0)+1);w.rounds++;w.maxAllowed[0]+=a===legalA.at(-1)?1:0;w.maxAllowed[1]+=b===legalB.at(-1)?1:0;
  w.explorations[0]+=exploreA?1:0;w.explorations[1]+=exploreB?1:0;w.priceChanges[0]+=a!==pa?1:0;w.priceChanges[1]+=b!==pb?1:0;w.capExecutions+=cap?1:0;
 }
 m.caps+=cap?1:0;m.t++;m.phase=next;m.previous[0]=a;m.previous[1]=b;
 return trace?{round:m.t,phase:p,previous:[pa,pb],actions:[a,b],explored:[exploreA,exploreB],epsilon:eps,rewards:[rA,rB],oldQ:[oldA,oldB],nextMax:[maxA,maxB],newQ:[newA,newB],actorsAfter:m.actors.map(s=>s.slice()),nextPhase:next}:undefined;
}
export function advanceTo(m,endStep){need(Number.isSafeInteger(endStep)&&endStep>=m.t&&endStep<=m.T,'Invalid advance endpoint');while(m.t<endStep)step(m);return m;}
export function f64Bytes(array){const out=Buffer.allocUnsafe(array.length*8);for(let i=0;i<array.length;i++)out.writeDoubleLE(array[i],i*8);return out;}
export function u32Bytes(array){const out=Buffer.allocUnsafe(array.length*4);for(let i=0;i<array.length;i++)out.writeUInt32LE(array[i],i*4);return out;}
export function rebuildMaxima(m){
 for(let f=0;f<2;f++)for(let row=0;row<m.rows;row++){
  const legal=m.supports[Math.floor(row/(m.n*m.n))][row%m.n],off=row*m.n;let winner=legal[0];
  for(let k=1;k<legal.length;k++)if(m.q[f][off+legal[k]]>m.q[f][off+winner])winner=legal[k];
  m.best[f][row]=winner;m.max[f][row]=m.q[f][off+winner];
 }
}
export function validateState(m,{checkCaches=true}={}){
 need(m.phase===phaseAt(m.t),'NEXT clock differs from completed round count');
 need(m.previous.length===2&&m.previous.every(i=>Number.isInteger(i)&&i>=0&&i<m.n),'Malformed terminal history');
 if(m.t===0)need(m.previous.every(i=>i===m.n-1),'Initial history differs');
 need(m.caps===(m.t===0?0:m.arm==='startup'?1:Math.ceil(m.t/4)),'Cap count differs');
 for(let f=0;f<2;f++){
  let count=0;
  for(let row=0;row<m.rows;row++){
   const legal=m.supports[Math.floor(row/(m.n*m.n))][row%m.n],allowed=new Set(legal),off=row*m.n;let winner=legal[0];
   for(let a=0;a<m.n;a++){const q=m.q[f][off+a],visits=m.counts[f][off+a];need(Number.isFinite(q),'Nonfinite Q cell');count+=visits;if(!allowed.has(a))need(Object.is(q,0)&&visits===0,'Forbidden dense cell changed');}
   for(let k=1;k<legal.length;k++)if(m.q[f][off+legal[k]]>m.q[f][off+winner])winner=legal[k];
   if(checkCaches)need(m.best[f][row]===winner&&Object.is(m.max[f][row],m.q[f][off+winner]),'Cached maximum differs from legal scan');
  }
  need(count===m.t,'Global action counts differ from training step');
 }
 need(m.transcriptBlocks.length===Math.floor(m.t/10000)&&m.transcriptRounds===m.t%10000,'Transcript block clock differs');
 m.transcriptBlocks.forEach((b,i)=>need(b.block===i+1&&b.firstRound===i*10000+1&&b.lastRound===(i+1)*10000&&b.rounds===10000&&b.bytes===1200000&&/^[a-f0-9]{64}$/.test(b.sha256),'Malformed transcript block inventory'));
 return true;
}
export function modelIdentity(m){
 return{step:m.t,phase:m.phase,previousIndices:m.previous.slice(),actorStates:m.actors.map(s=>s.slice()),capExecutions:m.caps,qSha256:m.q.map(q=>sha(f64Bytes(q))),countSha256:m.counts.map(c=>sha(u32Bytes(c))),bestCacheSha256:m.best.map(a=>sha(a)),maxCacheSha256:m.max.map(a=>sha(f64Bytes(a))),
  transcriptBlocks:m.transcriptBlocks.map(b=>({...b})),transcriptPartial:{rounds:m.transcriptRounds,bytes:m.transcriptRounds*120,sha256:sha(m.transcriptBuffer.subarray(0,m.transcriptRounds*120)),scope:'Incomplete engineering tail, not a completed block'},
  windows:m.windows.map(w=>({...w,maxAllowed:w.maxAllowed.slice(),explorations:w.explorations.slice(),priceChanges:w.priceChanges.slice(),transitions:[...w.transitions].sort((a,b)=>a[0]-b[0])}))};
}
// Artificial engineering inputs only; not a calibrated market or experiment.
export function syntheticMatchedRecord(n=62){
 need(Number.isInteger(n)&&n>=2&&n<=62,'Artificial dimension must be 2..62');
 const prices=Array.from({length:n},(_,i)=>1+i/n),upper=Array.from({length:n},(_,j)=>Math.min(n-1,Math.floor(j/2)+6));
 const sets=upper.map(u=>Array.from({length:Math.min(7,u+1)},(_,k)=>u-Math.min(6,u)+k)),rewards={profitA:[],profitB:[],consumerSurplus:[],quantityA:[],quantityB:[]};
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){rewards.profitA.push((a*3+b*5)%17-8);rewards.profitB.push((b*7+a*2)%19-9);rewards.consumerSurplus.push(200-a-b);rewards.quantityA.push(50-a/2);rewards.quantityB.push(50-b/2);}
 return{scenario:{id:'artificial-matched-clock-engineering-only'},originalTargets:[],finite:{prices,capIndex:Math.min(5,n-1),sets,upper,rewards},scope:'Wholly artificial signed/zero reward engineering fixture; not an inherited market or scientific outcome'};
}
