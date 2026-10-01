# agentic26 · Navigation

GOSIM Agentic App 2026 参赛开发仓库，主场景为 Navigation，实现方向为**帝王蟹能力层**。

## 产品目标

在限定时间内组合步行、公交、地铁和打车，以最低费用抵达目的地，包含混合路线中的打车计费。通过已授权的跨应用上下文和逐步学习的偏好减少用户表达，只追问影响任务完成的关键缺失信息；学习到的偏好允许用户查看和纠正。日历、消息、机票邮件或设备状态是候选数据源，具体接入尚待确定。

产品依托既有地图或系统 Agent 完成任务，复用地图的地点选择、路线呈现和导航交互。本项目重点是可被调用的出行能力，独立的约束表单或自然语言输入框不作为产品主入口；目标地图与宿主尚未选定。

后续考虑疲劳、最快等目标，比较时间、换乘和可靠性的候选方案。用户确认后建立 Trip，交通条件变化时重新规划、再次确认并核验结果。“最慢”的含义尚未确定；“最晚出发”是候选解释。

## 当前能力

当前只有供开发调试使用的本地出行约束草稿：填写起点、终点、可用分钟数和可选费用上限，校验后保存、重启恢复或清空。空地点、非法数字、非正时间和负预算会报错；存储损坏时显示错误并允许清空重建。应用只使用 `storage`，保存的是用户输入。它由官方 My Notes 模板改写，通过 card-host 运行，不是官方 Navigation 示例或完整 OctoSense 系统。

跨应用取信息、偏好学习、路线求解器、自然语言 Agent、地图/交通数据、导航执行和 Rinx 集成都尚未实现。技术提案见 [架构草案](docs/architecture.md)，实际验证见 [验证记录](docs/verification.md)。

开发指引见 [AGENTS.md](AGENTS.md)，知识归属和当前任务见 [文档导航](docs/index.md)。开发侧仅采用 SVC 的文档知识层与 task packet，不依赖完整 SVC CLI；它们不是应用中的用户记忆能力。

## 开始开发

本机路径：`~/Development/agentic26`。依赖源码位于同级 `.octosense-agentic26/`，不放入参赛仓库。macOS Apple Silicon 为当前验证目标；需要 Git、Rust stable、Python 3.9+ 和可用图形会话。初次安装下载依赖并编译，需要网络与数 GB 磁盘空间。

```sh
cd ~/Development/agentic26
make bootstrap     # 获取固定源码版本并构建 hub + card-host；本机已执行
make doctor
make dev           # 显示原生窗口，首帧就绪后返回，打印 PID 和日志路径
# make run         # 也可在前台运行，日志写到终端，Ctrl-C 退出
```

日常调试使用 `make dev`，窗口保持运行，终端可以继续执行下列命令。自动检查使用 `make run-hidden`，它提供相同的交互接口，但不显示或抢占窗口。

```sh
make logs          # 当前实例的最近 100 行日志
make tree          # widget tree，含控件 ID、类型和矩形位置
make shot          # 真实截图 → build/debug.png，不覆盖上架截图
curl --fail --silent --show-error http://127.0.0.1:8146/snap
```

修改 `bundle/main.splash` 后需要重启，没有自动热重载。先查看 `/s` 的 PID，确认与启动输出一致，再退出该实例；重启会重新加载代码并计算包摘要。

```sh
curl --fail --silent --show-error http://127.0.0.1:8146/s
curl --fail --silent --show-error http://127.0.0.1:8146/quit
make dev
make logs
make shot
```

应用数据保存在 `.local-state/agentic26-navigation/`，重启不清空草稿。后台日志为 `.local-state/card-host.log`，每次启动会覆盖，定位失败前应先保留日志。窗口出现和包被准入不证明回调成功；检查日志、实际点击并读回保存结果。

```sh
rg -n '\[E\]|splash:[0-9]+:|refused|on_render closure failed|callback error' .local-state/card-host.log
make smoke         # 隔离 bundle、端口和数据，交互、修改、故障定位、修复及状态恢复
make check         # Hub 基础预检；当前仍有未签名和发布者占位提示
```

当前固定宿主的回调错误形如 `splash:<id>:74:29`；只使用 `storage` 的本应用在源码前有三行 prelude，因此对应 `main.splash:71:29`。加载时的语法错误使用另一种位置格式，不能套用此偏移；查锁定版本的 [Errors and the log](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/e08517254d9b2c316352eec4f959810d9ad22d40/docs/SCRIPT-API.md#errors-and-the-log)。新增能力或升级运行时后需要重新验证位置映射。

`make smoke` 只在 `build/smoke/run-*/` 的副本中改标题并注入一个错误回调，断言日志位置、修复后的保存和重启恢复。预期故障留在 `fault.log`、`fault-log.json` 与 `fault-tree.txt`；其余会话汇总在 `combined.log`，不得含意外运行错误。每个实例由测试自行关闭。最近一次实测见 [本地开发任务](tasks/local-development/packet.md)。

`PORT=其他端口 make dev` 可以换端口，`logs`、`tree` 和 `shot` 必须使用相同 PORT。端口冲突时启动会拒绝继续；确认归属后再处理已有实例。换端口不会自动隔离数据，并行实验须使用 `python3 tools/octo run bundle --hidden --detach --port 8147 --app-data build/dev-8147` 显式隔离。

上架截图另用 `make shot SHOT=bundle/screenshots/01-main.png`，实际查看后执行 `make check` 更新摘要。发布签名后的包不应使用此开发流程。

默认工具链位置是仓库同级的 `.octosense-agentic26/`。所有命令接受环境变量 `AGENTIC26_TOOLCHAIN=/absolute/path/to/workspace`，该目录里仍保持官方要求的五个 sibling checkouts。bootstrap 校验版本，遇到其他源码修改会拒绝继续，不会自动 reset。开发二进制固定输出到 Hub 自己的 `target/`，不依赖全局 Cargo 配置。

## 参赛与上架

[当前官网](https://create.gosim.org/agenticapp26/)的初赛提交截止是 **2026-10-04 23:59（北京时间）**。比赛要求可运行作品与 Apache-2.0 公开源码；本地初始化不等于已报名、已提交或已上架。Hub 预检也不等于比赛验收。

依照 [App Hub 开发指引](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/FIRST-APP.md)，本仓库使用它推荐的 OctoScript script-app 模板，保留独立应用仓库；不会修改 Hub 的 catalog/index/artifacts。

源码仓库：[xiaoland/gosim-agentic26](https://github.com/xiaoland/gosim-agentic26)。源码发布与 Hub 上架、赛事提交是不同步骤。

`listing.json` 的发布者、支持和隐私网址目前保留明确占位值，不伪造身份/链接。正式发布应用前由作者补齐并审核；当前只声明经过本机验证的 macOS，不宣称手机可用。应用尚未签名或提交比赛。

许可证：Apache-2.0。模板来源与归属见 `NOTICE`；精确版本见锁文件。
