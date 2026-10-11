# 从瓶颈到实际查询

以下例子说明怎样形成假设，不要求固定顺序或候选数量。节点必须来自本轮工具事实。

首段替代：已有公交显示先慢速接驳到某地铁站再进入主干。可以用query_route的to_ref查起点到该站的真实node_ref，再从返回Route用extend_route查到destination；比较完整新组合，而非从原公交金额中扣去第一段。

末段替代：公交最后一段绕行，或供应商实际终点没有接上目标。可重新查origin到真实下车站，再查询taxi/walk到destination。已有incomplete Route可从其actual arrival节点继续，但一次补步行仍未接上，不能把供应商请求终点当成功；应判断入口、实际几何或其它真实节点是否能检验新的连接假设。

中段替代：原路线某段长绕行或复杂换乘。选择主干上的真实A/B节点，用transit到A、taxi/walk到B、transit到目标，各段分别查询完整方案。只使用已查段小计作探索依据；完整后才比较全程价格。工具暂不支持独立逆向后缀或重组已有legs，不能编造create_route/composite_route调用。

否定分支同样有价值：新组合确实超预算、最早场景已经超期、接驳端点不匹配、或没有比已有方案更好的证据时，保留具体工具依据。未知候车、当前打车价与未来接驳时刻不同、资料过期等限制继续随方案说明，不拿未知认证失败或成功。


## 两步累计示例

以下JSON展示参数之间的关系，不是可直接调用的真实ID。`$NODE_A`替换为本轮工具返回的接入节点node_ref；`$MODE_A`选择taxi或transit，`$MODE_B`选择walk、taxi或transit；`$FIRST_ROUTE_ID`替换为第一步成功结果中选定的Route.id。例子不规定搜索顺序或必须使用的交通方式。

query_route从起点建立新前缀：

```json
{"to_ref":"$NODE_A","mode":"$MODE_A"}
```

extend_route保留该前缀，再从它的实际终点查到目标：

```json
{"route_id":"$FIRST_ROUTE_ID","to_ref":"destination","mode":"$MODE_B"}
```

第二步返回的Route已经包含第一步与新段，时间和完整供应商费用由工具累计；不是只返回后缀。若把原整程公交Route.id放在第二步，就保留原整程并从其终点继续，不能借此替换原首段。
