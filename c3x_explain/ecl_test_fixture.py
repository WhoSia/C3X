"""A minimal synthetic chess position used ONLY for regression fixture tests.
Never treated as native-source real chess validation or scientific evidence.
"""
import chess

def base():
    b=chess.Board()
    return {"ply":1,"played_uci":"e2e4","fen":b.fen(),
       "firewall":{"pass":True},"realization_verification":{"pass":True},
       "candidates":[
          {"rank":1,"uci":"e2e4","san":"e4","depth":12,"score_cp":52,
           "score_bound":False,"pv_uci":["e2e4","e7e5","g1f3"]},
          {"rank":2,"uci":"d2d4","san":"d4","depth":12,"score_cp":21,
           "score_bound":False,"pv_uci":["d2d4","d7d5","c2c4"]}],
       "atoms":[{"atom_id":"p1:contrast","type":"candidate_contrast",
                 "provenance":"CONVENTIONAL_HEURISTIC_COMMENTARY",
                 "claim":{"top_uci":"e2e4"}}],
       "typed_graph":{"nodes":[]}}
