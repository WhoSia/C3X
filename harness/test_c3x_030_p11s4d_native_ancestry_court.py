import unittest
from c3x_030_p11s4d_native_ancestry_court import parse_event,correlate
class Tests(unittest.TestCase):
    def test_source_hit(self):
        a=parse_event("C3X_S4D kind=probe seq=0 key=123 ply=1 parent_move_raw=76 hit=1 depth=7 alpha=-5 beta=8")
        self.assertEqual(a["kind"],"probe")
    def test_return(self):
        a=parse_event("C3X_S4D kind=normal_return seq=0 key=123 ply=1 parent_move_raw=76 best_value=42 alpha_final=0 beta=50")
        self.assertEqual(a["best_value"],"42")
    def test_root(self):
        a=parse_event("C3X_S4D kind=root_candidate seq=0 root_move_raw=76 root_value=-42 old_best=22 root_depth=7")
        self.assertEqual(a["root_move_raw"],"76")
    def test_false_claim_guard(self):
        e=[parse_event("C3X_S4D kind=probe seq=0 key=123 ply=1 parent_move_raw=76 hit=1 depth=7"),
           parse_event("C3X_S4D kind=root_candidate seq=0 root_move_raw=76 root_value=-42 root_depth=7")]
        x=correlate(e,"123")
        self.assertFalse(x["raw_value_medation_PROVEN"])
        self.assertFalse(x["trace_is_complete_search_tree"])
        self.assertEqual(x["raw_parent_move_also_observed_in_root_candidates"],["76"])
    def test_invalid_event_hold(self):
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_NATIVE_EVENT"):
            parse_event("C3X_S4D kind=probe seq=1 key=23")
if __name__=='__main__':unittest.main()
