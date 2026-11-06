"""R13 native source↔root boundary chronology contracts (synthetic only)."""
import unittest
from c3x_029_p42_r13_native_single_cycle_to_root_boundary_court import (
    physical_trace,compare_temporal_source_root,TARGET)
from c3x_029_p42_r11_native_cycle_alpha_window_court import RX

def make(ordinal=0,leader=100,score=10,target_before_root=True):
    # First 33 original source-event calls; #30..33 would individually flip
    # a local cutoff if replaced by zero. The only changed chosen event is #33.
    cycles=[]
    for i in range(1,34):
        mod=0
        old=-4
        beta=0 if i in (30,31,32,33) else -2
        val=0 if i==ordinal else -1
        cycles.append({'key':1000+i,'ply':4,'depth':3,'mod4':mod,
                       'old_alpha':old,'beta':beta,'candidate':val,
                       'cutoff':int(val>=beta),'root_move':22})
    root_before={'depth':1,'leader':100,'score':0,'average':0}
    root_after={'depth':2,'leader':leader,'score':score,'average':9}
    if not target_before_root:
        root_before=dict(root_before,leader=leader,score=score)
    lines=[]
    for d in [root_before]:
        lines.append(f"event=ROOT_BOUNDARY depth={d['depth']} leader={d['leader']} score={d['score']} average={d['average']}")
    for c in cycles:
        lines.append("c3x042_r11 event=cycle_alpha key64={key} ply={ply} depth={depth} node_mod4={mod4} old_alpha={old_alpha} beta={beta} candidate={candidate} new_alpha={candidate} cutoff={cutoff} root_move={root_move}".format(**c))
    lines.append(f"event=ROOT_BOUNDARY depth=2 leader={leader} score={score} average=9")
    return {'events':cycles,'root_boundaries':[root_before,root_after],
            'first_trace':lines,'target_source_line_index':33}

class R13RootBridgeTests(unittest.TestCase):
    def test_true_source_event_precedes_root_boundary_changes(self):
        orig=make();tr=make(ordinal=TARGET,leader=200,score=15)
        r=compare_temporal_source_root(orig,tr)
        self.assertEqual(r['status'],'PASS_SINGLE_EVENT33_PRECEDES_FIRST_SOURCE_ROOT_BOUNDARY_DIVERGENCE_ONLY')
        self.assertEqual(r['first_changed_depth'],2)
        self.assertEqual(r['first_changed_leader_depth'],2)
        self.assertFalse(r['full_root_candidate_value_mediation_certified'])
    def test_identical_source_root_boundaries_fail_closed(self):
        orig=make();tr=make(ordinal=TARGET)
        self.assertEqual(compare_temporal_source_root(orig,tr)['status'],
                         'HOLD_ROOT_BOUNDARY_NO_DIVERGENCE_DESPITE_MOVE_CHANGE')
    def test_source_target_key_drifts_before_perturbation(self):
        o=make();t=make(ordinal=TARGET,leader=200)
        t['events'][10]['key']=8877
        self.assertEqual(compare_temporal_source_root(o,t)['status'],
                         'HOLD_UNMATCHED_EXACT_SINGLE_EVENT_SOURCE')
    def test_native_depth_support_mismatch_holds(self):
        o=make();t=make(ordinal=TARGET,leader=200)
        t['root_boundaries'].pop()
        self.assertEqual(compare_temporal_source_root(o,t)['status'],
                         'HOLD_ROOT_BOUNDARY_DEPTH_SUPPORT_CHANGED')
    def test_native_depth_number_mismatch_holds(self):
        o=make();t=make(ordinal=TARGET,leader=200)
        t['root_boundaries'][1]['depth']=3
        self.assertEqual(compare_temporal_source_root(o,t)['status'],
                         'HOLD_ROOT_ITERATION_DEPTH_DRIFT')
    def test_after_source_first_changed_root_cannot_precede_source(self):
        o=make();t=make(ordinal=TARGET,leader=200)
        t['target_source_line_index']=99999
        self.assertEqual(compare_temporal_source_root(o,t)['status'],
                         'HOLD_ROOT_BOUNDARY_DIVERGED_BEFORE_SOURCE_EVENT')
    def test_leader_constant_score_changed_preserves_distinction(self):
        o=make();t=make(ordinal=TARGET,leader=100,score=11)
        r=compare_temporal_source_root(o,t)
        self.assertEqual(r['first_changed_leader_depth'],None)
        self.assertEqual(r['first_changed_boundary']['changed_fields'],['score'])
    def test_native_root_boundary_logs_do_not_release_keys(self):
        r=compare_temporal_source_root(make(),make(ordinal=TARGET,leader=200))
        self.assertNotIn('key64',str(r))
        self.assertNotIn('1033',str(r))
    def test_two_native_source_logs_required(self):
        line='event=ROOT_BOUNDARY depth=1 leader=100 score=0 average=0'
        with self.assertRaisesRegex(ValueError,'NOT_IDENTICAL|ODD_NUMBER'):
            physical_trace(line+'\n'+line+'\n'+line,0)
    def test_actual_native_source_event_regex_accepts_source_row(self):
        row='c3x042_r11 event=cycle_alpha key64=7 ply=3 depth=6 node_mod4=0 old_alpha=-3 beta=0 candidate=-1 new_alpha=-1 cutoff=0 root_move=5'
        self.assertIsNotNone(RX.fullmatch(row))
    def test_r13_same_native_root_boundary_line_match_requires_exact_depth(self):
        o=make();t=make(ordinal=TARGET,leader=200)
        o['first_trace'].append('event=ROOT_BOUNDARY depth=10 leader=999 score=10 average=10')
        t['first_trace'].append('event=ROOT_BOUNDARY depth=10 leader=999 score=10 average=10')
        r=compare_temporal_source_root(o,t)
        self.assertEqual(r['first_changed_depth'],2)
if __name__=='__main__':
    unittest.main()
