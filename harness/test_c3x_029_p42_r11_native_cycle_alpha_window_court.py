"""R11 test of actual original cycle-alpha window event consistency; synthetic."""
import unittest
from c3x_029_p42_r11_native_cycle_alpha_window_court import parse_events,summarize,compare_source_prefix,audit

def line(*,key=32,ply=3,depth=7,mod=0,old=-5,beta=0,neutral=False,root=11):
    val=0 if neutral else -1+(mod&2)
    return (f'c3x042_r11 event=cycle_alpha key64={key} ply={ply} depth={depth} '
            f'node_mod4={mod} old_alpha={old} beta={beta} candidate={val} '
            f'new_alpha={val} cutoff={int(val>=beta)} root_move={root}\n')

def cases():
    results={}
    for mode in ('0','1'):
        results[mode]={}
        for arm in ('A','B'):
            move='b3a4' if (arm=='A' or mode=='1') else 'f3f4'
            rows=parse_events(line(neutral=mode=='1'),mode=='1')
            results[mode][arm]=[{'move':move,'events':rows,'r10_cycle_calls':1} for _ in range(2)]
    return results

class R11WindowTests(unittest.TestCase):
    def test_original_negative_draw_no_cutoff(self):
        ev=parse_events(line(),False)
        self.assertEqual(len(ev),1)
        self.assertEqual(ev[0]['cutoff'],0)
    def test_node_bit_2_produces_positive_draw(self):
        ev=parse_events(line(mod=2),False)
        self.assertEqual(ev[0]['candidate'],1)
        self.assertEqual(ev[0]['cutoff'],1)
    def test_neutralized_draw_cutoff(self):
        ev=parse_events(line(neutral=True),True)
        self.assertEqual(ev[0]['candidate'],0)
        self.assertEqual(ev[0]['cutoff'],1)
    def test_unmatched_native_alpha_return_rejected(self):
        raw=line().replace('candidate=-1 new_alpha=-1','candidate=1 new_alpha=-1')
        with self.assertRaisesRegex(ValueError,'INCONSISTENT'):
            parse_events(raw,False)
    def test_wrong_native_cutoff_rejected(self):
        raw=line().replace('cutoff=0','cutoff=1')
        with self.assertRaisesRegex(ValueError,'INCONSISTENT'):
            parse_events(raw,False)
    def test_wrong_neutrality_rejected(self):
        with self.assertRaisesRegex(ValueError,'INCONSISTENT'):
            parse_events(line(neutral=True),False)
    def test_malformed_private_source_event_rejected(self):
        with self.assertRaisesRegex(ValueError,'MALFORMED'):
            parse_events('c3x042_r11 unknown=1',False)
    def test_source_event_prefix_identity_before_perturbation(self):
        old=parse_events(line(),False);new=parse_events(line(neutral=True),True)
        d=compare_source_prefix(old,new)
        self.assertEqual(d['same_pre_return_source_event_prefix'],1)
        self.assertEqual(d['within_prefix_draw_return_disagreements'],1)
        self.assertEqual(d['within_prefix_cutoff_decision_disagreements'],1)
    def test_same_key_different_beta_not_same_causal_node(self):
        old=parse_events(line(),False);new=parse_events(line(neutral=True,beta=1),True)
        d=compare_source_prefix(old,new)
        self.assertEqual(d['same_pre_return_source_event_prefix'],0)
    def test_native_summary_does_not_claim_chess_value(self):
        s=summarize(parse_events(line()+line(mod=2),False))
        self.assertEqual(s['cycle_immediate_cutoffs'],1)
        self.assertEqual(s['cycle_window_events'],2)
    def test_synthetic_pass_only_local_window_observation(self):
        x=audit(cases(),[True]*4)
        self.assertEqual(x['status'],'PASS_NATIVE_CYCLE_ALPHA_EVENT_AND_CUTOFF_OBSERVATION_ONLY')
        self.assertFalse(x['single_source_event_root_causation_certified'])
        self.assertFalse(x['native_chess_strategic_truth_certified'])
        self.assertNotIn('key64',str(x))
    def test_native_source_missing_count_holds(self):
        c=cases();c['1']['B'][0]['r10_cycle_calls']=3
        self.assertEqual(audit(c,[True]*4)['status'],'HOLD_R10_R11_ACTUAL_SOURCE_COUNT_MISMATCH')
    def test_historical_root_drift_holds(self):
        c=cases();c['0']['B'][0]['move']='b3a4'
        self.assertEqual(audit(c,[True]*4)['status'],'HOLD_PREDECLARED_R10_CHOICE_REPLAY_DRIFT')
    def test_reader_drift_holds(self):
        self.assertEqual(audit(cases(),[True,False,True,True])['status'],
                         'HOLD_TT_FIRST_PHYSICAL_READER_CUSTODY')
    def test_missing_cold_trial_holds(self):
        c=cases();c['1']['A'].pop()
        self.assertEqual(audit(c,[True]*4)['status'],'HOLD_COLD_REPLAY_MISSING')

if __name__=='__main__':
    unittest.main()
