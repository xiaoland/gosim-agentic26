"""固定外壳的实际触控检查；查询采用待完成传输stub，不请求模型。"""
import json
import os
from pathlib import Path
import time
import test_trip_replay as replay


def prepare(jail):
    replay.prepare(jail, 'build/research/ui-ux-foundation/replay-seed-private')
    config_path = jail / 'private-config.json'
    config = json.loads(config_path.read_text())
    old = Path('build/research/journey-guardian/online/private-state/home/apps/os.agentic26-navigation/private-config.json')
    # 只复用地图凭据展示已保存几何；模型传输在source中明确拦截。
    if old.exists():
        config['amap_api_key'] = json.loads(old.read_text())['amap_api_key']
    config_path.write_text(json.dumps(config))
    config_path.chmod(0o600)


def source(original):
    boundary = 'record.host_request_id = host.request("model.chat", body, fn(reply){'
    assert original.count(boundary) == 1
    return original.replace(boundary, 'record.host_request_id = ux_pending_model(body, fn(reply){') + '\n' + FIXTURE


FIXTURE = r'''
let ux_overlay_seen="" let ux_inspect_seen=""
fn ux_pending_model(body,done){fs.write("ux-model-pending.json",{instance:trace_state.instance trip_id:trip_selected_id run:run_id}.to_json()) return nil}
fn ux_owned(path){let text=read_text(path) if text==nil || trace_state==nil {return nil} let value=text.parse_json() if value.instance!=trace_state.instance {return nil} return value}
fn ux_poll(){
 let request=ux_owned("ux-inspect.json")
 if request!=nil && request.nonce!=ux_inspect_seen {
  ux_inspect_seen=request.nonce
  fs.write("ux-inspected-"+request.nonce+".json",{trip_id:trip_selected_id trip_replay:trip_replay phase:phase agent_active:agent_active goal_state:if guardian_goal!=nil {guardian_goal.state} else {nil} spent_cents:if guardian_goal!=nil {guardian_goal.spent_cents} else {nil} proposal:guardian_pending!=nil interface_error:interface_error content_rect:ui.content.rect()}.to_json())
 }
 let overlay=ux_owned("ux-overlay.json")
 if overlay!=nil && overlay.nonce!=ux_overlay_seen {
  ux_overlay_seen=overlay.nonce interface_revision+=1
  mount_ui_blocks({blocks:[{id:"ux-anchor-check" overlay:true source:"View{width:Fill height:Fit flow:Down spacing:12 padding:12 ux_overlay_label := Label{text:\"有限overlay锚点检查（合成内容）\"} Button{text:\"返回原内容\" height:48 on_click:||hide_self()} for i in 14 {Label{text:\"原生可滚动检查行\"+i}}}"}]},run_id,interface_revision)
 }
 start_timeout(0.1,||ux_poll())
}
start_timeout(0.1,||ux_poll())
'''


def run(work, jail, request, stop, launch, original, injected):
    import hashlib
    rows, capture, click, android = replay.controls(work, request)
    checks = []
    counter = 0

    def check(name, value, required=True):
        checks.append({'name': name, 'passed': bool(value)})
        if required:
            assert value, name

    def inspect():
        nonlocal counter
        counter += 1
        marker = next(json.loads(r['t']) for r in rows() if r.get('i') == 'trace_identity')
        (jail / 'ux-inspect.json').write_text(json.dumps({'instance': marker['instance'], 'nonce': str(counter)}))
        path = jail / f'ux-inspected-{counter}.json'
        for _ in range(50):
            if path.exists():
                return json.loads(path.read_text())
            time.sleep(.1)
        raise AssertionError('外壳检查回执未到达')

    def shown(name):
        return next((r for r in rows() if r.get('i') == name and r['r'][3] > 0), None)

    def point(row):
        x, y, w, h = row['r']
        request('click', x=x+w/2, y=y+h/2, wait=1)
        time.sleep(.4)

    def select(title):
        click(widget='trip_menu')
        matches = [r for r in rows() if r['ty'] == 'Label' and r.get('t') == title and r['r'][0] < 320]
        assert len(matches) == 1, matches
        point(matches[0])

    def fill(name, text):
        entry = shown(name)
        assert entry
        point(entry)
        for _ in range(len(entry.get('val', entry.get('t', ''))) + 3):
            request('k', c='Backspace', wait=1)
            request('k', c='Delete', wait=1)
        request('t', t=text, wait=1)
        time.sleep(.3)
        assert shown(name).get('val') == text

    def disk():
        index = json.loads((jail / 'navigation-trips.json').read_text())['data']
        return index, {e['id']: json.loads((jail / e['file']).read_text())['data'] for e in index['trips']}

    index, records = disk()
    real = next(r for r in records.values() if r.get('snapshot') and len(r['snapshot']['blocks']) >= 3)
    legacy = next(r for r in records.values() if r.get('goal'))
    try:
        android()
        if os.environ.get('NAV_UX_RUNNING_ONLY') == '1':
            click(widget='trip_menu')
            click(widget='trip_new_button')
            fill('sentence', '40分钟内到机场，预算80元')
            request('k', c='Escape', wait=1)
            click(widget='query_button')
            current = capture('running-status')
            labels = [r.get('t', '') for r in current if r['r'][3] > 0]
            check('运行状态明确正在规划且无中断矛盾', any('正在规划' in t for t in labels) and not any('中断' in t for t in labels))
            check('运行停止入口可达', inspect()['agent_active'] and shown('query_button')['t'] == '停止')
            if shown('sentence') is None:
                click(text='调整要求')
            point(shown('sentence'))
            request('k', c='Enter', wait=1)
            check('运行中Enter保留任务', inspect()['agent_active'])
            request('k', c='Escape', wait=1)
            click(widget='query_button')
            current = capture('running-stopped')
            check('显式停止结束等待', not inspect()['agent_active'])
            check('停止后状态不再显示正在规划', not any('正在规划' in r.get('t', '') and r['r'][3] > 0 for r in current))
        else:
            current = capture('history-first-screen')
            check('历史首屏收起输入并显示路线卡片', shown('sentence') is None and any('查看路线 2' in r.get('t', '') and r['r'][3] > 20 for r in current))
            check('长标题保持单行且主内容空间增加', shown('trip_title')['r'][3] <= 48 and shown('content')['r'][1] < 270)
            history = shown('history_info')
            check('历史状态具有实际可见文字', history is not None and '历史' in history.get('t', ''), required=True)
            click(widget='trip_menu')
            current = capture('drawer')
            check('抽屉遮罩可见', shown('trip_scrim') is not None)
            check('抽屉新建动作达到44像素底线', shown('trip_new_button')['r'][3] >= 44)
            request('click', x=375, y=400, wait=1)
            time.sleep(.4)
            check('点遮罩关闭且不操作底层', shown('trip_new_button') is None and inspect()['trip_id'] == real['id'] and not inspect()['agent_active'])
            click(text='调整要求')
            capture('requirements-expanded')
            check('展开完整原要求并说明新建语义', shown('sentence').get('val') == real['input'] and any('新建一条出行' in r.get('t', '') for r in rows()))
            click(text='收起要求')
            check('收起历史要求同时隐藏查询动作', shown('sentence') is None and shown('query_button') is None)
            marker = next(json.loads(r['t']) for r in rows() if r.get('i') == 'trace_identity')
            (jail / 'ux-overlay.json').write_text(json.dumps({'instance': marker['instance'], 'nonce': 'first'}))
            time.sleep(.6)
            current = capture('collapsed-composer-overlay')
            label = shown('ux_overlay_label')
            check('收起输入后的overlay位于固定头部以下', label is not None and label['r'][1] >= shown('trip_context')['r'][1]+shown('trip_context')['r'][3])
            click(text='返回原内容')
            check('关闭overlay恢复旧卡片', any('查看路线 2' in r.get('t', '') and r['r'][3] > 20 for r in rows()))
            click(text='查看路线 2')
            request('m', k='scroll', x=220, y=650, dy=1800, precise=1, wait=1)
            time.sleep(1)
            current = capture('history-map')
            check('历史卡片打开原路线与地图控件', shown('route_map') is not None and any('E36路' in r.get('t', '') for r in current))
            click(text='返回列表')
            check('详情返回保留历史页', inspect()['trip_id'] == real['id'])
            click(widget='trip_menu')
            click(widget='trip_new_button')
            capture('empty-new-trip')
            check('新建草稿输入为空', shown('sentence').get('val') == '')
            fill('sentence', '40分钟内到机场，预算80元')
            request('k', c='Enter', wait=1)
            time.sleep(.3)
            check('多行Enter不提交查询', not inspect()['agent_active'] and not (jail / 'ux-model-pending.json').exists())
            request('k', c='Escape', wait=1)
            click(widget='query_button')
            time.sleep(.4)
            capture('running')
            check('规划中停止入口可达', inspect()['agent_active'] and shown('query_button')['t'] == '停止')
            if shown('sentence') is None:
                click(text='调整要求')
            point(shown('sentence'))
            request('k', c='Enter', wait=1)
            check('运行中Enter不触发停止', inspect()['agent_active'])
            request('k', c='Escape', wait=1)
            click(widget='query_button')
            check('停止按钮结束本次等待', not inspect()['agent_active'])
            select(legacy['title'])
            capture('guardian-summary')
            check('目标主次操作可见且管理折叠', shown('guardian_recheck_button')['r'][3] >= 44 and shown('guardian_details_button') is not None and not any(r.get('t') == '删除目标' and r['r'][3] > 0 for r in rows()))
            click(widget='guardian_details_button')
            fill('guardian_spent', '191')
            capture('guardian-fees-keyboard')
            check('键盘打开时费用字段仍在可见区域', shown('guardian_spent')['r'][1]+shown('guardian_spent')['r'][3] < 577)
            request('k', c='Escape', wait=1)
            # 先确认原生键盘关闭不丢内容，再以真实按钮提交。
            submit = shown('guardian_progress_submit')
            if submit is None or submit['r'][1] > 790:
                request('m', k='scroll', x=220, y=550, dy=300, precise=1, wait=1)
                time.sleep(.3)
            click(widget='guardian_progress_submit')
            check('费用编辑通过本地动作保存', inspect()['spent_cents'] == 19100)
            capture('guardian-progress-saved')
            click(widget='guardian_details_button')
            request('m', k='scroll', x=220, y=600, dy=600, precise=1, wait=1)
            time.sleep(.3)
            click(text='删除目标')
            capture('delete-goal-confirmation')
            check('目标删除有明确保留出行确认', shown('trip_delete_cancel') is not None and shown('trip_delete_confirm') is not None and disk()[1][legacy['id']]['goal'] is not None)
            click(widget='trip_delete_cancel')
            check('取消目标删除保持业务状态', disk()[1][legacy['id']]['goal'] is not None)
            click(widget='trip_close')
            click(text='删除目标')
            click(widget='trip_delete_confirm')
            check('确认只删除目标保留出行', legacy['id'] in disk()[1] and disk()[1][legacy['id']]['goal'] is None)
            if shown('trip_new_button') is None:
                click(widget='trip_menu')
            if shown('trip_manage_button')['t'] == '管理当前出行':
                click(widget='trip_manage_button')
            click(widget='trip_delete_button')
            capture('delete-trip-confirmation')
            click(widget='trip_delete_cancel')
            check('取消整条删除仍保留记录', legacy['id'] in disk()[1])
            click(widget='trip_delete_button')
            click(widget='trip_delete_confirm')
            check('确认整条删除且不伤真实规划记录', legacy['id'] not in disk()[1] and real['id'] in disk()[1])
    finally:
        logs = '\n'.join(p.read_text(errors='replace') for p in work.glob('*.log'))
        report = {'checks': checks, 'mode': 'macOS arm64宿主Android样式，非Android真机',
                  'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
                  'provider_model_requests': 0, 'model_transport': '显式pending stub，用于查询/停止UI',
                  'native_budget_exceeded': 'script time budget exceeded' in logs,
                  'native_utf8_panic': 'not a char boundary' in logs,
                  'native_render_errors': 'on_render closure failed' in logs}
        (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert not report['native_budget_exceeded'] and not report['native_utf8_panic'] and not report['native_render_errors'], report
    assert all(c['passed'] for c in checks), report
    print(f'PASS: {len(checks)} 项外壳UI检查；{work / "report.json"}')
