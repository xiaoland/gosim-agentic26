"""静态facts隔离输入：局部渲染成功与全界面未解决失败、同ID真实修复。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    events=[json.loads(line) for line in (ROOT/'build/research/journey-guardian/current-online-1/trace-private.jsonl').read_text().splitlines()]
    args=json.loads(json.loads(next(e['data'] for e in events if e['seq']==104))['arguments'])
    (Path(jail)/'partial-render-original.json').write_text(json.dumps({'source':args['source']},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
fn ensure_interface_facts_owned(token,done,owner){let facts={routes:[] guardian:nil phase:phase} ui_facts_json=facts.to_json() ui_facts_cached_revision=ui_facts_revision ui_facts_object=facts ui_facts_object_revision=ui_facts_revision ui_facts_object_run=run_id done(facts)}
fn ensure_interface_facts(token,done){ensure_interface_facts_owned(token,done,nil)}
let pr_stage=0 let pr_replies=[] let pr_pumps=0 let pr_siblings=[] let pr_refs=[] let pr_proposal=nil let pr_stores=0
fn guardian_store(goal,done){pr_stores+=1 done(false) return false}
fn pr_submit(params){let call={id:"partial-render-"+pr_stage function:{name:"render_ui" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)}
fn agent_pump(token){if token!=run_id{return} pr_pumps+=1 let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}} pr_replies.push(reply)
 fs.write("partial-render-progress.json",{stage:pr_stage replies:pr_replies pumps:pr_pumps}.to_json())
 if pr_stage==0 {pr_stage=1 pr_submit({blocks:[{id:"summary" source:"Label{text:\"合法总结\"}"} {id:"explanation" source:"Label{text:\"合法说明\"}"} {id:"routes" source:"Label{text:\"合法候选\"}"} {id:"suggestions" source:"Label{text:\"合法建议\"}"}]})}
 elif pr_stage==1 {for id in ["summary" "explanation" "routes" "suggestions"] {let block=block_by_id(id) pr_refs.push(block) pr_siblings.push({id:id revision:block.revision source:block.raw_source index:block.index same_block_reference:true})} pr_stage=2 pr_submit({blocks:[{id:"__document" source:"Label{text:\"实际修正根稿\"}"}]})}
 else {let siblings=[] for index id in ["summary" "explanation" "routes" "suggestions"] {let block=block_by_id(id) siblings.push({id:id revision:block.revision source:block.raw_source index:block.index same_block_reference:block==pr_refs[index]})}
  fs.write("partial-render-result.json",{proposal:pr_proposal stores:pr_stores goal_saved:guardian_goal!=nil replies:pr_replies sibling_before:pr_siblings sibling_after:siblings pumps:pr_pumps final_global_error:interface_error}.to_json())}
}
start_timeout(0.8,||fs.read_async("partial-render-original.json",fn(reply){run_id+=1 agent_active=true phase="running" candidates=[] guardian_goal=nil guardian_pending=nil trip_records=[] trip_selected_id=nil trip_replay=false guardian_mode=false position_record=nil destination_record=nil source_records=[] ui_blocks=[]
 let now=time_now() received_at=now arrive_by=now+3600 constraints={budget_cents:20000 currency:"CNY"} destination_record={name:"合成终点" longitude:114.03 latitude:22}
 let candidate=route_candidate("proposal-control","walking",600,500,now,now,"114.001,22","114.03,22",true,[{walking:{distance:"100" cost:{duration:"600"} steps:[{polyline:"114,22;114.001,22"}]}}]) candidate.geometry_ref="synthetic-geometry" candidates=[candidate]
 pr_proposal=guardian_propose({route_id:candidate.id preferences:"合成偏好" risk_acceptance:"未知" basis:"只准备，不是批准"})
 pr_submit(reply.text.parse_json())}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump','ensure_interface_facts_owned','ensure_interface_facts','guardian_store']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(600):
        if (jail/'partial-render-result.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'partial-render-result.json').read_bytes());a,b,c=o['replies'];checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('原208Bdocument真实unknown named id诊断失败保留',not a['success'] and [x['id'] for x in a['unresolved_blocks']]==['__document'] and 'id' in a['unresolved_blocks'][0]['diagnostics'])
    check('四named局部成功仍报告failed document全局未成功',b['success'] and [x['id'] for x in b['unresolved_blocks']]==['__document'] and b['unresolved_blocks'][0]['diagnostics']!='' and len(b['blocks'])==4)
    check('同ID真实修document全局清且siblings身份内容不变',c['success'] and c['unresolved_blocks']==[] and o['final_global_error']=='' and o['sibling_before']==o['sibling_after'] and len(o['sibling_after'])==4 and o['pumps']==3)
    check('精简回执保留准确状态与实际库存',all(x['status']=='initialized' for x in b['blocks']) and b['unresolved_blocks'][0]['status']=='error' and len(b['current_blocks'])==5 and all(x['status']=='initialized' for x in c['current_blocks']) and all(not any(k in r for k in ['changed_blocks_success','interface_success','meaning','notified']) for r in [a,b,c]) and all(not any(k in x for k in ['installed','notified','complete','repair']) for r in [a,b,c] for key in ['blocks','current_blocks','unresolved_blocks'] for x in r[key]))
    check('production propose返回prepare effect且未保存goal',o['proposal']['success'] and o['proposal']['effect']=='proposal_prepared_not_saved' and o['stores']==0 and not o['goal_saved'])
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'只隔离ensure_interface_facts固定最小facts；生产agent_schedule_next/prepare_render_tool/mount/wait/result/commit续链。原live-1 seq104 document source208B未改；四named合法控制；不验证facts/location/图或已采纳validator/cost。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
