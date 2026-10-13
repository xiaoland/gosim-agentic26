"""The source package is reproducible and independent consumers use identical bytes."""
import json
from pathlib import Path
import tempfile
import unittest

import native_ui_package as sdk


class NativeUiPackageTests(unittest.TestCase):
    def test_child_isolate_function_preserves_the_actual_prelude(self):
        function = sdk.script_prelude_function()
        literal = function.split('fn native_ui_style_source(){return ', 1)[1]
        source, _ = json.JSONDecoder().raw_decode(literal)
        self.assertEqual(source, (sdk.PACKAGE / 'material.splash').read_text())

    def test_two_independent_consumers_share_exact_prelude_and_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipts = []
            for index, source in enumerate(('MaterialTitle{text:"公开合成Notes"}',
                                             'MaterialCard{MaterialBody{text:"独立空状态"}}')):
                app = root / f'app-{index}'
                app.mkdir()
                (app / 'app.splash').write_text(source)
                (app / 'AGENT.md').write_text('synthetic only')
                (app / 'manifest.json').write_text(json.dumps({'id': f'fixture-{index}',
                    'agent': {'instructions': 'AGENT.md', 'skills': ['material-ui']}}))
                destination = root / f'output-{index}/bundle'
                receipt = sdk.build_bundle(app, destination)
                receipts.append(receipt)
                self.assertEqual((destination / 'main.splash').read_text(), sdk.compose_source(source))
                self.assertEqual((destination / 'skills/material-ui/SKILL.md').read_bytes(),
                                 (sdk.PACKAGE / 'skills/material-ui/SKILL.md').read_bytes())
                self.assertEqual((destination / 'skills/material-ui/references/primitives.splash').read_bytes(),
                                 (sdk.PACKAGE / 'material.splash').read_bytes())
                navigation = root / f'navigation-{index}'
                sdk.materialize_navigation_skill(navigation)
                self.assertEqual((navigation / 'assets/skills/material-ui/references/primitives.splash').read_bytes(),
                                 (destination / 'skills/material-ui/references/primitives.splash').read_bytes())
                self.assertEqual((destination / 'skills/material-ui/references/splash-entry.md').read_bytes(),
                                 (sdk.PACKAGE / 'skills/material-ui/references/splash-entry.md').read_bytes())
                self.assertEqual((navigation / 'assets/skills/material-ui/references/splash-entry.md').read_bytes(),
                                 (destination / 'skills/material-ui/references/splash-entry.md').read_bytes())
                with self.assertRaises(ValueError):
                    sdk.build_bundle(app, app / 'bundle')
            self.assertEqual(receipts[0]['package'], receipts[1]['package'])
            self.assertNotEqual(receipts[0]['main_sha256'], receipts[1]['main_sha256'])


if __name__ == '__main__':
    unittest.main()
