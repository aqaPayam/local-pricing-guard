// Prospective reference viewer. Locked without an accepted public export.
import {createReferenceReplay} from '/local-pricing-guard/guard-reference-game.js';
import {rational,add,subtract,divideInteger,fromJSON,fromDouble,approximate} from '/local-pricing-guard/recurring-game.js';
const need=(ok,message)=>{if(!ok)throw Error(message);},ARMS=['startup-guard','full-grid-after-cap'],SEEDS=Array.from({length:12},(_,i)=>907001+i);
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),hash=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
const ARM_COLORS={'startup-guard':'#75634a','full-grid-after-cap':'#3c6c50'},DIFFERENCE_COLORS={positive:'#3c6c50',negative:'#9a4b4b',zero:'#777165'};
const label=t=>t==='startup-guard'?'Guard stays on':'Guard removed after the first cap';
const runId=(seed,t)=>t==='startup-guard'?`base-g15-t1--matched5-startup--zero--s${seed}`:`base-g15-t1--full-grid-after-cap--zero--s${seed}`;
const cpId=(seed,t)=>runId(seed,t)+'--t2000000';
function ratio(v){need(v&&typeof v.numerator==='string'&&/^-?(0|[1-9]\d*)$/.test(v.numerator)&&typeof v.denominator==='string'&&/^[1-9]\d*$/.test(v.denominator)&&v.numerator.length<=2048&&v.denominator.length<=2048,'Malformed exact saved-weight ratio');return fromJSON(v);}

const equal=(a,b)=>a.n*b.d===b.n*a.d;

export function formatAmount(v,digits=3,{signed=false}={}){

 if(v===null||v===undefined)return '—';const exact=typeof v==='object'?ratio(v):null,x=exact?approximate(exact):v;need(Number.isFinite(x),'Nonfinite display');const sign=exact?(exact.n<0n?-1:exact.n>0n?1:0):Math.sign(x);if(!sign)return '0';

 let out;if(x===0&&exact){const a=(exact.n<0n?-exact.n:exact.n).toString(),b=exact.d.toString(),leadA=Number(a.slice(0,15))/10**(Math.min(15,a.length)-1),leadB=Number(b.slice(0,15))/10**(Math.min(15,b.length)-1);let lead=leadA/leadB,power=a.length-b.length;if(lead<1){lead*=10;power--;}if(lead>=10){lead/=10;power++;}out=(sign<0?'-':'')+lead.toFixed(3)+'e'+power;}else out=Math.abs(x)<10**-digits||Math.abs(x)>=1e7?x.toExponential(3).replace('e+','e'):x.toFixed(digits);

 return signed&&sign>0?'+'+out:out;

}

export function basketGraphic(quantity,tag){

 if(quantity===null)return '<span>No new purchases</span>';need(Number.isFinite(quantity)&&quantity>=0,'Invalid expected purchases');let marks='';for(let i=0;i<10;i++){const x=3+i*27,fill=Math.max(0,Math.min(1,quantity/10-i));marks+=`<rect x="${x}" y="12" width="21" height="14" rx="2" fill="#e5dfd1"/><rect x="${x}" y="${26-fill*14}" width="21" height="${fill*14}" fill="currentColor"/><path d="M${x} 12h21l-3 14h-15zM${x+5} 12l3-7h5l3 7" fill="none" stroke="currentColor" stroke-width="1.3"/>`;}return `<svg viewBox="0 0 274 30" aria-hidden="true" data-baskets="${esc(tag)}">${marks}</svg>`;

}

export function validateEvidence(data){
 const meta=data?.meta;
 need(data?.schemaVersion===1&&meta?.inventoryAccepted===true&&meta.independentAuditPassed===true&&meta.audit?.passed===true,'Authoritative reference inventory acceptance required');
 need(hash(meta.independentAuditSha256)&&hash(meta.primaryManifestSha256)&&hash(meta.startupGuardAuditSha256)&&typeof meta.fullTrainingReplay==='boolean'&&typeof meta.replayComplete==='boolean','Reference provenance/assurance malformed');
 const d=meta.defaultSelection;
 need(d?.seed===907001&&d.checkpoint===2000000&&JSON.stringify(d.treatments)===JSON.stringify(ARMS)&&d.chosenBeforeReferenceOutcomeInspection===true,'Retained reference default differs');
 need(JSON.stringify(data.orderedSeeds)===JSON.stringify(SEEDS)&&data.finalPolicies?.length===24&&data.checkpointStatuses?.length===24&&data.inheritedComparisonStatuses?.length===12&&data.pairedRows?.length===12,'Complete planned reference inventory required');
 need(JSON.stringify(data.pairedRows.map(r=>r.seed))===JSON.stringify(SEEDS),'Planned signed rows must keep seed order');
 const policies=new Map(),statuses=new Map();
 for(const p of data.finalPolicies){const id=cpId(p.seed,p.treatment);need(ARMS.includes(p.treatment)&&SEEDS.includes(p.seed)&&p.runId===runId(p.seed,p.treatment)&&p.checkpointId===id&&!policies.has(id),'Final policy identity differs');policies.set(id,p);
  if(p.available){ratio(p.cycleMetrics?.consumerSurplus);need(Number.isInteger(p.cycleLength)&&p.cycleLength>0&&p.cycleLength<=4*62*62&&p.cycleLength%4===0&&Number.isInteger(p.transientRounds)&&p.transientRounds>=0,'Complete final-cycle shape required');for(const f of ['A','B'])need(Number.isInteger(p.trainingSupport?.[f]?.neverTriedGreedyActions)&&p.trainingSupport[f].neverTriedGreedyActions>=0&&p.trainingSupport[f].neverTriedGreedyActions<=p.cycleLength,'Final cycle support required');}
  else need(p.cycleMetrics===null&&typeof p.reason==='string'&&p.reason.length,'Unavailable final cycle must be null with reason');
 }
 for(const [list,treatment,steps]of[[data.checkpointStatuses,'full-grid-after-cap',[1000000,2000000]],[data.inheritedComparisonStatuses,'startup-guard',[2000000]]])for(const s of list){
  const key=s.runId+'--t'+s.step;need(SEEDS.includes(s.seed)&&s.runId===runId(s.seed,treatment)&&steps.includes(s.step)&&!statuses.has(key)&&typeof s.scientificAvailable==='boolean'&&typeof s.status==='string','Checkpoint scope/identity differs');
  need(s.scientificAvailable?s.reason===null:typeof s.reason==='string'&&s.reason.length,'Checkpoint availability/reason differs');statuses.set(key,s);
 }
 let sum=rational(0n),count=0;const pairedSeeds=new Set();
 for(const seed of SEEDS){
  const entries=Object.fromEntries(ARMS.map(t=>[t,policies.get(cpId(seed,t))]));
  for(const t of ARMS)need(entries[t]&&statuses.get(cpId(seed,t))?.scientificAvailable===entries[t].available,'Final policy/status availability differs');
  createReferenceReplay({finiteGame:data.finiteGame,seed,treatments:entries});
  const row=data.pairedRows.find(r=>r.seed===seed);need(row&&!pairedSeeds.has(seed)&&JSON.stringify(row.runIds)===JSON.stringify(ARMS.map(t=>runId(seed,t)))&&row.cycleCustomerBenefits?.length===2,'Planned pair identity differs');pairedSeeds.add(seed);
  const available=ARMS.every(t=>entries[t].available);need(row.available===available,'Paired scientific availability differs');
  for(let i=0;i<2;i++)if(entries[ARMS[i]].available)need(equal(ratio(row.cycleCustomerBenefits[i]),ratio(entries[ARMS[i]].cycleMetrics.consumerSurplus)),'Paired cycle statistic differs');else need(row.cycleCustomerBenefits[i]===null,'Unavailable endpoint value must stay null');
  if(available){const delta=subtract(ratio(row.cycleCustomerBenefits[1]),ratio(row.cycleCustomerBenefits[0]));need(equal(delta,ratio(row.difference)),'Paired signed difference differs');sum=add(sum,delta);count++;}
  else need(row.difference===null&&typeof row.unavailableReason==='string'&&row.unavailableReason.length,'Unavailable pair must retain null/reason');
 }
 need(new Set(data.pairedRows.map(r=>r.seed)).size===12,'Duplicate paired rows');
 const p=data.primarySummary;need(p?.plannedDenominator===12&&p.availablePairs===count&&p.available===(count===12),'Planned denominator/availability differs');
 if(p.available)need(equal(ratio(p.meanDifference),divideInteger(sum,12)),'Planned twelve-pair mean differs');else need(p.meanDifference===null&&typeof p.unavailableReason==='string'&&p.unavailableReason.length,'Missing final cannot have planned mean');
 need(data.completePairDescription?.denominator===count&&JSON.stringify(data.completePairDescription.seedIds)===JSON.stringify(SEEDS.filter(seed=>data.pairedRows.find(r=>r.seed===seed).available)),'Available-pair denominator differs');
 if(meta.fullTrainingReplay||meta.replayComplete)need(meta.fullTrainingReplay&&meta.replayComplete&&data.checkpointStatuses.every(s=>s.scientificAvailable),'Complete new replay cannot omit secondary checkpoint slots');
 validateAnchors(data.anchors,data.finiteGame?.finite??data.finiteGame);
 return data;
}
function validateAnchors(a,finite){
 need(a&&typeof a.available==='boolean','Explicit static-anchor availability required');
 if(!a.available){need(a.values===null&&typeof a.reason==='string'&&a.reason.length,'Unavailable anchors must be null with reason');return;}
 need(a.independentAgreement===true&&a.reason===null&&a.provenance&&a.values?.n===finite.prices.length,'Independently agreed anchor identity required');
 const v=a.values,n=v.n,seen=new Set();
 for(const[group,kind]of[[v.pureNash,'Nash'],[v.jointProfitMaximum,'joint']]){
  need(Number.isInteger(group?.count)&&group.count===group.pairs?.length&&(kind==='Nash'||group.count>0),'Complete static anchor set required');seen.clear();
  if(kind==='Nash')need(group.count?group.reason===null:typeof group.reason==='string'&&group.reason.length,'Empty pure Nash set needs explicit explanation');
  for(const p of group.pairs){const pair=p.indices;need(pair?.length===2&&pair.every(i=>Number.isInteger(i)&&i>=0&&i<n)&&!seen.has(pair.join(',')),'Static anchor pair identity differs');seen.add(pair.join(','));const k=pair[0]*n+pair[1];
   for(let i=0;i<2;i++)need(equal(ratio(p.prices?.[i]),fromDouble(finite.prices[pair[i]])),'Static anchor price differs from original grid');
   const A=fromDouble(finite.rewards.profitA[k]),B=fromDouble(finite.rewards.profitB[k]);need(equal(ratio(p.profits?.A),A)&&equal(ratio(p.profits?.B),B)&&equal(ratio(p.profits?.joint),add(A,B))&&equal(ratio(p.consumerSurplus),fromDouble(finite.rewards.consumerSurplus[k])),'Static anchor values differ from saved exact weights');
   if(kind==='joint')need(equal(ratio(group.value),ratio(p.profits.joint)),'Joint-maximizer value differs');
  }
 }
 // Completeness/optimality of these sets is established by the bound audit;
 // this browser checks shape/values, not an independent stage-game theorem.
}

export function mount(data,doc=globalThis.document){
 validateEvidence(data);const el=id=>{const e=doc.getElementById(id);need(e,'Missing page element '+id);return e;},set=(id,v)=>el(id).textContent=v;let seed=907001,replay;
 const entry=t=>data.finalPolicies.find(p=>p.seed===seed&&p.treatment===t);
 el('seed').innerHTML=SEEDS.map(s=>`<option value="${s}">Example ${s-907000} of 12</option>`).join('');el('seed').value=String(seed);
 function choose(){seed=Number(el('seed').value);need(SEEDS.includes(seed),'Unknown planned seed');replay=createReferenceReplay({finiteGame:data.finiteGame,seed,treatments:Object.fromEntries(ARMS.map(t=>[t,entry(t)]))});render();set('feedback',replay.snapshot().available?'Ready to watch. No new customer benefit or profits earned yet.':replay.snapshot().reason);}
 function shops(t,s){return ['A','B'].map((shop,f)=>{const r=s.latest,q=r?.quantities[f]??null;return `<div class="matched-shop shop-${shop.toLowerCase()}"><span>SHOP ${shop} · ${f?'DASHED':'SOLID'}</span><div class="shop-roof" aria-hidden="true"></div><div class="shop-face"><span>${r?'Latest replay execution':'Saved memory · unearned'}</span><strong>${formatAmount(r?r.prices[f]:s.previousPrices[f],6)}</strong><div class="shop-reward"><p>Expected purchases<strong>${formatAmount(q,2)}</strong></p><p>This round’s profit<strong>${formatAmount(r?.profits[f])}</strong></p></div></div>${basketGraphic(q,t+shop)}</div>`;}).join('');}
 function drawPrefix(s){
  if(!s.trace.length){el('prefix-chart').innerHTML='<text x="360" y="135" text-anchor="middle" font-size="18">Run a round to draw the new replay.</text>';return;}
  const values=s.trace.flatMap(r=>ARMS.map(t=>r[t].consumerSurplus)),lo=Math.min(...values),hi=Math.max(...values),span=Math.max(.01,hi-lo),min=lo-span*.1,max=hi+span*.1,x=i=>s.trace.length===1?92:72+i*620/(s.trace.length-1),y=v=>220-(v-min)/(max-min)*180;let h='';
  for(let i=0;i<3;i++){const v=min+(max-min)*i/2;h+=`<path d="M72 ${y(v)}H692" stroke="#ded7ca"/><text x="62" y="${y(v)+5}" text-anchor="end" font-size="15">${esc(formatAmount(v,2))}</text>`;}
  for(const t of ARMS){h+=`<polyline points="${s.trace.map((r,i)=>x(i)+','+y(r[t].consumerSurplus)).join(' ')}" fill="none" stroke="${ARM_COLORS[t]}" stroke-width="3" stroke-dasharray="${t===ARMS[1]?'8 5':''}"/>`;s.trace.forEach((r,i)=>{const xx=x(i),yy=y(r[t].consumerSurplus),last=i===s.trace.length-1;h+=last&&t===ARMS[1]?`<rect x="${xx-6}" y="${yy-6}" width="12" height="12" fill="none" stroke="${ARM_COLORS[t]}" stroke-width="2.5"/>`:`<circle cx="${xx}" cy="${yy}" r="${last?5:2.5}" fill="${ARM_COLORS[t]}"/>`;});}
  h+=`<text x="72" y="257" font-size="15">Round ${s.trace[0].round}</text><text x="692" y="257" text-anchor="end" font-size="15">Round ${s.trace.at(-1).round}</text>`;el('prefix-chart').innerHTML=h;
 }
 function render(){const s=replay.snapshot();const supportCopy=ARMS.map(t=>{const p=entry(t);return p.available?`${label(t)}: never-tried actions on the saved cycle A${p.trainingSupport.A.neverTriedGreedyActions}, B${p.trainingSupport.B.neverTriedGreedyActions}.`:label(t)+': '+p.reason;}).join(' ');set('endpoint-details',`Seed ${seed} · ${s.available?'both accepted actual final 2M histories · NEXT phase4 in both versions':'final 2M comparison has an unavailable endpoint; no paired continuation is executed'}. No reset or fresh initial cap. ${supportCopy} Support does not establish convergence.`);set('selection-copy',`Example ${seed-907000} of 12 · starts after learning, where each pair of shops stopped. No new initial ceiling.`);set('round-counter',`${s.executions} ${s.executions===1?'round watched':'rounds watched'} · replay limit4,096`);
  for(const id of ['run-one','mobile-advance'])el(id).disabled=!s.canAdvance;for(const id of ['undo','mobile-undo'])el(id).disabled=!s.canUndo;el('run-twenty').disabled=!s.available||s.executions+20>4096;el('restart').disabled=!s.available;set('mobile-replay-count',`${s.executions} ${s.executions===1?'round watched':'rounds watched'}`);
  for(const t of ARMS){const a=s.treatments[t],p=entry(t);set(t+'-cycle',p.available?formatAmount(p.cycleMetrics.consumerSurplus):'Unavailable');set(t+'-lengths',p.available?`${p.transientRounds} rounds before a repeating pattern of ${p.cycleLength} rounds. A repeating pattern is not proof that learning converged.`:p.reason);
   if(s.available){set(t+'-rule',t===ARMS[0]?'Guard stays on: the original profit-based rule restricts their price choices.':'Guard removed: any price on the original board is permitted.');set(t+'-memory',`Last completed prices: A ${formatAmount(a.previousPrices[0],6)} · B ${formatAmount(a.previousPrices[1],6)} → the saved shops choose next`);el(t+'-shops').innerHTML=shops(t,a);set(t+'-latest',formatAmount(a.latest?.consumerSurplus));set(t+'-prefix',formatAmount(a.earned?.customerBenefit.average));}
   else{set(t+'-rule','Paired replay locked: '+s.reason);set(t+'-memory','No new execution or reward');el(t+'-shops').innerHTML='';set(t+'-latest','—');set(t+'-prefix','—');}
  }
  set('finite-difference',s.finiteBenefitDifference?`Customer-benefit difference since you started: ${formatAmount(s.finiteBenefitDifference.average,3,{signed:true})} (guard removed minus guard kept). This short replay is separate from the whole repeating-pattern average.`:'Watch one round to compare the newly earned customer benefit.');drawPrefix(s);
  el('training-copy').innerHTML=ARMS.map(t=>`<p><b>${label(t)}</b>: preceding training-window benefit ${entry(t).trainingTail?.metrics?.consumerSurplus?esc(formatAmount(entry(t).trainingTail.metrics.consumerSurplus)):'unavailable'}.</p>`).join('');
 }
 function evidence(){const p=data.primarySummary;set('primary-mean',p.available?formatAmount(p.meanDifference,3,{signed:true}):'Unavailable');set('mean-copy',p.available?'Average of all twelve saved repeating-pattern differences. Readouts are rounded; retained fractions are exact. No confidence interval or significance claim.':p.unavailableReason);
  const rows=data.pairedRows,values=rows.filter(r=>r.available).map(r=>approximate(ratio(r.difference))),scale=225/Math.max(...values.map(Math.abs),.000001),zero=355;let h='<path d="M355 25V420" stroke="#777165"/><text x="355" y="18" text-anchor="middle" font-size="15">0</text>';
  rows.forEach((r,i)=>{const y=42+i*31;h+=`<text x="22" y="${y+5}" font-size="15">Example ${i+1}</text>`;if(!r.available){h+=`<text x="390" y="${y+5}" font-size="15">Unavailable</text>`;return;}const v=ratio(r.difference),width=v.n===0n?0:Math.max(1,Math.abs(approximate(v))*scale);h+=v.n===0n?`<circle cx="${zero}" cy="${y}" r="4" fill="${DIFFERENCE_COLORS.zero}"/>`:`<rect x="${v.n<0n?zero-width:zero}" y="${y-9}" width="${width}" height="18" fill="${v.n<0n?DIFFERENCE_COLORS.negative:DIFFERENCE_COLORS.positive}"/>`;h+=`<text x="610" y="${y+5}" font-size="15">${esc(formatAmount(r.difference,3,{signed:true}))}</text>`;});el('paired-chart').innerHTML=h;
  el('paired-table').innerHTML='<table><thead><tr><th>Example / seed</th><th>Guard stays on</th><th>Guard removed</th><th>Removed minus kept</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>Example ${r.seed-907000}<br><small>seed ${r.seed}</small></td><td>${formatAmount(r.cycleCustomerBenefits[0])}</td><td>${formatAmount(r.cycleCustomerBenefits[1])}</td><td>${r.available?esc(formatAmount(r.difference,3,{signed:true})):esc(r.unavailableReason)}</td></tr>`).join('')+'</tbody></table>';
  const statusTable=(list,scope)=>`<h3>${scope}</h3><table><thead><tr><th>Seed</th><th>Step</th><th>Endpoint status</th></tr></thead><tbody>`+list.map(c=>`<tr><td>${c.seed}</td><td>${c.step}</td><td>${esc(c.scientificAvailable?'Accepted':c.reason)}</td></tr>`).join('')+'</tbody></table>';
  el('checkpoint-table').innerHTML=statusTable(data.checkpointStatuses,'24 new reference checkpoint slots')+statusTable(data.inheritedComparisonStatuses,'12 inherited startup-guard final comparisons');
  set('replay-scope',data.meta.fullTrainingReplay&&data.meta.replayComplete?'All twelve new 2M streams, all24 checkpoint comparisons and2,400 recorded transcript blocks were independently replayed. Older startup-guard endpoints reuse their separate accepted replay.':'Inventory checked. New complete-study replay is not claimed; accepted final endpoints and missing secondary checkpoints remain distinct.');
  set('provenance-copy',`New audit ${data.meta.independentAuditSha256}; inherited startup-guard audit ${data.meta.startupGuardAuditSha256}; new manifest ${data.meta.primaryManifestSha256}. Browser hash strings are provenance labels, not a scientific audit. Default chosen before new reference outcomes, after earlier studies.`);
  const a=data.anchors;set('anchor-status',a.available?`${a.values.pureNash.count} static pure Nash pairs; ${a.values.jointProfitMaximum.count} exact joint-profit maximizing pairs. No tie has been selected as a convenient score.`:'Static anchors unavailable: '+a.reason);
  el('anchor-table').innerHTML=a.available?[['Pure Nash pairs',a.values.pureNash],['Joint-profit maximizing pairs',a.values.jointProfitMaximum]].map(([name,g])=>`<h3>${name}</h3>`+(g.count?'<table><thead><tr><th>Original indices A/B</th><th>Prices A/B</th><th>Profit A</th><th>Profit B</th><th>Joint profit</th><th>Customer benefit</th></tr></thead><tbody>'+g.pairs.map(p=>`<tr><td>${p.indices.join(' / ')}</td><td>${p.prices.map(v=>formatAmount(v,6)).join(' / ')}</td><td>${formatAmount(p.profits.A)}</td><td>${formatAmount(p.profits.B)}</td><td>${formatAmount(p.profits.joint)}</td><td>${formatAmount(p.consumerSurplus)}</td></tr>`).join('')+'</tbody></table>':`<p>${esc(g.reason)}</p>`)).join(''):'';
 }
 el('seed').addEventListener('change',choose);for(const[id,action]of[['run-one',()=>replay.advance()],['run-twenty',()=>replay.advance(20)],['undo',()=>replay.undo()],['restart',()=>replay.restart()],['mobile-advance',()=>replay.advance()],['mobile-undo',()=>replay.undo()]])el(id).addEventListener('click',()=>{try{action();render();set('feedback',id==='restart'?'Playback restarted at both saved starting points; watched earnings cleared.':['undo','mobile-undo'].includes(id)?'Undid 1 round in both versions. No new prices or rewards were earned.':'Both versions advanced together. You control playback; the saved shops choose prices. No new learning occurred.');}catch(e){set('feedback',e.message);}});
 evidence();choose();el('reference-app').hidden=false;set('load-status','Evidence inventory checked. Each final endpoint and its support treatment are validated separately.');return{get replay(){return replay;},select(s){el('seed').value=String(s);choose();},render};
}
export async function boot(doc=globalThis.document,fetcher=globalThis.fetch){try{const response=await fetcher('/local-pricing-guard/reference-data.json');need(response.ok,'Accepted reference evidence unavailable');return mount(await response.json(),doc);}catch(e){const app=doc.getElementById('reference-app');if(app)app.hidden=true;for(const id of ['run-one','run-twenty','undo','restart','mobile-advance','mobile-undo']){const button=doc.getElementById(id);if(button)button.disabled=true;}doc.getElementById('load-status').textContent='Comparison locked: '+e.message+'. No example outcomes inserted.';return null;}}
if(typeof document!=='undefined')void boot();

