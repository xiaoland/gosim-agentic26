"""online5真实最大polyline与原goal薄阶段测量，不恢复图或会话。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
 b=ROOT/'build/research/journey-guardian/current-online-5';r=json.loads((b/'route1-10-raw-snapshot-private.json').read_bytes());trip=json.loads((b/'saved-full-snapshot-private.json').read_bytes())['data'];lines=[]
 def visit(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if k=='polyline' and isinstance(v,str):lines.append(v)
    else:visit(v)
  elif isinstance(x,list):
   for v in x:visit(v)
 visit(r);(jail/'phase-line.txt').write_text(max(lines,key=len));goal=trip['goal'];(jail/'phase-goal.json').write_text(json.dumps(goal,ensure_ascii=False,separators=(',',':')));trip['snapshot']=None
 (jail/'phase-trip.json').write_text(json.dumps({'schema':1,'selected_id':trip['id'],'next_id':2,'trips':[trip]},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn amap_request(path,params,token,done){}
let op_marks=[] let op_line=nil let op_goal=nil let op_trip=nil let op_json=nil let op_parsed=nil let op_started=0
fn op_mark(name){op_marks.push({name:name elapsed_ms:(time_now()-op_started)*1000})}
start_timeout(0.8,||fs.read_async("phase-line.txt",fn(a){op_line=a.text fs.read_async("phase-goal.json",fn(b){op_goal=b.text.parse_json() fs.read_async("phase-trip.json",fn(c){op_trip=c.text.parse_json()
start_timeout(0.01,||{op_started=time_now() op_mark("split_enter") let points=op_line.split(";") op_mark("split_return") let bounds=nil for i in 0..100 {bounds=map_bounds_add(bounds,route_point(points[i]))} op_mark("bounds100_return") op_marks.push({name:"split_count" value:points.len() bounds:bounds})})
start_timeout(0.2,||{op_started=time_now() op_mark("goal_to_json_enter") op_json=op_goal.to_json() op_mark("goal_to_json_return") op_marks.push({name:"goal_json_chars" value:op_json.len()})})
start_timeout(0.4,||{op_started=time_now() op_mark("goal_parse_enter") op_parsed=op_json.parse_json() op_mark("goal_parse_return")})
start_timeout(0.6,||{op_started=time_now() op_mark("goal_valid_enter") let valid=guardian_valid_goal(op_parsed) op_mark("goal_valid_return") op_marks.push({name:"goal_valid" value:valid})})
start_timeout(0.8,||{op_started=time_now() op_mark("trip_valid_enter") let valid=trip_valid(op_trip) op_mark("trip_valid_return") op_marks.push({name:"trip_valid" value:valid})})
start_timeout(1.2,||fs.write("phase-result.json",{marks:op_marks}.to_json()))
})})}))
'''
def source(original):
 for name in ['trace_initialize','trip_load','agent_pump','amap_request']:original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
 return original+'\n'+FIXTURE
def run(work,jail,original,injected):
 for _ in range(200):
  if (jail/'phase-result.json').exists():break
  time.sleep(.05)
 marks=json.loads((jail/'phase-result.json').read_bytes());r={'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':marks,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'boundary':'原online5最长412775字符19656点polyline；原goal35553B selected_route24273B。split+首100点bounds同入口；goal序列化/解析/校验分别入口。trip_valid原record头与goal，snapshot=nil；不恢复原liveheap、完整图、会话或snapshot。无人工延迟/预算改动。','model_requested':False,'provider_requested':False};(work/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
