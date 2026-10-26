// Independent economic/mask enumeration. New primary builder/certifier is not imported.
// The browser core is exercised as an object under test; Python Fraction audits
// every stored cycle and finite-prefix certificate separately.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createGame} from './recurring-game.js';

const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const periods=[1,2,4,8,16,32,64,128];
let checks=0;
function insist(ok,label){checks++;if(!ok)throw Error(label);}
function same(a,b,label){insist(JSON.stringify(a)===JSON.stringify(b),label);}
export function independentSavedOutcome(a,b,e){
 const za=(e.quality-a-e.outsideQuality)/e.mu,zb=(e.quality-b-e.outsideQuality)/e.mu;
 const offset=Math.max(0,za,zb),ea=Math.exp(za-offset),eb=Math.exp(zb-offset),den=Math.exp(-offset)+ea+eb;
 const qa=e.buyers*ea/den,qb=e.buyers*eb/den;
 return {consumerSurplus:e.buyers*e.mu*(offset+Math.log(den)),profitA:qa*(a-e.cost),profitB:qb*(b-e.cost),quantityA:qa,quantityB:qb};
}

export function checkDisplayRecord(record,{mesh,guard,cap,old},{exercise=true}={}){
 const sid=guard.scenario.id,e=guard.scenario.economy,epsilon=guard.scenario.epsilon;
 same(record.scenario,guard.scenario,'Saved display economy');same(old.scenario,guard.scenario,'Old target economy');same(cap.scenario,guard.scenario,'Old cap economy');
 insist(cap.controller==='cap'&&guard.controller==='guard'&&mesh.scenario===sid&&mesh.n===61,'Inherited games and fixed display size');
 same(cap.game.prices,guard.game.prices,'Same old cap grid');same(mesh.economy,e,'Source mesh economy');
 const support=cap.game.sets[0],oldIndex=support.at(-1),physical=guard.game.prices[oldIndex];
 same(support,Array.from({length:oldIndex+1},(_,i)=>i),'Old prefix cap');insist(cap.game.sets.every(s=>JSON.stringify(s)===JSON.stringify(support)),'Every old state has same cap prefix');
 insist(old.results.length===5&&old.results.every(r=>r.existingCompetitiveCap.index===oldIndex&&r.existingCompetitiveCap.price===physical),'Old initializer cap identity');
 const removed=mesh.prices.filter(p=>Math.abs(p-physical)<=1e-12);insist(removed.length<=1,'At most one near-cap quote');
 const prices=[...mesh.prices.filter(p=>Math.abs(p-physical)>1e-12),physical].sort((a,b)=>a-b),n=prices.length,capIndex=prices.indexOf(physical);
 insist([61,62].includes(n)&&prices.every((p,i)=>Number.isFinite(p)&&(!i||p>prices[i-1])),'Declared nonuniform finite game');
 same(record.finite.prices,prices,'Exact independent cap-priority merge');
 same(record.cap.removedBaseQuotes,removed.map(price=>({price,absoluteDistance:Math.abs(price-physical)})),'Every removed near-cap quote/distance');
 insist(record.cap.price===physical&&record.cap.index===capIndex&&record.cap.originalIndex===oldIndex&&record.cap.priorityTolerance===1e-12,'Preserved physical cap metadata');
 const game=record.finite;
 insist(game.capIndex===capIndex&&game.epsilon===epsilon&&game.comparisonAllowance===epsilon+1e-12,'Saved cap/mask constants');
 same(record.originalTargets,old.results.map(r=>({label:r.label,requestedTarget:r.requestedTarget,numericalMargin:r.numericalMargin,actualGuaranteedThreshold:r.actualGuaranteedThreshold})),'All fixed old targets');
 const table={consumerSurplus:[],profitA:[],profitB:[],quantityA:[],quantityB:[]};
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){
  const r=independentSavedOutcome(prices[i],prices[j],e);
  for(const key of Object.keys(table))table[key].push(r[key]);
 }
 for(const key of Object.keys(table))same(game.rewards[key],table[key],'Every independently rebuilt '+key+' value');
 let monotonicity=0;
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){
  const reward=table.consumerSurplus[i*n+j];
  if(i){insist(reward<=table.consumerSurplus[(i-1)*n+j],'Every A-coordinate saved reward order');monotonicity++;}
  if(j){insist(reward<=table.consumerSurplus[i*n+j-1],'Every B-coordinate saved reward order');monotonicity++;}
 }
 const sets=[],bestProfits=[];let nearBoundaries=0;
 for(let rival=0;rival<n;rival++){
  const a=prices.map((_,own)=>table.profitA[own*n+rival]),b=prices.map((_,own)=>table.profitB[rival*n+own]),bestA=Math.max(...a),bestB=Math.max(...b);
  const as=a.flatMap((p,i)=>bestA-p<=epsilon+1e-12?[i]:[]),bs=b.flatMap((p,i)=>bestB-p<=epsilon+1e-12?[i]:[]);
  insist(as.length>0,'Independently nonempty support');same(as,bs,'Both shops have identical numerical eligibility masks');sets.push(as);bestProfits.push(bestA);
  for(const p of a)if(Math.abs((epsilon+1e-12)-(bestA-p))<=64*Number.EPSILON*Math.max(1,Math.abs(bestA),Math.abs(p)))nearBoundaries++;
 }
 const upper=sets.map(s=>s.at(-1));same(game.sets,sets,'Entire independent binary64 mask');same(game.upper,upper,'Every maximum allowed quote');same(game.rowBestProfits,bestProfits,'Entire full-row best profit table');
 insist(upper.every((u,j)=>!j||u>=upper[j-1]),'All-state upper map monotonicity');
 insist(game.tableCoordinateMonotone&&game.upperMapMonotone&&game.tableMonotonicityChecks===monotonicity,'Reported monotonicity checks');
 insist(game.capOrbitNondecreasing===(upper[capIndex]>=capIndex),'Checked finite upward-orbit flag');
 same(game.certificates.map(c=>c.period),periods,'All finite prospective periods');
 for(const certificate of game.certificates){let at=capIndex;const expected=[];for(let j=0;j<certificate.period;j++){expected.push(at);at=upper[at];}same(certificate.cycleIndices,expected,'Independent cap-first orbit indices');insist(certificate.capFirst===true,'Actual first cap certificate');}
 let executions=0,oldStates=0,capOutcomes=0;
 if(exercise){
  const capActions=Array.from({length:capIndex+1},(_,i)=>i);
  // Every prior public pair: the first rule is a cap, with no old reward.
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){
   const player=createGame(record,2,{previous:[i,j]}),state=player.snapshot();oldStates++;
   same(player.allowed(0),capActions,'First cap overrides A guard for every old pair');same(player.allowed(1),capActions,'First cap overrides B guard for every old pair');
   insist(state.executions===0&&state.latest===null&&state.averages===null&&state.protectedBuffer.value===0,'Old memory earns no reward');
  }
  // All actual cap outcomes establish the correct asymmetric lagged rival state.
  for(const a of capActions)for(const b of capActions){
   const player=createGame(record,2),first=player.execute(a,b);executions++;capOutcomes++;
   insist(first.latest.type==='cap'&&first.latest.consumerSurplus===table.consumerSurplus[a*n+b]&&first.capExecutions===1,'Actual first cap reward/timing');
   same(player.allowed(0),sets[b],'A guard observes previous B quote');same(player.allowed(1),sets[a],'B guard observes previous A quote');
   const x=upper[b],y=upper[a],second=player.execute(x,y);executions++;
   insist(second.latest.type==='guard'&&second.latest.consumerSurplus===table.consumerSurplus[x*n+y]&&second.phase===0&&second.nextIsCap,'Guard reward followed by next cap');
   const undo=player.undo();same(undo.previousIndices,[a,b],'Undo restores asymmetric history');insist(undo.executions===1,'Undo removes actual reward');
   const reset=player.reset();insist(reset.executions===0&&reset.averages===null,'Reset removes accumulated reward');
  }
  for(const K of periods){
   const player=createGame(record,K);let previous=[n-1,n-1];
   for(let t=0;t<2*K+3;t++){
    const phase=t%K,allowed=phase===0?[capActions,capActions]:[sets[previous[1]],sets[previous[0]]];
    same(player.allowed(0),allowed[0],'Phase-correct A support');same(player.allowed(1),allowed[1],'Phase-correct B support');
    const a=allowed[0].at(-1),b=allowed[1].at(-1),state=player.execute(a,b);executions++;
    insist(state.latest.type===(phase===0?'cap':'guard')&&state.phase===(t+1)%K,'Every actual phase transition');
    insist(state.capExecutions===Math.ceil((t+1)/K)&&state.latest.consumerSurplus===table.consumerSurplus[a*n+b],'Cap rule counts and executed reward');
    insist(state.protectedBuffer.nonnegative,'Exact cumulative buffer stays above outward display floor');previous=[a,b];
   }
  }
 }
 return {scenario:sid,quotes:n,payoffPairs:n*n,tableCoordinateChecks:monotonicity,oldPublicPairsChecked:oldStates,capOutcomesChecked:capOutcomes,executionsChecked:executions,nearFloatingBoundaries:nearBoundaries};
}

export function auditSparseDisplay(directory='research/sparse-display-results'){
 checks=0;const manifest=read(path.join(directory,'manifest.json')),index=read(path.join(directory,'index.json')),completion=read(path.join(directory,'completion.json'));
 for(const [file,sha]of Object.entries({...manifest.sourceHashes,...manifest.inputHashes}))insist(hash(file)===sha,'Frozen display source/input '+file);
 same(index.manifestSha256,hash(path.join(directory,'manifest.json')),'Display index/manifest identity');
 insist(manifest.plan.cases===8&&index.cases.length===8&&new Set(index.cases.map(c=>c.scenario)).size===8,'Eight distinct finite scenarios');same(manifest.plan.periods,periods,'Frozen periods');
 const old=read('research/handover-init-results/results.json').records,details=[];let fixture;
 for(const source of manifest.plan.scenarios){
  const row=index.cases.find(r=>r.scenario===source.id);insist(row?.status==='completed','Retained successful display case');const file=path.join(directory,row.file);same(hash(file),row.sha256,'Display case/index hash');
  const record=read(file),inputs={mesh:read(source.mesh),guard:read(source.guard),cap:read(source.cap),old:old.find(r=>r.scenario.id===source.id)};
  details.push(checkDisplayRecord(record,inputs));if(!fixture)fixture={record,inputs};
  insist(row.quotes===record.finite.prices.length&&row.periods===8,'Index dimensions');
 }
 const journal=fs.readFileSync(path.join(directory,'journal.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
 for(const source of manifest.plan.scenarios)same(journal.filter(r=>r.scenario===source.id).map(r=>r.status),['started','completed'],'Per-case execution journal');
 insist(completion.passed&&completion.cases===8&&completion.failures===0&&completion.finalHashCheck&&completion.apiCalls===0&&completion.newTrainingRounds===0,'Finite completion/no-model inventory');
 const mutations={capIdentity:r=>r.cap.price+=.01,guardMask:r=>r.finite.sets[0]=[],rewardTable:r=>r.finite.rewards.consumerSurplus[0]+=1,phaseOrbit:r=>r.finite.certificates[1].cycleIndices[0]=(r.finite.capIndex+1)%r.finite.prices.length};
 const controls={};for(const [name,mutate]of Object.entries(mutations)){const changed=structuredClone(fixture.record);mutate(changed);let rejected=false;try{checkDisplayRecord(changed,fixture.inputs,{exercise:false});}catch{rejected=true;}insist(rejected,'Rejected display '+name+' corruption');controls[name]=rejected;}
 return {passed:true,completedAt:new Date().toISOString(),studyManifestHash:hash(path.join(directory,'manifest.json')),indexSha256:hash(path.join(directory,'index.json')),auditorSourceHash:hash(fileURLToPath(import.meta.url)),checks,cases:8,payoffPairs:details.reduce((s,r)=>s+r.payoffPairs,0),executionsChecked:details.reduce((s,r)=>s+r.executionsChecked,0),corruptionNegativeControls:controls,details,scope:'Independent full numerical payoff and both-shop eligibility enumeration, all reward-coordinate inequalities, cap identity, every old pair/cap outcome and actual core phases. Shared JavaScript Math binary64 arithmetic; separate Python Fraction certificate required for exact stored-weight cycle/prefix claims.'};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2),output=args.indexOf('--output'),directory=args.find((a,i)=>!a.startsWith('--')&&(i===0||args[i-1]!=='--output'))||'research/sparse-display-results',result=auditSparseDisplay(directory);
 if(output>=0)fs.writeFileSync(args[output+1],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}
