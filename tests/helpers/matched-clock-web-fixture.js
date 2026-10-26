// Wholly artificial UI fixture. No inherited game, Q, audit or outcome is read.
import crypto from 'node:crypto';
const exact=x=>{const scale=4;return{numerator:String(Math.round(x*scale)),denominator:'4',approximate:x};};
const runId=(seed,arm)=>`base-g15-t1--matched5-${arm}--zero--s${seed}`;
const ref=bytes=>({base64:Buffer.from(bytes).toString('base64'),bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
export function matchedWebFixture(){
 const data={schemaVersion:1,meta:{scope:'Artificial developer DOM fixture only; not accepted research evidence',inventoryAccepted:true,independentAuditPassed:true,audit:{passed:true},independentAuditSha256:'a'.repeat(64),primaryManifestSha256:'b'.repeat(64),fullTrainingReplay:true,replayComplete:true,defaultSelection:{seed:907001,checkpointStep:2000000,arms:['startup','recurring4'],chosenBeforeMatchedOutcomeInspection:true}},orderedSeeds:Array.from({length:12},(_,i)=>907001+i),arms:[{id:'startup'},{id:'recurring4'}],finiteGame:{prices:[1,2],capIndex:0,sets:[[0,1],[0,1]],upper:[1,1],rewards:{consumerSurplus:[4,3,3,1],profitA:[1,2,3,4],profitB:[4,3,2,1],quantityA:[10,20,30,40],quantityB:[40,30,20,10]}},runs:[],checkpoints:[],finalPolicyPairs:[],pairedRows:[],primarySummary:null};
 let sum=0;
 for(const seed of data.orderedSeeds){
  const values={};for(const arm of ['startup','recurring4']){
   const chosen=arm==='startup'?(seed%3===0?1:0):(seed%3===1?1:0),id=runId(seed,arm),mean=arm==='startup'?(chosen?1:4):(chosen?1.75:4);values[arm]=mean;
   data.runs.push({id,seed,arm,status:'artificial-completed'});
   const policies=[new Uint8Array(20),new Uint8Array(20)];for(let s=0;s<20;s++){const phase=Math.floor(s/4),a=phase===0||(arm==='recurring4'&&phase===4)?0:chosen;policies[0][s]=a;policies[1][s]=a;}
   for(const step of [1000000,2000000])data.checkpoints.push({id:id+`--t${step}`,runId:id,seed,arm,step,status:'artificial-accepted',scientificAvailable:true,reason:null,replayStatus:{accepted:true},terminal:{phase:4,previousIndices:[chosen,chosen],capExecutions:arm==='startup'?1:step/4},frozen:{actualTerminal:{cycleMetrics:{consumerSurplus:exact(mean)},transientRounds:0,cycleNodesFromStart:[4,8,12,16],trainingSupport:{A:{neverTriedGreedyActions:0},B:{neverTriedGreedyActions:0}}}},trainingTail:{metrics:{consumerSurplus:exact(mean)}},preview128:[]});
   data.finalPolicyPairs.push({checkpointId:id+'--t2000000',runId:id,seed,arm,available:true,reason:null,encoding:'uint8 WORLD row-major (phase,previousA,previousB)',states:20,start:{phase:4,previousIndices:[chosen,chosen]},policies:{A:ref(policies[0]),B:ref(policies[1])}});
  }
  const difference=values.recurring4-values.startup;sum+=difference;data.pairedRows.push({seed,available:true,reason:null,startup:{checkpointId:runId(seed,'startup')+'--t2000000',consumerSurplus:exact(values.startup)},recurring4:{checkpointId:runId(seed,'recurring4')+'--t2000000',consumerSurplus:exact(values.recurring4)},difference:exact(difference)});
 }
 data.primarySummary={available:true,reason:null,plannedPairs:12,acceptedPairs:12,mean:{numerator:String(Math.round(sum*4)),denominator:'48',approximate:sum/12}};return data;
}
