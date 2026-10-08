#!/usr/bin/env python3
"""P2 exploratory ALL-16 node-limit root-order/hash TT intervention stress.

Parent group/depth outcome has already been observed; this is NEVER new heldout.
Exactly the same original engine EP9 binary with OFF/MAIN env differences.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
PARENT_SHA="0fd87345c9cc4b0e23f8fac6c669ec328254178da424268303e99ee6159f81e3"
NODES_MIN=1024
MASKS=("OFF","MAIN")
HASHES=(16,64)
REPEATS=(1,2)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def uci(binary,fen,pair,node_cap,hash_mib,mode):
    b=chess.Board(fen)
    assert b.is_valid() and b.turn==chess.WHITE
    assert set(chess.Move.from_uci(x) for x in pair).issubset(set(b.legal_moves))
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    lines=[]
    with subprocess.Popen([binary],env=env,text=True,bufsize=1,
             stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) as p:
        def send(*cmd):p.stdin.write("\n".join(cmd)+"\n");p.stdin.flush()
        def wait(prefix):
            for _ in range(150000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("SF16 UCI EOF while "+prefix)
                lines.append(line.rstrip())
                if line.startswith(prefix):return
            raise RuntimeError("Too many UCI lines")
        send("uci");wait("uciok")
        send("setoption name Threads value 1",
             "setoption name Hash value "+str(hash_mib),
             "setoption name MultiPV value 2","ucinewgame","isready")
        wait("readyok")
        send("position fen "+fen,
             "go nodes "+str(node_cap)+" searchmoves "+" ".join(pair))
        wait("bestmove ");send("quit")
        assert p.wait(timeout=10)==0
    all_scores={}
    last_total_nodes=0
    for line in lines:
        if not line.startswith("info depth "):continue
        dm=re.search(r"\bdepth (\d+)",line); nm=re.search(r"\bnodes (\d+)",line)
        if nm:last_total_nodes=max(last_total_nodes,int(nm.group(1)))
        if not(dm and " multipv " in line and " pv " in line):continue
        mm=re.search(r"\bmultipv (\d+)",line)
        ss=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",line)
        if not(mm and ss):continue
        pv=line.split(" pv ",1)[1].split()
        root=pv[0]
        if root not in pair:continue
        all_scores[(int(dm.group(1)),int(mm.group(1)))]={
           "move":root,"kind":ss.group(1),"value_white":int(ss.group(2)),
           "bound":ss.group(3) or "exact_reported",
           "nodes":int(nm.group(1)) if nm else None,"pv":pv[:12]}
    depths=sorted(set(k[0] for k in all_scores))
    common=[dep for dep in depths if (dep,1) in all_scores and (dep,2) in all_scores]
    bestmove=[line.split()[1] for line in lines if line.startswith("bestmove ")]
    assert len(bestmove)==1 and bestmove[0] in pair
    record=[line for line in lines if line.startswith("info string c3x_p8_ep9 ")]
    assert len(record)==1
    tt={k:int(v) for k,v in (z.split("=",1) for z in record[0].split()[3:])}
    assert tt["mode"]=={"OFF":0,"MAIN":1}[mode]
    if mode=="OFF":assert tt["main_blocked"]==0 and tt["q_blocked"]==0
    else:assert tt["q_blocked"]==0
    output={"bestmove":bestmove[0],"last_nodes_seen":last_total_nodes,
            "same_config_node_limit":node_cap,"max_completed_both_pv_depth":max(common,default=None),
            "full_depth_completed":bool(common),
            "native_tt_telemetry":tt}
    if common:
        dep=max(common)
        ranks={"1":all_scores[dep,1],"2":all_scores[dep,2]}
        output["last_complete_two_root_ranked"]=ranks
        vals={v["move"]:v for v in ranks.values()}
        if len(vals)!=2:raise ValueError("Bad complete MultiPV ranking")
        cp=all(v["kind"]=="cp" and v["bound"]=="exact_reported" for v in vals.values())
        output["signed_white_cp_gap"]=vals[pair[0]]["value_white"]-vals[pair[1]]["value_white"] if cp else None
    else:
        output["last_complete_two_root_ranked"]=None
        output["signed_white_cp_gap"]=None
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--parent-panel",required=True)
    ap.add_argument("--ep9",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if sha(a.parent_panel)!=PARENT_SHA:raise SystemExit("P2_PARENT_EVIDENCE_SHA_FAIL")
    parent=json.loads(Path(a.parent_panel).read_bytes())
    assert parent["schema"]=="c3x-014-p2-real-new16-group-typed-native-tt-score-choice-court-v1"
    assert parent["clean_vs_sham_exact_all"] and len(parent["cases"])==64
    assert not parent["p1_four_holdout_games_opened"]
    selected=[x for x in parent["cases"] if x["depth"]==12 and x["repeat"]==1]
    assert len(selected)==16
    cases=[]
    for i,src in enumerate(selected,1):
        cap=max(NODES_MIN,int(src["clean"]["final_MultiPV"]["1"]["nodes"]))
        pair=src["pair"]
        for order in (pair,list(reversed(pair))):
            for h in HASHES:
                for repeat in REPEATS:
                    a0=uci(a.ep9,src["fen"],order,cap,h,"OFF")
                    a1=uci(a.ep9,src["fen"],order,cap,h,"MAIN")
                    gap0=a0["signed_white_cp_gap"];gap1=a1["signed_white_cp_gap"]
                    sign_flip=(gap0 is not None and gap1 is not None and gap0*gap1<0)
                    case={"source_game_id":src["game"],"group":src["group"],"round":src["round"],
                          "fen":src["fen"],"original_order":order==pair,
                          "pair":order,"hash_mib":h,"repeat":repeat,
                          "node_cap":cap,"mode_off":a0,"mode_main":a1,
                          "UCI_choice_changed":a0["bestmove"]!=a1["bestmove"],
                          "strict_signed_gap_inverted":sign_flip,
                          "ties_after_intervention":gap1==0 if gap1 is not None else None,
                          "fully_reported_common_rank_depth":a0["max_completed_both_pv_depth"] is not None and a1["max_completed_both_pv_depth"] is not None}
                    cases.append(case)
                    print("P2_NODE_CAP_STRESS",i,src["round"],"N",cap,
                          "order",order,"hash",h,"repeat",repeat,
                          "depths",a0["max_completed_both_pv_depth"],a1["max_completed_both_pv_depth"],
                          "best",a0["bestmove"],a1["bestmove"],"gap",gap0,gap1,flush=True)
    assert len(cases)==128
    split={}
    for k in [12,96,95]:
        tag=f"{k}.1"
        rows=[x for x in cases if x["round"]==tag]
        assert len(rows)==8,tag
        split[tag]={
           "cells":len(rows),
           "choice_changed":sum(x["UCI_choice_changed"] for x in rows),
           "strict_sign_flipped":sum(x["strict_signed_gap_inverted"] for x in rows),
           "cold_pair_agreement":sum(
              rows[j]["UCI_choice_changed"]==rows[j+1]["UCI_choice_changed"] and
              rows[j]["strict_signed_gap_inverted"]==rows[j+1]["strict_signed_gap_inverted"]
              for j in (0,2,4,6)),
           "one_or_both_rank_missing":sum(not x["fully_reported_common_rank_depth"] for x in rows)
        }
    public={"schema":"c3x-014-p2-node-cap-order-hash-postdiscovery-actual-native-court-v1",
        "status":"POSTDISCOVERY_INTRA_SOURCE_STRESS_ONLY__NO_INDEPENDENT_CHESS_CAUSAL_CONFIRMATION",
        "parent_panel_sha256":PARENT_SHA,"science_source":"TCEC S29 previously scored P2 16 development groups",
        "source_group_count":16,"preknown_discovery_rounds":["12.1","96.1","95.1"],
        "arms":["EP9 OFF","EP9 MAIN"],"node_budget_method":"N=max(1024, prior CLEAN depth12 cold1 rank1 final nodes), same cap per OFF and MAIN",
        "root_order_variants":["source order","reversed legal source moves"],"hash_MiB":[16,64],
        "cold_repeats":2,"cells":cases,
        "all_group_cells":len(cases),
        "choice_changes":sum(x["UCI_choice_changed"] for x in cases),
        "strict_cp_sign_inversions":sum(x["strict_signed_gap_inverted"] for x in cases),
        "missing_full_multiPv":sum(not x["fully_reported_common_rank_depth"] for x in cases),
        "preknown_three_rounds":split,
        "scientific_warning":["Same requested UCI node cap is NOT exact equal search work; record actual nodes and completed depths.","Discovery games were chosen after inspecting P2 result; this stress is neither source-independent nor new heldout.","No user human explanation or chess concept mediation passes here.","Move-order perturbation and Hash64 change TT state, potentially changing causal pathway itself."],
        "P1_heldout_opened":False,
        "chess_strategy_causal_conclusion":False}
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(public,indent=2)+"\n")
    print("P2_NODE_CAP_NATIVE_STRESS_VERDICT",json.dumps({"cases":len(cases),
       "changed_choice":public["choice_changes"],
       "strict":public["strict_cp_sign_inversions"],
       "missing":public["missing_full_multiPv"],
       "discovered":split}),flush=True)
if __name__=="__main__":main()
