# 混合路线搜索与打车价格

状态：2026-10-06，0.11.0工具实现、真实服务验证与最终包核对完成；地图呈现优化继续暂停。

## 目标与授权

用户要求“接入滴滴打车/腾讯出行进行打车询价（目前打车估价都是费用未知……可以先行调研一下）”“实现真正的‘混合’、‘尽一切可能’，而不只是让高德地图给出点到点的规划”。授权相关调查、必要实现、验证和说明更新；先核未知费用是否解析或权限问题，不把高德估算称滴滴实际报价。不把‘今天截止’当已核官方规则，独立核对。

保留OctoScript应用、M3自主工具编排、确定性费用与路径计算、无业务持久化／澄清、Android模式验收；地图UI暂停。没有凭据／合作接口的能力不得冒称完成，不增加固定业务workflow、预制UI或模型上限。原始API响应、日志、定位与key只保存本机忽略目录；不动用户实例，不推送或提交赛事。

## 责任和决策

UI稳定owner负责main.splash、navigation_data技能及相关smoke实现／验证；native稳定owner负责高德费用响应、滴滴／腾讯官方可接入接口调查、隔离API实验与最终包核对；advisor负责混合图模型与搜索取舍判断；根负责协调、方案采用、packet、长期知识和元数据。其它修改保留。先通过源代码和官方文档确认价格字段，再以公开端点实际响应判别，不泄漏.env。

候选搜索应能主动选择真实换乘点组合公共交通和局部打车，不仅转述供应商OD列表；保持每段实际几何、时间、完整费用与来源，未知不等于零。‘尽可能’以已查询图和覆盖范围说明，不虚构现实全局穷尽与最优。计费应按完整一次叫车行程报价，不能把全程费用线性按距离拆分，公共交通截段也不能任意平分票价。

## 验收依据与恢复点

待核：v5 driving taxi_cost字段与路径数量关系、show_fields参数、v3/v5返回费用单位与权限；滴滴／腾讯是否有应用可用报价而非跳转／叫车接口；现有规划器是否只调用高德OD策略。确定性测试应覆盖真正接驳候选生成、未知价格、重复费用／断开段、预算及期限；一个真实路线实验说明范围与结果。通过后做最小Android交付与同源最终封装，不盲抽M3或扩大UI验收。

当前无需用户审批；如服务需申请合作账号，先落实其它已授权部分后说明具体缺失的服务与凭据种类。

## 采用的求解接口

已采纳advisor建议：按需扩展通用路线前缀，不做全站对一次枚举，也不把能力锁为首末接驳。节点来自本轮真实OD、公交站／入口和地点搜索结果；边来自针对实际两端、模式与出发时间取得的完整行程。extend_route由确定性代码计算下一段出发时刻、查询与连接、累加完整费用并产生前缀或到目的地的完整候选；Agent自主选择节点与模式，可组成打车→公交、公交→打车、两端打车和中段打车。公交边重新查整个对应区间，不能裁切全程票价。无需LLM计算路线或价钱。

费用、期限、衔接分别表达满足／违反／未知；费用未全获时报告已知小计／下界，不算零。未知候车时保留行驶估值并计算还可用于候车的时间余量，不能声称到达保证；后续公交按明确最早到站场景查，实际班次仍可能受未知等待影响。现单一feasible保留兼容，但不能让它掩盖真实估值和可比较候选。

## 已核费用事实与外部条件

native以公开深圳市民中心→宝安机场实测：v5 strategy32有3条path但route.taxi_cost=92元；v5 strategy0单path、v3 strategy0也为92元。当前paths.len()==1才读取价格，导致多路径查询主动丢弃可用route级估价；不是本次key未开计价。采用单path请求绑定估价，不把route级价当每条路线的独立报价。safe证据在 `build/research/taxi-pricing/result-safe.json`，根已读取。

滴滴正式MCP可用个人账号激活key调用taxi_estimate，sandbox为Mock；腾讯出行MCP需要独立应用key。首选滴滴，已请用户在.env配置DIDI_MCP_KEY，不在聊天发密钥。native接续optional配置、secret处理和MCP精确协议／schema调查，main仍归UI owner；不等待key阻塞高德价格修复和混合工具。公交transit_fee官方称方案总花费，不能在未核混合覆盖范围时重复加出租车费用。

赛事官方仓库当前赛程仍写初赛10/4、复赛10/9 23:59、10/6公布晋级，未见文件延期；create官网抓取没有正文，无法据此确认用户所说今日提交期限。此不阻塞已授权开发，不据推测改变用户目标或替用户提交。

## 实际实施与证据

9项确定性原生检查通过，`build/smoke/navigation-harness-i8kkdb3_/report.json`，根已读取；模式为桌面，使用合成数据，不称Android或在线验收。覆盖完整三leg金额只相加一次、未知费用小计、未知等待与可比价格、断段、独立预算／期限、原prefix不受后续扩展修改、实际出租车首末几何与工具查询时刻。

实际工具链证据为 `build/research/mixed-routing/result-safe.json`，根已读取。macOS arm64宿主Android模式，非GPS、无M3，公开POI与供应商完整区间实际查询。原市民中心POI与道路起点约76米连接缺口，出租车／步行结果均不能填零补齐；另明确道路测试起点取得taxi 16元／611秒、transit 7元／4797秒、walk 0元／1秒，已查部分累计23元，超40分钟。机场POI末段仍缺连接，completed_candidates=0，不能称已完整抵达或完整自主规划。保留实际pickup／arrival节点供继续步行查询，未偷偷改用户起终点。

该阶段预算中止来自fixture同入口文件准备／探针再inline调用的负担；隔离真实产品dispatch后正常取得路段。宿主仍为64ms墙钟且同步native I/O计入；旧267／318ms阻塞原因尚未证明，未提高或取消预算。

正式滴滴四请求tools/list、maps_textsearch×2、taxi_estimate全部HTTP200 JSON，无session／无需初始化，7种车型返回49–258元。`build/research/taxi-pricing/didi-result-safe.json`和`didi-route-safe.json`根已读取，原响应私有保存，未下单。端点被提供方调整，自身几何958点；distanceKm和eta为字符串，eta没有单位后缀，官方询价参考未明确单位，不将其硬转分钟。应用薄adapter实际Android地点搜索与询价已完成；报价关联以定向检查验证，未把本次公开OD报价冒称用于该真实混合尝试。

报价关联已采纳advisor：按两端实际name／city／address和入口／航站楼语义作条件性关联，未知CRS不阻断费用比较，不篡改几何／认证衔接。所选priceText替换该taxi leg高德估价并确定性重算前缀／总价，不重复加价；优惠独立保留，不默认为可用。未核等待、上下车地点对应假设、未来价格变化继续明示。无需另建滴滴路段图。

SDK复用补充：官方Android／JS SDK存在，但当前OctoScript/macOS Android显示模式没有已验证SDK桥；锁定WebReader明确无页面→应用桥，不能仅从WebView源码存在宣称可调用JS SDK。采纳advisor本轮保官方REST最薄请求和必要归一化／业务组合；暂不迁高德MCP，其文档未证明完整时刻／分段费用覆盖，打车能力描述为唤端链接。地图UI恢复时优先验证SDK可嵌入路径，不自行扩展地图交互。

## 完成依据与后续边界

最终main为 `f8fe4d0f3cc5ce12a0e15972a6d155df8ca51b408c25a16861d2328eedb6e9ff`，navigation_data技能为 `3aa4e4c3779ce75f7113746d00b6441591581857560b98d604e517ed8135bec3`。最新10项定向原生检查在桌面通过：`build/smoke/navigation-harness-c8kw0qot/report.json`，根已读；增加报价替换而非叠加、派生2700分／原3000分不变、连接未知仍保留、不完整前缀全程价未知。检查后仅将既有tool result中的滴滴集合加入facts，未追加服务。实际Android应用adapter搜索分别7／9地点并取得7车型报价，`build/research/mixed-routing/didi-adapter-result-safe.json`根已读。

compare_routes／facts现在保留mixed_attempts与真实未到D原因、连接缺口和已知小计，不把无完整候选简化为没有任何结果。真实高德尝试与当前报价关联分别验证，不声称真实报价已经附入这条23元尝试或已完成用户40分钟任务。根查看android-tools.png，图片为早期fixture缺起终点状态，不能作为成功界面截图或新增UI验收；真实工具证据以trace和safe为准。所有自有实例已关闭，用户实例未动。

最终包证据 `build/research/mixed-routing/final-package/result-safe.json` 根已读取：check／build／doctor通过，10文件实际挂载逐字节一致，两技能材料化一致，decoded包7288108B。source SHA为 `b9c52a97349137750ac9a41a7edf15f4dc8d21b0485aff379240bb662077b211`，runtime BLAKE3为 `c85943209755f8ffa1150cf040298c9cf088a9ad3cd406b15e538f7f7e207d34`；宿主patch／lock未变。

本任务实现完成，无待用户批准项。尚未做新增M3自主全流程验收，不能保证Agent每次充分扩图；现实全局最优、候车、原始机场POI连接和地图UI均未被证明解决。既有预算缺陷仍归查询交付任务，SDK可嵌入路径随地图恢复开发再验证。README／architecture／sources已回流当前接口、意义和事实边界。
