"""持久化出行列表的隔离原生检查，由 smoke.py --trips 启动。"""
import hashlib
import json
import time
import struct
import zlib
from pathlib import Path


def prepare(jail):
    """用上一版合法业务记录检查迁移；不引用私人在线日志。"""
    now = time.time()
    route = {
        'id': 'legacy-route', 'kind': 'public_transit', 'segments': [],
        'selected_legs': [], 'price_cents': 800, 'currency': 'CNY',
        'duration_seconds': 600, 'departure_ts': now, 'source_ts': now,
        'expires_at': now + 300, 'source': 'synthetic-migration-fixture',
        'waiting_included': True, 'waiting_basis': 'provider_total',
        'request_bound': True, 'origin_complete': True, 'endpoint_complete': True,
        'actual_origin': '114,22', 'actual_endpoint': '114.03,22',
        'plan_key': 'legacy-plan', 'completion_status': 'reached_requested_destination',
        'provider_connection_status': None, 'requested_origin': None, 'requested_destination': None,
        'price_basis': None, 'known_cost_cents': None, 'warnings': '合成迁移记录，不是当前交通证据',
    }
    goal = {
        'schema': 1, 'state': 'active', 'version': 4, 'confirmed_at': now,
        'deadline_ts': now + 2400, 'total_budget_cents': 5000,
        'currency': 'CNY', 'spent_cents': 1200, 'progress': '旧版已确认进度',
        'preferences': '保留中文与“引号”', 'risk_acceptance': '接受供应商估计',
        'destination': {'name': '迁移目的地', 'longitude': 114.03, 'latitude': 22},
        'selected_route': route, 'selection_basis': '旧版确认业务',
        'confirmations': [{'version': 4, 'confirmed_at': now, 'action': 'confirm_progress'}],
    }
    legacy = Path(__file__).resolve().parents[1] / 'build/research/journey-guardian/online/private-state/home/apps/os.agentic26-navigation/guardian-goal.json'
    if legacy.exists():
        goal = json.loads(legacy.read_text())['goal']
    (jail / 'trips-legacy-expected.json').write_text(json.dumps(goal, ensure_ascii=False))
    data = {'schema': 1, 'saved_at': now, 'goal': goal, 'complete': 'navigation-goal-v1'}
    (jail / 'guardian-goal.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    def chunk(kind, value):
        return struct.pack('>I', len(value)) + kind + value + struct.pack('>I', zlib.crc32(kind + value) & 0xffffffff)
    for name, color in [('trip-map-a.png', (45, 125, 190)), ('trip-map-b.png', (190, 125, 45))]:
        scan = b''.join(b'\0' + bytes(color) * 300 for _ in range(180))
        image = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 300, 180, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(scan)) + chunk(b'IEND', b'')
        (jail / name).write_bytes(image)
    return data


def source(original):
    assert 'fn trip_new(' in original, '出行列表实现尚未就绪'
    interception = 'record.host_request_id = host.request("model.chat", body, fn(reply){'
    assert interception in original, '迟到模型回调入口已变化'
    instrumented = original.replace(interception, 'record.host_request_id = tl_host_request(body, fn(reply){', 1)
    instrumented = instrumented.replace('fn load_map_slot(', 'fn product_load_map_slot(', 1)
    return instrumented + '\n' + FIXTURE


FIXTURE = r'''
'''


def run(work, jail, request, stop, launch, original, injected):
    def wait_file(name):
        until = time.monotonic() + 30
        while time.monotonic() < until:
            path = jail / name
            if path.exists():
                return json.loads(path.read_text())
            time.sleep(.1)
        raise AssertionError(f'{name} 未完成，详见 {work}')

    def capture(name):
        rows = [r for r in json.loads(request('snap'))['s'] if r.get('ty') != 'Splash']
        (work / f'{name}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
        (work / f'{name}.png').write_bytes(request('g', raw=1))
        return rows

    def click(text=None, widget=None, contains=False):
        for _ in range(10):
            rows = capture('before-click')
            choices = [r for r in rows if r.get('ty') == 'Button' and r['r'][3] >= 20 and
                       (r.get('i') == widget if widget else (text in r.get('t', '') if contains else r.get('t') == text))]
            if choices:
                break
            request('m', k='scroll', x=220, y=700, dy=220, precise=1, wait=1)
            time.sleep(.2)
        assert len(choices) == 1, (text, widget, choices)
        x, y, w, h = choices[0]['r']
        request('click', x=x + w / 2, y=y + h / 2, wait=1)
        time.sleep(.3)

    def signal(name):
        markers = [json.loads(r['t']) for r in json.loads(request('snap', q='trace_identity'))['s'] if r.get('i') == 'trace_identity']
        assert len(markers) == 1
        (jail / name).write_text(json.dumps({'instance': markers[0]['instance']}))

    def android():
        time.sleep(3)
        request('k', c='Space', cmd=1, wait=1)
        for char in 'android':
            request('k', c='Key' + char.upper(), wait=1)
        request('k', c='enter', wait=1)
        time.sleep(1)
        request('m', k='down', x=200, y=300, wait=1)
        for y in range(320, 570, 25):
            request('m', k='move', x=200, y=y, wait=1)
        request('m', k='up', x=200, y=570, wait=1)
        request('t', t='Navigation', wait=1)
        request('k', c='enter', wait=1)
        time.sleep(1)

    def disk():
        index = json.loads((jail / 'navigation-trips.json').read_text())['data']
        return index, {entry['id']: json.loads((jail / entry['file']).read_text())['data'] for entry in index['trips']}

    def sidebar():
        rows = capture('sidebar-state')
        if not any(r.get('i') == 'trip_new_button' and r['r'][3] > 0 for r in rows):
            click(widget='trip_menu')

    def choose(trip_id):
        index, records = disk()
        title = records[trip_id]['title']
        sidebar()
        capture('sidebar')
        click(title, contains=True)

    def new():
        sidebar()
        click(widget='trip_new_button')

    android()
    signal('trips-go.json')
    ready = wait_file('trips-migration-ready.json')
    capture('migrated-goal')
    new()
    wait_file('trips-a-proposal.json')
    click('确认此方案')
    a = wait_file('trips-a-ready.json')['id']
    capture('trip-a-confirmed')
    signal('trips-late-start.json')
    wait_file('trips-late-dispatched.json')
    new()
    wait_file('trips-b-proposal.json')
    click('确认此方案')
    b = wait_file('trips-b-ready.json')['id']
    capture('trip-b-confirmed')
    click('结束目标')
    wait_file('trips-b-ended.json')
    choose(a)
    wait_file('trips-a-restored.json')
    time.sleep(.5)
    a_rows = capture('trip-a-restored')
    assert any(r.get('i') == 'trip_detail' and r.get('t') == 'A历史原始详情' and r['r'][3] > 0 for r in a_rows)
    assert not any(r.get('i') == 'trip_detail' and 'B历史' in r.get('t', '') for r in a_rows)
    click('A详情本地按钮')
    rows = capture('trip-a-local-action')
    assert any(r.get('i') == 'trip_detail' and r.get('t') == 'A详情点击成功' for r in rows)
    map_row = next(r for r in rows if r.get('i') == 'trip_map' and r['r'][3] >= 80)
    x, y, w, h = map_row['r']
    request('m', k='down', x=x + w / 2, y=y + h / 2, wait=1)
    request('m', k='move', x=x + w / 2 + 35, y=y + h / 2 + 15, wait=1)
    request('m', k='up', x=x + w / 2 + 35, y=y + h / 2 + 15, wait=1)
    time.sleep(.5)
    capture('trip-a-restored-map-drag')
    signal('trips-map-interacted.json')
    wait_file('trips-map-checked.json')
    choose(b)
    wait_file('trips-b-restored.json')
    capture('trip-b-restored')
    stop()
    launch('trips-restart')
    android()
    signal('trips-resume.json')
    wait_file('trips-restart-ready.json')
    rows = capture('trip-b-restarted')
    assert any(r.get('i') == 'trip_detail' and r.get('t') == 'B历史原始详情' and r['r'][3] > 0 for r in rows)
    index_before, records_before = disk()
    sidebar()
    click(widget='trip_delete_button')
    time.sleep(.5)
    index_after, records_after = disk()
    assert b not in records_after and a in records_after and ready['id'] in records_after
    assert not (jail / next(e['file'] for e in index_before['trips'] if e['id'] == b)).exists(), '已删除出行的当前 revision 未释放'
    assert records_after[a]['goal'] == records_before[a]['goal']
    assert records_after[a]['snapshot'] == records_before[a]['snapshot']
    capture('trip-b-deleted-other-survives')
    signal('trips-delete-checked.json')
    wait_file('trips-write-ready.json')
    index_path = jail / 'navigation-trips.json'
    backup = jail / 'trips-test-index-backup.json'
    index_path.rename(backup)
    index_path.mkdir()
    try:
        signal('trips-write-go.json')
        wait_file('trips-write-checked.json')
    finally:
        index_path.rmdir()
        backup.rename(index_path)
    signal('trips-write-restored.json')
    wait_file('trips-empty-ready.json')
    for trip_id in list(disk()[1]):
        if disk()[0]['selected_id'] != trip_id:
            choose(trip_id)
        sidebar()
        click(widget='trip_delete_button')
    assert disk()[0]['trips'] == []
    assert (jail / 'guardian-goal.json').exists()
    capture('empty-list')
    stop()
    launch('trips-empty-restart')
    android()
    signal('trips-empty-resume.json')
    report = wait_file('trips-report.json')
    capture('empty-list-restarted')
    report.update(mode='macOS arm64宿主Android样式，非Android真机',
                  synthetic_routes=True, synthetic_map_image=True, real_native_controls=True,
                  source_sha256=hashlib.sha256(original.encode()).hexdigest(),
                  injected_sha256=hashlib.sha256(injected.encode()).hexdigest(),
                  external_model_called=False)
    report['native_budget_exceeded'] = any('script time budget exceeded' in path.read_text(errors='replace') for path in work.glob('*.log'))
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert not report['native_budget_exceeded'], '原生回调超出执行时间预算，详见原生日志'
    assert all(c['passed'] for c in report['checks']), report
    print(f'PASS: {len(report["checks"])} 项出行列表检查；{work / "report.json"}')

FIXTURE = r'''
let tl_legacy_version=0 let tl_stage=0 let tl_checks=[] let tl_evidence={} let tl_legacy=nil let tl_a=nil let tl_b=nil let tl_done_count=0 let tl_callbacks=[] let tl_late_started=false let tl_old_token=0 let tl_old_block=nil let tl_old_pending=0 let tl_map_loads=0
fn tl_check(name,passed){tl_checks.push({name:name passed:passed})}
fn tl_checkpoint(){fs.write("trips-checkpoint.json",{checks:tl_checks evidence:tl_evidence legacy:tl_legacy a:tl_a b:tl_b}.to_json())}
fn tl_marker(name,data){fs.write(name,data.to_json())}
fn tl_owned(name){let text=read_text(name) return text!=nil && trace_state!=nil && text.parse_json().instance==trace_state.instance}
fn tl_host_request(body,done){tl_callbacks.push(done) tl_marker("trips-late-dispatched.json",{count:tl_callbacks.len()}) return 999}
fn load_map_slot(slot,candidate){
 tl_map_loads+=1
 let bytes=fs.read_bytes(if candidate.id=="route_A_1" {"trip-map-a.png"} else {"trip-map-b.png"})
 accept_map_slot(slot,bytes,run_id,slot.request,candidate.id,"合成纯色图，仅检验历史地图绑定和原生交互")
}
fn tl_context(tag){
 received_at=time_now() arrive_by=received_at+2400 user_limits={minutes:40 budget_cents:5000 currency:"CNY"} constraints={budget_cents:5000 currency:"CNY"}
 request_text=tag+"合成出行" ui.sentence.set_text(request_text)
 trip_begin(request_text)
 position_record={name:tag+"起点" longitude:114 latitude:22 source:"synthetic-fixture" mock:true sampled_at_unix:received_at coordinate_system:"GCJ-02" city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}
 destination_record={name:tag+"目的地" longitude:114.03 latitude:22 city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY" source:"synthetic-fixture"}
 let route=route_candidate("route_"+tag+"_1","public_transit",if tag=="A" {900} else {600},if tag=="A" {1000} else {2000},received_at,received_at,"114.03,22","114.03,22",true,[{walking:{steps:[{polyline:"114,22;114.03,22"}]}}])
 route.geometry_ref="polyline_"+tag+"_1" route.request_bound=true route.origin_complete=true
 candidates=[route] viewed_route_id=route.id answer_text=tag+"已取得路线与风险的终端说明" phase="complete" agent_active=false agent_messages=[{role:"user" content:"TRIP_"+tag+"_OLD_MODEL_SENTINEL"}]
 let raw="start_timeout(0.15,||emit({action:\"map\" widget:\"trip_map\" target:\"polyline_"+tag+"_1\" interactive:true})) View{width:Fill height:Fit flow:Down spacing:6 trip_detail := Label{text:\""+tag+"历史原始详情\"} Button{text:\""+tag+"详情本地按钮\" on_click:||ui.trip_detail.set_text(\""+tag+"详情点击成功\")} trip_map := AutoNaviMapView{width:Fill height:180 on_camera_changed:fn(lon,lat,zoom,width,height,request){emit({action:\"map_camera\" widget:\"trip_map\" center_lon:lon center_lat:lat zoom:zoom width:width height:height request:request})}} Label{text:\"合成图像，不是实际地图服务\"}}"
 interface_revision+=1
 mount_ui_blocks(if tag=="A" {{source:raw}} else {{blocks:[{id:"detail-B" source:raw}]}},run_id,interface_revision)
 start_timeout(0.5,||{
  let p=guardian_propose({route_id:route.id preferences:tag+"偏好" risk_acceptance:tag+"明确风险" basis:tag+"合成方案依据"})
  tl_check(tag+"提案未确认不写目标",p.success && trip_by_id(trip_selected_id).goal==nil)
  tl_marker("trips-"+if tag=="A" {"a"} else {"b"}+"-proposal.json",{id:trip_selected_id})
 })
}
fn tl_poll(){
 if tl_stage==0 {
  if tl_owned("trips-empty-resume.json") {
   let saved=read_text("trips-checkpoint.json").parse_json() tl_checks=saved.checks tl_evidence=saved.evidence
   tl_check("合法空库冷启动不复活旧guardian",trip_records.len()==0 && guardian_goal==nil && trip_selected_id==nil && fs.exists("guardian-goal.json"))
   tl_check("空库冷启动不发模型请求",tl_callbacks.len()==0)
   tl_marker("trips-report.json",{checks:tl_checks evidence:tl_evidence}) tl_stage=99
  } elif tl_owned("trips-resume.json") {
   let saved=read_text("trips-checkpoint.json").parse_json() tl_checks=saved.checks tl_evidence=saved.evidence tl_legacy=saved.legacy tl_a=saved.a tl_b=saved.b tl_legacy_version=read_text("trips-legacy-expected.json").parse_json().version
   tl_check("冷启动恢复选中B历史目标与三个出行",trip_records.len()==3 && trip_selected_id==tl_b && trip_replay && guardian_goal.state=="ended" && guardian_goal.selected_route.id=="route_B_1")
   tl_check("冷启动不恢复模型消息或未确认提案",agent_messages.len()==0 && guardian_pending==nil)
   tl_check("冷启动不自动模型核验",!agent_active && tl_callbacks.len()==0)
   tl_stage=8 start_timeout(0.5,||tl_marker("trips-restart-ready.json",{id:tl_b}))
  } elif tl_owned("trips-go.json") {
   tl_legacy=trip_selected_id let expected=read_text("trips-legacy-expected.json").parse_json() tl_legacy_version=expected.version
   tl_check("旧版guardian迁移保留目标进度预算期限",trip_records.len()==1 && guardian_goal!=nil && guardian_goal.version==expected.version && guardian_goal.spent_cents==expected.spent_cents && guardian_goal.total_budget_cents==expected.total_budget_cents && guardian_goal.deadline_ts==expected.deadline_ts && guardian_goal.progress==expected.progress && guardian_goal.selected_route.id==expected.selected_route.id)
   tl_check("迁移保留旧文件而新索引为权威",fs.exists("guardian-goal.json") && fs.exists("navigation-trips.json") && trip_by_id(tl_legacy).goal.version==tl_legacy_version)
   tl_check("启动迁移不自动业务查询",!agent_active && tl_callbacks.len()==0)
   tl_stage=1 tl_marker("trips-migration-ready.json",{id:tl_legacy})
  }
 }
 if tl_stage==1 && trip_selected_id!=tl_legacy {
  tl_a=trip_selected_id
  tl_check("真实新建A立即保存独立空草稿",trip_records.len()==2 && trip_by_id(tl_a).input=="" && guardian_goal==nil)
  tl_stage=2 tl_context("A")
 }
 if tl_stage==2 && guardian_goal!=nil && guardian_goal.selected_route.id=="route_A_1" {
  trip_save_current("complete")
  tl_check("真实确认A只更新A目标",trip_by_id(tl_a).goal.preferences=="A偏好" && trip_by_id(tl_legacy).goal.version==tl_legacy_version)
  tl_check("A存成功document原始DSL及当时事实",trip_by_id(tl_a).snapshot.blocks.len()==1 && trip_by_id(tl_a).snapshot.blocks[0].document && trip_by_id(tl_a).snapshot.facts.destination.name=="A目的地")
  tl_stage=3 tl_marker("trips-a-ready.json",{id:tl_a})
 }
 if tl_stage==3 && !tl_late_started && tl_owned("trips-late-start.json") {
  tl_late_started=true tl_old_token=run_id tl_old_block=block_by_id("__document")
  guardian_mode=true let old=guardian_propose({route_id:"route_A_1" preferences:"A偏好" risk_acceptance:"A明确风险" basis:"切换前未确认提案"}) tl_old_pending=guardian_pending.proposal_version
  agent_active=true phase="running"
  let record={step:99 run:run_id state:"queued" started_at:time_now()}
  minimax_request("",[],[],run_id,record,fn(data){tl_done_count+=1 answer_text="LATE_OLD_TRIP_POLLUTION"})
 }
 if tl_stage==3 && trip_selected_id!=tl_a {
  tl_b=trip_selected_id tl_stage=4
  tl_check("新建B取消A运行并清未确认消息",trip_records.len()==3 && guardian_goal==nil && guardian_pending==nil && agent_messages.len()==0 && run_id!=tl_old_token)
  let before=trip_state().to_json()
  tl_callbacks[0]({is_ok:true data:{response:{model:"MiniMax-M3" choices:[{message:{role:"assistant" content:"迟到污染"} finish_reason:"stop"}]} meta:{}}})
  enqueue_block_line(tl_old_block,0,"{\"action\":\"runtime_error\",\"message\":\"LATE_OLD_BLOCK\"}",0,tl_old_token,tl_old_block.revision)
  install_block_later(tl_old_block,tl_old_token,tl_old_block.revision,nil)
  start_timeout(0.15,||{
   tl_check("切换后真实旧模型回调不执行或写新项",tl_done_count==0 && answer_text!="LATE_OLD_TRIP_POLLUTION" && trip_state().to_json()==before)
   tl_check("旧渲染和旧块排队事件不污染新项",interface_error=="" && ui_blocks.len()==0)
   tl_context("B")
  })
 }
 if tl_stage==4 && guardian_pending!=nil {
  tl_check("旧trip确认不能覆盖新trip提案",!guardian_confirm(tl_old_pending) && guardian_goal==nil && guardian_pending.trip_id==tl_b)
  tl_stage=41
 }
 if tl_stage==41 && guardian_goal!=nil && guardian_goal.selected_route.id=="route_B_1" {
  trip_save_current("complete")
  tl_check("真实确认B不改A期限预算与路线",trip_by_id(tl_a).goal.selected_route.id=="route_A_1" && trip_by_id(tl_a).goal.total_budget_cents==5000 && trip_by_id(tl_b).goal.preferences=="B偏好")
  tl_stage=5 tl_marker("trips-b-ready.json",{id:tl_b})
 }
 if tl_stage==5 && guardian_goal.state=="ended" {
  trip_save_current("complete")
  tl_check("真实结束B不结束A",trip_by_id(tl_b).goal.state=="ended" && trip_by_id(tl_a).goal.state=="active")
  tl_stage=6 tl_marker("trips-b-ended.json",{id:tl_b})
 }
 if tl_stage==6 && trip_selected_id==tl_a && trip_replay {
  tl_check("真实切换A恢复自己的原始document与目标",guardian_goal.state=="active" && guardian_goal.selected_route.id=="route_A_1" && trip_history.facts.destination.name=="A目的地" && trip_history.blocks[0].document)
  tl_check("切换历史不恢复消息且不自动模型",agent_messages.len()==0 && guardian_pending==nil && !agent_active && tl_callbacks.len()==1)
  tl_check("历史候选不能准备当前替代",!guardian_prepare_selected().success)
  tl_evidence.map_before=tl_map_loads tl_stage=61 start_timeout(0.5,||tl_marker("trips-a-restored.json",{id:tl_a}))
 }
 if tl_stage==61 && tl_owned("trips-map-interacted.json") {
  let slot=map_slots["trip_map"]
  tl_check("历史polyline别名地图绑定且真实拖动回调",slot!=nil && slot.target_id=="route_A_1" && slot.state=="ready" && tl_map_loads>tl_evidence.map_before)
  tl_evidence.map={loads:tl_map_loads target:if slot!=nil {slot.target_id} else {nil} camera:if slot!=nil {slot.camera} else {nil}}
  tl_stage=7 tl_marker("trips-map-checked.json",{})
 }
 if tl_stage==7 && trip_selected_id==tl_b && trip_replay {
  tl_check("真实切换B保持B详情与结束状态",guardian_goal.state=="ended" && trip_history.facts.destination.name=="B目的地")
  let clean=true for trip in trip_records {if trip.snapshot!=nil && trip.snapshot.facts.guardian.proposal!=nil {clean=false}}
  tl_check("历史事实不持久化未确认提案",clean)
  tl_checkpoint() tl_stage=71 start_timeout(0.5,||tl_marker("trips-b-restored.json",{id:tl_b}))
 }
 if tl_stage==8 && tl_owned("trips-delete-checked.json") {
  tl_check("删除B保留A与迁移项",trip_by_id(tl_b)==nil && trip_by_id(tl_a).goal.state=="active" && trip_by_id(tl_legacy).goal.version==tl_legacy_version)
  tl_stage=9 tl_marker("trips-write-ready.json",{})
 }
 if tl_stage==9 && tl_owned("trips-write-go.json") {
  let before=trip_state().to_json() let selected=trip_selected_id
  let success=trip_new()
  tl_check("索引写入失败不新增切换或丢详情",!success && trip_state().to_json()==before && trip_selected_id==selected && guardian_error!="")
  tl_evidence.write_error=guardian_error tl_stage=10 tl_marker("trips-write-checked.json",{})
 }
 if tl_stage==10 && tl_owned("trips-write-restored.json") {tl_checkpoint() tl_stage=11 tl_marker("trips-empty-ready.json",{})}
 start_timeout(0.1,||tl_poll())
}
start_timeout(0.2,||tl_poll())
'''
