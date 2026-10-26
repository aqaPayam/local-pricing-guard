"""Synthetic delivery integrity checks; no research outcome files are read."""
from pathlib import Path
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import shutil
import unittest
import uuid
import zipfile

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('streaming',ROOT/'research/evidence_streaming.py')
stream=importlib.util.module_from_spec(spec);spec.loader.exec_module(stream)


@contextmanager
def workspace():
    parent=(ROOT/'.local').resolve();parent.mkdir(exist_ok=True)
    target=parent/('stream-integrity-test-'+uuid.uuid4().hex);target.mkdir()
    try:yield target
    finally:
        resolved=target.resolve()
        if not resolved.is_relative_to(parent) or not resolved.name.startswith('stream-integrity-test-'):raise ValueError('Unsafe test cleanup')
        shutil.rmtree(resolved)


class StreamingTests(unittest.TestCase):
    def test_chunked_mixed_sources_hash_crc_and_identical_fresh_repack(self):
        with workspace() as directory:
            large=bytes(range(251))*(stream.CHUNK//100+1)
            original=directory/'large.bin';original.write_bytes(large)
            sources={'data/large.bin':{'kind':'file','path':original},'readme.txt':{'kind':'bytes','data':b'fixed synthetic evidence\n'}}
            records=stream.inventory(sources)
            self.assertEqual(records['data/large.bin'],{'sha256':hashlib.sha256(large).hexdigest(),'bytes':len(large)})
            sources['PACKAGE_CONTENTS.json']={'kind':'bytes','data':json.dumps({'files':records},sort_keys=True).encode()}
            expected=stream.inventory(sources);archive=directory/'first.zip';stream.zip_sources(archive,sources,expected)
            extracted=directory/'extract';extracted.mkdir();verified=stream.extract_verified(archive,extracted)
            second=directory/'second.zip';restored=stream.extracted_sources(extracted,verified);stream.zip_sources(second,restored,stream.inventory(restored))
            self.assertEqual(stream.digest_file(archive),stream.digest_file(second))
            copied={'inherited.bin':{'kind':'zip','archive':archive,'member':'data/large.bin'}}
            self.assertEqual(stream.inventory(copied)['inherited.bin'],records['data/large.bin'])

    def test_changed_source_and_existing_destination_are_rejected(self):
        with workspace() as directory:
            file=directory/'source';file.write_bytes(b'before');sources={'file':{'kind':'file','path':file}};expected=stream.inventory(sources)
            file.write_bytes(b'after')
            with self.assertRaisesRegex(ValueError,'changed during'):stream.zip_sources(directory/'changed.zip',sources,expected)
            existing=directory/'preserve.zip';existing.write_bytes(b'preserve')
            with self.assertRaisesRegex(ValueError,'preserved'):stream.zip_sources(existing,sources)
            self.assertEqual(existing.read_bytes(),b'preserve')

    def test_unsafe_unmanifested_and_forged_payloads_are_rejected(self):
        with workspace() as directory:
            for index,kind in enumerate(['unsafe','unmanifested','wronghash']):
                archive=directory/f'{index}.zip';target=directory/f'extract-{index}';target.mkdir()
                with zipfile.ZipFile(archive,'w') as z:
                    if kind=='unsafe':z.writestr('../outside',b'bad');z.writestr('PACKAGE_CONTENTS.json',json.dumps({'files':{}}))
                    elif kind=='unmanifested':z.writestr('extra',b'bad');z.writestr('PACKAGE_CONTENTS.json',json.dumps({'files':{}}))
                    else:z.writestr('file',b'changed');z.writestr('PACKAGE_CONTENTS.json',json.dumps({'files':{'file':{'sha256':'0'*64,'bytes':7}}}))
                with self.assertRaises((ValueError,zipfile.BadZipFile)):stream.extract_verified(archive,target)
            self.assertFalse((directory/'outside').exists())


if __name__=='__main__':unittest.main()
