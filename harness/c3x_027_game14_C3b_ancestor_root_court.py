#!/usr/bin/env python3
"""C3X 0.27 Game14 ancestor/root adjudicator. Strictly observational, no promotion.

Consumes future native JSONL event arrays; never substitutes final bestmove
restoration for a verified return-to-ancestor chain. Original C3b stays intact.
"""
import argparse,json
from pathlib import Path

SCHEMA="c3x027-game14-C3b-ancestor-root-court-v1"
class Hold(Exception): pass

def judge(events, root_call):
    if not events:return {"status":"HOLD_NO_NATIVE_C3B_EVENTS","certified":False}
    seq=[x.get("sequence") for x in events]
    if seq!=list(range(1,len(events)+1)):
        return {"status":"HOLD_EVENT_GAP_OR_REORDER","certified":False}
    if any(x.get("root_call")!=root_call for x in events):
        return {"status":"HOLD_ROOT_CALL_CHANGED","certified":False}
    if any(x.get("truncated",False) for x in events):
        return {"status":"HOLD_SOURCE_TRACE_CENSORED","certified":False}
    snap=events[0]
    if snap.get("event")!="ANCESTOR_SNAPSHOT" or not isinstance(snap.get("ply"),int):
        return {"status":"HOLD_ANCESTOR_SNAPSHOT_MISSING","certified":False}
    p=snap["ply"]
    if p<1 or p>=128:return {"status":"HOLD_INVALID_PLY","certified":False}
    expected=[("ANCESTOR_SNAPSHOT",p),("CHILD_VALUE_RETURNED",p)]
    for ply in range(p,-1,-1):
        expected.extend([("PARENT_CANDIDATE_VALUE",ply),
                         ("ROOT_FRAME_RETURN" if ply==0 else "FRAME_RETURN",ply)])
    observed=[(e.get("event"),e.get("ply")) for e in events]
    if expected!=observed:
        return {"status":"HOLD_PARTIAL_OR_DIVERGED_SOURCE_PATH",
                "certified":False,"observed_events":len(events),"expected_events":len(expected)}
    for i in range(2,len(events),2):
        x,y=events[i:i+2]
        if (x.get("key64"),x.get("native_move")) != (y.get("key64"),y.get("native_move")):
            return {"status":"HOLD_FRAME_OR_MOVE_MISMATCH","certified":False}
        if x.get("frame_id") is None or x.get("frame_id")!=y.get("frame_id"):
            return {"status":"HOLD_FRAME_ID_NOT_CERTIFIED","certified":False}
        if x.get("value") is None or y.get("value") is None:
            return {"status":"HOLD_NATIVE_VALUE_MISSING","certified":False}
    return {"status":"PASS_C3B_OBSERVED_ANCESTOR_ROOT_CANDIDATE_CHAIN",
            "certified":True,"candidate_edges":p+1,
            "root_candidate_updated":True,
            "final_bestmove_causation_certified":False,
            "natural_TT_SEE_mediation_certified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--private-json",required=True)
    p.add_argument("--public-json",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.private_json).read_text())
    assert data.get("schema")==SCHEMA and data.get("source_game_id")==14
    out={"schema":SCHEMA,"scope":"historical_postselected_game14",
         "worlds":{w:judge(data.get("worlds",{}).get(w,[]),data["root_call"])
                   for w in ("A","B","C")},
         "natural_TT_SEE_mediation_certified":False}
    dest=Path(a.public_json);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("C3X027_GAME14_C3B_COURT",json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
