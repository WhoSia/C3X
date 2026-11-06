#!/usr/bin/env python3
"""P42/R9 native A/B control under broad value_draw parity neutralization.

Unlike the 0.27 Game14 historical harness, deliberately DOES NOT demand
the original A/B bestmove identities after an experimental draw-score change.
Reports any source-verified changed roots as counterfactual results, not CI bugs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import chess

from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_029_p42_r9_native_value_draw_court import inspect
from c3x_029_p42_r8_same_engine_tt_save_causal_court import STAGEA_SHA,SOURCE_SHA,FORECAST_SHA,file_sha

def verify_original_inputs(source,stagea,forecast):
    for p,sha in ((source,SOURCE_SHA),(stagea,STAGEA_SHA),(forecast,FORECAST_SHA)):
        need(file_sha(p)==sha,"R9_AB_ORIGINAL_SOURCE_SHA")
    raw=json.loads(Path(source).read_text())["source_games"][13]
    prior=json.loads(Path(stagea).read_text())["cases"][13]
    previous=json.loads(Path(forecast).read_text())["cases"][13]
    need(raw["id"]==prior["id"]==previous["id"]==14,"R9_AB_GAME_ID")
    need(raw["source_game_sha256"]=="0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652","R9_AB_GAME_SHA")
    b=chess.Board(raw["fen4"]+" "+str(raw["source_halfmove_clock"])+" "+str(raw["source_fullmove_number"]))
    move=chess.Move.from_uci(raw["played_legal_move_uci"])
    need(b.is_valid() and move in b.legal_moves,"R9_AB_LEGAL_GAME")
    world=dict(raw)
    world["native_move"]=move.from_square*64+move.to_square
    world,clock,_=native_world(world)
    roles=prior["worlds"]["O"]["roles"]
    role=next((x for x in ("STRICT","BROAD") if roles[x]["status"]=="FIRST_SOURCE_PAIR_PRE_TREATMENT"),None)
    need(role is not None,"R9_AB_ROOT_ROLE")
    source_role=roles[role]
    physical=source_role["physical"]
    watch={"key64":physical["key64"],"root_call":source_role["root_calls"][0]}
    pair={"physical":physical,"root_calls":source_role["root_calls"],
          "root_candidate_native":source_role["root_candidate_native"]}
    return world,clock,physical,watch,mask_filters(RULES[role],pair,"FIRST")

def verify_native_arm(normal,treated,actual_draw_counts,reader_verified):
    if len(normal)!=2 or len(treated)!=2:
        return "HOLD_COLD_REPLAY_MISSING"
    if normal[0]!=normal[1] or treated[0]!=treated[1]:
        return "HOLD_NEUTRALIZED_COLD_REPLAY_UNSTABLE"
    if not all(reader_verified):
        return "HOLD_TT_FIRST_PHYSICAL_READER_UNVERIFIED"
    changed={"A":normal[0]!="b3a4","B":treated[0]!="f3f4"}
    if any(changed.values()):
        for arm,flag in changed.items():
            if flag and any(n<=0 for n in actual_draw_counts[arm]):
                return "HOLD_ROOT_CHANGE_WITHOUT_ACTUAL_VALUE_DRAW_SOURCE_CONTACT"
        return "PASS_BROAD_VALUE_DRAW_NEUTRALIZATION_CHANGED_ACTUAL_AB_ROOT_CHOICE"
    return "PASS_BROAD_VALUE_DRAW_NEUTRALIZATION_PRESERVED_ACTUAL_AB_ROOT_CHOICE"

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    moves={"A":[],"B":[]}
    counts={"A":[],"B":[]}
    reader=[]
    for rep in range(2):
        for arm in ("A","B"):
            path=private/(f"neutral_{arm}_rep{rep}_draw.txt")
            path.write_text("")
            env=os.environ.copy()
            os.environ["C3X042_R9_DRAW_TRACE"]=str(path.resolve())
            os.environ["C3X042_R9_DRAW_PARITY_NEUTRAL"]="1"
            os.environ.pop("C3X042_R8_DROP_DESCENDANT_TT_SAVE",None)
            try:
                res=(cold(a.engine,world,clock,"O","OBS",watch=watch)
                     if arm=="A" else
                     cold(a.engine,world,clock,"O","V",physical,filter=filters,watch=watch))
            finally:
                os.environ.clear()
                os.environ.update(env)
            moves[arm].append(res["UCI"]["bestmove"])
            counts[arm].append(inspect(path.read_text(),True)["actual_value_draw_calls"])
            if arm=="B":
                reader.append(bool(verified_reader_lineage(res)["all_valid"])
                              and any(x.get("kind")=="reader_block" for x in res["blocks"]))
    status=verify_native_arm(moves["A"],moves["B"],counts,reader)
    out={
       "schema":"c3x042-r9-neutralized-actual-original-AB-replay-v1",
       "status":status,
       "A_neutralized_bestmoves":moves["A"],
       "B_neutralized_TT_FIRST_bestmoves":moves["B"],
       "original_A":"b3a4","original_B":"f3f4",
       "actual_source_value_draw_calls_by_arm_cold_repeat":counts,
       "tt_reader_lineage_verified":reader,
       "original_chess_source_sha_verified":True,
       "cause_scope":"broad original value_draw function return intervention only",
       "one_guard_mediation_certified":False,
       "specific_draw_site_to_root_certified":False,
       "chess_strategy_meaning_certified":False,
       "prospective_generalization_certified":False,
       "private_history_or_keys_exposed":False
    }
    dest=Path(a.public_out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X042_R9_REAL_ORIGINAL_NEUTRALIZED_AB",status,moves,counts)
    if not status.startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":
    main()
