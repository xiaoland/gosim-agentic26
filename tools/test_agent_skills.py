"""Catalog and recursive resource-copy regression, without touching live app state."""
import json
from pathlib import Path
import tempfile
import unittest
import agent

class SkillTests(unittest.TestCase):
    def test_catalog_tracks_metadata_and_nested_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / 'bundle'
            skill = bundle / 'assets/skills/example'
            (skill / 'references').mkdir(parents=True)
            entry = skill / 'SKILL.md'
            entry.write_text('---\nname: example\ndescription: "首次描述"\n---\n正文不进入metadata。')
            reference = skill / 'references/layout.md'
            reference.write_text('完整引用材料')
            agent.materialize_skills(bundle, root / 'jail')
            catalog = json.loads((root / 'jail/skills/catalog.json').read_text())
            self.assertEqual(catalog, [{'name': 'example', 'description': '首次描述',
                                       'files': ['SKILL.md', 'references/layout.md']}])
            self.assertEqual((root / 'jail/skills/example/references/layout.md').read_bytes(), reference.read_bytes())
            entry.write_text(entry.read_text().replace('首次描述', '更新描述'))
            agent.refresh_skill_catalog(bundle)
            self.assertEqual(json.loads((bundle / 'assets/skills/catalog.json').read_text())[0]['description'], '更新描述')

if __name__ == '__main__':
    unittest.main()
