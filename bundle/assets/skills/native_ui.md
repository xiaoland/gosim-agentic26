# Navigation 原生 Splash API

render_ui 的 source 在已经存在的 View.on_render 闭包中执行。可以包含脚本语句和原生控件表达式；这里是 Makepad Splash，不是 JavaScript。空值是 nil；函数写 fn(x){...} 或 || {...}；字符串与数字可用 + 连接。

每次顶部查询开始一个新任务；不存在澄清问答、跨查询继续或结果保存。

snapshot() 返回当前真实任务事实，包括 viewport、limits、origin、destination、sources、routes、viewed_route_id、原 arrive_by。emit(object) 把用户动作写到父应用。NavRegular 是 Navigation 无衬线字体，Label、Button、ButtonFlat、TextInput 已默认使用它。Label 的应用局部默认值是 width:Fill height:Fit flow:Flow.Right{wrap:true}，文字按可用宽度自然换行；可覆盖原生属性。

生成内容置于有限高度的子 Splash 内，子 ScrollYView 包含 View/Fit，按内容自然高度提供滚动；父区域承载运行反馈。Fit 是内容自然尺寸，Fill 是填父级剩余尺寸，不能在无确定高度的 Fit 父级里假定 Fill 会产生页面高度。控件写 View{width:Fill height:Fit flow:Down ...}；flow 可用 Down、Right、Overlay。子控件不放 children 数组，直接写在父控件的花括号里。控件命名写 title := Label{...}；这个名称不是脚本变量，事件中使用 ui.body.find("title") 取得真实句柄。句柄支持 set_text(text)，TextInput 支持 text()，Image 支持 load_image_from_data_async(bytes)。不要对句柄赋 on_click 属性；事件闭包在构造控件时指定。

有类型的原生成员需要实际类型构造或已有成员扩展，普通对象不能替代它。背景可写 show_bg:true draw_bg +: {color:#xf7f7f7} 或 draw_bg.color:#xf7f7f7。文字可写 draw_text +: {text_style:NavRegular{font_size:14} color:#x162e35}。padding/margin 可用数字或 Inset{top:4 right:4 bottom:4 left:4}；align 用 Align{x:0.5 y:0.5}。这对应锁定 Makepad theme_desktop_dark/button 的原生写法。

以下示例使用普通 View 的可见性切换形成独立详情页面。它是低层交互示例，页面、标题、内容组织由生成稿决定；不提供 RouteSheet 或自动详情组件。两个页面有各自的滚动容器，返回只改变可见性，不重新 render 列表。viewport 是生成区域最近已绘制的可用范围，有限高度让内部 Fill 容器能够计算滚动。

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
    ui.body.find("route_map").set_visible(false)
    ui.body.find("map_note").set_text("正在加载所选路线地图")
    emit({action:"view_route" id:id})
    emit({action:"map" widget:"route_map" target:id status_widget:"map_note"})
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
            route_map := Image{width:Fill height:200 visible:false}
            map_note := Label{text:""}
            detail_text := Label{text:""}
        }
    }
}
```

on_facts_changed 是外层已定义的脚本变量，在原生 View 表达式外设置。不会自动重建整个界面；Input 编辑内容应保留。不存在外层 on_render、self.snapshot、self.viewport 等变量。

路线查看的交互目标是打开包含所选路线实际地图、分段、费用和限制的独立详情页或浮层；地图无法加载时显示实际原因。关闭／返回后保留原列表的位置和内容；页面样式与结构由生成稿自行组织。

用户动作 emit({action:"view_route" id:真实路线ID或"viewed"}) 只本地切换当前查看路线，随后 snapshot().viewed_route_id 更新；它不会自动创建详情页面。提供查看按钮时，生成稿应通过 on_facts_changed 根据实际当前路线更新自己呈现的选择或路线信息，让用户看见操作结果；不得仅发出事件而保持所有内容不变。父应用只处理本次路线查看和地图加载；不把事件转为第二条用户消息或查询续聊。地图可自由放多个命名 Image，emit({action:"map" widget:"image_name" target:真实路线ID或"viewed"或"destination" status_widget:"caption_name"})。父应用分别请求和加载真实高德静态地图；status_widget 是可选命名 Label，显示来源和加载错误。target 用当前实际路线ID可固定本次详情目标；用 "viewed" 会随父查看状态更新，"destination" 仅显示实际目的地。命名 Image 应已构造且具有限高度，先显示详情页再发事件，父才能向实际实例加载字节。切换目标先隐藏旧图并显示加载状态，避免把前一条路线图误认成当前图；同一目标再次打开可复用当前run缓存。来源与加载反馈由 status_widget 接收。未知或缺失几何不伪造直线。

render_ui 返回本稿真实 diagnostics。错误说明实际变量、语法或原生类型问题，可以根据结果提交下一稿；应用不改写生成源码。

通用句柄 set_visible(bool)／visible() 可用于页面或自定义浮层。锁定版本 Modal.open/close 与 StackNavigation.push/pop 只有 Rust 接口，当前没有相应 Splash 句柄方法，不能直接写 ui.modal.open()。普通页面切换不销毁隐藏页；不要为打开详情而重建整个列表。
