import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p15_claim_authority_gate import assess
def row(kind):
    return dict(kind=kind,source_id="sealed-1",native_replay=True,legal_replay=True,
                competitor_refuted=True,matched_intervention=True,same_root_event_join=True,
                disjoint_prospective=True)
class Admission(unittest.TestCase):
    def test_declared_not_independent_certification(self):
        self.assertEqual(assess(row("transferred"))["status"],"DECLARED_PREREQUISITES_PRESENT_ONLY")
    def test_legal_replay_absent(self):
        x=row("descriptive");x["legal_replay"]=False
        self.assertEqual(assess(x)["status"],"HOLD_SOURCE_NOT_INDEPENDENTLY_REPLAYED")
    def test_no_competitor(self):
        x=row("contrastive");x["competitor_refuted"]=False
        self.assertEqual(assess(x)["status"],"HOLD_NO_MATCHED_COMPETITOR_REFUTER")
    def test_no_event_join(self):
        x=row("aligned");x["same_root_event_join"]=False
        self.assertEqual(assess(x)["status"],"HOLD_NO_WITHIN_RUN_JOIN")
    def test_transferred_requires_same_root_join(self):
        x=row("transferred");x["same_root_event_join"]=False
        self.assertEqual(assess(x)["status"],"HOLD_NO_WITHIN_RUN_JOIN")
    def test_no_transfer(self):
        x=row("transferred");x["disjoint_prospective"]=False
        self.assertEqual(assess(x)["status"],"HOLD_NO_PROSPECTIVE_TRANSFER")
if __name__=="__main__":unittest.main()
