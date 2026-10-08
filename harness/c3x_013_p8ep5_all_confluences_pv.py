#!/usr/bin/env python3
"""P8-EP5: all 14 source-locked legal confluences, real two-engine PV reply audit."""
import argparse,hashlib,json
from pathlib import Path
import chess
from harness.c3x_013_p8e1_pinned_ethereal import observe
from harness.c3x_013_p6r1_birth_rival_support import births
from harness.c3x_013_p7r1_tactical_support import hazard

SEGMENT_DIGEST="240501f203478560f22cd32614ba56b0870749cb0e890f7bc4a219d4ce955796"
ETH_COMMIT="0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"
DEPTHS=(8,12,16)

def witnesses(blob):
    doc=json.loads(blob)
    assert doc["schema"]=="c3x-013-p8-ep3-heldout-chess-legal-confluence-census-v1"
    assert doc["frozen_new_segment_list_sha256"]==SEGMENT_DIGEST
    assert doc["source_denominator"]==len(doc["records"])==32
    out=[]
    for group in doc["records"]:
        for ply,world in group["worlds"].items():
            if world.get("status")!="LEGAL_SOURCE_SUPPORT":continue
            for w in world["census"]["witnesses"]:
                root=chess.Board(world["fen"])
                assert root.is_valid() and not root.is_game_over()
                a=chess.Move.from_uci(w["single"])
                b=chess.Move.from_uci(w["double"])
                assert a in root.legal_moves and b in root.legal_moves
                assert a.from_square==b.from_square
                assert not root.is_capture(a) and not root.is_capture(b)
                found=[]
                for move,stored_reply in ((a,w["reply_after_single"]),(b,w["reply_after_double"])):
                    board=root.copy(stack=False);board.push(move)
                    reply=chess.Move.from_uci(stored_reply["reply"])
                    assert reply in board.legal_moves and board.is_capture(reply)
                    kind="EN_PASSANT" if board.is_en_passant(reply) else "NORMAL_CAPTURE"
                    assert kind==stored_reply["kind"]
                    board.push(reply)
                    found.append(board.fen(en_passant="fen"))
                assert found[0]==found[1]==w["exact_common_full_fen"]
                births_a,births_b=births(root,a),births(root,b)
                assert births_a==w["passed_birth_single"] and births_b==w["passed_birth_double"]
                assert bool(births_a)!=bool(births_b) is w["passed_birth_toggled"]
                matched=hazard(root,a)["recapture_types"]==hazard(root,b)["recapture_types"]
                assert matched==w["root_capture_hazard_equal"]
                out.append({"source_rank":group["source_rank"],
                            "broadcast":group["broadcast"],"game_url":group["game_url"],
                            "source_sha256":group["source_game_sha256"],"ply":int(ply),
                            "source_fen":world["fen"],"root_pair":{"a":a.uci(),"b":b.uci()},
                            "convergent_reply":{"a":w["reply_after_single"],
                                                "b":w["reply_after_double"]},
                            "common_six_field_fen":found[0],
                            "birth_true_toggle":w["passed_birth_toggled"],
                            "root_hazard_equal":matched,
                            "previously_scored_TCEC":group["source_rank"]==111 and ply=="48"})
    assert len(out)==14
    assert len({z["broadcast"] for z in out})==7
    assert sum(z["birth_true_toggle"] for z in out)==4
    assert sum(z["root_hazard_equal"] and z["birth_true_toggle"] for z in out)==1
    assert sum(z["previously_scored_TCEC"] for z in out)==1
    return out

def get_reply(trial,root_uci):
    pv=trial.get("raw",{}).get(root_uci,{}).get("pv",[])
    return pv[1] if len(pv)>=2 else None

def panel(exe,board,item):
    result={}
    for d in DEPTHS:
        trials=[observe(exe,board,item["root_pair"],d) for _ in (0,1)]
        score_exact=all(t["status"]=="CP_DIRECTION_ONLY" for t in trials)
        score_exact=score_exact and trials[0]["gap_cp"]==trials[1]["gap_cp"]
        replies={k:[get_reply(t,item["root_pair"][k]) for t in trials]
                 for k in ("a","b")}
        pv_first_reply_exact=all(replies[k][0] is not None and
                                 replies[k][0]==replies[k][1] for k in ("a","b"))
        legal_support={
            k:bool(score_exact and pv_first_reply_exact and
                   replies[k][0]==item["convergent_reply"][k]["reply"])
            for k in ("a","b")}
        result[str(d)]={"trials":trials,"root_gap_repeat_exact":score_exact,
                        "root_gap_cp":trials[0].get("gap_cp") if score_exact else None,
                        "PV_opponent_first_reply":replies,
                        "PV_first_reply_repeat_exact":pv_first_reply_exact,
                        "each_branch_selects_convergent_capture":legal_support,
                        "BOTH_branches_select_confluence":bool(all(legal_support.values()))}
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--parent",required=True)
    ap.add_argument("--stockfish",default="/usr/games/stockfish")
    ap.add_argument("--ethereal",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    raw=Path(args.parent).read_bytes()
    items=witnesses(raw)
    result={"schema":"c3x-013-p8-ep5-search-usage-of-legal-confluence-v1",
            "stage":"C3X 0.13 P8-EP5",
            "parent_source_sha256":hashlib.sha256(raw).hexdigest(),
            "source_groups_total":32,"source_groups_with_confluence":7,
            "source_legal_confluence_events":14,
            "source_birth_toggled_events":4,
            "strict_birth_toggle_and_same_hazard_events":1,
            "historically_ep4_engine_scored_events":1,
            "engine_binary_sha256":{
                "Stockfish":hashlib.sha256(Path(args.stockfish).read_bytes()).hexdigest(),
                "Ethereal_classical":hashlib.sha256(Path(args.ethereal).read_bytes()).hexdigest()},
            "ethereal_source_commit":ETH_COMMIT,"records":[],
            "authority":"ACTUAL_PV_CHOICE_OF_LEGAL_CONVERGENT_REPLIES_ONLY",
            "chess_concept_causal_mediation_proven":False,
            "human_understanding_measured":False,
            "C3X_014":"CANDIDATE_ONLY_UNOPENED"}
    for item in items:
        board=chess.Board(item["source_fen"])
        record={**item,"engine_panels":{
            name:panel(exe,board,item)
            for name,exe in (("Stockfish",args.stockfish),
                             ("Ethereal_classical",args.ethereal))}}
        record["both_engines_same_depth_both_branches_confluence"]=[
            str(depth) for depth in DEPTHS if all(
                record["engine_panels"][name][str(depth)]["BOTH_branches_select_confluence"]
                for name in ("Stockfish","Ethereal_classical"))]
        record["all_engines_PV_complete"]=all(
            record["engine_panels"][name][str(d)]["root_gap_repeat_exact"] and
            record["engine_panels"][name][str(d)]["PV_first_reply_repeat_exact"]
            for name in ("Stockfish","Ethereal_classical") for d in DEPTHS)
        result["records"].append(record)
    result["counts"]={
        "original_events":14,
        "PVs_complete_in_both_engines_at_all_depths":sum(x["all_engines_PV_complete"]
                                                         for x in result["records"]),
        "one_or_more_both_engine_same_depth_confluence_choices":sum(
            bool(x["both_engines_same_depth_both_branches_confluence"])
            for x in result["records"]),
        "any_branch_any_engine_any_depth_chooses_convergent_capture":sum(
            any(x["engine_panels"][name][str(d)]["each_branch_selects_convergent_capture"][k]
                for name in ("Stockfish","Ethereal_classical") for d in DEPTHS
                for k in ("a","b")) for x in result["records"]),
        "both_branch_confluence_chosen_by_Stockfish_in_any_depth":sum(
            any(x["engine_panels"]["Stockfish"][str(d)]["BOTH_branches_select_confluence"]
                for d in DEPTHS) for x in result["records"]),
        "both_branch_confluence_chosen_by_Ethereal_in_any_depth":sum(
            any(x["engine_panels"]["Ethereal_classical"][str(d)]["BOTH_branches_select_confluence"]
                for d in DEPTHS) for x in result["records"]),
        "birth_toggle_events_with_both_engines_confluence":sum(
            x["birth_true_toggle"] and bool(x["both_engines_same_depth_both_branches_confluence"])
            for x in result["records"])
    }
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
    print("P8EP5_ALL_14_SOURCE_CONFLUENCE_ENGINE_PV_USAGE",result["counts"])
    assert len(result["records"])==14 and not result["chess_concept_causal_mediation_proven"]
if __name__=="__main__":
    main()
