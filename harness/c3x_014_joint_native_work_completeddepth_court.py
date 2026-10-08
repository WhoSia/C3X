#!/usr/bin/env python3
"""C3X 0.14 all-sixteen-games actual work/completion joint search court.

Three source-frozen node limits. Real native post-search completedDepth logging.
The source group is 16 developmental chess games, not 192 independent cases.
"""
import argparse,hashlib,json,math,os,re,subprocess
from pathlib import Path
import chess

PARENT_SHA="37d6b3bde44e971ee88ae5fbababd63ba88980ce6b48e0bfa80234cebccdbdf1"
RATIOS=(("LOW",0.8),("BASE",1.0),("HIGH",1.2))
REPEATS=(1,2)
MODES=("OFF","MAIN")
TOL=0.02

def hashbytes(b):return hashlib.sha256(b).hexdigest()
def cap(n,scale):
    return max(1024,math.floor(n*scale) if scale<1 else math.ceil(n*scale))

def run(binary,fen,pair,nodes,mode):
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
                if not line:raise RuntimeError("Native engine EOF while "+prefix)
                lines.append(line.rstrip())
                if line.startswith(prefix):return
            raise RuntimeError("Excessive engine output")
        send("uci");till("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16","setoption name MultiPV value 2",
             "ucinewgame","isready")
        till("readyok")
        send("position fen "+fen,"go nodes "+str(nodes)+" searchmoves "+" ".join(pair))
        till("bestmove ");send("quit")
        if p.wait(timeout=15):raise RuntimeError("SF16 exited nonzero")
    native=[s for s in lines if s.startswith("info string c3x014_completion_probe ")]
    tt=[s for s in lines if s.startswith("info string c3x_p8_ep9 ")]
    if len(native)!=1 or len(tt)!=1:raise RuntimeError("Native telemetry missing or duplicate")
    detail={k:int(v) for k,v in (z.split("=",1) for z in native[0].split()[3:])}
    telemetry={k:int(v) for k,v in (z.split("=",1) for z in tt[0].split()[3:])}
    assert set(detail)=={"best_completed","best_root_depth","main_completed"}
    assert detail["best_completed"]==detail["main_completed"] and 0<=detail["best_completed"]<=detail["best_root_depth"]
    assert telemetry["mode"]=={"OFF":0,"MAIN":1}[mode]
    assert telemetry["q_blocked"]==0
    if mode=="OFF":assert telemetry["main_blocked"]==0
    pv={};max_nodes=0
    for line in lines:
        if not line.startswith("info depth "):continue
        dep=re.search(r"\bdepth (\d+)",line);num=re.search(r"\bnodes (\d+)",line)
        if num:max_nodes=max(max_nodes,int(num.group(1)))
        if not(dep and " multipv " in line and " pv " in line):continue
        rank=re.search(r"\bmultipv (\d+)",line)
        score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",line)
        if not(rank and score):continue
        move=line.split(" pv ",1)[1].split()[0]
        if move not in pair:continue
        pv[(int(dep.group(1)),int(rank.group(1)))]={
          "move":move,"score_kind":score.group(1),"score_white":int(score.group(2)),
          "bound":score.group(3) or "exact_reported"}
    both=[d for d,rk in pv if rk==1 and (d,2) in pv]
    maxPV=max(both,default=None)
    def pair_at(depth):
        if depth is None or (depth,1) not in pv or (depth,2) not in pv:return None
        x,y=pv[depth,1],pv[depth,2]
        if {x["move"],y["move"]}!=set(pair):return None
        if any(z["score_kind"]!="cp" or z["bound"]!="exact_reported" for z in (x,y)):return None
        bymove={z["move"]:z["score_white"] for z in (x,y)}
        return bymove[pair[0]]-bymove[pair[1]]
    best=[s.split()[1] for s in lines if s.startswith("bestmove ")]
    assert len(best)==1 and best[0] in pair
    return {"native_true_completed_depth":detail["best_completed"],
            "native_last_root_depth_started":detail["best_root_depth"],
            "two_PV_max_reported_depth":maxPV,
            "gap_at_native_completed_depth_cp":pair_at(detail["best_completed"]),
            "gap_at_max_two_PV_reported_depth_cp":pair_at(maxPV),
            "score_at_completed_depth_available":pair_at(detail["best_completed"]) is not None,
            "UCI_bestmove":best[0],"nodes_reported_last":max_nodes,
            "main_bound_early_returns_blocked":telemetry["main_blocked"],
            "native_trace":detail,
            "TT_trace":telemetry}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old-node-panel",required=True)
    ap.add_argument("--sf16",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    raw=Path(a.old_node_panel).read_bytes()
    if hashbytes(raw)!=PARENT_SHA:raise SystemExit("PARENT_SOURCE_HASH_CHANGED")
    x=json.loads(raw)
    assert x["schema"]=="c3x-014-p2-node-cap-order-hash-postdiscovery-actual-native-court-v1"
    assert len(x["cells"])==128 and x["source_group_count"]==16 and not x["P1_heldout_opened"]
    roots=[c for c in x["cells"] if c["original_order"] and c["hash_mib"]==16 and c["repeat"]==1]
    assert len(roots)==16 and len({c["group"] for c in roots})==16
    cells=[];baseline_match=0
    for i,root in enumerate(roots,1):
        for label,mult in RATIOS:
            requested=cap(root["node_cap"],mult)
            for repeat in REPEATS:
                outcomes={}
                for mode in MODES:
                    z=run(a.sf16,root["fen"],root["pair"],requested,mode)
                    outcomes[mode]=z
                    if label=="BASE":
                        orig=root["mode_off"] if mode=="OFF" else root["mode_main"]
                        same=(z["UCI_bestmove"]==orig["bestmove"] and
                              z["two_PV_max_reported_depth"]==orig["max_completed_both_pv_depth"] and
                              z["gap_at_max_two_PV_reported_depth_cp"]==orig["signed_white_cp_gap"] and
                              z["nodes_reported_last"]==orig["last_nodes_seen"])
                        baseline_match+=int(same)
                        if not same:raise RuntimeError("NATIVE_PROBE_CHANGES_PARENT_OUTPUT "+str((root["round"],mode,repeat)))
                A=outcomes["OFF"];B=outcomes["MAIN"]
                cd_same=A["native_true_completed_depth"]==B["native_true_completed_depth"]
                nodes_ratio=abs(A["nodes_reported_last"]-B["nodes_reported_last"])/max(A["nodes_reported_last"],B["nodes_reported_last"],1)
                near=cd_same and nodes_ratio<=TOL
                g0=A["gap_at_native_completed_depth_cp"];g1=B["gap_at_native_completed_depth_cp"]
                strict=(g0 is not None and g1 is not None and g0*g1<0)
                label_changed=A["UCI_bestmove"]!=B["UCI_bestmove"]
                row={"source_group":root["group"],"source_round":root["round"],"fen":root["fen"],
                     "pair":root["pair"],"original_source_node_cap":root["node_cap"],
                     "requested_node_cap":requested,"node_cap_ratio_label":label,
                     "cold_repeat":repeat,"off":A,"main":B,
                     "actual_work_discrepancy_fraction":nodes_ratio,
                     "same_true_native_completed_depth":cd_same,
                     "joint_near_work_and_completed_depth":near,
                     "native_completed_depth_cp_pair_valid":g0 is not None and g1 is not None,
                     "strict_native_completion_cp_gap_inversion":strict,
                     "UCI_bestmove_label_changed":label_changed,
                     "scores_tie_at_native_completed_depth":g0 is not None and g1 is not None and (g0==0 or g1==0)}
                cells.append(row)
                print("C3X014_JOINT_WORK_CELL",i,root["round"],label,repeat,
                      "depths",A["native_true_completed_depth"],B["native_true_completed_depth"],
                      "nodes",A["nodes_reported_last"],B["nodes_reported_last"],
                      "gap_at_completed",g0,g1,"near",near,"strict",strict,
                      "choice",label_changed,flush=True)
    assert len(cells)==192 and baseline_match==64
    cold=0
    for root in roots:
        for label,_ in RATIOS:
            z=[v for v in cells if v["source_group"]==root["group"] and v["node_cap_ratio_label"]==label]
            assert len(z)==2
            if all(z[0][k]==z[1][k] for k in ("off","main",
                  "joint_near_work_and_completed_depth","strict_native_completion_cp_gap_inversion",
                  "UCI_bestmove_label_changed")):cold+=1
    assert cold==48,("COLD_RUNS_NOT_STABLE",cold)
    counts={}
    for label,_ in RATIOS:
        sample=[v for v in cells if v["node_cap_ratio_label"]==label and v["cold_repeat"]==1]
        counts[label]={
            "source_groups":len(sample),
            "same_native_completed_depth":sum(v["same_true_native_completed_depth"] for v in sample),
            "joint_near_work_completed_depth":sum(v["joint_near_work_and_completed_depth"] for v in sample),
            "native_completed_cp_pair_scores_available":sum(v["native_completed_depth_cp_pair_valid"] for v in sample),
            "strict_native_complete_depth_cp_gap_inversions":sum(v["strict_native_completion_cp_gap_inversion"] for v in sample),
            "UCI_bestmove_changes":sum(v["UCI_bestmove_label_changed"] for v in sample),
            "joint_near_work_strict_sign_inversions":sum(v["joint_near_work_and_completed_depth"] and v["strict_native_completion_cp_gap_inversion"] for v in sample)}
    r96=[v for v in cells if v["source_round"]=="96.1" and v["cold_repeat"]==1]
    result={"schema":"c3x-014-joint-work-and-native-completion-response-court-v1",
            "formal_research_stage":"C3X 0.14","internal_work_only":True,
            "source_reuse":"P2 previously exposed development games; post-discovery outcomes only",
            "old_node_parent_sha256":PARENT_SHA,
            "SF16_binary_sha256":hashbytes(Path(a.sf16).read_bytes()),
            "source_group_count":16,"real_engine_process_count":384,
            "paired_off_MAIN_cells":192,"two_cold_repeats_same_outcome_by_game_cap_out_of48":cold,
            "original_base_cap_native_probe_did_not_alter_UCI_output_out_of64":baseline_match,
            "requested_cap_grid":["80_percent_previous_cap","100_percent_previous_cap","120_percent_previous_cap"],
            "equal_native_completion_plus_nodes_within_2_percent_is_posttreatment_descriptive_only":True,
            "node_gap_criterion_fraction":TOL,"first_cold_group_result_by_cap":counts,
            "previously_discovered_round96_first_cold":r96,
            "actual_cases":cells,
            "sealed_holdout_accessed":False,
            "causal_chess_mediation_established":False,
            "cannot_identify_pure_TT_direct_effect_by_posttreatment_conditioning":True,
            "warning":["Same requested node cap is not achieved exact node equivalence.",
                       "Comparison with same achieved completedDepth AND near nodes is post-treatment conditioning, not direct-effect identification.",
                       "At completed depth, both rank PV values can be reported but their numerical meaning remains depth-limited SF16 cp.",
                       "UCI bestmove may follow an incomplete last search iteration; distinct from last complete-depth scores.",
                       "All games and thresholds are after P2 discoveries, not new independent holdout."]
           }
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+"\n")
    print("C3X014_JOINT_BUDGET_VERDICT",json.dumps({"counts":counts,"total":len(cells),
          "base_match":baseline_match,"cold":cold,"round96":[{"cap":z["node_cap_ratio_label"],
          "depth_OFF":z["off"]["native_true_completed_depth"],"depth_MAIN":z["main"]["native_true_completed_depth"],
          "cp_gap_OFF":z["off"]["gap_at_native_completed_depth_cp"],
          "cp_gap_MAIN":z["main"]["gap_at_native_completed_depth_cp"],"strict":z["strict_native_completion_cp_gap_inversion"],
          "near":z["joint_near_work_and_completed_depth"]} for z in r96]}),flush=True)
if __name__=="__main__":main()
