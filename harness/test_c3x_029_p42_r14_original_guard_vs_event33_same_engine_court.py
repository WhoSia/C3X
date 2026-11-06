"""R14 same pinned-source C guard vs single cycle event33 (synthetic tests)."""
import unittest
from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import (
    parsed_actions,parse_three_cold_root_worlds,compare_native_worlds
)

def boundaries(leader,score,avg):
    return [{'depth':d,'leader':99 if d<9 else leader,
             'score':-10 if d<9 else score,
             'average':-10 if d<9 else avg} for d in range(1,13)]
def four_worlds():
    return {'A':boundaries(99,-20,-20),'B':boundaries(1373,-74,-70),
            'C':boundaries(1112,-89,-79),'B33':boundaries(1112,-89,-80)}
def groups():
    out=[]
    for name in ('A','B','C'):
        for _ in range(2):
            for e in four_worlds()[name]:
                out.append('event=ROOT_BOUNDARY depth={depth} leader={leader} score={score} average={average}'.format(**e))
    return '\n'.join(out)+'\n'

class R14NativeConvergenceTests(unittest.TestCase):
    def test_strict_six_physical_source_runs_parsed(self):
        g=parse_three_cold_root_worlds(groups())
        self.assertEqual(g['B'][8]['leader',1373)
        self.assertEqual(g['C'][8]['score',-89)
    def test_missing_cold_native_run_holds(self):
        with self.assertRaisesRegex(ValueError,'NOT_SIX_NATIVE'):
            parse_three_cold_root_worlds('\n'.join(groups().splitlines()[:10]))
    def test_changed_cold_depth_boundary_holds(self):
        lines=groups().splitlines()
        lines[56]=lines[56].replace('score=-89','score=-85')
        with self.assertRaisesRegex(ValueError,'C_HOLD_COLD|_C_HOLD_COLD|C_HOLD'):
            parse_three_cold_root_worlds('\n'.join(lines))
    def test_malformed_native_capture_guard_holds(self):
        with self.assertRaisesRegex(ValueError,'MALFORMED'):
            parsed_actions('action=EXACT_ONE_EVENT_REENABLED key64=8')
    def test_native_capture_source_signature_kept_private(self):
        line='action=EXACT_ONE_EVENT_REENABLED key64=8 root_call=1 move=6 threshold=2'
        items=parsed_actions(line)
        self.assertEqual(items[0]['action'],'EXACT_ONE_EVENT_REENABLED')
    def test_two_independent_source_interventions_can_match_leader_score_not_average(self):
        worlds=four_worlds()
        res=compare_native_worlds(worlds,[{},{}],{'NO_DISCOVERED_ATTACK_CONTINUE':2})
        self.assertEqual(res['status'],'PASS_ACTUAL_NATIVE_C_AND_B33_SOURCE_ROOT_COMPARISON_ONLY')
        self.assertEqual(res['first_B_C_divergent_depth'],9)
        self.assertEqual(res['first_B_B33_divergent_depth'],9)
        self.assertEqual(res['first_C_B33_divergent_depth'],9)
        self.assertFalse(res['C_vs_B33_all_depth_summary_equal'])
        self.assertIn(9,res['C_vs_B33_matching_leader_and_score_depths'])
        self.assertFalse(res['natural_guard_cycle_mediation_certified'])
    def test_fully_identical_root_summaries_not_full_state_equivalence(self):
        worlds=four_worlds();worlds['B33']=worlds['C']
        res=compare_native_worlds(worlds,[{},{}],{})
        self.assertTrue(res['C_vs_B33_all_depth_summary_equal'])
        self.assertFalse(res['identical_full_source_search_state_certified'])
    def test_source_root_support_changes_hold(self):
        worlds=four_worlds();worlds['B33']=worlds['B33'][:-1]
        self.assertEqual(compare_native_worlds(worlds,[],{})['status'],
                         'HOLD_ROOT_DEPTH_SUPPORT_DIFFERENT')
    def test_source_root_depth_mismatch_hold(self):
        worlds=four_worlds();worlds['B33'][8]['depth']=10
        self.assertEqual(compare_native_worlds(worlds,[],{})['status'],
                         'HOLD_ROOT_DEPTH_IDENTITY_CHANGED')
    def test_root_boundary_values_public_without_original_chess_source_key(self):
        res=compare_native_worlds(four_worlds(),[{},{}],{})
        self.assertNotIn('key64',str(res))
        self.assertFalse(res['private_chess_key_exposed'])
if __name__=='__main__':
    unittest.main()
