"""Remove submitted-report entries from the public manifest; keep local files intact."""
import json
from pathlib import Path
from export_online import is_public_file
root=Path(__file__).resolve().parents[1]
p=root/'sources/manifest.json';data=json.loads(p.read_text(encoding='utf-8'))
for lab in data:lab['files']=[f for f in lab['files'] if is_public_file(f['name'])]
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
