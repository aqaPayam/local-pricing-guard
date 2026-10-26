const $=id=>document.getElementById(id);
const names={'base-g15-t1':'Base market · original 15-price label','scale0.5-g15-t1':'Demand scale 0.5','lower-quality-g15-t1':'Lower-quality market','lowcost-g15-t1':'Lower-cost market','base-g11-t1':'Base market · original 11-price label','base-g31-t1':'Base market · original 31-price label','base-g15-t0.5':'Half tolerance','base-g15-t2':'Double tolerance'};
const targetNames={'cap-90pct':'90% of original cap reference','cap-95pct':'95% of original cap reference','cap-99pct':'99% of original cap reference','cap-100pct':'100% of original cap reference','near-Nash-anchor-floor':'Original near-Nash anchor floor'};
const policyNames={'guard-only':'Original guard only','closed-selected':'Originally selected timing','permanent-cap':'Cap every execution'};
const NS='http://www.w3.org/2000/svg';
const text=(tag,value,className='')=>{const n=document.createElement(tag);n.textContent=value;if(className)n.className=className;return n;};
const num=(value,digits=6)=>{if(value===null||value===undefined)return 'Unavailable';const n=Number(value);return Number.isFinite(n)?n.toFixed(digits):'Unavailable';};
const approx=value=>value===null||value===undefined?'Unavailable':`≈ ${num(value)}`;
const radiusNumber=value=>{const n=Number(value);return Number.isFinite(n)?(n!==0&&Math.abs(n)<0.0001?n.toExponential(3):n.toFixed(6)):'Unavailable';};
export function statusView(status){
 if(status==='certified safe'||status==='exact zero reserve')return {className:'safe',label:status==='exact zero reserve'?'Meets target exactly':'Meets the fixed target'};
 if(status==='already failing')return {className:'fail',label:'Below the fixed target'};
 return {className:'unresolved',label:'Not certified here'};
}
export function radiusView(radius){
 if(!radius)return {headline:'Unavailable',detail:'No radius certificate is available.'};
 const s=radius.status||'';
 if(s.includes('empty safe'))return {headline:'Already below target at zero',detail:'The safe nonnegative set is empty; this is not a zero-radius safety claim.'};
 if(s==='certified exact zero radius')return {headline:'Safe only at zero error',detail:'An exactly zero calibration margin is certified.'};
 if(s==='censored safe lower bound')return {headline:`At least ${num(radius.censoredLowerBound)}`,detail:'Safe through the declared search ceiling; the crossing was not identified.'};
 if(s==='certified crossing enclosure'&&radius.lower!==undefined&&radius.upper!==undefined)return {headline:Number(radius.lower)===0?`Between 0 and ${radiusNumber(radius.upper)} taste scales`:`≈ ${radiusNumber(radius.lower)} taste scales`,detail:'The break-even error has signed lower/upper bounds in the saved findings. The shown value is rounded.'};
 return {headline:'Unresolved or unavailable',detail:s||'No signed radius enclosure.'};
}
export function scheduleView(row){
 if(!row)return {className:'unresolved',headline:'Unavailable',number:'—',detail:'No checked timing result is available.'};
 if(row.status==='no recurring cap needed for the long-run target')return {className:'safe',headline:'No recurring cap needed',number:'0 recurring',detail:'The guard alone meets the long-run target throughout this error interval. One immediate startup cap additionally protects finite activation averages; doing nothing has a different startup scope.'};
 if(row.status==='largest certified fixed period'&&Number.isInteger(row.largestPeriod))return {className:'safe',headline:row.largestPeriod===1?'Cap every execution':`Cap every ${row.largestPeriod} executions`,number:`K = ${row.largestPeriod}`,detail:`Largest safe period in this exact fixed-cap family; the next integer period is certified failing. Cap-rule activation rate 1/${row.largestPeriod} is not the fraction of quotes changed.`};
 if(row.status==='infeasible for this fixed-cap family')return {className:'fail',headline:'This cap is insufficient',number:'No period',detail:'Even a cap every execution falls below the original target for this bound. A stricter cap or a different controller is not ruled out.'};
 if(row.status==='censored safe lower bound')return {className:'unresolved',headline:'Search ceiling reached',number:`K ≥ ${row.certifiedSafePeriodLowerBound}`,detail:'The displayed period is certified safe; larger periods are unchecked, so no exact maximum is claimed.'};
 return {className:'unresolved',headline:'Timing boundary unresolved',number:'—',detail:row.status||'No certified integer-period decision.'};
}
export function validateEvidence(data){
 if(!data?.meta?.primaryAudit?.passed||!Array.isArray(data.rows)||data.rows.length!==8||!Array.isArray(data.levels)||data.levels.length!==4)throw Error('Independent sensitivity evidence is unavailable.');
 for(const key of ['primaryManifestSha256','primaryResultsSha256','independentAuditSha256'])if(!/^[a-f0-9]{64}$/.test(data.meta[key]||''))throw Error('Sensitivity evidence identity is missing.');
 const allowed=['0','0.001','0.01','0.05'];
 if(data.levels.some((r,i)=>r.dExact!==allowed[i]))throw Error('Only the four declared error bounds may be shown.');
 for(const row of data.rows)for(const kind of ['effective','nominal']){
  const model=row[kind];if(!model||!Array.isArray(model.targetGroups)||model.targetGroups.length!==5)throw Error('Retained model/target labels are missing.');
  for(const target of model.targetGroups){
   if(!targetNames[target.label]||(target.thresholdExact===null?target.targetIdentityAvailable!==false:!Number.isFinite(Number(target.thresholdExact)))||!Array.isArray(target.policySlots)||target.policySlots.length!==3||!Array.isArray(target.robustPeriods)||target.robustPeriods.length!==4)throw Error('Target/policy evidence is incomplete.');
   for(const p of target.policySlots){
    if(!policyNames[p.slotId]||!Array.isArray(p.levels)||p.levels.length!==4)throw Error('Retained policy comparison is incomplete.');
    p.levels.forEach((v,i)=>{if(v.dExact!==allowed[i])throw Error('Policy level identity differs.');if(v.surplus&&(!Number.isFinite(Number(v.surplus.lower))||!Number.isFinite(Number(v.surplus.upper))||Number(v.surplus.lower)>Number(v.surplus.upper)))throw Error('Malformed welfare enclosure.');});
   }
  }
 }
 return data;
}
function svgNode(tag,attrs={},content){const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(content!==undefined)n.textContent=content;return n;}
function drawBars(target,level){
 const svg=$('policy-bars');svg.replaceChildren();const available=target.policySlots.flatMap(p=>{const v=p.levels.find(x=>x.dExact===level);return v?.surplus?[{p,v}]:[];});
 const narrow=(svg.clientWidth||900)<600,W=narrow?Math.max(300,svg.clientWidth):900,H=narrow?390:300;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
 svg.append(svgNode('title',{},'Saved worst customer-benefit averages and the unchanged original target'));
 if(target.thresholdExact===null){svg.append(svgNode('text',{x:35,y:140,'font-size':27},'Original target unavailable: no protection comparison.'));return;}
 const f=Number(target.thresholdExact),max=Math.max(f,...available.map(x=>Number(x.v.surplus.upper)),1)*1.14,x0=narrow?14:310,width=narrow?W-30:515,scale=x=>x0+width*x/max;
 const ticks=narrow?2:4,bottom=narrow?H-38:270;
 for(let i=0;i<=ticks;i++){const v=max*i/ticks,x=scale(v);svg.append(svgNode('line',{x1:x,x2:x,y1:38,y2:bottom,stroke:'#e1e5d9'}));svg.append(svgNode('text',{x,y:H-8,'text-anchor':'middle','font-size':narrow?13:20},v.toFixed(1)));}
 const tx=scale(f);svg.append(svgNode('line',{x1:tx,x2:tx,y1:25,y2:bottom,stroke:'#516f46','stroke-width':3,'stroke-dasharray':'8 5'}));svg.append(svgNode('text',{x:Math.min(W-55,tx),y:19,'text-anchor':'middle','font-size':narrow?14:21},'Fixed target'));
 target.policySlots.forEach((p,i)=>{const y=narrow?91+i*100:75+i*78,v=p.levels.find(x=>x.dExact===level);svg.append(svgNode('text',{x:narrow?14:6,y:narrow?y-28:y+7,'font-size':narrow?17:23},policyNames[p.slotId]));if(v?.surplus){const lo=Number(v.surplus.lower),hi=Number(v.surplus.upper),safe=statusView(v.status).className==='safe';svg.append(svgNode('rect',{x:x0,y:y-18,width:Math.max(0,scale(lo)-x0),height:33,rx:5,fill:safe?'#3d7673':'#b4775c'}));svg.append(svgNode('line',{x1:scale(lo),x2:scale(hi),y1:y-2,y2:y-2,stroke:'#263f37','stroke-width':5}));svg.append(svgNode('text',{x:scale(lo)-10,y:y+6,'text-anchor':'end','font-size':narrow?17:21,class:'bar-value'},`≈${lo.toFixed(3)}`));}else svg.append(svgNode('text',{x:x0+12,y:y+6,'font-size':narrow?15:22},'Unresolved / unavailable'));});
}
function init(data){
 let market='base-g15-t1',label='cap-95pct',kind='effective',level='0';
 const levels=$('error-levels');data.levels.forEach(v=>{const button=text('button',v.dExact==='0'?'No model gap':`d ≤ ${v.dExact}`);button.type='button';button.dataset.level=v.dExact;button.addEventListener('click',()=>{level=v.dExact;render();});levels.append(button);});
 data.rows.forEach(r=>{const o=text('option',names[r.scenario]||r.scenario);o.value=r.scenario;$('uncertainty-market').append(o);});Object.entries(targetNames).forEach(([id,name])=>{const o=text('option',name);o.value=id;$('uncertainty-target').append(o);});
 $('uncertainty-market').value=market;$('uncertainty-target').value=label;$('uncertainty-model').value=kind;
 $('uncertainty-market').addEventListener('change',e=>{market=e.target.value;render();});$('uncertainty-target').addEventListener('change',e=>{label=e.target.value;render();});$('uncertainty-model').addEventListener('change',e=>{kind=e.target.value;render();});
 function render(){
  const row=data.rows.find(r=>r.scenario===market),model=row[kind],target=model.targetGroups.find(t=>t.label===label);levels.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.level===level)));
  $('gap-description').textContent=level==='0'?'The actual market matches the original demand calibration.':'The rule stays fixed. Actual product quality may be lower by up to '+level+' times this market’s taste scale (mu). This is not a percentage or a probability.';
  $('uncertainty-scope').textContent='Only inside product quality changes. External enforcement, outside option, buyer count, taste scale and original absolute target stay fixed. Different original grid labels can retain different physical caps.';
  const fixed=$('fixed-target');fixed.replaceChildren(text('span',targetNames[label]),text('strong',approx(target.thresholdExact)),text('small','Original saved threshold, including its margin'));
  const cards=$('policy-cards');cards.replaceChildren();
  target.policySlots.forEach(p=>{const v=p.levels.find(x=>x.dExact===level),status=statusView(v?.status),card=text('article','',`policy-card ${status.className}`);card.append(text('h3',policyNames[p.slotId]));card.append(text('p',p.policyKind==='guard'?'No recurring cap · zero startup caps':p.available?`One actual cap every ${p.period} execution${p.period===1?'':'s'}`:'Inherited policy unavailable','policy-rhythm'));card.append(text('span',v?.surplus?approx(v.surplus.lower):'Unavailable','floor-number'));card.append(text('span',status.label,'status'));card.append(text('p',v?.reserve?`Benefit above target at this bound: ${approx(v.reserve.lower)}.`:'No certified reserve at this bound.'));
   if(p.policyKind==='guard')card.append(text('p','This floor concerns the long run. One startup cap also gives this same lower floor for every average from activation.'));
   if(p.duplicateOf)card.append(text('p',`Same policy as “${policyNames[p.duplicateOf]}” for this target; a retained comparison slot.`,'duplicate'));cards.append(card);});
  drawBars(target,level);const schedule=scheduleView(target.robustPeriods.find(r=>r.dExact===level)),rs=$('robust-schedule');rs.className='robust-schedule '+schedule.className;rs.replaceChildren(text('span',schedule.headline,'schedule-status'),text('strong',schedule.number,'period-number'),text('p',schedule.detail));
  const radius=$('radius-list');radius.replaceChildren();target.policySlots.forEach(p=>{const r=radiusView(p.radius),item=text('article','','radius-item');item.append(text('b',policyNames[p.slotId]),text('strong',r.headline),text('p',r.detail));radius.append(item);});
  $('uncertainty-audit').textContent=`Independent audit passed. Manifest ${data.meta.primaryManifestSha256}; results ${data.meta.primaryResultsSha256}; audit ${data.meta.independentAuditSha256}. Separate interval implementations share Python Decimal transcendental arithmetic; this is not formal verification.`;
 }
 $('uncertainty-loading').hidden=true;$('uncertainty-app').hidden=false;render();globalThis.addEventListener?.('resize',render);
}
async function boot(){try{const response=await fetch('/uncertainty-data.json');if(!response.ok)throw Error('Sensitivity evidence could not be loaded.');init(validateEvidence(await response.json()));}catch(error){$('uncertainty-app').hidden=true;$('uncertainty-loading').hidden=false;$('uncertainty-loading').textContent='This comparison is unavailable. '+error.message+' No protection value has been substituted.';}}
if(typeof document!=='undefined')boot();
