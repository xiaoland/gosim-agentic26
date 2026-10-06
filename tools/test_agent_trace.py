"""Focused regressions for private development trace reading and stopped archival."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import agent

class TraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.directory = self.root / 'logs'
        self.directory.mkdir()
        self.status = {'last_seq': 2, 'state': 'recording', 'format': 'jsonl-segments', 'segments': 1}
    def tearDown(self):
        self.temp.cleanup()
    def event(self, seq):
        return {'session': 'session', 'instance': 'vm-1', 'seq': seq, 'data': '{"text":"完整\\n记录"}'}
    def line(self, seq):
        return (json.dumps(self.event(seq), ensure_ascii=False)+'\n').encode()
    def read(self):
        return agent.trace_events(self.directory, self.status, 'session', 'vm-1', {}, {})
    def test_more_than_256_events_in_one_segment(self):
        self.status['last_seq'] = 300
        (self.directory/'segment-000001.jsonl').write_bytes(b''.join(self.line(i) for i in range(1,301)))
        self.assertEqual(len(self.read()), 300)
        self.assertEqual(self.status['state'], 'recording')
    def test_legacy_preserved(self):
        self.status.pop('format')
        for i in (1,2): (self.directory/f'7-{i}.json').write_bytes(self.line(i))
        self.assertEqual([e['seq'] for e in self.read()], [1,2])
    def test_truncated_final_record(self):
        (self.directory/'segment-000001.jsonl').write_bytes(self.line(1)+self.line(2)[:-1])
        self.assertEqual(len(self.read()), 1)
        self.assertEqual(self.status['state'], 'incomplete')
    def test_gap_duplicate_and_uncommitted(self):
        for sequences in ((1,), (1,1), (1,2,3)):
            self.status.update(state='recording')
            (self.directory/'segment-000001.jsonl').write_bytes(b''.join(self.line(i) for i in sequences))
            self.read()
            self.assertEqual(self.status['state'], 'incomplete')
    def test_missing_segment_directory_and_bad_json(self):
        path=self.directory/'segment-000001.jsonl'
        path.mkdir();self.read();self.assertEqual(self.status['state'],'incomplete')
        path.rmdir();path.write_bytes(b'broken\n');self.read();self.assertEqual(self.status['state'],'incomplete')
    def test_secret_rejected_including_partial_line(self):
        (self.directory/'segment-000001.jsonl').write_bytes(b'sensitive%2Fkey')
        with self.assertRaises(RuntimeError):
            agent.trace_events(self.directory,self.status,'session','vm-1',{'DIDI_MCP_KEY':'sensitive/key'}, {})
    def test_incomplete_latched(self):
        self.status['state']='incomplete'
        (self.directory/'segment-000001.jsonl').write_bytes(self.line(1)+self.line(2))
        self.read();self.assertEqual(self.status['state'],'incomplete')
    def test_archive_preserves_bytes_business_and_permissions(self):
        jail=self.root/'jail';trace=jail/'dev-trace'/'old';trace.mkdir(parents=True)
        original=b'private raw evidence\x00'
        (trace/'event.json').write_bytes(original);(jail/'business.txt').write_text('untouched')
        with patch.object(agent,'ROOT',self.root),patch.object(agent,'STATE',self.root/'state'),patch.object(agent,'SESSION',self.root/'session.json'),patch.object(agent.subprocess,'check_output',return_value=''):
            archive=agent.archive_stopped_traces(jail)
        copied=archive/'dev-trace/old/event.json'
        self.assertEqual(copied.read_bytes(),original)
        self.assertEqual(copied.stat().st_mode&0o777,0o600)
        self.assertEqual(archive.stat().st_mode&0o777,0o700)
        self.assertFalse((jail/'dev-trace').exists())
        self.assertEqual((jail/'business.txt').read_text(),'untouched')
        self.assertEqual(json.loads((archive/'archive.json').read_text())['file_sha256']['old/event.json'],hashlib.sha256(original).hexdigest())
    def test_archive_history_unique_and_current_never_falls_back(self):
        jail=self.root/'jail'
        archive=self.root/'build/traces/archives/a/dev-trace/session/vm-1'
        archive.mkdir(parents=True)
        with patch.object(agent,'ROOT',self.root):
            self.assertEqual(agent.trace_directory(jail,'session','vm-1',True),archive)
            with self.assertRaises(RuntimeError):agent.trace_directory(jail,'session','vm-1')
            (self.root/'build/traces/archives/b/dev-trace/session/vm-1').mkdir(parents=True)
            with self.assertRaises(RuntimeError):agent.trace_directory(jail,'session','vm-1',True)
    def test_other_private_host_blocks_archive(self):
        jail=self.root/'jail';(jail/'dev-trace').mkdir(parents=True)
        state=self.root/'state'
        executable=state/'app/OctoSense Navigation.app/Contents/MacOS'/agent.BINARY.name
        with patch.object(agent,'STATE',state),patch.object(agent,'SESSION',self.root/'absent'),patch.object(agent.subprocess,'check_output',return_value=f'123 {executable}\n'):
            with self.assertRaises(RuntimeError):agent.archive_stopped_traces(jail)
        self.assertTrue((jail/'dev-trace').exists())
    def test_active_session_never_moved(self):
        jail=self.root/'jail';(jail/'dev-trace').mkdir(parents=True)
        session=self.root/'session.json';session.write_text('{}')
        with patch.object(agent,'SESSION',session),self.assertRaises(RuntimeError):agent.archive_stopped_traces(jail)
        self.assertTrue((jail/'dev-trace').exists())

if __name__=='__main__': unittest.main()
