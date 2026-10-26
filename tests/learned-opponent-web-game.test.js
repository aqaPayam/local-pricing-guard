import test from 'node:test';import assert from 'node:assert/strict';
import {checkpointGameData,responseGamePolicy} from '../research/learned-opponent-web-game.js';
function fixture(){
 const finite={prices:[1,2,3],capIndex:1,sets:[[0,1],[1,2],[0,2]]},control={id:'selected95',period:4,phases:4},rows=36,offsets=[0];
 for(let row=0;row<rows;row++)offsets.push(offsets.at(-1)+2);
 const greedyOwn=[[],[]];for(let row=0;row<rows;row++){const phase=Math.floor(row/9),support=phase===0?[0,1]:finite.sets[row%3];greedyOwn[0].push(support[Math.floor(row/3)%2]);greedyOwn[1].push(support[(Math.floor(row/3)+1)%2]);}
 const counts=[Array(72).fill(0),Array(72).fill(0)];counts[0][0]=65535;counts[1][1]=65535;
 return {id:'artificial-checkpoint',seed:1,finite,control,terminal:{phase:0,previousIndices:[2,1]},greedyOwn,counts,overflow:[[[0,70000]],[[1,70000]]],source:{scope:'Artificial only'}};
}
test('original greedy B maps once into world order while full exact counts retain own-coordinate offsets',()=>{
 const f=fixture(),before=structuredClone(f),view=checkpointGameData(f,{expectedRounds:70000});assert.deepEqual(f,before);assert.equal(view.originalWorldPolicies.A.length,36);assert.equal(view.trainingCounts.A[0],70000);assert.equal(view.trainingCounts.B[1],70000);
 for(let phase=0;phase<4;phase++)for(let a=0;a<3;a++)for(let b=0;b<3;b++){const s=phase*9+a*3+b;assert.equal(view.originalWorldPolicies.A[s],f.greedyOwn[0][s]);assert.equal(view.originalWorldPolicies.B[s],f.greedyOwn[1][phase*9+b*3+a]);}
 assert.notEqual(view.originalWorldPolicies.B[3],f.greedyOwn[1][3]);assert.deepEqual(view.trainingCounts.rowOffsets,Array.from({length:37},(_,i)=>2*i));
 // Cap histories remain distinct even though both current supports are capped.
 assert.notEqual(view.originalWorldPolicies.A[0],view.originalWorldPolicies.A[3]);
});
test('count overflow, total horizon, own-row legality and saved startup/K4 next clocks are checked',()=>{
 for(const mutate of [f=>f.overflow[0].push([0,70000]),f=>f.counts[0][0]=12,f=>f.overflow[0][0][1]=69999,f=>f.greedyOwn[1][10]=0,f=>f.control.period=5,f=>f.terminal.phase=1]){const f=fixture();mutate(f);assert.throws(()=>checkpointGameData(f,{expectedRounds:70000}));}
 const f=fixture();f.control={id:'startup-only',period:null,phases:2};f.greedyOwn=f.greedyOwn.map(p=>p.slice(0,18));f.counts=f.counts.map(c=>c.slice(0,36));f.terminal.phase=1;assert.equal(checkpointGameData(f,{expectedRounds:70000}).terminal.phase,1);f.terminal.phase=0;assert.throws(()=>checkpointGameData(f,{expectedRounds:70000}));
});
test('response helper verifies every off-path action and preserves unavailable lock without fallback',()=>{
 const f=fixture(),record={id:'artificial-response',control:f.control,focal:'B',executionSucceeded:true,scientificAvailable:true,status:'certified',certificate:{passed:true}},world=checkpointGameData(f,{expectedRounds:70000});
 const policy=world.originalWorldPolicies.B;assert.deepEqual(responseGamePolicy(record,policy,f.finite).actions,policy);
 const bad=policy.slice();bad[35]=1;assert.throws(()=>responseGamePolicy(record,bad,f.finite));
 const unavailable={...record,executionSucceeded:false,scientificAvailable:false,status:'budget failure',failure:{message:'Artificial unavailable certificate'}};assert.equal(responseGamePolicy(unavailable,null,f.finite).actions,null);assert.match(responseGamePolicy(unavailable,null,f.finite).reason,/unavailable/);
});
