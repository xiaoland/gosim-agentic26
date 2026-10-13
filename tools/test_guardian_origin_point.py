"""真实online2 position_record经纬度形状的原计划重执行起点匹配。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=ROOT/'build/research/journey-guardian/current-online-2';saved=json.loads((base/'saved-full-snapshot-private.json').read_bytes())['data'];old=saved['goal'];route=old['selected_route'];record=json.loads(json.loads((base/'tool_result-32-private.json').read_bytes())['result'])['check'];origin=saved['snapshot']['facts']['origin']
    goal={'selected_route':{'id':route['id'],'source_ts':route['source_ts'],'departure_ts':route['departure_ts'],'actual_origin':route['actual_origin'],'duration_seconds':route['duration_seconds'],'selected_legs':[{'mode':l['mode'],'duration_seconds':l['duration_seconds'],'rail_service':l.get('rail_service')} for l in route['selected_legs']]},'progress':old['progress'],'spent_cents':old['spent_cents'],'deadline_ts':old['deadline_ts']}
    (Path(jail)/'origin-point-fixture.json').write_text(json.dumps({'goal':goal,'origin':origin,'at':record['checked_at']},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
start_timeout(0.8,||fs.read_async("origin-point-fixture.json",fn(reply){let data=reply.text.parse_json() let goal=data.goal let before=goal.to_json()
 let actual=guardian_reexecution(goal,data.at,data.origin) let missing=guardian_reexecution(goal,data.at,{name:"missing-coordinate"})
 let point=coord_text(data.origin) let legacy=guardian_reexecution(goal,data.at,{location:point}) let text=guardian_reexecution(goal,data.at,point)
 fs.write("origin-point-result.json",{actual:actual missing:missing legacy:legacy text:text unchanged:goal.to_json()==before}.to_json())
}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(200):
        if (jail/'origin-point-result.json').exists():break
        time.sleep(.02)
    o=json.loads((jail/'origin-point-result.json').read_bytes());a=o['actual'];m=o['missing'];checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('真实无location经纬度起点约8.5m且仅counterfactual invalid',8<a['original_origin_gap_m']<9 and a['origin_matches'] and a['reexecution_status']=='invalid' and any('S4831' in s for s in a['missed_fixed_services']) and a['actual_journey_status']=='unknown' and a['boarding_status']=='unknown')
    check('缺经纬度保持unknown且旧location/String兼容',m['original_origin_gap_m'] is None and not m['origin_matches'] and m['reexecution_status']=='unknown' and o['legacy']['origin_matches'] and o['text']['origin_matches'] and abs(o['legacy']['original_origin_gap_m']-a['original_origin_gap_m'])<.001 and o['legacy']['original_origin_gap_m']==o['text']['original_origin_gap_m'])
    check('原goal时刻source与fixedrail核心未改',o['unchanged'])
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':o,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'实际online2 facts.origin经纬度无location、原goal.actual_origin与S4831 selected_legs固定时刻；固定原report32 checked_at；薄goal仅时刻/身份/范围字段，不复制geometry/大图/个人HOME，不重跑规划或renderer。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
