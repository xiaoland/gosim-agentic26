#!/usr/bin/env python3
"""隔离原生宿主验证标准工具会话与实际控件事件；模型回复为合成fixture。"""
import hashlib, importlib.util, json, re, shutil, subprocess, tempfile, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=r'''
let smoke_turn=0
fn smoke_call(id,name,args){return {id:id type:"function" function:{name:name arguments:args.to_json()}}}
fn smoke_request(task,input,schema,token,record,done){
 smoke_turn+=1
 let message={role:"assistant" content:nil}
 if smoke_turn==1 {message.tool_calls=[smoke_call("notes-1","read_notes",{}) smoke_call("skill-1","read_skill",{name:"native_ui"})]}
 elif smoke_turn==2 {message.tool_calls=[smoke_call("render-1","render_ui",{source:"View{width:Fill height:Fit flow:Down title := Label{text:facts.status} Button{text:\"测试预算修改\" on_click: || emit({action:\"change_conditions\" text:\"预算改为80\"})}}"})]}
 else {message.content="合成工具会话已完成，等待用户操作"}
 start_timeout(0.01,||{if current_task(token){done({model:"MiniMax-M3" choices:[{message:message finish_reason:if route_get(message,"tool_calls").is_array(){"tool_calls"}else{"stop"}}]})}})
}
fn smoke_report(){
 if agent_active {start_timeout(0.1,||smoke_report()) return}
 let results=[]
 for message in agent_messages {if message.role=="tool" {results.push(message.tool_call_id)}}
 let original=agent_messages[1].content.parse_json().facts.arrive_by
 let rows=[
 {name:"同一assistant本轮两个tool_calls全部执行" passed:results.len()==3 && results[0]=="notes-1" && results[1]=="skill-1" && results[2]=="render-1"}
 {name:"保留原始assistant消息及call_id" passed:agent_messages[2].tool_calls.len()==2 && agent_messages[3].tool_call_id=="notes-1"}
 {name:"实际render结果是实例诊断" passed:agent_messages[6].content.parse_json().success && ui.generated.diagnostics()==""}
 {name:"无tool_calls结束等待用户" passed:!agent_active && agent_messages[7].content.is_string()}
 {name:"原截止未被工具执行重置" passed:arrive_by==original}
 ]
 if smoke_turn>3 {rows.push({name:"真实按钮事件进入同一历史并修改预算" passed:user_limits.budget_cents==8000 && arrive_by==original && agent_messages[8].role=="user"})}
 fs.write("harness-smoke.json",{checks:rows turn:smoke_turn phase:phase}.to_json())
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
  a.init_demo();jail=a.jail_path();a.materialize_skills(ROOT/'bundle',jail);(jail/'private-config.json').write_text('{"location_mode":"demo"}')
  launch('native');report=None
  for _ in range(150):
   try:report=json.loads((jail/'harness-smoke.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError):pass
   if report:break
   time.sleep(.1)
  assert report,'宿主未完成工具会话；查看 '+str(w/'native.log')
  assert all(row['passed'] for row in report['checks']),report
  rows=json.loads(q('snap'))['s'];button=next(row for row in rows if row.get('t')=='测试预算修改');r=button['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
  for _ in range(60):
   report=json.loads((jail/'harness-smoke.json').read_text())
   if report['turn']>3:break
   time.sleep(.1)
  assert len(report['checks'])==6 and all(row['passed'] for row in report['checks']),report
  report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),synthetic_model=True,real_native_controls=True)
  (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: 6工具会话/原生事件检查；'+str(w/'report.json'))
 finally:stop()
if __name__=='__main__':main()
