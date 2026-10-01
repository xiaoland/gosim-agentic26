#!/usr/bin/env python3
"""Fetch the pinned OctoSense sources and build the local development tools."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get('AGENTIC26_TOOLCHAIN', ROOT.parent / '.octosense-agentic26')).expanduser().resolve()


def run(*args, cwd=None):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def output(*args, cwd=None):
    return subprocess.check_output(list(map(str, args)), cwd=cwd, text=True).strip()


def main():
    for exe in ('git', 'cargo'):
        if not shutil.which(exe):
            raise SystemExit(f'{exe} is required; install it before running bootstrap.')
    lock = json.loads((ROOT / 'toolchain/sources.lock.json').read_text())
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    for name, source in lock['repositories'].items():
        checkout = WORKSPACE / name
        if not checkout.exists():
            run('git', 'init', checkout)
            run('git', 'remote', 'add', 'origin', source['url'], cwd=checkout)
            run('git', 'fetch', '--depth', '1', 'origin', source['revision'], cwd=checkout)
            run('git', 'checkout', '--detach', 'FETCH_HEAD', cwd=checkout)
        actual = output('git', 'rev-parse', 'HEAD', cwd=checkout)
        if actual != source['revision']:
            raise SystemExit(f'{checkout}: expected {source["revision"]}, got {actual}. Use a new AGENTIC26_TOOLCHAIN directory or resolve deliberately.')
        dirty = output('git', 'status', '--porcelain', '--untracked-files=no', cwd=checkout).splitlines()
        allowed = ['M Cargo.lock'] if name == 'OctoSense-App-Hub' else []
        if any(line.strip() not in allowed for line in dirty):
            raise SystemExit(f'{checkout}: modified sources; refusing to build an unrecorded revision.')
    harness = WORKSPACE / 'OctoScript-App-Design-Flow'
    run(sys.executable, harness / 'tools/setup-native.py', '--root', WORKSPACE, '--cache', WORKSPACE)
    run(sys.executable, harness / 'tools/setup-native.py', '--root', WORKSPACE, '--check')
    hub = WORKSPACE / 'OctoSense-App-Hub'
    pinned = (ROOT / 'toolchain/hub.Cargo.lock').read_bytes()
    current = (hub / 'Cargo.lock').read_bytes()
    upstream = subprocess.check_output(['git', 'show', 'HEAD:Cargo.lock'], cwd=hub)
    if current not in (upstream, pinned):
        raise SystemExit(f'{hub}/Cargo.lock has unrecognized edits; refusing to overwrite.')
    (hub / 'Cargo.lock').write_bytes(pinned)
    run('cargo', 'build', '--locked', '--release', '--target-dir', hub / 'target', '-p', 'octosense-card-host', '-p', 'octosense-app-hub', cwd=hub)
    run(sys.executable, ROOT / 'tools/octo', 'doctor')


if __name__ == '__main__':
    main()
