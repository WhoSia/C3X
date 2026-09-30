from __future__ import annotations
from typing import Any

TYPE_ORDER={
    "tactical_fact":0,
    "move_fact":1,
    "candidate_contrast":2,
    "tactical_contrast":3,
    "concept_proxy_delta":4,
    "verified_line_evidence":5,
    "causal_contrast":6,
    "retrieval_reference":7,
    "material_snapshot":8,
}

def _sentence_role(claim:dict[str,Any])->str:
    t=claim.get("type")
    return {
        "tactical_fact":"verified_tactic",
        "move_fact":"verified_move_fact",
        "candidate_contrast":"candidate_comparison",
        "tactical_contrast":"tactical_comparison",
        "concept_proxy_delta":"positional_proxy_comparison",
        "verified_line_evidence":"verified_line",
        "causal_contrast":"causal_scope",
        "retrieval_reference":"retrieval_context",
        "material_snapshot":"material_context",
    }.get(t,"bounded_evidence")

def realize_packet(moment:dict[str,Any],rating_band:str="advanced")->dict[str,Any]:
    render=moment.get("render_packet") or {}
    claims=[c for c in render.get("claims",[]) if c.get("factuality",{}).get("pass")]
    claims.sort(key=lambda c:(TYPE_ORDER.get(c.get("type"),99),c.get("claim_id","")))
    sentences=[]
    for i,c in enumerate(claims):
        text=(c.get("text") or "").strip()
        if not text:continue
        sentences.append({
            "sentence_id":f"sent:{moment.get('ply')}:{i}",
            "text":text,
            "role":_sentence_role(c),
            "claim_ids":[c["claim_id"]],
            "atom_ids":list(c.get("atom_ids",[])),
            "provenance":[c.get("provenance")],
            "authority":[c.get("authority")],
            "realization_mode":"verbatim_bounded_claim",
        })
    return {
        "schema":"c3x-constrained-realization-packet-v1",
        "rating_band":rating_band,
        "sentences":sentences,
        "text":" ".join(s["text"] for s in sentences),
        "source_claim_count":len(claims),
        "realized_sentence_count":len(sentences),
        "abstained_claim_count":max(0,len(render.get("claims",[]))-len(sentences)),
        "pass":all(s["claim_ids"] and s["atom_ids"] and s["text"] for s in sentences),
        "authority_note":"I6 realization may reorder or omit bounded claims but may not invent facts, change provenance, or upgrade authority.",
    }

def attach_realizations(moments:list[dict[str,Any]],rating_band:str)->None:
    for m in moments:
        m["realization_packet"]=realize_packet(m,rating_band)

def realization_benchmark(moments:list[dict[str,Any]])->dict[str,Any]:
    packets=[m.get("realization_packet") or realize_packet(m) for m in moments]
    return {
        "schema":"c3x-constrained-realization-benchmark-v1",
        "moment_count":len(packets),
        "sentence_count":sum(len(p.get("sentences",[])) for p in packets),
        "failed_packets":sum(not p.get("pass",False) for p in packets),
        "abstained_claim_count":sum(p.get("abstained_claim_count",0) for p in packets),
        "generation_mode":"claim-bounded deterministic realization",
        "free_form_llm_used":False,
        "human_fluency_score":None,
        "human_usefulness_score":None,
        "note":"I6 establishes a safe language-realization surface, not human utility or stylistic optimality.",
    }
