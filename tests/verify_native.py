"""One genuine MATLAB Engine session verifies the six chapters and Simulink."""
from pathlib import Path
import json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.catalog import ROOT
from backend.main import RunRequest
from backend.numerics import build_model,simulate_preview
import matlab.engine

checks=[];eng=matlab.engine.start_matlab('-nodesktop -nosplash')
eng.addpath(str(ROOT/'matlab'),nargout=0)
print('MATLAB',eng.version(),flush=True)
try:
    cases=[(1,'feedback'),(1,'residue1'),(2,'inertia'),(3,'second'),(4,'stability1'),(5,'frequency_inertia'),(6,'lead1'),(6,'lead2')]
    for i,(lab,task) in enumerate(cases):
        m=build_model(RunRequest(lab_id=lab,task_id=task));preview=simulate_preview(m)
        job=ROOT/'runtime'/f'qa_native_{i}';job.mkdir(exist_ok=True)
        native=json.loads(eng.labweb_run(json.dumps(dict(mode='matlab',model=m,preview=preview,job_dir=str(job),job_id=f'qa{i}')),nargout=1))
        y=np.asarray(native['output']).reshape(-1);expected=np.asarray(preview['output'])
        error=float(np.max(abs(y-expected))) if y.size else 0
        assert error<1e-7,(lab,task,error)
        if native['margins']['phase_margin'] is not None and preview['margins']['phase_margin'] is not None:
            assert abs(native['margins']['phase_margin']-preview['margins']['phase_margin'])<.01
        checks.append(dict(lab=lab,task=task,mode='matlab',max_error=error,version=native['version']))
        print('PASS MATLAB',lab,task,error,flush=True)
    for i,task in enumerate(['p','inertia','integrator','d','pi','pd']):
        m=build_model(RunRequest(lab_id=2,task_id=task,stop_time=2));preview=simulate_preview(m)
        job=ROOT/'runtime'/f'qa_simulink_{i}';job.mkdir(exist_ok=True)
        native=json.loads(eng.labweb_run(json.dumps(dict(mode='simulink',model=m,preview=preview,job_dir=str(job),job_id=f'qas{i}')),nargout=1))
        error=float(np.max(abs(np.asarray(native['output']).reshape(-1)-preview['output'])))
        assert error<.0002,(task,error)
        assert (job/'model.slx').exists()
        checks.append(dict(lab=2,task=task,mode='simulink',max_error=error,version=native['version']))
        print('PASS SIMULINK',task,error,flush=True)
    job=ROOT/'runtime'/'qa_code';job.mkdir(exist_ok=True)
    code="clear; clc; close all; s=tf('s'); G=1/(s+1); disp(dcgain(G)); figure; step(G); grid on;"
    native=json.loads(eng.labweb_run(json.dumps(dict(mode='code',code=code,job_dir=str(job),job_id='qacode')),nargout=1))
    assert '1' in native['console'] and native['images']
    checks.append(dict(mode='code',images=native['images']))
    print('PASS MATLAB editable code',native['images'],flush=True)
finally:
    eng.quit()
    (ROOT/'docs'/'native-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
