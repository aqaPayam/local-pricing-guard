import test from 'node:test';
import assert from 'node:assert/strict';
import {discreteUpperMap,fixedDestinations,uniformPrices} from '../research/mesh-refinement.js';
import {outcome} from '../research/robust-market.js';

test('binary search recovers full enumerated logit supports on synthetic domains',()=>{
  // These are synthetic numerical cases, not the eight frozen research labels.
  for(const mu of [.3,.8])for(const n of [7,28])for(const epsilon of [0,.08,2]){
    const e={quality:2.7,cost:.4,mu,buyers:17,outsideQuality:.2},prices=uniformPrices(.5,4.5,n),actual=discreteUpperMap(prices,e,epsilon);
    for(let j=0;j<n;j++){
      const row=prices.map(p=>outcome([p,prices[j]],e).profits[0]),best=Math.max(...row),allowed=row.flatMap((p,i)=>best-p<=epsilon+1e-12?[i]:[]);
      assert.equal(actual.upper[j],allowed.at(-1));assert.equal(actual.rows[j].bestProfit,best);
    }
  }
});
test('scalar destinations retain multiple basins and mixed-pair swapping limits',()=>{
  const {fixed,steps,fixedPoints}=fixedDestinations([0,0,2,4,4,6,6]);
  assert.deepEqual(fixed,[0,0,2,4,4,6,6]);assert.deepEqual(steps,[0,1,0,1,0,1,0]);assert.deepEqual(fixedPoints,[0,2,4,6]);
  let pair=[1,5];for(let t=0;t<8;t++)pair=[[0,0,2,4,4,6,6][pair[1]],[0,0,2,4,4,6,6][pair[0]]];
  assert.deepEqual(pair,[0,6]);
});
test('rejects nonmonotone or invalid maps rather than inferring optimality',()=>{
  assert.throws(()=>fixedDestinations([1,0]),/Monotone/);assert.throws(()=>fixedDestinations([0,2]),/Monotone/);assert.throws(()=>uniformPrices(2,1,4),/Invalid/);
});
test('all monotone maps on four ordered values agree with direct orbit tracing',()=>{
  for(let a=0;a<4;a++)for(let b=a;b<4;b++)for(let c=b;c<4;c++)for(let d=c;d<4;d++){
    const u=[a,b,c,d],r=fixedDestinations(u);
    for(let i=0;i<4;i++){let at=i,count=0;while(u[at]!==at&&count<8){at=u[at];count++;}assert.equal(r.fixed[i],at);assert.equal(r.steps[i],count);}
  }
});
