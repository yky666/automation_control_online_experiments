# Control Lab 2.0 · 学生免 MATLAB 实验工作台

六章共 33 项任务，包含完整推导、原理图、参数修改和自动报告。**默认运行不调用本机 MATLAB。** 平台数值计算使用服务端 SciPy；自由 MATLAB/Simulink 代码使用学校许可在 MATLAB Online 的个人会话中执行。

## 打开修复版

双击 **重启实验网页.cmd**，浏览器按 **Ctrl+F5** 更新旧页面。地址是 **http://127.0.0.1:8765**。旧启动脚本也会识别 2.0 版本并重启本项目的旧服务。

本机版本供开发演示；部署到服务器后，学生只访问网址，无需安装 Python、Node、MATLAB 或配置 Engine。

## 修复内容

- 修复图表卸载时 `Plotly.purge(null)` 导致的章节切换白屏，加入错误恢复界面。
- 参数按实际模型列出；固定任务可直接修改分子、分母。自定义最终模型时，任务参数暂不参与计算，并明确禁用。
- 所有任务支持幅值扫描；正弦自动等待可取消以修改时长。输入类型、采样点数可以修改。
- 未配置授权服务时，页面不显示可调用的 MATLAB/Simulink 引擎。默认提供平台运行、复制代码、Online 操作与报告。
- 增加六章、33 个任务和按钮操作的前端 DOM 交互测试。它不是浏览器截图或 Edge 视觉验收。

## 使用流程

1. 选择章节和任务，阅读默认展开的推导，可收起或切换紧凑排版。
2. 改参数、系数、输入或采样设置。实时预览只计算，不保存。
3. 点击“运行实验”保存结果；平台计算会在曲线和报告中标注，避免冒充原生 MATLAB/Simulink。
4. 使用 2～8 组参数扫描。固定系数任务也可以扫描输入幅值。
5. 代码页点击“复制并打开 MATLAB Online”，使用学校账户登录后粘贴运行。网页不声称已自动运行 Online 代码。
6. 框图页可以运行免安装数值实验；“复制模型脚本并打开 Online”提供实际构建 Simulink 模型的脚本。授权云端服务接通后，可调用真实 Simulink 并下载模型。
7. 生成 HTML、Markdown、JSON 或 ZIP。HTML 含推导、原理图、参数、曲线、代码、来源与个人分析，可打印保存 PDF。

## 当前云端状态

学校有 MATLAB 许可，尚无服务器。**当前没有公网部署网址或已连接的 MATLAB 云端接口。** 已提供 Online 入口、免 MATLAB 运行模式、服务器接口与容器部署文件。

MATLAB Online 是学校账户的个人云端开发会话；自建网页自动调用需要授权的服务器计算服务。完整说明见 [docs/CLOUD.md](docs/CLOUD.md)。

## 部署

```bash
docker compose up --build -d
```

容器包含前端、Python 数值服务、中文报告字体与离线公式资源，没有 MATLAB 安装要求。默认按浏览器会话隔离学生记录和报告，运行数据保存到卷。对外访问由学校配置 HTTPS。

可选的原生计算工作节点只在授权服务器安装 MATLAB/Simulink。令牌保存在服务端，学生不接触令牌、路径或本机许可。共享节点只执行校验后的参数化任务；自由脚本使用个人 Online 会话。

本机没有 Docker 工具，本次未实际构建镜像或部署云服务器；容器文件已准备，Python 服务和协议通过自动化测试。

## 本机安装

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1 -OpenBrowser
```

默认安装免 MATLAB 依赖。停止服务执行 `stop.ps1`。教师确需本机原生验证时显式执行 `setup.ps1 -TeacherMatlab`，并在启动前设置 `CONTROL_LAB_ENABLE_LOCAL_MATLAB=1`；学生默认流程不需要它。

## 目录与验证

`frontend/` 为工作台；`backend/` 为数值、报告与授权工作节点；`sources/` 保留 51 份原始文件和电路图；`runtime/` 为运行数据；`docs/` 为接口、部署、验证记录与示例报告。

```powershell
npx.cmd vitest run
.venv\Scripts\python.exe -m pytest tests\test_lab.py tests\test_cloud.py -q
npm.cmd run build
```

前端用 DOM 环境和图表生命周期模拟复现原白屏路径；云端协议用测试替身验证，不代表真实服务器已接通。此前原生 MATLAB/Simulink 本机实测记录在 `docs/native-verification.json`，也不代表云端已上线。

API 文档：`http://127.0.0.1:8765/docs`；接口清单：[docs/API.md](docs/API.md)。
