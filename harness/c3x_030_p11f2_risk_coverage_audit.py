#!/usr/bin/env python3
"""C3X F2: coverage-aware, game-clustered comparison of proposed evidence fusion.

Extends F1's same-case four-way comparison. Requires a separate raw-byte-SHA
locked preregistered holdout manifest; it MUST NOT contain predictions, outcomes,
or true labels. This checks identity, not chronology or label independence.
No paper superiority is inferred merely because a conservative gate abstains.
"""
import argparse,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
from c3x_030_p11f1_evidence_fusion_audit import validate,decide,METHODS

SCHEMA="c3x030-f2-risk-coverage-grouped-audit-v1"
MANIFEST_SCHEMA="c3x030-f2-blind-holdout-manifest-v1"
FORBIDDEN={"label","sarfa_positive","independent_response_verified",
           "native_event_to_root_certified","bestmove","score","outcome",
           "expected_bestmove","judge_label"}
def sha(raw):return hashlib.sha256(raw).hexdigest()

def check_manifest(data,manifest):
    if manifest.get("schema")!=MANIFEST_SCHEMA or not isinstance(manifest.get("entries"),list):
        raise ValueError("F2_HOLD_MANIFEST_SCHEMA")
    if any(set(e)&FORBIDDEN for e in manifest["entries"] if isinstance(e,dict)):
        raise ValueError("F2_HOLD_OUTCOME_LEAK_IN_BLIND_MANIFEST")
    holdout={c["case_id"]:c for c in data["cases"] if c["split"]=="holdout"}
    source={}
    for row in manifest["entries"]:
        if not isinstance(row,dict) or not all(k in row for k in ("case_id","game_id","fen","history_uci")):
            raise ValueError("F2_HOLD_MANIFEST_CASE_FIELDS")
        if row["case_id"] in source:raise ValueError("F2_HOLD_DUPLICATE_MANIFEST_CASE")
        if not isinstance(row["history_uci"],list) or not all(type(m) is str for m in row["history_uci"]):
            raise ValueError("F2_HOLD_MANIFEST_UCI_HISTORY")
        source[row["case_id"]]=row
    if set(source)!=set(holdout):
        raise ValueError("F2_HOLD_HOLDOUT_CASE_NOT_FROZEN")
    for key,c in holdout.items():
        if source[key]["game_id"]!=c["game_id"] or source[key]["fen"]!=c["fen"]:
            raise ValueError("F2_HOLD_MUTATED_FEN_OR_GAME")
        if c.get("history_uci")!=source[key]["history_uci"]:
            raise ValueError("F2_HOLD_MUTATED_HISTORY")
    if len({c["game_id"] for c in holdout.values()})<2:
        raise ValueError("F2_HOLD_INSUFFICIENT_HOLDOUT_GAME_GROUPS")
    return source

def counts(cases,method):
    tall=Counter()
    for c in cases:
        result=decide(c,method)
        if result is None:
            tall["abstain"]+=1
        elif result:
            tall["tp" if c["label"]==1 else "fp"]+=1
        else:
            tall["fn" if c["label"]==1 else "tn"]+=1
    n=len(cases)
    positive=sum(c["label"] for c in cases)
    claimed=tall["tp"]+tall["fp"]
    decided=n-tall["abstain"]
    return {"n":n,"positives":positive,"tp":tall["tp"],"fp":tall["fp"],
            "fn_nonabstained":tall["fn"],"tn":tall["tn"],
            "abstain":tall["abstain"],
            "coverage":decided/n,
            "positive_claims":claimed,
            "false_claims_per_all_cases":tall["fp"]/n,
            "false_claim_rate_per_positive_claim":tall["fp"]/claimed if claimed else None,
            "false_decision_rate_among_nonabstained":(tall["fp"]+tall["fn"])/decided if decided else None,
            "positive_recall_all_cases_including_abstentions_as_missed":tall["tp"]/positive if positive else None,
            "abstained_true_positives":sum(c["label"] for c in cases if decide(c,method) is None),
            "all_case_positive_F1_abstain_as_missed":
                2*tall["tp"]/(2*tall["tp"]+tall["fp"]+tall["fn"]+
                              sum(c["label"] for c in cases if decide(c,method) is None))
                if 2*tall["tp"]+tall["fp"]+tall["fn"]+
                   sum(c["label"] for c in cases if decide(c,method) is None)>0 else None}

def compare(data,manifest,draws=1000,seed=20261112):
    validate(data)
    check_manifest(data,manifest)
    cases=[c for c in data["cases"] if c["split"]=="holdout"]
    by_game=defaultdict(list)
    for c in cases:by_game[c["game_id"]].append(c)
    groups=sorted(by_game)
    results={m:counts(cases,m) for m in METHODS}
    # Resample full game clusters, never individual correlated FEN snapshots.
    intervals={}
    if len(groups)>=8 and draws>=200:
        rng=random.Random(seed)
        for comparator in METHODS[:-1]:
            samples=[]
            for _ in range(draws):
                ids=[groups[rng.randrange(len(groups))] for _ in groups]
                rows=[c for game in ids for c in by_game[game]]
                # Pair methods on identical selected game draws.
                a=counts(rows,"three_gate_fusion")
                b=counts(rows,comparator)
                samples.append(a["false_claims_per_all_cases"]-b["false_claims_per_all_cases"])
            samples.sort()
            intervals[comparator]={"metric":"fusion_minus_comparator_false_claims_per_all_cases",
                  "percentile_95":[samples[int(.025*(draws-1))],samples[int(.975*(draws-1))]],
                  "resampling_unit":"complete_game","draws":draws,
                  "small_sample_and_selection_bias_not_eliminated":True}
    else:
        intervals={"status":"HOLD_FEWER_THAN_8_INDEPENDENT_GAMES_OR_DRAWS"}
    return {"schema":SCHEMA,"n_distinct_holdout_games":len(groups),
            "same_cases":True,"methods":results,
            "paired_grouped_intervals":intervals,
            "not_verified_chronological_precommit_by_offline_hash":True,
            "not_verified_independent_labels_by_self_attestation":True,
            "no_paper_superiority_claim":True,
            "precommitted_FENs_not_evidence_of_benchmark_improvement":True,
            "note":"Coverage and false-claim risk must both be reported. At low coverage, conditional precision can mislead."}

def main():
    p=argparse.ArgumentParser()
    for k in ("data","manifest","manifest-sha","out"):p.add_argument("--"+k,required=True)
    a=vars(p.parse_args())
    raw=Path(a.manifest).read_bytes()
    if sha(raw)!=a.manifest_sha:raise ValueError("F2_HOLD_MANIFEST_RAW_BYTES_CHANGED")
    d=json.loads(Path(a.data).read_bytes());m=json.loads(raw)
    result=compare(d,m)
    result["manifest_raw_sha256"]=a.manifest_sha
    result["data_raw_sha256"]=sha(Path(a.data).read_bytes())
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("C3X_F2_RISK_COVERAGE",sha(out.read_bytes()),"SUPERIORITY_HOLD",result["no_paper_superiority_claim"])
if __name__=="__main__":main()
