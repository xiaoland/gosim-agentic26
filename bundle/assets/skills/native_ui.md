# Navigation 原生 Splash API

render_ui 的 source 在已经存在的 View.on_render 闭包中执行。可以包含脚本语句和原生控件表达式；这里是 Makepad Splash，不是 JavaScript。空值是 nil；函数写 fn(x){...} 或 || {...}；字符串与数字可用 + 连接。

每次顶部查询开始一个新任务；不存在澄清问答、跨查询继续或结果保存。

snapshot() 返回当前真实任务事实，包括 viewport、limits、origin、destination、sources、routes、viewed_route_id、原 arrive_by。emit(object) 把用户动作写到父应用。NavRegular 是 Navigation 无衬线字体，Label、Button、ButtonFlat、TextInput 已默认使用它。Label 的应用局部默认值是 width:Fill height:Fit flow:Flow.Right{wrap:true}，文字按可用宽度自然换行；可覆盖原生属性。

生成内容置于有限高度的子 Splash 内，子 ScrollYView 包含 View/Fit，按内容自然高度提供滚动；父区域承载运行反馈。Fit 是内容自然尺寸，Fill 是填父级剩余尺寸，不能在无确定高度的 Fit 父级里假定 Fill 会产生页面高度。控件写 View{width:Fill height:Fit flow:Down ...}；flow 可用 Down、Right、Overlay。子控件不放 children 数组，直接写在父控件的花括号里。控件命名写 title := Label{...}；这个名称不是脚本变量，事件中使用 ui.body.find("title") 取得真实句柄。句柄支持 set_text(text)，TextInput 支持 text()，Image 支持 load_image_from_data_async(bytes)。不要对句柄赋 on_click 属性；事件闭包在构造控件时指定。

有类型的原生成员需要实际类型构造或已有成员扩展，普通对象不能替代它。背景可写 show_bg:true draw_bg +: {color:#xf7f7f7} 或 draw_bg.color:#xf7f7f7。文字可写 draw_text +: {text_style:NavRegular{font_size:14} color:#x162e35}。padding/margin 可用数字或 Inset{top:4 right:4 bottom:4 left:4}；align 用 Align{x:0.5 y:0.5}。这对应锁定 Makepad theme_desktop_dark/button 的原生写法。

以下是实际执行过的基础表达式，仅说明语法：

```splash
fn route_detail(current){
    for route in current.routes {
        if route.id == current.viewed_route_id {
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
    return "点路线查看本次查询取得的分段与费用"
}
on_facts_changed = fn(current){ui.body.find("detail").set_text(route_detail(current))}
View{width:Fill height:Fit flow:Down spacing:8
    detail := Label{text:route_detail(facts)}
    if facts.routes.len() > 0 {
        Button{text:"查看第一条路线" on_click: || emit({action:"view_route" id:facts.routes[0].id})}
    }
}
```

on_facts_changed 是外层已定义的脚本变量。可在 View 表达式外设置 on_facts_changed = fn(facts){ui.body.find("title").set_text(facts.status)}。不会自动重建整个界面；Input 编辑内容应保留。不存在外层 on_render、self.snapshot、self.viewport 等变量。

用户动作 emit({action:"view_route" id:真实路线ID或"viewed"}) 只本地切换当前查看路线，随后 snapshot().viewed_route_id 更新；它不会自动创建详情页面。提供查看按钮时，生成稿应通过 on_facts_changed 根据实际当前路线更新自己呈现的选择或路线信息，让用户看见操作结果；不得仅发出事件而保持所有内容不变。父应用只处理本次路线查看和地图加载；不把事件转为第二条用户消息或查询续聊。地图可自由放多个命名 Image，emit({action:"map" widget:"image_name" target:真实路线ID或"viewed"或"destination" status_widget:"caption_name"})。父应用分别请求和加载真实高德静态地图；status_widget 是可选命名 Label，显示来源和加载错误。未知或缺失几何不伪造直线。

render_ui 返回本稿真实 diagnostics。错误说明实际变量、语法或原生类型问题，可以根据结果提交下一稿；应用不改写生成源码。
