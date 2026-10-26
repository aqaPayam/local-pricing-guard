import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { performance } from 'node:perf_hooks';
import { fileURLToPath } from 'node:url';
import {createMarket,train,advance,checkpoint,restore,cloneMarket,replaceLearner,resetObservation,gridBenchmarks} from './learning-market.js';
import {NASH_PRICE} from './replacement-market.js';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x));
export const treatments=[
 {name:'unchanged',treatment:{}}, {name:'inherited-sham',treatment:{}},
 {name:'reset-observation',replacement:'observation',treatment:{}},
 {name:'fresh-Q',replacement:'fresh',treatment:{}},
 {name:'fresh-Q-reset',replacement:'fresh-reset',treatment:{}},
 {name:'cross-play',replacement:'cross-play',treatment:{}},
 {name:'competitive-pretrained',replacement:'competitive',treatment:{}},
 ...[0,.005,.1,1,8].map(epsilon=>({name:`guard-${epsilon}`,treatment:{type:'guard',epsilon}})),
 ...['A','B'].map(coverage=>({name:`guard-only-${coverage}`,treatment:{type:'guard',epsilon:.1,coverage}})),
 {name:'guard-release',treatment:{type:'guard',epsilon:.1,releaseAfter:250}},
 {name:'wrong-mu-low',treatment:{type:'guard',epsilon:.1,model:{mu:.2}}},
 {name:'wrong-mu-high',treatment:{type:'guard',epsilon:.1,model:{mu:.5}}},
 {name:'wrong-cost',treatment:{type:'guard',epsilon:.1,model:{cost:1.2}}},
 {name:'best-response',treatment:{type:'best-response'}},
 {name:'fixed-Nash',treatment:{type:'fixed-nash'}}, {name:'price-cap',treatment:{type:'cap'}},
 {name:'continuous-.1',treatment:{type:'continuous',epsilon:.1}},
 {name:'undercut',forceFirst:'best-response',treatment:{}},
];
export function defaultPlan(){return {version:1,cpuBudgetSeconds:900,pilot:{developmentSeed:11,steps:100000,seconds:.154},tracePolicy:"All evaluation settlements compact numeric arrays; Q-update samples every1000; training samples every100000",seeds:Array.from({length:12},(_,i)=>1001+i),developmentSeeds:[11,22],trainingSteps:3000000,frozenRounds:2000,adaptiveRounds:20000,adaptiveExploration:.01,trainingCheckpoints:[1000000,2000000,3000000],primary:{gridSize:15,gamma:.95,alpha:.15,beta:4e-6,memory:true},treatments,sensitivities:[{gridSize:11},{gridSize:21},{gamma:0},{gamma:.5},{beta:2e-6},{beta:8e-6},{memory:false},{alpha:.05},{alpha:.3}],sensitivitySeeds:[2001,2002,2003,2004],guardTrainingEpsilons:[.1],guardTrainingSeeds:Array.from({length:12},(_,i)=>1001+i),continuousSeeds:[1001,1002]};}
const sources=['research/learning-market.js','research/run-learning-study.js','research/replacement-market.js','research/receiver-contract.js','tests/learning-market.test.js','research/LEARNING_PROTOCOL.md','research/LEARNING_PROTOCOL_AMENDMENT.md'];
export function freeze(directory,plan=defaultPlan()){
 if(fs.existsSync(directory))throw Error('Refuse to overwrite study');
 for(const source of sources)if(!fs.existsSync(source))throw Error(`Missing protocol/source ${source}`);
 fs.mkdirSync(path.join(directory,'sources'),{recursive:true});const hashes={};
 for(const source of sources){const bytes=fs.readFileSync(source);hashes[source]=sha(bytes);const dest=path.join(directory,'sources',source);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,bytes);}
 write(path.join(directory,'manifest.json'),{frozenAt:new Date().toISOString(),plan,sourceHashes:hashes,disclaimer:'Local profit-reward learners. No model APIs. Discrete guard is not the continuous theorem.'});
 return plan;
}
export function verify(directory){const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json')));for(const [source,hash]of Object.entries(manifest.sourceHashes))if(sha(fs.readFileSync(source))!==hash)throw Error(`Frozen source changed: ${source}`);return manifest.plan;}
export function runStudy(directory){
 const plan=verify(directory);if(fs.existsSync(path.join(directory,'completion.json'))||fs.existsSync(path.join(directory,'evaluations.jsonl')))throw Error('Refuse to append/repeat run');
 const started=performance.now(),evaluations=[],training=[];const out=fs.openSync(path.join(directory,'evaluations.jsonl'),'wx');
 fs.mkdirSync(path.join(directory,'checkpoints'),{recursive:true});
 const saveEvaluation=(m,name,mode,meta,options={})=>{const adaptive=mode!=='frozen';const continuous=options.treatment?.type==='continuous';const rounds=continuous?1000:adaptive?plan.adaptiveRounds:plan.frozenRounds;const r=advance(m,rounds,{learn:adaptive,explore:false,explorationRate:mode==='adaptive'?plan.adaptiveExploration:0,traceEvery:1,...options});const columns=['step','stateA','stateB','proposalA','proposalB','executedIndexA','executedIndexB','previousPriceA','previousPriceB','priceA','priceB','profitA','profitB','CS','coveredA','coveredB','exploration'];const rows=r.rows.map(x=>[x.step,...x.states,...x.actions,...x.executedIndices,...x.previousPrices,...x.prices,...x.profits,x.consumerSurplus,...x.covered,x.exploration]);const record={...meta,name,mode,metrics:r.metrics,columns,rows,updateAudits:r.rows.filter((_,i)=>i%1000===0)};fs.writeSync(out,JSON.stringify(record)+'\n');evaluations.push({...meta,name,mode,metrics:r.metrics});};
 function trainingRun(config,label,treatment={},competitive=false){const m=createMarket(config),curves=[],samples=[];let done=0;const checkpoints=plan.trainingCheckpoints.filter(x=>x<=plan.trainingSteps);if(!checkpoints.includes(plan.trainingSteps))checkpoints.push(plan.trainingSteps);for(const target of checkpoints){const r=train(m,target-done,{treatment,traceEvery:100000,binSize:10000,fixedOpponent:competitive?NASH_PRICE:null});curves.push(...r.bins);samples.push(...r.rows);done=target;write(path.join(directory,'checkpoints',`${label}-${target}.json`),checkpoint(m));}training.push({label,config,treatment,competitive,curves,samples});return m;}
 for(const seed of plan.seeds){trainingRun({...plan.primary,seed},`base-${seed}`);for(const step of plan.trainingCheckpoints.filter(x=>x<plan.trainingSteps)){const m=restore(JSON.parse(fs.readFileSync(path.join(directory,'checkpoints',`base-${seed}-${step}.json`))));saveEvaluation(m,'unchanged','frozen',{seed,cohort:'checkpoint',trainingStep:step});}}
 for(const seed of plan.seeds){
   const base=restore(JSON.parse(fs.readFileSync(path.join(directory,'checkpoints',`base-${seed}-${plan.trainingSteps}.json`)))),competitive=trainingRun({...plan.primary,seed},`competitive-${seed}`,{},true);
   for(const entry of plan.treatments){if(entry.treatment.type==='continuous'&&!plan.continuousSeeds.includes(seed))continue;for(const mode of ['frozen','adaptive','updating-greedy']){const m=cloneMarket(base);if(entry.replacement==='observation')resetObservation(m);if(entry.replacement==='fresh'||entry.replacement==='fresh-reset')replaceLearner(m,null,0,{reset:entry.replacement==='fresh-reset'});if(entry.replacement==='competitive')replaceLearner(m,competitive);if(entry.replacement==='cross-play'){const nextSeed=plan.seeds[(plan.seeds.indexOf(seed)+1)%plan.seeds.length];const donorPath=path.join(directory,'checkpoints',`base-${nextSeed}-${plan.trainingSteps}.json`);if(!fs.existsSync(donorPath))continue;replaceLearner(m,restore(JSON.parse(fs.readFileSync(donorPath))),0);}saveEvaluation(m,entry.name,mode,{seed,cohort:'primary'},{treatment:entry.treatment,forceFirst:entry.forceFirst??null});}}
   console.log(`Primary seed ${seed} complete`);
 }
 for(let i=0;i<plan.sensitivities.length;i++)for(const seed of plan.sensitivitySeeds){const config={...plan.primary,...plan.sensitivities[i],seed},m=trainingRun(config,`sensitivity-${i}-${seed}`);for(const entry of plan.treatments.filter(x=>['unchanged','guard-0','guard-0.1','fresh-Q','price-cap'].includes(x.name)))for(const mode of ['frozen','adaptive']){const branch=cloneMarket(m);if(entry.replacement==='fresh')replaceLearner(branch);saveEvaluation(branch,entry.name,mode,{seed,cohort:'sensitivity',sensitivity:i,config},{treatment:entry.treatment});}console.log(`Sensitivity ${i} seed ${seed} complete`);}
 for(const epsilon of plan.guardTrainingEpsilons)for(const seed of plan.guardTrainingSeeds){const treatment={type:'guard',epsilon},m=trainingRun({...plan.primary,seed},`guard-trained-${epsilon}-${seed}`,treatment);for(const mode of ['frozen','adaptive'])for(const protectedNow of [true,false])saveEvaluation(cloneMarket(m),protectedNow?'protected':'released',mode,{seed,cohort:'guard-trained',epsilon},{treatment:protectedNow?treatment:{}});}
 fs.closeSync(out);write(path.join(directory,'training.json'),training);write(path.join(directory,'summary.json'),{evaluations,benchmarks:[11,15,21].map(n=>gridBenchmarks(createMarket({gridSize:n}).prices))});write(path.join(directory,'completion.json'),{completedAt:new Date().toISOString(),seconds:(performance.now()-started)/1000,trainingMarkets:training.length,trainingSteps:training.length*plan.trainingSteps,evaluationBranches:evaluations.length,evaluationRounds:evaluations.reduce((s,x)=>s+x.metrics.rounds,0),apiCalls:0});
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [command,directory='.local/learning-study-v1']=process.argv.slice(2);
 if(command==='--freeze')freeze(directory);
 else if(command==='--pilot'){if(!fs.existsSync('research/LEARNING_PROTOCOL.md'))throw Error('Protocol required');const start=performance.now(),m=createMarket({seed:11});train(m,100000,{traceEvery:10000});console.log(JSON.stringify({steps:100000,seconds:(performance.now()-start)/1000,checkpoint:checkpoint(m).t,benchmark:gridBenchmarks(m.prices)}));}
 else if(command==='--run')runStudy(directory);
 else throw Error('Use --freeze DIR, --pilot or --run DIR');
}
