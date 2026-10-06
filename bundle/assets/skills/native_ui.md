# Navigation 原生 Splash API

render_ui 的 source 替换本次整稿，在已经存在的 View.on_render 闭包中执行；不是向旧稿追加节点。可以包含脚本语句和原生控件表达式；这里是 Makepad Splash，不是 JavaScript。不支持 XML/JSX 标签（例如 <View>、</View>）；原生控件直接使用 View{...} 表达式。显示文字是带引号的字符串（例如 text:"最早到达"），不能把中文标题当作未定义变量或把 source 当作隐含变量。空值是 nil；函数写 fn(x){...} 或 || {...}；字符串与数字可用 + 连接。

每次顶部查询开始一个新任务；不存在澄清问答、跨查询继续或结果保存。

数组使用 `for item in items {...}` 遍历、`items[index]` 访问和 `items.len()` 取长度；没有 Array.find 方法。按字段查找记录时使用 for 遍历并比较字段，找到后保存记录或 return；`ui.body.find("name")` 是原生控件句柄的查找方法，与数组不同。

snapshot() 返回当前真实任务事实，包括 viewport、limits、origin、destination、sources、routes、viewed_route_id、原 arrive_by。emit(object) 把用户动作写到父应用。NavRegular 是 Navigation 无衬线字体，Label、Button、ButtonFlat、TextInput 已默认使用它。Label 的应用局部默认值是 width:Fill height:Fit flow:Flow.Right{wrap:true}，文字按可用宽度自然换行；可覆盖原生属性。

生成内容置于有限高度的子 Splash 内，子 ScrollYView 包含 View/Fit，按内容自然高度提供滚动；父区域承载运行反馈。Fit 是内容自然尺寸，Fill 是填父级剩余尺寸，不能在无确定高度的 Fit 父级里假定 Fill 会产生页面高度。控件写 View{width:Fill height:Fit flow:Down ...}；flow 可用 Down、Right、Overlay。子控件不放 children 数组，直接写在父控件的花括号里。控件命名写 title := Label{...}；这个名称不是脚本变量，事件中使用 ui.body.find("title") 取得真实句柄。句柄支持 set_text(text)，TextInput 支持 text()，Image 支持 load_image_from_data_async(bytes)。不要对句柄赋 on_click 属性；事件闭包在构造控件时指定。

有类型的原生成员需要实际类型构造或已有成员扩展，普通对象不能替代它。背景可写 show_bg:true draw_bg +: {color:#xf7f7f7} 或 draw_bg.color:#xf7f7f7。文字可写 draw_text +: {text_style:NavRegular{font_size:14} color:#x162e35}。padding/margin 可用数字或 Inset{top:4 right:4 bottom:4 left:4}；align 用 Align{x:0.5 y:0.5}。这对应锁定 Makepad theme_desktop_dark/button 的原生写法。

以下示例使用普通 View 的可见性切换形成独立详情页面。它是低层交互示例，页面、标题、内容组织由生成稿决定；不提供 RouteSheet 或自动详情组件。两个页面有各自的滚动容器，返回只改变可见性，不重新 render 列表。viewport 是生成区域最近已绘制的可见范围，不是内容高度上限；可见视口内的 Fit 内容可自然增长并滚动，有限视口让内部 Fill 容器能够计算滚动。

```splash
let opened_route = ""
fn route_detail(current, id){
    for route in current.routes {
        if route.id == id {
            let text = route.kind_label + " · " + route.duration_label + " · " + route.price_label
            if !route.passed {text += "\n" + route.reason}
            for segment in route.segments {
                if segment.description != nil {text += "\n" + segment.description}
                if segment.walking_distance_m != nil {text += "\n步行 " + segment.walking_distance_m + " 米"}
                for line in segment.buslines {text += "\n" + line.name + "：" + line.departure_stop + " → " + line.arrival_stop}
            }
            return text
        }
    }
    return "本次查询没有这条路线"
}
fn open_detail(id){
    opened_route = id
    ui.body.find("detail_text").set_text(route_detail(snapshot(), id))
    ui.body.find("list_page").set_visible(false)
    ui.body.find("detail_page").set_visible(true)
    ui.body.find("route_map").set_visible(true)
    ui.body.find("map_note").set_text("正在加载所选路线地图")
    emit({action:"view_route" id:id})
    emit({action:"map" widget:"route_map" target:id status_widget:"map_note" interactive:true})
}
fn return_to_list(){
    ui.body.find("detail_page").set_visible(false)
    ui.body.find("list_page").set_visible(true)
    opened_route = ""
}
on_facts_changed = fn(current){
    if opened_route != "" {ui.body.find("detail_text").set_text(route_detail(current, opened_route))}
}
View{width:Fill height:facts.viewport.height flow:Overlay
    list_page := ScrollYView{width:Fill height:Fill flow:Down
        Label{text:"本次候选"}
        if facts.routes.len() > 0 {
            open_first := Button{text:"查看第一条路线" on_click: || open_detail(facts.routes[0].id)}
        }
        if facts.routes.len() > 1 {
            Button{text:"查看另一条路线" on_click: || open_detail(facts.routes[1].id)}
        }
    }
    detail_page := View{width:Fill height:Fill flow:Down visible:false
        back := Button{text:"返回列表" on_click: || return_to_list()}
        detail_scroll := ScrollYView{width:Fill height:Fill flow:Down
            route_map := AutoNaviMapView{width:Fill height:240
                on_camera_changed: fn(lon,lat,zoom,width,height,request){
                    emit({action:"map_camera" widget:"route_map" center_lon:lon center_lat:lat zoom:zoom width:width height:height request:request})
                }
            }
            View{width:Fill height:Fit flow:Right spacing:8
                Button{text:"放大" on_click: || ui.body.find("route_map").zoom_by(1)}
                Button{text:"缩小" on_click: || ui.body.find("route_map").zoom_by(-1)}
                Button{text:"全路线" on_click: || emit({action:"map_fit" widget:"route_map"})}
            }
            map_note := Label{text:""}
            detail_text := Label{text:""}
        }
    }
}
```

on_facts_changed 是外层已定义的脚本变量，在原生 View 表达式外设置。不会自动重建整个界面；Input 编辑内容应保留。不存在外层 on_render、self.snapshot、self.viewport 等变量。

路线查看的交互目标是打开包含所选路线实际地图、分段、费用和限制的独立详情页或浮层；地图无法加载时显示实际原因。关闭／返回后保留原列表的位置和内容；页面样式与结构由生成稿自行组织。

用户动作 emit({action:"view_route" id:真实路线ID或"viewed"}) 只本地切换当前查看路线，随后 snapshot().viewed_route_id 更新；它不会自动创建详情页面。提供查看按钮时，生成稿应通过 on_facts_changed 根据实际当前路线更新自己呈现的选择或路线信息，让用户看见操作结果；不得仅发出事件而保持所有内容不变。父应用只处理本次路线查看和地图加载；不把事件转为第二条用户消息或查询续聊。地图可自由放多个命名 AutoNaviMapView。这是原生GCJ-02摄像视口，拖动／缩放后通过on_camera_changed回调请求该新视口的高德底图与同源真实路线，并非只缩放旧图。构造时应给有限高度，并将回调的六个实参用map_camera事件传给父应用，见上例。回调request由控件产生，应用和模型不另造编号。手势在地图区域内改变相机；区域外的详情滚动由页面自己的ScrollYView处理。底图按官方静态图接口更新，有网络延迟，不是连续瓦片加载。

emit({action:"map" widget:"image_name" target:真实路线ID或"viewed"或"destination" status_widget:"caption_name" interactive:true})。父应用绑定真实路线、初始化全路线视口，再分别请求和加载真实高德视口图片；status_widget 是可选命名 Label，显示来源和加载错误。target 用当前实际路线ID可固定本次详情目标；用 "viewed" 会随父查看状态更新，"destination" 仅显示实际目的地。命名地图应已构造且具有限高度，先显示详情页再发事件，父才能向实际实例加载字节。切换目标显示加载状态，新路线重新匹配全路线视口；同一目标再次打开保留原生相机和当前run图片。来源与加载反馈由 status_widget 接收。旧Image静态图接口仍可用，省略interactive:true即可；它只有图片，不具备地图拖动缩放。未知或缺失几何不伪造直线。

render_ui 返回本稿真实 diagnostics；success 只表示执行时没有已报告错误，不表示出行内容或交互目标已经完成。错误说明实际变量、语法或原生类型问题，可以根据结果提交下一稿；应用不改写生成源码。

通用句柄 set_visible(bool)／visible() 可用于页面或自定义浮层。锁定版本 Modal.open/close 与 StackNavigation.push/pop 只有 Rust 接口，当前没有相应 Splash 句柄方法，不能直接写 ui.modal.open()。普通页面切换不销毁隐藏页；不要为打开详情而重建整个列表。


高德静态地图接口每次最多接收 **4 条独立折线（paths）**，这是供应商接口能力，不是应用自动分组规则。`snapshot().routes`／`get_route({id})` 的每条路线都有 `map_paths` 目录：`index` 是最终相接合并后的折线索引，`start`／`end` 是真实几何端点，`point_count` 是点数。目录完整保留全部折线；它与公交 `segments` 下标不是同一概念。

地图事件可选 `path_indices`，从该目录选择完整折线，例如 `emit({action:"map",widget:"part_map",target:id,path_indices:[0,1,2],status_widget:"part_note",interactive:true})`。未提供时仍请求完整路线；不会自动截前四条、拆图或跨缺口连接。多于四条时，可以根据目录分步嵌入多张独立命名地图，每张选择至多四条，张数、分组、打开步骤和布局由生成稿决定。展示完整路线时，各图的索引选择合起来应覆盖全部实际折线，缺失几何仍说明真实缺失。索引随当前路线目录变化，不猜测索引，也不把某些分段称作完整路线。

每个命名 AutoNaviMapView 保留自己的相机和加载状态，`on_camera_changed` 仍使用该控件名发出六参 `map_camera` 事件。选择了 path_indices 的图会 fit 所选几何范围；图上的 A/B 是本图所选几何首末点，状态说明“本图分段端点，非全行程起终点”。原行程起终点、完整费用与限制仍在路线事实中。`status_widget` 可显示分图范围、来源、加载或供应商错误。
