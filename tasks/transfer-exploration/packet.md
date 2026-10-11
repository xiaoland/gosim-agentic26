# 接驳探索与技能分工

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

## 当前实现与验证

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
