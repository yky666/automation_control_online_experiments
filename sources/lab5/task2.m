% Task2 惯性环节的频率特性测试验证
% 惯性时间常数T = RC = 100 kΩ x 0.01μF = 1ms 。

clc;clear;close all;
s=tf('s');
T=1e-3;
G_inertia = 1/(T*s+1);

f = [1,5,20,100,150,200,500,1000,2000,5000,1e4,5e4,1e5];
w = 2*pi*f;
[mag_meas,phase_meas]=bode(G_inertia,w);
mag_meas=squeeze(mag_meas);
phase_meas=squeeze(phase_meas);
L_meas = 20*log10(mag_meas);

w_full = logspace(0,6,200);
[mag_full,phase_full]=bode(G_inertia,w_full);
mag_full=squeeze(mag_full);
phase_full=squeeze(phase_full);
L_full = 20*log10(mag_full);

figure;
subplot(2,1,1);
semilogx(w_full,L_full,'b-','LineWidth',1.2);hold on;
semilogx(w,L_meas,'ro','MarkerSize',6,'DisplayName','实验测点');
grid on; title('惯性环节 T=1ms'); ylabel('Magnitude(dB)');legend('show');hold off;

subplot(2,1,2);
semilogx(w_full,phase_full,'b-','LineWidth',1.2);hold on;
semilogx(w,phase_meas,'ro','MarkerSize',6,'DisplayName','实验测点');
grid on; xlabel('Frequency(rad/s)');ylabel('Phase(deg)');legend('show');hold off;

%打印表格
fprintf('\n惯性环节 T=1ms\n');
fprintf('f(Hz)\tω(rad/s)\t20lg|G|(dB)\t相位(°)\n');
for i=1:length(f)
    fprintf('%d\t%.2f\t%.3f\t%.2f\n',f(i),w(i),L_meas(i),phase_meas(i));
end