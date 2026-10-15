% Task1 比例环节的频率特性测试验证
% R = 100kΩ,1MΩ,10MΩ
% 起始频率f分别为100kHz、10 kHz、1 kHz
clc; clear; close all;
s = tf('s');
Uim = 0.05;   %输入正弦幅值

GBW = 1e6;          %增益带宽积1MHz
f_list_all = {
    logspace(5,7,12),   % R=100k, K=1
    logspace(4,6,12),   % R=1M,  K=10
    logspace(3,5,12)    % R=10M, K=100
};
R_val = [100e3, 1e6, 10e6];
K_val = R_val/100e3;

for idx = 1:3
    K = K_val(idx);
    f = f_list_all{idx};
    w = 2*pi*f;
    fp = GBW / K;
    G_sys = K / (1 + s/(2*pi*fp));

    % 获取离散测点数据
    [mag_meas, phase_meas] = bode(G_sys, w);
    mag_meas = squeeze(mag_meas);
    phase_meas = squeeze(phase_meas);
    Uom = mag_meas * Uim;
    L_meas = 20*log10(mag_meas);

    % =========打印表格=========
    fprintf('\n================ R = %.0f kΩ, K=%.2f ================\n',R_val(idx)/1000,K);
    fprintf('f(Hz)\t\tω(rad/s)\tUom(V)\t\t20lg(Uom/Uim)/dB\t相位φ(°)\n');
    for i=1:length(f)
        fprintf('%.2e\t%.3e\t%.4f\t%.3f\t\t%.2f\n',...
            f(i),w(i),Uom(i),L_meas(i),phase_meas(i));
    end

    % =========自己subplot手动绘制伯德图，避开bode内置句柄bug=========
    fig = figure();
    w_full = logspace(min(log10(w)),max(log10(w)),200); %生成密集连续频率，画光滑伯德曲线
    [mag_full,phase_full] = bode(G_sys,w_full);
    mag_full = squeeze(mag_full);
    phase_full = squeeze(phase_full);
    L_full = 20*log10(mag_full);

    % 幅频子图
    subplot(2,1,1);
    semilogx(w_full, L_full, 'b-','LineWidth',1.2); hold on;
    semilogx(w, L_meas, 'ro','MarkerSize',6,'DisplayName','实验测试点');
    grid on;
    title(['比例环节 R=',num2str(R_val(idx)/1000),' k\Omega, K=',num2str(K)]);
    ylabel('Magnitude (dB)');
    legend('show');
    hold off;

    %相频子图
    subplot(2,1,2);
    semilogx(w_full, phase_full, 'b-','LineWidth',1.2); hold on;
    semilogx(w, phase_meas, 'ro','MarkerSize',6,'DisplayName','实验测试点');
    grid on;
    xlabel('Frequency (rad/s)');
    ylabel('Phase (deg)');
    legend('show');
    hold off;
end