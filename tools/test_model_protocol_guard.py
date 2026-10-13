"""第34轮真实控制序列泄漏与独立trace状态错误的隔离回归。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=ROOT/'build/research/rail-integration/e2e/round34';folder=Path(jail)/'protocol-fixture';folder.mkdir()
    request=json.loads((base/'model-request-204-private.json').read_bytes())['body']
    (folder/'request.json').write_text(request)
    for name,filename in [('leaked','model-response-209-private.json'),('structured','model-response-108-private.json')]:
        (folder/(name+'.json')).write_text(json.loads((base/filename).read_bytes())['body'])
    normal={'response':{'model':'MiniMax-M3','choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'普通说明 <think> 只是文字，已完成。'}}]}}
    (folder/'normal.json').write_text(json.dumps(normal,ensure_ascii=False))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn trip_save_current(status,done){}
let pg_input=nil let pg_replies=[] let pg_case=0 let pg_failures=0 let pg_tools=0 let pg_dispatches=0 let pg_results=[] let pg_status_arm=false let pg_status_calls=0
fn request_failed(record,text){pg_failures+=1 product_request_failed(record,text)}
fn agent_execute_next(token){if current_task(token){pg_tools+=1}}
fn pg_host(service,body,done){pg_dispatches+=1 start_timeout(0.01,||done({is_ok:true data:pg_replies[pg_case]})) return "isolated-no-network"}
fn trace_write_status(path,text){pg_status_calls+=1 if pg_status_arm {pg_status_arm=false loop {}} product_trace_write_status(path,text)}
fn pg_start(){run_id+=1 agent_active=true phase="running" answer_text="未提交正文" agent_messages=[] for message in pg_input.messages {agent_messages.push(message)} model_requests=[] model_request_owner=nil step_count=12 active_tool=nil agent_tool_job=nil agent_calls=[] agent_call_index=0 trace_state=nil
 let record=agent_request_record(run_id) let before=pg_failures let tools=pg_tools let messages=agent_messages.len()
 agent_prepare_request(run_id,record)
 start_timeout(0.5,||{
  pg_results.push({test_case:pg_case failures:pg_failures-before tools:pg_tools-tools active:agent_active phase:phase answer:answer_text record_state:record.state assistant_count:agent_messages.len()-messages assistant:agent_messages[agent_messages.len()-1] raw:pg_replies[pg_case]})
  pg_case+=1 if pg_case<3 {start_timeout(0.01,||pg_start())} else {start_timeout(0.01,||pg_trace())}
 })
}
fn pg_trace(){agent_active=true let before=pg_failures pg_status_arm=true let state={session:"protocol-fixture" instance:"vm-1" directory:"protocol-trace" seq:0 written_seq:0 segment:0 segment_bytes:0 run:run_id incomplete:false keys:[]}
 trace_schedule_status(state)
 start_timeout(0.25,||fs.write("protocol-result.json",{cases:pg_results dispatches:pg_dispatches trace:{failure_phase:route_get(state,"failure_phase") failure_kind:route_get(state,"failure_kind") incomplete:state.incomplete status_calls:pg_status_calls request_failures:pg_failures-before active:agent_active}}.to_json()))
}
fn pg_load(index){if index==3 {pg_start() return} let name=if index==0 {"leaked"} elif index==1 {"normal"} else {"structured"}
 fs.read_async("protocol-fixture/"+name+".json",fn(reply){pg_replies.push(reply.text.parse_json()) start_timeout(0.01,||pg_load(index+1))})}
start_timeout(0.8,||fs.read_async("protocol-fixture/request.json",fn(reply){pg_input=reply.text.parse_json() trip_records=[] trip_selected_id=nil trip_replay=false candidates=[] pg_load(0)}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','trip_save_current','request_failed','agent_execute_next','trace_write_status']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    needle='record.host_request_id=host.request("model.chat",body,fn(reply){';assert original.count(needle)==1
    return original.replace(needle,'record.host_request_id=pg_host("model.chat",body,fn(reply){',1)+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(600):
        if (jail/'protocol-result.json').exists():break
        time.sleep(.02)
    result=json.loads((jail/'protocol-result.json').read_bytes());cases=result['cases'];checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    a,b,c=cases
    check('实际209泄漏control明确失败一次不提交answer不执行tool',a['failures']==1 and a['phase']=='failed' and not a['active'] and a['tools']==0 and a['answer']=='未提交正文' and a['record_state']=='invalid_tool_protocol' and a['assistant_count']==1 and a['assistant']==a['raw']['response']['choices'][0]['message'])
    check('普通stop含think文字生产完整提交',b['failures']==0 and b['tools']==0 and b['phase']=='waiting' and not b['active'] and b['answer']==b['raw']['response']['choices'][0]['message']['content'])
    check('实际108结构化工具生产派发一次',c['failures']==0 and c['tools']==1 and c['assistant_count']==1 and c['active'] and result['dispatches']==3)
    t=result['trace'];check('状态checked硬退出只记录诊断不误停业务不递归',t['incomplete'] and t['failure_phase']=='status_commit' and t['failure_kind']=='execution_limit' and t['status_calls']==1 and t['request_failures']==0 and t['active'])
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':[{k:v for k,v in x.items() if k not in ('assistant','raw','answer')} for x in cases],'trace':t,'model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'boundary':'真实34 request204 messages与response209/108；normal文本明确控制，trip空且保存caller本地no-op，不恢复路图或旧trace。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(x['passed'] for x in checks),str(work/'report.json')
