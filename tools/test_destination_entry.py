"""用真实 T3 地点与步行响应验证目的地入口绑定；原件仅进入隔离 jail。"""
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'build/research/rail-integration/t3-endpoint'


def prepare(jail):
    directory = Path(jail) / 'entry-fixture'
    directory.mkdir()
    for name in ['production-text-t3', 'endpoint-to-t3-entrance']:
        original = EVIDENCE / f'{name}.json'
        data = json.loads(original.read_text())
        assert data['response']['status'] == '1'
        (directory / f'{name}.json').write_bytes(original.read_bytes())
    original_pois = json.loads((EVIDENCE / 'production-text-t3.json').read_text())['response']['pois']
    target = next(poi for poi in original_pois if poi['id'] == 'B0FFFZRC7K')
    missing = {key: value for key, value in target.items() if key != 'entr_location'}
    door = dict(target, name=target['name']+'1号门')
    exit_only = dict(missing, exit_location=target['entr_location'])
    (directory / 'negative-pois.json').write_text(json.dumps([missing, door, exit_only], ensure_ascii=False))

FIXTURE = r'''
let de_negatives=nil
let de_checks=[] let de_poi=nil let de_walk=nil let de_bound=nil let de_candidate=nil let de_stage="load" let de_result=nil let de_begins=0
fn de_check(name,passed){de_checks.push({name:name passed:passed}) fs.write("entry-progress.json",{stage:de_stage checks:de_checks}.to_json())}
fn de_finish(){fs.write("entry-report.json",{checks:de_checks old_center_gap:route_endpoint_gap(de_walk.route.origin,coord_text(de_poi)) entry_gap:route_endpoint_gap(route_leg_endpoint(de_walk.route.paths[0].steps,false),destination_coord(de_bound)) begins:de_begins}.to_json())}
fn de_read(path,done){fs.read_async("entry-fixture/"+path,fn(reply){done(reply.text.parse_json())})}
fn agent_pump(token){}
fn agent_begin(){de_begins+=1
 if de_stage=="guardian_entry" {
  de_check("主动guardian沿已存入口绑定不重新选择",destination_coord(destination_record)==destination_coord(de_bound) && destination_record.routing_point.ref==de_bound.routing_point.ref)
  let legacy={} for key value in de_poi {if key!="routing_point" && key!="destination_access" {legacy[key]=value}}
  guardian_goal.destination=legacy
  de_stage="guardian_legacy" start_task_ready("4小时内到机场，预算200",true)
 } elif de_stage=="guardian_legacy" {
  de_check("旧无binding guardian历史保中心且不自动改写",route_get(destination_record,"routing_point")==nil && coord_text(destination_record)==coord_text(de_poi) && destination_coord(destination_record)==coord_text(de_poi))
  agent_active=false de_finish()
 }
}
fn agent_tool_result(result){de_result=result
 de_check("真实walk接驳完整回执以destination结束且入口边界未知",result.success && result.routes.len()==1 && result.completed_candidate_ids.len()==1 && result.routes[0].destination_access.interior_status=="unknown" && result.routes[0].destination_access.floor_status=="unknown" && result.routes[0].destination_access.security_status=="unknown" && result.routes[0].cost.full_journey_amount_cents==nil && result.routes[0].assessment.budget_status=="unknown" && result.routes[0].assessment.deadline_status=="unknown")
 de_candidate=candidates[candidates.len()-1]
 fs.write("entry-access-types.json",{target_kind_string:de_candidate.destination_access.target_kind.is_string() entry_string:de_candidate.destination_access.routing_point.ref.is_string()}.to_json())
 de_check("真实walking几何3.58米通过25米但不宣称内部完整",de_candidate.endpoint_complete && de_candidate.request_bound && de_candidate.endpoint_gap_m<4 && de_candidate.endpoint_gap_m>3 && de_candidate.node_ref=="destination")
 de_stage="save" agent_active=false phase="waiting" ui_facts_revision+=1
 let now=time_now() let goal={schema:1 state:"active" version:1 confirmed_at:now deadline_ts:now+14400 total_budget_cents:20000 currency:"CNY" spent_cents:0 progress:"" preferences:"" risk_acceptance:"仅设施入口；内部未知" destination:de_bound selected_route:guardian_materialize(de_candidate) selection_basis:"实际入口步行原件" confirmations:[]}
 let trip={id:"trip-1" title:de_bound.name input:"入口绑定回归" created_at:now updated_at:now status:"confirmed" goal:goal snapshot:nil _dirty:true}
 trip_records=[] trip_selected_id=nil trip_generation=0 trip_next_id=1
 trip_commit({schema:1 selected_id:"trip-1" next_id:2 trips:[trip]},fn(committed){
  de_check("绑定目标真实提交",committed)
  trip_save_current("confirmed",fn(saved){
   trip_read("navigation-trips.json",fn(read){
    let record=read.data.trips[0] let destination=record.goal.destination
    de_check("同VM保存读回入口来源与canonical中心均保留",saved && destination.routing_point.ref==de_bound.routing_point.ref && coord_text(destination)==coord_text(de_poi) && destination_coord(destination)==destination_coord(de_bound) && record.snapshot.route_data[0].destination_access.target_kind=="amap_poi_entrance" && record.snapshot.facts.destination.routing_point.source=="amap-poi-entrance")
    guardian_goal=record.goal de_stage="guardian_entry" start_task_ready("4小时内到机场，预算200",true)
   })
  })
 })
}
fn de_begin(raw){
 let data=raw.response let target=nil for poi in data.pois {if poi.id=="B0FFFZRC7K" {target=poi}}
 let parsed=parse_pois({pois:[target]},raw.source_ts,false) de_poi=parsed[0] de_poi.city=de_poi.city_metadata.city de_poi.citycode=de_poi.city_metadata.citycode de_poi.adcode=de_poi.city_metadata.adcode de_poi.currency=de_poi.city_metadata.currency de_bound=bind_destination_poi(de_poi)
 de_check("真实T3中心不变且入口独立可引用来源",coord_text(de_poi)=="113.81184,22.627554" && de_poi.coordinate_basis=="location" && de_bound.routing_point.ref=="entrance:B0FFFZRC7K" && destination_coord(de_bound)=="113.814563,22.6246" && de_bound.routing_point.source=="amap-poi-entrance" && de_bound.routing_point.coordinate_basis=="entr_location" && de_bound.routing_point.canonical_poi_ref=="poi:B0FFFZRC7K" && de_bound.routing_point.queried_at==raw.source_ts)
 let missing_poi=parse_pois({pois:[de_negatives[0]]},raw.source_ts,false)[0]
 let door=parse_pois({pois:[de_negatives[1]]},raw.source_ts,false)[0]
 let exit_poi=parse_pois({pois:[de_negatives[2]]},raw.source_ts,false)[0]
 de_check("缺入口具体门仅exit均不替换中心",route_get(bind_destination_poi(missing_poi),"routing_point")==nil && route_get(bind_destination_poi(door),"routing_point")==nil && route_get(bind_destination_poi(exit_poi),"routing_point")==nil)
 run_id+=1 agent_active=true phase="running" trip_replay=false guardian_goal=nil ui_blocks=[]
 position_record={id:"entry-fixture-origin" mock:true sampled_at_unix:time_now() coordinate_system:"GCJ-02" name:"真实末端接驳起点" longitude:113.813082 latitude:22.625 source:"recorded-amap-walk" city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}
 destination_record=de_bound poi_records=[de_poi] constraints={budget_cents:20000 currency:"CNY"} user_limits={minutes:240 budget_cents:20000} received_at=time_now() arrive_by=received_at+14400 route_nodes={} route_prefixes={} candidates=[] prepare_route_graph_base()
 de_check("canonical与entry引用一致路由destination节点且canonicalPOI保持中心",coord_text(route_node("poi:B0FFFZRC7K"))==coord_text(de_poi) && coord_text(route_target_node("poi:B0FFFZRC7K"))==destination_coord(de_bound) && coord_text(route_target_node("entrance:B0FFFZRC7K"))==destination_coord(de_bound) && coord_text(route_node("destination"))==destination_coord(de_bound))
 let old=route_candidate("old-center","walking",208,0,time_now(),time_now(),de_walk.route.origin,coord_text(de_poi),true,[])
 de_check("旧实际末端对中心311米仍false不放宽25",old.endpoint_gap_m>300 && old.endpoint_gap_m<320 && !old.endpoint_complete)
 de_stage="extend" active_tool={id:"entry-walk" function:{name:"extend_route"}}
 accept_route_extension(route_prefixes["origin"],route_node("origin"),route_target_node("poi:B0FFFZRC7K"),"walk",de_walk,time_now(),time_now(),run_id)
}
start_timeout(2,||de_read("endpoint-to-t3-entrance.json",fn(walk){de_walk=walk.response de_read("negative-pois.json",fn(negative){de_negatives=negative de_read("production-text-t3.json",fn(raw){de_begin(raw)})})}))
'''


def source(original):
    injected = original
    for name in ['agent_begin', 'agent_pump', 'agent_tool_result']:
        assert f'fn {name}(' in injected
        injected = injected.replace(f'fn {name}(', f'fn product_{name}(', 1)
    return injected + '\n' + FIXTURE


def run(work, jail, original, injected):
    report = None
    for _ in range(600):
        path = jail / 'entry-report.json'
        if path.exists():
            report = json.loads(path.read_text())
            break
        if '[E]' in (work / 'native.log').read_text():
            break
        time.sleep(.05)
    errors = [line for line in (work / 'native.log').read_text().splitlines() if '[E]' in line]
    result = report or {'incomplete': True, 'progress': json.loads((jail / 'entry-progress.json').read_text()) if (jail / 'entry-progress.json').exists() else None}
    result.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(), model_called=False,
                  provider_called=False, native_errors=errors, recorded_real_supplier_data=True,
                  fixture_boundary='原始POI和walking响应；只恢复对应T3主POI，缺入口/具体门/exit为明确负例；交通时间以当前隔离入口评估，不声称新查询。')
    if report:
        from test_trip_snapshot import read_record
        index = json.loads((jail / 'navigation-trips.json').read_text())['data']
        record = read_record(jail, index['trips'][0]['file'])
        walking = json.loads((jail / 'entry-fixture/endpoint-to-t3-entrance.json').read_text())['response']
        result['saved_real_walking_segments_equal'] = record['snapshot']['route_data'][0]['segments'] == walking['route']['paths'][0]['steps']
        result['saved_binding_unmodified_by_recheck'] = record['goal']['destination']['routing_point']['ref'] == 'entrance:B0FFFZRC7K' and record['goal']['destination']['longitude'] == 113.811840
    (work / 'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    assert report and not errors and result['saved_real_walking_segments_equal'] and result['saved_binding_unmodified_by_recheck'] and all(check['passed'] for check in report['checks']), str(work / 'report.json')
    print(f'PASS: {len(report["checks"])} 项入口绑定检查；{work / "report.json"}')
