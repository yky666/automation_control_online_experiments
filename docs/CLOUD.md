# 学校云端运行方案

## 现在能使用的功能

学校已有许可、尚无服务器。2.1 学生界面使用静态示例与官方 GitHub 跳转：无 Online 权限时查看代码、默认结果示例并下载到本地；已有可用权限时跳转打开对应任务，运行在个人 MATLAB Online 会话。当前参数修改会复制到剪贴板，需在 Online 粘贴后点击 Run。

按钮实际执行“复制脚本＋打开官方仓库文件”，不自动执行或自动回传结果。网页不能跨站读取 MathWorks 登录态和许可证；许可选项是用户选择，最终权限由 MathWorks 验证。MathWorks 还提供有时限的基本版，不能声称本网页严格验证了学校付费许可。[官方 GitHub 跳转说明](https://www.mathworks.com/help/matlab/matlab_env/open-github-repositories-in-matlab-online.html)与[Online 版本说明](https://www.mathworks.com/products/matlab-online/matlab-online-versions.html)说明其实际行为。

## 无计算服务器的发布

2.1 学生页面可通过 GitHub Pages 发布。仓库 Settings → Pages 选择 GitHub Actions，再运行手动工作流 `Publish static course website`。页面只读取静态示例，实际 MATLAB/Simulink 运行发生在用户个人会话。

以下内容是可选的教师计算服务扩展；当前学生页面不调用后台运行接口。学校许可本身不会产生本项目可直接调用的 REST 接口。

## 免 MATLAB 平台部署

在学校服务器执行 `docker compose up --build -d`，把 8765 端口通过 HTTPS 反向代理提供给学生。容器包含前端、SciPy、报告和课程材料，没有 MATLAB 依赖。平台求解并非原生 MATLAB 或 Simulink。

默认 `CONTROL_LAB_SESSION_ISOLATION=1`，学生浏览器会话只访问自己的运行、CSV 和报告，数据保存到 Docker 卷。真实令牌不要写入前端或版本库。

当前设备没有 Docker，未验证实际镜像构建或云上部署。Python 服务、会话隔离和接口协议已进行自动化验证。

## 可选的真实 MATLAB/Simulink 工作节点

由学校 IT 或 MathWorks 确认许可适用于服务器和并发用途，准备授权 MATLAB、Control System Toolbox、Simulink 与 Python Engine 环境。不能从学生账户可登录，直接推定可以作为共享服务器运行。

在计算服务器设置强随机令牌并启动工作节点：

```powershell
$env:CONTROL_LAB_WORKER_TOKEN='<学校生成的服务端令牌>'
.venv\Scripts\python.exe -m uvicorn backend.cloud_worker:app --host 127.0.0.1 --port 8766
```

通过学校 HTTPS 反向代理暴露节点。在学生平台服务端设置：

```text
CONTROL_LAB_MATLAB_URL=https://学校工作节点域名
CONTROL_LAB_WORKER_TOKEN=同一服务端令牌
```

学生平台将校验后的参数转发到 `/v1/run`，节点重新构建模型并执行真实 MATLAB/Simulink，返回曲线与模型文件。学生不接触许可、令牌或 MATLAB 路径。

`/v1/run` 是本项目的桥接协议，不直接等于任意 MathWorks REST 地址。已有 Production Server 时，需要部署实验函数并实现对应协议适配。

节点要求认证，只接受已知任务、有限数值和受支持求解器；单节点一次运行一项，忙碌返回 429；每次有独立目录、进程和 180 秒时限。共享节点不开放任意代码执行，自由脚本使用学生个人 Online 会话。

`GET /api/health` 可查看 2.0 版本与 `capabilities.native`。未配置服务时不显示可调用引擎；配置后仍需在真实服务器运行实验确认许可、网络与文件返回。

另一条路线是用 [Simulink Compiler](https://www.mathworks.com/products/simulink-compiler.html)和 [Web App Server](https://www.mathworks.com/products/matlab-web-app-server.html)部署预编译仿真。它支持用户不安装本机 MATLAB，但不能自动替代自由脚本或完整图形编辑器。
