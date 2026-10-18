"""Package only successfully simulated native course models; no source overwrites."""
from pathlib import Path
import json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend.catalog import get_catalog
data=json.loads((ROOT/'runtime/course-audit/native-structure-results.json').read_text(encoding='utf-8'))
expected=sum(len(lab['tasks']) for lab in get_catalog())
if len(data)!=expected or any(r['status']=='failed' for r in data):raise SystemExit('Native verification is incomplete or failed; refusing to publish models')
dest=ROOT/'matlab/models';dest.mkdir(exist_ok=True)
for result in data:
    if result['status']!='passed':continue
    key=result['file'].removeprefix('lab').removesuffix('_simulink.m')
    source=ROOT/'runtime/course-audit/models'/f'course_lab{key}.slx'
    if not source.is_file():raise SystemExit(f'Missing verified model {source.name}')
    shutil.copy2(source,dest/source.name)
evidence=ROOT/'docs/native-models';evidence.mkdir(exist_ok=True)
for source in (ROOT/'runtime/course-audit/models').glob('*.png'):shutil.copy2(source,evidence/source.name)
(ROOT/'docs/course-model-verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Packaged',sum(r['status']=='passed' for r in data),'verified native models')
