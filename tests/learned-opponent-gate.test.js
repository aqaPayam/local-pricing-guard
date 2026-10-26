import test from 'node:test';import assert from 'node:assert/strict';
import {analyzeEvidence,jsonBytes} from '../research/learned-opponent-analysis.js';
import {buildWebEvidence} from '../research/build-learned-opponent-web.js';
import {evidenceFixture} from './helpers/learned-opponent-evidence-fixture.js';
const P='research/learned-opponent-results';
test('complete artificial closure derives all48 rows and24 checked checkpoints without Q floats in web payload',()=>{
 const f=evidenceFixture(),summary=analyzeEvidence(f.io);f.put(P+'/summary.json',jsonBytes(summary));const web=buildWebEvidence(f.io);
 assert.equal(web.records.length,48);assert.equal(web.webgameData.checkpointCases.length,24);assert.equal(web.webgameData.responsePolicies.length,48);assert.equal(web.meta.counts.scientificallyAvailable,48);assert.equal(web.webgameData.checkpointCases.every(x=>x.available),true);assert.equal(web.records[0].performance.rawGainSign,'zero');assert.equal(web.meta.defaultSelection.seed,907001);
 assert.equal('q' in web.webgameData.checkpointCases[0],false);assert.equal(web.webgameData.checkpointCases[0].trainingCounts.A.reduce((a,b)=>a+b,0),2000000);
});
test('honest retained unavailable label can pass independent inventory yet cannot become a zero-valued response',()=>{
 const f=evidenceFixture({unavailableIndices:[0]}),summary=analyzeEvidence(f.io);f.put(P+'/summary.json',jsonBytes(summary));const web=buildWebEvidence(f.io);
 assert.equal(summary.meta.primaryExecutionPassed,false);assert.equal(summary.meta.counts.unavailable,1);assert.equal(summary.records[0].display.rawGain,null);assert.equal(summary.pairedDifferences[0].difference,null);assert.equal(web.webgameData.responsePolicies[0].actions,null);assert.equal(web.meta.defaultSelection.focal,'A');
 const both=evidenceFixture({unavailableIndices:[0,1]}),bothSummary=analyzeEvidence(both.io);both.put(P+'/summary.json',jsonBytes(bothSummary));const locked=buildWebEvidence(both.io);assert.equal(locked.webgameData.checkpointCases[0].available,false);assert.match(locked.webgameData.checkpointCases[0].reason,/Both focal/);
 const none=evidenceFixture({unavailableIndices:Array.from({length:48},(_,i)=>i),mutateAudit:a=>a.corruptionNegativeControls={}}),noneSummary=analyzeEvidence(none.io);none.put(P+'/summary.json',jsonBytes(noneSummary));const noScience=buildWebEvidence(none.io);assert.equal(noScience.meta.audit.actualScientificNegativeControlsAvailable,false);assert.equal(noScience.meta.counts.scientificallyAvailable,0);assert.ok(noScience.webgameData.checkpointCases.every(c=>!c.available));
});
test('current audit/output/source bindings and independent exact summaries reject in-memory corruptions',()=>{
 for(const mutate of [a=>a.passed=false,a=>a.fullTrainingReplay=true,a=>a.resultsSha256='0'.repeat(64),a=>a.certifiedRecords=47,a=>a.independentSummaries.seedMeans[0].meanRawGain={numeratorHex:'0x1',denominatorHex:'0x1'}])assert.throws(()=>analyzeEvidence(evidenceFixture({mutateAudit:mutate}).io));
 const f=evidenceFixture();f.files.set('research/run-learned-opponent.py',Buffer.from('ARTIFICIAL changed supervisor'));assert.throws(()=>analyzeEvidence(f.io));
 const bad=evidenceFixture({mutateRecords:rows=>rows[0].performance.rawGainSign='positive'});assert.throws(()=>analyzeEvidence(bad.io));
});
test('manually edited summary, artifact byte and false complete-reception chronology cannot pass export',()=>{
 const f=evidenceFixture(),s=analyzeEvidence(f.io);s.records[0].display.rawGainSign='positive';f.put(P+'/summary.json',jsonBytes(s));assert.throws(()=>buildWebEvidence(f.io),/summary differs/);
 const changed=evidenceFixture();changed.files.set(P+'/artifacts/'+changed.records[0].id+'/response.u8',Buffer.from([1,1]));assert.throws(()=>analyzeEvidence(changed.io));
 const late=evidenceFixture({mutateRecords:rows=>rows[0].runtime.receivedCompleteMilliseconds=30});assert.throws(()=>analyzeEvidence(late.io),/before termination/);
 const tied=evidenceFixture({mutateRecords:rows=>{rows[0].runtime.receivedCompleteMilliseconds=20;rows[0].runtime.events[0].elapsedMilliseconds=20;}});assert.equal(analyzeEvidence(tied.io).records[0].scientificAvailable,true);
 const reordered=evidenceFixture({mutateRecords:rows=>rows[0].runtime.events.reverse()});assert.throws(()=>analyzeEvidence(reordered.io),/before termination/);
});
