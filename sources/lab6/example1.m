% 例1 频域法有源超前校正装置设计
num=1000;
den=conv([1,0],conv([0.1,1],[0.001,1]));
G0=tf(num,den); %未校正系统的开环传函

[Gm,Pm,Wcg,Wcp]=margin(G0); %未校正系统的频域性能指标
w=0.1:0.1:10000; %确定频率采样的间隔值
[mag, phase]=bode(G0,w); %计算对数幅频响应值
magdb=20*log(mag);
phim1=45;
deta=8;
phim=phim1-Pm+deta; %确定相位超前角
bita=(1-sin(phim*pi/180))/(1+sin(phim*pi/180)); %确定β值

n=find(magdb+10*log10(1/bita)<=0.0001);
%find()函数找出满足该式的magdb向量所有下标值e
wc=w(n(1)); %取第1项为wc是为了最大限度利用超前相位量
w1=wc*sqrt(bita);
w2=wc/sqrt(bita);%确定校正装置的两个转折频率←
numc=[1/w1, 1];
denc=[1/w2,1]; %令k=1,确定校正装置的传递函数~
Gc=tf(numc, denc); %校正后系统的开环传递函数
G=Gc*G0;
[Gmc, Pmc, Wcgc, Wcpc]=margin(G);
%校正前后系统的频域性能指标
GmcdB=20*log10(Gmc);

disp('校正装置的传递函数和校正后系统的开环传递函数'),Gc,G
disp('校正后系统的频域性能指标h,gama,wc'),[GmcdB,Pmc,Wcpc],
disp('校正装置的参数T和bita值'),T=1/w1;[T,bita],
%绘制校正前和校正后的伯德图
bode(G0, G);
%在同一窗口显示校正后的频域指标
hold on,margin(G)