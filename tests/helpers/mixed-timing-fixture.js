// Artificial in-memory fixture only; no numerical evidence files.
import assert from 'node:assert/strict';import crypto from 'node:crypto';
export const q=n=>({numerator:String(n),denominator:'1'}),clone=x=>JSON.parse(JSON.stringify(x));
const scenarios=['base-g15-t1','scale0.5-g15-t1','lower-quality-g15-t1','lowcost-g15-t1','base-g11-t1','base-g31-t1','base-g15-t0.5','base-g15-t2'];
const labels=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor'];
export const prefix='research/mixed-timing-results/';
export function fixture(change=()=>{},changeAudit=()=>{}){
 const files=new Map(),put=(name,value)=>files.set(name,Buffer.from(typeof value==='string'?value:JSON.stringify(value)+'\n'));
 const hash=name=>crypto.createHash('sha256').update(files.get(name)).digest('hex');
 for(const name of ['research/mixed-timing-analysis.js','research/mixed-timing-format.js','research/fake-primary.py','research/audit-mixed-study.py','research/audit-mixed-timing.js','research/audit-mixed-continuous.py','research/audit-continuous-study.py'])put(name,'ARTIFICIAL SOURCE '+name);
 const games=scenarios.map(id=>({scenario:{id},cap:{index:0,price:1},finite:{prices:[1,2],capIndex:0,sets:[[0,1],[0,1]],upper:[1,1],
  rewards:Object.fromEntries(['consumerSurplus','profitA','profitB','quantityA','quantityB'].map(k=>[k,[4,3,3,2]]))}}));
 const plans=scenarios.flatMap(scenario=>['finite','effective','nominal'].map(kind=>({id:scenario+'--'+kind,scenario,kind,labels,
  finiteFile:'research/sparse-display-results/cases/'+scenario+'.json',continuousFile:kind==='finite'?null:'research/artificial/'+scenario+'-'+kind+'.json'})));
 const records=plans.map(p=>({...clone(p),status:'completed timing certificate calculations',calculationFailures:0,envelope:{kind:p.kind},queriedSums:[],queryFailures:[],
  targets:labels.map((label,i)=>({id:p.id+'--'+label,scenario:p.scenario,kind:p.kind,label,actualThresholdExact:q(0),identity:{artificial:true},
   duplicateOf:i===0?null:p.id+'--'+labels[0],status:'certified startup-only zero limiting rate',
   frontier:{maxK:65536,bestFixedK:null,certifiedSafeK:null,safe:null,failing:null,queryLengths:[]},
   rates:{bestFixedK:null,fixedRateExact:null,optimumRateBoundsExact:{lower:q(0),upper:q(0)},constructedRateExact:q(0),exactOptimum:true},
   calendar:{kind:'startup-only',startupCaps:1,blockPreview64:[]},executionPreview:[]}))}));
 const context={records,games,completionPassed:null,finalDependenciesPassed:true,journalDrop:false};change(context);
 for(const game of games)put('research/sparse-display-results/cases/'+game.scenario.id+'.json',game);
 const finiteIndex={cases:scenarios.map(scenario=>({scenario,status:'completed',file:'cases/'+scenario+'.json',sha256:hash('research/sparse-display-results/cases/'+scenario+'.json')}))};
 put('research/sparse-display-results/index.json',finiteIndex);
 put('output/ARTIFICIAL-v9.zip','ARTIFICIAL OPTIONAL ARCHIVE');
 const delivery={archive:'output/ARTIFICIAL-v9.zip',sha256:hash('output/ARTIFICIAL-v9.zip'),verification:{passed:true,payloadHashesAndCRC:true}};put('output/adaptive-package-verification.json',delivery);
 const inputNames=['research/sparse-display-results/index.json','output/adaptive-package-verification.json',...scenarios.map(s=>'research/sparse-display-results/cases/'+s+'.json')];
 const manifest={sourceHashes:{'research/fake-primary.py':hash('research/fake-primary.py')},inputHashes:Object.fromEntries(inputNames.map(n=>[n,hash(n)])),
  v9Delivery:{receiptSha256:hash('output/adaptive-package-verification.json'),archiveSha256:delivery.sha256},
  plan:{modelCount:24,targetLabels:120,maxK:65536,displayPrecision:30,models:plans}};
 put(prefix+'sources/research/fake-primary.py',files.get('research/fake-primary.py').toString());put(prefix+'manifest.json',manifest);const mh=hash(prefix+'manifest.json');
 for(const record of records)put(prefix+'records/'+record.id+'.json',record);
 const index={manifestSha256:mh,records:records.map(r=>({id:r.id,file:'records/'+r.id+'.json',sha256:hash(prefix+'records/'+r.id+'.json'),status:r.status,targetLabels:r.targets.length}))};
 put(prefix+'results.json',{manifestSha256:mh,records});put(prefix+'index.json',index);
 const failures=records.reduce((a,r)=>a+r.calculationFailures,0);
 put(prefix+'completion.json',{manifestSha256:mh,models:24,targetLabels:120,passed:context.completionPassed??failures===0,calculationFailures:failures,
  resultsSha256:hash(prefix+'results.json'),indexSha256:hash(prefix+'index.json'),finalFrozenDependencyCheck:{passed:context.finalDependenciesPassed},resources:{newTrainingRounds:0,experimentalModelApiCalls:0}});
 put(prefix+'execution-start.json',{manifestSha256:mh});
 const journal=records.flatMap(r=>[{id:r.id,status:'started'},{id:r.id,status:r.status,calculationFailures:r.calculationFailures}]);if(context.journalDrop)journal.pop();put(prefix+'journal.jsonl',journal.map(r=>JSON.stringify(r)).join('\n')+'\n');
 const statusCounts={};for(const r of records)for(const t of r.targets)statusCounts[t.status]=(statusCounts[t.status]??0)+1;
 const audit={passed:true,requiresOrchestrator:false,continuousChecksComputedInProcess:true,auditorEntryPoint:'research/audit-mixed-study.py',
  studyManifestHash:mh,resultsSha256:hash(prefix+'results.json'),indexSha256:hash(prefix+'index.json'),completionSha256:hash(prefix+'completion.json'),journalSha256:hash(prefix+'journal.jsonl'),executionStartSha256:hash(prefix+'execution-start.json'),
  auditorSourceHash:hash('research/audit-mixed-study.py'),orchestratorSourceHash:hash('research/audit-mixed-study.py'),controlAuditorSourceHash:hash('research/audit-mixed-timing.js'),continuousAuditorSourceHash:hash('research/audit-mixed-continuous.py'),arithmeticBackendHash:hash('research/audit-continuous-study.py'),
  inheritedPremiseRevalidation:false,models:24,finiteModels:8,continuousModels:16,targetLabels:120,finiteTargetLabels:40,continuousTargetLabels:80,
  corruptionNegativeControls:{artificialRejection:true},primaryExecutionPassed:context.completionPassed??failures===0,calculationFailures:failures,statusCounts};changeAudit(audit);put(prefix+'independent-audit.json',audit);
 const reads=[];return {files,reads,io:{readBytes:name=>{reads.push(name);assert.ok(files.has(name),'Unexpected artificial file '+name);return files.get(name);},exists:()=>false}};
}
