# RC6 升级调查与隔离恢复点

状态：2026-10-12，runtime_update 已获root授权采用正式lock／patch／wrapper并setup宿主。旧源码完整保留，stage与正式应用build仍等待rail_model的main冻结；bundle/main不由本owner修改。

用户授权来源：主任务转述用户“octosense有更新，赛事方要求升级到最新版”，授权升级及必要修复。此次调查、编译与离线探针不调用 M3／交通供应商、不发布或推送、不批准系统权限。

## 官方基线

[RC6 Release](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.6) 由 API 在本次核对确认 `published_at=2026-10-11T12:01:37Z`，是最新桌面 prerelease。发行源码 `f9f6fea90b52182790cb2641fd0145c425af4d84`（commit 2026-10-11T08:35:22Z）；当时 main 为 `3a56305771594ae4c1430b5b61be40e50b76e9bf`，晚于发行版。主任务采纳发行 SHA 为目标，未选择 main。GitHub `/releases/latest` 返回404，因为当前发行版是 prerelease；不能据此判断无更新。实时 raw README 已写 RC6，网页缓存曾仍写 RC4。

RC6 依赖：Octoscript-Makepad `6cf2d90aa33ff4ae603f49c7557f3ecf986207f0`；Makepad `d653bc4493619ab979ccff165cf48c0c63b77d19`；Octoscript `2e37d9e657a246f16718d9a475e167ccd2d5b5fa`；App Hub `386359153ed6377b5f047bd9ed2767a6a2ac2bc7`。App Flow 已从 Design Flow 更名，旧 URL 仍可取到最新 README；本次 HEAD `15b1da01a769a770aaf12bd3012d17c6ff267b6c`。

## 已观察到的迁移边界

现有所有 OctoSense、Makepad、Hub patch 的直接 `git apply --check` 均失败，需要按语义移植，不能只改 revision。隔离 RC6 setup 已成功；保留完整官方 Makepad patch 栈。

| 当前覆盖 | RC6 源码证据与下一动作 |
| --- | --- |
| Hub request 存活检查 | `crates/appstore/src/services.rs` 已有带 invocation generation／deadline 的 `Replier.is_pending`，本地 location-replier 可删除，不覆盖回旧实现。 |
| 字体许可文档 gate | `crates/app-hub/src/gate.rs` 明确 plain documentation（含 font license）不加载链接，txt/md已跳过；本地 font gate 可删除。 |
| macOS 本地 location.get | 官方 `location.get@1` 仅Android且是未知时效缓存。应迁移为 `location.permission.request` 后 `location.sample@1`；不能继续按旧 contract 读 success/lat/lon/corelocation。旧定位覆盖可随应用迁移删除。 |
| maps.pick | 当前 main 没有 maps.pick 调用；不要为无消费者选择模式再移植旧 Maps bundle。官方 Maps 保持原版；交互地图控件另见 UI 覆盖。 |
| model.chat | RC6 官方仍为 one-shot complete＋media，未提供 chat。隔离三方移植纳入新版 bounded worker dispatch，保留 scope、pending、admission检查和原 complete 270秒期限，chat保持130秒；三项chat mock与19项原complete回归通过。 |
| UI＋AutoNaviMapView | RC6仍缺本地find/rect/fragment diagnostic/camera raster原语。三方移植保留新版 ScriptErrorRecord 与解码等待逻辑；UTF8历史稿前缀安全比较仍需保留。 |
| fs.read_async／utf8_chunks | RC6有native StorageSnapshot，尚无脚本 read_async／utf8_chunks。隔离移植保留现有API，并传递新版 callback host_prompts_allowed，后台回执不能借权限提示升级。 |
| checked timer | RC6仍无start_timeout_checked。隔离移植同时保留host_prompts_allowed，work和独立错误回执均延续其来源。 |

官方location.sample参数为可选 `timeout_ms`（默认10000，1..30000）、`max_age_ms`（默认5000，1..60000）、`max_accuracy_m`（>0且<=100000）。响应直接在 `r.data` 返回 latitude/longitude/accuracy_m/timestamp（Unix秒）/age_ms/source:"platform"/freshness:"fresh"；没有success/code包装。`location.sample.cancel({})` 返回cancelled计数。能力需requires host-api-v1及独立app consent＋OS grant；真实权限只能由用户物理点击。当前WGS84→GCJ02转换继续成立，但应根据新平台采样字段记录来源，不能只接受corelocation字符串。

RC6 bridge 参数仍1MiB，新增队列总16MiB／每app4MiB的前分配边界；Host reply上限4MiB。本地chat HTTP响应仍沿用1MiB。脚本单文件写／新增read_async仍1MiB；总jail默认16MiB（宿主可覆盖）；官方native文件import到64MiB不改变脚本写/read_async容量。没有提高脚本预算。

## 当前验证与正式切换条件

独立源码、target和原始日志保存在忽略的隔离实验目录。先完成chat mock tests、异步读取／checked timer／UTF8分片／UI原语与宿主编译；将可采用patch输出到build研究目录，保留精确官方基树与SHA摘要。未启动正式宿主、未修改共享target/stage、未作真实权限或在线供应商验收。root冻结业务基线后才能迁移正式工具链和应用定位调用。

隔离移植已生成候选 `build/research/runtime-upgrade/rc6/{octosense-navigation-rc6.patch,makepad-navigation-rc6.patch,candidate-lock.json}`；两份patch以临时index从官方SHA／官方Makepad完整patch栈tree应用，所得树与candidate-lock完全相同，`setup.py --check`通过。隔离验证结果已完成，详见下面；这仍是正式迁移的采用材料，尚未修改正式工具链。另有 `proposed-agent-runtime.lock.json` 提供完整官方依赖ref、显式Rust1.99与两份补丁的摘要／tree。草案使用单个navigation_overlay字段，须与wrapper精简同步采用，不能直接交给旧wrapper。

最终隔离结果：RC6宿主以已安装Rust1.99.0构建成功；默认1.93.0会因官方gridcraft使用Rust1.94起稳定的EULER_GAMMA失败，不是本地patch缺陷。未更改全局默认工具链；正式wrapper的build与hub_binary两处应显式使用lock的rust_toolchain="1.99.0"，doctor验证同版，不能静默退回1.93。

22项model mock回归（chat3＋complete19）、chat130秒／complete270秒／chat discovery期限测试、unlimited保账本且其它app继续限额测试、async容量/路径/UTF8/符号链接测试、async来源/单消费/死VM测试、checked timer2项、UTF8分片和fragment结构测试均通过。Native实际运行另通过6项UTF8/fragment/UI find+rect/AutoNavi camera/异步回执/checked timer检查，无原生错误；Android模式切换后重新打开probe，在412×892截图中已查看实际app画面（不冒称真机、无供图）。报告/截图/精确tree/patch摘要归 `build/research/runtime-upgrade/rc6/verification.json`、`candidate-lock.json` 与同目录支持文件。

context_sources实际只读核对确认 RC6 device_calendar.events.list@1 implemented/supported=true；permission.status supported=true/app_consent=false/os_permission=not_determined，无scope拒绝；notes.read implemented/supported=false。未申请权限；背景接口证据由其任务归属保存，Home截图不当app展示。

隔离候选probe已停止。root随后授权正式采用；lock／wrapper已精简为navigation_overlay，两份补丁已进入toolchain；正式旧宿主源码保留为OctoSense-pre-rc6，RC6 setup通过。真实ledger升级前后摘要相同，未改业务状态。location.sample、背景adapter和main集成由rail_model持有，正式stage/build等待其冻结。真实定位／授权需用户物理点击，真实M3／交通在线结果不能用本探针替代。

## Notes 窄桥实际接续

root采纳Notes advisor后授权本owner在同一宿主patch接入shared_tools.call/cancel并启用app-notes，未增加kernel。只开放notes.search/read，身份来自ServiceCall与contained_account，owner/risk来自Catalog；通过官方ensure_loaded／安装grant和Event::Call＋ToolReply，保留官方consent、schema、审计与跨应用工具预算。cancel以客户端request_id字符串识别，限定app/account/isolate；请求超时、isolate关闭、撤回与迟到结果边界均有测试。

actualprobe发现system-app先因tool offer缺失被拒。已使用官方set_agent_tool_offer，仅为os.agentic26-navigation登记两项；不授grant、consent，也不扩大到其它system/store apps。发现shared_tools不是已知capability，descriptor已改runtime及已验证macos平台；discovery校验单测补齐。最终桥5项和原relay44项测试通过，无kernel宿主app-hub,app-notes构建成功。

原生合成链证据在忽略的build/research/runtime-upgrade/rc6/notes-bridge-29fn_532：全新HOME，官方devmode只覆盖os.agentic26-navigation；closed搜索回app_not_running。经原生Notes UI创建唯一合成两行笔记，再桥search命中1项、read返回完整source及created_ms/edited_ms，官方{text,note,data}包络保留。截图已查看，自有实例已停；这不代表真实个人Notes许可或背景验收。该链运行于metadata修复前，记录两条descriptor错误；context_sources已完成修复后一次describe及无grant真实拒绝核对：两方法implemented/supported=true，actual not_granted映射needs_connect／records=[]，5项通过、native_errors=[]，无devmode／未开Notes／未申请权限且正常停止。证据归build/research/real-context/notes-adapter-check。

## RC6 存储兼容核实

官方 AppHub `cardapp.rs` 仍以 `data_root` 作为 apps 根，`host_dir=root/.host`；`app-policy/containers.rs` 的 isolate jail 仍为 `app_data_root.join(app_id)`。`host_tools/areas.rs` 明确指出脚本 `fs.*` 根是 jail，不是账户目录。隔离新版以 Navigation 正式 app id 写出的 probe 回执也实际位于 `home/apps/os.agentic26-navigation/`。新增 common/accounts 用于原生应用和 Agent 工作区，不要求迁移 Navigation 的 private-config、出行 index/snapshots 或 dev-trace；wrapper 与 smoke 的旧 jail 路径仍匹配。

模型 `complete/media/mod.rs::run_call` 先 attach ServiceCall 的 host_dir；ModelHost::attach 仍读取 `host_dir/model/ledger.json`。现有 unlimited 覆盖仍保留计数，UTC 日切计数规则没有改变。默认开发 home 的原账本 SHA6682e8 未改动，但它是旧19calls/61208tokens，不能冒称继承真实490calls/24547438tokens。后者归 rail 任务的 state-round30，SHAa094c993；下一轮 E2E 必须明确使用该 owner 的隔离 clone，不能重置计数或把默认 home 当成它。未迁移个人日历或笔记，也未固定全局账户 ID。

正式 main 冻结为5e61ab4f后开始构建。RC6 官方 Maps 新增 tools.json，wrapper 已允许固定源码树的附属文件并继续逐文件验证 pack。Notes 回调按宿主 call_id 代际取 Pending，防止已取消旧回调抢占复用 request_id 的新请求；五项桥边界回归继续通过。

项目预检与实际admission不能互换：官方 `check_bundle` 还检查 inventory、包内容、publisher/listing 等包门。root采用薄desktop `--navigation-check`＋shell helper，以普通 `HostLimits` 和运行时共享的两个Notes工具常量复用官方包门；仅接受Navigation，不改变全局default。官方harness仍处理盖摘要及其它提示，生成的两分支适配器将stamp送官方hub、check送配套host。隔离正常包接受、未offer notes.write拒绝、损坏digest拒绝三项已通过，stock拒绝仍单独保留作兼容边界证据。最终source owner main168396e0冻结后，配套正式check（官方harness机械检查保留）、盖摘要、build、doctor全部通过；四项gate边界以正式binary复跑通过。最终树51089110，patch79c14eab，源码集合3a7f2778、binarya2a1d4e2、manifest45cde105。pgrep无octosense，默认账本SHA6682e8未变。stock拒绝原件保留在stock-check-refusal.log。formal-adoption.json保存完整hash及停止状态；未作真实个人权限或付费业务验收。
