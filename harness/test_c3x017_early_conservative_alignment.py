import unittest
from c3x017_early_conservative_alignment import audit_world, check_events

def event(seq, kind="candidate", depth=1, move=100, child_return=4):
    return dict(seq=seq, kind=kind, depth=depth, move=move,
                child_return=child_return, before=-1, after=4,
                alpha=-20, beta=20)

def cell(events):
    return {"UCI": {"bestmove": "e2e4", "score_kind": "cp",
                    "score_value": 4, "score_flag": "exact_reported",
                    "nodes": 10, "pv": ["e2e4"]},
            "passive_root_events": events, "trace_censored": False}

def world(o, f, z=None):
    return {"id": 1, "cells": {"O": cell(o), "F": cell(f),
                               "Z": cell(z if z is not None else o)}}

class ConservativeEarlyAuditTests(unittest.TestCase):
    def test_candidate_reordered_but_same_value_not_false_divergence(self):
        r = audit_world(world([event(1, move=1), event(2, move=2)],
                              [event(1, move=2), event(2, move=1)]))
        self.assertEqual(r["candidate_differences"], [])
        self.assertEqual(r["ambiguous_groups"], [])

    def test_same_candidate_changed_child(self):
        r = audit_world(world([event(1)], [event(1, child_return=9)]))
        self.assertEqual(r["candidate_differences"][0]["fields"], ["child_return"])

    def test_repeated_candidate_needs_trial_identity(self):
        r = audit_world(world([event(1), event(2)],
                              [event(1), event(2)]))
        self.assertEqual(r["ambiguous_groups"][0]["reason"],
                         "REPEATED_VISITS_NEED_TRIAL_ID")

    def test_asymmetric_visits_are_ambiguous(self):
        r = audit_world(world([event(1), event(2)],
                              [event(1)]))
        self.assertEqual(r["ambiguous_groups"][0]["reason"],
                         "CANDIDATE_VISIT_MULTIPLICITY")

    def test_censored_is_not_complete(self):
        w = world([event(1)], [event(1)])
        w["cells"]["F"]["trace_censored"] = True
        self.assertEqual(audit_world(w)["status"], "TRACE_CENSORED")

    def test_gapped_sequence_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "NONCONTIGUOUS_SEQUENCE"):
            check_events([event(2)], False)

    def test_negative_control_drift_fails(self):
        w = world([event(1)], [event(1)])
        w["cells"]["Z"]["UCI"]["score_value"] = 3
        with self.assertRaisesRegex(ValueError, "NEGATIVE_CONTROL_OUTPUT_DRIFT"):
            audit_world(w)

if __name__ == "__main__":
    unittest.main()
