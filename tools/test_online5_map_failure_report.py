"""地图checked硬错/旧token与真实guardian_report{}提交的薄边界。"""
import hashlib,json,time
from pathlib import Path
from test_trip_snapshot import read_record
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
 b=ROOT/'build/research/journey-guardian/current-online-5';trip=json.loads((b/'saved-full-snapshot-private.json').read_bytes())['data'];trip['snapshot']=None;(jail/'helper-trip.json').write_text(json.dumps(trip,ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn guardian_refresh(){}
fn amap_request(path,params,token,done){}
let oh_arm=true let oh_failure_count=0 let oh_waiters=0 let oh_old_waiters=0 let oh_result=nil let oh_owner=nil let oh_old=nil let oh_done=false
fn map_geometry_batch(job){if oh_arm {oh_arm=false loop {}} product_map_geometry_batch(job)}
fn map_geometry_fail(job){oh_failure_count+=1 product_map_geometry_fail(job)}
fn agent_pump(token){if oh_done{return} oh_done=true let reply=nil for m in agent_messages {if route_get(m,"role")=="tool" {reply=m.content.parse_json()}} fs.write("helper-result.json",{map_failure_count:oh_failure_count waiters:oh_waiters old_waiters:oh_old_waiters map_result:oh_result error:route_get(oh_owner,"map_geometry_error") pending:route_get(map_geometry_jobs,"failure") old_pending:route_get(map_geometry_jobs,"old") old:oh_old reply:reply messages:agent_messages decisions:decisions call_index:agent_call_index goal:guardian_goal}.to_json())}
fn oh_start_old(){oh_old={id:"old" segments:[]} ensure_map_catalog(oh_old,fn(result){oh_old_waiters+=1}) run_id+=1 map_geometry_jobs={}
 start_timeout(0.2,||fs.read_async("helper-trip.json",fn(reply){let trip=reply.text.parse_json() trip_records=[trip] trip_selected_id=trip.id trip_next_id=2 trip_generation=0 guardian_goal=trip.goal guardian_mode=true trip_replay=false position_record=nil candidates=[] source_records=[] phase="running" agent_active=true active_tool=nil agent_tool_job=nil decisions=[] agent_messages=[] let call={id:"report-test" function:{name:"report_goal_check" arguments:"{}"}} agent_calls=[call] agent_call_index=0 agent_schedule_next(run_id)}))
}
start_timeout(0.8,||{run_id+=1 oh_owner={id:"failure" segments:[]} ensure_map_catalog(oh_owner,fn(result){oh_waiters+=1 oh_result=result start_timeout(0.01,||oh_start_old())})})
'''
def source(original):
 for name in ['trace_initialize','trip_load','guardian_refresh','amap_request','map_geometry_batch','map_geometry_fail','agent_pump']:original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
 return original+'\n'+FIXTURE
def run(work,jail,original,injected):
 for _ in range(300):
  if (jail/'helper-result.json').exists():break
  time.sleep(.05)
 o=json.loads((jail/'helper-result.json').read_bytes());before=json.loads((jail/'helper-trip.json').read_bytes())['goal'];after=o['goal'];index=json.loads((jail/'navigation-trips.json').read_bytes())['data'];stored=read_record(jail,index['trips'][0]['file'])['goal'];checks=[]
 def check(name,v):checks.append({'name':name,'passed':bool(v)})
 check('checked真实instruction硬错清job且明确失败等待者恰一次',o['map_failure_count']==1 and o['waiters']==1 and o['pending'] is None and not o['map_result']['success'] and bool(o['error']))
 check('旧token清pending后无等待者或旧结果回写',o['old_waiters']==0 and o['old_pending'] is None and 'map_geometry_cache' not in o.get('old',{}))
 check('生产report_goal_check{}提交与tool回执恰一次',o['reply']['success'] and o['call_index']==1 and len(o['decisions'])==1 and len([m for m in o['messages'] if m.get('role')=='tool'])==1 and stored['last_check']['goal_version']==before['version'])
 check('报告提交保原goal版本source时价期限',all(after[k]==before[k] and stored[k]==before[k] for k in ['version','deadline_ts','total_budget_cents','spent_cents','confirmed_at','selection_basis']) and all(stored['selected_route'][k]==before['selected_route'][k] for k in ['source_ts','price_cents','departure_ts','duration_seconds','segments']))
 r={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'boundary':'原online5合法35KB goal与record头，snapshot=nil；真实instruction limit错误经map_geometry_schedule checked sink，旧token+清字典为cancel_task对应状态转移，未重跑UI取消。生产guardian_report→独立tool_timeout commit→guardian_store→trip_commit实际磁盘。仅guardian_refresh界面重绘stub；无完整图、planner或HTTP/M3。'};(work/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));assert all(x['passed'] for x in checks),str(work/'report.json')
