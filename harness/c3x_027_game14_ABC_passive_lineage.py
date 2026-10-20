#!/usr/bin/env python3
"""Game14 A/B/C cold replay with isolated native passive lineage log (not proof by bestmove)."""
import argparse,os,json,re,hashlib
from collections import Counter
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_023_P1_same_descendant_SEE_node_matcher import identity
def dig(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
for x in ('source','stagea','forecast','engine','out','private'):p.add_argument('--'+x,required=True)
a=p.parse_args()
need(dig(a.source)=="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d","SOURCE_SHA_DRIFT")
need(dig(a.stagea)=="b0eb51ab779609db346c75d65a6a65fd31efc9a648111d042cfec5199a4afde1","STAGEA_SHA_DRIFT")
need(dig(a.forecast)=="4572edd4c0761c3875aed421b08880ff142c21f691fe940c7c6d760dbb397be5","FORECAST_SHA_DRIFT")
source=json.loads(Path(a.source).read_text())["source_games"][13]
old=json.loads(Path(a.stagea).read_text())["cases"][13]
forecast=json.loads(Path(a.forecast).read_text())["cases"][13]
need(source["id"]==old["id"]==forecast["id"]==14,"GAME14_ID_MISMATCH")
need(source["source_game_sha256"]=="0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652","GAME14_SOURCE_ID_DRIFT")
b=chess.Board(source["fen4"]+" "+str(source["source_halfmove_clock"])+" "+str(source["source_fullmove_number"]))
move=chess.Move.from_uci(source["played_legal_move_uci"])
need(b.is_valid() and move in b.legal_moves,"GAME14_CHESS_INVALID")
world=dict(source);world["native_move"]=move.from_square*64+move.to_square
world,clock,_=native_world(world)
roles=old["worlds"]["O"]["roles"]
role=next((x for x in ("STRICT","BROAD") if roles[x]["status"]=="FIRST_SOURCE_PAIR_PRE_TREATMENT"),None)
need(role is not None,"GAME14_NO_SOURCE")
target=roles[role];watch={"key64":target["physical"]["key64"],"root_call":target["root_calls"][0]}
pair={"physical":target["physical"],"root_calls":target["root_calls"],"root_candidate_native":target["root_candidate_native"]}
Path(a.private).mkdir(parents=True,exist_ok=True)
def replay(name,mode,physical=None,filters=None):
 path=Path(a.private)/(name+".txt")
 path.write_text("")
 os.environ["C3X027_CAPTURE_BRANCH_LOG"]=str(path.resolve())
 lineage_path=Path(a.private)/(name+"_lineage.txt")
 lineage_path.write_text("")
 os.environ["C3X027_GAME14_LINEAGE_LOG"]=str(lineage_path.resolve())
 try:result=cold(a.engine,world,clock,"O",mode,physical,filter=filters,watch=watch)
 finally:
  os.environ.pop("C3X027_CAPTURE_BRANCH_LOG",None)
  os.environ.pop("C3X027_GAME14_LINEAGE_LOG",None)
 return result,path
orig,op=replay("original","OBS")
tr, tp=replay("TT_FIRST","V",target["physical"],mask_filters(RULES[role],pair,"FIRST"))
need(orig["UCI"]["bestmove"]=="b3a4" and tr["UCI"]["bestmove"]=="f3f4","GAME14_ROOT_EFFECT_NOT_REPRODUCED")
blocks=[x for x in tr["blocks"] if x.get("kind")=="reader_block"]
need(blocks and verified_reader_lineage(tr)["all_valid"],"TT_FIRST_PHYSICAL_WRITER_READER_UNVERIFIED")
def logs(path): 
 out=[]
 for line in path.read_text().splitlines():
  row=dict(re.findall(r"(\w+)=([^ ]+)",line))
  if row:out.append(row)
 return out
o,t=logs(op),logs(tp)
oldkeys=Counter(identity(x) for x in orig["native_see_events"] if x.get("kind")=="witness")
newkeys=Counter(identity(x) for x in tr["native_see_events"] if x.get("kind")=="witness")
extra=newkeys-oldkeys
activated=[x for x in tr["native_see_events"] if x.get("kind")=="witness" and x.get("site")=="capture_prune" and extra[identity(x)]>0]
for x in activated:extra[identity(x)]-=1
matches=[]
for e in activated:
 k=(str(e["key64"]),str(e["root_call"]),str(e["move"]),str(e["threshold"]))
 matching=[z for z in t if tuple(z.get(a) for a in ("key64","root_call","move","threshold"))==k]
 matches.append({"target_site":"capture_prune","observed_target_boolean":e["delivered"],"matching_native_guard_actions":dict(Counter(z["action"] for z in matching)),"matches":len(matching)})
need(len(activated)==1 and len(matches)==1 and matches[0]["matches"]==2,"EXACT_ONE_CAPTURE_EVENT_NOT_REPRODUCED")
event=activated[0]
os.environ["C3X027_FORCE_CAPTURE_KEY64"]=str(event["key64"])
os.environ["C3X027_FORCE_CAPTURE_ROOT_CALL"]=str(event["root_call"])
os.environ["C3X027_FORCE_CAPTURE_MOVE"]=str(event["move"])
os.environ["C3X027_FORCE_CAPTURE_THRESHOLD"]=str(event["threshold"])
try:
 cf,cfpath=replay("TT_FIRST_REENABLE_ONE","V",target["physical"],mask_filters(RULES[role],pair,"FIRST"))
finally:
 for name in ("C3X027_FORCE_CAPTURE_KEY64","C3X027_FORCE_CAPTURE_ROOT_CALL","C3X027_FORCE_CAPTURE_MOVE","C3X027_FORCE_CAPTURE_THRESHOLD"):
  os.environ.pop(name,None)
cf_actions=Counter(x["action"] for x in logs(cfpath))
need(cf_actions["EXACT_ONE_EVENT_REENABLED"]==2,"COUNTERFACTUAL_GUARD_CONTACT_NOT_TWO_COLD_REPLAYS")
need(verified_reader_lineage(cf)["all_valid"] and any(x.get("kind")=="reader_block" for x in cf["blocks"]),"COUNTERFACTUAL_TT_SOURCE_CONTACT_HOLD")
cf_move=cf["UCI"]["bestmove"]
cf_status=("ORIGINAL_ROOT_RESTORED" if cf_move==orig["UCI"]["bestmove"] else
           "TREATED_ROOT_UNCHANGED" if cf_move==tr["UCI"]["bestmove"] else "THIRD_ROOT_CHOICE")
summary={"schema":"c3x027-sept-game14-actual-CPP-capture-guard-v1","exposed_selected_after_outcome":True,"game_id":14,"source_game_sha256":source["source_game_sha256"],"baseline_bestmove":orig["UCI"]["bestmove"],"TT_FIRST_bestmove":tr["UCI"]["bestmove"],"actual_physical_reader_blocks":len(blocks),"original_guard_actions":dict(Counter(x["action"] for x in o)),"treated_guard_actions":dict(Counter(x["action"] for x in t)),"treated_only_capture_source_events":len(activated),"exact_event_branch_actions":matches,"actual_branch_proof":bool(matches) and all(x["matches"]>0 for x in matches),"counterfactual_guard_reenable_not_run":False,"one_event_reenable_status":cf_status,"counterfactual_bestmove":cf_move,"counterfactual_branch_action_counts":dict(cf_actions),"native_guard_one_event_contact":True,"natural_full_mediation_certified":False}
Path(a.out).write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
print("C3X027_CAPTURE_DIRECT_GAME14",json.dumps(summary,sort_keys=True))

# C3X027 native event counts are exploratory until compared with original source semantics.
def lineage_public(path):
 from collections import Counter
 rows=[]
 for line in path.read_text().splitlines():
  if "c3x027_root_boundary" in line:
   rows.append("ROOT_BOUNDARY")
  elif "event=" in line:
   import re
   m=re.search(r"event=([A-Z_]+)",line)
   if m:rows.append(m.group(1))
 return dict(sorted(Counter(rows).items()))
lineage_summary={arm:lineage_public(Path(a.private)/(name+"_lineage.txt"))
 for arm,name in (("A","original"),("B","TT_FIRST"),("C","TT_FIRST_REENABLE_ONE"))}
out_path=Path(a.out)
public_lineage=out_path.with_name("C3X027_GAME14_PASSIVE_LINEAGE_AGGREGATE.json")
public_lineage.write_text(json.dumps({
 "schema":"c3x027-game14-passive-lineage-aggregate-v1",
 "source_game_sha256":source["source_game_sha256"],
 "scope":"historical-postselected-game14-not-prospective-mediation",
 "world_event_counts":lineage_summary,
 "raw_event_keys_and_child_positions_private":True,
 "native_descendant_transmission_certified":False,
 "natural_TT_SEE_mediation_certified":False},indent=2,sort_keys=True)+"\n")
print("C3X027_GAME14_PASSIVE_LINEAGE_COUNTS",json.dumps(lineage_summary,sort_keys=True))

def native_c_chain(path):
    import re
    rows=[]
    for line in path.read_text().splitlines():
        m=dict(re.findall(r"(\w+)=([^ ]+)",line))
        if "seq" in m and "event" in m: rows.append(m)
    chunks=[]
    for row in rows:
        if row["seq"]=="1":chunks.append([])
        if not chunks:return {"status":"HOLD_EVENT_SEQUENCE_NO_START"}
        chunks[-1].append(row)
    expected=["GUARD_REENABLED","DO_MOVE_EXECUTED","CHILD_ENTERED",
              "CHILD_VALUE_RETURNED","PARENT_CANDIDATE_VALUE"]
    results=[]
    for c in chunks:
        kinds=[r["event"] for r in c]
        levels={"guard":len(kinds)>0 and kinds[0]==expected[0],
                "child_do":kinds[:2]==expected[:2],
                "child_entry":kinds[:3]==expected[:3],
                "child_return":kinds[:4]==expected[:4],
                "parent_candidate":kinds[:5]==expected}
        if levels["child_entry"]:
            levels["key_link"]=(c[1]["key64"]==c[0]["expected_child64"]==
                                c[2]["key64"])
        else: levels["key_link"]=False
        if levels["parent_candidate"]:
            levels["return_value_link"]=(c[3]["value"]==c[4]["value"])
            levels["root_call_link"]=len({x["root_call"] for x in c})==1
            levels["sequence_monotonic"]=[int(x["seq"]) for x in c]==list(range(1,len(c)+1))
        else:
            levels["return_value_link"]=False
            levels["root_call_link"]=False
            levels["sequence_monotonic"]=False
        results.append({"observed_events":len(c),"levels":levels})
    return {"status":"PASS_LOCAL_PARENT_SOURCE_PATH" if len(results)==2 and
            all(all(x["levels"].values()) for x in results)
            else "HOLD_INCOMPLETE_OR_AMBIGUOUS_SOURCE_CHAIN",
            "cold_runs_observed":len(results),"cold_source_courts":results,
            "root_candidate_competition_certified":False,
            "natural_mediation_certified":False}
court=native_c_chain(Path(a.private)/"TT_FIRST_REENABLE_ONE_lineage.txt")
public_court=out_path.with_name("C3X027_GAME14_PASSIVE_SOURCE_CHAIN_COURT.json")
public_court.write_text(json.dumps({
 "schema":"c3x027-game14-capture-guard-to-parent-source-court-v1",
 "source_game_sha256":source["source_game_sha256"],
 "result":court,
 "not_same_as_024_ancestor_root_full_proof":True},indent=2,sort_keys=True)+"\n")
print("C3X027_GAME14_PASSIVE_SOURCE_CHAIN",json.dumps(court,sort_keys=True))
