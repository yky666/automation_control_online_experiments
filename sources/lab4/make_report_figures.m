clear; clc; close all;
root='D:/Kaiyuan/UGRD/大三/作业/自控实验/第四次/report_figures';
set(0,'DefaultFigureVisible','off');
% Task 1: same transfer function and gains as task1.m
D1=conv([1 0],conv([0.1 1],[0.1 1])); G1=tf(10,D1); k1=[1 2 3]; S1=arrayfun(@(k) feedback(k*G1,1),k1,'UniformOutput',false);
f=figure('Color','w','Position',[80 80 1200 480]); tiledlayout(1,2,'Padding','compact','TileSpacing','compact');
nexttile; rlocus(G1); grid on; xline(0,'k:','LineWidth',1); title('Task1 根轨迹'); xlabel('实部 (rad/s)'); ylabel('虚部 (rad/s)');
nexttile; pzmap(S1{:}); grid on; xline(0,'k:','LineWidth',1); title('Task1 闭环极点'); legend('K=1','K=2','K=3','Location','best');
exportgraphics(f,fullfile(root,'task1_stability.png'),'Resolution',180); close(f);
% Task 2: same transfer function and gains as task2.m
D2=conv([1 0],conv([0.1 1],[0.01 1])); G2=tf(10,D2); k2=[5 11 17]; S2=arrayfun(@(k) feedback(k*G2,1),k2,'UniformOutput',false);
f=figure('Color','w','Position',[80 80 1200 480]); tiledlayout(1,2,'Padding','compact','TileSpacing','compact');
nexttile; rlocus(G2); grid on; xline(0,'k:','LineWidth',1); title('Task2 根轨迹'); xlabel('实部 (rad/s)'); ylabel('虚部 (rad/s)');
nexttile; pzmap(S2{:}); grid on; xline(0,'k:','LineWidth',1); title('Task2 闭环极点'); legend('K=5','K=11','K=17','Location','best');
exportgraphics(f,fullfile(root,'task2_stability.png'),'Resolution',180); close(f);
% Task 3: exact models from task3.m, clean step plot and poles
D3=conv([1 0],conv([0.1 1],[0.1 1])); A=tf(10,D3); B=tf(10,D2); C=tf(10,conv([1 0],[0.1 1])); T={feedback(A,1),feedback(B,1),feedback(C,1)};
t=0:0.01:4; f=figure('Color','w','Position',[80 80 920 560]); hold on;
colors={[0.00 0.25 0.85],[0.85 0.12 0.12],[0.70 0.00 0.70]}; names={'C_1=1 \muF 三阶','C_1=0.1 \muF 三阶','二阶系统'};
for i=1:3, [y,tt]=step(T{i},t); plot(tt,y,'LineWidth',1.8,'Color',colors{i}); end
 yline(1,'k:','稳态值'); grid on; title('Task3 K=1：三种模型的单位阶跃响应'); xlabel('时间 t (s)'); ylabel('输出'); legend(names,'Location','best'); hold off;
exportgraphics(f,fullfile(root,'task3_step_clean.png'),'Resolution',180); close(f);
f=figure('Color','w','Position',[80 80 720 520]); pzmap(T{:}); grid on; xline(0,'k:','LineWidth',1); title('Task3 K=1：闭环极点分布'); legend(names,'Location','best');
exportgraphics(f,fullfile(root,'task3_stability.png'),'Resolution',180); close(f);
% Numeric pole and stepinfo check
for i=1:3, fprintf('Task3 model %d poles:\n',i); disp(pole(T{i})); q=stepinfo(T{i},'SettlingTimeThreshold',0.05); fprintf('Mp=%.2f tp=%.3f ts=%.3f\n',q.Overshoot,q.PeakTime,q.SettlingTime); end
