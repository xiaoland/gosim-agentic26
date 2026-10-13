---
name: native-ui
description: "Navigation的render_ui嵌入环境、手机候选比较、共享事实、当前facts绑定、区块尺寸、滚动、交互、字体和地图接口，用于将Makepad/Splash源码交给当前宿主执行。"
license: Apache-2.0
---

# Navigation原生界面适配

render源码在已存在的View.on_render中执行，接受Makepad/Splash脚本与控件表达式。不是XML/HTML、独立Rust应用、script_mod!宏或Canvas HTTP服务。snapshot()、emit()、NavRegular和AutoNaviMapView由Navigation提供；任务工具在父Agent调用，不是子VM函数。通用样式见技能material-ui；Nav兼容名称只提供样式，不选择Route。原生类型随锁定版本变化，上游控件或Rust方法不自动成为子VM接口。

手机列表先比较已评估候选的交通组合、费用覆盖、到达范围与关键unknown，再通过本地操作查看同一Route的完整分段、来源和真实地图；不成立候选也有查看价值。文案使用线路/站点名称与格式化时间，不暴露内部ID或原始时间戳，处理结束后不用“正在处理”标题。布局与信息组织由Agent决定。

展示按同一Route id绑定当前snapshot的price_label、duration_label、arrival_label及assessment依据，保留unknown与原因。不将余量补成总耗时，不把估价写成成交价；未知项存在时不给到达保证。铁路区间耗时不能代替整程耗时，已查段小计不能写成门到门总价。优先使用带日期、时区的真实时间标签；字段、范围与事实更新方式见宿主接口，不从工具字段猜造snapshot接口。守护展示同样绑定当前facts，业务规则见journey-guardian；事实语义见navigation-data。

新稿content_sizing默认natural，根及嵌套内容用width:Fill height:Fit随内容展开，由父容器滚动；height只约束外视口。源码自行管理有限ScrollYView时显式用viewport。短并列标签用width:Fit，长描述允许换行。当前宿主Android模式中，Flow.Right{wrap:true}内连续放置width:Fill height:Fit的Label会让后续标签以零宽度排版，造成大空白和文字不可见；多行卡片内容用flow:Down，长描述保留width:Fill，不将整段长文改成width:Fit。show_block使用实际已安装目标id，hide_self()关闭发起块；新详情overlay初始隐藏，根内容正常可见，更新保留显示状态。rendered只确认首次执行与事实绑定，空diagnostics或success不证明手机内容可见、可点或交付完成。

按需资料直接由read_skill读取，path相对技能根，例如{name:"native-ui",path:"references/host-interface.md"}：

- [宿主接口](references/host-interface.md)：编写或修正区块时查询source／blocks、尺寸、当前snapshot字段与更新、显示切换、字体和诊断契约。
- [地图接口](references/map-interface.md)：使用AutoNaviMapView时查询首次绑定、六参相机回调、真实路径目录、每图四条限制、分图覆盖与加载反馈。
- [路线详情示例](references/route-detail-example.md)：需要列表打开详情、同Route动态绑定及真实地图分页时读取完整Splash示例；这是可选组合，不是固定模板。

通用语言、布局、控件和排错资料分别见makepad-2-0-splash、makepad-2-0-layout、makepad-2-0-widgets、makepad-2-0-troubleshooting。资料入口不规定读取或调用顺序；地图目录未知时不能假定只有四条，选图与真实范围见地图接口。
