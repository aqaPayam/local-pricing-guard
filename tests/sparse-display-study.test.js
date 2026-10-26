import test from 'node:test';import assert from 'node:assert/strict';import {mergeCap,buildFiniteDisplay} from '../research/sparse-display-study.js';
test('predeclared merge preserves the exact physical cap and records near quote',()=>{
 const cap=1.1,base=[1,1.1+Number.EPSILON,2],r=mergeCap(base,cap);assert.equal(r.prices[r.capIndex],cap);assert.equal(r.prices.length,3);assert.equal(r.removedBaseQuotes.length,1);assert(r.removedBaseQuotes[0].absoluteDistance>0);
 const added=mergeCap([1,1.2,2],cap);assert.equal(added.prices.length,4);assert.equal(added.removedBaseQuotes.length,0);assert.throws(()=>mergeCap([1,cap,cap+Number.EPSILON,2],cap),/Multiple/);
});
test('rejects reversed, external or nonfinite cap intervals',()=>{for(const [p,c] of [[[2,1],1.5],[[1,2],3],[[1,2],NaN]])assert.throws(()=>mergeCap(p,c),/Invalid/);});
test('inherited identity mismatch is rejected before an economic game is generated',()=>{
 assert.throws(()=>buildFiniteDisplay({mesh:{scenario:'wrong',n:61},guard:{scenario:{economy:{},epsilon:0}},cap:{},old:{scenario:{id:'synthetic'}}}),/identity/);
});
