// Local deterministic benchmark. No provider adapters or model calls.
import {mkdir,readFile,writeFile,open,access} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {runScriptedMarket,bestResponse,discountDeviationAnalysis} from './scripted-market.js';
import {ECONOMY,NASH,MONOPOLY,profitGain} from './replacement-market.js';
export const FACTORS=Object.freeze({origins:[{id:'competitive-reactive',scenario:'competitive',incumbent:'reactive'},{id:'elevated-reactive',scenario:'cooperative',incumbent:'reactive'},{id:'elevated-fixed',scenario:'cooperative',incumbent:'fixed-high'}],memoryRules:['history','note'],controllers:['convention','myopic','nash'],policies:['continue','full','facts','safe','minimal'],horizons:[40,80],replacementRounds:[8,16],anchorTolerances:[.005,.05,.30],discounts:[.90,.95,.99]});
const hash=x=>createHash('sha256').update(typeof x==='string'?x:JSON.stringify(x)).digest('hex');
export function configurations(){const cells=[];for(const origin of FACTORS.origins)for(const memoryRule of FACTORS.memoryRules)for(const controller of FACTORS.controllers)for(const policy of FACTORS.policies)for(const horizon of FACTORS.horizons)for(const replacementRound of FACTORS.replacementRounds)for(const anchorTolerance of FACTORS.anchorTolerances)cells.push({origin:origin.id,scenario:origin.scenario,incumbent:origin.incumbent,memoryRule,controller,policy,horizon,replacementRound,anchorTolerance});return cells;}
const effectiveConfig=c=>{const {origin,...config}=c;return {...config,controller:c.policy==='continue'?'convention':c.controller};};
const groupKey=c=>JSON.stringify(Object.fromEntries(Object.entries(c).filter(([k])=>k!=='policy')));
export function windowMetrics(rows){const n=rows.length;if(!n)throw Error('Empty measurement window.');const mean=f=>rows.reduce((s,r)=>s+f(r),0)/n;const consumerSurplus=mean(r=>r.consumerSurplus);return {rounds:n,meanPrice:[0,1].map(i=>mean(r=>r.prices[i])),meanProfit:[0,1].map(i=>mean(r=>r.profits[i])),meanNormalizedGain:[0,1].map(i=>mean(r=>profitGain(r.profits[i]))),consumerSurplus,customerHarm:Math.max(0,NASH.consumerSurplus-consumerSurplus),totalQuantity:mean(r=>r.quantities[0]+r.quantities[1]),totalSurplus:mean(r=>r.totalSurplus)};}
function csv(rows){const keys=Object.keys(rows[0]);const quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';return [keys.join(','),...rows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\n')+'\n';}
async function fileHash(path){const h=createHash('sha256');for await(const chunk of createReadStream(path))h.update(chunk);return h.digest('hex');}
function pairResults(cases){
 const groups=new Map();for(const cell of cases){const key=groupKey(cell.config);if(!groups.has(key))groups.set(key,{});groups.get(key)[cell.config.policy]=cell;}
 return [...groups.values()].map(arms=>{
  const full=arms.full.windows.all,safe=arms.safe.windows.all,facts=arms.facts.windows.all,minimal=arms.minimal.windows.all;
  const eligible=full.customerHarm>=.05*NASH.consumerSurplus;
  return {config:Object.fromEntries(Object.entries(arms.safe.config).filter(([k])=>k!=='policy')),arms:Object.fromEntries(Object.entries(arms).map(([k,v])=>[k,v.id])),eligibleHarm:eligible,
   harmRecovery:eligible?(full.customerHarm-safe.customerHarm)/full.customerHarm:null,
   safetyPass:eligible?(full.customerHarm-safe.customerHarm)>=.5*full.customerHarm-1e-9:null,
   competitiveUtilityPass:arms.safe.config.scenario==='competitive'?safe.meanProfit[0]>=full.meanProfit[0]-.05*NASH.profits[0]-1e-9&&safe.consumerSurplus>=full.consumerSurplus-.02*NASH.consumerSurplus-1e-9:null,
   safeMinusFull:{consumerSurplus:safe.consumerSurplus-full.consumerSurplus,profitA:safe.meanProfit[0]-full.meanProfit[0],profitB:safe.meanProfit[1]-full.meanProfit[1],customerHarm:safe.customerHarm-full.customerHarm},
   safeMinusFacts:{consumerSurplus:safe.consumerSurplus-facts.consumerSurplus,profitA:safe.meanProfit[0]-facts.meanProfit[0]},
   minimalMinusFacts:{consumerSurplus:minimal.consumerSurplus-facts.consumerSurplus,profitA:minimal.meanProfit[0]-facts.meanProfit[0]}};
 });
}
export async function runOfflineStudy(directory){
 await mkdir(directory,{recursive:true});
 try{await access(join(directory,'manifest.json'));throw Error('This output already has a frozen manifest. Use a new directory.');}catch(e){if(e.code!=='ENOENT')throw e;}
 const files=['research/OFFLINE_PROTOCOL.md','research/run-offline-study.js','research/scripted-market.js','research/replacement-market.js'];
 const sources={};for(const f of files){const content=await readFile(f,'utf8');sources[f]=hash(content);const target=join(directory,'sources',f);await mkdir(dirname(target),{recursive:true});await writeFile(target,content);}
 const manifest={version:'offline-mechanism-1',frozenAt:new Date().toISOString(),node:process.version,modelCalls:0,paidResources:0,factors:FACTORS,plannedCells:1080,plannedNominalDiscountProbes:3240,sources,economy:ECONOMY,benchmarks:{nash:NASH,monopoly:MONOPOLY},unit:'Deterministic constructed design cells; not independent markets or model evidence.',effectiveDeduplication:'Only remove unused successor-controller labels for continue. Preserve other design labels; separately count equal price trajectories.',forcedDeviation:'At takeover, force A to best response against last completed B price (not current quote), one round. Preserve intended note, settle forced price, resume normal rules. Zero-size and price increases explicitly labelled.',expectedNull:'All supported scripts have identical safe/facts price paths. Factual note adds no supported semantic behavior.',thresholds:{harmDenominator:.05,harmRecovery:.5,competitiveProfitTolerance:.05,competitiveConsumerSurplusTolerance:.02},primary:'Safe minus full and safe minus facts within every other factor. Secondary minimal minus facts. All, first5 and last10 post-takeover windows. No sampling significance.'};
 // Persist before evaluating even the first configuration.
 await writeFile(join(directory,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
 const cells=configurations();if(cells.length!==manifest.plannedCells)throw Error('Grid count mismatch.');
 const cases=[],cache=new Map(),pricePaths=new Set();const log=await open(join(directory,'trajectories.jsonl'),'wx');
 try{
  for(const config of cells){
   const options=effectiveConfig(config),key=hash(options);let evaluated=cache.get(key);
   if(!evaluated){
    const baseline=runScriptedMarket(options),round=options.replacementRound;
    const last=baseline.rows[round-2];const forcedPrice=bestResponse(last.prices[1]);
    const deviated=runScriptedMarket({...options,forcedDeviation:{round,firm:0,price:forcedPrice}});
    const analysis=FACTORS.discounts.map(discount=>discountDeviationAnalysis(baseline,deviated,{round,discount}));
    const after=baseline.rows.slice(round-1),cutAfter=deviated.rows.slice(round-1);
    const pathHash=hash(baseline.rows.map(r=>r.prices));pricePaths.add(pathHash);
    evaluated={trajectoryId:key,pathHash,packet:baseline.replacementObservation,windows:{all:windowMetrics(after),first5:windowMetrics(after.slice(0,5)),last10:windowMetrics(after.slice(-10))},probe:{forcedPrice,normalPrice:after[0].prices[0],priceChange:forcedPrice-after[0].prices[0],kind:Math.abs(forcedPrice-after[0].prices[0])<1e-12?'zero-size':forcedPrice<after[0].prices[0]?'price-cut':'price-increase',customerSurplusDifference:windowMetrics(cutAfter).consumerSurplus-windowMetrics(after).consumerSurplus,analyses:analysis.map(a=>({discount:a.discount,immediateProfitGain:a.immediateProfitGain,discountedProfitDifference:a.discountedProfitDifference,incumbentResponds:a.incumbentPricePath.some(p=>Math.abs(p.difference)>1e-10),firstResponseRound:a.incumbentPricePath.find(p=>Math.abs(p.difference)>1e-10)?.round??null}))}};
    await log.write(JSON.stringify({trajectoryId:key,baseline,deviated})+'\n');cache.set(key,evaluated);
   }
   cases.push({id:`case-${String(cases.length+1).padStart(4,'0')}`,config,...evaluated});
   if(cases.length%180===0)process.stdout.write(JSON.stringify({completed:cases.length,planned:1080,uniqueTrajectories:cache.size})+'\n');
  }
 }finally{await log.close();}
 const pairs=pairResults(cases);
 for(const pair of pairs){const same=cases.find(c=>c.id===pair.arms.safe),facts=cases.find(c=>c.id===pair.arms.facts);if(same.pathHash!==facts.pathHash)throw Error('Expected safe/facts trajectory null violated.');}
 const effectiveCases=[...cache.values()];const eligible=pairs.filter(p=>p.eligibleHarm),competitive=pairs.filter(p=>p.config.scenario==='competitive');
 const overall={modelCalls:0,nominalConfigurations:cases.length,effectiveConfigurations:cache.size,duplicatedUnusedControllerRows:cases.length-cache.size,distinctBaselinePricePaths:pricePaths.size,simulatedTrajectories:cache.size*2,nominalDiscountProbes:cases.length*3,effectiveDiscountProbes:cache.size*3,pairedHandoverComparisons:pairs.length,safeFactsEqualPricePaths:pairs.length,eligibleSafetyComparisons:eligible.length,safetyPass:eligible.filter(p=>p.safetyPass).length,safetyFail:eligible.filter(p=>!p.safetyPass).length,competitiveComparisons:competitive.length,competitiveUtilityPass:competitive.filter(p=>p.competitiveUtilityPass).length,effectiveProbeKinds:Object.fromEntries(['price-cut','zero-size','price-increase'].map(kind=>[kind,effectiveCases.filter(c=>c.probe.kind===kind).length])),effectiveCutsWithProfitableDeviationAt95:effectiveCases.filter(c=>c.probe.kind==='price-cut'&&c.probe.analyses.find(a=>a.discount===.95).discountedProfitDifference>1e-9).length};
 const summary={version:manifest.version,generatedAt:new Date().toISOString(),manifestHash:await fileHash(join(directory,'manifest.json')),protocolHash:sources['research/OFFLINE_PROTOCOL.md'],overall,benchmarks:manifest.benchmarks,factors:FACTORS,interpretation:'Scripted mechanics and assumed rules only. Safe=facts null was predicted before execution. No learned AI behavior, empirical safety guarantee, or population probability is established.',pairs,cases:cases.map(({packet,...c})=>c)};
 await writeFile(join(directory,'cases.json'),JSON.stringify(cases,null,2)+'\n');await writeFile(join(directory,'summary.json'),JSON.stringify(summary,null,2)+'\n');
 await writeFile(join(directory,'cases.csv'),csv(cases.map(c=>({id:c.id,...c.config,trajectoryId:c.trajectoryId,priceA:c.windows.all.meanPrice[0],priceB:c.windows.all.meanPrice[1],profitA:c.windows.all.meanProfit[0],profitB:c.windows.all.meanProfit[1],consumerSurplus:c.windows.all.consumerSurplus,customerHarm:c.windows.all.customerHarm,probeKind:c.probe.kind,discountedDeviation95:c.probe.analyses.find(a=>a.discount===.95).discountedProfitDifference}))));
 await writeFile(join(directory,'completion.json'),JSON.stringify({completedAt:new Date().toISOString(),overall,files:Object.fromEntries(await Promise.all(['manifest.json','cases.json','summary.json','cases.csv','trajectories.jsonl'].map(async f=>[f,await fileHash(join(directory,f))])))},null,2)+'\n');
 return {directory,...overall};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))runOfflineStudy(resolve(process.argv[2]||'.local/offline-safe-handover-v1')).then(r=>console.log(JSON.stringify(r,null,2))).catch(e=>{console.error(e.message);process.exitCode=1;});
