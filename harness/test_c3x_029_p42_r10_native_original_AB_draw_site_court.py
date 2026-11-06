"""R10 source-site native event contract and causal outcome courts (synthetic)."""
import unittest
from c3x_029_p42_r10_native_original_AB_draw_site_court import observed, verdict

def roots():
    return {m:{"A":["b3a4"]*2,"B":["b3a4"]*2 if m=="3" else ["f3f4"]*2}
            for m in ("0","1","2","3")}
def counts():
    return {m:{a:[
      {"1":{"calls":1,"selected":int(m in ("1","3"))},
       "2":{"calls":1,"selected":int(m in ("2","3"))}}
      for _ in range(2)] for a in ("A","B")} for m in ("0","1","2","3")}
def line(site=1,mod=2,mode=1,ply=4):
    selected=int(mode==3 or mode==site)
    val=-1+(mod&2)
    return (f"c3x042_r10 site={site} ply={ply} mod4={mod} "
            f"original={val} selected={selected} result={0 if selected else val}\n")

class SourceSiteCourt(unittest.TestCase):
    def test_direct_cycle_contact(self):
        e=observed(line(1,2,1)+line(2,0,1),1)
        self.assertEqual(e["1"]["selected"],1)
        self.assertEqual(e["2"]["selected"],0)
    def test_direct_terminal_contact(self):
        e=observed(line(1,2,2)+line(2,2,2),2)
        self.assertEqual(e["1"]["selected"],0)
        self.assertEqual(e["2"]["selected"],1)
    def test_both_sites_contact(self):
        e=observed(line(1,1,3)+line(2,3,3),3)
        self.assertEqual(e["1"]["selected"],1)
        self.assertEqual(e["2"]["selected"],1)
    def test_no_call_never_invents_one(self):
        self.assertEqual(observed("",1)["1"]["calls"],0)
    def test_malformed_site_rejected(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            observed("c3x042_r10 site=33 ply=1 mod4=0 original=-1 selected=0 result=-1",0)
    def test_invalid_modified_value_rejected(self):
        with self.assertRaisesRegex(ValueError,"VALUE_OR_SCOPE_MISMATCH"):
            observed(line(1,2,1).replace("result=0","result=1"),1)
    def test_wrong_source_site_selection_rejected(self):
        with self.assertRaisesRegex(ValueError,"VALUE_OR_SCOPE_MISMATCH"):
            observed(line(2,2,2),1)
    def test_cycle_only_isolation_can_change_B(self):
        r=roots();r["1"]["B"]=["b3a4"]*2
        z=verdict(r,counts(),[True]*8)
        self.assertEqual(z["status"],"PASS_SOURCE_SITE_INTERVENTIONS_WITH_STABLE_HISTORICAL_CONTROLS")
        self.assertTrue(z["source_site_effects"]["1"]["B_root_changes"])
        self.assertFalse(z["source_site_effects"]["2"]["B_root_changes"])
        self.assertFalse(z["natural_guard_mediation_proven"])
    def test_both_sites_joint_only_nonadditive_case_allowed(self):
        z=verdict(roots(),counts(),[True]*8)
        self.assertEqual(z["status"],"PASS_SOURCE_SITE_INTERVENTIONS_WITH_STABLE_HISTORICAL_CONTROLS")
        self.assertFalse(z["source_site_effects"]["1"]["B_root_changes"])
        self.assertFalse(z["source_site_effects"]["2"]["B_root_changes"])
    def test_root_change_without_site_contact_rejected(self):
        r=roots();r["1"]["B"]=["b3a4"]*2
        c=counts();c["1"]["B"][1]["1"]["selected"]=0
        self.assertEqual(verdict(r,c,[True]*8)["status"],
                         "HOLD_CHANGED_ROOT_WITHOUT_MATCHED_SOURCE_CONTACT")
    def test_source_original_baseline_drift_rejected(self):
        r=roots();r["0"]["B"]=["b3a4"]*2
        self.assertEqual(verdict(r,counts(),[True]*8)["status"],
                         "HOLD_ORIGINAL_GAME14_BASELINE_DRIFT")
    def test_missing_tt_reader_rejected(self):
        self.assertEqual(verdict(roots(),counts(),[True]*7+[False])["status"],
                         "HOLD_PHYSICAL_TT_READER_PROOF")
    def test_historical_broad_effect_must_reproduce(self):
        r=roots();r["3"]["B"]=["f3f4"]*2
        self.assertEqual(verdict(r,counts(),[True]*8)["status"],
                         "HOLD_R9_BROAD_INTERVENTION_NOT_REPRODUCED")
    def test_replay_instability_rejected(self):
        r=roots();r["2"]["B"]=["f3f4","b3a4"]
        self.assertEqual(verdict(r,counts(),[True]*8)["status"],
                         "HOLD_SOURCE_ROOT_COLD_INSTABILITY")

if __name__=="__main__":
    unittest.main()
