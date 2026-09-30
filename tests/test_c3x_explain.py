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

def test_rating_band_thresholds_and_atom_ids():
    out=analyze_pgn(PGN,rating_band="beginner")
    assert out["rating_band"]=="beginner"
    assert out["candidate_gap_threshold_cp"]==80
    assert all("atom_id" in a for m in out["moments"] for a in m["atoms"])

def test_concept_proxy_delta_is_descriptive():
    import chess
    from c3x_explain.concepts import candidate_delta
    b=chess.Board()
    d=candidate_delta(b,chess.Move.from_uci("e2e4"),chess.Move.from_uci("a2a3"))
    assert d["played_minus_alternative"]["own_center_occupancy_count"]==1

def test_renderer_contract_preserves_authority_boundary():
    import json
    x=json.load(open("c3x/ontology/explanation-renderer-contract-v1.json"))
    assert x["schema"]=="c3x-renderer-contract-v1"
    assert any("C3X_CAUSAL_CONTRAST" in z for z in x["required_behavior"])
    assert "objective-chess-truth wording from engine preference alone" in x["forbidden"]


def test_verified_tactical_adapter_multi_attack_and_check():
    import chess
    from c3x_explain.tactics import verified_move_evidence,tactical_contrast
    b=chess.Board("r3k3/8/8/1N6/8/8/8/4K3 w - - 0 1")
    m=chess.Move.from_uci("b5c7")
    ev=verified_move_evidence(b,m)
    kinds={z["kind"] for z in ev}
    assert "check" in kinds
    assert "multi_attack" in kinds
    ma=next(z for z in ev if z["kind"]=="multi_attack")
    assert {z["square"] for z in ma["attacked"]}>={"a8","e8"}

def test_i2_graph_routes_and_traceability_packet():
    pgn='''[Event "Mate"]
[Result "*"]

1. f3 e5 2. g4 Qh4# *
'''
    out=analyze_pgn(pgn,rating_band="advanced")
    audit=out["evaluation_packet"]
    assert audit["traceability_coverage"]==1
    assert audit["provenance_coverage"]==1
    assert audit["firewall_failed_moments"]==0
    assert any("tactics" in m["commentary_plan"]["categories"] for m in out["moments"])
    assert any(a["type"]=="tactical_fact" and a["claim"]["kind"]=="checkmate"
               for m in out["moments"] for a in m["atoms"])


def test_i3_retrieval_requires_source_license_and_never_promotes_authority():
    from c3x_explain.retrieval import retrieve,retrieval_atoms
    records=[
      {"source_id":"ok","source_uri":"https://example.invalid/annotated","license_state":"citation_only",
       "motif_tags":["checkmate"],"commentary_excerpt":"A bounded source note."},
      {"source_id":"bad","source_uri":"https://example.invalid/bad","license_state":"unknown",
       "motif_tags":["checkmate"],"commentary_excerpt":"x"}
    ]
    packet=retrieve(["checkmate"],records)
    assert [h["source_id"] for h in packet["hits"]]==["ok"]
    assert packet["rejected_count"]==1
    atoms=retrieval_atoms(packet)
    assert atoms and all(a["provenance"]==HEURISTIC for a in atoms)
    assert all(a["authority"]=="retrieved_commentary_reference" for a in atoms)

def test_i3_typed_graph_and_multi_axis_packet():
    pgn='''[Event "Mate"]
[Result "*"]

1. f3 e5 2. g4 Qh4# *
'''
    records=[{"source_id":"mate-note","source_uri":"https://example.invalid/mate","license_state":"citation_only",
              "motif_tags":["checkmate","tactical_fact"],"commentary_excerpt":"Bounded note."}]
    out=analyze_pgn(pgn,rating_band="beginner",retrieval_records=records)
    assert out["commentary_evaluation"]["schema"]=="c3x-commentary-evaluation-packet-v1"
    assert out["commentary_evaluation"]["human_utility"]["correctness"] is None
    assert all(m["typed_graph"]["schema"]=="c3x-typed-explanation-subgraph-v1" for m in out["moments"])
    assert any(a["type"]=="retrieval_reference" for m in out["moments"] for a in m["atoms"])
    assert any("retrieval_context" in m["commentary_plan"]["categories"] for m in out["moments"])
