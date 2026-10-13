"""online3已查三腿费用范围与14条真实地图目录分组，纯投影不发图。"""
import copy,hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=ROOT/'build/research/journey-guardian/current-online-3';route=json.loads((base/'route1-10-materialized-private.json').read_bytes());facts=json.loads((base/'actual-facts-0-private.json').read_bytes());public=next(r for r in facts['routes'] if r['id']==route['id']);catalog=public['map_paths'];assert len(catalog)==14
    route['legs']=copy.deepcopy(route['selected_legs'])
    missing=copy.deepcopy(route);missing['legs'][1]['price_cents']=None;missing['price_cents']=None;missing['known_cost_cents']=800
    Path(jail,'cost-map-fixture.json').write_text(json.dumps({'route':route,'missing':missing,'catalog':catalog,'at':public['assessment']['evaluated_at'],'deadline':facts['arrive_by']},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let cm_paths=[]
fn map_geometry(candidate){return {paths:cm_paths omitted:0}}
start_timeout(0.8,||fs.read_async("cost-map-fixture.json",fn(reply){let data=reply.text.parse_json() let route=data.route let before=route.to_json()
 let cost=route_cost_facts(route) let label=route_cost_label(cost) let missing=route_cost_facts(data.missing) let missing_label=route_cost_label(missing)
 let assessment=guardian_assess(route,data.at,data.deadline,20000)
 route.map_paths_cache=data.catalog for entry in data.catalog {cm_paths.push(entry.start+";"+entry.end)}
 let metadata=route_map_metadata(route)
 let primitive=true for group in metadata.selection_groups {if !group.selection_scope.is_string(){primitive=false}}
 if !primitive {fs.write("cost-map-result.json",{primitive_valid:false}.to_json()) return}
 let rejected=static_map_params_selected(route,nil,nil)
 let selected=selected_map_geometry(route,metadata.selection_groups[0].path_indices) let accepted=static_map_params_selected(route,nil,metadata.selection_groups[0].path_indices)
 let saved=saved_route_cost_facts({cost:cost})
 fs.write("cost-map-result.json",{primitive_valid:primitive cost:cost label:label missing:missing missing_label:missing_label assessment:assessment metadata:metadata rejected:rejected selected:selected accepted:accepted leg_prices:[route.legs[0].price_cents route.legs[1].price_cents route.legs[2].price_cents] saved_cost:saved original_price:route.price_cents original_source_ts:route.source_ts original_deadline:data.deadline}.to_json())
}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request','map_geometry']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(250):
        if (jail/'cost-map-result.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'cost-map-result.json').read_bytes());checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    c=o['cost'];check('真实800+4300+0三腿合计5100而整程nil状态unknown',o['leg_prices']==[800,4300,0] and sum(o['leg_prices'])==o['original_price']==c['queried_legs_amount_cents']==5100 and c['queried_legs_complete'] and c['queried_leg_count']==3 and c['full_journey_amount_cents'] is None and o['assessment']['status']=='unknown')
    check('到T3入口三段51标签准确且附加费保持可能未知',c['queried_legs_scope']=='requested_routing_entry' and 'T3' in o['label'] and '已查3段估价合计 ¥51' in o['label'] and '未核接入可能需要附加路段或费用' in o['label'])
    check('缺4300腿报价仅已知800不称合计齐全',o['missing']['queried_legs_amount_cents'] is None and not o['missing']['queried_legs_complete'] and o['missing']['known_subtotal_cents']==800 and '合计' not in o['missing_label'] and '至少一段报价未知' in o['missing_label'])
    groups=o['metadata']['selection_groups'];flat=[i for g in groups for i in g['path_indices']]
    check('真实14目录分组每组最多4全覆盖无重漏',o['primitive_valid'] and o['metadata']['path_count']==14 and all(0<len(g['path_indices'])<=4 for g in groups) and flat==list(range(14)) and len(flat)==len(set(flat)))
    check('不选14明确拒绝选择一组4条参数形状成功不发HTTP',o['rejected']['error'] is not None and o['rejected']['params']=='' and o['accepted']['error'] is None and o['accepted']['params']!='' and len(o['selected']['paths'])==4 and o['selected']['selected'])
    check('无raw旧publiccost保新增范围count未知理由',o['saved_cost']['queried_legs_scope']==c['queried_legs_scope'] and o['saved_cost']['queried_leg_count']==3 and o['saved_cost']['unknown_reasons']==c['unknown_reasons'])
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'http_requested':False,'boundary':'真实online3保存route1_10与原14目录；selected_legs仅复制为legs报价/范围形状。map_geometry仅fixture用真实目录start/end构造14条两端点线，不重扫实际geometry、不声称几何等值或像素；不测UI map_bindings。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
