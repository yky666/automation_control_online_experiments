num=10;
den=[0.2,1,0,0];
G0=tf(num,den);
[Gm,Pm,Wcg,Wcp]=margin(G0);
w=0.1:1:10000;
[mag,phase]=bode(G0,w);
mag = squeeze(mag);    %【关键修复】去掉多余维度，新版matlab必须加
phase = squeeze(phase);
magdb=20*log10(mag);

phim1=35;
deta=18;
phim=(phim1-Pm+deta)/2;
alpha=(1+sin(phim*pi/180))/(1-sin(phim*pi/180));

n=find(magdb +10*log10(alpha) <= 0.0001);
wc=w(n(1));
w1=wc/sqrt(alpha);
w2=sqrt(alpha)*wc;

numc=(1/alpha)*[1/w1,1];
denc=[1/w2,1];
Gc1=tf(numc,denc);
Gc=Gc1*Gc1; %两级超前串联
G=(alpha)^2*Gc*G0;

disp('====计算结果====');
disp('单级校正网络Gc1：');
Gc1
disp('两级串联Gc：');
Gc
disp('校正后开环G：');
G
T=1/w2;
disp(['alpha = ',num2str(alpha),', T = ',num2str(T)]);

%========绘图：分开figure，杜绝叠加报错========

%% 清理之前的绘图窗口
close all force;

%% 1. 计算稳定裕度（不绘图）
[Gm0,Pm0,Wcg0,Wcp0] = margin(G0);
[Gm1,Pm1,Wcg1,Wcp1] = margin(G);

fprintf('\n===== 校正后系统 =====\n');
fprintf('幅值裕度 = %.4f\n',Gm1);
fprintf('相位裕度 = %.4f deg\n',Pm1);
fprintf('截止频率 = %.4f rad/s\n',Wcp1);
fprintf('幅值穿越频率 = %.4f rad/s\n',Wcg1);

%% 2. 校正前后的Bode图
figure(1);
bode(G0,G);
grid on;
title('校正前后系统Bode图');

%% 3. 单独绘制校正后的Bode图
figure(2);
bode(G);
grid on;
title('校正后系统Bode图');

%% 4. 校正后闭环阶跃响应
sys0 = feedback(G0,1);
sys = feedback(G,1);

figure(3);
step(sys,0:0.001:3);
grid on;
title('校正后闭环系统单位阶跃响应');

%% 5. 验证稳定性
fprintf('\n校正后闭环是否稳定：%d\n',isstable(sys));
