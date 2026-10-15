"""Deploy only on a licensed server. No arbitrary-code endpoint is exposed."""
import base64,hmac,os,threading,uuid
from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel
from .main import RunRequest
from .catalog import ROOT
from .numerics import build_model,simulate_preview
from . import native

app=FastAPI(title='Control Lab licensed MATLAB worker',docs_url=None,redoc_url=None)
BUSY=threading.Lock()
class WorkRequest(BaseModel):
    experiment:RunRequest

def authorize(header):
    token=os.getenv('CONTROL_LAB_WORKER_TOKEN','')
    if not token:raise HTTPException(503,'工作节点尚未配置访问令牌')
    if not hmac.compare_digest(header or '', 'Bearer '+token):raise HTTPException(401,'身份验证失败')

@app.post('/v1/run')
def run(request:WorkRequest,authorization:str|None=Header(default=None)):
    authorize(authorization)
    r=request.experiment
    if r.engine not in ('matlab','simulink'):raise HTTPException(422,'工作节点只执行 MATLAB 或 Simulink 实验')
    if not BUSY.acquire(blocking=False):raise HTTPException(429,'计算节点正在运行实验，请稍后重试')
    try:
        model=build_model(r);preview=simulate_preview(model)
        id=uuid.uuid4().hex[:12];folder=ROOT/'runtime'/'worker'/id
        result=native.execute(dict(mode=r.engine,model=model,preview=preview,job_id=id),folder)
        result['files']={name:base64.b64encode((folder/name).read_bytes()).decode('ascii') for name in ('model.slx','model.png') if (folder/name).exists()}
        return result
    except (ValueError,RuntimeError) as exc:raise HTTPException(503,str(exc))
    finally:BUSY.release()
