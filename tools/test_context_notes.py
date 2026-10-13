"""真实Notes不可用回执与合成来源/取消合同；不打开Notes或读取个人记录。"""
import json, time

FIXTURE=r'''
let nt_step=0 let nt_mode="real" let nt_checks=[] let nt_calls=[] let nt_cancel_reply=nil let nt_cancel_callback=false let nt_before=0 let nt_actual=nil
let nt_note={id:"n000001" folder:"notes" title:"合成测试笔记" source:"合成正文第一行\n第二行：不是实际用户笔记" created_ms:1791734000123 edited_ms:1791735000456 pinned:false}
fn nt_check(name,passed){nt_checks.push({name:name passed:passed})}
fn cn_dispatch(method,args,done){
 nt_calls.push({method:method args:args})
 if nt_mode=="real" {return product_cn_dispatch(method,args,done)}
 if method=="shared_tools.cancel" {done({is_ok:true data:{cancelled:true} error:nil}) return -1}
 if nt_mode=="cancel" {nt_cancel_reply=done return -1}
 let data=if args.tool=="notes.search" {{total:80 truncated:true hits:[{id:nt_note.id title:nt_note.title preview:"合成摘要" folder:"notes" edited_ms:nt_note.edited_ms pinned:false}]}} else {nt_note}
 done({is_ok:true error:nil data:{text:"官方包络合同fixture" note:"" data:data}})
 return -1
}
fn nt_done(result){
 if nt_step==0 {nt_actual=result nt_check("真实不可用Notes明确失败且零个人记录",!result.success && result.records.len()==0 && result.error.is_string())}
 elif nt_step==1 {nt_check("搜索截断只交摘要不冒充已读正文",result.success && result.truncated && result.total==80 && result.hits[0].edited_ms==nt_note.edited_ms && result.records.len()==0 && result.detail_tool=="read_note")}
 elif nt_step==2 {let record=result.records[0] nt_check("正文保逐字原文和修改毫秒来源",result.success && record.raw==nt_note.source && record.original.to_json()==nt_note.to_json() && record.edited_ms==nt_note.edited_ms && record.source_time==nt_note.edited_ms/1000 && !record.mock && record.transport=="local-shared-tools-extension")}
 elif nt_step==3 {nt_check("空关键词拒绝且不调用宿主",!result.success && nt_calls.len()==nt_before)}
 nt_step+=1 start_timeout(0.01,||nt_next())
}
fn nt_next(){
 if nt_step==4 {
  nt_mode="cancel"
  let request=context_notes_read("n000001",fn(result){nt_cancel_callback=true})
  context_notes_cancel(request)
  context_notes_cancel(request)
  nt_cancel_reply({is_ok:true error:nil data:{text:"迟到正文fixture" note:"" data:nt_note}})
  nt_check("取消用相同客户端ID且不接纳迟到正文",!nt_cancel_callback && nt_calls[nt_calls.len()-1].method=="shared_tools.cancel" && nt_calls[nt_calls.len()-1].args.request_id==request)
  fs.write("context-probe.json",{schema:1 completed:true checks:nt_checks actual_refusal:nt_actual synthetic_response_cases:4 cancel_observation:{request:request callback_called:nt_cancel_callback cancelled_request:nt_calls[nt_calls.len()-1].args.request_id} calls:nt_calls}.to_json())
  fs.write("harness-smoke.json",{checks:nt_checks actual_refusal:nt_actual synthetic_response_cases:4}.to_json()) return
 }
 if nt_step>0 {nt_mode="synthetic"}
 nt_before=nt_calls.len()
 if nt_step==0 || nt_step==1 {context_notes_search("合同探针",nt_done)}
 elif nt_step==2 {context_notes_read("n000001",nt_done)}
 else {context_notes_search("",nt_done)}
}
start_timeout(1,||nt_next())
'''

def source(original):
    assert 'fn cn_dispatch(' in original, '真实Notes adapter尚未集成'
    return original.replace('fn cn_dispatch(', 'fn product_cn_dispatch(', 1) + '\n' + FIXTURE


def run(work,jail,original,injected):
    path=jail/'harness-smoke.json';until=time.monotonic()+30
    while time.monotonic()<until and not path.exists(): time.sleep(.1)
    report=json.loads(path.read_text())
    assert all(check['passed'] for check in report['checks']),report
    report.update(mode='native-hidden',personal_notes_read=False,response_cases='真实拒绝；其余记录与取消为合成fixture')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('PASS: '+str(len(report['checks']))+'项Notes adapter检查；'+str(work/'report.json'))
