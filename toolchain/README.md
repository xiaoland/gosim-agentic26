# 固定的开发工具链

`sources.lock.json` 记录 2026-10-01 实际使用的五个上游 Git commit。
OctoScript-App-Design-Flow 的 `native-runtime.lock.json` 进一步锁定
Octoscript-Makepad，由该仓库固定 makepad 和 octoscript。

本次首次执行 `cargo build --locked` 时，上游 App Hub 的 Cargo.lock 与这组
path dependencies 不一致，Cargo 拒绝构建。按官方 QUICKSTART 的不带
`--locked` 的构建命令完成依赖解析后，将实际使用的锁文件保存在
`hub.Cargo.lock`。bootstrap 仅允许用它替换原始上游锁文件或相同的已有
锁文件；其他本地改动会被拒绝。随后使用 `--locked` 构建。

原 card-host 初始化没有修改上游 Rust 源码，也没有升级本机 Rust；正式 Navigation 的定位补丁见下文。初次验证环境为 macOS
arm64、rustc/cargo 1.93.0、Python 3.12.10（以 verification.md 实测为准）。
构建依赖遵从各自许可证；本仓库的 Apache-2.0 不重新许可外部依赖。

提供宿主模型服务的本地开发路径锁定在 `agent-runtime.lock.json`；Navigation 使用其中新增的 `model.chat` 覆盖，原有 `model.complete` 保持单次结构化调用。
它构建官方 OctoSense desktop 的 `app-hub` feature，关闭默认 features；
不需要构建 Octos 内核、Rinx 或 Terminal。原有 card-host 命令和版本保持独立。
初次完整编译约十分钟，改应用后的打包、增量编译和链接实测约一分钟。

在本机配置 `.env` 中的 `MINIMAX_API_KEY`、`MINIMAX_BASE_URL=https://api.minimax.cn/v1`、
`MINIMAX_MODEL=MiniMax-M3` 和 `AMAP_API_KEY` 后执行：

```sh
make agent-bootstrap
make agent-doctor
make agent-init-demo
make agent-dev
```

`agent-bootstrap` 默认在仓库同级 `.octosense-agentic26-host-bridge/` 准备固定源码，
按锁文件验证 RC6 官方源码和 Navigation 两份必要补丁，使用官方 `tools/setup.py --no-hub` 应用完整锁定运行时栈，并执行 `cargo +1.99.0 build --locked`。先安装锁定Rust版本；命令不会修改全局默认工具链。
可用 `AGENTIC26_AGENT_TOOLCHAIN` 指定另一隔离目录。启动器拒绝版本或源码摘要不符，
不会覆盖旧工具链或个人全局模型配置。

应用通过官方 `OCTOSENSE_SYSTEM_APPS` 编译进宿主。启动前复制当前 `bundle/` 到
忽略的 `build/agent/`，仅在这份副本中为 id 加 `os.` 前缀以进入 shell 的应用列表，并嵌入固定 Maps 与 Mail 官方 bundle，
由官方 packer 重新盖摘要。每次启动都增量构建，并核对生成包与当前源码；
因此编辑 `main.splash` 后需重新执行 `agent-dev` 或 `agent-hidden`。
输出和 `build/agent/build.json` 记录源码 SHA-256 与实际包的 BLAKE3，避免误用旧内嵌界面。
这条路径是本地开发加载方式；正式外部安装仍走官方签名 catalog。

`agent-init-demo` 明确重置三份互相独立的模拟来源，将模板时间替换为当前东八区时间，
航班设为两小时后；`agent-dev` 和 `agent-hidden` 保留已编辑的日历与笔记，默认位置模式为 live；`make agent-demo` 明确使用模拟位置，模拟位置过期需重新 `agent-init-demo`。
私有数据在 `.local-state/agent/`：官方宿主的 `octos/profiles/_main.json` 保存单个 MiniMax-M3 provider、地址与密钥，fallbacks 为空；应用 jail 内的 `private-config.json` 只保留高德、可选滴滴 key、位置模式与开发诊断配置，不再提供模型鉴权或选路配置；开发诊断元数据仍记录模型名称。目录为0700，私有文件为0600，均不进入包、Git或启动参数。

应用调用 `host.request("model.chat", ...)`，提交完整 messages、tools、`tool_choice: "auto"` 和 `reasoning_split: true`，省略 thinking 使用 M3 默认自适应思考。宿主也接受显式 adaptive／disabled，不再强制关闭思考。宿主返回原始 provider response 和 usage／budget 元数据；应用继续保存 assistant/tool 历史与执行工具。`model.chat` 的桥接等待为现有 HTTP 120秒超时加10秒收尾，共130秒；不会在网络请求仍有效时提前用通用60秒期限丢弃回执。其它方法的等待期限不变，不自动重试。该接口由 `octosense-navigation-rc6.patch` 提供，是待上游接纳的本地扩展；官方 `model.complete` 不支持原生工具调用或历史，不能用 JSON 动作模拟替代。

聊天扩展复用同一 ModelHost、主提供方凭据、HTTP transport、授权和 ledger。它只使用实际 primary，主项未配置或缺 key 时直接失败，不挑选 fallback；当前支持 OpenAI 兼容协议。完整消息不裁剪，不附加 one-shot 的结构化输出提示或 URL 拒绝规则。`host.request`与App Hub pump的两道参数门仅对`model.chat`允许编码后JSON参数最多2MiB，包含完整messages/tools，宿主追加model/stream前计数；其它服务仍为1MiB。原队列每VM4MiB／全局16MiB、HTTP响应1MiB、脚本执行／内存和服务等待边界保持。超过容量或循环JSON在入队前拒绝，不调用供应商。取消查询会屏蔽迟到回调，不保证远端HTTP已经中止或停止计费。 `model.chat`失败时，宿主私有日志保留既有已脱敏错误摘要及app／isolate／原request_id／chat_result阶段，公开错误仍是通用拒绝，不暴露供应商响应或key、不自动重试。App Hub实现由锁定的本地补丁及四个Cargo path覆盖实际链接；app-contract仍来自同一固定发行SHA。fragment验证只对代码态首个转义引号报告 `unexpected escaped quote outside string` 及行列，字符串／注释和普通流式tokenizer语义不变，不自动修正生成稿。

开发启动器仅给隔离 Navigation 应用写入显式 `unlimited:true` 配置，取消本机每分钟、每日调用及 token 预算准入，继续累计真实调用和 token 使用量，保留其它应用设置与宿主全局默认值。budget 回执标记 unlimited，额度及剩余额度字段为 null。此开发偏好不会取消供应商限流、网络超时或消息容量边界，应用也不能自行更改宿主配置。

模型配置仍固定 MiniMax-M3 与 `https://api.minimax.cn/v1`，启动器验证地址、模型与单一主提供方。M3出网和Authorization归宿主；应用manifest只声明高德与滴滴网络主机，并在锁定版本申请model能力。`DIDI_MCP_KEY` 来自正式个人MCP账号，缺省不阻断高德查询；应用仅调用地点搜索与询价，不下单。高德和滴滴key留在应用私有配置，模型key只留在宿主profile。
本轮撤掉应用自行添加的输入／输出、工具步数、自动阶段和纠正次数上限，直接生成 Splash 界面；宿主和服务端的实际能力及错误以运行结果为准。
技能包归`bundle/assets/skills/`，每个技能使用独立目录与`SKILL.md`。打包和启动时从frontmatter生成`catalog.json`，按原目录递归复制引用资料到私有jail；初始模型消息只载入名称和描述，正文由`read_skill`按需取得。上游来源、固定revision与文件摘要归[技能锁文件](skills.lock.json)，不在开发启动时下载技能。
技能读取依赖本地覆盖的 `fs.read_async(path, callback)`，由 `agent-runtime.lock.json` 的 `navigation_overlay` 固定 Makepad 与 OctoSense 补丁。文件读取及需要磁盘的 jail 路径校验在后台线程，结果回原 VM 的 UI 调度，返回 `{success, text, error}`；原同步 `fs.read` 保持原样，不放宽脚本预算。应用异步取得并缓存目录，正文和引用资料仍按需读取，回执绑定查询与工具调用。它是待上游接纳的本地扩展，官方未补丁宿主不能冒称支持。debug 环境的 `MAKEPAD_TEST_ASYNC_READ_DELAY_MS` 仅用于离线慢读取判别，正式验收与启动不设置；同一锁定覆盖提供 `String.utf8_chunks(max_bytes)`，仅按UTF8边界切分文本；`String.utf8_chunk(offset,max_bytes)`只返回一个片，offset为非负整数UTF8字节偏移并必须落在有效边界，max_bytes为至少4的有限整数，末尾offset返回空串。下一偏移使用offset加片的`len()`（UTF8字节数）。分timer写入可避免`utf8_chunks`一次复制全部片；供完整出行JSON分片保存，不改变文件容量、脚本预算或内存计费。同步诊断写入不因此变成异步。

本地 `navigation_overlay` 提供 `start_timeout_checked(delay, work, on_error)`。它只捕获该 work 入口未处理的 VM 硬错误，在下一个独立 timer 交付错误；普通 timer、主动捕获的异常及子界面的预期语法诊断保持原行为。应用以明确的 run／call／job 或模型请求记录归属结算，不读取全局日志猜错误来源，不自动重试、不提高执行预算。供应商失败时的完整响应与处理阶段仅保存在私有诊断分片中，不传给模型；该接口由锁文件固定的 Makepad 与 OctoSense 补丁提供，官方无补丁宿主不支持。

普通查询仍独立运行，不恢复模型会话，也不进行问题澄清。出行列表保存查询结果的历史界面、路线事实及用户确认后的守护状态；冷启动和切换只读展示，主动规划或核验重新建立模型会话。正常live不依赖模拟来源初始化；demo文件只在显式演示模式使用。启动器配置、已打包技能及宿主调试记录不作为业务恢复入口。
应用必须捕获网络派发失败并使用通用错误，不能把 key、含 key 的 URL、原始网络错误、
私有配置写入 UI、日志、模型输入或验收记录。显式开启的开发 trace 可保留移除凭据后的模型响应全文，原始记录只保存在私有忽略目录。

`agent-hidden` 隐藏窗口；两种启动都会先关闭此启动器的旧实例，使用独立数据和随机
localhost 端口。`.local-state/agent/session.json` 记录 PID、端口、进程起始标记、jail 和源码摘要。
`agent-status`、`agent-tree`、`agent-logs`、`agent-shot` 使用官方远程接口；
开发诊断以分段JSONL追加；超过单文件限制的事件完整分为私有UTF8文本片，JSONL引用仅在片写完后发布。读取校验片顺序、长度与事件身份后还原原事件，缺片明确报告不完整，同时兼容小事件和旧事件JSON。新启动在原宿主停止后将旧诊断完整迁到私有 `build/traces/archives/`，避免耗尽应用存储条目；存在活跃私有宿主时不迁出。显式指定历史session／instance可读取唯一对应归档，当前选择不采用归档。检查入口为 `python3 tools/test_agent_trace.py`，原生展示与追加行为仍由 `tools/smoke.py` 检查。

日志和树输出会先检查精确凭据。截图是实际运行的 PNG。`agent-stop` 在核对 PID、
进程起始标记与远程 `/s` 后请求 `/quit`，只管理它自己启动的实例。
调试时可在记录的端口访问 `/snap?all=1`、`/click?x=…&y=…&wait=1`、`/t?t=…`；
`/d`、`/log?n=1000` 和 `/g?raw=1` 分别返回树、日志和 PNG。

`agent-doctor` 检查版本、配置和打包边界，不发起账户请求，也不替代真实应用验收。
出行列表、历史详情、迁移与跨记录隔离回归使用 `python3 tools/smoke.py --trips`；使用已有私有真实结果回放时，以 `NAV_TRIP_REPLAY_STATE` 指定数据目录并运行 `python3 tools/smoke.py --trips-replay`，不会调用模型，测试地图配置不代表真实供图；守护状态与原生点击回归使用 `python3 tools/smoke.py --guardian`，在隔离数据中运行合成路线，覆盖确认、替代、版本、费用、恢复及删除；这不替代真实M3／高德核验。出行数据保存在 jail 的 `navigation-trips.json`、`navigation-trips.previous.json` 和各条 `navigation-trip-<id>-<revision>.json`；旧 `guardian-goal.json` 与备份只用于首次迁移。关闭实例后删除整个开发 state 会一并删除这些业务数据。
固定官方宿主已实测 M3 两次回调：先选读文件工具，再回传请求后独立读取的随机 nonce；
高德真实参数失败与网络策略拒绝均未在 host log、远程 log、snapshot 或 tree 中出现精确 key。
历史 Navigation 曾完成 M3 七轮约 21 秒、在线公共交通选择、确认保存读回及 stock 重启恢复；该基线没有混合候选；补充真实任务以七轮约 30 秒完成 ¥19／2063 秒的打车接地铁方案确认读回。完整条件、失败状态与源码版本对应关系见任务包，不以模型探针代替业务证据。

## 官方原版首屏与宿主扩展边界

2026-10-10 使用官方 App Hub `7b36c8afc2e4bad9dfa5d77692b6fd453f0b9785` 的未修改 `card-host` 验证首屏。原稿启动时直接调用该宿主未提供的 `ui.content.rect()`，即使外层有 `try` 也会触发 Makepad VM 空栈错误。应用现在先区分已验证的 Navigation 扩展宿主；原版不调用缺失方法，不启动查询或生成区块轮询，而是显示具体能力缺失说明。

这里通过 `AutoNaviMapView` 类型注册识别本项目已验证的扩展组合，不将一个类型的存在当成所有未来宿主的通用能力保证。官方 `card-host` 使用390×844手机视口，既不是Android模式，也不是Android真机。能渲染首屏只证明降级路径成立，不证明它能够定位、查询模型或完成路线规划。

正式 Navigation 已采用官方桌面 RC6（`desktop-v0.1.0-rc.6`），精确源码与依赖归 `agent-runtime.lock.json`。构建与 Hub CLI 显式选择锁定 Rust 1.99.0；doctor 检查该版本，缺少时明确失败，不使用全局默认替代。旧 card-host 隔离工具链不随此次升级改变。

| 能力 | RC6 归属 |
| --- | --- |
| 区块寻址、布局测量、渲染诊断、地图视口 | 两份 `navigation-rc6.patch` 中的本地扩展，官方原版仍未提供。 |
| 模型工具调用 | 同一 ModelHost 的本地 model.chat，复用凭据、授权和账本，保留130秒期限。 |
| 异步脚本读与受检计时器 | 本地扩展；保留新版 callback 权限提示来源，不提高脚本预算。 |
| 实时定位 | 使用官方 permission.request／sample／sample.cancel，不再应用旧 macOS location.get 补丁。 |
| 字体许可文档与 Replier 存活检查 | RC6 上游已包含相应处理，不再应用旧覆盖。 |

两份补丁与完整官方 Makepad patch 栈的精确树和摘要由 lock 校验。未知工具链修改仍拒绝构建；源码补丁不进入 bundle，也不能把本地扩展通过表述为官方原版安装兼容。

model.chat的非流式HTTP等待为300秒，外层服务等待310秒；普通模型complete及其它原有HTTP路径仍使用120秒。等待延长不新增重试或fallback，也不代表远端取消或保证完成。

## Notes 共享工具调用桥

Navigation 的本地 `shared_tools.call({request_id,tool,args})` 只开放 `notes.search` 与 `notes.read`；`request_id` 是应用为本次调用生成的非空字符串，最长64字节，不能用 host.request 返回的数字ID替代。`shared_tools.cancel({request_id})` 只取消同应用、当前账户及同一isolate的调用，返回cancelled数量。重复待处理ID明确失败，isolate关闭、超时或账户／admission改变会取消官方relay调用；迟到结果不进入应用。

调用身份来自ServiceCall，账户来自宿主contained_account，owner和risk来自官方Catalog，脚本不能提交caller、account、grant或风险字段。宿主仅为本项目system-app os.agentic26-navigation登记两项官方tool offer，使声明通过admission；这不授予工具或consent。manifest的agent.tools通过官方安装流程取得工具grant，relay继续裁决consent、参数schema、审计和既有工具预算。此预算独立于已设unlimited的M3账本；桥没有新增项目限制，也没有删掉官方跨应用策略。

成功的host回执data保留官方AI bus的 `{text,note,data}`；内层data才是搜索 `{total,truncated,hits}` 或单篇笔记字段。失败保留官方kind与message。宿主构建需app-notes；Notes必须是用户已打开的原生实例，关闭时应返回app_not_running，桥不会后台创建它或读取其存储。该桥是本项目扩展，不能称作官方notes.read host API；真实账户／授权和业务背景验收仍须实际验证。

## 官方实时定位

应用声明 host-api-v1，先由真实前台操作调用 `location.permission.request({})`，获准后调用 `location.sample`。参数为 timeout_ms（默认10000，1..30000）、max_age_ms（默认5000，1..60000）及可选 max_accuracy_m（>0且<=100000）。成功数据直接包含 latitude、longitude、accuracy_m、timestamp（Unix秒）、age_ms、source:"platform"、freshness:"fresh"，没有旧 success/lat/lon 包装。WGS84→GCJ02转换留在应用；取消使用 `location.sample.cancel({})`。系统授权仍由用户实际选择，升级离线探针没有申请权限或采样。

默认 `agent-dev`／`agent-hidden` 使用真实位置；启动器清除假 GPS 注入环境。`agent-demo` 明确使用演示位置，不是实时定位失败后的自动兜底。真实位置来自有权限的前台应用一次请求，宿主取消、关闭或切换应用后停止采集；当前前台判断指宿主内部选中应用，不等于已验证系统窗口失焦策略。系统授权由用户选择，不能由启动器修改 macOS 定位权限；超时、拒绝与取消按官方服务回执处理，不沿用旧覆层的15秒采样计时约定。

正式启动器将已锁定构建复制到隔离目录的 `OctoSense Navigation.app/Contents/MacOS/octosense`，补齐 executable、package type 与用途 plist，直接执行包内二进制。定位与日历的新旧用途说明均从锁定的 `desktop/packaging/macos/Info.plist` 读取；不能只复制 profile 级 sidecar，它可能缺少日历字段或被其它包覆盖。`agent-dev`、`agent-hidden` 和 demo 共用这条包装路径。该启动方式已观察到系统定位授权和真实样本；`open` 的 LaunchServices 启动仍未验证成功，本地包装不含签名或发布承诺。

## 官方 Maps 与包检查

Navigation 当前没有 maps.pick 消费者，RC6 不移植旧选点模式；Maps、Mail 使用锁定官方 App Hub 源码原包。Navigation、Maps 和 Mail 的实际编译产物均逐文件核对。保留官方入口不代表 Navigation 获得其中的账户权限。

`make check` 使用同一固定Rust构建 Hub CLI，再调用固定 harness 完成摘要、验证与预检；应用脚本仍在 bundle，宿主扩展只供可复现本地运行。

## Navigation 字体资源与文档 gate

Navigation Sans CN 的字体、完整 OFL 原文与复现说明一起放在 `bundle/assets/fonts/`，由既有 `{{assets}}` 本地资源服务加载；不安装系统字体、不修改宿主主题，也不增加外部字体主机。正式 gate 允许 OTF/TTF，整包上限仍为 8 MiB；最终脚本、字体与截图都计入该限制。

RC6 官方 gate 已将普通字体许可文档与资源加载区分，不再维护本地 font_document_overlay。完整许可和来源说明继续随字体打包，远端资源仍须满足清单主机策略。

正式构建将 `MAKEPAD_BUNDLE_NAME=OctoSense` 与 `MAKEPAD_BUNDLE_IDENTIFIER=dev.makepad.octosense` 明确传给官方 Makepad build script。默认身份原本由 target 的父目录推断，在隔离工具链目录中会生成另一个 bundle ID；显式固定构建身份，并在本机 `.app` 包装时按固定 OctoSense 配置设置 bundle ID、名称及 executable。Makepad 的 profile 级 Info.plist 可能被同 target 的另一个包构建覆盖，Cargo 缓存未必重新生成它，因此本机包装不从该共享副产物继承应用身份。用途说明从锁定官方打包模板合并定位与日历四个字段，不从共享副产物继承。RC6 EventKit 按系统接口分别检查 `NSCalendarsFullAccessUsageDescription` 或 `NSCalendarsUsageDescription`；两者缺失会返回 `host_not_configured`，即使宿主已在 `.app` 内运行。包装声明不授予系统许可，不修改系统定位或日历权限。`make check` 使用同一环境构建 Hub CLI，避免共享 target 的 plist 被另一个默认目录身份覆盖。

## Android 模式验收

后续交互与演示验收默认使用锁定 macOS 宿主的 Android 手机模式。`make agent-dev` 启动后，在顶栏当前样式菜单 `OctoSense ▾` 选择 `Android`；官方 smoke 也通过 `⌘Space`、输入 `android`、回车切换，日志 `wm: desktop style android applied` 确认应用。当前启动器没有 Android 模式参数，macOS 默认样式仍为 OctoSense，因此每次验收启动后明确切换，不依赖未经确认的持久化。

该模式提供手机视口与应用布局，用于检查滚动、按钮、输入和 Maps 往返；报告记录“macOS 宿主 Android 模式”。它与 Android 设备／APK 的系统权限及服务运行验证分别记录。此前桌面模式截图保留为历史证据，后续截图使用 Android 模式。具体运行证据与源码版本在对应任务包单独记录。


## 原生控件的动态查找与几何

正式运行时增加 `ui.find(name)`，字符串名称与既有 `ui.name` 共用同一查找实现。隔离 Splash 的查找始终限于自己的脚本根，不搜索其它应用；它不接受路径、源码或业务调用。`ui[name]` 在锁定解释器中不能索引 UI handle，不能将它当作动态查找 API。`ui.child(index)` 返回当前控件的直接原生子实例句柄，index 从 0 开始；不递归搜索，也不依赖动态名字。低层树可以按自己的准确渲染顺序递归取句柄，再将业务 node.id 绑定在应用对象中。多 Image 可通过这种独立实例句柄调用既有 `load_image_from_data_async(bytes)`，每次加载仍须由应用核验实例、目标与 generation；销毁后不得按旧名称给新图加载旧响应。

`ui.find(name).rect()` 或实例句柄的 `rect()` 只读该控件最近一帧已经绘制、裁剪后的 `{x,y,width,height}`，坐标为宿主布局点。未绘制时返回 `nil`，应用需等待绘制再读取，重新布局或图片尺寸改变后也要在新帧读取，不能猜测窗口尺寸。模型得到的是应用选择提供的几何事实，不获得窗口操作或其它应用句柄。这个接口不执行生成代码、不引入嵌套 VM 或沙箱。

`agent-runtime.lock.json` 的 `navigation_overlay` 固定宿主与 Makepad 两份RC6增量补丁，保留完整官方运行时栈。wrapper 校验补丁字节、上游版本和最终树；未知修改仍拒绝，不改其它应用权限或主题。

## 生成界面的执行诊断

`Splash.diagnostics()` 首次调用启用该实例后续诊断，因此父应用在 `set_text` 前调用它。接口返回最近收集的原始诊断字符串，重复读取不消耗；每次 `set_text` 清除旧稿诊断，空串停止子实例，捕获启用状态留给下一稿。已被日志排出的历史错误无法补回。只有调用接口的实例启用捕获，其日志通过 tee 保留；其它 Splash 默认行为不变。

脚本 `try` 主动捕获的异常仍按原 VM 清除，接口不会恢复它。原生 `on_render` 的属性类型错误已有实际证据返回 `expected DrawQuad, got object`，使应用能向 M3 反馈具体执行结果。这个接口属于现有 UI overlay，补丁摘要和 runtime tree 由锁文件管理，不是读取全局日志或新增界面校验。

历史页面恢复会重新设置 Splash 源码。配套 Makepad 覆盖使用安全的字符串前缀读取比较新旧源码；旧字节长度落在新稿中文字符中间时按全文变化重新解析，避免增量比较在解析前崩溃，不改写生成稿。具体版本和补丁摘要由 `agent-runtime.lock.json` 维护。

`ui.validate_fragment(source)` 复用 Makepad 词法器，返回片段的词法收尾与括号结构错误；空串只表示这些结构完整，不证明语法或运行成功。Navigation 在把 Agent 的 source 拼入事实与事件桥接上下文之前调用它，防止多余闭括号逃出界面壳却没有诊断。批量或整稿提交失败时，原区块源码、修订与地图保持，错误按实际区块 ID 返回原工具调用，让同一个 Agent 循环修稿；之后正常挂载仍读取 `Splash.diagnostics()`。该接口不执行片段、不限制业务布局，也不改变全局流式解析行为，属于本仓库锁定覆盖，官方原版尚未提供。

## AutoNaviMapView 原生视口

UI overlay还导出AutoNaviMapView原型，复用Image纹理而保留普通Image行为。fit_bounds、set_camera、zoom_by、load_map_image与on_camera_changed管理GCJ02相机及当前图片；控件不持有候选ID或凭据。应用继续通过官方net接口请求高德视口图片，原生提供单指拖动、双击缩放，页面可调用zoom_by。当前未实现双指捏合，不是连续瓦片地图。

该覆盖与脚本原型导出都由agent-runtime.lock.json及现有UI patch摘要／tree锁定。新checkout按锁定顺序重建，现有工具链需重新运行agent-dev／agent-hidden，不使用旧二进制冒充新接口。供应商scale=1图片按真实标记验证512像素Mercator基准；原生相机请求会使旧解码key失效，纹理安装只接受当前key。实际接口、手势和图片位移证据见[交互地图任务](../tasks/interactive-map/packet.md)，本机Android模式不代表Android真机。此类型是本仓库覆盖，不能宣称stock宿主已有该接口。


## 数据与隐私

Navigation 将用户本次输入、取得的位置与必要的路线及背景事实发送给 MiniMax，用于决定查询、比较与生成界面。高德收到定位转换、地点检索、路线规划和地图视口所需的坐标及参数；启用滴滴询价时，滴滴收到地点搜索与报价所需的出行参数。应用仅询价，不创建打车订单。新版已接入系统日历和 Notes 读取适配器，系统许可及 Notes 官方共享授权仍由宿主管理；本轮仅验证未授权拒绝和隔离合成资料，尚未完成真实个人背景验收。邮件账户仍未接入。显式 demo 使用独立模拟资料，仍调用真实模型与交通服务。

每条出行的输入、历史界面与路线事实，以及确认后的目标、确认记录与已花费用保存在本应用私有 jail；核验时必要业务事实会提供给模型，模型对话及未确认提案不恢复。应用内可结束或删除目标，也可删除整条出行；没有后台持续监控。本地开发启动器默认开启诊断记录。记录可能包含完整输入、位置、背景资料、模型消息、工具结果与生成源码，保存在忽略的私有目录，供本机排障；`python3 tools/agent.py dev --no-trace` 可关闭应用 trace。停止自有实例后，可自行删除不再需要的 `.local-state/agent/` 和 `build/traces/` 中记录；其它实验日志也可能位于 `build/`。API 密钥保存在本机配置，仅用于对应服务认证，不作为模型背景或界面内容。

第三方服务的数据保留与处理遵循各自条款，本应用不保证第三方立即删除请求。问题反馈使用仓库 Issues；提交前应去除密钥、精确位置和个人背景，不公开原始 trace。当前没有独立的开发者遥测或应用自建数据服务器。

RC6 的脚本私有存储仍在 `apps/<runtime app id>`，模型账本仍在 `apps/.host/model/ledger.json`；新增账户目录不改变 Navigation 的 `fs.*` 根。因此不移动既有配置、出行记录或 trace。默认开发 home 与独立实验 state 各自持有账本，启动实验时应继承对应 state 的账本；`unlimited` 仅取消本机 Navigation 的模型准入上限，保留实际使用计数与其它应用的官方策略。

独立官方 `hub check` 没有 Navigation 宿主的 Notes 工具 offer；当前含 Notes 声明的包因此会得到准确拒绝，不能把原生扩展宿主的通过当作 stock 或商店 gate 通过。`make check` 保留官方 harness 的盖摘要和其它预检，经配套宿主 `--navigation-check` 复用官方 `check_bundle`，只为 Navigation 提供与运行时共享的两项 Notes 声明。普通资源、签名、listing、内容及摘要规则不放宽，其它应用不接受该入口。`python3 tools/test_agent_project_gate.py` 验证正常包接受、未提供工具拒绝、其它应用不能借用声明及损坏摘要拒绝。`agent-doctor` 核定当前扩展宿主、源码、依赖、打包与凭据边界，不代替发布准入或真实个人许可。
