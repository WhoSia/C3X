from __future__ import annotations
from typing import Any

CAUSAL="C3X_CAUSAL_CONTRAST"
HEURISTIC="CONVENTIONAL_HEURISTIC_COMMENTARY"

def _claim_check(atom:dict[str,Any],known_ids:set[str])->list[str]:
    errs=[]
    aid=atom.get("atom_id")
    if not aid or aid not in known_ids:errs.append("missing_atom_id")
    if atom.get("provenance") not in (CAUSAL,HEURISTIC):errs.append("invalid_provenance")
    if not atom.get("authority"):errs.append("missing_authority")
    txt=(atom.get("text") or "").lower()
    causal_markers=("causes the engine","causally","because the search","causal")
    if any(x in txt for x in causal_markers) and atom.get("provenance")!=CAUSAL:
        errs.append("causal_wording_without_causal_provenance")
    if atom.get("type")=="causal_contrast":
        cert=(atom.get("claim") or {}).get("certificate")
        if not cert or cert.get("provenance_class")!=CAUSAL:
            errs.append("causal_atom_missing_first_class_certificate")
    return errs

def render_packet(moment:dict[str,Any])->dict[str,Any]:
    atoms=moment.get("atoms",[])
    known={a.get("atom_id") for a in atoms if a.get("atom_id")}
    claims=[];abstained=[];errors=[]
    for a in atoms:
        text=(a.get("text") or "").strip()
        aid=a.get("atom_id")
        if not text:
            if aid:abstained.append({"atom_id":aid,"reason":"no_bounded_surface_text"})
            continue
        errs=_claim_check(a,known)
        claim={
            "claim_id":f"claim:{aid}",
            "text":text,
            "atom_ids":[aid] if aid else [],
            "provenance":a.get("provenance"),
            "authority":a.get("authority"),
            "type":a.get("type"),
            "factuality":{"pass":not errs,"errors":errs},
        }
        claims.append(claim);errors.extend(f"{claim['claim_id']}:{e}" for e in errs)
    return {
        "schema":"c3x-bounded-render-packet-v1",
        "claims":claims,
        "abstained_atoms":abstained,
        "pass":not errors,
        "errors":errors,
        "surface_text":" ".join(c["text"] for c in claims if c["factuality"]["pass"]),
        "authority_note":"Rendering cannot upgrade evidence authority; every rendered claim is atom-traceable.",
    }

def renderer_benchmark(moments:list[dict[str,Any]])->dict[str,Any]:
    packets=[m.get("render_packet") or render_packet(m) for m in moments]
    claims=[c for p in packets for c in p["claims"]]
    passed=sum(c["factuality"]["pass"] for c in claims)
    return {
        "schema":"c3x-atomic-renderer-benchmark-v1",
        "moment_count":len(moments),
        "claim_count":len(claims),
        "factuality_passed_claims":passed,
        "atomic_factuality_rate":1.0 if not claims else passed/len(claims),
        "causal_claims":sum(c["provenance"]==CAUSAL for c in claims),
        "heuristic_claims":sum(c["provenance"]==HEURISTIC for c in claims),
        "abstained_atom_count":sum(len(p["abstained_atoms"]) for p in packets),
        "renderer_failed_moments":sum(not p["pass"] for p in packets),
        "human_strategic_completeness":None,
        "note":"Atomic traceability/factuality is not a human usefulness score.",
    }

def attach_render_packets(moments:list[dict[str,Any]])->None:
    for m in moments:
        m["render_packet"]=render_packet(m)
        m["commentary"]=m["render_packet"]["surface_text"]
