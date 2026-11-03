import unittest
from c3x_029_p30_foil_semantics import evaluate_question, foil_switch


def world(replies, plan='Q1'):
    return {'root_id': 'g1:ply40', 'plan_id': plan, 'replies': {
        reply: {'legal_domain_verified': True, 'actions': [
            {'id': name, 'legal_verified': True, 'q': q, 'utility': val}
            for name, q, val in acts]}
        for reply, acts in replies.items()}}


def question(foil):
    return {'root_id': 'g1:ply40', 'target': 'a', 'foil': foil,
            'plan_id': 'Q1', 'declared_before_outcome': True}


class P30(unittest.TestCase):
    def setUp(self):
        self.facts = {
            'a': world({'aR1': [('a1', True, .1)], 'aR2': [('a2', True, .2)]}),
            'b': world({'bR1': [('b1', False, .0)], 'bR2': [('b2', False, -.1)]}),
            'c': world({'cR1': [('c1', True, .2)], 'cR2': [('c2', True, .2)]})}

    def test_discriminating_plan_can_separate_finite_value(self):
        self.assertEqual(evaluate_question(question('b'), self.facts)['status'],
                         'FINITE_PLAN_VALUE_SEPARATION_DECLARED_ONLY')

    def test_same_plan_is_non_discriminating_for_other_foil(self):
        self.assertEqual(evaluate_question(question('c'), self.facts)['status'],
                         'SHARED_PLAN_NONDISCRIMINATIVE')

    def test_switch_foil_changes_verdict(self):
        a = foil_switch(question('b'), question('c'), self.facts)
        self.assertNotEqual(a['first']['status'], a['second']['status'])

    def test_plan_distinct_but_target_worse(self):
        self.facts['b'] = world({'x': [('x1', False, 2.0)]})
        self.assertEqual(evaluate_question(question('b'), self.facts)['status'],
                         'PLAN_DISTINCT_BUT_NO_VALUE_SEPARATION')

    def test_plan_not_guaranteed_even_one_reply(self):
        self.facts['a']['replies']['aR2']['actions'][0]['q'] = False
        self.assertEqual(evaluate_question(question('b'), self.facts)['status'],
                         'NO_TARGET_PLAN_GUARANTEE')

    def test_no_private_outcome_selection(self):
        q = question('b'); q['declared_before_outcome'] = False
        self.assertEqual(evaluate_question(q, self.facts)['status'], 'HOLD_PLAN_NOT_PREDECLARED')

    def test_false_oracle_flag(self):
        self.facts['a']['replies']['aR1']['actions'][0]['legal_verified'] = False
        self.assertEqual(evaluate_question(question('b'), self.facts)['status'], 'HOLD_UNVERIFIED_ACTION')

    def test_no_cross_world_reply_alignment_assumed(self):
        out = evaluate_question(question('b'), self.facts)
        self.assertEqual(out['target']['reply_count'], 2)
        self.assertEqual(out['foil']['reply_count'], 2)

    def test_world_identity_mismatch(self):
        self.facts['b']['root_id'] = 'g2'
        self.assertEqual(evaluate_question(question('b'), self.facts)['status'], 'HOLD_WORLD_IDENTITY')

    def test_duplicate_action_fails(self):
        x = self.facts['a']['replies']['aR1']['actions'][0].copy()
        self.facts['a']['replies']['aR1']['actions'].append(x)
        self.assertEqual(evaluate_question(question('b'), self.facts)['status'], 'FAIL_DUPLICATE_ACTION')


if __name__ == '__main__':
    unittest.main()
