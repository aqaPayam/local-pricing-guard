// Developer replay checks, not training, a new experiment or human validation.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {createContinuationGame,displayAmount} from '../research/learned-opponent-game.js';
import {fromDouble,rational,add,subtract} from '../research/recurring-game.js';import {exact,pack} from '../research/learned-opponent-format.js';
const data=JSON.parse(fs.readFileSync(new URL('../research/learned-opponent-results/web-data.json',import.meta.url),'utf8')),gameData=data.webgameData,f=gameData.finiteGame.finite,n=f.prices.length;
const mul=(a,b)=>rational(a.n*b.n,a.d*b.d),same=(a,b)=>assert.equal(a.n*b.d,b.n*a.d),gamma=rational(19n,20n);
function selection(record){return{finiteGame:gameData.finiteGame,checkpoint:gameData.checkpointCases.find(c=>c.id===record.oldRunID),response:gameData.responsePolicies.find(p=>p.recordId===record.id),focal:record.focal};}
const pairAt=(path,t)=>{const index=t<path.states.length?t:path.h+(t-path.h)%path.c;return[path.executedA[index],path.executedB[index]];};
test('all48 accepted selections replay64 audit-policy rounds with exact independent reference accounting',()=>{
 assert.equal(data.meta.independentAuditPassed,true);let guards=0,caps=0,finiteDiffers=0;
 for(const record of data.records){const input=selection(record),game=createContinuationGame(input),initial=game.snapshot();assert.equal(initial.earned,null);assert.equal(initial.baseline,null);assert.equal(initial.latest,null);assert.deepEqual(initial.previousIndices,input.checkpoint.terminal.previousIndices);assert.equal(initial.phase,input.checkpoint.terminal.phase);
  const baseline=JSON.parse(fs.readFileSync(new URL('../research/learned-opponent-results/'+record.baseline.path.file,import.meta.url),'utf8')),response=JSON.parse(fs.readFileSync(new URL('../research/learned-opponent-results/'+record.response.path.file,import.meta.url),'utf8'));let own=rational(0n),base=rational(0n),weight=rational(1n);const reward=f.rewards[record.focal==='A'?'profitA':'profitB'];
  for(let t=0;t<64;t++){const before=game.snapshot(),hint=before.auditAction;assert(game.allowed().includes(hint));assert.equal(game.snapshot().executions,t);const s=game.execute(hint),p=pairAt(response,t),b=pairAt(baseline,t);assert.deepEqual(s.latest.indices,p);assert.deepEqual(s.latest.baselineIndices,b);assert.equal(s.latest.phase,before.phase);own=add(own,mul(weight,fromDouble(reward[p[0]*n+p[1]])));base=add(base,mul(weight,fromDouble(reward[b[0]*n+b[1]])));same(exact(s.earned.exact),own);same(exact(s.baseline.exact),base);same(exact(s.difference.exact),subtract(own,base));weight=mul(weight,gamma);if(s.latest.type==='guard')guards++;else caps++;if(record.control.id==='startup-only')assert.equal(s.phase,1);else assert.equal(s.phase,(t+1)%4);}
  if(exact(game.snapshot().difference.exact).n*exact(record.performance.rawGain).d!==exact(record.performance.rawGain).n*exact(game.snapshot().difference.exact).d)finiteDiffers++;
 }
 assert(guards>0&&caps>0);assert(finiteDiffers>0);
});
test('manual low/high choices use prior-world rival action, independent baseline and correct own-row B counts',()=>{
 for(const record of data.records){const input=selection(record),game=createContinuationGame(input);for(let t=0;t<8;t++){
  const before=game.snapshot(),action=t%2?game.allowed().at(-1):game.allowed()[0],world=before.phase*n*n+before.previousIndices[0]*n+before.previousIndices[1],opponent=input.checkpoint.originalWorldPolicies[record.focal==='A'?'B':'A'][world],preview=game.preview(action);assert.equal(preview.indices[record.focal==='A'?1:0],opponent);assert.equal(game.snapshot().executions,t);const after=game.execute(action);assert.deepEqual(after.latest.indices,preview.indices);
  for(let actor=0;actor<2;actor++){const p=before.previousIndices,row=before.phase*n*n+p[actor]*n+p[1-actor],choices=before.phase===0?Array.from({length:f.capIndex+1},(_,i)=>i):f.sets[p[1-actor]],offsets=input.checkpoint.trainingCounts.rowOffsets,cells=input.checkpoint.trainingCounts[actor===0?'A':'B'],from=offsets[row],to=offsets[row+1],rank=choices.indexOf(after.latest.indices[actor]);assert.deepEqual(after.latest.coverage[actor===0?'A':'B'],{stateVisits:cells.slice(from,to).reduce((a,b)=>a+b,0),chosenActionVisits:cells[from+rank]});}
 }}
});
test('illegal quote is atomic and undo/reset restore all histories, clock and exact ledgers',()=>{
 const game=createContinuationGame(selection(data.records[0])),snapshots=[game.snapshot()];for(let i=0;i<7;i++)snapshots.push(game.execute(game.allowed().at(-1)));const before=JSON.stringify(game.snapshot());assert.throws(()=>game.execute(999));assert.equal(JSON.stringify(game.snapshot()),before);for(let i=6;i>=0;i--)assert.deepEqual(game.undo(),snapshots[i]);assert.equal(game.snapshot().earned,null);game.execute(game.allowed()[0]);assert.deepEqual(game.reset(),snapshots[0]);
});
test('unavailable response disables only hint; unavailable checkpoint and malformed off-path data lock play',()=>{
 const source=selection(data.records[0]),none={...source,response:{recordId:source.response.recordId,scientificAvailable:false,actions:null,reason:'Artificial unavailable'}};assert.equal(createContinuationGame(none).snapshot().auditAction,null);assert.doesNotThrow(()=>{const g=createContinuationGame(none);g.execute(g.allowed()[0]);});
 assert.throws(()=>createContinuationGame({...source,checkpoint:{...source.checkpoint,available:false}}),/locked/);
 const bad=structuredClone(source);bad.response.actions[bad.response.actions.length-1]=999;assert.throws(()=>createContinuationGame(bad),/off path/);const wrong=structuredClone(source);wrong.checkpoint.trainingCounts.B[0]++;assert.throws(()=>createContinuationGame(wrong),/count total/);assert.throws(()=>createContinuationGame({...source,focal:'B'}),/different saved shop/);
});
test('zero and tiny signed exact amounts do not masquerade as rounded numeric zero',()=>{
 assert.equal(displayAmount(null),'—');assert.equal(displayAmount(pack(rational(0n))),'0');assert.match(displayAmount(pack(rational(1n,10n**9n))),/e-9/);assert.match(displayAmount(pack(rational(-1n,10n**9n))),/^-.*e-9/);
});
