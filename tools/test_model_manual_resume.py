"""宿主模型失败后的显式继续规划；生产按钮/输入及归属边界，零网络。"""
import hashlib,json,re,time
from pathlib import Path
import agent
from test_trip_replay import controls
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail,case="normal"):
    (jail/"manual-resume-case.json").write_text(json.dumps({"case":case}))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_begin(){}
fn amap_request(path,params,token,done){}
let mr_case="normal" let mr_failed=nil let mr_before=nil let mr_dispatches=0 let mr_tools=0 let mr_late=0 let mr_pending_false=false let mr_after_true=false let mr_guards=nil let mr_received=0 let mr_deadline=0
fn agent_execute_next(token){mr_tools+=1}
fn trip_save_current(status,done){if status=="failed" {
 trip_pending_commit={fixture:true} start_timeout(0.02,||{mr_pending_false=!model_resume_available()})
 start_timeout(0.1,||{trip_generation+=1 trip_pending_commit=nil if done!=nil {done(true)} start_timeout(0.05,||mr_ready())})
 } elif done!=nil {done(true)}
}
fn mr_ready(){mr_after_true=model_resume_available() let trip=trip_selected_id let token=run_id
 trip_replay=true let history=!model_resume_available() trip_replay=false
 trip_selected_id="other-trip" let other=!model_resume_available() trip_selected_id=trip
 run_id+=1 let oldtoken=!model_resume_available() run_id=token
 let original=model_request_owner model_request_owner={state:"pending" run:token} let owner=!model_resume_available() model_request_owner=original
 let generation=trip_generation trip_generation+=1 let goal_change=!model_resume_available() trip_generation=generation
 let eligible=mr_failed.resume_eligible clear_model_resume() let cancelled=!model_resume_available() mr_failed.resume_eligible=eligible
 mr_guards={history:history trip:other old_token:oldtoken old_record:owner goal_change:goal_change cancel:cancelled}
 fs.write("manual-resume-ready.json",{pending_unavailable:mr_pending_false after_commit_available:mr_after_true guards:mr_guards original_messages:mr_before original_received:mr_received original_deadline:mr_deadline form_input:request_form_input model_request:request_text}.to_json())
}
fn mr_host(service,body,done){mr_dispatches+=1 fs.write("manual-resume-dispatch.json",{body:body dispatches:mr_dispatches tools:mr_tools candidates:candidates sources:source_records received_at:received_at arrive_by:arrive_by old_eligible:route_get(mr_failed,"resume_eligible") current_owner_changed:model_request_owner!=mr_failed}.to_json())
 let response={response:{model:"MiniMax-M3" choices:[{finish_reason:"stop" message:{role:"assistant" content:"合成模型完成，仅验证继续请求。"}}]}}
 model_response_received({settled:false},mr_failed,{is_ok:true data:response},run_id,fn(data){mr_late+=1})
 model_response_received({settled:false},model_request_owner,{is_ok:true data:response},run_id-1,fn(data){mr_late+=1})
 start_timeout(0.01,||{done({is_ok:true data:response}) start_timeout(0.2,||fs.write("manual-resume-completed.json",{phase:phase active:agent_active available:model_resume_available() late_actions:mr_late dispatches:mr_dispatches tools:mr_tools}.to_json()))})
 return "isolated-no-network"
}
fn mr_input_report(){if route_get(model_request_owner,"resume_input_changed")==true {fs.write("manual-resume-input.json",{changed:true available:model_resume_available() dispatches:mr_dispatches}.to_json()) return} start_timeout(0.05,||mr_input_report())}
start_timeout(0.7,||{
 mr_case=fs.read("manual-resume-case.json").parse_json().case
 let form="合成原请求，保留已完成工具" let request=if mr_case=="normal" {form} else {"重新核验已确认的出行目标"}
 ui.sentence.set_text(form) start_task_ready(request,false) guardian_mode=mr_case!="normal"
 received_at=time_now()-300 arrive_by=received_at+50400 mr_received=received_at mr_deadline=arrive_by
 trip_records=[{id:"fixture-trip" title:"合成恢复验证" input:request_form_input status:"running" goal:nil snapshot:nil created_at:received_at updated_at:received_at}] trip_selected_id="fixture-trip" trip_generation=4 trip_replay=false trip_loading=false trip_capture_pending=nil trip_pending_commit=nil guardian_goal=nil candidates=[{id:"retained-route" source_ts:received_at price_cents:5700}] source_records=[{kind:"synthetic" source:"retained-source" queried_at:received_at}] ui_blocks=[] active_tool=nil agent_tool_job={settled:true} agent_calls=[{id:"completed-tool"}] agent_call_index=1
 agent_messages=[{role:"system" content:"合成系统契约"} {role:"user" content:({request:request_text received_at:received_at arrive_by:arrive_by}).to_json()} {role:"assistant" content:nil tool_calls:[{id:"completed-tool" function:{name:"get_route" arguments:"{}"}}]} {role:"tool" tool_call_id:"completed-tool" content:({success:true route_id:"retained-route" source_ts:received_at}).to_json()}]
 mr_before=agent_messages.to_json() agent_active=true phase="running" model_requests=[] step_count=8 mr_failed=agent_request_record(run_id) mr_failed.state="host_error" mr_failed.action_started=false request_failed(mr_failed,"合成host_error，原查询已取得路线") start_timeout(0.5,||mr_input_report())
})
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_begin','amap_request','agent_execute_next','trip_save_current']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    needle='record.host_request_id=host.request("model.chat",body,fn(reply){';assert original.count(needle)==1
    return original.replace(needle,'record.host_request_id=mr_host("model.chat",body,fn(reply){',1)+'\n'+FIXTURE

def run(work,jail,original,injected,case="normal"):
    for _ in range(150):
        if (jail/'manual-resume-ready.json').exists():break
        time.sleep(.05)
    ready=json.loads((jail/'manual-resume-ready.json').read_bytes())
    m=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text());assert m;session={'port':int(m[1])}
    def request(route,**args):
        from urllib.parse import urlencode
        return agent.remote(session,route+('?' +urlencode(args) if args else ''))
    rows,capture,click,_=controls(work,request);before=capture('resume-before');assert any(r.get('i')=='query_button' and r.get('t')=='继续规划' for r in before)
    if case=="guardian-edit":
        nodes=rows()
        if not any(r.get('i')=='sentence' for r in nodes):click(text='调整要求');nodes=rows()
        field=next(r for r in nodes if r.get('i')=='sentence');x,y,w,h=field['r'];request('click',x=x+w/2,y=y+h/2,wait=1);request('t',t='修改原出行要求',wait=1)
        for _ in range(80):
            if (jail/'manual-resume-input.json').exists():break
            time.sleep(.05)
        changed=json.loads((jail/'manual-resume-input.json').read_bytes());capture('guardian-edited-before-resume')
        checks=[{'name':'守护模型指令不同于原表单仍先有资格','passed':ready['after_commit_available'] and ready['form_input']!=ready['model_request']},{'name':'实际编辑原句立即拒绝旧轮恢复且未派发','passed':changed['changed'] and not changed['available'] and changed['dispatches']==0},{'name':'目标generation及其它归属变化拒绝','passed':all(ready['guards'].values())}]
        report={'case':case,'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'ready':{k:v for k,v in ready.items() if k!='original_messages'},'input_changed':changed,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'生产start_task_ready捕获表单原文、合成守护指令差异及host_error；实际编辑TextInput，未点开始新规划。未冷重启或重新守护业务。'}
        (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json');return
    click(widget='query_button')
    for _ in range(150):
        if (jail/'manual-resume-completed.json').exists():break
        time.sleep(.05)
    dispatched=json.loads((jail/'manual-resume-dispatch.json').read_bytes());complete=json.loads((jail/'manual-resume-completed.json').read_bytes())
    messages=dispatched['body']['messages'];prior=json.loads(ready['original_messages']);runtime=json.loads(messages[-1]['content'])['runtime']
    # 真实TextInput事件调用production on_change，成功后资格仍不可复用。
    nodes=rows()
    if not any(r.get('i')=='sentence' for r in nodes):click(text='调整要求');nodes=rows()
    field=next(r for r in nodes if r.get('i')=='sentence');x,y,w,h=field['r'];request('click',x=x+w/2,y=y+h/2,wait=1);request('t',t='修改输入',wait=1)
    for _ in range(80):
        if (jail/'manual-resume-input.json').exists():break
        time.sleep(.05)
    changed=json.loads((jail/'manual-resume-input.json').read_bytes());after=capture('resume-after-input')
    checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('提交前不可继续提交后button显示继续规划',ready['pending_unavailable'] and ready['after_commit_available'])
    check('任务启动表单身份按模式保留', (ready['form_input']==ready['model_request']) if case=='normal' else (ready['form_input']!=ready['model_request'] and ready['model_request']=='重新核验已确认的出行目标'))
    check('实际点击生产继续只派发一次不重复原messages/tools',dispatched['dispatches']==1 and dispatched['tools']==0 and messages[:-1]==prior and dispatched['current_owner_changed'] and not dispatched['old_eligible'])
    check('只追加当前时间事实且原绝对期限资料守恒',len(messages)==len(prior)+1 and runtime['kind']=='model_request_resume' and runtime['received_at']==ready['original_received']==dispatched['received_at'] and runtime['arrive_by']==ready['original_deadline']==dispatched['arrive_by'] and runtime['elapsed_seconds']>=300 and not runtime['prior_results_refreshed'] and dispatched['candidates'][0]['id']=='retained-route' and dispatched['candidates'][0]['source_ts']==ready['original_received'] and dispatched['candidates'][0]['price_cents']==5700 and dispatched['sources'][0]['queried_at']==ready['original_received'])
    check('history切trip旧token旧owner无资格迟到不续',all(ready['guards'].values()) and complete['late_actions']==0 and complete['dispatches']==1)
    check('正常完成资格清除实际input.on_change不续',complete['phase']=='waiting' and not complete['active'] and not complete['available'] and changed['changed'] and not changed['available'] and changed['dispatches']==1)
    report={'case':case,'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'ready':{k:v for k,v in ready.items() if k!='original_messages'},'completed':complete,'input_changed':changed,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'代表性合成守护/普通指令及host_error/完成assistant+tool及保留路线来源；生产start_task_ready捕获句框身份、request_failed与resume按钮/agent_pump/prepare/响应，save仅模拟pending与generation提交回调，不重验存储；输入on_change真实UI事件，不读个人calendar。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
