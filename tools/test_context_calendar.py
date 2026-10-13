"""真实未授权状态与明确合成的系统日历响应契约；不请求或批准权限。"""
import json, time

FIXTURE = r'''
let ct_step=0 let ct_mode="real" let ct_checks=[] let ct_calls=[] let ct_before=0 let ct_actual=nil
let ct_calendar={id:"synthetic-calendar" account:"synthetic-account" name:"合同测试日历" account_name:"隔离合成账户" writable:false}
let ct_event={id:"synthetic-event" title:"合成合同事件" start_ms:1791735000123 end_ms:1791738600456 timezone:"America/New_York" all_day:false location:"合同测试位置" notes:"第一行\n第二行" recurring:true has_attendees:true revision:"synthetic-content-revision"}
fn ct_check(name,passed){ct_checks.push({name:name passed:passed})}
fn cc_dispatch(method,args,done){
 ct_calls.push({method:method args:args})
 if ct_mode=="real" {return product_cc_dispatch(method,args,done)}
 if method=="device_calendar.permission.status" {done({is_ok:true data:{supported:true app_consent:true os_permission:"granted"} error:nil})}
 elif method=="device_calendar.events.list" {
  if ct_mode=="stale" {done({is_ok:false data:nil error:"invalid_handle: Select a calendar for this app account"})}
  else {done({is_ok:true error:nil data:if ct_mode=="empty" {{events:[] truncated:false}} elif ct_mode=="malformed" {{events:[{id:"missing-time"}] truncated:false}} else {{events:[ct_event] truncated:true}}})}
 } else {done({is_ok:false data:nil error:"合同禁止请求权限或选择日历"})}
 return -1
}
fn ct_done(result){
 fs.write("calendar-contract-step.json",{step:ct_step mode:ct_mode result:result state:cc_state calls:ct_calls integer_check:{value:1791735000000 floored:floor(1791735000000) is_number:(1791735000000).is_number() difference:1791821400000-1791735000000}}.to_json())
 if ct_step==0 {ct_actual=result ct_check("真实未授权读取返回authorization_needed且没有事件",!result.success && result.status=="authorization_needed" && result.permission.app_consent==false && result.records.len()==0)}
 elif ct_step==1 {ct_check("所选日历查询为空明确限定时间窗",result.success && result.status=="empty" && !result.truncated && result.range.start_ms==1791735000000 && result.range.end_ms==1791821400000 && result.range.limit==200 && result.calendar.id==ct_calendar.id)}
 elif ct_step==2 {
  let record=if result.records.len()>0 {result.records[0]} else {{}}
  ct_check("截断保留完整事件毫秒时区原始内容且不补更新时间",result.success && result.status=="truncated" && result.truncated && result.range.limit==50 && record.start_ms==ct_event.start_ms && record.starts_at_unix==ct_event.start_ms/1000 && record.timezone==ct_event.timezone && record.original.notes==ct_event.notes && record.raw.parse_json().revision==ct_event.revision && record.source_time==nil && !record.mock && record.kind=="calendar")
 }
 elif ct_step==3 {ct_check("失效句柄清除旧选择且不回传旧事件",!result.success && result.status=="selection_needed" && result.records.len()==0 && cc_state.selection==nil && !fs.exists("context-calendar.json"))}
 elif ct_step==4 {ct_check("缺时间的事件拒绝且不交付部分背景",!result.success && result.status=="unavailable" && result.records.len()==0 && result.error.search("invalid_response:")==0)}
 elif ct_step==5 {ct_check("反向时间窗拒绝且没有宿主调用",!result.success && result.status=="invalid_arguments" && ct_calls.len()==ct_before)}
 elif ct_step==7 {ct_check("并发读取明确busy且不重复调宿主",!result.success && result.status=="busy" && ct_calls.len()==ct_before) cc_state.busy=false}
 elif ct_step==6 {ct_check("超过宿主200条上限拒绝且没有调用",!result.success && result.status=="invalid_arguments" && ct_calls.len()==ct_before)}
 ct_step+=1
 start_timeout(0.01,||ct_next())
}
fn ct_next(){
 if ct_step==8 {
  let safe=true for call in ct_calls {if call.method=="device_calendar.permission.request" || call.method=="device_calendar.calendars.select" {safe=false}}
  ct_check("全程未请求许可或选择日历",safe)
  fs.write("context-probe.json",{schema:1 completed:true checks:ct_checks actual_authorization:ct_actual synthetic_response_cases:7 calls:ct_calls integer_check:{value:1791735000000 floored:floor(1791735000000) is_number:(1791735000000).is_number() difference:1791821400000-1791735000000}}.to_json())
  fs.write("harness-smoke.json",{checks:ct_checks actual_authorization:ct_actual synthetic_response_cases:7}.to_json())
  return
 }
 if ct_step>0 {
  ct_mode=if ct_step==1 {"empty"} elif ct_step==2 {"truncated"} elif ct_step==3 {"stale"} elif ct_step==4 {"malformed"} else {"unused"}
  cc_state.selection={schema:1 handle:"synthetic-handle" calendar:ct_calendar} cc_state.loaded=true
  if ct_step==1 {fs.write("context-calendar.json",cc_state.selection.to_json()) cc_state.loaded=false cc_state.selection=nil}
 }
 ct_before=ct_calls.len()
 if ct_step==7 {cc_state.busy=true}
 context_calendar_read(1791735000000,if ct_step==5 {1791734000000} else {1791821400000},if ct_step==2 {50} elif ct_step==6 {201} else {nil},ct_done)
}
start_timeout(1,||ct_next())
'''

def source(original):
    assert 'fn cc_dispatch(' in original, '真实日历adapter尚未集成'
    return original.replace('fn cc_dispatch(', 'fn product_cc_dispatch(', 1) + '\n' + FIXTURE


def run(work, jail, original, injected):
    path = jail / 'harness-smoke.json'
    until = time.monotonic() + 30
    while time.monotonic() < until and not path.exists():
        time.sleep(.1)
    report = json.loads(path.read_text())
    assert all(check['passed'] for check in report['checks']), report
    report.update(mode='native-hidden', calendar_permission_requested=False, calendar_events_read=False,
                  response_cases='真实未授权状态；其余事件与句柄仅合成fixture')
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('PASS: ' + str(len(report['checks'])) + '项真实日历adapter检查；' + str(work / 'report.json'))
