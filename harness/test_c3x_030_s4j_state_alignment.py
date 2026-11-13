import unittest
from c3x_030_s4j_state_alignment import parse,compare
from c3x_030_s4j_state_fingerprint_patch import patch
from c3x_030_s4i_tt_early_cutoff_patch import TT_CUTOFF
from c3x_030_p11s4e_invocation_patch import NS,ENTRY,PROBE,RET,ROOT

def line(n=0,key=123,depth=4,alpha=-25,beta=40,val=31):
    return f"C3X_S4I_TT_CUTOFF ordinal={n} id={n+8} parent=2 key={key} ply=1 search_depth={depth} alpha={alpha} beta={beta} pv=0 cutnode=1 return_value={val}"

class StateFingerprintTests(unittest.TestCase):
    def test_singleton_candidate_not_causality(self):
        x=compare(parse([line(val=31)],"123"),parse([line(val=30)],"123"))
        self.assertEqual(x["shared_candidate_state_count"],1)
        self.assertEqual(x["unique_candidate_states"][0]["value_diff"],-1)
        self.assertFalse(x["causal_state_alignment_proven"])
    def test_repeated_states_are_ambiguous(self):
        a=parse([line(),line(1)],"123");b=parse([line(val=10)],"123")
        x=compare(a,b)
        self.assertEqual(len(x["ambiguous_repeated_states"]),1)
        self.assertEqual(len(x["unique_candidate_states"]),0)
    def test_wrong_source_key_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_STATE"):parse([line(key=321)],"123")
    def test_invalid_window_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_STATE"):parse([line(alpha=40,beta=20)],"123")
    def test_ordinary_stderr_ignored(self):
        self.assertEqual(parse(["some warning"],"123")["observed"],0)
    def test_saturated_is_censored(self):
        self.assertTrue(parse([line(n=i) for i in range(8)],"123")["right_censored"])
    def test_cpp_source_patch_preserves_return(self):
        stub="#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+TT_CUTOFF+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"
        out=patch(stub)
        self.assertEqual(out.count("return ttValue;"),1)
        self.assertIn('" alpha=" << alpha',out)
        self.assertIn('" beta=" << beta',out)
        self.assertIn('" cutnode=" << int(cutNode)',out)
        self.assertEqual(out.count("tte = TT.probe(posKey, ss->ttHit);"),1)
    def test_double_patch_refused(self):
        stub="#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+TT_CUTOFF+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"
        with self.assertRaises(ValueError):patch(patch(stub))
if __name__=="__main__":unittest.main()
