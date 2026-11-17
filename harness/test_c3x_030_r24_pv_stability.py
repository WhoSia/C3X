import unittest

from c3x_030_r24_pv_stability import compare


def row(pv, native=33, eligible=True, cp=10):
    return {"pv": pv.split(), "move": pv.split()[0], "cp": cp,
            "native": native, "eligible": eligible}


class PrincipalVariationTest(unittest.TestCase):
    def test_extension_and_actual_divergence_are_distinct(self):
        left = row("e2e4 b8c6")
        self.assertEqual(compare(left, row("e2e4 b8c6 g1f3"), [])["kind"], "prefix")
        self.assertEqual(compare(left, row("e2e4 g8f6"), [])["first_divergence_ply"], 2)

    def test_same_integer_display_is_not_same_native_score(self):
        result = compare(row("e2e4 b8c6", 33), row("e2e4 g8f6", 34), [])
        self.assertFalse(result["native_equal"])
        self.assertEqual(result["chooser"], "black")
        self.assertIsNone(compare(row("e2e4 b8c6", eligible=False), row("e2e4 g8f6"), []))

    def test_reports_rejoin_at_the_same_full_fen_after_distinct_moves(self):
        left = row("e2e4 b8c6 g1f3 g8f6")
        right = row("e2e4 g8f6 g1f3 b8c6")
        result = compare(left, right, [])
        self.assertEqual(result["same_ply_full_fen"], [4])
        self.assertEqual(result["kind"], "divergent")


if __name__ == "__main__":
    unittest.main()
