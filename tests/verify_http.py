from pathlib import Path
import json,re,sys,time,zipfile,io
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from backend.catalog import ROOT
c=httpx.Client(base_url='http://127.0.0.1:8765',headers={'X-Control-Lab':'1'},timeout=240)
checks=[]
index=c.get('/');assert index.status_code==200
for path in re.findall(r'(?:src|href)="([^"]+\.(?:js|css))"',index.text):
    response=c.get(path);assert response.status_code==200,(path,response.status_code)
checks.append({'check':'html and built static assets','status':'passed'})
catalog=c.get('/api/catalog').json()
assert len(catalog)==6
for lab in catalog:
    for file in lab['files']:
        assert c.get(file['url']).status_code==200,file['name']
checks.append({'check':'all 51 original files downloadable','status':'passed'})
saved=[]
for engine in ['matlab','simulink']:
    r=c.post('/api/run',json={'lab_id':6,'task_id':'lead2','engine':engine,'stop_time':5})
    assert r.status_code==200,(engine,r.text)
    run=r.json();assert run['engine']==engine and run['transport']=='MATLAB Engine API for Python'
    assert all(run['checks'].values()),run['metrics']
    saved.append(run)
    if engine=='simulink':assert c.get('/api/runs/'+run['id']+'/model.slx').status_code==200
    print('PASS HTTP',engine,run['elapsed'],run['metrics'],flush=True)
    checks.append({'check':engine+' HTTP endpoint','run_id':run['id'],'status':'passed','metrics':run['metrics']})
model_file=str(ROOT/'runtime'/saved[-1]['id']/'model.slx').replace("'","''")
code_text="clear; clc; close all; s=tf('s'); sys=1/(s+1); disp(dcgain(sys)); figure; step(sys);"
code_text+=f"\nh=load_system('{model_file}'); mdl=get_param(h,'Name'); out=sim(mdl); yy=out.get('web_output'); assert(numel(yy.Data)>1000); fprintf('SLX_SELF_CONTAINED_OK\\n'); close_system(mdl,0);"
code=c.post('/api/code/run',json={'code':code_text})
assert code.status_code==200,code.text
assert code.json()['images'] and '1' in code.json()['console']
assert 'SLX_SELF_CONTAINED_OK' in code.json()['console']
assert c.get(code.json()['images'][0]).status_code==200
checks.append({'check':'edited MATLAB code HTTP endpoint and actual figure','status':'passed'})
checks.append({'check':'downloadable SLX runs with embedded input in a fresh MATLAB workspace','status':'passed'})
print('PASS HTTP MATLAB code',flush=True)
ids=[r['id'] for r in saved]
report=c.post('/api/report',json={'run_ids':ids,'format':'html','student':{'name':'杨开元','student_id':'24345063'},'analysis':'本次对比使用相同系数与 5 s 仿真窗口。MATLAB lsim 和 Simulink ode45 的响应及实际指标一致，符合两级超前校正的理论预期。'})
assert report.status_code==200,report.text
assert report.text.count('<section>')==2
assert 'katex.render' in report.text and 'data:image/png;base64' in report.text
assert 'MATLAB 真实运行' in report.text and 'Simulink 真实仿真' in report.text
(ROOT/'docs'/'示例报告-两级超前校正.html').write_bytes(report.content)
bundle=c.post('/api/report',json={'run_ids':ids,'format':'zip'})
assert bundle.status_code==200
z=zipfile.ZipFile(io.BytesIO(bundle.content));assert 'runs.json' in z.namelist()
(ROOT/'docs'/'示例报告-复现包.zip').write_bytes(bundle.content)
checks.append({'check':'combined offline HTML and reproducibility ZIP','status':'passed'})
(ROOT/'docs'/'http-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('ALL HTTP CHECKS PASSED',flush=True)
