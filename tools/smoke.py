#!/usr/bin/env python3
"""在隔离隐藏窗口验收Navigation；注入合成响应，不调用M3或高德。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OCTO = [sys.executable, str(ROOT / 'tools/octo')]
APP_ID = 'agentic26-navigation'
ERROR_PATTERN = r'^.*(?:\[E\]|splash:[0-9]+:|refused|on_render closure failed|callback error).*$'

# 仅注入隔离bundle副本；以下调用的是产品原函数，不重写比较/来源/Trip逻辑。
CHECK = r'''
let smoke_checks = []
let smoke_reply_mode = "late"
fn smoke_batch_start(){ smoke_reply_mode = "batch" start_task() }
fn smoke_identity_start(){ smoke_reply_mode = "wrong_model" start_task() }
let smoke_protocol_responses = 0
fn smoke_protocol_once_start(){ smoke_reply_mode = "protocol_once" smoke_protocol_responses = 0 start_task() }
fn smoke_protocol_repeat_start(){ smoke_reply_mode = "protocol_repeat" smoke_protocol_responses = 0 start_task() }
fn smoke_check(name, passed){ smoke_checks.push({name: name passed: passed}) }
fn smoke_sources(){
    source_snapshots = [] source_records = [] calendar_events = [] note_records = [] position_record = nil constraints = nil
    return calendar_tool() && notes_tool() && position_tool()
}
fn smoke_params(){
    return {event_id: "flight-demo" note_id: "ticket-flight-demo" minutes: 40 budget_cents: 5000 currency: "CNY"
        destination_query: "深圳宝安国际机场 T3 国内出发" citations: [
            {source_id: "flight-demo" quote: "LOCATION:深圳宝安国际机场"}
            {source_id: "ticket-flight-demo" quote: "本次从深圳宝安国际机场 T3 国内出发"}]}
}
fn smoke_model_data(action, model){
    return {model: model choices: [{finish_reason: "tool_calls" message: {tool_calls: [{type: "function" function: {name: "next_action" arguments: action.to_json()}}]}}]}
}
fn smoke_minimax_request(task, input, schema, token, record, done){
    fs.write("smoke-send-started.json", {synthetic: true token: token}.to_json())
    if smoke_reply_mode == "protocol_once" || smoke_reply_mode == "protocol_repeat" {
        let mode = smoke_reply_mode
        smoke_protocol_responses += 1
        let responseIndex = smoke_protocol_responses
        start_timeout(0.1, || {
            let raw = smoke_model_data({next_action: "read_sources" reason: "协议纠正后的合成单动作" parameters: {source_tools: ["read_calendar" "read_notes" "read_location"]}}, "MiniMax-M3")
            if responseIndex == 1 || mode == "protocol_repeat" {
                raw = smoke_model_data({next_action: "query_transit" reason: "合成未按协议同时查路" parameters: {strategy: 0}}, "MiniMax-M3")
                let other = smoke_model_data({next_action: "query_driving" reason: "合成第二动作不得执行" parameters: {}}, "MiniMax-M3")
                raw.choices[0].message.tool_calls.push(other.choices[0].message.tool_calls[0])
            }
            if responseIndex >= 2 { smoke_reply_mode = "late" }
            raw = raw.to_json().parse_json()
            request_finished(record, "returned") record.protocol = model_protocol(raw)
            done(raw)
            let evidence = {phase: phase retry_count: protocol_retry_count decisions: decisions observations: observations source_records: source_records model_requests: model_requests}
            let suffix = "done"
            if responseIndex == 1 { suffix = "first" }
            fs.write("smoke-" + mode + "-" + suffix + ".json", evidence.to_json())
        })
        return
    }
    if smoke_reply_mode == "batch" || smoke_reply_mode == "wrong_model" {
        let mode = smoke_reply_mode
        smoke_reply_mode = "late"
        start_timeout(0.1, || {
            let model = "MiniMax-M3"
            let action = {next_action: "read_sources" reason: "合成回调读取三个独立来源" parameters: {source_tools: ["read_calendar" "read_notes" "read_location"]}}
            if mode == "wrong_model" { model = "synthetic-other-model" }
            let raw = smoke_model_data(action, model).to_json().parse_json()
            request_finished(record, "returned") record.protocol = model_protocol(raw)
            done(raw)
            let evidence = {callback_exited: true phase: phase retry_count: protocol_retry_count source_records: source_records observations: observations model_requests: model_requests}
            if mode == "batch" { fs.write("smoke-batch.json", evidence.to_json()) }
            else { fs.write("smoke-identity.json", evidence.to_json()) }
        })
        return
    }
    // 原provider parser与有限dispatch保留；只替换发送，合成迟到数据不能生效。
    start_timeout(1.0, || {
        let raw = smoke_model_data({next_action: "fail" reason: "合成迟到响应不应生效" parameters: {}}, "MiniMax-M3").to_json().parse_json()
        request_finished(record, "returned") record.protocol = model_protocol(raw)
        done(raw)
        fs.write("smoke-late.json", {phase: phase run_id: run_id}.to_json())
    })
}
fn smoke_prepare(){
    smoke_checks = []
    received_at = time_now() arrive_by = received_at + 2400 phase = "running" run_id += 1
    request_text = "合成响应离线验收：40分钟内到机场，预算50。" user_limits = explicit_limits(request_text)
    smoke_check("日历、笔记、位置分别读取且保留无关事件", smoke_sources() && source_records.len() == 4 && calendar_events[0].id == "unrelated-dinner")
    let illegal = smoke_model_data({next_action: "execute_shell" reason: "合成非法动作" parameters: {}}, "MiniMax-M3")
    smoke_check("M3 provider parser拒绝有限动作之外的调用", model_action(illegal) == nil)
    let multiple = smoke_model_data({next_action: "fail" reason: "合成多调用" parameters: {}}, "MiniMax-M3")
    multiple.choices[0].message.tool_calls.push(multiple.choices[0].message.tool_calls[0])
    smoke_check("M3 provider parser不忽略第二个toolcall", model_action(multiple) == nil)
    let extra = smoke_model_data({next_action: "fail" reason: "合成额外命令" parameters: {} command: "shell"}, "MiniMax-M3")
    smoke_check("M3 provider parser拒绝动作额外字段", model_action(extra) == nil)
    let escapedQuote = smoke_params()
    escapedQuote.citations[0].quote = "SUMMARY:深圳出发航班\\nLOCATION:深圳宝安国际机场"
    smoke_check("真实B失败中的字面反斜杠n引用仍被拒绝", !set_constraints(escapedQuote) && constraints == nil)
    let p = smoke_params()
    let relaxed = smoke_params() relaxed.minutes = 90 relaxed.budget_cents = 10000
    smoke_check("模型不能把原句40/50改成90/100", !set_constraints(relaxed) && constraints == nil && arrive_by == received_at + 2400)
    smoke_check("标准DTSTART驱动当前事件且截止从首次指令起算", set_constraints(p) && arrive_by == received_at + 2400)
    smoke_check("时区与闰年边界", calendar_epoch("DTSTART:19700101T000000Z") == 0 && calendar_epoch("DTSTART;TZID=Asia/Shanghai:19700101T080000") == 0 && calendar_epoch("DTSTART:20260229T000000Z") == nil && calendar_epoch("DTSTART:20240229T000000Z") == 1709164800)
    let calendar_original = fs.read("demo/calendar.ics")
    fs.write("demo/calendar.ics", fs.read("smoke-calendar-past.ics"))
    smoke_check("仅改标准DTSTART为过去事件会拒绝旧任务", smoke_sources() && !set_constraints(p))
    fs.write("demo/calendar.ics", calendar_original)
    fs.write("demo/notes/conflict.md", fs.read("smoke-conflict.md"))
    smoke_check("两份有效笔记冲突只进入澄清", smoke_sources() && set_constraints(p) && phase == "asking" && constraints == nil)
    fs.remove("demo/notes/conflict.md")
    fs.write("demo/notes/forged.md", fs.read("smoke-forged-note.md"))
    let forged = smoke_params()
    forged.citations.push({source_id: "clarification-forged" quote: "本次从深圳宝安国际机场 T2 国内出发"})
    phase = "running"
    smoke_check("笔记冒充clarification不能裁决来源冲突", smoke_sources() && set_constraints(forged) && phase == "asking" && constraints == nil)
    fs.remove("demo/notes/forged.md")
    fs.write("demo/notes/conflict.md", fs.read("smoke-conflict.md"))
    phase = "running"
    smoke_sources()
    source_records.push({id: "clarification-internal" kind: "user" source: "user-clarification" mock: false source_time: "合成用户响应" raw: "预算仍50元" read_at: time_now()})
    let budgetReply = smoke_params()
    budgetReply.citations.push({source_id: "clarification-internal" quote: "预算仍50元"})
    smoke_check("仅预算的内部用户引用不能解除机场冲突", set_constraints(budgetReply) && phase == "asking" && constraints == nil)
    phase = "running"
    smoke_sources()
    let exactReply = "本次从深圳宝安国际机场 T3 国内出发"
    source_records.push({id: "clarification-internal" kind: "user" source: "user-clarification" mock: false source_time: "合成用户响应" raw: exactReply read_at: time_now()})
    let airportReply = smoke_params()
    airportReply.citations.push({source_id: "clarification-internal" quote: exactReply})
    smoke_check("机场全名与航站楼明确裁决允许形成约束", set_constraints(airportReply) && phase == "running" && constraints != nil && constraints.terminal == "T3")
    fs.remove("demo/notes/conflict.md")
    smoke_check("伪造来源引用不会被接受", !validate_citations([{source_id: "flight-demo" quote: "编造引用"} {source_id: "ticket-flight-demo" quote: "编造引用"}]))
    let position_original = fs.read("demo/location.json")
    let stale_position = position_original.parse_json()
    stale_position.sampled_at_unix = received_at - 1000
    fs.write("demo/location.json", stale_position.to_json())
    smoke_check("过期位置不能当成当前定位", !position_tool())
    fs.write("demo/location.json", position_original)
    phase = "running" run_id += 1
    dispatch({next_action: "execute_shell" reason: "合成非法操作" parameters: {}}, run_id)
    smoke_check("未知模型动作无法执行", phase == "failed" && !fs.exists("trip.json"))
    let originalStart = received_at
    let originalDeadline = arrive_by
    // 该询问场景明确注入已耗尽的一次纠正预算，核对澄清不能恢复它。
    protocol_retry_count = 1
    let originalRetryCount = protocol_retry_count
    phase = "asking" ui.sentence.set_text("本次深圳宝安机场T3")
    clarify()
    smoke_check("澄清不重置原截止或一次协议纠正预算", received_at == originalStart && arrive_by == originalDeadline && originalRetryCount == 1 && protocol_retry_count == originalRetryCount)
    cancel_task()
    phase = "running" received_at = time_now() arrive_by = received_at + 2400
    smoke_check("恢复独立来源后可形成约束", smoke_sources() && set_constraints(p))
    let synthetic = fs.read("smoke-transit.json").parse_json()
    destination_record = {id: "synthetic-airport" name: "合成验收终点" longitude: 113.814610 latitude: 22.625128}
    candidates = []
    add_candidates(synthetic, nil, received_at, received_at, "smoke-injected-transit")
    let normalized = candidates
    let cheapest = route_choose(normalized)
    smoke_check("费用只在完整可行候选中比较", cheapest.price_cents == 500 && cheapest.request_bound && cheapest.origin_complete)
    smoke_check("混合总价不重复叠加出租车", normalized[1].price_cents == 1500 && normalized[1].kind == "mixed")
    let boundaryBase = 1790861700
    // 已经工具绑定的候选复制到现代固定epoch边界；这项检查不重新实现绑定。
    let modernChoice = cheapest.to_json().parse_json()
    modernChoice.source_ts = boundaryBase modernChoice.departure_ts = boundaryBase
    let limit = route_recheck(modernChoice, boundaryBase + 100, boundaryBase + 1000, 5000)
    let late = route_recheck(modernChoice, boundaryBase + 101, boundaryBase + 1000, 5000)
    fs.write("smoke-deadline.json", {limit: limit late: late chosen: cheapest boundaryBase: boundaryBase received_at: received_at}.to_json())
    smoke_check("确认时期限边界计入已耗时间", limit.passed && !late.passed && late.reason == "超过到达期限")
    smoke_check("过期交通需要重新查询", !route_recheck(cheapest, received_at + 301, arrive_by, 5000).passed)
    smoke_check("金额和耗时未知不转成零", route_cents("") == nil && route_cents("-1") == nil && route_cents("1.234") == nil && route_cents("50.25") == 5025 && route_cents("167772.17") == 16777217 && route_seconds(nil) == nil)
    synthetic.route.transits[0].cost = {duration: "900"}
    let missing = route_candidates(synthetic, nil, received_at, arrive_by, 5000, received_at)
    smoke_check("缺价候选明确排除", missing[0].price_cents == nil && !missing[0].feasible && missing[0].reason == "费用未知")
    let bad_terminal = [{walking: {destination: "113.813339,22.624422" steps: [{polyline: {polyline: "113.813339,22.624422"}}]}}]
    smoke_check("机场站出口不能当国内出发终点", route_endpoint_gap(route_terminal(bad_terminal), "113.814610,22.625128") > 25)
    let boarding = [{walking: {steps: [{polyline: {polyline: "113.814609,22.624996"}}]} bus: {buslines: [{name: "合成未结束乘车"}]}}]
    smoke_check("上车前walking不能证明最终到达", route_terminal(boarding) == nil)
    let driving = fs.read("smoke-driving.json").parse_json()
    let taxi = route_candidates(nil, driving, received_at, arrive_by, 5000, received_at)
    smoke_check("全程出租车候车未知而非零", !taxi[0].feasible && !taxi[0].waiting_included && taxi[0].reason == "出租车候车时间未知")
    let mismatched = fs.read("smoke-transit.json").parse_json()
    mismatched.route.origin = "113.890000,22.580000"
    mismatched.route.destination = "113.820000,22.630000"
    mismatched.route.transits[0].segments[0].walking.steps[0].polyline = {polyline: "113.890000,22.580000"}
    mismatched.route.transits[0].segments[1].walking.steps[0].polyline = {polyline: "113.820000,22.630000"}
    candidates = []
    add_candidates(mismatched, nil, received_at, received_at, "smoke-wrong-request")
    let wrong = candidates[0]
    chosen = wrong phase = "proposal"
    confirm_trip()
    smoke_check("自洽错误起终点不能绑定或确认本次Trip", !wrong.request_bound && !wrong.endpoint_complete && !wrong.feasible && !route_recheck(wrong, received_at, arrive_by, 5000).passed && !fs.exists("trip.json"))
    let shifted = fs.read("smoke-transit.json").parse_json()
    shifted.route.transits[0].segments[0].walking.steps[0].polyline = {polyline: "113.890000,22.580000"}
    candidates = [] phase = "running"
    add_candidates(shifted, nil, received_at, received_at, "smoke-wrong-actual-start")
    let shiftedCandidate = candidates[0]
    smoke_check("回显起点正确而实际首点远离仍拒绝", shiftedCandidate.request_bound && !shiftedCandidate.origin_complete && !route_recheck(shiftedCandidate, received_at, arrive_by, 5000).passed)
    synthetic = fs.read("smoke-transit.json").parse_json()
    candidates = [] phase = "running"
    add_candidates(synthetic, driving, received_at, received_at, "smoke-injected-map")
    for index candidate in candidates { candidate.id = "smoke:" + candidate.id candidate.planned_departure_at = received_at }
    destination_record = {id: "synthetic-airport" name: "合成验收终点" longitude: 113.814610 latitude: 22.625128}
    transit_count = 1 driving_done = true request_text = "合成响应离线验收：40分钟内到机场，预算50。"
    observations.push({tool: "smoke-injected-map" observed_at: time_now() data: "明确合成的公共交通、混合与出租车响应，不是在线查询"})
    present_results("离线合成响应验收；本窗口不证明在线路线成功。")
    fs.write("smoke-checks.json", smoke_checks.to_json())
}
'''


def synthetic_routes(origin):
    goal = '113.814610,22.625128'
    terminal = {'walking': {'origin': '113.813660,22.624023', 'destination': '113.814609,22.624996',
                           'distance': '570', 'cost': {'duration': '737'},
                           'steps': [{'instruction': '合成测试步行到终点', 'polyline': {'polyline': '113.814609,22.624996'}}]}}
    line = {'walking': {'origin': origin, 'steps': [{'polyline': {'polyline': origin}}]}, 'bus': {'buslines': [{'name': '合成地铁（离线验收）', 'cost': {'duration': '100'},
                                 'departure_stop': {'name': '测试上车站', 'location': origin},
                                 'arrival_stop': {'name': '测试下车站', 'location': '113.813660,22.624023'}}]}}
    taxi = {'taxi': {'price': '10.00', 'drivetime': '300', 'startname': '测试上车点', 'endname': '测试换乘点',
                     'startpoint': origin, 'endpoint': origin, 'distance': '1000'}}
    transit = {'status': '1', 'route': {'origin': origin, 'destination': goal, 'transits': [
        {'cost': {'duration': '900', 'transit_fee': '5.00'}, 'segments': [line, terminal]},
        {'cost': {'duration': '800', 'transit_fee': '15.00'}, 'segments': [taxi, line, terminal]},
        {'cost': {'duration': '3000', 'transit_fee': '3.00'}, 'segments': [line, terminal]}]}}
    driving = {'status': '1', 'route': {'origin': origin, 'destination': goal, 'taxi_cost': '32',
                                      'paths': [{'cost': {'duration': '700'}, 'steps': []}]}}
    return transit, driving


def main():
    (ROOT / 'build/smoke').mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='navigation-', dir=ROOT / 'build/smoke'))
    bundle = work / 'bundle'
    shutil.copytree(ROOT / 'bundle', bundle)
    # 离线副本不具备网络或模型能力；原callback仍由注入的合成宿主回应执行。
    manifest = json.loads((bundle / 'manifest.json').read_text())
    manifest['capabilities'] = ['storage']
    manifest.pop('network', None)
    (bundle / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    source = (bundle / 'main.splash').read_text()
    source_main_sha256 = hashlib.sha256(source.encode()).hexdigest()
    anchor = 'start_timeout(0.05, || restore_trip())'
    assert source.count(anchor) == 1, '应用启动契约已变化；需调整smoke注入入口'
    assert source.count('    minimax_request(') == 1, '模型发送契约已变化；禁止意外外部请求'
    assert source.count('host.request(') == 0, '不允许混入旧模型服务调用'
    source = source.replace('    minimax_request(', '    smoke_minimax_request(', 1)
    assert source.count('Label{text: "NAVIGATION"') == 1, '离线截图标记入口已变化；需调整smoke'
    source = source.replace(anchor, CHECK + '\nstart_timeout(0.05, || restore_trip())')
    source = source.replace('Label{text: "NAVIGATION"', 'Label{text: "NAVIGATION / 离线合成响应验收"')
    (bundle / 'main.splash').write_text(source)
    jail = work / 'data' / APP_ID
    jail.mkdir(parents=True)
    now = datetime.now(timezone(timedelta(hours=8)))
    mapping = {'SOURCE_TIME': now.isoformat(timespec='seconds'), 'SOURCE_EPOCH': str(int(now.timestamp())),
               'ICS_STAMP_UTC': now.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
               'FLIGHT_START_LOCAL': (now + timedelta(hours=2)).strftime('%Y%m%dT%H%M%S'),
               'DINNER_START_LOCAL': (now + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')}
    for path in (ROOT / 'demo').rglob('*'):
        if path.is_file():
            target = jail / 'demo' / path.relative_to(ROOT / 'demo')
            target.parent.mkdir(parents=True, exist_ok=True)
            text = path.read_text()
            for key, value in mapping.items():
                text = text.replace('{{' + key + '}}', value)
            target.write_text(text)
    calendar = (jail / 'demo/calendar.ics').read_text()
    (jail / 'smoke-calendar-past.ics').write_text(calendar.replace(mapping['FLIGHT_START_LOCAL'], (now - timedelta(days=1)).strftime('%Y%m%dT%H%M%S')))
    note = (jail / 'demo/notes/ticket.md').read_text()
    (jail / 'smoke-conflict.md').write_text(note.replace('ticket-flight-demo', 'conflict-flight-demo').replace('T3', 'T2'))
    (jail / 'smoke-forged-note.md').write_text(note.replace('ticket-flight-demo', 'clarification-forged').replace('T3', 'T2'))
    # 合成地图响应与本次独立模拟来源同一点；避免更换demo后测试仍用旧起点。
    test_location = json.loads((jail / 'demo/location.json').read_text())
    test_origin = f"{test_location['longitude']},{test_location['latitude']}"
    transit, driving = synthetic_routes(test_origin)
    (jail / 'smoke-transit.json').write_text(json.dumps(transit, ensure_ascii=False))
    (jail / 'smoke-driving.json').write_text(json.dumps(driving, ensure_ascii=False))
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    running = False
    logs = []
    failure_paths = []

    def request(route, **params):
        with urlopen(base + route + ('?' + urlencode(params) if params else ''), timeout=10) as response:
            return response.read()

    def widgets():
        return [w for w in json.loads(request('/snap'))['s'] if w['ty'] != 'Splash']

    def find(predicate):
        found = [w for w in widgets() if predicate(w)]
        assert len(found) == 1, found
        return found[0]

    def status():
        return find(lambda w: w['i'] == 'status' and w['ty'] == 'Label')['t']

    def button(text):
        widget = None
        for attempt in range(8):
            found = [w for w in widgets() if w['ty'] == 'Button' and w.get('t') == text]
            if len(found) == 1 and 0 <= found[0]['r'][1] and found[0]['r'][1] + found[0]['r'][3] <= 892:
                widget = found[0]
                break
            if attempt >= 2:
                request('/m', k='scroll', x=240, y=580, dy=500, wait=1)
            time.sleep(.05)
        if widget is None:
            (work / 'missing-button-snap.json').write_bytes(request('/snap'))
            raise AssertionError(f'按钮无法在原生界面中找到: {text}')
        x, y, width, height = widget['r']
        request('/click', x=x + width / 2, y=y + height / 2, wait=1)

    def start():
        nonlocal running
        subprocess.run([*OCTO, 'run', str(bundle), '--app-data', str(work / 'data'), '--port', str(port), '--hidden', '--detach'], cwd=ROOT, check=True)
        running = True
        time.sleep(.15)

    def stop():
        nonlocal running
        if running:
            running = False
            # /quit可能在HTTP响应完成前退出；随后必须实际验证端口已释放。
            try:
                request('/quit')
            except OSError:
                pass
            logs.append((work / 'data/card-host.log').read_text())
            for _ in range(30):
                with socket.socket() as sock:
                    if sock.connect_ex(('127.0.0.1', port)) != 0:
                        return
                time.sleep(.05)
            raise AssertionError('本次card-host未释放端口')

    def inject_callback(function, previous='cancel_task'):
        widget = find(lambda w: w['ty'] == 'Button' and w.get('t') == '取消')
        x, y, width, height = widget['r']
        # 仍通过真实按钮回调调用注入入口，避免依赖脚本控制台/非公开宿主接口。
        current = (bundle / 'main.splash').read_text()
        stop()
        (bundle / 'main.splash').write_text(current.replace('on_click: || ' + previous + '()', 'on_click: || ' + function + '()', 1))
        start()
        request('/click', x=x + width / 2, y=y + height / 2, wait=1)

    try:
        start()
        button('规划新行程')
        # 应用现在以timer进入模型请求；必须确认发送已开始才覆盖迟到回调。
        for _ in range(40):
            if (jail / 'smoke-send-started.json').is_file():
                break
            time.sleep(.05)
        assert (jail / 'smoke-send-started.json').is_file(), '合成模型发送未进入'
        button('取消')
        time.sleep(1.1)
        assert status() == '任务已取消', status()
        late = json.loads((jail / 'smoke-late.json').read_text())
        assert late['phase'] == 'cancelled', late
        assert not (jail / 'trip.json').exists()
        print('PASS: 取消后迟到模型回调不改变任务状态（合成响应）')
        inject_callback('smoke_batch_start')
        for _ in range(40):
            if (jail / 'smoke-batch.json').is_file():
                break
            time.sleep(.05)
        batch = json.loads((jail / 'smoke-batch.json').read_text())
        assert batch['callback_exited'] and batch['phase'] == 'running', batch
        assert len(batch['source_records']) == 4
        assert {record['kind'] for record in batch['source_records']} == {'calendar', 'note', 'location'}
        assert {item['tool'] for item in batch['observations']} == {'read_calendar', 'read_notes', 'read_location'}
        print('PASS: 解析JSON模型回调完整执行三个独立来源工具并退出（合成响应）')
        inject_callback('smoke_identity_start', previous='smoke_batch_start')
        for _ in range(40):
            if (jail / 'smoke-identity.json').is_file():
                break
            time.sleep(.05)
        identity = json.loads((jail / 'smoke-identity.json').read_text())
        assert identity['callback_exited'] and identity['phase'] == 'failed', identity
        assert identity['model_requests'][0]['state'] == 'invalid_response'
        assert identity['retry_count'] == 0 and len(identity['model_requests']) == 1
        assert not (jail / 'trip.json').exists()
        print('PASS: 实际模型回调拒绝非MiniMax-M3响应，不保存Trip（合成响应）')
        inject_callback('smoke_protocol_once_start', previous='smoke_identity_start')
        for _ in range(40):
            if (jail / 'smoke-protocol_once-done.json').is_file():
                break
            time.sleep(.05)
        rejected = json.loads((jail / 'smoke-protocol_once-first.json').read_text())
        corrected = json.loads((jail / 'smoke-protocol_once-done.json').read_text())
        assert rejected['retry_count'] == 1 and rejected['decisions'] == []
        assert [o['tool'] for o in rejected['observations']] == ['protocol_error']
        assert rejected['observations'][0]['data']['executed'] is False
        assert corrected['phase'] == 'running' and corrected['retry_count'] == 1
        assert [d['next_action'] for d in corrected['decisions']] == ['read_sources']
        assert len(corrected['source_records']) == 4
        inject_callback('smoke_protocol_repeat_start', previous='smoke_protocol_once_start')
        for _ in range(40):
            if (jail / 'smoke-protocol_repeat-done.json').is_file():
                break
            time.sleep(.05)
        repeated = json.loads((jail / 'smoke-protocol_repeat-done.json').read_text())
        assert repeated['phase'] == 'failed' and repeated['retry_count'] == 1
        assert repeated['decisions'] == [] and len(repeated['model_requests']) == 2
        assert not (jail / 'trip.json').exists()
        print('PASS: 多动作响应未执行，仅一次固定纠正；单动作恢复，重复违规停止（合成响应）')
        inject_callback('smoke_prepare', previous='smoke_protocol_repeat_start')
        checks = json.loads((jail / 'smoke-checks.json').read_text())
        assert all(item['passed'] for item in checks), [item['name'] for item in checks if not item['passed']]
        assert '最低估价' in status(), status()
        # 来源在proposal之后独立变化时，不能将旧目标/位置确认为Trip。
        for relative in ('demo/calendar.ics', 'demo/notes/ticket.md', 'demo/location.json'):
            path = jail / relative
            original = path.read_text()
            path.write_text(original + '\n')
            button('确认并保存 Trip')
            assert not (jail / 'trip.json').exists(), f'来源变化后仍确认旧Trip: {relative}'
            assert '未通过' in status() or '重新规划' in status() or '变化' in status(), status()
            failure_paths.append({'source_changed': relative, 'status': status(), 'trip_written': False})
            if len(failure_paths) == 1:
                (work / 'source-changed-snap.json').write_bytes(request('/snap'))
                subprocess.run([*OCTO, 'shot', str(port), str(work / 'source-changed.png')], check=True)
            path.write_text(original)
            button('取消')  # 隔离副本中此按钮现在调用smoke_prepare，建立新的合成proposal。
        print('PASS: proposal后日历/笔记/位置分别变化均阻止旧Trip确认')
        button('确认并保存 Trip')
        assert status() == 'Trip 已确认并读回；尚未开始导航', status()
        trip = json.loads((jail / 'trip.json').read_text())
        assert trip['schema'] == 2 and trip['state'] == 'confirmed'
        assert trip['selected_route']['price_cents'] == 500
        assert trip['selected_route']['endpoint_complete']
        assert {record['kind'] for record in trip['source_records']} == {'calendar', 'note', 'location'}
        assert any(observation['tool'] == 'smoke-injected-map' for observation in trip['tool_observations'])
        subprocess.run([*OCTO, 'shot', str(port), str(work / 'confirmed-synthetic.png')], check=True)
        stop()
        start()
        assert status() == '已读回确认的 Trip；尚未开始导航', status()
        assert json.loads((jail / 'trip.json').read_text()) == trip
        print(f'PASS: {len(checks)}条来源/金额/期限/终点边界与Trip确认读回、重启恢复')
        stop()
        (jail / 'trip.json').write_text('{broken json')
        start()
        assert '无法读取' in status() or '格式无效' in status(), status()
        print('PASS: 损坏Trip显示错误，未冒充已确认行程')
        stop()
        (jail / 'trip.json').write_text(json.dumps({'schema': 2, 'state': 'confirmed', 'selected_route': {'id': 'bad'}}))
        start()
        assert '无法读取' in status() or '格式无效' in status(), status()
        stop()
    finally:
        stop()
    (work / 'combined.log').write_text('\n'.join(logs))
    problems = re.findall(ERROR_PATTERN, '\n'.join(logs), re.M)
    assert not problems, problems
    (work / 'report.json').write_text(json.dumps({'passed': True, 'synthetic_network_responses': True, 'external_requests': 0, 'source_main_sha256': source_main_sha256, 'checks': checks, 'observed_failure_paths': failure_paths, 'parsed_batch_callback': batch, 'wrong_model_callback': identity, 'protocol_correction': corrected, 'repeated_protocol_failure': repeated}, ensure_ascii=False, indent=2))
    print(f'PASS: 无网络原生Navigation验收；证据: {work}')


if __name__ == '__main__':
    main()
