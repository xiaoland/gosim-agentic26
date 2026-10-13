"""以 round22 真实完整快照验证终态保存、overlay 通知和取消归属。

原始资料仅写入隔离 jail；模型完成响应由同轮录制响应离线提供。
生产 pump、事务、安装与本地动作均实际运行，不调用模型或交通供应商。
"""
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'build/research/rail-integration/e2e'

FIXTURE = r'''
let tp_checks=[] let tp_stage="loading" let tp_response=nil let tp_refreshes=0 let tp_save_seen=false let tp_last_status=nil let tp_cancel_done=0 let tp_cancel_value=nil
fn tp_check(name,passed){tp_checks.push({name:name passed:passed}) fs.write("terminal-progress.json",{stage:tp_stage checks:tp_checks}.to_json())}
fn tp_finish(){fs.write("terminal-report.json",{checks:tp_checks stage:tp_stage status:tp_last_status phase:phase refreshes:tp_refreshes generation:trip_generation}.to_json())}
fn tp_load(path,done){fs.read_async("terminal-fixture/"+path,fn(reply){done(reply.text.parse_json())})}
fn trip_refresh_shell(){tp_refreshes+=1 probe_product_trip_refresh_shell()}
fn minimax_request(task,input,schema,token,record,done){start_timeout(0.01,||done(tp_response))}
fn trip_save_current(status,done){return probe_product_trip_save_current(status,fn(committed){if done!=nil {done(committed)} if tp_stage=="terminal" && !tp_save_seen {tp_save_seen=true tp_check("正常stop完整保存提交成功",committed) start_timeout(0.2,||tp_terminal_read())}})}
fn tp_terminal_read(){trip_read("navigation-trips.json",fn(read){
 let saved=if read!=nil {read.data.trips[0]} else {nil}
 tp_check("终态新facts waiting且shell解除busy",saved!=nil && saved.status=="completed" && saved.snapshot.facts.phase=="waiting" && saved.snapshot.facts.routes.len()==16 && saved.snapshot.route_data.len()==16 && !shell_busy() && (!ui.control.visible() || ui.query_button.text()!="停止"))
 fs.write("terminal-button.json",{text:ui.query_button.text() control_visible:ui.control.visible() busy:shell_busy() phase:phase status:if saved!=nil {saved.status} else {nil} facts_phase:if saved!=nil {saved.snapshot.facts.phase} else {nil} routes:if saved!=nil {saved.snapshot.facts.routes.len()} else {nil} raw_routes:if saved!=nil {saved.snapshot.route_data.len()} else {nil} refreshes:tp_refreshes}.to_json())
 tp_stage="overlay" agent_active=true
 let body="Label{text:\"原生overlay边界\"}"
 let calls=[{id:"generic" function:{name:"render_ui" arguments:{blocks:[{id:"normal" source:body} {id:"hidden" source:body overlay:true height:100} {id:"explicit" source:body overlay:true visible:true height:100}]}.to_json()}} {id:"named" function:{name:"render_route_detail" arguments:{id:"detail" source:body height:100}.to_json()}}]
 agent_calls=calls agent_call_index=0 active_tool=nil agent_messages=[]
 agent_schedule_next(run_id)
})}
fn agent_pump(token){if tp_stage=="terminal" {probe_product_agent_pump(token) return} if tp_stage!="overlay" {return}
 let normal=block_by_id("normal") let hidden=block_by_id("hidden") let explicit=block_by_id("explicit") let detail=block_by_id("detail")
 tp_check("四种overlay默认与显式优先真实安装",normal!=nil && normal.visible && normal.installed && normal.notified && hidden!=nil && !hidden.visible && hidden.installed && explicit!=nil && explicit.visible && explicit.notified && detail!=nil && !detail.visible && detail.installed)
 tp_stage="late_notify" agent_active=false
 ui_dispatch_action({action:"show_block" block:"hidden" visible:true})
 start_timeout(0.7,||{
  tp_check("真实show_block打开获得无诊断通知",hidden.visible && hidden.notified && hidden.complete && hidden.handle.diagnostics()=="")
  ui_dispatch_action({action:"show_block" block:"hidden" visible:false})
  tp_check("真实show_block关闭",!hidden.visible)
  start_timeout(0.8,||trip_read("navigation-trips.json",fn(read){tp_last_status=read.data.trips[0].status tp_check("终态晚通知保completed持久化",tp_last_status=="completed") tp_cancel()}))
 })
}
fn tp_cancel(){tp_stage="cancel" ui_facts_revision+=1
 probe_product_trip_save_current("completed",fn(committed){tp_cancel_done+=1 tp_cancel_value=committed})
 tp_cancel_poll()
}
fn tp_cancel_poll(){if trip_pending_commit==nil {start_timeout(0.01,||tp_cancel_poll()) return}
 run_id+=1 trip_cancel_commit() let before=tp_refreshes
 start_timeout(0.5,||{tp_check("旧run取消回调恰一次false且不刷新新归属",tp_cancel_done==1 && tp_cancel_value==false && tp_refreshes==before) tp_finish()})
}
fn tp_routes(index){if index>=16 {
 run_id+=1 agent_active=false phase="proposal" trip_replay=false guardian_goal=nil guardian_pending=nil ui_blocks=[] ui_facts_revision+=1
 trip_records=[] trip_selected_id=nil trip_generation=0 trip_next_id=1
 let now=time_now() let draft={id:"trip-1" title:"终态真实负载" input:"离线原生终态验证" created_at:now updated_at:now status:"running" goal:nil snapshot:nil _dirty:true}
 trip_commit({schema:1 selected_id:"trip-1" next_id:2 trips:[draft]},fn(committed){tp_check("真实小draft提交",committed) tp_stage="terminal" agent_active=true agent_messages=[] agent_calls=[] agent_call_index=0 active_tool=nil step_count=0 probe_product_agent_pump(run_id)}) return
 }
 tp_load("route-"+index+".json",fn(c){candidates.push(c) start_timeout(0.01,||tp_routes(index+1))})
}
start_timeout(2,||tp_load("facts.json",fn(facts){position_record=facts.origin destination_record=facts.destination constraints=facts.limits user_limits=facts.limits arrive_by=facts.arrive_by received_at=facts.received_at route_nodes={} for node in facts.route_graph.nodes {route_nodes[node.ref]=node} candidates=[] tp_load("response.json",fn(response){tp_response=response tp_routes(0)})}))
'''


def source(original):
    injected = original
    for name in ['minimax_request', 'agent_pump', 'trip_save_current', 'trip_refresh_shell']:
        assert f'fn {name}(' in injected
        injected = injected.replace(f'fn {name}(', f'fn probe_product_{name}(', 1)
    return injected + '\n' + FIXTURE


def prepare(jail):
    from test_trip_snapshot import read_record
    recorded_jail = EVIDENCE / 'private-state-round22/home/apps/os.agentic26-navigation'
    index = json.loads((recorded_jail / 'navigation-trips.json').read_text())['data']
    snapshot = read_record(recorded_jail, index['trips'][0]['file'])['snapshot']
    facts = snapshot['facts']
    assert len(snapshot['route_data']) == len(facts['routes']) == 16
    candidates = []
    for raw, fact in zip(snapshot['route_data'], facts['routes']):
        assert raw['id'] == fact['id']
        candidate = dict(raw)
        # materialize 不保存这些候选字段；从同份公开事实恢复，未知仍为 None。
        candidate.update({key: fact.get(key) for key in ['taxi_wait_verified', 'endpoint_gap_m', 'request_bound', 'departure_ts', 'source_ts', 'expires_at', 'warnings', 'waiting_included', 'waiting_basis', 'origin_complete', 'endpoint_complete']})
        candidate.update(legs=fact['legs'], geometry_ref=fact['geometry_ref'], steps_cache=fact['steps'], segments_cache=fact['steps'])
        candidates.append(candidate)
    events = [json.loads(line) for line in (EVIDENCE / 'round22/trace-private.jsonl').read_text().splitlines()]
    event = next(event for event in events if event['seq'] == 236)
    response = json.loads(json.loads(event['data'])['body'])['response']
    assert response['choices'][0]['finish_reason'] == 'stop'
    directory = Path(jail) / 'terminal-fixture'
    directory.mkdir()
    for name, value in [('facts', facts), ('response', response)]:
        (directory / f'{name}.json').write_text(json.dumps(value, ensure_ascii=False))
    for index, candidate in enumerate(candidates):
        (directory / f'route-{index}.json').write_text(json.dumps(candidate, ensure_ascii=False))


def run(work, jail, original, injected):
    from test_trip_snapshot import read_record
    report = None
    for _ in range(600):
        path = jail / 'terminal-report.json'
        if path.exists():
            report = json.loads(path.read_text())
            break
        time.sleep(.05)
    assert report, str(work / 'native.log')
    index = json.loads((jail / 'navigation-trips.json').read_text())['data']
    saved = read_record(jail, index['trips'][0]['file'])['snapshot']
    fixture = [json.loads((jail / f'terminal-fixture/route-{index}.json').read_text()) for index in range(16)]
    errors = [line for line in (work / 'native.log').read_text().splitlines() if '[E]' in line]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(), actual_routes=16,
                  terminal_observation=json.loads((jail / 'terminal-button.json').read_text()),
                  raw_segments_preserved=len(saved['route_data']) == 16 and [route['segments'] for route in saved['route_data']] == [route['segments'] for route in fixture],
                  model_called=False, provider_called=False, native_errors=errors,
                  fixture_boundary='round22完整snapshot真实segments；legs/geometry及缺失候选字段由同份公开facts恢复，未知保nil；离线真实stop响应。')
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert all(check['passed'] for check in report['checks']), report
    assert report['raw_segments_preserved'] and not errors, report
    print(f'PASS: {len(report["checks"])} 项终态与overlay检查；{work / "report.json"}')
