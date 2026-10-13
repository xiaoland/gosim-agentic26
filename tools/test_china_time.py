"""固定北京时间与真实553条12306班次解析回归，不请求模型或交通供应商。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def prepare(jail):
    folder=Path(jail)/'china-time-fixture';folder.mkdir()
    raw=ROOT/'build/research/rail-integration/case27-provider/IZQ-IOQ-raw.json'
    (folder/'rail.json').write_bytes(raw.read_bytes())
    route=json.loads((ROOT/'build/research/rail-integration/e2e/round30/route2_33-private.json').read_bytes())
    (folder/'service.json').write_text(json.dumps(route['legs'][1]['rail_service'],ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let ct_raw=nil let ct_service=nil let ct_index=0 let ct_parsed=0 let ct_state=nil let ct_rows=[]
fn ct_batch(){let until=ct_index+8 if until>ct_raw.data.result.len(){until=ct_raw.data.result.len()}
 while ct_index<until {let service=rail_parse_service(ct_raw.data.result[ct_index],ct_raw.data.map,"2026-10-12",1791738423.562124) ct_index+=1 if service!=nil {ct_parsed+=1 rail_accept_service(ct_state,service)}}
 if ct_index<ct_raw.data.result.len(){start_timeout(0.01,||ct_batch())} else {start_timeout(0.01,||ct_finish())}
}
fn ct_finish(){
 let from={longitude:113.269 latitude:22.988 city_metadata:{citycode:"020" adcode:"440113"}}
 let to={longitude:113.814 latitude:22.624 city_metadata:{citycode:"0755" adcode:"440303"}}
 fs.write("china-time-result.json",{received_epoch:1791738423.562124 received_label:guardian_deadline(1791738423.562124) deadline_epoch:1791738423.562124+50400 deadline_label:guardian_deadline(1791738423.562124+50400) transit_params:transit_leg_params(from,to,0,1791738423.562124) received_date:rail_date(1791738423.562124) midnight_before:guardian_deadline(1791729672.456025) midnight_after:guardian_deadline(1791744072.456025) parsed:ct_parsed input_count:ct_raw.data.result.len() services:ct_state.services other_pairs:ct_state.other_pairs fixed_service:rail_service_labels(ct_service)}.to_json())
}
start_timeout(0.8,||fs.read_async("china-time-fixture/rail.json",fn(result){if !result.success {return} ct_raw=result.text.parse_json()
 fs.read_async("china-time-fixture/service.json",fn(reply){if !reply.success{return} ct_service=reply.text.parse_json()
 run_id+=1 arrive_by=1791738423.562124+50400 rail_services={} rail_service_sequence=0
 ct_state={from_code:"IZQ" to_code:"IOQ" earliest:1791738423.562124 other_pairs:{} services:[]}
 start_timeout(0.01,||ct_batch())
 })
}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(1000):
        if (jail/'china-time-result.json').exists():break
        time.sleep(.02)
    result=json.loads((jail/'china-time-result.json').read_bytes())
    service=json.loads((jail/'china-time-fixture/service.json').read_bytes())
    checks=[
        {'name':'31真实received与14h期限正确且epoch不变','passed':result['received_epoch']==1791738423.562124 and result['deadline_epoch']==1791738423.562124+50400 and result['received_label']=='2026-10-12 01:07（北京时间）' and result['deadline_label']=='2026-10-12 15:07（北京时间）'},
        {'name':'高德transit参数固定北京时间01:07与正确日期','passed':'&date=2026-10-12&time=01:07' in result['transit_params'] and result['received_date']=='2026-10-12'},
        {'name':'真实553记录生产parser不全拒且IZQ到IOQ晨班在14h窗口','passed':result['input_count']==553 and result['parsed']>0 and len(result['services'])>0 and all(s['departure_ts']>=result['received_epoch'] and s['departure_ts']<=result['deadline_epoch'] for s in result['services']) and any(s['arrival_ts']<=result['deadline_epoch'] and s['departure_label'].startswith('2026-10-12 06:') for s in result['services'])},
        {'name':'跨午夜标签保持10月11日22:41到12日02:41','passed':result['midnight_before']=='2026-10-11 22:41（北京时间）' and result['midnight_after']=='2026-10-12 02:41（北京时间）'},
        {'name':'真实固定班次全部原字段epoch保持且arrival/date正确','passed':all(result['fixed_service'].get(k)==v for k,v in service.items()) and result['fixed_service']['departure_label']=='2026-10-12 07:50（北京时间）' and result['fixed_service']['arrival_label']=='2026-10-12 09:09（北京时间）'},
    ]
    report={'checks':checks,'product_source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':{k:v for k,v in result.items() if k not in ['services','other_pairs','fixed_service','transit_params']},'window_service_count':len(result['services']),'other_pair_count':len(result['other_pairs']),'model_requested':False,'provider_requested':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'fixture_boundary':'生产时间helper和真实case27录制553班次，分8条timer解析；不重新查询12306或交通供应商。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in checks),str(work/'report.json')
