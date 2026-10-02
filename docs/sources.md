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

用户补充“初赛代码只要求 octoscript 的应用”，本项目据此收敛交付范围。[公开赛程固定版本](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/cc56fa42bcff23ec0df51e91191b0e283458a970/docs/competition-schedule.md#初赛需求成立作品能跑)也明确初赛不以 Rust 或 ROM 开发为门槛；可运行原型、操作结果、失败或空状态与复现材料的要求仍然保留。该证据不要求本项目新增原生宿主服务。

## 用户需求与二手讨论

已通过用户 Chrome 登录会话阅读 Project《比赛赛道说明》，并以本聊天中用户直接提供的产品描述为需求依据：限定时间内组合步行、公交、地铁、打车，最低费用到达，后续考虑疲劳和速度。

Project 中 ChatGPT 给出的架构/赛事解释是二手材料。“最晚出发”是对“最慢”的建议解释，尚未替用户定案。讨论中的票价、时间、地点均不作为真实服务数据。本仓库不复制整个私有聊天或其他会话内容。

用户于 2026-10-01 指定初赛演示：“40 分钟内到机场，预算 50，尽量便宜。”机场和货币需要由上下文补全。演示城市为深圳；用户已撤回仅操作手机既有应用、禁止直接接入服务的限制，提供本机服务配置，并授权开工。当前使用比赛官方工具链搭建可直接调用服务的 Navigation Agent，主 Agent 负责协调，有界工作委派给 GPT-6.1-Sol ExtraHigh；授权范围与执行状态归[任务包](../tasks/capability-boundary/packet.md#目标与授权)。

用户进一步明确：应用模型使用 MiniMax M3；mock/demo 也要分别保留日历、笔记等来源，不能预先合成为一个行程背景文件。用户已要求创建本地 `.env`，由其填入高德、MiniMax 等配置；创建配置文件不代表接入或运行验证完成。

## 已知技术边界

原有 card-host 不提供 host services，继续用于隔离脚本检查。另行固定的 stock OctoSense desktop 已在 macOS arm64 构建并验证 `model.complete`、独立文件读取与真实地图请求；完整 Navigation 任务的验收归[任务包](../tasks/capability-boundary/packet.md)。手机、实际 GPS 与 Rinx 集成尚未验证。旧 AI-SERVICES.md 主要记录 2026-09-27 状态，不能据此断言较新官方宿主没有 Agent 服务。

2026-10-01 为机场演示复核了[初赛交付要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md#初赛需求成立作品能跑)与[按作品形态交付](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md#按作品形态交付)：需可运行原型、实际操作及可核验结果，并展示失败或空状态；提交形态与宿主、平台、依赖和启动说明需要匹配。桌面控制手机的实验不能自行当作已经验证赛事宿主集成。

2026-10-01 核对并运行了以下固定源码。新增宿主的版本与补丁摘要归 [agent-runtime.lock.json](../toolchain/agent-runtime.lock.json)，原 card-host 版本保持独立：

- [官方课程分工](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/curriculum.md#八个项目各自负责什么)：octos 是运行时内核，octoscode／OctoLoop 用于开发协作与审查；按选题组合项目，不要求接齐全部工具。
- [OctoSense Cargo.toml](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/Cargo.toml)：本次调查提交 d405d5c，配套 octos ae230ce 和 App Hub 58c3c8a，实施时必须沿用宿主兼容组合。
- [AI 宿主注册](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/ai-host/src/lib.rs)与[应用 peer](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/ai-host/src/contained.rs)：已注册 model 与 octos，当前 shipped 策略默认等待用户同意；不能照搬旧说明中默认关闭的状态。
- [脚本应用工具执行器](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/shell/src/host_tools/script_apps.rs)和 [News 工具示例](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/news/bundle/tools.json)：读取经准入检查的 tools.json，host-service 工具走服务调用与结果队列；声明 implemented_by 为 app 不代表该执行器已经能执行脚本工具。该限制不禁止 OctoScript 自行调用脚本函数。此原生工具集成路径暂不作为初赛前置。
- [model.complete 参数与选择逻辑](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/ai-providers/host-service/src/complete/mod.rs)及[请求封装](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/ai-providers/host-service/src/complete/wire.rs)：只接受 task、input、schema、class、allow_urls；拒绝额外字段。它按宿主提供方顺序与 fast／strong 分类选模型，可能尝试其他提供方；本项目隔离配置只允许 MiniMax-M3 且无 fallback。返回经 schema 校验的 JSON，没有原生工具调用或历史透传；应用侧 callback 循环已完成两轮真实调用与工具结果回传。该版本不透传 thinking／extra_body；input、schema 上限分别为 32、8 KiB，宿主服务等待上限为 60 秒。
- [当前锁定 SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/e08517254d9b2c316352eec4f959810d9ad22d40/docs/SCRIPT-API.md#network)记录 `net.http_request` 的 HTTPS 请求及 `fs` 的应用隔离存储访问。接口存在不等于模型凭据通道或多源文件导入已实现；网络主机声明及权限仍须满足。

## MiniMax M3

应用模型由用户指定，不再是待选提供方。[MiniMax M3 官方页面](https://www.minimaxi.com/models/text/m3)使用模型标识 `MiniMax-M3`；[OpenAI 兼容接口文档](https://platform.minimax.cn/docs/api-reference/text-openai-api)列出该模型和函数工具支持，国内平台 Base URL 为 `https://api.minimax.cn/v1`。本机配置采用此地址，其他地区账户应使用所属平台的地址；不自行改为文档示例中的其他模型。

原生 Function Call 多轮需要按提供方协议回传完整 assistant 消息和工具结果。这个 API 能力不能直接等同于 `model.complete` 的能力；后者只暴露结构化单次调用。2026-10-01 的服务侧预检已验证返回模型均为 `MiniMax-M3`，并完成原生工具往返；随后 stock 官方宿主也通过了结构化动作、脚本读取独立随机值、模型继续回答的两轮探针。条件与后续应用验收归[任务包](../tasks/capability-boundary/packet.md)。

## 深圳服务候选

2026-10-01 已完成文档核对及带 Key 的隔离接口验证，地点、驾车、公共交通和步行查询均成功，条件与范围归[任务包](../tasks/capability-boundary/packet.md#服务预检证据)：

- [路径规划 2.0](https://lbs.amap.com/api/webservice/guide/api/newroute)列出公共交通、步行和驾车查询，以及时间、费用和出租车估价字段。实际深圳响应已出现公交候选中的 taxi 路段、换乘总费用与耗时；不能据此保证存在符合 40 分钟／50 元的混合方案。地图出租车估价不等于某网约车平台的实时可下单报价。
- [基础服务配额](https://lbs.amap.com/pages/base_service_price)按账户认证和服务类别区分，不能假定新建未认证账户即可调用全部接口；准备阶段需确认 Web 服务 Key 的相关权限和配额，不预先购买未确认需要的套餐。
- [地图 URI](https://lbs.amap.com/api/uri-api/guide/travel/route)按单一 mode 查询路线，不能据此承诺保留任意公交接打车方案；导航交接须分段处理或另行验证。

后续有限查询确认 `transits[].cost.transit_fee` 是完整候选总费用，混合方案不可再次加上 `taxi.price`；总耗时按官方定义包含等车，但没有独立证明出租车叫车等待。完整混合候选只能按供应商估计比较，全程驾车时长则不能冒充包含候车的出租车时长。官方公交参数支持 `strategy=0/3/8`（推荐／少步行／时间短）与大小写敏感的 `AlternativeRoute`，可据结果追加一组完整候选。

机场查询还观察到 POI 吸附差异：`route.destination` 可能保留请求坐标，实际末段却停在地铁出口。不得仅靠该字段判断到达航站楼；必须核对实际末段 polyline 与任务终点，坐标匹配仍不证明楼层、安检或实际抵达。

首轮演示背景分别使用日历文件、笔记和设备位置记录，由工具在运行时独立读取、关联并保留依据；不提供预合并的行程背景答案。它只证明多源上下文处理，不证明在线日历、笔记账户或定位接入。天气、提醒、在线日历及网约车实时报价服务是否增加，由演示必需能力和接口实测决定。

## 开发协作方法来源

[xiaoland/svc](https://github.com/xiaoland/svc) 本次采用版本为 Corpus 15.0.0，commit `4fe4c66ac4deb35209069c00b1bbdc1b22aae3af`。仅采用 `corpus/specs/` 的知识归属和 `corpus/task-packet/` 的任务控制语义，固定入口见 [知识导航](index.md)；未安装完整 CLI，也未引入其它模块。上游模板按需参考，项目说明与实际任务包由本仓库维护。

`../factory26/AGENTS.md` 是本轮用户指定的本地参考，读取于 2026-10-01。只借鉴知识回流、非简单任务的 packet、授权追溯和有界协作原则；其专属实验规则、模型与预算配置、自主提交授权和测试禁令不转移到本仓库。
