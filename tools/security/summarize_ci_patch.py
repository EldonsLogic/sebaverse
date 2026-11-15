"""Report actual CI native patch/rescan evidence; never approve database use."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
from check_reports import findings, scan_database, syft_sbom

ROOT = Path(__file__).resolve().parents[2]


def main():
    folder = ROOT / 'work/f2-security'
    patch = json.loads((folder / 'ubuntu-native-patch.json').read_text())
    if patch.get('status') != 'installed_rescan_required':
        raise ValueError('Successful actual install receipt missing')
    native = json.loads((folder / 'system-native.json').read_text())
    sbom = json.loads((folder / 'system-native-sbom.json').read_text())
    report = json.loads((folder / 'system-native-cves.json').read_text())
    identities = syft_sbom(sbom, 'Patched native chain')
    if native.get('status') != 'identified':
        raise ValueError('Fresh actual native inventory missing')
    catalog = {(name, version) for name, version, _ in identities.values()}
    if not {(p['name'], p['version']) for p in native['owners']} <= catalog:
        raise ValueError('Native package scan coverage incomplete')
    libc = [p for p in native['owners'] if p['name'] == 'libc6']
    if len(libc) != 1 or libc[0]['version'] != patch['installed_versions']['libc6']:
        raise ValueError('Fresh linked-chain files do not identify patched libc6 package')
    scan_database(report['descriptor'], datetime.now(timezone.utc))
    matches = findings(report)
    fixed = {'CVE-2026-8674', 'CVE-2026-84243', 'CVE-2026-97399',
             'CVE-2026-18374', 'CVE-2026-95818', 'CVE-2026-86805'}
    if any(m['vulnerability']['id'] in fixed and m['artifact']['name'] == 'libc6' for m in matches):
        raise ValueError('Reviewed libc6 findings remain in post-patch scan')
    result = {'status': 'installed_rescanned_not_cleared', 'phase_approval': False,
              'database_execution': 'not_performed', 'installed_versions': patch['installed_versions'],
              'native_packages': len(native['owners']), 'matches': len(matches),
              'severity_counts': dict(Counter(m['vulnerability']['severity'] for m in matches)),
              'six_reviewed_libc6_matches_absent': True,
              'input_hashes': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                               for name in ['ubuntu-native-patch.json', 'system-native.json',
                                            'system-native-sbom.json', 'system-native-cves.json']},
              'scope': 'Reviewed disposable-CI upgrade and actual native rescan only; remaining findings, derived runtime binding and real PostgreSQL integration remain gated.'}
    (folder / 'ubuntu-native-patch-summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
