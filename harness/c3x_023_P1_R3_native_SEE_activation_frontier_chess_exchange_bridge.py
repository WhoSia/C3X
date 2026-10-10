#!/usr/bin/env python3
"""C3X023-P1-R3 native SEE search-branch FRONTIER and legal-root-exchange bridge.

R1 outcome-selected six May games DEVELOPMENT ONLY. No SEE actuation.
Full observed first32 original vs physically suppressed TT reader trajectory.
Compute strict event set intersection/one-sided prefixes, separate full search
window drift from chess parent path drift, and real board-legal root replies.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T1_exact_state_six_native_development import (
    scan as T1read, SOURCE_SHA, STAGEA_SHA, frozen)
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
    SELECTED,cold,source_lines)
from c3x_023_P1_R2_T1_native_search_state_matcher import whole

T1_SHA="1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb"
SCHEMA="c3x023-P1-R3-native-postTT-SEE-event-frontier-and-root-chess-legality-v1"

def actual(events,source_kind):
    o={}
    for line in events["ordered_source_operator_trace"]:
        if line["source"]!="native_SEE" or line["fields"]["kind"]!="witness":continue
        key=whole(line["fields"])
        o.setdefault(key,[]).append((line["line_ordinal"],line["fields"]))
    return o

def categorized(original,treated,orig_first,treated_first):
    a=actual(original,"ORIGINAL")
    b=actual(treated,"TREAT")
    bad=set(k for d in (a,b) for k,v in d.items() if len(v)!=1)
    a={k:v[0] for k,v in a.items() if k not in bad}
    b={k:v[0] for k,v in b.items() if k not in bad}
    ao={k:v for k,v in a.items() if v[0]>orig_first}
    bo={k:v for k,v in b.items() if v[0]>treated_first}
    ap={k:v for k,v in a.items() if v[0]<=orig_first}
    bp={k:v for k,v in b.items() if v[0]<=treated_first}
    common=set(ao)&set(bo)
    onlyA=set(ao)-set(bo)
    onlyB=set(bo)-set(ao)
    path_a={x[0] for x in ao}
    path_b={x[0] for x in bo}
    # key[0] exact chess path + native move/site/threshold, key[1]
    # live alpha/beta/ply/depth/PV/rule50/input occupancy state.
    divergence_path=sum(k[0] in path_b for k in onlyA)
    divergence_window=sum(k[0] in path_a for k in onlyB)
    migrateA={k for k in onlyA if k in bp}
    migrateB={k for k in onlyB if k in ap}
    censored=any(x["kind"]=="censored"
                 for x in original["native_see_events"]+treated["native_see_events"])
    def site_counts(keys,records):
        return dict(sorted(Counter(records[k][1]["site"] for k in keys).items()))
    def original_true_false(keys,records):
        return dict(sorted(Counter(
            ("SEE_TRUE" if records[k][1]["original"] else "SEE_FALSE")
            for k in keys).items()))
    return {
      "status":"OBSERVED_PREFIX_ONE_SIDED_NOT_GLOBAL_ABSENCE" if censored
          else "OBSERVED_COMPLETE_WATCH_SCOPE_FRONTIER",
      "native_SEE_unique_post_real_TT_original_count":len(ao),
      "native_SEE_unique_post_real_TT_first_block_count":len(bo),
      "same_full_source_state_post_TT_both_arms_count":len(common),
      "original_only_post_TT_prefix_native_SEE_states":len(onlyA),
      "TT_FIRST_only_post_TT_prefix_native_SEE_states":len(onlyB),
      "source_path_same_but_search_state_different_original_events":divergence_path,
      "source_path_same_but_search_state_different_first_events":divergence_window,
      "post_in_one_but_PRE_TT_in_other_original_events":len(migrateA),
      "post_in_one_but_PRE_TT_in_other_first_events":len(migrateB),
      "original_only_site_counts":site_counts(onlyA,ao),
      "first_only_site_counts":site_counts(onlyB,bo),
      "common_site_counts":site_counts(common,ao),
      "original_only_native_SEE_original_return_distribution":
        original_true_false(onlyA,ao),
      "first_only_native_SEE_original_return_distribution":
        original_true_false(onlyB,bo),
      "source_event_ambiguity_quarantined":len(bad),
      "first32_source_observation_censored":censored,
      "DO_NOT_CLAIM_ABSENT_UNSEEN_PATH":True,
      "SEE_native_boolean_actuations":0}

def root_exchange(board,uci):
    m=chess.Move.from_uci(uci)
    need(m in board.legal_moves,"R3_NATIVE_ROOT_BESTMOVE_NOT_LEGAL")
    b=board.copy()
    mover=b.piece_at(m.from_square)
    need(mover is not None,"R3_NO_ROOT_MOVER")
    iscapture=b.is_capture(m);check=b.gives_check(m)
    b.push(m)
    response=[x for x in b.legal_moves]
    recapture=[x for x in response if x.to_square==m.to_square
               and b.is_capture(x)]
    return {"source_move_encoded_piece":mover.symbol(),
            "source_move_is_capture":iscapture,
            "source_move_gives_check":check,
            "opponent_legal_response_count":len(response),
            "immediate_legal_capture_of_moved_piece_count":len(recapture),
            "opponent_pseudo_attackers_on_destination_count":
               len(b.attackers(b.turn,m.to_square)),
            "original_moving_side_pseudo_defenders_on_destination_count":
               len(b.attackers(not b.turn,m.to_square)),
            "NOTE":"Legal recaptures vs pseudo-attack edges separate; all source-only root chess facts, not native descendant SEE node facts."}

def run(source,stagea,engine):
    T1=T1read(source,stagea,engine)
    replay=(json.dumps(T1,sort_keys=True,indent=2)+"\n").encode()
    need(hashlib.sha256(replay).hexdigest()==T1_SHA,
         "R3_T1_PRIVATE_NATIVE_SEARCH_STATE_PROOF_DRIFT")
    rows=[]
    for gid,order,role in SELECTED:
        original=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        prior=stagea["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        tar=prior["worlds"][order]["roles"][role]
        need(original["id"]==prior["id"]==gid and
             tar["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME",
             "R3_FROZEN_SOURCE_SELECTED_ROLE_DRIFT")
        board,clocks,_=native_world(original)
        scope={"key64":tar["physical"]["key64"],
               "root_call":tar["root_calls"][0]}
        o=cold(engine,board,clocks,order,"OBS",watch=scope)
        need(o["UCI"]==prior["worlds"][order]["baseline_UCI"],
             "R3_READONLY_WATCH_CHANGED_NATIVE_BASELINE")
        pair={"physical":tar["physical"],"root_calls":tar["root_calls"],
              "root_candidate_native":tar["root_candidate_native"]}
        v=cold(engine,board,clocks,order,"V",tar["physical"],
               filter=mask_filters(RULES[role],pair,"FIRST"),watch=scope)
        blocked=source_lines(v,"physical_TT","reader_block",tar)
        used=sum((source_lines(o,"TT_value_used",kind,tar)
                  for kind in ("used","main_cutoff","qsearch_cutoff")),[])
        need(used and blocked,"R3_NATIVE_TT_SOURCE_EVIDENCE_MISSING")
        proof=verified_reader_lineage(v)
        need(proof["all_valid"] and proof["count"]>=len(blocked),
             "R3_TRUE_PHYSICAL_NATIVE_WRITER_READER_LINEAGE_FAILURE")
        for x in (o,v):
            need(all(e.get("altered",0)==0
                     for e in x["native_see_events"]),
                 "R3_PASSIVE_SEE_OPERATOR_DID_CHANGE")
        observed=categorized(o,v,min(x["line_ordinal"] for x in used),
                               min(x["line_ordinal"] for x in blocked))
        fen4=original["fen4"]
        complete=fen4+" "+str(clocks[0])+" "+str(clocks[1])
        b=chess.Board(complete)
        fact_before=root_exchange(b,o["UCI"]["bestmove"])
        fact_after=root_exchange(b,v["UCI"]["bestmove"])
        choice_changed=o["UCI"]["bestmove"]!=v["UCI"]["bestmove"]
        rows.append({"game_id":gid,"order":order,"TT_role":role,
         "TT_source_first_reader_actually_blocked":True,
         "TT_changed_final_root_UCI":choice_changed,
         "observed_SEE_after_actual_source_operator":observed,
         "root_legal_response_microstructures":{
           "TT_original_bestmove":fact_before,
           "TT_FIRST_bestmove":fact_after},
         "source_operator_SEE_bool_perturbations":0})
        print("C3X023_P1_R3_READONLY_SEARCH_FRONTIER",gid,order,role,
          "changed_root_move",choice_changed,
          "original_only",observed["original_only_post_TT_prefix_native_SEE_states"],
          "TT_first_only",observed["TT_FIRST_only_post_TT_prefix_native_SEE_states"],
          "shared",observed["same_full_source_state_post_TT_both_arms_count"],
          "censored",observed["first32_source_observation_censored"],flush=True)
    result={"schema":SCHEMA,
            "scientific_status":"SIX_POST_OUTCOME_DEVELOPMENT_GAMES_SOURCE_FRONTIER_NOT_MEDIATION",
            "source_sha256":SOURCE_SHA,"original_T1_private_native_SHA256":T1_SHA,
            "source_only_replay_T1_verified":True,"cases":rows}
    def agg(name):
        return sum(r["observed_SEE_after_actual_source_operator"][name] for r in rows)
    result["summary"]={
      "frozen_development_cases":len(rows),
      "original_native_TT_first_reader_confirmed_cases":len(rows),
      "changed_final_UCI_game_count":sum(x["TT_changed_final_root_UCI"] for x in rows),
      "shared_SEE_full_live_state_after_native_TT_source":agg("same_full_source_state_post_TT_both_arms_count"),
      "original_only_SEE_full_state_prefix_events":agg("original_only_post_TT_prefix_native_SEE_states"),
      "TT_FIRST_only_SEE_full_state_prefix_events":agg("TT_FIRST_only_post_TT_prefix_native_SEE_states"),
      "same_board_path_but_window_different_original_events":agg("source_path_same_but_search_state_different_original_events"),
      "same_board_path_but_window_different_first_events":agg("source_path_same_but_search_state_different_first_events"),
      "temporal_migration_original_events":agg("post_in_one_but_PRE_TT_in_other_original_events"),
      "temporal_migration_first_events":agg("post_in_one_but_PRE_TT_in_other_first_events"),
      "first32_source_observation_censored_cases":agg("first32_source_observation_censored"),
      "all_native_SEE_return_interventions":0,
      "root_counterfactuals_with_different_immediate_legal_recapture_count":
          sum(r["root_legal_response_microstructures"]["TT_original_bestmove"]
                    ["immediate_legal_capture_of_moved_piece_count"] !=
              r["root_legal_response_microstructures"]["TT_FIRST_bestmove"]
                    ["immediate_legal_capture_of_moved_piece_count"] for r in rows),
      "site_counts_original_only":dict(sorted(sum((Counter(
         r["observed_SEE_after_actual_source_operator"]["original_only_site_counts"])
         for r in rows),Counter()).items())),
      "site_counts_first_only":dict(sorted(sum((Counter(
         r["observed_SEE_after_actual_source_operator"]["first_only_site_counts"])
         for r in rows),Counter()).items())),
      "CAUTION":"All counts are observed first32 native SEE watch prefixes; one-sided does not imply total absence or causal mediation; do not infer from 6 outcome-informed development cases."}
    return result

def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    result=run(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),a.engine)
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X023_P1_R3_NATIVE_TT_SEE_ACTIVATION_AND_ROOT_LEGAL_EXCHANGE_VERDICT",
          result["summary"],hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
