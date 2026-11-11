import unittest
from c3x_030_p11s4a_stockfish_trace_patch import apply,INCLUDE,COUNTER,PROBE,SAVE
class Test(unittest.TestCase):
    def data(self):
        return "#include <algorithm>\n"+COUNTER+"\n"+PROBE+"\n"+SAVE+"\n"
    def test_both_search_events_patched(self):
        s=apply(self.data())
        self.assertIn("C3X_TT_EVENT kind=probe",s)
        self.assertIn("C3X_TT_EVENT kind=save",s)
        self.assertIn("std::atomic<unsigned> c3x_tt_events",s)
    def test_exactly_once_or_hold(self):
        with self.assertRaisesRegex(ValueError,"UPSTREAM_SOURCE_ANCHOR"):
            apply(self.data()+PROBE)
    def test_no_second_patch(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_PATCHED"):
            apply(apply(self.data()))
    def test_original_save_kept(self):
        s=apply(self.data())
        self.assertEqual(s.count("tte->save(posKey, value_to_tt(bestValue"),1)
        self.assertEqual(s.count("c3x_tt_events.fetch_add"),2)
if __name__=="__main__":unittest.main()
