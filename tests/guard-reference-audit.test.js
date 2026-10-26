// Wholly invented games; importing or running performs no inherited IO.
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReplay,replayTo,replayStep,canonicalBytes,expectedGraphClaim,expectedWindowClaims,rowStart} from '../research/audit-matched-clock.js';
import {createReferenceReplay,validateReferenceReplay,expectedReferenceGraph,expectedReferenceWindows,referenceScientificTreatment,decodeAnchorBinary64,enumerateExactStaticAnchors} from '../research/audit-guard-reference.js';
const actors=[[11,22,33,44],[55,66,77,88]];
const toy=()=>({scenario:{id:'invented-independent-reference'},originalTargets:[],finite:{prices:[1,2,3],capIndex:1,sets:[[0],[0,1],[1]],rewards:{profitA:[-2,0,1,3,-1,2,0,1,0],profitB:[1,-3,0,0,2,-1,4,0,1],consumerSurplus:[9,8,7,8,6,5,7,5,3]}}});
const options={T:20000,actors};
const graphScope=' Support treatment is explicit; no inherited guard-envelope/floor assertion applies to full-grid continuation.';
const equalModels=(a,b)=>{
 for(let f=0;f<2;f++)for(const [kind,name] of [['f64','q'],['u32','counts']])assert.deepEqual(canonicalBytes(a[name][f],kind),canonicalBytes(b[name][f],kind));
 assert.deepEqual(a.rng,b.rng);assert.deepEqual(a.previous,b.previous);assert.equal(a.phase,b.phase);assert.equal(a.caps,b.caps);
 assert.deepEqual(a.transcript.snapshot(),b.transcript.snapshot());assert.deepEqual(a.learningBlocks,b.learningBlocks);
};

test('separate effective view preserves physical input and matches immutable old-arm arithmetic',()=>{
 const original=toy(),snapshot=structuredClone(original);
 const a=createReferenceReplay(original,{...options,mode:'startup-guard'}),b=createReplay(original.finite,'startup',options);
 assert.notEqual(a.finite,original.finite);assert.notEqual(a.finite.sets,original.finite.sets);
 replayTo(a,20000);replayTo(b,20000);equalModels(a,b);assert.deepEqual(original,snapshot);assert.equal(validateReferenceReplay(a),true);
 const graph=expectedReferenceGraph(a),old=expectedGraphClaim(b,{certifyFloor:false});
 delete graph.scientificTreatment;delete graph.supportTreatment;old.scope+=graphScope;assert.deepEqual(graph,old);
 assert.deepEqual(expectedReferenceWindows(a),expectedWindowClaims(b));
});

test('full support replay covers every original quote after a real cap with no physical mask mutation',()=>{
 const original=toy(),snapshot=structuredClone(original),a=createReferenceReplay(original,options),full=structuredClone(original.finite);
 full.sets=Array.from({length:3},()=>[0,1,2]);const b=createReplay(full,'startup',options),seen=new Set();
 for(let t=0;t<20000;t++){
  const x=replayStep(a,{trace:true}),y=replayStep(b,{trace:true});assert.deepEqual(x,y);
  if(x.phase>0)for(const index of x.actions)seen.add(index);
  assert.equal(x.targets[1],original.finite.rewards.profitB[x.actions[0]*3+x.actions[1]]+a.gamma*x.nextMaxima[1]);
 }
 equalModels(a,b);assert.deepEqual([...seen].sort(),[0,1,2]);assert.deepEqual(original,snapshot);assert.equal(a.caps,1);assert.equal(a.phase,4);
 assert.deepEqual(a.scientificTreatment,{capClock:'startup',supportMode:'full-grid-after-cap',initialCap:true,postInitialOriginalIndices:'all'});
 const matrix=Array.from({length:5},(_,p)=>Array.from({length:3},()=>p===0?[0,1]:[0,1,2]));
 assert.equal(a.supportTreatment.effectiveSupportsSha256,createHash('sha256').update(JSON.stringify(matrix)).digest('hex'));
 assert.equal(a.supportTreatment.originalGuardMasksSha256,createHash('sha256').update(JSON.stringify(original.finite.sets)).digest('hex'));
 const graph=expectedReferenceGraph(a);assert.equal(graph.floor,null);
 for(const cycle of graph.cycles){assert.equal(cycle.floorApplies,null);assert.equal(cycle.floorGap,null);assert.equal(cycle.metrics.maskCount.A.numerator,'3');assert.equal(cycle.metrics.maskCount.B.numerator,'3');}
 assert.ok(graph.terminalPreview128.every(w=>!w.cap));
});

test('full-grid next bootstrap maxima are pre-update, ties preserve indices and B uses WORLD rewards once',()=>{
 const a=createReferenceReplay(toy(),{T:4,alpha:1,gamma:.5,actors:[[0,0xffffffff,0,1],[0,0xffffffff,0,1]]});
 replayTo(a,3);a.previous=[0,1];a.rng=[[0,0xffffffff,0,1],[0,0xffffffff,0,1]];a.q[0].fill(0);a.q[1].fill(0);
 a.q[0][rowStart(a,3,0,1)+2]=10;a.q[1][rowStart(a,3,1,0)+1]=10;
 a.q[0][rowStart(a,4,2,1)+2]=9;a.q[1][rowStart(a,4,1,2)+2]=7;
 const w=replayStep(a,{trace:true});assert.deepEqual(w.actions,[2,1]);assert.deepEqual(w.nextMaxima,[9,7]);assert.deepEqual(w.newQ,[5.5,3.5]);
 assert.equal(w.targets[1],0+.5*7);assert.equal(a.phase,4);
 const zero=createReferenceReplay(toy(),{T:4,actors:[[0,0xffffffff,0,1],[0,0xffffffff,0,1]]});replayTo(zero,3);zero.previous=[2,2];zero.rng=[[0,0xffffffff,0,1],[0,0xffffffff,0,1]];zero.q[0].fill(0);zero.q[1].fill(0);
 assert.deepEqual(replayStep(zero,{trace:true}).actions,[0,0]);
});

test('scientific declarations, original and effective data and forbidden cap cells fail closed',()=>{
 assert.throws(()=>referenceScientificTreatment('startup'),/Unknown/);
 const mutations=[
  m=>m.finite.sets[0].pop(),m=>m.finite.rewards.profitB[0]++,m=>m.physicalRecord.finite.rewards.profitA[0]++,
  m=>m.supportTreatment.originalGuardMasksSha256='0'.repeat(64),m=>m.scientificTreatment.supportMode='startup-guard',
  m=>m.q[0][2]=-0,
 ];
 for(const mutate of mutations){const m=createReferenceReplay(toy(),options);mutate(m);assert.throws(()=>validateReferenceReplay(m));}
 const invalid=toy();invalid.finite.sets[0]=[];assert.throws(()=>createReferenceReplay(invalid,options),/legal masks/);
});

test('independent fresh binary64 decoder retains signed/fractional/subnormal and rejects nonfinite inputs',()=>{
 assert.deepEqual(decodeAnchorBinary64(-0),{n:0n,d:1n});assert.deepEqual(decodeAnchorBinary64(-1.5),{n:-3n,d:2n});
 assert.deepEqual(decodeAnchorBinary64(Number.MIN_VALUE),{n:1n,d:1n<<1074n});
 assert.deepEqual(decodeAnchorBinary64(2**52),{n:1n<<52n,d:1n});
 for(const v of [NaN,Infinity,-Infinity,'1'])assert.throws(()=>decodeAnchorBinary64(v),/finite binary64/);
});

const staticGame=(A,B,CS=[4,3,2,1])=>({prices:[1,2],rewards:{profitA:A,profitB:B,consumerSurplus:CS}});
test('every static tie and no-pure-Nash case is retained without an invented equilibrium',()=>{
 const tied=enumerateExactStaticAnchors(staticGame([0,-0,0,0],[0,0,-0,0]));
 assert.deepEqual(tied.pureNash.map(p=>p.indices),[[0,0],[0,1],[1,0],[1,1]]);assert.equal(tied.jointProfitMaximizers.length,4);assert.equal(tied.pureNashEmptyReason,null);
 const matching=enumerateExactStaticAnchors(staticGame([1,-1,-1,1],[-1,1,1,-1]));
 assert.deepEqual(matching.pureNash,[]);assert.match(matching.pureNashEmptyReason,/No pure Nash/);assert.equal(matching.jointProfitMaximizers.length,4);
});

test('asymmetric WORLD B orientation and all individual/exact summed values are explicit',()=>{
 const x=enumerateExactStaticAnchors(staticGame([0,2,3,1],[0,4,2,1]));
 assert.deepEqual(x.bestResponses,{AByFixedB:[[1],[0]],BByFixedA:[[1],[0]]});
 assert.deepEqual(x.pureNash.map(p=>p.indices),[[0,1],[1,0]]);
 assert.deepEqual(x.jointProfitMaximizers.map(p=>p.indices),[[0,1]]);
 assert.deepEqual(x.jointProfitMaximizers[0],{indices:[0,1],prices:{A:{numerator:'1',denominator:'1'},B:{numerator:'2',denominator:'1'}},profits:{A:{numerator:'2',denominator:'1'},B:{numerator:'4',denominator:'1'}},jointProfit:{numerator:'6',denominator:'1'},consumerSurplus:{numerator:'3',denominator:'1'}});
});

test('exact separate-profit summation avoids a newly rounded false joint-profit tie',()=>{
 const tiny=2**-53;assert.equal(1+tiny,1);
 const x=enumerateExactStaticAnchors(staticGame([1,1,-1,-1],[tiny,0,0,0]));
 assert.deepEqual(x.jointProfitMaximizers.map(p=>p.indices),[[0,0]]);
 assert.deepEqual(x.jointProfitMaximum,{numerator:'9007199254740993',denominator:'9007199254740992'});
 const sub=enumerateExactStaticAnchors(staticGame([-Number.MIN_VALUE,0,-1,-1],[Number.MIN_VALUE,0,-1,-1]));
 assert.deepEqual(sub.jointProfitMaximizers.map(p=>p.indices),[[0,0],[0,1]]);assert.deepEqual(sub.jointProfitMaximum,{numerator:'0',denominator:'1'});
});

test('malformed anchor dimensions, nonfinite payoffs and invalid domains are rejected',()=>{
 const a=staticGame([1,2,3],[1,2,3,4]);assert.throws(()=>enumerateExactStaticAnchors(a),/dimensions/);
 const b=staticGame([1,2,3,NaN],[1,2,3,4]);assert.throws(()=>enumerateExactStaticAnchors(b),/finite binary64/);
 const c=staticGame([1,2,3,4],[1,2,3,4]);c.prices=[2,2];assert.throws(()=>enumerateExactStaticAnchors(c),/increase/);
});
