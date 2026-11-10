"""C3X P4 exact Cui opponent-top-k x two-layer tree, source-frozen boundaries."""
import unittest
import chess
import chess.engine
from c3x_recursive_strategy import (
    tree_for_root,produce,opponent_ranked,source_info,SCHEMA
)


class DeterministicSource:
    def __init__(self): self.calls=0
    def analyse(self,board,limit,multipv=None,game=None,info=None):
        self.calls+=1
        def datum(m):
            return {"pv":[m],"depth":limit.depth,"nodes":33,
                    "score":chess.engine.PovScore(chess.engine.Cp(12),board.turn)}
        if multipv is None:return datum(sorted(board.legal_moves,key=lambda m:m.uci())[0])
        return [datum(m) for m in sorted(board.legal_moves,
                                          key=lambda m:m.uci())[:multipv]]


class P4Tests(unittest.TestCase):
    def setUp(self):self.board=chess.Board()

    def test_two_layer_full_tree_k2(self):
        engine=DeterministicSource()
        x=tree_for_root(self.board,chess.Move.from_uci("e2e4"),engine,k=2,depth=8)
        self.assertEqual(x["leaf_count"],4)
        self.assertEqual(len(x["tree"]),2)
        self.assertTrue(all(len(r["next_opponent_replies"])==2 for r in x["tree"]))
        self.assertEqual(x["source_work_estimate"]["opponent_queries"],3)
        self.assertEqual(x["source_work_estimate"]["player_queries"],6)
        self.assertEqual(engine.calls,9)
        self.assertEqual(len({tuple(leaf["trace_uci"]) for leaf in x["leaf_paths"]}),4)
        self.assertTrue(all(len(leaf["trace_uci"])==5 for leaf in x["leaf_paths"]))

    def test_both_roots_and_fen_identity(self):
        eng=DeterministicSource()
        x=produce(self.board.fen(),"e2e4","d2d4",eng,k=2,depth=8)
        self.assertEqual(x["schema"],SCHEMA)
        self.assertEqual(x["total_leaf_paths"],8)
        self.assertEqual([r["root_uci"] for r in x["roots"]],["e2e4","d2d4"])
        self.assertTrue(x["same_engine_not_independent_judge"])
        self.assertFalse(x["complete_opponent_reply_universe"])

    def test_reject_k_out_of_range(self):
        with self.assertRaisesRegex(ValueError,"K_BOUNDS"):
            tree_for_root(self.board,chess.Move.from_uci("e2e4"),DeterministicSource(),k=4)

    def test_reject_bad_depth(self):
        with self.assertRaisesRegex(ValueError,"DEPTH_BOUNDS"):
            tree_for_root(self.board,chess.Move.from_uci("e2e4"),DeterministicSource(),depth=2)

    def test_reject_illegal_root(self):
        with self.assertRaisesRegex(ValueError,"ILLEGAL_ROOT"):
            tree_for_root(self.board,chess.Move.from_uci("e2e5"),DeterministicSource())

    def test_missing_uci_search_proof_is_failure(self):
        bad={"pv":[],"depth":8,"nodes":100,
             "score":chess.engine.PovScore(chess.engine.Cp(0),chess.WHITE)}
        with self.assertRaisesRegex(ValueError,"NATIVE_DEPTH"):
            source_info(bad,self.board,8)

    def test_two_player_source_not_independent(self):
        r=produce(self.board.fen(),"e2e4","d2d4",DeterministicSource())
        self.assertTrue(r["not_source_chess_root_causal_intervention"])
        self.assertTrue(r["not_original_cui_verbalizer_or_human_eval"])


if __name__=="__main__":
    unittest.main()
