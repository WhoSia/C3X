"""P40/R3 audit of original frozen 8-event chess response-move contexts."""
import copy
import json
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from c3x_029_p40_r3_reply_context_audit import audit, EXPECTED_SHA
import hashlib


class OriginalReplyContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=os.environ.get("C3X_P40_R3_SOURCE")
        if not p:
            raise unittest.SkipTest("Exact original P39 archive member required")
        data=Path(p).read_bytes()
        if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA:
            raise ValueError("ORIGINAL_SOURCE_SHA")
        cls.record=json.loads(data)

    def test_original_complete_response_set(self):
        x=audit(self.record)
        self.assertEqual((x["events"],x["worlds"],x["reply_occurrences"]),(8,16,644))
        self.assertEqual(x["identical_uci_pairs"],313)
        self.assertEqual(x["different_proxy_pairs"],233)
        self.assertEqual([row["same_uci_different_b"] for row in x["cases"]],
                         [39,53,47,0,36,25,29,4])

    def test_case_omission_rejected(self):
        d=copy.deepcopy(self.record)
        d["game_events"]=7
        with self.assertRaises(AssertionError):audit(d)

    def test_duplicate_response_in_a_world_rejected(self):
        d=copy.deepcopy(self.record)
        d["cases"][0]["worlds"][0]["branches"].append(
            copy.deepcopy(d["cases"][0]["worlds"][0]["branches"][0]))
        with self.assertRaises(AssertionError):audit(d)


if __name__=="__main__":
    unittest.main()
