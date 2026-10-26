// Pure exact presentation arithmetic. Importing reads no evidence.
export const MAX_BITS=1000000;
const need=(ok,message)=>{if(!ok)throw Error(message);},abs=n=>n<0n?-n:n;
const bits=n=>abs(n).toString(2).length;
function bounded(n){need(typeof n==='bigint'&&bits(n)<=MAX_BITS,'Exact presentation integer exceeds bit budget');return n;}
function multiply(a,b){need(bits(a)+bits(b)<=MAX_BITS,'Exact presentation product exceeds bit budget');return bounded(a*b);}
function gcd(a,b){a=abs(a);b=abs(b);while(b){const r=a%b;a=b;b=r;}return a;}
export function parseSignedHex(s){
 need(typeof s==='string'&&s.length<=Math.ceil(MAX_BITS/4)+4,'Hex token exceeds budget before parsing');
 need(/^-?0x(?:0|[1-9a-f][0-9a-f]*)$/.test(s)&&s!=='-0x0','Noncanonical signed hexadecimal integer');
 const negative=s[0]==='-',body=s.slice(negative?3:2);
 need((body.length-1)*4+1<=MAX_BITS,'Hex token exceeds bit budget before parsing');
 const n=BigInt('0x'+body);return bounded(negative?-n:n);
}
export function exact(value){
 need(value&&typeof value==='object','Missing exact hex scalar');
 const n=parseSignedHex(value.numeratorHex),d=parseSignedHex(value.denominatorHex);
 need(d>0n&&gcd(n,d)===1n,'Reduced exact scalar with positive denominator required');return {n,d};
}
function reduced(n,d){need(d>0n,'Positive denominator required');bounded(n);bounded(d);const g=gcd(n,d);return {n:n/g,d:d/g};}
const hex=n=>(n<0n?'-0x':'0x')+abs(n).toString(16);
export const pack=value=>{const {n,d}=reduced(value.n,value.d);return {numeratorHex:hex(n),denominatorHex:hex(d)};};
export function add(a,b){a=exact(a);b=exact(b);const g=gcd(a.d,b.d),ad=a.d/g,bd=b.d/g;return pack(reduced(bounded(multiply(a.n,bd)+multiply(b.n,ad)),multiply(ad,b.d)));}
export function negate(a){a=exact(a);return pack({n:-a.n,d:a.d});}
export const subtract=(a,b)=>add(a,negate(b));
export function divideInteger(a,k){a=exact(a);need(Number.isSafeInteger(k)&&k>0,'Positive safe integer divisor required');const g=gcd(a.n,BigInt(k));return pack({n:a.n/g,d:multiply(a.d,BigInt(k)/g)});}
export function compare(a,b){a=exact(a);b=exact(b);const g=gcd(a.d,b.d),x=multiply(a.n,b.d/g),y=multiply(b.n,a.d/g);return x<y?-1:x>y?1:0;}
export const sign=value=>{const {n}=exact(value);return n<0n?'negative':n>0n?'positive':'zero';};
export const ZERO=Object.freeze({numeratorHex:'0x0',denominatorHex:'0x1'});
export const ONE=Object.freeze({numeratorHex:'0x1',denominatorHex:'0x1'});
export const GAP_TARGET=Object.freeze({numeratorHex:'0x1',denominatorHex:'0xf4240'});
export function median(values){need(Array.isArray(values)&&values.length>0,'Median requires available exact values');const sorted=values.slice().sort(compare),m=Math.floor(sorted.length/2);return sorted.length%2?sorted[m]:divideInteger(add(sorted[m-1],sorted[m]),2);}
export function scientificDisplay(value,digits=6){
 need(Number.isInteger(digits)&&digits>=1&&digits<=30,'Display precision outside1..30');
 const raw=exact(value),negative=raw.n<0n,n=abs(raw.n),d=raw.d;
 if(!n)return {lower:'0',upper:'0',sign:'zero',significantDigits:digits};
 // Decimal conversion is only a bounded display operation, never sign authority.
 let exponent=n.toString().length-d.toString().length;
 const power=k=>{need(Number.isSafeInteger(k)&&k>=0&&k*4+1<=MAX_BITS,'Display power exceeds bit budget');return 10n**BigInt(k);};
 if(exponent>=0?n<multiply(d,power(exponent)):multiply(n,power(-exponent))<d)exponent--;
 const shift=digits-1-exponent,numerator=shift>=0?multiply(n,power(shift)):n,denominator=shift>=0?d:multiply(d,power(-shift));
 const low=numerator/denominator,high=low+(numerator%denominator?1n:0n);
 function render(k,prefix){let e=exponent,s=k.toString();if(s.length>digits){e++;s=s.slice(0,digits);}return prefix+(s.length===1?s:s[0]+'.'+s.slice(1))+'e'+(e>=0?'+':'')+e;}
 return {lower:negative?render(high,'-'):render(low,''),upper:negative?render(low,'-'):render(high,''),sign:negative?'negative':'positive',significantDigits:digits};
}

export function validateAvailableRecord(record){
 need(record?.certificate?.passed===true,'Available record needs accepted exact certificate');
 const b=record.baseline?.value,r=record.response?.value,p=record.performance,c=record.certificate;
 [b,r,p?.rawGain,p?.possibleGain?.lower,p?.possibleGain?.upper,c.upperValue,c.responseOptimalityGap,c.requestedGap].forEach(exact);
 need(compare(c.requestedGap,GAP_TARGET)===0,'Prospective absolute gap target differs');
 need(compare(subtract(r,b),p.rawGain)===0&&sign(p.rawGain)===p.rawGainSign,'Raw achieved gain/sign differs');
 need(compare(subtract(c.upperValue,r),c.responseOptimalityGap)===0&&compare(c.responseOptimalityGap,ZERO)>=0,'Nonnegative response gap differs');
 need(compare(p.possibleGain.lower,compare(p.rawGain,ZERO)>0?p.rawGain:ZERO)===0,'Best-gain lower bound hides raw response');
 need(compare(subtract(c.upperValue,b),p.possibleGain.upper)===0&&compare(p.possibleGain.upper,p.possibleGain.lower)>=0,'Best-gain upper bound differs');
 need(c.withinRequestedGap===(compare(c.responseOptimalityGap,c.requestedGap)<=0),'Tight/loose classification differs');
 if(compare(b,ZERO)>0){need(p.relativeGain!==null,'Positive baseline relative gain missing');const x=exact(p.rawGain),y=exact(b);need(compare(p.relativeGain,pack(reduced(multiply(x.n,y.d),multiply(x.d,y.n))))===0&&p.relativeGainReason===null,'Relative raw gain differs');}
 else need(p.relativeGain===null&&typeof p.relativeGainReason==='string'&&p.relativeGainReason.length>0,'Nonpositive baseline needs null relative gain/reason');
 for(const path of [record.baseline,record.response])for(const name of ['A','B']){
  const coverage=path.coverage?.[name];need(coverage,'Both firms coverage required');
  const u=coverage.unweighted;need(Number.isInteger(path.h)&&path.h>=0&&Number.isInteger(path.c)&&path.c>0&&u?.states===path.h+path.c&&u.states<=15376,'Coverage full-path length differs');
  for(const key of ['unvisitedStates','neverTriedChosenActions'])need(Number.isInteger(u[key])&&u[key]>=0&&u[key]<=u.states,'Coverage count outside full path');
  for(const key of ['minimumStateVisits','minimumChosenActionVisits'])need(Number.isInteger(u[key])&&u[key]>=0&&u[key]<=2000000,'Coverage minimum missing/outside saved horizon');
  for(const key of ['unvisitedStateExposure','neverTriedChosenActionExposure'])need(compare(coverage.discounted?.[key],ZERO)>=0&&compare(coverage.discounted[key],ONE)<=0,'Discounted exposure outside[0,1]');
  need(u.unvisitedStates<=u.neverTriedChosenActions&&u.minimumChosenActionVisits<=u.minimumStateVisits&&compare(coverage.discounted.unvisitedStateExposure,coverage.discounted.neverTriedChosenActionExposure)<=0,'Unvisited-state support cannot exceed never-tried action support');
 }
 need(compare(subtract(record.response.eventualCycleCustomerBenefit,record.baseline.eventualCycleCustomerBenefit),p.cycleCustomerBenefitDifference)===0,'Secondary cycle welfare difference differs');
 return true;
}

export function summarizeRecords(records,{seeds=Array.from({length:12},(_,i)=>907001+i),controllers=['startup-only','selected95']}={}){
 need(Array.isArray(records)&&records.length===seeds.length*controllers.length*2,'All planned labels must be retained');
 const index=new Map();let cursor=0;
 for(const seed of seeds)for(const control of controllers)for(const focal of ['A','B']){
  const r=records[cursor++];need(r?.seed===seed&&r.control?.id===control&&r.focal===focal&&typeof r.id==='string','Stable seed/controller/seller identity differs');
  need(!index.has(r.id),'Duplicate record identity');index.set(r.id,r);
  need(typeof r.scientificAvailable==='boolean'&&typeof r.executionSucceeded==='boolean','Orthogonal scientific/execution status flags required');
  if(r.scientificAvailable)validateAvailableRecord(r);
  else need(typeof r.status==='string'&&r.failure,'Unavailable record needs retained status/failure');
 }
 const available=r=>r.scientificAvailable,seedMeans=[],controllerSummaries=[];
 for(const controller of controllers){
  const rows=records.filter(r=>r.control.id===controller),values=rows.filter(available).map(r=>r.performance.rawGain),counts={positive:0,zero:0,negative:0};
  values.forEach(v=>counts[sign(v)]++);const sorted=values.slice().sort(compare);
  const statusGroups={};for(const row of rows){const group=statusGroups[row.status]??={labels:0,executionSucceeded:0,scientificallyAvailable:0,rawGainSignCounts:{positive:0,zero:0,negative:0}};group.labels++;group.executionSucceeded+=Number(row.executionSucceeded);if(available(row)){group.scientificallyAvailable++;group.rawGainSignCounts[sign(row.performance.rawGain)]++;}}
  controllerSummaries.push({controller,plannedSellerLabels:rows.length,executionSucceeded:rows.filter(r=>r.executionSucceeded).length,available:values.length,unavailable:rows.length-values.length,statusGroups,rawGainSignCounts:counts,minimum:sorted[0]??null,median:values.length?median(values):null,maximum:sorted.at(-1)??null,recordIds:rows.map(r=>r.id)});
  for(const seed of seeds){const pair=rows.filter(r=>r.seed===seed),ok=pair.every(available);seedMeans.push({seed,controller,recordIds:pair.map(r=>r.id),status:ok?'available':'unavailable',meanRawGain:ok?divideInteger(add(pair[0].performance.rawGain,pair[1].performance.rawGain),2):null,reason:ok?null:'One or both seller responses unavailable; no zero imputation'});}
 }
 const pairedDifferences=seeds.map(seed=>{const a=seedMeans.find(r=>r.seed===seed&&r.controller===controllers[0]),b=seedMeans.find(r=>r.seed===seed&&r.controller===controllers[1]),ok=a.status==='available'&&b.status==='available';return {seed,comparison:controllers[1]+' minus '+controllers[0],recordIds:[...a.recordIds,...b.recordIds],status:ok?'available':'unavailable',difference:ok?subtract(b.meanRawGain,a.meanRawGain):null,reason:ok?null:'At least one controller seed mean unavailable; paired unit retained'};});
 return {controllerSummaries,seedMeans,pairedDifferences};
}
