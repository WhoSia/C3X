#!/usr/bin/env python3
"""Explicit source-native no-search root-opportunity PIN probe, chess law frozen40."""
import argparse,collections,hashlib,json,subprocess
from pathlib import Path
import chess

SOURCE_SHA="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
FIELDS=("key","in_check","pseudo","legal","captures","see_samples","see_pass",
        "root_legal_pinned_checks","root_legal_pin_rejects","root_see_pinned_masks",
        "root_mobility_pin_blockers","root_WeakQueen_hits",
        "classical_mobility_nonzero_pin_blockers","classical_WeakQueen_hits",
        "classical_WeakQueen_own_blockers","classical_WeakQueen_enemy_blockers")
SIG_FIELDS=("root_legal_pinned_checks","root_legal_pin_rejects","root_see_pinned_masks",
            "root_mobility_pin_blockers","root_WeakQueen_hits")
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(p,msg):
    if not p:raise RuntimeError(msg)
def native_probe(bin,hist):
    cmds="uci\nsetoption name Threads value 1\nsetoption name Hash value 16\nsetoption name Use NNUE value false\nisready\nposition startpos moves "+" ".join(hist)+"\nc3x014_root_probe\nquit\n"
    p=subprocess.run([bin],input=cmds,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                     text=True,timeout=40)
    require(p.returncode==0,"C3X014_ROOT_PROBE_NONZERO_EXIT_"+p.stderr[-500:])
    require("bestmove " not in p.stdout and "info depth " not in p.stdout,
            "FORCED_ROOT_PROBE_WRONGLY_PERFORMED_SEARCH")
    rows=[ln for ln in p.stdout.splitlines() if ln.startswith("info string c3x014_explicit_root_probe ")]
    require(len(rows)==1,"FORCED_NATIVE_ROOT_PROBE_OUTPUT_NOT_UNIQUE")
    obj={k:int(v) for k,v in (w.split("=",1) for w in rows[0].split()[3:])}
    require(set(obj)==set(FIELDS),"FORCED_NATIVE_SITE_FIELD_MISMATCH")
    require(all(n>=0 for n in obj.values()),"NEGATIVE_ROOT_PIN_SITE")
    require(obj["pseudo"]>=obj["legal"] and obj["see_samples"]==obj["captures"]*3,
            "ROOT_LEGAL_SEE_CENSUS_INVALID")
    require(obj["root_legal_pin_rejects"]<=obj["root_legal_pinned_checks"],
            "ROOT_PIN_REJECT_MORE_THAN_CHECKS")
    require(obj["root_WeakQueen_hits"]<=obj["classical_WeakQueen_hits"],
            "ROOT_WEAKQUEEN_MORE_THAN_SOURCE_HITS")
    return obj
def sign(z):return tuple(int(z[k]>0) for k in SIG_FIELDS)
def main():
    ap=argparse.ArgumentParser()
    for a in ("source","engine","out"):ap.add_argument("--"+a,required=True)
    x=ap.parse_args()
    require(sha(x.source)==SOURCE_SHA,"FROZEN_SOURCE_ONLY_40_PIN_SHA")
    src=json.loads(Path(x.source).read_bytes())
    cases=[]
    for i,w in enumerate(src["source_only_selected_witnesses"],1):
        board=chess.Board()
        for move in w["source_game_history_uci"]:
            require(chess.Move.from_uci(move) in board.legal_moves,"SOURCE_HISTORY_ILLEGAL")
            board.push_uci(move)
        require(board.fen(en_passant="fen")==w["board_six_field_FEN"],"SOURCE_ROOT_FEN_MISMATCH")
        samples=[native_probe(x.engine,w["source_game_history_uci"]) for _ in range(2)]
        require(samples[0]==samples[1],"SOURCE_NATIVE_ROOT_PROBE_COLD_NOT_EQUAL")
        got=samples[0]
        require(got["legal"]==board.legal_moves.count(),
                "ORIGINAL_SF16_LEGAL_MOVES_VS_CHESS_LIBRARY_MISMATCH")
        require(got["in_check"]==int(board.is_check()),"ROOT_CHECK_MISMATCH")
        cases.append({"game_index":w["game_index"],"round":w["source_round"],
            "law_subtype":w["source_chess_law_subtype"],"source_PIN_FEN":w["board_six_field_FEN"],
            "source_PIN_square":w["pinned_square"],
            "genuine_forced_NONGO_native_operators":got,
            "root_probe_presence_signature":sign(got),
            "is_force_probe_not_search_event":True})
        print("C3X014_EXPLICIT_ROOT_PIN_SITE_FIRED",i,w["game_index"],
              w["pinned_piece"],"signature",sign(got),
              "legal_source",got["legal"],"pin_rejected",got["root_legal_pin_rejects"],
              "weakqueen",got["root_WeakQueen_hits"],flush=True)
    require(len(cases)==40,"TOTAL_FROZEN_PIN_CASES_NOT40")
    groups=collections.defaultdict(list)
    for r in cases:groups[json.dumps(r["law_subtype"],sort_keys=True)].append(r)
    repeated={k:v for k,v in groups.items() if len(v)>1}
    require(len(groups)==30 and len(repeated)==4 and sum(len(v) for v in repeated.values())==14,"FROZEN_REPEATS")
    diverge=sum(len({tuple(row["root_probe_presence_signature"]) for row in group})>1
                for group in repeated.values())
    out={"schema":"c3x-014-explicit-post-hoc-genuine-sf16-root-pin-operator-opportunity-v1",
      "formal_research":"C3X 0.14","new_formal_P_substage":False,
      "source_legal_pin_40_cases_SHA256":SOURCE_SHA,
      "native_engine_SHA256":sha(x.engine),
      "fresh_native_SF16_processes":80,
      "actual_engine_searches":0,
      "cold_repeat_exact_root_operators":"40/40",
      "root_legal_moves_match_independent_chess_library":"40/40",
      "native_root_king_in_check_cases":sum(z["genuine_forced_NONGO_native_operators"]["in_check"] for z in cases),
      "forced_root_operator_nonzero_case_counts":{
          k:sum(z["genuine_forced_NONGO_native_operators"][k]>0 for z in cases) for k in SIG_FIELDS},
      "forced_root_operator_total_counts":{
          k:sum(z["genuine_forced_NONGO_native_operators"][k] for z in cases) for k in SIG_FIELDS},
      "distinct_legal_pin_law_composite_subtypes":len(groups),
      "repeated_legal_law_subtype_groups":4,
      "repeated_law_types_divergent_forced_root_operation_presence":diverge,
      "repeated_groups_case_details":{k:{"cases":len(v),
                    "distinct_source_games":len({q["game_index"] for q in v}),
                    "distinct_forced_root_opportunity_binary_signatures":
                        len({tuple(q["root_probe_presence_signature"]) for q in v})}
             for k,v in repeated.items()},
      "all_original_40_root_full_chess_source_and_true_forced_native_calls":cases,
      "causal_pin_specific_engine_search_effect_identified":False,
      "native_NNUE_latent_learned_subtype_identified":False,
      "procedural_P1_holdout_game_groups_used":False,
      "evidence_limits":[
          "FORCED diagnostic calls are intentionally scheduled at same root after original full history; they are NOT naturally invoked by original search and cannot be relabeled so.",
          "Original source Position::legal checked on pseudo-generated root candidate moves and Position::see_ge on legal root captures at thresholds -100,0,+100, then source classical Eval::trace(pos) only if no check.",
          "Root SEE mask depends on captures and threshold availability; if no qualifying captures occurred, zero is opportunity-limited.",
          "Classical WeakQueen covers either side of queen/slider ray, and is not a learned latent NNUE feature.",
          "Within law type differences remain observationally confounded by other material/placement and do not prove root PIN causal tactics.",
          "One TT/NNUE search-related inference cannot be copied from different worlds. New independent engine/source replication needed."
      ]}
    f=Path(x.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_EXPLICIT_ROOT_PIN_OPPORTUNITY_NATIVE_COURT_VERDICT",json.dumps({
      "source_worlds":40,"native_processes":80,"native_legal_certified":40,
      "force_root_presence":out["forced_root_operator_nonzero_case_counts"],
      "within_law_diverse":diverge}),flush=True)
if __name__=="__main__":main()
