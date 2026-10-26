import test from 'node:test';import assert from 'node:assert/strict';
import {exact,pack,parseSignedHex,add,subtract,compare,divideInteger,median,scientificDisplay,validateAvailableRecord,summarizeRecords,ZERO,ONE} from '../research/learned-opponent-format.js';
import {r,record} from './helpers/learned-opponent-fixture.js';
test('canonical signed hexadecimal scalars reject alternate signs, reduction and oversized tokens before conversion',()=>{
 assert.equal(parseSignedHex('-0xa'),-10n);assert.deepEqual(exact(ZERO),{n:0n,d:1n});
 for(const bad of ['-0x0','0X1','0x01','0xaB','+0x1','0x'])assert.throws(()=>parseSignedHex(bad));
 assert.throws(()=>exact({numeratorHex:'0x2',denominatorHex:'0x2'}));assert.throws(()=>exact({numeratorHex:'0x1',denominatorHex:'-0x1'}));
 assert.throws(()=>parseSignedHex('0x1'+'0'.repeat(250001)),/before parsing/);
});
test('bounded rational arithmetic, medians and outward decimals preserve tiny exact signs and large fractions',()=>{
 assert.deepEqual(add(r(-1n,3n),r(1n,2n)),r(1n,6n));assert.deepEqual(divideInteger(r(-2n,3n),2),r(-1n,3n));
 assert.deepEqual(median([r(5n),r(-1n),r(1n),r(3n)]),r(2n));
 assert.deepEqual(scientificDisplay(r(-1n,3n)),{lower:'-3.33334e-1',upper:'-3.33333e-1',sign:'negative',significantDigits:6});
 assert.deepEqual(scientificDisplay(r(9999999n,1000000n)),{lower:'9.99999e+0',upper:'1.00000e+1',sign:'positive',significantDigits:6});
 const big=10n**5000n,scalar=r(big+1n,big+3n);assert.ok(compare(scalar,ONE)<0);assert.equal(scientificDisplay(scalar).upper,'1.00000e+0');
 assert.deepEqual(scientificDisplay(r(1n,10n**5000n)),{lower:'1.00000e-5000',upper:'1.00000e-5000',sign:'positive',significantDigits:6});
 function displayRat(s){const [m,e]=s.split('e'),places=(m.split('.')[1]??'').length,n=BigInt(m.replace('.','')),shift=Number(e)-places;return shift>=0?r(n*10n**BigInt(shift)):r(n,10n**BigInt(-shift));}
 for(const scalar of [r(1n,3n),r(-1n,3n),r(9999999n,1000000n),r(big+1n,big+3n),r(1n,10n**5000n)]){const d=scientificDisplay(scalar);assert.ok(compare(displayRat(d.lower),scalar)<=0);assert.ok(compare(displayRat(d.upper),scalar)>=0);}
});
test('raw negative response, zero fallback, nonpositive baseline and loose upper certificate stay distinct',()=>{
 const neg=record(1,'startup-only','A',{baseline:-2n,response:-3n,upper:0n});assert.equal(validateAvailableRecord(neg),true);assert.deepEqual(neg.performance.rawGain,r(-1n));assert.deepEqual(neg.performance.possibleGain.lower,ZERO);assert.equal(neg.performance.relativeGain,null);
 const zero=record(1,'startup-only','A',{baseline:0n,response:0n,upper:1n});assert.equal(validateAvailableRecord(zero),true);
 for(const mutate of [x=>x.performance.rawGainSign='positive',x=>x.performance.possibleGain.lower=x.performance.rawGain,x=>x.certificate.responseOptimalityGap=ZERO,x=>x.performance.relativeGain=ZERO,x=>x.response.coverage.B.discounted.unvisitedStateExposure=r(21n,20n),x=>x.performance.cycleCustomerBenefitDifference=ZERO]){const x=structuredClone(neg);mutate(x);assert.throws(()=>validateAvailableRecord(x));}
});
test('all labels, paired seller means and controller differences retain a failed seed without imputation',()=>{
 const records=[];for(const seed of [1,2])for(const controller of ['startup-only','selected95'])for(const focal of ['A','B'])records.push(record(seed,controller,focal,{response:controller==='selected95'?14n:11n,upper:15n}));
 const all=summarizeRecords(records,{seeds:[1,2]});assert.deepEqual(all.pairedDifferences.map(x=>x.difference),[r(3n),r(3n)]);assert.equal(all.seedMeans.length,4);assert.equal(all.controllerSummaries[0].rawGainSignCounts.positive,4);
 const failed=structuredClone(records);failed[5]={...failed[5],certificate:null,performance:null,baseline:null,response:null,status:'budget failure',executionSucceeded:false,scientificAvailable:false,failure:{message:'Artificial hard-budget termination'}};
 const result=summarizeRecords(failed,{seeds:[1,2]});assert.equal(result.seedMeans.find(x=>x.seed===2&&x.controller==='startup-only').meanRawGain,null);assert.equal(result.pairedDifferences[1].difference,null);assert.equal(result.controllerSummaries[0].unavailable,1);
 assert.throws(()=>summarizeRecords(records.slice(1),{seeds:[1,2]}));const wrong=structuredClone(records);[wrong[0],wrong[1]]=[wrong[1],wrong[0]];assert.throws(()=>summarizeRecords(wrong,{seeds:[1,2]}));
 const fullyReceived=structuredClone(records);fullyReceived[0].executionSucceeded=false;fullyReceived[0].status='budget failure after complete certificate';fullyReceived[0].failure={message:'Artificial late termination'};
 const kept=summarizeRecords(fullyReceived,{seeds:[1,2]});assert.equal(kept.controllerSummaries[0].available,4);assert.equal(kept.controllerSummaries[0].executionSucceeded,3);assert.deepEqual(kept.pairedDifferences[0].difference,r(3n));
});
