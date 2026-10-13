#!/usr/bin/env python3
"""验证配套宿主包门的实际接受、工具声明与摘要拒绝边界。"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME = ROOT.parent / '.octosense-agentic26-host-bridge/target/debug/octosense'
DEFAULT_HUB = ROOT.parent / '.octosense-agentic26-host-bridge/target/debug/hub'
RUNTIME = DEFAULT_RUNTIME
HUB = DEFAULT_HUB


class ProjectGate(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='navigation-gate-')
        self.addCleanup(self.temporary.cleanup)
        self.bundle = Path(self.temporary.name) / 'bundle'
        shutil.copytree(ROOT / 'bundle', self.bundle)

    def check(self):
        return subprocess.run([str(RUNTIME), '--navigation-check', str(self.bundle), '--allow-unsigned'],
                              capture_output=True, text=True)

    def stamp(self):
        subprocess.run([str(HUB), 'stamp', str(self.bundle)], check=True, capture_output=True)

    def test_matching_host_accepts_current_bundle(self):
        self.stamp()
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASSED', result.stdout)

    def test_unoffered_tool_is_refused(self):
        path = self.bundle / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['agent']['tools'].append('notes.write')
        path.write_text(json.dumps(manifest))
        self.stamp()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('notes.write', result.stdout)
        self.assertIn('does not offer', result.stdout)

    def test_other_app_cannot_borrow_navigation_offer(self):
        path = self.bundle / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['id'] = 'unrelated-app'
        path.write_text(json.dumps(manifest))
        self.stamp()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('accepts only Navigation', result.stderr)

    def test_changed_source_without_stamp_is_refused(self):
        self.stamp()
        with (self.bundle / 'main.splash').open('a') as output:
            output.write('\n// package changed after stamping\n')
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('[refused] digest', result.stdout)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument('--hub', type=Path, default=DEFAULT_HUB)
    args = parser.parse_args()
    RUNTIME, HUB = args.runtime, args.hub
    unittest.main(argv=['project-gate'])
