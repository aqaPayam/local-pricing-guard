// Primary transport only. No training, inherited input reads or IO on import.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
export const LAYOUT='dense5-own-rival-original-action-v1';
const need=(v,m)=>{if(!v)throw Error(m);};
export const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export const jsonBytes=v=>Buffer.from(JSON.stringify(v,null,2)+'\n');
export function local(root,name){
 need(typeof name==='string'&&name.length&&!name.includes('\\')&&!name.includes(':')&&!name.startsWith('/')&&name.split('/').every(x=>x&&x!=='.'&&x!=='..'),'Unsafe artifact path');
 const base=path.resolve(root),p=path.resolve(base,name);need(p.startsWith(base+path.sep),'Artifact escapes directory');return p;
}
export function save(root,name,bytes){
 const p=local(root,name),b=Buffer.isBuffer(bytes)?bytes:jsonBytes(bytes);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,b,{flag:'wx'});return{file:name,bytes:b.length,sha256:sha(b)};
}
export function readRef(root,ref,ceiling=64_000_000){
 need(ref&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=ceiling&&/^[a-f0-9]{64}$/.test(ref.sha256),'Invalid bounded reference');
 const p=local(root,ref.file);need(fs.statSync(p).size===ref.bytes,'Stored length differs');const b=fs.readFileSync(p);need(sha(b)===ref.sha256,'Stored hash differs');return b;
}
const CRC=new Uint32Array(256);
for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xedb88320^(c>>>1):c>>>1;CRC[n]=c>>>0;}
export function crc32(bytes){let c=0xffffffff;for(const b of bytes)c=CRC[(c^b)&255]^(c>>>8);return(c^0xffffffff)>>>0;}
export function rawLength(n,encoding){
 need(Number.isInteger(n)&&n>=1&&n<=62,'Dense quote dimension outside protocol');
 need(['f64le','u32le'].includes(encoding),'Unknown dense encoding');return 5*n*n*n*(encoding==='f64le'?8:4);
}
export function denseBytes(values,encoding,n){
 const length=rawLength(n,encoding),width=encoding==='f64le'?8:4;need(values?.length===length/width,'Dense cell count differs');const b=Buffer.allocUnsafe(length);
 for(let i=0;i<values.length;i++){const v=values[i];if(encoding==='f64le'){need(Number.isFinite(v),'Nonfinite Q');b.writeDoubleLE(v,i*8);}else{need(Number.isInteger(v)&&v>=0&&v<=0xffffffff,'Invalid uint32 count');b.writeUInt32LE(v,i*4);}}
 return b;
}
export function writeDense(root,name,values,encoding,n){
 const raw=denseBytes(values,encoding,n),gzip=zlib.gzipSync(raw,{level:6,mtime:0});return{...save(root,name,gzip),encoding,compression:'gzip-single-member',rawBytes:raw.length,rawSha256:sha(raw)};
}
export function inflateDense(gzip,ref,n,encoding){
 const expected=rawLength(n,encoding);need(ref.encoding===encoding&&ref.compression==='gzip-single-member'&&ref.rawBytes===expected&&/^[a-f0-9]{64}$/.test(ref.rawSha256),'Declared raw dense identity differs');
 need(gzip.length>=18&&gzip.length<=expected+65536&&gzip[0]===31&&gzip[1]===139&&gzip[2]===8&&gzip[3]===0&&gzip.readUInt32LE(4)===0,'Unsupported or oversized canonical gzip wrapper');
 const compressed=gzip.subarray(10,-8),out=zlib.inflateRawSync(compressed,{info:true,maxOutputLength:expected+1});
 need(out.engine.bytesWritten===compressed.length,'Trailing gzip data or multiple members');const raw=out.buffer;
 need(raw.length===expected&&gzip.readUInt32LE(gzip.length-4)===expected&&gzip.readUInt32LE(gzip.length-8)===crc32(raw),'Gzip length or CRC differs');
 need(sha(raw)===ref.rawSha256,'Canonical dense hash differs');return raw;
}
export function readDense(root,ref,n,encoding){return inflateDense(readRef(root,ref,rawLength(n,encoding)+65536),ref,n,encoding);}
export function validateDensePair(qBytes,countBytes,finite,arm,step){
 const n=finite.prices.length,cells=5*n*n*n;need(['startup','recurring4'].includes(arm)&&Number.isSafeInteger(step)&&step>=0&&step<=2000000,'Invalid dense checkpoint arm/step');
 for(let f=0;f<2;f++){
  need(qBytes[f].length===cells*8&&countBytes[f].length===cells*4,'Dense pair length differs');let total=0;
  for(let row=0;row<5*n*n;row++){
   const phase=Math.floor(row/(n*n)),rival=row%n,cap=phase===0||(arm==='recurring4'&&phase===4),legal=cap?Array.from({length:finite.capIndex+1},(_,i)=>i):finite.sets[rival],allowed=new Set(legal);
   for(let a=0;a<n;a++){const i=row*n+a,q=qBytes[f].readDoubleLE(i*8),c=countBytes[f].readUInt32LE(i*4);need(Number.isFinite(q)&&c<=step,'Nonfinite Q or excessive cell count');total+=c;if(!allowed.has(a))need(qBytes[f].readBigUInt64LE(i*8)===0n&&c===0,'Forbidden cell is not positive-zero/unvisited');}
  }
  need(total===step,'Firm count total differs from checkpoint step');
 }
 return true;
}
export function writeCheckpoint(root,m,{id,software,graph,finiteGameRef,windowMetrics}){
 need(typeof id==='string'&&/^[a-zA-Z0-9-]+$/.test(id)&&m.t>0,'Invalid checkpoint identity');
 const dir=`checkpoints/${id}/${m.t}`,artifacts={q:[],counts:[]};
 for(let f=0;f<2;f++){artifacts.q.push(writeDense(root,`${dir}/Q-${f?'B':'A'}.f64le.gz`,m.q[f],'f64le',m.n));artifacts.counts.push(writeDense(root,`${dir}/counts-${f?'B':'A'}.u32le.gz`,m.counts[f],'u32le',m.n));}
 need(graph?.graph&&graph.policies?.length===2&&graph.worldPolicies?.length===2,'Complete primary graph and both policy coordinate families required');
 const policies={own:graph.policies.map((p,f)=>save(root,`${dir}/greedy-${f?'B':'A'}-own.u8`,Buffer.from(p))),world:graph.worldPolicies.map((p,f)=>save(root,`${dir}/greedy-${f?'B':'A'}-world.u8`,Buffer.from(p)))};
 const graphRef=save(root,`${dir}/graph.json`,graph.graph),windows=m.windows.map(w=>({...w,transitions:[...w.transitions].sort((a,b)=>a[0]-b[0])}));
 need(Array.isArray(windowMetrics)&&windowMetrics.length===2,'Both exact window summaries required');
 const metadata={schemaVersion:1,id,arm:m.arm,seed:m.seed,step:m.t,n:m.n,phases:5,layout:LAYOUT,finiteGameRef,learning:{T:m.T,alpha:m.alpha,gamma:m.gamma,initialization:'positive-zero'},terminal:{phase:m.phase,previousIndices:m.previous.slice()},actors:m.actors.map(s=>s.slice()),caps:m.caps,
  allocation:{cellsPerFirm:m.cells,qBytesPerFirm:m.cells*8,countBytesPerFirm:m.cells*4},artifacts,policies,policyCoordinateScope:'own rows phase/own/rival; WORLD rows phase/A/B; B mapped exactly once',windows,windowMetrics,curves:m.learningBlocks.map(b=>({...b})),transcriptBlocks:m.transcriptBlocks.map(b=>({...b,bytes:1200000})),
  transcriptPartial:{rounds:m.transcriptRounds,bytes:m.transcriptRounds*120,sha256:sha(m.transcriptBuffer.subarray(0,m.transcriptRounds*120)),scope:'Incomplete engineering tail, not a completed block'},
  cacheIdentity:{best:m.best.map(v=>sha(Buffer.from(v))),maximum:m.max.map(v=>sha(denseCacheBytes(v)))},graph:graphRef,software};
 return save(root,`${dir}/metadata.json`,metadata);
}
function denseCacheBytes(array){const b=Buffer.allocUnsafe(array.length*8);for(let i=0;i<array.length;i++)b.writeDoubleLE(array[i],i*8);return b;}
