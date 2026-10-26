// Prospective treatment-aware checkpoint transport; no IO on import.
// Reuses immutable gzip/ref primitives, not the old guard-specific validator.
import {save,writeDense,sha,LAYOUT} from './matched-clock-io.js';
import {validateGuardReference,FULL_GRID_TREATMENT} from './guard-reference-learning.js';
const need=(v,m)=>{if(!v)throw Error(m);};
export function validateReferenceDensePair(qBytes,countBytes,finite,treatment,step){
 need(treatment===FULL_GRID_TREATMENT,'Production checkpoint must explicitly use full-grid-after-cap');
 const n=finite.prices.length,cells=5*n*n*n;
 need(Number.isInteger(n)&&n>=1&&n<=62&&Number.isInteger(finite.capIndex)&&finite.capIndex>=0&&finite.capIndex<n,'Invalid physical grid/cap');
 need(Number.isSafeInteger(step)&&step>=0&&step<=2000000,'Invalid checkpoint step');
 need(qBytes?.length===2&&countBytes?.length===2,'Both private dense arrays required');
 for(let f=0;f<2;f++){
  need(qBytes[f].length===cells*8&&countBytes[f].length===cells*4,'Dense pair length differs');let total=0;
  for(let row=0;row<5*n*n;row++)for(let action=0;action<n;action++){
   const cell=row*n+action,q=qBytes[f].readDoubleLE(cell*8),count=countBytes[f].readUInt32LE(cell*4);
   need(Number.isFinite(q)&&count<=step,'Nonfinite Q or excessive count');total+=count;
   if(row<n*n&&action>finite.capIndex)need(qBytes[f].readBigUInt64LE(cell*8)===0n&&count===0,'Forbidden phase0 cell changed');
  }
  need(total===step,'Firm count total differs from checkpoint step');
 }
 return true;
}
export function writeReferenceCheckpoint(root,m,{id,software,graph,finiteGameRef,windowMetrics}){
 validateGuardReference(m);
 need(m.supportTreatment.treatment===FULL_GRID_TREATMENT,'Only declared full-grid treatment may be serialized for the new study');
 need(typeof id==='string'&&/^[a-zA-Z0-9-]+$/.test(id)&&m.t>0,'Invalid checkpoint identity');
 need(graph?.graph?.supportTreatment?.effectiveSupportsSha256===m.supportTreatment.effectiveSupportsSha256&&JSON.stringify(graph.graph.scientificTreatment)===JSON.stringify(m.scientificTreatment)&&graph.graph.floor===null,'Graph support/floor treatment differs');
 need(graph.graph.step===m.t&&graph.graph.phase===m.phase&&graph.graph.arm==='startup','Graph actual checkpoint clock differs');
 need(graph.graph.cycles?.length>0&&graph.graph.cycles.every(c=>c.floorApplies===null&&c.floorGap===null)&&[graph.graph.actualTerminal,graph.graph.freshCapCounterfactual].every(t=>t&&t.floorApplies===null&&t.floorGap===null),'Inherited guard-floor claim cannot enter full-grid checkpoint');
 need(graph.policies?.length===2&&graph.worldPolicies?.length===2&&windowMetrics?.length===2,'Complete graph/policies/windows required');
 const dir=`checkpoints/${id}/${m.t}`,artifacts={q:[],counts:[]};
 for(let f=0;f<2;f++){
  artifacts.q.push(writeDense(root,`${dir}/Q-${f?'B':'A'}.f64le.gz`,m.q[f],'f64le',m.n));
  artifacts.counts.push(writeDense(root,`${dir}/counts-${f?'B':'A'}.u32le.gz`,m.counts[f],'u32le',m.n));
 }
 const policies={own:graph.policies.map((p,f)=>save(root,`${dir}/greedy-${f?'B':'A'}-own.u8`,Buffer.from(p))),world:graph.worldPolicies.map((p,f)=>save(root,`${dir}/greedy-${f?'B':'A'}-world.u8`,Buffer.from(p)))};
 const denseCache=a=>{const b=Buffer.allocUnsafe(a.length*8);for(let i=0;i<a.length;i++)b.writeDoubleLE(a[i],i*8);return b;};
 const metadata={schemaVersion:1,id,arm:'startup',treatment:FULL_GRID_TREATMENT,scientificTreatment:structuredClone(m.scientificTreatment),supportTreatment:structuredClone(m.supportTreatment),seed:m.seed,step:m.t,n:m.n,phases:5,layout:LAYOUT,finiteGameRef,
  learning:{T:m.T,alpha:m.alpha,gamma:m.gamma,initialization:'positive-zero'},terminal:{phase:m.phase,previousIndices:m.previous.slice()},actors:m.actors.map(s=>s.slice()),caps:m.caps,
  allocation:{cellsPerFirm:m.cells,qBytesPerFirm:m.cells*8,countBytesPerFirm:m.cells*4},artifacts,policies,
  policyCoordinateScope:'own rows phase/own/rival; WORLD rows phase/A/B; B mapped exactly once',
  windows:m.windows.map(w=>({...w,transitions:[...w.transitions].sort((a,b)=>a[0]-b[0])})),windowMetrics,
  curves:m.learningBlocks.map(b=>({...b})),transcriptBlocks:m.transcriptBlocks.map(b=>({...b})),
  transcriptPartial:{rounds:m.transcriptRounds,bytes:m.transcriptRounds*120,sha256:sha(m.transcriptBuffer.subarray(0,m.transcriptRounds*120)),scope:'Incomplete engineering tail, not a completed block'},
  cacheIdentity:{best:m.best.map(v=>sha(Buffer.from(v))),maximum:m.max.map(v=>sha(denseCache(v)))},
  graph:save(root,`${dir}/graph.json`,graph.graph),software};
 return save(root,`${dir}/metadata.json`,metadata);
}
