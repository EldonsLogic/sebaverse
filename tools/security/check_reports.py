"""Fail closed on incomplete native/SBOM coverage or high/critical advisories."""
from pathlib import Path
import argparse
import hashlib
import json
import sys


def findings(report):
    return report.get('matches', [])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory',default='work/f2-security')
    args=parser.parse_args();directory=Path(args.directory)
    errors=[];reports=[]
    try:
        kev=json.loads((directory/'kev.json').read_text())
        kev_ids={v['cveID'] for v in kev['vulnerabilities']}
        if not kev_ids:errors.append('KEV coverage missing')
        native=json.loads((directory/'system-native.json').read_text())
        sbom=json.loads((directory/'system-native-sbom.json').read_text())
        owners={(p['name'],p['version']) for p in native['owners']}
        cataloged={(a['name'],a['version']) for a in sbom.get('artifacts',[])}
        if not owners or not owners<=cataloged:errors.append('System-native package coverage incomplete: '+str(sorted(owners-cataloged)))
        for name in ['image-cves.json','system-native-cves.json','postgres-core-cves.json']:
            report=json.loads((directory/name).read_text());matches=findings(report)
            if not report.get('descriptor',{}).get('db',{}):errors.append(name+': scanner database metadata missing')
            known_exploited=[x for x in matches if ({x['vulnerability']['id']}|{r['id'] for r in x.get('relatedVulnerabilities',[])}) & kev_ids]
            if known_exploited:errors.append(name+': known-exploited advisories='+str(len(known_exploited)))
            blocking=[x for x in matches if x['vulnerability']['severity'].lower() in ['high','critical']]
            if blocking:errors.append(name+': unresolved high/critical advisories='+str(len(blocking)))
            reviews=json.loads(Path('infra/security-reviewed-findings.json').read_text()) if Path('infra/security-reviewed-findings.json').exists() else {'findings':[]}
            reviewed={(r['report'],r['id'],r['package'],r['version']) for r in reviews['findings'] if r.get('rationale') and r.get('source') and r.get('reviewer')}
            unreviewed=[x for x in matches if (name,x['vulnerability']['id'],x['artifact']['name'],x['artifact']['version']) not in reviewed]
            if unreviewed:errors.append(name+': findings require explicit review='+str(len(unreviewed)))
            reports.append({'file':name,'matches':len(matches),'blocking':len(blocking),'sha256':hashlib.sha256((directory/name).read_bytes()).hexdigest(),'database':report.get('descriptor',{}).get('db')})
        image=json.loads((directory/'image-sbom.json').read_text())
        if len(image.get('artifacts',[]))<5:errors.append('Image package identification is insufficient')
        if not native.get('libraries') or not native.get('owners') or any(not p.get('notice_sha256') for p in native.get('owners',[])):errors.append('Native provenance/notices incomplete')
        if native.get('status')!='identified' or any(not p.get('version') for p in native.get('owners',[])):errors.append('Unknown native package versions')
    except (OSError,ValueError,KeyError) as exc:errors.append('Missing/unreadable required native evidence: '+str(exc))
    pin=json.loads(Path('infra/images.lock.json').read_text())['postgres']
    output={'image_reference':pin['reference'],'policy':'No unresolved high/critical native/image advisories; actual identified native closure and notices required before PG execution','status':'fail' if errors else 'pass','errors':errors,'reports':reports,'scope':'Actual Linux system-libpq + pinned image + supplier PostgreSQL core only; no bundled-wheel/hostOS/redistribution/app-security certification'}
    (directory/'preuse-result.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
    return bool(errors)


if __name__=='__main__':sys.exit(main())
