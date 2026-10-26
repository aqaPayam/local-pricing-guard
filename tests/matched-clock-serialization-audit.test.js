// Complete wholly artificial primary-to-independent transport fixture. No old
// game, original checkpoint, matched-market outcome or research run is read.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import zlib from 'node:zlib';import crypto from 'node:crypto';
import {createLearners,advanceTo,actorNamespaces} from '../research/matched-clock-learning.js';
import {evaluateFrozen,summarizeWindows} from '../research/matched-clock-graph.js';
import {writeCheckpoint} from '../research/matched-clock-io.js';
import {replayAndCheck,independentDense} from '../research/replay-matched-clock.js';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const root=path.resolve('.local'),raw=()=>({finite:{prices:[1,2,3],capIndex:1,sets:[[0,1],[0,1,2],[1,2]],upper:[1,2,2],rewards:{profitA:[0,1,4,5,6,9,10,11,12],profitB:[7,2,3,1,4,8,5,6,9],consumerSurplus:[9,8,7,8,7,6,7,6,5]}},originalTargets:[{label:'artificial95',requestedTarget:6,actualGuaranteedThreshold:5.1,numericalMargin:.9}]});
function save(dir,name,value){const bytes=Buffer.isBuffer(value)?value:Buffer.from(JSON.stringify(value,null,2)+'\n'),target=path.join(dir,name);fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes,{flag:'wx'});return{file:name,bytes:bytes.length,sha256:hash(bytes)};}
function fixture(arm){
  const directory=path.join(root,'matched-serialized-'+crypto.randomUUID());fs.mkdirSync(directory,{recursive:true});
  const record=raw(),finiteGameRef=save(directory,'invented-model.json',record),plan={id:'artificial-'+arm,arm,seed:907001,actors:actorNamespaces()[0].actors},software={scope:'wholly artificial fixture'},T=20000;
  const task={plan,finite:record.finite,originalTargets:record.originalTargets,finiteGameRef,software,T,checkpoints:[10000,20000]};
  const primary=createLearners(record,arm,{T}),checkpoints=[];
  try{for(const step of task.checkpoints){advanceTo(primary,step);const metadata=writeCheckpoint(directory,primary,{id:plan.id,software,graph:evaluateFrozen(primary),windowMetrics:summarizeWindows(primary),finiteGameRef});checkpoints.push({step,metadata,parentEligible:true});}}catch(error){cleanup(directory);throw error;}
  return{directory,task,run:{...plan,executionSucceeded:true,checkpoints}};
}
function cleanup(directory){const resolved=path.resolve(directory);assert.ok(resolved.startsWith(root+path.sep)&&path.basename(resolved).startsWith('matched-serialized-'));fs.rmSync(resolved,{recursive:true});}
function changedMeta(f,index,modify){
  const run=structuredClone(f.run),meta=JSON.parse(fs.readFileSync(path.join(f.directory,run.checkpoints[index].metadata.file),'utf8'));
  modify(meta);run.checkpoints[index].metadata=save(f.directory,'mutant-'+crypto.randomUUID()+'.json',meta);return run;
}

test('all canonical compressed checkpoint artifacts and complete graphs match independently from zero for both arms',()=>{
  for(const arm of ['startup','recurring4']){
    const f=fixture(arm);try{const r=replayAndCheck(f.task,f.run,f.directory);assert.equal(r.replayedRounds,20000);assert.equal(r.allPlannedCheckpointsMatched,true);assert.equal(r.transcriptBlocksMatched,2);assert.equal(r.finalConsumedIntegrityCheck,true);assert.equal(r.checkpointResults.length,2);}finally{cleanup(f.directory);}
  }
});

test('fresh-hash mutations of every scientific artifact family are rejected, including complete ancillary/cache/window fields',()=>{
  const f=fixture('recurring4');try{
    const mutations=[
      m=>{m.terminal.phase=1;},m=>{m.actors[0][0]^=1;},m=>{m.caps=true;},
      m=>{m.cacheIdentity.best.push('a'.repeat(64));},m=>{m.curves[0].profitSums[0]+=1;},
      m=>{m.windows[0].priceChanges[0]+=1;},m=>{m.windowMetrics[0].metrics.maskSpan.A.numerator='999';},
      m=>{m.transcriptBlocks[0].firstRound=0;},m=>{m.transcriptBlocks[0].sha256='b'.repeat(64);},
      m=>{m.extraScientificClaim=100;},
      m=>{const g=JSON.parse(fs.readFileSync(path.join(f.directory,m.graph.file)));g.actualTerminal.cycleMetrics.profits.B.numerator='999';m.graph=save(f.directory,'mutant-graph-'+crypto.randomUUID()+'.json',g);},
      m=>{const g=JSON.parse(fs.readFileSync(path.join(f.directory,m.graph.file)));g.terminalPreview128[0].cap=!g.terminalPreview128[0].cap;m.graph=save(f.directory,'mutant-graph-'+crypto.randomUUID()+'.json',g);},
      m=>{const ref=m.artifacts.q[0],b=zlib.gunzipSync(fs.readFileSync(path.join(f.directory,ref.file)));b[0]^=1;m.artifacts.q[0]={...save(f.directory,'mutant-q-'+crypto.randomUUID()+'.gz',zlib.gzipSync(b,{mtime:0})),encoding:'f64le',compression:'gzip-single-member',rawBytes:b.length,rawSha256:hash(b)};},
      m=>{const ref=m.artifacts.counts[1],b=zlib.gunzipSync(fs.readFileSync(path.join(f.directory,ref.file)));b.writeUInt32LE(b.readUInt32LE(0)+1,0);m.artifacts.counts[1]={...save(f.directory,'mutant-count-'+crypto.randomUUID()+'.gz',zlib.gzipSync(b,{mtime:0})),encoding:'u32le',compression:'gzip-single-member',rawBytes:b.length,rawSha256:hash(b)};},
    ];
    for(const mutate of mutations){const run=changedMeta(f,0,mutate),r=replayAndCheck(f.task,run,f.directory);assert.equal(r.checkpointResults[0].matched,false);assert.equal(r.checkpointResults[1].matched,true,'Bad1M-equivalent secondary must not suppress a valid final');assert.equal(r.fullHorizonReplayed,true);assert.equal(r.allPlannedCheckpointsMatched,false);}
  }finally{cleanup(f.directory);}
});

test('single-member, trailing bytes, raw-size ceilings and CRC are checked independently before adoption',()=>{
  const n=2,b=Buffer.alloc(5*n**3*8),gzip=zlib.gzipSync(b,{mtime:0}),ref={encoding:'f64le',compression:'gzip-single-member',rawBytes:b.length,rawSha256:hash(b)};
  assert.ok(independentDense(gzip,ref,n,'f64le').equals(b));
  const badCRC=Buffer.from(gzip);badCRC[badCRC.length-8]^=1;
  for(const bad of [Buffer.concat([gzip,Buffer.from([0])]),Buffer.concat([gzip,zlib.gzipSync(Buffer.alloc(0),{mtime:0})]),zlib.gzipSync(Buffer.alloc(b.length+1),{mtime:0}),badCRC])assert.throws(()=>independentDense(bad,ref,n,'f64le'));
  assert.throws(()=>independentDense(gzip,{...ref,rawBytes:b.length*2},n,'f64le'));
});

test('ineligible old files are never adopted and end-of-replay consumed drift is fatal',()=>{
  const f=fixture('startup');try{
    const run=structuredClone(f.run);run.checkpoints[0].parentEligible=false;const r=replayAndCheck(f.task,run,f.directory);assert.equal(r.checkpointResults[0].available,false);assert.equal(r.checkpointResults[1].available,true);assert.equal(r.replayedRounds,20000);assert.equal(r.allPlannedCheckpointsMatched,false);
    const first=path.join(f.directory,f.run.checkpoints[0].metadata.file),original=fs.readFileSync(first);
    assert.throws(()=>replayAndCheck(f.task,f.run,f.directory,{onCheckpoint:result=>{if(result.step===10000)fs.appendFileSync(first,' ');}}),/changed during replay/);
    fs.writeFileSync(first,original);
  }finally{cleanup(f.directory);}
});
