"""P37/R5 integration tests against authentic sealed R1/R2 artifacts only."""
import copy, os, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[0]))
from c3x_029_p37_r5_real_human_continuation_court import (
    SOURCE_ZIP_SHA256,SOURCE_JSON_SHA256,SOURCE_MEMBER,
    PRED_ZIP_SHA256,PRED_JSON_SHA256,PRED_MEMBER,load,audit)

class HumanReplyCourt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a=os.environ.get("C3X_P37_SOURCE_ZIP")
        b=os.environ.get("C3X_P37_PRED_ZIP")
        if not a or not b:
            raise unittest.SkipTest("Original R1 source and R2 pre-referee predictions required")
        cls.source=load(a,SOURCE_ZIP_SHA256,SOURCE_MEMBER,SOURCE_JSON_SHA256)
        cls.pred=load(b,PRED_ZIP_SHA256,PRED_MEMBER,PRED_JSON_SHA256)

    def test_native_archived_human_reply(self):
        r=audit(self.source,self.pred)
        self.assertEqual((r["observed_human_reply_labels"],r["counterfactual_unobserved"]),(6,2))
        self.assertEqual(r["hits"],{"stockfish_pv":4,"simple_json":2,"c3x_legal_plan":1})
        self.assertEqual(r["paired_pv_c3x"],{"pv_only_vs_c3x":3,"c3x_only_vs_pv":0,
                            "both_pv_c3x":1,"neither_pv_c3x":2})

    def test_tampered_human_move_rejected(self):
        source=copy.deepcopy(self.source)
        source["sources"][0]["selected"]["full_game_uci"][31]="a7a6"
        with self.assertRaisesRegex(ValueError,"GAME_HISTORY_SHA"):audit(source,self.pred)

    def test_tampered_prediction_prefix_rejected(self):
        pred=copy.deepcopy(self.pred)
        pred["cases"][0]["original_prefix_uci"][0]="a2a4"
        with self.assertRaisesRegex(ValueError,"PREFIX"):audit(self.source,pred)

    def test_source_case_mismatch_rejected(self):
        pred=copy.deepcopy(self.pred)
        pred["cases"][0]["case_id"]="invalid"
        with self.assertRaisesRegex(ValueError,"CASE_ID"):audit(self.source,pred)

    def test_no_counterfactual_human_label_imputation(self):
        x=audit(self.source,self.pred)
        self.assertEqual(len(x["unobserved"]),2)
        self.assertTrue(all(v["label_state"]=="COUNTERFACTUAL_HUMAN_REPLY_UNOBSERVED"
                            for v in x["unobserved"]))

if __name__=="__main__":unittest.main()
