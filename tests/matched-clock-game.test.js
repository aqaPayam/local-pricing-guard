import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createPairedReplay,decodeWorldPolicy} from '../research/matched-clock-game.js';
import {rational,add,fromDouble,exactJSON,divideInteger} from '../research/recurring-game.js';
const encoding='uint8 WORLD row-major (phase,previousA,previousB)';
const finite=()=>({prices:[.1,.2,.3],capIndex:0,sets:[[0],[1],[1,2]],rewards:{consumerSurplus:[.9,.8,.7,.6,.5,.4,.3,.2,.1],profitA:[-.1,0,.1,.2,.3,.4,.5,.6,.7],profitB:[.7,.6,.5,.4,.3,.2,.1,0,-.1],quantityA:[1,2,3,4,5,6,7,8,9],quantityB:[9,8,7,6,5,4,3,2,1]}});
const ref=bytes=>({base64:Buffer.from(bytes).toString('base64'),bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
function fixture(seed=907001){
 const f=finite(),arms={};
 for(const arm of ['startup','recurring4']){
  const policies=[new Uint8Array(45),new Uint8Array(45)];
  for(let s=0;s<45;s++){const p=Math.floor(s/9),a=Math.floor(s/3)%3,b=s%3,cap=p===0||(arm==='recurring4'&&p===4);policies[0][s]=cap?0:f.sets[b].at(-1);policies[1][s]=cap?0:f.sets[a].at(-1);}
  arms[arm]={seed,arm,checkpointId:`${arm}-final`,runId:`${arm}-s${seed}`,available:true,reason:null,encoding,states:45,start:{phase:4,previousIndices:arm==='startup'?[2,1]:[1,2]},policies:{A:ref(policies[0]),B:ref(policies[1])}};
 }
 return{finiteGame:f,seed,arms};
}
test('both actual histories start unearned at phase4 and only recurring gets its natural cap',()=>{
 for(let seed=907001;seed<=907012;seed++){
  const input=fixture(seed),g=createPairedReplay(input),start=g.snapshot();assert.equal(start.executions,0);assert.equal(start.arms.startup.earned,null);assert.equal(start.arms.recurring4.latest,null);assert.deepEqual(start.arms.startup.previousIndices,[2,1]);assert.deepEqual(start.arms.recurring4.previousIndices,[1,2]);
  assert.equal(start.arms.startup.nextIsCap,false);assert.equal(start.arms.recurring4.nextIsCap,true);const preview=g.preview();assert.deepEqual(g.snapshot(),start);assert.deepEqual(preview.startup.executedIndices,[1,2]);assert.deepEqual(preview.recurring4.executedIndices,[0,0]);
  const one=g.advance();assert.equal(one.arms.startup.phase,1);assert.equal(one.arms.startup.capExecutions,0);assert.equal(one.arms.recurring4.capExecutions,1);assert.equal(one.arms.startup.latest.profits[1],input.finiteGame.rewards.profitB[5]);
  g.restart();assert.deepEqual(g.snapshot(),start);
 }
});
test('WORLD B is not transposed twice, rewards use destination pairs, and memory/policies are isolated from caller edits',()=>{
 const input=fixture(),g=createPairedReplay(input);input.finiteGame.prices[2]=999;input.finiteGame.rewards.profitB[5]=999;input.arms.startup.start.previousIndices[0]=0;input.arms.startup.policies.B.base64='bad';
 const s=g.advance();assert.deepEqual(s.arms.startup.latest.sourceIndices,[2,1]);assert.deepEqual(s.arms.startup.latest.executedIndices,[1,2]);assert.deepEqual(s.arms.startup.latest.prices,[.2,.3]);assert.equal(s.arms.startup.latest.profits[1],.2);
 s.arms.startup.previousIndices[0]=99;s.trace[0].startup.executedIndices[0]=99;assert.deepEqual(g.snapshot().arms.startup.previousIndices,[1,2]);assert.deepEqual(g.snapshot().trace[0].startup.executedIndices,[1,2]);
});
test('exact binary64 finite sums/averages stay distinct from cycle statistics and undo restores both ledgers',()=>{
 const g=createPairedReplay(fixture()),sums=Object.fromEntries(['startup','recurring4'].map(a=>[a,{cs:rational(0n),A:rational(0n),B:rational(0n)}]));
 const start=g.snapshot();for(let t=1;t<=37;t++){const s=g.advance();for(const arm of ['startup','recurring4']){const r=s.arms[arm].latest;for(const[key,value]of[['cs',r.consumerSurplus],['A',r.profits[0]],['B',r.profits[1]]])sums[arm][key]=add(sums[arm][key],fromDouble(value));assert.deepEqual({...s.arms[arm].earned.customerBenefit.sum,approximate:undefined},{...exactJSON(sums[arm].cs),approximate:undefined});assert.deepEqual({...s.arms[arm].earned.profits.B.average,approximate:undefined},{...exactJSON(divideInteger(sums[arm].B,t)),approximate:undefined});assert.equal('cycleMetrics'in s.arms[arm].earned,false);}}
 const final=g.snapshot();g.undo(20);assert.equal(g.snapshot().executions,17);g.advance(20);assert.deepEqual(g.snapshot(),final);g.undo(20);g.undo(20);assert.deepEqual(g.snapshot(),start);
});
test('strict 4096-round limit is atomic, latest60 trace is bounded and restart restores actual endpoints',()=>{
 const g=createPairedReplay(fixture());for(let i=0;i<204;i++)g.advance(20);g.advance(16);const final=g.snapshot();assert.equal(final.executions,4096);assert.equal(final.trace.length,60);assert.equal(final.traceStartRound,4037);assert.equal(final.canAdvance,false);
 assert.throws(()=>g.advance(),/4096/);assert.deepEqual(g.snapshot(),final);for(const bad of [0,21,-1,1.5,NaN])assert.throws(()=>g.advance(bad),/batch/);assert.deepEqual(g.snapshot(),final);g.undo();assert.equal(g.snapshot().executions,4095);assert.throws(()=>g.advance(20),/4096/);assert.equal(g.snapshot().executions,4095);g.restart();assert.equal(g.snapshot().executions,0);assert.deepEqual(g.snapshot().arms.startup.previousIndices,[2,1]);
});
test('missing final arm locks paired controls with null earnings, not a zero substitute or silent one-arm replay',()=>{
 const input=fixture();input.arms.recurring4={...input.arms.recurring4,available:false,reason:'Retained missing final endpoint',policies:null};const g=createPairedReplay(input),s=g.snapshot();assert.equal(s.available,false);assert.equal(s.arms.startup.earned,null);assert.equal(s.finiteBenefitDifference,null);assert.match(s.reason,/missing final/);assert.throws(()=>g.advance(),/locked/);assert.throws(()=>g.preview(),/locked/);assert.deepEqual(g.restart(),s);assert.deepEqual(g.undo(),s);
});
test('canonical base64, all-state legality, dimensions and forbidden fresh-cap/mismatched identities reject',()=>{
 for(const change of [
  x=>{x.arms.startup.start.phase=0;},x=>{x.arms.startup.seed=907002;},x=>{x.arms.startup.states=44;},x=>{x.arms.startup.encoding='own/rival';},
  x=>{x.arms.startup.policies.A.base64+='\n';},x=>{x.arms.startup.policies.B.bytes=44;},x=>{x.finiteGame.rewards.quantityA[0]=-1;},x=>{x.finiteGame.sets[2]=[2,1];},
  x=>{const b=Buffer.from(x.arms.startup.policies.B.base64,'base64');b[0]=2;x.arms.startup.policies.B=ref(b);}
 ]){const x=fixture();change(x);assert.throws(()=>createPairedReplay(x));}
 assert.throws(()=>decodeWorldPolicy({base64:'AA==',bytes:45,sha256:'a'.repeat(64)},45),/reference/);
});
