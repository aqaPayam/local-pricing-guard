import {runScriptedMarket,runDeviationProbe,bestResponse,discountDeviationAnalysis,HANDOVER_POLICIES} from '/local-pricing-guard/scripted-market.js';
const $=id=>document.getElementById(id);
const labels={continue:'Unchanged control',full:'Full handover',facts:'Facts only',safe:'Structured facts (candidate)',minimal:'Fresh start'};
const fmt=(n,d=2)=>Number(n).toFixed(d);
let paths={},policy='full',cursor=1,timer=null,probe=null;
function options(){const origin=$('scenario').value;return {horizon:40,replacementRound:Number($('replacement').value),scenario:origin==='fixed-high'?'cooperative':origin,incumbent:origin==='fixed-high'?'fixed-high':'reactive',anchorTolerance:Number($('tolerance').value),controller:$('controller').value,memoryRule:$('memory-rule').value};}
function stop(){if(timer)clearInterval(timer);timer=null;$('play').textContent='Play';}
function clearProbe(){probe=null;$('probe-output').hidden=true;}
function rebuild(){stop();clearProbe();paths=Object.fromEntries(HANDOVER_POLICIES.map(p=>[p,runScriptedMarket({...options(),policy:p})]));cursor=1;$('replacement-label').textContent=$('replacement').value;render();}
function chart(path){
  const width=960,height=290,left=48,right=915,top=24,bottom=248;
  const all=Object.values(paths).flatMap(p=>p.rows.flatMap(r=>r.prices));
  const lo=Math.min(...all,1.4)-0.06,hi=Math.max(...all,2)+0.06;
  const x=r=>left+(r-1)/39*(right-left),y=p=>bottom-(p-lo)/(hi-lo)*(bottom-top);
  let body='';
  for(let i=0;i<5;i++){const v=lo+(hi-lo)*i/4;body+=`<line x1="${left}" y1="${y(v)}" x2="${right}" y2="${y(v)}" stroke="#e4e8df"/><text x="36" y="${y(v)+4}" text-anchor="end">${fmt(v)}</text>`;}
  for(const r of [1,10,20,30,40])body+=`<text x="${x(r)}" y="273" text-anchor="middle">${r}</text>`;
  body+=`<text x="${right}" y="288" text-anchor="end">Round</text><line x1="${left}" y1="${y(path.benchmarks.nashPrice)}" x2="${right}" y2="${y(path.benchmarks.nashPrice)}" stroke="#7a8b7d" stroke-dasharray="5 5"/>`;
  const rx=x(path.config.replacementRound);
  body+=`<line x1="${rx}" y1="${top}" x2="${rx}" y2="${bottom}" stroke="#9caa9f" stroke-dasharray="3 4"/><text x="${rx+6}" y="16">${policy==='continue'?'Comparison checkpoint':'Seller A replaced'}</text>`;
  for(const [firm,color] of [[1,'#237a91'],[0,'#b84f36']]){
    const rows=path.rows.slice(0,cursor),points=rows.map(r=>`${x(r.round)},${y(r.prices[firm])}`).join(' '),last=rows.at(-1);
    body+=`<polyline points="${points}" fill="none" stroke="${color}" stroke-width="${firm===0?3:5}" ${firm===1?'stroke-dasharray="5 5"':''}/><circle cx="${x(last.round)}" cy="${y(last.prices[firm])}" r="4" fill="${color}"/>`;
  }
  $('chart').innerHTML=body;
}
function render(){
  const path=paths[policy],row=path.rows[cursor-1],t=path.config.replacementRound;
  $('round').value=cursor;$('round-label').textContent=`${cursor} / 40`;
  document.querySelectorAll('[data-policy]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.policy===policy)));
  $('event').textContent=cursor<t?`Round ${cursor}: the initial ${path.config.scenario==='cooperative'?'elevated':'competitive'} convention is scripted. Handover checkpoint: round ${t}.`:policy==='continue'?`Round ${cursor}: both original controllers continue with all their information.`:`Round ${cursor}: A has ${policy==='full'?'inherited price history and the strategy note':policy==='facts'?'inherited price history; its old strategy note was deleted':policy==='safe'?'inherited the same price history and a neutral factual note':'started without old history or its strategy note'}. B retains its information.`;
  const metrics=[['Seller A price',fmt(row.prices[0],3),`Profit ${fmt(row.profits[0])}`],['Seller B price',fmt(row.prices[1],3),`Profit ${fmt(row.profits[1])}`],['Customer benefit',fmt(row.consumerSurplus),'Consumer surplus / round'],['Units sold',fmt(row.quantities.reduce((s,q)=>s+q,0),1),'Expected demand / round']];
  $('metrics').innerHTML=metrics.map(([label,value,caption])=>`<div class="metric"><span>${label}</span><strong>${value}</strong><small>${caption}</small></div>`).join('');
  chart(path);
  const obs=path.replacementObservation;
  $('observation-caption').textContent=`Packet at round ${t} (shown here even when the timeline is earlier). ${obs.history.length} past rows; displaying the last 3. New observations accumulate after the handover.`;
  $('observation').textContent=JSON.stringify({...obs,history:obs.history.slice(-3)},null,2);
  $('reason-a').textContent=`Seller A: ${row.reasons[0]}`;$('reason-b').textContent=`Seller B: ${row.reasons[1]}`;
  $('comparison').innerHTML=HANDOVER_POLICIES.map(p=>{const s=paths[p].summary;return `<tr class="${p===policy?'selected':''}"><td>${labels[p]}</td><td>${fmt((s.postReplacementMeanPrices[0]+s.postReplacementMeanPrices[1])/2,3)}</td><td>${fmt(s.postReplacementMeanProfits[0])}</td><td>${fmt(s.postReplacementMeanProfits[1])}</td><td>${fmt(s.postReplacementMeanConsumerSurplus)}</td></tr>`;}).join('');
  $('interpretation').textContent=policy==='continue'?'Unchanged control: both original convention rules continue. The selected incoming rule is not used in this path. Compare full versus facts only to hold the successor rule fixed while changing its inherited information.':path.config.scenario==='competitive'?'Negative control: the same interventions begin with competitive prices. Compare this with the elevated origin before attributing any effect specifically to harmful coordination.':path.config.controller!=='convention'?'This receiver does not copy the predecessor’s convention. Any recovery follows the independent rule we chose, rather than a demonstrated learning outcome.':path.config.memoryRule==='history'?'In this constructed example, numeric prices carry the convention. Removing the note leaves the rule’s input intact. This is an assumption encoded in the policy, not a discovery about AI.':'In this constructed example, the private note carries the convention. Removing that note changes the policy’s input. Compare the history-driven version to see why the handover effect depends on the controller.';
}
$('play').addEventListener('click',()=>{if(timer){stop();return;}if(cursor===40)cursor=1;$('play').textContent='Pause';render();timer=setInterval(()=>{cursor++;render();if(cursor===40)stop();},450);});
$('step').addEventListener('click',()=>{stop();cursor=Math.min(40,cursor+1);render();});
$('reset').addEventListener('click',()=>{stop();cursor=1;render();});
$('round').addEventListener('input',()=>{stop();cursor=Number($('round').value);render();});
for(const id of ['scenario','controller','memory-rule','replacement','tolerance'])$(id).addEventListener('input',rebuild);
document.querySelectorAll('[data-policy]').forEach(b=>b.addEventListener('click',()=>{stop();clearProbe();policy=b.dataset.policy;render();}));
$('export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({type:'scripted-mechanism-demonstration',modelCalls:0,paths},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='inheritance-lab-scripted.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
function showProbe(){
 if(!probe)return;const {baseline,deviated}=probe,round=baseline.config.replacementRound,discount=Number($('probe-discount').value),a=discountDeviationAnalysis(baseline,deviated,{round,discount});
 const before=baseline.rows[round-1].prices[0],after=deviated.rows[round-1].prices[0],kind=Math.abs(after-before)<1e-12?'unchanged':after<before?'cut':'increased';
 $('probe-output').hidden=false;$('probe-message').textContent=`A’s quote is ${kind}: ${fmt(before,3)} → ${fmt(after,3)} at round ${round}. ${a.incumbentPricePath.some(p=>Math.abs(p.difference)>1e-10)?'B changes its later prices relative to the original path.':'B’s later prices do not change relative to the original path.'}`;
 $('probe-metrics').innerHTML=[['Immediate A profit change',fmt(a.immediateProfitGain)],['Discounted A profit change',fmt(a.discountedProfitDifference)],['Discount factor',fmt(discount)],['Horizon',`${baseline.config.horizon-round+1} rounds`]].map(([k,v])=>`<div class="metric"><span>${k}</span><strong>${v}</strong></div>`).join('');
 let svg='';for(const [firm,color] of [[0,'#b84f36'],[1,'#237a91']]){const left=45+firm*480,right=440+firm*480,x=r=>left+(r-1)/39*(right-left),y=p=>213-p/3*165;svg+=`<text x="${left}" y="21">Seller ${firm===0?'A · quote changed once':'B · incumbent response'}</text>`;for(const p of [0,1,2,3])svg+=`<line x1="${left}" x2="${right}" y1="${y(p)}" y2="${y(p)}" stroke="#e0e5db"/><text x="${left-9}" y="${y(p)+4}" text-anchor="end">${p}</text>`;svg+=`<line x1="${x(round)}" x2="${x(round)}" y1="40" y2="213" stroke="#8b9b87" stroke-dasharray="3 4"/>`;for(const [path,dashed] of [[baseline,false],[deviated,true]])svg+=`<polyline fill="none" stroke="${color}" stroke-width="${dashed?3:5}" ${dashed?'stroke-dasharray="5 5" opacity="1"':'opacity=".3"'} points="${path.rows.map(r=>`${x(r.round)},${y(r.prices[firm])}`).join(' ')}"/>`;svg+=`<text x="${left}" y="237">Round 1</text><text x="${right}" y="237" text-anchor="end">Round 40</text>`;}$('probe-chart').innerHTML=svg;
}
$('run-probe').addEventListener('click',()=>{const config={...options(),policy},base=paths[policy],round=config.replacementRound;probe=runDeviationProbe(config,{round,price:bestResponse(base.rows[round-2].prices[1]),discount:Number($('probe-discount').value)});showProbe();});
$('probe-discount').addEventListener('change',showProbe);
rebuild();
