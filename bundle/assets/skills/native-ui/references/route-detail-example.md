# 路线列表、详情与地图分页示例

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

