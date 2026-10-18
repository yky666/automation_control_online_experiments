"""Keep DOM fixtures aligned with the real course catalog and numerical API."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend.catalog import get_catalog
from backend.main import RunRequest,preview
catalog=get_catalog();results={}
for lab in catalog:
    for task in lab['tasks']:
        req=RunRequest(lab_id=lab['id'],task_id=task['id'],params=task['defaults'],amplitude=task['defaults'].get('A',1),stop_time=4 if lab['id']==4 else 5)
        results[f"{lab['id']}:{task['id']}"]=preview(req)
(ROOT/'docs/catalog-qa.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf-8')
(ROOT/'tests/ui-results.json').write_text(json.dumps(results,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('Updated',len(results),'DOM task fixtures')
