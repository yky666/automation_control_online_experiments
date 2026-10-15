% Control Lab · 实际结果由你在 MATLAB / MATLAB Online 中运行得到
% 网页中的曲线是默认参数的预计算示例，不代表当前代码已经执行
clear; clc; close all;
K = 1;
GBW = 1000000;
T = 0.001;
zeta = 0.223607;
wn = 22.36068;
frequency = 100000;
A = 1;
Gopen = tf(K,[K/(2*pi*GBW) 1]);
sys = Gopen;
[num,den] = tfdata(sys,'v');
disp(sys); [z,poles_,gain_]=zpkdata(sys,'v'); disp(z); disp(poles_)
[GM,PM,Wcg,Wcp] = margin(Gopen);
fprintf('GM=%.6g dB, PM=%.6g deg, wc=%.6g rad/s\n',20*log10(GM),PM,Wcp);
stop_time = 5;
points = 1501;
decay = -real(pole(sys)); decay = decay(decay > 1e-9);
stop_time = 10/frequency;
if ~isempty(decay), stop_time = max(stop_time,10/min(decay)); end
points = max(points,ceil(stop_time*frequency*60)+1);
assert(points <= 200001,'正弦仿真采样过多，请调整频率或时长');
t = linspace(0,stop_time,points).';
u = A*sin(2*pi*frequency*t);
if ~isproper(sys)
    [r,p,k] = residue(num,den); disp(r); disp(p); disp(k);
    figure; bode(sys); grid on;
else
    y = lsim(sys,u,t);
    figure; plot(t,u,'--',t,y,'LineWidth',1.5); grid on;
    xlabel('Time (s)'); ylabel('Amplitude'); legend('Input','Output');
end
figure; bode(Gopen); grid on;
