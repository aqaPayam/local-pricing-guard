import test from 'node:test';
import assert from 'node:assert/strict';
import {statusView,radiusView,scheduleView,validateEvidence} from '../research/demo/uncertainty.js';

test('empty calibration-safe sets are distinct from certified exact zero and tiny positive reserve',()=>{
 const empty=radiusView({status:'already failing at zero; empty safe nonnegative set'});
 const zero=radiusView({status:'certified exact zero radius'});
 const tiny=radiusView({status:'certified crossing enclosure',lower:'0.000000012345',upper:'0.000000012346'});
 assert.match(empty.headline,/Already below/);assert.match(empty.detail,/empty/);
 assert.match(zero.headline,/only at zero/);assert.match(tiny.headline,/e-8/);assert.notEqual(tiny.headline,zero.headline);
 const overlap=radiusView({status:'unresolved zero-displacement overlap'});assert.match(overlap.headline,/Unresolved/);
 assert.match(radiusView({status:'certified crossing enclosure',lower:'0',upper:'0.00000000000000000001'}).headline,/Between 0/);
});
test('timing claims retain family infeasibility, censoring and phase/startup scope',()=>{
 assert.equal(scheduleView({status:'infeasible for this fixed-cap family'}).className,'fail');
 assert.match(scheduleView({status:'infeasible for this fixed-cap family'}).detail,/different controller/);
 assert.match(scheduleView({status:'censored safe lower bound',certifiedSafePeriodLowerBound:65536}).detail,/unchecked/);
 assert.match(scheduleView({status:'no recurring cap needed for the long-run target'}).detail,/startup/);
 assert.match(scheduleView({status:'largest certified fixed period',largestPeriod:1}).headline,/every execution/);
 assert.equal(statusView('already failing').className,'fail');assert.equal(statusView('unresolved overlap').className,'unresolved');
});
test('presentation refuses unavailable audit identities and undeclared interpolating levels',()=>{
 assert.throws(()=>validateEvidence({}),/evidence/);
 const fake={meta:{primaryAudit:{passed:true},primaryManifestSha256:'a'.repeat(64),primaryResultsSha256:'b'.repeat(64),independentAuditSha256:'c'.repeat(64)},rows:Array(8).fill({}),levels:['0','0.001','0.02','0.05'].map(dExact=>({dExact}))};
 assert.throws(()=>validateEvidence(fake),/four declared/);fake.meta.primaryAudit.passed=false;assert.throws(()=>validateEvidence(fake),/unavailable/);
});
