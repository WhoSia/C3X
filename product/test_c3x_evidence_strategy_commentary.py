"""P6 evidence-first Korean annotation is tied to exact source UCI tree and rules."""
import copy
import json
import unittest

import chess
from c3x_evidence_strategy_commentary import (
    annotate,markdown,replay_trace,SCHEMA
)
from c3x_recursive_strategy import produce
from test_c3x_recursive_strategy import DeterministicSource


class P6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(json.dumps(produce(
            chess.STARTING_FEN,"e2e4","d2d4",DeterministicSource(),k=2,depth=8)))

    def test_all_eight_paths_replayed(self):
        data=annotate(self.source)
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["fully_replay_verified_annotations"],8)
        for root in data["roots"]:
            self.assertEqual(len(root["atomic_conditional_annotations"]),4)
            for claim in root["atomic_conditional_annotations"]:
                self.assertEqual(len(claim["trace_uci"]),5)
                self.assertEqual(len(claim["trace_san"]),5)
                self.assertFalse(claim["independent_engine_quality_claimed"])
                self.assertTrue(claim["korean_explanation"].startswith("후보 "))

    def test_korean_markdown_claims_and_limits(self):
        result=annotate(self.source)
        msg=markdown(result)
        self.assertIn("실제 미래 대응",msg)
        self.assertIn("상대가",msg)
        self.assertIn("인과성",msg)
        self.assertIn("Shivkumar",msg)

    def test_reject_source_uci_tamper(self):
        x=copy.deepcopy(self.source)
        x["roots"][0]["tree"][0]["own_best_move_or_null"]["action_uci"]="a1a1"
        with self.assertRaisesRegex(ValueError,"ILLEGAL_SOURCE_MOVE|SOURCE_CONFLICT"):
            annotate(x)

    def test_reject_source_san_tamper(self):
        x=copy.deepcopy(self.source)
        x["roots"][0]["tree"][0]["opponent_move"]["action_san"]="NotReal"
        with self.assertRaisesRegex(ValueError,"FIRST_BRANCH_SOURCE_CONFLICT"):
            annotate(x)

    def test_reject_leaf_set_tamper(self):
        x=copy.deepcopy(self.source)
        x["roots"][1]["leaf_paths"][0]["trace_uci"]=["e2e5"]
        with self.assertRaisesRegex(ValueError,"SOURCE_LEAF_SET_MISMATCH"):
            annotate(x)

    def test_reject_fake_source_claim(self):
        x=copy.deepcopy(self.source)
        x["complete_opponent_reply_universe"]=True
        with self.assertRaisesRegex(ValueError,"SOURCE_TREE_EVIDENCE_IDENTITY"):
            annotate(x)

    def test_replay_illegal_move_strict(self):
        with self.assertRaisesRegex(ValueError,"ILLEGAL_SOURCE_MOVE"):
            replay_trace(chess.Board(),["e2e5"])

    def test_markdown_wrong_schema(self):
        with self.assertRaisesRegex(ValueError,"WRONG_ANNOTATION"):
            markdown({"schema":"fake"})


if __name__=="__main__":
    unittest.main()
