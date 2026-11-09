#!/usr/bin/env python3
"""P42/R21-D: complete original P34 planned same-board static SF16 NNUE trace.

Re-use original P34 R3 source-faithful trace adapter on the same legal chess
histories and root/reply conditions, *without* rerunning its adaptive reference
search or releasing private FEN/history/trace bytes. This isolates actual
static scores on same board, not search outcome or learned NNUE feature cause.
"""
import argparse,json,hashlib,collections
from pathlib import Path
from c3x_029_p34_r3_direct_nnue_classical_eval_trace import build
from c3x_029_p32_original_history_reply_value_native import FROZEN_SOURCE_SHA256

P34_SHA="c80704f2f81c4920597fbf6b559ef38dbae60f35458c7a2f665f1cf57d2563dc"

def digest(raw):return hashlib.sha256(raw).hexdigest()

def summarize(built):
    rows=built["records"]
    status=dict(collections.Counter(x["trace"]["status"] for x in rows))
    passed=[]
    for x in rows:
        t=x["trace"]
        if t["status"]!="DIRECT_STATIC_TRACE_OK":continue
        passed.append({"case_id":x["case_id"],"root_uci":x["root"],
                       "scope":x["scope"],"reply_uci":x["reply"],
                       "classical_white_pawns":t["classical_white_pawns"],
                       "nnue_white_pawns":t["nnue_white_pawns"],
                       "hybrid_final_white_pawns":t["final_white_pawns"],
                       "nnue_minus_classical_white_pawns":t["raw_nnue_minus_classical_white_pawns"],
                       "same_score_sign":(t["classical_white_pawns"]>0)==(t["nnue_white_pawns"]>0),
                       "raw_trace_sha256":x["raw_trace_sha256"]})
    return {"schema":"c3x042-r21-D-original-source-NNUE-static-evaluation-court-v1",
        "status":"ACTUAL_UNMODIFIED_STOCKFISH16_SAME_BOARD_STATIC_EVAL_ONLY",
        "source_original_C3X018_SHA":FROZEN_SOURCE_SHA256,
        "previous_P34_R2_SHA":P34_SHA,
        "total_same_board_conditions":len(rows),
        "trace_status_counts":status,
        "independently_parsed_static_worlds":len(passed),
        "white_pawn_score_sign_differences":sum(not x["same_score_sign"] for x in passed),
        "records":passed,
        "actual_nnue_feature_attribution_proved":False,
        "root_search_selection_causally_explained":False,
        "independent_chess_truth_proved":False,
        "new_prospective_cohort":False,
        "claim_ceiling":"Source-original static eval comparison only. Same-board NNUE/classical difference is not learned-feature causal source mediation, nor objective chess value."}

def main():
    p=argparse.ArgumentParser()
    for s in ("source","p34","engine","out"):p.add_argument("--"+s,required=True)
    a=p.parse_args()
    raw_source=Path(a.source).read_bytes()
    raw_p34=Path(a.p34).read_bytes()
    if digest(raw_source)!=FROZEN_SOURCE_SHA256 or digest(raw_p34)!=P34_SHA:
        raise ValueError("R21_D_HOLD_ORIGINAL_SOURCE_OR_P34_RECEIPT")
    original=build(json.loads(raw_source),json.loads(raw_p34),a.engine)
    if original["source_sha256"]!=FROZEN_SOURCE_SHA256:
        raise ValueError("R21_D_HOLD_ORIGINAL_ROOT_GAME_SOURCE")
    report=summarize(original)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R21_D_ACTUAL_SF16_STATIC_EVAL",report["independently_parsed_static_worlds"],
          "/",report["total_same_board_conditions"],"sign_changes",report["white_pawn_score_sign_differences"])
    if report["independently_parsed_static_worlds"]==0:
        raise SystemExit("R21_D_HOLD_NO_ACTUAL_ORIGINAL_SOURCE_STATIC_EVAL")

if __name__=="__main__":
    main()
