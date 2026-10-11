# 接驳探索与技能分工

## 当前恢复点

已落地并验证本机Navigation显式无预算上限、M3思考与消息保留、技能读取链审计、来源工具契约和model.chat等待期限修正。真实M3在受控交通数据中自主取得一次完整低价混合候选（打车接地铁，10元／名义27分钟，候车未知）；不是全局最优或多场景稳定性证明。完整UI交付仍未通过：成功路线轮在旧60秒桥超时停止，随后同上下文单请求已在新宿主成功，未执行返回工具。当前无实验实例在运行。后续若推进UI验收，使用最终构建及真实Android样式，保留完整trace；不要将已有路线证据重跑当作新结果。

## 目标与范围

用户最初要求：“现在我们来专注看看路线算法（本质是提示词）还有什么可以改进的，我们和普通导航最大的不同是，进行更多的接驳”。调查完成后明确授权：“按照这个方案处理，并且再审查一轮 agent 收到的工具和提示词，进行精简、去重、边界与职责澄清；然后开始前面确定的……改进项”。当前范围为实施技能重组、system及工具契约精简、接驳关系投影和必要验证，不改变自主Agent循环或重写底层求路器。

用户随后认可问题定位与方案，并强调推进三项改进应引入“技能机制”，避免系统提示词持续膨胀。已核实现有 name/description 目录、read_skill(name,path) 和引用文件的渐进读取机制；需要改善的是知识组织与发现，而非新增加载框架。按这个偏好修订方案：独立的混合接驳技能承载搜索策略，系统提示词保持简短，工具事实投影独立改进。

保留自主 function-calling loop，由 Agent 决定查询与组合；代码计算时间、费用及实际连接。增加接驳的目的是找到满足目标或更有价值的路线，不以工具调用数、换乘数作为效果指标。不加入固定查询顺序、强制候选数量或新输出限制。

## 已核事实

基线为 main 的 c1ed592，工作区开始时干净。guardian_impl 完成工具调查，guardian_verify 完成三份真实 M3 记录复盘，guardian_design 提供策略判断；主 Agent 已核节点注册与路线详情投影，并读取复盘依据。调查阶段未修改应用或重新请求线上模型；本轮已获授权开始实施。

query_route 返回真实供应商节点，extend_route 可从 origin 或已有 Route 的实际末端继续检索完整新段。现有前向工具可以实现首段、末段和中段换方式；没有独立反向后缀查询或复用旧 legs 的组合入口。此前普通公交方案不能裁切票价，新段仍需按前序抵达时间实际查询。

节点注册保留了经停站，但丢掉其所属候选、公交线路及先后顺序；query_route 的 steps 有文字线索，部分分段耗时为空。get_route 能返回分段实际耗时，但公交详情只提供上下站名，不返回有序 stop refs。search_places 注册真实图节点，回执却未直接提供相应 node_ref。相关代码归 bundle/main.splash 的 register_route_stations、query_route_summary、interface_route_facts 和 search_places 分派。

真实记录安全复盘在忽略目录 build/research/transfer-exploration/summary.md 与 timeline-safe.json，原 trace 路径和 seq 在复盘中保留：

- trip-list：60分钟／100元到海雅缤纷城，E36约2692秒／200分，已满足估计条件。返回26个公交节点，没有extend；navigation-data在主体查询与报价后才读取。已有便宜完整方案，因此未混合不构成单独的失败证据，技能读取晚仅是可检验问题。
- journey-guardian round2：初次规划对两条公交各补末端步行，供应商都只返回1秒路段，仍距目标约312米；重新核验查询新的公交资料后保留unknown。它确实尝试连接，问题不能概括成“没有调用工具”；也未取得不同入口或混合替代证据。
- host-model full-demo：40分钟机场任务已读接驳技能，公交五路约44–66分钟；两次extend均给全程出租车补末端步行，没有origin→中间站或公共交通与打车的真正组合。原结果已给M488→碧海湾→11号线文字和站点，细分耗时到选完全程车后才读取。最终生成稿称“唯一可行”但assessment仍有候车及滴滴连接未知，属于证据表述错误。打车到碧海湾是否更优尚未查询，本次不冒称存在确定优解。

这些是历史轮次的实际表现，不是同条件提示词实验。它们支持“已有能力未转成接驳探索”与“事实投影增加探索成本”并存，不能证明模型停止的内部原因。版本核对归同目录 version-safe.json：最近 trip-list 的关键查询、接驳函数、工具 schema 与导航技能均和当前源码一致；早期案例的版本差异已单独标注。

## 已接受的实施方案

搜索目标应是围绕用户期限、预算和偏好，发现供应商整程方案之外有价值的走法。接驳次数和工具调用次数不是优化目标。建议以“保留有价值的公共交通主干，验证替换低效片段”为导航技能的核心：长步行／慢公交接入时考虑更早接上主干，末段绕行时考虑提前离开主干，中段长绕行或换乘负担明显时考虑跨站连接；也可搜索原方案以外的真实站点。这些是形成假设的例子，不是固定流程或每轮必查清单。

最小变更同时覆盖技能和工具事实：

1. 复用现有技能目录与read_skill机制，system仅保留角色、目标及按需读取技能的入口。新增职责明确的mixed-routing技能承载瓶颈判断、可验证假设和何时继续，description明确其适用任务；navigation-data保留Route、时间、费用、来源等事实语义，不重复探索策略。详细案例放引用材料按需读取，不要求固定流程或独立计划工具。守护与UI的已有业务细则回到对应资料归属，不继续堆在system；具体搬迁范围在实施时依据现有消费者核定。
2. 查询短回执提供公交段线路、上下站ref及供应商已有的耗时／距离；完整有序途经站及其所属route/leg/segment通过get_route或图详情按需取得。缺失耗时仍为空，不发明站间耗时。站点可属于多条路线，不用单一归属覆盖其它发现。
3. search_places直接提供可供extend使用的node_ref。保留现有前向扩展和价格计算；暂不新增逆向搜索、create/composite框架、代码收益评分或必查站表。

模型每次探索围绕可能改变推荐的具体理由，工具给事实而不下发下一步指令。找到可用路线后仍可验证有依据的低价替代；已无具体改进机会时可交付已查范围，不能声称穷尽或全局最优。相同端点／模式在时间或证据变化后可能有重查必要，不机械禁止重复查询。

资料参考：[RAPTOR](https://www.microsoft.com/en-us/research/publication/round-based-public-transit-routing/)以到达时间、换乘等标准比较非劣路线；[ULTRA](https://i11www.iti.kit.edu/extra/publications/bbswz-ultra-19.pdf)明确区分起点、终点与中途接驳。可借鉴比较与搜索视角；本应用依赖供应商黑盒查询，没有论文算法所需的完整交通网络，本轮不引入全网求解器，也不继承其最优性保证。

## Harness诊断接续（2026-10-11，当前工作）

用户授权继续推进，要求参考Pi Agent和成熟Agent harness实践，并强调先排查技能读取是否真正可用、获取全面诊断。当前基线db572f4，工作区开始干净。上一阶段失败不归因为模型能力；不再仅微调路线提示词抽样。

已确认的关键事实：

- 应用minimax_request和宿主请求校验共同硬锁thinking:disabled；最后8次实际请求均如此。[MiniMax官方OpenAI协议](https://platform.minimax.io/docs/api-reference/text-openai-api)明确M3省略／adaptive启用思考、disabled跳过思考。这是配置问题，但需实证它对接驳行为的影响。
- guardian_verify逐环核28次实际read_skill：正文SHA对应物化文件，tool回执唯一call_id与assistant调用一致，下次请求的role:tool内容与回执逐字相同，Markdown完整、有真实换行，无额外转义层。最后115事件轮有目录却未调用技能，不是该轮文件读取失败。证据归build/research/transfer-exploration/skill-delivery-audit-safe.json，复核入口tools/audit_skill_delivery.py。
- app完整push assistant原对象，宿主serde_json原样包装响应，无已观察到的reasoning字段丢弃；disabled轮响应原本就没有reasoning。没有HTTP抓包，不冒称已核网络原始字节。
- seq112的宿主JSON回执已有finish_reason:tool_calls但无calls。app不检查finish_reason而记completed，是确定的终态缺陷；length截断和空正文／无成功稿也不能误记完成。

实现分工与决定：guardian_impl改应用为省略thinking、请求reasoning_split:true，继续无损回传assistant对象；用简短技能元提示说明匹配description时read_skill(name)，引用通过path按需读；分类异常终止且不自动重试。host_model改宿主支持省略／adaptive／disabled及split布尔透传，并维护overlay和构建锁。guardian_verify维护实际技能传递审计及最后受控观察；root维护知识归属。各owner不覆盖彼此文件，不改路线策略／供应商fixture或预算账本。

参考[Pi agent loop](https://github.com/earendil-works/pi/blob/ea448f454af474f3e2fe9733b331e17b0662f5d6/packages/agent/src/agent-loop.ts)和[技能提示](https://github.com/earendil-works/pi/blob/ea448f454af474f3e2fe9733b331e17b0662f5d6/packages/coding-agent/src/core/skills.ts)，官方仓库现重定向earendil-works/pi；源码对照归build/research/transfer-exploration/pi-harness-comparison.md。[Agent Skills官方接入指南](https://agentskills.io/client-implementation/adding-skills-support)支持模型匹配描述后调用专用读取工具，不要求业务固定流程。[MiniMax工具指南](https://platform.minimax.io/docs/guides/text-m3-function-call)要求完整回传思考上下文；不同官方页出现reasoning_content／reasoning_details差异，因此保留整对象，不押单一字段。reasoning_split防止思考混进用户结果，不能删除历史来处理显示。

先做无模型协议／技能回放：实际请求配置、两种reasoning字段完整往返、工具ID一致、坏tool_calls／length／空stop不执行工具不记完成、不自动续轮。然后仅在既有剩余9次／约295k tokens内做一次同fixture真实M3观察。若额度不足完整UI，只报告已观察到的路线行为，不放宽额度、不换账本，也不以必调用工具规则替代自主编排。

当前修复冻结：main a27ca4c486a9c260c9273148747f493f5386117207109ac484d2acc5c1fc6f3d，包77ada9b2666b3a9a4b6bab1273d1685a564c52856e50b79ccd64f9c1877ea76a，stamp f3bbff0faf8e69d9a4f66485cb2559de5bb6017dc7d7e71541088f96937834b9；实际在线host 38c1f446b5a5c5fc5a05d3ba33a6ca6bcd87b0115afc457904e3edf6cece6223，overlay tree6cce41cc408f4c8e6bd9bb466fe9cb2f9d119b07／patch97274e7aa258d9f28d1ce7ac17864738c7972aadd8774683f106db2ea86e8d40。

宿主早期构建hash c04864与最终hash不同，因为app-hub-app的build.rs把Navigation包编入可执行文件；最后应用改稿后重建。当前二进制、私有实验二进制、build/agent/build.json及在线freeze均为38c1，宿主源码tree一致，不把早期二进制当作本次线上对象。

Rust chat3项／complete19项通过；应用实际请求与loop的18项原生回放通过build/smoke/navigation-harness-j3cwtu_m/report.json，覆盖双工具ID／全文技能／reasoning_content与reasoning_details、坏tool_calls／length保留路线和成功块但磁盘failed、不重试，以及空stop／仅失败稿。报告main eec27a52与最终main只差截断错误文案，避免将“这次响应工具未执行”误读成整个查询无调用；没有因此重跑行为检查。check/build通过。HTTP仍120秒，model service实际继承桥默认60秒，没有旧上下文提及的270秒；无输出token参数，本次不做额外超时调参。最后同fixture真实M3已执行，出现独立reasoning_content并在首回复主动读mixed-routing等技能；后台轨迹也开始query_route(to_ref)查询中转站，尚无完整混合候选。实验存在两个准备缺陷：首次临时空索引缺saved_at导致0模型调用，修正后共享fixture-go又让vm-2与vm-3同时启动。两份完整轨迹分别128和63事件、6和3次成功响应，合计9次／95363 tokens，与账本吻合；不是宿主重复计费或模型重试。第4个可见请求收到100次/日拒绝，不是60秒超时。两VM并发污染了单轮对照，不声称A/B或完整接驳验收通过。

验证owner已将实验入口修为按session和instance定向VM触发并消费一次性token；实际双VM、零模型请求的6项隔离检查通过，账本逐字不变。合法索引构造也纳入入口。10份mount及两份原业务索引已逐字恢复，自有实例已停止。证据归fixture-protocol-gate/report-safe.json及restore-safe.json。原始两VM日志私密保留，推理内容只在安全报告中记字段、长度和hash。当前账本100次／1800256 tokens；用户随后授权“100次/实验；1000次/天”，再批准2000万tokens；最新指示覆盖这些额度：“不需要设置任何上限，我看了minimax余额有1000元”。因此当前决定为撤去本机Navigation调用／token／每分钟及实验次数的人为预算上限，保留真实用量统计及服务端实际限制。host_model负责宿主支持方式、开发配置与私有账本；guardian_verify撤去实验次数cap并等待配置／构建就绪。不能用重置账本或极大数字伪装无限；不扩展为移除网络超时等无关边界。

日调用配置已更新并通过tools/test_model_config.py回归：configure只把Navigation calls_per_day设为1000，已有token／分钟上限及真实使用量保留，新配置默认仍为20次／分钟、100万tokens／日。私有实验账本仅该字段100→1000，原100次／1800256 tokens、2M tokens／日未变；安全记录为fixture-protocol-final/daily-cap-update-safe.json。该中间配置随后被用户的无上限要求覆盖，后续需同步配置、文档和实验驱动。

单VM接续已执行（fixture-single-vm）：只有目标vm-3派发模型，应用11次请求、10次成功响应，账本增加10次／170368 tokens至110次／1970624 tokens。第11次被原200万tokens／日额度拒绝，不是模型自然结束或实验100次上限。已查询公交、整程车、滴滴报价及路线图，读取路线事实／UI等技能，但未读mixed-routing、未查询to_ref或extend，尚未render，完整199事件保留。该轮仍不构成自主接驳或完整交付通过。最新用户授权已取消人为额度，按上述当前决定完成支持后以新目录做一次完整单VM观察，不改prompt／schema／skills，不反复抽样。

无上限配置已落地：宿主ledger显式支持per-app unlimited:true，准入跳过三项预算但照常计数／charge／落盘；budget回执限额及剩余额度为null，真实usage仍为数字。guardian_design核现有消费者未依赖这些null字段做算术，设置仅由开发宿主写入，不能由模型选择。tools/agent.py仅对Navigation启用，私有账本保留110次／1970624 tokens，未修改其它应用。Rust lib28通过（1 ignored）、chat3／complete19及Python配置回归通过，patch独立回放与宿主构建通过。新tree eb42b1207d20bd95c1900a6000bc3cc083efa231，patch117eba3a95e6b100cf0228238c5ff2f0a17e01c37988fe668d744538bd216cd7，binary12838260cfaa2a7f3378168dd1b1d136c7e5fc8b57c34d927be905a949333ec7。账本证据fixture-single-vm/unlimited-update-safe.json。实验驱动也撤去次数cap，保留单VM触发，下一轮目录fixture-natural-final。

不限额轮fixture-natural-final进入重复前置失败后由协调者停止，未以次数cap终止。set_constraints的demo机票分支要求日历及关联笔记逐字引用，但schema未声明且错误不区分原因；普通明确目的地本可直接search/adopt，不依赖该分支。成功设置票据约束后，fixture将真实POI B02F38ZM54的“深圳宝安国际机场T3航站楼(国内出发)”改成缺“国际”的短名，导致完整机场名包含核验必拒。真实online seq28还有type150105/parentB0FFFZRC7K，fixture对应字段也不忠实。本轮不作为混合路线能力结论。guardian_impl窄修工具适用范围、引用schema和可修正错误，不放宽身份；guardian_verify修fixture为已观测真实POI身份，交通事实保持，完成恢复后等新冻结再进行一次观察。

该前置失败轮最终693条连续事件、59次请求与回复，实际增加59次／1354460 tokens，含30次机场身份拒绝和5次来源引用拒绝；已点停止并保留迟到current=false响应，不冒称远端请求被取消。所有私有mount／索引恢复，证据fixture-natural-final/result-safe.json及restore-safe.json。

契约窄修已完成：schema公开set_constraints的demo票据用途、所选event/note双引用及单行原文要求；错误区分记录未知／引用不匹配／缺来源；机场拒绝仅返回失败及来源与POI字段，不再在已提交错误后返回true。system、技能、匹配谓词及约束模型未变。12项原生source-contract检查通过（build/smoke/navigation-harness-rppjjphy/report.json），check/build/py_compile/diffcheck通过。新main6a16d08d54f94cc78166a03846b95de3dd733b593b6bcae35917f785a90a96db，bundle39dd0e7e91c7a5ab9d47b131b996a279b1df586c0d1560818d10160bc5f0a4f0，stamp626558db932948a9bcad38352618a874658a7a161b6938fa3a3a33df538bc299，新binary4acea10343026ec39f8d8bfdef8a66eb2544906660714a84d9dfad87f238f3e9，host overlay未变。identity-v2 fixture仅根据旧真实online seq28修POI名称、类型、parent、地址，交通几何／时长／费用不变；下一次证据归fixture-identity-v2。

identity-v2在线路线行为已成立：第一次set_constraints／adopt即成功，read mixed后seq142 query_route(taxi,to_ref=poi:BHY)取得300秒／700分前缀，seq156 extend_route(route_2_6,transit,destination)形成完整route_2_7，两腿1000分／1620秒名义行程，含已耗时及分钟对齐为1706.09秒。首尾连接核实，唯一未认证原因仍为出租车候车未知。不是整程打车后补步行。第13次模型请求于60.33秒被桥超时终止（seq191–193），前12次成功、尚未生成块，不能称完整交付。host_model接续核对并窄修model.chat服务等待短于HTTP120秒的问题；verify保存全部请求与恢复状态，优先研究同上下文单请求恢复验证，避免重跑前12轮。

桥超时窄修已冻结：仅model.chat的HostService.timeout覆盖为HTTP TIMEOUT+10秒（130秒），其它方法保持60秒；无自动重试，网络超时不变。定向测试、patch回放、build及diffcheck通过。最终tree67df053ebba09f016b03c8a190aeec4a2861b054，patchb3c80f517b61983dabf07eff1f38d5ed67d4ffa85941f37f5d529601707223d1，binary41b409cf49ee38faf7fbb89568288c79bf705d3188a195a1dc82d42bd87765f5，应用聚合仍39dd0e7。原轮12可见成功响应tokens294175，账本增359109，差64934可能来自迟到第13响应计费；没有迟到原始body，不推断其内容。新宿主已重放原第13完整body一次：41条messages／23tools与原请求JSON结构逐字段相同，单VM仅1请求，3.222秒成功返回tool_calls（attach_quote），计费1次／52335 tokens，reasoning字段保留。只保存未执行工具，无路线内存恢复，不冒称UI端到端验证；本次未跨60秒，130秒长等待边界仍依据定向测试，不能由该在线成功单独证明。证据request-13-replay/result-safe.json与restore-safe.json：11份mount各自原件、两索引一致恢复，临时文件移出、自有实例停止。

## 上一阶段实现与验证

最终源码main为51f45061f0fd68e98af13ae2ba672d50ef355bf40928e5fc515507f3a69f4070，包聚合ce36450801ad57e0bf8516e20a89d19dd5c6ba45acd3d6fb2e5829a6ec356be1，Hub摘要124962e33bcbee71e8dca13672b4febef10cd24cfafccfa14d3bd80bffcc8b59。未更新宿主或版本号。guardian_impl拥有生产main／技能／原生回归，guardian_verify拥有在线实验与证据，root整合文档和本任务包。

复用原有技能加载器，目录7项增至9项；system正文437缩至187字符（不含目录，不作为token／速度收益），公开工具仍23个。mixed-routing、navigation-data、journey-guardian和native-ui分别承载搜索、事实、守护及呈现规则。工具保留单位、身份和副作用；native-ui增加一条忠实呈现已知耗时、估价及未知的说明，不添加模板或验证器。源码审计入口为build/research/transfer-exploration/prompt-audit-safe.json。

在实际模型误用前缀后，query_route增加可选to_ref：默认查询整程，指定真实中间节点时复用extend(origin)取得新前缀，再用返回Route继续extend。extend参数明确传入完整Route就会保留全部耗时／费用，不会裁切。保留origin兼容路径，技能引用给泛化调用示例，不指定测试站名或必调用顺序。

主Agent已采纳以下验证报告，均在忽略目录：

- build/smoke/navigation-harness-canyido6/report.json：最终main的22项原生路线检查通过，包括默认整程、query中转前缀与后续累计、站点／耗时投影、多线路归属、未知保留、完整计价和报价派生。合成供应商、desktop模式、无模型调用。
- build/smoke/navigation-harness-26af12va/report.json：最终main的12项Android样式技能／schema检查通过，目录可发现、正文及引用按需读取、实际工具参数语义生效。无模型调用。
- build/smoke/navigation-harness-misp0b5q/report.json：早期同逻辑生产空库启动通过。此前txoc8s32复现隐藏动态父区的子控件尚未创建却被更新；窄修在父区隐藏时不寻址子控件。最终版本后续仅工具／技能变更，不扩大UI验收。
- make check、agent-build、Python语法与git diff --check通过。完整最终摘要归final-freeze-safe.json。

## 模型实验与判别

以下目录均位于build/research/transfer-exploration/，原始模型消息不进入Git。模型为真实M3，宿主macOS的Android样式，不冒称Android真机。实验复用已有账户及账本，不重置、不放宽额度。真实供应商与受控供应商分开报告。

| 轮次与证据 | 实际观察与判断 |
| --- | --- |
| online/result-safe.json；176连续事件、9次M3 | 真实高德／滴滴，模拟起点。早读技能且实际得到M488的1080秒接入、11号线720秒主干与碧海湾ref，仍只比较全程公交和约20元打车，没有查询中转替代；无依据生成“含候车30–40分钟”。不能据此断言真实未查组合一定更便宜。 |
| fixture-provider-failure/；11次M3 | 合成reverse-geocode缺country，被生产城市契约拒绝。保留失败，不计为搜索策略结果。 |
| fixture-current/result-safe.json；253连续事件、18次M3／324299 tokens、81.85秒 | 同原始40分钟／50元／尽量便宜请求，工具正常给整程公交44分钟5元、车22分钟20元；可查但未在请求中透露的前缀＋公交约27分钟10元。模型先从全程车终点错误续接，晚读技能也未纠正。 |
| fixture-revised/result-safe.json；214连续事件、13次M3／241643 tokens、43.19秒 | 仅修mixed中预算不等于优化完成、从origin重建首段。首轮已读新版技能，也询到起点到碧海湾7元，但extend保留整程公交又加公交成88分钟10元，未建立前缀；未读reference。 |
| fixture-schema/result-safe.json；实际20次M3／523133 tokens、95.17秒 | 补extend参数与引用示例，仍把整程公交末端再加车（66分钟25元）。本轮日志缺215–328，实际331事件只导出217条，不冒称完整轨迹；账本计数不采用可见请求数。 |

三轮受控失败支持接口可用性问题与策略问题并存，不证明模型内部原因，也不宣称单次提示变化的稳定因果效果。因此最后变更是query_route的直观中转目标接口，而非继续堆system或反复微调抽样。最后接口判别已结束，仍未主动查询中转前缀并续接。本轮停止提示／接口试错，不继续耗尽额度抽样；工具能力有回归证据，自主行为未通过。

合成接驳继续保留候车未知；不能为通过检查补零或要求passed=true。判断依据是完整查询证据、费用比较与真实未知，不是extend次数。便宜直达、中段或末端替换、接驳无优势的新版模型稳定性仍未系统覆盖；历史复盘／工具回归不冒称这些已获在线验证。

## 证据与私有实验状态

schema轮日志缺口根因为私有jail达到宿主MAX_ENTRIES=256，历史dev-trace占约23.89MB，新segment文件无法创建；不是字符串字节算法或64MiB容量限制。既有trace_status如实标incomplete，未改生产日志实现。trace-capacity-diagnosis-safe.json保留诊断；145个历史文件逐个SHA核验后移到private-trace-archive-20261011，含目录移出189entries，jail从256降至67，账本SHA不变。trace-archive-checksums-private.json保留校验。缺失事件无法恢复，不用后续成功掩盖。

为修复实验mount选择，验证owner曾将私有应用历史mount统一为冻结生产pack，未逐份备份各旧revision；可恢复当前官方pack，不能恢复历史挂载原稿。原两个业务索引有备份，业务记录与trace未改，正式用户实例未碰；此限制只涉及私有测试目录，需保留于实验报告。每轮关闭自己的实例并恢复索引及生产包。

进入最后接口轮前账本83次／1633114 tokens，剩17次／366886 tokens，额度保持100次／2M tokens。最终轮新增8次／71779 tokens，账本到91次／1704893 tokens；未放宽额度。最终恢复已核对fixture-final-api/restore-safe.json：各私有mount均为最终生产main，两个原业务索引逐字一致，自有实例关闭，恢复过程未改账本。

最后接口轮115事件连续完整，未读取skill/reference，query_route均未传to_ref；4种整程公交加全程taxi后直接propose_goal，没有完整混合替代。seq112原始M3回执finish_reason为tool_calls却没有message.tool_calls，只有“现在渲染完整UI”文字；应用按无工具调用结束，seq115 generated=false/rendered=false。因此不能称自然model stop或端到端／UI验收通过。该异常发生在路线选择之后，不冒充未探索的内部原因；原始回执保留。技能发现／使用、路线工具自主选择及无工具回执的交付问题仍需后续研究，不能靠更多固定流程或必调用规则掩盖。

本轮实现和定向回归已完成，自主接驳与完整交付仍未验收通过。最终证据入口为build/research/transfer-exploration/verification-final-safe.json；最后轮结果为fixture-final-api/result-safe.json，trace SHA e915e1d3aaf03a2a1356ecaed3aa8d4c3a0cffd56de23c200f621bddacf33fc9。README已明确工具能力与模型实际表现的区别。本任务共79次M3／1460227 tokens（含无效country轮）；不再本轮追加模型调用。接续应先研究技能发现／使用和工具自主选择的失败，再决定不同机制的实验；不重复同场景微调抽样，也不以必调用顺序替代Agent编排。
