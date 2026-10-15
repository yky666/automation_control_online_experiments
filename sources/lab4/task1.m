%% 自控实验四 任务一：三阶系统稳定性分析 C1=1uF
clear; clc; close all;

% 开环传递函数 G(s)=10K / [s*(0.1s+1)*(0.1s+1)]
num_K1 = 10*1;   % K=1 稳定(减幅振荡)
num_K2 = 10*2;   % K=2 临界稳定(等幅振荡)
num_K3 = 10*3;   % K=3 不稳定(增幅振荡)
den = conv([1 0], conv([0.1 1], [0.1 1])); 

G1 = tf(num_K1, den);
G2 = tf(num_K2, den);
G3 = tf(num_K3, den);

% 单位负反馈闭环
sys_cl1 = feedback(G1,1);
sys_cl2 = feedback(G2,1);
sys_cl3 = feedback(G3,1);

% ========== 1. 阶跃响应：限定仿真时间0~5秒 ==========
figure('Name','三种状态阶跃响应 C1=1uF');
t = 0:0.01:2;   % 时间范围0~2s，观察振荡
[y1,~] = step(sys_cl1,t);
[y2,~] = step(sys_cl2,t);
[y3,~] = step(sys_cl3,t);

plot(t,y1,'b-','LineWidth',1.5); hold on;
plot(t,y2,'r-','LineWidth',1.5);
plot(t,y3,'m-','LineWidth',1.5);   % m 品红色，替代十六进制橙色

legend('K=1 稳定（减幅振荡）','K=2 临界稳定（等幅振荡）','K=3 不稳定（增幅振荡）','Location','best');
grid on;
title('三阶系统单位阶跃响应，C_1=1\muF');
xlabel('时间 t (s)'); ylabel('输出幅值');
hold off;

% ========== 2. 根轨迹：加粗线条 ==========
figure('Name','根轨迹图');
rlocus(G1);
set(findobj(gcf,'type','line'),'LineWidth',1.5); % 加粗根轨迹线条
grid on;
title('开环传递函数 G(s)=10K/[s(0.1s+1)^2] 根轨迹');

% ========== 3. 闭环零极点图：加粗、放大标记点 ==========
figure('Name','闭环零极点图');
pzmap(sys_cl1, sys_cl2, sys_cl3);
% 找到零极点标记，放大
pz_lines = findobj(gcf,'Type','line');
for i = 1:length(pz_lines)
    set(pz_lines(i),'MarkerSize',8,'LineWidth',1.5);
end
legend('K=1','K=2','K=3','Location','best');
grid on;
title('闭环系统零极点分布');
