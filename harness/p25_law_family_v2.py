#!/usr/bin/env python3
"""P25 exact-prefix repair: make receipt hashing stable across JSON round trips.

P25 v1 used integer keys for the in-memory atlas_receipts map. json.dumps(sort_keys=True)
sorted those numerically before the first hash, while the written JSON necessarily converted them
to strings; a later verifier then sorted them lexicographically. No selective intervention outcome
was opened before this was detected. This wrapper normalizes through JSON once before hashing and
then delegates every scientific operation to the frozen P25 implementation.
"""
import hashlib,json
import p25_law_family as p

def stable_canon(o):
    normalized=json.loads(json.dumps(o,ensure_ascii=False,allow_nan=False))
    return json.dumps(normalized,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()

def stable_digest(o):return hashlib.sha256(stable_canon(o)).hexdigest()
def stable_seal(o):
    o.pop("receipt_sha256",None)
    o["receipt_sha256"]=stable_digest(o)
    return o

p.canon=stable_canon
p.digest=stable_digest
p.seal=stable_seal

if __name__=="__main__":p.main()
