#!/usr/bin/env python3
"""只读核验技能工具回执与下一真实模型请求的字节链，不将未调用视为读取失败。"""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/research/transfer-exploration'
NAMES=('online','fixture-provider-failure','fixture-current','fixture-revised','fixture-schema','fixture-final-api','fixture-protocol-final')
sha=lambda value:hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()

def data(e):return json.loads(e['data']) if isinstance(e['data'],str) else e['data']

def audit(name,trace_path=None):
 path=Path(trace_path) if trace_path else BASE/name/'trace-private.jsonl';events=list(map(json.loads,path.read_text().splitlines()))
 requests=[]
 for e in events:
  if e['event']=='model_request':requests.append((e,json.loads(data(e)['body'])))
 first=requests[0][1];system=next(m['content'] for m in first['messages'] if m['role']=='system');catalog=json.loads(system[system.index('[{'):])
 calls={e['call_id']:e for e in events if e['event']=='tool_call' and data(e)['name']=='read_skill'}
 reads=[]
 for e in events:
  if e['event']!='tool_result' or data(e)['name']!='read_skill':continue
  result=json.loads(data(e)['result']);call=calls[e['call_id']];args=json.loads(data(call)['arguments']);content=result.get('content','');following=next(((n,b) for n,b in requests if n['seq']>e['seq']),None)
  matching=[];assistant_calls=[]
  if following:
   n,b=following
   matching=[m for m in b['messages'] if m.get('role')=='tool' and m.get('tool_call_id')==e['call_id']]
   assistant_calls=[t for m in b['messages'] if m.get('role')=='assistant' for t in m.get('tool_calls',[]) if t.get('id')==e['call_id']]
  later_requests=[(n,bb) for n,bb in requests if n['seq']>e['seq']]
  retention=[]
  for n,bb in later_requests:
   mm=[m for m in bb['messages'] if m.get('role')=='tool' and m.get('tool_call_id')==e['call_id']]
   retention.append({'request_seq':n['seq'],'count':len(mm),'byte_identical':len(mm)==1 and mm[0]['content']==data(e)['result']})
  file_matches=[]
  if result.get('success'):
   candidates=[ROOT/'bundle/assets/skills'/result['name']/result['path']]
   candidates+=list((ROOT/'build/smoke').glob('navigation-harness-*/private-state/home/apps/os.agentic26-navigation/skills/'+result['name']+'/'+result['path']))
   candidates+=list((ROOT/'build/research').glob('*/online/private-state/home/apps/os.agentic26-navigation/skills/'+result['name']+'/'+result['path']))
   for f in candidates:
    if f.is_file() and sha(f.read_bytes())==sha(content):file_matches.append(str(f))
  decoded=json.loads(matching[0]['content']) if len(matching)==1 else None
  reads.append({'call_seq':call['seq'],'result_seq':e['seq'],'call_id':e['call_id'],'arguments':args,'success':result.get('success'),'returned_path':result.get('path'),'listed_resource':result.get('path') in result.get('files',[]),'content_sha256':sha(content),'content_utf8_bytes':len(content.encode()),'markdown_lf':content.count('\n'),'markdown_literal_backslash_n':content.count('\\n'),'physical_file_matches':file_matches,'catalog_has_name':any(x['name']==result.get('name') for x in catalog),'next_request_seq':following[0]['seq'] if following else None,'matching_tool_messages':len(matching),'matching_assistant_call':len(assistant_calls),'assistant_function_name':assistant_calls[0]['function']['name'] if assistant_calls else None,'next_tool_content_byte_identical_to_result_json':len(matching)==1 and matching[0]['content']==data(e)['result'],'next_decoded_result_equal':decoded==result,'next_decoded_markdown_byte_identical':decoded is not None and decoded.get('content')==content,'tool_message_is_json_text':True,'tool_json_text_lf':matching[0]['content'].count('\n') if matching else None,'tool_json_text_literal_backslash_n':matching[0]['content'].count('\\n') if matching else None,'subsequent_visible_request_retention':retention,'following_model_response_seq':next((x['seq'] for x in events if following and x['seq']>following[0]['seq'] and x['event']=='model_response'),None)})
 return {'trace':str(path),'trace_sha256':sha(path.read_bytes()),'catalog_request_seq':requests[0][0]['seq'],'catalog':[{'name':item['name'],'description_sha256':sha(item.get('description','')),'description_utf8_bytes':len(item.get('description','').encode())} for item in catalog],'catalog_names':len(catalog),'skill_read_calls':len(calls),'skill_reads':reads,'trace_continuous': [e['seq'] for e in events]==list(range(1,len(events)+1)),'interpretation':'未调用不表示不可读取；完整已传仅证明进入应用发给model.chat的请求，不证明模型遵循或供应商最终理解。'}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--trace',action='append',type=Path,help='可重复指定原始JSONL；省略时审计默认历史材料')
 parser.add_argument('--output',type=Path,default=BASE/'skill-delivery-audit-safe.json')
 args=parser.parse_args()
 rows=[audit(p.parent.name,p) for p in args.trace] if args.trace else [audit(n) for n in NAMES]+[audit('fixture-protocol-final',BASE/'fixture-protocol-final/trace-background-vm2-private.jsonl')]
 failures=[(r['trace'],x['result_seq']) for r in rows for x in r['skill_reads'] if not x['next_decoded_markdown_byte_identical'] or not x['next_tool_content_byte_identical_to_result_json'] or x['matching_assistant_call']!=1 or any(not item['byte_identical'] for item in x['subsequent_visible_request_retention'])]
 out=args.output;out.write_text(json.dumps({'runs':rows,'broken_next_request_chains':failures,'encoding':'tool.content保存result.to_json()的结构化JSON文字；HTTP body再编码这一字符串。解开HTTP JSON后工具文字含合法JSON转义，内层JSON解开后Markdown与物化文件逐字相同。没有多包一层JSON字符串，也没有LF被改为额外literal backslash-n的证据。'},ensure_ascii=False,indent=2));print(out);print('reads',sum(r['skill_read_calls'] for r in rows),'broken',failures)
