"""第24轮原参数渲染入口诊断；缺失raw明确采用相邻真实候选负载。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'build/research/rail-integration/e2e'
def prepare(jail):
 events=[json.loads(x) for x in (E/'round24/trace-private.jsonl').read_text().splitlines()]
 nodes={};context=None
 for e in events:
  if e['event']!='tool_result':continue
  d=json.loads(e['data']);v=json.loads(d['result'])
  if d['name']=='adopt_destination':context=v
  for node in v.get('new_nodes',[]):nodes[node['ref']]=node
  for poi in v.get('places',[]):
   if poi.get('node_ref'):nodes[poi['node_ref']]=dict(poi,ref=poi['node_ref'])
   if poi.get('entrance'):nodes[poi['entrance']['ref']]=poi['entrance']
 raw={int(x.stem.rsplit('-',1)[1]):x for x in (E/'private-state-round24/home/apps/os.agentic26-navigation').rglob('first-render-2-route-*.json')}
 assert set(raw)==set(range(19))-{3,5},sorted(raw)
 directory=Path(jail)/'render-entry-fixture';directory.mkdir();context['new_nodes']=list(nodes.values())
 arguments=json.loads(json.loads((E/'round24/render-blocking-call-private.json').read_text())['data'])['arguments'];arguments=json.loads(arguments)
 (directory/'context.json').write_text(json.dumps(context,ensure_ascii=False));(directory/'arguments.json').write_text(json.dumps(arguments,ensure_ascii=False))
 total=0
 for i in range(19):
  route=json.loads(raw[i if i in raw else i-1].read_text())
  if i not in raw:route['id']=f'route_2_{i+1}'
  route['stations_registered_generation']=-1
  text=json.dumps(route,ensure_ascii=False);total+=len(text.encode());(directory/f'route-{i}.json').write_text(text)
 boundary={'round':24,'candidate_count':19,'actual_raw_count':17,'missing_raw_indexes':[3,5],'duplicate_loads':[{'index':3,'source':2},{'index':5,'source':4}],'exact_original_raw_replay':False,'nodes':len(nodes),'fixture_raw_bytes':total,'original_arguments_bytes':len(json.dumps(arguments,ensure_ascii=False).encode())}
 (directory/'boundary.json').write_text(json.dumps(boundary));return boundary
FIXTURE=r'''
let re_context=nil let re_params=nil let re_marks=[] let re_dispatches=0 let re_reply=nil let re_started=0 let re_done=false
let re_stage=0 let re_checks=[] let re_mounts=0 let re_guard="" let re_invalidations=0 let re_mount_before=0
fn re_check(name,passed){re_checks.push({name:name passed:passed}) fs.write("render-entry-progress.json",{stage:re_stage checks:re_checks}.to_json())}
fn render_probe_mark(stage){re_marks.push({stage:stage at:time_now()}) product_render_probe_mark(stage)}
fn mount_ui_blocks(params,token,revision){re_mounts+=1 re_marks.push({stage:"mount_wrapper_enter" at:time_now() serialized_bytes:ui_facts_json.len() test_stage:re_stage facts_revision:ui_facts_cached_revision current_revision:ui_facts_revision}) let changed=product_mount_ui_blocks(params,token,revision) re_marks.push({stage:"mount_wrapper_return" at:time_now() test_stage:re_stage}) return changed}
fn ensure_interface_facts_owned(token,done,owner){product_ensure_interface_facts_owned(token,fn(facts){done(facts)
 if re_guard=="call" {re_guard="" active_tool={id:"replacement-call"}}
 elif re_guard=="run" {re_guard="" run_id+=1}
 elif re_guard=="stale" {re_guard="" re_invalidations+=1 ui_facts_revision+=1}
},owner)}
fn amap_request(path,params,token,done){}
fn re_submit(id,params){let call={id:id function:{name:"render_ui" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 active_tool=nil agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] start_timeout(0.01,||agent_schedule_next(run_id))}
fn agent_pump(token){if token!=run_id {return} re_dispatches+=1 for message in agent_messages {if message.role=="tool" {re_reply=message.content.parse_json()}}
 if re_stage==0 {
  let errors=re_reply!=nil && !re_reply.success && re_reply.blocks.len()==5 for block in re_reply.blocks {if block.diagnostics=="" {errors=false}}
  re_check("原XML实际诊断错误回执与一次派发",errors && re_dispatches==1)
  re_stage=1 re_submit("legal-native",{blocks:[{id:"legal-native" source:"Label{text:\"原生隔离渲染\"}"}]})
 } elif re_stage==1 {
  re_check("合法Splash实际installed notified rendered",re_reply.success && re_reply.blocks[0].status=="initialized" && re_dispatches==2)
  re_stage=2 start_timeout(0.1,||re_cancel_call())
 } elif re_stage==4 {
  let fresh=true for mark in re_marks {if route_get(mark,"test_stage")==4 && mark.stage=="mount_wrapper_enter" && mark.facts_revision!=mark.current_revision {fresh=false}}
  re_check("缓存过期异步复核完整19事实后挂载",re_invalidations==1 && fresh && ui_facts_object.routes.len()==19 && ui_facts_cached_revision==ui_facts_revision && re_reply.success && re_dispatches==3)
  re_report()
 }
}
fn re_cancel_call(){re_mount_before=re_mounts re_guard="call" let call={id:"cancelled-call"} active_tool=call interface_revision+=1 prepare_render_tool("render_ui",{blocks:[{id:"must-not-mount-call" source:"Label{text:\"cancelled\"}"}]},run_id,call,interface_revision)
 start_timeout(0.1,||{re_check("旧activecall独立挂载入口不推进",re_mounts==re_mount_before && re_dispatches==2 && block_by_id("must-not-mount-call")==nil) re_stage=3 re_cancel_run()})}
fn re_cancel_run(){re_mount_before=re_mounts re_guard="run" let call={id:"cancelled-run"} active_tool=call interface_revision+=1 prepare_render_tool("render_ui",{blocks:[{id:"must-not-mount-run" source:"Label{text:\"cancelled\"}"}]},run_id,call,interface_revision)
 start_timeout(0.1,||{re_check("旧run独立挂载入口不推进",re_mounts==re_mount_before && re_dispatches==2 && block_by_id("must-not-mount-run")==nil) re_stage=4 re_guard="stale" re_submit("stale-native",{blocks:[{id:"stale-native" source:"Label{text:\"复核后原生渲染\"}"}]})})}
fn re_report(){if re_done{return} re_done=true fs.write("render-entry-report.json",{checks:re_checks dispatches:re_dispatches reply:re_reply marks:re_marks elapsed:time_now()-re_started facts_count:if ui_facts_object!=nil {ui_facts_object.routes.len()} else {nil} serialized_bytes:ui_facts_json.len() active_call:if active_tool!=nil {active_tool.id} else {nil}}.to_json())}
fn re_load(index){if index>=19 {re_begin() return}
 fs.read_async("render-entry-fixture/route-"+index+".json",fn(reply){let candidate=reply.text.parse_json() candidate.stations_registered_generation=route_node_generation candidates.push(candidate) start_timeout(0.01,||re_load(index+1))})}
fn re_begin(){run_id+=1 agent_active=true phase="running" trip_replay=false
 position_record=re_context.origin destination_record=re_context.destination constraints=re_context.constraints user_limits=re_context.limits arrive_by=re_context.arrive_by received_at=position_record.sampled_at_unix
 route_nodes={} for node in re_context.new_nodes {route_nodes[node.ref]=node} ui_blocks=[] source_records=[] ui_facts_revision+=1 ui_facts_cached_revision=-1
 re_started=time_now() re_submit("round24-recorded-render",re_params) start_timeout(10,||re_report())}
start_timeout(1,||fs.read_async("render-entry-fixture/context.json",fn(reply){re_context=reply.text.parse_json() fs.read_async("render-entry-fixture/arguments.json",fn(args){re_params=args.text.parse_json() candidates=[] re_load(0)})}))
'''

def source(original):
 for name in ['render_probe_mark','mount_ui_blocks','agent_pump','amap_request','ensure_interface_facts_owned']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+FIXTURE
def run(work,jail,original,injected):
 for _ in range(700):
  if (jail/'render-entry-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'render-entry-report.json').read_text()) if (jail/'render-entry-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'render-entry-fixture/boundary.json').read_text()),provider_called=False,model_called=False,native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line])
 report['limitations']=[
  '17 original raw candidates; missing indexes3/5 duplicate adjacent real raw2/4 with missing IDs. Raw/public-summary equivalence is not asserted.',
  'Original argument values are preserved by parse/re-serialization; textual formatting differs.',
  'Original accumulated agent/model messages, source_records and live heap are not restored; station generation is marked cached.',
  'Native XML/FlowPad parser and not-found diagnostics are expected feedback for the unchanged original source.']
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 safe={key:report.get(key) for key in ['checks','dispatches','facts_count','serialized_bytes','product_source_sha256','fixture_boundary','limitations','provider_called','model_called']}
 safe['budget_bail']=any('budget exceeded' in line or 'instruction limit reached' in line for line in report['native_errors'])
 (work/'report-safe.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2));print(work/'report.json')
 assert report.get('dispatches')==3 and len(report.get('checks',[]))==5 and all(check['passed'] for check in report['checks']),str(work/'report.json')
 assert not safe['budget_bail'],str(work/'report.json')

# 共享模型/界面事实的时间标签及公开render回执边界；同一原生runner，无新UI驱动。
def contract_prepare(jail):
 events=[json.loads(line) for line in (E/'round27/trace-private.jsonl').read_text().splitlines()]
 first=next(e for e in events if e['event']=='model_request')
 messages=json.loads(json.loads(first['data'])['body'])['messages']
 context=json.loads(next(m['content'] for m in messages if m['role']=='user'))['facts']
 assert context['received_at']==1791729672.456025 and context['arrive_by']==1791744072.456025
 recorded=json.loads((E/'round24/render-blocking-call-private.json').read_text())
 arguments=json.loads(json.loads(recorded['data'])['arguments'])
 directory=Path(jail)/'render-contract-fixture';directory.mkdir()
 (directory/'context.json').write_text(json.dumps(context,ensure_ascii=False))
 (directory/'arguments.json').write_text(json.dumps(arguments,ensure_ascii=False))
 boundary={'round27_first_model_context_seq':first['seq'],'received_at':context['received_at'],'arrive_by':context['arrive_by'],'candidate_load':0,'xml_source':'round24 original render arguments, unchanged values','provider_requests':0,'model_requests':0}
 (directory/'boundary.json').write_text(json.dumps(boundary));return boundary

CONTRACT_FIXTURE=r'''
let pc_context=nil let pc_xml=nil let pc_stage=0 let pc_checks=[] let pc_replies=[] let pc_geometry=[] let pc_trace=[] let pc_labels=nil let pc_dispatches=0 let pc_done=false let pc_provider_calls=0
fn pc_check(name,passed){pc_checks.push({name:name passed:passed}) fs.write("render-contract-progress.json",{stage:pc_stage checks:pc_checks dispatches:pc_dispatches}.to_json())}
fn amap_request(path,params,token,done){pc_provider_calls+=1}
fn trace_emit_run(event,data,call_id,token){if event=="render_result" {pc_trace.push({call_id:call_id geometry:data.geometry})} product_trace_emit_run(event,data,call_id,token)}
fn pc_submit(id,params){let call={id:id function:{name:"render_ui" arguments:params.to_json()}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)}
fn agent_pump(token){if token!=run_id{return} pc_dispatches+=1 let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}}
 pc_replies.push(reply)
 let rects=[] for result in reply.blocks {let block=block_by_id(result.id) rects.push({id:result.id geometry:route_get(block,"render_geometry")})}
 pc_geometry.push(rects)
 let public_clean=true for block in reply.blocks {if route_get(block,"container_rect")!=nil || route_get(block,"body_rect")!=nil {public_clean=false}}
 if pc_stage==0 {
  let block=reply.blocks[0] let private_rect=block_by_id("pc-visible").render_geometry
  pc_check("visible=true原生源码已执行通知，公开无rect且私有保几何",reply.success && block.status=="initialized" && block.visible && block.diagnostics=="" && public_clean && private_rect.container_rect!=nil && private_rect.body_rect!=nil)
  pc_stage=1 start_timeout(0.1,||pc_submit("pc-hidden-call",{blocks:[{id:"pc-hidden" source:"Label{text:\"隐藏待渲染\"}" overlay:true height:100}]}))
 } elif pc_stage==1 {
  let block=reply.blocks[0]
  pc_check("真实hidden已安装未通知为pending而非失败",!reply.success && block.status=="initialization_unconfirmed" && block.diagnostics=="" && !block.visible && public_clean && block_by_id("pc-hidden").render_geometry!=nil)
  pc_stage=2 start_timeout(0.1,||pc_submit("pc-xml-call",pc_xml))
 } else {
  let errors=!reply.success && reply.blocks.len()==5 for block in reply.blocks {if block.status!="error" || block.diagnostics=="" {errors=false}}
  pc_check("原XML真实语法运行错误仍有明确diagnostics",errors && public_clean)
  start_timeout(0.3,||pc_report())
 }
}
fn pc_report(){if pc_done{return} pc_done=true fs.write("render-contract-report.json",{checks:pc_checks labels:pc_labels replies:pc_replies private_geometry:pc_geometry trace_geometry:pc_trace dispatches:pc_dispatches provider_calls:pc_provider_calls}.to_json())}
fn pc_begin(){run_id+=1 agent_active=true phase="running" guardian_mode=false trip_replay=false trip_records=[] trip_selected_id=nil ui_blocks=[] candidates=[] source_records=[] route_nodes={} route_prefixes={}
 received_at=pc_context.received_at arrive_by=pc_context.arrive_by position_record=pc_context.origin destination_record=pc_context.destination user_limits=pc_context.limits constraints=pc_context.limits ui_facts_revision+=1 ui_facts_cached_revision=-1
 let model=model_task_context() let facts=interface_facts_with_routes([])
 pc_labels={model_received_label:model.received_at_label interface_received_label:facts.received_at_label model_deadline_label:model.arrive_by_label interface_deadline_label:facts.arrive_by_label model_received_epoch:model.received_at interface_received_epoch:facts.received_at model_deadline_epoch:model.arrive_by interface_deadline_epoch:facts.arrive_by model_timezone:model.timezone interface_timezone:facts.timezone}
 pc_check("真实跨午夜modelcontext/interface标签一致且epoch不变",model.received_at_label=="2026-10-11 22:41（北京时间）" && facts.received_at_label==model.received_at_label && model.arrive_by_label=="2026-10-12 02:41（北京时间）" && facts.arrive_by_label==model.arrive_by_label && model.received_at==1791729672.456025 && facts.received_at==model.received_at && model.arrive_by==1791744072.456025 && facts.arrive_by==model.arrive_by && model.timezone=="Asia/Shanghai" && facts.timezone==model.timezone)
 pc_submit("pc-visible-call",{blocks:[{id:"pc-visible" source:"Label{text:\"真实可见原生\"}"}]}) start_timeout(10,||pc_report())
}
start_timeout(1,||fs.read_async("render-contract-fixture/context.json",fn(reply){pc_context=reply.text.parse_json() fs.read_async("render-contract-fixture/arguments.json",fn(args){pc_xml=args.text.parse_json() pc_begin()})}))
'''
def contract_source(original):
 for name in ['amap_request','agent_pump','trace_emit_run']:
  original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
 return original+'\n'+CONTRACT_FIXTURE

def contract_run(work,jail,original,injected):
 for _ in range(800):
  if (jail/'render-contract-report.json').exists():break
  time.sleep(.02)
 report=json.loads((jail/'render-contract-report.json').read_text()) if (jail/'render-contract-report.json').exists() else {'incomplete':True}
 report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),fixture_boundary=json.loads((jail/'render-contract-fixture/boundary.json').read_text()),native_errors=[line for line in (work/'native.log').read_text().splitlines() if '[E]' in line],model_called=False)
 public_clean=all('container_rect' not in b and 'body_rect' not in b for reply in report.get('replies',[]) for b in reply['blocks'])
 geometry=report.get('trace_geometry',[])
 trace_kept=len(geometry)==3 and all(isinstance(item.get('geometry'),list) and all('container_rect' in b['rects'] and 'body_rect' in b['rects'] for b in item['geometry']) for item in geometry)
 report['public_rect_keys_absent']=public_clean;report['private_trace_geometry_present']=trace_kept
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(work/'report-safe.json').write_text(json.dumps({k:v for k,v in report.items() if k!='native_errors'},ensure_ascii=False,indent=2));print(work/'report.json')
 assert len(report.get('checks',[]))==4 and all(c['passed'] for c in report['checks']),str(work/'report.json')
 assert public_clean and trace_kept and report.get('provider_calls')==0,str(work/'report.json')
