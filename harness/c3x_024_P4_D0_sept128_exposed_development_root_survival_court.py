#!/usr/bin/env python3
"""P4 D0: SHA pinned exposed Sept2025 game107 failure plus all-game root cues.
Development-only and no retraining performance claim. Does not touch fresh cohort.
"""
import argparse,json,hashlib,collections
from pathlib import Path
from c3x_024_P3_Sep2025_128_preFIRST_M0_M1_M2_M3v1_M3v2 import native_lookup
from c3x_024_P3_preFIRST_literal_512role_integrity_gate import locked,read,SRC_SHA,STAGE_SHA,FORECAST_SHA
OUTCOME_SHA="63853d8de4861b24163a007898df0b23e21f3db9642adb16214f9eff4c9ab7ef"
SCORE_SCHEMA="c3x024-P3-September2025-128-game-prospective-after-human-Git-presealed-five-models-v1"
MODELS=("M0","M3_v2")
def diagnose(src,stage,fc,seal,outcome):
    lock=locked(src,stage,fc,seal)
    if outcome["schema"]!=SCORE_SCHEMA or outcome["independent_source_game_rows"]!=128 or outcome["real_native_physical_FIRST_contact_roles"]!=501:
        raise ValueError("P4_D0_WRONG_PROSPECTIVE_OUTCOME")
    all_scores=outcome["source_only_deidentified_game_results"]
    if len(all_scores)!=128:raise ValueError("P4_D0_MISSING_GAME_ROWS")
    table=collections.Counter()
    focal=None
    num=0
    for source,old,pred,scored in zip(src["selected"],stage["ecologies"]["sep2025_broadcast"]["cases"],fc["cases"],all_scores):
        gid=source["id"]
        if old["id"]!=gid or pred["game_id"]!=gid or scored["game_id"]!=gid:
            raise ValueError("P4_D0_SOURCE_SCORE_IDENTITY_DRIFT")
        native,by_uci=native_lookup(source)
        worlds=old["worlds"]
        bases={o:worlds[o]["baseline_UCI"]["bestmove"] for o in ("O","F")}
        source_depth={}
        for order in ("O","F"):
            l=worlds[order]["depth_leaders"]
            source_depth[order]={str(d):{"UCI":native.get(l.get(str(d),{}).get("native_leader")),
                                           "score":l.get(str(d),{}).get("score"),
                                           "retries":l.get(str(d),{}).get("retry_count")}
                                  for d in range(8,13)}
        if gid==107:
            focal={"game_id":gid,"O_F_untreated_baseline_UCI":bases,
                   "untreated_depth8to12_leaders":source_depth,
                   "root_orders":{},"strictly_exposed_development":True}
        for order in ("O","F"):
            for role in ("STRICT","BROAD"):
                scope=worlds[order]["roles"][role]
                prior=pred["root_orders"][order][role]
                eligible=prior["status"]=="FROZEN_SOURCE_ELIGIBLE"
                if not eligible:continue
                original=prior["M0"]
                opposite=prior["M1"]
                d11=prior["M2_depth11"]
                noncensored=not worlds[order]["passive_SEE_witness_censored"]
                first_candidate=native.get(scope["root_candidate_native"])
                alternatives=(opposite,d11)
                alt=opposite if opposite!=original else (d11 if d11 and d11!=original else original)
                corroborated=alt!=original and (alt==d11 and alt==opposite)
                depth_prefix=[source_depth[order][str(d)]["UCI"] for d in range(8,12)]
                earlier_alternative_count=sum(m==alt for m in depth_prefix)
                source_reader_linked=first_candidate==original
                actual=next(x for x in scored["roles"] if x["root_order"]==order and x["role"]==role) if "roles" in scored else None
                # Scored aggregation intentionally omits per-role outcomes, only game-level counts.
                # Any per-role false-positive correctness is already precommitted in overall result.
                key=(role, bool(source_reader_linked), bool(opposite!=original),bool(d11 and d11!=original),
                     bool(corroborated), min(earlier_alternative_count,4))
                table[str(key)]+=1
                num+=1
                if gid==107:
                    focal["root_orders"][order+"/"+role]={
                       "M0":original,"M1":opposite,"M2_depth11":d11,
                       "M3_v1":prior["M3_v1"],"M3_v2":prior["M3_v2"],
                       "original_root_source_reader_candidate_UCI":first_candidate,
                       "source_reader_matches_original_leader":source_reader_linked,
                       "candidate_alt":alt,"alt_equals_untreated_opposite_depth12":alt==opposite,
                       "alt_equals_same_order_depth11":alt==d11,
                       "earlier_8to11_depth_alt_count":earlier_alternative_count,
                       "alt_two_cue_corroborated":corroborated,
                       "passive_SEE_observer_censored":not noncensored,
                       "same_root_original_SEE_witness":prior["original_same_root_SEE_contact"],
                       "first_source_root_call":prior["root_source_call"]}
    if num!=501 or focal is None:raise ValueError("P4_D0_WRONG_TOTAL_OR_FOCAL_MISSING")
    target=focal["root_orders"]["O/STRICT"]
    if (target["M0"],target["M3_v2"])!=("d6c5","d6c7"):
        raise ValueError("P4_D0_FROZEN_ONE_FALSE_POSITIVE_CHANGED")
    return {"schema":"c3x024-P4-D0-fully-exposed-root-candidate-survival-development-v1",
      "source_games":128,"original_eligible_role_cells":501,
      "negative_result_preserved":{"M0_correct":449,"M3_v2_correct":448,
                                   "M3_v2_only_one_false_positive":"game107 O STRICT d6c7 loses to d6c5"},
      "source_input_SHA256":SRC_SHA,"untreated_stageA_SHA256":STAGE_SHA,
      "model_pre_FIRST_SHA256":FORECAST_SHA,"prospective_score_SHA256":OUTCOME_SHA,
      "case107_pretreatment_mechanistic_features":focal,
      "all_501_development_role_joint_untreated_feature_counts":dict(sorted(table.items())),
      "source_target_probe_only_development":True,
      "NO_NEW_HELDOUT_DATA_CONSUMED":True,
      "cannot_infer_unique_root_causation_or_natural_TT_SEE_mediation":True}
def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","forecast","seal","score","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    src=read(a.source,SRC_SHA)
    stage=read(a.stagea,STAGE_SHA)
    fc=read(a.forecast,FORECAST_SHA)
    seal=json.loads(Path(a.seal).read_text())
    score=read(a.score,OUTCOME_SHA)
    d=diagnose(src,stage,fc,seal,score)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("C3X024_P4_D0_EXPOSED_GAME107_SOURCE_DIAGNOSIS",json.dumps(d["case107_pretreatment_mechanistic_features"],sort_keys=True),flush=True)
    print("C3X024_P4_D0_DEVELOPMENT_501_JOINT_PRETREATMENT_FEATURE_COUNT",json.dumps(d["all_501_development_role_joint_untreated_feature_counts"],sort_keys=True),flush=True)
    print("C3X024_P4_D0_FULL_JSON_SHA256",hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
