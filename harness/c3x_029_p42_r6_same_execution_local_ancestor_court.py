#!/usr/bin/env python3
"""P42/R6 independent joint-court over SAME native cold runs.

Never join traces from two separate engine builds / process histories.
Existing 0.27 C3b source events plus new post-do_move-key events must be
collected together from the same ABC experiment. Private raw keys never exported.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from c3x_027_game14_C3b_ancestor_root_court import judge as judge_original_c3b
from c3x_029_p42_r5_game14_local_spine_court import (
    adjudicate as judge_local, parse as parse_local
)

PRIVATE_EVENTS={
    "ANCESTOR_SNAPSHOT","CHILD_VALUE_RETURNED","PARENT_CANDIDATE_VALUE",
    "FRAME_RETURN","ROOT_FRAME_RETURN","ANCESTOR_EDGE_AMBIGUOUS",
    "ANCESTOR_DEPTH_CENSORED"
}
INTS=("sequence","root_call","ply","key64","native_move","value","frame_id")

def parse_original_native(raw: str) -> list[list[dict]]:
    groups=[]
    for line in raw.splitlines():
        # Do not treat the earlier c3x027 lineages' 'seq' as C3b 'sequence'.
        if not ("sequence=" in line and "frame_id=" in line and "event=" in line):
            continue
        d=dict(re.findall(r"([a-z_0-9]+)=([^\s]+)",line))
        if d.get("event") not in PRIVATE_EVENTS:
            continue
        if any(k not in d for k in INTS):
            raise ValueError("R6_HOLD_MISSING_C3B_NATIVE_FIELD")
        try:
            row={k:int(d[k]) for k in INTS}
        except ValueError as e:
            raise ValueError("R6_HOLD_NONNUMERIC_C3B_NATIVE_FIELD") from e
        row["event"]=d["event"]
        if row["sequence"]==1:
            groups.append([])
        if not groups:
            raise ValueError("R6_HOLD_ORPHAN_C3B_EVENT")
        groups[-1].append(row)
    return groups

def local_groups(raw: str) -> list[list[dict]]:
    groups=[]
    for d in parse_local(raw):
        if d["event"]=="GUARD_FALLTHROUGH":
            groups.append([])
        if not groups:
            raise ValueError("R6_HOLD_ORPHAN_LOCAL_EVENT")
        groups[-1].append(d)
    return groups

def joint_court(old_raw: str, new_raw: str, replay_count=2) -> dict:
    base={"root_causation_certified":False,"natural_mediation_certified":False,
          "chess_strategic_semantics_verified":False,"raw_source_keys_exposed":False}
    local=judge_local(new_raw,replay_count)
    groups=parse_original_native(old_raw)
    new=local_groups(new_raw)
    def fail(reason):
        return dict(base,status="HOLD_"+reason,
                    old_c3b_groups=len(groups),actual_local_groups=len(new),
                    local_status=local["status"])
    if local["status"]!="LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY":
        return fail("LOCAL_ORIGINAL_BRANCH_NOT_CERTIFIED")
    if not (len(groups)==len(new)==replay_count):
        return fail("COLD_REPLAY_GROUP_COUNT_MISMATCH")
    certs=[]
    for i,(older,modern) in enumerate(zip(groups,new)):
        first=older[0]
        if first["event"]!="ANCESTOR_SNAPSHOT":
            return fail("ANCESTOR_SOURCE_SNAPSHOT_MISSING")
        live=modern[0]
        if (first["root_call"]!=live["root_call"]
            or first["native_move"]!=live["move"]
            or first["key64"]!=live["parent64"]):
            return fail("SAME_EXECUTION_GUARD_SOURCE_ID_DRIFT")
        expected_root_move=live["root_move"]
        ancestor=judge_original_c3b(older,live["root_call"])
        if not ancestor.get("certified",False):
            return fail("ORIGINAL_C3B_"+ancestor["status"])
        # The actual source parent candidate (not just a returned child)
        # is required to agree with the newer returned/assessed value.
        parent=[e for e in older if e["event"]=="PARENT_CANDIDATE_VALUE"
                and e["ply"]==first["ply"]]
        root=[e for e in older if e["event"]=="PARENT_CANDIDATE_VALUE"
              and e["ply"]==0]
        if (len(parent)!=1 or parent[0]["value"]!=modern[4]["score"]):
            return fail("SAME_EXECUTION_PARENT_NATIVE_VALUE_DIVERGENCE")
        if len(root)!=1 or root[0]["native_move"]!=expected_root_move:
            return fail("UNRESTRICTED_ROOT_CANDIDATE_ID_MISMATCH")
        certs.append(ancestor["candidate_edges"])
    return dict(base,
        status="PASS_JOINT_SOURCE_LOCAL_AND_OBSERVED_ROOT_CANDIDATE_ONLY",
        replays=replay_count,
        source_c3b_candidate_edges=certs,
        local_actual_parent_assignments=local["counts"]["parent_assignment"],
        caveat="Only observed executed candidate lineage, not proof of cause of final bestmove.")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--private-original-C3b",required=True)
    p.add_argument("--private-actual-child",required=True)
    p.add_argument("--public-out",required=True)
    a=p.parse_args()
    r=joint_court(Path(getattr(a,"private_original_C3b")).read_text(),
                  Path(a.private_actual_child).read_text())
    out=Path(a.public_out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("C3X042_R6_JOINT_SOURCE_COURT",r["status"])
    if not r["status"].startswith("PASS_"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
