#!/usr/bin/env python3
"""Synthetic-only controls: 256 games, 1003 native contacts, 21 frozen HOLD,
exactly one M4 positive prediction; no actual July2025 outcomes.
"""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_024_P4_July256_after_human_seal_game_cluster_M4_vs_M0 import audit
MODELS=("M0","M1","M2_depth11","M3_v1","M4_survivor")
class GateTester(unittest.TestCase):
    def synth(self,path,misreport=False):
        for shard in range(4):
            rows=[]
            for g in range(shard*64+1,shard*64+65):
                arms=[]
                for role_idx,(order,role) in enumerate(((o,r) for o in ("O","F") for r in ("STRICT","BROAD"))):
                    unit=(g-1)*4+role_idx
                    hold=unit<21
                    m0="e2e4";v2="d2d4" if unit==21 else m0
                    f={"M0":m0,"M1":"d2d4","M2_depth11":m0,"M3_v1":m0,"M3_v2":m0,"M4_survivor":v2}
                    x={"root_order":order,"role":role,
                       "status":"PRESEALED_INELIGIBLE_NO_FIRST_READER" if hold else "REAL_NATIVE_PHYSICAL_TT_FIRST",
                       "predicted":{k:(None if hold else v) for k,v in f.items()},
                       "treated_bestmove":None if hold else "d2d4" if unit==21 else "e2e4",
                       "correct":{k:(None if hold else int((v=="d2d4") if unit==21 else (v=="e2e4")))
                                  for k,v in f.items()},
                       "source_TT_first_contact":not hold,
                       "selected_native_reader_blocks":0 if hold else 1,
                       "cold_pairs_checked":0 if hold else 2,
                       "source_SEE_Boolean_flips":0,
                       "actual_root_flip":False if not hold else None}
                    arms.append(x)
                rows.append({"game_id":g,"roles":arms})
            result={"schema":"c3x024-P4-256game-human-Git-presealed-six-model-physical-TT-FIRST-shard-v1",
                    "shard":shard,"case_range":[shard*64+1,shard*64+64],
                    "source_games":64,"potential_roles":256,
                    "model_forecast_source_SHA256":"fictional-synthetic-source-forecast",
                    "untreated_stageA_SHA256":"fictional-synthetic-stage",
                    "original_source_JSON_SHA256":"fictional-synthetic-original",
                    "treated_SEE_Boolean_flips":0,"all_cells":rows}
            if misreport and shard==0:result["case_range"]=[999,1000]
            (path/f"C3X024_P4_TREATED_SHARD_{shard}.json").write_text(json.dumps(result))
    def test_stable_game_level_independent_denominator(self):
        with tempfile.TemporaryDirectory() as p:
            dir=Path(p);self.synth(dir)
            (dir/'fixture_seal.json').write_text(json.dumps({'forecast_raw_SHA256':'fictional-synthetic-source-forecast','stageA_untreated_raw_SHA256':'fictional-synthetic-stage','source_JSON_SHA256':'fictional-synthetic-original','eligible_first_reader_role_cells':1003,'prior_HOLD_roles':21,'M4_predicted_changes':1}))
            out=audit(dir,dir/'fixture_seal.json')
            self.assertEqual(out["independent_source_game_rows"],256)
            self.assertEqual(out["presealed_ineligible_role_cells"],21)
            self.assertEqual(out["real_native_physical_FIRST_contact_roles"],1003)
            self.assertEqual(out["M4_survivor_precommitted_positive_predictions"],1)
            self.assertEqual(out["M4_survivor_vs_M0_per_game_average_role_accuracy_comparison"]["wins"],1)
            self.assertEqual(out["M4_survivor_vs_M0_per_game_average_role_accuracy_comparison"]["losses"],0)
    def test_bad_shard_fails_without_promoting_exposure(self):
        with tempfile.TemporaryDirectory() as p:
            dir=Path(p);self.synth(dir,True)
            (dir/'fixture_seal.json').write_text(json.dumps({'forecast_raw_SHA256':'fictional-synthetic-source-forecast','stageA_untreated_raw_SHA256':'fictional-synthetic-stage','source_JSON_SHA256':'fictional-synthetic-original','eligible_first_reader_role_cells':1003,'prior_HOLD_roles':21,'M4_predicted_changes':1}))
            with self.assertRaises(ValueError):audit(dir,dir/'fixture_seal.json')
if __name__=="__main__":unittest.main()
