# 资料与事实核对

核对日期：2026-10-01，北京时间。动态信息后续需重新核实。

## 一手资料

- [比赛官网](https://create.gosim.org/agenticapp26/)：用户给出的 `/agentic26` 返回 404，有效地址是 `/agenticapp26/`。浏览器实时页面使用 Rinx 名称；搜索缓存中的 robrix2 名称较旧。
- [官方赛程与提交要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md)：主场景选 Navigation。初赛截止 2026-10-04 23:59、复赛截止 10-09 23:59、线上决赛 10-12、前三名现场展示 10-17，均北京时间。官网标注部分中间时段是配套排期，后续通知优先。
- [Navigation 场景](https://octosense.org/cn/apps/navigation/)：围绕日程、地点、路况提出计划，用户确认后执行并跟进变化。体验指南中的概念与示例数据不等于已发布 API。
- [官方实现路径](https://create.gosim.org/agenticapp26/#steps)：帝王蟹能力层允许补充数据或操作能力，接入邮件、日历、消息及设备状态；用户已选择此方向。Navigation 场景与能力层是不同维度，不是互斥的主场景。
- [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)：保存目录、校验和宿主工具；应用应有自己的源码仓库，工具链作为 sibling checkouts。遵从其 FIRST-APP.md 指向的 script-app 模板。
- [开发模板与工具](https://github.com/OctoSense-org/OctoScript-App-Design-Flow)：QUICKSTART、SCRIPT-API、CAPABILITIES 和 AI-SERVICES。精确源码版本见 `toolchain/sources.lock.json`。

官网要求可运行作品、公开 Apache-2.0 源码、固定宿主版本、启动说明和真实任务证据。Rinx 是主要基线，作品需在注明版本的 OctoSense 或 Rinx 环境验收。Hub 检查是包预检，不替代运行/交互/Agent 任务核验，也不代表比赛录取或验收；当前无需等待上架。当前实现与完成证据归 README 和任务包。

用户补充“初赛代码只要求 octoscript 的应用”，本项目据此收敛交付范围。[公开赛程固定版本](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/cc56fa42bcff23ec0df51e91191b0e283458a970/docs/competition-schedule.md#初赛需求成立作品能跑)也明确初赛不以 Rust 或 ROM 开发为门槛；可运行原型、操作结果、失败或空状态与复现材料的要求仍然保留。该证据不要求本项目新增原生宿主服务。

## 用户需求与二手讨论

已通过用户 Chrome 登录会话阅读 Project《比赛赛道说明》，并以本聊天中用户直接提供的产品描述为需求依据：限定时间内组合步行、公交、地铁、打车，最低费用到达，后续考虑疲劳和速度。

Project 中 ChatGPT 给出的架构/赛事解释是二手材料。“最晚出发”是对“最慢”的建议解释，尚未替用户定案。讨论中的票价、时间、地点均不作为真实服务数据。本仓库不复制整个私有聊天或其他会话内容。

用户于 2026-10-01 指定初赛演示：“40 分钟内到机场，预算 50，尽量便宜。”机场和货币需要由上下文补全。深圳是初始演示资料；用户随后要求解除城市等演示限制，并明确机场应由 Agent 自主判断，不能让模拟资料替代真实行程。用户已撤回仅操作手机既有应用、禁止直接接入服务的限制，提供本机服务配置，并授权开工。当前使用比赛官方工具链搭建可直接调用服务的 Navigation Agent，主 Agent 负责协调，有界工作委派给 GPT-6.1-Sol medium／low；授权范围与执行状态归[任务包](../tasks/capability-boundary/packet.md#目标与授权)。

用户进一步明确：应用模型使用 MiniMax M3；mock/demo 也要分别保留日历、笔记等来源，不能预先合成为一个行程背景文件。用户已要求创建本地 `.env`，由其填入高德、MiniMax 等配置；创建配置文件不代表接入或运行验证完成。

## 已知技术边界

原有 card-host 不提供 host services，继续用于隔离脚本检查。另行固定的 stock OctoSense desktop 已在 macOS arm64 构建并验证 `model.complete`、独立文件读取与真实地图请求；后续获授权的定位补丁另经真实 CoreLocation 请求验证。完整 Navigation 任务的验收归[任务包](../tasks/capability-boundary/packet.md)。手机与 Rinx 集成尚未验证。旧 AI-SERVICES.md 主要记录 2026-09-27 状态，不能据此断言较新官方宿主没有 Agent 服务。

2026-10-01 为机场演示复核了[初赛交付要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md#初赛需求成立作品能跑)与[按作品形态交付](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md#按作品形态交付)：需可运行原型、实际操作及可核验结果，并展示失败或空状态；提交形态与宿主、平台、依赖和启动说明需要匹配。桌面控制手机的实验不能自行当作已经验证赛事宿主集成。

2026-10-01 核对并运行了以下固定源码。新增宿主的版本与补丁摘要归 [agent-runtime.lock.json](../toolchain/agent-runtime.lock.json)，原 card-host 版本保持独立：

- [官方课程分工](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/curriculum.md#八个项目各自负责什么)：octos 是运行时内核，octoscode／OctoLoop 用于开发协作与审查；按选题组合项目，不要求接齐全部工具。
- [OctoSense Cargo.toml](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/Cargo.toml)：本次调查提交 d405d5c，配套 octos ae230ce 和 App Hub 58c3c8a，实施时必须沿用宿主兼容组合。
- [AI 宿主注册](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/ai-host/src/lib.rs)与[应用 peer](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/ai-host/src/contained.rs)：已注册 model 与 octos，当前 shipped 策略默认等待用户同意；不能照搬旧说明中默认关闭的状态。
- [脚本应用工具执行器](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/crates/shell/src/host_tools/script_apps.rs)和 [News 工具示例](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/news/bundle/tools.json)：读取经准入检查的 tools.json，host-service 工具走服务调用与结果队列；声明 implemented_by 为 app 不代表该执行器已经能执行脚本工具。该限制不禁止 OctoScript 自行调用脚本函数。此原生工具集成路径暂不作为初赛前置。
- [model.complete 参数与选择逻辑](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/ai-providers/host-service/src/complete/mod.rs)及[请求封装](https://github.com/OctoSense-org/OctoSense/blob/d405d5ca53012cb6bf606ed9323c68baf12c7ec6/apps/ai-providers/host-service/src/complete/wire.rs)：只接受 task、input、schema、class、allow_urls；拒绝额外字段。它按宿主提供方顺序与 fast／strong 分类选模型，可能尝试其他提供方；本项目隔离配置只允许 MiniMax-M3 且无 fallback。返回经 schema 校验的 JSON，没有原生工具调用或历史透传；应用侧 callback 循环已完成两轮真实调用与工具结果回传。该版本不透传 thinking／extra_body；input、schema 上限分别为 32、8 KiB，宿主服务等待上限为 60 秒。
- [当前锁定 SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/e08517254d9b2c316352eec4f959810d9ad22d40/docs/SCRIPT-API.md#network)记录 `net.http_request` 的 HTTPS 请求及 `fs` 的应用隔离存储访问。接口存在不等于模型凭据通道或多源文件导入已实现；网络主机声明及权限仍须满足。

## 0.2 应用联动调查

2026-10-03 对照固定 OctoSense `d405d5c` 与官方最新 `4a541777298eb4f85d9ac8ec2b83fab9e12ce909`。最新版本已经有 [Calendar 服务](https://github.com/OctoSense-org/OctoSense/blob/4a541777298eb4f85d9ac8ec2b83fab9e12ce909/apps/calendar/host-service/src/lib.rs)，但只接受 `os.calendar` 调用，工具没有跨应用共享声明；其 [脚本界面](https://github.com/OctoSense-org/OctoSense/blob/4a541777298eb4f85d9ac8ec2b83fab9e12ce909/apps/calendar/bundle/main.splash)仍是说明页。固定版本没有该 bundle，不能据此说整个生态没有 Calendar，也不能据新版服务存在就说 Navigation 已能读取日历。新版 [native-apps.json](https://github.com/OctoSense-org/OctoSense/blob/4a541777298eb4f85d9ac8ec2b83fab9e12ce909/native-apps.json)声明了 Reminders 原生模块与部分只读工具，当前 `app-hub` 构建未启用该原生 feature；只读声明不代表创建提醒已可用。本轮只读调查，没有升级产品工具链。

固定 Maps 的原生界面、Mail 的空账户页面和账户表单打开/取消已在无凭据的隔离实例实测；没有账户登录、邮件读取或真实导航。固定官方 Maps 本身没有跨应用选点回传契约；0.2 的本地窄桥已在隔离探针中验证，属于本仓库扩展。Mail 账户按调用 app 授权，`mail.message` 读取正文会将消息标为已读并尝试同步该标记，不能将它归为纯只读操作。

[高德静态地图](https://lbs.amap.com/api/webservice/guide/api/staticmaps)支持标记与折线；使用公开样例坐标和现有配置取得 PNG 后，已在固定 Makepad 的原生 `Image` 中以字节加载并查看。该证据分别证明服务结果与原生显示，不证明真实用户路线已接入地图，也不证明自由选点或跨应用联动。实验与方案归 [0.2 任务包](../tasks/interaction-integration/packet.md)。

2026-10-04 本地 Maps 扩展隔离验证了搜索结果选择、取消、关闭、非法调用方和旧票据；另用原 Maps 的真实 Photon 搜索输入“深圳宝安国际机场”，选中实际结果并将名称、WGS84 坐标返回原请求实例。公开搜索未读取设备定位或服务 Key；搜索探针底图未显示，不能把它视为瓦片渲染验收。回传源为 `octosense.maps.search`，不是高德 POI 或航站楼核验结果。最终覆盖版本以 `toolchain/agent-runtime.lock.json` 为准。

## MiniMax M3

应用模型由用户指定，不再是待选提供方。[MiniMax M3 官方页面](https://www.minimaxi.com/models/text/m3)使用模型标识 `MiniMax-M3`；[OpenAI 兼容接口文档](https://platform.minimax.cn/docs/api-reference/text-openai-api)列出该模型和函数工具支持，国内平台 Base URL 为 `https://api.minimax.cn/v1`。本机配置采用此地址，其他地区账户应使用所属平台的地址；不自行改为文档示例中的其他模型。

原生 Function Call 多轮需要按提供方协议回传完整 assistant 消息和工具结果。这个 API 能力不能直接等同于 `model.complete` 的能力；后者只暴露结构化单次调用。2026-10-01 的服务侧预检已验证返回模型均为 `MiniMax-M3`，并完成原生工具往返；随后 stock 官方宿主也通过了结构化动作、脚本读取独立随机值、模型继续回答的两轮探针。条件与后续应用验收归[任务包](../tasks/capability-boundary/packet.md)。

## 地图与交通服务

2026-10-01 已完成文档核对及带 Key 的隔离接口验证，地点、驾车、公共交通和步行查询均成功，条件与范围归[任务包](../tasks/capability-boundary/packet.md#服务预检证据)：

- [路径规划 2.0](https://lbs.amap.com/api/webservice/guide/api/newroute)列出公共交通、步行和驾车查询，以及时间、费用和出租车估价字段。实际深圳响应已出现公交候选中的 taxi 路段、换乘总费用与耗时；不能据此保证存在符合 40 分钟／50 元的混合方案。地图出租车估价不等于某网约车平台的实时可下单报价。
- [基础服务配额](https://lbs.amap.com/pages/base_service_price)按账户认证和服务类别区分，不能假定新建未认证账户即可调用全部接口；准备阶段需确认 Web 服务 Key 的相关权限和配额，不预先购买未确认需要的套餐。
- [地图 URI](https://lbs.amap.com/api/uri-api/guide/travel/route)按单一 mode 查询路线，不能据此承诺保留任意公交接打车方案；导航交接须分段处理或另行验证。

后续有限查询确认 `transits[].cost.transit_fee` 是完整候选总费用，混合方案不可再次加上 `taxi.price`；总耗时按官方定义包含等车，但没有独立证明出租车叫车等待。完整混合候选只能按供应商估计比较，全程驾车时长则不能冒充包含候车的出租车时长。2026-10-03 重新核对官方 v5 公交参数：`strategy=0/1/2/3/4/5/7/8` 分别为推荐、最经济、少换乘、少步行、舒适、不乘地铁、地铁优先与时间短；`6` 地铁图模式要求双方地铁站 POI ID，不能用于只有一般起终点坐标的请求。`AlternativeRoute` 大小写敏感，表示返回候选数。schema 中的策略语义需与接口版本一致，不能套用其它路线接口的编号。

机场查询还观察到 POI 吸附差异：`route.destination` 可能保留请求坐标，实际末段却停在地铁出口。不得仅靠该字段判断到达航站楼；必须核对实际末段 polyline 与任务终点，坐标匹配仍不证明楼层、安检或实际抵达。

2026-10-03 核对[搜索 POI](https://developer.amap.com/api/webservice/guide/api-advanced/search)与[路径规划 2.0](https://developer.amap.com/api/webservice/guide/api/newroute)：地点查询使用 `citylimit=false` 与 `extensions=all`，目的地城市来自 POI，公交请求使用独立的 `city1`／`city2` 及 `ad1`／`ad2`。逆地理编码的直辖市 `city` 可为空，只有北京、上海、天津、重庆可取其省级名称；不能一般性地把省名当作城市。深圳实测不证明其他城市均可返回路线，服务拒绝或信息不完整仍保留失败。

首轮演示背景分别使用日历文件、笔记和设备位置记录，由工具在运行时独立读取、关联并保留依据；不提供预合并的行程背景答案。这些模拟文件只证明多源上下文处理，不证明在线日历或笔记账户接入；默认设备定位另依下节宿主补丁读取。天气、提醒、在线日历及网约车实时报价服务是否增加，由演示必需能力和接口实测决定。

2026-10-03 核对[高德 POI 搜索](https://developer.amap.com/api/webservice/guide/api/search/)及[官方 POI 分类下载](https://developer.amap.com/api/webservice/download)：`city` 表示查询偏好，`citylimit=false` 不限制同城；`types=150104` 对应飞机场，`150105` 对应机场出发／到达，不能将整个 `150100` 大类当作机场。返回的 `typecode`、`parent` 和 `entr_location` 可用于核实 POI 类型、父子关系与供应商到达点，但不证明商业客运运营、正确航站楼或用户此次行程目的地。

同日一次实际广州偏好查询返回白云机场及其航站楼、沙湾机场、从化良口机场，类别均为 `150104`，且白云 T1 名称明示暂停营业。这个分类没有说明各机场是否提供公共客运。因此类型和距离只能帮助形成机场假设，不能当作已知机票事实。查询条件与安全结果归任务包引用的私有证据，不含用户精确定位或凭据。

## 设备定位接入依据

2026-10-02 核对官方 [location 能力](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md)及锁定运行时源码：grant 允许读取 `sys.gps`，但 macOS 的 Apple LocationUpdate 尚未接到正式应用，现有 GPS 缓存不含原始采样时间。实时定位需要本地宿主补丁，不把清单许可或接口示例当成已通过定位验收。具体补丁与验证归[当前任务](../tasks/capability-boundary/packet.md#实时定位接入)。

Apple 平台事件明确使用 WGS84，并携带系统采样时间与精度；路线请求不能直接把该坐标标为高德坐标。[高德坐标转换](https://developer.amap.com/api/webservice/guide/api/convert)支持 `coordsys=gps`，输入经度在前、纬度在后，最多六位小数；[逆地理编码](https://developer.amap.com/api/webservice/guide/api/georegeo)提供城市名称、编码和行政区信息，用于核实实际起点城市。原始设备样本及转换服务来源分别保留，不以转换完成时刻代替采样时间。

## 开发协作方法来源

[xiaoland/svc](https://github.com/xiaoland/svc) 本次采用版本为 Corpus 15.0.0，commit `4fe4c66ac4deb35209069c00b1bbdc1b22aae3af`。仅采用 `corpus/specs/` 的知识归属和 `corpus/task-packet/` 的任务控制语义，固定入口见 [知识导航](index.md)；未安装完整 CLI，也未引入其它模块。上游模板按需参考，项目说明与实际任务包由本仓库维护。

`../factory26/AGENTS.md` 是本轮用户指定的本地参考，读取于 2026-10-01。只借鉴知识回流、非简单任务的 packet、授权追溯和有界协作原则；其专属实验规则、模型与预算配置、自主提交授权和测试禁令不转移到本仓库。

## 打车询价与主动混合路线

2026-10-06核对[高德路径规划2.0](https://lbs.amap.com/api/webservice/guide/api/newroute)：驾车route.taxi_cost是元单位出租车估算，strategy=0只返回单路线；不是滴滴车型报价。使用公开深圳端点及当前key的实际响应核验多路径有route级估价、单路径同价，发现应用在多路径分支主动丢弃价格。实际证据和修复入口归[混合路线任务](../tasks/mixed-routing/packet.md)，不能从文档字段存在断言所有地点／请求均会有价。

[滴滴官方开发文档](https://mcp.didichuxing.com/api)提供正式MCP、个人账号激活key、地点查询及taxi_estimate。询价参数坐标来自maps_textsearch，价格来自structuredContent.items[].priceText（元）；生产与sandbox分开，后者Mock不能作实时报价。坐标系在该文档未声明，不能假定高德点可直接替代。当前只计划询价，不接创建／取消订单。接入验证需正式独立key，不能以高德key替代。

[腾讯出行MCP接入指南](https://tms-web-1g1czzwka2fd06f2-1301126013.ap-shanghai.app.tcloudbase.com/api/18-doc-mcp-guide.html)提供独立应用KEY及询价工具，是备选调查结果，尚未实现或验证腾讯报价。优先接滴滴，避免两套提供方适配在截止前重复建设。
