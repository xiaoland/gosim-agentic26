# Agent 生成耗时与失败诊断

状态：2026-10-06，0.11.4已修复0.11.3全候选目录重算导致的挂起，并分离工具结果提交与日志／UI副作用；挂起边界和分图共十四项定向检查、默认可运行回归及唯一封装通过。没有新增正常M3验收，生成语法与完整界面可靠性仍未通过；保留本任务作为接续入口。

## 目标与授权

用当前实例实际轨迹解释耗时与失败：模型输入规模与请求等待、工具查询与计算、界面生成修正、原生渲染，以及开发诊断自身开销。对照必须明确版本、输入、服务与运行条件，不能将主观变慢当成已测性能回归。

诊断阶段只读；用户随后明确要求“开始修正”，授权上述已查问题的必要源码、测试和说明更新。当前用户实例不重启、不关闭、不注入；调查阶段不新请求模型或地图服务；修复验证先用隔离原生检查，之后仅一轮有明确目的的正常M3验收。不将原始位置／模型内容或凭据纳入Git。0.11.1修复及证据归[查询交付任务](../query-delivery/packet.md)。

## 责任与判别

UI稳定owner取得当前启动／实例／run对应的模型、工具、渲染、宿主记录，报告实际时序、错误及记录缺口。native稳定owner检查0.11.1前后调用控制流、数据与诊断开销，必要有界隔离实验；不重复导出当前实例。根整合因果与改善建议。

先确认当前确实运行0.11.1，记录完整并来自可见实例。按每次准备／派发／响应、工具开始／结果、生成稿／诊断／终端分段计算，不将缺记录当成功或供应商慢。明确失败是服务返回、模型生成语法／API、预算／heap、显示或记录中止。已有样本不足公平前后比较时，说明可证瓶颈和不能证明的变化。

## 已采用证据

根已读 `build/research/query-performance/result-safe.json`、`timing-safe.json`及`native-analysis-safe.json`。当前main260c727e…确为0.11.1，Android模式、可见vm-2，导出458个连续事件、8段；run3只观察到search_places调用开始，不判终态失败，不继续尾随。未操作用户实例或新增服务请求。

| 实际轮次 | 总耗时 | 模型派发至响应合计 | 工具合计 | 模型调用数 |
| --- | --- | --- | --- | --- |
| run1 | 96.08秒 | 90.24秒 | 4.24秒 | 12 |
| run2 | 83.70秒 | 80.13秒 | 2.41秒 | 9 |

派发至响应是客户端观察等待，包含网络、提供方和回调排队，不能独立当成模型推理时间。prepared到dispatch约19–28毫秒，但不覆盖之前全部构建或记录成本。主要墙钟等待在模型往返，不支持把本次主耗时归诊断IO。

run1实际正文由5941B增长到519326B，prompt由1817增长到130960tokens；工具结果约89%是完整facts。run2增长到266747B／66455tokens，完整facts约78%。同一候选、站点、前缀等反复回传并留在全部消息历史；render_ui每次还返回约71–83KB完整facts。观察到的工具结果没有polyline字段，不归因完整几何。0.11.1没有改模型提示、工具、传输或循环；0.11新增图状态和工具扩大了旧有重复快照问题。没有公平同条件新旧样本，不量化版本退化或去重后秒数。

run1三个生成请求24.24／16.18／16.07秒，前两份真实XML式／原生语法失败，第三份执行成功但无地图与按钮，不算完整任务。run2一稿生成43.36秒／3423输出tokens，实际通知seq393到达，seq394读到未定义变量错误而拒绝成功，晚通知修复正确工作，不是通知漏锁。

新查询还有确定性状态污染：start_task清poi_records却没有清picker_pois。run2首个模型消息含上一轮20个地点、约10.6KB，第一次adopt_destination确实引用其中旧地点，被本轮记录拒绝；随后还出现缺起终点的交通查询和修正。这是内存中的跨轮状态残留，不是模型历史恢复或业务文件持久化。

同启动日志有父VM heap allocation limit exceeded：refresh_generated_facts复制约55049B的Label文字时仅剩12431B，后续JSON及回调属性分配也不足，出现继发prototype等错误。日志没有逐行时间，不能精确把每个heap错误绑定run3或证明内存泄漏；本轮没有script time budget exceeded证据。工具完整字符串、decisions结果对象、界面facts及诊断序列化可形成多份副本，尚未量化各自占用，不能单独归罪trace或宣称精简输入就修好了堆不足。

## 决定与下一步

Advisor建议先修独立查询地点残留与本地交付故障，再整理工具数据边界。模型工具结果与原生snapshot应从同一业务状态派生不同投影：工具返回本次新增记录、比较及具体错误，render只返回本稿诊断、通知和视口；不每次附整图／全facts。实际候选和详情保持可按ID取得，不截候选、不设输出上限、不固定调用顺序、不强制技能、不新增内容校验器。UI语法错误与堆副本生命周期分别诊断，不能以提高宿主预算或盲抽模型掩盖。

用户已授权实施。先离线确认同轨迹重复字节减少与必要事实可取得，并用实际原生边界验证内存和交付；当前不能承诺提速倍数。


## 实施与验收计划

UI稳定owner拥有main.splash及必要技能资料，修独立查询地点状态、模型工具数据投影、实际保留副本与完整界面事实传递。native稳定owner负责堆副本生命周期判别及tools/smoke.py本轮性能检查入口；该测试文件职责暂从UI移交，避免同时修改。根维护版本、README／architecture、packet与整合；最终封装只执行一次。当前guides/delegation.md不存在，按已有稳定owner接续，不复制其它仓库方法。

验收用同真实轨迹或其必要代表数据核对模型请求字节下降、原决策事实与完整候选可按ID取得，Android隔离宿主验证连续独立查询无旧地点、完整详情／地图数据可访问、无变化刷新不产生重复事实更新，以及实际多轮模型／界面事实保留的堆边界。生成语法资料仅对实际错误修正，不加固定流程、强制skill、预制业务UI、输出上限或内容validator。不得以提高宿主配额或关诊断掩盖问题。

不操作用户实例，不新增模型／地图盲抽样；若进一步真实验收有明确必要，先向根说明辨别目标。原始运行材料只在私有ignored目录，公开检查不得包含用户位置或模型原文。


模型结果已改为本次新增记录／候选摘要与完整计算原因，增加按ID读取路线和读取本轮图；render回执仅诊断、通知状态和视口。保留UI snapshot全部路线、分段、图、报价目录。Advisor确认本轮不整体删UI字段：模型按需工具不等于原生动态访问，让Agent再把目录写进源码会转移输出与转录成本，并破坏变化通知。

native源级判别显示Label脚本绑定在控件同文判等前已经分配并记账，临时对象释放后计账要等GC reconcile；isolate轮转回收和slot触发条件不能保证55KB复制前及时回收。所以根因不等于Label永久泄漏。实施采用业务revision在序列化前跳过、子界面轮询小revision、decisions去结果副本；不修改原生内存配额或GC实现。开始新轮还清active_tool与旧calls，避免跨轮回调保留旧对象。


根已读 `build/research/query-performance/repair-result-safe.json`，性能7项与相邻晚通知5项通过，同main224cf5ce…，技能native_ui54481fb6…／navigation_data9c3e23dc…冻结。同组合成记录旧请求262683B→新38779B，减少85.24%，不是原真实run1重放或tokens测量。完整snapshot70140B保留所有候选、几何／路线与图读取，30修订产生31次写入、100无变化不重复写，原生错误0；独立新轮清旧地点／预览／工具参数，增量起终节点实际入口成立。根看相邻late-success实际Android截图。早期fixture调用model_task_context提前初始化图导致节点检查失败，改夹具顺序而非应用，不算通过。自有实例关闭，无用户操作／服务。

根决定补一轮正常M3验收：本次工具结果契约改变，合成量化不能证明模型能实际消化和完成展示。使用唯一最终0.11.2封装，在隔离Android模式宿主、明确公开demo位置和独立日历／笔记来源跑原句，真实模型和出行服务、无额外编排指令／手挂稿／强制skill。只一轮，不失败再抽；保实际消息体积、耗时、错误和输出。它只验证新接口语义和实际交付，不公平量化前后提速或普遍成功率。UI稳定owner负责，native仅最终包核对，根整合。


根已读唯一最终封装 `build/research/query-performance/final-package/result-safe.json`：0.11.2 check／build／doctor通过，main224cf5ce…、sourcec285bbac…、runtime9ab83326…；10文件embedded／mounted逐字节一致，两技能材料化一致，自有loopback实例关闭，宿主patch trees不变。这不替代下面正常M3验收。

## 正常查询结果与接续边界

根已读 `build/research/query-performance/normal-final/result-safe.json` 并查看实际 `android-result.png` 和 `android-after-view.png`。唯一正常查询使用公开演示地点宝安大仟里及独立日历／机票笔记，真实M3、高德和滴滴服务，在macOS宿主Android模式运行，不是Android真机或用户实际定位。原句查询耗时56.009秒，9次模型调用均HTTP 200；最后请求98690B／24500输入tokens。首次render_ui执行无诊断并收到成功通知，未观察到堆／预算错误；get_route实际两次成功。不同位置和调用轨迹不能据此与此前96／84秒计算提速比例或成功率。

执行成功不代表界面正确。生成根容器使用Overlay，使三个直接兄弟控件的标题、推荐和列表文字重叠；按钮处理器还查找五个没有构造的控件，实际点击报widget not found，没有进入路线详情。生成稿没有原生地图控件。曾有两次set_constraints失败和一次attach_quote缺少混合前缀失败，均是实际工具错误，未隐藏或伪装成功。原始模型轨迹与宿主日志只保存在ignored证据目录；自有实例已关闭，没有手改生成稿、附加模型抽样或操作用户实例。

Advisor建议交付有证据的性能与状态修复，保留失败稿继续调查生成布局和控件引用；盲抽至成功、追加禁令或手改样本不能证明生成交互问题解决。此轮不修改原生预算、固定UI或增加输出校验，也不恢复此前暂停的地图工作。后续从上述失败稿的Overlay兄弟布局和缺失控件引用开始，区分模型可用资料、实际控件构造与交互执行证据，再确定必要改动；不能将本轮标记为完整查询交付验收通过。

用户随后反馈：“这次确实有包含地图，但是地图没有能显示出来”。这是用户新轮的观察，不与上面公开demo的缺地图稿混为一谈。UI稳定owner正在只读匹配当前可见实例的生成稿、地图事件、请求／响应与原生诊断；不点击、重启或注入用户实例，不新增外部请求。先定位未挂载、未派发、服务失败或图片安装失败的实际边界，本次反馈先授权调查，不预先宣称地图被省略或修改源码。

用户进一步明确同轮“全程打车”地图可以渲染、“打车+公共交通”失败并报20003。高德[官方错误码](https://lbs.amap.com/api/webservice/guide/tools/info)定义20003为UNKNOWN_ERROR，不能单靠错误码认定缺参数、配额或无权限。[静态图规范](https://lbs.amap.com/api/webservice/guide/api/staticmaps)限定paths最多四个折线／多边形；当前源码保留不相接的全部分段，所以需对照两候选实际请求的paths数量、参数与响应，尚未证明这是本轮根因。

根已读 `build/research/map-20003/result-safe.json`：用户当前0.11.2／vm-2／run1的284事件，与公开demo不同。真实AutoNaviMapView和view_route／map／camera事件均执行。失败候选内部kind为public_transit（用户界面称混合），请求12条paths／514点／13341B，HTTP200返回56B的UNKNOWN_ERROR／20003，重复请求亦失败，没有图像提交。成功打车候选3条paths／657点／16524B，HTTP200返回39948B图片并accepted=true，后续缩放成功。两者相同端点标记、372×240／scale1、显式location／zoom和参数键，失败请求反而更短；没有堆／预算或render诊断，不支持归因UI省略、无camera或单纯URL长度。

失败请求明确违反四条折线契约；20003仍不能证明这是服务端唯一原因。12条之间11处真实缺口约0.30–28.27米，不能截前四条或强行跨缺口连接。调查曾建议原生overlay解耦底图与路线；用户随后选择“将这个限制告诉 agent，并且提示 agent 可以分步嵌入多个地图”，当前按用户方向实施，不引入原生overlay。

UI稳定owner负责技能资料与必要的最小地图事件能力，让Agent知道每张地图最多四条独立折线，并能选择同一完整路线中的分段分别展示；完整路线事实不删减，由Agent决定张数、步骤和布局。仅写多图提示不足以解决现有每个地图都请求全路线的问题，需要核对并补足实际分段选择契约。系统提示不扩写，不预制业务UI，不新增强制分组、候选截断或跨缺口补线。必要定向隔离Android模式验证由同owner完成；根维护文档、版本与封装整合。用户实例不操作，不追加M3抽样或无目的地图调用。

当前采用map事件可选path_indices；不传仍兼容完整路线，不由宿主自动分组或加最多四条输出校验。按实际map_geometry最终折线索引选择，get_route及UI snapshot提供全部索引／端点／点数目录，而非新增polyline全文副本。分图按所选完整折线取景，标记如采用子集首末点须注明是本图分段端点，非全行程起终点。0.11.3版本已准备，最终摘要与封装待应用和定向检查冻结后由native稳定owner唯一执行。

首个定向夹具采用六条不相接折线分两图，以覆盖大于四条和同批多图边界。原生Android模式中两slot已注册／loading，但只有第二图camera／ready；夹具过早假定第一图ready而出现nil断言，不能记为通过。owner正在核对同批fit延迟闭包实参是否重复引用最后slot；必要公共边界修复属于用户多图方向的实现范围，不加重试兜底或扩大服务调用。

后续证据排除该闭包猜测：两个fit实参不同，两图均实际绘制372×160，但mailbox仅第二图事件。native只读源码确认子emit对Label的异步读改写会丢同批事件：两callback先排mailbox.text getter，各读同旧串，后排set_text由最后写覆盖。原生camera按实例独立，不需要Rust修复。UI采用子VM脚本mailbox_buffer同步追加，再写Label，原来的父消费／查询代际机制不变；不靠延迟或重试。源码判别入口为Makepad image.rs的camera回调及widget_async.rs的回调优先pump和异步text／set_text队列。

根已读取 `build/research/map-sections/result-safe.json` 与 `build/smoke/navigation-harness-jmgq90xe/report.json`，并查看实际Android模式截图。main2f42bc78…冻结，七项定向检查通过：六条不相接折线按[0,1,2]和[3,4,5]分两图，全部原折线逐条一致、目录端点／点数准确、默认不自动截断、分段A/B含义明确、独立camera／加载、同目标改索引重新取景及不存在索引明确失败。截图使用明确标注的蓝／橙合成图片，验证原生控件与事件链路，不是供应商地图。此次实测六条分两图，不是先前计划的十二条分三图；覆盖同一超四条与同批多图边界，未为数字另做重复检查。自有实例已关闭，无新模型或出行服务请求；没有证明M3会每次采用分图资料。一次隔离启动曾remote404，未进入夹具，不算检查通过。最终封装正在由native稳定owner执行。

根已读取 `build/research/map-split/final-package/result-safe.json`：唯一0.11.3 check／build／doctor通过，source15c9de6e…、main2f42bc78…、runtime63c95db1…、binary40a4971d…；嵌入与实际挂载10文件逐字节一致、两技能材料化一致，锁定宿主覆盖树未变。自有隐藏loopback已关闭，未操作用户实例或复跑UI／模型／服务。当前获授权分图能力已完成；接续仅需在用户正常查询中观察Agent采用资料与实际分图表现，既有生成布局／失效控件问题仍按此前证据保留，不能把这次检查宣称为完整出行界面验收。

## 当前恢复点：两次查询停在正在处理

用户反馈两次正常尝试一直“正在处理”，要求参考Pi Agent的function calling harness与现代agent loop，质疑当前实现仍不够简化。先调查实际停点与官方Pi源级实现，不加提示词补丁、不将主观等待直接归因模型或界面。UI稳定owner只读当前可见实例的两轮时序和宿主错误；pi_loop_reference拥有官方固定版本源码对照，核工具完成、错误／终止／取消与UI生命周期边界，不重复导出用户实例。根整合证据后决定必要修复；不引入Node运行时、外部harness服务或新持久化作为预设答案，不操作用户实例或追加模型抽样。原始材料继续只放ignored build。

根已读 `build/research/agent-loop-stall/result-safe.json`，当前0.11.3／vm-5的625个事件完整：run1全部12次模型调用返回，45.57秒进入render_ui，seq219调用／220源码后没有render或tool结果，约355秒后用户终止。宿主指令超限IP位于父route_point；native源确认每入口200000指令的硬Bail展开根栈，普通try不能捕获。render_source后mount同步interface_facts→全部routefacts→新map_path_catalog→map_geometry逐点计算，child安装及回执timer还未执行，因此显示busy没有控制后继。IP不证明route_point是唯一成本，但调用链及断点吻合上轮新目录重算回归。run3的22工具均有结果，十次render中前七次原生API／变量错误，126.24秒结束；只读截图与可见Label证明当前已显示结果／查询按钮。生成源码内嵌旧runtime_status并非可见文案，不能声称两轮都仍卡住。日志缺逐事件时间，不能精确复原用户两个观察时刻。

Pi官方badlogic/pi-mono重定向earendil-works/pi，本次固定commit[28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9](https://github.com/earendil-works/pi/commit/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9)。[agent-loop](https://github.com/earendil-works/pi/blob/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9/packages/agent/src/agent-loop.ts)同样保存assistant与tool批、取得结果后继续、无tool结束；Navigation已是该基本形态。值得采用的是[agent生命周期](https://github.com/earendil-works/pi/blob/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9/packages/agent/src/agent.ts)统一结算及控制状态先于UI事件处理；Pi finally自身也不能令永不settle的工具或原生硬Bail凭空返回。当前不移植Pi Node运行时，不切其Anthropic MiniMax endpoint，也不引入steering、follow-up或持久化。

Advisor与native建议修已证根因并小范围解耦，不重写loop。依用户此前“开始修正”的性能与可靠性授权，UI稳定owner实现0.11.4：UI快照只引用按get_route首次构建并缓存的目录，未读取nil明确含义；普通地图仍可直接加载完整真实路线。合法tool结果先序列化、提交消息和索引，再安排下一控制入口；日志／UI更新移独立入口，结束／取消先清busy。不得提前续轮却缺对应结果，不把未挂载稿误报成功，也不加超时看门狗、硬步数或固定流程。验证首次mount无全候选扫描、单candidate冷读实际代表负载与副作用失败不阻断已提交结果续轮。若原失败几何未被记录，不冒称真实重放；不新增模型或地图抽样。native稳定owner仍负责唯一最终封装，根整合说明。

根已读 `build/research/agent-loop-stall/repair-result-safe.json`，并查看两份实际Android模式截图：final mainb5cc2e3c…下挂起边界七项与既有分图七项通过。首次mount保16候选且几何扫描0；657点代表真实路线cold get_route只扫描该候选一次，warm复用，其余目录nil。诊断／facts副作用故障注入后两个对应tool_call_id均先提交，续轮到terminal；终端和取消先clear busy。日志五个nil.failure为刻意注入，不是自然宿主回归，没有指令／时间／堆超限。几何取自此前私有map-20003已存taxi请求，与本轮get_route目录657点规模一致；本轮原始全候选几何未记录，不能精确重放原run1。未知更长单候选仍可能触宿主真实单入口预算，不预设分批框架、裁数据或保证所有未来数据。没有新模型或服务请求，自有实例关闭，生成语法问题仍独立保留。

根已读取唯一0.11.4 `build/research/agent-loop-stall/final-package/result-safe.json`：check／build／doctor通过，source311bd34c…、mainb5cc2e3c…、runtime01a5ce8b…、binary565cfd9e…；10文件嵌入／实际挂载逐字节一致、技能材料化一致，宿主覆盖树未变，自有隐藏loopback关闭。源码包摘要不包含smoke工具。整合时发现回归入口硬依赖ignored私有几何，已让UI仅调整工具：默认公开合成657点、显式选项读取私有代表数据，禁止把用户几何提交或自动调用服务；这一必要可运行性检查不重新构建应用。

根已读 `build/research/agent-loop-stall/portable-test-safe.json` 与qjusm76a报告，默认 `python3 tools/smoke.py --loop-settle` 使用三条公开合成折线、每条219点，七项通过；显式 `--loop-settle --loop-settle-private-replay` 才读取本机既有私有代表数据，缺数据明确失败，不自动服务回退。工具SHAe5680b8a…，产品和技能仍同冻结摘要，私有检查未重跑，不重新封装。当前修复交付完成，后续正常查询仍需区分实际循环挂起与生成稿自修导致的长等待，不能把126秒已结束样本当持续busy，也不宣称所有未来原生预算或生成质量问题已消除。
