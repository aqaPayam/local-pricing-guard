import {createPairedReplay} from '/local-pricing-guard/matched-clock-game.js';

import {rational,add,subtract,divideInteger,fromJSON,approximate} from '/local-pricing-guard/recurring-game.js';

const need=(ok,message)=>{if(!ok)throw Error(message);},ARMS=['startup','recurring4'],SEEDS=Array.from({length:12},(_,i)=>907001+i);

const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),hash=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);

const ARM_COLORS={startup:'#75634a',recurring4:'#3c6c50'},DIFFERENCE_COLORS={positive:'#3c6c50',negative:'#9a4b4b',zero:'#777165'};

const runId=(seed,arm)=>`base-g15-t1--matched5-${arm}--zero--s${seed}`,cpId=(seed,arm,step)=>runId(seed,arm)+`--t${step}`;

function ratio(v){need(v&&typeof v.numerator==='string'&&/^-?(0|[1-9]\d*)$/.test(v.numerator)&&typeof v.denominator==='string'&&/^[1-9]\d*$/.test(v.denominator)&&v.numerator.length<=2048&&v.denominator.length<=2048,'Malformed exact saved-weight ratio');return fromJSON(v);}

const equal=(a,b)=>a.n*b.d===b.n*a.d;

export function formatAmount(v,digits=3,{signed=false}={}){

 if(v===null||v===undefined)return '—';const exact=typeof v==='object'?ratio(v):null,x=exact?approximate(exact):v;need(Number.isFinite(x),'Nonfinite display');const sign=exact?(exact.n<0n?-1:exact.n>0n?1:0):Math.sign(x);if(!sign)return '0';

 let out;if(x===0&&exact){const a=(exact.n<0n?-exact.n:exact.n).toString(),b=exact.d.toString(),leadA=Number(a.slice(0,15))/10**(Math.min(15,a.length)-1),leadB=Number(b.slice(0,15))/10**(Math.min(15,b.length)-1);let lead=leadA/leadB,power=a.length-b.length;if(lead<1){lead*=10;power--;}if(lead>=10){lead/=10;power++;}out=(sign<0?'-':'')+lead.toFixed(3)+'e'+power;}else out=Math.abs(x)<10**-digits||Math.abs(x)>=1e7?x.toExponential(3).replace('e+','e'):x.toFixed(digits);

 return signed&&sign>0?'+'+out:out;

}

export function validateEvidence(data){

 const meta=data?.meta;need(data?.schemaVersion===1&&meta?.inventoryAccepted===true&&meta.independentAuditPassed===true&&meta.audit?.passed===true,'Authoritative evidence inventory acceptance required');

 need(hash(meta.independentAuditSha256)&&hash(meta.primaryManifestSha256)&&typeof meta.fullTrainingReplay==='boolean'&&typeof meta.replayComplete==='boolean','Evidence provenance/replay flags malformed');

 const d=meta.defaultSelection;need(d?.seed===907001&&d.checkpointStep===2000000&&JSON.stringify(d.arms)===JSON.stringify(ARMS)&&d.chosenBeforeMatchedOutcomeInspection===true,'Retained matched-study default differs');

 need(JSON.stringify(data.orderedSeeds)===JSON.stringify(SEEDS)&&data.runs?.length===24&&data.checkpoints?.length===48&&data.finalPolicyPairs?.length===24&&data.pairedRows?.length===12,'Complete planned inventory required');

 const runs=new Map(data.runs.map(r=>[r.id,r])),cps=new Map(data.checkpoints.map(c=>[c.id,c])),policies=new Map(data.finalPolicyPairs.map(p=>[p.checkpointId,p]));need(runs.size===24&&cps.size===48&&policies.size===24,'Duplicate planned identities');

 let acceptedPairs=0,sum=rational(0n);

 for(const seed of SEEDS){

  const selected={};for(const arm of ARMS){const id=runId(seed,arm),run=runs.get(id);need(run?.seed===seed&&run.arm===arm,'Run identity mismatch');

   for(const step of [1000000,2000000]){const c=cps.get(cpId(seed,arm,step));need(c?.runId===id&&c.seed===seed&&c.arm===arm&&c.step===step&&typeof c.scientificAvailable==='boolean'&&typeof c.status==='string','Checkpoint identity/status mismatch');if(c.scientificAvailable){need(c.replayStatus?.accepted===true&&c.terminal?.phase===4&&c.terminal.previousIndices?.length===2&&c.frozen?.actualTerminal?.cycleMetrics,'Accepted endpoint data missing');ratio(c.frozen.actualTerminal.cycleMetrics.consumerSurplus);const a=c.frozen.actualTerminal;need(Number.isInteger(a.transientRounds)&&a.transientRounds>=0&&Array.isArray(a.cycleNodesFromStart)&&a.cycleNodesFromStart.length>0&&a.cycleNodesFromStart.length<=5*62*62,'Complete cycle/transient shape required');for(const firm of ['A','B'])need(Number.isInteger(a.trainingSupport?.[firm]?.neverTriedGreedyActions)&&a.trainingSupport[firm].neverTriedGreedyActions>=0&&a.trainingSupport[firm].neverTriedGreedyActions<=a.cycleNodesFromStart.length,'Cycle chosen-action support required');}else need(typeof c.reason==='string'&&c.reason.length&&c.frozen===null,'Unavailable endpoint must retain null values/reason');}

   const c=cps.get(cpId(seed,arm,2000000)),p=policies.get(c.id);need(p?.runId===id&&p.arm===arm&&p.seed===seed&&p.available===c.scientificAvailable,'Final policy/endpoint availability differs');if(p.available)need(p.start.phase===c.terminal.phase&&JSON.stringify(p.start.previousIndices)===JSON.stringify(c.terminal.previousIndices),'Policy actual start differs');selected[arm]=p;

  }

  createPairedReplay({finiteGame:data.finiteGame,seed,arms:selected});

  const row=data.pairedRows.find(r=>r.seed===seed),available=ARMS.every(a=>selected[a].available);need(row&&row.available===available,'Paired availability differs');

  if(available){for(const arm of ARMS){need(row[arm]?.checkpointId===cpId(seed,arm,2000000),'Paired checkpoint differs');need(equal(ratio(row[arm].consumerSurplus),ratio(cps.get(row[arm].checkpointId).frozen.actualTerminal.cycleMetrics.consumerSurplus)),'Paired cycle value differs');}const diff=subtract(ratio(row.recurring4.consumerSurplus),ratio(row.startup.consumerSurplus));need(equal(diff,ratio(row.difference)),'Paired signed difference differs');sum=add(sum,diff);acceptedPairs++;}else need(row.difference===null&&typeof row.reason==='string'&&row.reason.length,'Unavailable pair requires null/reason');

 }

 const primary=data.primarySummary;need(primary?.plannedPairs===12&&primary.acceptedPairs===acceptedPairs&&primary.available===(acceptedPairs===12),'Primary denominator/availability differs');if(primary.available)need(equal(ratio(primary.mean),divideInteger(sum,12)),'Planned mean differs');else need(primary.mean===null&&typeof primary.reason==='string','Missing final pair cannot have a planned mean');

 if(meta.fullTrainingReplay||meta.replayComplete)need(meta.fullTrainingReplay&&meta.replayComplete&&data.checkpoints.every(c=>c.scientificAvailable&&c.replayStatus.accepted),'Aggregate replay cannot omit secondary checkpoints');return data;

}

export function basketGraphic(quantity,tag){

 if(quantity===null)return '<span>No new purchases</span>';need(Number.isFinite(quantity)&&quantity>=0,'Invalid expected purchases');let marks='';for(let i=0;i<10;i++){const x=3+i*27,fill=Math.max(0,Math.min(1,quantity/10-i));marks+=`<rect x="${x}" y="12" width="21" height="14" rx="2" fill="#e5dfd1"/><rect x="${x}" y="${26-fill*14}" width="21" height="${fill*14}" fill="currentColor"/><path d="M${x} 12h21l-3 14h-15zM${x+5} 12l3-7h5l3 7" fill="none" stroke="currentColor" stroke-width="1.3"/>`;}return `<svg viewBox="0 0 274 30" aria-hidden="true" data-baskets="${esc(tag)}">${marks}</svg>`;

}

export function mount(data,doc=globalThis.document){

 validateEvidence(data);const el=id=>{const x=doc.getElementById(id);need(x,'Missing page element '+id);return x;},set=(id,v)=>el(id).textContent=v;let seed=907001,replay=null;

 const checkpoint=arm=>data.checkpoints.find(c=>c.id===cpId(seed,arm,2000000));

 el('seed').innerHTML=SEEDS.map(s=>`<option value="${s}">Seed ${s}</option>`).join('');el('seed').value=String(seed);

 function choose(){seed=Number(el('seed').value);need(SEEDS.includes(seed),'Unknown planned seed');const arms=Object.fromEntries(ARMS.map(a=>[a,data.finalPolicyPairs.find(p=>p.checkpointId===cpId(seed,a,2000000))]));replay=createPairedReplay({finiteGame:data.finiteGame,seed,arms});render();set('feedback',replay.snapshot().available?'Saved endpoints ready. No newly earned rewards yet.':replay.snapshot().reason);}

 function shops(arm,s){return ['A','B'].map((shop,f)=>{const r=s.latest,price=r?r.prices[f]:null,quantity=r?r.quantities[f]:null,profit=r?r.profits[f]:null;return `<div class="matched-shop shop-${shop.toLowerCase()}"><span>SHOP ${shop} · ${f?'DASHED':'SOLID'}</span><div class="shop-roof" aria-hidden="true"></div><div class="shop-face"><span>${r?'Latest replay execution':'Saved memory · unearned'}</span><strong>${r?formatAmount(price,6):formatAmount(s.previousPrices[f],6)}</strong><div class="shop-reward"><p>Expected purchases<strong>${formatAmount(quantity,2)}</strong></p><p>This round’s profit<strong>${formatAmount(profit)}</strong></p></div></div>${basketGraphic(quantity,arm+shop)}</div>`;}).join('');}

 function drawPrefix(s){if(!s.trace.length){el('prefix-chart').innerHTML='<text x="360" y="135" text-anchor="middle" font-size="18">Run a round to draw the new replay.</text>';return;}const values=s.trace.flatMap(r=>ARMS.map(a=>r[a].consumerSurplus)),lo=Math.min(...values),hi=Math.max(...values),span=Math.max(.01,hi-lo),min=lo-span*.1,max=hi+span*.1,x=i=>s.trace.length===1?92:72+i*620/(s.trace.length-1),y=v=>220-(v-min)/(max-min)*180;let h='';for(let i=0;i<3;i++){const v=min+(max-min)*i/2;h+=`<path d="M72 ${y(v)}H692" stroke="#ded7ca"/><text x="62" y="${y(v)+5}" text-anchor="end" font-size="15">${esc(formatAmount(v,2))}</text>`;}for(const[arm,color,dash]of[['startup',ARM_COLORS.startup,''],['recurring4',ARM_COLORS.recurring4,'8 5']]){h+=`<polyline points="${s.trace.map((r,i)=>x(i)+','+y(r[arm].consumerSurplus)).join(' ')}" fill="none" stroke="${color}" stroke-width="3" stroke-dasharray="${dash}"/>`;s.trace.forEach((r,i)=>{const xx=x(i),yy=y(r[arm].consumerSurplus),last=i===s.trace.length-1;if(last&&arm==='recurring4')h+=`<rect x="${xx-6}" y="${yy-6}" width="12" height="12" fill="none" stroke="${color}" stroke-width="2.5"/>`;else h+=`<circle cx="${xx}" cy="${yy}" r="${last?5:2.5}" fill="${color}" stroke="#fffdf7" stroke-width="${last?1:0}"/>`;});}h+='<text x="72" y="257" font-size="15">Round '+s.trace[0].round+'</text><text x="692" y="257" text-anchor="end" font-size="15">Round '+s.trace.at(-1).round+'</text>';el('prefix-chart').innerHTML=h;}

 function render(){const s=replay.snapshot();set('selection-copy',`Seed ${seed} · final 2M actual histories · NEXT phase 4 in both worlds. No fresh initial limit is inserted.`);set('round-counter',`${s.executions} new frozen rounds · limit 4,096`);el('run-one').disabled=!s.canAdvance;el('run-twenty').disabled=!s.available||s.executions+20>4096;el('undo').disabled=!s.canUndo;el('restart').disabled=!s.available;el('mobile-advance').disabled=!s.canAdvance;el('mobile-undo').disabled=!s.canUndo;set('mobile-replay-count',`Frozen replay · ${s.executions} ${s.executions===1?'round':'rounds'}`);

  for(const arm of ARMS){const cp=checkpoint(arm),a=s.arms[arm];set(arm+'-cycle',cp.scientificAvailable?formatAmount(cp.frozen.actualTerminal.cycleMetrics.consumerSurplus):'Unavailable');set(arm+'-lengths',cp.scientificAvailable?`${cp.frozen.actualTerminal.transientRounds} transient rounds, then ${cp.frozen.actualTerminal.cycleNodesFromStart.length} rounds per complete cycle. Never-tried cycle actions: Shop A ${cp.frozen.actualTerminal.trainingSupport.A.neverTriedGreedyActions}, Shop B ${cp.frozen.actualTerminal.trainingSupport.B.neverTriedGreedyActions}. Support does not prove convergence.`:cp.reason);

   if(s.available){set(arm+'-rule',`Next clock step ${a.phase}: ${a.nextIsCap?'price limit replaces the guard':'ordinary guard'}. ${a.capExecutions} cap executions in this new replay.`);set(arm+'-memory',`Previous A ${formatAmount(a.previousPrices[0],6)} · previous B ${formatAmount(a.previousPrices[1],6)} → both saved quotes`);el(arm+'-shops').innerHTML=shops(arm,a);set(arm+'-latest',formatAmount(a.latest?.consumerSurplus));set(arm+'-prefix',formatAmount(a.earned?.customerBenefit.average));}

   else{set(arm+'-rule','Paired replay locked: '+s.reason);set(arm+'-memory','No new execution or reward');el(arm+'-shops').innerHTML='';set(arm+'-latest','—');set(arm+'-prefix','—');}}

  set('finite-difference',s.finiteBenefitDifference?`Current finite-prefix average difference: ${formatAmount(s.finiteBenefitDifference.average,3,{signed:true})}. This is separate from the complete-cycle comparison.`:'No finite-prefix difference has been earned.');drawPrefix(s);

  el('training-copy').innerHTML=ARMS.map(a=>{const c=checkpoint(a),v=c.trainingTail?.metrics?.consumerSurplus;return `<p><b>${a==='startup'?'One initial limit':'Repeated limits'}</b>: preceding training-window benefit ${v?esc(formatAmount(v)):'unavailable'}.</p>`;}).join('');

 }

 function evidence(){const p=data.primarySummary;set('primary-mean',p.available?formatAmount(p.mean,3,{signed:true}):'Unavailable');set('mean-copy',p.available?'Exact saved-weight mean of all twelve paired final-cycle differences. No confidence interval or significance claim.':p.reason);const rows=data.pairedRows,values=rows.filter(r=>r.available).map(r=>approximate(ratio(r.difference))),max=Math.max(...values.map(Math.abs),.000001),zero=355,scale=225/max;let h='<path d="M355 25V420" stroke="#777165"/><text x="355" y="18" text-anchor="middle" font-size="15">0</text>';

  rows.forEach((r,i)=>{const y=42+i*31;h+=`<text x="22" y="${y+5}" font-size="15">${r.seed}</text>`;if(r.available){const exact=ratio(r.difference),v=approximate(exact),width=exact.n===0n?0:Math.max(1,Math.abs(v)*scale),x=exact.n<0n?zero-width:zero;h+=exact.n===0n?`<circle cx="${zero}" cy="${y}" r="4" fill="${DIFFERENCE_COLORS.zero}"/>`:`<rect x="${x}" y="${y-9}" width="${width}" height="18" fill="${exact.n<0n?DIFFERENCE_COLORS.negative:DIFFERENCE_COLORS.positive}"/>`;h+=`<text x="610" y="${y+5}" font-size="15">${esc(formatAmount(r.difference,3,{signed:true}))}</text>`;}else h+=`<text x="390" y="${y+5}" font-size="15">Unavailable</text>`;});el('paired-chart').innerHTML=h;

  el('paired-table').innerHTML='<table><thead><tr><th>Seed</th><th>One initial limit</th><th>Repeated limits</th><th>Difference</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>${r.seed}</td><td>${r.available?esc(formatAmount(r.startup.consumerSurplus)):'—'}</td><td>${r.available?esc(formatAmount(r.recurring4.consumerSurplus)):'—'}</td><td>${r.available?esc(formatAmount(r.difference,3,{signed:true})):esc(r.reason)}</td></tr>`).join('')+'</tbody></table>';

  el('checkpoint-table').innerHTML='<table><thead><tr><th>Seed</th><th>Arm</th><th>Step</th><th>Endpoint status</th></tr></thead><tbody>'+data.checkpoints.map(c=>`<tr><td>${c.seed}</td><td>${c.arm==='startup'?'One initial limit':'Repeated limits'}</td><td>${c.step}</td><td>${esc(c.scientificAvailable?'Accepted':c.reason)}</td></tr>`).join('')+'</tbody></table>';

  set('replay-scope',data.meta.fullTrainingReplay&&data.meta.replayComplete?'All 24 two-million-round training streams, all 48 checkpoint comparisons and all recorded transcript blocks were independently replayed for this study.':'Inventory integrity accepted; complete replay assurance is not claimed. Endpoint-specific statuses and secondary failures remain visible.');set('provenance-copy',`Independent audit ${data.meta.independentAuditSha256}; manifest ${data.meta.primaryManifestSha256}. These are provenance labels, not browser cryptographic verification. Defaults were chosen before new matched-study outcomes, after earlier project results were known.`);

 }

 el('seed').addEventListener('change',choose);for(const[id,action]of[['run-one',()=>replay.advance()],['run-twenty',()=>replay.advance(20)],['undo',()=>replay.undo()],['restart',()=>replay.restart()],['mobile-advance',()=>replay.advance()],['mobile-undo',()=>replay.undo()]])el(id).addEventListener('click',()=>{try{action();render();set('feedback',id==='restart'?'Saved actual endpoints restored; new earnings cleared.':'Both worlds advanced or restored together. No learning occurred.');}catch(e){set('feedback',e.message);}});

 evidence();choose();el('matched-app').hidden=false;set('load-status','Evidence inventory checked. Endpoint availability is shown separately; replay uses saved frozen policies.');return{get replay(){return replay;},select(value){el('seed').value=String(value);choose();},render};

}

export async function boot(doc=globalThis.document,fetcher=globalThis.fetch){try{const response=await fetcher('/local-pricing-guard/matched-data.json');need(response.ok,'Accepted matched-study evidence is unavailable');return mount(await response.json(),doc);}catch(e){const app=doc.getElementById('matched-app');if(app)app.hidden=true;for(const id of ['run-one','run-twenty','undo','restart','mobile-advance','mobile-undo']){const button=doc.getElementById(id);if(button)button.disabled=true;}doc.getElementById('load-status').textContent='Comparison locked: '+e.message+'. No example outcomes have been inserted.';return null;}}

if(typeof document!=='undefined')void boot();

