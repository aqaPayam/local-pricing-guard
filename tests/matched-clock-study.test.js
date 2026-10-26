import test from 'node:test';
import assert from 'node:assert/strict';
import {manifestClosure,sourceClosure,runtimeFingerprint,plannedRuns,checkPriorPayload,moduleSpecifiers} from '../research/matched-clock-study.js';
import {jsonBytes,sha} from '../research/matched-clock-io.js';
const store=entries=>{const files=new Map(Object.entries(entries).map(([k,v])=>[k,Buffer.isBuffer(v)?v:jsonBytes(v)]));return{readBytes:k=>{assert.ok(files.has(k),k);return files.get(k);},exists:k=>files.has(k)};};
test('legacy hash closure binds all recognized aliases and rejects malformed maps even alongside a valid map',()=>{
 const a=Buffer.from('old source'),b=Buffer.from('old input'),tree=store({'old/manifest.json':{sources:{'old/source.js':sha(a)},hashes:{'old/input.bin':sha(b)}},'old/source.js':a,'old/input.bin':b});
 assert.deepEqual(manifestClosure(['old/manifest.json'],tree),{'old/manifest.json':sha(tree.readBytes('old/manifest.json')),'old/source.js':sha(a),'old/input.bin':sha(b)});
 for(const bad of [[],null,7,'wrong'])assert.throws(()=>manifestClosure(['old/manifest.json'],store({'old/manifest.json':{sourceHashes:{},inputHashes:bad}})));
 assert.throws(()=>manifestClosure(['old/manifest.json'],store({'old/manifest.json':{sourceHashes:{'old/input.bin':sha(b)},hashes:{'old/input.bin':'0'.repeat(64)}},'old/input.bin':b})));
});
test('relative source import closure retains transitive modules without performing module IO',()=>{
 const io=store({'src/a.js':Buffer.from("import {b} from './b.js';"),'src/b.js':Buffer.from("import './c.js';"),'src/c.js':Buffer.from('export const b=1;')});assert.deepEqual(Object.keys(sourceClosure(['src/a.js'],io)),['src/a.js','src/b.js','src/c.js']);
});
test('module closure ignores quoted/commented/regex/template fixture imports but retains static and literal dynamic imports',()=>{
 const code=["import {x} from './real.js'; import './same-line.js';",'const fixture="import {b} from \'./fake.js\';";',"// import './comment.js';",'const template=`import "./template.js"`;','const pattern=/import [\'\"](.+)[\'\"]/g;',"export {x} from './export.js';", "await import('./dynamic.js');", "const value={import:'./property.js'};"].join('\n');
 assert.deepEqual(moduleSpecifiers(code),['./real.js','./same-line.js','./export.js','./dynamic.js']);
});
test('runtime backend equality excludes executable location but retains hash versions OS and flags',()=>{
 const one={executablePath:'C:/one/node.exe',executableSha256:'a'.repeat(64),node:'v24',v8:'same',platform:'win32',architecture:'x64',osRelease:'fixed',execArgv:[]},two={...one,executablePath:'C:/copy/node.exe'};assert.deepEqual(runtimeFingerprint(one),runtimeFingerprint(two));assert.notDeepEqual(runtimeFingerprint(one),runtimeFingerprint({...two,v8:'different'}));assert.throws(()=>runtimeFingerprint({}));
});
test('full24 paired identities share exact actor namespaces but remain distinct run identities',()=>{
 const plan=plannedRuns();assert.equal(plan.length,24);assert.equal(new Set(plan.map(p=>p.id)).size,24);for(let i=0;i<24;i+=2){assert.equal(plan[i].seed,907001+i/2);assert.deepEqual(plan[i].actors,plan[i+1].actors);assert.equal(plan[i].arm,'startup');assert.equal(plan[i+1].arm,'recurring4');}
});
function anchorFixture(){
 const input=Buffer.from('invented saved finite input'),source=Buffer.from('invented old scientific source'),plan=jsonBytes({files:{'old/input.bin':{sha256:sha(input),bytes:input.length},'old/source.js':{sha256:sha(source),bytes:source.length}}}),receipt=jsonBytes({sha256:'f'.repeat(64),prospectiveInventorySha256:sha(plan),verification:{passed:true}}),anchor={planFile:'old/plan.json',planSha256:sha(plan),receiptFile:'old/receipt.json',receiptSha256:sha(receipt),archiveSha256:'f'.repeat(64)},entries={'old/input.bin':input,'old/source.js':source,'old/plan.json':plan,'old/receipt.json':receipt};return{input,source,anchor,entries,inputs:{'old/input.bin':sha(input)},sources:{'old/source.js':sha(source),'new/source.js':'a'.repeat(64)}};
}
test('fixed earlier payload metadata anchors old input and imported source without loading archive or Q',()=>{
 const f=anchorFixture(),r=checkPriorPayload(f.inputs,f.sources,store(f.entries),f.anchor);assert.equal(r.payloadIdentitiesChecked,2);assert.equal(r.archiveSha256,'f'.repeat(64));
 const changed=Buffer.from('self-consistently changed old input');assert.throws(()=>checkPriorPayload({'old/input.bin':sha(changed)},f.sources,store({...f.entries,'old/input.bin':changed}),f.anchor));
 assert.throws(()=>checkPriorPayload(f.inputs,{'old/source.js':'0'.repeat(64)},store(f.entries),f.anchor));
 assert.throws(()=>checkPriorPayload({...f.inputs,'not/in/plan':'0'.repeat(64)},f.sources,store(f.entries),f.anchor));
});
test('earlier payload anchor rejects edited plan, false receipt and wrong archive binding',()=>{
 const f=anchorFixture();assert.throws(()=>checkPriorPayload(f.inputs,f.sources,store({...f.entries,'old/plan.json':jsonBytes({files:{}})}),f.anchor));
 for(const patch of [{verification:{passed:false}},{sha256:'0'.repeat(64)},{prospectiveInventorySha256:'0'.repeat(64)}]){
  const value={...JSON.parse(f.entries['old/receipt.json']),...patch},bytes=jsonBytes(value);assert.throws(()=>checkPriorPayload(f.inputs,f.sources,store({...f.entries,'old/receipt.json':bytes}),{...f.anchor,receiptSha256:sha(bytes)}));
 }
});
