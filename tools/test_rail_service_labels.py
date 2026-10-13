"""真实固定班次与整条Route的时间标签边界，不重新查询交通供应商。"""
import hashlib
import json
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def prepare(jail):
    directory = Path(jail) / 'rail-label-fixture'
    directory.mkdir()
    captured = ROOT / 'build/research/rail-integration/e2e/round30/route2_33-private.json'
    (directory / 'route.json').write_bytes(captured.read_bytes())

FIXTURE = r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
fn rl_begin(){fs.read_async("rail-label-fixture/route.json",fn(result){if !result.success {return}
 let route=result.text.parse_json()
 start_timeout(0.01,||{
  let labelled=rail_service_labels(route.legs[1].rail_service)
  let legs=route_leg_facts(route)
  fs.write("rail-label-result.json",{service:labelled legs:legs nil_service:rail_service_labels(nil) route_duration_seconds:route.duration_seconds route_duration_label:duration_text(route.duration_seconds) route_arrival_ts:route.estimated_arrival_ts route_arrival_label:guardian_deadline(route.estimated_arrival_ts)}.to_json())
  let state={session:"rail-label-fixture" instance:"vm-1" directory:"rail-label-trace" seq:0 written_seq:0 segment:0 segment_bytes:0 run:run_id incomplete:false keys:[]}
  fs.write(state.directory+"/status.json",trace_status(state).to_json())
  trace_failed_status(state)
 })
})}
start_timeout(0.8,||rl_begin())
'''

def source(original):
    for name in ['trace_initialize', 'trip_load', 'agent_pump', 'amap_request']:
        original = original.replace(f'fn {name}(', f'fn product_{name}(', 1)
    return original + '\n' + FIXTURE

def run(work, jail, original, injected):
    for _ in range(500):
        status_path = jail / 'rail-label-trace/status.json'
        if status_path.exists() and json.loads(status_path.read_bytes()).get('state') == 'incomplete':
            break
        time.sleep(.02)
    actual = json.loads((jail / 'rail-label-result.json').read_bytes())
    captured = json.loads((jail / 'rail-label-fixture/route.json').read_bytes())
    service = captured['legs'][1]['rail_service']
    labelled = actual['service']
    labels = {'departure_label':'2026-10-12 07:50（北京时间）', 'arrival_label':'2026-10-12 09:09（北京时间）', 'duration_label':'约 79 分钟'}
    checks = [
        {'name':'实际固定班次epoch与原字段不变并给出07:50到09:09及79分钟', 'passed':all(labelled.get(k)==v for k,v in service.items()) and all(labelled[k]==v for k,v in labels.items())},
        {'name':'整Route保原epoch与571分钟09:11且不混用服务时刻', 'passed':actual['route_duration_seconds']==captured['duration_seconds'] and actual['route_arrival_ts']==captured['estimated_arrival_ts'] and actual['route_duration_label']=='约 571 分钟' and actual['route_arrival_label']=='2026-10-12 09:11（北京时间）'},
        {'name':'公开腿投影继承服务标签且nil服务仍nil', 'passed':actual['legs'][1]['rail_service']==labelled and actual['legs'][0]['rail_service'] is None and actual['legs'][2]['rail_service'] is None and actual['nil_service'] is None},
        {'name':'直接trace_failed_status独立入口落盘incomplete', 'passed':json.loads(status_path.read_bytes())['state']=='incomplete'},
    ]
    report={'checks':checks,'product_source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed_labels':labels,'route_labels':{'duration':actual['route_duration_label'],'arrival':actual['route_arrival_label']},'fixture_boundary':'使用round30真实公开Route与服务；直接调用失败状态helper，不冒称写片故障或hardbail覆盖。','model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l]}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in checks),str(work/'report.json')
