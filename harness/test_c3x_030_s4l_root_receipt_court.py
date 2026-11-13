import unittest
from c3x_030_s4l_root_receipt_court import parse,compare
from c3x_030_s4l_root_score_patch import patch
from c3x_030_p11s4e_invocation_patch import NS,ENTRY,PROBE,RET,ROOT
from c3x_030_s4i_tt_early_cutoff_patch import TT_CUTOFF

def e(n):return f"C3X_S4K_GO_BEGIN epoch={n} cap_per_go=8"
def z(n,root=1):return f"C3X_S4K_GO_END epoch={n} source_cutoff_total=0 root_score_total={root}"
def root(n,flag=1):
    return f"C3X_S4L_ROOT_SCORE ordinal=0 epoch={n} root_move_raw=42 value=9 old_best=5 alpha=1 beta=20 move_count=1 will_update_best={flag} will_update_root_pv=1 depth=3"
def sample():return [e(1),root(1),z(1),e(2),root(2),z(2)]
class S4LTest(unittest.TestCase):
    def test_valid_root_score(self):
        x=parse(sample(),"123")
        self.assertEqual(x["all_root_score_events_total"],2)
        self.assertFalse(x["trials"]["1"]["root_score_right_censored"])
    def test_false_update_flag_rejected(self):
        x=sample();x[1]=root(1,0)
        with self.assertRaisesRegex(ValueError,"FALSE_ROOT"):parse(x,"123")
    def test_unmatched_root_total_rejected(self):
        x=sample();x[2]=z(1,2)
        with self.assertRaisesRegex(ValueError,"TOTAL_RECEIPT"):parse(x,"123")
    def test_epoch_alignment_not_event_identity(self):
        a=parse(sample(),"123")
        q=compare(a,a)
        self.assertFalse(q["root_value_counterfactual_mediation_proven"])
        self.assertTrue(q["root_update_site_by_epoch"]["1"]["never_align_root_receipts_by_ordinal"])
    def test_missing_epoch_rejected(self):
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_EPOCH"):parse(sample()[:-3],"123")
    def test_source_only_inserts_read_only_before_rootmove(self):
        src="#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+TT_CUTOFF+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"
        src+="\nvoid MainThread::search() {\n      Thread::search();          // main thread start searching\n  }\n\n  // When we reach the maximum depth"
        out=patch(src)
        self.assertEqual(out.count('C3X_S4L_ROOT_SCORE ordinal='),1)
        self.assertEqual(out.count('" root_score_total="'),1)
        self.assertEqual(out.count('tte = TT.probe(posKey, ss->ttHit);'),1)
if __name__=="__main__":unittest.main()
