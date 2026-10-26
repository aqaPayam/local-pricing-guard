// Descriptive adapter only; requires final independently audited primary output.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const file=p=>path.join(ROOT,p),bytes=p=>fs.readFileSync(file(p));
const read=p=>JSON.parse(bytes(p)),sha=p=>crypto.createHash('sha256').update(bytes(p)).digest('hex');
const need=(condition,message)=>{if(!condition)throw Error(message);};
const inputHashes={};const use=p=>{inputHashes[p]=sha(p);return read(p);};
const M='research/misspec-results/manifest.json',R='research/misspec-results/results.json';
const A='research/misspec-results/independent-audit.json',C='research/misspec-results/completion.json';
const manifest=use(M),results=use(R),audit=use(A),completion=use(C);
need(audit.passed===true,'Independent misspecification audit has not passed');
need(audit.studyManifestHash===sha(M)&&audit.resultsSha256===sha(R),'Independent primary identity binding differs');
need(audit.auditorSourceHash===sha('research/audit-misspec-study.py'),'Independent auditor source binding differs');
inputHashes['research/audit-misspec-study.py']=sha('research/audit-misspec-study.py');
need(audit.arithmeticBackendHash===sha('research/audit-continuous-study.py'),'Independent arithmetic backend binding differs');
inputHashes['research/audit-continuous-study.py']=sha('research/audit-continuous-study.py');
need(Object.keys(audit.corruptionNegativeControls??{}).length>0&&Object.values(audit.corruptionNegativeControls).every(Boolean),'Independent corruption controls missing/failed');
need(results.manifestSha256===sha(M)&&completion.resultsSha256===sha(R)&&completion.finalFrozenDependencyCheck?.passed===true,'Primary completion/result binding differs');
for(const field of ['sourceHashes','inputHashes'])for(const [name,hash]of Object.entries(manifest[field]??{})){
 need(sha(name)===hash,'Frozen dependency drift '+name);inputHashes[name]=hash;
 const snapshot='research/misspec-results/sources/'+name;
 if(field==='sourceHashes'&&fs.existsSync(file(snapshot))){need(sha(snapshot)===hash,'Frozen source snapshot drift '+snapshot);inputHashes[snapshot]=hash;}
}
const levels=manifest.plan.uncertaintyBounds.map(r=>({id:r.exactDecimal,dExact:r.exactDecimal,numerator:r.numerator,denominator:r.denominator,units:r.units}));
need(levels.length===4&&JSON.stringify(levels.map(r=>r.dExact))===JSON.stringify(['0','0.001','0.01','0.05']),'Four exact predeclared error levels differ');
const pairs=r=>r?{lower:r.lower,upper:r.upper}:null;
function radiusView(radius){const result={status:radius?.status??'unresolved',safeSet:radius?.safeNonnegativeSet??null,source:radius??null};
 if(radius?.radiusEnclosure){result.lower=radius.radiusEnclosure.lower;result.upper=radius.radiusEnclosure.upper;}
 if(radius?.certifiedRadiusLowerBound!==undefined)result.censoredLowerBound=radius.certifiedRadiusLowerBound;
 if(radius?.certifiedSimpleSufficientRadiusLower!==undefined)result.simpleSufficientLower=radius.certifiedSimpleSufficientRadiusLower;
 return result;
}
function policyView(policy){return {slotId:policy.slot,available:policy.available===true,policyKind:policy.policy?.kind??'unavailable',
 period:policy.policy?.period??null,startupCaps:policy.startupCapCount??null,duplicateOf:policy.duplicateOf??null,
 frequency:pairs(policy.capRuleActivationFrequency),singleStartupCapVariant:policy.singleStartupCapVariant??null,
 radius:radiusView(policy.radius),levels:policy.sensitivity.map(level=>({dExact:level.dbar.exactDecimal,status:level.status,
  surplus:pairs(level.surplus),reserve:pairs(level.reserve),
  finiteActivationAverageFromArbitraryOldPrices:level.finiteActivationAverageGuaranteedFromArbitraryOldPrices??null}))};}
function robustView(value){return {dExact:value.dbar.exactDecimal,status:value.status,
 largestPeriod:value.largestPeriod??null,certifiedSafePeriodLowerBound:value.certifiedSafePeriodLowerBound??null,
 certifiedFailingPeriodUpperBound:value.certifiedFailingPeriodUpperBound??null,source:value};}
const rows=[],targetRows=[],policyRows=[],reserveRows=[],robustPeriodRows=[];
for(const scenario of manifest.plan.scenarios){const row={scenario:scenario.id,economy:scenario.economy};
 for(const continuum of manifest.plan.continuums){
  const selected=results.records.filter(r=>r.scenario===scenario.id&&r.continuum===continuum);need(selected.length===1,'Missing/duplicate primary model '+scenario.id+'/'+continuum);
  const current=selected[0],sourceRecord=`research/misspec-results/records/${scenario.id}-${continuum}.json`,journal=use(sourceRecord);
  need(JSON.stringify(journal)===JSON.stringify(current),'Primary per-record journal mismatch '+sourceRecord);
  need(current.targets.length===5&&manifest.plan.targetLabels.every(label=>current.targets.some(t=>t.label===label)),'Retained target labels differ '+sourceRecord);
  const model={status:current.status,actualDemand:current.actualDemand,nominalEnforcement:current.nominalEnforcement??null,
   sourceRecord,sourceRecordSha256:sha(sourceRecord),targetGroups:[],failure:current.failure??null};
  for(const target of current.targets){
   need(target.policies.length===3&&manifest.plan.policySlots.every(slot=>target.policies.some(p=>p.slot===slot)),'Three fixed policy slots differ');
   const compact={label:target.label,requestedExact:target.requestedImported?.exactDecimal??null,
    thresholdExact:target.actualThresholdExact??target.actualThresholdImported?.exactDecimal??null,
    targetIdentityAvailable:target.targetIdentityAvailable??(typeof target.requestedImported?.exactDecimal==='string'&&typeof target.actualThresholdImported?.exactDecimal==='string'),
    d0ReproducesClosedSelection:target.d0ReproducesClosedSelection??false,
    closedSelectionStatus:target.closedSelectionStatus??null,policySlots:target.policies.map(policyView),robustPeriods:target.robustPeriods.map(robustView)};
   need(compact.robustPeriods.length===4&&JSON.stringify(compact.robustPeriods.map(v=>v.dExact))===JSON.stringify(levels.map(v=>v.dExact)),'Four robust period levels differ');
   const context={scenario:scenario.id,continuum,label:target.label,requestedExact:compact.requestedExact,thresholdExact:compact.thresholdExact};
   for(const policy of compact.policySlots){
    need(policy.levels.length===4&&JSON.stringify(policy.levels.map(v=>v.dExact))===JSON.stringify(levels.map(v=>v.dExact)),'Four fixed-policy levels differ');
    policyRows.push({...context,...policy});
    for(const level of policy.levels)reserveRows.push({...context,slotId:policy.slotId,period:policy.period,duplicateOf:policy.duplicateOf,...level});
   }
   for(const robust of compact.robustPeriods)robustPeriodRows.push({...context,...robust});
   targetRows.push({...context,...compact});model.targetGroups.push(compact);
  }
  row[continuum]=model;
 }
 row.physicalCap=row.effective.nominalEnforcement?.physicalCap??row.nominal.nominalEnforcement?.physicalCap??null;
 const classification=model=>model.targetGroups.map(t=>[t.label,t.policySlots.map(p=>[p.slotId,p.radius.status,p.levels.map(l=>l.status)]),t.robustPeriods.map(r=>[r.status,r.largestPeriod])]);
 row.nominalEffectiveClassificationsAgree=JSON.stringify(classification(row.effective))===JSON.stringify(classification(row.nominal));
 rows.push(row);
}
need(rows.length===8&&results.records.length===16&&targetRows.length===80&&policyRows.length===240&&reserveRows.length===960&&robustPeriodRows.length===320,'Complete declared misspecification inventory differs');
const histogram=(values,key)=>{const result={};for(const value of values){const name=key(value);result[name]=(result[name]??0)+1;}return result;};
const levelAggregates=[];
for(const continuum of manifest.plan.continuums)for(const level of levels)for(const slot of manifest.plan.policySlots){
 const values=reserveRows.filter(r=>r.continuum===continuum&&r.dExact===level.dExact&&r.slotId===slot);
 levelAggregates.push({continuum,dExact:level.dExact,slotId:slot,labels:values.length,statuses:histogram(values,r=>r.status)});
}
const summary={kind:'Hash-gated descriptive adapter only; fixed deployed enforcement and alternative actual demand, no new cases or optimization',
 analysisSourceHash:sha('research/misspec-analysis.js'),inputHashes,levels,rows,targetRows,policyRows,reserveRows,robustPeriodRows,levelAggregates,
 counts:{scenarioLabels:rows.length,modelSemantics:results.records.length,targetLabels:targetRows.length,policySlots:policyRows.length,
  availablePolicySlots:policyRows.filter(r=>r.available).length,duplicatePolicySlots:policyRows.filter(r=>r.duplicateOf!==null).length,
  reserveRows:reserveRows.length,robustPeriodRows:robustPeriodRows.length,unresolvedModels:completion.unresolvedModels,
  d0ClosedSelectionsReproduced:targetRows.filter(r=>r.d0ReproducesClosedSelection).length,
  nominalEffectiveClassificationsAgree:rows.filter(r=>r.nominalEffectiveClassificationsAgree).length,
  radiusStatuses:histogram(policyRows,r=>r.radius.status),robustPeriodStatuses:histogram(robustPeriodRows,r=>r.status)},
 audits:{independent:Object.fromEntries(Object.entries(audit).filter(([key])=>key!=='details'))},resources:completion.resources,
 scope:'Dimensionless downward inside-quality displacement with outside quality fixed. Nominal external enforcement, physical cap, original absolute target and price orbit stay fixed. Four uncertainty levels are illustrative bounds, not empirically calibrated confidence intervals. Duplicate slots/repeated calibrations are not independent evidence. No unknown enforcement, uncertain mu, non-logit demand, incentive stability or general controller optimum is covered.'};
const displayRadius=p=>p.radius.status.includes('empty safe')?'empty (fails at zero)':p.radius.lower!==undefined?`≈${Number(p.radius.lower).toPrecision(5)}…${Number(p.radius.upper).toPrecision(5)}`:p.radius.censoredLowerBound!==undefined?`≥${p.radius.censoredLowerBound} (censored)`:p.radius.status;
const displayPeriod=r=>r.status==='no recurring cap needed for the long-run target'?'none needed':r.status==='largest certified fixed period'?String(r.largestPeriod):r.status==='infeasible for this fixed-cap family'?'fixed cap insufficient':r.status;
let text='# Fixed enforcement with lower actual demand quality\n\n';
text+='This export runs only after the independent audit passes and exactly binds the primary manifest/results, current auditor/backend sources, frozen dependencies and all per-record journals. It adds no sensitivity cases or controller optimization. The target remains the original absolute F-delta amount; enforcement and the physical cap are not refitted to demand.\n\n';
text+='## Three policy slots and their different questions\n\n';
text+='Guard-only, the CLOSED-study selected timing and permanent activation of the same physical cap are preserved for every old target. Repeated policies are explicitly marked duplicates. A policy already below target at d=0 has an empty safe nonnegative set; it is not called a safe zero-radius policy. Exact zero, unresolved overlaps and censored radii remain distinct. The compact summary retains complete radius sign records and the simple nominal-reserve/(B*mu) sufficient comparison.\n\n';
text+='Here d is a taste-scale displacement: actual inside quality falls by d*mu while outside quality remains fixed. It is not percentage error, a confidence level or an estimated real-market error rate. All four tested bounds are predeclared exact rationals.\n\n';
text+='## Effective-model 95% target radius comparison\n\n';
text+='Displayed positive endpoints are approximate; full directed decimal enclosures are retained in the summary and raw records. Empty or unresolved sets are never converted to ordinary positive/zero radii.\n\n';
text+='| Scenario | Guard-only radius | Inherited selected timing radius | Permanent same-cap radius |\n|---|---|---|---|\n';
for(const row of rows){const t=row.effective.targetGroups.find(v=>v.label==='cap-95pct');text+=`| ${row.scenario} | ${t.policySlots.map(displayRadius).join(' | ')} |\n`;}
text+='\n## All fixed-target robust timing comparisons, effective model\n\n';
text+='These periods are new design comparisons for a KNOWN bound [0,d_bar], within the same fixed-cap fixed-period family. They are not changes to the inherited fixed-policy slot or adaptation to observed demand. The d=0 comparison must reproduce the closed selection.\n\n';
text+='| Scenario | Original target | d=0 | d=0.001 | d=0.01 | d=0.05 |\n|---|---|---|---|---|---|\n';
for(const row of rows)for(const t of row.effective.targetGroups)text+=`| ${row.scenario} | ${t.label} | ${t.robustPeriods.map(displayPeriod).join(' | ')} |\n`;
text+='\n## Reserve, startup and scope\n\n';
text+='Every fixed policy retains its surplus, reserve and certification at all four bounds. Welfare decreases with d, so checking the endpoint certifies a uniform bound over fixed unknown d in [0,d_bar]; no distribution or failure probability is assumed. Near-100% fragility may simply reflect a target that already consumes nearly all modeled cap welfare. It is not evidence of a new emergent mechanism. Timing alone can fail when even permanent activation of the inherited cap misses the fixed target; stronger caps or other controllers are outside this family.\n\n';
text+='Guard-only has zero startup caps and a long-run floor from arbitrary old history. Its separate single-immediate-cap variant additionally protects the activation average under the inherited condition. Cap frequency is not quote-change frequency or economic cost. Continuous calculations do not alter or recertify the earlier finite playable game.\n\n';
text+=`Retained inventory: ${targetRows.length} model/target groups, ${policyRows.length} policy slots (${summary.counts.duplicatePolicySlots} duplicates), ${reserveRows.length} fixed-level reserve rows, ${robustPeriodRows.length} robust-period comparisons. d=0 reproduces ${summary.counts.d0ClosedSelectionsReproduced}/80 closed selections; nominal/effective classification agreement holds in ${summary.counts.nominalEffectiveClassificationsAgree}/8 retained labels. All unresolved/censored statuses are saved rather than filtered.\n\n`;
text+=`Primary runtime ${Number(completion.resources.seconds).toFixed(3)} seconds; largest after-model RSS sample ${completion.resources.largestObservedRSSBytes} bytes, not a continuously measured peak. No new learner training, experimental seller/model API calls or paid inference services were used; Codex development assistance is separately disclosed.\n\n`;
text+='The independent audit uses separate alternative-demand, radius and selection logic with its frozen 130-digit backend. Both interval stacks share standard Decimal arithmetic; this is not formal verification or arithmetic-library independence. Only this bounded quality-shift family is studied: inaccurate enforcement, uncertain taste scale, other demand shapes, time-varying errors, empirical calibration and individually optimizing seller behavior remain unaddressed. Earlier archives and numerical evidence are preserved.\n';
fs.writeFileSync(file('research/misspec-results/summary.json'),JSON.stringify(summary)+'\n');
fs.writeFileSync(file('research/MODEL_MISSPEC_RESULTS.md'),text);
console.log(JSON.stringify({passed:true,models:16,targetGroups:80,policySlots:240,reserveRows:960,robustPeriodRows:320,
 summarySha256:sha('research/misspec-results/summary.json'),reportSha256:sha('research/MODEL_MISSPEC_RESULTS.md')}));
