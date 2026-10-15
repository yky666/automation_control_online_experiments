% Task3 二阶控制系统环节的频率特性测试验证
% 频率从0.1Hz一直到150Hz

clc;clear;close all;
s=tf('s');
Phi = 500/(s^2 +10*s +500);

% 频率梯度
f = [0.1,1,5,8,10,15,20,25,30,35,40,50,80,100,150];
w = 2*pi*f;
[mag_meas,phase_meas]=bode(Phi,w);
mag_meas=squeeze(mag_meas);
phase_meas=squeeze(phase_meas);
L_meas = 20*log10(mag_meas);

% 计算并绘制伯德图
w_full = logspace(-1,3,300);
[mag_full,phase_full]=bode(Phi,w_full);
mag_full=squeeze(mag_full);
phase_full=squeeze(phase_full);
L_full = 20*log10(mag_full);

figure;
subplot(2,1,1);
semilogx(w_full,L_full,'b-','LineWidth',1.2);hold on;
semilogx(w,L_meas,'ro','MarkerSize',6,'DisplayName','实验测点');
grid on; title('二阶闭环系统 \Phi(s)=500/(s^2+10s+500)'); ylabel('Magnitude(dB)');legend('show');hold off;

subplot(2,1,2);
semilogx(w_full,phase_full,'b-','LineWidth',1.2);hold on;
semilogx(w,phase_meas,'ro','MarkerSize',6,'DisplayName','实验测点');
grid on; xlabel('Frequency(rad/s)');ylabel('Phase(deg)');legend('show');hold off;

%输出表格
fprintf('\n二阶闭环系统\n');
fprintf('f(Hz)\tω(rad/s)\t20lg|Φ|(dB)\t相位φ(°)\n');
for i=1:length(f)
    fprintf('%.1f\t%.3f\t%.3f\t\t%.2f\n',f(i),w(i),L_meas(i),phase_meas(i));
end