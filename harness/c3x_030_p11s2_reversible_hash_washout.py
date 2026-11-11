#!/usr/bin/env python3
"""C3X 0.30 P11/S2 — within-one-process Clear Hash washout/rebound trial.

For each of P11's 20 *development* FENs, run same full-strength Stockfish16
process and same game object 7 searches in fixed preregistered order:
baseline, warm1, warm2, clear1, postclear_warm1, clear2, postclear_warm2.

Direct UCI Clear Hash button before clear1/clear2; no new game, and no process
restart within each FEN. Test return to baseline vs warm rebound.
Historical discovery cohort, not independent confirmation or TT-exclusive proof.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import chess
import chess.engine
from c3x_030_p11_repeatability_cohort import positions, SOURCE_COMMIT
from c3x_030_p11s1_search_state_ablation import trial,engine_configuration,check_options,NODE_LIMIT

SCHEMA="c3x030-p11s2-reversible-clear-hash-washout-v1"
PHASES=("baseline","warm1","warm2","clear1","postclear_warm1","clear2","postclear_warm2")
CLEAR_PHASES=("clear1","clear2")

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def phase_summary(moves):
    if set(moves)!=set(PHASES):
        raise ValueError("P11S2_HOLD_PHASE_SET")
    base=moves["baseline"]
    return {
        "warm1_differs":moves["warm1"]!=base,
        "warm2_differs":moves["warm2"]!=base,
        "clear1_restores":moves["clear1"]==base,
        "clear2_restores":moves["clear2"]==base,
        "after_clear1_warm_differs":moves["postclear_warm1"]!=base,
        "after_clear2_warm_differs":moves["postclear_warm2"]!=base,
        "both_clear_phases_restore":moves["clear1"]==base and moves["clear2"]==base,
        "any_nonclear_warm_differs":any(moves[p]!=base for p in PHASES
                                       if p not in ("baseline",*CLEAR_PHASES)),
        "distinct_moves":len(set(moves.values()))
    }

def run(binary):
    out={"schema":SCHEMA,"source_commit":SOURCE_COMMIT,
         "stockfish_binary_sha256":digest(binary),"phases":list(PHASES),
         "clear_hash_before":list(CLEAR_PHASES),"requested_nodes":NODE_LIMIT,
         "chess_engine_skill_level":20,"uci_limit_strength":False,
         "use_nnue":False,"threads":1,
         "development_reuses_previous_p11_positions":True,
         "new_holdout_position_cohort":False,"natively_instrumented_TT_entries":False,
         "causal_claim_isolated_to_complete_TT_only":False,
         "cohort":{}}
    for pos_id,source in positions().items():
        board=chess.Board(source["fen"])
        rows={}
        with chess.engine.SimpleEngine.popen_uci(binary,timeout=120) as engine:
            check_options(engine)
            engine.configure(engine_configuration())
            game=object()
            for phase in PHASES:
                if phase in CLEAR_PHASES:
                    engine.configure({"Clear Hash":None})
                rows[phase]=trial(engine,board,game)
        moves={name:rows[name]["move_uci"] for name in PHASES}
        summary=phase_summary(moves)
        out["cohort"][pos_id]=dict(source,phase_rows=rows,summary=summary)
        print("P11S2_PHASES",pos_id,repr(moves),repr(summary),flush=True)
    out["total_native_searches"]=len(out["cohort"])*len(PHASES)
    out["total_actual_nodes"]=sum(row["nodes_actual"] for x in out["cohort"].values()
                                   for row in x["phase_rows"].values())
    out["position_summary_counts"]={
        key:sum(int(p["summary"][key]) for p in out["cohort"].values())
        for key in ("warm1_differs","warm2_differs",
                    "clear1_restores","clear2_restores",
                    "both_clear_phases_restore",
                    "after_clear1_warm_differs","after_clear2_warm_differs",
                    "any_nonclear_warm_differs")}
    out["source_search_event_to_final_choice_mediation_proven"]=False
    out["physical_uci_button_intervention_executed"]=True
    out["limitations"]=("UCI Clear Hash can modify engine search-related state. We have not "
                        "measured exact TT-entry changes and do not assert all non-TT "
                        "state is held fixed; descriptive mechanistic washout protocol.")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stockfish",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    d=run(a.stockfish)
    file=Path(a.out);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("P11S2_REAL_NATIVE",d["total_native_searches"],"NODES",d["total_actual_nodes"],
          "COUNTS",repr(d["position_summary_counts"]),"SHA",digest(file),flush=True)

if __name__=="__main__":main()
