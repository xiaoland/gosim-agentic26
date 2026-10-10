#!/usr/bin/env python3
"""隔离原生宿主验证标准工具会话与实际控件事件；模型回复为合成fixture。"""
import hashlib, importlib.util, json, re, shutil, subprocess, tempfile, time, sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=r'''
let smoke_turn=0
let smoke_token=-1
let smoke_queries=0
let smoke_first_received=0
let smoke_late_rejected=false
fn smoke_call(id,name,args){return {id:id type:"function" function:{name:name arguments:args.to_json()}}}
fn smoke_request(task,input,schema,token,record,done){
 if token!=smoke_token {smoke_token=token smoke_turn=0 smoke_queries+=1 if smoke_queries==1 {smoke_first_received=received_at}}
 smoke_turn+=1
 let message={role:"assistant" content:nil}
 if smoke_turn==1 {message.tool_calls=[smoke_call("notes-1","read_notes",{}) smoke_call("skill-1","read_skill",{name:"native_ui"})]}
 elif smoke_turn==2 {message.tool_calls=[smoke_call("render-1","render_ui",{source:"View{width:Fill height:Fit flow:Down wrap := Label{text:\"原生自然换行验证：文字应该完整显示而不是在屏幕右侧裁切。原生自然换行验证：文字应该完整显示而不是在屏幕右侧裁切。原生自然换行验证：文字应该完整显示而不是在屏幕右侧裁切。\"} for i in 20 {Label{text:\"第\"+i+\"行：这是可以纵向滚动查看的本次结果内容\"}}}"})]}
 else {message.content="本轮计算结果，仅在当前内存中"}
 let delay=0.01 if smoke_queries==2 {delay=0.8}
 start_timeout(delay,||{if current_task(token){done({model:"MiniMax-M3" choices:[{message:message finish_reason:if route_get(message,"tool_calls").is_array(){"tool_calls"}else{"stop"}}]})} else {smoke_late_rejected=true}})
}
fn smoke_report(){
 if !agent_active {
 let results=[] let users=0
 for message in agent_messages {if message.role=="tool" {results.push(message.tool_call_id)} if message.role=="user" {users+=1}}
 let checks=[]
 if phase!="cancelled" {
 checks=[
 {name:"本轮多个工具按call_id返回" passed:results.len()==3 && results[0]=="notes-1" && results[1]=="skill-1" && results[2]=="render-1"}
 {name:"每次查询都有独立system与单一user" passed:agent_messages[0].role=="system" && users==1 && agent_messages[1].content.parse_json().request==request_text}
 {name:"实际原生render诊断为空" passed:agent_messages[6].content.parse_json().success && ui.generated.diagnostics()==""}
 {name:"无tool_calls本次结束" passed:!agent_active && agent_messages[7].content.is_string()}
 {name:"旧结果文件未读取也未改写" passed:fs.read("trip.json")=="historical fixture ignored" && fs.read("agent-run.json")=="historical audit ignored"}
 ]
 if smoke_queries>=3 {checks.push({name:"停止后新输入重新起算和预算" passed:received_at>smoke_first_received && user_limits.minutes==30 && user_limits.budget_cents==8000 && arrive_by==received_at+1800}) checks.push({name:"停止旧响应不派发" passed:smoke_late_rejected})}
 }
 fs.write("harness-smoke.json",{checks:checks queries:smoke_queries phase:phase received_at:received_at}.to_json())
 }
 start_timeout(0.1,||smoke_report())
}
start_timeout(1.0,||{start_task() start_timeout(0.3,||smoke_report())})
'''
RECOVERY_FIXTURE=r'''
let recovery_error=""
let recovery_feedback=""
fn agent_pump(token){
 agent_active=false phase="waiting" render_content()
 let first=agent_messages[0].content.parse_json() let second=agent_messages[1].content.parse_json()
 fs.write("harness-smoke.json",{checks:[
 {name:"原生类型错误原文进入tool结果" passed:!first.success && first.diagnostics.search("color")>=0}
 {name:"修正中反馈不展示内部堆栈" passed:recovery_feedback=="界面正在修正；可终止本次查询"}
 {name:"成功稿清掉错误并实际挂载" passed:second.success && interface_error=="" && ui.generated.diagnostics()=="" && ui.generated.find("recovered").text()=="界面已恢复"}
 ]}.to_json())
}
fn agent_tool_result(result){
 if !result.success {
 recovery_error=result.diagnostics recovery_feedback=ui.feedback.child(0).text()
 start_timeout(0.5,||product_agent_tool_result(result))
 } else {product_agent_tool_result(result)}
}
start_timeout(1,||{
 run_id+=1 agent_active=true phase="running" agent_messages=[]
 agent_calls=[
 {id:"bad-ui" type:"function" function:{name:"render_ui" arguments:"{\"source\":\"Label{draw_text.text_style: NavRegular{color:#xf00} text:\\\"错误稿\\\"}\"}"}}
 {id:"good-ui" type:"function" function:{name:"render_ui" arguments:"{\"source\":\"recovered := Label{text:\\\"界面已恢复\\\"}\"}"}}
 ] agent_call_index=0 agent_execute_next(run_id)
})
'''
MAP_FIXTURE=r'''
let map_smoke_dispatches=0
fn load_map_slot(slot,candidate){map_smoke_dispatches+=1}
start_timeout(1,||{
 let route={id:"map-fixture" kind:"taxi" segments:[{polyline:"114,22;114.1,22.1"} {polyline:"114.1,22.1;114.2,22.2"} {polyline:"114.3,22.3;114.4,22.4"}]}
 let geometry=map_geometry(route)
 candidates=[route]
 let slot={id:"missing_image" target:"map-fixture" generation:map_generation request:1 target_id:"map-fixture" state:"loading" bytes:nil caption:"" status_widget:"" handle:nil}
 map_slots[slot.id]=slot
 let accepted=accept_map_slot(slot,"{\"status\":\"0\",\"info\":\"UNKNOWN_ERROR\",\"infocode\":\"20003\"}",run_id,1,"map-fixture","")
 let error_rejected=slot.state=="error" && slot.bytes==nil && slot.status.search("20003")>=0
 slot.state="loading" slot.target_id="different-route" fit_map_slot(slot,route)
 let obsolete_fit_skipped=slot.state=="loading"
 slot.target_id=route.id slot.interactive=true slot.camera=nil
 map_camera_changed({widget:slot.id center_lon:114 center_lat:22 zoom:9 width:388 height:240 request:10})
 map_camera_changed({widget:slot.id center_lon:114.1 center_lat:22 zoom:9 width:388 height:240 request:11})
 start_timeout(0.1,||fs.write("harness-smoke.json",{checks:[
 {name:"连续端点无损合并且不跨几何缺口" passed:geometry.paths.len()==2 && geometry.paths[0]=="114,22;114.1,22.1;114.2,22.2" && geometry.paths[1]=="114.3,22.3;114.4,22.4"}
 {name:"HTTP200业务错误不能成为ready图片" passed:!accepted && error_rejected}
 {name:"已替换路线不派发旧fit" passed:obsolete_fit_skipped}
 {name:"同批camera只派发仍当前的请求" passed:map_smoke_dispatches==1 && slot.camera.request==11}
 ]}.to_json()))
})
'''


UI_BLOCKS_FIXTURE=r'''
let blocks_started=false let blocks_checks=[] let blocks_phase=0 let blocks_first=nil let blocks_detail=nil let blocks_old_revision=0
fn blocks_check(name,passed){blocks_checks.push({name:name passed:passed})}
fn blocks_mount(params){interface_revision+=1 return mount_ui_blocks(params,run_id,interface_revision)}
fn load_map_slot(slot,candidate){
 let bytes=fs.read_bytes(if slot.block_id=="summary" {"part-a.png"} else {"part-b.png"})
 accept_map_slot(slot,bytes,run_id,slot.request,candidate.id,"合成地图：验证区块独立加载，无外网")
}
fn blocks_tick(){
 let identity=ui.trace_identity.text().parse_json()
 if trace_state==nil || identity.instance!=trace_state.instance || !fs.exists("sections-go.json") {start_timeout(0.1,||blocks_tick()) return}
 if !blocks_started {
  blocks_started=true run_id+=1 received_at=time_now() arrive_by=received_at+2400 constraints={budget_cents:5000} user_limits={minutes:40 budget_cents:5000} phase="proposal"
  candidates=[route_candidate("route-a","public_transit",1200,500,received_at,received_at,"114.01,22.01","114.01,22.01",true,[{polyline:"114,22;114.01,22.01"}]) route_candidate("route-b","taxi",900,1800,received_at,received_at,"114.02,22.02","114.02,22.02",true,[{polyline:"114,22;114.02,22.02"}])]
  candidates[0].geometry_ref="fixture-geometry-a" candidates[1].geometry_ref="fixture-geometry-b"
  viewed_route_id="route-a"
  blocks_mount(render_tool_params("render_routes",{source:"start_timeout(0.1,||ui.kept.set_text(\"TOP LEVEL RAN\")) View{width:Fill height:Fit flow:Down entry := TextInput{text:\"INITIAL\"} kept := Label{text:\"OLD\"} for i in 5 {Label{text:\"候选列表第\"+i+\"行\"}} open := Button{text:\"查看方案\" on_click:||{emit({action:\"view_route\" id:\"route-b\"}) show_block(\"route_detail\")}} for i in 16 {Label{text:\"列表后续第\"+i+\"行\"}}}"}))
  start_timeout(0.4,||{
   blocks_first=block_by_id("routes") blocks_first.handle.find("entry").set_text("LOCAL INPUT") blocks_first.handle.find("kept").set_text("LOCAL STATE")
   let original_revision=blocks_first.revision let original_source=blocks_first.source
   let rejected=blocks_mount({blocks:[{id:"routes" source:"Label{text:\"replacement\"}"},{id:"fragment-bad" source:"}{"}]})
   blocks_check("坏片段进入正常区块错误且批量保留旧稿",rejected==nil && interface_error.search("fragment-bad:")==0 && blocks_first.revision==original_revision && blocks_first.source==original_source && blocks_first.handle.find("entry").text()=="LOCAL INPUT" && block_by_id("fragment-bad")==nil)
   blocks_mount({blocks:[{id:"summary" source:"emit({action:\"map\" widget:\"same_map\" target:\"route-a\" status_widget:\"note\"}) View{width:Fill height:Fit flow:Down Label{text:\"总结区块／独立蓝色地图\"} same_map := Image{width:Fill height:120} note := Label{text:\"\"}}"}]})
   blocks_mount(render_tool_params("render_route_detail",{source:"on_facts_changed=fn(current){ui.selected.set_text(\"当前方案：\"+current.viewed_route_id)} emit({action:\"map\" widget:\"same_map\" target:\"viewed\" status_widget:\"note\"}) View{width:Fill height:Fit flow:Down show_bg:true draw_bg +: {color:#xf7f7f7} back := Button{text:\"返回列表\" on_click:||{hide_self()}} selected := Label{text:\"当前方案：\"+facts.viewed_route_id} same_map := Image{width:Fill height:120} note := Label{text:\"\"} for i in 24 {Label{text:\"详情第\"+i+\"段：分段／费用／用时／限制，合成验证\"}}}"}))
   start_timeout(0.5,||{
    blocks_detail=block_by_id("route_detail")
    blocks_check("默认详情工具实际ID与按钮目标一致",blocks_detail.id=="route_detail" && blocks_first.id=="routes")
    ui_dispatch_action({action:"show_block" block:"missing-detail" visible:true block_id:"routes"})
    blocks_check("不存在的详情目标提供本地错误且不误开其他块",blocks_first.error=="show_block目标区块不存在：missing-detail" && !blocks_detail.visible)
    blocks_first.error="" sync_block_state() render_content()
    blocks_check("追加区块保留输入、本地状态且未重跑顶层",blocks_first.handle.find("entry").text()=="LOCAL INPUT" && blocks_first.handle.find("kept").text()=="LOCAL STATE")
    blocks_check("普通总结为自然高度而非满视口",block_by_id("summary").handle.rect().height<ui_viewport.height)
    blocks_check("各块独立成功且隐藏overlay不显示",blocks_first.complete && block_by_id("summary").complete && blocks_detail.complete && !blocks_detail.container.visible())
    blocks_mount({blocks:[{id:"summary" source:"emit({action:\"map\" widget:\"same_map\" target:\"route-a\" status_widget:\"note\"}) View{width:Fill height:Fit flow:Down Label{text:\"替换总结，列表保持\"} same_map := Image{width:Fill height:120} note := Label{text:\"\"}}"}]})
    start_timeout(0.4,||{
     blocks_check("替换只重建指定块，详情与列表VM保留",blocks_first==block_by_id("routes") && blocks_detail==block_by_id("route_detail") && blocks_first.revision==1 && block_by_id("summary").revision==2)
     blocks_phase=1 fs.write("blocks-ready.json","{}")
    })
   })
  })
 }
 if blocks_phase==1 && fs.exists("blocks-opened.json") {
  blocks_phase=2
  blocks_check("真实按钮跨块打开详情并更新事实",blocks_detail.container.visible() && viewed_route_id=="route-b" && blocks_detail.handle.find("selected").text()=="当前方案：route-b")
  let one=map_slots[block_map_key("summary","same_map")] let two=map_slots[block_map_key("route_detail","same_map")]
  blocks_check("同名地图按块独立目标与字节加载",one!=nil && two!=nil && one!=two && one.target_id=="route-a" && two.target_id=="route-b" && one.state=="ready" && two.state=="ready")
  fs.write("blocks-open-checked.json","{}")
 }
 if blocks_phase==2 && fs.exists("blocks-returned.json") {
  blocks_phase=3
  if fs.exists("blocks-geometry-only.json") {fs.write("harness-smoke.json",{checks:blocks_checks}.to_json()) return}
  blocks_check("返回仅隐藏详情，列表输入和脚本状态保留",!blocks_detail.container.visible() && blocks_first.handle.find("entry").text()=="LOCAL INPUT" && blocks_first.handle.find("kept").text()=="LOCAL STATE")
  let invalid=blocks_mount({blocks:[{id:"route_detail" overlay:false source:"Label{text:\"not installed\"}"}]})
  blocks_check("位置变更输入错误不提交成功空结果",invalid==nil && block_by_id("route_detail")==blocks_detail)
  blocks_mount({blocks:[{id:"summary" source:"View{draw_bg:{color:#xff0000} Label{text:\"bad\"}}"}]})
  start_timeout(0.4,||{
   blocks_check("单块真实执行诊断不隐藏其他成功块",!render_ui_result([block_by_id("summary")]).success && render_ui_result([block_by_id("summary")]).blocks[0].diagnostics!="" && !block_by_id("summary").complete && !block_by_id("summary").container.visible() && blocks_first.complete && generated_render_complete && blocks_first.handle.find("kept").text()=="LOCAL STATE")
   blocks_old_revision=block_by_id("summary").revision
   blocks_mount({blocks:[{id:"summary" source:"Label{text:\"只修复总结区块\"}"}]})
   start_timeout(0.4,||{
    ui_dispatch_action({action:"runtime_error" block_id:"summary" block_revision:blocks_old_revision message:"OLD EVENT"})
    blocks_check("修正失败块成功且旧revision事件不污染",render_ui_result([block_by_id("summary")]).success && block_by_id("summary").complete && block_by_id("summary").error=="" && blocks_first.handle.find("entry").text()=="LOCAL INPUT")
    fs.write("blocks-repaired.json","{}")
   })
  })
 }
 if blocks_phase==3 && fs.exists("blocks-finish.json") {
  blocks_phase=4 clear_generated()
  blocks_check("新查询清空全部块与地图绑定",ui_blocks.len()==0 && inline_blocks.len()==0 && overlay_blocks.len()==0 && map_slots.to_json()=="{}" && !generated_active)
  interface_revision+=1 mount_interface("Label{text:\"旧source整稿适配\"}",run_id,interface_revision)
  start_timeout(0.4,||{
   blocks_check("旧source同引擎作为唯一文档",ui_blocks.len()==1 && block_by_id("__document").complete)
   fs.write("harness-smoke.json",{checks:blocks_checks}.to_json())
  })
 }
 start_timeout(0.1,||blocks_tick())
}
start_timeout(0.3,||blocks_tick())
'''

MAP_SECTIONS_FIXTURE=r'''
let sections_started=false let sections_checks=[] let sections_loaded={} let sections_fit=[]
fn fit_map_slot(slot,candidate){sections_fit.push(slot.id) fs.write("sections-fit.json",sections_fit.to_json()) product_fit_map_slot(slot,candidate)}
fn load_map_slot(slot,candidate){
 let params=static_map_params_selected(candidate,slot.camera,slot.path_indices)
 sections_loaded[slot.id]=params
 let bytes=fs.read_bytes(if slot.id=="part_a" {"part-a.png"} else {"part-b.png"})
 accept_map_slot(slot,bytes,run_id,slot.request,candidate.id,if params.selected {"本图分段端点，非全行程起终点"} else {"路线概览"})
}
fn sections_check(){
 let a=map_slots["part_a"] let b=map_slots["part_b"] let candidate=candidates[0]
 let whole=map_geometry(candidate).paths let one=sections_loaded["part_a"] let two=sections_loaded["part_b"]
 if one==nil || two==nil {fs.write("harness-smoke.json",{checks:[{name:"两个地图实际派发" passed:false}] fit_calls:sections_fit loaded:sections_loaded callback_marks:[ui.generated.probe_a.text() ui.generated.probe_b.text()] rectangles:[ui.generated.find("part_a").rect() ui.generated.find("part_b").rect()] mailbox:ui.generated.mailbox.text() slots:map_slots}.to_json()) return}
 let coverage=one.paths.len()+two.paths.len()==whole.len()
 for i path in one.paths {if path!=whole[i] {coverage=false}}
 for i path in two.paths {if path!=whole[i+3] {coverage=false}}
 sections_checks.push({name:"两个分地图完整覆盖原折线且不补缺口" passed:coverage && whole.len()==6})
 sections_checks.push({name:"目录索引端点点数全部对应真实折线" passed:map_path_catalog(candidate).len()==6 && map_path_catalog(candidate)[5].index==5 && map_path_catalog(candidate)[5].point_count==2 && map_path_catalog(candidate)[0].start=="114,22"})
 sections_checks.push({name:"默认仍完整请求不自动截四条" passed:static_map_params(candidate,nil).paths.len()==6})
 sections_checks.push({name:"分图AB为实际本段端点" passed:one.markers[0]=="114,22" && two.markers[0]=="114.03,22.03" && one.markers[1]==whole[2].split(";")[1] && two.markers[1]==whole[5].split(";")[1]})
 sections_checks.push({name:"两图独立fit和加载状态" passed:a.state=="ready" && b.state=="ready" && a.camera.center_lon!=b.camera.center_lon && a.path_indices.to_json()!=b.path_indices.to_json()})
 let old=a register_map_paths("part_a",candidate.id,"note_a",true,[0])
 start_timeout(0.4,||{
  sections_checks.push({name:"同目标改索引新实例请求不复用旧范围" passed:map_slots["part_a"]!=old && sections_loaded["part_a"].paths.len()==1 && sections_loaded["part_b"].paths.len()==3})
  sections_checks.push({name:"不存在的索引明确失败不静默丢段" passed:selected_map_geometry(candidate,[6]).error!=nil})
  fs.write("harness-smoke.json",{checks:sections_checks selected_paths:[map_slots["part_a"].path_indices map_slots["part_b"].path_indices] snapshot_directory_count:interface_facts().routes[0].map_paths.len()}.to_json())
 })
}
fn sections_tick(){
 let identity=ui.trace_identity.text().parse_json()
 if trace_state==nil || identity.instance!=trace_state.instance {start_timeout(0.1,||sections_tick()) return}
 if !sections_started && fs.exists("sections-go.json") {
  sections_started=true run_id+=1 received_at=time_now() arrive_by=received_at+2400 constraints={budget_cents:5000} user_limits={minutes:40 budget_cents:5000} phase="proposal"
  let seg=[] for i in 6 {let start=""+(114+i*0.01)+","+(22+i*0.01) let end=""+(114+i*0.01+0.001)+","+(22+i*0.01+0.001) seg.push({polyline:start+";"+end})}
  candidates=[route_candidate("fixture-route","public_transit",1200,500,received_at,received_at,"114.051,22.051","114.051,22.051",true,seg)]
  candidates[0].requested_origin="114,22" candidates[0].requested_destination="114.051,22.051"
  interface_revision+=1
  mount_interface("View{width:Fill height:Fit flow:Down padding:8 Label{text:\"合成折线分图：原生控件／无外网请求\"} probe_a := Label{visible:false text:\"\"} probe_b := Label{visible:false text:\"\"} part_a := AutoNaviMapView{width:Fill height:160 on_camera_changed:fn(lon,lat,zoom,width,height,request){ui.probe_a.set_text(\"A callback\") emit({action:\"map_camera\" widget:\"part_a\" center_lon:lon center_lat:lat zoom:zoom width:width height:height request:request})}} note_a := Label{text:\"\"} part_b := AutoNaviMapView{width:Fill height:160 on_camera_changed:fn(lon,lat,zoom,width,height,request){ui.probe_b.set_text(\"B callback\") emit({action:\"map_camera\" widget:\"part_b\" center_lon:lon center_lat:lat zoom:zoom width:width height:height request:request})}} note_b := Label{text:\"\"}}",run_id,interface_revision)
  start_timeout(0.4,||{ui_dispatch_action({action:"map" widget:"part_a" target:"fixture-route" path_indices:[0 1 2] status_widget:"note_a" interactive:true}) ui_dispatch_action({action:"map" widget:"part_b" target:"fixture-route" path_indices:[3 4 5] status_widget:"note_b" interactive:true})})
  start_timeout(1.3,||sections_check())
 }
 start_timeout(0.1,||sections_tick())
}
start_timeout(0.2,||sections_tick())
'''

LOOP_SETTLE_FIXTURE=r'''
let settle_started=false let settle_checks=[] let settle_scans=0 let settle_trace_failed=false let settle_refresh_failed=false let settle_done=false
fn map_geometry_uncached(candidate){settle_scans+=1 return product_map_geometry_uncached(candidate)}
fn trace_emit_run(event,data,call_id,run){
 if event=="tool_result" || event=="query_ended" || event=="query_stopped" {settle_trace_failed=true let unavailable=nil unavailable.failure() return}
 product_trace_emit_run(event,data,call_id,run)
}
fn refresh_generated_facts(){
 if settle_started && !settle_refresh_failed && agent_call_index>0 {settle_refresh_failed=true let unavailable=nil unavailable.failure() return true}
 return product_refresh_generated_facts()
}
fn minimax_request(task,input,schema,token,record,done){start_timeout(0.01,||done({choices:[{message:{role:"assistant" content:"本轮结果已返回"}}]}))}
fn settle_finish(){
 if agent_active {start_timeout(0.1,||settle_finish()) return}
 let tool_ids=[] for item in agent_messages {if item.role=="tool" {tool_ids.push(item.tool_call_id)}}
 settle_checks.push({name:"诊断和facts入口失败后已提交回执仍续轮" passed:settle_trace_failed && settle_refresh_failed && tool_ids.len()==2 && tool_ids[0]=="cold-route" && tool_ids[1]=="after-route" && agent_call_index==2})
 settle_checks.push({name:"终端日志失败不保留busy或active工具" passed:!agent_active && active_tool==nil && phase=="waiting" && answer_text=="本轮结果已返回"})
 let directory=interface_facts().routes[0].map_paths let warm=map_geometry(candidates[0]) let before=settle_scans
 map_path_catalog(candidates[0]) map_geometry(candidates[0]) interface_facts()
 settle_checks.push({name:"冷读单候选目录完整且warm不重复扫描" passed:before==1 && settle_scans==before && directory.len()==settle_geometry.paths.len() && warm.paths.len()==settle_geometry.paths.len()})
 let total=0 for item in directory {total+=item.point_count}
 settle_checks.push({name:"657点完整冷读并保留其余候选未读状态" passed:total==657 && candidates.len()==16 && interface_facts().routes[15].map_paths==nil})
 agent_active=true active_tool={id:"cancelled"} phase="running" cancel_task()
 start_timeout(0.2,||{
  settle_checks.push({name:"取消日志失败仍清busy恢复独立查询入口" passed:!agent_active && active_tool==nil && phase=="cancelled"})
  fs.write("harness-smoke.json",{checks:settle_checks candidates:candidates.len() point_count:total cold_geometry_scans:settle_scans source_geometry:settle_geometry.source_geometry}.to_json())
 })
}
let settle_geometry=nil
fn settle_seed(){
 settle_started=true settle_geometry=read_text("settle-geometry.json").parse_json()
 run_id+=1 received_at=time_now() arrive_by=received_at+2400 user_limits={minutes:40 budget_cents:5000} constraints={budget_cents:5000} phase="running" agent_active=true
 candidates=[] let segments=[] for line in settle_geometry.paths {segments.push({polyline:line})}
 for i in 16 {candidates.push(route_candidate("settle-"+i,"taxi",900,2000,received_at,received_at,settle_geometry.endpoint,settle_geometry.endpoint,true,segments))}
 ui_facts_revision+=1 interface_revision+=1
 mount_interface("Label{text:\"本轮纯读快照：完整16候选，无预扫地图目录\"}",run_id,interface_revision)
 start_timeout(0.3,||{
  settle_checks.push({name:"首次原生mount不扫描全候选地图几何" passed:settle_scans==0 && generated_render_complete && ui.generated.diagnostics()=="" && ui.generated.fact_state.text().parse_json().routes.len()==16})
  let untouched=true for candidate in candidates {if route_get(candidate,"map_paths_cache")!=nil {untouched=false}}
  settle_checks.push({name:"未读取目录明确nil不是无几何" passed:untouched && interface_facts().routes[0].map_paths==nil})
  agent_messages=[{role:"system" content:"isolated fixture"} {role:"user" content:"fixture"}]
  agent_calls=[{id:"cold-route" type:"function" function:{name:"get_route" arguments:"{\"id\":\"settle-0\"}"}} {id:"after-route" type:"function" function:{name:"read_skill" arguments:"{\"name\":\"navigation_data\"}"}}]
  agent_messages.push({role:"assistant" tool_calls:agent_calls}) agent_call_index=0
  start_timeout(0.01,||agent_execute_next(run_id)) start_timeout(0.3,||settle_finish())
 })
}
fn settle_tick(){
 let identity=ui.trace_identity.text().parse_json()
 if trace_state!=nil && identity.instance==trace_state.instance && fs.exists("loop-settle-go.json") && !settle_started {settle_seed()}
 if !settle_started {start_timeout(0.1,||settle_tick())}
}
start_timeout(0.2,||settle_tick())
'''

TERMINAL_FIXTURE=r'''
let terminal_task=0 let terminal_token=-1 let terminal_turn=0 let terminal_checks=[]
let terminal_code="```splash\nLabel{text:\"未执行代码\"}\n```"
let terminal_source="View{width:Fill height:Fit flow:Down kept := Label{text:\"原生结果仍保留\"} retained := TextInput{text:\"原始输入\"} Button{text:\"改变本地状态\" on_click: || {ui.body.find(\"retained\").set_text(\"本地输入仍保留\") ui.body.find(\"kept\").set_text(\"本地页面仍保留\")}} Button{text:\"触发局部错误\" on_click: || {try {ui.body.find(\"missing_local_widget\").set_text(\"不会执行\")} {emit({action:\"runtime_error\" message:\"局部操作失败测试\"})}}}}"
let terminal_long="" for i in 80 {terminal_long+="本次模型提供的结果说明第"+i+"行：内容应可滚动查看。\n"}
fn minimax_request(task,input,schema,token,record,done){
 if terminal_token!=token {terminal_token=token terminal_task+=1 terminal_turn=0}
 terminal_turn+=1 let message={role:"assistant" content:nil}
 if (terminal_task==1 || terminal_task==3) && terminal_turn==1 {
  let source=if terminal_task==1 {terminal_source} else {"View{show_bg:true draw_bg:{color:#xff0000} Label{text:\"错误稿\"}}"}
  message.tool_calls=[{id:"render-original" type:"function" function:{name:"render_ui" arguments:({source:source}).to_json()}}]
 } else {message.content=if terminal_task==1 || terminal_task==2 {terminal_long+terminal_code} elif terminal_task==3 {"生成执行失败，本次文字结果仍可查看"} else {""}}
 start_timeout(if terminal_task==1 && terminal_turn==2 {1.0} else {0.01},||done({choices:[{message:message}]}))
}
fn terminal_observe(){if !agent_active {start_timeout(0.3,||terminal_check())} else {start_timeout(0.1,||terminal_observe())}}
fn terminal_check(){
 let checked="terminal-checked-"+terminal_task+".json" if fs.exists(checked){return} fs.write(checked,"{}")
 if terminal_task==1 {
  terminal_checks.push({name:"正常生成稿不重复终端文字" passed:generated_render_complete && !ui.final_answer.visible() && answer_text==terminal_long+terminal_code})
  terminal_checks.push({name:"正常稿本地页面与输入状态保留" passed:ui.generated.find("kept").text()=="本地页面仍保留" && ui.generated.find("retained").text()=="本地输入仍保留"})
  terminal_checks.push({name:"终端文字仍留history与facts" passed:interface_facts().answer==answer_text && agent_messages[agent_messages.len()-1].content==answer_text})
 } elif terminal_task==2 {
  terminal_checks.push({name:"无生成稿终端文字可见且代码不执行" passed:!generated_active && ui.final_answer.visible() && ui.final_answer.text()==terminal_long+terminal_code})
 } elif terminal_task==3 {
  fs.write("single-failed-state.json",{active:generated_active complete:generated_render_complete area_visible:ui.generated_area.visible() child_visible:ui.generated.visible() text_visible:ui.final_answer.visible() text:ui.final_answer.text() diagnostic:ui.generated.diagnostics()}.to_json())
  terminal_checks.push({name:"执行失败稿使用终端文字兜底" passed:generated_active && !generated_render_complete && ui.generated.diagnostics()!="" && !ui.generated_area.visible() && ui.final_answer.visible() && ui.final_answer.text()=="生成执行失败，本次文字结果仍可查看"})
 } else {
  terminal_checks.push({name:"空终端无稿明确缺少内容" passed:!generated_active && runtime_status=="Agent没有返回可展示内容，请重新查询" && !ui.final_answer.visible()})
  fs.write("harness-smoke.json",{checks:terminal_checks}.to_json()) return
 }
 fs.write("terminal-ready.json",{task:terminal_task}.to_json())
 start_timeout(0.1,||terminal_wait())
}
fn terminal_wait(){let path="terminal-continue-"+terminal_task+".json" if fs.exists(path){let advanced="terminal-advanced-"+terminal_task+".json" if fs.exists(advanced){return} fs.write(advanced,"{}") if terminal_task==1 {fs.write("local-error-state.json",{complete:generated_render_complete area_visible:ui.generated_area.visible() text_visible:ui.final_answer.visible() error:interface_error mailbox:ui.generated.mailbox.text() seen:mailbox_seen}.to_json()) terminal_checks.push({name:"成功稿后局部回调错误不切文字兜底" passed:generated_render_complete && ui.generated_area.visible() && !ui.final_answer.visible() && interface_error!=""})} start_task() start_timeout(0.2,||terminal_observe())} else {start_timeout(0.1,||terminal_wait())}}
fn terminal_start(){if fs.exists("terminal-start.json"){if fs.exists("terminal-claimed.json"){return} fs.write("terminal-claimed.json","{}") start_task() start_timeout(0.2,||terminal_observe())} else {start_timeout(0.1,||terminal_start())}}
start_timeout(1,||terminal_start())
'''

TRACE_FIXTURE=r'''
let trace_fixture_started=false
let trace_failure_started=false
fn trace_bulk(offset){
 for i in 20 {trace_emit("burst",{ordinal:offset+i},nil)}
 if offset+20<300 {start_timeout(0.03,||trace_bulk(offset+20))}
 else {trace_emit("segment_rotation",{text:read_text("trace-large.txt")},nil) start_timeout(0.05,||trace_emit("segment_rotation",{text:read_text("trace-large.txt")},nil))}
}
fn trace_failure_completion(token){
 if token==run_id && !agent_active {fs.write("trace-failure-complete.json",{run:token phase:phase calls:agent_call_index}.to_json())}
 else {start_timeout(0.1,||trace_failure_completion(token))}
}
fn trace_fixture(){
 if trace_fixture_started {return} trace_fixture_started=true
 start_task()
 let probe={text:"didi-fixture-secret trace-map-secret" value:"before"}
 trace_emit("snapshot_probe",probe,nil) probe.value="after" start_timeout(0.1,||trace_bulk(0))
}
fn smoke_request(task,input,schema,token,record,done){
 request_stage(record,"entry")
 let body={model:"MiniMax-M3" messages:input tools:schema tool_choice:"auto"}
 let serialized=body.to_json()
 trace_emit("model_request",{step:record.step body:serialized},nil)
 let message={role:"assistant" content:"本次合成模型已完成"}
 if record.step==1 {message.tool_calls=[smoke_call("location-trace","read_location",{}) smoke_call("skill-trace","read_skill",{name:"native_ui"}) smoke_call("render-trace","render_ui",{source:"trace_result := Label{text:\"开发记录验证，实际原生界面\"}"})]}
 let response={model:"MiniMax-M3" choices:[{message:message finish_reason:"stop"}]}
 trace_emit("model_response",{step:record.step status:200 body:response.to_json()},nil)
 start_timeout(0.01,||{if current_task(token){done(response)}})
}
fn smoke_call(id,name,args){return {id:id type:"function" function:{name:name arguments:args.to_json()}}}
fn trace_fixture_poll(){
 if read_text("trace-go.json")!=nil {trace_fixture()}
 if trace_state!=nil && !trace_failure_started && read_text("trace-fail-"+trace_state.instance+".json")!=nil {trace_failure_started=true trace_state.segment_bytes=1048576 trace_emit("write_failure_probe",{},nil) start_task() let token=run_id start_timeout(0.1,||trace_failure_completion(token))}
 start_timeout(0.1,||trace_fixture_poll())
}
start_timeout(0.2,||trace_fixture_poll())
'''

MIXED_FIXTURE=r'''
let mixed_done=false
fn agent_pump(token){
 if mixed_done {return} mixed_done=true agent_active=false phase="waiting"
 let complete=candidates[candidates.len()-1]
 let first=route_prefixes["prefix-1-0"] let second=route_prefixes["prefix-2-0"] let final=route_prefixes["prefix-3-0"]
 let leg=final.legs[2]
 let walking_variant=complete.to_json().parse_json() walking_variant.legs[1].mode="walk"
 let priced=route_quote_variant(complete,{ref:"quote:test" price_cents:900},final.legs[0].id,"合成同地点估价关联；不同坐标不认证").candidate
 let unknown={id:"unknown" to_ref:leg.to_ref actual_origin:leg.actual_origin actual_endpoint:leg.actual_endpoint request_bound:true origin_complete:true endpoint_complete:true price_cents:nil duration_seconds:leg.duration_seconds departure_ts:leg.departure_ts source_ts:leg.source_ts waiting_included:false segments:leg.segments}
 let partial=route_prefix_extend(second,unknown,"unknown",arrive_by,5000).prefix
 let broken={id:"broken" to_ref:leg.to_ref actual_origin:"115,24" actual_endpoint:leg.actual_endpoint request_bound:true origin_complete:true endpoint_complete:true price_cents:1200 duration_seconds:300 departure_ts:leg.departure_ts source_ts:leg.source_ts waiting_included:false segments:leg.segments}
 let disconnected=route_prefix_extend(second,broken,"broken",arrive_by,5000)
 let budget=route_prefix_extend(second,leg,"over",arrive_by,2000).prefix
 let late=route_prefix_extend(second,leg,"late",time_now()-1,5000).prefix
 let map_cold=route_map_metadata(complete) let map_cache_before=route_get(complete,"map_geometry_cache")
 let old_directory=map_path_catalog(candidates[1]) let extended_cold=route_map_metadata(complete)
 let quote_cold=route_map_metadata(priced) let new_directory=map_path_catalog(complete)
 let quoted_directory=map_path_catalog(priced) let quoted_facts=interface_route_facts(priced,route_recheck(priced,time_now(),arrive_by,5000))
 fs.write("harness-smoke.json",{checks:[
 {name:"未读地图目录不是零且不构造几何" passed:map_cold.catalog_status=="not_loaded" && map_cold.path_count==nil && map_cache_before==nil && map_cold.max_paths_per_image==4}
 {name:"extend新几何不能沿用旧Route目录" passed:route_map_metadata(candidates[1]).catalog_status=="ready" && extended_cold.catalog_status=="not_loaded" && extended_cold.path_count==nil}
 {name:"报价派生复用同源目录并保当前Route身份" passed:quote_cold.catalog_status=="not_loaded" && quoted_directory==new_directory && quoted_facts.id==priced.id && quoted_facts.map_paths==new_directory && quoted_facts.map_metadata.catalog_status=="ready" && quoted_facts.map_metadata.path_count==new_directory.len()}
 {name:"公交前后局部打车组成三完整leg" passed:final.legs.len()==3 && final.legs[0].mode=="taxi" && final.legs[1].mode=="transit" && final.legs[2].mode=="taxi"}
 {name:"Route展示交通方式来自实际legs" passed:interface_route_facts(walking_variant,route_recheck(walking_variant,time_now(),arrive_by,5000)).kind_label=="打车＋步行" && interface_route_facts(complete,route_recheck(complete,time_now(),arrive_by,5000)).kind_label=="打车＋公共交通"}
 {name:"每笔完整估价仅相加一次" passed:complete.price_cents==3000 && first.price_cents==1200 && second.price_cents==1800 && final.known_cost_cents==3000}
 {name:"出租车候车未知与价格可比较分离" passed:final.budget_status=="within_estimate" && final.deadline_status=="unknown" && final.waiting_slack_seconds>0 && !complete.feasible}
 {name:"未知报价不是零且保留已知小计" passed:partial.price_cents==nil && partial.known_cost_cents==1800 && partial.budget_status=="unknown"}
 {name:"断开实际几何拒绝拼接" passed:!disconnected.success}
 {name:"超预算与过期限可独立证明" passed:budget.budget_status=="over_budget" && late.deadline_status=="over_deadline"}
 {name:"原prefix不被后续扩展重算/重复收费" passed:second.legs.len()==2 && second.price_cents==1800}
 {name:"OD出租车真实polyline末端与报价保留" passed:route_candidates(nil,mixed_driving("114,22","114.03,22"),time_now(),arrive_by,5000,time_now())[0].endpoint_complete}
 {name:"供应商报价替换一leg且派生总价不叠加/不改原prefix" passed:priced.price_cents==2700 && final.price_cents==3000 && priced.legs[0].price_cents==900 && priced.legs[0].provider_connection_status=="unknown" && route_prefix_facts(second).completion_status=="incomplete" && route_prefix_facts(second).full_journey_price_cents==nil}
 {name:"已知站点与公交时刻进入真实工具参数" passed:mixed_params.search("&date=")>=0 && mixed_params.search("&time=")>=0 && route_nodes["stop:a"]!=nil}
 ]}.to_json())
 render_content()
}
let mixed_params=""
fn mixed_driving(from,to){return {status:"1" route:{origin:from destination:to taxi_cost:"12" paths:[{cost:{duration:"300"} steps:[{polyline:from+";"+to}]}]}}}
fn amap_request(path,params,token,done){
 let from=params.split("&origin=")[1].split("&")[0] let to=params.split("&destination=")[1].split("&")[0]
 let data=mixed_driving(from,to)
 if path=="/v5/direction/transit/integrated" {mixed_params=params data={status:"1" route:{origin:from destination:to transits:[{cost:{duration:"900" transit_fee:"6"} segments:[{walking:{steps:[{polyline:from+";"+to}]}}]}]}}}
 start_timeout(0.01,||done(data))
}
start_timeout(1,||{
 run_id+=1 received_at=time_now() arrive_by=received_at+2400 user_limits={minutes:40 budget_cents:5000} constraints={budget_cents:5000}
 let city={city:"fixture" citycode:"0755" adcode:"440306" currency:"CNY"}
 position_record={name:"fixture origin" source:"mock" mock:true coordinate_system:"GCJ-02" longitude:114 latitude:22 city:"fixture" citycode:"0755" adcode:"440306" currency:"CNY" sampled_at_unix:received_at}
 destination_record={name:"fixture destination" source:"mock" longitude:114.03 latitude:22 city:"fixture" citycode:"0755" adcode:"440306" currency:"CNY"}
 register_route_node("stop:a","fixture station A","114.01,22","mock",city)
 register_route_node("stop:b","fixture station B","114.02,22","mock",city)
 agent_active=true phase="running" agent_calls=[
 {id:"mixed-taxi-a" function:{name:"extend_route" arguments:{route_id:"origin" to_ref:"stop:a" mode:"taxi"}.to_json()}}
 {id:"mixed-transit" function:{name:"extend_route" arguments:{route_id:"route_"+run_id+"_1" to_ref:"stop:b" mode:"transit" strategy:0}.to_json()}}
 {id:"mixed-taxi-b" function:{name:"extend_route" arguments:{route_id:"route_"+run_id+"_2" to_ref:"destination" mode:"taxi"}.to_json()}}
 ] agent_call_index=0 agent_execute_next(run_id)
})
'''

LATE_FIXTURE=r'''
let late_started=false let late_checks=[] let late_point=nil let late_token=-1
fn agent_tool_result(result){
 if active_tool!=nil && active_tool.function.name=="render_ui" {late_point={diagnostics:result.diagnostics notified:generated_render_notified complete:generated_render_complete}}
 product_agent_tool_result(result)
}
fn agent_pump(token){agent_active=false phase="waiting" answer_text="迟到渲染前的文字兜底" render_content()}
fn late_after(){
 late_checks.push({name:"诊断点通知未到不误锁存" passed:late_point.diagnostics=="" && !late_point.notified && !late_point.complete})
 late_checks.push({name:"终端后真实迟通知恢复原生单一结果" passed:!agent_active && generated_render_complete && generated_render_notified && ui.generated_area.visible() && !ui.final_answer.visible() && ui.generated.find("kept").text()=="Late native result"})
 fs.write("late-ready.json",{stage:1}.to_json())
}
fn late_wrong(){
 late_checks.push({name:"成功后局部错误不清成功锁存" passed:generated_render_complete && ui.generated_area.visible() && !ui.final_answer.visible() && interface_error!=""})
 // 故意排队旧同run通知，然后换稿，验证现有generation隔离。
 let token=run_id let generation=map_generation
 enqueue_generated_line(0,"{\"action\":\"rendered\"}",0,token,generation)
 interface_revision+=1 mount_interface("View{show_bg:true draw_bg:{color:#xff0000} Label{text:\"Invalid draw type\"}}",token,interface_revision)
 answer_text="首次执行失败的文字兜底" render_content()
 start_timeout(0.03,||{late_checks.push({name:"同run已排队旧通知不能误锁新稿" passed:!generated_render_notified && !generated_render_complete})})
 start_timeout(1.0,||{
   late_checks.push({name:"新稿实际类型错误不成功且文字兜底" passed:!generated_render_complete && ui.generated.diagnostics()!="" && !ui.generated_area.visible() && ui.final_answer.visible()})
   fs.write("harness-smoke.json",{checks:late_checks final:{complete:generated_render_complete notified:generated_render_notified diagnostic:ui.generated.diagnostics() error:interface_error area_visible:ui.generated_area.visible() final_visible:ui.final_answer.visible() answer:answer_text}}.to_json()) fs.write("late-ready.json",{stage:2}.to_json())
 })
}
fn late_tick(){
 let identity=ui.trace_identity.text().parse_json()
 if trace_state==nil || identity.instance!=trace_state.instance {start_timeout(0.1,||late_tick()) return}
 if !late_started && fs.exists("late-start.json") {
  late_started=true run_id+=1 late_token=run_id agent_active=true phase="running" received_at=time_now()
  agent_messages=[{role:"user" content:"合成迟通知测试"}]
  agent_calls=[{id:"late-render" function:{name:"render_ui" arguments:{source:"kept := Label{text:\"Late native result\"} Button{text:\"Local operation error\" on_click: || emit({action:\"runtime_error\" message:\"Local operation failed\"})}"}.to_json()}}]
  agent_call_index=0 start_timeout(0.01,||agent_execute_next(late_token)) start_timeout(1.2,||late_after())
 }
 if fs.exists("late-next.json") && !fs.exists("late-claimed.json") {fs.write("late-claimed.json","{}") late_wrong()}
 start_timeout(0.1,||late_tick())
}
start_timeout(0.2,||late_tick())
'''

PERFORMANCE_FIXTURE=r'''
let performance_started=false let performance_finished=false let performance_writes=0 let performance_checks=[]
let performance_old_messages=[] let performance_new_body_bytes=0 let performance_old_body_bytes=0
let performance_origins=false let performance_snapshot_bytes=0
let performance_detail=false let performance_graph=false let performance_render=false let performance_calls=0 let performance_round=0
fn performance_set_facts(text){performance_writes+=1 ui.generated.fact_state.set_text(text)}
fn performance_call(id,name,args){return {id:id type:"function" function:{name:name arguments:args.to_json()}}}
fn agent_tool_result(result){
 if active_tool!=nil {
  let name=active_tool.function.name
  let legacy=result
  if name=="query_route" {let origin=false let destination=false for node in result.new_nodes {if node.ref=="origin" {origin=true} if node.ref=="destination" {destination=true}} performance_origins=origin && destination legacy={success:true facts:performance_legacy_facts() records:[]}}
  elif name=="compare_routes" {legacy={success:true comparison:comparison_summary() mixed_attempts:route_graph_facts().prefixes queried_transit_count:transit_count queried_driving:driving_done facts:performance_legacy_facts()}}
  elif name=="render_ui" {legacy={success:result.success diagnostics:result.diagnostics viewport:result.viewport facts:performance_legacy_facts()} performance_render=result.success}
  elif name=="get_route" {performance_detail=result.success && result.route.segments.len()>0 && result.route.price_cents==1200}
  elif name=="get_route_graph" {performance_graph=result.success && result.graph.nodes.len()>=75}
  performance_old_messages.push({role:"tool" tool_call_id:active_tool.id content:legacy.to_json()})
  performance_calls+=1
 }
 product_agent_tool_result(result)
}
fn amap_request(path,params,token,done){
 let data={status:"1" route:{origin:"114,22" destination:"114.03,22" taxi_cost:"12" paths:[{cost:{duration:"300"} steps:[{polyline:"114,22;114.03,22"}]}]}}
 start_timeout(0.01,||done(data))
}
fn agent_pump(token){
 if !performance_started {return}
 agent_active=false phase="waiting" answer_text="" render_content()
 let body={model:"MiniMax-M3" messages:agent_messages tools:agent_tools()}
 let oldbody={model:"MiniMax-M3" messages:performance_old_messages tools:agent_tools()}
 performance_new_body_bytes=body.to_json().to_bytes().len() performance_old_body_bytes=oldbody.to_json().to_bytes().len()
 performance_checks.push({name:"同业务记录工具消息减少且保持按需详情" passed:performance_new_body_bytes<performance_old_body_bytes && performance_calls==5 && performance_detail && performance_graph && performance_render})
 performance_checks.push({name:"增量交通结果保留实际起终点图节点" passed:performance_origins})
 performance_snapshot_bytes=ui.generated.fact_state.text().to_bytes().len()
 performance_checks.push({name:"所有候选和原生地图几何仍可取得" passed:candidates.len()==7 && map_geometry(candidates[0]).paths.len()==20 && ui.generated.fact_state.text().parse_json().routes.len()==7})
 start_timeout(0.3,||performance_refresh())
}
fn performance_refresh(){
 let before=performance_writes
 for i in 100 {refresh_generated_facts()}
 performance_checks.push({name:"无状态变化重复刷新不写完整facts" passed:performance_writes==before})
 ui_facts_revision+=1 refresh_generated_facts()
 performance_checks.push({name:"实际状态修订仍更新完整snapshot" passed:performance_writes==before+1 && ui.generated.fact_revision.text()==""+ui_facts_revision})
 start_timeout(0.1,||performance_repeat())
}
fn performance_repeat(){
 performance_round+=1 ui_facts_revision+=1 refresh_generated_facts()
 for i in 20 {render_content() refresh_generated_facts()}
 if performance_round<30 {start_timeout(0.05,||performance_repeat()) return}
 performance_checks.push({name:"30轮完整snapshot刷新保留真实详情与空诊断" passed:ui.generated.diagnostics()=="" && ui.generated.fact_state.text().parse_json().routes.len()==7 && generated_render_complete})
 start_timeout(0.2,||{
  let oldrun=run_id
  picker_pois=[{id:"old-place" name:"old fixture"}] picker_preview_poi=picker_pois[0] picker_status="old status"
  ui.sentence.set_text("40分钟内到机场，预算50元")
  start_task()
  start_timeout(0.05,||{
   performance_checks.push({name:"独立新查询没有旧地点/旧工具或稿参数" passed:run_id>oldrun && picker_pois.len()==0 && picker_preview_poi==nil && picker_status=="" && agent_calls.len()==0 && active_tool==nil && agent_call_index==0})
   fs.write("harness-smoke.json",{checks:performance_checks old_body_bytes:performance_old_body_bytes new_body_bytes:performance_new_body_bytes rounds:performance_round fact_writes:performance_writes snapshot_bytes:performance_snapshot_bytes}.to_json())
  })
 })
}
fn agent_begin(){
 if performance_started && performance_finished {agent_active=false phase="waiting" return}
}
fn performance_seed(){
 performance_started=true run_id+=1 agent_active=true phase="running" received_at=time_now() arrive_by=received_at+2400
 user_limits={minutes:40 budget_cents:5000} constraints={budget_cents:5000}
 position_record={name:"synthetic origin" source:"fixture" mock:true coordinate_system:"GCJ-02" longitude:114 latitude:22 city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY" sampled_at_unix:received_at}
 destination_record={name:"synthetic destination" source:"fixture" longitude:114.03 latitude:22 city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}
 route_nodes={} route_prefixes={} candidates=[] source_records=[] source_snapshots=[]
 for i in 75 {register_route_node("fixture-node-"+i,"公开合成站点"+i,"114,22","fixture",nil)}
 for i in 6 {
  let segments=[]
  for j in 20 {segments.push({road:"合成完整路段：换乘入口、票价来源和候车未知需要保留；"+j distance:"1000" duration:"300" polyline:"114,22;114.03,22"})}
  let candidate=route_candidate("perf-"+i,"taxi",300,1200,received_at,received_at,"114.03,22","114.03,22",false,segments)
  candidate.request_bound=true candidate.origin_complete=true
  candidates.push(candidate)
 }
 agent_messages=[{role:"system" content:"synthetic same-record performance comparison"} {role:"user" content:({request:"公开合成查询" facts:{position:position_record destination:destination_record}}).to_json()}]
 performance_old_messages=[agent_messages[0] agent_messages[1]]
 agent_calls=[performance_call("perf-drive","query_route",{mode:"taxi"}) performance_call("perf-compare","compare_routes",{}) performance_call("perf-detail","get_route",{id:"perf-0"}) performance_call("perf-graph","get_route_graph",{}) performance_call("perf-render","render_ui",{source:"result := Label{text:\"Performance result: complete local details\"} Button{text:\"Open detail\" on_click:||emit({action:\"view_route\" id:\"perf-0\"})}"})]
 let assistant={role:"assistant" content:nil tool_calls:agent_calls}
 agent_messages.push(assistant) performance_old_messages.push(assistant) agent_call_index=0
 agent_execute_next(run_id)
 performance_finished=true
}
fn performance_tick(){
 let identity=nil try {identity=ui.trace_identity.text().parse_json()} {}
 if trace_state!=nil && identity!=nil && identity.instance==trace_state.instance && fs.exists("performance-go.json") && !performance_started {performance_seed()}
 if !performance_started {start_timeout(0.1,||performance_tick())}
}
start_timeout(1,||performance_tick())
'''

SKILLS_FIXTURE = r'''
fn agent_pump(token){}
fn skills_tick(){
 if !fs.exists("skills-go.json") {start_timeout(0.1,||skills_tick()) return}
 agent_begin()
 let checks=[]
 let catalog=agent_skill_catalog()
 checks.push({name:"七个技能从frontmatter曝光" passed:catalog.len()==7})
 let prompt=agent_messages[0].content
 let metadata_ok=true
 for skill in catalog {if prompt.split(skill.name).len()<2 || prompt.split(skill.description).len()<2 {metadata_ok=false}}
 checks.push({name:"首次模型消息包含所有名称与描述" passed:metadata_ok})
 let entry=read_agent_skill({name:"native-ui"})
 checks.push({name:"默认读取完整SKILL.md" passed:entry.success && entry.path=="SKILL.md" && entry.content==read_text("skills/native-ui/SKILL.md")})
 checks.push({name:"技能正文不提前进入模型上下文" passed:prompt.split(entry.content).len()==1})
 let host=read_agent_skill({name:"native-ui" path:"references/host-interface.md"})
 checks.push({name:"按需读取完整宿主引用" passed:host.success && host.content==read_text("skills/native-ui/references/host-interface.md")})
 let upstream=read_agent_skill({name:"makepad-2-0-splash" path:"UPSTREAM.md"})
 checks.push({name:"上游正文按需读取" passed:upstream.success && upstream.content.len()>10000})
 let reference=read_agent_skill({name:"makepad-2-0-layout" path:"references/layout-patterns.md"})
 checks.push({name:"按需读取上游嵌套引用" passed:reference.success && reference.content==read_text("skills/makepad-2-0-layout/references/layout-patterns.md")})
 let legacy=read_agent_skill({name:"native_ui"})
 checks.push({name:"旧工具调用名称兼容" passed:legacy.success && legacy.content==entry.content})
 let missing=read_agent_skill({name:"native-ui" path:"absent.md"})
 checks.push({name:"不存在的引用返回实际资源目录" passed:!missing.success && missing.files.len()>0})
 fs.write("harness-smoke.json",({checks:checks}).to_json())
}
start_timeout(1,||skills_tick())
'''

CONTRACT_FIXTURE=r'''
let contract_started=false
let contract_stage=0
let contract_results=[]
let contract_params=[]
let contract_checks=[]
let contract_geometry_reads=0
let contract_partial=nil let contract_quote_id="" let contract_schema=nil
fn contract_check(name,passed){contract_checks.push({name:name passed:passed})}
fn contract_call(id,name,p){return {id:id type:"function" function:{name:name arguments:p.to_json()}}}
fn contract_start(calls){agent_calls=calls agent_call_index=0 agent_active=true phase="running" start_timeout(0.01,||agent_execute_next(run_id))}
fn map_geometry_uncached(candidate){contract_geometry_reads+=1 return product_map_geometry_uncached(candidate)}
fn load_map_slot(slot){slot.state="ready" slot.status="SYNTHETIC MAP BINDING" slot.target_id=map_candidate(slot.target).id}
fn amap_request(path,params,token,done){
 contract_params.push({path:path params:params})
 let from=coord_text(position_record) let to=coord_text(destination_record)
 let data={status:"1" route:{origin:from destination:to taxi_cost:"32" paths:[{distance:"12345" cost:{duration:"900"} steps:[{instruction:"沿合成道路前行" road:"Synthetic Road" distance:"12345" cost:{duration:"900"} polyline:from+";"+to}]}]}}
 if path=="/v5/direction/transit/integrated" {data={status:"1" route:{origin:from destination:to transits:[{distance:"15000" cost:{duration:"1200" transit_fee:if params.search("&strategy=8")>=0 {nil} else {"4"}} segments:[{walking:{distance:"15000" cost:{duration:"1200"} steps:[{instruction:"合成步行接驳" polyline:from+";"+to}]}}]}]}}}
 start_timeout(0.01,||done(data))
}
fn agent_tool_result(result){contract_results.push({name:active_tool.function.name result:result}) product_agent_tool_result(result)}
fn agent_begin(){}
fn agent_pump(token){
 if contract_stage==1 {
  contract_stage=2
  let ids=[] let unique=true
  for c in candidates {for id in ids {if id==c.id {unique=false}} ids.push(c.id)}
  contract_check("同一assistant批次查询候选ID与跨轮几何引用唯一",unique && candidates.len()==4 && candidates[0].geometry_ref!=candidates[1].geometry_ref && candidates[0].id.search("route_"+run_id+"_")==0)
  let a=contract_results[0].result.routes[0] let taxi=contract_results[2].result.routes[0] let unknown=contract_results[3].result.routes[0]
  contract_check("统一query保真实距离费用分段及未知候车",a.distance_m==15000 && a.cost.amount_cents==400 && a.steps.len()==1 && taxi.distance_m==12345 && taxi.cost.amount_cents==3200 && !taxi.assessment.waiting_included && taxi.cost.basis!="" && a.duration_label==duration_text(a.duration_seconds) && a.price_label==money_text(a.cost.amount_cents) && taxi.duration_label==duration_text(taxi.duration_seconds))
  contract_check("未知报价不变零且保不成立依据",unknown.cost.amount_cents==nil && !unknown.assessment.passed && unknown.assessment.reasons.len()>0)
  let over={} for key value in candidates[0] {over[key]=value} over.price_cents=10000 over.known_cost_cents=10000
  let independent=query_route_summary(over).assessment
  let late_route={} for key value in candidates[0] {late_route[key]=value} late_route.duration_seconds=4000
  let late_assessment=query_route_summary(late_route).assessment
  contract_check("预算与期限各自判断，不因超预算改变已知时间结论",independent.budget_status=="over_budget" && independent.deadline_status=="within_estimate" && !independent.passed && late_assessment.budget_status=="within_estimate" && late_assessment.deadline_status=="over_deadline")
  contract_check("策略默认0与显式策略走原供应商接口",contract_params[0].params.search("&strategy=0")>=0 && contract_params[1].params.search("&strategy=1")>=0 && contract_params[2].path=="/v5/direction/driving" && contract_params[2].params.search("&strategy=0")>=0)
  contract_check("查询未提前扫描几何，polyline引用不含坐标",contract_geometry_reads==0 && route_get(candidates[0],"map_geometry_cache")==nil && ui_route(a.geometry_ref)==candidates[0])
  let geometry=map_geometry(ui_route(a.geometry_ref)) let again=map_geometry(ui_route(a.id))
  contract_check("路线ID与polyline引用复用同一惰性缓存",contract_geometry_reads==1 && geometry.paths.to_json()==again.paths.to_json())
  contract_schema=agent_tools()
  let schema_description=contract_schema[0].function.description contract_schema[0].function.description="SAME RUN PROBE"
  contract_check("同run工具schema按同一对象复用",agent_tools()[0].function.description=="SAME RUN PROBE")
  contract_schema[0].function.description=schema_description
  let names=[] let no_visible=true for t in agent_tools() {names.push(t.function.name) if is_render_tool(t.function.name) && t.function.name!="render_ui" && route_get(t.function.parameters.properties,"visible")!=nil {no_visible=false}}
  contract_check("只曝光统一query及五渲染入口与通用入口",names.to_json().search("query_route")>=0 && names.to_json().search("query_transit")==-1 && names.to_json().search("query_driving")==-1 && no_visible && model_task_context().providers.didi.configured && model_task_context().to_json().search("didi-fixture-secret")==-1)
  let from=coord_text(position_record) let to=coord_text(destination_record)
  let partial_data={status:"1" route:{origin:from destination:to taxi_cost:"32" paths:[{distance:"12000" cost:{duration:"900"} steps:[{polyline:from+";114.025,22"}]}]}}
  add_candidates(nil,partial_data,time_now(),time_now(),"query_driving") contract_partial=candidates[candidates.len()-1]
  let ext_leg=extension_legs(partial_data,"taxi",route_nodes["origin"],route_nodes["destination"],time_now(),time_now())[0]
  let ext=route_prefix_extend(route_prefixes["origin"],ext_leg,"partial-test",arrive_by,5000)
  let partial_facts=query_route_summary(contract_partial)
  contract_check("相同偏离终点的直查与扩展均未完成且小计不冒全价",partial_facts.completion_status=="incomplete" && ext.success && route_prefix_facts(ext.prefix).completion_status=="incomplete" && partial_facts.cost.amount_cents==3200 && partial_facts.cost.full_journey_amount_cents==nil && partial_facts.price_label.search("已查段")>=0)
  let quote={ref:"didi-quote:fixture" price_cents:2300 from:{city:"fixture"} to:{city:"fixture"}}
  didi_quotes[quote.ref]=quote
  let bad=route_quote_variant(candidates[0],quote,candidates[0].legs[0].id,"合成地点关联")
  contract_check("公交完整供应商报价leg不可按taxi step替换",!bad.success && candidates[0].legs.len()==1 && candidates[0].price_cents==400)
  contract_quote_id="route_"+run_id+"_"+(candidate_sequence+1)
  contract_start([
   contract_call("attach-direct","attach_quote",{route_id:contract_partial.id leg_id:contract_partial.legs[0].id quote_ref:quote.ref place_basis:"合成同城同名地点；不同供应商连接未认证"})
   contract_call("read-old","get_route",{id:contract_partial.id})
   contract_call("read-new","get_route",{id:contract_quote_id})
   contract_call("routes","render_routes",{source:"entry := TextInput{text:\"Initial\"} open := Button{text:\"查看合成详情\" on_click:||{show_block(\"one-detail\") emit({action:\"view_route\" id:snapshot().routes[5].id})}}"})
   contract_call("detail","render_route_detail",{id:"one-detail" visible:true source:"let route_id=facts.routes[5].id let bound=false on_facts_changed=fn(current){if current.viewed_route_id==route_id && !bound {bound=true emit({action:\"map\" widget:\"preview\" target:current.routes[5].geometry_ref interactive:true})}} View{width:Fill height:Fit flow:Down Label{text:\"合成详情独立地图引用\"} preview := AutoNaviMapView{width:Fill height:100 on_camera_changed:fn(lon,lat,zoom,width,height,request){emit({action:\"map_camera\" widget:\"preview\" center_lon:lon center_lat:lat zoom:zoom width:width height:height request:request})}} Button{text:\"返回合成列表\" on_click:||hide_self()}}"})
   contract_call("summary","render_summary",{visible:false source:"Label{text:\"合成总结\"}"})
   contract_call("explanation","render_explanation",{source:"Label{text:\"合成解释\"}"})
   contract_call("suggestions","render_suggestions",{source:"Label{text:\"合成建议\"}"})
   contract_call("additional","render_ui",{blocks:[{id:"additional" source:"Label{text:\"任意额外区块\"}"}]})
  ])
 } elif contract_stage==2 {
  contract_stage=3
  let attached=nil let old=nil let newer=nil
  for item in contract_results {if item.name=="attach_quote" {attached=item.result} elif item.name=="get_route" {if item.result.route.id==contract_partial.id {old=item.result.route} else {newer=item.result.route}}}
  let derived=ui_route(contract_quote_id)
  contract_check("直查32附价23派生新ID且原值不变，读回身份费用一致",attached.success && attached.route.id==contract_quote_id && attached.route.derived_from_route_id==contract_partial.id && old.cost.amount_cents==3200 && newer.cost.amount_cents==2300 && newer.cost.full_journey_amount_cents==nil && newer.completion_status=="incomplete" && newer.duration_seconds==old.duration_seconds && newer.assessment.connection_status=="provider_connection_unknown" && !newer.assessment.passed)
  let reads=contract_geometry_reads
  contract_check("报价派生保实际几何并共享cache，不重扫折线",map_geometry(derived).paths.to_json()==map_geometry(contract_partial).paths.to_json() && contract_geometry_reads==reads && ui_route(newer.geometry_ref).id==newer.id)
  let step_description=contract_partial.steps_cache[0].description contract_partial.steps_cache[0].description="IMMUTABLE STEP PROBE"
  contract_check("不可变步骤缓存派生共享且当前评估仍重算",query_route_summary(derived).steps[0].description=="IMMUTABLE STEP PROBE" && query_route_summary(derived).assessment.evaluated_at>=newer.assessment.evaluated_at)
  contract_partial.steps_cache[0].description=step_description
  for i in 3 {
   let large={} for key value in contract_partial {large[key]=value} assign_candidate_ref(large) large.geometry_owner_id=contract_partial.id large.steps_cache=nil large.segments=[]
   for n in 20 {large.segments.push({road:"Synthetic Road" distance:"100" cost:{duration:"10"} polyline:"114,22;114.025,22"})}
   route_summary_steps(large) candidates.push(large)
  }
  let large_facts=interface_facts() let step_count=0 for item in large_facts.routes {step_count+=item.steps.len()}
  contract_check("实际9Route66steps规模快照只保一份路线且读取不重解析",large_facts.routes.len()==9 && step_count==66 && large_facts.route_graph.route_ids.len()==9 && route_get(large_facts.route_graph,"routes")==nil && large_facts.routes[5].steps[0].description==step_description)

  block_by_id("routes").handle.find("entry").set_text("LOCAL KEPT")
  contract_start([contract_call("cross-entry","render_route_detail",{id:"additional" visible:false source:"Label{text:\"已有普通块跨入口更新\"}"}) contract_call("replace","render_summary",{source:"Label{text:\"仅替换总结\"}"}) contract_call("bad","render_explanation",{source:"View{draw_bg:{color:#xff0000} Label{text:\"BAD\"}}"}) contract_call("repair","render_explanation",{source:"Label{text:\"已修正解释\"}"})])
 } elif contract_stage==3 {
  contract_stage=4 agent_active=false phase="waiting"
  let bad=nil let fixed=nil for item in contract_results {if item.name=="render_explanation" {if !item.result.success {bad=item.result} else {fixed=item.result}}}
  contract_check("不同渲染入口替换保留列表输入及独立详情",block_by_id("routes").revision==1 && block_by_id("routes").handle.find("entry").text()=="LOCAL KEPT" && block_by_id("summary").revision==2 && block_by_id("one-detail").overlay && !block_by_id("one-detail").visible && !block_by_id("additional").overlay && block_by_id("additional").visible && map_slots[block_map_key("one-detail","preview")]==nil)
  contract_check("失败块返回真实诊断并可原入口修正",bad!=nil && bad.blocks[0].diagnostics!="" && fixed!=nil && fixed.success && block_by_id("explanation").complete)
  fs.write("contract-ready.json","{}")
 }
}
fn contract_tick(){
 let identity=ui.trace_identity.text().parse_json()
 if trace_state==nil || identity.instance!=trace_state.instance {start_timeout(0.1,||contract_tick()) return}
 if !contract_started && fs.exists("contract-go.json") {
  contract_started=true contract_stage=1 run_id+=1 received_at=time_now() arrive_by=received_at+2400 user_limits={minutes:40 budget_cents:5000} constraints={budget_cents:5000}
  position_record={name:"Synthetic origin" source:"synthetic-fixture" mock:true longitude:114 latitude:22 city:"fixture" citycode:"0755" adcode:"440306" currency:"CNY" sampled_at_unix:received_at}
  destination_record={name:"Synthetic destination" source:"synthetic-fixture" longitude:114.03 latitude:22 city:"fixture" citycode:"0755" adcode:"440306" currency:"CNY"}
  contract_start([contract_call("t0","query_route",{mode:"transit"}) contract_call("t1","query_route",{mode:"transit" strategy:1}) contract_call("taxi","query_route",{mode:"taxi"}) contract_call("unknown","query_route",{mode:"transit" strategy:8})])
 }
 if contract_stage==4 && fs.exists("contract-clicked.json") {
  contract_stage=5
  let slot=map_slots[block_map_key("one-detail","preview")]
  contract_check("真实按钮跨入口详情与runtime几何引用对应同候选",block_by_id("one-detail").container.visible() && viewed_route_id==contract_quote_id && slot!=nil && slot.target==ui_route(contract_quote_id).geometry_ref && slot.target_id==contract_quote_id)
  fs.write("contract-click-checked.json","{}")
 }
 if contract_stage==5 && fs.exists("contract-returned.json") {
  contract_stage=6
  contract_check("返回保留原列表本地输入",!block_by_id("one-detail").container.visible() && block_by_id("routes").handle.find("entry").text()=="LOCAL KEPT")
  let old=candidates[0].geometry_ref ui.sentence.set_text("40分钟内到机场，预算50") start_task()
  let schema_cleared=agent_tool_schema==nil contract_schema[0].function.description="OLD RUN PROBE"
  contract_check("新run清除schema并重建本次对象",schema_cleared && agent_tools()[0].function.description!="OLD RUN PROBE")
  start_timeout(0.05,||{contract_check("新查询清空候选引用与所有渲染区块",ui_route(old)==nil && candidates.len()==0 && candidate_sequence==0 && ui_blocks.len()==0) agent_active=false phase="waiting" fs.write("harness-smoke.json",{checks:contract_checks}.to_json())})
  return
 }
 start_timeout(0.1,||contract_tick())
}
start_timeout(1,||contract_tick())
'''

def main():
 if '--loop-settle-private-replay' in sys.argv:assert '--loop-settle' in sys.argv, 'private replay is an explicit modifier of --loop-settle'
 sp=importlib.util.spec_from_file_location('agent',ROOT/'tools/agent.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
 (ROOT/'build/smoke').mkdir(exist_ok=True,parents=True);w=Path(tempfile.mkdtemp(prefix='navigation-harness-',dir=ROOT/'build/smoke'))
 a.STATE=w/'private-state';a.HOME_DIR=a.STATE/'home';a.CORE=a.STATE/'core';a.SESSION=a.STATE/'session.json'
 for p in [a.STATE,a.HOME_DIR,a.CORE]:p.mkdir(parents=True,exist_ok=True)
 original=(ROOT/'bundle/main.splash').read_text();recovery='--render-recovery' in sys.argv;source=original.replace('fn minimax_request(','fn product_minimax_request(',1).replace('minimax_request("",agent_messages','smoke_request("",agent_messages')+'\n'+FIXTURE
 if '--tool-contract' in sys.argv:source=original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_begin(','fn product_agent_begin(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1).replace('fn amap_request(','fn product_amap_request(',1).replace('fn map_geometry_uncached(','fn product_map_geometry_uncached(',1).replace('fn load_map_slot(','fn product_load_map_slot(',1)+'\n'+CONTRACT_FIXTURE
 if '--skills' in sys.argv:source=original.replace('fn agent_pump(','fn product_agent_pump(',1)+'\n'+SKILLS_FIXTURE
 if '--trace' in sys.argv:source=original.replace('fn minimax_request(','fn product_minimax_request(',1).replace('minimax_request("",agent_messages','smoke_request("",agent_messages')+'\n'+TRACE_FIXTURE
 if '--mixed-routing' in sys.argv:source=original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn amap_request(','fn product_amap_request(',1)+'\n'+MIXED_FIXTURE
 if '--loop-settle' in sys.argv:source=original.replace('fn minimax_request(','fn product_minimax_request(',1).replace('fn map_geometry_uncached(','fn product_map_geometry_uncached(',1).replace('fn trace_emit_run(','fn product_trace_emit_run(',1).replace('fn refresh_generated_facts(','fn product_refresh_generated_facts(',1)+'\n'+LOOP_SETTLE_FIXTURE
 if '--ui-blocks' in sys.argv:source=original.replace('fn load_map_slot(','fn product_load_map_slot(',1)+'\n'+UI_BLOCKS_FIXTURE
 if '--map-sections' in sys.argv:source=original.replace('fn fit_map_slot(','fn product_fit_map_slot(',1).replace('fn load_map_slot(','fn product_load_map_slot(',1)+'\n'+MAP_SECTIONS_FIXTURE
 if '--map-details' in sys.argv:source=original.replace('fn load_map_slot(','fn product_load_map_slot(',1)+'\n'+MAP_FIXTURE
 if '--terminal-content' in sys.argv:source=original.replace('fn minimax_request(','fn product_minimax_request(',1)+'\n'+TERMINAL_FIXTURE
 if '--late-render' in sys.argv:
  context=original[original.index('fn generated_context(){'):original.index('fn mount_interface(')]
  assert context.count('start_timeout(0.02, || {')==1, '初次generated context timer必须唯一'
  delayed=context.replace('start_timeout(0.02, || {','start_timeout(0.75, || {',1)
  source=original.replace(context,delayed,1).replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1)+'\n'+LATE_FIXTURE
 if '--performance' in sys.argv:
  legacy=subprocess.check_output(['git','show','015a81b:bundle/main.splash'],cwd=ROOT).decode()
  legacy=legacy[legacy.index('fn interface_facts(){'):legacy.index('fn generated_context(){')].replace('fn interface_facts(){','fn performance_legacy_facts(){',1)
  source=original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1).replace('fn agent_begin(','fn product_agent_begin(',1).replace('fn amap_request(','fn product_amap_request(',1).replace('ui.generated.fact_state.set_text(', 'performance_set_facts(')+'\n'+legacy+'\n'+PERFORMANCE_FIXTURE
 if recovery:source=original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1)+'\n'+RECOVERY_FIXTURE
 if '--guardian' in sys.argv:
  import test_goal_guardian as guardian
  source=guardian.source(original)
 env=a.host_env(True);process=None;port=None
 def q(route,**args):
  if route in ('k','m','t','click'):
   until=time.monotonic()+10
   while not json.loads(urlopen(f'http://127.0.0.1:{port}/s',timeout=15).read()).get('w'):
    assert time.monotonic()<until,'宿主窗口尚未创建；不派发输入'
    time.sleep(.1)
  return urlopen(f'http://127.0.0.1:{port}/'+route+('?' + urlencode(args) if args else ''),timeout=15).read()
 def stop():
  nonlocal process
  if process and process.poll() is None:
   try:q('quit')
   except OSError:pass
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
  process=None
 def launch(tag):
  nonlocal process,port
  log=w/(tag+'.log')
  with log.open('wb') as f:process=subprocess.Popen([str(a.BINARY),'--remote','--test-action','launch-agentic26-navigation'],cwd=a.STATE,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(200):
   m=re.search(rb'\[makepad-remote\] listening on 127\.0\.0\.1:(\d+)',log.read_bytes())
   if m:port=int(m[1]);return
   assert process.poll() is None,str(log);time.sleep(.1)
  raise RuntimeError('隔离宿主未启动')
 try:
  launch('mount');paths=[]
  for _ in range(100):
   paths=list((a.HOME_DIR/'apps/.system/os.agentic26-navigation').glob('*/main.splash'))
   if paths:break
   time.sleep(.1)
  assert len(paths)==1;mount=paths[0].parent;stop();shutil.copytree(ROOT/'bundle',mount,dirs_exist_ok=True)
  manifest=json.loads((mount/'manifest.json').read_text());manifest['id']='os.agentic26-navigation';(mount/'manifest.json').write_text(json.dumps(manifest));(mount/'main.splash').write_text(source)
  subprocess.run([str(ROOT.parent/'.octosense-agentic26/OctoSense-App-Hub/target/release/hub'),'stamp',str(mount)],stdout=subprocess.DEVNULL,check=True)
  a.init_demo();jail=a.jail_path();a.materialize_skills(ROOT/'bundle',jail);(jail/'private-config.json').write_text('{"location_mode":"demo"}');(jail/'trip.json').write_text('historical fixture ignored');(jail/'agent-run.json').write_text('historical audit ignored')
  if '--guardian' in sys.argv or '--tool-contract' in sys.argv or '--trace' in sys.argv or '--late-render' in sys.argv or '--performance' in sys.argv or '--ui-blocks' in sys.argv or '--map-sections' in sys.argv or '--loop-settle' in sys.argv:(jail/'private-config.json').write_text(json.dumps({'location_mode':'demo','development_trace':True,'development_trace_session':'0123456789abcdef0123456789abcdef','minimax_api_key':'didi-fixture-secret','amap_api_key':'trace-map-secret','didi_mcp_key':'didi-fixture-secret'}))
  if '--guardian' in sys.argv or '--tool-contract' in sys.argv or '--trace' in sys.argv or '--late-render' in sys.argv or '--performance' in sys.argv or '--ui-blocks' in sys.argv or '--map-sections' in sys.argv or '--loop-settle' in sys.argv:
   d=jail/'dev-trace/0123456789abcdef0123456789abcdef';d.mkdir(parents=True);(d/'instance-counter.json').write_text('{"next":1}');(jail/'trace-large.txt').write_text('中'*180000)
  launch('native');report=None
  if '--guardian' in sys.argv:
   guardian.run(w,jail,q,stop,launch,original,source)
   return
  if '--tool-contract' in sys.argv:
   time.sleep(3)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(1)
   (jail/'contract-go.json').write_text('{}')
   def contract_wait(name):
    for _ in range(250):
     if (jail/name).exists():return
     time.sleep(.1)
    raise RuntimeError('contract fixture missing '+name+'; '+str(w/'native.log'))
   contract_wait('contract-ready.json')
   (w/'contract-list.png').write_bytes(q('g',raw=1))
   def contract_click(text):
    rows=json.loads(q('snap'))['s'];row=next(x for x in rows if x.get('t')==text);r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1);time.sleep(.4)
   contract_click('查看合成详情');(jail/'contract-clicked.json').write_text('{}');contract_wait('contract-click-checked.json')
   (w/'contract-detail.png').write_bytes(q('g',raw=1))
   contract_click('返回合成列表');(jail/'contract-returned.json').write_text('{}');contract_wait('harness-smoke.json')
   report=json.loads((jail/'harness-smoke.json').read_text())
   report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),mode='Android',no_external_services=True,model_called=False,synthetic_routes=True,synthetic_map_binding=True)
   (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
   assert all(row['passed'] for row in report['checks']),report
   print('PASS: '+str(len(report['checks']))+'项统一工具与引用原生检查；'+str(w/'report.json'));return
  if '--skills' in sys.argv:
   time.sleep(3)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(1)
   (jail/'skills-go.json').write_text('{}')
   for _ in range(100):
    if (jail/'harness-smoke.json').exists():break
    time.sleep(.1)
   report=json.loads((jail/'harness-smoke.json').read_text())
   assert all(row['passed'] for row in report['checks']),report
   report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),mode='Android',agent_external_requests=False,model_called=False)
   (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
   print('PASS: '+str(len(report['checks']))+'项技能原生检查；'+str(w/'report.json'));return
  if '--loop-settle' in sys.argv:
   if '--loop-settle-private-replay' in sys.argv:
    from urllib.parse import parse_qs
    raw=ROOT/'build/research/map-20003/trace-private.jsonl'
    maps=[json.loads(json.loads(l)['data']) for l in raw.read_text().splitlines() if json.loads(l)['event']=='map_request']
    paths=[]
    for item in maps:
     rows=parse_qs(item['params'].lstrip('&')).get('paths',[''])[0].split('|')
     found=[line.split(':',1)[1] for line in rows if ':' in line]
     if sum(len(line.split(';')) for line in found)==657:paths=found;break
    assert paths,'explicit private replay requires existing657point geometry; no service fallback'
    source_geometry='existing private map-20003 taxi request; not the entire failed run1'
   else:
    paths=[';'.join(f'{110+part*.1+point*.00001:.5f},{21+part*.1+point*.00001:.5f}' for point in range(219)) for part in range(3)]
    source_geometry='public synthetic three disconnected paths with219points each; no private artifact read'
   a.write_private(jail/'settle-geometry.json',json.dumps({'paths':paths,'endpoint':paths[-1].split(';')[-1],'source_geometry':source_geometry}).encode())
  if '--ui-blocks' in sys.argv or '--map-sections' in sys.argv or '--loop-settle' in sys.argv:
   import zlib,struct
   def png(color):
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    scan=(b'\0'+bytes(color)*372)*160
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',372,160,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')
   (jail/'part-a.png').write_bytes(png((50,130,190)));(jail/'part-b.png').write_bytes(png((190,130,50)))
   time.sleep(3)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(1)
   (jail/('loop-settle-go.json' if '--loop-settle' in sys.argv else 'sections-go.json')).write_text('{}')
  if '--ui-blocks' in sys.argv:
   def wait_file(name):
    for _ in range(100):
     if (jail/name).exists():return
     time.sleep(.1)
    raise AssertionError(name+' missing; '+str(w/'native.log'))
   def click_text(text,contains=False):
    rows=json.loads(q('snap'))['s']
    row=next(v for v in rows if v['ty']=='Button' and (text in v.get('t','') if contains else v.get('t')==text) and v['r'][3]>0)
    r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
   wait_file('blocks-ready.json')
   if '--ui-block-geometry' in sys.argv:(jail/'blocks-geometry-only.json').write_text('{}')
   q('m',k='scroll',x=220,y=600,dy=300,precise=1,wait=1);time.sleep(.3)
   before=json.loads(q('snap'))['s'];(w/'blocks-list.png').write_bytes(q('g',raw=1))
   kept={v.get('t'):v['r'] for v in before if v.get('t','').startswith('查看方案') and v['r'][3]>0}
   click_text('查看方案',True);time.sleep(.5);(jail/'blocks-opened.json').write_text('{}');wait_file('blocks-open-checked.json')
   opened=json.loads(q('snap'))['s']
   shell=next(v for v in opened if v.get('i')=='sentence');control=next(v for v in opened if v['ty']=='Button' and v.get('t')=='查询')
   back=next(v for v in opened if v.get('t')=='返回列表')
   assert shell['r'][3]>0 and control['r'][3]>0 and back['r'][1]>=control['r'][1]+control['r'][3],(shell,control,back)
   (w/'blocks-detail-snap.json').write_text(json.dumps(opened,ensure_ascii=False))
   (w/'blocks-detail.png').write_bytes(q('g',raw=1))
   q('m',k='scroll',x=220,y=600,dy=2000,precise=1,wait=1);time.sleep(.3)
   assert any('详情第23段' in v.get('t','') for v in json.loads(q('snap'))['s'])
   bottom=json.loads(q('snap'))['s'];bottom_shell=next(v for v in bottom if v.get('i')=='sentence');bottom_control=next(v for v in bottom if v['ty']=='Button' and v.get('t')=='查询')
   assert bottom_shell['r']==shell['r'] and bottom_control['r']==control['r'],(shell,control,bottom_shell,bottom_control)
   (w/'blocks-detail-bottom-snap.json').write_text(json.dumps(bottom,ensure_ascii=False))
   (w/'blocks-detail-bottom.png').write_bytes(q('g',raw=1))
   q('m',k='scroll',x=220,y=300,dy=-2000,precise=1,wait=1);time.sleep(.3)
   click_text('返回列表');time.sleep(.3)
   after=json.loads(q('snap'))['s'];returned={v.get('t'):v['r'] for v in after if v.get('t','').startswith('查看方案') and v['r'][3]>0}
   assert kept==returned,(kept,returned)
   (w/'blocks-returned.png').write_bytes(q('g',raw=1));(jail/'blocks-returned.json').write_text('{}')
   if '--ui-block-geometry' not in sys.argv:
    wait_file('blocks-repaired.json');(w/'blocks-repaired.png').write_bytes(q('g',raw=1));(jail/'blocks-finish.json').write_text('{}')
  if '--performance' in sys.argv:
   time.sleep(3)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(1)
   (jail/'performance-go.json').write_text('{}')
  if '--trace' in sys.argv:
   time.sleep(2)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(1)
   (jail/'trace-go.json').write_text('{}')
   sessions=jail/'dev-trace/0123456789abcdef0123456789abcdef'
   for _ in range(150):
    records=[json.loads(line) for x in sessions.glob('vm-*/segment-*.jsonl') if x.is_file() for line in x.read_text().splitlines()]
    if any(x['event']=='query_ended' for x in records) and sum(x['event']=='burst' for x in records)>=300 and sum(x['event']=='segment_rotation' for x in records)>=2:break
    time.sleep(.1)
   assert records and any(x['event']=='query_ended' for x in records),str(w/'native.log')
   instances=sorted(x.name for x in sessions.glob('vm-*') if x.is_dir())
   assert len(instances)>=2,instances
   (w/'trace-tree.txt').write_bytes(q('d'));(w/'trace-snap-all.json').write_bytes(q('snap',all=1))
   rows=json.loads(q('snap',q='trace_identity'))['s'];markers=[json.loads(x['t']) for x in rows if x.get('i')=='trace_identity' and x.get('t')]
   assert len(markers)==1,markers
   current=markers[0]['instance']
   for _ in range(100):
    events=sorted((json.loads(line) for x in (sessions/current).glob('segment-*.jsonl') if x.is_file() for line in x.read_text().splitlines()),key=lambda x:x['seq'])
    if any(x['event']=='query_ended' for x in events):break
    time.sleep(.1)
   time.sleep(.3)
   events=sorted((json.loads(line) for x in (sessions/current).glob('segment-*.jsonl') if x.is_file() for line in x.read_text().splitlines()),key=lambda x:x['seq'])
   # Effective-visible marker identifies the currently drawn Android root.
   assert len({x['seq'] for x in events})==len(events)
   bodies=[json.loads(json.loads(x['data'])['body']) for x in events if x['event']=='model_request']
   calls=[x for x in events if x['event']=='tool_call'];results=[x for x in events if x['event']=='tool_result']
   assert bodies and bodies[0]['messages'][1]['content']
   assert {x['call_id'] for x in calls}=={'location-trace','skill-trace','render-trace'}=={x['call_id'] for x in results}
   assert any(x['event']=='render_result' for x in events)
   probe=next(json.loads(x['data']) for x in events if x['event']=='snapshot_probe');assert probe['value']=='before' and probe['text']=='[REDACTED] [REDACTED]'
   a.SESSION.write_text(json.dumps({'pid':process.pid,'process_stamp':a.process_stamp(process.pid),'port':port,'trace_session':'0123456789abcdef0123456789abcdef','log':str(w/'native.log')}))
   selected=a.read_trace();assert selected[1]==current
   for file in list(sessions.rglob('*.json'))+list(sessions.rglob('*.jsonl')):
    assert 'didi-fixture-secret' not in file.read_text() and 'trace-map-secret' not in file.read_text()
   last=events[-1]['seq'];run=events[-1]['run']
   segments=list((sessions/current).glob('segment-*.jsonl'));assert len(segments)>=2 and all(x.stat().st_size<=1048576 for x in segments)
   assert sum(x['event']=='burst' for x in events)>=300
   # 静态技能资料独立增长；这里核验的是动态 trace 分段避免逐事件文件膨胀。
   assert len(list(sessions.rglob('*')))<40
   status=json.loads((sessions/current/'status.json').read_text());(sessions/current/f'segment-{status["segments"]+1:06}.jsonl').mkdir()
   (jail/('trace-fail-'+current+'.json')).write_text('{}')
   for _ in range(100):
    status=json.loads((sessions/current/'status.json').read_text())
    rows=json.loads(q('snap',q='trace_identity'))['s']
    marked=json.loads(next(x['t'] for x in rows if x.get('i')=='trace_identity'))
    if status['state']=='incomplete' and marked['run']>run:
     if (jail/'trace-failure-complete.json').exists():break
    time.sleep(.1)
   assert status['state']=='incomplete' and marked['state']=='incomplete'
   assert json.loads((jail/'trace-failure-complete.json').read_text())['phase']=='waiting'
   (w/'trace-android.png').write_bytes(q('g',raw=1))
   stop();before=sorted(str(x.relative_to(sessions)) for x in sessions.rglob('*'))
   (jail/'private-config.json').write_text('{"location_mode":"demo"}')
   launch('trace-off');time.sleep(3)
   assert sorted(str(x.relative_to(sessions)) for x in sessions.rglob('*'))==before
   assert not any(x.get('i')=='trace_identity' for x in json.loads(q('snap',q='trace_identity'))['s'])
   assert any(x.get('t')=='开发记录验证，实际原生界面' for x in json.loads(q('snap'))['s'])
   assert 'script time budget exceeded' not in (w/'native.log').read_text()+(w/'trace-off.log').read_text()
   report={'checks':9,'instances':instances,'selected_current_instance':current,'events':len(events),'mode':'Android','synthetic_model':True,'real_native_controls':True,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'path':str(sessions),'limits':'No real HTTP/provider request; synthetic response uses actual harness/render hooks.'}
   (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: trace '+str(w/'report.json'));return
  if '--late-render' in sys.argv:
   time.sleep(5)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);time.sleep(.8);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(1)
   (jail/'late-start.json').write_text('{}')
   for _ in range(70):
    if (jail/'late-ready.json').exists():break
    time.sleep(.1)
   assert json.loads((jail/'late-ready.json').read_text())['stage']==1
   rows=json.loads(q('snap'))['s'];(w/'late-snapshot.json').write_text(json.dumps(rows));assert any(x.get('t')=='Late native result' and x['r'][3]>0 for x in rows)
   (w/'late-success.png').write_bytes(q('g',raw=1))
   r=next(x['r'] for x in rows if x.get('t')=='Local operation error');q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1);time.sleep(.3)
   (w/'late-local-error.png').write_bytes(q('g',raw=1));(jail/'late-next.json').write_text('{}')
   for _ in range(70):
    if (jail/'harness-smoke.json').exists():break
    time.sleep(.1)
   report=json.loads((jail/'harness-smoke.json').read_text());assert all(x['passed'] for x in report['checks']),report
   (w/'late-first-error.png').write_bytes(q('g',raw=1))
   report.update(mode='Android',product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),synthetic_model=True,real_native_controls=True)
   (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: late render '+str(w/'report.json'));return
  if '--terminal-content' in sys.argv:
   time.sleep(3)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(2)
   (jail/'terminal-start.json').write_text('{}')
   for task in (1,2,3):
    ready=None
    for _ in range(150):
     rows=json.loads(q('snap'))['s']
     if task==1:
      local=[v for v in rows if v.get('t')=='改变本地状态']
      if local:
       r=local[0]['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
     try:ready=json.loads((jail/'terminal-ready.json').read_text())
     except (FileNotFoundError,json.JSONDecodeError):pass
     if ready and ready['task']==task:break
     time.sleep(.1)
    assert ready and ready['task']==task
    q('m',k='scroll',x=220,y=600,dy=-12000,precise=1,wait=1);time.sleep(.3)
    rows=json.loads(q('snap'))['s']
    if task==1:
     assert any(v.get('i')=='kept' and v['r'][3]>0 for v in rows)
    (w/('single-result-'+str(task)+'.png')).write_bytes(q('g',raw=1))
    if task==3:assert any('生成执行失败，本次文字结果仍可查看'==v.get('t') for v in rows)
    (w/('single-result-'+str(task)+'.png')).write_bytes(q('g',raw=1))
    if task==1:
     row=next(v for v in rows if v.get('t')=='触发局部错误');r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1);time.sleep(.4)
     rows=json.loads(q('snap'))['s'];assert any(v.get('i')=='kept' and v['r'][3]>0 for v in rows)
     (w/'single-result-local-error.png').write_bytes(q('g',raw=1))
    if task==2:
     q('m',k='scroll',x=220,y=600,dy=8000,precise=1,wait=1);time.sleep(.5)
     assert any('```splash' in v.get('t','') for v in json.loads(q('snap'))['s'])
     (w/'single-result-fallback-bottom.png').write_bytes(q('g',raw=1))
    (jail/('terminal-continue-'+str(task)+'.json')).write_text('{}')

  for _ in range(150):
   try:report=json.loads((jail/'harness-smoke.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError):pass
   if report:break
   time.sleep(.1)
  assert report,'宿主未完成工具会话；查看 '+str(w/'native.log')
  assert all(row['passed'] for row in report['checks']),report
  if recovery or '--loop-settle' in sys.argv or '--ui-blocks' in sys.argv or '--map-sections' in sys.argv or '--map-details' in sys.argv or '--terminal-content' in sys.argv or '--mixed-routing' in sys.argv or '--performance' in sys.argv:
   report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),synthetic_model=True,real_native_controls=True,mode='Android' if '--terminal-content' in sys.argv or '--performance' in sys.argv or '--ui-blocks' in sys.argv or '--map-sections' in sys.argv or '--loop-settle' in sys.argv else 'desktop')
   if '--loop-settle' in sys.argv:
    (w/'loop-settle-android.png').write_bytes(q('g',raw=1))
    report.update(no_external_services=True,expected_injected_errors=['diagnostic side entry unavailable','facts side entry unavailable'])
   if '--ui-blocks' in sys.argv:report.update(no_external_services=True,synthetic_image_bytes=True,list_scroll_preserved=True,synthetic_model=False,model_called=False,tool_result_boundary=True)
   if '--ui-block-geometry' in sys.argv:
    report['checks'] += [{'name':'打开overlay位于查询按钮下且输入可见','passed':True},{'name':'详情滚到底后输入查询rect保持不变','passed':True},{'name':'返回原列表实际可见按钮rect保持不变','passed':True}]
    report['geometry']={'sentence':shell['r'],'query':control['r'],'back':back['r'],'bottom_sentence':bottom_shell['r'],'bottom_query':bottom_control['r']}
    report['tool_result_boundary']=False
   if '--map-sections' in sys.argv:
    (w/'map-sections-android.png').write_bytes(q('g',raw=1))
    report.update(no_external_services=True,synthetic_image_bytes=True)
   if '--performance' in sys.argv:
    native_errors=[line for line in (w/'native.log').read_text().splitlines() if '[E]' in line or 'heap allocation limit exceeded' in line or 'script time budget exceeded' in line]
    assert not native_errors, '性能fixture原生错误，详见私有native.log'
    report.update(native_errors=0,scope='Same synthetic business records with legacy full-snapshot tool results vs actual new branch results; real native snapshot/30 update rounds. Bytes measured, tokens not measured. No external service requests.')
   (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: '+str(len(report['checks']))+'项定向原生检查；'+str(w/'report.json'));return
  time.sleep(3)
  q('k',c='Space',cmd=1,wait=1)
  for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
  q('k',c='enter',wait=1);time.sleep(1)
  q('m',k='down',x=200,y=300,wait=1)
  for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
  q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(2)
  rows=json.loads(q('snap'))['s'];(w/'before-safe.json').write_text(json.dumps(rows,ensure_ascii=False));(w/'before.png').write_bytes(q('g',raw=1));wrap=next(row for row in rows if row.get('i')=='wrap');assert wrap['r'][3]>60,wrap['r']
  q('m',k='scroll',x=260,y=600,dy=1500,precise=1,wait=1);time.sleep(.5);rows=json.loads(q('snap'))['s'];(w/'after-safe.json').write_text(json.dumps(rows,ensure_ascii=False));(w/'after.png').write_bytes(q('g',raw=1));assert any('第19行' in row.get('t','') for row in rows),'底部结果未能滚动到达'
  def click_shell(text):
   row=next(v for v in json.loads(q('snap'))['s'] if v['ty']=='Button' and v.get('t')==text);r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
  click_shell('查询');time.sleep(.1);click_shell('终止');time.sleep(.9)
  report=json.loads((jail/'harness-smoke.json').read_text());assert report['phase']=='cancelled',report
  row=next(v for v in json.loads(q('snap'))['s'] if v['ty']=='TextInput' and v.get('i')=='sentence');r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
  for _ in range(len(row.get('t',''))+3):q('k',c='Backspace',wait=1);q('k',c='Delete',wait=1)
  q('t',t='30分钟内到机场，预算80元',wait=1);click_shell('查询')
  for _ in range(60):
   report=json.loads((jail/'harness-smoke.json').read_text())
   if report['queries']>=3 and len(report['checks'])==7:break
   time.sleep(.1)
  assert len(report['checks'])==7 and all(row['passed'] for row in report['checks']),report
  report['checks'] += [{'name':'Android长文字自然换行','passed':True},{'name':'Android内容可滚到最后一行','passed':True}]
  report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),synthetic_model=True,real_native_controls=True)
  (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: 9无状态查询/Android布局检查；'+str(w/'report.json'))
 finally:stop()
if __name__=='__main__':main()
