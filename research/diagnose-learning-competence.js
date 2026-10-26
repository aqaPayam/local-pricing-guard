import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createMarket,restore,cloneMarket,advance,gridBenchmarks} from './learning-market.js';
import {outcome,NASH_PRICE} from './replacement-market.js';
const study=process.argv[2]||'.local/learning-study-v1',output=process.argv[3]||'research/learning-diagnostics';
const read=p=>JSON.parse(fs.readFileSync(p)),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),save=(name,x)=>fs.writeFileSync(path.join(output,name),JSON.stringify(x));
if(!fs.existsSync(path.join(study,'completion.json')))throw Error('Wait for main completion');
if(fs.existsSync(output))throw Error('Refuse to overwrite diagnostic');
const main=read(path.join(study,'manifest.json')),plan=main.plan;
fs.mkdirSync(output,{recursive:true});save('manifest.json',{frozenAt:new Date().toISOString(),mainManifest:sha(path.join(study,'manifest.json')),sources:Object.fromEntries(['research/LEARNING_DIAGNOSTIC_PROTOCOL.md','research/diagnose-learning-competence.js','research/learning-market.js','research/replacement-market.js','research/receiver-contract.js'].map(p=>[p,sha(p)])),apiCalls:0});
const load=(label,step)=>restore(read(path.join(study,'checkpoints',`${label}-${step}.json`)));
const warm=[],stability=[],continuous=[];
for(const seed of plan.seeds){
 const m=load(`competitive-${seed}`,plan.trainingSteps),n=m.prices.length,b=gridBenchmarks(m.prices),j=m.prices.reduce((k,p,i)=>Math.abs(p-NASH_PRICE)<Math.abs(m.prices[k]-NASH_PRICE)?i:k,0),bestProfit=Math.max(...b.profits.map(a=>a[j]));
 const trajectory=advance(cloneMarket(m),2000,{learn:false,explore:false,traceEvery:1,fixedOpponent:NASH_PRICE});
 const stateChecks=[];for(let s=0;s<n*n+1;s++){const row=m.q[0].slice(s*n,(s+1)*n);let a=0;for(let k=1;k<n;k++)if(row[k]>row[a])a=k;stateChecks.push({state:s,greedyAction:a,profit:b.profits[a][j],gap:bestProfit-b.profits[a][j]});}
 warm.push({seed,rivalGridIndex:j,bestResponseIndex:b.bestResponses[j],bestProfit,metrics:trajectory.metrics,realizedGap:bestProfit-trajectory.metrics.profitA,stateChecks,rows:trajectory.rows});
 for(const step of plan.trainingCheckpoints){const base=load(`base-${seed}`,step),r=advance(base,2000,{learn:false,explore:false,traceEvery:1}),seen=new Map();let cycle=null;for(let i=0;i<r.rows.length;i++){const key=r.rows[i].executedIndices.join(',');if(seen.has(key)){cycle={transient:seen.get(key)+1,length:i-seen.get(key)};break;}seen.set(key,i);}stability.push({seed,trainingStep:step,cycle,metrics:r.metrics,last200MeanCS:r.rows.slice(-200).reduce((s,x)=>s+x.consumerSurplus,0)/200,rows:r.rows});}
}
for(const seed of [1001,1002])for(const epsilon of [0,.005,.1]){const m=load(`base-${seed}`,plan.trainingSteps),r=advance(m,1000,{learn:false,explore:false,traceEvery:1,treatment:{type:'continuous',epsilon}});continuous.push({seed,epsilon,...r});}
save('warm.json',warm);save('stability.json',stability);save('continuous.json',continuous);save('summary.json',{warm:warm.map(({rows,stateChecks,...r})=>({...r,allStateMeanGap:stateChecks.reduce((s,x)=>s+x.gap,0)/stateChecks.length,allStateWorstGap:Math.max(...stateChecks.map(x=>x.gap))})),stability:stability.map(({rows,...r})=>r),continuous:continuous.map(x=>({seed:x.seed,epsilon:x.epsilon,metrics:x.metrics}))});save('completion.json',{completedAt:new Date().toISOString(),warmMarkets:warm.length,policyCheckpoints:stability.length,continuousCases:continuous.length,apiCalls:0});
