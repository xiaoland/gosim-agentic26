"""Development .app privacy declarations come from the pinned packaging template."""
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

import agent


class PackagingTests(unittest.TestCase):
    def test_profile_sidecar_cannot_drop_or_replace_calendar_declarations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / 'target/octosense'
            binary.parent.mkdir()
            binary.write_bytes(b'fixture executable')
            (binary.parent / 'Info.plist').write_bytes(plistlib.dumps({
                'CFBundleIdentifier': 'other-package',
                'NSLocationWhenInUseUsageDescription': 'sidecar text',
            }))
            source = root / 'source'
            template = source / 'desktop/packaging/macos/Info.plist'
            template.parent.mkdir(parents=True)
            privacy = {key: 'official ' + key for key in (
                'NSLocationUsageDescription', 'NSLocationWhenInUseUsageDescription',
                'NSCalendarsUsageDescription', 'NSCalendarsFullAccessUsageDescription')}
            template.write_bytes(plistlib.dumps(privacy))
            with patch.object(agent, 'BINARY', binary), patch.object(agent, 'SOURCE', source), \
                    patch.object(agent, 'STATE', root / 'state'):
                executable = agent.packaged_host()
                info = plistlib.loads((executable.parent.parent / 'Info.plist').read_bytes())
                self.assertEqual(executable.read_bytes(), binary.read_bytes())
                self.assertEqual(info['CFBundleIdentifier'], 'dev.makepad.octosense')
                for key, value in privacy.items():
                    self.assertEqual(info[key], value)
                template.write_bytes(plistlib.dumps({}))
                with self.assertRaisesRegex(RuntimeError, 'NSLocationUsageDescription'):
                    agent.packaged_host()


if __name__ == '__main__':
    unittest.main()
