% task1 绘制开环传递函数阶跃响应曲线
sys=tf(4,[3 1]);
step(sys)