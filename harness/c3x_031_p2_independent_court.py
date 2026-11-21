"""C3X 0.31/P2 independent raw native contrast and sealed forecast audit.

Read original P2 pre-intervention contacts, independently executed treatment
raw results, and all 1152 original UCI/stderr log files. Not a new engine run.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import re

SOURCE_SHA = "17915c7d9ae56dd950cd026d07a4917a414213415ea3b28af256b305eb8ad146"
TREAT_SHA = "69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f"
SOURCE_BINARY_SHA = "ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1"
MODEL_SHA = "f27a89fd15efa3f35738ba8cf2a6d1243c8336268e4661c653bbd1e6c0bfee23"
PRE_FREEZE_GAMES_SHA = "2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4"
PREDECLARED_MACRO = {
    "iii ch-sudamericano women": "iii ch-sudamericano",
    "iii ch-sudamericano blitz": "iii ch-sudamericano",
    "fide world open u20 rapid": "fide world open u20",
    "fide world open u20 blitz": "fide world open u20",
    "world girls u20 rapid": "world girls u20",
    "world girls u20 blitz": "world girls u20",
    "future stars chn w rapid": "future stars chn w",
    "future stars chn w blitz": "future stars chn w",
    "tal memorial rapid 2026": "tal memorial 2026",
    "tal memorial blitz 2026": "tal memorial 2026",
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, why):
    if not ok:
        raise ValueError(why)

def normalize(stdout):
    return [re.sub(r"\b(?:nps|time) \d+ ?", "", line)
            for line in stdout.decode().splitlines()
            if line.startswith(("info depth ", "bestmove "))]

def score(rows, key):
    n=len(rows)
    labels=[r["y"] for r in rows]
    probs=[r[key] for r in rows]
    brier=sum((p-y)**2 for p,y in zip(probs,labels))/n
    loss=-sum(y*math.log(max(1e-12,min(1-1e-12,p)))+
        (1-y)*math.log(max(1e-12,min(1-1e-12,1-p)))
        for y,p in zip(labels,probs))/n
    grouped=defaultdict(lambda:[0,0])
    for row in rows:
        grouped[row[key]][0]+=1
        grouped[row[key]][1]+=row["y"]
    retrieved=tp=0
    AP=0.0
    for prob in sorted(grouped,reverse=True):
        count,positive=grouped[prob]
        retrieved+=count
        tp+=positive
        if positive:
            AP+=(positive/max(1,sum(labels)))*(tp/retrieved)
    return {"brier":brier,"log_loss":loss,"average_precision":AP if sum(labels) else None,
            "positive_count":sum(labels),"predicted_positive":sum(p>=.5 for p in probs),
            "true_positive_at_0_5":sum(y and p>=.5 for y,p in zip(labels,probs))}

def interval(rows,group_field,seed):
    groups=sorted({r[group_field] for r in rows})
    bygroup={g:[r for r in rows if r[group_field]==g] for g in groups}
    rng=random.Random(seed)
    draws={"m0_minus_m2":[],"m1_minus_m2":[]}
    for _ in range(2000):
        sample=[r for key in (rng.choice(groups) for _ in groups) for r in bygroup[key]]
        for label,k in (("m0_minus_m2","m0"),("m1_minus_m2","m1")):
            draws[label].append(score(sample,k)["brier"]-score(sample,"m2")["brier"])
    return {key:{"difference":score(rows,key[:2])["brier"]-score(rows,"m2")["brier"],
                 "bootstrap_95":[sorted(seq)[50],sorted(seq)[1949]]}
            for key,seq in draws.items()}

def verify(source,treatment,logroot):
    require(source["stage"]=="P2_PHYSICAL_EVENT_SELECTED_WITHOUT_TREATMENT"
            and source["real_treatment_searches"]==0,
            "pretreated source not frozen")
    require(source["game_freeze_sha256"]==PRE_FREEZE_GAMES_SHA
            and source["frozen_model_sha256"]==MODEL_SHA,
            "pre-treatment source context changed")
    require(treatment["before_treatment_source_discovery_sha256"]==SOURCE_SHA
            and treatment["original_p1_train_model_sha256"]==MODEL_SHA
            and treatment["stockfish16_source_patched_binary_sha256"]==SOURCE_BINARY_SHA,
            "model/source comparison not pre-frozen")
    require(len(source["source_events"])==len(treatment["cases"])==64,
            "original game denominator truncated")
    require(len({r["game_sha256"] for r in source["source_events"]})==64,
            "duplicate full game")
    original={r["id"]:r for r in source["source_events"]}
    logs={p.relative_to(logroot).as_posix():p for p in Path(logroot).rglob("*.txt")}
    require(len(logs)==1152,"missing one or more native source log files")
    counts=Counter()
    rows=[]; flips=[]; comparison=[]
    for case in treatment["cases"]:
        ident=case["id"]
        require(ident in original,"unexpected post-selected game")
        s=original[ident]
        require(case["game_sha256"]==s["game_sha256"] and
                case["family"]==s["family"],"history/family changed")
        logname=f"{ident}/untargeted-sham/stdout.txt"
        require(logname in logs,"missing sham UCI")
        sham_uci=normalize(logs[logname].read_bytes())
        require(sham_uci==case["sham_public_uci"],"sham UCI not original native raw")
        require(case["sham_result"]==s["baseline_bestmove"],
                "no-contact sham altered final choice")
        require(sha(("\n".join(sham_uci)+"\n").encode())==s["untouched_uci_sha256"],
                "sham changed untreated UCI trajectory")
        counts["sham_verified"]+=1
        for g in ("0","1"):
            before=s["targets"][g]
            after=case["targets"][g]
            require(before["status"]=="UNTREATED_NATIVELY_OBSERVED_FORECAST_FROZEN"
                    and after["status"]=="ACTUAL_SOURCE_TREATMENT_OBSERVED",
                    "missing physical target on new source")
            require(before["target"]==after["original_target"]
                    and before["predicted_bestmove_flip_probabilities"]==
                        after["frozen_predictions"],
                    "forecast or nominated source target replaced post-treatment")
            require(before["before_treatment_features"]==
                    after["frozen_pre_contact_features"],
                    "native source predictor is a treated variable")
            arms=after["arms"]
            for label in ("futility_only","both_off"):
                arm=arms[label]
                require(len(arm["full_repeats"])==2,
                        "physical native cold repeats missing")
                compare=[]
                for repeat,receipt in enumerate(arm["full_repeats"]):
                    dirname=f"{ident}/{g}/{label}-{repeat}"
                    stderr_name=dirname+"/stderr.txt"
                    stdout_name=dirname+"/stdout.txt"
                    require(stderr_name in logs and stdout_name in logs,
                            "missing physically executed source pair")
                    require(sha(logs[stderr_name].read_bytes())==
                            receipt["stderr_sha256"],
                            "source original stderr byte SHA changed")
                    normalized=normalize(logs[stdout_name].read_bytes())
                    require(normalized==receipt["public_uci"]
                            and normalized[-1].split()[1]==arm["final_move"],
                            "native output not parsed faithfully")
                    require(receipt["event"]["open"]==before["target"],
                            "original pre-contact event signature changed")
                    closed=receipt["event"]["close"]
                    require(closed["skip_f"]=="1"
                            and closed["skip_n"]==str(int(label=="both_off"))
                            and closed["stopped"]=="0",
                            "treatment not physically contacted/observable")
                    require(receipt["source_best"]["move"]==arm["final_move"],
                            "source root producer disagrees with public recommendation")
                    compare.append((
                        receipt["public_uci"],receipt["source_best"],
                        receipt["source_best_producer"],receipt["event"],
                        receipt["source_root_counts"]))
                    counts["treated_native_runs_verified"]+=1
                require(compare[0]==compare[1],
                        "paired native cold repeats are not deterministic")
            if g=="0":
                x,y=arms["futility_only"],arms["both_off"]
                for key in ("direct_child_return","null_tried","null_cut",
                            "real_child_board_replies","final_move",
                            "final_completed_depth"):
                    require(x[key]==y[key],
                            "null-ineligible condition is not a real negative control")
            origin_return=before["direct_open_close_pair"]["close"]["value"]
            main=arms["both_off"]
            y=int(main["final_move"]!=s["baseline_bestmove"])
            require(y==int(after["treatment_bestmove_changed"]),
                    "post-treatment effect label changed")
            counts["root_flip_g"+g]+=y
            counts["futility_only_flip_g"+g]+=int(arms["futility_only"]["final_bestmove_changed"])
            counts["direct_child_return_changed_g"+g]+=int(
                origin_return!=main["direct_child_return"])
            counts["root_flip_with_same_completed_depth"]+=int(y and
                int(main["final_completed_depth"])==int(s["untouched_public"][0]))
            counts["root_flip_with_different_completed_depth"]+=int(y and
                int(main["final_completed_depth"])!=int(s["untouched_public"][0]))
            rows.append({"id":ident+"-"+g, "family":case["family"],
                         "macro_family":PREDECLARED_MACRO.get(case["family"],case["family"]),
                         "game":case["game_sha256"], "stratum":g, "y":y,
                         **after["frozen_predictions"]})
            if y:
                flips.append({
                    "event":ident+"-"+g,"family":case["family"],
                    "original_bestmove_uci":s["baseline_bestmove"],
                    "treated_bestmove_uci":main["final_move"],
                    "original_completed_depth":int(s["untouched_public"][0]),
                    "treated_completed_depth":int(main["final_completed_depth"]),
                    "original_child_return":origin_return,
                    "treatment_child_return":main["direct_child_return"],
                    "frozen_M2_probability":after["frozen_predictions"]["m2"],
                })
    require(counts["sham_verified"]==64
            and counts["treated_native_runs_verified"]==512
            and len(rows)==128,
            "raw native search denominator truncated")
    require(counts["root_flip_g0"]==3 and counts["root_flip_g1"]==4
            and counts["root_flip_with_same_completed_depth"]==1,
            "signed P2 outcome does not match original raw replay")
    require(len({r["game"] for r in rows})==64
            and len({r["family"] for r in rows})==17
            and len({r["macro_family"] for r in rows})==12,
            "original group denominator or macro sensitivity changed")
    require(treatment["observed_effect_denominator"]==128
            and treatment["new_source_native_searches_attempted"]==576,
            "original physical search total mismatched")
    overall={m:score(rows,m) for m in ("m0","m1","m2")}
    original=treatment["result_over_eligible_events"]
    for m in overall:
        for stat in ("brier","log_loss","average_precision"):
            require(abs(overall[m][stat]-original["scores"][m][stat])<1e-12,
                    "published predictor score disagrees with original raw records")
    groups=interval(rows,"family",310221)
    for key,values in groups.items():
        o=original["Brier_effect_differences"][key]
        require(abs(values["difference"]-o["observed"])<1e-12
                and all(abs(a-b)<1e-12 for a,b in zip(
                    values["bootstrap_95"],o["family_cluster_bootstrap95"])),
                "registered 17-group uncertainty rerun is inconsistent")
    sensitivity=interval(rows,"macro_family",310222)
    require(sum(r["y"] for r in rows)==7,"unexpected number of physical total effects")
    return {
        "id":"C3X_031_P2_INDEPENDENT_NATIVE_LOG_AND_FORECAST_COURT",
        "evidence":"EXACT_ORIGINAL_SOURCE_LOGS_DERIVED_AUDIT_NO_NEW_STOCKFISH_SEARCH",
        "original_P2_source_sha256":SOURCE_SHA,
        "original_P2_treated_sha256":TREAT_SHA,
        "new_native_searches_in_this_court":0,
        "verified_original_source_searches":192,
        "verified_original_treatment_and_sham_searches":576,
        "original_verified_raw_stderr_and_UCI_files":len(logs),
        "event_family_groups":17,"predeclared_macro_group_sensitivity":12,
        "physical_event_count":len(rows),
        "event_outcome_counts":dict(counts),
        "actual_root_choice_flips":flips,
        "predictor_metrics_recomputed_from_original_raw":overall,
        "original_17_family_bootstrap_recomputed":groups,
        "secondary_12_macro_family_bootstrap":sensitivity,
        "predeclared_P2_predictive_gain_pass":False,
        "P2_science_verdict":"NEGATIVE_PROSPECTIVE_TRANSPORT",
        "identified_TT_history_budget_mediator":False,
        "independent_chess_move_merit_measured":False,
        "human_learning_value_measured":False,
        "scope":"New game-family source effects within 32k-node bounded search; six of seven flips differ in completed depth."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("treated",type=Path)
    p.add_argument("logs",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    original=a.source.read_bytes()
    treated=a.treated.read_bytes()
    require(sha(original)==SOURCE_SHA,"original pre-contact JSON bytes not preserved")
    require(sha(treated)==TREAT_SHA,"original treated native JSON bytes not preserved")
    result=verify(json.loads(original),json.loads(treated),a.logs)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("P2_INDEPENDENT_RAW_COURT",result["P2_science_verdict"],
          "flips",len(result["actual_root_choice_flips"]),
          "original_searches",result["verified_original_treatment_and_sham_searches"],
          "output_sha256",sha(a.output.read_bytes()))

if __name__=="__main__":
    main()
