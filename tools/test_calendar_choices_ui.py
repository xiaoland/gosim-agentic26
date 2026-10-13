"""Android样式下实际日历列表/选择/空列表交互，全部宿主回复为合成数据。"""
import hashlib,json,re,time
from pathlib import Path
import agent
from test_trip_replay import controls
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):pass
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){done()}
let cu_calls=[] let cu_lists=0
let cu_calendars=[{id:"synthetic-one" account:"synthetic-account" name:"合成日历甲" account_name:"合成账户" writable:false} {id:"synthetic-two" account:"synthetic-account" name:"合成日历乙" account_name:"合成账户" writable:true}]
fn cc_dispatch(method,args,done){cu_calls.push({method:method args:args})
 start_timeout(0.01,||{
  if method=="device_calendar.permission.status" {done({is_ok:true data:{supported:true app_consent:true os_permission:"granted"} error:nil})}
  elif method=="device_calendar.calendars.list" {cu_lists+=1 done({is_ok:true data:{calendars:if cu_lists==1 {cu_calendars} else {[]}} error:nil})}
  elif method=="device_calendar.calendars.select" {let selected=nil for calendar in cu_calendars {if calendar.id==args.calendar_id {selected=calendar}}
   done({is_ok:true data:{handle:"synthetic-handle" calendar:selected} error:nil})
  } else {done({is_ok:false data:nil error:"fixture forbids permission request/events"})}
  fs.write("calendar-ui-observed.json",{calls:cu_calls lists:cu_lists status:context_settings_status choices_count:context_calendar_choices_cache.len() selection:cc_state.selection}.to_json())
 }) return -1
}
start_timeout(0.6,||{trip_sidebar_open=true ui.trip_sidebar.set_visible(true) ui.trip_scrim.set_visible(true)})
'''
def source(original):
    for name in ['trace_initialize','trip_load','cc_dispatch']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    match=None
    for _ in range(100):
        match=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text())
        if match:break
        time.sleep(.05)
    assert match,'remote未就绪'
    session={'port':int(match[1])}
    def request(route,**args):
        from urllib.parse import urlencode
        return agent.remote(session,route+('?' +urlencode(args) if args else ''))
    rows,capture,click,_=controls(work,request)
    time.sleep(1)
    initial=capture('calendar-ui-initial')
    click(widget='context_settings_toggle');click(text='选择读取的日历')
    listed=capture('calendar-ui-listed')
    def shown(items,text,ty=None):return [r for r in items if text in r.get('t','') and (ty is None or r.get('ty')==ty) and r.get('r',[0,0,0,0])[2]>0 and r['r'][3]>0 and r.get('v',1)!=0]
    checks=[]
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    check('实际Android列表按钮显示数量与两可见Calendar按钮',bool(shown(listed,'找到2个日历')) and len(shown(listed,'合成日历甲','Button'))==1 and len(shown(listed,'合成日历乙','Button'))==1)
    click(text='合成日历乙')
    selected=capture('calendar-ui-selected');observed=json.loads((jail/'calendar-ui-observed.json').read_bytes())
    check('实际选择回调显示已选未读且清空列表',bool(shown(selected,'已选择日历：合成日历乙；尚未读取事件。')) and not shown(selected,'合成日历甲','Button') and not shown(selected,'合成日历乙','Button') and observed['choices_count']==0 and observed['selection']['calendar']['id']=='synthetic-two')
    click(text='选择读取的日历')
    empty=capture('calendar-ui-empty');observed=json.loads((jail/'calendar-ui-observed.json').read_bytes())
    check('同UI空列表显示明确空说明',bool(shown(empty,'宿主未返回可选择的日历；尚未选择日历。')) and observed['choices_count']==0)
    methods=[c['method'] for c in observed['calls']]
    check('只严格合成status/list/select无真实授权或事件',methods==['device_calendar.permission.status','device_calendar.calendars.list','device_calendar.permission.status','device_calendar.calendars.select','device_calendar.permission.status','device_calendar.calendars.list'])
    png=(work/'calendar-ui-listed.png').read_bytes();import struct
    size=struct.unpack('>II',png[16:24]);check('实际Phone视口412x892',size==(412,892))
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':observed,'screenshot_size':size,'mode':'macOS隐藏窗口，宿主Android phone样式，非Android真机','native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'real_calendar_calls':0,'model_requested':False,'provider_requested':False,'screenshot_viewed':False,'boundary':'新无个人HOME；真实UI点击，官方Calendar字段形状的纯合成backend；未请求真实status/permission/list/select/events。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
