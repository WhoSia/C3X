import unittest
from c3x_030_p11s4c_once_native_court import events,MARKER,SHAM
class Cases(unittest.TestCase):
    def test_one_valid_native_source_receipt(self):
        d={"stderr_other":[MARKER+"key=123 ply=1 depth=7 parent_move_raw=19 old_hit=1 new_hit=0"]}
        self.assertEqual(len(events(d)),1)
    def test_sham_has_no_event(self):
        self.assertEqual(events({"stderr_other":[]}),[])
    def test_bad_ply_receipt_hold(self):
        d={"stderr_other":[MARKER+"key=123 ply=4 depth=7 parent_move_raw=19 old_hit=1 new_hit=0"]}
        with self.assertRaisesRegex(ValueError,"BAD_PHYSICAL_EVENT"):events(d)
    def test_sham_key_not_zero(self):
        self.assertEqual(len(SHAM),20)
if __name__=="__main__":unittest.main()
