#!/usr/bin/env python3
"""C3X 0.14 — surgical first actual MAIN TT return and rival path trace.

28 fixed original/semantic-sham fully legal source worlds from pre-outcome
source freeze; 2 cold trials, CLEAN/OFF/ONE_MAIN/MAIN, depth12 MultiPV2.
Not independent validation of chess strategy or concept mediation.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
DEPTH=12
ARMS=("CLEAN","OFF","ONE_MAIN","MAIN")
REPEATS=(1,2)
def sha(b):return hashlib.sha256(b).hexdigest()

def run(binary,fen,pair,history,arm):
    b=chess.Board()
    for u in history:
        m=chess.Move.from_uci(u)
        if m not in b.legal_moves:raise RuntimeError("ILLEGAL_PREVIOUS_SOURCE_HISTORY")
        b.push(m)
    assert b.fen(en_passant="fen")==fen and b.turn==chess.WHITE and b.is_valid()
    assert len(pair)==2 and all(chess.Move.from_uci(m) in b.legal_moves for m in pair)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=arm)
    lines=[]
    with subprocess.Popen([binary],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT,text=True,bufsize=1) as p:
        def send(*cmd):p.stdin.write("\n".join(cmd)+"\n");p.stdin.flush()
        def till(prefix):
            for _ in range(100000):
                x=p.stdout.readline()
                if not x:raise RuntimeError("Engine EOF "+prefix+" "+str(lines[-8:]))
                lines.append(x.rstrip())
                if x.startswith(prefix):return
            raise RuntimeError("Unexpected native SF16 output size")
        send("uci");till("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        till("readyok")
        send("position startpos moves "+" ".join(history),
             "go depth "+str(DEPTH)+" searchmoves "+" ".join(pair))
        till("bestmove ");send("quit")
        if p.wait(timeout=15)!=0:raise RuntimeError("Nonzero engine return")
    info={}
    for line in lines:
        if not(line.startswith("info depth ") and " multipv " in line and " pv " in line):continue
        d=re.search(r"\bdepth (\d+)",line)
        if not d or int(d.group(1))!=DEPTH:continue
        k=re.search(r"\bmultipv (\d+)",line)
        sc=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",line)
        nd=re.search(r"\bnodes (\d+)",line)
        if not(k and sc and nd):continue
        pvmoves=line.split(" pv ",1)[1].split()
        if pvmoves[0] not in pair:continue
        info[int(k.group(1))]={
            "root_move":pvmoves[0],"score_kind":sc.group(1),
            "score_value_white":int(sc.group(2)),
            "score_flag":sc.group(3) or "exact_reported",
            "nodes":int(nd.group(1)),"pv":pvmoves[:14]}
    if set(info)!={1,2} or {v["root_move"] for v in info.values()}!=set(pair):
        raise RuntimeError("No complete depth12 MultiPV")
    best=[z.split()[1] for z in lines if z.startswith("bestmove ")]
    if len(best)!=1 or best[0]!=info[1]["root_move"]:raise RuntimeError("UCI bestmove mismatch")
    exact=all(v["score_kind"]=="cp" and v["score_flag"]=="exact_reported" for v in info.values())
    scores={v["root_move"]:v["score_value_white"] for v in info.values()}
    gap=scores[pair[0]]-scores[pair[1]] if exact else None
    out={"bestmove":best[0],"ranks":info,"signed_white_cp_gap":gap,"exact_numeric_cp":exact}
    if arm=="CLEAN":
        if any(z.startswith("info string c3x_p8_ep9") or z.startswith("info string c3x014_path")
               for z in lines):raise RuntimeError("Original engine unexpectedly instrumented")
    else:
        ttrows=[z for z in lines if z.startswith("info string c3x_p8_ep9 ")]
        native=[z for z in lines if z.startswith("info string c3x014_completion_probe ")]
        mech=[z for z in lines if z.startswith("info string c3x014_path ")]
        if len(ttrows)!=1 or len(native)!=1 or len(mech)!=1:
            raise RuntimeError("Source native telemetry count invalid "+str([len(ttrows),len(native),len(mech)]))
        tt={k:int(v) for k,v in (t.split("=",1) for t in ttrows[0].split()[3:])}
        nt={k:int(v) for k,v in (t.split("=",1) for t in native[0].split()[3:])}
        mc={k:int(v) for k,v in (t.split("=",1) for t in mech[0].split()[3:])}
        if tt["mode"]!={"OFF":0,"ONE_MAIN":4,"MAIN":1}[arm]:raise RuntimeError("Wrong EP9 mode")
        if nt["best_completed"]!=DEPTH or nt["main_completed"]!=DEPTH:raise RuntimeError("Fixed depth not completed")
        if tt["q_blocked"]!=0:raise RuntimeError("Unexpected qsearch cutoff suppression")
        if arm=="OFF" and tt["main_blocked"]!=0:raise RuntimeError("OFF improperly blocks TT")
        if arm=="ONE_MAIN" and tt["main_blocked"] not in (0,1):
            raise RuntimeError("ONE_MAIN exceeded one blocked return")
        if arm=="ONE_MAIN" and tt["main_eligible"]>0 and tt["main_blocked"]!=1:
            raise RuntimeError("ONE_MAIN failed to block an actual eligible return")
        if arm=="MAIN" and tt["main_taken"]!=0:raise RuntimeError("MAIN failed to block all real returns")
        if tt["main_blocked"]>0 and mc["first_blocked_ply"]<0:raise RuntimeError("Blocked event lacks provenance")
        if tt["main_blocked"]==0 and mc["first_blocked_ply"]!=-1:raise RuntimeError("Invented blocked event")
        for n in ("picker_main_nodes","picker_main_ttmove","lmr_invoked","lmr_with_reduction",
                  "history_quiet_update","history_continuation_update","main_evaluate_calls",
                  "main_tt_eval_reads","main_alpha_beta_move_cutoffs","main_tt_save_terminal"):
            if mc[n]<0:raise RuntimeError("Negative engine counter")
        out["native_tt"]=tt;out["native_completed"]=nt;out["mechanism_path"]=mc
    return out
def semantic(r):
    return {k:r[k] for k in ("bestmove","ranks","signed_white_cp_gap","exact_numeric_cp")}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--frozen-source",required=True);ap.add_argument("--clean",required=True)
    ap.add_argument("--patched",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if sha(Path(a.frozen_source).read_bytes())!=SOURCE_SHA:raise SystemExit("CONCEPT_SOURCE_SHA_MISMATCH")
    p=json.loads(Path(a.frozen_source).read_bytes())
    assert p["schema"]=="c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1"
    assert p["groups_with_both_worlds"]==14 and not p["engine_scores_seen_during_source_freeze"]
    groups=[c for c in p["cases"] if c["concept_changing_world"] is not None and c["concept_preserving_world"] is not None]
    assert len(groups)==14 and not p["P1_sealed_holdout_read"]
    cases=[]
    for index,c in enumerate(groups,start=1):
        for wlabel,black,fen in [
           ("PLAYED_HISTORY",c["original_black18"],c["original_legal_history_root_fen"]),
           ("CONCEPT_SHAM_HISTORY",c["concept_preserving_world"]["black18_uci"],c["concept_preserving_world"]["root_full_FEN"])]:
            history=c["first_17_ply_path_uci"]+[black]
            for repeat in REPEATS:
                arms={}
                for mode in ARMS:
                    arms[mode]=run(a.clean if mode=="CLEAN" else a.patched,
                                   fen,c["root_candidate_pair"],history,mode)
                sham=semantic(arms["CLEAN"])==semantic(arms["OFF"])
                if not sham:raise RuntimeError("NATIVE_PROVENANCE_SHAM_MISMATCH_"+wlabel+"_"+c["official_original_game_headers"]["Round"])
                o,u,m=arms["OFF"],arms["ONE_MAIN"],arms["MAIN"]
                def contrast(t):
                    x=o["signed_white_cp_gap"];y=t["signed_white_cp_gap"]
                    return y-x if x is not None and y is not None else None
                row={"source_game":c["source_game_id"],"group":c["source_group"],
                    "round":c["official_original_game_headers"]["Round"],"world":wlabel,
                    "historically_legal_black18":black,"root_FEN":fen,"full_history":history,
                    "legal_white_root_pair":c["root_candidate_pair"],"cold_repeat":repeat,
                    "original_CLEAN_vs_OFF_sham_exact":sham,"arms":arms,
                    "one_return_gap_shift_cp":contrast(u),
                    "main_family_gap_shift_cp":contrast(m),
                    "one_return_UCI_bestmove_changed":o["bestmove"]!=u["bestmove"],
                    "main_family_UCI_bestmove_changed":o["bestmove"]!=m["bestmove"],
                    "one_return_strict_signed_cp_inversion":o["signed_white_cp_gap"] is not None and u["signed_white_cp_gap"] is not None and o["signed_white_cp_gap"]*u["signed_white_cp_gap"]<0,
                    "all_family_strict_signed_cp_inversion":o["signed_white_cp_gap"] is not None and m["signed_white_cp_gap"] is not None and o["signed_white_cp_gap"]*m["signed_white_cp_gap"]<0}
                cases.append(row)
                print("C3X014_SINGLE_EVENT_ACTUAL",index,row["round"],wlabel,"cold",repeat,
                      "blocked",u["native_tt"]["main_blocked"],"off_ONE_MAIN_family",
                      o["signed_white_cp_gap"],u["signed_white_cp_gap"],m["signed_white_cp_gap"],
                      "one_flip",row["one_return_UCI_bestmove_changed"],
                      "full_flip",row["main_family_UCI_bestmove_changed"],flush=True)
    assert len(cases)==14*2*2
    cold=0
    for g in groups:
        for world in ("PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"):
            a,b=[x for x in cases if x["group"]==g["source_group"] and x["world"]==world]
            if a["arms"]==b["arms"]:cold+=1
    assert cold==28,("COLD_EVENT_OR_SOURCE_OUTPUT_NOT_REPRODUCIBLE",cold)
    first=[c for c in cases if c["cold_repeat"]==1]
    groupsummary=[]
    for g in groups:
        original=next(c for c in first if c["group"]==g["source_group"] and c["world"]=="PLAYED_HISTORY")
        sham=next(c for c in first if c["group"]==g["source_group"] and c["world"]=="CONCEPT_SHAM_HISTORY")
        site0=original["arms"]["ONE_MAIN"]["mechanism_path"]["first_blocked_key"]
        site1=sham["arms"]["ONE_MAIN"]["mechanism_path"]["first_blocked_key"]
        groupsummary.append({
          "round":original["round"],"group":g["source_group"],
          "same_measured_pawn_concept_contrast":True,
          "different_source_board_world":original["root_FEN"]!=sham["root_FEN"],
          "first_TT_return_posKey_same_across_two_worlds":site0==site1,
          "historical_first_event_key_played":site0,"historical_first_event_key_semantic_sham":site1,
          "played_one_event_cp_shift":original["one_return_gap_shift_cp"],
          "sham_world_one_event_cp_shift":sham["one_return_gap_shift_cp"],
          "played_one_event_root_flip":original["one_return_UCI_bestmove_changed"],
          "sham_world_one_event_root_flip":sham["one_return_UCI_bestmove_changed"],
          "played_family_root_flip":original["main_family_UCI_bestmove_changed"],
          "sham_world_family_root_flip":sham["main_family_UCI_bestmove_changed"]})
    result={"schema":"c3x-014-one-native-TT-return-vs-family-and-mechanism-rival-trace-v1",
      "formal_unit":"C3X 0.14","internal_work_only":True,
      "one_formal_C3X_study_no_P_substage":True,
      "source_worlds_sha256":SOURCE_SHA,"original_engine_sha256":sha(Path(a.clean).read_bytes()),
      "surgical_engine_sha256":sha(Path(a.patched).read_bytes()),
      "source_game_groups":14,"concept_preserving_alternative_per_group":1,
      "distinct_source_history_worlds":28,"cold_restarts":2,"actual_engine_processes":224,
      "source_world_cold_cells":56,"source_worlds_two_cold_identical_all_arms":cold,
      "clean_vs_OFF_control_exact_all_56":all(x["original_CLEAN_vs_OFF_sham_exact"] for x in cases),
      "ONE_MAIN_blocked_event_count_per_run_max":max(x["arms"]["ONE_MAIN"]["native_tt"]["main_blocked"] for x in cases),
      "ONE_MAIN_runs_with_exactly_one_blocked_event":sum(x["arms"]["ONE_MAIN"]["native_tt"]["main_blocked"]==1 for x in cases),
      "worlds_first_cold_one_event_root_flip":sum(x["one_return_UCI_bestmove_changed"] for x in first),
      "worlds_first_cold_family_root_flip":sum(x["main_family_UCI_bestmove_changed"] for x in first),
      "worlds_first_cold_one_event_strict_sign_inversion":sum(x["one_return_strict_signed_cp_inversion"] for x in first),
      "worlds_first_cold_family_strict_sign_inversion":sum(x["all_family_strict_signed_cp_inversion"] for x in first),
      "source_group_contrasts":groupsummary,"all_raw_native_run_cells":cases,
      "P1_sealed_four_games_opened":False,"causal_chess_concept_mediation_identified":False,
      "separate_LMR_history_order_NNUE_alpha_beta_causal_effects_identified":False,
      "scientific_limits":[
        "ONE_MAIN blocks first dynamically encountered eligible main TT bound return in each run. Different black world may have different first events, not a matched exact same transposition key.",
        "Each intervention is at EXACT same full 18-ply chess history within each world; the chess board and pawn feature vector are held fixed.",
        "Counters of MovePicker TT moves, LMR, history, static NNUE evaluations and alpha-beta cutoffs are downstream search-path observables, not factorial interventions or mediators causally identified.",
        "The early TT return pathway may have already updated quiet TT move history before the actual return, and this pre-return side effect is preserved in ONE_MAIN.",
        "Same nominal search depth does not match actual nodes/work; source group N=14 and two cold repeats not 56 independent games.",
        "Original TCEC development-game cohort is known from prior experiments, not independent fresh ecological replication."]}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print("C3X014_SINGLE_TT_RETURN_MECHANISM_VERDICT",json.dumps({
      "games":14,"worlds":28,"engine_runs":224,"cold":cold,
      "one_blocked":result["ONE_MAIN_runs_with_exactly_one_blocked_event"],
      "one_root_flips":result["worlds_first_cold_one_event_root_flip"],
      "family_root_flips":result["worlds_first_cold_family_root_flip"],
      "one_strict":result["worlds_first_cold_one_event_strict_sign_inversion"],
      "family_strict":result["worlds_first_cold_family_strict_sign_inversion"],
      "cross_world_first_TT_key_same":sum(x["first_TT_return_posKey_same_across_two_worlds"] for x in groupsummary)}),flush=True)
if __name__=="__main__":main()
