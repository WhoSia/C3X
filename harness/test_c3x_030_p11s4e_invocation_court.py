import unittest
from c3x_030_p11s4e_invocation_court import inspect,parse_event
class Cases(unittest.TestCase):
    def event(self,s):return parse_event("C3X_S4E "+s)
    def test_complete_local_invocation(self):
        es=[self.event("kind=probe id=4 parent=1 key=99 hit=1 ply=1 depth=4"),
            self.event("kind=normal_return id=4 parent=1 ply=1 value=28"),
            self.event("kind=scope_exit id=4 parent=1 ply=1 value_known=0"),
            self.event("kind=root_candidate id=1 child_last=4 root_move_raw=76 value=-28 old_best=-400 depth=4")]
        a=inspect(es)
        self.assertEqual(a["normal_returns_with_same_invocation_probe"],1)
        self.assertFalse(a["causal_parent_return_mediation_proven"])
    def test_inconsistent_parent_hold(self):
        es=[self.event("kind=probe id=4 parent=1 key=99 hit=1 ply=1 depth=4"),
            self.event("kind=scope_exit id=4 parent=9 ply=1 value_known=0"),
            self.event("kind=root_candidate id=1 child_last=4 root_move_raw=76 value=-28 depth=4")]
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_PARENT"):inspect(es)
    def test_missing_source_signal_hold(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_SIGNAL_NOT_OBSERVED"):inspect([])
    def test_invalid_event_id_hold(self):
        with self.assertRaisesRegex(ValueError,"MISSING_INVOCATION_ID"):
            self.event("kind=probe parent=1 ply=1")
if __name__=="__main__":unittest.main()
