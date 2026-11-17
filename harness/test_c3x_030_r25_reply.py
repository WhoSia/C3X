"""Acceptance checks for the native witness and its board interpretation."""

from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from c3x_030_r25_reply_provenance import join_reply
from c3x_030_r25_reply_resource import inspect
from c3x_reply_causal_card import render

RECEIPTS = Path(__file__).resolve().parents[1] / "receipts"


def fixture_inputs():
    cases = json.loads((RECEIPTS / "C3X_030_R24_PV_EXTENSION_CASES_20261117.json").read_text())
    freeze = json.loads((RECEIPTS / "C3X_030_R24_EQUAL_NATIVE_FORK_FREEZE_20261117.json").read_text())
    case = next(row for row in cases["cases"] if row["id"] == freeze["case"])
    return case, freeze


class ReplyProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.lines = [
            "C3X_R25_REPLY_BEGIN call=23 attempt=27 iteration=12 admitted=1",
            "C3X_R25_EVALUATED call=23 move=d6h2 pv_update=1",
            "C3X_R25_REPLY_END call=23 reply=d6h2 value=-292",
            "C3X_R25_COPY producer=540 attempt=27 call=23 reply=d6h2 value=292",
        ]
        self.proof = {"best": {"move": "d1e2", "producer": "540"},
                      "best_source": {"attempt": "27", "value": "292"}}
        self.report = {"pv": ["d1e2", "d6h2"], "producer": "540"}

    def join(self, depth=12):
        with patch("c3x_030_r25_reply_provenance.observations", return_value=[self.report]):
            return join_reply([], self.proof, self.lines, depth)

    def test_copied_reply_transports_actual_signed_value(self):
        trace = self.join()["reply_trace"]
        self.assertEqual(trace["copy"]["call"], "23")
        self.assertEqual(trace["copy"]["value"], "292")
        self.assertEqual(trace["end"]["value"], "-292")

    def test_equal_native_value_cannot_substitute_a_different_reply(self):
        self.report["pv"][1] = "d6e7"
        with self.assertRaisesRegex(ValueError, "did not match"):
            self.join()

    def test_intervention_cannot_escape_target_iteration(self):
        with self.assertRaisesRegex(ValueError, "escaped"):
            self.join(18)


class ReplyExplanationTests(unittest.TestCase):
    def test_b4_survives_all_legal_black_replies_within_stated_horizon(self):
        case, freeze = fixture_inputs()
        facts = inspect(case["history"], freeze["reports"])
        self.assertTrue(facts["d6e7"]["b4_now"])
        self.assertFalse(facts["d6h2"]["b4_now"])
        evasion, = facts["d6h2"]["evasions"]
        self.assertEqual((evasion["san"], evasion["black_choices"], evasion["b4_available"]), ("Kh1", 37, 37))

    def test_card_keeps_gui_score_native_value_and_white_rook_distinct(self):
        case, freeze = fixture_inputs()
        result = json.loads((RECEIPTS / "C3X_030_R25_REPLY_REPLAY_20261117.json").read_text())
        card = render(case, freeze, result)
        self.assertIn("| 12 | Be7 | Bh2+ | +89cp | 294 |", card)
        self.assertIn("| 12 | 엔진 기본 순서 | Bh2+ | +89cp | 292 |", card)
        self.assertIn("Rfxc1", card)
        self.assertIn("Raxc1", card)

    def test_card_rejects_reply_not_copied_from_the_native_child(self):
        case, freeze = fixture_inputs()
        result = json.loads((RECEIPTS / "C3X_030_R25_REPLY_REPLAY_20261117.json").read_text())
        changed = deepcopy(result)
        changed["rows"]["18-sham"]["reply_trace"]["copy"]["reply"] = "d6h2"
        with self.assertRaisesRegex(ValueError, "unconnected"):
            render(case, freeze, changed)
