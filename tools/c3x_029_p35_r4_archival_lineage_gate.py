#!/usr/bin/env python3
"""P35/R4 archival re-audit: authentic P34 sources only, NOT a new engine run."""
import argparse, collections, hashlib, json, re, zipfile
from pathlib import Path
SOURCE_SHA="6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c"
P34_SHA="c80704f2f81c4920597fbf6b559ef38dbae60f35458c7a2f665f1cf57d2563dc"
ZIP_SHA="2b426b81c97d1483581e398c7a300b221a39ebe6d9e5e0194bec4d3f2885547e"
RAW_SHA="07d78a9261dd87d12b900bc3cec715d4d28aa739212ef3c81507b918a6ba14f9"
REGEX=re.compile(r"(?m)^\s*(Classical evaluation|NNUE evaluation|Final evaluation)\s+([+-]?\d+(?:\.\d+)?)\s+\(white side\)")

def fail_unless(ok, reason):
    if not ok: raise ValueError("P35_R4_HOLD_"+reason)
def sha(data): return hashlib.sha256(data).hexdigest()
def member(z, name, expected=None):
    b=z.read(name)
    if expected: fail_unless(sha(b)==expected,"SHA_"+name)
    return b

def audit(source_zip, search_zip, trace_zip):
    fail_unless(sha(Path(trace_zip).read_bytes())==ZIP_SHA,"RAW_ZIP_SHA")
    with zipfile.ZipFile(source_zip) as zs, zipfile.ZipFile(search_zip) as zp, zipfile.ZipFile(trace_zip) as zt:
        src=json.loads(member(zs,"C3X018_INDEPENDENT_BLIND16_PGN_SOURCE.json",SOURCE_SHA))
        search=json.loads(member(zp,"P34_FOUR_ROOTS_CLASSICAL_NNUE_BUDGET24000.json",P34_SHA))
        raw=json.loads(member(zt,"P34_R4_RAW_DIRECT_NNUE_CLASSICAL_TRACES.json",RAW_SHA))
        compact=json.loads(member(zp,"P34_R3_DIRECT_SAME_BOARD_EVAL_TRACE.json"))
        binaries=[]
        for z in (zp,zt):
            m=re.fullmatch(r"([a-f0-9]{64})\s+\S+\s*",z.read("SF16_BINARY_SHA256.txt").decode())
            fail_unless(m is not None,"BINARY_SHA_FORMAT")
            binaries.append(m.group(1))
        fail_unless(len(set(binaries))==1,"ARCHIVED_BINARY_SHA_DIFFERENCE")
        fail_unless(len(src["selected"])==16 and len(search["records"])==4,"SOURCE_COHORT_COUNT")
        fail_unless(len(raw["records"])==len(compact["records"])==12,"RAW_BOARD_COUNT")
        fail_unless(raw["source_sha256"]==SOURCE_SHA and raw["p34_json_sha256"]==P34_SHA,"PARENT_DIGEST")
        cases={x["id"]:x for x in src["selected"]}
        roots={(x["case_id"],x["root_uci"]):x for x in search["records"]}
        fail_unless(len(roots)==4,"DUPLICATE_ROOT")
        groups=collections.defaultdict(list)
        for i,(r,prior) in enumerate(zip(raw["records"],compact["records"])):
            fail_unless({k:v for k,v in r.items() if k!="raw_source_eval_trace"}==prior,"R3_R4_ROW_"+str(i))
            key=(r["case_id"],r["root"])
            fail_unless(key in roots,"UNKNOWN_ROOT")
            case=cases[r["case_id"]]
            fail_unless(roots[key]["full_source_history"] is True,"SEARCH_HISTORY_DECLARATION")
            fail_unless(0<case["source_ply_before_original_move"]<len(case["full_original_mainline_uci"]),"SOURCE_PLY")
            fail_unless(r["position_history_length"]==case["source_ply_before_original_move"]+1+int(r["reply"] is not None),"HISTORY_LENGTH")
            s=r["raw_source_eval_trace"]
            fail_unless(sha(s.encode())==r["raw_trace_sha256"],"RAW_TEXT_SHA")
            fail_unless("id name Stockfish 16\n" in s and "option name Use NNUE type check" in s,"ENGINE_BANNER")
            fail_unless("NNUE derived piece values" in s and "NNUE network contributions" in s,"NATIVE_TRACE_REGIONS")
            parsed={k:float(v) for k,v in REGEX.findall(s)}
            labels={"Classical evaluation":"classical_white_pawns","NNUE evaluation":"nnue_white_pawns","Final evaluation":"final_white_pawns"}
            fail_unless(set(parsed)==set(labels),"DIRECT_EVAL_PARSE")
            fail_unless(all(abs(parsed[k]-r["trace"][v])<1e-8 for k,v in labels.items()),"DIRECT_EVAL_VALUE")
            if r["reply"] is None: fail_unless(r["scope"]=="immediately_after_root","ROOT_SCOPE")
            else:
                mode={"after_classical_worst_reply":"classical","after_nnue_worst_reply":"nnue"}.get(r["scope"])
                fail_unless(mode is not None,"REPLY_SCOPE")
                refs=roots[key]["reference_by_mode"][mode]
                worst=min(v["root_value_cp"] for v in refs)
                fail_unless(r["reply"] in {v["reply"] for v in refs if v["root_value_cp"]==worst},"WORST_REPLY_ID")
            groups[key].append(r)
        fail_unless(len(groups)==4 and all(len(v)==3 for v in groups.values()),"THREE_PER_ROOT")
        contrasts=[]
        for (case,root),rows in sorted(groups.items()):
            a=next(r for r in rows if r["scope"]=="after_classical_worst_reply")
            b=next(r for r in rows if r["scope"]=="after_nnue_worst_reply")
            fail_unless(a["reply"]!=b["reply"],"NONDISTINCT_REFERENCE_REPLIES")
            ec=a["trace"]["classical_white_pawns"]-b["trace"]["classical_white_pawns"]
            en=a["trace"]["nnue_white_pawns"]-b["trace"]["nnue_white_pawns"]
            contrasts.append({"case_id":case,"root_uci":root,"reply_classical_ref":a["reply"],"reply_nnue_ref":b["reply"],"classical_contrast_pawn":round(ec,4),"nnue_contrast_pawn":round(en,4),"difference_in_differences_pawn":round(en-ec,4),"strict_static_rank_reversal":ec*en<0})
        return {"status":"ARCHIVAL_CHECK_PASS_NOT_NEW_NATIVE_RUN","source_games":16,"selected_roots":4,"audited_boards":12,
                "raw_trace_sha_verified":12,"compact_records_matched":12,"binary_sha256":binaries[0],
                "source_sha256":SOURCE_SHA,"search_sha256":P34_SHA,"raw_zip_sha256":ZIP_SHA,
                "contrasts":contrasts,"strict_reversals":sum(x["strict_static_rank_reversal"] for x in contrasts),
                "claim_ceiling":"Direct static evaluator archival evidence. No search evaluator dispatch/parent/root mediation or heldout result."}

def main():
    p=argparse.ArgumentParser()
    for x in ("source-zip","search-zip","trace-zip","out"):p.add_argument("--"+x,required=True)
    a=p.parse_args()
    result=audit(a.source_zip,a.search_zip,a.trace_zip)
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
