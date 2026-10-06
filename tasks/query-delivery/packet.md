# 首次定位与查询结果交付

状态：2026-10-06，逐轮只读诊断已完成；用户回复“是的，先修”，授权修复诊断记录配额和迟到渲染通知状态。0.11.1修复、检查与封装已完成，保留当前用户实例。用户所指三轮仍不能逐一关联，修复不等于详情／地图普遍可靠。

## 目标、边界与授权

用户报告：“第一次时，提示授权，然后授权后结果是无法获取定位，无法计算；可能是没有等待授权”“第二次时，有结果，但是没有地图”“第三次时，只有‘查询完成’，没有渲染出任何内容”“第四次时，只要方案摘要，没有给出方案详情”。延续已授权交互地图与原生查询范围，完成必要调查、修复、正常harness验收与说明更新。不能再用手工挂载skill示例作为整次查询证据。

同一M3自由编排，保持独立查询、无持久化、无澄清、无第二展示loop、无预制业务卡、无强制工具顺序或输出validator。不改TCC，不关闭用户实例；凭据、个人位置、原始历史和日志留忽略目录。按既有授权本地提交，不推送、签名或发布。

native_error_api负责定位、覆盖及最终封装，后续接管预算入口调查；ui_finish负责终端／生成稿／地图详情及实际Android检查；根负责判断、整合、知识回流与提交。源码职责保持稳定，不回退其它修改。

## 已确认问题与修复

现场readonly-safe.json显示用户当前bundle／挂载／skill一致，5215B生成稿和8候选只有Label，没有地图、Button、emit或事实回调。日志有HTML解析、width scope、border_radius错误后修稿；前几轮完整VM历史没有只读入口，未注入用户实例，不能声称四轮逐次重现。

终端assistant.content原来只写facts.answer，再用“查询完成”代替可见回复。0.9.1将所有非空终端内容通过通用文字区域呈现，同时保留已生成UI和本地状态，产生双份结果；代码块只按文字显示，不抽取执行。空回复且无稿明确缺少展示内容。安全模型请求失败归runtime_status，已有稿和原生诊断保留，不再统一误报生成界面失败。

Android针对检查发现首次生成区域零高度，以及父Factory重render会清掉子Splash VM，即使同名／等值body也不能保证保留。首次mount先apply有限高度，再安装完整source；零面积子几何回退父内容视口。活跃稿不重建，只更新事实；终端文字区域独立更新。render_ui契约说明整稿替换，success仅无已报执行诊断，不证明内容目标完成。

定位旧15秒采样和16秒registry时钟从dispatch开始，弹窗可能消耗预算，超时stop后授权也不会续采样。现通过cx.request_permission(Location)等待匹配系统结果，获权后才启动新15秒采样；registry的system_permission与sheet暂停原因独立。拒绝、终止、关闭heap和迟到授权不能重启请求。OS失焦不等于宿主内部切换，真实内部切换仍停止采集；业务arrive_by不变，无mock fallback。原Maps／字体／UI五patch字节保留，覆盖重放和source verify通过。

正常生成稿曾使用不存在的Array.find，按钮事件在切页和map事件前中断。native_ui只补锁定语言实际for／下标／len查项语法，未扩运行时；navigation_data明确passed=false及reason/reasons、未知末段的含义，未增加输出检查器。

## 验证与证据边界

定位location-permission/result-safe.json：隔离回调覆盖30秒授权等待、错误ID、获权新采样时钟、拒绝／取消／迟授权和独立registry暂停原因。没有重置系统权限或再次触发真实首次弹窗，不能保证15秒内取得合格GPS。

Android终端检查5项通过，build/smoke/navigation-harness-cxnwuz4_/report.json对应最终main49cdbe17…：实际生成内容可见，本地修改的输入／页面保留，80行文字与代码块末尾可滚达，纯终端／空终端及安全transport反馈正确。根已读报告并看top/bottom截图。早期tirpvy1h只属桌面检查；这组使用合成模型，不能代替真实M3。

正常M3旧失败全部保留在query-output-recovery/result-safe.json。明确要求地图／详情的样本1次render诊断空，却因Array.find点击失败，并把passed=false候选称符合；原句另一轮316秒后实际失败，无render记录，旧观察器状态过时且transport记录缺失，不能归因供应商。修正版原句曾返回HTML／backgroundColor诊断，随后父agent_tools报script time budget exceeded。

预算源码每个入口独立64ms墙钟，不跨网络等待累积。budget-probe/result-safe.json以207567B已有历史／9379B稿对照，新旧入口均完成schema／JSON／bytes，未精确重现原失败。最小timer将状态UI与请求准备分开，没有提高预算或逐stage预防性拆分；不能声称故障已彻底修复。

最终原句“40 分钟内到机场，预算 50，尽量便宜。”由标准M3循环实际完成：5条assistant、5个HTTP200、1次render_ui诊断空，取得真实8候选并自动生成稿。Android实际点击两条打车候选显示高德地图、费用未知和限制详情，返回有效；点击后history不增长。本轮无native错误，响应未截断。根读normal-final/record-final-safe.json，并看final-detail.png和final-second-detail.png。位置为显式演示的宝安大仟里室外步道，不是广州设备GPS；M3／地点／交通／地图服务真实。Android切换导致旧新观察器竞写safe，最终仅采用对应本次received_at的完整history与record，不能使用空idle文件判定该轮状态。

最终check／agent-build／doctor通过，final-package/result-safe.json：source04eae20e…、main49cdbe17…、包7250742B共10文件；embedded与mounted逐字节一致，stage仅manifest预期完整性盖章差异，两技能材料化SHA一致。根已读报告，自有实例均关闭。中间包19a67566…已被最终版本替代。

## 剩余与接续

完整规划仍未验收：生成稿没有逐段道路，公交仅摘要无详情按钮；行驶时间数值成立不等于候车／起点／末段已核实。末稿邀请放宽条件，但产品没有对话续接。下一步围绕这些实际遗漏分析取得的事实和技能使用，不靠盲抽样或手修稿通过。首次真实授权与原预算故障保留对应证据边界。

README与architecture已回流已证行为。所有原始证据在忽略的build目录，safe入口为build/research/query-output-recovery/result-safe.json；运行记录不是产品持久化。当前无需要用户审批的源码事项，不声明整体验收通过。

## 当前窄修：单一结果展示

用户确认“已有正常生成的界面时只展示它；没有可用界面时，才用最终文字兜底。最终回复仍保留在本次工具历史中，不再并列呈现第二份结果”，回复“是的”授权实现。UI稳定owner负责main与最小Android检查；根负责版本／长期说明，native仅最终封装。使用实际原生执行／render状态，不能仅凭开始mount时的generated_active隐藏兜底；不增加内容检查器、额外模型loop或服务请求。验证正常稿不重复、无稿／执行失败文字可见、本地状态保留；无M3抽样和广泛回归。0.9.2包元数据与main4bbd2922…已冻结。采用rendered事件与当前diagnostics空状态选择生成稿，而不是仅generated_active；失败且最终文字到达时隐藏父generated_area，不销毁实例。根已读single-result-safe.json并查看实际正常稿与失败兜底截图：Android6项通过，正常稿不重复、无稿长文滚达／代码只文字、失败稿文字可见、空结果明确，history／facts.answer与本地页面输入保留。本轮只合成模型／真实原生控件，未请求M3或交通服务；有意TypeMismatch留原始诊断，不假称零诊断。自有实例关闭，用户实例未碰。native完成唯一最终封装，不追加行为验收。根已读single-result-package/result-safe.json：check／build／doctor通过，main4bbd2922…、sourceaed06eaa…，包7251151B／10文件；embedded／mounted逐字节一致，stage仅manifest预期完整性盖章差异，两技能SHA保持，自有实例关闭。README与architecture已更新当前单一展示契约；该窄修完成，前述完整规划／首次授权／预算边界仍保留。

## 当前缺陷：地图再次消失

用户报告“地图又不见了”，授权沿查询／地图故障范围必要调查修复。UI稳定owner只读当前实例，核挂载／skill与生成稿是否含地图及事件、真实原生诊断、地图加载和父显示区域；不重启用户实例、不注入VM／挂稿、不先归因模型。需区分模型未生成、地图请求失败与0.9.2展示选择隐藏已有地图。前一窄修合成检查没有地图，不能当地图实际查询回归已通过。root维护packet／docs与元数据，未先改版本，无新的M3抽样。

根已读map-visibility/result-safe.json：当前生成稿无地图控件／map事件，只有view_route；真实18候选、maps_available=true、位置非mock，区域与详情均正面积，model稿以视口小为由省略地图。main／skill材料一致不证明该轮读过skill，也不证明生成时viewport与事后geometry相同；实际入模历史不可取，未注入VM；源码中的966×466仅mount时facts，不能反证428。旧11:11 audit不属于本轮，未采用。

采用advisor：只澄清实际viewport／滚动布局契约，不加must提示词、地图门槛或强制补稿，不能宣称能保证每稿地图。并修后续局部诊断隐藏曾成功稿的确定性次生问题：成功标记按当前稿保持，新稿／清空复位；原始错误继续反馈，初次失败仍文字兜底。这一修复不能解释本现场地图省略。

已向用户询问是否允许宿主保底地图，或维持完全Agent生成。用户明确回答：“我们不提供这种保底；我们应该尽可能避免 Agent 省略地图，本质上，这是呈现形式/UIUX 不够好的问题”。已确定不引入宿主固定地图，继续优化Agent呈现；独立诊断隐藏修复与布局契约已完成。

0.9.3采用证据：mainb7b842fd…、native_ui14962b49…冻结。rendered通知只表示排队，成功在原有render_ui 0.25秒诊断结果点且通知已到时锁存；仅新稿／清空复位。Android7项定向通过（jy6rm9qr），root已读safe报告并查看局部错误和首稿失败实际截图。真实按钮查不存在控件，由子try捕获并emit runtime_error，父保持原稿及本地输入／页面，反馈已有结果保留；首稿真实类型错误仍文字兜底，不误锁存。未声称未捕获callback自动桥回，未请求M3或出行服务。用户实例只读，自己的隔离实例关闭。当前地图省略仍未证明解决，用户已否决宿主保底，当前未决的是如何改善Agent呈现；未添加固定地图、强制组件或输出检查器。native做唯一最终封装，root回流README／architecture并本地提交。

用户随后建议“优先改进软件的可观测性、可诊断性”，诊断优先工作归[开发诊断任务](../observability/packet.md)。先补精确模型／工具／渲染／事件轨迹，再以本地图省略案例调查UIUX，不以观测工具替代产品能力或恢复业务状态。0.9.3最终包已完成check／build／doctor与10文件一致性，mainb7b842fd…、source68b5c33f…、包7251476B，自有实例关闭；根已读取safe，采用并本地提交该局部修；地图省略仍未解决。

开发诊断0.10.0的[证据与恢复点](../observability/packet.md)已补齐。一次真实M3任务在read_location入口发生宿主预算中止，trace明确没有后续技能／渲染事件；开关记录对照均完成，现场根因仍未确定。地图省略的后续调查应使用新trace核对实际messages、技能结果、工具调用与生成源码，不再从最终视口反推先前输入。


## 当前接续：诊断配额与迟通知修复

用户先授权“是的，推进诊断”，之后听取两项明确问题回复“是的，先修”，授权必要源码、工具、测试和说明更新。本次只修开发记录耗尽宿主条目配额，以及同稿迟到通知不能更新显示；不扩为地图保底、内容检查器、模型抽样或新一轮详情设计。用户正在运行的实例不重启、不关闭、不注入；原始记录只保存在私有忽略目录。

### 诊断依据

根已读 `build/research/query-delivery-current/result-safe.json`。当前应用jail有258条目、约2.97MB，旧诊断占240条目。计数文件合法且权限正常，但宿主每次fs.write包括覆盖都先查全jail的256条目上限；当前实例计数写入失败、instance=nil，没有事件目录。当前挂载main f8fe4d0f…与快照归一匹配，技能材料一致不证明本轮读过。

另一启动session的vm-2/run1独立证实迟通知问题：seq79空诊断且notified=false，18ms后seq81收到rendered，seq97结束仍rendered=false；6035B生成稿包含地图与9个按钮。旧run2生成XML／JSX标签式源码并实际解析失败，之后记录止于新请求准备，不能称正常结束。它们不能直接对应用户指定三轮。当前run2源码含地图、8个按钮和详情／返回事件，树无实际详情地图控件；宿主日志有解析、类型、指令与heap错误，但无当轮trace不能进一步归因。

### 实施与责任

UI稳定owner拥有main.splash、必要既有原生测试：改用宿主已核fs.append按容量分段JSONL，保持session／instance／run／seq、精确密钥去除与不完整状态。每文件上限1MiB，不能全量重写或静默截断大事件。同稿rendered到达时依据实际诊断锁存成功并刷新显示；原0.25秒点仍可作为工具回执，不再是唯一成功入口。新稿／清空复位；旧run／generation不能改新稿，终端之后通知也可完成，成功稿不因后续局部错误撤销。

native稳定owner拥有agent.py及对应包装器检查，协调新格式读取与序号完整性、截断处理、私有权限及凭据检查。新启动前仅将已停止开发实例的诊断完整迁出到私有build保留证据；不碰业务来源、不迁活跃实例、不扩大宿主quota。当前超配额不能只靠改新格式恢复，需确认旧记录可安全迁出。根维护版本、持续说明、packet与整合。

### 验证与恢复点

有界检查覆盖超过256事件仍不耗尽文件数、分段读取与不完整记录、旧记录迁出边界、迟于0.25秒及终端回复的成功通知、错误稿和旧稿通知隔离。以宿主Android模式验证实际显示；只启动关闭自有隔离实例，不新请求模型或地图。随后进行唯一最终封装与挂载一致性检查。两处修复、有界行为检查与最终封装已完成。


根已采用工具包装器11项检查，实际输出见 `build/research/trace-quota-recovery/wrapper-result-safe.json`：旧格式和分段读取、序号缺失／重复／未提交、截断、精确凭据检查、归档原字节与权限、活跃实例拒迁、历史唯一查找且当前不回退。可运行入口为 `python3 tools/test_agent_trace.py`。本次没有迁移正在运行的用户数据。

同产品main SHA260c727e…的Android原生9项记录检查通过，报告 `build/smoke/navigation-harness-14pw5ou6/report.json`：324事件、两份大UTF8记录换段且各段不超1MiB，写入故障明确不完整但新查询继续，默认关闭不新增文件，实际当前实例选取正确。根读报告并看trace-android.png。迟通知5项见 `build/smoke/navigation-harness-ax167u45/report.json`，覆盖0.25秒时未通知、终端后恢复单一生成稿、成功稿局部错保留、同run旧generation通知拒绝，以及新稿实际DrawQuad类型错误仍文字兜底。根读报告并看late-success.png与late-first-error.png。两个检查均为合成模型、真实原生控件，未请求M3或地图；不能当完整导航验收。

早期迟通知夹具因旧新VM竞写、嵌套异常例子empty-stack及宿主诊断格式器UTF8异常失败，没有算通过。最终夹具按当前可见身份运行，以简单实际按钮发送局部错误事件，延迟只替隔离源码计时数值；首错仍真实类型错误。empty-stack和UTF8格式器问题没有在本次修复，当前证据只证明所列显示状态边界。


根已读最终封装 `build/research/trace-quota-recovery/final-package/result-safe.json`：check／build／doctor通过，source2b5e411b…、main260c727e…、runtime49b9da77…；10文件embedded／mounted逐字节相等，两技能材料化相等，自有实例关闭。源码与宿主patch trees没有后续改动。README、architecture及工具链说明已回流当前行为。此两项窄修完成；用户重新运行make agent-dev后旧开发记录将在停止边界归档，当前运行实例仍未迁出或重启。后续使用新trace关联实际地图／详情呈现，不能补认历史三轮或声称所有生成稿已可靠。
