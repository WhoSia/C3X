"""P41/R5 adversarial branch-sampling checks; original bytes required in CI."""
import copy
import json
import os
import unittest
from pathlib import Path
from c3x_029_p41_r5_lexical_reply_sample_control import audit,source


def artificial():
    return {"game_events":8,"candidate_worlds":16,
        "cases":[{"case_id":str(i),"event_family":"event-"+str(i),
                  "worlds":[{
                      "root_uci":name,"w":9,
                      "branches":[{"opponent_reply":"a1a2","b":1},
                                  {"opponent_reply":"b1b2","b":2},
                                  {"opponent_reply":"c1c2","b":3},
                                  {"opponent_reply":"d1d2","b":9}]}
                      for name in ("a2a3","b2b3")]}
                 for i in range(8)]}


class TruncationAudit(unittest.TestCase):
    def test_strict_subset_misses_lexical_fourth_response(self):
        d=audit(artificial())
        self.assertEqual(d["worlds_missing_worst"],16)
        self.assertEqual(d["sum_missed_w_gap"],16*6)

    def test_full_k_restores_all_w(self):
        d=audit(artificial(),k=4)
        self.assertEqual(d["worlds_missing_worst"],0)

    def test_tampered_source_w_is_rejected(self):
        data=artificial();data["cases"][0]["worlds"][0]["w"]+=1
        with self.assertRaisesRegex(ValueError,"FULL_W"):
            audit(data)

    def test_duplicate_opponent_replies_rejected(self):
        data=artificial()
        data["cases"][0]["worlds"][0]["branches"][1]["opponent_reply"]="a1a2"
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            audit(data)

    def test_exact_original_historical_result_when_available(self):
        path=os.environ.get("C3X_P41_R5_ORIGINAL")
        if not path:
            self.skipTest("Only original P39 SHA-verified source proves historical count")
        d=audit(source(Path(path)))
        self.assertEqual((d["worlds_missing_worst"],d["sum_missed_w_gap"],
                          d["max_missed_w_gap"]),(14,278,51))
        self.assertEqual(d["source_events"],8)


if __name__=="__main__":
    unittest.main()
