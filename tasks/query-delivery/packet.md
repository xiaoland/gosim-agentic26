# 首次定位与查询结果交付

状态：2026-10-05，用户反馈0.9.2后“地图又不见了”，现场分类已确认，0.9.3确定性次生修复与布局契约检查通过，地图呈现继续由Agent负责，优先接续开发诊断；0.9.2单一结果区域修正曾通过Android定向检查与最终封装；0.9.1局部修复和封装已完成。原句正常harness已实际交付候选地图与详情，完整道路分段／公交详情仍未通过。首次真实授权未重测，预算故障未精确重现；单次成功不证明普遍可靠。

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
