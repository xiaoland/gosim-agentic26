# 真实背景信息接入

目标是让 Navigation 的 Agent 按需读取真实系统日历和 OctoSense Notes，保留逐原记录、来源与时间范围。主 Agent 转述用户睡前授权继续“真实接入背景信息（日历、笔记等）”，随后明确授权 adapter 实现、隔离测试和背景合同回流。最初adapter调查与隔离片段由context_sources完成；现main／adapter／manifest／caller与UI由rail_model稳定维护，宿主及封包由runtime_update维护，正常窗口的针对交互由rail_e2e执行。不得代点个人授权、选择日历、打开真实 Notes、读 seed 充当个人背景或调用 M3；不能改他人源码或编译共享 target。

## 当前恢复点

用户实际出现两次模型服务失败，原386条连续日志与原请求均保留在build/research/real-context/user-model-failures。root授权同窗口人工继续失败模型轮次，不重跑已完成工具、不新增自动重试或延长HTTP期限。main `117426564ae29875b756523d2c2aa413a4e4a4cddbbe9ead322cd715f550c056`已冻结，runtime既有check／stamp／build／doctor全PASS，source `545b4d1d`／binary `6ad1e128`，receipt为build/research/runtime-upgrade/rc6/manual-resume-preflight.json；同按钮在安全条件下显示“继续规划”，保留本轮消息、Route、来源时间与绝对期限，仅追加当前时间／已过时长／资料未刷新的结构化事实。输入变化、停止、切记录、新规划与成功响应清资格。正常79292／53163已为修复停止，原模型会话不冷恢复；重开窗口后此能力用于之后的同窗口失败，不能称旧失败已继续。

唯一Android针对组5/5通过，报告build/research/rail-integration/manual-resume-probe/resume-hi21s_e5/report.json：实际可见按钮点击生产shell_action→resume→agent_pump／prepare只截获一次派发；原四条消息与Route金额／source_ts／received_at／绝对期限不变，不重复工具；保存pending到完成后的资格、旧owner／run／trip／history／迟到回复、成功与真实输入变化边界已核。保存提交回调明确合成，停止失效仅核源码，不冒称重验持久化。早期控制层漏可见性导致按钮隐藏的失败原件resume-gkdv0zl5保留；修复共用shell_control_visible后最终通过。无M3／供应商调用、账本未变、实例全停。

独立原请求长deadline探针由root单次授权，只取得响应而未执行工具：同ureq／TLS／primary正文HTTP200在91.094秒完成，低于原120秒，只说明服务间歇性失败，不支持延长期限。receipt为build/research/real-context/user-model-failures/long-deadline-attempt/receipt-safe.json；59242 tokens仅在隔离回执记录，未写原宿主账本，不代用其响应续用户任务。正常HOME停止前账本27calls／491507tokens，SHA eb970a550c7c637d1f5ab6de4238cd9ec6ccf38fb4a81886598c278398bc58a8。封包后rail_e2e已重开唯一可见正常窗口49677／63428，session725874fe15164e6b83e20c029e3e16eb，source545b4d1d；Android新出行输入图已查看，未submit、恢复旧messages或执行探针。calls／tokens守恒；正常launcher配置后当前文件SHA b005e9c9e1b713faebe2324cf97dd23628ce3a5b9418d4e4dc39dfd1322a408b，不称字节与旧SHA相同。receipt为build/research/real-context/user-connection/manual-resume-input-safe.json，窗口保持供用户操作。

用户随后亲点授权后宿主Review返回host_not_configured，原图与safe回执为user-connection/calendar-host-not-configured。root授权runtime_update修复开发.app打包：现launcher虽已在包内运行，但Makepad共享profile sidecar没有Calendar用途字段。packaged_host改为从锁定官方打包模板合并新旧Calendar与定位四字段，相关dev／hidden共用路径，权限API与main不改。原41618已由rail_e2e停；fixture、实际包plist与doctor通过，binary仍301f8848，tools SHA3afe5952，账本8923b604前后匹配。恢复回执build/research/runtime-upgrade/rc6/calendar-packaging-receipt.json，已交原窗口owner唯一重开展开供用户亲自重试；本次无permission.request／events／provider，不冒称用户已授权。

用户正常环境的“背景与权限”展开故障已修并实际通过展开／收起／再开，三按钮各288×44可见；main `11b85622`，证据在build/research/real-context/user-connection/fixed-ui-receipt-safe.json及fixed-{expanded,collapsed,reopened}.png。根因是set_visible(true)后render继承首次visible:false声明，覆盖展开；改为每次生成由当前状态控制可见性的内层View，许可调用不变。

用户随后实际点击日历授权报cache_uninitialized。官方宿主只有permission.status可在冷缓存时异步LoadConsent，其他方法直接拒绝。main `36dd92c9`已将permission／choices／select统一先等待cc_permission_status；request仍由用户点击触发，list／select未授权时明确返回authorization_needed，不伪造空日历，并清除失效选择列表。read此前已有相同状态前置。唯一正常34102已停止，唯一生命周期组7/7 PASS，报告build/research/rail-integration/calendar-lifecycle-probe/calendar-fkvgixc7/report.json：真实新隔离HOME只调用一次冷cache status，成功初始化并返回未授权；三入口等初始化、失败不续调、未授权不派发等仅严格合成验证。无真实request／list／select／events或Notes读取，无M3，账本未变、实例全停。runtime封包check／stamp／build／doctor全通过，source `198dde5e`／binary `301f8848`；rail_e2e已重开原正常HOME唯一可见窗口41618／54689，Android背景面板展开并留给用户亲自授权。证据为build/research/real-context/user-connection/calendar-fixed-entry-safe.json与calendar-fixed-entry.png。尚未验证个人授权、日历选择或真实事件读取，不能将fixture或status初始化当授权成功。

用户已实际授权后为selection_needed，列表按钮仍无可选择项。正常51390的脱敏UI证据显示条件已生成160px ScrollYView，证明cache非空，但没有选择Button；官方Calendar字段id/account/name/account_name/writable与main映射一致。根因是按钮for放在新ScrollYView未调用的on_render内，父render只生成空滚动区。main `2506f383`已将条目直接放到构造体，由已有父on_render一次生成；统一callback显示数量、真实空列表或选择成功状态，选择后清列表并说明尚未读取事件。51390已停止，单个Android412×892合成UI组5/5 PASS，报告build/research/rail-integration/calendar-ui-probe/calendar-wolx9ljw/report.json：实际按钮显示2条／数量提示，合成项点击通过status／select回调后确认已选未读并清列表，empty[]反馈明确。所有backend均合成、无真实日历或M3调用，账本不变、实例全停；空HOME无trip_menu的前置失败原件保留，最终只在fixture展开侧栏，不修改生产或新建行程。正式封包check／stamp／build／doctor通过，source `ddea1379`／binary `56fd343d`。e2e已在原已授权正常HOME重开唯一可见窗口79292／53163，仅重放列表按钮：真实返回12个日历、状态selection_needed，实际可见3个完整及1个部分条目并可滚动，窗口留给用户选择。脱敏证据为build/research/real-context/user-connection/calendar-list-fixed-safe.json；包含个人名称的截图仅在忽略目录私有保留。未代选择、未读取事件或Notes、未规划；合成选择状态不能冒称真实个人选择已完成。

日历与 Notes adapter 已由 rail_model 内联生产 `bundle/main.splash`，并注册读取工具及用户主动连接入口。本项目没有现成 Splash import；忽略目录 `build/research/real-context/context-calendar.splash` 和 `context-notes.splash` 仅保留早期隔离实验材料，不能作为继续修改或运行加载入口。永久检查为 `tools/test_context_calendar.py`／`test_context_notes.py`，按现有 smoke pattern 抽取 main 函数，入口注册归主 owner。

日历签名为 `context_calendar_read(start_ms,end_ms,limit,done)`；nil limit 是明确应用默认 200，Agent可选1..200整数。官方 API 没有默认 limit，四个请求字段均必填。window限制1970至2100、最多93天；读取先检查真实permission.status，无授权时只返authorization_needed，绝不自动弹许可或选择。status／permission／choices／select／snapshot供UI接入；permission和select只由真实用户点击调用。选择句柄只存自身账户jail，不持久化事件。Agent独立选择时间窗，不能预拼行程背景文件、强制ICS+笔记两证据或日历→机场workflow。

Notes签名为 `context_notes_search(query,done)`／`context_notes_read(id,done)`／cancel(request_id)／cancel_all()；新轮次与取消应调用cancel_all。search只交官方metadata，records=[]，详情工具read_note按id读取原文。query限非空256UTF8字节，官方最多50摘要并返total/truncated。使用本地扩展 `shared_tools.call({request_id,tool,args})`／cancel，仅notes.search/read；成功宿主data为官方{text,note,data}，内层data才是记录。这是RC6本地扩展，不冒称官方Notes host API或Apple Notes。manifest须请求agent.tools两项；宿主仅对Navigation提供admission offer，仍复用官方relay/grant/AppPeer，不代授权或绕存储。

## 事实与来源合同

最新稳定RC6为 `f9f6fea90b52182790cb2641fd0145c425af4d84`；DesignFlow为 `15b1da01a769a770aaf12bd3012d17c6ff267b6c`。旧d405d5c没有device_calendar或Notes共享能力。RC6 app-hub注册device_calendar；macOS用EventKit，Android系统适配。OctoSense Notes需要app-notes，native-apps.json定义shareable notes.search/read，实际执行器只在Notes打开时存在。原生Notes初始为空；Calendar UI的40条初始化记录及独立Notes示例不是真实个人背景。

| 原字段／状态 | 返回合同 |
| --- | --- |
| event.id+calendar.id | source id；calendar元数据原样保留，不按文字合并 |
| start_ms/end_ms/timezone/all_day | 原样保留并附Unix秒；不用local_time重新解释，不把全天事件当航班 |
| title/location/notes/revision | 逐原记录与raw JSON；revision是内容散列，source_time=nil，不造更新时间 |
| read_at/range/original | 查询来源与范围，不等于实时状态；空仅表明所选窗为空 |
| truncated=true | 数据不完整，由Agent收窄窗口或再读，不据此声称不存在行程 |
| 无许可／无handle | authorization_needed／selection_needed，不冒称空个人日历 |
| stale_consent/account_changed/invalid_handle | 清除旧选择，不交付旧事件；不可继续当新规划证据 |
| Notes source/created_ms/edited_ms | 原文和原始毫秒保留；edited_ms提供source_time，搜索摘要不是全文 |
| Notes未grant／未consent／未打开 | needs_connect／app_not_running；返回真实错误和零记录 |

当前Splash floor经f32导致epoch毫秒变形，原生测得floor(1791735000000)=1791734972416；adapter用%1检查，caller用x-x%1，不用floor处理Unix毫秒。接受的持续合同已回流docs/architecture.md，不在本包维护第二份长架构说明。

源码复核：[服务注册](https://github.com/OctoSense-org/OctoSense/blob/f9f6fea90b52182790cb2641fd0145c425af4d84/crates/shell/src/apps.rs#L273)、[Calendar API](https://github.com/OctoSense-org/OctoSense/blob/f9f6fea90b52182790cb2641fd0145c425af4d84/crates/shell/src/device_calendar/mod.rs#L200)、[EventKit](https://github.com/OctoSense-org/OctoSense/blob/f9f6fea90b52182790cb2641fd0145c425af4d84/crates/shell/src/device_calendar/macos.rs)、[Notes声明](https://github.com/OctoSense-org/OctoSense/blob/f9f6fea90b52182790cb2641fd0145c425af4d84/native-apps.json#L223)。Notes桥源码是本地shared_tools.rs，不能将它归为上游RC6已有服务。

## 验证与下一步

真实RC6 discovery三项完成：events.list描述implemented/supported=true；permission.status为supported=true、app_consent=false、os_permission=not_determined；notes.read描述implemented/supported=false。证据 `build/research/real-context/rc6-probe`。没有请求许可、选择日历、读事件或个人笔记。

日历adapter修订9项已通过，增加非法limit边界；合成内容明确独立于真实未授权状态。证据 `build/research/real-context/calendar-adapter-check`。Notes新桥5项通过：真实宿主返回not_granted，adapter映射needs_connect且零记录；其余截断、原文时间、空输入和取消迟到响应仅fixture；证据 `notes-adapter-check`。新桥无grant实际拒绝核验已完成；metadata修复后又仅复核一次：shared_tools.call/cancel描述均implemented=true，真实not_granted保持needs_connect零记录，native_errors为空。receipt保留binary摘要与停止依据。不能把合成包络当真实个人数据读取。

隔离运行使用owner提供的upgrade-investigation binary和自身空HOME，无profile/key、不启devmode、只停自己实例。Android样式截图已经查看，显示切换后的宿主Home，不算应用UI验收。main 集成和 smoke 注册已完成；宿主 metadata 及真实拒绝复核已完成。真实事件与Notes正文验收的最小缺口为用户亲自完成相应许可／日历选择或Notes共享并打开Notes；不阻塞代码交接，也不声称真实数据验收已完成。


## 用户现场连接恢复点

2026-10-12用户在电脑前，root授权启动正常个人环境供用户完成许可。rail_e2e以make agent-dev（无demo）启动可见唯一PID4419/port56948，默认.local-state/agent HOME，Android412×892已实际打开Navigation侧栏。未提交规划、未模拟位置/背景、未点个人授权/选择日历、未打开Notes。实际点击“背景与权限”后未展开，日历授权按钮尚不可见；保持实例供用户，已交root/source owner判断该UI阻断。只有用户操作后才核脱敏连接状态与数量，不输出原个人内容。

root后续明确授权修复入口，稳定源码owner仍rail_model；rail_e2e仅拥有实际UI验收/唯一实例停止重开，runtime_update负责封包。Android原树显示context_settings_toggle可见[16,202,288,44]，点击后context_settings仍[0,0,0,0]/v0；私有原件build/research/real-context/user-connection/settings-clicked-private.json与settings-clicked.png。尚未改源码、未请求许可，待owner修复后重开正常HOME验收。


## 背景入口修复后现场

2026-10-12 main11b85622/source1653eeec/binary4aae4b58已封包，rail_e2e以正常make agent-dev重开唯一可见PID34102/port50213，非demo。Android侧栏“背景与权限”展开→收起→再次展开实际通过，授权设备位置/授权系统日历/选择读取的日历三按钮分别288×44可见；最终保持展开供用户。原故障为初次visible=false声明在render时覆盖set_visible(true)，修复以动态内View可见性控制，权限调用不变。未点任何权限/选择、未读取个人记录、未规划。实际已查看图与safe回执在build/research/real-context/user-connection/fixed-{expanded,collapsed,reopened}.png与fixed-ui-receipt-safe.json；等待用户自行授权/选择后再只核脱敏连接状态。


日历cache_uninitialized后root授权status首读顺序修复，main36dd92c9针对7/7通过，source198dde5e/binary301f8848封包。rail_e2e正常HOME重开唯一visible41618/54689，实际Android背景面板展开，一图calendar-fixed-entry.png已查看。保持窗口供用户亲点系统日历授权/选择；未代permission/choices/select/读取/规划，不声称用户已连接成功。


用户亲点授权后宿主Review device calendar显示host_not_configured（缺Calendar usage descriptions）。rail_e2e保实际图calendar-host-not-configured.png及脱敏receipt，未代Approve；runtime_update负责最小.app用途声明修复。原唯一41618按协调已stop/ps空，等待重新打包后仅展示入口给用户亲操作，不重复个人读取或在线规划。


runtime补齐Calendar两官方用途plist键并离线验收，binary301f/source198dde保持，tools agent.py3afe5952；receipt calendar-packaging-receipt.json。正常HOME唯一visible51390/58420已重开并展示Android背景入口，实际图calendar-packaged-entry.png已查看；保持给用户重新亲点授权，尚未验个人连接成功。Agent未代Approve/OS许可/choices/select/读data/规划。


日历列表渲染fix main2506f383/source ddea1379/binary56fd343d封包后，正常已授权HOME唯一visible79292/53163重开。rail_e2e仅重放用户已请求列表按钮，真实返回12个日历、selection_needed，Android选择区当前3整行+1部分行按钮可见，可滚动；未代选具体日历/读events/新权限/规划。保持选择页供用户。脱敏safe receipt calendar-list-fixed-safe.json，私有截图calendar-list-fixed-private.png只root查看，不在聊天/共享文档记录个人calendar名称/id。
