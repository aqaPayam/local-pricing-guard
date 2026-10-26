// Statistical-analysis checks on synthetic differences only; no training data.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import crypto from 'node:crypto';
import{indices,pairedMeanInterval,percentileType7}from'../research/adaptive-bootstrap.js';
test('prospective resample inventory is complete and unchanged before outcomes',()=>{
 const data=fs.readFileSync(new URL('../research/adaptive-bootstrap-indices.json',import.meta.url)),stored=JSON.parse(data);
 assert.equal(crypto.createHash('sha256').update(data).digest('hex'),'8fd7455251b3d7faa50ad0125672ab5f0adfa8763a78988d41575a25af05cfbc');
 assert.deepEqual(stored.indices,indices());assert.equal(stored.indices.length,5120);assert(stored.indices.every(row=>row.length===12&&row.every(i=>Number.isInteger(i)&&i>=0&&i<12)));
});
test('type7 interpolation uses endpoints and between-order positions',()=>{
 const ordered=Array.from({length:12},(_,i)=>i);assert.equal(percentileType7(ordered,0),0);assert.equal(percentileType7(ordered,1),11);assert.equal(percentileType7(ordered,.025),.275);assert.equal(percentileType7(ordered,.975),10.725);
});
test('whole-pair resampling preserves exact-zero and constant shifts and rejects missing pairs',()=>{
 const zero=pairedMeanInterval(Array(12).fill(0));assert.equal(zero.estimate,0);assert.equal(zero.lower,0);assert.equal(zero.upper,0);
 const constant=pairedMeanInterval(Array(12).fill(-3));assert.equal(constant.estimate,-3);assert.equal(constant.lower,-3);assert.equal(constant.upper,-3);
 const pairs=Array.from({length:12},(_,i)=>i-6),a=pairedMeanInterval(pairs),b=pairedMeanInterval(pairs.map(x=>x+4));assert.equal(a.estimate,-.5);assert.equal(b.estimate-a.estimate,4);assert(Math.abs((b.lower-a.lower)-4)<1e-12);assert(Math.abs((b.upper-a.upper)-4)<1e-12);
 assert.throws(()=>pairedMeanInterval(pairs.slice(1)),/twelve/);assert.throws(()=>pairedMeanInterval([...pairs.slice(1),NaN]),/twelve/);
});
