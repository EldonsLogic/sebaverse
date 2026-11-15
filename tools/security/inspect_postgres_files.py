"""Read-only proof of the authored COPY delta and retained entrypoint bytes."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import tarfile

from build_postgres_candidate import archive_member, digest, require

ROOT = Path(__file__).resolve().parents[2]
GOSU = 'usr/local/bin/gosu'
ENTRYPOINT = 'usr/local/bin/docker-entrypoint.sh'
MAX_LAYER_CONTENT = 1024 * 1024 * 1024
MAX_SOURCE = 128 * 1024


def inspect_layer(stream, final, expected_stub):
    """Never extract or execute foreign files. Retain only the one target source."""
    entrypoint = None
    seen = set()
    stub_found = False
    total = 0
    with tarfile.open(fileobj=stream, mode='r|*') as layer:
        for member in layer:
            name = member.name.removeprefix('./').rstrip('/')
            require(not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts,
                    'Unsafe filesystem-layer path')
            total += member.size
            require(0 <= member.size and total <= MAX_LAYER_CONTENT, 'Expanded layer exceeds bound')
            if final:
                require(name not in seen, 'Duplicate authored-layer path')
                seen.add(name)
                if member.isdir():
                    require(name in {'usr', 'usr/local', 'usr/local/bin'}, 'Unexpected authored-layer directory')
                else:
                    require(name == GOSU and member.isfile(), 'Only the authored regular gosu stub may change')
                    require(member.size <= MAX_SOURCE and member.mode & 0o7777 == 0o755, 'Stub size/mode mismatch')
                    data = layer.extractfile(member).read()
                    require(hashlib.sha256(data).hexdigest() == expected_stub, 'Effective stub differs from authored bytes')
                    stub_found = True
            if name in {'usr/.wh..wh..opq', 'usr/local/.wh..wh..opq',
                        'usr/local/bin/.wh..wh..opq', 'usr/local/bin/.wh.docker-entrypoint.sh'}:
                entrypoint = b''
            if name == ENTRYPOINT:
                require(member.isfile() and member.size <= MAX_SOURCE, 'Entrypoint must be a bounded regular source file')
                entrypoint = layer.extractfile(member).read()
    if final:
        require(stub_found, 'Authored stub missing from COPY layer')
    return entrypoint


def main():
    directory = ROOT / 'work/f2-security'
    path = directory / 'postgres-derived.oci.tar'
    receipt = json.loads((directory / 'postgres-derived-build.json').read_text())
    require(digest(path) == receipt['archive_sha256'], 'Derived archive differs from inspected build')
    manifest_name = 'blobs/sha256/' + receipt['platform_manifest_digest'].split(':')[1]
    manifest = json.loads(archive_member(path, manifest_name))
    source = None
    with tarfile.open(path, 'r:*') as archive:
        for index, layer in enumerate(manifest['layers']):
            name = 'blobs/sha256/' + layer['digest'].split(':')[1]
            data = inspect_layer(archive.extractfile(name), index == len(manifest['layers']) - 1,
                                 receipt['authored_replacement_sha256'])
            if data is not None:
                source = data
    require(bool(source), 'Retained entrypoint not found or removed')
    (directory / 'postgres-entrypoint-source.txt').write_bytes(source)
    result = {'status': 'static_files_inspected_not_cleared', 'archive_sha256': receipt['archive_sha256'],
              'platform_manifest_digest': receipt['platform_manifest_digest'],
              'copy_delta': 'only intended directories plus regular0755 gosu stub; exact authored hash',
              'stub_sha256': receipt['authored_replacement_sha256'],
              'entrypoint_sha256': hashlib.sha256(source).hexdigest(),
              'entrypoint_source': 'postgres-entrypoint-source.txt',
              'limits': 'Source extracted for manual branch review; no shell/image/DB execution. Lower-layer bytes retained.'}
    (directory / 'postgres-derived-files.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
