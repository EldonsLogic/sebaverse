"""Download metadata-bound Ubuntu glibc archives and inspect notices; never install."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {'libc6', 'libc6-i386', 'libc-bin', 'libc-dev-bin', 'libc6-dev', 'libc-devtools', 'locales', 'libc-l10n'}
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_TAR = 256 * 1024 * 1024
MAX_NOTICE = 2 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_row(row):
    name, version = row['name'], row['candidate']
    metadata = row['metadata']
    if name not in ALLOWED or not re.fullmatch(r'[A-Za-z0-9.+:~_-]+', version):
        raise ValueError('Unexpected package/version')
    if metadata.get('candidate') != version or not re.fullmatch(r'[0-9a-f]{64}', metadata.get('sha256', '')):
        raise ValueError('Missing exact candidate checksum binding')
    if not any(o.get('trusted') is True and o.get('origin') == 'Ubuntu' and o.get('label') == 'Ubuntu'
               and o.get('archive') in {'noble-updates', 'noble-security'} and o.get('component') == 'main'
               for o in metadata.get('origins', [])):
        raise ValueError('Missing trusted Ubuntu origin')
    return name, version, metadata['sha256']


def member_path(name):
    while name.startswith('./'):
        name = name[2:]
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or '\x00' in name:
        raise ValueError('Unsafe archive path')
    return str(path)


def read_notices(payloads, packages):
    """Inspect tar bytes without extracting files or executing maintainer scripts."""
    entries = {}
    for payload in payloads:
        if len(payload) > MAX_TAR:
            raise ValueError('Archive filesystem exceeds bound')
        with tarfile.open(fileobj=io.BytesIO(payload), mode='r:') as archive:
            for member in archive:
                path = member_path(member.name)
                if not path.startswith('usr/share/doc/'):
                    continue
                if path in entries:
                    # Shared directories across glibc companions are normal.
                    if member.isdir() and entries[path][0] == 'directory':
                        continue
                    raise ValueError('Duplicate documentation path')
                if member.isdir():
                    entries[path] = ('directory', None)
                elif member.issym():
                    target = member.linkname
                    if target.startswith('/'):
                        raise ValueError('Absolute documentation symlink')
                    parts = list(PurePosixPath(path).parent.parts)
                    for component in PurePosixPath(target).parts:
                        if component == '..':
                            if not parts:
                                raise ValueError('Escaping symlink')
                            parts.pop()
                        elif component not in {'.', ''}:
                            parts.append(component)
                    resolved = member_path('/'.join(parts))
                    if not resolved.startswith('usr/share/doc/'):
                        raise ValueError('Documentation symlink escapes scope')
                    entries[path] = ('symlink', resolved)
                elif member.isfile():
                    if path.endswith('/copyright'):
                        if member.size > MAX_NOTICE:
                            raise ValueError('Oversized copyright notice')
                        data = archive.extractfile(member).read(MAX_NOTICE + 1)
                        if not data or len(data) > MAX_NOTICE:
                            raise ValueError('Missing or oversized notice')
                        entries[path] = ('file', data)
                elif member.islnk():
                    raise ValueError('Unsupported documentation hard link')
    result = {}
    for package in packages:
        path, seen = 'usr/share/doc/' + package + '/copyright', set()
        for _ in range(16):
            if path in seen:
                raise ValueError('Cyclic notice symlink')
            seen.add(path)
            if path not in entries:
                # A directory itself may be symlinked by a companion.
                parent = str(PurePosixPath(path).parent)
                value = entries.get(parent)
                if value and value[0] == 'symlink':
                    path = value[1] + '/' + PurePosixPath(path).name
                    continue
                raise ValueError('Candidate copyright missing: ' + package)
            kind, value = entries[path]
            if kind == 'file':
                result[package] = {'archive_path': path, 'sha256': digest(value), 'bytes': len(value), 'data': value}
                break
            if kind != 'symlink':
                raise ValueError('Notice is not a regular file')
            path = value
        else:
            raise ValueError('Notice resolution limit exceeded')
    return result


def filesystem_tar(archive):
    with subprocess.Popen(['dpkg-deb', '--fsys-tarfile', str(archive)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        data = process.stdout.read(MAX_TAR + 1)
        if len(data) > MAX_TAR:
            process.kill()
            raise ValueError('Expanded archive exceeds bound')
        if process.wait(timeout=90):
            raise ValueError('dpkg-deb inspection failed')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', default='work/f2-security')
    output = Path(parser.parse_args().output_root).resolve()
    if not output.is_relative_to((ROOT / 'work').resolve()):
        parser.error('Output must remain under ignored repository work')
    source = output / 'ubuntu-native-candidate.json'
    data = source.read_bytes()
    record = json.loads(data)
    if record.get('status') != 'candidate_recorded_review_required':
        raise ValueError('Candidate transaction is not reviewable')
    rows = record['transaction']
    names = [validate_row(row)[0] for row in rows]
    if not rows or len(set(names)) != len(names) or 'libc6' not in names:
        raise ValueError('Incomplete or duplicate transaction')
    destination = output / 'candidate-archives'
    destination.mkdir(exist_ok=False)
    archives, payloads = [], []
    for row in rows:
        name, version, expected = validate_row(row)
        folder = destination / name
        folder.mkdir()
        subprocess.run(['apt-get', 'download', name + '=' + version], cwd=folder, check=True, timeout=120)
        files = list(folder.iterdir())
        if len(files) != 1 or files[0].is_symlink() or files[0].suffix != '.deb' or files[0].stat().st_size > MAX_ARCHIVE:
            raise ValueError('Unexpected downloaded archive')
        archive = files[0]
        if digest(archive.read_bytes()) != expected:
            raise ValueError('Downloaded archive checksum mismatch')
        archives.append({'name': name, 'version': version, 'path': str(archive), 'sha256': expected})
        payloads.append(filesystem_tar(archive))
    notices = read_notices(payloads, names)
    for archive in archives:
        notice = notices[archive['name']]
        notice_path = destination / archive['name'] / 'copyright'
        notice_path.write_bytes(notice.pop('data'))
        archive['copyright'] = dict(notice, copied_path=str(notice_path))
    receipt = {'schema_version': 1, 'status': 'downloaded_not_installed', 'candidate_record_sha256': digest(data),
               'packages': archives, 'limitations': ['Notice inspection is evidence for review, not rights clearance or install authorization.', 'No maintainer scripts executed; no system packages changed.']}
    (output / 'ubuntu-native-downloads.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
