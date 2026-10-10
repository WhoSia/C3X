#!/usr/bin/env python3
"""Synthetic-only controls: 128 games, 501 native contacts, 11 frozen HOLD,
exactly one M3-v2 positive prediction; does not load any Sept2025 outcomes.
"""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_024_P3_Sep128_after_preseal_game_cluster_model_score import audit
MODELS=("M0","M1","M2_depth11","M3_v1","M3_v2")
class GateTester(unittest.TestCase):
    def synth(self,path,misreport=False):
        for shard in range(4):
            rows=[]
            for g in range(shard*32+1,shard*32+33):
                arms=[]
                for role_idx,(order,role) in enumerate(((o,r) for o in ("O","F") for r in ("STRICT","BROAD"))):
                    unit=(g-1)*4+role_idx
                    hold=unit<11
                    m0="e2e4";v2="d2d4" if unit==11 else m0
                    f={"M0":m0,"M1":"d2d4","M2_depth11":m0,"M3_v1":m0,"M3_v2":v2}
                    x={"root_order":order,"role":role,
                       "status":"PRESEALED_INELIGIBLE_NO_FIRST_READER" if hold else "REAL_NATIVE_PHYSICAL_TT_FIRST",
                       "predicted":{k:(None if hold else v) for k,v in f.items()},
                       "treated_bestmove":None if hold else "d2d4" if unit==11 else "e2e4",
                       "correct":{k:(None if hold else int((v=="d2d4") if unit==11 else (v=="e2e4")))
                                  for k,v in f.items()},
                       "source_TT_first_contact":not hold,
                       "selected_native_reader_blocks":0 if hold else 1,
                       "cold_pairs_checked":0 if hold else 2,
                       "source_SEE_Boolean_flips":0,
                       "actual_root_flip":False if not hold else None}
                    arms.append(x)
                rows.append({"game_id":g,"roles":arms})
            result={"schema":"c3x024-P3-128game-human-Git-presealed-five-model-physical-TT-FIRST-shard-v1",
                    "shard":shard,"case_range":[shard*32+1,shard*32+32],
                    "source_games":32,"potential_roles":128,
                    "model_forecast_source_SHA256":"c402a6808bcaa2d73ec58632f87aa4ba7e8be0577b051b85e0a5610750eb1887",
                    "untreated_stageA_SHA256":"1c9f265b507712069442956c3ecf0dcdcb7e9abbeaaff4b683ba9beb263d3b09",
                    "original_source_JSON_SHA256":"ee8265f96b055645428f2fa87b36647e1931c86c848db5725a8b0ec63596dacb",
                    "treated_SEE_Boolean_flips":0,"all_cells":rows}
            if misreport and shard==0:result["case_range"]=[999,1000]
            (path/f"C3X024_P3_TREATED_SHARD_{shard}.json").write_text(json.dumps(result))
    def test_stable_game_level_independent_denominator(self):
        with tempfile.TemporaryDirectory() as p:
            dir=Path(p);self.synth(dir)
            out=audit(dir)
            self.assertEqual(out["independent_source_game_rows"],128)
            self.assertEqual(out["presealed_ineligible_role_cells"],11)
            self.assertEqual(out["real_native_physical_FIRST_contact_roles"],501)
            self.assertEqual(out["M3_v2_precommitted_positive_predictions"],1)
            self.assertEqual(out["M3_v2_vs_M0_per_game_average_role_accuracy_comparison"]["wins"],1)
            self.assertEqual(out["M3_v2_vs_M0_per_game_average_role_accuracy_comparison"]["losses"],0)
    def test_bad_shard_fails_without_promoting_exposure(self):
        with tempfile.TemporaryDirectory() as p:
            dir=Path(p);self.synth(dir,True)
            with self.assertRaises(ValueError):audit(dir)
if __name__=="__main__":unittest.main()
