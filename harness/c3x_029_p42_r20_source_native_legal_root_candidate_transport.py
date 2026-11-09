#!/usr/bin/env python3
"""P42/R20: source-native actual root leader identities after R18 reversal.

Replays unchanged R18 through verified R19. Decode the original Stockfish
non-special root Move bit encoding and independently verify every candidate
against the exact legal chess source position. Never classify an arbitrary
internal number as a legal move without that validation.
"""
import argparse,json,subprocess
from pathlib import Path
import chess
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import parse_three_cold_root_worlds
from c3x_027_game14_root_boundary_court import parse_boundary_lines

def native_to_legal_uci(raw:int,board:chess.Board)->str:
    if type(raw) is not int or raw<=0 or raw>=4096:
        raise ValueError("R20_HOLD_SPECIAL_OR_NONPOSITIVE_NATIVE_ROOT_MOVE")
    src=(raw>>6)&63
    dst=raw&63
    move=chess.Move(src,dst)
    if move not in board.legal_moves:
        raise ValueError("R20_HOLD_NATIVE_ROOT_LEADER_NOT_LEGAL_CHESS_MOVE")
    return move.uci()

def root_legal(rows,board):
    if len(rows)!=12 or any(x["depth"]!=i for i,x in enumerate(rows,1)):
        raise ValueError("R20_HOLD_ROOT_DEPTH_SUPPORT")
    return [native_to_legal_uci(row["leader"],board) for row in rows]

def classify(roots,verified_r19,board):
    required=("A","B","C","C_reverse")
    base={
       "status":"HOLD_LEGAL_ROOT_CANDIDATE_WORLD",
       "objective_chess_best_move_proved":False,
       "unique_natural_source_mediation_proved":False,
       "independent_adversarial_future_reason_proved":False,
       "prospective_cohort_proved":False,
       "nnue_enabled":False,
       "private_chess_source_history_exposed":False,
    }
    if verified_r19.get("status")!="PASS_NATIVE_SOURCE_REVERSAL_CHANGED_INTERMEDIATE_ROOT_LEADER":
        return dict(base,status="HOLD_R19_ACTUAL_LEADER_EFFECT_NOT_ADMITTED")
    try:
        legal={name:root_legal(roots[name],board) for name in required}
    except (ValueError,KeyError):
        return dict(base,status="HOLD_CHESS_ROOT_LEGALITY_OR_WORLD_MISSING")
    derived=[i for i in range(1,13)
             if legal["C"][i-1]!=legal["C_reverse"][i-1]]
    if derived!=verified_r19["leader_changed_depths"]:
        return dict(base,status="HOLD_ROOT_INTERMEDIATE_SOURCE_RECHECK_DRIFT")
    depthwise=[]
    for depth in range(1,13):
        d=depth-1
        depthwise.append({
            "depth":depth,
            "A":legal["A"][d],
            "B":legal["B"][d],
            "C":legal["C"][d],
            "C_reverse":legal["C_reverse"][d],
            "reverse_matches_original_B":legal["C_reverse"][d]==legal["B"][d],
            "reverse_matches_original_C":legal["C_reverse"][d]==legal["C"][d],
            "reverse_is_third_move":legal["C_reverse"][d] not in (legal["B"][d],legal["C"][d]),
        })
    return dict(base,
        status="PASS_ACTUAL_NATIVE_LEGAL_ROOT_LEADER_CANDIDATE_TRANSPORT_ONLY",
        source_chess_move_legality_verified=True,
        original_game14_legal_source_board_verified=True,
        exactly_twelve_depths=True,
        changed_root_leader_depths=derived,
        root_depths=depthwise,
        final_original_C_move=legal["C"][-1],
        final_reversed_C_move=legal["C_reverse"][-1],
        first_original_B_recovery_depth=next(
          (r["depth"] for r in depthwise
           if r["depth"] in derived and r["reverse_matches_original_B"]),None),
        third_candidate_emergence_depths=[
           r["depth"] for r in depthwise
           if r["depth"] in derived and r["reverse_is_third_move"]],
        caveat="Intermediate legal leader identities, not a single-path root mediation proof.")

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    board=chess.Board(world["fen4"]+" "+str(world["source_halfmove_clock"])+" "+str(world["source_fullmove_number"]))
    if not board.is_valid():raise ValueError("R20_HOLD_ACTUAL_CHESS_SOURCE_BOARD_INVALID")
    root=Path(a.private);root.mkdir(parents=True,exist_ok=True)
    r19private=root/"R19_repeat_R18_source"
    r19out=root/"R19_verified_public_held_private.json"
    subprocess.run([
      "python","-u","harness/c3x_029_p42_r19_native_R18_root_depth_propagation.py",
      "--source",a.source,"--stagea",a.stagea,"--forecast",a.forecast,
      "--engine",a.engine,"--private",str(r19private),"--public-out",str(r19out)
    ],check=True)
    verified=json.loads(r19out.read_text())
    if (verified["status"]!="PASS_NATIVE_SOURCE_REVERSAL_CHANGED_INTERMEDIATE_ROOT_LEADER"
       or verified["original_C_move"]!="b3a4" or verified["reverse_C_move"]!="b3a4"
       or verified["exact_source_event_contacts_per_cold"]!=[2,2]):
       raise ValueError("R20_HOLD_ORIGINAL_SINGLE_CYCLE_INTERVENTION_PROVENANCE")
    old=r19private/"R18_verified_native"
    r14=old/"original_R16_and_R15_controls"/"native_R15_original_guard_and_combined"/"original_R14_controls"
    originals=parse_three_cold_root_worlds((r14/"ABC_legacy_root_depths.txt").read_text())
    reversed=[]
    for i in range(2):
        court=parse_boundary_lines((old/f"reverse_cold_{i}"/"root.txt").read_text().splitlines())
        if court["status"]!="PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS":
            raise ValueError("R20_HOLD_REVERSED_NATIVE_ROOT_SOURCE")
        reversed.append(court["runs"][0])
    if reversed[0]!=reversed[1]:
        raise ValueError("R20_HOLD_R18_REVERSE_COLD_REPLAY")
    result=classify({**originals,"C_reverse":reversed[0]},verified,board)
    result["schema"]="c3x042-r20-legal-native-root-choice-counterfactual-v1"
    result["actual_source_matched_C_event_ordinal"]=verified["reverse_target_source_ordinal"]
    result["physical_cutoff_reversed"]=verified["reversed_C_immediate_cutoff"]==[False,False]
    result["root_depth_summary_causal_sensitivity_r19"]=True
    out=Path(a.public_out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X042_R20_LEGAL_ROOT_LEADERS",result["status"],
          "changed",result.get("changed_root_leader_depths"),
          "matches_B",result.get("first_original_B_recovery_depth"),
          "third",result.get("third_candidate_emergence_depths"))
    if not result["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":
    main()
