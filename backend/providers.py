"""Student platform is MATLAB-free. Native calculations are optional server services."""
import base64,os,re
from urllib.parse import urlparse
import httpx
from . import native

def status():
    url=os.getenv('CONTROL_LAB_MATLAB_URL','').rstrip('/')
    token=os.getenv('CONTROL_LAB_WORKER_TOKEN','')
    local=os.getenv('CONTROL_LAB_ENABLE_LOCAL_MATLAB','0')=='1'
    detected=native.available() if local else {'engine_api':False,'executable':False,'transport':None}
    return dict(ready=bool(url and token) or (local and (detected['engine_api'] or detected['executable'])),
        configured=bool(url),mode='remote' if url else 'local' if local else 'online',
        code_execution=local and bool(detected['engine_api'] or detected['executable']),
        label='云端 MATLAB 服务' if url else '本机教师调试' if local else 'MATLAB Online',
        online_url='https://matlab.mathworks.com/',**detected)

def execute(req,job_dir,experiment=None):
    config=status()
    if config['mode']=='remote':
        if req['mode']=='code':raise RuntimeError('共享计算服务只执行参数化实验。自由 MATLAB 脚本请在 MATLAB Online 的个人会话中运行。')
        url=os.environ['CONTROL_LAB_MATLAB_URL'].rstrip('/')
        if urlparse(url).scheme not in ('http','https'):raise RuntimeError('云端接口地址必须使用 http 或 https')
        token=os.getenv('CONTROL_LAB_WORKER_TOKEN','')
        if not token:raise RuntimeError('云端计算服务尚未配置访问令牌')
        try:
            response=httpx.post(url+'/v1/run',json={'experiment':experiment},headers={'Authorization':'Bearer '+token},timeout=210,follow_redirects=False)
            response.raise_for_status();result=response.json()
        except (httpx.HTTPError,ValueError) as exc:raise RuntimeError('云端 MATLAB 服务调用失败，请检查服务地址、许可和访问令牌。') from exc
        job_dir.mkdir(parents=True,exist_ok=True)
        for name,data in result.pop('files',{}).items():
            if name not in ('model.slx','model.png'):raise RuntimeError('云端返回了不支持的文件')
            try:decoded=base64.b64decode(data,validate=True)
            except ValueError as exc:raise RuntimeError('云端文件编码无效') from exc
            if len(decoded)>20*1024*1024:raise RuntimeError('云端模型文件超过大小限制')
            (job_dir/name).write_bytes(decoded)
        result['transport']='云端 MATLAB 计算服务（HTTPS/HTTP）'
        return result
    if config['mode']=='local':return native.execute(req,job_dir)
    raise RuntimeError('学生版不调用本机 MATLAB。可直接运行平台实验；自由代码使用 MATLAB Online。管理员接入云端计算服务后可启用 MATLAB/Simulink 一键调用。')
