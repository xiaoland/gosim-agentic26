# 统一 Route 身份与报价派生

状态：2026-10-06，统一Route实现、二十一项同源检查与最新封装完成；两中间稿真实报价派生已验证，最终稿在线验收在定位回调被宿主硬预算阻断，完整UI／地图未通过。

## 目标与授权

用户建议标准化路线，避免Agent手传耗时、金额和折线；接受先统一已有工具产生的Route，让已查打车路线直接附价、返回可读取／查看／画图的新Route，于本轮明确“同意，开始调整”。授权必要代码、定向测试、技能及文档更新与在线验收；不扩大为规划内核重写、固定workflow或新增持久化。不先增加无独立职责的create_route／composite_route包装。

## 事实与实施范围

前一轮报价成功却显示错误：直查route_1_6仍3200分，Agent重查得到未完成prefix，再附价派生quoted-prefix-2为2300分，界面选择旧候选却写新小计。回执已明确未完成；candidate／prefix两身份与不同事实结构增加了关联负担。调查与完整轨迹入口归[工具契约任务](../tool-contracts/packet.md)，原始记录仅在ignored私有build目录。

复用现有计算与几何cache，统一query／extend／attach返回Route和可引用legs；get_route、比较、查看、地图使用同一身份，未完成路线也可读取真实范围。attach_quote以route_id／leg_id附加本轮报价，派生新Route、重算费用，原对象不变，不为附价重查路。到达覆盖范围、连接核实、费用完整与满足约束独立；未完成金额是小计，全程价格未知。公交完整供应商报价不拆摊，不补断裂几何。模型仍自行选择检索和呈现。

路线owner拥有main.splash路线逻辑、navigation-data及必要现有smoke；UI owner仅维护native-ui作用域与事实绑定示例，root维护文档／版本／packet。共享技能迁移保留，不撤其它修改，不静默混入提交。当前不提交或推送。

## 完成依据与下一步

必要检查验证直查附价派生新ID、旧价不变、未完成小计不冒全价，以及读取／查看／地图身份一致；保留时间、接驳和未知语义。冻结后唯一native owner重新封装，正常入口显式demo背景与在线M3／交通跑一轮，保留完整请求／响应／工具／DSL／点击诊断，不人工补稿冒称模型成功，不盲抽。

地图机械错已由私有回放证明：生成稿View内bound_route :=应改为外层let，修后可发初始map事件；不是供应商加载失败。产品资料例原本正确，本轮只明确let词法状态与:=命名成员，暂不引入查询结束后的第二修稿循环。实际地图与费用解释质量仍需如实验收。

## 实现与定向证据

main冻结ad6654e92352b9d4acffaedbf66356832f4e0275425e0d4d2f2448d3a91c5a24，版本0.13.0。extend_route公开route_id替代prefix_id；query／extend／attach／compare使用短统一Route投影，get／snapshot为同核心字段详情超集。几何不进入模型，query不带完整segments与map目录；旧price_cents等UI兼容字段仅详情保留，未完整或未认证覆盖的price_label明确标已查段。报价派生不重新查询，不重放新增路段连接门槛。

封装中发现assessment.deadline_status错误复用综合passed，路线owner暂停交付并窄修独立截止判断。ad6654稿改列中间稿；native正在进行的构建仅归该稿，不启动挂载实例冒最终版本。修后检查预算与期限能独立变化，再以实际新SHA重新封装。

截止判据修后最终main3a30f888333d1581786c23719787bd9a13a2e87e5d11b0ad3231499a55f478f9，同组十七项通过，报告build/smoke/navigation-harness-ztl55yyb/report.json。中间并发旧夹具有contract-ready等待超时（7e43zbiy），无已见脚本错误，不算通过，两自有实例由finally清理。旧ad6654构建期间改稿被source guard正常拒绝，未挂载／doctor；新freeze再做唯一最终封装。

最终0.13.0 check／build／doctor通过，31包文件嵌入与挂载、23技能材料化逐字节一致。sourceb024a9c4…／runtimec90bd1cd…／binary9b6ecce1…，安全报告build/research/route-identity/final-package/result-safe.json。原生owner自有隐藏实例关闭，未重复业务／服务测试，实际stage与binary交路线owner运行唯一在线demo轮。

唯一在线demo轮原句已核，实际报价派生关系正确：原route_1_6仍3200分，attach派生route_1_7为2200分且未完成，耗时几何保留；Agent从原路线真实末端补查walk形成route_1_8，再附价派生route_1_9为2200分，已覆盖端点但滴滴连接／候车未知，全程金额仍nil，compare回执一致。尚不能称完整交付：step9比较回执后暂未进入下一请求／渲染，稳定owner正在诊断tool结果提交、结算与原生执行副作用，不注入工具或手动生成界面推进。

停滞已由原生日志确认64ms硬时间预算，耗尽IP在agent_tools／render_block_tool schema重建；compare结果seq189已先提交消息、推进索引并清active，但随后入口Bail，没有后续model_request／dispatch，非M3等待。每轮schema构建重复读取location_mode配置，存储阻塞计入时间预算；耗尽IP不能单独证明schema或fs占了全部耗时。采用本次run固定schema缓存、start_task清理并一次取mode，避免不必要的重复构造与读取；不加看门狗／限额或提升预算，模型编排自由不变。修后必要重用／新run清理检查、新SHA封装和一次正常demo在线复验，以实际结果判断作用；旧3a30稿的报价成功证据保留，但不当完整交付。

schema缓存修后main3b76db85a5695119dc0e96a86267621aceca49be717a9a6b6a952e7187b54662，十九项同源检查通过（438rohn0）。初轮新run检查误用数组!=（结构相等）断言独立对象，改为修改旧schema哨兵并检新run不继承，产品源码未据夹具失败改动。旧在线轮完整证据e2e/demo/e2e-result-safe.json，自有实例已关闭；新包仅做必要封装再跑唯一demo-schema-cached正常入口，不续注旧轮。

缓存稿封装check／build／doctor通过，31包／23技能一致，safe cached-package/result-safe.json。该稿在线越过原schema停滞，真实报价派生route_1_9=2100分，原route_1_8／route_1_6仍3300分；端点／滴滴连接／候车未知保持，全程价nil，Agent实际补查公交与打车末段。首render_summary前父VM再硬止，DSL仅787bytes、未install／无子实例，也没有render_source／result，不能归模型DSL错误。

新耗尽IP为route_uint数字正则，调用路径mount_ui_blocks→block_source→facts_json→interface_facts；统一facts重复解析每条Route步骤，snapshot.graph又构造同一批Route摘要（该轮九Route／六十六steps），是本次新增重复工作。最小修复缓存不可变步骤投影、派生共享，snapshot.routes保完整对象、graph仅nodes／route_ids，get_route_graph按需仍返回路线；assessment不缓存。必要规模检查后新freeze封装与一轮在线，不提高预算、不盲cache所有状态。旧失败完整记录独立保留。

facts修复freeze8a299fa3083046f3fbd337c98122af4a392734cf3e576f8d7a5a8505d15fe500，二十一项同源检查通过（f1qaiu2m），包含实际规模、派生共享和assessment当前重算。graph有nodes／route_ids／initial_route_id，按需工具仍nodes／routes。native已唤醒做独立facts-package；新稿唯一demo-facts-cached，不冒称旧失败轮通过。

最新facts-package check／build／doctor及31包文件／23技能字节一致通过，source01184a5f…／runtime5d6be8ce…／binarycc3a5351…，报告build/research/route-identity/facts-package/result-safe.json。驱动切Android／挂载回执404，实际切换已发生，在同一自有实例恢复并核原句；没有重启／重抽，首次M3请求后demo位置城市核对回调即64ms硬止（position_current，main810:41）。该轮无Route创建／渲染，不是GPS授权或M3等待，无法证明最新稿UI／地图。该定位逻辑未被本次Route修改，不扩大为宿主预算或定位内核重写；保留冷Android样式和storage等待日志但不把它们单独当全部耗时根因。稳定owner导出整轮并关闭自有实例，停止抽样。

完成范围是统一业务契约、直接附价、同身份读取／查看／地图接口和性能回归窄修；剩余独立问题是宿主硬时间预算导致完整在线验收阻断，以及最终生成稿的UI／地图质量尚未验证。无提高预算、看门狗、强制工具流程或人工补稿。恢复从最终8a299fa3稿与对应facts-package开始，旧稿在线报价证据只按各自hash归属；需要后续定位／运行时诊断，不能把现版本描述为完整端到端通过。

最终失败安全入口build/research/route-identity/e2e/demo-facts-cached/e2e-result-safe.json，完整private trace与实际停滞截图保留；三个在线自有实例均关闭，最终main hash未改变。未提交或推送，当前工作区仍保留另一任务技能迁移。

十六项同源原生Android样式定向通过，报告ignored build/smoke/navigation-harness-ihgc0eo7/report.json，覆盖旧价不变、新价新ID、直查与扩展同端点状态一致、公交leg拒绝附价、同ID读取／查看／地图cache及新查询清空。地图是合成shim，无M3／供应商，不能当真实底图或模型验收。原有十项混合检查通过（hx2pjv__，冻结前仅nil约束保护变化），不将不同hash报告冒成同源。导航技能380c852d…、UI技能a42e14ad…，后者按同一ID动态绑定price／duration／reason／segments并明确变量作用域。README与architecture同步实际契约；native唯一封装后在线M3正常入口判别。
