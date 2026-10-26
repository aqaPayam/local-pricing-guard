// Entirely artificial in-memory evidence; no market files are read.
import test from 'node:test';import assert from 'node:assert/strict';
import {analyzeEvidence,resultsText} from '../research/mixed-timing-analysis.js';
import {fixture,q,prefix} from './helpers/mixed-timing-fixture.js';
test('complete artificial40/80 inventory preserves zero boundaries, duplicates and raw finite tables',()=>{
 const f=fixture(),s=analyzeEvidence(f.io);assert.equal(s.models.length,24);assert.equal(s.targetRows.length,120);assert.equal(s.finiteGames.length,8);
 assert.equal(s.meta.populationCounts.finite.targetLabels,40);assert.equal(s.meta.populationCounts.continuous.targetLabels,80);assert.equal(s.meta.duplicateCounts.finite,32);
 assert.equal(s.meta.defaultSelection.scenario,'base-g15-t1');assert.equal(s.meta.defaultSelection.target,'cap-95pct');assert.equal(s.meta.executionPassed,true);
 assert.equal(s.models[0].targets[0].rates.constructedRateExact.numerator,'0');assert.equal(s.models[0].targets[0].rates.bestFixedK,null);
 assert.match(resultsText(s),/All 80 continuous labels/);assert.equal(f.files.has(prefix+'summary.json'),false);
});
test('authoritative audit gate rejects JS components and does not read later evidence',()=>{
 for(const change of [a=>{a.passed=false;a.componentPassed=true;a.requiresOrchestrator=true;},a=>{a.requiresOrchestrator=true;},a=>{a.continuousChecksComputedInProcess=false;}]){
  const f=fixture(()=>{},change);assert.throws(()=>analyzeEvidence(f.io),/authoritative/);assert.deepEqual(f.reads,[prefix+'independent-audit.json']);
 }
 const f=fixture(()=>{},a=>{a.auditorSourceHash=a.controlAuditorSourceHash;});assert.throws(()=>analyzeEvidence(f.io),/source binding/);
});
test('recomputed fixture hashes do not hide missing labels, wrong signs, duplicate or payoff defects',()=>{
 const cases=[
  c=>c.records[0].targets.pop(),
  c=>{c.records[0].targets[1].duplicateOf=null;},
  c=>{c.records[0].targets[0].status='guessed safe optimum';},
  c=>{c.records[0].targets[0].rates.constructedRateExact=q(1);},
  c=>{const r=c.records[0].targets[0].rates;r.absoluteSavingBoundsExact={lower:q(1),upper:q(2)};r.absoluteSavingSigns={lower:'zero',upper:'positive'};},
  c=>{c.records[0].targets[0].frontier.queryLengths=[65537];},
  c=>{c.games[0].finite.rewards.profitA.pop();},
  c=>{c.games[0].cap.price=2;},
  c=>{c.games[0].finite.sets[0]=[];},
  c=>{c.journalDrop=true;},
  c=>{c.finalDependenciesPassed=false;}
 ];for(const change of cases)assert.throws(()=>analyzeEvidence(fixture(change).io));
});
test('honestly audited calculation failures remain complete and never acquire zero rates',()=>{
 const f=fixture(c=>{const r=c.records[0];r.status='unresolved model identity';r.calculationFailures=5;
  for(const t of r.targets){t.status='unresolved calculation or identity';t.actualThresholdExact=null;t.identity=null;t.duplicateOf=null;t.rates=null;t.calendar={kind:'unavailable',blockPreview64:[]};t.error='ARTIFICIAL retained identity failure';}
 });const s=analyzeEvidence(f.io);assert.equal(s.meta.independentAuditPassed,true);assert.equal(s.meta.executionPassed,false);assert.equal(s.targetRows.length,120);
 assert.equal(s.meta.statusCounts.finite.categories['calculation-or-identity-failure'],5);assert.ok(s.models[0].targets.every(t=>t.rates===null&&t.display.rate===null&&t.error));
});
