import unittest
from c3x_030_p11s3_dual_original_audit import SCHEMA,A1,A2,ARMS,PHASES,COMMIT,audit

def fixtures():
    x={"schema":A1,"source_commit":COMMIT,"native_searches":480,
       "independent_confirmatory_cohort":False,"no_intentional_strength_prng":True,
       "binary_sha256":"a"*64,"cohort":{}}
    y={"schema":A2,"source_commit":COMMIT,"total_native_searches":140,
       "new_holdout_position_cohort":False,"chess_engine_skill_level":20,
       "stockfish_binary_sha256":"a"*64,"cohort":{}}
    for family in ("english","ruy_lopez","sicilian_najdorf","queens_gambit"):
        for ply in (4,6,8,10,12):
            id=family+"_ply"+str(ply)
            moves=["e2e4"]*6
            a={arm:{"trials":[{"move_uci":u,"nodes_actual":12000} for u in moves],
                    "summary":{"counts":{"e2e4":6},"actual_nodes_total":72000,
                               "observed_switch":False}} for arm in ARMS}
            b={phase:{"move_uci":"e2e4","nodes_actual":12000} for phase in PHASES}
            s={"clear1_restores":True,"clear2_restores":True,"warm1_differs":False,
               "warm2_differs":False,"after_clear1_warm_differs":False,
               "after_clear2_warm_differs":False}
            x["cohort"][id]={"fen":id,"history_uci":[],"arms":a}
            y["cohort"][id]={"fen":id,"history_uci":[],"phase_rows":b,"summary":s}
    x["native_nodes_total"]=480*12000
    x["within_arm_switch_position_counts"]={a:0 for a in ARMS}
    x["cross_arm_disagreements_with_cold_reference"]={a:0 for a in ARMS}
    y["total_actual_nodes"]=140*12000
    y["position_summary_counts"]={"clear1_restores":20,"clear2_restores":20,
        "warm1_differs":0,"warm2_differs":0,"after_clear1_warm_differs":0,
        "after_clear2_warm_differs":0}
    return x,y

class Test(unittest.TestCase):
    def test_frozen_integrity(self):
        x,y=fixtures();z=audit(x,y);self.assertEqual(z["new_native_searches_performed"],0)
        self.assertEqual(z["S2"]["clear1_restores"],20)
    def test_different_binaries_hold(self):
        x,y=fixtures();y["stockfish_binary_sha256"]="z"*64
        with self.assertRaisesRegex(ValueError,"SCOPE_OR_BINARY_IDENTITY"):audit(x,y)
    def test_one_tampered_move_hold(self):
        x,y=fixtures();x["cohort"]["english_ply4"]["arms"]["same_game_retained"]["trials"][2]["move_uci"]="d2d4"
        with self.assertRaisesRegex(ValueError,"S1_SUMMARY_MISMATCH"):audit(x,y)
    def test_resets_s2_summary_hold(self):
        x,y=fixtures();y["cohort"]["english_ply4"]["phase_rows"]["clear1"]["move_uci"]="d2d4"
        with self.assertRaisesRegex(ValueError,"S2_SUMMARY_MISMATCH"):audit(x,y)
if __name__=="__main__":unittest.main()
