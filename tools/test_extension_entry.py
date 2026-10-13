"""第25轮相同请求新取得完整响应的离线option入口诊断，供应商原件不重请求。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'build/research/rail-integration/e2e'
def prepare(jail):
 events=[json.loads(x) for x in (E/'round25/trace-private.jsonl').read_text().splitlines()]
 nodes={};routes={};context=None;lastmodel=[e for e in events if e['event']=='model_request'][-1]
 messages=json.loads(json.loads(lastmodel['data'])['body'])['messages'];calls=[];laterresults=[]
 for e in events:
  d=json.loads(e['data'])
  if e['event']=='tool_call' and e['seq']>lastmodel['seq']:calls.append({'id':e['call_id'],'type':'function','function':{'name':d['name'],'arguments':d['arguments']}})
  if e['event']=='tool_result':
   value=json.loads(d['result'])
   if d['name']=='adopt_destination':context=value
   for node in value.get('new_nodes',[]):nodes[node['ref']]=node
   for poi in value.get('places',[]):
    if poi.get('node_ref'):nodes[poi['node_ref']]=dict(poi,ref=poi['node_ref'])
    if poi.get('entrance'):nodes[poi['entrance']['ref']]=poi['entrance']
   for route in value.get('routes',[]):routes[route['id']]=route
   if e['seq']>lastmodel['seq']:laterresults.append({'role':'tool','tool_call_id':e['call_id'],'name':d['name'],'content':d['result']})
 assistant=json.loads(json.loads(next(e['data'] for e in events if e['seq']==93))['message'])
 context.update(nodes=list(nodes.values()),old_public_routes=list(routes.values()),messages=messages+[assistant]+laterresults,active_call=calls[-1],query=json.loads(next(e['data'] for e in events if e['seq']==97)))
 directory=Path(jail)/'extension-entry-fixture';directory.mkdir();(directory/'context.json').write_text(json.dumps(context,ensure_ascii=False));raw=ROOT/'build/research/rail-integration/case25-provider/same-request-recheck-response.json';(directory/'response.json').write_bytes(raw.read_bytes())
 boundary={'round':25,'response':'new same-request recheck, not original unrecorded response','raw_bytes':raw.stat().st_size,'original_lastmodel_messages':len(messages),'messages_after_restored_tool_calls_results':len(context['messages']),'assistant_reply_raw_available':True,'assistant_message_source':'actual seq93 message JSON','restored_public_nodes':len(nodes),'retained_old_public_routes':len(routes),'old_raw_candidates_available':False,'source_records_restored':False}
 (directory/'boundary.json').write_text(json.dumps(boundary));return boundary
FIXTURE=r'''
let ex_context=nil let ex_response=nil let ex_marks=[] let ex_phase="loading" let ex_dispatches=0 let ex_started=0 let ex_done=false let ex_nodes=0 let ex_endpoints=0 let ex_old_public=[] let ex_reply=nil
fn ex_mark(stage){ex_marks.push({stage:stage at:time_now() nodes:ex_nodes endpoints:ex_endpoints})}
fn route_leg_endpoint(segments,first){ex_endpoints+=1 ex_mark("endpoint_enter") let value=product_route_leg_endpoint(segments,first) ex_mark("endpoint_return") return value}
fn register_route_node(ref,name,point,source,city){ex_nodes+=1 return product_register_route_node(ref,name,point,source,city)}
fn register_route_stations(segments){ex_mark("stops_enter") product_register_route_stations(segments) ex_mark("stops_return")}
fn extension_leg(route,option,index,count,mode,from,to,at,departure,sequence){ex_phase="option" ex_mark("option_enter") let leg=product_extension_leg(route,option,index,count,mode,from,to,at,departure,sequence) ex_mark("option_return") return leg}
fn route_prefix_extend(prefix,leg,id,deadline,budget){ex_mark("join_enter") let value=product_route_prefix_extend(prefix,leg,id,deadline,budget) ex_mark("join_return") return value}
fn register_mixed_candidate(next,to,mode){ex_mark("mixed_enter") let value=product_register_mixed_candidate(next,to,mode) ex_mark("mixed_return") return value}
fn query_route_summary_checked(candidate,check){ex_phase="summary" ex_mark("summary_enter") let value=product_query_route_summary_checked(candidate,check) ex_mark("summary_return") return value}
fn agent_commit_tool_result(job){ex_phase="commit" ex_mark("commit_enter") product_agent_commit_tool_result(job) ex_mark("commit_return")}
fn trace_append_file(path,text){ex_mark("trace_append_enter") product_trace_append_file(path,text) ex_mark("trace_append_return")}
fn trace_write_status(path,text){ex_mark("trace_status_enter") product_trace_write_status(path,text) ex_mark("trace_status_return")}
fn amap_request(path,params,token,done){}
fn agent_execute_next(token){if !current_task(token){return} ex_mark("accept_enter") accept_route_extension(route_prefixes["origin"],route_node("origin"),route_target_node("poi:B0FFFZRC7K"),"transit",ex_response,ex_context.query.departure_at,ex_context.query.departure_at,token) ex_mark("accept_return")}
fn agent_pump(token){if token!=run_id {return} ex_dispatches+=1 for message in agent_messages {if message.role=="tool" {ex_reply=message.content.parse_json()}} start_timeout(0.3,||ex_report())}
fn ex_report(){if ex_done{return} ex_done=true fs.write("extension-entry-report.json",{phase:ex_phase dispatches:ex_dispatches reply:ex_reply marks:ex_marks nodes:ex_nodes endpoints:ex_endpoints elapsed:time_now()-ex_started message_count:agent_messages.len() candidate_count:candidates.len() run:run_id expected_run:25 active_call:if active_tool!=nil {active_tool.id} else {nil}}.to_json())}
fn ex_begin(){run_id=25 agent_active=true phase="running" trip_replay=false
 position_record=ex_context.origin destination_record=ex_context.destination constraints=ex_context.constraints user_limits=ex_context.limits arrive_by=ex_context.arrive_by received_at=position_record.sampled_at_unix
 route_nodes={} for node in ex_context.nodes {route_nodes[node.ref]=node} route_prefixes={} candidates=[] ex_old_public=ex_context.old_public_routes agent_messages=ex_context.messages agent_calls=[ex_context.active_call] agent_call_index=0 active_tool=ex_context.active_call route_extension_count=7 candidate_sequence=19
 prepare_route_graph_base() ex_marks=[] ex_nodes=0 ex_endpoints=0 ex_started=time_now() agent_schedule_next(run_id) start_timeout(5,||ex_report())}
start_timeout(1,||fs.read_async("extension-entry-fixture/context.json",fn(reply){ex_context=reply.text.parse_json() fs.read_async("extension-entry-fixture/response.json",fn(raw){ex_response=raw.text.parse_json() ex_begin()})}))
'''
def source(original):
 for name in ['route_leg_endpoint','register_route_node','register_route_stations','extension_leg','route_prefix_extend','register_mixed_candidate','query_route_summary_checked','agent_commit_tool_result','trace_append_file','trace_write_status','agent_pump','amap_request','agent_execute_next']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+FIXTURE
def run(work,jail,original,injected):
 for _ in range(600):
  if (jail/'extension-entry-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'extension-entry-report.json').read_text()) if (jail/'extension-entry-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'extension-entry-fixture/boundary.json').read_text()),provider_called=False,model_called=False,native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line]);(work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(work/'report.json')
