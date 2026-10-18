"""Handout traceability and hands-on activities (page numbers are slide pages)."""
COURSEWORK={
1:dict(pages='第 9～17、18～38、40～43 页',required=['从空白模型插入 Step、Sum、Gain、Integrator、Scope，设置 +- 与增益 2，连接反馈及 Scope 分支。','完成传递函数、零极点、部分分式的四项正式任务。','练习 tf/zpk/ss、tf2zp/zp2tf、residue 的双向转换和串联、并联、反馈连接。'],blocks=['Step','Sum','Gain','Integrator','TransferFcn','Scope'],originals=['/sources/lab1/simulink_example.slx'],caveats=['建模入门例子对应 x′=u−2x，单独列为“Simulink 入门”任务。状态空间及连接为课件教学内容，不冒充新增正式作业。']),
2:dict(pages='第 5～22 页；表 1～6',required=['按课件搭建 P、惯性、积分、理想 D、PI、理想 PD 六种结构，保留分支、求和和导数模块。','由 R₁、R₂、C 求带符号 K 与时间常数 T；各工况比较曲线，填写表 1～6。','比例取 R₂=100、200、500、1000 kΩ；其他环节取 C=0.1、1、10、100 μF（R=100 kΩ）。'],blocks=['Step','Gain','Integrator','Derivative','Sum','TransferFcn','Scope'],originals=[f'/sources/lab2/task{i}.slx' for i in range(1,7)],caveats=['原 task3.slx 分母缺少零系数，实际是比例模型；正确积分应为 [T 0]，或 Gain(-1/T) + Integrator。','课程理想 D/PD 与数值页的带滤波 D/PD 分开显示；阶跃冲激的数值尖峰不能当作物理峰值。','反相符号保留。若按课件允许加入反相补偿器，需明确勾选补偿。']),
3:dict(pages='第 10～28 页；第 29 页要求例题一并提交',required=['求特征根及 damp 参数，测试基础系统 10/(s²+2s+10)。','例 1 动态指标；例 2 固定 ωn=10，ζ=0:0.25:1.25；例 3 固定 ζ=0.25，ωn=10、30、50。','零点 z=−5、−2、−1 与原系统比较；多项式输入例 4；完成任务 1～4，分别记录 2%/5% 调节时间。'],blocks=['Step','TransferFcn','Scope'],originals=[],caveats=['本章主要要求 MATLAB 编程和曲线指标读取；模块搭建是可选复核。','课件“磁悬浮系统控制器”目的句没有给出对应任务或模型，按材料记录为待教师确认，不能擅自编造实验。']),
4:dict(pages='第 5～21 页；任务 1～3、表 1～2',required=['用积分、两个惯性、可调比例与负反馈组合三阶系统，不只使用一个合并后的闭环 Transfer Fcn。','T₁=T₂=0.1 时比较 K=1、2、3；T₂=0.01 时比较 K=5、11、17，求临界增益及 Routh 表。','K=1 比较 T₂=0.1、0.01 及去掉第二惯性环节的二阶模型，记录 Mp、tp、ts。'],blocks=['Step','Sum','Gain','Integrator','TransferFcn','Scope'],originals=[],caveats=['信号画布和元件电路页均可实际求解；元件电路保留课件下方的反馈反相器，共五个运放。']),
5:dict(pages='第 5～30 页；三个任务、表 1～3',required=['Sine Wave 激励，与输入同时接入 Scope，逐个频率读取输出峰值和相位差。','比例 K=1、10、100，幅值 0.05 V；惯性 T=1 ms，幅值 1 V，测试转折频率附近。','二阶系统用积分、惯性、增益和负反馈组成；按频率表采样并加密谐振区域，再做阶跃响应。','记录实际输出的削顶、幅值比和相位；用实测 Bode 渐近线识别最小相位模型并和 MATLAB 比较。'],blocks=['SineWave','Step','Gain','Sum','Integrator','TransferFcn','Scope'],originals=[],caveats=['示例带宽模型是单主极点假设；元件页可用有限运放模拟带宽与输出限幅，没有建模死区、噪声和压摆率。仿真数据不能冒充硬件实测。','识别题需学生根据自己的频率表判断结构；网页记录表只提供单位换算和幅相计算。']),
6:dict(pages='第 9～18、19～35 页；任务 1、例 1/2、练习 2',required=['设计有源单级超前，验证 Kv=20、PM>35°、GM>10 dB；保留校正前后 Bode 与闭环响应。','按选定 C 由零极点参数计算 R₁、R₂、R₃，注意有源电路反相和无源低频衰减。','双积分例 2 要求 Ka=10、PM>35°；用两级无源网络和 α² 放大器组成。','练习 2 的另一被控对象要求 ess≤0.1、Mp≤27.5%、ts≤1.7s，不能把两组指标混用。'],blocks=['Step','Sum','Gain','TransferFcn','Scope'],originals=[],caveats=['元件页实际接入阻容网络、缓冲与补偿运放；可修改端子接线并求解。完整官方库使用 Simscape Online。'])
}

PRESETS={
 (3,'second'):[dict(label='课件基础系统',params={'wn':10**.5,'zeta':1/10**.5})],
 (3,'damping_sweep'):[dict(label=f'ζ={z}',params={'wn':10,'zeta':z}) for z in [0,.25,.5,.75,1,1.25]],
 (3,'frequency_sweep'):[dict(label=f'ωn={w}',params={'zeta':.25,'wn':w}) for w in [10,30,50]],
 (3,'zero'):[dict(label=f'z=−{z}',params={'wn':10**.5,'zeta':1/10**.5,'zero':z}) for z in [5,2,1]],
 (4,'stability1'):[dict(label=f'K={k}',params={'K':k,'T1':.1,'T2':.1}) for k in [1,2,3]],
 (4,'stability2'):[dict(label=f'K={k}',params={'K':k,'T1':.1,'T2':.01}) for k in [5,11,17]],
 (4,'stability3'):[dict(label=f'T₂={t}',params={'K':1,'T1':.1,'T2':t}) for t in [.1,.01]],
}
PRESETS[(2,'p')]=[dict(label=f'R₂={r} kΩ（反相）',params={'K':-r/100}) for r in [100,200,500,1000]]
for kind in ('inertia','integrator','d','pi','pd'):
    PRESETS[(2,kind)]=[dict(label=f'C={c} μF（反相）',params={'K':-1,'T':100000*c*1e-6}) for c in [.1,1,10,100]]
PRESETS[(3,'zero')].insert(0,dict(label='无零点基准',params={'wn':10**.5,'zeta':1/10**.5},numerator=[10],denominator=[1,2,10]))

def coursework(lab):return COURSEWORK[lab]
