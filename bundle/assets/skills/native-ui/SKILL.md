---
name: native-ui
description: "Navigation的render_ui嵌入环境、共享事实、区块交互、字体和地图接口，用于将Makepad/Splash源码交给当前宿主执行。"
license: Apache-2.0
---

# Navigation原生界面适配

render_ui的源码在已存在的View.on_render中执行，可以包含脚本和控件表达式；不是独立Rust应用、script_mod!宏或Canvas HTTP服务。snapshot()、emit()、NavRegular和AutoNaviMapView由Navigation提供；任务工具在父Agent中调用，不是子VM的脚本函数。

[宿主接口与实际可用示例](references/host-interface.md)说明source／blocks、事实更新、详情显示、地图事件及诊断。通用语言和布局知识分别见技能makepad-2-0-splash与技能makepad-2-0-layout。这些是资料入口，不规定读取或调用顺序。

技能资源相对路径可用read_skill的path参数读取，例如{name:"native-ui",path:"references/host-interface.md"}。原生类型及API随锁定版本变化；上游列表中的控件或Rust方法不自动成为当前子VM可调用接口。
