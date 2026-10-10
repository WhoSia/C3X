#!/usr/bin/env python3
"""R1 fail-closed physical TT→same native SEE descendant observation, no SEE flip."""
import sys,unittest,copy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import (
    verify_precommitted_literals,exact_block,SCHEMA,SOURCE_SHA,STAGEA_SHA
)
class P1R1(unittest.TestCase):
    def test_source_preregistered_native_shas(self):
        self.assertEqual(len(SOURCE_SHA),len(STAGEA_SHA))
        self.assertEqual(SOURCE_SHA,"0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61")
        self.assertEqual(STAGEA_SHA,"fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442")
    def test_no_treatment_without_exact_forecast_and_original_source(self):
        with self.assertRaises((KeyError,AssertionError,RuntimeError)):
            verify_precommitted_literals({},{},{"status":"NOT_SEALED"})
    @patch("c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court.verified_reader_lineage")
    def test_exact_full64_slot_epoch_call_candidate(self,proof):
        proof.return_value={"all_valid":True,"count":1}
        src={"physical":{"key64":17,"slot":0,"epoch":3},
             "root_calls":[5,6],"root_candidate_native":29}
        base={"blocks":[{"kind":"reader_block","root_call":5,"root_move":29,
                         "key64":17,"slot":0,"epoch":3}],
              "lineage_summary":{"reader_block":1}}
        self.assertEqual(len(exact_block(base,src)[0]),1)
        for field,val in [("key64",18),("slot",1),("epoch",4),("root_call",6),("root_move",30)]:
            fail=copy.deepcopy(base)
            fail["blocks"][0][field]=val
            with self.assertRaises(RuntimeError):exact_block(fail,src)
    def test_stage_B_script_has_no_natural_SEE_mutation(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court.py").read_text()
        for term in ('"policy":"OBS","passive_ancestry":True',
                     '"SEE_Boolean_interventions":0',
                     'P1R1_SOURCE_DUPLICATE_COLD_MISMATCH',
                     'P1R1_SOURCE_OBS_SEE_PATH_DRIFT',
                     'verify_precommitted_literals(source,stagea,forecasts)',
                     'native_reader_writer_lineage_proof'):
            self.assertIn(term,s)
        self.assertNotIn('"policy":"FLIP"',s)
if __name__=="__main__":unittest.main()
