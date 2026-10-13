"""大envelope上scrub快速跳过与原split算法的原生等值检查。"""
import hashlib
import json
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def prepare(jail):
    folder=Path(jail)/'trace-scrub-fixture';folder.mkdir()
    original=ROOT/'build/research/rail-integration/e2e/round30/reconstructed-step12-request-private.json'
    (folder/'body.json').write_bytes(original.read_bytes())

FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let ts_envelope=nil let ts_checks=[] let ts_input_bytes=0
fn ts_original(text,keys){
 for key in keys {if key.is_string() && key!="" {
  let parts=text.split(key) let replaced=""
  for index part in parts {if index>0 {replaced+="[REDACTED]"} replaced+=part}
  text=replaced
 }} return text
}
fn ts_case(index){
 let key="fixture_scrub_7ae2/key value" let keys=[key key.url_encode()]
 let text=if index==0 {ts_envelope} elif index==1 {ts_envelope+key+"中间"+key} else {ts_envelope+key.url_encode()+"中间"+key.url_encode()}
 let actual=trace_scrub(text,keys) let expected=ts_original(text,keys)
 let name=if index==0 {"大envelope无key原字符串保持且等值原split"} elif index==1 {"两次合成key完整脱敏等值原split"} else {"URL编码key配置形式完整脱敏等值原split"}
 ts_checks.push({name:name passed:actual==expected && if index==0 {actual==text} else {actual.search(key)<0 && actual.search(key.url_encode())<0 && actual.search("[REDACTED]")>=0}})
 if index<2 {start_timeout(0.01,||ts_case(index+1))} else {fs.write("trace-scrub-report.json",{checks:ts_checks input_bytes:ts_input_bytes}.to_json())}
}
start_timeout(0.8,||fs.read_async("trace-scrub-fixture/body.json",fn(result){if !result.success {return}
 let data={step:12 service:"minimax" body:result.text}
 start_timeout(0.01,||{
  ts_envelope={v:1 session:"trace-scrub-fixture" instance:"vm-1" run:2 seq:227 event:"model_request" at:time_now() call_id:nil data:data.to_json()}.to_json()
  ts_input_bytes=ts_envelope.len() start_timeout(0.01,||ts_case(0))
 })
}))
'''

def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(500):
        if (jail/'trace-scrub-report.json').exists():break
        time.sleep(.02)
    report=json.loads((jail/'trace-scrub-report.json').read_bytes())
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_requested=False,provider_requested=False,native_errors=[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],fixture_boundary='仅真实step12重建body生成的大envelope；凭据匹配只用固定合成字符串，不读真实key。')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert report['input_bytes']>1048576 and all(c['passed'] for c in report['checks']),str(work/'report.json')
