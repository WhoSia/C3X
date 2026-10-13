"""I10-P4 experimentally trainable NINE-parameter evidence-only claim selector.

This is an intentionally narrow listwise linear model. Trained against *declared
proxy question-to-claim labels*, never human chess preferences, chess Elo or
source-causal validity. It only chooses already-compiled claim IDs.
No dependency on torch, sentence embeddings, large models or API calls.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Any

SCHEMA="c3x-ecl-i10-p4-tiny-listwise-linear-v1"
QUESTIONS=("ENGINE_PREFERENCE","PLAYED_CONTINUATION","ALTERNATIVE_CONTINUATION")
ROLES=("SCORE","PLAYED_PV","ALTERNATIVE_PV")
DIM=9

def classify_claim(packet:dict[str,Any],claim:dict[str,Any])->str|None:
    if claim.get("kind")=="ENGINE_RESTRICTED_SNAPSHOT":
        return "SCORE"
    if claim.get("kind")!="SOURCE_PV_LEGAL_REPLAY":
        return None
    cid=claim.get("claim_id","")
    played=packet.get("played_uci")
    if not played or not isinstance(cid,str):
        return None
    if cid.endswith(":pv:"+played):
        return "PLAYED_PV"
    if cid.endswith(":pv:"+str(packet.get("leader"))) or cid.endswith(":pv:"+str(packet.get("rival"))):
        return "ALTERNATIVE_PV"
    return None

def _allowed_claims(packet:dict[str,Any])->list[dict[str,Any]]:
    if (packet.get("verdict")!="EMIT_BOUNDED_CONVENTIONAL" or
        packet.get("source_causal_claim") is not False or
        packet.get("confidence_probability") is not None):
        return []
    claims=packet.get("claims")
    if not isinstance(claims,list) or not claims:
        return []
    seen=set()
    for x in claims:
        if not isinstance(x,dict) or not isinstance(x.get("claim_id"),str):
            return []
        if not x.get("atom_ids") or not isinstance(x.get("text_ko"),str):
            return []
        if x["claim_id"] in seen or classify_claim(packet,x) not in ROLES:
            return []
        if x.get("authority") not in ("ENGINE_RANKING_AT_RECORDED_DEPTH_ONLY",
                                    "SINGLE_REPLAYED_ENGINE_LINE_ONLY"):
            return []
        seen.add(x["claim_id"])
    return claims

def _feature(question:str,role:str)->list[float]:
    if question not in QUESTIONS or role not in ROLES:
        raise ValueError("UNKNOWN_QUESTION_OR_ROLE")
    values=[0.0]*DIM
    values[QUESTIONS.index(question)*len(ROLES)+ROLES.index(role)]=1.0
    return values

def weak_proxy_examples(packets:list[dict[str,Any]],group_id:str)->list[dict[str,Any]]:
    """Explicit predeclared question targets, not human adjudication.

    Labels are deterministic structural 'answer matches requested claim type'
    targets; they do NOT certify educational usefulness, relative chess quality,
    or correctness of the upstream UCI engine beyond the original gates.
    """
    out=[]
    for p in packets:
        claims=_allowed_claims(p)
        if not claims:continue
        for q,role in zip(QUESTIONS,ROLES):
            target=next((c["claim_id"] for c in claims if classify_claim(p,c)==role),None)
            if target:
                out.append({"source_group_id":group_id,
                            "ply":p.get("ply"),"question":q,
                            "claim_roles":[classify_claim(p,c) for c in claims],
                            "target_claim_role":role,
                            "target_claim_id":target,
                            "source_candidate_ids":[c["claim_id"] for c in claims]})
    return out

def _validate_model(model:dict[str,Any])->list[float]:
    if not isinstance(model,dict) or model.get("schema")!=SCHEMA:
        raise ValueError("WRONG_MODEL_SCHEMA")
    weights=model.get("weights")
    if not isinstance(weights,list) or len(weights)!=DIM:
        raise ValueError("WRONG_MODEL_DIMENSION")
    if any(type(w) not in (int,float) or not math.isfinite(w) or abs(w)>1e5 for w in weights):
        raise ValueError("INVALID_NONFINITE_OR_UNBOUNDED_WEIGHT")
    if model.get("feature_names")!=[f"{q}/{r}" for q in QUESTIONS for r in ROLES]:
        raise ValueError("FEATURE_SCHEMA_MISMATCH")
    if model.get("trained_parameter_count")!=DIM or model.get("proxy_labels_only") is not True:
        raise ValueError("MODEL_AUTHORITY_MISMATCH")
    digest=model.get("sha256_canonical")
    if digest is not None:
        unsigned={k:v for k,v in model.items() if k!="sha256_canonical"}
        expected=hashlib.sha256(json.dumps(unsigned,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if digest!=expected:
            raise ValueError("MODEL_ARTIFACT_SHA256_MISMATCH")
    return [float(w) for w in weights]

def train(examples:list[dict[str,Any]],*,epochs:int=100,rate:float=0.35)->dict[str,Any]:
    if not isinstance(examples,list) or not 1<=len(examples)<=10000:
        raise ValueError("INSUFFICIENT_OR_EXCESSIVE_TRAINING_EXAMPLES")
    if not isinstance(epochs,int) or not 1<=epochs<=500 or not 0<rate<=1:
        raise ValueError("TRAINING_HYPERPARAMETER_NOT_ADMITTED")
    # Prevent duplicate game/puzzle pseudo-replication from masquerading as
    # independent supervision. All examples from one source are one source group.
    groups=sorted({str(e.get("source_group_id")) for e in examples})
    rows=[]
    for e in examples:
        q=e.get("question"); roles=e.get("claim_roles")
        if q not in QUESTIONS or not isinstance(roles,list) or not roles or any(r not in ROLES for r in roles):
            raise ValueError("INVALID_PROXY_TRAINING_QUESTION_OR_ROLES")
        if len(roles)!=len(set(roles)) or e.get("target_claim_role") not in roles:
            raise ValueError("AMBIGUOUS_OR_UNAVAILABLE_PROXY_TARGET")
        rows.append((q,roles,roles.index(e["target_claim_role"])))
    # Explicitly initialize without priors or random seeds.
    w=[0.0]*DIM
    for _ in range(epochs):
        for q,roles,target in rows:
            idx=[QUESTIONS.index(q)*3+ROLES.index(r) for r in roles]
            scores=[w[i] for i in idx]
            shift=max(scores)
            v=[math.exp(x-shift) for x in scores]
            z=sum(v)
            for j,i in enumerate(idx):
                w[i] += rate*((1.0 if j==target else 0.0)-v[j]/z)
    model={
      "schema":SCHEMA,
      "weights":[round(x,10) for x in w],
      "feature_names":[f"{q}/{r}" for q in QUESTIONS for r in ROLES],
      "trained_parameter_count":DIM,
      "training_example_count":len(rows),
      "training_source_group_count":len(groups),
      "training_source_groups":groups,
      "proxy_labels_only":True,
      "calibrated_probability":None,
      "independent_human_training":False,
      "objective_chess_superiority":None,
      "model_type":"TRAINED_LISTWISE_LINEAR_CLAIM_ROUTER_NOT_CHESS_VALUATION",
    }
    _validate_model(model)
    model["sha256_canonical"]=hashlib.sha256(json.dumps(model,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return model

def select(packet:dict[str,Any],question:str,*,model:dict[str,Any]|None=None)->dict[str,Any]:
    if question not in QUESTIONS:
        raise ValueError("UNRECOGNIZED_USER_QUESTION")
    # Reject malformed/forged packets fail-closed regardless of learned scores.
    claims=_allowed_claims(packet)
    if not claims:
        return {"schema":"c3x-ecl-i10-p4-selection-v1","decision":"ABSTAIN",
                "reason":"UPSTREAM_EVIDENCE_NOT_ADMITTED",
                "selected_claim_ids":[],"text_ko":None,"source_causal_claim":False,
                "confidence_probability":None}
    if model is None:
        # Frozen I10-P3 baseline priority exactly as built (first compiled claim).
        chosen=claims[0];mode="P3_STATIC_TOP_PRIORITY_BASELINE"
    else:
        weights=_validate_model(model)
        qstart=QUESTIONS.index(question)*3
        ranked=sorted(claims,key=lambda c:(-weights[qstart+ROLES.index(classify_claim(packet,c))],c["claim_id"]))
        chosen=ranked[0];mode="P4_TRAINED_9_PARAMETER_PROXY_SELECTOR"
    # User query targets are NOT retrofitted into a convenient good-looking answer.
    question_role=dict(zip(QUESTIONS,ROLES))[question]
    choice_role=classify_claim(packet,chosen)
    return {
       "schema":"c3x-ecl-i10-p4-selection-v1",
       "decision":"EMIT_BOUNDED_CONVENTIONAL","reason":"EXACT_COMPILED_CLAIM_ID",
       "mode":mode,"question":question,
       "selected_claim_ids":[chosen["claim_id"]],
       "claim_role":choice_role,
       "weak_proxy_question_match":choice_role==question_role,
       "text_ko":chosen["text_ko"],
       "evidence_atom_ids":list(chosen["atom_ids"]),
       "source_causal_claim":False,
       "confidence_probability":None,
       "human_outcome":None,
       "scope":"ONE_VERIFIED_CONVENTIONAL_SOURCE_CLAIM_ONLY",
    }

def benchmark(packets:list[dict[str,Any]], model:dict[str,Any], test_group:str)->dict[str,Any]:
    _validate_model(model)
    if test_group in model.get("training_source_groups",[]):
        raise ValueError("TRAIN_TEST_GAME_GROUP_LEAKAGE")
    examples=weak_proxy_examples(packets,test_group)
    rows=[]
    for e in examples:
        p=next((x for x in packets if x.get("ply")==e["ply"] and
                e["target_claim_id"] in {c.get("claim_id") for c in x.get("claims",[])}),None)
        if p is None:raise ValueError("MISSING_BENCHMARK_PACKET")
        for m in (None,model):
            result=select(p,e["question"],model=m)
            rows.append({"group_id":test_group,"ply":e["ply"],"question":e["question"],
                         "mode":result["mode"],
                         "selected":result["selected_claim_ids"][0],
                         "proxy_match":result["weak_proxy_question_match"],
                         "causal":result["source_causal_claim"]})
    agg={}
    for mode in ("P3_STATIC_TOP_PRIORITY_BASELINE","P4_TRAINED_9_PARAMETER_PROXY_SELECTOR"):
        subset=[x for x in rows if x["mode"]==mode]
        agg[mode]={"proxy_correct":sum(x["proxy_match"] for x in subset),
                   "proxy_total":len(subset),
                   "proxy_match_rate":None if not subset else sum(x["proxy_match"] for x in subset)/len(subset)}
    return {"schema":"c3x-ecl-i10-p4-proxy-comparator-v1",
            "independent_test_group":test_group,
            "proxy_comparison":agg,"cases":rows,
            "original_engine_evidence_equal":True,
            "outputs_same_source_claim_set":True,
            "actual_Queen_Cui_CCC_called":False,
            "real_human_comprehension_gain":None,
            "claims_of_chess_playing_strength":None}
