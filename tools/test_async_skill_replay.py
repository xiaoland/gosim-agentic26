"""离线回放真实 read_skill 响应，验证200ms后台读取、完整回执与取消。

原始响应和完整私有state只从忽略的研究目录复制；不会调用模型或交通服务。
"""
import hashlib, importlib.util, json, re, shutil, subprocess, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=r'''
let async_probe_dispatches=0 let async_probe_heartbeats=0 let async_probe_cancelled_return=false
let async_probe_last_messages=nil let async_probe_start_heartbeat=0 let async_probe_tool_heartbeats=0
start_interval(0.02,||{async_probe_heartbeats+=1})
fn async_probe_host_request(body,done){
 async_probe_dispatches+=1
 if async_probe_dispatches==1 {async_probe_start_heartbeat=async_probe_heartbeats start_timeout(0.01,||done({is_ok:true data:async_probe_reply error:nil}))}
 else {
  async_probe_last_messages=body.messages async_probe_tool_heartbeats=async_probe_heartbeats-async_probe_start_heartbeat
  let token=run_id
  read_agent_skill({name:"rail-routing"},token,fn(result){async_probe_cancelled_return=true})
  run_id+=1 active_tool=nil
  start_timeout(0.35,||fs.write("async-skill-replay-result.json",{dispatches:async_probe_dispatches heartbeats_during_tools:async_probe_tool_heartbeats cancelled_return:async_probe_cancelled_return messages:async_probe_last_messages}.to_json()))
 }
 return "offline-async-skill-replay"
}
start_timeout(2,||start_task_with(async_probe_input,false))
'''

def main():
 sp=importlib.util.spec_from_file_location('agent',ROOT/'tools/agent.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
 original_state=ROOT/'build/research/rail-integration/e2e/private-state-round13'
 events=[json.loads(x) for x in (ROOT/'build/research/rail-integration/e2e/round13/trace-private.jsonl').read_text().splitlines()]
 event=next(e for e in events if e['seq']==104 and e['event']=='model_response')
 reply=json.loads(json.loads(event['data'])['body'])
 input_text=json.loads((ROOT/'build/research/rail-integration/e2e/input-safe.json').read_text())['input']
 out=Path(tempfile.mkdtemp(prefix='async-skills-',dir=ROOT/'build/research/rail-integration'))
 state=out/'private-state';shutil.copytree(original_state,state)
 a.STATE=state;a.HOME_DIR=state/'home';a.CORE=state/'core';a.SESSION=state/'session.json'
 mount=list((a.HOME_DIR/'apps/.system/os.agentic26-navigation').glob('*/main.splash'))[0].parent
 original=(ROOT/'bundle/main.splash').read_text()
 source=original.replace('record.host_request_id = host.request("model.chat", body, fn(reply){','record.host_request_id = async_probe_host_request(body, fn(reply){',1)
 assert source!=original
 source+='\nlet async_probe_reply='+json.dumps(json.dumps(reply,ensure_ascii=False),ensure_ascii=False)+'.parse_json()\nlet async_probe_input='+json.dumps(input_text,ensure_ascii=False)+'\n'+FIXTURE
 (mount/'main.splash').write_text(source)
 subprocess.run([str(ROOT.parent/'.octosense-agentic26/OctoSense-App-Hub/target/release/hub'),'stamp',str(mount)],stdout=subprocess.DEVNULL,check=True)
 jail=a.HOME_DIR/'apps/os.agentic26-navigation';a.materialize_skills(ROOT/'bundle',jail)
 config=json.loads((jail/'private-config.json').read_text());directory=jail/'dev-trace'/config['development_trace_session'];counter=json.loads((directory/'instance-counter.json').read_text())['next'];trace=directory/('vm-'+str(counter))
 ledger=jail.parent/'.host/model/ledger.json';before=hashlib.sha256(ledger.read_bytes()).hexdigest()
 result_path=jail/'async-skill-replay-result.json';result_path.unlink(missing_ok=True)
 env=a.host_env(True);env['MAKEPAD_TEST_ASYNC_READ_DELAY_MS']='200'
 log=out/'native.log';process=None;ui_response=None;t0=time.monotonic()
 try:
  with log.open('wb') as fd:process=subprocess.Popen([str(a.BINARY),'--remote','--test-action','launch-agentic26-navigation'],cwd=state,env=env,stdout=fd,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(200):
   match=re.search(rb'listening on 127\.0\.0\.1:(\d+)',log.read_bytes())
   if match:break
   assert process.poll() is None;time.sleep(.05)
  session={'pid':process.pid,'port':int(match[1]),'process_stamp':a.process_stamp(process.pid)}
  for _ in range(750):
   rows=[]
   for f in sorted(trace.glob('segment-*.jsonl')):
    for line in f.read_text().splitlines():
     try:rows.append(json.loads(line))
     except json.JSONDecodeError:pass
   if ui_response is None and any(e['event']=='tool_call' for e in rows):
    started=time.monotonic();tree=a.remote(session,'g?raw=1');ui_response={'elapsed_ms':(time.monotonic()-started)*1000,'returned':bool(tree),'tool_result_count_at_start':sum(e['event']=='tool_result' for e in rows)}
   if result_path.exists():break
   assert process.poll() is None;time.sleep(.02)
  assert result_path.exists(),str(log)
  raw=json.loads(result_path.read_text());tools=[m for m in raw['messages'] if m['role']=='tool']
  expected_calls=reply['response']['choices'][0]['message']['tool_calls']
  exact=True
  for call in expected_calls:
   found=[m for m in tools if m['tool_call_id']==call['id']]
   args=json.loads(call['function']['arguments']);resource=args.get('path','SKILL.md');name=args['name'].replace('_','-')
   if len(found)!=1:exact=False;continue
   result=json.loads(found[0]['content']);exact &= result.get('success') is True and result.get('content')==(jail/'skills'/name/resource).read_text()
  system=raw['messages'][0]['content']
  no_body=all((jail/'skills'/json.loads(c['function']['arguments'])['name']/'SKILL.md').read_text() not in system for c in expected_calls)
  errors=[x for x in log.read_text().splitlines() if '[E]' in x]
  unexpected_errors=[error for error in errors if "widget 'shell_state' not found in tree" not in error]
  checks=[{'name':'生产响应链工具回执与下次派发恰一次','passed':raw['dispatches']==2 and len(tools)==len(expected_calls) and exact}, {'name':'200ms后台读取期间UI事件循环继续响应','passed':raw['heartbeats_during_tools']>=10 and ui_response is not None and ui_response['returned']}, {'name':'首次系统上下文只有目录不含正文','passed':no_body}, {'name':'取消后的旧读取无回执','passed':not raw['cancelled_return']}, {'name':'实际账本未变化','passed':hashlib.sha256(ledger.read_bytes()).hexdigest()==before}]
  report={'checks':checks,'product_source_sha256':hashlib.sha256(original.encode()).hexdigest(),'original_response_seq':104,'full_state_copy':True,'model_called':False,'provider_called':False,'backend_delay_ms':200,'heartbeat_count':raw['heartbeats_during_tools'],'ui_response':ui_response,'native_errors':errors,'unexpected_native_errors':unexpected_errors,'elapsed_seconds':time.monotonic()-t0}
  (out/'report-safe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  assert all(c['passed'] for c in checks) and not unexpected_errors,str(out/'report-safe.json')
  print('PASS: 5项200ms异步技能真实响应链检查；'+str(out/'report-safe.json'))
 finally:
  if process and process.poll() is None:
   process.terminate()
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.kill();process.wait()
if __name__=='__main__':main()
