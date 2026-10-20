import unittest
from harness.c3x_027_game14_transmission_adapter import assess, ContractError, GAME_SHA, SCHEMA

def case():
    return {"schema":SCHEMA,"game_sha256":GAME_SHA,"protocol":"STRICT_ONLY_15",
      "worlds":{"A":{"bestmove":"b3a4"},
        "B":{"bestmove":"f3f4","tt_writer_reader_valid":True,
             "original_see_boolean":False,"guard_action":"NO_DISCOVERED_ATTACK_CONTINUE"},
        "C":{"bestmove":"b3a4","tt_writer_reader_valid":True,
             "original_see_boolean":False,"guard_action":"EXACT_ONE_EVENT_REENABLED",
             "exact_reenable_count":1}}}
class C3X027TransmissionContract(unittest.TestCase):
    def test_historical_root_does_not_imply_descendant(self):
        g=assess(case())["gates"]
        self.assertTrue(g["G3"].startswith("PASS"))
        self.assertEqual(g["G4"],"HOLD_NOT_MEASURED")
        self.assertEqual(g["G9"],"HOLD_NOT_MEASURED")
    def test_physical_contact_missing(self):
        d=case();d["worlds"]["C"]["tt_writer_reader_valid"]=False
        self.assertEqual(assess(d)["gates"]["G1"],"FAIL_TT_LINEAGE")
    def test_protocols_must_not_merge(self):
        d=case();d["protocol"]="MERGED"
        with self.assertRaises(ContractError):assess(d)
    def test_no_bestmove_fabrication(self):
        d=case();d["worlds"]["C"]["bestmove"]="f3f4"
        with self.assertRaises(ContractError):assess(d)
    def test_trace_sequence_fails_closed(self):
        d=case();d["worlds"]["C"]["events"]=[{"event_sequence":2}]
        with self.assertRaises(ContractError):assess(d)
    def test_same_root_call_does_not_replace_frame_identity(self):
        d=case();d["worlds"]["C"]["target_guard_event_id"]="a"
        kinds=["GUARD_REENABLED","DO_MOVE_EXECUTED","CHILD_ENTERED"]
        d["worlds"]["C"]["events"]=[
            {"event_sequence":i+1,"target_guard_event_id":"a",
             "event_kind":k,"root_call":1,"frame_id":i+1}
            for i,k in enumerate(kinds)]
        with self.assertRaises(ContractError):assess(d)
if __name__=="__main__":unittest.main()
