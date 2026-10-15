# Control Lab 2.0 API

地址 `http://127.0.0.1:8765`，交互文档 `/docs`。POST 需要 `Content-Type: application/json` 和 `X-Control-Lab: 1`。同源部署支持 HTTPS 域名；容器模式按浏览器会话隔离运行与报告。

| 路径 | 用途 |
|---|---|
| GET `/api/health` | 2.0 版本、平台计算和授权引擎状态 |
| GET `/api/catalog` | 六章内容、任务参数定义、原始材料 |
| POST `/api/preview` | 无存档平台预览，不使用本机 MATLAB |
| POST `/api/run` | 运行并保存实验 |
| POST `/api/code/template` | 生成 MATLAB 代码与 Simulink Online 模型脚本 |
| POST `/api/code/run` | 仅限显式启用的教师本机调试，学生使用 Online |
| POST `/api/scan` | 2～8 组参数或输入幅值扫描 |
| GET `/api/runs` | 当前会话运行摘要 |
| GET `/api/runs/{id}` | 完整模型、数据、指标和来源 |
| GET `/api/runs/{id}/data.csv` | 时域数据 |
| GET `/api/runs/{id}/measurements.csv` | 频率测点 |
| GET `/api/runs/{id}/model.slx` | 本次原生仿真生成的模型（存在时） |
| POST `/api/report` | 保存的运行生成 html/markdown/json/zip |

默认 `engine=scipy` 是免 MATLAB 平台计算。`matlab/simulink` 需要配置授权工作节点，或者明确启用教师调试，见 CLOUD.md。

```json
{"lab_id":3,"task_id":"second","params":{"zeta":0.5,"wn":10},"engine":"scipy","stop_time":5,"points":1501,"amplitude":1,"settling_threshold":0.02,"auto_duration":true}
```

同时提供 `numerator` 和 `denominator` 可替换最终模型（降幂系数）。`input_signal` 可取 step/ramp/sine/step_ramp/polynomial。正弦默认自动选择稳态窗口；`auto_duration=false` 时 `stop_time` 生效。

```json
{"request":{"lab_id":1,"task_id":"tf1","engine":"scipy"},"parameter":"amplitude","values":[0.5,1,2]}
```

所有任务支持输入幅值扫描，手动窗口支持 `stop_time` 扫描；模型参数按任务定义验证。

报告示例：

```json
{"run_ids":["已保存运行编号"],"format":"zip","student":{"name":"学生姓名","student_id":"学号"},"analysis":"自己的分析与反思"}
```

云端工作节点协议是服务端认证的 `POST /v1/run`，请求为 `{"experiment":运行请求}`，不是任意 MathWorks REST API 的通用代理。配置与许可要求见 CLOUD.md。
