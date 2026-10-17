import importlib.util
from pathlib import Path
import unittest
import hashlib
import json
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'i10_p8_native_trace_adapter.py'
spec = importlib.util.spec_from_file_location('adapter', SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class AdapterTests(unittest.TestCase):
    def test_byte_custody_and_order(self):
        b = b'uciok\r\ninfo string c3x025_p12 kind=SOURCE_EVENT call_id=2\r\nbestmove e2e4\r\n'
        e, r = adapter.transform(b, 'run1', None)
        self.assertEqual(e['lines'][1], 'info string c3x025_p12 kind=SOURCE_EVENT call_id=2')
        self.assertEqual(e['lines'][2], 'bestmove e2e4')
        self.assertEqual(r['raw_sha256'], hashlib.sha256(b).hexdigest())
        self.assertEqual(r['recognized_family_line_count'], 1)
        self.assertEqual(e['schema'], 'c3x-p7-raw-uci-v1')
    def test_strict_encoding(self):
        with self.assertRaises(adapter.Hold): adapter.transform(b'\xff', 'r', None)
    def test_zero_known_events_remains_legitimate(self):
        _,r=adapter.transform(b'uciok\nbestmove e2e4\n', 'r', None)
        self.assertEqual(r['recognized_family_line_count'], 0)
    def test_empty_rejected(self):
        with self.assertRaises(adapter.Hold): adapter.transform(b'', 'r', None)
    def test_no_overwrite_cli(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); raw=d/'raw.log'; a=d/'in.json'; b=d/'receipt.json'
            raw.write_bytes(b'info string c3x025_p13 kind=Q_BEST_VALUE_ASSIGNED child_id=2\n')
            args=['--raw',str(raw),'--run-id','test','--output-json',str(a),'--output-receipt',str(b)]
            self.assertEqual(adapter.main(args),0)
            self.assertEqual(adapter.main(args),1)
            self.assertEqual(json.loads(a.read_text())['run_id'],'test')

if __name__=='__main__': unittest.main()
