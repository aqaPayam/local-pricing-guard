import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createMarket,train,advance,checkpoint,cloneMarket} from './learning-market.js';
const study=process.argv[2]||'.local/learning-study-v1',dir=process.argv[3]||'research/initialization-results';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),save=(name,x)=>fs.writeFileSync(path.join(dir,name),JSON.stringify(x));
if(!fs.existsSync(path.join(study,'completion.json')))throw Error('Wait for main completion');
if(fs.existsSync(dir))throw Error('Refuse to overwrite initialization extension');
fs.mkdirSync(path.join(dir,'checkpoints'),{recursive:true});
save('manifest.json',{frozenAt:new Date().toISOString(),sources:Object.fromEntries(['research/ZERO_INITIALIZATION_PROTOCOL.md','research/run-zero-initialization.js','research/learning-market.js','research/replacement-market.js','research/receiver-contract.js'].map(p=>[p,hash(p)])),mainManifest:hash(path.join(study,'manifest.json')),seeds:[2001,2002,2003,2004],trainingSteps:3000000,apiCalls:0});
const summaries=[],curves=[];const output=fs.openSync(path.join(dir,'evaluations.jsonl'),'wx');
const columns=['step','stateA','stateB','proposalA','proposalB','executedA','executedB','previousPriceA','previousPriceB','priceA','priceB','profitA','profitB','CS','coveredA','coveredB','exploration'];
for(const seed of [2001,2002,2003,2004])for(const initialization of ['normal','zero']){
 const m=createMarket({seed});if(initialization==='zero')m.q.forEach(q=>q.fill(0));const curve=[],samples=[];
 for(const step of [1000000,2000000,3000000]){const r=train(m,1000000,{traceEvery:100000,binSize:10000});curve.push(...r.bins);samples.push(...r.rows);save(`checkpoints/${seed}-${initialization}-${step}.json`,checkpoint(m));}
 curves.push({seed,initialization,curve,samples});
 for(const [name,treatment]of [['unchanged',{}],['guard-.1',{type:'guard',epsilon:.1}],['price-cap',{type:'cap'}]])for(const mode of ['frozen','adaptive']){
  const r=advance(cloneMarket(m),mode==='frozen'?2000:20000,{learn:mode==='adaptive',explore:false,explorationRate:mode==='adaptive'?.01:0,traceEvery:1,treatment});
  const rows=r.rows.map(x=>[x.step,...x.states,...x.actions,...x.executedIndices,...x.previousPrices,...x.prices,...x.profits,x.consumerSurplus,...x.covered,x.exploration]);
  fs.writeSync(output,JSON.stringify({seed,initialization,name,mode,treatment,metrics:r.metrics,columns,rows,updateAudits:r.rows.filter((_,i)=>i%1000===0)})+'\n');summaries.push({seed,initialization,name,mode,metrics:r.metrics});
 }
 console.log(`Initialization ${initialization} seed ${seed} complete`);
}
fs.closeSync(output);save('training.json',curves);save('summary.json',summaries);save('completion.json',{completedAt:new Date().toISOString(),trainingMarkets:8,trainingSteps:24000000,evaluationBranches:48,evaluationRounds:528000,apiCalls:0});
