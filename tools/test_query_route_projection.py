"""真实原生摘要与JSON回执键的query_route投影合同，保留实际异步batch及提交队列。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
 p=ROOT/'build/research/journey-guardian/current-online-14'
 results=[json.loads(json.loads((p/f'tool_result-{n}-private.json').read_text())['result']) for n in [46,48]]
 (jail/'query-projection-input.json').write_text(json.dumps(results,ensure_ascii=False,separators=(',',':')))
 for i in range(2):
  (jail/f'query-projection-route-{i}.json').write_bytes((ROOT/f'build/research/journey-guardian/current-online-13/all-trace-original-private/vm-1/first-render-2-route-{i}.json').read_bytes())
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
let qp_inputs=nil let qp_full=[] let qp_replies=[] let qp_stage=0 let qp_before=nil
fn query_route_summary_checked(candidate,check){let result=product_query_route_summary_checked(candidate,check) qp_full.push(result) return result}
fn tool_new_nodes(){return qp_inputs[0].new_nodes}
fn agent_pump(token){
 for message in agent_messages {if message.role=="tool" {qp_replies.push({name:active_qp_name result:message.content.parse_json() full:qp_full})}}
 qp_stage+=1 start_timeout(0.01,||qp_next())
}
let active_qp_name=""
fn qp_next(){
 if qp_stage>=5 {
  qp_full=[]
  let details=[] for candidate in candidates {details.push(interface_route_facts(candidate,route_recheck(candidate,time_now(),arrive_by,20000)))}
  let json_results=[] for result in qp_inputs {json_results.push({original:result projected:query_route_result_summaries(result.routes)})}
  fs.write("query-projection-result.json",{replies:qp_replies details:details json_results:json_results original_costs:qp_before current_costs:[candidates[0].price_cents candidates[1].price_cents]}.to_json()) return
 }
 qp_full=[] active_qp_name=["query_route" "query_transit" "query_driving" "query_route" "extend_route"][qp_stage]
 let call={id:"query-projection-"+qp_stage function:{name:active_qp_name}}
 agent_calls=[call] agent_messages=[] agent_call_index=0 decisions=[] active_tool=call agent_result_pending=nil
 agent_tool_job={id:qp_stage+1 token:run_id call:call call_index:0 candidate_start:0 message_start:0 decision_start:0 continuation_queued:false next_dispatched:false phase:"route_summary" settled:false failure_seen:false}
 if qp_stage<3 {finish_tool_from_state(run_id)} else {
  // options已接收后的真实公共回执路径；不查询供应商、不改变已有Route。
  accept_extension_option({token:run_id owner:agent_tool_job index:0 options:[] candidates:candidates from:{ref:"origin"} to:{ref:"destination"} mode:"transit" departure:received_at added:[] rejected:[] completed:[]})
 }
}
fn qp_load(index){if index>=2 {qp_before=[candidates[0].price_cents candidates[1].price_cents] qp_next() return}
 fs.read_async("query-projection-route-"+index+".json",fn(reply){if !reply.success{return} candidates.push(reply.text.parse_json()) start_timeout(0.01,||qp_load(index+1))})
}
start_timeout(0.8,||fs.read_async("query-projection-input.json",fn(reply){if !reply.success{return}
 qp_inputs=reply.text.parse_json() run_id+=1 agent_active=true trip_replay=false constraints={budget_cents:20000} arrive_by=time_now()+18000 received_at=time_now() candidates=[] route_nodes={} tool_candidate_start=0 qp_load(0)
}))
'''
def source(original):
 for name in ['trace_initialize','trip_load','amap_request','agent_pump','query_route_summary_checked','tool_new_nodes']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 for _ in range(750):
  if (jail/'query-projection-result.json').exists():break
  time.sleep(.02)
 result=json.loads((jail/'query-projection-result.json').read_text());checks=[]
 def check(name,value):checks.append({'name':name,'passed':bool(value)})
 def reduced(routes):return [{k:v for k,v in r.items() if k not in ('legs','steps')} for r in routes]
 replies=result['replies']
 check('真实原生摘要query默认及to_ref回执仅删legs/steps',all(replies[i]['result']['routes']==reduced(replies[i]['full']) for i in [0,3]))
 check('其它query别名与extend_route保全明细',all(replies[i]['result']['routes']==replies[i]['full'] for i in [1,2,4]))
 nodes=result['json_results'][0]['original']['new_nodes']
 thin=[{k:v for k,v in n.items() if k not in ('longitude','latitude','coordinate_system')} for n in nodes]
 check('query两路径节点引用摘要其它工具完整节点保持',all(r['result']['new_nodes']==(thin if i in (0,3) else nodes) for i,r in enumerate(replies)))
 check('online14公交及taxi真实JSON回执同样只删两键',all(r['projected']==reduced(r['original']['routes']) for r in result['json_results']))
 check('原生完整摘要及get_route同用完整事实保legs steps segments',all(r['legs'] and r['steps'] for reply in replies for r in reply['full']) and all(r['legs'] and r['steps'] and r['segments'] for r in result['details']))
 check('候选原金额保持',result['original_costs']==result['current_costs'])
 report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'native_errors':[x for x in (work/'native.log').read_text().splitlines() if '[E]' in x],'model_requested':False,'provider_requested':False,'boundary':'生产summary_checked原生对象、真实read_route_summaries异步batch、工具owner提交队列和extension回执路径；供应商查询与候选注册未执行，候选为online13原始live Route，online14公交/taxi原JSON回执作第二键类型对照。get_route共用完整事实读取，不冒完整查询E2E。'}
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks) and not report['native_errors'],str(work/'report.json')
