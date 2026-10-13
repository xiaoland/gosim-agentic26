"""大私有trace事件的原生分片与CLI重组回归；不调用模型或交通供应商。"""
import hashlib
import json
import time
from pathlib import Path
import agent
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'build/research/rail-integration/e2e/round33'

def prepare(jail):
    directory = Path(jail) / 'trace-payload-fixture'
    directory.mkdir()
    body = (ROOT/'build/research/rail-integration/case36-contract/reconstructed-step12-private.json').read_bytes()
    (directory / 'body.json').write_bytes(body)
    pieces=[]
    text=body.decode()
    while text:
        piece=text[:65536];text=text[65536:];pieces.append(piece)
    for i,piece in enumerate(pieces):(directory/f'body-part-{i}.txt').write_text(piece)
    (directory/'body-count.json').write_text(json.dumps({'count':len(pieces)}))
    (directory/'source.splash').write_bytes((EVIDENCE/'actual-render-source-private.splash').read_bytes())

FIXTURE = r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let tp_body="" let tp_dispatches=0 let tp_body_count=0
fn tp_host(service,body,done){tp_dispatches+=1 return "isolated-no-network"}
fn tp_read(path,done){fs.read_async(path,fn(result){if result.success {done(result.text)} else {fs.write("trace-payload-error.json",{error:result.error}.to_json())}})}
fn tp_begin(){
 trace_enabled=false trace_state={session:"trace-payload-fixture" instance:"vm-1" directory:"trace-payload-output" seq:0 written_seq:0 segment:0 segment_bytes:0 run:run_id incomplete:false keys:[]}
 tp_read("trace-payload-fixture/body-count.json",fn(text){tp_body_count=text.parse_json().count tp_load_body(0)})
}
fn tp_load_body(index){if index>=tp_body_count {start_timeout(0.01,||{
 let body=tp_body.parse_json() agent_active=true step_count=11 let record=agent_request_record(run_id)
 minimax_request("",body.messages,body.tools,run_id,record,fn(reply){})
 start_timeout(0.5,||tp_render())
}) return}
 tp_read("trace-payload-fixture/body-part-"+index+".txt",fn(text){tp_body+=text start_timeout(0.01,||tp_load_body(index+1))})
}

fn tp_render(){tp_read("trace-payload-fixture/source.splash",fn(rendered){start_timeout(0.01,||{
 fs.write("trace-payload-render-source.txt",rendered)
 trace_emit_run("render_source",{block_id:"actual-round33" revision:1 source:rendered},"trace-payload-render",run_id)
 start_timeout(0.4,||{
  trace_emit_run("fixture_small",{label:"小事件兼容"},nil,run_id)
  start_timeout(0.3,||fs.write("trace-payload-done.json",{dispatches:tp_dispatches seq:trace_state.seq written_seq:trace_state.written_seq incomplete:trace_state.incomplete}.to_json()))
 })
})})}

start_timeout(0.8,||tp_begin())
'''

def source(original):
    for name in ['trace_initialize', 'agent_pump', 'amap_request', 'trip_load']:
        original = original.replace(f'fn {name}(', f'fn product_{name}(', 1)
    needle='record.host_request_id=host.request("model.chat",body,fn(reply){'
    assert original.count(needle)==1
    original=original.replace(needle,'record.host_request_id=tp_host("model.chat",body,fn(reply){',1)
    return original + '\n' + FIXTURE

def run(work, jail, original, injected):
    for _ in range(800):
        if (jail/'trace-payload-done.json').exists():break
        time.sleep(.02)
    done=json.loads((jail/'trace-payload-done.json').read_bytes())
    directory=jail/'trace-payload-output'
    status=json.loads((directory/'status.json').read_bytes())
    events=agent.trace_events(directory,status,'trace-payload-fixture','vm-1',{}, {})
    def data(kind):return json.loads(next(e['data'] for e in events if e['event']==kind))
    checks=[]
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    body=json.loads((jail/'trace-payload-fixture/body.json').read_bytes())
    check('生产minimax_request原messages/tools派发恰一次无网络',done['dispatches']==1 and json.loads(data('model_request')['body'])==body)
    check('真实seq300 source原字段完整字节等值',data('render_source')['source']==(jail/'trace-payload-render-source.txt').read_text())
    check('小事件旧JSONdata兼容',data('fixture_small')=={'label':'小事件兼容'})
    lines=[json.loads(l) for p in sorted(directory.glob('segment-*.jsonl')) for l in p.read_text().splitlines()]
    refs=[e for e in lines if 'trace_fields' in e]
    modelref=next(e for e in refs if e['event']=='model_request')['trace_fields'][0]
    sourceref=next(e for e in refs if e['event']=='render_source')['trace_fields'][0]
    check('超过1MiB逐入口有界片且旧小于1MiB单原字段兼容',len(refs)==2 and modelref['bytes']>1048576 and len(modelref['parts'])>4 and all(0<p['bytes']<=262144 for p in modelref['parts']) and len(sourceref['parts'])==1 and all(p.stat().st_size<65536 for p in directory.glob('segment-*.jsonl')))
    check('完整写入后状态recording且派发一次',not done['incomplete'] and status['state']=='recording' and done['written_seq']==done['seq'] and done['dispatches']==1)
    ref=next(e for e in refs if e['event']=='model_request');missing=directory/ref['trace_fields'][0]['parts'][2]['name'];saved=missing.read_bytes()
    try:
        missing.unlink();broken=dict(status,state='recording');got=agent.trace_events(directory,broken,'trace-payload-fixture','vm-1',{}, {})
        check('缺中间原字段片明确incomplete不返回残缺事件',broken['state']=='incomplete' and not any(e['event']=='model_request' for e in got))
    finally:missing.write_bytes(saved)
    report={'checks':checks,'product_source_sha256':hashlib.sha256(original.encode()).hexdigest(),'bytes':{'model_body':(jail/'trace-payload-fixture/body.json').stat().st_size,'raw_fields':[e['trace_fields'][0]['bytes'] for e in refs],'jsonl_total':sum(p.stat().st_size for p in directory.glob('segment-*.jsonl'))},'fixture_boundary':'round36 step12重建非缺失原请求；round33 seq300真实source444087B用于旧单字段兼容；无现场liveheap复现，不宣称host真实网络dispatch容量验证。','model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l]}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in checks),str(work/'report.json')
