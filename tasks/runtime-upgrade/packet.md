# 官方宿主兼容与初赛反馈落实

状态：2026-10-10，落实 [App Hub #116 的赛事反馈](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/116#issuecomment-6077995438)。评审版本为 v0.13.0／702ea6c，初赛结果入围，65/100；这不等于商店上架或完整业务验收。

## RC6 正式升级接续

2026-10-12，用户明确“octosense有更新，赛事方要求升级到最新版”，root授权 runtime_update 正式采用已隔离验证的RC6，负责lock、必要补丁、构建wrapper、工具链说明和宿主setup/build；main及官方定位迁移由rail_model持有。双方确认所有自有实例已停并冻结host/stage后开始迁移。旧宿主源码完整保存在同工具链的OctoSense-pre-rc6；私有数据与真实ledger不重置、不移出，升级前SHA保存于忽略的formal-adoption.json。

当前正式源码setup及tree/依赖校验已通过；lock选发行f9f6fea9与Rust1.99.0，wrapper精简为navigation_overlay，不再应用旧定位、Maps pick、Replier、font gate覆层。model.chat、UI／地图、fs.read_async／UTF8分片、checked timer继续由两份RC6本地补丁提供，权限提示来源保留新版约束。root另授权窄shared_tools.call/cancel，仅通过官方relay消费notes.search/read，新增app-notes而不加kernel。桥请求身份、取消／isolate关闭／超时／迟到和discovery边界5项与官方relay44项回归通过；全新隔离Notes经UI创建合成笔记后search／完整read成功，closed回app_not_running，不访问真实Notes存储。metadata修复后context_sources核两方法describe可用、actual not_granted→needs_connect且无records，5项通过、native_errors=[]，正常停止。main5e61ab4f冻结后正式build/doctor已通过，host tree a618c245；Notes回调补宿主call_id代际守卫，原5项边界仍通过。官方check补必填profile后已盖摘要，但stock gate拒绝notes.search（未提供项目宿主offer）；root采用薄desktop项目预检，复用官方完整gate和原HostLimits，仅共享Navigation两Notes工具声明。正常包/未offer/digest及其它appid四项边界通过，最终main168396e0冻结后配套项目check、stamp、正式build、doctor全部通过，host tree51089110、source集合3a7f2778、binarya2a1d4e2；不冒称无补丁通过或发布就绪。默认HOME旧19账本SHA6682e8始终未变，490账本独立属state-round30，下一E2E由其owner显式clone继承。formal迁移未启动native或调用provider，未重置任何账本。Material7项与定位6项离线集成检查已通过并全停机，最终pgrep无octosense。正式runtime迁移交付已完成；root授权的后续真实E2E接续，尚不宣称正式应用业务或个人背景验收完成。详情与隔离证据见[RC6调查](rc6-investigation.md)。

## 人工继续失败轮次封包

mainowner交接人工继续main11742656，5项必要组通过／全停后check（stamp）→build→doctor均通过；host／patch／lock保持，source集合545b4d1d2c38372e1b5f1dffb88151174af90973ec21b1dcac503981d2d8677e／binary6ad1e1285c03ce2f3024d2619ef8d56fc168f18fd351331898250d86680e8ee5，receipt归build/research/runtime-upgrade/rc6/manual-resume-preflight.json。封包owner0native／provider，默认账本fresh基线与结束SHA匹配、pgrep空。原E2E owner重开只留主输入给用户，旧失败live会话不冷恢复，不执行隔离probe返回工具、不自动重放／付费规划；后续同窗口可由用户显式人工继续。

## 用户现场两次模型超时只读判别

root授权只读当前79292／53163日志与386seq原trace，不重启／新请求。私有chat诊断正常记录call_id38／47、phase chat_result，均为等待HTTP status line超时，无HTTPstatus或body，不能猜quota／协议／模型能力。原run4 step6及run6 step5分别120.164899／120.203141秒，对齐HTTP120秒；chat宿主130秒为10秒余量，本次无提前截断冲突。同实例25次成功1.39–21秒，不是全部服务不可达，仍不能区分供应商延迟与间歇网络。

root随后采纳advisor，明确授权一次原380body隔离长等待POST，仅HTTP300秒、同ureq2.12.1/tls及实际profile／endpoint／model／参数，保存不执行工具。8.6秒隔离编译后唯一请求HTTP200，header91.003秒／complete91.094秒，5结构化tool_calls未执行，usage43445+15797=59242tokens，response115850B。结果低于原120秒，不能据此证明需加超时；同body间歇性成功，下一恢复策略由root／应用owner裁决，不自动重放或执行。原宿主账本未写，这一次明确授权外部调用usage单独保留；安全回执long-deadline-attempt/receipt-safe.json及原response私有。

安全证据归build/research/real-context/user-model-failures/host-provider-timeout-evidence-safe.json；官方M3工具文档支持完整thinking／非流式调用，没有120秒完成保证。建议不先扩timeout或改代理；若root需要活探针，可一次既有primary模型发现GET仅看状态／耗时、零生成，不重放个人body，且无法倒推旧两次原因。此owner0provider／native／源码改动，主应用caller与生成问题归rail_model。

## 日历列表UI封包

mainowner日历列表UI修复main2506f383及Android合成5项通过／全停后check（stamp）→build→doctor全部通过；host／patch／lock保持，source集合ddea1379d085be50e442d4b92a1197033bcbbaac1495193363edceb0ef40f64d／binary56fd343df1a239819179e5c1330e84c521df071dd5a7b7f70495640af1986eea，receipt归build/research/runtime-upgrade/rc6/calendar-ui-preflight.json。本owner0native／provider，pgrep为空，默认账本fresh基线匹配。原E2E owner按root唯一授权重开已授权正常HOME，仅重放list确认实际buttons可见，不公开名称ID／代选择／events／规划。

## 日历授权开发包声明修复

用户亲自触发授权后RC6返回host_not_configured。root授权修复开发包装，rail_e2e停止唯一41618后检查：dev／hidden已走既有定位.app，但profile级Info.plist只有定位说明，未包含Calendar两字段。packaged_host现从锁定官方desktop/packaging/macos/Info.plist合并定位／日历四项用途说明，维持bundle身份、二进制与权限行为，不新增全局授权或个人数据读取。相关所有start caller共用该包装路径。

窄fixture检查覆盖sidecar遗漏／错误来源与官方模板缺字段拒绝；实际.app四字段逐字匹配锁定官方文案、包内binary SHA301f8848与原binary相同、doctor通过。tools agent.py SHA3afe5952，main36dd92c9／source198dde5e／host／patch／lock不改，无需重编译或stamp。receipt归build/research/runtime-upgrade/rc6/calendar-packaging-receipt.json；账本8923b604前后相同、0native/provider/permission/events、pgrep为空。已交原E2E owner唯一正常HOME重开展开，用户自行重试许可，未声称真实授权完成。

## 日历冷cache初始化封包

mainowner交接status前置生命周期修复main36dd92c9，必要7项通过／全停后check（stamp）→build→doctor均通过，host／patch／lock保持。source集合198dde5eec1796a1027c13f8d8d6e0dd20eeaedb618fc7c8ea97aecf5f5e8410／binary301f884894d543a41cb7afcd29e3eb57934cf732a3d30227ca52e1b55845ebf5，完整身份归build/research/runtime-upgrade/rc6/calendar-entry-preflight.json；开工捕获默认账本新基线，封包后原SHA匹配、0native／provider／pgrep为空。原E2E owner随后仅正常个人HOME可见展开供用户自行授权，不代permission／choices／events或规划。

## 背景权限入口封包

mainowner交接背景权限入口可见性窄修main11b85622，正常窗口已停后check（stamp）→build→doctor通过；host／patch／lock保持。source集合1653eeec6a32757f72fba5f07710d3da22d734bb3460b3bad589dd7ee0f3672a／binary4aae4b581bab5f9d2ef457ae42ba7a73c3c3399f8f06e9658531f7f767762404，完整身份归build/research/runtime-upgrade/rc6/context-entry-preflight.json。本owner0 native／provider、pgrep为空，原38账本SHA365ecc5d保持；当前默认HOME账本SHA8923b604，未取得开工新基线，不冒称与旧19相同，root采纳当前记录且不追溯／重置。原窗口owner随后仅实际展开／收起／再开截图检查，不代授权／个人读取／付费规划。

## 正式40当前树句柄封包

root授权main460d58d1统一current-tree helper覆盖旧句柄触点后直接封包，未重复child组；check（含stamp）→build→doctor均通过，host／patch／lock保持。source集合634d0b7c941c1724c5bbf762c8fa763d94f5b1957f3370eab35d3cf86d1ecc4d／binaryce1710d8642ec59c558c9baafe0264152c1ffcf23d5126a95cd0cedfdaf382d6，完整身份归build/research/runtime-upgrade/rc6/round40-preflight.json。pgrep为空、本owner0 native／provider，默认19与原38真实633calls／37544171tokens／SHA365ecc5d账本均未变。后续唯一 cold40 已通过实际 Android 样式重应用、原 S4831 卡片→详情→地图像素→返回／重开；root查看实际截图。43事件连续，0新模型／规划调用，原快照与六块源码、账本均未变，实例已停。证据归 build/research/rail-integration/e2e/cold-restore-round40/result-safe.json；保留非阻断初始化诊断，不冒称零警告。这仅是恢复修复验收，真实在线使用第38轮05130a81，不能说第40轮重新在线通过。

## 39冷恢复树生命周期判别

root授权只读锁定平台，未改host／构建／启动实例。句柄固定UID，当前树重获路径为ui.generated_area或ui.block_overlay的child(index).child(0)，没有公开全树reapply完成通知；WidgetAsyncDone仅单次render结果送原UID。render_style同id同类型保留子WidgetRef，普通render重建动态子节点；父preserve重跑顶层启动timer，main无条件trip_load→trip_restore可另触发普通render／重安装，所以不能把第二批child全归为平台style强制换实例。建议main统一所有block操作从当前树重获，并以当前handle mailbox初绑定通知判就绪；detail_text错误是否同根因仍待应用owner必要单组区分，不盲延迟或重装所有DSL。安全源码证据归build/research/runtime-upgrade/rc6/cold39-lifecycle-evidence-safe.json，已交root／rail_model。

## 正式39冷恢复封包

root采纳恢复原38六区块组5项通过／全停，冻结main68bfac72，授权既有check（含stamp）→正式build→doctor；三项全部通过，host／patch／lock保持。source集合5a81779d45470cf139cf1a7ffe76d52fe48b68ca756a8090dd63f61c23a471c2／binary24a5d390c267f257735d68e0a00759fa120cde7c05ad3d2c3f2d2113118b7d47，完整身份归build/research/runtime-upgrade/rc6/round39-preflight.json。pgrep为空、本owner0 native／provider，默认19账本与原38真实633calls／37544171tokens／SHA365ecc5d均未变。后续root只授权原38snapshot冷恢复卡片／详情／地图／返回检查，不重新付费规划。

## 正式38最终封包

root与应用owner分别解码原报告确认提示示例无反斜线，暂停原因仅为工具输出外层JSON转义误读；原main05130a81保持，无新native组。恢复授权后check（含官方stamp）→正式build→doctor均通过，source集合6a182be5818195d47ea0ea866cab0da85b1ca0a0d3a8f3c68afc852450971e2d／binary18c46f8476f4dc8361f3a932788c7833e671d6fb4176375804a32abe23d1cafc，完整身份归build/research/runtime-upgrade/rc6/round38-preflight.json。pgrep为空，本owner0 native／provider，默认旧19账本SHA6682e8及原正式37账本SHAcdcb172c均未变。下一在线38由root单次授权，E2E owner显式clone37真实608calls／35583597tokens，只清新clone旧devtrace、原HOME／归档保留。暂停日志保留，不作为成功证据。

## 38 必要宿主修复与隔离验证

root授权三项精确修复，未扩其它服务、响应、文件或脚本预算。补齐App Hub真实pump二级参数门：仅model.chat为2MiB，其它仍1MiB；此前37前测试只证明Makepad桥入队，不证明pump，本节更正其证据范围。Replier只读request_id复用现有编号。Cargo四个App Hub实现crate以锁定本地path实际链接，app-contract仍为同固定git来源，Cargo.lock只移除四条source、无版本刷新。

真实Cx／Splash→App Hub pump→HostService离线测试已通过：约1.114MB聊天到dispatch；同pump参数检查对其它服务>1MiB及聊天>2MiB拒绝。合成HTTP503与nochoice子进程实际私有日志含call_id／phase／脱敏detail且无fixture key，公开通用拒绝不变。fragment代码态首个反斜线引号诊断固定为`unexpected escaped quote outside string`，合法字符串／路径／regex／注释不触发，默认流式tokenizer不变、不自动unescape；四份37原稿准确报6:32、6:32、7:32、3:58。仅必要组通过，0网络／provider，未启动桌面实例。

补丁与lock已同步，hosttree62df0767717306087e12f4fc0f4c1fdb32f95cea／Makepadtree2f5384d5013646e0c242755684f0924e38d7d5d7／Hubtree05e7b843fbcf85b11ab4c034d0fa14a993138560，source校验通过。证据归build/research/runtime-upgrade/rc6/round38-host-fixes-evidence.json；独立binary编译通过，SHA3580d802d16601d146393cbbf58cc4b5f19a9b0ff3a230e81678d82fcb271b2b，pgrep为空；交应用owner唯一四原稿工具反馈组。root采纳五项应用消费组后曾授权封包；随后发现提示示例解码值仍有反斜线，已在make check编译阶段按root指示停止自身runner，未stamp／stage／agent-build。待应用owner单例修正、新freeze／全停与root再次授权。暂停回执round38-preflight-paused.json；不调用供应商或改变原账本。

## 正式37供应商通用错误判别

37全停后只读原seq306、request301及native.log：step20回is_ok=false／provider通用错误，请求约964038B在当前2MiB参数界内，没有invalid_tool_protocol证据。chat.rs99将transport／非2xxHTTP／malformedJSON／nochoice／invalidassistant的具体原因存入Refusal.detail，probe已对HTTP／transport摘要去key并截120字；media/mod.rs425却仅调用Refusal.to_string，Display只输出code与公开通用message，丢失detail且这条路径不写宿主日志。现有37回执／native原件无法恢复具体HTTP状态、供应商码或响应摘要，不能猜quota、context或模型能力；runtime1073指令限另行保留不冒认为供应商原因。

root已授权并实现最窄私有诊断：仅model.chat失败记录既有已脱敏detail及app／isolate／原request_id／chat_result阶段，公开generic合同保持，不retry。原37具体供应商原因仍不可恢复，不因新诊断推断旧原因。原只读证据归build/research/runtime-upgrade/rc6/round37-provider-error-evidence-safe.json，当前验证见下。

## 正式37前构建接续

root采纳应用case36-un8h56l7同VM消费10项通过／native_errors为空／全停，冻结main2d25c613及技能资料，授权既有check→stamp→正式build→doctor。四阶段全部通过；新hosttree46c0f897／Makepadtree d7a73b7a固定精确chat请求2MiB与单片UTF8原语，最终source集合1e60be2ef01ed11f6830e91b51c77fe3d9d890131ab721bb326f15d9098efb3f，binary1209c9f1d9d5908abf9617b89f0cbcdfb5ff9dd1fca746efbe5fcf04c31aaf3e，完整身份归build/research/runtime-upgrade/rc6/round37-preflight.json。pgrep为空，本owner0 native／provider；默认旧19账本SHA6682e8和原正式36账本SHA39d9da3f均未变。下一在线37另由root单次授权，owner显式继承36真实588calls／32905601tokens，仅清新clone旧devtrace，原HOME／归档保留。

## 正式36请求容量与37接续

36全停后重建step12参数1285108B，应用compare保24方案去重复详情后仍1107830B；超过既有host.request编码后JSON 1MiB。root授权精确model.chat参数2MiB及单片UTF8原语，不删历史／graph，不放宽其它服务／输出／fs／脚本或费用预算。最早gate在Makepad splash_host.rs，入队前原生boundedJSON Rust遍历，不计逐字Script指令／不charge Script heap；catch之前vm.err_clear使Script现有try无法取得具体错误对象，拒绝阶段与字节数由应用记录，不把原36的泛catch伪称已拿到精确native原因。

已实现service==model.chat 2MiB，其它仍1MiB；原queue每VM4MiB／global16MiB保持。String.utf8_chunk(offset,max_bytes)只复制一片，UTF8字节offset有限非负整数且真实边界，max至少4整数，末尾返回空String，len为UTF8bytes。两项原语测试通过，实际VM桥单组较大聊天入队／其它两服务仍拒／聊天超过2MiB拒通过，0网络。补丁／嵌入patch／runtime lock已同步，Makepadtree d7a73b7a51181c467e688e5fbb0d0dc521606020、hosttree46c0f8978f1e7fa632fb0c55927ae468660fea66。独立target desktop编译通过，binary SHAaf4ecd80已交应用owner进行唯一离线消费验证；本owner未启动native，无正式stage／target构建，最终封包需root最终freeze授权。日志归build/research/runtime-upgrade/rc6/round37-{utf8-tests,gate-tests,isolated-build}.log。下一真实37继承实际36账本由root另行指定，不使用默认19或旧测试账本。

## 正式36前构建接续

root采纳binding-ikbt8agr必要原生4项通过／全停，冻结mainb868a635，授权既有check→stamp→build→doctor单次。四阶段已通过；hosttree／lock保持，source集合86414b162d4e8228714f7afd9a282da306f0a70fdb239da3daab2d3390d6ad03，binary187c960fa868a875882eea1329f05ca2f8d194a5302cf059c2e8b33098458be9。完整回执归build/research/runtime-upgrade/rc6/round36-preflight.json；pgrep为空，本owner0 native／provider，默认旧19账本SHA6682e8未变。正式36另由root授权E2E owner显式继承35真实577calls／31767377tokens／SHAa69630fe，仅清新clone旧devtrace，原35HOME／归档保留。

## 正式35前构建接续

root采纳应用owner的局部invalid_tool_protocol守卫及4项原生边界，全停后冻结main5b25619e，授权既有check→stamp→build→doctor。四阶段已通过，宿主tree／lock不改，source集合8e392ea9de3f2eba6ee03469c034d586f3cbfc1b7da617bbe2b6050589b12242，binary97317a072889b080ffab118c36ebf4bd8ef4a37cb6f19481d8a34e04d6b94c5b。完整回执归build/research/runtime-upgrade/rc6/round35-preflight.json；pgrep为空，本owner未启动native／调用provider。默认HOME旧19账本SHA6682e8不变。下一35由E2E owner显式继承34的562calls／30398837tokens／SHAa3a67646，只清新clone旧trace，原34HOME与归档保留。

## 正式34供应商协议调查

34已正常终止并全停。runtime_update只读当前锁定host与13份真实请求／响应：隔离profile为MiniMax-M3、minimax-cn、OpenAI、https://api.minimax.cn/v1；宿主仅复制args并加入model／stream:false，发至官方/v1/chat/completions，返回完整原response。前12响应均structured tool_calls（共39工具），第13finish stop、无tool_calls，content含MiniMax内部控制标记。13次tools／auto／reasoning_split相同，应用owner已核完整assistant历史保留；没有宿主丢弃tool_calls的证据。

官方[M3工具文档](https://platform.minimax.io/docs/guides/text-m3-function-call)要求结构化调用和完整thinking历史，没有将hosted普通content的内部标记解释为调用的规范。Pi cd8bdf75（2026-10-11）MiniMax使用Anthropic，OpenAI解码只消费结构化delta.tool_calls；不是此rawcontent的正式normalize依据。官方repo issue31有类似泄露报告，但经第三方gateway且无厂商原因确认，不能证明本次直连随机性或归因模型能力。M2自部署解析说明不适用于本次M3 hosted响应。

建议root选择确切供应商控制标记泄露的显式协议失败，保存原回执，不执行文本、不自动retry、不forced工具、不换模型；当前未授权实施，host／lock／patch／main未改。实际schema内容和响应类型之间的触发机制仍未证实；若要可靠恢复需要供应商契约或另行授权协议迁移，不能凭一次异常新增解析器。安全证据归build/research/runtime-upgrade/rc6/round34-provider-evidence-safe.json。日志212事件虽连续，但status incomplete仍保留，不冒称完整。此次0 native／provider／build。

## 正式34前构建接续

root采纳rail_model冻结main2c01a96d及agent.py6dcbb401、实际raw body/source写入与派发7项原生通过、reader18项通过和全停机回执，授权既有check→stamp→agent-build→doctor一次。宿主RC6、Rust1.99.0、host tree51089110及lock保持；项目check、stamp、正式build与doctor全部通过；最终source集合7ac615f4、binarydf198f90，receipt归build/research/runtime-upgrade/rc6/round34-preflight.json，pgrep无octosense。不启动native／调用provider／扩测。下一正式34由原owner显式继承round33的549calls／29475759tokens／SHA3c7284账本，仅在新clone清旧dev-trace，原HOME与归档保留；默认HOME旧19账本保持，不能替代。

## 正式33序列化失败判别

33已导出并全停后，runtime_update只读锁定RC6源码，未构建／启动native／改锁或预算。Makepad `heap.rs::to_json` 将有界长度预估的None统一记为usizeMAX；None包含容量不足、循环／深度与算术预估失败，不能凭该哨兵认定递归。rail_model重建的step20请求为75messages／body910273B，trace内层1074858B、外层1404094B，纯JSON树；它们超过错误时heap余量600716B，支持额外trace脚本字符串峰值触发retained cap。此前相近step19成功不否定累积余量耗尽。

`heap allocation` 表示持续retained cap，不是新timer自动清零的单入口预算；`charge_allocation`将cap标为exceeded，后续`new_with_proto`返回冻结poison对象，解释次级push_all_fn_args无prototype。`host.request`反而用`to_json_string_bounded(args,1MiB)`生成Rust临时String，不charge Script heap；910273B请求本身仍在该边界内。普通try不能捕获allocation Bail；当前checkedtimer的错误对象／字符串仍在同耗尽heap里分配，其现有测试只证明wallbudget恢复，不能声称heaperror安全。GC能reconcile cap，但isolate pump仅按对象／字符串count翻倍heuristic触发，不保证heap failure后即恢复。

后续raw field写入合同已只读核实：锁定Makepad `splash_storage.rs:576–602`直接接收Script String并复制Rust text写文件，不经过host.request或JSON编码；成功返回NIL，失败为可捕获的script_err_io，而非bool。try中成功写后才commit引用是正确合同。单文件限额为1MiB raw UTF8 bytes，全jail默认／本项目普通policy为16MiB；原20.77MB jail会拒新写，新隔离clone清旧trace而原件留档，无须改宿主预算。应用owner实际910273B body／444087B source原生写入及reader／模型派发单组7项通过，reader18项通过，实例全停；等待最终freeze后按root授权原构建链收束。

建议先由应用owner移除业务entry的大trace重复序列化，保持完整消息与诊断归属并实际离线重放；不机械加堆，不把普通timer或try当恢复保证。当前没有证据证明serializer长度计算错误；若修复后仍有独立heap恢复失败，root再界定窄host repair。原日志与重建metadata归build/research/rail-integration/e2e/round33，源码机制已直接交rail_model与root。

## 目标与授权

用户明确要求“我们先落实其给出的改进建议吧”，授权三项必要的实现、实验、验证与文档：修复官方原版 card-host 首屏错误；将 MiniMax 直连迁移到宿主 model 服务；补充无补丁环境下的实际降级演示。延续自主 commit 授权；本轮先完成可审阅的改进，不自动重打已发布标签或替赛事方接受结果。既有 M3 在线验证和隔离模拟位置授权适用。

保留模型自主 function-calling loop、工具结果和完整运行证据，不改为固定 workflow，不恢复旧查询、不新增问答或业务 fallback。官方缺少原生能力时呈现准确边界；不能用 patched host 的通过冒称 stock 兼容。密钥与原始日志保持私有，仅清理本任务实例。

## 当前事实与责任

- v0.13.0 已公开，Release 和 Hub #116 已提交；赛事方在 2026-10-09 报告官方 card-host 首屏 main.splash 约2428行触发 empty-stack。
- stock_startup 已在官方 App Hub 7b36c8af 原版 card-host 复现启动rect调用导致empty-stack，并完成最小能力门修复：main SHA72d3c8a9。真实390×844首屏、禁用点击与回车回归通过；patched Android 9项合成回归通过。main已交host_model接力，永久检查tools/test_stock_startup.py用于最终再验证。
- host_model 已核最新 OctoSense 40ca21da 仍仅有 model.complete one-shot，不能透传 messages/tools；已在同一 ModelHost 内新增窄 model.chat，复用 profile/transport/凭据与账本，并完成应用模型传输迁移。现有 complete 保持；扩展尚待上游接纳。
- stock_demo 已完成29.63秒无补丁补充视频及核验记录，不覆盖已发布96秒演示。
- root 维护任务与长期文档、协调接口和集成验收，并依据最终 stock 画面制作降级演示。当前工作区开始时干净。

以前的源码、宿主、路线与发布证据移到 [初赛调查与交付记录](preliminary-evidence.md)，其中“最新”等时间词仅适用于当时版本，不作为此次运行结论。

## 完成依据与下一步

1. 使用明确SHA、无本地补丁的官方 card-host 加载真实 bundle，实际可见首屏；缺能力入口不再触发原生错误，界面准确说明剩余依赖。保留截图和宿主日志。
2. 模型迁移通过真实 M3 的 function call → 本地工具结果 → 继续模型闭环；历史、取消与失败处理保持，应用不再读取或发送 MiniMax key。若官方服务存在缺口，先依据实际契约裁决最小路径。
3. 官方card-host手机视口下记录无补丁首屏与降级操作（不冒称Android模式），更新演示／README／工具链／架构的实际范围；本地包检查和已有受影响回归通过。

下一步：三项反馈改动已完成；root完成最终封包、构建核对与提交。独立的生成UI残余保留在本任务接续，不声称完整任务验收通过。

已采用 advisor 判断：直接把历史塞进 model.complete 的 input 会改变 function-calling 语义，不能作为迁移。新增 chat 必须复用同一宿主授权和 ledger；one-shot 的 schema、URL、32KiB输入／16KiB输出约束不成为 chat 内容转换。当前取消继续丢弃迟到回调，不声称远端HTTP取消。历史实际14轮消耗413,501 tokens，默认100k/day不足；用户已允许充足M3真实验收，本项目隔离开发配置可通过现有宿主额度入口调整，保留历史usage，不改全局默认或绕过账本。root采用tokens_per_day=1,000,000，per_minute=20／calls_per_day=100，仅本项目隔离开发Navigation覆盖，具体最终行为回流工具链说明。

首屏证据：build/smoke/stock-startup-o575cvuf/report.json；patched回归：build/smoke/navigation-harness-ru0lqrmv/report.json。root已读取同binary前后错误对照并查看真实first.png；仅证明首屏降级与保留patched路径，非完整在线任务。

无补丁补充视频已完成：demo/Navigation-stock-demo.mp4（29.63秒、中文旁白/字幕、真实截图剪辑），采集main72d3c8a9、官方card-host7b36c8af，非Android模式。媒体owner解码与音轨检查通过，root查看第二镜头关键帧；仅演示首屏/缺能力，未覆盖后来模型迁移。公开evidence脱除私有路径。

root从两份既有私有完整trace仅统计model_dispatch时间，14请求运行最大7次／60秒，11请求运行最大11次／60秒；因此保留默认6/min会造成已知回归，将仅隔离开发应用覆盖设为20/min、100/day、1,000,000 tokens/day。不是删除宿主准入，使用计数保持，应用不能设置额度。

模型迁移进展：main b607ed3a；真实M3原生两轮工具闭环通过（2次、917tokens），实际host.request/registry/agent_pump/tool_result保留call_id；Rust两项chat集成与19项原complete回归、launcher凭据归属/额度保计数、11项trace读取归档检查通过。实际产品迟到host回调隔离检查通过。后续完整Navigation在线demo结果见下；不作为业务完成声明。

迁移后正式单次在线demo已结束：17次请求、38工具、491,392 tokens、最大请求237,579 bytes；完整trace316事件连续，无model service／rate／budget错误，自有实例关闭。最终画面空白（root已看截图），与rendered=true不一致，离线归因见下。不得把该轮记为完整UI通过。模型两轮、迟到回调、Rust/trace回归可独立采用。

root最终stock复跑通过：build/smoke/stock-startup-fdo1h576/report.json；make check通过（含model能力、仅高德和滴滴应用主机）。盖摘要后doctor提示需重新agent-build，为正常封包顺序，待最终源码/版本确定后build→doctor。

离线归因已完成：build/research/host-model/render-replay-visible/保留原稿、真实回放和对照截图。summary/explanation/routes均complete、visible且无原生诊断，但实际高度为0；仅将原稿顶层ScrollYView改为内容自适应View的隔离实验恢复654高路线卡片。详情事件另引用不存在的widget ID。未修改生产生成稿、未添加自动布局fallback、未追加M3调用；该问题属于生成布局与渲染成功判据的接续修复，不属于模型消息丢失。

当前应用版本更新为0.14.0，区别于已发布初赛0.13.0；不重打旧标签或覆盖旧Release。

最终封包：0.14.0 的 make check、make agent-build、make agent-doctor 均通过。构建输出的应用包源码摘要为fd5b88974dc4c0b38bf5560aac562adda465e040dbfcb24f0596450b96c87284；main源码仍b607ed3a，模型迁移后stock检查无需因仅版本/摘要变化重复。日志归build/research/host-model/final-{check,build,doctor}.log。三项反馈的本仓库改动交付完成；上游接纳与生成UI零高/错误控件引用是剩余事项，尚未向赛事方声称验收通过。
