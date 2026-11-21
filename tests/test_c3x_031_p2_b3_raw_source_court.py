"""B3 original raw-court helper consistency checks (not substitute for real ZIP)."""
import unittest

from c3x_031_p2_b3_raw_source_court import (
    parse_event,raw_best,tied_ap,independent_scores,
    EXPECTED_B1_SHA,EXPECTED_B2_PRIVATE_SHA,EXPECTED_RAW_ZIP_SHA,
)


class B3ReceiptTests(unittest.TestCase):
    def test_fixed_original_source_hashes(self):
        self.assertEqual(len(EXPECTED_B1_SHA),64)
        self.assertEqual(len(EXPECTED_B2_PRIVATE_SHA),64)
        self.assertEqual(len(EXPECTED_RAW_ZIP_SHA),64)
        self.assertEqual(len({EXPECTED_B1_SHA,EXPECTED_B2_PRIVATE_SHA,
                              EXPECTED_RAW_ZIP_SHA}),3)

    def test_source_event_field_parser(self):
        x=parse_event("C3X_R33_OPEN event=12 skip_f=1 skip_n=0")
        self.assertEqual(x,{"event":"12","skip_f":"1","skip_n":"0"})

    def test_reject_duplicate_source_field(self):
        with self.assertRaises(ValueError):
            parse_event("C3X_R33_OPEN event=12 event=13")

    def test_refuse_missing_raw_best(self):
        with self.assertRaises(ValueError):
            raw_best(b"info depth 4 score cp 30 pv e2e4\n")

    def test_refuse_ambiguous_raw_best(self):
        with self.assertRaises(ValueError):
            raw_best(b"bestmove e2e4\nbestmove d2d4\n")

    def test_tied_average_precision_symmetric(self):
        self.assertEqual(tied_ap([0,1],[.2,.2]),.5)
        self.assertEqual(tied_ap([1,0],[.2,.2]),.5)
        self.assertEqual(tied_ap([0,0],[.2,.2]),None)

    def test_source_scores_use_original_frozen_predictions(self):
        rows=[{"y":0,"predictions":{"m0":.1,"m1":.2,"m2":.3}}
              for _ in range(125)]
        rows.append({"y":1,"predictions":{"m0":.1,"m1":.2,"m2":.3}})
        result=independent_scores(rows)
        self.assertEqual(result["m0"]["predicted_positive_at_0_5"],0)
        self.assertEqual(result["m2"]["true_positive_at_0_5"],0)
        self.assertEqual(result["m2"]["average_precision"],1/126)


if __name__=="__main__":
    unittest.main()
