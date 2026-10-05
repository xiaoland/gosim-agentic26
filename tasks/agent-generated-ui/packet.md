# Agent 直接生成 Navigation 界面

状态：2026-10-05，0.8.3本地提交7d14dfc，用户已确认地图可见并指出它只是图片。交互地图接续[独立任务](../interactive-map/packet.md)；本包保留生成界面、详情和静态图片的历史证据及未确认empty stack根因。

## 本轮地图实现与AppCard评估

用户同意“先补齐地图＋详情切换的可运行低层示例，明确详情应包含路线地图；同时单独评估AppCard的生成与运行链路能否复用”，授权原话：“嗯，同意这个方向，推进”。地图相关必要应用／技能修改、验证和说明已获授权，AppCard范围为调查与隔离实验，不直接调整宿主构建或迁移产品。

稳定ui_finish负责通用Image＋地图事件／来源反馈和详情切换、最小呈现目标及实际Android模式验证；native_error_api负责AppCard工具、技能、模型、生成修复与kernel依赖的可复用性调查，以及冻结后一次封装。根负责整合、决策、版本与知识回流。本次不改写生成稿，不引入预制业务卡、第二模型循环、规定工具顺序或输出限制。地图切路线仍是本地操作，几何／费用／原期限保留真实来源。

完成依据：实际原生地图可见、切两条路线对应图片、返回列表状态保留；生成行为与地图桥验证分开报告，必要仅一次正常M3样本，不做大范围重复抽样。AppCard报告须区分源码具备、实调用和接入缺口，由advisor处理是否复用的工程取舍；无迁移授权则保留具体提议。沿既有授权本地提交，不推送。私有地点、地图URL／密钥、原始稿与日志留忽略目录。

地图实施发现同目标缓存再次注册未同步更新隐藏Image的缺口，UI owner已在register_map共用路径同步update_map_widget，并刷新status_widget。技能增加命名Image与来源标签、详情打开后按真实route id发事件；提示目标明确详情包含地图。当前真实公开demo地点高德返回3个驾车候选；首静态图HTTP200但实际为56B业务错误JSON（UNKNOWN_ERROR／20003），并非有效PNG；解码日志不能证明当前控件收到图。桥此前错误标为ready，已增加业务错误反馈。官方静态图只允许最多4个折线／多边形，原24个分段按共享端点无损合并为4个连续路径，533个含重复端点→513个非重复几何点全部保留后实际返回74355B PNG。不跨缺口补线、不裁段；正在实际页面验收。native源码核对hidden View仍转发Actions，无原生修改依据。

地图实现冻结：main SHA256 26e33e3022d4109c316ab53f05aa95325b1ef185b8c2fa9735abb525e649bc8c，native_ui 360fe23557488be5aa217a2c46e084d0042c6f42960dbec9ea03cb5a70aec84c。根已读取map-details/result-safe.json和build/smoke/navigation-harness-sac3qoex/report.json，并查看android-map-second.png。Android实际两条公开demo端点的真实高德地图可见且不同，返回列表中段rect相同，缓存同目标重开可见；自有实例已关闭。两项原生回归通过，命令python3 tools/smoke.py --map-details：共享端点无损合并／不跨缺口、HTTP200错误JSON不成为ready图片。本轮模型请求0次，这是技能示例与地图桥联调，不冒称M3生成行为可靠或GPS实测；更多不连续path仍可能被provider拒绝，显示错误而非截段。原样技能实例含演示文案，仅在忽略实验目录，不是产品固定稿。冻结后一次check／agent-build／agent-doctor通过，根已读取map-details-final-package/result-safe.json，10文件stage／嵌入pack／实际挂载字节一致。source aggregate e8a9db15e8beda5273cbc50b0bf450234ad79c95b52d8da797db9a97e2652b7a，runtime BLAKE3 3a29432b6b67a4517af00285f8087ea27fef19e0241191d37b797c47c511006f，binary SHA256 ab5ae356912d7e1002ff73d4e4caa87fc43802108f39fe26dd655d3e17dac1bb；解码包7,244,157 bytes。无Rust／宿主改动，封装不追加模型／服务，实例关闭；根本地提交，不推送，用户新查询验收待进行。

AppCard调查与advisor取舍完成：不直接接入整个助手，不复制生成修复实现；现有完整tool history已保留原始意图。锁定octos_ui客户端tool_context为空且send_tool_result忽略，完整迁移需kernel与业务tool桥；M3配置存在不证明运行。待工具结果入口可用，最小判别实验才是同一实际M3会话完成read_skill结果、render_ui真实诊断并自主修正。长期说明回流docs/architecture.md；本次源码只读，无AppCard构建或服务调用。地图实现继续，不等待完整助手接入。

## 当前地图与AppCard调查

用户实测确认按钮与页面切换可用，但候选详情只有文字，询问AppCard能否利用。此前只读调查未改应用或操作用户实例；本轮授权范围见上。根已读取map-readonly/result-safe.json：当前生成正文没有Image、地图字样或map事件；8条路线且maps_available=true，但没有发起地图请求，不能归因于加载失败或缺失几何。隐蔽mailbox未直接读取，未向用户实例注入脚本。当前技能完整详情例子仅文字，地图只有接口签名，可能引导了生成行为，此因果解释属于推断。

AppCard是OctoSense apps/appcard的原生Ask anything助手，有Agent/kernel与L0检查、lower/eval及卡片Splash链路；当前lock仅启用app-hub、未启app-appcard。Makepad widgets的appcard feature与它不同，在锁定版本为空feature。MapView已编译，支持路线叠加和触控，但默认本地vector MBTiles、非高德静态图；中国底图、候选映射、GCJ/WGS与网络域名尚未接入或验证。不能直接将导出类型称为可用的中国路线地图。建议先补现有Image+map事件的完整可运行低层示例，后续单独评估MapView与AppCard运行链路；调查期间零模型请求，无新增源码或构建。

## 当前详情呈现改动

用户建议：“更新可见详情？我会建议用 popup/sheet 或者进入一个新的页面来呈现。”在说明提供通用原语与用法、由Agent组织内容后，用户授权：“是的。开始修改吧。”本轮必要源码、资料、原生交互检查和说明更新获授权；沿既有授权本地提交，不推送。

先核对锁定Makepad已有浮层、显示／关闭与页面切换能力，优先直接提供实际可用的原生语法。不能把路线详情封装成强制业务组件，不能新增展示模型循环、问答、持久化或输出限制。Agent选择呈现方式并组织真实详情；查看、关闭／返回只本地执行。

稳定ui_finish负责应用、技能、必要smoke与Android模式实际交互；native_error_api核对原生能力及冻结后一次封装；根负责取舍、版本和权威说明。验收关注真实打开详情、关闭／返回后保留方案列表，以及长详情自然滚动；隔离实例使用公开事实，不操作用户实例。原生能力与模型实际交付分别报告，不把示例通过称为所有生成稿均可靠。锁定版本Modal和StackNavigation虽有Rust方法，但未暴露Splash打开／关闭／push／pop调用；不把类型导出当作方法可用。现成通用set_visible可调用，采用普通View切换详情页与返回，不新增Rust或导航框架。advisor建议保留控件实例，以实际生成区域高度建立有限视口；判别检查为列表滚到中部、长详情到底、返回后位置不丢且隐藏列表不响应点击。示例解释语法，不要求固定节点名或页面结构。

完成：main仅修正interface_facts的viewport优先读取generated.rect，缺少绘制area时沿原content.rect路径；技能以普通View/set_visible提供可选详情页与返回，长详情独立滚动、列表实例保留。未新增原生API、业务RouteSheet、导航框架或模型请求。

根已读取build/research/agent-generated-ui/page-navigation/result-safe.json并查看detail-bottom.png与list-returned.png。Android412×892隔离原生六项通过：打开独立详情、隐藏列表不响应点击、详情滚动到底23段、返回恢复原列表位置、保留编辑内容、无诊断；实例已关闭。main SHA256 4ed9b1ffb4a46086e3db2d91127a95d205e107b6b4e8e3996dc55c8fe105c6cc，native_ui af0270b19aa7f49c51c4cf3dac8e2b29538bf3f289b8be5bf1b4f63f4a19b777。validate.py与driver.py保留在忽略实验目录，可重跑本轮检查；未重跑旧全量验收。事实为合成路线、模型请求0次，不代表正常M3查询自动生成页面可靠；未接系统返回手势，显式返回按钮已验证。最终0.8.2 check／agent-build／agent-doctor通过；根已读取page-navigation-final-package/result-safe.json，10文件stage／嵌入pack／实际挂载逐字节一致。source aggregate 3f86da69424cefdcd0913849f8ba4c7deeb91bae4d24758a927c2b93547c0404，runtime BLAKE3 263a090a1f9096e600cebfe434c3543272317c1e64ccdbbff257665aeae19312，binary SHA256 7b4750ed71d123ca2a02e20e4b04586aaa8ab6c485edd27ddd1886b8a21034d9；解码包7,242,184 bytes。封装未追加服务请求或行为测试，实例已关闭，无Rust／工具链变更。根本地提交，不推送；用户新查询验收待进行。

## 当前按钮与诊断修复

用户报告生成时pop_stack_value on empty stack和字体类型color不存在，稍后正常渲染负例；两个查看按钮点击无效果。渲染错误自动恢复是用户观察，具体工具链与错误关联待核验，不能先认定VM错误阻断后续按钮。

稳定ui_finish负责用户实例只读取证、生成按钮→emit→父事件→查看状态／界面刷新的端到端修复，复用真实生成稿作隔离验证。native_error_api核对empty stack及类型错误关系，支持必要原生／包装部分；不为诊断扩展通用错误系统。原始diagnostics继续回给Agent并保留宿主日志，用户修正中的提示简短，恢复成功清掉原始反馈。保持自由原生UI，不添加预制路线卡、结构校验或工具顺序；按钮修复只本地查看，不引入问答续接或结果保存。

本轮沿用户已授权“继续修复”的界面范围，必要源码／资料／针对性验证与说明更新可继续。本地提交沿既有授权，不推送。只读用户实例不点击或关闭，验证使用自建隔离Android实例；不重复全量回归或无目的模型抽样。根负责版本0.8.1与权威说明，模型与宿主事实以实际证据为准。

只读与隔离实证已确认：实际7个按钮使用正确view_route与真实ID，原稿无on_facts_changed赋值或viewed_route_id读取；隔离点击使mailbox追加事件、父viewed_id由空变为2:taxi-0且无原生诊断，画面仍不变。因此按钮不是被此前color错误永久阻断，而是生成稿缺少状态变化后的内容呈现。当前日志确有font_style.color错误、后续Label.wrap错误及修正稿执行，未找到用户unknown:130:1015那条，empty stack归因仍不确定；源码失败回滚与每次事件独立执行不支持永久VM污染推断。

根采用advisor判断：仅增加“已查看”提示不能兑现查看真实路线内容，不把ack作为完成。修正技能里只有emit的误导样例，提供实际可执行的低层事件／事实回调示例，由生成稿自己的区域显示所选候选的真实分段、费用和限制，不规定页面模板。核对父查看后的事实通知，必要修其共通路径。旧稿不人工改写；用真实稿与7条事实作一次定向M3修稿隔离实验，真实点两条路线、观察内容改变且点击不新增模型调用。这个实验不是生产第二展示loop，不恢复用户会话；现页面更新应用后需新查询。

完成证据build/research/agent-generated-ui/button-recovery/result-safe.json，根已读取并查看android-second-private.png。一次定向M3 HTTP200、17.36秒、1642输出tokens，返回单Splash代码块而非render_ui tool_call；只提取原源码不改写后实际挂载，不能称产品正常harness自动挂载成功。隔离点2:taxi-0与2:transit-0分别显示239B／1314B详情，耗时／费用与真实快照相符、公交5条线路名与上下站全匹配，点击新增模型请求为0、无原生诊断、原received_at／deadline不变。旧用户实例仅只读、不点不关，私有稿及路线截图留忽略目录，不进应用包或Git。

错误反馈3项实际原生／合成模型通过，报告build/smoke/navigation-harness-g7l8vwr5/report.json，根已读取：具体color类型诊断保留tool结果、修正中不展示内部堆栈、成功清错误且挂载。主源码02ff1afe4fee3ce5c2131615600e9c124b4da425f3732fb00fdd862959336717，注入摘要另记。仅改恢复反馈与技能示例，父状态通知原本正常，无Rust或第二展示模型循环。新生成稿仍有处理中的标题与重复步行表述，不称全面UI可靠性；旧稿无法凭资料更新自行变好，新版需重新查询。实验实例已关闭，正式0.8.1 make check／agent-build／agent-doctor与隔离挂载逐文件一致已通过，根已读取build/research/agent-generated-ui/button-recovery-final-package/result-safe.json。main与freeze一致，source aggregate c535716bdac88b9056a4ee69ddf552273115d301b9c0132b4be68ad098819a02，runtime BLAKE3 91a7f8850d43c683d469970d56a0437da5407ea6cce77b1487334712e8e5736d，binary SHA256 bcaa605ec4ea8c06432907b9d04c6ec9a29a583065864049c537bf8772fa93fe；解码包7,240,480 bytes／10文件，技能材料化一致，无Rust改动、无额外服务请求。根本地提交，不推送。

## 本轮授权、取舍与计划

用户原话：“好的，继续修复。而且关于‘旧任务污染’，不知道我前面有没有跟你提到不要做任何持久化，也就是，不存在上一轮运行结果恢复；也暂时不存在问题澄清（因为我们还不是对话式的交互）。”这取代调查阶段关于修复历史Trip恢复边界、让澄清变成生成UI的提案；本轮直接撤除这些行为，不为它们建设更完善的恢复或问答系统。

每次查询独立初始化本次位置、来源、约束、候选与工具历史。标准工具调用会话只在本次Agent执行内存在，新输入不是上一轮补充；终止后的下一次查询也新建。不保存或恢复Trip、用户历史、模型会话或结果审计。凭据配置、打包技能、显式模拟输入文件与宿主调试日志不是应用业务结果；必要子实例通信材料只允许当前运行临时生命周期，不作恢复读取。

正常live不提供演示日历／笔记工具。模型可自行查询公开地点和交通，说明机场推断、具体缺失或失败；不请求用户澄清，不把测试资料伪装成真实来源。输出仍由LLM自由生成，不规定工具顺序或页面模板。修复反馈Label换行，提供正确的Fit／Fill与文本wrap语法，保证外壳生成区域具备真实可用的滚动视口；不添加组件白名单、输出校验或地图数量限制。

稳定ui_finish拥有必要应用／技能／smoke／实际截图实现、修复和有限验证；native_error_api已确认既有原生机制足够，不需新Rust，保留必要包装及最终一次check／build／doctor责任。根负责版本0.8.0、长期文档和任务包整合。保留其它工作，不操作用户实例，不重复全量94回归或多轮无目的M3。完成依据为独立首次与再次查询无旧状态、无保存恢复／澄清入口，Android模式实际长内容换行与滚动，最终包与挂载一致。本地提交沿用既有授权，不推送、发布或签名。

## 根因调查依据

本机只读证据build/research/agent-generated-ui/clarification-layout/current-state-safe.json：配置live，最新history没有agent_begin的system、只有ask_user，render_source_bytes=0；首facts带旧confirmed Trip的模拟日历／笔记／位置。query_task复用已恢复user_limits，完整新指令也未调用start_task。纯文本通过父feedback显示，位于生成Splash的ScrollYView外。

布局证据build/research/agent-generated-ui/nested-splash/layout-result-safe.json：默认Label和仅width:Fill仍为23px单行；显式width:Fill height:Fit flow:Flow.Right{wrap:true}变100px自然换行。ScrollYView固定视口→body Fit→模型根Fill不产生预期可滚动内容，模型根Fit能见0–4行，滚动后12–17行。根已读取两份证据，负责人已看截图并关闭实验实例。

advisor已就生命周期／呈现通道／真实来源给建议；用户新指示进一步删除持久化和澄清，不能沿用旧提案当实施要求。当前无待用户决定事项。

实施中单一父ScrollYView跨Splash实测仍有末尾两行不可达；已采用有限父容器／Splash视口、子ScrollYView与内容Fit的现成路径，不要求单一全局滚动条，不需新增Rust。修复后的9项实际原生、合成模型检查全部通过，证据build/smoke/navigation-harness-dldf0lwz/report.json，根已读取：本次多个call_id、独立system/user历史、真实render、无调用结束、旧结果文件未读未改、停止迟到拒绝、新查询新的时间／预算、Android换行及最后一行可达。产品main 1699f02b7b113322f1b3d0222dbd08406092aa74e7f6c0533e81b8ddeb3bc838，注入摘要另记，合成模型不冒称真实路线任务。

正常live启动不依赖demo初始化，显式demo空来源拒绝、三文件齐备继续，三个入口隔离检查通过；证据build/research/agent-start-mode/result-safe.json，根已读取，无进程或凭据读取。

本轮真实live M3查询已发生，定位超时，取得4个真实高德POI；两次生成错误Parser/width not found与status not found之后可见缺失结果，不读demo、不等待澄清，也没有产生路线。旧观察器未取得完整工具history，不拿桌面idle记录证明真实调用序列。实际稿在修复后重新挂载验证，不追加M3；根已读取build/research/agent-generated-ui/native-stateless/result-safe.json并查看final-top.png／final-bottom.png，末尾字段实际可达。自身实验实例已关闭。

实测稿仍出现内部函数、POI ID、Unix时间戳与生成时“正在处理”标题，模型自行推断北京/CNY，目的地未被规划器采用。根采用滚动证据但不把这些文字当内容质量通过；只补一句面向用户输出目标，不新增强system、结构检查或人工改稿，没有额外模型验证。9项产品main为1699f02b…c838，当前布局查看版c7e7c818…32c2只追加viewport实际读取及文字清理；最终main 8e334492e011df57c34d509cb2e5a854419091fb0e7df9ec74d4f2765e1df931再补简短输出目标。此前c7e7构建已完成，必要文字改动后再次打包／增量构建，只为最终摘要一致，不重跑行为验收。含输出目标的首次正式封装已通过gate／build／doctor并实际挂载一致，证据native-stateless-final-package/result-safe.json（主源码8e334492）。根最终权限整合发现maps.pick已随旧交互撤除，故清单删除unused maps、listing同步不宣称当前Maps往返；该metadata不改行为，不追加模型或原生检查。最终stamp／gate／build／doctor及实际挂载逐文件一致已通过，证据build/research/agent-generated-ui/native-stateless-permissions-package/result-safe.json取代前一次包记录，根已读取。最终能力storage／net／location，源包7,239,143 bytes；source aggregate90039435952ce5e59a4242c94f2a0b98a8bbb445c6ce2be6d1354adcb826be41，bundle BLAKE3 4b264dbf872233d2f7a24cd85b5fd2c76398f4d3c04525e8575c4fa2c9bf4b5c，binary SHA256 e94472bf192a70a3643d4b5fb295ef7d37c4527023611d9e466f1a29d44ae2af。没有追加M3／行为测试，实验实例全关闭。根本地提交，不推送。


## 此前目标、授权与责任（历史）

固定外壳只保留输入框和查询／终止按钮，其余内容让 Agent 组织。Navigation 使用无衬线字体，其它应用保持原样。用户先指出分区协议约束过多、预制组件包装度高及一图限制，授权“是的，继续”；继而明确：“我个人建议不要在这个开发阶段做任何的安全边界、一致性校验、输出限制等等各种限制”。这更新了本轮取舍，不再为开发期界面建设沙箱或组件协议。根已告知按直接原生生成推进；用户指定的时间／预算仍是路线任务条件，密钥仍不进入 Git 或模型输入。

必要实现、实验、验证与文档更新已授权，不重复请用户审核。本地提交沿用既有授权；不推送、发布、签名或赛事提交。bundle 保持 OctoScript 脚本及资源；只关闭本任务实例，不改系统权限、字体或其它应用。后续交互与截图以 macOS 宿主 Android 手机模式验收，不称 Android 真机。初赛北京时间 2026-10-04 23:59 截止，优先可运行闭环，不扩展通用平台。

根负责协调、决策、长期文档、证据采用与最终提交。GPT-6.1 Sol medium 的稳定负责人 ui_finish 负责应用、smoke、截图及实际交互；host_finish 已完成原生接口验证，但后续两次模型capacity失败且没有执行操作。新增诊断与工具链收尾正式转交 GPT-6.1 Sol low 的稳定负责人 native_error_api；直接对接 ui_finish，保留原host变更／证据，不重复原探针。advisor 只作 consequential judgment，不作 reviewer。现有改动和失败证据保留，不继续旧 schema 验收。

## 0.7.0 已实现设计（历史）

用户原话已纠正为“不是workflow”：只提供元提示词、工具、技能等资料，由LLM自己处理、组合完成目标。根已承认此前限制／协议／重复回归过多，停止全量验收和旧展示错误重问流程，不再为旧稿窄修延误模式迁移。

采用一个标准工具调用循环，复用现有M3 HTTP和领域执行函数。保留assistant原始tool_calls，按tool_call_id执行当前批次（顺序足够），追加对应role:tool结果，全部完成后回到模型。工具不自行next_action／request_interface，不存在第二个展示Agent或历史主人。assistant无tool_calls即本轮结束等待用户，不强制finish；用户终止沿当前run生命周期停止后续派发、保留原业务期限。工具正常失败回结果，传输失败明确结束，不隐藏重试。

工具直接复用技能读取、日历／笔记／定位、地点查找及采用、公交／驾车查询、候选确定性比较、render_ui(source)、Trip确认保存读回。不是next_action加action参数的万能封套。工具说明真实输入与结果；缺位置／目的地返回实际缺失，不用available_actions／can_present当phase许可表。原present_results强制公交＋驾车、选route、结束、触发另一UI循环的连锁行为撤掉。LLM决定继续查什么、何时澄清、展示及结束，路线计算不重写。

技能按需提供已执行的Makepad基本语法、原生类型继承、Navigation字体、snapshot／mailbox接口与示例，不规定页面结构或“读技能→渲染→修复”顺序。render_ui挂载并读真实diagnostics后返回结果；错误反馈在同一工具历史由模型决定处理，不在工具内部重新问模型。纯查看与地图加载本地响应，需要判断的用户动作进入同一会话。

已撤应用自设的模型token、源码／输入长度、工具步数、自动阶段、纠正次数、网络／地图timer、响应bytes、source条数／字数、几何截断与重复调用quota。不是重写宿主／服务实际能力。删除后只允许更多／更久／更自由的框架限制撤掉；原时间／预算、实际坐标／端点、未知费用／来源事实和确认计算继续作为产品语义。密钥不入Git／模型输入，不改其它应用。

官方宿主现有app peer入口不直接采用：锁定script_apps.rs只提工具授权、不传instructions／skills，implemented_by:app返回app_tool_unavailable；本机launcher没有kernel。不能据清单支持宣称已可调用。参照[pi-agent-core](https://github.com/earendil-works/pi/blob/main/packages/agent/README.md)的标准tool调用／结果历史和[按需skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)，迁移现有OctoScript loop，不安装Node／SDK后端或造新平台。

## 原生依据与迁移前的调查记录

现成 `build/research/agent-generated-ui/nested-splash/{parent,child}.splash` 已在 Android 412×892 模式实际渲染中文、按钮及两 Image；父通过 ui.child.red／blue 分别加载图像，子写 mailbox、父读取三次实际点击均通过。先 set_text("") 再 set_text(newbody) 后旧 timer 没写新 mailbox。根已查看 android-app.png；证据为 result-safe.json、lifecycle-safe.json。公开 fixture 不是 M3 产品验收，也未证明 snapshot 热更新或真实 Android。

原生 ui.find(name)、ui.child(index) 和只读 rect 已实现并锁定。动态字符串查找复用静态 getter，直接子实例可独立加载，rect 是最近一帧已绘制裁剪 area，未绘制返回 nil；不能在借用 render 中同步查询。host 独立索引重放与像素／几何／查找实证已采用，原定位、Maps 和字体 patch 字节保持不变；新增接口不需要重新设计业务桥。

host 已完成嵌套命名 Image 的 mailbox → ui.child.find(name) → 分别异步加载实测：蓝图先回、清空后同名换稿、倒序加载与旧代迟到均符合实际实例，像素已查看。证据 api-nested-mailbox-result-safe.json，使用公开 fixture 色块与城市标识，没有真实网络地图或 M3，不替代产品验收。无需新 Rust／重编；源码已交 UI 直接复用。剩余是 M3 自己生成该闭环及真实地图／交互验证。

此前发现 raw body 默认子 VM、LinkLabel、Factory、嵌套 VM 与原生资源不受完整脚本限制，曾据此停止直接生成。用户本次明确不做开发期边界，该治理不再是本轮任务，不继续沙箱工程。调查结果是历史事实，不再作为停止实现的理由。

2026-10-04 复核[官方提交指南](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md)，允许说明可构建原生宿主扩展，未发现 stock-only 规则。用户初赛 OctoScript 应用边界仍保留；宿主覆盖单独锁定、复现与声明。

## 执行诊断的必要接口

实际生成已能进入子执行，但 M3 反复将 draw_bg／draw_text 写普通object而失败。当前try先trap.err_clear再进入失败分支，没有脚本异常值；Splash captured_errors／take_errors只写宿主日志，View只转Error:TypeMismatch。真实native.log含 expected DrawQuad, got object；原生正确扩展语法为 draw_bg +: {...}、draw_text +: {...}。手工日志反馈可推进调查，不作为应用自行修正完成。

根采纳advisor：新增极小Splash实例只读最近原始诊断，让应用把实际执行结果交M3；set_text每稿清旧诊断、复用捕获与格式化、保留宿主日志，不读全局log、不做错误平台或沙箱。这是必要功能接口，不是重新加界面边界。native_error_api 获授权实现必要Rust／patch／lock／包装，UI继续语法与交互，不等桥。如果只能通过重构全局错误系统才能归属实例，或最终仍只有TypeMismatch则停止接口扩展并如实保留缺口，不堵当前生成。完成依据为 known ordinary-object失败→应用读具体错误→M3修正→实际挂载，非人工改源。

diagnostics 已由公开fixture闭环验证：具体on_render类型文本可读、重复读相同、原log保留，clear后正确+:稿诊断为空且中文实际挂载；证据 nested-splash/diagnostics-result-safe.json 与 diagnostics-after.png（负责人已查看）。nested-splash/diagnostics-patch-replay-safe.json 独立索引完整重放两patch且verify_source通过，最终Makepad tree 4f2d590852cd98f479848636ce80c882477e0579、host tree 668cfb41686ec8780381b47494368b98a8f1aad2。当前binary 072307a2是接口实验，不冒称正式包。UI已收到先diagnostics启用再set_text的消费方式；真实M3自行纠正闭环仍待验收。

接口边界归toolchain/README：首次调用只启用当前实例以后捕获，读取不消耗缓存、set_text清空、原log tee保留，其它Splash默认不捕获；try主动捕获的异常依然会清除，不能恢复具体文本。不宣称已获全部错误类型。

## 0.7.0 完成依据

单一正文技能为 bundle/assets/skills/native_ui.md 与 navigation_data.md；官方 bundle/skills 目录保留给 peer 声明，故材料放 assets，应用运行目录仍为 skills。启动器从构建包材料化到应用私有目录，read_skill 按需读取；未引入 kernel、SDK 后端或通用技能平台。材料化逐字节一致证据为 build/research/agent-generated-ui/skills-materialization/result-safe.json。6项实际原生、合成模型验证为 build/smoke/navigation-harness-807l3mw4/report.json，覆盖同一回复多个调用、原消息和call_id、真实render诊断、无调用结束、原deadline与实际按钮回同一历史；根已读取，不重复全量旧回归。

真实 M3／高德记录为 build/research/agent-generated-ui/native-harness/result-safe.json，根已读取并查看 agent-harness-before-click.png。模型自行选择 read_location／read_skill → search_places／set_constraints（缺来源实际错误）→ adopt_destination／query_transit／query_driving → compare_routes → read_skill → render_ui，实际返回7候选、空diagnostics并可见。该顺序是本次观察，不是应用规定的workflow；没有人工改模型生成稿。

实际点击“放宽时间到80分钟”进入同一历史，原received_at不变、arrive_by按新时限从原起算更新；模型自主只调用render_ui后结束。工具facts仍confirmable=[]，模型却声称路线可行，Trip未确认。窄屏长行裁切，包截图取初始负例，不用后续错误文案作展示成果。后续应解决模型对当前检查事实的误读与原生布局可靠性；不能用增加预设workflow或夸大验收掩盖。任务无待用户审批事项。

执行产品main SHA256 96bb5ed6269c9d44230207eb05ce03ab28370a8f811eb92e8c8178a150dccdb8；最终8c6f93ad586881c135c95db0d8675eff22db32e4480981cacd5d0ae85427c743只改单正文技能读取及行尾清理。native_error_api已完成冻结后一次check／build／doctor及隔离挂载，根已读取 build/research/agent-generated-ui/final-package/result-safe.json。0.7.0解码包7,272,241 bytes／10文件，stage、官方pack与实际挂载逐文件一致；source aggregate 10be566979a3e093b46f47b22fbf813d29e78b2421a1298a0502d60855c6a816、runtime BLAKE3 7e1410d54c55980314db1f97b6e2bfb5dd474930131ff3cd6de202e79c801c32、binary SHA256 17b5ed78d3c64158c15c01291da1b08bf5f25f20df5827c88b69676d41c2f345。该封装不调用外网、不替代产品交互证据，自有实例已关闭；根本地提交。不继续全量94回归、不添加模型试跑，不推送、签名或发布。

## 统一 harness 前的直接生成证据

正式应用 main SHA256 efa9d528624eef4502d3cce95f945253b05c85fac2f787929bb62225d38fa64c 的 build/smoke/navigation-native-r4ayl04r/report.json 已通过94业务＋13直接生成功能，覆盖中文挂载、嵌套图、mailbox查看、独立／倒序／单图失败、换稿与停止迟到、超过旧步数／500秒／32KiB仍执行、多次协议反馈可继续及用户终止。受影响HTTP派发的独立7项通过 navigation-native-26_8v34q/report.json，实证无应用40秒timer时持续等待、可终止及实际HTTP状态。两份均隔离原生运行、无外网；报告把产品摘要和注入后摘要区分，不代替真实M3。

真实直接Splash澄清首次输入2975B，被旧40秒timer结束，没有服务响应或源码；旧timer现已撤。新请求输入2977B已HTTP200返回：17.81秒，6171B源码，923输入／1413输出tokens，未设置max_tokens。子on_render运行失败：M3用了不存在的self.viewport／self.snapshot，当前澄清背景没有路线，源码尚未渲染。原源码及结果保留，不算成功；负责人加入实际语法／API短例，并将子render真实错误通过mailbox反馈到模型继续修正，保留用户终止，不限制纠正次数、不改写或隐藏错误、仍按原任务期限。尚未冻结截图或封装。之前的47b5aa（94＋10）与7jgg9dwg（94＋11）属本轮中间功能证据，不称最终同版。

## 中间控件树阶段的证据

已经完成但按用户新指示撤换的低层树通过 94 项业务、29 项 UI 边界，报告 navigation-native-ypcpf722/report.json，产品 main SHA256 e8f552c8939d6b63fd6a881265e1d6619d65eaa42c089de031f83b18d40b174f；注入测试后摘要分开记录。该记录无在线请求，不证明新直接生成路径。

真实 asking 首次及一次反馈因数组形状、text／data 并存和虚构 Map 目标失败；schema 对齐后一次请求 40 秒超时。真实 Maps 选点、坐标转换及城市核对后，高德取得 7 候选，proposal 输入 30,705 bytes／11,388 prompt tokens，首次有两张不同目标的图但多余 Map color／align 被拒，一次纠正被旧 4096 输出预算截断。曾决定展示8192并重新冻结当前来源，尚未发出新模型请求即被用户新方向替代。完整原 segments 未保存，不能伪称精确重放。所有失败保留；未达到真实双图验收。

## 0.6.0 基线证据

分区协议与一图是旧实现，不是产品要求；其完成记录不替代本轮验收。main `49994976`，产品前版 `b0d6f6de` 完成 94 业务／58 定位／7 派发／47 UX 回归；最终只增加三处 map:null 拒绝，精确差异归 `source-null-delta-safe.json`，同版 15 项检查归 `build/smoke/navigation-_jx3fjkc/report.json`。固定三次 proposal＋一次 asking 均最多一次反馈有效，归 `sections-map-fixed-safe.json`；不代表可靠率。

0.6.0 实际服务 UI 联调用了明确 demo 起点、真实 Maps／高德，得到 7 条不可行候选，复用真实 M3 布局，切卡跟随图、展开／编辑及原期限通过。不是完整自主任务或真实 GPS 验收；原 desktop 横排长按钮裁切。旧证据归 `build/research/agent-generated-ui/report-safe.json`。

字体已完成：Navigation Sans CN 基于思源黑体 CN 2.005，保留全部字形／映射、去 hinting 并依 OFL 更名。来源／复现与完整许可归 `bundle/assets/fonts/README.md` 和 `OFL.txt`；实际探针同窗对照确认 Nav 无衬线、原主题文楷，其它应用字体与主题摘要未改。证据 `build/font-probe/report.md`、`formal-font.png`、`unchanged-host-fonts.json`，根已查看。

0.6.0 check／build／doctor 通过，包 8,290,866 bytes；字体附属文档 gate 独立覆盖、官方包装身份与原定位／Maps patch 不变归 `build/research/agent-generated-ui/host-font-precheck/final-safe.json`。source aggregate `7157c910`，bundle BLAKE3 `7d440ae8`，binary `ed1c112a`。本轮必须重新封装，不能沿用旧摘要。
