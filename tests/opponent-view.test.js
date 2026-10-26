import test from 'node:test';import assert from 'node:assert/strict';
import {renderPurchaseBaskets} from '../research/demo/opponent.js';
const fills=markup=>[...markup.matchAll(/<rect[^>]*height="([0-9.]+)"/g)].map(m=>Number(m[1]));
test('ten-unit basket scale faithfully represents purchases above50 and up to100',()=>{
 const q65=fills(renderPurchaseBaskets(65,'A'));assert.equal(q65.length,10);assert.deepEqual(q65.slice(0,6),Array(6).fill(17));assert.equal(q65[6],8.5);assert.deepEqual(q65.slice(7),[0,0,0]);assert.equal(q65.reduce((a,b)=>a+b,0),17*6.5);assert.deepEqual(fills(renderPurchaseBaskets(100,'B')),Array(10).fill(17));assert.deepEqual(fills(renderPurchaseBaskets(0,'A')),Array(10).fill(0));
});
test('empty purchase memory draws no earned baskets and malformed quantities reject',()=>{
 assert.match(renderPurchaseBaskets(null,'A'),/No local purchases yet/);for(const q of [NaN,Infinity,-1])assert.throws(()=>renderPurchaseBaskets(q,'A'));assert.throws(()=>renderPurchaseBaskets(10,'C'));
});
