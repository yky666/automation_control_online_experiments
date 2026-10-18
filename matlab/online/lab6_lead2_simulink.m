% Control Lab · 实际结果由你在 MATLAB / MATLAB Online 中运行得到
% 网页中的曲线是默认参数的预计算示例，不代表当前代码已经执行
clear; clc; close all;
Kv = 20;
K = 10;
targetPM = 35;
reserve = 8;
alpha = 3;
wm = 6;
MpReq = 27.5;
tsReq = 1.7;
essReq = 0.1;
frequency = 1;
A = 1;
G0 = tf(K,conv([1 0],conv([0.5 1],[1/30 1])));
stages=2;
wz=wm/sqrt(alpha); wp=wm*sqrt(alpha);
Gc=tf([1/wz 1],[1/wp 1]);
Gopen=G0*Gc^stages;

sys = feedback(Gopen,1);
[num,den] = tfdata(sys,'v');
disp(sys); [z,poles_,gain_]=zpkdata(sys,'v'); disp(z); disp(poles_)
[GM,PM,Wcg,Wcp] = margin(Gopen);
fprintf('GM=%.6g dB, PM=%.6g deg, wc=%.6g rad/s\n',20*log10(GM),PM,Wcp);
stop_time = 5;
points = 1501;
t = linspace(0,stop_time,points).';
u = A*ones(size(t));
if ~isproper(sys)
    [r,p,k] = residue(num,den); disp(r); disp(p); disp(k);
    figure; bode(sys); grid on;
else
    y = lsim(sys,u,t);
    figure; plot(t,u,'--',t,y,'LineWidth',1.5); grid on;
    xlabel('Time (s)'); ylabel('Amplitude'); legend('Input','Output');
    if isstable(sys), disp(stepinfo(y,t,dcgain(sys)*A,'SettlingTimeThreshold',0.02)); end
end
figure; bode(Gopen); grid on;
if isproper(sys) && isstable(sys)
    info=stepinfo(sys);
    disp(struct('overshoot_pass',info.Overshoot<=MpReq,'settling_pass',info.SettlingTime<=tsReq));
    ess=1/K; disp(struct('ramp_error',ess,'ramp_error_pass',ess<=essReq));
end
% 理想超前电路选值：C_design 可按元件条件修改
C_design=1e-6; R1_design=1/(wz*C_design); R2_design=R1_design/(alpha-1); R3_design=R1_design+R2_design;
disp(table(R1_design,R2_design,R3_design,C_design));

% 课程模块结构；在原生 Simulink 中继续插入、组合、编辑和仿真
mdl = 'course_lab6_lead2';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl);
[num,den]=tfdata(sys,'v');
if exist('G0','var'), [plant_num,plant_den]=tfdata(G0,'v'); end
if exist('u','var') && exist('t','var'), wks=get_param(mdl,'ModelWorkspace'); assignin(wks,'web_input',timeseries(u,t)); end
% 将模块变量保存到模型工作区，避免依赖个人基础工作区配置。
wks=get_param(mdl,'ModelWorkspace');
course_variables={'A','K','T','Tf','T1','T2','frequency','wn','zeta','alpha','wz','wp','GBW','num','den','plant_num','plant_den','wm','MpReq','tsReq','essReq'};
for course_i=1:numel(course_variables), course_name=course_variables{course_i}; if exist(course_name,'var'), assignin(wks,course_name,eval(course_name)); end; end
add_block('simulink/Sources/Step',[mdl '/b1'],'Position',[30 100 145 165],'Time','0','Before','0','After','A');
add_block('simulink/Math Operations/Sum',[mdl '/b2'],'Position',[190 100 305 165],'Inputs','+-');
add_block('simulink/Continuous/Transfer Fcn',[mdl '/b3'],'Position',[350 100 465 165],'Numerator','[1/wz 1]/alpha','Denominator','[1/wp 1]');
add_block('simulink/Continuous/Transfer Fcn',[mdl '/b4'],'Position',[525 100 640 165],'Numerator','[1/wz 1]/alpha','Denominator','[1/wp 1]');
add_block('simulink/Math Operations/Gain',[mdl '/b5'],'Position',[700 100 815 165],'Gain','alpha^2');
add_block('simulink/Continuous/Transfer Fcn',[mdl '/b6'],'Position',[880 100 995 165],'Numerator','plant_num','Denominator','plant_den');
add_block('simulink/Sinks/Scope',[mdl '/b7'],'Position',[1080 100 1195 165],'NumInputPorts','1');
add_line(mdl,'b1/1','b2/1','autorouting','on');
add_line(mdl,'b2/1','b3/1','autorouting','on');
add_line(mdl,'b3/1','b4/1','autorouting','on');
add_line(mdl,'b4/1','b5/1','autorouting','on');
add_line(mdl,'b5/1','b6/1','autorouting','on');
add_line(mdl,'b6/1','b2/2','autorouting','on');
add_line(mdl,'b6/1','b7/1','autorouting','on');
add_block('simulink/Sinks/To Workspace',[mdl '/Record'],'VariableName','web_output','SaveFormat','Timeseries','Position',[1070 340 1190 380]);
add_line(mdl,'b6/1','Record/1','autorouting','on');
model_stop=5; model_step=model_stop/1500;
if exist('t','var') && numel(t)>1, model_stop=t(end); model_step=t(2)-t(1); end
set_param(mdl,'StopTime',num2str(model_stop,16),'Solver','ode45','RelTol','1e-7','AbsTol','1e-9','MaxStep',num2str(model_step,16),'ReturnWorkspaceOutputs','on');
save_system(mdl); open_system(mdl);
% Record 为附加数据记录模块；Scope 可双击查看各通道。
out=sim(mdl); yy=out.get('web_output');
figure; plot(yy.Time,yy.Data); grid on; xlabel('Time (s)'); ylabel('Output');