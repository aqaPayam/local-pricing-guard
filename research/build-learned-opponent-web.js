// Read-only gated export. Importing performs no IO or response optimization.
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {isDeepStrictEqual} from 'node:util';
import {analyzeEvidence,jsonBytes,localIO} from './learned-opponent-analysis.js';
import {evidenceReader,sha256} from './learned-opponent-evidence.js';
import {checkpointGameData,responseGamePolicy} from './learned-opponent-web-game.js';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),PREFIX='research/learned-opponent-results';
const need=(ok,message)=>{if(!ok)throw Error(message);};
export function buildWebEvidence(io){
 const summary=analyzeEvidence(io),e=evidenceReader(io),saved=e.bytes(PREFIX+'/summary.json');
 need(saved.equals(jsonBytes(summary)),'Saved derived summary differs from read-only raw regeneration');
 const manifest=e.json(PREFIX+'/manifest.json'),exporter='research/build-learned-opponent-web.js';
 need(manifest.sourceHashes[exporter]===e.hash(exporter),'Web exporter source absent/drifted from prospective freeze');
 const checkpoints=[],responses=[],seen=new Map();let finiteGame=null,finiteSource=null;
 for(const record of summary.records){
  const input=record.input,key=record.oldRunID;
  need(input&&input.oldRunID===key,'Record checkpoint source identity missing');
  if(!seen.has(key)){
   const source={inputRoot:'project',finiteGame:input.finiteGame,metadata:input.metadata,counts:input.counts,savedPolicies:input.savedPolicies};let checkpoint;
   try{
    const raw=e.json(e.ref('',input.finiteGame).name),finite=raw.finite;need(raw.scenario?.id==='base-g15-t1','Original finite game scenario differs');
    const n=finite?.prices?.length;for(const name of ['profitA','profitB','consumerSurplus'])need(finite.rewards?.[name]?.length===n*n&&finite.rewards[name].every(Number.isFinite),'Full saved finite payoff table missing '+name);
    if(finiteGame===null){finiteGame=raw;finiteSource=input.finiteGame;}else need(isDeepStrictEqual(finiteSource,input.finiteGame)&&isDeepStrictEqual(finiteGame,raw),'One unchanged finite game required');
    need(summary.records.some(r=>r.oldRunID===key&&r.scientificAvailable),'Both focal responses are scientifically unavailable; this checkpoint lacks new numerical reconstruction and manual play is locked');
    const metadata=e.json(e.ref('',input.metadata).name),counts=input.counts.map(ref=>{const b=e.ref('',ref).bytes;need(b.length%2===0,'Saved u16 count bytes malformed');return Array.from({length:b.length/2},(_,i)=>b.readUInt16LE(i*2));}),greedyOwn=input.savedPolicies.map(ref=>Array.from(e.ref('',ref).bytes));
    checkpoint=checkpointGameData({id:key,seed:record.seed,finite,control:record.control,terminal:{phase:metadata.phase,previousIndices:metadata.previousIndices},counts,greedyOwn,overflow:metadata.countOverflow,source});
    const offsets=Buffer.alloc(checkpoint.trainingCounts.rowOffsets.length*4);checkpoint.trainingCounts.rowOffsets.forEach((v,i)=>offsets.writeUInt32LE(v,4*i));
    need(metadata.layout?.n===checkpoint.n&&metadata.layout.rows===checkpoint.phases*checkpoint.n**2&&metadata.layout.cells===checkpoint.trainingCounts.A.length&&metadata.layout.offsetsSha256===sha256(offsets),'Original compact row-layout identity differs');
    need(isDeepStrictEqual(checkpoint.terminal,input.checkpointEntry.terminal),'Game terminal differs from selected checkpoint');
    if(record.scientificAvailable)need(isDeepStrictEqual(checkpoint.terminal,{phase:record.mdp.terminal.phase,previousIndices:record.mdp.terminal.previousIndices}),'Game and audited response terminal differ');
   }catch(error){
    // An independently accepted input failure remains a visible locked checkpoint.
    need(!summary.records.some(r=>r.oldRunID===key&&r.scientificAvailable),'Accepted scientific checkpoint failed display transform: '+error.message);
    checkpoint={id:key,seed:record.seed,control:record.control,status:'unavailable',available:false,reason:error.message,n:null,phases:record.control.phases,terminal:null,originalWorldPolicies:null,trainingCounts:null,source};
   }
   seen.set(key,checkpoint);checkpoints.push(checkpoint);
  }
  const checkpoint=seen.get(key);let policy;
  if(record.scientificAvailable){need(checkpoint.available&&finiteGame,'Scientifically available response needs its validated original game');
   const own=record.focal==='A'?'A':'B',other=own==='A'?'B':'A';need(sha256(Buffer.from(checkpoint.originalWorldPolicies[own]))===record.mdp.baselineWorldPolicySha256&&sha256(Buffer.from(checkpoint.originalWorldPolicies[other]))===record.mdp.opponentWorldPolicySha256,'Display world greedy policy mapping differs from audited MDP');
   policy=Array.from(e.ref(PREFIX,record.optimizer.responsePolicy).bytes);}
  responses.push(checkpoint.available?responseGamePolicy(record,policy,finiteGame.finite):{recordId:record.id,scientificAvailable:false,executionSucceeded:record.executionSucceeded,status:record.status,actions:null,reason:checkpoint.reason,source:record.optimizer?.responsePolicy??null});
 }
 need(checkpoints.length===24&&responses.length===48,'Every checkpoint and response identity must be retained');
 for(const [name,h]of Object.entries(e.inputHashes))need(summary.inputHashes[name]===h||name===PREFIX+'/summary.json'||name===exporter,'Unbound game display source '+name);
 e.recheck();
 const {inputHashes,...payload}=summary;
 return {...payload,meta:{...payload.meta,webExporterSha256:e.hash(exporter),summarySha256:e.hash(PREFIX+'/summary.json'),displayScope:'No Q floats, browser optimization, new learning or language-model/chat/API seller calls. Manual execution starts at saved history/NEXT phase; its earned finite discounted score is separate from infinite audited policy values. A new manual segment is not an original activation-prefix welfare certificate.'},
  webgameData:{finiteGame,finiteGameSource:finiteSource,checkpointCases:checkpoints,responsePolicies:responses,coordinateScope:'Original greedy A/B and response actions are WORLD indexed. Compact exact training counts remain OWN/rival indexed with shared offsets; B count lookup swaps completed histories once.'}};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const output=process.argv[2]==='--output'?path.resolve(process.argv[3]):path.join(ROOT,PREFIX,'web-data.json'),payload=buildWebEvidence(localIO());fs.writeFileSync(output,jsonBytes(payload));console.log(JSON.stringify({output,records:payload.records.length,checkpointCases:payload.webgameData.checkpointCases.length}));
}
