"""I10-P3 ECL: evidence-compiled, small-model-ready chess explanations.

Every accepted sentence is backed by a typed record. This code is a compact,
untrained *static* ranking baseline, not a chess LM, calibrated classifier or
source-causal theorem. The existing I9 and I10 gates retain authority.
"""
from __future__ import annotations
import json
from typing import Any
import chess
from .judgment import judge_moment

SCHEMA = "c3x-ecl-i10-p3-evidence-compiler-v1"
SELECTOR_SCHEMA = "c3x-ecl-i10-p3-static-lightweight-selector-v1"
CAUSAL = "C3X_CAUSAL_CONTRAST"
CONVENTIONAL = "CONVENTIONAL_HEURISTIC_COMMENTARY"
# Explicitly static weights; never claim these are fitted or calibrated.
STATIC_WEIGHTS = {"score": 2, "reply": 3, "concept": 1}

def _abstain(moment:dict[str,Any],reason:str,judgment:dict[str,Any]|None=None)->dict[str,Any]:
    return {"schema":SCHEMA,"ply":moment.get("ply"),
            "played_uci":moment.get("played_uci"),"verdict":"ABSTAIN",
            "reason":reason,"judgment_reason":(judgment or {}).get("reason"),
            "claims":[],"selected_claim_ids":[],"withheld_causal_certificate_ids":[],
            "text_ko":None,"model_kind":"UNTRAINED_STATIC_SELECTOR_NO_LM",
            "confidence_probability":None,"human_utility":None,
            "source_causal_claim":False}

def compile_evidence(moment:dict[str,Any],judgment:dict[str,Any]|None=None)->dict[str,Any]:
    """Compile already-gated I9/I10 context. No applicant supplies permission.

    The mere presence of graph certificate node + atom does NOT authorize causal
    wording. This deliberately refuses source causal claims until the separate
    exact-byte repository approval + independent scope adapter is installed.
    """
    j=judge_moment(moment) if judgment is None else judgment
    if (moment.get("firewall",{}).get("pass") is not True or
        moment.get("realization_verification",{}).get("pass") is not True):
        return _abstain(moment,"LEGACY_EVIDENCE_OR_REALIZATION_GATE_FAIL",j)
    if j.get("decision")!="ENGINE_SNAPSHOT_PREFERENCE_ONLY":
        return _abstain(moment,"I10_SOURCE_RIVAL_JUDGMENT_UNAVAILABLE",j)
    if j.get("played_uci")!=moment.get("played_uci"):
        return _abstain(moment,"JUDGMENT_ORIGIN_PLAYED_MOVE_MISMATCH",j)
    rows=moment.get("candidates") or []
    candidates={r.get("uci"):r for r in rows if isinstance(r,dict) and isinstance(r.get("uci"),str)}
    leader=j.get("preferred_move"); rival=j.get("challenger")
    if (not leader or not rival or leader==rival or
        leader not in candidates or rival not in candidates or
        moment.get("played_uci") not in (leader,rival) or
        type(j.get("candidate_gap_cp")) is not int or j["candidate_gap_cp"]<=0):
        return _abstain(moment,"INCONSISTENT_RIVAL_CONTEXT",j)
    try:
        b=chess.Board(moment["fen"])
        if not b.is_valid() or any(chess.Move.from_uci(u) not in b.legal_moves for u in (leader,rival)):
            return _abstain(moment,"RIVAL_NOT_LEGAL_IN_ORIGINAL_BOARD",j)
    except (ValueError,KeyError,TypeError):
        return _abstain(moment,"UNREADABLE_ORIGINAL_FEN",j)
    source_ids={a.get("atom_id") for a in moment.get("atoms",[])
                if isinstance(a,dict) and isinstance(a.get("atom_id"),str)}
    bound_ids=set(j.get("evidence_atom_ids") or [])
    # Unproven, missing or mixed provenance MUST NOT be converted to claims.
    if not bound_ids or not bound_ids.issubset(source_ids):
        return _abstain(moment,"JUDGMENT_ATOM_PROVENANCE_MISMATCH",j)
    names={u:b.san(chess.Move.from_uci(u)) for u in (leader,rival)}
    claimed_names={leader:j.get("preferred_san"),rival:j.get("challenger_san")}
    if any(claimed_names[u]!=names[u] for u in (leader,rival)):
        return _abstain(moment,"SOURCE_SAN_CONFLICT",j)
    claims=[{
        "claim_id":f"ply:{moment['ply']}:score",
        "kind":"ENGINE_RESTRICTED_SNAPSHOT",
        "atom_ids":sorted(bound_ids),
        "text_ko":(f"제한된 원본 엔진 분석에서 {names[leader]}가 {names[rival]}보다 "
                   f"{j['candidate_gap_cp']}cp 높게 평가됐습니다. 이는 최선수의 증명이 아닙니다."),
        "priority":STATIC_WEIGHTS["score"],
        "authority":"ENGINE_RANKING_AT_RECORDED_DEPTH_ONLY",
    }]
    # I10 first verifies all source PV moves. Do not manufacture another line
    # or call the shown response forced. The observed game may differ from PV.
    for line in j.get("legally_replayed_candidate_lines") or []:
        if not isinstance(line,dict) or line.get("candidate") not in (leader,rival):
            continue
        if line.get("semantic_scope")!="CHESS_LEGALITY_REPLAY_ONLY_NOT_FORCED_REFUTATION":
            continue
        sans=line.get("san_line")
        if not isinstance(sans,list) or not sans or sans[0]!=names[line["candidate"]]:
            continue
        claims.append({
            "claim_id":f"ply:{moment['ply']}:pv:{line['candidate']}",
            "kind":"SOURCE_PV_LEGAL_REPLAY",
            "atom_ids":sorted(bound_ids),
            "text_ko":f"{names[line['candidate']]}의 엔진 탐색 변형: {' '.join(sans[:6])}. 필연적인 반박은 아닙니다.",
            "priority":STATIC_WEIGHTS["reply"] if len(sans)>=2 else STATIC_WEIGHTS["concept"],
            "authority":"SINGLE_REPLAYED_ENGINE_LINE_ONLY",
        })
    # Explicitly ignore the legacy graph's provenance string when the public
    # certificate trust list is empty. It is not proof of exact-byte admission.
    withheld=sorted({str(x) for x in j.get("local_causal_certificate_ids",[]) if x})
    claims.sort(key=lambda c:(-c["priority"],c["claim_id"]))
    selected=claims[:3]
    text=" ".join(c["text_ko"] for c in selected)
    return {
        "schema":SCHEMA,"ply":moment.get("ply"),"played_uci":moment.get("played_uci"),
        "verdict":"EMIT_BOUNDED_CONVENTIONAL","reason":"SOURCE_GROUNDED_PAIR_AND_ATOMS",
        "leader":leader,"rival":rival,
        "actual_move_role":j.get("played_move_role"),
        "claims":claims,
        "selected_claim_ids":[c["claim_id"] for c in selected],
        "withheld_causal_certificate_ids":withheld,
        "text_ko":text,
        "model_interface":{
            "schema":SELECTOR_SCHEMA,
            "kind":"SPARSE_STATIC_LINEAR_RANKING_UNTRAINED",
            "feature_names":["engine_score_gap_cp","pv_legally_replayed_count","causal_claim_authorized"],
            "features":[j["candidate_gap_cp"],len(claims)-1,0],
            "weights":dict(STATIC_WEIGHTS),
            "trainable_parameters":0,
            "frozen_labels":True,
            "permitted_actions":["CHOOSE_CLAIM_IDS","ABSTAIN"],
            "forbidden_actions":["ISSUE_CAUSAL_AUTHORITY","INVENT_PV","GUESS_PROBABILITY"]
        },
        "model_kind":"UNTRAINED_STATIC_SELECTOR_NO_LM",
        "source_engine_identity":"NOT_AUTHENTICATED_BY_THIS_LAYER",
        "source_causal_claim":False,
        "confidence_probability":None,
        "human_utility":None,
        "overall_claim":"EXPLANATION_BOUND_TO_I9_I10_FACTS_ONLY"
    }

def compile_graph(graph:dict[str,Any])->dict[str,Any]:
    packets=[compile_evidence(m) for m in graph.get("moments",[])]
    return {
        "schema":"c3x-ecl-i10-p3-graph-v1",
        "source_schema":graph.get("schema"),
        "model_kind":"ZERO_TRAINING_LIGHTWEIGHT_EVIDENCE_COMPILER",
        "packets":packets,
        "emitted":sum(x["verdict"]=="EMIT_BOUNDED_CONVENTIONAL" for x in packets),
        "abstained":sum(x["verdict"]=="ABSTAIN" for x in packets),
        "new_causal_authority_created":False,"trained_neural_model":False,
        "actual_end_to_end_speed_comparison":None,
        "independent_human_benefit":None
    }

def render_markdown(graph_packet:dict[str,Any])->str:
    lines=["# C3X ECL — 근거로 제한한 체스 해설", "",
           "기존 I9/I10의 적법성·근거만 사용합니다. 학습 모델·확률 보정·인과 증명·객관적 최선수라고 주장하지 않습니다.",""]
    for p in graph_packet.get("packets",[]):
        lines.extend([f"## Ply {p.get('ply')}", "",
                      p.get("text_ko") or f"판단 보류: {p.get('reason')}", "",
                      "증거 ID: "+", ".join(p.get("selected_claim_ids") or []),
                      "원인 증명서 발행: 없음", ""])
    return "\n".join(lines)
