#!/usr/bin/env python3
"""C3X 0.14 — Stockfish16 NNUE/classical evaluation phenotypes of legal pin subtypes.

Original unpatched engine, 40 predetermined source-only legal pin witness worlds,
two evaluator settings with two cold starts; NOT evidence of learned pin labels.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,os,re,subprocess
from pathlib import Path
import chess

SOURCE_SHA="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
DEPTH=12
MODES=("NNUE","CLASSICAL")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def must(x,msg):
    if not x:raise RuntimeError(msg)

def native(engine_path,history,pinned_square,mode,capture_pin_trace=False):
    board=chess.Board()
    for u in history:
        m=chess.Move.from_uci(u)
        must(m in board.legal_moves,"ILLEGAL_GAME_HISTORY")
        board.push(m)
    must(board.turn is not None and board.is_pinned(board.turn,chess.parse_square(pinned_square)),
         "PIN_WITNESS_NOT_TRUE_ON_ROOT")
    lines=[]
    with subprocess.Popen([engine_path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True,bufsize=1) as p:
        def send(*xs):p.stdin.write("\n".join(xs)+"\n");p.stdin.flush()
        def until(prefix):
            for _ in range(120000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("STOCKFISH_UCI_EOF")
                lines.append(line.rstrip())
                if line.startswith(prefix):return
            raise RuntimeError("EXCESSIVE_UCI_OUTPUT")
        send("uci");until("uciok")
        opts="\n".join(x for x in lines if x.startswith("option name "))
        must("option name Use NNUE " in opts,"STOCKFISH16_NO_NATIVE_NNUE_SWITCH")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1",
             "setoption name Use NNUE value "+("true" if mode=="NNUE" else "false"),
             "ucinewgame","isready")
        until("readyok")
        send("position startpos moves "+" ".join(history),"go depth "+str(DEPTH))
        until("bestmove ")
        send("quit")
        must(p.wait(timeout=15)==0,"STOCKFISH_EXIT_NONZERO")
    final=[]
    for line in lines:
        if not line.startswith("info depth "):continue
        d=re.search(r"\bdepth (\d+)",line)
        if not d or int(d.group(1))!=DEPTH or " pv " not in line:continue
        score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",line)
        nd=re.search(r"\bnodes (\d+)",line)
        if not(score and nd):continue
        pv=line.split(" pv ",1)[1].split()
        final.append({"score_kind":score.group(1),"value_root_stm":int(score.group(2)),
                      "score_flag":score.group(3) or "exact_reported",
                      "nodes":int(nd.group(1)),"pv":pv[:16]})
    must(bool(final),"MISSING_DEPTH12_FINAL_PV")
    last=final[-1]
    best=[line.split()[1] for line in lines if line.startswith("bestmove ")]
    must(len(best)==1 and best[0]==last["pv"][0],"INVALID_UCI_FINAL_BESTMOVE")
    chosen=chess.Move.from_uci(best[0])
    must(chosen in board.legal_moves,"ENGINE_CHOSE_ILLEGAL_MOVE")
    last.update({"bestmove":best[0],"pinned_piece_moved":chosen.from_square==chess.parse_square(pinned_square),
                 "root_full_FEN":board.fen(en_passant="fen"),
                 "depth12_completed_reported":True,
                 "evaluation_arm":mode})
    if capture_pin_trace:
        traces=[ln for ln in lines if ln.startswith("info string c3x014_native_pin_trace ")]
        must(len(traces)==1,"REAL_PIN_SOURCE_TRACE_MISSING_OR_DUPLICATE")
        trace={}
        for kv in traces[0].split()[3:]:
            name,value=kv.split("=",1)
            trace[name]=int(value)
        from c3x_014_pin_native_trace_fields import PIN_FIELDS
        must(set(trace)==set(PIN_FIELDS),"NATIVE_PIN_TRACE_FIELDS_INCOMPLETE")
        must(all(v>=0 for v in trace.values()),"NEGATIVE_NATIVE_PIN_EVENT_COUNT")
        last["native_pin_trace"]=trace
    return last

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--stockfish",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    must(sha(a.source)==SOURCE_SHA,"ENGINE_PIN_SAMPLE_NOT_FROZEN_SOURCE_ONLY")
    s=json.loads(Path(a.source).read_bytes())
    must(s["schema"]=="c3x-014-official-TCEC-S29-chess-law-absolute-pin-subtype-census-before-engine-scores-v1","WRONG_PIN_CENSUS")
    must(s["games_read"]==100 and s["source_only_selected_sample_size"]==40,"PIN_SOURCE_SELECTION_DRIFT")
    must(not s["engine_outputs_used_for_selection"],"ENGINE_SELECTED_PIN_SOURCE")
    rows=[]
    for i,w in enumerate(s["source_only_selected_witnesses"],1):
        arm={}
        for mode in MODES:
            tests=[native(a.stockfish,w["source_game_history_uci"],w["pinned_square"],mode)
                   for cold in (1,2)]
            must(tests[0]==tests[1],"NATIVE_PIN_COLD_DIFFER_"+mode+"_"+str(i))
            must(tests[0]["root_full_FEN"]==w["board_six_field_FEN"],"PIN_SOURCE_FEN_MISMATCH")
            arm[mode]=tests[0]
        n,c=(arm[k] for k in MODES)
        numeric=n["score_kind"]==c["score_kind"]=="cp" and n["score_flag"]==c["score_flag"]=="exact_reported"
        row={"source_game_index":w["game_index"],"source_round":w["source_round"],
             "ply":w["ply"],"pinned_square":w["pinned_square"],
             "pinned_piece":w["pinned_piece"],"pinning_piece":w["pinning_piece"],
             "pin_axis":w["axis"],"pin_subtype":w["source_chess_law_subtype"],
             "source_original_FEN":w["board_six_field_FEN"],
             "pin_root_legal_piece_move_count":w["pinned_piece_legal_moves_count"],
             "pin_root_pseudo_legal_piece_move_count":w["pinned_piece_pseudolegal_moves_count"],
             "pin_can_capture_pinner":w["pinned_piece_can_legally_capture_pinner"],
             "nnue_and_classical":arm,"bestmove_changed_between_evaluation_implementations":
                 n["bestmove"]!=c["bestmove"],
             "pinned_piece_moves_in_NNUE":n["pinned_piece_moved"],
             "pinned_piece_moves_in_classical":c["pinned_piece_moved"],
             "same_root_bestmove_different_evaluation_cp":numeric and
                 n["bestmove"]==c["bestmove"] and n["value_root_stm"]!=c["value_root_stm"],
             "NNUE_minus_classical_root_cp":n["value_root_stm"]-c["value_root_stm"] if numeric else None}
        rows.append(row)
        print("C3X014_REAL_STOCKFISH_PIN_EVAL_ALGORITHM_CONTRAST",i,
              w["source_round"],w["pinned_piece"],w["pinning_piece"],w["axis"],
              "root",n["bestmove"],c["bestmove"],"cp",row["NNUE_minus_classical_root_cp"],
              "NNUE_pinnedmove",n["pinned_piece_moved"],
              "classic_pinnedmove",c["pinned_piece_moved"],flush=True)
    must(len(rows)==40,"PIN_OUTPUT_MISSING")
    group=collections.defaultdict(list)
    for r in rows:group[r["pinned_piece"]].append(r)
    groupstats={k:{"source_positions":len(a),
                    "NNUE_and_classical_choose_different_root_move":
                      sum(r["bestmove_changed_between_evaluation_implementations"] for r in a),
                    "NNUE_selected_pinned_piece_move":sum(r["pinned_piece_moves_in_NNUE"] for r in a),
                    "CLASSICAL_selected_pinned_piece_move":sum(r["pinned_piece_moves_in_classical"] for r in a),
                    "observed_cp_only_contrasts":sum(r["NNUE_minus_classical_root_cp"] is not None for r in a)}
                for k,a in sorted(group.items())}
    out={"schema":"c3x-014-source-frozen-king-absolute-pin-native-NNUE-vs-classical-phenotype-court-v1",
         "one_formal_stage":"C3X 0.14","internal_concept_discovery_only":True,
         "original_source_only_chess_law_pin_sha256":SOURCE_SHA,
         "original_stockfish16_sf_16_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
         "original_stockfish_engine_binary_sha256":sha(a.stockfish),
         "source_game_groups":len({z["source_game_index"] for z in rows}),
         "source_pinned_legal_positions":40,
         "evaluation_modes":["Use NNUE true","Use NNUE false"],
         "actual_native_unmodified_SF16_engine_processes":160,
         "technical_cold_restarts_per_condition":2,
         "cold_reproducibility_all_conditions":"80/80",
         "root_bestmove_changes_when_entire_evaluator_switches":
             sum(r["bestmove_changed_between_evaluation_implementations"] for r in rows),
         "NNUE_classical_root_cp_score_differences_exact_and_numeric":
             sum(r["NNUE_minus_classical_root_cp"] is not None and r["NNUE_minus_classical_root_cp"]!=0 for r in rows),
         "number_of_root_NNUE_pinned_piece_moves":sum(r["pinned_piece_moves_in_NNUE"] for r in rows),
         "number_of_root_CLASSICAL_pinned_piece_moves":sum(r["pinned_piece_moves_in_classical"] for r in rows),
         "per_chess_law_pinned_piece_type":groupstats,"all_actual_source_pin_native_evaluation_cells":rows,
         "P1_four_game_sealed_holdout_touched":False,
         "has_established_stockfish_specific_internal_pin_subtypes":False,
         "has_established_pins_cause_engine_search_preference_changes":False,
         "has_established_educational_explanation_utility":False,
         "interpretation_limits":[
           "NNUE versus CLASSICAL is an intervention on the entire evaluator implementation, NOT on a pin. It affects all chess position concepts and subsequent search tree.",
           "The law pin subtype labels were fixed without engine scores; selecting an engine result difference does not demonstrate the engine has internal discrete pin labels.",
           "The 40 source positions are deliberately subtype diversified and not a random unbiased sample of all chess positions.",
           "Repeated positions within the original 100 TCEC matches are strongly correlated by opening/players.",
           "No causal effect of relative queen pins, mobility, SEE, or history/LMR is identified merely from UCI bestmove changes.",
           "A source-layer follow-up needs per-position SEE/mobility/WeakQueen native branch telemetry and exposure before any discovered latent mechanism claim."
         ]}
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("C3X014_PIN_EVALUATION_IMPL_NATIVE_COURT_VERDICT",json.dumps({
      "positions":40,"engines":160,"changed_root_bestmove":out["root_bestmove_changes_when_entire_evaluator_switches"],
      "NNUE_moves_pinned_piece":out["number_of_root_NNUE_pinned_piece_moves"],
      "classic_moves_pinned_piece":out["number_of_root_CLASSICAL_pinned_piece_moves"],
      "subgroups":groupstats}),flush=True)
if __name__=="__main__":main()
