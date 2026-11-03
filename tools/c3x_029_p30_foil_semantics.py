"""P30: foil-aware research claim audit over DECLARED candidate observations.

This module does not reconstruct chess states, verify external truth labels,
or establish Stockfish's decision-making causes.
"""
from math import isfinite


def evaluate_question(question, facts):
    """Evaluate a predeclared plan claim for 'why target rather than foil?'

    facts: for each candidate, independent per-candidate legal-reply records.
    Each reply includes 'legal_domain_verified', and actions with 'legal_verified',
    'q' (plan success) and 'utility'. Evaluates finite 2-ply values only.
    """
    needed = {'root_id', 'target', 'foil', 'plan_id', 'declared_before_outcome'}
    if not isinstance(question, dict) or not needed <= question.keys():
        return {'status': 'HOLD_QUESTION_SCHEMA'}
    if question['declared_before_outcome'] is not True:
        return {'status': 'HOLD_PLAN_NOT_PREDECLARED'}
    target, foil = question['target'], question['foil']
    if not all(isinstance(x, str) and x for x in (target, foil, question['root_id'], question['plan_id'])) or target == foil:
        return {'status': 'HOLD_INVALID_PAIR'}
    if not isinstance(facts, dict) or target not in facts or foil not in facts:
        return {'status': 'HOLD_MISSING_CANDIDATE'}
    evaluated = {}
    for candidate in (target, foil):
        world = facts[candidate]
        if not isinstance(world, dict) or world.get('root_id') != question['root_id'] or world.get('plan_id') != question['plan_id']:
            return {'status': 'HOLD_WORLD_IDENTITY', 'candidate': candidate}
        replies = world.get('replies')
        if not isinstance(replies, dict) or not replies:
            return {'status': 'HOLD_REPLY_UNIVERSE', 'candidate': candidate}
        ordinary, constrained = [], []
        failed = []
        for reply_id, record in replies.items():
            if not isinstance(reply_id, str) or not reply_id or not isinstance(record, dict) or record.get('legal_domain_verified') is not True:
                return {'status': 'HOLD_UNVERIFIED_REPLY', 'candidate': candidate}
            actions = record.get('actions')
            if not isinstance(actions, list) or not actions:
                return {'status': 'HOLD_ACTION_UNIVERSE', 'candidate': candidate}
            action_ids = set()
            for action in actions:
                if not isinstance(action, dict) or action.get('legal_verified') is not True or type(action.get('q')) is not bool:
                    return {'status': 'HOLD_UNVERIFIED_ACTION', 'candidate': candidate}
                u = action.get('utility')
                if type(u) not in (int, float) or not isfinite(u) or not isinstance(action.get('id'), str) or not action['id']:
                    return {'status': 'HOLD_UTILITY_OR_ACTION_ID', 'candidate': candidate}
                if action['id'] in action_ids:
                    return {'status': 'FAIL_DUPLICATE_ACTION', 'candidate': candidate}
                action_ids.add(action['id'])
            ordinary.append(max(a['utility'] for a in actions))
            supported = [a['utility'] for a in actions if a['q']]
            if supported:
                constrained.append(max(supported))
            else:
                failed.append(reply_id)
        evaluated[candidate] = {'value': min(ordinary),
                                'plan_guaranteed': not failed,
                                'plan_value': min(constrained) if not failed else None,
                                'missing_plan_replies': sorted(failed),
                                'reply_count': len(replies)}
    a, b = evaluated[target], evaluated[foil]
    if not a['plan_guaranteed']:
        verdict = 'NO_TARGET_PLAN_GUARANTEE'
    elif b['plan_guaranteed']:
        verdict = 'SHARED_PLAN_NONDISCRIMINATIVE'
    elif a['plan_value'] > b['value']:
        verdict = 'FINITE_PLAN_VALUE_SEPARATION_DECLARED_ONLY'
    else:
        verdict = 'PLAN_DISTINCT_BUT_NO_VALUE_SEPARATION'
    return {'status': verdict, 'target': a, 'foil': b,
            'finite_value_delta': a['value'] - b['value'],
            'warning': 'Declared world universes/utility only; source, legality, outcome chronology NOT independently verified'}


def foil_switch(question_a, question_b, facts):
    """Observe whether the SAME frozen plan is discriminative across different foils."""
    if question_a.get('root_id') != question_b.get('root_id') or question_a.get('target') != question_b.get('target') or question_a.get('plan_id') != question_b.get('plan_id'):
        return {'status': 'HOLD_NONMATCHED_QUESTIONS'}
    if question_a.get('foil') == question_b.get('foil'):
        return {'status': 'HOLD_SAME_FOIL'}
    return {'status': 'DECLARED_FOIL_SWITCH_ONLY',
            'first': evaluate_question(question_a, facts),
            'second': evaluate_question(question_b, facts)}
