#!/usr/bin/env python3
"""Synthetic 256game×4 role exact M4 UCI literal exporter control, no native July source data."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_024_P4_print_human_git_1024role_six_model_literal_batches import record
M=("M0","M1","M2_depth11","M3_v1","M3_v2","M4_survivor")
class SixModelLiteralControls(unittest.TestCase):
    def make(self):
        gs=[]
        for i in range(1,257):
            roles={}
            for order in ("O","F"):
                roles[order]={}
                for role in ("STRICT","BROAD"):
                    hold=i==256 and order=="F" and role=="BROAD"
                    alt=i==1 and order=="O" and role=="STRICT"
                    r={"status":"HOLD_NO_PHYSICAL_FIRST_READER" if hold else "FROZEN_SOURCE_ELIGIBLE",
                       "M3_v1_trigger":False,"M3_v2_trigger":False,"M4_trigger":alt,
                       "M4_reason":"CROSS_ORDER_SURVIVOR_RECONFIRMED_SAME_ORDER" if alt else "M0_DEFAULT"}
                    for m in M:r[m]=None if hold else ("d2d4" if alt and m=="M4_survivor" else "e2e4")
                    roles[order][role]=r
            gs.append({"game_id":i,"source_game_sha256":format(i,"064x"),"root_orders":roles})
        return {"schema":"c3x024-P4-July2025-256-source-only-untreated-six-model-exact-UCI-FORECAST-NO-TREATMENT-v1",
                "source_games":256,"role_cell_denominator":1024,"TT_FIRST_interventions_seen":0,"SEE_boolean_interventions_seen":0,
                "summary":{"eligible_pre_FirST_physical_role_cells":1023,"M4_predicted_changes":1},"cases":gs}
    def test_1024_complete_exact_original_literal_rows(self):
        allrows,eligible,positive=record(self.make())
        self.assertEqual(len(allrows),256)
        self.assertEqual((eligible,positive),(1023,1))
        self.assertEqual(sum(len(x[2]) for x in allrows),1024)
        self.assertEqual(allrows[0][2][0][8],"d2d4")
        self.assertIsNone(allrows[-1][2][-1][8])
    def test_treated_forecast_is_rejected(self):
        j=self.make();j["TT_FIRST_interventions_seen"]=1
        with self.assertRaises(ValueError):record(j)
    def test_frozen_role_identity_cannot_be_dropped(self):
        j=self.make();j["cases"][0]["root_orders"]["O"].pop("BROAD")
        with self.assertRaises(KeyError):record(j)
if __name__=="__main__":unittest.main()
