#!/usr/bin/env python3
"""隔离原生宿主验证标准工具会话与实际控件事件；模型回复为合成fixture。"""
import hashlib, importlib.util, json, re, shutil, subprocess, tempfile, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=r'''
let smoke_turn=0
let smoke_token=-1
let smoke_queries=0
let smoke_first_received=0
let smoke_late_rejected=false
fn smoke_call(id,name,args){return {id:id type:"function" function:{name:name arguments:args.to_json()}}}
fn smoke_request(task,input,schema,token,record,done){
 if token!=smoke_token {smoke_token=token smoke_turn=0 smoke_queries+=1 if smoke_queries==1 {smoke_first_received=received_at}}
 smoke_turn+=1
 let message={role:"assistant" content:nil}
 if smoke_turn==1 {message.tool_calls=[smoke_call("notes-1","read_notes",{}) smoke_call("skill-1","read_skill",{name:"native_ui"})]}
 elif smoke_turn==2 {message.tool_calls=[smoke_call("render-1","render_ui",{source:"View{width:Fill height:Fit flow:Down wrap := Label{text:\"原生自然换行验证：文字应该完整显示而不是在屏幕右侧裁切。原生自然换行验证：文字应该完整显示而不是在屏幕右侧裁切。原生自然换行验证：文字应该完整显示而不是在屏幕右侧裁切。\"} for i in 20 {Label{text:\"第\"+i+\"行：这是可以纵向滚动查看的本次结果内容\"}}}"})]}
 else {message.content="本轮计算结果，仅在当前内存中"}
 let delay=0.01 if smoke_queries==2 {delay=0.8}
 start_timeout(delay,||{if current_task(token){done({model:"MiniMax-M3" choices:[{message:message finish_reason:if route_get(message,"tool_calls").is_array(){"tool_calls"}else{"stop"}}]})} else {smoke_late_rejected=true}})
}
fn smoke_report(){
 if !agent_active {
 let results=[] let users=0
 for message in agent_messages {if message.role=="tool" {results.push(message.tool_call_id)} if message.role=="user" {users+=1}}
 let checks=[]
 if phase!="cancelled" {
 checks=[
 {name:"本轮多个工具按call_id返回" passed:results.len()==3 && results[0]=="notes-1" && results[1]=="skill-1" && results[2]=="render-1"}
 {name:"每次查询都有独立system与单一user" passed:agent_messages[0].role=="system" && users==1 && agent_messages[1].content.parse_json().request==request_text}
 {name:"实际原生render诊断为空" passed:agent_messages[6].content.parse_json().success && ui.generated.diagnostics()==""}
 {name:"无tool_calls本次结束" passed:!agent_active && agent_messages[7].content.is_string()}
 {name:"旧结果文件未读取也未改写" passed:fs.read("trip.json")=="historical fixture ignored" && fs.read("agent-run.json")=="historical audit ignored"}
 ]
 if smoke_queries>=3 {checks.push({name:"停止后新输入重新起算和预算" passed:received_at>smoke_first_received && user_limits.minutes==30 && user_limits.budget_cents==8000 && arrive_by==received_at+1800}) checks.push({name:"停止旧响应不派发" passed:smoke_late_rejected})}
 }
 fs.write("harness-smoke.json",{checks:checks queries:smoke_queries phase:phase received_at:received_at}.to_json())
 }
 start_timeout(0.1,||smoke_report())
}
start_timeout(1.0,||{start_task() start_timeout(0.3,||smoke_report())})
'''
def main():
 sp=importlib.util.spec_from_file_location('agent',ROOT/'tools/agent.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
 (ROOT/'build/smoke').mkdir(exist_ok=True,parents=True);w=Path(tempfile.mkdtemp(prefix='navigation-harness-',dir=ROOT/'build/smoke'))
 a.STATE=w/'private-state';a.HOME_DIR=a.STATE/'home';a.CORE=a.STATE/'core';a.SESSION=a.STATE/'session.json'
 for p in [a.STATE,a.HOME_DIR,a.CORE]:p.mkdir(parents=True,exist_ok=True)
 original=(ROOT/'bundle/main.splash').read_text();source=original.replace('fn minimax_request(','fn product_minimax_request(',1).replace('minimax_request("",agent_messages','smoke_request("",agent_messages')+'\n'+FIXTURE
 env=a.host_env(True);process=None;port=None
 def q(route,**args):return urlopen(f'http://127.0.0.1:{port}/'+route+('?' + urlencode(args) if args else ''),timeout=15).read()
 def stop():
  nonlocal process
  if process and process.poll() is None:
   try:q('quit')
   except OSError:pass
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
  process=None
 def launch(tag):
  nonlocal process,port
  log=w/(tag+'.log')
  with log.open('wb') as f:process=subprocess.Popen([str(a.BINARY),'--remote','--test-action','launch-agentic26-navigation'],cwd=a.STATE,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(200):
   m=re.search(rb'\[makepad-remote\] listening on 127\.0\.0\.1:(\d+)',log.read_bytes())
   if m:port=int(m[1]);return
   assert process.poll() is None,str(log);time.sleep(.1)
  raise RuntimeError('隔离宿主未启动')
 try:
  launch('mount');paths=[]
  for _ in range(100):
   paths=list((a.HOME_DIR/'apps/.system/os.agentic26-navigation').glob('*/main.splash'))
   if paths:break
   time.sleep(.1)
  assert len(paths)==1;mount=paths[0].parent;stop();shutil.copytree(ROOT/'bundle',mount,dirs_exist_ok=True)
  manifest=json.loads((mount/'manifest.json').read_text());manifest['id']='os.agentic26-navigation';(mount/'manifest.json').write_text(json.dumps(manifest));(mount/'main.splash').write_text(source)
  subprocess.run([str(ROOT.parent/'.octosense-agentic26/OctoSense-App-Hub/target/release/hub'),'stamp',str(mount)],stdout=subprocess.DEVNULL,check=True)
  a.init_demo();jail=a.jail_path();a.materialize_skills(ROOT/'bundle',jail);(jail/'private-config.json').write_text('{"location_mode":"demo"}');(jail/'trip.json').write_text('historical fixture ignored');(jail/'agent-run.json').write_text('historical audit ignored')
  launch('native');report=None
  for _ in range(150):
   try:report=json.loads((jail/'harness-smoke.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError):pass
   if report:break
   time.sleep(.1)
  assert report,'宿主未完成工具会话；查看 '+str(w/'native.log')
  assert all(row['passed'] for row in report['checks']),report
  time.sleep(3)
  q('k',c='Space',cmd=1,wait=1)
  for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
  q('k',c='enter',wait=1);time.sleep(1)
  q('m',k='down',x=200,y=300,wait=1)
  for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
  q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(2)
  rows=json.loads(q('snap'))['s'];(w/'before-safe.json').write_text(json.dumps(rows,ensure_ascii=False));(w/'before.png').write_bytes(q('g',raw=1));wrap=next(row for row in rows if row.get('i')=='wrap');assert wrap['r'][3]>60,wrap['r']
  q('m',k='scroll',x=260,y=600,dy=1500,precise=1,wait=1);time.sleep(.5);rows=json.loads(q('snap'))['s'];(w/'after-safe.json').write_text(json.dumps(rows,ensure_ascii=False));(w/'after.png').write_bytes(q('g',raw=1));assert any('第19行' in row.get('t','') for row in rows),'底部结果未能滚动到达'
  def click_shell(text):
   row=next(v for v in json.loads(q('snap'))['s'] if v['ty']=='Button' and v.get('t')==text);r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
  click_shell('查询');time.sleep(.1);click_shell('终止');time.sleep(.9)
  report=json.loads((jail/'harness-smoke.json').read_text());assert report['phase']=='cancelled',report
  row=next(v for v in json.loads(q('snap'))['s'] if v['ty']=='TextInput' and v.get('i')=='sentence');r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
  for _ in range(len(row.get('t',''))+3):q('k',c='Backspace',wait=1);q('k',c='Delete',wait=1)
  q('t',t='30分钟内到机场，预算80元',wait=1);click_shell('查询')
  for _ in range(60):
   report=json.loads((jail/'harness-smoke.json').read_text())
   if report['queries']>=3 and len(report['checks'])==7:break
   time.sleep(.1)
  assert len(report['checks'])==7 and all(row['passed'] for row in report['checks']),report
  report['checks'] += [{'name':'Android长文字自然换行','passed':True},{'name':'Android内容可滚到最后一行','passed':True}]
  report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),synthetic_model=True,real_native_controls=True)
  (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: 9无状态查询/Android布局检查；'+str(w/'report.json'))
 finally:stop()
if __name__=='__main__':main()
