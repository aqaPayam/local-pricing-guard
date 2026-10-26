import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {plannedRuns,validateBaseline,inventory,verify,OLD_MANIFEST,OLD_AUDIT} from '../research/guard-reference-study.js';
import {plannedRuns as oldRuns} from '../research/matched-clock-study.js';
import {scientificTreatment} from '../research/guard-reference-learning.js';
import {sha} from '../research/matched-clock-io.js';
function baseline(){return {manifest:{file:'old/manifest.json',sha256:OLD_MANIFEST},audit:{file:'old/audit.json',sha256:OLD_AUDIT},finalEndpoints:Array.from({length:12},(_,i)=>({seed:907001+i,arm:'startup',available:true,replayMatched:true,step:2000000,nextPhase:4,runId:`base-g15-t1--matched5-startup--zero--s${907001+i}`})),finiteGame:{file:'old/physical.json',sha256:'a'.repeat(64),bytes:1},inputHashes:{'old/physical.json':'a'.repeat(64)}};}
test('all twelve reference labels preserve accepted private actor namespaces with explicit changed support',()=>{
 const plans=plannedRuns(),old=oldRuns().filter(p=>p.arm==='startup');assert.equal(plans.length,12);
 for(let i=0;i<12;i++){assert.equal(plans[i].id,`base-g15-t1--full-grid-after-cap--zero--s${907001+i}`);assert.deepEqual(plans[i].actors,old[i].actors);assert.deepEqual(plans[i].segments,old[i].segments);assert.equal(plans[i].arm,'startup');assert.equal(plans[i].treatment,'full-grid-after-cap');assert.deepEqual(plans[i].scientificTreatment,scientificTreatment());}
});
test('administrative inventory validates every invented old byte identity and keeps original physical input',()=>{
 const files={'research/invented.js':Buffer.from('// invented source only'),'old/physical.json':Buffer.from(JSON.stringify({scenario:{id:'base-g15-t1'},finite:{prices:Array.from({length:62},(_,i)=>i)}}))};
 const b=baseline();b.finiteGame={file:'old/physical.json',bytes:files['old/physical.json'].length,sha256:sha(files['old/physical.json'])};b.inputHashes[b.finiteGame.file]=b.finiteGame.sha256;
 const io={readBytes:n=>files[n],exists:n=>Object.hasOwn(files,n)};const value=inventory(b,{sourceFiles:['research/invented.js'],io});assert.deepEqual(value.finiteGame,b.finiteGame);assert.equal(value.runs.length,12);
 files['old/physical.json']=Buffer.from('changed');assert.throws(()=>inventory(b,{sourceFiles:['research/invented.js'],io}),/dependency changed/);
 for(const modify of [b=>b.audit.sha256='0'.repeat(64),b=>b.finalEndpoints.pop(),b=>b.finalEndpoints[0].available=false,b=>b.finalEndpoints[1].seed=907001]){const bad=baseline();modify(bad);assert.throws(()=>validateBaseline(bad));}
});
test('source-only frozen verifier rejects support/plan/snapshot drift before any learner or anchor',()=>{
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'guard-reference-admin-')),project=path.join(directory,'project'),study=path.join(directory,'study');
 try{
  const file='research/invented.js',bytes=Buffer.from('// wholly invented');fs.mkdirSync(path.join(project,'research'),{recursive:true});fs.writeFileSync(path.join(project,file),bytes);fs.mkdirSync(path.join(study,'sources/research'),{recursive:true});fs.writeFileSync(path.join(study,'sources',file),bytes);
  const b=baseline(),m={sourceHashes:{[file]:sha(bytes)},inputHashes:{[file]:sha(bytes)},baseline:b,inputs:{finiteGame:{file,sha256:sha(bytes)}},plan:{runs:plannedRuns(),retainedRuns:12,T:2000000,checkpoints:[1000000,2000000],alpha:.1,gamma:19/20,initialization:'positive-zero',scientificTreatment:scientificTreatment()}};
  const write=()=>fs.writeFileSync(path.join(study,'manifest.json'),JSON.stringify(m));write();assert.equal(verify(study,{projectRoot:project,checkRuntime:false}).plan.runs.length,12);
  m.plan.scientificTreatment.supportMode='startup-guard';write();assert.throws(()=>verify(study,{projectRoot:project,checkRuntime:false}),/support treatment/);m.plan.scientificTreatment=scientificTreatment();write();fs.appendFileSync(path.join(study,'sources',file),' drift');assert.throws(()=>verify(study,{projectRoot:project,checkRuntime:false}),/snapshot/);
 }finally{assert.ok(path.resolve(directory).startsWith(path.resolve(os.tmpdir())+path.sep));fs.rmSync(directory,{recursive:true,force:true});}
});
