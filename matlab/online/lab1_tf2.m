% Control Lab · 实际结果由你在 MATLAB / MATLAB Online 中运行得到
% 网页中的曲线是默认参数的预计算示例，不代表当前代码已经执行
clear; clc; close all;
K = 1;
frequency = 1;
A = 1;
Gopen = tf([1 4 2],[1 4 4 16 0 0 0 0]);
sys = Gopen;
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

% 课件模型转换：包含双向还原，不只是打印 tf
[z0,p0,k0]=tf2zp(num,den); Gz=zpk(z0,p0,k0); disp(Gz);
[nback,dback]=zp2tf(z0,p0,k0); disp(tf(nback,dback));
[rr,pp,kk]=residue(num,den); [nr,dr]=residue(rr,pp,kk); disp(tf(nr,dr));
if isproper(sys), Gss=ss(sys); disp(Gss); disp(tf(Gss)); end
