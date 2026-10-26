"""Bounded-memory delivery primitives; no scientific calculations or outcomes."""
from contextlib import contextmanager, ExitStack
from io import BytesIO
from pathlib import Path, PurePosixPath
import hashlib
import json
import zipfile

CHUNK = 1024*1024


def safe_name(name):
    return (isinstance(name,str) and bool(name) and '\\' not in name and ':' not in name
            and not name.startswith('/') and not name.endswith('/')
            and all(p not in ('', '.', '..') for p in name.split('/')))


def digest_stream(stream):
    digest=hashlib.sha256();size=0
    while True:
        chunk=stream.read(CHUNK)
        if not chunk:break
        digest.update(chunk);size+=len(chunk)
    return {'sha256':digest.hexdigest(),'bytes':size}


def digest_file(path):
    with Path(path).open('rb') as stream:return digest_stream(stream)


@contextmanager
def source_stream(source, archives=None):
    kind=source['kind']
    if kind=='file':
        with Path(source['path']).open('rb') as stream:yield stream
    elif kind=='bytes':
        with BytesIO(source['data']) as stream:yield stream
    elif kind=='zip':
        if not safe_name(source['member']):raise ValueError('Unsafe source member')
        if archives is not None:
            with archives[str(source['archive'])].open(source['member']) as stream:yield stream
        else:
            with zipfile.ZipFile(source['archive']) as archive:
                with archive.open(source['member']) as stream:yield stream
    else:raise ValueError('Unknown evidence source kind')


def inventory(sources):
    result={}
    with ExitStack() as stack:
        archives={str(s['archive']):None for s in sources.values() if s['kind']=='zip'}
        for name in archives:archives[name]=stack.enter_context(zipfile.ZipFile(name))
        for name,source in sorted(sources.items()):
            if not safe_name(name):raise ValueError('Unsafe delivery path '+name)
            with source_stream(source,archives) as stream:result[name]=digest_stream(stream)
    return result


def zip_sources(destination,sources,expected=None):
    """Same deterministic metadata as prior deliveries; stream each file once."""
    destination=Path(destination)
    if destination.exists():raise ValueError('Existing evidence archive preserved')
    with ExitStack() as stack:
        archives={str(s['archive']):None for s in sources.values() if s['kind']=='zip'}
        for name in archives:archives[name]=stack.enter_context(zipfile.ZipFile(name))
        archive=stack.enter_context(zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6))
        for name,source in sorted(sources.items()):
            if not safe_name(name):raise ValueError('Unsafe delivery member '+name)
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3;info.external_attr=0o100644<<16;info._compresslevel=6
            if expected:info.file_size=expected[name]['bytes']
            digest=hashlib.sha256();size=0
            with source_stream(source,archives) as stream,archive.open(info,'w') as target:
                while True:
                    chunk=stream.read(CHUNK)
                    if not chunk:break
                    target.write(chunk);digest.update(chunk);size+=len(chunk)
            if expected and {'sha256':digest.hexdigest(),'bytes':size}!=expected[name]:raise ValueError('Source changed during archive creation '+name)


def extract_verified(archive,directory):
    """Validate every path/hash/CRC while streaming into a new empty directory."""
    directory=Path(directory).resolve()
    if not directory.is_dir() or any(directory.iterdir()):raise ValueError('Fresh empty extraction directory required')
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or any(not safe_name(n) for n in names):raise ValueError('Unsafe/duplicate archive inventory')
        contents=json.loads(z.read('PACKAGE_CONTENTS.json'))
        records=contents['files']
        if set(names)!=set(records)|{'PACKAGE_CONTENTS.json'}:raise ValueError('Unmanifested archive entry')
        for name in sorted(names):
            target=(directory/PurePosixPath(name)).resolve()
            if not target.is_relative_to(directory):raise ValueError('Extraction traversal')
            target.parent.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256();size=0
            with z.open(name) as source,target.open('xb') as output:
                while True:
                    chunk=source.read(CHUNK)
                    if not chunk:break
                    output.write(chunk);digest.update(chunk);size+=len(chunk)
            if name!='PACKAGE_CONTENTS.json' and (digest.hexdigest()!=records[name]['sha256'] or size!=records[name]['bytes']):raise ValueError('Manifested payload differs '+name)
    return records


def extracted_sources(directory,records):
    directory=Path(directory).resolve();names=[*records,'PACKAGE_CONTENTS.json'];sources={}
    for name in names:
        if not safe_name(name):raise ValueError('Unsafe extracted inventory')
        p=(directory/name).resolve()
        if not p.is_relative_to(directory):raise ValueError('Extracted source traversal')
        sources[name]={'kind':'file','path':p}
    return sources
