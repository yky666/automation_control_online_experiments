import base64,json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import providers,native

HEADERS={'X-Control-Lab':'1'}
BODY={'lab_id':3,'task_id':'second','engine':'scipy'}

def test_student_mode_never_needs_local_matlab(monkeypatch):
    monkeypatch.delenv('CONTROL_LAB_MATLAB_URL',raising=False)
    monkeypatch.setenv('CONTROL_LAB_ENABLE_LOCAL_MATLAB','0')
    def forbidden(*args,**kwargs):raise AssertionError('Student computation touched local MATLAB')
    monkeypatch.setattr(native,'available',forbidden);monkeypatch.setattr(native,'execute',forbidden)
    client=TestClient(app)
    assert client.get('/api/health').json()['capabilities']['native']['ready'] is False
    assert client.post('/api/run',json=BODY,headers=HEADERS).status_code==200
    assert client.post('/api/run',json={**BODY,'engine':'matlab'},headers=HEADERS).status_code==503
    assert client.post('/api/code/run',json={'code':'disp(1)'},headers=HEADERS).status_code==503

def test_same_origin_hosted_platform(monkeypatch):
    monkeypatch.setenv('CONTROL_LAB_ENABLE_LOCAL_MATLAB','0')
    client=TestClient(app,base_url='https://lab.school.example')
    assert client.post('/api/preview',json=BODY,headers={**HEADERS,'Origin':'https://lab.school.example'}).status_code==200
    assert client.post('/api/preview',json=BODY,headers={**HEADERS,'Origin':'https://foreign.example'}).status_code==403

def test_cloud_student_records_are_isolated(monkeypatch):
    monkeypatch.setenv('CONTROL_LAB_SESSION_ISOLATION','1')
    first=TestClient(app);second=TestClient(app)
    saved=first.post('/api/run',json=BODY,headers=HEADERS).json()
    assert first.get('/api/runs/'+saved['id']).status_code==200
    assert second.get('/api/runs/'+saved['id']).status_code==404
    assert second.post('/api/report',json={'run_ids':[saved['id']]},headers=HEADERS).status_code==404
    assert saved['id'] not in [r['id'] for r in second.get('/api/runs').json()]

def test_parameter_editing_and_global_scan():
    client=TestClient(app)
    a=client.post('/api/preview',json={'lab_id':3,'task_id':'task3','params':{'K':1}},headers=HEADERS).json()
    b=client.post('/api/preview',json={'lab_id':3,'task_id':'task3','params':{'K':2}},headers=HEADERS).json()
    assert a['model']['den']!=b['model']['den']
    custom=client.post('/api/preview',json={**BODY,'numerator':[2],'denominator':[1,1]},headers=HEADERS).json()
    assert custom['metrics']['steady_state']==2
    scan=client.post('/api/scan',json={'request':BODY,'parameter':'amplitude','values':[1,2]},headers=HEADERS).json()
    assert scan['runs'][1]['metrics']['steady_state']==2*scan['runs'][0]['metrics']['steady_state']

def test_manual_sine_duration_and_online_model_script():
    client=TestClient(app)
    r=client.post('/api/preview',json={'lab_id':5,'task_id':'frequency_inertia','stop_time':.01,'auto_duration':False},headers=HEADERS).json()
    assert r['model']['stop_time']==.01
    script=client.post('/api/code/template',json=BODY,headers=HEADERS).json()['simulink_code']
    assert "new_system(mdl)" in script and "out=sim(mdl)" in script and "assignin(wks,'web_input'" in script

def test_remote_adapter_protocol_and_no_arbitrary_code(monkeypatch,tmp_path):
    monkeypatch.setenv('CONTROL_LAB_MATLAB_URL','https://worker.school.example')
    monkeypatch.setenv('CONTROL_LAB_WORKER_TOKEN','test-only-token')
    class Response:
        def raise_for_status(self):pass
        def json(self):return {'version':'test worker fixture','output':[0,1],'files':{'model.slx':base64.b64encode(b'fixture-model').decode()}}
    def fake_post(url,**kw):
        assert url=='https://worker.school.example/v1/run'
        assert kw['headers']['Authorization']=='Bearer test-only-token'
        assert kw['json']=={'experiment':BODY}
        return Response()
    monkeypatch.setattr(providers.httpx,'post',fake_post)
    result=providers.execute({'mode':'matlab'},tmp_path,experiment=BODY)
    assert '云端' in result['transport'] and (tmp_path/'model.slx').read_bytes()==b'fixture-model'
    with pytest.raises(RuntimeError,match='自由 MATLAB'):providers.execute({'mode':'code'},tmp_path)

def test_worker_requires_auth_and_validates_experiment(monkeypatch):
    from backend.cloud_worker import app as worker
    monkeypatch.setenv('CONTROL_LAB_WORKER_TOKEN','test-only-token')
    client=TestClient(worker)
    payload={'experiment':{**BODY,'engine':'matlab'}}
    assert client.post('/v1/run',json=payload).status_code==401
    assert client.post('/v1/run',json={'experiment':{**BODY,'engine':'matlab','solver':'malicious'}},headers={'Authorization':'Bearer test-only-token'}).status_code==422
