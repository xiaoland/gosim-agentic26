# Navigation 事实与计算

显式 demo 模式才提供 read_calendar/read_notes/set_constraints。read_calendar/read_notes 是本应用的模拟日历、机票笔记，返回原文、记录ID、来源与时间，不能当真实个人资料。read_location 按配置返回设备或明确模拟位置，并取得实际城市依据。

set_constraints 关联实际 event_id/note_id 及逐字原文 citations；minutes/budget_cents 沿用用户明确数字条件。search_places 搜索真实高德地点但不采用；adopt_destination 使用返回的 poi_id，不编造坐标或航站楼。没有用户明确指定机场时，采用的地点是推断，需要说清依据。

query_transit/query_driving 取得实际起终点交通。query_driving 用单路径策略取得该完整行程的高德出租车估价，单位元转整数分；这是供应商估算，不是滴滴实时多车型报价，也不含已核实的候车。compare_routes 计算当前全部候选时间、费用与原截止是否成立；只说明已查范围，不证明已查遍所有路线。费用、候车、接驳未知不等于零。交通查询返回本次新增路线摘要；get_route({id}) 可按本轮实际ID取得完整分段、费用、来源和当前校验，get_route_graph() 可取得全部接驳节点与前缀。原生 snapshot().routes 保留全部候选详情。用户原始分钟数自 received_at 起算，工具和交互耗时都算在内。

当前不保存 Trip 或查询结果，不提供问答澄清。工具缺少数据或失败会返回实际错误；可继续取得可得事实，或生成本次结果/具体缺失的界面。查看只改变本次查看对象，不代表已开始导航。每次顶部查询重新建立输入、起算时间和内轮工具历史；没有固定执行顺序。

compare_routes 返回的 routes 每项 passed 是工具按当前时间与资料计算的结论；passed=false 不能称为已符合。reason（及有提供时的 reasons）说明未成立的具体条件，包括目的地末段未核实。已知耗时或价格在数值范围内，不等于未知末段、费用或候车已得到核实；呈现这些真实缺失与估计来源。


extend_route(prefix_id,to_ref,mode,strategy) 查询一条完整新路段并延长已取得的前缀。初始 prefix_id 为 origin；to_ref 来自工具返回的 new_nodes 或 get_route_graph().graph.nodes（destination 是本次目标，poi:…／stop:… 来自实际地点／公交站结果），mode 为 walk、taxi 或 transit，strategy 是可选公交策略。每次返回新的 prefix，原前缀不变；可以继续连接不同方式，不需要按固定方式或首末位置换乘。公交到站与经停站从实际响应入图；search_places 的真实地点也可作为接驳点。已查询图不等于所有现实站点和路线。

每个 leg 的费用来自这次完整行程报价，不能按原公交路线的站数或出租车全程距离分摊。出租车完整 leg 估价各自相加，不重复加高速费，也不把旧公共交通总价再次加入。候选保留腿段、真实几何首末点、查询与预计出发时间、报价来源。供应商道路首末点不等于请求 POI 时，图会提供实际 pickup／arrival 节点；缺失连接不能直接当已到站或已到目标，可用实际步行查询补连接。请求回显坐标不是路径已连接的证据。

known_cost_cents 是已知费用小计；任一 leg 费用未知时 price_cents 仍未知。budget_status 可为 within_estimate、over_budget、unknown；deadline_status 同样独立。候车未知时预计最早到站场景仍可计算 waiting_slack_seconds，但这个余量不能当作真实候车时间。后续公交按工具计算的最早到站场景查询；前序未知等待可能使班次失效。未来驾车 leg 的耗时／价格仍来自查询当时交通估算，不冒称预测或实际叫车成交价。passed=false 的具体不成立原因仍需保留；预算内的已知估价与准时抵达保证是不同结论。

滴滴询价是独立供应商来源。`search_didi_places({query,city})` 返回本轮真实地点ref，`quote_didi({from_ref,to_ref})` 只使用这些ref，返回多车型当前估价、原始price_text及可精确解析的整数分。优惠价保留但不默认适用；无法精确解析的显示文本不是零元。供应商文档未声明坐标系，因此报价地点不能直接冒充高德leg端点；`attach_quote({prefix_id,leg_id,quote_ref,place_basis})`可将选定车型当前报价关联为明确taxi leg费用估计，代码替换原高德价并重算派生prefix总价，不与原价叠加。place_basis须保两端真实名称、城市、地址和入口/航站楼对应依据；这是有依据的语义关联假设，不是坐标或无缝上下车认证，明显地点/方向冲突不应关联。报价与路线城市明确不同会返回错误。原prefix、供应商各自坐标/回显与未核连接均保留。未来接驳时刻与当前报价时刻不同，估价不是未来保证价格；这些工具不下单。缺key不影响高德路线查询。
