#!/usr/bin/env python3
"""Exercise the real native draft UI in an isolated card-host session."""
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OCTO = [sys.executable, str(ROOT / 'tools/octo')]
APP_ID = 'agentic26-navigation'
ERROR_PATTERN = r'^.*(?:\[E\]|splash:[0-9]+:|refused|on_render closure failed|callback error).*$'


def main():
    (ROOT / 'build/smoke').mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='run-', dir=ROOT / 'build/smoke'))
    # Copy the bundle so a test does not restamp or edit the development copy.
    import shutil
    shutil.copytree(ROOT / 'bundle', work / 'bundle')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    running = False
    logs = []
    draft = work / 'data' / APP_ID / 'trip-draft.json'

    def request(route, **params):
        with urlopen(base + route + ('?' + urlencode(params) if params else ''), timeout=10) as response:
            return response.read()

    def widgets():
        return [w for w in json.loads(request('/snap'))['s'] if w['ty'] != 'Splash']

    def find(predicate):
        found = [w for w in widgets() if predicate(w)]
        assert len(found) == 1, found
        return found[0]

    def click(widget):
        x, y, width, height = widget['r']
        assert 0 <= y and y + height <= 892, f'Control clipped: {widget}'
        request('/click', x=x+width/2, y=y+height/2, wait=1)

    def button(text):
        click(find(lambda w: w['ty'] == 'Button' and w.get('t') == text))

    def fill(field, text):
        click(find(lambda w: w['ty'] == 'TextInput' and w['i'] == field))
        request('/k', k='down', c='KeyA', cmd=1, wait=1)
        request('/k', k='down', c='Backspace', wait=1)
        if text:
            request('/t', t=text, wait=1)
        assert find(lambda w: w['i'] == field and w['ty'] == 'TextInput')['val'] == text

    def status(text):
        actual = find(lambda w: w['i'] == 'status' and w['ty'] == 'Label')['t']
        assert actual == text, (actual, text)

    def start():
        nonlocal running
        subprocess.run([*OCTO, 'run', str(work / 'bundle'), '--app-data', str(work / 'data'), '--port', str(port), '--hidden', '--detach'], cwd=ROOT, check=True)
        running = True
        # load() runs after the first frame; wait for its short startup timer.
        time.sleep(0.15)

    def stop(log_name=None):
        nonlocal running
        if running:
            request('/quit')
            running = False
            log = work / 'data/card-host.log'
            assert log.is_file(), f'Missing runtime log: {log}'
            text = log.read_text()
            if log_name:
                (work / log_name).write_text(text)
            else:
                logs.append(text)
            for _ in range(30):
                with socket.socket() as sock:
                    if sock.connect_ex(('127.0.0.1', port)) != 0:
                        return
                time.sleep(0.05)
            raise AssertionError('card-host did not release its port')

    try:
        start()
        status('No saved trip. Start with your constraints.')
        # The disclosure and actions must all be in the window.
        footer = find(lambda w: w.get('t') == 'Local draft only. No location or network access.')
        assert footer['r'][1] + footer['r'][3] <= 892
        button('Save draft')
        status('Enter an origin and a destination.')
        assert not draft.exists()
        fill('origin', 'Demo origin')
        fill('destination', 'Demo destination')
        for value in ('abc', '0', '1441', '-1'):
            fill('minutes', value)
            button('Save draft')
            assert not draft.exists(), f'Invalid time accepted: {value}'
        fill('minutes', '60')
        fill('budget', '-1')
        button('Save draft')
        status('Budget must be a non-negative amount.')
        assert not draft.exists()
        fill('budget', '50.25')
        button('Save draft')
        status('Draft saved locally and verified.')
        saved = json.loads(draft.read_text())
        assert saved == dict(schema=1, origin='Demo origin', destination='Demo destination', minutes='60', budget='50.25', objective='min_cost')
        print('PASS: empty/invalid input rejected; valid draft saved and read back')
        subprocess.run([*OCTO, 'shot', str(port), str(work / 'saved.png')], check=True)
        stop()
        start()
        status('Your saved draft has been restored.')
        for field in ('origin', 'destination', 'minutes', 'budget'):
            assert find(lambda w: w['i'] == field and w['ty'] == 'TextInput')['val'] == saved[field]
        print('PASS: all constraints survive restart')
        stop()
        # Exercise edit -> runtime failure -> log location -> repair in the copy.
        main_script = work / 'bundle/main.splash'
        source = main_script.read_text()
        fault = '    ui.debug_missing_method()\n'
        edited = source.replace('text: "Go your way."', 'text: "Edit loop verified."', 1)
        broken = edited.replace('fn save(){\n', 'fn save(){\n' + fault, 1)
        main_script.write_text(broken)
        start()
        find(lambda w: w['ty'] == 'Label' and w.get('t') == 'Edit loop verified.')
        status('Your saved draft has been restored.')
        button('Save draft')
        status('Your saved draft has been restored.')
        assert json.loads(draft.read_text()) == saved
        runtime_log = json.loads(request('/log', n=100))['l']
        fault_line = broken.splitlines().index(fault.rstrip('\n')) + 1
        # The pinned storage-only host prepends three lines to main.splash.
        reported_line = fault_line + 3
        assert any(re.search(r'splash:\d+:' + str(reported_line) + r':\d+', line)
                   and 'debug_missing_method' in line for line in runtime_log), runtime_log
        (work / 'fault-log.json').write_text(json.dumps(runtime_log, indent=2))
        (work / 'fault-tree.txt').write_bytes(request('/d'))
        stop(log_name='fault.log')
        fault_errors = re.findall(ERROR_PATTERN, (work / 'fault.log').read_text(), re.M)
        assert fault_errors and all('debug_missing_method' in line for line in fault_errors), fault_errors
        main_script.write_text(edited)
        start()
        find(lambda w: w['ty'] == 'Label' and w.get('t') == 'Edit loop verified.')
        status('Your saved draft has been restored.')
        button('Save draft')
        status('Draft saved locally and verified.')
        assert json.loads(draft.read_text()) == saved
        main_script.write_text(source)
        print(f'PASS: source edit loaded; callback error located at main.splash:{fault_line}; repair preserves saved state')
        fill('budget', '')
        button('Save draft')
        assert json.loads(draft.read_text())['budget'] == ''
        button('Clear draft')
        assert not draft.exists()
        assert all(w['val'] == '' for w in widgets() if w['ty'] == 'TextInput')
        stop()
        start()
        status('No saved trip. Start with your constraints.')
        print('PASS: optional budget; clearing survives restart')
        stop()
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_text('{"schema": 999}')
        start()
        status('Cannot read draft. Clear to start again.')
        button('Clear draft')
        assert not draft.exists()
        print('PASS: unsupported saved state is visible and recoverable')
        stop()
        draft.write_text('{broken json')
        start()
        status('Cannot read draft. Clear to start again.')
        button('Clear draft')
        assert not draft.exists()
        print('PASS: malformed storage is visible and recoverable')
    finally:
        stop()
    (work / 'combined.log').write_text('\n'.join(logs))
    problems = re.findall(ERROR_PATTERN, '\n'.join(logs), re.M)
    assert not problems, problems
    print(f'PASS: no unexpected script/runtime errors; native evidence: {work}')


if __name__ == '__main__':
    main()
