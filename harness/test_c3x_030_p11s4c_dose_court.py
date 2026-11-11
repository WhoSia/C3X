import unittest
from c3x_030_p11s4c_dose_court import physical_events,ARMS,DOSES
class Test(unittest.TestCase):
    def test_all_predeclared_arms(self):
        self.assertEqual(ARMS,("upstream","sham","zero","one","two","unbounded"))
        self.assertEqual((DOSES["zero"],DOSES["one"],DOSES["two"]),(0,1,2))
    def test_one_actual_native_event(self):
        lines=["C3X_S4C2_MASK ordinal=0 key=234 ply=1 parent_move_raw=19 depth=3 new_hit=0"]
        self.assertEqual(physical_events({"stderr_other":lines}),lines)
    def test_no_physical_contact(self):
        self.assertEqual(physical_events({"stderr_other":[]}),[])
    def test_wrong_ply_rejected(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED_SOURCE_EVENT"):
            physical_events({"stderr_other":["C3X_S4C2_MASK ordinal=0 ply=2 new_hit=0"]})
if __name__=="__main__":unittest.main()
