# 基础界面与交互优化

状态：2026-10-12，固定外壳优化与七种通用样式已实现，7 项原生手机交互通过。第38轮真实 M3 生成整卡候选，实际查看 S4831 详情和接驳地图、保存均通过；第40轮仅恢复修复版本读取同一快照，卡片→详情→地图→返回／重开通过，0新增模型或规划调用。root已查看实际详情、地图与重开截图，账本及原生成源码未变；完整版本边界与保留诊断见[铁路任务](../rail-integration/packet.md)。以下旧版本证据只证明各自记录范围，不表示完整 Material 合规或 Android 真机验证。

## 目标与授权

用户要求：“改进一下基本的UI/UX，有点丑和差，分析一下或者查阅vercel或者别的设计指南”。授权分析和必要实现，沿用提交推送及原生验证授权。保留sidebar出行列表/index详情和Agent自由DSL；本轮不模板化路线、不改写旧生成稿、不新增模型提示词或依赖。

root整合设计判断、文档和提交；guardian_design给出层级/状态建议；guardian_impl拥有bundle生产源码；guardian_verify负责受影响交互与真实截图。实例已全部释放，无用户待决定事项。

## 分析与已交付

原固定壳同时显示完整需求标题、同文输入和长历史声明，结果前占约260像素；守护说明和操作在滚动区外挤压路线。侧栏缺少遮罩，当前项只用圆点表示，按钮尺寸与权重近似。

现以紧凑应用栏显示当前目的地；历史页默认收起输入，历史时间与调整入口同一行，原需求可展开且收起不丢草稿，提交新建出行的语义明确。多行回车换行、Cmd/Ctrl+Enter提交；运行时回车不能误停，停止入口始终可达。状态明确显示正在规划/规划已停止，不依赖空串清除旧控件文字。

守护区常显期限、余额、核验状态及时间，完整依据与进度放入可滚动展开区。费用表单前置，实际软键盘打开时字段与确认可见。错误保持直接显示，目标结束/删除归次级管理。删除确认绑定具体对象，明确删目标保留出行、删整条出行连同历史删除，切换清除旧确认。

侧栏增加可点关闭的遮罩，底层不响应；用背景与文字标明选中，显示实际目的地和日期，完整请求未更改。局部sans字体、统一间距和字号、44像素以上主要触控区域、低饱和青绿主操作建立层级。没有修改其它应用主题。详情覆盖层使用稳定结果锚点，不依赖可收起的输入框。

依据为[Vercel Web Interface Guidelines](https://vercel.com/design/guidelines)的触控、焦点、状态、删除确认和内容层级原则，以及[Android布局建议](https://developer.android.com/design/ui/mobile/guides/layout-and-content/layout-and-nav-patterns)。[Android触控建议](https://support.google.com/accessibility/android/answer/7101858)提供48dp参考；本次实际主要控件44像素满足Vercel移动底线，不冒称Makepad逻辑像素等于真机dp。来源于2026-10-11读取，DOM/React/CSS条目没有机械套用。

## 完成证据

最终 main SHA256 45be0ef62ec6135c75616d67fd7e9dfb0a14ac2154f422b3a0a296a8c8d8c62c；bundle聚合 061e27e5162f06cc529e2267829e10bfccfbd07eab9f75f6c2d6594d3858a4d1。make check、make agent-build、make agent-doctor及git diff检查通过。

- 前图和隔离业务seed：build/research/ui-ux-foundation/before/manifest-safe.json；未复制凭据或账本。
- 25项实际交互通过：build/smoke/navigation-harness-47z4y5f6/report.json。覆盖历史状态、展开收起、草稿保留、抽屉遮罩及关闭、详情地图与返回、等待桩查询/停止、费用键盘/保存、两类删除取消/确认。已查看最终12张截图；root也查看历史首屏、侧栏、费用键盘和删除目标页。
- c16源码运行边界5项通过（最终源码只增加原版宿主分支判断）：build/smoke/navigation-harness-kgfbvsad/report.json。正在规划和规划已停止文字正确，停止可达，回车不误停。未重复整套业务回归。
- 统一证据：build/research/ui-ux-foundation/verification-safe.json；真实地图纹理可见，无渲染、UTF8或执行预算错误。本轮0次真实M3请求，内部测试dispatch来自明确等待桩。复用已有真实路线和历史生成稿，没有假称新增在线规划通过。

官方无补丁宿主首屏回归通过：build/smoke/stock-startup-dpnj98r3/report.json，缺能力说明可见、按钮禁用、Cmd+Enter不绕过能力门，无脚本错误。此前9mz_ez5m旧按钮名测试失败与y3_5g1ol原版缺控件寻址失败均保留；测试适配新控件和多行提交，生产显式状态同步仅在配套能力可用时调用。此检查使用390×844手机视口，不是Android模式或完整功能验收。

普通回放入口为 python3 tools/smoke.py --ux-shell（NAV_TRIP_REPLAY_STATE指向私有业务seed）；同一入口设置 NAV_UX_RUNNING_ONLY=1 只验证运行文案与停止边界。历史回放测试适配新的目的地列表标题，测试材料保留在忽略目录。

## 修正与边界

实际检查发现并修复动态on_render条件的空栈、历史文字缺失、列表metadata裁切、输入收起后按钮残留、费用表单被键盘遮挡，以及运行/停止状态文字残留。采用常驻控件显式同步与现有布局处理，不增加宿主覆盖。

验收为macOS arm64宿主Android样式，未做Android真机、读屏或全部主题/桌面尺寸适配。本轮改进固定外壳，已有Agent生成内容的样式保留；没有重新进行路线优化算法或容量压力验证，也未制作新视频。

## 下一轮：可组合的候选卡片与事实绑定（提议）

用户在继续铁路闭环时提出候选应采用 rich 卡片并带地图缩略图，可考虑 minimal Material 2/3；没有要求立即建设完整组件库。guardian_design 本轮只读调查，未改 main、bundle 或启动实例。铁路地图与日志修复继续由 rail_model 负责，宿主升级、真实日历笔记由各自 owner 推进。

已查看 round30 的实际列表截图（build/research/rail-integration/e2e/round30/round30-return-list.png）：候选目前由较长正文和单独详情按钮组成，阅读时难快速比较时间与费用。源码中父外壳有 NavPrimary/NavSecondary/NavMeta，但 generated_context 仅给子VM提供字体与通用 Label/Button/TextInput 默认值，尚未共享一组卡片样式。现有 snapshot 已有 Route 格式化价格、耗时、到达时间、分段与不确定性；native-ui 已要求按同一 Route ID 读取，故时刻误写不是缺少 Material 外观能解决的问题。

建议先采用 Material 3 的颜色角色、文字层级与 surface 思路，在当前 Splash 上提供应用局部的少量可覆盖样式：surface/card 容器、title/body/meta 文本、主次操作与间距/圆角常量。卡片只承载任意子内容，不读取 Route、不排序候选、不自动开详情。首轮不加入全套 M2/M3 双版本、动态配色算法、导航框架、阴影等级、弹簧/共享元素动效或主题切换系统；现有按下/焦点/禁用反馈保留。建议初始视觉尺度为标题20–22、正文14–16、辅助12–13，间距4/8/12/16/24，卡片圆角12–16；这是待原生手机截图检验的应用提案，不声称Makepad逻辑像素等于Android dp/sp。

事实绑定优先于新增外观：Agent仍决定构图、解释、比较与交互，但卡片内班次、发到日期时间、门到门总耗时、费用小计/完整性和未知项应直接取同一 Route 的确定性展示字段，并在 on_facts_changed 中按该ID更新；铁路区间时长与含候车的门到门耗时必须分开。缺少便捷展示字段时，在现有 snapshot 投影补齐格式化值，不让模型抄工具文本或自行换算；不新增预制 RouteCard 或另一份可写路线状态。历史恢复使用当时事实，不能用当前时间重算静态标签。仅增加技能文字不能保证生成稿遵守；必要验收要对实际生成控件文本与绑定Route做核对。

缩略图可优先复用已存在 Image + map事件（interactive:false），target 与文字绑定相同 Route ID；不由模型传坐标/绘制想象线路。列表缩略图不接管滚动/缩放，点击仍由Agent自己的动作打开详情。每图最多4条 paths 是实际供应商限制；超出时可明确选取局部概览并标出范围，完整详情继续覆盖全部可用几何，铁路缺几何不能补直线假装实测。图片大小、摆位与候选数量不固定成模板，也不新增自动截前四条或虚构缩略图。此次未运行新缩略图组合，现成接口可复用与组合后体验已验收须分开。

官方依据：[Android Material 3](https://developer.android.com/develop/ui/compose/designsystems/material3)将颜色、字体与形状作为主题，并说明产品无需使用全部15种字体；[Card](https://developer.android.com/develop/ui/compose/components/card)以单个主题内容容器和可组合子内容区分卡片与整个页面。M3主站页面本次只返回JavaScript提示，因此使用Google官方Android实现说明核实原则。[Makepad官方仓库](https://github.com/makepad/makepad)确认其Rust运行时、Splash及widgets体系；当前锁定源码可见View、ButtonFlat、Image、主题模块，未找到可直接导入的官方Material组件包。Compose API不能直接当作Splash API；本次建议是局部样式与现有控件组合，不引入Compose依赖，也不宣称完整Material合规。

接续只需先做一个真实铁路候选与一个非铁路候选的Agent自由布局，检查手机宽度下的文字层级、长站名、未知费用、静态地图滚动、详情返回及同Route事实更新/历史恢复。用round30真实记录核对班次与门到门耗时，不因视觉更好而降低事实要求。确认这组原语可改善实际稿件后再判断是否值得命名成库；本轮未实现或新增验证。

滚动合同待实际对照后决定：round30 的显式height使父body Fill，自然Fit详情的长正文可能挤掉地图；全局改body Fit又会破坏既有内部ScrollYView Fill稿件。建议一个显式内容尺寸选项，区分 natural（外视口限高、body Fit、外层滚动）与 viewport（body Fill、Agent管理内部布局/滚动），未指定时保留旧稿规则。新长详情示例选择natural；不按DSL文本猜模式、不静默重解释历史源码。这是两种原生布局能力的合同，不是路线模板或新增导航框架。rail_model正在隔离复用原事实/原DSL对照；本建议没有宣称该对照已通过。

## 通用视觉原语实施与原生验收（2026-10-12）

用户本轮授权最小 Material 3 方向的通用视觉原语和 rich 候选展示，输入之外仍由 Agent 自主组织 DSL，不预制 RouteCard、固定候选模板或保底稿。main 与 native-ui 契约由 rail_model 整合；本地原语和展示合同检查由 material_primitives 负责，真实铁路闭环仍归 rail_e2e。宿主 RC6 迁移期间不并行改共享 stage 或启动原生实例。

现有 generated_context 是子 VM 的统一定义入口，没有已维护的外部源码模块机制。选择在那里一次内联 NavSurface、NavCard、NavTitle、NavBody、NavMeta、NavAction 与 NavSecondaryAction；不为七种样式新增加载框架或未消费的 bundle asset。两个容器明确 Fill/Fit 并允许任意子内容；字体复用应用局部 NavRegular，标题／正文／辅助文字为 22／16／13 逻辑像素，主要操作高 48 逻辑像素，保留按下、焦点、禁用状态。没有路线读取、排序或选择逻辑，不宣称完整 Material 合规。

原语已由 rail_model 内联 generated_context，当前生产 main SHA256 为 5e61ab4f3291ad656700c51ea394c5fdc160d673d130f02b8fbd0ebca61d4f49；忽略目录的 material.splash 只是源稿，不是运行加载入口。正式 RC6 binary SHA256 为 733cbcb0104599b6244b6da01ff7f1c977b9a4117800cef5ced1628ec9826e1a。运行 `python3 tools/smoke.py --material-primitives`，7 项实际检查通过：自然高度与长中文换行、手机宽度与 48 逻辑像素操作、主操作点击、禁用动作不执行、布局与子内容可覆盖、卡片标题坐标点击、卡片内边距坐标点击。最终证据为 build/smoke/navigation-harness-tzw7zru2/report.json，已查看 material-phone.png、material-card-pressed.png 与 material-actions.png，文字与浅色背景对比清楚，按下背景变色可辨。模型和交通供应商调用均为零，无原生错误；所有本组实例已停止。

实际拒绝了未经验证的 Overlay 组合：自然 Fit 卡内的 Fill 按钮零高度，不能充当整卡点击区。可运行组合使用 NavCard 的 on_item_tap、手形光标、已有次操作背景和两个简短 hover/down 动画；一个 Fill/Fit 子 View 承载全部自由内容与内边距，因此文字和留白均可触控。此组合为可选通用用法，未增加新组件或路线模板，短说明交 native-ui owner 整合。早期失败实例保留于 build/smoke，没有把其截图算作最终通过证据。

合成展示不证明模型自由生成、真实 Route 标签绑定或地图缩略图，这些仍需真实候选验收。验收条件为 macOS arm64 宿主 Android 样式，不是 Android 真机；未检查键盘操作、读屏、深色主题或完整 Material 合规。
