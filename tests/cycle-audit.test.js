import test from 'node:test';
import assert from 'node:assert/strict';
import {solveGraph,pricingGame,solvePricing} from '../research/cycle-game.js';
import {auditWeightedGraph,buildIndependentGame,componentsIndependent,verifySingletonLemma} from '../research/audit-cycle-study.js';

test('independent decomposition and certificate audit distinguish reachable negative cycles',()=>{
 const adjacency=[[1],[0],[2],[0]],weights=[[-5],[1],[-7],[-100]],result=solveGraph(adjacency,weights),weight=(u,v)=>weights[u][adjacency[u].indexOf(v)],r=auditWeightedGraph(adjacency,weight,result);
 assert.equal(r.allUpper,-7);assert.equal(result.starts[0].upperBound,-2);assert.equal(result.starts[3].upperBound,-2);assert.deepEqual(componentsIndependent(adjacency).components,[[0,1],[2],[3]]);
});
test('independent certificate pipeline rejects corrupted cycle, weight, bound and prefix',()=>{
 const adjacency=[[1],[0],[2],[0]],weights=[[-5],[1],[-7],[-100]],r=solveGraph(adjacency,weights),weight=(u,v)=>weights[u][adjacency[u].indexOf(v)];
 const badCycle=structuredClone(r);badCycle.certificates[0].cycle=[0,2];assert.throws(()=>auditWeightedGraph(adjacency,weight,badCycle),/feasible cyclic edge/);
 const badWeight=structuredClone(r);badWeight.certificates[0].cycleWeights[0]+=1;assert.throws(()=>auditWeightedGraph(adjacency,weight,badWeight),/witness edge weights/);
 const badBound=structuredClone(r);badBound.certificates[0].lowerBound+=1;assert.throws(()=>auditWeightedGraph(adjacency,weight,badBound),/every-edge dual inequality/);
 const badPrefix=structuredClone(r);badPrefix.starts[3].prefix=[3,2,0];assert.throws(()=>auditWeightedGraph(adjacency,weight,badPrefix),/feasible prefix edge/);
});
test('independent economics reconstruct graph and audit both pricing objectives and shortcut',()=>{
 const scenario={id:'unit-only-cycle-grid3',economy:{quality:2,cost:1,mu:.25,buyers:100,outsideQuality:0},gridSize:3,epsilon:.1};
 for(const type of ['guard','cap','none']){const a=pricingGame(scenario,type),b=buildIndependentGame(scenario,type);assert.deepEqual(a.prices,b.prices);assert.deepEqual(a.sets,b.sets);assert.deepEqual(a.rewards,b.rewards);for(const objective of ['minCS','maxJointProfit']){const result=solvePricing(a,objective),weight=(_,v)=>objective==='minCS'?b.rewards[v].consumerSurplus:-b.rewards[v].jointProfit;auditWeightedGraph(b.adjacency,weight,result);if(objective==='minCS')assert.equal(verifySingletonLemma(b,result).applicable,true);}}
});
