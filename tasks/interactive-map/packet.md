# Navigation 交互地图

状态：2026-10-05，接续0.8.3静态图片地图；已授权实现交互地图，已选AutoNaviMapView官方静态图视口路径，0.9.0原生和应用实现、真实地图交互验收及最终封装完成，沿授权本地提交，用户实际查询出现缺定位／地图／内容／详情，正常harness交付未通过；接续[查询交付任务](../query-delivery/packet.md)，本包原语与直接挂载示例证据仍有效。

## 目标与授权

用户确认现有地图仅图片后授权：“是的，开始接入 MapView 或者我们自己实现一个 AutoNaviMapView”。完成必要原生／应用／技能／配置／验证与文档修改；不是只提交调研。能力应让用户拖动、缩放并查看真实候选路线，Agent得到通用地图原语，不能变成固定路线详情组件。优先复用已有地图机制；底图、中国坐标与实际可用性决定选择。

固定输入框和查询／终止按钮、一个M3工具循环、无持久化与无澄清保持。地图手势／查看不重新请求模型，不设置图数、控件树或人工输出限制。使用官方可公开配置的服务，不将猜测的瓦片URL称为正式接口；地图底图与高德GCJ02路线必须一致，缺段不补直线。仅明确需要额外用户凭据或服务资格时提出具体缺口。

## 当前事实与责任

0.8.3本地提交7d14dfc，用户验证图片已显示。地图桥通过命名Image及map事件请求高德静态图，完整真实几何只在共享端点合并；HTTP200错误JSON会反馈，缓存再次打开会显示。历史证据归tasks/agent-generated-ui/packet.md，不等于交互地图实现。

锁定Makepad已有MapView，可pan/zoom与路线叠加；默认本地vector MBTiles，非高德图片或已配置中国底图。当前宿主编译maps，MapView类型存在不证明中国导航可用；路线数据绑定、坐标与服务需要实证。完整AppCard助手本轮不接入。

稳定native_error_api负责控件与工具链必要修改、官方接口调查及隔离判别，先给事实和推荐；ui_finish负责应用／skills／必要smoke及Android交互验证，与native协商契约；根负责advisor取舍、版本、长期说明、最终证据采用及本地提交。不得回退其它工作，隔离实例只关闭自有，不点关用户实例。按已有授权本地提交，不推送、签名或发布。

## 计划与完成依据

先用现有MapView或最小适配做一个真实中国路线pan/zoom实验，判别是否需要AutoNaviMapView。advisor依据实验与官方服务接口选择；先可用即停止广泛调查，不为未来导航引入平台。选择后完成原语、地图事件绑定、可运行skill示例和实际触控处理。Android模式验收真实底图与路线位置、平移缩放、候选切换、与外层滚动配合、返回列表；失败保留具体原因。不把缩放单张图片称为交互地图，不冒称Android真机。

原始服务结果／地点／请求URL与日志留build忽略目录，安全报告记录来源类别和摘要。最终必要包检查、一次构建与实际挂载一致后结束；不做无目的重复模型抽样或全量回归。当前无待用户决定事项。

## 已选实现方向

MapView没有现成高德raster source；直接采用还需中国vector底图和GCJ/WGS处理。采用AutoNaviMapView维护GCJ02 Mercator相机，拖动即时移动已载纹理，手势结束／缩放后由原应用高德代理请求该视口新图，完整同源paths和markers保持。不是单图片放大，视口外新内容由服务返回；这是有请求延迟的交互raster地图，非连续瓦片或导航SDK。

advisor采用此方向，关键是初帧也明确location／zoom／size（scale=1），不用未知auto-fit相机；原生fit_bounds按真实几何确定初camera。实际绘制矩形、请求尺寸与比例必须一致。每图独立camera／request，现HTTP代际及原生decodekey要贯穿到纹理安装，不添一般安全框架。用真实标注屏幕位移判别地理与像素一致；用户要求的无限制生成与实际供应商尺寸范围分开。

## 实施恢复点

原生实现复用Image纹理与事件，导出AutoNaviMapView及fit_bounds／zoom_by／load_map_image／camera回调；相机改变使旧decodekey失效，切目标清纹理，同目标手势保留空间预览。UI将map slot绑定interactive与原生camera回调，显式camera请求，skill示例改为可选择的交互原语，包含缩放与全路线按钮；没有新增模型循环。

首次隔离运行因ImageFit未在别名scope暴露而失败，修正为实际导出引用后编译、独立patch重放与source verify通过。随后发现共用参数读取在单参set_visible调用时读多参越界，native owner已按真实方法分支修复；失败实例已关闭，未用M3重试或重跑业务。此处是中间失败记录，当前实际交互完成依据见下。native负责唯一相机／旧响应probe，UI负责真实高德图像位移／zoom／外scroll／返回，避免重复。

真实地图首次验收发现两项实际问题：旧纹理UV越界时边缘条带，原生256像素Mercator基准与高德scale1图片不符。拖动预览marker确移动220px，释放图却偏移；用已有图片与公开端点按512基准预测尖端A(355.70,177.61)、B(33.33,136.21)，实际(356,178)、(33,136)吻合。native已统一512投影及AutoNavi专用越界背景；不修改普通Image、不追加业务／M3。这个实测纠正先前未经验证的256假设，不把接口参数文档当投影证明。

原生唯一probe已通过嵌套、camera／zoom、旧response拒绝／current接受和普通Image set_visible，根读map-native-probe/result-safe.json并查看after.png。这证明原生接口和纹理基本链路，不替代当前真实地图几何修复验收。

## 完成依据

根已读取build/research/interactive-map/result-safe.json和build/smoke/navigation-harness-se83nuez/report.json，并查看final-zoom.png。Android412×892实际拖动220px：marker约286→66，释放新PNG仍66且新区域出现；zoom9→10获得新细节，两条真实路线图不同；地图外详情滚动、返回列表位置、同目标相机保留通过，原生日志无错误。使用当前skill原例与明确公开demo端点的真实GCJ02几何，M3请求0，不冒称自主规划或GPS实测。原生支持单指／双击及按钮缩放，双指捏合未实现；有官方请求延迟和配额错误，非连续瓦片。

首fit出现过10021配额错误，定位同批camera延迟任务重复读取可变最新request，现捕获各次编号只派发仍当前的请求，不添加ratecap或隐藏重试。最终main 6cb8fd06ce8f34aa7f64413b7aea1f7b600552331bfe73c1baf35a8b963c86ac，native_ui 9ed764b604134d33714561ed0433999a056e3eab6c36c8849f25e99bf473bd16。实际交互之后只增加旧目标fit拒绝；同版四项原生回归覆盖无损几何、错误不ready、旧fit不派发、同批camera只派当前，命令python3 tools/smoke.py --map-details。实例均自有且已关闭，未重跑全量验收。原生接口和patch证据归map-native-contract-safe.json；最终一次check／agent-build／agent-doctor通过，根已读取final-package/result-safe.json与overlay-replay-safe.json，stage／嵌入pack／实际挂载10文件字节一致。source aggregate 3a0660ae7c67aa7a91323455cfe61a4d3672f818e0aba2ef22d075ccea920242，runtime BLAKE3 33852ffc06581e7f44e38826b143087c3eb287996bc7996899568d9584ed5cc4，binary SHA256 f34130a351d7e3c46971ded5c942a655692d3fc86c2f1b3b403ef5bc35a34abe；解码包7,248,484 bytes。原定位／Maps／字体lock和5个patch摘要未变，两个完整新UI patch分别在独立index重放通过；host tree f3974b955cafbf3ed779e5296e9052946a10d4c7，Makepad 534b7e5732e63d35bedffc596b8386c78d572ca1。封装无服务／M3／行为复跑，自有实例关闭；根本地提交，不推送。
