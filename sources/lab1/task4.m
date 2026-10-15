%任务4：已知开环 G(s)=(2s+1)/(s^2+2s+3)，求单位负反馈闭环传递函数

%清理工作区和命令行窗口
clc;

%% 写法1：使用 cloop() 函数
% [numc,denc]=cloop(num,den,sign)，sign=-1 表示负反馈
num = [2 1];        % 开环分子：2s+1
den = [1 2 3];      % 开环分母：s^2+2s+3
if exist('cloop','file') == 2
    [numc,denc] = cloop(num,den,-1);
    Gc_cloop = tf(numc,denc)
else
    % R2024b 中 cloop 可能已移除，使用等价的 feedback 实现
    Gc_cloop = feedback(tf(num,den),1,-1)
end

%% 写法2：使用 feedback() 函数
% sys=feedback(sys1,sys2,sign)，sys1为前向通道，sys2为反馈通道
s = tf('s');
G_open = (2*s + 1)/(s^2 + 2*s + 3);
H = 1;                              % 单位反馈 H(s)=1
Gc_feedback = feedback(G_open,H,-1)

% 数值验证两种路径得到的系统完全等价
equivalence_error = norm(Gc_cloop - Gc_feedback, inf)

% 理论上单位负反馈闭环为 G/(1+G)，结果应为：
% (2s+1)/(s^2+4s+4)
