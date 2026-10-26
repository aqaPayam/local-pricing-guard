import test from 'node:test';import assert from 'node:assert/strict';
import {structuralBound} from '../research/cycle-structure.js';
import {solveGraph} from '../research/cycle-game.js';
function synthetic(sets) {
 const n=sets.length,rewards=Array.from({length:n*n},(_,state)=>({prices:[Math.floor(state/n),state%n],consumerSurplus:20-Math.floor(state/n)-state%n})),
 adjacency=rewards.map((_,s)=>sets[s%n].flatMap(a=>sets[Math.floor(s/n)].map(b=>a*n+b))),
 result=solveGraph(adjacency,adjacency.map(row=>row.map(v=>rewards[v].consumerSurplus)));
 result.universalWitness={consumerSurplus:result.universal.upperBound};return {game:{n,sets,rewards,adjacency},result};
}
test('finite deficit excludes initial previous reward and includes future acyclic states',()=>{
 const {game,result}=synthetic([[0],[0],[0,1]]),r=structuralBound(game,result,[1,2,20]);
 assert.equal(r.applicable,true);assert.equal(r.largestSelfFeasibleIndex,0);
 assert.ok(Math.abs(r.starts[8].totalPositiveDeficitBound-2)<1e-6);
 for(let start=0;start<9;start++) {
  let paths=[{state:start,sum:0}];
  for(let T=1;T<=5;T++) {
   paths=paths.flatMap(p=>game.adjacency[p.state].map(v=>({state:v,sum:p.sum+game.rewards[v].consumerSurplus})));
   for(const p of paths)assert.ok(p.sum/T+1e-10>=r.adjustedFloor-r.starts[start].totalPositiveDeficitBound/T);
  }
 }
});
test('monotone upper assumption is checked rather than inferred from a guard label',()=>{
 const {game,result}=synthetic([[0,1],[0],[0,1,2]]),r=structuralBound(game,result);
 assert.equal(r.applicable,false);assert.equal(r.assumptions.monotoneUpper,false);
});
test('interval assumption is necessary even with monotone endpoints',()=>{
 const {game,result}=synthetic([[0],[0,2],[0,1,2]]),r=structuralBound(game,result);
 assert.equal(r.applicable,false);assert.equal(r.assumptions.intervals,false);
});
