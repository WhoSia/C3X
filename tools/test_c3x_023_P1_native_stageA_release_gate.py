#!/usr/bin/env python3
"""Do not upload experimental outcomes through an untreated licensed release."""
import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_023_rights_preupload_gate import licensed_lichess_native_stageA_audit
class NativeStageALicence(unittest.TestCase):
    def make(self):
        return {"schema":"c3x023-P1-licensed-May-and-CC0-stageA-untreated-native-node-SEE-rivals-v1",
         "phase":"NEW_P1_STAGE_A_ONLY_WITH_NO_INTERVENTION",
         "source_sha256":"0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61",
         "summary":{"actual_TT_FIRST_interventions":0,"actual_SEE_Boolean_interventions":0,
                    "treatment_outcomes_seen":False,"distinct_source_boards":32,
                    "potential_role_cells":128},
         "ecologies":{k:{"license":lic,"cases":[{"id":i,"worlds":{
                w:{"roles":{"STRICT":{},"BROAD":{}}} for w in ("O","F")}}
              for i in range(1,17)]}
           for k,lic in (("may2026_broadcast","CC BY-SA 4.0"),
                         ("lichess_CC0_nonmate_puzzles","CC0"))}}
    def test_frozen_unexposed_source_passes_policy_scan(self):
        self.assertEqual(licensed_lichess_native_stageA_audit(json.dumps(self.make()).encode()),[])
    def test_intervention_results_not_authorized(self):
        d=self.make();d["summary"]["actual_TT_FIRST_interventions"]=1
        self.assertIn("SOURCE_STUDY_NON_BLIND_TREATMENT",
                      licensed_lichess_native_stageA_audit(json.dumps(d).encode()))
    def test_board_personal_original_or_hidden_leaks(self):
        d=self.make();d["ecologies"]["may2026_broadcast"]["cases"][0]["fen4"]="..."
        self.assertIn("STAGEA_ORIGINAL_SOURCE_DATA_LEAK",
                      licensed_lichess_native_stageA_audit(json.dumps(d).encode()))
if __name__=="__main__":unittest.main()
