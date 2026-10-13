"""首模型上下文的真实生产启动边界；延迟来自既有skills worker队列，零联网。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'build/research/rail-integration/e2e'
def prepare(jail):
 directory=Path(jail)/'model-bootstrap-fixture';directory.mkdir()
 value=json.loads((E/'round28/input-safe.json').read_text())
 (directory/'input.json').write_text(json.dumps({'text':value['input']},ensure_ascii=False))
 boundary={'input_round':28,'input_codepoints':len(value['input']),'expected_minutes':840,'expected_budget_cents':20000,'backend_delay_ms':200,'delay_kind':'worker queued latency from a preceding actual skills/catalog.json async read; not private-config file-read duration','context':'actual start_task_ready resets first context; no synthetic agent_begin or model reply','model_requested':False,'provider_requested':False}
 (directory/'boundary.json').write_text(json.dumps(boundary));return boundary
FIXTURE=r'''
let mb_input="" let mb_case=0 let mb_checks=[] let mb_cases=[] let mb_dispatches=0 let mb_failures=0 let mb_before_dispatches=0 let mb_before_failures=0 let mb_pending_heartbeats=0 let mb_context_entries=0 let mb_hard=false let mb_done=false let mb_case_started=0 let mb_queue_started=0 let mb_queue_returned=0 let mb_record=nil let mb_host_observation=nil let mb_provider_calls=0
fn mb_check(name,passed){mb_checks.push({name:name passed:passed}) fs.write("model-bootstrap-progress.json",{test_case:mb_case checks:mb_checks dispatches:mb_dispatches failures:mb_failures}.to_json())}
fn request_failed(record,text){mb_failures+=1 product_request_failed(record,text)}
fn model_task_context(){mb_context_entries+=1 if mb_hard {mb_hard=false loop {}} return product_model_task_context()}
fn amap_request(path,params,token,done){mb_provider_calls+=1}
fn mb_host_request(service,body,done){mb_dispatches+=1 let user=body.messages[1].content.parse_json() let facts=user.facts
 mb_host_observation={service:service message_count:body.messages.len() request_matches:user.request==mb_input limits:facts.limits received_at:facts.received_at arrive_by:facts.arrive_by received_at_label:facts.received_at_label arrive_by_label:facts.arrive_by_label timezone:facts.timezone}
 start_timeout(0.15,||mb_case_done()) return "isolated-first-host-dispatch"
}
fn mb_heartbeat(){if mb_done{return} if model_request_owner!=nil && route_get(model_request_owner,"processing_stage")=="private_config_load" && !private_config_cached {mb_pending_heartbeats+=1} start_timeout(0.02,||mb_heartbeat())}
fn mb_case_done(){let dispatched=mb_dispatches-mb_before_dispatches let failed=mb_failures-mb_before_failures let record=if model_requests.len()>0 {model_requests[0]} else {nil}
 if mb_case==0 {
  let valid=mb_host_observation!=nil && mb_host_observation.service=="model.chat" && mb_host_observation.message_count==2 && mb_host_observation.request_matches && mb_host_observation.limits.minutes==840 && mb_host_observation.limits.budget_cents==20000 && mb_host_observation.arrive_by-mb_host_observation.received_at==840*60
  mb_check("原14h首次context在200ms worker queued latency仍响应且派发一次",dispatched==1 && failed==0 && valid && private_config_cached && mb_pending_heartbeats>=2 && mb_queue_returned-mb_queue_started>=0.19)
 } elif mb_case==1 {mb_check("旧run的迟到首配置回调不写cache或派发",dispatched==0 && failed==0 && !private_config_cached && private_config_text==nil && agent_active)}
 elif mb_case==2 {mb_check("无效配置JSON明确失败且零派发",dispatched==0 && failed==1 && !agent_active && phase=="failed" && record!=nil && record.state=="configuration_error")}
 else {mb_check("checked initial_context硬预算错误明确失败且零派发",dispatched==0 && failed==1 && !agent_active && phase=="failed" && record!=nil && record.state=="model_execution_failed")}
 mb_cases.push({test_case:mb_case dispatched:dispatched failures:failed private_config_cached:private_config_cached pending_heartbeats:mb_pending_heartbeats context_entries:mb_context_entries queue_latency_ms:(mb_queue_returned-mb_queue_started)*1000 record_state:if record!=nil {record.state} else {nil} record_phase:if record!=nil {route_get(record,"processing_stage")} else {nil} active:agent_active phase:phase elapsed_ms:(time_now()-mb_case_started)*1000})
 mb_case+=1 start_timeout(0.1,||mb_start())
}
fn mb_start(){if mb_case>=4 {mb_report() return}
 mb_before_dispatches=mb_dispatches mb_before_failures=mb_failures mb_pending_heartbeats=0 mb_context_entries=0 mb_case_started=time_now() mb_hard=mb_case==3 agent_skill_catalog_cache=nil
 if mb_case==2 {fs.write("private-config.json","{invalid-bootstrap-fixture")}
 elif mb_case==3 {fs.write("private-config.json","{}")}
 reset_private_config() trip_records=[] trip_selected_id=nil trip_replay=false guardian_mode=false
 mb_queue_started=time_now() fs.read_async("skills/catalog.json",fn(reply){mb_queue_returned=time_now()})
 start_task_ready(mb_input,false)
 if mb_case==1 {start_timeout(0.07,||{run_id+=1 agent_active=true phase="replacement" model_request_owner={kind:"agent" run:run_id step:1 started_at:time_now() state:"pending"}})}
 let test_case=mb_case start_timeout(0.9,||{if mb_case==test_case && test_case!=0 {mb_case_done()}})
}
fn mb_report(){if mb_done{return} mb_done=true fs.write("model-bootstrap-report.json",{checks:mb_checks cases:mb_cases dispatches:mb_dispatches failures:mb_failures provider_calls:mb_provider_calls host_observation:mb_host_observation}.to_json())}
start_timeout(1,||fs.read_async("model-bootstrap-fixture/input.json",fn(reply){mb_input=reply.text.parse_json().text mb_heartbeat() mb_start() start_timeout(12,||mb_report())}))
'''
def source(original):
 for name in ['request_failed','model_task_context','amap_request']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 needle='record.host_request_id=host.request("model.chat",body,fn(reply){';assert original.count(needle)==1
 original=original.replace(needle,'record.host_request_id=mb_host_request("model.chat",body,fn(reply){',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 for _ in range(900):
  if (jail/'model-bootstrap-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'model-bootstrap-report.json').read_text()) if (jail/'model-bootstrap-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'model-bootstrap-fixture/boundary.json').read_text()),native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],model_provider_requested=False)
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(work/'report-safe.json').write_text(json.dumps({k:v for k,v in report.items() if k!='native_errors'},ensure_ascii=False,indent=2));print(work/'report.json')
 assert len(report.get('checks',[]))==4 and all(c['passed'] for c in report['checks']),str(work/'report.json')
 assert report.get('dispatches')==1 and report.get('provider_calls')==0,str(work/'report.json')

# 最终源码只追加核验配置guard；先前版本三个启动边界证据不重复执行。
def invalid_source(original):
 injected=source(original)
 injected=injected.replace('mb_input=reply.text.parse_json().text mb_heartbeat() mb_start()','mb_input=reply.text.parse_json().text mb_case=2 mb_heartbeat() mb_start()')
 injected=injected.replace('mb_case+=1 start_timeout(0.1,||mb_start())','mb_report()')
 return injected

def invalid_run(work,jail,original,injected):
 for _ in range(600):
  if (jail/'model-bootstrap-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'model-bootstrap-report.json').read_text()) if (jail/'model-bootstrap-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'model-bootstrap-fixture/boundary.json').read_text()),native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],model_provider_requested=False,validation_scope='Only invalid configuration stage; normal/oldrun/hardbudget evidence belongs to previous 0a53 version.')
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(work/'report-safe.json').write_text(json.dumps({k:v for k,v in report.items() if k!='native_errors'},ensure_ascii=False,indent=2));print(work/'report.json')
 assert len(report.get('checks',[]))==1 and report['checks'][0]['passed'],str(work/'report.json')
