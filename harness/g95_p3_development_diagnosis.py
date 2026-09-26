#!/usr/bin/env python3
import argparse,json
from collections import Counter
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--p2-final",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 x=json.loads(Path(a.p2_final).read_text())
 if x.get("schema")!="c3x-g95-p2-adjudication-v1":raise SystemExit("P3_DEV_P2_SCHEMA")
 bad=[z for z in x["certificates"] if z.get("status")=="CONTRADICTED_CONTEXT_CELL"]
 if len(bad)!=8:raise SystemExit(f"P3_DEV_EXPECTED_8 got {len(bad)}")
 engines=Counter(z["profile"]["engine"] for z in bad);coords=sorted(bad[0]["profile"]["context"])
 constant={c:next(iter({z["profile"]["context"][c] for z in bad})) for c in coords if len({z["profile"]["context"][c] for z in bad})==1}
 varying={c:sorted({z["profile"]["context"][c] for z in bad}) for c in coords if c not in constant}
 out={"schema":"c3x-g95-p3-development-diagnosis-v1","scientific_stage":"C3X 0.7.0-G9.5-P3","authority":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_VOTE","p2_verdict":x["verdict"],"contradiction_count":len(bad),"contradictions_by_engine":dict(engines),"constant_p2_context_across_contradictions":constant,"varying_p2_context_across_contradictions":varying,"record_ids":[z["record_id"] for z in bad],"interpretation":"The P2 failure witnesses cluster strongly at first-occurrence / first-quartile events, while engine and event/search-state details vary. This motivates temporal and key-reuse topology families but does not select or certify any P3 schema.","p3_schema_selected":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P3_DEVELOPMENT_DIAGNOSIS",len(bad),dict(engines),constant)
if __name__=="__main__":main()
