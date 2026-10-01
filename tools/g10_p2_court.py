from __future__ import annotations
import argparse,json
from pathlib import Path
from c3x_g10.question_identity import adjudicate,stable_hash
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--bank",required=True);ap.add_argument("--shard",action="append",required=True);ap.add_argument("--out-court",required=True);ap.add_argument("--out-stable",required=True);ap.add_argument("--out-all",required=True);a=ap.parse_args()
    bank=json.load(open(a.bank,encoding="utf-8"));rows=[]
    for p in a.shard:rows.extend(json.load(open(p,encoding="utf-8"))["cases"])
    rows=sorted(rows,key=lambda x:x["case_id"])
    if [x["case_id"] for x in rows]!=sorted(x["case_id"] for x in bank["cases"]):raise SystemExit("MEASURED_CASE_BANK_MISMATCH")
    c=adjudicate(rows,bank)
    stable=[x for x in rows if x["identity"]["stable"]]
    sb={"schema":"c3x-g10-p2-stable-object-bank-v1","authority":"STABLE_RESEARCH_QUESTION_OBJECT_ONLY","source_bank_sha256":bank["bank_sha256"],"case_count":len(stable),"case_ids":[x["case_id"] for x in stable],"cases":stable,"fresh_local_certificate_induction_opened":False,"p1_survivors_used":False}
    sb["bank_sha256"]=stable_hash(sb["case_ids"])
    Path(a.out_court).write_text(json.dumps(c,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(a.out_stable).write_text(json.dumps(sb,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(a.out_all).write_text(json.dumps({"schema":"c3x-g10-p2-full-measurements-v1","cases":rows},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("G10_P2_COURT_VERDICT",c["verdict"])
    print("G10_P2_STABLE_BANK",c["stable_object_n"],c["stable_bank_sha256"],c["scope_counts"])
    print("G10_P2_ERROR_LOCALIZATION",json.dumps(c["measurement_error_localization"],sort_keys=True))
if __name__=="__main__":main()
