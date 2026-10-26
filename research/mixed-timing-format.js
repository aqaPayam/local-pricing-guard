// Exact presentation arithmetic only. This module reads no evidence.
const need=(ok,message)=>{if(!ok)throw Error(message);};
const integer=/^-?(0|[1-9][0-9]*)$/;
export function rational(value){
 need(value&&typeof value.numerator==='string'&&typeof value.denominator==='string'&&integer.test(value.numerator)&&integer.test(value.denominator),'Malformed exact rational');
 const n=BigInt(value.numerator),d=BigInt(value.denominator);need(d>0n,'Positive rational denominator required');return {n,d};
}
export function rationalSign(value){const {n}=rational(value);return n<0n?'negative':n>0n?'positive':'zero';}
export function equalRational(a,b){a=rational(a);b=rational(b);return a.n*b.d===b.n*a.d;}

// Outward six-significant-digit display conveniences. Exact primary values
// and their original 30-digit outward displays remain unchanged elsewhere.
export function scientificDisplay(value,digits=6){
 need(Number.isInteger(digits)&&digits>=1&&digits<=30,'Display precision outside1..30');
 const raw=rational(value),negative=raw.n<0n,n=negative?-raw.n:raw.n,d=raw.d;
 if(n===0n)return {lower:'0',upper:'0',sign:'zero',significantDigits:digits};
 let exponent=n.toString().length-d.toString().length;
 if(exponent>=0?n<d*10n**BigInt(exponent):n*10n**BigInt(-exponent)<d)exponent--;
 const shift=digits-1-exponent;
 const numerator=shift>=0?n*10n**BigInt(shift):n;
 const denominator=shift>=0?d:d*10n**BigInt(-shift);
 const low=numerator/denominator,high=low+(numerator%denominator===0n?0n:1n);
 function render(coefficient,sign){
  let e=exponent,chars=coefficient.toString();
  if(chars.length>digits){e++;chars=chars.slice(0,digits);}
  const mantissa=chars.length===1?chars:chars[0]+'.'+chars.slice(1);
  return sign+mantissa+'e'+(e>=0?'+':'')+e;
 }
 return {lower:negative?render(high,'-'):render(low,''),upper:negative?render(low,'-'):render(high,''),sign:negative?'negative':'positive',significantDigits:digits};
}

export function constructedCalendarTiming(calendar,previewLength=0){
 const result={initialShortBlocks:null,firstLongBlock:null,firstLongExecution:null,
  withinExecutionPreview:null,reason:null,
  scope:'Exact timing of the constructed lower-credit calendar; not a limiting-frequency estimate or unknown continuous-optimum calendar'};
 if(calendar?.kind!=='funded-mixed')return {...result,reason:calendar?.kind==='startup-only'?'One actual startup cap; no repeating mixed calendar':calendar?.kind==='fixed-safe'?'Fixed-safe fallback has no long gap':'No available mixed calendar'};
 const a=rational(calendar.creditAExact),b=rational(calendar.creditBExact),K=calendar.K;
 need(a.n>=0n&&b.n<0n&&Number.isInteger(K)&&K>=1&&K<65536,'Invalid mixed calendar credits/gap');
 if(a.n===0n)return {...result,reason:'Zero short-block credit; the calendar never chooses a long gap'};
 const num=(-b.n)*a.d,den=b.d*a.n,n=(num+den-1n)/den;
 const block=n+1n,execution=n*BigInt(K)+1n;
 need((n-1n)*den<num&&num<=n*den,'First-long threshold inequalities failed');
 return {...result,initialShortBlocks:String(n),firstLongBlock:String(block),firstLongExecution:String(execution),
  withinExecutionPreview:execution<=BigInt(previewLength),reason:'First boundary with exact accumulated short credit at least the funded long-gap debt'};
}

export function statusCategory(target){
 const status=target?.status;
 need(typeof status==='string','Primary status string missing');
 if(status==='certified startup-only zero limiting rate')return 'startup-only';
 if(status==='certified exact equality frontier; zero mixed saving')return 'exact-zero-saving';
 if(status==='certified exact mixed optimum')return 'exact-optimum';
 if(status==='certified continuous optimum enclosure')return 'continuous-enclosure';
 if(status==='infeasible cap-first two-mode family')return 'infeasible';
 if(status==='censored safe ceiling')return 'censored';
 if(status==='unresolved calculation or identity')return 'calculation-or-identity-failure';
 if(status==='unresolved certified frontier bracket'||status==='unresolved cap/target boundary; no certified schedule')return 'unresolved';
 throw Error('Unrecognized retained primary status '+status);
}
