#!/usr/bin/env python3
"""Verify a native search event's exact 2-ply chess ancestry and TT-bound direction.

EP11 native raw panel is required, SHA-lock enforced by calling CI. Enumerates ALL
legal 2-ply paths from the original full-six-field FEN to the event full-six-field
FEN. Does NOT infer that the engine's original move preference is chess causation.
"""
import argparse,hashlib,json
from pathlib import Path
import chess

EXPECTED_ROOT="2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17"
EXPECTED_EVENT="2r2rk1/p1q2ppp/bp1bnn2/3pN3/2pP1P1P/1P2P1P1/PB2NRB1/R2Q2K1 w - - 1 18"
SOURCE_SHA="40e389cbd2a4b68782d7b211f5db5e44c9bf1a04dc6d78d1df08910a07155c48"

def court(raw):
    assert raw["schema"]=="c3x-013-p8ep11-tt-key-fen-context-replay-v1"
    assert raw["controls_all_pass"]
    assert raw["source_fen"]==EXPECTED_ROOT
    assert raw["event_anchor"]["node_full_fen"]==EXPECTED_EVENT
    root=chess.Board(EXPECTED_ROOT)
    assert root.is_valid()
    target=chess.Board(EXPECTED_EVENT)
    assert target.is_valid()
    paths=[]
    for m1 in root.legal_moves:
        b1=root.copy(stack=True)
        b1.push(m1)
        for m2 in b1.legal_moves:
            b2=b1.copy(stack=True)
            b2.push(m2)
            if b2.fen(en_passant="fen")==EXPECTED_EVENT:
                paths.append({"moves_uci":[m1.uci(),m2.uci()],
                              "moves_san":[root.san(m1),b1.san(m2)],
                              "root_candidate":m1.uci(),
                              "event_fen":b2.fen(en_passant="fen")})
    paths.sort(key=lambda p:p["moves_uci"])
    assert paths==[{"moves_uci":["f3f4","d8c7"],"moves_san":["f4","Qc7"],
                    "root_candidate":"f3f4","event_fen":EXPECTED_EVENT}],paths
    event=raw["event_anchor"]["native_event"]
    assert event["actual_key_hex"]==raw["event_anchor"]["key_hex"]=="5794315daed72c1b"
    assert event["actual_tt_bound"]==2, "SF16 bound 2 is BOUND_LOWER"
    assert event["actual_value"]==108 and event["actual_beta"]==100 and event["actual_alpha"]==99
    assert event["actual_tt_depth"]==4 and event["actual_depth"]==2
    assert event["actual_rule50"]==1 and event["actual_ply"]==2
    assert raw["same_exact_position_depth12_count"]==4
    assert raw["keyed_replay_equals_ordinal_intervention_depth12_count"]==4
    assert all(x["controls_all_pass"] if "controls_all_pass" in x else True for x in raw["cells"])
    fact={"schema":"c3x-013-p8ep11-legal-root-to-search-event-provenance-v1",
        "scoped_verdict":"EXACT_TWO_PLY_PATH_VERIFIED__NODE_TT_LOWER_BOUND_RETURN__NO_STRATEGIC_CAUSAL_CERTIFICATE",
        "origin_game":"CECLUB 2026 original reused P7, not independent holdout",
        "original_root_fen":EXPECTED_ROOT,"actual_event_fen":EXPECTED_EVENT,
        "two_ply_legal_paths_to_exact_event_fen":paths,
        "legal_path_count":1,
        "event_line":"17. f4 Qc7",
        "event_within_root_candidate":"f3f4",
        "event_outside_alternative_candidate":"g3g4",
        "native_tt_key_hex":event["actual_key_hex"],
        "tt_bound_code":2,"tt_bound_name":"BOUND_LOWER",
        "tt_entry_stored_depth":event["actual_tt_depth"],
        "node_remaining_depth":event["actual_depth"],
        "node_window_alpha":event["actual_alpha"],
        "node_window_beta":event["actual_beta"],
        "tt_return_value":event["actual_value"],
        "technical_meaning":"Lower-bound TT value 108 exceeds node beta 100 and permits MAIN non-PV early return in this exact original SF16 execution.",
        "confidence_ceiling":["The stored TT entry carries only a 16-bit key signature, not proof of full 64-bit entry provenance.","The exact event node is in the f3f4 candidate's searched branch, not automatically a reason for choosing f3f4.","Search changes propagate after the prevented return, and no novel independent games or human learning assessments were collected."],
        "causal_chess_strategy_claim":False,
        "C3X_014_at_EP11_run":"UNOPENED_UNNAMED"}
    return fact

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--json-out",required=True)
    p.add_argument("--markdown-out",required=True);a=p.parse_args()
    b=Path(a.input).read_bytes();assert hashlib.sha256(b).hexdigest()==SOURCE_SHA,"EP11 original science artifact hash mismatch"
    x=court(json.loads(b))
    Path(a.json_out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.json_out).write_text(json.dumps(x,indent=2)+"\n")
    Path(a.markdown_out).write_text(
        "# C3X 0.13 EP11 — Verified engine-search event location\n\n"
        "In the previously examined CECLUB position, the ONE legal two-ply path to the "
        "actual Stockfish 16 TT-cutoff node was **17. f4 Qc7** (UCI f3f4, d8c7). "
        "At that exact node the TT entry reported a **lower-bound** value 108 "
        "against beta 100, and the native main-search early return could occur. "
        "Intervening at the keyed event reproduced the ordinal32 local engine "
        "preference sensitivity in this same source position. This does **not** "
        "prove that a human chess concept, the move f4 itself, or an invariant "
        "TT entry caused the engine's preferred root move. "
        "Source panel SHA-256: "+SOURCE_SHA+".\n")
    print("EP11_EXACT_LEGAL_EVENT_ANCESTRY_PASS",x["event_line"],x["technical_meaning"])
if __name__=="__main__":main()
