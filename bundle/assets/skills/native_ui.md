# Navigation 原生 Splash API

render_ui 的 source 在已经存在的 View.on_render 闭包中执行。可以包含脚本语句和原生控件表达式；这里是 Makepad Splash，不是 JavaScript。空值是 nil；函数写 fn(x){...} 或 || {...}；字符串与数字可用 + 连接。

snapshot() 返回当前真实任务事实，包括 viewport、limits、origin、destination、sources、routes、viewed_route_id、原 arrive_by。emit(object) 把用户动作写到父应用。NavRegular 是 Navigation 无衬线字体，Label、Button、ButtonFlat、TextInput 已默认使用它。

控件写 View{width:Fill height:Fit flow:Down ...}；flow 可用 Down、Right、Overlay。子控件不放 children 数组，直接写在父控件的花括号里。控件命名写 title := Label{...}；这个名称不是脚本变量，事件中使用 ui.body.find("title") 取得真实句柄。句柄支持 set_text(text)，TextInput 支持 text()，Image 支持 load_image_from_data_async(bytes)。不要对句柄赋 on_click 属性；事件闭包在构造控件时指定。

有类型的原生成员需要实际类型构造或已有成员扩展，普通对象不能替代它。背景可写 show_bg:true draw_bg +: {color:#xf7f7f7} 或 draw_bg.color:#xf7f7f7。文字可写 draw_text +: {text_style:NavRegular{font_size:14} color:#x162e35}。padding/margin 可用数字或 Inset{top:4 right:4 bottom:4 left:4}；align 用 Align{x:0.5 y:0.5}。这对应锁定 Makepad theme_desktop_dark/button 的原生写法。

以下是实际执行过的基础表达式，仅说明语法：

```splash
View{width:Fill height:Fit flow:Down spacing:8
    title := Label{text:facts.status draw_text +: {text_style:NavRegular{font_size:14}}}
    edit := TextInput{width:Fill text:"" on_return: |text| emit({action:"change_conditions" text:text})}
    Button{text:"选择地点" on_click: || emit({action:"maps_pick"})}
}
```

on_facts_changed 是外层已定义的脚本变量。可在 View 表达式外设置 on_facts_changed = fn(facts){ui.body.find("title").set_text(facts.status)}。不会自动重建整个界面；Input 编辑内容应保留。不存在外层 on_render、self.snapshot、self.viewport 等变量。

用户动作 emit({action:"view_route" id:真实路线ID或"viewed"}) 只本地查看；confirm_route 同字段表达用户明确确认；change_conditions 带 text；continue；refresh；其他事件也会进入同一个 Agent 会话。地图可自由放多个命名 Image，emit({action:"map" widget:"image_name" target:真实路线ID或"viewed"或"destination" status_widget:"caption_name"})。父应用分别请求和加载真实高德静态地图；status_widget 是可选命名 Label，显示来源和加载错误。未知或缺失几何不伪造直线。

render_ui 返回本稿真实 diagnostics。错误说明实际变量、语法或原生类型问题，可以根据结果提交下一稿；应用不改写生成源码。
