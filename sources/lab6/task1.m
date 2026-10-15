% 任务1 串联有源超前校正设计 G0(s)=K/(s(s+2)), Kv=20, 相位裕度>35°,幅值裕度>10dB
% 1. 根据静态速度误差系数Kv求K
% Kv = lim s*G0(s) = K/2 =20 => K=40
num0=40;
den0=conv([1,0],[1,2]);
G0=tf(num0,den0); %未校正系统开环传递函数

[Gm,Pm,Wcg,Wcp]=margin(G0); %未校正系统频域指标
w=0.1:0.1:100; %频率范围
[mag, phase]=bode(G0,w);
magdb=20*log10(mag);

phim1=35; %期望相位裕度
deta=8; %预留补偿相位
phim=phim1-Pm+deta; %需要超前提供的最大相位角
beta=(1-sin(phim*pi/180))/(1+sin(phim*pi/180)); %计算β

% 找到满足幅值衰减10log10(1/beta)处的频率作为新截止频率wc
n=find(magdb+10*log10(1/beta)<=0.0001);
wc=w(n(1));

% 超前校正两个转折频率
w1=wc*sqrt(beta);
w2=wc/sqrt(beta);
T=1/w2;

numc=[1/w1, 1];
denc=[1/w2, 1];
Gc=tf(numc, denc); %超前校正装置传递函数

G=Gc*G0; %校正后开环传递函数
[Gmc, Pmc, Wcgc, Wcpc]=margin(G);
GmcdB=20*log10(Gmc);

disp('校正装置传递函数Gc');
Gc
disp('校正后开环传递函数G=Gc*G0');
G
disp('校正后频域指标：幅值裕度(dB),相位裕度(°),截止频率wc(rad/s)');
[GmcdB,Pmc,Wcpc]
disp('校正装置参数 T 和 beta');
[T,beta]

%绘制伯德图，对比校正前后
figure;
bode(G0,G);
grid on;
hold on;
margin(G);
legend('校正前G0','校正后G');