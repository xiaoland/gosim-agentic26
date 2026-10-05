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

支持 `model.complete` 的本地开发路径另外锁定在 `agent-runtime.lock.json`。
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
按定位覆盖、Maps 覆盖、控件接口覆盖及字体文档 gate 覆盖的顺序验证源码树，再使用官方 `tools/setup.py --no-hub` 应用已锁定的运行时补丁并执行 `cargo build --locked`。
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
私有数据在 `.local-state/agent/`：官方宿主的 `octos/profiles/_main.json` 保留单个 M3 provider，
兼容 `model.complete` 探针；当前应用通过 stock `net.http_request` 直接调用 M3 和高德。
仅这个应用的 jail 内 `private-config.json` 提供 `amap_api_key`、`minimax_api_key`、
`minimax_base_url`、`minimax_model` 与 `location_mode` 运行时字段。
目录权限为 0700、这两个文件为 0600；两份配置不进入应用包、Git 或启动参数。
模型配置固定一个 MiniMax-M3 provider，fallbacks 为空；其它模型配置会被拒绝。
M3 地址只允许已实测的 `api.minimax.cn` HTTPS 主机、默认或 443 端口和 `/v1` 路径，
不接受 URL 账号、查询参数或片段；启动器将尾斜杠和显式 443 规范为上述 Base URL。
应用请求固定 `/v1/chat/completions`，用 Authorization header 传 key，并关闭 thinking；
应用清单仍须声明这个 HTTPS 主机，应用本身也须核对私有配置中的模型和地址。
两家 key 对应用运行时可见，费用、时效及路线是否满足用户条件由应用计算。
本轮撤掉应用自行添加的输入／输出、工具步数、自动阶段和纠正次数上限，直接生成 Splash 界面；宿主和服务端的实际能力及错误以运行结果为准。
当前应用按独立查询运行，不保存或恢复Trip、用户历史与模型会话，不进行问题澄清。正常live不依赖模拟来源初始化；demo文件只在显式演示模式使用。启动器配置、已打包技能及宿主调试记录不作为业务恢复入口。
应用必须捕获网络派发失败并使用通用错误，不能把 key、含 key 的 URL、原始网络错误、
私有配置写入 UI、日志、模型输入或验收记录。显式开启的开发 trace 可保留移除凭据后的模型响应全文，原始记录只保存在私有忽略目录。

`agent-hidden` 隐藏窗口；两种启动都会先关闭此启动器的旧实例，使用独立数据和随机
localhost 端口。`.local-state/agent/session.json` 记录 PID、端口、进程起始标记、jail 和源码摘要。
`agent-status`、`agent-tree`、`agent-logs`、`agent-shot` 使用官方远程接口；
日志和树输出会先检查精确凭据。截图是实际运行的 PNG。`agent-stop` 在核对 PID、
进程起始标记与远程 `/s` 后请求 `/quit`，只管理它自己启动的实例。
调试时可在记录的端口访问 `/snap?all=1`、`/click?x=…&y=…&wait=1`、`/t?t=…`；
`/d`、`/log?n=1000` 和 `/g?raw=1` 分别返回树、日志和 PNG。

`agent-doctor` 检查版本、配置和打包边界，不发起账户请求，也不替代真实应用验收。
固定官方宿主已实测 M3 两次回调：先选读文件工具，再回传请求后独立读取的随机 nonce；
高德真实参数失败与网络策略拒绝均未在 host log、远程 log、snapshot 或 tree 中出现精确 key。
历史 Navigation 曾完成 M3 七轮约 21 秒、在线公共交通选择、确认保存读回及 stock 重启恢复；该基线没有混合候选；补充真实任务以七轮约 30 秒完成 ¥19／2063 秒的打车接地铁方案确认读回。完整条件、失败状态与源码版本对应关系见任务包，不以模型探针代替业务证据。

## 实时定位宿主补丁

用户已批准在固定官方源码上补齐 macOS CoreLocation 的一次性 `location.get` 服务。补丁保存在 `toolchain/patches/`，基版本、补丁 SHA、应用后的 Git tree 与 Cargo.lock 摘要均由 `agent-runtime.lock.json` 校验；未知工具链修改不自动 reset，也不以放宽 dirty 检查来接受。应用源码仍只在 `bundle/`，Rust 补丁不进入应用包；需要这组宿主补丁的实时定位功能不能宣称在未修改的 stock 宿主已可用。

默认 `agent-dev`／`agent-hidden` 使用真实位置；启动器清除假 GPS 注入环境。`agent-demo` 明确使用演示位置，不是实时定位失败后的自动兜底。真实位置来自有权限的前台应用一次请求，宿主取消、关闭或切换应用后停止采集；当前前台判断指宿主内部选中应用，不等于已验证系统窗口失焦策略。系统授权由用户选择，不能由启动器修改 macOS 定位权限。宿主先等待匹配的系统权限结果，获权后再开始15秒采样；授权等待不消耗采样或registry请求时钟，且与已有sheet暂停原因独立。拒绝、取消和迟到授权不会启动已结束的请求。此计时修复已通过隔离回调检查，未重置系统权限来重测首次真实弹窗。

正式启动器将已锁定构建复制到隔离目录的 `OctoSense Navigation.app/Contents/MacOS/octosense`，补齐 executable、package type 与定位用途 plist，直接执行包内二进制。该启动方式已观察到系统定位授权和真实样本；`open` 的 LaunchServices 启动仍未验证成功，本地包装不含签名或发布承诺。

## Maps 选点覆盖与包检查

`agent-runtime.lock.json` 的 maps_overlays 记录定位基树、增量 patch 摘要、最终源码树和锁文件。原定位 patch 保持独立；bootstrap 可以接续已应用的完整组合，未知修改仍拒绝。Maps 选择模式修改也属于受校验的覆盖，暂存包须与该固定源码一致，不将其称为未修改的官方 Maps。Navigation、Maps 和 Mail 的实际编译产物都逐文件核对；Mail 保留官方入口不表示 Navigation 获得邮箱账户权限。

Maps 能力的同版本 app-contract 通过本地 path patch 进入实际权限策略，Cargo.lock 同步锁定。`make check` 构建同一组合的 Hub CLI，再调用固定 OctoScript-App-Design-Flow harness 完成摘要、验证与预检；无需扩展旧 card-host 的闭名单。应用脚本仍在 bundle，宿主覆盖仅供可复现本地运行，不能把这组 Rust 代码当作初赛 OctoScript 应用包。

## Navigation 字体资源与文档 gate

Navigation Sans CN 的字体、完整 OFL 原文与复现说明一起放在 `bundle/assets/fonts/`，由既有 `{{assets}}` 本地资源服务加载；不安装系统字体、不修改宿主主题，也不增加外部字体主机。正式 gate 允许 OTF/TTF，整包上限仍为 8 MiB；最终脚本、字体与截图都计入该限制。

固定 Hub 的原检查将字体版权及来源文档里的普通 URL 当作资源加载而拒绝。`agent-runtime.lock.json` 的 font_document_overlay 锁定一条叠加于 Maps Hub tree 的独立补丁，保留原 Maps 与定位补丁字节。该补丁仅识别 `assets/fonts/` 中伴随实际 `.otf`／`.ttf` 的 `OFL.txt`、`LICENSE.txt`、`LICENSE.md` 与 `README.md`。执行脚本与 Agent 文件继续走原检查；带 HTML、Markdown 图片、CSS 资源或远端 `http_resource` 引用的文档也继续受原检查。普通版权／来源链接与本地 `http_resource("{{assets}}/…")` 示例可以保留，未知远端字体资源仍不能绕过清单主机限制。

正式构建将 `MAKEPAD_BUNDLE_NAME=OctoSense` 与 `MAKEPAD_BUNDLE_IDENTIFIER=dev.makepad.octosense` 明确传给官方 Makepad build script。默认身份原本由 target 的父目录推断，在隔离工具链目录中会生成另一个 bundle ID；显式固定构建身份，并在本机 `.app` 包装时按固定 OctoSense 配置设置 bundle ID、名称及 executable。Makepad 的 profile 级 Info.plist 可能被同 target 的另一个包构建覆盖，Cargo 缓存未必重新生成它，因此本机包装不从该共享副产物继承应用身份。用途说明仍来自官方模板，不修改系统定位权限。`make check` 使用同一环境构建 Hub CLI，避免共享 target 的 plist 被另一个默认目录身份覆盖。

## Android 模式验收

后续交互与演示验收默认使用锁定 macOS 宿主的 Android 手机模式。`make agent-dev` 启动后，在顶栏当前样式菜单 `OctoSense ▾` 选择 `Android`；官方 smoke 也通过 `⌘Space`、输入 `android`、回车切换，日志 `wm: desktop style android applied` 确认应用。当前启动器没有 Android 模式参数，macOS 默认样式仍为 OctoSense，因此每次验收启动后明确切换，不依赖未经确认的持久化。

该模式提供手机视口与应用布局，用于检查滚动、按钮、输入和 Maps 往返；报告记录“macOS 宿主 Android 模式”。它与 Android 设备／APK 的系统权限及服务运行验证分别记录。此前桌面模式截图保留为历史证据，后续截图使用 Android 模式。具体运行证据与源码版本在对应任务包单独记录。


## 原生控件的动态查找与几何

正式运行时增加 `ui.find(name)`，字符串名称与既有 `ui.name` 共用同一查找实现。隔离 Splash 的查找始终限于自己的脚本根，不搜索其它应用；它不接受路径、源码或业务调用。`ui[name]` 在锁定解释器中不能索引 UI handle，不能将它当作动态查找 API。`ui.child(index)` 返回当前控件的直接原生子实例句柄，index 从 0 开始；不递归搜索，也不依赖动态名字。低层树可以按自己的准确渲染顺序递归取句柄，再将业务 node.id 绑定在应用对象中。多 Image 可通过这种独立实例句柄调用既有 `load_image_from_data_async(bytes)`，每次加载仍须由应用核验实例、目标与 generation；销毁后不得按旧名称给新图加载旧响应。

`ui.find(name).rect()` 或实例句柄的 `rect()` 只读该控件最近一帧已经绘制、裁剪后的 `{x,y,width,height}`，坐标为宿主布局点。未绘制时返回 `nil`，应用需等待绘制再读取，重新布局或图片尺寸改变后也要在新帧读取，不能猜测窗口尺寸。模型得到的是应用选择提供的几何事实，不获得窗口操作或其它应用句柄。这个接口不执行生成代码、不引入嵌套 VM 或沙箱。

`agent-runtime.lock.json` 的 `ui_widget_overlay` 叠加于原 Maps 宿主 tree；其中包含一条追加于官方 Makepad patch 栈的独立 `makepad-ui-find-rect.patch`。wrapper 校验原定位、Maps、字体文档 patch 字节、新覆盖的基树、固定最终 runtime tree 与 patch 摘要。已有官方 runtime 栈可接续应用新层；新 checkout 由官方 setup 按完整锁定顺序重建。未知源码修改仍拒绝，不改其它应用权限或主题。

## 生成界面的执行诊断

`Splash.diagnostics()` 首次调用启用该实例后续诊断，因此父应用在 `set_text` 前调用它。接口返回最近收集的原始诊断字符串，重复读取不消耗；每次 `set_text` 清除旧稿诊断，空串停止子实例，捕获启用状态留给下一稿。已被日志排出的历史错误无法补回。只有调用接口的实例启用捕获，其日志通过 tee 保留；其它 Splash 默认行为不变。

脚本 `try` 主动捕获的异常仍按原 VM 清除，接口不会恢复它。原生 `on_render` 的属性类型错误已有实际证据返回 `expected DrawQuad, got object`，使应用能向 M3 反馈具体执行结果。这个接口属于现有 UI overlay，补丁摘要和 runtime tree 由锁文件管理，不是读取全局日志或新增界面校验。

## AutoNaviMapView 原生视口

UI overlay还导出AutoNaviMapView原型，复用Image纹理而保留普通Image行为。fit_bounds、set_camera、zoom_by、load_map_image与on_camera_changed管理GCJ02相机及当前图片；控件不持有候选ID或凭据。应用继续通过官方net接口请求高德视口图片，原生提供单指拖动、双击缩放，页面可调用zoom_by。当前未实现双指捏合，不是连续瓦片地图。

该覆盖与脚本原型导出都由agent-runtime.lock.json及现有UI patch摘要／tree锁定。新checkout按锁定顺序重建，现有工具链需重新运行agent-dev／agent-hidden，不使用旧二进制冒充新接口。供应商scale=1图片按真实标记验证512像素Mercator基准；原生相机请求会使旧解码key失效，纹理安装只接受当前key。实际接口、手势和图片位移证据见[交互地图任务](../tasks/interactive-map/packet.md)，本机Android模式不代表Android真机。此类型是本仓库覆盖，不能宣称stock宿主已有该接口。
