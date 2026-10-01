# 初始化验证记录

日期：2026-10-01。环境：macOS arm64、Rust/cargo 1.93.0、Python 3.12.10。

## 实际执行

- 官方 `setup-native.py --check`：通过，三个运行时 revision 与上游 lock 一致。
- 初次普通 release 构建：完成，5m 24s；此前 `--locked` 因上游 Cargo.lock 不匹配而失败，见 toolchain/README.md。
- `make bootstrap`：通过，使用保存的 hub.Cargo.lock 执行 `cargo build --locked --release`，随后 doctor 全部通过。
- `make smoke`：通过，驱动真实隐藏 card-host，使用独立 bundle 和应用数据。测试空输入、非法/超范围分钟数、负预算、合法草稿保存与读回、全字段重启恢复、预算留空、清空与重启、未知 schema 和损坏 JSON 的恢复。最终各次运行日志没有脚本/回调错误。
- 截图检查发现过底部溢出，修正布局后确认按钮、状态和能力说明在 412×892 窗口内可见。
- `make run-hidden` → `make shot`：最后版本的真实截图为 `bundle/screenshots/01-main.png`，已打开检查。保存按钮的焦点颜色也已修正并检查。测试的保存状态截图为 `build/smoke/run-h3oa_nqi/saved.png`，也已检查。
- 所有本次启动的 card-host 实例均已通过自己的 remote `/quit` 关闭。
- `hub scan bundle --packet build/review.json`：生成七问；自查回答见 `build/REVIEW-ANSWERS.md`。未配置外部 reviewer，未伪造独立审核通过。

## 最终预检输出

```text
python3 tools/octo check bundle
octo: hub stamp -> e2c0eef913eaaf90f67e2147c29763e6f5c59111cec860cd0e9719f8cabc241b
octo: /Volumes/WorkSSD/Development/.octosense-agentic26/OctoSense-App-Hub/target/release/hub check /Volumes/WorkSSD/Development/agentic26/bundle --allow-unsigned
agentic26-navigation 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
octo: note: listing.json still holds template placeholders (example.com, Replace with); the gate accepts them, a reviewer will not.
```

## 当前限制

这是应用初始化，不是完整参赛作品。路线规划、交通/地图 provider、LLM/Agent、Trip 执行与动态重规划尚未实现。Rinx、OctoSense shell、手机和真实导航均未验证。平台清单只写本次验证的 macOS。

发布者信息保留占位，未签名、未创建 GitHub 远端、未推送或提交比赛。未申请视觉/发布批准，因为本次只初始化开发仓库。后续发布阶段由作者补齐身份、支持和隐私资料，再完成必要审核与签名。

## 过程中发现的差异

- 用户给出的 `/agentic26` 路径返回 404；已从官方仓库找到 `/agenticapp26/`。
- 官网实时页使用 Rinx，搜索缓存仍有 robrix2。
- 上游 Cargo.lock 与推荐 native runtime 的 path dependencies 不匹配，已保存实际解析后的锁文件，无 Rust 源码补丁。
- 损坏 JSON 不能仅靠与 nil 比较识别；缺失属性读取也会产生脚本错误。最终恢复逻辑使用源码已确认的 `is_object`/`is_string` 和 `try` fallback，并通过原生重启测试。对象合并尝试未通过测试，最终直接读取经过检查的解析对象。
