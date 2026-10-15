% 例题1 绘制反馈回路阶跃响应曲线
sys=tf(100,[1 5 0]);
sysc=feedback(sys,1);
step(sysc)