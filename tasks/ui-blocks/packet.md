# Agent增量DSL区块

状态：2026-10-06，实现、必要隔离验收与最终封装完成，待用户体验。

## 目标与授权

用户提出“允许 render_ui 一次提交一个/多个区块”，并确认compare_routes、get_route、extend_route无需调整。各区块仍由Agent编写任意Makepad／Splash DSL；可按需求渐进提交、追加或替换指定区块，保留其它区块和本轮详情交互状态。前述总结论、解释、方案卡片、建议和详情页作为呈现内容，不将五个名字或数量写成宿主限制。

本次授权包括必要渲染工具、挂载与事件衔接、技能和定向验证，不改路线工具，不引入预制业务卡片、固定业务workflow、第二模型循环或内容validator。混合探索与先计划的目标讨论归[前序任务](../agent-performance/packet.md)，本次不顺带改变查询编排。

## 当前事实与责任

当前0.11.5的render_ui(source)替换整稿；父应用提供有限高度、滚动、facts／revision、子VM事件缓冲，地图槽通过同一个generated子实例查控件。整稿更新会清地图和子实例状态。不能仅将区块字符串合成整稿重挂载，却声称其它块状态保留。

UI稳定owner负责main.splash、native_ui及必要smoke：先核实际Splash／View能力，选择最小可增量挂载方案，明确旧整稿兼容、跨块详情切换、地图控件寻址、事实更新和块级诊断。Advisor处理隔离与布局的实质取舍，根整合文档、版本和提交；native最终一次封装。共享repo不回撤其它改动。

## 实现决定

采用稳定容器和每块独立Splash。新blocks参数按任意id追加或替换；旧source继续作为单块整文档替换，清空其它块。详情用通用覆盖层保留列表滚动，不固定五个槽名或数量。事件携块id与修订号，地图以块id和控件id共同定位；只替换指定块的地图和诊断。父层每个事实修订只生成一次快照，再复用于各块。

View.render会重建同名子控件，不能作为保状态机制。现有render_style走ScriptReapply。Android模式隔离探针确认追加第二独立Splash后，旧块输入与本地Label保持；旧源码中的startup timer没有再次覆盖本地Label，说明顶层代码未重跑。普通块采用Fit自然高度和外层连续滚动，overlay采用有限视口与独立滚动。复用现有原生入口，不增加Rust容器或共享VM动态执行框架。

## 验证与证据边界

macOS arm64宿主Android模式的十二项定向检查通过，覆盖追加保输入／本地状态且旧块不重跑、自然高度、独立VM诊断、仅指定块替换、实际按钮打开／返回详情、同名地图在不同块独立加载、单块失败诊断和修正、旧revision事件、新查询清空及旧source兼容。地图使用实际Image实例和合成PNG，本轮模型和供应商请求均为零，不声称新增交互相机或在线规划验收。该组主源码摘要为af2ead0c7f5f5c6df07892f6e22364a08d5a63eb4dcc97b0edcdb9745fd9edbd。

根查看实际截图后发现详情滚到底时绘制越出视口、覆盖固定shell；十二项状态检查没有捕获像素越界。最终补上有限容器的clip_x／clip_y，并将偏移几何读取放到既有facts几何入口缓存。只追加四项几何／返回检查，确认输入和查询位置不变、详情起点在查询按钮下、返回列表坐标和本地输入保持；根已查看最终到底截图。两处更正各自贡献未再单独区分。最终主源码摘要为66a169a77fe295bb3397a093a88a4b89d7fe92452fe00ee87c9eeb212ec01b14，不将前组十二项声称为最终源码全部重跑。

安全报告在ignored build/research/ui-blocks/result-safe.json；两组实际报告分别为build/smoke/navigation-harness-3fq28ixa/report.json与build/smoke/navigation-harness-swzj0jq3/report.json。封装入口为build/research/ui-blocks/final-package/result-safe.json，中间稿已暂停，新摘要验证取代它。自有测试实例关闭，未操作用户实例。

## 接续与边界

每个区块有独立脚本变量，通过snapshot与父事件交互，不共享VM变量。接口不提供删除／重排序，已存在块的普通／overlay位置保持，显式位置变更返回具体错误。源码执行成功不是用户任务完成，也未通过新M3样本证明模型稳定采用区块或完整呈现。三个路线工具和查询编排未改。

根已核最终封装报告：make check／agent-build／agent-doctor通过，十文件嵌入与实际挂载逐字节一致；source2cd7e87c…、runtime278ce8e7…、binarye5e3e08b…，自有实例已关闭，宿主覆盖锁未改。可用make agent-dev重启体验0.11.6；不替用户操作现有实例。推送、签名、发布或赛事提交不在本次授权范围。
