"""P2-D1 original native case/depth selection and negative contact controls."""
import json,os
from pathlib import Path
import unittest
from copy import deepcopy
from c3x_031_p2_d1_equal_depth import FROZEN_CASES,real_target,last_nodes

SOURCE=Path(os.environ.get("C3X_P2_SOURCE","/tmp/p2-precontact/C3X_031_P2_PHYSICAL_EVENT_AND_FORECAST_PRETREATMENT.json"))
TREATED=Path(os.environ.get("C3X_P2_TREATED","/tmp/p2-treated/C3X_031_P2_TWIC1670_TREATED_NATIVE_ALL_EVENTS.json"))


class P2D1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SOURCE.read_text())
        cls.treated=json.loads(TREATED.read_text())

    def test_exact_seven_original_root_flips(self):
        actual={r["id"]+"-"+g for r in self.treated["cases"]
                for g,row in r["targets"].items()
                if row["treatment_bestmove_changed"]}
        self.assertEqual(actual,set(FROZEN_CASES))

    def test_frozen_13_original_and_treatment_depth_cells(self):
        self.assertEqual(sum(len(set(depths)) for depths in FROZEN_CASES.values()),13)
        sources={x["id"]:x for x in self.source["source_events"]}
        treated={x["id"]:x for x in self.treated["cases"]}
        for key,(start,end) in FROZEN_CASES.items():
            game,group=key.rsplit("-",1)
            self.assertEqual(int(sources[game]["untouched_public"][0]),start)
            self.assertEqual(int(treated[game]["targets"][group]["arms"]["both_off"]["final_completed_depth"]),end)

    def test_actual_treatment_target_is_derived_from_untouched_source(self):
        row=self.source["source_events"][0]["targets"]["1"]
        self.assertEqual(row["status"],"UNTREATED_NATIVELY_OBSERVED_FORECAST_FROZEN")
        fake=[{"open":row["target"],"close":{"stopped":"0","skip_f":"0","skip_n":"0"}}]
        m,status=real_target(fake,row["target"])
        self.assertIsNotNone(m)
        self.assertEqual(status,"SOURCE_TARGET_PHYSICALLY_MATCHED")

    def test_changed_target_signature_is_held_not_relabelled(self):
        row=self.source["source_events"][0]["targets"]["1"]
        changed=deepcopy(row["target"])
        changed["attempt"]="999999"
        _,status=real_target([{"open":changed,"close":{"stopped":"0"}}],row["target"])
        self.assertEqual(status,"HOLD_PRECONTACT_TARGET_DRIFT")

    def test_missing_or_duplicated_source_contact_is_hold(self):
        row=self.source["source_events"][0]["targets"]["1"]["target"]
        x={"open":row,"close":{"stopped":"0"}}
        self.assertEqual(real_target([],row)[1],"HOLD_TARGET_ABSENT")
        self.assertEqual(real_target([x,x],row)[1],"HOLD_DUPLICATE_TARGET_ORDINAL")

    def test_depth_node_reporting_requires_actual_nodes(self):
        self.assertEqual(last_nodes(["info depth 13 score cp 20 nodes 12345 pv a2a4","bestmove a2a4"]),12345)
        with self.assertRaisesRegex(ValueError,"node/score"):
            last_nodes(["info depth 12 score cp 15 pv e2e4"])


if __name__=="__main__":
    unittest.main()
