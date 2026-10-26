import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {validateTask} from '../research/guard-reference-case.js';
import {scientificTreatment} from '../research/guard-reference-learning.js';
import {runtimeIdentity} from '../research/matched-clock-study.js';
import {save,sha} from '../research/matched-clock-io.js';
const record=()=>({finite:{prices:[1,2],capIndex:0,sets:[[0],[1]],rewards:{profitA:[-1,0,2,1],profitB:[2,-2,1,0],consumerSurplus:[9,7,8,6]}}});
const software=runtimeIdentity();
function task(){const r=record();return{executionMode:'artificial',scientificTreatment:scientificTreatment(),plan:{id:'artificial-reference',seed:907001,arm:'startup',treatment:'full-grid-after-cap',scientificTreatment:scientificTreatment(),actors:[[1,2,3,4],[5,6,7,8]]},T:20000,checkpoints:[10000,20000],record:r,finite:r.finite,software};}
test('artificial child task requires explicit treatment in both task and plan, original aliases and fixed clock',()=>{
 const t=task();assert.equal(validateTask(t,'.').node,software.node);
 for(const mutate of [t=>delete t.scientificTreatment,t=>t.plan.scientificTreatment.postInitialOriginalIndices='guard',t=>t.plan.treatment='startup-guard',t=>t.plan.arm='recurring4',t=>t.checkpoints=[0,20000],t=>t.finite=record()]){
  const bad=task();mutate(bad);assert.throws(()=>validateTask(bad,'.'));
 }
});
test('frozen task checks all invented source/input/snapshot maps and raw record bindings before learner allocation',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'guard-reference-task-')),project=path.join(temp,'project'),directory=path.join(temp,'study');
 try{
  const t=task();t.executionMode='frozen-primary';t.T=2000000;t.checkpoints=[1000000,2000000];t.projectRoot=project;
  const sourceHashes={},names=['guard-reference-case.js','guard-reference-learning.js','guard-reference-io.js','matched-clock-learning.js','matched-clock-graph.js','matched-clock-io.js'];
  for(const name of names){const relative='research/'+name,bytes=Buffer.from('// Wholly invented source identity '+name);sourceHashes[relative]=save(project,relative,bytes).sha256;save(directory,'sources/'+relative,bytes);}
  t.finiteGameRef=save(project,'artificial/physical.json',t.record);
  const m={sourceHashes,inputHashes:{[t.finiteGameRef.file]:t.finiteGameRef.sha256},runtime:software,inputs:{finiteGame:t.finiteGameRef},plan:{runs:[t.plan],scientificTreatment:scientificTreatment(),T:t.T,checkpoints:t.checkpoints,alpha:.1,gamma:19/20}};
  const write=()=>{const bytes=Buffer.from(JSON.stringify(m));fs.mkdirSync(directory,{recursive:true});fs.writeFileSync(path.join(directory,'manifest.json'),bytes);t.manifestSha256=sha(bytes);};
  write();validateTask(t,directory);
  fs.appendFileSync(path.join(project,'research/guard-reference-io.js'),'drift');assert.throws(()=>validateTask(t,directory),/live dependency/);
  fs.writeFileSync(path.join(project,'research/guard-reference-io.js'),fs.readFileSync(path.join(directory,'sources/research/guard-reference-io.js')));
  fs.appendFileSync(path.join(directory,'sources/research/guard-reference-case.js'),'snapshot drift');assert.throws(()=>validateTask(t,directory),/snapshot/);
  fs.writeFileSync(path.join(directory,'sources/research/guard-reference-case.js'),fs.readFileSync(path.join(project,'research/guard-reference-case.js')));
  t.record.finite.rewards.profitA[0]=99;t.finite=t.record.finite;assert.throws(()=>validateTask(t,directory),/original game/);
 }finally{const resolved=path.resolve(temp);assert.ok(resolved.startsWith(path.resolve(os.tmpdir())+path.sep)&&path.basename(resolved).startsWith('guard-reference-task-'));fs.rmSync(resolved,{recursive:true,force:true});}
});
