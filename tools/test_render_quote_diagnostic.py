"""第37轮代码态非法转义引号的原稿反馈；仅离线生产render工具入口。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEQUENCES=(253,276,287,298)
EXPECTED_SOURCE_LINES=(6,6,7,3)
EXPECTED_SOURCE_COLUMNS=(32,32,32,58)
# 由锁定runtime诊断字串和应用公开hint契约确定后填入，不先猜文案。
DIAGNOSTIC_MARKER='unexpected escaped quote outside string'
HINT_MARKER='source是已解码的Splash源码'
HINT_EXAMPLE='show_block("route_detail")'

def prepare(jail):
    base=ROOT/'build/research/rail-integration/e2e/round37';d=Path(jail)/'quote-fixture';d.mkdir()
    for index,seq in enumerate(SEQUENCES):
        raw=(base/f'render_routes-{seq}-private.json').read_bytes()
        value=json.loads(raw);assert isinstance(value['source'],str)
        (d/f'case-{index}.json').write_bytes(raw)
    (d/'boundary.json').write_text(json.dumps({'sequences':SEQUENCES,'expected_source_lines':EXPECTED_SOURCE_LINES,'expected_source_columns':EXPECTED_SOURCE_COLUMNS,'unchanged_original_sources':True}))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
let qd_cases=[] let qd_index=0 let qd_replies=[] let qd_pumps=0 let qd_sources=[]
fn qd_submit(){let value=if qd_index<4 {qd_cases[qd_index]} else {{source:"Label{text:\"合法原生字符串\"}"}}
 qd_sources.push(value.source)
 let call={id:"quote-case-"+qd_index function:{name:"render_routes" arguments:value.to_json()}}
 agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] active_tool=nil agent_tool_job=nil agent_result_pending=nil decisions=[] agent_schedule_next(run_id)
}
fn agent_pump(token){if token!=run_id{return} qd_pumps+=1 let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}} qd_replies.push(reply)
 fs.write("quote-progress.json",{test_case:qd_index pumps:qd_pumps replies:qd_replies}.to_json())
 qd_index+=1 if qd_index<5 {start_timeout(0.05,||qd_submit())} else {fs.write("quote-result.json",{replies:qd_replies pumps:qd_pumps sources:qd_sources}.to_json())}
}
fn qd_load(index){if index>=4 {run_id+=1 agent_active=true phase="running" candidates=[] trip_records=[] trip_selected_id=nil trip_replay=false guardian_mode=false ui_blocks=[] source_records=[] route_nodes={} qd_submit() return}
 fs.read_async("quote-fixture/case-"+index+".json",fn(reply){qd_cases.push(reply.text.parse_json()) start_timeout(0.01,||qd_load(index+1))})
}
start_timeout(0.8,||qd_load(0))
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    assert DIAGNOSTIC_MARKER and HINT_MARKER,'runtime诊断和公开hint字串尚未确定，禁止启动未定契约'
    for _ in range(600):
        if (jail/'quote-result.json').exists():break
        time.sleep(.02)
    result=json.loads((jail/'quote-result.json').read_bytes());checks=[]
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    for i,seq in enumerate(SEQUENCES):
        reply=result['replies'][i];text=json.dumps(reply,ensure_ascii=False)
        raw=json.loads((jail/f'quote-fixture/case-{i}.json').read_bytes())['source']
        check(f'原稿{seq}真实非法引号诊断和短hint并继续工具链',not reply['success'] and DIAGNOSTIC_MARKER in text and f'fragment:{EXPECTED_SOURCE_LINES[i]}:{EXPECTED_SOURCE_COLUMNS[i]}:' in text and HINT_MARKER in text and '字符串外直接写'+HINT_EXAMPLE+'，' in reply['error'] and result['sources'][i]==raw)
    legal=result['replies'][4]
    check('合法原生control成功且不附非法引号hint',legal['success'] and legal['notified'] and HINT_MARKER not in json.dumps(legal,ensure_ascii=False) and result['pumps']==5)
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':result,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'四真实37 source JSON解码后值未改；仅render_routes生产工具入口，无完整路线图或供应商；合法control明确测试。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(x['passed'] for x in checks),str(work/'report.json')
