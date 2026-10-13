"""原online5快照/原M3路线卡详情生产恢复，最多一次静态地图。"""
import hashlib,json,re,time,shutil
from pathlib import Path
from urllib.parse import urlencode
import agent
from test_trip_replay import prepare as replay_prepare
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/research/journey-guardian/current-online-5'
def prepare(jail):
 replay_prepare(jail,BASE/'private-state/home/apps/os.agentic26-navigation')
 config=json.loads((BASE/'private-state/home/apps/os.agentic26-navigation/private-config.json').read_bytes());config['development_trace']=False;(jail/'private-config.json').write_text(json.dumps(config))
FIXTURE=r'''
fn trace_initialize(){}
let ou_models=0 let ou_traffic=0 let ou_http=0 let ou_immediate=false
fn minimax_request(task,input,schema,token,record,done){ou_models+=1}
fn amap_request(path,params,token,done){ou_traffic+=1}
fn view_route(id){product_view_route(id) ou_immediate=viewed_route_id==id start_timeout(0.01,||fs.write("ui-viewed.json",{id:viewed_route_id immediate:ou_immediate}.to_json()))}
fn ensure_map_catalog(candidate,done){product_ensure_map_catalog(candidate,fn(result){done(result) if result.success && candidate.id=="route_1_10" {start_timeout(0.01,||fs.write("ui-catalog.json",{paths:map_geometry(candidate).paths catalog:map_path_catalog(candidate)}.to_json()))}})}
fn dispatch_map_render(slot,candidate,token,request,target_id,geometry){if !map_slot_current(slot,token,request,target_id) || geometry.error!=nil {return} if ou_http>=1{return} ou_http+=1 fs.write("ui-http.json",{count:ou_http params_bytes:geometry.params.len() paths:geometry.paths.len()}.to_json()) product_dispatch_map_render(slot,candidate,token,request,target_id,geometry)}
fn accept_map_slot(slot,bytes,token,request,target_id,detail){fs.write_bytes("ui-map.png",bytes) let accepted=product_accept_map_slot(slot,bytes,token,request,target_id,detail) start_timeout(0.01,||fs.write("ui-accepted.json",{accepted:accepted http:ou_http models:ou_models traffic:ou_traffic state:slot.state}.to_json())) return accepted}
start_timeout(2,||{let blocks=[] for b in ui_blocks {blocks.push({id:b.id raw_source:b.raw_source notified:b.notified diagnostic:b.handle.diagnostics()})} fs.write("ui-restored.json",{blocks:blocks replay:trip_replay}.to_json())})
'''
def source(original):
 for name in ['trace_initialize','minimax_request','amap_request','view_route','ensure_map_catalog','dispatch_map_render','accept_map_slot']:original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 def waitfile(name,seconds=12):
  deadline=time.time()+seconds
  while time.time()<deadline:
   if (jail/name).exists():return json.loads((jail/name).read_bytes())
   time.sleep(.1)
  raise AssertionError('missing '+name)
 restored=waitfile('ui-restored.json');m=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text());assert m;session={'port':int(m[1])}
 def req(route,**p):return agent.remote(session,route+('?' + urlencode(p) if p else ''))
 def cap(name):
  s=json.loads(req('snap',all=1));(work/(name+'.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2));(work/(name+'.png')).write_bytes(req('g',raw=1));return s['s']
 def scroll(dy):req('m',k='scroll',x=210,y=720,dy=dy,precise=1,wait=1);time.sleep(.5)
 rows=cap('restored');selected=None
 for _ in range(8):
  buttons=[r for r in rows if r.get('ty')=='Button' and r.get('t')=='查看详情' and 50<r['r'][1]<820 and r['r'][3]>20]
  if buttons:selected=sorted(buttons,key=lambda r:r['r'][1])[0];break
  scroll(400);rows=cap('candidate-scroll')
 assert selected,'Route卡查看详情按钮不在实际viewport'
 x,y,w,h=selected['r'];req('click',x=x+w/2,y=y+h/2,wait=1);time.sleep(.3);cap('detail-immediate');viewed=waitfile('ui-viewed.json');catalog=waitfile('ui-catalog.json',15);accepted=waitfile('ui-accepted.json',18)
 rows=cap('detail-map-before-scroll')
 # 原详情先显示路线文本；仅滚动父容器以暴露真实地图，不修改DSL。
 for _ in range(8):
  maps=[r for r in rows if r.get('i')=='route_map' and r['r'][3]>20]
  if maps and 50<maps[-1]['r'][1] and maps[-1]['r'][1]+maps[-1]['r'][3]<850:break
  scroll(500);rows=cap('detail-map-scroll')
 cap('detail-map-visible')
 back=[r for r in rows if r.get('ty')=='Button' and r.get('t')=='返回候选' and 50<r['r'][1]<850]
 if not back:
  for _ in range(8):
   scroll(-500);rows=cap('detail-return-scroll');back=[r for r in rows if r.get('ty')=='Button' and r.get('t')=='返回候选' and 50<r['r'][1]<850]
   if back:break
 assert back,'原返回候选按钮不在viewport';x,y,w,h=back[0]['r'];req('click',x=x+w/2,y=y+h/2,wait=1);time.sleep(.5);cap('returned')
 checks=[{'name':'原routes182/detail194逐字恢复并通知','passed':all(next(b['raw_source'] for b in restored['blocks'] if b['id']==i)==(BASE/f).read_text() for i,f in [('routes','render-render_routes-182-0-private.splash'),('route_detail','render-render_route_detail-194-0-private.splash')])},{'name':'真实卡点击即时发布Route且一次静态图accepted','passed':viewed['id']=='route_1_10' and viewed['immediate'] and accepted['accepted'] and accepted['http']==1 and accepted['models']==0 and accepted['traffic']==0}]
 report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'restored':restored,'viewed':viewed,'accepted':accepted,'catalog_paths':len(catalog['paths']),'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'boundary':'原online5完整分片记录生产trip_load/trip_restore；原routes182/detail194不改；仅dispatch_map_render外层限制一次真实静态HTTP。无规划/守护重查，不称原2VM liveheap根因复现。实际截图待view；目录需Python对照。','screenshot_viewed':False};(work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
