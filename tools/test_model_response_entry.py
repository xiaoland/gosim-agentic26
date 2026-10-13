"""第26轮合法原模型响应的隔离入口回放；不调用 model.chat 或供应商。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'build/research/rail-integration/e2e'
def prepare(jail):
 from test_trip_snapshot import read_record
 events=[json.loads(line) for line in (E/'round26/trace-private.jsonl').read_text().splitlines()]
 request=json.loads(json.loads(next(e['data'] for e in events if e['seq']==124))['body'])
 response=json.loads(next(e['data'] for e in events if e['seq']==129))['body']
 payload=json.loads(response);assert payload['response']['choices'][0]['finish_reason']=='tool_calls'
 calls=payload['response']['choices'][0]['message']['tool_calls'];assert len(calls)==1 and calls[0]['function']['name']=='search_places'
 context=None;nodes={};public={}
 for event in events:
  if event['event']!='tool_result':continue
  data=json.loads(event['data']);value=json.loads(data['result'])
  if data['name']=='adopt_destination':context=value
  for node in value.get('new_nodes',[]):nodes[node['ref']]=node
  for route in value.get('routes',[]):public[route['id']]=route
 assert context is not None
 context.update(messages=request['messages'],nodes=list(nodes.values()),public_routes=list(public.values()))
 # 本轮没有raw或已保存snapshot；旧轮完整真实记录只用于“已发布Route不删除”边界。
 previous=E/'private-state-round22/home/apps/os.agentic26-navigation'
 index=json.loads((previous/'navigation-trips.json').read_text())['data']
 snapshot=read_record(previous,index['trips'][0]['file'])['snapshot']
 directory=Path(jail)/'model-response-fixture';directory.mkdir()
 (directory/'context.json').write_text(json.dumps(context,ensure_ascii=False))
 (directory/'response.json').write_text(response)
 for i,raw in enumerate(snapshot['route_data'][:2]):
  candidate=dict(raw,geometry_ref=raw.get('history_geometry_ref'),legs=[])
  (directory/f'route-{i}.json').write_text(json.dumps(candidate,ensure_ascii=False))
 boundary={'round':26,'request_seq':124,'response_seq':129,'step':9,'response_body_bytes':len(response.encode()),'messages':len(request['messages']),'actual_response':True,'tool_count':1,'tool_name':'search_places','original_public_routes':len(public),'original_raw_available':False,'retained_raw_source':'round22 actual full snapshot first2, original IDs; only preservation boundary','provider_requests':0,'model_requests':0}
 (directory/'boundary.json').write_text(json.dumps(boundary));return boundary
FIXTURE=r'''
let mr_context=nil let mr_payload=nil let mr_case=0 let mr_checks=[] let mr_cases=[] let mr_dispatches=0 let mr_failures=0 let mr_actions=0 let mr_before_messages=0 let mr_before_failures=0 let mr_before_dispatches=0 let mr_before_actions=0 let mr_route_ids=[] let mr_record=nil let mr_done=false let mr_hard=false let mr_trace_arm=false let mr_trace_hit=false let mr_host_replays=0 let mr_provider_calls=0
fn mr_check(name,passed){mr_checks.push({name:name passed:passed}) fs.write("model-response-progress.json",{test_case:mr_case checks:mr_checks dispatches:mr_dispatches failures:mr_failures actions:mr_actions}.to_json())}
fn request_failed(record,text){mr_failures+=1 product_request_failed(record,text)}
fn request_stage(record,stage){if stage=="model_action" {mr_actions+=1 if mr_hard {mr_hard=false loop {}}} product_request_stage(record,stage)}
fn trace_append_file(path,text){if mr_trace_arm && text.search("mr_trace_only")>=0 {mr_trace_arm=false mr_trace_hit=true loop {}} product_trace_append_file(path,text)}
fn amap_request(path,params,token,done){mr_provider_calls+=1}
fn mr_host_request(service,body,done){mr_host_replays+=1
 if mr_case==4 {mr_trace_arm=true trace_emit("mr_trace_only",{marker:"isolated-fixed"},nil)}
 start_timeout(0.01,||{done({is_ok:true data:mr_payload})
  if mr_case==2 {run_id+=1}
  elif mr_case==3 {let newer={kind:"agent" run:run_id step:step_count+1 started_at:time_now() state:"pending"} model_requests.push(newer) model_request_owner=newer}
 }) return "isolated-original-response"
}
fn agent_execute_next(token){if !current_task(token){return} let call=agent_calls[agent_call_index]
 if call.function.name=="search_places" {mr_dispatches+=1}
 start_timeout(0.1,||mr_case_done())
}
fn mr_case_done(){let ids=[] for candidate in candidates {ids.push(candidate.id)} let retained=ids.len()==mr_route_ids.len() for index id in ids {if id!=mr_route_ids[index] {retained=false}}
 let added=agent_messages.len()-mr_before_messages let dispatched=mr_dispatches-mr_before_dispatches let failed=mr_failures-mr_before_failures let actions=mr_actions-mr_before_actions
 let record=if model_requests.len()>0 {model_requests[0]} else {nil}
 if mr_case==0 || mr_case==4 {
  let legal=added==1 && dispatched==1 && failed==0 && actions==1 && agent_calls.len()==1 && agent_calls[0].function.name=="search_places" && agent_messages[agent_messages.len()-1].tool_calls[0].id==mr_payload.response.choices[0].message.tool_calls[0].id
  mr_check(if mr_case==0 {"真实合法1241B响应生产done及一次工具派发"} else {"真实独立trace硬错误不误停模型action"},legal && agent_active && retained && (mr_case==0 || mr_trace_hit))
 } elif mr_case==1 {mr_check("模型action硬执行错误明确终止且保已有Route",added==0 && dispatched==0 && failed==1 && actions==1 && !agent_active && phase=="failed" && retained)}
 else {mr_check(if mr_case==2 {"旧run模型action不动作"} else {"旧request模型action不动作"},added==0 && dispatched==0 && failed==0 && actions==0 && retained && agent_active)}
 mr_cases.push({test_case:mr_case added_messages:added dispatched:dispatched failures:failed action_entries:actions active:agent_active phase:phase retained:retained record_state:if record!=nil {record.state} else {nil}})
 mr_case+=1 start_timeout(0.15,||mr_start())
}
fn mr_start(){if mr_case>=5 {mr_report() return}
 run_id+=1 agent_active=true phase="running" active_tool=nil agent_tool_job=nil agent_result_pending=nil agent_calls=[] agent_call_index=0 decisions=[] model_requests=[] model_request_owner=nil step_count=8 trip_replay=false guardian_mode=false
 agent_messages=[] for message in mr_context.messages {agent_messages.push(message)}
 mr_before_messages=agent_messages.len() mr_before_actions=mr_actions mr_before_failures=mr_failures mr_before_dispatches=mr_dispatches mr_hard=mr_case==1
 product_agent_pump(run_id)
 let test_case=mr_case start_timeout(0.4,||{if mr_case==test_case && (test_case==1 || test_case==2 || test_case==3) {mr_case_done()}})
}
fn mr_report(){if mr_done{return} mr_done=true fs.write("model-response-report.json",{checks:mr_checks cases:mr_cases dispatches:mr_dispatches failures:mr_failures actions:mr_actions host_replays:mr_host_replays provider_calls:mr_provider_calls trace_hit:mr_trace_hit route_ids:mr_route_ids test_case:mr_case}.to_json())}
fn mr_load(index){if index>=2 {mr_begin() return} fs.read_async("model-response-fixture/route-"+index+".json",fn(reply){let candidate=reply.text.parse_json() candidate.stations_registered_generation=route_node_generation candidates.push(candidate) mr_route_ids.push(candidate.id) start_timeout(0.01,||mr_load(index+1))})}
fn mr_begin(){position_record=mr_context.origin destination_record=mr_context.destination constraints=mr_context.constraints user_limits=mr_context.limits arrive_by=mr_context.arrive_by received_at=position_record.sampled_at_unix route_nodes={} for node in mr_context.nodes {route_nodes[node.ref]=node} route_prefixes={} ui_blocks=[] source_records=[] trip_records=[] trip_selected_id=nil trip_saved_run=-1 ui_facts_revision+=1 prepare_route_graph_base()
 mr_start() start_timeout(10,||mr_report())}
start_timeout(1,||fs.read_async("model-response-fixture/context.json",fn(reply){mr_context=reply.text.parse_json() fs.read_async("model-response-fixture/response.json",fn(raw){mr_payload=raw.text.parse_json() candidates=[] mr_load(0)})}))
'''
def source(original):
 for name in ['request_failed','request_stage','trace_append_file','amap_request','agent_pump','agent_execute_next']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 needle='record.host_request_id=host.request("model.chat",body,fn(reply){'
 assert original.count(needle)==1
 original=original.replace(needle,'record.host_request_id=mr_host_request("model.chat",body,fn(reply){',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 for _ in range(800):
  if (jail/'model-response-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'model-response-report.json').read_text()) if (jail/'model-response-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'model-response-fixture/boundary.json').read_text()),native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],model_provider_requested=False)
 report['limitations']=['Actual seq124 messages and seq129 host response restored; network call alone is replaced with local recorded callback delivery.','Round26 has no raw candidate dump or saved snapshot; retained candidates are actual round22 snapshot first2, only for preservation check.','Hard execution errors use actual VM instruction limits; timer time-budget contract is separately verified in host Rust test.']
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(work/'report-safe.json').write_text(json.dumps({k:v for k,v in report.items() if k!='native_errors'},ensure_ascii=False,indent=2));print(work/'report.json')
 assert len(report.get('checks',[]))==5 and all(c['passed'] for c in report['checks']),str(work/'report.json')
 assert report.get('provider_calls')==0 and report.get('host_replays')==5,str(work/'report.json')
