"""P6 grammar support lemmas: chess facts only, no engine causal claim."""
import json
import unittest
from pathlib import Path
import chess
from c3x_explain.concepts import snapshot

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"c3x"/"certificates"/"g95-p16-local-minimal-full-bridge.json"
def pawn_signature(b):
    return sorted((square,p.color) for square,p in b.piece_map().items() if p.piece_type==chess.PAWN)
def pawn_features(b,color):
    v=snapshot(b,color)
    return v["own_isolated_pawn_count"],v["own_passed_pawn_count"]

class GrammarSupport(unittest.TestCase):
    def test_p16_all_historical_edits_fix_pawn_positions(self):
        obj=json.loads(OLD.read_text())
        boards={k:chess.Board(v["fen"]) for k,v in obj["counterfactual_boards"].items()}
        self.assertTrue(all(b.is_valid() for b in boards.values()))
        base=boards["B0"]
        for name,b in boards.items():
            self.assertEqual(pawn_signature(base),pawn_signature(b),name)
            for color in (chess.WHITE,chess.BLACK):
                self.assertEqual(pawn_features(base,color),pawn_features(b,color),name)
    def test_noncapture_forward_pawn_move_keeps_isolation(self):
        b=chess.Board("4k3/8/8/2p5/3P4/8/8/4K3 w - - 0 1")
        self.assertTrue(b.is_valid())
        before=pawn_features(b,chess.WHITE)
        move=chess.Move.from_uci("d4d5")
        self.assertIn(move,b.legal_moves)
        b.push(move)
        after=pawn_features(b,chess.WHITE)
        self.assertEqual(before[0],after[0])
        self.assertNotEqual(before[1],after[1]) # Passed status can change by advancing
    def test_isolation_file_change_is_not_single_legal_pawn_move(self):
        b=chess.Board("4k3/8/8/8/P1P5/8/8/4K3 w - - 0 1")
        self.assertTrue(b.is_valid())
        self.assertEqual(pawn_features(b,chess.WHITE)[0],2)
        illegal=chess.Move.from_uci("c4b4")
        self.assertNotIn(illegal,b.legal_moves)
        modified=b.copy(stack=False)
        pawn=modified.remove_piece_at(chess.C4)
        modified.set_piece_at(chess.B4,pawn)
        self.assertTrue(modified.is_valid())
        self.assertEqual(pawn_features(modified,chess.WHITE)[0],0)
    def test_no_human_or_causal_authority_from_grammar(self):
        obj=json.loads(OLD.read_text())
        self.assertIsNone(obj["concept_label"])
        self.assertEqual(obj["replication_status"],"LOCAL_ONLY")
if __name__=="__main__":
    unittest.main()
