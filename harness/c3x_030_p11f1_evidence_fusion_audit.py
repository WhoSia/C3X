#!/usr/bin/env python3
"""C3X 0.30 P11/F1: fail-closed paired, group-aware evidence fusion comparison.

This evaluates an EXISTING independently labeled experiment; it does NOT
make up independent labels, physical TT causation, or chess evidence.
Claim gate = SARFA positive + independent reply evidence + native causal
chain certificate. All four methods see the SAME cases. Unknown != false.
Permits abstention; reports precision, recall, F1, coverage, false positive
rate over positives/negatives, grouped game cases. No significance or
superiority claim without blind independent heldout data.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path

SCHEMA="c3x030-f1-source-response-grounding-paired-audit-v1"
METHODS=("sarfa_only","response_only","native_only","three_gate_fusion")
DIMENSIONS=("sarfa_positive","independent_response_verified","native_event_to_root_certified")

def hashfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(data):
    if data.get("schema")!=SCHEMA or not isinstance(data.get("cases"),list):
        raise ValueError("F1_HOLD_INPUT_SCHEMA")
    if len(data["cases"])<4:raise ValueError("F1_HOLD_TOO_FEW_CASES")
    if data.get("labels_independent_of_method_generation") is not True:
        raise ValueError("F1_HOLD_JUDGE_NOT_INDEPENDENT")
    if data.get("same_chess_cases_for_all_methods") is not True:
        raise ValueError("F1_HOLD_UNMATCHED_METHOD_SUPPORT")
    if data.get("source_and_judge_engines_distinct") is not True:
        raise ValueError("F1_HOLD_SOURCE_JUDGE_LEAK")
    seen=set();split_games=defaultdict(set)
    for c in data["cases"]:
        for field in ("case_id","game_id","split","fen","label"):
            if field not in c:raise ValueError("F1_HOLD_MISSING_CASE_FIELD:"+field)
        if c["case_id"] in seen or not isinstance(c["case_id"],str) or not c["case_id"]:
            raise ValueError("F1_HOLD_DUPLICATE_CASE_ID")
        seen.add(c["case_id"])
        if c["split"] not in ("development","holdout"):
            raise ValueError("F1_HOLD_UNKNOWN_SPLIT")
        if not isinstance(c["game_id"],str) or not c["game_id"]:
            raise ValueError("F1_HOLD_GAME_ID")
        split_games[c["game_id"]].add(c["split"])
        if c["label"] not in (0,1) or type(c["label"]) is not int:
            raise ValueError("F1_HOLD_UNGROUNDED_REFERENCE_LABEL")
        if any(c.get(dim) not in (True,False,None) for dim in DIMENSIONS):
            raise ValueError("F1_HOLD_INVALID_OR_UNKNOWN_EVIDENCE")
        if any(type(c.get(dim)) not in (bool,type(None)) for dim in DIMENSIONS):
            raise ValueError("F1_HOLD_EVIDENCE_MUST_BE_BOOLEAN_OR_UNKNOWN")
        if not isinstance(c["fen"],str) or not c["fen"]:
            raise ValueError("F1_HOLD_FEN_IDENTITY")
        raw=c.get("original_receipt_sha256")
        if type(raw) is not str or len(raw)!=64 or any(v not in "0123456789abcdef" for v in raw):
            raise ValueError("F1_HOLD_MISSING_RAW_EVIDENCE_SHA")
    if any(len(s)>1 for s in split_games.values()):
        raise ValueError("F1_HOLD_SAME_GAME_IN_DEVELOPMENT_AND_HOLDOUT")
    if "holdout" not in {c["split"] for c in data["cases"]}:
        raise ValueError("F1_HOLD_NO_HELDOUT_CASES")
    if not data.get("holdout_cases_precommitted_before_outcomes"):
        raise ValueError("F1_HOLD_HOLDOUT_NOT_PRECOMMITTED")
    return split_games

def decide(case,method):
    if method=="sarfa_only":inputs=(case["sarfa_positive"],)
    elif method=="response_only":inputs=(case["independent_response_verified"],)
    elif method=="native_only":inputs=(case["native_event_to_root_certified"],)
    elif method=="three_gate_fusion":inputs=tuple(case[k] for k in DIMENSIONS)
    else:raise ValueError("F1_HOLD_UNKNOWN_METHOD")
    if any(v is False for v in inputs):return False
    if any(v is None for v in inputs):return None
    return True

def metric(cases,method):
    tallies=Counter()
    for c in cases:
        pred=decide(c,method)
        if pred is None:tallies["abstain"]+=1;continue
        if pred and c["label"]==1:tallies["tp"]+=1
        elif pred:tallies["fp"]+=1
        elif c["label"]==1:tallies["fn"]+=1
        else:tallies["tn"]+=1
    n=len(cases)
    tp,fp,fn=tallies["tp"],tallies["fp"],tallies["fn"]
    pr=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    return {"n":n,"distinct_games":len({x["game_id"] for x in cases}),
            "coverage":(n-tallies["abstain"])/n,
            "abstentions":tallies["abstain"],
            "tp":tp,"fp":fp,"fn":fn,"tn":tallies["tn"],
            "precision":pr,"recall_among_non_abstained":recall,"f1_among_non_abstained":f1,
            "not_population_confidence_interval":True}

def evaluate(data):
    validate(data)
    outputs={}
    for subset in ("development","holdout"):
        c=[x for x in data["cases"] if x["split"]==subset]
        outputs[subset]={m:metric(c,m) for m in METHODS} if c else None
    return {"schema":"c3x030-f1-comparison-audit-output-v1",
            "comparators":list(METHODS),
            "metrics_by_split":outputs,
            "uses_actual_benchmarked_originals":True,
            "no_superiority_or_significance_claim":True,
            "no_dose_or_TT_causality_inferred_from_SARFA":True,
            "grouping_unit":"game_id","missing_evidence_abstains_not_fails":True,
            "must_independently_review_factual_labels":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    data=json.loads(Path(args.input).read_text())
    result=evaluate(data)
    result["source_raw_json_sha256"]=hashfile(args.input)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("C3X_F1_PAIRED_AUDIT",hashfile(out),"HOLD_SUPERIORITY_UNTIL_PRECOMMITTED_REAL_LABELS")
if __name__=="__main__":main()
