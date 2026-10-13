"""用已记录的真实跨城高德几何验证分批解析和原生详情/地图入口。"""
import hashlib
import json
import time
from pathlib import Path

FIXTURE=r'''
fn agent_pump(token){}
fn load_map_slot(slot,candidate){}
let geometry_checks=[] let geometry_route=nil
fn geometry_check(name,passed){geometry_checks.push({name:name passed:passed})}
fn geometry_finish(){fs.write("harness-smoke.json",{checks:geometry_checks}.to_json())}
fn agent_tool_result(result){
 geometry_check("真实跨城get_route返回完整目录",result.success && result.route.map_paths.len()==geometry_expected.len())
 let paths=map_geometry(geometry_route).paths let preserved=paths.len()==geometry_expected.len()
 for index line in paths {if line!=geometry_expected[index] {preserved=false}}
 geometry_check("所有17636点按原供应商折线无损保存",preserved)
 let cache=geometry_route.map_geometry_cache let catalog=geometry_route.map_paths_cache
 ensure_map_catalog(geometry_route,||{
  geometry_check("重复详情复用同一几何与目录缓存",geometry_route.map_geometry_cache==cache && geometry_route.map_paths_cache==catalog)
  let tiny={id:"merge-boundary" segments:[{polyline:geometry_long} {polyline:geometry_tail} {polyline:"181,22;114,22"}]}
  ensure_map_catalog(tiny,||{
   geometry_check("跨批共享端点仅去一份且非法折线遗漏",tiny.map_geometry_cache.paths.len()==1 && tiny.map_geometry_cache.paths[0]==geometry_merged && tiny.map_geometry_cache.omitted==2)
   let old={id:"cancelled-geometry" segments:geometry_segments}
   let old_called=false ensure_map_catalog(old,||{old_called=true})
   run_id+=1 map_geometry_jobs={}
   start_timeout(0.05,||{
    geometry_check("新查询取消旧几何任务和回调",!old_called && route_get(old,"map_geometry_cache")==nil)
    interface_revision+=1
    mount_ui_blocks({blocks:[{id:"geometry" source:"View{width:Fill height:Fit map := AutoNaviMapView{width:Fill height:240}}"}]},run_id,interface_revision)
    start_timeout(0.5,||{
     let slot={id:"geometry-map" block_id:"geometry" widget:"map" generation:map_generation target_id:geometry_route.id path_indices:nil state:"ready" status:"fixture"}
     map_slots[slot.id]=slot fit_map_slot(slot,geometry_route)
     geometry_check("实际原生地图fit使用缓存bounds不重新解析大折线",slot.state=="ready" && block_by_id("geometry").handle.diagnostics()=="" && geometry_route.map_paths_cache[0].bounds!=nil)
     geometry_finish()
    })
   })
  })
 })
}
start_timeout(1,||{
 run_id+=1 agent_active=true constraints={budget_cents:20000} arrive_by=time_now()+14400
 geometry_route=route_candidate("recorded-cross-city","public_transit",6000,1000,time_now(),time_now(),"114.029506,22.609878","114.029506,22.609878",true,geometry_segments)
 geometry_route.requested_origin="113.269097,22.988344" assign_candidate_ref(geometry_route) candidates=[geometry_route]
 agent_calls=[{id:"geometry-get" function:{name:"get_route" arguments:{id:geometry_route.id}.to_json()}}] agent_call_index=0
 agent_schedule_next(run_id)
})
'''

def source(original):
    data=json.loads((Path(__file__).resolve().parents[1]/'build/research/rail-integration/amap/v5-gzsz.json').read_text())
    segments=[s for t in data['response']['route']['transits'] for s in t['segments']]
    paths=[]
    for segment in segments:
        lines=[]
        if 'polyline' in segment: lines.append(segment['polyline'])
        for part in ('walking','taxi'):
            value=segment.get(part,{})
            if 'polyline' in value:lines.append(value['polyline'])
            lines.extend(step['polyline'] for step in value.get('steps',[]) if 'polyline' in step)
        lines.extend(line['polyline'] for line in segment.get('bus',{}).get('buslines',[]) if 'polyline' in line)
        for line in lines:
            if isinstance(line,dict):line=line['polyline']
            if paths and paths[-1].split(';')[-1]==line.split(';')[0]:paths[-1]+=';'+line.split(';',1)[1]
            else:paths.append(line)
    def literal(value):return json.dumps(json.dumps(value,ensure_ascii=False),ensure_ascii=False)+'.parse_json()'
    long=';'.join(f'113.{100000+i},23.1' for i in range(240))
    tail=long.split(';')[-1]+';113.2,23.2'
    prelude='\nlet geometry_segments='+literal(segments)+'\nlet geometry_expected='+literal(paths)+'\nlet geometry_long='+json.dumps(long)+'\nlet geometry_tail='+json.dumps(tail)+'\nlet geometry_merged='+json.dumps(long+';113.2,23.2')+'\n'
    return original.replace('fn agent_pump(', 'fn product_agent_pump(',1).replace('fn agent_tool_result(', 'fn product_agent_tool_result(',1).replace('fn load_map_slot(', 'fn product_load_map_slot(',1)+prelude+FIXTURE

def run(w,jail,original,injected):
    report=None
    for _ in range(600):
        try:report=json.loads((jail/'harness-smoke.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):pass
        if report:break
        time.sleep(.1)
    assert report,str(w/'native.log')
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),model_called=False,recorded_real_amap_geometry=True,provider_called=False,native_errors=[x for x in (w/'native.log').read_text().splitlines() if '[E]' in x])
    (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert not report['native_errors'],report['native_errors']
    assert all(x['passed'] for x in report['checks']),report
    print('PASS: '+str(len(report['checks']))+'项跨城几何原生检查；'+str(w/'report.json'))
