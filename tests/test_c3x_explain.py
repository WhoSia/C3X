import json
from c3x_explain.core import analyze_pgn,HEURISTIC,CAUSAL

PGN='''[Event "Smoke"]
[Site "?"]
[Date "2026.09.30"]
[Round "1"]
[White "A"]
[Black "B"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *
'''

def test_no_engine_legal_spine():
    out=analyze_pgn(PGN)
    assert out["schema"]=="c3x-explanation-graph-v1"
    assert set(out["provenance_classes"])=={HEURISTIC,CAUSAL}
    for m in out["moments"]:
        assert m["firewall"]["pass"]

def test_certificate_provenance():
    import chess,chess.pgn,io
    g=chess.pgn.read_game(io.StringIO(PGN));b=g.board()
    cert={"schema":"c3x-causal-contrast-certificate-v1","fen":b.fen(),"certificate_id":"fixture",
          "pair_id":"e2e4::d2d4","bound":"LOWER","family":"OWN|DISPREFERRED_FROM_LOSS","collapse_to":"e2e4"}
    out=analyze_pgn(PGN,certificates=[cert])
    hit=[a for m in out["moments"] for a in m["atoms"] if a["provenance"]==CAUSAL]
    assert hit and hit[0]["claim"]["certificate_id"]=="fixture"
