// Prospective descriptive adapter. Importing performs no IO or response solving.
import {summarizeRecords,scientificDisplay,sign,GAP_TARGET} from './learned-opponent-format.js';
import {evidenceReader,localIO as projectIO,sha256} from './learned-opponent-evidence.js';
import {isDeepStrictEqual} from 'node:util';
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
const need=(ok,message)=>{if(!ok)throw Error(message);};
const PREFIX='research/learned-opponent-results',ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const same=(a,b,message)=>need(isDeepStrictEqual(a,b),message);
export const jsonBytes=value=>Buffer.from(JSON.stringify(value)+'\n');
export const orderedSeeds=Object.freeze(Array.from({length:12},(_,i)=>907001+i));
export const controllerOrder=Object.freeze(['startup-only','selected95']);
export const focalOrder=Object.freeze(['A','B']);
export const defaultSelection=Object.freeze({seed:907001,controller:'startup-only',focal:'A',chosenBeforeOutcomeInspection:true,
 scope:'Presentation choice before new strategic outcomes, not a scientific factor or whole-project preregistration; retain even if zero, negative or unavailable.'});

function optionalDisplay(value){
 if(value===null||value===undefined)return null;
 try{return {...scientificDisplay(value),status:'available'};}
 catch(error){return {status:'unavailable',reason:'Optional bounded decimal display: '+error.message,exactSign:sign(value)};}
}
export function presentRecord(record){
 const reason=record.scientificAvailable?null:record.failure?.message??record.scientificUnavailableReason??record.unavailableReason??'Scientific response/certificate unavailable; retained primary status '+record.status;
 const display=record.scientificAvailable?{
  baselineValue:optionalDisplay(record.baseline.value),responseValue:optionalDisplay(record.response.value),
  rawGain:optionalDisplay(record.performance.rawGain),rawGainSign:record.performance.rawGainSign,
  bestImprovement:{lower:optionalDisplay(record.performance.possibleGain.lower),upper:optionalDisplay(record.performance.possibleGain.upper)},
  upperValue:optionalDisplay(record.certificate.upperValue),responseOptimalityGap:optionalDisplay(record.certificate.responseOptimalityGap),
  relativeGain:optionalDisplay(record.performance.relativeGain),relativeGainReason:record.performance.relativeGainReason,
  cycleCustomerBenefit:{baseline:optionalDisplay(record.baseline.eventualCycleCustomerBenefit),response:optionalDisplay(record.response.eventualCycleCustomerBenefit),difference:optionalDisplay(record.performance.cycleCustomerBenefitDifference)},
  unavailableReason:null
 }:{baselineValue:null,responseValue:null,rawGain:null,rawGainSign:null,bestImprovement:null,upperValue:null,responseOptimalityGap:null,relativeGain:null,relativeGainReason:reason,cycleCustomerBenefit:null,unavailableReason:reason};
 // Scientific source objects remain intact; displays never replace exact values.
 return {...record,display};
}

export function deriveSummary(records,meta){
 need(meta?.independentAuditPassed===true,'Complete independent acceptance is required before descriptive derivation');
 const groups=summarizeRecords(records);
 for(const record of records){
  need(record.scenario==='base-g15-t1'&&record.initialization==='zero'&&record.checkpointStep===2000000,'Fixed scenario/initialization/checkpoint differs');
  need(record.control.id==='startup-only'?record.control.period===null:record.control.period===4,'Original startup/K4 controller identity differs');
 }
 return {schemaVersion:1,meta:{...meta,defaultSelection,optimizerIterationsReplayed:false,fullTrainingReplay:false,inheritedEconomicReenumeration:false,
  statisticalScope:'48 dependent seller/controller counterfactuals from 12 whole-market seeds in one targeted stratum. Descriptive exact counts/medians/seed means and paired differences; no confidence intervals, p-values or market-population inference.',
  controllerComparisonScope:'Separately trained policy pairs differ in clocks, legal experiences and phase capacities. Paired seed comparison is not a clock-only causal intervention, cap-frequency causal effect or unrestricted capability control.',
  informationScope:'White-box response audit: the optimizer knows the complete frozen partner lookup, legal masks and saved rewards. This is not a competitor learning a response from limited observations.',
  valueScope:'Mathematical discount19/20 and saved numerical rewards; raw achieved response, baseline fallback, possible best bound and remaining optimizer gap remain distinct.',
  welfareScope:'Secondary eventual-cycle customer-benefit mean, excluding transient; not discounted welfare, a finite-prefix guarantee or a learning effect.'},
  orderedSeeds:[...orderedSeeds],controllerOrder:[...controllerOrder],focalOrder:[...focalOrder],records:records.map(presentRecord),...groups};
}

export const plannedCases=()=>orderedSeeds.flatMap(seed=>controllerOrder.flatMap(id=>focalOrder.map(focal=>{
 const oldRunID=`base-g15-t1--${id}--zero--s${seed}`;return {id:oldRunID+'--focal'+focal,oldRunID,scenario:'base-g15-t1',seed,initialization:'zero',control:{id,period:id==='startup-only'?null:4,phases:id==='startup-only'?2:4},focal,checkpointStep:2000000};
})));
export function analyzeEvidence(io){
 const e=evidenceReader(io),file=name=>PREFIX+'/'+name,A=file('independent-audit.json');
 // Failed/missing complete acceptance blocks later checkpoint or Q reads.
 const audit=e.json(A);need(audit.passed===true&&audit.allPlannedLabelsRetained===true&&audit.labels===48,'Complete independent learned-opponent acceptance missing');
 need(audit.arithmeticBackendHash===null&&audit.optimizerIterationsReplayed===false&&audit.fullTrainingReplay===false&&audit.inheritedEconomicReenumeration===false,'Independent arithmetic/replay/reuse scope differs');
 const M=file('manifest.json'),R=file('results.json'),I=file('index.json'),C=file('completion.json'),J=file('journal.jsonl'),S=file('execution-start.json');
 for(const [field,name]of [['studyManifestHash',M],['resultsSha256',R],['indexSha256',I],['completionSha256',C],['journalSha256',J],['runStartSha256',S],['auditorSourceHash','research/audit-learned-opponent.py']])e.bind(name,audit[field]);
 const manifest=e.json(M),result=e.json(R),index=e.json(I),completion=e.json(C),start=e.json(S),plans=plannedCases();
 need(manifest.schemaVersion===1&&manifest.plan?.retainedRecords===48&&manifest.plan.maximumSweeps===600&&manifest.plan.floatStoppingThreshold===1e-10&&manifest.plan.hardCaseSeconds===300&&manifest.plan.dyadicDenominatorPower===32,'Prospective matrix/solver settings differ');
 same(manifest.plan.cases,plans,'Frozen case identity/order differs');same(manifest.plan.discount,{numerator:19,denominator:20},'Mathematical audit discount differs');
 same(manifest.plan.requestedAbsoluteGap,GAP_TARGET,'Frozen absolute gap target differs');
 need(manifest.plan.maximumStates===15376&&manifest.plan.maximumScalarBits===1000000&&manifest.plan.maximumCandidateNumeratorBits===4096,'Frozen integer/state ceilings differ');
 need(manifest.plan.optimizerIterationsReplayed===false&&manifest.plan.fullTrainingReplay===false,'Frozen replay scope differs');
 for(const value of [result,index,completion,start])need(value.manifestSha256===e.hash(M),'Primary manifest binding differs');
 need(completion.resultsSha256===e.hash(R)&&completion.indexSha256===e.hash(I),'Completion output bindings differ');
 need(completion.inventoryComplete===true&&completion.retainedRecords===48&&typeof completion.primaryPassed==='boolean'&&completion.finalFrozenDependencyCheck?.passed===true,'Complete retained inventory/final dependency check missing');
 need(audit.primaryExecutionPassed===completion.primaryPassed,'Independent execution status differs');
 need(completion.resources?.trainingRounds===0&&completion.resources.experimentalModelApiCalls===0,'Experimental training/API scope differs');
 const controls=audit.corruptionNegativeControls;need(controls&&typeof controls==='object'&&!Array.isArray(controls)&&Object.values(controls).every(x=>x===true),'Independent negative controls missing/failed');
 need(typeof audit.actualScientificNegativeControlsAvailable==='boolean'&&audit.actualScientificNegativeControlsAvailable===(completion.scientificallyAvailable>0),'Actual scientific-control availability differs');
 need(Object.keys(controls).length>0||completion.scientificallyAvailable===0,'Available numerical certificates need actual negative controls');
 for(const group of ['sourceHashes','inputHashes']){
  need(manifest[group]&&typeof manifest[group]==='object'&&!Array.isArray(manifest[group]),'Frozen identity map missing '+group);
  for(const [name,h]of Object.entries(manifest[group])){e.bind(name,h);if(group==='sourceHashes')e.bind(file('sources/'+name),h);}
 }
 for(const name of ['research/learned-opponent-study.js','research/learned-opponent-case.js','research/run-learned-opponent.py','research/audit-learned-opponent.py','research/learned-opponent-format.js','research/learned-opponent-analysis.js','research/learned-opponent-evidence.js','research/learned-opponent-web-game.js'])need(manifest.sourceHashes[name]===e.hash(name),'Required frozen source missing '+name);
 const delivery=manifest.v10Delivery;need(delivery&&manifest.inputHashes[delivery.receipt]===delivery.receiptSha256,'Inherited delivery identity map differs');
 const old=e.json(delivery.receipt);need(old.verification?.passed===true&&old.verification.payloadHashesAndCRC===true&&old.sha256===delivery.archiveSha256&&old.bytes===delivery.archiveBytes,'Accepted V10 full delivery differs');
 // Optional historical ZIP is checked when present but is not nested/required.
 if(io.exists?.(delivery.archive))need(sha256(io.readBytes(delivery.archive))===delivery.archiveSha256,'Available accepted V10 archive differs');
 need(result.records?.length===48&&index.records?.length===48&&start.plannedRecords===48,'Every planned label/start identity required');
 const artifacts=new Set();function walkRefs(value,base){
  if(!value||typeof value!=='object')return;
  if(typeof value.file==='string'&&typeof value.sha256==='string'&&Number.isSafeInteger(value.bytes)){if(!base)need(manifest.inputHashes[value.file]===value.sha256,'Original reference absent from frozen input map '+value.file);const ref=e.ref(base,value);artifacts.add(ref.name);return;}
  for(const child of Object.values(value))walkRefs(child,base);
 }
 let available=0,tight=0,failures=0,budgets=0;
 for(let i=0;i<plans.length;i++){
  const plan=plans[i],r=result.records[i],entry=index.records[i];for(const key of Object.keys(plan))same(r?.[key],plan[key],'Record planned identity differs '+key);
  need(entry.id===r.id&&entry.file==='records/'+r.id+'.json'&&entry.status===r.status&&entry.executionSucceeded===r.executionSucceeded&&entry.scientificAvailable===r.scientificAvailable,'Index record/status identity differs');
  const ref=e.ref(PREFIX,entry);same(e.json(ref.name),r,'Aggregate/indexed record differs');
  same(r.input,manifest.inputs[plan.oldRunID],'Frozen checkpoint input identity differs');
  const input=manifest.inputs[plan.oldRunID];need(input?.inputRoot==='project'&&input.oldRunID===plan.oldRunID&&input.checkpointStep===2000000,'Original checkpoint identity missing');
  walkRefs(input,'');for(const [name,h]of Object.entries(e.inputHashes))if(name===input.metadata.file||name===input.finiteGame.file)need(manifest.inputHashes[name]===h,'Original selected source absent from frozen input map');
  const {input:omitted,...output}=r;walkRefs(output,PREFIX);
  need(typeof r.executionSucceeded==='boolean'&&typeof r.scientificAvailable==='boolean','Orthogonal status flags missing');failures+=Number(!r.executionSucceeded);budgets+=Number(r.status==='retained hard-budget timeout');
  if(r.scientificAvailable){available++;tight+=Number(r.certificate?.withinRequestedGap===true);need(r.optimizer?.optimizerIterationsReplayed===false,'False proposal replay scope');
   const events=r.runtime?.events,received=Array.isArray(events)?events.findIndex(x=>x.type==='complete certificate received'):-1,terminated=Array.isArray(events)?events.findIndex(x=>x.type==='termination requested'):-1;
   need(r.runtime?.completeCertificate&&received>=0&&terminated>received&&events.filter(x=>x.type==='complete certificate received').length===1&&events.filter(x=>x.type==='termination requested').length===1&&typeof r.runtime.receivedCompleteMilliseconds==='number'&&r.runtime.receivedCompleteMilliseconds<=r.runtime.terminationRequestedMilliseconds,'Complete scientific report was not received before termination');
   need(events[received].sha256===r.runtime.completeCertificate.sha256&&events[received].elapsedMilliseconds===r.runtime.receivedCompleteMilliseconds&&events[terminated].elapsedMilliseconds===r.runtime.terminationRequestedMilliseconds,'Complete-reception event identity/timing differs');
   const complete=e.ref(PREFIX,r.runtime.completeCertificate),report=e.json(complete.name);for(const key of ['input','mdp','optimizer','baseline','response','certificate','performance'])same(report[key],r[key],'Received complete report differs '+key);
   need(r.optimizer.finalFloat64.bytes===r.mdp.states*8&&r.optimizer.responsePolicy.bytes===r.mdp.states,'Complete final vector/policy dimensions differ');
   for(const name of ['baseline','response']){const p=e.json(e.ref(PREFIX,r[name].path).name);need(p.h===r[name].h&&p.c===r[name].c&&p.h+p.c<=r.mdp.states,'Saved full path decomposition differs');for(const k of ['states','executedA','executedB','nextStates','payoffIndices'])need(Array.isArray(p[k])&&p[k].length===p.h+p.c,'Complete full-path array missing');}
  }else need(r.performance===null&&r.baseline===null&&r.response===null&&r.certificate===null&&typeof r.scientificUnavailableReason==='string','Unavailable scientific quantities must remain null with reason');
 }
 need(completion.executionFailures===failures&&completion.budgetFailures===budgets&&completion.scientificallyAvailable===available&&completion.tightCertificates===tight&&completion.looseCertificates===available-tight,'Orthogonal retained completion counts differ');
 need(completion.primaryPassed===(failures===0),'Primary execution success inconsistent with retained failures');
 need(audit.certifiedRecords===available&&audit.tightRecords===tight&&audit.looseRecords===available-tight&&audit.unavailableRecords===48-available,'Independent retained scientific counts differ');
 const events=e.bytes(J).toString('utf8').trim().split(/\r?\n/).map(line=>JSON.parse(line)),begun=events.filter(x=>x.type==='case started'),retained=events.filter(x=>x.type==='case retained');
 same(begun.map(x=>x.id),plans.map(x=>x.id),'Every case-start journal identity required');same(retained.map(x=>x.id),plans.map(x=>x.id),'Every case-retained journal identity required');
 for(let i=0;i<plans.length;i++){const r=result.records[i],event=retained[i];need(event.status===r.status&&event.executionSucceeded===r.executionSucceeded&&event.scientificAvailable===r.scientificAvailable&&event.recordSha256===index.records[i].sha256,'Retained journal status/hash differs');}
 const summary=deriveSummary(result.records,{independentAuditPassed:true,primaryExecutionPassed:completion.primaryPassed,primaryManifestSha256:e.hash(M),primaryResultsSha256:e.hash(R),primaryIndexSha256:e.hash(I),independentAuditSha256:e.hash(A),audit,resources:completion.resources,counts:{planned:48,executionSucceeded:48-failures,executionFailures:failures,budgetFailures:budgets,scientificallyAvailable:available,tightCertificates:tight,looseCertificates:available-tight,unavailable:48-available},sourceHashes:{analysis:e.hash('research/learned-opponent-analysis.js'),format:e.hash('research/learned-opponent-format.js'),evidence:e.hash('research/learned-opponent-evidence.js'),webGame:e.hash('research/learned-opponent-web-game.js')}});
 for(const field of ['controllerSummaries','seedMeans','pairedDifferences'])same(summary[field],audit.independentSummaries?.[field],'Independent exact descriptive aggregate differs '+field);
 e.recheck();summary.inputHashes=e.inputHashes;return summary;
}
export const localIO=(root=ROOT)=>projectIO(root);
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const summary=analyzeEvidence(localIO());fs.writeFileSync(path.join(ROOT,PREFIX,'summary.json'),jsonBytes(summary));fs.writeFileSync(path.join(ROOT,'research/LEARNED_OPPONENT_RESULTS.md'),resultsText(summary));
 console.log(JSON.stringify({records:summary.records.length,scientificallyAvailable:summary.meta.counts.scientificallyAvailable,pairedDifferences:summary.pairedDifferences.length}));
}

export function resultsText(summary){
 const format=d=>!d?'unavailable':d.status==='unavailable'?'exact '+d.exactSign+'; decimal display unavailable':d.lower+(d.lower===d.upper?'':' … '+d.upper);
 let text='# Unilateral responses against the saved learned opponent\n\n';
 text+='This targeted follow-up continues the final2M saved histories and next controller phases. It changes one seller policy while the deterministic saved partner remains frozen; it introduces no fresh cap, exploration, Q updates or new training. The selected95 controller is the original K4 clock.\n\n';
 text+=`Independent inventory/binding acceptance: true. Scientifically available numerical certificates: ${summary.meta.counts?.scientificallyAvailable??summary.records.filter(r=>r.scientificAvailable).length}/48. Primary execution passed: ${summary.meta.primaryExecutionPassed}. Scientific availability and worker execution status are separate; every planned label is retained. A passed all-unavailable inventory establishes no numerical response claim.\n\n`;
 text+='All signs and comparisons use exact saved-weight values and mathematical discount19/20. A positive achieved gain rejects unilateral optimality only against this partner from this terminal state. A nonpositive proposed gain with a loose upper bound establishes no stability. The legal baseline justifies a zero lower bound for the best achievable improvement without replacing a negative proposed response.\n\n';
 text+='| Controller | Scientific/24 | Execution success/24 | Positive / zero / negative raw gains | Raw-gain min / median / max |\n|---|---|---|---|---|\n';
 for(const c of summary.controllerSummaries)text+=`| ${c.controller} | ${c.available} | ${c.executionSucceeded} | ${c.rawGainSignCounts.positive} / ${c.rawGainSignCounts.zero} / ${c.rawGainSignCounts.negative} | ${[c.minimum,c.median,c.maximum].map(x=>format(optionalDisplay(x))).join(' / ')} |\n`;
 text+='\n';
 text+='| Seed | Controller | Seller | Execution/scientific | Primary status | Raw achieved gain | Remaining gap upper | Possible best improvement |\n|---|---|---|---|---|---|---|---|\n';
 for(const r of summary.records)text+=`| ${r.seed} | ${r.control.id} | ${r.focal} | ${r.executionSucceeded}/${r.scientificAvailable} | ${r.status} | ${format(r.display.rawGain)} | ${format(r.display.responseOptimalityGap)} | ${r.display.bestImprovement?format(r.display.bestImprovement.lower)+' to '+format(r.display.bestImprovement.upper):'unavailable'} |\n`;
 text+='\nThe 24 seller results per controller are dependent within12 market seeds. All12 two-seller means per controller and12 paired controller differences are retained in summary.json; a missing seller makes the corresponding mean/pair unavailable. Counts, range and median are descriptive. No bootstrap, CI, p-value, population effect or convergence claim is added.\n\n';
 text+='Controllers have separately trained policy pairs and different clocks, legal experiences and phase capacities. The paired-seed comparison is not a clock-only causal intervention or a cap-frequency causal effect. Within one checkpoint the achieved response comparison holds the opponent and initial state fixed.\n\n';
 text+='This is a white-box response audit: the optimizer knows the full frozen partner lookup, legal masks and saved reward table. It is not a competitor learning a response from limited observations.\n\n';
 text+='| Seed | Startup-only two-seller mean gain | Selected95 two-seller mean gain | Paired selected95 minus startup-only |\n|---|---|---|---|\n';
 for(const seed of summary.orderedSeeds){const a=summary.seedMeans.find(x=>x.seed===seed&&x.controller==='startup-only'),b=summary.seedMeans.find(x=>x.seed===seed&&x.controller==='selected95'),d=summary.pairedDifferences.find(x=>x.seed===seed);text+=`| ${seed} | ${format(optionalDisplay(a.meanRawGain))} | ${format(optionalDisplay(b.meanRawGain))} | ${format(optionalDisplay(d.difference))} |\n`;}
 text+='\n';
 text+='Both firms retain unweighted training-support counts across the full transient plus one cycle and exact normalized infinite-discounted exposure to unsupported states/actions. These describe frozen lookup-table reliance, not a partner that resumes learning. Secondary baseline/response customer benefit is an eventual-cycle mean, separate from private-profit PV and finite-prefix guarantees.\n\n';
 text+='The saved final f64 proposal, exact dyadic quantization, response argmax, complete paths and all legal Bellman edges are checked independently. Optimizer iteration trajectories and complete original training are not replayed. Accepted old numerical payoff tables are reused through explicit hash bindings; this is not new economic re-enumeration or formal verification. Budget failures, loose certificates and resource overruns remain visible.\n\n';
 const resources=summary.meta.resources??{};
 text+=`Primary elapsed seconds: ${resources.seconds??'unavailable'}. Largest sampled Node-process RSS bytes: ${resources.largestSampledNodeProcessRSSBytes??'unavailable'}. Largest approximately paired Node/supervisor RSS bytes: ${resources.largestApproximatelyPairedRSSBytes??'unavailable'}. These are recorded samples, not continuously measured peaks. New primary output before completion bytes: ${resources.newOutputBytesBeforeCompletion??'unavailable'}. Retained soft-target flags: ${JSON.stringify(resources.softTargetExceeded??null)}. Sampling/unavailable scope: ${resources.scope??resources.pairedRSSUnavailableReason??'See complete primary resource records'}.\n\n`;
 text+='Frozen-partner policy-response audits are established prior work, including Lopes de Moraes and De Losso, Algorithmic Collusion Without Deterrence, arXiv2610.21867v2 §§3.2(iv),4.5. This guarded phase-aware application makes no equilibrium, intent, mutual-adaptation, every-state incentive or real-market claim. No language-model/chat/API seller calls or paid inference were used; Codex development assistance is separate.\n';
 return text;
}
