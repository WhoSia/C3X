import unittest
from c3x_030_s4k_epoch_court import parse, compare_by_go
from c3x_030_s4k_go_epoch_patch import patch
from c3x_030_s4i_tt_early_cutoff_patch import TT_CUTOFF
from c3x_030_p11s4e_invocation_patch import NS,ENTRY,PROBE,RET,ROOT

def go_start(n):return f"C3X_S4K_GO_BEGIN epoch={n} cap_per_go=8"
def go_end(n,k):return f"C3X_S4K_GO_END epoch={n} source_cutoff_total={k}"
def event(n,ordinal,depth=3,value=40):
    return (f"C3X_S4I_TT_CUTOFF ordinal={ordinal} epoch={n} id={n*100+ordinal+1} "
        f"parent=5 key=123 ply=1 search_depth={depth} alpha=-20 beta=50 "
        f"pv=0 cutnode=1 return_value={value}")
def log(n1=1,n2=1):
    return ([go_start(1)]+[event(1,j) for j in range(min(n1,8))]+[go_end(1,n1)]
        +[go_start(2)]+[event(2,j) for j in range(min(n2,8))]+[go_end(2,n2)])
def cpp():
    pre="#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+TT_CUTOFF+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"
    pre+="\nvoid MainThread::search() {\n\n  if (Limits.perft)\n  {}\n"
    pre+="      Thread::search();          // main thread start searching\n  }\n\n  // When we reach the maximum depth"
    return pre

class TestGoEpoch(unittest.TestCase):
    def test_actual_per_trial_count(self):
        x=parse(log(3,10),"123")
        self.assertEqual(x["all_cutoff_events_total"],13)
        self.assertEqual(x["logged_cutoff_events_total"],11)
        self.assertFalse(x["trials"]["1"]["right_censored"])
        self.assertTrue(x["trials"]["2"]["right_censored"])
    def test_exact_eight_is_not_necessarily_truncated(self):
        x=parse(log(8,8),"123")
        self.assertFalse(x["trials"]["1"]["right_censored"])
    def test_missing_go_end_fails(self):
        with self.assertRaisesRegex(ValueError,"MISSING_GO"):parse(log()[:-1],"123")
    def test_duplicate_ordinal_fails(self):
        l=log();l.insert(2,l[1])
        with self.assertRaisesRegex(ValueError,"IDENTITY_OR_WINDOW"):parse(l,"123")
    def test_wrong_source_key_fails(self):
        with self.assertRaisesRegex(ValueError,"IDENTITY_OR_WINDOW"):parse(log(),"999")
    def test_total_must_cover_logged_events(self):
        l=log(2,1);l[3]=go_end(1,1)
        with self.assertRaisesRegex(ValueError,"TOTAL_DISAGREES"):parse(l,"123")
    def test_cross_arm_joins_own_epoch_only(self):
        sham=parse(log(),"123")
        two=parse(log(),"123")
        x=compare_by_go(sham,two)
        self.assertEqual(x["shared_states_total"],2)
        self.assertFalse(x["full_tt_to_root_causal_mediation_proven"])
    def test_original_source_epoch_patch_contract(self):
        s=patch(cpp())
        self.assertEqual(s.count("C3X_S4K_GO_BEGIN epoch="),1)
        self.assertEqual(s.count("C3X_S4K_GO_END epoch="),1)
        self.assertIn('" epoch=" << c3x_k_go_epoch.load',s)
        self.assertIn("return ttValue;",s)
    def test_double_patch_fails(self):
        with self.assertRaises(ValueError):patch(patch(cpp()))
if __name__=="__main__":unittest.main()
