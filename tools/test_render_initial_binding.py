"""隐藏区块首次事实绑定、确认超时及后续本地错误的隔离原生检查。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    b=ROOT/'build/research/rail-integration/e2e/round35';d=Path(jail)/'binding-fixture';d.mkdir()
    saved=json.loads((b/'saved-full-snapshot-private.json').read_bytes())['data']['snapshot'];assert saved is not None
    (d/'facts.json').write_text(json.dumps(saved['facts'],ensure_ascii=False,separators=(',',':')))
    (d/'original.json').write_bytes((b/'render_route_detail-220-private.json').read_bytes())
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
let ib_facts=nil let ib_original=nil let ib_stage=0 let ib_replies=[] let ib_pumps=0 let ib_done=false let ib_bind_text=""
fn ensure_interface_facts_owned(token,done,owner){ui_facts_object=ib_facts ui_facts_object_revision=ui_facts_revision ui_facts_object_run=run_id ui_facts_json=ib_facts.to_json() ui_facts_cached_revision=ui_facts_revision done(ib_facts)}
fn block_rendered(block){if block.id=="ib-timeout" {return true} return product_block_rendered(block)}
fn ib_submit(id,source){let call={id:id function:{name:"render_ui" arguments:{blocks:[{id:id source:source overlay:true visible:false height:100}]}.to_json()}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)}
fn agent_pump(token){if token!=run_id{return} ib_pumps+=1 let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}} ib_replies.push(reply) fs.write("binding-progress.json",{stage:ib_stage replies:ib_replies pumps:ib_pumps}.to_json())
 if ib_stage==0 {ib_stage=1 start_timeout(0.05,||ib_submit("ib-legal","on_facts_changed=fn(current){ui.body.find(\"bound\").set_text(\"bound:\"+current.routes.len())}\nView{bound := Label{text:\"unbound\"}}\nstart_timeout(0.7,||{let value=1 value.tostr()})"))}
 elif ib_stage==1 {ib_bind_text=block_by_id("ib-legal").handle.find("bound").text() ib_stage=2 start_timeout(0.05,||ib_submit("ib-timeout","Label{text:\"installed without fixture acknowledgement\"}"))}
 else {start_timeout(0.1,||ib_report())}
}
fn ib_report(){if ib_done{return} ib_done=true let legal=block_by_id("ib-legal") fs.write("binding-result.json",{replies:ib_replies pumps:ib_pumps bound_text:ib_bind_text facts_routes:ib_facts.routes.len() later_diagnostic:legal.handle.diagnostics() legal_complete:legal.complete}.to_json())}
start_timeout(0.8,||fs.read_async("binding-fixture/facts.json",fn(reply){ib_facts=reply.text.parse_json() fs.read_async("binding-fixture/original.json",fn(source){ib_original=source.text.parse_json() run_id+=1 agent_active=true phase="running" candidates=[] trip_records=[] trip_selected_id=nil trip_replay=false guardian_mode=false ui_blocks=[] source_records=[] route_nodes={} ib_submit("ib-original",ib_original.source)})}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump','ensure_interface_facts_owned','block_rendered']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(600):
        if (jail/'binding-result.json').exists():break
        time.sleep(.02)
    observed=json.loads((jail/'binding-result.json').read_bytes());a,b,c=observed['replies'];checks=[]
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    check('真实35原稿首次绑定tostr诊断回执且继续Agent',not a['success'] and a['blocks'][0]['installed'] and 'method tostr not found on number' in a['blocks'][0]['diagnostics'] and observed['pumps']==3)
    check('合法hidden初绑定当前facts通知成功',b['success'] and b['notified'] and b['blocks'][0]['installed'] and b['blocks'][0]['notified'] and not b['blocks'][0]['visible'] and observed['bound_text']=='bound:'+str(observed['facts_routes']))
    check('未确认超时failure保installed空diagnostics',not c['success'] and not c['notified'] and c['blocks'][0]['status']=='initialization_unconfirmed' and c['blocks'][0]['installed'] and not c['blocks'][0]['notified'] and c['blocks'][0]['diagnostics']=='')
    check('已确认后的本地回调错误不追加工具回执',observed['later_diagnostic']!='' and observed['legal_complete'] and observed['pumps']==3)
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':observed,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'35真实detail220 source未改、实际保存facts固定；ensure facts仅固定输入，不恢复候选图；timeout仅夹具截获该block通知，合法块后续计时回调错误为明确控制。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(x['passed'] for x in checks),str(work/'report.json')
