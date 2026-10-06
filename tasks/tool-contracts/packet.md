# 查询、几何引用与区块工具契约

状态：2026-10-06，接口实现、定向检查与新稿封装完成；在线复验仍未完成详情与地图交付，不宣称完整验收通过。

## 用户目标与授权

用户建议合并query_transit／query_driving为mode参数工具，精简响应为duration、distance、cost、steps；地图几何自动以polyline_xxx引用复用；各区块分别作为渲染工具。用户特别说明这些只是对实现的假设，不要求机械照搬。授权必要调查、接口修改、技能／文档和定向验证，不改变单一Agent loop、模型或供应商，不引入固定workflow／预制卡片／持久化。

## 实际入口与判断

两个查询当前分别提供公交strategy和驾车出租车估价，返回同一个model_route_summary加新接驳节点。摘要有大量重复时效／校验字段，但没有完整折线；get_route和原生snapshot也移除了原始polyline。地图已通过路线target与path_indices从运行时几何cache取数据，LLM不必传原始折线。需要明确可复用引用而非重复建设存储框架；并核同批查询的route id碰撞，保证引用指向正确候选。

UI owner负责main.splash、两技能及必要smoke，先报告真实契约和最小方案再实现。Advisor判断mode语义、简化响应不能丢的未知项及来源、几何引用与分块工具粒度。根维护文档／版本、采用证据和本地提交，native最终封装。共享repo不撤他人修改。不得操作用户实例；在线验收使用独立测试实例，按实际失败选择修复／复核，不无限盲抽模型。

## 完成依据

统一查询调用可区分真实公交与出租车语义；响应可读、单位清楚、费用未知不等于零，详细依据可按需读取。几何引用自动生成，同批候选不撞ID，引用可用于现有地图并复用缓存，新查询清空。独立区块工具仍接受任意DSL，复用现有挂载／诊断，不能变成业务模板或自动必调顺序。macOS宿主Android模式做最小合成原生检查，模型采用情况另行报告。

## 已选方案

统一query_route的mode为transit／taxi，公交strategy可选且默认0；出租车使用原固定单路径高德查询，明确估价与候车未知。查询短响应包含稳定id、mode、实际duration_seconds／distance_m、带金额单位和依据的cost、短steps及必要assessment／source；get_route／compare保留详细依据。距离取供应商实际字段，不从重复几何猜测。steps此前未返回，不先宣称模型输入总量一定减少。

候选使用本次run单调唯一id并包含run归属；自动polyline_*引用直接解析已有候选的lazy几何cache，局部路径沿用实际索引。查询不遍历所有坐标，不新增几何注册表。新增render_summary／render_explanation／render_routes／render_suggestions／render_route_detail，各接任意DSL与可覆盖id／原生布局元数据，同类不限一个块。通用render_ui保留任意额外内容和整稿兼容，共用单引擎；不强制五工具或固定调用序列。

## 共享工作区衔接

实施前发现独立侧对话的技能目录／catalog迁移，入口tasks/skill-standardization/packet.md；其owner非本线程native。当前复用navigation-data/SKILL.md与native-ui/references/host-interface.md，保留迁移frontmatter、资料、构建工具和锁；本任务不回撤或认领它们。用户明确回复“侧对话已完成编辑”，可稳定复用新目录。功能实现继续；提交与封装须核双方实际边界，不能把另一任务变更静默混入当前提交。

## 最终接口与验证

用户澄清当前不需要Agent管理区块显隐。五个新render_*不曝光或读取visible；普通新块直接显示，详情先准备为隐藏页面，显示／返回由用户本地点击事件完成，已有块更新保当前页面状态。通用render_ui只保已有兼容，没有新增显隐需求。

最终main d8aac94adf335e24f86781a18bca4c4bba0ffafb930a80b93298d5f17d666bec。macOS宿主Android样式的十二项同源合成检查通过，覆盖同批查询唯一候选／跨轮引用、实际距离／价时／步骤／未知候车、未知报价、策略路由、几何查询惰性与cache引用、暴露工具、独立块更新、诊断修正、实际按钮打开／返回、清空，并包含新tools无visible及附带旧参数不改默认的判别。根已读安全报告并查看列表与详情实际截图；自有实例关闭，未触用户实例。

证据为ignored build/research/tool-contracts/result-safe.json及build/smoke/navigation-harness-jlhx42m1/report.json。最初两次失败分别是夹具缺source、地图shim调用不存在函数并有旧新VM竞写，已修夹具重跑同组，不把初轮断言通过当零错误。最终只出现故意注入的DrawQuad类型错误及对应修正回执。没有M3／供应商调用；地图用合成加载shim，仅验证引用／目标，不称真实底图或相机显示验收；steps新增，不宣称token总量减少或模型可靠性改善。

最终封装入口为build/research/tool-contracts/final-package/result-safe.json，检查完整当前bundle与新技能目录的实际嵌入／挂载字节。本任务不将侧对话已完成的技能迁移静默混入提交；当前共享工作区需要保持双方范围可追溯。

## 新增在线验收授权

用户明确补充“你的验收，总是可以使用M3在线服务，额度很充足，你可以进行完整的端到端验收，而不只是模拟”。这覆盖真实M3和业务服务验收，替换先前本轮不追加服务样本的边界；此前合成检查仍仅按原条件陈述。UI稳定owner先运行一轮当前harness完整原句，真实定位优先；如果实际定位失败，另行明确显式demo背景，不伪装为live，模型与交通仍真实。验收当前标准loop／统一查询／几何引用／五类DSL工具及实际UI交互，具体失败用于下一修复，不把接口存在当实际交付。

独立state与rawtrace放ignored build/research/tool-contracts/e2e，凭据／坐标不公开。当前main d8aac94a…，完整封装报告make check／agent-build／agent-doctor通过，31包文件embedded／mounted相同，23技能资源materialized相同，source1fd7a3f3…／runtimef88703f9…／binary458313d9…，自有封装实例已关闭。在线样本实际结果和可能源码变更须单独记录，不能沿用这份旧摘要冒称新稿。

在线首个驱动样本在TextInput中插入了重复任务句，initial_limits无法确定，因此不是原句验收。实时定位本身成功且CNY／非mock；该次十四模型请求和生成诊断只归错误输入，已要求隔离保留并排除，不能作为产品查询根因。owner改用默认原句，点击前读真实输入并核记录，再运行正确样本，未据此改产品源码。

正确原句的真实样本在49.81秒结束，八次M3请求均HTTP200，实时定位非mock。统一查询生成五个公交候选与一个出租车候选，五种渲染工具回执成功。但这不构成完整交付通过：模型仅生成文字列表，详情无可达入口、分段或地图，还在详情DSL根再次隐藏内容；地图工具根本未请求，不能归因于底图加载。它未继续探索混合接驳，错误声称已配置的滴滴未配置，并把最短公交约122分钟转述成95分钟。安全证据归build/research/tool-contracts/e2e/live-valid/e2e-result-safe.json及generated-contracts-safe.json；原始消息、坐标与源码仅保留在ignored私有目录。自有实例已关闭，未手动注入界面代替模型结果。

下一步由同一UI owner窄修：补非敏感的实际服务配置事实，查询摘要复用已有耗时／价格格式化；两项渲染工具说明可点击候选详情及不满足条件候选的查看价值，澄清父详情容器已负责初始隐藏；以简短混合出行目标替换重复目标说明。保留自由DSL和模型工具编排，不增加模板、强制调用、内容检查器或宿主保底。必要定向检查后用正常入口再做一轮真实端到端，验证实际工具选择、数值、点击／返回与地图；若仍失败，按实际证据报告模型交付边界，不盲加提示或抽样追成功。源码改变后必须重新封装，旧d8aac版本的包摘要不能用于新稿。

上述窄修已实施，main24c2e599cb0fa413af5bb9369f043179c66c2397243e88b1c121c917f0e4a031；同一十二项原生定向检查通过，加入格式化一致与服务状态只含boolean的判别，报告build/smoke/navigation-harness-nhfcm7_f/report.json。新稿唯一封装check／build／doctor通过，31包文件与23技能资源逐字节一致；sourcefcf4f317…／runtime69e48e91…／binary032a06ee…，报告build/research/tool-contracts/repaired-package/result-safe.json。

新独立live-repaired实例已核原句，首M3请求HTTP200，确认新混合目标与真实滴滴configured=true实际入模。但read_location超过两分钟无回执，尚未查询交通，不能验收通过。原生owner只读核实例存活且无预算／堆错误；源码显示已授权采样有十五秒超时，当前等待更符合授权等待或权限回调未交付，但没有足够日志区分，原生UI观察服务启动失败，不能断言用户未授权或GPS故障。仅关闭该自有实例；另开明确显式demo背景、真实M3与交通的一轮判别验收，独立记录，绝不冒称实时定位完成。

用户随后明确“我现在不在电脑面前，无法进行授权；你可以考虑临时进行模拟定位”，授权临时模拟位置，不再等待用户处理定位弹窗。当前独立demo轮继续使用真实模型与交通，不修改正常运行默认实时定位。

该唯一demo轮使用模拟位置、日历与笔记，以及真实M3和交通查询，十一模型请求后结束。更新目标、工具说明与配置事实实际入模。Agent生成三个可见候选卡片与查看详情按钮，并在同一循环自行修正Flow／Column DSL错误；然而实际点击详情仍空白。生成源码的三详情根仍visible:false，打开父容器不能显示隐藏的根；地图仅定义相机变化回调，没有初始绑定／fit事件，全轮没有地图请求或图像回执。还曾通过通用render_ui整稿清空其它区块，再重建详情。这些是实际模型呈现失败，不是高德底图获取失败；不再通过加提示或反复采样追成功，也不人工修改生成稿冒称Agent交付。

完成证据为build/research/tool-contracts/e2e/demo-repaired/e2e-result-safe.json，独立定位轮为live-repaired/e2e-result-safe.json。demo轮142.10秒、六候选展示三项，展示费用与耗时标签吻合工具；未调用extend_route或滴滴询价。早期比较中2342秒的公交满足四十分钟期限，但生成结束时已消耗142秒，超过初始58秒余量，静态推荐未重新核对期限；因此不能只凭标签正确认定推荐正确。UI owner已查看三卡与点击后空白的真实截图，两自有实例关闭，源码保持24c2e599…未再修改。

接续事项：工具接口与自由DSL能力已经具备，稳定交互详情／地图及主动混合探索仍需要可区分的下一步设计或诊断证据。保留当前失败源、模型消息与实际交互截图在私有ignored目录；正常定位默认不变，实时授权／回调的观察缺口也独立保留。当前工作区包含另一任务已完成技能迁移，不静默一并提交或推送。

用户要求保留Agent／LLM运行全过程，以溯源详情空白、没有地图请求与没有混合／滴滴调用；并明确“如果只是模型单纯没有做，那么就考虑改进系统提示词、agent skill或者工具description、工具schema”。同一UI owner先核逐轮请求／响应、工具参数／回执、实际读取资料、每次DSL及本地事件的完整性，并按run／step／call_id建立私有诊断入口。先区分已证执行原因、可检验契约缺口与不可观察的模型内部原因，再对确定遗漏做最小修正和在线复验，不把补提示本身当修复成功，也不添加固定workflow或强制工具序列。

运行证据核对完成，安全入口build/research/tool-contracts/e2e/evidence-index-safe.json：live-valid八请求／十五工具对、demo-repaired十一请求／三十八工具对均完整，事件序列连续；工具回执字符串确实进入下一请求history，实际skill全文和每次DSL均可按seq／step／call_id关联。定位等待轮read_location无回执单独保留。没有返回隐藏reasoning字段，不把公开assistant文字当内部思考。

确定的契约问题是实际已读资料仍混有整稿内detail_page visible:false及局部设置visible的示例，独立详情块则由父层管理；初始map emit说明也已读到，不能归因于资料缺失。采用advisor建议仅窄修这个歧义：主示例用独立块打开／返回及首次打开map绑定，旧整稿保文字兼容说明；render_route_detail.source参数解释父显隐和首次地图绑定、camera后续更新。保持任意DSL、不增自报ready字段或校验，暂不同时改探索策略。新版真实一轮只判详情可见／map请求／返回；若重复同错，不继续重写同句抽样，撤销“主要由示例歧义导致”的解释。未探索和静态结论过期限仍独立未解决。

契约窄修源码main b71a369672f616eb4e507df772b50879b2ffc34e462e62ac2acd3b4d3c653708，主资料示例为独立列表和详情，详情首次收到选定路线事实后绑定地图。工具的source参数承载生命周期说明，其余探索目标／工具schema不变。十二项同源Android样式原生检查通过；新稿check／build／doctor、31包文件与23技能材料化一致，封装安全入口build/research/tool-contracts/detail-package/result-safe.json，source2a806d3c…／runtime5b942c79…／binarya8d44328…，只关闭自有实例。

唯一demo-detail-contract真实服务轮十四模型请求结束，实际读取新版host-interface。卡片打开出租车详情已有可见分段／费用／限制，根不再visible:false，原隐藏故障没有复现。首次点击正确show_block和view_route，详情回调准备map事件，却因生成DSL将bound_route := ""放在View内而非脚本let声明，on_facts_changed报variable bound_route not found，在地图请求前失败。这是新语言／变量使用错误，不是原隐藏故障或供应商底图失败，仍不能称地图验收通过。另实际出现extend_route、滴滴报价及attach调用，不把这一样本的探索变化因果归于详情资料窄修；按回执继续区分成功与失败。保留整轮和返回证据，不继续改提示或重抽。

最终安全入口build/research/tool-contracts/e2e/demo-detail-contract/e2e-result-safe.json，索引已追加325事件／十四响应／三十三工具对；98.65秒。详情可见且返回列表恢复，地图零事件／请求／图像，源码未变且自有实例关闭。extend只成功origin至目的地一段taxi，没有形成混合候选；滴滴报价成功，attach先失败后成功写入未完成quoted-prefix-2（2300分），原直达route_1_6仍3200分。模型详情却声称这条直达路线已替换为23元，这是费用绑定对象的解释错误，不能把询价成功当候选正确使用报价。当前完成了证据保留与详情契约窄修；地图DSL变量错误、引用报价解释、混合探索与过期静态结论按上述真实证据保留为未解决事项，不宣称完整端到端通过。

用户新问地图作用域错误是否机械可修，以及报价是否显示错误，建议get_route／create_route／composite_route标准化避免手传duration／spend／polyline。地图稳定owner沿生成稿核作用域与修复边界，可做仅改外层let的私有隔离回放，明确人工实验不冒模型交付；route调查owner只读核候选／prefix身份与attach契约，先交付事实解释与最小设计，尚不授权大范围路线重构。

调查证实普通直查candidate缺legs／prefix_id，attach只接受prefix；模型为附价重查extend形成incomplete对象。已有回执明确未完成及completed_candidate_ids为空，仍被模型关联旧candidate，说明既有字段并非缺失，但双身份契约确实增加负担。建议先统一现query／extend／attach返回的Route，普通查询有可引用leg，get／查看／地图统一route id，attach使用route_id／leg_id并返回不可变派生新Route。不先新增create_route包装；composite仅在复用既有段的独立需求成立时再加，仍必须验证端点和公交时刻，不能只相加。到达覆盖范围、连接核实、费用覆盖范围三者独立，未完成小计不当全程价格；公交完整供应商报价不可拆摊。此为方案，未实施路线重构。

地图主skill已用正确外层let，当前错来自生成稿。原运行几何只在内存且own已关闭，不能精确回放真实原地图；因此最小隔离实验只用原稿／facts修声明，记录map事件边界，不请求HTTP或替换几何。它能判机械修复是否解除变量错误，不证明模型以后正确生成或真实底图已验收。

单变量回放已通过，安全入口build/research/tool-contracts/e2e/map-scope-replay/result-safe.json：原source seq268仅把View内bound_route :=改为外层let，实际点击后on_facts_changed无原生错误且收到route_1_6／taxi_map初始map事件。own关闭，产品main未变；无HTTP／M3／替换几何。说明此变量修法足以解除本次绑定阻断。原skill例本来正确，长期可简述let词法状态与:=控件成员区别；点击错误发生在terminal之后，未进入先前render工具诊断回执，是否让Agent继续修交互是独立设计事项，当前不暗中加第二循环。
