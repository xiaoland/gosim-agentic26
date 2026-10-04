# 交互优化与 OctoSense 应用联动

状态：2026-10-04。0.1 用户验收版已提交并推送为 `c99f50e`。0.2 界面、Maps 窄桥、正式构建及隔离在线整合已完成，待用户验收。包版本为 0.5.0，里程碑名称与包版本分别使用。

## 目标、授权与边界

用户明确：“很好，我验证了，可以称为‘0.1验收通过’，你可以提交、推送。接下来，我们进一步优化交互体验（UI/UX），并且尝试和 OctoSense 上其它应用（日历、提醒、地图等）产生联动。”随后要求先讨论：“UI/UX 优化、应用联动都是 0.2 的事情，我们还得先讨论呢。”研究授权为：“围绕这两点，你可以开始调研、分析、实验、思考、规划了，然后交付给我这两点的落地/优化方案。”用户于 2026-10-04 对[落地与优化方案](proposal.md)明确：“同意，开始实现。”

这授权原生目的地选择、方案卡、地图概览、条件修正，以及独立 Maps 搜索结果选择和返回的必要源码、宿主覆盖、验证与说明。日历／邮件账户接入、写提醒、任意地图落针、手选起点、连续导航和长期偏好学习不在本次实施范围。签名、上架及赛事提交未获本阶段授权。此前“只有输入框和两个按钮”是 0.1 的收敛边界，不限制 0.2 引入有任务价值的可视化交互。system prompt 保持目标、来源边界和协议，不加入规划教程。

用户要求主 Agent 保持协调角色、有界任务使用 GPT-6.1-Sol medium／low。会话环境切换后，原子 Agent 不再出现于 live agents，相关 cargo／smoke／probe 进程也未运行；按 Delegation 责任转移要求，由 `ui_finish` 接续界面、局部修复和在线验收，由 `host_finish` 接续宿主、构建与包检查。保留原有源码和实验，不重置。主 Agent 整合文档、包元数据、截图和交付。Ponytail 只提醒避免无效复杂度，不作为架构取舍依据。

## 方案与实施事实

界面保留一句话入口，查询后支持目的地搜索、预览与采用、代表候选及完整卡片列表、同源静态地图。卡片查看不写 Trip，独立确认重检同一候选。未知价格、缺段、过期和不可行原因保持可见。预算修正、停止后继续和地点采用保留原始起算时间；普通文字修正交模型理解，不被旧显式 POI 硬覆盖。历史记录保留来源和模拟标识，不能作为当前有效路线。

Maps 桥通过实际 isolate 绑定原 ClientId，请求的选择标识由宿主维护，只接受真实 Maps 返回方。成功激活原窗口，取消／关闭／旧请求有明确结果；不使用共享私有文件或剪贴板交换位置。Maps 返回 WGS84 和来源，Navigation 再进行高德转换、城市核实与重规划，不伪造高德 POI ID 或航站楼。等待选择消耗原期限。长等待只用于 maps.pick，不扩大其它服务期限。

宿主保持 OctoSense `d405d5c` 与 Hub `58c3c8a`，定位 patch 字节与旧 card-host 锁保持原样。独立 Maps 覆盖归 `toolchain/agent-runtime.lock.json`；单包同版本 app-contract 本地覆盖使实际策略识别 maps。新增能力预检使用相同 Hub CLI 的完整官方 harness，旧 checker 不放宽。补丁按上游→定位→Maps 在隔离 index 重建，最终树与锁定值一致。此桥是本仓库扩展，不是 stock 官方 API。

## 完成证据与实际限制

| 验证 | 观察与证据 |
| --- | --- |
| UI 离线原生 | main SHA-256 `8ceab7b01503fd66d83d4658ab2f3e9e44b189297c4f7600e25b7d75987ea781`；94 业务、58 定位、7 派发、23 UX 通过，`build/smoke/navigation-hoqk8vqw/report.json`。 |
| UI 实际点选 | 卡片切换不写 Trip；POI 搜索→预览→采用保持 received_at／arrive_by；原生 Image 显示公开样本 PNG。`build/research/interaction-integration/ui-finish-native/evidence.json`。候选与图片样本明确合成，不证明真实路线在线地图。 |
| Maps 正反往返 | 合成搜索结果的实际选择／取消／关闭／非法调用方／旧票据，加 Rust 身份边界；另实际中文搜索“深圳宝安国际机场”，选中 Photon 真实结果，回原实例同请求 WGS84 坐标。`maps-pick/report-safe.md`、`summary-safe.json`。底图瓦片当时未显示，不宣称其渲染通过。 |
| 正式工具链 | agent-bootstrap、含 maps 的完整 check、agent-build、agent-doctor 通过。`maps-pick/formal-*.log` 和 `build/agent/build.json`。doctor核对实际源包、覆盖树与二进制摘要；启动时另核实挂载。最新源码和截图已完成最终重盖摘要／重建，该同源版本的实际在线交互也已完成。 |
| 私密边界 | Git 管理及待新增文件已按实际凭据精确扫描，未发现密钥。运行日志、GPS与账户资料均在忽略目录。实际初始截图已查看并采用到 bundle，未含私有位置。 |

上述研究与验证的前缀为 `build/research/interaction-integration/`，均被忽略。完整研究入口为 `interop-study/`、`static-map-study/`、`app-surface-study/` 和 `ux-study/`；浏览器原型只辅助讨论，不能代替 Makepad 验收。持久事实归 README、architecture、sources 与工具链说明；proposal 保存已接受方案，不代表每项均已验收。

在线整合首次实际 M3 返回 read_location，宿主明确 permission_denied；没有盲目重试或自动模拟兜底。本次真实 GPS 端到端依赖系统定位授权。已明确改用隔离的显式 demo 起点，继续真实 M3／高德／Maps 验证，UI保留模拟来源。该验证不能被报告为真实定位通过。

在线实验另发现并修复首次选点截止未初始化、候选累积摘要重复增长及宽窗图像拉伸。新增回归覆盖首次截止、八策略候选完整性和去重；地图采用等比显示。已选地点后的刷新起点是执行前置，由确定性入口复用现有定位工具，再交回 M3 选择交通查询，未增加教程 prompt。

## 最终整合与接续入口

同一最终版本已完成实际 Maps 搜索／采用 → WGS84 返回 → 高德转换与城市核实 → 刷新明确模拟起点 → M3 查询三公交策略及驾车 → 14 候选 → 比较负例。原指令为 90 分钟、预算 100 元，本次选择公开机场 POI，航站楼未核实；费用、候车或端点等检查未通过，因此没有写 Trip。模型输入最大 12,747 字节，重复摘要修复在线有效。实际切换卡片后显示同源静态概览，不新增模型请求或写 Trip；无效确认被拒绝。再次 Maps 取消后原目标、received_at、arrive_by 和已有结果保留。

安全证据为 `build/research/interaction-integration/live-integration/report-safe.json`，实际结果图为 `final-cards-map.png`、`final-switched-map.png` 与 `final-maps-cancelled.png`，主 Agent 已查看卡片／地图图像。最终源包 SHA-256 为 `c7bad35424b73bdeb158e3c412195518881d91cedb2fb01e7082ee867b9206af`，bundle BLAKE3 为 `4be5e403292021a24489d1ce8dc7eabe1b82f1f22e1d9c500df3b2e33c418b71`；完整构建记录归 `build/agent/build.json`。最后 check→build→doctor 有效，之后没有产品源码变化。全部本任务测试实例已关闭。

当前交付可用 `make agent-dev` 体验；系统定位仍需当前宿主得到用户授权。0.2 等待用户验收，若有复测问题从本包接续，不重新解释为已验收。应用日历／提醒、真实账户及连续导航继续保留后续范围。

0.1 历史在线基线与用户真实广州番禺负例归[能力任务包](../capability-boundary/packet.md)，不能代替 0.2 当前源包证据。Calendar 新版本服务仅其自身可调用、未跨应用共享；Reminders 只读声明不等于写提醒可用。Mail 的账户权限与读正文标已读副作用已核实，但没有接入私人账户，本阶段不用它替代日历／提醒需求。
