import {createHumanMarketSession} from '/scripted-market.js';
import {outcome,NASH} from '/replacement-market.js';
const $=id=>document.getElementById(id);
const fmt=(n,d=2)=>Number(n).toFixed(d);
const names={full:'Everything',facts:'Facts only',safe:'Structured facts · candidate',minimal:'Clean slate'};
let session,packet,policy='safe',played=[],last=null;
function setup(){const origin=$('human-scenario').value;return {scenario:origin==='fixed-high'?'cooperative':origin,incumbent:origin==='fixed-high'?'fixed-high':'reactive',anchorTolerance:.05,memoryRule:$('human-rule').value,policy};}
function newGame(){
  session=createHumanMarketSession(setup());packet=session.observe();played=[];last=null;
  const fixed=setup().incumbent==='fixed-high';$('human-rule').disabled=fixed;
  document.querySelector('.market-description').textContent=`The first 15 rounds happened before you arrived. You play the next 25. Your goal is to earn profit; customer benefit is shown separately. ${fixed?'This control rival always charges the high reference price, even after you cut yours. The convention-channel setting is ignored by this rival.':'The reactive rival follows its programmed convention and may respond in the next round.'}`;
  $('human-price').value='1.473';$('human-price-range').value='1.473';
  $('human-feedback').textContent='Your rival’s current price is sealed. Set yours, then both prices are revealed together.';
  $('market-scene').classList.remove('new-round');render();
}
function shop(x,color,label,price,isYou){
  const windows=[0,1,2,3,4,5].map(i=>`<path d="M${x+17+i*29} 109 h29 v25 q-14.5 15 -29 0z" fill="${i%2?'#fff8e9':color}"/>`).join('');
  return `<g><ellipse cx="${x+104}" cy="243" rx="119" ry="12" fill="#173e3910"/><rect x="${x}" y="66" width="208" height="173" rx="11" fill="#fffdf5" stroke="#cdd8cd"/><path d="M${x-9} 78 L${x+17} 43 H${x+191} L${x+217} 78z" fill="${color}"/><rect x="${x+17}" y="91" width="174" height="18" fill="${color}"/>${windows}<rect x="${x+22}" y="151" width="91" height="62" rx="5" fill="#dce9df"/><path d="M${x+68} 151 v62 M${x+22} 181 h91" stroke="#b6cbc0" stroke-width="3"/><rect x="${x+129}" y="148" width="57" height="91" rx="5" fill="${color}" opacity=".85"/><circle cx="${x+173}" cy="194" r="3" fill="#fff9e8"/><rect x="${x+29}" y="169" width="77" height="29" rx="4" fill="#fffdf5"/><text x="${x+67}" y="189" text-anchor="middle" class="shop-price">${price===null?'?':fmt(price,3)}</text><text x="${x+104}" y="65" text-anchor="middle" class="shop-name">${label}</text><rect x="${x+28}" y="250" width="152" height="25" rx="12" fill="${isYou?'#fae6da':'#e0edf0'}"/><text x="${x+104}" y="267" text-anchor="middle" class="shop-caption">${isYou?'A · YOU':'B · SCRIPTED RIVAL'}</text><rect x="${x-17}" y="209" width="24" height="30" rx="4" fill="#bd946a"/><circle cx="${x-5}" cy="202" r="16" fill="#6b9579"/></g>`;
}
function person(x,y,color,index){return `<g class="customer person-${index%3}" transform="translate(${x},${y})"><circle cy="-10" r="5" fill="${color}"/><path d="M-6 0q0-8 6-8t6 8v10H-6z" fill="${color}"/><path d="M-3 10v8 M3 10v8" stroke="${color}" stroke-width="3" stroke-linecap="round"/></g>`;}
function scene(){
  const previous=packet.history.at(-1);
  const visible=last||(previous?outcome([previous.myPrice,previous.competitorPrice]):null);
  const q=visible?visible.quantities:[0,0],outside=visible?100-q[0]-q[1]:100;
  $('market-scene').setAttribute('aria-label',visible?`${last?`Settled round ${last.round}`:'Last inherited round'}. Your price ${fmt(visible.prices[0],3)}, rival price ${fmt(visible.prices[1],3)}. Expected sales: yours ${fmt(q[0],1)}, rival ${fmt(q[1],1)}; no purchase ${fmt(outside,1)}.`:'No inherited market record. Current rival price is sealed. One hundred potential customers await the first decision.');
  const na=Math.round(q[0]/5),nab=Math.round((q[0]+q[1])/5);
  const people=Array.from({length:20},(_,i)=>person(230+(i%10)*48,306+Math.floor(i/10)*37,i<na?'#bc5b3e':i<nab?'#297a8d':'#89958e',i)).join('');
  $('market-scene').innerHTML=`<defs><pattern id="paving" width="30" height="22" patternUnits="userSpaceOnUse"><path d="M0 0h30v22H0z" fill="none" stroke="#e3e5d9" stroke-width=".6"/></pattern></defs><rect width="900" height="360" rx="16" fill="#eef2e6"/><path d="M0 253 Q250 221 450 247 T900 242 V360H0z" fill="#e5e6d8"/><path d="M0 253 Q250 221 450 247 T900 242 V360H0z" fill="url(#paving)"/><path class="customer-route" d="M450 285 Q300 255 207 238 M450 285 Q590 250 691 238" fill="none" stroke="#bbcbb8" stroke-width="2" stroke-dasharray="5 7"/><circle cx="450" cy="110" r="42" fill="#fffdf3"/><text x="450" y="102" text-anchor="middle" class="market-center">100</text><text x="450" y="123" text-anchor="middle" class="small-scene">potential customers</text><text x="450" y="169" text-anchor="middle" class="small-scene">${last?`Round ${last.round} · settled`:previous?'Inherited last round':'No old market record'}</text><text x="450" y="189" text-anchor="middle" class="small-scene">${last?'Both prices now revealed':'Current rival price is sealed'}</text>${shop(90,'#bc5b3e','YOUR CORNER SHOP',visible?visible.prices[0]:null,true)}${shop(602,'#297a8d','THE OTHER SHOP',visible?visible.prices[1]:null,false)}${people}<rect x="14" y="285" width="166" height="58" rx="9" fill="#fffdf2"/><text x="28" y="306" class="small-scene">${visible?`Your sales: ${fmt(q[0],1)}`:'Choose your first price'}</text><text x="28" y="326" class="small-scene">${visible?`Rival sales: ${fmt(q[1],1)}`:'No choices revealed yet'}</text><rect x="734" y="285" width="152" height="58" rx="9" fill="#fffdf2"/><text x="748" y="306" class="small-scene">${visible?'Chose not to buy':'Waiting for a price'}</text><text x="748" y="328" class="no-buy">${visible?fmt(outside,1):'100'}</text>`;
}
function priceChart(){
  const rows=session.observe().history.filter(r=>r.round>0),w=900,l=42,r=873,t=16,b=163;
  const x=n=>l+(n-1)/39*(r-l),y=p=>b-p/3*(b-t);
  let s='';for(const p of [0,1,2,3])s+=`<line x1="${l}" y1="${y(p)}" x2="${r}" y2="${y(p)}" stroke="#e0e5d9"/><text x="28" y="${y(p)+4}" text-anchor="end">${p}</text>`;
  s+=`<line x1="${l}" y1="${y(NASH.prices[0])}" x2="${r}" y2="${y(NASH.prices[0])}" stroke="#8c9a8e" stroke-dasharray="5 5"/><line x1="${x(16)}" y1="${t}" x2="${x(16)}" y2="${b}" stroke="#9da994" stroke-dasharray="3 5"/><text x="${x(16)+6}" y="24">Your first round</text>`;
  for(const [key,color] of [['competitorPrice','#297a8d'],['myPrice','#bc5b3e']]){s+=`<polyline points="${rows.map(row=>`${x(row.round)},${y(row[key])}`).join(' ')}" fill="none" stroke="${color}" stroke-width="${key==='myPrice'?3:5}" ${key==='competitorPrice'?'stroke-dasharray="5 5"':''}/>`;for(const row of rows.slice(-1))s+=`<circle cx="${x(row.round)}" cy="${y(row[key])}" r="4" fill="${color}"/>`;}
  for(const n of [1,10,16,25,40])s+=`<text x="${x(n)}" y="188" text-anchor="middle">${n}</text>`;
  if(!rows.length)s+='<text x="450" y="78" text-anchor="middle">No old history inherited. Your new rounds will appear here.</text>';
  $('human-chart').innerHTML=s;
}
function renderPacket(){
  document.querySelectorAll('[data-packet]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.packet===policy)));
  $('packet-title').textContent=names[policy];
  $('public-equation').textContent='quantity_i = 100 × exp((2 − price_i) / 0.25) / [1 + exp((2 − price_A) / 0.25) + exp((2 − price_B) / 0.25)]\n\nprofit_i = (price_i − 1) × quantity_i\n\nQuality = 2; outside quality = 0; demand scale = 0.25; customers = 100.';
  $('packet-flow').innerHTML=`<span title="Old manager">♙</span><i>→</i><span title="Handover packet">${policy==='minimal'?'○':'▤'}</span><i>→</i><span title="You">♙</span>`;
  $('packet-note').textContent=packet.previousOperationalNote?`Note received: “${packet.previousOperationalNote}”`:'No predecessor strategy note was passed to you.';
  const latest=session.observe().history.filter(r=>r.round>0).slice(-3);
  $('packet-history').innerHTML=`<span class="packet-count">${packet.history.filter(r=>r.round>0).length} previous rounds inherited · cost & demand rules always kept</span><p class="fine">${policy==='full'?'The old strategy is inherited text, not a requirement to follow it.':policy==='safe'?'Candidate design: factual note replaces the strategy; the same numeric history remains.':'New observations are kept normally after takeover.'}</p><h3>Latest facts you can see</h3>${latest.length?`<div class="mini-history">${latest.map(r=>`<div><span>R${r.round}</span><b class="firm-a">A ${fmt(r.myPrice,3)}</b><b class="firm-b">B ${fmt(r.competitorPrice,3)}</b></div>`).join('')}</div>`:'<p class="fine">No completed rounds available yet.</p>'}`;
}
function render(){
  const obs=session.observe(),sum=played.reduce((s,row)=>s+row.profits[0],0);
  $('human-round').textContent=obs.finished?'Complete · 25 / 25 turns':`Round ${obs.round} / 40 · your turn ${played.length+1} of 25`;
  $('human-metrics').innerHTML=[['Your total profit',fmt(sum),'Only your 25 playable rounds'],['Your latest profit',last?fmt(last.profits[0]):'—','(Price − cost) × your sales'],['Customer benefit',last?fmt(last.consumerSurplus):'—','Value gained, in model units'],['Your latest sales',last?fmt(last.quantities[0],1):'—','Expected customer demand']].map(([name,value,caption])=>`<div><span>${name}</span><b>${value}</b><small>${caption}</small></div>`).join('');
  scene();renderPacket();priceChart();
  $('submit-price').disabled=obs.finished;$('human-price').disabled=obs.finished;$('human-price-range').disabled=obs.finished;document.querySelectorAll('[data-price]').forEach(b=>b.disabled=obs.finished);
  $('human-ledger').innerHTML=played.length?`<table><thead><tr><th>Round</th><th>Your price</th><th>Rival price</th><th>Your sales</th><th>Your profit</th></tr></thead><tbody>${played.slice(-5).reverse().map(row=>`<tr><td>${row.round}</td><td>${fmt(row.prices[0],3)}</td><td>${fmt(row.prices[1],3)}</td><td>${fmt(row.quantities[0],1)}</td><td>${fmt(row.profits[0])}</td></tr>`).join('')}</tbody></table>`:'<p>Your first completed round will appear here.</p>';
  $('human-ending').hidden=!obs.finished;
  if(obs.finished){const avg=played.reduce((s,row)=>s+row.consumerSurplus,0)/played.length;$('human-ending').innerHTML=`<p class="eyebrow">MARKET CLOSED</p><h2>You completed the handover.</h2><p>Your total profit: <b>${fmt(sum)}</b>. Average customer benefit: <b>${fmt(avg)}</b> (competitive reference ${fmt(NASH.consumerSurplus)}).</p><p>Try the same prices with another packet, or switch to the scripted comparison. This one human run is not a controlled AI experiment.</p>`;}
}
$('quote-form').addEventListener('submit',e=>{e.preventDefault();if(!$('quote-form').reportValidity())return;try{last=session.step(Number($('human-price').value));played.push(last);render();$('market-scene').classList.remove('new-round');requestAnimationFrame(()=>$('market-scene').classList.add('new-round'));$('human-feedback').textContent=`Round ${last.round}: you charged ${fmt(last.prices[0],3)}, the rival charged ${fmt(last.prices[1],3)}. You sold ${fmt(last.quantities[0],1)} and ${last.profits[0]<0?'lost':'earned'} ${fmt(Math.abs(last.profits[0]))}. ${session.observe().finished?'All 25 turns are complete.':'Your rival can respond to these prices next round.'}`;}catch(err){$('human-feedback').textContent=err.message;}});
$('human-price-range').addEventListener('input',()=>$('human-price').value=$('human-price-range').value);
$('human-price').addEventListener('input',()=>{if($('human-price').validity.valid)$('human-price-range').value=$('human-price').value;});
document.querySelectorAll('[data-price]').forEach(b=>b.addEventListener('click',()=>{$('human-price').value=b.dataset.price;$('human-price-range').value=b.dataset.price;}));
document.querySelectorAll('[data-packet]').forEach(b=>b.addEventListener('click',()=>{policy=b.dataset.packet;newGame();}));
for(const id of ['human-scenario','human-rule'])$(id).addEventListener('change',newGame);
$('human-reset').addEventListener('click',newGame);
$('human-export').addEventListener('click',()=>{const data={type:'human-versus-scripted-demonstration',modelCalls:0,config:setup(),initialPacket:packet,currentObservation:session.observe(),playedRounds:played.map(({notes,...row})=>row),warning:'Human demonstration; not evidence about AI collusion.'},url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='my-handover-game.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
for(const mode of ['human','lab'])$(`mode-${mode}`).addEventListener('click',()=>{const human=mode==='human';$('human-game').hidden=!human;$('lab-mode').hidden=human;$('mode-human').setAttribute('aria-pressed',String(human));$('mode-lab').setAttribute('aria-pressed',String(!human));});
$('human-scenario').add(new Option('High prices · rival never reacts','fixed-high'));
newGame();
