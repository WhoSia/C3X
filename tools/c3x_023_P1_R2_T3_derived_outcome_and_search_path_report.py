#!/usr/bin/env python3
"""Rights-reviewed derived move/score/depth trajectories for completed T3 trials.

No third-party original PGN, FEN, player names, or full source lineage
exported. Native engine int move and UCI outputs are newly computed results.
TT intervention original; precise SEE single-return source alteration only.
"""
import argparse,json,hashlib
from pathlib import Path
SCHEMA="c3x023-P1-R2-T3-exact-native-SEE-two-cases-physical-TT-crossed-development-v1"
ARMS=("native_sham_baseline","native_TT_FIRST_only","native_SEE_once_only","native_joint_once")
ARMLABELS=("TT0_SEE_SHAM","TT1_SEE_SHAM","TT0_SEE_FLIP","TT1_SEE_FLIP")

def derive(blob):
    if blob.get("schema")!=SCHEMA or blob.get("summary",{}).get("source_chess_cases")!=2:
        raise ValueError("T3_NOT_VALIDATED_TWO_SOURCE_FACTORIAL")
    out={"schema":"c3x023-P1-R2-T3-presealed-two-native-prune-sites-derived-depth-and-bestmove-v1",
         "science":"POST_R1_DEVELOPMENT_CONDITIONAL_OPERATOR_INTERACTION_NOT_NATURAL_MEDIATION",
         "origin_license":"Lichess May 2026 Broadcast CC BY-SA 4.0",
         "changes":"Newly computed engine move/score and native source-depth summaries from two annotated experimental positions; no original full PGN/header/player data",
         "origin_credit":"Lichess broadcasters",
         "cases":[]}
    for c in blob["cases"]:
        st={"game_id":c["game_id"],"root_order":c["root_order"],
            "source_role":c["source_role"],
            "exact_prune_site":c["exact_source_preregistered_pruning_site"],
            "TT_FIRST_native_source_physical_verified":True,
            "SEE_conditional_dose_exactly_one_per_flip_arm":True,
            "original_native_SEE_bool":c["native_sham_baseline"]["source_native_SEE_original_Boolean"],
            "natural_mediation_not_proved":True,
            "arms":{},"depth_first_changes":{}}
        for k,label in zip(ARMS,ARMLABELS):
            arm=c[k]
            if arm.get("status")!="VALID_SOURCE_SINGLETON" or not arm.get("cold_reproducible"):
                raise ValueError("T3_SOURCE_CONTACT_NOT_PROVEN")
            if arm.get("SEE_site_exact_hits")!=1:
                raise ValueError("T3_TARGET_NOT_UNIQUE")
            if arm.get("SEE_actuator_delivered")!=(1 if "FLIP" in label else 0):
                raise ValueError("T3_PRECISE_SOURCE_ACTUATOR_DOSE_INCONSISTENT")
            u=arm["terminal_UCI"]
            depths=arm["root_depth_history"]
            st["arms"][label]={
                "bestmove_exact_UCI":u.get("bestmove"),
                "searchinfo":{k:v for k,v in u.items() if k not in ("bestmove","pv","moves","fen","pgn") and
                              isinstance(v,(str,int,float,bool,type(None)))},
                "real_native_TT_first_block":arm["real_native_TT_FIRST"],
                "SEE_source_event_Boolean":arm["source_native_SEE_delivered_Boolean"],
                "depths":{str(d):{"native_root_candidate":q.get("native_leader"),
                                   "root_return_score":q.get("score"),
                                   "retry_count":q.get("retry_count"),
                                   "source_trace_may_be_partial":bool(q.get("terminal_or_source_trace_partial",False))}
                          for d,q in sorted(depths.items(),key=lambda i:int(i[0]))}}
        a=st["arms"]["TT0_SEE_SHAM"];b=st["arms"]["TT1_SEE_SHAM"]
        c1=st["arms"]["TT0_SEE_FLIP"];d=st["arms"]["TT1_SEE_FLIP"]
        st["categorical_interaction"]={
            "TT_alone_changes_bestmove":a["bestmove_exact_UCI"]!=b["bestmove_exact_UCI"],
            "SEE_alone_changes_bestmove":a["bestmove_exact_UCI"]!=c1["bestmove_exact_UCI"],
            "joint_differs_from_TT_alone":b["bestmove_exact_UCI"]!=d["bestmove_exact_UCI"],
            "joint_new_candidate_unique_to_joint":d["bestmove_exact_UCI"] not in (
                a["bestmove_exact_UCI"],b["bestmove_exact_UCI"],c1["bestmove_exact_UCI"])}
        for pair in (("TT0_SEE_SHAM","TT1_SEE_SHAM"),("TT0_SEE_SHAM","TT0_SEE_FLIP"),
                     ("TT1_SEE_SHAM","TT1_SEE_FLIP"),("TT0_SEE_FLIP","TT1_SEE_FLIP")):
            l,r=(st["arms"][a] for a in pair)
            shared=sorted(set(l["depths"]) & set(r["depths"]),key=int)
            st["depth_first_changes"][pair[0]+"__VS__"+pair[1]]={
                "shared_observed_depths":[int(q) for q in shared],
                "first_native_root_leader_divergence_depth":next(
                    (int(q) for q in shared if l["depths"][q]["native_root_candidate"] !=
                                           r["depths"][q]["native_root_candidate"]),None),
                "first_source_root_score_divergence_depth":next(
                    (int(q) for q in shared if l["depths"][q]["root_return_score"] !=
                                           r["depths"][q]["root_return_score"]),None),
                "trace_outside_common_depth_window_not_interpreted":True}
        out["cases"].append(st)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",required=True)
    q=p.parse_args();i=Path(q.source);o=Path(q.out)
    d=derive(json.loads(i.read_bytes()));o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("C3X023_T3_NATIVE_UCI_DEPTH_DERIVED_POSTHOC_SOURCE_FINAL",[
     {"game_id":c["game_id"],"prune_site":c["exact_prune_site"],
      "UCI":{a:val["bestmove_exact_UCI"] for a,val in c["arms"].items()},
      "depth_first_changes":c["depth_first_changes"]} for c in d["cases"]],
     hashlib.sha256(o.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
