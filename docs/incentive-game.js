// A local one-block human challenge against the PUBLIC upper-price script.
// No optimization is performed here; optional hints are audited stored actions.
import {createGame,rational,add,subtract,fromDouble,fromJSON,exactJSON,compare,approximate} from '/local-pricing-guard/recurring-game.js';
const mul=(a,b)=>rational(a.n*b.n,a.d*b.d);
export function createProfitChallenge(record,certificate){
 const {period:K,focal,discount,optimalBlockProfit,baselineBlockProfit,capAction,phasePolicies=[]}=certificate;
 if(!Number.isInteger(K)||K<1||K>65536||(focal!==0&&focal!==1))throw Error('Invalid challenge identity');
 const gamma=fromJSON(discount),best=fromJSON(optimalBlockProfit),baseline=fromJSON(baselineBlockProfit);
 if(gamma.n<0n||gamma.n>=gamma.d||compare(best,baseline)<0)throw Error('Invalid exact discount/profit certificate');
 const n=record.finite.prices.length,policies=new Map();
 for(const p of phasePolicies){if(!Number.isInteger(p.phase)||p.phase<1||p.phase>=K||p.actions.length!==n*n||policies.has(p.phase))throw Error('Malformed stored policy layer');const actions=Array.from(p.actions);if(actions.some((a,state)=>!Number.isInteger(a)||!record.finite.sets[state%n]?.includes(a)))throw Error('Stored policy action is not permitted at its public state');policies.set(p.phase,actions);}
 if(policies.size!==K-1||!Number.isInteger(capAction)||capAction<0||capAction>record.finite.capIndex)throw Error('Incomplete stored strategy');
 const core=createGame(record,K),history=[];let discounted=rational(0n),factor=rational(1n),ledger=[];
 const done=()=>core.snapshot().executions===K;
 const allowed=()=>done()?[]:core.allowed(focal);
 function opponentQuote(){if(done())return null;return Math.max(...core.allowed(1-focal));}
 function preview(own){if(done())return {legal:false,reason:'The block is complete. Undo or restart to try another choice.'};const other=opponentQuote();return focal===0?core.preview(own,other):core.preview(other,own);}
 function hint(){
  if(done())return null;const state=core.snapshot(),action=state.phase===0?capAction:policies.get(state.phase)[state.previousIndices[focal]*n+state.previousIndices[1-focal]];
  if(!allowed().includes(action))throw Error('Stored hint is not permitted at this public state');return action;
 }
 function snapshot(){const game=core.snapshot(),complete=game.executions===K,gap=complete?subtract(best,discounted):null,vsBaseline=complete?subtract(discounted,baseline):null;
  if(gap&&gap.n<0n)throw Error('Played block exceeds its certificate; evidence is inconsistent');
  return {game,period:K,focal,discount:exactJSON(gamma),complete,remaining:K-game.executions,
   discountedProfit:{value:approximate(discounted),exact:exactJSON(discounted)},
   bestCompleteBlock:{value:approximate(best),exact:exactJSON(best)},
   baselineCompleteBlock:{value:approximate(baseline),exact:exactJSON(baseline)},
   shortfall:gap?{value:approximate(gap),exact:exactJSON(gap),matched:gap.n===0n}:null,
   versusBaseline:vsBaseline?{value:approximate(vsBaseline),exact:exactJSON(vsBaseline),sign:vsBaseline.n>0n?'positive':vsBaseline.n<0n?'negative':'zero'}:null,
   opponent:complete?null:{index:opponentQuote(),price:record.finite.prices[opponentQuote()],scope:'Public deterministic maximum-permitted-price script; no learning/model player'},
   ledger:ledger.slice(),canUndo:history.length>0,scope:'One actual cap-first block. Earlier profit receives the declared exact discount; compare only complete matching blocks. Finite saved-weight game, separate from continuous analysis.'};
 }
 function execute(own){const reward=preview(own);if(!reward.legal)throw Error(reward.reason||'Choose a permitted quote');const weighted=mul(factor,fromDouble(reward.profits[focal])),nextDiscounted=add(discounted,weighted);if(core.snapshot().executions+1===K&&compare(nextDiscounted,best)>0)throw Error('Played block exceeds its certificate; evidence is inconsistent');const before={discounted,factor,ledger};core.execute(...reward.indices);history.push(before);discounted=nextDiscounted;ledger=[...ledger,{execution:ledger.length+1,ownIndex:own,opponentIndex:reward.indices[1-focal],...reward,focalProfit:reward.profits[focal],discountWeight:exactJSON(factor),discountedProfit:exactJSON(weighted)}];factor=mul(factor,gamma);return snapshot();}
 return {allowed,opponentQuote,preview,hint,execute,snapshot,undo(){if(history.length){const previous=history.pop();core.undo();discounted=previous.discounted;factor=previous.factor;ledger=previous.ledger;}return snapshot();},reset(){core.reset();history.length=0;discounted=rational(0n);factor=rational(1n);ledger=[];return snapshot();}};
}
