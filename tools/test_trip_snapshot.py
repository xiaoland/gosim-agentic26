"""用第十四轮真实候选验证完整大出行快照的分片提交与恢复，不调用供应商。"""
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'build/research/rail-integration/e2e'

FIXTURE = r'''
let snapshot_checks=[] let snapshot_facts=nil let snapshot_blocks=nil
let snapshot_captured=nil let snapshot_bytes=0 let snapshot_primary=""
let snapshot_first_transaction=nil
let snapshot_manifest=nil let snapshot_record_file="" let snapshot_part_text=""
fn snapshot_check(name,passed){snapshot_checks.push({name:name passed:passed}) let progress={stage:name snapshot_bytes:snapshot_bytes checks:snapshot_checks} start_timeout(0.01,||fs.write("snapshot-progress.json",progress.to_json()))}
fn snapshot_finish(){fs.write("harness-smoke.json",{checks:snapshot_checks snapshot_bytes:snapshot_bytes routes:candidates.len() storage_error:guardian_error generation:trip_generation loading:trip_loading}.to_json())}
fn interface_facts(){if snapshot_facts!=nil {return snapshot_facts} return product_interface_facts()}
fn snapshot_read_equal(read,label){
 if read==nil {return false}
 let expected=snapshot_captured.to_json().utf8_chunks(262144)
 let actual=read.data.trips[0].snapshot.to_json().utf8_chunks(262144)
 for index part in expected {fs.write("snapshot-"+label+"-expected-"+index+".text",part)}
 for index part in actual {fs.write("snapshot-"+label+"-actual-"+index+".text",part)}
 fs.write("snapshot-"+label+"-dump.json",{expected:expected.len() actual:actual.len()}.to_json())
 return true
}
fn snapshot_read_file(path,done){fs.read_async(path,fn(reply){if !reply.success {snapshot_check("真实夹具可读取",false) snapshot_finish() return} done(reply.text.parse_json())})}
fn snapshot_load_route(index){
 if index>=10 {snapshot_begin() return}
 snapshot_read_file("snapshot-fixture/route-"+index+".json",fn(route){candidates.push(route) start_timeout(0.01,||snapshot_load_route(index+1))})
}
fn snapshot_dirty_data(){let data=trip_edit_state() data.trips[0]._dirty=true return data}
fn snapshot_begin(){
 let primitive="中文🙂".utf8_chunks(4) fs.write("snapshot-primitive.json",{pieces:primitive.len()}.to_json())
 route_nodes={} for node in snapshot_facts.route_graph.nodes {route_nodes[node.ref]=node}
 position_record=snapshot_facts.origin destination_record=snapshot_facts.destination
 user_limits=snapshot_facts.limits constraints=snapshot_facts.limits received_at=snapshot_facts.received_at arrive_by=snapshot_facts.arrive_by
 didi_quotes=snapshot_facts.taxi_quotes didi_places=snapshot_facts.taxi_quote_places guardian_goal=nil guardian_pending=nil
 answer_text=snapshot_facts.answer let old_blocks=ui_blocks ui_blocks=snapshot_blocks
 snapshot_captured=trip_capture() ui_blocks=old_blocks snapshot_bytes=snapshot_captured.to_json().len()
 fs.write("snapshot-progress.json",{stage:"captured" snapshot_bytes:snapshot_bytes routes:snapshot_captured.route_data.len()}.to_json())
 snapshot_check("真实10候选materialize快照超过单文件1MiB",snapshot_bytes>1048576 && snapshot_captured.route_data.len()==10)
 let now=time_now()
 trip_records=[] trip_selected_id=nil trip_next_id=1 trip_generation=0
 let trip={id:"trip-1" title:"真实分片回放" input:"隔离保存回归" created_at:now updated_at:now status:"completed" goal:nil snapshot:snapshot_captured _dirty:true}
 trip_commit({schema:1 selected_id:trip.id next_id:2 trips:[trip]},fn(saved){
  snapshot_check("完整大快照提交成功",saved && trip_generation==1)
  if !saved {let tx=snapshot_first_transaction fs.write("snapshot-failed-tx.json",{parts_array:route_get(tx,"parts").is_array() part_index:route_get(tx,"part_index") file:route_get(tx,"file") total:route_get(tx,"total") cancelled:route_get(tx,"cancelled") base_generation:route_get(tx,"base_generation") transaction_run:route_get(tx,"run") current_run:run_id}.to_json()) snapshot_finish() return}
  trip_read("navigation-trips.json",fn(read){
   fs.write("snapshot-read-diagnostic.json",{read_nil:read==nil error:guardian_error expected_bytes:snapshot_captured.to_json().len() actual_bytes:if read!=nil {read.data.trips[0].snapshot.to_json().len()} else {0} expected_captured_at:snapshot_captured.captured_at actual_captured_at:if read!=nil {read.data.trips[0].snapshot.captured_at} else {nil}}.to_json())
   snapshot_check("完整facts几何原稿读回等值",snapshot_read_equal(read,"first"))
   snapshot_read_file("navigation-trips.json",fn(index){
    snapshot_record_file=index.data.trips[0].file
    snapshot_read_file(snapshot_record_file,fn(manifest){
     snapshot_manifest=manifest
     snapshot_check("revision manifest按顺序引用多个完整分片",manifest.complete=="navigation-trip-parts-v1" && manifest.parts.len()>1 && manifest.total_bytes>1048576)
     fs.read_async("navigation-trips.json",fn(reply){snapshot_primary=reply.text snapshot_missing()})
    })
   })
  })
 })
 snapshot_first_transaction=trip_pending_commit
}
fn snapshot_missing(){
 let part=snapshot_manifest.parts[0]
 fs.read_async(part.file,fn(reply){
  snapshot_part_text=reply.text fs.remove(part.file)
  trip_read("navigation-trips.json",fn(read){
   snapshot_check("缺片拒绝恢复并保现有内存state",read==nil && trip_generation==1 && trip_records[0].snapshot==snapshot_captured)
   fs.write(part.file,snapshot_part_text) snapshot_reordered()
  })
 })
}
fn snapshot_manifest_text(manifest){let data={schema:manifest.schema saved_at:manifest.saved_at id:manifest.id revision:manifest.revision file:manifest.file parts:manifest.parts total_bytes:manifest.total_bytes} return data.to_json().strip_suffix("}")+",\"complete\":\"navigation-trip-parts-v1\"}"}
fn snapshot_reordered(){
 let reordered=snapshot_manifest.to_json().parse_json()
 let first=reordered.parts[0] reordered.parts[0]=reordered.parts[1] reordered.parts[1]=first
 fs.write(snapshot_record_file,snapshot_manifest_text(reordered))
 trip_read("navigation-trips.json",fn(read){
  snapshot_check("重排分片引用拒绝恢复并保现有state",read==nil && trip_generation==1 && trip_records[0].snapshot==snapshot_captured)
  fs.write(snapshot_record_file,snapshot_manifest_text(snapshot_manifest))
  snapshot_legacy()
 })
}
fn snapshot_legacy(){
 let now=time_now() let legacy={id:"trip-999" title:"旧单文件" input:"legacy" created_at:now updated_at:now status:"completed" goal:nil snapshot:{captured_at:now facts:{legacy:true} blocks:[] route_data:[]}}
 fs.write("navigation-trip-trip-999-1.json","{\"schema\":1,\"saved_at\":"+now.to_json()+",\"data\":"+legacy.to_json()+",\"complete\":\"navigation-trip-v1\"}")
 fs.write("snapshot-legacy-index.json",trip_encode({schema:1 selected_id:"trip-999" next_id:1000 generation:1 trips:[{id:"trip-999" file:"navigation-trip-trip-999-1.json"}]}))
 trip_read("snapshot-legacy-index.json",fn(read){
  snapshot_check("legacy单文件出行完整恢复",read!=nil && read.data.trips[0].snapshot.facts.legacy==true && read.data.selected_id=="trip-999")
  snapshot_write_failure()
 })
}
fn snapshot_write_failure(){
 let failed_file=trip_part_name("navigation-trip-trip-1-2.json",1)
 fs.mkdir(failed_file)
 trip_commit(snapshot_dirty_data(),fn(saved){
  snapshot_check("分片写失败不发布新generation且保完整旧state",!saved && trip_generation==1 && trip_records[0].snapshot==snapshot_captured && trip_pending_commit==nil)
  fs.read_async("navigation-trips.json",fn(reply){
   snapshot_check("失败保旧primary且清理新revision",reply.success && reply.text==snapshot_primary && !fs.exists("navigation-trip-trip-1-2.json") && !fs.exists(trip_part_name("navigation-trip-trip-1-2.json",0)) && !fs.exists(trip_part_name("navigation-trip-trip-1-2.json",1)))
   snapshot_manifest_failure()
  })
 })
}
fn snapshot_manifest_failure(){
 let file="navigation-trip-trip-1-2.json" fs.mkdir(file)
 trip_commit(snapshot_dirty_data(),fn(saved){
  snapshot_check("manifest写失败保旧state并清理新分片",!saved && trip_generation==1 && trip_records[0].snapshot==snapshot_captured && !fs.exists(file) && !fs.exists(trip_part_name(file,0)))
  snapshot_primary_failure()
 })
}
fn snapshot_primary_failure(){
 fs.remove("navigation-trips.json") fs.mkdir("navigation-trips.json")
 trip_commit(snapshot_dirty_data(),fn(saved){
  snapshot_check("primary写失败不推进generation或替换内存state",!saved && trip_generation==1 && trip_records[0].snapshot==snapshot_captured && !fs.exists("navigation-trip-trip-1-2.json") && !fs.exists(trip_part_name("navigation-trip-trip-1-2.json",0)))
  fs.remove("navigation-trips.json") fs.write("navigation-trips.json",snapshot_primary)
  trip_read("navigation-trips.json",fn(read){
   snapshot_check("primary故障移除后旧完整详情仍可恢复",snapshot_read_equal(read,"restored"))
   snapshot_cancel()
  })
 })
}
fn snapshot_cancel(){
 let old_run=run_id let callbacks=0
 trip_commit(snapshot_dirty_data(),fn(saved){
  callbacks+=1
  snapshot_check("取消提交只结案一次且不能发布旧查询",!saved && callbacks==1 && run_id!=old_run && trip_generation==1 && trip_pending_commit==nil)
  fs.read_async("navigation-trips.json",fn(reply){
   snapshot_check("取消保持旧primary与完整快照",reply.success && reply.text==snapshot_primary && trip_records[0].snapshot==snapshot_captured && !fs.exists(trip_part_name("navigation-trip-trip-1-2.json",0)))
   snapshot_retry()
  })
 })
 start_timeout(0.01,||snapshot_cancel_started())
}
fn snapshot_retry(){
 trip_commit(snapshot_dirty_data(),fn(saved){
  snapshot_check("同VM失败取消后真实大快照可以重试成功",saved && trip_generation==2)
  trip_read("navigation-trips.json",fn(read){
   snapshot_check("同VM重复保存仍完整等值",read!=nil && read.data.generation==2 && snapshot_read_equal(read,"repeated"))
   snapshot_finish()
  })
 })
}
fn snapshot_cancel_started(){
 if trip_pending_commit==nil {snapshot_check("分片取消发生在pending事务内",false) snapshot_finish() return}
 if trip_pending_commit.part_index<1 {start_timeout(0.01,||snapshot_cancel_started()) return}
 snapshot_check("取消发生在真实分片已写入之后",trip_pending_commit.written.len()>0)
 trip_cancel_commit() run_id+=1
}
start_timeout(1,||{
 snapshot_read_file("snapshot-fixture/facts.json",fn(facts){snapshot_facts=facts
  snapshot_read_file("snapshot-fixture/blocks.json",fn(blocks){snapshot_blocks=blocks candidates=[] snapshot_load_route(0)})
 })
})
'''


def recorded_fixture():
    events = [json.loads(line) for line in (EVIDENCE / 'round14/trace-private.jsonl').read_text().splitlines()]
    render = next(event for event in events if event['seq'] == 308)
    source = json.loads(render['data'])['source']
    start = source.index('text:', source.index('fact_state := Label')) + len('text:')
    facts_text, _ = json.JSONDecoder().raw_decode(source[start:])
    facts = json.loads(facts_text)
    call = next(event for event in events if event['seq'] == 307)
    arguments = json.loads(json.loads(call['data'])['arguments'])
    routes = [next((EVIDENCE / 'private-state-round14').rglob(f'first-render-2-route-{index}.json')) for index in range(10)]
    return facts, arguments, routes


def source(original):
    return original.replace('fn interface_facts(', 'fn product_interface_facts(', 1) + '\n' + FIXTURE


def prepare(jail):
    facts, arguments, routes = recorded_fixture()
    directory = jail / 'snapshot-fixture'
    directory.mkdir()
    (directory / 'facts.json').write_text(json.dumps(facts, ensure_ascii=False, separators=(',', ':')))
    blocks = [{
        'id': arguments['id'], 'raw_source': arguments['source'], 'complete': True, 'installed': True, 'error': '',
        'overlay': arguments['overlay'], 'height': arguments['height'], 'visible': True, 'document': None,
    }]
    (directory / 'blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, separators=(',', ':')))
    segments_bytes = 0
    for index, path in enumerate(routes):
        candidate = json.loads(path.read_text())
        segments_bytes += len(json.dumps(candidate['segments'], ensure_ascii=False, separators=(',', ':')).encode())
        (directory / f'route-{index}.json').write_bytes(path.read_bytes())
    assert segments_bytes == 893884
    assert len((directory / 'facts.json').read_bytes()) == 244659


def read_record(jail, filename):
    """读回业务 record（data 字段）；用于旧测试兼容单文件与固定 revision 分片。"""
    jail = Path(jail)
    manifest = json.loads((jail / filename).read_text())
    if manifest['complete'] == 'navigation-trip-v1':
        return manifest['data']
    assert manifest['complete'] == 'navigation-trip-parts-v1'
    assert manifest['file'] == filename and manifest['parts']
    texts = []
    total = 0
    for index, part in enumerate(manifest['parts']):
        assert part['file'] == filename.removesuffix('.json') + f'-part-{index}.text'
        raw = (jail / part['file']).read_bytes()
        assert len(raw) == part['bytes'] and len(raw) <= 1048576
        total += len(raw)
        texts.append(raw.decode('utf-8'))
    assert total == manifest['total_bytes']
    parsed = json.loads(''.join(texts))
    assert parsed['complete'] == 'navigation-trip-v1'
    assert parsed['data']['id'] == manifest['id']
    return parsed['data']


def run(work, jail, original, injected):
    report = None
    for _ in range(1500):
        try:
            report = json.loads((jail / 'harness-smoke.json').read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        if report:
            break
        log = work / 'native.log'
        if log.exists() and any(token in log.read_text() for token in ('is reserved and cannot', 'contained a mini-app isolate panic', 'script heap allocation limit exceeded', 'push_all_fn_args called without prototype', 'instruction limit reached')):
            progress = jail / 'snapshot-progress.json'
            report = {'checks': [{'name': '原生回归完成', 'passed': False}],
                      'progress': json.loads(progress.read_text()) if progress.exists() else None}
            break
        time.sleep(.1)
    assert report, str(work / 'native.log')
    errors = [line for line in (work / 'native.log').read_text().splitlines() if '[E]' in line]
    report.update(product_source_sha256=hashlib.sha256(original.encode()).hexdigest(),
                  recorded_round=14, facts_bytes=244659, original_segments_bytes=893884,
                  model_called=False, provider_called=False, native_errors=errors)
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert not errors, errors
    for label in ('first', 'restored', 'repeated'):
        metadata = json.loads((jail / f'snapshot-{label}-dump.json').read_text())
        decoded = {}
        for kind in ('expected', 'actual'):
            text = ''.join((jail / f'snapshot-{label}-{kind}-{i}.text').read_text()
                           for i in range(metadata[kind]))
            decoded[kind] = json.loads(text)
        assert decoded['expected'] == decoded['actual'], label
    report['native_async_snapshot_structural_equality'] = ['first', 'restored', 'repeated']
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert all(check['passed'] for check in report['checks']), report
    index = json.loads((jail / 'navigation-trips.json').read_text())['data']
    manifest = json.loads((jail / index['trips'][0]['file']).read_text())
    record = read_record(jail, index['trips'][0]['file'])
    facts, arguments, routes = recorded_fixture()
    assert record['snapshot']['facts'] == facts
    assert record['snapshot']['blocks'][0]['source'] == arguments['source']
    assert [route['segments'] for route in record['snapshot']['route_data']] == [json.loads(path.read_text())['segments'] for path in routes]
    assert len(record['snapshot']['route_data']) == 10
    print(f'PASS: {len(report["checks"])} 项真实大出行快照检查；{work / "report.json"}')
