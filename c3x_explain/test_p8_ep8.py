#!/usr/bin/env python3
"""Proof-of-interface tests: P8 engine observations never become causal claims."""
import unittest
import chess
from c3x_explain.p8_ep8 import observation_index,observation_atoms_for_board
from c3x_explain.renderer import render_packet
from c3x_explain.core import analyze_pgn

ROOT="r5k1/6p1/p5qn/4p2p/2ppP3/3Q3P/1P1B1PP1/R5K1 w - - 0 25"

def packet():
    depths={}
    for depth in (8,12,16):
        branches={}
        for key in ("a","b"):
            branches[key]={
                "free_opponent_reply":{"depth_completed":depth,"score_white_cp":-30,"mate_white":None,"first_move":"c4d3"},
                "forced_convergence_reply_via_go_searchmoves":{"depth_completed":depth,"score_white_cp":10,"mate_white":None,"first_move":"c4b3"},
                "cold_equal_FEN_after_capture_depth_minus_one":{"depth_completed":depth-1,"score_white_cp":0,"mate_white":None,"first_move":"d3d5"}}
        depths[str(depth)]={"trials":[{"branches":branches},{"branches":branches}]}
    return {"schema":"c3x-013-p8-ep8-three-arm-conditional-reply-v2",
            "status":"DEVELOPMENTAL_REAL_ENGINE_COMPARISON_NOT_CAUSAL",
            "root_fen":ROOT,
            "source":{"rank":111,"ply":48,"game_url":"https://lichess.org/broadcast/tcec-s30-playoff-swiss-10-playoff-cat-2/round-1/kpZI9MVi/1oANqqKQ"},
            "engines":{name:{"binary_sha256":"a"*64,"depths":depths}
                       for name in ("Stockfish","Ethereal_classical")}}

class P8EP8BridgeTests(unittest.TestCase):
    def test_pair_observations_noncausal(self):
        b=chess.Board(ROOT)
        atoms=observation_atoms_for_board(observation_index([packet()]),b,"b2b3")
        self.assertEqual(len(atoms),6)
        self.assertTrue(all(a["provenance"]=="CONVENTIONAL_HEURISTIC_COMMENTARY" for a in atoms))
        self.assertTrue(all(a["claim"]["causal_certificate"] is None for a in atoms))
        self.assertTrue(all("causal" not in a["text"].lower() for a in atoms))
        for i,a in enumerate(atoms): a["atom_id"]=f"test:{i}"
        rendered=render_packet({"atoms":atoms})
        self.assertTrue(rendered["pass"],rendered["errors"])

    def test_reject_unauthorized_causal_schema(self):
        p=packet();p["status"]="C3X_CAUSAL_CONTRAST"
        with self.assertRaises(ValueError):
            observation_index([p])

    def test_abstain_on_repetition_instability(self):
        p=packet()
        p["engines"]["Stockfish"]["depths"]["8"]["trials"][1]["branches"]=dict(
            p["engines"]["Stockfish"]["depths"]["8"]["trials"][1]["branches"])
        a=dict(p["engines"]["Stockfish"]["depths"]["8"]["trials"][1]["branches"]["a"])
        a["free_opponent_reply"]=dict(a["free_opponent_reply"],score_white_cp=-31)
        p["engines"]["Stockfish"]["depths"]["8"]["trials"][1]["branches"]["a"]=a
        atoms=observation_atoms_for_board(observation_index([p]),chess.Board(ROOT),"b2b3")
        self.assertEqual(len(atoms),5)
        self.assertFalse(any(a["claim"]["engine"]=="Stockfish" and a["claim"]["depth"]==8 for a in atoms))

    def test_full_fen_required(self):
        b=chess.Board(ROOT); b.fullmove_number += 1
        self.assertFalse(observation_atoms_for_board(observation_index([packet()]),b,"b2b3"))

    def test_end_to_end_pgn_uses_noncausal_claims(self):
        pgn=f'[Event "C3X frozen EP8 adapter test"]\n[SetUp "1"]\n[FEN "{ROOT}"]\n\n25. b3 *\n'
        out=analyze_pgn(pgn,ep8_observation_packets=[packet()])
        self.assertEqual(out["moment_count"],1)
        self.assertEqual(out["ep8_observation_atom_count"],6)
        self.assertEqual(out["evaluation_packet"]["causal_atom_count"],0)
        self.assertEqual(out["renderer_benchmark"]["renderer_failed_moments"],0)
        self.assertEqual(out["verification_benchmark"]["failed_clean_packets"],0)

if __name__=="__main__":
    unittest.main()
