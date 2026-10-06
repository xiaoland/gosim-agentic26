# 开发诊断与可观测性

状态：2026-10-06，0.10.0诊断链实现与封装已完成；实际开发记录随后耗尽宿主文件数配额，0.11.1存储与读取修复由[查询交付任务](../query-delivery/packet.md)维护。下述0.10.0证据不证明长时间记录可用。

## 目标与授权

用户说：“我看到你说‘无法取得这轮生成前的完整模型消息’，我建议你优先改进软件的可观测性、可诊断性”。授权必要应用诊断、开发工具、验证与说明更新。地图缺失调查归[查询交付任务](../query-delivery/packet.md)，用户已否决宿主保底地图；改善Agent UIUX仍是后续目标。

要回答：某轮模型实际收到哪些messages/tools/viewport，返回什么，调用哪些技能及工具，各call_id参数与结果，生成哪份源码、有哪些原生诊断／本地事件／地图请求状态，以及等待或失败发生在dispatch、HTTP、模型消息还是工具阶段。记录实际事件，不用事后UI几何推测先前输入。

只开发态诊断，不读取轨迹恢复行程或补入下一轮上下文；正式应用默认关闭。日志属于私有ignored jail／build，不进bundle或Git，不落凭据。不要向模型新增诊断提示、加入地图检查器／强制循环或宿主保底。诊断写入失败不能卡业务；不每100ms重复记录，不引入通用日志平台。

## 责任与当前事实

UI稳定owner负责bundle/main.splash记录入口与最小Android验证；native稳定owner负责tools/agent.py开发配置、读取导出、必要Makefile包装；根负责设计判断、packet／README／architecture／版本与整合。共享格式、目录与开关由两owner直接协调，不改对方文件。advisor处理身份关联与读取选择判断，不作代码review。

旧Android style重执行产生过多VM observer竞写同safe文件，run_id在新VM重置。旧agent-run文件还在jail但与当前运行不符，不能当当轮记录。现正式界面只读树没有完整模型内存入口。需要实例＋运行＋事件身份，精确冻结实际请求body和响应，读取工具不能误取旧运行；锁定脚本没有UUID／随机VM身份接口，fs读写是同步入口。采用启动器session UUID＋同一UI线程无让出的初始化序号；计数领取失败关闭记录，不能默认为1。每个实例独立事件文件、seq和status，导出合并为JSONL。开发态固定外壳透明1px标记用于唯一有效可见实例选择，多标记报歧义，不按文件时间猜测。advisor认可这一最小实现，仍需实际重建与snap验证。

## 计划与完成依据

先核实FS写／append、现诊断导出与精确key处理，确定启用／身份／记录契约；沿真实工具循环记录不可变请求与响应及执行事件。验证开发开关、生效模型上下文、call_id对应、当前实例选择、日志故障不阻断任务、凭据不落及正式默认关闭。用最小合成模型与真实原生流程，必要一轮真正任务用于证明记录能回答地图案例；不盲目抽样，未验证不假称普遍可靠。

当前无待用户审批事项，日志不是业务持久化；原始私有记录保存本机忽略目录，公开说明只保留事实与使用方法。

## 验证恢复点

导出包装器隔离契约检查已通过，证据为 `build/research/dev-trace/wrapper-test/result-safe.json`：当前标记选择、旧实例排除、序列缺失与读取期间切换、初始化失败、生成内容同名标记拒读、私有导出权限及精确凭据检查。无服务调用。

最终应用源码SHA为 `78c6f3dc087ab81c002fbe7bac30aed8055d99e07f36436d7ccd98e88fb132aa`。macOS arm64宿主 Android 模式7项定向检查通过，证据为 `build/smoke/navigation-harness-jmi8gl41/report.json`，根已查看实际 `trace-android.png`。初始化必须一次主动安装新VM身份，后续旧VM只更新与自己身份匹配的标记；不能只依赖constructor默认文字，因为style preserve可能保留旧值。两个独立实例中普通snap与reader采用实际可见vm-2，编号大小不是选择依据。透明Label需要padding:0和微型字型才有正面积。

最终证据入口为 `build/research/development-trace/result-safe.json`。检查覆盖不可变快照、call_id对应、原生render结果、精确凭据移除、写失败仍能完成新查询、默认关闭，以及相同read_location工具在trace开／关均完成且无budget错误。导出包装器最终18项隔离检查还覆盖故意不可读事件文件的部分导出、同启动器host.log私有权限与凭据检查，以及历史记录不拼接当前日志。

仅做了一轮正常真实M3样本，使用明确demo起点而非GPS，源码为 `149972874cd30195d86ec6336b5d4bdca054b269740703645fd4a66ba89047b8`。记录有1准备正文、1派发、1HTTP200；实际消息2条、工具11个，视口388×662。模型回复选择read_location、read_notes、read_calendar，实际执行停在read_location；宿主main660报告script time budget exceeded，没有tool_result、read_skill或render_ui，不能称导航成功。原现场marker仍沿用vm-1，证据明确选择vm-2导出；最终同源检查验证修正后的current选择。没有为此再抽样M3。

现场fs close出现267／318ms UI-hang，但不足区分trace写入与demo读取原因；开关对照均完成也不能证明现场预算缺陷已修复。原生硬中止只能从同启动器host.log诊断，不能伪造应用错误事件。预算失败与Agent地图省略仍由查询交付任务接续，本任务不扩为性能排查或地图质量验证。所有验收自有实例已关闭。

最终封装证据为 `build/research/development-trace/final-package/result-safe.json`，根已读取。check／build／doctor通过，10文件实际挂载字节一致，技能材料化一致，自有实例已关闭，未修改宿主补丁或锁文件。source SHA为 `7126e11c207ef7fa19b228455f9ec6e7706f71d27b820536f7f3c239b79b765b`，runtime BLAKE3为 `008697e6987df73b7b8929c418f276090039b31fc3d48dde11c4bf70493e74bf`。包核对不替代导航验收；本任务完成，预算错误与地图UIUX继续由查询交付任务维护。
