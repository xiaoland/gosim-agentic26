# Agent 直接生成 Navigation 界面

状态：2026-10-04，单一工具调用 harness 与按需技能已实现，真实 M3 自主查询／比较／生成原生界面及一次生成按钮交互已发生。起点显式 demo，macOS 宿主 Android 手机模式；不称真实 GPS 或 Android 真机。模型后续解释与确定性不可确认结果不一致、长行裁切仍待解决，不称路线和 UI 质量验收通过。源码与实际负例截图已冻结，本轮自有实例已关闭，正式封装与实际挂载一致性已通过，准备本地提交。

## 目标、授权与责任

固定外壳只保留输入框和查询／终止按钮，其余内容让 Agent 组织。Navigation 使用无衬线字体，其它应用保持原样。用户先指出分区协议约束过多、预制组件包装度高及一图限制，授权“是的，继续”；继而明确：“我个人建议不要在这个开发阶段做任何的安全边界、一致性校验、输出限制等等各种限制”。这更新了本轮取舍，不再为开发期界面建设沙箱或组件协议。根已告知按直接原生生成推进；用户指定的时间／预算仍是路线任务条件，密钥仍不进入 Git 或模型输入。

必要实现、实验、验证与文档更新已授权，不重复请用户审核。本地提交沿用既有授权；不推送、发布、签名或赛事提交。bundle 保持 OctoScript 脚本及资源；只关闭本任务实例，不改系统权限、字体或其它应用。后续交互与截图以 macOS 宿主 Android 手机模式验收，不称 Android 真机。初赛北京时间 2026-10-04 23:59 截止，优先可运行闭环，不扩展通用平台。

根负责协调、决策、长期文档、证据采用与最终提交。GPT-6.1 Sol medium 的稳定负责人 ui_finish 负责应用、smoke、截图及实际交互；host_finish 已完成原生接口验证，但后续两次模型capacity失败且没有执行操作。新增诊断与工具链收尾正式转交 GPT-6.1 Sol low 的稳定负责人 native_error_api；直接对接 ui_finish，保留原host变更／证据，不重复原探针。advisor 只作 consequential judgment，不作 reviewer。现有改动和失败证据保留，不继续旧 schema 验收。

## 已决定的实现

用户原话已纠正为“不是workflow”：只提供元提示词、工具、技能等资料，由LLM自己处理、组合完成目标。根已承认此前限制／协议／重复回归过多，停止全量验收和旧展示错误重问流程，不再为旧稿窄修延误模式迁移。

采用一个标准工具调用循环，复用现有M3 HTTP和领域执行函数。保留assistant原始tool_calls，按tool_call_id执行当前批次（顺序足够），追加对应role:tool结果，全部完成后回到模型。工具不自行next_action／request_interface，不存在第二个展示Agent或历史主人。assistant无tool_calls即本轮结束等待用户，不强制finish；用户终止沿当前run生命周期停止后续派发、保留原业务期限。工具正常失败回结果，传输失败明确结束，不隐藏重试。

工具直接复用技能读取、日历／笔记／定位、地点查找及采用、公交／驾车查询、候选确定性比较、render_ui(source)、Trip确认保存读回。不是next_action加action参数的万能封套。工具说明真实输入与结果；缺位置／目的地返回实际缺失，不用available_actions／can_present当phase许可表。原present_results强制公交＋驾车、选route、结束、触发另一UI循环的连锁行为撤掉。LLM决定继续查什么、何时澄清、展示及结束，路线计算不重写。

技能按需提供已执行的Makepad基本语法、原生类型继承、Navigation字体、snapshot／mailbox接口与示例，不规定页面结构或“读技能→渲染→修复”顺序。render_ui挂载并读真实diagnostics后返回结果；错误反馈在同一工具历史由模型决定处理，不在工具内部重新问模型。纯查看与地图加载本地响应，需要判断的用户动作进入同一会话。

已撤应用自设的模型token、源码／输入长度、工具步数、自动阶段、纠正次数、网络／地图timer、响应bytes、source条数／字数、几何截断与重复调用quota。不是重写宿主／服务实际能力。删除后只允许更多／更久／更自由的框架限制撤掉；原时间／预算、实际坐标／端点、未知费用／来源事实和确认计算继续作为产品语义。密钥不入Git／模型输入，不改其它应用。

官方宿主现有app peer入口不直接采用：锁定script_apps.rs只提工具授权、不传instructions／skills，implemented_by:app返回app_tool_unavailable；本机launcher没有kernel。不能据清单支持宣称已可调用。参照[pi-agent-core](https://github.com/earendil-works/pi/blob/main/packages/agent/README.md)的标准tool调用／结果历史和[按需skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)，迁移现有OctoScript loop，不安装Node／SDK后端或造新平台。

## 原生依据与迁移前的调查记录

现成 `build/research/agent-generated-ui/nested-splash/{parent,child}.splash` 已在 Android 412×892 模式实际渲染中文、按钮及两 Image；父通过 ui.child.red／blue 分别加载图像，子写 mailbox、父读取三次实际点击均通过。先 set_text("") 再 set_text(newbody) 后旧 timer 没写新 mailbox。根已查看 android-app.png；证据为 result-safe.json、lifecycle-safe.json。公开 fixture 不是 M3 产品验收，也未证明 snapshot 热更新或真实 Android。

原生 ui.find(name)、ui.child(index) 和只读 rect 已实现并锁定。动态字符串查找复用静态 getter，直接子实例可独立加载，rect 是最近一帧已绘制裁剪 area，未绘制返回 nil；不能在借用 render 中同步查询。host 独立索引重放与像素／几何／查找实证已采用，原定位、Maps 和字体 patch 字节保持不变；新增接口不需要重新设计业务桥。

host 已完成嵌套命名 Image 的 mailbox → ui.child.find(name) → 分别异步加载实测：蓝图先回、清空后同名换稿、倒序加载与旧代迟到均符合实际实例，像素已查看。证据 api-nested-mailbox-result-safe.json，使用公开 fixture 色块与城市标识，没有真实网络地图或 M3，不替代产品验收。无需新 Rust／重编；源码已交 UI 直接复用。剩余是 M3 自己生成该闭环及真实地图／交互验证。

此前发现 raw body 默认子 VM、LinkLabel、Factory、嵌套 VM 与原生资源不受完整脚本限制，曾据此停止直接生成。用户本次明确不做开发期边界，该治理不再是本轮任务，不继续沙箱工程。调查结果是历史事实，不再作为停止实现的理由。

2026-10-04 复核[官方提交指南](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md)，允许说明可构建原生宿主扩展，未发现 stock-only 规则。用户初赛 OctoScript 应用边界仍保留；宿主覆盖单独锁定、复现与声明。

## 执行诊断的必要接口

实际生成已能进入子执行，但 M3 反复将 draw_bg／draw_text 写普通object而失败。当前try先trap.err_clear再进入失败分支，没有脚本异常值；Splash captured_errors／take_errors只写宿主日志，View只转Error:TypeMismatch。真实native.log含 expected DrawQuad, got object；原生正确扩展语法为 draw_bg +: {...}、draw_text +: {...}。手工日志反馈可推进调查，不作为应用自行修正完成。

根采纳advisor：新增极小Splash实例只读最近原始诊断，让应用把实际执行结果交M3；set_text每稿清旧诊断、复用捕获与格式化、保留宿主日志，不读全局log、不做错误平台或沙箱。这是必要功能接口，不是重新加界面边界。native_error_api 获授权实现必要Rust／patch／lock／包装，UI继续语法与交互，不等桥。如果只能通过重构全局错误系统才能归属实例，或最终仍只有TypeMismatch则停止接口扩展并如实保留缺口，不堵当前生成。完成依据为 known ordinary-object失败→应用读具体错误→M3修正→实际挂载，非人工改源。

diagnostics 已由公开fixture闭环验证：具体on_render类型文本可读、重复读相同、原log保留，clear后正确+:稿诊断为空且中文实际挂载；证据 nested-splash/diagnostics-result-safe.json 与 diagnostics-after.png（负责人已查看）。nested-splash/diagnostics-patch-replay-safe.json 独立索引完整重放两patch且verify_source通过，最终Makepad tree 4f2d590852cd98f479848636ce80c882477e0579、host tree 668cfb41686ec8780381b47494368b98a8f1aad2。当前binary 072307a2是接口实验，不冒称正式包。UI已收到先diagnostics启用再set_text的消费方式；真实M3自行纠正闭环仍待验收。

接口边界归toolchain/README：首次调用只启用当前实例以后捕获，读取不消耗缓存、set_text清空、原log tee保留，其它Splash默认不捕获；try主动捕获的异常依然会清除，不能恢复具体文本。不宣称已获全部错误类型。

## 当前完成依据与恢复点

单一正文技能为 bundle/assets/skills/native_ui.md 与 navigation_data.md；官方 bundle/skills 目录保留给 peer 声明，故材料放 assets，应用运行目录仍为 skills。启动器从构建包材料化到应用私有目录，read_skill 按需读取；未引入 kernel、SDK 后端或通用技能平台。材料化逐字节一致证据为 build/research/agent-generated-ui/skills-materialization/result-safe.json。6项实际原生、合成模型验证为 build/smoke/navigation-harness-807l3mw4/report.json，覆盖同一回复多个调用、原消息和call_id、真实render诊断、无调用结束、原deadline与实际按钮回同一历史；根已读取，不重复全量旧回归。

真实 M3／高德记录为 build/research/agent-generated-ui/native-harness/result-safe.json，根已读取并查看 agent-harness-before-click.png。模型自行选择 read_location／read_skill → search_places／set_constraints（缺来源实际错误）→ adopt_destination／query_transit／query_driving → compare_routes → read_skill → render_ui，实际返回7候选、空diagnostics并可见。该顺序是本次观察，不是应用规定的workflow；没有人工改模型生成稿。

实际点击“放宽时间到80分钟”进入同一历史，原received_at不变、arrive_by按新时限从原起算更新；模型自主只调用render_ui后结束。工具facts仍confirmable=[]，模型却声称路线可行，Trip未确认。窄屏长行裁切，包截图取初始负例，不用后续错误文案作展示成果。后续应解决模型对当前检查事实的误读与原生布局可靠性；不能用增加预设workflow或夸大验收掩盖。任务无待用户审批事项。

执行产品main SHA256 96bb5ed6269c9d44230207eb05ce03ab28370a8f811eb92e8c8178a150dccdb8；最终8c6f93ad586881c135c95db0d8675eff22db32e4480981cacd5d0ae85427c743只改单正文技能读取及行尾清理。native_error_api已完成冻结后一次check／build／doctor及隔离挂载，根已读取 build/research/agent-generated-ui/final-package/result-safe.json。0.7.0解码包7,272,241 bytes／10文件，stage、官方pack与实际挂载逐文件一致；source aggregate 10be566979a3e093b46f47b22fbf813d29e78b2421a1298a0502d60855c6a816、runtime BLAKE3 7e1410d54c55980314db1f97b6e2bfb5dd474930131ff3cd6de202e79c801c32、binary SHA256 17b5ed78d3c64158c15c01291da1b08bf5f25f20df5827c88b69676d41c2f345。该封装不调用外网、不替代产品交互证据，自有实例已关闭；根本地提交。不继续全量94回归、不添加模型试跑，不推送、签名或发布。

## 统一 harness 前的直接生成证据

正式应用 main SHA256 efa9d528624eef4502d3cce95f945253b05c85fac2f787929bb62225d38fa64c 的 build/smoke/navigation-native-r4ayl04r/report.json 已通过94业务＋13直接生成功能，覆盖中文挂载、嵌套图、mailbox查看、独立／倒序／单图失败、换稿与停止迟到、超过旧步数／500秒／32KiB仍执行、多次协议反馈可继续及用户终止。受影响HTTP派发的独立7项通过 navigation-native-26_8v34q/report.json，实证无应用40秒timer时持续等待、可终止及实际HTTP状态。两份均隔离原生运行、无外网；报告把产品摘要和注入后摘要区分，不代替真实M3。

真实直接Splash澄清首次输入2975B，被旧40秒timer结束，没有服务响应或源码；旧timer现已撤。新请求输入2977B已HTTP200返回：17.81秒，6171B源码，923输入／1413输出tokens，未设置max_tokens。子on_render运行失败：M3用了不存在的self.viewport／self.snapshot，当前澄清背景没有路线，源码尚未渲染。原源码及结果保留，不算成功；负责人加入实际语法／API短例，并将子render真实错误通过mailbox反馈到模型继续修正，保留用户终止，不限制纠正次数、不改写或隐藏错误、仍按原任务期限。尚未冻结截图或封装。之前的47b5aa（94＋10）与7jgg9dwg（94＋11）属本轮中间功能证据，不称最终同版。

## 中间控件树阶段的证据

已经完成但按用户新指示撤换的低层树通过 94 项业务、29 项 UI 边界，报告 navigation-native-ypcpf722/report.json，产品 main SHA256 e8f552c8939d6b63fd6a881265e1d6619d65eaa42c089de031f83b18d40b174f；注入测试后摘要分开记录。该记录无在线请求，不证明新直接生成路径。

真实 asking 首次及一次反馈因数组形状、text／data 并存和虚构 Map 目标失败；schema 对齐后一次请求 40 秒超时。真实 Maps 选点、坐标转换及城市核对后，高德取得 7 候选，proposal 输入 30,705 bytes／11,388 prompt tokens，首次有两张不同目标的图但多余 Map color／align 被拒，一次纠正被旧 4096 输出预算截断。曾决定展示8192并重新冻结当前来源，尚未发出新模型请求即被用户新方向替代。完整原 segments 未保存，不能伪称精确重放。所有失败保留；未达到真实双图验收。

## 0.6.0 基线证据

分区协议与一图是旧实现，不是产品要求；其完成记录不替代本轮验收。main `49994976`，产品前版 `b0d6f6de` 完成 94 业务／58 定位／7 派发／47 UX 回归；最终只增加三处 map:null 拒绝，精确差异归 `source-null-delta-safe.json`，同版 15 项检查归 `build/smoke/navigation-_jx3fjkc/report.json`。固定三次 proposal＋一次 asking 均最多一次反馈有效，归 `sections-map-fixed-safe.json`；不代表可靠率。

0.6.0 实际服务 UI 联调用了明确 demo 起点、真实 Maps／高德，得到 7 条不可行候选，复用真实 M3 布局，切卡跟随图、展开／编辑及原期限通过。不是完整自主任务或真实 GPS 验收；原 desktop 横排长按钮裁切。旧证据归 `build/research/agent-generated-ui/report-safe.json`。

字体已完成：Navigation Sans CN 基于思源黑体 CN 2.005，保留全部字形／映射、去 hinting 并依 OFL 更名。来源／复现与完整许可归 `bundle/assets/fonts/README.md` 和 `OFL.txt`；实际探针同窗对照确认 Nav 无衬线、原主题文楷，其它应用字体与主题摘要未改。证据 `build/font-probe/report.md`、`formal-font.png`、`unchanged-host-fonts.json`，根已查看。

0.6.0 check／build／doctor 通过，包 8,290,866 bytes；字体附属文档 gate 独立覆盖、官方包装身份与原定位／Maps patch 不变归 `build/research/agent-generated-ui/host-font-precheck/final-safe.json`。source aggregate `7157c910`，bundle BLAKE3 `7d440ae8`，binary `ed1c112a`。本轮必须重新封装，不能沿用旧摘要。
