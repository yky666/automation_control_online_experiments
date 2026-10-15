import json,math
import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.main import app,RunRequest
from backend.catalog import LABS
from backend.numerics import build_model,simulate_preview,matlab_code

def calc(lab,task,**kw):return simulate_preview(build_model(RunRequest(lab_id=lab,task_id=task,**kw)))

@pytest.mark.parametrize('lab,task',[(l['id'],t['id']) for l in LABS for t in l['tasks']])
def test_every_course_task(lab,task):
    r=calc(lab,task)
    assert np.isfinite(r['output']).all()
    assert len(r['bode']['w'])==len(r['bode']['magnitude'])
    assert matlab_code(r['model'])
    json.dumps(r,allow_nan=False)

def test_first_order_analytic():
    r=calc(2,'inertia',params={'K':-2,'T':0.1})
    np.testing.assert_allclose(r['output'],-2*(1-np.exp(-np.asarray(r['time'])/0.1)),atol=1e-10)
    assert r['metrics']['steady_state']==-2
    assert r['metrics']['overshoot']<1e-6

def test_integrator_and_pd():
    r=calc(2,'integrator',params={'K':-1,'T':0.2})
    np.testing.assert_allclose(r['output'],-5*np.asarray(r['time']),atol=1e-10)
    assert r['metrics']['settling_time'] is None
    pd=calc(2,'pd',params={'K':2,'T':0.1,'Tf':0.01})
    np.testing.assert_allclose(pd['output'],2+20*np.exp(-np.asarray(pd['time'])/0.01),atol=1e-9)

def test_second_order_metrics():
    r=calc(3,'second',params={'zeta':0.5,'wn':10},stop_time=4)
    assert abs(r['metrics']['overshoot']-100*math.exp(-math.pi*.5/math.sqrt(.75)))<.01
    assert abs(r['metrics']['peak_time']-math.pi/(10*math.sqrt(.75)))<.005
    assert r['metrics']['settling_time'] is not None
    short=calc(3,'second',params={'zeta':0.05,'wn':1},stop_time=.1)
    assert short['metrics']['steady_state']==1
    assert short['metrics']['settling_time'] is None

@pytest.mark.parametrize('task,k,state,kcr',[('stability1',1,'stable',2),('stability1',2,'marginal',2),('stability1',3,'unstable',2),('stability2',5,'stable',11),('stability2',11,'marginal',11),('stability2',17,'unstable',11)])
def test_routh_boundary(task,k,state,kcr):
    r=calc(4,task,params={'K':k})
    assert r['metrics']['stability']==state
    assert abs(r['model']['design']['Kcr']-kcr)<1e-8
    if state!='stable':assert r['metrics']['settling_time'] is None

def test_inertia_frequency_and_independent_fit():
    r=calc(5,'frequency_inertia',params={'frequency':1/(2*np.pi*.001)})
    fit=r['sine_fit']
    assert abs(fit['theoretical_gain']-1/math.sqrt(2))<1e-8
    assert abs(fit['phase']+45)<.02
    assert fit['relative_gain_error']<.001

def test_lead_design_requirements():
    r=calc(6,'lead1')
    assert r['metrics']['ramp_error']==.05
    assert all(r['checks'].values())
    r=calc(6,'lead2')
    assert all(r['checks'].values())
    assert r['model']['design']['stages']==2
    assert r['metrics']['ramp_error']==.1

def test_native_residue_direct_term():
    r=calc(1,'residue1')
    np.testing.assert_allclose(r['residue']['direct'],[1,-3,9])
    np.testing.assert_allclose(r['residue']['residues'],[[-27,0]])
    assert r['time']==[]

def test_api_snapshots_reports_and_validation():
    client=TestClient(app);headers={'X-Control-Lab':'1'}
    payload={'lab_id':3,'task_id':'second','params':{'zeta':.5,'wn':10}}
    assert client.get('/api/health').status_code==200
    assert client.post('/api/run',json=payload).status_code==403
    assert client.post('/api/run',json=payload,headers={**headers,'Origin':'https://example.org'}).status_code==403
    assert client.post('/api/run',json={**payload,'stop_time':0},headers=headers).status_code==422
    assert client.post('/api/run',json={**payload,'params':{'zeta':-.1}},headers=headers).status_code==422
    assert client.post('/api/run',json={**payload,'numerator':[1],'denominator':[0]},headers=headers).status_code==422
    preview=client.post('/api/preview',json=payload,headers=headers).json()
    assert 'id' not in preview
    run=client.post('/api/run',json=payload,headers=headers).json();id=run['id']
    assert client.get('/api/runs/'+id).json()['model']==run['model']
    assert client.get('/api/runs/'+id+'/data.csv').status_code==200
    report=client.post('/api/report',json={'run_ids':[id],'format':'markdown','student':{'name':'<script>alert(1)</script>'}},headers=headers)
    assert report.status_code==200 and '原理推导' in report.text
    assert client.post('/api/report',json={'run_ids':['not-a-run']},headers=headers).status_code==404
    scan=client.post('/api/scan',json={'request':payload,'parameter':'zeta','values':[.25,.5,.75]},headers=headers).json()
    assert len(scan['runs'])==3
    assert scan['runs'][0]['metrics']['overshoot']>scan['runs'][-1]['metrics']['overshoot']
