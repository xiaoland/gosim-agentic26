#!/usr/bin/env python3
"""复用既有私有状态启动一轮接驳观察；不创建、重置或修改模型账本。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import uuid
import agent

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'build/research/journey-guardian/online/private-state'
EVIDENCE = ROOT / 'build/research/transfer-exploration/online'
agent.STATE = STATE
agent.HOME_DIR = STATE / 'home'
agent.CORE = STATE / 'core'
agent.SESSION = STATE / 'session.json'


def preflight():
    ledger = agent.HOME_DIR / 'apps/.host/model/ledger.json'
    profile_path = agent.CORE / 'profiles/_main.json'
    profile = json.loads(profile_path.read_text())
    jail = agent.jail_path()
    config = json.loads((jail / 'private-config.json').read_text())
    assert profile['enabled'] and profile['config']['llm']['primary']['model_id'] == 'MiniMax-M3'
    assert profile['config']['env_vars'].get('MINIMAX_API_KEY')
    assert config.get('amap_api_key') and config.get('didi_mcp_key')
    return {'state': str(STATE), 'model': 'MiniMax-M3', 'model_key_present': True,
            'map_key_present': True, 'didi_key_present': True,
            'ledger': json.loads(ledger.read_text()), 'ledger_sha256': hashlib.sha256(ledger.read_bytes()).hexdigest(),
            'active_own_session': agent.SESSION.exists()}


def start():
    initial = preflight()
    assert not initial['active_own_session'], '当前私有实例未释放'
    executable_path = STATE / 'app/OctoSense Navigation.app/Contents/MacOS' / agent.BINARY.name
    assert not any(line.strip().split(None, 1)[-1] == str(executable_path)
                   for line in subprocess.check_output(['ps', '-axo', 'pid=,comm='], text=True).splitlines()), '私有实例仍在运行'
    values = agent.env_values()
    # 只采用实现owner已冻结的构建；此入口不编译、不改生产stage。
    metadata = json.loads((agent.BUILD / 'build.json').read_text())
    expected, staged = agent.bundle_files(values), agent.bundle_files(values, agent.STAGE)
    assert metadata['source_sha256'] == agent.source_digest(expected), '构建未覆盖当前冻结源'
    # stage仅规范运行时应用ID并重新盖manifest摘要，其余资源必须逐字一致。
    assert {k: v for k, v in expected.items() if k != 'manifest.json'} == {k: v for k, v in staged.items() if k != 'manifest.json'}, '暂存资源与冻结源不一致'
    assert json.loads(staged['manifest.json'])['id'] == metadata['runtime_id']
    assert metadata['host_binary_sha256'] == hashlib.sha256(agent.BINARY.read_bytes()).hexdigest()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.chmod(0o700)
    agent.init_demo()
    jail = agent.jail_path()
    agent.materialize_skills(agent.STAGE, jail)
    config_path = jail / 'private-config.json'
    config = json.loads(config_path.read_text())
    trace_session = uuid.uuid4().hex
    trace_root = jail / 'dev-trace' / trace_session
    agent.private_dir(trace_root)
    agent.write_private(trace_root / 'instance-counter.json', agent.json_bytes({'next': 1}))
    config.update(location_mode='demo', development_trace=True, development_trace_session=trace_session,
                  development_trace_metadata={'source_sha256': metadata['source_sha256'],
                                              'main_sha256': hashlib.sha256((ROOT / 'bundle/main.splash').read_bytes()).hexdigest(),
                                              'host_platform': 'darwin', 'host_architecture': 'arm64',
                                              'runtime_mode': 'unknown', 'model': 'MiniMax-M3'})
    agent.write_private(config_path, agent.json_bytes(config))
    executable = agent.packaged_host()
    log = EVIDENCE / 'native.log'
    with log.open('wb') as stream:
        process = subprocess.Popen([str(executable), '--remote', '--test-action', 'launch-' + metadata['runtime_id'].removeprefix('os.')],
                                   cwd=STATE, env=agent.host_env(False), stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(150):
        assert process.poll() is None, '私有宿主启动失败，保留native.log'
        match = re.search(rb'listening on 127\.0\.0\.1:(\d+) pid=(\d+)', log.read_bytes())
        if match:
            assert int(match[2]) == process.pid
            session = {'pid': process.pid, 'port': int(match[1]), 'process_stamp': agent.process_stamp(process.pid),
                       'hidden': False, 'log': str(log), 'jail': str(jail), 'trace_session': trace_session, **metadata}
            agent.write_private(agent.SESSION, agent.json_bytes(session))
            session['mounted_bundle'] = str(agent.mounted_bundle(metadata))
            agent.write_private(agent.SESSION, agent.json_bytes(session))
            assert preflight()['ledger_sha256'] == initial['ledger_sha256'], '启动不能改变账本'
            agent.write_private(EVIDENCE / 'preflight-safe.json', agent.json_bytes(initial))
            agent.write_private(EVIDENCE / 'startup-safe.json', agent.json_bytes({**metadata, 'trace_session': trace_session,
                                'mounted_bundle': session['mounted_bundle'], 'main_sha256': config['development_trace_metadata']['main_sha256']}))
            print(json.dumps({'pid': process.pid, 'port': session['port'], 'trace_session': trace_session}, ensure_ascii=False))
            return
        time.sleep(.2)
    process.terminate()
    process.wait(timeout=10)
    raise RuntimeError('启动超时，保留native.log')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'start', 'export', 'stop'])
    args = parser.parse_args()
    if args.action == 'preflight':
        print(json.dumps(preflight(), ensure_ascii=False, indent=2))
    elif args.action == 'start':
        start()
    elif args.action == 'export':
        agent.trace_output('trace-export', destination=EVIDENCE / 'trace-private.jsonl')
    elif args.action == 'stop':
        agent.stop()


if __name__ == '__main__':
    main()
