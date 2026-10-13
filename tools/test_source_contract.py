"""Native source-citation and ticket-POI contract checks, without services."""
import hashlib,json,time
FIXTURE=r'''
fn agent_pump(token){}
let source_checks=[] let source_results=[] let source_stage=0
fn agent_tool_result(result){source_results.push(result) product_agent_tool_result(result)}
fn source_check(name,value){source_checks.push({name:name passed:value error:constraint_error})}
fn source_params(citations){return {event_id:"flight-demo" note_id:"ticket-flight-demo" minutes:40 budget_cents:5000 currency:"CNY" destination_query:"深圳宝安国际机场T3国内出发" citations:citations}}
fn source_run(){
 trip_new() trip_begin("40分钟内到深圳宝安机场T3，预算50元")
 received_at=time_now() user_limits={minutes:40 budget_cents:5000 currency:"unspecified"}
 calendar_tool() notes_tool() position_tool()
 position_record.currency="CNY" position_record.city="深圳市" position_record.citycode="0755" position_record.adcode="440306"
 let event={source_id:"flight-demo" quote:"SUMMARY:深圳出发航班"} let note={source_id:"ticket-flight-demo" quote:"terminal: T3"}
 source_check("少于两引用明确日历与笔记前置",!set_constraints(source_params([note])) && constraint_error.search("各一条")>=0 && constraints==nil)
 source_check("未知source_id反馈实际ID",!set_constraints(source_params([event, {source_id:"user_request" quote:"预算50元"}])) && constraint_error.search("source_id未知：user_request")>=0 && constraints==nil)
 source_check("错归quote反馈对应记录且不改变约束",!set_constraints(source_params([event, {source_id:note.source_id quote:"用户指令不存在于此raw"}])) && constraint_error.search("ticket-flight-demo 的quote不匹配")>=0 && constraints==nil)
 source_check("双笔记明确缺calendar",!set_constraints(source_params([note note])) && constraint_error.search("缺少calendar")>=0)
 source_check("双日历明确缺note",!set_constraints(source_params([event event])) && constraint_error.search("缺少note")>=0)
 source_check("跨行quote仍拒绝且指出原因",!set_constraints(source_params([event, {source_id:note.source_id quote:"terminal: T3\n---"}])) && constraint_error.search("quote跨行")>=0)
 source_records.push({id:"other-calendar" mock:true kind:"calendar" raw:"其它日历原文"}) source_records.push({id:"other-note" mock:true kind:"note" raw:"其它笔记原文"})
 source_check("引用其它event不认证所选event",!set_constraints(source_params([{source_id:"other-calendar" quote:"其它日历原文"} note])) && constraint_error.search("event_id：flight-demo")>=0)
 source_check("引用其它note不认证所选note",!set_constraints(source_params([event, {source_id:"other-note" quote:"其它笔记原文"}])) && constraint_error.search("note_id：ticket-flight-demo")>=0)
 source_check("良好原文引用采纳demo约束并保持用户金额期限",set_constraints(source_params([event note])) && constraints.event_id=="flight-demo" && constraints.note_id=="ticket-flight-demo" && constraints.budget_cents==5000 && arrive_by==received_at+2400)
 let schema=nil for tool in agent_tools() {if tool.function.name=="set_constraints" {schema=tool.function}}
 source_check("实际schema说明适用范围与各所选record原文",schema.description.search("用户明确地点")>=0 && schema.parameters.properties.citations.minItems==2 && schema.parameters.properties.citations.items.required.len()==2 && schema.parameters.properties.citations.description.search("event_id及note_id")>=0 && schema.parameters.properties.citations.items.properties.quote.description.search("单行子串")>=0)
 poi_records=[{id:"test-airport" source:"amap-poi" longitude:113.81 latitude:22.62 coordinate_system:"GCJ-02" name:"深圳宝安机场T3国内出发" address:"深圳宝安机场入口" queried_at:time_now() city_metadata:{city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}}]
 register_route_pois(poi_records)
 run_id+=1 agent_active=true phase="running" agent_calls=[{id:"bad-airport" function:{name:"adopt_destination" arguments:{poi_id:"test-airport" basis:"合成fixture已命名短机场；不猜同机场"}.to_json()}}] agent_call_index=0
 agent_schedule_next(run_id) start_timeout(0.1,||source_after_reject())
}
fn source_after_reject(){
 if active_tool!=nil {start_timeout(0.1,||source_after_reject()) return}
 source_check("机场身份拒绝只返回一次且不采用目的地",source_results.len()==1 && !source_results[0].success && destination_record==nil && source_results[0].error.search("期望airport=深圳宝安国际机场")>=0 && source_results[0].error.search("POI id=test-airport")>=0 && source_results[0].error.search("address=深圳宝安机场入口")>=0)
 poi_records[0].name="深圳宝安国际机场T3国内出发" poi_records[0].longitude=113.81 poi_records[0].latitude=22.62 poi_records[0].coordinate_system="GCJ-02"
 register_route_pois(poi_records)
 source_check("完整ticket机场名仍通过身份校验",select_destination({poi_id:"test-airport"},"合成完整机场名称") && destination_record!=nil)
 start_timeout(0.05,||source_poi_contract())
}
let source_place_count=0
fn amap_request(path,params,token,done){
 source_place_count+=1
 let id=if source_place_count==1 {"retained-airport"} else {"later-station"}
 let name=if source_place_count==1 {"深圳宝安机场T3国内出发"} else {"广州南站"}
 start_timeout(0.01,||done({status:"1" pois:[{id:id name:name location:"113.81,22.62" typecode:"150104" cityname:"深圳市" citycode:"0755" adcode:"440306" pname:"广东省" address:"来源fixture"}]}))
}
fn source_poi_contract(){
 start_task_with("240分钟内到深圳宝安机场T3，预算200元",false)
 position_record={name:"广州珠江新城" longitude:113.32 latitude:23.12 coordinate_system:"GCJ-02" source:"fixture" mock:true sampled_at_unix:time_now() city:"广州市" citycode:"020" adcode:"440106" currency:"CNY"}
 agent_calls=[{id:"retained-search" function:{name:"search_places" arguments:{query:"宝安机场"}.to_json()}} {id:"later-search" function:{name:"search_places" arguments:{query:"广州南站"}.to_json()}} {id:"retained-adopt" function:{name:"adopt_destination" arguments:{poi_id:"retained-airport" basis:"用户明确机场，实际搜索结果"}.to_json()}}]
 agent_call_index=0 source_results=[]
 start_timeout(0.05,||{agent_schedule_next(run_id) source_wait_poi()})
}
fn source_wait_poi(){
 if source_results.len()<3 {start_timeout(0.05,||source_wait_poi()) return}
 source_check("先搜目的地再搜接驳仍可采纳本query合法POI",source_results[0].success && source_results[1].success && source_results[2].success && destination_record.id=="retained-airport" && route_node("poi:retained-airport")!=nil && route_node("poi:later-station")!=nil && constraints.budget_cents==20000)
 start_timeout(0.05,||{
  start_task_with("240分钟内到另一地点，预算200元",false)
  agent_calls=[{id:"old-adopt" function:{name:"adopt_destination" arguments:{poi_id:"retained-airport" basis:"旧查询引用"}.to_json()}}] agent_call_index=0 source_results=[]
  start_timeout(0.05,||{agent_schedule_next(run_id) source_wait_old()})
 })
}
fn source_wait_old(){
 if source_results.len()<1 {start_timeout(0.05,||source_wait_old()) return}
 source_check("新query清除旧POI且拒绝混用",!source_results[0].success && destination_record==nil && route_poi("retained-airport")==nil)
 start_timeout(0.05,||source_io_observation())
}
fn source_io_observation(){
 trace_enabled=false let disabled=trace_io_begin("read","skill_resource")==nil && trace_io==nil
 trace_enabled=true trace_session="public-io-fixture"
 ui.trace_identity.set_text(trace_identity_json())
 let row=trace_io_begin("read","skill_resource")
 let before={io:trace_io}
 let active=before.io.op=="read" && before.io.path_kind=="skill_resource" && before.io.returned==false
 trace_io_end(row)
 read_text("skills/catalog.json")
 let read_marker={io:trace_io}
 let read_done=read_marker.io.op=="read" && read_marker.io.path_kind=="skill_resource" && read_marker.io.returned && read_marker.io.elapsed_seconds>=0
 trace_append_file("public-io-probe.txt","public")
 let append_marker={io:trace_io}
 trace_write_status("public-io-probe-status.json","{}")
 trace_marker() let status_marker=ui.trace_identity.text().parse_json()
 source_check("开发IO内存保真实读写阶段且仅生命周期刷新隐藏标记",disabled && active && read_done && append_marker.io.op=="append" && append_marker.io.path_kind=="trace_segment" && append_marker.io.returned && status_marker.io.op=="write" && status_marker.io.path_kind=="trace_status" && status_marker.io.returned && route_get(status_marker.io,"content")==nil && route_get(status_marker.io,"path")==nil)
 trace_enabled=false
 fs.write("harness-smoke.json",{checks:source_checks}.to_json())
}
start_timeout(1,||source_run())
'''

def source(original):
    return original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1).replace('fn amap_request(','fn product_amap_request(',1)+'\n'+FIXTURE

def run(w,jail,original,injected):
    report=None
    for _ in range(150):
        try:report=json.loads((jail/'harness-smoke.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):pass
        if report:break
        time.sleep(.1)
    assert report,'source contract replay did not finish; '+str(w/'native.log')
    errors=[line for line in (w/'native.log').read_text().splitlines() if '[E]' in line]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,no_external_services=True,native_errors=errors)
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not errors,errors
    assert all(x['passed'] for x in report['checks']),report
    print('PASS: '+str(len(report['checks']))+'项来源原生检查；'+str(w/'report.json'))
