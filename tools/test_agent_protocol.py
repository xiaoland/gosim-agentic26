"""Native replay of actual request/assistant/tool boundaries; no model service."""
import hashlib,json,time

FIXTURE=r'''
let protocol_case=0 let protocol_turn=0 let protocol_checks=[] let protocol_raw=[] let protocol_body=nil let protocol_answer=nil
let protocol_text="中文引号\\\"与反斜杠\\\\及换行\\n"
fn trace_emit_run(event,data,call_id,token){
 if event=="assistant_message" {protocol_raw.push(data.message.parse_json())}
 product_trace_emit_run(event,data,call_id,token)
}
fn protocol_call(id,name,args){return {id:id type:"function" function:{name:name arguments:args.to_json()}}}
fn protocol_host_request(service,body,done){
 protocol_turn+=1 protocol_body=body
 let message={role:"assistant" content:"现在渲染完整UI" reasoning_content:protocol_text reasoning_details:[{type:"reasoning.text" text:protocol_text}]}
 let finish="stop"
 if protocol_case<=3 && protocol_turn==1 {
  message.content=protocol_text
  let kept=route_candidate("protocol-route","public_transit",300,500,time_now(),time_now(),"114,22","114,22",true,[])
  assign_candidate_ref(kept) candidates.push(kept)
  message.tool_calls=[protocol_call("protocol-skill","read_skill",{name:"mixed-routing"}) protocol_call("protocol-render","render_summary",{source:"protocol_kept := Label{text:\"已取得的原生块\"}"})]
  finish="tool_calls" protocol_answer=message
 } elif protocol_case==1 {
  let messages=body.messages
  protocol_checks.push({name:"assistant推理字段正文双工具原样进入下一实际请求" passed:messages[2].to_json()==protocol_answer.to_json() && messages[2].reasoning_content==protocol_text && messages[2].reasoning_details[0].text==protocol_text && messages[2].tool_calls[1].id=="protocol-render"})
  protocol_checks.push({name:"两工具回执按call_id且完整skill正文进入下一实际请求" passed:messages[3].role=="tool" && messages[3].tool_call_id=="protocol-skill" && messages[3].content.parse_json().content==read_text("skills/mixed-routing/SKILL.md") && messages[4].tool_call_id=="protocol-render" && messages[4].content.parse_json().success})
  message.content="本轮正常结束"
 } elif protocol_case==2 {finish="tool_calls"}
 elif protocol_case==3 {finish="length" message.tool_calls=[protocol_call("must-not-run","read_skill",{name:"mixed-routing"})]}
 elif protocol_case==4 {message.content=""}
 elif protocol_case==5 {message.content="" message.tool_calls=[protocol_call("failed-render","render_summary",{source:"not_a_real_widget := TotallyMissingWidget{}"})] finish="tool_calls"}
 if protocol_case==5 && protocol_turn>1 {message={role:"assistant" content:""} finish="stop"}
 start_timeout(0.01,||done({is_ok:true data:{response:{model:"MiniMax-M3" choices:[{message:message finish_reason:finish}]}}}))
 return "protocol-local"
}
fn protocol_start(){
 protocol_case+=1 protocol_turn=0 protocol_raw=[]
 start_task_with("40分钟内到深圳机场，预算50元",false)
 start_timeout(0.1,||protocol_poll())
}
fn protocol_poll(){
 if agent_active {start_timeout(0.1,||protocol_poll()) return}
 let trip=trip_by_id(trip_selected_id)
 protocol_checks.push({name:"请求省略thinking并显式reasoning_split第"+protocol_case passed:route_get(protocol_body,"thinking")==nil && protocol_body.reasoning_split==true})
 protocol_checks.push({name:"原始assistant记录保留推理字段第"+protocol_case passed:protocol_raw.len()>0 && protocol_raw[0].reasoning_content==protocol_text && protocol_raw[0].reasoning_details[0].text==protocol_text})
 if protocol_case==1 {
  protocol_checks.push({name:"正常stop保存completed并保成功原生块" passed:phase=="waiting" && trip.status=="completed" && protocol_turn==2 && generated_render_complete && block_by_id("summary")!=nil})
  let prompt=protocol_body.messages[0].content
  protocol_checks.push({name:"技能触发元提示绑定description与实际read_skill参数" passed:prompt.search("description")>=0 && prompt.search("read_skill(name)")>=0 && prompt.search("相对path")>=0})
 } elif protocol_case==2 {protocol_checks.push({name:"坏tool_calls无调用明确failed且不重试" passed:phase=="failed" && trip.status=="failed" && protocol_turn==2 && model_requests[model_requests.len()-1].state=="invalid_tool_response" && decisions.len()==2 && generated_render_complete && block_by_id("summary")!=nil && candidates.len()==1 && candidates[0].price_cents==500 && trip.snapshot.route_data.len()==1})}
 elif protocol_case==3 {protocol_checks.push({name:"length可解析调用也不执行并记failed" passed:phase=="failed" && trip.status=="failed" && protocol_turn==2 && decisions.len()==2 && generated_render_complete && block_by_id("summary")!=nil && candidates.len()==1 && candidates[0].price_cents==500 && trip.snapshot.route_data.len()==1 && agent_messages.len()==6 && model_requests[model_requests.len()-1].state=="truncated_response"})}
 elif protocol_case==4 {protocol_checks.push({name:"空stop无成功稿不保存completed" passed:phase=="failed" && trip.status=="failed" && runtime_status!=""})}
 elif protocol_case==5 {protocol_checks.push({name:"仅失败生成块加空stop不保存completed" passed:phase=="failed" && trip.status=="failed" && !generated_render_complete && protocol_turn==2})}
 if protocol_case<5 {start_timeout(0.1,||protocol_start())} else {fs.write("harness-smoke.json",{checks:protocol_checks}.to_json())}
}
start_timeout(1,||protocol_start())
'''

def source(original):
    return original.replace('host.request("model.chat", body,', 'protocol_host_request("model.chat", body,',1).replace('fn trace_emit_run(', 'fn product_trace_emit_run(',1)+'\n'+FIXTURE

def run(w,jail,original,injected):
    report=None
    for _ in range(250):
        try:report=json.loads((jail/'harness-smoke.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):pass
        if report:break
        time.sleep(.1)
    assert report,'native replay did not finish; '+str(w/'native.log')
    errors=[line for line in (w/'native.log').read_text().splitlines() if '[E]' in line]
    unexpected=[line for line in errors if 'TotallyMissingWidget' not in line and 'on_render closure failed; discarding its output: [Error:NotFound]' not in line]
    assert not unexpected, unexpected
    report.update(expected_injected_render_errors=len(errors),unexpected_native_errors=0)
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(injected.encode()).hexdigest(),model_called=False,actual_production_request_and_loop=True)
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(x['passed'] for x in report['checks']),report
    print('PASS: '+str(len(report['checks']))+'项协议原生检查；'+str(w/'report.json'))
