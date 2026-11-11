"""Synthetic contract verification; P11 real 360-search fixture is CI artifact."""
import copy
import unittest
from c3x_030_p11_original_reanalysis import reanalyze, SCHEMA, FAMILIES, ARMS

def example():
    rows={}
    for fam in FAMILIES:
        for ply in (4,6,8,10,12):
            a={}
            for name in ARMS:
                trials=[{"move_uci":"a2a3","nodes_actual":12000}] * 6
                a[name]={"trials":trials,"summary":{"counts":{"a2a3":6},
                                      "actual_nodes_total":72000,
                                      "switch_observed":False}}
            rows[fam+"_ply"+str(ply)]={"fen":fam+str(ply),"arms":a}
    return {"schema":SCHEMA,"source_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
            "repeats_per_arm":6,"total_native_searches":360,
            "skill_level":20,"intentional_handicap_rng_enabled":False,
            "classical_evaluation_nnue_disabled":True,
            "native_source_causal_intervention_performed":False,"cohort":rows,
            "total_actual_native_nodes":360*12000}

class Audit(unittest.TestCase):
    def test_clean(self):
        r=reanalyze(example())
        self.assertEqual(r["totals"]["cold_parallel4"]["within_position_switches"],0)
        self.assertEqual(r["inherited_native_searches"],360)
    def test_cross_arm_different_without_within_arm_switch(self):
        x=example()
        a=x["cohort"]["ruy_lopez_ply4"]["arms"]["cold_parallel4"]
        a["trials"]=[dict(move_uci="b2b3",nodes_actual=12000)]*6
        a["summary"]["counts"]={"b2b3":6}
        y=reanalyze(x)
        self.assertEqual(y["totals"]["cold_parallel4"]["within_position_switches"],0)
        self.assertEqual(y["totals"]["cold_parallel4"]["positions_with_any_reference_disagreement"],1)
        self.assertEqual(y["totals"]["cold_parallel4"]["trials_disagreeing_with_cold_reference"],6)
    def test_tampered_counts_rejected(self):
        x=example()
        x["cohort"]["ruy_lopez_ply4"]["arms"]["warm_single"]["summary"]["counts"]={"b2b3":6}
        with self.assertRaisesRegex(ValueError,"TAMPERED_SUMMARY"):reanalyze(x)
    def test_dishonest_source_scope_rejected(self):
        x=example();x["skill_level"]=0
        with self.assertRaisesRegex(ValueError,"SCOPE"):reanalyze(x)
    def test_duplicate_positions_rejected(self):
        x=example()
        x["cohort"]["english_ply12"]["fen"]=x["cohort"]["english_ply10"]["fen"]
        with self.assertRaisesRegex(ValueError,"FEN_DUPLICATE"):reanalyze(x)

if __name__=="__main__":unittest.main()
