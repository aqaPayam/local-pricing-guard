// Descriptive, hash-gated export of reviewed continuous and finite controllers.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const file=name=>path.join(ROOT,name),bytes=name=>fs.readFileSync(file(name));
const read=name=>JSON.parse(bytes(name)),sha=name=>crypto.createHash('sha256').update(bytes(name)).digest('hex');
const insist=(ok,message)=>{if(!ok)throw Error(message);};
const inputHashes={};
function use(name){inputHashes[name]=sha(name);return read(name);}
function manifest(name){const value=use(name),folder=path.posix.dirname(name);
 for(const field of ['sourceHashes','inputHashes'])for(const [dependency,hash]of Object.entries(value[field]??{})){
  insist(sha(dependency)===hash,'Frozen dependency drift '+dependency);inputHashes[dependency]=hash;
  const snapshot=folder+'/sources/'+dependency;
  if(field==='sourceHashes'&&fs.existsSync(file(snapshot))){insist(sha(snapshot)===hash,'Source snapshot drift '+snapshot);inputHashes[snapshot]=hash;}
 }
 return value;
}
function audit(name,manifestName,resultName,resultField,source){const value=use(name);
 insist(value.passed===true,'Independent audit has not passed '+name);
 insist(value.studyManifestHash===sha(manifestName)&&value[resultField]===sha(resultName),'Independent audit result/manifest binding differs '+name);
 insist(value.auditorSourceHash===sha(source),'Independent auditor source binding differs '+name);inputHashes[source]=sha(source);
 insist(Object.keys(value.corruptionNegativeControls??{}).length>0&&Object.values(value.corruptionNegativeControls).every(Boolean),'Corruption controls missing/failed '+name);
 return value;
}
const primaryManifest='research/recurring-results/manifest.json',primaryResults='research/recurring-results/results.json';
const finiteManifest='research/sparse-display-results/manifest.json',finiteIndex='research/sparse-display-results/index.json';
const pm=manifest(primaryManifest),fm=manifest(finiteManifest),results=use(primaryResults),index=use(finiteIndex);
const pc=use('research/recurring-results/completion.json'),fc=use('research/sparse-display-results/completion.json');
insist(results.manifestSha256===sha(primaryManifest)&&pc.resultsSha256===sha(primaryResults)&&pc.finalFrozenDependencyCheck?.passed===true,'Continuous controller completion binding failed');
insist(index.manifestSha256===sha(finiteManifest)&&fc.passed===true&&fc.finalHashCheck===true,'Finite controller completion binding failed');
const pa=audit('research/recurring-results/independent-audit.json',primaryManifest,primaryResults,'resultsSha256','research/audit-sparse-reset.py');
const fa=audit('research/sparse-display-results/independent-audit.json',finiteManifest,finiteIndex,'indexSha256','research/audit-sparse-display.js');
const ra=audit('research/sparse-display-results/rational-audit.json',finiteManifest,finiteIndex,'indexSha256','research/audit-sparse-reset.py');
insist(pa.arithmeticBackendHash===sha('research/audit-continuous-study.py'),'Independent inherited arithmetic-backend binding failed');
inputHashes['research/audit-continuous-study.py']=sha('research/audit-continuous-study.py');
insist(results.records.length===16&&index.cases.length===8,'Declared record inventory differs');
const rows=[],targetRows=[],frontierRows=[],finiteRows=[];
for(const scenario of pm.plan.scenarios){
 const row={scenario:scenario.id,economy:scenario.economy,originalGridSize:scenario.gridSize,epsilon:scenario.epsilon,toleranceFactor:scenario.toleranceFactor};
 for(const kind of pm.plan.continuums){
  const selected=results.records.filter(r=>r.scenario===scenario.id&&r.continuum===kind);insist(selected.length===1,'Missing/duplicate model '+scenario.id+'/'+kind);
  const current=selected[0],recordName=`research/recurring-results/records/${scenario.id}-${kind}.json`,journal=use(recordName);
  insist(JSON.stringify(journal)===JSON.stringify(current),'Primary per-record journal differs '+recordName);
  insist(current.comparisons.length===5&&pm.plan.targetLabels.every(label=>current.comparisons.some(c=>c.label===label)),'Five target labels not retained '+recordName);
  const compact={status:current.status,sourceRecord:recordName,sourceRecordSha256:sha(recordName),physicalCap:current.physicalCap??null,
   normalizedCapExact:current.normalizedCapExact??null,conditions:current.conditions??null,inheritedContinuum:current.inheritedContinuum??null,
   frontier:current.frontier??[],comparisons:current.comparisons,aJ:current.aJ??null,qStarMinusAJ:current.qStarMinusAJ??null,
   orbitRewards:(current.orbit??[]).map(step=>({j:step.j,executedPrice:step.executedPrice,consumerSurplus:step.consumerSurplus,
     profitPerSellerOnWorstCSPath:step.profitPerSellerOnWorstCSPath})),failure:current.failure??null,seconds:current.seconds};
  row[kind]=compact;
  for(const target of compact.comparisons)targetRows.push({scenario:scenario.id,continuum:kind,physicalCap:compact.physicalCap,...target});
  for(const period of compact.frontier)frontierRows.push({scenario:scenario.id,continuum:kind,physicalCap:compact.physicalCap,...period});
 }
 row.physicalCap=row.effective.physicalCap;
 insist(JSON.stringify(row.effective.physicalCap)===JSON.stringify(row.nominal.physicalCap),'Nominal/effective cap identity differs');
 const classify=r=>r.comparisons.map(c=>[c.label,c.status??c.classification,c.largestPeriod??null,c.certifiedSafePeriodLowerBound??null,c.certifiedFailingPeriodUpperBound??null]);
 row.nominalEffectiveAgreement=JSON.stringify(classify(row.effective))===JSON.stringify(classify(row.nominal));
 const entries=index.cases.filter(c=>c.scenario===scenario.id);insist(entries.length===1,'Missing/duplicate finite game '+scenario.id);
 const entry=entries[0],name='research/sparse-display-results/'+entry.file;
 insist(sha(name)===entry.sha256,'Finite case/index hash differs '+name);const finite=use(name);
 insist(JSON.stringify(finite.scenario)===JSON.stringify(scenario),'Finite scenario/economy identity differs '+name);
 if(row.physicalCap)insist(finite.cap.price===Number(row.physicalCap.physicalPriceImported.serialized)&&finite.cap.originalIndex===row.physicalCap.oldIndex,'Continuous/finite original physical cap differs '+name);
 row.finite={file:name,sha256:entry.sha256,status:entry.status,quotes:finite.finite.prices.length,cap:finite.cap,
  originalTargets:finite.originalTargets,certificates:finite.finite.certificates,
  tableCoordinateMonotone:finite.finite.tableCoordinateMonotone,upperMapMonotone:finite.finite.upperMapMonotone,
  capOrbitNondecreasing:finite.finite.capOrbitNondecreasing,scope:finite.scope};
 for(const certificate of finite.finite.certificates)finiteRows.push({scenario:scenario.id,quotes:row.finite.quotes,cap:finite.cap,...certificate});
 rows.push(row);
}
insist(rows.length===8&&targetRows.length===80,'Complete eight-label/80-target matrix differs');
const countsByStatus={};for(const target of targetRows){const status=target.status??target.classification;countsByStatus[status]=(countsByStatus[status]??0)+1;}
const aggregate=[];
for(const continuum of pm.plan.continuums)for(const label of pm.plan.targetLabels){
 const selected=targetRows.filter(r=>r.continuum===continuum&&r.label===label);
 aggregate.push({continuum,label,targets:selected.length,noRecurringCapNeeded:selected.filter(r=>r.status==='no recurring cap needed for the long-run target').length,
  exactLargestPeriods:selected.filter(r=>r.status==='largest certified fixed period').map(r=>({scenario:r.scenario,period:r.largestPeriod})),
  familyInfeasible:selected.filter(r=>r.status==='infeasible for this fixed-cap family').length,
  retainedOtherStatuses:selected.filter(r=>!['no recurring cap needed for the long-run target','largest certified fixed period','infeasible for this fixed-cap family'].includes(r.status)).map(r=>({scenario:r.scenario,status:r.status??r.classification}))});
}
const compactAudit=a=>Object.fromEntries(Object.entries(a).filter(([key])=>key!=='details'));
const summary={kind:'Descriptive export only; no new controller optimization, targets, training or seller model calls',analysisSourceHash:sha('research/recurring-analysis.js'),
 inputHashes,counts:{scenarios:rows.length,continuousModels:results.records.length,targetLabels:targetRows.length,
  continuousResolved:pc.resolved,continuousUnresolved:pc.unresolved,fixedFrontierRows:frontierRows.length,
  finiteGames:index.cases.length,finiteCertificates:finiteRows.length,finiteFailures:fc.failures,
  nominalEffectiveAgreement:rows.filter(r=>r.nominalEffectiveAgreement).length,targetStatuses:countsByStatus},
 rows,targetRows,frontierRows,finiteRows,aggregate,audits:{continuous:compactAudit(pa),finite:compactAudit(fa),finiteRational:compactAudit(ra)},
 resources:{continuous:pc.resources,finite:fc},
 scope:'Same original physical cap within each retained label, different timing. Original cap prices and targets can differ across grid-size labels even when their unchanged-guard continuum agrees. Largest periods are optimal only within this fixed-cap fixed-period family. Continuous interval proofs and exact rational saved-weight finite-game certificates have distinct models. No incentive stability, human validation or general controller optimum is inferred.'};
const approx=x=>x===undefined||x===null?'unresolved':Number(x).toFixed(6);
const selected=(row,label)=>{const t=row.effective.comparisons.find(c=>c.label===label);return t.status==='no recurring cap needed for the long-run target'?'none needed':t.status==='largest certified fixed period'?String(t.largestPeriod):t.status??t.classification;};
let text='# Recurring the same inherited physical cap\n\n';
text+='All three independent controller audits passed with exact source/manifest/result/index bindings. This export rechecks every frozen dependency, all 16 primary journals and eight finite-game case hashes. It adds no controller cases or optimization.\n\n';
text+='The ongoing controller applies an actual inherited cap immediately and once every K executions; the original profit guard applies on the other K-1 executions. The cap replaces that guard on cap rounds. A public phase clock and recurring restriction are new ongoing control, rather than a one-time initializer.\n\n';
text+='## All eight primary model labels\n\n';
text+='The effective exact-real tolerance is primary; nominal sensitivity is retained separately. A finite K below is certified safe with K+1 certified failing for the same old actual F-delta threshold. “None needed” concerns the long-run target: untouched guard and one immediate cap have different finite-startup guarantees. Cap prices are displayed approximately; exact imported prices remain in the raw records and summary.\n\n';
text+='| Scenario | Original physical cap | Continuous Nash price | 90% old cap target | 95% target | 99% target | 100% target | Near-Nash anchor |\n|---|---:|---:|---|---:|---:|---:|---:|\n';
for(const row of rows)text+=`| ${row.scenario} | ${approx(row.physicalCap?.physicalPriceImported.exactDecimal)} | ${approx(row.effective.inheritedContinuum?.nash.price.lower)} | ${selected(row,'cap-90pct')} | ${selected(row,'cap-95pct')} | ${selected(row,'cap-99pct')} | ${selected(row,'cap-100pct')} | ${selected(row,'near-Nash-anchor-floor')} |\n`;
text+='\nInterpreting a period: K=4 applies the cap rule on one of every four executions. This is not the fraction of quotes actually changed, a general autonomy measure or an economic cost. Permanent-cap K=1 is retained whenever strong targets require it. Larger K is called maximal only within this exact physical-cap and fixed-integer-period family.\n\n';
text+='The three base grid-size labels share an unchanged-guard continuum, but can inherit different cap prices AND old targets. Cross-label differences in K therefore cannot be attributed solely to action resolution or treated as a uniform intervention comparison. No cap was silently moved to continuous Nash. Equivalent calibrations and repeated labels remain disclosed rather than counted as independent economic replications.\n\n';
text+=`All ${summary.counts.nominalEffectiveAgreement}/8 labels have matching nominal/effective target statuses and period boundaries. Across both models, every one of the 80 original requested/actual target labels remains visible, including ${countsByStatus['no recurring cap needed for the long-run target']??0} already-met long-run targets. Full safe/next-failing enclosures, retained uncertainty/censoring, all 128 fixed-frontier records and 64-term orbit receipts are linked from the summary.\n\n`;
text+='## What the guarantees mean\n\n';
text+='Under the validated A<q_star and inherited monotonicity/contraction assumptions, the maximum-allowed-price policy attains the smallest customer reward at every phase. Its descending cycle rewards give both the long-run average floor G_K and a floor G_K for EVERY average measured from immediate cap activation. The worst individual round is separately saved and can lie below G_K. An arbitrary initial phase has only the long-run conclusion unless its preceding partial cycle is separately bounded.\n\n';
text+='If the old target is already at or below C_star, zero recurring activations suffice for the long-run target. Doing nothing has zero startup caps; one real immediate cap has one startup cap and additionally gives the stated finite-activation-average floor. These policies are not merged. Infeasibility or censoring, if encountered, applies only to the declared family/search and cannot rule out other persistent controllers.\n\n';
text+='The 64 explicit reward terms and a64 are followed by an analytic geometric-tail enclosure, not invented simulated rewards. Each uncertain rival interval is mapped using two separately signed scalar endpoint roots. Saved seller profits describe the CS-worst path; they are not profit guarantees, joint-profit optima or repeated-game incentive tests.\n\n';
text+='## Separately certified finite human game\n\n';
text+='Each game adds the exact inherited physical cap to its original 61-mesh quotes, with the declared near-duplicate cap-priority rule. Its saved numerical guard masks, full payoff table and actual quote count are independently checked. Exact rational arithmetic certifies means and minimum prefix averages of the STORED binary64 reward weights. This does not make the saved weights exact-real logit transcendental values or transfer the continuous result by analogy.\n\n';
text+='| Scenario | Actual quotes | Actual cap index | Period certificates | Upper map monotone | Cap orbit nondecreasing |\n|---|---:|---:|---:|---|---|\n';
for(const row of rows)text+=`| ${row.scenario} | ${row.finite.quotes} | ${row.finite.cap.index} | ${row.finite.certificates.length} | ${row.finite.upperMapMonotone} | ${row.finite.capOrbitNondecreasing} |\n`;
text+='\n## Evidence, resources and limits\n\n';
text+=`Primary models: ${pc.resolved} resolved, ${pc.unresolved} unresolved; ${pc.targetLabels} target labels; runtime ${pc.resources.seconds.toFixed(3)} seconds; largest after-record RSS sample ${pc.resources.largestObservedRSSBytes} bytes. Finite builder: ${fc.cases} cases, ${fc.failures} failures; runtime ${Number(fc.seconds).toFixed(3)} seconds; largest after-case RSS sample ${fc.largestObservedRSSBytes} bytes. These are not continuously measured memory peaks. No training, model players, APIs or purchases were used.\n\n`;
text+='The independent controller audit reuses its closed 130-digit backend, separately from the primary controller. Both share standard Decimal arithmetic; this is not a formally verified or arithmetic-library-independent proof. The finite JS audit and separate Fraction audit check the saved masks/weights and phase/prefix semantics. Exact counts and corruption controls are retained verbatim in the summary. All earlier evidence and delivery archives remain preserved.\n';
fs.writeFileSync(file('research/recurring-results/summary.json'),JSON.stringify(summary)+'\n');
fs.writeFileSync(file('research/RECURRING_RESULTS.md'),text);
console.log(JSON.stringify({passed:true,continuousModels:16,targetLabels:80,frontierRows:frontierRows.length,finiteGames:8,finiteCertificates:finiteRows.length,
 summarySha256:sha('research/recurring-results/summary.json'),reportSha256:sha('research/RECURRING_RESULTS.md')}));
