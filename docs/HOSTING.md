# 公网托管记录

## 已发布的公网镜像

- URL：https://control-lab-yky666.craftychord64.chatgpt.site/
- 平台：Sites，访问范围 `public`，无需访客连接应用。
- 发布时间：2026-10-21（北京时间）。
- 上游代码：GitHub `54e2b6184577f1dc267be135cd9e4cbee0156b4c`，包含拖动模块崩溃修复。
- 构建：Vite 根路径 `/`；六章、38 项任务、两个仿真 Worker、201 项关联资源静态检查通过，前端 26 项测试通过。
- 平台已返回 `succeeded`、正式 URL；随后读取访问配置确认 `public`。当前执行环境的匿名 HTTP 检查被 Cloudflare 返回 403，因此没有声称完成真实浏览器验收。

供后续更新使用的非敏感标识（不得创建重复 Site）：

```json
{
  "project_id": "appgprj_6ad89fd451808191a20399323f8f613b",
  "source_commit_sha": "13c753acb7901a46a0c4531c1e76faf16faa8669",
  "saved_version_id": "appgprj_6ad89fd451808191a20399323f8f613b~appgver_1f280d6c4f7881919cb6c475cd2a8aa4",
  "deployment_id": "appgdep_6ad8a12b531c8191ac5d574e62ffb31e",
  "access_mode": "public"
}
```

本地托管源码及 `.openai/hosting.json` 保存在忽略目录 `runtime/control-lab-public-20261021/`。镜像使用发布时的静态构建；修改上游功能后需重新构建、同步并发布镜像，不能只更新 GitHub 源码就宣称镜像已更新。继续更新时先读取同一 Site 的状态，按 Sites source helper 流程取得新凭据并同步；令牌不保存到仓库。

## GitHub Pages

正式 URL：https://yky666.github.io/automation_control_online_experiments/

2026-10-21（北京时间），仓库管理员将 Source 设为 GitHub Actions 后，重新运行发布流程，build 和 deploy 均成功。[成功部署记录](https://github.com/yky666/automation_control_online_experiments/actions/runs/39592495291/attempts/2)，发布代码 `fa456f73ed997178acf7359e5c13fc7c41fa16e4`。

匿名 HTTP 检查通过：首页及 JS/CSS 资源返回 200，课程目录包含六章共 38 项任务，六章各抽查一份示例数据、示例报告、PI/双级超前原生电路模型和建模脚本均可访问。此为网络资源检查，不代表自动登录 MathWorks 或真实浏览器交互验收。

自动流程 `.github/workflows/pages.yml` 在推送 `main` 后测试、以 `/automation_control_online_experiments/` 构建、检查 201 项关联资源并发布。日后无需再次设置 Pages；手动发布可运行 **Publish static course website**。

GitHub Pages 不运行 Python、MATLAB 或 Simulink 服务端。浏览器数值仿真照常运行，原生代码通过访客个人 MATLAB Online 会话执行。
