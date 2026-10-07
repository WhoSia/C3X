from __future__ import annotations
from typing import Any,Iterable

HEURISTIC="CONVENTIONAL_HEURISTIC_COMMENTARY"
SUPPORTED="SUPPORTED"
ABSTAIN_CHAIN="ABSTAIN_CHAIN_REALIZABILITY_UNAVAILABLE"
ABSTAIN_PARENT="ABSTAIN_PARENT_CLASS_INACTIVE"
ABSTAIN_SCOPE="ABSTAIN_ACTIVATION_SCOPE_UNCERTAIN"
VALID={SUPPORTED,ABSTAIN_CHAIN,ABSTAIN_PARENT,ABSTAIN_SCOPE}

def canonical_fen(fen:str)->str:
    return " ".join(str(fen).split()[:4])

def authority_index(packets:Iterable[dict[str,Any]])->dict[str,list[dict[str,Any]]]:
    out={}
    for p in packets:
        fen=p.get("position_fen") or p.get("fen")
        if fen:out.setdefault(canonical_fen(str(fen)),[]).append(p)
    return out

def route_for_fen(index:dict[str,list[dict[str,Any]]],fen:str)->dict[str,Any]:
    rows=index.get(canonical_fen(fen),[])
    if not rows:
        return {"state":"LEGACY_UNSCOPED","allow_causal":True,"packets":[]}
    states=[str(p.get("state") or "").upper() for p in rows]
    bad=[s for s in states if s not in VALID]
    if bad:raise ValueError(f"Unknown C3X authority state: {bad[0]}")
    allow=all(s==SUPPORTED for s in states)
    state=SUPPORTED if allow else next(s for s in states if s!=SUPPORTED)
    return {"state":state,"allow_causal":allow,"packets":rows}

def authority_atom(packet:dict[str,Any])->dict[str,Any]:
    state=str(packet.get("state") or "").upper()
    if state not in VALID:raise ValueError(f"Unknown C3X authority state: {state}")
    if state==SUPPORTED:
        text=("C3X records this position as executable-support eligible for the bounded mechanism route. "
              "This support state alone does not establish a causal mechanism.")
    elif state==ABSTAIN_CHAIN:
        text=("C3X withholds mechanism-level causal commentary here because the frozen contrast grammar is not "
              "executable as a stable routed intervention on this position.")
    elif state==ABSTAIN_PARENT:
        text=("C3X withholds downstream mechanism attribution here because the parent mediator class is outside "
              "the currently authorized active regime.")
    else:
        text=("C3X withholds downstream mechanism attribution here because activation-scope authority is uncertain.")
    return {
      "type":"mechanism_authority_route","provenance":HEURISTIC,
      "authority":"c3x_precausal_authority_router",
      "claim":{"state":state,"source_stage":packet.get("source_stage","C3X 0.10.0-G10-P23"),
               "support_receipt":packet.get("support_receipt"),"authority_ceiling":"routing/abstention only"},
      "text":text
    }

def atoms_for_fen(index:dict[str,list[dict[str,Any]]],fen:str)->list[dict[str,Any]]:
    return [authority_atom(p) for p in index.get(canonical_fen(fen),[])]
