"""第23轮查询入口的隔离诊断；原轮未落raw几何，负载替代边界写入报告。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'build/research/rail-integration/e2e'


def prepare(jail):
 from test_trip_snapshot import read_record
 events=[json.loads(line) for line in (EVIDENCE/'round23/trace-private.jsonl').read_text().splitlines()]
 nodes={};places=[];context=None;public={};entry_poi=None
 for event in events:
  if event['event']!='tool_result':continue
  data=json.loads(event['data']);result=json.loads(data['result'])
  if data['name']=='adopt_destination':context=result
  if data['name']=='search_places':
   places=result['places']
   for poi in places:
    if poi['id']=='B0FFFZRC7K':entry_poi=poi
   for place in places:
    nodes[place['node_ref']]=dict(place,ref=place['node_ref'])
    if place.get('entrance'):nodes[place['entrance']['ref']]=dict(place['entrance'])
  for node in result.get('new_nodes',[]):nodes[node['ref']]=node
  for route in result.get('routes',[]):public[route['id']]=route
 assert len(public)==12 and 'poi:B00140VAP3' in nodes
 # 原轮没有render或raw dump。保留旧轮真实segments作为明确的扫描负载替代。
 recorded=EVIDENCE/'private-state-round22/home/apps/os.agentic26-navigation'
 index=json.loads((recorded/'navigation-trips.json').read_text())['data'];snapshot=read_record(recorded,index['trips'][0]['file'])['snapshot']
 directory=Path(jail)/'query-entry-fixture';directory.mkdir()
 context.update(nodes=list(nodes.values()),places=places,entry_poi=entry_poi)
 (directory/'context.json').write_text(json.dumps(context,ensure_ascii=False))
 for index,raw in enumerate(snapshot['route_data'][:12]):
  candidate=dict(raw,geometry_ref=raw.get('history_geometry_ref'),legs=[])
  (directory/f'route-{index}.json').write_text(json.dumps(candidate,ensure_ascii=False))
 (directory/'boundary.json').write_text(json.dumps({'round23_public_routes':12,'round23_public_nodes':len(nodes),'round23_latest_pois':len(places),'raw_geometry_source':'round22 full snapshot first12, unchanged','live_generation_unknown':True,'cache_setup':'first10 marked current; last2 absent, inferred from successful preceding query ordering, not recovered live metadata'},ensure_ascii=False))

FIXTURE=r'''
let qe_checks=[] let qe_context=nil let qe_report=nil
let qe_marks=[] let qe_points=0 let qe_stops=0 let qe_candidates=0 let qe_hits=0 let qe_stage="loading" let qe_started=0 let qe_done=false
fn qe_mark(name){qe_marks.push({stage:name at:time_now() points:qe_points stops:qe_stops candidates:qe_candidates hits:qe_hits})}
fn qe_check(name,passed){qe_checks.push({name:name passed:passed})}
fn qe_finish(path){if qe_done {return} qe_done=true qe_report={reached_supplier:true path:path elapsed:time_now()-qe_started marks:qe_marks points:qe_points stop_registers:qe_stops candidates:qe_candidates hits:qe_hits}
 qe_check("准确广州南query生产入口到截获且不扫描旧候选",path=="/v5/direction/transit/integrated" && qe_candidates==0 && qe_stops==0 && qe_points==2)
 qe_stage="refs" start_timeout(0.01,||qe_refs())
}
fn qe_refs(){
 run_id+=1 route_nodes={} route_prefixes={} route_node_generation+=1
 qe_check("跨query旧广州南引用不进入新registry",route_node("poi:B00140VAP3")==nil)
 prepare_route_graph_base()
 register_route_pois([qe_context.entry_poi])
 let poi=qe_context.entry_poi
 qe_check("新真实POI及其独立入口可引用",route_poi(poi.id)!=nil && route_node(poi.entrance.ref)!=nil && coord_text(route_node(poi.entrance.ref))==coord_text(poi.entrance))
 let segments=candidates[1].segments
 let start=route_leg_endpoint(segments,true) let end=route_leg_endpoint(segments,false)
 let from=register_route_node("fixture-from","旧轮真实方案起点",start,"recorded-amap",nil)
 let to=register_route_node("fixture-to","旧轮真实方案终点",end,"recorded-amap",nil)
 let leg=extension_leg({origin:start destination:end},{segments:segments cost:{duration:"6000" transit_fee:"50"}},0,1,"transit",from,to,time_now(),time_now(),100)
 let refs=[] for segment in segments {let lines=route_get(route_get(segment,"bus"),"buslines") if lines.is_array() {for line in lines {for stop in [line.departure_stop line.arrival_stop] {if route_get(stop,"id").is_string() {refs.push("stop:"+stop.id)}}}}}
 let valid=refs.len()>0 for ref in refs {if route_node(ref)==nil {valid=false}}
 qe_check("新leg生产入口即时登记真实停站引用",valid)
 route_nodes={} route_prefixes={} route_node_generation+=1
 read_route_graph(run_id,fn(graph){
  let indexed={} for node in graph.nodes {indexed[node.ref]=true}
  let rebuilt=graph.routes.len()==12 for candidate in candidates {if candidate.stations_registered_generation!=route_node_generation {rebuilt=false}}
  for ref in refs {if indexed[ref]!=true {rebuilt=false}}
  qe_check("异步完整图新代际重建全部候选停站",rebuilt)
  qe_report.checks=qe_checks fs.write("query-entry-report.json",qe_report.to_json())
 })
}
fn route_point(value){if qe_stage=="query" {qe_points+=1} return product_route_point(value)}
fn prepare_route_graph_base(){if qe_stage=="query" {qe_mark("base_enter")} let result=product_prepare_route_graph_base() if qe_stage=="query" {qe_mark("base_return")} return result}
fn register_candidate_stations(candidate){if qe_stage=="query" {qe_candidates+=1 if route_get(candidate,"stations_registered_generation")==route_node_generation {qe_hits+=1} qe_mark("candidate_enter")} product_register_candidate_stations(candidate) if qe_stage=="query" {qe_mark("candidate_return")}}
fn verify_route_node_city(node,token,done){qe_mark("verify_city_enter") product_verify_route_node_city(node,token,fn(){qe_mark("verify_city_return") done()})}
fn amap_request(path,params,token,done){qe_mark("amap_intercept") qe_finish(path)}
fn agent_pump(token){}
fn agent_tool_result(result){fs.write("query-entry-report.json",{reached_supplier:false error:route_get(result,"error") marks:qe_marks}.to_json())}
fn qe_load(index){if index>=12 {
 qe_stage="query" qe_started=time_now() qe_mark("query_enter")
 active_tool={id:"call_01a12b1b0c637391b5869fc2" function:{name:"query_route"}}
 query_route({mode:"transit" to_ref:"poi:B00140VAP3"},run_id) qe_mark("query_return") return
 }
 fs.read_async("query-entry-fixture/route-"+index+".json",fn(reply){let candidate=reply.text.parse_json() if index<10 {candidate.stations_registered_generation=route_node_generation} candidates.push(candidate) start_timeout(0.01,||qe_load(index+1))})
}
start_timeout(2,||fs.read_async("query-entry-fixture/context.json",fn(reply){let context=reply.text.parse_json() qe_context=context
 run_id+=1 agent_active=true phase="running" trip_replay=false ui_blocks=[] position_record=context.origin destination_record=context.destination constraints=context.constraints user_limits=context.limits received_at=position_record.sampled_at_unix arrive_by=context.arrive_by
 route_nodes={} for node in context.nodes {route_nodes[node.ref]=node} route_prefixes={} poi_records=context.places candidates=[] route_node_generation+=1 qe_load(0)
}))
'''

def source(original):
 injected=original
 for name in ['route_point','prepare_route_graph_base','register_candidate_stations','verify_route_node_city','amap_request','agent_pump','agent_tool_result']:
  injected=injected.replace(f'fn {name}(',f'fn product_{name}(',1)
 # Counter only; no extra per-stop timer or syscall in the hot loop.
 injected=injected.replace('fn register_route_node(ref,name,point,source,city){','fn register_route_node(ref,name,point,source,city){\n if qe_stage=="query" && ref.is_string() && ref.search("stop:")==0 {qe_stops+=1}',1)
 return injected+'\n'+FIXTURE


def run(work,jail,original,injected):
 report=None
 for _ in range(600):
  path=jail/'query-entry-report.json'
  if path.exists():report=json.loads(path.read_text());break
  if '[E]' in (work/'native.log').read_text():break
  time.sleep(.05)
 result=report or {'incomplete':True}
 result.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'query-entry-fixture/boundary.json').read_text()),model_called=False,provider_called=False,native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line])
 (work/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(work/'report.json')
 assert report and not result['native_errors'] and all(check['passed'] for check in report.get('checks',[])),str(work/'report.json')
