// Read-only presentation of audited saved evidence. No learning or optimizer.
const need=(ok,message)=>{if(!ok)throw Error(message);};
const exactNumber=value=>{
  need(value&&typeof value==='object'&&/^-?\d+$/.test(value.numerator)&&/^\d+$/.test(value.denominator)&&BigInt(value.denominator)>0n,'Missing exact saved-weight value');
  need(typeof value.approximate==='number'&&Number.isFinite(value.approximate),'Missing approximate display value');
  const n=BigInt(value.numerator),a=value.approximate;
  need(n===0n?a===0:n>0n?a>0:a<0,'Exact/display sign differs');
  const q=Number(value.numerator)/Number(value.denominator);
  if(Number.isFinite(q))need(Math.abs(q-a)<=Math.max(Number.MIN_VALUE,8*Number.EPSILON*Math.abs(q)),'Exact/display magnitude differs');
  return value.approximate;
};
const finite=value=>{need(typeof value==='number'&&Number.isFinite(value),'Missing numerical value');return value;};
const integer=(value,min=0)=>Number.isSafeInteger(value)&&value>=min;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const pair=value=>Array.isArray(value)&&value.length===2;
const scheduleName=run=>run.controller.id==='startup-only'?'One startup cap, then guard forever':run.controller.id==='permanent-cap'?'A cap every round':run.controller.id==='selected95'?`Inherited 95%-target rhythm · every ${run.controller.period} rounds`:'A cap every 16 rounds';
const maskName=id=>id==='base-g15-t1'?'Original tolerance · ε = 0.1':'Half tolerance · ε = 0.05';
const initName=id=>id==='zero'?'Zero scores':'Optimistic scores';
const number=(x,d=3)=>finite(x).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const value=(x,d=3)=>number(exactNumber(x),d);
const signed=x=>{finite(x);return x===0?'0':(x>0?'+':'')+(Math.abs(x)<.0005?x.toExponential(3):number(x));};
const pct=x=>number(100*exactNumber(x),1)+'%';
const escape=text=>String(text).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const table=(head,rows)=>`<table><thead><tr>${head.map(x=>`<th scope="col">${escape(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${escape(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
function validateMeans(m){exactNumber(m?.consumerSurplus);for(const key of ['profits','prices']){need(pair(m[key]),'Missing both firm means');m[key].forEach(exactNumber);}}
function validateGeometry(g){
  for(const key of ['maskCount','maskFraction','maskSpan','maxAllowedUsage'])for(const f of ['A','B']){
    const x=exactNumber(g?.[key]?.[f]);need(x>=0,'Negative price-choice geometry');
    if(key==='maskCount')need(x>0&&x<=62,'Invalid mean choice count');
    if(key==='maskFraction'||key==='maxAllowedUsage')need(x<=1,'Invalid price-choice fraction');
  }
  const cap=exactNumber(g?.capRuleFrequency);need(cap>=0&&cap<=1,'Invalid cap-rule frequency');
}
function validateEndpoint(endpoint){
  need(endpoint&&integer(endpoint.transientLength)&&integer(endpoint.cycleLength,1),'Missing frozen graph endpoint');
  validateMeans(endpoint.means);validateGeometry(endpoint.geometry);exactNumber(endpoint.floorGap);exactNumber(endpoint.target95Gap);
  for(const f of ['A','B'])for(const key of ['unvisitedStates','neverTriedGreedyActions','minimumStateVisits','minimumActionVisits'])need(integer(endpoint.visitSupport?.[f]?.[key]),'Missing visit support');
  need(endpoint.floorApplies===true&&BigInt(endpoint.floorGap.numerator)>=0n,'Applicable terminal floor missing or violated');
}
export function validateAdaptiveData(data){
  need(data?.schemaVersion===1,'Unsupported learner evidence');
  const audit=data.meta?.primaryAudit,c=data.meta?.counts;
  need(audit?.passed===true&&audit.runs===192&&audit.checkpoints===384&&audit.fullTrainingReplay===false,'Complete independent checkpoint audit required');
  need(c?.runs===192&&c.checkpoints===384&&c.primaryPairs===48&&c.primaryContrasts===4&&c.unresolvedRuns===0,'Incomplete planned inventory');
  for(const k of ['primaryManifestSha256','primaryResultsSha256','primaryIndexSha256','independentAuditSha256','summarySha256'])need(/^[a-f0-9]{64}$/.test(data.meta[k]),'Missing evidence identity');
  need(same(data.orderedSeeds,Array.from({length:12},(_,i)=>907001+i)),'Changed paired seeds');
  const defaultFields={scenario:'base-g15-t1',qInit:'zero',seed:907001,controller:'selected95',step:2000000,chosenBeforeOutcomeInspection:true};
  need(Object.entries(defaultFields).every(([key,value])=>data.meta.defaultSelection?.[key]===value),'Changed uninspected-outcome display default');
  need(data.scenarios?.length===2&&data.runs?.length===192&&data.primaryPairs?.length===48&&data.primaryContrasts?.length===4,'Missing complete display inventory');
  const scenarios=new Map(data.scenarios.map(s=>[s.scenario.id,s]));
  need(scenarios.size===2&&scenarios.has('base-g15-t1')&&scenarios.has('base-g15-t0.5'),'Unexpected mask conditions');
  for(const s of scenarios.values()){
    const g=s.finite,n=g.prices.length;need(n===62&&integer(g.capIndex)&&g.capIndex<n,'Missing saved game');
    need(g.prices.every((x,i)=>Number.isFinite(x)&&(!i||x>g.prices[i-1]))&&g.sets.length===n&&g.sets.every(a=>a.length&&a.every((x,i)=>integer(x)&&x<n&&(!i||x>a[i-1]))),'Malformed quote support');
    for(const k of ['consumerSurplus','profitA','profitB','quantityA','quantityB'])need(g.rewards[k]?.length===n*n&&g.rewards[k].every(Number.isFinite),'Missing payoff table');
  }
  const identities=new Set();
  for(const run of data.runs){
    const g=scenarios.get(run.scenario)?.finite,n=g?.prices.length;
    need(n&&run.status==='completed frozen-policy evaluation'&&['startup-only','permanent-cap','selected95','K16'].includes(run.controller?.id)&&['zero','optimistic'].includes(run.qInit)&&data.orderedSeeds.includes(run.seed),'Unexpected run condition/status');
    const key=[run.scenario,run.qInit,run.controller.id,run.seed].join('/');need(!identities.has(key),'Duplicate run condition');identities.add(key);
    const expected=run.controller.id==='startup-only'?null:run.controller.id==='permanent-cap'?1:run.controller.id==='K16'?16:run.scenario==='base-g15-t1'?4:10;
    need(run.controller.period===expected,'Changed cap schedule');
    need(same(run.checkpoints?.map(x=>x.step),[1000000,2000000])&&run.learningCurve?.length===200,'Incomplete saved trajectory');
    run.learningCurve.forEach((p,i)=>{need(p.endStep===(i+1)*10000,'Changed curve horizon');finite(p.means?.consumerSurplus);});
    for(const cp of run.checkpoints){
      validateMeans(cp.trainingTail?.means);validateGeometry(cp.trainingTail?.geometry);validateEndpoint(cp.frozen?.actualTerminal);validateEndpoint(cp.frozen?.freshCap);exactNumber(cp.controllerFloor?.longRunFloor);
      need(cp.trainingTail.rounds===100000&&cp.trainingTail.endStep===cp.step&&cp.preview128?.length===128,'Incomplete checkpoint/tail/preview');
      finite(cp.trainingTail.explorationMean);
      const coverage=cp.coverage;need(integer(coverage?.statesPerFirm,1)&&integer(coverage.legalCellsPerFirm,1),'Missing score coverage');
      for(const f of ['A','B'])need(integer(coverage[f]?.visitedStates)&&coverage[f].visitedStates<=coverage.statesPerFirm&&integer(coverage[f]?.visitedActions)&&coverage[f].visitedActions<=coverage.legalCellsPerFirm,'Malformed visit coverage');
      const graph=cp.frozen.allStates;for(const key of ['states','cycleCount','cyclesWithUnvisitedStates','cyclesWithNeverTriedGreedyActions'])need(integer(graph?.[key]),'Missing graph diagnostics');
      need(integer(cp.terminalStart?.phase)&&cp.terminalStart.phase===(run.controller.id==='startup-only'?1:cp.step%run.controller.period),'Checkpoint terminal clock differs');
      let previous=cp.terminalStart.previousIndices,phase=cp.terminalStart.phase;
      for(const p of cp.preview128){
        need(pair(previous)&&previous.every(x=>integer(x)&&x<n)&&same(p.previousIndices,previous)&&p.phase===phase,'Preview start/continuity differs');
        need(pair(p.executedIndices)&&p.executedIndices.every((a,f)=>integer(a)&&a<n&&(phase===0?a<=g.capIndex:g.sets[previous[1-f]].includes(a))),'Illegal preview price');
        const next=run.controller.id==='startup-only'?1:(phase+1)%run.controller.period;
        need(p.nextPhase===next,'Preview cap clock differs');previous=p.executedIndices;phase=next;
      }
      need(run.controller.id!=='startup-only'||cp.terminalStart.phase===1,'Startup continuation silently received another cap');
    }
  }
  const contrastKeys=new Set();
  for(const c of data.primaryContrasts){
    const key=c.scenario+'/'+c.qInit;need(!contrastKeys.has(key)&&scenarios.has(c.scenario)&&['zero','optimistic'].includes(c.qInit),'Duplicate or malformed contrast');contrastKeys.add(key);
    need(c.availablePairs===12&&c.seedPairs===12&&c.pairedRows?.length===12&&same(c.pairedRows.map(p=>p.seed),data.orderedSeeds),'Incomplete planned pairing');
    [c.mean,c.median,c.range?.minimum,c.range?.maximum,c.interval?.lower,c.interval?.upper].forEach(finite);
    c.pairedRows.forEach(p=>exactNumber(p.difference));
  }
  return data;
}
export function previewReward(record,point){
  const g=record.finite,n=g.prices.length,[a,b]=point.executedIndices,i=a*n+b;
  return {prices:[g.prices[a],g.prices[b]],quantities:[g.rewards.quantityA[i],g.rewards.quantityB[i]],profits:[g.rewards.profitA[i],g.rewards.profitB[i]],consumerSurplus:g.rewards.consumerSurplus[i]};
}
const $=id=>document.getElementById(id);
const text=(id,s)=>{$(id).textContent=s;};
function options(element,rows,selected){element.replaceChildren(...rows.map(([v,label])=>{const o=document.createElement('option');o.value=String(v);o.textContent=label;return o;}));element.value=String(selected);}
function chart(element,series,{baseline=null,labels=[],capRounds=[],xTitle='Round',yTitle='Customer benefit',xMin=0,xMax=null}={}){
  const W=720,H=270,L=67,R=18,T=30,B=58,points=series.flatMap(s=>s.points),ys=points.map(p=>p[1]);
  if(baseline!==null)ys.push(baseline);
  if(!ys.length){element.innerHTML='';return;}
  let lo=Math.min(...ys),hi=Math.max(...ys),pad=Math.max((hi-lo)*.15,.05);lo-=pad;hi+=pad;
  const max=xMax??Math.max(1,...points.map(p=>p[0])),sx=x=>L+(x-xMin)/(max-xMin)*(W-L-R),sy=y=>H-B-(y-lo)/(hi-lo)*(H-T-B);
  let svg=`<title>${escape(yTitle)} by ${escape(xTitle)}</title><rect width="${W}" height="${H}" fill="#fffdf4"/><text x="${L}" y="18" font-size="16">${escape(yTitle)}</text>`;
  for(const x of capRounds)svg+=`<path d="M${sx(x)} ${T}V${H-B}" stroke="#bac9a9" stroke-dasharray="2 5"/>`;
  for(let i=0;i<4;i++){const y=lo+(hi-lo)*i/3,at=sy(y);svg+=`<path d="M${L} ${at}H${W-R}" stroke="#dce2d5"/><text x="${L-8}" y="${at+5}" text-anchor="end" font-size="14">${escape(number(y,2))}</text>`;}
  if(baseline!==null)svg+=`<path d="M${L} ${sy(baseline)}H${W-R}" stroke="#718267" stroke-dasharray="4 5"/><text x="${W-R}" y="${sy(baseline)-7}" text-anchor="end" font-size="13">${escape('Separate long-run floor '+number(baseline,3))}</text>`;
  for(const s of series){const ps=s.points.map(([x,y])=>`${sx(x)},${sy(y)}`).join(' ');svg+=`<polyline points="${ps}" fill="none" stroke="${s.color}" stroke-width="2.5" ${s.dashed?'stroke-dasharray="7 4"':''}/>`;if(s.points.length===1)svg+=`<circle cx="${sx(s.points[0][0])}" cy="${sy(s.points[0][1])}" r="4" fill="${s.color}"/>`;}
  for(const [x,label]of labels)svg+=`<text x="${sx(x)}" y="${H-B+25}" text-anchor="middle" font-size="14">${escape(label)}</text>`;
  svg+=`<text x="${W-R}" y="${H-8}" text-anchor="end" font-size="14">${escape(xTitle)}</text>`;
  element.setAttribute('viewBox',`0 0 ${W} ${H}`);element.innerHTML=svg;
}
function pairChart(element,c){
  const values=c.pairedRows.map(p=>exactNumber(p.difference)),max=Math.max(.1,...values.map(Math.abs),Math.abs(c.interval.lower),Math.abs(c.interval.upper))*1.1,W=720,H=300,L=67,R=18,T=30,B=65;
  const sx=i=>L+(i+.5)/12*(W-L-R),sy=y=>T+(max-y)/(2*max)*(H-T-B);
  let svg=`<title>All twelve whole-market seed differences; selected rhythm minus startup only</title><rect width="720" height="300" fill="#fffdf4"/>`;
  for(const y of [-max/1.1,0,max/1.1])svg+=`<path d="M${L} ${sy(y)}H${W-R}" stroke="${y===0?'#73826a':'#dce2d5'}" ${y===0?'stroke-dasharray="4 4"':''}/><text x="${L-8}" y="${sy(y)+5}" text-anchor="end" font-size="14">${escape(number(y,2))}</text>`;
  values.forEach((v,i)=>{svg+=`<path d="M${sx(i)} ${sy(0)}V${sy(v)}" stroke="#ccd6c1" stroke-width="2"/><circle cx="${sx(i)}" cy="${sy(v)}" r="5" fill="#6d8861"/><text x="${sx(i)}" y="${H-B+25}" text-anchor="middle" font-size="13">${String(c.pairedRows[i].seed).slice(-3)}</text>`;});
  svg+=`<text x="${L}" y="18" font-size="16">Difference in frozen-cycle customer benefit</text><text x="${W-R}" y="${H-10}" text-anchor="end" font-size="14">Seed suffix · full IDs 907001–907012</text>`;
  element.setAttribute('viewBox',`0 0 ${W} ${H}`);element.innerHTML=svg;
}
export function mountAdaptive(data){
  validateAdaptiveData(data);let selectedRun,selectedPoint,record,cursor=0;
  const def=data.meta.defaultSelection;
  options($('market'),data.scenarios.map(s=>[s.scenario.id,maskName(s.scenario.id)]),def.scenario);
  options($('seed'),data.orderedSeeds.map(s=>[s,s]),def.seed);$('initialization').value=def.qInit;$('checkpoint').value=String(def.step);
  $('design-counts').innerHTML=[['192','saved training runs'],['12','paired whole-market seeds'],['4','cap schedules'],['384','audited checkpoints']].map(([a,b])=>`<div><strong>${a}</strong><span>${b}</span></div>`).join('');
  $('all-contrasts').innerHTML=table(['Guard','Scores','Pairs','Mean difference','Median','Seed range','Marginal 95% interval'],data.primaryContrasts.map(c=>[maskName(c.scenario),initName(c.qInit),'12/12',signed(c.mean),signed(c.median),`${signed(c.range.minimum)} to ${signed(c.range.maximum)}`,`${signed(c.interval.lower)} to ${signed(c.interval.upper)}`]));
  text('overall-finding','The four planned comparisons are shown above without dropping any seed. Read the actual training record, frozen continuation, and all-policy model guarantee separately. This design measures conditional learner behavior; it does not establish learned collusion, intent, convergence or an equilibrium.');
  text('audit-detail','All 192 runs and 384 checkpoints were independently checked, including saved-score greedy choices, complete successor graphs, exact saved-weight cycle means, visit counts and diagnostic cloned updates. The numerical core was tested before training; the full adapter was snapshotted during training before the independent referee read its first real checkpoint. The complete main training trajectory was not independently replayed; sampled updates and cloned probes were checked. The development and referee agents use Codex; no Codex/chat account is an experimental shop.');
  function selectCondition(){
    const scenario=$('market').value,qInit=$('initialization').value,previous=$('controller').value||def.controller;
    const candidates=data.runs.filter(r=>r.scenario===scenario&&r.qInit===qInit&&r.seed===def.seed);
    options($('controller'),['startup-only','permanent-cap','selected95','K16'].map(id=>{const r=candidates.find(r=>r.controller.id===id);return[id,scheduleName(r)];}),previous);
    const c=data.primaryContrasts.find(c=>c.scenario===scenario&&c.qInit===qInit);
    $('contrast-card').innerHTML=`<span>Final frozen-cycle comparison · all 12 paired seeds</span><strong>${escape(signed(c.mean))}</strong><p>Mean change in customer benefit. Marginal 95% seed-variation interval: ${escape(signed(c.interval.lower))} to ${escape(signed(c.interval.upper))}.</p><p>Individual differences: ${escape(signed(c.range.minimum))} to ${escape(signed(c.range.maximum))}. Four strata are reported separately.</p>`;
    pairChart($('paired-seeds'),c);selectRun();
  }
  function details(means,geometry){return table(['Saved mean','Shop A','Shop B'],[['Expected profit',value(means.profits[0]),value(means.profits[1])],['Price',value(means.prices[0],5),value(means.prices[1],5)],['Permitted price count',value(geometry.maskCount.A,2),value(geometry.maskCount.B,2)],['Permitted fraction of grid',pct(geometry.maskFraction.A),pct(geometry.maskFraction.B)],['Permitted price span',value(geometry.maskSpan.A,5),value(geometry.maskSpan.B,5)],['Largest-permitted price use',pct(geometry.maxAllowedUsage.A),pct(geometry.maxAllowedUsage.B)]]);}
  function selectRun(){
    selectedRun=data.runs.find(r=>r.scenario===$('market').value&&r.qInit===$('initialization').value&&r.controller.id===$('controller').value&&r.seed===Number($('seed').value));
    need(selectedRun,'Selected run unavailable');selectedPoint=selectedRun.checkpoints.find(p=>p.step===Number($('checkpoint').value));record=data.scenarios.find(s=>s.scenario.id===selectedRun.scenario);cursor=0;
    const cp=selectedPoint,end=cp.frozen.actualTerminal,support=end.visitSupport,unsupported=['A','B'].some(f=>support[f].unvisitedStates||support[f].neverTriedGreedyActions);
    text('selected-scope',`${maskName(selectedRun.scenario)} · ${initName(selectedRun.qInit)} · seed ${selectedRun.seed} · ${scheduleName(selectedRun)}. ${cp.step===2000000?'Primary final checkpoint.':'Secondary intermediate checkpoint.'}`);
    text('visit-support',`${unsupported?'Caution: the eventual cycle includes untrained defaults.':'The eventual-cycle states and greedy actions were tried in training.'} A: ${support.A.unvisitedStates} unvisited states / ${support.A.neverTriedGreedyActions} never-tried greedy actions. B: ${support.B.unvisitedStates} / ${support.B.neverTriedGreedyActions}. These counts concern this cycle; they do not prove convergence.`);
    $('visit-support').classList.toggle('support-warning',unsupported);
    text('training-cs',value(cp.trainingTail.means.consumerSurplus));text('cycle-cs',value(end.means.consumerSurplus));text('controller-floor',value(cp.controllerFloor.longRunFloor));
    text('cycle-description',`${end.transientLength} transient executions, then a ${end.cycleLength}-round cycle from the actual terminal history and clock. Updates and exploration are stopped.`);
    text('floor-description','All permitted continuations in this same finite model satisfy this long-run floor under the verified cap-start envelope. This is separate from a learned outcome and is not a prefix claim from this arbitrary checkpoint clock.');
    const curve=selectedRun.learningCurve.filter(p=>p.endStep<=cp.step);
    chart($('learning-history'),[{color:'#6d8861',points:curve.map(p=>[p.endStep,p.means.consumerSurplus])}],{baseline:exactNumber(cp.controllerFloor.longRunFloor),labels:[[0,'0'],[cp.step/2,(cp.step/2/1000000)+'M'],[cp.step,cp.step/1000000+'M']],xTitle:'Training round · 10,000-round means',xMax:cp.step});
    $('training-details').innerHTML=`<p>Actual window ${cp.trainingTail.startStep.toLocaleString('en-US')}–${cp.step.toLocaleString('en-US')} · mean exploration probability ${number(cp.trainingTail.explorationMean,4)} · cap rule frequency ${pct(cp.trainingTail.geometry.capRuleFrequency)}.</p>${details(cp.trainingTail.means,cp.trainingTail.geometry)}<p>Visited score states: A ${cp.coverage.A.visitedStates}/${cp.coverage.statesPerFirm}; B ${cp.coverage.B.visitedStates}/${cp.coverage.statesPerFirm}. Tried legal score cells: A ${cp.coverage.A.visitedActions}/${cp.coverage.legalCellsPerFirm}; B ${cp.coverage.B.visitedActions}/${cp.coverage.legalCellsPerFirm}.</p>`;
    $('frozen-details').innerHTML=`<p>Exact eventual-cycle means, not the truncated replay average. Cap rule frequency ${pct(end.geometry.capRuleFrequency)}. Gap above separate long-run floor ${signed(exactNumber(end.floorGap))}; gap above unchanged absolute 95% target ${signed(exactNumber(end.target95Gap))}.</p>${details(end.means,end.geometry)}<p>Secondary fresh-cap counterfactual: customer benefit ${value(cp.frozen.freshCap.means.consumerSurplus)}, ${cp.frozen.freshCap.transientLength} transient executions and ${cp.frozen.freshCap.cycleLength}-round eventual cycle. This resets the start; it is not the primary continuation.</p><p>Complete graph: ${cp.frozen.allStates.states.toLocaleString('en-US')} states, ${cp.frozen.allStates.cycleCount} cycles, including ${cp.frozen.allStates.cyclesWithUnvisitedStates} cycles with an unvisited state. These structural cycles are not observations of learning.</p>`;
    text('replay-origin',selectedRun.controller.id==='startup-only'?'Guard continues · no fresh cap':cp.terminalStart.phase===0?'Next: an actual cap round':`Next: guard · cap in ${selectedRun.controller.period-cp.terminalStart.phase} rounds`);
    text('terminal-history',`Starting after ${cp.step.toLocaleString('en-US')} actual training rounds. Previous prices: A ${number(record.finite.prices[cp.terminalStart.previousIndices[0]],5)}, B ${number(record.finite.prices[cp.terminalStart.previousIndices[1]],5)}. This old history earns no new reward.`);
    renderReplay();
  }
  function renderReplay(){
    const points=selectedPoint.preview128.slice(0,cursor),last=points.at(-1),reward=last?previewReward(record,last):null;
    ['a','b'].forEach((id,f)=>{text('price-'+id,reward?number(reward.prices[f],5):'—');text('demand-'+id,reward?number(reward.quantities[f],2):'—');text('profit-'+id,reward?number(reward.profits[f],3):'—');});
    $('replay-step').value=String(cursor);text('replay-position',`${cursor} / 128`);$('one-round').disabled=cursor===128;$('more-rounds').disabled=cursor===128;$('restart-replay').disabled=cursor===0;
    text('replay-feedback',cursor?`${cursor} stored executions revealed. Latest was ${last.phase===0?'an actual cap':'a guard'} round; customer benefit ${number(reward.consumerSurplus)}. ${cursor<128?'The preview may stop before the full transient or cycle ends.':'Preview complete. The full graph, not these 128 rounds, supplies the eventual-cycle means.'}`:'Reveal a saved execution to show prices, purchases and profit. Starting prices above are history only.');
    chart($('replay-prices'),[0,1].map(f=>({color:f===0?'#b56e43':'#4b8190',dashed:f===1,points:points.map((p,i)=>[i+1,previewReward(record,p).prices[f]])})),{labels:[[0,'0'],[32,'32'],[64,'64'],[96,'96'],[128,'128']],capRounds:points.flatMap((p,i)=>p.phase===0?[i+1]:[]),xTitle:'Revealed frozen-policy execution',yTitle:'Price · A solid, B dashed',xMax:128});
    $('replay-ledger').innerHTML=points.length?table(['Round','Rule','A price','B price','A profit','B profit','Customer benefit'],points.map((p,i)=>{const r=previewReward(record,p);return[i+1,p.phase===0?'CAP':'GUARD',number(r.prices[0],5),number(r.prices[1],5),number(r.profits[0]),number(r.profits[1]),number(r.consumerSurplus)];})):'No execution has been revealed.';
  }
  $('market').addEventListener('change',selectCondition);$('initialization').addEventListener('change',selectCondition);
  ['controller','seed','checkpoint'].forEach(id=>$(id).addEventListener('change',selectRun));
  $('one-round').addEventListener('click',()=>{cursor=Math.min(128,cursor+1);renderReplay();});$('more-rounds').addEventListener('click',()=>{cursor=Math.min(128,cursor+16);renderReplay();});$('restart-replay').addEventListener('click',()=>{cursor=0;renderReplay();});$('replay-step').addEventListener('input',()=>{cursor=Math.max(0,Math.min(128,Number($('replay-step').value)));renderReplay();});
  selectCondition();$('adaptive-app').hidden=false;$('go-evidence').hidden=false;$('load-status').hidden=true;
}
async function boot(){try{const response=await fetch('/adaptive-data.json');need(response.ok,'Evidence file unavailable');mountAdaptive(await response.json());}catch(error){$('adaptive-app').hidden=true;$('go-evidence').hidden=true;text('load-status','Learner evidence could not be verified for this display. The controls remain locked. '+error.message);}}
if(typeof document!=='undefined')boot();
