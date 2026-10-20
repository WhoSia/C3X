#!/usr/bin/env python3
"""Bounded native SEE guard consequence derived from original SF16 exact callsites and private cold traces."""
import json,sys,hashlib
from pathlib import Path
from collections import Counter
from c3x_023_P1_same_descendant_SEE_node_matcher import identity

SITES={"capture_prune","quiet_prune","qsearch_futility","qsearch_prune"}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def classify(records):
 out=Counter();keys=Counter()
 for event in records:
  if event["kind"]=="censored":
   out["observed_prefix_censored"]+=1;continue
  if event["kind"]!="witness":continue
  assert event["site"] in SITES and event["altered"]==0
  assert event["original"]==event["delivered"]
  verdict="CONTINUE_PRUNE" if event["delivered"]==0 else "GUARD_PASSED"
  out[(event["site"],verdict)]+=1;keys[identity(event)]+=1
 return out,keys
def main():
 private=Path(sys.argv[1]); out=Path(sys.argv[2])
 d=json.loads(private.read_text())
 entries=[]; total=Counter()
 for r in d["cases"]:
  o,ok=classify(r["native_SEE_original"])
  t,tk=classify(r["native_SEE_treated"])
  obs_only=sum((ok-tk).values());treated_only=sum((tk-ok).values());shared=sum((ok&tk).values())
  counts={f"{k[0]}.{k[1]}" if isinstance(k,tuple) else k:int(v) for k,v in o.items()}
  treated={f"{k[0]}.{k[1]}" if isinstance(k,tuple) else k:int(v) for k,v in t.items()}
  row={"game_id":r["id"],"source_game_sha256":r["source_game_sha256"],
       "root_changed":r["root_changed"],"TT_first_physical_contact":r["TT_FIRST_contact"],
       "source_first_post_TT_chronological_status":r["source_chronology"]["status"],
       "original_bounded_guard_counts":counts,"treated_bounded_guard_counts":treated,
       "first32_shared_event_observations":shared,"original_only_event_observations":obs_only,
       "TT_FIRST_only_event_observations":treated_only,
       "sufficient_to_certify_SEE_parent_root_mediation":False}
  entries.append(row)
  total["original_only"]+=obs_only;total["treated_only"]+=treated_only
  total["shared"]+=shared
  total["cases"]+=1
  total["treatment_with_only_new_events"]+=int(treated_only>0)
 result={"schema":"c3x027-sept16-native-SEE-guard-consumer-bounded-source-inferred-v1",
   "input_private_sha256":digest(private),"original_source_guard_semantics":"Stockfish16 search.cpp if(!c3x022_r2_see(...)) continue, compound qsearch_futility enters SEE only once first test passed",
   "direct_boolean_consumption_certified_from_source_control_flow":True,
   "actual_prune_branch_taken_direct_instrumentation":False,
   "SEE_event_identity_scope":"TT-key+root-call watch, finite prefix; full root descendants NOT observable",
   "no_causal_parent_transport_proved":True,"cases":entries,"summary":dict(total)}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("C3X027_SEPT_GUARD_CONSUMER_LEDGER_PASS",result["summary"])
 for z in entries:
  if z["root_changed"]:print("C3X027_SEPT_FLIP_GUARD_DETAILS",z)
if __name__=="__main__":main()
