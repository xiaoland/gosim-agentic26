"""Independent source reads and current-run POI adoption, without services."""
import hashlib,json,time
FIXTURE=r'''
fn agent_pump(token){}
let source_checks=[] let source_results=[] let source_stage=0
fn agent_tool_result(result){source_results.push(result) product_agent_tool_result(result)}
fn source_check(name,value){source_checks.push({name:name passed:value error:constraint_error})}
fn agent_begin(){}
fn source_run(){
 run_id+=1 agent_active=true trip_replay=false guardian_mode=false received_at=time_now() user_limits=nil constraints=nil arrive_by=nil
 calendar_tool() notes_tool() position_tool()
 source_check("模拟日历与笔记独立读取不设置约束",calendar_events.len()>0 && note_records.len()>0 && constraints==nil && arrive_by==nil)
 position_record.currency="CNY" position_record.city="深圳市" position_record.citycode="0755" position_record.adcode="440306"
 source_check("设置约束不裁决机票机场文字",set_constraints({arrive_within_minutes:40 budget_cents:5000 currency:"CNY" basis:"用户时限预算；地域人民币"}) && arrive_by==received_at+2400)
 poi_records=[{id:"test-airport" source:"amap-poi" longitude:113.81 latitude:22.62 coordinate_system:"GCJ-02" name:"深圳宝安机场T3国内出发" address:"深圳宝安机场入口" queried_at:time_now() city_metadata:{city:"深圳市" citycode:"0755" adcode:"440306" currency:"CNY"}}]
 register_route_pois(poi_records)
 agent_calls=[{id:"actual-poi" function:{name:"adopt_destination" arguments:{poi_id:"test-airport" basis:"模型按本轮地点资料采用；不依赖机场文字完全一致"}.to_json()}}] agent_call_index=0
 agent_schedule_next(run_id) start_timeout(0.1,||source_after_adopt())
}
fn source_after_adopt(){
 if active_tool!=nil {start_timeout(0.1,||source_after_adopt()) return}
 source_check("本轮真实POI采用一次成功且保约束",source_results.len()==1 && source_results[0].success && destination_record.id=="test-airport" && constraints.budget_cents==5000 && arrive_by==received_at+2400)
 fs.write("harness-smoke.json",{checks:source_checks}.to_json())
}
start_timeout(1,||source_run())
'''

def source(original):
    fixture=FIXTURE
    globals_lines=[line for line in fixture.splitlines() if line.startswith('let ')]
    for line in globals_lines:fixture=fixture.replace(line+'\n','')
    for name in ['agent_pump','agent_tool_result','agent_begin']:
        start=fixture.index('fn '+name+'(')
        end=fixture.index('\n',start)
        definition=fixture[start:end].strip()
        fixture=fixture[:start]+fixture[end:]
        original=original.replace('fn '+name+'(',definition+'\nfn product_'+name+'(',1)
    return '\n'.join(globals_lines)+'\n'+original+'\n'+fixture

def run(w,jail,original,injected):
    report=None
    for _ in range(150):
        try:report=json.loads((jail/'harness-smoke.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):pass
        if report:break
        time.sleep(.1)
    assert report,'source contract replay did not finish; '+str(w/'native.log')
    errors=[line for line in (w/'native.log').read_text().splitlines() if '[E]' in line]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,no_external_services=True,native_errors=errors,boundary='本次变更的真实demo背景文件独立读取、通用setter及已有POI经生产dispatcher采用回执；不重跑旧多trip/IO协议证据。')
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not errors,errors
    assert all(x['passed'] for x in report['checks']),report
    print('PASS: '+str(len(report['checks']))+'项来源原生检查；'+str(w/'report.json'))
