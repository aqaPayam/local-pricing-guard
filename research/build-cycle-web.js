// Read-only display export. Does not optimize, train, audit or modify frozen data.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2),outputIndex=args.indexOf('--output');
if(args.length&&!(args.length===2&&outputIndex===0))throw Error('Use node research/build-cycle-web.js [--output FILE]');
const directory=path.join(ROOT,'research/cycle-results'),output=outputIndex===0?path.resolve(ROOT,args[1]):path.join(directory,'web-data.json');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const source=name=>path.join(directory,name);
const index=read(source('index.json')),manifest=read(source('manifest.json')),completion=read(source('completion.json'));
if(completion.failures.length||index.length!==manifest.plan.cases||completion.cases!==index.length)throw Error('Incomplete cycle results');
const structureFile=source('structure.json'),structure=fs.existsSync(structureFile)?read(structureFile):null;
const structureById=new Map((structure?.records||[]).map(record=>[record.id,record]));
const auditFile=source('independent-audit.json'),audit=fs.existsSync(auditFile)?read(auditFile):null;
const primitiveSummary=value=>Object.fromEntries(Object.entries(value||{}).filter(([,v])=>v===null||['boolean','string','number'].includes(typeof v)));

function finite(value,label){if(!Number.isFinite(value))throw Error('Non-finite display input: '+label);return value;}
function startExport(record,objective,key,label,state,provenance=[]){
 const result=record.objectives[objective].starts[state];
 if(!result?.infinitePath)throw Error('No recurrent path for displayed start');
 return {key,label,state,indices:[Math.floor(state/record.game.n),state%record.game.n],
  prefix:result.prefix,cycle:result.cycle,bounds:result.economicBounds,numericGap:result.numericGap,provenance};
}
function validatePath(record,start){
 const {n,sets,rewards}=record.game,size=n*n;
 for(const state of [...start.prefix,...start.cycle])if(!Number.isInteger(state)||state<0||state>=size)throw Error('Invalid display path state');
 if(start.prefix[0]!==start.state||start.prefix.at(-1)!==start.cycle[0])throw Error('Disconnected prefix/cycle');
 const edge=(u,v)=>sets[u%n].includes(Math.floor(v/n))&&sets[Math.floor(u/n)].includes(v%n);
 for(let i=1;i<start.prefix.length;i++)if(!edge(start.prefix[i-1],start.prefix[i]))throw Error('Illegal display entry edge');
 for(let i=0;i<start.cycle.length;i++)if(!edge(start.cycle[i],start.cycle[(i+1)%start.cycle.length]))throw Error('Illegal display cycle edge');
 start.mean=Object.fromEntries(['consumerSurplus','profitA','profitB','jointProfit'].map(key=>[key,
  start.cycle.reduce((sum,state)=>sum+finite(rewards[state][key],key),0)/start.cycle.length]));
 const objective= start.objective==='maxJointProfit'?'jointProfit':'consumerSurplus';
 if(start.bounds.lower>start.mean[objective]+1e-7||start.mean[objective]>start.bounds.upper+1e-7)throw Error('Witness outside displayed bounds');
}

const cases=index.map(entry=>{
 const file=source(entry.file),bytes=fs.readFileSync(file);
 if(sha(bytes)!==entry.sha256)throw Error('Frozen case hash mismatch: '+entry.id);
 const record=JSON.parse(bytes),{n,prices,sets,rewards}=record.game;
 if(prices.length!==n||sets.length!==n||rewards.length!==n*n||sets.some(row=>!row.length||row.some(i=>!Number.isInteger(i)||i<0||i>=n)))throw Error('Malformed display market');
 const expandedRewards=rewards.map((r,state)=>{
  const p=[prices[Math.floor(state/n)],prices[state%n]],e=record.scenario.economy;
  const utility=p.map(v=>(e.quality-v-e.outsideQuality)/e.mu),maximum=Math.max(0,...utility),outside=Math.exp(-maximum),mass=utility.map(v=>Math.exp(v-maximum)),denominator=outside+mass[0]+mass[1];
  const quantities=mass.map(v=>e.buyers*v/denominator);
  const profits=quantities.map((q,i)=>q*(p[i]-e.cost));
  if(Math.abs(profits[0]-r.profitA)>1e-8||Math.abs(profits[1]-r.profitB)>1e-8)throw Error('Display demand/profit mismatch');
  return {...r,quantities};
 });
 const objectives=Object.fromEntries(['minCS','maxJointProfit'].map(objective=>{
  const raw=record.objectives[objective],near=raw.diagnosticStarts.find(s=>s.provenance.some(p=>p.kind==='near-continuous-Nash-anchor')),
   high=raw.diagnosticStarts.find(s=>s.provenance.some(p=>p.kind==='high-high-anchor'));
  if(!near||!high)throw Error('Required display anchors missing');
  const starts=[startExport(record,objective,'high','High starting prices',high.state),startExport(record,objective,'nash','Near competitive reference',near.state)];
  for(const diagnostic of raw.diagnosticStarts){const saved=diagnostic.provenance.filter(p=>p.kind==='saved-training-terminal-diagnostic');if(!saved.length)continue;
   const armCounts=Object.fromEntries([...new Set(saved.map(p=>p.trainedArm))].map(arm=>[arm,saved.filter(p=>p.trainedArm===arm).length]));
   const label=`Saved terminal [${diagnostic.indices.join(', ')}] · ${saved.length} checkpoints`;
   starts.push(startExport(record,objective,'saved-'+diagnostic.state,label,diagnostic.state,saved.map(p=>({seed:p.seed,trainedArm:p.trainedArm,checkpoint:p.checkpoint,checkpointSha256:p.checkpointSha256}))));
   starts.at(-1).armCounts=armCounts;
  }
  const global={key:'global',label:'Global envelope · start on optimal loop',state:raw.universal.cycle[0],
   indices:[Math.floor(raw.universal.cycle[0]/n),raw.universal.cycle[0]%n],prefix:[raw.universal.cycle[0]],cycle:raw.universal.cycle,
   bounds:raw.universal.economicBounds,numericGap:raw.universal.upperBound-raw.universal.lowerBound,provenance:[]};
  starts.push(global);
  for(const start of starts){start.objective=objective;validatePath(record,start);}
  return [objective,{method:raw.method,starts,globalBounds:raw.universal.economicBounds,
    globalMean:raw.universalWitness,allStartBounds:raw.starts.map(s=>s.economicBounds)}];
 }));
 const structural=structureById.get(record.id);
 if(structural&&structural.caseSha256!==entry.sha256)throw Error('Structural display data references another case');
 return {id:record.id,scenario:record.scenario,controller:record.controller,caseSha256:entry.sha256,
  stateCount:record.stateCount,edgeCount:record.edgeCount,game:{n,prices,sets,rewards:expandedRewards,treatment:record.game.treatment},
  benchmarks:record.benchmarks,objectives,learnerComparisons:record.learnerComparisons,
  structure:structural?.applicable?{applicable:true,adjustedFloor:structural.adjustedFloor,
    largestSelfFeasibleIndex:structural.largestSelfFeasibleIndex,stationaryPrices:structural.stationaryPrices,
    stationaryReward:structural.stationaryReward,assumptions:structural.assumptions,
    maximumStartDeficit:structural.maximumStartDeficit,numericalSlack:structural.numericalSlack,
    starts:structural.starts.map(s=>({state:s.state,totalPositiveDeficitBound:s.totalPositiveDeficitBound,finiteAverageLowerBounds:s.finiteAverageLowerBounds})),scope:structural.scope}:null};
});
const data={schemaVersion:1,meta:{scope:'Coordinated finite-grid envelopes; not independently learned collusion or equilibrium.',
 completedAt:completion.completedAt,caseCount:cases.length,apiCalls:completion.apiCalls,
 manifestSha256:sha(fs.readFileSync(source('manifest.json'))),indexSha256:sha(fs.readFileSync(source('index.json'))),
 structureSha256:structure?sha(fs.readFileSync(structureFile)):null,
 audit:{passed:audit?.passed===true,source:audit?'research/cycle-results/independent-audit.json':null,
   sha256:audit?sha(fs.readFileSync(auditFile)):null,summary:primitiveSummary(audit)},
 exporterSha256:sha(fs.readFileSync(fileURLToPath(import.meta.url))),
 displayChecks:'Case hashes, grid, path continuity, allowed edges, economic display arithmetic and witness means checked. These checks do not replace the independent auditor.'},
 scenarios:manifest.plan.scenarios,cases};
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(data));
console.log(JSON.stringify({output:path.relative(ROOT,output).replaceAll('\\','/'),cases:cases.length,auditPassed:data.meta.audit.passed,bytes:fs.statSync(output).size}));
