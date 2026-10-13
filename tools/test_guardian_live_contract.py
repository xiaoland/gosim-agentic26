"""guardian-live-1：依据校验、局部/全界面成功与单字段报价来源；一个原生组。"""
import copy,hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=ROOT/'build/research/journey-guardian/current-online-1';d=Path(jail)/'live-contract-fixture';d.mkdir()
    envelope=json.loads((base/'fixture-goal-original.json').read_bytes());goal=envelope['goal'];assert isinstance(goal['selection_basis'],str) and goal['selection_basis'].strip()
    for name in ('valid','missing','nonstring','empty'):
        value=copy.deepcopy(goal)
        if name=='missing':value.pop('selection_basis')
        elif name=='nonstring':value['selection_basis']=42
        elif name=='empty':value['selection_basis']=''
        out={'schema':1,'saved_at':envelope['saved_at'],'goal':value,'complete':'navigation-goal-v1'}
        (d/(name+'.json')).write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
    events=[json.loads(line) for line in (base/'trace-private.jsonl').read_text().splitlines()]
    call=json.loads(next(e['data'] for e in events if e['seq']==104));args=json.loads(call['arguments'])
    (d/'bad-document.json').write_text(json.dumps({'source':args['source']},ensure_ascii=False,separators=(',',':')))
    # 原公开结果报价为500/1000；没有供应商raw，最小option控制仅保transit_fee字段金额。
    provider={'status':'1','route':{'transits':[{'cost':{'duration':'600','transit_fee':fee},'distance':'100','segments':[{'walking':{'distance':'100','cost':{'duration':'600'},'steps':[{'polyline':'114,22;114.001,22'}]}}]} for fee in ('5','10')]}}
    (d/'provider.json').write_text(json.dumps(provider,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
let lc_stage=0 let lc_replies=[] let lc_pumps=0 let lc_bad=nil let lc_costs=[] let lc_validator=nil let lc_proposal=nil let lc_stores=0 let lc_siblings=[]
fn guardian_store(goal,done){lc_stores+=1 done(false) return false}
fn lc_submit(params){let call={id:"live-contract-"+lc_stage function:{name:"render_ui" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)}
fn agent_pump(token){if token!=run_id{return} lc_pumps+=1 let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}} lc_replies.push(reply)
 fs.write("live-contract-progress.json",{stage:lc_stage replies:lc_replies pumps:lc_pumps}.to_json())
 if lc_stage==0 {lc_stage=1 lc_submit({blocks:[{id:"summary" source:"Label{text:\"合法总结\"}"} {id:"explanation" source:"Label{text:\"合法说明\"}"} {id:"routes" source:"Label{text:\"合法候选\"}"} {id:"suggestions" source:"Label{text:\"合法建议\"}"}]})}
 elif lc_stage==1 {for id in ["summary" "explanation" "routes" "suggestions"] {let block=block_by_id(id) lc_siblings.push({id:id revision:block.revision source:block.raw_source})} lc_stage=2 lc_submit({blocks:[{id:"__document" source:"Label{text:\"实际修正根稿\"}"}]})}
 else {let siblings=[] for id in ["summary" "explanation" "routes" "suggestions"] {let block=block_by_id(id) siblings.push({id:id revision:block.revision source:block.raw_source})}
  fs.write("live-contract-result.json",{validators:lc_validator costs:lc_costs proposal:lc_proposal stores:lc_stores goal_saved:guardian_goal!=nil replies:lc_replies sibling_before:lc_siblings sibling_after:siblings pumps:lc_pumps final_global_error:interface_error}.to_json())}
}
fn lc_read(name){let value=read_text("live-contract-fixture/"+name+".json").parse_json() let path="live-contract-fixture/encoded-"+name+".json" fs.write(path,guardian_encode(value.goal)) return guardian_read(path)}
fn lc_prepare(provider){let now=time_now() received_at=now arrive_by=now+3600 constraints={budget_cents:20000 currency:"CNY"} user_limits={minutes:60 budget_cents:20000}
 destination_record={name:"合成请求终点" longitude:114.03 latitude:22 citycode:"0755" adcode:"440306" currency:"CNY"} position_record={id:"synthetic-origin" name:"合成起点" mock:false accuracy_m:10 coordinate_system:"GCJ-02" longitude:114 latitude:22 source:"synthetic-fixture" sampled_at_unix:now citycode:"0755" adcode:"440306" currency:"CNY"}
 candidates=route_candidates(provider,nil,now,arrive_by,20000,now)
 for index route in candidates {route.geometry_ref="synthetic-"+index lc_costs.push({cost:route_cost_facts(route) arrival:route_arrival_facts(route,now+600) price_cents:route.price_cents})}
 guardian_goal=nil guardian_mode=false guardian_pending=nil trip_selected_id="synthetic-trip" trip_records=[] trip_replay=false agent_active=true phase="running" run_id+=1 source_records=[] ui_blocks=[] route_nodes={}
 fs.write("live-contract-helpers.json",{validators:lc_validator costs:lc_costs}.to_json())
 lc_proposal=guardian_propose({route_id:candidates[0].id preferences:"合成偏好" risk_acceptance:"未知估计" basis:"只准备，不代表批准"})
 lc_submit(lc_bad)
}
start_timeout(0.8,||{
 let valid=lc_read("valid") let missing=lc_read("missing") let nonstring=lc_read("nonstring") let empty=lc_read("empty")
 lc_validator={valid:valid!=nil && guardian_valid_goal(valid.goal) missing_rejected:missing==nil nonstring_rejected:nonstring==nil empty_rejected:empty==nil}
 fs.read_async("live-contract-fixture/bad-document.json",fn(reply){lc_bad=reply.text.parse_json() fs.read_async("live-contract-fixture/provider.json",fn(data){lc_prepare(data.text.parse_json())})})
})
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump','guardian_store']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(600):
        if (jail/'live-contract-result.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'live-contract-result.json').read_bytes());checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('真实goal读回仅合法非空String依据接受',all(o['validators'].values()))
    a,b,c=o['replies'];check('原failed document真实保留不借局部成功清全局',not a['success'] and b['success'] and b['changed_blocks_success'] and not b['interface_success'] and [x['id'] for x in b['unresolved_blocks']]==['__document'] and b['unresolved_blocks'][0]['diagnostics']!='')
    check('同ID真实修document全局成功且四siblings保持',c['success'] and c['changed_blocks_success'] and c['interface_success'] and c['unresolved_blocks']==[] and o['final_global_error']=='' and o['sibling_before']==o['sibling_after'] and len(o['sibling_after'])==4 and o['pumps']==3)
    check('option字段报价500/1000守恒整程nil到达范围未知',len(o['costs'])==2 and [x['price_cents'] for x in o['costs']]==[500,1000] and all(x['cost']['full_journey_amount_cents'] is None and x['cost']['queried_legs_amount_cents']==x['price_cents'] and '本次option字段报价' in x['cost']['basis'] and 'cost.coverage' in x['cost']['basis'] and x['arrival']['estimated_arrival_ts'] is None and x['arrival']['arrival_scope']=='queried_endpoint_only' for x in o['costs']))
    check('production propose只prepare无需先批准且不save',o['proposal']['success'] and o['proposal']['effect']=='proposal_prepared_not_saved' and not o['goal_saved'] and o['stores']==0)
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'原live-1已确认goal生产读边界/四selection_basis形状；原seq104 document source未改，四named合法控制；原公开500/1000报价值的最小transit_fee option控制，非缺失raw供应商完整重放；不验证批准持久化。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
