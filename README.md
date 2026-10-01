# agentic26 · Navigation

GOSIM Agentic App 2026 参赛开发仓库。目标是在限定时间内，组合步行、公交、地铁、打车，以最低费用到达目的地；后续扩展疲劳、最快等偏好。

当前是 **原生开发脚手架**：可填写、校验、保存和恢复一份出行约束草稿。路线求解器、自然语言 Agent、地图/交通数据、导航执行、Rinx 集成均未实现。界面中的“保存”只写本地草稿。

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

## 文件

- `bundle/`：应用源、包清单、图标及原生截图；只有这里属于 Hub 应用包。
- `BRIEF.md`：用户需求及当前初始化范围。
- `docs/architecture.md`：约束、混合路段、票制状态、Agent/求解器分工草案。
- `docs/sources.md`：一手赛事/上游资料与二手讨论的边界。
- `docs/verification.md`：本次实际执行的验证及局限。
- `tools/`：本仓库的工具链包装与原生测试。
- `toolchain/sources.lock.json`：五个上游 Git revision；`hub.Cargo.lock` 固定本次构建的 Rust 依赖。
- `.local-state/`、`build/`：本地草稿、日志和 review packet，均忽略于 Git。

## 从这里继续

1. 选定演示城市与数据来源，明确“最慢”的产品含义。建立带来源/时间戳的混合路段与按整段计费的打车 fixture。
2. 实现独立确定性求解器：时间为硬约束、费用最小化，并覆盖不可达、超时、换乘与票价边界。
3. 接入候选路线界面、Trip 状态与确认/重规划流程，再接真实 provider。
4. 验证实际宿主 Agent 接口，然后连接自然语言理解和工具调用。App Hub 准入声明不等于宿主已实现服务。
5. 固定比赛运行的 OctoSense/Rinx 宿主版本，录制完整真实任务证据，补齐发布资料。

## 参赛与上架

[当前官网](https://create.gosim.org/agenticapp26/)的初赛提交截止是 **2026-10-04 23:59（北京时间）**。比赛要求可运行作品与 Apache-2.0 公开源码；本地初始化不等于已报名、已提交或已上架。Hub 预检也不等于比赛验收。

依照 [App Hub 开发指引](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/FIRST-APP.md)，本仓库使用它推荐的 OctoScript script-app 模板，保留独立应用仓库；不会修改 Hub 的 catalog/index/artifacts。

`listing.json` 的发布者、支持和隐私网址目前保留明确占位值，不伪造身份/链接。正式发布前由作者补齐并审核；当前只声明经过本机验证的 macOS，不宣称手机可用。此仓库尚未配置 GitHub origin，也没有执行推送、签名或赛事提交。

许可证：Apache-2.0。模板来源与归属见 `NOTICE`；精确版本见锁文件。
