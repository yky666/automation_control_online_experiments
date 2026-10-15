% Control Lab · 实际结果由你在 MATLAB / MATLAB Online 中运行得到
% 网页中的曲线是默认参数的预计算示例，不代表当前代码已经执行
clear; clc; close all;
Kv = 20;
K = 1000;
targetPM = 45;
reserve = 8;
alpha = 3;
wm = 6;
MpReq = 27.5;
tsReq = 1.7;
essReq = 0.1;
frequency = 1;
A = 1;
G0 = tf(K,conv([1 0],conv([0.1 1],[0.001 1])));
[~,PM0]=margin(G0);
phi=targetPM-PM0+reserve;
assert(phi>0 && phi<85,'所需超前角需在 0~85 度内');
alpha=(1+sind(phi))/(1-sind(phi));
wm=exp(fzero(@(x) 20*log10(abs(evalfr(G0,1i*exp(x))))+10*log10(alpha),[-16 22]));
stages=1;
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


assert(isproper(sys),'理想微分需加入滤波后再用 Transfer Fcn');
mdl = 'control_lab_6_lead_example1';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl);
add_block('simulink/Sources/From Workspace',[mdl '/Input'],'VariableName','web_input','Position',[30 80 150 110]);
add_block('simulink/Continuous/Transfer Fcn',[mdl '/Plant'],'Numerator',mat2str(num),'Denominator',mat2str(den),'Position',[220 70 390 125]);
add_block('simulink/Sinks/To Workspace',[mdl '/Output'],'VariableName','web_output','SaveFormat','Timeseries','Position',[450 80 580 110]);
add_line(mdl,'Input/1','Plant/1'); add_line(mdl,'Plant/1','Output/1');
wks=get_param(mdl,'ModelWorkspace'); assignin(wks,'web_input',timeseries(u,t));
set_param(mdl,'StopTime',num2str(t(end),16),'Solver','ode45','MaxStep',num2str(t(2)-t(1),16),'RelTol','1e-7','AbsTol','1e-9','ReturnWorkspaceOutputs','on');
save_system(mdl); open_system(mdl);
out=sim(mdl); yy=out.get('web_output');
figure; plot(yy.Time,yy.Data); grid on;
