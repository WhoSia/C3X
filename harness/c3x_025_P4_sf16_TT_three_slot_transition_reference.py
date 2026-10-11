#!/usr/bin/env python3
"""C3X0.25-P4 isolated, deterministic, single-thread SF16 TT slot transition reference.

NOT the native engine, NOT native-vs-Python equivalence, NOT NNUE/search/SEE or
Elo. See prereg c3x-025-P4-P5-two-axis-mechanistic-semantics-...md.
Original upstream SF16 Git 68e1e9b3811e16cad014b590d7443b9063b3eb52.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

PINNED_SF16="68e1e9b3811e16cad014b590d7443b9063b3eb52"
DEPTH_OFFSET=-7
CLUSTER_SIZE=3
AGE_MASK=248
GEN_DELTA=8
GEN_CYCLE=263
EXACT=3
UPPER=1
LOWER=2

@dataclass
class Entry:
    key16:int=0
    depth8:int=0
    genBound8:int=0
    move16:int=0
    value16:int=0
    eval16:int=0

    def __post_init__(self):
        if not 0<=self.key16<=65535:raise ValueError("key16 out of bounds")
        for field in ("depth8","genBound8"):
            if not 0<=getattr(self,field)<=255:raise ValueError(field+" out of bounds")
        if not 0<=self.move16<=65535:raise ValueError("move16 out of bounds")
        for field in ("value16","eval16"):
            if not -32768<=getattr(self,field)<=32767:raise ValueError(field+" out of bounds")

@dataclass(frozen=True)
class Probe:
    slot:int
    found:bool
    refreshed:bool
    reason:str
    stored_key16:int
    # No full64 original key is stored in the compact SF16 TTEntry.

class Cluster:
    def __init__(self,slots:list[Entry]|None=None,generation:int=0):
        if not 0<=generation<256 or generation%8:
            raise ValueError("invalid original packed generation")
        self.generation=generation
        self.slots=[Entry() for _ in range(CLUSTER_SIZE)] if slots is None else [
            Entry(**asdict(e)) for e in slots]
        if len(self.slots)!=CLUSTER_SIZE:raise ValueError("SF16 TT cluster has 3 slots")

    def clone(self)->Cluster:return Cluster(self.slots,self.generation)

    def new_search(self)->None:
        self.generation=(self.generation+GEN_DELTA)&255

    def replacement_score(self,i:int)->int:
        e=self.slots[i]
        age=(GEN_CYCLE+self.generation-e.genBound8)&AGE_MASK
        return e.depth8-age

    def probe(self,full64_key:int,refresh:bool=True)->Probe:
        """Only models a single already-selected TT cluster (mul_hi64 not modeled).
        refresh=False is a COUNTERFACTUAL non-native lookup control.
        """
        if not 0<=full64_key<2**64:raise ValueError("invalid source key")
        short=full64_key&65535
        for i,e in enumerate(self.slots):
            if e.key16==short or not e.depth8:
                observed=bool(e.depth8)
                if refresh:
                    e.genBound8=self.generation|(e.genBound8&(GEN_DELTA-1))
                return Probe(i,observed,refresh,
                             "COMPACT_KEY_MATCH" if e.key16==short else "EMPTY_SLOT",
                             e.key16)
        # Stockfish16 uses > while iterating candidates: ties retain earlier slot.
        replace=0
        for i in range(1,CLUSTER_SIZE):
            if self.replacement_score(replace)>self.replacement_score(i):
                replace=i
        e=self.slots[replace]
        return Probe(replace,False,False,"DEPTH_MINUS_AGE_REPLACEMENT",e.key16)

    def save(self,slot:int,full64_key:int,value:int,pv:bool,bound:int,
             depth:int,move:int,eval_value:int)->dict:
        """Exactly isolates the two distinct SF16 TTEntry::save write clauses."""
        if not 0<=slot<CLUSTER_SIZE:raise ValueError("invalid slot")
        if not 0<=full64_key<2**64:raise ValueError("invalid key")
        if bound not in (0,1,2,3):raise ValueError("invalid 2bit bound")
        if not 0<=move<65536:raise ValueError("invalid encoded move")
        if not -32768<=value<=32767 or not -32768<=eval_value<=32767:
            raise ValueError("native signed16 overflow not simulated")
        e=self.slots[slot];short=full64_key&65535
        write_move=bool(move or short!=e.key16)
        if write_move:e.move16=move
        write_score=(bound==EXACT or short!=e.key16 or
                     depth-DEPTH_OFFSET+2*int(pv)>e.depth8-4)
        if write_score:
            packed_depth=depth-DEPTH_OFFSET
            if not 0<packed_depth<256:raise ValueError("original depth assert violated")
            e.key16=short
            e.depth8=packed_depth
            e.genBound8=self.generation|(int(pv)<<2)|bound
            e.value16=value;e.eval16=eval_value
        return {"move16_written":write_move,"score_fields_written":write_score,
                "move_field_after":e.move16,"value_field_after":e.value16,
                "depth_field_after":e.depth8,"packed_generation_after":e.genBound8}

    def state(self)->dict:
        return {"generation":self.generation,
                "three_slots":[asdict(s) for s in self.slots]}

def constructive_witnesses()->dict:
    # Case A: same returned hit observed both arms; refreshing only one changes
    # the later slot chosen for a different key.  The first hit's value ignored.
    seed=Cluster([Entry(key16=i+1,depth8=12,genBound8=0,move16=10+i,value16=50)
                  for i in range(3)],generation=16)
    active=seed.clone();passive=seed.clone()
    a=active.probe(1,True)
    b=passive.probe(1,False)
    miss_active=active.probe(4)
    miss_passive=passive.probe(4)
    if not (a.found and b.found and a.slot==b.slot==0
            and miss_active.slot==1 and miss_passive.slot==0
            and not miss_active.found and not miss_passive.found):
        raise AssertionError("SF16 probe age witness no longer valid")
    # Case B: same short key, one new move while old bound/score/depth retained.
    e=Entry(key16=0x42,depth8=32,genBound8=LOWER,move16=0x100,value16=80,eval16=40)
    mixed=Cluster([e,Entry(),Entry()],generation=16)
    before=mixed.state()
    verdict=mixed.save(0,0x42,999,False,UPPER,10,0x200,777)
    after=mixed.state()
    if verdict["score_fields_written"] or not verdict["move16_written"] or (
            before["three_slots"][0]["value16"]!=after["three_slots"][0]["value16"]):
        raise AssertionError("mixed-field source save counterexample lost")
    # Case C: low16 key equality while original true full64 key is distinct.
    key_a=0x00010042
    key_b=0x00020042
    alias=Cluster([Entry(key16=0x42,depth8=9,genBound8=0,move16=9),Entry(),Entry()])
    probe=alias.probe(key_b)
    if key_a==key_b or key_a&65535!=key_b&65535 or not probe.found:
        raise AssertionError("low16 full-key alias witness invalid")
    return {
        "schema":"c3x025-P4-SF16-three-slot-source-anchored-constructive-witnesses-v1",
        "science_status":"FINITE_ABSTRACT_SINGLE_CLUSTER_DEVELOPMENT_MODEL_NOT_NATIVE_ENGINE_EXPERIMENT",
        "pinned_upstream_SF16_git":PINNED_SF16,
        "P4_I_ignored_probe_hit_can_modify_later_replacement":{
           "same_first_observed_hit":True,
           "first_hit_original_score_was_consumed":False,
           "generation":16,"three_old_entry_depths":[12,12,12],
           "active_refresh_slot":a.slot,
           "counterfactual_no_refresh_slot":b.slot,
           "later_different_key_miss_replaces_active_slot":miss_active.slot,
           "later_different_key_miss_replaces_no_refresh_slot":miss_passive.slot,
           "claims_specific_july_case_executed":False},
        "P4_II_move_writer_can_differ_from_score_writer":{
           "new_short_key_matches":True,
           "same_key_new_move_updates":verdict["move16_written"],
           "numeric_score_fields_update":verdict["score_fields_written"],
           "initial_move16":before["three_slots"][0]["move16"],
           "final_move16":after["three_slots"][0]["move16"],
           "initial_value16":before["three_slots"][0]["value16"],
           "final_value16":after["three_slots"][0]["value16"],
           "requires_per_field_native_writer_lineage":True},
        "P4_III_low16_alias_is_not_full64_identity":{
           "source_key_A": "WITHHELD_SYNTHETIC",
           "source_key_B":"WITHHELD_SYNTHETIC",
           "full64_keys_distinct":True,"low16_equal":True,
           "same_cluster_assumed":True,
           "native_compact_match_only":probe.found,
           "full64_source_writer_verified":False},
        "P4_IV_boundaries":{
           "matches_original_pinned_source_individual_clauses_only":True,
           "uses_native_Cpp_oracle":False,
           "natural_TT_SEE_mediation_proven":False,
           "TT_engine_performance_or_Elo_measured":False,
           "future_M5_independent_validation":False}}
def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    x=constructive_witnesses()
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
    print("C3X025_P4_SF16_MICROTRANSITION_WITNESSES",
          {k:v for k,v in x.items() if k.startswith("P4_")},flush=True)
    print("C3X025_P4_SF16_WITNESS_JSON_SHA256",
          hashlib.sha256(target.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
