import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeMesh} from '../research/mesh-refinement.js';
import {auditMeshCase,traceScalarDestinations} from '../research/audit-mesh-refinement.js';

function synthetic(economy={quality:2.7,cost:.4,mu:.3,buyers:17,outsideQuality:.2},epsilon=.08,lo=.5,hi=4.5,n=23){
 const targets=[{label:'unit-low',requestedTarget:10,actualGuaranteedThreshold:9.9999999},{label:'unit-high',requestedTarget:30,actualGuaranteedThreshold:29.9999997}],inputs={economy,epsilon,lo,hi,targets};return {inputs,result:{economy,...analyzeMesh({...inputs,n})}};
}
test('full independent streaming enumeration and pair tails match a synthetic case',()=>{
 const f=synthetic(),r=auditMeshCase(f.result,f.inputs);assert.equal(r.pairsScanned,23**2);assert.equal(r.pairTailsChecked,23**2);
});
test('independent audit rejects corrupt maps, maxima, destinations, welfare and targets',()=>{
 const f=synthetic();for(const mutate of [r=>{r.map.upper[0]++;},r=>{r.map.rows[0].bestProfit++;},r=>{r.destinations.fixed[0]++;},r=>{r.welfare.oneRoundCapWorst++;},r=>{r.targets[0].alreadySafe=!r.targets[0].alreadySafe;}]){const changed=structuredClone(f.result);mutate(changed);assert.throws(()=>auditMeshCase(changed,f.inputs));}
});
test('direct orbit audit preserves mixed-pair swapping destinations',()=>{
 const r=traceScalarDestinations([0,0,2,4,4,6,6]);assert.deepEqual(r.fixed,[0,0,2,4,4,6,6]);assert.deepEqual(r.steps,[0,1,0,1,0,1,0]);assert.throws(()=>traceScalarDestinations([1,0]),/cycle/);
});
test('analytic nonmonotone synthetic example retains unresolved target labels',()=>{
 const f=synthetic({quality:2+Math.log(2),cost:0,mu:1,buyers:1,outsideQuality:0},.5,1,5,101),r=auditMeshCase(f.result,f.inputs);assert.equal(r.status,'unresolved-upper-map-nonmonotone');assert.equal(f.result.targets.length,2);assert.ok(f.result.targets.every(t=>t.allStateFailingTail===null));
});
