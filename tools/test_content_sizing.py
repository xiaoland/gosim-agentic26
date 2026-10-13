"""新稿内容尺寸与旧快照恢复的原生合同；只使用简单合法原生Label。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    pass
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
let cs_stage=0 let cs_checks=[] let cs_dispatches=0 let cs_reply=nil
fn cs_check(name,value){cs_checks.push({name:name passed:value}) fs.write("content-sizing-progress.json",{stage:cs_stage checks:cs_checks}.to_json())}
fn cs_cache(){ui_facts_object={routes:[] guardian:nil viewed_route_id:""} ui_facts_object_run=run_id ui_facts_object_revision=ui_facts_revision ui_facts_json=ui_facts_object.to_json() ui_facts_cached_revision=ui_facts_revision}
fn cs_submit(id,p){let call={id:id function:{name:"render_ui" arguments:p.to_json()}} agent_active=true agent_calls=[call] agent_call_index=0 active_tool=nil agent_messages=[] cs_cache() agent_schedule_next(run_id)}
fn cs_has_body(block,height){return block.source.search("body := View{width:Fill height:"+height+" flow:Down")>=0}
fn cs_finish(){fs.write("content-sizing-report.json",{checks:cs_checks dispatches:cs_dispatches stage:cs_stage}.to_json())}
fn agent_pump(token){if token!=run_id {return} cs_dispatches+=1 for message in agent_messages {if message.role=="tool" {cs_reply=message.content.parse_json()}}
 if cs_stage==0 {
  let natural=block_by_id("natural") let viewport=block_by_id("viewport")
  cs_check("新height520默认natural保存metadata且body Fit",cs_reply.success && natural.installed && natural.content_sizing=="natural" && natural.height==520 && block_content_height(natural)=="Fit" && cs_has_body(natural,"Fit"))
  cs_check("显式viewport body Fill且外height520不变",viewport.installed && viewport.content_sizing=="viewport" && viewport.height==520 && block_content_height(viewport)=="Fill" && cs_has_body(viewport,"Fill"))
  cs_stage=1 agent_active=false start_timeout(0.1,||cs_save())
 } elif cs_stage==3 {
  cs_check("无效content_sizing真实工具false反馈且不安装",!cs_reply.success && cs_reply.error.search("content_sizing")>=0 && block_by_id("invalid")==nil && cs_dispatches==2)
  cs_finish()
 }
}
fn cs_save(){cs_cache() let snapshot=trip_capture()
 let valid=snapshot.blocks.len()==2
 for block in snapshot.blocks {if block.id=="natural" {valid=valid && block.content_sizing=="natural"} elif block.id=="viewport" {valid=valid && block.content_sizing=="viewport"}}
 cs_check("生产trip_capture保两种metadata",valid)
 snapshot.blocks.push({id:"legacy" source:"Label{text:\"旧记录\"}" overlay:false height:520 visible:false document:false render_status:"installed_pending_render"})
 let now=time_now() let trip={id:"trip-1" title:"content sizing" input:"隔离内容尺寸回归" created_at:now updated_at:now status:"completed" goal:nil snapshot:snapshot _dirty:true}
 trip_records=[] trip_selected_id=nil trip_generation=0 trip_next_id=1 trip_replay=false
 trip_commit({schema:1 selected_id:"trip-1" next_id:2 trips:[trip]},fn(committed){cs_check("生产事务完整保存成功",committed) trip_read("navigation-trips.json",fn(read){
  let saved=read.data.trips[0] let metadata=saved.snapshot.blocks
  cs_check("生产读回新metadata与真正缺字段legacy等值",metadata[0].content_sizing=="natural" && metadata[1].content_sizing=="viewport" && route_get(metadata[2],"content_sizing")==nil)
  trip_records=[saved] trip_selected_id=saved.id cs_stage=2 clear_generated() trip_restore()
  start_timeout(0.5,||cs_restored())
 })})
}
fn cs_restored(){let natural=block_by_id("natural") let viewport=block_by_id("viewport") let legacy=block_by_id("legacy")
 cs_check("生产restore新natural Fit与viewport Fill保持",natural!=nil && viewport!=nil && natural.installed && viewport.installed && natural.content_sizing=="natural" && viewport.content_sizing=="viewport" && cs_has_body(natural,"Fit") && cs_has_body(viewport,"Fill"))
 cs_check("生产restore旧缺字段height520仍Fill",legacy!=nil && legacy.installed && route_get(legacy,"content_sizing")==nil && legacy.height==520 && block_content_height(legacy)=="Fill" && cs_has_body(legacy,"Fill"))
 cs_stage=3 trip_replay=false cs_submit("invalid-sizing",{blocks:[{id:"invalid" source:"Label{text:\"无效参数\"}" height:520 content_sizing:"bad-value"}]})
}
start_timeout(0.8,||{run_id+=1 candidates=[] route_nodes={} guardian_goal=nil trip_replay=false trip_records=[] trip_selected_id=nil clear_generated() cs_stage=0 cs_submit("valid-sizing",{blocks:[{id:"natural" source:"Label{text:\"自然内容\"}" height:520} {id:"viewport" source:"Label{text:\"视口内容\"}" height:520 content_sizing:"viewport"}]})})
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(1000):
        if (jail/'content-sizing-report.json').exists():break
        time.sleep(.02)
    path=jail/'content-sizing-report.json'
    report=json.loads(path.read_bytes()) if path.exists() else {'incomplete':True,'last_progress':json.loads((jail/'content-sizing-progress.json').read_bytes()) if (jail/'content-sizing-progress.json').exists() else None}
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_requested=False,provider_requested=False,native_errors=[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],fixture_boundary='简单合法Label实际安装，完整生产capture/commit/read/restore；不验收像素可见性或地图。')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not report.get('incomplete') and all(c['passed'] for c in report['checks']),str(work/'report.json')
