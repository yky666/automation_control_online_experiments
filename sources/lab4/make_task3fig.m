clear; clc; close all; set(0,'DefaultFigureVisible','off');
D1=conv([1 0],conv([0.1 1],[0.1 1])); D2=conv([1 0],conv([0.1 1],[0.01 1])); D3=conv([1 0],[0.1 1]); T={feedback(tf(10,D1),1),feedback(tf(10,D2),1),feedback(tf(10,D3),1)};
t=0:0.01:4; f=figure('Color','w','Position',[80 80 900 550]); hold on; colors={[0 .25 .85],[.85 .12 .12],[.7 0 .7]}; names={'C_1=1 \muF 三阶','C_1=0.1 \muF 三阶','二阶系统'};
for i=1:3, [y,tt]=step(T{i},t); plot(tt,y,'LineWidth',1.8,'Color',colors{i});end
yline(1,'k:','稳态值'); grid on; title('Task3 K=1：三种模型的单位阶跃响应'); xlabel('时间 t (s)'); ylabel('输出'); legend(names,'Location','best'); hold off; exportgraphics(f,'D:/Kaiyuan/UGRD/大三/作业/自控实验/第四次/report_figures/task3_step_clean.png','Resolution',180);close(f);
f=figure('Color','w','Position',[80 80 720 520]); pzmap(T{:}); grid on; xline(0,'k:','LineWidth',1); title('Task3 K=1：闭环极点分布'); legend(names,'Location','best'); exportgraphics(f,'D:/Kaiyuan/UGRD/大三/作业/自控实验/第四次/report_figures/task3_stability.png','Resolution',180);close(f);
for i=1:3, fprintf('Task3 model %d poles: ',i); fprintf('%.5f%+.5fi ',pole(T{i})); q=stepinfo(T{i},'SettlingTimeThreshold',0.05); fprintf('Mp=%.2f tp=%.3f ts=%.3f\n',q.Overshoot,q.PeakTime,q.SettlingTime);end
