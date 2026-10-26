// Prospectively fixed whole-seed resampling. No training or study outcomes.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import{fileURLToPath}from'node:url';
export const BOOTSTRAP={seed:20261026,replicates:5120,sampleSize:12,algorithm:'Mulberry32',percentiles:[0.025,0.975],percentileConvention:'linear/type7, h=(N-1)*p',unit:'Whole paired market seed; shared index draws across all four primary strata'};
export function mulberry32(initial){let state=initial>>>0;return()=>{state=(state+0x6D2B79F5)>>>0;let t=Math.imul(state^(state>>>15),state|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
export function indices(){const random=mulberry32(BOOTSTRAP.seed);return Array.from({length:BOOTSTRAP.replicates},()=>Array.from({length:BOOTSTRAP.sampleSize},()=>Math.floor(BOOTSTRAP.sampleSize*random())));}
export function percentileType7(sorted,p){if(!sorted.length||p<0||p>1||sorted.some(v=>!Number.isFinite(v)))throw Error('Finite sorted samples and percentile in [0,1] required');const at=(sorted.length-1)*p,lo=Math.floor(at),hi=Math.ceil(at);return sorted[lo]+(sorted[hi]-sorted[lo])*(at-lo);}
export function pairedMeanInterval(pairs,draws=indices()){
 if(pairs.length!==BOOTSTRAP.sampleSize||pairs.some(v=>!Number.isFinite(v)))throw Error('All twelve finite paired seed differences required');
 if(draws.length!==BOOTSTRAP.replicates||draws.some(row=>row.length!==BOOTSTRAP.sampleSize||row.some(i=>!Number.isInteger(i)||i<0||i>=BOOTSTRAP.sampleSize)))throw Error('Declared 5120-by-12 index matrix required');
 const mean=pairs.reduce((a,b)=>a+b,0)/pairs.length,values=draws.map(row=>row.reduce((sum,i)=>sum+pairs[i],0)/row.length).sort((a,b)=>a-b);
 return{estimate:mean,lower:percentileType7(values,0.025),upper:percentileType7(values,0.975),replicates:BOOTSTRAP.replicates,pairs:12,scope:'Marginal descriptive percentile interval on paired whole-seed mean, not simultaneous coverage or round-level replication'};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv.length!==3||process.argv[2]!=='freeze')throw Error('Use node research/adaptive-bootstrap.js freeze');
 const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),output=path.join(root,'research/adaptive-bootstrap-indices.json'),data=Buffer.from(JSON.stringify({...BOOTSTRAP,indices:indices()})+'\n');
 if(fs.existsSync(output)){if(!fs.readFileSync(output).equals(data))throw Error('Existing prospective resample inventory differs; refusing overwrite');}else fs.writeFileSync(output,data,{flag:'wx'});
 console.log(JSON.stringify({file:path.relative(root,output),sha256:crypto.createHash('sha256').update(data).digest('hex'),bytes:data.length,replicates:BOOTSTRAP.replicates,sampleSize:BOOTSTRAP.sampleSize,outcomesRead:0}));
}
