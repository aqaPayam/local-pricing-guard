// Read-only display adapter. Neither solves a market nor substitutes for either audit.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),M='research/mesh-results/',C='research/continuous-results/',args=process.argv.slice(2);
if(args.length&&!(args.length===2&&args[0]==='--output'))throw Error('Use node research/build-refinement-web.js [--output FILE]');
const abs=p=>path.resolve(ROOT,p),read=p=>JSON.parse(fs.readFileSync(abs(p),'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(abs(p))).digest('hex');
const need=(value,message)=>{if(!value)throw Error(message);};
function frozen(manifest){for(const group of ['sourceHashes','inputHashes'])for(const [file,digest] of Object.entries(manifest[group]||{}))need(hash(file)===digest,'Changed frozen dependency '+file);}
const mm=read(M+'manifest.json'),ma=read(M+'independent-audit.json'),mi=read(M+'index.json'),mc=read(M+'completion.json');
const cm=read(C+'manifest.json'),ca=read(C+'independent-audit.json'),cr=read(C+'results.json'),cc=read(C+'completion.json');
need(ma.passed===true&&ca.passed===true,'Both independent audits must pass before display export');
need(ma.studyManifestHash===hash(M+'manifest.json')&&mi.manifestSha256===ma.studyManifestHash,'Mesh manifest link mismatch');
need(ma.indexSha256===hash(M+'index.json'),'Mesh audited index link mismatch');
need(ca.studyManifestHash===hash(C+'manifest.json')&&cr.manifestSha256===ca.studyManifestHash,'Continuous manifest link mismatch');
need(ca.resultsSha256===hash(C+'results.json')&&cc.resultsSha256===ca.resultsSha256,'Continuous results link mismatch');
need(mc.passed===true&&mc.failures===0&&cc.finalFrozenDependencyCheck.passed===true,'Incomplete study');frozen(mm);frozen(cm);
const inherited=read('research/handover-init-results/results.json');
need(mi.cases.length===mm.plan.cases&&cr.records.length===cm.plan.records&&ma.cases===mi.cases.length&&ca.records===cr.records.length,'Missing declared records');
const records=mm.plan.scenarioLabels.map(id=>{
 const old=inherited.records.find(r=>r.scenario.id===id);need(old,'Missing inherited market '+id);
 const meshes=mi.cases.filter(r=>r.scenario===id).sort((a,b)=>a.n-b.n).map(entry=>{
  const file=M+entry.file;need(hash(file)===entry.sha256,'Changed mesh case '+file);const r=read(file);need(r.scenario===id&&r.n===entry.n,'Mesh identity mismatch');
  need(r.targets.length===old.results.length,'Missing mesh targets');for(const target of r.targets){const t=old.results.find(t=>t.label===target.label);need(t&&t.requestedTarget===target.requestedTarget&&t.actualGuaranteedThreshold===target.actualGuaranteedThreshold,'Moving inherited threshold');}
  return{n:r.n,sha256:entry.sha256,status:r.status,spacing:r.spacing,epsilon:r.epsilon,comparisonAllowance:r.map.comparisonAllowance,declaredEndpointPrices:r.declaredEndpointPrices,actualEndpointPrices:r.actualEndpointPrices,capIndex:r.capIndex,capPrice:r.prices[r.capIndex],ownPermanentCapFloor:r.ownPermanentCapFloor,welfare:r.welfare,fixedPoints:r.destinations?.fixedPoints||[],targets:r.targets,numericScope:r.numericScope};
 });
 need(meshes.length===mm.plan.meshSizes.length,'Missing market mesh');
 const continuous=Object.fromEntries(['effective','nominal'].map(kind=>{const rows=cr.records.filter(r=>r.scenario===id&&r.continuum===kind);need(rows.length===1,'Missing continuum '+id+' '+kind);const r=rows[0];need(r.comparisons.length===old.results.length,'Missing continuous targets');for(const t of r.comparisons){const original=old.results.find(o=>o.label===t.label);need(original&&Number(t.thresholdImported?.binary64Serialization)===original.actualGuaranteedThreshold&&Number(t.requestedImported?.binary64Serialization)===original.requestedTarget,'Continuous target identity mismatch');}return[kind,r];}));
 return{scenario:old.scenario,originalTargets:old.results.map(t=>({label:t.label,requestedTarget:t.requestedTarget,numericalMargin:t.numericalMargin,actualGuaranteedThreshold:t.actualGuaranteedThreshold,existingCap:t.existingCompetitiveCap})),meshes,continuous};
});
const data={schemaVersion:1,meta:{scope:'Audited finite-grid diagnostics and independently validated continuous enclosures; no model players or new training.',apiCalls:0,mesh:{manifestSha256:hash(M+'manifest.json'),indexSha256:hash(M+'index.json'),auditSha256:hash(M+'independent-audit.json'),passed:true,checks:ma.checks,cases:ma.cases},continuous:{manifestSha256:hash(C+'manifest.json'),resultsSha256:hash(C+'results.json'),auditSha256:hash(C+'independent-audit.json'),passed:true,checks:ca.checks??null,records:ca.records},exporterSha256:hash('research/build-refinement-web.js')},meshSizes:mm.plan.meshSizes,records};
const output=args.length?abs(args[1]):abs(M+'web-data.json');fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(data));console.log(JSON.stringify({output:path.relative(ROOT,output),markets:records.length,meshes:mi.cases.length,continuousRecords:cr.records.length,bytes:fs.statSync(output).size}));
