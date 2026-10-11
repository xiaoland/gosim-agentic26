# 基础界面与交互优化

状态：2026-10-11，基于 a57ab66（0.16.0）完成固定外壳优化，未改业务或存储schema。

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
