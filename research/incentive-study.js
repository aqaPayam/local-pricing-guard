// Exact unilateral finite-block audit. Importing this module runs no cases.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import{fileURLToPath}from'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const OUT=path.join(ROOT,'research/incentive-results');
const SOURCES=['research/incentive-study.js','tests/incentive-study.test.js','research/INCENTIVE_PROTOCOL.md','research/INCENTIVE_THEORY.md'];
const DISCOUNTS=[{p:19,q:20},{p:0,q:1}],SELLERS=['A','B'];
const hashBytes=b=>crypto.createHash('sha256').update(b).digest('hex');
const sha=p=>hashBytes(fs.readFileSync(path.resolve(ROOT,p)));
const read=p=>JSON.parse(fs.readFileSync(path.resolve(ROOT,p),'utf8').replace(/^\uFEFF/,''));
const need=(condition,message)=>{if(!condition)throw Error(message);};
const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){const c=a%b;a=b;b=c;}return a;};
export function rational(n,d=1n){n=BigInt(n);d=BigInt(d);need(d!==0n,'Zero rational denominator');if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return{n:n/g,d:d/g};}
const add=(a,b)=>rational(a.n*b.d+b.n*a.d,a.d*b.d);
const subtract=(a,b)=>rational(a.n*b.d-b.n*a.d,a.d*b.d);
const multiply=(a,b)=>rational(a.n*b.n,a.d*b.d);
const divide=(a,b)=>rational(a.n*b.d,a.d*b.n);
const compare=(a,b)=>{const d=a.n*b.d-b.n*a.d;return d<0n?-1:d>0n?1:0;};
function approximate(a){if(a.n===0n)return 0;const sign=a.n<0n?-1:1,n=(a.n<0n?-a.n:a.n).toString(),d=a.d.toString(),nl=n.slice(0,16),dl=d.slice(0,16);const v=sign*Number(nl)/Number(dl)*10**((n.length-nl.length)-(d.length-dl.length));return Number.isFinite(v)?v:null;}
const packed=a=>({numerator:a.n.toString(),denominator:a.d.toString(),approximate:approximate(a)});
const unpack=a=>rational(a.numerator,a.denominator);
export function binary64(value){
 need(typeof value==='number'&&Number.isFinite(value),'Finite saved binary64 payoff required');
 const buffer=new ArrayBuffer(8),view=new DataView(buffer);view.setFloat64(0,value,false);const bits=view.getBigUint64(0,false),negative=(bits>>63n)!==0n,e=Number((bits>>52n)&2047n),fraction=bits&((1n<<52n)-1n);
 if(e===0&&fraction===0n)return rational(0n);
 let mantissa=e===0?fraction:(1n<<52n)+fraction,shift=e===0?-1074:e-1023-52;
 if(negative)mantissa=-mantissa;
 return shift>=0?rational(mantissa<<BigInt(shift)):rational(mantissa,1n<<BigInt(-shift));
}
export function integerWeights(values){
 const fractions=values.map(binary64);let denominator=1n;
 for(const value of fractions)if(value.d>denominator)denominator=value.d;
 return{denominator,weights:fractions.map(value=>value.n*(denominator/value.d))};
}
export function layerHash(values){return hashBytes(Buffer.from(values.map(String).join('\n')+'\n'));}
function discount(value){const p=BigInt(value.p),q=BigInt(value.q);need(q>0n&&p>=0n&&p<q&&gcd(p,q)===1n,'Reduced discount in [0,1) required');return{p,q};}
export function prepareGame(raw,focal='A'){
 need(SELLERS.includes(focal),'Unknown focal seller');const f=raw.finite,n=f.prices.length;
 need(Number.isInteger(n)&&n>0&&n<=62,'Finite game needs 1..62 original quotes');
 need(f.prices.every((v,i)=>Number.isFinite(v)&&(i===0||v>f.prices[i-1])),'Original price indices must increase');
 need(Number.isInteger(f.capIndex)&&f.capIndex>=0&&f.capIndex<n,'Invalid physical cap index');
 need(f.sets.length===n&&f.upper.length===n,'Mask/upper size mismatch');
 for(let j=0;j<n;j++){const s=f.sets[j];need(Array.isArray(s)&&s.length>0&&s.every((a,k)=>Number.isInteger(a)&&a>=0&&a<n&&(k===0||a>s[k-1])),'Nonempty sorted unique original action indices required');need(f.upper[j]===s.at(-1),'Saved upper choice must equal mask maximum');}
 const table=f.rewards[focal==='A'?'profitA':'profitB'];need(Array.isArray(table)&&table.length===n*n,'Focal saved profit table size mismatch');
 const converted=integerWeights(table),reward=(a,b)=>converted.weights[focal==='A'?a*n+b:b*n+a];
 return{raw,focal,n,sets:f.sets,upper:f.upper,cap:f.capIndex,D:converted.denominator,reward,
  rewardOrientation:focal==='A'?'original profitA[own*n+rival]':'original profitB[rival*n+own]'};
}
function best(actions,value){let choice=actions[0],maximum=value(choice),ties=1;
 for(let z=1;z<actions.length;z++){const a=actions[z],v=value(a);if(v>maximum){maximum=v;choice=a;ties=1;}else if(v===maximum)ties++;}return{action:choice,value:maximum,ties};}
function baselineStates(game,K){const states=Array(K).fill(null);let own=game.cap,rival=game.cap;
 for(let phase=1;phase<K;phase++){states[phase]=[own,rival];[own,rival]=[game.upper[rival],game.upper[own]];}return states;}
function phaseImmediate(game,phase,state){const cap=phase===0,actions=cap?Array.from({length:game.cap+1},(_,i)=>i):game.sets[state[1]],rival=cap?game.cap:game.upper[state[0]],baseline=cap?game.cap:game.upper[state[1]],opt=best(actions,a=>game.reward(a,rival));return{rival,baseline,opt,gain:opt.value-game.reward(baseline,rival)};}
export function solveBlock(raw,K,focal,gamma){
 need(Number.isInteger(K)&&K>=1&&K<=65536,'Integer period in [1,65536] required');
 const game=prepareGame(raw,focal),{p,q}=discount(gamma),{n,D}=game,total=n*n,states=baselineStates(game,K),powers=[1n];
 for(let h=1;h<=K;h++)powers.push(powers.at(-1)*q);
 let next=Array(total).fill(0n),nextBase=Array(total).fill(0n),nonnegativeChecks=0,tiedMaxima=0;
 const layers=[],policies=new Map(),pathValues=new Map();
 for(let phase=K-1;phase>=1;phase--){const h=K-phase,scale=powers[h-1],current=Array(total),baseline=Array(total),policy=new Uint8Array(total);
  // Values depend on i through U(i), and on j through its complete support.
  for(let i=0;i<n;i++){const b=game.upper[i],actionValues=Array.from({length:n},(_,a)=>game.reward(a,b)*scale+p*next[a*n+b]);
   for(let j=0;j<n;j++){const index=i*n+j,opt=best(game.sets[j],a=>actionValues[a]),a0=game.upper[j];current[index]=opt.value;policy[index]=opt.action;baseline[index]=game.reward(a0,b)*scale+p*nextBase[a0*n+b];need(current[index]>=baseline[index],'Negative exact finite gain falsifies DP');nonnegativeChecks++;if(opt.ties>1)tiedMaxima++;}
  }
  const state=states[phase],index=state[0]*n+state[1],immediate=phaseImmediate(game,phase,state);
  pathValues.set(phase,{phase,state,remainingRewards:h,denominator:D*scale,optimal:current[index],baseline:baseline[index],optimalAction:policy[index],baselineAction:immediate.baseline,opponentAction:immediate.rival,immediate});
  layers.push({phase,states:total,remainingRewards:h,scaleDenominator:(D*scale).toString(),optimalValueSha256:layerHash(current),baselineValueSha256:layerHash(baseline),argmaxSha256:hashBytes(policy),argmaxBytes:policy.length});
  policies.set(phase,policy);next=current;nextBase=baseline;
 }
 const scale=powers[K-1],actions=Array.from({length:game.cap+1},(_,i)=>i),opt=best(actions,a=>game.reward(a,game.cap)*scale+(K===1?0n:p*next[a*n+game.cap]));
 const base=game.reward(game.cap,game.cap)*scale+(K===1?0n:p*nextBase[game.cap*n+game.cap]);need(opt.value>=base,'Negative cap gain falsifies DP');nonnegativeChecks++;if(opt.ties>1)tiedMaxima++;
 const capFinite=rational(opt.value,D*scale),baseFinite=rational(base,D*scale),capInfinite=rational(q*opt.value,D*(powers[K]-p**BigInt(K))),baseInfinite=rational(q*base,D*(powers[K]-p**BigInt(K)));
 const immediate=phaseImmediate(game,0,null);pathValues.set(0,{phase:0,state:null,remainingRewards:K,denominator:D*scale,optimal:opt.value,baseline:base,optimalAction:opt.action,baselineAction:game.cap,opponentAction:game.cap,immediate});
 const phaseDiagnostics=[...pathValues.values()].sort((a,b)=>a.phase-b.phase).map(v=>{
  const finite=rational(v.optimal,v.denominator),prescribed=rational(v.baseline,v.denominator),factor=rational(p**BigInt(v.remainingRewards),powers[v.remainingRewards]),continuation=multiply(factor,capInfinite),baseContinuation=multiply(factor,baseInfinite),infinite=add(finite,continuation),baselineInfinite=add(prescribed,baseContinuation),gain=subtract(infinite,baselineInfinite);
  need(gain.n>=0n,'Negative exact infinite gain falsifies DP');
  return{phase:v.phase,priorFocalState:v.state,remainingRewards:v.remainingRewards,optimalAction:v.optimalAction,baselineAction:v.baselineAction,opponentAction:v.opponentAction,
   finiteOptimal:packed(finite),finiteBaseline:packed(prescribed),nextCycleOptimalContribution:packed(continuation),nextCycleBaselineContribution:packed(baseContinuation),
   infiniteOptimal:packed(infinite),infiniteBaseline:packed(baselineInfinite),infiniteGain:packed(gain),relativeGain:baselineInfinite.n>0n?packed(divide(gain,baselineInfinite)):null,relativeGainUnavailableReason:baselineInfinite.n>0n?null:'Baseline value is nonpositive; no relative percentage benefit is displayed',
   immediateBestAction:v.immediate.opt.action,immediateBestTies:v.immediate.opt.ties,immediateBestGain:packed(rational(v.immediate.gain,D))};
 });
 const replay=[];let state=null,weighted=0n;
 for(let phase=0;phase<K;phase++){const b=phase===0?game.cap:game.upper[state[0]],a=phase===0?opt.action:policies.get(phase)[state[0]*n+state[1]];need(phase===0?a<=game.cap:game.sets[state[1]].includes(a),'Replay chose forbidden action');const reward=game.reward(a,b);weighted+=reward*(p**BigInt(phase))*powers[K-1-phase];replay.push({phase,priorFocalState:state,focalAction:a,opponentAction:b,originalQuoteIndices:focal==='A'?[a,b]:[b,a],profit:packed(rational(reward,D))});state=[a,b];}
 need(weighted===opt.value,'Policy replay differs from exact finite optimum');
 const screenPhase=K===1?0:K-1,screen=phaseDiagnostics[screenPhase],screenGain=unpack(screen.immediateBestGain);
 return{period:K,focalSeller:focal,discount:{numerator:p.toString(),denominator:q.toString()},rewardOrientation:game.rewardOrientation,profitCommonDenominator:D.toString(),statesPerGuardLayer:total,
  layers:layers.sort((a,b)=>a.phase-b.phase),policies,cap:{action:opt.action,baselineAction:game.cap,tiedMaximizers:opt.ties,scaleDenominator:(D*scale).toString(),optimalNumerator:opt.value.toString(),baselineNumerator:base.toString(),finiteOptimal:packed(capFinite),finiteBaseline:packed(baseFinite),infiniteOptimal:packed(capInfinite),infiniteBaseline:packed(baseInfinite),infiniteGain:packed(subtract(capInfinite,baseInfinite))},
  phaseDiagnostics,optimalBlockReplay:replay,replayDiscountedProfit:packed(rational(weighted,D*scale)),
  oneShotScreen:{kind:K===1?'cap one-shot analogue':'last guard before the next cap',phase:screenPhase,priorFocalState:screen.priorFocalState,action:screen.immediateBestAction,baselineAction:screen.baselineAction,opponentAction:screen.opponentAction,gain:screen.immediateBestGain,positive:screenGain.n>0n,capActivationLowerGain:packed(multiply(rational(p**BigInt(screenPhase),powers[screenPhase]),screenGain)),resetJustification:'Returning to the original baseline at the next real cap restores both cap quotes independently of the deviating previous pair; no extra punishment is introduced'},
  checks:{allStateBaselineFeasibility:true,exactNonnegativeFiniteGainChecks:nonnegativeChecks,exactNonnegativeOnPathInfiniteGains:phaseDiagnostics.length,tiedStateMaxima:tiedMaxima,completeOptimalBlockReplay:true},
  scope:'Exact rationals of saved finite-game binary64 profit weights. Fixed public opponent, not learned behavior or equilibrium; undiscounted customer benefit is certified separately.'};
}
export function welfareCertificate(raw,K){
 need(Number.isInteger(K)&&K>=1&&K<=65536,'Integer period in [1,65536] required');
 const game=prepareGame(raw,'A'),{n}=game,f=raw.finite;need(Array.isArray(f.rewards.consumerSurplus)&&f.rewards.consumerSurplus.length===n*n,'Customer-benefit table size mismatch');
 const cs=integerWeights(f.rewards.consumerSurplus),profitA=integerWeights(f.rewards.profitA),profitB=integerWeights(f.rewards.profitB);
 need(game.upper.every((u,i)=>i===0||u>=game.upper[i-1]),'All-policy floor requires nondecreasing upper map');
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){const v=cs.weights[i*n+j];if(i+1<n)need(v>=cs.weights[(i+1)*n+j],'Customer benefit increases with shop A price');if(j+1<n)need(v>=cs.weights[i*n+j+1],'Customer benefit increases with shop B price');}
 let a=game.cap,b=game.cap,sum=0n,sumA=0n,sumB=0n,floor=null,floorLength=0;const cycle=[];
 for(let phase=0;phase<K;phase++){if(phase>0)[a,b]=[game.upper[b],game.upper[a]];const index=a*n+b;sum+=cs.weights[index];sumA+=profitA.weights[index];sumB+=profitB.weights[index];const prefix=rational(sum,cs.denominator*BigInt(phase+1));if(floor===null||compare(prefix,floor)<0){floor=prefix;floorLength=phase+1;}cycle.push({phase,quoteIndices:[a,b],customerBenefit:packed(rational(cs.weights[index],cs.denominator))});}
 const comparisons=raw.originalTargets.map(t=>{const actual=binary64(t.actualGuaranteedThreshold);return{label:t.label,requestedTarget:packed(binary64(t.requestedTarget)),numericalMargin:typeof t.numericalMargin==='number'?packed(binary64(t.numericalMargin)):null,actualThreshold:packed(actual),activationFloorMeetsTarget:compare(floor,actual)>=0,activationFloorReserve:packed(subtract(floor,actual))};});
 return{period:K,cycle,cycleMean:packed(rational(sum,cs.denominator*BigInt(K))),activationAverageFloor:packed(floor),minimizingPrefixLength:floorLength,baselineProfitCycleMeans:{A:packed(rational(sumA,profitA.denominator*BigInt(K))),B:packed(rational(sumB,profitB.denominator*BigInt(K)))},targetComparisons:comparisons,
  scope:'Own inherited finite numerical game only: cap-first minimum nonempty prefix mean bounds every activation-average horizon, and the cycle mean is its long-run floor. Continuous selected-period identity transfers no target guarantee.'};
}
function save(file,value){fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value)+'\n',{flag:'wx'});}
function inventory(){
 const files={},use=name=>{files[name]=sha(name);return read(name);};
 for(const [folder,auditors]of [['sparse-display-results',['independent-audit.json','rational-audit.json']],['recurring-results',['independent-audit.json']]]){
  const prefix='research/'+folder+'/',manifest=use(prefix+'manifest.json');
  for(const receipt of auditors){const audit=use(prefix+receipt);need(audit.passed===true&&audit.studyManifestHash===sha(prefix+'manifest.json'),'Inherited audit/manifest mismatch '+prefix+receipt);need(Object.keys(audit.corruptionNegativeControls??{}).length>0&&Object.values(audit.corruptionNegativeControls).every(v=>v===true),'Inherited rejection controls missing');
   const auditor=folder==='recurring-results'||receipt==='rational-audit.json'?'research/audit-sparse-reset.py':'research/audit-sparse-display.js';need(audit.auditorSourceHash===sha(auditor),'Inherited auditor source drift');files[auditor]=sha(auditor);
   if(audit.indexSha256)need(audit.indexSha256===sha(prefix+'index.json'),'Inherited index binding differs');if(audit.resultsSha256)need(audit.resultsSha256===sha(prefix+'results.json'),'Inherited results binding differs');
  }
  for(const group of ['sourceHashes','inputHashes'])for(const[name,digest]of Object.entries(manifest[group]??{})){need(sha(name)===digest,'Inherited frozen dependency drift '+name);need(!files[name]||files[name]===digest,'Inherited conflicting hash '+name);files[name]=digest;}
 }
 const index=use('research/sparse-display-results/index.json');need(index.manifestSha256===sha('research/sparse-display-results/manifest.json')&&index.cases.length===8,'Inherited finite case inventory differs');
 const cases=[];for(const entry of index.cases){const name='research/sparse-display-results/'+entry.file;need(entry.status==='completed'&&sha(name)===entry.sha256,'Finite case identity differs');use(name);cases.push({scenario:entry.scenario,rawFile:name,rawSha256:entry.sha256});}
 const recurring=use('research/recurring-results/results.json'),completion=use('research/recurring-results/completion.json');need(recurring.manifestSha256===sha('research/recurring-results/manifest.json')&&completion.resultsSha256===sha('research/recurring-results/results.json')&&completion.finalFrozenDependencyCheck?.passed===true,'Closed recurring completion differs');
 for(const entry of cases){const name='research/recurring-results/records/'+entry.scenario+'-effective.json',record=use(name),matches=recurring.records.filter(r=>r.scenario===entry.scenario&&r.continuum==='effective');need(matches.length===1&&JSON.stringify(matches[0])===JSON.stringify(record),'Closed effective journal differs');}
 const receiptPath='output/misspec-package-verification.json',delivery=use(receiptPath);need(delivery.verification?.passed===true&&delivery.verification.payloadHashesAndCRC===true&&/^[a-f0-9]{64}$/.test(delivery.sha256),'V7 delivery receipt failed');
 if(fs.existsSync(path.resolve(ROOT,delivery.archive)))need(sha(delivery.archive)===delivery.sha256,'V7 archive differs from its delivery receipt');
 return{files,cases,delivery:{receipt:receiptPath,receiptSha256:sha(receiptPath),archive:delivery.archive,archiveSha256:delivery.sha256,archivePresentAtVerification:fs.existsSync(path.resolve(ROOT,delivery.archive))}};
}
export function freeze(directory=OUT){
 directory=path.resolve(directory);need(!fs.existsSync(directory)||fs.readdirSync(directory).length===0,'Evidence directory nonempty; no overwrite');const inherited=inventory();
 const manifest={frozenAt:new Date().toISOString(),sourceHashes:Object.fromEntries(SOURCES.map(name=>[name,sha(name)])),inputHashes:inherited.files,v7Delivery:inherited.delivery,
  plan:{cases:inherited.cases,periodSlots:['permanent-cap','closed-effective-95pct','fixed-16'],focalSellers:SELLERS,discounts:DISCOUNTS,retainedRecords:96,softResourceTargets:{seconds:60,observedRSSBytes:250000000,newOutputBytes:10000000},ties:'Smallest original quote index among exact maxima',layerEncoding:'Signed base10 numerator per focal-row-major state, final newline; exact common scale denominator',scope:'No training, experimental seller/model API calls or new finite game/economy.'}};
 for(const name of SOURCES){const target=path.join(directory,'sources',name);fs.mkdirSync(path.dirname(target),{recursive:true});fs.copyFileSync(path.resolve(ROOT,name),target,fs.constants.COPYFILE_EXCL);}
 save(path.join(directory,'manifest.json'),manifest);return{manifestSha256:hashBytes(fs.readFileSync(path.join(directory,'manifest.json'))),frozenAt:manifest.frozenAt};
}
export function verify(directory=OUT){
 directory=path.resolve(directory);const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json'),'utf8'));
 for(const group of ['sourceHashes','inputHashes'])for(const[name,digest]of Object.entries(manifest[group])){need(sha(name)===digest,'Frozen incentive dependency changed '+name);if(group==='sourceHashes')need(hashBytes(fs.readFileSync(path.join(directory,'sources',name)))===digest,'Frozen source snapshot drift '+name);}
 const current=inventory();need(current.delivery.receiptSha256===manifest.v7Delivery.receiptSha256&&current.delivery.archiveSha256===manifest.v7Delivery.archiveSha256,'V7 delivery identity changed');return manifest;
}
function slotRows(raw,closed){
 const source=closed.comparisons.filter(r=>r.label==='cap-95pct'),target=raw.originalTargets.filter(r=>r.label==='cap-95pct');need(source.length===1&&target.length===1,'Missing/duplicate inherited 95% target');
 const prior=source[0],identity=prior.actualThresholdImported??prior.thresholdImported;need(identity?.exactDecimal!==undefined,'Missing inherited absolute target identity');need(compare(binary64(target[0].actualGuaranteedThreshold),rational(BigInt(identity.numerator),BigInt(identity.denominator)))===0,'Inherited 95% absolute target changed');
 const period=prior.status==='largest certified fixed period'?prior.largestPeriod:null;
 return[{id:'permanent-cap',period:1,source:'Predeclared permanent activation'},
  {id:'closed-effective-95pct',period,source:'Closed EFFECTIVE continuous cap-95pct selection; period identity only',inheritedSelectionStatus:prior.status,inheritedRequestedTarget:prior.requestedImported,inheritedActualTarget:identity},
  {id:'fixed-16',period:16,source:'Prospectively fixed looser period'}].map((slot,i,slots)=>({...slot,duplicateOf:slot.period===null?null:slots.slice(0,i).find(p=>p.period===slot.period)?.id??null}));
}
function outputBytes(directory){let sum=0;for(const entry of fs.readdirSync(directory,{withFileTypes:true})){const file=path.join(directory,entry.name);sum+=entry.isDirectory()?outputBytes(file):fs.statSync(file).size;}return sum;}
export function run(directory=OUT){
 directory=path.resolve(directory);const manifest=verify(directory);for(const name of ['run-start.json','journal.jsonl','records','policies','welfare','results.json','index.json','completion.json'])need(!fs.existsSync(path.join(directory,name)),'Partial/closed evidence preserved; refusing rerun');
 const started=performance.now(),manifestSha256=hashBytes(fs.readFileSync(path.join(directory,'manifest.json')));save(path.join(directory,'run-start.json'),{startedAt:new Date().toISOString(),manifestSha256});
 const journal=value=>fs.appendFileSync(path.join(directory,'journal.jsonl'),JSON.stringify({at:new Date().toISOString(),...value})+'\n');
 const records=[],index=[],rssSamples=[],welfareFiles=new Map();
 for(const entry of manifest.plan.cases){let raw,closed,slots,error;
  try{raw=read(entry.rawFile);need(raw.scenario.id===entry.scenario||raw.scenario===entry.scenario,'Raw scenario identity differs');closed=read('research/recurring-results/records/'+entry.scenario+'-effective.json');need(closed.scenario===entry.scenario&&closed.continuum==='effective','Closed effective identity differs');slots=slotRows(raw,closed);}catch(e){error=e;slots=manifest.plan.periodSlots.map(id=>({id,period:id==='permanent-cap'?1:id==='fixed-16'?16:null,source:'Retained planned slot; inherited identity unavailable',duplicateOf:null}));}
  for(const slot of slots)for(const focal of manifest.plan.focalSellers)for(const gamma of manifest.plan.discounts){const id=`${entry.scenario}--${slot.id}--${focal}--g${gamma.p}-${gamma.q}`,began=performance.now();journal({id,status:'started'});
   let result={id,scenario:entry.scenario,periodSlot:slot,focalSeller:focal,discount:{numerator:String(gamma.p),denominator:String(gamma.q)},status:'unresolved'};
   try{if(error)throw error;need(slot.period!==null,'Closed period unavailable; no period invented');const solved=solveBlock(raw,slot.period,focal,gamma);const policyDir=path.join(directory,'policies',id);for(const layer of solved.layers){const relative=`policies/${id}/phase-${String(layer.phase).padStart(5,'0')}.bin`,file=path.join(directory,relative);fs.mkdirSync(policyDir,{recursive:true});fs.writeFileSync(file,solved.policies.get(layer.phase),{flag:'wx'});layer.argmaxFile=relative;}
    delete solved.policies;const key=entry.scenario+'--K'+slot.period;
    if(!welfareFiles.has(key)){const certificate=welfareCertificate(raw,slot.period),file=`welfare/${key}.json`;save(path.join(directory,file),{scenario:entry.scenario,rawCaseSha256:entry.rawSha256,...certificate});welfareFiles.set(key,{file,sha256:hashBytes(fs.readFileSync(path.join(directory,file)))});}
    result={...result,...solved,welfareCertificate:welfareFiles.get(key),status:'completed exact unilateral audit'};
   }catch(e){result={...result,status:'unresolved calculation or inherited identity',failure:e.message,failureType:e.name};}
   result.seconds=(performance.now()-began)/1000;const file='records/'+id+'.json';save(path.join(directory,file),result);records.push(result);index.push({id,file,sha256:hashBytes(fs.readFileSync(path.join(directory,file))),status:result.status});rssSamples.push({id,rssBytes:process.memoryUsage().rss});journal({id,status:result.status,seconds:result.seconds});console.log(JSON.stringify({id,status:result.status,seconds:result.seconds}));
  }
 }
 save(path.join(directory,'results.json'),{manifestSha256,records});save(path.join(directory,'index.json'),{manifestSha256,records:index,welfareCertificates:[...welfareFiles.values()]});
 let final;try{verify(directory);final={passed:true};}catch(e){final={passed:false,failure:e.message};}
 const unresolvedRecords=records.filter(r=>r.status!=='completed exact unilateral audit').length;
 const completion={passed:final.passed&&records.length===manifest.plan.retainedRecords&&unresolvedRecords===0,records:records.length,unresolvedRecords,manifestSha256,resultsSha256:hashBytes(fs.readFileSync(path.join(directory,'results.json'))),indexSha256:hashBytes(fs.readFileSync(path.join(directory,'index.json'))),finalFrozenDependencyCheck:final,resources:{seconds:(performance.now()-started)/1000,rssSamples,largestObservedRSSBytes:Math.max(...rssSamples.map(r=>r.rssBytes)),sampling:'Process RSS after each retained record, not continuously measured peak',newOutputBytesBeforeCompletion:outputBytes(directory),node:process.version,experimentalModelApiCalls:0,newTrainingRounds:0}};
 save(path.join(directory,'completion.json'),completion);need(final.passed,'Final frozen dependency verification failed');return completion;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const[mode,...args]=process.argv.slice(2);need(['freeze','verify','run'].includes(mode)&&(!args.length||args.length===2&&args[0]==='--output'),'Use node research/incentive-study.js freeze|verify|run [--output DIR]');const output=args.length?path.resolve(ROOT,args[1]):OUT;console.log(JSON.stringify(mode==='freeze'?freeze(output):mode==='run'?run(output):verify(output)));
}
