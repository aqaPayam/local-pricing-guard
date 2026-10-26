import test from 'node:test';import assert from 'node:assert/strict';
import {fixture,prefix} from './helpers/mixed-timing-fixture.js';
import {analyzeEvidence} from '../research/mixed-timing-analysis.js';
import {buildWebEvidence} from '../research/build-mixed-timing-web.js';
function prepared(){const f=fixture(),s=analyzeEvidence(f.io);f.files.set(prefix+'summary.json',Buffer.from(JSON.stringify(s)+'\n'));f.files.set('research/build-mixed-timing-web.js',Buffer.from('ARTIFICIAL EXPORTER SOURCE'));return f;}
test('pure compact export faithfully retains24 artificial models/120 labels and8 full finite games',()=>{
 const f=prepared(),before=new Map([...f.files].map(([k,v])=>[k,Buffer.from(v)])),data=buildWebEvidence(f.io);
 assert.equal(data.models.length,24);assert.equal(data.models.flatMap(m=>m.targets).length,120);assert.equal(data.finiteGames.length,8);assert.equal(data.meta.primaryAudit.requiresOrchestrator,false);
 assert.equal(data.models[0].targets[0].rates.constructedRateExact.numerator,'0');assert.equal(data.models[0].targets[0].rates.bestFixedK,null);
 for(const [name,bytes]of before)assert.deepEqual(f.files.get(name),bytes);assert.equal(f.files.size,before.size);
});
test('edited compact summaries cannot pass by retaining original source/input hashes',()=>{
 for(const change of [s=>{s.models[0].targets[0].status='certified largest fabricated gain';},s=>{s.meta.populationCounts.finite.targetLabels=39;},s=>{s.finiteGames[0].finite.prices[0]=0;}]){
  const f=prepared(),summary=JSON.parse(f.files.get(prefix+'summary.json'));change(summary);f.files.set(prefix+'summary.json',Buffer.from(JSON.stringify(summary)+'\n'));
  assert.throws(()=>buildWebEvidence(f.io),/raw-evidence regeneration/);
 }
});
test('post-summary primary/completion/source corruption is blocked before export',()=>{
 for(const file of [prefix+'results.json',prefix+'completion.json','research/audit-mixed-study.py',prefix+'sources/research/fake-primary.py']){
  const f=prepared();f.files.set(file,Buffer.concat([f.files.get(file),Buffer.from(' ')]));assert.throws(()=>buildWebEvidence(f.io));
 }
});
test('optional closed archive verification does not create a nested-archive dependency or change portable bytes',()=>{
 const f=prepared(),without=buildWebEvidence(f.io);f.io.exists=name=>name==='output/ARTIFICIAL-v9.zip';
 const withArchive=buildWebEvidence(f.io);assert.deepEqual(withArchive,without);
 assert.equal(Object.hasOwn(analyzeEvidence(f.io).inputHashes,'output/ARTIFICIAL-v9.zip'),false);
 f.files.set('output/ARTIFICIAL-v9.zip',Buffer.from('CORRUPTED OPTIONAL ARCHIVE'));assert.throws(()=>buildWebEvidence(f.io),/Available V9 archive differs/);
});
