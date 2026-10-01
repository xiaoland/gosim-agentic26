# 能力层项目初始化

- **目标**：将 Navigation 定位为帝王蟹能力层项目，接入 SVC 的文档知识归属与 task packet 机制，清理重复的模板入口，并发布源码到 `xiaoland/gosim-agentic26`。
- **边界与授权**：2026-10-01 用户原话：“我觉得我们的项目应该做到 ”帝王蟹：能力层“ ；现在我们继续初始化：引入 xiaoland/svc 的文档知识层、task packet 机制（此外的，都不要引入）；并且参考 ../factory26 的 AGENTS.md”。随后授权：“可以简化从 OctoSense-org/OctoSense-App-Hub 初始化出来的内偶然那个，比如 BRIEF.md,CLAUDE.md 等”和“你可以自由提交”。本次发布授权：“可以发布仓库到 xiaoland/gosim-agentic26 了”。可以创建公开源码仓库并推送当前任务改动；不实现数据连接或偏好学习，不引入 SVC 其它模块，不签名、上架应用或提交比赛。
- **完成依据**：知识入口能定位每类内容的唯一归属；packet 能独立恢复本轮目标、范围、事实和下一步；引用的文件与固定上游版本可读取；差异不包含应用或工具源码改动。GitHub 仓库为 public，远端 `main` 与本地 HEAD 一致，本地分支跟踪 `origin/main`。
- **当前事实**：知识导航和本 packet 已接通；中文 AGENTS 已定义任务创建、授权、知识回流与退休规则，并保留原有包安全和实际验收约束。产品需求与当前能力已合并到 README，重复的需求文件和 Agent 转发文件已删除；文件地图与知识归属分别由 AGENTS 和文档导航维护。仅采用 SVC Corpus 15.0.0 的 `specs/` 与 `task-packet/`，commit `4fe4c66ac4deb35209069c00b1bbdc1b22aae3af`；未安装 CLI 或复制其它 Corpus。2026-10-01 清理后的 `git diff --check` 通过，29 个本地链接及标题锚点可读取；应用、工具链、LICENSE 与 NOTICE 无差异，未重跑应用测试。现有应用仍只有本地出行约束草稿，跨应用数据和偏好学习尚未实现；[先前验证](../../docs/verification.md)保持历史身份。源码已发布到 [xiaoland/gosim-agentic26](https://github.com/xiaoland/gosim-agentic26)，GitHub API 确认 public、默认分支 main、Apache-2.0；远端 main 与本地 HEAD 一致，origin 已配置且本地 main 跟踪 origin/main。
- **下一步**：初始化与源码仓库发布已完成。后续能力开发以新 packet 确定演示城市、数据源和宿主能力；本 packet 在验收且无需恢复后按仓库规则退休。

材料入口：[项目知识导航](../../docs/index.md)、[产品目标](../../README.md#产品目标)、[当前能力](../../README.md#当前能力)、[技术草案](../../docs/architecture.md)、[来源](../../docs/sources.md)。
