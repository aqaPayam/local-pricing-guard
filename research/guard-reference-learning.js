// Prospective pure support adapter. Importing performs no IO or training.
// The physical record and accepted numerical update/PRNG/clock remain unchanged.
import crypto from 'node:crypto';
import {createLearners,rebuildMaxima,validateState} from './matched-clock-learning.js';
import {evaluateFrozen,summarizeWindows} from './matched-clock-graph.js';
const need=(v,m)=>{if(!v)throw Error(m);};
const sha=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
export const FULL_GRID_TREATMENT='full-grid-after-cap';
export const GUARDED_PARITY_TREATMENT='startup-guard';
export function scientificTreatment(treatment=FULL_GRID_TREATMENT){
 need([FULL_GRID_TREATMENT,GUARDED_PARITY_TREATMENT].includes(treatment),'Unknown explicit scientific treatment');
 return {capClock:'startup',supportMode:treatment,initialCap:true,postInitialOriginalIndices:treatment===FULL_GRID_TREATMENT?'all':'original rival-dependent guard'};
}

export function supportDeclaration(finite,treatment=FULL_GRID_TREATMENT){
 need([FULL_GRID_TREATMENT,GUARDED_PARITY_TREATMENT].includes(treatment),'Unknown explicit support treatment');
 const n=finite.prices.length;
 return {schemaVersion:1,treatment,clock:'startup-only-five-phase',initialCap:'original physical cap; phase0 only',
  laterPhases:[1,2,3,4],laterSupport:treatment===FULL_GRID_TREATMENT?'all original price indices, independent of previous rival':'unchanged original rival-dependent guard',
  originalIndexRange:[0,n-1],originalCapIndex:finite.capIndex,originalGuardMasksSha256:sha(finite.sets),
  physicalRecordUnchanged:true,floorTransferred:false,
  scope:treatment===FULL_GRID_TREATMENT?'Initial cap, unrestricted thereafter over the original price grid; no inherited guard floor':'Artificial old-arm parity mode; not an additional new experimental treatment'};
}
function expectedSupports(finite,treatment){
 const n=finite.prices.length,cap=Array.from({length:finite.capIndex+1},(_,i)=>i),full=Array.from({length:n},(_,i)=>i);
 return Array.from({length:5},(_,phase)=>Array.from({length:n},(_,rival)=>(phase===0?cap:treatment===FULL_GRID_TREATMENT?full:finite.sets[rival]).slice()));
}
export function createGuardReferenceLearners(record,{treatment=FULL_GRID_TREATMENT,...options}={}){
 const m=createLearners(record,'startup',options);
 m.supportTreatment=supportDeclaration(m.finite,treatment);
 m.scientificTreatment=scientificTreatment(treatment);
 m.supports=expectedSupports(m.finite,treatment);
 m.supportTreatment.effectiveSupportsSha256=sha(m.supports);
 rebuildMaxima(m);
 return m;
}
export function validateGuardReference(m){
 need(m.arm==='startup'&&m.record&&(m.record.finite??m.record)===m.finite,'Reference must retain original physical record and startup clock');
 const d=m.supportTreatment;
 need(d&&[FULL_GRID_TREATMENT,GUARDED_PARITY_TREATMENT].includes(d.treatment),'Explicit support treatment missing');
 need(JSON.stringify(m.scientificTreatment)===JSON.stringify(scientificTreatment(d.treatment)),'Scientific treatment differs from support declaration');
 const expected=expectedSupports(m.finite,d.treatment),declaration=supportDeclaration(m.finite,d.treatment);
 declaration.effectiveSupportsSha256=sha(expected);
 need(JSON.stringify(d)===JSON.stringify(declaration),'Support declaration differs from physical record/treatment');
 need(sha(m.supports)===declaration.effectiveSupportsSha256,'Effective supports differ from declared treatment');
 validateState(m);
 return true;
}
export function evaluateGuardReference(m){
 validateGuardReference(m);
 const evaluation=evaluateFrozen(m,{certifyFloor:false});
 evaluation.graph.scientificTreatment=structuredClone(m.scientificTreatment);
 evaluation.graph.supportTreatment=structuredClone(m.supportTreatment);
 evaluation.graph.floor=null;
 evaluation.graph.scope+=' Support treatment is explicit; no inherited guard-envelope/floor assertion applies to full-grid continuation.';
 return evaluation;
}
export function summarizeGuardReferenceWindows(m){
 validateGuardReference(m);
 return summarizeWindows(m);
}
