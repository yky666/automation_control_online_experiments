clear; clc; close all; set(0,'DefaultFigureVisible','off'); root='D:/Kaiyuan/UGRD/大三/作业/自控实验/第四次/report_figures';
D1=conv([1 0],conv([0.1 1],[0.1 1])); G1=tf(10,D1); K1=[1 2 3]; S1=arrayfun(@(k) feedback(k*G1,1),K1,'UniformOutput',false);
f=figure('Color','w','Position',[80 80 1200 480]); subplot(1,2,1); rlocus(G1); grid on; xline(0,'k:','LineWidth',1); title('Task1 根轨迹'); xlabel('实部 (rad/s)'); ylabel('虚部 (rad/s)');
subplot(1,2,2); pzmap(S1{:}); grid on; xline(0,'k:','LineWidth',1); title('Task1 闭环极点'); legend('K=1','K=2','K=3','Location','best'); exportgraphics(f,fullfile(root,'task1_stability.png'),'Resolution',180); close(f);
D2=conv([1 0],conv([0.1 1],[0.01 1])); G2=tf(10,D2); K2=[5 11 17]; S2=arrayfun(@(k) feedback(k*G2,1),K2,'UniformOutput',false);
f=figure('Color','w','Position',[80 80 1200 480]); subplot(1,2,1); rlocus(G2); grid on; xline(0,'k:','LineWidth',1); title('Task2 根轨迹'); xlabel('实部 (rad/s)'); ylabel('虚部 (rad/s)');
subplot(1,2,2); pzmap(S2{:}); grid on; xline(0,'k:','LineWidth',1); title('Task2 闭环极点'); legend('K=5','K=11','K=17','Location','best'); exportgraphics(f,fullfile(root,'task2_stability.png'),'Resolution',180); close(f);
