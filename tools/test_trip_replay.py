"""复用私有真实生成记录，检查侧栏切换与冷启动，不调用模型。"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import time


def source(original):
    return original


def prepare(jail):
    root = Path(os.environ.get('NAV_TRIP_REPLAY_STATE', 'build/research/journey-guardian/online/private-state/home/apps/os.agentic26-navigation'))
    assert (root / 'navigation-trips.json').exists(), '先提供真实保存记录：NAV_TRIP_REPLAY_STATE'
    for pattern in ('navigation-trips*.json', 'navigation-trip-trip-*.json', 'guardian-goal*.json'):
        for path in root.glob(pattern):
            shutil.copyfile(path, jail / path.name)


def run(work, jail, request, stop, launch, original, injected):
    checks = []

    def rows():
        return [r for r in json.loads(request('snap'))['s'] if r.get('ty') != 'Splash']

    def capture(name):
        value = rows()
        (work / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2))
        (work / (name + '.png')).write_bytes(request('g', raw=1))
        return value

    def click(widget=None, text=None):
        matches = [r for r in rows() if r['ty'] == 'Button' and r['r'][3] > 20 and
                   ((widget and r.get('i') == widget) or (text and text in r.get('t', '')))]
        assert len(matches) == 1, (widget, text, matches)
        x, y, w, h = matches[0]['r']
        request('click', x=x+w/2, y=y+h/2, wait=1)
        time.sleep(.5)

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
        return index, {e['id']: json.loads((jail / e['file']).read_text())['data'] for e in index['trips']}

    index, records = disk()
    real = next(r for r in records.values() if r.get('snapshot') and len(r['snapshot']['blocks']) >= 3)
    legacy = next(r for r in records.values() if r.get('goal') and r['id'] != real['id'])
    before = {r['id']: {'goal': r['goal'], 'snapshot': r['snapshot']} for r in (real, legacy)}
    android()
    capture('real-cold-start')
    for number, record in enumerate((legacy, real, legacy, real), 1):
        click(widget='trip_menu')
        click(text=record['title'])
        current = capture(f'switch-{number}')
        assert not any(r.get('i') == 'trip_new_button' and r['r'][3] > 0 for r in current), '切换未完成，侧栏仍打开'
        assert next(r['t'] for r in current if r.get('i') == 'trip_title').startswith(record['title']), '详情仍是旧项'
        assert disk()[0]['selected_id'] == record['id']
        if record['id'] == real['id']:
            assert any(r['ty'] == 'Button' and '查看路线 2' in r.get('t', '') for r in current)
        checks.append({'name': f'真实材料侧栏切换{number}完成且显示正确详情', 'passed': True})
    stop()
    launch('trip-real-restart')
    android()
    current = capture('real-restarted')
    assert any(r.get('i') == 'trip_title' and '历史详情' in r.get('t', '') for r in current)
    click(text='查看路线 2')
    request('m', k='scroll', x=220, y=650, dy=1800, precise=1, wait=1)
    time.sleep(.5)
    current = capture('restored-detail')
    assert any(r.get('i') == 'route_map' and r['ty'] == 'Image' and r['r'][3] > 0 for r in current), '历史详情地图控件未恢复'
    checks.append({'name': '真实原稿重启后卡片事件与地图详情可打开', 'passed': True})
    _, after = disk()
    assert all(after[key]['goal'] == value['goal'] and after[key]['snapshot'] == value['snapshot'] for key, value in before.items())
    checks.append({'name': '历史切换不改写保存目标与快照', 'passed': True})
    trace = []
    for path in (jail / 'dev-trace').glob('*/vm-*/*.jsonl'):
        trace.extend(json.loads(line) for line in path.read_text().splitlines())
    assert not any(e.get('event') in ('model_dispatch', 'model_request', 'tool_call') for e in trace), '只读恢复触发了业务查询'
    checks.append({'name': '切换重启均不触发模型或业务工具', 'passed': True})
    logs = '\n'.join(p.read_text(errors='replace') for p in work.glob('*.log'))
    assert 'script time budget exceeded' not in logs and 'not a char boundary' not in logs, '原生同步回调有执行异常'
    report = {'checks': checks, 'mode': 'macOS arm64，宿主 Android 样式，非 Android 真机',
              'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
              'real_record_bytes': len(json.dumps(real, ensure_ascii=False).encode()),
              'route_count': len(real['snapshot']['route_data']), 'block_count': len(real['snapshot']['blocks']),
              'model_called': False, 'native_execution_clean': True}
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f'PASS: {len(checks)} 项真实材料回放检查；{work / "report.json"}')
