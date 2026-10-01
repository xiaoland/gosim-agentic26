# agentic26 · Navigation

GOSIM Agentic App 2026 参赛开发仓库，主场景为 Navigation，实现方向为**帝王蟹能力层**。

## 产品目标

在限定时间内组合步行、公交、地铁和打车，以最低费用抵达目的地，包含混合路线中的打车计费。通过已授权的跨应用上下文和逐步学习的偏好减少用户表达，只追问影响任务完成的关键缺失信息；学习到的偏好允许用户查看和纠正。日历、消息、机票邮件或设备状态是候选数据源，具体接入尚待确定。

后续考虑疲劳、最快等目标，比较时间、换乘和可靠性的候选方案。用户确认后建立 Trip，交通条件变化时重新规划、再次确认并核验结果。“最慢”的含义尚未确定；“最晚出发”是候选解释。

## 当前能力

当前只有本地出行约束草稿：填写起点、终点、可用分钟数和可选费用上限，校验后保存、重启恢复或清空。空地点、非法数字、非正时间和负预算会报错；存储损坏时显示错误并允许清空重建。应用只使用 `storage`，保存的是用户输入。

跨应用取信息、偏好学习、路线求解器、自然语言 Agent、地图/交通数据、导航执行和 Rinx 集成都尚未实现。技术提案见 [架构草案](docs/architecture.md)，实际验证见 [验证记录](docs/verification.md)。

开发指引见 [AGENTS.md](AGENTS.md)，知识归属和当前任务见 [文档导航](docs/index.md)。开发侧仅采用 SVC 的文档知识层与 task packet，不依赖完整 SVC CLI；它们不是应用中的用户记忆能力。

## 开始开发

本机路径：`~/Development/agentic26`。依赖源码位于同级 `.octosense-agentic26/`，不放入参赛仓库。macOS Apple Silicon 为当前验证目标；需要 Git、Rust stable、Python 3.9+ 和可用图形会话。初次安装下载依赖并编译，需要网络与数 GB 磁盘空间。

```sh
cd ~/Development/agentic26
make bootstrap     # 获取固定源码版本并构建 hub + card-host；本机已执行
make doctor
make run           # 显示原生开发窗口，Ctrl-C 退出
```

修改 `bundle/main.splash` 后重启；启动与检查会重新计算包摘要。发布签名后的包不应使用此开发流程。

```sh
make smoke         # 后台原生交互测试，隔离测试数据，自动关闭自己启动的实例
make check         # Hub 基础预检；初始化阶段仍有未签名和发布者占位提示
make run-hidden    # 后台启动，默认端口 8146，保持运行供调试
make shot          # 对该实例拍摄真实截图
curl --fail --silent http://127.0.0.1:8146/quit
make check         # 截图变更后重新盖摘要
```

`PORT=其他端口 make run` 可以换端口。已有实例占用端口时先确认归属，不要退出其他项目的宿主。

默认工具链位置是仓库同级的 `.octosense-agentic26/`。所有命令接受环境变量 `AGENTIC26_TOOLCHAIN=/absolute/path/to/workspace`，该目录里仍保持官方要求的五个 sibling checkouts。bootstrap 校验版本，遇到其他源码修改会拒绝继续，不会自动 reset。开发二进制固定输出到 Hub 自己的 `target/`，不依赖全局 Cargo 配置。

## 参赛与上架

[当前官网](https://create.gosim.org/agenticapp26/)的初赛提交截止是 **2026-10-04 23:59（北京时间）**。比赛要求可运行作品与 Apache-2.0 公开源码；本地初始化不等于已报名、已提交或已上架。Hub 预检也不等于比赛验收。

依照 [App Hub 开发指引](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/FIRST-APP.md)，本仓库使用它推荐的 OctoScript script-app 模板，保留独立应用仓库；不会修改 Hub 的 catalog/index/artifacts。

`listing.json` 的发布者、支持和隐私网址目前保留明确占位值，不伪造身份/链接。正式发布前由作者补齐并审核；当前只声明经过本机验证的 macOS，不宣称手机可用。此仓库尚未配置 GitHub origin，也没有执行推送、签名或赛事提交。

许可证：Apache-2.0。模板来源与归属见 `NOTICE`；精确版本见锁文件。
