from __future__ import annotations
from typing import Any,Iterable

HEURISTIC="CONVENTIONAL_HEURISTIC_COMMENTARY"
ALLOWED_LICENSE_STATES={"public_domain","permissive","user_owned","licensed","citation_only"}

def _tags(x:dict[str,Any])->set[str]:
    out=set()
    for k in ("motif_tags","concept_tags","category_tags"):
        out.update(str(v).strip().lower() for v in x.get(k,[]) if str(v).strip())
    return out

def validate_record(r:dict[str,Any])->list[str]:
    errs=[]
    for k in ("source_id","source_uri","license_state"):
        if not r.get(k):errs.append(f"missing_{k}")
    if r.get("license_state") not in ALLOWED_LICENSE_STATES:errs.append("license_not_admitted")
    excerpt=str(r.get("commentary_excerpt",""))
    if len(excerpt)>240:errs.append("excerpt_too_long")
    if not _tags(r):errs.append("missing_retrieval_tags")
    return errs

def retrieve(query_tags:Iterable[str],records:Iterable[dict[str,Any]],top_k:int=3)->dict[str,Any]:
    q={str(x).strip().lower() for x in query_tags if str(x).strip()}
    hits=[];rejected=[]
    for r in records:
        errs=validate_record(r)
        if errs:
            rejected.append({"source_id":r.get("source_id"),"errors":errs});continue
        tags=_tags(r);inter=len(q&tags);union=len(q|tags) or 1
        score=inter/union
        if inter==0:continue
        hits.append({"source_id":r["source_id"],"source_uri":r["source_uri"],"license_state":r["license_state"],
                     "score":round(score,6),"matched_tags":sorted(q&tags),"all_tags":sorted(tags),
                     "excerpt":str(r.get("commentary_excerpt",""))})
    hits.sort(key=lambda z:(-z["score"],z["source_id"]))
    return {"schema":"c3x-retrieval-packet-v1","query_tags":sorted(q),"hits":hits[:max(0,int(top_k))],
            "rejected_count":len(rejected),"rejected":rejected,
            "authority":"retrieval_is_reference_only_no_causal_promotion"}

def retrieval_atoms(packet:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    for h in packet.get("hits",[]):
        out.append({"type":"retrieval_reference","provenance":HEURISTIC,
                    "authority":"retrieved_commentary_reference",
                    "claim":{"source_id":h["source_id"],"source_uri":h["source_uri"],
                             "license_state":h["license_state"],"matched_tags":h["matched_tags"],
                             "similarity_score":h["score"]},
                    "text":f"Related annotated commentary source available: {h['source_id']} ({', '.join(h['matched_tags'])})."})
    return out

def audit_retrieval_corpus(records:Iterable[dict[str,Any]])->dict[str,Any]:
    rows=list(records);errors=[];states={};sources=set()
    for rec in rows:
        es=validate_record(rec)
        if es:errors.append({"source_id":rec.get("source_id"),"errors":es})
        state=str(rec.get("license_state") or "missing");states[state]=states.get(state,0)+1
        if rec.get("source_uri"):sources.add(str(rec["source_uri"]))
    return {
        "schema":"c3x-retrieval-corpus-governance-v1",
        "record_count":len(rows),
        "admissible_count":len(rows)-len(errors),
        "rejected_count":len(errors),
        "license_state_counts":dict(sorted(states.items())),
        "distinct_source_uris":len(sources),
        "errors":errors,
        "pass":not errors,
        "authority":"corpus_governance_does_not_promote_retrieved_commentary_to_causal_evidence",
    }
