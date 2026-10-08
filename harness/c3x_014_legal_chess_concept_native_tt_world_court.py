#!/usr/bin/env python3
"""C3X 0.14 legal PGN-history concept mediation *challenge*, no mediation proof.

All source worlds are selected without SF16 outcome data in original artifact.
This code runs CLEAN / EP9 OFF / EP9 MAIN with two cold restarts for every
historically legal original/alternative FEN and a FEN-only history-drop control.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
DEPTH=12
MODES=("CLEAN","OFF","MAIN")
WORLD_LABELS=("PLAYED_HISTORY","CONCEPT_CHANGE_HISTORY","CONCEPT_SHAM_HISTORY","PLAYED_FEN_ONLY")

def filehash(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()

def engine(binary,fen,pair,prefix,mode,fen_only):
    b=chess.Board(fen)
    assert b.is_valid() and b.turn==chess.WHITE
    assert all(chess.Move.from_uci(m) in b.legal_moves for m in pair)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    lines=[]
    with subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as p:
        def send(*q):p.stdin.write("\n".join(q)+"\n");p.stdin.flush()
        def till(prefix):
            for _ in range(150000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("Engine EOF while "+prefix)
                lines.append(line.rstrip())
                if line.startswith(prefix):return
            raise RuntimeError("UCI response size unexpected")
        send("uci");till("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        till("readyok")
        if fen_only:send("position fen "+fen)
        else:send("position startpos moves "+" ".join(prefix))
        send("go depth "+str(DEPTH)+" searchmoves "+" ".join(pair))
        till("bestmove ");send("quit")
        if p.wait(timeout=12)!=0:raise RuntimeError("Native SF16 error")
    info={}
    for line in lines:
        if not(line.startswith("info depth ") and " multipv " in line and " pv " in line):continue
        dm=re.search(r"\bdepth (\d+)",line)
        if not dm or int(dm.group(1))!=DEPTH:continue
        rank=re.search(r"\bmultipv (\d+)",line)
        score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",line)
        nodes=re.search(r"\bnodes (\d+)",line)
        if not(rank and score and nodes):continue
        mv=line.split(" pv ",1)[1].split()[0]
        if mv not in pair:continue
        info[int(rank.group(1))]={"move":mv,"kind":score.group(1),
               "value_white":int(score.group(2)),"bound":score.group(3) or "exact_reported",
               "nodes":int(nodes.group(1)),"pv":line.split(" pv ",1)[1].split()[:12]}
    if set(info)!={1,2} or {r["move"] for r in info.values()}!=set(pair):
        raise RuntimeError("Missing depth12 complete two-rank PV "+str(info))
    best=[x.split()[1] for x in lines if x.startswith("bestmove ")]
    if len(best)!=1 or best[0]!=info[1]["move"]:raise RuntimeError("UCI bestmove final rank mismatch")
    typed=all(z["kind"]=="cp" and z["bound"]=="exact_reported" for z in info.values())
    bymv={z["move"]:z["value_white"] for z in info.values()}
    gap=bymv[pair[0]]-bymv[pair[1]] if typed else None
    provenance={"depth":DEPTH,"requested_history_complete":not fen_only,
                "bestmove":best[0],"ranks":info,"signed_white_gap_cp":gap,
                "numeric_cp_exact":typed}
    if mode=="CLEAN":
        if any(z.startswith("info string c3x_p8_ep9 ") for z in lines):
            raise RuntimeError("Original unexpectedly instrumented")
    else:
        ts=[z for z in lines if z.startswith("info string c3x_p8_ep9 ")]
        ds=[z for z in lines if z.startswith("info string c3x014_completion_probe ")]
        if len(ts)!=1 or len(ds)!=1:raise RuntimeError("Missing native telemetry")
        tt={k:int(v) for k,v in (p.split("=",1) for p in ts[0].split()[3:])}
        native={k:int(v) for k,v in (p.split("=",1) for p in ds[0].split()[3:])}
        if tt["mode"]!={"OFF":0,"MAIN":1}[mode] or tt["q_blocked"]!=0:raise RuntimeError("Wrong native mode")
        if mode=="OFF" and tt["main_blocked"]!=0:raise RuntimeError("Sham blocked return")
        if native["best_completed"]!=DEPTH or native["main_completed"]!=DEPTH:
            raise RuntimeError("UCI fixed-depth node not completed")
        provenance["native_tt"]=tt;provenance["native_completed"]=native
    return provenance

def scientific_eq(a,b):
    return {k:a[k] for k in ("bestmove","ranks","signed_white_gap_cp","numeric_cp_exact")}=={
            k:b[k] for k in ("bestmove","ranks","signed_white_gap_cp","numeric_cp_exact")}

def build_worlds(group):
    pre=chess.Board()
    moves=group["first_17_ply_path_uci"]
    if len(moves)!=17:raise RuntimeError("Not exactly 17 historical plies")
    for move in moves:pre.push_uci(move)
    if pre.fen(en_passant="fen")!=group["first_17_ply_fen"]:
        raise RuntimeError("Legal history original mismatch")
    spec=[("PLAYED_HISTORY",group["original_black18"],group["original_legal_history_root_fen"],False),
          ("PLAYED_FEN_ONLY",group["original_black18"],group["original_legal_history_root_fen"],True)]
    for name,key in (("CONCEPT_CHANGE_HISTORY","concept_changing_world"),
                     ("CONCEPT_SHAM_HISTORY","concept_preserving_world")):
        w=group[key]
        if w is not None:spec.append((name,w["black18_uci"],w["root_full_FEN"],False))
    out=[]
    for name,black,fen,fen_only in spec:
        board=pre.copy(stack=True)
        board.push_uci(black)
        if board.fen(en_passant="fen")!=fen:raise RuntimeError("World lacks historical FEN equivalence")
        pair=group["root_candidate_pair"]
        if not all(chess.Move.from_uci(m) in board.legal_moves for m in pair):
            raise RuntimeError("Candidate pair illegal in historical world")
        out.append({"name":name,"original_black_move":black,
                    "root_fen":fen,"full_18_ply_history":moves+[black],
                    "fen_only":fen_only,"pair":pair})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--concept-source",required=True)
    p.add_argument("--clean",required=True);p.add_argument("--instrumented",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    if filehash(args.concept_source)!=SOURCE_SHA:raise SystemExit("SOURCE_ONLY_CONCEPT_ARTIFACT_BYTES_MISMATCH")
    src=json.loads(Path(args.concept_source).read_bytes())
    assert src["schema"]=="c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1"
    assert src["source_group_count"]==16 and src["groups_with_both_worlds"]==14
    assert len(src["cases"])==16 and src["engine_scores_seen_during_source_freeze"] is False
    assert not src["P1_sealed_holdout_read"]
    cells=[]
    for idx,c in enumerate(src["cases"],start=1):
        worlds=build_worlds(c)
        for world in worlds:
            for cold in (1,2):
                clean=engine(args.clean,world["root_fen"],world["pair"],world["full_18_ply_history"],"CLEAN",world["fen_only"])
                off=engine(args.instrumented,world["root_fen"],world["pair"],world["full_18_ply_history"],"OFF",world["fen_only"])
                main=engine(args.instrumented,world["root_fen"],world["pair"],world["full_18_ply_history"],"MAIN",world["fen_only"])
                sham=scientific_eq(clean,off)
                if not sham:raise RuntimeError("FAILED_CLEAN_EP9_SHAM_EQUIVALENCE "+c["official_original_game_headers"]["Round"]+" "+world["name"])
                g0=off["signed_white_gap_cp"];g1=main["signed_white_gap_cp"]
                flip=off["bestmove"]!=main["bestmove"]
                strict=(g0 is not None and g1 is not None and g0*g1<0)
                cell={"group":c["source_group"],"round":c["official_original_game_headers"]["Round"],
                      "source_game_id":c["source_game_id"],"world":world["name"],"world_source":world,
                      "cold_repeat":cold,"clean":clean,"off":off,"main":main,
                      "sham_exact":sham,"main_masked_TT_cutoffs":main["native_tt"]["main_blocked"],
                      "gap_shift_white_cp":g1-g0 if g0 is not None and g1 is not None else None,
                      "strict_white_cp_gap_sign_inverted":strict,"UCI_bestmove_changed":flip}
                cells.append(cell)
                print("C3X014_NATIVE_CHESS_CONCEPT_CELL",idx,c["official_original_game_headers"]["Round"],
                      world["name"],cold,"off_main_gap",g0,g1,"shift",cell["gap_shift_white_cp"],
                      "flip",flip,"ttmask",cell["main_masked_TT_cutoffs"],flush=True)
    assert len(cells)==60*2 and all(c["sham_exact"] for c in cells)
    # Frozen population, first cold source-game summaries, do not throw out NULL.
    indexed={}
    for c in cells:
        if c["cold_repeat"]==1:indexed.setdefault(c["group"],{})[c["world"]]=c
    assert len(indexed)==16
    cold=0
    for g in indexed:
        for label,c in indexed[g].items():
            other=next(x for x in cells if x["group"]==g and x["world"]==label and x["cold_repeat"]==2)
            if all(c[k]==other[k] for k in ("clean","off","main","gap_shift_white_cp",
                        "strict_white_cp_gap_sign_inverted","UCI_bestmove_changed")):cold+=1
    if cold!=60:raise RuntimeError("COLD_NOT_STABLE "+str(cold))
    summaries=[]
    for case in src["cases"]:
        group=case["source_group"];d=indexed[group]
        orig=d["PLAYED_HISTORY"]
        fen=d["PLAYED_FEN_ONLY"]
        ent={"source_group":group,"source_round":case["official_original_game_headers"]["Round"],
             "target_available":"CONCEPT_CHANGE_HISTORY" in d,
             "semantic_sham_available":"CONCEPT_SHAM_HISTORY" in d,
             "source_concept_delta":case["targeted_concept_delta"],
             "history_vs_FEN_OFF_same_output":scientific_eq(orig["off"],fen["off"]),
             "history_vs_FEN_MAIN_same_output":scientific_eq(orig["main"],fen["main"]),
             "original_TT_gap_shift_white_cp":orig["gap_shift_white_cp"],
             "worlds":{}}
        for kind in ("CONCEPT_CHANGE_HISTORY","CONCEPT_SHAM_HISTORY"):
            if kind not in d:continue
            w=d[kind]
            ent["worlds"][kind]={
                "root_black18_uci":w["world_source"]["original_black_move"],
                "TT_gap_shift_white_cp":w["gap_shift_white_cp"],
                "difference_in_TT_gap_shift_vs_played_cp":(w["gap_shift_white_cp"]-orig["gap_shift_white_cp"]
                 if w["gap_shift_white_cp"] is not None and orig["gap_shift_white_cp"] is not None else None),
                "root_bestmove_relabel_under_MAIN":w["UCI_bestmove_changed"],
                "blocked_MAIN":w["main_masked_TT_cutoffs"]}
        if all(k in d for k in ("CONCEPT_CHANGE_HISTORY","CONCEPT_SHAM_HISTORY")):
            change=d["CONCEPT_CHANGE_HISTORY"];sham=d["CONCEPT_SHAM_HISTORY"]
            ent["difference_TT_sensitivity_concept_change_minus_sham_cp"]=(
                change["gap_shift_white_cp"]-sham["gap_shift_white_cp"]
                if change["gap_shift_white_cp"] is not None and sham["gap_shift_white_cp"] is not None else None)
        summaries.append(ent)
    histories_differ=sum(not x["history_vs_FEN_OFF_same_output"] for x in summaries)
    changed_worlds=[x for x in summaries if x["target_available"]]
    changed_vs_original=[x["worlds"]["CONCEPT_CHANGE_HISTORY"]["difference_in_TT_gap_shift_vs_played_cp"] for x in changed_worlds]
    sham_vs_original=[x["worlds"]["CONCEPT_SHAM_HISTORY"]["difference_in_TT_gap_shift_vs_played_cp"] for x in summaries if x["semantic_sham_available"]]
    contrasts=[x["difference_TT_sensitivity_concept_change_minus_sham_cp"] for x in summaries if "difference_TT_sensitivity_concept_change_minus_sham_cp" in x]
    def stats(nums):
        valid=[x for x in nums if x is not None]
        return {"observed_groups":len(nums),"finite_cp_groups":len(valid),
                "nonzero_groups":sum(x!=0 for x in valid),
                "mean_signed_cp":sum(valid)/len(valid) if valid else None,
                "median_abs_cp":sorted(abs(x) for x in valid)[len(valid)//2] if valid else None}
    out={"schema":"c3x-014-historical-legal-concept-black-response-native-tt-challenge-v1",
         "formal_study":"C3X 0.14","internal_checkpoint_not_formal_substage":True,
         "source_json_sha256":SOURCE_SHA,"source_groups":16,"legal_world_count":60,
         "total_real_native_engine_processes":360,"world_cold_repeat_cases":120,
         "cold_exact_pairs_out_of60":cold,"original_vs_OFF_sham_exact_out_of120":len(cells),
         "concept_change_source_groups":len(changed_worlds),
         "history_vs_FEN_source_groups_with_different_OFF_engine_outputs":histories_differ,
         "all_game_concept_and_mechanism_details":summaries,
         "concept_change_vs_original_treatment_sensitivity_cp":stats(changed_vs_original),
         "semantic_sham_vs_original_treatment_sensitivity_cp":stats(sham_vs_original),
         "concept_change_vs_sham_treatment_sensitivity_cp":stats(contrasts),
         "all_cells":cells,"P1_sealed_holdout_accessed":False,
         "chess_domain_mediation_causally_identified":False,
         "ambiguity":["Black legal move changes many chess properties, not just one measured concept.","FEN-only input lacks game repetition history, even when full six-field position matches.","TT suppression is a family intervention that may change node workload and internal depth.","Cold restarts are technical controls, not independent game groups.","No claim of structural pawn-causality or human learning utility from this study."]}
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2)+"\n")
    print("C3X014_LEGAL_CONCEPT_NATIVE_MEDIATION_CHALLENGE_VERDICT",json.dumps({
        "source_groups":len(summaries),"concept_targets":len(changed_worlds),
        "worlds":60,"engine_processes":360,"cold_pairs":cold,
        "history_FEN_OFF_outputs_differ_groups":histories_differ,
        "concept_minus_played":out["concept_change_vs_original_treatment_sensitivity_cp"],
        "sham_minus_played":out["semantic_sham_vs_original_treatment_sensitivity_cp"],
        "changed_minus_sham":out["concept_change_vs_sham_treatment_sensitivity_cp"]}),flush=True)
if __name__=="__main__":main()
