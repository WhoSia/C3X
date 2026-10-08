#!/usr/bin/env python3
"""C3X 0.14: native SF16 true completedDepth versus printed MultiPV depth.

All 16 games are known P2 development sources. P1 holdout is never accessed.
The source C++ probe runs only after search finishes, before UCI bestmove.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
STRESS_SHA="37d6b3bde44e971ee88ae5fbababd63ba88980ce6b48e0bfa80234cebccdbdf1"

def sha(b):return hashlib.sha256(b).hexdigest()

def uci(binary,fen,pair,nodes,mode):
    board=chess.Board(fen)
    assert board.is_valid() and all(chess.Move.from_uci(m) in board.legal_moves for m in pair)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    lines=[]
    with subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
       stderr=subprocess.STDOUT,bufsize=1,text=True,env=env) as p:
        def send(*cmd):p.stdin.write("\n".join(cmd)+"\n");p.stdin.flush()
        def until(prefix):
            for _ in range(150000):
                z=p.stdout.readline()
                if not z:raise RuntimeError("UCI engine ended during "+prefix)
                lines.append(z.rstrip())
                if z.startswith(prefix):return
            raise RuntimeError("UCI response did not finish")
        send("uci");until("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        until("readyok")
        send("position fen "+fen,"go nodes "+str(nodes)+" searchmoves "+" ".join(pair))
        until("bestmove ");send("quit")
        assert p.wait(timeout=10)==0
    raw=[z for z in lines if z.startswith("info string c3x014_completion_probe ")]
    if len(raw)!=1:raise RuntimeError("Missing native completedDepth logger "+repr(raw))
    field={k:int(v) for k,v in (x.split("=",1) for x in raw[0].split()[3:])}
    if not set(field)=={"best_completed","best_root_depth","main_completed"}:
        raise RuntimeError("native completion field mismatch")
    if field["best_completed"]!=field["main_completed"]:
        raise RuntimeError("Threads1 best thread different completion")
    if not 0<=field["best_completed"]<=field["best_root_depth"]:
        raise RuntimeError("Native completion invariant")
    uci_bests=[z.split()[1] for z in lines if z.startswith("bestmove ")]
    assert len(uci_bests)==1
    depth_rank={}
    last_nodes=0
    for z in lines:
        if not z.startswith("info depth "):continue
        d=re.search(r"\bdepth (\d+)",z);nm=re.search(r"\bnodes (\d+)",z)
        if nm:last_nodes=max(last_nodes,int(nm.group(1)))
        if not(d and " multipv " in z and " pv " in z):continue
        rk=re.search(r"\bmultipv (\d+)",z)
        sc=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",z)
        if not(rk and sc):continue
        move=z.split(" pv ",1)[1].split()[0]
        if move not in pair:continue
        depth_rank[(int(d.group(1)),int(rk.group(1)))]=(move,sc.group(1),int(sc.group(2)),sc.group(3))
    common=[d for d,k in depth_rank if k==1 and (d,2) in depth_rank]
    common_max=max(common,default=None)
    gap=None
    if common_max is not None:
        a,b=depth_rank[(common_max,1)],depth_rank[(common_max,2)]
        bymove={t[0]:t for t in (a,b)}
        if set(bymove)==set(pair) and all(t[1]=="cp" and t[3] is None for t in (a,b)):
            gap=bymove[pair[0]][2]-bymove[pair[1]][2]
    ttrows=[z for z in lines if z.startswith("info string c3x_p8_ep9 ")]
    assert len(ttrows)==1
    tt={k:int(v) for k,v in (t.split("=",1) for t in ttrows[0].split()[3:])}
    assert tt["mode"]=={"OFF":0,"MAIN":1}[mode]
    assert (mode!="OFF" or tt["main_blocked"]==0) and tt["q_blocked"]==0
    return {"mode":mode,"native":field,"max_pv_reported_rank12_depth":common_max,
            "reported_gap_white_cp":gap,
            "pv_reported_depth_is_native_completed":common_max==field["best_completed"],
            "uci_bestmove":uci_bests[0],"actual_final_nodes":last_nodes,
            "blocked_MAIN":tt["main_blocked"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stress-parent",required=True);ap.add_argument("--native-binary",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    raw=Path(a.stress_parent).read_bytes()
    if sha(raw)!=STRESS_SHA:raise SystemExit("SOURCE_STRESS_SHA_MISMATCH")
    parent=json.loads(raw)
    assert parent["schema"]=="c3x-014-p2-node-cap-order-hash-postdiscovery-actual-native-court-v1"
    assert parent["source_group_count"]==16 and len(parent["cells"])==128
    assert not parent["P1_heldout_opened"]
    selected=[x for x in parent["cells"] if x["original_order"] and x["hash_mib"]==16 and x["repeat"]==1]
    assert len(selected)==16 and len({x["group"] for x in selected})==16
    allcases=[]
    for ix,src in enumerate(selected,1):
        for cold in (1,2):
            for mode in ("OFF","MAIN"):
                panel=uci(a.native_binary,src["fen"],src["pair"],src["node_cap"],mode)
                original=src["mode_off"] if mode=="OFF" else src["mode_main"]
                matches=(panel["uci_bestmove"]==original["bestmove"]
                         and panel["reported_gap_white_cp"]==original["signed_white_cp_gap"]
                         and panel["max_pv_reported_rank12_depth"]==original["max_completed_both_pv_depth"]
                         and panel["actual_final_nodes"]==original["last_nodes_seen"])
                row={"source_group":src["group"],"source_round":src["round"],"repeat":cold,
                    "fixed_source_node_cap":src["node_cap"],"legal_pair":src["pair"],
                    "matches_original_previous_native_PV_and_nodes":matches,**panel}
                allcases.append(row)
                print("P3_NATIVE_COMPLETION",ix,src["round"],mode,cold,
                    "native_completed",panel["native"]["best_completed"],
                    "last_root_started",panel["native"]["best_root_depth"],
                    "bothPV_marked",panel["max_pv_reported_rank12_depth"],
                    "matches_original",matches,flush=True)
    assert len(allcases)==64
    cold_repro=0
    for src in selected:
        for mode in ("OFF","MAIN"):
            records=[x for x in allcases if x["source_group"]==src["group"] and x["mode"]==mode]
            assert len(records)==2
            keys=("native","max_pv_reported_rank12_depth","uci_bestmove","actual_final_nodes","reported_gap_white_cp","blocked_MAIN")
            if all(records[0][k]==records[1][k] for k in keys):cold_repro+=1
    mismatch=sum(x["native"]["best_completed"]!=x["max_pv_reported_rank12_depth"] for x in allcases)
    nmatch=sum(x["matches_original_previous_native_PV_and_nodes"] for x in allcases)
    cases={}
    for rnd in ("12.1","96.1","95.1"):
        sample=[x for x in allcases if x["source_round"]==rnd and x["repeat"]==1]
        assert len(sample)==2
        cases[rnd]={x["mode"]:{
            "actual_native_completedDepth":x["native"]["best_completed"],
            "last_native_rootDepth_started":x["native"]["best_root_depth"],
            "max_PV_reported_two_ranks":x["max_pv_reported_rank12_depth"],
            "cp_gap":x["reported_gap_white_cp"],
            "bestmove":x["uci_bestmove"],
            "node_cap":x["fixed_source_node_cap"],
            "nodes_seen":x["actual_final_nodes"]
         } for x in sample}
    out={"schema":"c3x-014-native-stockfish16-completed-depth-vs-UCI-PV-court-v1",
         "one_formal_stage":"C3X 0.14","technical_pass":"P3 internal checkpoint",
         "no_chess_concept_inference":True,"parent_node_stress_sha256":STRESS_SHA,
         "source_games":16,"engine_runs":64,"cold_pair_equal_out_of32":cold_repro,
         "exact_same_parent_stress_uci_output_count_out_of64":nmatch,
         "native_completedDepth_disagrees_with_max_two_PV_reported_depth_out_of64":mismatch,
         "first_cold_known_discoveries":cases,"all_runs":allcases,
         "validity":["The native logger executes only after engine search exit, not during search.",
          "Reported MultiPV score lines may be stale during aborted aspiration/re-search.",
          "A printed UCI PV depth is not a certificate that the entire root MultiPV iteration completed.",
          "Node budget is still nominal: two modes can do different work.",
          "Same 16 development sources, P1 holdout untouched, no new chess concept causation"]}
    file=Path(a.out);file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps(out,indent=2)+"\n")
    print("P3_NATIVE_COMPLETED_DEPTH_VERDICT",json.dumps({
        "run_n":len(allcases),"cold_pairs":cold_repro,"parent_outputs_exact":nmatch,
        "PV_vs_true_native_mismatch":mismatch,"known":cases}),flush=True)
    if cold_repro!=32 or nmatch!=64:
        raise SystemExit("P3_NATIVE_PROBE_FAIL_CLOSED_REPRO_OR_SOURCE_BASELINE_MISMATCH")
if __name__=="__main__":main()
