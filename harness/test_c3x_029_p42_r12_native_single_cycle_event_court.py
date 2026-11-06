"""R12 synthetic source matching, causal selection and negative verdict tests."""
import unittest
from c3x_029_p42_r12_native_single_cycle_event_court import (
 selected_ordinals,match_single_event,summarize_court,PREFIX_LIMIT
)

def ev(i):
    # exactly four candidate original cutoff decision changes when swapped to zero.
    # -1 versus beta==0 changes non-cutoff->cutoff; +1 beta==1 changes cutoff->no-cutoff.
    flip=i in (3,8,18,29)
    val=-1 if (flip or i%2==0) else 1
    beta=0 if flip else (-4 if val<0 else 0)
    return {'key':1234+i,'ply':2,'depth':5,'mod4':0 if val==-1 else 2,
            'old_alpha':-6,'beta':beta,'candidate':val,
            'cutoff':int(val>=beta),'root_move':999}
def baseline():
    e=[ev(i) for i in range(1,PREFIX_LIMIT+1)]
    return [{'move':'f3f4','events':e,'reader_valid':True} for _ in range(2)]
def probed(b,ordinal,move='f3f4'):
    out=[]
    for trial in range(2):
        copy=[dict(x) for x in b[trial]['events']]
        copy[ordinal-1]['candidate']=0
        copy[ordinal-1]['cutoff']=int(0>=copy[ordinal-1]['beta'])
        out.append({'move':move,'events':copy,'reader_valid':True})
    return out

class R12NativeSingleEventTests(unittest.TestCase):
    def test_source_selection_is_four_real_cutoff_changers(self):
        self.assertEqual(selected_ordinals(baseline()[0]['events']),[3,8,18,29])
    def test_selected_ordinal_is_true_source_cutoff_change(self):
        b=baseline();p=probed(b,3)
        self.assertEqual(match_single_event(b[0]['events'],p[0]['events'],3),
                         'PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX')
    def test_source_identity_drift_rejected(self):
        b=baseline();p=probed(b,8)
        p[0]['events'][4]['key']=777
        self.assertEqual(match_single_event(b[0]['events'],p[0]['events'],8),
                         'HOLD_PREINTERVENTION_NATIVE_SOURCE_IDENTITY_DRIFT')
    def test_second_event_change_rejected(self):
        b=baseline();p=probed(b,18)
        p[0]['events'][4]['candidate']=0
        self.assertEqual(match_single_event(b[0]['events'],p[0]['events'],18),
                         'HOLD_INCORRECT_SOURCE_EVENT_MUTATION_SCOPE')
    def test_missing_target_source_event_holds(self):
        b=baseline();p=probed(b,18)
        self.assertEqual(match_single_event(b[0]['events'],p[0]['events'][:12],18),
                         'HOLD_SINGLE_NATIVE_SOURCE_EVENT_MISSING')
    def test_no_preselected_counterfactual_cutoff_holds(self):
        b=baseline();p=probed(b,4)
        self.assertEqual(match_single_event(b[0]['events'],p[0]['events'],4),
                         'HOLD_SOURCE_EVENT_NOT_A_FROZEN_CUTOFF_DISAGREEMENT')
    def test_full_native_synthetic_falsification_no_single_flip(self):
        b=baseline()
        p={o:probed(b,o) for o in (3,8,18,29)}
        r=summarize_court(b,p,[3,8,18,29],[True]*8,[True]*2)
        self.assertEqual(r['status'],'PASS_FOUR_ORIGINAL_SINGLE_EVENT_SOURCE_INTERVENTIONS_ONLY')
        self.assertEqual(r['successful_single_event_root_restorations'],0)
        self.assertFalse(r['single_event_source_to_root_path_certified'])
        self.assertNotIn('1234',str(r))
    def test_single_native_target_root_restoration_registered_without_overclaim(self):
        b=baseline()
        p={o:probed(b,o,'b3a4' if o==8 else 'f3f4') for o in (3,8,18,29)}
        r=summarize_court(b,p,[3,8,18,29],[True]*8,[True]*2)
        self.assertEqual(r['successful_single_event_root_restorations'],1)
        self.assertFalse(r['natural_causal_mediation_certified'])
    def test_unknown_third_candidate_kept_and_not_binary_forced(self):
        b=baseline()
        p={o:probed(b,o,'h2h4' if o==3 else 'f3f4') for o in (3,8,18,29)}
        r=summarize_court(b,p,[3,8,18,29],[True]*8,[True]*2)
        self.assertIn('h2h4',r['targets'][0]['native_bestmoves'])
    def test_missing_native_tt_reader_holds(self):
        b=baseline();p={o:probed(b,o) for o in (3,8,18,29)}
        self.assertEqual(summarize_court(b,p,[3,8,18,29],[True]*7+[False],[True]*2)['status'],
                         'HOLD_NATIVE_TT_FIRST_READER_PROOF')
    def test_missing_cold_run_holds(self):
        b=baseline();p={o:probed(b,o) for o in (3,8,18,29)}
        p[3].pop()
        self.assertEqual(summarize_court(b,p,[3,8,18,29],[True]*8,[True]*2)['status'],
                         'HOLD_SINGLE_EVENT_COLD_REPLAY_MISSING')
    def test_cold_baseline_drift_holds(self):
        b=baseline();b[0]['move']='b3a4'
        p={o:probed(b,o) for o in (3,8,18,29)}
        self.assertEqual(summarize_court(b,p,[3,8,18,29],[True]*8,[True]*2)['status'],
                         'HOLD_ORIGINAL_GAME14_B_COLD_BASELINE_DRIFT')
    def test_selection_replay_drift_holds(self):
        b=baseline();b[1]['events'][2]['beta']=-3
        b[1]['events'][4]['beta']=1
        p={o:probed(b,o) for o in (3,8,18,29)}
        self.assertEqual(summarize_court(b,p,[3,8,18,29],[True]*8,[True]*2)['status'],
                         'HOLD_SOURCE_EVENT_SELECTION_COLD_DRIFT')
    def test_prefix_shortage_holds(self):
        with self.assertRaisesRegex(ValueError,'PREFIX_NOT_PRESENT'):
            selected_ordinals([ev(i) for i in range(1,32)])
    def test_wrong_number_predeclared_flip_events_holds(self):
        b=baseline()[0]['events']
        b[2]['beta']=-2
        with self.assertRaisesRegex(ValueError,'FROZEN_FOUR'):
            selected_ordinals(b)
if __name__=='__main__':
    unittest.main()
