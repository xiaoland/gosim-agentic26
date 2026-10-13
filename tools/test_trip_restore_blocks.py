"""第38轮分片冷恢复：生产trip_load读取完整记录，恢复文档与全部命名块。"""
import hashlib,json,time
from pathlib import Path
from test_trip_replay import prepare as replay_prepare
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
    base=ROOT/'build/research/rail-integration/e2e'
    replay_prepare(jail,base/'private-state-round38/home/apps/os.agentic26-navigation')
    snapshot=json.loads((base/'round38/saved-full-snapshot-private.json').read_bytes())['data']['snapshot']
    assert len(snapshot['blocks'])==6
    (Path(jail)/'restore-expected-blocks.json').write_text(json.dumps(snapshot['blocks'],ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
let rb_model=0 let rb_provider=0 let rb_restore_calls=0 let rb_started=0 let rb_done=false
fn minimax_request(task,input,schema,token,record,done){rb_model+=1}
fn amap_request(path,params,token,done){rb_provider+=1}
fn trip_restore(){rb_restore_calls+=1 product_trip_restore() rb_started=time_now() start_timeout(0.05,||rb_poll())}
fn rb_poll(){let ready=true for block in ui_blocks {if !block.installed || !block.notified {ready=false}}
 if (!ready || ui_blocks.len()!=6) && time_now()-rb_started<4 {start_timeout(0.05,||rb_poll()) return}
 if rb_done{return} rb_done=true let blocks=[] for block in ui_blocks {blocks.push({id:block.id document:block.document raw_source:block.raw_source visible:block.visible installed:block.installed notified:block.notified complete:block.complete diagnostic:if block.installed {block.handle.diagnostics()} else {block.error}})}
 fs.write("restore-blocks-result.json",{blocks:blocks replay:trip_replay selected:trip_selected_id restore_calls:rb_restore_calls model_calls:rb_model provider_calls:rb_provider loading:trip_loading runtime_status:runtime_status guardian_error:guardian_error}.to_json())
}
'''
def source(original):
    for name in ['trace_initialize','minimax_request','amap_request','trip_restore']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    return original+'\n'+FIXTURE

def run(work,jail,original,injected):
    for _ in range(700):
        if (jail/'restore-blocks-result.json').exists():break
        time.sleep(.02)
    observed=json.loads((jail/'restore-blocks-result.json').read_bytes());expected=json.loads((jail/'restore-expected-blocks.json').read_bytes());blocks=observed['blocks'];checks=[]
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    check('生产trip_load分片后trip_restore一次恢复六完整身份',observed['replay'] and not observed['loading'] and observed['restore_calls']==1 and [b['id'] for b in blocks]==[b['id'] for b in expected])
    check('文档与命名块原稿document元数据保持',all(b['raw_source']==e['source'] and b['document']==e['document'] for b,e in zip(blocks,expected)))
    check('原可见性保持且hidden overlay不自动展开',all(b['visible']==(False if e['overlay'] else e['visible']) for b,e in zip(blocks,expected)))
    check('六块实际安装首次通知完成且无子VM诊断',len(blocks)==6 and all(b['installed'] and b['notified'] and b['complete'] and not b['diagnostic'] for b in blocks))
    check('冷恢复无模型或交通调用',observed['model_calls']==0 and observed['provider_calls']==0)
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'observed':observed,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'原38索引manifest与全部parts复制，生产trip_load→trip_read分片读取；Python对照完整snapshot只用于六块expected，不送单个1.23MB文件到native；未验证Android卡片地图交互。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks),str(work/'report.json')
