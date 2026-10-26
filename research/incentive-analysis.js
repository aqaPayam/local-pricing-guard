// Descriptive adapter only. No search or DP cases are run by this module.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import{fileURLToPath}from'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const PREFIX='research/incentive-results/';
const file=name=>{const p=path.resolve(ROOT,name);if(p!==ROOT&&!p.startsWith(ROOT+path.sep))throw Error('Outside workspace path');return p;};
const bytes=name=>fs.readFileSync(file(name)),read=name=>JSON.parse(bytes(name));
const sha=name=>crypto.createHash('sha256').update(bytes(name)).digest('hex');
const need=(condition,message)=>{if(!condition)throw Error(message);};
const inputHashes={},use=name=>{inputHashes[name]=sha(name);return read(name);};
const M=PREFIX+'manifest.json',R=PREFIX+'results.json',I=PREFIX+'index.json',A=PREFIX+'independent-audit.json',C=PREFIX+'completion.json';
const manifest=use(M),results=use(R),index=use(I),audit=use(A),completion=use(C);
need(audit.passed===true,'Independent incentive audit has not passed');
need(audit.studyManifestHash===sha(M)&&audit.resultsSha256===sha(R)&&audit.indexSha256===sha(I),'Independent primary manifest/results/index binding differs');
const auditor='research/audit-incentive-study.py';
need(audit.auditorSourceHash===sha(auditor),'Independent auditor source binding differs');inputHashes[auditor]=sha(auditor);
if(audit.arithmeticBackendHash!==undefined&&audit.arithmeticBackendHash!==null){need(typeof audit.arithmeticBackend==='string','Auditor backend path missing');need(sha(audit.arithmeticBackend)===audit.arithmeticBackendHash,'Independent arithmetic backend differs');inputHashes[audit.arithmeticBackend]=audit.arithmeticBackendHash;}
need(Object.keys(audit.corruptionNegativeControls??{}).length>=5&&Object.values(audit.corruptionNegativeControls).every(value=>value===true),'Independent corruption controls missing/failed');
need(results.manifestSha256===sha(M)&&index.manifestSha256===sha(M)&&completion.manifestSha256===sha(M),'Primary manifest links differ');
need(completion.resultsSha256===sha(R)&&completion.indexSha256===sha(I)&&completion.finalFrozenDependencyCheck?.passed===true,'Primary final completion/hash check failed');
need(completion.passed===true&&completion.unresolvedRecords===0,'Primary completion has not explicitly passed without unresolved labels');
for(const field of ['sourceHashes','inputHashes'])for(const[name,hash]of Object.entries(manifest[field]??{})){
 need(sha(name)===hash,'Frozen input/source drift '+name);inputHashes[name]=hash;
 if(field==='sourceHashes'){const snapshot=PREFIX+'sources/'+name;need(sha(snapshot)===hash,'Frozen source snapshot drift '+snapshot);inputHashes[snapshot]=hash;}
}
const start=use(PREFIX+'run-start.json');need(start.manifestSha256===sha(M),'Run-start manifest identity differs');
const journalPath=PREFIX+'journal.jsonl';inputHashes[journalPath]=sha(journalPath);
const journal=bytes(journalPath).toString('utf8').trim().split('\n').map(line=>JSON.parse(line));
const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){[a,b]=[b,a%b];}return a;};
function ratio(n,d){n=BigInt(n);d=BigInt(d);need(d!==0n,'Zero descriptive rational denominator');if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return{numerator:String(n/g),denominator:String(d/g)};}
const checkRatio=value=>{need(value&&/^-?\d+$/.test(value.numerator)&&/^\d+$/.test(value.denominator)&&BigInt(value.denominator)>0n,'Exact rational metadata unavailable');return value;};
const sign=value=>{if(value===null||value===undefined)return'unavailable';checkRatio(value);const n=BigInt(value.numerator);return n<0n?'negative':n>0n?'positive':'zero';};
const subtract=(a,b)=>ratio(BigInt(checkRatio(a).numerator)*BigInt(b.denominator)-BigInt(b.numerator)*BigInt(a.denominator),BigInt(a.denominator)*BigInt(b.denominator));
const relative=(gain,base)=>BigInt(checkRatio(base).numerator)<=0n?null:ratio(BigInt(checkRatio(gain).numerator)*BigInt(base.denominator),BigInt(gain.denominator)*BigInt(base.numerator));
function approximate(value){if(!value)return null;checkRatio(value);if(value.approximate!==undefined)return value.approximate;const n=BigInt(value.numerator),s=n<0n?-1:1,ns=String(n<0n?-n:n),ds=value.denominator,nl=ns.slice(0,16),dl=ds.slice(0,16);const v=s*Number(nl)/Number(dl)*10**((ns.length-nl.length)-(ds.length-dl.length));return Number.isFinite(v)?v:null;}
const histogram=(values,key)=>{const counts={};for(const value of values){const k=key(value);counts[k]=(counts[k]??0)+1;}return counts;};
const context=r=>({id:r.id,scenario:r.scenario,slotId:r.periodSlot.id,period:r.period??r.periodSlot.period??null,duplicateOf:r.periodSlot.duplicateOf??null,focalSeller:r.focalSeller,discount:r.discount,discountId:r.discount.numerator+'/'+r.discount.denominator});
const welfareByFile=new Map(),welfareRows=[];
for(const item of index.welfareCertificates){const name=PREFIX+item.file;need(sha(name)===item.sha256,'Indexed welfare hash differs '+name);const w=use(name);
 need(w.targetComparisons.length===5,'Five original welfare targets missing');
 const compact={...w,sourceFile:name,sourceSha256:item.sha256};welfareByFile.set(item.file,compact);welfareRows.push(compact);
}
const records=[],phaseRows=[],screenRows=[];
need(results.records.length===96&&index.records.length===96&&completion.records===96,'All 96 retained labels required');
need(new Set(index.records.map(v=>v.id)).size===96&&new Set(results.records.map(v=>v.id)).size===96,'Duplicate/missing retained identities');
for(const primary of results.records){const matches=index.records.filter(v=>v.id===primary.id);need(matches.length===1,'Record index identity differs');const item=matches[0],name=PREFIX+item.file;
 need(item.status===primary.status&&sha(name)===item.sha256,'Record hash/status differs '+name);const saved=use(name);need(JSON.stringify(saved)===JSON.stringify(primary),'Saved record/aggregate mismatch '+name);
 const events=journal.filter(e=>e.id===primary.id);need(events.length===2&&events[0].status==='started'&&events[1].status===primary.status,'Incomplete retained record journal '+primary.id);
 const r={...context(primary),status:primary.status,sourceRecord:name,sourceRecordSha256:item.sha256,periodSlot:primary.periodSlot,failure:primary.failure??null,failureType:primary.failureType??null,
  rewardOrientation:primary.rewardOrientation??null,cap:null,phases:[],screen:null,optimalBlockReplay:[],baselineBlockTrace:[],policies:[],welfare:null,checks:primary.checks??null};
 if(primary.status==='completed exact unilateral audit'){
  const K=primary.period;need(Number.isInteger(K)&&K>=1&&primary.phaseDiagnostics.length===K,'All baseline-path phases required '+primary.id);
  const w=welfareByFile.get(primary.welfareCertificate.file);need(w&&w.sourceSha256===primary.welfareCertificate.sha256&&w.scenario===r.scenario&&w.period===K,'Welfare/record identity mismatch');r.welfare={sourceFile:w.sourceFile,sourceSha256:w.sourceSha256,period:w.period};
  const rawEntry=manifest.plan.cases.find(v=>v.scenario===r.scenario);need(rawEntry,'Raw case mapping missing');const raw=read(rawEntry.rawFile),finite=raw.finite,n=finite.prices.length;
  r.cap={...primary.cap,finiteGain:subtract(primary.cap.finiteOptimal,primary.cap.finiteBaseline),relativeGain:relative(primary.cap.infiniteGain,primary.cap.infiniteBaseline),relativeGainUnavailableReason:primary.phaseDiagnostics[0].relativeGainUnavailableReason??null,gainSign:sign(primary.cap.infiniteGain)};
  need(r.cap.gainSign!=='negative','Negative exact cap gain');
  for(const layer of primary.layers){const policyPath=PREFIX+layer.argmaxFile;need(sha(policyPath)===layer.argmaxSha256&&bytes(policyPath).length===layer.argmaxBytes,'Argmax policy hash/length differs');inputHashes[policyPath]=layer.argmaxSha256;r.policies.push({...layer,argmaxFile:policyPath});}
  need(r.policies.length===K-1,'Every guard phase policy required');
  for(let phase=0;phase<K;phase++){const value=primary.phaseDiagnostics[phase];need(value.phase===phase,'Baseline-path phase order differs');
   const view={...value,finiteGain:subtract(value.finiteOptimal,value.finiteBaseline),gainSign:sign(value.infiniteGain),immediateGainSign:sign(value.immediateBestGain)};
   need(view.gainSign!=='negative'&&view.immediateGainSign!=='negative','Negative exact baseline-path gain');r.phases.push(view);phaseRows.push({...context(primary),...view});
   const pair=r.focalSeller==='A'?[value.baselineAction,value.opponentAction]:[value.opponentAction,value.baselineAction],tableIndex=pair[0]*n+pair[1];
   r.baselineBlockTrace.push({phase,priorFocalState:value.priorFocalState,focalAction:value.baselineAction,opponentAction:value.opponentAction,originalQuoteIndices:pair,prices:pair.map(i=>finite.prices[i]),profitApproximate:finite.rewards[r.focalSeller==='A'?'profitA':'profitB'][tableIndex],customerBenefitApproximate:finite.rewards.consumerSurplus[tableIndex],sourceOriginalTableIndex:tableIndex,displayScope:'Direct saved binary64 table lookup, not a new certificate'});
  }
  r.optimalBlockReplay=primary.optimalBlockReplay.map(step=>{const pair=step.originalQuoteIndices,tableIndex=pair[0]*n+pair[1];return{...step,prices:pair.map(i=>finite.prices[i]),customerBenefitApproximate:finite.rewards.consumerSurplus[tableIndex]};});
  need(r.optimalBlockReplay.length===K,'Complete optimal block replay required');
  r.replayDiscountedProfit=primary.replayDiscountedProfit;
  r.screen={...primary.oneShotScreen,gainSign:sign(primary.oneShotScreen.gain),activationLowerGainSign:sign(primary.oneShotScreen.capActivationLowerGain)};screenRows.push({...context(primary),...r.screen});
 }
 records.push(r);
}
need(journal.length===192,'Journal contains unaccounted started/finished events');
const rows=[];
for(const entry of manifest.plan.cases){const raw=read(entry.rawFile),row={scenario:entry.scenario,economy:raw.economy??raw.scenario?.economy??null,physicalCap:{index:raw.finite.capIndex,price:raw.finite.prices[raw.finite.capIndex]},rawCase:entry,periodSlots:[]};
 for(const slotId of manifest.plan.periodSlots){const selected=records.filter(r=>r.scenario===entry.scenario&&r.slotId===slotId);need(selected.length===4,'All focal/discount labels required for slot');
  const first=selected[0],slot={slotId,period:first.period,periodSource:first.periodSlot,duplicateOf:first.duplicateOf,welfare:first.welfare?{...welfareByFile.get(first.welfare.sourceFile.slice(PREFIX.length))}:null,focalSellers:{}};
  for(const focal of manifest.plan.focalSellers){const group=selected.filter(r=>r.focalSeller===focal);need(group.length===2,'Both discounts required');slot.focalSellers[focal]={discounts:Object.fromEntries(group.map(r=>[r.discountId,r]))};}
  row.periodSlots.push(slot);
 }rows.push(row);
}
need(rows.length===8&&records.length===96,'Complete eight-game comparison matrix required');
const summary={kind:'Hash-gated descriptive unilateral-incentive adapter; no new cases or DP search',analysisSourceHash:sha('research/incentive-analysis.js'),inputHashes,rows,records,phaseRows,screenRows,welfareRows,
 counts:{scenarioLabels:rows.length,records:records.length,completedRecords:records.filter(r=>r.cap!==null).length,unresolvedRecords:records.filter(r=>r.cap===null).length,duplicateRecordLabels:records.filter(r=>r.duplicateOf!==null).length,distinctWelfareCertificates:welfareRows.length,baselinePathPhaseRows:phaseRows.length,
  capGainSignsByDiscount:Object.fromEntries(['19/20','0/1'].map(discountId=>[discountId,histogram(records.filter(r=>r.discountId===discountId),r=>r.cap?.gainSign??'unavailable')])),
  capGainSigns:histogram(records,r=>r.cap?.gainSign??'unavailable'),phaseGainSigns:histogram(phaseRows,r=>r.gainSign),immediatePhaseGainSigns:histogram(phaseRows,r=>r.immediateGainSign),screenGainSigns:histogram(screenRows,r=>r.gainSign),statuses:histogram(records,r=>r.status),gammaZeroCapZeroButLaterPositive:records.filter(r=>r.discount.numerator==='0'&&r.cap?.gainSign==='zero'&&r.phases.some(v=>v.phase>0&&v.gainSign==='positive')).length},
 audits:{independent:Object.fromEntries(Object.entries(audit).filter(([key])=>key!=='details'))},resources:completion.resources,
 scope:'Exact rational optimization on saved finite-game binary64 weights against the fixed public upper-script opponent. Positive gains reject only that script at stated phase/discount; zero recorded gains establish no general equilibrium. Profit discounting and separately certified undiscounted all-policy welfare are distinct. No learning, emergent collusion, empirical market or human-play validation.'};
const display=value=>value===null?'unavailable':approximate(value)===null?'see exact fraction':Number(approximate(value)).toPrecision(6);
let text='# Individual profit incentives under the public upper script\n\n';
text+='The independent audit binds the exact primary manifest/results/index, live auditor, frozen inputs, all 96 per-record outputs, policy bytes, welfare certificates and complete journals. This descriptive adapter runs no new dynamic program. Exact rational signs determine every positive/zero label; displayed values are approximate. The rational weights are the saved finite-game binary64 payoffs, not exact-real logit economics.\n\n';
text+='## Cap activation: full discounted response\n\n';
text+='Each opponent continues its public upper-choice script after a deviation. All period slots, focal sellers, discounts, duplicates, failures and zero outcomes remain in the raw/summary tables. Relative gain is unavailable when the baseline value is nonpositive.\n\n';
text+='| Scenario | Period slot | K | Seller | Discount | Exact gain sign | Baseline value (approx.) | Optimal gain (approx.) | Relative gain (approx.) |\n|---|---|---|---|---|---|---|---|---|\n';
for(const r of records)text+=`| ${r.scenario} | ${r.slotId}${r.duplicateOf?' (duplicate of '+r.duplicateOf+')':''} | ${r.period??'unavailable'} | ${r.focalSeller} | ${r.discountId} | ${r.cap?.gainSign??r.status} | ${display(r.cap?.infiniteBaseline??null)} | ${display(r.cap?.infiniteGain??null)} | ${display(r.cap?.relativeGain??null)} |\n`;
const selectedDiscounted=records.filter(r=>r.slotId==='closed-effective-95pct'&&r.discountId==='19/20'&&r.cap?.relativeGain!==null&&r.cap?.relativeGain!==undefined),relativePercent=selectedDiscounted.map(r=>100*approximate(r.cap.relativeGain));
if(relativePercent.length)text+=`\nThe inherited 95%-period slots at discount 19/20 have approximately ${Math.min(...relativePercent).toPrecision(4)}% to ${Math.max(...relativePercent).toPrecision(4)}% relative optimal profit gain at activation. These small magnitudes matter for interpretation: an exact rejection of script optimality is not evidence of a large economic effect. The simple last-guard screen below already explains the qualitative rejection.\n`;
text+='\n## Simple last-guard screen and all-phase interpretation\n\n';
text+='For K>1 the screen is a feasible one-shot profit gain on the last guard execution. The next real cap discards history, so returning to the original script restores its continuation. K=1 uses the cap-stage analogue. A positive screen is an elementary explanation, not a separate new collusion mechanism. Gamma=0 at activation ignores later phases: the summary retains every baseline-path phase, including later positive incentives after an exact-zero cap gain. Full finite and infinite values retain different optimal and baseline next-cycle constants.\n\n';
text+=`Exact cap signs: ${JSON.stringify(summary.counts.capGainSigns)}. Exact last-guard/cap-screen signs: ${JSON.stringify(summary.counts.screenGainSigns)}. There are ${summary.counts.gammaZeroCapZeroButLaterPositive} retained gamma-zero labels with zero activation gain and a positive later-phase gain. These are deterministic labels, not independent replications or statistical evidence.\n\n`;
text+='## Customer benefit remains a separate all-policy certificate\n\n';
text+='A permitted individual deviation does not invalidate the enforced all-policy customer-benefit floor. Each distinct finite game/K has its own exact both-upper cycle mean and minimum nonempty-prefix mean. Importing a continuous-selected period transfers its identity only; the five original absolute targets are compared anew within the finite numerical game.\n\n';
text+='| Scenario | K | Long-run cycle floor (approx.) | All activation-average floor (approx.) | Minimizing prefix | Original target labels met |\n|---|---|---|---|---|---|\n';
for(const w of welfareRows)text+=`| ${w.scenario} | ${w.period} | ${display(w.cycleMean)} | ${display(w.activationAverageFloor)} | ${w.minimizingPrefixLength} | ${w.targetComparisons.filter(t=>t.activationFloorMeetsTarget).map(t=>t.label).join(', ')||'none'} |\n`;
text+='\n## Limits and provenance\n\n';
text+=`All ${records.length} planned comparison labels are retained, with ${summary.counts.unresolvedRecords} unresolved. ${summary.counts.duplicateRecordLabels} labels repeat an earlier period slot and are marked as such. Saved full policies are referenced by hash and byte length; their complete Bellman layers were independently recomputed, rather than inferred from one replay. The elementary screen, all-state optimization and all-policy safety answer different questions.\n\n`;
text+=`Primary elapsed time: ${Number(completion.resources.seconds).toFixed(3)} seconds; largest after-record RSS sample ${completion.resources.largestObservedRSSBytes} bytes (${completion.resources.sampling}). This is not a continuously measured peak. No training or experimental seller/model API calls were made. Codex development and AI-agent review assistance are disclosed; agent review is not human peer review.\n\n`;
text+='The fixed opponent has no punishment, adaptation, private state or learning. Neither positive nor zero recorded gains establish a general collusion equilibrium, learned-agent convergence, human behavior or an empirically validated market. Exact unilateral DP and reset decomposition are established methods; no new optimization algorithm is claimed. Earlier numerical studies, notes, games and archives remain preserved.\n';
fs.writeFileSync(file(PREFIX+'summary.json'),JSON.stringify(summary)+'\n');fs.writeFileSync(file('research/INCENTIVE_RESULTS.md'),text);
console.log(JSON.stringify({passed:true,records:records.length,phaseRows:phaseRows.length,welfareCertificates:welfareRows.length,summarySha256:sha(PREFIX+'summary.json'),reportSha256:sha('research/INCENTIVE_RESULTS.md')}));
