// Invented serialized evidence only; no inherited data or Q access.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import zlib from 'node:zlib';import {createHash} from 'node:crypto';
import {createGuardReferenceLearners,evaluateGuardReference,summarizeGuardReferenceWindows,scientificTreatment} from '../research/guard-reference-learning.js';
import {advanceTo} from '../research/matched-clock-learning.js';
import {writeReferenceCheckpoint} from '../research/guard-reference-io.js';
import {replayAndCheck} from '../research/replay-guard-reference.js';
const sha=b=>createHash('sha256').update(b).digest('hex');
const bytes=x=>Buffer.from(JSON.stringify(x,null,2)+'\n');
function withFixture(fn){
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'reference-serialized-invented-'));
 try{
  const record={scenario:{id:'invented-not-a-market'},originalTargets:[],finite:{prices:[1,2,3],capIndex:1,sets:[[0],[1],[1]],rewards:{profitA:[-2,0,1,3,-1,2,0,1,0],profitB:[1,-3,0,0,2,-1,4,0,1],consumerSurplus:[9,8,7,8,6,5,7,5,3]}}};
  const m=createGuardReferenceLearners(record,{T:20000,seed:907001}),id='invented-full-grid-reference',initial=m.actors.map(s=>s.slice());
  const finiteGameRef={file:'invented-physical.json',bytes:bytes(record).length,sha256:sha(bytes(record))};
  const plan={id,arm:'startup',seed:907001,treatment:'full-grid-after-cap',scientificTreatment:scientificTreatment(),actors:initial};
  const task={plan,record,finite:record.finite,finiteGameRef,originalTargets:[],software:{scope:'invented-only'},scientificTreatment:scientificTreatment(),T:20000,checkpoints:[10000,20000]};
  const run={...plan,checkpoints:[]};
  for(const end of task.checkpoints){advanceTo(m,end);const metadata=writeReferenceCheckpoint(directory,m,{id,software:task.software,finiteGameRef,graph:evaluateGuardReference(m),windowMetrics:summarizeGuardReferenceWindows(m)});run.checkpoints.push({step:end,parentEligible:true,metadata});}
  fn({directory,task,run});
 }finally{
  const resolved=path.resolve(directory),base=path.resolve(os.tmpdir());assert.ok(resolved.startsWith(base+path.sep)&&path.basename(resolved).startsWith('reference-serialized-invented-'));fs.rmSync(resolved,{recursive:true,force:true});
 }
}
function rewrite(directory,ref,data){const b=Buffer.isBuffer(data)?data:bytes(data);fs.writeFileSync(path.join(directory,ref.file),b);ref.bytes=b.length;ref.sha256=sha(b);}
function changedCheckpoint(fixture,change){
 const slot=fixture.run.checkpoints[0],meta=JSON.parse(fs.readFileSync(path.join(fixture.directory,slot.metadata.file)));
 change(meta,fixture.directory);rewrite(fixture.directory,slot.metadata,meta);
}

test('complete original-ref serialization matches all independent effective-support claims and round blocks',()=>withFixture(({directory,task,run})=>{
 const result=replayAndCheck(task,run,directory);
 assert.equal(result.fullHorizonReplayed,true);assert.equal(result.allPlannedCheckpointsMatched,true);assert.equal(result.replayedRounds,20000);assert.equal(result.transcriptBlocksMatched,2);
 assert.equal(result.finalConsumedIntegrityCheck,true);assert.equal(result.checkpointResults.length,2);
 for(const cp of result.checkpointResults){assert.equal(cp.corruptionNegativeControls.length,14);assert.ok(cp.corruptionNegativeControls.every(c=>c.rejected));}
}));

test('fresh-hash artificial artifact-family corruptions reject independently while separately valid final survives',()=>{
 const mutations=[
  ['scientific support mode',m=>{m.scientificTreatment.supportMode='startup-guard';}],
  ['original mask identity',m=>{m.supportTreatment.originalGuardMasksSha256='0'.repeat(64);}],
  ['effective support identity',m=>{m.supportTreatment.effectiveSupportsSha256='0'.repeat(64);}],
  ['NEXT phase',m=>{m.terminal.phase=0;}],
  ['actor word',m=>{m.actors[1][2]^=1;}],
  ['complete cache identity',m=>{m.cacheIdentity.best.push('0'.repeat(64));}],
  ['round block origin',m=>{m.transcriptBlocks[0].firstRound=0;}],
  ['training window counter',m=>{m.windows.at(-1).priceChanges[1]++;}],
  ['display block reward',m=>{m.curves[0].profitSums[1]+=1;}],
  ['transferred guard floor',(m,d)=>{const g=JSON.parse(fs.readFileSync(path.join(d,m.graph.file)));g.floor={transferred:true};rewrite(d,m.graph,g);}],
  ['B cycle reward',(m,d)=>{const g=JSON.parse(fs.readFileSync(path.join(d,m.graph.file)));g.actualTerminal.cycleMetrics.profits.B.numerator=(BigInt(g.actualTerminal.cycleMetrics.profits.B.numerator)+1n).toString();rewrite(d,m.graph,g);}],
  ['all-state WORLD policy',(m,d)=>{const r=m.policies.world[1],b=fs.readFileSync(path.join(d,r.file));b[0]=2;rewrite(d,r,b);}],
  ['dense Q canonical bit',(m,d)=>{const r=m.artifacts.q[0],b=zlib.gunzipSync(fs.readFileSync(path.join(d,r.file)));b[8]^=1;rewrite(d,r,zlib.gzipSync(b));r.rawSha256=sha(b);}],
  ['dense count canonical bit',(m,d)=>{const r=m.artifacts.counts[1],b=zlib.gunzipSync(fs.readFileSync(path.join(d,r.file)));b[0]^=1;rewrite(d,r,zlib.gzipSync(b));r.rawSha256=sha(b);}],
 ];
 for(const[label,mutate]of mutations)withFixture(f=>{
  changedCheckpoint(f,mutate);const result=replayAndCheck(f.task,f.run,f.directory);
  assert.equal(result.checkpointResults[0].available,false,label);assert.equal(result.checkpointResults[1].available,true,label);assert.equal(result.allPlannedCheckpointsMatched,false,label);assert.equal(result.fullHorizonReplayed,true,label);assert.equal(result.finalConsumedIntegrityCheck,true,label);
 });
});

test('new worker rejects hidden task treatment and global consumed-artifact drift',()=>{
 withFixture(f=>{f.task.scientificTreatment.supportMode='startup-guard';assert.throws(()=>replayAndCheck(f.task,f.run,f.directory),/scientific treatment/);});
 withFixture(f=>{
  assert.throws(()=>replayAndCheck(f.task,f.run,f.directory,{onCheckpoint:value=>{if(value.step===10000)fs.appendFileSync(path.join(f.directory,f.run.checkpoints[0].metadata.file),' ');}}),/Consumed artifact changed/);
 });
});
