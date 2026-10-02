from __future__ import annotations
import itertools,json
from copy import deepcopy
from typing import Any

GENERATORS=("C","S","G","E","U")
ADMISSIBLE_GRAMMAR=("C","S","E")
ENDPOINTS=("A_FROM","A_TO","B_FROM","B_TO")

def _canon(x:Any)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def delta_edges(c:dict)->tuple[tuple[str,str],...]:
    b=c["board_trigger"];out=[]
    for i,(x,y) in enumerate(zip(b["relation_before"],b["relation_after"])):
        if x==y:continue
        out.append((ENDPOINTS[i],"GAIN" if (not x and y) else "LOSS"))
    return tuple(out)

def _swap_ab_label(x):
    if x=="A":return "B"
    if x=="B":return "A"
    return x

def _swap_surface(s:str)->str:
    if s=="A_TO_B":return "B_TO_A"
    if s=="B_TO_A":return "A_TO_B"
    return s

def _map_endpoint(ep:str,g:str)->str:
    cand,where=ep.split("_",1)
    if g=="C":cand="B" if cand=="A" else "A"
    if g=="E":where="TO" if where=="FROM" else "FROM"
    return cand+"_"+where

def transform_signature(c:dict,generators)->dict[str,Any]:
    gens=set(generators)
    edges=[list(x) for x in delta_edges(c)]
    role=c["board_trigger"]["moved_side_role"]
    bound=c["bound"]
    topo=deepcopy(c["response_topology"])
    surface=c["surface"]["board_native_transition"]

    if "C" in gens:
        for e in edges:e[0]=_map_endpoint(e[0],"C")
        for cell in topo.values():
            cell["native"]=_swap_ab_label(cell.get("native"))
            cell["t_only"]=_swap_ab_label(cell.get("t_only"))
        surface=_swap_surface(surface)
    if "E" in gens:
        for e in edges:e[0]=_map_endpoint(e[0],"E")
    if "S" in gens:
        role="OPPONENT" if role=="OWN" else "OWN"
    if "G" in gens:
        for e in edges:e[1]="LOSS" if e[1]=="GAIN" else "GAIN"
    if "U" in gens:
        bound="UPPER" if bound=="LOWER" else "LOWER"

    return {
      "role":role,
      "delta_edges":sorted(tuple(e) for e in edges),
      "bound":bound,
      "response_topology":topo,
      "surface":surface,
      "falsifier":c["falsifier"],
    }

def morphism_witness(a:dict,b:dict,grammar=ADMISSIBLE_GRAMMAR)->dict[str,Any]:
    candidates=[]
    for r in range(len(grammar)+1):
        for subset in itertools.combinations(grammar,r):
            if transform_signature(a,subset)==transform_signature(b,()):
                candidates.append(tuple(subset))
    if not candidates:
        return {"isomorphic":False,"minimal_generators":None,"all_witnesses":[]}
    candidates.sort(key=lambda x:(len(x),x))
    return {"isomorphic":True,"minimal_generators":list(candidates[0]),"all_witnesses":[list(x) for x in candidates]}

def orbit_partition(certs:list[dict],grammar=ADMISSIBLE_GRAMMAR)->list[list[str]]:
    ids={c["id"]:c for c in certs};remaining=set(ids);parts=[]
    while remaining:
        seed=sorted(remaining)[0];component={seed};changed=True
        while changed:
            changed=False
            for a in list(component):
                for b in list(remaining-component):
                    if morphism_witness(ids[a],ids[b],grammar)["isomorphic"] or morphism_witness(ids[b],ids[a],grammar)["isomorphic"]:
                        component.add(b);changed=True
        remaining-=component;parts.append(sorted(component))
    return sorted(parts,key=lambda x:(len(x),x))

def development_adjudication(ecology:dict)->dict[str,Any]:
    certs={c["id"]:c for c in ecology["certificates"]}
    expected=[]
    for w in ecology["frozen_development_witnesses"]:
        got=morphism_witness(certs[w["a"]],certs[w["b"]])
        expected.append({"a":w["a"],"b":w["b"],"expected":w["expected_generators"],"got":got})
    negatives=[]
    for p in ecology["prior_p6_negative_pairs"]:
        got=morphism_witness(certs[p["a"]],certs[p["b"]])
        negatives.append({"a":p["a"],"b":p["b"],"got":got})
    parts=orbit_partition(list(certs.values()))
    largest=max(len(x) for x in parts)
    expected_pass=all(x["got"]["isomorphic"] and x["got"]["minimal_generators"]==x["expected"] for x in expected)
    negative_pass=all(not x["got"]["isomorphic"] for x in negatives)
    nondegenerate=largest < len(certs) and len(parts)>=2
    verdict="PASS_MORPHISM_GRAMMAR_PRESEALED" if expected_pass and negative_pass and nondegenerate else "FAIL_DEGENERATE_ISOMORPHISM_GRAMMAR"
    return {
      "verdict":verdict,
      "admissible_grammar":list(ADMISSIBLE_GRAMMAR),
      "unlicensed_generators":["G","U"],
      "development_witnesses":expected,
      "negative_pair_checks":negatives,
      "orbit_partition":parts,
      "largest_orbit":largest,
      "certificate_count":len(certs),
      "nondegenerate":nondegenerate,
      "context_factorization":"UNCHANGED_RELATION_BACKGROUND_IS_CONTEXT; CHANGED_ENDPOINT_EDGE_IS_MECHANISM_TRIGGER",
    }
