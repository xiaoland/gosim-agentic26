# 资料与事实核对

核对日期：2026-10-01，北京时间。动态信息后续需重新核实。

## 一手资料

- [比赛官网](https://create.gosim.org/agenticapp26/)：用户给出的 `/agentic26` 返回 404，有效地址是 `/agenticapp26/`。浏览器实时页面使用 Rinx 名称；搜索缓存中的 robrix2 名称较旧。
- [官方赛程与提交要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md)：主场景选 Navigation。初赛截止 2026-10-04 23:59、复赛截止 10-09 23:59、线上决赛 10-12、前三名现场展示 10-17，均北京时间。官网标注部分中间时段是配套排期，后续通知优先。
- [Navigation 场景](https://octosense.org/cn/apps/navigation/)：围绕日程、地点、路况提出计划，用户确认后执行并跟进变化。体验指南中的概念与示例数据不等于已发布 API。
- [官方实现路径](https://create.gosim.org/agenticapp26/#steps)：帝王蟹能力层允许补充数据或操作能力，接入邮件、日历、消息及设备状态；用户已选择此方向。Navigation 场景与能力层是不同维度，不是互斥的主场景。
- [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)：保存目录、校验和宿主工具；应用应有自己的源码仓库，工具链作为 sibling checkouts。遵从其 FIRST-APP.md 指向的 script-app 模板。
- [开发模板与工具](https://github.com/OctoSense-org/OctoScript-App-Design-Flow)：QUICKSTART、SCRIPT-API、CAPABILITIES 和 AI-SERVICES。精确源码版本见 `toolchain/sources.lock.json`。

官网要求可运行作品、公开 Apache-2.0 源码、固定宿主版本、启动说明和真实任务证据。Rinx 是主要基线，作品需在注明版本的 OctoSense 或 Rinx 环境验收。Hub 检查是包预检，不替代运行/交互/Agent 任务核验，也不代表比赛录取或验收；当前无需等待上架。此仓库目前仅完成开发初始化。

## 用户需求与二手讨论

已通过用户 Chrome 登录会话阅读 Project《比赛赛道说明》，并以本聊天中用户直接提供的产品描述为需求依据：限定时间内组合步行、公交、地铁、打车，最低费用到达，后续考虑疲劳和速度。

Project 中 ChatGPT 给出的架构/赛事解释是二手材料。“最晚出发”是对“最慢”的建议解释，尚未替用户定案。讨论中的票价、时间、地点均不作为真实服务数据。本仓库不复制整个私有聊天或其他会话内容。

用户于 2026-10-01 指定初赛演示：“40 分钟内到机场，预算 50，尽量便宜。”机场和货币需要由上下文补全，并要求通过操作用户手机上的既有应用完成任务，不自行接入地图、打车、地铁查询、日程、提醒等服务。这是本项目的用户约束，不宣称为赛事要求。具体目标手机与应用尚待确定。

## 已知技术边界

锁定版本的文档说明 card-host 不提供 host services，普通 Hub script app 的宿主 Agent 能力仍存在实现缺口。只验证本机 macOS arm64 原生 card-host；Rinx、手机、定位、地图、实时交通、模型调用尚未验证。上游 AI-SERVICES.md 的技术状态主要记录于 2026-09-27，接入时应重新核对代码。

2026-10-01 为机场演示复核了[初赛交付要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md#初赛需求成立作品能跑)与[按作品形态交付](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md#按作品形态交付)：需可运行原型、实际操作及可核验结果，并展示失败或空状态；提交形态与宿主、平台、依赖和启动说明需要匹配。桌面控制手机的实验不能自行当作已经验证赛事宿主集成。

[Android UI Automator 官方文档](https://developer.android.com/training/testing/other-components/ui-automator)说明可在应用进程外与用户及系统应用交互，并取得控件和截图。这是候选操作技术的依据，不是本仓库或任意地图应用已可用的证据；手机系统、应用页面可读性和真实操作仍须逐一验证。

## 开发协作方法来源

[xiaoland/svc](https://github.com/xiaoland/svc) 本次采用版本为 Corpus 15.0.0，commit `4fe4c66ac4deb35209069c00b1bbdc1b22aae3af`。仅采用 `corpus/specs/` 的知识归属和 `corpus/task-packet/` 的任务控制语义，固定入口见 [知识导航](index.md)；未安装完整 CLI，也未引入其它模块。上游模板按需参考，项目说明与实际任务包由本仓库维护。

`../factory26/AGENTS.md` 是本轮用户指定的本地参考，读取于 2026-10-01。只借鉴知识回流、非简单任务的 packet、授权追溯和有界协作原则；其专属实验规则、模型与预算配置、自主提交授权和测试禁令不转移到本仓库。
