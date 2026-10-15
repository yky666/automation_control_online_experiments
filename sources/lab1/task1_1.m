%任务1-1：建立控制系统传递函数模型 G(s)=5/[s(s+1)(s^2+4s+4)]
clc;        %清空命令窗口

%% 写法1：定义s算子，直接用数学表达式书写
s = tf('s');   %定义拉普拉斯算子s，可直接书写传递函数表达式
Gs1 = 5 / ( s*(s+1)*(s^2+4*s+4) )  

%% 写法2：分子分母多项式系数形式
% 展开分母 s(s+1)(s²+4s+4) = s^4 +5*s^3 +8*s^2 +4*s
num1 = [5];             %分子多项式系数：5
den1 = [1 5 8 4 0];     %分母多项式系数：s^4+5s^3+8s^2+4s
Gs1_coeff = tf(num1, den1)  %构建传递函数
if exist('printsys','file') == 2
    printsys(num1, den1)    %旧版 MATLAB 的格式化打印函数
else
    disp(Gs1_coeff)         %新版 MATLAB 已移除 printsys，直接显示 tf 对象
end
