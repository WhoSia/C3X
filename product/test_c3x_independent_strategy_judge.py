"""P4-B strict frozen source tree custody and independent judge tests."""
import unittest
from unittest.mock import Mock
import chess
import chess.engine

from c3x_recursive_strategy import produce
from c3x_independent_strategy_judge import reconstruct,judge,SCHEMA,DEPTHS
from test_c3x_recursive_strategy import DeterministicSource


class SimJudge:
    def __init__(self):self.calls=0
    def analyse(self,board,limit,game=None,info=None):
        self.calls+=1
        m=next(iter(board.legal_moves))
        return {"depth":limit.depth,"nodes":87,"pv":[m],
                "score":chess.engine.PovScore(chess.engine.Cp(18),board.turn)}


class P4BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=produce(chess.STARTING_FEN,"e2e4","d2d4",DeterministicSource(),k=2,depth=8)

    def test_exact_all_eight_legality(self):
        roots=reconstruct(self.source)
        self.assertEqual(len(roots),2)
        for r in roots:
            self.assertEqual(len(r["leaves"]),4)
            for leaf in r["leaves"]:
                self.assertEqual(len(leaf["path_uci"]),5)
                self.assertTrue(leaf["board"].is_valid())

    def test_independent_judge_16_distinct_searches(self):
        engine=SimJudge()
        result=judge(reconstruct(self.source),engine)
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["independent_search_count"],16)
        self.assertEqual(engine.calls,16)
        self.assertEqual(result["roots"][0]["depth_summaries"]["12"]["span_across_only_four_paths_cp"],0)
        self.assertFalse(result["full_opponent_universe_judged"])

    def test_tamper_one_source_move_rejected(self):
        import copy
        src=copy.deepcopy(self.source)
        src["roots"][0]["tree"][0]["own_best_move_or_null"]["action_uci"]="a1a1"
        with self.assertRaisesRegex(ValueError,"BRANCH_PATH_DISAGREEMENT"):
            reconstruct(src)

    def test_tamper_one_leaf_rejected(self):
        import copy
        src=copy.deepcopy(self.source)
        src["roots"][0]["leaf_paths"][0]["trace_uci"][1]="h1h1"
        with self.assertRaisesRegex(ValueError,"TREE_LEAF_FABRICATION"):
            reconstruct(src)

    def test_wrong_source_tree_status_rejected(self):
        import copy
        src=copy.deepcopy(self.source)
        src["not_source_chess_root_causal_intervention"]=False
        with self.assertRaisesRegex(ValueError,"SOURCE_FROZEN_CUSTODY"):
            reconstruct(src)

    def test_incomplete_actual_judge_fails_closed(self):
        class Broken:
            def analyse(self,board,limit,**kwargs):
                return {"depth":limit.depth,"nodes":0,"pv":[],
                        "score":chess.engine.PovScore(chess.engine.Cp(0),board.turn)}
        with self.assertRaisesRegex(ValueError,"INDEPENDENT_JUDGE_DEPTH"):
            judge(reconstruct(self.source),Broken())


if __name__=="__main__":
    unittest.main()
