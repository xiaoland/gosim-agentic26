"""online2真实物化Route范围与严格render参数/库存；单VM、无网络。"""
import copy,hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=ROOT/'build/research/journey-guardian/current-online-2';snapshot=json.loads((base/'saved-full-snapshot-private.json').read_bytes())['data']['snapshot'];original=next(r for r in snapshot['route_data'] if r['id']=='route_1_5')
    events=[json.loads(line) for line in (base/'trace-private.jsonl').read_text().splitlines()]
    proposal=json.loads(json.loads(next(e['data'] for e in events if e['seq']==160))['result'])['proposal']
    invalid=json.loads(json.loads(next(e['data'] for e in events if e['seq']==192))['arguments'])
    route=copy.deepcopy(original)
    def trim(value):
        if isinstance(value,dict):return {k:trim(v) for k,v in value.items() if k not in ('polyline',)}
        if isinstance(value,list):return [trim(v) for v in value]
        return value
    route['segments']=trim(route['segments'])
    route['geometry_ref']=route['history_geometry_ref'];route['taxi_wait_verified']=None
    route['endpoint_gap_m']=None
    route['legs']=[]
    nodes=[]
    for i,saved in enumerate(route['selected_legs']):
        leg=copy.deepcopy(saved);leg.update(id=f'restored-leg-{i}',from_ref=saved['from']['ref'],to_ref=saved['to']['ref'],requested_to_ref=saved['to']['ref'],segments=route['segments'])
        route['legs'].append(leg)
        for saved_node in (saved['from'],saved['to']):
            node=copy.deepcopy(saved_node)
            if 'longitude' not in node:
                node['longitude'],node['latitude']=map(float,node['location'].split(','))
            nodes.append(node)
    folder=Path(jail)/'online2-fixture';folder.mkdir()
    (folder/'route.json').write_text(json.dumps(route,ensure_ascii=False,separators=(',',':')))
    context={'fixed_at':proposal['created_at'],'original_queried_arrival':proposal['assessment']['estimated_arrival_ts'],'deadline':snapshot['facts']['arrive_by'],'destination':snapshot['facts']['destination'],'basis':proposal['goal']['selection_basis'],'nodes':nodes,'expected_queried_to_ref':route['legs'][-1]['requested_to_ref'],'original_price_basis':original['price_basis'],'original_price':original['price_cents'],'original_duration':original['duration_seconds'],'original_source_ts':original['source_ts'],'geometry_trimmed':True,'original_segments_count':len(original['segments'])}
    (folder/'context.json').write_text(json.dumps(context,ensure_ascii=False,separators=(',',':')))
    (folder/'invalid-render.json').write_text(json.dumps(invalid,ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
fn ensure_interface_facts_owned(token,done,owner){let facts={routes:[] guardian:nil phase:phase} ui_facts_json=facts.to_json() ui_facts_cached_revision=ui_facts_revision ui_facts_object=facts ui_facts_object_revision=ui_facts_revision ui_facts_object_run=run_id done(facts)}
fn ensure_interface_facts(token,done){ensure_interface_facts_owned(token,done,nil)}
let oc_route=nil let oc_context=nil let oc_invalid=nil let oc_helpers=nil let oc_stage=0 let oc_replies=[] let oc_stores=0
fn guardian_store(goal,done){oc_stores+=1 done(false) return false}
fn oc_submit(params){let call={id:"online2-"+oc_stage function:{name:"render_ui" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)}
fn agent_pump(token){if token!=run_id{return} let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}} oc_replies.push(reply)
 fs.write("online2-progress.json",{stage:oc_stage replies:oc_replies}.to_json())
 if oc_stage==0 {oc_stage=1 oc_submit({source:"Label{text:\"禁止互斥\"}" blocks:[{id:"summary" source:"Label{text:\"禁止互斥\"}"}]})}
 elif oc_stage==1 {oc_stage=2 oc_submit({blocks:[{id:"summary" source:"Label{text:\"合法总结\"}"}]})}
 elif oc_stage==2 {oc_stage=3 oc_submit({blocks:[{id:"summary" source:"Label{text:\"更新总结\"}"} {id:"route_detail" source:"Label{text:\"明确提交的详情\"}" overlay:true visible:false}]})}
 else {let inventory=render_current_blocks() fs.write("online2-result.json",{helpers:oc_helpers replies:oc_replies inventory:inventory stores:oc_stores goal_saved:guardian_goal!=nil basis:guardian_pending.goal.selection_basis label:guardian_proposal_label()}.to_json())}
}
fn oc_begin(){run_id+=1 agent_active=true phase="running" trip_replay=false guardian_mode=false guardian_goal=nil guardian_pending=nil guardian_check=nil trip_records=[] trip_selected_id="synthetic-trip" candidates=[oc_route] source_records=[] ui_blocks=[] position_record=nil destination_record=oc_context.destination route_nodes={} for node in oc_context.nodes {route_nodes[node.ref]=node}
 received_at=oc_route.source_ts arrive_by=oc_context.deadline constraints={budget_cents:20000 currency:"CNY"} user_limits={budget_cents:20000 minutes:240}
 let check=route_recheck(oc_route,oc_context.fixed_at,arrive_by,20000) let summary=query_route_summary_checked(oc_route,check) let assessed=guardian_assess(oc_route,oc_context.fixed_at,arrive_by,20000) let fact=interface_route_facts(oc_route,check)
 let proposal=guardian_propose({route_id:oc_route.id preferences:"原合约范围" risk_acceptance:"未知" basis:oc_context.basis})
 oc_helpers={summary:summary assessed:assessed fact:fact proposal:proposal label:guardian_proposal_label() raw_price:oc_route.price_cents raw_duration:oc_route.duration_seconds raw_price_basis:oc_route.price_basis raw_source_ts:oc_route.source_ts}
 fs.write("online2-helpers.json",oc_helpers.to_json()) oc_submit(oc_invalid)
}
start_timeout(0.8,||fs.read_async("online2-fixture/route.json",fn(reply){oc_route=reply.text.parse_json() fs.read_async("online2-fixture/context.json",fn(c){oc_context=c.text.parse_json() fs.read_async("online2-fixture/invalid-render.json",fn(p){oc_invalid=p.text.parse_json() start_timeout(0.01,||oc_begin())})})}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump','ensure_interface_facts_owned','ensure_interface_facts','guardian_store']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(600):
        if (jail/'online2-result.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'online2-result.json').read_bytes());c=json.loads((jail/'online2-fixture/context.json').read_bytes());h=o['helpers'];checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('固定原160时刻partial summary/assess端点原值且目的地aliasnil',h['summary']['estimated_arrival_ts'] is None and h['assessed']['estimated_arrival_ts'] is None and abs(h['summary']['queried_endpoint_arrival_ts']-c['original_queried_arrival'])<.01 and h['summary']['queried_endpoint_arrival_ts']==h['assessed']['queried_endpoint_arrival_ts'])
    selected=h['proposal']['proposal']['goal']['selected_route'];assessment=h['proposal']['proposal']['assessment']
    check('真实proposal/publicselected仍partialunknown且1000fullnil',h['proposal']['success'] and assessment['status']=='unknown' and assessment['estimated_arrival_ts'] is None and selected['estimated_arrival_ts'] is None and selected['queried_endpoint_arrival_ts']==assessment['queried_endpoint_arrival_ts'] and selected['cost']['queried_legs_amount_cents']==1000 and selected['cost']['full_journey_amount_cents'] is None)
    check('duration范围已查最早场景原price/duration/source/basis不变',h['summary']['duration_scope']=='queried_legs_only' and 'earliest_scenario' in h['summary']['duration_basis'] and h['raw_price']==c['original_price']==1000 and h['raw_duration']==c['original_duration'] and h['raw_price_basis']==c['original_price_basis'] and h['raw_source_ts']==c['original_source_ts'])
    label=h['label'];marker='Agent推荐理由（不是可行性认证）'
    check('权威unknown/cost/arrival先于原Agent理由且不save',o['basis']==c['basis'] and label.index('证据不足，状态未知')<label.index(marker) and label.index('全程费用未知')<label.index(marker) and label.index('目的地到达未知')<label.index(marker) and o['stores']==0 and not o['goal_saved'])
    check('queried station entrance与整体destination分离partial slacknil保queried',h['summary']['queried_to_ref']==c['expected_queried_to_ref'] and h['summary']['queried_to_ref']!='destination' and h['summary']['overall_destination_ref']=='destination' and h['fact']['waiting_slack_seconds'] is None and h['fact']['queried_endpoint_slack_seconds']==c['deadline']-h['fact']['queried_endpoint_arrival_ts'])
    a,b,d,e=o['replies'];check('真实192未声明item及sourceblocks互斥拒无部分安装',not a['success'] and 'item' in a['error'] and a['current_blocks']==[] and not b['success'] and '互斥' in b['error'] and b['current_blocks']==[])
    check('正常blocks及更新current_blocks与实际库存相符',d['success'] and [x['id'] for x in d['current_blocks']]==['summary'] and e['success'] and [x['id'] for x in e['current_blocks']]==['summary','route_detail'] and e['current_blocks']==o['inventory'] and e['current_blocks'][0]['revision']==2 and e['current_blocks'][1]['revision']==1)
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'真实online2 route1_5物化字段，只删segments.polyline几何并从selected_legs.from/to恢复legs refs/segments与Node经纬度（来自原location），补coldmetadata；固定原160时刻用于helper，真实propose用真实now仅比scope，不shadow时钟；固定facts仅renderer，不完整图/liveheap/地图/批准持久化。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')

# 已有原组结束后追加的最小完整Route对照；不重复partial/render负载。
def full_prepare(jail):pass
def full_source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
start_timeout(0.8,||{
 let at=1791801357.637638 arrive_by=1791819000 constraints={budget_cents:20000 currency:"CNY"}
 let full=route_candidate("synthetic-full-control","walking",600,500,at,at,"114.03,22","114.03,22",true,[])
 full.actual_origin="114,22" full.request_bound=true full.origin_complete=true full.endpoint_complete=true full.connection_verified=true full.provider_connection_status="checked" full.completion_status="reached_requested_destination" full.geometry_ref="synthetic-full-control"
 let check=route_recheck(full,at,arrive_by,20000) let summary=query_route_summary_checked(full,check)
 fs.write("online2-full-control.json",{summary:summary at:at}.to_json())
})
'''
def full_run(work,jail,original,injected):
    for _ in range(200):
        if (jail/'online2-full-control.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'online2-full-control.json').read_bytes());s=o['summary']
    checks=[{'name':'正常完整Route到达alias非nil且目的地范围与整程价正常','passed':s['estimated_arrival_ts']==o['at']+600 and s['estimated_arrival_ts']==s['queried_endpoint_arrival_ts'] and s['arrival_scope']=='requested_routing_point' and s['duration_scope']=='requested_routing_point' and s['cost']['full_journey_amount_cents']==500}]
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'追加仅正常完整Route最小synthetic helper对照；无geometry/图/渲染链，不宣称原online2完整。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
