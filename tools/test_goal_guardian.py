"""出行目标守护的隔离原生检查，由 smoke.py --guardian 启动。"""
import hashlib
import json
import time


def source(original):
    assert 'fn guardian_propose(' in original, '目标守护实现尚未就绪'
    return original + '\n' + FIXTURE


def run(work, jail, request, stop, launch, original, injected):
    def stored_goal():
        index = json.loads((jail / 'navigation-trips.json').read_text())['data']
        entry = next(e for e in index['trips'] if e['id'] == index['selected_id'])
        return json.loads((jail / entry['file']).read_text())['data']['goal']

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
fn gt_saved_text(){let saved=trip_read("navigation-trips.json") if saved==nil {return nil} for trip in saved.data.trips {if trip.id==saved.data.selected_id {return {goal:trip.goal}.to_json()}} return {goal:nil}.to_json()}
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
  let report=guardian_report({route_id:"guardian-a"})
  gt_check("替代费用不足不伪称原路线已核验",report.success && !report.check.original_plan_verified && report.check.status=="unknown" && report.check.remaining_budget_cents==500)
  gt_check("固定核验区保留具体原因",regex("上次核验依据：","").test(guardian_label()) && regex("未取得原选定剩余路段的新证据","").test(guardian_label()))
  gt_evidence.fixed_label=guardian_label()
  fs.write("guardian-test-storage-ready.json",{checks:gt_checks}.to_json()) gt_stage=4
 }
 if gt_stage==4 && read_text("guardian-test-storage-go.json")!=nil {
  let previous=guardian_goal.to_json() let changed=previous.parse_json() changed.version+=1 changed.spent_cents=4900
  let stored=guardian_store(changed)
  gt_check("写入失败不能推进内存目标",!stored && guardian_goal.to_json()==previous)
  fs.write("guardian-test-storage-checked.json",{checks:gt_checks}.to_json()) gt_stage=5
 }
 if gt_stage==5 && read_text("guardian-test-storage-restored.json")!=nil {
  let before=guardian_goal.to_json()
  fs.write("navigation-trips.json","{corrupt") guardian_goal=nil trip_load()
  gt_evidence.recovery={before:before after:if guardian_goal!=nil {guardian_goal.to_json()} else {nil} error:guardian_error}
  gt_check("主记录损坏从确认备份恢复且明确说明",guardian_goal!=nil && guardian_error!="")
  guardian_store(guardian_goal)
  gt_check("结束后不能主动核验",guardian_finish() && guardian_goal.state=="ended" && !guardian_recheck())
  gt_check("删除清除可恢复目标",guardian_delete() && guardian_goal==nil && gt_saved_text().parse_json().goal==nil)
  trip_load()
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
