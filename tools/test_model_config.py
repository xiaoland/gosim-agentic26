#!/usr/bin/env python3
"""验证开发宿主的模型凭据归属、额度更新和历史记录脱敏。"""
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import agent


def main():
    (agent.ROOT / 'build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='model-config-', dir=agent.ROOT / 'build') as work:
        agent.STATE = Path(work)
        agent.HOME_DIR = agent.STATE / 'home'
        agent.CORE = agent.STATE / 'core'
        jail = agent.HOME_DIR / 'apps/os.agentic26-navigation'
        ledger_path = agent.HOME_DIR / 'apps/.host/model/ledger.json'
        original = {'day': 20736, 'apps': {'os.agentic26-navigation': {'calls': 11, 'tokens': 284057}},
                    'limits': {'other-app': {'per_minute': 3, 'calls_per_day': 4, 'tokens_per_day': 500}}}
        agent.write_private(ledger_path, agent.json_bytes(original))
        values = {'MINIMAX_API_KEY': 'fixture-model-private-key', 'MINIMAX_BASE_URL': 'https://api.minimax.cn/v1',
                  'AMAP_API_KEY': 'fixture-map-private-key'}
        with patch.object(agent, 'materialize_skills'):
            agent.configure(values, jail)
            agent.configure(values, jail)
        ledger = json.loads(ledger_path.read_bytes())
        assert ledger['day'] == original['day'] and ledger['apps'] == original['apps']
        assert ledger['limits']['other-app'] == original['limits']['other-app']
        assert ledger['limits']['os.agentic26-navigation'] == {'per_minute': 20, 'calls_per_day': 100, 'tokens_per_day': 1_000_000}
        config = json.loads((jail / 'private-config.json').read_bytes())
        assert not any(name.startswith('minimax_') for name in config)
        assert values['MINIMAX_API_KEY'].encode() not in (jail / 'private-config.json').read_bytes()
        profile = json.loads((agent.CORE / 'profiles/_main.json').read_bytes())
        assert profile['config']['llm']['fallbacks'] == []
        assert profile['config']['llm']['primary']['model_id'] == 'MiniMax-M3'
        configured = agent.configured_secrets(config)
        assert configured['MINIMAX_API_KEY'] == values['MINIMAX_API_KEY']
        try:
            agent.no_secrets(values['MINIMAX_API_KEY'].encode(), configured, '测试导出')
        except RuntimeError:
            pass
        else:
            raise AssertionError('宿主模型 key 必须阻止日志导出')
    print('PASS: 宿主独占模型凭据、仅本应用额度覆盖、当日使用量保留、宿主 key 导出阻断')


if __name__ == '__main__':
    main()
