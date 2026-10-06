# Navigation 文档与任务导航

长期说明解释产品目标、技术约束和操作方法；task packet 保存正在处理的问题、授权与下一步。历史验证只证明其记录版本和条件下观察到的结果。

## 知识归属

| 要理解什么 | 权威入口 |
| --- | --- |
| 产品目标、能力层方向、用户行为与当前范围 | README 的 [产品目标](../README.md#产品目标) 与 [当前能力](../README.md#当前能力) |
| 组件职责、路线模型、上下文与宿主边界 | [技术草案](architecture.md)；提案尚不等于实现 |
| Navigation 字体来源、许可与复现 | [字体资源说明](../bundle/assets/fonts/README.md)，完整 [OFL](../bundle/assets/fonts/OFL.txt) |
| 开发命令、环境与参赛交付 | [README](../README.md)、[工具链说明](../toolchain/README.md) |
| 赛事、上游能力和方法资料的事实来源 | [资料核对](sources.md) |
| 已执行验证及其条件、证据和局限 | [初始化验证](verification.md)；后续任务证据先归对应 packet |
| 协作、授权、开发约束 | [AGENTS.md](../AGENTS.md) |
| 当前任务、待决事项和恢复点 | 对应 `tasks/<task>/packet.md` |

一个文件可以承载职责清楚的不同章节，不额外创建重复的 PRD、TDD 或部署模板。实现事实优先由源码、配置、schema 和锁文件维护；文档保留行为意义、理由及难以从源码恢复的约束。

## 当前任务

[首次定位与查询交付](../tasks/query-delivery/packet.md)保存当前诊断日志配额与迟到渲染通知修复入口。[混合路线与打车价格](../tasks/mixed-routing/packet.md)保存0.11.0实现与证据边界。[开发诊断](../tasks/observability/packet.md)保存可观测性／可诊断性实施与验证入口。[首次定位与查询交付](../tasks/query-delivery/packet.md)保存地图省略与UIUX待改善事项，以及既有真实运行缺陷、修复与harness验收入口。[交互地图](../tasks/interactive-map/packet.md)保留0.9.0原语接入、真实图联调和证据边界。[Agent 动态界面与局部字体](../tasks/agent-generated-ui/packet.md)保留0.8.3及此前原生生成、详情和静态图证据。[交互优化与应用联动](../tasks/interaction-integration/packet.md)保留 0.2 实现及实际宿主接口核对。[一句话机场 Navigation Agent](../tasks/capability-boundary/packet.md)保留直接服务接入方案、0.1 用户验收及历史运行证据。已完成的[本地开发与调试闭环](../tasks/local-development/packet.md)和[能力层项目初始化](../tasks/initialization/packet.md)保留各自验证与发布依据。此入口不重复 packet 的进度；后续非简单任务建立或接续对应 packet，并维护有效导航。

## 采用的 SVC 范围

采用 [xiaoland/svc](https://github.com/xiaoland/svc) 的 Corpus 15.0.0，固定在 commit `4fe4c66ac4deb35209069c00b1bbdc1b22aae3af`，仅使用下列两个知识域。方法资料按需从固定版本读取；本仓库保存自己的项目知识与任务状态，不复制上游 Corpus，不依赖本机全局 `svc` 的版本。

| 需要方法说明时 | 固定版本入口 |
| --- | --- |
| 判断持久知识应该归哪里 | [Specifications](https://github.com/xiaoland/svc/blob/4fe4c66ac4deb35209069c00b1bbdc1b22aae3af/corpus/specs/index.md) |
| 建立与维护 task packet | [Task Packet](https://github.com/xiaoland/svc/blob/4fe4c66ac4deb35209069c00b1bbdc1b22aae3af/corpus/task-packet/index.md) |
| 任务包需要拆分时 | [Growth](https://github.com/xiaoland/svc/blob/4fe4c66ac4deb35209069c00b1bbdc1b22aae3af/corpus/task-packet/growth.md) |
| 建立第一个 packet 时 | [Packet template](https://github.com/xiaoland/svc/blob/4fe4c66ac4deb35209069c00b1bbdc1b22aae3af/corpus/task-packet/templates/packet.template.md)；只取有用字段，不复制空章节 |

本次没有安装完整 SVC CLI，也没有配置其 dev、run、double、telemetry、analysis，或引入 Working Methods、Taste、Sub-agents、Verification 与协调扩展。需要创建任务包时直接编辑 Markdown；文档中不提供未安装的 `svc task` 命令。

共享开发规则参考同级 `factory26/AGENTS.md` 的知识归属、授权记录、任务恢复和知识回流方式。Factory 的实验、预算、模型配置、提交授权和测试禁令不属于本项目规则。
