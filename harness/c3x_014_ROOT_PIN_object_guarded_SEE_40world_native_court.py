#!/usr/bin/env python3
"""C3X 0.14 strict natural-search original root PIN object SEE conditional court.

ALL previously score-blind frozen 40 S29 root witnesses, not selected by
global intervention responses. Real Source Native Stockfish16 2-arm×2-cold
160 engine processes, strict OFF sham vs 400-run source original baseline.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess,collections
from pathlib import Path
import chess
from c3x_014_pin_native_trace_fields import PIN_FIELDS

S29_SOURCE="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
S29_PRIOR_CAUSAL="336d9fcd5d5023a73824dc95b9399570b2786bfcb527dd2e1a42b6471a6a7374"
MODES=("OFF","ROOT_OBJECT_SEE_UNMASK")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def must(x,msg):
    if not x:raise RuntimeError(msg)
def main_engine(engine,source,arm):
    board=chess.Board()
    for move in source["source_game_history_uci"]:
        assert chess.Move.from_uci(move) in board.legal_moves
        board.push_uci(move)
    sq=chess.parse_square(source["pinned_square"])
    sniper=chess.parse_square(source["pinning_square"])
    must(board.is_pinned(board.turn,sq),"UNPINNED_ROOT_FROZEN_OBJECT")
    must(board.piece_at(sniper) is not None and
        board.piece_at(sniper).color !=board.piece_at(sq).color,"NOT_ENEMY_ROOT_PINNER")
    env={**os.environ,"C3X014_PIN_ROOT_OBJECT_ARM":arm,
        "C3X014_PIN_ROOT_SQUARE_ID":str(sq),
        "C3X014_PIN_ROOT_PINNER_ID":str(sniper)}
    lines=[]
    with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
          text=True,bufsize=1,env=env) as p:
        def send(*commands):
            p.stdin.write("\n".join(commands)+"\n");p.stdin.flush()
        def until(prefix):
            for _ in range(180000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("NATIVE_ROOT_OBJECT_EOF_BEFORE_"+prefix)
                lines.append(line.rstrip())
                if line.startswith(prefix):return
            raise RuntimeError("NATIVE_ROOT_OBJECT_TOO_MUCH_OUTPUT")
        send("uci");until("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1","setoption name Use NNUE value false",
             "ucinewgame","isready")
        until("readyok")
        send("position startpos moves "+" ".join(source["source_game_history_uci"]),"go depth 12")
        until("bestmove ")
        send("quit")
        must(p.wait(timeout=18)==0,"ROOT_OBJECT_ENGINE_NONZERO_EXIT")
    infos=[]
    for line in lines:
        if not line.startswith("info depth "):continue
        mat=re.search(r"\bdepth (\d+)",line)
        if not mat or int(mat.group(1))!=12 or " pv " not in line:continue
        score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",line)
        nodes=re.search(r"\bnodes (\d+)",line)
        if score and nodes:
            infos.append({"score_kind":score.group(1),
             "value_root_stm":int(score.group(2)),
             "score_flag":score.group(3) or "exact_reported",
             "nodes":int(nodes.group(1)),
             "pv":line.split(" pv ",1)[1].split()[:16]})
    must(infos,"DEPTH12_COMPLETION_MISSING")
    last=infos[-1]
    best=[line.split()[1] for line in lines if line.startswith("bestmove ")]
    must(len(best)==1 and best[0]==last["pv"][0],"MISSING_OR_ILLEGAL_BESTMOVE")
    m=chess.Move.from_uci(best[0])
    must(m in board.legal_moves,"STOCKFISH16_CHOSE_ILLEGAL_ROOT_MOVE")
    last.update({"bestmove":best[0],"pinned_piece_moved":m.from_square==sq,
        "root_full_FEN":board.fen(en_passant="fen"),"depth12_completed_reported":True,
        "evaluation_arm":"CLASSICAL"})
    def typed(key):
        data=[z for z in lines if z.startswith("info string "+key+" ")]
        must(len(data)==1,"NATIVE_SITE_INFO_MISSING_OR_DUPLICATE_"+key)
        out={}
        for token in data[0].split()[3:]:
            k,v=token.split("=",1);out[k]=int(v)
        return out
    tracer=typed("c3x014_native_pin_trace")
    must(set(tracer)==set(PIN_FIELDS),"S29_SITE_TRACE_SOURCE_FIELDS_CHANGED")
    last["native_pin_trace"]=tracer
    obj=typed("c3x014_root_object_see")
    must(set(obj)=={"arm","pinned_square","pinner_square","king_square","considered","target_fired"},
        "INVALID_ROOT_OBJECT_NATIVE_COUNTER_SCHEMA")
    must(obj["arm"]==MODES.index(arm) and obj["pinned_square"]==sq and
        obj["pinner_square"]==sniper and obj["king_square"]==board.king(board.turn),
        "ROOT_OBJECT_SOURCE_IDENTITY_REJECTED_BY_STOCKFISH")
    must(obj["considered"]>=obj["target_fired"]>=0,"ROOT_OBJECT_WITNESS_COUNT_INCONSISTENT")
    if arm=="OFF":must(obj["target_fired"]==obj["considered"]==0,"ROOT_OFF_ACTUALLY_TREATED")
    last["object_guard"]=obj
    return last
def base_only(z):return {k:v for k,v in z.items() if k!="object_guard"}
def main():
    ap=argparse.ArgumentParser()
    for key in ("source","prior-400","engine","out"):ap.add_argument("--"+key,required=True)
    a=ap.parse_args()
    must(sha(a.source)==S29_SOURCE,"OLD40_SOURCE_CHANGED")
    must(sha(a.prior_400)==S29_PRIOR_CAUSAL,"OLD_SOURCE_NATIVE_CAUSAL_TRIAL_CHANGED")
    src=json.loads(Path(a.source).read_bytes())
    parent=json.loads(Path(a.prior_400).read_bytes())
    frozen=src["source_only_selected_witnesses"]
    prior=parent["all_40_root_worlds_and_5_original_native_treatment_runs"]
    must(len(frozen)==len(prior)==40,"NOT40_ORIGINAL")
    rows=[]
    for i,(w,old) in enumerate(zip(frozen,prior),1):
        must(w["board_six_field_FEN"]==old["root_original_FEN"],"PRIOR_S29_SOURCE_ROW_MISMATCH")
        results={}
        for mode in MODES:
            reps=[main_engine(a.engine,w,mode) for _ in range(2)]
            must(reps[0]==reps[1],"ROOT_PIN_OBJECT_COLD_REPRODUCE_FAIL_"+mode)
            results[mode]=reps[0]
        baseline={k:v for k,v in old["all_real_native_SF16_classic_five_arms"]["OFF"].items()
                  if k!="pin_causal_intervention"}
        must(base_only(results["OFF"])==baseline,"OBJECT_SOURCE_PASSIVE_OFF_ALTERED_REAL_ORIGINAL_SEARCH_OR_COUNTERS")
        # Treatment guards target the EXACT source root pinned piece and its
        # original pinning slider, allowing ONLY that bit through static SEE.
        target=results["ROOT_OBJECT_SEE_UNMASK"]
        original=results["OFF"]
        changed={k:target[k]!=original[k] for k in ("bestmove","score_kind","score_flag","value_root_stm","pv","nodes")}
        fired=target["object_guard"]["target_fired"]
        if fired==0:must(not any(changed.values()),"ROOT_OBJECT_NOT_FIRED_YET_UCI_OUTPUT_CHANGED")
        global_resp=old["direct_software_causal_branch_vs_OFF"]["SEE_UNMASK"]["bestmove_changed"]
        rows.append({"source_game":w["game_index"],"source_round":w["source_round"],
            "original_root_pin_square":w["pinned_square"],
            "original_root_pinner_square":w["pinning_square"],
            "original_root_chess_law":w["source_chess_law_subtype"],
            "root_full_FEN":w["board_six_field_FEN"],
            "original_global_SEE_UNMASK_bestmove_change":global_resp,
            "targeted_exposure":target["object_guard"],
            "root_object_TARGETED_changed_bestmove":changed["bestmove"],
            "root_object_TARGETED_changed_score":any(changed[k] for k in ("score_kind","score_flag","value_root_stm")),
            "root_object_TARGETED_changed_PV":changed["pv"],
            "root_object_TARGETED_changed_nodes":changed["nodes"],
            "source_native_OFF":original,
            "source_native_targeted_ROOT_PIN_SEE_UNMASK":target,
            "method":"root-pinned piece/pinner/king source identities matched and target piece present among SEE pinned attackers; only its one bit unmasked"})
        print("C3X014_SOURCE_NATIVE_ROOT_OBJECT_PIN_SEE",i,w["game_index"],
            "target_event",fired,"global_SEE_flip",global_resp,
            "object_SEE_flip",changed["bestmove"],flush=True)
    out={"schema":"c3x-014-source-original-S29-frozen40-true-root-pin-object-guarded-SEE-causal-v1",
      "formal_research":"C3X 0.14","next_015_not_open":True,
      "exact_original_source_frozen_SHA256":S29_SOURCE,
      "previous_40_global_software_SEE_WQ_trial_SHA256":S29_PRIOR_CAUSAL,
      "root_SOURCE_games":40,
      "source_root_objects_exact_king_pinner_and_pinned_piece_native_guarded":True,
      "actual_source_native_SF16_engine_processes":160,
      "native_per_arm":2,"cold_exact_all_80_conditions":"80/80",
      "original_SF16_OFF_bestmove_score_PV_nodes_and_full_site_trace_equal":"40/40",
      "root_PIN_chess_move_generation_changed":False,
      "original_global_SEE_UNMASK_bestmove_responder_worlds":sum(r["original_global_SEE_UNMASK_bestmove_change"] for r in rows),
      "targeted_root_object_source_SEE_fired_worlds":sum(r["targeted_exposure"]["target_fired"]>0 for r in rows),
      "targeted_root_object_source_SEE_actual_events":sum(r["targeted_exposure"]["target_fired"] for r in rows),
      "targeted_root_object_SEE_intervention_changed_bestmove":sum(r["root_object_TARGETED_changed_bestmove"] for r in rows),
      "targeted_root_object_SEE_intervention_changed_score":sum(r["root_object_TARGETED_changed_score"] for r in rows),
      "global_SEE_flip_but_specific_object_branch_never_exposed":sum(
          r["original_global_SEE_UNMASK_bestmove_change"] and r["targeted_exposure"]["target_fired"]==0 for r in rows),
      "all_40_object_specific_output_and_site_traces":rows,
      "old_4game_P1_procedural_holdout_untouched":True,
      "independent_S28_object_targeted_court_executed":False,
      "latent_NNUE_pin_feature_identified":False,
      "scientific_limits":[
         "Object-conditional SEE-unmask changes an artificial static exchange heuristic only; chess legal moves and move generator remain original.",
         "An original pinned piece must still occupy the source square, original pinner slider and king must occupy the original squares, native pin bitboards must confirm the same royal pin, and hypothetical SEE occupied bitboard must preserve the pinner.",
         "If eligible event never fires, this search cannot identify its effect at this source pin; zero is an exposure limit, not absence of chess tactics.",
         "This observation is limited to original frozen S29 source worlds, original SF16 version classical route and depth12.",
         "Full algebraically learned NNUE features and human tactical explanation reliability are not tested."
      ]}
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("C3X014_ROOT_PIN_OBJECT_NATIVE_CONDITIONAL_SEE_CAUSAL_VERDICT",json.dumps({
      "source_worlds":40,"real_engine_processes":160,
      "original_global_SEE_bestmove_flips":out["original_global_SEE_UNMASK_bestmove_responder_worlds"],
      "root_object_fired_worlds":out["targeted_root_object_source_SEE_fired_worlds"],
      "root_object_fired_events":out["targeted_root_object_source_SEE_actual_events"],
      "root_object_bestmove_changed":out["targeted_root_object_SEE_intervention_changed_bestmove"],
      "global_SEE_flip_where_original_ROOT_object_never_fired":out["global_SEE_flip_but_specific_object_branch_never_exposed"]}),flush=True)
if __name__=="__main__":main()
