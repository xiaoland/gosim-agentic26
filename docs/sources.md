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

用户于 2026-10-01 指定初赛演示：“40 分钟内到机场，预算 50，尽量便宜。”机场和货币需要由上下文补全。当前演示城市确定为深圳；用户撤回仅操作手机既有应用、禁止直接接入服务的限制，选择使用比赛官方工具链搭建可直接调用服务的 Navigation Agent。最新指示是先继续方案和计划，需要的服务后续由用户准备，当前不进入产品实现。

## 已知技术边界

本仓库锁定的 card-host 不提供 host services；目前只验证 macOS arm64 原生草稿开发闭环，Rinx／OctoSense shell、手机、定位、地图和模型调用均未验证。锁定 AI-SERVICES.md 主要记录 2026-09-27 状态，不能据此断言较新官方宿主没有 Agent 服务。

2026-10-01 为机场演示复核了[初赛交付要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md#初赛需求成立作品能跑)与[按作品形态交付](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md#按作品形态交付)：需可运行原型、实际操作及可核验结果，并展示失败或空状态；提交形态与宿主、平台、依赖和启动说明需要匹配。桌面控制手机的实验不能自行当作已经验证赛事宿主集成。

2026-10-01 为服务接入方案核对了以下固定源码，尚未构建或运行该组合，也未替换本仓库锁文件：

- [官方课程分工](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/curriculum.md#八个项目各自负责什么)：octos 是运行时内核，octoscode／OctoLoop 用于开发协作与审查；按选题组合项目，不要求接齐全部工具。
- [OctoSense Cargo.toml](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/Cargo.toml)：本次调查提交 d405d5c，配套 octos ae230ce 和 App Hub 58c3c8a，实施时必须沿用宿主兼容组合。
- [AI 宿主注册](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/ai-host/src/lib.rs)与[应用 peer](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/ai-host/src/contained.rs)：已注册 model 与 octos，当前 shipped 策略默认等待用户同意；不能照搬旧说明中默认关闭的状态。
- [脚本应用工具执行器](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/shell/src/host_tools/script_apps.rs)和 [News 工具示例](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/news/bundle/tools.json)：读取经准入检查的 tools.json，host-service 工具走服务调用与结果队列；脚本内实现的工具不能直接视为可执行。Navigation 服务及其权限仍需本项目实现和实测。

## 深圳服务候选

2026-10-01 的文档核对支持首选高德 Web 服务进行接口验证，尚未发起带 Key 的实际请求：

- [路径规划 2.0](https://lbs.amap.com/api/webservice/guide/api/newroute)列出公共交通、步行和驾车查询，以及时间、费用和出租车估价字段；公交结果可描述打车路段。字段是否返回及深圳具体路线是否可用仍需实测，不能据此保证存在符合 40 分钟／50 元的混合方案。地图出租车估价不等于某网约车平台的实时可下单报价。
- [基础服务配额](https://lbs.amap.com/pages/base_service_price)按账户认证和服务类别区分，不能假定新建未认证账户即可调用全部接口；准备阶段需确认 Web 服务 Key 的相关权限和配额，不预先购买未确认需要的套餐。
- [地图 URI](https://lbs.amap.com/api/uri-api/guide/travel/route)按单一 mode 查询路线，不能据此承诺保留任意公交接打车方案；导航交接须分段处理或另行验证。

首轮行程来源可采用明确标注的演示文件，由工具在运行时读取；它只证明上下文读取，不证明在线日历或航班服务接入。天气、提醒、在线日历及网约车实时报价服务是否增加，由演示必需能力和接口实测决定。

## 开发协作方法来源

[xiaoland/svc](https://github.com/xiaoland/svc) 本次采用版本为 Corpus 15.0.0，commit `4fe4c66ac4deb35209069c00b1bbdc1b22aae3af`。仅采用 `corpus/specs/` 的知识归属和 `corpus/task-packet/` 的任务控制语义，固定入口见 [知识导航](index.md)；未安装完整 CLI，也未引入其它模块。上游模板按需参考，项目说明与实际任务包由本仓库维护。

`../factory26/AGENTS.md` 是本轮用户指定的本地参考，读取于 2026-10-01。只借鉴知识回流、非简单任务的 packet、授权追溯和有界协作原则；其专属实验规则、模型与预算配置、自主提交授权和测试禁令不转移到本仓库。
