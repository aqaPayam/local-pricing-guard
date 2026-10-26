// Descriptive export only. It refuses unchecked/mismatched primary evidence.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const file=name=>path.join(ROOT,name);
const bytes=name=>fs.readFileSync(file(name));
const read=name=>JSON.parse(bytes(name));
const sha=name=>crypto.createHash('sha256').update(bytes(name)).digest('hex');
const assert=(condition,message)=>{if(!condition)throw new Error(message);};
const inputHashes={};
function use(name){inputHashes[name]=sha(name);return read(name);}
function linkedManifest(name){
  const manifest=use(name),folder=path.posix.dirname(name);
  for(const field of ['sourceHashes','inputHashes'])for(const [dependency,hash] of Object.entries(manifest[field]??{})){
    assert(sha(dependency)===hash,`Frozen ${field} dependency drift: ${dependency}`);
    inputHashes[dependency]=hash;
    if(field==='sourceHashes'){
      const snapshot=`${folder}/sources/${dependency}`;
      if(fs.existsSync(file(snapshot))){
        assert(sha(snapshot)===hash,`Frozen source snapshot drift: ${snapshot}`);
        inputHashes[snapshot]=hash;
      }else assert(folder!=='research/continuous-results',`Required continuous source snapshot missing: ${snapshot}`);
    }
  }
  return manifest;
}
function acceptedAudit(name,manifestName,linkedName,field,auditorSource){
  const audit=use(name);
  assert(audit.passed===true,`Independent audit has not passed: ${name}`);
  assert(audit.studyManifestHash===sha(manifestName),`Audit manifest link differs: ${name}`);
  assert(audit[field]===sha(linkedName),`Audit result/index link differs: ${name}`);
  assert(audit.auditorSourceHash===sha(auditorSource),`Independent auditor source link differs: ${name}`);
  inputHashes[auditorSource]=sha(auditorSource);
  assert(Object.keys(audit.corruptionNegativeControls??{}).length>0&&Object.values(audit.corruptionNegativeControls).every(Boolean),`Audit negative controls missing/failed: ${name}`);
  return audit;
}
const continuousManifestName='research/continuous-results/manifest.json';
const meshManifestName='research/mesh-results/manifest.json';
const cm=linkedManifest(continuousManifestName),mm=linkedManifest(meshManifestName);
const continuous=use('research/continuous-results/results.json');
const completion=use('research/continuous-results/completion.json');
assert(continuous.manifestSha256===sha(continuousManifestName),'Continuous result manifest link differs');
assert(completion.resultsSha256===sha('research/continuous-results/results.json'),'Continuous completion result link differs');
assert(completion.finalFrozenDependencyCheck?.passed===true,'Continuous end dependency check did not pass');
const index=use('research/mesh-results/index.json'),meshCompletion=use('research/mesh-results/completion.json');
assert(index.manifestSha256===sha(meshManifestName),'Mesh index manifest link differs');
assert(meshCompletion.passed===true&&meshCompletion.sourceHashesRechecked===true,'Mesh completion/dependency check did not pass');
const ca=acceptedAudit('research/continuous-results/independent-audit.json',continuousManifestName,'research/continuous-results/results.json','resultsSha256','research/audit-continuous-study.py');
const ma=acceptedAudit('research/mesh-results/independent-audit.json',meshManifestName,'research/mesh-results/index.json','indexSha256','research/audit-mesh-refinement.js');
assert(continuous.records.length===cm.plan.records&&index.cases.length===72,'Declared record inventories differ');
const labels=cm.plan.targetLabels;
const continuums=cm.plan.continuums;
const rows=[];const meshRows=[];
for(const scenario of cm.plan.scenarios){
  const row={scenario:scenario.id,economy:scenario.economy,originalGridSize:scenario.gridSize,
    epsilon:scenario.epsilon,toleranceFactor:scenario.toleranceFactor};
  for(const kind of continuums){
    const records=continuous.records.filter(r=>r.scenario===scenario.id&&r.continuum===kind);
    assert(records.length===1,`Missing/duplicate continuum ${scenario.id}/${kind}`);
    const record=records[0];
    const journal=use(`research/continuous-results/records/${scenario.id}-${kind}.json`);
    assert(JSON.stringify(journal)===JSON.stringify(record),`Continuous journal/result mismatch ${scenario.id}/${kind}`);
    assert(record.comparisons.length===5&&new Set(record.comparisons.map(r=>r.label)).size===5&&labels.every(label=>record.comparisons.some(r=>r.label===label)),`Retained comparison labels differ ${scenario.id}/${kind}`);
    row[kind]=record;
  }
  row.nominalEffectiveClassificationsAgree=labels.every(label=>row.effective.comparisons.find(v=>v.label===label).classification===row.nominal.comparisons.find(v=>v.label===label).classification);
  row.meshCases=[];
  for(const item of index.cases.filter(v=>v.scenario===scenario.id)){
    const name=`research/mesh-results/${item.file}`;
    assert(sha(name)===item.sha256,`Mesh case hash differs: ${name}`);
    const current=use(name);
    assert(current.scenario===scenario.id&&current.n===item.n&&JSON.stringify(current.economy)===JSON.stringify(scenario.economy)&&current.epsilon===scenario.epsilon,`Mesh case identity differs ${name}`);
    const compact={scenario:scenario.id,n:item.n,file:name,sha256:item.sha256,status:current.status,
      fixedPoints:current.destinations?.fixedPoints??null,fixedPointCount:current.destinations?.fixedPoints?.length??null,
      monotone:current.map?.monotone??false,declaredEndpointPrices:current.declaredEndpointPrices,
      actualEndpointPrices:current.actualEndpointPrices,spacing:current.spacing,
      welfare:current.welfare??null,targets:current.targets??[],ownPermanentCapFloor:current.ownPermanentCapFloor,
      inheritedComparisons:current.inheritedComparisons??[],numericScope:current.numericScope};
    row.meshCases.push(compact);meshRows.push(compact);
  }
  assert(row.meshCases.length===9,`Expected nine retained mesh diagnostics for ${scenario.id}`);
  rows.push(row);
}
assert(rows.length===8&&meshRows.length===72,'Complete scenario/mesh counts differ');
const comparisonsByLabel=[];
for(const kind of continuums)for(const label of labels){
  const values=rows.map(r=>r[kind].comparisons.find(v=>v.label===label));
  comparisonsByLabel.push({continuum:kind,label,total:values.length,
    alreadyGuaranteed:values.filter(v=>v.classification==='already guaranteed').length,
    allStartFailingContinuation:values.filter(v=>v.classification==='all-start failing continuation').length,
    unresolved:values.filter(v=>v.classification==='unresolved').length});
}
const auditCompact=a=>({passed:a.passed,checks:a.checks,records:a.records,cases:a.cases,
  resolved:a.resolved,comparisonCount:a.comparisonCount,payoffPairsScanned:a.payoffPairsScanned,
  pairTailValuesChecked:a.pairTailValuesChecked,inheritedComparisons:a.inheritedComparisons,
  nearFloatingBoundaries:a.nearFloatingBoundaries,corruptionNegativeControls:a.corruptionNegativeControls,
  scope:a.scope});
const summary={kind:'Post-run descriptive analysis of independently audited, separately frozen continuous and finite-mesh evidence; no new optimization',
  analysisSourceHash:sha('research/refinement-analysis.js'),inputHashes,
  counts:{scenarioLabels:rows.length,continuousRecords:continuous.records.length,meshRecords:meshRows.length,
    continuousResolved:completion.resolved,continuousUnresolved:completion.unresolved,
    meshFailures:meshCompletion.failures,meshUnresolved:meshCompletion.unresolved,
    monotoneMeshMaps:meshRows.filter(r=>r.monotone).length,
    nominalEffectiveClassificationsAgree:rows.filter(r=>r.nominalEffectiveClassificationsAgree).length},
  comparisonsByLabel,rows,meshRows,
  audits:{continuous:auditCompact(ca),mesh:auditCompact(ma)},
  resources:{continuous:completion.resources,mesh:meshCompletion},
  scope:'Eight retained labels are four calibrations with three dimensionless shapes, including grid-size/tolerance variants. Continuous conclusions use the reviewed sufficient theorem and exact-real comparison model; mesh results are binary64 diagnostics. No finite-grid error constant, unique basin at every grid, learned collusion, repeated-game incentive stability or external validation is inferred.'};
const approx=value=>value===undefined||value===null?'unresolved':Number(value).toFixed(6);
let text='# Continuous and mesh refinement results\n\n';
text+='Both independent audits passed and link to the exact frozen manifests and current result/index hashes. This export also verifies every source/input hash, every mesh case hash and every continuous journal record. The full enclosures and all target labels remain in `mesh-results/summary.json`; no new scenarios or optimization are introduced here.\n\n';
text+='The finite initializer guarantees remain valid on their original grids. In the declared continuous comparison, the validated upper-choice map has one attracting fixed point and the same worst long-run surplus from every initial price pair. A finite initializer cannot remove a below-target continuation once that unchanged continuous guard resumes. This is a conditional mathematical capacity result; it does not say sellers learn or prefer this policy.\n\n';
text+='## Complete continuous table\n\n';
text+='The primary effective tolerance is the exact real sum of imported binary64 epsilon and the imported binary64 `1e-12` allowance. Nominal epsilon is separately retained. The displayed numbers below are approximations; actual interval endpoints and signed root evidence are saved as decimal strings.\n\n';
text+='| Retained scenario | Continuous Nash CS | Continuous worst CS | Nash minus worst CS | Stationary profit per seller | 95% old cap | Near-Nash anchor |\n|---|---:|---:|---:|---:|---|---|\n';
for(const row of rows){const r=row.effective;const classification=label=>r.comparisons.find(v=>v.label===label)?.classification??'unresolved';text+=`| ${row.scenario} | ${approx(r.nash?.consumerSurplus.lower)} | ${approx(r.worst?.consumerSurplus.lower)} | ${approx(r.nashToWorstSurplusGap?.lower)} | ${approx(r.worst?.profitA.lower)} | ${classification('cap-95pct')} | ${classification('near-Nash-anchor-floor')} |\n`;}
text+='\n';
for(const kind of continuums){text+=`For ${kind} tolerance: `+comparisonsByLabel.filter(r=>r.continuum===kind).map(r=>`${r.label}: ${r.alreadyGuaranteed}/8 already guaranteed, ${r.allStartFailingContinuation}/8 all-start failing continuation, ${r.unresolved}/8 unresolved`).join('; ')+'.\n\n';}
text+=`Nominal/effective classifications agree in ${summary.counts.nominalEffectiveClassificationsAgree}/8 retained labels. Requested targets and actual relaxed thresholds remain separate. Failure means a permitted continuation below the threshold is available from every initial state; it is not a prediction that all seller behavior fails. “Already guaranteed” means no initializer is needed for that threshold in this comparison model.\n\n`;
text+='## All predeclared mesh diagnostics\n\n';
text+='Each row uses the same saved endpoints, with a new grid benchmark for best profit and binary64 interpolation. Its own permanent-cap floor is distinct from the fixed old targets. “Cap tail” is the worst top-choice continuation after one actual new-grid cap execution. All values here are numerical diagnostics, not validated real intervals or proof that the largest grid equals the limit.\n\n';
text+='| Scenario | Grid | Fixed points | Minimum across starts | Maximum across starts | Spread | One-round cap tail | Own cap floor |\n|---|---:|---:|---:|---:|---:|---:|---:|\n';
for(const r of meshRows)text+=`| ${r.scenario} | ${r.n} | ${r.fixedPointCount??'unresolved'} | ${approx(r.welfare?.minimumAcrossStartingStates)} | ${approx(r.welfare?.maximumAcrossStartingStates)} | ${approx(r.welfare?.spread)} | ${approx(r.welfare?.oneRoundCapWorst)} | ${approx(r.ownPermanentCapFloor)} |\n`;
text+='\nAll 72 labels, including every coarse-grid fluctuation, remain visible. A sampled downward trend does not establish monotonic mesh convergence. The conditional theorem gives the continuous conclusion; no explicit numerical width/slope constant or mesh error rate is claimed.\n\n';
text+='## Validation, resources and limits\n\n';
text+=`Continuous records: ${completion.resolved} certified, ${completion.unresolved} unresolved; runtime ${completion.resources.seconds.toFixed(3)} seconds; largest after-record RSS sample ${completion.resources.largestObservedRSSBytes} bytes. Mesh records: ${meshCompletion.cases}, ${meshCompletion.failures} failures, ${meshCompletion.unresolved} unresolved; runtime ${Number(meshCompletion.seconds).toFixed(3)} seconds; largest observed RSS sample ${meshCompletion.largestObservedRSSBytes} bytes. Neither memory figure is a continuously measured peak. No training, model game players, APIs or paid services were used.\n\n`;
text+='The continuous audit uses a separate calculation kernel and rechecks root signs, sufficient conditions, welfare/target enclosures and corruption controls. Both continuous implementations share the standard Decimal backend: independent calculation code does not provide independence from that arithmetic library or a formally verified proof. The mesh audit independently scans all predeclared price-profit pairs and tail data, including inherited graph matches and corruption controls. Exact audit counts, scope and source/result links are retained in the summary and original certificates.\n\n';
text+='The stationary unilateral deviation gain is a one-period payoff quantity. It does not establish repeated-game incentive compatibility or policy stability. These known symmetric deterministic logit calibrations provide sensitivity checks, with equivalent calibrations and repeated grid labels disclosed; they are not independent real-market replications. Earlier finite certificates and delivery archives are preserved.\n';
fs.writeFileSync(file('research/mesh-results/summary.json'),JSON.stringify(summary)+'\n');
fs.writeFileSync(file('research/REFINEMENT_RESULTS.md'),text);
console.log(JSON.stringify({passed:true,scenarioLabels:rows.length,continuousRecords:continuous.records.length,meshRecords:meshRows.length,summarySha256:sha('research/mesh-results/summary.json'),reportSha256:sha('research/REFINEMENT_RESULTS.md')}));
