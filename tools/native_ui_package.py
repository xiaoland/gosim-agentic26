#!/usr/bin/env python3
"""Materialize the versioned native UI prelude and skill into an independent app."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'packages/native-ui'
DISTRIBUTION = ('package.json', 'material.splash', 'skills/material-ui/SKILL.md', 'skills/material-ui/manifest.json', 'skills/material-ui/references/splash-entry.md', 'LICENSE')


def package_identity(package=PACKAGE):
    metadata = json.loads((package / 'package.json').read_text())
    digest = hashlib.sha256()
    for relative in DISTRIBUTION:
        digest.update(relative.encode() + b'\0')
        digest.update((package / relative).read_bytes() + b'\0')
    return {'name': metadata['name'], 'version': metadata['version'],
            'sha256': digest.hexdigest(), 'prelude_sha256': hashlib.sha256(
                (package / metadata['prelude']).read_bytes()).hexdigest()}


def compose_source(application_source, package=PACKAGE):
    identity = package_identity(package)
    prelude = (package / 'material.splash').read_text()
    return (f"// BEGIN {identity['name']} {identity['version']} sha256:{identity['sha256']}\n"
            + prelude.rstrip() + '\n// END agentic-native-ui\n\n'
            + application_source)


def script_prelude_function(package=PACKAGE):
    """A materialized string function for apps hosting a separate Splash isolate."""
    identity = package_identity(package)
    literal = json.dumps((package / 'material.splash').read_text(), ensure_ascii=False)
    return (f"// BEGIN {identity['name']} {identity['version']} sha256:{identity['sha256']}\n"
            + 'fn native_ui_style_source(){return ' + literal + '}\n'
            + '// END agentic-native-ui\n')


def materialize_navigation_skill(bundle, package=PACKAGE):
    """Navigation keeps its business skill; this directory is generated from the SDK."""
    destination = Path(bundle) / 'assets/skills/material-ui'
    materialize_skill(destination, package)
    return package_identity(package)


def materialize_skill(destination, package=PACKAGE):
    """Copy skill text and generate its reference from the one canonical prelude."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ('SKILL.md', 'manifest.json'):
        data = (package / 'skills/material-ui' / filename).read_bytes()
        target = destination / filename
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
    resources = json.loads((package / 'package.json').read_text())['skill_resources']
    for relative, source in resources.items():
        reference = destination / relative
        reference.parent.mkdir(parents=True, exist_ok=True)
        data = (package / source).read_bytes()
        if not reference.exists() or reference.read_bytes() != data:
            reference.write_bytes(data)


def build_bundle(application, destination, package=PACKAGE):
    application, destination, package = (Path(path).resolve() for path in
                                         (application, destination, package))
    if destination.is_relative_to(application) or destination.is_relative_to(package):
        raise ValueError('生成目录不能覆盖应用或SDK源目录。')
    source = (application / 'app.splash').read_text()
    manifest = json.loads((application / 'manifest.json').read_text())
    declaration = manifest.get('agent', {})
    if 'material-ui' not in declaration.get('skills', []):
        raise ValueError('示例manifest必须声明agent.skills中的material-ui。')
    if declaration.get('instructions') != 'AGENT.md':
        raise ValueError('本示例构建入口只接受AGENT.md指令路径。')
    identity = package_identity(package)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'main.splash').write_text(compose_source(source, package))
    shutil.copyfile(application / 'manifest.json', destination / 'manifest.json')
    shutil.copyfile(application / declaration['instructions'], destination / declaration['instructions'])
    materialize_skill(destination / 'skills/material-ui', package)
    # Metadata is beside the bundle, not an undeclared application asset.
    receipt = {'package': identity, 'application_id': manifest['id'],
               'main_sha256': hashlib.sha256((destination / 'main.splash').read_bytes()).hexdigest()}
    (destination.parent / 'native-ui-package.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('application', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(build_bundle(args.application, args.destination), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
