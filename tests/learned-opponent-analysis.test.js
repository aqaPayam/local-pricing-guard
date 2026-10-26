import test from 'node:test';import assert from 'node:assert/strict';
import {deriveSummary,presentRecord,resultsText,defaultSelection} from '../research/learned-opponent-analysis.js';
import {plannedRecords,record,r} from './helpers/learned-opponent-fixture.js';
test('artificial complete matrix preserves scientific records and fixed presentation default',()=>{
 const records=plannedRecords(),before=structuredClone(records),summary=deriveSummary(records,{independentAuditPassed:true,primaryExecutionPassed:true});
 assert.deepEqual(records,before);assert.equal(summary.records.length,48);assert.equal(summary.seedMeans.length,24);assert.equal(summary.pairedDifferences.length,12);
 assert.deepEqual(summary.pairedDifferences.map(x=>x.difference),Array(12).fill(r(2n)));assert.deepEqual(defaultSelection,{seed:907001,controller:'startup-only',focal:'A',chosenBeforeOutcomeInspection:true,scope:'Presentation choice before new strategic outcomes, not a scientific factor or whole-project preregistration; retain even if zero, negative or unavailable.'});
 for(let i=0;i<records.length;i++){const {display,...source}=summary.records[i];assert.deepEqual(source,records[i]);assert.equal(display.rawGain.sign,'positive');}
 assert.equal(summary.meta.optimizerIterationsReplayed,false);assert.equal(summary.meta.fullTrainingReplay,false);assert.match(resultsText(summary),/No bootstrap, CI, p-value/);
});
test('derivation rejects absent independent acceptance and changed fixed stratum or clock',()=>{
 assert.throws(()=>deriveSummary(plannedRecords(),{independentAuditPassed:false}));
 for(const mutate of [r=>r.scenario='other',r=>r.initialization='optimistic',r=>r.checkpointStep=1000000,r=>r.control.period=5]){const rows=plannedRecords();mutate(rows[2]);assert.throws(()=>deriveSummary(rows,{independentAuditPassed:true}));}
});
test('retained unavailable default has null display while valid budget-result remains in seed means',()=>{
 const rows=plannedRecords();rows[0]={...rows[0],executionSucceeded:false,scientificAvailable:false,status:'budget failure',failure:{message:'Artificial incomplete certificate'},certificate:null,baseline:null,response:null,performance:null};
 rows[2].executionSucceeded=false;rows[2].status='budget failure after complete scientific receipt';rows[2].failure={message:'Artificial late termination'};
 const summary=deriveSummary(rows,{independentAuditPassed:true,primaryExecutionPassed:false});assert.equal(summary.meta.defaultSelection.seed,907001);assert.equal(summary.records[0].display.rawGain,null);assert.match(summary.records[0].display.unavailableReason,/incomplete certificate/);assert.equal(summary.seedMeans.find(x=>x.seed===907001&&x.controller==='startup-only').meanRawGain,null);assert.deepEqual(summary.seedMeans.find(x=>x.seed===907001&&x.controller==='selected95').meanRawGain,r(3n));assert.equal(summary.pairedDifferences[0].difference,null);
 assert.equal(presentRecord(record(1,'startup-only','A',{baseline:0n,response:0n,upper:1n})).display.rawGainSign,'zero');
});
