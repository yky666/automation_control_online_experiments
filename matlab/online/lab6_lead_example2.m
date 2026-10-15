% Control Lab · 实际结果由你在 MATLAB / MATLAB Online 中运行得到
% 网页中的曲线是默认参数的预计算示例，不代表当前代码已经执行
clear; clc; close all;
Kv = 20;
K = 10;
targetPM = 35;
reserve = 8;
alpha = 6;
wm = 6;
MpReq = 30;
tsReq = 5;
essReq = 0.1;
frequency = 1;
A = 1;
G0 = tf(K,[0.2 1 0 0]);
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
    ess=0; disp(struct('ramp_error',ess,'ramp_error_pass',ess<=essReq));
end