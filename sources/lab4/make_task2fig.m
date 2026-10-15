clear; clc; close all; set(0,'DefaultFigureVisible','off');
D2=conv([1 0],conv([0.1 1],[0.01 1])); G2=tf(10,D2); k2=[5 11 17]; S2=arrayfun(@(k) feedback(k*G2,1),k2,'UniformOutput',false);
f=figure('Color','w','Position',[80 80 1200 480]); tiledlayout(1,2,'Padding','compact','TileSpacing','compact');
nexttile; rlocus(G2); grid on; xline(0,'k:','LineWidth',1); title('Task2 根轨迹'); xlabel('实部 (rad/s)'); ylabel('虚部 (rad/s)');
nexttile; pzmap(S2{:}); grid on; xline(0,'k:','LineWidth',1); title('Task2 闭环极点'); legend('K=5','K=11','K=17','Location','best');
exportgraphics(f,'D:/Kaiyuan/UGRD/大三/作业/自控实验/第四次/report_figures/task2_stability.png','Resolution',180); close(f);
