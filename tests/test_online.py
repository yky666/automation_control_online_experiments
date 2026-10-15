import json
from pathlib import Path
from tools.export_online import is_public_file,recipe
ROOT=Path(__file__).resolve().parents[1]

def test_all_static_tasks_and_links_are_complete():
    catalog=json.loads((ROOT/'public/course/catalog.json').read_text(encoding='utf-8'))
    assert len(catalog)==6
    assert sum(len(lab['tasks']) for lab in catalog)==33
    for lab in catalog:
        for task in lab['tasks']:
            key=f"{lab['id']}_{task['id']}"
            example=json.loads((ROOT/f'public/course/examples/{key}.json').read_text(encoding='utf-8'))
            assert example['example'] and not example.get('id') and not example.get('owner')
            assert example['matlab_recipe']==recipe(task)[0]
            for suffix in ('','_simulink'):
                script=(ROOT/f'matlab/online/lab{key}{suffix}.m').read_text(encoding='utf-8')
                assert 'sys =' in script and '实际结果由你' in script
                assert '实验报告' not in script
            report=(ROOT/f'public/course/reports/{key}.html').read_text(encoding='utf-8')
            assert '默认参数示例' in report and 'data:image/png;base64,' in report
        for f in lab['files']:
            assert is_public_file(f['name'])
            assert (ROOT/'public'/f['url'].lstrip('/')).is_file()

def test_static_export_excludes_submitted_reports():
    assert not is_public_file('实验一+杨开元.pdf')
    assert not is_public_file('自动控制实验报告.docx')
    assert not list((ROOT/'public/sources').rglob('*杨开元*'))
