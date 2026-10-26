// Read-only evidence adapter. Importing performs no evidence reads or writes.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
import {analyzeEvidence,localIO} from './mixed-timing-analysis.js';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SUMMARY='research/mixed-timing-results/summary.json',CANONICAL='research/mixed-timing-results/web-data.json';
const need=(ok,message)=>{if(!ok)throw Error(message);};
export function buildWebEvidence(io){
 // This reruns the full evidence-gated derivation read-only. An editable saved
 // summary cannot pass merely by copying the original input hashes.
 const summary=analyzeEvidence(io),regenerated=Buffer.from(JSON.stringify(summary)+'\n'),saved=Buffer.from(io.readBytes(SUMMARY));
 need(saved.equals(regenerated),'Compact summary differs from raw-evidence regeneration');
 const digest=data=>crypto.createHash('sha256').update(data).digest('hex');
 const data={schemaVersion:1,meta:{...summary.meta,summarySha256:digest(saved),
  exporterSha256:digest(io.readBytes('research/build-mixed-timing-web.js')),
  primaryAudit:{passed:true,executionPassed:summary.meta.executionPassed,models:24,targetLabels:120,finiteTargetLabels:40,continuousTargetLabels:80,
   source:'research/mixed-timing-results/independent-audit.json',sha256:summary.meta.independentAuditSha256,
   requiresOrchestrator:false,continuousChecksComputedInProcess:true,inheritedPremiseRevalidation:false},
  sourceHashes:{...summary.meta.sourceHashes,authoritativeAuditor:summary.meta.audit.auditorSourceHash,
   controlAuditor:summary.meta.audit.controlAuditorSourceHash,continuousAuditor:summary.meta.audit.continuousAuditorSourceHash,
   inheritedArithmeticBackend:summary.meta.audit.arithmeticBackendHash},
  provenance:'All compact models regenerated read-only from the complete independently accepted raw study, with exact source/output/journal/completion bindings and byte comparison to the saved summary. Eight unchanged full finite games are separately index-bound. No new market optimization or learned-policy replay.',
  playerScope:'Manual finite interaction controls both shops; no model players in that interaction. No new language-model/chat/API seller calls or learner training. Codex development assistance is disclosed separately.'},
  scenarioOrder:summary.scenarioOrder,targetOrder:summary.targetOrder,finiteGames:summary.finiteGames,models:summary.models};
 return data;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2);need(args.length===0||(args.length===2&&args[0]==='--output'),'Use node research/build-mixed-timing-web.js [--output FILE]');
 const output=path.resolve(ROOT,args.length?args[1]:CANONICAL),relative=path.relative(ROOT,output);
 need(relative!==''&&!relative.startsWith('..'+path.sep)&&relative!=='..'&&!path.isAbsolute(relative),'Output escapes workspace');
 need(output===path.resolve(ROOT,CANONICAL)||!fs.existsSync(output),'Explicit output already exists; scientific/source files are preserved');
 const data=buildWebEvidence(localIO());fs.mkdirSync(path.dirname(output),{recursive:true});const bytes=Buffer.from(JSON.stringify(data));fs.writeFileSync(output,bytes);
 console.log(JSON.stringify({passed:true,models:data.models.length,targetLabels:120,finiteGames:data.finiteGames.length,bytes:bytes.length,
  output:relative.replaceAll('\\','/'),sha256:crypto.createHash('sha256').update(bytes).digest('hex')}));
}
