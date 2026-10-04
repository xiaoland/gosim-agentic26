# Navigation 事实与计算

read_calendar/read_notes 是本应用的模拟日历、机票笔记，返回原文、记录ID、来源与时间，不能当真实个人资料。read_location 按配置返回设备或明确模拟位置，并取得实际城市依据。

set_constraints 关联实际 event_id/note_id 及逐字原文 citations；minutes/budget_cents 沿用用户明确数字条件。search_places 搜索真实高德地点但不采用；adopt_destination 使用返回的 poi_id，不编造坐标或航站楼。没有用户明确指定机场时，采用的地点是推断，需要说清依据。

query_transit/query_driving 取得实际起终点交通。compare_routes 计算当前全部候选时间、费用与原截止是否成立；只说明已查范围，不证明已查遍所有路线。费用、候车、接驳未知不等于零。路线ID、真实分段、费用与来源均在 facts.routes 中。用户原始分钟数自 received_at 起算，工具和交互耗时都算在内。

confirm_trip 必须先有用户明确确认；保存前重新检查原截止、预算、来源并实际写入读回。查看不是确认，确认不是已开始导航。工具缺少数据或失败会返回实际错误，可以选择补充工具、澄清或结束本轮；没有固定执行顺序。
