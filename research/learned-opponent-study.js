// Prospective primary. Importing this module reads no evidence and solves no case.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
import {binary64,integerWeights} from './incentive-study.js';
import {layout,nextPhase} from './adaptive-learning.js';
export const MAX_BITS=1000000,MAX_CANDIDATE_BITS=4096,MAX_STATES=15376,QUANTIZATION_BITS=32;
const need=(ok,message)=>{if(!ok)throw Error(message);},abs=x=>x<0n?-x:x;
export const bitLength=x=>abs(x).toString(2).length;
function bounded(x,limit=MAX_BITS){need(typeof x==='bigint'&&bitLength(x)<=limit,'Exact integer bit budget exceeded');return x;}
export function guardedMultiply(a,b){need(bitLength(a)+bitLength(b)<=MAX_BITS,'Product exceeds prospective integer budget');return bounded(a*b);}
function guardedAdd(a,b){need(Math.max(bitLength(a),bitLength(b))+1<=MAX_BITS,'Sum exceeds prospective integer budget');return bounded(a+b);}
function pow(a,n){need(Number.isInteger(n)&&n>=0&&n<=MAX_STATES,'Discount exponent exceeds complete-state bound');need(n*bitLength(a)+1<=MAX_BITS,'Power exceeds prospective integer budget');return bounded(a**BigInt(n));}
function gcd(a,b){a=abs(a);b=abs(b);while(b){const r=a%b;a=b;b=r;}return a;}
export function fraction(n,d=1n){n=bounded(n);d=bounded(d);need(d!==0n,'Zero exact denominator');if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return{n:n/g,d:d/g};}
const plus=(a,b)=>fraction(guardedAdd(guardedMultiply(a.n,b.d),guardedMultiply(b.n,a.d)),guardedMultiply(a.d,b.d));
const minus=(a,b)=>plus(a,{n:-b.n,d:b.d});
const times=(a,b)=>fraction(guardedMultiply(a.n,b.n),guardedMultiply(a.d,b.d));
export const compareFractions=(a,b)=>{const x=guardedMultiply(a.n,b.d),y=guardedMultiply(b.n,a.d);return x<y?-1:x>y?1:0;};
export const sign=a=>a.n<0n?'negative':a.n>0n?'positive':'zero';
export const hex=x=>(x<0n?'-0x':'0x')+abs(bounded(x)).toString(16);
export function parseHex(text,limit=MAX_BITS){
 need(typeof text==='string'&&text.length<=Math.ceil(limit/4)+4,'Hex token exceeds bit budget before parsing');
 need(typeof text==='string'&&/^-?0x(?:0|[1-9a-f][0-9a-f]*)$/.test(text)&&text!=='-0x0','Noncanonical signed hexadecimal integer');
 const negative=text[0]==='-',body=text.slice(negative?3:2);
 need((body.length-1)*4+1<=limit,'Hex token exceeds bit budget before parsing');
 const value=BigInt('0x'+body);return bounded(negative?-value:value,limit);
}
export const pack=a=>({numeratorHex:hex(a.n),denominatorHex:hex(a.d)});
export function unpack(a){need(a&&typeof a==='object','Missing exact hex fraction');const n=parseHex(a.numeratorHex),d=parseHex(a.denominatorHex);need(d>0n,'Positive exact denominator required');const r=fraction(n,d);need(r.n===n&&r.d===d,'Exact scalar must be reduced');return r;}
export const GAP_TARGET=fraction(1n,1000000n);
export function quantize(value){
 need(typeof value==='number'&&Number.isFinite(value),'Finite final binary64 proposal required');const r=binary64(value),n=guardedMultiply(r.n,1n<<32n),q=n/r.d,rem=abs(n%r.d),twice=2n*rem;
 const rounded=twice>r.d||(twice===r.d&&(abs(q)&1n)===1n)?q+(n<0n?-1n:1n):q;return bounded(rounded,MAX_CANDIDATE_BITS);
}
export function vectorBytes(values){need(values.length>0&&values.length<=MAX_STATES,'Invalid candidate vector dimension');return Buffer.from(values.map(x=>hex(bounded(x,MAX_CANDIDATE_BITS))).join('\n')+'\n');}
export function parseVector(bytes,count){need(Number.isInteger(count)&&count>0&&count<=MAX_STATES,'Invalid candidate vector dimension');need(Buffer.isBuffer(bytes)&&bytes.length<=count*(Math.ceil(MAX_CANDIDATE_BITS/4)+5),'Candidate vector byte budget exceeded before decoding');const text=bytes.toString('utf8');need(text.endsWith('\n'),'Candidate vector final newline required');const rows=text.slice(0,-1).split('\n');need(rows.length===count,'Candidate vector dimension differs');return rows.map(s=>parseHex(s,MAX_CANDIDATE_BITS));}
export function float64Bytes(values){need(values.length>0&&values.length<=MAX_STATES,'Invalid proposal vector dimension');const b=Buffer.alloc(values.length*8);values.forEach((v,i)=>{need(Number.isFinite(v),'Nonfinite proposal vector');b.writeDoubleLE(v,i*8);});return b;}

function boundedLayout(finite,control){const n=finite?.prices?.length;need(Number.isInteger(n)&&n>0&&n<=62&&Number.isInteger(control?.phases)&&control.phases>0&&control.phases*n*n<=MAX_STATES,'Complete state dimensions exceed prospective bound');need(control.id==='startup-only'?control.phases===2&&control.period===null:control.id==='selected95'&&control.phases===control.period,'Original controller clock identity differs');return layout(finite,control);}

export function reconstructGreedy(finite,control,q,counts,overflow=[[],[]],{expectedRounds=null}={}){
 const L=boundedLayout(finite,control),n=L.n,N=L.rows;need(N<=MAX_STATES,'Complete state budget exceeded');
 need(q?.length===2&&counts?.length===2&&overflow?.length===2,'Both saved firms are required');
 const actorPolicies=[new Uint8Array(N),new Uint8Array(N)],rowVisits=[new Uint32Array(N),new Uint32Array(N)],actionCounts=[],totalActionCounts=[];
 for(let f=0;f<2;f++){
  need(q[f].length===L.cells&&counts[f].length===L.cells,'Saved Q/count dimensions differ');
  const extra=new Map();let previous=-1;for(const pair of overflow[f]){need(Array.isArray(pair)&&pair.length===2,'Malformed overflow entry');const [cell,count]=pair;need(Number.isInteger(cell)&&cell>previous&&cell<L.cells&&counts[f][cell]===65535&&Number.isSafeInteger(count)&&count>65535&&count<=2000000,'Malformed original count overflow');extra.set(cell,count);previous=cell;}
  const cells=new Uint32Array(L.cells);
  for(let k=0;k<L.cells;k++){need(Number.isInteger(counts[f][k])&&counts[f][k]>=0&&counts[f][k]<=65535&&Number.isFinite(q[f][k]),'Malformed saved Q/count cell');cells[k]=extra.get(k)??counts[f][k];}
  for(let row=0;row<N;row++){
   const phase=Math.floor(row/(n*n)),support=L.support(phase,row%n),offset=L.offsets[row];let best=0,total=0;
   for(let k=0;k<support.length;k++){if(q[f][offset+k]>q[f][offset+best])best=k;total+=cells[offset+k];}
   need(Number.isSafeInteger(total)&&total<=2000000,'Original state visits exceed training horizon');actorPolicies[f][row]=support[best];rowVisits[f][row]=total;
  }
  const total=Array.from(cells).reduce((sum,x)=>sum+x,0);need(Number.isSafeInteger(total),'Original exact count total exceeds safe integer');if(expectedRounds!==null)need(total===expectedRounds,'Original action count total differs from training horizon');totalActionCounts.push(total);actionCounts.push(cells);
 }
 const worldPolicies=[new Uint8Array(N),new Uint8Array(N)];
 for(let s=0;s<N;s++){const phase=Math.floor(s/(n*n)),i=Math.floor(s/n)%n,j=s%n;worldPolicies[0][s]=actorPolicies[0][s];worldPolicies[1][s]=actorPolicies[1][phase*n*n+j*n+i];}
 function supportCount(f,state,action){const phase=Math.floor(state/(n*n)),i=Math.floor(state/n)%n,j=state%n,row=phase*n*n+(f===0?i*n+j:j*n+i),rival=f===0?j:i,rank=L.rank(phase,rival,action);need(rank>=0,'Coverage action is not legal');return{stateVisits:rowVisits[f][row],chosenActionVisits:actionCounts[f][L.offsets[row]+rank]};}
 return {L,worldPolicies,supportCount,totalActionCounts};
}

export function prepareMDP(record,control,worldPolicies,focal='A',supportCount=()=>({stateVisits:0,chosenActionVisits:0})){
 const f=record.finite??record,L=boundedLayout(f,control),n=L.n,N=L.rows;need(N<=MAX_STATES&&['A','B'].includes(focal),'Invalid full-state MDP identity');
 for(const key of ['profitA','profitB','consumerSurplus'])need(f.rewards[key]?.length===n*n&&f.rewards[key].every(Number.isFinite),'Saved numerical reward table missing');
 need(worldPolicies?.length===2&&worldPolicies.every(p=>p.length===N),'Both full-world greedy policies required');
 const focalIndex=focal==='A'?0:1,opponent=worldPolicies[1-focalIndex],baseline=worldPolicies[focalIndex],offsets=new Uint32Array(N+1);
 for(let s=0;s<N;s++){const phase=Math.floor(s/(n*n)),i=Math.floor(s/n)%n,j=s%n;for(let actor=0;actor<2;actor++)need(L.support(phase,actor===0?j:i).includes(worldPolicies[actor][s]),'Original greedy policy is illegal');offsets[s+1]=offsets[s]+L.support(phase,focalIndex===0?j:i).length;}
 const E=offsets[N],actions=new Uint8Array(E),successors=new Uint32Array(E),pairs=new Uint16Array(E);
 for(let s=0;s<N;s++){
  const phase=Math.floor(s/(n*n)),i=Math.floor(s/n)%n,j=s%n,support=L.support(phase,focalIndex===0?j:i),clock=nextPhase(control,phase);
  for(let k=0;k<support.length;k++){const e=offsets[s]+k,own=support[k],a=focalIndex===0?own:opponent[s],b=focalIndex===0?opponent[s]:own;actions[e]=own;pairs[e]=a*n+b;successors[e]=clock*n*n+a*n+b;}
 }
 const rawRewards=f.rewards[focalIndex===0?'profitA':'profitB'],weights=integerWeights(rawRewards),csWeights=integerWeights(f.rewards.consumerSurplus);
 need(weights.denominator>0n&&bitLength(weights.denominator)<=1075&&weights.weights.every(x=>bitLength(x)<=2099),'Binary64 reward size premise differs');
 function edge(state,action){need(Number.isInteger(state)&&state>=0&&state<N,'Invalid world state');const begin=offsets[state],end=offsets[state+1];for(let e=begin;e<end;e++)if(actions[e]===action)return e;throw Error('Proposed response action is illegal');}
 return {record,finite:f,control:{...control},n,N,E,L,focal,focalIndex,worldPolicies,opponent,baseline,offsets,actions,successors,pairs,rawRewards,weights,csWeights,edge,supportCount};
}

export function iterateValues(mdp,{maxSweeps=600,tolerance=1e-10,onIteration=()=>{}}={}){
 need(Number.isInteger(maxSweeps)&&maxSweeps>=1&&maxSweeps<=600&&tolerance===1e-10,'Prospective proposal settings differ');
 let v=new Float64Array(mdp.N),next=new Float64Array(mdp.N),difference=Infinity,iterations=0,stopReason='maximum completed sweeps';
 for(let sweep=1;sweep<=maxSweeps;sweep++){
  difference=0;
  for(let s=0;s<mdp.N;s++){
   let best=-Infinity;for(let e=mdp.offsets[s];e<mdp.offsets[s+1];e++){const x=mdp.rawRewards[mdp.pairs[e]]+(19/20)*v[mdp.successors[e]];need(Number.isFinite(x),'Nonfinite approximate Bellman proposal');if(x>best)best=x;}
   next[s]=best;difference=Math.max(difference,Math.abs(best-v[s]));
  }
  [v,next]=[next,v];iterations=sweep;onIteration({completedSweeps:sweep,difference,values:v});
  if(difference<=tolerance){stopReason='completed floating difference threshold';break;}
 }
 return {values:v,completedSweeps:iterations,difference,stopReason,optimizerIterationsReplayed:false};
}

export function bellmanCertificate(mdp,floatValues){
 need(floatValues.length===mdp.N,'Final proposal length differs');const dyadic=Array.from(floatValues,quantize),D=mdp.weights.denominator,L=D>(1n<<32n)?D:1n<<32n,scale=L/(1n<<32n),Z=dyadic.map(z=>guardedMultiply(z,scale)),R=mdp.weights.weights.map(r=>guardedMultiply(r,L/D)),policy=new Uint8Array(mdp.N);
 let M=null,witness=null,checked=0;
 for(let s=0;s<mdp.N;s++){
  let best=null,action=null;for(let e=mdp.offsets[s];e<mdp.offsets[s+1];e++){
   const score=guardedAdd(guardedMultiply(20n,R[mdp.pairs[e]]),guardedMultiply(19n,Z[mdp.successors[e]])),residual=guardedAdd(score,-guardedMultiply(20n,Z[s]));checked++;
   if(best===null||score>best){best=score;action=mdp.actions[e];}
   if(M===null||residual>M){M=residual;witness={sourceState:s,action:mdp.actions[e],nextState:mdp.successors[e],payoffIndex:mdp.pairs[e]};}
  }policy[s]=action;
 }
 need(checked===mdp.E&&M!==null,'Every legal edge must be checked');
 return {dyadic,policy,L,M,maximumWitness:witness,allEdgesChecked:checked,upperValue:state=>{need(Number.isInteger(state)&&state>=0&&state<mdp.N,'Upper-value state invalid');return fraction(guardedAdd(Z[state],M),L);}};
}

function polynomial(values){let acc=0n,qPower=1n;for(let i=values.length-1;i>=0;i--){acc=guardedAdd(guardedMultiply(values[i],qPower),guardedMultiply(19n,acc));qPower=guardedMultiply(qPower,20n);}return {acc,qPower};}
export function discountedPathValue(values,denominator,h,c){
 need(Number.isInteger(h)&&h>=0&&Number.isInteger(c)&&c>0&&h+c===values.length&&values.length<=MAX_STATES,'Invalid complete transient/cycle dimensions');
 need(typeof denominator==='bigint'&&denominator>0n,'Positive reward denominator required');bounded(denominator);values.forEach(x=>bounded(x));
 need(8*values.length*5+8*4096+16384<MAX_BITS,'Prospective arithmetic size proof failed');
 const pre=polynomial(values.slice(0,h)),cyc=polynomial(values.slice(h)),difference=guardedAdd(cyc.qPower,-pow(19n,c));need(difference>0n,'Discounted cycle denominator must be positive');
 const numerator=guardedAdd(guardedMultiply(guardedMultiply(20n,pre.acc),difference),guardedMultiply(guardedMultiply(pow(19n,h),20n),cyc.acc)),den=guardedMultiply(guardedMultiply(denominator,pre.qPower),difference);
 return fraction(numerator,den);
}

export function walkPolicy(mdp,policy,start){
 need(policy.length===mdp.N&&Number.isInteger(start)&&start>=0&&start<mdp.N,'Invalid policy/terminal dimension');
 // Check off-path legality too; the independent audit separately rechecks argmax.
 for(let s=0;s<mdp.N;s++)mdp.edge(s,policy[s]);
 const first=new Int32Array(mdp.N).fill(-1),states=[],executedA=[],executedB=[],nextStates=[],payoffIndices=[],coverage={A:{stateVisits:[],chosenActionVisits:[]},B:{stateVisits:[],chosenActionVisits:[]}};let at=start;
 while(first[at]===-1){
  need(states.length<mdp.N,'Path exceeded complete-state bound');first[at]=states.length;const e=mdp.edge(at,policy[at]),pair=mdp.pairs[e],a=Math.floor(pair/mdp.n),b=pair%mdp.n;
  states.push(at);executedA.push(a);executedB.push(b);payoffIndices.push(pair);nextStates.push(mdp.successors[e]);
  for(const [actor,name] of [[0,'A'],[1,'B']]){const v=mdp.supportCount(actor,at,actor===0?a:b);need(Number.isSafeInteger(v.stateVisits)&&v.stateVisits>=0&&v.stateVisits<=2000000&&Number.isSafeInteger(v.chosenActionVisits)&&v.chosenActionVisits>=0&&v.chosenActionVisits<=v.stateVisits,'Original training support inconsistent');coverage[name].stateVisits.push(v.stateVisits);coverage[name].chosenActionVisits.push(v.chosenActionVisits);}
  at=mdp.successors[e];
 }
 const h=first[at],c=states.length-h,value=discountedPathValue(payoffIndices.map(i=>mdp.weights.weights[i]),mdp.weights.denominator,h,c),support={};
 for(const name of ['A','B']){
  const entries=coverage[name],stateFlags=entries.stateVisits.map(v=>v===0?1n:0n),actionFlags=entries.chosenActionVisits.map(v=>v===0?1n:0n),stateExposure=times(discountedPathValue(stateFlags,1n,h,c),fraction(1n,20n)),actionExposure=times(discountedPathValue(actionFlags,1n,h,c),fraction(1n,20n));
  need(compareFractions(stateExposure,fraction(0n))>=0&&compareFractions(stateExposure,fraction(1n))<=0&&compareFractions(actionExposure,fraction(0n))>=0&&compareFractions(actionExposure,fraction(1n))<=0,'Discounted training-support exposure outside[0,1]');
  support[name]={unweighted:{states:states.length,unvisitedStates:stateFlags.filter(x=>x===1n).length,neverTriedChosenActions:actionFlags.filter(x=>x===1n).length,minimumStateVisits:Math.min(...entries.stateVisits),minimumChosenActionVisits:Math.min(...entries.chosenActionVisits)},discounted:{unvisitedStateExposure:pack(stateExposure),neverTriedChosenActionExposure:pack(actionExposure)}};
 }
 const cycleCS=payoffIndices.slice(h).reduce((sum,i)=>guardedAdd(sum,mdp.csWeights.weights[i]),0n),eventualCycleCustomerBenefit=fraction(cycleCS,guardedMultiply(mdp.csWeights.denominator,BigInt(c)));
 return {path:{states,executedA,executedB,nextStates,payoffIndices,h,c,closingState:at,coverage},value,coverage:support,eventualCycleCustomerBenefit};
}

export function evaluateProposal(mdp,values,start){
 const cert=bellmanCertificate(mdp,values),baseline=walkPolicy(mdp,mdp.baseline,start),response=walkPolicy(mdp,cert.policy,start),upper=cert.upperValue(start),gap=minus(upper,response.value),rawGain=minus(response.value,baseline.value),bestUpper=minus(upper,baseline.value),lower=rawGain.n>0n?rawGain:fraction(0n);
 need(gap.n>=0n&&bestUpper.n>=0n&&compareFractions(lower,bestUpper)<=0,'Invalid exact Bellman/achieved-value certificate');
 const relative=baseline.value.n>0n?fraction(guardedMultiply(rawGain.n,baseline.value.d),guardedMultiply(rawGain.d,baseline.value.n)):null;
 return {baseline,response,candidate:cert,certificate:{passed:true,commonDenominatorHex:hex(cert.L),maximumResidualNumeratorHex:hex(cert.M),maximumWitness:cert.maximumWitness,allEdgesChecked:cert.allEdgesChecked,upperValue:pack(upper),responseOptimalityGap:pack(gap),requestedGap:pack(GAP_TARGET),withinRequestedGap:compareFractions(gap,GAP_TARGET)<=0},performance:{rawGain:pack(rawGain),rawGainSign:sign(rawGain),possibleGain:{lower:pack(lower),upper:pack(bestUpper)},relativeGain:relative?pack(relative):null,relativeGainReason:relative?null:'Exact baseline is zero or negative',cycleCustomerBenefitDifference:pack(minus(response.eventualCycleCustomerBenefit,baseline.eventualCycleCustomerBenefit))}};
}

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export const STATUS=Object.freeze({tight:'certified response within gap target',loose:'certified response with loose gap',timeout:'retained hard-budget timeout',input:'retained input failure',proposal:'retained proposal failure',certificate:'retained certificate failure',worker:'retained worker failure'});
export function plannedCases(){const rows=[];for(let seed=907001;seed<=907012;seed++)for(const id of ['startup-only','selected95'])for(const focal of ['A','B']){const oldRunID=`base-g15-t1--${id}--zero--s${seed}`;rows.push({id:oldRunID+'--focal'+focal,oldRunID,scenario:'base-g15-t1',seed,initialization:'zero',control:id==='startup-only'?{id,period:null,phases:2}:{id,period:4,phases:4},focal,checkpointStep:2000000});}return rows;}
export function contained(root,file){const base=path.resolve(root),absolute=path.resolve(base,file);need(absolute.startsWith(base+path.sep),'Artifact escapes declared directory');return absolute;}
export function writeArtifact(directory,file,bytes){const full=contained(directory,file);need(Buffer.isBuffer(bytes),'Artifact bytes required');fs.mkdirSync(path.dirname(full),{recursive:true});fs.writeFileSync(full,bytes,{flag:'wx'});return{file,bytes:bytes.length,sha256:hash(bytes)};}
export function verifyArtifact(directory,ref){need(ref&&typeof ref.file==='string'&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&/^[a-f0-9]{64}$/.test(ref.sha256),'Malformed artifact reference');const file=contained(directory,ref.file);need(fs.statSync(file).size===ref.bytes,'Artifact size differs');const b=fs.readFileSync(file);need(hash(b)===ref.sha256,'Artifact hash differs');return b;}
const jsonBytes=value=>Buffer.from(JSON.stringify(value)+'\n');
export function scientificArtifactRefs(report){return[report.optimizer?.finalFloat64,report.optimizer?.dyadicValues,report.optimizer?.responsePolicy,report.baseline?.path,report.response?.path];}
export function validateCompleteReport(directory,ref,plan){
 const report=JSON.parse(verifyArtifact(directory,ref));need(report.id===plan.id&&report.focal===plan.focal&&report.scenario===plan.scenario&&report.seed===plan.seed&&report.checkpointStep===plan.checkpointStep,'Complete report identity differs');
 need(report.initialization===plan.initialization&&report.control.id===plan.control.id&&report.control.period===plan.control.period&&report.control.phases===plan.control.phases,'Complete report original controller identity differs');
 need(report.certificate?.passed===true&&typeof report.certificate.withinRequestedGap==='boolean'&&Number.isSafeInteger(report.certificate.allEdgesChecked)&&report.certificate.allEdgesChecked>0,'A full all-edge certificate is required');
 for(const artifact of scientificArtifactRefs(report))verifyArtifact(directory,artifact);
 need(Number.isInteger(report.mdp?.states)&&report.mdp.states>0&&report.mdp.states<=MAX_STATES&&report.mdp.edges===report.certificate.allEdgesChecked,'Complete MDP certificate dimensions differ');
 need(report.optimizer.finalFloat64.bytes===report.mdp.states*8&&report.optimizer.responsePolicy.bytes===report.mdp.states,'Complete candidate/policy dimensions differ');parseVector(verifyArtifact(directory,report.optimizer.dyadicValues),report.mdp.states);
 for(const r of [report.baseline,report.response]){const p=JSON.parse(verifyArtifact(directory,r.path));need(p.h===r.h&&p.c===r.c&&Number.isInteger(p.h)&&p.h>=0&&Number.isInteger(p.c)&&p.c>0&&p.h+p.c<=report.mdp.states,'Complete path decomposition missing');for(const name of ['states','executedA','executedB','nextStates','payoffIndices'])need(Array.isArray(p[name])&&p[name].length===p.h+p.c,'Complete path array missing');for(const actor of ['A','B'])for(const key of ['stateVisits','chosenActionVisits'])need(p.coverage?.[actor]?.[key]?.length===p.h+p.c,'Complete support witness missing');}
 for(const value of [report.baseline?.value,report.response?.value,report.certificate.upperValue,report.certificate.responseOptimalityGap,report.performance?.rawGain,report.performance?.possibleGain?.lower,report.performance?.possibleGain?.upper])unpack(value);
 return report;
}
export function solveLoadedCase(plan,{mdp,start,input},directory,{onIteration=()=>{},onStage=()=>{}}={}){
 need(Number.isInteger(start)&&start>=0&&start<mdp.N,'Invalid actual terminal node');const prefix='artifacts/'+plan.id+'/',began=performance.now();
 onStage('proposal');const proposal=iterateValues(mdp,{onIteration});onStage('exact certificate');const result=evaluateProposal(mdp,proposal.values,start);
 const finalFloat64=writeArtifact(directory,prefix+'proposal.f64le',float64Bytes(proposal.values)),dyadicValues=writeArtifact(directory,prefix+'values.hex',vectorBytes(result.candidate.dyadic)),responsePolicy=writeArtifact(directory,prefix+'response-policy.u8',Buffer.from(result.candidate.policy));
 const baselinePath=writeArtifact(directory,prefix+'baseline-path.json',jsonBytes(result.baseline.path)),responsePath=writeArtifact(directory,prefix+'response-path.json',jsonBytes(result.response.path));
 const pathResult=(r,ref)=>({value:pack(r.value),path:ref,h:r.path.h,c:r.path.c,coverage:r.coverage,eventualCycleCustomerBenefit:pack(r.eventualCycleCustomerBenefit)}),n=mdp.n;
 const report={...plan,input,mdp:{n,states:mdp.N,edges:mdp.E,coordinateOrder:'World (phase,previousA,previousB), row-major; B Q lookup alone transposes',terminal:{node:start,phase:Math.floor(start/(n*n)),previousIndices:[Math.floor(start/n)%n,start%n]},focalRewardOrientation:`Original ${plan.focal==='A'?'profitA':'profitB'}[executedA*n+executedB]`,opponentWorldPolicySha256:hash(Buffer.from(mdp.opponent)),baselineWorldPolicySha256:hash(Buffer.from(mdp.baseline))},optimizer:{completedSweeps:proposal.completedSweeps,stopReason:proposal.stopReason,floatDifference:proposal.difference,maximumSweeps:600,floatStoppingThreshold:1e-10,hardBudgetSeconds:300,optimizerIterationsReplayed:false,quantization:{denominatorPower:32,ties:'nearest-even exact binary64 rational'},finalFloat64,dyadicValues,responsePolicy},baseline:pathResult(result.baseline,baselinePath),response:pathResult(result.response,responsePath),certificate:result.certificate,performance:result.performance,workerComputationSeconds:(performance.now()-began)/1000};
 const complete=writeArtifact(directory,prefix+'complete-certificate.json',jsonBytes(report));return{report,complete};
}

const ADAPTIVE='research/adaptive-learning-results/';
export const V10_ARCHIVE_SHA256='5b494614af0efabe6a416814604a4914fb8e5492d6d78fb106d5a09b8497bdcf',V10_RECEIPT_SHA256='e2915ad87588a781abf3c925209b8bf450ba4fab13cc49dcffac4b9b1aa2979e';
const readJSON=(root,file)=>JSON.parse(fs.readFileSync(contained(root,file),'utf8'));
const sameJSON=(a,b,message)=>need(JSON.stringify(a)===JSON.stringify(b),message);
function fileDigest(file){const h=crypto.createHash('sha256'),fd=fs.openSync(file,'r'),chunk=Buffer.allocUnsafe(1024*1024);try{let bytes;while((bytes=fs.readSync(fd,chunk,0,chunk.length,null))>0)h.update(chunk.subarray(0,bytes));}finally{fs.closeSync(fd);}return h.digest('hex');}
export function projectReference(root,file,expected=null){const full=contained(root,file),ref={file:file.replaceAll('\\','/'),bytes:fs.statSync(full).size,sha256:fileDigest(full)};if(expected!==null)need(ref.sha256===expected,'Inherited file identity differs '+file);return ref;}
function verifyProjectReference(root,ref,declaredHashes=null){if(declaredHashes)need(declaredHashes[ref.file]===ref.sha256,'Inherited reference is not bound by frozen input map '+ref.file);return verifyArtifact(root,ref);}
export function identifyInputs(plan,{projectRoot=ROOT,index=null,declaredHashes=null}={}){
 const indexed=index??readJSON(projectRoot,ADAPTIVE+'index.json'),matches=indexed.records.filter(r=>r.id===plan.oldRunID);need(matches.length===1,'Original indexed run missing or duplicated');const row=matches[0],oldRecord=projectReference(projectRoot,ADAPTIVE+row.file,row.sha256),old=JSON.parse(verifyProjectReference(projectRoot,oldRecord,declaredHashes));
 need(old.id===plan.oldRunID&&old.scenario===plan.scenario&&old.seed===plan.seed&&old.initialization==='zero'&&old.status==='completed frozen-policy evaluation'&&old.actualMainRounds===2000000,'Original completed learner identity differs');sameJSON(old.control,plan.control,'Original saved controller differs');
 const entries=old.checkpoints.filter(c=>c.step===2000000),indexedEntries=row.checkpoints.filter(c=>c.step===2000000);need(entries.length===1&&indexedEntries.length===1,'Final original checkpoint missing or duplicated');const entry=entries[0];for(const key of ['step','file','sha256'])sameJSON(indexedEntries[0][key],entry[key],'Indexed final checkpoint differs');
 const metadata=projectReference(projectRoot,ADAPTIVE+entry.file,entry.sha256),meta=JSON.parse(verifyProjectReference(projectRoot,metadata,declaredHashes)),finiteGame=projectReference(projectRoot,old.rawFile,old.rawSha256);
 sameJSON(meta.control,plan.control,'Original metadata controller identity differs');need(meta.step===2000000&&meta.T===2000000&&meta.seed===plan.seed&&meta.initialization==='zero'&&meta.alpha===.1&&meta.gamma===19/20,'Original metadata training identity differs');sameJSON(entry.terminal,{phase:meta.phase,previousIndices:meta.previousIndices},'Original metadata terminal header differs');
 need(Number.isInteger(meta.layout?.n)&&meta.layout.n>0&&meta.layout.n<=62&&meta.layout.rows===plan.control.phases*meta.layout.n**2&&meta.layout.rows<=MAX_STATES&&Number.isInteger(meta.layout.cells)&&meta.layout.cells>0&&meta.layout.cells<=meta.layout.rows*meta.layout.n,'Original compact layout header invalid');
 need(meta.phase===(plan.control.id==='startup-only'?1:2000000%4)&&meta.capExecutions===(plan.control.id==='startup-only'?1:500000)&&Array.isArray(meta.previousIndices)&&meta.previousIndices.length===2&&meta.previousIndices.every(i=>Number.isInteger(i)&&i>=0&&i<meta.layout.n),'Original terminal NEXT-clock header invalid');
 for(const kind of ['q','counts','policies'])need(Array.isArray(meta.files?.[kind])&&meta.files[kind].length===2,'Original metadata artifact header missing');
 for(let actor=0;actor<2;actor++)need(meta.files.q[actor].bytes===meta.layout.cells*8&&meta.files.counts[actor].bytes===meta.layout.cells*2&&meta.files.policies[actor].bytes===meta.layout.rows,'Original metadata binary dimensions differ');
 const convert=ref=>({...ref,file:ADAPTIVE+ref.file}),input={inputRoot:'project',oldRunID:plan.oldRunID,checkpointStep:2000000,finiteGame,oldRecord,metadata,q:meta.files.q.map(convert),counts:meta.files.counts.map(convert),savedPolicies:meta.files.policies.map(convert),checkpointEntry:{step:entry.step,file:entry.file,sha256:entry.sha256,terminal:entry.terminal}};
 for(const ref of [finiteGame,...input.q,...input.counts,...input.savedPolicies]){const actual=projectReference(projectRoot,ref.file,ref.sha256);need(actual.bytes===ref.bytes,'Original declared artifact byte count differs');if(declaredHashes)need(declaredHashes[ref.file]===ref.sha256,'Original artifact absent from frozen inputs');}
 return input;
}
export function validateOriginalEndpoint(finite,control,meta){
 const n=finite.prices.length,step=meta.step;need(step===2000000&&meta.T===step,'Only the saved final two-million-round endpoint is allowed');
 const expectedPhase=control.id==='startup-only'?1:step%control.period,expectedCaps=control.id==='startup-only'?1:Math.ceil(step/control.period);need(meta.phase===expectedPhase&&meta.capExecutions===expectedCaps,'Original terminal NEXT phase or cap count differs');
 need(Array.isArray(meta.previousIndices)&&meta.previousIndices.length===2&&meta.previousIndices.every(i=>Number.isInteger(i)&&i>=0&&i<n),'Original terminal price indices invalid');
 const upper=finite.sets.map(s=>s.at(-1));need(upper.every((v,i)=>i===0||v>=upper[i-1]),'Accepted upper-map monotonicity premise differs');let bound=finite.capIndex,steps=control.id==='startup-only'?step-1:(meta.phase+control.period-1)%control.period;
 for(let r=0;r<steps;r++){const next=upper[bound];if(next===bound)break;need(next>=bound,'Cap-start upper orbit differs');bound=next;}
 need(meta.previousIndices.every(i=>i<=bound),'Original actual terminal exceeds clock-specific cap envelope');return{upperBoundIndex:bound,guardStepsSinceCap:steps};
}
export function loadEvidenceCase(plan,{projectRoot=ROOT,input=null,declaredHashes=null}={}){
 input=input??identifyInputs(plan,{projectRoot,declaredHashes});need(input.inputRoot==='project'&&input.oldRunID===plan.oldRunID&&input.checkpointStep===2000000,'Inherited input identity differs');
 const old=JSON.parse(verifyProjectReference(projectRoot,input.oldRecord,declaredHashes)),meta=JSON.parse(verifyProjectReference(projectRoot,input.metadata,declaredHashes)),raw=JSON.parse(verifyProjectReference(projectRoot,input.finiteGame,declaredHashes)),f=raw.finite;
 const finalEntries=old.checkpoints.filter(c=>c.step===2000000);need(finalEntries.length===1,'Original final checkpoint missing or duplicated');for(const key of ['step','file','sha256','terminal'])sameJSON(input.checkpointEntry[key],finalEntries[0][key],'Original final checkpoint identity differs');
 need(raw.scenario?.id===plan.scenario&&old.id===plan.oldRunID&&old.rawFile===input.finiteGame.file&&old.rawSha256===input.finiteGame.sha256&&old.actualMainRounds===2000000&&old.status==='completed frozen-policy evaluation','Original game/run binding differs');sameJSON(meta.control,plan.control,'Original checkpoint clock differs');sameJSON(old.control,plan.control,'Original run controller differs');
 need(meta.seed===plan.seed&&meta.initialization==='zero'&&meta.alpha===.1&&meta.gamma===19/20,'Original binary64 training settings differ');
 need(f.prices.length<=62&&f.prices.every((p,i)=>Number.isFinite(p)&&(i===0||p>f.prices[i-1])),'Original sorted price choices invalid');const L=boundedLayout(f,plan.control),offsetBytes=Buffer.alloc(L.offsets.length*4);L.offsets.forEach((v,i)=>offsetBytes.writeUInt32LE(v,4*i));
 need(meta.layout.n===L.n&&meta.layout.rows===L.rows&&meta.layout.cells===L.cells&&meta.layout.offsetsSha256===hash(offsetBytes),'Original compact layout identity differs');validateOriginalEndpoint(f,plan.control,meta);
 sameJSON(input.checkpointEntry.terminal,{phase:meta.phase,previousIndices:meta.previousIndices},'Original actual terminal history differs');need(input.metadata.file===ADAPTIVE+input.checkpointEntry.file&&input.metadata.sha256===input.checkpointEntry.sha256,'Original selected checkpoint binding differs');
 const q=[],counts=[];for(let actor=0;actor<2;actor++){
  for(const [kind,key]of [['q','q'],['counts','counts'],['savedPolicies','policies']])sameJSON(input[kind][actor],{...meta.files[key][actor],file:ADAPTIVE+meta.files[key][actor].file},'Original '+kind+' artifact reference differs');
  need(input.q[actor].bytes===L.cells*8&&input.counts[actor].bytes===L.cells*2&&input.savedPolicies[actor].bytes===L.rows,'Original compact artifact dimensions differ before allocation');const qb=verifyProjectReference(projectRoot,input.q[actor],declaredHashes),cb=verifyProjectReference(projectRoot,input.counts[actor],declaredHashes);q.push(Float64Array.from({length:L.cells},(_,i)=>qb.readDoubleLE(i*8)));counts.push(Uint16Array.from({length:L.cells},(_,i)=>cb.readUInt16LE(i*2)));
 }
 const greedy=reconstructGreedy(f,plan.control,q,counts,meta.countOverflow,{expectedRounds:2000000});
 for(let actor=0;actor<2;actor++){const saved=verifyProjectReference(projectRoot,input.savedPolicies[actor],declaredHashes);for(let s=0;s<L.rows;s++){const phase=Math.floor(s/(L.n*L.n)),i=Math.floor(s/L.n)%L.n,j=s%L.n,world=actor===0?s:phase*L.n*L.n+j*L.n+i;need(saved[s]===greedy.worldPolicies[actor][world],'Original saved policy differs from complete masked Q argmax');}}
 const start=meta.phase*L.n*L.n+meta.previousIndices[0]*L.n+meta.previousIndices[1],mdp=prepareMDP(raw,plan.control,greedy.worldPolicies,plan.focal,greedy.supportCount);return{mdp,start,input};
}

export const SOURCES=Object.freeze([
 'research/learned-opponent-study.js','research/learned-opponent-case.js','research/run-learned-opponent.py','tests/test_learned_opponent_supervisor.py','tests/learned-opponent-study.test.js',
 'research/LEARNED_OPPONENT_PROTOCOL.md','research/LEARNED_OPPONENT_THEORY.md','research/LEARNED_OPPONENT_ANALYSIS_CONTRACT.md','research/LEARNED_OPPONENT_DERIVATIVE_CONTRACT.md','research/LEARNED_OPPONENT_CONCEPT_REVIEW.md','research/LEARNED_OPPONENT_PROSPECTIVE_REVIEW.md',
 'research/audit-learned-opponent.py','tests/test_learned_opponent_audit.py','tests/test_learned_opponent_cross_audit.py',
 'tests/test_learned_opponent_inventory_audit.py',
 'research/learned-opponent-format.js','research/learned-opponent-analysis.js','tests/learned-opponent-format.test.js','tests/learned-opponent-analysis.test.js'
 ,'research/learned-opponent-evidence.js','research/learned-opponent-web-game.js','tests/learned-opponent-evidence.test.js','tests/learned-opponent-web-game.test.js','tests/helpers/learned-opponent-fixture.js'
 ,'research/build-learned-opponent-web.js','tests/learned-opponent-gate.test.js','tests/helpers/learned-opponent-evidence-fixture.js'
]);
export const DEFAULT_OUTPUT=path.join(ROOT,'research/learned-opponent-results');
export function manifestDependencies(manifest){
 const groups=['sourceHashes','inputHashes','hashes','sources'],merged={};need(groups.some(g=>Object.hasOwn(manifest,g)),'Inherited manifest has no recognized declared identity map');
 for(const group of groups)if(Object.hasOwn(manifest,group)){
  const map=manifest[group];need(map&&typeof map==='object'&&!Array.isArray(map),'Malformed inherited identity map '+group);
  for(const [file,digest]of Object.entries(map)){
   need(file&&!file.includes('\\')&&!file.includes(':')&&!file.startsWith('/')&&file.split('/').every(part=>part&&part!=='.'&&part!=='..'),'Unsafe inherited dependency path');need(typeof digest==='string'&&/^[a-f0-9]{64}$/.test(digest),'Malformed inherited identity digest');need(!merged[file]||merged[file]===digest,'Conflicting inherited identity maps '+file);merged[file]=digest;
  }
 }return merged;
}
export function inventory({projectRoot=ROOT}={}){
 // Administrative identities only: no Q decoding, MDP construction or solving.
 const inputHashes={},visited=new Set(),use=(name,expected=null)=>{const ref=projectReference(projectRoot,name,expected);need(!inputHashes[ref.file]||inputHashes[ref.file]===ref.sha256,'Conflicting inherited identity '+name);inputHashes[ref.file]=ref.sha256;return ref;},json=(name,expected=null)=>{const ref=use(name,expected);return JSON.parse(verifyArtifact(projectRoot,ref));};
 function closure(name,expected=null){const ref=use(name,expected);if(visited.has(name))return;visited.add(name);const m=JSON.parse(verifyArtifact(projectRoot,ref));for(const [file,digest]of Object.entries(manifestDependencies(m))){use(file,digest);if(file.endsWith('/manifest.json'))closure(file,digest);}}
 closure(ADAPTIVE+'manifest.json');const manifestHash=inputHashes[ADAPTIVE+'manifest.json'],audit=json(ADAPTIVE+'independent-audit.json'),index=json(ADAPTIVE+'index.json'),results=json(ADAPTIVE+'results.json'),completion=json(ADAPTIVE+'completion.json');
 need(audit.passed===true&&audit.studyManifestHash===manifestHash&&audit.resultsSha256===inputHashes[ADAPTIVE+'results.json']&&audit.indexSha256===inputHashes[ADAPTIVE+'index.json']&&audit.completionSha256===inputHashes[ADAPTIVE+'completion.json']&&audit.fullTrainingReplay===false,'Closed learner audit binding differs');use('research/audit-adaptive-learning.py',audit.auditorSourceHash);
 need(completion.passed===true&&completion.finalFrozenDependencyCheck?.passed===true&&completion.runs===192&&completion.checkpoints===384&&completion.unresolvedRuns===0&&completion.manifestSha256===manifestHash&&completion.resultsSha256===audit.resultsSha256&&completion.indexSha256===audit.indexSha256,'Closed learner completion differs');need(index.manifestSha256===manifestHash&&results.manifestSha256===manifestHash&&index.records.length===192&&results.records.length===192,'Closed learner result inventory differs');
 const cases=plannedCases(),inputs={};for(const plan of cases){if(inputs[plan.oldRunID])continue;const input=identifyInputs(plan,{projectRoot,index}),old=json(input.oldRecord.file,input.oldRecord.sha256),same=results.records.filter(r=>r.id===plan.oldRunID);need(same.length===1&&JSON.stringify(same[0])===JSON.stringify(old),'Closed learner result and indexed record differ');for(const ref of [input.finiteGame,input.oldRecord,input.metadata,...input.q,...input.counts,...input.savedPolicies])use(ref.file,ref.sha256);inputs[plan.oldRunID]=input;}
 const receiptFile='output/mixed-timing-package-verification.json',delivery=json(receiptFile,V10_RECEIPT_SHA256);need(delivery.archive==='output/price-guard-mixed-timing-v10.zip'&&delivery.verification?.passed===true&&delivery.verification.payloadHashesAndCRC===true&&delivery.sha256===V10_ARCHIVE_SHA256&&delivery.bytes===123232702,'Closed V10 full delivery receipt failed');
 const benchmark=json('.local/learned-process-benchmark-final-v2.json');need(benchmark.scope.startsWith('Artificial engineering benchmark')&&benchmark.states===MAX_STATES&&benchmark.edges===MAX_STATES*62&&benchmark.executionSucceeded===true&&benchmark.finalSourceCheck?.passed===true,'Final prospective artificial process benchmark missing');
 need(Array.isArray(benchmark.artifacts)&&benchmark.artifacts.length>=8&&benchmark.tests?.some(t=>t.label==='kernel'&&t.passed===true&&t.tests===17)&&benchmark.tests?.some(t=>t.label==='process'&&t.passed===true&&t.tests===11),'Final benchmark task/artifact/test receipts missing');
 for(const required of ['research/learned-opponent-study.js','research/learned-opponent-case.js','research/run-learned-opponent.py','research/learned-opponent-evidence.js'])need(benchmark.sourceHashes?.[required],'Final benchmark source identity missing '+required);
 for(const [file,digest]of Object.entries(benchmark.sourceHashes))use(file,digest);for(const artifact of benchmark.artifacts??[]){const ref=use(artifact.file,artifact.sha256);need(ref.bytes===artifact.bytes,'Final benchmark artifact byte count differs');}
 const archive=contained(projectRoot,delivery.archive),present=fs.existsSync(archive);if(present)need(fileDigest(archive)===delivery.sha256&&fs.statSync(archive).size===delivery.bytes,'Closed V10 full archive differs');
 return{inputHashes,inputs,cases,v10Delivery:{receipt:receiptFile,receiptSha256:inputHashes[receiptFile],archive:delivery.archive,archiveSha256:delivery.sha256,archiveBytes:delivery.bytes,archivePresentAtVerification:present},scope:'Administrative source/schema/hash identity check only; no inherited Q values decoded or new MDP queries'};
}
function saveJSON(directory,file,value){return writeArtifact(directory,file,jsonBytes(value));}
export function freeze(directory=DEFAULT_OUTPUT,{projectRoot=ROOT}={}){
 directory=path.resolve(directory);need(!fs.existsSync(directory)||fs.readdirSync(directory).length===0,'Evidence directory nonempty; refusing overwrite');const inherited=inventory({projectRoot}),sourceHashes=Object.fromEntries(SOURCES.map(name=>[name,projectReference(projectRoot,name).sha256]));
 const manifest={schemaVersion:1,frozenAt:new Date().toISOString(),sourceHashes,inputHashes:inherited.inputHashes,v10Delivery:inherited.v10Delivery,inputs:inherited.inputs,plan:{cases:inherited.cases,retainedRecords:48,discount:{numerator:19,denominator:20},maximumSweeps:600,floatStoppingThreshold:1e-10,requestedAbsoluteGap:pack(GAP_TARGET),dyadicDenominatorPower:32,hardCaseSeconds:300,maximumStates:MAX_STATES,maximumScalarBits:MAX_BITS,maximumCandidateNumeratorBits:MAX_CANDIDATE_BITS,softResourceTargets:{seconds:7200,sampledProcessRSSBytes:512000000,newOutputBytes:250000000},fullTrainingReplay:false,optimizerIterationsReplayed:false,scope:'Exact finite saved-opponent MDP audit from actual terminal history/NEXT phase; deterministic saved expected own profits; no training, fresh cap, messages or experimental model API calls'}};
 for(const name of SOURCES){const full=contained(directory,'sources/'+name);fs.mkdirSync(path.dirname(full),{recursive:true});fs.copyFileSync(contained(projectRoot,name),full,fs.constants.COPYFILE_EXCL);}const ref=saveJSON(directory,'manifest.json',manifest);return{frozenAt:manifest.frozenAt,manifestSha256:ref.sha256,sourceFiles:SOURCES.length,inputFiles:Object.keys(inherited.inputHashes).length,retainedRecords:48};
}
export function verify(directory=DEFAULT_OUTPUT,{projectRoot=ROOT,verifyDelivery=true}={}){
 directory=path.resolve(directory);const manifest=readJSON(directory,'manifest.json');for(const group of ['sourceHashes','inputHashes'])for(const [file,digest]of Object.entries(manifest[group])){need(projectReference(projectRoot,file,digest).sha256===digest,'Frozen dependency changed '+file);if(group==='sourceHashes')need(fileDigest(contained(directory,'sources/'+file))===digest,'Frozen source snapshot differs '+file);}
 sameJSON(manifest.plan.cases,plannedCases(),'Frozen 48-case plan differs');need(manifest.plan.retainedRecords===48&&manifest.plan.maximumSweeps===600&&manifest.plan.hardCaseSeconds===300,'Frozen numerical settings differ');
 if(verifyDelivery){const delivery=readJSON(projectRoot,manifest.v10Delivery.receipt);need(fileDigest(contained(projectRoot,manifest.v10Delivery.receipt))===manifest.v10Delivery.receiptSha256&&delivery.sha256===manifest.v10Delivery.archiveSha256,'V10 receipt identity differs');const archive=contained(projectRoot,manifest.v10Delivery.archive);if(fs.existsSync(archive))need(fileDigest(archive)===manifest.v10Delivery.archiveSha256&&fs.statSync(archive).size===manifest.v10Delivery.archiveBytes,'V10 archive differs');}return manifest;
}
export function assertFreshRun(directory){for(const name of ['execution-start.json','journal.jsonl','records','artifacts','tasks','results.json','index.json','completion.json'])need(!fs.existsSync(path.join(directory,name)),'Partial/closed learned-opponent evidence preserved; refusing rerun: '+name);}
function outputBytes(directory){let sum=0;for(const e of fs.readdirSync(directory,{withFileTypes:true})){const full=path.join(directory,e.name);sum+=e.isDirectory()?outputBytes(full):fs.statSync(full).size;}return sum;}
export function run(){throw Error('Use python -B research/run-learned-opponent.py; hard deadlines require an isolated Node process per case');}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const mode=process.argv[2],directory=process.argv[3]?path.resolve(process.argv[3]):DEFAULT_OUTPUT;
 if(mode==='preflight')console.log(JSON.stringify(inventory()));else if(mode==='freeze')console.log(JSON.stringify(freeze(directory)));else if(mode==='verify')console.log(JSON.stringify({passed:!!verify(directory)}));else if(mode==='run')console.log(JSON.stringify(await run(directory)));else throw Error('Use preflight, freeze, verify or run; importing this source performs no IO');
}
