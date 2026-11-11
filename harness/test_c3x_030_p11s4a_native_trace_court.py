import unittest
from c3x_030_p11s4a_native_trace_court import compare_records,trace_events,parse_info
class Test(unittest.TestCase):
    def record(self,move="e2e4"):
        return {"trials":[{"bestmove":move,"depth":8,"nodes":12013,"score":("cp",30),
                           "pv":["e2e4","e7e5"]}]}
    def test_no_event_does_not_qualify(self):
        s=compare_records(self.record(),dict(self.record(),events=[]))
        self.assertTrue(s["noninterference_pass"])
        self.assertFalse(s["events_both_probe_and_save"])
    def test_detect_changed_choice(self):
        s=compare_records(self.record(),dict(self.record("d2d4"),events=[]))
        self.assertFalse(s["noninterference_pass"])
    def test_two_valid_source_events(self):
        x=trace_events(["C3X_TT_EVENT kind=probe index=0 ply=1 key=123 hit=0 depth=4 root=0",
                        "C3X_TT_EVENT kind=save index=0 ply=1 key=123 value=5 depth=4 root=0"])
        s=compare_records(self.record(),dict(self.record(),events=x))
        self.assertTrue(s["events_both_probe_and_save"])
    def test_info_parser(self):
        info=parse_info("info depth 10 seldepth 12 score cp 12 nodes 15001 pv e2e4 e7e5")
        self.assertEqual(info["score"],("cp",12))
        self.assertEqual(info["depth"],10)
        self.assertEqual(info["nodes"],15001)
    def test_malformed_event_reject(self):
        with self.assertRaisesRegex(ValueError,"BAD_ENGINE_TRACE"):
            trace_events(["C3X_TT_EVENT fake"])
if __name__=="__main__":unittest.main()
