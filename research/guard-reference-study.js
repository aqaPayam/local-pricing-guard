// Prospective source/identity administration; import performs no IO or learning.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {plannedRuns as oldPlans,runtimeIdentity,runtimeFingerprint,sourceClosure} from './matched-clock-study.js';
import {sha,local} from './matched-clock-io.js';
import {scientificTreatment,FULL_GRID_TREATMENT} from './guard-reference-learning.js';
export const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const need=(v,m)=>{if(!v)throw Error(m);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export const OLD_MANIFEST='dcd573fc866e59cd1a27c3158cb9e9be58702034f9fb250e251c54f579a01817';
export const OLD_AUDIT='a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6';
export const SOURCE_FILES=[
 'research/GUARD_REFERENCE_PROTOCOL.md','research/GUARD_REFERENCE_ANALYSIS_CONTRACT.md','research/GUARD_REFERENCE_ROOT_REVIEW.md','research/GUARD_REFERENCE_PROSPECTIVE_REVIEW.md',
 'research/guard-reference-learning.js','research/guard-reference-io.js','research/guard-reference-case.js','research/guard-reference-study.js','research/run-guard-reference.py','research/benchmark-guard-reference.py',
 'research/guard-reference-analysis.py','research/guard-reference-baseline.py','research/audit-guard-reference.js','research/replay-guard-reference.js','research/audit-guard-reference-study.py',
 'tests/guard-reference-learning.test.js','tests/guard-reference-case.test.js','tests/guard-reference-study.test.js','tests/guard-reference-audit.test.js','tests/guard-reference-cross-audit.test.js','tests/guard-reference-serialization-audit.test.js',
 'tests/test_guard_reference_analysis.py','tests/test_guard_reference_case.py','tests/test_guard_reference_baseline.py','tests/test_guard_reference_replay_process.py','tests/test_guard_reference_supervisor.py','tests/test_guard_reference_benchmark.py','tests/test_guard_reference_cross_anchors.py','tests/test_guard_reference_inventory_audit.py'
];
export function plannedRuns(){return oldPlans().filter(p=>p.arm==='startup').map(p=>({...p,id:`base-g15-t1--full-grid-after-cap--zero--s${p.seed}`,treatment:FULL_GRID_TREATMENT,scientificTreatment:scientificTreatment()}));}
export function validateBaseline(baseline){
 need(baseline&&baseline.manifest?.sha256===OLD_MANIFEST&&baseline.audit?.sha256===OLD_AUDIT,'Fixed accepted old comparison required');
 need(baseline.finalEndpoints?.length===12&&baseline.finalEndpoints.every((e,i)=>e.seed===907001+i&&e.arm==='startup'&&e.available===true&&e.replayMatched===true&&e.step===2000000&&e.nextPhase===4&&e.runId===`base-g15-t1--matched5-startup--zero--s${e.seed}`),'All twelve authenticated old final endpoints required');
 need(baseline.inputHashes&&typeof baseline.inputHashes==='object'&&!Array.isArray(baseline.inputHashes)&&Object.keys(baseline.inputHashes).length>0,'Complete old input identity map required');
 need(baseline.inputHashes[baseline.finiteGame?.file]===baseline.finiteGame?.sha256,'Original physical record must be in old closure');
 for(const[name,h]of Object.entries(baseline.inputHashes)){local(ROOT,name);need(/^[a-f0-9]{64}$/.test(h),'Invalid old dependency hash');}
 return true;
}
export function inventory(baseline,{projectRoot=ROOT,sourceFiles=SOURCE_FILES,io=null}={}){
 validateBaseline(baseline);const readBytes=io?.readBytes??(n=>fs.readFileSync(local(projectRoot,n))),exists=io?.exists??(n=>fs.existsSync(local(projectRoot,n)));
 const sourceHashes=sourceClosure(sourceFiles,{readBytes,exists}),inputHashes={...baseline.inputHashes};
 for(const[name,h]of Object.entries(inputHashes))need(exists(name)&&sha(readBytes(name))===h,'Authenticated inherited dependency changed '+name);
 const bytes=readBytes(baseline.finiteGame.file);need(bytes.length===baseline.finiteGame.bytes,'Original finite length differs');
 const raw=JSON.parse(bytes);need(raw.scenario?.id==='base-g15-t1'&&raw.finite?.prices?.length===62,'Original physical62-price input required');
 return {sourceHashes,inputHashes,finiteGame:baseline.finiteGame,baseline:{manifest:baseline.manifest,audit:baseline.audit,summary:baseline.summary,builder:baseline.builder,finalEndpoints:baseline.finalEndpoints,scope:baseline.scope},runtime:runtimeIdentity(),runs:plannedRuns(),scientificTreatment:scientificTreatment()};
}
export function verify(directory,{projectRoot=ROOT,checkRuntime=true}={}){
 const m=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json')));
 for(const group of ['sourceHashes','inputHashes']){
  need(m[group]&&typeof m[group]==='object'&&!Array.isArray(m[group])&&Object.keys(m[group]).length>0,'Complete frozen hash map required');
  for(const[name,h]of Object.entries(m[group])){
   need(/^[a-f0-9]{64}$/.test(h)&&sha(fs.readFileSync(local(projectRoot,name)))===h,'Frozen live dependency changed '+name);
   if(group==='sourceHashes')need(sha(fs.readFileSync(local(directory,'sources/'+name)))===h,'Frozen snapshot changed '+name);
  }
 }
 need(same(m.plan.runs,plannedRuns())&&m.plan.retainedRuns===12&&m.plan.T===2000000&&same(m.plan.checkpoints,[1000000,2000000])&&m.plan.alpha===.1&&m.plan.gamma===19/20&&m.plan.initialization==='positive-zero','Exact fixed12-run learning matrix differs');
 need(same(m.plan.scientificTreatment,scientificTreatment()),'Explicit new support treatment differs');
 need(m.baseline?.manifest?.sha256===OLD_MANIFEST&&m.baseline?.audit?.sha256===OLD_AUDIT&&m.baseline.finalEndpoints?.length===12,'Fixed old comparison identity differs');
 need(m.inputHashes[m.inputs?.finiteGame?.file]===m.inputs?.finiteGame?.sha256,'Physical input absent from frozen closure');
 if(checkRuntime)need(same(runtimeFingerprint(m.runtime),runtimeFingerprint(runtimeIdentity())),'Frozen Node/V8 backend differs');
 return m;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const[mode,file]=process.argv.slice(2);
 if(mode==='plan')console.log(JSON.stringify(plannedRuns()));
 else if(mode==='runtime')console.log(JSON.stringify(runtimeIdentity()));
 else if(mode==='sources')console.log(JSON.stringify(sourceClosure(SOURCE_FILES,{readBytes:n=>fs.readFileSync(local(ROOT,n)),exists:n=>fs.existsSync(local(ROOT,n))})));
 else if(mode==='inventory'){need(file,'Explicit authenticated baseline JSON required; Python loader owns authentication');console.log(JSON.stringify(inventory(JSON.parse(fs.readFileSync(file==='-'?0:file)))));}
 else if(mode==='verify')console.log(JSON.stringify({passed:true,runs:verify(file).plan.runs.length}));
 else throw Error('Explicit source/plan/runtime/inventory/verify mode required; freeze/run are owned by the Python parent');
}
