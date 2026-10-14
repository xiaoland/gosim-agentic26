"""真实 checked timer 执行失败结算与归属；隔离回放不请求供应商或模型。"""
import hashlib,json,time
from pathlib import Path
import test_extension_entry as extension
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
 boundary=extension.prepare(jail)
 recorded=json.loads((ROOT/'build/research/rail-integration/e2e/round24/render-blocking-call-private.json').read_text())
 arguments=json.loads(json.loads(recorded['data'])['arguments'])
 directory=Path(jail)/'checked-timer-fixture';directory.mkdir()
 (directory/'render-arguments.json').write_text(json.dumps(arguments,ensure_ascii=False))
 return boundary
FIXTURE=r'''
let ct_context=nil let ct_raw=nil let ct_xml=nil let ct_case=0 let ct_checks=[] let ct_dispatches=0 let ct_failure_calls=0 let ct_before_failures=0 let ct_before_dispatches=0 let ct_job=nil let ct_reply=nil let ct_done=false let ct_trace_hit=false let ct_trace_arm=false let ct_provider_calls=0 let ct_model_calls=0 let ct_published=nil let ct_cases=[]
fn ct_progress(){fs.write("checked-timer-progress.json",{test_case:ct_case checks:ct_checks dispatches:ct_dispatches failure_calls:ct_failure_calls}.to_json())}
fn ct_check(name,passed){ct_checks.push({name:name passed:passed}) ct_progress()}
fn amap_request(path,params,token,done){ct_provider_calls+=1}
fn agent_begin(token){ct_model_calls+=1}
fn tool_execution_failed(job,error){ct_failure_calls+=1 product_tool_execution_failed(job,error)}
fn trace_append_file(path,text){if ct_trace_arm && text.search("ct_trace_only")>=0 {ct_trace_arm=false ct_trace_hit=true loop {}} product_trace_append_file(path,text)}
fn agent_commit_tool_result(pending){if ct_case==6 && !pending.owner.failure_seen {
 let owner=pending.owner agent_messages.push({role:"tool" tool_call_id:owner.call.id content:pending.result.to_json()}) loop {}
 } product_agent_commit_tool_result(pending)}
fn ct_publish(){let route=ct_raw.route let leg=extension_leg(route,route.transits[0],0,route.transits.len(),"transit",route_node("origin"),route_target_node("poi:B0FFFZRC7K"),ct_context.query.departure_at,ct_context.query.departure_at,40)
 let extended=route_prefix_extend(route_prefixes["origin"],leg,"ct-prefix",arrive_by,constraints.budget_cents) let next=extended.prefix
 route_prefixes[next.id]=next ct_published=register_mixed_candidate(next,route_target_node("poi:B0FFFZRC7K"),"transit").id
}
fn agent_execute_next(token){
 if ct_case>=7 {product_agent_execute_next(token) return}
 let job=agent_tool_job ct_job=job
 if ct_case==0 {tool_timeout(0.01,job,"fixture_before_register",||loop {})}
 elif ct_case==1 {tool_timeout(0.01,job,"fixture_after_publish",||{ct_publish() loop {}})}
 elif ct_case==2 || ct_case==3 {
  tool_timeout(0.01,job,"fixture_cancelled",||loop {})
  start_timeout(0.012,||{if ct_case==2 {run_id+=1} else {active_tool={id:"ct-replacement"}}})
  start_timeout(0.15,||ct_cancel_done(job))
 } else {tool_timeout(0.04,job,"fixture_normal",||agent_tool_result({success:true marker:"ct-complete"}))}
}
fn ct_cancel_done(job){let identity=job.call.id let count=0 for message in agent_messages {if route_get(message,"tool_call_id")==identity {count+=1}}
 ct_check(if ct_case==2 {"旧run错误回调不提交或续轮"} else {"旧call错误回调不提交或续轮"},count==0 && ct_dispatches==ct_before_dispatches && !job.settled)
 ct_cases.push({test_case:ct_case call_id:identity settled:job.settled tool_messages:count dispatches:ct_dispatches-ct_before_dispatches}) ct_case+=1 start_timeout(0.1,||ct_start_case())}
fn agent_pump(token){if token!=run_id{return} ct_dispatches+=1 let count=0 ct_reply=nil
 for message in agent_messages {if route_get(message,"tool_call_id")==ct_job.call.id {count+=1 ct_reply=message.content.parse_json()}}
 let once=count==1 && ct_dispatches==ct_before_dispatches+1 && decisions.len()==1 && ct_job.settled && active_tool==nil && agent_call_index==1
 if ct_case==0 {ct_check("注册前硬执行错误一次完整结算",once && !ct_reply.success && ct_reply.error_kind=="execution_limit" && ct_reply.published_route_ids.len()==0 && ct_job.failure_seen)}
 elif ct_case==1 {ct_check("完整Route发布后硬错误保留完整ID",once && !ct_reply.success && ct_reply.published_route_ids.len()==1 && ct_reply.published_route_ids[0]==ct_published && candidates.len()==1 && ct_job.failure_seen)}
 elif ct_case==4 {ct_check("真实普通trace硬错误不伤业务job",once && ct_reply.success && ct_trace_hit && !ct_job.failure_seen && ct_failure_calls==ct_before_failures)}
 elif ct_case==5 {ct_check("正常checked入口一次成功结算",once && ct_reply.success && !ct_job.failure_seen && ct_failure_calls==ct_before_failures)}
 elif ct_case==6 {ct_check("消息已push未release错误收束不重复",once && ct_reply.success && ct_job.failure_seen && ct_failure_calls==ct_before_failures+1)}
 elif ct_case==7 {let diagnosed=ct_reply!=nil && !ct_reply.success && ct_reply.blocks.len()==5 for block in ct_reply.blocks {if block.diagnostics=="" {diagnosed=false}}
 ct_check("原XML子VMdiagnostics正常失败回执不触发sink",once && diagnosed && !ct_job.failure_seen && ct_failure_calls==ct_before_failures)}
 elif ct_case==8 {let block=ct_reply.blocks[0] ct_check("合法原生render正常installed notified rendered",once && ct_reply.success && block.status=="initialized" && !ct_job.failure_seen && ct_failure_calls==ct_before_failures)}
 ct_cases.push({test_case:ct_case call_id:ct_job.call.id job_id:ct_job.id phase:ct_job.phase settled:ct_job.settled failure_seen:ct_job.failure_seen tool_messages:count decisions:decisions.len() dispatches:ct_dispatches-ct_before_dispatches success:ct_reply.success error_kind:route_get(ct_reply,"error_kind")})
 ct_case+=1 start_timeout(0.1,||ct_start_case())
}
fn ct_start_case(){if ct_case>=9 {ct_report() return}
 run_id+=1 agent_active=true phase="running" trip_replay=false agent_result_pending=nil agent_tool_job=nil active_tool=nil decisions=[] ui_facts_revision+=1
 agent_messages=[] for message in ct_context.messages {agent_messages.push(message)}
 ct_before_dispatches=ct_dispatches ct_before_failures=ct_failure_calls
 let name=if ct_case>=7 {"render_ui"} else {"ct_fixture"}
 let params={blocks:[{id:"ct-native" source:"Label{text:\"checked原生回执\"}"}]} if ct_case==7 {params=ct_xml}
 let call={id:"ct-call-"+ct_case function:{name:name arguments:params.to_json()}} agent_calls=[call] agent_call_index=0
 if ct_case==4 {ct_trace_arm=true trace_emit("ct_trace_only",{marker:"isolated-fixed"},nil)}
 agent_schedule_next(run_id) ct_job=agent_tool_job ct_progress()
}
fn ct_report(){if ct_done{return} ct_done=true fs.write("checked-timer-report.json",{checks:ct_checks cases:ct_cases dispatches:ct_dispatches failure_calls:ct_failure_calls provider_calls:ct_provider_calls model_calls:ct_model_calls route_ids:if ct_published!=nil {[ct_published]} else {[]} trace_hit:ct_trace_hit test_case:ct_case}.to_json())}
fn ct_begin(){run_id+=1 agent_active=true phase="running" trip_replay=false guardian_mode=false
 position_record=ct_context.origin destination_record=ct_context.destination constraints=ct_context.constraints user_limits=ct_context.limits arrive_by=ct_context.arrive_by received_at=position_record.sampled_at_unix
 route_nodes={} for node in ct_context.nodes {route_nodes[node.ref]=node} route_prefixes={} candidates=[] source_records=[] ui_blocks=[] candidate_sequence=19 route_extension_count=7 prepare_route_graph_base()
 ct_start_case() start_timeout(15,||ct_report())}
start_timeout(1,||fs.read_async("extension-entry-fixture/context.json",fn(reply){ct_context=reply.text.parse_json() fs.read_async("extension-entry-fixture/response.json",fn(raw){ct_raw=raw.text.parse_json() fs.read_async("checked-timer-fixture/render-arguments.json",fn(xml){ct_xml=xml.text.parse_json() ct_begin()})})}))
'''
def source(original):
 for name in ['amap_request','agent_begin','tool_execution_failed','trace_append_file','agent_commit_tool_result','agent_execute_next','agent_pump']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+FIXTURE
def run(work,jail,original,injected):
 for _ in range(1100):
  if (jail/'checked-timer-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'checked-timer-report.json').read_text()) if (jail/'checked-timer-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'extension-entry-fixture/boundary.json').read_text()),native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line])
 report['limitations']=['Actual case25 30 messages, 259 public nodes and full later same-request raw retained; old candidate raw/source_records/live heap are unavailable.','Application hard failures use actual VM instruction limit; host Rust test separately proves actual64ms time budget with80ms native sleep.','Original round24 XML values are preserved; native validation has one actual complete case25 candidate, not the original round24 nineteen-candidate heap.']
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 safe={key:value for key,value in report.items() if key!='native_errors'}
 (work/'report-safe.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2));print(work/'report.json')
 assert len(report.get('checks',[]))==9 and all(c['passed'] for c in report['checks']),str(work/'report.json')
 assert report.get('provider_calls')==0 and report.get('model_calls')==0,str(work/'report.json')
