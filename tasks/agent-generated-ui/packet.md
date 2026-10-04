# Agent 动态生成 Navigation 界面

状态：2026-10-04，实现、正式宿主交互与应用包封装已完成，等待用户体验验收。

## 目标与授权

用户要求输入框和单一查询／终止按钮之外的内容由 Agent 动态生成，可提供地图等原语。用户明确授权：“好的，按这个方向开始修改。”并要求 Navigation 使用正常无衬线字体，其它应用保持原样。范围包括必要源码、资源、验证与文档；不安装系统字体、不改变其它应用，不扩大到任意代码执行或新的服务接入。既有本地提交授权保留，本次不推送、签名、发布或赛事提交。

主 Agent 协调；GPT-6.1 Sol medium 的 `ui_finish` 负责应用与行为验证，`host_finish` 负责宿主包装、锁定与最终包检查。字体资源负责人已完成。advisor 处理生成协议与执行边界的实质判断。源码职责互不覆盖，负责人继续完成局部失败，不将例行技术选择交给用户。

## 当前实现与决定

固定外壳仅输入和查询／终止按钮。M3 提交浅层 `sections(flow,title,items)`，选择当前原语目录中的文字、事实、地点、路线、条件和操作，决定组合与顺序。可选根级 `map(target,section)` 指定真实目标和原分区下标；当前组件只承载一张地图，因此目录没有地图叶子。应用转换为 Makepad 原生组件，不 eval 模型代码，也不恢复旧固定整页。

转换保留必要层级：column 直接 group 包含标题与叶子；无标题 row 直接 row；有标题 row 保留标题在上所需的层级。按实际组件计数，总计 36、同组 12 是展示预算，不是已测出的运行时性能上限。校验当前对象、动作及结构；不合规时最多一次完整反馈，列出所有独立违规，再失败报告展示错误并保留业务结果和仍适用视图，不截断、猜测修复或追加采样。

展示与业务循环独立，不消耗业务步数或重置原截止。任务标识和内部 revision 拒绝旧响应；终止覆盖展示等待。切卡、展开、地图加载和编辑本地响应，确认按实际对象及原截止重新核验。工具派发与展示接收使用单次新 timer 入口，避免同一 callback 重复审计写入耗尽脚本预算。

Navigation 专用字体基于思源黑体 CN 2.005，去 hinting、保留全部字形与映射并依 OFL 更名。来源、完整许可和复现归 `bundle/assets/fonts/README.md` 与 `OFL.txt`。实际锁定 Makepad 字体探针确认中文、英文、数字、输入与按钮使用无衬线，同窗原主题仍文楷；其它应用、主题与文楷资源摘要未改变。未安装系统字体。

Hub 原预检会将字体许可的来源链接视作运行时请求。独立 font-document gate 覆盖仅豁免附带真实 OTF／TTF 的指定纯文本许可与说明；脚本、HTML、图片、CSS 和远程资源仍按原规则校验。原定位与 Maps 覆盖不变。包装器固定官方 bundle identity，防止共享编译目录遗留其它包的 Info.plist；不改变系统权限。具体版本归锁文件与工具链说明。

## 当前证据与局限

最终候选 `main.splash` SHA-256 前缀 `49994976`。94 项业务、58 项定位、7 项派发和 47 项 UX 回归对应产品源码 `b0d6f6de` 前缀；最终候选仅增加三处显式 `map:null` 拒绝检查，撤销这三处可精确复现前版摘要，因此不重复无关回归。最终同版新增 15 项边界覆盖准确计数、36 恰好接受、结构开销、非法地图目标／位置、null 与旧地图叶子拒绝。固定三次 proposal＋一次 asking，每过程最多一次完整反馈，批中不改源码、不补抽样：两次 proposal 首次有效；第三次 42 节点经反馈有效；asking 引用不存在的 viewed 地图，经反馈省略地图有效。四过程有效，不声称统计可靠率或首次全部成功。全部输出与调用耗时归 `build/research/agent-generated-ui/sections-map-fixed-safe.json`。

字体证据归 `build/font-probe/report.md`、`formal-font.png`、`unchanged-host-fonts.json`。主 Agent 已查看字体探针，所有探针窗口已关闭。正式 gate 四项检查、合法字体 fixture 的官方完整 harness 通过，证据归 `build/research/agent-generated-ui/host-font-precheck/`；包装身份检查归该目录 `identity-and-gate-safe.json`。

最终实际服务联调使用显式模拟起点，经真实 Maps 搜索选择、转换与城市核实、高德公交及驾车取得 7 条新候选；冻结批次有效 M3 布局以当前有效引用接收，没有重映射候选或追加采样。地图随切卡从打车切到公交，展开／收起、地点与条件编辑实际通过，未新增模型调用或改变收到指令时间和原截止。全部候选不可确认；实际布局未选确认操作，确认、来源失效、停止／迟到与二次失败保业务采用行为未变化的回归记录；最终差异由同版 15 项检查覆盖。证据入口为 `build/research/agent-generated-ui/report-safe.json`，回归 `navigation-q2bdxozj/report.json`，最终边界 `navigation-_jx3fjkc/report.json`。

这是实际服务 UI 联调，不冒称新一轮完整自主业务任务或真实定位成功。正式最终源码已实际显示，主 Agent 与 UI 负责人均查看 `bundle/screenshots/01-main.png`，其来源与负例标注保留。横排长按钮有文字裁切，完整内容与操作可原生滚动到；布局质量仍需用户体验反馈。

`make check` 的完整官方 harness、`make agent-build` 和 `make agent-doctor` 全部通过。0.6.0 包共 8,290,866 bytes，距 8 MiB 余 97,742 bytes。源码聚合 SHA-256 为 `7157c91090210d93a2a2de29f6fd45a3140e8f4a9891bd263d366078336c3d0f`，bundle BLAKE3 为 `7d440ae804fc0d3a482542a942ad9b301b38aceb71dd233e1d1521ef84f40417`，二进制 SHA-256 为 `ed1c112a5156d5a7588301b2352bc72dab9a39748ac650860aac3ffcbdce02fc`。正式 pack、源码、二进制 guard 与挂载 main／font 匹配，Maps／Mail、其它字体及主题未变；完整证据归 `build/research/agent-generated-ui/host-font-precheck/final-safe.json`。最后截图更新后的 pack 与二进制重新封装核对，未再启动；实际操作对应相同最终 main 的此前运行包。所有本任务实例已关闭，不操作用户实例。

早期深层 schema 在锁定 VM 的 JSON 深度上限产生非法请求；动态 key、oneOf 不支持的旧归因已被否定。标准引用能解决序列化深度，但未解决模型字段耦合；两种平铺协议完整批次失败，sections 将结构与真实引用分开后保留。后续仅消除无价值包装并将单地图限制表达为实际契约，没有提高预算或放宽事实校验。M3 官方 verifier 未支持 json_object，接口接受 schema 不等于严格执行；相关官方来源与隔离调查归 `strict-capability-safe.json`，不宣称所有模型端点均不可能支持。

## 接续与完成依据

本次获授权实现、必要验证、资源与文档已完成；本地提交，不推送或发布。固定外壳、真实 M3 分区组合、真实引用与操作边界、地图和原期限、本应用无衬线及其它应用不变都有上述证据。用户可用 `make agent-dev` 体验当前版本；尚未用户验收，不标成已通过新的产品里程碑。后续修改从本任务的体验反馈接续，不用历史成功代替新版本验证。
