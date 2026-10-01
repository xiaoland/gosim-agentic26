# Navigation 开发入口

本仓库开发 Navigation 帝王蟹能力层作品。产品目标与当前实现范围归 [README](README.md)，不能将草稿界面作为已完成的路线规划或能力层作品展示。

用英文思考，用中文与用户沟通和编写项目说明。共享开发指引只维护在 `AGENTS.md`。若有 `AGENTS.local.md`，随后读取；个人指南不写入共享说明。

## 仓库与知识入口

```text
bundle/       应用源码、清单与真实截图；当前只有这里属于 Hub 应用包
docs/         技术草案、事实来源、验证记录与知识导航
tasks/        当前任务的问题、方案、授权、计划和恢复点
tools/        工具链包装及原生应用测试
toolchain/    上游源码与 Rust 依赖锁定信息
README.md     产品需求、当前能力、开发操作与参赛交付说明
```

先读 [文档与任务导航](docs/index.md)，再按本次任务读取其知识归属。改行为前读 README 的 [产品目标](README.md#产品目标) 与 [当前能力](README.md#当前能力)，以及 [技术草案](docs/architecture.md)；接续任务先读对应 `tasks/<task>/packet.md`。

## 协作与授权

理解用户期望的结果，区分需求、当前事实和提议；用证据检验技术判断。调查、只读分析、隔离实验和 task packet 整理可以自主推进。

源码修改需要用户授权。用户直接要求实现、修复、重构或具体初始化改动，即授权该范围必要的修改、验证和文档更新；不重复索取已有授权。实质范围变化、不可逆操作或缺少用户特定信息时，先完成独立工作，再呈现最小的待决定事项。

用户已于 2026-10-01 授权自主 Git commit；提交仅纳入当前获授权任务的改动，保留其它工作区修改。推送、签名、发布和赛事提交仍需要对应授权。参考仓库中的授权、实验配方和个人偏好不自动适用于这里。

较长任务报告有意义的发现、方向变化和阻塞；开工后持续完成已授权范围。主 Agent 负责整合；必要的有界委派只传目标、材料入口、权限边界、返回要求和停止条件，结果用实际证据核验。

## 文档知识与 task packet

本项目仅采用 SVC 的 `specs/` 知识归属和 `task-packet/` 机制，版本和按需阅读入口见 [知识导航](docs/index.md)。不安装完整 SVC CLI，不引入其它 Corpus 模块、Agent 配置或编排设施。

知识归属见 [文档导航](docs/index.md)。可由源码、配置或锁文件直接维护的事实以它们为准。只更新实际受影响的归属，不复制说明或创建空模板。

非简单任务主动建立或接续 `tasks/<task>/packet.md`。用中文简要记录目标、边界与用户授权、完成依据、当前事实及不确定性、下一步；用户需要决定事项时明确写出。授权保留原话及其范围，计划改变时同步更新当前正文，不用追加历史声明掩盖旧决定。

从一个 `packet.md` 开始；仅当独立的计划、调查、设计、决定或证据确有检索和维护压力时拆出 supporting files，并保留短入口。任务包不是运行时调度系统，也不是长期产品文档。接受的持续知识随任务回流到其归属；用户验收且无剩余恢复价值后可删除任务包，不强制建立归档。未决事项必须有接续入口。

开发任务包可纳入 Git，但本机路径、凭据和原始运行日志按各自边界保存。Hub 扫描的 review packet 属于忽略的 `build/`，与 `tasks/` 不同；两者都不进入 `bundle/`。

## 应用开发与验收

官方工具链在仓库同级 `.octosense-agentic26/`，版本归 `toolchain/sources.lock.json`。使用 `make bootstrap`、`make doctor`、`make run`、`make smoke` 和 `make check`；实际命令与环境见 [README](README.md)。

修改应用前按需查官方 [QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)、[SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md) 与 [CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md)。不能凭文档中的概念演示或清单声明虚构已实现的宿主 API；核对目标版本源码并实际调用。

- LLM 解释意图、提取约束和解释结果；确定性规划器计算路线和费用。上下文与交通数据保留来源、时间和适用范围；推断偏好不能伪装成用户明确指示。
- 只申请实际使用的能力，每个 HTTPS 主机都声明在 `network.hosts`；不使用 HTTP。账户凭据由宿主或服务端管理，不在应用中收集密码、PIN 或验证码，不把凭据写入 `bundle/`。
- 原生检查使用隐藏窗口与隔离数据，只关闭本任务启动的实例。非平凡行为用实际交互和适当测试验证；文档调整核对引用和归属，不新增内容测试。
- 截图必须来自实际运行并查看过。当前只验证 macOS arm64 card-host，新增平台声明必须有运行证据。
- 包编辑后重新盖摘要，签名后再编辑需要重新盖摘要和签名。`make check` 的包预检不替代应用任务验收。
- 密钥、`.local-state/`、`build/`、工具链和日志不进入应用包或 Git。发布者信息、签名和赛事交付依 [PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md) 的对应授权推进。

私人 ChatGPT 讨论只帮助理解需求，赛事规则以官方资料为准；来源及已知边界见 [资料核对](docs/sources.md)。
