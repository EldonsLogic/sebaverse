"""Capture npm's unsuppressed audit; narrowly apply AUTH-005 in synthetic development.

AUTH-011: the exception ends as soon as the registry publishes a version above the highest
affected one, and never later than 30 days after review. It binds the dependency and build
configuration, not application source files.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import subprocess

REVIEW_MAX_SECONDS = 30 * 86400

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_inputs(root):
    paths = [root / name for name in ('web/package.json', 'web/package-lock.json', 'web/vite.config.ts',
             '.github/workflows/dependencies.yml', 'tools/check_npm_audit.py')]
    require(all(not p.is_symlink() for p in paths), 'Source symlink is outside the review')
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def version_key(value):
    parts = value.split('+', 1)[0].split('.')
    return tuple(int(part) for part in parts) if len(parts) == 3 and all(p.isdigit() for p in parts) else None


def fixed_releases(policy, published):
    """Return package releases above the reviewed highest affected version (prereleases ignored)."""
    watch = policy.get('fix_watch')
    require(isinstance(watch, dict) and watch, 'Exception has no fix watch')
    require(isinstance(published, dict) and set(published) == set(watch), 'Registry release list unavailable')
    released = {}
    for name, highest in watch.items():
        limit = version_key(highest)
        require(limit is not None and isinstance(published[name], list) and published[name], 'Fix watch malformed')
        # Reject malformed release data and responses missing the reviewed version.
        numeric = r"(?:0|[1-9][0-9]*)"
        prerelease = r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
        semver = rf"{numeric}\.{numeric}\.{numeric}(?:-{prerelease}(?:\.{prerelease})*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
        require(all(isinstance(v, str) and re.fullmatch(semver, v) for v in published[name])
                and highest in published[name], 'Registry releases malformed or incomplete')
        newer = [v for v in published[name] if version_key(v) and version_key(v) > limit]
        if newer:
            released[name] = sorted(newer, key=version_key)
    return released


def validate(report, returncode, policy, root, scope, now=None, published=None):
    now = now or datetime.now(timezone.utc)
    require(type(report) is dict and report.get('auditReportVersion') == 2 and not report.get('error'), 'Invalid or failed audit')
    vulns = report.get('vulnerabilities')
    counts = report.get('metadata', {}).get('vulnerabilities', {})
    require(type(vulns) is dict and counts.get('total') == len(vulns), 'Incomplete audit counts')
    require(returncode in (0, 1), 'npm audit did not complete')
    if not vulns:
        require(returncode == 0 and all(counts.get(k) == 0 for k in ('info', 'low', 'moderate', 'high', 'critical')), 'Invalid clean audit')
        return {'status': 'pass', 'exceptions': 0}
    require(returncode == 1, 'Audit findings and process status disagree')
    require(scope == 'synthetic-development', 'Findings are not permitted outside synthetic development')
    require(policy.get('review_status') == 'reviewed', 'Exception has not completed independent review')
    require(policy.get('authority') == 'AUTH-005' and policy.get('scope') == scope, 'Missing scoped authority')
    start = datetime.fromisoformat(policy['reviewed_at_utc'])
    end = datetime.fromisoformat(policy['expires_at_utc'])
    require(start.tzinfo is not None and end.tzinfo is not None and start <= now < end and (end-start).total_seconds() <= REVIEW_MAX_SECONDS, 'Review expired or invalid')
    require(policy.get('source_inputs') == source_inputs(root), 'Reviewed source or lock changed')
    require(vulns == policy.get('reviewed_vulnerabilities'), 'New or changed audit finding')
    released = fixed_releases(policy, published)
    require(not released, 'Fix released, exception ended; upgrade and re-run: ' + json.dumps(released))
    require(counts == policy.get('reviewed_counts'), 'Audit severity or counts changed')
    lock = json.loads((root / 'web/package-lock.json').read_text())['packages']
    require(set(vulns) == {'fdir', 'picomatch', 'tinyglobby', 'vite'}, 'Unexpected dependency chain')
    for name, finding in vulns.items():
        require(finding.get('name') == name and finding.get('severity') == 'high', 'Finding identity changed')
        for node in finding.get('nodes', []):
            require(lock.get(node, {}).get('version') == policy['versions'].get(name), 'Affected version changed')
    return {'status': 'pass_with_temporary_development_exception', 'exceptions': len(vulns),
            'expires_at_utc': policy['expires_at_utc'], 'authority': 'AUTH-005'}


def registry_versions(name):
    result = subprocess.run(['npm', 'view', name, 'versions', '--json', '--registry=https://registry.npmjs.org'],
                            cwd=ROOT, capture_output=True, text=True, timeout=60)
    require(result.returncode == 0, 'Registry lookup failed for ' + name)
    versions = json.loads(result.stdout)
    require(isinstance(versions, list), 'Registry releases must be an array')
    return versions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', required=True, choices=['synthetic-development', 'production'])
    args = parser.parse_args()
    output = ROOT / 'work/ci'
    output.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(['npm', '--prefix', 'web', 'audit', '--audit-level=low', '--json',
                             '--registry=https://registry.npmjs.org'], cwd=ROOT, capture_output=True,
                            text=True, timeout=120)
    (output / 'web-audit.json').write_text(result.stdout)
    try:
        report = json.loads(result.stdout)
        policy = json.loads((ROOT / 'infra/development-npm-review.json').read_text())
        published = None
        if report.get('vulnerabilities'):
            published = {name: registry_versions(name) for name in policy.get('fix_watch', {})}
        receipt = validate(report, result.returncode, policy, ROOT, args.scope, published=published)
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        receipt = {'status': 'fail', 'reason': str(exc)}
    receipt['raw_report_sha256'] = hashlib.sha256(result.stdout.encode()).hexdigest()
    (output / 'web-audit-policy.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return 1 if receipt['status'] == 'fail' else 0


if __name__ == '__main__':
    raise SystemExit(main())
