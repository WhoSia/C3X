from __future__ import annotations
from copy import deepcopy
from typing import Any

CAUSAL="C3X_CAUSAL_CONTRAST"
CAUSAL_MARKERS=("causes the engine","causally","because the search","causal")

def _certificate_ids(moment:dict[str,Any])->set[str]:
    out=set()
    for n in (moment.get("typed_graph") or {}).get("nodes",[]):
        if n.get("node_type")=="causal_certificate":
            p=n.get("payload") or {}
            if p.get("certificate_id"):out.add(str(p["certificate_id"]))
    return out

def verify_realization(moment:dict[str,Any],packet:dict[str,Any]|None=None)->dict[str,Any]:
    packet=packet or moment.get("realization_packet") or {}
    claims={c.get("claim_id"):c for c in (moment.get("render_packet") or {}).get("claims",[]) if c.get("claim_id")}
    atom_ids={a.get("atom_id") for a in moment.get("atoms",[]) if a.get("atom_id")}
    cert_ids=_certificate_ids(moment)
    errors=[]
    verified=[]
    for s in packet.get("sentences",[]):
        sid=s.get("sentence_id","unknown")
        cids=s.get("claim_ids") or []
        aids=s.get("atom_ids") or []
        if not cids:errors.append(f"{sid}:missing_claim_trace")
        if not aids or not set(aids)<=atom_ids:errors.append(f"{sid}:invalid_atom_trace")
        linked=[claims.get(cid) for cid in cids]
        if any(c is None for c in linked):errors.append(f"{sid}:unknown_claim")
        linked=[c for c in linked if c is not None]
        if any(not c.get("factuality",{}).get("pass") for c in linked):errors.append(f"{sid}:failed_source_claim")
        expected_text=" ".join((c.get("text") or "").strip() for c in linked).strip()
        if (s.get("text") or "").strip()!=expected_text:errors.append(f"{sid}:text_not_claim_bounded")
        expected_prov=sorted({c.get("provenance") for c in linked})
        expected_auth=sorted({c.get("authority") for c in linked})
        if sorted(set(s.get("provenance") or []))!=expected_prov:errors.append(f"{sid}:provenance_mismatch")
        if sorted(set(s.get("authority") or []))!=expected_auth:errors.append(f"{sid}:authority_mismatch")
        txt=(s.get("text") or "").lower()
        if any(x in txt for x in CAUSAL_MARKERS):
            if CAUSAL not in expected_prov:errors.append(f"{sid}:unsupported_causal_wording")
            causal_atoms=[a for a in moment.get("atoms",[]) if a.get("atom_id") in aids and a.get("provenance")==CAUSAL]
            if not causal_atoms:errors.append(f"{sid}:causal_wording_without_causal_atom")
            for a in causal_atoms:
                cert=((a.get("claim") or {}).get("certificate") or {})
                cid=cert.get("certificate_id")
                if not cid or str(cid) not in cert_ids:errors.append(f"{sid}:causal_wording_without_graph_certificate")
        verified.append({"sentence_id":sid,"claim_ids":cids,"atom_ids":aids})
    return {
        "schema":"c3x-adversarial-realization-verification-v1",
        "pass":not errors,
        "errors":errors,
        "verified_sentences":verified,
        "rejected_text":"" if not errors else packet.get("text",""),
        "authority_note":"Verification rejects unsupported surface transformations and cannot upgrade source evidence.",
    }

def adversarial_suite(moment:dict[str,Any])->dict[str,Any]:
    base=deepcopy(moment.get("realization_packet") or {})
    sentences=base.get("sentences",[])
    if not sentences:
        return {"schema":"c3x-adversarial-realization-suite-v1","cases":[],"rejection_rate":1.0,"pass":True}
    cases=[]
    def run(name,p):
        v=verify_realization(moment,p)
        cases.append({"name":name,"rejected":not v["pass"],"errors":v["errors"]})
    p=deepcopy(base);p["sentences"][0]["atom_ids"]=[];run("drop_atom_trace",p)
    p=deepcopy(base);p["sentences"][0]["authority"]=["objective_chess_truth"];run("authority_upgrade",p)
    p=deepcopy(base);p["sentences"][0]["text"]=(p["sentences"][0]["text"]+" This causally proves the move is objectively best.");run("unsupported_causal_wording",p)
    p=deepcopy(base);p["sentences"][0]["text"]="Tampered unsupported sentence.";run("surface_tamper",p)
    rate=sum(c["rejected"] for c in cases)/len(cases)
    return {"schema":"c3x-adversarial-realization-suite-v1","cases":cases,"rejection_rate":rate,"pass":rate==1.0}

def attach_verification(moments:list[dict[str,Any]])->None:
    for m in moments:
        m["realization_verification"]=verify_realization(m)
        m["adversarial_realization_suite"]=adversarial_suite(m)
        m["commentary"]=m.get("realization_packet",{}).get("text","") if m["realization_verification"]["pass"] else ""

def verification_benchmark(moments:list[dict[str,Any]])->dict[str,Any]:
    clean=[m.get("realization_verification") or verify_realization(m) for m in moments]
    adv=[m.get("adversarial_realization_suite") or adversarial_suite(m) for m in moments]
    cases=[c for p in adv for c in p.get("cases",[])]
    rejected=sum(c.get("rejected",False) for c in cases)
    return {
        "schema":"c3x-adversarial-verification-benchmark-v1",
        "moment_count":len(moments),
        "clean_pass_rate":1.0 if not clean else sum(v.get("pass",False) for v in clean)/len(clean),
        "adversarial_case_count":len(cases),
        "adversarial_rejection_rate":1.0 if not cases else rejected/len(cases),
        "failed_clean_packets":sum(not v.get("pass",False) for v in clean),
        "human_utility_score":None,
        "note":"I7 is a structural faithfulness firewall; it does not certify strategic completeness or pedagogy.",
    }
