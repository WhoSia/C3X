"""Guard against false writer lineage and inaccurate public lesson copy."""
import unittest

from c3x_030_r31_learner import NATIVE_PANEL, PUBLIC_PANEL, check_public
from c3x_030_r31_tt_pv import KEY, slots

IN = "31904,11,3,1,1,2154,1976,2020"
OUT = "31904,12,1,1,1,2154,1947,2020"


class WriterLineageTests(unittest.TestCase):
    def setUp(self):
        self.scout = {"key": KEY, "slot": "0", "tuple": IN}
        self.pv = {"key": KEY, "slot": "0", "tuple": OUT}
        self.write = f"C3X_R31_WRITE key={KEY} slot=0 before={IN} after={OUT}"

    def events(self, *writes):
        return slots(["C3X_R31_SCOUT anchor", *writes, "C3X_R31_PV anchor"], self.scout, self.pv)

    def test_target_slot_continuity_with_neighboring_write(self):
        neighbor = self.write.replace("slot=0", "slot=1").replace(KEY, "42")
        self.assertEqual([row["slot"] for row in self.events(neighbor, self.write)], ["1", "0"])

    def test_missing_and_unaccounted_write(self):
        with self.assertRaisesRegex(ValueError, "account for the consumer"):
            self.events()
        with self.assertRaisesRegex(ValueError, "Gap"):
            self.events(self.write.replace(IN, OUT))

    def test_tag_alias_and_slot_mismatch_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Different full key"):
            self.events(self.write.replace(KEY, str(int(KEY) + 65536)))
        self.pv["slot"] = "1"
        with self.assertRaisesRegex(ValueError, "same physical slot"):
            self.events(self.write)

    def test_move_only_write_followed_by_full_update(self):
        move_only = IN.replace("2154", "22")
        first = self.write.replace(OUT, move_only) + " replaced=0"
        second = self.write.replace(IN, move_only) + " replaced=1"
        self.assertEqual([row["replaced"] for row in self.events(first, second)], ["0", "1"])


class LearnerPanelTests(unittest.TestCase):
    def public_log(self):
        moves = ("a5a4", "a5a4", "f6d7", "f6d7", "f6d7", "f6d7", "f6d7")
        return [f"info depth {d} seldepth {d} multipv 1 score cp -200 nodes 200 nps 500 pv {m}"
                for d, m in enumerate(moves, 9)] + ["bestmove f6d7"]

    def test_matched_panels_and_frozen_public_story(self):
        self.assertEqual(len(NATIVE_PANEL.split()), len(PUBLIC_PANEL.split()))
        self.assertEqual(NATIVE_PANEL.count("."), PUBLIC_PANEL.count("."))
        check_public(self.public_log())

    def test_wrong_leader_and_wrong_bestmove_are_rejected(self):
        logs = self.public_log()
        with self.assertRaisesRegex(ValueError, "iteration history"):
            check_public(logs[1:])
        with self.assertRaisesRegex(ValueError, "final move"):
            check_public([*logs[:-1], "bestmove a5a4"])


if __name__ == "__main__":
    unittest.main()
