"""第32轮费用与已查端点时刻的公开/历史重投影合同。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IDS=['route_2_6','route_2_10','route_2_7','route_2_8']
def prepare(jail):
    base=ROOT/'build/research/rail-integration/e2e/round32'
    public=json.loads((base/'route-cost-time-facts-private.json').read_bytes())
    snapshot=json.loads((base/'saved-full-snapshot-private.json').read_bytes())['data']['snapshot']
    folder=Path(jail)/'route-public-fixture';folder.mkdir()
    for i,id in enumerate(IDS):
        raw=next(r for r in snapshot['route_data'] if r['id']==id)
        (folder/f'route-{i}.json').write_text(json.dumps({'raw':raw,'public':public[id]},ensure_ascii=False,separators=(',',':')))
    snapshot['facts']['routes']=[public[id] for id in IDS]
    snapshot['route_data']=[]
    (folder/'context.json').write_text(json.dumps(snapshot,ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let pc_items=[] let pc_output=[] let pc_context=nil let pc_raw_before=[]
fn pc_clone(value){return value.to_json().parse_json()}
fn pc_load(index){if index>=4 {start_timeout(0.01,||pc_project(0)) return}
 fs.read_async("route-public-fixture/route-"+index+".json",fn(reply){if !reply.success{return} let item=reply.text.parse_json() pc_items.push(item) pc_raw_before.push(item.raw.to_json()) start_timeout(0.01,||pc_load(index+1))})
}
fn pc_project(index){if index>=pc_items.len(){start_timeout(0.01,||pc_finish()) return}
 let item=pc_items[index] let candidate=pc_clone(item.raw)
 candidate.geometry_ref=route_get(candidate,"history_geometry_ref") candidate.taxi_wait_verified=nil candidate.endpoint_gap_m=route_get(item.public,"endpoint_gap_m")
 let check={estimated_arrival_ts:item.public.estimated_arrival_ts passed:item.public.assessment.passed reason:"已保存事实离线投影"}
 let summary=query_route_summary_checked(candidate,check)
 let fact=interface_route_facts(candidate,check)
 let history=history_route_public_facts(item.public,item.raw)
 let fallback=history_route_public_facts(item.public,nil)
 pc_output.push({id:item.raw.id cost:route_cost_facts(item.raw) arrival:route_arrival_facts(item.raw,item.public.estimated_arrival_ts) summary:summary interface:fact history:history fallback:fallback cold_kind:route_kind_label(item.raw)})
 fs.write("route-public-projection-"+index+".json",pc_output[index].to_json())
 start_timeout(0.01,||pc_project(index+1))
}
fn pc_finish(){
 let full=pc_clone(pc_items[0].raw) full.destination_access=nil full.connection_verified=true full.provider_connection_status="checked" full.request_bound=true full.origin_complete=true full.endpoint_complete=true full.completion_status="reached_requested_destination"
 let goal={schema:1 state:"active" version:1 deadline_ts:arrive_by total_budget_cents:20000 currency:"CNY" spent_cents:0 progress:nil preferences:nil risk_acceptance:nil destination:nil confirmed_at:received_at selection_basis:nil selected_route:pc_clone(pc_items[0].raw) confirmations:nil}
 let guardian=guardian_public_goal(goal,true)
 let unchanged=true for index item in pc_items {if item.raw.to_json()!=pc_raw_before[index] {unchanged=false}}
 trip_replay=true trip_history=pc_context trip_history.route_data=[] for item in pc_items {trip_history.route_data.push(item.raw)}
 let history_facts=interface_facts_with_routes(nil)
 fs.write("route-public-history-interface.json",history_facts.to_json())
 fs.write("route-public-controls.json",{full_cost:route_cost_facts(full) full_arrival:route_arrival_facts(full,pc_items[0].public.estimated_arrival_ts) guardian:guardian raw_unchanged:unchanged}.to_json())
 fs.write("route-public-done.json",{done:true}.to_json())
}
start_timeout(0.8,||fs.read_async("route-public-fixture/context.json",fn(reply){if !reply.success{return} pc_context=reply.text.parse_json() received_at=pc_context.facts.received_at arrive_by=pc_context.facts.arrive_by constraints={budget_cents:20000} route_nodes={} for node in pc_context.facts.route_graph.nodes {route_nodes[node.ref]=node} candidates=[] guardian_goal=nil trip_replay=false pc_load(0)}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(1000):
        if (jail/'route-public-done.json').exists():break
        time.sleep(.02)
    duplicates=[]
    def pairs(items):
        seen=set()
        for k,v in items:
            if k in seen:duplicates.append(k)
            seen.add(k)
        return dict(items)
    def load(name):return json.loads((jail/name).read_bytes(),object_pairs_hook=pairs)
    projected=[load(f'route-public-projection-{i}.json') for i in range(4)]
    controls=load('route-public-controls.json');history=load('route-public-history-interface.json')
    originals=[load(f'route-public-fixture/route-{i}.json') for i in range(4)]
    checks=[]
    def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
    check('partial57整程nil报价小计57保持且label明确',all(p['cost']['amount_cents'] is None and p['cost']['full_journey_amount_cents'] is None and not p['cost']['complete'] and p['cost']['queried_legs_amount_cents']==5700 and p['cost']['known_subtotal_cents']==5700 and p['history']['price_cents'] is None and '全程费用未知' in p['history']['price_label'] for p in projected[:2]))
    check('完整已知控制保整程57与请求端点alias',controls['full_cost']['amount_cents']==5700 and controls['full_cost']['complete'] and controls['full_arrival']['estimated_arrival_ts']==originals[0]['public']['estimated_arrival_ts'] and controls['full_arrival']['arrival_scope']=='requested_routing_point')
    check('端点未核实CD不暴露目的地alias保原queried时刻',all(p['arrival']['estimated_arrival_ts'] is None and p['arrival']['arrival_scope']=='queried_endpoint_only' and p['arrival']['queried_endpoint_arrival_ts']==o['public']['estimated_arrival_ts'] for p,o in zip(projected[2:],originals[2:])))
    check('入口A保原时刻并明确内部未知',projected[0]['arrival']['estimated_arrival_ts']==originals[0]['public']['estimated_arrival_ts'] and projected[0]['arrival']['arrival_scope']=='requested_routing_entry' and '内部通达未知' in projected[0]['arrival']['arrival_label'])
    check('summary接口history三投影费用时刻一致',all(p['summary']['cost']==p['cost']==p['interface']['cost']==p['history']['cost'] and p['summary']['arrival_scope']==p['interface']['arrival_scope']==p['history']['arrival_scope'] and p['summary']['queried_endpoint_arrival_ts']==p['history']['queried_endpoint_arrival_ts'] for p in projected))
    check('历史无raw仍只采用保存小计和端点证据',all(p['fallback']['cost']['amount_cents'] is None and p['fallback']['cost']['queried_legs_amount_cents']==o['raw']['price_cents'] and p['fallback']['queried_endpoint_arrival_ts']==o['public']['estimated_arrival_ts'] for p,o in zip(projected,originals)))
    check('cold selected_legs保公共交通铁路步行类别',projected[0]['cold_kind']=='公共交通＋铁路＋步行' and controls['guardian']['selected_route']['kind_label']=='公共交通＋铁路＋步行')
    check('守护公开整程价nil且已查小计57保持',controls['guardian']['selected_route']['price_cents'] is None and controls['guardian']['selected_route']['cost']['queried_legs_amount_cents']==5700)
    check('历史interface采用重投影且保存raw金额时刻未改',controls['raw_unchanged'] and [r['cost'] for r in history['routes']]==[p['history']['cost'] for p in projected] and all(p['cost']['queried_legs_amount_cents']==o['raw']['price_cents'] and p['arrival']['queried_endpoint_arrival_ts']==o['public']['estimated_arrival_ts'] for p,o in zip(projected,originals)))
    check('编码后覆写字段各一次无重复键',not duplicates)
    report={'checks':checks,'product_source_sha256':hashlib.sha256(original.encode()).hexdigest(),'model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'fixture_boundary':'round32四条实际public事实与保存route_data；summary克隆只补cold必需可选metadata；完整费用控制为明确测试控制，不声称原路线完整。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in checks),str(work/'report.json')
