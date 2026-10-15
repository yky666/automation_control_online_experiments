%任务1-2：建立控制系统传递函数模型
% G(s)=(s^2+4s+2)/[s^3(s^2+4)(s^2+4s)]

%清理工作区和命令行窗口
clc;

%% 写法1：定义s算子，直接写数学表达式
s = tf('s');
Gs2 = (s^2 + 4*s + 2)/(s^3*(s^2 + 4)*(s^2 + 4*s))

%% 写法2：使用分子、分母多项式系数
% 分母展开：
% s^3(s^2+4)(s^2+4s)=s^4(s^2+4)(s+4)
% =s^7+4s^6+4s^5+16s^4
num2 = [1 4 2];                  % 分子 s^2+4s+2
den2 = [1 4 4 16 0 0 0 0];       % 分母 s^7+4s^6+4s^5+16s^4

Gs2_coeff = tf(num2,den2)
if exist('printsys','file') == 2
    printsys(num2,den2)
else
    disp(Gs2_coeff)
end
