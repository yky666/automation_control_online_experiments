%% 自控实验四 任务三增强版 K=1恒定，多图可视化+图上标注动态指标
clear; clc; close all;

%% 1.构造三个系统
num1 = 10;
den1 = conv([1 0], conv([0.1 1], [0.1 1]));
G1 = tf(num1, den1);
sys1 = feedback(G1,1);   % C1=1uF 三阶

num2 = 10;
den2 = conv([1 0], conv([0.1 1], [0.01 1]));
G2 = tf(num2, den2);
sys2 = feedback(G2,1);   % C1=0.1uF 三阶

num3 =10;
den3 = conv([1 0], [0.1 1]);
G3 = tf(num3, den3);
sys3 = feedback(G3,1);   % 二阶系统

%% 获取动态性能指标 5%误差带
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

%% ==========图1：阶跃响应，图中标注Mp tp ts==========
figure('Name','任务三：阶跃响应+动态指标标注');
t = 0:0.01:4;
[y1,~] = step(sys1, t);
[y2,~] = step(sys2, t);
[y3,~] = step(sys3, t);

p1=plot(t,y1,'b-','LineWidth',1.5); hold on;
p2=plot(t,y2,'r-','LineWidth',1.5);
p3=plot(t,y3,'m-','LineWidth',1.5);

% 标记各个系统峰值点
peak1_y = 1 + info1.Overshoot/100;
plot(info1.PeakTime, peak1_y,'bo','MarkerSize',7,'MarkerFaceColor','b');
text(info1.PeakTime+0.04,peak1_y,sprintf('Mp1=%.1f%%\ntp1=%.2fs',info1.Overshoot,info1.PeakTime),'FontSize',8);

peak2_y = 1 + info2.Overshoot/100;
plot(info2.PeakTime, peak2_y,'ro','MarkerSize',7,'MarkerFaceColor','r');
text(info2.PeakTime+0.04,peak2_y,sprintf('Mp2=%.1f%%\ntp2=%.2fs',info2.Overshoot,info2.PeakTime),'FontSize',8);

peak3_y = 1 + info3.Overshoot/100;
plot(info3.PeakTime, peak3_y,'mo','MarkerSize',7,'MarkerFaceColor','m');
text(info3.PeakTime+0.04,peak3_y,sprintf('Mp3=%.1f%%\ntp3=%.2fs',info3.Overshoot,info3.PeakTime),'FontSize',8);

% 画调节时间竖线
xline(info1.SettlingTime,'b--','ts1','LineWidth',1.2);
xline(info2.SettlingTime,'r--','ts2','LineWidth',1.2);
xline(info3.SettlingTime,'m--','ts3','LineWidth',1.2);

yline(1,'k-.','稳态值','LineWidth',1);

legend([p1,p2,p3],{'C_1=1\muF 三阶','C_1=0.1\muF 三阶','二阶系统'},'Location','best');
grid on;
title('K=1不变：不同时间常数单位阶跃响应（标注动态指标）');
xlabel('t (s)'); ylabel('输出幅值');
hold off;

%% ==========图2：闭环零极点分布图（可视化极点位置对比）==========
figure('Name','闭环零极点对比');
pzmap(sys1,sys2,sys3);
pz_lines = findobj(gcf,'Type','line');
for i = 1:length(pz_lines)
    set(pz_lines(i),'MarkerSize',8,'LineWidth',1.5);
end
legend('C_1=1\muF 三阶','C_1=0.1\muF 三阶','二阶系统','Location','best');
grid on;
title('三套模型闭环零‑极点分布对比');

%% ==========图3：Bode伯德图对比（频域可视化，看带宽、谐振峰值）==========
figure('Name','Bode频域特性对比');
bode(sys1,sys2,sys3);
bode_lines = findobj(gcf,'Type','line');
for i =1:length(bode_lines)
    set(bode_lines(i),'LineWidth',1.4);
end
grid on;
legend('C_1=1\muF 三阶','C_1=0.1\muF 三阶','二阶系统','Location','best');
title('三套闭环系统Bode图对比');
