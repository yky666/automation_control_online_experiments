"""Course content transcribed against the six local handouts and original scripts."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def section(title, text, *formulas):
    return {'title':title,'text':text,'formulas':list(formulas)}
def task(id,name,kind='transfer',defaults=None,**kw):
    return {'id':id,'name':name,'kind':kind,'defaults':defaults or {},**kw}
def field(key,label,default,low,high,step=0.1,unit=''):
    return dict(key=key,label=label,default=default,min=low,max=high,step=step,unit=unit)

LABS=[
 dict(id=1,title='数学模型与传递函数',subtitle='从微分方程到可计算的控制系统',tag='建模基础',color='#4776b0',
 objectives=['掌握 tf、zpk 与多项式系数建模。','通过 residue 求部分分式，辨别多项式直接项。','从反馈信号关系求取闭环传递函数。'],
 tasks=[
 task('tf1','任务 1-1 · 四阶传递函数',num=[5],den=[1,5,8,4,0]),
 task('tf2','任务 1-2 · 七阶传递函数',num=[1,4,2],den=[1,4,4,16,0,0,0,0]),
 task('zpk1','任务 2-1 · 共轭零点与六个极点',num=[8,16,16],den=[1,11,29,-11,-30,0,0]),
 task('zpk2','任务 2-2 · 零极点模型转换',num=[1],den=[1,0,-1,1,-1,0]),
 task('residue1','任务 3-1 · 非真有理式展开','residue',num=[1,0,0,0],den=[1,3]),
 task('residue2','任务 3-2 · 重极点部分分式','residue',num=[8,16,16],den=[1,5,1,5,0,0]),
 task('feedback','任务 4 · 单位负反馈','feedback',{'K':1},num=[2,1],den=[1,2,3]),
 task('dynamic_feedback','扩展 · 动态反馈通道','dynamic_feedback',{'K':1},num=[2,1],den=[1,2,3])],
 fields=[field('K','前向增益 K',1,0.1,10,0.1)],
 sections=[
 section('01 · 从微分方程建立传递函数','线性定常系统在零初始条件下，微分的拉普拉斯变换对应乘以 s。先写出输入与输出的关系，再将各项移到同一侧。传递函数描述的是系统关系，不依赖某一次输入。',r'a_n y^{(n)}+\cdots+a_1\dot y+a_0y=b_m u^{(m)}+\cdots+b_0u',r'G(s)=\frac{Y(s)}{U(s)}=\frac{b_ms^m+\cdots+b_0}{a_ns^n+\cdots+a_0}'),
 section('02 · 降幂系数与零系数','tf 的向量必须按 s 的降幂排列。缺失项必须保留零。任务 1-1 中首先相乘两个二次因式，再乘 s，得到可直接用于程序的系数。',r'G_1(s)=\frac{5}{s(s+1)(s^2+4s+4)}=\frac{5}{s^4+5s^3+8s^2+4s}',r'\mathrm{num}=[5],\quad \mathrm{den}=[1,5,8,4,0]',r'G_2(s)=\frac{s^2+4s+2}{s^3(s^2+4)(s^2+4s)}=\frac{s^2+4s+2}{s^7+4s^6+4s^5+16s^4}'),
 section('03 · 零极点增益模型','分子根为零点，分母根为极点；实系数系统的复根成共轭对。重根的次数需要保留。将因式逐项相乘，可核对 zpk 与 tf 是否表示同一模型。',r'G(s)=k\frac{\prod_i(s-z_i)}{\prod_j(s-p_j)}',r'(s+1-j)(s+1+j)=s^2+2s+2',r'G(s)=\frac{8(s^2+2s+2)}{s^2(s+5)(s+6)(s^2-1)}'),
 section('04 · 部分分式与重极点','先做多项式长除，再对真有理部分展开。分子阶数不低于分母时，residue 返回的直接项不能忽略。重极点需要包含所有阶次的项。',r'G(s)=D(s)+\sum_i\sum_{q=1}^{m_i}\frac{r_{iq}}{(s-p_i)^q}',r'\frac{s^3}{s+3}=s^2-3s+9-\frac{27}{s+3}',r'\mathcal L^{-1}\!\left\{\frac{r}{(s-p)^q}\right\}=\frac{r\,t^{q-1}}{(q-1)!}e^{pt}'),
 section('05 · 由信号关系推导负反馈','比较点取 e=r−Hy，前向通道取 y=Ge。代入并将输出移到左侧，得到一般负反馈关系。单位负反馈只是 H=1 的特例。',r'E=R-HY,\quad Y=GE=G(R-HY)',r'(1+GH)Y=GR\quad\Rightarrow\quad T(s)=\frac{G(s)}{1+G(s)H(s)}',r'H=1:\quad T(s)=\frac{2s+1}{s^2+2s+3+(2s+1)}=\frac{2s+1}{s^2+4s+4}')],
 steps=['选取任务，核对分子、分母降幂向量与末项零系数。','运行模型，查看极点、零点与部分分式；非真有理模型只做代数分析。','切换单位反馈或动态反馈，修改 K，比较闭环响应与极点。'],
 questions=[['传递函数需要什么初始条件？','定义 Y/U 时采用零初始条件；非零初始状态的响应需另行叠加。'],['同一传递函数是否一定代表同一内部系统？','输入输出等价不保证内部状态实现相同；极零消去可能隐藏内部不稳定模态。']]),
 dict(id=2,title='典型环节模拟',subtitle='用电路与阶跃响应理解六种基本环节',tag='Simulink 建模',color='#547c69',
 objectives=['从运放的虚短、虚断推导六种典型环节。','比较增益与时间常数对阶跃响应的影响。','区别理想微分冲激与带限微分的有限峰值。'],
 tasks=[task('p','任务 1 · 比例环节 P','typical',{'K':2}),task('inertia','任务 2 · 惯性环节','typical',{'K':1,'T':0.1}),task('integrator','任务 3 · 积分环节 I','typical',{'K':1,'T':0.1}),task('d','任务 4 · 微分环节 D（带限实现）','typical',{'K':-1,'T':0.1,'Tf':0.01}),task('pi','任务 5 · 比例积分 PI','typical',{'K':1,'T':0.1}),task('pd','任务 6 · 比例微分 PD（带限实现）','typical',{'K':1,'T':0.1,'Tf':0.01})],
 fields=[field('K','带符号增益 K',1,-10,10,0.1),field('T','时间常数 T',0.1,0.001,5,0.001,'s'),field('Tf','微分滤波时间 Tf',0.01,0.0001,1,0.0001,'s')],
 sections=[
 section('01 · 运放节点关系与比例环节','理想运放负反馈下，正端接地使负端近似为零，输入电流近似为零。输入电阻电流等于反馈电阻电流，因此反相比例增益必须带负号。需要正增益时，用额外反相器补偿。',r'\frac{u_i-0}{R_1}=\frac{0-u_o}{R_2}\quad\Rightarrow\quad G_P(s)=-\frac{R_2}{R_1}=K',r'U_i(s)=\frac{A}{s}\quad\Rightarrow\quad u_o(t)=KA\,1(t)'),
 section('02 · 惯性环节：电阻与电容并联反馈','反馈阻抗是 R₂ 与电容的并联，电容阻抗为 1/(Cs)。代入反相运放的一般公式 −Zf/Zin，得到一阶低通。对阶跃进行部分分式展开即可得到指数响应。',r'Z_f=\frac{R_2}{1+R_2Cs},\quad G(s)=-\frac{R_2/R_1}{1+R_2Cs}=\frac{K}{Ts+1},\quad T=R_2C',r'Y(s)=\frac{KA}{s(Ts+1)}=KA\left(\frac1s-\frac1{s+1/T}\right)',r'y(t)=KA(1-e^{-t/T}),\quad y(T)=0.63212\,KA'),
 section('03 · 积分环节：电容反馈','取反馈阻抗 1/(Cs)，由输入电流流入电容得到输出微分方程。积分环节没有有限的阶跃稳态值，响应斜率由增益、输入幅值和时间常数共同决定。',r'G_I(s)=-\frac{1}{R_1Cs}=\frac{K}{Ts},\quad \dot y=\frac{K}{T}u',r'Y(s)=\frac{KA}{Ts^2}\quad\Rightarrow\quad y(t)=\frac{KA}{T}t'),
 section('04 · 微分环节与可实现的滤波','输入端为电容、反馈为电阻时，电容电流与输入导数成正比。理想阶跃的导数为冲激，不能用采样尖峰声称测得真实峰值。本工作台保留理想推导，实际仿真加入 Tf，显示可实现的指数脉冲。',r'G_D(s)=-RC_1s=-Ts,\quad y(t)=-TA\delta(t)',r'G_{Df}(s)=\frac{KTs}{T_fs+1},\quad y_f(t)=\frac{KTA}{T_f}e^{-t/T_f}'),
 section('05 · 比例积分环节','反馈电阻与电容串联时 Zf=R₂+1/(Cs)。输出包含瞬时比例跳变与随后线性累积，阶跃下起点 KA、斜率 KA/T。',r'G_{PI}(s)=-\frac{R_2+1/(Cs)}{R_1}=K\left(1+\frac1{Ts}\right),\quad K=-\frac{R_2}{R_1},\ T=R_2C',r'y(t)=KA\left(1+\frac{t}{T}\right)'),
 section('06 · 比例微分环节与时间常数来源','输入端 R₁ 与 C₁ 并联、反馈为 R₂ 时，输入导纳为 1/R₁+C₁s。由 −Zf/Zin 得 T=R₁C₁；课件中出现 R₂C₁ 的写法需按实际接线核对。滤波只加在微分支路，使阶跃末值仍为 KA。',r'G_{PD}(s)=-R_2\left(\frac1{R_1}+C_1s\right)=K(1+Ts),\quad K=-R_2/R_1,\ T=R_1C_1',r'y(t)=KA\,1(t)+KTA\delta(t)',r'G_{PDf}=K\left(1+\frac{Ts}{T_fs+1}\right),\quad y_f(t)=KA+\frac{KTA}{T_f}e^{-t/T_f}')],
 steps=['选取 P、惯性、I、D、PI、PD；根据反相器设置带符号 K。','以相同时间范围修改 K、T，对照解析式和曲线。','D/PD 使用带限模型，修改 Tf 观察峰值和脉冲面积。','选择 Simulink，服务器生成 Step / Transfer Fcn / To Workspace 模型并返回真实仿真数据。'],
 questions=[['为什么积分环节不显示调节时间？','单位阶跃输出持续增长，不存在有限稳态值，阶跃调节时间不适用。'],['D/PD 为什么需要 Tf？','理想微分非真有理、无限高频增益；滤波使模型可实现，并限定噪声和尖峰。']]),
 dict(id=3,title='时域性能分析与设计',subtitle='把极点位置与响应速度、超调量联系起来',tag='动态性能',color='#9b7151',
 objectives=['掌握二阶系统极点、阻尼比与自然频率的关系。','读取上升时间、峰值时间、超调量与调节时间。','比较零点与任意输入对响应的影响。'],
 tasks=[task('second','例题 · 阻尼比与自然频率','second',{'zeta':0.5,'wn':10}),task('zero','扩展 · 附加闭环零点','zero',{'zeta':0.5,'wn':10,'zero':5}),task('example1','例 1 · 100/[s(s+5)] 单位反馈','feedback',num=[100],den=[1,5,0]),task('example4','例 4 · 多项式输入','transfer',num=[10],den=[1,2,10],input='polynomial'),task('task1','任务 1 · 一阶开环阶跃','transfer',num=[4],den=[3,1]),task('task2','任务 2 · 二阶开环阶跃','transfer',num=[2],den=[1,3,25]),task('task3','任务 3 · 100/[s(s+3)] 单位反馈','feedback',num=[100],den=[1,3,0]),task('task4','任务 4 · 阶跃加斜坡','transfer',num=[1,1],den=[1,1,1],input='step_ramp')],
 fields=[field('zeta','阻尼比 ζ',0.5,0,2,0.05),field('wn','自然角频率 ωn',10,0.5,80,0.5,'rad/s'),field('zero','附加零点 z（位置 −z）',5,0.1,100,0.1,'rad/s')],
 sections=[
 section('01 · 二阶模型与闭环极点','标准二阶系统分母与一般二次多项式逐项对应。解特征方程可得到极点。ζ=0 时持续振荡；0<ζ<1 时欠阻尼；ζ=1 为临界阻尼；ζ>1 为过阻尼。',r'T(s)=\frac{\omega_n^2}{s^2+2\zeta\omega_ns+\omega_n^2}',r'p_{1,2}=-\zeta\omega_n\pm\omega_n\sqrt{\zeta^2-1},\quad \omega_d=\omega_n\sqrt{1-\zeta^2}'),
 section('02 · 欠阻尼阶跃响应推导','单位阶跃的拉普拉斯变换为 1/s。分离稳态项，并把二次分母配方，利用指数衰减正弦变换对得到时域解析式。此公式只适用于 0<ζ<1。',r'Y(s)=\frac1s-\frac{s+2\zeta\omega_n}{s^2+2\zeta\omega_ns+\omega_n^2}',r'y(t)=1-e^{-\zeta\omega_nt}\left[\cos(\omega_dt)+\frac{\zeta}{\sqrt{1-\zeta^2}}\sin(\omega_dt)\right]'),
 section('03 · 峰值时间与超调量','令响应的一阶导数等于零，首个非零峰值满足 ωd tp=π。将峰值时间代回解析式得到超调。保持 ζ 不变时，ωn 只缩放时间轴，不改变百分比超调。',r'\dot y(t)=\frac{\omega_n}{\sqrt{1-\zeta^2}}e^{-\zeta\omega_nt}\sin(\omega_dt)',r't_p=\frac{\pi}{\omega_d},\quad M_p=100e^{-\pi\zeta/\sqrt{1-\zeta^2}}\%'),
 section('04 · 上升时间与调节时间的口径','上升时间使用稳态响应的 10%～90%，调节时间采用“此后始终落在误差带内”。4/(ζωn) 和 3/(ζωn) 分别是常用 2% 和 5% 近似，实际值需由响应求取。有限仿真若末段还没进入误差带，显示未确定，不用最后一个采样值代替稳态。',r'|y(t)-y_\infty|\leq\varepsilon |y_\infty|\quad(\forall t\geq t_s)',r't_s\approx\frac4{\zeta\omega_n}\ (2\%),\qquad t_s\approx\frac3{\zeta\omega_n}\ (5\%)'),
 section('05 · 零点改变瞬态，任意输入用 lsim','添加左半平面零点并保持直流增益为 1 后，分子变为 ωn²(s/z+1)。极点保持不变，但阶跃导数权重改变，因此超调可能增大。一般输入响应由卷积给出，不能直接使用阶跃指标评价斜坡跟踪。',r'T_z(s)=\frac{\omega_n^2(s/z+1)}{s^2+2\zeta\omega_ns+\omega_n^2}',r'y(t)=\int_0^t h(t-\tau)u(\tau)\,d\tau',r'u_{\rm task4}=1+t,\quad u_{\rm example4}=5+2t+8t^2')],
 steps=['选取例题或四个任务，保持同一时间网格。','固定 ωn，扫描 ζ=0、0.25、0.5、0.75、1、1.25。','固定 ζ=0.25，扫描 ωn=10、30、50，比较时间尺度。','加入零点；切换误差带；记录指标定义及采样间隔。'],
 questions=[['ζ 增大是否总能缩短调节时间？','不是。进入过阻尼区后慢实极点可能接近原点，响应反而变慢。'],['斜坡输入能用阶跃超调量评价吗？','不能，斜坡没有固定末值；应分析跟踪误差和速度误差系数。']]),
 dict(id=4,title='控制系统稳定性分析',subtitle='用 Routh 判据、根轨迹与真实响应交叉验证',tag='稳定性边界',color='#9b5960',
 objectives=['确定三阶系统的临界增益。','研究时间常数对稳定边界的影响。','比较 Routh 第一列、闭环极点与响应趋势。'],
 tasks=[task('stability1','任务 1 · 等时间常数三阶系统','stability',{'K':1,'T1':0.1,'T2':0.1}),task('stability2','任务 2 · 不等时间常数三阶系统','stability',{'K':5,'T1':0.1,'T2':0.01}),task('stability3','任务 3 · 时间常数比较','stability',{'K':1,'T1':0.1,'T2':0.01}),task('reduced','任务 3 · 移除第二惯性环节','reduced',{'K':1,'T1':0.1})],
 fields=[field('K','开环可调增益 K',1,0.01,20,0.01),field('T1','第一惯性时间 T₁',0.1,0.001,1,0.001,'s'),field('T2','第二惯性时间 T₂',0.1,0.001,1,0.001,'s')],
 sections=[
 section('01 · 典型环节串联与闭环特征式','比例增益 10K、积分环节和两个惯性环节串联，得到开环模型。单位负反馈的特征方程是 1+G=0；不能用开环极点直接判断闭环稳定。',r'G(s)=\frac{10K}{s(T_1s+1)(T_2s+1)}',r'\Delta(s)=T_1T_2s^3+(T_1+T_2)s^2+s+10K'),
 section('02 · 逐行建立 Routh 表','三阶多项式的前两行由交错系数排列，第三行按交叉乘积计算。T₁、T₂ 为正时，第一列全为正的条件只剩 K>0 和第三行首项>0。全零行必须用辅助多项式处理。',r'\begin{array}{c|cc}s^3&T_1T_2&1\\s^2&T_1+T_2&10K\\s^1&\dfrac{T_1+T_2-10KT_1T_2}{T_1+T_2}&0\\s^0&10K&0\end{array}',r'0<K<K_{\rm cr}=\frac{T_1+T_2}{10T_1T_2}=\frac1{10}\left(\frac1{T_1}+\frac1{T_2}\right)'),
 section('03 · 临界振荡频率与边界验证','达到临界增益时第三行全零，使用 s² 行形成辅助多项式。虚轴根给出持续振荡频率，剩余实根为负。临界状态不是渐近稳定，阶跃指标不适用。',r'(T_1+T_2)s^2+10K_{\rm cr}=0\quad\Rightarrow\quad \omega_{\rm cr}=\frac1{\sqrt{T_1T_2}}',r'T_1=T_2=0.1:\ K_{\rm cr}=2,\quad \omega_{\rm cr}=10\ {\rm rad/s}',r'T_1=0.1,T_2=0.01:\ K_{\rm cr}=11,\quad \omega_{\rm cr}=31.6228\ {\rm rad/s}'),
 section('04 · 根轨迹与时间常数的作用','根轨迹是增益改变时特征根的轨迹。K<Kcr 的所有根位于左半平面，K>Kcr 有一对根进入右半平面。减小 T₂ 使临界增益增大；删除第二惯性环节后变为二阶系统，只要 K>0 就渐近稳定。',r'\operatorname{Re}p_i<0\ (\forall i)\quad\Leftrightarrow\quad\text{渐近稳定}',r'T_2\to0:\quad\Delta(s)=T_1s^2+s+10K',r'\omega_n=\sqrt{10K/T_1},\quad\zeta=\frac1{2\sqrt{10KT_1}}')],
 steps=['任务 1 分别取 K=1、2、3；查看响应和极点。','任务 2 分别取 K=5、11、17；核对临界增益。','任务 3 固定 K=1，比较两种 T₂ 与降阶系统。','在极点页查看根轨迹和 Routh 第一列，记录稳定边界。'],
 questions=[['临界稳定和渐近稳定有什么区别？','虚轴单根导致不衰减振荡，系统不渐近稳定；BIBO 稳定需要传递函数全部极点严格位于左半平面。'],['改变输入幅值会改变线性系统稳定性吗？','不会改变极点；但实际电路若进入饱和，则线性模型的条件已不满足。']]),
 dict(id=5,title='频率特性测试与验证',subtitle='从正弦稳态测量到 Bode 曲线',tag='频域测量',color='#6b6ca7',
 objectives=['用正弦输入幅值比和相位差测量频率响应。','识别比例环节带宽、惯性转折频率与二阶谐振。','用时域正弦拟合独立验证 freqresp。'],
 tasks=[task('bandwidth','任务 1 · 比例环节与运放带宽','bandwidth',{'K':1,'GBW':1e6,'frequency':1e5,'A':0.05}),task('frequency_inertia','任务 2 · T=1 ms 惯性环节','frequency_inertia',{'K':1,'T':0.001,'frequency':100,'A':1}),task('frequency_second','任务 3 · 二阶频率特性','second',{'zeta':10/(2*500**0.5),'wn':500**0.5,'frequency':3.5,'A':1})],
 fields=[field('K','比例增益 K',1,0.1,100,0.1),field('GBW','增益带宽积 GBW',1e6,1e3,1e8,1e3,'Hz'),field('T','惯性时间常数 T',0.001,0.00001,1,0.00001,'s'),field('zeta','阻尼比 ζ',0.223607,0.05,2,0.01),field('wn','自然角频率 ωn',22.36068,1,100,0.1,'rad/s'),field('frequency','测试正弦频率 f',3.5,0.01,1e7,0.01,'Hz')],
 sections=[
 section('01 · 由稳态正弦定义频率响应','稳定线性系统在正弦输入作用下，暂态衰减后输出具有同一频率。输出输入幅值比是 |G(jω)|，相位差是 arg G(jω)。角频率和频率必须换算，不能把 Hz 直接送入 bode。',r'u(t)=A\sin(\omega t),\quad y_{ss}(t)=B\sin(\omega t+\varphi)',r'|G(j\omega)|=B/A,\quad L=20\log_{10}(B/A),\quad\omega=2\pi f',r'\varphi=-\omega\Delta t=-360^\circ f\Delta t\quad\text{（输出滞后时）}'),
 section('02 · 比例环节与有限带宽','两级反相放大器的理想总增益为正，理想比例环节幅频为水平线、相位为零。采用单主极点近似且把 GBW/K 作为闭环带宽时，得到低通扩展模型；这是一种带宽假设，不能把计算测点称作实物测量。',r'G_{\rm ideal}=K,\quad L=20\log_{10}K,\quad\varphi=0',r'f_p=\frac{\mathrm{GBW}}{K},\quad G(s)=\frac{K}{1+s/(2\pi f_p)}',r'K\in\{1,10,100\}\quad\Rightarrow\quad f_p\in\{10^6,10^5,10^4\}\ {\rm Hz}'),
 section('03 · 惯性环节的幅相推导','将 s=jω 代入并乘以共轭，分母模长为 √(1+ω²T²)。转折频率 ωb=1/T 时幅值下降 3.0103 dB、相位为 −45°。高频幅值渐近线斜率为 −20 dB/dec。',r'G(j\omega)=\frac1{1+j\omega T}=\frac{1-j\omega T}{1+\omega^2T^2}',r'L=-10\log_{10}(1+\omega^2T^2),\quad\varphi=-\arctan(\omega T)',r'T=10^{-3}\ {\rm s}:\quad\omega_b=1000\ {\rm rad/s},\quad f_b=159.1549\ {\rm Hz}'),
 section('04 · 二阶系统与谐振峰','令 r=ω/ωn，分母实部为 1−r²、虚部为 2ζr。相位必须用 atan2 保留象限，频率高于 ωn 时继续趋向 −180°。对幅值平方的分母求导得到谐振条件。',r'G(j\omega)=\frac1{1-r^2+j2\zeta r},\quad |G|=\frac1{\sqrt{(1-r^2)^2+4\zeta^2r^2}}',r'\varphi=-\operatorname{atan2}(2\zeta r,1-r^2)',r'\omega_r=\omega_n\sqrt{1-2\zeta^2},\quad M_r=\frac1{2\zeta\sqrt{1-\zeta^2}},\quad0<\zeta<1/\sqrt2',r'\frac{500}{s^2+10s+500}:\quad \omega_n=\sqrt{500},\quad\zeta=\frac{10}{2\sqrt{500}}'),
 section('05 · 从时域拟合进行独立验证','仿真时间自动包含不少于 10 个测试周期，并等待最慢极点的暂态衰减。对末段输出拟合 a sinωt+b cosωt+c，与 freqresp 对比。两次 bode 的同源采样不算独立验证。',r'y_{ss}\approx a\sin\omega t+b\cos\omega t+c',r'B=\sqrt{a^2+b^2},\quad\varphi=\operatorname{atan2}(b,a),\quad\epsilon_A=\left|\frac{B/A}{|G(j\omega)|}-1\right|')],
 steps=['扫描频率范围，在转折频率和谐振峰附近增加测点。','运行后分别查看 Bode、正弦输入输出、测点表与拟合误差。','任务 1 比较 K=1、10、100；任务 2 核对 159.15 Hz；任务 3 查看谐振。','导出测点 CSV，保留计算引擎、输入幅值和拟合窗口。'],
 questions=[['为何幅值用 20log10？','功率正比于幅值平方，10log10(A²)=20log10(A)；自然对数会给出错误的 dB 值。'],['仅凭幅频能唯一得到相频吗？','需满足适当的最小相位条件并固定增益符号等；全通因子与纯时延可改变相位而不改变幅值。']]),
 dict(id=6,title='频域法串联超前校正',subtitle='从稳态精度出发，闭合一次控制器设计循环',tag='控制器设计',color='#2f807d',
 objectives=['由稳态速度误差系数确定开环增益。','设计有源单级与无源两级超前网络。','在实际闭环响应中检验频域与时域指标。'],
 tasks=[task('lead1','任务 1 · 有源单级超前校正','lead1',{'Kv':20,'targetPM':35,'reserve':8}),task('lead2','任务 2 · 两级无源超前校正','lead2',{'K':10,'alpha':3,'wm':6,'MpReq':27.5,'tsReq':1.7,'essReq':0.1}),task('lead_example1','例 1 · 高频有源校正（修正 log10）','lead_example1',{'K':1000,'targetPM':45,'reserve':8}),task('lead_example2','例 2 · 双积分两级校正','lead_example2',{'K':10,'alpha':6,'wm':6,'MpReq':30,'tsReq':5,'essReq':0.1})],
 fields=[field('Kv','速度误差系数目标 Kv',20,1,100,1,'s⁻¹'),field('K','开环增益 K',10,0.1,2000,0.1),field('targetPM','目标相位裕度',35,5,70,1,'°'),field('reserve','预留相位',8,0,20,1,'°'),field('alpha','超前比 α',3,1.01,15,0.01),field('wm','最大超前角频率 ωm',6,0.1,300,0.1,'rad/s'),field('MpReq','允许超调量',27.5,1,80,0.1,'%'),field('tsReq','允许调节时间',1.7,0.1,20,0.1,'s'),field('essReq','允许斜坡稳态误差',0.1,0.001,1,0.001)],
 sections=[
 section('01 · 先满足稳态精度','单位负反馈的误差 E=R/(1+G)。对单位斜坡 R=1/s²，使用终值定理得到 ess=1/Kv；前提是闭环稳定。任务 1 的 Kv=K/2，所以 Kv=20 对应 K=40。',r'e_{ss}=\lim_{s\to0}sE(s)=\lim_{s\to0}\frac1{s[1+G(s)]}=\frac1{K_v},\quad K_v=\lim_{s\to0}sG(s)',r'G_0=\frac{K}{s(s+2)}:\quad K_v=K/2,\quad K=2K_v=40'),
 section('02 · 有源超前网络的幅相特性','取零点比极点更接近原点，即 α>1。相角是两个一阶因式相角之差；对 ω 求导可得最大相位所在频率。低频直流增益为 1，使速度误差系数保持不变。',r'G_c(s)=\frac{1+\alpha Ts}{1+Ts},\quad\alpha>1,\quad\beta=1/\alpha',r'\varphi_c=\arctan(\alpha T\omega)-\arctan(T\omega)',r'\omega_m=\frac1{T\sqrt\alpha},\quad\sin\varphi_m=\frac{\alpha-1}{\alpha+1},\quad|G_c(j\omega_m)|=\sqrt\alpha'),
 section('03 · 从相位缺口选取参数','先读未校正相位裕度 PM₀，加上预留角来计算需要的最大超前。新截止频率同时受校正网络幅值影响，不能直接沿用旧截止频率。工作台使用对数频率扫描后求根细化截止频率。',r'\varphi_m=PM_{\rm target}-PM_0+\delta,\quad\beta=\frac{1-\sin\varphi_m}{1+\sin\varphi_m}',r'L_0(\omega_c)+10\log_{10}(1/\beta)=0',r'\omega_z=\omega_c\sqrt\beta,\quad\omega_p=\omega_c/\sqrt\beta,\quad T=1/\omega_p'),
 section('04 · 无源网络衰减与两级补偿','单级无源超前在低频衰减 1/α，两级衰减 1/α²。串联放大器 α² 抵消低频衰减，保持 Kv。任务 2 采用 α=3、ωm=6 rad/s；修改参数后必须重新检查所有指标。',r'G_{c1}(s)=\frac1\alpha\frac{1+s/\omega_z}{1+s/\omega_p},\quad\omega_z=\omega_m/\sqrt\alpha,\quad\omega_p=\omega_m\sqrt\alpha',r'G=\alpha^2G_{c1}^2G_0,\qquad G_0=\frac{K}{s(0.5s+1)(s/30+1)}',r'K_v=K,\quad e_{ss}=1/K'),
 section('05 · 从时域要求到频域设计，再回到时域验证','根据超调上限反求阻尼比，再由二阶近似估算自然频率和相位裕度。这些关系用于选取设计目标，对高阶校正系统只是近似；最终结论以闭环极点、实际 stepinfo 和斜坡误差为准。',r'\zeta=-\frac{\ln(M_p/100)}{\sqrt{\pi^2+\ln^2(M_p/100)}},\quad\omega_n\gtrsim\frac4{\zeta t_s}',r'PM\approx\arctan\frac{2\zeta}{\sqrt{\sqrt{1+4\zeta^4}-2\zeta^2}}',r'PM=180^\circ+\angle G(j\omega_c),\quad |G(j\omega_c)|=1',r'GM_{\rm dB}=-20\log_{10}|G(j\omega_\pi)|,\quad\angle G(j\omega_\pi)=-180^\circ')],
 steps=['任务 1 从 Kv 确定 K，运行自动设计，读取 β、T、转折频率。','对照校正前后 Bode 与闭环阶跃，检查 PM>35°、GM>10 dB。','任务 2 调整 α 和 ωm，检查 ess≤0.1、Mp≤27.5%、ts≤1.7 s。','记录高频增益增加和噪声放大的代价，导出设计报告。'],
 questions=[['增加超前相位是否一定增大最终相位裕度？','不一定；超前也提高幅值并移动截止频率，必须在新的截止频率计算相位裕度。'],['为什么代码中的 log 需核对？','dB 幅值必须使用 log10；原例 1 的 20*log(mag) 已在工作台标准代码中修正，原脚本保留供对照。']])
]

LABS[5]['sections'].insert(1,section('阻容电路 · 有源与无源超前网络','课件电路中 R₁ 与 C 并联，其等效阻抗与 R₂ 串联。无源网络取 R₂ 上的分压；有源网络以串联阻抗为输入阻抗、R₃ 为反馈阻抗，使用运放关系 −Zf/Zin。工作台有源模型采用额外反相补偿并归一化低频增益；无源网络则单独补偿衰减。',r'Z_1(s)=R_1\parallel\frac1{Cs}=\frac{R_1}{1+R_1Cs}',r'G_{\rm passive}(s)=\frac{R_2}{R_2+Z_1(s)}=\frac1\alpha\frac{1+\alpha Ts}{1+Ts}',r'\alpha=\frac{R_1+R_2}{R_2}>1,\quad T=\frac{R_1R_2C}{R_1+R_2},\quad\alpha T=R_1C',r'G_{\rm active}(s)=-\frac{R_3}{R_1+R_2}\frac{1+\alpha Ts}{1+Ts}'))

LABS[2]['fields'].append(field('K','前向增益 K',1,0.01,20,0.01))
LABS[0]['tasks'] += [
 task('ode_demo','Simulink 入门 · 积分器反馈建模',num=[1],den=[1,2]),
 task('conversion','教学例 · 模型双向转换',num=[1,3],den=[1,2,2,1]),
 task('connections','教学例 · 串联、并联和反馈连接',num=[10,5],den=[1,1,0])]
LABS[2]['tasks'] += [task('damping_sweep','例 2 · 固定 ωn 扫描阻尼比','second',{'wn':10,'zeta':.25}),task('frequency_sweep','例 3 · 固定阻尼比扫描 ωn','second',{'wn':10,'zeta':.25})]
for t in LABS[2]['tasks']:
    if t['id'] in ('second','zero'):t['defaults'].update(wn=10**.5,zeta=1/10**.5)
for f in LABS[2]['fields']:
    if f['key']=='zeta':f['min']=0
for f in LABS[1]['fields']:
    if f['key']=='T':f['max']=10
for t in LABS[5]['tasks']:
    if t['id']=='lead_example2':t['defaults']={'K':10,'alpha':6,'wm':6,'targetPM':35}
for lab in LABS:
    if not any(f['key']=='frequency' for f in lab['fields']):lab['fields'].append(field('frequency','正弦频率 f',1,0.01,10000,0.01,'Hz'))
    for task_item in lab['tasks']:
        if task_item['kind'] in ('feedback','dynamic_feedback'):task_item['defaults'].setdefault('K',1)

def get_catalog():
    from .coursework import coursework,PRESETS
    originals=json.loads((ROOT/'sources'/'manifest.json').read_text(encoding='utf-8'))
    diagrams_path=ROOT/'sources'/'figures'/'diagrams.json'
    diagrams=json.loads(diagrams_path.read_text(encoding='utf-8')) if diagrams_path.exists() else {}
    result=[]
    for lab in LABS:
        tasks=[]
        for task in lab['tasks']:
            keys=list(task['defaults'])
            if task['kind']=='typical':keys={'p':['K'],'inertia':['K','T'],'integrator':['K','T'],'d':['K','T','Tf'],'pi':['K','T'],'pd':['K','T','Tf']}[task['id']]
            model_name=f"course_lab{lab['id']}_{task['id']}.slx"
            native_model={'download':f'/models/{model_name}','online_file':f'matlab/models/{model_name}'} if (ROOT/'matlab/models'/model_name).is_file() else None
            tasks.append(dict(task,parameters=[k for k in keys if k in {f['key'] for f in lab['fields']}],presets=PRESETS.get((lab['id'],task['id']),[]),native_model=native_model))
        result.append(dict(lab,tasks=tasks,coursework=coursework(lab['id']),diagrams={k.split(':')[1]:v for k,v in diagrams.items() if k.startswith(str(lab['id'])+':')},files=next(x['files'] for x in originals if x['id']==lab['id'])))
    return result

def get_task(lab_id,task_id):
    lab=next((l for l in LABS if l['id']==lab_id),None)
    if not lab: raise ValueError('实验编号不存在')
    selected=next((t for t in lab['tasks'] if t['id']==task_id),None)
    if not selected: raise ValueError('实验任务不存在')
    return lab,selected
