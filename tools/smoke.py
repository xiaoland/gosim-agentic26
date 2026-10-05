#!/usr/bin/env python3
"""隔离原生宿主验证标准工具会话与实际控件事件；模型回复为合成fixture。"""
import hashlib, importlib.util, json, re, shutil, subprocess, tempfile, time, sys
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
RECOVERY_FIXTURE=r'''
let recovery_error=""
let recovery_feedback=""
fn agent_pump(token){
 agent_active=false phase="waiting" render_content()
 let first=agent_messages[0].content.parse_json() let second=agent_messages[1].content.parse_json()
 fs.write("harness-smoke.json",{checks:[
 {name:"原生类型错误原文进入tool结果" passed:!first.success && first.diagnostics.search("color")>=0}
 {name:"修正中反馈不展示内部堆栈" passed:recovery_feedback=="界面正在修正；可终止本次查询"}
 {name:"成功稿清掉错误并实际挂载" passed:second.success && interface_error=="" && ui.generated.diagnostics()=="" && ui.generated.find("recovered").text()=="界面已恢复"}
 ]}.to_json())
}
fn agent_tool_result(result){
 if !result.success {
 recovery_error=result.diagnostics recovery_feedback=ui.feedback.child(0).text()
 start_timeout(0.5,||product_agent_tool_result(result))
 } else {product_agent_tool_result(result)}
}
start_timeout(1,||{
 run_id+=1 agent_active=true phase="running" agent_messages=[]
 agent_calls=[
 {id:"bad-ui" type:"function" function:{name:"render_ui" arguments:"{\"source\":\"Label{draw_text.text_style: NavRegular{color:#xf00} text:\\\"错误稿\\\"}\"}"}}
 {id:"good-ui" type:"function" function:{name:"render_ui" arguments:"{\"source\":\"recovered := Label{text:\\\"界面已恢复\\\"}\"}"}}
 ] agent_call_index=0 agent_execute_next(run_id)
})
'''
MAP_FIXTURE=r'''
let map_smoke_dispatches=0
fn load_map_slot(slot,candidate){map_smoke_dispatches+=1}
start_timeout(1,||{
 let route={id:"map-fixture" kind:"taxi" segments:[{polyline:"114,22;114.1,22.1"} {polyline:"114.1,22.1;114.2,22.2"} {polyline:"114.3,22.3;114.4,22.4"}]}
 let geometry=map_geometry(route)
 candidates=[route]
 let slot={id:"missing_image" target:"map-fixture" generation:map_generation request:1 target_id:"map-fixture" state:"loading" bytes:nil caption:"" status_widget:"" handle:nil}
 map_slots[slot.id]=slot
 let accepted=accept_map_slot(slot,"{\"status\":\"0\",\"info\":\"UNKNOWN_ERROR\",\"infocode\":\"20003\"}",run_id,1,"map-fixture","")
 let error_rejected=slot.state=="error" && slot.bytes==nil && slot.status.search("20003")>=0
 slot.state="loading" slot.target_id="different-route" fit_map_slot(slot,route)
 let obsolete_fit_skipped=slot.state=="loading"
 slot.target_id=route.id slot.interactive=true slot.camera=nil
 map_camera_changed({widget:slot.id center_lon:114 center_lat:22 zoom:9 width:388 height:240 request:10})
 map_camera_changed({widget:slot.id center_lon:114.1 center_lat:22 zoom:9 width:388 height:240 request:11})
 start_timeout(0.1,||fs.write("harness-smoke.json",{checks:[
 {name:"连续端点无损合并且不跨几何缺口" passed:geometry.paths.len()==2 && geometry.paths[0]=="114,22;114.1,22.1;114.2,22.2" && geometry.paths[1]=="114.3,22.3;114.4,22.4"}
 {name:"HTTP200业务错误不能成为ready图片" passed:!accepted && error_rejected}
 {name:"已替换路线不派发旧fit" passed:obsolete_fit_skipped}
 {name:"同批camera只派发仍当前的请求" passed:map_smoke_dispatches==1 && slot.camera.request==11}
 ]}.to_json()))
})
'''
TERMINAL_FIXTURE=r'''
let terminal_task=0 let terminal_token=-1 let terminal_turn=0 let terminal_checks=[]
let terminal_code="```splash\nLabel{text:\"未执行代码\"}\n```"
let terminal_source="View{width:Fill height:Fit flow:Down kept := Label{text:\"原生结果仍保留\"} retained := TextInput{text:\"原始输入\"} Button{text:\"改变本地状态\" on_click: || {ui.body.find(\"retained\").set_text(\"本地输入仍保留\") ui.body.find(\"kept\").set_text(\"本地页面仍保留\")}} Button{text:\"触发局部错误\" on_click: || {try {ui.body.find(\"missing_local_widget\").set_text(\"不会执行\")} {emit({action:\"runtime_error\" message:\"局部操作失败测试\"})}}}}"
let terminal_long="" for i in 80 {terminal_long+="本次模型提供的结果说明第"+i+"行：内容应可滚动查看。\n"}
fn minimax_request(task,input,schema,token,record,done){
 if terminal_token!=token {terminal_token=token terminal_task+=1 terminal_turn=0}
 terminal_turn+=1 let message={role:"assistant" content:nil}
 if (terminal_task==1 || terminal_task==3) && terminal_turn==1 {
  let source=if terminal_task==1 {terminal_source} else {"View{show_bg:true draw_bg:{color:#xff0000} Label{text:\"错误稿\"}}"}
  message.tool_calls=[{id:"render-original" type:"function" function:{name:"render_ui" arguments:({source:source}).to_json()}}]
 } else {message.content=if terminal_task==1 || terminal_task==2 {terminal_long+terminal_code} elif terminal_task==3 {"生成执行失败，本次文字结果仍可查看"} else {""}}
 start_timeout(if terminal_task==1 && terminal_turn==2 {1.0} else {0.01},||done({choices:[{message:message}]}))
}
fn terminal_observe(){if !agent_active {start_timeout(0.3,||terminal_check())} else {start_timeout(0.1,||terminal_observe())}}
fn terminal_check(){
 let checked="terminal-checked-"+terminal_task+".json" if fs.exists(checked){return} fs.write(checked,"{}")
 if terminal_task==1 {
  terminal_checks.push({name:"正常生成稿不重复终端文字" passed:generated_render_complete && !ui.final_answer.visible() && answer_text==terminal_long+terminal_code})
  terminal_checks.push({name:"正常稿本地页面与输入状态保留" passed:ui.generated.find("kept").text()=="本地页面仍保留" && ui.generated.find("retained").text()=="本地输入仍保留"})
  terminal_checks.push({name:"终端文字仍留history与facts" passed:interface_facts().answer==answer_text && agent_messages[agent_messages.len()-1].content==answer_text})
 } elif terminal_task==2 {
  terminal_checks.push({name:"无生成稿终端文字可见且代码不执行" passed:!generated_active && ui.final_answer.visible() && ui.final_answer.text()==terminal_long+terminal_code})
 } elif terminal_task==3 {
  fs.write("single-failed-state.json",{active:generated_active complete:generated_render_complete area_visible:ui.generated_area.visible() child_visible:ui.generated.visible() text_visible:ui.final_answer.visible() text:ui.final_answer.text() diagnostic:ui.generated.diagnostics()}.to_json())
  terminal_checks.push({name:"执行失败稿使用终端文字兜底" passed:generated_active && !generated_render_complete && ui.generated.diagnostics()!="" && !ui.generated_area.visible() && ui.final_answer.visible() && ui.final_answer.text()=="生成执行失败，本次文字结果仍可查看"})
 } else {
  terminal_checks.push({name:"空终端无稿明确缺少内容" passed:!generated_active && runtime_status=="Agent没有返回可展示内容，请重新查询" && !ui.final_answer.visible()})
  fs.write("harness-smoke.json",{checks:terminal_checks}.to_json()) return
 }
 fs.write("terminal-ready.json",{task:terminal_task}.to_json())
 start_timeout(0.1,||terminal_wait())
}
fn terminal_wait(){let path="terminal-continue-"+terminal_task+".json" if fs.exists(path){let advanced="terminal-advanced-"+terminal_task+".json" if fs.exists(advanced){return} fs.write(advanced,"{}") if terminal_task==1 {fs.write("local-error-state.json",{complete:generated_render_complete area_visible:ui.generated_area.visible() text_visible:ui.final_answer.visible() error:interface_error mailbox:ui.generated.mailbox.text() seen:mailbox_seen}.to_json()) terminal_checks.push({name:"成功稿后局部回调错误不切文字兜底" passed:generated_render_complete && ui.generated_area.visible() && !ui.final_answer.visible() && interface_error!=""})} start_task() start_timeout(0.2,||terminal_observe())} else {start_timeout(0.1,||terminal_wait())}}
fn terminal_start(){if fs.exists("terminal-start.json"){if fs.exists("terminal-claimed.json"){return} fs.write("terminal-claimed.json","{}") start_task() start_timeout(0.2,||terminal_observe())} else {start_timeout(0.1,||terminal_start())}}
start_timeout(1,||terminal_start())
'''

def main():
 sp=importlib.util.spec_from_file_location('agent',ROOT/'tools/agent.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
 (ROOT/'build/smoke').mkdir(exist_ok=True,parents=True);w=Path(tempfile.mkdtemp(prefix='navigation-harness-',dir=ROOT/'build/smoke'))
 a.STATE=w/'private-state';a.HOME_DIR=a.STATE/'home';a.CORE=a.STATE/'core';a.SESSION=a.STATE/'session.json'
 for p in [a.STATE,a.HOME_DIR,a.CORE]:p.mkdir(parents=True,exist_ok=True)
 original=(ROOT/'bundle/main.splash').read_text();recovery='--render-recovery' in sys.argv;source=original.replace('fn minimax_request(','fn product_minimax_request(',1).replace('minimax_request("",agent_messages','smoke_request("",agent_messages')+'\n'+FIXTURE
 if '--map-details' in sys.argv:source=original.replace('fn load_map_slot(','fn product_load_map_slot(',1)+'\n'+MAP_FIXTURE
 if '--terminal-content' in sys.argv:source=original.replace('fn minimax_request(','fn product_minimax_request(',1)+'\n'+TERMINAL_FIXTURE
 if recovery:source=original.replace('fn agent_pump(','fn product_agent_pump(',1).replace('fn agent_tool_result(','fn product_agent_tool_result(',1)+'\n'+RECOVERY_FIXTURE
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
  if '--terminal-content' in sys.argv:
   time.sleep(3)
   q('k',c='Space',cmd=1,wait=1)
   for ch in 'android':q('k',c='Key'+ch.upper(),wait=1)
   q('k',c='enter',wait=1);time.sleep(1)
   q('m',k='down',x=200,y=300,wait=1)
   for y in range(320,570,25):q('m',k='move',x=200,y=y,wait=1)
   q('m',k='up',x=200,y=570,wait=1);q('t',t='Navigation',wait=1);q('k',c='enter',wait=1);time.sleep(2)
   (jail/'terminal-start.json').write_text('{}')
   for task in (1,2,3):
    ready=None
    for _ in range(150):
     rows=json.loads(q('snap'))['s']
     if task==1:
      local=[v for v in rows if v.get('t')=='改变本地状态']
      if local:
       r=local[0]['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1)
     try:ready=json.loads((jail/'terminal-ready.json').read_text())
     except (FileNotFoundError,json.JSONDecodeError):pass
     if ready and ready['task']==task:break
     time.sleep(.1)
    assert ready and ready['task']==task
    q('m',k='scroll',x=220,y=600,dy=-12000,precise=1,wait=1);time.sleep(.3)
    rows=json.loads(q('snap'))['s']
    if task==1:
     assert any(v.get('i')=='kept' and v['r'][3]>0 for v in rows)
    (w/('single-result-'+str(task)+'.png')).write_bytes(q('g',raw=1))
    if task==3:assert any('生成执行失败，本次文字结果仍可查看'==v.get('t') for v in rows)
    (w/('single-result-'+str(task)+'.png')).write_bytes(q('g',raw=1))
    if task==1:
     row=next(v for v in rows if v.get('t')=='触发局部错误');r=row['r'];q('click',x=r[0]+r[2]/2,y=r[1]+r[3]/2,wait=1);time.sleep(.4)
     rows=json.loads(q('snap'))['s'];assert any(v.get('i')=='kept' and v['r'][3]>0 for v in rows)
     (w/'single-result-local-error.png').write_bytes(q('g',raw=1))
    if task==2:
     q('m',k='scroll',x=220,y=600,dy=8000,precise=1,wait=1);time.sleep(.5)
     assert any('```splash' in v.get('t','') for v in json.loads(q('snap'))['s'])
     (w/'single-result-fallback-bottom.png').write_bytes(q('g',raw=1))
    (jail/('terminal-continue-'+str(task)+'.json')).write_text('{}')

  for _ in range(150):
   try:report=json.loads((jail/'harness-smoke.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError):pass
   if report:break
   time.sleep(.1)
  assert report,'宿主未完成工具会话；查看 '+str(w/'native.log')
  assert all(row['passed'] for row in report['checks']),report
  if recovery or '--map-details' in sys.argv or '--terminal-content' in sys.argv:
   report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),injected_source_sha256=hashlib.sha256(source.encode()).hexdigest(),synthetic_model=True,real_native_controls=True,mode='Android' if '--terminal-content' in sys.argv else 'desktop')
   (w/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS: '+str(len(report['checks']))+'项定向原生检查；'+str(w/'report.json'));return
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
