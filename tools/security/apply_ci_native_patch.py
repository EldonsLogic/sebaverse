"""Apply a separately approved, exact Ubuntu CI archive transaction; no DB access."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = {'libc6', 'libc-bin', 'libc-dev-bin', 'libc6-dev', 'libc6-i386', 'locales'}
SPEC = importlib.util.spec_from_file_location('native_metadata', Path(__file__).with_name('prepare_ci_native.py'))
metadata = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metadata)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=300).stdout


def require_platform(env, release, machine):
    if env.get('GITHUB_ACTIONS') != 'true' or release.get('ID') != 'ubuntu' or release.get('VERSION_ID') != '24.04' or machine != 'x86_64':
        raise ValueError('Only the approved Ubuntu24.04 amd64 GitHub CI runner is permitted')


def verify_transaction(approval, candidate, downloads, folder):
    if approval.get('schema_version') != 1 or approval.get('status') != 'approved_ci_only' or approval.get('scope') != 'ubuntu24.04-amd64-glibc-six-package-patch':
        raise ValueError('Explicit CI-only approval missing')
    if candidate.get('status') != 'candidate_recorded_review_required' or downloads.get('status') != 'downloaded_not_installed':
        raise ValueError('Candidate/download evidence incomplete')
    if downloads.get('candidate_record_sha256') != sha(folder / 'ubuntu-native-candidate.json'):
        raise ValueError('Candidate receipt hash mismatch')
    groups = [approval.get('packages', []), candidate.get('transaction', []), downloads.get('packages', [])]
    maps = []
    for rows in groups:
        mapping = {row['name']: row for row in rows}
        if len(mapping) != len(rows) or set(mapping) != PACKAGES:
            raise ValueError('Exactly the approved six packages are required')
        maps.append(mapping)
    approved, candidates, archives = maps
    result = []
    for name in sorted(PACKAGES):
        item, planned, actual = approved[name], candidates[name], archives[name]
        if item['version'] != planned['candidate'] or item['version'] != actual['version']:
            raise ValueError('Version differs from approval')
        if item['archive_sha256'] != actual['sha256'] or item['archive_sha256'] != planned['metadata']['sha256']:
            raise ValueError('Archive checksum differs from approval')
        archive = Path(actual['path'])
        notice = Path(actual['copyright']['copied_path'])
        for path in [archive, notice]:
            if path.is_symlink() or not path.resolve().is_relative_to((folder / 'candidate-archives').resolve()) or not path.is_file():
                raise ValueError('Archive/notice escapes reviewed download directory')
        if archive.suffix != '.deb' or sha(archive) != item['archive_sha256']:
            raise ValueError('Archive bytes differ from approval')
        if actual['copyright']['sha256'] != item['copyright_sha256'] or sha(notice) != item['copyright_sha256']:
            raise ValueError('Notice bytes differ from approval')
        result.append((name, item['version'], archive.resolve()))
    return result, candidates


def verify_simulation(text, planned, candidates):
    rows = metadata.parse_transaction(text)
    expected = {name: version for name, version, _ in planned}
    if {row['name']: row['candidate'] for row in rows} != expected:
        raise ValueError('Fresh dry-run differs from approved transaction')
    if any(row['installed'] != candidates[row['name']]['installed'] for row in rows):
        raise ValueError('Installed baseline changed since review')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', default='work/f2-security')
    args = parser.parse_args()
    folder = (ROOT / args.output_root).resolve()
    if not folder.is_relative_to((ROOT / 'work').resolve()):
        parser.error('Evidence must remain under repository work')
    release = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().replace('"', '').splitlines() if '=' in line)
    require_platform(os.environ, release, platform.machine())
    approval_path = ROOT / 'infra/local/native-patch-approval.json'
    approval_bytes = approval_path.read_text()
    committed = run(['git', '-C', str(ROOT), 'show', 'HEAD:infra/local/native-patch-approval.json'])
    if committed != approval_bytes:
        raise ValueError('Approval must exactly match committed HEAD')
    approval = json.loads(approval_bytes)
    candidate = json.loads((folder / 'ubuntu-native-candidate.json').read_text())
    downloads = json.loads((folder / 'ubuntu-native-downloads.json').read_text())
    planned, candidates = verify_transaction(approval, candidate, downloads, folder)
    archives = [str(path) for _, _, path in planned]
    base = ['apt-get', '--no-remove', '--no-install-recommends', '--only-upgrade']
    simulation = run(base + ['--simulate', 'install'] + archives)
    verify_simulation(simulation, planned, candidates)
    # Recheck every bound byte immediately before the sole mutating command.
    verify_transaction(approval, candidate, downloads, folder)
    receipt = {'schema_version': 1, 'status': 'started', 'approval_sha256': sha(approval_path),
               'started_at_utc': datetime.now(timezone.utc).isoformat(), 'simulation': simulation,
               'command': ['sudo'] + base + ['-y', 'install'] + archives, 'scope': 'CI package patch only; no native-use or DB approval'}
    output = folder / 'ubuntu-native-patch.json'
    try:
        receipt['output'] = run(receipt['command'])
        versions = {}
        for name, version, _ in planned:
            actual = run(['dpkg-query', '-W', '-f=${Version}', name]).strip()
            versions[name] = actual
            if actual != version:
                raise ValueError('Post-install version mismatch: ' + name)
        receipt.update(status='installed_rescan_required', installed_versions=versions)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        receipt.update(status='failed_do_not_use', error=str(error))
        raise
    finally:
        output.write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
