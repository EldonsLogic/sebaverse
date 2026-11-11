"""Validate planning artifacts; no external calls or product execution."""
from pathlib import Path
import json,hashlib,re,math,os
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
def project_files(suffix):
 # Installed packages and scratch are not project-owned specifications.
 excluded={'.git','work','.venv','node_modules','.local','__pycache__'}
 for directory,dirs,files in os.walk(R):
  dirs[:]=[name for name in dirs if name not in excluded]
  for name in files:
   if name.endswith(suffix):yield Path(directory)/name

errors=[];warnings=[]
manifest=json.loads((R/'sources/research-manifest.json').read_text())
for row in manifest:
 p=R/row['path']
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('Research hash mismatch '+row['path'])
for folder,n in [('global-competitors',13),('open-source-audit',14)]:
 if len(list((R/'research'/folder).glob('*.md')))!=n:errors.append('Wrong research file count '+folder)
reqs=json.loads((R/'registers/requirements.json').read_text());ids={x['id'] for x in reqs}
if len(ids)!=len(reqs):errors.append('Duplicate requirement ID')
for r in reqs:
 for k in ['sources','priority','phase','acceptance_criteria','specification','status','owner','omission_disposition']:
  if not r.get(k):errors.append(f'{r["id"]} missing {k}')
 for d in r['dependencies']:
  if d not in ids:errors.append(f'{r["id"]} missing dependency {d}')
 if not (R/r['specification']).is_file():errors.append('Missing spec '+r['specification'])
# Requirements graph must remain acyclic.
graph={r['id']:r['dependencies'] for r in reqs};active=set();done=set()
def visit(k):
 if k in active:errors.append('Dependency cycle '+k);return
 if k in done:return
 active.add(k)
 for d in graph[k]:
  if d in graph:visit(d)
 active.remove(k);done.add(k)
for k in graph:visit(k)
for p in project_files('.json'):
 try:json.loads(p.read_text())
 except Exception as e:errors.append(f'Invalid JSON {p.relative_to(R)} {e}')
for p in project_files('.md'):
 text=p.read_text()
 if text.count('```')%2:errors.append('Unbalanced fence '+str(p.relative_to(R)))
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if target.startswith(('http:','https:','#','mailto:','codex:')):continue
  dest=target.split('#')[0]
  if dest and not (p.parent/dest).exists():
   msg=f'{p.relative_to(R)} -> {dest}'
   (warnings if 'research' in p.relative_to(R).parts else errors).append('Unresolved local link '+msg)
sc=json.loads((R/'economics/scenarios.json').read_text())
for k,v in [('text',.475),('cascade',5.575),('realtime',25.475)]:
 if not math.isclose(sc['per_active_learner_ai_usd'][k],v,abs_tol=1e-8):errors.append('Baseline arithmetic changed; update validation intentionally '+k)
if any(x['status']!='pending' for x in json.loads((R/'execution/gate-records.json').read_text())):warnings.append('Gate status changed; confirm approval provenance')
run_date=datetime.now(ZoneInfo('Africa/Cairo')).strftime('%d %B %Y')
report=f'# Artifact validation\n\nRun date: {run_date}. Status: {"PASS" if not errors else "FAIL"}.\n\n- {len(manifest)} preserved research/evidence files match SHA-256 manifest.\n- 13 global + 14 audit Markdown deliverables present.\n- {len(reqs)} unique requirement rows checked for required fields, specs and acyclic dependencies.\n- JSON, Markdown fences and local links checked.\n- Illustrative baseline text/cascade/realtime arithmetic reproduced.\n- Product implementation, provider benchmarks, accessibility, security and learning efficacy were not tested.\n- Historical GAP-001 remains open; passing artifacts do not establish full conversation completeness.\n\n'
report+='## Errors\n\n'+('\n'.join('- '+x for x in errors) or 'None.')+'\n\n## Warnings\n\n'+('\n'.join('- '+x for x in warnings) or 'None.')+'\n'
(R/'VALIDATION.md').write_text(report)
print(report)
if errors:raise SystemExit(1)
