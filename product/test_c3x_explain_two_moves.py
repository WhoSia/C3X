"""C3X 0.30 P1 product explanation contracts. Fake engine only in unit tests."""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock

import chess
import chess.engine

from c3x_explain_two_moves import (
    board_from_history,verify_board_and_pair,measured_features,difference_facts,
    root_analysis,ranked_replies_and_own_responses,generate,make_markdown,
    ROOT_DEPTHS,REPLY_DEPTH,SCHEMA,evaluation_profile,configure_engine
)


class SimulatedEngine:
    def __init__(self):
        self.calls=0

    def analyse(self,board,limit,root_moves=None,multipv=None,game=None,info=None):
        self.calls+=1
        depth=limit.depth
        if root_moves is not None:
            move=root_moves[0]
            cp=50 if move.uci()=="e2e4" else 40
            return {"depth":depth,"nodes":177,"pv":[move],
                    "score":chess.engine.PovScore(chess.engine.Cp(cp),board.turn)}
        if multipv:
            moves=sorted(board.legal_moves,key=lambda m:m.uci())[:multipv]
            return [{"depth":depth,"nodes":222,
                     "pv":[move],
                     "score":chess.engine.PovScore(chess.engine.Cp(-15),board.turn)}
                     for move in moves]
        m=next(iter(board.legal_moves))
        return {"depth":depth,"nodes":333,"pv":[m],
                "score":chess.engine.PovScore(chess.engine.Cp(10),board.turn)}


class ProductContracts(unittest.TestCase):
    def setUp(self):
        self.board=chess.Board()

    def test_explicit_profile_no_silent_fallback(self):
        self.assertEqual(evaluation_profile()["mode"],"classical")
        for mode,net in (("wrong",None),("nnue",None),("classical","unused")):
            with self.assertRaises(ValueError): evaluation_profile(mode,net)
        with tempfile.TemporaryDirectory() as td:
            binary=Path(td)/"sf"
            binary.write_bytes(b"test binary")
            net=Path(td)/"net"
            net.write_bytes(b"wrong net")
            with self.assertRaisesRegex(ValueError,"NNUE_IDENTITY"):
                evaluation_profile("nnue",net)
            engine=Mock()
            engine.id={"name":"Stockfish 16"}
            engine.options={"Use NNUE":None,"Threads":None,"Hash":None}
            proof=configure_engine(engine,binary,evaluation_profile())
            engine.configure.assert_called_once_with({"Use NNUE":False,"Threads":1,"Hash":16})
            self.assertEqual(proof["evaluation_mode"],"classical")
            self.assertFalse(proof["source_build_verified_by_this_call"])
            engine.id={"name":"another engine"}
            with self.assertRaises(ValueError): configure_engine(engine,binary,evaluation_profile())

    def test_legal_pair(self):
        b,a,c=verify_board_and_pair(self.board.fen(),"e2e4","d2d4")
        self.assertEqual(a.uci(),"e2e4")
        self.assertEqual(c.uci(),"d2d4")

    def test_identical_or_illegal_refused(self):
        for a,b in (("e2e4","e2e4"),("e2e5","d2d4")):
            with self.assertRaisesRegex(ValueError,"TWO_DISTINCT"):
                verify_board_and_pair(self.board.fen(),a,b)

    def test_invalid_fen(self):
        with self.assertRaisesRegex(ValueError,"BAD_FEN"):
            verify_board_and_pair("not_a_fen","e2e4","d2d4")

    def test_check_capture_facts_true(self):
        b=chess.Board()
        for u in ("f2f3","e7e5","g2g4"):b.push_uci(u)
        x=measured_features(b,chess.Move.from_uci("d8h4"))
        self.assertTrue(x["gives_check"])
        self.assertTrue(x["opponent_in_check_after_move"])
        self.assertEqual(x["san"],"Qh4#")

        b=chess.Board()
        for u in ("e2e4","d7d5"):b.push_uci(u)
        self.assertTrue(measured_features(b,chess.Move.from_uci("e4d5"))["is_capture"])

    def test_shared_development_not_fabricated_difference(self):
        a=measured_features(self.board,chess.Move.from_uci("e2e4"))
        b=measured_features(self.board,chess.Move.from_uci("d2d4"))
        d=difference_facts(a,b)
        self.assertIn("is_capture",d["suppressed_shared_measured_facts"])
        self.assertTrue(d["shared_features_not_proposed_as_differentiating_reasons"])

    def test_engine_depth_gate(self):
        mock=Mock()
        mock.analyse.return_value={
            "depth":7,"nodes":100,"pv":[chess.Move.from_uci("e2e4")],
            "score":chess.engine.PovScore(chess.engine.Cp(1),chess.WHITE)}
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            root_analysis(self.board,chess.Move.from_uci("e2e4"),mock,8)

    def test_engine_forced_move_pv_gate(self):
        mock=Mock()
        mock.analyse.return_value={
            "depth":8,"nodes":100,"pv":[chess.Move.from_uci("d2d4")],
            "score":chess.engine.PovScore(chess.engine.Cp(1),chess.WHITE)}
        with self.assertRaisesRegex(ValueError,"FORCED_ROOT"):
            root_analysis(self.board,chess.Move.from_uci("e2e4"),mock,8)

    def test_actual_chess_branch_structure_mock_only(self):
        engine=SimulatedEngine()
        out=generate(self.board,"e2e4","d2d4",engine)
        self.assertEqual(out["schema"],SCHEMA)
        self.assertEqual(out["candidate_A_minus_B_cp_by_depth_or_null"],{"8":10,"10":10})
        self.assertEqual(len(out["root_candidates"]),2)
        self.assertEqual(engine.calls,12) # 4 root calls + 2*(1 MultiPV + 3 own replies)
        for row in out["root_candidates"]:
            probe=row["opponent_reply_probe"]
            self.assertEqual(probe["sampled_reply_count"],3)
            self.assertEqual(len(probe["reply_lines"]),3)
            self.assertGreater(probe["opponent_replies_total"],3)

    def test_markup_usable_and_limits_visible(self):
        result=generate(self.board,"e2e4","d2d4",SimulatedEngine())
        md=make_markdown(result)
        self.assertIn("# C3X — 두 후보 수의 차이는 무엇인가?",md)
        self.assertIn("최악값",md)
        self.assertIn("인과",md)
        self.assertIn("| 8 |",md)

    def test_history_replay_validation_and_fen_equivalence(self):
        b=board_from_history("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",["e2e4"])
        self.assertEqual(len(b.move_stack),1)
        self.assertEqual(b.peek().uci(),"e2e4")
        with self.assertRaisesRegex(ValueError,"HISTORY_FEN_MISMATCH"):
            board_from_history(chess.STARTING_FEN,["e2e4"])
        for bad in (["e2e5"],["0000"],["g1f3","f3g1"]):
            with self.assertRaisesRegex(ValueError,"ILLEGAL_HISTORY_MOVE"):
                board_from_history(chess.STARTING_FEN,bad)
        with self.assertRaisesRegex(ValueError,"BAD_HISTORY_LENGTH"):
            board_from_history(chess.STARTING_FEN,"e2e4")

    def test_preserve_repetition_history_and_input_board(self):
        board=chess.Board()
        history="g1f3 g8f6 f3g1 f6g8 g1f3 g8f6 f3g1".split()
        for move in history:
            board.push_uci(move)
        self.assertEqual(board.fen(),"rnbqkb1r/pppppppp/5n2/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 7 4")
        original_fen=board.fen()
        original_stack=tuple(board.move_stack)

        class HistoryEngine(SimulatedEngine):
            def __init__(self):
                super().__init__()
                self.seen=[]
            def analyse(self,board,limit,**kwargs):
                self.seen.append(tuple(board.move_stack))
                return super().analyse(board,limit,**kwargs)

        engine=HistoryEngine()
        result=generate(board,"f6g8","f6h5",engine)
        self.assertEqual(result["input_history_scope"],"PROVIDED_MOVE_STACK")
        self.assertEqual(result["input_history_ply_count"],7)
        self.assertTrue(result["root_candidates"][0]["facts"]["threefold_position_after_move"])
        self.assertFalse(result["root_candidates"][1]["facts"]["threefold_position_after_move"])
        self.assertTrue(all(stack[:7]==original_stack for stack in engine.seen))
        self.assertEqual(board.fen(),original_fen)
        self.assertEqual(tuple(board.move_stack),original_stack)

    def test_fen_only_history_scope_does_not_claim_repetition(self):
        board=chess.Board("rnbqkb1r/pppppppp/5n2/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 7 4")
        result=generate(board,"f6g8","f6h5",SimulatedEngine())
        self.assertEqual(result["input_history_scope"],"FEN_ONLY_OR_INITIAL_POSITION")
        self.assertFalse(result["root_candidates"][0]["facts"]["threefold_position_after_move"])
        self.assertIn("과거 반복에 의한 무승부 권리를 확정할 수 없다",make_markdown(result))

    def test_legacy_report_history_scope_remains_readable(self):
        result=generate(self.board,"e2e4","d2d4",SimulatedEngine())
        result.pop("input_history_scope")
        result.pop("input_history_ply_count")
        self.assertIn("과거 반복에 의한 무승부 권리를 확정할 수 없다",make_markdown(result))

    def test_terminal_rule_state_refused(self):
        b=chess.Board("8/8/8/8/8/8/4K3/7k w - - 0 1")
        with self.assertRaisesRegex(ValueError,"TERMINAL"):
            verify_board_and_pair(b.fen(),"e2e3","e2e4")


if __name__=="__main__":
    unittest.main()
