# 决赛前目标守护与原生 UI 交付

## 目标、授权与冻结时间

用户要求继续完成验收，改善退化的 UI/UX，并提醒 **2026-10-14 08:00 冻结决赛版本**。已授权必要源码修复、真实 M3／供应商验证及自主提交推送。主 Agent 整合，以 GPT-6.1-Sol medium/low 委派稳定 owner；保留初赛 v0.13.0、不读取新个人数据、不下单、不提交上游 PR。

冻结前只处理影响交付的请求失败、手机交互与事实解释。保持自主 function-calling loop、渐进技能和自由 Splash DSL，不增加固定业务模板、文本拦截、静默改写生成稿、组件库扩展或重复旧测试矩阵。

## 当前源码与交付

候选 `08ac09a` 已推送 origin/main，包含固定 RC6、铁路、背景、守护、原生 UI 包及请求／布局合同修复。随后发现并修复真实浮层测量缺陷，必要验收已完成，本次提交推送收尾。

最新封包：main `0b4070e2`／source `9e2d03a8`／binary `f4902cb8`／bundle `a33ba985`。check、stamp、build、doctor通过；完整摘要见 build/research/journey-guardian/online10-detail-layout/overlay-preflight-safe.json。宿主 RC6、SDK与锁未变，模型HTTP300秒／桥310秒，普通HTTP120秒。

模型原始回复、技能回执、工具调用、源码和实际错误均保留在忽略的build目录；密钥、私有日志及状态不进入Git或应用包。当前账本 **68 calls／4,002,189 tokens**，旧两次超时usage未知，不能算零。

## 已得到的证据与局限

- online7完成广州→宝安官方入口的真实条件守护闭环：M3自主建立公交＋S4837＋步行，查看同Route详情与地图，经父确认保存goal v2。已查估价57元，合成18:41期限／200元预算保持；站内连接、内部通达与整程费用未知。
- 独立native-ui包第二consumer由真实M3按需读技能并生成列表、详情、更新、返回和重开，未手改原稿。经历21稿／27请求，不声称首稿稳定性；SDK3975fe7f／prelude2280b462，证据归build/research/native-ui-notes-model。
- online10真实“继续规划”保留同窗原消息，不重放17对已完成工具。两次HTTP失败精确发生于120.626／120.158秒。模型专属等待修复后实际响应有215.697／126.576／282.809秒，证明旧120秒会截断这些生成，不保证远端总能完成。
- 父提案由整段长文改为可展开确认，费用／到达范围与关键未知仍可见；真实pending对象变更使新提案重新折叠。原生11项通过，确认仍走原事务与版本判断。
- 首批M3稿误用viewport无内部滚动及横排默认Fill，定点变体分别定位；只澄清既有工具／技能合同。后续正常read/render循环保留真实语法错误，由M3自主修稿，安装独立候选卡片与ScrollYView详情。两条不同Route卡片→正确详情→返回实测通过；未改模型源码，未重查交通。
- 新合法ScrollYView仍只露27px地图，根因是父浮层对请求height892加顶部margin后仍以892测量，实际剩余540。共享block_height改为按剩余可见区域约束浮层显示高度，保存的请求height／DSL和inline行为不变。原M3稿逐字3775320c…验证完整388×220地图与真实返回；定点11项通过。该单详情探针父壳透出，不能当完整产品UI通过。
- 所有原生验收为macOS宿主Android样式412×892，不是Android真机。没有后台监听、自动下单或准时保证。

事实解释仍未通过：首次query已经完整提供全程金额nil、已查小计、目的地到达未知及unknown评估，M3仍升级为整程满足，之后出现170→70、虚构一票制和已查终点53分钟余量。后期动态详情正确不能抵消静态解释错误。详情来源文字也仍缺失。

冻结前停止未证实的query投影／提示词试错；改动可能影响接驳步骤和节点合同。未来仅从首次错误之前request36做单变量判别，而非继续错误锚定的晚期对话。精确时序、原件索引与实验边界见[范围解释调查](scope-explanation-findings.md)。

## 当前责任与收尾

- layout_diagnosis已完成浮层修复、实际原稿地图／返回与定点检查，封包后全停，源码交还root。
- guardian_qualification已完成最终正式trip恢复壳验收：原接受5块与最新卡片／详情原稿逐字安装，route_1_4（170分钟／小计5元）及route_1_3（162分钟／小计10元）卡→详情→同Route静态图完整388×220→返回均通过。父守护按钮底319、结果锚点328，无透出／重叠。仅验证首组真实paths[0,1,2,3]，不冒全部几何覆盖。0模型／0交通规划、目标未确认、账本不变，PID66401不存在、session删除、匹配实例为空；全停证据已保存。root已查看两张实际地图截图。
- root已查看实际截图，README与本packet同步交互通过及解释失败的独立边界。完成本次提交推送后保留当前候选；不再跑整套规划或旧矩阵，不新建Hub发布workflow，不覆盖初赛tag。

## 证据入口

本轮证据均在build/research/journey-guardian：
- current-online-7/result-safe.json：真实条件守护闭环。
- current-online-9/result-safe.json：范围／标题错误；compare-purpose-probe与online9-comparison-counterfactual保留比较投影机械检查和未覆盖的单变量结果。
- current-online-10/result-safe.json、allstop-safe.json：同窗恢复通过、两次120秒超时与呈现失败。
- online10-ui-recovery/interaction-safe.json：延长等待、自主语法修稿、原详情零尺寸。
- online10-ui-continuation/interaction-safe.json：单响应后语法失败，原件保持。
- online10-ui-repair-loop/interaction-safe.json、viewport-evidence-safe.json：正常自修后双Route返回通过，地图27px裁切。
- online10-detail-layout/overlay-preflight-safe.json及layout-mrau8_t4/report.json：最终封包、原稿完整地图与浮层尺寸定点证据。
- online10-overlay-trip-qualification/interaction-safe.json、allstop-safe.json：最终正式父壳双Route完整地图／返回／无重叠通过，最终封包与全停。

早期证据见[验收历史](qualification-history.md)，长期产品与技术归README和docs/architecture.md。历史通过仅证明其记录版本与条件；本packet维护当前冻结恢复点。
