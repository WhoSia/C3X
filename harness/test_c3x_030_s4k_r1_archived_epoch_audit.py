import unittest
from unittest.mock import patch
import hashlib,json
import c3x_030_s4k_r1_archived_epoch_audit as a
from c3x_030_s4k_epoch_court import parse

class ArchiveContract(unittest.TestCase):
    def test_random_bytes_cannot_self_certify(self):
        with self.assertRaisesRegex(ValueError,"ARCHIVED_RAW_SHA"):a.audit(b"{}")
    def test_actual_cutoffs_must_cover_bounded_receipts(self):
        t={"events":[{"ordinal":0,"state":[123,2,-20,40,1,0,1],"return_value":5}],
           "actual_source_cutoffs_at_this_return_site":0,"observed":1,
           "right_censored":False,"coverage_complete":True}
        with self.assertRaisesRegex(ValueError,"SOURCE_TOTAL_CONTRACT"):a.validate_trial(t,"123")
    def test_forged_censoring_flag_rejected(self):
        t={"events":[],"actual_source_cutoffs_at_this_return_site":9,
           "observed":0,"right_censored":False,"coverage_complete":True}
        with self.assertRaisesRegex(ValueError,"SOURCE_TOTAL_CONTRACT"):a.validate_trial(t,"123")
    def test_invalid_tt_key_rejected(self):
        t={"events":[{"ordinal":0,"state":[999,2,-20,40,1,0,1],"return_value":5}],
           "actual_source_cutoffs_at_this_return_site":1,"observed":1,
           "right_censored":False,"coverage_complete":True}
        with self.assertRaisesRegex(ValueError,"EVENT_IDENTITY"):a.validate_trial(t,"123")
    def test_wrong_alpha_beta_window_rejected(self):
        t={"events":[{"ordinal":0,"state":[123,2,50,40,1,0,1],"return_value":5}],
           "actual_source_cutoffs_at_this_return_site":1,"observed":1,
           "right_censored":False,"coverage_complete":True}
        with self.assertRaisesRegex(ValueError,"EVENT_IDENTITY"):a.validate_trial(t,"123")
    def test_valid_single_receipt(self):
        t={"events":[{"ordinal":0,"state":[123,2,-20,40,1,0,1],"return_value":5}],
           "actual_source_cutoffs_at_this_return_site":1,"observed":1,
           "right_censored":False,"coverage_complete":True}
        self.assertEqual(a.validate_trial(t,"123"),(1,1))
if __name__=="__main__":unittest.main()
