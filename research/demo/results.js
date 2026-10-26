import study from '/study-data.js';
const $=id=>document.getElementById(id),f=(n,d=2)=>Number(n).toFixed(d);
const labels={continue:'Unchanged',full:'Full',facts:'Facts only',safe:'Structured facts',minimal:'Clean slate'};
const policies=['continue','full','facts','safe','minimal'];
const s=study.overall;
$('result-stats').innerHTML=[['216 / 216','Identical safe / facts price paths','Predicted null across paired constructed comparisons.'],[`${s.safetyPass} / ${s.eligibleSafetyComparisons}`,'Pass the provisional harm target','Against full handover; 80 eligible comparisons fail.'],[`${s.competitiveUtilityPass} / ${s.competitiveComparisons}`,'Meet competitive utility tolerance','Constructed competitive controls; not a population estimate.'],['0','AI game-player calls','1,080 design cells; 936 effective configurations; 28 distinct original price paths.']].map(([n,label,caption])=>`<article><b>${n}</b><span>${label}</span><small>${caption}</small></article>`).join('');
function barChart(id,rows,key,reference,color){const max=Math.max(reference,...rows.map(r=>r[key]))*1.14,left=140,right=515,width=right-left;let svg='';for(let i=0;i<rows.length;i++){const row=rows[i],y=18+i*43,x=left+row[key]/max*width;svg+=`<text x="130" y="${y+17}" text-anchor="end">${labels[row.policy]}</text><rect x="${left}" y="${y}" width="${width}" height="24" rx="4" fill="#edf0e7"/><rect x="${left}" y="${y}" width="${Math.max(0,x-left)}" height="24" rx="4" fill="${row.policy==='safe'?'#63875c':color}"/><text x="${x+7}" y="${y+17}">${f(row[key])}</text>`;}const rx=left+reference/max*width;svg+=`<line x1="${rx}" x2="${rx}" y1="10" y2="221" stroke="#243e34" stroke-dasharray="3 4"/><text x="${rx}" y="244" text-anchor="middle">Reference ${f(reference)}</text>`;$(id).innerHTML=svg;}
function render(){
 const config={origin:$('result-origin').value,memoryRule:$('result-memory').value,controller:$('result-controller').value,horizon:Number($('result-horizon').value),replacementRound:Number($('result-takeover').value),anchorTolerance:Number($('result-tolerance').value)};
 const rows=policies.map(policy=>study.cases.find(row=>row.policy===policy&&Object.entries(config).every(([k,v])=>row[k]===v)));
 if(rows.some(r=>!r))throw Error('Missing study cell.');
 const pair=study.pairs.find(p=>Object.entries(config).every(([k,v])=>p.config[k]===v));
 const gate=pair.eligibleHarm?`${pair.safetyPass?'Pass':'Fail'}: structured facts reduces benchmark-relative harm by ${f(pair.harmRecovery*100,1)}% against full handover (target ≥ 50%).`:'The full-handover harm is below the denominator threshold, so a percentage recovery is not scored.';
 $('result-verdict').textContent=`${gate} Structured facts and facts only match exactly in this setting. ${config.origin==='competitive-reactive'?`Competitive utility gate: ${pair.competitiveUtilityPass?'pass':'fail'}.`:''} This is a comparison of programmed rules.`;
 barChart('result-cs',rows,'consumerSurplus',study.benchmarks.nash.consumerSurplus,'#809eaa');barChart('result-profit',rows,'profitA',study.benchmarks.nash.profits[0],'#c68a70');
 $('result-table').innerHTML=rows.map(r=>`<tr class="${r.policy==='safe'?'selected':''}"><td>${labels[r.policy]}</td><td>${f(r.priceA,3)}</td><td>${f(r.priceB,3)}</td><td>${f(r.profitA)}</td><td>${f(r.profitB)}</td><td>${f(r.consumerSurplus)}</td></tr>`).join('');
 $('result-probes').innerHTML=rows.map(r=>`<tr><td>${labels[r.policy]}</td><td>${r.probeKind}</td><td>${f(r.immediateGain)}</td><td>${f(r.discountedGain95)}</td><td>${r.incumbentResponds95?'Yes':'No'}</td></tr>`).join('');
}
for(const id of ['result-origin','result-memory','result-controller','result-horizon','result-takeover','result-tolerance'])$(id).addEventListener('change',render);
$('result-provenance').textContent=`Frozen before execution: ${study.provenance.frozenAt}. Protocol SHA-256: ${study.provenance.protocolHash}. Manifest SHA-256: ${study.provenance.manifestHash}. ${study.provenance.warning}`;
render();
