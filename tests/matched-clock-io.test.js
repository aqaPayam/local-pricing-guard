import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {rawLength,denseBytes,writeDense,readDense,inflateDense,validateDensePair,sha,local,save} from '../research/matched-clock-io.js';
const temp=()=>{const p=path.join(process.cwd(),'.local','matched-transport-test-'+crypto.randomUUID());fs.mkdirSync(p,{recursive:true});return p;};
test('canonical full dense f64/u32 identities include positive forbidden zeros',()=>{
 const root=temp();try{const n=2,q=new Float64Array(5*n*n*n),counts=new Uint32Array(q.length);q[0]=-.25;counts[0]=7;
  for(const [values,encoding] of [[q,'f64le'],[counts,'u32le']]){const ref=writeDense(root,encoding+'.gz',values,encoding,n),raw=readDense(root,ref,n,encoding);assert.equal(raw.length,rawLength(n,encoding));assert.equal(ref.rawSha256,sha(denseBytes(values,encoding,n)));}
 }finally{fs.rmSync(root,{recursive:true});}
});
test('strict single-member gzip rejects truncation, concatenation, trailing bytes, raw/hash/ceiling drift',()=>{
 const root=temp();try{const n=2,ref=writeDense(root,'q.gz',new Float64Array(40),'f64le',n),gzip=fs.readFileSync(path.join(root,'q.gz'));
  for(const bad of [gzip.subarray(0,-1),Buffer.concat([gzip,gzip]),Buffer.concat([gzip,Buffer.from([0])])])assert.throws(()=>inflateDense(bad,ref,n,'f64le'));
  assert.throws(()=>inflateDense(gzip,{...ref,rawBytes:ref.rawBytes-8},n,'f64le'));
  assert.throws(()=>inflateDense(gzip,{...ref,rawSha256:'0'.repeat(64)},n,'f64le'));
  const bomb=zlib.gzipSync(Buffer.alloc(ref.rawBytes+1));assert.throws(()=>inflateDense(bomb,ref,n,'f64le'));
  const corrupt=Buffer.from(gzip);corrupt[corrupt.length-8]^=1;assert.throws(()=>inflateDense(corrupt,ref,n,'f64le'));
 }finally{fs.rmSync(root,{recursive:true});}
});
test('dense validation rejects forbidden minus-zero, forbidden counts, wrong totals and nonfinite Q',()=>{
 const f={prices:[1,2],capIndex:0,sets:[[0,1],[0,1]]},q=[new Float64Array(40),new Float64Array(40)],c=[new Uint32Array(40),new Uint32Array(40)];c[0][0]=c[1][0]=2;
 const check=()=>validateDensePair(q.map(v=>denseBytes(v,'f64le',2)),c.map(v=>denseBytes(v,'u32le',2)),f,'startup',2);
 assert.equal(check(),true);q[0][1]=-0;assert.throws(check);q[0][1]=0;c[0][1]=1;assert.throws(check);c[0][1]=0;c[0][0]=1;assert.throws(check);c[0][0]=2;q[0][0]=NaN;assert.throws(check);
});
test('artifact paths and exclusive writes reject traversal, aliases and overwritten checkpoints',()=>{
 const root=temp();try{for(const p of ['../bad','/bad','a/../b','a\\b','a:b','a//b'])assert.throws(()=>local(root,p));const ref=save(root,'fine/value.json',{a:1});assert.equal(ref.bytes,13);assert.throws(()=>save(root,'fine/value.json',{}));}finally{fs.rmSync(root,{recursive:true});}
});
