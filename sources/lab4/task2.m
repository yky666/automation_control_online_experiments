%% 自控实验四 任务二 C1=0.1uF  K=5,11,17
clear; clc; close all;

%开环传递函数 G(s)=10K / [s(0.1s+1)(0.01s+1)]
den_c1 = conv([1 0], conv([0.1 1], [0.01 1]));

num_K5  = 10*5;
num_K11 = 10*11;
num_K17 = 10*17;

%构造开环
G5  = tf(num_K5, den_c1);
G11 = tf(num_K11,den_c1);
G17 = tf(num_K17,den_c1);

%单位负反馈闭环
sys5  = feedback(G5, 1);
sys11 = feedback(G11,1);
sys17 = feedback(G17,1);

%% ==========1.阶跃响应==========
figure('Name','C1=0.1uF 阶跃响应 K=5,11,17');
t = 0:0.01:1.0;
[y5,~]  = step(sys5, t);
[y11,~] = step(sys11,t);
[y17,~] = step(sys17,t);

plot(t,y5,'b-','LineWidth',1.5); hold on;
plot(t,y11,'r-','LineWidth',1.5);
plot(t,y17,'m-','LineWidth',1.5);

legend('K=5 稳定（减幅振荡）','K=11 临界稳定（等幅振荡）','K=17 不稳定（增幅振荡）','Location','best');
grid on;
title('C_1=0.1\muF 单位阶跃响应');
xlabel('时间 t (s)'); ylabel('输出幅值');
hold off;

%% ==========2.根轨迹==========
figure('Name','C1=0.1uF 根轨迹');
G_open = tf(10, den_c1);
rlocus(G_open);
set(findobj(gcf,'type','line'),'LineWidth',1.5);
grid on;
title('G(s)=\dfrac{10K}{s(0.1s+1)(0.01s+1)} 根轨迹');

%% ==========3.闭环零极点图==========
figure('Name','C1=0.1uF 闭环零极点');
pzmap(sys5, sys11, sys17);
pz_lines = findobj(gcf,'Type','line');
for i = 1:length(pz_lines)
    set(pz_lines(i),'MarkerSize',8,'LineWidth',1.5);
end
legend('K=5','K=11','K=17','Location','best');
grid on;
title('C_1=0.1\muF 闭环系统零极点分布');
