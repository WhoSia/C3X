#!/usr/bin/env python3
"""C3X 0.27 game14 source-lineage court; original 0.24 kept unchanged.

Missing native lineage events are HOLD, not assumed from matching bestmoves.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA="c3x027-game14-transmission-court-v1"
GAME_SHA="0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652"
HASHES={
 "source":"9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d",
 "stagea":"b0eb51ab779609db346c75d65a6a65fd31efc9a648111d042cfec5199a4afde1",
 "forecast":"4572edd4c0761c3875aed421b08880ff142c21f691fe940c7c6d760dbb397be5"}
GATES=tuple("G"+str(i) for i in range(11))
class ContractError(ValueError): pass
def need(value, message):
    if not value: raise ContractError(message)
def assess(d):
    need(d.get("schema")==SCHEMA,"SCHEMA_MISMATCH")
    need(d.get("game_sha256")==GAME_SHA,"GAME_SOURCE_MISMATCH")
    need(d.get("protocol") in ("STRICT_ONLY_15","STRICT_ELSE_BROAD_16"),"PROTOCOL_MERGE")
    g={k:"HOLD_NOT_MEASURED" for k in GATES}
    w=d.get("worlds",{})
    if not all(n in w for n in ("A","B","C")):
        return {"schema":SCHEMA,"gates":g,"natural_full_mediation_certified":False}
    need([w[n].get("bestmove") for n in ("A","B","C")]==["b3a4","f3f4","b3a4"],"ROOT_PARITY_FAIL")
    g["G0"]="PASS_HISTORICAL_ROOT_MOVES"
    b,c=w["B"],w["C"]
    if not b.get("tt_writer_reader_valid") or not c.get("tt_writer_reader_valid"):
        g["G1"]="FAIL_TT_LINEAGE"
        return {"schema":SCHEMA,"gates":g,"natural_full_mediation_certified":False}
    g["G1"]="PASS_TT_SOURCE_CONTACT"
    if b.get("original_see_boolean") is False and b.get("guard_action")=="NO_DISCOVERED_ATTACK_CONTINUE":
        g["G2"]="PASS_ACTUAL_GUARD_SKIP"
    if c.get("original_see_boolean") is False and c.get("guard_action")=="EXACT_ONE_EVENT_REENABLED" and c.get("exact_reenable_count")==1:
        g["G3"]="PASS_EXACT_ONE_GUARD_BYPASS"
    if not all(g[k].startswith("PASS") for k in ("G2","G3")):
        return {"schema":SCHEMA,"gates":g,"natural_full_mediation_certified":False}
    events=c.get("events",[])
    if events:
        need(not c.get("truncated",False),"CENSORED_NATIVE_TRACE")
        need([e.get("event_sequence") for e in events]==list(range(1,len(events)+1)),"EVENT_SEQUENCE_GAP")
        target=c.get("target_guard_event_id")
        x=[e for e in events if e.get("target_guard_event_id")==target and target is not None]
        kinds=[e.get("event_kind") for e in x]
        expected=["GUARD_REENABLED","DO_MOVE_EXECUTED","CHILD_ENTERED",
                  "CHILD_VALUE_RETURNED","PARENT_CANDIDATE_VALUE","ROOT_CANDIDATE_UPDATE"]
        if kinds[:3]==expected[:3]:
            a,m,ch=x[:3]
            need(all("frame_id" in e and "root_call" in e for e in x[:3]),"FRAME_ID_MISSING")
            need(a["root_call"]==m["root_call"]==ch["root_call"],"ROOT_CALL_MISMATCH")
            need(a["frame_id"]==m["frame_id"] and ch.get("parent_frame_id")==m["frame_id"],"CHILD_ID_MISMATCH")
            need(ch.get("key64")==m.get("expected_child64") and ch.get("key64") is not None,"CHILD_KEY_MISMATCH")
            g["G4"]="PASS_NATIVE_CHILD_ENTRY"
        if g["G4"].startswith("PASS") and len(x)>3 and kinds[3]==expected[3]:
            need(x[3].get("frame_id")==x[2]["frame_id"],"RETURN_FRAME_MISMATCH")
            need(x[3].get("value_after") is not None,"RETURN_VALUE_MISSING")
            g["G5"]="PASS_NATIVE_CHILD_RETURN"
        if g["G5"].startswith("PASS") and len(x)>4 and kinds[4]==expected[4]:
            need(x[4].get("frame_id")==x[1]["frame_id"],"PARENT_FRAME_MISMATCH")
            need(x[4].get("child_frame_id")==x[3]["frame_id"],"RETURN_CONSUMER_NOT_LINKED")
            need(x[4].get("source_value_transform_verified") is True,"VALUE_TRANSFORM_NOT_AUDITED")
            g["G6"]="PASS_NATIVE_PARENT_CONSUMPTION"
        if g["G6"].startswith("PASS") and len(x)>5 and kinds[5]==expected[5]:
            need(x[5].get("root_call")==x[0]["root_call"] and
                 x[5].get("root_candidate_update_actual") is True,"ROOT_UPDATE_UNVERIFIED")
            g["G8"]="PASS_ROOT_CANDIDATE_UPDATE"
    return {"schema":SCHEMA,"gates":g,"natural_full_mediation_certified":False,
            "root_transmission_proven":False,"source_guard_restoration_observed":True}
def main():
    p=argparse.ArgumentParser()
    for n in ("source","stagea","forecast","private-input","public-output"):
        p.add_argument("--"+n,required=True)
    a=p.parse_args()
    for key,sha in HASHES.items():
        need(hashlib.sha256(Path(getattr(a,key)).read_bytes()).hexdigest()==sha,"INPUT_HASH_DRIFT_"+key)
    o=assess(json.loads(Path(a.private_input).read_text()))
    o["G0_byte_sha_verified"]=True
    f=Path(a.public_output);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(o,sort_keys=True,indent=2)+"\n")
    print("C3X027_TRANSMISSION_COURT",json.dumps(o,sort_keys=True))
if __name__=="__main__":main()
