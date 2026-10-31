#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p9_r13_replay_metadata_gate import PIN,ARMS,classify

def fixture():
    d={"schema":"c3x029-P9-R13-replay-metadata-v1",
       "case_id":"may2026-broadcast-game2",
       "source_sha256":"0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61",
       "binary_sha256":"a"*64,"patch_chain_sha256":"b"*64,
       "cold_processes_per_arm":2,**PIN}
    d["arms"]={a:{"bestmove":"e1g1","nodes":20062,"score_cp":-8,
        "tt_reader_block":a.startswith("TT1_"),"see_source_hit":1,"see_actuator_delivered":a.endswith("_FLIP"),"source_replay_equal":True} for a in ARMS}
    return d

class ReplayGate(unittest.TestCase):
    def test_ready_is_not_mechanism_pass(self):
        x=classify(fixture())
        self.assertEqual(x["status"],"READY_FOR_EXACT_NUMERIC_REPLAY_COMPARISON")
        self.assertEqual(x["caution"],"DOES_NOT_CERTIFY_CAUSAL_MEDIATION")
    def test_depth_shift_not_original_replay(self):
        d=fixture();d["depth"]=16
        self.assertEqual(classify(d)["status"],"CONFIGURATION_SHIFT_NOT_ORIGINAL_REPLAY")
    def test_missing_source_hash_fails(self):
        d=fixture();d["source_sha256"]="wrong"
        with self.assertRaisesRegex(ValueError,"SOURCE_SHA"):classify(d)
    def test_missing_see_contact_fails(self):
        d=fixture();d["arms"]["TT1_SEE_FLIP"]["see_source_hit"]=0
        self.assertEqual(classify(d)["status"],"FAIL_SOURCE_OR_OBSERVER_PARITY")
    def test_one_cold_repeat_is_hold(self):
        d=fixture();d["cold_processes_per_arm"]=1
        self.assertEqual(classify(d)["status"],"HOLD_INSUFFICIENT_COLD_REPEATS")
    def test_missing_binary_hold(self):
        d=fixture();d["binary_sha256"]=""
        self.assertEqual(classify(d)["status"],"HOLD_UNVERIFIED_BINARY_OR_PATCH")

if __name__=="__main__":unittest.main()
