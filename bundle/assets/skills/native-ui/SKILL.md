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

生成稿若展示守护状态，须从snapshot().guardian.current_check/goal/proposal与on_facts_changed读取状态变化。静态“待确认/已保存/仍成立”标题会在用户点击后失真；确认事件不启动另一模型请求替你擦标题。current_check是本轮判定，last_check是历史核验。已确认旧方案的公开id/geometry_ref为saved_goal_route，original_route_id仅溯源，不是本轮可调用Route。
