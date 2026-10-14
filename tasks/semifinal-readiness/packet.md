# 已提交版本后的完整守护验收与界面改进

## 目标、授权与边界

继续完成出行目标守护的完整验收，并按实际失败改善手机 UI／UX、IA 和 harness。用户此前明确要求“继续完成完整验收，同时改进IA（字体大小有问题）”；本轮必要源码修复、真实 M3／供应商验证及自主提交推送已有授权。

2026-10-14，用户重新确认还可继续改进，因此此前“08:00冻结”不再作为当前工作的硬停止条件。已发布的 `v0.16.1` 保持不可变；后续源码与交付变化使用新的版本，不移动初赛 `v0.13.0` 或已发布标签。公开赛程与用户本次工作安排分开记录，不自行宣布赛事方已接受新评审版本。

保持自主 function-calling loop、渐进技能和自由 Splash DSL；harness 负责机械合同，LLM 保留语义判断。不增加固定业务模板、文本拦截、静默改写生成稿或固定成功路线，不为当前任务扩组件库、后台监听或新能力。真实模型与交通验证使用隔离状态；不读取新个人数据、不下单、不提交上游 PR。用户自行制作视频，本任务不再制作视频。

## 当前冻结提交

用户最新授权：“注意冻结代码并更新comment，14:00截止”。应用源码冻结在09c6f9e23b6683cd9ab5ba0b474df915a990730b，标签v0.16.3不可移动，14:00后不继续修改本次冻结代码。Release v0.16.3与既有#116/comment-6151741694已于13:56公开更新；匿名下载ZIP摘要f7feefe8与固定Git42文件核对通过。最终交付归build/submission/final-09c6f9e；仅README/本packet随后同步发布事实，bundle、tools、toolchain保持冻结。旧v0.16.1保持不变，视频继续引用其用户正确资产。

## 此前已提交版本

`0.16.1` 已公开提交：[Release v0.16.1](https://github.com/xiaoland/gosim-agentic26/releases/tag/v0.16.1)与[App Hub #116](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/116)。固定源码为 `c47929b23942e0f61de90e109c1034fab8e06463`；它与 `369cf70` 的 bundle 逐字相同，应用 source SHA256 `409553b9`、bundle BLAKE3 `df5b79e0`。之后的工作不能将这份已发布证据改写为新版本结果。

06:00一次性审计已更新 #116 的标题与正文当前Version，保留初赛历史；匿名访问视频与ZIP均HTTP 200，实际下载摘要通过，ZIP的42个文件与固定源码逐字一致。视频资产为 `final-v1.mp4`，104.367秒；正确视频、ZIP和证据的完整摘要归 `build/submission/audit-0600/result-safe.json`，最终交付原件归 `build/submission/final-c47929b/`。

配套 `--navigation-check --allow-unsigned` 通过；标准 `hub scan` 因 contained apps 未提供 `notes.search` 而 REFUSED，未生成扫描包。Hub尚未上架，也没有0.16.1的新赛事方验收回应。正式Hub审批还缺GitHub-attested workflow、pack、receipt与下载后publisher验证；不为得到绿色检查而删除实际使用的Notes授权。来源审计见 `build/submission/audit-20261014-0600/audit.md`，扫描边界调查见 `build/submission/candidate-229101c/scan-investigation.md`。

## 最新验收及未解决问题

已验收的0.16.3封包固定在`1fb22a7`，source `2dbd68fc`、main `9306ee59`、bundle `73c604e8`、binary `66f3d9ee`，make check/build通过，实测固定身份归 `build/research/journey-guardian/current-online-26/result-safe.json`；build/agent/build.json为会变化的当前构建，不作为旧证据。通用约束原生14/14和必要来源／POI调用者3/3通过，无native错误；6个回执投影函数与已验收0.16.2逐字相同，复用既有证据而非重跑矩阵。online26已自然结束并全停，约束采用切片通过，UI未通过；当前未发布。技能显隐资料的后续补充不属于这份已测封包。

**online26通过约束采用切片。** 19/19真实响应自然stop，初始constraints／limits／deadline为空，M3实际采用120分钟／10000分／CNY，basis注明用户时限预算和来自城市的币种推断。期限严格为固定received_at＋7200秒，adopt_destination后约束逐值不变；旧v2目标逐值保持，新出行goal为nil、没有确认。该轮只覆盖相对时限，不覆盖真实模型对绝对“下午”钟面日期的采用、完整规划UI或可行性。原件`build/research/journey-guardian/current-online-26/result-safe.json`，状态`PASS_CONSTRAINT_ADOPTION_SLICE`，严格归`1fb22a7`／source `2dbd68fc`／main `9306ee59`；新增19 calls／986,678 tokens，本日累计78／4,943,131，usage完整、实例全停。

**online26的UI不是PASS。** 生成详情在首次事实回调中用`viewed_route_id != nil`判断选中，将实际空串当作有选择，主动发show_block；没有用户点击或view_route事件，实际浮层自行展开。定点因果和原稿归`current-online-26/ui-side-finding-safe.json`。owner仅补技能中的空串、首次广播及显隐不等于路线选择的合同，不改runtime、不手改生成稿；root查看实际截图后确认错误浮层覆盖主结果，因此限定一次局部UI再生成判别，复用原请求与事实、只更新实际已读合同，不重开交通规划。效果未通过详情交付验证：同次CF自然续接只生成四区块，首卡可选合法Route但详情目标未安装。

**online25通过条件替代保存与冷恢复。** 使用online24已经真实父确认的v1记录作donor，在0.16.2固定源码 `c33bebe8a11d58aa6e8b3886e7a47497ce431fe9`（source `6d628190`、main `62789ef1`、bundle `42fdaaf4`）冷恢复后，以广州南公开mock新位置和新时间戳启动一次新的前台重核；不加载旧模型消息。真实M3／供应商12/12响应后自然stop，渲染语法错误由模型自行修复，实际回调结算且未再触发堆错误。提案与推荐绑定同一条新塘公交Route；父界面展开保留整程费用、目的地到达和可行性unknown，测试读取条件后才确认保存v2。原16:11:18期限、200元预算、已花0、目的地及原用户偏好／风险约定保持；v2磁盘和冷启goal逐值相等，冷启0query／0dispatch、账本不变，root已查看v2冷恢复截图。原件 `build/research/journey-guardian/current-online-25/result-safe.json`，状态 `PASS_CONDITIONAL_REPLACEMENT_SAVE_AND_COLD_RESTORE`；新增12 calls／597,083 tokens，本日累计59／3,956,453，全部自有实例已停。

这是online24前一源码版本的v1＋当前修复版本新重核v2的接续证据，不是一轮、同版从零完整可行性的证明。新Route已查小计11元、已查最早场景约214分钟，整程费用与目的地到达未知；估算性自由文字未经全量认证。摘要曾把原57元估价说成已花／余额143，父权威支出0／余额200及保存值仍正确。原风险约定按既有目标合同保留，不能声称模型的新风险文字静默替换用户同意；没有新个人数据、下单或Android真机验证。online24的堆失败、错误提案绑定与修复负控保留于[验收历史](qualification-history.md)，不被online25通过覆盖。

**online23只通过新鲜手机UI验收。** 空出行、正常挂载入口、真实M3／交通服务，13次请求与13份完整响应后自然stop；首卡内容连续，两条不同Route的详情、真实388×260地图、滚动和返回通过，第一路线首组与末组已实际查看。没有手改生成稿或注入修稿观察；中间地图组未逐图采样，本轮没有滴滴报价结果、未确认目标或下单，不认证细语义、全部候选动作或完整守护。原件 `build/research/journey-guardian/current-online-23/result-safe.json`，发布附件 `qualification-ui.json`。该轮累计229 calls／12,981,059 tokens，全停。

较早online7曾在真实循环完成条件替代、父确认与goal v2保存，期限和预算保持，整程费用／站内衔接未知未被认证。online11另有普通出行自动保存和冷重开的证据。它们证明各自记录版本及条件，与本次online24→25的接续证据分开；版本和原件见[验收历史](qualification-history.md)。

仍须解决或验证：

- 条件提案→确认v1→位置变化→新前台重核→条件确认v2→冷恢复已获得跨修复版本的实际证据。尚未认证同一最终版本从零完成全部环节、替代拒绝或全部候选动作、真实个人进度及费用；按下一切片影响选择必要验收，不重跑旧矩阵。
- 模型曾把已查区间小计／时刻提升为整程价格／T3到达及预算期限满足，并虚构票价、误读用时或一票制。机械投影精简已落地，但没有认证这些语义缺陷消失；正确动态详情不能抵消静态卡片或提案错误。详情来源文字也有缺失记录，按当前实际输出核对。
- 通用约束切片已实现并完成机械检查：demo／live的set_constraints接受模型解释，harness校验参数并以固定received_at换算；地点采用独立，初始limits／期限为nil，未设约束仍可读背景，计算型交通工具和提案返回缺项，已确认目标锁定。旧自然语言正则真值与demo票据裁决已移除。原生14项归`build/smoke/navigation-harness-09me1hwv/report.json`，来源／POI调用者3项归`build/smoke/navigation-harness-k_p__hil/report.json`；均0模型／供应商、无native错误。6个投影函数未改的身份归`build/research/constraints-adoption/projection-identity-safe.json`。online26另取得相对时限／中文数词预算采用的真实模型证据；绝对钟面分支仍只有原生对照，不把这一切片扩成任意表达或完整UI通过。
- harness与验收须区分实际用户可见render、父提案、无tool_calls自然结束内容和诊断reasoning；online16／17曾被错误提前中止，不算用户结果语义FAIL。旧JSON夹具曾掩盖原生标识符键差异，包预检或render success不能代替真实异步回执和可见控件。
- 新运行先核当前包挂载、source／binary身份、Android样式、空出行与单业务VM；online20隔离状态曾缺Navigation挂载，不能复制旧包制造可用状态。模型恢复、工具取消、跨出行状态及错误后详情身份需按真实触发核对，复用未受影响的既有证据。
- 布局问题优先区分生成稿使用、工具／技能合同和宿主引擎语义。旧wrap连续Fill与natural根Fill已取得单变量证据；不据旧失败直接改全局布局引擎，不手改模型稿冒充自主修正。

完整完成依据是同一明确用例中的实际操作、Route依据、父目标确认与版本、持久化读回及手机UI相互一致；如失败，保留原件并限定下一步判别，不自动新开付费整轮追绿。原生验收为macOS Apple Silicon宿主的Android样式，不是Android真机；没有后台监听、自动下单、全局最优或准时保证。

## 当前责任与下一步

| Owner | 当前责任与返回要求 |
| --- | --- |
| root | 整合授权、取舍、源码owner与运行槽，采用实际证据；决定必要修复、版本更新及外部交付。 |
| guardian_interaction | 通用约束和UI合同精确化已完成；render模型回执已精简，保留内部执行状态、实际库存与未解决诊断，partial原生5项通过；无新增业务验证或补详情，已全停。 |
| guardian_qualification | online26约束采用PASS、UI问题原件与账本已导出全停；准备一次局部UI再生成判别，先核合同实际已读，同次CF实际57消息自然续接已结束全停，详情交付FAIL；当前不再启动模型，保留原稿/实际点击/广播证据。 |
| layout_decision | 只读判断布局／harness问题的因果及最小改动；实现由root指定稳定owner，不将使用约束直接升级为全局引擎变更。 |
| submission_packet | 整合本packet、验收历史、README和architecture的版本／验收／接口说明，准备必要发布材料建议；不改bundle、提交Git或外部Issue。 |

已交付的本地`emit action:propose_goal`：直接复用同名Agent工具的`guardian_propose`准备pending，父应用仍须真实确认才保存目标。它不自动选择方案、不续聊，也不为旧`propose_with_id`添加别名兼容。该切片已实现并通过10/10原生定点：真实生成按钮→待确认→父确认保存v1，替代准备不写盘→父确认v2；非法Route/缺参/忙/历史/旧稿明确失败，保留合法pending。旧修订为dispatcher定点，其余合法操作实际点击；0模型/供应商，全停。证据`build/smoke/navigation-harness-q50id3ky/report.json`。smoke临时安装目录过滤的竞态也作窄修。

本轮通用约束实现、机械检查、统一封包及单次相对时限真实模型验收已完成。UI技能资料已补准；同次CF自然续接2响应仅生成routes/suggestions，实际首卡选中route_2_1却没有详情区块，状态FAIL_DETAIL_DELIVERY_MISSING（online26-ui-contract-continuation/result-safe.json）。空选/返回重开未覆盖，原首CF仍UNCOVERED，均不改写。render模型回执已删重复成功标志与宽泛命名，保留真实初始化/库存/旧块诊断，partial原生5项通过，main ff01466a；最终check/build通过，当前source 1298597a、main ff01466a、bundle c59c59c8、binary 1a10ee00（build/agent/build.json）；真实模型约束证据仍归旧1fb22a7，不拼接为最终源码整轮验收。命名修正不被宣称是遗漏根因或UI已修好。下一必要工作是从真实完整呈现中继续定位详情交付遗漏，当前不为字段改名追加CF。本日81 calls／5,192,462 tokens，所有自有实例全停。已按14:00最新授权发布固定v0.16.3并更新原comment；各轮测试仍分版本，冻结包不是最终整轮UI通过。

本次外部更新已完成，不继续修改冻结源码。online25严格归0.16.2／c33bebe固定source，0.16.3的实现与当前单次验收单独记证据；已有Notes offer和GitHub-attested Hub审批缺口仍保留，外部交付由root后续决定。

当前没有新增待用户决定事项。若实施中出现实质范围变化、缺少用户特定资料或外部发布授权，再呈现最小待决定事项；继续改进本身不重复询问。

## 恢复与知识入口

逐轮原始失败、修复、账本、封包及证据引用归[验收历史](qualification-history.md)；范围解释的单变量判别与未投入生产的假设归[范围解释调查](scope-explanation-findings.md)。原始模型／工具／生成源码、私有状态和日志仍在忽略的 `build/`，不进入Git或bundle；缺失usage仍未知，不记为零。

长期产品与技术知识仍归README、docs/architecture.md和相应任务，不在本入口复制源码可维护的合同。当前任务尚未完成，不因0.16.1已提交或focused UI通过而关闭。
