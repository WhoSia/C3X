#!/usr/bin/env python3
"""P7-R3 exact 2x2 pawn birth algebra; NOT a legal intervention nor engine cause."""
import argparse,collections,hashlib,io,json
from pathlib import Path
import chess,chess.pgn
from harness.c3x_013_p5_source_partition import extract
from harness.c3x_013_p6e_pawn_birth_events import game_events,blockers

TAXONOMY={(1,0):"POSITION_ALONE_SUFFICIENT",
          (0,1):"OPPONENT_CONFIGURATION_ALONE_SUFFICIENT",
          (1,1):"EITHER_FACTOR_SUFFICIENT",
          (0,0):"JOINT_NECESSARY"}

def one_game(item):
    audit=game_events(item)
    result={"broadcast":item["broadcast"],"game_url":item["game_url"],
            "source_game_sha256":item["sha"],"old_P6E_status":audit["status"],
            "birth_events":[]}
    if audit["status"]!="LEGAL_FULL_GAME":
        result["status"]="HOLD_P6E_ORIGINAL_SOURCE"
        return result
    by_ply=collections.defaultdict(list)
    for e in audit["events"]:
        by_ply[e["ply"]].append(e)
    game=chess.pgn.read_game(io.StringIO(item["raw"].decode("utf-8","replace")))
    if not game or game.errors:
        result["status"]="HOLD_PGN_PARSE"
        return result
    b=game.board()
    count=0
    for ply,m in enumerate(game.mainline_moves(),1):
        if m not in b.legal_moves:
            result.update({"status":"HOLD_ILLEGAL_GAME","ply":ply})
            return result
        previous=b.copy(stack=False)
        b.push(m)
        for event in by_ply.get(ply,[]):
            color=(event["newly_passed_color"]=="white")
            origin=chess.parse_square(event["pawn_before"])
            dest=chess.parse_square(event["pawn_after"])
            piece_before=previous.piece_at(origin)
            piece_after=b.piece_at(dest)
            if (not piece_before or not piece_after or
                piece_before.piece_type!=chess.PAWN or piece_after.piece_type!=chess.PAWN or
                piece_before.color!=color or piece_after.color!=color):
                raise ValueError("BIRTH_PAWN_IDENTITY_DRIFT")
            B00=blockers(previous,origin,color)
            B10=blockers(previous,dest,color)
            B01=blockers(b,origin,color)
            B11=blockers(b,dest,color)
            if B00!=event["blockers_before"] or B11!=[]:
                raise ValueError("BIRTH_BLOCKER_PROOF_DRIFT")
            a=int(not B10)
            bb=int(not B01)
            count+=1
            result["birth_events"].append({
                "ply":ply,"uci":m.uci(),"pawn_color":event["newly_passed_color"],
                "pawn_coordinate_before":event["pawn_before"],
                "pawn_coordinate_after":event["pawn_after"],
                "source_P6E_heuristic_category":event["event_class"],
                "four_cell_truth":{"old_position_old_enemy":0,
                    "new_position_old_enemy":a,
                    "old_position_new_enemy":bb,
                    "new_position_new_enemy":1},
                "blocker_sets":{"old_position_old_enemy":B00,
                    "new_position_old_enemy":B10,
                    "old_position_new_enemy":B01,
                    "new_position_new_enemy":B11},
                "factor_class":TAXONOMY[(a,bb)],
                "formal_counterfactual_is_legal_move":False
            })
    if count!=len(audit["events"]):
        raise ValueError("BIRTH_EVENT_LOSS")
    result["status"]="FACTOR_PROOF_COMPLETE"
    result["source_pawn_birth_count"]=count
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    source=extract(args.source)
    results=[one_game(x) for x in source]
    ev=[e for x in results for e in x["birth_events"]]
    counts={name:sum(e["factor_class"]==name for e in ev)
            for name in TAXONOMY.values()}
    old_labels={k:sum(e["source_P6E_heuristic_category"]==k for e in ev)
                for k in sorted(set(e["source_P6E_heuristic_category"] for e in ev))}
    grouped={name:len({x["broadcast"] for x in results
                       if any(e["factor_class"]==name for e in x["birth_events"])})
             for name in TAXONOMY.values()}
    result={"schema":"c3x-013-p7-r3-four-cell-pawn-birth-algebra-v1",
            "stage":"C3X 0.13 P7",
            "source_sha256":hashlib.sha256(Path(args.source).read_bytes()).hexdigest(),
            "original_frozen_broadcast_groups":16,
            "legal_game_count":sum(x["status"]=="FACTOR_PROOF_COMPLETE" for x in results),
            "historical_P6E_birth_events":len(ev),"factor_event_counts":counts,
            "source_group_counts_by_factor":grouped,
            "historical_heuristic_labels_preserved":old_labels,
            "games":results,
            "authority":"FORMAL_PAWN_FEATURE_COUNTERFACTUAL_ONLY_NOT_CHESS_LEGAL_OR_ENGINE_CAUSAL",
            "chess_engine_evaluation":None,"human_utility_evaluation":None,
            "0_14_status":"CANDIDATE_ONLY_UNOPENED"}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("P7_R3_PAWN_BIRTH_FACTOR_COUNTS",counts,"source_games",grouped)
    print("P7_R3_HISTORIC_P6E_TAXONOMY_PRESERVED",old_labels)
    assert len(source)==16 and len(ev)==19
    assert all(not e["formal_counterfactual_is_legal_move"] for e in ev)
    assert len(results)==16 and len(ev)==sum(counts.values())
if __name__=="__main__":main()
