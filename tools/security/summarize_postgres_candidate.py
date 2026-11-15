"""Summarize a static derived-image experiment; NEVER authorize native/DB use."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import sys

from check_reports import findings, scan_database, syft_sbom

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'work/f2-security'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    paths = {name: DIRECTORY / name for name in [
        'postgres-derived-build.json', 'postgres-derived.oci.tar',
        'postgres-derived-sbom.json', 'postgres-derived-cves.json']}
    build = json.loads(paths['postgres-derived-build.json'].read_text())
    if build.get('status') != 'built_static_not_cleared':
        raise ValueError('Static build receipt missing or invalid')
    if digest(paths['postgres-derived.oci.tar']) != build['archive_sha256']:
        raise ValueError('Derived archive changed after static inspection')
    sbom = json.loads(paths['postgres-derived-sbom.json'].read_text())
    identities = syft_sbom(sbom, 'Derived OCI experiment')
    metadata = sbom['source']['metadata']
    if sbom['source']['type'] != 'image' or metadata.get('manifestDigest') != build['platform_manifest_digest']:
        raise ValueError('Derived SBOM is not bound to actual built platform manifest')
    if metadata.get('architecture') != 'amd64' or metadata.get('os') != 'linux':
        raise ValueError('Derived SBOM platform differs')
    catalogers = sbom['descriptor']['configuration']['catalogers']
    if catalogers['requested'].get('default') != ['image', 'file']:
        raise ValueError('Experiment requires full default image catalog, not selected packages')
    if not {'apk-db-cataloger', 'go-module-binary-cataloger'} <= set(catalogers['used']):
        raise ValueError('Missing OS or Go binary cataloger coverage')
    if any(a['name'] == 'stdlib' and a['version'] == 'go1.24.6' for a in sbom['artifacts']):
        raise ValueError('Original vulnerable Go runtime still cataloged in effective filesystem')
    report = json.loads(paths['postgres-derived-cves.json'].read_text())
    matches = findings(report)
    scan_database(report['descriptor'], datetime.now(timezone.utc))
    target = report.get('source', {}).get('target', {})
    if report.get('source', {}).get('type') != 'image' or target.get('manifestDigest') != build['platform_manifest_digest']:
        raise ValueError('Advisory report source differs from derived image')
    for match in matches:
        artifact = match['artifact']
        if identities.get(artifact['id']) != (artifact['name'], artifact['version'], artifact['type']):
            raise ValueError('Advisory artifact differs from actual catalog')
    counts = Counter(m['vulnerability']['severity'] for m in matches)
    result = {
        'status': 'held_findings' if matches else 'scan_clean_not_preuse_approved',
        'task': 'DEV-006', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'database_execution': 'not_performed', 'phase_approval': False,
        'platform_manifest_digest': build['platform_manifest_digest'],
        'archive_sha256': build['archive_sha256'], 'packages': len(identities),
        'matches': len(matches), 'severity_counts': dict(counts),
        'input_hashes': {name: digest(path) for name, path in paths.items() if path.suffix != '.tar'},
        'scope': 'Static derived merged-filesystem experiment only. Native chain/core review, final source/runner binding and actual database integration remain gated. Lower-layer bytes are retained.'}
    (DIRECTORY / 'postgres-derived-summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
