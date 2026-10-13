"""第29轮完整公开graph投影及真实get_route_graph selector的有界原生回放。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'build/research/rail-integration/e2e'
def prepare(jail):
 request=json.loads((E/'round29/reconstructed-step11-request-private.json').read_text());full=json.loads(request['messages'][-2]['content'])['graph']
 assert (len(full['nodes']),len(full['routes']),len(full['transit_segments']))==(516,21,54)
 selected=max(full['nodes'],key=lambda node:len(node.get('memberships',[])))
 supplier=json.loads((ROOT/'build/research/rail-integration/amap/v5-gzsz.json').read_text())['response']
 segments=[segment for option in supplier['route']['transits'] for segment in option['segments']]
 directory=Path(jail)/'model-graph-fixture';directory.mkdir()
 for name,value in [('captured',full),('segments',segments),('selector',{'ref':selected['ref'],'missing_ref':'fixture:missing-node'})]:
  (directory/f'{name}.json').write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')))
 boundary={'round':29,'full_graph_nodes':516,'full_graph_routes':21,'full_graph_relations':54,'selected_ref':selected['ref'],'selected_memberships':len(selected['memberships']),'captured_relation_duration_available':False,'original_candidate_raw_available':False,'production_fixture':'same actual AMap v5-gzsz segments used by existing test_route_graph, repeated20 candidates; not round29 raw/live heap','provider_requested':False,'model_requested':False}
 (directory/'boundary.json').write_text(json.dumps(boundary));return boundary
FIXTURE=r'''
let mg_full=nil let mg_segments=nil let mg_selector=nil let mg_projected=nil let mg_stage=0 let mg_checks=[] let mg_dispatches=0 let mg_production_default=nil let mg_internal_full=nil let mg_production_selected=nil let mg_selected_ref=nil let mg_done=false let mg_provider_calls=0
fn mg_check(name,passed){mg_checks.push({name:name passed:passed}) fs.write("model-graph-progress.json",{stage:mg_stage checks:mg_checks dispatches:mg_dispatches}.to_json())}
fn amap_request(path,params,token,done){mg_provider_calls+=1}
fn mg_nodes(index){let until=index+50 if until>mg_full.nodes.len(){until=mg_full.nodes.len()} while index<until {mg_projected.nodes.push(route_model_node_index(mg_full.nodes[index])) index+=1}
 if index<mg_full.nodes.len(){start_timeout(0.01,||mg_nodes(index))} else {start_timeout(0.01,||mg_routes(0))}}
fn mg_routes(index){if index>=mg_full.routes.len(){start_timeout(0.01,||mg_relations(0)) return} mg_projected.routes.push(route_model_graph_index(mg_full.routes[index])) start_timeout(0.01,||mg_routes(index+1))}
fn mg_relations(index){if index>=mg_full.transit_segments.len(){
 fs.write("model-graph-captured-projection.json",route_graph_result(mg_projected).to_json()) fs.write("model-graph-tools.json",agent_tools().to_json()) start_timeout(0.01,||mg_production_begin()) return
 } let relation=mg_full.transit_segments[index] let stops=relation.stops
 mg_projected.relations.push(route_model_relation_index(relation,if stops.len()>0 {stops[0].node_ref} else {nil},if stops.len()>0 {stops[stops.len()-1].node_ref} else {nil},nil)) start_timeout(0.01,||mg_relations(index+1))}
fn mg_production_begin(){mg_stage=1 run_id+=1 agent_active=true guardian_mode=false trip_replay=false ui_blocks=[] trip_records=[] trip_selected_id=nil candidates=[] route_nodes={} route_prefixes={} route_node_generation+=1
 arrive_by=time_now()+14400 constraints={budget_cents:20000} user_limits={minutes:240 budget_cents:20000} received_at=time_now()
 position_record={name:"广州站" longitude:113.257 latitude:23.149 source:"contract-fixture" city:"广州市" citycode:"020" adcode:"440104" currency:"CNY"}
 destination_record={id:"model-graph-destination" name:"南京南站" longitude:114.116 latitude:22.532 source:"contract-fixture" city:"深圳市" citycode:"0755" adcode:"440303" currency:"CNY"}
 for index in 20 {let candidate=route_candidate("recorded-model-graph-"+index,"public_transit",6000,1000,time_now(),time_now(),"114.029506,22.609878","114.029506,22.609878",true,mg_segments) assign_candidate_ref(candidate) candidates.push(candidate)}
 mg_submit("mg-default",{})
}
fn mg_submit(id,params){let call={id:id function:{name:"get_route_graph" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)}
fn agent_pump(token){if !current_task(token){return} mg_dispatches+=1 let result=nil for message in agent_messages {if route_get(message,"role")=="tool" {result=message.content.parse_json()}}
 if mg_stage==1 {mg_production_default=result.graph
  mg_check("生产默认get_route_graph全候选轻索引一次派发",result.success && result.graph.projection=="index" && result.graph.routes.len()==20 && mg_dispatches==1)
  read_route_graph(run_id,fn(graph){mg_internal_full=graph let multi=nil for node in graph.nodes {if node.memberships.len()>1 && multi==nil {multi=node.ref}}
   mg_selected_ref=multi mg_stage=2 mg_submit("mg-selector",{node_refs:[multi "fixture:missing-node"]})
  })
 } else {mg_production_selected=result.graph
  mg_check("生产node_refs保真实多membership与missing refs一次派发",result.success && result.graph.projection=="node_details" && result.graph.nodes.len()==1 && result.graph.nodes[0].ref==mg_selected_ref && result.graph.nodes[0].memberships.len()>1 && result.graph.missing_refs.len()==1 && result.graph.missing_refs[0]=="fixture:missing-node" && mg_dispatches==2)
  start_timeout(0.15,||mg_report())
 }
}
fn mg_report(){if mg_done{return} mg_done=true fs.write("model-graph-production-default.json",mg_production_default.to_json()) fs.write("model-graph-production-full.json",mg_internal_full.to_json()) fs.write("model-graph-production-selected.json",mg_production_selected.to_json()) fs.write("model-graph-report.json",{checks:mg_checks dispatches:mg_dispatches selected_ref:mg_selected_ref provider_calls:mg_provider_calls}.to_json())}
start_timeout(1,||fs.read_async("model-graph-fixture/captured.json",fn(reply){mg_full=reply.text.parse_json() fs.read_async("model-graph-fixture/segments.json",fn(segments){mg_segments=segments.text.parse_json() fs.read_async("model-graph-fixture/selector.json",fn(selector){mg_selector=selector.text.parse_json() mg_projected={token:run_id nodes:[] routes:[] relations:[] memberships:{} model_projection:true selected_refs:nil missing_refs:[]} mg_nodes(0)})})}))
'''
def source(original):
 for name in ['agent_pump','amap_request']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 for _ in range(1400):
  if (jail/'model-graph-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'model-graph-report.json').read_text()) if (jail/'model-graph-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'model-graph-fixture/boundary.json').read_text()),model_requested=False,native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line])
 def load(name):return json.loads((jail/name).read_text())
 def relation_id(r):return (r['route_id'],r['leg_id'],r['segment_index'],r['busline_index'],r['line_id'])
 def compact(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
 full=load('model-graph-fixture/captured.json');projected=load('model-graph-captured-projection.json')
 nodes_ok=[n['ref'] for n in projected['nodes']]==[n['ref'] for n in full['nodes']] and all('memberships' not in n for n in projected['nodes'])
 routes_ok=[r['id'] for r in projected['routes']]==[r['id'] for r in full['routes']] and all(a['cost']==b['cost'] for a,b in zip(projected['routes'],full['routes']))
 relations_ok=len(projected['transit_segments'])==len(full['transit_segments'])
 for actual,expected in zip(projected['transit_segments'],full['transit_segments']):
  relations_ok &= relation_id(actual)==relation_id(expected) and actual['duration_seconds'] is None and actual['direction']=={'from_ref':expected['stops'][0]['node_ref'],'to_ref':expected['stops'][-1]['node_ref']}
  relations_ok &= [(s['node_ref'],s['role'],s['index']) for s in actual['stops']]==[(s['node_ref'],s['role'],s['index']) for s in expected['stops']]
 report['checks'].append({'name':'captured516节点21Route54线路完整身份成本未知及停站顺序','passed':bool(nodes_ok and routes_ok and relations_ok)})
 actual_default=load('model-graph-production-default.json');internal=load('model-graph-production-full.json');actual_selected=load('model-graph-production-selected.json')
 selected_ref=report['selected_ref'];node=next(n for n in internal['nodes'] if n['ref']==selected_ref)
 related=[r for r in internal['transit_segments'] if any(s['node_ref']==selected_ref for s in r['stops'])]
 selector_ok=actual_selected['nodes']==[node] and {relation_id(r) for r in actual_selected['transit_segments']}=={relation_id(r) for r in related} and {r['id'] for r in actual_selected['routes']}=={r['route_id'] for r in related} and actual_selected['missing_refs']==['fixture:missing-node']
 report['checks'].append({'name':'生产selector完整节点及全部多归属线路等值于内部full','passed':selector_ok})
 report['checks'].append({'name':'生产default保内部full全部身份与停站顺序且无重复memberships','passed':{n['ref'] for n in actual_default['nodes']}=={n['ref'] for n in internal['nodes']} and {r['id'] for r in actual_default['routes']}=={r['id'] for r in internal['routes']} and {relation_id(r) for r in actual_default['transit_segments']}=={relation_id(r) for r in internal['transit_segments']} and all('memberships' not in n for n in actual_default['nodes'])})
 request=json.loads((E/'round29/reconstructed-step11-request-private.json').read_text());before=len(compact(request));old_result=json.loads(request['messages'][-2]['content']);old_result['graph']=projected;request['messages'][-2]['content']=compact(old_result).decode();request['tools']=load('model-graph-tools.json');after=len(compact(request))
 (work/'reconstructed-step11-projected-private.json').write_bytes(compact(request))
 report['bytes']={'captured_full_graph':len(compact(full)),'projected_graph_native':(jail/'model-graph-captured-projection.json').stat().st_size,'step11_before':before,'step11_after_with_new_schema':after,'limit':1048576,'new_schema':len(compact(request['tools']))}
 report['checks'].append({'name':'完整历史保留且第11请求加新schema仍明显小于1MiB','passed':after<1048576 and after<before and len(request['messages'])==len(json.loads((E/'round29/reconstructed-step11-request-private.json').read_text())['messages'])})
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(work/'report-safe.json').write_text(json.dumps({k:v for k,v in report.items() if k!='native_errors'},ensure_ascii=False,indent=2));print(work/'report.json')
 assert all(c['passed'] for c in report['checks']) and report['provider_calls']==0,str(work/'report.json')
