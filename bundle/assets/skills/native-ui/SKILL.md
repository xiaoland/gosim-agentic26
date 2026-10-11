---
name: native-ui
description: "Navigation的render_ui嵌入环境、共享事实、区块交互、字体和地图接口，用于将Makepad/Splash源码交给当前宿主执行。"
license: Apache-2.0
---

# Navigation原生界面适配

render_ui的源码在已存在的View.on_render中执行，可以包含脚本和控件表达式；不是独立Rust应用、script_mod!宏或Canvas HTTP服务。snapshot()、emit()、NavRegular和AutoNaviMapView由Navigation提供；任务工具在父Agent中调用，不是子VM的脚本函数。

[宿主接口与实际可用示例](references/host-interface.md)说明source／blocks、事实更新、详情显示、地图事件及诊断。通用语言和布局知识分别见技能makepad-2-0-splash与技能makepad-2-0-layout。这些是资料入口，不规定读取或调用顺序。

技能资源相对路径可用read_skill的path参数读取，例如{name:"native-ui",path:"references/host-interface.md"}。原生类型及API随锁定版本变化；上游列表中的控件或Rust方法不自动成为当前子VM可调用接口。

区块源码被嵌在内容自适应Fit父body，父应用已有ScrollYView；overlay与整稿也如此。未指定区块height时，顶层ScrollYView{height:Fill}会显示为零高；此结构会收到具体渲染错误，请自行修正源码。普通内容以自然Fit布局展开；确需内部Fill滚动时显式指定区块height。不会自动改稿或追加地图模板。widget ID必须是本块实际构造的名字；隐藏或离屏控件的rect为零不是布局失败证据。

render_summary/render_explanation/render_routes/render_suggestions/render_route_detail均接收任意source；默认实际ID分别为summary、explanation、routes、suggestions、route_detail，可显式覆盖。show_block使用实际目标ID，hide_self()关闭发起块。详情默认overlay且初始隐藏，打开父容器后根内容须正常可见；原块更新保留其它块状态。

交付已评估方案及其分段、费用、耗时、限制和真实地图；不成立的候选同样有查看价值，不只给摘要。文案面向用户，使用线路/站点名称和格式化时间，不暴露内部Route/node ID或原始时间戳；本次处理结束后不用“正在处理”标题。布局与信息组织由Agent决定，不套固定模板。

文案忠实呈现navigation-data的独立判断：已知行驶/公交耗时与候车未知分开显示，不将余量补成总耗时，不把估价写成成交价；未知项存在时不给到达保证。

展示事实须按同一Route id读取当前snapshot，使用格式化价格/耗时和assessment依据。多个候选共用详情时，on_facts_changed按current.viewed_route_id更新文案和地图；使用独立详情块同样合法。守护状态也须读取snapshot().guardian及事实更新，静态“待确认/已保存/仍成立”标题会在用户点击后失真；本地确认不另请求模型修标题。守护业务边界见journey-guardian。

地图目录与绑定、每图最多4条独立paths及跨图/本地分页覆盖方式见宿主接口引用。目录未加载不是只有四条；get_route按需取得该目标目录，extend后的新几何不沿用旧目录。布局与分组由Agent决定，不追加固定地图模板。
