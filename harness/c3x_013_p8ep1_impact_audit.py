#!/usr/bin/env python3
"""P8-EP1: frozen P7/P8 tactical support rejudgment for en passant victim square.

Never reselect rooted moves or overwrite the original engine outcomes.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from harness.c3x_013_p7r1_tactical_support import hazard,census

def direct_only_types(board,move):
    """Old buggy recapture policy, retained to quantify the exact semantic delta."""
    q=board.copy(stack=False);q.push(move)
    dest=move.to_square
    vals=[]
    for reply in q.legal_moves:
        if reply.to_square==dest and q.is_capture(reply):
            p=q.piece_at(reply.from_square)
            if p:vals.append(chess.piece_name(p.piece_type))
    return sorted(vals)

def root_audit(board,move_uci):
    move=chess.Move.from_uci(move_uci)
    assert move in board.legal_moves
    old=direct_only_types(board,move)
    new=hazard(board,move)["recapture_types"]
    q=board.copy(stack=False);q.push(move)
    ep=[r.uci() for r in q.legal_moves if q.is_en_passant(r)]
    return {"uci":move_uci,"old_recapture_types":old,
            "corrected_recapture_types":new,
            "opponent_legal_en_passant_replies":ep,
            "changed":old!=new}

def recompute_source_worlds(records,keypath):
    totals_old={};totals_new={}
    changed=[]
    for source in records:
        worlds=keypath(source)
        for label,old in worlds:
            if old.get("status") not in ("TACTICAL_RULE_SUPPORT_MEASURED","CHESS_RULE_PAIR_SUPPORT_ONLY"):
                continue
            board=chess.Board(old["fen"])
            if not board.is_valid():raise ValueError("ORIGINAL_SOURCE_CHESS_BOARD_INVALID")
            new=census(board)["counts"]
            orig=old["tactical"]["counts"] if "tactical" in old else old["gate_counts"]
            for k in new:
                totals_old[k]=totals_old.get(k,0)+orig[k]
                totals_new[k]=totals_new.get(k,0)+new[k]
            diffs={k:{"old":orig[k],"corrected":new[k]} for k in new if orig[k]!=new[k]}
            if diffs:
                changed.append({"broadcast":source["broadcast"],
                                "label":label,"game_url":source["game_url"],
                                "fen4_sha256":hashlib.sha256(
                                    " ".join(board.fen(en_passant="fen").split()[:4]).encode()).hexdigest(),
                                "changed_census":diffs})
    return {"old_total":totals_old,"corrected_total":totals_new,
            "source_worlds_with_changed_counts":changed}

def main():
    p=argparse.ArgumentParser()
    for key in ("p7r1","p7r2","p8r1","p8r2"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data={key:json.loads(Path(getattr(a,key)).read_text()) for key in
          ("p7r1","p7r2","p8r1","p8r2")}
    hashes={key:hashlib.sha256(Path(getattr(a,key)).read_bytes()).hexdigest() for key in data}
    assert data["p7r1"]["schema"]=="c3x-013-p7-r1-disjoint-tactical-support-census-v1"
    assert data["p7r2"]["schema"]=="c3x-013-p7-r2-tactical-cold-near-equal-v1"
    assert data["p8r1"]["schema"]=="c3x-013-p8-r1-source-only-phase-positivity-v1"
    assert data["p8r2"]["schema"]=="c3x-013-p8-r2-frozen-birth-two-engine-v1"
    first=recompute_source_worlds(
        data["p7r1"]["records"],
        lambda r:[("32",r)])
    second=recompute_source_worlds(
        data["p8r1"]["records"],
        lambda r:list(r["worlds"].items()))
    p7source={(r["broadcast"],r["game_url"]):r for r in data["p7r1"]["records"]}
    affected={"P7_tactically_admitted_pairs":[],"P8_born_versus_nonborn_pairs":[]}
    for r in data["p7r2"]["records"]:
        pair=r.get("qualification",{}).get("tactically_filtered_pair")
        if not pair:continue
        original=p7source.get((r["broadcast"],r["game_url"]))
        if not original:raise ValueError("P7_SOURCE_KEY_LOSS")
        b=chess.Board(original["fen"])
        left,right=[root_audit(b,pair[x]) for x in ("a","b")]
        if not (left["old_recapture_types"]==right["old_recapture_types"]):
            raise ValueError("P7_ORIGINAL_PAIR_NOT_OLD_HAZARD_MATCHED")
        affected["P7_tactically_admitted_pairs"].append({
            "broadcast":r["broadcast"],"pair":[pair["a"],pair["b"]],
            "old_matched":True,
            "corrected_matched":left["corrected_recapture_types"]==right["corrected_recapture_types"],
            "root_details":[left,right]})
    for r in data["p8r2"]["results"]:
        pair=r["pair_true_false"]
        b=chess.Board(r["root_fen"])
        left,right=[root_audit(b,pair[x]) for x in ("a","b")]
        if left["old_recapture_types"]!=right["old_recapture_types"]:
            raise ValueError("P8_ORIGINAL_BIRTH_PAIR_NOT_OLD_HAZARD_MATCHED")
        affected["P8_born_versus_nonborn_pairs"].append({
            "broadcast":r["broadcast"],"ply":r["ply"],
            "pair":[pair["a"],pair["b"]],"old_matched":True,
            "corrected_matched":left["corrected_recapture_types"]==right["corrected_recapture_types"],
            "root_details":[left,right]})
    historical={}
    for key,items in affected.items():
        historical[key]={"pairs":len(items),
           "newly_rejected":sum(not r["corrected_matched"] for r in items),
           "pairs_with_ep_hazard_change":sum(any(x["changed"] for x in r["root_details"]) for r in items),
           "details":items}
    out={"schema":"c3x-013-p8-ep1-en-passant-victim-revision-v1",
         "status":"RETROSPECTIVE_RULE_CORRECTION_NOT_NEW_CHEMISTRY_OR_CAUSAL_SCIENCE",
         "frozen_inputs_sha256":hashes,
         "source_census":{"P7_original_29_worlds":first,
                          "P8_original_32_groups_three_landmarks":second},
         "historical_frozen_pair_adjudication":historical,
         "corrected_capture_rule":"Compare opponent legal captured VICTIM square, not capture landing square; en passant victim=target+8 when Black captures, target-8 when White captures",
         "chess_engine_scores_recomputed":False,
         "old_source_results_overwritten":False,
         "causal_explanation_granted":False,
         "C3X_014":"CANDIDATE_ONLY_UNOPENED"}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2)+"\n")
    print("P8_EP1_P7_SOURCE_WORLDS_CHANGED",len(first["source_worlds_with_changed_counts"]))
    print("P8_EP1_P8_SOURCE_WORLDS_CHANGED",len(second["source_worlds_with_changed_counts"]))
    print("P8_EP1_FROZEN_PAIRS",{k:{"pairs":v["pairs"],"newly_rejected":v["newly_rejected"],
                                      "affected":v["pairs_with_ep_hazard_change"]}
                                        for k,v in historical.items()})
    assert historical["P7_tactically_admitted_pairs"]["pairs"]==8
    assert historical["P8_born_versus_nonborn_pairs"]["pairs"]==8
    assert not out["causal_explanation_granted"]
if __name__=="__main__":main()
