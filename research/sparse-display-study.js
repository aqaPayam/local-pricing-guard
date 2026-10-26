// Prospective finite numerical game for the recurring-cap human demonstration.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
import {outcome} from './robust-market.js';import {certifyCycle} from './recurring-game.js';
export const PERIODS=Object.freeze([1,2,4,8,16,32,64,128]);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),DIR='research/sparse-display-results';
const IDS=['base-g15-t1','scale0.5-g15-t1','lower-quality-g15-t1','lowcost-g15-t1','base-g11-t1','base-g31-t1','base-g15-t0.5','base-g15-t2'];
const SOURCES=['research/sparse-display-study.js','research/recurring-game.js','research/robust-market.js','research/SPARSE_RESET_PROTOCOL.md','research/SPARSE_RESET_THEORY.md','tests/recurring-game.test.js','tests/sparse-display-study.test.js'];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(ROOT,p))).digest('hex'),read=p=>JSON.parse(fs.readFileSync(path.resolve(ROOT,p),'utf8'));
const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v)+'\n',{flag:'wx'});
function same(a,b){return JSON.stringify(a)===JSON.stringify(b);}
export function mergeCap(prices,pCap){
 if(!Number.isFinite(pCap)||pCap<prices[0]||pCap>prices.at(-1)||!prices.every((p,i)=>Number.isFinite(p)&&(!i||p>prices[i-1])))throw Error('Invalid finite interval/cap');
 const removed=prices.filter(p=>Math.abs(p-pCap)<=1e-12);if(removed.length>1)throw Error('Multiple near-cap base quotes');
 const merged=[...new Set([...prices.filter(p=>Math.abs(p-pCap)>1e-12),pCap])].sort((a,b)=>a-b);
 return {prices:merged,removedBaseQuotes:removed.map(price=>({price,absoluteDistance:Math.abs(price-pCap)})),capIndex:merged.indexOf(pCap),priorityTolerance:1e-12};
}
export function buildFiniteDisplay({mesh,guard,cap,old}){
 const id=old.scenario.id,economy=guard.scenario.economy,epsilon=guard.scenario.epsilon;
 if(mesh.scenario!==id||mesh.n!==61||mesh.prices?.length!==61||guard.id!==id+'-guard'||cap.id!==id+'-cap'||guard.controller!=='guard'||cap.controller!=='cap'||!same(cap.scenario,guard.scenario)||!same(old.scenario,guard.scenario)||!same(mesh.economy,economy)||!same(cap.game?.prices,guard.game?.prices)||!same(mesh.declaredEndpointPrices,[guard.game.prices[0],guard.game.prices.at(-1)]))throw Error('Inherited finite-game identity mismatch');
 const originalCapIndex=Math.max(...cap.game.sets[0]);
 if(!cap.game.sets.every(s=>same(s,Array.from({length:originalCapIndex+1},(_,i)=>i))))throw Error('Inherited cap is not a common prefix');
 const pCap=cap.game.prices[originalCapIndex];
 if(old.results.length!==5||new Set(old.results.map(r=>r.label)).size!==5||!old.results.every(r=>['requestedTarget','numericalMargin','actualGuaranteedThreshold'].every(k=>Number.isFinite(r[k]))&&r.existingCompetitiveCap.index===originalCapIndex&&r.existingCompetitiveCap.price===pCap))throw Error('Initializer physical cap mismatch');
 const merged=mergeCap(mesh.prices,pCap),prices=merged.prices,n=prices.length,rewards={consumerSurplus:[],profitA:[],profitB:[],quantityA:[],quantityB:[]};
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){const r=outcome([prices[i],prices[j]],economy);rewards.consumerSurplus.push(r.consumerSurplus);rewards.profitA.push(r.profits[0]);rewards.profitB.push(r.profits[1]);rewards.quantityA.push(r.quantities[0]);rewards.quantityB.push(r.quantities[1]);}
 let monotoneChecks=0;
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){const c=rewards.consumerSurplus[i*n+j];if(i){monotoneChecks++;if(c>rewards.consumerSurplus[(i-1)*n+j])throw Error('Saved surplus table increases in Shop A price');}if(j){monotoneChecks++;if(c>rewards.consumerSurplus[i*n+j-1])throw Error('Saved surplus table increases in Shop B price');}}
 const sets=[],rowBestProfits=[];
 for(let j=0;j<n;j++){const row=prices.map((_,i)=>rewards.profitA[i*n+j]),best=Math.max(...row),allowed=row.flatMap((p,i)=>best-p<=epsilon+1e-12?[i]:[]);if(!allowed.length)throw Error('Empty saved guard set');sets.push(allowed);rowBestProfits.push(best);}
 const upper=sets.map(s=>s.at(-1));if(!upper.every((u,j)=>!j||u>=upper[j-1]))throw Error('Nonmonotone display upper map');
 const finite={prices,sets,upper,capIndex:merged.capIndex,rewards,epsilon,comparisonAllowance:epsilon+1e-12,tableMonotonicityChecks:monotoneChecks,tableCoordinateMonotone:true,upperMapMonotone:true,capOrbitNondecreasing:upper[merged.capIndex]>=merged.capIndex,rowBestProfits};
 finite.certificates=PERIODS.map(K=>certifyCycle(finite,K));
 return {scenario:old.scenario,originalTargets:old.results.map(r=>({label:r.label,requestedTarget:r.requestedTarget,numericalMargin:r.numericalMargin,actualGuaranteedThreshold:r.actualGuaranteedThreshold})),cap:{price:pCap,index:merged.capIndex,originalIndex:originalCapIndex,source:'Original inherited competitive-cap case, checked against all five initializer labels',priorityTolerance:merged.priorityTolerance,removedBaseQuotes:merged.removedBaseQuotes},finite,scope:'Saved numerical finite game on the 61-price base mesh with exact inherited cap priority; expected demand is a model quantity, not human data'};
}
function inventory(){
 const hm=read('research/handover-init-results/manifest.json');for(const [p,h] of Object.entries({...hm.sourceHashes,...hm.inputHashes}))if(hash(p)!==h)throw Error('Changed inherited frozen source/input '+p);
 const ha=read('research/handover-init-results/independent-audit.json');if(!ha.passed||ha.studyManifestHash!==hash('research/handover-init-results/manifest.json')||ha.auditorSourceHash!==hash('research/audit-handover-init.js'))throw Error('Initializer audit link mismatch');
 const mm=read('research/mesh-results/manifest.json');for(const [p,h] of Object.entries({...mm.sourceHashes,...mm.inputHashes}))if(hash(p)!==h)throw Error('Changed inherited mesh dependency '+p);
 const ma=read('research/mesh-results/independent-audit.json'),mi=read('research/mesh-results/index.json');if(!ma.passed||ma.indexSha256!==hash('research/mesh-results/index.json')||ma.studyManifestHash!==hash('research/mesh-results/manifest.json')||ma.auditorSourceHash!==hash('research/audit-mesh-refinement.js'))throw Error('Mesh audit link mismatch');
 const files=['research/handover-init-results/manifest.json','research/handover-init-results/results.json','research/handover-init-results/independent-audit.json','research/audit-handover-init.js','research/mesh-results/manifest.json','research/mesh-results/index.json','research/mesh-results/independent-audit.json','research/audit-mesh-refinement.js'];
 const scenarios=IDS.map(id=>{const entry=mi.cases.find(c=>c.scenario===id&&c.n===61);if(!entry||hash('research/mesh-results/'+entry.file)!==entry.sha256)throw Error('Missing/changed audited61-price source');const mesh='research/mesh-results/'+entry.file,guard='research/cycle-results/cases/'+id+'-guard.json',cap='research/cycle-results/cases/'+id+'-cap.json';files.push(mesh,guard,cap);return{id,mesh,guard,cap};});
 return {scenarios,inputHashes:{...hm.sourceHashes,...hm.inputHashes,...mm.sourceHashes,...mm.inputHashes,...Object.fromEntries(files.map(p=>[p,hash(p)]))}};
}
export function freezeDisplay(directory=DIR){const dir=path.resolve(ROOT,directory);fs.mkdirSync(dir,{recursive:true});if(fs.readdirSync(dir).length)throw Error('Existing display evidence preserved');const inputs=inventory(),manifest={frozenAt:new Date().toISOString(),plan:{scenarios:inputs.scenarios,periods:PERIODS,cases:8,capPriorityTolerance:1e-12,finiteWeights:'Exact rational values of saved binary64 consumer-surplus rewards; masks use recorded JavaScript arithmetic',apiCalls:0,trainingRounds:0},sourceHashes:Object.fromEntries(SOURCES.map(p=>[p,hash(p)])),inputHashes:inputs.inputHashes};save(path.join(dir,'manifest.json'),manifest);return{frozenAt:manifest.frozenAt,manifestSha256:hash(path.relative(ROOT,path.join(dir,'manifest.json')))};}
function verify(manifest){for(const [p,h] of Object.entries({...manifest.sourceHashes,...manifest.inputHashes}))if(hash(p)!==h)throw Error('Frozen dependency changed '+p);}
export function runDisplay(directory=DIR){
 const dir=path.resolve(ROOT,directory),manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));verify(manifest);
 if(['index.json','journal.jsonl','completion.json'].some(p=>fs.existsSync(path.join(dir,p))))throw Error('Partial or complete display evidence preserved');
 fs.mkdirSync(path.join(dir,'cases'),{recursive:true});const journal=x=>fs.appendFileSync(path.join(dir,'journal.jsonl'),JSON.stringify({at:new Date().toISOString(),...x})+'\n');
 const old=read('research/handover-init-results/results.json').records,started=performance.now(),cases=[];let rss=process.memoryUsage().rss;
 for(const entry of manifest.plan.scenarios){
  journal({scenario:entry.id,status:'started'});
  try{const record=old.find(r=>r.scenario.id===entry.id);if(!record)throw Error('Missing audited old targets');const result=buildFiniteDisplay({mesh:read(entry.mesh),guard:read(entry.guard),cap:read(entry.cap),old:record}),file='cases/'+entry.id+'.json';save(path.join(dir,file),result);cases.push({scenario:entry.id,file,sha256:hash(path.relative(ROOT,path.join(dir,file))),status:'completed',quotes:result.finite.prices.length,periods:result.finite.certificates.length});journal({scenario:entry.id,status:'completed',file});}
  catch(error){const failure={scenario:entry.id,status:'failed',error:String(error.message)};save(path.join(dir,'cases',entry.id+'-failure.json'),failure);cases.push(failure);journal(failure);}rss=Math.max(rss,process.memoryUsage().rss);
 }
 save(path.join(dir,'index.json'),{manifestSha256:hash(path.relative(ROOT,path.join(dir,'manifest.json'))),cases});let finalHashCheck=true,hashError=null;try{verify(manifest);}catch(e){finalHashCheck=false;hashError=String(e.message);}
 const done={cases:cases.length,failures:cases.filter(c=>c.status!=='completed').length,finalHashCheck,hashError,seconds:(performance.now()-started)/1000,largestObservedRSSBytes:rss,sampling:'After each case, not continuously measured peak',apiCalls:0,newTrainingRounds:0};done.passed=done.cases===8&&!done.failures&&finalHashCheck;save(path.join(dir,'completion.json'),done);journal({status:'completed',passed:done.passed});return done;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const [mode,directory]=process.argv.slice(2);if(!['freeze','run'].includes(mode))throw Error('Explicit freeze or run required');console.log(JSON.stringify(mode==='freeze'?freezeDisplay(directory):runDisplay(directory)));}
