"""online15地点、采用与详情回执的原生边界，实测完整入口/坐标可按需恢复。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
 p=ROOT/'build/research/journey-guardian/current-online-15'
 def load(n):return json.loads(json.loads((p/f'tool_result-{n}-private.json').read_text())['result'])
 value={'search':load(15),'adopt':load(28),'query':load(30),'routes':[load(45)['route'],load(47)['route']]}
 provider=[]
 for poi in value['search']['places']:
  entry=poi.get('entrance');city=poi['city_metadata']
  provider.append({'id':poi['id'],'name':poi['name'],'typecode':poi['typecode'],'type':poi['type'],'parent':poi['parent'],'location':str(poi['longitude'])+','+str(poi['latitude']),'entr_location':str(entry['longitude'])+','+str(entry['latitude']) if entry else '', 'cityname':city['city'],'citycode':city['citycode'],'adcode':city['adcode'],'pname':'广东省','address':poi['address']})
 value['search_provider']={'pois':provider}
 (jail/'model-tool-projection-input.json').write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn projection_clock(){return 1791905600.294132}
let mp_input=nil let mp_stage=0 let mp_results=[] let mp_original_nodes=[] let mp_adopt_full=nil
fn amap_request(path,p,token,done){start_timeout(0.01,||done(mp_input.search_provider))}
fn ensure_map_catalog(candidate,done){done()}
fn route_recheck(candidate,at,deadline,budget){return {}}
fn interface_route_facts(candidate,check){for fact in mp_input.routes {if fact.id==candidate.id {return fact}} return nil}
fn agent_pump(token){
 for message in agent_messages {if message.role=="tool" {mp_results.push(message.content.parse_json())}}
 if mp_stage==0 {for poi in poi_records {mp_original_nodes.push(route_nodes[poi.node_ref].to_json().parse_json()) if poi.entrance!=nil {mp_original_nodes.push(route_nodes[poi.entrance.ref].to_json().parse_json())}}}
 if mp_stage==1 {mp_adopt_full={success:true origin:position_record destination:destination_record constraints:constraints limits:user_limits arrive_by:arrive_by new_nodes:tool_new_nodes()}}
 mp_stage+=1 start_timeout(0.01,||mp_next())
}
fn mp_next(){
 if mp_stage>=5 {
  let only_steps={id:"history-only-steps" steps:mp_input.routes[0].steps}
  let empty_segments={id:"history-empty-segments" steps:mp_input.routes[0].steps segments:[]}
  fs.write("model-tool-projection-result.json",{results:mp_results adopt_full:mp_adopt_full original_nodes:mp_original_nodes only_steps:model_route_detail(only_steps) empty_segments:model_route_detail(empty_segments) full_route_inputs:mp_input.routes thin_nodes:model_node_references(mp_input.query.new_nodes)}.to_json()) return
 }
 let name="" let p={}
 if mp_stage==0 {name="search_places" p={query:"深圳宝安机场T3"}}
 elif mp_stage==1 {name="adopt_destination" p={poi_id:mp_input.adopt.destination.id basis:mp_input.adopt.constraints.inference.reason}}
 elif mp_stage==2 {
  name="get_route_graph"
  for node in mp_input.query.new_nodes {let added=register_route_node(node.ref,node.name,coord_text(node),node.source,route_get(node,"city_metadata")) mp_original_nodes.push(added.to_json().parse_json())}
  let refs=[] for node in mp_original_nodes {refs.push(node.ref)} p={node_refs:refs}
 }
 else {name="get_route" candidates=[] for fact in mp_input.routes {candidates.push({id:fact.id})} p={id:mp_input.routes[mp_stage-3].id}}
 let call={id:"model-tool-projection-"+mp_stage function:{name:name arguments:p.to_json()}}
 agent_calls=[call] agent_messages=[] agent_call_index=0 active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)
}
start_timeout(0.8,||fs.read_async("model-tool-projection-input.json",fn(reply){if !reply.success{return}
 mp_input=reply.text.parse_json() run_id+=1 agent_active=true trip_replay=false guardian_mode=false guardian_goal=nil constraints=nil candidates=[] route_nodes={} route_prefixes={}
 position_record=mp_input.adopt.origin constraints=mp_input.adopt.constraints user_limits=mp_input.adopt.limits received_at=mp_input.adopt.arrive_by-user_limits.minutes*60 arrive_by=mp_input.adopt.arrive_by source_records=[]
 mp_next()
}))
'''
def source(original):
 original=original.replace('time_now()','projection_clock()')
 for name in ['trace_initialize','trip_load','amap_request','ensure_map_catalog','route_recheck','interface_route_facts','agent_pump']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 for _ in range(750):
  if (jail/'model-tool-projection-result.json').exists():break
  time.sleep(.02)
 output=json.loads((jail/'model-tool-projection-result.json').read_text());input=json.loads((jail/'model-tool-projection-input.json').read_text());r=output['results'];checks=[]
 def check(name,value):checks.append({'name':name,'passed':bool(value)})
 def without(value,keys):return {k:v for k,v in value.items() if k not in keys}
 check('实际search_places全部20POI只删入口与重复返回时刻',r[0]['success'] and r[0]['places']==[without(x,('entrance','returned_at')) for x in input['search']['places']])
 full=output['adopt_full']
 check('实际adopt仅省重复字段且原目标约束绝对期限保持',r[1]=={**without(full,('origin','limits','new_nodes')),'destination':without(full['destination'],('entrance','routing_point'))} and full['destination']['id']==input['adopt']['destination']['id'] and full['constraints']==input['adopt']['constraints'] and full['arrive_by']==input['adopt']['arrive_by'])
 nodes={n['ref']:n for n in r[2]['graph']['nodes']};originals={n['ref']:n for n in output['original_nodes']}
 check('按refs真实get_route_graph恢复全部POI入口及query新增站点坐标来源',r[2]['success'] and set(nodes)==set(originals) and all(all(nodes[ref].get(k)==v for k,v in old.items()) for ref,old in originals.items()))
 check('get_route两真实回执仅删steps详细segments和地图目录全保',all(result=={'success':True,'route':without(fact,('steps',))} for result,fact in zip(r[3:],input['routes'])))
 check('原UI完整事实steps及segments未变',output['full_route_inputs']==input['routes'])
 check('旧历史只有steps或空segments均保唯一详情',output['only_steps']=={'id':'history-only-steps','steps':input['routes'][0]['steps']} and output['empty_segments']=={'id':'history-empty-segments','steps':input['routes'][0]['steps'],'segments':[]})
 check('query所有新增节点仅省坐标且不裁身份数量',output['thin_nodes']==[without(x,('longitude','latitude','coordinate_system')) for x in input['query']['new_nodes']])
 def size(value):return len(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
 report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'bytes':{'search_places':[size(input['search']),size(r[0])],'adopt_destination':[size(output['adopt_full']),size(r[1])],'get_route_1':[size({'success':True,'route':input['routes'][0]}),size(r[3])],'get_route_2':[size({'success':True,'route':input['routes'][1]}),size(r[4])],'query_route':[size(input['query']),size({**input['query'],'new_nodes':output['thin_nodes']})]},'native_errors':[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],'model_requested':False,'provider_requested':False,'boundary':'online15POI回执字段还原为供应商输入形状并经真实parse_pois构造原生POI；完整get_route公开事实注入，不重查供应商/模型/地图；真实search/adopt/get_route/get_route_graph工具分支、POI注册/采用、图selector与owner消息提交。离线冻结原时刻；详细get_route格式化不重算原数据，断言地图目录及UI原事实保持。'}
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks) and not report['native_errors'],str(work/'report.json')
