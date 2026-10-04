#!/usr/bin/env python3
"""Build and run the pinned stock desktop host with project-private state."""
import argparse
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN = Path(os.environ.get('AGENTIC26_AGENT_TOOLCHAIN', ROOT.parent / '.octosense-agentic26-host-bridge')).expanduser().resolve()
SOURCE = TOOLCHAIN / 'OctoSense'
BINARY = TOOLCHAIN / 'target/debug/octosense'
BUILD = ROOT / 'build/agent'
STATE = ROOT / '.local-state/agent'
HOME_DIR = STATE / 'home'
CORE = STATE / 'octos'
SESSION = STATE / 'session.json'
SELECTION = BUILD / 'system-apps.json'
STAGE = BUILD / 'system-apps/navigation/bundle'
LOCK = json.loads((ROOT / 'toolchain/agent-runtime.lock.json').read_text())
SYSTEM_APPS = ('navigation', 'maps', 'mail')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def command(*args, cwd=SOURCE, env=None):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, env=env, check=True)


def output(*args, cwd=SOURCE):
    return subprocess.check_output(list(map(str, args)), cwd=cwd, text=True).strip()


def private_dir(path):
    at = path
    while at != ROOT and ROOT in at.parents:
        require(not at.is_symlink(), '隔离数据目录不能是符号链接。')
        at = at.parent
    path.mkdir(parents=True, exist_ok=True)
    at = path
    while at == STATE or STATE in at.parents:
        at.chmod(0o700)
        at = at.parent


def write_private(path, data):
    private_dir(path.parent)
    require(not path.is_symlink(), '私有配置不能是符号链接。')
    temporary = path.with_name(path.name + '.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
    temporary.chmod(0o600)
    temporary.replace(path)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def minimax_base_url(value):
    message = 'MINIMAX_BASE_URL 必须是 https://api.minimax.cn/v1，仅允许默认或443端口，无账号、查询参数或片段。'
    try:
        url = urlsplit(value)
    except ValueError:
        raise RuntimeError(message) from None
    require(value == value.strip() and all(ord(c) >= 32 and ord(c) != 127 for c in value)
            and url.scheme == 'https' and url.netloc.lower() in ('api.minimax.cn', 'api.minimax.cn:443')
            and url.username is None and url.password is None and '?' not in value and '#' not in value
            and url.path in ('/v1', '/v1/'), message)
    return 'https://api.minimax.cn/v1'


def env_values(required=True):
    path = ROOT / '.env'
    if not required and not path.is_file():
        return {}
    require(path.is_file(), '缺少 .env；请配置 MINIMAX_API_KEY、MINIMAX_BASE_URL、MINIMAX_MODEL=MiniMax-M3、AMAP_API_KEY。')
    values = {}
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        require('=' in line, f'.env 第 {number} 行格式无效；内容省略。')
        name, value = line.split('=', 1)
        name = name.strip()
        require(re.fullmatch(r'[A-Z][A-Z0-9_]*', name) and name not in values,
                f'.env 第 {number} 行变量名无效或重复；内容省略。')
        try:
            parts = shlex.split(value, comments=True)
        except ValueError:
            raise RuntimeError(f'.env 第 {number} 行引号无效；内容省略。') from None
        require(len(parts) <= 1, f'.env 第 {number} 行需使用单个值；内容省略。')
        values[name] = parts[0] if parts else ''
    if required:
        for name in ('MINIMAX_API_KEY', 'MINIMAX_BASE_URL', 'MINIMAX_MODEL', 'AMAP_API_KEY'):
            require(bool(values.get(name)), f'.env 缺少 {name}。')
        require(values['MINIMAX_MODEL'] == LOCK['model'], '模型必须是 MiniMax-M3；拒绝其它模型或静默回退。')
        values['MINIMAX_BASE_URL'] = minimax_base_url(values['MINIMAX_BASE_URL'])
    return values


def secrets(values):
    return [values[name].encode() for name in ('MINIMAX_API_KEY', 'AMAP_API_KEY') if values.get(name)]


def no_secrets(data, values, label):
    require(not any(secret in data for secret in secrets(values)), f'{label} 检测到凭据；拒绝输出或打包，具体值省略。')


def host_env(hidden=False):
    env = dict(os.environ)
    for name in ('MAKEPAD_HOME', 'MAKEPAD_WM_ROOT', 'MAKEPAD_WM_THEME', 'MAKEPAD_REMOTE', 'MAKEPAD_HIDE_WINDOWS',
                 'OCTOS_APP_CORE_BIN', 'OCTOSENSE_HUB', 'OCTOSENSE_HUB_ANCHOR', 'MINIMAX_API_KEY', 'AMAP_API_KEY',
                 'FAKE_GPS_FILE', 'FAKE_GPS_MS'):
        env.pop(name, None)
    env.update(OCTOSENSE_HOME=str(HOME_DIR), OCTOSENSE_APP_DATA=str(HOME_DIR / 'apps'),
               OCTOS_APP_CORE_DIR=str(CORE), OCTOSENSE_LLM_VAULT='file', OCTOSENSE_MAIL_VAULT='file',
               OCTOSENSE_SECRETS='file', OCTOSENSE_SYSTEM_APPS=str(SELECTION),
               MAKEPAD_BUNDLE_NAME='OctoSense', MAKEPAD_BUNDLE_IDENTIFIER='dev.makepad.octosense')
    if hidden:
        env['MAKEPAD_HIDE_WINDOWS'] = '1'
    return env


def verify_overlay(source, spec):
    require(output('git', 'rev-parse', 'HEAD', cwd=source) == spec['revision'], '宿主覆盖补丁的上游版本不符。')
    patch = (ROOT / spec['patch']).resolve()
    require(patch.is_relative_to(ROOT / 'toolchain/patches')
            and hashlib.sha256(patch.read_bytes()).hexdigest() == spec['patch_sha256'], '宿主覆盖补丁摘要不符。')
    require(not output('git', 'diff', '--name-only', cwd=source)
            and not output('git', 'ls-files', '--others', '--exclude-standard', cwd=source),
            '宿主工具链有未审核改动，拒绝构建。')
    require(output('git', 'write-tree', cwd=source) == spec['tree'], '宿主工具链源码树与固定补丁不符。')


def apply_overlay(source, spec):
    require(output('git', 'rev-parse', 'HEAD', cwd=source) == spec['revision'], '宿主覆盖补丁的上游版本不符。')
    patch = (ROOT / spec['patch']).resolve()
    require(hashlib.sha256(patch.read_bytes()).hexdigest() == spec['patch_sha256'], '宿主覆盖补丁摘要不符。')
    tree = output('git', 'write-tree', cwd=source)
    if tree != spec['tree']:
        require(tree == spec.get('base_tree', output('git', 'rev-parse', 'HEAD^{tree}', cwd=source))
                and not output('git', 'diff', '--name-only', cwd=source)
                and not output('git', 'ls-files', '--others', '--exclude-standard', cwd=source), '保留未知工具链修改；请选择新的 AGENTIC26_AGENT_TOOLCHAIN。')
        command('git', 'apply', '--check', patch, cwd=source)
        command('git', 'apply', '--index', patch, cwd=source)
    verify_overlay(source, spec)


def verify_source():
    require(SOURCE.is_dir(), '请先运行 make agent-bootstrap。')
    spec = LOCK['octosense']
    require(output('git', 'rev-parse', 'HEAD') == spec['revision'], '隔离 OctoSense 版本与 agent-runtime.lock.json 不符。')
    overlays = LOCK['location_overlays']
    require(overlays['octosense']['revision'] == spec['revision']
            and overlays['app_hub']['revision'] == LOCK['app_hub_revision'], '宿主覆盖补丁与固定上游版本不符。')
    maps = LOCK['maps_overlays']
    for name, source in [('octosense', SOURCE), ('app_hub', SOURCE / '.sources/app-hub')]:
        require(maps[name]['base_tree'] == overlays[name]['tree'], 'Maps 覆盖补丁的定位基线不符。')
        require(hashlib.sha256((ROOT / overlays[name]['patch']).read_bytes()).hexdigest() == overlays[name]['patch_sha256'], '定位基线补丁摘要不符。')
        overlay = LOCK.get('font_document_overlay', maps[name]) if name == 'app_hub' else maps[name]
        if name == 'app_hub' and 'font_document_overlay' in LOCK:
            require(overlay['base_tree'] == maps[name]['tree'], '字体文档覆盖补丁的 Maps 基线不符。')
            require(hashlib.sha256((ROOT / maps[name]['patch']).read_bytes()).hexdigest() == maps[name]['patch_sha256'], 'Maps 基线补丁摘要不符。')
        verify_overlay(source, overlay)
    for name, expected in [('Cargo.lock', maps['octosense']['cargo_lock_sha256']),
                           ('runtime-patches.lock.json', spec['runtime_patches_lock_sha256'])]:
        require(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == expected, f'官方 {name} 摘要不符。')
    checked = subprocess.run([sys.executable, str(SOURCE / 'tools/setup.py'), '--check'], cwd=SOURCE,
                             capture_output=True, text=True)
    require(checked.returncode == 0, '官方 setup --check 未通过；请运行 agent-bootstrap 查看源码问题。')
    runtime = json.loads(checked.stdout)
    require(runtime['runtime']['revision'] == LOCK['runtime']['octoscript_makepad']
            and runtime['repositories']['makepad']['revision'] == LOCK['runtime']['makepad_base']
            and runtime['repositories']['octoscript']['revision'] == LOCK['runtime']['octoscript']
            and runtime['patches']['makepad']['tree'] == LOCK['runtime']['makepad_patched_tree'],
            '官方运行时依赖与 agent-runtime.lock.json 不符。')


def bundle_files(values, root=None):
    root = ROOT / 'bundle' if root is None else root
    require(root.is_dir() and not root.is_symlink(), '应用 bundle 目录缺失或是符号链接。')
    files = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'bundle 中不能包含符号链接。')
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        require(path.name != 'private-config.json' and not path.name.startswith('.env')
                and path.suffix not in ('.key', '.cert') and '.local-state' not in path.parts,
                'bundle 包含私有配置文件，拒绝打包。')
        data = path.read_bytes()
        no_secrets(data, values, 'bundle')
        files[rel] = data
    require('manifest.json' in files and 'main.splash' in files, 'bundle 缺少 manifest.json 或 main.splash。')
    return files


def source_digest(files):
    digest = hashlib.sha256()
    for name, data in files.items():
        digest.update(name.encode() + b'\0' + str(len(data)).encode() + b'\0' + data)
    return digest.hexdigest()


def official_bundles(values):
    bundles = {}
    for name in SYSTEM_APPS[1:]:
        files = bundle_files(values, SOURCE / 'apps' / name / 'bundle')
        require(set(files) == {'manifest.json', 'main.splash'}
                and json.loads(files['manifest.json'])['id'] == 'os.' + name,
                f'固定官方 {name} bundle 的文件集合或 id 不符。')
        bundles[name] = files
    return bundles


def selection_bytes():
    return json_bytes({'schema': 1, 'source': 'system-apps', 'apps': list(SYSTEM_APPS), 'assets': {}})


def write_staged_bundle(root, files):
    root.mkdir(parents=True, exist_ok=True)
    require(not root.is_symlink(), '暂存 bundle 不能是符号链接。')
    for path in root.rglob('*'):
        require(not path.is_symlink(), '暂存 bundle 中不能包含符号链接。')
        if path.is_file() and path.relative_to(root).as_posix() not in files:
            path.unlink()
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != data:
            path.write_bytes(data)


def stage(values):
    files = bundle_files(values)
    digest = source_digest(files)
    manifest = json.loads(files['manifest.json'])
    app_id = manifest['id']
    require(re.fullmatch(r'[a-z0-9][a-z0-9.-]*', app_id), '应用 id 格式无效。')
    # The stock shell only lists embedded system apps whose ids start with os.
    runtime_id = app_id if app_id.startswith('os.') else 'os.' + app_id
    manifest['id'] = runtime_id
    manifest['integrity']['bundle_blake3'] = ''
    files['manifest.json'] = json_bytes(manifest)
    metadata = {'source_sha256': digest, 'source_id': app_id, 'runtime_id': runtime_id}
    write_staged_bundle(STAGE, files)
    metadata['system_apps'] = {'navigation': dict(metadata)}
    for name, official_files in official_bundles(values).items():
        write_staged_bundle(STAGE.parents[1] / name / 'bundle', official_files)
        metadata['system_apps'][name] = {'source_sha256': source_digest(official_files),
                                       'source_id': 'os.' + name, 'runtime_id': 'os.' + name}
    selection = selection_bytes()
    if not SELECTION.is_file() or SELECTION.read_bytes() != selection:
        SELECTION.write_bytes(selection)
    return metadata, files


def verify_pack(path, files, runtime_id, values):
    require(path.is_file(), f'未找到官方生成的 {path.name}。')
    pack = json.loads(path.read_bytes())
    require(pack['schema'] == 1 and set(pack['files']) == set(files),
            '官方 system-app 包的 schema 或文件集合与当前源码不符。')
    decoded = {name: base64.b64decode(data, validate=True) for name, data in pack['files'].items()}
    for name, data in decoded.items():
        no_secrets(data, values, '官方 system-app 包')
        if name != 'manifest.json':
            require(data == files[name], '官方 system-app 包含旧源码；拒绝启动。')
    packed_manifest = json.loads(decoded['manifest.json'])
    require(packed_manifest['id'] == runtime_id, '官方 system-app id 不符。')
    bundle_digest = packed_manifest['integrity']['bundle_blake3']
    require(isinstance(bundle_digest, str) and re.fullmatch(r'[0-9a-f]{64}', bundle_digest),
            '官方 system-app 缺少有效的 bundle 摘要。')
    expected_manifest = json.loads(files['manifest.json'])
    expected_manifest['integrity']['bundle_blake3'] = bundle_digest
    require(packed_manifest == expected_manifest, '官方 system-app 清单与当前源码不符。')
    return bundle_digest


def build(values):
    verify_source()
    metadata, files = stage(values)
    bundles = {'navigation': files, **official_bundles(values)}
    spec = LOCK['build']
    args = ['cargo', 'build', '--locked', '-p', spec['package'], '--bin', spec['binary'],
            '--no-default-features', '--features', ','.join(spec['features']),
            '--target-dir', str(TOOLCHAIN / 'target'), '--message-format=json']
    print('+', ' '.join(args), flush=True)
    result = subprocess.run(args, cwd=SOURCE, env=host_env(), stdout=subprocess.PIPE, text=True)
    out_dirs = set()
    for line in result.stdout.splitlines():
        event = json.loads(line)
        if event.get('reason') == 'compiler-message':
            print(event['message'].get('rendered') or event['message']['message'], end='', flush=True)
        if event.get('reason') == 'build-script-executed' and re.search(
                r'(?:^|[#/])octosense-app-hub-app(?:[@ ]|$)', event.get('package_id', '')):
            out_dirs.add(Path(event['out_dir']))
    require(result.returncode == 0, '官方宿主构建失败。')
    require(len(out_dirs) == 1, '本次构建未唯一报告官方 system-app 输出目录；拒绝使用旧包。')
    out_dir = out_dirs.pop()
    require(source_digest(bundle_files(values)) == metadata['source_sha256'], '构建期间 bundle 已改变；请重新运行命令。')
    current_official = official_bundles(values)
    require(SELECTION.read_bytes() == selection_bytes(), '构建期间 system-app 选择已改变。')
    for name, staged_files in bundles.items():
        app = metadata['system_apps'][name]
        if name != 'navigation':
            require(source_digest(current_official[name]) == app['source_sha256']
                    and current_official[name] == staged_files, '构建期间官方 bundle 已改变。')
        require(bundle_files(values, STAGE.parents[1] / name / 'bundle') == staged_files,
                '构建期间暂存 bundle 已改变。')
        app['bundle_blake3'] = verify_pack(out_dir / f'system-{name}.pack.json', staged_files, app['runtime_id'], values)
    metadata['bundle_blake3'] = metadata['system_apps']['navigation']['bundle_blake3']
    metadata['host_revision'] = LOCK['octosense']['revision']
    metadata['host_overlay_tree'] = LOCK['maps_overlays']['octosense']['tree']
    metadata['hub_overlay_tree'] = LOCK.get('font_document_overlay', LOCK['maps_overlays']['app_hub'])['tree']
    metadata['host_binary_sha256'] = hashlib.sha256(BINARY.read_bytes()).hexdigest()
    (BUILD / 'build.json').write_bytes(json_bytes(metadata))
    print('当前源码 SHA-256:', metadata['source_sha256'], flush=True)
    return metadata


def bootstrap():
    for name in ('git', 'cargo'):
        require(bool(shutil.which(name)), f'缺少 {name}。')
    TOOLCHAIN.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        command('git', 'init', SOURCE, cwd=TOOLCHAIN)
        command('git', 'remote', 'add', 'origin', LOCK['octosense']['url'])
        command('git', 'fetch', '--depth', '1', 'origin', LOCK['octosense']['revision'])
        command('git', 'checkout', '--detach', 'FETCH_HEAD')
    require(output('git', 'rev-parse', 'HEAD') == LOCK['octosense']['revision'], '隔离源码版本不符；请选择新的 AGENTIC26_AGENT_TOOLCHAIN。')
    hub = SOURCE / '.sources/app-hub'
    if not hub.exists():
        spec = LOCK['location_overlays']['app_hub']
        command('git', 'init', hub, cwd=TOOLCHAIN)
        command('git', 'remote', 'add', 'origin', spec['url'], cwd=hub)
        command('git', 'fetch', '--depth', '1', 'origin', spec['revision'], cwd=hub)
        command('git', 'checkout', '--detach', 'FETCH_HEAD', cwd=hub)
    for name, source in [('app_hub', hub), ('octosense', SOURCE)]:
        maps = LOCK['maps_overlays'][name]
        final = LOCK.get('font_document_overlay', maps) if name == 'app_hub' else maps
        tree = output('git', 'write-tree', cwd=source)
        if tree != final['tree']:
            if tree != maps['tree']:
                apply_overlay(source, LOCK['location_overlays'][name])
            apply_overlay(source, maps)
        apply_overlay(source, final)
    command(sys.executable, SOURCE / 'tools/setup.py', '--no-hub', '--cache', ROOT.parent / '.octosense-agentic26')
    build(env_values(required=False))


def jail_path():
    manifest = json.loads((ROOT / 'bundle/manifest.json').read_text())
    app_id = manifest['id']
    require(re.fullmatch(r'[a-z0-9][a-z0-9.-]*', app_id), '应用 id 格式无效。')
    return HOME_DIR / 'apps' / (app_id if app_id.startswith('os.') else 'os.' + app_id)


def configure(values, jail, location_mode="live"):
    now = datetime.now(timezone.utc).isoformat()
    profile = {'id': '_main', 'name': 'Navigation MiniMax-M3', 'enabled': True, 'created_at': now, 'updated_at': now,
               'config': {'llm': {'primary': {'family_id': 'minimax-cn', 'model_id': LOCK['model'],
                          'route': {'base_url': values['MINIMAX_BASE_URL'], 'api_key_env': 'MINIMAX_API_KEY', 'api_type': 'openai'}},
                          'fallbacks': []}, 'env_vars': {'MINIMAX_API_KEY': values['MINIMAX_API_KEY']}}}
    write_private(CORE / 'profiles/_main.json', json_bytes(profile))
    write_private(jail / 'private-config.json', json_bytes({
        'amap_api_key': values['AMAP_API_KEY'], 'minimax_api_key': values['MINIMAX_API_KEY'],
        'minimax_base_url': values['MINIMAX_BASE_URL'], 'minimax_model': LOCK['model'],
        'location_mode': location_mode
    }))


def init_demo():
    stop()
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)
    values = {'SOURCE_TIME': now.isoformat(), 'SOURCE_EPOCH': str(int(now.timestamp())),
              'ICS_DATE': now.strftime('%Y%m%d'), 'ICS_STAMP_UTC': now.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
    for name, hours in [('FLIGHT', 2), ('DINNER', 1)]:
        at = now + timedelta(hours=hours)
        values[name + '_START_LOCAL'] = at.strftime('%Y%m%dT%H%M%S')
        values[name + '_START_EPOCH'] = str(int(at.timestamp()))
    jail = jail_path()
    for rel in ('calendar.ics', 'notes/ticket.md', 'location.json'):
        content = (ROOT / 'demo' / rel).read_text()
        for name, value in values.items():
            content = content.replace('{{' + name + '}}', value)
        require('{{' not in content, 'demo 模板有未识别的时间占位符。')
        write_private(jail / 'demo' / rel, content.encode())
    print('已明确重置三份模拟来源；日常启动不会覆盖这些文件。')


def process_stamp(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'lstart=', '-o', 'comm='], capture_output=True, text=True)
    return result.stdout.strip()


def remote(session, route, timeout=15):
    with urlopen(f'http://127.0.0.1:{session["port"]}/{route}', timeout=timeout) as response:
        return response.read()


def current_session():
    require(SESSION.is_file(), '没有本启动器管理的运行实例。')
    session = json.loads(SESSION.read_bytes())
    require(process_stamp(session['pid']) == session['process_stamp'], '记录的 PID 已退出或被复用。')
    status = json.loads(remote(session, 's'))
    require(status['pid'] == session['pid'], '远程端口的 PID 不属于本次实例。')
    return session


def mounted_bundle(metadata):
    root = HOME_DIR / 'apps/.system' / metadata['runtime_id']
    until = time.monotonic() + 15
    while time.monotonic() < until:
        if root.is_dir():
            for manifest_path in root.glob('*/manifest.json'):
                manifest = json.loads(manifest_path.read_bytes())
                if manifest['integrity']['bundle_blake3'] == metadata['bundle_blake3']:
                    path = manifest_path.parent
                    require((path / 'main.splash').read_bytes() == (STAGE / 'main.splash').read_bytes(),
                            '实际加载的 main.splash 与刚构建的源码不符。')
                    return path
        time.sleep(0.1)
    raise RuntimeError('目标应用未加载当前官方包；请检查私有宿主日志。')


def stop():
    if not SESSION.is_file():
        return
    session = json.loads(SESSION.read_bytes())
    if process_stamp(session['pid']) != session['process_stamp']:
        SESSION.unlink()
        return
    try:
        current_session()
        remote(session, 'quit', timeout=10)
    except (OSError, RuntimeError, ValueError):
        # The exact PID and process start/command stamp still identify our child.
        if process_stamp(session['pid']) == session['process_stamp']:
            os.kill(session['pid'], signal.SIGTERM)
    until = time.monotonic() + 10
    while time.monotonic() < until and process_stamp(session['pid']) == session['process_stamp']:
        time.sleep(0.1)
    require(process_stamp(session['pid']) != session['process_stamp'], '自己的宿主尚未退出；保留会话记录。')
    SESSION.unlink()
    print('已关闭本启动器的宿主实例。')


def packaged_host():
    # 本机实测裸二进制未完成授权；包内运行成功触发授权并取得定位样本。
    contents = STATE / 'app/OctoSense Navigation.app/Contents'
    private_dir(contents / 'MacOS')
    info = plistlib.loads((BINARY.parent / 'Info.plist').read_bytes())
    require(info.get('NSLocationWhenInUseUsageDescription'), '官方宿主缺少定位用途说明。')
    # Makepad writes this sidecar into a shared target profile. Another package's
    # build script can overwrite it without invalidating our cached executable.
    # The wrapper owns its bundle identity; match the pinned OctoSense config.
    info.update(CFBundleIdentifier='dev.makepad.octosense', CFBundleName='OctoSense',
                CFBundleDisplayName='OctoSense', CFBundleExecutable=BINARY.name, CFBundlePackageType='APPL')
    executable = contents / 'MacOS' / BINARY.name
    require(not executable.is_symlink(), '私有宿主可执行文件不能是符号链接。')
    # 使用独立文件，后续 cargo 构建不会覆盖正在运行的宿主。
    shutil.copyfile(BINARY, executable)
    executable.chmod(0o700)
    write_private(contents / 'Info.plist', plistlib.dumps(info))
    return executable


def start(hidden, demo=False):
    values = env_values()
    jail = jail_path()
    sources = ('calendar.ics', 'notes/ticket.md', 'location.json') if demo else ('calendar.ics', 'notes/ticket.md')
    require(all((jail / 'demo' / rel).is_file() for rel in sources),
            '模拟来源尚未初始化；先运行 make agent-init-demo。')
    metadata = build(values)
    stop()
    executable = packaged_host()
    configure(values, jail, "demo" if demo else "live")
    private_dir(STATE / 'logs')
    log = STATE / 'logs' / (datetime.now().strftime('%Y%m%d-%H%M%S') + '.log')
    with log.open('wb') as stream:
        proc = subprocess.Popen([str(executable), '--remote', '--test-action', 'launch-' + metadata['runtime_id'].removeprefix('os.')],
                                cwd=STATE, env=host_env(hidden), stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    log.chmod(0o600)
    try:
        until = time.monotonic() + 60
        while time.monotonic() < until:
            data = log.read_bytes()
            no_secrets(data, values, '宿主启动日志')
            match = re.search(rb'\[makepad-remote\] listening on 127\.0\.0\.1:(\d+) pid=(\d+)', data)
            if match:
                require(int(match[2]) == proc.pid, '远程接口 PID 与子进程不符。')
                session = {'pid': proc.pid, 'port': int(match[1]), 'process_stamp': process_stamp(proc.pid),
                           'hidden': hidden, 'log': str(log), 'jail': str(jail), **metadata}
                write_private(SESSION, json_bytes(session))
                current_session()
                session['mounted_bundle'] = str(mounted_bundle(metadata))
                write_private(SESSION, json_bytes(session))
                print(json.dumps(session, ensure_ascii=False, indent=2))
                return
            require(proc.poll() is None, '宿主启动失败；查看私有日志，凭据值不会输出。')
            time.sleep(0.2)
        raise RuntimeError('宿主启动超时。')
    except Exception:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=10)
        if SESSION.is_file():
            SESSION.unlink()
        raise


def doctor():
    verify_source()
    values = env_values()
    bundle_files(values)
    for name, files in official_bundles(values).items():
        require(bundle_files(values, STAGE.parents[1] / name / 'bundle') == files,
                f'暂存 {name} 与固定官方 bundle 不符；请重新构建。')
    require(SELECTION.is_file() and SELECTION.read_bytes() == selection_bytes(),
            '开发宿主必须选择 Navigation、Maps、Mail；请重新构建。')
    require(BINARY.is_file(), '缺少官方宿主二进制；运行 make agent-bootstrap。')
    require((BUILD / 'build.json').is_file(), '缺少当前构建记录；运行 make agent-build。')
    metadata = json.loads((BUILD / 'build.json').read_bytes())
    require(metadata['source_sha256'] == source_digest(bundle_files(values))
            and metadata['host_overlay_tree'] == LOCK['maps_overlays']['octosense']['tree']
            and metadata['hub_overlay_tree'] == LOCK.get('font_document_overlay', LOCK['maps_overlays']['app_hub'])['tree']
            and metadata['host_binary_sha256'] == hashlib.sha256(BINARY.read_bytes()).hexdigest(),
            '构建记录、应用源码或宿主二进制已改变；运行 make agent-build。')
    print('固定官方源码、定位与 Maps 窄选点覆盖补丁、字体文档 gate 覆盖、运行时补丁、MiniMax-M3 单 provider/无 fallback 配置及 Navigation／固定官方 Maps、Mail 包和选择、凭据边界通过；未调用外部服务。')


def check():
    verify_source()
    values = env_values(required=False)
    bundle_files(values)
    command('cargo', 'build', '--locked', '-p', 'octosense-app-hub', '--bin', 'hub',
            '--target-dir', TOOLCHAIN / 'target', env=host_env())
    harness_root = Path(os.environ.get('AGENTIC26_TOOLCHAIN', ROOT.parent / '.octosense-agentic26')).expanduser().resolve()
    harness = harness_root / 'OctoScript-App-Design-Flow/tools/octo'
    require(harness.is_file(), '缺少固定官方检查 harness；先运行 make bootstrap。')
    harness_lock = json.loads((ROOT / 'toolchain/sources.lock.json').read_bytes())['repositories']['OctoScript-App-Design-Flow']
    require(output('git', 'rev-parse', 'HEAD', cwd=harness.parent.parent) == harness_lock['revision']
            and not output('git', 'diff', 'HEAD', '--', 'tools/octo', cwd=harness.parent.parent),
            '官方检查 harness 与固定版本不符。')
    env = host_env()
    env.update(OCTOSENSE_APP_HUB=str(SOURCE / '.sources/app-hub'), OCTO_HUB=str(TOOLCHAIN / 'target/debug/hub'))
    command(sys.executable, harness, 'check', ROOT / 'bundle', cwd=ROOT, env=env)
    no_secrets((ROOT / 'bundle/manifest.json').read_bytes(), values, '盖摘要后的清单')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('bootstrap', 'doctor', 'check', 'build', 'init-demo', 'dev', 'hidden', 'stop', 'status', 'tree', 'logs', 'shot'))
    parser.add_argument('--demo', action='store_true', help='明确使用模拟定位；默认请求系统实时定位。')
    parser.add_argument('--output', type=Path, default=BUILD / 'screenshot.png')
    args = parser.parse_args()
    if args.action == 'bootstrap':
        bootstrap()
    elif args.action == 'doctor':
        doctor()
    elif args.action == 'check':
        check()
    elif args.action == 'build':
        build(env_values(required=False))
    elif args.action == 'init-demo':
        init_demo()
    elif args.action in ('dev', 'hidden'):
        start(args.action == 'hidden', demo=args.demo)
    elif args.action == 'stop':
        stop()
    else:
        session = current_session()
        if args.action == 'status':
            print(json.dumps(session, ensure_ascii=False, indent=2))
        elif args.action == 'shot':
            data = remote(session, 'g?raw=1', timeout=30)
            require(data.startswith(b'\x89PNG\r\n\x1a\n'), '官方远程截图未返回 PNG。')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(data)
            print(args.output.resolve())
        else:
            data = remote(session, 'd' if args.action == 'tree' else 'log?n=1000')
            no_secrets(data, env_values(), '远程调试输出')
            print(data.decode())


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('agent:', error, file=sys.stderr)
        sys.exit(1)
