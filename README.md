# Control Lab · 自动控制在线实验

六章共 33 项任务，包含默认完整展开的原理推导、原理图、可编辑 MATLAB 代码、参数修改和结果示例。当前学生网页采用 **静态示例 + MATLAB Online 跳转**，无需部署计算服务器或安装本机 MATLAB Engine。

[![Open in MATLAB Online](https://www.mathworks.com/images/responsive/global/open-in-matlab-online.svg)](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab1_tf1.m)

## 学生使用

1. 默认浏览六章内容、默认参数的预计算结果和示例报告，无需 Online 许可。
2. 修改任务参数、传递函数、输入信号或采样设置，MATLAB 代码随之更新。图表仍为默认示例，不代表修改后的代码已执行。
3. 没有 Online 权限时，复制或下载 `.m`，到本地 MATLAB 运行；Simulink 页可下载生成模型的脚本。
4. 已有可用的 MATLAB Online 许可时，在右侧勾选对应选项，再点击“复制并打开 MATLAB Online”。官方跳转链接克隆本仓库并打开当前任务文件，登录和使用权限由 MathWorks 验证。
5. 仓库文件使用默认参数。当前修改或手动编辑已复制到剪贴板，需在 Online 编辑器中粘贴并点击 **Run**。Simulink 任务还需要相应产品权限。
6. 参数扫描下载各组代码，在 MATLAB 执行；个人报告应使用实际运行结果。网页示例报告供格式与理论对照参考。

网页不会自动读取 MathWorks 账户、许可证或个人运行结果。勾选许可是用户的使用方式选择，并非本网页已经验证许可证。[官方 GitHub 跳转说明](https://www.mathworks.com/help/matlab/matlab_env/open-github-repositories-in-matlab-online.html)说明链接打开文件的行为；[Online 版本说明](https://www.mathworks.com/products/matlab-online/matlab-online-versions.html)说明许可版和基本版。MathWorks 也提供有时间限制的基本版，因此不能把未关联学校许可直接等同于官方禁止访问。

## 无服务器发布

本项目支持 GitHub Pages。仓库包含手动工作流 `.github/workflows/pages.yml`，不会因推送代码自动发布。

在仓库 **Settings → Pages** 将 Source 设为 **GitHub Actions**，再在 **Actions → Publish static course website → Run workflow** 运行。发布成功后，地址为 `https://yky666.github.io/automation_control_online_experiments/`。这个地址只有工作流成功部署后才可访问。

工作流生成匿名默认示例、HTML 报告和静态课程资源，以仓库子路径构建。页面不调用 Python API，也不需要学生访问 localhost。

## 本机开发

Windows 一键安装与启动：

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1 -OpenBrowser
```

已有环境可重新导出和构建：

```powershell
.venv\Scripts\python.exe tools\export_online.py
node tools\export_scripts.mjs
npm.cmd run build
```

浏览器访问 `http://127.0.0.1:8765`，更新后按 **Ctrl+F5**。也可双击“重启实验网页.cmd”。

跨平台需 Python 3.12、Node 24；安装 `requirements-cloud.txt` 和 npm 依赖后执行 `npm run export:online`、`npm run build`。静态文件在 `dist/`，可托管到任何支持 HTTPS 的静态服务。

## 实验与代码

| 章节 | 内容 | MATLAB Online 默认任务 |
| --- | --- | --- |
| 1 | 数学模型与传递函数 | [四阶传递函数](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab1_tf1.m) |
| 2 | 典型环节模拟 | [比例环节](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab2_p.m) |
| 3 | 时域性能分析与设计 | [二阶系统](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab3_second.m) |
| 4 | 控制系统稳定性分析 | [三阶系统](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab4_stability1.m) |
| 5 | 频率特性测试与验证 | [惯性环节](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab5_frequency_inertia.m) |
| 6 | 频域法串联超前校正 | [单级超前校正](https://matlab.mathworks.com/open/github/v1?repo=yky666/automation_control_online_experiments&file=matlab/online/lab6_lead1.m) |

`matlab/online/` 有 66 份参数脚本：每个任务一份 MATLAB 脚本和一份 Simulink 模型脚本。脚本生成来自同一套参数配方；默认曲线由 SciPy 预计算，并明确标注来源。理想微分等非真有理模型仅做代数和频率分析，Simulink Transfer Fcn 仿真需要先加入滤波。

`frontend/` 是 React 工作台；`backend/` 保留数值计算、运行记录、报告和可选授权工作节点，供教师扩展。当前学生跳转界面不使用这些运行接口。[云端扩展说明](docs/CLOUD.md)描述服务端原生计算条件。

不提交 `.venv`、`node_modules`、运行记录、个人报告、令牌或 Simulink 缓存。课程中已有的个人实验报告也不进入公开静态资源。

## 验证

```powershell
npm.cmd test
.venv\Scripts\python.exe -m pytest tests\test_lab.py tests\test_cloud.py tests\test_online.py -q
npm.cmd run build
```

前端测试覆盖全部任务切换、许可选择、默认示例与当前脚本区分、MATLAB/Simulink 官方跳转和既有平台回归。DOM 测试不代表自动登录学校账户或真实浏览器截图验收。原有本机 MATLAB/Simulink 检查也不代表已接通云端后台。
