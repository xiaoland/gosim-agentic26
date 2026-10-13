"""online12原句重复预算词、数值一致/冲突与生产启动前边界。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    text=json.loads((ROOT/'build/research/journey-guardian/current-online-12/prepare-safe.json').read_text())['input']
    (jail/'limits-input.json').write_text(json.dumps({'text':text},ensure_ascii=False))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn render_content(){}
fn guardian_refresh(){}
fn refresh_generated_facts(){return true}
fn interface_facts(){return {routes:[] limits:user_limits}}
let el_checks=[] let el_begins=0 let el_dispatches=0 let el_stage="" let el_original="" let el_goal=nil
fn el_check(name,value){el_checks.push({name:name passed:value})}
fn trip_begin(text,done){el_begins+=1 done(true)}
fn agent_begin(){
 el_dispatches+=1
 if el_stage=="normal" {
  el_check("原句生产普通启动保300分钟20000分与本次起算期限",user_limits.minutes==300 && user_limits.budget_cents==20000 && arrive_by==received_at+18000 && request_text==el_original && ui.composer_help.text().search("提交会新建")>=0)
  el_stage="guardian" el_goal={deadline_ts:time_now()+1200 total_budget_cents:20000 spent_cents:5000 currency:"CNY" destination:{name:"锁定目标"} last_check:nil}
  guardian_goal=el_goal start_task_with("重新核验已确认的出行目标",true)
 } else {
  el_check("守护非数字指令使用锁定期限剩余预算且不建新trip",guardian_mode && arrive_by==el_goal.deadline_ts && user_limits.budget_cents==15000 && user_limits.currency=="CNY" && constraints.guardian_locked && el_begins==1 && el_dispatches==2)
  fs.write("limits-result.json",{checks:el_checks begins:el_begins dispatches:el_dispatches}.to_json())
 }
}
start_timeout(0.8,||fs.read_async("limits-input.json",fn(reply){
 if !reply.success {return} el_original=reply.text.parse_json().text
 let actual=explicit_limits(el_original)
 el_check("实际online12双预算语词只一金额解析300分钟20000分",actual!=nil && actual.minutes==300 && actual.budget_cents==20000 && actual.currency=="unspecified")
 let same=explicit_limits("5小时内到机场，预算200元，预算200.00元，守护预算。")
 el_check("同金额重复合并保币种与单位",same!=nil && same.to_json()==actual.to_json() && explicit_limits("300分钟内到机场，预算200元").to_json()==actual.to_json())
 el_check("明确金额冲突或明确币种冲突不能唯一确定",explicit_limits("5小时内到机场，预算200元，预算300元")==nil && explicit_limits("5小时内到机场，预算200人民币，预算200美元")==nil)
 let cny=explicit_limits("5小时内到机场，预算CNY200元，预算RMB200元")
 el_check("人民币别名一致可合并而无法识别数字声明不忽略",cny!=nil && cny.currency=="CNY" && cny.budget_cents==20000 && explicit_limits("5小时内到机场，预算200元，预算USD300")==nil)
 el_check("原分钟小时整数与金额精度币种合同保持",explicit_limits("5小时30分钟，预算200元")==nil && explicit_limits("1.5小时，预算200元")==nil && explicit_limits("5小时，预算200.001元")==nil && explicit_limits("5小时，预算200美元").currency=="unsupported")
 let prior_run=run_id generated_active=true composer_open=false phase="completed"
 start_task_with("5小时，预算200元，预算300元",false)
 el_check("普通金额冲突提前反馈不建trip不模型且不改原run",el_begins==0 && el_dispatches==0 && run_id==prior_run && generated_active && composer_open && ui.composer_help.text()==runtime_status && runtime_status.search("无法唯一确定")>=0)
 start_task_with("5小时，预算200美元",false)
 el_check("既有不支持币种提前反馈不建trip不模型",el_begins==0 && el_dispatches==0 && run_id==prior_run && ui.composer_help.text()==runtime_status && runtime_status.search("币种预算")>=0)
 el_stage="normal" ui.sentence.set_text(el_original) start_task_with(el_original,false)
}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','render_content','guardian_refresh','refresh_generated_facts','interface_facts','trip_begin','agent_begin']:
        original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(400):
        if (jail/'limits-result.json').exists():break
        time.sleep(.025)
    report=json.loads((jail/'limits-result.json').read_text())
    report.update(main_sha256=hashlib.sha256(original.encode()).hexdigest(),model_requested=False,provider_requested=False,native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],boundary='原online12句及小控制输入，生产explicit_limits/start_task_with/start_task_ready；trip提交、绘制与agent_begin消费stub，仅核启动约束边界，不冒付费模型或保存闭环。')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in report['checks']) and not report['native_errors'],str(work/'report.json')
