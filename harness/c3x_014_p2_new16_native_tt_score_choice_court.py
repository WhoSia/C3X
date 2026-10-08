#!/usr/bin/env python3
"""C3X 0.14 P2: frozen sixteen-game native Stockfish16 TT cutoff response court.

This is a continuation of original P1 EP9 native source code. Every source game is
determined before any baseline scores. MultiPV bound flags and root work are
recorded; mate and bound-marked scores are censored from numeric cp comparisons.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
SOURCE_SHA="cb879eaa14bcbf3896c4d069dcb1cf543135c68c5b1fa0ea2eab942613332eeb"
GROUPS=16
DEPTHS=(8,12)
REPEATS=(1,2)
MASKS=("MAIN","QSEARCH","BOTH")

def h(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()

def run(binary,fen,pair,depth,mode):
    b=chess.Board(fen)
    assert b.is_valid() and b.turn==chess.WHITE
    assert len(pair)==2 and all(chess.Move.from_uci(m) in b.legal_moves for m in pair)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    for k in ("C3X_P8_EP10_SITE","C3X_P8_EP10_ORDINAL","C3X_P8_EP11_TARGET_KEY"):
        env.pop(k,None)
    lines=[]
    with subprocess.Popen([str(binary)],env=env,text=True,bufsize=1,
             stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) as p:
        def send(*commands):p.stdin.write("\n".join(commands)+"\n");p.stdin.flush()
        def wait(prefix):
            for _ in range(100000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("UCI engine EOF "+str(lines[-10:]))
                lines.append(line.rstrip())
                if line.startswith(prefix):return
            raise RuntimeError("Too many UCI lines")
        send("uci");wait("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        wait("readyok")
        send("position fen "+fen,"go depth "+str(depth)+" searchmoves "+" ".join(pair))
        wait("bestmove ");send("quit")
        assert p.wait(timeout=15)==0
    infos={}
    for s in lines:
        if not(s.startswith("info depth ") and " multipv " in s and " pv " in s):continue
        dep=re.search(r"\bdepth (\d+)\b",s)
        if dep is None or int(dep.group(1))!=depth:continue
        m=re.search(r"\bmultipv (\d+)\b",s)
        sc=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",s)
        nd=re.search(r"\bnodes (\d+)\b",s)
        if m is None or sc is None or nd is None:continue
        pv=s.split(" pv ",1)[1].split()
        move=pv[0];assert chess.Move.from_uci(move) in b.legal_moves
        infos[int(m.group(1))]={
         "root_move":move,"score_kind":sc.group(1),
         "score_value_white_perspective":int(sc.group(2)),
         "score_bound_flag":sc.group(3) or "exact_reported",
         "nodes":int(nd.group(1)),"pv":pv[:16]}
    if set(infos)!={1,2} or {z["root_move"] for z in infos.values()}!=set(pair):
        raise ValueError("Missing matching final MultiPV pair "+str(infos))
    best=[s.split()[1] for s in lines if s.startswith("bestmove ")]
    assert best==[infos[1]["root_move"]]
    native=[s for s in lines if s.startswith("info string c3x_p8_ep9 ")]
    assert len(native)==(0 if mode=="CLEAN" else 1)
    tel={}
    if native:
        tel={k:int(v) for k,v in (x.split("=",1) for x in native[0].split()[3:])}
        assert tel["mode"]=={"OFF":0,"MAIN":1,"QSEARCH":2,"BOTH":3}[mode]
        if mode=="OFF":assert tel["main_blocked"]==0 and tel["q_blocked"]==0
        if mode=="MAIN":assert tel["q_blocked"]==0
        if mode=="QSEARCH":assert tel["main_blocked"]==0
        if mode=="BOTH":assert tel["main_taken"]==0 and tel["q_taken"]==0
    vals={v["root_move"]:v for v in infos.values()}
    typed=(vals[pair[0]]["score_kind"]=="cp" and vals[pair[1]]["score_kind"]=="cp" and
           all(v["score_bound_flag"]=="exact_reported" for v in vals.values()))
    gap=(vals[pair[0]]["score_value_white_perspective"]-
         vals[pair[1]]["score_value_white_perspective"]) if typed else None
    return {"bestmove":best[0],"final_MultiPV":infos,
            "signed_white_cp_gap":gap,
            "numeric_gap_censored":not typed,
            "tt":tel}
def eq(x):return {k:x[k] for k in ("bestmove","final_MultiPV","signed_white_cp_gap","numeric_gap_censored")}

def margin(g):
    if g is None:return "MATE_OR_BOUND"
    return "NEAR" if abs(g)<=25 else "MID" if abs(g)<=60 else "FAR"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--frozen-source",required=True)
    ap.add_argument("--clean",required=True)
    ap.add_argument("--ep9",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if h(a.frozen_source)!=SOURCE_SHA:raise SystemExit("P2_FROZEN_COHORT_SHA_FAIL")
    data=json.loads(Path(a.frozen_source).read_bytes())
    assert data["schema"]=="c3x-014-p2-official-s29-score-blind-independent-16-source-groups-v1"
    assert data["engine_scores_read"] is False and not data["hidden_p1_holdout_game_details_read"]
    gs=data["selected_16_game_groups"]
    assert len(gs)==16 and len({x["opening_group_hash"] for x in gs})==16
    cases=[]
    for ix,g in enumerate(gs):
        for dep in DEPTHS:
            for repeat in REPEATS:
                fen=g["full_root_fen"];pair=g["candidate_pair_uci"]
                baseline=run(a.clean,fen,pair,dep,"CLEAN")
                sham=run(a.ep9,fen,pair,dep,"OFF")
                control=eq(baseline)==eq(sham)
                arms={}
                if control:
                    for mode in MASKS:arms[mode]=run(a.ep9,fen,pair,dep,mode)
                cell={"group":g["opening_group_hash"],"game":g["source_game_id"],
                      "round":g["source_headers"]["Round"],"fen":fen,"pair":pair,
                      "depth":dep,"repeat":repeat,"clean":baseline,"off":sham,
                      "sham_exact":control,"arms":arms,
                      "margin_bin":margin(sham["signed_white_cp_gap"])}
                if control:
                    cell["choice_flip"]={mode:arms[mode]["bestmove"]!=sham["bestmove"]
                                          for mode in MASKS}
                    cell["gap_shift_white_cp"]={
                        mode:(arms[mode]["signed_white_cp_gap"]-sham["signed_white_cp_gap"])
                        if (arms[mode]["signed_white_cp_gap"] is not None and
                            sham["signed_white_cp_gap"] is not None) else None
                        for mode in MASKS}
                    cell["native_blocked"]={mode:{"main":arms[mode]["tt"]["main_blocked"],
                                                 "qsearch":arms[mode]["tt"]["q_blocked"]}
                                               for mode in MASKS}
                cases.append(cell)
                print("P2_ACTUAL_GAME",ix+1,g["source_headers"]["Round"],"d",dep,"cold",repeat,
                    "sham",control,"baseline_gap",sham["signed_white_cp_gap"],
                    "main_gap",arms.get("MAIN",{}).get("signed_white_cp_gap"),
                    "base_best",sham["bestmove"],"main_best",arms.get("MAIN",{}).get("bestmove"),flush=True)
    assert len(cases)==64
    all_sham=all(x["sham_exact"] for x in cases)
    cold={}
    for mode in ("CLEAN","OFF")+MASKS:
        same=0
        for grp in gs:
            for dep in DEPTHS:
                first,second=[x for x in cases if x["group"]==grp["opening_group_hash"] and x["depth"]==dep]
                aa=first["clean"] if mode=="CLEAN" else first["off"] if mode=="OFF" else first["arms"].get(mode)
                bb=second["clean"] if mode=="CLEAN" else second["off"] if mode=="OFF" else second["arms"].get(mode)
                if aa is not None and bb is not None and eq(aa)==eq(bb):same+=1
        cold[mode]=same
    depth12_group_main=[]
    for g in gs:
        rows=[x for x in cases if x["group"]==g["opening_group_hash"] and x["depth"]==12]
        depth12_group_main.append(all(x.get("choice_flip",{}).get("MAIN",False) for x in rows))
    firsts=[x for x in cases if x["repeat"]==1 and x["depth"]==12]
    bybin={k:{"groups":sum(z["margin_bin"]==k for z in firsts),
              "main_flip_both_cold":sum(x for x,z in zip(depth12_group_main,firsts) if x and z["margin_bin"]==k)}
           for k in ("NEAR","MID","FAR","MATE_OR_BOUND")}
    flips={mode:sum(x.get("choice_flip",{}).get(mode,False) for x in cases) for mode in MASKS}
    gap_nonnull={mode:[x["gap_shift_white_cp"][mode] for x in cases
                       if x.get("gap_shift_white_cp",{}).get(mode) is not None] for mode in MASKS}
    summary={"schema":"c3x-014-p2-real-new16-group-typed-native-tt-score-choice-court-v1",
       "scientific_status":"PRESELECTED_SOURCE_GAME_DEVELOPMENT__NO_STRATEGIC_CAUSATION",
       "upstream_official_source":data["official_source"],
       "source_cohort_sha256":SOURCE_SHA,
       "engine":"official Stockfish16 sf_16 original and EP9 native TT return suppression",
       "engine_sha256":{"clean":h(a.clean),"ep9":h(a.ep9)},
       "independent_game_groups":16,"games_share_tcec_ecology":True,
       "p1_four_holdout_games_opened":False,
       "depths":list(DEPTHS),"cold_repeats":len(REPEATS),
       "cases":cases,"clean_vs_sham_exact_all":all_sham,
       "cold_pair_exact_by_arm_out_of_32":cold,
       "first_choice_flips_by_arm_out_of_64_dependent_cells":flips,
       "depth12_distinct_game_groups_both_cold_main_flip_out_of16":sum(depth12_group_main),
       "baseline_depth12_margin_strata":bybin,
       "numeric_cp_gap_shift_observations_by_arm":{
           k:{"count":len(v),"nonnull_changes":sum(x!=0 for x in v),
              "mean_absolute_shift_cp":sum(abs(x) for x in v)/len(v) if v else None,
              "max_absolute_shift_cp":max((abs(x) for x in v),default=None)}
           for k,v in gap_nonnull.items()},
       "authority_boundaries":[
           "each cold process is dependent technical repeat, the independent sample unit is the source opening group",
           "same depth does not match nodes/work across native arms; different search budget may mediate observed score changes",
           "UCI bound marked or mate scores cannot be used for exact numeric cp gap",
           "the TT family early-return intervention is not a board-pawn/strategy causal intervention",
           "no holdout or independent engine provided chess semantic causal validation"],
       "causal_chess_feature_identified":False}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2)+"\n")
    print("P2_REAL_NATIVE_COURT_VERDICT",json.dumps({
        "sham":all_sham,"group_n":16,"case_n":len(cases),"cold":cold,
        "flips":flips,"bothcold_depth12_MAIN":sum(depth12_group_main),
        "margin":bybin,"gap_shifts":summary["numeric_cp_gap_shift_observations_by_arm"]}),flush=True)
    if not all_sham or not all(x==32 for x in cold.values()):
        raise SystemExit("P2_INVALID_SHAM_OR_COLD_DETERMINISM")
if __name__=="__main__":main()
