"""Reports use immutable stored runs, never data supplied by the browser."""
from io import BytesIO, StringIO
import base64,csv,html,json,re,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from .catalog import get_task,ROOT

plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','SimHei','Noto Sans CJK SC','Noto Sans CJK JP','DejaVu Sans'],'axes.unicode_minus':False,'font.size':10})
def esc(v):return html.escape(str(v))
def chart(run,kind):
    fig,ax=plt.subplots(figsize=(8,3.3),layout='constrained')
    if kind=='time':
        if len(run['time']):
            ax.plot(run['time'],run['output'],color='#247d78',label='输出')
            ax.plot(run['time'],run['input'],color='#96a5af',ls='--',label='输入')
            if 'baseline' in run:ax.plot(run['time'],run['baseline']['y'],color='#cc9360',label='校正前输出')
            ax.legend();ax.set(xlabel='时间 / s',ylabel='幅值',title=run['model']['task_name'])
        else:ax.text(.5,.5,'非真有理模型：仅做代数与频率分析',ha='center',va='center',transform=ax.transAxes)
    elif kind=='bode':
        ax.semilogx(run['bode']['w'],run['bode']['magnitude'],color='#247d78',label='当前模型')
        if 'baseline' in run:ax.semilogx(run['bode']['w'],run['baseline']['magnitude'],color='#cc9360',label='校正前')
        ax.set(xlabel='角频率 / (rad/s)',ylabel='幅值 / dB',title='频率响应');ax.legend()
    else:
        p=run['poles']
        if p:ax.scatter([v[0] for v in p],[v[1] for v in p],marker='x',color='#247d78',s=60)
        ax.axhline(0,color='#aebfc7',lw=.7);ax.axvline(0,color='#aebfc7',lw=.7);ax.set(xlabel='实部 / (1/s)',ylabel='虚部 / (1/s)',title='闭环 / 当前模型极点')
    ax.grid(True,alpha=.2);buf=BytesIO();fig.savefig(buf,format='png',dpi=145);plt.close(fig)
    return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()

def model_diagram(run):
    m=run['model'];manifest=ROOT/'sources'/'figures'/'diagrams.json'
    if manifest.exists():
        diagrams=json.loads(manifest.read_text(encoding='utf-8'))
        item=diagrams.get(f"{m['lab_id']}:{m['task_id']}") or diagrams.get(f"{m['lab_id']}:all")
        if item:
            path=ROOT/item['url'].lstrip('/')
            encoded=base64.b64encode(path.read_bytes()).decode()
            return f'<figure><img style="max-height:320px" src="data:image/png;base64,{encoded}"/><figcaption>实验原理图</figcaption></figure>'
    return '<figure><svg viewBox="0 0 600 140" style="max-height:170px;width:100%" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="#709591" stroke-width="2"><path d="M25 55H105M135 55H215M375 55H570"/><circle cx="120" cy="55" r="15"/><rect x="215" y="30" width="160" height="50" rx="5" fill="#f2f8f6"/>'+('<path d="M480 55V115H120V70"/>' if m['closed'] else '')+'</g><g fill="#426b6b" text-anchor="middle" font-size="14"><text x="40" y="35">u(t)</text><text x="295" y="60">传递函数模型 G(s)</text><text x="550" y="35">y(t)</text>'+('<text x="295" y="110">反馈通道 H(s)</text>' if m['closed'] else '')+'</g></svg><figcaption>当前实验信号关系</figcaption></figure>'

def fmt(value):
    if value is None:return '不适用 / 未确定'
    if isinstance(value,float):return f'{value:.6g}'
    if isinstance(value,bool):return '满足' if value else '不满足'
    return str(value)

LABELS={'stability':'稳定性','steady_state':'理论阶跃稳态值','overshoot':'超调量 / %','settling_time':'调节时间 / s','rise_time':'上升时间（10%–90%）/ s','peak_time':'峰值时间 / s','observed_end_value':'当前窗口末值','ramp_error':'单位斜坡稳态误差','phase_margin':'相位裕度 / °','gain_margin_db':'幅值裕度 / dB','crossover':'截止角频率 / rad·s⁻¹','phase_crossover':'相位穿越角频率 / rad·s⁻¹'}
STATES={'stable':'渐近稳定','marginal':'临界 / 边界状态','unstable':'不稳定'}

def table(mapping):
    return '<table><tbody>'+''.join(f'<tr><th>{esc(LABELS.get(k,k))}</th><td>{esc(STATES.get(v,fmt(v)) if isinstance(v,str) else fmt(v))}</td></tr>' for k,v in mapping.items() if k in LABELS)+'</tbody></table>'

def katex_embed():
    vendor=ROOT/'node_modules'/'katex'/'dist'
    if not vendor.exists():return '<script>document.querySelectorAll(".math").forEach(e=>{e.textContent=e.dataset.tex})</script>'
    css=(vendor/'katex.min.css').read_text(encoding='utf-8')
    def font(m):
        f=vendor/m.group(1)
        if not f.exists():return m.group(0)
        mime='font/woff2' if f.suffix=='.woff2' else 'font/woff' if f.suffix=='.woff' else 'font/ttf'
        return 'url(data:'+mime+';base64,'+base64.b64encode(f.read_bytes()).decode()+')'
    css=re.sub(r'url\((fonts/[^)]+)\)',font,css)
    js=(vendor/'katex.min.js').read_text(encoding='utf-8').replace('</script',r'<\/script')
    return '<style>'+css+'</style><script>'+js+'</script><script>document.querySelectorAll(".math").forEach(e=>katex.render(e.dataset.tex,e,{displayMode:true,throwOnError:false}));</script>'

def make_html(runs,student,analysis):
    sections=[]
    for run in runs:
        m=run['model'];lab,task=get_task(m['lab_id'],m['task_id'])
        theory=''.join(f'<h3>{esc(s["title"])}</h3><p>{esc(s["text"])}</p>'+''.join(f'<div class="math" data-tex="{esc(f)}"></div>' for f in s['formulas']) for s in lab['sections'])
        design=json.dumps(m['design'],ensure_ascii=False,indent=2)
        conclusion=f'本次运行的系统状态为{STATES[run["metrics"]["stability"]]}。'
        if run.get('checks'):conclusion+='设计指标：'+'；'.join(f'{LABELS.get(k,k)}{fmt(v)}' for k,v in run['checks'].items())+'。'
        sections.append(f'''<section><h2>实验 {lab['id']} · {esc(lab['title'])}</h2><h3>{esc(task['name'])}</h3>
<p class="provenance">运行编号 {esc(run['id'])} · {esc(run['created_at'])} · {esc(run['engine_label'])} {esc(run.get('version',''))}</p>
<h3>一、实验目的与步骤</h3><ul>{''.join('<li>'+esc(x)+'</li>' for x in lab['objectives'])}</ul><ol>{''.join('<li>'+esc(x)+'</li>' for x in lab['steps'])}</ol>
<h3>二、实验原理与推导</h3>{theory}
<h3>三、参数与模型</h3>{model_diagram(run)}<p>输入：{esc(m['input_signal'])}；仿真时长 {m['stop_time']:.6g} s；采样数 {m['points']}；误差带 ±{100*m['settling_threshold']:g}%。</p><pre>{esc(json.dumps(m['params'],ensure_ascii=False,indent=2))}</pre><p>分子（降幂）：{esc(m['num'])}<br>分母（降幂）：{esc(m['den'])}</p><pre>{esc(design)}</pre>
<h3>四、实验结果与指标</h3>{table(run['metrics'])}{table(run['margins'])}<p>幅值裕度：{'∞（未出现相位穿越）' if run['margins'].get('gain_margin_infinite') else fmt(run['margins'].get('gain_margin_db'))+' dB'}</p>
<figure><img src="{chart(run,'time')}"/><figcaption>图 {lab['id']}-1 输入与输出响应</figcaption></figure><figure><img src="{chart(run,'bode')}"/><figcaption>图 {lab['id']}-2 幅频响应</figcaption></figure><figure><img src="{chart(run,'poles')}"/><figcaption>图 {lab['id']}-3 极点分布</figcaption></figure>
<h3>五、结果分析与结论</h3><p>{esc(conclusion)}</p>{''.join('<p>'+esc(n)+'</p>' for n in run['notes'])}<p>{esc(analysis or '尚未填写个人分析。请结合参数变化、理论对照和实际运行结果补充。')}</p>
<h3>六、思考题</h3>{''.join('<p><b>'+esc(q)+'</b><br>'+esc(a)+'</p>' for q,a in lab['questions'])}<h3>附录：本次 MATLAB 代码</h3><pre>{esc(run['code'])}</pre></section>''')
    name=student.get('name','');sid=student.get('student_id','')
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>自动控制实验报告</title><style>
body{{max-width:860px;margin:42px auto;padding:0 30px;color:#24363e;font:15px/1.85 'Microsoft YaHei',sans-serif}}h1{{font-size:30px;color:#154847}}h2{{border-bottom:2px solid #247d78;padding-bottom:8px;margin-top:48px}}h3{{margin-top:28px}}pre{{padding:16px;background:#f2f5f5;white-space:pre-wrap;font:12px/1.7 Consolas,monospace;overflow-wrap:anywhere}}table{{border-collapse:collapse;width:100%;margin:18px 0}}th,td{{border:1px solid #cbd8dc;padding:7px 12px;text-align:left}}th{{width:44%;background:#f4f7f7}}img{{max-width:100%}}figure{{margin:25px 0;break-inside:avoid}}figcaption{{text-align:center;color:#677d86}}.provenance{{font-size:12px;color:#647881}}.math{{overflow-x:auto;padding:5px 0}}.print{{background:#247d78;color:white;padding:10px 18px;border:0;border-radius:6px;cursor:pointer}}@media print{{body{{margin:0;max-width:none;font-size:11pt}}.print{{display:none}}h2,h3{{break-after:avoid}}pre{{font-size:8pt}}section+section{{break-before:page}}.katex-display{{overflow:visible}}}}\n</style><button class="print" onclick="window.print()">打印 / 保存 PDF</button><h1>自动控制实验报告</h1><p>姓名：{esc(name)}　学号：{esc(sid)}　班级：{esc(student.get('class_name',''))}</p><p>生成日期：{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')} · 共 {len(runs)} 次已完成运行</p><p>本报告依据保存的运行记录生成。不同引擎和工况分别标记；个人分析由填写内容保留。</p>{''.join(sections)}{katex_embed()}</html>'''

def make_markdown(runs,student,analysis):
    out=['# 自动控制实验报告',f'姓名：{student.get("name","")}　学号：{student.get("student_id","")}']
    for r in runs:
        lab,task=get_task(r['model']['lab_id'],r['model']['task_id'])
        out += [f'## 实验 {lab["id"]} · {lab["title"]}',task['name'],f'运行：{r["id"]}；{r["engine_label"]}；{r["created_at"]}','### 原理推导']
        for s in lab['sections']:out += [f'#### {s["title"]}',s['text']]+['$$\n'+f+'\n$$' for f in s['formulas']]
        out += ['### 参数与结果','```json',json.dumps({'model':r['model'],'metrics':r['metrics'],'margins':r['margins'],'checks':r['checks']},ensure_ascii=False,indent=2),'```','### 分析',analysis or '待填写个人分析。','### MATLAB 代码','```matlab',r['code'],'```']
    return '\n\n'.join(out)

def csv_data(run):
    s=StringIO();w=csv.writer(s);w.writerow(['time_s','input','output']);w.writerows(zip(run['time'],run['input'],run['output']));return '\ufeff'+s.getvalue()

def report_bytes(runs,student,analysis,format):
    if format=='json':return json.dumps(dict(student=student,runs=runs,analysis=analysis),ensure_ascii=False,indent=2).encode('utf-8')
    if format=='markdown':return make_markdown(runs,student,analysis).encode('utf-8')
    report=make_html(runs,student,analysis)
    if format=='html':return report.encode('utf-8')
    b=BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('report.html',report);z.writestr('report.md',make_markdown(runs,student,analysis))
        z.writestr('runs.json',json.dumps(runs,ensure_ascii=False,indent=2))
        for r in runs:
            z.writestr(f'lab{r["model"]["lab_id"]}_{r["id"]}.csv',csv_data(r));z.writestr(f'lab{r["model"]["lab_id"]}_{r["id"]}.m',r['code'])
            model=ROOT/'runtime'/r['id']/'model.slx'
            if model.exists():z.write(model,f'lab{r["model"]["lab_id"]}_{r["id"]}.slx')
    return b.getvalue()
