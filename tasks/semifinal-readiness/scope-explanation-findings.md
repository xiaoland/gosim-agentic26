# 范围解释错误：形成位置与冻结边界

## 当前结论

2026-10-13 的 online10 与独立 UI 恢复实验均保留语义 FAIL。完整正确资料确实进入了实际模型请求，错误首先发生于第一批新候选的解释，早于 compare_routes 与界面生成。冻结前不修改 query 投影、不追加同义禁令，也不再付费尝试；新增分组尚无收益证据，不能为了更短回执删去接驳探索所需的分段、节点、来源或费用依据。该决定不表示错误已修复。

模型后来能依据真实渲染诊断自主修稿，并在动态列表与详情中正确使用格式化范围标签，但静态解释和最终答复仍把小计、已查终点场景推广为整程成立。这两种表现不能互相抵消。

## 首形成位置

| 位置 | 实际收到的事实 | 首次错误及后续影响 |
|---|---|---|
| request36，tool result30，assistant43 | route_1_2：全程金额 nil，小计500分，coverage=queried_legs_only；10200秒、duration_scope=queried_legs_only；目的地到达 nil，已查终点19:39；budget/deadline均unknown。 | 公开称“两条新公交整程证据”“都早于20:34到”；推理明确把¥5称整程总价。此时尚未调用compare。 |
| request49，result47，assistant56 | route_1_4仍为10200秒=170分钟，费用与目的地到达范围未知。 | 公开文本首次误写70分钟；同条推理多次仍写170。70不是回执数值或确定性换算结果。开始猜公交卡/套餐价。 |
| request62，assistant69，propose call74 | 原cost.basis明确供应商option报价，没有交通分段票价分摊或包含关系。12306 result45是W无座、¥54。 | 首次明确“一票制”，把不同供应商报价差异解释成公交卡产品，并把无座称预留座位。提案basis保留70与一票制。compare call72与propose74同一模型批次，result73尚未进入模型。 |
| request77，result73与75，assistant84 | 精简compare仍有price_label、arrival_label、assessmentunknown；提案也保留nil与unknown。 | 模型已注意passed=false，仍维持¥5最优，并把已查小计差-5200分推广成节省¥52。后来精简比较不能证明已消除首轮锚定。 |
| assistant117，render call118 | compare73重算route_1_4已查终点19:41；目的地到达仍nil，期限20:34。 | 首次明确“到限前53分钟到达”。53来自20:34−19:41，但这是已查终点差，不能认证目的地期限。 |
| 独立UI恢复的assistant1/2/3 | 原failed request121逐字保留旧推理；真实诊断反馈后再生成。 | 170修正，动态正文正确保留小计和目的地未知；一票制、53分钟余量和全程便宜仍在静态解释/终稿。终稿19:41也未跟随当前详情19:49。 |

首次错误前模型实际读到的 rail-routing result15 写“公交化城际…整段方案价”，mixed-routing result17 写“普通导航返回的整程方案”。这些是可能的整体暗示，不是已证明的唯一原因；模型自行补出了交通卡票制和报价包含关系。journey-guardian result13已有未知不得认证的边界。query result30同时包含顶层duration_seconds、单leg报价、请求目标ref以及旁列的范围/unknown字段；字段全在，不能将本次问题描述成服务漏传或技能未读。

## 原件索引

原始资料保存在忽略的 `build/research/journey-guardian/current-online-10/`，不进入应用包或Git。以下文件足够恢复具体判断，不需要重新查询交通：

- `model_request-36-private.json`：首次错误前的完整实际请求，body内11条messages、26个tools；`messages[8].content`是query result30，对应tool_call_id `call_e46D8noH0PYoXeBxqCESoXX3`。body为94352字节，SHA256 `d51418182180548aff9b900742eba39ec90c7d4fc3d7b235b7e9758c2d9ca8ee`；该content的SHA256为 `bbf86d2b5978a0e448861389c0a19cdad4232f61c59c1e27624b7fb250913e9a`。
- `tool-result-13/15/17-private.json`：实际进入消息的守护、铁路与混合技能正文。
- `tool-result-30/45/47/73/75-private.json`：首批候选、12306无座班次、经济策略候选、比较、提案的真实回执。
- `assistant_message-43/56/69/84/117-private.json`：按序保存原content与reasoning，不能只摘用户可见一句话推断其收到什么。
- `tool-call-72/74/118-private.json`与`vm-1-events-private.jsonl`：compare/propose同批次的时序和首次静态解释原稿。
- `model_request-121-private.json`：原服务失败请求，含render118和真实诊断119；不是新生产会话恢复入口。

独立恢复资料在 `build/research/journey-guardian/online10-ui-recovery/`：`request-1-private.json`与原request121 byte-equal；`assistant-1/2/3-private.json`、`tool-1/2-private.json`、`source-2-2-explanation-private.splash`保存自修后仍错误的解释；`interaction-safe.json`、`actual-final-ui-tree-private.json`和`allstop-safe.json`区分初始化成功、真实交互失败及全停。此实验3次真实成功请求耗时215.697、126.576、18.929秒，账本终值64calls/3440448tokens；不据此把online10整轮改成PASS。

## 保留的下一次判别实验

未来若明确授权验证查询资料形状，唯一有区分力的入口是首次错误之前的原request36，而不是已经包含assistant43/56/69错误锚定的晚期request121，或只在晚期换compare回执。

复用既有官方host model.chat隔离入口：仅替换`messages[8].content`中的query30候选投影；其余消息、推理、tool call IDs、tools和模型设置逐字保持。实验必须先证明所有原cost/basis、scope、nil/unknown、legs/steps/source及new_nodes守恒。只减少字节长度不构成待验证假设；也不能删除探索资料换取正确答复。若同时改技能词汇或description，必须明确这是额外变量，不能称单变量。

首响应观察它是否仍将500分、170分钟、已查终点19:39提升为总程费用、票制或期限成立。可以条件推荐，不能要求拒绝partial；没有解释该边界则记未覆盖。需要后续工具时仅使用真实冻结只读回执，未知交通分支停止，不伪回执、不写提案/确认、不改期限，也不为成功多次采样。只有真实不同范围内容被准确解释才能判断该受控响应通过；单次结果不构成统计因果保证，手机候选比较、不同Route详情与地图仍需另以实际交互验收。
