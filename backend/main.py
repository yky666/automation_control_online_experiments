from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,math,os,time,uuid
import contextvars,secrets
from typing import Literal
import numpy as np
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import FileResponse,Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field,model_validator
from .catalog import ROOT,get_catalog,get_task
from .numerics import build_model,simulate_preview,matlab_code,simulink_code,calculate_metrics
from .providers import status as native_status,execute
from .reporting import report_bytes,csv_data

RUNTIME=ROOT/'runtime';RUNTIME.mkdir(exist_ok=True)
app=FastAPI(title='Control Lab Student Platform',version='2.3.0')
OWNER=contextvars.ContextVar('owner',default=None)

@app.middleware('http')
async def local_api_guard(request:Request,call_next):
    if request.method in ('POST','PUT','DELETE'):
        origin=request.headers.get('origin')
        from urllib.parse import urlparse
        allowed={'http://127.0.0.1:8765','http://localhost:8765','http://127.0.0.1:5173','http://localhost:5173'}|set(os.getenv('CONTROL_LAB_ALLOWED_ORIGINS','').split(','))
        same_origin=origin and urlparse(origin).netloc==request.headers.get('host') and urlparse(origin).scheme in ('http','https')
        if origin and origin not in allowed and not same_origin:return Response('来源不允许',status_code=403)
        if request.headers.get('x-control-lab')!='1':return Response('需要 X-Control-Lab: 1 请求头',status_code=403)
    owner=None
    if os.getenv('CONTROL_LAB_SESSION_ISOLATION','0')=='1':
        owner=request.cookies.get('control_lab_session')
        if not owner or len(owner)!=48 or any(c not in '0123456789abcdef' for c in owner):owner=secrets.token_hex(24)
    context=OWNER.set(owner)
    try:
        response=await call_next(request)
        if owner:response.set_cookie('control_lab_session',owner,httponly=True,samesite='lax',secure=request.url.scheme=='https',max_age=86400*30)
        return response
    finally:OWNER.reset(context)

class RunRequest(BaseModel):
    lab_id:int=Field(ge=1,le=6)
    task_id:str=Field(max_length=60)
    params:dict[str,float]=Field(default_factory=dict)
    engine:Literal['scipy','matlab','simulink']='scipy'
    stop_time:float=Field(default=5,gt=0,le=120)
    points:int=Field(default=1501,ge=201,le=10001)
    amplitude:float=Field(default=1,gt=0,le=100)
    input_signal:Literal['step','ramp','sine','step_ramp','polynomial']|None=None
    settling_threshold:Literal[0.02,0.05]=0.02
    numerator:list[float]|None=None
    denominator:list[float]|None=None
    solver:Literal['ode45','ode15s']='ode45'
    auto_duration:bool=True
    @model_validator(mode='after')
    def check(self):
        if not all(math.isfinite(v) for v in self.params.values()):raise ValueError('参数必须为有限数值')
        if self.params.get('frequency',1)<=0:raise ValueError('正弦频率必须大于零')
        if (self.numerator is None)!=(self.denominator is None):raise ValueError('分子和分母必须同时填写')
        if self.numerator is not None:
            if not 1<=len(self.numerator)<=12 or not 1<=len(self.denominator)<=12:raise ValueError('系数向量长度必须为 1～12')
            if not all(math.isfinite(v) for v in self.numerator+self.denominator) or self.denominator[0]==0:raise ValueError('系数必须有限，分母最高次系数不能为零')
        get_task(self.lab_id,self.task_id)
        return self

class CodeRequest(BaseModel):
    code:str=Field(min_length=1,max_length=40000)

class ScanRequest(BaseModel):
    request:RunRequest
    parameter:str
    values:list[float]=Field(min_length=2,max_length=8)

class ReportRequest(BaseModel):
    run_ids:list[str]=Field(min_length=1,max_length=24)
    format:Literal['html','markdown','json','zip']='html'
    student:dict[str,str]=Field(default_factory=dict)
    analysis:str=Field(default='',max_length=20000)

def stamp():return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
def save_run(run):
    if OWNER.get():run['owner']=OWNER.get()
    (RUNTIME/run['id']).mkdir(exist_ok=True)
    (RUNTIME/run['id']/'result.json').write_text(json.dumps(run,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    return run
def read_run(id):
    if not len(id)==12 or not all(c in '0123456789abcdef' for c in id):raise HTTPException(404,'运行记录不存在')
    f=RUNTIME/id/'result.json'
    if not f.exists():raise HTTPException(404,'运行记录不存在')
    run=json.loads(f.read_text(encoding='utf-8'))
    if OWNER.get() and run.get('owner')!=OWNER.get():raise HTTPException(404,'运行记录不存在')
    return run
def clean(v):
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
    if isinstance(v,list):return [clean(x) for x in v]
    if isinstance(v,float) and not math.isfinite(v):return None
    return v
def vector(v):return np.asarray(v,dtype=float).reshape(-1).tolist()

@app.get('/api/health')
def health():return dict(status='ok',version='2.3.0',application='control-lab-workbench',matlab=native_status(),capabilities={'platform':True,'native':native_status()},python=os.sys.version.split()[0],local_only=False)

@app.get('/api/catalog')
def catalog():return get_catalog()

@app.post('/api/code/template')
def code_template(req:RunRequest):
    try:m=build_model(req);return {'code':matlab_code(m),'simulink_code':simulink_code(m),'model':m}
    except ValueError as e:raise HTTPException(422,str(e))

@app.post('/api/run')
def run(req:RunRequest):
    start=time.perf_counter();id=uuid.uuid4().hex[:12];job=RUNTIME/id
    try:
        model=build_model(req);result=simulate_preview(model)
        if req.engine!='scipy':
            native=execute(dict(mode=req.engine,model=model,preview=result,job_id=id),job,experiment=req.model_dump())
            for key in ['time','input','output']:
                if key in native:native[key]=vector(native[key])
            if len(native['time'])!=len(native['output']) or len(native['time'])!=len(native['input']) or not np.isfinite(np.asarray(native['output'],dtype=float)).all():
                raise RuntimeError('真实仿真输出包含非有限值或采样长度不一致，请检查模型、参数和仿真窗口。')
            for key in ['poles','zeros']:
                if key in native:native[key]=np.asarray(native[key],dtype=float).reshape(-1,2).tolist()
            for key in ['w','magnitude','phase']:native['bode'][key]=vector(native['bode'][key])
            if native.get('baseline'):
                for k in ['y','magnitude','phase']:native['baseline'][k]=vector(native['baseline'][k])
            result.update(native)
            result['engine']=req.engine;result['engine_label']='Simulink 真实仿真' if req.engine=='simulink' else 'MATLAB 真实运行'
            result['metrics']=calculate_metrics(model['num'],model['den'],np.asarray(result['time']),np.asarray(result['output']),model['settling_threshold'],req.amplitude,model['input_signal'])
            if result.get('stepinfo'):
                result['metrics'].update(result.pop('stepinfo'))
                if result['metrics'].get('settling_time') and result['metrics']['settling_time']>=model['stop_time']:result['metrics']['settling_time']=None
            kv=model['design'].get('Kv')
            if kv and result['metrics']['stability']=='stable':result['metrics']['ramp_error']=1/kv
            if result['metrics']['stability']=='stable' and 'ramp_error_theoretical' in model['design']:result['metrics']['ramp_error']=model['design']['ramp_error_theoretical']
            if 'requirements' in model['design']:result['checks']={k:result['metrics'].get(k) is not None and result['metrics'][k]<=v+1e-8 for k,v in model['design']['requirements'].items()}
            if model['task_id']=='lead1':result['checks']={'phase_margin':result['margins']['phase_margin'] is not None and result['margins']['phase_margin']>model['params']['targetPM'],'gain_margin_db':result['margins']['gain_margin_infinite'] or (result['margins']['gain_margin_db'] is not None and result['margins']['gain_margin_db']>10)}
            if model['task_id']=='lead_example2':result['checks']={'phase_margin':result['margins']['phase_margin'] is not None and result['margins']['phase_margin']>model['params']['targetPM']}
        result.update(id=id,created_at=stamp(),elapsed=round(time.perf_counter()-start,3),code=matlab_code(model))
        return save_run(clean(result))
    except ValueError as e:raise HTTPException(422,str(e))
    except RuntimeError as e:raise HTTPException(503,str(e))

@app.post('/api/preview')
def preview(req:RunRequest):
    try:
        model=build_model(req);result=simulate_preview(model)
        return clean(dict(result,code=matlab_code(model)))
    except ValueError as e:raise HTTPException(422,str(e))

@app.post('/api/code/run')
def code_run(req:CodeRequest):
    id=uuid.uuid4().hex[:12]
    try:
        result=execute(dict(mode='code',code=req.code,job_id=id),RUNTIME/id)
        return dict(result,id=id,images=[f'/api/code/{id}/image/{name}' for name in result['images']])
    except RuntimeError as e:raise HTTPException(503,str(e))

@app.get('/api/code/{id}/image/{name}')
def code_image(id:str,name:str):
    if not len(id)==12 or not all(c in '0123456789abcdef' for c in id) or not name.startswith('figure_') or not name.endswith('.png') or not name[7:-4].isdigit():raise HTTPException(404)
    f=RUNTIME/id/name
    if not f.is_file():raise HTTPException(404)
    return FileResponse(f)

@app.post('/api/scan')
def scan(req:ScanRequest):
    lab,_=get_task(req.request.lab_id,req.request.task_id)
    if req.parameter not in [f['key'] for f in lab['fields']]+['amplitude','stop_time']:raise HTTPException(422,'该参数不可扫描')
    requests=[]
    for v in req.values:
        update={req.parameter:v} if req.parameter in ('amplitude','stop_time') else {'params':dict(req.request.params,**{req.parameter:v})}
        try:r=RunRequest.model_validate(dict(req.request.model_dump(),**update))
        except ValueError as e:raise HTTPException(422,str(e))
        try:build_model(r)
        except ValueError as e:raise HTTPException(422,str(e))
        requests.append(r)
    return {'parameter':req.parameter,'runs':[run(r) for r in requests]}

@app.get('/api/runs')
def runs():
    all=[]
    for f in sorted(RUNTIME.glob('*/result.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:100]:
        r=json.loads(f.read_text(encoding='utf-8'))
        if OWNER.get() and r.get('owner')!=OWNER.get():continue
        all.append({k:r[k] for k in ['id','created_at','engine_label','elapsed','metrics','model']})
    return all

@app.get('/api/runs/{id}')
def get_run(id:str):return read_run(id)

@app.get('/api/runs/{id}/data.csv')
def data_csv(id:str):return Response(csv_data(read_run(id)),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="run_{id}.csv"'})

@app.get('/api/runs/{id}/measurements.csv')
def measurements_csv(id:str):
    import io
    data=read_run(id).get('measurements',[])
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=['f','w','magnitude','phase','output_amplitude']);w.writeheader();w.writerows(data)
    return Response('\ufeff'+s.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="measurements_{id}.csv"'})

@app.get('/api/runs/{id}/model.slx')
def model_slx(id:str):
    read_run(id);f=RUNTIME/id/'model.slx'
    if not f.exists():raise HTTPException(404,'此运行没有 Simulink 模型')
    return FileResponse(f,filename=f'control_lab_{id}.slx')

@app.get('/api/runs/{id}/model.png')
def model_png(id:str):
    read_run(id);f=RUNTIME/id/'model.png'
    if not f.exists():raise HTTPException(404,'模型图未生成')
    return FileResponse(f)

@app.post('/api/report')
def report(req:ReportRequest):
    results=[read_run(id) for id in dict.fromkeys(req.run_ids)]
    ext={'html':'html','markdown':'md','json':'json','zip':'zip'}[req.format]
    b=report_bytes(results,req.student,req.analysis,req.format)
    name=f'control_lab_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    dest=RUNTIME/'reports';dest.mkdir(exist_ok=True);(dest/name).write_bytes(b)
    return Response(b,media_type={'html':'text/html','markdown':'text/markdown','json':'application/json','zip':'application/zip'}[req.format],headers={'Content-Disposition':f'attachment; filename="{name}"'})

app.mount('/sources',StaticFiles(directory=ROOT/'sources'),name='originals')
if (ROOT/'dist').exists():app.mount('/',StaticFiles(directory=ROOT/'dist',html=True),name='website')
