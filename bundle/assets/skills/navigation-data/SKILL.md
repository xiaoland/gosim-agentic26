---
name: navigation-data
description: "Navigation真实出行资料、统一Route身份、混合接驳与供应商报价语义，用于选择工具并解释可追溯路线。"
license: Apache-2.0
---

# Navigation 事实与计算

显式 demo 模式才提供 read_calendar/read_notes/set_constraints。read_calendar/read_notes 是本应用的模拟日历、机票笔记，返回原文、记录ID、来源与时间，不能当真实个人资料。read_location 按配置返回设备或明确模拟位置，并取得实际城市依据。

set_constraints 关联实际 event_id/note_id 及逐字原文 citations；minutes/budget_cents 沿用用户明确数字条件。search_places 搜索真实高德地点但不采用；adopt_destination 使用返回的 poi_id，不编造坐标或航站楼。没有用户明确指定机场时，采用的地点是推断，需要说清依据。

query_route({mode:"transit"|"taxi",strategy?}) 查询本次实际起终点，返回 routes。transit 默认策略0，亦可1经济、2少换乘、3少步行、4舒适、5无地铁、7地铁优先、8快；taxi 用单路径高德驾车方案取得该完整查询的出租车估价，不是滴滴实时报价，候车未知。每次查询创建本轮唯一 Route id 和 geometry_ref，所有 Route 都有稳定 leg id；一个 leg 是一次完整供应商计价方案，steps/segments 只描述内部步骤。公交整体报价不能按站数、距离或内部 taxi step 拆摊。

query_route、extend_route 返回 routes；get_route({id})、attach_quote 返回 route；compare_routes 与 snapshot().routes 使用同一 Route 事实字段。get_route 只读本轮已有 Route 并按当前时间核查，不重查供应商；完整、未完成 Route 都可读取、查看和绘图。get_route_graph 返回 nodes、routes 与初始 route_id:"origin"。geometry_ref 直接解析运行时真实几何，模型不传 polyline，也不手传 duration 或金额重建路线。

Route 的 duration_seconds、distance_m 和费用来自实际资料；duration_label、price_label 是应用格式化字段。cost.amount_cents 是该 Route 所包含全部 legs 的估价合计，任一 leg 缺价则 nil；known_subtotal_cents 仅累计已知金额。cost.full_journey_amount_cents 只在请求起终点覆盖及连接核实、金额齐全时提供，否则 nil。cost.coverage 为 requested_journey 或 queried_legs_only；后者的 price_label 明确显示“已查段”。费用均为整数分，currency 与 basis 保留来源语义，未知不是零。

completion_status 为 reached_requested_destination、incomplete 或 unknown，依据实际路线终点，不由查询工具名称决定。到达请求终点与满足预算/期限是独立事实；起点、候车、跨供应商连接和时效仍可未知。assessment.passed/reasons/evaluated_at 是按当前时刻重算的约束判断；budget_status、deadline_status 和 connection_status 各自描述独立条件，passed=false 不能改写成所有条件都超限，unknown 不能改写成符合。已查小计低于预算不证明全程预算内，已知行驶用时短不证明候车和连接后准时。新规划的用户期限从 received_at 起算，查询、生成和交互时间均计入；守护核验使用已确认的绝对期限，重新打开不会重新起算。duration_seconds 是路线估计用时；是否超过当前截止看 assessment，不把原分钟数、当前剩余期限和来源 expires_at 混成一个条件。来源过期与超过到达截止是两种理由。

展示或解释所选 Route 时，按同一 id 查 snapshot().routes，并使用该对象的 price_label/duration_label/cost/assessment；标题和按钮同样属于事实陈述，不在详情承认未知却在卡片称已符合；不要把报价文字静态写到另一个 Route 卡片，也不要继续使用过期比较结论。

已查范围不证明现实全局最优。围绕用户的时间、预算和低价目标，根据实际缺口探索可得的步行/交通接驳及可用供应商报价，工具选择与顺序由你决定。未核实的末端或候车仍属未知；不能仅凭用时数值称准时，或在所有 assessment.passed=false 时称某条路线可行、稳妥或最便宜的完整方案。展示当前所选 Route 的 assessment 理由，并明确仍未探索的比较范围。

当前出行列表保存独立规划记录及成功Agent界面和当时事实，重开只展示历史详情，不恢复模型会话或自动查询，不提供问答澄清。新规划建立独立出行；目标确认只作用于当前所选出行，多个出行的目标互不覆盖。历史结果不认证当前成立，主动核验才取得本轮新证据。工具缺少数据或失败会返回实际错误；可继续取得可得事实，或生成本次结果/具体缺失的界面。查看只改变本次查看对象，不代表已开始导航。每次顶部查询重新建立输入、起算时间和内轮工具历史；没有固定执行顺序。

compare_routes 返回的 routes 每项 passed 是工具按当前时间与资料计算的结论；passed=false 不能称为已符合。reason（及有提供时的 reasons）说明未成立的具体条件，包括目的地末段未核实。已知耗时或价格在数值范围内，不等于未知末段、费用或候车已得到核实；呈现这些真实缺失与估计来源。


extend_route({route_id,to_ref,mode,strategy?}) 从现有 Route 的实际末端查询一条完整新路段，返回新 Route，原 Route 不变。初始 route_id 为 origin；to_ref 可直接使用 query_route 返回的 new_nodes.ref，或 get_route_graph().nodes 中的真实 ref，mode 为 walk、taxi 或 transit。origin 种子可以查到真实中转站；取得的新 Route 可以更换交通方式继续接驳。直达公共交通超期只描述该已查方案，不能据此断言到中转站后打车、或先打车到站点再乘公共交通都不成立。围绕实际目标选择值得比较的中转节点和方式组合；每段另查完整供应商方案，不从原完整公交方案截取耗时或拆分票价。工具选择与顺序仍由你决定。供应商道路末端不等于目标 POI 时，新 Route 保留真实 arrival 节点和 incomplete；可从该新 id 继续查真实步行连接，不把请求坐标当已连接证据。

确定性工具检查相邻真实端点并累计完整 legs 的费用和时间。候车未知时，后续公交按前序最早到达场景查询，未知等待可能使班次失效；waiting_slack_seconds 不是真实候车时间。未来驾车路段仍用查询当时交通估算，不能称预测或成交价格。金额未知仍保留已知小计，未完成 Route 的小计不是到目的地总价。


滴滴询价是独立供应商来源。初始任务事实 providers.didi.configured 仅说明本机是否配置Key，不表示服务已可用；没有调用或实际调用失败都不能据此声称未配置。`search_didi_places({query,city})` 返回本轮真实地点ref，`quote_didi({from_ref,to_ref})` 只使用这些ref，返回多车型当前估价、原始price_text及可精确解析的整数分。优惠价保留但不默认适用；无法精确解析的显示文本不是零元。供应商文档未声明坐标系，因此报价地点不能直接冒充高德leg端点；`attach_quote({route_id,leg_id,quote_ref,place_basis})` 可直接给普通出租车查询或组合 Route 的明确 taxi leg 关联指定车型当前估价。代码替换该 leg 原价并重算费用，返回新 route 和新 id，以及 derived_from_route_id；原 Route 不变，不与原价叠加。展示、查看和地图需选择返回的新 Route id，不能把新价归给原 id。报价派生保留原耗时、实际几何与完成状态，不升级候车或滴滴上下车连接保证。place_basis须保两端真实名称、城市、地址和入口/航站楼对应依据；这是有依据的语义关联假设，不是坐标或无缝上下车认证，明显地点/方向冲突不应关联。报价与路线城市明确不同会返回错误。原 Route 与未核连接均保留。未来接驳时刻与当前报价时刻不同，估价不是未来保证价格；这些工具不下单。缺key不影响高德路线查询。


地图由父应用持有的真实路线几何绘制，map 事件 target 可以直接用 geometry_ref（polyline_…）或路线 id，不需要模型传坐标或 polyline。geometry_ref 映射同一候选的惰性几何缓存，不在查询时扫描全部折线。`get_route` 与原生 `snapshot().routes` 的 `map_paths` 列出全部可用折线的 index、start、end、point_count；费用及可行性仍针对整条路线，分图不会重新计算或切摊票价。高德静态图每次最多4条独立折线；可用 map 事件的 path_indices 在多个独立命名地图中选择不同完整折线，资料见 native-ui。应用不自动截断、分组或跨缺口补线；模型可以决定分步查看或并列展示，保留完整路线及实际缺失说明。

出行目标守护使用propose_goal({route_id,preferences,risk_acceptance,basis})提出本轮真实路线和目标。偏好与风险接受文字必须供用户明确确认，不能将推断描述为既定用户指令。父应用确认后才持久保存选定路线、绝对到达期限、总预算/币种和确认版本，普通未确认规划恢复为带时间的历史详情，未确认提案不恢复。重新打开只展示历史；点击重新核验才建立新工具循环，模型历史不恢复。守护的report_goal_check({route_id?})确定性返回valid/invalid/unknown。已知到达超期或已花金额超预算直接失效；缺交通/费用/候车/连接证据为未知，不能当成立。新线路与原选定线路不同，只能作为替代提案；失效时自主探索接驳与报价，展示差额、来源和风险，用户确认才替换，不放宽目标。

进度与累计已花费用由用户在父应用确认，从总预算扣除。不能用定位推断上车、付费、购票或已完成路段。当前首版不会逐段推断在途进度；有已确认进度或已花费用时，原计划可能因缺剩余路段证据保持未知，可以基于当前位置探索替代。不要重复把已付公共交通整程票价算作剩余费用；票价适用范围或进度不明确时说明缺口，建议用户使用进度入口简短确认。所有交通检查仅在用户主动核验时执行，打开只展示历史，不后台监听或下单。

守护核验的交付是本轮实际证据与report_goal_check计算并记录的结论，不是读旧快照后自算到达。初始current_check没有本轮交通证据时为unknown（绝对期限已过或已超支仍invalid）；read_location仅取得位置，不证明原路线仍成立或已上车。get_route({id:"saved_goal_route"})返回evidence_scope:saved_snapshot、历史来源时间、估价与路线目录，只供识别原计划/比较/看旧地图。original_route_id不是本轮引用。自行选择query_route/extend_route/报价等工具取得可用交通证据，交付当前核验及依据；缺证据可以如实结束为未知，不能口头宣称仍成立。有进度时新剩余段与旧整程估价/耗时不可直接比较，差额未知须说明适用范围。
