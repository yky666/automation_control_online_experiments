%% 任务二：串联超前校正装置设计
% 要求：ess<=0.1, Mp<=27.5%, ts<=1.7s
% 采用两级串联无源超前校正
clear; clc; close all;

%% ===== 1. 原系统及稳态误差要求 =====
% G0(s)=K/[s(0.5s+1)(s/30+1)]

ess_req = 0.1;
Mp_req = 27.5;
ts_req = 1.7;

K = 10;                    % Kv=K>=10
num = K;
den = conv([1,0],conv([0.5,1],[1/30,1]));
G0 = tf(num,den);

disp('========== 原系统 ==========');
G0

Kv0 = dcgain(minreal(tf([1,0],1)*G0));
ess0 = 1/Kv0;

fprintf('速度误差系数 Kv = %.4f\n',Kv0);
fprintf('单位斜坡稳态误差 ess = %.4f\n',ess0);

%% ===== 2. 时域指标转换为频域指标 =====
% 根据超调量计算阻尼比
zeta = -log(Mp_req/100) / ...
    sqrt(pi^2+log(Mp_req/100)^2);

% 采用2%误差带：ts≈4/(zeta*wn)
wn_min = 4/(zeta*ts_req);

% 二阶系统阻尼比与相位裕度近似关系
phim_min = atan(2*zeta / ...
    sqrt(sqrt(1+4*zeta^4)-2*zeta^2))*180/pi;

phim1 = 50;               % 设计目标相位裕度

fprintf('\n========== 频域指标转换 ==========\n');
fprintf('阻尼比下限 zeta = %.4f\n',zeta);
fprintf('自然频率下限 wn = %.4f rad/s\n',wn_min);
fprintf('理论相位裕度约 = %.4f deg\n',phim_min);
fprintf('设计目标相位裕度 = %.2f deg\n',phim1);

%% ===== 3. 未校正系统频域分析 =====
[Gm0,Pm0,Wcg0,Wcp0] = margin(G0);

fprintf('\n========== 校正前频域指标 ==========\n');
fprintf('相位裕度 = %.4f deg\n',Pm0);
fprintf('截止频率 = %.4f rad/s\n',Wcp0);

%% ===== 4. 两级无源超前校正设计 =====
% 选取满足设计要求的超前网络参数
% 两级串联，每一级具有相同参数

alpha = 3;
wm = 6;                    % 最大相位超前频率

w1 = wm/sqrt(alpha);
w2 = wm*sqrt(alpha);

% 单级无源超前校正网络
numc = (1/alpha)*[1/w1,1];
denc = [1/w2,1];

Gc1 = tf(numc,denc);

% 两级无源超前校正网络串联
Gc = Gc1*Gc1;

% 增益补偿，使低频增益保持不变
G = alpha^2*Gc*G0;

T = 1/w2;

disp('========== 校正装置 ==========');
disp('单级无源超前校正网络 Gc1：');
Gc1

disp('两级串联无源超前校正网络 Gc：');
Gc

disp('校正后开环传递函数 G：');
G

fprintf('alpha = %.6f\n',alpha);
fprintf('T = %.6f\n',T);
fprintf('wm = %.4f rad/s\n',wm);
fprintf('w1 = %.4f rad/s\n',w1);
fprintf('w2 = %.4f rad/s\n',w2);

%% ===== 5. 校正后频域指标 =====
[Gm1,Pm1,Wcg1,Wcp1] = margin(G);

fprintf('\n========== 校正后频域指标 ==========\n');
fprintf('幅值裕度 = %.4f\n',Gm1);
fprintf('幅值裕度(dB) = %.4f dB\n',20*log10(Gm1));
fprintf('相位裕度 = %.4f deg\n',Pm1);
fprintf('截止频率 = %.4f rad/s\n',Wcp1);
fprintf('幅值穿越频率 = %.4f rad/s\n',Wcg1);

%% ===== 6. 构造闭环系统 =====
sys0 = feedback(G0,1);
sys = feedback(G,1);

stable0 = isstable(sys0);
stable1 = isstable(sys);

fprintf('\n========== 稳定性验证 ==========\n');
fprintf('校正前闭环是否稳定：%d\n',stable0);
fprintf('校正后闭环是否稳定：%d\n',stable1);

%% ===== 7. 校正后时域性能指标 =====
% 使用stepinfo计算超调量、调节时间等
% 2%稳态误差带

if stable1
    info = stepinfo(sys,'SettlingTimeThreshold',0.02);

    Mp = info.Overshoot;
    ts = info.SettlingTime;
    tr = info.RiseTime;
    tp = info.PeakTime;

    % 校正后单位斜坡稳态误差
    Kv = dcgain(minreal(tf([1,0],1)*G));
    ess = 1/Kv;

    fprintf('\n========== 校正后时域指标 ==========\n');
    fprintf('上升时间 tr = %.4f s\n',tr);
    fprintf('峰值时间 tp = %.4f s\n',tp);
    fprintf('超调量 Mp = %.4f %%\n',Mp);
    fprintf('调节时间 ts = %.4f s\n',ts);
    fprintf('速度误差系数 Kv = %.4f\n',Kv);
    fprintf('稳态速度误差 ess = %.4f\n',ess);
else
    Mp = NaN;
    ts = Inf;
    ess = Inf;
    disp('校正后闭环不稳定，无法满足时域指标');
end

%% ===== 8. 绘图 =====
% 避免margin绘图与bode图叠加冲突
close all force;

% Figure 1：校正前后Bode图
figure(1);
bode(G0,G);
grid on;
title('任务二：校正前后系统Bode图');

% Figure 2：校正后Bode图
figure(2);
bode(G);
grid on;
title('任务二：校正后系统Bode图');

% Figure 3：校正后单位阶跃响应
figure(3);
t = 0:0.001:3;
step(sys,t);
grid on;
title('任务二：校正后闭环单位阶跃响应');
xlabel('时间(s)');
ylabel('输出幅值');

% Figure 4：校正网络幅频特性
figure(4);
bode(Gc1,Gc);
grid on;
title('任务二：单级与两级无源超前校正网络');

% Figure 5：校正后阶跃响应及性能指标
figure(5);
[y,t] = step(sys,t);
y = squeeze(y);

plot(t,y,'b','LineWidth',1.5);
hold on;
yline(1,'k--','稳态值');
yline(1.02,'r--','+2%');
yline(0.98,'r--','-2%');

grid on;
xlabel('时间(s)');
ylabel('输出幅值');
title('任务二：校正后阶跃响应及2%误差带');
legend('校正后阶跃响应','稳态值', ...
       '+2%误差带','-2%误差带', ...
       'Location','best');

%% ===== 9. 设计要求检验 =====
fprintf('\n========== 设计要求检验 ==========\n');

fprintf('稳态误差：%.4f <= %.4f，',ess,ess_req);
if ess <= ess_req+1e-8
    fprintf('满足\n');
else
    fprintf('不满足\n');
end

fprintf('超调量：%.4f%% <= %.4f%%，',Mp,Mp_req);
if Mp <= Mp_req
    fprintf('满足\n');
else
    fprintf('不满足\n');
end

fprintf('调节时间：%.4fs <= %.4fs，',ts,ts_req);
if ts <= ts_req
    fprintf('满足\n');
else
    fprintf('不满足\n');
end

if stable1 && ess<=ess_req+1e-8 && ...
        Mp<=Mp_req && ts<=ts_req
    disp('结论：串联超前校正设计满足全部要求！');
else
    disp('结论：部分指标未满足，需要调整参数。');
end
