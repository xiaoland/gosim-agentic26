---
name: makepad-2-0-splash
description: "Makepad 2.0 Splash语法：draw_bg类型属性覆盖、字符串与控件闭合、if/else表达式、错误传播后缀及运行时求值，用于编写或修正原生界面源码。"
license: MIT
---

# makepad-2-0-splash

复用固定版本的Makepad社区技能。Navigation的render_ui嵌入环境和项目接口见技能native-ui；上游的Rust宿主、script_mod!、Canvas服务和热重载示例有各自环境，不是Navigation工具或子VM中隐含存在的API。

按问题读取下列资料；上游文中提及的完整宿主源码路径不随应用包提供，本目录的随包资源以下列链接为准。

- [通用语言参考](references/splash-language-reference.md)：类型属性覆盖、字符串与控件表达式、条件和循环。
- [上游技能正文](UPSTREAM.md)
- [splash-scripting-patterns.md](references/splash-scripting-patterns.md)
- [canvas-splash-patterns.md](references/canvas-splash-patterns.md)
