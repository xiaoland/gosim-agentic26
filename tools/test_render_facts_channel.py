"""原稿不改；事实通道、源串放大与历史恢复的隔离原生判别。"""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'build/research/journey-guardian/current-online-24'

def prepare(jail):
    directory=Path(jail)/'facts-channel-fixture';directory.mkdir()
    record=json.loads((E/'current-record-private.json').read_text())
    facts=record['snapshot']['facts'];facts['channel_probe']=1
    (directory/'facts.json').write_text(json.dumps(facts,ensure_ascii=False))
    shutil.copyfile(E/'failed-render394-parameters-private.json',directory/'arguments.json')
    actual=E/'private-state/home/apps/os.agentic26-navigation'
    for pattern in ['navigation-trips*.json','navigation-trip-*.json','navigation-trip-*.text']:
        for path in actual.glob(pattern):shutil.copyfile(path,Path(jail)/path.name)
    (directory/'boundary.json').write_text(json.dumps({'facts_origin':'online24最后稳定初轮14route磁盘快照；不是失败第二loop完整内存','route_count':len(facts['routes']),'facts_utf8_bytes':len(json.dumps(facts,ensure_ascii=False).encode()),'source_origin':'failed-render394原5blocks逐值保留','stress':'30份相同事实wrapper源串（每入口5份），仅机械放大；不是线上精确堆重现','source_sha256':hashlib.sha256((E/'failed-render394-parameters-private.json').read_bytes()).hexdigest()},ensure_ascii=False))

FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){if fs.exists("channel-restart.json") {product_trip_load(done)}}
fn amap_request(path,params,token,done){}
fn dispatch_map_render(slot,candidate,token,request,target_id,geometry){}
fn minimax_request(task,input,schema,token,record,done){rc_checks.push({name:"不调用模型" passed:false})}
let rc_compiled=[] let rc_pressure_index=0 let rc_captured_commit=nil
fn set_block_visibility(block){if block.id=="channel-captured" && block.installed && rc_captured_commit==nil {let facts=block_current_handle(block).find("fact_state").text().parse_json() rc_captured_commit={probe:facts.channel_probe written:block.written_revision revision:block_current_handle(block).find("fact_revision").text()}} return product_set_block_visibility(block)}
let rc_facts=nil let rc_stage=0 let rc_checks=[] let rc_source_bytes=0 let rc_actual=nil let rc_replies=[]
fn interface_facts(){if rc_facts!=nil {return rc_facts} return product_interface_facts()}
fn ensure_interface_facts_owned(token,done,owner){if rc_facts==nil {product_ensure_interface_facts_owned(token,done,owner) return} let value=facts_json() ui_facts_object=rc_facts ui_facts_object_run=run_id ui_facts_object_revision=ui_facts_revision done(rc_facts)}
fn rc_check(name,passed){rc_checks.push({name:name passed:passed}) fs.write("channel-progress.json",{stage:rc_stage checks:rc_checks}.to_json())}
fn rc_submit(params){let call={id:"channel-"+rc_stage function:{name:"render_ui" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 active_tool=nil agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] start_timeout(0.01,||agent_schedule_next(run_id))}
fn agent_pump(token){if token!=run_id {return} let result=nil for m in agent_messages {if route_get(m,"role")=="tool" {result=m.content.parse_json()}} rc_replies.push(result)
 if rc_stage==0 {rc_check("实际失败5blocks原稿全部收到工具回执",result!=nil && result.blocks.len()==5 && result.success) let bound=block_current_handle(block_by_id("summary")).find("fact_state").text() fs.write("channel-bound-facts.json",bound) rc_stage=1
  rc_submit({blocks:[{id:"channel-probe" source:"let observed=0 on_facts_changed=fn(current){observed+=1 ui.callback.set_text(\"callback:\"+current.channel_probe+\":\"+observed)} View{width:Fill height:Fit flow:Down body_first := Label{text:\"body:\"+facts.channel_probe+\":\"+facts.routes.len()} callback := Label{text:\"pending\"} entry := TextInput{text:\"保留本地输入\"}}"} {id:"channel-hidden" overlay:true visible:false source:"on_facts_changed=fn(current){ui.hidden_callback.set_text(\"hidden:\"+current.channel_probe)} View{width:Fill height:Fit flow:Down hidden_first := Label{text:\"hidden-body:\"+facts.channel_probe} hidden_callback := Label{text:\"pending\"}}"}]})
 } elif rc_stage==1 {
  let block=block_by_id("channel-probe") let hidden=block_by_id("channel-hidden")
  rc_check("首次body与on_facts_changed完整同修订",result.success && block_current_handle(block).find("body_first").text()=="body:1:14" && block_current_handle(block).find("callback").text()=="callback:1:1" && block.written_revision==ui_facts_revision)
  rc_check("隐藏详情首次事实绑定也完成",hidden.complete && !hidden.visible && block_current_handle(hidden).find("hidden_first").text()=="hidden-body:1" && block_current_handle(hidden).find("hidden_callback").text()=="hidden:1")
  block_current_handle(block).find("entry").set_text("实际本地输入保持")
  rc_facts.channel_probe=2 ui_facts_revision+=1 refresh_generated_facts() rc_stage=2 start_timeout(0.3,||rc_refreshed())
 } elif rc_stage==4 {let block=block_by_id("__document")
  rc_check("source整稿首次body和回调绑定完整同修订",result.success && block.document && block_current_handle(block).find("document_first").text()=="document:3:14" && block_current_handle(block).find("document_callback").text()=="callback:3" && block.written_revision==ui_facts_revision)
  fs.write("channel-result.json",{checks:rc_checks source_bytes:rc_source_bytes facts_bytes:ui_facts_json.len() captured_commit:rc_captured_commit replies:rc_replies}.to_json())
 }
}
fn rc_refreshed(){let block=block_by_id("channel-probe") let hidden=block_by_id("channel-hidden")
 rc_check("后续广播完整事实修订且保留本地输入",block_current_handle(block).find("callback").text()=="callback:2:2" && block_current_handle(hidden).find("hidden_callback").text()=="hidden:2" && block_current_handle(block).find("entry").text()=="实际本地输入保持" && block.written_revision==ui_facts_revision)
 // 在mount和install间更新缓存，首绑仍使用mount捕获的旧数据与旧修订，随后才广播新修订。
 rc_stage=3 let old=ui_facts_revision
 mount_ui_blocks({blocks:[{id:"channel-captured" source:"on_facts_changed=fn(current){ui.captured_callback.set_text(\"captured:\"+current.channel_probe)} View{width:Fill height:Fit flow:Down captured_first := Label{text:\"first:\"+facts.channel_probe} captured_callback := Label{text:\"pending\"}}"}]},run_id,interface_revision)
 rc_facts.channel_probe=3 ui_facts_revision+=1 facts_json()
 start_timeout(0.4,||{let captured=block_by_id("channel-captured") rc_check("安装延迟不混合捕获数据与修订",rc_captured_commit!=nil && rc_captured_commit.probe==2 && rc_captured_commit.written==old && rc_captured_commit.revision==""+old) refresh_generated_facts()
  start_timeout(0.2,||{rc_check("捕获首绑后收到新的完整修订",block_current_handle(captured).find("captured_callback").text()=="captured:3" && captured.written_revision==ui_facts_revision) rc_stage=4 rc_submit({source:"on_facts_changed=fn(current){ui.document_callback.set_text(\"callback:\"+current.channel_probe)} View{width:Fill height:Fit flow:Down document_first := Label{text:\"document:\"+facts.channel_probe+\":\"+facts.routes.len()} document_callback := Label{text:\"pending\"}}"})})
 })
}
fn rc_start(){run_id+=1 agent_active=true phase="running" trip_replay=false trip_loading=false trip_records=[] trip_selected_id=nil ui_facts_revision+=1 ui_facts_cached_revision=-1 rc_pressure()}
fn rc_pressure(){
 let block={id:"pressure" overlay:false document:false height:nil revision:1 content_sizing:"natural"}
 for i in 5 {let value=block_source(block,"Label{text:\"隔离源串压力\"}") rc_compiled.push(value) rc_source_bytes+=value.len() rc_pressure_index+=1}
 fs.write("channel-pressure-progress.json",{built:rc_pressure_index source_bytes:rc_source_bytes}.to_json())
 if rc_pressure_index<30 {start_timeout(0.01,||rc_pressure()) return}
 rc_check("30份源串构造完成且未嵌入全量事实",rc_compiled.len()==30 && rc_source_bytes<400000)
 fs.write("channel-pressure.json",{source_bytes:rc_source_bytes facts_bytes:ui_facts_json.len()}.to_json())
 rc_compiled=[] start_timeout(0.01,||rc_submit(rc_actual))
}
start_timeout(0.9,||{
 if fs.exists("channel-restart.json") {start_timeout(4,||{let blocks=[] let correct=true let count=0 for block in ui_blocks {if !block.installed || !block.notified {correct=false} else {let fact=block_current_handle(block).find("fact_state").text().parse_json() if fact.routes.len()!=14 || fact.history.current!=false {correct=false} count+=1} blocks.push({id:block.id installed:block.installed notified:block.notified error:block.error})} fs.write("channel-cold-result.json",{passed:trip_replay && count==4 && correct blocks:blocks route_count:trip_history.facts.routes.len()}.to_json())}) return}
 fs.read_async("facts-channel-fixture/facts.json",fn(reply){rc_facts=reply.text.parse_json() fs.read_async("facts-channel-fixture/arguments.json",fn(args){rc_actual=args.text.parse_json() rc_start()})})
})
'''

def source(original):
    if os.environ.get('NAV_RENDER_FACTS_BASELINE')=='1':
        original=subprocess.check_output(['git','show','8ff06ea:bundle/main.splash'],cwd=ROOT,text=True)
    for name in ['trace_initialize','trip_load','amap_request','dispatch_map_render','minimax_request','interface_facts','ensure_interface_facts_owned','agent_pump','set_block_visibility']:
        original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
    return original+'\n'+FIXTURE


def run(work,jail,request,stop,launch,original,injected):
    baseline=os.environ.get('NAV_RENDER_FACTS_BASELINE')=='1'
    def wait(name,seconds=25):
        until=time.monotonic()+seconds
        while not (jail/name).exists() and time.monotonic()<until:time.sleep(.05)
        return json.loads((jail/name).read_text()) if (jail/name).exists() else None
    if baseline:
        wait('channel-result.json',14)
        errors=[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l]
        report={'expected_baseline_failure':any('heap allocation limit exceeded' in l for l in errors),'pressure_finished':(jail/'channel-pressure.json').exists(),'native_errors':errors,'boundary':json.loads((jail/'facts-channel-fixture/boundary.json').read_text()),'tested_commit':'8ff06ea'}
        (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert report['expected_baseline_failure'],work/'report.json'
        print('旧版受相同128MiB cap拒绝；'+str(work/'report.json'));return
    result=wait('channel-result.json');assert result,work/'native.log'
    result['checks'].append({'name':'原5block首次绑定事实与输入全部字段逐值相同','passed':json.loads((jail/'channel-bound-facts.json').read_text())==json.loads((jail/'facts-channel-fixture/facts.json').read_text())})
    (work/'live.png').write_bytes(request('g',raw=1))
    stop();(jail/'channel-restart.json').write_text('{}');launch('channel-cold')
    cold=wait('channel-cold-result.json',25);assert cold and cold['passed'],(cold,work)
    logs='\n'.join(p.read_text(errors='replace') for p in work.glob('*.log'))
    report={**result,'cold':cold,'main_sha256':hashlib.sha256(original.encode()).hexdigest(),'boundary':json.loads((jail/'facts-channel-fixture/boundary.json').read_text()),'native_errors':[l for l in logs.splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'mode':'macOS宿主默认桌面样式（机械通道检查，不作手机布局验收）'}
    report['checks'].append({'name':'生产trip_load/trip_restore冷恢复4原稿与完整14Route首绑','passed':cold['passed']})
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in report['checks']) and not report['native_errors'],work/'report.json'
    print(f'PASS: {len(report["checks"])} 项事实通道与冷恢复；{work / "report.json"}')
