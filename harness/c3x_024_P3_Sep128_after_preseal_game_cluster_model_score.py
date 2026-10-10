#!/usr/bin/env python3
"""Combine all four fully frozen September 128-game TT FIRST shards.
Game is sample unit; four nested role cells are NOT independent games.
"""
import argparse,glob,hashlib,json,random,math
from pathlib import Path
from collections import Counter
MODELS=("M0","M1","M2_depth11","M3_v1","M3_v2")
def audit(directory):
    paths=sorted(glob.glob(str(Path(directory)/"C3X024_P3_TREATED_SHARD_*.json")))
    if len(paths)!=4:raise ValueError("P3_NOT_ALL_FOUR_PRESEALED_SHARDS_SUCCESSFUL")
    allrows=[]
    for shard,p in enumerate(paths):
        raw=Path(p).read_bytes()
        data=json.loads(raw)
        if data["schema"]!="c3x024-P3-128game-human-Git-presealed-five-model-physical-TT-FIRST-shard-v1" or data["shard"]!=shard or data["case_range"]!=[shard*32+1,(shard+1)*32] or data["source_games"]!=32 or data["potential_roles"]!=128:
            raise ValueError("P3_WRONG_SHARD_OR_PRIOR_SOURCE")
        if data["model_forecast_source_SHA256"]!="c402a6808bcaa2d73ec58632f87aa4ba7e8be0577b051b85e0a5610750eb1887" or data["untreated_stageA_SHA256"]!="1c9f265b507712069442956c3ecf0dcdcb7e9abbeaaff4b683ba9beb263d3b09" or data["original_source_JSON_SHA256"]!="ee8265f96b055645428f2fa87b36647e1931c86c848db5725a8b0ec63596dacb":
            raise ValueError("P3_SHARD_INPUT_SHA_DRIFT")
        if data["treated_SEE_Boolean_flips"]!=0:raise ValueError("P3_SEE_FORCED_INTERVENTION_FORBIDDEN")
        if len(data["all_cells"])!=32:raise ValueError("P3_SHARD_LOST_GAMES")
        for row in data["all_cells"]:
            if row["game_id"]!=len(allrows)+1 or len(row["roles"])!=4:
                raise ValueError("P3_GAME_IDS_OUT_OF_ORDER_OR_MISSING_ROLES")
            allrows.append(row)
    if len(allrows)!=128:raise ValueError("P3_NOT_128_INDEPENDENT_GAME_ROWS")
    roles=[(g["game_id"],c) for g in allrows for c in g["roles"]]
    if len(roles)!=512:raise ValueError("P3_NOT_512_TOTAL_PREDECLARED_ROLES")
    hold=[x for _,x in roles if x["status"]=="PRESEALED_INELIGIBLE_NO_FIRST_READER"]
    contact=[(g,x) for g,x in roles if x["status"]=="REAL_NATIVE_PHYSICAL_TT_FIRST"]
    no=[x for _,x in roles if x["status"]=="NO_CONTACT_HOLD"]
    if len(hold)!=11 or len(contact)+len(no)!=501:
        raise ValueError("P3_REAL_CONTACT_AND_PRE_FIRST_ELIGIBILITY_DRIFT")
    if any(x["treated_bestmove"] is not None or x["cold_pairs_checked"]!=0 for x in hold):
        raise ValueError("P3_PRESEALED_HOLD_WAS_TREATED")
    for g,x in contact:
        if not x["source_TT_first_contact"] or x["selected_native_reader_blocks"]<1 or x["cold_pairs_checked"]!=2 or x["source_SEE_Boolean_flips"]!=0:
            raise ValueError("P3_NATIVE_PHYSICAL_CONTACT_UNVERIFIED")
        if any(x["correct"][m] is None for m in MODELS):raise ValueError("P3_INCOMPLETE_EXACT_PREDICTION")
    role_accuracy={m:sum(int(x["correct"][m]) for _,x in contact) for m in MODELS}
    source_game=[]
    for g in allrows:
        cells=[x for x in g["roles"] if x["status"]=="REAL_NATIVE_PHYSICAL_TT_FIRST"]
        denom=len(cells)
        counts={m:sum(int(x["correct"][m]) for x in cells) for m in MODELS}
        source_game.append({"game_id":g["game_id"],"contact_role_cells":denom,
            "correct_role_counts":counts,
            "per_game_role_exact_accuracy":{m:counts[m]/denom if denom else None for m in MODELS},
            "any_correct_in_game":{m:int(counts[m]>0) if denom else None for m in MODELS},
            "root_bestmove_flips":sum(x["actual_root_flip"] is True for x in cells)})
    touched=[g for g in source_game if g["contact_role_cells"]]
    def wins_losses(metric,challenger,benchmark):
        return {"wins":sum(g[metric][challenger]>g[metric][benchmark] for g in touched),
                "losses":sum(g[metric][challenger]<g[metric][benchmark] for g in touched),
                "ties":sum(g[metric][challenger]==g[metric][benchmark] for g in touched)}
    primary=wins_losses("per_game_role_exact_accuracy","M3_v2","M0")
    any_correct=wins_losses("any_correct_in_game","M3_v2","M0")
    per_game_deltas=[g["per_game_role_exact_accuracy"]["M3_v2"]-
                     g["per_game_role_exact_accuracy"]["M0"] for g in touched]
    effect=sum(per_game_deltas)/len(per_game_deltas) if touched else None
    rng=random.Random(20261011)
    if touched:
        n=len(touched)
        boots=sorted(sum(per_game_deltas[rng.randrange(n)] for _ in range(n))/n
                    for _ in range(5000))
        interval=[boots[125],boots[4874]]
    else:interval=[None,None]
    exact_flip_roles=[(g,x) for g,x in roles
                      if x["status"]=="REAL_NATIVE_PHYSICAL_TT_FIRST"
                      and x["predicted"]["M3_v2"]!=x["predicted"]["M0"]]
    n_predicted=sum(x["predicted"]["M3_v2"]!=x["predicted"]["M0"]
                  for g,x in roles if x["status"]!="PRESEALED_INELIGIBLE_NO_FIRST_READER")
    if n_predicted!=1:raise ValueError("P3_HUMAN_GIT_SEALED_ONE_POSITIVE_NOT_KEPT")
    # Cannot manufacture statistically independent roles or a natural TT->SEE chain.
    return {"schema":"c3x024-P3-September2025-128-game-prospective-after-human-Git-presealed-five-models-v1",
      "scientific_comparison":"M3_v2 versus M0 exact-UCI prediction after SOURCE_AND_STAGEA_AND_FORECAST_GIT_PRESEAL",
      "original_literally_Git_sealed_predictions_SHA256":"c402a6808bcaa2d73ec58632f87aa4ba7e8be0577b051b85e0a5610750eb1887",
      "independent_source_game_rows":128,
      "statistical_dependency":"128 distinct original games but events can be shared; role cells nested within game. Event-cluster-adjusted inference not established.",
      "eligible_pre_first_role_cells":501,"presealed_ineligible_role_cells":11,
      "real_native_physical_FIRST_contact_roles":len(contact),
      "physical_FIRST_NO_CONTACT_HOLD":len(no),
      "contacted_games":len(touched),
      "final_root_bestmove_change_roles":sum(g["root_bestmove_flips"] for g in source_game),
      "source_games_with_final_root_change":sum(g["root_bestmove_flips"]>0 for g in source_game),
      "exact_UCI_correct_contacted_roles_by_model":role_accuracy,
      "model_names":list(MODELS),
      "M3_v1_precommitted_positive_predictions":0,
      "M3_v2_precommitted_positive_predictions":1,
      "M3_v2_positive_prediction_physical_contact":bool(exact_flip_roles),
      "M3_v2_vs_M0_per_game_average_role_accuracy_comparison":primary,
      "M3_v2_vs_M0_per_game_any_correct":any_correct,
      "M3_v2_minus_M0_mean_game_level_accuracy":effect,
      "M3_v2_minus_M0_game_cluster_bootstrap_95pct":[interval[0],interval[1]],
      "no_claim_of_superiority":not (primary["wins"]>primary["losses"] and interval[0]>0),
      "natural_TT_SEE_mediation_proven":False,
      "SEE_boolean_changes":0,
      "source_only_deidentified_game_results":source_game,
      "original_complete_PGN_FEN_players_private":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    d=audit(a.directory)
    o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    summary={k:v for k,v in d.items() if k in (
        "real_native_physical_FIRST_contact_roles","physical_FIRST_NO_CONTACT_HOLD",
        "exact_UCI_correct_contacted_roles_by_model",
        "M3_v2_vs_M0_per_game_average_role_accuracy_comparison",
        "M3_v2_vs_M0_per_game_any_correct",
        "M3_v2_minus_M0_mean_game_level_accuracy",
        "M3_v2_minus_M0_game_cluster_bootstrap_95pct",
        "final_root_bestmove_change_roles","source_games_with_final_root_change")}
    print("C3X024_P3_AFTER_LITERAL_GIT_SEAL_PROSPECTIVE_128_GAME_MODEL_COURT",summary,
          hashlib.sha256(o.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
