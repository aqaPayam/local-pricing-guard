import data from '/robust-data.js';
const $=id=>document.getElementById(id),fmt=(x,d=2)=>Number.isFinite(x)?x.toFixed(d):'—';
const names=['Base: 15 prices','Higher demand scale','Lower product value','Lower cost',
 'Base: 11 prices','Base: 31 prices','Half guard tolerance','Double guard tolerance'];
$('robust-scenario').innerHTML=data.scenarios.map((s,i)=>`<option value="${s.id}">${names[i]}</option>`).join('');
function render(){
 const scenario=data.scenarios.find(s=>s.id===$('robust-scenario').value),
  [learning,exploring]=$('robust-mode').value.split('-').map(Number),protection=$('robust-protection').value;
 const rows=data.summaries.filter(r=>r.scenario===scenario.id&&r.learn===Boolean(learning)&&
  r.explorationRate===(exploring?.01:0)&&r.protection===protection);
 const labels={'none':'No control','cap-proposal':'Simple price cap','guard-proposal':'Guard: original learner','guard-aware':'Guard-aware learner'};
 $('robust-context').textContent=`${scenario.gridSize} price choices before constraints. Guard tolerance ${fmt(scenario.epsilon,3)} in this market. Each displayed comparison uses all eight matched seeds. Protection ${protection==='protected'?'stays active':'is removed, including the choice restriction'}.`;
 $('robust-cards').innerHTML=rows.map(r=>{const m=r.metrics,cs=m.consumerSurplus;
  return `<article class="study-card"><h3>${protection==='released'?'Trained with: ':''}${labels[r.arm]}</h3><dl><dt>Proposals accepted</dt><dd>${fmt(100*m.retention.mean,1)}%</dd><dt>Prices allowed</dt><dd>${fmt(m.feasibleCount.mean,1)} / ${scenario.gridSize}</dd><dt>Allowed range width</dt><dd>${fmt(m.feasibleSpan.mean,3)}</dd><dt>Customer benefit (model)</dt><dd>${fmt(cs.mean)}</dd><dt>Profit: shop A / shop B</dt><dd>${fmt(m.profitA.mean)} / ${fmt(m.profitB.mean)}</dd></dl><p class="fine">95% seed interval, rounded: ${fmt(cs.low)} to ${fmt(cs.high)}. Seed variation only.</p></article>`;
 }).join('');
}
for(const id of ['robust-scenario','robust-mode','robust-protection'])$(id).addEventListener('change',render);
render();
