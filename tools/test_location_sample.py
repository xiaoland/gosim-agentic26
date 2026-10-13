"""RC6官方freshfix字段的应用消费合同，所有定位与高德请求仅本地截获。"""
import hashlib,json,time
from pathlib import Path

def prepare(jail):
    pass
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
let ls_stage=0 let ls_checks=[] let ls_requests=[] let ls_cancel_args=nil let ls_callback=nil let ls_failures=[] let ls_completed=0 let ls_amap=[] let ls_fix=nil
fn ls_check(name,value){ls_checks.push({name:name passed:value}) fs.write("location-sample-progress.json",{stage:ls_stage checks:ls_checks}.to_json())}
fn location_dispatch(args,done){ls_requests.push(args) ls_callback=done return "fixture-location-request"}
fn location_cancel_dispatch(args){ls_cancel_args=args}
fn fail_task(text){ls_failures.push(text) product_fail_task(text)}
fn amap_request(path,params,token,done){
 ls_amap.push({path:path params:params})
 if path=="/v3/assistant/coordinate/convert" {start_timeout(0.01,||done({locations:"114.128888,22.565555"}))}
 elif path=="/v3/geocode/regeo" {start_timeout(0.01,||done({regeocode:{addressComponent:{country:"中国" city:"深圳市" citycode:"0755" adcode:"440303" province:"广东省"}}}))}
}
fn ls_reset(){run_id+=1 agent_active=true position_record=nil ls_requests=[] ls_failures=[] ls_completed=0 ls_amap=[] ls_callback=nil source_snapshots=[] source_records=[]}
fn ls_done(){ls_completed+=1}
fn ls_normal(){ls_stage=0 ls_reset()
 ls_fix={latitude:22.567891234 longitude:114.123456789 accuracy_m:15 timestamp:time_now() source:"platform" freshness:"fresh"}
 live_position(run_id,||{ls_done()
  let args=ls_requests[0]
  ls_check("正式sample参数精确10s60s100m且fresh官方字段消费",ls_requests.len()==1 && args.timeout_ms==10000 && args.max_age_ms==60000 && args.max_accuracy_m==100 && ls_completed==1)
  ls_check("WGS84原始坐标精度timestamp保留并独立GCJ转换",position_record.original_longitude==ls_fix.longitude && position_record.original_latitude==ls_fix.latitude && position_record.sampled_at_unix==ls_fix.timestamp && position_record.accuracy_m==15 && position_record.original_coordinate_system=="WGS84" && position_record.longitude==114.128888 && position_record.latitude==22.565555)
  ls_check("生产转换与城市请求参数准确仅stub两次",ls_amap.len()==2 && ls_amap[0].path=="/v3/assistant/coordinate/convert" && ls_amap[0].params=="&locations=114.123457,22.567891&coordsys=gps&output=JSON" && ls_amap[1].path=="/v3/geocode/regeo" && ls_amap[1].params=="&location=114.128888,22.565555&extensions=base&radius=0&output=JSON" && position_record.city=="深圳市" && position_record.currency=="CNY")
  start_timeout(0.01,||ls_error())
 })
 ls_callback({is_ok:true data:ls_fix})
}
fn ls_error(){ls_stage=1 ls_reset() live_position(run_id,||ls_done()) ls_callback({is_ok:false error:"permission_denied"})
 ls_check("官方错误明确拒绝且不转换不完成",ls_failures.len()==1 && ls_completed==0 && ls_amap.len()==0 && position_record==nil)
 start_timeout(0.01,||ls_stale())
}
fn ls_stale(){ls_stage=2 ls_reset() live_position(run_id,||ls_done()) ls_callback({is_ok:true data:{latitude:22.567891234 longitude:114.123456789 accuracy_m:15 timestamp:time_now()-61 source:"platform" freshness:"fresh"}})
 ls_check("陈旧fix拒绝且不转换不完成",ls_failures.len()==1 && ls_completed==0 && ls_amap.len()==0 && position_record==nil)
 start_timeout(0.01,||ls_cancel())
}
fn ls_cancel(){ls_stage=3 ls_reset() ls_cancel_args=nil live_position(run_id,||ls_done()) let callback=ls_callback cancel_pending_location()
 callback({is_ok:true data:{latitude:22.567891234 longitude:114.123456789 accuracy_m:15 timestamp:time_now() source:"platform" freshness:"fresh"}})
 ls_check("sample.cancel空参数且迟到callback无副作用",ls_cancel_args!=nil && ls_cancel_args.to_json()=="{}" && pending_location==nil && ls_failures.len()==0 && ls_completed==0 && ls_amap.len()==0 && position_record==nil)
 fs.write("location-sample-report.json",{checks:ls_checks stage:ls_stage}.to_json())
}
start_timeout(0.8,||ls_normal())
'''

def source(original):
    assert 'host.request("location.sample", args, done)' in original
    assert 'host.request("location.sample.cancel", {},' in original
    for name in ['trace_initialize','trip_load','agent_pump','location_dispatch','location_cancel_dispatch','amap_request','fail_task']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(1000):
        if (jail/'location-sample-report.json').exists():break
        time.sleep(.02)
    path=jail/'location-sample-report.json'
    report=json.loads(path.read_bytes()) if path.exists() else {'incomplete':True,'last_progress':json.loads((jail/'location-sample-progress.json').read_bytes()) if (jail/'location-sample-progress.json').exists() else None}
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_requested=False,provider_requested=False,os_location_requested=False,os_permission_requested=False,native_errors=[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],fixture_boundary='合成官方freshfix，定位请求和转换/城市网络均截获；验证应用消费合同，不宣称系统定位已获授权或实测。')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not report.get('incomplete') and all(c['passed'] for c in report['checks']),str(work/'report.json')
