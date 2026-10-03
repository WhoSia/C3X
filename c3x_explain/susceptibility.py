from __future__ import annotations
from typing import Any,Iterable

HEURISTIC="CONVENTIONAL_HEURISTIC_COMMENTARY"
AUTHORITY="c3x_transparent_preoutcome_susceptibility"

def canonical_fen(fen:str)->str:
    return " ".join(str(fen).split()[:4])

def susceptibility_index(packets:Iterable[dict[str,Any]])->dict[str,list[dict[str,Any]]]:
    out={}
    for p in packets:
        fen=p.get("position_fen") or p.get("fen")
        if fen:
            out.setdefault(canonical_fen(str(fen)),[]).append(p)
    return out

def _trace_text(packet:dict[str,Any])->str:
    family=str(packet.get("family_id") or packet.get("family") or "transparent susceptibility rule")
    decision=str(packet.get("decision") or "ABSTAIN").upper()
    trace=packet.get("trace") or {}
    if family=="T1_INTEGER_SCORECARD":
        score=trace.get("score");threshold=trace.get("threshold")
        active=[z for z in trace.get("terms",[]) if z.get("contribution")]
        terms=", ".join(f"{z.get('indicator')} {int(z.get('contribution',0)):+d}" for z in active[:6]) or "no active score terms"
        return f"{family} gives score {score} against threshold {threshold} ({terms})"
    if family=="T2_ORDERED_RULE_LIST":
        if trace.get("fired_rule") is None:return f"{family} reaches its explicit default abstention"
        lits=trace.get("rule") or []
        body=", ".join(f"{z.get('indicator')}={z.get('value')}" for z in lits)
        return f"{family} fires rule {trace.get('fired_rule')}: {body}"
    if family=="T3_SPARSE_INTERACTION_TABLE":
        hit=[z for z in trace.get("cells",[]) if z.get("training_cell")]
        if not hit:return f"{family} finds no admitted transparent interaction cell"
        z=hit[0];return f"{family} matches {z.get('features')}={z.get('cell')} with development cell {z.get('training_cell')}"
    return f"{family} exposes the recorded transparent decision trace"

def admissibility_atom(packet:dict[str,Any])->dict[str,Any]:
    decision=str(packet.get("decision") or "ABSTAIN").upper()
    if decision not in {"ADMIT","ABSTAIN"}:raise ValueError(f"Unknown susceptibility decision: {decision}")
    trace=packet.get("trace") or {}
    family=packet.get("family_id") or packet.get("family")
    reason=_trace_text(packet)
    if decision=="ADMIT":
        text=(f"A transparent pre-edit intervention screen admits this counterfactual candidate: {reason}. "
              "This is only an intervention-admissibility prediction; it is not a causal certificate or objective chess truth.")
    else:
        why=packet.get("abstention_reason") or "the transparent admission rule was not satisfied"
        text=(f"C3X abstains from claiming a stable counterfactual intervention here: {reason}; {why}. "
              "Abstention is not evidence that the chess idea is bad or that no causal mechanism exists.")
    claim={
      "decision":decision,"family_id":family,"trace":trace,
      "feature_values":packet.get("feature_values") or {},
      "abstention_reason":packet.get("abstention_reason"),
      "authority_ceiling":"pre-edit preference-preservation susceptibility only",
      "source_stage":packet.get("source_stage","C3X 0.9.0-G10-P17")
    }
    return {"type":"intervention_admissibility","provenance":HEURISTIC,"authority":AUTHORITY,"claim":claim,"text":text}

def atoms_for_fen(index:dict[str,list[dict[str,Any]]],fen:str)->list[dict[str,Any]]:
    return [admissibility_atom(p) for p in index.get(canonical_fen(fen),[])]
