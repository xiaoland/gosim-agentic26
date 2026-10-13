# 出行目标守护：前台闭环

状态：2026-10-12，online5实际详情／地图机械缺口已用原保存Route和未改M3稿离线修复验证；当前封包收尾。混杂双VM在线与修后离线证据分开，不宣称完整新在线守护通过。下述0.15.0验收只证明当时版本与条件，不代表当前守护流程已全量复验。

## 目标与授权

用户要求从混合出行规划发展为持续维护出行目标，并明确“是的，请开始落地”。范围是确认目标与路线、保存必要业务状态、前台重新核验、解释替代差异、用户确认后更新。沿用自主提交、推送、真实 M3 验证及临时模拟定位授权；不下单、不自动扩大预算或延后期限。

此次授权改变此前完全不持久化的边界：只恢复用户确认的目标、选定路线依据、进度、累计费用及确认版本，不恢复模型会话、未确认候选或生成 DSL。首版只有一个活动目标，可结束或删除，无后台监控和到达保证。

## 当前实施与恢复点

本批online8恢复入口修复：用户授权继续全部必要修复；旧online8 step12供应商失败后全停，不续旧VM或导入会话。守护核验的模型指令与句框原出行要求本来不同，原恢复资格将两者混用而错误拒绝。当前任务启动分别保存模型request_text与request_form_input，失败／继续／输入事件分别核对两种身份；run、trip、generation、消息数、工具已结束、未消费响应与取消／历史限制沿用。现有manual_resume测试扩为normal、guardian指令差异及guardian编辑三组，生产start_task_ready、request_failed、实际继续按钮和TextInput事件共15项通过，原tool消息、绝对期限、路线与来源守恒；history、切trip、旧token／owner、goal generation及取消资格核对通过。证据归build/research/journey-guardian/manual-resume-identity-probe，三张关键截图已查看，全部隔离实例停、零M3／供应商。guardian fixture只隔离共享身份合同，不重跑真实核验业务、磁盘失败保存或冷重启；旧online8呈现仍未完成。check／stamp／build／doctor一次通过，封包回执为build/research/journey-guardian/manual-resume-identity-probe/preflight-safe.json；mainbd665b36／sourcef5fc121e／binaryd3189251。下一步仅由root限定新独立在线case。

最新online5原正式UI vm2自然完成12响应／33工具对，实际已装详情、消费show_block与view_route，但child facts的viewed仍空、Route存在且地图目录未就绪，详情查空ID显示“路线不在结果”。原采集漏掉同session先行vm1（13响应），真实账本合计25次，不能把混杂session当单loop预算复现；审计归current-online-5/session-audit-safe.json。已全停17424，原211seq vm2／vm1原件、保存快照与M3详情194源未改。job21 report_goal_check空参数execution_limit后模型自主重试成功；原提案实际超23:30，仍未确认，期限预算不改。

只读已核父view_route把合法ID发布绑在ensure_map_catalog完成回调，几何batch硬退出会丢失后续timer并留下waiters。最大实际polyline412775字符／19656点；一小薄堆旧源测量split2.77ms／含100点3.13ms，真实goal仅35553B，to_json0.59ms／parse0.77ms／valid0.11ms，未复现64ms。原389KB文件是UI树，不能当大goal因果；阶段报告online5-phase-probe/phase-ehdk8p_d/report.json保留。

本批必要修复：合法Route选择与文本事实先发布，地图目录不阻塞详情；复用UTF8单片接口拆2048字节块、保全原始路径，checked几何任务失败清pending并有阶段错误，旧run不续回调。report只分检查和版本绑定的提交入口，不盲拆三次clone或放预算。现有高德price_basis补明当前投影未分摊各交通段价格，未拆分不代表未包含；不同站对报价只能保留假设作为待验证预算参考，不认证本Route整程价。金额与unknown状态不变。实际原稿UI组已3/3通过：online5-ui-probe/ui-v1bsvxqy/report.json，实测main401f4f32，生产trip_load恢复原routes182／detail194逐字；点击即时发布Route_1_10，20原线生成14目录，全路径字符串／端点／点数／bounds与原算法等值。一次真实staticHTTP，412×892实际详情与高德地图像素同屏、返回候选成功，图detail-map-visible.png与returned.png已查看；0M3／交通请求、native_errors为空。最终main5912仅额外在cancel清旧几何pending，不重UI。最后online5-helper-probe/helper-3oi6d9ou/report.json 4/4：真实checked instruction硬错清pending／记录error／等待者一次，旧token不回调不写缓存，生产report{}独立commit真实落盘，回执与decision一次、原goal版本／source时价／期限守恒。取消仅核对应状态转移，未重跑UI取消；guardian_refresh界面重绘仅在helper fixture stub。首前置失败helper-or6n3lzw保留，不伪归产品错误或改PASS。全部实例停，无新M3／交通规划；修后离线闭环不冒称再次在线完整守护通过。最终main5912a1a8／source2868eb38／binaryeb4d0f46，check／stamp／build／doctor通过，回执build/research/runtime-upgrade/rc6/guardian-map-job-preflight.json。SDK3975／prelude2280／host锁不变，正常HOME36calls／655511tokens、d1f154e4 SHA保持，pgrep空。下一步只由root决定剩余验收范围，不默认启动新付费整轮。


最新current-online-4保留146连续事件、9响应／23工具对。父真实点击已确认conditional提案，goal变version2，期限23:30与总预算200不变；整程费用与连接仍未知，未升级可行性。所有78197实例已停。原125源码只有静态MaterialCards，没有本地候选按钮、详情或地图；确认后生成文字仍称未确认。当前fixture只给“重新核验已确认的出行目标”，不能把缺地图归为用户不需要，也不向fixturegoal塞虚假的用户偏好。

已核实际原首请求model_request-4-private.json没有presentation_task，普通规划与守护虽共用model_task_context，却只提供事实与嵌入环境。当前最小修复在同一上下文新增产品交付目标：候选本地打开对应Route详情、同Route真实步骤／来源／覆盖与未知、真实几何分图地图或缺数据说明，以及审批／选定状态取当前facts或不重复父权威状态。它不规定五槽、布局、组件、工具顺序或额外用户输入；原约束／请求与SDK397／host锁不变。native-ui的方法资料原已有on_facts_changed与动态守护事实要求，此次只说明presentation_task属于产品默认目标而非用户偏好。另有online4实际确认图中MaterialTitle／Body使用宿主WenKai、父Nav使用Sans的局部适配遗漏；本批generated_context导入后派生五个Material文字／按钮为既有NavRegular Sans，原字号、颜色与布局保留，canonical SDK／其它应用不改。一屏Material／Nav对照4/4通过，实际412×892截图font-phone.png已查看，生产区块通知成功，native_errors为空；报告material-font-probe/calendar-8526upaw/report.json。字体证据是实际generated_context的Sans资源绑定＋已查看字形，snapshot未暴露内部family，不冒称字段验真。不跑主题、其它应用或路线矩阵，零模型／供应商、账本未变，全部实例已停。离线原请求／源码引用核4项通过，report在build/research/journey-guardian/presentation-context-check/report-safe.json，不冒称新请求、UI或像素已执行；无原生／模型／供应商。最终main05ac1517／sourcec6734a6a／binaryd7090547；check／stamp／build／doctor全通过，回执build/research/runtime-upgrade/rc6/presentation-font-preflight.json。SDK3975／prelude2280与锁不变，正常HOME36calls／655511tokens、d1f154e4 SHA前后相同，pgrep空。下一步由root安排针对性呈现验收，不暗续普通终态或再付费规划。


最新实际循环current-online-3保留346连续事件、25响应／36工具对与原提案；原C4983 Route_1_10已到T3官方入口，逐腿800／4300／0分，内部价格5100分和cost_complete齐全。整程公开金额为空来自连接unknown／condition接入32.6267米／入口内部未知guard，不是漏解析前段城际票价；前段只有地铁5、13和步行。原推荐理由“全程¥51、满足预算期限”仍超出了确定性assessment unknown，父确认未执行，goal仍版本1。原详情已安装打开，地图事件漏path_indices，实际14条目录违反每图4条限制，因此没有HTTP或地图像素；不把该错误说成网络供应商失败。唯一43888已停止，完整价格材料与原稿保留current-online-3，未手改理由或暗续谈。

本批保full_journey_amount nil／assessment unknown；费用增加已查腿终点范围、腿数及unknown_reasons。全部腿已报价时明确“到T3请求入口的已查三段估价合计51”，并提示未核接入可能有附加费用；入口内部未知不表示必收费。缺一腿报价则仍为已知小计。条件推荐可以准备提案，但不认证预算／期限，新风险描述不是用户已接受。地图目录增加覆盖全部真实索引、每组至多4条的selection_groups／selection_scope，Agent自主选择，代码不自动选前4、分图或安装UI。map_bindings保实际状态与http_requested，未发请求仍false。唯一隔离小组6/6通过，报告online3-cost-map-probe/guardian-ni118dtk/report-safe.json：实际三腿51与缺4300报价仅小计8、无raw旧公共cost保新增字段、真实14目录[4,4,4,2]无重漏、漏选择错误与合法四条参数形状。几何只是按原目录首末点构造的两点fixture，不声称完整几何等值／像素／HTTP／UI map_bindings测试。实测main7be7；最终f930仅将未到达入口的错误措辞改为“目的地采用官方入口”，两个已达变体不受影响，未重复组。全部实例已停、账本原／隔离SHA一致，零模型／供应商。不重做上一批7／1／3，不改SDK397或host锁。最终check／stamp／build／doctor通过，mainf930fc4e／source1313baa1／binaryaf690100，封包回执build/research/runtime-upgrade/rc6/guardian-quoted-map-preflight.json。正常HOME36calls／655511tokens与d1f154e4 SHA前后相同，pgrep空。下一实际复测仅由root授权，原online3仍未确认目标或显示地图成功。


当前恢复点是本批main `3dfa44a34ede271eb0dfdf4f7c856433b8d8826b39f9b29ad556b25fd2943762`。current-online-2原件保留249连续事件、16响应／37工具对与3215963B快照；Agent自主准备提案，但原理由声称所有候选均能按时到机场，selected route_1_5实际末端是站入口，距T3设施入口约41.6米，整程端点／费用仍未知。父确认没有执行，goal仍版本1。原理由在提案回执之前形成，因此本次到达投影修复不被描述为消除首次夸大的证明。

普通Route、guardian assessment及提案选中路线现在共用目的地到达范围；部分路线保留queried_endpoint时刻，目的地estimated_arrival别名为空。耗时保留真实数值，同时明确已查路段与最早场景；等待余量同范围，局部终点余量单独提供。query摘要区分queried_to_ref／实际leg_to_ref与overall_destination_ref。原41米覆盖缺口不放宽阈值；已有extend_route的mode:walk可查询真实末段。确认面板先展示权威范围／费用／status，随后保留“Agent推荐理由（不是可行性认证）”；unknown提案仍允许，不分析或改写理由。

原render_ui 192含blocks:[summary]之外未声明item，曾静默丢掉详情。现在render入口拒绝未知参数、source与blocks歧义，并返回真实current_blocks库存；正常更新不自动补详情。子按钮需要自己的on_click，外卡on_item_tap API仍保留。技能原已真正读取，不能将此次失败归为资料未传入。

必要隔离证据已收束：online2-contract-probe/guardian-z9xzxtuq/report-safe.json 7/7（实际保存route_1_5映射为合法最小运行结构，非完整liveheap／供应商复演）；online2-full-probe/guardian-7fb1tb06/report.json 1/1完整路线反例；guardian-origin-probe/guardian-zqerxlox/report.json 3/3实际longitude／latitude形状。最后发现guardian_reexecution向字符串坐标解析传入位置对象的真实bug，修正后8.4826米origin_gap有效，固定班次错过仅使重走原整程失效，actual_journey／boarding仍unknown。缺坐标未知及旧location／String兼容已核。前两组未为最后独立坐标修复重跑；各报告独立版本与边界明确，原fixture前置失败保留。所有自有原生实例已停，零模型／供应商，SDK3975fe7f／prelude2280保持。check／stamp／build／doctor全通过，最终source76b596d4／binarye84fe4a2；封包回执为build/research/runtime-upgrade/rc6/guardian-scope-preflight.json。正常HOME36calls／655511tokens、d1f154e4 SHA前后相同，pgrep空；下一步只有root授权的真实M3复测，当前不宣称守护闭环成功。


用户授权继续复赛产品优化；root授权rail_model稳定实现原计划当前可执行性与守护费用差额范围。main／技能／必要架构与测试由rail_model维护，runtime_update仅并行独立通用UI材料，不改main；正常49677已由rail_e2e停止。此批不调用M3、不读取个人背景、不修改发布版本或标签。

首实现复用route_timing处理已保存的固定班次，guardian snapshot、saved_goal_route与report_goal_check均提供original_plan_reexecution：当前评估时间、旧来源时间、原起点匹配、固定班次错过项和从现在重走原整程的估计。它明确为reexecute_original_full_journey，不认证旧报价或推断已登乘；起点缺失／不匹配，或已有确认进度费用时，剩余行程仍未知。原时刻不能后移，真实在途状态一直保持未知，直到另有本轮证据。

守护比较复用统一cost事实：full_journey_delta_cents只在两整程估价齐全、原起终点一致且无进度费用时提供；queried_legs_subtotal_delta_cents保留已查路段金额差并声明覆盖范围可能不同，旧报价未刷新。提案与核验中的cost_delta_cents改为整程差，不更改registry中的价格；父应用真实确认、目标版本和异步提交合同沿用。main acc0d0ec的唯一隔离组7/7通过，证据为build/research/rail-integration/guardian-reexecution-probe/guardian-pm_vvqjc/report-safe.json。当前起点、缺位置、有progress与固定过班范围、partial／full差额、snapshot／提案版本及未批准不写入均核对；actual_journey_status与boarding_status一直unknown，current_check未被counterfactual失效升级。旧source／quote／deadline／班次字段结构守恒，steps_cache允许作为派生缓存增加；首wholeJSON不变断言失败材料guardian-92jicif9保留。guardiansave仅计数拒写，不声称当前真实批准持久化或旧32项全量复验；0M3／供应商、账本未变、全部实例已停。通用UI包已合并：最终main ecd0d021／source a1b2081a／binary 22cf5897，SDK617b1d41／prelude2280b462；既有check／stamp／build／doctor全通过，封包回执build/research/runtime-upgrade/rc6/guardian-sdk-preflight.json。独立示例当前runner的浅／深／再浅像素与交互已验证，Navigation旧Nav派生保原字体颜色；最终同步不重复守护7项或旧Nav组。所有原生实例已停，本封包未调用模型或供应商；正常HOME当前36calls／655511tokens、SHA d1f154e4保持，不与过时27call基线混同。下一步仅由root限定一次当前主线在线范围；当前真实前台重核与替换尚未验证。

### 当前在线失败与必要修复

本批真实guardian-live-1尚未通过。current-online-1保留201连续事件、9模型响应／37工具对，原goal版本1，没有propose_goal。首render_ui的__document实际show_block(id:...)违反真实target_id参数，unknown named arg id；后四named区块初始化成功却不含路线查看／地图，旧失败__document仍在全局诊断中，不能把changed成功当全界面成功。

实际最后模型请求已包含Route的full_journey金额nil、queried_legs_only、已查终点估计、预算／期限unknown，终稿却把¥5小计扣为剩余¥195并宣称均满足期限；不是解析漏字段。供应商basis文字“完整公共交通方案总价”确有范围冲突，本次只改为本次option／leg字段报价，真实500／1000金额及原来源不动。工具与守护技能将propose_goal的准备效果明确为无需此前确认、不保存；真实父确认才生效，不追加流程或替Agent造提案。render回执分清changed初始化与当前unresolved块，并提供实际ID修正合同，不自动清错或隐藏失败稿。

另有验收前置的合成legacy缺selection_basis触发NotFound；生产0.15提交9b3c291已要求basis非空并保存，此夹具缺字段不是合法旧生产格式。然而valid_goal确漏检后续必读字段，此次补缺失／非String／空依据拒绝，不伪造默认理由。旧合法记录不变；原夹具补齐与产品validator修复分别记录。唯一在线63114已停。独立SDKconsumer77993停止后，source6fb7a708的静态渲染尾链4/4通过：原208B失败稿保留，named局部成功仍interface_success=false／unresolved __document；render_ui.blocks同ID真实修正后才interface_success=true与诊断清除，四成功siblings对象／id／index／revision／raw_source未变，未测WidgetUID或像素。生产propose_goal实际返回proposal_prepared_not_saved、store计数0。报告build/research/rail-integration/partial-render-probe/guardian-irb3a7nn/report-safe.json；固定ensure_interface_facts仅为隔离静态输入，不证明完整图或真实业务绑定。三坏依据＋合法goal的实际encode／write／read及500／1000价格范围已有原件guardian-live-contract-probe/guardian-n69zox61/report-safe.json；该报告同时保留city前置FAIL，不拼成全组通过。此前mock／accuracy／city及测试uid()前置失败材料均保留，未为夹具修改产品。所有实例已停，零模型／供应商；最终main317c97a1只额外同步SDK915453c3的按需原语资料、marker与catalog，主题prelude2280不变。check／stamp／build／doctor全通过，source dc2dabbe／binary8214149f，回执build/research/runtime-upgrade/rc6/guardian-contract-preflight.json；封包不启动原生或供应商，pgrep空，正常HOME36calls／655511tokens及d1f154e4 SHA保持。随后SDK仅追加按需语言资料splash-entry.md，prelude与上述守护修复不变；最终main20a56ff3／source d2edd65c／binary328d4906，SDK3975fe7f。单次sync／check／stamp／build／doctor通过，回执build/research/runtime-upgrade/rc6/sdk-entry-preflight.json；正常HOME36calls／655511tokens与d1f154e4 SHA前后相同，所有自有实例已停，未新增模型／原生验证。随后真实guardian复测仍由root单独授权，当前在线失败不改写为成功。

## 已交付行为与责任

Agent 继续自主选择检索、路线组合和界面工具。propose_goal 只准备提案；父应用实际确认按钮才保存。用户查看本轮候选后也可通过“用当前查看方案准备替代”进入同一个提案函数，不需要模型续接或固定候选模板。提案绑定查询及目标版本，拒绝、终止和旧版本不能覆盖当前目标。

冷启动恢复活动目标并新建核验循环，也提供主动核验。保留绝对期限、总预算、目的地、偏好及风险；累计支出由用户确认，剩余预算允许为负。核验明确区分估计成立、失效、信息不足。原选定路线只有对应的新证据才能认定成立；不同路线只能作为替代候选。

选定路线物化必要路段、几何和报价依据，公开历史引用为 saved_goal_route。业务写入使用完成标记、上一份确认备份及删除墓碑，处理宿主截断写和容忍部分 JSON 的解析行为；存储失败不推进内存。父确认区和详情视口随目标状态更新，已知无有限高度的顶层滚动容器会返回诊断，由 Agent 修正，不自动改稿。

root 负责整合与文档；guardian_design 负责状态和确认权属判断；guardian_impl 为生产源码 owner；guardian_verify 负责原生测试、在线证据及宿主实例。全部测试实例已关闭。长期契约已回流 README、docs/architecture.md 和 toolchain/README.md。

## 验收依据

- 最终源码 main SHA256 为 e31f3e52bd888a694e1394faf1e20f4ad9f3acc0cc8273bd47579e443f77dfa7；bundle 聚合摘要为 9da632d22af96bd32eb770947f995ca6a372d4a1a720bc9246b3402d918d5656。make check、make agent-build、make agent-doctor 通过。
- 官方无补丁宿主首屏降级回归通过，证据为 build/smoke/stock-startup-76x9yexx/report.json；该检查使用手机视口，不代表 Android 模式或完整功能可用。
- 最终原生 32 项全部通过：真实确认、候选查看→准备→拒绝→再次准备→确认替代、费用、版本冲突、重启不恢复模型历史、损坏恢复、写失败、结束删除和布局边界。路线为合成数据，实际执行原生控件点击。入口为 python3 tools/smoke.py --guardian；私有报告位于 build/smoke/navigation-harness-05vb9f0g/verification-safe.json。验证 owner 已查看四张关键截图。
- 第二轮真实 M3／高德完成初次规划、确认目标、确认已花190元、重新查询及报告核验。保持200元总预算与原绝对期限，剩余10元；取得5条新候选，因机场 T3 末段约312米没有直接证据而报告 unknown，未自动替换。13次初查询加11次重核验，共479509 tokens；374条连续 trace 保留，零生成渲染诊断。私有报告为 build/research/journey-guardian/online/round2-safe.json，root 已查看目标详情及最终核验画面。
- 在线源码 main 为 fa23a1170c5db616209c57eae2a666e69f8ffcf627faf165e13406fb1390bf07，bundle 聚合为 608e8a7d760258af0295d4140e6e10ec63de67a2ca881a69df1c944cb3573cc3；后续本地候选入口与固定理由显示由最终原生测试补证，未重复付费查询。真实在线没有得到完整可行替代，替代确认机制由合成路线和真实点击验证，不能混称在线替代成功。

两轮均使用 macOS arm64 配套宿主 Android 样式，临时定位、日历、笔记及支出为隔离演示材料，交通与模型请求真实；不是 Android 真机。测试额度临时提高至200万 tokens，继承既有账本未清零，最终累计75次／1432469 tokens；生产默认100万额度未改。

## 失败诊断与接续边界

首轮在线不能算通过：模型没有新查交通或报告核验，读取旧 Route ID 失败后按缓存声称仍成立，父状态停留待核验；还发现旧确认子控件残留和详情视口位置错误。完整失败材料保留于 online/round1。随后引入历史路线稳定引用、历史与当前核验分离、新鲜候选事实、明确技能说明及本地可见性修复，第二轮取得上述新查询证据。source_sha256 在构建记录中代表整个 bundle 聚合，不能与 main_sha256 混用。

用户改变进度后，首版不可靠地推断旧路线剩余路段或已乘车状态，而是报告信息不足并探索当前位置替代；新剩余路程与旧整程的费用时间差也可能未知。普通前台返回事件尚未验证，仅冷启动和主动按钮有完成依据。官方原版宿主只验证首屏降级，完整功能仍依赖锁定配套宿主。生成界面仍可能遗漏信息；没有全局最优、穷尽路径或准时保证。

非阻塞 UI 观察：故意触发旧版本提案确认错误后，新提案页面仍保留该错误文字，成功保存会清除；不影响拒绝或确认的状态结果。未扩展后台、账户联动、真机或新演示视频。
