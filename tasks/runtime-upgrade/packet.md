# 官方宿主兼容与初赛反馈落实

状态：2026-10-10，落实 [App Hub #116 的赛事反馈](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/116#issuecomment-6077995438)。评审版本为 v0.13.0／702ea6c，初赛结果入围，65/100；这不等于商店上架或完整业务验收。

## 目标与授权

用户明确要求“我们先落实其给出的改进建议吧”，授权三项必要的实现、实验、验证与文档：修复官方原版 card-host 首屏错误；将 MiniMax 直连迁移到宿主 model 服务；补充无补丁环境下的实际降级演示。延续自主 commit 授权；本轮先完成可审阅的改进，不自动重打已发布标签或替赛事方接受结果。既有 M3 在线验证和隔离模拟位置授权适用。

保留模型自主 function-calling loop、工具结果和完整运行证据，不改为固定 workflow，不恢复旧查询、不新增问答或业务 fallback。官方缺少原生能力时呈现准确边界；不能用 patched host 的通过冒称 stock 兼容。密钥与原始日志保持私有，仅清理本任务实例。

## 当前事实与责任

- v0.13.0 已公开，Release 和 Hub #116 已提交；赛事方在 2026-10-09 报告官方 card-host 首屏 main.splash 约2428行触发 empty-stack。
- stock_startup 已在官方 App Hub 7b36c8af 原版 card-host 复现启动rect调用导致empty-stack，并完成最小能力门修复：main SHA72d3c8a9。真实390×844首屏、禁用点击与回车回归通过；patched Android 9项合成回归通过。main已交host_model接力，永久检查tools/test_stock_startup.py用于最终再验证。
- host_model 已核最新 OctoSense 40ca21da 仍仅有 model.complete one-shot，不能透传 messages/tools；已在同一 ModelHost 内新增窄 model.chat，复用 profile/transport/凭据与账本，并完成应用模型传输迁移。现有 complete 保持；扩展尚待上游接纳。
- stock_demo 已完成29.63秒无补丁补充视频及核验记录，不覆盖已发布96秒演示。
- root 维护任务与长期文档、协调接口和集成验收，并依据最终 stock 画面制作降级演示。当前工作区开始时干净。

以前的源码、宿主、路线与发布证据移到 [初赛调查与交付记录](preliminary-evidence.md)，其中“最新”等时间词仅适用于当时版本，不作为此次运行结论。

## 完成依据与下一步

1. 使用明确SHA、无本地补丁的官方 card-host 加载真实 bundle，实际可见首屏；缺能力入口不再触发原生错误，界面准确说明剩余依赖。保留截图和宿主日志。
2. 模型迁移通过真实 M3 的 function call → 本地工具结果 → 继续模型闭环；历史、取消与失败处理保持，应用不再读取或发送 MiniMax key。若官方服务存在缺口，先依据实际契约裁决最小路径。
3. 官方card-host手机视口下记录无补丁首屏与降级操作（不冒称Android模式），更新演示／README／工具链／架构的实际范围；本地包检查和已有受影响回归通过。

下一步：三项反馈改动已完成；root完成最终封包、构建核对与提交。独立的生成UI残余保留在本任务接续，不声称完整任务验收通过。

已采用 advisor 判断：直接把历史塞进 model.complete 的 input 会改变 function-calling 语义，不能作为迁移。新增 chat 必须复用同一宿主授权和 ledger；one-shot 的 schema、URL、32KiB输入／16KiB输出约束不成为 chat 内容转换。当前取消继续丢弃迟到回调，不声称远端HTTP取消。历史实际14轮消耗413,501 tokens，默认100k/day不足；用户已允许充足M3真实验收，本项目隔离开发配置可通过现有宿主额度入口调整，保留历史usage，不改全局默认或绕过账本。root采用tokens_per_day=1,000,000，per_minute=20／calls_per_day=100，仅本项目隔离开发Navigation覆盖，具体最终行为回流工具链说明。

首屏证据：build/smoke/stock-startup-o575cvuf/report.json；patched回归：build/smoke/navigation-harness-ru0lqrmv/report.json。root已读取同binary前后错误对照并查看真实first.png；仅证明首屏降级与保留patched路径，非完整在线任务。

无补丁补充视频已完成：demo/Navigation-stock-demo.mp4（29.63秒、中文旁白/字幕、真实截图剪辑），采集main72d3c8a9、官方card-host7b36c8af，非Android模式。媒体owner解码与音轨检查通过，root查看第二镜头关键帧；仅演示首屏/缺能力，未覆盖后来模型迁移。公开evidence脱除私有路径。

root从两份既有私有完整trace仅统计model_dispatch时间，14请求运行最大7次／60秒，11请求运行最大11次／60秒；因此保留默认6/min会造成已知回归，将仅隔离开发应用覆盖设为20/min、100/day、1,000,000 tokens/day。不是删除宿主准入，使用计数保持，应用不能设置额度。

模型迁移进展：main b607ed3a；真实M3原生两轮工具闭环通过（2次、917tokens），实际host.request/registry/agent_pump/tool_result保留call_id；Rust两项chat集成与19项原complete回归、launcher凭据归属/额度保计数、11项trace读取归档检查通过。实际产品迟到host回调隔离检查通过。后续完整Navigation在线demo结果见下；不作为业务完成声明。

迁移后正式单次在线demo已结束：17次请求、38工具、491,392 tokens、最大请求237,579 bytes；完整trace316事件连续，无model service／rate／budget错误，自有实例关闭。最终画面空白（root已看截图），与rendered=true不一致，离线归因见下。不得把该轮记为完整UI通过。模型两轮、迟到回调、Rust/trace回归可独立采用。

root最终stock复跑通过：build/smoke/stock-startup-fdo1h576/report.json；make check通过（含model能力、仅高德和滴滴应用主机）。盖摘要后doctor提示需重新agent-build，为正常封包顺序，待最终源码/版本确定后build→doctor。

离线归因已完成：build/research/host-model/render-replay-visible/保留原稿、真实回放和对照截图。summary/explanation/routes均complete、visible且无原生诊断，但实际高度为0；仅将原稿顶层ScrollYView改为内容自适应View的隔离实验恢复654高路线卡片。详情事件另引用不存在的widget ID。未修改生产生成稿、未添加自动布局fallback、未追加M3调用；该问题属于生成布局与渲染成功判据的接续修复，不属于模型消息丢失。

当前应用版本更新为0.14.0，区别于已发布初赛0.13.0；不重打旧标签或覆盖旧Release。

最终封包：0.14.0 的 make check、make agent-build、make agent-doctor 均通过。构建输出的应用包源码摘要为fd5b88974dc4c0b38bf5560aac562adda465e040dbfcb24f0596450b96c87284；main源码仍b607ed3a，模型迁移后stock检查无需因仅版本/摘要变化重复。日志归build/research/host-model/final-{check,build,doctor}.log。三项反馈的本仓库改动交付完成；上游接纳与生成UI零高/错误控件引用是剩余事项，尚未向赛事方声称验收通过。
