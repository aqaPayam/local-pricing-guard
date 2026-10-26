// Independent initializer auditor. No imports from the initializer or market engine.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {auditCycleStudy} from './audit-cycle-study.js';

const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
let checks=0,edgesChecked=0;
function requireThat(ok,message){checks++;if(!ok)throw Error(message);}
function compare(actual,expected,label='value',tolerance=1e-9){
 if(typeof expected==='number'){requireThat(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,`${label}: ${actual} != ${expected}`);return;}
 if(expected===null||typeof expected!=='object'){requireThat(actual===expected,label);return;}
 requireThat(actual!==null&&typeof actual==='object',label+' object');
 if(Array.isArray(expected))requireThat(Array.isArray(actual)&&actual.length===expected.length,label+' array length');
 for(const [key,value] of Object.entries(expected))compare(actual[key],value,label+'/'+key,tolerance);
}
function economic(prices,e){
 const utilities=prices.map(p=>(e.quality-p-e.outsideQuality)/e.mu),shift=Math.max(0,...utilities),weights=utilities.map(v=>Math.exp(v-shift)),sum=Math.exp(-shift)+weights[0]+weights[1],sales=weights.map(w=>e.buyers*w/sum),profits=prices.map((p,i)=>(p-e.cost)*sales[i]);
 return {prices,consumerSurplus:e.buyers*e.mu*(shift+Math.log(sum)),profitA:profits[0],profitB:profits[1],jointProfit:profits[0]+profits[1]};
}
export function rebuildInitializerGame(scenario){
 const e=scenario.economy,n=scenario.gridSize;
 function symmetricPrice(joint){let low=e.cost,high=Math.max(e.cost,e.quality)+20*e.mu+2;for(let i=0;i<100;i++){const p=(low+high)/2,r=economic([p,p],e),share=r.profitA/((p-e.cost)*e.buyers),derivative=1-(p-e.cost)*(1-(joint?2:1)*share)/e.mu;if(derivative>0)low=p;else high=p;}return(low+high)/2;}
 const nash=symmetricPrice(false),joint=symmetricPrice(true),gap=joint-nash,low=nash-.1*gap,high=joint+.1*gap,prices=Array.from({length:n},(_,i)=>low+(high-low)*i/(n-1)),rewards=[];
 for(let a=0;a<n;a++)for(let b=0;b<n;b++)rewards.push(economic([prices[a],prices[b]],e));
 const sets=Array.from({length:n},(_,r)=>{const best=Math.max(...prices.map((_,a)=>rewards[a*n+r].profitA));return prices.flatMap((_,a)=>best-rewards[a*n+r].profitA<=scenario.epsilon+1e-12?[a]:[]);});
 const adjacency=Array.from({length:n*n},(_,s)=>{const a=Math.floor(s/n),b=s%n;return sets[b].flatMap(x=>sets[a].map(y=>x*n+y));});
 let capIndex=0;for(let i=1;i<n;i++)if(Math.abs(prices[i]-nash)<Math.abs(prices[capIndex]-nash)-1e-14)capIndex=i;
 return {n,prices,rewards,sets,adjacency,capIndex};
}
const range=xs=>({minimum:Math.min(...xs),maximum:Math.max(...xs)});
function rectangle(n,k){const states=[];for(let state=0;state<n*n;state++)if(Math.floor(state/n)<=k&&state%n<=k)states.push(state);return states;}
function classification(bounds,threshold){requireThat(Number.isFinite(bounds.lower)&&Number.isFinite(bounds.upper)&&bounds.lower<=bounds.upper,'Ordered finite inherited interval');return bounds.lower>=threshold?'safe':bounds.upper<threshold?'unsafe':'ambiguous';}
export function independentlyClassify(bounds,target){const margin=1e-8*Math.max(1,target),threshold=target-margin;return {margin,threshold,classes:bounds.map(b=>classification(b,threshold))};}
function rectangleSummary(game,bounds,classes,k){
 const states=rectangle(game.n,k),counts={safe:0,unsafe:0,ambiguous:0};for(const s of states)counts[classes[s]]++;
 const outcomeRanges={};for(const metric of ['consumerSurplus','profitA','profitB','jointProfit'])outcomeRanges[metric]=range(states.map(s=>game.rewards[s][metric]));
 return {index:k,price:game.prices[k],postStates:states,postStateCount:states.length,classificationCounts:counts,certifiedSafe:counts.safe===states.length,certifiedFailure:counts.unsafe>0,unresolved:counts.unsafe===0&&counts.ambiguous>0,reachableWorstCSBounds:{lower:Math.min(...states.map(s=>bounds[s].lower)),upper:Math.min(...states.map(s=>bounds[s].upper))},attainedPostStateWorstCSRange:range(states.map(s=>bounds[s].upper)),certifiedPostStateFloorRange:range(states.map(s=>bounds[s].lower)),oneRoundOutcomeRanges:outcomeRanges,allowedInitialPricesPerSeller:k+1,allowedInitialGridFraction:(k+1)/game.n,allowedInitialPriceSpan:game.prices[k]-game.prices[0]};
}
function verifyTail(game,start,prefix,cycle,declaredMean){
 requireThat(Array.isArray(cycle)&&cycle.length>0&&new Set(cycle).size===cycle.length,'Failure tail nonempty simple cycle');
 requireThat(Array.isArray(prefix)&&prefix.length>0&&prefix[0]===start&&prefix.at(-1)===cycle[0],'Failure prefix begins at actual post-state and joins tail');
 for(let i=1;i<prefix.length;i++)requireThat(game.adjacency[prefix[i-1]]?.includes(prefix[i]),'Failure prefix feasible edge');
 for(let i=0;i<cycle.length;i++)requireThat(game.adjacency[cycle[i]]?.includes(cycle[(i+1)%cycle.length]),'Failure cycle feasible edge');
 compare(declaredMean,cycle.reduce((sum,s)=>sum+game.rewards[s].consumerSurplus,0)/cycle.length,'Failure tail economic mean');
}
export function auditInitializerTarget(record,guard,cap,target,game){
 const bounds=guard.objectives.minCS.starts.map(s=>s.economicBounds),n=game.n,{margin,threshold,classes}=independentlyClassify(bounds,target.requestedTarget),groups={safe:[],unsafe:[],ambiguous:[]};classes.forEach((c,s)=>groups[c].push(s));
 compare(record,{label:target.label,basis:target.basis,fraction:target.fraction??null,referenceValue:target.referenceValue,requestedTarget:target.requestedTarget,numericalMargin:margin,actualGuaranteedThreshold:threshold},'Target metadata',1e-12);
 compare(record.classification,classes,'Rebuilt safe/unsafe/ambiguous classification');compare(record.statesByClass,groups,'Complete safe-set inventory');
 let outgoing=0;for(const state of groups.safe)for(const next of game.adjacency[state]){edgesChecked++;outgoing++;requireThat(classes[next]==='safe','Every independently rebuilt guard edge preserves safe set');}
 compare(record,{forwardInvariant:true,safeOutgoingEdges:outgoing,certifiedSafeRegionEmpty:groups.safe.length===0,allStatesCertifiedUnsafe:groups.unsafe.length===n*n,finiteInitializerImpossible:groups.unsafe.length===n*n,maximumAttainedReachableCSUpper:Math.max(...bounds.map(b=>b.upper))},'Region and impossibility');
 const candidates=Array.from({length:n},(_,k)=>rectangleSummary(game,bounds,classes,k));
 compare(record.prefixCandidates,candidates.map(c=>({index:c.index,price:c.price,postStateCount:c.postStateCount,classificationCounts:c.classificationCounts,certifiedSafe:c.certifiedSafe,reachableWorstCSBounds:c.reachableWorstCSBounds})),'Every common prefix cap');
 const existing=candidates[game.capIndex],largest=candidates.filter(c=>c.certifiedSafe).at(-1)||null;
 compare(record.existingCompetitiveCap,existing,'Actual competitive cap and first-execution economic ranges');compare(record.largestSafeCommonPrefixCap,largest,'Largest safe cap only within common prefix family');
 const bad=existing.postStates.find(s=>classes[s]==='unsafe');
 if(bad===undefined)compare(record.existingFailureWitness,null,'No invented failure for an ambiguous/safe rectangle');
 else {const witness=record.existingFailureWitness,prior=guard.objectives.minCS.starts[bad];compare(witness,{postInitializerState:bad,postInitializerPair:[Math.floor(bad/n),bad%n],guardPrefix:prior.prefix,guardCycle:prior.cycle,attainedGuardTailMean:bounds[bad].upper,numericalGuardTailLower:bounds[bad].lower},'Failure witness');verifyTail(game,bad,witness.guardPrefix,witness.guardCycle,witness.attainedGuardTailMean);requireThat(witness.attainedGuardTailMean<threshold,'Witness tail strictly fails actual relaxed threshold');}
 if(groups.unsafe.length===n*n)for(let s=0;s<n*n;s++){const prior=guard.objectives.minCS.starts[s];verifyTail(game,s,prior.prefix,prior.cycle,bounds[s].upper);requireThat(bounds[s].upper<threshold,'Every possible finite initializer endpoint has unsafe guard continuation');}
 const expected=[];for(const group of guard.objectives.minCS.diagnosticStarts)for(const p of group.provenance)if(p.kind==='saved-training-terminal-diagnostic'&&p.trainedArm==='none')expected.push({seed:p.seed,state:group.state,indices:group.indices,checkpoint:p.checkpoint,checkpointSha256:p.checkpointSha256,withoutInitializer:{classification:classes[group.state],reachableCSBounds:bounds[group.state]},withExistingOneRoundCap:{classificationCounts:existing.classificationCounts,certifiedSafe:existing.certifiedSafe,reachableCSBounds:existing.reachableWorstCSBounds},withLargestSafePrefixCap:largest?{index:largest.index,reachableCSBounds:largest.reachableWorstCSBounds}:null});
 compare(record.noneTrainedStartComparisons,expected,'All inherited unprotected starts and provenance');compare(record.anchorAttainedCSUpper,target.anchorAttainedCSUpper??null,'Anchor lower versus attained upper');
 return {label:record.label,safeStates:groups.safe.length,unsafeStates:groups.unsafe.length,ambiguousStates:groups.ambiguous.length,existingCapSafe:existing.certifiedSafe,largestSafeCap:largest?.index??null,finiteInitializerImpossible:groups.unsafe.length===n*n};
}
function expectedTargets(guard,cap){
 const floor=cap.objectives.minCS.universal.economicBounds.lower,anchor=guard.objectives.minCS.diagnosticStarts.find(s=>s.provenance.some(p=>p.kind==='near-continuous-Nash-anchor'));requireThat(!!anchor,'Preserved anchor exists');
 return [.9,.95,.99,1].map(f=>({label:`cap-${Math.round(100*f)}pct`,basis:'same-case permanent competitive-cap CS floor',fraction:f,referenceValue:floor,requestedTarget:f*floor})).concat({label:'near-Nash-anchor-floor',basis:'near-continuous-Nash anchor certified reachable CS lower bound',referenceValue:anchor.result.economicBounds.lower,requestedTarget:anchor.result.economicBounds.lower,anchorAttainedCSUpper:anchor.result.economicBounds.upper});
}
export function auditHandoverInit(directory='research/handover-init-results',{progress=false}={}){
 checks=0;edgesChecked=0;
 const manifest=read(path.join(directory,'manifest.json')),result=read(path.join(directory,'results.json')),completion=read(path.join(directory,'completion.json'));
 compare(Object.keys(manifest.sourceHashes).sort(),['research/handover-init.js','research/HANDOVER_INIT_PROTOCOL.md','tests/handover-init.test.js'].sort(),'Complete frozen source inventory');requireThat(Object.keys(manifest.inputHashes).length===19,'Sixteen primary cases plus three primary provenance inputs');
 for(const [file,hash]of Object.entries({...manifest.sourceHashes,...manifest.inputHashes}))requireThat(digest(fs.readFileSync(file))===hash,'Frozen source/input hash '+file);
 for(const [file,hash]of Object.entries(manifest.sourceHashes))requireThat(digest(fs.readFileSync(path.join(directory,'sources',file)))===hash,'Frozen source snapshot '+file);
 const primaryAudit=auditCycleStudy('research/cycle-results');requireThat(primaryAudit.passed,'Independent inherited numerical certificates reverified');
 const primary=read('research/cycle-results/manifest.json'),index=read('research/cycle-results/index.json');compare(result.plan,manifest.plan,'Frozen initializer plan');
 compare(manifest.plan,{scenarios:8,targetFractions:[.9,.95,.99,1],includeNearNashAnchor:true,marginScale:1e-8,labelsPerScenario:5,caseLabels:40,apiCalls:0,newTrainingRounds:0},'Prespecified matrix');
 requireThat(result.records.length===8&&new Set(result.records.map(r=>r.scenario.id)).size===8,'All eight scenarios exactly once');const details=[];let fixture=null;
 for(const scenario of primary.plan.scenarios){const record=result.records.find(r=>r.scenario.id===scenario.id);requireThat(!!record,'Scenario retained '+scenario.id);compare(record.scenario,scenario,'Exact preserved scenario identity');const loaded={};for(const controller of ['guard','cap']){const row=index.find(r=>r.id===scenario.id+'-'+controller),file=path.posix.join('research/cycle-results',row.file),bytes=fs.readFileSync(file);requireThat(manifest.inputHashes[file]===digest(bytes)&&row.sha256===digest(bytes),'Exact primary case input hash');loaded[controller]=JSON.parse(bytes);compare(loaded[controller].scenario,scenario,'Primary model identity');requireThat(loaded[controller].controller===controller,'Primary controller identity');}
  const {guard,cap}=loaded,game=rebuildInitializerGame(scenario);compare(guard.game,{n:game.n,prices:game.prices,sets:game.sets,adjacency:game.adjacency,rewards:game.rewards},'Independently rebuilt guard and economics');compare(cap.game.sets,Array.from({length:game.n},()=>Array.from({length:game.capIndex+1},(_,i)=>i)),'Independent competitive cap index');compare(record,{guardCaseId:guard.id,capCaseId:cap.id,permanentCapFloor:cap.objectives.minCS.universal.economicBounds},'Preserved case references');
  const targets=expectedTargets(guard,cap);requireThat(record.results.length===5&&new Set(record.results.map(r=>r.label)).size===5,'Five retained target labels');for(let i=0;i<5;i++){const row=record.results[i];details.push({scenario:scenario.id,...auditInitializerTarget(row,guard,cap,targets[i],game)});if(!fixture||!fixture.row.existingFailureWitness&&row.existingFailureWitness)fixture={row,guard,cap,target:targets[i],game};}if(progress)process.stderr.write('Independently audited initializer '+scenario.id+'\n');
 }
 compare(completion,{scenarios:8,labels:40,failures:[],apiCalls:0,newTrainingRounds:0},'Complete run inventory');compare(read(path.join(directory,'failures.json')),[],'No omitted failed scenario');
 const controls={};requireThat(!!fixture,'Actual record available for corruption checks');
 const trials={safeSet:r=>{r.classification[0]=r.classification[0]==='safe'?'unsafe':'safe';},capIndex:r=>{r.existingCompetitiveCap.index++;},economicRange:r=>{r.existingCompetitiveCap.oneRoundOutcomeRanges.consumerSurplus.minimum++;},failureTail:r=>{if(r.existingFailureWitness)r.existingFailureWitness.attainedGuardTailMean++;else r.existingFailureWitness={attainedGuardTailMean:-1};}};
 for(const [name,mutate]of Object.entries(trials)){const changed=structuredClone(fixture.row);mutate(changed);let rejected=false;try{auditInitializerTarget(changed,fixture.guard,fixture.cap,fixture.target,fixture.game);}catch{rejected=true;}requireThat(rejected,'Corruption control rejected '+name);controls[name]=rejected;}
 return {passed:true,completedAt:new Date().toISOString(),auditorSourceHash:digest(fs.readFileSync(fileURLToPath(import.meta.url))),studyManifestHash:digest(fs.readFileSync(path.join(directory,'manifest.json'))),inheritedCycleManifestHash:primaryAudit.studyManifestHash,checks,edgesChecked,scenarios:8,labels:40,corruptionNegativeControls:controls,details,scope:'Independently rebuilt guard edges/economics and checked inherited numerical certificates, relaxed long-run thresholds, all safe edges, exhaustive prefix caps, first-execution ranges, legal failing tails, all-state impossibility and original checkpoint provenance. No higher-target finite-horizon claim, equilibrium test, human validation or new shield algorithm.'};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2),out=args.indexOf('--output'),directory=args.find((x,i)=>!x.startsWith('--')&&(i===0||args[i-1]!=='--output'))||'research/handover-init-results',result=auditHandoverInit(directory,{progress:args.includes('--progress')});
 if(out>=0){requireThat(!!args[out+1],'Explicit output path required');fs.writeFileSync(args[out+1],JSON.stringify(result,null,2));}console.log(JSON.stringify(result));
}
