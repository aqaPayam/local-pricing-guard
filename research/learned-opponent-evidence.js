// Lazy read-only evidence identity helpers; constructing/importing reads nothing.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
const need=(ok,message)=>{if(!ok)throw Error(message);};
export const sha256=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export function safeName(name){
 need(typeof name==='string'&&name.length>0&&!name.includes('\\')&&!name.includes(':')&&!name.startsWith('/')&&name.split('/').every(s=>s&&s!=='.'&&s!=='..'),'Unsafe project-relative evidence name');return name;
}
export function localIO(root){
 const base=path.resolve(root),resolve=name=>{const target=path.resolve(base,...safeName(name).split('/'));need(target.startsWith(base+path.sep),'Evidence escapes project root');return target;};
 return {readBytes:name=>fs.readFileSync(resolve(name)),exists:name=>fs.existsSync(resolve(name))};
}
export function evidenceReader(io){
 need(io&&typeof io.readBytes==='function','Read-only evidence IO required');const cache=new Map(),inputHashes={};
 const bytes=name=>{name=safeName(name);if(!cache.has(name))cache.set(name,Buffer.from(io.readBytes(name)));return cache.get(name);};
 const hash=name=>{name=safeName(name);const h=sha256(bytes(name));need(!inputHashes[name]||inputHashes[name]===h,'Conflicting evidence identity '+name);inputHashes[name]=h;return h;};
 const json=name=>{hash(name);return JSON.parse(bytes(name).toString('utf8').replace(/^\uFEFF/,''));};
 const bind=(name,expected)=>{need(typeof expected==='string'&&/^[0-9a-f]{64}$/.test(expected)&&hash(name)===expected,'Evidence hash binding differs '+name);return bytes(name);};
 const ref=(base,entry)=>{need(entry&&typeof entry.file==='string'&&Number.isSafeInteger(entry.bytes)&&entry.bytes>=0,'Artifact reference malformed');const name=safeName((base?base+'/':'')+safeName(entry.file)),data=bind(name,entry.sha256);need(data.length===entry.bytes,'Artifact byte length differs '+name);return {name,bytes:data};};
 const recheck=()=>{for(const [name,h]of Object.entries(inputHashes))need(sha256(Buffer.from(io.readBytes(name)))===h,'Evidence changed during read-only derivation '+name);return true;};
 return {bytes,hash,json,bind,ref,recheck,inputHashes};
}
