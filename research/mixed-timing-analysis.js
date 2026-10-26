// Descriptive adapter. Importing performs no evidence reads or writes.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
import {rational,rationalSign,equalRational,scientificDisplay,constructedCalendarTiming,statusCategory} from './mixed-timing-format.js';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const PREFIX='research/mixed-timing-results/';
const SCENARIOS=['base-g15-t1','scale0.5-g15-t1','lower-quality-g15-t1','lowcost-g15-t1','base-g11-t1','base-g31-t1','base-g15-t0.5','base-g15-t2'];
const LABELS=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor'];
const KINDS=['finite','effective','nominal'];
const need=(ok,message)=>{if(!ok)throw Error(message);};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const histogram=(values,key)=>{const result={};for(const value of values){const label=key(value);result[label]=(result[label]??0)+1;}return result;};
const orderedObject=value=>Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b)));
const jsonBytes=value=>Buffer.from(JSON.stringify(value)+'\n');
function safeName(value){need(typeof value==='string'&&value.length>0&&!value.includes('\\')&&!value.includes(':')&&!value.startsWith('/')&&value.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Unsafe evidence name');return value;}
export const defaultSelection=Object.freeze({kind:'finite',scenario:'base-g15-t1',target:'cap-95pct',calendar:'mixed',chosenBeforeOutcomeInspection:true,
 scope:'Presentation choice before new cases, not scientific preregistration; retain this selection even if its result is zero or unavailable.'});

export function analyzeEvidence(io){
 const inputHashes={},cache=new Map();
 const bytes=name=>{name=safeName(name);if(!cache.has(name))cache.set(name,Buffer.from(io.readBytes(name)));return cache.get(name);};
 const hash=name=>{const h=crypto.createHash('sha256').update(bytes(name)).digest('hex');if(inputHashes[name])need(inputHashes[name]===h,'Conflicting source identity '+name);inputHashes[name]=h;return h;};
 const read=name=>{hash(name);return JSON.parse(bytes(name).toString('utf8').replace(/^\uFEFF/,''));};
 const M=PREFIX+'manifest.json',R=PREFIX+'results.json',I=PREFIX+'index.json',C=PREFIX+'completion.json',A=PREFIX+'independent-audit.json',J=PREFIX+'journal.jsonl',E=PREFIX+'execution-start.json';
 // A failed/missing audit blocks all later inherited evidence reads.
 const audit=read(A);need(audit.passed===true&&audit.requiresOrchestrator===false&&audit.continuousChecksComputedInProcess===true,'Complete authoritative mixed-timing audit has not passed');
 const manifest=read(M),result=read(R),index=read(I),completion=read(C),start=read(E);
 for(const [field,name] of [['studyManifestHash',M],['resultsSha256',R],['indexSha256',I],['completionSha256',C],['journalSha256',J],['executionStartSha256',E]])need(audit[field]===hash(name),'Independent output binding differs '+field);
 for(const [field,name] of [['auditorSourceHash','research/audit-mixed-study.py'],['orchestratorSourceHash','research/audit-mixed-study.py'],['controlAuditorSourceHash','research/audit-mixed-timing.js'],['continuousAuditorSourceHash','research/audit-mixed-continuous.py'],['arithmeticBackendHash','research/audit-continuous-study.py']])need(audit[field]===hash(name),'Independent source binding differs '+field);
 need(audit.auditorEntryPoint==='research/audit-mixed-study.py','Authoritative auditor entry point differs');
 need(audit.inheritedPremiseRevalidation===false,'Reused inherited premise scope differs');
 need(audit.models===24&&audit.finiteModels===8&&audit.continuousModels===16&&audit.targetLabels===120&&audit.finiteTargetLabels===40&&audit.continuousTargetLabels===80,'Full independent inventory missing');
 need(Object.keys(audit.corruptionNegativeControls??{}).length>0&&Object.values(audit.corruptionNegativeControls).every(x=>x===true),'Independent corruption controls missing/failed');
 need(completion.models===24&&completion.targetLabels===120&&typeof completion.passed==='boolean'&&audit.primaryExecutionPassed===completion.passed,'Primary execution inventory/status differs');
 need(completion.finalFrozenDependencyCheck?.passed===true,'Final frozen dependency check failed');
 need(completion.resources?.newTrainingRounds===0&&completion.resources?.experimentalModelApiCalls===0,'No-new-training/experimental-API execution scope differs');
 for(const value of [result,index,completion,start])need(value.manifestSha256===hash(M),'Primary manifest binding differs');
 need(completion.resultsSha256===hash(R)&&completion.indexSha256===hash(I),'Primary output binding differs');
 need(manifest.plan?.modelCount===24&&manifest.plan?.targetLabels===120&&manifest.plan?.maxK===65536&&manifest.plan?.displayPrecision===30,'Prospective model/ceiling/precision plan differs');
 const plan=SCENARIOS.flatMap(scenario=>KINDS.map(kind=>({id:scenario+'--'+kind,scenario,kind})));
 need(manifest.plan.models?.length===24&&manifest.plan.models.every((p,i)=>p.id===plan[i].id&&p.scenario===plan[i].scenario&&p.kind===plan[i].kind&&same(p.labels,LABELS)),'Planned ordering/identity differs');
 need(result.records?.length===24&&index.records?.length===24,'Retained models missing');
 const visited=new Set();
 function bind(name,expected){name=safeName(name);need(hash(name)===expected,'Frozen dependency drift '+name);}
 function closure(name,expected){bind(name,expected);if(visited.has(name))return;visited.add(name);const m=read(name);
  for(const group of ['sourceHashes','inputHashes'])for(const [dep,h]of Object.entries(m[group]??{})){bind(dep,h);if(path.posix.basename(dep)==='manifest.json')closure(dep,h);}
 }
 for(const group of ['sourceHashes','inputHashes'])for(const [name,h]of Object.entries(manifest[group]??{})){
  bind(name,h);if(path.posix.basename(name)==='manifest.json')closure(name,h);
  if(group==='sourceHashes')bind(PREFIX+'sources/'+name,h);
 }
 const delivery=read('output/adaptive-package-verification.json');
 need(delivery.verification?.passed===true&&delivery.verification?.payloadHashesAndCRC===true&&manifest.v9Delivery?.receiptSha256===hash('output/adaptive-package-verification.json')&&manifest.v9Delivery?.archiveSha256===delivery.sha256,'Accepted V9 evidence receipt differs');
 // Nested historical archives are optional in portable extracted evidence.
 if(io.exists?.(delivery.archive))need(crypto.createHash('sha256').update(io.readBytes(safeName(delivery.archive))).digest('hex')===delivery.sha256,'Available V9 archive differs');
 const finiteIndexFile='research/sparse-display-results/index.json',finiteIndex=read(finiteIndexFile);
 need(finiteIndex.cases?.length===8,'Eight indexed finite games required');
 const finiteGameSources={},finiteGames=[];
 for(const scenario of SCENARIOS){
  const entries=finiteIndex.cases.filter(x=>x.scenario===scenario);need(entries.length===1&&entries[0].status==='completed','Finite source index identity differs');
  const entry=entries[0],name='research/sparse-display-results/'+entry.file;bind(name,entry.sha256);const game=read(name),f=game.finite,n=f?.prices?.length;
  need(game.scenario?.id===scenario&&Number.isInteger(n)&&n>0&&n<=62,'Finite game dimensions/identity differ');
  need(f.prices.every((p,i)=>Number.isFinite(p)&&(!i||p>f.prices[i-1])),'Finite increasing price table differs');
  need(Number.isInteger(f.capIndex)&&f.capIndex>=0&&f.capIndex<n&&game.cap?.index===f.capIndex&&game.cap?.price===f.prices[f.capIndex],'Finite physical cap identity differs');
  need(f.sets?.length===n&&f.sets.every(s=>s.length>0&&s.every((a,j)=>Number.isInteger(a)&&a>=0&&a<n&&(!j||a>s[j-1]))),'Finite masks malformed');
  need(f.upper?.length===n&&f.upper.every((a,i)=>a===f.sets[i].at(-1)&&(!i||a>=f.upper[i-1])),'Finite upper map identity differs');
  for(const key of ['consumerSurplus','profitA','profitB','quantityA','quantityB'])need(f.rewards?.[key]?.length===n*n&&f.rewards[key].every(Number.isFinite),'Finite full payoff dimension differs '+key);
  finiteGames.push(game);finiteGameSources[scenario]={file:name,sha256:hash(name),indexFile:finiteIndexFile,indexSha256:hash(finiteIndexFile)};
 }
 const models=[],targetRows=[];
 let failures=0;
 for(let p=0;p<plan.length;p++){
  const expected=plan[p],planned=manifest.plan.models[p],record=result.records[p],entry=index.records[p],name=PREFIX+'records/'+expected.id+'.json';
  need(record.id===expected.id&&record.scenario===expected.scenario&&record.kind===expected.kind&&entry.id===expected.id&&entry.file==='records/'+expected.id+'.json','Record/index identity differs');
  bind(name,entry.sha256);need(same(read(name),record),'Per-record/aggregate mismatch');
  need(record.status===entry.status&&record.targets?.length===5&&entry.targetLabels===5&&record.targets.every((t,i)=>t.label===LABELS[i]),'Every ordered target label must be retained');
  need(record.finiteFile===planned.finiteFile&&record.continuousFile===planned.continuousFile&&planned.finiteFile===finiteGameSources[expected.scenario].file,'Model input/source identity differs');
  need(Number.isInteger(record.calculationFailures)&&record.calculationFailures>=0&&record.calculationFailures<=5,'Failure inventory malformed');failures+=record.calculationFailures;
  const duplicates=new Map();
  const targets=record.targets.map(t=>{
   need(t.id===expected.id+'--'+t.label&&t.scenario===expected.scenario&&t.kind===expected.kind,'Target identity differs');
   const category=statusCategory(t);need(t.frontier?.maxK===65536&&Array.isArray(t.frontier.queryLengths)&&t.frontier.queryLengths.every(k=>Number.isInteger(k)&&k>=1&&k<=65536),'Bounded target query inventory differs');
   if(t.actualThresholdExact!==null){const f=rational(t.actualThresholdExact),key=f.n+'/'+f.d;need((t.duplicateOf??null)===(duplicates.get(key)??null),'Target duplicate identity differs');if(!duplicates.has(key))duplicates.set(key,t.id);}
   else need(category==='calculation-or-identity-failure'&&t.duplicateOf===null,'Unknown threshold must remain an honest failure');
   need(t.calendar&&Array.isArray(t.executionPreview)&&Array.isArray(t.calendar.blockPreview64),'Retained calendar/preview missing');
   if(t.rates===null)need(t.calendar.kind==='unavailable','Unavailable rates must not invent a calendar');
   else {
    for(const key of ['lower','upper'])rational(t.rates.optimumRateBoundsExact[key]);rational(t.rates.constructedRateExact);
    need(t.rates.bestFixedK===t.frontier.bestFixedK,'Own fixed comparator differs');
    if(t.rates.absoluteSavingBoundsExact)for(const key of ['lower','upper'])need(t.rates.absoluteSavingSigns?.[key]===rationalSign(t.rates.absoluteSavingBoundsExact[key]),'Exact saving sign differs');
    if(t.rates.constructedSavingExact)need(t.rates.constructedSavingSign===rationalSign(t.rates.constructedSavingExact),'Constructed saving sign differs');
    if(category==='startup-only')need(t.calendar.kind==='startup-only'&&t.calendar.startupCaps===1&&t.frontier.bestFixedK===null&&rationalSign(t.rates.constructedRateExact)==='zero','Startup-only is not zero intervention or a fixed period');
    if(t.calendar.kind==='funded-mixed')need(equalRational(t.rates.constructedRateExact,t.rates.optimumRateBoundsExact.upper),'Constructed rate must equal exact rational upper bound');
   }
   const timing=constructedCalendarTiming(t.calendar,t.executionPreview.length);
   const view={...t,statusCategory:category,constructedCalendarTiming:timing,
    display:{rate:t.rates?scientificDisplay(t.rates.constructedRateExact):null,
     absoluteSaving:t.rates?.absoluteSavingBoundsExact?{lower:scientificDisplay(t.rates.absoluteSavingBoundsExact.lower),upper:scientificDisplay(t.rates.absoluteSavingBoundsExact.upper)}:null,
     relativeSaving:t.rates?.relativeSavingBoundsExact?{lower:scientificDisplay(t.rates.relativeSavingBoundsExact.lower),upper:scientificDisplay(t.rates.relativeSavingBoundsExact.upper)}:null}};
   targetRows.push({...view,modelId:expected.id,source:{file:name,sha256:hash(name)}});return view;
  });
  models.push({...record,source:{file:name,sha256:hash(name)},targets});
 }
 need(failures===completion.calculationFailures&&failures===audit.calculationFailures,'Retained calculation failure counts differ');
 need(targetRows.length===120&&same(orderedObject(histogram(targetRows,t=>t.status)),orderedObject(audit.statusCounts)),'Full status inventory differs from independent audit');
 const journal=bytes(J).toString('utf8').trim().split(/\r?\n/).map(x=>JSON.parse(x));need(journal.length===48,'All started/finished journal events required');
 for(let i=0;i<models.length;i++){need(journal[2*i].id===models[i].id&&journal[2*i].status==='started'&&journal[2*i+1].id===models[i].id&&journal[2*i+1].status===models[i].status&&journal[2*i+1].calculationFailures===models[i].calculationFailures,'Journal order/status differs');}
 const groups={finite:targetRows.filter(t=>t.kind==='finite'),effective:targetRows.filter(t=>t.kind==='effective'),nominal:targetRows.filter(t=>t.kind==='nominal'),continuous:targetRows.filter(t=>t.kind!=='finite')};
 const populationCounts={},statusCounts={},duplicateCounts={};
 for(const [kind,rows]of Object.entries(groups)){
  populationCounts[kind]={models:kind==='continuous'?16:8,targetLabels:rows.length,availableRates:rows.filter(t=>t.rates!==null).length,
   exactOptimumRates:rows.filter(t=>t.rates?.exactOptimum===true).length,
   ownFixedComparators:rows.filter(t=>t.rates?.fixedRateExact!=null).length,
   certifiedPositiveSavings:rows.filter(t=>t.rates?.absoluteSavingSigns?.lower==='positive').length,
   exactZeroSavings:rows.filter(t=>t.rates?.absoluteSavingSigns?.lower==='zero'&&t.rates?.absoluteSavingSigns?.upper==='zero').length,
   firstLongBeyondExecutionPreview:rows.filter(t=>t.constructedCalendarTiming.withinExecutionPreview===false).length};
  statusCounts[kind]={primary:histogram(rows,t=>t.status),categories:histogram(rows,t=>t.statusCategory)};
  duplicateCounts[kind]=rows.filter(t=>t.duplicateOf!==null).length;
 }
 const sourceHashes={analysis:hash('research/mixed-timing-analysis.js'),format:hash('research/mixed-timing-format.js')};
 const summary={schemaVersion:1,meta:{independentAuditPassed:true,executionPassed:completion.passed,
  primaryManifestSha256:hash(M),primaryResultsSha256:hash(R),primaryIndexSha256:hash(I),independentAuditSha256:hash(A),
  sourceHashes,populationCounts,statusCounts,duplicateCounts,resources:completion.resources,inheritedPremiseRevalidation:false,defaultSelection,finiteGameSources,
  audit:Object.fromEntries(Object.entries(audit).filter(([key])=>key!=='details')),
  scope:'Same physical cap and full guard; every activation prefix, every allowed seller response and realized controller path. Rule-frequency comparison is not monetary cost, behavior, equilibrium or empirical-market validation. Finite exact saved-weight results and continuous enclosures are separate populations.'},
  scenarioOrder:SCENARIOS,targetOrder:LABELS,finiteGames,models,targetRows,inputHashes};
 return summary;
}

export function resultsText(summary){
 let text='# Mixed gaps between identical cap executions\n\n';
 text+='This descriptive report is generated only after the complete independent timing audit accepts the raw study and exact source/output bindings. The inherited physical cap, full guard and original absolute targets remain fixed. It contains no new learning or economic calibration.\n\n';
 text+='The finite population has 8 saved numerical games and 40 target labels. The continuous population has 16 model records and 80 labels, split into 40 effective-model and 40 nominal-sensitivity labels. Duplicates, zero savings, unresolved boundaries, censoring, infeasibility and calculation failures remain present; these are not independent empirical observations.\n\n';
 text+=`Independent audit accepted: true. Primary numerical execution passed: ${summary.meta.executionPassed}. A passed audit establishes honest full retention, not that every endpoint resolved.\n\n`;
 text+='The benchmark is each label\'s own largest safe fixed integer gap where certified. Exact rational rate bounds and the constructed calendar rate remain separate from outward decimal displays. For continuous interiors, a conservative feasible rate is not declared the unknown exact-real optimum. Frequency counts applications of the cap rule, even when no quote changes; it is not a monetary cost.\n\n';
 for(const [title,kinds]of [['All 40 saved finite labels',['finite']],['All 80 continuous labels',['effective','nominal']]]){
  text+='## '+title+'\n\n| Scenario | Model | Target | Primary status | Own fixed K | Constructed cap-rule rate | Absolute saving bounds | First long execution |\n|---|---|---|---|---|---|---|---|\n';
  for(const t of summary.targetRows.filter(t=>kinds.includes(t.kind))){const r=t.rates,d=t.display;
   const rate=d.rate?d.rate.lower+(d.rate.lower===d.rate.upper?'':' … '+d.rate.upper):'unavailable';
   const saving=d.absoluteSaving?d.absoluteSaving.lower.lower+' … '+d.absoluteSaving.upper.upper:'unavailable';
   text+=`| ${t.scenario} | ${t.kind} | ${t.label} | ${t.status} | ${r?.bestFixedK??'unavailable'} | ${rate} | ${saving} | ${t.constructedCalendarTiming.firstLongExecution??t.constructedCalendarTiming.reason} |\n`;
  }text+='\n';
 }
 text+='## Safety, illustrations and scope\n\n';
 text+='Credit is exact worst-case bookkeeping, not a payment or observed seller/customer reward. An individually losing long block is chosen only after prior short blocks fund its debt. The guarantee covers every cumulative prefix since the first real cap, not sliding windows or independently restarted blocks. The old memory pair earns no reward. Actual execution rewards and boundary credit are distinct; credit updates only at completed blocks.\n\n';
 text+='The 64 block decisions and finite256/continuous64 execution previews are bounded illustrations. First-long timing is computed exactly from the constructed credits; it can lie far beyond the preview. Neither a preview\'s cap ratio nor absence of a long block estimates asymptotic frequency. Continuous price/reward enclosures are not invented point values. The manual finite game uses the unchanged saved masks and reward tables. No old phase-Q policy is replayed under the new clock.\n\n';
 text+='Global continuous order/contraction premises are reused through accepted immutable source/audit bindings; this stage independently rechecks inherited scalar-root certificates and orbit propagation, and checks every used sum and timing certificate, not those inherited global premises again. Separate80/130-digit control implementations share Decimal/library assumptions. This is validated numerical evidence, not formal verification. The exact finite claim concerns saved binary64 weights and the restricted cap-first two-mode family.\n\n';
 const resources=summary.meta.resources;
 text+=`Primary runtime: ${resources.seconds??'unavailable'} seconds. Largest after-model working-set sample: ${resources.largestObservedRSSBytes??'unavailable'} bytes; this is not a continuously measured peak. New primary output before completion: ${resources.newOutputBytesBeforeCompletion??'unavailable'} bytes. Soft-target overrun flags are retained: ${JSON.stringify(resources.softTargetExceeded??null)}. All labels and artifacts are retained despite any overrun; no precision, target or search ceiling was changed to reduce output.\n\n`;
 text+='Adjacent mixtures, renewal/Jensen arguments and funded pathwise budgets have established prior literature, documented in the novelty/prospective reviews. Zero or small frequency reductions are valid results. No language-model/chat/API seller calls, new learner training, purchase, human study or external submission belongs to this analysis. Codex development assistance is disclosed separately.\n';
 return text;
}

export function localIO(root=ROOT){return {readBytes:name=>fs.readFileSync(path.join(root,safeName(name))),exists:name=>fs.existsSync(path.join(root,safeName(name)))};}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===2,'Use node research/mixed-timing-analysis.js');const summary=analyzeEvidence(localIO());
 fs.writeFileSync(path.join(ROOT,PREFIX+'summary.json'),jsonBytes(summary));fs.writeFileSync(path.join(ROOT,'research/MIXED_TIMING_RESULTS.md'),resultsText(summary));
 console.log(JSON.stringify({passed:true,models:summary.models.length,targetLabels:summary.targetRows.length,executionPassed:summary.meta.executionPassed}));
}
