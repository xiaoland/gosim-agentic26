"""守护原整程重执行/差额范围与未批准提案，单VM函数级离线回归。"""
import copy,hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=1791800000
    service={'trip':'SYNTH1','train_id':'synthetic-train','train_start_date':'2026-10-12','boarding_date':'2026-10-12','from_station':'SYN','to_station':'END','departure_ts':base+300,'arrival_ts':base+1800}
    route={'id':'saved-synthetic','kind':'mixed','duration_seconds':1920,'price_cents':1000,'known_cost_cents':1000,'currency':'CNY','estimated':True,'source':'synthetic-saved','source_ts':base,'expires_at':base+300,'departure_ts':base,'waiting_included':True,'waiting_basis':'provider_total','taxi_wait_verified':False,'request_bound':True,'origin_complete':True,'endpoint_complete':True,'actual_origin':'114,22','actual_endpoint':'114.03,22','destination':'114.03,22','endpoint_gap_m':0,'completion_status':'unknown','connection_verified':True,'provider_connection_status':'checked','warnings':'合成旧价，不是新查询','geometry_ref':'synthetic-geometry','plan_key':'synthetic-saved-plan','segments':[{'walking':{'steps':[{'polyline':'114,22;114.03,22','road':'synthetic-road'}],'distance':'3000','cost':{'duration':'1920'}}}], 'selected_legs':[{'mode':'walk','duration_seconds':60},{'mode':'rail','duration_seconds':1500,'rail_service':service,'quote':{'quoted_at':base,'expires_at':base+300}},{'mode':'walk','duration_seconds':120}]}
    goal={'schema':1,'state':'active','version':4,'confirmed_at':base,'deadline_ts':base+3600,'total_budget_cents':5000,'spent_cents':0,'currency':'CNY','progress':'','preferences':'合成偏好','risk_acceptance':'估计未知','destination':{'name':'合成终点','longitude':114.03,'latitude':22},'selected_route':route,'selection_basis':'合成已确认计划','confirmations':[]}
    candidate=copy.deepcopy(route);candidate.update(id='new-synthetic',price_cents=1200,known_cost_cents=1200)
    d=Path(jail)/'guardian-reexecution-fixture';d.mkdir();(d/'data.json').write_text(json.dumps({'base':base,'goal':goal,'candidate':candidate},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let gr_data=nil let gr_stores=0
fn guardian_store(goal,done){gr_stores+=1 done(false) return false}
fn gr_begin(){let goal=gr_data.goal let route=gr_data.candidate let base=gr_data.base let before=goal.to_json()
 let at={location:"114,22" longitude:114 latitude:22 sampled_at_unix:base+301}
 let early=guardian_reexecution(goal,base+100,at) let late=guardian_reexecution(goal,base+301,at) let absent=guardian_reexecution(goal,base+301,nil)
 let progress=goal.to_json().parse_json() progress.progress="用户已确认到站" let underway=guardian_reexecution(progress,base+301,at)
 let partial=guardian_cost_delta(route,goal)
 let valid=late.evidence_scope.is_string() && partial.comparison_scope.is_string()
 if !valid {fs.write("guardian-reexecution-result.json",{primitive_valid:false}.to_json()) return}
 let fullgoal=goal.to_json().parse_json() fullgoal.selected_route.completion_status="reached_requested_destination"
 let fullroute=route.to_json().parse_json() fullroute.completion_status="reached_requested_destination"
 let full=guardian_cost_delta(fullroute,fullgoal) let remaining=guardian_cost_delta(route,progress)
 guardian_goal=goal guardian_mode=true guardian_pending=nil guardian_check=nil trip_replay=false trip_selected_id="synthetic-trip" trip_generation=1 trip_loading=false trip_pending_commit=nil trip_capture_pending=nil agent_active=false phase="waiting" run_id+=1 candidates=[route] source_records=[] ui_blocks=[] route_nodes={} guardian_sequence=0
 destination_record=goal.destination position_record=at constraints={budget_cents:5000 currency:"CNY"} user_limits={budget_cents:5000 minutes:60} received_at=base arrive_by=goal.deadline_ts
 let snapshot=guardian_snapshot()
 let proposal=guardian_propose({route_id:route.id preferences:"合成偏好" risk_acceptance:"估计未知" basis:"隔离函数级提案"})
 let version=guardian_pending.proposal_version let stale=guardian_confirm(version-1) let same=guardian_goal.to_json()==before
 fs.write("guardian-reexecution-result.json",{goal_before:before.parse_json() goal_after:goal primitive_valid:valid early:early late:late absent:absent underway:underway partial:partial full:full remaining:remaining snapshot:snapshot proposal:proposal stale_confirm_result:stale stores:gr_stores goal_unchanged:same raw_unchanged:goal.to_json()==before original_source_ts:goal.selected_route.source_ts original_quote_ts:goal.selected_route.selected_legs[1].quote.quoted_at original_deadline:goal.deadline_ts original_departure:goal.selected_route.selected_legs[1].rail_service.departure_ts original_arrival:goal.selected_route.selected_legs[1].rail_service.arrival_ts}.to_json())
}
start_timeout(0.8,||fs.read_async("guardian-reexecution-fixture/data.json",fn(reply){gr_data=reply.text.parse_json() start_timeout(0.01,||gr_begin())}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request','guardian_store']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(400):
        if (jail/'guardian-reexecution-result.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'guardian-reexecution-result.json').read_bytes());base=json.loads((jail/'guardian-reexecution-fixture/data.json').read_bytes())['base'];checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('公开primitive身份为字符串无reserved scope',o['primitive_valid'])
    check('固定rail错过不平移且actualboarding始终unknown',o['early']['estimated_reexecution_arrival_ts']==base+1920==o['late']['estimated_reexecution_arrival_ts'] and o['late']['reexecution_status']=='invalid' and len(o['late']['missed_fixed_services'])==1 and all(o[k]['boarding_status']=='unknown' and o[k]['actual_journey_status']=='unknown' for k in ('early','late','absent','underway')))
    check('原起点缺位置有progress核验范围明确不同',o['late']['origin_matches'] and not o['absent']['origin_matches'] and o['absent']['reexecution_status']=='unknown' and o['underway']['reexecution_status']=='unknown' and o['underway']['progress_scope']=='remaining_journey_not_identified')
    before=json.loads(json.dumps(o['goal_before']));after=json.loads(json.dumps(o['goal_after']));before['selected_route'].pop('steps_cache',None);after['selected_route'].pop('steps_cache',None)
    business_unchanged=before==after
    check('旧source quote deadline固定发到时刻原样不改',business_unchanged and o['original_source_ts']==o['original_quote_ts']==base and o['original_deadline']==base+3600 and o['original_departure']==base+300 and o['original_arrival']==base+1800)
    check('partial小计差200整程nil仅两完整整程200',o['partial']['queried_legs_subtotal_delta_cents']==200 and o['partial']['full_journey_delta_cents'] is None and o['partial']['comparison_scope']=='queried_legs_only' and o['full']['full_journey_delta_cents']==200 and o['remaining']['full_journey_delta_cents'] is None and o['remaining']['queried_legs_subtotal_delta_cents'] is None)
    check('生产snapshot与proposal公开同范围且未批准不写goal',o['snapshot']['original_plan_reexecution']['boarding_status']=='unknown' and o['snapshot']['goal']['selected_route']['original_plan_reexecution']['source_ts']==base and o['proposal']['success'] and o['proposal']['proposal']['base_version']==4 and o['proposal']['proposal']['goal']['version']==5 and o['proposal']['proposal']['cost_delta_cents'] is None and o['proposal']['proposal']['cost_comparison']['queried_legs_subtotal_delta_cents']==200 and not o['stale_confirm_result'] and o['stores']==0 and business_unchanged and o['snapshot']['current_check']['status']=='unknown' and o['snapshot']['goal']['state']=='active')
    check('未确认progress不等于尚未出发且不升级实际目标为invalid',o['late']['progress_scope']=='no_confirmed_progress' and o['late']['origin_matches'] and o['late']['reexecution_status']=='invalid' and o['late']['actual_journey_status']=='unknown' and o['late']['boarding_status']=='unknown' and o['snapshot']['current_check']['status']=='unknown' and o['snapshot']['goal']['state']=='active' and o['stores']==0)
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'cache_boundary':'前后业务goal结构等值仅排除生产route_summary_steps添加的steps_cache；不把派生cache当业务目标修改。','boundary':'代表性合成saved selected_legs固定rail+旧quote和partial/full控制；生产helper/snapshot/propose/旧version确认；guardian_store仅计数拒写，未验证真实批准持久化或完整原32矩阵。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
