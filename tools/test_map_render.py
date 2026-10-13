"""第31轮原始几何的相机派生、一次真实静态图及取消边界。"""
import hashlib,json,math,re,time
from pathlib import Path
from urllib.parse import parse_qs
import agent
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    raw=json.loads((ROOT/'build/research/rail-integration/e2e/round31/map-request-242-private.json').read_bytes())
    q=parse_qs(raw['params'].lstrip('&'));paths=[p.split(':',1)[1] for p in q['paths'][0].split('|')]
    assert len(paths)==12 and len(paths[9].split(';'))==12117
    lon,lat=map(float,q['location'][0].split(','))
    folder=Path(jail)/'map-render-fixture';folder.mkdir()
    (folder/'geometry.json').write_text(json.dumps({'paths':paths,'camera':{'source_width':352,'source_height':240,'center_lon':lon,'center_lat':lat,'zoom':7}},separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let mr_raw=nil let mr_route=nil let mr_slot=nil let mr_stage=0 let mr_dispatches=0 let mr_http_dispatches=0 let mr_checks=[] let mr_zoom_params=nil
fn mr_check(name,value){mr_checks.push({name:name passed:value}) fs.write("map-render-progress.json",{stage:mr_stage checks:mr_checks}.to_json())}
fn dispatch_map_render(slot,candidate,token,request,target_id,geometry){
 if !map_slot_current(slot,token,request,target_id){return}
 mr_dispatches+=1
 if mr_stage==0 {fs.write("map-render-derived.json",{params:geometry.params paths:geometry.paths markers:geometry.markers}.to_json()) mr_http_dispatches+=1 product_dispatch_map_render(slot,candidate,token,request,target_id,geometry)}
 elif mr_stage==1 {mr_zoom_params=geometry.params fs.write("map-render-zoom.json",{params:geometry.params paths:geometry.paths}.to_json()) mr_check("zoom变化重新派生不复用旧显示params",mr_zoom_params!=fs.read("map-render-derived.json").parse_json().params) start_timeout(0.01,||mr_cancel())}
}
fn update_map_widget(slot){if route_get(slot,"block_id")=="map-probe" {product_update_map_widget(slot)}}
fn mr_poll(){
 if mr_slot.state=="error" {mr_check("真实静态图响应成功",false) fs.write("map-render-report.json",{checks:mr_checks http_dispatches:mr_http_dispatches status:mr_slot.status}.to_json()) return}
 if mr_slot.state!="ready" || mr_slot.loaded_request!=mr_slot.request {start_timeout(0.1,||mr_poll()) return}
 mr_check("真实静态图ready并实际Image提交",mr_slot.bytes!=nil && mr_slot.bytes.len()>0 && block_by_id("map-probe").handle.diagnostics()=="")
 fs.write("map-render-image-ready.json",{bytes:mr_slot.bytes.len() state:mr_slot.state}.to_json())
 start_timeout(2,||mr_zoom())
}
fn mr_test_slot(id,indices,zoom){let camera={source_width:352 source_height:240 center_lon:mr_raw.camera.center_lon center_lat:mr_raw.camera.center_lat zoom:zoom} let slot={id:id widget:"map" block_id:"fixture-only" target:mr_route.id target_id:mr_route.id generation:map_generation request:1 camera:camera path_indices:indices state:"loading" status:"" bytes:nil interactive:false} map_slots[id]=slot return slot}
fn mr_zoom(){mr_stage=1 let slot=mr_test_slot("zoom-fixture",[0 1 2 9],9) load_map_slot(slot,mr_route)}
fn mr_cancel(){mr_stage=2 let before=mr_dispatches let slot=mr_test_slot("cancel-fixture",[0 1 2 9],7) load_map_slot(slot,mr_route) slot.request+=1
 start_timeout(0.2,||{mr_check("旧request取消后不dispatch",mr_dispatches==before)
  let rejected=mr_test_slot("all12-fixture",nil,7) load_map_slot(rejected,mr_route)
  mr_check("nil选择12条明确失败且不HTTP",rejected.state=="error" && rejected.status.search("最多4")>=0 && mr_dispatches==before && mr_http_dispatches==1)
  fs.write("map-render-original-after.json",mr_route.map_geometry_cache.paths.to_json())
  fs.write("map-render-report.json",{checks:mr_checks http_dispatches:mr_http_dispatches dispatches:mr_dispatches}.to_json())
 })
}
start_timeout(0.8,||fs.read_async("map-render-fixture/geometry.json",fn(reply){if !reply.success{return} mr_raw=reply.text.parse_json() run_id+=1 candidates=[] trip_replay=false agent_active=false clear_generated()
 mr_route={id:"route31-map-fixture" kind:"mixed" segments:[] map_geometry_cache:{paths:mr_raw.paths omitted:0} map_paths_cache:[] requested_origin:nil requested_destination:nil}
 for index path in mr_raw.paths {mr_route.map_paths_cache.push({index:index point_count:path.split(";").len()})}
 candidates=[mr_route] ui_facts_json="{}" ui_facts_cached_revision=ui_facts_revision
 mount_ui_blocks({blocks:[{id:"map-probe" source:"map_image := Image{width:352 height:240}" height:280}]},run_id,interface_revision)
 start_timeout(0.5,||{
  mr_slot={id:"actual-map" widget:"body" block_id:"map-probe" target:mr_route.id target_id:mr_route.id generation:map_generation request:1 camera:mr_raw.camera path_indices:[0 1 2 9] state:"loading" status:"" bytes:nil interactive:false loaded_generation:-1 loaded_request:-1 status_widget:nil caption:""}
  mr_slot.widget="map_image"
  map_slots[mr_slot.id]=mr_slot start_timeout(0.2,||{load_map_slot(mr_slot,mr_route) mr_poll()})
 })
}))
'''
def source(original):
    for name in ['trace_initialize','trip_load','agent_pump','amap_request','dispatch_map_render','update_map_widget']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    captured=False
    for _ in range(1800):
        if (jail/'map-render-image-ready.json').exists() and not captured:
            match=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text())
            assert match,'remote listener missing'
            session={'port':int(match[1])}
            (work/'map-visible.png').write_bytes(agent.remote(session,'g?raw=1'))
            (work/'map-visible-snapshot.json').write_bytes(agent.remote(session,'snap?all=1'))
            captured=True
        if (jail/'map-render-report.json').exists():break
        time.sleep(.05)
    report=json.loads((jail/'map-render-report.json').read_bytes())
    geometry=json.loads((jail/'map-render-fixture/geometry.json').read_bytes())
    derived=json.loads((jail/'map-render-derived.json').read_bytes())
    orig=geometry['paths'];after=json.loads((jail/'map-render-original-after.json').read_bytes())
    def point(p):return tuple(map(float,p.split(',')))
    def px(p):
        lon,lat=p;scale=256*2**7
        return (scale*(lon+180)/360,scale*(1-math.log(math.tan(math.pi/4+math.radians(lat)/2))/math.pi)/2)
    def distance(a,b):return math.dist(px(a),px(b))
    max_error=0.;valid=True
    for i,line in zip([0,1,2,9],derived['paths']):
        source_points=list(map(point,orig[i].split(';')));shown=list(map(point,line.split(';')))
        valid &= all(abs(a-b)<=.000000501 for a,b in zip(source_points[0],shown[0])) and all(abs(a-b)<=.000000501 for a,b in zip(source_points[-1],shown[-1]))
        cursor=0;last=shown[0]
        for source_point in source_points:
            if cursor<len(shown) and all(abs(a-b)<=.000000501 for a,b in zip(source_point,shown[cursor])):
                last=shown[cursor];cursor+=1
            else:max_error=max(max_error,distance(source_point,last))
        valid &= cursor==len(shown)
    decimals=all(re.fullmatch(r'-?\d+\.\d{6},-?\d+\.\d{6}',p) for line in derived['paths'] for p in line.split(';'))
    report['checks'] += [{'name':'原12路径保留且四条独立端点顺序不跨gap','passed':orig==after and len(derived['paths'])==4 and valid}, {'name':'全部六位坐标且省略点Mercator径向误差不超1px','passed':decimals and max_error<=1}, {'name':'URI明显缩短且截图已捕获','passed':len(derived['params'].encode())<306464 and captured}]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),original_points=sum(len(p.split(';')) for p in orig),derived_points=sum(len(p.split(';')) for p in derived['paths']),params_bytes=len(derived['params'].encode()),max_omitted_error_pixels=max_error,screenshot_captured=captured,model_requested=False,traffic_requested=False,native_error_count=sum('[E]' in l for l in (work/'native.log').read_text().splitlines()),fixture_boundary='原31map请求解码为原始cache，非重新恢复供应商raw；仅一次生产静态图HTTP，其它派生只捕获无HTTP；实际截图仍需查看确认。')
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in report['checks']),str(work/'report.json')

def visible_source(original):
    """仅第二次获授权静态图：正常安装与持久原图片，不重跑派生矩阵。"""
    injected=source(original).replace('fn accept_map_slot(', 'fn product_accept_map_slot(', 1)
    injected=injected.replace('start_timeout(2,||mr_zoom())', 'fs.write("map-render-report.json",{checks:mr_checks http_dispatches:mr_http_dispatches dispatches:mr_dispatches}.to_json())')
    injected=injected.replace('candidates=[mr_route] ui_facts_json=', 'let now=time_now() trip_records=[{id:"map-trip" input:"静态图可见性验证" title:"原31路线地图" status:"completed" goal:nil snapshot:nil created_at:now updated_at:now}] trip_selected_id="map-trip" composer_open=false candidates=[mr_route] ui_facts_json=')
    injected+='''
fn accept_map_slot(slot,bytes,token,request,target_id,detail){
 if !map_slot_current(slot,token,request,target_id){return false}
 fs.write_bytes("map-render-downloaded.png",bytes)
 return product_accept_map_slot(slot,bytes,token,request,target_id,detail)
}
'''
    return injected

def visible_run(work,jail,original,injected):
    import struct
    for _ in range(1200):
        if (jail/'map-render-report.json').exists():break
        time.sleep(.05)
    report=json.loads((jail/'map-render-report.json').read_bytes())
    image=jail/'map-render-downloaded.png'
    png=image.read_bytes();assert png.startswith(b'\x89PNG\r\n\x1a\n')
    (work/'map-downloaded.png').write_bytes(png)
    time.sleep(1)
    match=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text());assert match
    session={'port':int(match[1])}
    snapshot=json.loads(agent.remote(session,'snap?all=1'))
    (work/'map-visible-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False))
    (work/'map-visible.png').write_bytes(agent.remote(session,'g?raw=1'))
    def nodes(value):
        if isinstance(value,dict):
            if value.get('i')=='map_image':yield value
            for v in value.values():yield from nodes(v)
        elif isinstance(value,list):
            for v in value:yield from nodes(v)
    images=list(nodes(snapshot));shown=[n for n in images if n.get('v',1)!=0 and n.get('r',[0,0,0,0])[2]>0 and n['r'][3]>0]
    previous=ROOT/'build/research/rail-integration/map-render-probe/map-dyyoznf3/private-state/home/apps/os.agentic26-navigation/map-render-derived.json'
    params=json.loads((jail/'map-render-derived.json').read_bytes())['params']
    report['checks'] += [
        {'name':'同原2437B派生参数且仅一请求','passed':params==json.loads(previous.read_bytes())['params'] and len(params.encode())==2437 and report['http_dispatches']==1},
        {'name':'响应立即真实write_bytes持久PNG352x240','passed':struct.unpack('>II',png[16:24])==(352,240)},
        {'name':'实际Phone视口Image有可见非零rect','passed':bool(shown)},
    ]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),params_bytes=len(params.encode()),downloaded_png_bytes=len(png),downloaded_png_sha256=hashlib.sha256(png).hexdigest(),image_rects=[{k:n[k] for k in ['i','ty','r','v'] if k in n} for n in images],runtime_mode='desktop Android phone mode (not physical Android device)',model_requested=False,traffic_requested=False,native_error_count=sum('[E]' in l for l in (work/'native.log').read_text().splitlines()),fixture_boundary='获单独授权的第二次同参数静态图，仅normal具名Image安装/下载落盘/截图；未重跑zoom和取消矩阵。',screenshot_viewed=False)
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(c['passed'] for c in report['checks']),str(work/'report.json')
