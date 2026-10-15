%% 自控实验 任务三：开环增益不变K=1，不同时间常数对动态性能影响
clear; clc; close all;

%% =========子任务1：C1=1uF 三阶系统=========
num1 = 10;
den1 = conv([1 0], conv([0.1 1], [0.1 1]));
G1 = tf(num1, den1);
sys1 = feedback(G1,1); %单位负反馈闭环

%% =========子任务2：C1=0.1uF 三阶系统=========
num2 = 10;
den2 = conv([1 0], conv([0.1 1], [0.01 1]));
G2 = tf(num2, den2);
sys2 = feedback(G2,1);

%% =========子任务3：二阶系统（移除第二个惯性环节）=========
num3 =10;
den3 = conv([1 0], [0.1 1]);
G3 = tf(num3, den3);
sys3 = feedback(G3,1);

%% =========绘制阶跃响应，三条曲线放同一画布=========
figure('Name','任务三：三组系统阶跃响应对比');
t = 0:0.01:4;
[y1,~] = step(sys1, t);
[y2,~] = step(sys2, t);
[y3,~] = step(sys3, t);

plot(t,y1,'b-','LineWidth',1.5); hold on;
plot(t,y2,'r-','LineWidth',1.5);
plot(t,y3,'m-','LineWidth',1.5);

legend('C_1=1\muF 三阶','C_1=0.1\muF 三阶','二阶系统','Location','best');
grid on;
title('K=1不变，不同时间常数系统单位阶跃响应对比');
xlabel('t (s)'); ylabel('输出');
hold off;

%% =========自动求取动态指标（5%误差带，适合实验报告）=========
info1 = stepinfo(sys1,'SettlingTimeThreshold',0.05);
info2 = stepinfo(sys2,'SettlingTimeThreshold',0.05);
info3 = stepinfo(sys3,'SettlingTimeThreshold',0.05);

fprintf('\n=====C1=1uF 三阶系统指标=====\n');
fprintf('超调量 Mp = %.2f %% \n',info1.Overshoot);
fprintf('峰值时间 tp = %.3f s \n',info1.PeakTime);
fprintf('调节时间 ts = %.3f s \n',info1.SettlingTime);

fprintf('\n=====C1=0.1uF 三阶系统指标=====\n');
fprintf('超调量 Mp = %.2f %% \n',info2.Overshoot);
fprintf('峰值时间 tp = %.3f s \n',info2.PeakTime);
fprintf('调节时间 ts = %.3f s \n',info2.SettlingTime);

fprintf('\n=====二阶系统指标=====\n');
fprintf('超调量 Mp = %.2f %% \n',info3.Overshoot);
fprintf('峰值时间 tp = %.3f s \n',info3.PeakTime);
fprintf('调节时间 ts = %.3f s \n',info3.SettlingTime);
