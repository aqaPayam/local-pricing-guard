import test from 'node:test';import assert from 'node:assert/strict';
import {rationalSign,equalRational,scientificDisplay,constructedCalendarTiming,statusCategory} from '../research/mixed-timing-format.js';
const q=(n,d=1)=>({numerator:String(n),denominator:String(d)});
const calendar=(a,b,K=2)=>({kind:'funded-mixed',creditAExact:a,creditBExact:b,K});
test('first-long diagnostic matches independent integer-credit simulation including ties',()=>{
 for(let a=1n;a<=9n;a++)for(let debt=1n;debt<=17n;debt++)for(const K of [1,4,100]){
  let balance=0n,shorts=0n;while(balance<debt){balance+=a;shorts++;}
  const view=constructedCalendarTiming(calendar(q(a,13),q(-debt,13),K),256);
  assert.equal(view.initialShortBlocks,String(shorts));assert.equal(view.firstLongBlock,String(shorts+1n));
  assert.equal(view.firstLongExecution,String(shorts*BigInt(K)+1n));assert.equal(view.withinExecutionPreview,shorts*BigInt(K)+1n<=256n);
 }
});
test('huge first-long timing and zero/nonmixed reasons stay exact and unavailable',()=>{
 const view=constructedCalendarTiming(calendar(q(1,10n**40n),q(-1),4),256);
 assert.equal(view.initialShortBlocks,String(10n**40n));assert.equal(view.firstLongExecution,String(4n*10n**40n+1n));assert.equal(view.withinExecutionPreview,false);
 assert.match(constructedCalendarTiming(calendar(q(0),q(-1))).reason,/never/);
 for(const kind of ['startup-only','fixed-safe','unavailable'])assert.equal(constructedCalendarTiming({kind}).firstLongExecution,null);
 assert.throws(()=>constructedCalendarTiming(calendar(q(-1),q(-2))));assert.throws(()=>constructedCalendarTiming(calendar(q(1),q(0))));
});
test('outward rational displays preserve tiny signs and strict decimal rounding',()=>{
 assert.deepEqual(scientificDisplay(q(1,3)),{lower:'3.33333e-1',upper:'3.33334e-1',sign:'positive',significantDigits:6});
 assert.deepEqual(scientificDisplay(q(-1,3)),{lower:'-3.33334e-1',upper:'-3.33333e-1',sign:'negative',significantDigits:6});
 assert.equal(scientificDisplay(q(1,10n**500n)).lower,'1.00000e-500');assert.equal(scientificDisplay(q(9999999,10000000)).upper,'1.00000e+0');
 assert.equal(rationalSign(q(1,10n**500n)),'positive');assert.equal(rationalSign(q(0)),'zero');assert.ok(equalRational(q(1,3),q(7,21)));
 assert.throws(()=>scientificDisplay({numerator:'1',denominator:'0'}));assert.throws(()=>scientificDisplay({numerator:null,denominator:'1'}));
});
test('status inventory does not conflate zero, missing, censoring or failure',()=>{
 assert.equal(statusCategory({status:'certified startup-only zero limiting rate'}),'startup-only');
 assert.equal(statusCategory({status:'certified exact equality frontier; zero mixed saving'}),'exact-zero-saving');
 assert.equal(statusCategory({status:'censored safe ceiling'}),'censored');
 assert.equal(statusCategory({status:'unresolved calculation or identity'}),'calculation-or-identity-failure');
 assert.throws(()=>statusCategory({status:'certified best guessed optimum'}));
});
