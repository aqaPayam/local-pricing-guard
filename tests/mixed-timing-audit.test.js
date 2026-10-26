import test from 'node:test';
import assert from 'node:assert/strict';
import {Rat,rat,exactDouble,exactDecimal,outwardDecimal,verifyDisplay,tailEnvelope,
  finiteEnvelope,boundedFrontier,adjacentRates,intervalRates,calendarBlocks,
  verifyCalendarBlocks,executionPreview,verifyFiniteEconomics,MAX_K} from '../research/audit-mixed-timing.js';

const q=(n,d=1)=>new Rat(BigInt(n),BigInt(d));
const equal=(a,b)=>assert.equal(rat(a).toString(),rat(b).toString());

test('independent exact imports include subnormal, negative, decimal and malformed values',()=>{
  equal(exactDouble(.5),q(1,2));equal(exactDouble(-.1),q(-3602879701896397n,36028797018963968n));
  equal(exactDouble(Number.MIN_VALUE),new Rat(1n,1n<<1074n));equal(exactDouble(-0),0n);
  equal(exactDecimal('-1.25e-3'),q(-1,800));equal(q(-7,3).floor(),-3n);equal(q(-7,3).ceil(),-2n);
  assert.throws(()=>exactDouble(Infinity));assert.throws(()=>exactDecimal('NaN'));
  assert.throws(()=>rat({numerator:'1',denominator:'0'}));assert.throws(()=>new Rat(1n,0n));
});

test('finite frontier, funded equality and huge rational period do not use observed mixture ratios',()=>{
  const env=tailEnvelope([3,1,0]);const f=boundedFrontier(env,q(3,2));
  assert.equal(f.status,'adjacent');assert.equal(f.K,2);equal(f.a,1n);equal(f.b,q(-1,2));
  equal(f.p,q(2,3));equal(f.rate,q(3,8));equal(f.relativeSaving,q(1,4));
  const blocks=calendarBlocks(f.K,f.a,f.b,6);
  assert.deepEqual(blocks.map(b=>b.length),[2,3,3,2,3,3]);
  equal(blocks[2].before,q(1,2));assert.equal(blocks[2].long,true);equal(blocks[2].after,0n);
  const tiny=adjacentRates(1,q(1,10n**100n),-1n),tinyBlocks=calendarBlocks(1,tiny.a,tiny.b,64);
  assert(tiny.relativeSaving.cmp(0n)>0);assert(tinyBlocks.every(b=>b.length===1));
});

test('every activation prefix and final partial gap, without a sliding-window promise',()=>{
  const env=tailEnvelope([3,1,0]),f=boundedFrontier(env,q(3,2));
  const rows=executionPreview(env,q(3,2),f.K,f.a,f.b,2400);
  assert(rows.every(r=>r.prefixExcess.cmp(0n)>=0));assert(rows.some(r=>r.reward.cmp(q(3,2))<0));
  const at3=rows[2];assert.equal(at3.mode,'cap');equal(at3.reward,3n);
  equal(at3.boundaryCreditAfter,1n);equal(at3.prefixExcess,q(5,2));
  assert(rows.some(r=>!r.blockComplete&&!r.prefixExcess.eq(r.boundaryCreditAfter)));
  assert.equal(rows.at(-1).caps,900); // exact three-cap/eight-execution repetition
});

test('plateaus, startup-only, first-cap failure and a=0 remain separate',()=>{
  const plateau=tailEnvelope([5,5,2]);let f=boundedFrontier(plateau,5);
  assert.equal(f.status,'adjacent');assert.equal(f.K,2);equal(f.a,0n);equal(f.rate,q(1,2));
  assert(calendarBlocks(2,f.a,f.b,20).every(b=>b.length===2));
  assert.equal(boundedFrontier(plateau,2).status,'startup-only');
  assert.equal(boundedFrontier(plateau,-1).status,'startup-only');
  assert.equal(boundedFrontier(plateau,6).status,'infeasible-first-cap');
  assert.equal(boundedFrontier(tailEnvelope([5]),5).status,'startup-only');
  const bZero=boundedFrontier(tailEnvelope([3,1,0]),2);
  assert.equal(bZero.K,2);equal(bZero.a,0n);assert.throws(()=>adjacentRates(1,1,0));
});

test('frontier respects ceiling and censoring, including equality at maximum',()=>{
  const env=tailEnvelope([3,1,0]),f=boundedFrontier(env,q(1,1000000000));
  assert.equal(f.status,'censored');assert.equal(f.safeK,MAX_K);
  assert(env.queries.length>0&&env.queries.every(k=>k<=MAX_K));
  assert.throws(()=>env.sum(MAX_K+1));assert.throws(()=>adjacentRates(MAX_K,1,-1));
  assert.equal(boundedFrontier(tailEnvelope([3,1,0]),q(4,16),16).status,'censored');
});

test('continuous rate enclosure direction and exact constructed rate differ from rounded display',()=>{
  const r=intervalRates(2,{lower:1,upper:2},{lower:-3,upper:-1});
  equal(r.lower,q(3,8));equal(r.upper,q(4,9));equal(r.constructed,r.upper);
  const trueRate=adjacentRates(2,q(3,2),-2).rate;
  assert(r.lower.cmp(trueRate)<0&&r.upper.cmp(trueRate)>0);
  const low=outwardDecimal(r.lower),high=outwardDecimal(r.upper,30,'upper');
  verifyDisplay({lower:r.lower,upper:r.upper},{lower:low,upper:high,precision:30});
  assert(exactDecimal(high).cmp(r.constructed)>0);
  assert(!exactDecimal(outwardDecimal(q(1,3),30,'upper')).eq(q(1,3)));
  const negative=q(-1,3);assert(exactDecimal(outwardDecimal(negative,30,'lower')).cmp(negative)<0);
  assert(exactDecimal(outwardDecimal(negative,30,'upper')).cmp(negative)>0);
  assert.throws(()=>intervalRates(2,{lower:-1,upper:2},{lower:-3,upper:-1}));
  assert.throws(()=>intervalRates(2,{lower:1,upper:2},{lower:-3,upper:0}));
  assert.throws(()=>verifyDisplay({lower:r.upper,upper:r.lower},{lower:low,upper:high,precision:30}));
});

test('full finite supports, cap orbit and all legal artificial prefixes',()=>{
  const n=3,game={prices:[0,1,2],sets:[[0,1],[1,2],[2]],upper:[1,2,2],capIndex:0,
    rewards:{consumerSurplus:Array.from({length:9},(_,i)=>3-Math.floor(i/n)-(i%n))}};
  const env=finiteEnvelope(game);assert.deepEqual(env.indices,[0,1,2]);equal(env.cstar,-1n);
  const F=q(3,2),f=boundedFrontier(env,F),preview=executionPreview(env,F,f.K,f.a,f.b,8);
  let paths=0;
  const walk=(step,previous,total)=>{
    if(step===preview.length){paths++;return;}
    const cap=preview[step].mode==='cap',a=cap?[0]:game.sets[previous[1]],b=cap?[0]:game.sets[previous[0]];
    for(const x of a)for(const y of b){
      const next=total.add(exactDouble(game.rewards.consumerSurplus[x*n+y]).sub(F));
      assert(next.cmp(0n)>=0);walk(step+1,[x,y],next);
    }
  };
  walk(0,[2,2],q(0));assert(paths>1);
  const malformed=structuredClone(game);malformed.upper[1]=0;assert.throws(()=>finiteEnvelope(malformed));
  const down=structuredClone(game);down.capIndex=2;down.upper=[0,1,1];down.sets=[[0],[1],[1]];assert.throws(()=>finiteEnvelope(down));
  const badReward=structuredClone(game);badReward.rewards.consumerSurplus[1]=4;assert.throws(()=>finiteEnvelope(badReward));
});

test('independent economic enumeration checks saved weights and complete masks',()=>{
  const e={quality:0,cost:0,mu:1,buyers:3,outsideQuality:0};
  const r={scenario:{economy:e,epsilon:0},finite:{prices:[0],sets:[[0]],upper:[0],capIndex:0,
    epsilon:0,comparisonAllowance:1e-12,rowBestProfits:[0],rewards:{consumerSurplus:[3*Math.log(3)],
      profitA:[0],profitB:[0],quantityA:[1],quantityB:[1]}}};
  assert.equal(verifyFiniteEconomics(r).payoffPairs,1);
  const corrupt=structuredClone(r);corrupt.finite.rewards.quantityB[0]=2;assert.throws(()=>verifyFiniteEconomics(corrupt));
  const mask=structuredClone(r);mask.finite.sets[0]=[];assert.throws(()=>verifyFiniteEconomics(mask));
});

test('unfunded iid long block and unweighted per-gap mean are genuine negative controls',()=>{
  const env=tailEnvelope([3,1,0]),F=q(3,2),f=boundedFrontier(env,F);
  // Choosing the first long block with the nominal mixing probability has
  // zero expected endpoint excess, but its realized third prefix is negative.
  equal(f.a.mul(q(1,3)).add(f.b.mul(q(2,3))),0n);
  assert(env.sum(3).sub(F.mul(3n)).cmp(0n)<0);
  const unweighted=env.sum(1).div(1n).add(env.sum(3).div(3n)).div(2n);
  const executed=env.sum(1).add(env.sum(3)).div(4n);
  equal(unweighted,q(13,6));equal(executed,q(7,4));assert(unweighted.cmp(2)>0&&executed.cmp(2)<0);
});

test('scientific credit mutations reject despite independent object serialization',()=>{
  const blocks=calendarBlocks(2,1,q(-1,2),6),saved=blocks.map(b=>({length:b.length,
    creditBeforeExact:b.before.toJSON(),creditAfterExact:b.after.toJSON(),endpointCreditExact:b.amount.toJSON()}));
  verifyCalendarBlocks(saved,2,1,q(-1,2));
  for(const change of [
    s=>s[0].length=3,
    s=>s[2].length=2,
    s=>s[1].creditAfterExact=q(0).toJSON(),
    s=>s[1].endpointCreditExact=q(1).toJSON(),
  ]){const corrupt=structuredClone(saved);change(corrupt);assert.throws(()=>verifyCalendarBlocks(corrupt,2,1,q(-1,2)));}
});
