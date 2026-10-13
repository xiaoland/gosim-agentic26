"""日历冷cache只读status与显式操作的初始化顺序；不请求真实授权/事件。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    assert not (Path(jail)/'context-calendar.json').exists()
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
let cl_case=0 let cl_ready=false let cl_calls=[] let cl_results=[] let cl_violation=false let cl_actual=nil
let cl_calendar={id:"synthetic-calendar" account:"synthetic-account" name:"合成日历" account_name:"合成账户" writable:false}
fn cc_dispatch(method,args,done){cl_calls.push({test_case:cl_case method:method ready:cl_ready})
 if cl_case==0 {if method!="device_calendar.permission.status" {cl_violation=true return -1} return product_cc_dispatch(method,args,done)}
 if method=="device_calendar.permission.status" {
  start_timeout(0.02,||{
   if cl_case>=4 && cl_case<=6 {done({is_ok:false data:nil error:"storage_error: synthetic cold init failure"}) return}
   cl_ready=true done({is_ok:true data:{supported:true app_consent:cl_case<7 os_permission:if cl_case<7 {"granted"} else {"not_determined"}} error:nil})
  })
 } else {
  if !cl_ready {cl_violation=true done({is_ok:false error:"cache_uninitialized: synthetic ordering violation" data:nil}) return -1}
  if method=="device_calendar.permission.request" {done({is_ok:true data:{supported:true app_consent:true os_permission:"granted"} error:nil})}
  elif method=="device_calendar.calendars.list" {done({is_ok:true data:{calendars:[cl_calendar]} error:nil})}
  elif method=="device_calendar.calendars.select" {done({is_ok:true data:{handle:"synthetic-handle" calendar:cl_calendar} error:nil})}
  else {cl_violation=true done({is_ok:false data:nil error:"fixture forbids event reads"})}
 }
 return -1
}
fn cl_done(result){if cl_case==0 {cl_actual=result} cl_results.push({test_case:cl_case result:result selection_cleared:cc_state.selection==nil})
 fs.write("calendar-lifecycle-progress.json",{test_case:cl_case results:cl_results calls:cl_calls violation:cl_violation}.to_json())
 cl_case+=1 if cl_case<9 {start_timeout(0.01,||cl_next())} else {fs.write("calendar-lifecycle-result.json",{results:cl_results calls:cl_calls violation:cl_violation actual:cl_actual}.to_json())}
}
fn cl_next(){cl_ready=false cc_state.busy=false cc_state.loaded=true cc_state.selection=if cl_case>=7 {{schema:1 handle:"synthetic-stale" calendar:cl_calendar}} else {nil}
 if cl_case==0 {context_calendar_status(cl_done)}
 elif cl_case==1 || cl_case==4 {context_calendar_permission(cl_done)}
 elif cl_case==2 || cl_case==5 || cl_case==7 {context_calendar_choices(cl_done)}
 else {context_calendar_select("synthetic-calendar",cl_done)}
}
start_timeout(0.8,||cl_next())
'''
def source(original):
    for name in ['trace_initialize','trip_load','cc_dispatch']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(500):
        if (jail/'calendar-lifecycle-result.json').exists():break
        time.sleep(.02)
    observed=json.loads((jail/'calendar-lifecycle-result.json').read_bytes());checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    def calls(i):return [c for c in observed['calls'] if c['test_case']==i]
    real=calls(0);actual=observed['actual']
    check('真实冷cache只一次status且不等于授权',len(real)==1 and real[0]['method']=='device_calendar.permission.status' and actual['status'] in ('authorization_needed','unsupported') and actual.get('records')==[])
    for i,method in [(1,'permission.request'),(2,'calendars.list'),(3,'calendars.select')]:
        cs=calls(i);check('显式'+method+'等待status完成',len(cs)==2 and cs[0]['method']=='device_calendar.permission.status' and cs[1]['method']=='device_calendar.'+method and cs[1]['ready'] and observed['results'][i]['result']['success'])
    check('三入口初始化失败不续调宿主',all(len(calls(i))==1 and not observed['results'][i]['result']['success'] for i in (4,5,6)))
    check('未授权list/select明确拒绝清旧选择且不派发',all(len(calls(i))==1 and observed['results'][i]['result']['status']=='authorization_needed' and not observed['results'][i]['result']['success'] and observed['results'][i]['selection_cleared'] for i in (7,8)))
    check('全组严格顺序无自动授权无个人事件读取',not observed['violation'] and sum(c['method']=='device_calendar.permission.request' for c in observed['calls'])==1 and not any('events.' in c['method'] for c in observed['calls']))
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':observed,'real_permission_status_calls':1,'real_permission_requests':0,'real_calendar_list_select_events':0,'model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'boundary':'新隔离HOME无calendar consent文件/新process cache；只有case0调用真实status，case1–8严格异步合成backend，不代表用户已授权。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
