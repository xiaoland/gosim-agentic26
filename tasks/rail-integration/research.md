# 铁路与城际来源调查

本文件保存研究阶段的来源、证据及合同判断。当前实现与验收状态归[任务包](packet.md)；研究时的建议不代表当前实现。

## 高德与OTA补充结论

用户补充：“也许其实高德地图、携程旅行、TripAdvisor或者其它OTA有提供相关的查询能力”。rail_model接续高德文档与低频真实请求，rail_sources接续OTA正式入口；没有登录OTA、申请账号或执行第三方CLI。

| 来源 | 证据与适用范围 | 未证实部分 |
| --- | --- | --- |
| [高德v5](https://lbs.amap.com/api/webservice/guide/api/newroute)／[v3](https://lbs.amap.com/api/webservice/guide/api/direction) | 六次官方请求成功。广州南→深圳北及反向路线含番禺、琶洲、深圳机场、竹料等城际，作为bus.buslines返回，已有站序、耗时和折线；文档另定义railway车次、站点时刻及席别价格 | 本次railway为空或缺失；没有取得国铁运行实例、实时余票。首末班时刻不能冒充本次列车时刻，总方案费用不能拆作铁路票价 |
| [途牛铁路MCP](https://open.tuniu.com/mcp/docs/apidoc/mcp/trainMCP.html) | searchLowestPriceTrain与queryTrainDetail可独立查询，文档有实际上下站、完整出到日期时间、逐席别价格及余票。个人会员手机号关联；API Key或正式OAuth接入，不必自己部署铁路查询服务器 | 尚未授权调用。价格单位、99余票语义、缓存时效和广东城际覆盖需实测；平台配额5RPM、50RPD，不能大规模展开候选矩阵 |
| [飞猪FlyAI官方列车工具](https://github.com/alibaba-flyai/flyai-skill/blob/86fe2cc3e25464d0e0bd6a769b27b5f9f3b04128/skills/flyai/references/search-train.md) | search-train支持城市／车站、日期、直达／中转、车次与席别过滤；示例含完整分段日期时间、人民币价格与跳转链接 | 隔离实跑已成功，但返回粗价且quantity为空；未发现可用余票字段，不能证明全部班次或逐席别库存；README无Key启动与官网推荐正式Key应分别验证 |
| [Trip.com Developers](https://developer.trip.com/?lang=en-US) | 官方列出Train Tickets开发者分类 | 详情需平台分配账号；个人自助接入、公开schema、中国铁路覆盖未确认 |
| [去哪儿开放平台](https://open.qunar.com/data/detail/open) | 官方确认铁路搜索等标准API | 需单独协议、运营申请和联调，没有即时个人Key与公开铁路schema证据 |
| [TripAdvisor Terra](https://docs.terra.tripadvisor.com/docs/endpoints-overview) | 公开接口主要为地点、评论、照片与推荐 | 未找到铁路班次端点，不作为本次铁路来源；不据此断言私有合作接口不存在 |

高德净化请求及文档副本归build/research/rail-integration/amap，OTA官方材料归build/research/rail-integration/ota。高德还暴露独立费用缺陷：route_cents只接受最多两位小数，本次真实transit_fee为39.000000／28.000000，会转成未知金额；当时仅记录；后续实现已修复，当前进度见packet。源码尚未解析有意义railway，但不能将这次缺少铁路班次归咎于漏解析，因为没有取得该返回样本。

途牛[正式MCP授权](https://open.tuniu.com/mcp/docs/guide/mcp-auth.html)支持HTTPS Streamable HTTP、OAuth 2.1及DCR/CIMD，火车入口为https://openapi.tuniu.cn/hybrid/mcp/train；实际tools/list是schema准据。API Key与推荐OAuth入口不能混作同一个认证方案。[平台配额](https://open.tuniu.com/mcp/docs/guide/ratelimit.html)属于供应商约束，不是重新给Navigation增加本机模型上限。

## 数据入口结论（2026-10-11）

首个可验证来源是12306官网的匿名网页查询。本次init动态取得leftTicket/queryG，查询2026-10-12上海虹桥→南京南返回340条记录；随后同一K528样本停站和票价接口成功，停站22条，硬座50.5元、硬卧96.5元、软卧146.5元。没有账号、API key或验证码，TLS正常验证。原始响应与请求元数据归build/research/rail-integration/sources/live；这仅证明本日低频访问可用，不证明长期可用性、完整预售窗或获得第三方服务授权。

未找到面向普通第三方开发者的12306公开查询API文档、Key申请入口或SLA；不能据此断言合作接口不存在。公开网页端点、社区MCP封装、商业API是三种不同来源，不把MCP包装当作铁路官方授权。

| 入口 | 已核能力与用途 | 当前判断 |
| --- | --- | --- |
| [12306官方网页](https://kyfw.12306.cn/otn/leftTicket/init) | 真实班次、余票；停站及席别票价补查，本轮匿名成功 | 数据合同对照来源，接口路径从网页动态取得，不硬编码某次query后缀 |
| [Joooook/12306-mcp](https://github.com/Joooook/12306-mcp/blob/ff6439da6f63d7d72181abea4568abd69878c600/src/index.ts) | MIT、0.3.10，commit ff6439da6f63d7d72181abea4568abd69878c600；车站、余票、停站和中转，Node stdio/HTTP | 社区复用备选；不能盲用其start_date，源码把列车始发日当区间日期，跨日样本有风险；本轮未执行该包 |
| [drfccv/mcp-server-12306](https://github.com/drfccv/mcp-server-12306/blob/f6865c077cfd51eb90021cc75aff33fad75ac3d5/src/mcp_12306/services/ticket_service.py) | MIT、0.5.0.post20260930，commit f6865c077cfd51eb90021cc75aff33fad75ac3d5；查询、公布票价、停站、中转 | 当前固定queryI而官网使用queryG，HTTP verify=False；不直接采用；公布票价也不当作当前成交价 |
| [聚合22](https://www.juhe.cn/docs/api/id/22)／[817](https://www.juhe.cn/docs/api/id/817) | 商业第三方铁路查询／票务API产品 | 若匿名网页来源不可持续，再核账号、报价和合同；本轮未申请或调用，不称12306官方API |
| [广东城际出行助手](https://iro-traa.gzmtr.com/traa.html) | 官方页面有route／price／carriage JSON调用，路线、时间、换乘及票价结构 | 直接查询返回非法来源，普通iab访问亦转禁止访问；没有取得成功班次JSON，不作为已可接通数据源 |

12306实测暴露两项数据合同问题：输入AOH→NKH却包含IMH→NJH等同城站组合，必须看每条实际上下车站码；K528的列车始发日20261011与乘车日20261012不同，两者独立保存。票价编码、席别码与人民币单位应由适配层处理，Agent不解析管道字段或手算金额。余票是查询时观察值，不是已购票或保留席位。没有统一缓存TTL证据，展示和再核验应保留抓取时间及来源。

## 铁路与城际的覆盖语义

运营方、车次字母和票制不能互相代替。固定班次、当日一次有效票和乘车码可能并存；票不绑定某班次也不代表列车没有实际时刻。

| 服务 | 已核信息 | 建模影响 |
| --- | --- | --- |
| 国铁高铁／动车 | 12306按日期、上下站、车次与席别查询；定期／计次票另有规则 | 运行实例固定，票价／余票与登乘状态分开 |
| 广深城际 | 广州白云—深圳部分始发终到C字头列车实施当日一次有效；高峰可按当次组织 | 查询具体班次，票务规则另存，不把“公交化”当无限制登乘 |
| 广东城际 | 广惠、广肇、广清、广州东环、琶莲等有12306与城际乘车码双票务，交路与支付渠道不同 | 站站停、大站快车、特快分别查询；价格依据保留票务渠道 |
| 穗深及机场贯通交路 | 穗深于2026年1月28日由广东城际接管；7月17日上线新的多元支付；7月31日竹料—新塘南开通，串联白云／深圳机场 | 值得作为机场接驳候选，但当前官方机器查询不可用，不能用旧运营与票制资料代替实时班次 |

来源：[深圳交运局票制公告](https://www.sz.gov.cn/cn/xxgk/bmtx/content/post_11941722.html)、[广东交通厅城际说明](https://td.gd.gov.cn/gkmlpt/content/4/4791/post_4791025.html?jump=true)、[广州政府接管报道](https://www.gz.gov.cn/zwfw/zxfw/jtfw/content/post_10679383.html)、[运营方通讯员双票务报道](https://ep.ycwb.com/epaper/xkb/html/2026-07/17/content_1506_759391.htm)、[广州交通局贯通公告](https://jtj.gz.gov.cn/gkmlpt/content/10/10947/post_10947514.html)。网页接口拒绝与普通浏览器结果归build/research/rail-integration/intercity，未尝试改变身份或绕过限制。该来源当前不能验证晚点、取消、余票、实际拥挤度、站台保证或机场站到航站楼耗时。

## 研究时识别的实现缺口与建议合同

现有统一Route、整数分金额、不可变派生、已有小计与未知项、守护状态及地图目录可以复用。铁路结果继续进入同一Route、同一候选列表和同一Agent loop，不另建铁路聊天或展示系统。

main.splash只在44行以railway对象阻止误判终点，站点注册、steps与几何均未解析铁路。当前recheck/guardian以max(now,departure)+duration重算，可能把错过的固定车次向后平移；prefix延长只核25米几何，不证明安检／站台连接。这些问题不能靠给工具加mode=rail解决。

建议先区分发现与采用两个输入合同，统一输出Route：

- search_rail_services以真实铁路站身份、乘车日期与时间窗取得service_ref、实际发到时刻、席别／票价／余票及查询依据。需要区分列车内部ID、显示车次、列车始发日和乘车区间日期，不把同城不同站合并。
- extend_route_with_rail引用本轮route_id、service_ref及选定票价／席别事实。代码检查前缀到站时间、固定发车与已知登乘条件，生成新Route；不允许模型复制或手算班次时间／价格。错过班次明确失效，不能平移；信息不足保留未知。已有walk／taxi／transit负责前后接驳。

铁路站码关联实际入口／出口POI，地图到站、站内转移与具备登乘条件分别记录。停止检票依据运营方或车站公告，不能统一捏造5／15／30分钟；12306[运输规程](https://mobile.12306.cn/otsmobile/h5/otsbussiness/info/transportationRules.html)说明提前停止检票时间在本站公告。未知安检／站内耗时可以用于形成候选，但不能宣称已经赶得上。班次前等待、实际晚点、余票和购票状态是不同事实。缺铁路几何时展示真实站点及缺失说明，不用起终点直线伪造行驶轨迹。

## 推荐接续与验收

先补一个高德国铁直达站对，核v5／v3能否返回具体班次；同时优先在隔离环境验证途牛正式查询工具，仅取得tools/list、班次搜索及详情，不开放订单工具。核完整分页、真实车站、日期、价格单位、席别和余票语义，与低频12306同日同车对照。途牛配额有限，应批量发现、只核有价值候选，不让接驳探索无限展开供应商请求。飞猪可补充结构化中转搜索，库存未知保持未知。若正式来源无法满足，再验证固定Joooook版本，并窄修跨日和站码合同，不重造12306客户端。

现有高德工具负责能提供的路线探索；只有需要其候选范围之外的站对班次枚举时，再新增search_rail_services。供应商数据进入同一Route合同，不能让Agent复制价格与固定时刻。HTTPS MCP能否被当前宿主直接消费仍需核查；CLI／stdio隔离实验不代表Android应用接通。本轮不搭通用后端或免费第三方代理。

有意义的首轮应用验收应为“真实市内接驳→具体铁路班次→到站后接驳”，比较门到门时间和全程费用。由Agent决定车站、班次和接驳，技能补铁路事实与探索知识，不规定固定查询步骤。

必要反例包括：晚到后不能平移原班次；跨日过路车日期正确；同城另一站不能替代未查询的接驳；席别价未知不记零；余票有不等于已购票；同站POI接近不等于保证换乘。广东城际则额外验证票务渠道、停站交路与最后班次，不能从“公交化”推导零等待。

研究阶段已完成，tools/rail_provider.py及四项合同测试已完成；今日广深查询251班，G6183四个席别的编码价与独立票价查询一致。参考client只用于隔离验证，不是运行时后台。尚未执行真实M3铁路端到端，也未取得广东城际官方助手成功接口响应。高德城际路线成功不代表该助手已接通。
