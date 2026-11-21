"""R38 original raw R37 archive audit and mutation-negative gates.

The real artifact comes from native R37 GitHub Actions run 44866204367,
not from a synthetic source. Synthetic edits test fail-closed behavior only.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest
from zipfile import ZipFile

from c3x_030_r38_reply_court import audit_zip, verify, SOURCE_MEMBER

ARCHIVE = Path(os.environ.get("C3X_R37_ZIP", "r37/C3X_030_R37_R30_017_EXHAUSTIVE_BOARD_ONLY_BERSERK.json"))
# The workflow downloads artifact contents, not the original artifact wrapper ZIP.
# Both direct JSON and original ZIP are supported by load_fixture().
def load_fixture():
    if ARCHIVE.suffix == ".zip":
        with ZipFile(ARCHIVE) as z:
            return json.loads(z.read(SOURCE_MEMBER))
    return json.loads(ARCHIVE.read_bytes())


class R38Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_fixture()
        cls.audited = verify(cls.data)

    def test_all_540_actual_searches_have_real_native_nodes(self):
        self.assertEqual(self.audited["originated_native_searches"], 540)
        self.assertEqual(self.audited["total_native_nodes"], 14596738)
        self.assertEqual(self.audited["independent_game_count"], 1)
        self.assertTrue(self.audited["same_45_opponent_replies_for_all_3_moves"])
        self.assertFalse(self.audited["strategic_winner_proved"])

    def test_actual_response_minima(self):
        minima = self.audited["response_minima"]
        self.assertEqual([minima[x]["10"]["score_cp_white"] for x in ("e2f3","e2d3","a2a3")], [74,62,53])
        self.assertEqual([minima[x]["12"]["score_cp_white"] for x in ("e2f3","e2d3","a2a3")], [72,60,49])

    def test_conditional_qf3_qd3_reversals_are_real(self):
        p = self.audited["conditional_first_move_pairwise_comparison"]
        self.assertEqual(p["10"]["e2f3_vs_e2d3"],
                         {"first_higher":33,"tie":1,"second_higher":11})
        self.assertEqual(p["12"]["e2f3_vs_e2d3"],
                         {"first_higher":34,"tie":1,"second_higher":10})
        self.assertFalse(self.audited["universal_Qf3_over_Qd3"])

    def test_cannot_discard_one_opponent_reply(self):
        z = deepcopy(self.data)
        del z["unfiltered_results"][0]["results"]["a7a5"]
        with self.assertRaises(ValueError):
            verify(z)

    def test_cannot_fabricate_cold_replay(self):
        z = deepcopy(self.data)
        z["unfiltered_results"][0]["results"]["a7a5"]["10"][1]["cp"] += 1
        with self.assertRaisesRegex(ValueError,"native replay changed"):
            verify(z)

    def test_illegal_pv_is_rejected(self):
        z = deepcopy(self.data)
        z["unfiltered_results"][0]["results"]["a7a5"]["10"][0]["pv"] = ["a2a3"]
        z["unfiltered_results"][0]["results"]["a7a5"]["10"][1]["pv"] = ["a2a3"]
        with self.assertRaisesRegex(ValueError,"illegal reported PV"):
            verify(z)

    def test_cannot_rewrite_original_board_fen(self):
        z = deepcopy(self.data)
        z["source_position_fen"] = z["source_position_fen"].replace("w - -", "b - -")
        with self.assertRaisesRegex(ValueError,"position mismatch"):
            verify(z)

    def test_cannot_promote_new_cold_repeats(self):
        z = deepcopy(self.data)
        z["search_parameters"]["repeats"] = 1
        with self.assertRaisesRegex(ValueError,"search schedule mismatch"):
            verify(z)

    def test_cannot_claim_complete_original_history(self):
        z = deepcopy(self.data)
        z["complete_original_PGN_history_used"] = True
        with self.assertRaisesRegex(ValueError,"history claim mismatch"):
            verify(z)

    def test_cannot_switch_referee_network(self):
        z = deepcopy(self.data)
        z["referee_network_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError,"referee source/network mismatch"):
            verify(z)

    def test_rank_must_recompute_from_raw_leaves(self):
        z = deepcopy(self.data)
        z["referee_summary"]["comparison"]["12"]["bounded_referee_ranking"].reverse()
        with self.assertRaisesRegex(ValueError,"derived candidate ranking mismatch"):
            verify(z)


if __name__ == "__main__":
    unittest.main()
