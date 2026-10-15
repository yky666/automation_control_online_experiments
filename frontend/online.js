export const REPOSITORY='yky666/automation_control_online_experiments';
const base=import.meta.env?.BASE_URL||'/';
export const assetUrl=path=>base+path.replace(/^\//,'');
export const onlineUrl=(labId,taskId,mode='matlab')=>{
 const file=`matlab/online/lab${labId}_${taskId}${mode==='simulink'?'_simulink':''}.m`;
 return 'https://matlab.mathworks.com/open/github/v1?'+new URLSearchParams({repo:REPOSITORY,file});
};
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
 const safeBody=body.replace('disp(sys); pole(sys), zero(sys)',"disp(sys); [z,poles_,gain_]=zpkdata(sys,'v'); disp(z); disp(poles_)");
 if(mode!=='simulink')return safeBody;
 if(!['ode45','ode15s'].includes(request.solver))throw Error('求解器无效');
 return safeBody+`\n\nassert(isproper(sys),'理想微分需加入滤波后再用 Transfer Fcn');\nmdl = 'control_lab_${request.lab_id}_${request.task_id}';\nif bdIsLoaded(mdl), close_system(mdl,0); end\nnew_system(mdl);\nadd_block('simulink/Sources/From Workspace',[mdl '/Input'],'VariableName','web_input','Position',[30 80 150 110]);\nadd_block('simulink/Continuous/Transfer Fcn',[mdl '/Plant'],'Numerator',mat2str(num),'Denominator',mat2str(den),'Position',[220 70 390 125]);\nadd_block('simulink/Sinks/To Workspace',[mdl '/Output'],'VariableName','web_output','SaveFormat','Timeseries','Position',[450 80 580 110]);\nadd_line(mdl,'Input/1','Plant/1'); add_line(mdl,'Plant/1','Output/1');\nwks=get_param(mdl,'ModelWorkspace'); assignin(wks,'web_input',timeseries(u,t));\nset_param(mdl,'StopTime',num2str(t(end),16),'Solver','${request.solver}','MaxStep',num2str(t(2)-t(1),16),'RelTol','1e-7','AbsTol','1e-9','ReturnWorkspaceOutputs','on');\nsave_system(mdl); open_system(mdl);\nout=sim(mdl); yy=out.get('web_output');\nfigure; plot(yy.Time,yy.Data); grid on;\n`;
}

export function downloadText(text,name,type='text/plain;charset=utf-8'){
 const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
}
export function exampleCsv(example){return '\ufefftime,input,output\n'+example.time.map((t,i)=>[t,example.input[i],example.output[i]].join(',')).join('\n')}

export function makeScanCode(example,request,key,values){
 return values.map(value=>`%% ${key} = ${value}\n`+makeCode(example,{...request,...(['amplitude','stop_time'].includes(key)?{[key]:value}:{params:{...request.params,[key]:value}})}).replace('clear; clc; close all;','clc;')).join('\n\n');
}
