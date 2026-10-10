#!/usr/bin/env python3
"""C3X021 P2: FIRST x SECOND physical TT reader factorial, and legal searchmoves.

March full frozen denominator 16 games x STRICT/BROAD, 31 eligible; exact
source full64 writer target. Focus only already-known P1 root flips in #4/#9
for matched board-unchanged chess legal-root affordance interventions.
Results are exploratory; parent sample and predictions were frozen before run.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_021_P1_march_native_TT_atomic_bridge import (
    move_micro_comparison,root_depth_ladder)

MARCH_SHA="d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
P1_SHA="5ee15c3ec48be0042a9bb0ae7566808737f56e7568c2b29d43f00ae64afcb259"
ATOMIC_SHA="c14711c0e31bde26c2c7fc6e77f1f2fdf0ac70180a517b91f71845f1fd78ed3f"
R1_SHA="e9765a9d9c2254866cba80a968ed4f10013d7ee0b2ff93f41c4d203daed98a8c"
ROLES=("STRICT","BROAD")
ARMS=("ZERO","FIRST","SECOND","BOTH")
# This retrospective focus is fixed in the *pre-outcome* P2 design;
# it can never be counted as another prospective cohort.
FOCI={(4,"BROAD"):("h8h4","g5h4"),
      (9,"STRICT"):("a6b7","f6h5")}

def checked(path,digest):
    blob=Path(path).read_bytes()
    need(hashlib.sha256(blob).hexdigest()==digest,
         "P2_INPUT_SHA_DRIFT_"+Path(path).name)
    return json.loads(blob)

def same_world(x,y):
    need(x["UCI"]==y["UCI"] and x==y,"P2_COLD_DUPLICATE_MISMATCH")

def cold_native(engine,world,clocks,target,filters,probe):
    opts={"fen_clocks":clocks,"tt_reader_filters":filters,
          "probe_watch":probe,"native_use_watch":probe}
    x=play(engine,world,"F","V",target,**opts)
    y=play(engine,world,"F","V",target,**opts)
    same_world(x,y)
    need(0<len(x["root_events"])<4096,"P2_NATIVE_ROOT_TRACE_CENSORED")
    need(not any(e.get("kind")=="censored"
                 for e in x["native_tt_value_uses"]+x["watched_tt_probes"]),
         "P2_NATIVE_TT_WATCH_CENSORED")
    return x

def witness(x,physical,root_calls,kind):
    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    selected={"ZERO":set(),"FIRST":{root_calls[0]},
              "SECOND":{root_calls[1]},"BOTH":set(root_calls)}[kind]
    need(all(e["root_call"] in selected and
             all(e[k]==physical[k] for k in ("key64","slot","epoch"))
             for e in blocks),"P2_BLOCK_PHYSICAL_KEY_OR_CALL_DRIFT")
    need(len(blocks)==x["lineage_summary"]["reader_block"],
         "P2_FULL_READER_BLOCK_DENOMINATOR")
    first=sum(e["root_call"]==root_calls[0] for e in blocks)
    second=sum(e["root_call"]==root_calls[1] for e in blocks)
    return {
        "first_delivered":first>0,"second_delivered":second>0,
        "first_contact_count":first,"second_contact_count":second,
        "delivered_bits":str(int(first>0))+str(int(second>0)),
        "source_block_events":blocks,
    }

def native_arm(x,physical,root_calls,kind,F):
    contact=witness(x,physical,root_calls,kind)
    u=x["UCI"]
    return {
        "kind":kind,"UCI":u,"same_as_F_bestmove":u["bestmove"]==F["bestmove"],
        "same_as_F_six_field_UCI":u==F,
        "categorical_F_bestmove_differs":u["bestmove"]!=F["bestmove"],
        "root_depth_ladder":root_depth_ladder(x["root_events"]),
        "source_root_event_count":len(x["root_events"]),
        "second_full64_probe_events":[e for e in x["watched_tt_probes"]
            if e.get("kind")=="probe"],
        "second_native_actual_TT_value_use_events":[e for e in x["native_tt_value_uses"]
            if e.get("kind")=="used"],
        **contact,
        "cold_double_exact":True,
    }

def legal_root_cold(engine,world,clocks,allowed):
    atom=tuple(allowed)
    need(len(set(atom))==len(atom) and 1<=len(atom)<=2,
         "P2_LEGAL_ROOT_ALTERNATIVES")
    args={"fen_clocks":clocks,"root_searchmoves":atom}
    a=play(engine,world,"O",None,**args)
    b=play(engine,world,"O",None,**args)
    same_world(a,b)
    need(a["UCI"]["bestmove"] in atom,
         "P2_SEARCHMOVES_ENGINE_IGNORED_ROOT_ADMISSIBILITY")
    return {"candidate_set":list(atom),"UCI":a["UCI"],
            "search_context":"SEPARATE_COLD_UCI_ROOT_SEARCHMOVES",
            "cold_double_exact":True}

def board_court(engine,original,atoms,clocks,F,V):
    world,_=canonical_engine_world(original)
    micro=move_micro_comparison(F,V,atoms)
    legal={x["move"]:x for x in atoms["profile"]["moves"]}
    need(F in legal and V in legal and F!=V,"P2_PAIR_LEGAL_AND_DISTINCT")
    need(F==original["played_legal_move_uci"],
         "P2_ORIGINAL_GAME_ROOT_CANDIDATE_DRIFT")
    # source frozen facts and no post-outcome tailoring
    if original["id"]==4:
        need(legal[F]["root_capture"] and legal[V]["root_capture"]
             and legal[F]["to"]==legal[V]["to"]=="h4",
             "P2_GAME4_SAME_CAPTURED_SQUARE_FACT")
        need(micro["F_micro"]["reply_legal_move_count"]==
             micro["V_micro"]["reply_legal_move_count"]==29,
             "P2_GAME4_REPLY_FAN_FACT")
    if original["id"]==9:
        need(not legal[F]["root_capture"] and not legal[V]["root_capture"],
             "P2_GAME9_NONCAPTURE_FACT")
        need((micro["F_micro"]["reply_legal_move_count"],
              micro["V_micro"]["reply_legal_move_count"])==(40,41),
             "P2_GAME9_REPLY_FAN_FACT")
    ordered=(F,V)
    arms={
        "LEGAL_PAIR_ONLY":legal_root_cold(engine,world,clocks,ordered),
        "FORCE_F_ONLY":legal_root_cold(engine,world,clocks,(F,)),
        "FORCE_V_ONLY":legal_root_cold(engine,world,clocks,(V,))
    }
    need(arms["FORCE_F_ONLY"]["UCI"]["bestmove"]==F and
         arms["FORCE_V_ONLY"]["UCI"]["bestmove"]==V,
         "P2_FORCE_LEGAL_CHESS_MOVE_FALSIFIED")
    return {"game":original["id"],"F":F,"V":V,
            "same_source_board":world["fen4"],
            "features":micro,
            "root_alternatives":arms,
            "limit":"Restricting root searchmoves alters available choices; it does not identify which chess property the unrestricted engine evaluated."}

def main():
    p=argparse.ArgumentParser()
    for arg in ("march","p1","atomic","r1","engine","out"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    march=checked(a.march,MARCH_SHA)
    previous=checked(a.p1,P1_SHA)
    atom=checked(a.atomic,ATOMIC_SHA)
    previous_watch=checked(a.r1,R1_SHA)
    need(len(march["selected"])==len(previous["cases"])==
         len(atom["positions"])==len(previous_watch["cases"])==16,
         "P2_ALL16_SOURCE_ALIGNMENT")
    result={"schema":"c3x021-P2-march31-native-full-factorial-and-legal-root-contrast-v1",
            "design":"EXPLORATORY_POST_P1_CHOICE_FLIP_FIXED31_FOUR_ARM_AND_TWO_LEGAL_ROOT_CONTRASTS",
            "source_sha256":{"march":MARCH_SHA,"p1":P1_SHA,
                             "atomic":ATOMIC_SHA,"p1_r1":R1_SHA},
            "native_engine":"frozen Stockfish16, depth12, Threads1, Hash16, NNUE off",
            "historical_negative":{"0.19_K4":"FAIL_0_OF_4","Feb_F19_5":"FAIL",
                                  "CPP_224":"REJECTED_ADVERSARIAL_REPLICATION"},
            "cases":[],"legal_root_counterfactuals":[]}
    for original,old,atoms,r1 in zip(
        march["selected"],previous["cases"],atom["positions"],previous_watch["cases"]
    ):
        gid=original["id"]
        need(gid==old["id"]==atoms["id"]==r1["game"] and
             original["source_game_sha256"]==old["source_sha"]==
             atoms["game_sha256"],"P2_ORIGINAL_SOURCE_IDENTITY_DRIFT")
        world,_=canonical_engine_world(original)
        clocks=game_clocks(original)
        old_f=old["controls"]["F"]["UCI"]
        row={"id":gid,"roles":{}}
        for role in ROLES:
            prior=old["roles"][role]
            if prior["status"]=="NO_ELIGIBLE_PHYSICAL_PAIR":
                need(r1["roles"][role]["class"]=="NO_ELIGIBLE_PHYSICAL_PAIR",
                     "P2_NO_PAIR_ORIGINAL_STATUS_DRIFT")
                row["roles"][role]={"status":"NO_ELIGIBLE_PHYSICAL_PAIR"}
                continue
            need(prior["status"]=="ACTUAL_SOURCE_CONTACT",
                 "P2_PARENT_FIRST_CONTACT_REQUIRED")
            physical=prior["source_physical"]
            root_calls=prior["source_root_calls"]
            pair={"root_calls":root_calls,
                  "root_candidate_native":prior["source_root_move_native"]}
            probe={"key64":physical["key64"],"root_call":root_calls[1]}
            arms={}
            for name in ARMS:
                raw=cold_native(a.engine,world,clocks,physical,
                                mask_filters(RULES[role],pair,name),probe)
                arms[name]=native_arm(raw,physical,root_calls,name,old_f)
                if name=="ZERO":
                    need(arms[name]["UCI"]==old_f and
                         arms[name]["delivered_bits"]=="00",
                         "P2_ZERO_NOT_ORIGINAL_F_SHAM")
                if name=="FIRST":
                    need(arms[name]["UCI"]==prior["V"]["UCI"] and
                         arms[name]["delivered_bits"].startswith("1"),
                         "P2_FIRST_NOT_ORIGINAL_P1_V")
            case={"status":"ALL4_COLD_CONTROLS_VALID",
                  "source_physical":physical,
                  "root_calls":root_calls,
                  "source_native_candidate":pair["root_candidate_native"],
                  "arms":arms,
                  "frozen_R1_second_use_class":r1["roles"][role]["class"],
                  "F_vs_FIRST_legal_move_contrast":prior["F_vs_V"],
                  "actual_2x2_contact_dose":{
                      name:arms[name]["delivered_bits"] for name in ARMS}}
            row["roles"][role]=case
            if (gid,role) in FOCI:
                need((old_f["bestmove"],arms["FIRST"]["UCI"]["bestmove"])==
                     FOCI[gid,role],"P2_FIXED_FOCAL_BESTMOVE_DRIFT")
                result["legal_root_counterfactuals"].append(
                    {"role":role,**board_court(a.engine,original,atoms,clocks,
                                      *FOCI[gid,role])})
        result["cases"].append(row)
        print("C3X021_P2_CASE",gid,
              {role:(row["roles"][role]["status"],
                     {k:(v["UCI"]["bestmove"],v["delivered_bits"])
                      for k,v in row["roles"][role].get("arms",{}).items()})
               for role in ROLES},flush=True)
    eligible=[r for c in result["cases"] for r in c["roles"].values()
              if r["status"]=="ALL4_COLD_CONTROLS_VALID"]
    need(len(eligible)==31 and len(result["legal_root_counterfactuals"])==2,
         "P2_ROLE31_AND_FOCAL2_DENOMINATORS")
    result["summary"]={
        "all_source_positions":16,
        "role_cells":32,
        "source_eligible":len(eligible),
        "source_no_eligible":1,
        "cold_native_factorial_runs":len(eligible)*len(ARMS)*2,
        "root_searchmoves_cold_runs":len(result["legal_root_counterfactuals"])*3*2,
        "arm_contact_denominator":{
            arm:sum(v["arms"][arm]["delivered_bits"]=="11"
                    for v in eligible) for arm in ARMS
        },
        "delivered_first_only":sum(
            r["arms"]["FIRST"]["first_delivered"] for r in eligible),
        "delivered_second_only":sum(
            r["arms"]["SECOND"]["second_delivered"] for r in eligible),
        "delivered_both":sum(
            r["arms"]["BOTH"]["first_delivered"] and
            r["arms"]["BOTH"]["second_delivered"] for r in eligible),
        "categorical_root_flips_by_arm":{
            arm:sum(r["arms"][arm]["categorical_F_bestmove_differs"]
                    for r in eligible) for arm in ARMS
        },
        "focused_game4":{
            k:result["cases"][3]["roles"]["BROAD"]["arms"][k]["UCI"]["bestmove"]
            for k in ARMS},
        "focused_game9":{
            k:result["cases"][8]["roles"]["STRICT"]["arms"][k]["UCI"]["bestmove"]
            for k in ARMS},
        "scope":"Known P1 flipped games chosen retrospectively; source/factorial arms pre-frozen before P2 outcomes."
    }
    dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("C3X021_P2_FOUR_ARM_ALL31_AND_LEGAL_MOVE_COURT",
          json.dumps(result["summary"],sort_keys=True),flush=True)

if __name__=="__main__":
    main()
