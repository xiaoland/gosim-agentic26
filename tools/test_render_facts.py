"""回放 round16 的真实渲染参数和23份候选；另2份显式重复仅构成25候选负载。

原始资料只复制到隔离 jail。实际工具队列、安装诊断、回执与事实更新来自生产代码；
截获耗尽工具队列后的 agent_pump，不调用模型或供应商。
"""
import hashlib
import json
import re
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'build/research/rail-integration/e2e'

FIXTURE = r'''
let rf_checks=[] let rf_context=nil let rf_arguments=nil let rf_stage=0 let rf_dispatches=0
let rf_old_called=false let rf_old_revision_called=false let rf_written_revision=-1
let rf_cancel_count=0 let rf_cancel_value=nil let rf_revision_first=nil let rf_revision_second=nil let rf_revision_callbacks=0
fn rf_check(name,passed){rf_checks.push({name:name passed:passed}) fs.write("render-facts-progress.json",{checks:rf_checks stage:rf_stage dispatches:rf_dispatches}.to_json())}
fn rf_finish(){fs.write("harness-smoke.json",{checks:rf_checks dispatches:rf_dispatches route_count:candidates.len() revision:ui_facts_revision cached_revision:ui_facts_cached_revision}.to_json())}
fn rf_load(path,done){fs.read_async(path,fn(reply){if !reply.success {rf_check("真实夹具读取",false) rf_finish() return} done(reply.text.parse_json())})}
fn rf_route(index){
 fs.write("render-facts-stage.json",{stage:"loading" index:index}.to_json())
 if index>=25 {rf_begin() return}
 rf_load("render-fixture/route-"+index+".json",fn(candidate){candidates.push(candidate) start_timeout(0.01,||rf_route(index+1))})
}
fn rf_submit(id,params){
 let call={id:id function:{name:"render_ui" arguments:params.to_json()}}
 agent_calls=[call] agent_call_index=0 active_tool=nil
 agent_messages.push({role:"assistant" content:nil tool_calls:[call]})
 fs.write("render-facts-stage.json",{stage:"submit" call:id}.to_json())
 start_timeout(0.01,||agent_schedule_next(run_id))
}
fn rf_begin(){
 fs.write("render-facts-stage.json",{stage:"begin"}.to_json())
 run_id+=1 agent_active=true phase="running" trip_replay=false
 position_record=rf_context.origin destination_record=rf_context.destination
 constraints=rf_context.constraints user_limits=rf_context.limits arrive_by=rf_context.arrive_by received_at=position_record.sampled_at_unix
 route_nodes={} for node in rf_context.new_nodes {route_nodes[node.ref]=node}
 ui_facts_revision+=1 ui_facts_cached_revision=-1
 rf_submit("recorded-round16-xml",rf_arguments)
}
fn rf_reply(){let found=nil for message in agent_messages {if message.role=="tool" {found=message.content.parse_json()}} return found}
fn rf_valid_facts(block){
 if block==nil || !block.installed {return false}
 let facts=block.handle.find("fact_state").text().parse_json()
 if facts.routes.len()!=25 {return false}
 let ids={} for fact in facts.routes {ids[fact.id]=true}
 for candidate in candidates {if ids[candidate.id]!=true {return false}}
 return true
}
fn agent_pump(token){
 if !current_task(token) {return}
 rf_dispatches+=1
 let reply=rf_reply()
 fs.write("render-facts-reply-"+rf_stage+".json",reply.to_json())
 if rf_stage==0 {
  rf_check("真实XML源码获得一次明确错误回执并继续派发",reply!=nil && !reply.success && route_get(reply,"error")!="工具参数或数据执行错误" && (route_get(reply,"error")!=nil || reply.blocks[0].diagnostics!="") && rf_dispatches==1)
  rf_stage=1
  let body="Label{text:\"离线真实事实回归\"}"
  rf_submit("legal-splash",{blocks:[{id:"valid-a" source:body} {id:"valid-b" source:body}]})
 } elif rf_stage==1 {
  rf_check("合法Splash实际安装通知诊断成功回执",reply!=nil && reply.success && reply.blocks.len()==2 && reply.blocks[0].installed && reply.blocks[0].notified && reply.blocks[0].diagnostics=="" && rf_dispatches==2)
  rf_check("两个实际区块保全部25候选事实",rf_valid_facts(block_by_id("valid-a")) && rf_valid_facts(block_by_id("valid-b")))
  rf_stage=2 ui_facts_revision+=1 refresh_generated_facts()
  start_timeout(0.5,||{
   let one=block_by_id("valid-a") let two=block_by_id("valid-b")
   rf_check("共享事实刷新同revision且候选完整",one.written_revision==ui_facts_revision && two.written_revision==ui_facts_revision && rf_valid_facts(one) && rf_valid_facts(two))
   rf_written_revision=one.written_revision
   rf_save_current()
  })
 }
}
fn rf_save_current(){
 let now=time_now()
 let draft={id:"trip-1" title:"实际渲染事实" input:"离线保存caller回归" created_at:now updated_at:now status:"draft" goal:nil snapshot:nil _dirty:true}
 trip_records=[] trip_selected_id=nil trip_next_id=1 trip_generation=0 trip_saved_run=-1
 fs.write("render-facts-stage.json",{stage:"before_draft" candidates:candidates.len() facts_cached:ui_facts_cached_revision facts_count:ui_facts_object.routes.len()}.to_json())
 trip_commit({schema:1 selected_id:"trip-1" next_id:2 trips:[draft]},fn(draft_saved){
  rf_check("真实draft索引初始化",draft_saved)
  if !draft_saved {rf_finish() return}
  rf_save_completed()
 })
}
fn rf_save_completed(){
 fs.write("render-facts-stage.json",{stage:"calling_save_current" records:trip_records.len()}.to_json())
 trip_save_current("completed",fn(committed){
  fs.write("render-facts-stage.json",{stage:"save_done" success:committed generation:trip_generation error:guardian_error}.to_json())
  rf_check("真实保存caller准备共同事实并提交成功",committed && trip_generation==2)
  if !committed {rf_finish() return}
  trip_read("navigation-trips.json",fn(read){
   let snapshot=if read!=nil {read.data.trips[0].snapshot} else {nil}
   rf_check("真实保存caller读回25事实25raw与两份合法原稿",snapshot!=nil && snapshot.facts.routes.len()==25 && snapshot.route_data.len()==25 && snapshot.blocks.len()==2 && snapshot.blocks[0].source=="Label{text:\"离线真实事实回归\"}" && snapshot.blocks[1].source=="Label{text:\"离线真实事实回归\"}" && snapshot.facts.routes[0].estimated==candidates[0].estimated)
   rf_check("真实不完整候选保未知末端与金额等待false",snapshot!=nil && snapshot.route_data[0].selected_legs[0].to==nil && snapshot.route_data[0].actual_endpoint==nil && snapshot.facts.routes[0].cost.full_journey_amount_cents==nil && snapshot.facts.routes[0].waiting_included==candidates[0].waiting_included && snapshot.facts.routes[0].endpoint_complete==false)
   rf_cancel_checks()
  })
 })
}
fn rf_cancel_checks(){
 rf_written_revision=block_by_id("valid-a").written_revision
 ui_facts_revision+=1 let cancelled_revision=ui_facts_revision let cancelled_run=run_id
 ensure_interface_facts(run_id,fn(facts){rf_cancel_count+=1 rf_cancel_value=facts})
 run_id+=1
 start_timeout(0.5,||{
  fs.write("render-cancel-diagnostic.json",{count:rf_cancel_count value_nil:rf_cancel_value==nil cancelled_revision:cancelled_revision cached_revision:ui_facts_cached_revision cached_run:ui_facts_object_run current_run:run_id old_run:cancelled_run expected_written:rf_written_revision actual_written:block_by_id("valid-a").written_revision}.to_json())
  rf_check("旧run事实任务仅结案nil且不发布旧run缓存",rf_cancel_count==1 && rf_cancel_value==nil && !(ui_facts_cached_revision==cancelled_revision && ui_facts_object_run==cancelled_run))
  ui_facts_revision+=1
  ensure_interface_facts(run_id,fn(facts){rf_revision_first=facts rf_revision_callbacks+=1})
  ui_facts_revision+=1 let latest_revision=ui_facts_revision
  ensure_interface_facts(run_id,fn(facts){rf_revision_second=facts rf_revision_callbacks+=1})
  start_timeout(1,||{
   rf_check("旧revision等待者迁最新完整事实且不发布旧revision",rf_revision_callbacks==2 && rf_revision_first!=nil && rf_revision_first==rf_revision_second && rf_revision_first.routes.len()==25 && ui_facts_cached_revision==latest_revision && ui_facts_object_revision==latest_revision)
   rf_finish()
  })
 })
}
start_timeout(1,||{
 rf_load("render-fixture/context.json",fn(context){rf_context=context
 rf_load("render-fixture/arguments.json",fn(arguments){rf_arguments=arguments candidates=[] rf_route(0)})})
})
'''


def recorded_fixture():
    directory = EVIDENCE / 'private-state-round16/home/apps/os.agentic26-navigation'
    raw = {int(path.stem.rsplit('-', 1)[1]): path
           for path in directory.rglob('first-render-2-route-*.json')}
    assert set(raw) == set(range(25)) - {1, 18}, sorted(raw)
    events = [json.loads(line) for line in (EVIDENCE / 'round16/trace-private.jsonl').read_text().splitlines()]
    adopted = next(json.loads(json.loads(event['data'])['result']) for event in events
                   if event['event'] == 'tool_result' and json.loads(event['data']).get('name') == 'adopt_destination')
    arguments = json.loads((EVIDENCE / 'round16/render-pending-arguments.json').read_text())
    return raw, adopted, arguments


def source(original):
    assert 'fn agent_pump(' in original
    return original.replace('fn agent_pump(', 'fn product_agent_pump(', 1) + '\n' + FIXTURE


def prepare(jail):
    raw, context, arguments = recorded_fixture()
    directory = Path(jail) / 'render-fixture'
    directory.mkdir()
    for name, value in [('context', context), ('arguments', arguments)]:
        (directory / f'{name}.json').write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')))
    for index in range(25):
        if index in raw:
            (directory / f'route-{index}.json').write_bytes(raw[index].read_bytes())
        else:
            candidate = json.loads(raw[0 if index == 1 else 17].read_text())
            candidate['id'] = f'render_fixture_repeat_{index}'
            (directory / f'route-{index}.json').write_text(json.dumps(candidate, ensure_ascii=False, separators=(',', ':')))


def run(work, jail, original, injected):
    report = None
    for _ in range(900):
        try:
            report = json.loads((jail / 'harness-smoke.json').read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        if report:
            break
        log = (work / 'native.log').read_text()
        if any(token in log for token in ('instruction limit reached', 'script instruction limit exceeded', 'script heap allocation limit exceeded', 'contained a mini-app isolate panic', 'out of bounds', 'property _record_file not found')):
            report = {'checks': [{'name': '原生入口预算与运行完成', 'passed': False}]}
            progress = jail / 'render-facts-progress.json'
            if progress.exists(): report['progress'] = json.loads(progress.read_text())
            break
        time.sleep(.1)
    assert report, str(work / 'native.log')
    errors = [line for line in (work / 'native.log').read_text().splitlines() if '[E]' in line]
    xml_reply = json.loads((jail / 'render-facts-reply-0.json').read_text())
    xml_ids = set(re.findall(r'splash:(\d+):', json.dumps(xml_reply)))
    unexpected = [line for line in errors if not any(f'splash:{source_id}:' in line for source_id in xml_ids) and 'on_render closure failed; discarding its output' not in line]
    report.update(unexpected_native_errors=unexpected, product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),
                  recorded_round=16, actual_raw_candidate_count=23, missing_original_indexes=[1, 18],
                  duplicated_load_candidates=[{'index': 1, 'source_index': 0}, {'index': 18, 'source_index': 17}],
                  exact_original_25_replay=False, model_called=False, provider_called=False, native_errors=errors)
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert all(check['passed'] for check in report['checks']), report
    assert not unexpected, unexpected
    from test_trip_snapshot import read_record
    index = json.loads((jail / 'navigation-trips.json').read_text())['data']
    saved = read_record(jail, index['trips'][0]['file'])['snapshot']
    fixture = [json.loads((jail / f'render-fixture/route-{i}.json').read_text()) for i in range(25)]
    assert [route['segments'] for route in saved['route_data']] == [route['segments'] for route in fixture]
    assert [route['id'] for route in saved['facts']['routes']] == [route['id'] for route in fixture]
    report['saved_all_raw_segments_equal'] = True
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f'PASS: {len(report["checks"])} 项渲染事实链检查；{work / "report.json"}')
