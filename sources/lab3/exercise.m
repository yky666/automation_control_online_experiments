%exercise 零点 z=-5,-2,-1 对系统阶跃响应的影响
clear; clc; close all;

den = [1 2 10];          % 分母：s^2+2s+10，所有系统相同

figure; hold on; grid on;

% 1) 先画原系统（无零点）G(s)=10/(s^2+2s+10)
sys0 = tf([10], den);
step(sys0, 10);

% 2) 再画三个带零点的系统：2(s+5), 5(s+2), 10(s+1) → 分子 [2 10],[5 10],[10 10]
j = [2 5 10];
for i = 1:3
    num = [j(i) 10];
    sys = tf(num, den);
    step(sys, 10);
end

hold off;
title('零点 z 变化时系统的阶跃响应曲线');   % 注意：直接写"z"，不要加反斜杠
xlabel('时间 t/s');  ylabel('输出 y(t)');
legend('原系统(无零点)', 'z=-5', 'z=-2', 'z=-1', 'Location','southeast');
