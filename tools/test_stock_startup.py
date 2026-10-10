#!/usr/bin/env python3
"""在指定官方 card-host 上验证真实 bundle 的手机首屏与缺能力入口。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', required=True, type=Path)
    parser.add_argument('--host-revision', required=True)
    args = parser.parse_args()
    binary = args.binary.resolve()
    output_root = ROOT / 'build/smoke'
    output_root.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='stock-startup-', dir=output_root))
    bundle = work / 'bundle'
    shutil.copytree(ROOT / 'bundle', bundle)
    command = [str(binary), '--bundle', str(bundle), '--app-data', str(work / 'data'),
               '--allow-unsigned', '--stamp', '--size', '390x844', '--remote']
    log = work / 'native.log'
    process = None
    port = None
    report = {'host_revision': args.host_revision,
              'source_sha256': hashlib.sha256((bundle / 'main.splash').read_bytes()).hexdigest(),
              'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
              'mode': 'macOS arm64 card-host，390×844 手机视口，非 Android 模式或真机',
              'command': command, 'passed': False}

    def request(route, **params):
        suffix = '?' + urlencode(params) if params else ''
        return urlopen(f'http://127.0.0.1:{port}/{route}{suffix}', timeout=15).read()

    def snapshot():
        # Splash 的 text 是完整源码；证据只保留真实控件。
        return [row for row in json.loads(request('snap'))['s'] if row.get('ty') != 'Splash']

    try:
        with log.open('wb') as stream:
            process = subprocess.Popen(command, cwd=work,
                                       env=dict(os.environ, MAKEPAD_HIDE_WINDOWS='1'),
                                       stdout=stream, stderr=subprocess.STDOUT)
        for _ in range(150):
            assert process.poll() is None, log.read_text()[-2000:]
            match = re.search(rb'listening on 127\.0\.0\.1:(\d+)', log.read_bytes())
            if match:
                port = int(match[1])
                break
            time.sleep(.1)
        assert port, '隔离宿主未开放远程检查接口'
        time.sleep(2)
        rows = snapshot()
        assert any('当前宿主缺少 Navigation' in row.get('t', '') and row['r'][3] > 0 for row in rows)
        (work / 'first.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
        (work / 'first.png').write_bytes(request('g', raw=1))
        button = next(row for row in rows if row.get('ty') == 'Button' and row.get('t') == '查询（不可用）')
        x, y, width, height = button['r']
        request('m', k='click', x=x + width / 2, y=y + height / 2, wait=1)
        entry = next(row for row in rows if row.get('ty') == 'TextInput')
        x, y, width, height = entry['r']
        request('m', k='click', x=x + width / 2, y=y + height / 2, wait=1)
        request('k', c='KeyA', cmd=1, wait=1)
        request('t', t='去机场，预算 50 元', wait=1)
        request('k', c='enter', wait=1)
        time.sleep(.5)
        rows = snapshot()
        assert any('当前宿主缺少 Navigation' in row.get('t', '') and row['r'][3] > 0 for row in rows)
        assert any(row.get('t') == '查询（不可用）' for row in rows)
        (work / 'after-input.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
        (work / 'after-input.png').write_bytes(request('g', raw=1))
        assert any(row.get('ty') == 'TextInput' and row.get('t') == '去机场，预算 50 元' for row in rows)
        errors = [line for line in log.read_text().splitlines() if '[E]' in line or 'panicked' in line]
        assert not errors, errors
        report.update(passed=True, checks=['空配置首屏说明可见', '查询按钮不可用', '输入回车不能绕过能力门', '无原生脚本错误'])
    finally:
        if process and process.poll() is None:
            try:
                request('quit')
            except OSError:
                process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=15)
        report['own_closed'] = process is not None and process.poll() is not None
        (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(f"{'PASS' if report['passed'] else 'FAIL'}: {work / 'report.json'}")


if __name__ == '__main__':
    main()
