"""Capture npm's unsuppressed audit; narrowly apply AUTH-005 in synthetic development."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_inputs(root):
    paths = [root / name for name in ('web/package.json', 'web/package-lock.json', 'web/vite.config.ts',
             'web/index.html', '.github/workflows/dependencies.yml', 'tools/check_npm_audit.py')]
    paths += sorted((root / 'web/src').rglob('*'))
    require(all(not p.is_symlink() for p in paths), 'Source symlink is outside the review')
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def validate(report, returncode, policy, root, scope, now=None):
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
    require(start.tzinfo is not None and end.tzinfo is not None and start <= now < end and (end-start).total_seconds() <= 3*86400, 'Review expired or invalid')
    require(policy.get('source_inputs') == source_inputs(root), 'Reviewed source or lock changed')
    require(vulns == policy.get('reviewed_vulnerabilities'), 'New or changed audit finding')
    require(counts == policy.get('reviewed_counts'), 'Audit severity or counts changed')
    lock = json.loads((root / 'web/package-lock.json').read_text())['packages']
    require(set(vulns) == {'fdir', 'picomatch', 'tinyglobby', 'vite'}, 'Unexpected dependency chain')
    for name, finding in vulns.items():
        require(finding.get('name') == name and finding.get('severity') == 'high', 'Finding identity changed')
        for node in finding.get('nodes', []):
            require(lock.get(node, {}).get('version') == policy['versions'].get(name), 'Affected version changed')
    return {'status': 'pass_with_temporary_development_exception', 'exceptions': len(vulns),
            'expires_at_utc': policy['expires_at_utc'], 'authority': 'AUTH-005'}


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
        receipt = validate(report, result.returncode, policy, ROOT, args.scope)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        receipt = {'status': 'fail', 'reason': str(exc)}
    receipt['raw_report_sha256'] = hashlib.sha256(result.stdout.encode()).hexdigest()
    (output / 'web-audit-policy.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return 1 if receipt['status'] == 'fail' else 0


if __name__ == '__main__':
    raise SystemExit(main())
