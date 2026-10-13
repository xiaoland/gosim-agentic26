"""出行目标守护的隔离原生检查，由 smoke.py --guardian 启动。"""
import hashlib
from test_trip_snapshot import read_record
import json
import time


def source(original):
    assert 'fn guardian_propose(' in original, '目标守护实现尚未就绪'
    return original + '\n' + FIXTURE


def run(work, jail, request, stop, launch, original, injected):
    def stored_goal():
        index = json.loads((jail / 'navigation-trips.json').read_text())['data']
        entry = next(e for e in index['trips'] if e['id'] == index['selected_id'])
        return read_record(jail,entry['file'])['goal']

    def wait_file(name):
        until = time.monotonic() + 30
        while time.monotonic() < until:
            path = jail / name
            if path.exists():
                return json.loads(path.read_text())
            time.sleep(.1)
        raise AssertionError(f'{name} 未完成，详见 {work / "native.log"}')

    def capture(name):
        rows = [row for row in json.loads(request('snap'))['s'] if row.get('ty') != 'Splash']
        (work / f'{name}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
        (work / f'{name}.png').write_bytes(request('g', raw=1))
        return rows

    def click(text, last=False):
        if text == "确认此方案" and any(row.get("t") == "查看提案" for row in capture("before-open-proposal")):
            click("查看提案")
        for attempt in range(5):
            rows = capture('before-click')
            visible = [row for row in rows if row.get('ty') == 'Button' and row.get('t') == text and row['r'][3] >= 20]
            if visible:
                break
            request('m', k='scroll', x=220, y=700, dy=300, precise=1, wait=1)
            time.sleep(.2)
        assert visible, f'{text} 未实际可见'
        row = visible[-1] if last else visible[0]
        x, y, width, height = row['r']
        request('click', x=x + width / 2, y=y + height / 2, wait=1)
        time.sleep(.4)

    def signal(name):
        rows = json.loads(request('snap', q='trace_identity'))['s']
        markers = [json.loads(row['t']) for row in rows if row.get('i') == 'trace_identity']
        assert len(markers) == 1, markers
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

    android()
    signal('guardian-test-go.json')
    wait_file('guardian-test-proposed.json')
    capture('proposal')
    click('确认此方案')
    wait_file('guardian-test-confirmed.json')
    capture('confirmed')
    stop()
    launch('guardian-restart')
    android()
    signal('guardian-test-resume.json')
    wait_file('guardian-test-replacement.json')
    click('查看合成候选B')
    time.sleep(.3)
    viewed = capture('viewed-candidate')
    assert any(row.get('i') == 'guardian_viewed_candidate' and 'guardian-b' in row.get('t', '') and row['r'][3] > 0 for row in viewed), '当前候选身份未可见'
    click('用当前查看方案准备替代')
    time.sleep(.3)
    capture('local-replacement-proposal')
    assert stored_goal()['selected_route']['id'] == 'guardian-a'
    click('拒绝提案')
    time.sleep(.3)
    capture('local-replacement-rejected')
    assert stored_goal()['selected_route']['id'] == 'guardian-a'
    click('用当前查看方案准备替代')
    time.sleep(.3)
    capture('replacement')
    click('确认此方案')
    wait_file('guardian-test-progress.json')
    click('确认进度/费用')
    time.sleep(.3)
    row = next(row for row in capture('progress') if row.get('i') == 'guardian_spent' and row.get('ty') == 'TextInput')
    x, y, width, height = row['r']
    request('click', x=x + width / 2, y=y + height / 2, wait=1)
    for _ in range(len(row.get('val', row.get('t', ''))) + 3):
        request('k', c='Backspace', wait=1)
        request('k', c='Delete', wait=1)
    request('t', t='45', wait=1)
    request('k', c='Escape', wait=1)
    time.sleep(.3)
    click('确认进度/费用', last=True)
    wait_file('guardian-test-storage-ready.json')
    check_rows = capture('current-check-reasons')
    # 匿名父Label不进入remote snapshot；保留实际截图人工核对，fixture同时记录文案。
    goal_path = jail / 'navigation-trips.json'
    backup = jail / 'guardian-test-goal-backup.json'
    goal_path.rename(backup)
    goal_path.mkdir()
    try:
        (jail / 'guardian-test-storage-go.json').write_text('{}')
        wait_file('guardian-test-storage-checked.json')
    finally:
        goal_path.rmdir()
        backup.rename(goal_path)
    (jail / 'guardian-test-storage-restored.json').write_text('{}')
    wait_file('guardian-layout-ready-1.json')
    capture('overlay-fill-without-height')
    (jail / 'guardian-layout-next-1.json').write_text('{}')
    wait_file('guardian-layout-ready-2.json')
    capture('overlay-fit-long')
    request('m', k='scroll', x=220, y=600, dy=2000, precise=1, wait=1)
    time.sleep(.3)
    layout_rows = capture('overlay-fit-bottom')
    assert any(row.get('t') == '守护overlay第23行' and row['r'][3] > 0 for row in layout_rows), '自然Fit详情未滚动到最后一行'
    (jail / 'guardian-layout-next-2.json').write_text('{}')
    wait_file('guardian-layout-ready-3.json')
    capture('overlay-fill-explicit-height')
    (jail / 'guardian-layout-next-3.json').write_text('{}')
    report = wait_file('guardian-test-report.json')
    recovery = report['evidence']['recovery']
    restored = json.loads(recovery['before']) == json.loads(recovery['after'])
    next(check for check in report['checks'] if check['name'] == '主记录损坏从确认备份恢复且明确说明')['passed'] &= restored
    capture('resumed-checks')
    report.update(mode='macOS arm64，宿主 Android 样式，非 Android 真机',
                  model_called=False, synthetic_routes=True, real_native_controls=True,
                  source_sha256=hashlib.sha256(original.encode()).hexdigest(),
                  injected_sha256=hashlib.sha256(injected.encode()).hexdigest())
    report['native_utf8_panic'] = any('not a char boundary' in path.read_text(errors='replace') for path in work.glob('*.log'))
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert not report['native_utf8_panic'], '历史中文 DSL 重挂触发宿主 UTF8 panic，详见原生日志'
    assert all(check['passed'] for check in report['checks']), report
    print(f'PASS: {len(report["checks"])} 项目标守护检查；{work / "report.json"}')


FIXTURE = r'''
let gt_stage=0 let gt_checks=[] let gt_version=0 let gt_original=nil let gt_evidence={} let gt_local_pending_checked=false let gt_local_rejected=false
fn gt_saved_text(){
 let index=read_text("navigation-trips.json").parse_json().data
 for entry in index.trips {if entry.id==index.selected_id {
  let text=read_text(entry.file) let parsed=text.parse_json()
  if parsed.complete=="navigation-trip-parts-v1" {text="" for part in parsed.parts {text+=read_text(part.file)} parsed=text.parse_json()}
  return {goal:parsed.data.goal}.to_json()
 }}
 return {goal:nil}.to_json()
}
fn blocks_mount(params){interface_revision+=1 return mount_ui_blocks(params,run_id,interface_revision)}
fn gt_layout(case){
 clear_generated() interface_error=""
 let params={id:"guardian-layout" overlay:true source:if case==2 {"View{width:Fill height:Fit flow:Down for i in 24 {Label{text:\"守护overlay第\"+i+\"行\"}}}"} else {"layout_scroll := ScrollYView{width:Fill height:Fill flow:Down for i in 24 {Label{text:\"守护overlay第\"+i+\"行\"}}}"}}
 if case==3 {params.height=260}
 let mounted=blocks_mount({blocks:[params]})
 start_timeout(0.3,||{
  let block=block_by_id("guardian-layout") let rect=nil let diagnostic=interface_error
  if block!=nil && block.installed {rect=if case==2 {block.container.rect()} else {block.handle.find("layout_scroll").rect()} diagnostic=block.handle.diagnostics()}
  gt_evidence["overlay_case_"+case]={accepted:mounted!=nil rect:rect diagnostic:diagnostic}
  if case==1 {gt_check("无显式高度overlay顶层Fill滚动明确拒绝",mounted==nil && diagnostic!="")}
  if case==3 {gt_check("显式高度overlay顶层Fill滚动实际非零",rect!=nil && rect.height>0 && diagnostic=="")}
  fs.write("guardian-layout-ready-"+case+".json",{case:case}.to_json())
 })
}
fn gt_check(name,passed){gt_checks.push({name:name passed:passed})}
fn gt_route(id,price,duration){
 let now=time_now()
 let route=route_candidate(id,"public_transit",duration,price,now,now,"114.03,22","114.03,22",true,[{walking:{steps:[{polyline:"114,22;114.03,22"}]}}])
 route.request_bound=true route.origin_complete=true route.geometry_ref="polyline_"+id
 return route
}
fn gt_context(){
 if trip_selected_id==nil {trip_new()} trip_replay=false trip_history=nil
 received_at=time_now() arrive_by=received_at+2400
 constraints={budget_cents:5000 currency:"CNY"} user_limits={minutes:40 budget_cents:5000}
 destination_record={name:"合成目的地" longitude:114.03 latitude:22 city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY" source:"synthetic-fixture"}
 position_record={name:"合成起点" longitude:114 latitude:22 source:"synthetic-fixture" mock:true sampled_at_unix:received_at coordinate_system:"GCJ-02" city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}
 candidates=[gt_route("guardian-a",1000,900),gt_route("guardian-b",2000,600)]
}
fn gt_propose(id){return guardian_propose({route_id:id preferences:"尽量便宜" risk_acceptance:"接受供应商估计，不保证到达" basis:"合成原生状态验证"})}
fn gt_poll(){
 if trip_loading || trip_pending_commit!=nil {start_timeout(0.1,||gt_poll()) return}
 if trip_selected_id==nil {trip_new() start_timeout(0.1,||gt_poll()) return}
 if gt_stage==0 {
  let trigger=read_text("guardian-test-resume.json") if trigger==nil {trigger=read_text("guardian-test-go.json")}
  if trigger==nil || trace_state==nil || trigger.parse_json().instance!=trace_state.instance {start_timeout(0.1,||gt_poll()) return}
 }
 if gt_stage==0 && read_text("guardian-test-go.json")!=nil && guardian_goal==nil {
  gt_context() agent_messages=[{role:"user" content:"GUARDIAN_OLD_MODEL_SENTINEL"}] let proposal=gt_propose("guardian-a")
  let rejected=blocks_mount({blocks:[{id:"guardian-bad-scroll" source:"ScrollYView{width:Fill height:Fill flow:Down Label{text:\"没有有限父高度\"}}"}]})
  gt_check("无有限高度的inline滚动容器明确拒绝",rejected==nil && block_by_id("guardian-bad-scroll")==nil)
  blocks_mount({blocks:[{id:"guardian-finite-scroll" height:180 source:"scroll_fixture := ScrollYView{width:Fill height:Fill flow:Down Label{text:\"有限高度原生滚动区域\"} for i in 8 {Label{text:\"守护布局检查第\"+i+\"行\"}}}"}]})
  gt_check("未确认提案不落盘",proposal.success && guardian_goal==nil && gt_saved_text().parse_json().goal==nil)
  fs.write("guardian-test-proposed.json",{proposal:proposal checks:gt_checks}.to_json()) gt_stage=1
 }
 if gt_stage==1 && guardian_goal!=nil {
  let block=block_by_id("guardian-finite-scroll")
  let container_rect=if block!=nil {block.container.rect()} else {nil}
  let scroll_rect=if block!=nil && block.installed {block.handle.find("scroll_fixture").rect()} else {nil}
  gt_evidence.finite={installed:if block!=nil {block.installed} else {false} container:container_rect scroll:scroll_rect diagnostic:if block!=nil && block.installed {block.handle.diagnostics()} else {interface_error}}
  fs.write("guardian-inline-before-restart.json",gt_evidence.finite.to_json())
  gt_check("真实确认保存目标与完整路线",guardian_goal.selected_route.id=="guardian-a" && guardian_goal.version==1 && guardian_goal.selected_route.segments.len()==1 && guardian_goal.confirmations.len()==1)
  fs.write("guardian-test-confirmed.json",{checks:gt_checks}.to_json()) gt_stage=10
 }
 if gt_stage==0 && read_text("guardian-test-resume.json")!=nil && guardian_goal!=nil {
  gt_checks=read_text("guardian-test-confirmed.json").parse_json().checks
  let old=false for message in agent_messages {if route_get(message,"content")=="GUARDIAN_OLD_MODEL_SENTINEL" {old=true}}
  gt_check("重启恢复业务但不恢复旧模型消息",guardian_goal.selected_route.id=="guardian-a" && !old && guardian_pending==nil)
  gt_original=guardian_goal.to_json() gt_context() guardian_mode=true
  let now=time_now() let route=candidates[0]
  gt_check("证据完整时估计成立",guardian_assess(route,now,now+2400,5000).status=="valid")
  gt_check("出发延迟明确失效",guardian_assess(route,now+1800,now+2400,5000).status=="invalid")
  gt_check("已花费用使剩余预算不足",guardian_assess(route,now,now+2400,500).status=="invalid")
  let unknown=route.to_json().parse_json() unknown.waiting_included=false
  gt_check("未知候车不等于失效",guardian_assess(unknown,now,now+2400,5000).status=="unknown")
  gt_check("供应商缺失不等于失效",guardian_assess(nil,now,now+2400,5000).status=="unknown")
  gt_check("过期证据保持未知",guardian_assess(route,now+301,now+2400,5000).status=="unknown")
  let repriced=route.to_json().parse_json() repriced.price_cents=1200 repriced.duration_seconds=950
  repriced.segments[0].walking.cost={duration:"950"} repriced.segments[0].walking.distance="3000"
  gt_check("同线路新用时和费用仍匹配原计划",guardian_plan_key(repriced)==guardian_plan_key(route))
  let different=route.to_json().parse_json() different.segments[0].bus={buslines:[{id:"bus-new" name:"不同公交线路" departure_stop:{id:"stop-a" name:"A"} arrival_stop:{id:"stop-b" name:"B"}}]}
  gt_check("不同公交线路不能认原计划成立",guardian_plan_key(different)!=guardian_plan_key(route))
  gt_propose("guardian-b") gt_check("替代提案不改已确认路线",guardian_goal.to_json()==gt_original && gt_saved_text().parse_json().goal.selected_route.id=="guardian-a")
  gt_version=guardian_pending.proposal_version guardian_reject()
  gt_check("拒绝提案保留原状态",guardian_pending==nil && guardian_goal.to_json()==gt_original)
  gt_propose("guardian-b")
  gt_check("旧提案确认不能覆盖新提案",!guardian_confirm(gt_version) && guardian_goal.to_json()==gt_original)
  gt_version=guardian_pending.proposal_version guardian_reject() agent_active=false phase="complete"
  viewed_route_id="" gt_check("未查看本轮候选不能准备替代",!guardian_prepare_selected().success && guardian_pending==nil)
  viewed_route_id="saved_goal_route" gt_check("旧目标快照不能准备替代",!guardian_prepare_selected().success && guardian_pending==nil)
  viewed_route_id="" guardian_refresh()
  blocks_mount({blocks:[{id:"guardian-candidate-choose" source:"View{width:Fill height:Fit flow:Down Button{text:\"查看合成候选B\" on_click:||emit({action:\"view_route\" id:\"guardian-b\"})}}"}]})
  fs.write("guardian-test-replacement.json",{checks:gt_checks}.to_json()) gt_stage=2
 }
 if gt_stage==2 && guardian_pending!=nil && !gt_local_pending_checked {
  let old=gt_original.parse_json() let pending=guardian_pending.goal
  gt_check("本地准备替代不保存且沿用目标风险",guardian_goal.selected_route.id=="guardian-a" && pending.selected_route.id=="guardian-b" && pending.deadline_ts==old.deadline_ts && pending.total_budget_cents==old.total_budget_cents && pending.preferences==old.preferences && pending.risk_acceptance==old.risk_acceptance)
  gt_local_pending_checked=true
 }
 if gt_stage==2 && guardian_pending==nil && gt_local_pending_checked && !gt_local_rejected && guardian_goal.selected_route.id=="guardian-a" {gt_check("真实拒绝本地替代保持原路线",true) gt_local_rejected=true}
 if gt_stage==2 && guardian_pending==nil && guardian_goal.selected_route.id=="guardian-b" {
  gt_check("真实确认替代才更新路线",guardian_goal.version==2 && guardian_goal.total_budget_cents==5000 && guardian_goal.selected_route.id=="guardian-b" && guardian_goal.confirmations.len()==2)
  gt_propose("guardian-a") gt_version=guardian_pending.proposal_version
  fs.write("guardian-test-progress.json",{version:guardian_goal.version}.to_json()) gt_stage=3
 }
 if gt_stage==3 && guardian_goal.spent_cents==4500 {
  gt_check("真实确认费用派生剩余预算",guardian_snapshot().remaining_budget_cents==500 && guardian_goal.version==3)
  gt_check("目标版本变化后旧确认被拒",!guardian_confirm(gt_version) && guardian_goal.selected_route.id=="guardian-b")
  gt_stage=31
  guardian_report({route_id:"guardian-a"},fn(report){
  gt_check("替代费用不足不伪称原路线已核验",report.success && !report.check.original_plan_verified && report.check.status=="unknown" && report.check.remaining_budget_cents==500)
  gt_check("固定核验区保留具体原因",regex("上次核验依据：","").test(guardian_label()) && regex("未取得原选定剩余路段的新证据","").test(guardian_label()))
  gt_evidence.fixed_label=guardian_label()
  fs.write("guardian-test-storage-ready.json",{checks:gt_checks}.to_json()) gt_stage=4
  })
 }
 if gt_stage==4 && read_text("guardian-test-storage-go.json")!=nil {
  let previous=guardian_goal.to_json() let changed=previous.parse_json() changed.version+=1 changed.spent_cents=4900
  gt_stage=41
  guardian_store(changed,fn(committed){
  gt_check("写入失败不能推进内存目标",!committed && guardian_goal.to_json()==previous)
  fs.write("guardian-test-storage-checked.json",{checks:gt_checks}.to_json()) gt_stage=5
  })
 }
 if gt_stage==5 && read_text("guardian-test-storage-restored.json")!=nil {
  let before=guardian_goal.to_json()
  gt_stage=51
  fs.write("navigation-trips.json","{corrupt") guardian_goal=nil trip_load(||{
  gt_evidence.recovery={before:before after:if guardian_goal!=nil {guardian_goal.to_json()} else {nil} error:guardian_error}
  gt_check("主记录损坏从确认备份恢复且明确说明",guardian_goal!=nil && guardian_error!="")
  guardian_finish()
  gt_stage=52
  })
 }
 if gt_stage==52 && trip_pending_commit==nil && guardian_goal!=nil && guardian_goal.state=="ended" {
  gt_check("结束后不能主动核验",!guardian_recheck()) guardian_delete() gt_stage=53
 }
 if gt_stage==53 && trip_pending_commit==nil && guardian_goal==nil {
  gt_check("删除清除可恢复目标",gt_saved_text().parse_json().goal==nil)
  gt_stage=54 trip_load(||{
  gt_check("删除后再次读取不会从备份复活",guardian_goal==nil)
  clear_generated()
  blocks_mount({blocks:[{id:"guardian-inline-isolated" height:180 source:"inline_scroll := ScrollYView{width:Fill height:Fill flow:Down for i in 8 {Label{text:\"独立inline检查\"}}}"}]})
  gt_stage=6
  start_timeout(0.3,||{
    let block=block_by_id("guardian-inline-isolated") let rect=if block!=nil && block.installed {block.handle.find("inline_scroll").rect()} else {nil}
    gt_evidence.inline_isolated={rect:rect diagnostic:if block!=nil && block.installed {block.handle.diagnostics()} else {interface_error}}
    gt_check("显式高度inline滚动容器实际非零",rect!=nil && rect.height>0)
    gt_layout(1)
  })
  })
 }
 if gt_stage==6 && read_text("guardian-layout-next-1.json")!=nil {gt_layout(2) gt_stage=7}
 if gt_stage==7 && read_text("guardian-layout-next-2.json")!=nil {gt_layout(3) gt_stage=8}
 if gt_stage==8 && read_text("guardian-layout-next-3.json")!=nil {
  fs.write("guardian-test-report.json",{checks:gt_checks evidence:gt_evidence}.to_json()) gt_stage=10
 }
 start_timeout(0.1,||gt_poll())
}
start_timeout(0.2,||gt_poll())
'''

# 只验证异步业务提交边界，不启动手机交互、模型或交通查询。
COMMIT_BOUNDARY_FIXTURE = r'''
let gc_checks=[] let gc_callbacks=0 let gc_primary="" let gc_deleted_generation=0
fn gc_check(name,passed){gc_checks.push({name:name passed:passed})}
fn gc_finish(){fs.write("guardian-commit-report.json",{checks:gc_checks generation:trip_generation}.to_json())}
fn gc_goal(version){
 let now=time_now()
 return {schema:1 state:"active" version:version confirmed_at:now deadline_ts:now+2400 total_budget_cents:5000 currency:"CNY" spent_cents:0 progress:"合成提交边界" preferences:"" risk_acceptance:"供应商估计" destination:{name:"合成目的地" longitude:114.03 latitude:22} selected_route:{id:"gc-route" kind:"public_transit" plan_key:"gc-plan" segments:[] departure_ts:now source_ts:now price_cents:1000 duration_seconds:900} selection_basis:"隔离回归" confirmations:[]}
}
fn gc_start(){
 if trip_loading || trip_pending_commit!=nil {start_timeout(0.05,||gc_start()) return}
 let now=time_now()
 trip_records=[] trip_selected_id=nil trip_next_id=1 trip_generation=0 guardian_goal=nil
 let rows=[] for i in 2 {rows.push({id:"trip-"+(i+1) title:"提交边界" input:"fixture" created_at:now updated_at:now status:"draft" goal:nil snapshot:nil _dirty:true})}
 trip_commit({schema:1 selected_id:"trip-1" next_id:3 trips:rows},fn(committed){
  gc_check("两个实际出行记录提交前置成功",committed && trip_generation==1)
  if !committed {gc_finish() return}
  let goal=gc_goal(1)
  guardian_store(goal,fn(saved){
   gc_callbacks+=1 gc_check("守护成功回调才发布目标与记录",saved && gc_callbacks==1 && guardian_goal.version==1 && trip_by_id("trip-1").goal.version==1 && trip_generation==2 && trip_pending_commit==nil)
   fs.read_async("navigation-trips.json",fn(reply){gc_primary=reply.text gc_guardian_failure()})
  })
  gc_check("守护异步保存成功前不推进内存目标记录或代际",trip_pending_commit!=nil && guardian_goal==nil && trip_by_id("trip-1").goal==nil && trip_generation==1 && gc_callbacks==0)
 })
}
fn gc_guardian_failure(){
 fs.remove("navigation-trips.json") fs.mkdir("navigation-trips.json")
 guardian_store(gc_goal(2),fn(saved){
  gc_callbacks+=1 gc_check("守护写失败回调不推进原目标与记录",!saved && gc_callbacks==2 && guardian_goal.version==1 && trip_by_id("trip-1").goal.version==1 && trip_generation==2 && trip_pending_commit==nil)
  fs.remove("navigation-trips.json") fs.write("navigation-trips.json",gc_primary)
  gc_deleted_generation=trip_generation trip_delete("trip-1")
  gc_check("删除提交完成前保留当前记录",trip_pending_commit!=nil && trip_by_id("trip-1")!=nil && trip_generation==gc_deleted_generation)
  start_timeout(0.05,||gc_deleted())
 })
 gc_check("守护失败事务完成前仍保原目标",guardian_goal.version==1 && trip_by_id("trip-1").goal.version==1 && trip_generation==2)
}
fn gc_deleted(){
 if trip_pending_commit!=nil {start_timeout(0.05,||gc_deleted()) return}
 gc_check("删除完成后内存仅保剩余出行",trip_by_id("trip-1")==nil && trip_selected_id=="trip-2" && trip_generation==gc_deleted_generation+1 && guardian_goal==nil)
 trip_read("navigation-trips.json",fn(primary){
  gc_check("删除后的primary恢复不复活记录或目标",primary!=nil && primary.data.trips.len()==1 && primary.data.trips[0].id=="trip-2" && primary.data.trips[0].goal==nil)
  trip_read("navigation-trips.previous.json",fn(previous){
   gc_check("删除后的previous恢复不复活记录或目标",previous!=nil && previous.data.trips.len()==1 && previous.data.trips[0].id=="trip-2" && previous.data.trips[0].goal==nil)
   fs.write("navigation-trips.json","broken")
   trip_load(||{
    gc_check("主索引损坏经生产load恢复备份仍不复活已删除出行",trip_by_id("trip-1")==nil && trip_selected_id=="trip-2" && trip_records.len()==1 && guardian_goal==nil && guardian_error!="")
    gc_finish()
   })
  })
 })
}
start_timeout(1,||gc_start())
'''


def commit_boundary_source(original):
    return original + '\n' + COMMIT_BOUNDARY_FIXTURE


def run_commit_boundaries(work, jail, original, injected):
    target = jail / 'guardian-commit-report.json'
    until = time.monotonic() + 30
    while not target.exists() and time.monotonic() < until:
        time.sleep(.1)
    assert target.exists(), f'异步提交回归未完成：{work / "native.log"}'
    report = json.loads(target.read_text())
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(), model_called=False,
                  provider_called=False, production_trip_delete=True, production_guardian_store=True,
                  production_trip_load=True)
    report['budget_errors'] = [line for line in (work / 'native.log').read_text().splitlines()
                               if 'budget exceeded' in line or 'instruction limit exceeded' in line]
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert not report['budget_errors'] and all(item['passed'] for item in report['checks']), report
    print(f'PASS: {len(report["checks"])} 项异步守护/删除提交边界；{work / "report.json"}')

# A focused phone interaction group; it shares the existing synthetic Route/context helpers.
PROPOSAL_FOLD_FIXTURE = r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
let gf_case=0 let gf_checks=[]
fn gf_check(name,value){gf_checks.push({name:name passed:value})}
fn gf_propose(){let basis="" for i in 10 {basis+="合成选择依据：当前仅已查路段小计，目的地通达和真实候车尚未核实；确认不保证到达。"}
 let result=guardian_propose({route_id:"guardian-a" preferences:"尽量便宜" risk_acceptance:"接受明确未知" basis:basis})
 gf_check("生产准备新提案保持未保存",result.success && guardian_goal==nil)
}
fn gf_poll(){if gf_case==0 && fs.exists("fold-next.json") {let old=guardian_pending let version=old.goal.version gf_propose() gf_check("同目标版本新提案对象重新折叠",guardian_pending!=old && guardian_pending.goal.version==version && guardian_open_proposal==nil) gf_case=1 fs.write("fold-replaced.json",{checks:gf_checks}.to_json())}
 if gf_case==1 && guardian_pending==nil {gf_check("真实拒绝清提案和展开且未保存",guardian_open_proposal==nil && guardian_goal==nil) gf_propose() gf_case=2 fs.write("fold-rejected.json",{checks:gf_checks}.to_json())}
 if gf_case==2 && guardian_goal!=nil && guardian_pending==nil && trip_pending_commit==nil {gf_check("真实确认完成目标与磁盘事务",guardian_goal.version==1 && guardian_open_proposal==nil && trip_by_id(trip_selected_id).goal==guardian_goal) fs.write("fold-result.json",{checks:gf_checks goal_version:guardian_goal.version}.to_json()) return}
 start_timeout(0.05,||gf_poll())}
start_timeout(0.7,||{run_id+=1 agent_active=false phase="waiting" trip_records=[{id:"trip-1" title:"合成提案折叠" input:"合成原生验证" status:"planned" goal:nil snapshot:nil created_at:time_now() updated_at:time_now() _record_file:nil _dirty:true}] trip_selected_id="trip-1" trip_next_id=2 trip_generation=0 trip_replay=false trip_loading=false guardian_goal=nil guardian_mode=false composer_open=false
 gt_context() candidates[0].request_bound=false candidates[0].endpoint_complete=false gf_propose() render_content() fs.write("fold-ready.json",{summary:guardian_proposal_summary_label() full:guardian_proposal_label()}.to_json()) gf_poll()})
'''
def proposal_fold_source(original):
    for name in ['trace_initialize','trip_load','amap_request']:
        original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
    helpers=FIXTURE[FIXTURE.index('fn gt_route('):FIXTURE.index('fn gt_propose(')]
    return original+'\n'+helpers+'\n'+PROPOSAL_FOLD_FIXTURE

def run_proposal_fold(work,jail,original,injected):
    from test_trip_replay import controls
    import agent,re
    from urllib.parse import urlencode
    def wait(name):
        until=time.monotonic()+20
        while not (jail/name).exists() and time.monotonic()<until:time.sleep(.05)
        return json.loads((jail/name).read_text())
    ready=wait('fold-ready.json');time.sleep(.4);m=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text());assert m
    def request(route,**args):return agent.remote({'port':int(m[1])},route+('?' +urlencode(args) if args else ''))
    rows,capture,click,_=controls(work,request)
    def scroll(dy):request('m',k='scroll',x=210,y=680,dy=dy,precise=1,wait=1);time.sleep(.12)
    def seek(widget):
        for _ in range(18):
            found=[r for r in rows() if r.get('i')==widget and r['r'][3]>=30]
            if found:return found[0]
            scroll(220)
        raise AssertionError('widget unreachable '+widget)
    def tap(widget):
        r=seek(widget);x,y,w,h=r['r'];request('click',x=x+w/2,y=y+h/2,wait=1);time.sleep(.2)
    initial=capture('fold-compact');summary=next(r for r in initial if r.get('i')=='guardian_proposal_summary')
    checks=[{'name':'长unknown提案默认紧凑且真实确认未构造','passed':summary['r'][3]<300 and not any(r.get('i')=='guardian_accept' for r in initial) and '费用：' in ready['summary'] and '到达范围：' in ready['summary'] and '未知' in ready['summary']}]
    tap('guardian_proposal_toggle');seek('guardian_accept');expanded=capture('fold-expanded-confirm-reachable');checks.append({'name':'实际展开原全文且真实确认可滚达','passed':any(r.get('i')=='guardian_accept' and r['r'][3]>=30 for r in expanded)})
    for _ in range(12):scroll(-220)
    tap('guardian_proposal_toggle');collapsed=capture('fold-collapsed');checks.append({'name':'实际收起后确认隐藏且保摘要','passed':not any(r.get('i')=='guardian_accept' for r in collapsed) and any(r.get('i')=='guardian_proposal_summary' for r in collapsed)})
    tap('guardian_proposal_toggle');(jail/'fold-next.json').write_text('{}');wait('fold-replaced.json');time.sleep(.3);replaced=capture('fold-new-proposal');checks.append({'name':'同目标新对象默认折叠实际按钮不继承','passed':not any(r.get('i')=='guardian_accept' for r in replaced) and any(r.get('i')=='guardian_proposal_toggle' and r.get('t')=='查看提案' for r in replaced)})
    tap('guardian_decline');wait('fold-rejected.json');tap('guardian_proposal_toggle');tap('guardian_accept');result=wait('fold-result.json');capture('fold-confirmed');checks.extend(result['checks'])
    index=json.loads((jail/'navigation-trips.json').read_text())['data'];entry=next(e for e in index['trips'] if e['id']==index['selected_id']);goal=read_record(jail,entry['file'])['goal'];checks.append({'name':'确认经生产存储读回goal版本1','passed':goal['version']==1})
    report={'checks':checks,'main_sha256':hashlib.sha256(original.encode()).hexdigest(),'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'复用existing synthetic Route/context，生产prepare/summary/full/真实toggle/reject/confirm/store与磁盘read；无模型DSL或交通。只覆盖新增折叠交互，不重跑旧guardian全矩阵。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks) and not report['native_errors'],str(work/'report.json')
