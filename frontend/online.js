import {courseGraph,modelScript} from './blocks.js';
export const REPOSITORY='yky666/automation_control_online_experiments';
const base=import.meta.env?.BASE_URL||'/';
export const assetUrl=path=>base+path.replace(/^\//,'');
export const onlineUrl=(labId,taskId,mode='matlab')=>{
 const file=`matlab/online/lab${labId}_${taskId}${mode==='simulink'?'_simulink':''}.m`;
 return 'https://matlab.mathworks.com/open/github/v1?'+new URLSearchParams({repo:REPOSITORY,file});
};
export const onlineFileUrl=file=>'https://matlab.mathworks.com/open/github/v1?'+new URLSearchParams({repo:REPOSITORY,file:file.replace(/^\//,'')});
async function json(path){const r=await fetch(assetUrl(path));if(!r.ok)throw Error('实验示例未加载成功，请刷新页面');return r.json()}
export const loadCourse=()=>json('course/catalog.json');
export const loadExample=(lab,task)=>json(`course/examples/${lab}_${task}.json`);
const scalar=value=>{if(!Number.isFinite(Number(value)))throw Error('参数必须为有限数值');return String(Number(value))};
const vector=values=>'['+values.map(scalar).join(' ')+']';

// MATLAB performs the actual model construction and simulation in the user's session.
// The browser only generates code; the saved example curves remain unchanged.
export function makeCode(example,request,mode='matlab'){
 const m=example.model,p={...m.params,...request.params,A:request.amplitude};
 for(const [key,bound] of Object.entries(example.parameter_bounds||{})){const v=Number(p[key]);if(!Number.isFinite(v)||v<bound[0]||v>bound[1])throw Error(`${key} 应在 ${bound[0]}～${bound[1]} 之间`)}
 const params=Object.entries(p).map(([key,value])=>`${key} = ${scalar(value)};`).join('\n');
 let recipe=example.matlab_recipe;
 if(request.numerator)recipe=`Gopen = tf(${vector(request.numerator)},${vector(request.denominator)});\nsys = Gopen;`;
 const sig=request.input_signal||m.input_signal;
 const input={step:'A*ones(size(t))',ramp:'A*t',sine:'A*sin(2*pi*frequency*t)',step_ramp:'A*(1+t)',polynomial:'A*(5+2*t+8*t.^2)'}[sig];
 if(!input)throw Error('输入类型无效');
 const stop=Number(request.stop_time),points=Number(request.points);
 if(!(stop>0&&stop<=120)||!Number.isInteger(points)||points<201||points>10001||!(p.A>0&&p.A<=100))throw Error('请检查仿真时长、幅值与采样点数');
 if(sig==='sine'&&!(p.frequency>0))throw Error('正弦频率必须大于零');
 const setup=`stop_time = ${scalar(stop)};\npoints = ${scalar(points)};\n${sig==='sine'&&request.auto_duration?"decay = -real(pole(sys)); decay = decay(decay > 1e-9);\nstop_time = 10/frequency;\nif ~isempty(decay), stop_time = max(stop_time,10/min(decay)); end\n":''}${sig==='sine'?"points = max(points,ceil(stop_time*frequency*60)+1);\nassert(points <= 200001,'正弦仿真采样过多，请调整频率或时长');\n":''}t = linspace(0,stop_time,points).';\nu = ${input};`;
 const body=`% Control Lab · 实际结果由你在 MATLAB / MATLAB Online 中运行得到\n% 网页中的曲线是默认参数的预计算示例，不代表当前代码已经执行\nclear; clc; close all;\n${params}\n${recipe}\n[num,den] = tfdata(sys,'v');\ndisp(sys); pole(sys), zero(sys)\n[GM,PM,Wcg,Wcp] = margin(Gopen);\nfprintf('GM=%.6g dB, PM=%.6g deg, wc=%.6g rad/s\\n',20*log10(GM),PM,Wcp);\n${setup}\nif ~isproper(sys)\n    [r,p,k] = residue(num,den); disp(r); disp(p); disp(k);\n    figure; bode(sys); grid on;\nelse\n    y = lsim(sys,u,t);\n    figure; plot(t,u,'--',t,y,'LineWidth',1.5); grid on;\n    xlabel('Time (s)'); ylabel('Amplitude'); legend('Input','Output');\n${sig==='step'?`    if isstable(sys), disp(stepinfo(y,t,dcgain(sys)*A,'SettlingTimeThreshold',${scalar(request.settling_threshold)})); end\n`:''}end\nfigure; bode(Gopen); grid on;\n${request.numerator?'':example.matlab_checks||''}`;
 let safeBody=body.replace('disp(sys); pole(sys), zero(sys)',"disp(sys); [z,poles_,gain_]=zpkdata(sys,'v'); disp(z); disp(poles_)");
 if(request.lab_id===3)safeBody+="\n[wn_modes,zeta_modes,poles_modes]=damp(sys); disp(table(poles_modes,wn_modes,zeta_modes));";
 if(request.lab_id===6&&!request.numerator)safeBody+="\n% 理想超前电路选值：C_design 可按元件条件修改\nC_design=1e-6; R1_design=1/(wz*C_design); R2_design=R1_design/(alpha-1); R3_design=R1_design+R2_design;\ndisp(table(R1_design,R2_design,R3_design,C_design));\n";
 if(request.lab_id===1){safeBody+="\n% 课件模型转换：包含双向还原，不只是打印 tf\n[z0,p0,k0]=tf2zp(num,den); Gz=zpk(z0,p0,k0); disp(Gz);\n[nback,dback]=zp2tf(z0,p0,k0); disp(tf(nback,dback));\n[rr,pp,kk]=residue(num,den); [nr,dr]=residue(rr,pp,kk); disp(tf(nr,dr));\nif isproper(sys), Gss=ss(sys); disp(Gss); disp(tf(Gss)); end\n";if(request.task_id==='connections')safeBody+="G1=tf(5,[1 1]); G2=tf([2 1],[1 0]); G3=tf(4,[3 1]);\ndisp(series(G1,G2)); disp(parallel(G1,G2)); disp(feedback(G1,G2,-1)); disp(series(series(G1,G2),G3));\n"}
 if(mode!=='simulink')return safeBody;
 if(!['ode45','ode15s'].includes(request.solver))throw Error('求解器无效');
 if(m.num.length>m.den.length&&!request.numerator)return safeBody+'\n% 本任务为非真有理式的代数分析，不自动构造不适定的 Transfer Fcn 仿真。';
 return modelScript(courseGraph(request,{...m,input_signal:sig}),{prelude:safeBody,request});
}

export function downloadText(text,name,type='text/plain;charset=utf-8'){
 const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
}
export function exampleCsv(example){return '\ufefftime,input,output\n'+example.time.map((t,i)=>[t,example.input[i],example.output[i]].join(',')).join('\n')}

export function makeScanCode(example,request,key,values){
 return values.map(value=>`%% ${key} = ${value}\n`+makeCode(example,{...request,...(['amplitude','stop_time'].includes(key)?{[key]:value}:{params:{...request.params,[key]:value}})}).replace('clear; clc; close all;','clc;')).join('\n\n');
}
