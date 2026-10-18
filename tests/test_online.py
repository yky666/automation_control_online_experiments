import json
from pathlib import Path
from tools.export_online import is_public_file,recipe
ROOT=Path(__file__).resolve().parents[1]

def test_all_static_tasks_and_links_are_complete():
    catalog=json.loads((ROOT/'public/course/catalog.json').read_text(encoding='utf-8'))
    assert len(catalog)==6
    assert sum(len(lab['tasks']) for lab in catalog)==38
    for lab in catalog:
        for task in lab['tasks']:
            key=f"{lab['id']}_{task['id']}"
            example=json.loads((ROOT/f'public/course/examples/{key}.json').read_text(encoding='utf-8'))
            assert example['example'] and not example.get('id') and not example.get('owner')
            assert example['matlab_recipe']==recipe(task)[0]
            if task['id']!='residue1':
                assert task['native_model']
                assert (ROOT/'public'/task['native_model']['download'].lstrip('/')).is_file()
                assert (ROOT/task['native_model']['online_file']).is_file()
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


def test_physical_downloads_are_real_models_with_successful_native_evidence():
    from zipfile import ZipFile
    evidence=json.loads((ROOT/'docs/physical-model-verification.json').read_text(encoding='utf-8'))
    assert len(evidence)==18 and all(item['passed'] for item in evidence)
    for item in evidence:
        source=ROOT/'matlab/physical'/(item['name']+'.slx')
        public=ROOT/'public/physical'/source.name
        assert source.read_bytes()==public.read_bytes()
        with ZipFile(source) as model:
            assert 'simulink/blockdiagram.xml' in model.namelist()
            xml=b' '.join(model.read(name) for name in model.namelist() if name.endswith('.xml'))
            assert b'fl_lib' in xml and b'physical_input' in xml

def test_course_pages_presets_and_original_model_corrections():
    from backend.catalog import get_catalog
    from backend.main import RunRequest,preview
    catalog=get_catalog()
    assert all(lab['coursework']['pages'] and lab['coursework']['required'] for lab in catalog)
    damping=next(t for t in catalog[2]['tasks'] if t['id']=='damping_sweep')
    assert [p['params']['zeta'] for p in damping['presets']]==[0,.25,.5,.75,1,1.25]
    assert len(next(t for t in catalog[2]['tasks'] if t['id']=='zero')['presets'])==4
    assert next(f for f in catalog[1]['fields'] if f['key']=='T')['max']>=10
    result=preview(RunRequest(lab_id=6,task_id='lead_example2'))
    assert result['model']['design']['Ka']==10
    assert 'requirements' not in result['model']['design']
    assert set(result['checks'])=={'phase_margin'}
