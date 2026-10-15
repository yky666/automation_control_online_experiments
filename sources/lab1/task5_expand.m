%自主扩展实验：比较参数变化和反馈结构变化对闭环传递函数的影响

%清理工作区和命令行窗口
clc;

s = tf('s');

%% 扩展1：改变开环增益K，观察闭环极点与阶跃响应变化
K_list = [0.5 1 2 5];               % 选取不同开环增益
figure('Name','gain_sweep','Color','w');
hold on;
grid on;

for i = 1:length(K_list)
    K = K_list(i);
    G = K*(2*s + 1)/(s^2 + 2*s + 3);
    T = feedback(G,1,-1);           % 单位负反馈闭环传递函数
    step(T);
    fprintf('K = %.1f 时的闭环传递函数：\n',K);
    T
    fprintf('K = %.1f 时的闭环极点：\n',K);
    pole(T)
    info = stepinfo(T);
    fprintf(['K=%.1f: 稳态值=%.4f, 上升时间=%.4f s, ', ...
        '调节时间=%.4f s, 超调量=%.2f%%\n'], ...
        K,dcgain(T),info.RiseTime,info.SettlingTime,info.Overshoot);
end

legend('K=0.5','K=1','K=2','K=5');
title('不同开环增益K下的单位负反馈闭环阶跃响应');
xlabel('时间/s');
ylabel('输出响应');

%% 扩展2：将单位反馈改为非单位反馈 H(s)=1/(s+1)
G0 = (2*s + 1)/(s^2 + 2*s + 3);
H1 = 1;
H2 = 1/(s + 1);

T_unit = feedback(G0,H1,-1)         % 单位负反馈闭环
T_dynamic = feedback(G0,H2,-1)      % 动态反馈环节下的闭环

figure('Name','feedback_structure','Color','w');
step(T_unit,T_dynamic);
grid on;
legend('H(s)=1','H(s)=1/(s+1)');
title('单位反馈与动态反馈结构的闭环响应比较');
xlabel('时间/s');
ylabel('输出响应');
