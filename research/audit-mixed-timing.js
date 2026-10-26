// Independent mixed-timing arithmetic and controller audit.
// No primary timing/search/calendar module is imported. Importing this file
// performs no evidence reads. Real-data orchestration will be added only after
// the prospective primary schema/source review; current tests are artificial.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SCENARIOS=['base-g15-t1','scale0.5-g15-t1','lower-quality-g15-t1','lowcost-g15-t1',
  'base-g11-t1','base-g31-t1','base-g15-t0.5','base-g15-t2'];
const LABELS=['cap-90pct','cap-95pct','cap-99pct','cap-100pct','near-Nash-anchor-floor'];
const KINDS=['finite','effective','nominal'];

export const MAX_K = 65536;
let CHECKS=0;
export const insist = (ok, message) => { CHECKS++;if (!ok) throw new Error(message); };
const gcd = (x,y) => {x=x<0n?-x:x; y=y<0n?-y:y; while(y){const r=x%y;x=y;y=r;} return x;};

export class Rat {
  constructor(n,d=1n) {
    n=BigInt(n);d=BigInt(d);insist(d!==0n,'Nonzero exact denominator');
    if(d<0n){n=-n;d=-d;}const g=gcd(n,d);this.n=n/g;this.d=d/g;
    Object.freeze(this);
  }
  add(x){x=rat(x);return new Rat(this.n*x.d+x.n*this.d,this.d*x.d);}
  sub(x){x=rat(x);return new Rat(this.n*x.d-x.n*this.d,this.d*x.d);}
  mul(x){x=rat(x);return new Rat(this.n*x.n,this.d*x.d);}
  div(x){x=rat(x);insist(x.n!==0n,'Exact division by nonzero value');return new Rat(this.n*x.d,this.d*x.n);}
  neg(){return new Rat(-this.n,this.d);}
  cmp(x){x=rat(x);const d=this.n*x.d-x.n*this.d;return d<0n?-1:d>0n?1:0;}
  eq(x){return this.cmp(x)===0;}
  floor(){let z=this.n/this.d;if(this.n<0n&&this.n%this.d)z--;return z;}
  ceil(){return -this.neg().floor();}
  toJSON(){return {numerator:String(this.n),denominator:String(this.d)};}
  toString(){return `${this.n}/${this.d}`;}
}

export function exactDouble(value) {
  insist(typeof value==='number'&&Number.isFinite(value),'Finite binary64 import');
  const view=new DataView(new ArrayBuffer(8));view.setFloat64(0,value,false);
  const bits=view.getBigUint64(0,false),sign=bits>>63n?-1n:1n;
  const exp=Number((bits>>52n)&2047n),mantissa=bits&((1n<<52n)-1n);
  if(exp===0&&mantissa===0n)return new Rat(0n);
  const m=exp===0?mantissa:(1n<<52n)+mantissa;
  const e=exp===0?-1074:exp-1075;
  return e>=0?new Rat(sign*(m<<BigInt(e))):new Rat(sign*m,1n<<BigInt(-e));
}

export function exactDecimal(value) {
  insist(typeof value==='string','Exact decimal string required');
  const m=/^([+-]?)(\d+)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(value);
  insist(m!==null,'Valid finite decimal string');
  const exp=Number(m[4]||0)-(m[3]||'').length;
  insist(Number.isSafeInteger(exp)&&Math.abs(exp)<=100000,'Bounded decimal exponent');
  const n=BigInt((m[2]+(m[3]||''))||'0')*(m[1]==='-'?-1n:1n);
  return exp>=0?new Rat(n*10n**BigInt(exp)):new Rat(n,10n**BigInt(-exp));
}

export function rat(x) {
  if(x instanceof Rat)return x;
  if(typeof x==='number')return exactDouble(x);
  if(typeof x==='bigint')return new Rat(x);
  if(typeof x==='string')return exactDecimal(x);
  insist(x&&typeof x==='object'&&typeof x.numerator==='string'&&typeof x.denominator==='string','Explicit exact rational object');
  insist(/^-?\d+$/.test(x.numerator)&&/^\d+$/.test(x.denominator),'Integral rational strings');
  return new Rat(x.numerator,x.denominator);
}

export function outwardDecimal(x,precision=30,direction='lower') {
  x=rat(x);insist(Number.isInteger(precision)&&precision>=1&&precision<=200,'Declared significant digits');
  insist(direction==='lower'||direction==='upper','Outward display direction');
  if(x.n===0n)return '0';
  const n=x.n<0n?-x.n:x.n;
  let exponent=String(n).length-String(x.d).length;
  const scale=exponent>=0?new Rat(10n**BigInt(exponent)):new Rat(1n,10n**BigInt(-exponent));
  if(new Rat(n,x.d).cmp(scale)<0)exponent--;
  const places=exponent-precision+1;
  const step=places>=0?new Rat(10n**BigInt(places)):new Rat(1n,10n**BigInt(-places));
  const units=x.div(step),rounded=direction==='lower'?units.floor():units.ceil();
  return `${rounded}e${places}`;
}

export function verifyDisplay(bounds,display,precision=30) {
  const low=rat(bounds.lower),high=rat(bounds.upper);
  insist(low.cmp(high)<=0,'Ordered exact rate enclosure');
  insist((display.significantDigits??display.precision)===precision,'Declared rate-display precision');
  if(display.significantDigits!==undefined&&display.precision!==undefined)
    insist(display.significantDigits===display.precision,'Consistent precision labels');
  insist(exactDecimal(display.lower).cmp(low)<=0&&exactDecimal(display.upper).cmp(high)>=0,'Outward rate displays enclose exact endpoints');
  // Requiring the declared significant rounding prevents arbitrarily loose
  // strings from passing only the weaker inclusion check.
  insist(exactDecimal(display.lower).eq(exactDecimal(outwardDecimal(low,precision,'lower'))),'Canonical lower significant rounding');
  insist(exactDecimal(display.upper).eq(exactDecimal(outwardDecimal(high,precision,'upper'))),'Canonical upper significant rounding');
}

export function tailEnvelope(rewards) {
  insist(Array.isArray(rewards)&&rewards.length>0,'Nonempty artificial or verified orbit rewards');
  const terms=rewards.map(rat);
  insist(terms.every((r,i)=>!i||r.cmp(terms[i-1])<=0),'Nonincreasing upper-path rewards');
  const prefix=[new Rat(0n)];for(const r of terms)prefix.push(prefix.at(-1).add(r));
  const queries=[];
  return {terms,queries,r0:terms[0],cstar:terms.at(-1),
    sum(L){insist(Number.isInteger(L)&&L>=1&&L<=MAX_K,'Bounded frontier sum length');queries.push(L);
      return L<=terms.length?prefix[L]:prefix.at(-1).add(terms.at(-1).mul(BigInt(L-terms.length)));},
    reward(age){insist(Number.isInteger(age)&&age>=0,'Nonnegative execution age');return terms[Math.min(age,terms.length-1)];}
  };
}

export function finiteEnvelope(game) {
  const {prices,sets,upper,capIndex,rewards}=game,n=prices.length;
  insist(n>0&&prices.every((p,i)=>Number.isFinite(p)&&(!i||p>prices[i-1])),'Sorted finite quotes');
  insist(Array.isArray(sets)&&sets.length===n&&Array.isArray(upper)&&upper.length===n,'Full support dimensions');
  insist(Number.isInteger(capIndex)&&capIndex>=0&&capIndex<n,'Valid finite physical-cap index');
  for(let j=0;j<n;j++){
    const s=sets[j];insist(Array.isArray(s)&&s.length>0&&s.every((x,i)=>Number.isInteger(x)&&x>=0&&x<n&&(!i||x>s[i-1])),'Nonempty sorted support');
    insist(upper[j]===s.at(-1),'Upper action is attained support maximum');
    insist(!j||upper[j]>=upper[j-1],'Entire upper map nondecreasing');
  }
  insist(upper[capIndex]>=capIndex,'Cap-start nondecreasing orbit premise');
  const cs=rewards.consumerSurplus;
  insist(cs.length===n*n&&cs.every(Number.isFinite),'Full finite customer-benefit table');
  for(let a=0;a<n;a++)for(let b=0;b<n;b++){
    if(a)insist(cs[a*n+b]<=cs[(a-1)*n+b],'A-coordinate benefit monotonicity');
    if(b)insist(cs[a*n+b]<=cs[a*n+b-1],'B-coordinate benefit monotonicity');
  }
  const indices=[];let at=capIndex;
  for(let guard=0;guard<=n;guard++){
    insist(!indices.includes(at),'Upper cap orbit has no nontrivial cycle');indices.push(at);
    const next=upper[at];if(next===at)break;
    insist(next>at&&guard<n,'Finite upper orbit reaches a fixed point');at=next;
  }
  insist(upper[indices.at(-1)]===indices.at(-1),'Actual eventual fixed point retained');
  return {...tailEnvelope(indices.map(i=>cs[i*n+i])),indices};
}

export function verifyFiniteEconomics(record) {
  const {finite:game,scenario}=record,{economy:e}=scenario,{prices,epsilon}=game,n=prices.length;
  insist(e&&e.mu>0&&e.buyers>0,'Positive economic scale');
  insist(epsilon===scenario.epsilon&&game.comparisonAllowance===epsilon+1e-12,'Unchanged binary64 guard allowance');
  const tables={consumerSurplus:[],profitA:[],profitB:[],quantityA:[],quantityB:[]};
  // Written here, not imported from either primary study or old browser core.
  for(const a of prices)for(const b of prices){
    const x=(e.quality-a-e.outsideQuality)/e.mu,y=(e.quality-b-e.outsideQuality)/e.mu;
    const shift=Math.max(0,x,y),ea=Math.exp(x-shift),eb=Math.exp(y-shift),den=Math.exp(-shift)+ea+eb;
    const qa=e.buyers*ea/den,qb=e.buyers*eb/den;
    const r={consumerSurplus:e.buyers*e.mu*(shift+Math.log(den)),profitA:qa*(a-e.cost),profitB:qb*(b-e.cost),quantityA:qa,quantityB:qb};
    for(const name of Object.keys(tables))tables[name].push(r[name]);
  }
  for(const name of Object.keys(tables))assert.deepEqual(game.rewards[name],tables[name],`Every independent ${name} table value`);
  const sets=[],bestProfits=[];
  for(let rival=0;rival<n;rival++){
    const pa=prices.map((_,own)=>tables.profitA[own*n+rival]),pb=prices.map((_,own)=>tables.profitB[rival*n+own]);
    const ba=Math.max(...pa),bb=Math.max(...pb);
    const sa=pa.flatMap((p,i)=>ba-p<=epsilon+1e-12?[i]:[]),sb=pb.flatMap((p,i)=>bb-p<=epsilon+1e-12?[i]:[]);
    assert.deepEqual(sa,sb,'Both shops have same numerical legal supports');sets.push(sa);bestProfits.push(ba);
  }
  assert.deepEqual(game.sets,sets,'Every independently enumerated numerical mask');
  assert.deepEqual(game.upper,sets.map(s=>s.at(-1)),'Every independently attained maximum');
  assert.deepEqual(game.rowBestProfits,bestProfits,'Every full-row best profit');
  return {payoffPairs:n*n,envelope:finiteEnvelope(game)};
}

export function adjacentRates(K,a,b) {
  insist(Number.isInteger(K)&&K>=1&&K+1<=MAX_K,'Adjacent frontier inside ceiling');a=rat(a);b=rat(b);
  insist(a.cmp(0n)>=0&&b.cmp(0n)<0,'Safe amount and STRICT next failure');
  const p=a.div(a.sub(b)),fixed=new Rat(1n,BigInt(K)),rate=new Rat(1n).div(rat(BigInt(K)).add(p));
  return {K,a,b,p,fixed,rate,absoluteSaving:fixed.sub(rate),relativeSaving:fixed.sub(rate).div(fixed)};
}

export function boundedFrontier(envelope,F,maxK=MAX_K) {
  F=rat(F);insist(Number.isInteger(maxK)&&maxK>=1&&maxK<=MAX_K,'Declared bounded frontier ceiling');
  if(F.cmp(envelope.cstar)<=0)return {status:'startup-only',rate:new Rat(0n),startupCaps:1};
  if(F.cmp(envelope.r0)>0)return {status:'infeasible-first-cap',rate:null,startupCaps:1};
  const excess=K=>envelope.sum(K).sub(F.mul(BigInt(K)));
  let lo=1,hi=null;
  while(lo<maxK){const next=Math.min(maxK,lo*2);if(excess(next).cmp(0n)<0){hi=next;break;}lo=next;}
  if(hi===null)return {status:'censored',safeK:lo,rateUpper:new Rat(1n,BigInt(lo)),rateLower:new Rat(0n)};
  while(hi-lo>1){const mid=Math.floor((lo+hi)/2);if(excess(mid).cmp(0n)>=0)lo=mid;else hi=mid;}
  return {status:'adjacent',...adjacentRates(lo,excess(lo),excess(hi))};
}

export function intervalRates(K,aBounds,bBounds) {
  const aL=rat(aBounds.lower),aU=rat(aBounds.upper),bL=rat(bBounds.lower),bU=rat(bBounds.upper);
  insist(aL.cmp(aU)<=0&&bL.cmp(bU)<=0&&aL.cmp(0n)>=0&&bU.cmp(0n)<0,'Signed ordered interval frontier');
  const lower=adjacentRates(K,aU,bU).rate,construction=adjacentRates(K,aL,bL);
  return {lower,upper:construction.rate,constructed:construction.rate,gap:construction.rate.sub(lower),construction};
}

export function calendarBlocks(K,a,b,count=64) {
  const values=adjacentRates(K,a,b);a=values.a;b=values.b;
  insist(Number.isInteger(count)&&count>=0&&count<=10000,'Bounded diagnostic block count');
  const H=a.sub(b),blocks=[];let credit=new Rat(0n);
  for(let index=0;index<count;index++){
    const before=credit,long=a.cmp(0n)>0&&credit.cmp(b.neg())>=0;
    const amount=long?b:a;credit=credit.add(amount);
    insist(credit.cmp(0n)>=0&&credit.cmp(H)<0,'Exact boundary-credit invariant');
    blocks.push({index,length:K+(long?1:0),long,before,amount,after:credit});
  }
  return blocks;
}

export function verifyCalendarBlocks(saved,K,a,b) {
  const expected=calendarBlocks(K,a,b,saved.length);
  for(let i=0;i<saved.length;i++){
    const s=saved[i],e=expected[i];
    insist(s.length===e.length,'Funded gap length including equality tie');
    for(const [field,value]of [['creditBeforeExact',e.before],['creditAfterExact',e.after],['endpointCreditExact',e.amount]])
      insist(rat(s[field]).eq(value),`Exact ${field}`);
  }
  return expected;
}

export function executionPreview(envelope,F,K,a,b,horizon=256) {
  F=rat(F);const blocks=calendarBlocks(K,a,b,horizon);let block=0,age=0,total=new Rat(0n),credit=new Rat(0n),caps=0;
  const rows=[];
  for(let t=0;t<horizon;t++){
    const current=blocks[block],reward=envelope.reward(age);if(age===0)caps++;
    total=total.add(reward.sub(F));
    const before=credit,complete=age+1===current.length;
    if(complete){credit=current.after;block++;}
    insist(total.cmp(0n)>=0,'Every actually executed activation prefix protected');
    rows.push({execution:t+1,mode:age===0?'cap':'guard',age,blockLength:current.length,reward,
      boundaryCreditBefore:before,boundaryCreditAfter:credit,prefixExcess:total,caps,blockComplete:complete});
    age=complete?0:age+1;
  }
  return rows;
}

export function assertRationalEqual(saved,actual,message) {assert(rat(saved).eq(actual),message);}

export function scientificBounds(saved) {
  insist(saved&&typeof saved==='object','Scientific bound object present');
  const lo=rat(saved.lowerExact),hi=rat(saved.upperExact);
  insist(lo.cmp(hi)<=0,'Scientific bounds ordered');
  verifyDisplay({lower:lo,upper:hi},saved.outwardDisplay);
  return {lo,hi};
}

function equalBounds(saved,lo,hi,label) {
  const actual=scientificBounds(saved);
  insist(actual.lo.eq(lo)&&actual.hi.eq(hi),label);return actual;
}

function equalRateBounds(saved,lo,hi,label) {
  insist(saved&&rat(saved.lower).eq(lo)&&rat(saved.upper).eq(hi),label);
}

function signName(x){return rat(x).cmp(0n)<0?'negative':rat(x).cmp(0n)>0?'positive':'zero';}

export function verifyPrimaryCalendar(calendar) {
  const {kind,K,blockPreview64:rows}=calendar;
  insist(['funded-mixed','fixed-safe','startup-only','unavailable'].includes(kind),'Declared calendar type');
  if(kind==='startup-only'||kind==='unavailable'){
    insist(K===null&&calendar.creditAExact===null&&calendar.creditBExact===null&&Array.isArray(rows)&&rows.length===0,'No invented repeating calendar');
    insist(calendar.creditUpperExclusiveExact===null,'No invented finite credit bound for nonrepeating calendar');
    insist(calendar.startupCaps===(kind==='startup-only'?1:null),'Truthful startup count');return [];
  }
  insist(calendar.startupCaps===1&&Number.isInteger(K)&&K>=1&&K<=MAX_K,'Actual first cap and bounded calendar gap');
  const a=rat(calendar.creditAExact),b=calendar.creditBExact===null?null:rat(calendar.creditBExact);
  insist(a.cmp(0n)>=0,'Certified nonnegative short credit');
  insist(kind==='funded-mixed'?b!==null&&b.cmp(0n)<0&&K+1<=MAX_K:b===null,'Calendar credit type');
  if(b!==null)assertRationalEqual(calendar.creditUpperExclusiveExact,a.sub(b),'Exact exclusive bounded-credit ceiling H');
  else insist(calendar.creditUpperExclusiveExact===null,'Fixed-safe surplus need not have a finite exclusive credit ceiling');
  insist(Array.isArray(rows)&&rows.length===64,'Every64 predeclared diagnostic block retained');
  let credit=rat(0n),start=1;const expected=[];
  for(let i=0;i<64;i++){
    const long=b!==null&&a.cmp(0n)>0&&credit.cmp(b.neg())>=0;
    const length=K+(long?1:0),amount=long?b:a,after=credit.add(amount),row=rows[i];
    insist(row.block===i+1&&row.startExecution===start&&row.length===length,'Every block index/start clock/length');
    insist(row.long===long,'Truthful long-block flag');
    if(Object.hasOwn(row,'endExecution'))insist(row.endExecution===start+length-1,'Every block completion clock');
    assertRationalEqual(row.boundaryCreditBeforeExact,credit,'Boundary credit before block');
    assertRationalEqual(row.blockEndpointCreditExact,amount,'Exact endpoint credit');
    assertRationalEqual(row.boundaryCreditAfterExact,after,'Boundary credit after block');
    if(Object.hasOwn(row,'endpointSign'))insist(row.endpointSign===signName(amount),'Truthful endpoint sign');
    insist(after.cmp(0n)>=0&&(b===null||after.cmp(a.sub(b))<0),'Exact conservative-credit invariant');
    expected.push({start,length,long,before:credit,amount,after});credit=after;start+=length;
  }
  return expected;
}

export function verifyRateFields(r,{lower,upper,constructed,bestK=null,pLower=null,pUpper=null,forceInexact=false}) {
  insist(r&&r.bestFixedK===bestK,'Best fixed comparator is established, not an unresolved fallback');
  const fixed=bestK===null?null:new Rat(1n,BigInt(bestK));
  if(fixed===null)insist(r.fixedRateExact===null,'No fabricated best-fixed rate');
  else assertRationalEqual(r.fixedRateExact,fixed,'Own best-fixed rate');
  equalRateBounds(r.optimumRateBoundsExact,lower,upper,'Exact optimum-rate bounds');
  verifyDisplay({lower,upper},r.optimumRateDisplay);
  assertRationalEqual(r.constructedRateExact,constructed,'Exact achieved calendar rate');
  verifyDisplay({lower:constructed,upper:constructed},r.constructedRateDisplay);
  assertRationalEqual(r.optimalityGapUpperExact,constructed.sub(lower),'Honest rate-optimality gap');
  insist(r.exactOptimum===(!forceInexact&&lower.eq(upper)),'Exact optimum flag matches proof');
  if(pLower===null)insist(r.mixFractionBoundsExact===null,'No invented mixture');
  else {equalRateBounds(r.mixFractionBoundsExact,pLower,pUpper,'Block mixture bounds, not time share');
    insist(r.mixFractionSigns.lower===signName(pLower)&&r.mixFractionSigns.upper===signName(pUpper),'Exact block-mixture signs');}
  if(fixed===null){
    insist(r.absoluteSavingBoundsExact===null&&r.relativeSavingBoundsExact===null&&r.constructedSavingExact===null,'No invented savings versus an unknown comparator');
  }else{
    equalRateBounds(r.absoluteSavingBoundsExact,fixed.sub(upper),fixed.sub(lower),'Absolute frequency saving');
    equalRateBounds(r.relativeSavingBoundsExact,fixed.sub(upper).div(fixed),fixed.sub(lower).div(fixed),'Relative frequency saving');
    assertRationalEqual(r.constructedSavingExact,fixed.sub(constructed),'Constructed saving');
    insist(r.absoluteSavingSigns.lower===signName(fixed.sub(upper))&&r.absoluteSavingSigns.upper===signName(fixed.sub(lower)),'Exact saving signs, including tiny positives');
    insist(r.relativeSavingSigns.lower===signName(fixed.sub(upper).div(fixed))&&r.relativeSavingSigns.upper===signName(fixed.sub(lower).div(fixed))&&r.constructedSavingSign===signName(fixed.sub(constructed)),'All remaining relative/constructed sign labels');
  }
}

export function verifyPrimaryTarget(row,{F,r0,cstar,kind,finite=null}) {
  F=rat(F);assertRationalEqual(row.actualThresholdExact,F,'Unchanged actual target');
  insist(typeof row.label==='string'&&row.prefixCertificateScope==='Every prefix from the first actual cap; not sliding windows or arbitrary old guard histories','Target proof scope');
  const f=row.frontier;
  insist(f.maxK===MAX_K&&Array.isArray(f.queryLengths)&&f.queryLengths.every(k=>Number.isInteger(k)&&k>=1&&k<=MAX_K),'Every frontier query obeys ceiling');
  let interpretation;
  if(F.cmp(cstar.lo)<=0){
    insist(row.status==='certified startup-only zero limiting rate'&&row.calendar.kind==='startup-only','Certified zero-rate startup classification');
    verifyRateFields(row.rates,{lower:rat(0n),upper:rat(0n),constructed:rat(0n)});
    assertRationalEqual(row.rates.fixedFamilyInfimumRateExact,rat(0n),'Zero fixed-family infimum');
    insist(f.bestFixedK===null&&f.certifiedSafeK===null&&f.safe===null&&f.failing===null&&f.queryLengths.length===0,'No fabricated frontier for startup-only');
    interpretation={type:'startup'};
  }else if(F.cmp(r0.hi)>0){
    insist(row.status==='infeasible cap-first two-mode family'&&row.rates===null&&row.calendar.kind==='unavailable','First-cap infeasibility is unavailable, not zero');
    insist(f.bestFixedK===null&&f.certifiedSafeK===null&&f.safe===null&&f.failing===null&&f.queryLengths.length===0,'No fabricated infeasible frontier');
    interpretation={type:'infeasible'};
  }else{
    const safe=f.safe,fail=f.failing,L=safe?.period??null,H=fail?.period??null;
    insist(L===f.certifiedSafeK,'Safe-bound metadata agrees');
    if(L!==null)insist(Number.isInteger(L)&&L>=1&&L<=MAX_K&&f.queryLengths.includes(L),'Safe period queried in range');
    if(H!==null)insist(Number.isInteger(H)&&H>=1&&H<=MAX_K&&(L===null||H>L)&&f.queryLengths.includes(H),'Failing period queried in range');
    let a,b,safeSum,failSum;
    if(safe){safeSum=scientificBounds(safe.sumBounds);a=equalBounds(safe.excessBounds,safeSum.lo.sub(F.mul(BigInt(L))),safeSum.hi.sub(F.mul(BigInt(L))),'Exact safe excess subtraction');insist(a.lo.cmp(0n)>=0,'Certified safe sign');}
    if(fail){failSum=scientificBounds(fail.sumBounds);b=equalBounds(fail.excessBounds,failSum.lo.sub(F.mul(BigInt(H))),failSum.hi.sub(F.mul(BigInt(H))),'Exact failing excess subtraction');insist(b.hi.cmp(0n)<0,'Certified STRICT failing sign');}
    if(L!==null&&H===L+1){
      insist(f.bestFixedK===L&&row.calendar.kind==='funded-mixed','Adjacent boundaries establish own best fixed K');
      const rates=intervalRates(L,{lower:a.lo,upper:a.hi},{lower:b.lo,upper:b.hi});
      const pLower=adjacentRates(L,a.lo,b.lo).p,pUpper=adjacentRates(L,a.hi,b.hi).p;
      verifyRateFields(row.rates,{lower:rates.lower,upper:rates.upper,constructed:rates.constructed,bestK:L,pLower,pUpper});
      assertRationalEqual(row.calendar.creditAExact,a.lo,'Calendar uses lower short credit');
      assertRationalEqual(row.calendar.creditBExact,b.lo,'Calendar uses lower long credit');
      insist(row.calendar.K===L,'Calendar frontier identity');
      const status=kind==='finite'&&a.lo.eq(0n)?'certified exact equality frontier; zero mixed saving':rates.lower.eq(rates.upper)?'certified exact mixed optimum':'certified continuous optimum enclosure';
      insist(row.status===status,'Truthful exact/continuous/equality classification');
      interpretation={type:'adjacent',L,H,a,b,safeSum,failSum};
    }else if(L!==null){
      insist(f.bestFixedK===null&&row.calendar.kind==='fixed-safe'&&row.calendar.K===L,'Unresolved/censored schedule is fixed-safe only');
      const lower=H===null?rat(0n):new Rat(1n,BigInt(H)),upper=new Rat(1n,BigInt(L));
      verifyRateFields(row.rates,{lower,upper,constructed:upper,forceInexact:true});
      assertRationalEqual(row.calendar.creditAExact,a.lo,'Fallback safe lower credit');
      insist(row.status===(L===MAX_K?'censored safe ceiling':'unresolved certified frontier bracket'),'Censoring remains distinct from optimum');
      interpretation={type:'fallback',L,H,a,b,safeSum,failSum};
    }else{
      insist(row.status==='unresolved cap/target boundary; no certified schedule'&&row.rates===null&&row.calendar.kind==='unavailable'&&f.bestFixedK===null,'Honest unresolved boundary');
      interpretation={type:'unresolved',H,b,failSum};
    }
    if(kind==='finite'&&finite){
      const expected=boundedFrontier(finite,F);
      if(expected.status==='adjacent'){
        insist(interpretation.type==='adjacent'&&interpretation.L===expected.K,'Independent finite largest-safe search');
        insist(interpretation.safeSum.lo.eq(finite.sum(expected.K))&&interpretation.safeSum.hi.eq(finite.sum(expected.K)),'Exact independently summed finite safe frontier');
        insist(interpretation.failSum.lo.eq(finite.sum(expected.K+1))&&interpretation.failSum.hi.eq(finite.sum(expected.K+1)),'Exact independently summed finite next failure');
      }else insist(expected.status==='censored'&&interpretation.type==='fallback'&&interpretation.L===MAX_K,'Exact finite censored search');
    }
  }
  verifyPrimaryCalendar(row.calendar);
  return interpretation;
}

export function verifyPrimaryPreview(row,{F,kind,cstarLower,reward,price}) {
  const c=row.calendar,rows=row.executionPreview;
  if(c.kind==='unavailable'){insist(Array.isArray(rows)&&rows.length===0,'Unavailable evidence has no invented execution');return;}
  const horizon=kind==='finite'?256:64;
  insist(Array.isArray(rows)&&rows.length===horizon,'Declared bounded preview retained');
  const startup=c.kind==='startup-only',a=c.creditAExact===null?null:rat(c.creditAExact),b=c.creditBExact===null?null:rat(c.creditBExact);
  let B=rat(0n),age=0,length=null,endpoint=null,sumLow=rat(0n),sumHigh=rat(0n),previous=null,capCount=0,block=1;
  const allowedFields=new Set(['execution','mode','age','executedPrice','rewardBounds',
    'boundaryCreditBeforeExact','boundaryCreditAfterExact','completedBlock','cumulativePrefixExcessBounds',
    'certifiedPrefixLowerBoundExact','scope','previousExecutedPrice','previousIndices','executedIndices',
    'plannedGapLength','block','blockLength','capCount']);
  for(let i=0;i<horizon;i++){
    const r=rows[i];insist(Object.keys(r).every(k=>allowedFields.has(k)),'All preview fields have independent scientific checks');
    if(!startup&&age===0){const long=b!==null&&a.cmp(0n)>0&&B.cmp(b.neg())>=0;length=c.K+(long?1:0);endpoint=long?b:a;}
    const expectedReward=reward(age),expectedPrice=price(age),mode=age===0?'cap':'guard';if(mode==='cap')capCount++;
    insist(r.execution===i+1&&r.mode===mode&&r.age===age,'Actual execution clock/mode/age');
    assert.deepEqual(r.executedPrice,expectedPrice,'Current executed price or genuine enclosure');
    assert.deepEqual(r.previousExecutedPrice,previous,'Carried previous executed price; old memory unearned');
    assert.deepEqual(r.previousIndices,previous!==null&&Object.hasOwn(previous,'index')?[previous.index,previous.index]:null,'Both previous symmetric quote indices');
    assert.deepEqual(r.executedIndices,Object.hasOwn(expectedPrice,'index')?[expectedPrice.index,expectedPrice.index]:null,'Both currently executed quote indices');
    insist(r.plannedGapLength===(startup?null:length),'Truthful planned gap, including nonrepeating startup');
    if(Object.hasOwn(r,'block'))insist(r.block===block,'Actual preview block number');
    if(Object.hasOwn(r,'blockLength'))insist(r.blockLength===length,'Actual preview chosen block length');
    if(Object.hasOwn(r,'capCount'))insist(r.capCount===capCount,'Actual executed cap-rule count');
    equalBounds(r.rewardBounds,expectedReward.lo,expectedReward.hi,'Current earned reward only');
    sumLow=sumLow.add(expectedReward.lo);sumHigh=sumHigh.add(expectedReward.hi);
    const targetTotal=rat(F).mul(BigInt(i+1)),prefixLow=sumLow.sub(targetTotal),prefixHigh=sumHigh.sub(targetTotal);
    equalBounds(r.cumulativePrefixExcessBounds,prefixLow,prefixHigh,'Every executed reward contributes to current cumulative excess');
    const lower=startup?rat(cstarLower).sub(F).mul(BigInt(i+1)):B.add(endpoint.cmp(0n)<0?endpoint:0n);
    assertRationalEqual(r.certifiedPrefixLowerBoundExact,lower,'Correct concavity/floor proof lower bound');
    insist(lower.cmp(0n)>=0,'Nonnegative all-prefix certificate');
    assertRationalEqual(r.boundaryCreditBeforeExact,B,'Boundary credit before execution');
    const completed=!startup&&age+1===length;
    insist(r.completedBlock===completed,'Block completes after actual final reward');
    if(completed){B=B.add(endpoint);block++;}
    assertRationalEqual(r.boundaryCreditAfterExact,B,'Boundary credit changes only at block completion');
    insist(r.scope==='Bounded upper-envelope illustration; not learned/human behavior or limiting-rate estimate','Limited preview scope');
    if(kind==='finite')insist(prefixLow.cmp(0n)>=0,'Every exact finite illustrated activation prefix');
    previous=expectedPrice;age=completed?0:age+1;
  }
}

function local(name){const p=path.resolve(ROOT,name);insist(p===ROOT||p.startsWith(ROOT+path.sep),'Workspace-contained evidence path');return p;}
function read(name){return JSON.parse(fs.readFileSync(local(name),'utf8').replace(/^\uFEFF/,''));}
function hash(name){
  const fd=fs.openSync(local(name),'r'),h=crypto.createHash('sha256'),buffer=Buffer.allocUnsafe(2*1024*1024);
  try{let n;while((n=fs.readSync(fd,buffer,0,buffer.length,null))>0)h.update(buffer.subarray(0,n));}finally{fs.closeSync(fd);}
  return h.digest('hex');
}
function same(a,b,label){assert.deepEqual(a,b,label);}
function originalBounds(raw){return {lo:exactDecimal(raw.lower),hi:exactDecimal(raw.upper)};}

function verifyManifestTree(name,known=new Map(),visited=new Set()){
  if(visited.has(name))return known;visited.add(name);const m=read(name);
  for(const group of ['sourceHashes','inputHashes'])for(const [file,sha]of Object.entries(m[group]||{})){
    insist(!known.has(file)||known.get(file)===sha,'Consistent inherited dependency hash '+file);known.set(file,sha);
    insist(hash(file)===sha,'Live inherited dependency '+file);
    if(path.basename(file)==='manifest.json')verifyManifestTree(file,known,visited);
  }
  return known;
}

function verifyOldAudit(folder,file,auditor){
  const prefix='research/'+folder+'/',a=read(prefix+file);
  insist(a.passed===true&&a.studyManifestHash===hash(prefix+'manifest.json')&&a.auditorSourceHash===hash(auditor),'Accepted old independent-audit binding');
  insist(a.corruptionNegativeControls&&Object.keys(a.corruptionNegativeControls).length>0&&Object.values(a.corruptionNegativeControls).every(x=>x===true),'Old negative controls retained');
  for(const [field,name]of [['resultsSha256','results.json'],['indexSha256','index.json']])if(a[field]!==undefined)insist(a[field]===hash(prefix+name),'Old audited output identity');
  verifyManifestTree(prefix+'manifest.json');return a;
}

function oldPremiseGate(){
  verifyOldAudit('sparse-display-results','independent-audit.json','research/audit-sparse-display.js');
  verifyOldAudit('sparse-display-results','rational-audit.json','research/audit-sparse-reset.py');
  verifyOldAudit('recurring-results','independent-audit.json','research/audit-sparse-reset.py');
  verifyOldAudit('continuous-results','independent-audit.json','research/audit-continuous-study.py');
  verifyOldAudit('handover-init-results','independent-audit.json','research/audit-handover-init.js');
  const receipt=read('output/adaptive-package-verification.json');
  insist(receipt.verification.passed===true&&receipt.verification.payloadHashesAndCRC===true,'Accepted V9 delivery receipt');
  if(fs.existsSync(local(receipt.archive)))insist(hash(receipt.archive)===receipt.sha256,'Available V9 archive identity');
  return receipt;
}

function continuousComponent(bridge,plan,periods){
  const entry=bridge.records[plan.id],guard=`research/cycle-results/cases/${plan.scenario}-guard.json`;
  insist(entry&&entry.closedFile===plan.continuousFile&&entry.closedSha256===hash(plan.continuousFile)&&entry.guardFile===guard&&entry.guardSha256===hash(guard),'Continuous bridge bound to actual orbit/guard bytes');
  same(entry.periods,periods,'All queried sums computed by continuous component');
  const result=entry.result;
  insist(result.passed===true&&result.scalarRootCertificates===128&&result.orbitTerms===64&&result.inheritedPremiseRevalidation===false,'Precise continuous helper scope');
  return result;
}

function checkSumProvenance(saved,K,{closed=null,source=null}={}){
  const p=saved.provenance;
  if(closed===null){same(p,{method:'Exact cap-start orbit plus constant fixed-point tail',length:K},'Finite sum provenance');return;}
  const inherited=closed.periodEvaluations.find(r=>r.period===K);
  if(inherited){same(p,{source:source+'#period/'+K,originalInterval:inherited.cycleSumConsumerSurplus},'Cached old sum source and original enclosure');}
  else{
    insist(p.method==='Accepted80-digit64-prefix contraction tail'&&p.source===source&&p.length===K,'New bounded tail sum provenance');
    const b=scientificBounds(saved),raw=p.originalInterval;
    insist(exactDecimal(raw.lower).eq(b.lo)&&exactDecimal(raw.upper).eq(b.hi)&&exactDecimal(raw.width).cmp(b.hi.sub(b.lo))>=0,'Original interval strings and honest width');
  }
}

function verifyIdentity(target,plan,original,closed,duplicate){
  insist(target.id===plan.id+'--'+original.label&&target.label===original.label&&target.scenario===plan.scenario&&target.kind===plan.kind,'Every planned target identity');
  insist(target.duplicateOf===duplicate,'Duplicate target provenance retained');
  const identity={finiteSource:plan.finiteFile,requestedExact:exactDouble(original.requestedTarget).toJSON(),
    actualThresholdExact:exactDouble(original.actualGuaranteedThreshold).toJSON(),numericalMarginImportedExact:exactDouble(original.numericalMargin).toJSON()};
  if(closed){const old=closed.comparisons.filter(r=>r.label===original.label);insist(old.length===1,'Unique closed continuous target');
    same(rat(old[0].actualThresholdImported).toJSON(),identity.actualThresholdExact,'Same old continuous absolute target');
    same(rat(old[0].requestedImported).toJSON(),identity.requestedExact,'Same requested target');
    identity.continuousSource=plan.continuousFile;identity.closedTarget=old[0];}
  same(target.identity,identity,'Complete cap/target source metadata');
}

function verifyFiniteEnvelopeSummary(summary,raw,env){
  insist(summary.kind==='finite'&&summary.capIndex===raw.finite.capIndex&&summary.limitIndex===env.indices.at(-1),'Cap-start limit identity');
  same(summary.upperOrbitIndices,env.indices,'Independent entire cap-start upper orbit');
  assertRationalEqual(summary.capPriceExact,exactDouble(raw.cap.price),'Exact physical cap price');
  equalBounds(summary.r0,env.r0,env.r0,'Finite first earned reward');
  equalBounds(summary.Cstar,env.cstar,env.cstar,'Finite cap-start limiting reward, not global old-history floor');
  insist(summary.scope==='Cap-start upper-orbit limit; not arbitrary old guard cycles','No substituted global floor');
}

function scientificNegativeControls(fixture,finiteFixture){
  const {target,context,preview,identityContext}=fixture;
  const mutations={
    changedTarget:r=>r.actualThresholdExact=rat(context.F).add(1n).toJSON(),
    forbiddenQuery:r=>r.frontier.queryLengths.push(MAX_K+1),
    missingDuplicate:r=>r.duplicateOf='not-the-declared-target-group',
    missingLabel:r=>r.label='omitted-planned-label',
  },controls={};
  if(target.calendar.blockPreview64.length){Object.assign(mutations,{
    clock:r=>r.calendar.blockPreview64[0].startExecution++,
    tieOrGap:r=>r.calendar.blockPreview64[0].length++,
    credit:r=>r.calendar.blockPreview64[0].boundaryCreditAfterExact=rat(-1n).toJSON(),
  });}
  if(target.executionPreview.length){Object.assign(mutations,{
    partialGapReward:r=>r.executionPreview[0].cumulativePrefixExcessBounds.lowerExact=rat(-1n).toJSON(),
    carriedHistory:r=>r.executionPreview[1].previousExecutedPrice=null,
  });}
  if(target.rates){Object.assign(mutations,{
    wrongRateDirection:r=>{const b=r.rates.optimumRateBoundsExact;r.rates.optimumRateBoundsExact={lower:rat(b.upper).add(1n).toJSON(),upper:b.lower};},
    falseOptimum:r=>r.rates.exactOptimum=!r.rates.exactOptimum,
  });if(target.rates.absoluteSavingSigns)mutations.falseSavingSign=r=>r.rates.absoluteSavingSigns.lower='arbitrary';}
  for(const [name,mutate]of Object.entries(mutations)){
    const changed=structuredClone(target);mutate(changed);let rejected=false;
    try{verifyPrimaryTarget(changed,context);verifyPrimaryPreview(changed,preview);verifyIdentity(changed,identityContext.plan,identityContext.old,identityContext.closed,identityContext.duplicate);}catch{rejected=true;}
    insist(rejected,'Scientific negative control rejected '+name);controls[name]=true;
  }
  if(finiteFixture){
    for(const [name,mutate]of Object.entries({changedCap:s=>s.capPriceExact=rat(s.capPriceExact).add(1n).toJSON(),
      substitutedGlobalFloor:s=>s.Cstar.lowerExact=rat(s.Cstar.lowerExact).sub(1n).toJSON()})){
      const changed=structuredClone(finiteFixture.summary);mutate(changed);let rejected=false;
      try{verifyFiniteEnvelopeSummary(changed,finiteFixture.raw,finiteFixture.env);}catch{rejected=true;}
      insist(rejected,'Scientific model corruption rejected '+name);controls[name]=true;
    }
  }
  return controls;
}

function verifyFailureTarget(t,plan,old,closed,duplicate){
  insist(t.id===plan.id+'--'+old.label&&t.label===old.label&&t.kind===plan.kind&&t.scenario===plan.scenario&&typeof t.error==='string'&&typeof t.errorType==='string'&&t.rates===null,'Honest retained target failure');
  verifyPrimaryCalendar(t.calendar);insist(t.executionPreview.length===0,'No failed-row illustration');
  const f=t.frontier;
  insist(f.maxK===MAX_K&&f.bestFixedK===null&&f.certifiedSafeK===null&&f.safe===null&&f.failing===null&&Array.isArray(f.queryLengths)&&f.queryLengths.every(k=>Number.isInteger(k)&&k>=1&&k<=MAX_K),'Retained failed-query chronology without a successful frontier');
  if(t.actualThresholdExact!==null){assertRationalEqual(t.actualThresholdExact,exactDouble(old.actualGuaranteedThreshold),'Known threshold retained on calculation failure');verifyIdentity(t,plan,old,closed,duplicate);}
  else insist(t.identity===null&&t.duplicateOf===null,'Unknown pre-case identity is not invented');
}

export function auditMixedTiming(directory='research/mixed-timing-results',{continuousBridge=null}={}){
  CHECKS=0;const begun=Date.now(),prefix=path.relative(ROOT,local(directory)).replaceAll('\\','/')+'/';
  const manifest=read(prefix+'manifest.json'),results=read(prefix+'results.json'),index=read(prefix+'index.json'),completion=read(prefix+'completion.json'),start=read(prefix+'execution-start.json');
  const mh=hash(prefix+'manifest.json');
  insist(continuousBridge&&continuousBridge.studyManifestHash===mh&&continuousBridge.resultsSha256===hash(prefix+'results.json')&&continuousBridge.inheritedResultsSha256===hash('research/continuous-results/results.json'),'Fresh Python-orchestrator bridge bound to primary and inherited actual bytes');
  insist(continuousBridge.continuousAuditorSourceHash===hash('research/audit-mixed-continuous.py')&&continuousBridge.arithmeticBackendHash===hash('research/audit-continuous-study.py')&&continuousBridge.orchestratorSourceHash===hash('research/audit-mixed-study.py'),'Continuous bridge source identities');
  for(const group of ['sourceHashes','inputHashes'])for(const [file,sha]of Object.entries(manifest[group])){
    insist(hash(file)===sha,'Frozen new dependency '+file);
    if(group==='sourceHashes')insist(hash(prefix+'sources/'+file)===sha,'Exact new source snapshot '+file);
  }
  const auditorFiles=['research/audit-mixed-timing.js','research/audit-mixed-continuous.py','research/audit-mixed-study.py','tests/mixed-timing-audit.test.js','tests/test_mixed_continuous_audit.py','tests/test_mixed_timing_cross_audit.py','tests/test_mixed_audit_driver.py'];
  for(const file of auditorFiles)insist(manifest.sourceHashes[file]===hash(file),'Independent auditor/test frozen before cases '+file);
  const delivery=oldPremiseGate();
  insist(manifest.v9Delivery.archiveSha256===delivery.sha256&&manifest.v9Delivery.receiptSha256===hash('output/adaptive-package-verification.json'),'Same accepted V9 receipt identity');
  const plans=SCENARIOS.flatMap(sid=>KINDS.map(kind=>({id:sid+'--'+kind,scenario:sid,kind,labels:[...LABELS],finiteFile:`research/sparse-display-results/cases/${sid}.json`,continuousFile:kind==='finite'?null:`research/recurring-results/records/${sid}-${kind}.json`})));
  same(manifest.plan.models,plans,'Independent complete24-model120-label matrix');
  insist(manifest.plan.modelCount===24&&manifest.plan.targetLabels===120&&manifest.plan.maxK===MAX_K&&manifest.plan.displayPrecision===30&&manifest.plan.blockPreviewLimit===64&&manifest.plan.finiteExecutionPreviewLimit===256&&manifest.plan.continuousExecutionPreviewLimit===64,'All frozen numerical limits');
  same(manifest.plan.softResourceTargets,{seconds:1800,observedRSSBytes:250000000,newOutputBytes:50000000},'Prospective resource targets');
  insist(results.manifestSha256===mh&&index.manifestSha256===mh&&start.manifestSha256===mh&&completion.manifestSha256===mh,'Every output bound to manifest');
  insist(results.records.length===24&&index.records.length===24,'All model records retained');
  insist(completion.resultsSha256===hash(prefix+'results.json')&&completion.indexSha256===hash(prefix+'index.json')&&completion.finalFrozenDependencyCheck.passed===true,'Final output/dependency binding');
  const journal=fs.readFileSync(local(prefix+'journal.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
  insist(journal.length===48,'All24 started and finished journals');
  const globalContinuum=read('research/continuous-results/results.json').records;
  const details=[],statusCounts={},seenIDs=new Set();let fixture=null,finiteFixture=null,failureFixture=null,labels=0,failures=0,totalQueries=0,scalarRoots=0;
  for(let i=0;i<plans.length;i++){
    const plan=plans[i],r=results.records[i],ix=index.records[i];
    insist(r.id===plan.id&&r.scenario===plan.scenario&&r.kind===plan.kind&&r.finiteFile===plan.finiteFile&&r.continuousFile===plan.continuousFile,'Model plan/source identity');same(r.labels,LABELS,'Model labels in frozen order');
    insist(ix.id===plan.id&&ix.file==='records/'+plan.id+'.json'&&ix.sha256===hash(prefix+ix.file)&&ix.status===r.status&&ix.targetLabels===5,'Indexed model identity/hash/status');
    same(read(prefix+ix.file),r,'Journal record and aggregate byte-decoded identity');
    insist(journal[2*i].id===plan.id&&journal[2*i].status==='started'&&journal[2*i+1].id===plan.id&&journal[2*i+1].status===r.status&&journal[2*i+1].calculationFailures===r.calculationFailures,'Per-model execution chronology');
    insist(Array.isArray(r.targets)&&r.targets.length===5&&Number.isInteger(r.calculationFailures)&&r.calculationFailures>=0&&r.calculationFailures<=5,'Every planned target slot retained');
    const raw=read(plan.finiteFile),original=raw.originalTargets;
    insist(raw.scenario.id===plan.scenario&&raw.cap.index===raw.finite.capIndex&&raw.cap.price===raw.finite.prices[raw.finite.capIndex],'Inherited physical cap identity');
    same(original.map(t=>t.label),LABELS,'Five inherited target labels in source order');
    let env,r0,cstar,closed=null,helper=null,callbacks;
    const querySet=[...new Set(r.targets.flatMap(t=>t.frontier.queryLengths))].sort((a,b)=>a-b);
    same(r.queriedSums.map(s=>s.period),querySet,'All and only queried sums retained');totalQueries+=querySet.length;
    insist(Array.isArray(r.queryFailures)&&r.queryFailures.every(q=>querySet.includes(q.period)&&typeof q.error==='string'&&typeof q.errorType==='string'),'Retained bounded query failures');
    if(r.envelope!==null){
      if(plan.kind==='finite'){
        env=verifyFiniteEconomics(raw).envelope;r0={lo:env.r0,hi:env.r0};cstar={lo:env.cstar,hi:env.cstar};
        verifyFiniteEnvelopeSummary(r.envelope,raw,env);finiteFixture??={summary:r.envelope,raw,env};
        callbacks={reward:age=>({lo:env.reward(age),hi:env.reward(age)}),price:age=>{const at=env.indices[Math.min(age,env.indices.length-1)];return {index:at,priceExact:exactDouble(raw.finite.prices[at]).toJSON()};}};
      }else{
        closed=read(plan.continuousFile);
        insist(closed.scenario===plan.scenario&&closed.continuum===plan.kind&&closed.status==='certified recurring-cap enclosures','Inherited continuous model identity');
        assertRationalEqual(closed.physicalCap.physicalPriceImported,exactDouble(raw.cap.price),'Same continuous physical cap');
        const inherited=globalContinuum.filter(x=>x.scenario===plan.scenario&&x.continuum===plan.kind);insist(inherited.length===1&&inherited[0].status==='certified theorem and enclosures'&&inherited[0].assumptions.eligible===true,'Accepted inherited global premises');
        for(const [key,value]of Object.entries(raw.scenario.economy))if(key!=='id')assertRationalEqual(closed.importedBinary64[key],exactDouble(value),'Same imported economy '+key);
        same(closed.inheritedContinuum,{qstar:inherited[0].worst.normalizedPrice,consumerSurplus:inherited[0].worst.consumerSurplus,rho:inherited[0].assumptions.rho,nash:inherited[0].nash,rounding:inherited[0].rounding},'Hash-bound old global theorem enclosures');
        helper=continuousComponent(continuousBridge,plan,r.queriedSums.filter(x=>x.sumBounds!==null).map(x=>x.period));scalarRoots+=128;
        r0=originalBounds(closed.orbit[0].consumerSurplus);cstar=originalBounds(closed.inheritedContinuum.consumerSurplus);
        insist(r.envelope.kind===plan.kind&&r.envelope.source===plan.continuousFile&&r.envelope.scope==='Accepted continuous cap-start attained envelope; prices/rewards remain enclosures','Continuous envelope interpretation');
        same(r.envelope.physicalCap,closed.physicalCap,'Continuous cap provenance unchanged');
        callbacks={reward:age=>originalBounds(closed.orbit[age].consumerSurplus),price:age=>({priceEnclosure:closed.orbit[age].executedPrice})};
      }
      equalBounds(r.envelope.r0,r0.lo,r0.hi,'Envelope first earned reward');equalBounds(r.envelope.Cstar,cstar.lo,cstar.hi,'Cap-start limiting reward');
      if(closed){same(r.envelope.r0.provenance,{source:plan.continuousFile+'#orbit/0',originalInterval:closed.orbit[0].consumerSurplus},'Original first-reward enclosure provenance');
        same(r.envelope.Cstar.provenance,{source:plan.continuousFile+'#inheritedContinuum',originalInterval:closed.inheritedContinuum.consumerSurplus},'Original limiting-reward provenance');}
      else insist(r.envelope.r0.provenance===null&&r.envelope.Cstar.provenance===null,'Exact finite envelope has no invented interval source');
      for(const s of r.queriedSums){
        if(s.sumBounds===null){insist(r.queryFailures.some(q=>q.period===s.period)&&r.calculationFailures>0,'Missing query result is an honest retained failure');continue;}
        const bounds=scientificBounds(s.sumBounds);checkSumProvenance(s.sumBounds,s.period,{closed,source:plan.continuousFile});
        if(env){const total=env.sum(s.period);insist(bounds.lo.eq(total)&&bounds.hi.eq(total),'Every exact finite queried sum');}
        else{const independent=helper.sumBounds.find(x=>x.period===s.period);insist(independent&&bounds.lo.cmp(independent.bounds.lower)<=0&&bounds.hi.cmp(independent.bounds.upper)>=0,'Every new continuous queried sum encloses independent calculation');}
      }
    }
    const seen=new Map();let modelFailures=0;
    for(let j=0;j<5;j++){
      const t=r.targets[j],old=original[j],F=exactDouble(old.actualGuaranteedThreshold),key=F.toString();
      insist(!seenIDs.has(t.id),'No duplicated/omitted target slot');seenIDs.add(t.id);labels++;
      const duplicate=seen.get(key)||null;
      if(t.status==='unresolved calculation or identity'){
        verifyFailureTarget(t,plan,old,closed,duplicate);
        failureFixture??={target:t,plan,old,closed,duplicate};
        modelFailures++;
      }else{
        insist(r.envelope!==null,'Available target requires a model envelope');
        verifyIdentity(t,plan,old,closed,duplicate);
        const context={F,r0,cstar,kind:plan.kind,finite:env},preview={F,kind:plan.kind,cstarLower:cstar.lo,...callbacks};
        verifyPrimaryTarget(t,context);verifyPrimaryPreview(t,preview);
        for(const field of ['safe','failing'])if(t.frontier[field]){
          const stored=t.frontier[field],s=r.queriedSums.find(q=>q.period===stored.period);same(stored.sumBounds,s.sumBounds,'Frontier copies independently checked queried sum');
        }
        if(fixture===null||(fixture.target.calendar.kind!=='funded-mixed'&&t.calendar.kind==='funded-mixed'))fixture={target:t,context,preview,identityContext:{plan,old,closed,duplicate}};
      }
      if(t.actualThresholdExact!==null&&!seen.has(key))seen.set(key,t.id);
      statusCounts[t.status]=(statusCounts[t.status]||0)+1;
    }
    insist(modelFailures===r.calculationFailures,'Every target failure counted');failures+=modelFailures;
    insist(r.status===(modelFailures===0?'completed timing certificate calculations':r.envelope===null?'unresolved model identity':'retained target calculation failures'),'Honest model completion status');
    insist(Number.isFinite(r.seconds)&&r.seconds>=0,'Reported model runtime available');
    details.push({id:plan.id,kind:plan.kind,labels:5,queriedSums:querySet.length,scalarRootCertificates:helper?128:0,calculationFailures:modelFailures,statuses:r.targets.map(t=>t.status)});
  }
  insist(labels===120&&completion.models===24&&completion.targetLabels===120&&completion.calculationFailures===failures,'Complete primary inventory');
  insist(completion.passed===(failures===0),'Primary execution success separate from scientific unresolved statuses');
  const resources=completion.resources;insist(resources.experimentalModelApiCalls===0&&resources.newTrainingRounds===0,'No new API/model/learning runs');
  same(resources.rssSamples.map(x=>x.id),plans.map(x=>x.id),'Every model resource sample retained');
  const samples=resources.rssSamples.map(x=>x.rssBytes).filter(x=>x!==null);
  insist(samples.every(x=>Number.isFinite(x)&&x>0)&&resources.largestObservedRSSBytes===(samples.length?Math.max(...samples):null),'Sampled RSS maximum is honest');
  insist(Number.isFinite(resources.seconds)&&resources.seconds>=0&&resources.softTargetExceeded.seconds===(resources.seconds>1800)&&resources.softTargetExceeded.observedRSS===(samples.length?Math.max(...samples)>250000000:null),'Reported runtime/memory soft-target flags');
  const primaryFiles=['manifest.json','execution-start.json','journal.jsonl','results.json','index.json',...index.records.map(x=>x.file),...Object.keys(manifest.sourceHashes).map(x=>'sources/'+x)];
  const bytes=primaryFiles.reduce((s,f)=>s+fs.statSync(local(prefix+f)).size,0);
  insist(resources.newOutputBytesBeforeCompletion===bytes&&resources.softTargetExceeded.outputBytes===(bytes>50000000),'Primary-only output size and overrun flag');
  let corruptionNegativeControls;
  if(fixture!==null)corruptionNegativeControls=scientificNegativeControls(fixture,finiteFixture);
  else{
    insist(failureFixture!==null,'An actual retained row supplies negative controls');
    corruptionNegativeControls={};
    for(const [name,mutate]of Object.entries({fabricatedRate:r=>r.rates={},omittedFailure:r=>delete r.error,wrongFailedSlot:r=>r.id+='-omitted'})){
      const x=structuredClone(failureFixture.target);mutate(x);let rejected=false;
      try{verifyFailureTarget(x,failureFixture.plan,failureFixture.old,failureFixture.closed,failureFixture.duplicate);}catch{rejected=true;}
      insist(rejected,'Scientific failure-retention corruption '+name);corruptionNegativeControls[name]=true;
    }
  }
  same(Object.keys(continuousBridge.records).sort(),details.filter(x=>x.scalarRootCertificates>0).map(x=>x.id).sort(),'Only all required continuous components present');
  return {passed:false,componentPassed:true,requiresOrchestrator:true,completedAt:new Date().toISOString(),studyManifestHash:mh,resultsSha256:hash(prefix+'results.json'),indexSha256:hash(prefix+'index.json'),completionSha256:hash(prefix+'completion.json'),journalSha256:hash(prefix+'journal.jsonl'),executionStartSha256:hash(prefix+'execution-start.json'),
    auditorSourceHash:hash('research/audit-mixed-timing.js'),continuousAuditorSourceHash:hash('research/audit-mixed-continuous.py'),arithmeticBackendHash:hash('research/audit-continuous-study.py'),
    checks:CHECKS,models:24,finiteModels:8,continuousModels:16,targetLabels:labels,finiteTargetLabels:40,continuousTargetLabels:80,queriedSums:totalQueries,scalarRootCertificates:scalarRoots,calculationFailures:failures,primaryExecutionPassed:completion.passed,
    statusCounts,corruptionNegativeControls,details,seconds:(Date.now()-begun)/1000,
    inheritedPremiseRevalidation:false,inheritedPremiseScope:'Accepted immutable global monotonicity/contraction and q_star/C_star/rho certificates reused through verified live manifest/audit/output/source hashes; not independently recomputed in this stage. Legacy administrative oldCheckpointHashes are historical references, not new timing-model inputs, and are not recursively expanded',
    scope:'Separate JS BigInt finite/control arithmetic and complete scientific-field/clock/credit/preview audit; separate130-digit code checks128 scalar-root signs/model,64 orbit propagation rows/model and every queried continuous contraction-tail sum. Shared JS Math for numerical-game payoffs and shared Python Decimal backend disclosed. No formal verification or new learning experiment.'};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const args=process.argv.slice(2);insist(args[0]==='--internal-continuous-bridge','Run authoritative Python audit-mixed-study.py; JS alone cannot certify the continuous component');
  const bridge=JSON.parse(fs.readFileSync(0,'utf8'));
  const result=auditMixedTiming(args[1]||'research/mixed-timing-results',{continuousBridge:bridge});
  console.log(JSON.stringify(result));
}
