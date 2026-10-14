"""通用约束设置的生产启动、工具边界与守护锁定；零模型/供应商请求。"""
import hashlib,json,time
FIXTURE=r'''
fn trace_initialize(){}
let ct_now=1791954000 let ct_mode="live" let ct_stage=0 let ct_checks=[] let ct_results=[] let ct_begins=0 let ct_dispatches=0 let ct_provider_calls=0 let ct_calendar_range=nil let ct_guardian=false let ct_saved=nil
fn time_now(){return ct_now}
fn location_mode(){return ct_mode}
fn trip_load(done){}
fn render_content(){}
fn guardian_refresh(){}
fn refresh_generated_facts(){}
fn interface_facts(){return {routes:[] limits:user_limits arrive_by:arrive_by}}
fn trip_begin(text,done){ct_begins+=1 done(true)}
fn amap_request(path,params,token,done){ct_provider_calls+=1}
fn context_calendar_read(start,end,limit,done){ct_calendar_range={start:start end:end} done({success:true records:[]})}
fn ct_check(name,passed){ct_checks.push({name:name passed:passed}) fs.write("constraints-progress.json",{stage:ct_stage checks:ct_checks}.to_json())}
fn ct_params(){return {arrive_within_minutes:120 budget_cents:10000 currency:"CNY" basis:"用户两小时与一百元；广州地点资料按人民币计价，币种为地域推断"}}
fn ct_call(name,p){let call={id:"constraints-"+ct_stage function:{name:name arguments:p.to_json()}} agent_calls=[call] agent_call_index=0 active_tool=nil agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] agent_schedule_next(run_id)}
fn agent_tool_result(result){ct_results.push(result) product_agent_tool_result(result)}
fn agent_begin(){ct_dispatches+=1
 if ct_guardian {
  ct_check("守护重核沿用已确认期限剩余预算且不新建trip",guardian_mode && arrive_by==ct_saved.deadline_ts && constraints.budget_cents==8000 && constraints.currency=="CNY" && constraints.guardian_locked && ct_begins==1)
  let prior=constraints.to_json()
  ct_check("函数级setter与地点采用拒绝改锁定目标",!set_constraints(ct_params()) && !select_destination({poi_id:"ct-airport"},"另一地点") && constraints.to_json()==prior && arrive_by==ct_saved.deadline_ts)
  ct_stage=7 ct_call("set_constraints",ct_params()) return
 }
 let initial=model_task_context()
 ct_check("自然中文数字输入正常启动且首context未猜约束",ct_begins==1 && ct_dispatches==1 && request_text=="从这里两小时内到白云机场，不超过一百，尽量便宜" && initial.limits==nil && initial.arrive_by==nil && initial.arrive_by_label==nil && initial.received_at==rail_time("2026-10-14","13:00") && initial.received_at_label=="2026-10-14 13:00（北京时间）" && initial.timezone=="Asia/Shanghai")
 ct_now+=180 ct_stage=0 ct_call("read_calendar",{})
}
fn agent_pump(token){let result=ct_results[ct_results.len()-1]
 if ct_stage==0 {
  ct_check("无约束可独立读取日历且默认窗不是零期限",result.success && ct_calendar_range.start==received_at*1000 && ct_calendar_range.end==(received_at+86400)*1000 && constraints==nil && arrive_by==nil)
  ct_stage=1 ct_call("query_route",{mode:"transit"})
 } elif ct_stage==1 {
  let proposal=guardian_propose({route_id:"not-yet-created" preferences:"" risk_acceptance:"" basis:"缺约束"})
  ct_check("交通与提案缺期限明确失败且不请求供应商",!result.success && result.error.search("到达期限")>=0 && !proposal.success && guardian_pending==nil && ct_provider_calls==0)
  ct_stage=2 ct_call("set_constraints",ct_params())
 } elif ct_stage==2 {
  ct_check("13点接收13点03设置120分钟仍是15点100元",result.success && arrive_by==rail_time("2026-10-14","15:00") && constraints.budget_cents==10000 && constraints.currency=="CNY" && constraints.basis==ct_params().basis && result.arrive_by==arrive_by)
  ct_mode="demo" agent_tool_schema=nil let demo=false for spec in agent_tools(){if spec.function.name=="set_constraints" {demo=true}}
  ct_mode="live" agent_tool_schema=nil let live=false for spec in agent_tools(){if spec.function.name=="set_constraints" {live=true}}
  ct_check("demo与live共有setter且不要求日历笔记关联",demo && live && calendar_events.len()==0 && note_records.len()==0)
  ct_stage=3 ct_call("adopt_destination",{poi_id:"ct-airport" basis:"本轮高德机场POI；入口范围保持公开事实"})
 } elif ct_stage==3 {
  ct_check("先约束后采用地点不改期限预算或要求起点",result.success && position_record==nil && destination_record.id=="ct-airport" && destination_record.selection_basis!="" && arrive_by==rail_time("2026-10-14","15:00") && constraints.budget_cents==10000)
  let before=constraints.to_json() let deadline=arrive_by
  let rejected=true
  for p in [{arrive_within_minutes:1.5 budget_cents:10000 currency:"CNY" basis:"小数分钟"} {arrive_within_minutes:120 budget_cents:-1 currency:"CNY" basis:"负预算"} {arrive_within_minutes:120 budget_cents:1.5 currency:"CNY" basis:"亚分预算"} {arrive_within_minutes:9007199254740991 budget_cents:10000 currency:"CNY" basis:"溢出时限"} {arrive_within_minutes:120 budget_cents:9007199254740992 currency:"CNY" basis:"溢出金额"} {arrive_within_minutes:120 budget_cents:10000 currency:"USD" basis:"无换汇"} {arrive_within_minutes:120 date:"2026-10-14" time:"15:00" budget_cents:10000 currency:"CNY" basis:"两种时限"} {date:"2026-02-29" time:"15:00" budget_cents:10000 currency:"CNY" basis:"无效日期"} {date:"2026-10-14" time:"25:00" budget_cents:10000 currency:"CNY" basis:"无效时刻"} {budget_cents:10000 currency:"CNY" basis:"缺时限"} {arrive_within_minutes:120 budget_cents:10000 currency:"CNY"}] {
   if set_constraints(p) || constraint_error=="" || constraints.to_json()!=before || arrive_by!=deadline {rejected=false}
  }
  ct_check("机械数值时间币种与shape失败不改变已有约束",rejected)
  ct_check("绝对北京时间由现有helper转换且预算零合法",set_constraints({date:"2026-10-14" time:"15:00" budget_cents:0 currency:"CNY" basis:"用户今天下午三点；按接收日期解释"}) && arrive_by==deadline && constraints.budget_cents==0)
  constraints=nil user_limits=nil arrive_by=nil destination_record=nil ct_stage=4 ct_call("adopt_destination",{poi_id:"ct-airport" basis:"先采用本轮地点"})
 } elif ct_stage==4 {
  ct_check("先采用地点可成功且不创造时间预算",result.success && destination_record.id=="ct-airport" && constraints==nil && user_limits==nil && arrive_by==nil)
  ct_stage=5 ct_call("set_constraints",ct_params())
 } elif ct_stage==5 {
  ct_check("后设置约束保留已采用地点与原时间锚点",result.success && destination_record.id=="ct-airport" && arrive_by==rail_time("2026-10-14","15:00") && constraints.budget_cents==10000)
  ct_guardian=true ct_saved={deadline_ts:rail_time("2026-10-14","16:00") total_budget_cents:10000 spent_cents:2000 currency:"CNY" destination:{name:"已确认目的地"} last_check:nil}
  guardian_goal=ct_saved start_task_with("重新核验已确认出行目标",true)
 } elif ct_stage==7 {
  ct_check("工具setter拒绝修改已确认约束",!result.success && result.error.search("锁定")>=0 && arrive_by==ct_saved.deadline_ts && constraints.budget_cents==8000)
  ct_stage=8 ct_call("adopt_destination",{poi_id:"ct-airport" basis:"另选"})
 } else {
  ct_check("工具地点采用拒绝改已确认目的地",!result.success && result.error.search("锁定")>=0 && destination_record.name==ct_saved.destination.name)
  fs.write("constraints-result.json",{checks:ct_checks provider_calls:ct_provider_calls begins:ct_begins dispatches:ct_dispatches}.to_json())
 }
}
start_timeout(0.8,||{trip_loading=false trip_pending_commit=nil trip_capture_pending=nil trip_records=[] trip_selected_id=nil guardian_goal=nil guardian_mode=false
 poi_records=parse_pois({pois:[{id:"ct-airport" name:"广州白云国际机场" location:"113.299,23.392" typecode:"150104" cityname:"广州市" citycode:"020" adcode:"440111" pname:"广东省" address:"本轮合成高德格式POI"}]},ct_now,false)
 // 生产start会清本轮POI；在首次启动hook之后注册用于两顺序判别。
 start_task_with("从这里两小时内到白云机场，不超过一百，尽量便宜",false)
 start_timeout(0.005,||{})
})
'''
# 目的地来自生产parse_pois/registry，置于本次启动之后，而不是跨run复用。
FIXTURE=FIXTURE.replace(' ct_now+=180 ct_stage=0', ' ct_now+=180 poi_records=parse_pois({pois:[{id:"ct-airport" name:"广州白云国际机场" location:"113.299,23.392" typecode:"150104" cityname:"广州市" citycode:"020" adcode:"440111" pname:"广东省" address:"本轮合成高德格式POI"}]},ct_now,false) register_route_pois(poi_records) ct_stage=0')

def source(original):
    fixture=FIXTURE
    globals_line=next(line for line in fixture.splitlines() if line.startswith('let ct_now='))
    fixture=fixture.replace(globals_line+'\n','')
    def take(name):
        nonlocal fixture
        start=fixture.index('fn '+name+'(')
        brace=fixture.index('{',start)
        depth=0;quoted=False;escaped=False
        for end in range(brace,len(fixture)):
            char=fixture[end]
            if quoted:
                if escaped:escaped=False
                elif char=='\\':escaped=True
                elif char=='"':quoted=False
            elif char=='"':quoted=True
            elif char=='{':depth+=1
            elif char=='}':
                depth-=1
                if depth==0:break
        definition=fixture[start:end+1]
        fixture=fixture[:start]+fixture[end+1:]
        return definition
    clock=take('time_now')
    for name in ['trace_initialize','trip_load','render_content','guardian_refresh','refresh_generated_facts','interface_facts','trip_begin','agent_begin','location_mode','context_calendar_read','agent_pump','agent_tool_result','amap_request']:
        definition=take(name)
        needle='fn '+name+'('
        assert original.count(needle)==1,name
        original=original.replace(needle,definition+'\nfn product_'+name+'(',1)
    return globals_line+'\n'+clock+'\n'+original+'\n'+fixture

def run(work,jail,original,injected):
    until=time.monotonic()+25
    while not (jail/'constraints-result.json').exists() and time.monotonic()<until:
        if '[E]' in (work/'native.log').read_text(errors='replace'):break
        time.sleep(.05)
    assert (jail/'constraints-result.json').exists(),work/'native.log'
    report=json.loads((jail/'constraints-result.json').read_text())
    report.update(main_sha256=hashlib.sha256(original.encode()).hexdigest(),model_requested=False,provider_requested=False,native_errors=[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],boundary='生产start_task_with/start_task_ready、model_task_context、setter、POI解析/registry/采用、标准tool dispatcher/回执和已确认goal重核。trip写盘/绘制/首次模型消费及live日历适配stub；固定13:00→13:03，不认证LLM语义、用户授权或真实交通。')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in report['checks']) and not report['native_errors'],work/'report.json'
    print(f'PASS: {len(report["checks"])}项通用约束原生检查；{work / "report.json"}')
