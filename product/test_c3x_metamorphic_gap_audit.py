"""P5 Martin replication, mirror-covariant chess rules and honest search claims."""
import unittest
import chess
import chess.engine

from c3x_metamorphic_gap_audit import (
    mirror_move,mirrored_pair,relative_distance_abs,case_analysis,
    predeclared_cases,run,SCHEMA
)


class DeterministicCovariantEngine:
    """Synthetic mirror-consistent score; never presented as empirical engine."""
    def __init__(self):
        self.calls=0
    def analyse(self,board,limit,root_moves=None,game=None,info=None):
        self.calls+=1
        mv=root_moves[0]
        # Symmetry-invariant score for all tests; no fabricated root variation.
        return {"depth":limit.depth,"nodes":250,"pv":[mv],
                "score":chess.engine.PovScore(chess.engine.Cp(33),board.turn)}


class FiniteDepthBiasedEngine(DeterministicCovariantEngine):
    def analyse(self,board,limit,root_moves=None,game=None,info=None):
        result=super().analyse(board,limit,root_moves,game,info)
        score=25 if board.turn==chess.WHITE else -17
        if root_moves[0].from_square==chess.E2:score+=5
        result["score"]=chess.engine.PovScore(chess.engine.Cp(score),board.turn)
        return result


class P5Contracts(unittest.TestCase):
    def test_mirror_involution_normal_and_castling(self):
        b=chess.Board()
        self.assertEqual(b.mirror().mirror().fen(),b.fen())
        self.assertEqual(mirror_move(mirror_move(chess.Move.from_uci("e2e4"))).uci(),"e2e4")
        c,a,d=mirrored_pair(b,chess.Move.from_uci("e2e4"),
                          chess.Move.from_uci("d2d4"))
        self.assertEqual(a.uci(),"e7e5")
        self.assertEqual(d.uci(),"d7d5")
        self.assertEqual(c.turn,chess.BLACK)

    def test_mirror_promotion_retains_piece(self):
        m=chess.Move.from_uci("a7a8q")
        self.assertEqual(mirror_move(m).uci(),"a2a1q")

    def test_predeclared_two_real_legal_cases(self):
        data=predeclared_cases()
        self.assertEqual(len(data),2)
        for label,fen,a,b in data:
            board=chess.Board(fen)
            self.assertTrue(board.is_valid())
            self.assertIn(chess.Move.from_uci(a),board.legal_moves)
            self.assertIn(chess.Move.from_uci(b),board.legal_moves)
            mirrored_pair(board,chess.Move.from_uci(a),chess.Move.from_uci(b))

    def test_distances_deny_zero_division(self):
        self.assertEqual(relative_distance_abs(0,0),0.0)
        self.assertEqual(relative_distance_abs(15,-15),1.0)
        self.assertEqual(relative_distance_abs(-30,-30),0.0)
        self.assertIsNone(relative_distance_abs(None,1))

    def test_24_query_full_contract_with_fake(self):
        e=DeterministicCovariantEngine()
        d=run(e)
        self.assertEqual(d["schema"],SCHEMA)
        self.assertEqual(e.calls,24)
        self.assertEqual(d["number_of_real_engine_forced_root_queries"],24)
        self.assertTrue(d["no_bug_claim_from_any_finite_depth_disagreement"])
        for case in d["cases"]:
            for depth in ("8","10","12"):
                record=case["per_depth"][depth]
                self.assertEqual(record["mirrored_gap_minus_original_gap_cp_or_null"],0)
                self.assertFalse(record["strict_opposite_sign_or_null"])

    def test_violations_descriptive_not_assertion_engine_bug(self):
        d=case_analysis(chess.STARTING_FEN,"e2e4","d2d4",
                        FiniteDepthBiasedEngine(),"unit")
        self.assertEqual(d["case_id"],"unit")
        self.assertTrue(d["per_depth"]["8"]["finite_search_not_proof_of_engine_bug"])
        self.assertIsInstance(d["per_depth"]["8"]["absolute_gap_disagreement_cp_or_null"],int)

    def test_illegal_source_forced_move_rejected(self):
        class Broken:
            def analyse(self,board,limit,root_moves=None,**kwargs):
                return {"depth":limit.depth,"nodes":100,
                        "pv":[chess.Move.from_uci("h1h8")],
                        "score":chess.engine.PovScore(chess.engine.Cp(3),board.turn)}
        with self.assertRaisesRegex(ValueError,"FORCED_ROOT"):
            case_analysis(chess.STARTING_FEN,"e2e4","d2d4",Broken(),"unit")


if __name__=="__main__":
    unittest.main()
