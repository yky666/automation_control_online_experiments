% task3 绘制单位负反馈回路阶跃响应曲线
sys=tf(100,[1 3 0]);
sysc=feedback(sys,1);
step(sysc)