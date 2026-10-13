"""原生执行12306匿名查询、精确班次接入和固定时刻反例。"""
import hashlib
import json
import time

FIXTURE=r'''
fn agent_pump(token){}
let rail_test_results=[] let rail_test_checks=[] let rail_test_stage=0 let rail_test_service=nil let rail_test_first_id="" let rail_test_first_prefix=""
fn rail_test_check(name,passed){rail_test_checks.push({name:name passed:passed})}
fn rail_test_finish(){fs.write("harness-smoke.json",{checks:rail_test_checks actual_service:rail_test_service results:rail_test_results}.to_json())}
fn agent_tool_result(result){

 let serialized=result.to_json()
 rail_test_check("工具回执可独立序列化并读回",serialized.parse_json().success==result.success)
 fs.write("rail-stage.json",{stage:rail_test_stage success:result.success error:route_get(result,"error") service_count:if route_get(result,"services").is_array() {result.services.len()} else {nil}}.to_json())
 rail_test_results.push({stage:rail_test_stage success:result.success error:route_get(result,"error")})
 if rail_test_stage==0 {
  rail_test_check("实际公开车站表返回精确站ref",result.success && result.stations.len()>0)
  if !result.success {rail_test_finish() return}
  let station=nil for item in result.stations {if item.name=="广州" {station=item}}
  if station==nil {rail_test_finish() return}
  rail_test_stage=1 search_rail_services({from_station:station.ref to_station:"深圳"},run_id)
 } elif rail_test_stage==1 {
  rail_test_check("原生HTTPS匿名会话取得实际班次",result.success && result.services.len()>0)
  rail_test_check("紧凑班次回执保公共来源与完整内部记录",result.timezone=="Asia/Shanghai" && result.source_ts.is_number() && result.ticket_status=="not_purchased" && result.services.len()>0 && route_get(result.services[0],"warnings")==nil && rail_services[result.services[0].ref].warnings.is_string() && rail_services[result.services[0].ref].boarding_date==result.boarding_date)
  if !result.success {rail_test_finish() return}
  let service=nil let seat=nil
  for item in result.services {if service==nil && item.from_station.name=="广州" && item.to_station.name=="深圳" {for option in item.seats {if seat==nil && option.availability_status=="available" && option.price_cents!=nil {service=rail_services[item.ref] seat=option}}}}
  rail_test_check("真实上下车站与席别价格保留",service!=nil)
  if service==nil {rail_test_finish() return}
  rail_test_service=service
  rail_test_check("固定到达等于发车加真实历时",service.arrival_ts==service.departure_ts+service.duration_seconds && service.train_start_date.is_string() && service.boarding_date==rail_date(time_now()))
  rail_test_stage=2
  extend_route_with_rail({route_id:"origin" service_ref:service.ref seat_code:seat.code from_ref:"origin" to_ref:"poi:rail-destination" place_basis:"原生合同fixture：模拟POI与实际站名对应，不是现场站台验证"},run_id)
 } elif rail_test_stage==2 {
  rail_test_check("真实班次接入统一Route及完整费用",result.success && result.route.legs[0].mode=="rail" && result.route.legs[0].rail_service.ref==rail_test_service.ref && result.route.cost.queried_legs_amount_cents!=nil)
  if result.success {
   let route=ui_route(result.route.id)
   rail_test_check("站内登乘未知不能通过可行性",!result.route.assessment.passed && result.route.assessment.connection_status=="provider_connection_unknown")
   let before=route_timing(route,rail_test_service.departure_ts-1)
   let missed=route_timing(route,rail_test_service.departure_ts+1)
   rail_test_check("真实发车过一秒保持原到达时刻且判错过",before.arrival_ts==rail_test_service.arrival_ts && missed.arrival_ts==rail_test_service.arrival_ts && missed.missed.len()==1 && guardian_assess(route,rail_test_service.departure_ts+1,arrive_by,20000).status=="invalid")
   let saved=guardian_materialize(route)
   rail_test_check("历史快照保固定班次与席别",saved.selected_legs[0].rail_service.ref==rail_test_service.ref && route_timing(saved,rail_test_service.departure_ts+1).missed.len()==1)
   rail_test_check("铁路缺几何不补直线",map_geometry(route).paths.len()==0 && map_geometry(route).omitted>0)
  }
  rail_test_check("高德六位金额精确入分，非零亚分拒绝",route_cents("39.000000")==3900 && route_cents("28.010000")==2801 && route_cents("0.001")==nil)
  if result.success {
   let route=ui_route(result.route.id) rail_test_first_id=route.id rail_test_first_prefix=route.prefix_id rail_test_stage=3
   extend_route_with_rail({route_id:"origin" service_ref:rail_test_service.ref seat_code:route.legs[0].rail_seat.code from_ref:"origin" to_ref:"poi:rail-destination" place_basis:"相同班次第二派生的原生合同fixture"},run_id)
  } else {rail_test_finish()}
 } elif rail_test_stage==3 {
  let route=if result.success {ui_route(result.route.id)} else {nil}
  rail_test_check("同班次重复派生保不同Route及前缀归属",route!=nil && route.id!=rail_test_first_id && route.prefix_id!=rail_test_first_prefix && route_prefixes[rail_test_first_prefix].route_id==rail_test_first_id && route_prefixes[route.prefix_id].route_id==route.id)
  if route==nil {rail_test_finish() return}
  register_route_node("poi:rail-origin","广州站","113.257,23.149","amap-poi",nil)
  let seed=route_prefix_origin(route_nodes["origin"],time_now())
  let approach={id:"fixture-approach" from_ref:"origin" to_ref:"arrival:fixture" requested_to_ref:"poi:rail-origin" mode:"walk" departure_ts:time_now() duration_seconds:1 price_cents:0 price_basis:"fixture" source_ts:time_now() waiting_included:true request_bound:true origin_complete:true endpoint_complete:true requested_origin:seed.actual_endpoint requested_destination:"113.257,23.149" actual_origin:seed.actual_endpoint actual_endpoint:"113.25737,23.149" segments:[] warnings:"synthetic geometry"}
  let prefix=route_prefix_extend(seed,approach,"fixture-approach-prefix",arrive_by,20000).prefix
  let candidate=register_mixed_candidate(prefix,route_nodes["destination"],"walk")
  rail_test_stage=4
  extend_route_with_rail({route_id:candidate.id service_ref:rail_test_service.ref seat_code:route.legs[0].rail_seat.code from_ref:"poi:rail-origin" to_ref:"poi:rail-destination" place_basis:"实际班次与模拟已核POI合同；非现场站台"},run_id)
 } else {
  rail_test_check("查询明确到正确车站允许未知几何接入",result.success)
  if result.success {
   let route=ui_route(result.route.id) let rail=route.legs[1]
   rail_test_check("条件候选保实际缺口与固定班次不挪铁路起点",rail.connection_gap_m>25 && rail.connection_actual_endpoint=="113.25737,23.149" && rail.actual_origin=="113.257,23.149" && rail.departure_ts==rail_test_service.departure_ts && rail.station_access_status=="unknown" && rail.boarding_status=="unknown" && !route.connection_verified)
   let facts=result.route.legs[1]
   rail_test_check("公开回执暴露未知接入及缺口",facts.connection_gap_m==rail.connection_gap_m && facts.station_access_status=="unknown" && facts.connection_actual_endpoint==rail.connection_actual_endpoint && !result.route.assessment.passed)
   let prefix=route_as_prefix(route)
   let onward={id:"fixture-airport" from_ref:prefix.node_ref to_ref:"destination" requested_to_ref:"destination" mode:"walk" departure_ts:rail_test_service.arrival_ts duration_seconds:10 price_cents:100 price_basis:"fixture" source_ts:time_now() waiting_included:true request_bound:true origin_complete:true endpoint_complete:true requested_origin:prefix.actual_endpoint requested_destination:coord_text(route_nodes["destination"]) actual_origin:prefix.actual_endpoint actual_endpoint:coord_text(route_nodes["destination"]) segments:[] warnings:"synthetic geometry"}
   let joined=route_prefix_extend(prefix,onward,"fixture-airport-prefix",arrive_by,20000)
   let final=register_mixed_candidate(joined.prefix,route_nodes["destination"],"walk")
   let summary=query_route_summary(final) let saved=guardian_materialize(final)
   rail_test_check("后续到机场不洗掉未知且价格仅已查小计",joined.success && !final.connection_verified && final.provider_connection_status=="unknown" && !summary.assessment.passed && summary.cost.full_journey_amount_cents==nil && summary.cost.known_subtotal_cents==rail.price_cents+100 && route_prefix_facts(joined.prefix).full_journey_price_cents==nil)
   let restored=saved.to_json().parse_json()
   rail_test_check("保存恢复保留未知接入与端点缺口",restored.connection_verified==false && restored.provider_connection_status=="unknown" && restored.selected_legs[1].connection_gap_m==rail.connection_gap_m && restored.selected_legs[1].connection_actual_endpoint==rail.connection_actual_endpoint && restored.selected_legs[1].station_access_status=="unknown")
   let approach={} for key value in route.legs[0] {approach[key]=value}
   let before=route_prefix_origin(route_nodes["origin"],time_now())
   let base=route_prefix_extend(before,approach,"negative-base",arrive_by,20000).prefix
   let plain={} for key value in rail {plain[key]=value} plain.connection_verified=nil
   rail_test_check("普通连接仍拒绝25米以上缺口",!route_prefix_extend(base,plain,"ordinary-gap",arrive_by,20000).success)
   approach.requested_to_ref="poi:another-station"
   rail_test_check("另一站或无目标溯源不放行",!route_prefix_extend_rail(base,plain,route_nodes["poi:rail-origin"],"wrong-target",arrive_by,20000).success)
   approach.requested_to_ref="poi:rail-origin" approach.request_bound=false
   rail_test_check("未绑定供应商请求不放行",!route_prefix_extend_rail(base,plain,route_nodes["poi:rail-origin"],"unbound",arrive_by,20000).success)
   approach.request_bound=true
   let arrival={ref:"poi:rail-origin" name:"广州站" source:"amap-route-geometry"}
   rail_test_check("任意arrival套站名不放行",!route_prefix_extend_rail(base,plain,arrival,"arrival-name",arrive_by,20000).success)
   let wrong={ref:"poi:rail-origin" name:"广州南站" source:"amap-poi"}
   rail_test_check("另一个实际车站不放行",!route_prefix_extend_rail(base,plain,wrong,"wrong-station",arrive_by,20000).success)
  }
  rail_test_finish()
 }
}
fn rail_test_start(){
 run_id+=1 agent_active=true phase="running" arrive_by=time_now()+14400
 position_record={name:"广州站" longitude:113.257 latitude:23.149 source:"native-contract-fixture" city:"广州市" citycode:"020" adcode:"440104" currency:"CNY"}
 destination_record={name:"合同终点" longitude:114.116 latitude:22.532 source:"native-contract-fixture" city:"深圳市" citycode:"0755" adcode:"440303" currency:"CNY"}
 constraints={budget_cents:20000 currency:"CNY"} prepare_route_graph()
 register_route_node("poi:rail-destination","深圳站","114.116,22.532","native-contract-fixture",{city:"深圳市" citycode:"0755" adcode:"440303" currency:"CNY"})
 search_rail_stations({query:"广州"},run_id)
}
start_timeout(1,||rail_test_start())
'''

def source(original):
    return original.replace('fn agent_pump(', 'fn product_agent_pump(', 1).replace('fn agent_tool_result(', 'fn product_agent_tool_result(', 1) + '\n' + FIXTURE

def run(w,jail,original,injected):
    report=None
    for _ in range(1800):
        try: report=json.loads((jail/'harness-smoke.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError): pass
        if report: break
        time.sleep(.1)
    assert report, '铁路原生查询未完成；'+str(w/'native.log')
    errors=[line for line in (w/'native.log').read_text().splitlines() if '[E]' in line]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,real_12306_queries=True,synthetic_station_geometry=True,native_errors=errors)
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not errors,errors
    assert all(x['passed'] for x in report['checks']),report
    print('PASS: '+str(len(report['checks']))+'项铁路原生检查；'+str(w/'report.json'))

EGRESS_FIXTURE=r'''
let eg_checks=[] let eg_service=nil let eg_final=nil
fn eg_check(name,passed){eg_checks.push({name:name passed:passed})}
fn eg_finish(){fs.write("harness-smoke.json",{checks:eg_checks actual_service:eg_service}.to_json())}
fn eg_copy(value){let copy={} for key item in value {copy[key]=item} return copy}
fn eg_start(){
 if trip_loading || trip_pending_commit!=nil {start_timeout(0.05,||eg_start()) return}
 fs.read_async("rail-egress-service.json",fn(reply){
  if !reply.success {eg_check("实际班次夹具可读取",false) eg_finish() return}
  eg_service=reply.text.parse_json()
  run_id+=1 received_at=time_now() arrive_by=eg_service.arrival_ts+14400 user_limits={minutes:240 budget_cents:20000} constraints={budget_cents:20000 currency:"CNY"}
  position_record={name:"广州南站" longitude:113.269097 latitude:22.988344 source:"synthetic-station-geometry" currency:"CNY" city:"深圳市" citycode:"0755" adcode:"440309" sampled_at_unix:received_at}
  destination_record={name:"机场合同终点" longitude:113.81461 latitude:22.625128 source:"synthetic-station-geometry" currency:"CNY" city:"深圳市" citycode:"0755" adcode:"440309" sampled_at_unix:received_at}
  prepare_route_graph()
  let from=register_route_node("poi:eg-from","广州南站","113.269097,22.988344","amap-poi",nil)
  let station=register_route_node("poi:eg-station","深圳北站","114.029506,22.609878","amap-poi",nil)
  let airport=register_route_node("poi:eg-airport","机场合同终点","113.81461,22.625128","amap-poi",nil)
  let rail={id:"eg-rail" mode:"rail" from_ref:from.ref to_ref:station.ref requested_to_ref:station.ref departure_ts:eg_service.departure_ts duration_seconds:eg_service.duration_seconds price_cents:7450 price_basis:"recorded-service" source_ts:eg_service.source_ts waiting_included:false request_bound:true origin_complete:true endpoint_complete:true actual_origin:coord_text(from) actual_endpoint:coord_text(station) segments:[] warnings:"真实班次，合成站内几何反例" rail_service:eg_service rail_seat:{code:"O" price_cents:7450} provider_connection_status:"unknown" station_access_status:"unknown" boarding_status:"unknown"}
  let seed=route_prefix_origin(route_nodes["origin"],eg_service.departure_ts)
  let prefix=route_prefix_extend_rail(seed,rail,from,"eg-rail-prefix",arrive_by,20000).prefix
  let response={origin:coord_text(station) destination:coord_text(airport)}
  let option={cost:{duration:"120" transit_fee:"8.000000"} segments:[{walking:{steps:[{polyline:"114.029221,22.610287;113.81461,22.625128"}]}}]}
  let leg=extension_leg(response,option,0,1,"transit",station,airport,time_now(),eg_service.arrival_ts,99)
  eg_check("54米真实pickup坐标反例保provider绑定且origin未知",leg.request_bound && !leg.origin_complete && leg.endpoint_complete && route_endpoint_gap(prefix.actual_endpoint,leg.actual_origin)>50)
  let joined=route_prefix_extend(prefix,leg,"eg-out-prefix",arrive_by,20000)
  eg_check("实际铁路下车站允许有溯源的条件出站",joined.success && joined.prefix.legs.len()==2 && !leg.origin_complete && leg.actual_origin=="114.029221,22.610287" && leg.connection_actual_endpoint==coord_text(station) && leg.connection_gap_m>50 && leg.station_access_status=="unknown" && leg.connection_verified==false)
  if !joined.success {eg_finish() return}
  let fresh=extension_leg(response,option,0,1,"transit",station,airport,time_now(),eg_service.arrival_ts,100)
  let bad=eg_copy(fresh) bad.request_bound=false
  eg_check("未绑定供应商请求仍拒出站",!route_prefix_extend(prefix,bad,"eg-unbound",arrive_by,20000).success)
  bad=eg_copy(fresh) bad.actual_origin=nil
  eg_check("实际pickup缺失仍拒出站",!route_prefix_extend(prefix,bad,"eg-no-origin",arrive_by,20000).success)
  bad=eg_copy(fresh) bad.endpoint_complete=false
  eg_check("实际末端未核实仍拒出站",!route_prefix_extend(prefix,bad,"eg-no-end",arrive_by,20000).success)
  bad=eg_copy(fresh) bad.from_ref="arrival:another"
  eg_check("另一节点不能套用站身份",!route_prefix_extend(prefix,bad,"eg-ref",arrive_by,20000).success)
  let saved_name=station.name station.name="深圳机场北站"
  eg_check("另一实际车站不放宽出站",!route_prefix_extend(prefix,eg_copy(fresh),"eg-name",arrive_by,20000).success) station.name=saved_name
  let saved_source=station.source station.source="amap-route-geometry"
  eg_check("任意arrival节点不冒充真实站POI",!route_prefix_extend(prefix,eg_copy(fresh),"eg-source",arrive_by,20000).success) station.source=saved_source
  let plain=eg_copy(prefix) plain.legs=[eg_copy(rail)] plain.legs[0].mode="transit"
  eg_check("非铁路前缀仍拒25米以上缺口",!route_prefix_extend(plain,eg_copy(fresh),"eg-nonrail",arrive_by,20000).success)
  let onward={id:"eg-final" mode:"walk" from_ref:airport.ref to_ref:"destination" requested_to_ref:"destination" departure_ts:joined.prefix.earliest_arrival_ts duration_seconds:5 price_cents:0 price_basis:"synthetic" source_ts:time_now() waiting_included:true request_bound:true origin_complete:true endpoint_complete:true actual_origin:joined.prefix.actual_endpoint actual_endpoint:coord_text(route_nodes["destination"]) segments:[] warnings:"synthetic endpoint"}
  let final=route_prefix_extend(joined.prefix,onward,"eg-final-prefix",arrive_by,20000)
  eg_final=register_mixed_candidate(final.prefix,route_nodes["destination"],"walk")
  let facts=query_route_summary(eg_final)
  eg_check("后续连接不洗掉出站未知或宣称完整可行",final.success && eg_final.connection_verified==false && eg_final.provider_connection_status=="unknown" && !facts.assessment.passed && facts.cost.full_journey_amount_cents==nil && facts.cost.known_subtotal_cents==8250 && eg_final.legs[1].origin_complete==false)
  let missed=route_timing(eg_final,eg_service.departure_ts+1)
  eg_check("真实固定班次过时仍拒且不可平移",missed.missed.len()==1 && guardian_assess(eg_final,eg_service.departure_ts+1,arrive_by,20000).status=="invalid")
  let now=time_now() trip_records=[] trip_selected_id=nil trip_next_id=1 trip_generation=0
  let trip={id:"trip-1" title:"铁路出站条件合同" input:"offline" created_at:now updated_at:now status:"completed" goal:nil snapshot:{captured_at:now facts:facts blocks:[] route_data:[guardian_materialize(eg_final)]} _dirty:true}
  trip_commit({schema:1 selected_id:trip.id next_id:2 trips:[trip]},fn(committed){
   eg_check("条件铁路Route实际保存成功",committed)
   trip_read("navigation-trips.json",fn(read){
    let restored=if read!=nil {read.data.trips[0].snapshot.route_data[0]} else {nil}
    eg_check("异步恢复保出站gap原始端点与unknown",restored!=nil && restored.connection_verified==false && restored.provider_connection_status=="unknown" && restored.selected_legs[1].connection_gap_m==leg.connection_gap_m && restored.selected_legs[1].actual_origin==leg.actual_origin && restored.selected_legs[1].connection_actual_endpoint==coord_text(station) && restored.selected_legs[1].station_access_status=="unknown" && restored.selected_legs[1].origin_complete==false && route_timing(restored,eg_service.departure_ts+1).missed.len()==1)
    eg_finish()
   })
  })
 })
}
start_timeout(1,||eg_start())
'''


def egress_source(original):
    return original + '\n' + EGRESS_FIXTURE


def prepare_egress(jail):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    events = [json.loads(line) for line in (root/'build/research/rail-integration/e2e/round15/trace-private.jsonl').read_text().splitlines()]
    result = json.loads(json.loads(next(event['data'] for event in events if event['seq']==119))['result'])
    service = next(leg['rail_service'] for leg in result['route']['legs'] if leg['mode']=='rail')
    (jail/'rail-egress-service.json').write_text(json.dumps(service,ensure_ascii=False))


def run_egress(w,jail,original,injected):
    target=jail/'harness-smoke.json'
    until=time.monotonic()+30
    while not target.exists() and time.monotonic()<until: time.sleep(.1)
    assert target.exists(), f'铁路出站合同未完成：{w/"native.log"}'
    report=json.loads(target.read_text())
    errors=[line for line in (w/'native.log').read_text().splitlines() if '[E]' in line]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,provider_called=False,recorded_service_round=15,synthetic_connection_geometry=True,native_errors=errors)
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not errors and all(item['passed'] for item in report['checks']), report
    print(f'PASS: {len(report["checks"])} 项铁路出站条件合同；{w/"report.json"}')
