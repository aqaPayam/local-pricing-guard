import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {MESH_SIZES,analyzeMesh} from './mesh-refinement.js';
import {outcome} from './robust-market.js';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SOURCES=['research/mesh-refinement.js','research/mesh-refinement-study.js','research/CONTINUOUS_REFINEMENT_PROTOCOL.md','research/CONTINUOUS_REFINEMENT_THEORY.md','research/ORDER_ENVELOPE_CANDIDATE.md','research/robust-market.js','tests/mesh-refinement.test.js'];
const FIXED_INPUTS=['research/cycle-results/manifest.json','research/cycle-results/independent-audit.json','research/handover-init-results/manifest.json','research/handover-init-results/independent-audit.json','research/handover-init-results/results.json'];
const SCENARIOS=['base-g15-t1','scale0.5-g15-t1','lower-quality-g15-t1','lowcost-g15-t1','base-g11-t1','base-g31-t1','base-g15-t0.5','base-g15-t2'];
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,p))).digest('hex');
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v)+'\n');
const casePath=s=>'research/cycle-results/cases/'+s+'-guard.json';
function hashes(paths){return Object.fromEntries(paths.map(p=>[p,digest(p)]));}

export function freezeMesh(directory='research/mesh-results'){
  const dir=path.resolve(ROOT,directory);fs.mkdirSync(dir,{recursive:true});
  if(fs.existsSync(path.join(dir,'manifest.json')))throw Error('Existing freeze preserved');
  const manifest={frozenAt:new Date().toISOString(),plan:{scenarioLabels:SCENARIOS,meshSizes:MESH_SIZES,cases:SCENARIOS.length*MESH_SIZES.length,method:'Monotone upper-map order envelope with explicit unresolved branch',scope:'binary64 numerical diagnostic; independent streaming full-payoff audit required',apiCalls:0,trainingRounds:0},sourceHashes:hashes(SOURCES),inputHashes:hashes([...FIXED_INPUTS,...SCENARIOS.map(casePath)])};
  write(path.join(dir,'manifest.json'),manifest);return manifest;
}
function verifyManifest(m){for(const [p,h] of Object.entries({...m.sourceHashes,...m.inputHashes}))if(digest(p)!==h)throw Error('Frozen source/input changed: '+p);}
function compareInherited(result,sourceCases,economy,epsilon){
  return sourceCases.filter(c=>c.scenario.epsilon===epsilon&&JSON.stringify(c.scenario.economy)===JSON.stringify(economy)&&c.game.n===result.n&&Math.abs(c.game.prices[0]-result.prices[0])<1e-12&&Math.abs(c.game.prices.at(-1)-result.prices.at(-1))<1e-12).map(c=>{
    const priceError=Math.max(...c.game.prices.map((p,i)=>Math.abs(p-result.prices[i]))),sameUpperMap=result.map.upper.every((u,j)=>u===c.game.sets[j].at(-1));let maxLowerShortfall=0,maxUpperExcess=0;
    if(result.destinations)for(const s of c.objectives.minCS.starts){const i=Math.floor(s.state/result.n),j=s.state%result.n,fi=result.destinations.fixed[i],fj=result.destinations.fixed[j],cs=outcome([result.prices[fi],result.prices[fj]],economy).consumerSurplus;maxLowerShortfall=Math.max(maxLowerShortfall,s.economicBounds.lower-cs);maxUpperExcess=Math.max(maxUpperExcess,cs-s.economicBounds.upper);}
    const tolerance=1e-10;
    return {inheritedCase:c.id,priceError,sameUpperMap,checkedStarts:c.objectives.minCS.starts.length,maxLowerShortfall,maxUpperExcess,comparisonTolerance:tolerance,passed:!!result.destinations&&sameUpperMap&&maxLowerShortfall<=tolerance&&maxUpperExcess<=tolerance};
  });
}
export function runMesh(directory='research/mesh-results'){
  const dir=path.resolve(ROOT,directory),manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));verifyManifest(manifest);
  if(['completion.json','index.json','journal.jsonl'].some(p=>fs.existsSync(path.join(dir,p))))throw Error('Existing or partial research output preserved');
  fs.mkdirSync(path.join(dir,'cases'),{recursive:true});
  const started=performance.now(),raw=read('research/handover-init-results/results.json'),sources=SCENARIOS.map(s=>read(casePath(s))),index=[];let rss=process.memoryUsage().rss;
  const journal=entry=>fs.appendFileSync(path.join(dir,'journal.jsonl'),JSON.stringify({at:new Date().toISOString(),...entry})+'\n');
  for(const source of sources){
    const {id,economy,epsilon}=source.scenario,targets=raw.records.find(r=>r.scenario.id===id)?.results;
    for(const n of MESH_SIZES){
      journal({scenario:id,n,status:'started'});
      try{
        if(targets?.length!==5)throw Error('Missing fixed audited targets');
        const result=analyzeMesh({economy,epsilon,lo:source.game.prices[0],hi:source.game.prices.at(-1),n,targets});
        const comparisons=compareInherited(result,sources,economy,epsilon),name=id+'-n'+n+'.json',payload={scenario:id,economy,...result,inheritedComparisons:comparisons};
        write(path.join(dir,'cases',name),payload);index.push({scenario:id,n,file:'cases/'+name,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,'cases',name))).digest('hex'),status:result.status,fixedPoints:result.destinations?.fixedPoints.length??null,welfare:result.welfare??null,inheritedComparisons:comparisons});
        journal({scenario:id,n,status:result.status,file:name});
      }catch(error){const failure={scenario:id,n,status:'failed',error:String(error.message)};write(path.join(dir,'cases',id+'-n'+n+'-failure.json'),failure);index.push({...failure,inheritedComparisons:[]});journal(failure);}
      rss=Math.max(rss,process.memoryUsage().rss);
    }
  }
  write(path.join(dir,'index.json'),{manifestSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,'manifest.json'))).digest('hex'),cases:index});
  let sourceHashesRechecked=true,sourceHashError=null;try{verifyManifest(manifest);}catch(error){sourceHashesRechecked=false;sourceHashError=String(error.message);journal({status:'final-hash-failure',error:sourceHashError});}
  const failures=index.filter(r=>r.status==='failed').length,inheritedComparisonFailures=index.flatMap(r=>r.inheritedComparisons).filter(r=>!r.passed).length;
  const completion={completedAt:new Date().toISOString(),cases:index.length,failures,unresolved:index.filter(r=>r.status!=='monotone-order-envelope').length,inheritedComparisons:index.reduce((s,r)=>s+r.inheritedComparisons.length,0),inheritedComparisonFailures,sourceHashesRechecked,sourceHashError,passed:index.length===72&&!failures&&!inheritedComparisonFailures&&sourceHashesRechecked,seconds:(performance.now()-started)/1000,largestObservedRSSBytes:rss,memorySampling:'After each case; not continuously measured peak',runtimeTargetSeconds:600,rssTargetBytes:250000000,apiCalls:0,trainingRounds:0};write(path.join(dir,'completion.json'),completion);journal({status:'completed',passed:completion.passed});return completion;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const [mode,directory]=process.argv.slice(2);if(!['freeze','run'].includes(mode))throw Error('Expected freeze or run; no default research execution');
  console.log(JSON.stringify(mode==='freeze'?freezeMesh(directory):runMesh(directory)));
}
