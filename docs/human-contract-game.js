// Human-playable continuous market. No external inference or training.
import {outcome,NASH_PRICE,MONOPOLY_PRICE} from '/local-pricing-guard/replacement-market.js';
import {brInterval,projectQuote} from '/local-pricing-guard/receiver-contract.js';
export function createContractGame({coverage='both',epsilon=.1,rival='high',initial='high',policy=null,rounds=30}={}) {
  if(!['none','A','both'].includes(coverage)||!['high','myopic','learned'].includes(rival)||!['high','competitive'].includes(initial)||!Number.isFinite(epsilon)||epsilon<0||!Number.isInteger(rounds)||rounds<1||rounds>100)throw Error('Invalid game setup');
  if(rival==='learned'&&(!policy||!Array.isArray(policy.prices)||policy.prices.length<2||policy.prices.some(p=>!Number.isFinite(p)||p<0||p>3)||!Array.isArray(policy.greedy)||policy.greedy.length<policy.prices.length**2||policy.greedy.some(i=>!Number.isInteger(i)||i<0||i>=policy.prices.length)))throw Error('Valid saved learned policy required');
  let previous=Array(2).fill(initial==='high'?MONOPOLY_PRICE:NASH_PRICE),rows=[];
  const nearest=p=>policy.prices.reduce((best,v,i)=>Math.abs(v-p)<Math.abs(policy.prices[best]-p)?i:best,0);
  const interval=()=>coverage==='none'?{lower:0,upper:3}:brInterval(previous[1],{epsilon});
  function observe(){return {round:rows.length+1,rounds,done:rows.length===rounds,previous:previous.slice(),interval:interval(),rows:structuredClone(rows),setup:{coverage,epsilon,rival,initial},totalProfit:rows.reduce((v,r)=>v+r.profits[0],0)};}
  return {observe,commit(proposal){
    if(rows.length===rounds)throw Error('Game finished');
    if(!Number.isFinite(proposal)||proposal<0||proposal>3)throw Error('Choose a price from 0 to 3');
    // Both proposals depend only on completed history, never today's human quote.
    const rivalProposal=rival==='high'?MONOPOLY_PRICE:rival==='myopic'?brInterval(previous[0]).bestPrice:policy.prices[policy.greedy[nearest(previous[1])*policy.prices.length+nearest(previous[0])]];
    const proposals=[proposal,rivalProposal],allowed=proposals.map((p,i)=>(coverage==='both'||coverage==='A'&&i===0)?projectQuote(p,previous[1-i],{epsilon}):{price:p,lower:0,upper:3});
    const result=outcome(allowed.map(v=>v.price));
    const row={round:rows.length+1,previous:previous.slice(),proposals,intervals:allowed.map(({lower,upper})=>({lower,upper})),...result};
    previous=result.prices.slice();rows.push(row);return structuredClone(row);
  }};
}
