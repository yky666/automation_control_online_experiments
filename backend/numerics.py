import math
import numpy as np
from scipy import signal, optimize
from .catalog import get_task

def trim(a):
    a=np.trim_zeros(np.asarray(a,dtype=float),'f')
    return a if len(a) else np.array([0.])
def feedback(n,d,hnum=None,hden=None):
    if hnum is None: return trim(n),trim(np.polyadd(d,n))
    return trim(np.polymul(n,hden)),trim(np.polyadd(np.polymul(d,hden),np.polymul(n,hnum)))
def roots(a):
    return np.roots(trim(a)) if len(trim(a))>1 else np.array([],dtype=complex)
def stability(d):
    p=roots(d)
    tol=1e-7*max(1,float(np.max(np.abs(p))) if p.size else 1)
    if np.any(p.real>tol): return 'unstable'
    axis=p[np.abs(p.real)<=tol]
    if axis.size:
        if any(abs(a-b)<10*tol for i,a in enumerate(axis) for b in axis[i+1:]): return 'unstable'
        return 'marginal'
    return 'stable'
def frequency(n,d,w):
    return np.polyval(n,1j*w)/np.polyval(d,1j*w)
def margins(n,d):
    w=np.logspace(-7,9,10000)
    h=frequency(n,d,w)
    mag=20*np.log10(np.maximum(np.abs(h),1e-300))
    phase=np.unwrap(np.angle(h))*180/np.pi
    cross=np.where(mag[:-1]*mag[1:]<0)[0]
    pm=[]
    for i in cross:
        wc=float(np.exp(optimize.brentq(lambda v:20*np.log10(abs(frequency(n,d,np.exp(v)))),np.log(w[i]),np.log(w[i+1]))))
        ph=float(np.interp(np.log(wc),np.log(w),phase))
        value=(180+ph+180)%360-180
        pm.append((value,wc))
    gm=[]
    for angle in range(-900,901,360):
        a=phase-angle
        for i in np.where(a[:-1]*a[1:]<0)[0]:
            wp=float(np.exp(np.interp(angle,sorted([phase[i],phase[i+1]]),[np.log(w[i]),np.log(w[i+1])] if phase[i]<phase[i+1] else [np.log(w[i+1]),np.log(w[i])])) )
            gm.append((-20*math.log10(abs(frequency(n,d,wp))),wp))
    p=min(pm,key=lambda x:abs(x[0])) if pm else (None,None)
    g=min(gm,key=lambda x:abs(x[0])) if gm else (None,None)
    return {'phase_margin':p[0],'crossover':p[1],'gain_margin_db':g[0],'phase_crossover':g[1],'gain_margin_infinite':not bool(gm)}

def build_model(req):
    lab,task=get_task(req.lab_id,req.task_id)
    p={f['key']:f['default'] for f in lab['fields']}
    p.update(task['defaults']);p.update(req.params)
    for f in lab['fields']:
        if f['key'] in req.params and not f['min']<=p[f['key']]<=f['max']: raise ValueError(f"{f['label']} 超出允许范围")
    p.update(A=req.amplitude)
    kind=task['kind']; K=p.get('K',1);T=p.get('T',0.1)
    baseline=None;design={};close=False
    if kind=='typical':
        typ=task['id'];Tf=p['Tf']
        n,d={'p':([K],[1]),'inertia':([K],[T,1]),'integrator':([K],[T,0]),'d':([K*T,0],[Tf,1]),'pi':([K*T,K],[T,0]),'pd':([K*(Tf+T),K],[Tf,1])}[typ]
    elif kind in ('second','zero'):
        z=p['zeta'];wn=p['wn'];n=[wn*wn];d=[1,2*z*wn,wn*wn]
        if kind=='zero':n=[wn*wn/p['zero'],wn*wn]
    elif kind=='bandwidth':n=[K];d=[K/(2*np.pi*p['GBW']),1]
    elif kind=='frequency_inertia':n=[K];d=[T,1]
    elif kind in ('stability','reduced'):
        n=[10*K];d=np.polymul([1,0],[p['T1'],1])
        if kind=='stability':
            d=np.polymul(d,[p['T2'],1]);t1=p['T1'];t2=p['T2'];kcr=(t1+t2)/(10*t1*t2)
            design={'Kcr':kcr,'critical_frequency':1/math.sqrt(t1*t2),'routh':[[t1*t2,1],[t1+t2,10*K],[(t1+t2-10*K*t1*t2)/(t1+t2),0],[10*K,0]]}
        close=True
    elif kind.startswith('lead'):
        if kind=='lead1':n0=[2*p['Kv']];d0=[1,2,0]
        elif kind=='lead_example1':n0=[K];d0=np.polymul([1,0],np.polymul([0.1,1],[0.001,1]))
        elif kind=='lead2':n0=[K];d0=np.polymul([1,0],np.polymul([0.5,1],[1/30,1]))
        else:n0=[K];d0=[0.2,1,0,0]
        m0=margins(n0,d0)
        if kind in ('lead1','lead_example1'):
            phi=p['targetPM']-(m0['phase_margin'] or 0)+p['reserve']
            if not 0<phi<85: raise ValueError('所需最大超前角必须在 0～85° 内，请调整目标裕度或预留角')
            alpha=(1+math.sin(math.radians(phi)))/(1-math.sin(math.radians(phi)))
            wm=float(np.exp(optimize.brentq(lambda x:20*math.log10(abs(frequency(n0,d0,np.exp(x))))+10*math.log10(alpha),-16,22)))
            stages=1
        else:alpha=p['alpha'];wm=p['wm'];stages=2
        wz=wm/math.sqrt(alpha);wp=wm*math.sqrt(alpha)
        nc=[1/wz,1];dc=[1/wp,1]
        n,d=n0,d0
        for _ in range(stages):n=np.polymul(n,nc);d=np.polymul(d,dc)
        bn,bd=feedback(n0,d0)
        baseline={'num':bn.tolist(),'den':bd.tolist(),'open_num':list(n0),'open_den':np.asarray(d0).tolist()}
        design={'alpha':alpha,'beta':1/alpha,'T':1/wp,'wz':wz,'wp':wp,'wm':wm,'stages':stages,'before_margins':m0,'controller_num':list(nc),'controller_den':list(dc),'Kv':(2*p['Kv']/2 if kind=='lead1' else K if kind=='lead2' else None)}
        if kind=='lead2':design['requirements']={'overshoot':p['MpReq'],'settling_time':p['tsReq'],'ramp_error':p['essReq']}
        if kind=='lead_example2':
            design['requirements']={'overshoot':p['MpReq'],'settling_time':p['tsReq'],'ramp_error':p['essReq']}
            design['ramp_error_theoretical']=0.
        close=True
    else:
        n=task['num'];d=task['den']
        if kind in ('feedback','dynamic_feedback'):
            n=np.asarray(n)*K;close=True
    if req.numerator is not None:
        n=req.numerator;d=req.denominator;baseline=None;design={'custom_coefficients':True};close=False
    on,od=trim(n),trim(d)
    if close:
        n,d=feedback(n,d,[1],[1,1]) if kind=='dynamic_feedback' else feedback(n,d)
        if kind=='dynamic_feedback':od=trim(np.polymul(od,[1,1]))
    n,d=trim(n),trim(d)
    if d[0]==0 or not np.isfinite(d).all() or not np.isfinite(n).all():raise ValueError('无效的传递函数系数')
    n=n/d[0];on=on/od[0];d=d/d[0];od=od/od[0]
    sig=req.input_signal or task.get('input','sine' if lab['id']==5 else 'step')
    stop=req.stop_time
    if sig=='sine' and req.auto_duration:
        f=p.get('frequency',1);decay=[-v.real for v in roots(d) if v.real<-1e-9]
        stop=max(10/f,10/min(decay) if decay else 10/f)
    points=req.points
    if sig=='sine':
        points=max(points,int(math.ceil(stop*p.get('frequency',1)*60))+1)
        if points>200001:raise ValueError('正弦频率与慢极点组合需要超过 200000 个采样点，请降低测试频率或减小时间常数。')
    return dict(lab_id=lab['id'],task_id=task['id'],task_name=task['name'],params=p,num=n.tolist(),den=d.tolist(),open_num=on.tolist(),open_den=od.tolist(),closed=close,baseline=baseline,design=design,input_signal=sig,stop_time=stop,auto_duration=req.auto_duration,points=points,requested_points=req.points,settling_threshold=req.settling_threshold,solver=req.solver)

def input_values(model,t):
    A=model['params']['A'];sig=model['input_signal']
    if sig=='step':return np.ones_like(t)*A
    if sig=='ramp':return A*t
    if sig=='step_ramp':return A*(1+t)
    if sig=='polynomial':return A*(5+2*t+8*t*t)
    return A*np.sin(2*np.pi*model['params'].get('frequency',1)*t)

def calculate_metrics(n,d,t,y,threshold,A,sig):
    state=stability(d);steady=None;over=None;settling=None;rise=None;peak_time=None
    if state=='stable' and sig=='step' and d[-1]!=0:
        steady=float(n[-1]/d[-1]*A)
        if abs(steady)>1e-12:
            norm=np.asarray(y)/steady
            over=max(0,float(np.max(norm)-1))*100
            peak_time=float(t[int(np.argmax(norm))]) if over>0.001 else None
            outside=np.where(abs(norm-1)>threshold)[0]
            if not len(outside):settling=0.
            elif outside[-1]<len(t)-1:settling=float(t[outside[-1]+1])
            def first_cross(target):
                hits=np.where(norm>=target)[0]
                if not len(hits):return None
                i=hits[0]
                return float(t[i]) if i==0 else float(t[i-1]+(t[i]-t[i-1])*(target-norm[i-1])/(norm[i]-norm[i-1]))
            t10=first_cross(0.1);t90=first_cross(0.9)
            if t10 is not None and t90 is not None:rise=t90-t10
    return dict(stability=state,steady_state=steady,overshoot=over,settling_time=settling,rise_time=rise,peak_time=peak_time,observed_end_value=float(y[-1]) if len(y) else None,settling_threshold=threshold)

def simulate_preview(model):
    n=model['num'];d=model['den'];t=np.linspace(0,model['stop_time'],model['points']);u=input_values(model,t);notes=[]
    if len(n)>len(d):
        t=np.array([]);y=np.array([]);u=np.array([]);notes.append('非真有理传递函数仅做代数与频率分析；含理想微分，不生成普通阶跃曲线。')
    else:
        _,y,_=signal.lsim((n,d),u,t)
    if not np.isfinite(y).all():raise ValueError('该工况响应数值溢出，请缩短仿真时间或减小参数')
    metric=calculate_metrics(n,d,t,y,model['settling_threshold'],model['params']['A'],model['input_signal'])
    if metric['stability']!='stable':notes.append('系统不渐近稳定，超调量、调节时间与有限稳态值不适用。')
    if metric['stability']=='stable' and model['input_signal']=='step' and metric['settling_time'] is None:notes.append('当前仿真窗口未确定调节时间，可延长仿真；末点不是理论稳态。')
    rr=roots(model['open_den']);zz=roots(model['open_num']);freqs=np.abs(np.r_[rr,zz]);freqs=freqs[freqs>1e-9]
    w=np.logspace(math.log10(max(float(freqs.min())/100,1e-4)) if freqs.size else -2,math.log10(float(freqs.max())*100) if freqs.size else 3,450)
    h=frequency(model['open_num'],model['open_den'],w)
    bode=dict(w=w.tolist(),magnitude=(20*np.log10(np.maximum(abs(h),1e-300))).tolist(),phase=(np.unwrap(np.angle(h))*180/np.pi).tolist())
    extras={}
    if model['baseline']:
        b=model['baseline'];_,yb,_=signal.lsim((b['num'],b['den']),u,t)
        hb=frequency(b['open_num'],b['open_den'],w)
        extras['baseline']={'y':yb.tolist(),'magnitude':(20*np.log10(abs(hb))).tolist(),'phase':(np.unwrap(np.angle(hb))*180/np.pi).tolist()}
    if model['input_signal']=='sine' and metric['stability']=='stable':
        f=model['params'].get('frequency',1);mask=t>=model['stop_time']-5/f;tt=t[mask]
        fit=np.linalg.lstsq(np.column_stack((np.sin(2*np.pi*f*tt),np.cos(2*np.pi*f*tt),np.ones_like(tt))),y[mask],rcond=None)[0]
        amp=float(np.hypot(fit[0],fit[1]));phase=float(np.degrees(np.arctan2(fit[1],fit[0])));exact=frequency(n,d,2*np.pi*f)
        extras['sine_fit']={'frequency_hz':f,'amplitude':amp,'gain':amp/model['params']['A'],'phase':phase,'theoretical_gain':float(abs(exact)),'theoretical_phase':float(np.angle(exact)*180/np.pi),'relative_gain_error':abs(amp/model['params']['A']/abs(exact)-1)}
        sf=np.logspace(np.log10(w[0]/(2*np.pi)),np.log10(w[-1]/(2*np.pi)),15);hh=frequency(n,d,sf*2*np.pi)
        extras['measurements']=[dict(f=float(fx),w=float(2*np.pi*fx),magnitude=float(20*np.log10(abs(hx))),phase=float(np.angle(hx)*180/np.pi),output_amplitude=float(model['params']['A']*abs(hx))) for fx,hx in zip(sf,hh)]
    if model['task_id'].startswith('residue'):
        r,p,k=signal.residue(n,d);extras['residue']={'residues':[[float(v.real),float(v.imag)] for v in r],'poles':[[float(v.real),float(v.imag)] for v in p],'direct':k.tolist()}
    if model['closed']:
        gains=np.linspace(0,40 if model['lab_id']==4 else 10,120);base=np.asarray(model['open_num'])/model['params'].get('K',1) if model['lab_id']==4 else np.asarray(model['open_num'])
        locus_den=model['open_den']
        branches=[];prev=None
        for gain in gains:
            cur=roots(np.polyadd(locus_den,base*gain))
            if prev is not None:
                _,idx=optimize.linear_sum_assignment(abs(prev[:,None]-cur[None,:]));cur=cur[idx]
            branches.append([[float(z.real),float(z.imag)] for z in cur]);prev=cur
        extras['root_locus']={'gains':gains.tolist(),'roots':branches}
    m=margins(model['open_num'],model['open_den'])
    design=model['design']
    kv=design.get('Kv')
    if kv and metric['stability']=='stable':metric['ramp_error']=1/kv
    if metric['stability']=='stable' and 'ramp_error_theoretical' in design:metric['ramp_error']=design['ramp_error_theoretical']
    checks={}
    if 'requirements' in design:
        checks={key:(metric.get(key) is not None and metric[key]<=limit+1e-8) for key,limit in design['requirements'].items()}
    if model['task_id']=='lead1':checks={'phase_margin':m['phase_margin'] is not None and m['phase_margin']>model['params']['targetPM'],'gain_margin_db':m['gain_margin_infinite'] or (m['gain_margin_db'] is not None and m['gain_margin_db']>10)}
    result=dict(engine='scipy',engine_label='平台计算（免 MATLAB）',model=model,time=t.tolist(),input=u.tolist(),output=np.asarray(y).tolist(),bode=bode,metrics=metric,margins=m,poles=[[float(p.real),float(p.imag)] for p in roots(d)],zeros=[[float(p.real),float(p.imag)] for p in roots(n)],notes=notes,checks=checks,**extras)
    return result

def matlab_code(model):
    v=lambda x:'['+' '.join(f'{a:.12g}' for a in x)+']'
    lines=['% Control Lab — 由当前参数生成，可独立运行','clear; clc; close all;',f'num = {v(model["num"])};',f'den = {v(model["den"])};','sys = tf(num,den);','disp(sys); pole(sys), zero(sys)',f'Gopen = tf({v(model["open_num"])},{v(model["open_den"])});','[GM,PM,Wcg,Wcp] = margin(Gopen);','fprintf("GM=%.6g dB, PM=%.6g deg, wc=%.6g rad/s\\n",20*log10(GM),PM,Wcp);']
    if len(model['num'])>len(model['den']):lines+=['[r,p,k] = residue(num,den);','disp(r); disp(p); disp(k);','figure; bode(sys); grid on;']
    else:
        lines += [f't = linspace(0,{model["stop_time"]:.12g},{model["points"]}).\';',f'A = {model["params"]["A"]:.12g};']
        sig=model['input_signal'];expr={'step':'A*ones(size(t))','ramp':'A*t','step_ramp':'A*(1+t)','polynomial':'A*(5+2*t+8*t.^2)','sine':f'A*sin(2*pi*{model["params"].get("frequency",1):.12g}*t)'}[sig]
        lines += [f'u = {expr};','y = lsim(sys,u,t);','figure; plot(t,u,"--",t,y,"LineWidth",1.5); grid on;','xlabel("Time (s)"); ylabel("Amplitude"); legend("Input","Output");']
        if sig=='step':lines+=['if isstable(sys)',f'    info = stepinfo(y,t,dcgain(sys)*A,"SettlingTimeThreshold",{model["settling_threshold"]});','    disp(info);','end']
        lines+=['figure; bode(Gopen); grid on;']
    return '\n'.join(lines)

def simulink_code(model):
    if len(model['num'])>len(model['den']):return '% 非真有理模型不能用 Transfer Fcn 运行，请先加入微分滤波。\n'+matlab_code(model)
    return matlab_code(model)+f'''\n\n% 在 MATLAB / Simulink Online 中构建并运行当前模型
mdl = 'control_lab_{model['lab_id']}';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl);
add_block('simulink/Sources/From Workspace',[mdl '/Input'],'VariableName','web_input','Position',[30 80 150 110]);
add_block('simulink/Continuous/Transfer Fcn',[mdl '/Plant'],'Numerator',mat2str(num),'Denominator',mat2str(den),'Position',[220 70 390 125]);
add_block('simulink/Sinks/To Workspace',[mdl '/Output'],'VariableName','web_output','SaveFormat','Timeseries','SampleTime',num2str(t(2)-t(1),16),'Position',[450 80 580 110]);
add_line(mdl,'Input/1','Plant/1'); add_line(mdl,'Plant/1','Output/1');
wks=get_param(mdl,'ModelWorkspace'); assignin(wks,'web_input',timeseries(u,t));
set_param(mdl,'StopTime',num2str(t(end),16),'Solver','{model['solver']}','MaxStep',num2str(t(2)-t(1),16),'ReturnWorkspaceOutputs','on');
save_system(mdl); open_system(mdl);
out=sim(mdl); yy=out.get('web_output');
figure; plot(yy.Time,yy.Data); grid on; xlabel('Time (s)'); ylabel('Output');
'''
