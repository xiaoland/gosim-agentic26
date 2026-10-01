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
