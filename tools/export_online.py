"""Build public, non-personal course examples for static hosting and Online links."""
from pathlib import Path
import json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.catalog import get_catalog
from backend.main import RunRequest,clean
from backend.numerics import build_model,simulate_preview,matlab_code
from backend.reporting import report_bytes

def matlab_vector(v):return '['+' '.join(f'{x:.12g}' for x in v)+']'

def recipe(task):
    kind=task['kind'];close=False;checks=''
    if kind=='typical':
        nd={'p':('K','1'),'inertia':('K','[T 1]'),'integrator':('K','[T 0]'),'d':('[K*T 0]','[Tf 1]'),'pi':('[K*T K]','[T 0]'),'pd':('[K*(Tf+T) K]','[Tf 1]')}[task['id']]
        code=f'Gopen = tf({nd[0]},{nd[1]});'
    elif kind in ('second','zero'):
        code=f"Gopen = tf({'[wn^2/zero wn^2]' if kind=='zero' else 'wn^2'},[1 2*zeta*wn wn^2]);"
    elif kind=='bandwidth':code='Gopen = tf(K,[K/(2*pi*GBW) 1]);'
    elif kind=='frequency_inertia':code='Gopen = tf(K,[T 1]);'
    elif kind in ('stability','reduced'):
        code="Gopen = tf(10*K,conv([1 0],[T1 1]));";close=True
        if kind=='stability':code="Gopen = tf(10*K,conv([1 0],conv([T1 1],[T2 1])));\nKcr=(T1+T2)/(10*T1*T2); disp(Kcr);"
    elif kind.startswith('lead'):
        d={'lead1':'tf(2*Kv,[1 2 0])','lead_example1':'tf(K,conv([1 0],conv([0.1 1],[0.001 1])))','lead2':'tf(K,conv([1 0],conv([0.5 1],[1/30 1])))','lead_example2':'tf(K,[0.2 1 0 0])'}[kind]
        code='G0 = '+d+';\n'
        if kind in ('lead1','lead_example1'):
            code+="[~,PM0]=margin(G0);\nphi=targetPM-PM0+reserve;\nassert(phi>0 && phi<85,'所需超前角需在 0~85 度内');\nalpha=(1+sind(phi))/(1-sind(phi));\nwm=exp(fzero(@(x) 20*log10(abs(evalfr(G0,1i*exp(x))))+10*log10(alpha),[-16 22]));\nstages=1;\n"
        else:code+='stages=2;\n'
        code+='wz=wm/sqrt(alpha); wp=wm*sqrt(alpha);\nGc=tf([1/wz 1],[1/wp 1]);\nGopen=G0*Gc^stages;\n'
        close=True
        if kind in ('lead2','lead_example2'):checks="if isproper(sys) && isstable(sys)\n    info=stepinfo(sys);\n    disp(struct('overshoot_pass',info.Overshoot<=MpReq,'settling_pass',info.SettlingTime<=tsReq));\n    ess="+('1/K' if kind=='lead2' else '0')+"; disp(struct('ramp_error',ess,'ramp_error_pass',ess<=essReq));\nend"
    else:
        gain='K*' if kind in ('feedback','dynamic_feedback') else ''
        code=f"Gopen = tf({gain}{matlab_vector(task['num'])},{matlab_vector(task['den'])});";close=bool(gain)
    code+='\nsys = '+('feedback(Gopen,tf(1,[1 1]));\nGopen=Gopen*tf(1,[1 1]);' if kind=='dynamic_feedback' else 'feedback(Gopen,1);' if close else 'Gopen;')
    return code,checks

def is_public_file(name):return '杨开元' not in name and '实验报告' not in name

def export():
    dest=ROOT/'public'/'course';dest.mkdir(parents=True,exist_ok=True)
    examples=dest/'examples';examples.mkdir(exist_ok=True)
    reports=dest/'reports';reports.mkdir(exist_ok=True)
    online=ROOT/'matlab'/'online';online.mkdir(exist_ok=True)
    catalog=get_catalog()
    for lab in catalog:
        lab['files']=[f for f in lab['files'] if is_public_file(f['name'])]
        for task in lab['tasks']:
            req=RunRequest(lab_id=lab['id'],task_id=task['id'],params=task['defaults'],stop_time=4 if lab['id']==4 else 5)
            m=build_model(req);r=clean(simulate_preview(m))
            r.update(engine_label='默认参数结果示例（预计算 · SciPy）',example=True,matlab_recipe=recipe(task)[0],matlab_checks=recipe(task)[1],parameter_bounds={f['key']:[f['min'],f['max']] for f in lab['fields']})
            key=f"{lab['id']}_{task['id']}"
            (examples/(key+'.json')).write_text(json.dumps(r,ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8')
            # Full reports contain only example data and no saved student identity.
            rr=dict(r,code=matlab_code(m),id='example',created_at='预计算示例',elapsed=0)
            report=report_bytes([rr],{},'本报告为默认参数示例，不能作为个人实际实验运行记录。','html').decode('utf-8')
            report=report.replace('自动控制实验报告','自动控制实验示例报告').replace('次已完成运行','组默认参数示例').replace('本报告依据保存的运行记录生成。不同引擎和工况分别标记；个人分析由填写内容保留。','本报告使用默认参数预计算示例。实际实验需要在自己的 MATLAB 会话执行，并记录运行结果。')
            (reports/(key+'.html')).write_text(report,encoding='utf-8')
    (dest/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    # Vite copies public assets. Original report submissions are excluded.
    public_sources=(ROOT/'public'/'sources').resolve()
    assert public_sources==ROOT.resolve()/'public'/'sources', 'Unexpected generated resource path'
    if public_sources.exists():shutil.rmtree(public_sources)
    selected=[ROOT/f['url'].lstrip('/') for lab in catalog for f in lab['files']]
    selected+=list((ROOT/'sources'/'figures').glob('*.png'))
    for source in selected:
        target=public_sources/source.relative_to(ROOT/'sources');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    print(f'Exported {sum(len(l["tasks"]) for l in catalog)} public examples')

if __name__=='__main__':export()
