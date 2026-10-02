from __future__ import annotations
from dataclasses import dataclass,field
from enum import Enum
from typing import Any,Iterable

class ClaimStatus(str,Enum):
    ACTIVE="ACTIVE"
    SUSPENDED="SUSPENDED"
    DEMOTED="DEMOTED"
    RETRACTED="RETRACTED"
    RESTORED="RESTORED"
    BRANCHED_CONFLICT="BRANCHED_CONFLICT"

AUTHORITY_ORDER=[
    "MEASUREMENT_ROUTING",
    "CHESS_NATIVE_SURFACE",
    "MECHANISM_CANDIDATE",
    "LOCAL_CAUSAL_EXPLANATION",
    "COMPOSITION_CANDIDATE",
    "TRANSPORTABLE_CAUSAL_PATTERN",
]

CONSTITUTIVE_INVALIDATORS={"PROVENANCE_INVALID","CORRESPONDENCE_INVALID","CONSTITUTIVE_FALSIFIER_CONTRADICTION"}
SUSPENDERS={"UNRESOLVED_DIRECT_CONTRADICTION","DEPENDENCY_SUSPENDED"}
DEMOTION_SIGNALS={"LOCAL_MINIMALITY_LOST","FALSIFIER_SUPPORT_LOST","REPLICATION_SCOPE_LOST"}
BRANCH_SIGNALS={"CONTEXT_CONDITION_DISCOVERED","COMPATIBLE_CONTEXT_SPLIT"}
RESTORERS={"CONTRADICTION_RESOLVED","PROVENANCE_RESTORED","DEPENDENCY_RESTORED"}

def authority_rank(a:str)->int:return AUTHORITY_ORDER.index(a)
def lower_authority(a:str)->str:
    i=authority_rank(a);return AUTHORITY_ORDER[max(0,i-1)]

@dataclass
class Claim:
    claim_id:str
    authority:str
    status:ClaimStatus=ClaimStatus.ACTIVE
    evidence:set[str]=field(default_factory=set)
    dependencies:set[str]=field(default_factory=set)
    history:list[dict[str,Any]]=field(default_factory=list)
    original_authority:str|None=None
    branch_key:str|None=None
    def __post_init__(self):
        if self.original_authority is None:self.original_authority=self.authority

def canonical_status(authority:str,evidence:Iterable[str],dependency_states:Iterable[str]=())->dict[str,Any]:
    ev=set(evidence);deps=set(dependency_states)
    if ev & CONSTITUTIVE_INVALIDATORS:
        return {"status":ClaimStatus.RETRACTED.value,"authority":"MEASUREMENT_ROUTING","reason":sorted(ev&CONSTITUTIVE_INVALIDATORS)}
    if "RETRACTED" in deps:
        return {"status":ClaimStatus.SUSPENDED.value,"authority":authority,"reason":["DEPENDENCY_RETRACTED"]}
    if ev & SUSPENDERS or "SUSPENDED" in deps:
        return {"status":ClaimStatus.SUSPENDED.value,"authority":authority,"reason":sorted(ev&SUSPENDERS) or ["DEPENDENCY_SUSPENDED"]}
    if ev & BRANCH_SIGNALS:
        return {"status":ClaimStatus.BRANCHED_CONFLICT.value,"authority":authority,"reason":sorted(ev&BRANCH_SIGNALS)}
    if ev & DEMOTION_SIGNALS:
        return {"status":ClaimStatus.DEMOTED.value,"authority":lower_authority(authority),"reason":sorted(ev&DEMOTION_SIGNALS)}
    return {"status":ClaimStatus.ACTIVE.value,"authority":authority,"reason":[]}

def apply_evidence(claim:Claim,atoms:Iterable[str],event_id:str,procedural_phase:str="POST_FREEZE")->Claim:
    atoms=set(atoms)
    # Procedural order is intentionally noncommutative: observing outcomes before freeze permanently invalidates provenance.
    if procedural_phase=="OUTCOME_BEFORE_REQUIRED_FREEZE":
        atoms.add("PROVENANCE_INVALID")
    claim.evidence|=atoms
    old={"status":claim.status.value,"authority":claim.authority}
    new=canonical_status(claim.original_authority or claim.authority,claim.evidence)
    claim.status=ClaimStatus(new["status"]);claim.authority=new["authority"]
    claim.history.append({"event_id":event_id,"atoms":sorted(atoms),"old":old,"new":new,"procedural_phase":procedural_phase})
    return claim

def resolve_atoms(claim:Claim,remove:Iterable[str],add:Iterable[str],event_id:str)->Claim:
    claim.evidence-=set(remove);claim.evidence|=set(add)
    old={"status":claim.status.value,"authority":claim.authority}
    new=canonical_status(claim.original_authority or claim.authority,claim.evidence)
    if old["status"] in {ClaimStatus.SUSPENDED.value,ClaimStatus.DEMOTED.value} and new["status"]==ClaimStatus.ACTIVE.value:
        new["status"]=ClaimStatus.RESTORED.value
    claim.status=ClaimStatus(new["status"]);claim.authority=new["authority"]
    claim.history.append({"event_id":event_id,"remove":sorted(remove),"add":sorted(add),"old":old,"new":new})
    return claim

def evidence_set_confluent(authority:str,sequences:list[list[set[str]]])->dict[str,Any]:
    finals=[]
    for i,seq in enumerate(sequences):
        c=Claim(f"probe-{i}",authority)
        for j,atoms in enumerate(seq):apply_evidence(c,atoms,f"e{j}")
        finals.append((c.status.value,c.authority,frozenset(c.evidence)))
    target_sets={x[2] for x in finals}
    comparable=len(target_sets)==1
    states={(x[0],x[1]) for x in finals}
    return {"comparable_final_evidence":comparable,"confluent":comparable and len(states)==1,"finals":[[a,b,sorted(e)] for a,b,e in finals]}

def classify_certificate_conflict(a:dict[str,Any],b:dict[str,Any])->dict[str,Any]:
    if a.get("certificate_id")==b.get("certificate_id"):
        return {"class":"NONCOMPARABLE","reason":"SAME_CERTIFICATE"}
    if a.get("correspondence_id")!=b.get("correspondence_id"):
        return {"class":"NONCOMPARABLE","reason":"CORRESPONDENCE_MISMATCH"}
    if a.get("falsifier_contradiction") or b.get("falsifier_contradiction"):
        return {"class":"FALSIFIER_CONFLICT","reason":"CONSTITUTIVE_FALSIFIER_CONTRADICTION"}
    same_context=a.get("context_signature")==b.get("context_signature")
    same_mechanism=a.get("mechanism_signature")==b.get("mechanism_signature")
    same_consequence=a.get("consequence_schema")==b.get("consequence_schema")
    if same_context and not same_mechanism and same_consequence:
        return {"class":"MECHANISM_CONFLICT","reason":"SAME_CONTEXT_CONSEQUENCE_DIFFERENT_MECHANISM"}
    if not same_context and same_mechanism and same_consequence:
        return {"class":"CONTEXT_SPLIT","reason":"MECHANISM_PERSISTS_ACROSS_CONTEXT_SPLIT"}
    if same_mechanism and same_consequence:
        independent=a.get("provenance_id")!=b.get("provenance_id") and a.get("world_id")!=b.get("world_id")
        return {"class":"COMPATIBLE_COMPOSABLE" if independent else "COMPATIBLE_BUT_PROVENANCE_DEPENDENT","reason":"MATCHED_MECHANISM_AND_CONSEQUENCE"}
    return {"class":"NONCOMPARABLE","reason":"NO_FROZEN_EQUIVALENCE"}

def propagate_revision(claims:dict[str,Claim])->dict[str,Any]:
    changed=True
    rounds=0
    while changed:
        changed=False;rounds+=1
        for c in claims.values():
            dep_states=[claims[d].status.value for d in c.dependencies if d in claims]
            if not dep_states:continue
            base=c.original_authority or c.authority
            new=canonical_status(base,c.evidence,dep_states)
            if c.status.value!=new["status"] or c.authority!=new["authority"]:
                old={"status":c.status.value,"authority":c.authority}
                c.status=ClaimStatus(new["status"]);c.authority=new["authority"]
                c.history.append({"event_id":f"dependency-propagation-{rounds}","old":old,"new":new})
                changed=True
        if rounds>len(claims)+2:raise RuntimeError("DEPENDENCY_PROPAGATION_NONCONVERGENCE")
    return {"rounds":rounds,"claims":{k:{"authority":v.authority,"status":v.status.value} for k,v in sorted(claims.items())}}

def rendered_language_allowed(claim:Claim)->dict[str,Any]:
    causal=claim.authority in {"LOCAL_CAUSAL_EXPLANATION","TRANSPORTABLE_CAUSAL_PATTERN"} and claim.status in {ClaimStatus.ACTIVE,ClaimStatus.RESTORED}
    transport=claim.authority=="TRANSPORTABLE_CAUSAL_PATTERN" and causal
    return {"causal":causal,"transport":transport,"status":claim.status.value,"authority":claim.authority}
