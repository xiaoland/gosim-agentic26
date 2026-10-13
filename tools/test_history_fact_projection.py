"""历史快照改变查看路线后，对象投影与编码必须使用同一选择。"""
import json, time, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):
 p=Path(jail)/'history-facts-fixture';p.mkdir()
 snapshot=json.loads((ROOT/'build/research/rail-integration/e2e/round30/saved-full-snapshot-private.json').read_bytes())['data']['snapshot']
 (p/'facts.json').write_text(json.dumps({'facts':snapshot['facts'],'captured_at':snapshot['captured_at'],'route_data':[{'id':'route_2_33'}]},ensure_ascii=False,separators=(',',':')))
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn agent_pump(token){}
fn hf_begin(){fs.read_async("history-facts-fixture/facts.json",fn(result){if !result.success{return}
 trip_replay=true trip_history=result.text.parse_json() viewed_route_id="route_2_33"
 let route=trip_history_route(viewed_route_id)
 route.map_paths_cache=[{index:0 point_count:2 start:"113.813772,22.624076" end:"113.814544,22.624627"}]
 start_timeout(0.01,||{
  let projected=interface_facts_with_routes([])
  let encoded=projected.to_json()
  let parsed=encoded.parse_json()
  let selected=nil let original=nil
  for route in parsed.routes {if route.id==viewed_route_id {selected=route}}
  for route in trip_history.facts.routes {if route.id==viewed_route_id {original=route}}
  let observation={catalog_merged:selected.map_paths!=nil catalog_count:selected.map_paths.len() original_catalog_unchanged:original.map_paths==nil duration_unchanged:selected.duration_seconds==original.duration_seconds metadata_status:selected.map_metadata.catalog_status parent_viewed:viewed_route_id projected_viewed:projected.viewed_route_id encoded_viewed:parsed.viewed_route_id original_viewed:trip_history.facts.viewed_route_id}
  start_timeout(0.01,||{fs.write("history-facts-observation.json",observation.to_json()) fs.write("history-facts-encoded.json",encoded)})
 })
})}
start_timeout(0.8,||hf_begin())
'''
def source(original):
 for name in ['trace_initialize','trip_load','agent_pump']:
  original=original.replace('fn '+name+'(','fn product_'+name+'(',1)
 return original+'\n'+FIXTURE

def run(work,jail,original,injected):
 for _ in range(500):
  if (jail/'history-facts-observation.json').exists() and (jail/'history-facts-encoded.json').exists():break
  time.sleep(.02)
 observation=json.loads((jail/'history-facts-observation.json').read_bytes())
 encoded=(jail/'history-facts-encoded.json').read_text()
 report={'observation':observation,'viewed_field_occurrences':encoded.count('"viewed_route_id":'),'product_source_sha256':hashlib.sha256(original.encode()).hexdigest(),'native_errors':[x for x in (work/'native.log').read_text().splitlines() if '[E]' in x],'model_requested':False,'provider_requested':False}
 report['passed']=observation['parent_viewed']==observation['projected_viewed']==observation['encoded_viewed']=='route_2_33' and observation['original_viewed']=='' and report['viewed_field_occurrences']==1 and observation['catalog_merged'] and observation['catalog_count']==1 and observation['original_catalog_unchanged'] and observation['duration_unchanged'] and observation['metadata_status']=='ready'
 (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 assert report['passed'], str(work/'report.json')
