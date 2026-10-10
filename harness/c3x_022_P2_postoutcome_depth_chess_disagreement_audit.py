#!/usr/bin/env python3
"""Post-outcome forensic ONLY. Audit failed exact-UCI forecasts at native root depth
against chess-decision primitives frozen before any TT counterfactual.

This never changes the sealed CROSS_ORDER_RESTORATION_V1 predictions.
"""
import argparse
import hashlib
import json
from pathlib import Path
from collections import defaultdict

SOURCE_SHA="ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554"
PRIMITIVES_SHA="b3b4a29788c1f9dc2b4d491cd60d44ad8e6530d3d66be5d77039a6fd59cc958d"
STAGEB_SHA="f8c9210cfb9f158d038e70045a1839c3ecebb487781dbc59ce9615b2491a1899"
ECOLOGIES=("twic","lichess_puzzles")
ROLES=("STRICT","BROAD")
ORDERS=("O","F")

def verified(path,sha):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError("FORENSIC_INPUT_SHA_DRIFT_"+Path(path).name)
    return json.loads(raw)

def explain(court,primitives,source):
    audit={"schema":"c3x022-P2-postoutcome-falsified-UCI-chess-depth-forensics-v1",
           "label":"POST_OUTCOME_DESCRIPTIVE__NEVER_PROSPECTIVE",
           "source_sha256":SOURCE_SHA,"primitives_sha256":PRIMITIVES_SHA,
           "stageB_sha256":STAGEB_SHA,"ecologies":{}}
    for eco in ECOLOGIES:
        original=source["ecologies"][eco]["selected"]
        prim=primitives["ecologies"][eco]["selected"]
        c=court["per_ecology"][eco]["cases"]
        if len(original)!=len(prim)!=len(c):
            raise ValueError("FORENSIC_ECOLOGY_LENGTH_DRIFT")
        if len(original)!=16 or len(prim)!=16 or len(c)!=16:
            raise ValueError("FORENSIC_16_DENOMINATOR")
        records=[]
        altered_game_ids=set()
        incorrect_game_ids=set()
        unique_causal_episodes=set()
        for row,p,case in zip(original,prim,c):
            gid=row["id"]
            if not(gid==p["id"]==case["game"] and
                   row["source_game_sha256"]==p["source_game_sha256"]==case["source_game_sha256"]):
                raise ValueError("FORENSIC_SOURCE_ID_MISMATCH")
            moves={m["move"]:m for m in p["profile"]["moves"]}
            for order in ORDERS:
                base=case["worlds"][order]["baseline_UCI"]["bestmove"]
                for role in ROLES:
                    arm=case["worlds"][order]["roles"][role]
                    if not arm["source_contact"]:
                        continue
                    actual=arm["actual_post_intervention_bestmove"]
                    predicted=arm["registered_exact_UCI_forecast"]
                    if not {base,actual,predicted}.issubset(moves):
                        raise ValueError("FORENSIC_NATIVE_UCI_NOT_FROZEN_LEGAL")
                    flipped=base!=actual
                    wrong=predicted!=actual
                    if not (flipped or wrong):
                        continue
                    if flipped:
                        altered_game_ids.add(gid)
                    if wrong:
                        incorrect_game_ids.add(gid)
                    role_sig=(gid,order,base,actual,arm["first_physical_target"]["key64"],
                              arm["first_physical_target"]["slot"],arm["first_physical_target"]["epoch"])
                    unique_causal_episodes.add(role_sig)
                    descriptions={}
                    for name,move in (("baseline",base),("predicted",predicted),("actual",actual)):
                        v=moves[move]
                        descriptions[name]={
                            "UCI":move,"piece":v["piece"],
                            "root_capture":v["root_capture"],
                            "gives_check":v["after_root_opponent_in_check"],
                            "opponent_legal_reply_count":v["reply_legal_move_count"],
                            "opponent_legal_reply_sha256":v["reply_legal_move_sha256"],
                            "legal_immediate_recaptures_of_arrival":v["reply_captures_destination"],
                            "geometric_attack_edges_added":len(v["attack_edge_added"]),
                            "geometric_attack_edges_removed":len(v["attack_edge_removed"]),
                            "king_pin_edges_added":v["pin_added"],
                            "king_pin_edges_removed":v["pin_removed"]}
                    records.append({
                        "source_game_id":gid,
                        "root_order":order,"source_role":role,
                        "physical_writer_key64":str(arm["first_physical_target"]["key64"]),
                        "physical_writer_slot":arm["first_physical_target"]["slot"],
                        "physical_writer_epoch":arm["first_physical_target"]["epoch"],
                        "actual_first_reader_contact":True,
                        "final_move_changed":flipped,
                        "exact_UCI_prediction_wrong":wrong,
                        "predicted_root_move":predicted,
                        "baseline_root_move":base,
                        "actual_root_move":actual,
                        "actual_equal_to_other_order_baseline":
                            actual==case["worlds"]["F" if order=="O" else "O"]["baseline_UCI"]["bestmove"],
                        "first_observed_root_leader_depth_change":
                            arm["earliest_root_leader_depth_changed"],
                        "all_observed_root_leader_depth_changes":
                            arm["changed_root_leader_depths"],
                        "root_depths_not_comparable":arm["missing_root_depths_due_to_source_stop_or_trace"],
                        "frozen_chess_action_facts":descriptions})
        audit["ecologies"][eco]={
            "affected_source_games":sorted(altered_game_ids),
            "forecast_wrong_source_games":sorted(incorrect_game_ids),
            "observed_role_cell_records_with_flip_or_forecast_error":len(records),
            "unique_physical_source_episode_keys_in_records":len(unique_causal_episodes),
            "records":records,
            "limitations":["Game clusters and STRICT/BROAD roles are not independent",
                           "Chess action differences from fixed pre-native source facts are not a demonstrated unique native C++ valuation cause",
                           "No root-call/candidate trace after earliest path divergence was aligned or invented"]
        }
    return audit

def main():
    a=argparse.ArgumentParser()
    for n in ("stageb","primitives","source","out"):a.add_argument("--"+n,required=True)
    p=a.parse_args()
    d=explain(verified(p.stageb,STAGEB_SHA),
              verified(p.primitives,PRIMITIVES_SHA),
              verified(p.source,SOURCE_SHA))
    out=Path(p.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_RETROSPECTIVE_CHESS_X_DEPTH_FORENSICS",
          {k:{"altered":v["affected_source_games"],"wrong":v["forecast_wrong_source_games"]}
           for k,v in d["ecologies"].items()},
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)

if __name__=="__main__":main()
