# 固定的开发工具链

`sources.lock.json` 记录 2026-10-01 实际使用的五个上游 Git commit。
OctoScript-App-Design-Flow 的 `native-runtime.lock.json` 进一步锁定
Octoscript-Makepad，由该仓库固定 makepad 和 octoscript。

本次首次执行 `cargo build --locked` 时，上游 App Hub 的 Cargo.lock 与这组
path dependencies 不一致，Cargo 拒绝构建。按官方 QUICKSTART 的不带
`--locked` 的构建命令完成依赖解析后，将实际使用的锁文件保存在
`hub.Cargo.lock`。bootstrap 仅允许用它替换原始上游锁文件或相同的已有
锁文件；其他本地改动会被拒绝。随后使用 `--locked` 构建。

没有修改上游 Rust 源码，也没有升级本机 Rust。初次验证环境为 macOS
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
使用官方 `tools/setup.py --no-hub` 应用已锁定的运行时补丁，再执行 `cargo build --locked`。
可用 `AGENTIC26_AGENT_TOOLCHAIN` 指定另一隔离目录。启动器拒绝版本或源码摘要不符，
不会覆盖旧工具链或个人全局模型配置。

应用通过官方 `OCTOSENSE_SYSTEM_APPS` 编译进宿主。启动前复制当前 `bundle/` 到
忽略的 `build/agent/`，仅在这份副本中为 id 加 `os.` 前缀以进入 stock shell 的应用列表，
由官方 packer 重新盖摘要。每次启动都增量构建，并核对生成包与当前源码；
因此编辑 `main.splash` 后需重新执行 `agent-dev` 或 `agent-hidden`。
输出和 `build/agent/build.json` 记录源码 SHA-256 与实际包的 BLAKE3，避免误用旧内嵌界面。
这条路径是本地开发加载方式；正式外部安装仍走官方签名 catalog。

`agent-init-demo` 明确重置三份互相独立的模拟来源，将模板时间替换为当前东八区时间，
航班设为两小时后；`agent-dev` 和 `agent-hidden` 保留已编辑的数据。
私有数据在 `.local-state/agent/`：官方宿主的 `octos/profiles/_main.json` 保留单个 M3 provider，
兼容 `model.complete` 探针；当前应用通过 stock `net.http_request` 直接调用 M3 和高德。
仅这个应用的 jail 内 `private-config.json` 提供 `amap_api_key`、`minimax_api_key`、
`minimax_base_url`、`minimax_model` 四个运行时字段。
目录权限为 0700、这两个文件为 0600；两份配置不进入应用包、Git 或启动参数。
模型配置固定一个 MiniMax-M3 provider，fallbacks 为空；其它模型配置会被拒绝。
M3 地址只允许已实测的 `api.minimax.cn` HTTPS 主机、默认或 443 端口和 `/v1` 路径，
不接受 URL 账号、查询参数或片段；启动器将尾斜杠和显式 443 规范为上述 Base URL。
应用请求固定 `/v1/chat/completions`，用 Authorization header 传 key，并关闭 thinking；
应用清单仍须声明这个 HTTPS 主机，应用本身也须核对私有配置中的模型和地址。
两家 key 对被授权应用运行时可见；应用承担动作 schema 校验、调用预算与错误脱敏，
不能依赖 `model.complete` 的预算或输出检查覆盖直接请求。
应用必须捕获网络派发失败并使用通用错误，不能把 key、含 key 的 URL、原始网络错误、
响应全文或私有配置写入 UI、日志、模型输入、Trip 或验收记录。

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
当前 Navigation 已完成 M3 七轮约 21 秒、在线公共交通选择、确认保存读回及 stock 重启恢复；该基线没有混合候选；补充真实任务以七轮约 30 秒完成 ¥19／2063 秒的打车接地铁方案确认读回。完整条件、失败状态与源码版本对应关系见任务包，不以模型探针代替业务证据。
