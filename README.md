# agentic26 · Navigation

GOSIM Agentic App 2026 参赛开发仓库，主场景为 Navigation，实现方向为**帝王蟹能力层**。

## 产品目标

在限定时间内组合步行、公交、地铁和打车，以最低费用抵达目的地，包含混合路线中的打车计费。通过已授权的跨应用上下文和逐步学习的偏好减少用户表达，只追问影响任务完成的关键缺失信息；学习到的偏好允许用户查看和纠正。日历、消息、机票邮件或设备状态是候选数据源，具体接入尚待确定。

初赛以 OctoScript 应用交付，复用比赛官方宿主，应用模型指定为 MiniMax M3（`MiniMax-M3`）。Agent 通过工具读取背景、查询交通并决定下一步，确定性代码检查候选路线，应用呈现来源、方案、确认和任务结果。优先验证现成模型接口与应用侧工具循环，不把新增 Rust 宿主服务作为初赛前置。本项目继续以可被调用的出行能力为重点，本地约束表单仅用于开发调试。

直接服务接入已获用户允许，不再要求所有数据与操作经过手机既有应用。首轮先接任务必需的服务；天气、提醒、手机自动化和运行时动态生成工具不作为前置，避免扩展到完整出行服务平台。

初赛演示城市为深圳，输入是一句“40 分钟内到机场，预算 50，尽量便宜。”系统需要从已授权、有来源的行程、位置和偏好补全机场、币种和出发位置。真实公共交通任务已完成确认、读回与重启恢复，另有真实混合任务完成确认读回；补全规则、完成证据及剩余边界归[当前任务](tasks/capability-boundary/packet.md)。

演示背景也按实际来源分别提供：日历文件、笔记和设备位置记录。Agent 在运行时关联这些资料，形成带依据的出行约束；不预先把目的地、偏好和起点整理为一个“行程背景文件”。演示数据与真实在线服务结果分别标注。

后续考虑疲劳、最快等目标，比较时间、换乘和可靠性的候选方案。用户确认后建立 Trip，交通条件变化时重新规划、再次确认并核验结果。“最慢”的含义尚未确定；“最晚出发”是候选解释。

## 当前能力

当前应用提供一句话任务入口。MiniMax M3 选择工具，分别读取模拟日历、笔记和设备位置，关联机场与航站楼，再查询高德地点、公共交通与驾车数据。确定性代码检查费用、剩余时间和实际路线端点，比较供应商返回的完整候选；用户确认后保存并读回 Trip。已在官方 stock OctoSense 的 macOS arm64 宿主完成真实操作：M3 七轮约 21 秒，补全深圳宝安机场 T3 国内出发与人民币，选中供应商估价 ¥3、1403 秒（约 24 分钟）的公共交通路线，确认、写入读回及重启恢复均通过。随后从宝安大仟里室外步道的独立模拟位置运行相同指令，M3 七轮约 30 秒，选中打车接地铁的完整混合候选：¥19、2063 秒（界面约 35 分钟），确认读回通过；同场公共交通 ¥5、3086 秒，超过期限。

这不是官方 Navigation 示例，而是从官方 My Notes 模板演进的应用。当前仅验证 macOS arm64。日历、笔记和位置是明确标注的模拟来源，地图与模型使用在线服务；尚未接通真实账户、GPS、导航执行、持续重规划或长期偏好学习。费用与耗时是供应商估计，推荐仅表示已核实候选中的最低估价，不保证实际到达或成交价。两次真实任务分别验证公共交通和混合候选，驾车费用均保持未知。混合费用直接使用供应商完整候选总价；综合耗时包含供应商等车估计，叫车等待未单独核实。未知价格、过期与端点等边界另经隔离原生检查。全程打车缺少候车数据时只作对照。首轮支持数字分钟数与“预算”金额；无法识别的硬约束需要澄清，不能由模型自行放宽。

开发指引见 [AGENTS.md](AGENTS.md)，知识归属和当前任务见 [文档导航](docs/index.md)。仅采用 SVC 的文档知识层与 task packet；它们不是应用中的用户记忆能力。

## 开始开发

macOS Apple Silicon 是当前验证目标，需要 Git、Rust stable、Python 3.9+ 和可用图形会话。依赖源码放在仓库同级的忽略目录，不进入参赛包；首次编译需要网络与数 GB 磁盘空间。

在 Git 忽略的 `.env` 配置 `AMAP_API_KEY`、`MINIMAX_API_KEY`、`MINIMAX_BASE_URL` 和 `MINIMAX_MODEL=MiniMax-M3`。高德使用 Web 服务 Key，当前模型地址固定为 `https://api.minimax.cn/v1`。启动器生成隔离宿主 profile 和应用私有配置，权限为 0600；凭据不进入 `bundle/`、Git、模型输入或日志。受信任的本地应用在运行时读取高德与 M3 Key，具体边界见[架构说明](docs/architecture.md#宿主集成)。

```sh
cd ~/Development/agentic26
make agent-bootstrap   # 构建固定版本的官方 OctoSense desktop
make agent-doctor      # 检查版本、配置及打包边界，不请求在线服务
make agent-init-demo   # 重置独立模拟来源及时间；会关闭本启动器的实例
make agent-dev         # 显示正式应用窗口
```

`agent-init-demo` 将日历航班设为两小时后，并生成独立笔记与带当前时间的位置记录。默认位置为宝安大仟里室外步道的模拟坐标，曾在上述真实查询中返回可行混合候选；实时结果可能变化。三份模板在 `demo/`，运行数据在 `.local-state/agent/` 的应用 jail 中；普通启动保留已编辑的来源。位置过期会阻止规划，重新生成演示数据应明确执行初始化命令。

```sh
make agent-status
make agent-tree
make agent-logs
make agent-shot SHOT=build/debug.png
make agent-stop
make agent-hidden      # 相同接口，隐藏窗口，用于原生交互验收
make smoke             # 隔离数据与离线合成响应的行为检查
make check             # Hub 包预检；不替代真实任务验收
```

修改应用后重新执行 `agent-dev` 或 `agent-hidden`。官方系统应用在编译时嵌入，启动器会重新打包、增量编译，并核对实际挂载源码，不能靠重启旧二进制加载新脚本。启动器只关闭它自己管理的实例。调试接口、运行版本和目录说明见[工具链说明](toolchain/README.md)。

旧 `make bootstrap`、`make doctor`、`make dev` 与 `make run-hidden` 仍保留为 App Hub card-host 路径，适合不需要宿主模型服务的隔离实验；完整 Navigation 使用上面的 `agent-*` 命令。两条工具链分别由 `toolchain/sources.lock.json` 与 `toolchain/agent-runtime.lock.json` 锁定，不修改个人全局模型配置或上游 Rust 源码。

真实截图必须来自当前应用并查看后再更新 `bundle/screenshots/01-main.png`。包编辑后执行 `make check` 更新摘要；签名后的包不能直接沿用此编辑流程。历史初始化证据见[验证记录](docs/verification.md)，当前行为的验收证据见[任务包](tasks/capability-boundary/packet.md)。

## 参赛与上架

[当前官网](https://create.gosim.org/agenticapp26/)的初赛提交截止是 **2026-10-04 23:59（北京时间）**。比赛要求可运行作品与 Apache-2.0 公开源码；本地初始化不等于已报名、已提交或已上架。Hub 预检也不等于比赛验收。

依照 [App Hub 开发指引](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/FIRST-APP.md)，本仓库使用它推荐的 OctoScript script-app 模板，保留独立应用仓库；不会修改 Hub 的 catalog/index/artifacts。

源码仓库：[xiaoland/gosim-agentic26](https://github.com/xiaoland/gosim-agentic26)。源码发布与 Hub 上架、赛事提交是不同步骤。

`listing.json` 的发布者、支持和隐私网址目前保留明确占位值，不伪造身份/链接。正式发布应用前由作者补齐并审核；当前只声明经过本机验证的 macOS，不宣称手机可用。应用尚未签名或提交比赛。

许可证：Apache-2.0。模板来源与归属见 `NOTICE`；精确版本见锁文件。
