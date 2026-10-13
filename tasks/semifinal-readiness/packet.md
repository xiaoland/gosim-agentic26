# 决赛前目标守护与原生 UI 交付

## 目标、授权与冻结时间

用户要求继续完成验收，改善退化的 UI/UX，并提醒 **2026-10-14 08:00 冻结决赛版本**。最新明确要求“继续完成完整验收，同时改进IA（字体大小有问题）”，授权本轮必要默认字体、信息标签、技能资料及相关代码修复，随后真实全链验收。已授权必要源码修复、真实 M3／供应商验证及自主提交推送。主 Agent 整合，以 GPT-6.1-Sol medium/low 委派稳定 owner；保留初赛 v0.13.0、不读取新个人数据、不下单、不提交上游 PR。

冻结前优先处理视频中一眼可见的请求失败、手机交互和空白内容；不为放大检查的费用措辞或算术细节扩大验收。保持自主 function-calling loop、渐进技能和自由 Splash DSL，不增加固定业务模板、文本拦截、静默改写生成稿、组件库扩展或重复旧测试矩阵。用户明确无需我们制作视频。

## 当前源码与交付

已推送的最新提交为 `d1d80fb`，包含工具回执精简、渐进技能资料、字体信息层级和原生界面语法修正。其交互通过不代表解释准确性或完整全链通过；当前只收尾影响手机演示直观效果的问题。

当前候选封包在 `online19-card-layout-ui/receipt-safe.json` 记录：source `c1349ebb`／main `af40ad3e`／binary `32beddf0`／bundle `94026d78`，check/stamp/build/doctor 通过。正文16／Meta14／通用标题22／主出行标题18可两行；滴滴采用供应商当前有效优惠价。宿主 RC6、SDK与锁未变，模型HTTP300秒／桥310秒，普通HTTP120秒。新的聚焦 UI replay 尚未完成；这些封包检查不代表它通过。

模型原始回复、技能回执、工具调用、源码和实际错误均保留在忽略的build目录；密钥、私有日志及状态不进入Git或应用包。online19自然结束后账本 **182 calls／9,806,261 tokens**，该轮20次回复的usage均已计入。历史轮次缺失usage仍未知，不能算零；聚焦UI回放如发生模型调用则另计。

## 已得到的证据与局限

- online7完成广州→宝安官方入口的真实条件守护闭环：M3自主建立公交＋S4837＋步行，查看同Route详情与地图，经父确认保存goal v2。已查估价57元，合成18:41期限／200元预算保持；站内连接、内部通达与整程费用未知。
- 独立native-ui包第二consumer由真实M3按需读技能并生成列表、详情、更新、返回和重开，未手改原稿。经历21稿／27请求，不声称首稿稳定性；SDK3975fe7f／prelude2280b462，证据归build/research/native-ui-notes-model。
- online10真实“继续规划”保留同窗原消息，不重放17对已完成工具。两次HTTP失败精确发生于120.626／120.158秒。模型专属等待修复后实际响应有215.697／126.576／282.809秒，证明旧120秒会截断这些生成，不保证远端总能完成。
- 父提案由整段长文改为可展开确认，费用／到达范围与关键未知仍可见；真实pending对象变更使新提案重新折叠。原生11项通过，确认仍走原事务与版本判断。
- 首批M3稿误用viewport无内部滚动及横排默认Fill，定点变体分别定位；只澄清既有工具／技能合同。后续正常read/render循环保留真实语法错误，由M3自主修稿，安装独立候选卡片与ScrollYView详情。两条不同Route卡片→正确详情→返回实测通过；未改模型源码，未重查交通。
- 新合法ScrollYView仍只露27px地图，根因是父浮层对请求height892加顶部margin后仍以892测量，实际剩余540。共享block_height改为按剩余可见区域约束浮层显示高度，保存的请求height／DSL和inline行为不变。原M3稿逐字3775320c…验证完整388×220地图与真实返回；定点11项通过。该单详情探针父壳透出，不能当完整产品UI通过。
- 所有原生验收为macOS宿主Android样式412×892，不是Android真机。没有后台监听、自动下单或准时保证。

事实解释仍未通过：首次query已经完整提供全程金额nil、已查小计、目的地到达未知及unknown评估，M3仍升级为整程满足，之后出现170→70、虚构一票制和已查终点53分钟余量。后期动态详情正确不能抵消静态解释错误。详情来源文字也仍缺失。

前轮曾因冻结节奏停止未证实的query投影／提示词试错；最新完整验收授权下可按新证据继续必要修复，但不能凭缩短回执宣称语义已修复。已有request36保留为首接触单变量判别入口，晚期错误锚定回放不具备同样区分力。精确时序、原件索引与实验边界见[范围解释调查](scope-explanation-findings.md)。

## 本轮完整验收结果与下一步

IA源码定点已通过，root已查看实际字体图；完整成本／basis／unknown结构不变，不手改原M3稿。正式fresh普通规划current-online-11于20:18:50.755开始，绝对deadline2026-10-14 01:18:50.755、预算200／已花0／无进度，空trip／模型历史／DSL／候选；模型及高德／12306／滴滴均真实。

首轮20/20真实响应于约20:23自然stop，未resume或中止。真实技能全文、供应商、渲染诊断完整进入同一loop。新字号、两候选详情／首末地图／返回实测通过；生产自动保存completed记录及8个区块，冷重开逐字readback相等，0query／0dispatch、账本不变。原／冷实例、mock采样流均已全停。

仍未通过：总结把unknown费用／到达提升为预算／期限满足，将“未拆分不表示未包含”推为已含城际票价。旧报告曾将采用165优惠价判为资格未知；用户明确优惠绝对可用且无资格要求，该失败判断已撤销。详情泄露内部Route ID且缺来源时间。完整守护v1/v2尚未覆盖。

原输入只要求规划与比较，没有持续守护／准备确认意图；普通trip正确保存，无propose_goal不单独算Agent/harness故障。父应用首次普通结果转为守护目标的发现性入口是独立产品缺口，本轮暂不扩该入口。下一案例使用自然明确意图“准备方案供我确认保存目标，确认后在前台核验时守护期限和预算，未核事项保留”，不规定工具或流程、不指定成功路线。

采纳最小有证据契约改进：
- 高德cost.basis及相应技能去双重否定，直接“本次供应商查询区间报价；各分段票价及包含关系未知，无法确认是否包含城际车票”；原报价不变、不自动加铁路票价。
- 用户明确“滴滴优惠价是绝对可用的，不需要任何资格”，因此按平台返回优惠价选有效报价。原MCP普通177／优惠165；现price_text/price_cents采用165／16500，base_price_text/base_price_cents保177／17700对照。旧discount_applicability:unknown方案与资格假设彻底撤销，旧quote-scope receipt只作历史，不作为当前barrier。无优惠用普通价；有优惠但无法精确解析时按金额未知，不拿原价冒充有效价。生产附价只替换指定taxi腿，不叠加或改旧Route。报价仍是当前估价，不认证未来实付或上下车连接。
- 定点合同通过不抵消模型语义失败；新完整case必须实际验证。旧request36保留作首接触判别入口。

首次明确守护在线案例current-online-12在21:37:23启动后暴露机械错误：输入的“预算200元”后再次自然提到“守护期限和预算”，旧解析要求全句恰好出现一次“预算”，于是到达约束成为0且提案失败。M3当时确实尝试了`propose_goal`，不能据此判成缺守护意图；10个已完成回复后停机，原失败日志完整保留。layout_diagnosis已修复重复语词，同金额合并、冲突金额／币种拒绝；普通无效约束在trip／模型前给出可见原因，守护重核仍使用已锁定的期限和预算。原生9/9、封包检查通过，全停释放native槽。此修复不改写online12的失败和旧deadline0。

新鲜current-online-13于22:33:50实际启动，期限锁定10月14日03:33:50，200元／300分钟约束正确。11个完整M3响应自然结束，模型真实调用供应商、读取技能并提出pending。首次query结果已有整程金额与目的地到达nil、期限和预算unknown，但随后首响应就把已查170分钟当全程“远在期限内”，又猜缺失票价；最终总结和父确认理由沿用这一判断。父确认上方虽保留unknown，下方仍有矛盾理由，故**语义验收FAIL，未代用户点击确认，v1/v2未运行**。另一独立缺陷：最终Routes稿顶层一次读取`snapshot().routes`，磁盘事实有两条且segment完整，实际界面却无详情Button；渲染成功回执不能代替可见入口。实际截图、请求、工具事实和原稿保留在`current-online-13/`。本轮新增11 calls／554,435 tokens，累计110／6,672,962；全停后槽释放。后续反事实与原生对照见下，不把首轮猜测当成根因。

首接触单变量回放把原`query_route`的Route保值重排为请求目标unknown与已查场景170分钟／500分，原请求其它消息、schema与模型设置逐值相同。官方宿主一次真实M3回复仍称“两条完整路线、5小时内、低于200元”，并猜城际票价40–70元；故**分组投影假设FAIL，不投入生产**。累计111 calls／6,698,711 tokens，回放无业务工具执行、无目标变更。随后回到原请求，只内联现有navigation-data技能正文，作为独立隔离实验；没有伪造read_skill或立即改生产。

内联navigation-data全文的单变量首响应仍在推理中把已查170分钟称为整程期限内，猜总价40–80元；累计112 calls／6,726,168 tokens。再以原请求仅将Route顶层泛称`duration_seconds`改名`queried_scenario_duration_seconds`，同值与其它事实不变，首响应仍说“费用很低、时间内”，并猜未报价打车超200元；累计113 calls／6,751,681 tokens。这三项反事实都只有一轮模型响应、未执行后续工具、未变目标；均为FAIL，此方向停止采样，不能把技能或字段重排当作已证修复。用户明确要求改进harness时以删除、精确化为主，保持“harness机械、LLM语义权威”；现在改查真实工具说明与回执中的重复/歧义，而非加禁令、正文校验或固定编排。

只读harness审查发现首次`query_route`实际回执含两Route的`legs`/`steps`完整明细，已经可由`get_route(id)`按需取得。原回执18125B；仅删两Route这些重复键后11943B，缩短6182B（34.1%），其余查询事实及30个`new_nodes`逐值不变。第四个且最后一个首接触反事实中，M3首次明确区分已查终点与真实目的地，自主请求`get_route`；但仍将01:51与03:33先后说反，整体语义**FAIL**。累计114 calls／6,775,098 tokens。这个观察支持删重复数据以减负，不支持准确性已解决；不再重复反事实采样。后续生产精简仅触及query回执边界，保持get_route完整明细与其它调用者。

精简现已落地：仅`query_route`模型回执删`legs/steps`，完整`get_route`、旧query_transit/driving、扩展/铁路/守护及内部Route计算不变；工具说明精确指向按需详情，未增加固定调用顺序。用online13原tool原件做原生回执对照，摘要减少34.1%，其余Route字段/new_nodes逐值一致；既有合同11项及包封检查通过。新鲜真实M3完整案例正在该新barrier上启动，不能用反事实首响应或定点检查替代。

online14新鲜运行于23:21:31启动，300分钟／200元和源码/二进制摘要核验正确，但实际`query_route`公交及打车回执在模型request50中仍带完整`legs/steps`。真实call45/47不是旧别名，说明上述原生同步fixture未覆盖生产异步batch路径，**精简效果验收FAIL，停止该轮语义验收**。6次模型dispatch中5次完整回复，账本累计120 calls／6,929,096 tokens；末请求usage未知。没有用户确认目标，全部实例已停。原生探针确认：原生摘要对象的枚举键为标识符，旧JSON fixture的键为字符串，旧代码直接与字符串`"legs"`/`"steps"`比较使生产删减永不命中；不是异步闭包丢失name。修复在共享投影里先将键转字符串再比较，默认和`to_ref`两条query路径共用；旧版同真实异步测试关键项FAIL、新版6/6 PASS，check/stamp/build/doctor通过并全停。online14原失败原件保留；online15新鲜真实请求才可确认线上已生效。

online15新鲜请求已证实真实公交查询11112B、打车查询3251B，首回执确实删掉`legs/steps`，M3也自主两次`get_route`补读详情。但assistant60首次把供应商“分段票价包含未知”改述为仅算首段，并无来源地补城际票价45–50元和整程50–60元；语义**FAIL**，未确认目标，v1/v2未覆盖。模型首错前还收到两份`get_route`回执13372/14296B，以及此前`search_places`20个POI的14456B、`adopt_destination`5336B、`read_skill(native-ui)`7589B。当前账本127 calls／7,107,102 tokens，最后请求usage未知，全停。本轮已证明仅删query重复明细不足；用户质疑我们前期只审首回执、未盘整条实际上下文以及JSON fixture假绿，事实成立。后续暂停在线试错与视频交付，分别审查工具回执的全链负担和skills渐进披露，以删除/精确化为主，保持harness机械、LLM语义权威。

UI初查推翻“首次snapshot尚未绑定”的猜测：终稿包装源码已有两Route各5段。原生日志另有旧稿的`pop_stack_resolved on empty stack`与`on_render closure failed; discarding its output`，后续对照证明不能归到最终Routes稿；最终render成功回执对应执行结果，也不证明生成了详情入口。

进一步原生对照确认最终Routes稿没有Button的直接原因是Splash的`?`为错误传播后缀，原稿按C三元表达式计算的计数实际为`false`，两路线分支均未执行；对照合法`if/else`后暴露另一个`View{flow:Right wrap:true}`错误，正确形式为`flow:Flow.Right{wrap:true}`时两个Button出现。早期StackError属于旧详情稿，不能归到最终Routes的render回执。layout_diagnosis只在原有Makepad语法资料和技能目录增补两个实际语法点，未改原M3稿、宿主或模板；资源入口、check/stamp/build/doctor通过，新source `dc658c49`／binary `6a23f4aa`，新M3生成尚未验收，原online13卡片FAIL保留。

用户随后明确本轮不用制作视频。已生成的剪辑与逐镜索引移至忽略的`build/finals-video/exports/`保留，不纳Git或本轮交付；收尾集中在应用、harness和真实验收。

当前责任：
- harness_surface已交实际回执重复字段分析，layout_diagnosis完成query回执删重及原生封包；LLM保留语义判断，工具不裁决自由文案。
- guardian_qualification完成online15真实删重验证后因首次语义冲突全停；不继续补v1/v2。
- harness_surface只读盘点模型首次误读前全部工具回执、schema及按需恢复路径，重点补齐search_places/adopt_destination/skills，不再只审query。
- skill_architecture独立核对Agent Skills规范和matt-skills原始资料，精简native-ui入口与reference的渐进披露；仅拥有native-ui技能目录/catalog对应条目。
- layout_diagnosis只读检查搜索/采用/查询/详情的生产投影与调用者，待整体审查后负责main及原生边界检查。
- layout_diagnosis已修复原生键比较并覆盖默认及`to_ref`回执，原生6/6、check/stamp/build/doctor通过，全部本任务实例关闭后交槽。
- finals_video已完成的素材依用户新指示仅留本地忽略目录，不作为交付。
- root维护README／packet、采用实际截图与诊断、继续必要修复和完整验收，不以旧恢复交互替代新的任务效果。

继续复用不受本轮修复影响的协议、保存事务、同窗恢复、浮层、第二consumer证据；不重复旧矩阵。模拟GPS按真实时间采样仅刷新公开mock观测，不能续交通证据寿命或移动已启动案例deadline。

全链只读审查已补齐首错前11份工具回执共74,196B，模型请求体在第53次达132,956B。除已精简query外，主要重复来自search_places候选完整入口、adopt_destination重复上下文与节点、query_route新增节点、get_route与segments重复的顶层steps；约14KB的首批减法仍是估算，不能当语义修复。native-ui技能入口已由7,428B精简到3,098B，详情示例移入直接可读引用，隔离物化与目录测试通过；真实read_skill及M3效果待验证。官方Agent Skills规范没有7.6KB字节硬上限，但建议渐进披露。layout_diagnosis负责四处模型回执投影和原生测试，保持POI/Route内部事实及UI历史不变；harness_surface继续只读核对系统提示词、工具schema和领域技能有无重复或误导。冻结前只接受保留决策事实且可按需恢复的机械减法，不添加结论校验或固定路线流程。

投影已完成并封包：source `ce70a7fd`、binary `001449dd`、bundle `787cd573`，check/stamp/build/doctor与原生四处7/7、真实异步query两路径6/6通过，全部本任务原生实例停止。以online15同场景重放，search_places 14,456→10,331B，adopt_destination 5,337→2,087B，query_route 11,112→9,291B，两次get_route 13,372→11,252B和14,296→12,059B；合计减少约13.6KB。选定POI入口、节点坐标和来源经真实get_route_graph selector读回，旧历史仅steps和地图目录保持。工具description的“完整”范围歧义已消除，navigation-data技能合同同步；这些是机械精简，**未认证M3语义改善**。原生证据见`online15-tool-projection/receipt-safe.json`。

online16首次真实验证已证实五个技能及四份引用进入模型后续请求，地点采用前误调用工具后M3自行修复，首路线解释正确区分已查区间与整程未知。验收负责人在第六次回复的内部reasoning里见到错误预算判断便停机，但正文仅表示继续查铁路，实际工具也继续查票；尚无render、propose或final。advisor复核后将本轮更正为**人为提前中止、用户结果未覆盖**，保留旧判断原件但不算本版语义FAIL。证据`current-online-16/result-safe.json`及`qualification-correction-safe.md`。同封包fresh online17又因将带5个tool_calls的assistant.content误判为用户可见文本而提前停机；源码实际仅在无tool_calls的自然结束分支将content写入answer_text，故本轮也**用户结果未覆盖**。已纠正验收判据为实际render、propose_goal父提案、无tool_calls自然结束的最终内容或真实不可逆动作；中间reasoning和content只作诊断。安排online18自然运行，不注入纠正、不代确认。

online18完成真实工具探索并生成父待确认提案，但提案推荐理由把¥5的未知包含关系说成“仅地铁段”，又凭没有来源的“公开价目”断言全程低于预算与期限余量；真实Route全程金额nil，提案未由用户确认，语义FAIL。随后模型多次render失败，实际手机屏幕只有父提案文字，没有候选卡片或地图；render错误包括draw_bg类型、文本内部引号提前闭合造成的中文裸变量，以及根View少一个闭合括号。用户最新要求先放下不会影响演示直观效果的缺陷，因此冻结该细微费用措辞调查，转而优先解决**候选/详情/地图缺失和页面可读性**。online18原始证据、截图与全停账本见`current-online-18/result-safe.json`（156 calls／7,989,955 tokens，最后请求usage未知）。

UI资料已按实际已读内容收紧：native-ui入口3,261B、宿主参考19,278B，地图合同完整移至入口直链的6,537B按需引用；typed `draw_bg`、内部引号和根View闭合的最短边界前置，删除重复/复杂可选动画示例。通用Splash语法入口和参考也改为短正例。online18实际技能回执与模型请求逐字一致，故不是传输截断；原生三种合法正控与三个原稿失败负控6/6，目录物化、check/stamp/build/doctor通过，全停。新资料source `18dbeb77`、binary `34638471`、bundle `be0beb14`，证据见`online18-syntax/receipt-safe.json`。这些只证明资料和语法，不证明新M3会成功生成。guardian_qualification现用已保留的真实Route事实及首路线几何做隔离M3 UI定点验收；第二路线缺原始折线，不伪造地图。验收优先两卡、两详情身份、首路线地图和返回。

隔离M3 UI定点已自然结束并全停：原online18的55条模型历史和真实Route事实逐值保留，只增加隔离UI任务与新版技能，未预装旧DSL，未重查交通/写目标。M3实际读取七份新技能/引用后首稿render_routes与render_route_detail均原生成功，两卡可点、两详情绑定各自Route，A首末两组真实地图388×240及返回通过。首稿B因原几何未保全，缺图文字下面残留A旧像素；同存活VM收到该实际观察后，M3自主提交第二详情稿，A→B缺图隐藏→A首末地图恢复→返回实测通过。B地图原始折线未保全，**未覆盖**，不伪造补线。截图与逐字生成稿索引见`online18-ui-recovery/result-safe.json`；本实验6次M3实际调用、683,210 tokens，累计162 calls／8,673,165 tokens，全停。此定点证明资料修改后界面交互可用，不改online18真实提案语义FAIL，也不认证新鲜完整E2E或卡片内容准确；生成卡片仍有无来源估价，不能作为费用事实演示。后续冻结优先整理交付、提交推送，不再为小措辞追模型绿。

online19 在已推送 `d1d80fb` 上以空出行、真实 M3／高德／12306／滴滴运行至自然结束，20/20 回复完整；前两张 Route 卡能打开各自详情，route2 首末地图、route5 首图和返回实测通过。第⑥滴滴卡把 `didi-quote:30` 当 Route id 发给 `view_route`，宿主只显示错误却保留上一次公交 route5 的详情；点击后出现错误路线，是明确演示阻塞。第⑥卡源码包含报价、用时和风险，屏幕却只有标题与大片空白。未代用户确认目标、未下单；原件、截图与全停记录见 `current-online-19/result-safe.json`。

这两个可见故障已分别有机械因果与窄修：无效 `view_route` 清空选择并关闭当前路线详情；标记 `render_route_detail` 的用途，未选合法Route时详情待开，合法选择后再显示，保留 `show_block→view_route` 与反序两种按钮动作。原生点击对照含旧详情泄漏、修后隐藏、错误后恢复、返回与自定义详情id，见 `quote-detail-identity/receipt-safe.json`；工具回执与技能同时说明报价ref不是Route id，只有 `attach_quote` 返回的新Route可查看。第⑥卡的原稿、单卡均复现大空白；将其三个 `Flow.Right{wrap:true}` 多行容器改为 `flow:Down` 后七段文字同屏，单纯将所有Label宽度改为Fit会截断长说明。原生差分见 `card-layout-repro/comparison-safe.json`。因此只在native-ui技能加一条该宿主Android样式布局限制，不改模型原稿、固定卡片模板或上游宿主。两项修复及封包已通过本地检查。一次复用online19事实的隔离UI回放在模型调用前被旧私有夹具挂载格式挡住，按短界限全停、0新增模型调用；不能声称新M3已采纳布局资料。待演示时以首两张已验证路线和地图为主，不把第⑥卡的旧截图当成修复后效果。

## 证据入口

本轮证据均在build/research/journey-guardian：
- current-online-7/result-safe.json：真实条件守护闭环。
- current-online-9/result-safe.json：范围／标题错误；compare-purpose-probe与online9-comparison-counterfactual保留比较投影机械检查和未覆盖的单变量结果。
- current-online-10/result-safe.json、allstop-safe.json：同窗恢复通过、两次120秒超时与呈现失败。
- online10-ui-recovery/interaction-safe.json：延长等待、自主语法修稿、原详情零尺寸。
- online10-ui-continuation/interaction-safe.json：单响应后语法失败，原件保持。
- online10-ui-repair-loop/interaction-safe.json、viewport-evidence-safe.json：正常自修后双Route返回通过，地图27px裁切。
- online10-detail-layout/overlay-preflight-safe.json及layout-mrau8_t4/report.json：最终封包、原稿完整地图与浮层尺寸定点证据。
- online10-overlay-trip-qualification/interaction-safe.json、allstop-safe.json：前轮正式父壳双Route完整地图／返回／无重叠通过。
- online10-detail-layout/font-ia-preflight-safe.json：IA与字号封包／原生定点。
- current-online-11/result-safe.json、diagnosis-safe.md：新IA真实普通规划／三供应商／首末图／生产冷恢复、包含误读首源与意图索引；其中优惠资格旧判断已被用户新事实撤销，原件不篡改。
- online10-detail-layout/discount-effective-preflight-safe.json：当前有效165／原价177、附价派生及原值保持、无资格门槛，包含未知直接事实。
- current-online-12/failure-safe.json、allstop-safe.json：明确守护在线失败；重复“预算”导致本轮没有有效期限，M3已调用提案但不能确认。
- online10-detail-layout/limits-preflight-safe.json：重复语词修复、普通失败前置可见反馈与守护锁定约束的最终封包。
- current-online-13/：新鲜11响应、合理意图触发pending，但首次范围误读、确认文案矛盾及方案详情入口缺失，保留截图与私有原始trace；后续安全索引另补。
- online13-first-contact-counterfactual/result-safe.json：官方M3一请求、原Route保值分组，仍有整程范围误读与虚构票价，假设失败。
- online13-first-contact-skill-counterfactual/result-safe.json：原首接触仅内联既有技能正文仍误读。
- online13-first-contact-duration-counterfactual/result-safe.json：原首接触仅改泛称耗时键仍误读。
- online13-first-contact-reduced-counterfactual/result-safe.json：仅删重复legs/steps使回执减34.1%，模型开始主动取详情但时间判断仍错误，语义FAIL。
- online13-query-projection/receipt-safe.json：query回执生产精简、完整详情保留及原生/构建封包。
- current-online-14/result-safe.json：实际生产query_route回执仍含legs/steps，旧fixture的JSON键掩盖原生标识符键比较错误，模型轮次停在首个确定失败。
- online14-query-projection/receipt-safe.json：原生键修复、真实异步批次和默认/to_ref查询两路径原生检查及最终封包。
- current-online-15/result-safe.json、response-size-safe.json：真实query删重已生效，但两次大详情和早期地点回执仍增重，模型仍猜缺失票价；全停且未确认目标。
- online13-render-diagnosis/receipt-safe.json：卡片缺失实际Splash语法因果与最小资料修正封包，未冒新M3通过。


早期证据见[验收历史](qualification-history.md)，长期产品与技术归README和docs/architecture.md。历史通过仅证明其记录版本与条件；本packet维护当前冻结恢复点。
