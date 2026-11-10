"""C3X 0.30 R7-C: exact SARFA on real-model score-vector interface.

Fixtures below are purely artificial; actual model evidence lives only
in SHA-pinned original R7 workflow artifacts.
"""
import math
import unittest

from c3x_030_r7c_sarfa_on_real_qwen_explanation_prompt_contrast import (
    analyze,vector,R7_MODEL_JSON_SHA,SCHEMA,SCORER_SCHEMA,R5_AUDIT_SHA
)
from c3x_030_r6a_actual_open_decoder_blind_arm import ARMS,MODEL_ID,MODEL_REVISION


def fixture():
    base={"a2a3":-3.0,"b2b3":-2.0,"c2c3":-1.0}
    treated={"a2a3":0.0,"b2b3":-2.0,"c2c3":-1.0}
    reports={}
    for arm in ARMS:
        values=base if arm=="fen_only" else treated
        rows=[]
        for i in range(4):
            rows.append({
                "ordinal":i,"legal_actions_scored":len(values),
                "full_summed_log_probability_ranking":[
                    {"uci":u,"summed_log_probability":value,
                     "mean_log_probability_per_token":value/2,
                     "continuation_tokens":2} for u,value in values.items()]
            })
        reports[arm]={
            "schema":SCORER_SCHEMA,
            "condition":arm,
            "model_id":MODEL_ID,
            "model_revision":MODEL_REVISION,
            "source_target_and_original_reference_never_seen_during_inference":True,
            "entries":rows
        }
    audit={
        "schema":"c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1",
        "cases":[{"case_id":"oldcase:"+str(j),"candidate_control_packets":[
            {"root_uci_source_only_label_not_decoder_input":"a2a3"} for _ in range(2)]
        } for j in range(2)]
    }
    return reports,audit


class ActualModelSARFAContractTests(unittest.TestCase):
    def test_treated_explanation_boosts_selected_move(self):
        scores,audit=fixture()
        result=analyze(scores,audit,R5_AUDIT_SHA)
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(len(result["arms"]),4)
        for row in result["arms"]:
            self.assertEqual(row["n_increased_target_preference"],4)
            self.assertEqual(row["n_positive_sarfa"],4)
            self.assertGreater(row["rows"][0]["sarfa_positive_saliency"],0)

    def test_negatively_changed_target_has_zero_positive_sarfa(self):
        scores,audit=fixture()
        for x in scores["fen_plus_strict_masked"]["entries"]:
            x["full_summed_log_probability_ranking"][0]["summed_log_probability"]=-6.0
        result=analyze(scores,audit,R5_AUDIT_SHA)
        masked=next(x for x in result["arms"] if x["treated_arm"]=="fen_plus_strict_masked")
        self.assertEqual(masked["n_positive_sarfa"],0)
        self.assertEqual(masked["n_increased_target_preference"],0)
        self.assertTrue(all(r["treated_minus_fen_only_selected_probability"]<0 for r in masked["rows"]))

    def test_source_target_never_seen_by_model(self):
        scores,audit=fixture()
        del scores["fen_only"]["source_target_and_original_reference_never_seen_during_inference"]
        with self.assertRaisesRegex(ValueError,"MODEL_PROVENANCE"):
            analyze(scores,audit,R5_AUDIT_SHA)

    def test_nonidentical_action_set_rejected(self):
        scores,audit=fixture()
        scores["fen_plus_unmasked"]["entries"][0]["full_summed_log_probability_ranking"][0]["uci"]="d2d3"
        with self.assertRaisesRegex(ValueError,"NONIDENTICAL"):
            analyze(scores,audit,R5_AUDIT_SHA)

    def test_duplicate_action_rejected(self):
        scores,audit=fixture()
        rows=scores["fen_plus_unmasked"]["entries"][0]["full_summed_log_probability_ranking"]
        rows[0]["uci"]=rows[1]["uci"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            analyze(scores,audit,R5_AUDIT_SHA)

    def test_nonfinite_probability_rejected(self):
        scores,audit=fixture()
        scores["fen_only"]["entries"][0]["full_summed_log_probability_ranking"][0]["summed_log_probability"]=math.nan
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            analyze(scores,audit,R5_AUDIT_SHA)

    def test_wrong_sha_rejected(self):
        scores,audit=fixture()
        with self.assertRaisesRegex(ValueError,"SOURCE_AUDIT"):
            analyze(scores,audit,"wrong")

    def test_empty_or_missing_arms_rejected(self):
        scores,audit=fixture()
        del scores["fen_only"]
        with self.assertRaisesRegex(ValueError,"FIVE_MODEL_ARMS"):
            analyze(scores,audit,R5_AUDIT_SHA)


if __name__=="__main__":
    unittest.main()
