#!/usr/bin/env python3
"""Before-SEE-actuator target selection must be deterministic and strict."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_R2_T2_prepare_literal_SEE_targets import prepare,DECIDED,SCHEMA
class SourceSitePreActuation(unittest.TestCase):
    def study(self):
        out=[]
        for gid,order,role in ((1,"O","STRICT"),(8,"O","BROAD"),
                                (11,"F","STRICT"),(12,"F","STRICT"),
                                (2,"O","STRICT"),(3,"O","STRICT")):
            matched=gid in (1,11,12,2)
            a={"site":"quiet_prune","key64":123,"parent_key64":111,
               "t1_exact_ancestor_path":"111,123",
               "source_root_call":4,"source_root_move":38,
               "move":72,"threshold":-95,
               "original_native_SEE_Boolean":1,
               "t1_source_line_ordinal_original":23,
               "t1_source_line_ordinal_TT_FIRST":30,
               "actual_source_TT_score_used_before_SEE":True,
               "actual_selected_TT_first_reader_blocked_before_SEE":True,
               "native_search_state":{k:0 for k in (
                 "t1_ply","t1_depth","t1_alpha","t1_beta","t1_pv",
                 "t1_qsearch","t1_rule50","t1_occupied_present","t1_occupied_out")}}
            out.append({"source_id":gid,"root_order":order,"source_role":role,
             "actual_terminal_bestmove_flipped":gid in (1,8,11,12),
             "causal_observational_state_classification":{
                 "exact_state_events":[a] if matched else []}})
        return {"schema":"c3x023-P1-R2-T1-native-same-search-state-SEE-after-TT-source-v1",
         "new_licensed_source_sha256":"0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61",
         "cases":out}
    def test_fixed_four_development_examples(self):
        r=prepare(self.study())
        self.assertEqual(r["summary"]["target_exact_node_ready"],4)
        self.assertEqual(len(r["cases"]),4)
        self.assertEqual(r["summary"]["source_T2_Boolean_interventions_performed"],0)
    def test_no_unsafe_extrapolation_if_no_quiet_source(self):
        a=self.study()
        a["cases"][0]["causal_observational_state_classification"]["exact_state_events"][0]["site"]="capture_prune"
        r=prepare(a)
        self.assertEqual(r["summary"]["target_scope_HOLD"],1)
        self.assertIsNone(r["cases"][0]["source_exact_pruning_SEE_target"])
    def test_frozen_schema_not_accepted_if_changed(self):
        with self.assertRaises(ValueError):prepare({"schema":"WRONG"})
if __name__=="__main__":unittest.main()
