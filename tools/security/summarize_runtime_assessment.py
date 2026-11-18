"""AUTH-006 static evidence summary; never approves or executes an image."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,os


def main():
    root=Path('work/runtime-assessment')
    sbom=json.loads((root/'sbom.json').read_text())
    report=json.loads((root/'advisories.json').read_text())
    matches=report['matches']
    counts=Counter(m['vulnerability']['severity'].lower() for m in matches)
    selected=[{'name':a['name'],'version':a['version'],'licenses':a.get('licenses',[])}
              for a in sbom['artifacts'] if a['name'] in {'openssl','libssl3','libssl3t64','gosu','postgresql-17','postgresql-common'}]
    result={'status':'not_qualified_for_use','reason':'Static evidence only; unchanged gate and compatibility/rights review still required',
            'candidate':os.environ['CANDIDATE_NAME'],'reference':os.environ['CANDIDATE_REF'],
            'created_at_utc':datetime.now(timezone.utc).isoformat(),'distro':sbom.get('distro'),
            'packages':len(sbom['artifacts']),'findings':len(matches),'severity_counts':dict(counts),
            'selected_packages':selected,
            'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'sbom.json',root/'advisories.json']},
            'image_executed':False,'runtime_pin_changed':False}
    (root/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
