import test from 'node:test';import assert from 'node:assert/strict';
import {safeName,evidenceReader,sha256} from '../research/learned-opponent-evidence.js';
test('evidence helper imports/construction are lazy and all artifact identities are explicit',()=>{
 const files={'study/value.json':Buffer.from('{"value":1}\n'),'study/artifacts/x.bin':Buffer.from([1,2,3])};let reads=0;
 const reader=evidenceReader({readBytes:name=>{reads++;assert.ok(files[name]);return files[name];}});assert.equal(reads,0);assert.deepEqual(reader.json('study/value.json'),{value:1});
 const data=files['study/artifacts/x.bin'],ref={file:'artifacts/x.bin',bytes:3,sha256:sha256(data)};assert.equal(reader.ref('study',ref).bytes.length,3);assert.equal(reader.recheck(),true);
 assert.throws(()=>reader.ref('study',{...ref,bytes:2}));assert.throws(()=>reader.ref('study',{...ref,sha256:'0'.repeat(64)}));
});
test('unsafe paths, changed snapshots and malformed byte/hash refs cannot masquerade as accepted inputs',()=>{
 for(const bad of ['../secret','/absolute','C:/secret','a\\b','a/../b','a//b','./a'])assert.throws(()=>safeName(bad));
 let value=Buffer.from('before');const reader=evidenceReader({readBytes:()=>value});reader.hash('safe/file');value=Buffer.from('after');assert.throws(()=>reader.recheck(),/changed during/);
 for(const bad of [{file:'a',bytes:-1,sha256:'0'.repeat(64)},{file:'a',bytes:1,sha256:'INVALID'},{file:'../a',bytes:1,sha256:'0'.repeat(64)}])assert.throws(()=>reader.ref('study',bad));
});
