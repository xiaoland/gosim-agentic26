# Navigation 原生 Splash API

源码嵌入既有View.on_render，以下写法适用于所有render入口：

- draw_bg、draw_text是有类型的原生成员，不能用普通对象替换。改背景用`draw_bg +:{color:#xf7f7f7}`或`draw_bg.color:#xf7f7f7`；`draw_bg:{color:...}`会类型不符。文字颜色用`draw_text +:{color:#x162e35}`，不猜造text_color、bold或控件顶层color字段。
- text是字符串。字符串内部的ASCII双引号必须保留Splash转义；中文引号可直接使用，例如`NavBody{text:"按“最便宜优先”排列"}`。JSON解码后仍须是完整合法的Splash字符串，不能让内部引号提前结束text。
- 每个控件与根View都各自闭合花括号，例如`View{width:Fill height:Fit flow:Down NavMeta{text:"待核事项"}}`的末尾是两个`}`。source提交完整片段，不能漏掉最后一个子控件或根的闭合。

背景需要显示时指定show_bg:true。文字默认正文16；标题22、辅助14由样式提供，主要比较信息与关键未知用正文层级。字号在text_style内，例如 draw_text +: {text_style:NavRegular{font_size:16} color:#x162e35}；draw_text本身不提供font_size或font_bold，标题可用NavTitle。padding/margin 可用数字或 Inset{top:4 right:4 bottom:4 left:4}；align 用 Align{x:0.5 y:0.5}。这对应锁定 Makepad theme_desktop_dark/button 的原生写法。

render_summary、render_explanation、render_routes、render_suggestions、render_route_detail 分别提交结论、解释、方案列表、建议和详情的任意 source DSL，不规定调用顺序或要求五块齐全；id 可覆盖默认 summary/explanation/routes/suggestions/route_detail，同一入口可用不同 id 创建多个块。五个入口可指定 overlay、height、content_sizing，不提供 visible 参数。新普通块有源码就自然显示；详情承载对应已评估候选的真实分段、费用、耗时、限制和地图，不成立方案也有详情价值。初始隐藏由父容器管理，DSL根不需再次 visible:false；用户通过 DSL 本地 show_block(target_id)／hide_self() 按钮打开或返回，并非让 Agent 决定业务内容可见性。更新已有 id 保留当前显示/页面状态，未指定 overlay 时也保留原位置。它们复用同一执行引擎与逐块诊断回执。

render_ui 仍可提交任意额外内容，用 source 替换整稿，也可用 blocks 提交一个或多个命名区块：`{blocks:[{id:"summary",source:"Label{text:\"本次结果\"}"}]}`。后续相同 id 只替换该块，新 id 追加；未更新块的输入、滚动、脚本和地图状态保留。source 是同一引擎的单文档替换，会清除此前所有块。每块源码在其独立 View.on_render 闭包中执行。可以包含脚本语句和原生控件表达式；这里是 Makepad Splash，不是 JavaScript。不支持 XML/JSX 标签（例如 <View>、</View>）；原生控件直接使用 View{...} 表达式。工具参数的source经JSON解码后是Splash源码；字符串内容中的合法Splash转义仍保留。空值是 nil；函数写 fn(x){...} 或 || {...}；字符串与数字可用 + 连接，例如 `"第" + n + "段"`；number没有`tostr()`方法。

每次顶部提交开始独立规划；不提供澄清问答或恢复模型对话。出行列表保存普通规划详情供历史展示，不自动继续工具执行。

数组使用 `for item in items {...}` 遍历、`items[index]` 访问和 `items.len()` 取长度；没有 Array.find 方法。按字段查找记录时使用 for 遍历并比较字段，找到后保存记录或 return；`ui.body.find("name")` 是原生控件句柄的查找方法，与数组不同。

snapshot() 返回当前真实任务事实，包括 viewport、limits、origin、destination、sources、routes、viewed_route_id、原 arrive_by。 routes中每项的显示字段为id、kind_label、price_label、duration_label、arrival_label、currency、reason、reasons、segments；来源是source对象的provider、queried_at、expires_at、warnings，不存在provider_label。departure_ts、estimated_arrival_ts及顶层received_at、arrive_by都是Unix秒；缺失时间保持未知。不能把get_route或其它工具出现的字段假定为snapshot中的同名字段，已声明但为nil的字段保持未知；动态可选键用对象索引（例如route["optional_key"]）取得值后检查nil，不对不存在的命名字段直接使用点号访问。emit(object) 把用户动作写到父应用。NavRegular 是 Navigation 无衬线字体，Label、Button、ButtonFlat、TextInput 已默认使用它。Label 的应用局部默认值是 width:Fill height:Fit flow:Flow.Right{wrap:true}，文字按可用宽度自然换行；可覆盖原生属性。

模型get_route_graph的默认结果是完整范围的精简身份索引与有序线路关系，node_refs可按需取得指定完整节点及其全部关联；它与原生snapshot的完整事实视图不同。get_route(id)读取完整Route，图索引不替代路线详情。

本轮中国交通的snapshot及任务上下文提供timezone:"Asia/Shanghai"与arrive_by_label，Route摘要、get_route及snapshot.routes提供estimated_arrival_label；它们含日期及“北京时间”，由确定性代码按UTC+8格式化。优先直接使用这些标签；estimated_arrival_label为nil表示请求目的地的到达估计未知；queried_endpoint_arrival_label可能仍有已查路段终点时间，不代表到达目的地。arrival_scope区分requested_routing_point、requested_routing_entry、queried_endpoint_only及unknown；呈现费用使用price_label，到达使用arrival_label；两者已由当前代码包含费用覆盖和到达范围，动态键为nil时显示未知。解释与建议同样绑定当前facts中的reasons、budget_status和deadline_status，让unknown及其原因直接可见。arrival_label会保留已查路段终点或官方入口的范围，不把queried_endpoint_arrival_label另抄成目的地时刻；官方入口不证明设施内部通达。Unix秒本身没有显示时区，不能把UTC钟面静态抄入当地期限，也不能对已格式化标签重复加8小时。此约定适用于当前中国交通事实，不宣称未知地区也使用北京时间。铁路service的真实北京时间发到文本同样可直接使用。铁路腿rail_service的departure_label、arrival_label、duration_label只表示固定列车区间，不包含前后接驳或跨夜等车，不能代替整条Route耗时。

普通 blocks 区块默认 Fit 自然高度，由父 ScrollYView 连续滚动；不是每块占满视口。区块可选 height 指定外视口高度。新稿content_sizing默认natural，内容Fit展开；viewport显式选择内容Fill，由源码管理有限视口；长内容若需要自然展开并由父容器滚动，选择natural。viewport中的根View即使height:Fit，也不会使父body自动提供完整内容的滚动范围；需要有限视口时，在源码中用ScrollYView{width:Fill height:Fill flow:Down ...}承载Fit内容。该字段与原稿一并持久化，旧记录缺字段保持原height规则。`overlay:true` 区块放在生成视口上方，有限高度、独立 ScrollYView；generic render_ui.blocks 的新 overlay 默认隐藏，新普通块默认显示；visible 显式值优先，更新已有块时未指定 visible 则保留当前显示状态。show_block(target_id)／hide_self() 控制父容器打开和关闭，根 DSL 不需重复隐藏。现有块的普通／overlay位置保持不变。整稿 source 仍置于有限高度子 Splash 与 ScrollYView 内。Fit 是内容自然尺寸，Fill 是填父级剩余尺寸，不能在无确定高度的 Fit 父级里假定 Fill 会产生页面高度。新稿natural的body为Fit，即使height指定了外视口也不改变内容尺寸。顶层ScrollYView height:Fill应显式使用content_sizing:viewport；自然Fit长内容由父容器滚动。旧保存稿缺content_sizing时保留旧height规则。控件写 View{width:Fill height:Fit flow:Down ...}；flow 可用 Down、Right、Overlay。子控件不放 children 数组，直接写在父控件的花括号里。控件命名写 title := Label{...}；这个名称不是脚本变量，事件中使用 ui.body.find("title") 取得真实句柄。句柄支持 set_text(text)，TextInput 支持 text()，Image 支持 load_image_from_data_async(bytes)。不要对句柄赋 on_click 属性；事件闭包在构造控件时指定。

横向`Flow.Right{wrap:true}`中的Fill逐项占用当前行剩余宽度，不按兄弟控件均分。短标签或Surface并列时明确使用`width:Fit`或具体宽度；NavSurface的默认width:Fill也占剩余行宽，横排用`NavSurface{width:Fit height:Fit ...}`，保留Fill时放在Down流中。短标签例如`View{width:Fill height:Fit flow:Flow.Right{wrap:true} spacing:8 Label{width:Fit text:"公共交通"} Label{width:Fit text:"约162分钟"}}`；长描述放在Down流中，让`Label{width:Fill height:Fit ...}`按整行宽度换行。默认Fill标签连续放进横向wrap行，后面的标签可能得到极窄宽度并把后续内容推到视口外。

回调共享的脚本状态在 View 表达式外用 `let` 声明，例如 `let bound_route = ""`；事件闭包捕获这个词法变量。View 内的 `name := value` 定义命名成员，不声明同名词法变量，不能用 `bound_route := ""` 代替回调所读取的状态。

Route.destination_access非nil时，呈现其target_kind、routing_point与未知内部通达/楼层/安检；即使endpoint_complete为true，也只到披露的高德入口。canonical目的地身份与其中心坐标保留在snapshot().destination，不把入口事实写成已进入航站楼或完成安检。

路线展示以同一个真实 route id 查找 snapshot().routes，直接使用该记录的 price_label、duration_label、reason 和 segments；事实更新时仍按此 id 重读，不把一次报价或另一条路线的数值静态复制过来。报价替换返回新的派生 Route，derived_from_route_id 指向原路线，原 Route 不变；选择派生方案时，详情文字与地图 target 都使用它的新 id（或对应 geometry_ref）。price_label以短标签呈现已查范围或已知小计，并明确全程费用未知；完整未知原因、计价basis及当前评估仍在cost与assessment中，由同Route详情读取。cost.amount_cents、full_journey_amount_cents、complete及Route.price_cents仅表示请求全程；queried_legs_amount_cents、queried_legs_complete保留已查腿组合报价，known_subtotal_cents保留已知小计。全程金额为nil不是零；不能用已查腿报价齐全称全程总价。到达文案使用arrival_label的范围；端点未核实的queried_endpoint_arrival_label不能改写为到达目的地。

on_facts_changed 是外层已定义的脚本变量，在原生 View 表达式外设置。控件首次安装后会以当前snapshot调用一次，随后只在事实修订变化时调用；初始没有所选Route时应保留占位或已明确绑定的Route。不会自动重建整个界面；Input 编辑内容应保留。不存在外层 on_render、self.snapshot、self.viewport 等变量。

任务上下文的presentation_task是普通规划与守护共有的产品交付目标，不是用户偏好。手机列表用于先比较已评估候选：交通组合、费用及覆盖、到达范围和关键未核事项是主要决策信息，关键unknown与价格、时间同等可见。用户再通过本地操作打开同一Route的完整分段、来源和真实地图；不成立的候选同样有查看价值。文案面向用户，使用线路/站点名称和格式化时间，不暴露内部Route/node ID或原始时间戳；本次处理结束后不用“正在处理”标题。布局与信息组织由Agent决定，不套固定模板。

路线查看的交互目标是打开包含所选路线实际地图、分段、费用和限制的独立详情页或浮层；地图无法加载时显示实际原因。关闭／返回后保留原列表的位置和内容；页面样式与结构由生成稿自行组织。

用户动作 emit({action:"view_route" id:真实路线ID或"viewed"}) 只本地切换当前查看路线，随后 snapshot().viewed_route_id 更新；它不会自动创建详情页面。活跃目标的本轮核验候选被查看后，父应用提供“用当前查看方案准备替代”入口，显示所选候选费用与耗时；查询完成时用户可点击准备提案，再通过父确认控件决定是否替换。该入口不请求模型、不直接保存，也不修改目标约束；历史saved_goal_route不能用作本轮替代。展示候选时提供现有view_route本地动作即可，不要要求用户另发消息才能选择方案。提供查看按钮时，生成稿应通过 on_facts_changed 根据实际当前路线更新自己呈现的选择或路线信息，让用户看见操作结果；不得仅发出事件而保持所有内容不变。父应用只处理本次路线查看和地图加载；不把事件转为第二条用户消息或查询续聊。

render_ui 返回本稿真实 diagnostics；installed仅确认源码安装，rendered确认控件安装及当前snapshot的首次on_facts_changed（若有）执行完成，不证明可见布局。工具等待本次修改的全部区块，包括隐藏详情；等待期限内仍未确认时返回success:false、initialization_unconfirmed，installed仍为真实安装状态，这不是语法诊断。success不表示出行内容或交互目标已经完成。错误说明实际变量、语法或原生类型问题，可以根据结果提交下一稿；应用不改写生成源码。工具回执只包含当时已执行路径的诊断；之后按钮回调的错误仍显示在本地反馈并记录诊断。查询结束后不会回填旧render工具结果或自动启动另一条模型循环。

通用句柄 set_visible(bool)／visible() 可用于页面或自定义浮层。锁定版本 Modal.open/close 与 StackNavigation.push/pop 只有 Rust 接口，当前没有相应 Splash 句柄方法，不能直接写 ui.modal.open()。普通页面切换不销毁隐藏页；不要为打开详情而重建整个列表。

桥接函数签名是`show_block(target_id)`、`hide_self()`和`emit(event)`；其中event是一个对象，不能写`show_block(id:...)`或把事件字段当函数命名实参。普通调用例如`show_block("route_detail")`。

区块之间用 `show_block(target_id)` 打开显式目标，例如 `show_block("route_detail")`；返回按钮用 `hide_self()` 关闭自身，不传目标 ID。target_id 是 render 提交的实际目标区块 id：工具覆盖默认 id 时，打开按钮也使用该实际 id，而不是来源区块名。两个函数复用本地 show_block 事件，不请求模型。底层 `emit({action:"show_block",block:target_id,visible:bool})` 仍可用于其它显式显隐操作。overlay 显示时暂停下层内容区的绘制与交互；关闭后恢复原内容滚动位置。隐藏不销毁该区块或其它列表块。每块 snapshot()/on_facts_changed 接收同一份当前任务事实；父应用每次事实修订只序列化一次，并更新落后区块。事件来源和稿件修订由 emit 内部附加，生成稿无需填写来源元数据；旧稿事件不会操作替换后的新稿。

render_ui的blocks回执逐块返回id、revision、diagnostics、installed、status、notified、complete与visible；container_rect/body_rect只保留在私有渲染诊断，不返回模型。失败块可以单独提交修正版，其它块保留。rendered状态证明本稿已执行并通知，不保证子卡片或按钮可见；尺寸需结合父容器、滚动和隐藏状态判断；widget ID须为本块实际构造的名字，隐藏或离屏控件rect为零不是布局失败证据。自然内容的嵌套View应明确width:Fill height:Fit，不能只写padding和背景而依赖默认尺寸。区块没有删除／重排序接口；新查询清空全部区块。

守护展示事实在snapshot().guardian中，包括goal、proposal、current_check、last_check和remaining_budget_cents。current_check是本轮判定，last_check是历史；页面按事实变化更新，不能静态写“已保存/仍成立”。提案、核验和用户确认的业务规则见journey-guardian。propose_goal/report_goal_check是父Agent工具，不是子VM方法；emit不支持保存确认或费用变更，生成页面只能解释事实。

出行列表恢复成功原始DSL与保存时的历史facts，不恢复模型会话或未确认提案。snapshot().history.current为false，显示生成时刻；历史facts不重算为当前assessment。历史展示只接阅读、地图和区块切换动作；主动核验由父外壳发起。父侧栏负责新建、选择和删除，index显示所选出行详情。

Navigation的生成VM在导入通用SDK后，局部将MaterialTitle／Body／Meta／Action／SecondaryAction默认文字适配为Navigation Sans，保留通用字号、颜色和布局。Nav兼容名称沿用同一Sans字族；普通Label／按钮／输入默认同样适配。此处不改全局主题或其它应用，Agent仍可显式选择自己的字体。


NavSurface、NavCard、NavTitle、NavBody、NavMeta、NavAction、NavSecondaryAction只提供通用样式，已带背景与文字默认值，可直接组合；无需另造hover／down对象。NavAction是按钮，不能放任意子控件；卡片可自由组合内容，需要整卡交互时用实际支持的on_item_tap，不把自然Fit父中的Fill按钮当作已占满可触区域。下面是已实际验证的可选整卡交互组合，不规定业务内容。on_item_tap报告直接子控件；将所有内容放进单个Fill/Fit View，padding放在该子View中，使卡片内部留白同样可点。子Button／NavAction必须提供自己的on_click；不能仅依赖外层Card的on_item_tap接收它的点击。my-detail须替换为本轮实际安装区块，路线选择和数据绑定由调用方自己的事实逻辑完成。

```splash
// 可选通用组合；my-detail 必须是本次已安装的实际详情区块。
NavCard{padding:0 cursor:MouseCursor.Hand
  on_item_tap:|index|{show_block("my-detail")}
  View{width:Fill height:Fit flow:Down spacing:8 padding:16
    NavTitle{text:"任意内容标题"}
    NavBody{text:"任意内容与控件，由 Agent 自主组合。"}
    NavMeta{text:"查看详情 →"}
  }
}
```

render回执的success／changed_blocks_success只描述本次修改区块；interface_success与unresolved_blocks列出当前界面仍失败或未确认的区块。按真实id用render_ui的blocks更新可修正该块，并保留其它成功块；__document也支持此方式，不必以source替换整稿。不要把某次named工具成功当作所有当前区块都已成功，原诊断仍保留。

render入口按本工具声明拒绝未知参数；render_ui的source与blocks互斥，额外item不会安装详情。current_blocks列出实际区块id、修订、安装／通知／显示状态和实际地图事件绑定；没有所需id就不能称其已安装，库存也不证明内容或像素完成。show_block只打开实际已安装目标；可用同一render_ui.blocks入口安装或修正，不要求固定五块或先调用get_route。