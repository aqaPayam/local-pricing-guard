import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mount,boot,validateEvidence,formatAmount,basketGraphic} from '../research/demo/reference.js';
import {referenceFixture} from './helpers/guard-reference-web-fixture.js';
class Element{constructor(){this.textContent='';this.innerHTML='';this.hidden=true;this.disabled=false;this.value='';this.events={};}addEventListener(name,fn){this.events[name]=fn;}dispatch(name){return this.events[name]?.({preventDefault(){}});}}
function docFixture(){const html=fs.readFileSync(new URL('../research/demo/reference.html',import.meta.url),'utf8'),nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));return{html,getElementById:id=>nodes.get(id)??null};}
test('invented complete reference mounts all signed pairs, distinct status scopes and static ties without unearned rewards',()=>{
 const data=referenceFixture(),doc=docFixture(),view=mount(data,doc);assert.equal(validateEvidence(data),data);assert.equal(view.replay.snapshot().executions,0);
 assert.equal(doc.getElementById('startup-guard-latest').textContent,'—');assert.match(doc.getElementById('full-grid-after-cap-shops').innerHTML,/Saved memory · unearned/);
 assert.equal((doc.getElementById('paired-table').innerHTML.match(/<tr>/g)??[]).length,13);
 assert.equal((doc.getElementById('checkpoint-table').innerHTML.match(/<tr>/g)??[]).length,38);
 assert.match(doc.getElementById('paired-chart').innerHTML,/#9a4b4b/);assert.match(doc.getElementById('paired-chart').innerHTML,/#777165/);
 assert.match(doc.getElementById('anchor-status').textContent,/1 static pure Nash pairs; 2 exact joint-profit maximizing pairs/);
 assert.equal((doc.getElementById('anchor-table').innerHTML.match(/<tr>/g)??[]).length,5);
 assert.match(doc.getElementById('startup-guard-rule').textContent,/Guard stays on/);assert.match(doc.getElementById('full-grid-after-cap-rule').textContent,/any price on the original board/);
 assert.match(doc.html,/You control the playback\. The saved shops choose their prices/);
 assert.match(doc.html,/id="run-one"[^>]*>Watch both: 1 round<\/button>/);assert.match(doc.html,/id="mobile-advance"[^>]*>Watch both: 1 round<\/button>/);
 assert.match(doc.html,/Positive: removing the guard helped customers\. Negative: keeping the guard helped customers/);
 assert.match(doc.getElementById('seed').innerHTML,/Example 1 of 12/);assert.match(doc.getElementById('endpoint-details').textContent,/NEXT phase4/);
});
test('all twelve seed controls and mobile controls advance both frozen worlds with no new caps, undo and restart exactly',()=>{
 const data=referenceFixture(),doc=docFixture(),view=mount(data,doc);
 for(const seed of data.orderedSeeds){view.select(seed);const initial=view.replay.snapshot();doc.getElementById('mobile-advance').dispatch('click');assert.equal(view.replay.snapshot().executions,1);assert.equal(view.replay.snapshot().treatments['full-grid-after-cap'].capExecutions,0);assert.match(doc.getElementById('prefix-chart').innerHTML,/<circle/);assert.match(doc.getElementById('prefix-chart').innerHTML,/<rect x="86"/);doc.getElementById('mobile-undo').dispatch('click');assert.deepEqual(view.replay.snapshot(),initial);assert.match(doc.getElementById('feedback').textContent,/Undid 1 round in both versions/);assert.equal(doc.getElementById('mobile-undo').disabled,true);doc.getElementById('run-twenty').dispatch('click');assert.equal(view.replay.snapshot().executions,20);doc.getElementById('undo').dispatch('click');assert.equal(view.replay.snapshot().executions,19);assert.match(doc.getElementById('feedback').textContent,/Undid 1 round in both versions/);doc.getElementById('restart').dispatch('click');assert.deepEqual(view.replay.snapshot(),initial);}
});
test('rejected secondary is retained while complete accepted finals and the planned mean remain available',()=>{
 const d=referenceFixture(),c=d.checkpointStatuses[0];Object.assign(c,{scientificAvailable:false,status:'rejected',reason:'Invented retained secondary failure'});d.meta.fullTrainingReplay=false;d.meta.replayComplete=false;
 const doc=docFixture(),v=mount(d,doc);assert.equal(v.replay.snapshot().available,true);assert.equal(d.primarySummary.available,true);assert.match(doc.getElementById('checkpoint-table').innerHTML,/retained secondary failure/);assert.match(doc.getElementById('replay-scope').textContent,/not claimed/);
});
test('missing final locks the selected pair and nulls the planned mean while other seed pairs remain selectable',()=>{
 const d=referenceFixture(),p=d.finalPolicies.find(p=>p.seed===907001&&p.treatment==='full-grid-after-cap');Object.assign(p,{available:false,reason:'Invented missing final',policies:null,cycleMetrics:null});
 Object.assign(d.checkpointStatuses.find(c=>c.seed===907001&&c.step===2000000),{scientificAvailable:false,status:'failed',reason:p.reason});Object.assign(d.pairedRows[0],{available:false,difference:null,unavailableReason:p.reason});d.pairedRows[0].cycleCustomerBenefits[1]=null;
 Object.assign(d.primarySummary,{available:false,availablePairs:11,meanDifference:null,unavailableReason:p.reason});d.completePairDescription.denominator=11;d.completePairDescription.seedIds.shift();d.meta.fullTrainingReplay=false;d.meta.replayComplete=false;
 const doc=docFixture(),v=mount(d,doc);assert.equal(v.replay.snapshot().available,false);assert.equal(doc.getElementById('mobile-advance').disabled,true);assert.equal(doc.getElementById('primary-mean').textContent,'Unavailable');assert.equal(doc.getElementById('full-grid-after-cap-latest').textContent,'—');v.select(907002);assert.equal(v.replay.snapshot().available,true);
});
test('malformed treatment/anchors/identities lock before rendering; offline branch and tiny signed values stay distinct',async()=>{
 for(const mutate of [d=>d.meta.inventoryAccepted=false,d=>d.finalPolicies[1].scientificTreatment.supportMode='startup-guard',d=>d.pairedRows.reverse(),d=>d.primarySummary.availablePairs=11,d=>d.anchors.values.jointProfitMaximum.pairs[0].profits.joint.numerator='999',d=>d.checkpointStatuses.pop(),d=>d.meta.defaultSelection.chosenBeforeReferenceOutcomeInspection=false]){const d=referenceFixture();mutate(d);const doc=docFixture();await boot(doc,async()=>({ok:true,json:async()=>d}));assert.equal(doc.getElementById('reference-app').hidden,true);assert.equal(doc.getElementById('mobile-advance').disabled,true);assert.match(doc.getElementById('load-status').textContent,/locked/);}
 const doc=docFixture();await boot(doc,async()=>({ok:false}));assert.match(doc.getElementById('load-status').textContent,/No example/);assert.equal(formatAmount(null),'—');assert.equal(formatAmount({numerator:'0',denominator:'1'}),'0');assert.match(formatAmount({numerator:'-1',denominator:'1'+'0'.repeat(500)}),/-1\.000e-500/);assert.match(basketGraphic(65,'invented'),/height="7"/);
});
