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
 source_records.push({id:"other-calendar" kind:"calendar" raw:"其它日历原文"}) source_records.push({id:"other-note" kind:"note" raw:"其它笔记原文"})
 source_check("引用其它event不认证所选event",!set_constraints(source_params([{source_id:"other-calendar" quote:"其它日历原文"} note])) && constraint_error.search("event_id：flight-demo")>=0)
 source_check("引用其它note不认证所选note",!set_constraints(source_params([event, {source_id:"other-note" quote:"其它笔记原文"}])) && constraint_error.search("note_id：ticket-flight-demo")>=0)
 source_check("良好原文引用采纳demo约束并保持用户金额期限",set_constraints(source_params([event note])) && constraints.event_id=="flight-demo" && constraints.note_id=="ticket-flight-demo" && constraints.budget_cents==5000 && arrive_by==received_at+2400)
 let schema=nil for tool in agent_tools() {if tool.function.name=="set_constraints" {schema=tool.function}}
 source_check("实际schema说明适用范围与各所选record原文",schema.description.search("普通已有POI")>=0 && schema.parameters.properties.citations.minItems==2 && schema.parameters.properties.citations.items.required.len()==2 && schema.parameters.properties.citations.description.search("event_id及note_id")>=0 && schema.parameters.properties.citations.items.properties.quote.description.search("单行子串")>=0)
 poi_records=[{id:"test-airport" name:"深圳宝安机场T3国内出发" address:"深圳宝安机场入口" queried_at:time_now() city_metadata:{city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}}]
 run_id+=1 agent_active=true phase="running" agent_calls=[{id:"bad-airport" function:{name:"adopt_destination" arguments:{poi_id:"test-airport" basis:"合成fixture已命名短机场；不猜同机场"}.to_json()}}] agent_call_index=0
 agent_execute_next(run_id) start_timeout(0.1,||source_after_reject())
}
fn source_after_reject(){
 if active_tool!=nil {start_timeout(0.1,||source_after_reject()) return}
 source_check("机场身份拒绝只返回一次且不采用目的地",source_results.len()==1 && !source_results[0].success && destination_record==nil && source_results[0].error.search("期望airport=深圳宝安国际机场")>=0 && source_results[0].error.search("POI id=test-airport")>=0 && source_results[0].error.search("address=深圳宝安机场入口")>=0)
 poi_records[0].name="深圳宝安国际机场T3国内出发" poi_records[0].longitude=113.81 poi_records[0].latitude=22.62 poi_records[0].coordinate_system="GCJ-02"
 source_check("完整ticket机场名仍通过身份校验",select_destination({poi_id:"test-airport"},"合成完整机场名称") && destination_record!=nil)
 fs.write("harness-smoke.json",{checks:source_checks}.to_json())
}
start_timeout(1,||source_run())
'''

def source(original):
    return original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1)+'\n'+FIXTURE

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
