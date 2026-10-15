from pathlib import Path
import json,os,shutil,subprocess,sys,threading,time
import importlib.util
from .catalog import ROOT

LOCK=threading.Lock()
MATLAB_EXE=os.getenv('MATLAB_EXECUTABLE') or shutil.which('matlab') or ''
def available():
    try:engine=importlib.util.find_spec('matlab.engine') is not None
    except ModuleNotFoundError:engine=False
    return {'engine_api':engine,'executable':bool(MATLAB_EXE),'transport':'MATLAB Engine API for Python' if engine else 'MATLAB -batch' if MATLAB_EXE else None}

def execute(req,job_dir,timeout=180):
    job_dir.mkdir(parents=True,exist_ok=True)
    request_file=job_dir/'request.json';out=job_dir/'native.json';log=job_dir/'matlab.log'
    req=dict(req,job_dir=str(job_dir));request_file.write_text(json.dumps(req,ensure_ascii=False),encoding='utf-8')
    status=available()
    if not status['executable'] and not status['engine_api']:raise RuntimeError('未检测到 MATLAB；请在本机安装 MATLAB，并配置 MATLAB_EXECUTABLE。')
    if status['engine_api']:cmd=[sys.executable,str(ROOT/'backend'/'matlab_worker.py'),str(request_file),str(out)]
    else:
        q=lambda p:str(p).replace("'","''")
        batch=f"addpath('{q(ROOT/'matlab')}'); req=fileread('{q(request_file)}'); response=labweb_run(req); fid=fopen('{q(out)}','w','n','UTF-8'); fprintf(fid,'%s',response); fclose(fid);"
        cmd=[MATLAB_EXE,'-batch',batch]
    with LOCK:
        with log.open('w',encoding='utf-8') as stream:
            proc=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            try:proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                import psutil
                try:
                    children=psutil.Process(proc.pid).children(recursive=True)
                    for child in children:child.kill()
                except psutil.NoSuchProcess:pass
                proc.kill();proc.wait()
                raise RuntimeError(f'MATLAB 超过 {timeout} 秒，已终止本次工作进程；请检查代码是否包含无限循环。')
    if proc.returncode or not out.exists():
        detail=log.read_text(encoding='utf-8',errors='replace')[-2500:]
        raise RuntimeError('MATLAB 运行失败：\n'+detail)
    result=json.loads(out.read_text(encoding='utf-8'))
    result['transport']=status['transport']
    return result
