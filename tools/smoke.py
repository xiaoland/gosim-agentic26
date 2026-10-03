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
let smoke_last_model_input = nil
let smoke_last_system = ""
fn smoke_batch_start(){ smoke_reply_mode = "batch" start_task() }
fn smoke_identity_start(){ smoke_reply_mode = "wrong_model" start_task() }
let smoke_protocol_responses = 0
fn smoke_protocol_once_start(){ smoke_reply_mode = "protocol_once" smoke_protocol_responses = 0 start_task() }
fn smoke_protocol_repeat_start(){ smoke_reply_mode = "protocol_repeat" smoke_protocol_responses = 0 start_task() }
fn smoke_check(name, passed){ smoke_checks.push({name: name passed: passed}) }
fn smoke_sources(){
    source_snapshots = [] source_records = [] calendar_events = [] note_records = [] position_record = nil constraints = nil
    let valid = calendar_tool() && notes_tool() && position_tool()
    if valid { position_record.city = "深圳市" position_record.citycode = "0755" position_record.adcode = "440306" position_record.currency = "CNY" observe("read_location", position_record) }
    return valid
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
    smoke_last_model_input = input.to_json().parse_json()
    smoke_last_system = task
    fs.write("smoke-last-input.json", {task: task input: smoke_last_model_input token: token}.to_json())
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
            if responseIndex == 1 {
                let evidence = {phase: phase retry_count: protocol_retry_count decisions: decisions observations: observations source_records: source_records model_requests: model_requests}
                fs.write("smoke-" + mode + "-first.json", evidence.to_json())
            } else {
                start_timeout(0.15, || {
                    let evidence = {phase: phase retry_count: protocol_retry_count decisions: decisions observations: observations source_records: source_records model_requests: model_requests}
                    fs.write("smoke-" + mode + "-done.json", evidence.to_json())
                })
            }
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
            start_timeout(0.15, || {
            let evidence = {callback_exited: true phase: phase retry_count: protocol_retry_count source_records: source_records observations: observations model_requests: model_requests}
            if mode == "batch" { fs.write("smoke-batch.json", evidence.to_json()) }
            else { fs.write("smoke-identity.json", evidence.to_json()) }
            })
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
fn smoke_airports(){
    observations = [] model_requests = [] decisions = []
    let config_original = fs.read("private-config.json")
    let original_request = request_text let original_limits = user_limits.to_json().parse_json()
    let original_received = received_at let original_deadline = arrive_by
    fs.write("private-config.json", {location_mode: "live"}.to_json())
    let origin = position_record.to_json().parse_json()
    origin.id = "synthetic-live-position" origin.mock = false origin.accuracy_m = 35 origin.sampled_at_unix = time_now()
    origin.city = "广州市" origin.citycode = "020" origin.adcode = "440113" origin.currency = "CNY"
    position_record = origin constraints = nil destination_record = nil poi_records = [] candidates = [] chosen = nil used_tools = []
    source_records.retain(fn(source){ return source.kind != "location" })
    source_records.push({id: origin.id kind: "location" source: "synthetic-corelocation" mock: false raw: origin.to_json()})
    source_snapshots.retain(fn(snapshot){ return snapshot.kind != "location" && snapshot.path != "demo/location.json" })
    source_snapshots.push({kind: "location" raw: origin.to_json()})
    smoke_check("真实模式不能把模拟深圳机票绑定为实际目的地", !set_constraints(smoke_params()) && constraint_error.search("模拟") >= 0 && constraints == nil)
    let airport_state = navigation_tool_state()
    smoke_check("模型真实状态显示来源mock等级和机场发现动作", airport_state.location_mode == "live" && airport_state.source_records[0].mock == true && airport_state.available_actions.to_json().search("discover_airports") >= 0 && airport_state.available_actions.to_json().search("set_constraints") < 0)
    smoke_location_mode = "airports" phase = "running"
    let before_bad = smoke_location_map_calls
    discover_airports({budget_cents: 1}, run_id)
    smoke_check("机场发现拒绝模型金额且保留用户40分钟50元", phase == "failed" && constraints == nil && smoke_location_map_calls == before_bad && user_limits.to_json() == original_limits.to_json())
    phase = "running" run_id += 1
    let action = model_action(smoke_model_data({next_action: "discover_airports" reason: "根据真实城市查机场" parameters: {}}, "MiniMax-M3"))
    smoke_check("模型协议可表达机场发现", action != nil)
    dispatch(action, run_id)
    smoke_check("实际机场发现查询绑定真实城市类型并保留固定硬约束", smoke_city_params.search("&city=020&citylimit=false&extensions=all&children=1") == 0 && smoke_city_params.search("&types=150104") >= 0 && constraints.inferred == true && constraints.minutes == 40 && constraints.budget_cents == 5000 && arrive_by == original_deadline)
    smoke_check("机场候选只保留实际机场类别并优先合法入口坐标", poi_records.len() == 3 && poi_records[0].id == "airport-a" && poi_records[0].coordinate_basis == "entr_location" && poi_records[0].longitude == 113.814610 && poi_records[1].coordinate_basis == "location" && poi_records[1].parent == "airport-a")
    smoke_check("伪造ID非机场与明确暂停营业POI均不能选", !select_destination({poi_id: "unqueried"}, "合成未查询") && !select_destination({poi_id: "hotel"}, "合成非机场") && !select_destination({poi_id: "closed"}, "合成已关闭") && destination_error.search("暂停营业") >= 0 && destination_record == nil)
    let inference_reason = "当前城市的机场查询返回该候选，暂按机场入口规划"
    smoke_check("机场选择保存可解释推断且不伪造机票引用或航站楼", select_destination({poi_id: "airport-a"}, inference_reason) && constraints.airport == "合成客运机场A" && constraints.terminal == "" && constraints.departure_scene == "" && !field_present(constraints, "event_id") && !field_present(constraints, "citations") && constraints.inference.reason == inference_reason && constraints.inference.location_source == origin.id && constraints.inference.poi_id == destination_record.id && !constraints.inference.terminal_verified)
    smoke_check("推断结果明确假设来源与航站楼未核实", result_text().search("暂按 合成客运机场A") >= 0 && result_text().search("未读取真实机票，航站楼未确定") >= 0 && result_text().search(inference_reason) >= 0)
    let calls_before_repeat = smoke_location_map_calls
    discover_airports({}, run_id)
    smoke_check("形成约束后不能重复机场请求或覆盖选择", phase == "failed" && smoke_location_map_calls == calls_before_repeat && destination_record.id == "airport-a")
    phase = "running"
    add_candidates(fs.read("smoke-transit.json").parse_json(), fs.read("smoke-driving.json").parse_json(), received_at, received_at, "smoke-inferred-routes")
    transit_count = 1 driving_done = true
    present_results("合成推断机场比较")
    confirm_trip()
    let inferred_trip = fs.read("trip.json").parse_json()
    smoke_check("推断与理由随真实确认写入并读回Trip", phase == "confirmed" && inferred_trip.constraints.inferred == true && inferred_trip.constraints.inference.reason == inference_reason && inferred_trip.destination.id == "airport-a" && inferred_trip.constraints.terminal == "")
    fs.remove("trip.json") saved_trip = nil
    step_count = 12 automatic_seconds = 180 protocol_retry_count = 1
    let correction_token = run_id
    ui.sentence.set_text("改到另一座机场")
    query_task()
    smoke_check("结果修正续原任务硬约束并重新请求有效位置", phase == "running" && received_at == original_received && arrive_by == original_deadline && user_limits.to_json() == original_limits.to_json() && constraints == nil && destination_record == nil && candidates.len() == 0 && position_record == nil && navigation_tool_state().available_source_tools.to_json().search("read_location") >= 0)
    smoke_check("用户修正开启新自动阶段并隔离旧回调", run_id > correction_token && step_count == 1 && automatic_seconds == 0 && protocol_retry_count == 0 && smoke_last_model_input.clarifications[smoke_last_model_input.clarifications.len() - 1] == "改到另一座机场")
    smoke_check("实际模型请求只有短目标边界没有固定读源或查询攻略", smoke_last_system.len() < 600 && smoke_last_system.search("先提交") < 0 && smoke_last_model_input.tool_state.available_actions.to_json().search("discover_airports") < 0)
    cancel_task() phase = "running" position_record = origin constraints = nil used_tools = []
    position_record.currency = nil
    let before_missing_currency = smoke_location_map_calls
    discover_airports({}, run_id)
    smoke_check("无真实计价依据不能发现机场或借用模拟币种", phase == "failed" && constraints == nil && smoke_location_map_calls == before_missing_currency)
    phase = "running" position_record.currency = "CNY" position_record.sampled_at_unix = time_now() - 61
    discover_airports({}, run_id)
    smoke_check("无有效真实定位不能查询或回退模拟机场", phase == "failed" && constraints == nil && smoke_location_map_calls == before_missing_currency)
    phase = "running" position_record.sampled_at_unix = time_now() smoke_location_mode = "airport_empty" used_tools = []
    discover_airports({}, run_id)
    smoke_check("没有机场候选明确来源不足不退回模拟机票", phase == "failed" && poi_records.len() == 0 && destination_record == nil && constraints.airport == "")
    phase = "failed" ui.sentence.set_text("80分钟内到机场，预算80元")
    query_task()
    smoke_check("完整分钟预算指令启动新行程而非覆盖旧约束", phase == "running" && user_limits.minutes == 80 && user_limits.budget_cents == 8000 && request_text == "80分钟内到机场，预算80元" && replies.len() == 0 && received_at > original_received)
    cancel_task()
    fs.write("private-config.json", config_original)
    received_at = original_received arrive_by = original_deadline user_limits = original_limits request_text = original_request
    constraints = nil destination_record = nil candidates = [] chosen = nil used_tools = [] replies = []
    phase = "running" smoke_location_mode = "valid"
    smoke_sources()
    let before_demo = smoke_location_map_calls
    discover_airports({}, run_id)
    smoke_check("显式演示保持引用路线且不改为真实机场推断", phase == "failed" && constraints == nil && smoke_location_map_calls == before_demo && set_constraints(smoke_params()) && constraints.inferred == false && constraints.destination_query == "深圳宝安国际机场 T3 国内出发")
    cancel_task() phase = "running" constraints = nil step_count = 0 automatic_seconds = 0
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
    let incomplete = smoke_params() incomplete.destination_query = "深圳宝安国际机场 T3 航站楼"
    smoke_check("模型漏出发区域时依据已引用笔记形成完整目的地", set_constraints(incomplete) && constraints.destination_query == "深圳宝安国际机场 T3 国内出发")
    constraints = nil
    incomplete.destination_query = "深圳宝安国际机场 T3 国际出发"
    smoke_check("模型明确矛盾的出发区域仍拒绝", !set_constraints(incomplete) && constraint_error.search("出发区域") >= 0 && constraints == nil)
    let absent = smoke_params() absent.note_id = nil
    smoke_check("缺少引用字段有具体诊断而非类型异常", !set_constraints(absent) && constraint_error.search("引用") >= 0 && constraint_error.search("尚未查询") >= 0)
    smoke_check("坏引用诊断不泄露来源正文且保留原预算", !set_constraints(escapedQuote) && constraint_error.search("来源引用无效") >= 0 && user_limits.budget_cents == 5000)
    absent = smoke_params() absent.citations[0].quote = "SUMMARY:深圳出发航班\nLOCATION:深圳宝安国际机场"
    smoke_check("真实跨行引用也不允许", !set_constraints(absent))
    let fresh = position_record.sampled_at_unix position_record.sampled_at_unix = received_at - 1000
    smoke_check("过期位置诊断明确尚未查询路线", !set_constraints(smoke_params()) && constraint_error.search("过期") >= 0 && constraint_error.search("尚未查询") >= 0)
    position_record.sampled_at_unix = fresh
    let relaxed = smoke_params() relaxed.minutes = 90 relaxed.budget_cents = 10000
    smoke_check("模型不能把原句40/50改成90/100", !set_constraints(relaxed) && constraints == nil && arrive_by == received_at + 2400)
    smoke_check("标准DTSTART驱动当前事件且截止从首次指令起算", set_constraints(p) && arrive_by == received_at + 2400)
    smoke_check("未说币种保持未指定并由已核实城市推断", user_limits.currency == "unspecified" && constraints.currency == "CNY" && constraints.currency_basis.search("大陆") >= 0)
    smoke_check("预算币种只解析金额附近且未知币种不推断", explicit_limits("40分钟内到Beijing机场PVG，预算50人民币").currency == "CNY" && explicit_limits("40分钟内到机场，预算50越南盾").currency == "unsupported" && explicit_limits("40分钟内到机场，预算50GBP").currency == "unsupported" && explicit_limits("40分钟内到机场，预算50，尽量便宜").currency == "unspecified")
    smoke_check("预算后明确声明币种不被标点吞掉", explicit_limits("40分钟内到机场，预算50，币种是美元").currency == "unsupported" && explicit_limits("40分钟内到PVG，预算50，用USD结算").currency == "unsupported")
    user_limits.currency = declared_currency("币种是USD")
    constraints = nil
    smoke_check("单独外币澄清阻止规划且保留原40与50", set_constraints(p) && phase == "asking" && constraints == nil && user_limits.minutes == 40 && user_limits.budget_cents == 5000)
    let currency_start = received_at let currency_deadline = arrive_by
    ui.sentence.set_text("币种是人民币")
    clarify()
    smoke_check("后续人民币声明可恢复且保留原金额分钟与期限", user_limits.currency == "CNY" && user_limits.minutes == 40 && user_limits.budget_cents == 5000 && received_at == currency_start && arrive_by == currency_deadline && set_constraints(p) && constraints != nil)
    constraints = nil phase = "running"
    user_limits = explicit_limits("40分钟内到机场，预算50美元")
    smoke_check("最新完整外币预算也覆盖旧人民币声明", set_constraints(p) && phase == "asking" && constraints == nil && user_limits.currency == "unsupported" && user_limits.budget_cents == 5000)
    cancel_task() phase = "running"
    source_records.retain(fn(source){ return source.kind != "user" })
    user_limits = explicit_limits(request_text)
    source_records.retain(fn(source){ return source.id != "clarification-currency" }) phase = "running"
    set_constraints(p)
    smoke_check("长时间与大预算不受演示阈值限制且不丢分", explicit_limits("2000分钟内到机场，预算1000001.25").budget_cents == 100000125 && route_seconds("90000") == 90000 && route_cents("90071992547409.91") == 9007199254740991 && route_cents("90071992547409.92") == nil && route_seconds("9007199254740992") == nil)
    let original_limits = user_limits
    let broad = smoke_params() broad.minutes = 2000 broad.budget_cents = 100000125
    user_limits = explicit_limits("2000分钟内到机场，预算1000001.25")
    constraints = nil
    smoke_check("长于一天的用户期限与大预算严格绑定", set_constraints(broad) && arrive_by == received_at + 120000 && constraints.budget_cents == 100000125)
    user_limits = explicit_limits("40分钟内到机场，预算50美元") constraints = nil
    smoke_check("明确外币预算不换汇也不改原金额", set_constraints(p) && phase == "asking" && constraints == nil && user_limits.budget_cents == 5000)
    user_limits = original_limits phase = "running" constraints = nil
    set_constraints(p)
    let scene_conflict = note_records[0].to_json().parse_json() scene_conflict.id = "scene-conflict" scene_conflict.raw = scene_conflict.raw.replace("国内出发", "国际出发")
    note_records.push(scene_conflict) constraints = nil
    smoke_check("同机场航站楼不同出发区域也须澄清", set_constraints(p) && phase == "asking" && constraints == nil)
    let terminal_only = "本次从深圳宝安国际机场 T3 出发"
    source_records.push({id: "clarification-scene" kind: "user" source: "user-clarification" mock: false source_time: "合成用户响应" read_at: time_now() raw: terminal_only})
    let scene_reply = smoke_params() scene_reply.citations.push({source_id: "clarification-scene" quote: terminal_only})
    phase = "running"
    smoke_check("只裁决机场航站楼不解除出发区域冲突", set_constraints(scene_reply) && phase == "asking" && constraints == nil)
    source_records.retain(fn(source){ return source.id != "clarification-scene" })
    let explicit_scene = "本次从深圳宝安国际机场 T3 国内出发"
    source_records.push({id: "clarification-scene" kind: "user" source: "user-clarification" mock: false source_time: "合成用户响应" read_at: time_now() raw: explicit_scene})
    scene_reply.citations[2].quote = explicit_scene phase = "running"
    smoke_check("明确引用出发区域允许用户裁决冲突", set_constraints(scene_reply) && constraints != nil && constraints.departure_scene == "国内出发")
    source_records.retain(fn(source){ return source.id != "clarification-scene" })
    note_records.retain(fn(note){ return note.id != "scene-conflict" }) phase = "running"
    let both_original = note_records[0].raw
    note_records[0].raw += "\n另有国际出发记录"
    constraints = nil
    smoke_check("同一笔记双场景先澄清", set_constraints(p) && phase == "asking" && constraints == nil)
    source_records.push({id: "clarification-both" kind: "user" source: "user-clarification" mock: false source_time: "合成用户响应" read_at: time_now() raw: "本次从深圳宝安国际机场 T3 国内出发"})
    let both_reply = smoke_params() both_reply.citations.push({source_id: "clarification-both" quote: "本次从深圳宝安国际机场 T3 国内出发"})
    phase = "running"
    smoke_check("同一笔记双场景可由唯一用户场景裁决", set_constraints(both_reply) && constraints != nil && constraints.departure_scene == "国内出发")
    note_records[0].raw = both_original
    source_records.retain(fn(source){ return source.id != "clarification-both" })

    let original_note = note_records[0].raw
    note_records[0].raw = original_note.replace("国内出发", "国际出发")
    let international = smoke_params() international.destination_query = "深圳宝安国际机场 T3 国际出发"
    for source in source_records { if source.id == "ticket-flight-demo" { source.raw = note_records[0].raw } }
    international.citations[1].quote = "本次从深圳宝安国际机场 T3 国际出发"
    constraints = nil
    smoke_check("国际出发场景取自笔记而非固定国内", set_constraints(international) && constraints.departure_scene == "国际出发")
    note_records[0].raw = original_note
    for source in source_records { if source.id == "ticket-flight-demo" { source.raw = original_note } }
    constraints = nil
    set_constraints(p)
    smoke_check("城市缺字段与非大陆不伪造币种", amap_city("深圳市", [], "440306", "广东省") == nil && amap_city("香港", "1852", "810000", "香港特别行政区") == nil && amap_city([], "0571", "330106", "浙江省") == nil)
    smoke_check("时区与闰年边界", calendar_epoch("DTSTART:19700101T000000Z") == 0 && calendar_epoch("DTSTART;TZID=Asia/Shanghai:19700101T080000") == 0 && calendar_epoch("DTSTART:20260229T000000Z") == nil && calendar_epoch("DTSTART:20240229T000000Z") == 1709164800)
    let original_position = position_record
    let original_constraints = constraints
    position_record = {mock: true sampled_at_unix: time_now() longitude: 120.100000 latitude: 30.200000 city: "杭州市" citycode: "0571" adcode: "330106" currency: "CNY"}
    constraints = original_constraints.to_json().parse_json()
    constraints.airport = "上海虹桥国际机场" constraints.terminal = "T2" constraints.destination_query = "上海虹桥国际机场 T2 国际出发" constraints.departure_scene = "国际出发"
    smoke_location_mode = "city_contract"
    phase = "running" step_count = 0 loop_started_at = time_now() automatic_seconds = 0
    find_destination(run_id)
    smoke_check("POI终点城市独立取自实际元数据", select_destination({poi_id: "cross-city"}) && destination_record.citycode == "021" && destination_record.adcode == "310105" && destination_record.city != position_record.city)
    transit_count = 0 used_tools = [] smoke_city_params = ""
    query_transit({strategy: 0}, run_id)
    smoke_check("跨城交通参数绑定两端真实城市与行政区", smoke_city_params.search("&city1=0571&city2=021&ad1=330106&ad2=310105&strategy=0") >= 0)
    driving_done = false
    query_transit({strategy: 3}, run_id)
    let state_after_three = navigation_tool_state()
    smoke_check("公交0与3后状态保留其它普通策略且驾车未完成", state_after_three.queried_transit_strategies.to_json() == [0 3].to_json() && state_after_three.remaining_transit_strategies.to_json() == [1 2 4 5 7 8].to_json() && !state_after_three.driving_done && !state_after_three.can_present)
    observations = []
    next_action(run_id)
    smoke_check("实际模型发送边界包含确定性工具状态", smoke_last_model_input != nil && smoke_last_model_input.tool_state.queried_transit_strategies.to_json() == state_after_three.queried_transit_strategies.to_json() && smoke_last_model_input.tool_state.remaining_transit_strategies.to_json() == state_after_three.remaining_transit_strategies.to_json() && smoke_last_model_input.tool_state.available_actions.to_json() == state_after_three.available_actions.to_json() && smoke_last_model_input.tool_state.source_records.to_json() == state_after_three.source_records.to_json() && smoke_last_model_input.tool_state.destination.id == state_after_three.destination.id && !smoke_last_model_input.tool_state.driving_done && !smoke_last_model_input.tool_state.can_present)
    let calls_before_eight = smoke_location_map_calls
    query_transit({strategy: 8}, run_id)
    smoke_check("第三种合法策略8可派发而非两次上限", transit_count == 3 && smoke_location_map_calls == calls_before_eight + 1 && smoke_city_params.search("&strategy=8") >= 0 && navigation_tool_state().remaining_transit_strategies.to_json() == [1 2 4 5 7].to_json())
    let calls_before_economy = smoke_location_map_calls
    query_transit({strategy: 1}, run_id)
    smoke_check("最经济策略1实际派发且其它未查策略保留", transit_count == 4 && smoke_location_map_calls == calls_before_economy + 1 && smoke_city_params.search("&strategy=1") >= 0 && navigation_tool_state().remaining_transit_strategies.to_json() == [2 4 5 7].to_json())
    let calls_before_unsupported = smoke_location_map_calls
    query_transit({strategy: 1}, run_id)
    smoke_check("经济策略重复请求零派发", phase == "failed" && smoke_location_map_calls == calls_before_unsupported)
    phase = "running"
    query_transit({strategy: 6}, run_id)
    smoke_check("未取得地铁站POI时策略6零派发且原因明确", phase == "failed" && smoke_location_map_calls == calls_before_unsupported && ui.status.text().search("地铁站POI") >= 0)
    phase = "running"
    query_transit({strategy: 1.5}, run_id)
    smoke_check("小数策略参数无效且零派发", phase == "failed" && smoke_location_map_calls == calls_before_unsupported && ui.status.text().search("参数无效") >= 0)
    phase = "running"
    let calls_before_repeat = smoke_location_map_calls
    query_transit({strategy: 3}, run_id)
    smoke_check("重复策略3拒绝且没有额外地图派发", phase == "failed" && transit_count == 4 && smoke_location_map_calls == calls_before_repeat)
    phase = "running"
    present_results("合成检查：未查询驾车不得提前展示")
    smoke_check("驾车未查询时不能提前present", phase == "failed" && !navigation_tool_state().can_present)
    phase = "running" driving_done = true
    smoke_check("公交与驾车比较齐备才允许present", navigation_tool_state().can_present)
    driving_done = false

    poi_records.push({id: "wrong-airport" name: "其它机场 T2 国际出发" address: "同城市另一机场" city_metadata: amap_city("上海市", "021", "310105", "上海市")})
    destination_record = nil
    smoke_check("相同航站楼与场景不能证明机场身份", select_destination({poi_id: "wrong-airport"}) && phase == "failed" && destination_record == nil)
    phase = "running"
    smoke_check("POI缺城市元数据明确失败不回填起点城市", select_destination({poi_id: "missing-city"}) && phase == "failed" && destination_record == nil)
    smoke_location_mode = "valid" phase = "running" run_id += 1
    position_record = original_position constraints = original_constraints transit_count = 0 used_tools = []
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
    destination_record = {id: "synthetic-airport" name: "合成验收终点" longitude: 113.814610 latitude: 22.625128 city: "深圳市" citycode: "0755" adcode: "440306" currency: "CNY"}
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
    let unknownLate = modernChoice.to_json().parse_json()
    unknownLate.price_cents = nil unknownLate.duration_seconds = 1001 unknownLate.endpoint_complete = false
    let unknownCheck = route_recheck(unknownLate, boundaryBase, boundaryBase + 1000, 5000)
    smoke_check("未知价格仍报告已知超时与末段缺失而不称超预算", !unknownCheck.passed && unknownCheck.reason.search("费用未知") >= 0 && unknownCheck.reason.search("超过到达期限") >= 0 && unknownCheck.reason.search("末段未核实") >= 0 && unknownCheck.reason.search("超过预算") < 0)
    let overBoth = modernChoice.to_json().parse_json() overBoth.price_cents = 5001 overBoth.duration_seconds = 1001
    smoke_check("同候选超预算与超时同时说明", route_reason(overBoth, boundaryBase, boundaryBase + 1000, 5000).search("超过预算；超过到达期限") >= 0)
    smoke_check("过期交通需要重新查询", !route_recheck(cheapest, received_at + 301, arrive_by, 5000).passed)
    smoke_check("金额和耗时未知不转成零", route_cents("") == nil && route_cents("-1") == nil && route_cents("1.234") == nil && route_cents("50.25") == 5025 && route_cents("167772.17") == 16777217 && route_seconds(nil) == nil)
    synthetic.route.transits[0].cost = {duration: "900"}
    let missing = route_candidates(synthetic, nil, received_at, arrive_by, 5000, received_at)
    smoke_check("缺价候选明确排除", missing[0].price_cents == nil && !missing[0].feasible && missing[0].reason.search("费用未知") >= 0 && missing[0].reason.search("超过预算") < 0)
    let bad_terminal = [{walking: {destination: "113.813339,22.624422" steps: [{polyline: {polyline: "113.813339,22.624422"}}]}}]
    smoke_check("机场站出口不能当国内出发终点", route_endpoint_gap(route_terminal(bad_terminal), "113.814610,22.625128") > 25)
    let boarding = [{walking: {steps: [{polyline: {polyline: "113.814609,22.624996"}}]} bus: {buslines: [{name: "合成未结束乘车"}]}}]
    smoke_check("上车前walking不能证明最终到达", route_terminal(boarding) == nil)
    let driving = fs.read("smoke-driving.json").parse_json()
    let taxi = route_candidates(nil, driving, received_at, arrive_by, 5000, received_at)
    smoke_check("全程出租车候车未知而非零", !taxi[0].feasible && !taxi[0].waiting_included && taxi[0].reason.search("出租车候车时间未知") >= 0)
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
    destination_record = {id: "synthetic-airport" name: "合成验收终点" longitude: 113.814610 latitude: 22.625128 city: "深圳市" citycode: "0755" adcode: "440306" currency: "CNY"}
    transit_count = 1 driving_done = true request_text = "合成响应离线验收：40分钟内到机场，预算50。"
    observations.push({tool: "smoke-injected-map" observed_at: time_now() data: "明确合成的公共交通、混合与出租车响应，不是在线查询"})
    phase = "failed"
    smoke_check("失败后保留候选及完整理由和路线摘要", result_text().search("比较未完成，仅已有结果") >= 0 && result_text().search("方案 1") >= 0 && result_text().search("公共交通") >= 0 && result_text().search("步行") >= 0)
    phase = "asking" answer_text = "请补充出发区域" ui.sentence.set_text("预算50元")
    let replyCount = replies.len() let clarifyStart = received_at let clarifyDeadline = arrive_by
    query_task()
    smoke_check("查询在asking中进入澄清而不重置首次期限", replies.len() == replyCount + 1 && received_at == clarifyStart && arrive_by == clarifyDeadline)
    cancel_task() phase = "running"
    smoke_sources() set_constraints(p)
    smoke_airports()
    smoke_sources() set_constraints(p)
    destination_record = {id: "synthetic-airport" name: "合成验收终点" longitude: 113.814610 latitude: 22.625128 city: "深圳市" citycode: "0755" adcode: "440306" currency: "CNY"}
    candidates = [] add_candidates(synthetic, driving, received_at, received_at, "smoke-injected-map")
    transit_count = 1 driving_done = true
    present_results("离线合成响应验收；本窗口不证明在线路线成功。")
    fs.write("smoke-checks.json", smoke_checks.to_json())
}
'''

LOCATION_CHECK = r'''
let smoke_location_mode = "valid"
let smoke_location_checks = []
let smoke_location_cases = ["valid" "permission_denied" "transport" "timeout" "accuracy" "negative_accuracy" "stale" "future" "missing" "malformed" "timeout_guard" "conversion" "other_city" "municipality" "city" "overseas" "cancel" "failed_late" "batch"]
let smoke_location_done = 0
let smoke_location_map_calls = 0
let smoke_location_sample = 0
let smoke_location_cancels = 0
let smoke_city_params = ""
fn smoke_location_check(name, passed){ smoke_location_checks.push({name: name passed: passed}) }
fn smoke_location_dispatch(args, done){
    smoke_location_sample = time_now() - 0.25
    let fix = {success: true lat: 22.572704321 lon: 113.866299765 accuracy_m: 35 sampled_at: smoke_location_sample coordinate_system: "WGS84" source: "corelocation"}
    if smoke_location_mode == "accuracy" { fix.accuracy_m = 101 }
    if smoke_location_mode == "negative_accuracy" { fix.accuracy_m = -1 }
    if smoke_location_mode == "stale" { fix.sampled_at -= 61 }
    if smoke_location_mode == "future" { fix.sampled_at += 31 }
    if smoke_location_mode == "missing" { fix = {success: true coordinate_system: "WGS84" source: "corelocation"} }
    if smoke_location_mode == "malformed" { fix.coordinate_system = "unknown" }
    if smoke_location_mode == "permission_denied" || smoke_location_mode == "timeout" { fix = {success: false code: smoke_location_mode} }
    let response = {is_ok: true data: fix}
    if smoke_location_mode == "transport" { response = {is_ok: false error: "synthetic-host-refusal"} }
    if smoke_location_mode != "timeout_guard" { start_timeout(0.05, || done(response)) }
    return 41
}
fn smoke_location_cancel(args){
    smoke_location_cancels += 1
    smoke_location_check("宿主取消仅发送本次请求标识", args.request_id == 41)
}
fn smoke_amap_request(path, params, token, done){
    smoke_location_map_calls += 1
    if smoke_location_mode == "airports" || smoke_location_mode == "airport_empty" {
        if path != "/v3/place/text" { fail_task("机场检查拒绝非地点路径") return }
        smoke_city_params = params
        let pois = [{id: "airport-a" name: "合成客运机场A" typecode: "150104" type: "机场相关;飞机场" location: "113.900000,22.700000" entr_location: "113.814610,22.625128" parent: [] cityname: "广州市" citycode: "020" adcode: "440114" pname: "广东省"}
            {id: "airport-b" name: "合成客运机场B T2" typecode: "150104" type: "机场相关;飞机场" location: "121.327000,31.197000" entr_location: "invalid" parent: "airport-a" cityname: "上海市" citycode: "021" adcode: "310105" pname: "上海市"}
            {id: "hotel" name: "机场酒店" typecode: "100100" location: "113.800000,22.600000" cityname: "广州市" citycode: "020" adcode: "440114" pname: "广东省"}
            {id: "closed" name: "合成机场(暂停营业)" typecode: "150104" location: "113.800000,22.600000" cityname: "广州市" citycode: "020" adcode: "440114" pname: "广东省"}]
        if smoke_location_mode == "airport_empty" { pois = [pois[2]] }
        done({status: "1" pois: pois})
        return
    }
    if smoke_location_mode == "city_contract" {
        if path == "/v3/place/text" {
            smoke_check("目的地搜索用实际城市偏好且不限制跨城并请求元数据", params.search("&city=0571&citylimit=false&extensions=all") == 0)
            done({status: "1" pois: [{id: "cross-city" name: "上海虹桥国际机场 T2 国际出发" location: "121.327000,31.197000" cityname: "上海市" citycode: "021" adcode: "310105" pname: "上海市"} {id: "missing-city" name: "上海虹桥国际机场 T2 国际出发" location: "121.327000,31.197000"}]})
        } elif path == "/v5/direction/transit/integrated" { smoke_city_params = params }
        else { fail_task("跨城离线检查拒绝意外地图路径") }
        return
    }
    let data = {status: "1" locations: "113.872300,22.569705"}
    if path == "/v3/assistant/coordinate/convert" {
        smoke_location_check("GPS转换只发送六位坐标并明确gps", params == "&locations=113.866300,22.572704&coordsys=gps&output=JSON")
        if smoke_location_mode == "conversion" { data.locations = "invalid;multiple" }
    } elif path == "/v3/geocode/regeo" {
        data = {status: "1" regeocode: {addressComponent: {country: "中国" province: "广东省" city: "深圳市" citycode: "0755" adcode: "440306"}}}
        smoke_location_check("城市核对使用实际位置与基本地址", params.search("&extensions=base&radius=0&output=JSON") >= 0 && params.search("&location=") == 0)
        if smoke_location_mode == "other_city" { data.regeocode.addressComponent = {country: "中国" province: "浙江省" city: "杭州市" citycode: "0571" adcode: "330106"} }
        if smoke_location_mode == "municipality" { data.regeocode.addressComponent = {country: "中国" province: "上海市" city: [] citycode: "021" adcode: "310115"} }
        if smoke_location_mode == "overseas" { data.regeocode.addressComponent = {country: "中国" province: "香港特别行政区" city: "香港" citycode: "1852" adcode: "810000"} }
        if smoke_location_mode == "city" { data.regeocode.addressComponent.citycode = [] }
    } else { fail_task("离线测试拒绝其它地图请求") return }
    let payload = data.to_json().parse_json()
    start_timeout(0.02, || { if current_task(token) { done(payload) } })
}
fn smoke_location_case(index){
    if index >= smoke_location_cases.len() {
        fs.write("private-config.json", {location_mode: "demo"}.to_json())
        fs.write("smoke-location-checks.json", smoke_location_checks.to_json())
        return
    }
    smoke_location_mode = smoke_location_cases[index]
    received_at = time_now() arrive_by = received_at + 2400 loop_started_at = received_at automatic_seconds = 0 phase = "running" run_id += 1
    position_record = nil source_records = [] source_snapshots = [] observations = [] used_tools = [] model_requests = []
    calendar_events = [] note_records = [] smoke_location_done = 0 smoke_location_map_calls = 0 smoke_location_cancels = 0
    let original_start = received_at
    let original_deadline = arrive_by
    let token = run_id
    if smoke_location_mode == "batch" {
        smoke_reply_mode = "late"
        dispatch({next_action: "read_sources" reason: "合成实时定位批量" parameters: {source_tools: ["read_calendar" "read_location" "read_notes"]}}, token)
        smoke_location_check("批量来源在异步定位前不提前执行下一步", note_records.len() == 0 && model_requests.len() == 0)
    } else {
        live_position(token, fn(){ smoke_location_done += 1 })
        if smoke_location_mode == "cancel" { cancel_task() }
        if smoke_location_mode == "failed_late" { fail_task("合成任务已失败") }
    }
    let check_after = 0.6
    if smoke_location_mode == "timeout_guard" { check_after = 16.25 }
    start_timeout(check_after, || {
        if smoke_location_mode == "valid" || smoke_location_mode == "batch" || smoke_location_mode == "other_city" || smoke_location_mode == "municipality" {
            smoke_location_check("真实来源保留系统采样与原始WGS84精度", position_record != nil && position_record.mock == false && position_record.sampled_at_unix == smoke_location_sample && position_record.original_longitude == 113.866299765 && position_record.original_latitude == 22.572704321 && position_record.accuracy_m == 35 && position_record.coordinate_system == "GCJ-02" && position_record.currency == "CNY")
            if smoke_location_mode == "other_city" { smoke_location_check("非深圳城市来自实际响应不改成深圳", route_get(position_record, "city") == "杭州市" && route_get(position_record, "citycode") == "0571" && route_get(position_record, "adcode") == "330106") }
            if smoke_location_mode == "municipality" { smoke_location_check("直辖市空城市字段只用对应省名", route_get(position_record, "city") == "上海市" && route_get(position_record, "citycode") == "021") }
            smoke_location_check("真实来源snapshot可确认且不依赖模拟文件", sources_current() && source_snapshots.len() > 0)
            if smoke_location_mode == "valid" {
                smoke_location_check("真实定位仅完成一次且未改期限", smoke_location_done == 1 && received_at == original_start && arrive_by == original_deadline && smoke_location_map_calls == 2)
                let original_sample = position_record.sampled_at_unix
                position_record.sampled_at_unix = time_now() - 61
                phase = "proposal" chosen = {}
                confirm_trip()
                smoke_location_check("真实定位超过60秒阻止Trip确认且不刷新采样", phase == "needs_replan" && position_record.sampled_at_unix < original_sample && !fs.exists("trip.json"))
            } elif smoke_location_mode == "batch" {
                smoke_location_check("定位完成后继续第三来源且模型仅推进一次", note_records.len() == 1 && observations.len() == 3 && model_requests.len() == 1 && source_records.len() == 4)
            }
        } elif smoke_location_mode == "cancel" || smoke_location_mode == "failed_late" {
            let expected = "cancelled"
            if smoke_location_mode == "failed_late" { expected = "failed" }
            smoke_location_check("取消或失败后的定位结果不转换不覆盖任务", phase == expected && position_record == nil && source_records.len() == 0 && smoke_location_map_calls == 0 && smoke_location_done == 0 && smoke_location_cancels == 1)
        } else {
            smoke_location_check("定位失败阻塞且不回退模拟：" + smoke_location_mode, phase == "failed" && position_record == nil && source_records.len() == 0 && smoke_location_done == 0)
            if smoke_location_mode == "timeout_guard" { smoke_location_check("应用定位超时主动停止宿主采集", smoke_location_cancels == 1 && pending_location == nil) }
            if smoke_location_mode != "city" && smoke_location_mode != "overseas" && smoke_location_mode != "conversion" { smoke_location_check("无效fix不发送到高德：" + smoke_location_mode, smoke_location_map_calls == 0) }
        }
        run_id += 1
        smoke_location_case(index + 1)
    })
}
fn smoke_location_start(){
    cancel_task()
    smoke_location_checks = []
    smoke_location_check("六位经纬度保留符号和跨整数舍入", coordinate_six(-0.0000006) == "-0.000001" && coordinate_six(179.9999999) == "180.000000" && coordinate_six(0) == "0.000000")
    fs.write("private-config.json", {}.to_json())
    smoke_location_check("未配置时默认真实定位", location_mode() == "live")
    smoke_location_case(0)
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
    host_call = 'host.request("location.get", args, done)'
    cancel_call = 'host.request("location.cancel", args, fn(r){})'
    assert source.count(host_call) == 1 and source.count(cancel_call) == 1 and source.count('host.request(') == 2, '定位发送边界已变化；禁止真实宿主请求'
    source = source.replace(host_call, 'smoke_location_dispatch(args, done)')
    source = source.replace(cancel_call, 'smoke_location_cancel(args)')
    source = source.replace('amap_request("/' , 'smoke_amap_request("/')
    source = source.replace('    minimax_request(', '    smoke_minimax_request(', 1)
    source = source.replace(anchor, CHECK + LOCATION_CHECK + '\nstart_timeout(0.05, || restore_trip())')
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
    (jail / 'private-config.json').write_text(json.dumps({'location_mode': 'demo'}))
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

    def confirm():
        widget = find(lambda w: w['ty'] == 'TextInput' and w['i'] == 'sentence')
        x, y, width, height = widget['r']
        request('/click', x=x + width / 2, y=y + height / 2, wait=1)
        request('/key', c='KeyA', cmd=1, wait=1)
        request('/text', text='确认', wait=1)
        button('查询')

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
        widget = find(lambda w: w['ty'] == 'Button' and w.get('t') == '终止')
        x, y, width, height = widget['r']
        # 仍通过真实按钮回调调用注入入口，避免依赖脚本控制台/非公开宿主接口。
        current = (bundle / 'main.splash').read_text()
        stop()
        (bundle / 'main.splash').write_text(current.replace('on_click: || ' + previous + '()', 'on_click: || ' + function + '()', 1))
        start()
        request('/click', x=x + width / 2, y=y + height / 2, wait=1)

    try:
        start()
        assert sorted(w['t'] for w in widgets() if w['ty'] == 'Button') == ['查询', '终止']
        button('查询')
        # 应用现在以timer进入模型请求；必须确认发送已开始才覆盖迟到回调。
        for _ in range(40):
            if (jail / 'smoke-send-started.json').is_file():
                break
            time.sleep(.05)
        assert (jail / 'smoke-send-started.json').is_file(), '合成模型发送未进入'
        button('终止')
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
        inject_callback('smoke_location_start', previous='smoke_protocol_repeat_start')
        for _ in range(800):
            if (jail / 'smoke-location-checks.json').is_file():
                break
            time.sleep(.05)
        location_checks = json.loads((jail / 'smoke-location-checks.json').read_text())
        assert all(item['passed'] for item in location_checks), [item['name'] for item in location_checks if not item['passed']]
        print(f'PASS: {len(location_checks)}条真实定位分支、坐标转换、城市边界与迟到隔离（合成宿主/地图响应）')
        inject_callback('smoke_prepare', previous='smoke_location_start')
        checks = json.loads((jail / 'smoke-checks.json').read_text())
        assert all(item['passed'] for item in checks), [item['name'] for item in checks if not item['passed']]
        assert '最低估价' in status(), status()
        # 来源在proposal之后独立变化时，不能将旧目标/位置确认为Trip。
        for relative in ('demo/calendar.ics', 'demo/notes/ticket.md', 'demo/location.json'):
            path = jail / relative
            original = path.read_text()
            path.write_text(original + '\n')
            confirm()
            assert not (jail / 'trip.json').exists(), f'来源变化后仍确认旧Trip: {relative}'
            assert '未通过' in status() or '重新规划' in status() or '变化' in status(), status()
            failure_paths.append({'source_changed': relative, 'status': status(), 'trip_written': False})
            if len(failure_paths) == 1:
                (work / 'source-changed-snap.json').write_bytes(request('/snap'))
                subprocess.run([*OCTO, 'shot', str(port), str(work / 'source-changed.png')], check=True)
            path.write_text(original)
            button('终止')  # 隔离副本中此按钮现在调用smoke_prepare，建立新的合成proposal。
        print('PASS: proposal后日历/笔记/位置分别变化均阻止旧Trip确认')
        confirm()
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
        legacy_trip = json.loads(json.dumps(trip))
        legacy_trip['constraints'].pop('inferred', None)
        legacy_trip.pop('user_limits', None)
        stop()
        (jail / 'trip.json').write_text(json.dumps(legacy_trip, ensure_ascii=False))
        start()
        assert status() == '已读回确认的 Trip；尚未开始导航', status()
        assert json.loads((jail / 'trip.json').read_text()) == legacy_trip
        widget = find(lambda w: w['ty'] == 'TextInput' and w['i'] == 'sentence')
        x, y, width, height = widget['r']
        request('/click', x=x + width / 2, y=y + height / 2, wait=1)
        request('/key', c='KeyA', cmd=1, wait=1)
        request('/text', text='改到另一机场', wait=1)
        button('查询')
        resumed = json.loads((jail / 'smoke-last-input.json').read_text())['input']
        assert resumed['received_at'] == trip['received_at']
        assert resumed['explicit_user_limits']['minutes'] == trip['constraints']['minutes']
        assert resumed['explicit_user_limits']['budget_cents'] == trip['constraints']['budget_cents']
        assert resumed['clarifications'][-1] == '改到另一机场'
        assert 'read_location' in resumed['tool_state']['available_source_tools']
        assert resumed['tool_state']['destination'] is None
        audit = json.loads((jail / 'agent-run.json').read_text())
        assert audit['arrive_by'] == trip['arrive_by'] and audit['state'] == 'running'
        assert json.loads((jail / 'trip.json').read_text()) == legacy_trip
        print(f'PASS: {len(checks)}条边界及新旧schema2确认读回、重启与保留期限的用户修正')
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
    (work / 'report.json').write_text(json.dumps({'passed': True, 'synthetic_network_responses': True, 'external_requests': 0, 'source_main_sha256': source_main_sha256, 'checks': checks, 'location_checks': location_checks, 'observed_failure_paths': failure_paths, 'parsed_batch_callback': batch, 'wrong_model_callback': identity, 'protocol_correction': corrected, 'repeated_protocol_failure': repeated}, ensure_ascii=False, indent=2))
    print(f'PASS: 无网络原生Navigation验收；证据: {work}')


if __name__ == '__main__':
    main()
