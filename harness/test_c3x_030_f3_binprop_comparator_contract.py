import random
import unittest
import chess
from c3x_030_f3_binprop_comparator_contract import evaluate_episode, score_candidate, GROUPS, METHODS

def fixture():
    boards=[]
    for i in range(sum(GROUPS.values())):
        b=chess.Board()
        rng=random.Random(4400+i)
        for _ in range(10):
            b.push(rng.choice(list(b.legal_moves)))
        boards.append({"position_id":f"pos{i}","game_id":f"game{i//2}","fen":b.fen()})
    pools={}
    at=0
    for name,n in GROUPS.items():
        pools[name]=boards[at:at+n]
        at+=n
    predictions={g:[(g.endswith("positive")) for _ in range(n)] for g,n in GROUPS.items()}
    motif={"name":"independent-motif","valid":True,
           "source_kind":"externally_executed_boolean",
           "delta":0.5,"predictions":predictions}
    direct=dict(motif,name="direct-motif",delta=None)
    return {"schema":"c3x030-f3-binary-concept-matched-episode-v1",
            "episode_id":"synthetic-contract-only",
            "labels_are_external":True,
            "paper_episode_same_game_continuations":True,
            "ranking_frozen_before_heldout":True,
            "pools":pools,
            "methods":{"direct":[direct],"binprop":[motif],"c3x_boolean_concept":[]}}

class PaperFaithfulContract(unittest.TestCase):
    def test_no_real_claim_and_correct_score(self):
        result=evaluate_episode(fixture())
        self.assertEqual(result["methods"]["binprop"]["score"],1)
        self.assertEqual(result["methods"]["direct"]["score"],1)
        self.assertEqual(result["methods"]["c3x_boolean_concept"]["score"],0)
        self.assertEqual(result["paper_superiority_verdict"],"HOLD")
        self.assertFalse(result["game_disjoint_external_cohort_claim"])
    def test_nearby_negatives_are_primary_hard_counterfactual(self):
        e=fixture();e["methods"]["binprop"][0]["predictions"]["holdout_nearby_negative"]=[False]*4+[True]*4
        self.assertEqual(evaluate_episode(e)["methods"]["binprop"]["score"],0.5)
    def test_duplicate_board_is_not_independent(self):
        e=fixture();e["pools"]["holdout_negative"][0]["fen"]=e["pools"]["support_positive"][0]["fen"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_BOARD"):
            evaluate_episode(e)
    def test_illegal_chess_fen_rejected(self):
        e=fixture();e["pools"]["support_positive"][0]["fen"]="not-a-fen"
        with self.assertRaisesRegex(ValueError,"INVALID_CHESS_FEN"):
            evaluate_episode(e)
    def test_invented_external_labels_fail_closed(self):
        e=fixture();e["labels_are_external"]=False
        with self.assertRaisesRegex(ValueError,"NO_EXTERNAL"):
            evaluate_episode(e)
    def test_uncomparable_shap_values_cannot_be_cast_to_boolean_motifs(self):
        e=fixture();e["methods"]["shap"]=[]
        with self.assertRaisesRegex(ValueError,"UNCOMPARABLE"):
            evaluate_episode(e)
    def test_binprop_discovery_delta_required(self):
        e=fixture();e["methods"]["binprop"][0]["delta"]=None
        with self.assertRaisesRegex(ValueError,"BINPROP_DELTA"):
            evaluate_episode(e)
    def test_direct_does_not_require_binprop_delta(self):
        e=fixture()
        self.assertIsNone(e["methods"]["direct"][0]["delta"])
        self.assertEqual(evaluate_episode(e)["methods"]["direct"]["score"],1)
    def test_fallback_on_low_support(self):
        e=fixture();e["methods"]["binprop"][0]["predictions"]["support_positive"]=[False]*3+[True]
        r=evaluate_episode(e)
        self.assertTrue(r["methods"]["binprop"]["used_fallback"])
        self.assertEqual(len(r["methods"]["binprop"]["selection_names"]),1)
    def test_boolean_not_float(self):
        e=fixture();e["methods"]["binprop"][0]["predictions"]["holdout_positive"][0]=1
        with self.assertRaisesRegex(ValueError,"PREDICTION_LENGTH_OR_BOOLEAN"):evaluate_episode(e)
if __name__=="__main__":unittest.main()
