#!/usr/bin/env python3
"""C3X0.14 post-outcome S28 64 legal root pin-object SEE mechanism replication.

Original S28 five-arm GLOBAL software intervention outcomes were seen before this
S28 object-guarded design. Use same source-pinned S29-verified C++ root guard;
two independent processes each OFF and ROOT_OBJECT_SEE_UNMASK per S28 source game.
Not an unseen S28 prediction or learned neural chess category certificate.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from c3x_014_ROOT_PIN_object_guarded_SEE_40world_native_court import main_engine,base_only

SOURCE_SHA="1152473ed8d8793361f922434c75c7da2b9a58e0aa68a59466fc65179d6ac5e4"
PARENT_SHA="86bcbaa3e5e974834b35c35e387b1255e6369ca708c65f8d260d44faa359acd9"
MODES=("OFF","ROOT_OBJECT_SEE_UNMASK")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def assert_(cond,msg):
    if not cond:raise RuntimeError(msg)
def by_fen(rows):
    z=collections.defaultdict(list)
    for r in rows:z[r["root_original_FEN"]].append(r)
    return z
def main():
    p=argparse.ArgumentParser()
    for k in ("source","prior-704","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    assert_(sha(a.source)==SOURCE_SHA,"S28_ORIGINAL_SOURCE_FROZEN_SHA")
    assert_(sha(a.prior_704)==PARENT_SHA,"S28_ORIGINAL_GLOBAL_OPERATOR_704_SHA")
    s=json.loads(Path(a.source).read_bytes()); prior=json.loads(Path(a.prior_704).read_bytes())
    sources=s["actual_source_only_64_chess_pin_selected_worlds"]
    baselines=prior["all_64_S28_source_new_season_native_classic_causal_five_arm_outcomes"]
    assert_(len(sources)==len(baselines)==64,"S28_FULL64_CASE_COUNT_GATE")
    assert_(len(set(w["game_index"] for w in sources))==64,"S28_ORIGINAL_GAME_SOURCE_DISTINCT")
    rows=[]
    for i,(w,old) in enumerate(zip(sources,baselines),1):
        assert_(w["game_index"]==old["source_game_id"] and
                w["board_six_field_FEN"]==old["exact_original_position_FEN"],
                "SOURCE_S28_ORIGINAL_704_EXACT_CASE_MISMATCH")
        arms={}
        for arm in MODES:
            cold=[main_engine(a.engine,w,arm) for _ in range(2)]
            assert_(cold[0]==cold[1],"SOURCE_NATIVE_COLD_RESTART_NOT_EQUAL_"+arm)
            arms[arm]=cold[0]
        untouched={k:v for k,v in old["all_5_arms_native_source_outcomes"]["OFF"].items()
                      if k!="pin_causal_intervention"}
        assert_(base_only(arms["OFF"])==untouched,
                "S28_ROOT_OBJ_OFF_CHANGED_ORIGINAL_SF16_UCI_OR_PIN_SITE_TRACE")
        obj=arms["ROOT_OBJECT_SEE_UNMASK"]; natural=arms["OFF"]
        count=obj["object_guard"]["target_fired"]
        diff={k:obj[k]!=natural[k] for k in
              ("bestmove","score_kind","score_flag","value_root_stm","pv","nodes")}
        if not count:
            assert_(not any(diff.values()),"S28_ZERO_TARGETED_PIN_BRANCH_YET_UCI_CHANGED")
        global_effect=old["native_direct_source_operator_firing_and_root_effect"]["SEE_UNMASK"]["bestmove_changed"]
        rows.append({
            "original_source_game":w["game_index"],"source_round":w["source_round"],
            "root_original_FEN":w["board_six_field_FEN"],
            "root_pinned_piece_square":w["pinned_square"],"root_pinner_square":w["pinning_square"],
            "pre_score_chess_law_subtype":w["source_chess_law_subtype"],
            "global_software_SEE_UNMASK_bestmove_changed":global_effect,
            "root_object_SEE_branch_actual_fired":count,
            "root_object_SEE_changed_bestmove":diff["bestmove"],
            "root_object_SEE_changed_score":any(diff[k] for k in ("score_kind","score_flag","value_root_stm")),
            "root_object_SEE_changed_nodes":diff["nodes"],"root_object_SEE_changed_PV":diff["pv"],
            "original_native_OFF":natural,
            "root_object_only_SEE_UNMASK_native":obj
        })
        print("C3X014_S28_ROOT_PIN_OBJECT_NATIVE",i,"game",w["game_index"],
              "source_fired",count,"root_obj_flip",diff["bestmove"],
              "old_global_flip",global_effect,flush=True)
    fen_groups=by_fen(rows)
    duplicate=[(k,v) for k,v in fen_groups.items() if len(v)>1]
    assert_(len(fen_groups)==63 and len(duplicate)==1 and
            sorted(x["original_source_game"] for x in duplicate[0][1])==[61,62],
            "SOURCE_S28_ONE_DUPLICATED_FEN_GAME_PAIR_CONTRACT")
    for _,same in duplicate:
        original=same[0]
        for e in same[1:]:
            # Original same 6-field FEN but potentially different source histories
            # (native recency/rule50 can matter); preserve observed disagreement.
            pass
    exposed=[r for r in rows if r["root_object_SEE_branch_actual_fired"]]
    responded=[r for r in rows if r["root_object_SEE_changed_bestmove"]]
    combined={f"{int(r['global_software_SEE_UNMASK_bestmove_changed'])}{int(r['root_object_SEE_changed_bestmove'])}":
              sum(int(x['global_software_SEE_UNMASK_bestmove_changed'])==int(r['global_software_SEE_UNMASK_bestmove_changed'])
                  and int(x['root_object_SEE_changed_bestmove'])==int(r['root_object_SEE_changed_bestmove'])
                  for x in rows) for r in rows}
    law_groups=collections.defaultdict(list)
    for r in rows:law_groups[json.dumps(r["pre_score_chess_law_subtype"],sort_keys=True)].append(r)
    law_stats={k:{"source_games":len(v),"obj_fired":sum(r["root_object_SEE_branch_actual_fired"]>0 for r in v),
                  "obj_flip":sum(r["root_object_SEE_changed_bestmove"] for r in v),
                  "global_flip":sum(r["global_software_SEE_UNMASK_bestmove_changed"] for r in v)}
               for k,v in law_groups.items()}
    result={
      "schema":"c3x-014-S28-root-original-pin-object-source-native-SEE-64-game-court-postdiscovery-v1",
      "formal_research":"C3X 0.14","proposed_C3X015_NOT_OPEN":True,
      "chronological_admission":"POST-DISCOVERY: S28 global five-arm outcomes already public before this new root-object study. Mechanism replication on old source-frozen roots, NOT new blind S28 phenotype discovery.",
      "original_S28_source_64_SHA256":SOURCE_SHA,
      "original_S28_global_704_natives_JSON_SHA256":PARENT_SHA,
      "original_native_SF16_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "source_root_game_count":64,"source_root_unique_FEN_count":63,
      "duplicated_identical_six_field_FEN_games":[61,62],
      "source_game_original_chess_pin_legal_move_generation_changed":False,
      "actual_native_SF16_new_engine_processes":256,
      "new_native_treatments":["OFF","ROOT_OBJECT_SEE_UNMASK"],
      "cold_restart_conditions_exact":"128/128",
      "all_OFF_root_UCI_score_PV_nodes_pin_site_trace_equal_previous_704":"64/64",
      "unfired_root_PIN_target_branch_changes_UCI":"0",
      "old_S28_global_SEE_bestmove_change_root_games":
         sum(r["global_software_SEE_UNMASK_bestmove_changed"] for r in rows),
      "new_original_ROOT_object_SEE_branch_exposed_root_games":len(exposed),
      "new_original_ROOT_object_SEE_actual_native_fired_events":
         sum(r["root_object_SEE_branch_actual_fired"] for r in rows),
      "new_original_ROOT_object_SEE_changed_bestmove_root_games":len(responded),
      "old_global_vs_new_root_object_bestmove_response_contingency":combined,
      "new_object_targeted_root_bestmove_response_unique_FEN":
         sum(any(e["root_object_SEE_changed_bestmove"] for e in arr) for arr in fen_groups.values()),
      "new_object_targeted_root_response_per_chess_law_subtype":law_stats,
      "full_original_64_source_game_native_2arm_output_and_guard":rows,
      "old_procedurally_sealed_P1_four_game_cohort_opened":False,
      "source_native_KING_pin_structure_root_object_guarded":True,
      "NNUE_learned_latent_concept_identified":False,
      "root_specific_chess_PIN_caused_strategy":False,
      "scientific_limits":[
        "Original S28 global operator response labels were already seen; the proposed root-object mechanism replication is post-outcome and may be hypothesis-contaminated.",
        "Guard checks same type+color on pinned square, original king/pinner square and geometric legal pin, but does not track unique real piece identity through move history.",
        "Targeted SEE event fires on any encountered descendant search position with matching original object-and-ray identities, not only at root position.",
        "The artificially changed SEE heuristic is not real chess legality; legal move generation stays pristine.",
        "64 source-game IDs are 63 unique six-field FEN positions: games 61 and 62 duplicate, never pretend full distinct position sample.",
        "Season-disjoint same TCEC provider not provider-disjoint, one SF16/classical source version, fixed depth12 no budget response surface.",
        "Responses are code-mechanism perturbation outcomes, NOT proof of NNUE discovered hidden chess concept categories."
      ]
    }
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_S28_OBJECT_RESTRICTED_SEE_NATIVE_REPLICATION_VERDICT",json.dumps({
        "worlds":64,"uniqueFEN":63,"realNativeSF16":256,"cold":"128/128",
        "OFFsham":"64/64",
        "previousGlobalSEEflip":result["old_S28_global_SEE_bestmove_change_root_games"],
        "specificRootObjectFiredWorlds":len(exposed),
        "specificRootObjectFiredEvents":result["new_original_ROOT_object_SEE_actual_native_fired_events"],
        "specificRootObjectFlipWorlds":len(responded),
        "specificRootObjectFlipUniqueFEN":result["new_object_targeted_root_bestmove_response_unique_FEN"],
        "contingency":combined
    }),flush=True)
if __name__=="__main__":main()
