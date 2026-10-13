"""真实多方案记录的生产接驳回执、未知终点与轻量模型上下文回归。"""
import hashlib,json,time
from pathlib import Path
FIXTURE=r'''
fn agent_pump(token){}
let extension_checks=[] let extension_stage=0 let extension_count=0
fn extension_seed_existing(){
 if extension_count<11 {
  let segments=extension_data.route.transits[extension_count%2].segments
  let candidate=route_candidate("recorded-existing-"+extension_count,"public_transit",6000,5000,time_now(),time_now(),route_leg_endpoint(segments,false),coord_text(route_nodes["destination"]),true,segments)
  candidate.price_basis="recorded-load-fixture" candidate.requested_origin=coord_text(route_nodes["origin"]) candidate.requested_destination=coord_text(route_nodes["destination"])
  normalize_queried_route(candidate) assign_candidate_ref(candidate) candidates.push(candidate) extension_count+=1
  start_timeout(0.01,||extension_seed_existing()) return
 }
 let prefix=route_prefixes["origin"]
 // 本夹具只测生产回执负载，用记录路径实际起点作为前缀端点，不宣称现场接驳。
 prefix.actual_endpoint=route_leg_endpoint(extension_data.route.transits[0].segments,true)
 accept_route_extension(prefix,route_nodes["origin"],route_nodes["destination"],"transit",extension_data,time_now(),time_now(),run_id)
}
fn extension_check(name,passed){extension_checks.push({name:name passed:passed})}
fn agent_tool_result(result){
 if extension_stage==2 {
  extension_check("整段查询finish caller保全部新增候选",result.success && result.routes.len()==candidates.len()-12)
  let old_returned=false let count=candidates.len()
  read_route_summaries(candidates,run_id,fn(old){old_returned=true})
  accept_route_extension(route_prefixes["origin"],route_nodes["origin"],route_nodes["destination"],"transit",extension_data,time_now(),time_now(),run_id)
  run_id+=1
  start_timeout(0.05,||{
   extension_check("旧query批次不能回执或登记新候选",!old_returned && candidates.len()==count)
   fs.write("harness-smoke.json",{checks:extension_checks routes:result.routes.len()}.to_json())
  }) return
 }
 if extension_stage==0 {
  extension_check("未知路线终点给明确边界错误",!result.success && result.error=="Route实际终点未知，不能据请求终点继续扩展")
  extension_stage=1
  start_timeout(0.01,||extension_seed_existing())
 } else {
  let parsed=result.to_json().parse_json()
  extension_check("20真实方案保所有接受或明确拒绝回执",result.success && result.routes.len()+result.rejected.len()==20 && parsed.routes.len()==result.routes.len())
  extension_check("已有11候选之后新增候选与前缀全部保留",candidates.len()==12+result.routes.len() && result.routes.len()>0)
  let refs={} let valid=true for route in result.routes {if refs[route.id]==true {valid=false} refs[route.id]=true}
  extension_check("多方案引用无覆盖",valid)
  let source=route_get(candidates[0],"steps_cache") let context=model_task_context()
  extension_check("模型上下文不触发无关路线步骤解析",route_get(candidates[0],"steps_cache")==source && context.viewport!=nil && context.rendering_environment.scroll.is_string())
  extension_stage=2 tool_candidate_start=12 active_tool={id:"extension-finish" function:{name:"query_route"}} start_timeout(0.01,||finish_tool_from_state(run_id))
 }
}
start_timeout(1,||{
 let endpoint=route_leg_endpoint(extension_data.route.transits[0].segments,false)
 extension_check("供应商末端空占位不抹掉真实端点",endpoint!=nil && route_leg_endpoint([{}],false)==nil)
 extension_check("真正未定位末段保持未知",route_leg_endpoint([{walking:{steps:[{polyline:"113.1,22.1;113.2,22.2"}]}} {walking:{distance:"5" steps:[]}}],false)==nil)
 run_id+=1 agent_active=true arrive_by=time_now()+14400 constraints={budget_cents:20000}
 position_record={name:"广州南站" longitude:113.268730 latitude:22.988359 source:"contract-fixture" mock:true city:"广州市" citycode:"020" adcode:"440104" currency:"CNY"}
 destination_record={name:"深圳北站" longitude:114.029506 latitude:22.609878 source:"contract-fixture" mock:true city:"深圳市" citycode:"0755" adcode:"440303" currency:"CNY"}
 prepare_route_graph_base()
 let unknown=route_candidate("unknown-endpoint","public_transit",1,1,time_now(),time_now(),nil,coord_text(route_nodes["destination"]),true,[])
 unknown.price_basis="contract-fixture"
 unknown.requested_origin=coord_text(route_nodes["origin"]) unknown.requested_destination=coord_text(route_nodes["destination"])
 normalize_queried_route(unknown) assign_candidate_ref(unknown) candidates.push(unknown)
 extend_route({route_id:unknown.id to_ref:"destination" mode:"walk"},run_id)
})
'''
def source(original):
 root=Path(__file__).resolve().parents[1]
 data=json.loads((root/'build/research/rail-integration/amap/v5-gzsz.json').read_text())['response']
 data['route']['origin']='113.268730,22.988359'  # synthetic request boundary; original segment geometry is unchanged
 data['route']['transits']=data['route']['transits']*10
 prelude='\nlet extension_data='+json.dumps(json.dumps(data,ensure_ascii=False),ensure_ascii=False)+'.parse_json()\n'
 return original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1)+prelude+FIXTURE
def run(w,jail,original,injected):
 report=None
 for _ in range(300):
  try:report=json.loads((jail/'harness-smoke.json').read_text())
  except (FileNotFoundError,json.JSONDecodeError):pass
  if report:break
  time.sleep(.1)
 errors=[x for x in (w/'native.log').read_text().splitlines() if '[E]' in x]
 result=report or {'checks':[], 'incomplete':True}
 result.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,provider_called=False,recorded_real_supplier_data=True,duplicated_supplier_options=20,synthetic_request_origin=True,preexisting_candidates=11,native_errors=errors)
 (w/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 assert report and not errors and all(x['passed'] for x in report['checks']),str(w/'report.json')
 print('PASS: '+str(len(report['checks']))+'项生产接驳回执检查；'+str(w/'report.json'))
