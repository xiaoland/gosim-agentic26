"""online9真实比较候选及官方入口Route的用途投影合同；零网络。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/research/journey-guardian/current-online-9'
ROUTE_FIELDS={'id','mode','kind','completion_status','arrival_scope','price_label','duration_label','arrival_label','cost','assessment'}
COST_FIELDS={'amount_cents','known_subtotal_cents','currency','coverage','unknown_reasons'}
def prepare(jail):
    original=json.loads((BASE/'tool-result-91-private.json').read_bytes());entry=json.loads((BASE/'tool-result-128-private.json').read_bytes())['routes']
    assert len(original['routes'])==2 and all(r['arrival_scope']=='queried_endpoint_only' for r in original['routes'])
    assert len(entry)==1 and entry[0]['arrival_scope']=='requested_routing_entry'
    d=Path(jail)/'compare-contract-fixture';d.mkdir()
    (d/'original.json').write_text(json.dumps({'comparison':original,'entry_routes':entry},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let cp_original=nil let cp_routes=[] let cp_entry=[] let cp_before=""
fn cp_next(index){if index>=cp_original.comparison.routes.len(){cp_extra(0) return}
 cp_routes.push(comparison_route_index(cp_original.comparison.routes[index])) start_timeout(0.01,||cp_next(index+1))
}
fn cp_extra(index){if index>=cp_original.entry_routes.len(){fs.write("compare-contract-result.json",{routes:cp_routes entry_routes:cp_entry comparison:comparison_summary(cp_original.comparison.routes) original_unchanged:cp_original.to_json()==cp_before}.to_json()) return}
 cp_entry.push(comparison_route_index(cp_original.entry_routes[index])) start_timeout(0.01,||cp_extra(index+1))
}
start_timeout(0.8,||fs.read_async("compare-contract-fixture/original.json",fn(reply){cp_original=reply.text.parse_json() cp_before=cp_original.to_json() cp_next(0)}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(500):
        if (jail/'compare-contract-result.json').exists():break
        time.sleep(.02)
    fixture=json.loads((jail/'compare-contract-fixture/original.json').read_bytes());old=fixture['comparison']
    actual=json.loads((jail/'compare-contract-result.json').read_bytes());before=old['routes']+fixture['entry_routes'];after=actual['routes']+actual['entry_routes']
    checks=[{'name':'全部原比较身份顺序与后续entry控制身份保留输入未改','passed':[r['id'] for r in actual['routes']]==[r['id'] for r in old['routes']] and [r['id'] for r in actual['entry_routes']]==[r['id'] for r in fixture['entry_routes']] and actual['original_unchanged']},
            {'name':'partial及官方入口的显示标签与完成到达范围逐值守恒','passed':all(all(a[k]==b[k] for k in ROUTE_FIELDS-{'cost','assessment'}) for a,b in zip(after,before))},
            {'name':'整程金额未知与已知小计覆盖原因及完整当前assessment守恒','passed':all(a['cost']=={k:b['cost'][k] for k in COST_FIELDS} and a['assessment']==b['assessment'] for a,b in zip(after,before)) and all(a['cost']['amount_cents'] is None for a in after)},
            {'name':'比较只公开用途字段而完整源数据仍含端点时刻与计价依据','passed':all(set(a)==ROUTE_FIELDS and set(a['cost'])==COST_FIELDS for a in after) and any('destination_access' in b and 'queried_endpoint_arrival_ts' in b and 'basis' in b['cost'] for b in before)},
            {'name':'比较摘要仍以原完整Routes计算保持原回执','passed':actual['comparison']==old['comparison']}]
    updated=dict(old,routes=actual['routes']);(work/'compare91-original-private.json').write_text(json.dumps(old,ensure_ascii=False,indent=2));(work/'compare91-projected-private.json').write_text(json.dumps(updated,ensure_ascii=False,indent=2));(work/'entry128-projection-private.json').write_text(json.dumps({'original':fixture['entry_routes'],'projected':actual['entry_routes']},ensure_ascii=False,indent=2))
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'bytes':{'old_compare':len(json.dumps(old,ensure_ascii=False,separators=(',',':')).encode()),'new_compare':len(json.dumps(updated,ensure_ascii=False,separators=(',',':')).encode())},'route_ids':[r['id'] for r in actual['routes']],'entry_control_ids':[r['id'] for r in actual['entry_routes']],'model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'boundary':'online9原compare91全部两partial候选与后续entry128 Route直入生产comparison_route_index；未把后续entry混入原compare91。原完整summary保留，不恢复Route graph/会话或执行get_route/供应商。导出原/新回执仅供受控变量对照，不证明模型解释改善。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
