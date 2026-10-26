import {createTimingGame,finiteTimingEnvelope} from '/local-pricing-guard/mixed-timing-game.js';
import {fromJSON,approximate,rational,add,subtract,multiplyInteger,divideInteger,compare} from '/local-pricing-guard/recurring-game.js';
const $=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names={'base-g15-t1':'Base · original 15-price label','scale0.5-g15-t1':'Demand scale 0.5','lower-quality-g15-t1':'Lower-quality market','lowcost-g15-t1':'Lower-cost market','base-g11-t1':'Base · original 11-price label','base-g31-t1':'Base · original 31-price label','base-g15-t0.5':'Base · half tolerance','base-g15-t2':'Base · double tolerance'};
const targetNames={'cap-90pct':'90% of original permanent-cap floor','cap-95pct':'95% of original permanent-cap floor','cap-99pct':'99% of original permanent-cap floor','cap-100pct':'100% of original permanent-cap floor','near-Nash-anchor-floor':'Original near-Nash anchor target'};
const kinds=['finite','effective','nominal'],hash=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x),need=(ok,message)=>{if(!ok)throw Error(message);};
const exact=x=>{need(x&&typeof x.numerator==='string'&&/^-?\d+$/.test(x.numerator)&&typeof x.denominator==='string'&&/^[1-9]\d*$/.test(x.denominator)&&x.numerator.length<5000&&x.denominator.length<5000,'Missing exact evidence value');return fromJSON(x);};
const decimalExact=x=>{const m=typeof x==='string'&&x.match(/^(-?)(\d+)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/);need(m&&x.length<5000,'Missing decimal enclosure');const places=(m[3]?.length??0)-Number(m[4]??0);need(Number.isSafeInteger(places)&&Math.abs(places)<=5000,'Decimal exponent outside display scope');const n=BigInt((m[1]??'')+m[2]+(m[3]??''));return places>=0?rational(n,10n**BigInt(places)):rational(n*10n**BigInt(-places));};
const val=x=>typeof x==='number'?x:approximate(exact(x.exact??x));
export function displayAmount(x,d=3){if(x===null||x===undefined)return '—';const v=val(x);need(Number.isFinite(v),'Nonfinite display value');const source=typeof x==='object'?(x.exact??x):null;if(v===0&&source&&BigInt(source.numerator)!==0n)return BigInt(source.numerator)>0n?'positive, very small':'negative, very small';return v!==0&&Math.abs(v)<.5*10**(-d)?v.toExponential(3):v.toFixed(d);}
const pct=x=>{const q=exact(x.exact??x);return displayAmount({exact:{numerator:String(q.n*100n),denominator:String(q.d)}},3)+'%';};
const rateRange=t=>t?.rates?.optimumRateDisplay?`[${t.rates.optimumRateDisplay.lower}, ${t.rates.optimumRateDisplay.upper}]`:'unavailable';
export function validateTimingData(data){
 need(data?.schemaVersion===1&&data.meta?.independentAuditPassed===true,'Accepted timing evidence is unavailable');
 const m=data.meta,a=m.audit;need(a?.passed===true&&a.requiresOrchestrator===false&&a.continuousChecksComputedInProcess===true&&a.models===24&&a.targetLabels===120,'Complete authoritative audit is required');
 for(const key of ['primaryManifestSha256','primaryResultsSha256','primaryIndexSha256','independentAuditSha256'])need(hash(m[key]),'Missing provenance identity');
 for(const [key,auditKey] of [['authoritativeAuditor','auditorSourceHash'],['controlAuditor','controlAuditorSourceHash'],['continuousAuditor','continuousAuditorSourceHash'],['inheritedArithmeticBackend','arithmeticBackendHash']])need(hash(m.sourceHashes?.[key])&&m.sourceHashes[key]===a[auditKey],'Independent source provenance labels differ');
 need(a.studyManifestHash===m.primaryManifestSha256&&a.resultsSha256===m.primaryResultsSha256&&a.indexSha256===m.primaryIndexSha256,'Inconsistent audit provenance labels');
 need(m.primaryAudit?.passed===true&&m.primaryAudit.requiresOrchestrator===false&&m.primaryAudit.continuousChecksComputedInProcess===true,'Component-only evidence cannot unlock play');
 need(Array.isArray(data.scenarioOrder)&&data.scenarioOrder.length===8&&new Set(data.scenarioOrder).size===8&&Array.isArray(data.targetOrder)&&data.targetOrder.length===5&&data.targetOrder.every(k=>Object.hasOwn(targetNames,k))&&new Set(data.targetOrder).size===5,'Incomplete scenario or target inventory');
 const d=m.defaultSelection;need(d?.kind==='finite'&&d.scenario==='base-g15-t1'&&d.target==='cap-95pct'&&d.calendar==='mixed'&&d.chosenBeforeOutcomeInspection===true,'Prospective default identity differs');
 need(data.models?.length===24&&data.finiteGames?.length===8,'All 24 models and eight finite games must remain visible');
 for(const [i,sid] of data.scenarioOrder.entries()){
  const record=data.finiteGames[i];need(record.scenario?.id===sid&&hash(m.finiteGameSources?.[sid]?.sha256)&&hash(m.finiteGameSources[sid].indexSha256),'Missing finite-game provenance');need(Number.isFinite(record.scenario.economy?.buyers)&&record.scenario.economy.buyers>0,'Missing modeled customer count');finiteTimingEnvelope(record);
  for(const kind of kinds){
   const rows=data.models.filter(r=>r.scenario===sid&&r.kind===kind);need(rows.length===1,'Missing or duplicated model');const model=rows[0];
   need(model.id===sid+'--'+kind&&model.targets?.length===5,'Missing model target slots');
   for(const [j,t] of model.targets.entries()){
    need(t.id===model.id+'--'+data.targetOrder[j]&&t.label===data.targetOrder[j]&&t.kind===kind&&t.scenario===sid&&typeof t.status==='string'&&typeof t.statusCategory==='string','Target identity differs');
    if(t.actualThresholdExact!==null)exact(t.actualThresholdExact);
    need(t.calendar&&['funded-mixed','fixed-safe','startup-only','unavailable'].includes(t.calendar.kind)&&Array.isArray(t.executionPreview),'Calendar evidence is missing');
    if(t.rates){const bounds=t.rates.optimumRateBoundsExact,lo=exact(bounds.lower),hi=exact(bounds.upper),made=exact(t.rates.constructedRateExact),shown=t.rates.optimumRateDisplay;need(lo.n>=0n&&compare(lo,hi)<=0&&compare(hi,rational(1n))<=0&&compare(made,hi)===0,'Malformed exact rate bounds');need(shown?.significantDigits===30&&compare(decimalExact(shown.lower),lo)<=0&&compare(decimalExact(shown.upper),hi)>=0,'Displayed optimum bounds do not enclose the exact bounds');}
    if(kind==='finite'&&t.calendar.kind!=='unavailable')createTimingGame(record,t);
   }
  }
 }
 return data;
}

let data,record,target,game,quotes=[null,null],notice='';
function selectedModel(kind='finite'){return data.models.find(m=>m.scenario===$('market').value&&m.kind===kind);}
function selectedTarget(kind='finite'){return selectedModel(kind).targets.find(t=>t.label===$('target').value);}
function restart(){
 record=data.finiteGames.find(r=>r.scenario.id===$('market').value);target=selectedTarget();quotes=[null,null];notice='';game=null;
 const fixed=target.frontier.bestFixedK??target.frontier.certifiedSafeK;
 $('schedule').innerHTML='<option value="mixed">Funded timing</option>'+`<option value="fixed"${Number.isInteger(fixed)?'':' disabled'}>${target.frontier.bestFixedK?`Same target’s best fixed gap · ${fixed} executions`:Number.isInteger(fixed)?`Certified fixed-safe fallback · ${fixed}`:'No finite best fixed gap'}</option>`;
 $('schedule').value=restart.mode??'mixed';
 try{game=createTimingGame(record,target,{mode:$('schedule').value});}catch(error){notice=error.message;}
 render();
}
function fill(which){if(!game)return;const allowed=[game.allowed(0),game.allowed(1)];quotes=allowed.map((s,f)=>which==='low'||which==='asymmetric'&&f===0?s[0]:s.at(-1));notice='Both next choices are filled. No reward is earned until you execute.';render();}
function execute(event){event?.preventDefault();if(!game)return;try{game.execute(...quotes);quotes=[null,null];notice='The two prices were executed together. Customer benefit and both profits now count.';}catch(error){notice=error.message;}render();}
function futureGaps(s){
 if(s.timing.kind==='startup-only')return `<div class="calendar-gap current"><b>${s.executions?'GUARD FOREVER':'FIRST CAP'}</b><strong>One cap</strong><small>No repeating calendar</small></div>`;
 let credit=exact(s.boundaryCredit.exact),rows=[];const a=exact(target.calendar.creditAExact),b=target.calendar.creditBExact?exact(target.calendar.creditBExact):null,K=s.timing.K;
 for(let k=0;k<5;k++){
  const length=k===0?s.chosenGapLength:K+(s.timing.kind==='funded-mixed'&&a.n>0n&&compare(credit,rational(-b.n,b.d))>=0?1:0),long=length===K+1;
  rows.push(`<div class="calendar-gap${k===0?' current':''}${long?' long':''}"><b>${k===0?'CURRENT GAP':'PLAN ONLY'}</b><strong>${length} executions</strong><small>CAP + ${length-1} guard</small><div class="calendar-dots">${Array.from({length:Math.min(length,12)},()=>'<i></i>').join('')}${length>12?'…':''}</div></div>`);
  credit=add(credit,long?b:a);
 }
 return rows.join('');
}
function render(){
 const s=game?.snapshot(),last=s?.latest;
 $('selection-copy').textContent=`This game uses ${record.finite.prices.length} saved quotes and the original physical cap ≈ ${displayAmount(record.cap.price,6)}. Changing a selector restarts only this local game. Both shops are your deliberate choices.`;
 $('quote-fields').disabled=!game;$('undo').disabled=!s?.canUndo;$('save').disabled=!s?.executions;
 $('execution-title').textContent=s?.executions?`After ${s.executions} real execution${s.executions===1?'':'s'}`:'Before the first execution';
 $('next-cap').textContent=!s?'Play locked':s.nextIsCap?'CAP NEXT':s.timing.kind==='startup-only'?'GUARD CONTINUES':`${s.movesUntilCap} guard execution${s.movesUntilCap===1?'':'s'} before next cap`;
 $('calendar-strip').innerHTML=s?futureGaps(s):'<p class="locked-message">No certified schedule is available for this selection. Its status stays visible below.</p>';
 $('calendar-copy').textContent=s?'Orange border: the current gap. Later tiles are plans, not executed rounds or earned rewards. A longer gap is funded only at a completed-gap boundary.':'Unavailable is not zero protection or a fabricated result.';
 $('phase-rule').textContent=!s?notice:s.nextIsCap?'The cap replaces the guard for this execution. Both shops may choose any saved price at or below the original cap.':'Each allowed set uses the other shop’s previous executed price. Changing one next choice does not change the other shop’s current allowed set.';
 $('actual-average').textContent=s?.averages?'≈ '+displayAmount(s.averages.consumerSurplus,4):'—';$('actual-round').textContent=last?'Latest round’s customer benefit ≈ '+displayAmount(last.consumerSurplus,4):'No customer benefit or profit counted yet';$('target-value').textContent=target.actualThresholdExact?'≈ '+displayAmount(target.actualThresholdExact,4):'Unavailable';$('proof-buffer').textContent=s?'≈ '+displayAmount(s.guaranteedBuffer,4):'Unavailable';
 $('boundary-credit').textContent=s?'≈ '+displayAmount(s.boundaryCredit,4):'—';$('actual-excess').textContent=s?'≈ '+displayAmount(s.actualExcess,4):'—';
 for(const [f,suffix] of [[0,'a'],[1,'b']]){
  const allowed=game?.allowed(f)??[];if(quotes[f]!==null&&!allowed.includes(quotes[f]))quotes[f]=null;
  $('last-price-'+suffix).textContent=last?displayAmount(last.prices[f],6):'—';$('last-profit-'+suffix).textContent=last?displayAmount(last.profits[f],3):'—';$('last-demand-'+suffix).textContent=last?displayAmount(last.quantities[f],2):'—';
  $('basket-'+suffix).innerHTML=last?baskets(last.quantities[f],f):'';
  $('quote-'+suffix).innerHTML='<option value="">Choose a permitted price…</option>'+record.finite.prices.map((p,i)=>`<option value="${i}"${allowed.includes(i)?'':' disabled'}>${displayAmount(p,6)} · #${i}</option>`).join('');$('quote-'+suffix).value=quotes[f]===null?'':String(quotes[f]);
  $('price-dots-'+suffix).innerHTML=record.finite.prices.map((_,i)=>`<i class="${allowed.includes(i)?'allowed':''}${quotes[f]===i?' chosen':''}"></i>`).join('');
  $('allowed-'+suffix).textContent=`${allowed.length} of ${record.finite.prices.length} saved quotes permitted. Every permitted quote is available.`;
  $('lagged-'+suffix).textContent=!s?'No execution available':s.nextIsCap?'This cap uses no rival-history restriction.':`Uses Shop ${f===0?'B':'A'}’s previous executed price ≈ ${displayAmount(s.previousPrices[1-f],6)}.`;
 }
 $('purchase-key').textContent=`A full basket represents about ${displayAmount(record.scenario.economy.buyers/20,2)} modeled expected purchases, not sampled customers. Every permitted saved quote remains selectable.`;
 $('old-history').textContent=s?.executions?'Only actual executions appear above. Previous public prices only determine the next guard choices.':'The initial high public prices are unearned memory. Last prices, purchases and profits stay blank until the first actual cap.';
 $('feedback').textContent=notice||(!s?'Choose another certified calendar to unlock play.':!s.executions?'Try the highest pair first to see the most adverse permitted customer-benefit path. The first round is a real cap.':s.executions===1?'Now compare the latest reward, running average and proof buffer. These are different quantities.':s.executions===2?'Lower manual prices can improve actual benefit. They do not change this guarantee-funded calendar.':'Your choices illustrate the rule; the guarantee comes from the complete independent calculation.');
 renderPreview();renderFunding(s);renderRates(s);renderCharts(s);renderEvidence();
}
function renderPreview(){
 const p=game?.preview(...quotes),valid=p?.legal===true;$('execute').disabled=!valid;
 $('quote-preview').textContent=valid?`Not executed: A ≈ ${displayAmount(p.prices[0],6)}, B ≈ ${displayAmount(p.prices[1],6)}; customer benefit ≈ ${displayAmount(p.consumerSurplus,4)}. Profit A ≈ ${displayAmount(p.profits[0],3)}, B ≈ ${displayAmount(p.profits[1],3)}.`:'Choose one permitted price for each shop. No price has been clipped or executed.';
}
function baskets(quantity,f){const unit=record.scenario.economy.buyers/20,count=Math.max(0,quantity/unit);return Array.from({length:Math.min(20,Math.ceil(count))},(_,i)=>`<svg class="basket-icon" viewBox="0 0 18 20" aria-hidden="true"><path d="M4 7Q4 1 9 1Q14 1 14 7" fill="none" stroke="${f?'#237a91':'#b84f36'}"/><rect x="1" y="7" width="16" height="12" rx="2" fill="#dce3d2"/><rect x="1" y="7" width="${16*Math.max(0,Math.min(1,count-i))}" height="12" rx="2" fill="${f?'#237a91':'#b84f36'}"/></svg>`).join('');}
function renderFunding(s){
 if(!s){$('funding-meter').innerHTML='';$('funding-copy').textContent='No guarantee is invented for unavailable evidence.';return;}
 if(s.timing.kind==='startup-only'){$('funding-meter').innerHTML='<strong class="funding-value">One cap is enough here.</strong>';$('funding-copy').textContent='For this target and finite price list, one startup cap followed by the guard protects every average from activation. The limiting cap frequency is zero.';return;}
 if(s.timing.kind!=='funded-mixed'){$('funding-meter').innerHTML=`<strong class="funding-value">Fixed gap: ${s.timing.K}</strong>`;$('funding-copy').textContent=target.frontier.bestFixedK?'You selected this same target’s best fixed integer gap. Compare its rhythm with funded timing.':'This is a certified fixed-safe fallback. The best timing remains unresolved or censored; no optimum is claimed.';return;}
 const b=exact(target.calendar.creditBExact),needed=rational(-b.n,b.d),credit=exact(s.boundaryCredit.exact),width=needed.n?Math.min(1,Math.max(0,approximate(rational(credit.n*needed.d,credit.d*needed.n)))):1;
 $('funding-meter').innerHTML=`<svg class="funding-meter" viewBox="0 0 280 40" role="img" aria-label="Completed-gap credit compared with the possible long-gap shortfall"><rect x="2" y="12" width="274" height="15" rx="6" fill="#d8e1cc"/><rect x="2" y="12" width="${274*width}" height="15" rx="6" fill="#799268"/><line x1="276" x2="276" y1="6" y2="33" stroke="#b84f36" stroke-width="2"/></svg><p class="fine">Funding needed for a longer gap: ≈ ${displayAmount({exact:{numerator:String(needed.n),denominator:String(needed.d)}},4)}</p>`;
 $('funding-copy').textContent=s.chosenGapLength===s.timing.K+1?'This longer gap is already funded by completed-gap credit. It can spend that credit before it ends. The following gap is decided using the credit left after completion.':'First complete enough short gaps to fund the possible benefit shortfall of a longer gap. Its credit can then fall while the activation average stays protected.';
}
function renderRates(s){
 const r=target.rates;if(!r){$('rate-comparison').innerHTML='<p>Rate unavailable.</p>';$('first-long').textContent=target.status;$('session-rate').textContent='No certified game result has been substituted.';return;}
 const planName=target.calendar.kind==='startup-only'?'Startup-only plan':target.calendar.kind==='fixed-safe'?'Certified safe fallback':'Funded plan';
 let html=`<div class="rate-line"><span>${planName} · limiting</span><strong>≈ ${pct(r.constructedRateExact)}</strong></div>`;
 if(r.fixedRateExact)html+=`<div class="rate-line"><span>Own best fixed gap · ${r.bestFixedK}</span><strong>≈ ${pct(r.fixedRateExact)}</strong></div><div class="rate-saving">Funded timing uses ≈ ${pct(r.relativeSavingBoundsExact.lower)} fewer cap-rule applications than that fixed rhythm in the limit.</div>`;
 else html+=target.calendar.kind==='startup-only'?'<p class="fine">One startup cap, then guard forever. The limiting frequency is zero; there is no finite best fixed gap.</p>':'<p class="fine">A certified fixed-safe fallback is available. The true best timing remains unresolved or censored; no optimum is claimed.</p>';
 $('rate-comparison').innerHTML=html;
 const first=target.constructedCalendarTiming;
 $('first-long').textContent=first?.firstLongExecution?`For funded timing, the first longer gap starts at execution ${first.firstLongExecution} (block ${first.firstLongBlock}). ${first.withinExecutionPreview?'It lies within the saved adverse-path preview.':'It is beyond the saved preview. No future reward is credited, and no long gap need appear in a short play session.'}`:'This selection has no positively mixed longer gap. Zero limiting frequency and unavailable timing remain different states.';
 $('session-rate').textContent=s?`Active selection: ${s.timing.mode==='fixed'?'fixed rhythm':'funded timing'}. Actual cap applications: ${s.capExecutions} / ${s.executions}. ${s.executions?'Observed session fraction ≈ '+displayAmount(s.capFraction*100,2)+'%.':'Nothing executed yet.'}`:'No active execution ledger.';
}
function renderCharts(s){
 const ledger=game?.ledger()??[],shown=ledger.slice(-60),F=target.actualThresholdExact?val(target.actualThresholdExact):0;
 const plot=(lines,lo,hi,title,line=null)=>{
  const pad=Math.max((hi-lo)*.1,.02);lo-=pad;hi+=pad;const x=i=>60+(shown.length<2?0:635*i/(shown.length-1)),y=v=>192-154*(v-lo)/(hi-lo);
  let svg=`<title>${esc(title)}</title><line x1="60" x2="695" y1="192" y2="192" stroke="#cad5be"/><text x="5" y="41">${displayAmount(hi,2)}</text><text x="5" y="194">${displayAmount(lo,2)}</text>`;
  for(const [i,r] of shown.entries())if(r.type==='cap')svg+=`<line x1="${x(i)}" x2="${x(i)}" y1="30" y2="192" stroke="#c7b89b" stroke-dasharray="2 4"/>`;
  if(line!==null)svg+=`<line x1="60" x2="695" y1="${y(line)}" y2="${y(line)}" stroke="#607b4d" stroke-width="2" stroke-dasharray="7 5"/>`;
  for(const series of lines){const points=shown.map((r,i)=>`${x(i)},${y(series.f(r))}`);svg+=`<polyline points="${points.join(' ')}" fill="none" stroke="${series.color}" stroke-width="2.7"${series.dash?' stroke-dasharray="7 5"':''}/>`;for(const [i,r] of shown.entries())svg+=`<circle cx="${x(i)}" cy="${y(series.f(r))}" r="2.5" fill="${series.color}"/>`;}
  svg+=shown.length?`<text x="60" y="221">Execution ${shown[0].execution}</text><text x="695" y="221" text-anchor="end">${shown.at(-1).execution}</text>`:'<text x="90" y="120">Execute real prices to start this chart.</text>';return svg;
 };
 const benchmark=r=>F+val(r.guaranteedBuffer)/r.execution,benefits=shown.flatMap(r=>[r.averageConsumerSurplus,benchmark(r)]).concat(F);
 $('benefit-chart').innerHTML=plot([{f:r=>r.averageConsumerSurplus,color:'#b84f36'},{f:benchmark,color:'#237a91',dash:true}],Math.min(...benefits),Math.max(...benefits),'Actual running benefit versus adverse path and target',F);
 $('price-chart').innerHTML=plot([{f:r=>r.prices[0],color:'#b84f36'},{f:r=>r.prices[1],color:'#237a91',dash:true}],record.finite.prices[0],record.finite.prices.at(-1),'Executed prices; Shop B has a dashed blue line');
 $('history-label').textContent=`${ledger.length} actual execution${ledger.length===1?'':'s'} · manual coordinator`;
 $('ledger').innerHTML='<table><thead><tr><th>Execution</th><th>Rule</th><th>Gap / age</th><th>A price</th><th>B price</th><th>Customer benefit</th><th>A profit</th><th>B profit</th><th>Actual excess</th><th>Guaranteed buffer</th><th>Boundary credit</th></tr></thead><tbody>'+ledger.map(r=>`<tr><td>${r.execution}</td><td>${r.type}</td><td>${r.gapLength??'startup'} / ${r.age}</td><td>${r.prices[0].toPrecision(17)}</td><td>${r.prices[1].toPrecision(17)}</td><td>${r.consumerSurplus.toPrecision(17)}</td><td>${r.profits[0].toPrecision(17)}</td><td>${r.profits[1].toPrecision(17)}</td><td>≈ ${displayAmount(r.actualExcess,6)}</td><td>≈ ${displayAmount(r.guaranteedBuffer,6)}</td><td>≈ ${displayAmount(r.boundaryCreditAfter,6)}</td></tr>`).join('')+'</tbody></table>';
}
function renderEvidence(){
 const kind=$('evidence-kind').value,t=selectedTarget(kind),m=selectedModel(kind),r=t.rates,continuous=kind!=='finite';
 $('evidence-comparison').innerHTML=`<div class="evidence-card${continuous?' continuous':''}"><h3>${continuous?'Continuous evidence only · no finite quote indices':'Finite game · saved numerical rewards'}</h3><p>${esc(t.status)}</p><p>Absolute target ≈ ${t.actualThresholdExact?displayAmount(t.actualThresholdExact,8):'unavailable'}. ${continuous?'Validated bounds enclose the restricted optimum. The constructed lower-credit calendar need not attain the unknown real-valued optimum.':'Exactness refers to rational values of this saved numerical table, not an exact-real market.'}</p><p>Optimum cap frequency ${r?rateRange(t):'unavailable'} applications / execution. ${r?`Constructed rate ≈ ${displayAmount(r.constructedRateExact,8)}.`:''} Own best fixed integer gap: ${t.frontier.bestFixedK??'not established'}.</p><p>${continuous?'Every allowed continuous response is covered under the stated model/order premises. The live manual game above uses its own separate finite certificate.':'Both shops can choose every saved allowed quote. This is an all-response guarantee, not a claim about what independent learners discover.'}</p></div>`;
 $('exact-evidence').textContent=JSON.stringify({selected:{model:m.id,target:t},finiteGameSource:data.meta.finiteGameSources[record.scenario.id],meta:data.meta},null,2);
}
function save(){if(!game)return;const blob=new Blob([JSON.stringify({kind:'Local manual two-shop timing game',scenario:record.scenario.id,target:target.label,mode:$('schedule').value,snapshot:game.snapshot(),ledger:game.ledger(),evidence:{primaryManifestSha256:data.meta.primaryManifestSha256,independentAuditSha256:data.meta.independentAuditSha256},scope:'Developer-built manual illustration, not a human study or model-player experiment.'},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='cap-timing-'+record.scenario.id+'.json';a.click();URL.revokeObjectURL(url);notice='Saved this local record. No result was uploaded.';render();}
export async function mountTiming(){
 try{
  const response=await fetch('/local-pricing-guard/timing-data.json');need(response.ok,'Accepted timing data could not be loaded');data=validateTimingData(await response.json());
  $('market').innerHTML=data.scenarioOrder.map(s=>`<option value="${esc(s)}">${esc(names[s]??s)}</option>`).join('');$('target').innerHTML=data.targetOrder.map(t=>`<option value="${esc(t)}">${esc(targetNames[t])}</option>`).join('');
  $('market').value='base-g15-t1';$('target').value='cap-95pct';$('schedule').value='mixed';$('evidence-kind').value='finite';
  for(const id of ['market','target','schedule'])$(id).addEventListener('change',()=>{restart.mode=$('schedule').value;restart();});
  for(const [id,which] of [['choose-high','high'],['choose-low','low'],['choose-asymmetric','asymmetric']])$(id).addEventListener('click',()=>fill(which));
  for(const [f,id] of [[0,'quote-a'],[1,'quote-b']])$(id).addEventListener('change',()=>{quotes[f]=$(id).value===''?null:Number($(id).value);render();});
  $('quote-form').addEventListener('submit',execute);$('undo').addEventListener('click',()=>{game?.undo();quotes=[null,null];notice='The last execution and both reward ledgers were undone.';render();});$('restart').addEventListener('click',()=>{game?.reset();quotes=[null,null];notice='Restarted with one pending cap. No old or future reward was counted.';render();});$('save').addEventListener('click',save);$('evidence-kind').addEventListener('change',renderEvidence);
  $('all-results').innerHTML='<table><thead><tr><th>Market / model</th><th>Target</th><th>Status</th><th>Own best fixed K</th><th>Optimum rate bounds</th><th>Constructed first long execution</th></tr></thead><tbody>'+data.models.flatMap(m=>m.targets.map(t=>`<tr><td>${esc(m.scenario)} / ${esc(m.kind)}</td><td>${esc(t.label)}</td><td>${esc(t.status)}</td><td>${t.frontier.bestFixedK??'—'}</td><td>${esc(rateRange(t))}</td><td>${esc(t.constructedCalendarTiming?.firstLongExecution??'—')}</td></tr>`)).join('')+'</tbody></table>';
  $('timing-app').hidden=false;$('load-status').textContent='Accepted evidence loaded: 40 finite labels and 80 continuous labels. Live play uses only its own finite game.';restart();
 }catch(error){$('timing-app').hidden=true;$('quote-fields').disabled=true;$('load-status').textContent='Play is locked: '+error.message;}
}
if(typeof document!=='undefined')await mountTiming();
