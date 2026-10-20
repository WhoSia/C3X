#!/usr/bin/env python3
"""Strict depth-boundary A/B/C comparison for C3X 0.27 game14.

The source-native boundaries are observational summaries, not a causal root
certificate. World-level final bestmove equality never upgrades G8/G9.
"""
import re
from pathlib import Path

def parse_boundary_lines(lines):
    groups=[]
    active=None
    for line in lines:
        if "event=ROOT_BOUNDARY" not in line:
            continue
        fields=dict(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=([^\\s]+)",line))
        required=("depth","leader","score","average")
        if any(key not in fields for key in required):
            return {"status":"HOLD_MALFORMED_DEPTH_BOUNDARY","runs":[]}
        try:
            row={key:int(fields[key]) for key in required}
        except ValueError:
            return {"status":"HOLD_NONNUMERIC_DEPTH_BOUNDARY","runs":[]}
        if row["depth"]==1:
            active=[]
            groups.append(active)
        if active is None or (active and row["depth"]<=active[-1]["depth"]):
            return {"status":"HOLD_NONMONOTONIC_OR_UNBOUNDED_DEPTH","runs":[]}
        active.append(row)
    if len(groups)!=2 or not groups[0] or groups[0]!=groups[1]:
        return {"status":"HOLD_COLD_BOUNDARIES_MISSING_OR_CHANGED","runs":groups}
    return {"status":"PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS","runs":groups}

def compare_worlds(text_by_world):
    reports={name:parse_boundary_lines(text_by_world.get(name,"").splitlines())
             for name in ("A","B","C")}
    if any(v["status"]!="PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS"
           for v in reports.values()):
        return {"status":"HOLD_INCOMPLETE_NATIVE_DEPTH_DATA",
                "world_status":{k:v["status"] for k,v in reports.items()},
                "causal_parent_to_root_certified":False}
    by={name:{r["depth"]:r for r in reports[name]["runs"][0]} for name in reports}
    common=sorted(set.intersection(*(set(v) for v in by.values())))
    if not common:
        return {"status":"HOLD_NO_COMMON_DEPTH","causal_parent_to_root_certified":False}
    divergences=[]
    for depth in common:
        rows={name:by[name][depth] for name in by}
        different=[key for key in ("leader","score","average")
                   if rows["B"][key]!=rows["C"][key]]
        if different:
            divergences.append({"depth":depth,"fields":different,
                                "A":rows["A"],"B":rows["B"],"C":rows["C"]})
    return {"status":"PASS_OBSERVATIONAL_DEPTH_COMPARISON",
            "common_depths":len(common),
            "first_B_C_boundary_difference":divergences[0] if divergences else None,
            "different_depth_count":len(divergences),
            "causal_parent_to_root_certified":False,
            "natural_TT_SEE_mediation_certified":False}
