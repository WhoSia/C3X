import unittest
from c3x_029_p31_native_trace_overlap_bounds import overlap_bounds, same_choice_trace_bounds, from_repo


class P31TraceBounds(unittest.TestCase):
    def test_frechet_lower_and_upper(self):
        self.assertEqual(overlap_bounds(12,10,10),{'lower':8,'upper':10})

    def test_disjoint_is_possible(self):
        self.assertEqual(overlap_bounds(12,2,3),{'lower':0,'upper':2})

    def test_bounds_never_invent_joint_counts(self):
        s={'unique_input_positions':12,
           'observed_summary':{'categorical_bestmove_changed':2,'PV_changed':10,
                               'nodes_changed':11,'score_or_bound_changed':8}}
        o=same_choice_trace_bounds(s)
        self.assertEqual(o['bestmove_unchanged'],10)
        self.assertEqual(o['pv_changed_given_same_bestmove_bounds'],{'lower':8,'upper':10})
        self.assertEqual(o['nodes_changed_given_same_bestmove_bounds'],{'lower':9,'upper':10})
        self.assertEqual(o['score_or_bound_changed_given_same_bestmove_bounds'],{'lower':6,'upper':8})

    def test_invalid_count_rejected(self):
        with self.assertRaises(ValueError):overlap_bounds(12,13,2)

    def test_bool_count_rejected(self):
        with self.assertRaises(ValueError):overlap_bounds(12,True,2)

    def test_original_real_archive_receipt(self):
        o=from_repo()
        self.assertEqual(o['cohort_size'],12)
        self.assertEqual(o['bestmove_changed'],2)
        self.assertEqual(o['pv_changed_given_same_bestmove_bounds']['lower'],8)


if __name__=="__main__":
    unittest.main()
