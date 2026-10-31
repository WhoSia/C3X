"""P16: normalized immutable identity for matched chess claims.
Never identify the objective by a free-text slogan alone.
"""
import hashlib,json
REQUIRED=("source_game","root_state_digest","side","candidate_set","property_id","reply_scope","horizon_plies","ruleset")
def fingerprint(record):
    if not isinstance(record,dict) or any(k not in record for k in REQUIRED):
        raise ValueError("MISSING_CLAIM_IDENTITY")
    if record["side"] not in ("w","b") or record["reply_scope"] not in ("all_legal","capture_only"):
        raise ValueError("INVALID_SCOPE")
    if type(record["horizon_plies"]) is not int or record["horizon_plies"]<1:
        raise ValueError("INVALID_HORIZON")
    if any(not isinstance(record[k],str) or not record[k] for k in ("source_game","root_state_digest","property_id","ruleset")):
        raise ValueError("INVALID_SOURCE")
    a=record["candidate_set"]
    if not isinstance(a,list) or len(a)<2 or any(not isinstance(s,str) or not s for s in a) or len(set(a))!=len(a):
        raise ValueError("INVALID_CANDIDATES")
    stable={k:record[k] for k in REQUIRED};stable["candidate_set"]=sorted(a)
    return hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
