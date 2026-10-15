% task4 系统在输入1(t)+t*1(t)激励下响应
num=[1 1];
den=[1 1 1];
G=tf(num,den);
t=[0:0.1:10];
u=1+t;
lsim(G,u,t),hold on,plot(t,u,'r');
grid on;