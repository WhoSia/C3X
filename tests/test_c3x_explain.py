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

def test_i4_certificate_is_first_class_graph_authority_object():
    import chess,chess.pgn,io
    g=chess.pgn.read_game(io.StringIO(PGN));b=g.board()
    cert={"schema":"c3x-causal-contrast-certificate-v1","fen":b.fen(),"certificate_id":"first-class-fixture",
          "pair_id":"e2e4::d2d4","bound":"LOWER","family":"OWN|DISPREFERRED_FROM_LOSS","collapse_to":"e2e4",
          "authority_ceiling":["engine preference only"]}
    out=analyze_pgn(PGN,certificates=[cert])
    m=next(m for m in out["moments"] if any(a["type"]=="causal_contrast" for a in m["atoms"]))
    nodes=m["typed_graph"]["nodes"];edges=m["typed_graph"]["edges"]
    assert any(n["node_type"]=="causal_certificate" and n["payload"]["certificate_id"]=="first-class-fixture" for n in nodes)
    assert any(e["relation"]=="authorizes_causal_scope" for e in edges)

def test_i4_verified_line_evidence_replays_legally():
    import chess
    from c3x_explain.planning import verified_line_evidence
    b=chess.Board()
    e=verified_line_evidence(b,{"uci":"e2e4","san":"e4","pv_uci":["e2e4","e7e5","g1f3"]})
    assert e and e["all_moves_legally_replayed"]
    assert [s["uci"] for s in e["steps"]]==["e2e4","e7e5","g1f3"]
    assert e["semantic_scope"]=="bounded_pv_line_fact_only"

def test_i4_retrieval_corpus_governance_is_explicit():
    from c3x_explain.retrieval import audit_retrieval_corpus
    rows=[
      {"source_id":"ok","source_uri":"https://example.invalid/a","license_state":"citation_only",
       "motif_tags":["mate"],"commentary_excerpt":"note"},
      {"source_id":"bad","source_uri":"https://example.invalid/b","license_state":"unknown",
       "motif_tags":["mate"],"commentary_excerpt":"bad"}
    ]
    a=audit_retrieval_corpus(rows)
    assert not a["pass"] and a["admissible_count"]==1 and a["rejected_count"]==1

def test_i5_renderer_claims_are_atom_traceable_and_atomic_factuality_passes():
    pgn='''[Event "Mate"]
[Result "*"]

1. f3 e5 2. g4 Qh4# *
'''
    out=analyze_pgn(pgn)
    bench=out["renderer_benchmark"]
    assert bench["schema"]=="c3x-atomic-renderer-benchmark-v1"
    assert bench["atomic_factuality_rate"]==1.0
    assert bench["renderer_failed_moments"]==0
    for m in out["moments"]:
        atom_ids={a["atom_id"] for a in m["atoms"]}
        for c in m["render_packet"]["claims"]:
            assert c["factuality"]["pass"]
            assert set(c["atom_ids"])<=atom_ids
        assert m["commentary"]==m["render_packet"]["surface_text"]

def test_i6_constrained_realization_is_sentence_atom_claim_traceable():
    out=analyze_pgn(PGN,rating_band="intermediate")
    assert out["realization_benchmark"]["schema"]=="c3x-constrained-realization-benchmark-v1"
    assert out["realization_benchmark"]["failed_packets"]==0
    assert out["realization_benchmark"]["free_form_llm_used"] is False
    for m in out["moments"]:
        rp=m["realization_packet"]
        assert rp["pass"]
        claim_ids={c["claim_id"] for c in m["render_packet"]["claims"] if c["factuality"]["pass"]}
        atom_ids={a["atom_id"] for a in m["atoms"]}
        for sent in rp["sentences"]:
            assert set(sent["claim_ids"])<=claim_ids
            assert set(sent["atom_ids"])<=atom_ids
            assert sent["realization_mode"]=="verbatim_bounded_claim"
        assert m["commentary"]==rp["text"]

def test_i7_adversarial_realization_firewall_rejects_all_frozen_attacks():
    pgn='''[Event "Mate"]
[Result "*"]

1. f3 e5 2. g4 Qh4# *
'''
    out=analyze_pgn(pgn)
    bench=out["verification_benchmark"]
    assert bench["schema"]=="c3x-adversarial-verification-benchmark-v1"
    assert bench["clean_pass_rate"]==1.0
    assert bench["adversarial_case_count"]>=4
    assert bench["adversarial_rejection_rate"]==1.0
    for m in out["moments"]:
        assert m["realization_verification"]["pass"]
        suite=m["adversarial_realization_suite"]
        if suite["cases"]:
            assert suite["pass"]
            assert {c["name"] for c in suite["cases"]}=={
                "drop_atom_trace","authority_upgrade","unsupported_causal_wording","surface_tamper"
            }
            assert all(c["rejected"] for c in suite["cases"])

def test_i8_preseal_keeps_human_outcomes_closed():
    from c3x_explain.human_utility import i8_preseal,aggregate_human_outcomes
    p=i8_preseal()
    assert p["schema"]=="c3x-human-utility-preseal-v2"
    assert p["status"]=="HUMAN_OUTCOME_UNOPENED"
    assert "subsequent_move_understanding" in p["endpoints"]
    assert p["trial_families"]["move_understanding"]["arms"]==["c3x","baseline","no_commentary"]
    empty=aggregate_human_outcomes([],[])
    assert empty["human_outcome_opened"] is False
    assert empty["verdict"]=="NO_HUMAN_UTILITY_CLAIM"

def test_i8_preference_blinding_is_deterministic_and_key_separated():
    from c3x_explain.human_utility import build_preference_trial
    args=dict(
        trial_id="p-001",rating_band="advanced",
        position_fen="8/8/8/8/8/8/4K3/7k w - - 0 1",
        c3x_text="C3X explanation.",baseline_text="Baseline explanation.",
        played_move="Ke3",seed="sealed-study-seed",
        reference_validity={"c3x":True,"baseline":False},
    )
    a=build_preference_trial(**args); b=build_preference_trial(**args)
    assert a==b
    assert "arm_identity" not in a["participant_packet"]
    assert set(a["participant_packet"]["commentary"])=={"A","B"}
    assert "subsequent_move_understanding" not in a["participant_packet"]["questions"]
    assert set(a["adjudication_key"]["arm_identity"].values())=={"c3x","baseline"}

def test_i8_understanding_exposes_exactly_one_randomized_arm():
    from c3x_explain.human_utility import build_understanding_trial
    kwargs=dict(
        trial_id="u-001",participant_id="participant-001",rating_band="beginner",
        position_fen="8/8/8/8/8/8/4K3/7k w - - 0 1",
        c3x_text="C3X explanation.",baseline_text="Baseline explanation.",
        played_move="Ke3",understanding_prompt="Best interpretation?",
        understanding_options=["safe","unsafe"],understanding_answer="safe",
        seed="sealed-study-seed",
    )
    a=build_understanding_trial(**kwargs); b=build_understanding_trial(**kwargs)
    assert a==b
    assert "assigned_arm" not in a["participant_packet"]
    assert isinstance(a["participant_packet"]["commentary"],str)
    assert a["adjudication_key"]["assigned_arm"] in {"c3x","baseline","no_commentary"}
    assert a["adjudication_key"]["participant_id_hash"]!="participant-001"

def test_i8_preference_and_understanding_scoring_stay_separate():
    from c3x_explain.human_utility import (
        build_preference_trial,build_understanding_trial,
        score_preference_response,score_understanding_response,aggregate_human_outcomes
    )
    pref=build_preference_trial(
        trial_id="p-002",rating_band="beginner",
        position_fen="8/8/8/8/8/8/4K3/7k w - - 0 1",
        c3x_text="C3X explanation.",baseline_text="Baseline explanation.",
        played_move="Ke3",seed="sealed-study-seed",
        reference_validity={"c3x":True,"baseline":False},
    )
    presp={
        "correctness":{"A":5,"B":2},"usefulness":{"A":4,"B":3},
        "pedagogical_clarity":{"A":4,"B":2},"preference":"A",
        "trust":{"A":75,"B":25},
    }
    prow=score_preference_response(presp,pref["adjudication_key"])
    assert prow["schema"]=="c3x-human-preference-scored-v2"
    assert prow["c3x"]["trust_brier"] is not None

    under=build_understanding_trial(
        trial_id="u-002",participant_id="participant-002",rating_band="beginner",
        position_fen="8/8/8/8/8/8/4K3/7k w - - 0 1",
        c3x_text="C3X explanation.",baseline_text="Baseline explanation.",
        played_move="Ke3",understanding_prompt="Best interpretation?",
        understanding_options=["safe","unsafe"],understanding_answer="safe",
        seed="sealed-study-seed",
    )
    urow=score_understanding_response("safe",under["adjudication_key"])
    assert urow["correct"]==1
    assert "preference_c3x" not in urow

    summary=aggregate_human_outcomes([prow],[urow],expected_understanding_counts={
        f"beginner:{urow['assigned_arm']}":2
    })
    assert summary["human_outcome_opened"] is True
    cell=summary["understanding"]["by_band"]["beginner"][urow["assigned_arm"]]
    assert cell["observed_n"]==1 and cell["expected_n"]==2 and cell["missing_n"]==1
    assert cell["missing_worst_case_accuracy"]<=cell["missing_best_case_accuracy"]

def test_i8_trial_bank_manifest_has_no_human_outcome_bytes():
    from c3x_explain.human_utility import build_preference_trial,build_understanding_trial,trial_bank_manifest
    p=build_preference_trial(
        trial_id="p-bank",rating_band="expert",position_fen="8/8/8/8/8/8/4K3/7k w - - 0 1",
        c3x_text="c",baseline_text="b",played_move="Ke3",seed="s"
    )
    u=build_understanding_trial(
        trial_id="u-bank",participant_id="x",rating_band="expert",
        position_fen="8/8/8/8/8/8/4K3/7k w - - 0 1",
        c3x_text="c",baseline_text="b",played_move="Ke3",
        understanding_prompt="q",understanding_options=["a","b"],understanding_answer="a",seed="s"
    )
    m=trial_bank_manifest([p],[u])
    assert m["preference_trial_count"]==1
    assert m["understanding_trial_count"]==1
    assert m["human_outcomes_included"] is False
    assert len(m["public_identity_sha256"])==64


def test_i9_transparent_admissibility_atom_is_traceable_and_bounded():
    import chess
    packet={
      "schema":"c3x-transparent-susceptibility-decision-v1",
      "position_fen":chess.Board().fen(),
      "decision":"ADMIT",
      "family_id":"T1_INTEGER_SCORECARD",
      "trace":{
        "score":3,"threshold":2,
        "terms":[
          {"indicator":"pair_consensus_orientation","value":True,"coefficient":2,"contribution":2},
          {"indicator":"gap_dispersion_le_5","value":True,"coefficient":1,"contribution":1}
        ]
      },
      "feature_values":{"pair_geometry":"CONSENSUS_ORIENTATION","gap_dispersion_cp":4},
      "source_stage":"C3X 0.9.0-G10-P17"
    }
    out=analyze_pgn(PGN,susceptibility_packets=[packet])
    atoms=[a for m in out["moments"] for a in m["atoms"] if a["type"]=="intervention_admissibility"]
    assert len(atoms)==1
    a=atoms[0]
    assert a["provenance"]==HEURISTIC
    assert a["authority"]=="c3x_transparent_preoutcome_susceptibility"
    assert a["claim"]["decision"]=="ADMIT"
    assert "mechanism claims" in a["text"]
    m=next(m for m in out["moments"] if a["atom_id"] in {x["atom_id"] for x in m["atoms"]})
    assert m["firewall"]["pass"]
    assert any(n["node_type"]=="evidence_atom" and n["payload"]["type"]=="intervention_admissibility"
               for n in m["typed_graph"]["nodes"])
    assert any(s["role"]=="counterfactual_admissibility" for s in m["realization_packet"]["sentences"])

def test_i9_abstention_is_surfaceable_without_negative_chess_claim():
    import chess
    packet={
      "schema":"c3x-transparent-susceptibility-decision-v1",
      "position_fen":chess.Board().fen(),
      "decision":"ABSTAIN",
      "family_id":"T2_ORDERED_RULE_LIST",
      "trace":{"fired_rule":None},
      "abstention_reason":"no frozen transparent rule cleared the admission gate",
      "feature_values":{},
      "source_stage":"C3X 0.9.0-G10-P17"
    }
    out=analyze_pgn(PGN,susceptibility_packets=[packet])
    atom=next(a for m in out["moments"] for a in m["atoms"] if a["type"]=="intervention_admissibility")
    assert atom["claim"]["decision"]=="ABSTAIN"
    assert "abstains" in atom["text"]
    assert "chess idea is bad" in atom["text"]
    assert all(m["firewall"]["pass"] for m in out["moments"])


def test_p23_chain_unavailable_blocks_causal_certificate_surface():
    import chess,chess.pgn,io
    g=chess.pgn.read_game(io.StringIO(PGN));b=g.board()
    cert={"schema":"c3x-causal-contrast-certificate-v1","fen":b.fen(),"certificate_id":"p23-blocked",
          "pair_id":"e2e4::d2d4","bound":"LOWER","family":"OWN|DISPREFERRED_FROM_LOSS","collapse_to":"e2e4"}
    route={"schema":"c3x-explanation-authority-route-v1","position_fen":b.fen(),
           "state":"ABSTAIN_CHAIN_REALIZABILITY_UNAVAILABLE","source_stage":"C3X 0.10.0-G10-P23"}
    out=analyze_pgn(PGN,certificates=[cert],authority_packets=[route])
    causal=[a for m in out["moments"] for a in m["atoms"] if a["provenance"]==CAUSAL]
    routing=[a for m in out["moments"] for a in m["atoms"] if a["type"]=="mechanism_authority_route"]
    assert causal==[]
    assert routing and routing[0]["claim"]["state"]=="ABSTAIN_CHAIN_REALIZABILITY_UNAVAILABLE"
    assert out["causal_authority_blocked_moments"]>=1
    assert all(m["firewall"]["pass"] for m in out["moments"])


def test_p23_supported_route_preserves_bounded_causal_certificate():
    import chess,chess.pgn,io
    g=chess.pgn.read_game(io.StringIO(PGN));b=g.board()
    cert={"schema":"c3x-causal-contrast-certificate-v1","fen":b.fen(),"certificate_id":"p23-supported",
          "pair_id":"e2e4::d2d4","bound":"LOWER","family":"OWN|DISPREFERRED_FROM_LOSS","collapse_to":"e2e4"}
    route={"schema":"c3x-explanation-authority-route-v1","position_fen":b.fen(),
           "state":"SUPPORTED","source_stage":"C3X 0.10.0-G10-P23"}
    out=analyze_pgn(PGN,certificates=[cert],authority_packets=[route])
    causal=[a for m in out["moments"] for a in m["atoms"] if a["provenance"]==CAUSAL]
    assert causal and causal[0]["claim"]["certificate_id"]=="p23-supported"
    assert out["authority_packet_count"]==1


def test_p24_unverified_ecology_calibration_blocks_causal_certificate_surface():
    import chess,chess.pgn,io
    g=chess.pgn.read_game(io.StringIO(PGN));b=g.board()
    cert={"schema":"c3x-causal-contrast-certificate-v1","fen":b.fen(),"certificate_id":"p24-blocked",
          "pair_id":"e2e4::d2d4","bound":"LOWER","family":"OWN|DISPREFERRED_FROM_LOSS","collapse_to":"e2e4"}
    route={"schema":"c3x-explanation-authority-route-v1","position_fen":b.fen(),
           "state":"ABSTAIN_ECOLOGY_CALIBRATION_UNVERIFIED","source_stage":"C3X 0.10.0-G10-P24"}
    out=analyze_pgn(PGN,certificates=[cert],authority_packets=[route])
    causal=[a for m in out["moments"] for a in m["atoms"] if a["provenance"]==CAUSAL]
    routing=[a for m in out["moments"] for a in m["atoms"] if a["type"]=="mechanism_authority_route"]
    assert causal==[]
    assert routing and routing[0]["claim"]["state"]=="ABSTAIN_ECOLOGY_CALIBRATION_UNVERIFIED"
    assert "source-disjoint cohort" in routing[0]["text"]
    assert out["causal_authority_blocked_moments"]>=1
    assert all(m["firewall"]["pass"] for m in out["moments"])
