# Navigation 地图绑定与路径目录

map 事件建立路线目标绑定并初始化相机；map_camera 回调使用这个已存在的绑定请求后续视口，不能替代首次 map 事件。路线详情示例的普通事实更新只刷新文案，不重复绑定地图；切换路线重置页码并绑定新路线，翻页绑定所选真实折线。再次打开同一路线详情保留页码、地图相机和列表位置。多张地图或其它分页布局同样可用，示例不规定页面结构。单文档 source 也可以用自己命名的 View.set_visible 切换内页；此时隐藏与打开都由同一文档管理，这是另一种局部交互方式，不要把内页隐藏复制到父已管理隐藏的独立详情区块根。

地图可自由放多个命名 AutoNaviMapView。这是原生GCJ-02摄像视口，拖动／缩放后通过on_camera_changed回调请求该新视口的高德底图与同源真实路线，并非只缩放旧图。构造时应给有限高度，并将回调的六个实参用map_camera事件传给父应用，六参依次为longitude、latitude、zoom、width、height、request；事件字段对应center_lon、center_lat、zoom、width、height、request；按需示例见references/route-detail-example.md。回调request由控件产生，应用和模型不另造编号。手势在地图区域内改变相机；区域外的详情滚动由页面自己的ScrollYView处理。底图按官方静态图接口更新，有网络延迟，不是连续瓦片加载。

emit({action:"map" widget:"image_name" target:真实路线ID或"viewed"或"destination" status_widget:"caption_name" interactive:true})。父应用绑定真实路线、初始化全路线视口，再分别请求和加载真实高德视口图片；status_widget 是可选命名 Label，显示来源和加载错误。target 用当前实际路线ID可固定本次详情目标；用 "viewed" 会随父查看状态更新，"destination" 仅显示实际目的地。命名地图应已构造且具有限高度，先显示详情页再发事件，父才能向实际实例加载字节。切换目标显示加载状态，新路线重新匹配全路线视口；同一目标再次打开保留原生相机和当前run图片。来源与加载反馈由 status_widget 接收。旧Image静态图接口仍可用，省略interactive:true即可；它只有图片，不具备地图拖动缩放。未知或缺失几何不伪造直线。

高德静态地图接口每次最多接收 **4 条独立折线（paths）**，这是供应商接口能力，不是应用自动分组规则。`snapshot().routes`／`get_route({id})` 的每条路线都有 `map_paths` 目录：`index` 是最终相接合并后的折线索引，`start`／`end` 是真实几何端点，`point_count` 是点数。目录完整保留全部折线；它与公交 `segments` 下标不是同一概念。`map_metadata` 给出 `catalog_status`（`not_loaded`／`ready`）、`path_count`（未读取时为 nil，读取后为实际数量）和 `max_paths_per_image:4`。`map_paths` 为 nil 表示目录尚未读取，不表示没有几何，也不表示折线数不超过四条。目录对应当前 Route 的实际几何：extend 返回的新路线不能沿用旧路线目录；仅替换报价而几何不变的派生路线可复用同源目录。目录未知时，`get_route({id})` 可取得该路线目录；实际地图取得几何后，snapshot 也会更新目录。普通地图可不传索引来显示四条以内的完整路线；数量超过四条会明确拒绝本幅请求并提供所有可用索引，不会静默截取前四条。未知数量不等于已满足供应商的四条上限。

地图事件可选 `path_indices`，从该目录选择完整折线，例如 `emit({action:"map",widget:"part_map",target:id,path_indices:[0,1,2],status_widget:"part_note",interactive:true})`。未提供时选择完整路线，仍受每图四条上限；不会自动截前四条、拆图或跨缺口连接。多于四条时，可以根据目录分步嵌入多张独立命名地图，每张选择至多四条，张数、分组、打开步骤和布局由生成稿决定。展示完整路线时，各图的索引选择合起来应覆盖全部实际折线，缺失几何仍说明真实缺失。索引随当前路线目录变化，不猜测索引，也不把某些分段称作完整路线。

每个命名 AutoNaviMapView 保留自己的相机和加载状态，`on_camera_changed` 仍使用该控件名发出六参 `map_camera` 事件。选择了 path_indices 的图会 fit 所选几何范围；图上的 A/B 是本图所选几何首末点，状态说明“本图分段端点，非全行程起终点”。原行程起终点、完整费用与限制仍在路线事实中。`status_widget` 可显示分图范围、来源、加载或供应商错误。

地图 widget/status_widget 名字局限在发事件的区块内，不同块可以使用相同名字。map、map_camera、map_fit 事件仍按上文使用；替换一个块仅撤掉它的地图绑定，其它块相机保留。跨块先显示详情块，再以 view_route 更新当前查看路线；详情块可在 on_facts_changed 中更新自己的内容并发 map 事件，或直接绑定事实中的路线 ID。没有自动创建业务详情页面。

地图事件 target 也可直接引用 query_route 返回的 geometry_ref（polyline_…）；父应用按同一候选的真实几何加载，不由模型传折线坐标。原路线 id、viewed 和 path_indices 仍可用；新查询使上一轮引用失效。

静态底图传输由父应用处理，不需要生成稿复制polyline。父应用保留原始完整几何及目录，在当前相机下分批派生约一像素误差内的显示折线，保留各路径端点与独立身份；放大或缩小时按新相机重新计算，不能将概览点集作为新的供应商路线。中心、标记及显示点遵从六位小数接口精度。已派发的服务或网络失败仍显示真实地图错误，不自动重试，也不把图片未返回标成ready。

地图目录的map_metadata.selection_groups提供完整覆盖全部路径的可选path_indices分组，每组最多4条，selection_scope仅代表所选真实折线，缺口不补线。它不会自动选组或安装地图。只有已知目录不超过4条时map事件可省略path_indices；目录未知时可读取Route或等当前facts目录后明确选择分图。render回执current_blocks的map_bindings记录实际state／status／http_requested：未绑定、等待、失败与ready不能互相替代，也不证明像素可见。

