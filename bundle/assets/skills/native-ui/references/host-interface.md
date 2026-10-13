# Navigation 原生 Splash API

render_summary、render_explanation、render_routes、render_suggestions、render_route_detail 分别提交结论、解释、方案列表、建议和详情的任意 source DSL，不规定调用顺序或要求五块齐全；id 可覆盖默认 summary/explanation/routes/suggestions/route_detail，同一入口可用不同 id 创建多个块。五个入口可指定 overlay、height、content_sizing，不提供 visible 参数。新普通块有源码就自然显示；详情承载对应已评估候选的真实分段、费用、耗时、限制和地图，不成立方案也有详情价值。初始隐藏由父容器管理，DSL根不需再次 visible:false；用户通过 DSL 本地 show_block(target_id)／hide_self() 按钮打开或返回，并非让 Agent 决定业务内容可见性。更新已有 id 保留当前显示/页面状态，未指定 overlay 时也保留原位置。它们复用同一执行引擎与逐块诊断回执。

render_ui 仍可提交任意额外内容，用 source 替换整稿，也可用 blocks 提交一个或多个命名区块：`{blocks:[{id:"summary",source:"Label{text:\"本次结果\"}"}]}`。后续相同 id 只替换该块，新 id 追加；未更新块的输入、滚动、脚本和地图状态保留。source 是同一引擎的单文档替换，会清除此前所有块。每块源码在其独立 View.on_render 闭包中执行。可以包含脚本语句和原生控件表达式；这里是 Makepad Splash，不是 JavaScript。不支持 XML/JSX 标签（例如 <View>、</View>）；原生控件直接使用 View{...} 表达式。工具参数的source是JSON解码后的Splash源码，字符串外直接写`show_block("route_detail")`，不要在源码中再保留JSON层的`\"`；字符串内部的合法转义仍保留。代码态的多余转义引号会返回其首个行列位置，不会自动改写源码。显示文字是带引号的字符串（例如 text:"最早到达"），不能把中文标题当作未定义变量或把 source 当作隐含变量。空值是 nil；函数写 fn(x){...} 或 || {...}；字符串与数字可用 + 连接，例如 `"第" + n + "段"`；number没有`tostr()`方法。

每次顶部提交开始独立规划；不提供澄清问答或恢复模型对话。出行列表保存普通规划详情供历史展示，不自动继续工具执行。

数组使用 `for item in items {...}` 遍历、`items[index]` 访问和 `items.len()` 取长度；没有 Array.find 方法。按字段查找记录时使用 for 遍历并比较字段，找到后保存记录或 return；`ui.body.find("name")` 是原生控件句柄的查找方法，与数组不同。

snapshot() 返回当前真实任务事实，包括 viewport、limits、origin、destination、sources、routes、viewed_route_id、原 arrive_by。 routes中每项的显示字段为id、kind_label、price_label、duration_label、arrival_label、currency、reason、reasons、segments；来源是source对象的provider、queried_at、expires_at、warnings，不存在provider_label。departure_ts、estimated_arrival_ts及顶层received_at、arrive_by都是Unix秒；缺失时间保持未知。不能把get_route或其它工具出现的字段假定为snapshot中的同名字段，已声明但为nil的字段保持未知；动态可选键用对象索引（例如route["optional_key"]）取得值后检查nil，不对不存在的命名字段直接使用点号访问。emit(object) 把用户动作写到父应用。NavRegular 是 Navigation 无衬线字体，Label、Button、ButtonFlat、TextInput 已默认使用它。Label 的应用局部默认值是 width:Fill height:Fit flow:Flow.Right{wrap:true}，文字按可用宽度自然换行；可覆盖原生属性。

模型get_route_graph的默认结果是完整范围的精简身份索引与有序线路关系，node_refs可按需取得指定完整节点及其全部关联；它与原生snapshot的完整事实视图不同。get_route(id)读取完整Route，图索引不替代路线详情。

本轮中国交通的snapshot及任务上下文提供timezone:"Asia/Shanghai"与arrive_by_label，Route摘要、get_route及snapshot.routes提供estimated_arrival_label；它们含日期及“北京时间”，由确定性代码按UTC+8格式化。优先直接使用这些标签；estimated_arrival_label为nil表示请求目的地的到达估计未知；queried_endpoint_arrival_label可能仍有已查路段终点时间，不代表到达目的地。arrival_scope区分requested_routing_point、requested_routing_entry、queried_endpoint_only及unknown；呈现费用使用price_label，到达使用arrival_label；两者已由当前代码包含费用覆盖和到达范围，动态键为nil时显示未知。解释与建议同样绑定当前facts中的reasons、budget_status和deadline_status，让unknown及其原因直接可见。arrival_label会保留已查路段终点或官方入口的范围，不把queried_endpoint_arrival_label另抄成目的地时刻；官方入口不证明设施内部通达。Unix秒本身没有显示时区，不能把UTC钟面静态抄入当地期限，也不能对已格式化标签重复加8小时。此约定适用于当前中国交通事实，不宣称未知地区也使用北京时间。铁路service的真实北京时间发到文本同样可直接使用。

普通 blocks 区块默认 Fit 自然高度，由父 ScrollYView 连续滚动；不是每块占满视口。区块可选 height 指定外视口高度。新稿content_sizing默认natural，内容Fit展开；viewport显式选择内容Fill，由源码管理有限视口；长内容若需要自然展开并由父容器滚动，选择natural。viewport中的根View即使height:Fit，也不会使父body自动提供完整内容的滚动范围；需要有限视口时，在源码中用ScrollYView{width:Fill height:Fill flow:Down ...}承载Fit内容。该字段与原稿一并持久化，旧记录缺字段保持原height规则。`overlay:true` 区块放在生成视口上方，有限高度、独立 ScrollYView；generic render_ui.blocks 的新 overlay 默认隐藏，新普通块默认显示；visible 显式值优先，更新已有块时未指定 visible 则保留当前显示状态。show_block(target_id)／hide_self() 控制父容器打开和关闭，根 DSL 不需重复隐藏。现有块的普通／overlay位置保持不变。整稿 source 仍置于有限高度子 Splash 与 ScrollYView 内。Fit 是内容自然尺寸，Fill 是填父级剩余尺寸，不能在无确定高度的 Fit 父级里假定 Fill 会产生页面高度。新稿natural的body为Fit，即使height指定了外视口也不改变内容尺寸。顶层ScrollYView height:Fill应显式使用content_sizing:viewport；自然Fit长内容由父容器滚动。旧保存稿缺content_sizing时保留旧height规则。控件写 View{width:Fill height:Fit flow:Down ...}；flow 可用 Down、Right、Overlay。子控件不放 children 数组，直接写在父控件的花括号里。控件命名写 title := Label{...}；这个名称不是脚本变量，事件中使用 ui.body.find("title") 取得真实句柄。句柄支持 set_text(text)，TextInput 支持 text()，Image 支持 load_image_from_data_async(bytes)。不要对句柄赋 on_click 属性；事件闭包在构造控件时指定。

横向`Flow.Right{wrap:true}`中的Fill逐项占用当前行剩余宽度，不按兄弟控件均分。短标签或Surface并列时明确使用`width:Fit`或具体宽度；NavSurface的默认width:Fill也占剩余行宽，横排用`NavSurface{width:Fit height:Fit ...}`，保留Fill时放在Down流中。短标签例如`View{width:Fill height:Fit flow:Flow.Right{wrap:true} spacing:8 Label{width:Fit text:"公共交通"} Label{width:Fit text:"约162分钟"}}`；长描述放在Down流中，让`Label{width:Fill height:Fit ...}`按整行宽度换行。默认Fill标签连续放进横向wrap行，后面的标签可能得到极窄宽度并把后续内容推到视口外。

回调共享的脚本状态在 View 表达式外用 `let` 声明，例如 `let bound_route = ""`；事件闭包捕获这个词法变量。View 内的 `name := value` 定义命名成员，不声明同名词法变量，不能用 `bound_route := ""` 代替回调所读取的状态。

有类型的原生成员需要实际类型构造或已有成员扩展，普通对象不能替代它。背景可写 show_bg:true draw_bg +: {color:#xf7f7f7} 或 draw_bg.color:#xf7f7f7。文字可写 draw_text +: {text_style:NavRegular{font_size:14} color:#x162e35}。padding/margin 可用数字或 Inset{top:4 right:4 bottom:4 left:4}；align 用 Align{x:0.5 y:0.5}。这对应锁定 Makepad theme_desktop_dark/button 的原生写法。

以下是分别提交给 render_routes 和 render_route_detail 的低层区块源码示例，示例省略工具的 id 参数，使用真实默认 routes 和 route_detail。列表打开父详情容器并更新查看路线；详情按 viewed_route_id 读取当前路线，并在取得当前目录后绑定自己的命名地图；本例用本地上一段／下一段切换每页至多四条真实折线，页数由目录计算，不限两页。父容器管理初始隐藏，详情源码根正常可见。布局、名称和所选候选由生成稿决定，不提供 RouteSheet 或自动详情组件。viewport 是生成区域最近已绘制的可见范围，不是内容高度上限；Fit 内容可自然增长并滚动。

列表 source：

```splash
let route_id = facts.routes[0].id
View{width:Fill height:Fit flow:Down
    Label{text:"本次候选"}
    Button{text:"查看路线详情" on_click: || {
        show_block("route_detail")
        emit({action:"view_route" id:route_id})
    }}
}
```

对应 render_route_detail 省略 id 时默认区块为 route_detail，source：

```splash
let route_id = ""
let bound_route = ""
let page = 0
let page_count = 0
fn route_detail(current, id){
    for route in current.routes {
        if route.id == id {
            let text = route.kind_label + " · " + route.duration_label + " · " + route.price_label
            let arrival = route["arrival_label"]
            text += "\n" + if arrival != nil {arrival} else {"到达时间与范围未知"}
            if route.reason != nil {text += "\n" + route.reason}
            for segment in route.segments {
                if segment.description != nil {text += "\n" + segment.description}
                for line in segment.buslines {
                    text += "\n" + line.name + "：" + line.departure_stop + " → " + line.arrival_stop
                }
            }
            return text
        }
    }
    return "该路线已不在本次结果中"
}
fn bind_page(current){
    for route in current.routes {
        if route.id == route_id {
            if route.map_paths == nil {
                ui.body.find("page_note").set_text("当前路线地图目录尚未取得")
                return
            }
            page_count = 0
            let in_page = 0
            let indices = []
            for path in route.map_paths {
                if in_page == 0 {page_count += 1}
                in_page += 1
                if in_page == 4 {in_page = 0}
                if path.index >= page * 4 && path.index < (page + 1) * 4 {
                    indices.push(path.index)
                }
            }
            if indices.len() == 0 {
                ui.body.find("page_note").set_text("当前路线没有可绘制的折线")
                return
            }
            ui.body.find("page_note").set_text("本图分段 " + (page + 1) + "/" + page_count + "，非全行程起终点")
            bound_route = route_id
            emit({action:"map" widget:"route_map" target:route_id path_indices:indices status_widget:"map_note" interactive:true})
            return
        }
    }
}
on_facts_changed = fn(current){
    if current.viewed_route_id != nil && current.viewed_route_id != "" && current.viewed_route_id != route_id {
        route_id = current.viewed_route_id
        page = 0
        page_count = 0
        bound_route = ""
    }
    ui.body.find("detail_text").set_text(route_detail(current, route_id))
    if route_id != "" && bound_route != route_id {bind_page(current)}
}
View{width:Fill height:Fit flow:Down spacing:8
    Button{text:"返回列表" on_click: || hide_self()}
    detail_text := Label{text:"打开候选后显示当前路线详情"}
    page_note := Label{text:"打开详情后取得当前路线地图目录"}
    View{width:Fill height:Fit flow:Right spacing:8
        Button{text:"上一段" on_click: || {
            if page > 0 {
                page -= 1
                bind_page(snapshot())
            }
        }}
        Button{text:"下一段" on_click: || {
            if page + 1 < page_count {
                page += 1
                bind_page(snapshot())
            }
        }}
    }
    route_map := AutoNaviMapView{width:Fill height:240
        on_camera_changed: fn(lon,lat,zoom,width,height,request){
            emit({action:"map_camera" widget:"route_map" center_lon:lon center_lat:lat zoom:zoom width:width height:height request:request})
        }
    }
    map_note := Label{text:"等待本图分段加载"}
}
```

Route.destination_access非nil时，呈现其target_kind、routing_point与未知内部通达/楼层/安检；即使endpoint_complete为true，也只到披露的高德入口。canonical目的地身份与其中心坐标保留在snapshot().destination，不把入口事实写成已进入航站楼或完成安检。

map 事件建立路线目标绑定并初始化相机；map_camera 回调使用这个已存在的绑定请求后续视口，不能替代首次 map 事件。本例普通事实更新只刷新文案，不重复绑定地图；切换路线重置页码并绑定新路线，翻页绑定所选真实折线。再次打开同一路线详情保留页码、地图相机和列表位置。多张地图或其它分页布局同样可用，示例不规定页面结构。单文档 source 也可以用自己命名的 View.set_visible 切换内页；此时隐藏与打开都由同一文档管理，这是另一种局部交互方式，不要把内页隐藏复制到父已管理隐藏的独立详情区块根。

路线展示以同一个真实 route id 查找 snapshot().routes，直接使用该记录的 price_label、duration_label、reason 和 segments；事实更新时仍按此 id 重读，不把一次报价或另一条路线的数值静态复制过来。报价替换返回新的派生 Route，derived_from_route_id 指向原路线，原 Route 不变；选择派生方案时，详情文字与地图 target 都使用它的新 id（或对应 geometry_ref）。price_label对全程费用未知的路线明确“已知小计；全程费用未知”。cost.amount_cents、full_journey_amount_cents、complete及Route.price_cents仅表示请求全程；queried_legs_amount_cents、queried_legs_complete保留已查腿组合报价，known_subtotal_cents保留已知小计。全程金额为nil不是零；不能用已查腿报价齐全称全程总价。到达文案使用arrival_label的范围；端点未核实的queried_endpoint_arrival_label不能改写为到达目的地。

on_facts_changed 是外层已定义的脚本变量，在原生 View 表达式外设置。控件首次安装后会以当前snapshot调用一次，随后只在事实修订变化时调用；初始没有所选Route时应保留占位或已明确绑定的Route。不会自动重建整个界面；Input 编辑内容应保留。不存在外层 on_render、self.snapshot、self.viewport 等变量。

路线查看的交互目标是打开包含所选路线实际地图、分段、费用和限制的独立详情页或浮层；地图无法加载时显示实际原因。关闭／返回后保留原列表的位置和内容；页面样式与结构由生成稿自行组织。

用户动作 emit({action:"view_route" id:真实路线ID或"viewed"}) 只本地切换当前查看路线，随后 snapshot().viewed_route_id 更新；它不会自动创建详情页面。活跃目标的本轮核验候选被查看后，父应用提供“用当前查看方案准备替代”入口，显示所选候选费用与耗时；查询完成时用户可点击准备提案，再通过父确认控件决定是否替换。该入口不请求模型、不直接保存，也不修改目标约束；历史saved_goal_route不能用作本轮替代。展示候选时提供现有view_route本地动作即可，不要要求用户另发消息才能选择方案。提供查看按钮时，生成稿应通过 on_facts_changed 根据实际当前路线更新自己呈现的选择或路线信息，让用户看见操作结果；不得仅发出事件而保持所有内容不变。父应用只处理本次路线查看和地图加载；不把事件转为第二条用户消息或查询续聊。地图可自由放多个命名 AutoNaviMapView。这是原生GCJ-02摄像视口，拖动／缩放后通过on_camera_changed回调请求该新视口的高德底图与同源真实路线，并非只缩放旧图。构造时应给有限高度，并将回调的六个实参用map_camera事件传给父应用，见上例。回调request由控件产生，应用和模型不另造编号。手势在地图区域内改变相机；区域外的详情滚动由页面自己的ScrollYView处理。底图按官方静态图接口更新，有网络延迟，不是连续瓦片加载。

emit({action:"map" widget:"image_name" target:真实路线ID或"viewed"或"destination" status_widget:"caption_name" interactive:true})。父应用绑定真实路线、初始化全路线视口，再分别请求和加载真实高德视口图片；status_widget 是可选命名 Label，显示来源和加载错误。target 用当前实际路线ID可固定本次详情目标；用 "viewed" 会随父查看状态更新，"destination" 仅显示实际目的地。命名地图应已构造且具有限高度，先显示详情页再发事件，父才能向实际实例加载字节。切换目标显示加载状态，新路线重新匹配全路线视口；同一目标再次打开保留原生相机和当前run图片。来源与加载反馈由 status_widget 接收。旧Image静态图接口仍可用，省略interactive:true即可；它只有图片，不具备地图拖动缩放。未知或缺失几何不伪造直线。

render_ui 返回本稿真实 diagnostics；installed仅确认源码安装，rendered确认控件安装及当前snapshot的首次on_facts_changed（若有）执行完成，不证明可见布局。工具等待本次修改的全部区块，包括隐藏详情；等待期限内仍未确认时返回success:false、initialization_unconfirmed，installed仍为真实安装状态，这不是语法诊断。success不表示出行内容或交互目标已经完成。错误说明实际变量、语法或原生类型问题，可以根据结果提交下一稿；应用不改写生成源码。工具回执只包含当时已执行路径的诊断；之后按钮回调的错误仍显示在本地反馈并记录诊断。查询结束后不会回填旧render工具结果或自动启动另一条模型循环。

通用句柄 set_visible(bool)／visible() 可用于页面或自定义浮层。锁定版本 Modal.open/close 与 StackNavigation.push/pop 只有 Rust 接口，当前没有相应 Splash 句柄方法，不能直接写 ui.modal.open()。普通页面切换不销毁隐藏页；不要为打开详情而重建整个列表。


高德静态地图接口每次最多接收 **4 条独立折线（paths）**，这是供应商接口能力，不是应用自动分组规则。`snapshot().routes`／`get_route({id})` 的每条路线都有 `map_paths` 目录：`index` 是最终相接合并后的折线索引，`start`／`end` 是真实几何端点，`point_count` 是点数。目录完整保留全部折线；它与公交 `segments` 下标不是同一概念。`map_metadata` 给出 `catalog_status`（`not_loaded`／`ready`）、`path_count`（未读取时为 nil，读取后为实际数量）和 `max_paths_per_image:4`。`map_paths` 为 nil 表示目录尚未读取，不表示没有几何，也不表示折线数不超过四条。目录对应当前 Route 的实际几何：extend 返回的新路线不能沿用旧路线目录；仅替换报价而几何不变的派生路线可复用同源目录。目录未知时，`get_route({id})` 可取得该路线目录；实际地图取得几何后，snapshot 也会更新目录。普通地图可不传索引来显示四条以内的完整路线；数量超过四条会明确拒绝本幅请求并提供所有可用索引，不会静默截取前四条。未知数量不等于已满足供应商的四条上限。

地图事件可选 `path_indices`，从该目录选择完整折线，例如 `emit({action:"map",widget:"part_map",target:id,path_indices:[0,1,2],status_widget:"part_note",interactive:true})`。未提供时选择完整路线，仍受每图四条上限；不会自动截前四条、拆图或跨缺口连接。多于四条时，可以根据目录分步嵌入多张独立命名地图，每张选择至多四条，张数、分组、打开步骤和布局由生成稿决定。展示完整路线时，各图的索引选择合起来应覆盖全部实际折线，缺失几何仍说明真实缺失。索引随当前路线目录变化，不猜测索引，也不把某些分段称作完整路线。

每个命名 AutoNaviMapView 保留自己的相机和加载状态，`on_camera_changed` 仍使用该控件名发出六参 `map_camera` 事件。选择了 path_indices 的图会 fit 所选几何范围；图上的 A/B 是本图所选几何首末点，状态说明“本图分段端点，非全行程起终点”。原行程起终点、完整费用与限制仍在路线事实中。`status_widget` 可显示分图范围、来源、加载或供应商错误。

桥接函数签名是`show_block(target_id)`、`hide_self()`和`emit(event)`；其中event是一个对象，不能写`show_block(id:...)`或把事件字段当函数命名实参。普通调用例如`show_block("route_detail")`。

区块之间用 `show_block(target_id)` 打开显式目标，例如 `show_block("route_detail")`；返回按钮用 `hide_self()` 关闭自身，不传目标 ID。target_id 是 render 提交的实际目标区块 id：工具覆盖默认 id 时，打开按钮也使用该实际 id，而不是来源区块名。两个函数复用本地 show_block 事件，不请求模型。底层 `emit({action:"show_block",block:target_id,visible:bool})` 仍可用于其它显式显隐操作。overlay 显示时暂停下层内容区的绘制与交互；关闭后恢复原内容滚动位置。隐藏不销毁该区块或其它列表块。每块 snapshot()/on_facts_changed 接收同一份当前任务事实；父应用每次事实修订只序列化一次，并更新落后区块。事件来源和稿件修订由 emit 内部附加，生成稿无需填写来源元数据；旧稿事件不会操作替换后的新稿。

地图 widget/status_widget 名字局限在发事件的区块内，不同块可以使用相同名字。map、map_camera、map_fit 事件仍按上文使用；替换一个块仅撤掉它的地图绑定，其它块相机保留。跨块先显示详情块，再以 view_route 更新当前查看路线；详情块可在 on_facts_changed 中更新自己的内容并发 map 事件，或直接绑定事实中的路线 ID。没有自动创建业务详情页面。

render_ui的blocks回执逐块返回id、revision、diagnostics、installed、status、notified、complete与visible；container_rect/body_rect只保留在私有渲染诊断，不返回模型。失败块可以单独提交修正版，其它块保留。rendered状态证明本稿已执行并通知，不保证子卡片或按钮可见；尺寸需结合父容器、滚动和隐藏状态判断。自然内容的嵌套View应明确width:Fill height:Fit，不能只写padding和背景而依赖默认尺寸。区块没有删除／重排序接口；新查询清空全部区块。

地图事件 target 也可直接引用 query_route 返回的 geometry_ref（polyline_…）；父应用按同一候选的真实几何加载，不由模型传折线坐标。原路线 id、viewed 和 path_indices 仍可用；新查询使上一轮引用失效。

守护展示事实在snapshot().guardian中，包括goal、proposal、current_check、last_check和remaining_budget_cents。current_check是本轮判定，last_check是历史；页面按事实变化更新，不能静态写“已保存/仍成立”。提案、核验和用户确认的业务规则见journey-guardian。propose_goal/report_goal_check是父Agent工具，不是子VM方法；emit不支持保存确认或费用变更，生成页面只能解释事实。

出行列表恢复成功原始DSL与保存时的历史facts，不恢复模型会话或未确认提案。snapshot().history.current为false，显示生成时刻；历史facts不重算为当前assessment。历史展示只接阅读、地图和区块切换动作；主动核验由父外壳发起。父侧栏负责新建、选择和删除，index显示所选出行详情。

NavSurface、NavCard、NavTitle、NavBody、NavMeta、NavAction、NavSecondaryAction只提供通用样式。下面是已实际验证的可选整卡交互组合，不规定业务内容。on_item_tap报告直接子控件；将所有内容放进单个Fill/Fit View，padding放在该子View中，使卡片内部留白同样可点。子Button／NavAction必须提供自己的on_click；不能仅依赖外层Card的on_item_tap接收它的点击。my-detail须替换为本轮实际安装区块，路线选择和数据绑定由调用方自己的事实逻辑完成。

```splash
// 可选通用组合；my-detail 必须是本次已安装的实际详情区块。
NavCard{padding:0 cursor:MouseCursor.Hand
  draw_bg:NavSecondaryAction.draw_bg{color:#xf0f5f3 color_hover:#xe4eeea color_down:#xc5dbd1}
  animator:Animator{
    hover:{default:@off
      off:AnimatorState{from:{all:Forward{duration:0.1}} apply:{draw_bg:{hover:0.0}}}
      on:AnimatorState{from:{all:Forward{duration:0.1}} apply:{draw_bg:{hover:1.0}}}
    }
    down:{default:@off
      off:AnimatorState{from:{all:Forward{duration:0.1}} apply:{draw_bg:{down:0.0}}}
      on:AnimatorState{from:{all:Forward{duration:0.0}} apply:{draw_bg:{down:1.0}}}
    }
  }
  on_item_tap:|index|{show_block("my-detail")}
  View{width:Fill height:Fit flow:Down spacing:8 padding:16
    NavTitle{text:"任意内容标题"}
    NavBody{text:"任意内容与控件，由 Agent 自主组合。"}
    NavMeta{text:"查看详情 →"}
  }
}
```

静态底图传输由父应用处理，不需要生成稿复制polyline。父应用保留原始完整几何及目录，在当前相机下分批派生约一像素误差内的显示折线，保留各路径端点与独立身份；放大或缩小时按新相机重新计算，不能将概览点集作为新的供应商路线。中心、标记及显示点遵从六位小数接口精度。已派发的服务或网络失败仍显示真实地图错误，不自动重试，也不把图片未返回标成ready。

render回执的success／changed_blocks_success只描述本次修改区块；interface_success与unresolved_blocks列出当前界面仍失败或未确认的区块。按真实id用render_ui的blocks更新可修正该块，并保留其它成功块；__document也支持此方式，不必以source替换整稿。不要把某次named工具成功当作所有当前区块都已成功，原诊断仍保留。

render入口按本工具声明拒绝未知参数；render_ui的source与blocks互斥，额外item不会安装详情。current_blocks列出实际区块id、修订、安装／通知／显示状态和实际地图事件绑定；没有所需id就不能称其已安装，库存也不证明内容或像素完成。show_block只打开实际已安装目标；可用同一render_ui.blocks入口安装或修正，不要求固定五块或先调用get_route。

地图目录的map_metadata.selection_groups提供完整覆盖全部路径的可选path_indices分组，每组最多4条，selection_scope仅代表所选真实折线，缺口不补线。它不会自动选组或安装地图。只有已知目录不超过4条时map事件可省略path_indices；目录未知时可读取Route或等当前facts目录后明确选择分图。render回执current_blocks的map_bindings记录实际state／status／http_requested：未绑定、等待、失败与ready不能互相替代，也不证明像素可见。
