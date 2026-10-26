// Manifest/identity administration. No input reads, freeze or training on import.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {actorNamespaces} from './matched-clock-learning.js';
import {local,sha,save,jsonBytes} from './matched-clock-io.js';
export const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const need=(v,m)=>{if(!v)throw Error(m);};
export const V11_ANCHOR={planFile:'output/learned-opponent-package-plan.json',planSha256:'85260f459d4d02d586dc12af8b3e24f7abda64f0e555bbc4275d46d25e8a198f',receiptFile:'output/learned-opponent-package-verification.json',receiptSha256:'af26e009bb754f54bc9963ff8e4a2e44255dd5010279e68d4c26430cb57f43a8',archiveSha256:'7544aab654822b5444f966b24ea8e985d973e04562422ff9d1c26bc44b9c9885'};
export const SOURCE_FILES=[
 'research/MATCHED_CLOCK_PROTOCOL.md','research/MATCHED_CLOCK_ANALYSIS_CONTRACT.md',
 'research/MATCHED_CLOCK_PROSPECTIVE_REVIEW.md','research/MATCHED_CLOCK_ROOT_REVIEW.md','research/MATCHED_CLOCK_PEER_REVIEW.md','research/matched-clock-analysis.py','tests/test_matched_clock_analysis.py',
 'research/matched-clock-learning.js','research/matched-clock-graph.js','research/matched-clock-io.js','research/matched-clock-study.js','research/matched-clock-case.js','research/run-matched-clock.py',
 'research/benchmark-matched-clock.py','tests/test_matched_clock_benchmark.py',
 'research/audit-matched-clock.js','research/replay-matched-clock.js','research/audit-matched-clock-study.py','tests/test_matched_clock_inventory_audit.py',
 'tests/matched-clock-learning.test.js','tests/matched-clock-graph.test.js','tests/matched-clock-io.test.js','tests/matched-clock-study.test.js','tests/test_matched_clock_supervisor.py','tests/matched-clock-audit.test.js','tests/matched-clock-root-cross.test.js','tests/matched-clock-cross-audit.test.js','tests/matched-clock-serialization-audit.test.js'
];
export function plannedRuns(){return actorNamespaces().flatMap(({seed,actors,segments})=>['startup','recurring4'].map(arm=>({id:`base-g15-t1--matched5-${arm}--zero--s${seed}`,scenario:'base-g15-t1',arm,seed,initialization:'positive-zero',actors:actors.map(a=>a.slice()),segments:segments.slice()})));}
export function runtimeIdentity(){return{executablePath:process.execPath,executableSha256:sha(fs.readFileSync(process.execPath)),node:process.version,v8:process.versions.v8,platform:process.platform,architecture:process.arch,osRelease:os.release(),execArgv:process.execArgv.slice()};}
export function runtimeFingerprint(identity){return Object.fromEntries(['executableSha256','node','v8','platform','architecture','osRelease','execArgv'].map(k=>{need(Object.hasOwn(identity,k),'Missing runtime backend identity '+k);return[k,identity[k]];}));}
export function manifestClosure(seedFiles,{readBytes,exists}){
 const hashes={},queue=[...seedFiles],seen=new Set();
 const use=(name,expected)=>{local(ROOT,name);need(exists(name),'Missing inherited dependency '+name);const bytes=readBytes(name),h=sha(bytes);need(!expected||h===expected,'Inherited declared hash differs '+name);need(!hashes[name]||hashes[name]===h,'Conflicting inherited identity '+name);hashes[name]=h;return bytes;};
 while(queue.length){const file=queue.shift();if(seen.has(file))continue;seen.add(file);const bytes=use(file);if(!file.endsWith('/manifest.json'))continue;
  const m=JSON.parse(bytes),groups=['sourceHashes','inputHashes','hashes','sources'];need(groups.some(k=>Object.hasOwn(m,k)),'Inherited manifest has no recognized hash map '+file);
  for(const k of groups)if(Object.hasOwn(m,k))need(m[k]!==null&&typeof m[k]==='object'&&!Array.isArray(m[k]),'Malformed recognized identity map '+file+' '+k);
  for(const key of ['sourceHashes','inputHashes','hashes','sources'])for(const [name,value] of Object.entries(m[key]??{})){
   const h=typeof value==='string'?value:value?.sha256;need(/^[a-f0-9]{64}$/.test(h),'Malformed legacy identity '+file+' '+name);use(name,h);if(name.endsWith('/manifest.json'))queue.push(name);
  }
 }
 return hashes;
}
export function moduleSpecifiers(text){
 // Lex strings/comments/regex/template fixtures before finding actual import
 // tokens. A regex over raw test sources confuses quoted examples with modules.
 const tokens=[];let i=0;
 while(i<text.length){
  const c=text[i];if(/\s/.test(c)){i++;continue;}
  if(c==='/'&&text[i+1]==='/'){i+=2;while(i<text.length&&text[i]!=='\n')i++;continue;}
  if(c==='/'&&text[i+1]==='*'){const end=text.indexOf('*/',i+2);need(end>=0,'Unclosed source comment');i=end+2;continue;}
  if(c==='"'||c==="'"){
   const quote=c;let value='';i++;let closed=false;
   while(i<text.length){let a=text[i++];if(a===quote){closed=true;break;}if(a==='\\'){
    need(i<text.length,'Unclosed source escape');a=text[i++];
    if(a==='\n')continue;if(a==='\r'){if(text[i]==='\n')i++;continue;}
    if(a==='x'||a==='u'){
     let digits;if(a==='u'&&text[i]==='{'){const end=text.indexOf('}',i+1);need(end>=0,'Unclosed unicode escape');digits=text.slice(i+1,end);i=end+1;}else{const n=a==='x'?2:4;digits=text.slice(i,i+n);i+=n;}
     need(/^[0-9a-f]+$/i.test(digits),'Invalid source hex escape');value+=String.fromCodePoint(parseInt(digits,16));continue;
    }
    a=({n:'\n',r:'\r',t:'\t',b:'\b',f:'\f',v:'\v','0':'\0'})[a]??a;
   }value+=a;}
   need(closed,'Unclosed source string');tokens.push({type:'string',value});continue;
  }
  if(c==='`'){
   i++;let closed=false;while(i<text.length){const a=text[i++];if(a==='\\'){i++;continue;}if(a==='`'){closed=true;break;}}need(closed,'Unclosed source template');tokens.push({type:'template',value:''});continue;
  }
  const previous=tokens.at(-1),regexStart=!previous||previous.type==='punct'&&'=([{,:;?!~&|+-*%^<>'.includes(previous.value)||previous.type==='word'&&['return','case','throw','typeof','void','yield','await','in','of','else','do'].includes(previous.value);
  if(c==='/'&&regexStart){
   i++;let bracket=false,closed=false;while(i<text.length){const a=text[i++];if(a==='\\'){i++;continue;}if(a==='[')bracket=true;if(a===']')bracket=false;if(a==='/'&&!bracket){closed=true;break;}}need(closed,'Unclosed source regex');while(/[a-z]/i.test(text[i]??'')&&i<text.length)i++;tokens.push({type:'regex',value:''});continue;
  }
  if(/[a-z_$]/i.test(c)){const start=i++;while(i<text.length&&/[a-z0-9_$]/i.test(text[i]))i++;tokens.push({type:'word',value:text.slice(start,i)});continue;}
  tokens.push({type:'punct',value:c});i++;
 }
 const found=[];
 for(let k=0;k<tokens.length;k++){
  const t=tokens[k],next=tokens[k+1];if(t.type!=='word'||!['import','export'].includes(t.value)||tokens[k-1]?.value==='.')continue;
  if(t.value==='import'&&next?.type==='string'){found.push(next.value);continue;}
  if(t.value==='import'&&next?.value==='('&&tokens[k+2]?.type==='string'&&tokens[k+3]?.value===')'){found.push(tokens[k+2].value);continue;}
  if(t.value==='export'&&!['{','*'].includes(next?.value)||t.value==='import'&&!(next?.type==='word'||['{','*'].includes(next?.value)))continue;
  for(let j=k+1;j<tokens.length&&tokens[j].value!==';';j++)if(tokens[j].type==='word'&&tokens[j].value==='from'&&tokens[j+1]?.type==='string'){found.push(tokens[j+1].value);break;}
 }
 return found.filter(name=>name.startsWith('.'));
}
export function sourceClosure(seedFiles,{readBytes,exists}){
 const names=new Set(seedFiles),queue=[...seedFiles];
 while(queue.length){const file=queue.shift();need(exists(file),'Missing prospective source '+file);if(!file.endsWith('.js')&&!file.endsWith('.mjs'))continue;
  const text=readBytes(file).toString('utf8');for(const specifier of moduleSpecifiers(text)){
   const name=path.posix.normalize(path.posix.join(path.posix.dirname(file),specifier));local(ROOT,name);if(!names.has(name)){names.add(name);queue.push(name);}
  }
 }
 return Object.fromEntries([...names].sort().map(name=>[name,sha(readBytes(name))]));
}
export function checkPriorPayload(inputHashes,sourceHashes,{readBytes},anchor=V11_ANCHOR){
 const planBytes=readBytes(anchor.planFile),receiptBytes=readBytes(anchor.receiptFile);need(sha(planBytes)===anchor.planSha256&&sha(receiptBytes)===anchor.receiptSha256,'Accepted V11 plan/receipt anchor changed');
 const plan=JSON.parse(planBytes),receipt=JSON.parse(receiptBytes);need(receipt.sha256===anchor.archiveSha256&&receipt.prospectiveInventorySha256===anchor.planSha256&&receipt.verification?.passed===true,'Accepted V11 receipt does not bind fixed plan/archive');
 let checked=0;
 for(const[name,h]of Object.entries(inputHashes)){const row=plan.files?.[name];need(row&&row.sha256===h&&row.bytes===readBytes(name).length,'Inherited finite dependency differs from accepted V11 payload '+name);checked++;}
 for(const[name,h]of Object.entries(sourceHashes)){const row=plan.files?.[name];if(row){need(row.sha256===h&&row.bytes===readBytes(name).length,'Imported old scientific source differs from accepted V11 '+name);checked++;}}
 return{scope:'Accepted V11 payload identity metadata only; no archive or old Q read and no old numerical audit rerun',plan:{file:anchor.planFile,sha256:anchor.planSha256},receipt:{file:anchor.receiptFile,sha256:anchor.receiptSha256},archiveSha256:anchor.archiveSha256,payloadIdentitiesChecked:checked};
}
export function inventory({projectRoot=ROOT,sourceFiles=SOURCE_FILES,io=null}={}){
 const readBytes=io?.readBytes??(name=>fs.readFileSync(local(projectRoot,name))),exists=io?.exists??(name=>fs.existsSync(local(projectRoot,name))),json=name=>JSON.parse(readBytes(name));
 const base='research/sparse-display-results/',manifestFile=base+'manifest.json',indexFile=base+'index.json',auditFiles=[base+'independent-audit.json',base+'rational-audit.json'];
 const inputHashes=manifestClosure([manifestFile,indexFile,...auditFiles],{readBytes,exists}),manifestHash=sha(readBytes(manifestFile)),index=json(indexFile);
 need(index.manifestSha256===manifestHash,'Saved finite index/manifest identity differs');const matches=index.cases?.filter(c=>c.scenario==='base-g15-t1');need(matches?.length===1&&matches[0].status==='completed','Exact retained finite game absent');
 const finiteFile=base+matches[0].file,rawBytes=readBytes(finiteFile),raw=JSON.parse(rawBytes);need(sha(rawBytes)===matches[0].sha256&&raw.scenario?.id==='base-g15-t1'&&raw.finite?.prices?.length===62,'Original 62-quote game identity differs');inputHashes[finiteFile]=sha(rawBytes);
 for(let i=0;i<auditFiles.length;i++){const a=json(auditFiles[i]),source=i?'research/audit-sparse-reset.py':'research/audit-sparse-display.js';need(a.passed===true&&a.studyManifestHash===manifestHash&&a.indexSha256===sha(readBytes(indexFile))&&a.auditorSourceHash===sha(readBytes(source)),'Inherited full finite audit binding differs');inputHashes[source]=sha(readBytes(source));}
 const sourceHashes=sourceClosure(sourceFiles,{readBytes,exists}),priorDelivery=checkPriorPayload(inputHashes,sourceHashes,{readBytes});inputHashes[V11_ANCHOR.planFile]=V11_ANCHOR.planSha256;inputHashes[V11_ANCHOR.receiptFile]=V11_ANCHOR.receiptSha256;
 return{inputHashes,finiteGame:{file:finiteFile,bytes:rawBytes.length,sha256:sha(rawBytes)},sourceHashes,priorDelivery,runtime:runtimeIdentity(),runs:plannedRuns()};
}
export function freeze(directory,{projectRoot=ROOT,sourceFiles=SOURCE_FILES,benchmarkFile,pythonRuntimeFile}={}){
 need(typeof benchmarkFile==='string','Final source-bound maximal artificial benchmark is mandatory before freeze');
 need(typeof pythonRuntimeFile==='string','Explicit Python/zlib parent-runtime receipt required before freeze');
 const parentBytes=fs.readFileSync(local(projectRoot,pythonRuntimeFile)),parentRuntime=JSON.parse(parentBytes);
 need(/^[a-f0-9]{64}$/.test(parentRuntime.executableSha256)&&typeof parentRuntime.pythonVersion==='string'&&typeof parentRuntime.implementation==='string'&&typeof parentRuntime.zlibCompileVersion==='string'&&typeof parentRuntime.zlibRuntimeVersion==='string','Malformed Python/zlib runtime receipt');
 const inherited=inventory({projectRoot,sourceFiles}),b=JSON.parse(fs.readFileSync(local(projectRoot,benchmarkFile)));
 need(b.passed===true&&b.artificial===true&&b.n===62&&b.roundsPerArm===2000000&&b.arms?.length===2&&b.fullIndependentReplay===true,'Maximal artificial source-bound benchmark has not passed');
 for(const[name,h]of Object.entries(b.sourceHashes??{})){need(inherited.sourceHashes[name]===h,'Benchmark source changed '+name);inherited.inputHashes[name]=h;}
 for(const required of ['research/matched-clock-learning.js','research/matched-clock-io.js','research/matched-clock-graph.js','research/run-matched-clock.py','research/matched-clock-case.js','research/audit-matched-clock.js','research/replay-matched-clock.js'])need(b.sourceHashes?.[required]===inherited.sourceHashes[required],'Benchmark does not bind critical source '+required);
 inherited.inputHashes[benchmarkFile]=sha(fs.readFileSync(local(projectRoot,benchmarkFile)));
 inherited.inputHashes[pythonRuntimeFile]=sha(parentBytes);
 for(const ref of b.artifacts??[]){const bytes=fs.readFileSync(local(projectRoot,ref.file));need(bytes.length===ref.bytes&&sha(bytes)===ref.sha256,'Benchmark artifact drift '+ref.file);inherited.inputHashes[ref.file]=ref.sha256;}
 directory=path.resolve(directory);need(!fs.existsSync(directory)||fs.readdirSync(directory).length===0,'Refusing nonempty/previous study');fs.mkdirSync(directory,{recursive:true});
 const m={schemaVersion:1,frozenAt:new Date().toISOString(),sourceHashes:inherited.sourceHashes,inputHashes:inherited.inputHashes,priorDelivery:inherited.priorDelivery,inputs:{finiteGame:inherited.finiteGame},runtime:inherited.runtime,parentRuntime,benchmark:{file:benchmarkFile,sha256:inherited.inputHashes[benchmarkFile]},plan:{runs:inherited.runs,retainedRuns:24,T:2000000,checkpoints:[1000000,2000000],alpha:.1,gamma:19/20,initialization:'positive-zero',clock:'0->1->2->3->4->1',transcript:{bytesPerRound:120,roundsPerBlock:10000,completeBlocksPerRun:200},hardCaseSeconds:600,softResourceTargets:{primarySeconds:3600,replaySeconds:3600,sampledRSSBytes:512000000,newRawEquivalentBytes:1750000000},scope:'One unchanged numerical game; matched dense five-phase architecture; independent same-runtime replay required before endpoint acceptance; no experimental language-model/API seller calls'}};
 for(const[name,h]of Object.entries(m.sourceHashes)){const bytes=fs.readFileSync(local(projectRoot,name));need(sha(bytes)===h,'Source drift during freeze');save(directory,'sources/'+name,bytes);}
 save(directory,'manifest.json',m);return m;
}
export function verify(directory,{projectRoot=ROOT,checkRuntime=true}={}){
 const m=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json')));
 for(const group of ['sourceHashes','inputHashes'])for(const[name,h]of Object.entries(m[group])){need(sha(fs.readFileSync(local(projectRoot,name)))===h,'Frozen live dependency changed '+name);if(group==='sourceHashes')need(sha(fs.readFileSync(local(directory,'sources/'+name)))===h,'Frozen source snapshot changed '+name);}
 need(JSON.stringify(m.plan.runs)===JSON.stringify(plannedRuns()),'Planned identities/actors changed');if(checkRuntime)need(JSON.stringify(runtimeFingerprint(m.runtime))===JSON.stringify(runtimeFingerprint(runtimeIdentity())),'Frozen Node/V8 executable/runtime differs');return m;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [mode,directory=path.join(ROOT,'research/matched-clock-results'),benchmarkFile,pythonRuntimeFile]=process.argv.slice(2);
 if(mode==='freeze')console.log(JSON.stringify(freeze(directory,{benchmarkFile,pythonRuntimeFile})));
 else if(mode==='verify')console.log(JSON.stringify({passed:true,runs:verify(directory).plan.runs.length}));
 else if(mode==='runtime')console.log(JSON.stringify(runtimeIdentity()));
 else if(mode==='sources')console.log(JSON.stringify(sourceClosure(SOURCE_FILES,{readBytes:name=>fs.readFileSync(local(ROOT,name)),exists:name=>fs.existsSync(local(ROOT,name))})));
 else if(mode==='plan')console.log(JSON.stringify(plannedRuns()));
 else if(mode==='inventory')console.log(JSON.stringify(inventory()));else throw Error('Explicit inventory, freeze or verify required; import performs no work');
}
