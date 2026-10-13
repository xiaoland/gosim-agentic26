"""真实滴滴普通/优惠价与高德查询区间报价的离线生产解析合同。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    didi=ROOT/'build/research/journey-guardian/current-online-11/didi-quote-raw-response-94-private.json'
    amap=ROOT/'build/research/rail-integration/amap/v5-gzsz.json'
    payload={'didi':json.loads(didi.read_text())['result'],'amap':json.loads(amap.read_text())['response']}
    (jail/'quote-scope-input.json').write_text(json.dumps(payload,ensure_ascii=False))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){fs.write("quote-scope-unexpected-http.json","{}")}
fn minimax_request(task,input,schema,token,record,done){fs.write("quote-scope-unexpected-model.json","{}")}
let qs_data=nil let qs_reply=nil let qs_result=nil
fn didi_request(name,args,token,done){done(qs_result)}
fn agent_tool_result(result){qs_reply=result}
start_timeout(0.8,||fs.read_async("quote-scope-input.json",fn(reply){
 if !reply.success {return} qs_data=reply.text.parse_json() let before=qs_data.to_json()
 run_id+=1 agent_active=true phase="tools" let at=time_now() qs_result=qs_data.didi
 let df=qs_data.didi.structuredContent.from.to_json().parse_json() let dt=qs_data.didi.structuredContent.to.to_json().parse_json() df.city=nil dt.city=nil
 didi_places={"scope-from":df "scope-to":dt} didi_quotes={}
 quote_didi({from_ref:"scope-from" to_ref:"scope-to"},run_id)
 let quotes=qs_reply.quotes let effective=nil for q in quotes {if q.product_name=="特惠快车" {effective=q}}
 let from=register_route_node("scope-origin","记录查询起点",qs_data.amap.route.origin,"recorded-amap",nil)
 let to=register_route_node("scope-destination","记录查询终点",qs_data.amap.route.destination,"recorded-amap",nil)
 let options=qs_data.amap.route.transits let direct=route_candidates(qs_data.amap,nil,at,at+7200,20000,at)
 let leg=extension_leg(qs_data.amap.route,options[0],0,options.len(),"transit",from,to,at,at,1)
 // 附价累加控制：真实普通报价177与额外合成公交250分，不声明真实出行或地点认证。
 position_record={name:df.name longitude:df.longitude latitude:df.latitude city:nil citycode:nil adcode:nil currency:"CNY" mock:true source:"quote-scope-control"}
 destination_record={id:"quote-scope-destination" name:dt.name longitude:dt.longitude latitude:dt.latitude city:nil citycode:nil adcode:nil currency:"CNY" mock:true source:"quote-scope-control"}
 received_at=at arrive_by=at+7200 constraints={budget_cents:30000 currency:"CNY"} trip_replay=false candidates=[]
 let start=coord_text(position_record) let end=coord_text(destination_record)
 let control={status:"1" route:{origin:start destination:end taxi_cost:"177" paths:[{distance:"1000" cost:{duration:"900"} steps:[{polyline:start+";"+end}]}]}}
 let original=route_candidates(nil,control,at,arrive_by,30000,at)[0] original.requested_origin=start original.requested_destination=end
 normalize_queried_route(original) assign_candidate_ref(original)
 let extra=original.legs[0].to_json().parse_json() extra.id="scope-extra-transit" extra.mode="transit" extra.price_cents=250 extra.segments=[]
 original.legs.push(extra) original.price_cents=17950 original.known_cost_cents=17950 candidates.push(original)
 let old_price=original.price_cents let old_leg_price=original.legs[0].price_cents let old_duration=original.duration_seconds let old_segments=original.segments.to_json()
 attach_quote({route_id:original.id leg_id:original.legs[0].id quote_ref:effective.ref place_basis:"附价累加控制，不认证不同提供方地点或连接"},run_id)
 let attached=qs_reply let derived=candidates[candidates.len()-1]
 qs_result=qs_data.didi.to_json().parse_json() let invalid=qs_result.structuredContent.items[1] invalid.priceDiscounted="165-180" qs_result.structuredContent.items=[invalid]
 quote_didi({from_ref:"scope-from" to_ref:"scope-to"},run_id) let invalid_quote=qs_reply.quotes[0]
 attach_quote({route_id:original.id leg_id:original.legs[0].id quote_ref:invalid_quote.ref place_basis:"未知优惠报价控制"},run_id) let invalid_attached=qs_reply
 fs.write("quote-scope-result.json",{quotes:quotes attached:attached derived_price:derived.price_cents derived_leg_price:derived.legs[0].price_cents extra_price:derived.legs[1].price_cents derived_from:derived.derived_from_route_id original_id:original.id old_values_unchanged:original.price_cents==old_price && original.legs[0].price_cents==old_leg_price && original.duration_seconds==old_duration && original.segments.to_json()==old_segments invalid_quote:invalid_quote invalid_attach_rejected:!invalid_attached.success
 original_fee:options[0].cost.transit_fee direct_price:direct[0].price_cents direct_basis:direct[0].price_basis leg_price:leg.price_cents leg_basis:leg.price_basis inputs_unchanged:before==qs_data.to_json()}.to_json())
}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','minimax_request','didi_request','agent_tool_result']:
        original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(400):
        if (jail/'quote-scope-result.json').exists():break
        time.sleep(.025)
    o=json.loads((jail/'quote-scope-result.json').read_text())
    quote=next(q for q in o['quotes'] if q['product_name']=='特惠快车')
    checks=[{'name':'真实优惠165为有效16500且普通177以base17700保留无资格字段','passed':quote['price_text']=='165' and quote['price_cents']==16500 and quote['base_price_text']=='177' and quote['base_price_cents']==17700 and quote['discounted_price_text']=='165' and 'discount_applicability' not in quote},
            {'name':'无优惠采用普通价177且不精确优惠保持未知拒绝附价','passed':next(q for q in o['quotes'] if q['product_name']=='快车')['price_cents']==17700 and o['invalid_quote']['price_text']=='165-180' and o['invalid_quote']['price_cents'] is None and o['invalid_quote']['base_price_cents']==17700 and o['invalid_attach_rejected']},
            {'name':'生产attach_quote仅替换taxi为16500加250得16750且旧值不变','passed':o['attached']['success'] and o['derived_price']==16750 and o['derived_leg_price']==16500 and o['extra_price']==250 and o['derived_from']==o['original_id'] and o['old_values_unchanged']},
            {'name':'真实高德区间39两生产入口保3900及直接包含未知事实','passed':o['original_fee']=='39.000000' and o['direct_price']==o['leg_price']==3900 and all('供应商本次查询区间报价；各交通分段票价及包含关系未知，无法据此确认是否包含城际车票' in o[k] and 'amap-option.cost.transit_fee' in o[k] for k in ['direct_basis','leg_basis'])},
            {'name':'供应商原返回等值且无外部调用','passed':o['inputs_unchanged'] and not (jail/'quote-scope-unexpected-http.json').exists() and not (jail/'quote-scope-unexpected-model.json').exists()}]
    report={'checks':checks,'main_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':{'effective_price_text':quote['price_text'],'base_price_text':quote['base_price_text'],'base_price_cents':quote['base_price_cents'],'price_cents':quote['price_cents'],'discounted_price_text':quote['discounted_price_text'],'derived_price_cents':o['derived_price'],'original_route_unchanged':o['old_values_unchanged'],'amap_price_cents':o['direct_price'],'amap_leg_price_cents':o['leg_price']},'native_errors':[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],'model_requested':False,'provider_requested':False,'boundary':'online11真实MCP返回与已保存高德v5真实区间响应，生产quote_didi/route_candidates/extension_leg解析；普通/优惠规范化及生产attach_quote，附价用受控taxi/额外250分leg，不声明真实行程或地点匹配；不重新询价、不增加优惠资格。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in checks) and not report['native_errors'],str(work/'report.json')
