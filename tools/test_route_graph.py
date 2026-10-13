"""真实供应商记录的图读取负载与精确铁路站对原生合同。"""
import hashlib
import json
import time
from pathlib import Path

FIXTURE=r'''
fn agent_pump(token){}
let graph_checks=[] let graph_stage=0 let graph_first_cache=nil let graph_other_pair=nil
fn graph_check(name,passed){graph_checks.push({name:name passed:passed})}
fn graph_finish(){fs.write("harness-smoke.json",{checks:graph_checks}.to_json())}
fn agent_tool_result(result){
 if graph_stage==0 {
  let graph=result.graph let reply=result.to_json().parse_json()
  graph_check("20候选完整接驳图回执可序列化",result.success && graph.routes.len()==20 && reply.graph.routes.len()==20 && graph.transit_segments.len()==graph_expected_lines*20)
  let indexed={} let memberships={} for node in graph.nodes {indexed[node.ref]=node for member in node.memberships {memberships[node.ref+":"+member.route_id+":"+member.segment_index+":"+member.busline_index+":"+member.stop_index]=true}}
  let valid=true let matched=0
  for relation in graph.transit_segments {for stop in relation.stops {if stop.node_ref!=nil {
   let node=indexed[stop.node_ref] if node==nil {valid=false} else {if memberships[stop.node_ref+":"+relation.route_id+":"+relation.segment_index+":"+relation.busline_index+":"+stop.index]!=true {valid=false} matched+=1}
  }}}
  graph_check("所有真实停站保线路与候选归属",valid && matched>0)
  graph_first_cache=candidates[0].segments_cache graph_stage=1
  read_route_graph(run_id,fn(second){
   graph_check("再次读取复用详细段缓存且保全部候选",candidates[0].segments_cache==graph_first_cache && second.routes.len()==20)
   let old_called=false read_route_graph(run_id,fn(old){old_called=true}) run_id+=1
   route_nodes={} route_node_generation+=1
   start_timeout(0.05,||{
    graph_check("旧查询图回调不能进入新查询",!old_called)
    read_route_graph(run_id,fn(rebuilt){
    graph_check("节点registry新代际重建停站而非误用旧cache",rebuilt.nodes.len()>2 && candidates[0].stations_registered_generation==route_node_generation)
    let date="2026-10-12" let at=rail_time(date,"00:00") arrive_by=at+86400
    rail_station_text=graph_station_text
    graph_stage=2
    rail_collect_services({records:graph_rail_records names:graph_rail_names date:date at:at earliest:at index:0 services:[] rejected:0 p:{from_station:"上海虹桥" to_station:"南京南"} from_code:"AOH" to_code:"NKH" other_pairs:{}},run_id)
    })
   })
  })
 } elif graph_stage==2 {
  let exact=result.services.len()==graph_expected_exact && result.services.len()>0
  for service in result.services {if service.from_station.code!="AOH" || service.to_station.code!="NKH" {exact=false}}
  graph_check("同供应商340条样本仅精确站对进services",exact && result.total_returned==340)
  let callable=true for pair in result.other_observed_station_pairs {if rail_station_code(pair.from_station.ref)!=pair.from_station.code || rail_station_code(pair.to_station.ref)!=pair.to_station.code {callable=false}}
  graph_check("邻站组合保观察count及可调用真实refs",callable && result.other_observed_station_pairs.len()>0 && result.other_observed_station_pairs[0].observed_service_count>0)
  graph_stage=3
  rail_collect_services({records:graph_rail_records names:graph_rail_names date:result.boarding_date at:result.source_ts earliest:result.earliest_departure_ts index:0 services:[] rejected:0 p:{from_station:"广州南" to_station:"深圳机场"} from_code:"IZQ" to_code:"SCA" other_pairs:{}},run_id)
 } elif graph_stage==3 {
  graph_check("无精确班次明确empty不偷偷扩大",result.success && result.services.len()==0 && result.empty_reason!=nil && result.other_observed_station_pairs.len()>0)
  let service=nil for ref item in rail_services {if service==nil {service=item}}
  register_route_node("poi:wrong-rail","上海站","113.269097,22.988344","amap-poi",nil)
  register_route_node("poi:correct-rail","南京南站","114.116,22.532","amap-poi",nil)
  graph_stage=4
  extend_route_with_rail({route_id:"origin" service_ref:service.ref seat_code:"O" from_ref:"poi:wrong-rail" to_ref:"poi:correct-rail" place_basis:"合同反例：供应商实际上海虹桥而POI上海"},run_id)
 } else {
  graph_check("错误站身份拒绝并返回可修正事实",!result.success && result.service_from_station.code=="AOH" && result.service_to_station.code=="NKH" && result.supplied_from.name=="上海站" && result.supplied_to.name=="南京南站")
  graph_finish()
 }
}
start_timeout(1,||{
 graph_check("实际城际设施POI末端标签对应基础车站",rail_place_name("琶洲站(城际站)")=="琶洲" && rail_place_name("深圳机场站(T3)(城际站)")=="深圳机场")
 graph_check("全半角及多位航站楼编号保持同一规范化",rail_place_name("深圳机场站（T12）（城际站）")=="深圳机场" && rail_place_name("深圳机场站（T3）(城际站)")=="深圳机场")
 graph_check("不同实际车站与未知括号不被合并",rail_place_name("广州站")!=rail_place_name("广州东站") && rail_place_name("深圳机场站(T3)(城际站)")!=rail_place_name("深圳机场北站(城际站)") && rail_place_name("琶洲站(其他设施)")=="琶洲站(其他设施)" && rail_place_name("琶洲站(其他设施)(城际站)")=="琶洲站(其他设施)")
 run_id+=1 agent_active=true arrive_by=time_now()+14400 constraints={budget_cents:20000}
 position_record={name:"广州站" longitude:113.257 latitude:23.149 source:"contract-fixture" city:"广州市" citycode:"020" adcode:"440104" currency:"CNY"}
 destination_record={name:"南京南站" longitude:114.116 latitude:22.532 source:"contract-fixture" city:"深圳市" citycode:"0755" adcode:"440303" currency:"CNY"}
 for index in 20 {let candidate=route_candidate("recorded-graph-"+index,"public_transit",6000,1000,time_now(),time_now(),"114.029506,22.609878","114.029506,22.609878",true,graph_segments) assign_candidate_ref(candidate) candidates.push(candidate)}
 agent_calls=[{id:"graph-get" function:{name:"get_route_graph" arguments:"{}"}}] agent_call_index=0 agent_schedule_next(run_id)
})
'''

def source(original):
    root=Path(__file__).resolve().parents[1]
    amap=json.loads((root/'build/research/rail-integration/amap/v5-gzsz.json').read_text())['response']
    segments=[s for t in amap['route']['transits'] for s in t['segments']]
    rail=json.loads((root/'build/research/rail-integration/sources/live/tickets.body').read_text())['data']
    expected=sum(1 for r in rail['result'] if r.split('|')[6:8]==['AOH','NKH'])
    def literal(x):return json.dumps(json.dumps(x,ensure_ascii=False),ensure_ascii=False)+'.parse_json()'
    prelude='\nlet graph_segments='+literal(segments)+'\nlet graph_rail_records='+literal(rail['result'])+'\nlet graph_rail_names='+literal(rail['map'])+'\nlet graph_station_text='+json.dumps((root/'build/research/rail-integration/sources/live/stations.body').read_text(),ensure_ascii=False)+'\nlet graph_expected_exact='+str(expected)+'\nlet graph_expected_lines='+str(sum(len(s.get('bus',{}).get('buslines',[])) for s in segments))+'\n'
    return original.replace('fn agent_pump(', 'fn product_agent_pump(',1).replace('fn agent_tool_result(', 'fn product_agent_tool_result(',1)+prelude+FIXTURE

def run(w,jail,original,injected):
    report=None
    for _ in range(900):
        try:report=json.loads((jail/'harness-smoke.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):pass
        if report:break
        time.sleep(.1)
    assert report,str(w/'native.log')
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,provider_called=False,recorded_real_supplier_data=True,duplicated_graph_candidates=20,native_errors=[x for x in (w/'native.log').read_text().splitlines() if '[E]' in x])
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not report['native_errors'],report['native_errors']
    assert all(x['passed'] for x in report['checks']),report
    print('PASS: '+str(len(report['checks']))+'项图及铁路站对原生检查；'+str(w/'report.json'))
