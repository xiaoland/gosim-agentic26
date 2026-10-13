# 决赛前目标守护与原生 UI 交付

## 目标、授权与截止时间

用户要求继续完成验收，并提醒 **2026-10-14 08:00 冻结决赛版本**。最新同时要求改善正在退化的 UI/UX。已授权必要实现、修复、真实 M3 与供应商验证、文档更新；不再请求同范围审核。主 Agent 负责整合，以 GPT-6.1-Sol medium/low 委派稳定 owner。保留既有无关修改，不覆盖初赛 v0.13.0，不读取新的个人数据、不下单、不提交上游 PR。

当前收紧为：解决影响实际交付的模型请求失败、候选解释与手机交互缺陷，然后整理可复现版本和资料。暂停新能力、组件库扩展、全量地图翻页、旧测试矩阵及统计性重复。保持自主 function-calling loop、渐进技能、自由 Makepad/Splash DSL；不新增固定业务模板、文本一致性拦截或静默重写生成稿。

## 已完成与剩余目标

- 独立 native-ui 包的第二个非出行 consumer 已由真实 M3 读取技能并生成 UI，通过列表、详情、更新、返回和重新打开交互。SDK3975fe7f／prelude2280b462；27 请求／26 回执，21稿，不声称首稿稳定性。证据见历史记录和 build/research/native-ui-notes-model。
- online7 完成广州→宝安入口的真实条件守护闭环：自主公交＋S4837＋步行、详情地图、父确认、磁盘 goal v2。三段已查估价57元、入口16:29、目标18:41／200元保持；站内连接、设施通达和整程费用未知。仅 macOS Android 样式，不是真机或保证可登乘。
- 仍需改善候选静态解释、提案依据与手机比较体验。online9 动态详情正确，但静态文本将局部到达升级为整程到达，详情标题硬写另一 Route ID。正确事实完整进入模型，不能归因于技能未读取。

## 当前恢复点

online10 已在17:01:24全停。唯一VM1／query1、10次模型派发／8次成功响应、18工具对；原合成目标20:34:24／200元／已花0保持，goal仍v1。当前真实用量账本 **61 calls／3,169,262 tokens**，两次超时没有返回usage，不能算作零。

本轮首次失败后，真实“继续规划”成功，同窗口保留原消息，不重放17对已完成工具，证明恢复身份修复在线有效。首份5区块原稿约12KB，详情有未闭合括号；诊断已返回同M3，但修稿请求再次失败，暂无可用新界面。提案把170分钟误写成70，并有无来源的一票制断言；未确认保存，不能称整轮通过。原件、截图、完整消息和停机证据在 build/research/journey-guardian/current-online-10。

**最新硬证据：两次失败均为 HTTP 状态行等待超时，分别120.626秒／120.158秒，未收到HTTP状态码。** 宿主日志保留 Network Error/status line/timed out；complete HTTP固定120秒，model.chat非流式，外层等待130秒。请求体约274KB／318KB。长上下文或生成导致慢属于可能解释，没有服务端计时，不可叫已证实5xx、429或余额问题。

## 当前责任与下一步

- presentation_advisor：已建议仅model.chat HTTP300秒、bridge310秒，普通HTTP120秒不变；root采纳，300秒不保证远端完成。
- layout_diagnosis：已完成chat专属300秒、外层310秒与父确认区折叠。宿主定点6项、原生折叠11项通过，最后封包已全停。只有Navigation overlay补丁／tree更新，RC6 commit和其他锁保持。以真实pending对象身份区分同版本新提案。
- guardian_qualification：online10-ui-recovery已完成并全停。3次真实M3响应分别215.697／126.576／18.929秒，前两次超过旧120秒；真实渲染诊断回同M3后自主修稿，五块初始化成功。原始source未手改，原交通未重查。当前只读追查“一票制”、局部到达升级为整程及53分钟余量的最早形成位置，提出最小工具／技能改进，不占native槽。
- layout_diagnosis：继续独占native槽，复用恢复实验原稿和真实facts做无模型、无交通的详情布局定位与必要修复。实际route1_4详情返回／地图翻页／地图rect均为零，地图HTTP虽ready25989B但无像素，长滚动仍不可达；第二Route未覆盖。必须保留原稿，诊断变体不冒充模型成功。
- root：维护本packet、整合证据、查看真实截图，更新README与listing，最后处理冻结状态。

计划：先消除实际返回与地图不可见的确定性故障，并处理候选事实表述的最小根因。复用已有原稿，避免再跑整套交通／模型实验。必要修复后只做相关手机交互与模型验证，随后整理冻结版本；不扩展组件库、不重复旧矩阵。

恢复实验也将170分钟写对，但仍有“一票制”、整程便宜及53分钟期限余量等无依据结论，不能称语义通过。最新账本64 calls／3,440,448 tokens，增加3次／271,186 tokens；两次旧超时usage仍未知。证据在online10-ui-recovery/interaction-safe.json、allstop-safe.json，root已查看comparison-top.png与route14-detail-ready.png，确认界面泄露原始Route ID和内部指令、详情控件不可达。
## 冻结前取舍

首个query回执已包含正确费用覆盖、到达范围和unknown评估，但模型在首次解释时即升级为整程成立，之后出现170→70及虚构一票制，比较回执在该错误之后才到达。因此不将问题归因为技能读取失败，也不将后期动态详情正确当作修复。经独立判断，本轮停止首次query投影／提示词试错：其收益尚未证明，改动会触及接驳探索所需steps与节点合同。保留现有权威评估与父确认，明确自由解释仍有准确性局限。未来有判别力的实验应从首次错误之前的原请求做单变量投影对比，而非继续承接已错误锚定的对话。精确时序和原件索引见[范围解释调查](scope-explanation-findings.md)。

## 详情布局定点结果

原稿声明viewport、根Fill，却没有内部滚动；横排NavSurface仍为默认Fill。隔离三变体证明：仅改natural与rootFit恢复地图可达，但返回及下一段仍零面积；横排Surface改Fit后返回63×48、翻页76×48、地图388×220均可达。不是宿主渲染缺陷，不修改运行时或静默改写模型稿。layout-kwq7bhlr原native报告保存全部变体，0M3／0交通查询。layout-nhkys032仅对原route_1_4发一次静态地图HTTP，25989字节ready且实际有像素，已全停。root查看截图；它是布局探针，父控件透出及地图小图等现象仍不能称可交付UI通过。

最后只替换既有schema中viewport的歧义说明、澄清横排Surface尺寸合同，不增加固定模板。已完成check/stamp/build/doctor，最终main ce18256a／source 1386c068／binary 6e4eb95c／bundle 875d407f；宿主与SDK锁未变。完整回执online10-detail-layout/preflight-safe.json。

online10-ui-continuation唯一响应耗时282.809秒成功，M3自主改为独立候选卡片＋ScrollYView详情；实际renderer拒绝整批，route_detail:91:13 unclosed {。旧界面保留，新双Route／返回／地图未覆盖；该实验已全停。账本65calls／3,564,055tokens（+1／123,607）。完整消息和实际tool错误已保存，未手改DSL。

root调整收尾判断：成功assistant带tool_calls却在可修复语法错误处人为结束，不构成正常agent loop闭环。复用既有adapter、已保存真实错误与原冻结state做明确标注的新隔离续生成，正常read/render自修到自然stop或真实provider失败；不新增风格要求、不重查交通、不写目标、不手修源码。guardian_qualification继续独占native/provider槽，原单响应实验FAIL不改写。

## 当前实现与版本

已完成两项窄修改：
1. comparison_route_index改为用途白名单，全部候选保留身份、范围、三个显示标签、费用和assessment；完整get_route、snapshot、持久化和原比较计算不变。online9真实数据原生5/5通过，比较回执6620→2804B。一次真实单变量回放改变了模型行动，但没有propose，故未覆盖basis准确性。
2. 已有presentation_task和native-ui产品段改为手机先比较交通组合、费用覆盖、到达范围和关键未知，完整分段／来源／地图归详情。没有加固定模板或组件；online10原轮因语法错误后超时失败；隔离恢复已自主修稿，但实际手机比较与详情仍未通过。

前一封包：main1c7d42f5／source8f2ef984／binarya3310c4b／bundle568da435，check/stamp/build/doctor通过。回执chat-timeout-300/preflight-safe.json明确chat300/310、普通HTTP120、无新增retry/fallback。原生折叠实测main86040c83，最终仅将cancel重绘移到原run失效后；7个模型响应／续接函数对online10逐字未改，不冒所有旧矩阵重验。

root已查看折叠／展开实际图；unknown仍可见，完整正文与确认可达。bundle/listing.json中的持久化旧事实及0.13 release notes已改，并已包含在本次封包；截图仍准确标为0.13来源。README同步同窗继续和父提案展开语义。

## 冻结时完成

- 按真实结果更新README，明确核心闭环、解释和UI的独立证据边界；候选图只使用实际运行且root查看过的截图。
- bundle最后编辑后运行make check、make agent-build、make agent-doctor，记录最终main/source/binary/bundle摘要；只补当前改动必要检查。
- 仅提交获授权任务改动，保留私有日志、密钥、build和无关修改边界；不覆盖v0.13.0。最终记录提交SHA、可复现入口与实际局限。
- 不为赶冻结新建Hub发布workflow。当前Hub只接受GitHub attestation；publisher-prepare会改manifest并封包，后续不能继续restamp。外部发布按相应授权执行。
- 10月14日08:00使用用户最新时限；历史官方10月9日冻结资料不能用来否定新通知，尚未核新的官方时限。

## 证据入口

本轮证据均在 build/research/journey-guardian 下：
- current-online-7/result-safe.json：条件核心闭环。
- current-online-9/result-safe.json：静态范围与标题错误。
- compare-purpose-probe/preflight-safe.json：比较投影机械合同。
- online9-comparison-counterfactual/result-safe.json：单变量回放未覆盖。
- mobile-comparison-objective/preflight-safe.json：手机比较目标封包。
- current-online-10/result-safe.json、allstop-safe.json：恢复通过、呈现失败与两次超时。

此前修复、各次精确版本和未完成范围保留在[验收历史](qualification-history.md)；长期产品与架构归README和docs/architecture.md。本packet只维护当前工作，不以旧通过替代当前结果。
