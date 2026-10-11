#!/usr/bin/env python3
"""提取真实接驳调用与显式助手内容；不按调用数量自动判定策略质量。"""
import argparse
import collections
import hashlib
import json
from pathlib import Path


def analyze(path):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    calls = {}
    runs = {}
    for event in events:
        run = runs.setdefault(str(event['run']), {'calls': [], 'results': [], 'assistant_content': [], 'model_responses': 0})
        data = json.loads(event['data']) if isinstance(event['data'], str) else event['data']
        seq = event['seq']
        if event['event'] == 'tool_call':
            name = data['name']
            try:
                args = json.loads(data['arguments'])
            except json.JSONDecodeError:
                args = {'unparsed_arguments': data['arguments']}

            calls[event['call_id']] = {'seq': seq, 'name': name, 'arguments': args}
            if not name.startswith('render'):
                item = {'seq': seq, 'name': name, 'arguments': args}
                if name == 'extend_route':
                    item['branch_kind'] = ('origin_to_node' if args.get('route_id') == 'origin' and args.get('to_ref') != 'destination'
                                           else 'terminal_walk' if args.get('mode') == 'walk' and args.get('to_ref') == 'destination'
                                           else 'continuation')
                run['calls'].append(item)
        elif event['event'] == 'tool_result' and data['name'] in ('query_route', 'extend_route', 'get_route', 'get_route_graph', 'search_places', 'quote_didi', 'attach_quote', 'read_skill'):
            result = json.loads(data['result'])
            item = {'seq': seq, 'name': data['name'], 'call_seq': calls.get(event['call_id'], {}).get('seq'),
                    'success': result.get('success'), 'error': result.get('error')}
            # 只输出路由事实，避免复印地图URL或供应商原始报文。
            if data['name'] == 'read_skill':
                content = result.get('content', '')
                item['skill'] = {'name': result.get('name'), 'path': result.get('path'),
                                 'content_sha256_literal': hashlib.sha256(content.encode()).hexdigest(),
                                 'content_sha256_normalized_newlines': hashlib.sha256(content.replace('\\n', '\n').encode()).hexdigest()}
            if 'new_nodes' in result:
                item['new_nodes'] = [{k: v for k, v in n.items() if k not in ('longitude', 'latitude', 'city_metadata')} for n in result['new_nodes']]
            route_list = result.get('routes', [result['route']] if result.get('route') else [])
            item['routes'] = [{k: r.get(k) for k in ('id', 'mode', 'kind', 'duration_seconds', 'cost', 'assessment', 'steps', 'segments', 'legs', 'completion_status', 'node_ref', 'derived_from_route_id')} for r in route_list]
            if result.get('quotes'):
                item['quotes'] = [{k: q.get(k) for k in ('ref', 'product_name', 'price_cents', 'discounted_price_text', 'eta', 'basis')} for q in result['quotes']]
            if data['name'] == 'search_places':
                item['places'] = [{k: p.get(k) for k in ('id', 'name', 'node_ref')} for p in result.get('places', [])]
            run['results'].append(item)
        elif event['event'] == 'model_request' and 'request_contract' not in run:
            body = json.loads(data['body'])
            system = next((m.get('content', '') for m in body.get('messages', []) if m.get('role') == 'system'), '')
            prefix = system.split('\n', 1)[0]
            run['request_contract'] = {'seq': seq, 'system_content': system, 'system_literal_first_line_characters': len(prefix),
                                       'system_sha256': hashlib.sha256(system.encode()).hexdigest(),
                                       'tool_names': [t['function']['name'] for t in body.get('tools', [])]}
        elif event['event'] == 'model_response':
            body = json.loads(data['body'])
            for choice in body.get('response', body).get('choices', []):
                content = choice['message'].get('content')
                if content:
                    run['assistant_content'].append({'seq': seq, 'finish_reason': choice.get('finish_reason'), 'content': content})
            run['model_responses'] += 1
        elif event['event'] == 'query_ended':
            run['query_ended_seq'] = seq
    seqs = [e['seq'] for e in events]
    return {'trace': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'events': len(events), 'sequence_continuous': bool(seqs) and seqs == list(range(seqs[0], seqs[-1] + 1)),
            'event_counts': dict(collections.Counter(e['event'] for e in events)), 'runs': runs,
            'interpretation': 'origin_to_node与后续非walk的完整腿需一起核对；terminal_walk仅补末段。passed=false可保留候车/连接未知，不自动判探索失败。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(Path(__file__).resolve().parents[1] / 'build')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(analyze(args.trace), ensure_ascii=False, indent=2))
    args.output.chmod(0o600)
    print(args.output)


if __name__ == '__main__':
    main()
