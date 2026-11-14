"""Supplier-declared PostgreSQL core supplements OS catalog coverage explicitly."""
from pathlib import Path
import json
pin=json.loads(Path('infra/images.lock.json').read_text())['postgres']
platform=next(p for p in pin['platforms'] if p['platform']['architecture']=='amd64' and p['platform']['os']=='linux')
version=platform['version']
bom={'bomFormat':'CycloneDX','specVersion':'1.6','version':1,'components':[{'type':'application','bom-ref':'supplier-postgresql-'+version,'name':'postgresql','version':version,'cpe':'cpe:2.3:a:postgresql:postgresql:'+version+':*:*:*:*:*:*:*','licenses':[{'license':{'id':'PostgreSQL'}}],'externalReferences':[{'type':'distribution','url':pin['source']}],'properties':[{'name':'identification','value':'Supplier OCI annotation from exact pinned image; supplements (does not replace) actual OS/native package catalog'}]}]}
Path('work/f2-security/postgres-core.cdx.json').write_text(json.dumps(bom,indent=2)+'\n')
