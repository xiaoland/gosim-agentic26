# 已提交版本后的完整守护验收与界面改进

## 目标、授权与边界

继续完成出行目标守护的完整验收，并按实际失败改善手机 UI／UX、IA 和 harness。用户此前明确要求“继续完成完整验收，同时改进IA（字体大小有问题）”；本轮必要源码修复、真实 M3／供应商验证及自主提交推送已有授权。

2026-10-14，用户重新确认还可继续改进，因此此前“08:00冻结”不再作为当前工作的硬停止条件。已发布的 `v0.16.1` 保持不可变；后续源码与交付变化使用新的版本，不移动初赛 `v0.13.0` 或已发布标签。公开赛程与用户本次工作安排分开记录，不自行宣布赛事方已接受新评审版本。

保持自主 function-calling loop、渐进技能和自由 Splash DSL；harness 负责机械合同，LLM 保留语义判断。不增加固定业务模板、文本拦截、静默改写生成稿或固定成功路线，不为当前任务扩组件库、后台监听或新能力。真实模型与交通验证使用隔离状态；不读取新个人数据、不下单、不提交上游 PR。用户自行制作视频，本任务不再制作视频。

## 当前已提交版本

`0.16.1` 已公开提交：[Release v0.16.1](https://github.com/xiaoland/gosim-agentic26/releases/tag/v0.16.1)与[App Hub #116](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/116)。固定源码为 `c47929b23942e0f61de90e109c1034fab8e06463`；它与 `369cf70` 的 bundle 逐字相同，应用 source SHA256 `409553b9`、bundle BLAKE3 `df5b79e0`。之后的工作不能将这份已发布证据改写为新版本结果。

06:00一次性审计已更新 #116 的标题与正文当前Version，保留初赛历史；匿名访问视频与ZIP均HTTP 200，实际下载摘要通过，ZIP的42个文件与固定源码逐字一致。视频资产为 `final-v1.mp4`，104.367秒；正确视频、ZIP和证据的完整摘要归 `build/submission/audit-0600/result-safe.json`，最终交付原件归 `build/submission/final-c47929b/`。

配套 `--navigation-check --allow-unsigned` 通过；标准 `hub scan` 因 contained apps 未提供 `notes.search` 而 REFUSED，未生成扫描包。Hub尚未上架，也没有0.16.1的新赛事方验收回应。正式Hub审批还缺GitHub-attested workflow、pack、receipt与下载后publisher验证；不为得到绿色检查而删除实际使用的Notes授权。来源审计见 `build/submission/audit-20261014-0600/audit.md`，扫描边界调查见 `build/submission/candidate-229101c/scan-investigation.md`。

## 最新验收及未解决问题

**online23只通过新鲜手机UI验收。** 空出行、正常挂载入口、真实M3／交通服务，13次请求与13份完整响应后自然stop；首卡内容连续，两条不同Route的详情、真实388×260地图、滚动和返回通过，第一路线首组与末组已实际查看。没有手改生成稿或注入修稿观察；中间地图组未逐图采样，本轮没有滴滴报价结果、未确认目标或下单，不认证细语义、全部候选动作或完整守护。原件 `build/research/journey-guardian/current-online-23/result-safe.json`，发布附件 `qualification-ui.json`。该轮累计229 calls／12,981,059 tokens，全停。

较早online7曾在真实循环完成条件替代、父确认与goal v2保存，期限和预算保持，整程费用／站内衔接未知未被认证。online11另有普通出行自动保存和冷重开的证据。它们证明各自记录版本及条件，不能补足0.16.1完整守护v1／v2尚未覆盖的部分；版本和原件见[验收历史](qualification-history.md)。

仍须解决或验证：

- 完整守护需实际走完准备方案、父确认保存目标、变化后前台重新核验、替代差异、拒绝或确认、目标版本与持久化恢复。新用例应明确自然守护意图，不指定工具顺序或成功路线；目标期限和预算不能在途中改写。
- 模型曾把已查区间小计／时刻提升为整程价格／T3到达及预算期限满足，并虚构票价、误读用时或一票制。机械投影精简已落地，但没有认证这些语义缺陷消失；正确动态详情不能抵消静态卡片或提案错误。详情来源文字也有缺失记录，按当前实际输出核对。
- harness与验收须区分实际用户可见render、父提案、无tool_calls自然结束内容和诊断reasoning；online16／17曾被错误提前中止，不算用户结果语义FAIL。旧JSON夹具曾掩盖原生标识符键差异，包预检或render success不能代替真实异步回执和可见控件。
- 新运行先核当前包挂载、source／binary身份、Android样式、空出行与单业务VM；online20隔离状态曾缺Navigation挂载，不能复制旧包制造可用状态。模型恢复、工具取消、跨出行状态及错误后详情身份需按真实触发核对，复用未受影响的既有证据。
- 布局问题优先区分生成稿使用、工具／技能合同和宿主引擎语义。旧wrap连续Fill与natural根Fill已取得单变量证据；不据旧失败直接改全局布局引擎，不手改模型稿冒充自主修正。

完整完成依据是同一明确用例中的实际操作、Route依据、父目标确认与版本、持久化读回及手机UI相互一致；如失败，保留原件并限定下一步判别，不自动新开付费整轮追绿。原生验收为macOS Apple Silicon宿主的Android样式，不是Android真机；没有后台监听、自动下单、全局最优或准时保证。

## 当前责任与下一步

| Owner | 当前责任与返回要求 |
| --- | --- |
| root | 整合授权、取舍、源码owner与运行槽，采用实际证据；决定必要修复、版本更新及外部交付。 |
| guardian_interaction | 唯一修改main及UI／guardian技能，落实本地`emit action:propose_goal`，复用同名Agent工具的`guardian_propose`准备pending；返回必要边界检查与封包前身份。 |
| guardian_qualification | 待统一封包后，真实验证v1→位置变化→recheck→v2→冷恢复；先给具体用例、版本身份与范围，区分新鲜规划、隔离回放和历史恢复，失败保留原件并全停自有实例。 |
| layout_decision | 只读判断布局／harness问题的因果及最小改动；实现由root指定稳定owner，不将使用约束直接升级为全局引擎变更。 |
| submission_packet | 仅整理本packet与现有验收历史，本轮不改README、应用源码或Git提交。 |

已采纳的下一修复切片是本地`emit action:propose_goal`：直接复用同名Agent工具的`guardian_propose`准备pending，父应用仍须真实确认才保存目标。它不自动选择方案、不续聊，也不为旧`propose_with_id`添加别名兼容。该切片已实现并通过10/10原生定点：真实生成按钮→待确认→父确认保存v1，替代准备不写盘→父确认v2；非法Route/缺参/忙/历史/旧稿明确失败，保留合法pending。旧修订为dispatcher定点，其余合法操作实际点击；0模型/供应商，全停。证据`build/smoke/navigation-harness-q50id3ky/report.json`。smoke临时安装目录过滤的竞态也作窄修。

root已采用实现并统一0.16.2check/build通过，source `0fbaf642`、main `c00bac0a`、bundle `e8223804`；运行槽交guardian_qualification完成真实v1→位置变化→recheck→v2→冷恢复，本地通过不提前认证真实闭环。harness保持机械合同、LLM保留语义权威；修复不影响的协议、保存事务、同窗恢复、浮层与第二consumer检查不重复跑，不为小措辞做统计矩阵，也不提前宣称完整任务成功。

当前没有新增待用户决定事项。若实施中出现实质范围变化、缺少用户特定资料或外部发布授权，再呈现最小待决定事项；继续改进本身不重复询问。

## 恢复与知识入口

逐轮原始失败、修复、账本、封包及证据引用归[验收历史](qualification-history.md)；范围解释的单变量判别与未投入生产的假设归[范围解释调查](scope-explanation-findings.md)。原始模型／工具／生成源码、私有状态和日志仍在忽略的 `build/`，不进入Git或bundle；缺失usage仍未知，不记为零。

长期产品与技术知识仍归README、docs/architecture.md和相应任务，不在本入口复制源码可维护的合同。当前任务尚未完成，不因0.16.1已提交或focused UI通过而关闭。
