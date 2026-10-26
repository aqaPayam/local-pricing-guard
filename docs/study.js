import data from '/local-pricing-guard/credit-data.js';
const $=id=>document.getElementById(id),fmt=(n,d=1)=>Number.isFinite(n)?n.toFixed(d):'—';
const metric=(r,k)=>r?.metrics?.[k]?.mean;
const summaries=data.summaries;
const original=summaries.find(r=>r.cohort==='deployment'&&r.arm==='guard-proposal'&&r.evaluation==='adaptive'&&r.protection==='protected');
const boundary=after=>{
 $('before').setAttribute('aria-pressed',String(!after));$('after').setAttribute('aria-pressed',String(after));
 const raw='#c35232',guard='#537988';
 $('boundary').innerHTML=`<rect x="12" y="45" width="245" height="95" rx="15" fill="#f7e6d9"/><text x="135" y="83" text-anchor="middle" font-size="22" fill="${raw}">Raw proposal</text><text x="135" y="115" text-anchor="middle" font-size="16">The seller's initial choice</text><path d="M270 91H350" stroke="#647470" stroke-width="3"/><rect x="365" y="45" width="220" height="95" rx="15" fill="#e1eced"/><text x="475" y="83" text-anchor="middle" font-size="22" fill="${guard}">Price guard</text><text x="475" y="115" text-anchor="middle" font-size="16">Keep an allowed price</text><path d="M598 91H678" stroke="#647470" stroke-width="3"/><rect x="690" y="45" width="255" height="95" rx="15" fill="#e7eddb"/><text x="817" y="83" text-anchor="middle" font-size="22">Shoppers see</text><text x="817" y="115" text-anchor="middle" font-size="16">Exactly the same prices</text><path d="M${after?630:310} 15V170" stroke="#222" stroke-width="3" stroke-dasharray="6 5"/><text x="${after?630:310}" y="193" text-anchor="middle" font-size="15">Count proposal here</text>`;
 $('boundary-metrics').innerHTML=[['Proposals unchanged',after?'100.0%':fmt(metric(original,'retention')*100)+'%'],['Customer benefit',fmt(metric(original,'consumerSurplus'))],['Prices allowed',fmt(metric(original,'feasibleFraction')*15)+' / 15']].map(([a,b])=>`<div class="metric"><span>${a}</span><strong>${b}</strong></div>`).join('');
 $('boundary-explanation').textContent=after?'Calling the already accepted price the proposal makes retention perfect. The shopper outcome and allowed price set have not improved.':'Counting the initial choice reveals how often the guard replaces a proposal. This measures intervention at this boundary, not intrinsic freedom.';
};
$('before').addEventListener('click',()=>boundary(false));$('after').addEventListener('click',()=>boundary(true));boundary(false);
const labels={'none':'No control','cap-proposal':'Simple price cap','cap-aware':'Cap-aware learner','guard-proposal':'Guard: proposal credit','guard-executed':'Guard: naive executed credit','guard-aware':'Guard-aware learner'};
function render(){const cohort=$('cohort').value;const rows=summaries.filter(r=>r.cohort===cohort&&r.evaluation==='adaptive'&&r.protection==='protected'&&(cohort!=='long-deployment'||r.window==='last20k'));
 $('result-cards').innerHTML=rows.map(r=>`<article class="study-card"><h3>${labels[r.arm]||r.arm}</h3><dl><dt>Customer benefit</dt><dd>${fmt(metric(r,'consumerSurplus'))}</dd><dt>Profit per seller</dt><dd>${fmt((metric(r,'profitA')+metric(r,'profitB'))/2)}</dd><dt>Proposals unchanged</dt><dd>${fmt(metric(r,'retention')*100)}%</dd><dt>Prices you can choose</dt><dd>${fmt(metric(r,'feasibleFraction')*15)} / 15</dd></dl><svg viewBox="0 0 100 4" role="img" aria-label="Feasible action fraction"><rect width="100" height="4" rx="2" fill="#e1e6dc"/><rect width="${metric(r,'feasibleFraction')*100}" height="4" rx="2" fill="#2d747c"/></svg><p class="fine">n = ${r.n} paired seeds</p></article>`).join('');
}
$('cohort').addEventListener('change',render);render();
