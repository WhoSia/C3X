import json

import chess

from c3x_g10.demand_validity import (
    P1_POLICY,
    adjudicate_demand_validity,
    engine_stability_features,
    freeze_base_evaluation_bank,
    freeze_final_case_bank,
    maia_policy_features,
    opening_relation,
    phase_from_board,
    p1_preseal,
    refined_gate,
)


def test_preseal_forbids_certificate_yield():
    p=p1_preseal()
    assert p["fresh_certificate_outcomes_opened"] is False
    assert p["certificate_yield_visible"] is False
    assert p["policy"]["uses_certificate_yield"] is False
    assert p["policy"]["annotation_used_for_selection"] is False


def test_opening_relation_not_ply_only():
    catalog=[
        {"eco":"B00","name":"King Pawn","moves":("e2e4",),"epd":""},
        {"eco":"B20","name":"Sicilian","moves":("e2e4","c7c5"),"epd":""},
    ]
    x=opening_relation(["e2e4"],catalog)
    assert x["relation"]=="EXACT_NAMED_POSITION"
    assert x["theory_proximity"] is True
    assert x["ply_only_proxy_used"] is False
    y=opening_relation(["d2d4"],catalog)
    assert y["relation"]=="NO_NAMED_PREFIX"


def test_maia_salience_requires_both_pair_moves_across_bands():
    p={
        1200:{"e2e4":.30,"d2d4":.10,"g1f3":.05},
        1800:{"e2e4":.25,"d2d4":.09,"g1f3":.10},
        2400:{"e2e4":.10,"d2d4":.02,"g1f3":.30},
    }
    x=maia_policy_features(p,played_uci="e2e4",candidate_pair=("e2e4","d2d4"))
    assert x["supported_band_count"]==2
    assert x["human_pair_supported"] is True
    assert x["actual_human_judgment"] is False


def _obs(a,b,c="g1f3"):
    return {"candidates":[{"uci":a},{"uci":b},{"uci":c}]}


def test_engine_stability_preserves_pair_not_order():
    obs={
        "stockfish_19@2000":_obs("e2e4","d2d4"),
        "stockfish_19@5000":_obs("d2d4","e2e4"),
        "stockfish_19@10000":_obs("e2e4","d2d4"),
        "stockfish_19@40000":_obs("e2e4","c2c4","d2d4"),
        "berserk@10000":_obs("d2d4","g1f3","e2e4"),
        "ethereal@10000":_obs("c2c4","e2e4","d2d4"),
    }
    x=engine_stability_features(obs,candidate_pair=("e2e4","d2d4"))
    assert x["stockfish_budget_pair_support"]==4
    assert x["cross_engine_medium_pair_support"]==3
    assert x["engine_pair_stable"] is True
    assert x["order_flip_allowed"] is True


def test_refined_gate_excludes_theory_when_human_pair_supported():
    row={
        "p0":{"admitted":True},
        "opening":{"theory_proximity":True},
        "validity":{
            "human_salience":{"human_pair_supported":True},
            "engine_stability":{"engine_pair_stable":True},
        },
    }
    x=refined_gate(row)
    assert x["admitted"] is False
    assert "OPENING_THEORY_DEGENERACY" in x["reasons"]
    assert x["annotation_used"] is False


def test_banks_are_hash_addressed_and_annotation_free():
    rows=[]
    for i in range(60):
        rows.append({
            "case_id":f"c{i}",
            "source_month":"2026-07" if i%2==0 else "2026-08",
            "phase":["opening","middlegame","endgame"][i%3],
            "opening":{"theory_proximity":bool(i%2)},
            "p0":{"admitted":True},
            "validity":{
                "human_salience":{"human_pair_supported":not bool(i%2)},
                "engine_stability":{"engine_pair_stable":True},
            },
        })
    base=freeze_base_evaluation_bank(rows)
    assert len(base["cases"])==P1_POLICY["base_eval_target"]
    assert base["annotation_labels_used"] is False
    scored=[]
    for x in base["cases"]:
        x=dict(x);x["refined_gate"]=refined_gate(x);scored.append(x)
    bank=freeze_final_case_bank(scored)
    assert bank["bank_sha256"]
    assert bank["selection_rule"]["annotation_used"] is False
    assert bank["fresh_local_certificate_induction_opened"] is False


def test_phase_is_descriptive_only():
    assert phase_from_board(chess.Board())=="opening"


def test_court_holds_if_maia_unrealized():
    court=adjudicate_demand_validity(
        pool_summary={"positions_scanned":100},
        scored_base_rows=[],
        scored_controls=[],
        final_bank={"cases":[],"bank_sha256":"x"},
        instrument_status={
            "maia3_all_rating_bands_pass":False,
            "all_three_engines_pass":True,
            "opening_corpus_pass":True,
            "annotation_source_pass":True,
        },
    )
    assert court["verdict"]=="HOLD_HUMAN_SALIENCE_INSTRUMENT_UNREALIZED"
    assert court["fresh_local_certificate_induction_opened"] is False
