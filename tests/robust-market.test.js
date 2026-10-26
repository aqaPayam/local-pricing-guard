import test from 'node:test';import assert from 'node:assert/strict';
import * as r from '../research/robust-market.js';
import * as old from '../research/learning-market.js';
import {creditAdvance,creditTrain} from '../research/credit-learning.js';
import {outcome as oldOutcome,NASH_PRICE,MONOPOLY_PRICE} from '../research/replacement-market.js';
test('generic economy has base numerical economic and grid parity',()=>{
 const b=r.continuousBenchmarks();assert.ok(Math.abs(b.nashPrice-NASH_PRICE)<1e-14);assert.ok(Math.abs(b.jointPrice-MONOPOLY_PRICE)<1e-14);
 for(const p of [1,1.2,1.7,2.3])for(const q of [1,1.9,2.5])assert.deepEqual(r.outcome([p,q]),oldOutcome([p,q]));
 assert.deepEqual(r.gridPrices(),old.gridPrices());
});
test('old initialized checkpoints produce exact original proposal paths',()=>{
 const initial=old.createMarket({seed:717}),generic=r.createMarket({seed:717});delete generic.config.economy;assert.deepEqual(initial,generic);
 for(const treatment of [{},{type:'cap'},{type:'guard',epsilon:.1}]){
  const a=old.createMarket({seed:717}),b=old.cloneMarket(a);b.config.economy={...r.BASE};
  const x=creditAdvance(a,1000,{treatment,explorationRate:.01}),y=r.advance(b,1000,{treatment,explorationRate:.01});
  delete b.config.economy;assert.deepEqual(a,b);assert.equal(x.metrics.consumerSurplus,y.metrics.consumerSurplus);assert.equal(x.metrics.retention,y.metrics.retention);
 }
});
test('fast/general paths agree for all economies, arms and multiple grids',()=>{
 for(const e of r.ECONOMIES)for(const n of [11,15,31])for(const arm of [{treatment:{}},{treatment:{type:'cap'}},{treatment:{type:'guard',epsilon:.1}},{treatment:{type:'guard',epsilon:.1},mode:'aware'}]){
  const a=r.createMarket({seed:103,gridSize:n,economy:e}),b=r.cloneMarket(a);r.advance(a,100,arm);r.train(b,100,arm);assert.deepEqual(a,b);
 }
});
test('numerical benchmarks satisfy first order conditions, full finite Nash enumeration',()=>{
 for(const e of r.ECONOMIES){const b=r.continuousBenchmarks(e),h=1e-5,p=b.nashPrice,j=b.jointPrice,d=(r.outcome([p+h,p],e).profits[0]-r.outcome([p-h,p],e).profits[0])/(2*h),jd=(r.outcome([j+h,j+h],e).profits.reduce((a,b)=>a+b)-r.outcome([j-h,j-h],e).profits.reduce((a,b)=>a+b))/(2*h);assert.ok(Math.abs(d)<1e-6);assert.ok(Math.abs(jd)<1e-6);for(const n of [11,15,31]){const grid=r.gridPrices(n,e),g=r.gridBenchmarks(grid,e);for(const [i,j]of g.equilibria){assert.ok(g.profits.every(row=>row[j]<=g.profits[i][j]+1e-12));assert.ok(g.profits.every(row=>row[i]<=g.profits[j][i]+1e-12));}assert.ok(grid[0]<p&&grid.at(-1)>b.jointPrice);}}
});
test('aware execution feasible and frozen Q unchanged; released interfaces coincide',()=>{
 for(const e of r.ECONOMIES){const m=r.createMarket({seed:120,economy:e}),before=m.q.map(x=>Array.from(x)),v=r.advance(m,300,{mode:'aware',treatment:{type:'guard',epsilon:.1},explorationRate:1,learn:false,compactTrace:true});assert.equal(v.metrics.retention,1);assert.deepEqual(m.q.map(x=>Array.from(x)),before);assert.equal(v.trace.length,1200);const a=r.cloneMarket(m),b=r.cloneMarket(m);r.advance(a,300,{mode:'aware',explorationRate:.01});r.advance(b,300,{mode:'proposal',explorationRate:.01});assert.deepEqual(a,b);}
});
